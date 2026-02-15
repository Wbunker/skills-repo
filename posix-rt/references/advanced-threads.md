# Advanced Threads

## Table of Contents
- [Thread-Specific Data](#thread-specific-data)
- [Thread Cancellation](#thread-cancellation)
- [Fork Safety in Threaded Programs](#fork-safety-in-threaded-programs)
- [Thread Pools](#thread-pools)
- [Work Queue Pattern](#work-queue-pattern)
- [Thread-Safe Library Design](#thread-safe-library-design)
- [C11 Atomics and Memory Ordering](#c11-atomics-and-memory-ordering)

## Thread-Specific Data

Per-thread storage that's automatically cleaned up on thread exit.

### POSIX keys (portable)
```c
static pthread_key_t log_key;
static pthread_once_t key_once = PTHREAD_ONCE_INIT;

typedef struct {
    FILE *fp;
    int level;
    char prefix[32];
} thread_log_t;

static void log_destructor(void *ptr) {
    thread_log_t *log = ptr;
    if (log->fp) fclose(log->fp);
    free(log);
}

static void create_key(void) {
    pthread_key_create(&log_key, log_destructor);
}

thread_log_t *get_thread_log(void) {
    pthread_once(&key_once, create_key);
    thread_log_t *log = pthread_getspecific(log_key);
    if (!log) {
        log = calloc(1, sizeof(*log));
        snprintf(log->prefix, sizeof(log->prefix), "T%ld",
                 syscall(SYS_gettid));
        pthread_setspecific(log_key, log);
    }
    return log;
}
```

### Destructor ordering
- Destructors run when a thread exits (return or `pthread_exit`)
- If a destructor sets another TSD key, destructors may run again (up to `PTHREAD_DESTRUCTOR_ITERATIONS` times, typically 4)
- Destructor order among keys is undefined

### _Thread_local (C11) / __thread (GCC)
```c
_Thread_local int errno_shadow;       // C11
__thread int errno_shadow;            // GCC/Clang extension

// No destructor support — must manually clean up
// Faster than pthread_getspecific (direct memory access)
// Cannot be dynamically initialized (no constructor)
```

**Choose**: Use `_Thread_local` for simple types. Use POSIX keys when you need destructors or dynamic initialization.

## Thread Cancellation

Allow one thread to request another thread's termination:

```c
// Request cancellation:
pthread_cancel(target_tid);

// Target thread controls how cancellation works:
pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, &old);   // default
pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &old);

pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, &old);   // default
pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, &old);
```

### Deferred cancellation (default, recommended)
Cancellation occurs only at **cancellation points** — specific POSIX functions:

Key cancellation points: `pthread_cond_wait`, `pthread_cond_timedwait`, `sem_wait`, `sigwait`, `read`, `write`, `sleep`, `nanosleep`, `clock_nanosleep`, `accept`, `connect`, `recv`, `send`, `poll`, `select`, `epoll_wait`, `mq_receive`, `mq_send`, `open`, `close`, `fcntl` (some), `msgrcv`, `msgsnd`, `pause`, `pread`, `pwrite`, `wait`, `waitpid`.

```c
// Explicit cancellation point:
pthread_testcancel();  // if cancellation pending, thread exits here
```

### Cleanup handlers
Ensure resources are released on cancellation:
```c
void *worker(void *arg) {
    int *resource = malloc(1024);

    pthread_cleanup_push(free, resource);
    pthread_cleanup_push(unlock_wrapper, &mutex);

    pthread_mutex_lock(&mutex);
    while (condition)
        pthread_cond_wait(&cond, &mutex);  // cancellation point
    pthread_mutex_unlock(&mutex);

    pthread_cleanup_pop(0);  // unlock: 0 = don't execute (already unlocked)
    pthread_cleanup_pop(1);  // free: 1 = execute

    return NULL;
}
```

### Asynchronous cancellation
The thread can be canceled at **any point** — extremely dangerous. Only safe if the thread executes no library calls and touches no shared state:

```c
// ONLY use for pure computation:
pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
while (1) {
    compute();  // no library calls, no shared state
}
```

### Cancellation in RT
**Avoid cancellation in RT code.** It's hard to reason about correctness. Instead:
- Use a flag (`volatile sig_atomic_t` or `_Atomic`) checked in the loop
- Use a dedicated shutdown mechanism (eventfd, signal, etc.)

## Fork Safety in Threaded Programs

### The problem
After `fork()`, only the calling thread survives. Mutexes held by vanished threads remain locked — deadlock.

### pthread_atfork
```c
// Register fork handlers:
void prepare(void) {
    // Called in parent BEFORE fork
    // Lock all mutexes in consistent order
    pthread_mutex_lock(&mutex_a);
    pthread_mutex_lock(&mutex_b);
}

void parent(void) {
    // Called in parent AFTER fork
    pthread_mutex_unlock(&mutex_b);
    pthread_mutex_unlock(&mutex_a);
}

void child(void) {
    // Called in child AFTER fork
    // Re-initialize or unlock mutexes
    pthread_mutex_unlock(&mutex_b);
    pthread_mutex_unlock(&mutex_a);
}

pthread_atfork(prepare, parent, child);
```

### Practical advice (Butenhof)
1. Avoid `fork()` in multithreaded programs
2. If you must fork, immediately `exec()` — don't do anything else
3. Use `posix_spawn()` instead of `fork()+exec()`
4. If you can't exec, only call async-signal-safe functions in the child

## Thread Pools

### Fixed-size thread pool
```c
typedef struct {
    void (*function)(void *);
    void *arg;
} task_t;

typedef struct {
    pthread_t *threads;
    task_t *queue;
    int queue_size, queue_count, queue_head, queue_tail;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    int shutdown;
    int thread_count;
} threadpool_t;

void *worker(void *arg) {
    threadpool_t *pool = arg;
    while (1) {
        pthread_mutex_lock(&pool->lock);
        while (pool->queue_count == 0 && !pool->shutdown)
            pthread_cond_wait(&pool->not_empty, &pool->lock);

        if (pool->shutdown && pool->queue_count == 0) {
            pthread_mutex_unlock(&pool->lock);
            break;
        }

        task_t task = pool->queue[pool->queue_head];
        pool->queue_head = (pool->queue_head + 1) % pool->queue_size;
        pool->queue_count--;
        pthread_cond_signal(&pool->not_full);
        pthread_mutex_unlock(&pool->lock);

        task.function(task.arg);
    }
    return NULL;
}

void threadpool_submit(threadpool_t *pool, void (*fn)(void *), void *arg) {
    pthread_mutex_lock(&pool->lock);
    while (pool->queue_count == pool->queue_size)
        pthread_cond_wait(&pool->not_full, &pool->lock);

    pool->queue[pool->queue_tail] = (task_t){ fn, arg };
    pool->queue_tail = (pool->queue_tail + 1) % pool->queue_size;
    pool->queue_count++;
    pthread_cond_signal(&pool->not_empty);
    pthread_mutex_unlock(&pool->lock);
}

void threadpool_shutdown(threadpool_t *pool) {
    pthread_mutex_lock(&pool->lock);
    pool->shutdown = 1;
    pthread_cond_broadcast(&pool->not_empty);
    pthread_mutex_unlock(&pool->lock);
    for (int i = 0; i < pool->thread_count; i++)
        pthread_join(pool->threads[i], NULL);
}
```

### RT thread pool considerations
- Pre-create all threads during initialization
- Set RT scheduling and CPU affinity per thread
- Use `PTHREAD_PRIO_INHERIT` on the pool mutex
- Pre-allocate the task queue (no malloc in submit path)
- Use condition variables with `CLOCK_MONOTONIC`

## Work Queue Pattern

Butenhof's work queue — a thread pool with work items:

```c
typedef struct work_item {
    struct work_item *next;
    void (*routine)(void *);
    void *arg;
} work_item_t;

typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t  cv;
    work_item_t    *head;
    work_item_t    *tail;
    int             quit;
    int             parallelism;
    int             idle;
    int             count;
} workqueue_t;
```

Key difference from a simple thread pool: the work queue can grow its thread count dynamically based on demand (up to a maximum), and idle threads exit after a timeout.

## Thread-Safe Library Design

### Reentrant vs thread-safe
- **Reentrant**: Can be called simultaneously from multiple threads with no shared state. Strongest guarantee.
- **Thread-safe**: Can be called from multiple threads with internal synchronization. May have lock contention.

### Patterns for thread safety

**Per-instance locking** (best for data structures):
```c
typedef struct {
    pthread_mutex_t lock;
    // ... data ...
} safe_container_t;
```

**Global lock** (simplest, worst contention):
```c
static pthread_mutex_t global_lock = PTHREAD_MUTEX_INITIALIZER;
```

**Reader-writer lock** (read-heavy workloads):
```c
static pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;
```

**Lock-free** (expert-level, uses atomics):
```c
// CAS-based update:
_Atomic int counter;
int old = atomic_load(&counter);
while (!atomic_compare_exchange_weak(&counter, &old, old + 1))
    ;  // retry
```

### _r functions (POSIX reentrant alternatives)
```c
// NOT thread-safe:
struct tm *tm = localtime(&time);    // returns static buffer
char *s = strtok(str, delim);       // uses static state

// Thread-safe alternatives:
struct tm tm_buf;
localtime_r(&time, &tm_buf);        // caller provides buffer
char *saveptr;
char *s = strtok_r(str, delim, &saveptr);  // caller provides state
```

## C11 Atomics and Memory Ordering

### Atomic types
```c
#include <stdatomic.h>

_Atomic int counter = 0;
atomic_int counter2 = ATOMIC_VAR_INIT(0);  // equivalent
```

### Operations
```c
atomic_store(&var, value);
int val = atomic_load(&var);
int old = atomic_fetch_add(&var, 1);     // returns old value
int old = atomic_fetch_sub(&var, 1);
int old = atomic_fetch_or(&var, mask);
int old = atomic_fetch_and(&var, mask);
bool ok = atomic_compare_exchange_strong(&var, &expected, desired);
bool ok = atomic_compare_exchange_weak(&var, &expected, desired);
// weak can spuriously fail — use in retry loops
```

### Memory ordering
```c
atomic_store_explicit(&var, value, memory_order_release);
int val = atomic_load_explicit(&var, memory_order_acquire);

// memory_order_relaxed:  no ordering guarantees (fastest)
// memory_order_acquire:  subsequent reads/writes not reordered before this
// memory_order_release:  preceding reads/writes not reordered after this
// memory_order_acq_rel:  both acquire and release
// memory_order_seq_cst:  full sequential consistency (default, slowest)
```

### Common patterns

**Publish/subscribe** (release/acquire):
```c
// Publisher:
data = prepare_data();
atomic_store_explicit(&data_ready, 1, memory_order_release);

// Subscriber:
while (!atomic_load_explicit(&data_ready, memory_order_acquire))
    ;  // spin or yield
use(data);  // guaranteed to see publisher's writes
```

**Atomic flag** (spinlock):
```c
atomic_flag lock = ATOMIC_FLAG_INIT;

// Lock:
while (atomic_flag_test_and_set_explicit(&lock, memory_order_acquire))
    ;  // spin

// Unlock:
atomic_flag_clear_explicit(&lock, memory_order_release);
```

### Memory fences
```c
atomic_thread_fence(memory_order_acquire);
atomic_thread_fence(memory_order_release);
atomic_thread_fence(memory_order_seq_cst);
atomic_signal_fence(memory_order_release);  // compiler-only barrier (for signal handlers)
```
