# Synchronization

## Table of Contents
- [Mutexes](#mutexes)
- [Mutex Attributes](#mutex-attributes)
- [Priority Inversion and Inheritance](#priority-inversion-and-inheritance)
- [Condition Variables](#condition-variables)
- [Read-Write Locks](#read-write-locks)
- [Barriers](#barriers)
- [Spinlocks](#spinlocks)
- [Synchronization Design Patterns](#synchronization-design-patterns)

## Mutexes

### Basic usage
```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// Or dynamic initialization:
pthread_mutex_t mutex;
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutex_init(&mutex, &attr);
pthread_mutexattr_destroy(&attr);

// Lock/unlock:
pthread_mutex_lock(&mutex);       // blocks until acquired
// ... critical section ...
pthread_mutex_unlock(&mutex);

// Non-blocking:
int ret = pthread_mutex_trylock(&mutex);
if (ret == EBUSY) { /* already held */ }

// Timed:
struct timespec abstime;
clock_gettime(CLOCK_REALTIME, &abstime);
abstime.tv_sec += 1;  // 1 second timeout
ret = pthread_mutex_timedlock(&mutex, &abstime);
if (ret == ETIMEDOUT) { /* timed out */ }

// Cleanup:
pthread_mutex_destroy(&mutex);
```

### Rules
- Only the thread that locked a mutex may unlock it (except `PTHREAD_MUTEX_NORMAL` — UB if wrong thread unlocks)
- Locking an already-held normal mutex = **deadlock**
- Unlocking an unheld mutex = **undefined behavior** (except error-checking type)
- Destroying a locked mutex = **undefined behavior**

## Mutex Attributes

```c
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
```

### Type
```c
pthread_mutexattr_settype(&attr, type);
```

| Type | Re-lock by owner | Unlock by non-owner | Dead-on-error |
|------|-----------------|--------------------|----|
| `PTHREAD_MUTEX_NORMAL` | Deadlock | UB | No |
| `PTHREAD_MUTEX_ERRORCHECK` | Returns `EDEADLK` | Returns `EPERM` | No |
| `PTHREAD_MUTEX_RECURSIVE` | Succeeds (ref-counted) | Returns `EPERM` | No |
| `PTHREAD_MUTEX_DEFAULT` | Implementation-defined | Implementation-defined | — |

**For RT**: Use `ERRORCHECK` during development, `NORMAL` for production after debugging. Avoid `RECURSIVE` — it usually signals a design problem.

### Process-shared
```c
pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
```
The mutex can be placed in shared memory and used across processes. Requires the mutex is in `mmap`'d or `shm_open`'d memory, not on the stack.

### Robust mutexes (GNU Make 3.82+ / POSIX.1-2008)
```c
pthread_mutexattr_setrobust(&attr, PTHREAD_MUTEX_ROBUST);
```
If the owning thread dies while holding the mutex, the next `pthread_mutex_lock` returns `EOWNERDEAD` instead of hanging forever:

```c
int ret = pthread_mutex_lock(&mutex);
if (ret == EOWNERDEAD) {
    // Previous owner died — state may be inconsistent
    // Fix up shared state, then:
    pthread_mutex_consistent(&mutex);
    // Now use normally
}
```

## Priority Inversion and Inheritance

**Priority inversion**: A high-priority thread blocks on a mutex held by a low-priority thread, which is preempted by a medium-priority thread. The high-priority thread is effectively running at low priority.

### Priority inheritance protocol
```c
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
```
When a high-priority thread blocks on the mutex, the owning thread temporarily inherits the waiter's priority. Linux implements this via PI-futexes.

### Priority ceiling protocol
```c
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_PROTECT);
pthread_mutexattr_setprioceiling(&attr, 80);  // ceiling priority
```
Any thread that locks the mutex runs at the ceiling priority while holding it. Prevents inversion but requires knowing the maximum priority of all potential users.

### Choosing a protocol
| Protocol | Use case |
|----------|----------|
| `PRIO_NONE` | Non-RT code, or when inversion is acceptable |
| `PRIO_INHERIT` | General RT — most common and recommended |
| `PRIO_PROTECT` | Hard RT with known priority set, or when avoiding the overhead of PI tracking |

**For most RT applications, always use `PTHREAD_PRIO_INHERIT`.**

### Complete RT mutex setup
```c
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);  // dev
// pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_NORMAL);   // prod

pthread_mutex_t mutex;
pthread_mutex_init(&mutex, &attr);
pthread_mutexattr_destroy(&attr);
```

## Condition Variables

Allow threads to wait for a predicate to become true:

```c
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// Producer:
pthread_mutex_lock(&mutex);
shared_data_ready = 1;
pthread_cond_signal(&cond);      // wake one waiter
// pthread_cond_broadcast(&cond); // wake all waiters
pthread_mutex_unlock(&mutex);

// Consumer — MUST use a while loop (spurious wakeups):
pthread_mutex_lock(&mutex);
while (!shared_data_ready) {
    pthread_cond_wait(&cond, &mutex);
    // atomically: unlock mutex → sleep → [wakeup] → lock mutex
}
// shared_data_ready is true, mutex is held
process(shared_data);
pthread_mutex_unlock(&mutex);
```

### Timed wait
```c
struct timespec abstime;
clock_gettime(CLOCK_REALTIME, &abstime);  // or CLOCK_MONOTONIC with attr
abstime.tv_sec += 5;

int ret = pthread_cond_timedwait(&cond, &mutex, &abstime);
if (ret == ETIMEDOUT) { /* timed out, mutex is re-acquired */ }
```

### Using CLOCK_MONOTONIC (recommended for RT)
```c
pthread_condattr_t cattr;
pthread_condattr_init(&cattr);
pthread_condattr_setclock(&cattr, CLOCK_MONOTONIC);

pthread_cond_t cond;
pthread_cond_init(&cond, &cattr);
pthread_condattr_destroy(&cattr);

// Now timedwait uses CLOCK_MONOTONIC:
struct timespec abstime;
clock_gettime(CLOCK_MONOTONIC, &abstime);
abstime.tv_sec += 1;
pthread_cond_timedwait(&cond, &mutex, &abstime);
```

### Rules
- Always check the predicate in a **while loop** — never `if`
- The mutex MUST be held when calling `wait`/`timedwait`
- `signal` vs `broadcast`: use `signal` when exactly one waiter can make progress; use `broadcast` when the condition could satisfy multiple waiters or you're not sure
- Signal/broadcast with the mutex held (simpler, correct) or after unlocking (slightly more efficient but risks races in some patterns)

## Read-Write Locks

Multiple simultaneous readers or one exclusive writer:

```c
pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;

// Reader:
pthread_rwlock_rdlock(&rwlock);
// ... read shared data ...
pthread_rwlock_unlock(&rwlock);

// Writer:
pthread_rwlock_wrlock(&rwlock);
// ... modify shared data ...
pthread_rwlock_unlock(&rwlock);

// Non-blocking / timed variants:
pthread_rwlock_tryrdlock(&rwlock);
pthread_rwlock_trywrlock(&rwlock);
pthread_rwlock_timedrdlock(&rwlock, &abstime);
pthread_rwlock_timedwrlock(&rwlock, &abstime);
```

### Writer starvation
Default Linux implementation favors readers — a steady stream of readers can starve writers. Set writer preference:

```c
pthread_rwlockattr_t attr;
pthread_rwlockattr_init(&attr);
pthread_rwlockattr_setkind_np(&attr, PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP);
pthread_rwlock_init(&rwlock, &attr);
```

### When to use rwlocks
- Shared data is read much more often than written
- Read operations are long enough to benefit from parallelism
- If reads are short, a plain mutex may be faster due to rwlock overhead
- **Not recommended for hard RT** — no priority inheritance support in most implementations

## Barriers

Synchronize a group of threads at a rendez-vous point:

```c
pthread_barrier_t barrier;
pthread_barrier_init(&barrier, NULL, NUM_THREADS);

// In each thread:
// ... phase 1 work ...
int ret = pthread_barrier_wait(&barrier);
// All threads blocked until NUM_THREADS arrive
// Exactly one thread gets PTHREAD_BARRIER_SERIAL_THREAD
if (ret == PTHREAD_BARRIER_SERIAL_THREAD) {
    // This one thread can do the "merge" step
}
// ... phase 2 work ...

pthread_barrier_destroy(&barrier);  // only after all threads pass
```

Useful for phased computation (matrix operations, simulations, parallel pipelines).

## Spinlocks

Busy-wait locks — never sleep, just spin:

```c
pthread_spinlock_t spin;
pthread_spin_init(&spin, PTHREAD_PROCESS_PRIVATE);

pthread_spin_lock(&spin);
// ... very short critical section ...
pthread_spin_unlock(&spin);

pthread_spin_destroy(&spin);
```

### When to use
- Critical section is **very short** (< ~1 µs)
- Threads are pinned to dedicated CPUs (spinning doesn't waste shared CPU time)
- On PREEMPT_RT, spinlocks are often converted to sleeping locks by the kernel — understand your kernel's behavior

### When NOT to use
- If the critical section might block (I/O, syscall, page fault)
- Without CPU pinning — spinning wastes time for other threads
- In most applications — mutexes with futex-based implementation are nearly as fast for short critical sections

## Synchronization Design Patterns

### Monitor pattern (Butenhof)
Encapsulate shared state + mutex + condition variables:

```c
typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    int items[QUEUE_SIZE];
    int head, tail, count;
} bounded_queue_t;

void queue_init(bounded_queue_t *q) {
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
    q->head = q->tail = q->count = 0;
}

void queue_put(bounded_queue_t *q, int item) {
    pthread_mutex_lock(&q->lock);
    while (q->count == QUEUE_SIZE)
        pthread_cond_wait(&q->not_full, &q->lock);
    q->items[q->tail] = item;
    q->tail = (q->tail + 1) % QUEUE_SIZE;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
}

int queue_get(bounded_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0)
        pthread_cond_wait(&q->not_empty, &q->lock);
    int item = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_SIZE;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return item;
}
```

### Lock ordering to prevent deadlocks
```c
// ALWAYS acquire locks in a consistent global order:
// Rule: lock A before lock B (by address, ID, or hierarchy)
if (&lockA < &lockB) {
    pthread_mutex_lock(&lockA);
    pthread_mutex_lock(&lockB);
} else {
    pthread_mutex_lock(&lockB);
    pthread_mutex_lock(&lockA);
}
```

### Double-checked locking (with C11 atomics)
```c
#include <stdatomic.h>

static atomic_intptr_t instance = 0;
static pthread_mutex_t init_lock = PTHREAD_MUTEX_INITIALIZER;

struct resource *get_instance(void) {
    struct resource *p = (struct resource *)atomic_load_explicit(
        &instance, memory_order_acquire);
    if (!p) {
        pthread_mutex_lock(&init_lock);
        p = (struct resource *)atomic_load_explicit(
            &instance, memory_order_relaxed);
        if (!p) {
            p = create_resource();
            atomic_store_explicit(&instance, (intptr_t)p,
                                  memory_order_release);
        }
        pthread_mutex_unlock(&init_lock);
    }
    return p;
}
```

Prefer `pthread_once` over double-checked locking when possible — it's simpler and always correct.
