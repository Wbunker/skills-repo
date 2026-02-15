# Threads

## Table of Contents
- [Thread Creation](#thread-creation)
- [Thread Attributes](#thread-attributes)
- [Thread Lifecycle](#thread-lifecycle)
- [Join vs Detach](#join-vs-detach)
- [Stack Management](#stack-management)
- [Thread Identity](#thread-identity)
- [One-Time Initialization](#one-time-initialization)
- [Thread-Safe Initialization Patterns](#thread-safe-initialization-patterns)

## Thread Creation

```c
#include <pthread.h>

void *thread_func(void *arg) {
    int value = *(int *)arg;
    // ... work ...
    return result_ptr;  // or pthread_exit(result_ptr)
}

pthread_t tid;
int arg = 42;
int ret = pthread_create(&tid, NULL, thread_func, &arg);
if (ret != 0) {
    // pthread functions return error number directly (not -1/errno)
    fprintf(stderr, "pthread_create: %s\n", strerror(ret));
}
```

**Critical**: pthreads functions return error codes directly — they do NOT set `errno`. Always check the return value.

**Argument passing pitfall**:
```c
// WRONG — race condition, loop variable changes before thread reads it:
for (int i = 0; i < N; i++)
    pthread_create(&tids[i], NULL, func, &i);

// RIGHT — give each thread its own copy:
int *args = malloc(N * sizeof(int));
for (int i = 0; i < N; i++) {
    args[i] = i;
    pthread_create(&tids[i], NULL, func, &args[i]);
}
```

## Thread Attributes

Configure thread properties before creation:

```c
pthread_attr_t attr;
pthread_attr_init(&attr);

// Detach state:
pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

// Stack size:
pthread_attr_setstacksize(&attr, 2 * 1024 * 1024);  // 2 MB

// Scheduling (must set inherit first):
pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
struct sched_param param = { .sched_priority = 50 };
pthread_attr_setschedparam(&attr, &param);

// Scope (use SYSTEM for RT — maps 1:1 to kernel thread):
pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM);

pthread_create(&tid, &attr, func, arg);
pthread_attr_destroy(&attr);  // safe to destroy after create
```

### Key attributes reference

| Function | Purpose | Default |
|----------|---------|---------|
| `setdetachstate` | Joinable or detached | `PTHREAD_CREATE_JOINABLE` |
| `setstacksize` | Thread stack size | System default (often 8 MB) |
| `setstackaddr` / `setstack` | Custom stack address | System-allocated |
| `setschedpolicy` | `SCHED_OTHER`, `SCHED_FIFO`, `SCHED_RR` | `SCHED_OTHER` |
| `setschedparam` | Priority | 0 |
| `setinheritsched` | Inherit or explicit scheduling | `PTHREAD_INHERIT_SCHED` |
| `setscope` | `PTHREAD_SCOPE_SYSTEM` or `PROCESS` | Implementation-defined |
| `setguardsize` | Guard page size at stack end | System page size |

**Important**: `PTHREAD_INHERIT_SCHED` is the default — the thread inherits the creator's scheduling. For RT threads, you MUST set `PTHREAD_EXPLICIT_SCHED` to apply `setschedpolicy`/`setschedparam`.

## Thread Lifecycle

A thread exists from `pthread_create` until either:
1. It returns from its start function
2. It calls `pthread_exit(retval)`
3. It is canceled via `pthread_cancel`
4. Any thread calls `exit()` (terminates the entire process)

```c
// Return value (equivalent to pthread_exit):
void *func(void *arg) {
    int *result = malloc(sizeof(int));
    *result = 42;
    return result;
}

// Explicit exit:
void *func(void *arg) {
    pthread_exit(NULL);  // cleanup handlers run
    // code after pthread_exit is unreachable
}
```

**Thread termination does NOT release**: mutexes held, file descriptors, malloc'd memory (unless cleanup handlers handle it). Only the thread's stack is freed.

### Cleanup handlers

Push/pop cleanup handlers that run on thread exit or cancellation:

```c
void cleanup(void *arg) {
    pthread_mutex_unlock((pthread_mutex_t *)arg);
}

void *func(void *arg) {
    pthread_mutex_lock(&mutex);
    pthread_cleanup_push(cleanup, &mutex);

    // ... work that might be canceled ...

    pthread_cleanup_pop(1);  // 1 = execute handler; 0 = just remove
    return NULL;
}
```

**Implemented as macros**: `push` and `pop` must appear in the same lexical scope (they expand to `{ ... }`). This is a POSIX requirement.

## Join vs Detach

### Join — wait for thread completion
```c
void *retval;
int ret = pthread_join(tid, &retval);
// retval points to the value passed to return/pthread_exit
// retval is PTHREAD_CANCELED if thread was canceled
```

- Only one thread may join a given thread (joining twice is undefined behavior)
- A joinable thread that is never joined **leaks resources** (like a zombie process)
- Cannot join a detached thread

### Detach — fire and forget
```c
pthread_detach(tid);
// or: create with PTHREAD_CREATE_DETACHED attribute

// Resources are automatically freed when thread exits
```

**Design rule**: Every thread must be either joined or detached. No exceptions.

### Choosing join vs detach
- **Join** when you need the result, need to sequence work, or need to know when the thread is done
- **Detach** for background workers, daemon threads, or event handlers that run indefinitely

## Stack Management

### Default stack
The default stack size is typically 8 MB on Linux (check with `ulimit -s`). Each thread gets its own stack, so 1000 threads = ~8 GB of virtual address space for stacks alone.

### Setting stack size
```c
pthread_attr_t attr;
pthread_attr_init(&attr);

// Minimum is PTHREAD_STACK_MIN (typically 16 KB on Linux):
size_t stack_size = 256 * 1024;  // 256 KB
if (stack_size < PTHREAD_STACK_MIN)
    stack_size = PTHREAD_STACK_MIN;
pthread_attr_setstacksize(&attr, stack_size);
```

### Custom stack (advanced)
```c
// Allocate your own stack:
size_t stack_size = 1024 * 1024;
void *stack = mmap(NULL, stack_size, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);

pthread_attr_setstack(&attr, stack, stack_size);
// You must manage this memory — free/munmap after join
```

### Guard pages
A guard page (default: one page) at the end of the stack causes a segfault on overflow instead of silent corruption:

```c
pthread_attr_setguardsize(&attr, 4096);  // one page
pthread_attr_setguardsize(&attr, 0);     // disable (dangerous)
```

### Pre-faulting the stack for RT
```c
// In the RT thread, before entering the critical loop:
void prefault_stack(void) {
    volatile char stack[MAX_STACK_USE];
    memset((void *)stack, 0, sizeof(stack));
}
```

## Thread Identity

```c
pthread_t self = pthread_self();           // current thread ID
int equal = pthread_equal(tid1, tid2);     // compare thread IDs

// Linux-specific: get kernel thread ID (for scheduling, /proc):
#include <sys/syscall.h>
pid_t ktid = syscall(SYS_gettid);
```

`pthread_t` is an opaque type — don't compare with `==`, use `pthread_equal()`.

## One-Time Initialization

Thread-safe initialization that runs exactly once:

```c
pthread_once_t once_control = PTHREAD_ONCE_INIT;

void init_func(void) {
    // runs exactly once, regardless of how many threads call pthread_once
    global_resource = create_resource();
}

// In any thread:
pthread_once(&once_control, init_func);
// After this, global_resource is guaranteed initialized
```

**Behavior**: If multiple threads call `pthread_once` simultaneously, one executes the function and the others block until it completes. All subsequent calls are no-ops.

## Thread-Safe Initialization Patterns

### Lazy singleton
```c
static pthread_once_t once = PTHREAD_ONCE_INIT;
static struct config *cfg;

static void init_config(void) {
    cfg = load_config("/etc/app.conf");
}

struct config *get_config(void) {
    pthread_once(&once, init_config);
    return cfg;
}
```

### Thread-local storage (POSIX)
```c
// POSIX thread-specific data:
static pthread_key_t key;
static pthread_once_t key_once = PTHREAD_ONCE_INIT;

static void destructor(void *ptr) { free(ptr); }
static void make_key(void) { pthread_key_create(&key, destructor); }

void *get_thread_data(void) {
    pthread_once(&key_once, make_key);
    void *data = pthread_getspecific(key);
    if (!data) {
        data = calloc(1, sizeof(struct my_data));
        pthread_setspecific(key, data);
    }
    return data;
}
```

### Thread-local storage (C11 / GCC)
```c
// Simpler — compiler-managed:
_Thread_local int per_thread_counter = 0;

// GCC/Clang extension (older code):
__thread int per_thread_counter = 0;
```

Prefer `_Thread_local` / `thread_local` (C23) for new code. Use POSIX keys when you need destructor callbacks.
