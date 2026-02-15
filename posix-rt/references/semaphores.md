# Semaphores

## Table of Contents
- [Named vs Unnamed Semaphores](#named-vs-unnamed-semaphores)
- [Named Semaphores](#named-semaphores)
- [Unnamed Semaphores](#unnamed-semaphores)
- [Semaphore Operations](#semaphore-operations)
- [Process-Shared Semaphores](#process-shared-semaphores)
- [Patterns and Use Cases](#patterns-and-use-cases)
- [Semaphores vs Mutexes vs Condition Variables](#semaphores-vs-mutexes-vs-condition-variables)

## Named vs Unnamed Semaphores

| Feature | Named | Unnamed |
|---------|-------|---------|
| Identifier | String name (`/sem_name`) | Memory address |
| Scope | Any process that knows the name | Threads in same process, or processes sharing memory |
| Persistence | Kernel-persistent until `sem_unlink` | Lifetime of containing memory |
| Creation | `sem_open` | `sem_init` |
| Destruction | `sem_close` + `sem_unlink` | `sem_destroy` |
| Backing | `/dev/shm/sem.*` on Linux | In user memory (stack, heap, shared mem) |

## Named Semaphores

```c
#include <semaphore.h>
#include <fcntl.h>

// Create or open:
sem_t *sem = sem_open("/mysem", O_CREAT | O_EXCL, 0660, 1);
//                     name     flags              mode  initial_value
if (sem == SEM_FAILED) perror("sem_open");

// Open existing:
sem_t *sem = sem_open("/mysem", 0);

// Close (per-process):
sem_close(sem);

// Remove (system-wide):
sem_unlink("/mysem");
// Like files: actual removal happens when last reference closes
```

### Naming rules
Same as message queues: must start with `/`, no additional `/`.

## Unnamed Semaphores

```c
sem_t sem;

// Initialize:
int pshared = 0;  // 0 = thread-shared, 1 = process-shared
int initial_value = 1;
sem_init(&sem, pshared, initial_value);

// Destroy:
sem_destroy(&sem);
// Must not destroy while any thread is waiting on it
```

For process-shared unnamed semaphores, the `sem_t` must reside in shared memory (`mmap` or `shm_open`).

## Semaphore Operations

### Wait (decrement / P / down)
```c
// Blocking:
sem_wait(&sem);
// Decrements value. Blocks if value is 0.

// Non-blocking:
int ret = sem_trywait(&sem);
if (ret == -1 && errno == EAGAIN) { /* value was 0 */ }

// Timed (absolute time, uses CLOCK_REALTIME):
struct timespec abstime;
clock_gettime(CLOCK_REALTIME, &abstime);
abstime.tv_sec += 2;
ret = sem_timedwait(&sem, &abstime);
if (ret == -1 && errno == ETIMEDOUT) { /* timed out */ }
```

**Note**: `sem_timedwait` uses `CLOCK_REALTIME`, not `CLOCK_MONOTONIC`. This is a known POSIX limitation. On Linux, there's no standard way to use `CLOCK_MONOTONIC` with semaphores (unlike condition variables which support `pthread_condattr_setclock`).

### Post (increment / V / up)
```c
sem_post(&sem);
// Increments value. If threads are waiting, one is woken.
// This is ONE OF THE FEW async-signal-safe functions.
```

`sem_post` is async-signal-safe — it can be called from a signal handler. This makes semaphores uniquely useful for signal-to-thread communication.

### Get value
```c
int val;
sem_getvalue(&sem, &val);
// If val > 0: number of available resources
// If val == 0: one or more threads may be waiting
// Linux: val can be negative (number of waiters), but this is non-portable
```

**Warning**: The value is immediately stale — another thread could change it between `sem_getvalue` and your next operation. Use only for debugging/monitoring.

## Process-Shared Semaphores

### Named (inherently process-shared)
```c
// Process A:
sem_t *sem = sem_open("/shared_sem", O_CREAT, 0660, 0);
// ... wait for process B to signal ...
sem_wait(sem);

// Process B:
sem_t *sem = sem_open("/shared_sem", 0);
// ... signal process A ...
sem_post(sem);
```

### Unnamed in shared memory
```c
#include <sys/mman.h>
#include <fcntl.h>

// Create shared memory:
int fd = shm_open("/shared", O_CREAT | O_RDWR, 0660);
ftruncate(fd, sizeof(sem_t));
sem_t *sem = mmap(NULL, sizeof(sem_t), PROT_READ | PROT_WRITE,
                  MAP_SHARED, fd, 0);
close(fd);

// Initialize (once, by one process):
sem_init(sem, 1, 0);  // pshared=1

// Both processes can now sem_wait/sem_post on sem
```

## Patterns and Use Cases

### Binary semaphore (mutex alternative)
```c
sem_t binary_sem;
sem_init(&binary_sem, 0, 1);  // initial value 1

sem_wait(&binary_sem);    // "lock"
// critical section
sem_post(&binary_sem);    // "unlock"
```

Unlike mutexes: any thread can post (not just the one that waited). No ownership, no priority inheritance. **Prefer mutexes for mutual exclusion.**

### Counting semaphore (resource pool)
```c
#define MAX_CONNECTIONS 10
sem_t conn_sem;
sem_init(&conn_sem, 0, MAX_CONNECTIONS);

// Acquire connection:
sem_wait(&conn_sem);
connection_t *conn = pool_get();

// Release:
pool_put(conn);
sem_post(&conn_sem);
```

### Producer-consumer synchronization
```c
sem_t items;    // counts available items
sem_t spaces;   // counts available spaces
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void init(void) {
    sem_init(&items, 0, 0);
    sem_init(&spaces, 0, BUFFER_SIZE);
}

void producer(int item) {
    sem_wait(&spaces);           // wait for space
    pthread_mutex_lock(&mutex);
    buffer[write_pos++ % BUFFER_SIZE] = item;
    pthread_mutex_unlock(&mutex);
    sem_post(&items);            // signal item available
}

int consumer(void) {
    sem_wait(&items);            // wait for item
    pthread_mutex_lock(&mutex);
    int item = buffer[read_pos++ % BUFFER_SIZE];
    pthread_mutex_unlock(&mutex);
    sem_post(&spaces);           // signal space available
    return item;
}
```

### Signal handler to thread communication
```c
// Semaphore post is async-signal-safe:
sem_t event_sem;
sem_init(&event_sem, 0, 0);

void signal_handler(int sig) {
    sem_post(&event_sem);  // safe to call here
}

void *worker(void *arg) {
    while (1) {
        sem_wait(&event_sem);
        handle_event();
    }
}
```

## Semaphores vs Mutexes vs Condition Variables

| Feature | Semaphore | Mutex | Condvar + Mutex |
|---------|-----------|-------|-----------------|
| Ownership | None | Thread that locked | N/A |
| Priority inheritance | No | Yes (`PRIO_INHERIT`) | Via mutex |
| Async-signal-safe | `sem_post` only | No | No |
| Cross-process | Yes (named or shared) | Yes (with `PROCESS_SHARED`) | Yes (with `PROCESS_SHARED`) |
| Counting | Yes (any non-negative) | Binary only | N/A |
| Error detection | Limited | `ERRORCHECK` type | Via mutex |
| Deadlock detection | No | `ERRORCHECK` type | No |
| Best for | Counting resources, signal-to-thread | Mutual exclusion | Complex predicates |

**Guidelines**:
- **Mutual exclusion**: Use a mutex
- **Waiting for a condition**: Use condvar + mutex
- **Counting resources**: Use a semaphore
- **Signal handler notification**: Use a semaphore (`sem_post`)
- **RT with priority concerns**: Use mutex with `PRIO_INHERIT`
