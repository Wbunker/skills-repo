---
name: posix-rt
description: >
  Expert-level POSIX real-time and systems programming assistance covering
  threads, synchronization, scheduling, IPC, signals, timers, async I/O,
  memory management, and Linux real-time system configuration. Use when the
  user is writing C/C++ systems code involving pthreads, mutexes, condition
  variables, semaphores, shared memory, message queues, real-time signals,
  POSIX timers, async I/O (aio or io_uring), memory locking, process
  scheduling (SCHED_FIFO, SCHED_RR, SCHED_DEADLINE), CPU affinity, epoll,
  eventfd, timerfd, signalfd, PREEMPT_RT, or any POSIX.1b/POSIX.1c real-time
  extension. Also triggers on mentions of priority inversion, priority
  inheritance, lock-free programming, deterministic latency, mlockall,
  clock_gettime, posix_spawn, or cgroups for real-time workloads.
---

# POSIX Real-Time Programming Expert

## Standards Context

All historical POSIX real-time standards are unified into **POSIX.1-2024** (IEEE Std 1003.1-2024, Issue 8):
- POSIX.1b (formerly POSIX.4) — real-time extensions (scheduling, timers, AIO, IPC, memory locking)
- POSIX.1c (formerly POSIX.4a) — threads (pthreads)

Real-time features are optional feature groups. Check availability:
```c
#include <unistd.h>
// _POSIX_TIMERS, _POSIX_PRIORITY_SCHEDULING, _POSIX_MESSAGE_PASSING,
// _POSIX_MEMLOCK, _POSIX_SHARED_MEMORY_OBJECTS, _POSIX_SEMAPHORES,
// _POSIX_THREADS, _POSIX_ASYNCHRONOUS_IO
```

Compile with: `-D_POSIX_C_SOURCE=200809L` (or `_GNU_SOURCE` for Linux extensions).
Link with: `-lpthread` and `-lrt` (older systems; modern glibc integrates `-lrt`).

## Essential Headers

| Header | Purpose |
|--------|---------|
| `<pthread.h>` | Threads, mutexes, conditions, rwlocks, barriers |
| `<sched.h>` | Scheduling policies, CPU affinity |
| `<time.h>` | `clock_gettime`, `clock_nanosleep`, `timer_create` |
| `<signal.h>` | Real-time signals, `sigqueue`, `sigwaitinfo` |
| `<semaphore.h>` | Named and unnamed semaphores |
| `<mqueue.h>` | POSIX message queues |
| `<sys/mman.h>` | `shm_open`, `mmap`, `mlockall`, `mlock` |
| `<aio.h>` | POSIX async I/O |
| `<sys/epoll.h>` | Linux epoll |
| `<sys/timerfd.h>` | Linux timerfd |
| `<sys/signalfd.h>` | Linux signalfd |
| `<sys/eventfd.h>` | Linux eventfd |
| `<liburing.h>` | Linux io_uring (liburing) |

## Real-Time Application Checklist

1. Use `CLOCK_MONOTONIC` for all interval/deadline timing (never `CLOCK_REALTIME`)
2. Lock memory early: `mlockall(MCL_CURRENT | MCL_FUTURE)` + pre-fault stack/heap
3. Set RT scheduling: `SCHED_FIFO` or `SCHED_DEADLINE`
4. Pin RT threads to isolated CPUs: `pthread_setaffinity_np`
5. Use `PTHREAD_PRIO_INHERIT` on all mutexes shared with RT threads
6. Never call unbounded-time functions from RT threads (malloc, printf, file I/O)
7. Pre-allocate all resources before entering the RT loop
8. Use `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, ...)` for periodic loops

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Threads** | [references/threads.md](references/threads.md) | Thread creation, attributes, lifecycle, stack management, detach vs join |
| **Synchronization** | [references/synchronization.md](references/synchronization.md) | Mutexes, condition variables, rwlocks, barriers, spinlocks, priority inheritance/ceiling |
| **Scheduling** | [references/scheduling.md](references/scheduling.md) | `SCHED_FIFO`, `SCHED_RR`, `SCHED_DEADLINE`, CPU affinity, priority management |
| **Clocks & Timers** | [references/clocks-timers.md](references/clocks-timers.md) | `clock_gettime`, `clock_nanosleep`, `timer_create`, `timerfd`, periodic loops |
| **Signals** | [references/signals.md](references/signals.md) | Real-time signals, `sigqueue`, `sigwaitinfo`, `signalfd`, signals + threads |
| **Message Queues** | [references/message-queues.md](references/message-queues.md) | POSIX mq_* API, priority messages, notification, attributes |
| **Semaphores** | [references/semaphores.md](references/semaphores.md) | Named/unnamed semaphores, process-shared, `sem_timedwait` |
| **Shared Memory** | [references/shared-memory.md](references/shared-memory.md) | `shm_open`, `mmap`, process-shared synchronization, memory-mapped files |
| **Memory Locking** | [references/memory-locking.md](references/memory-locking.md) | `mlockall`, `mlock`, pre-faulting, stack pre-allocation, `madvise` |
| **Async I/O** | [references/async-io.md](references/async-io.md) | POSIX AIO, `io_uring`, `epoll`, `eventfd`, event loop patterns |
| **Process Management** | [references/process-management.md](references/process-management.md) | `fork`, `exec`, `posix_spawn`, `waitpid`, process groups, RT and fork |
| **Advanced Threads** | [references/advanced-threads.md](references/advanced-threads.md) | Thread-specific data, cancellation, fork safety, signal handling in threads, thread pools |
| **System Setup** | [references/system-setup.md](references/system-setup.md) | PREEMPT_RT, CPU isolation, cgroups v2, kernel tuning, boot parameters, capabilities |
| **Debugging** | [references/debugging.md](references/debugging.md) | Latency tracing, `ftrace`, `cyclictest`, priority inversion detection, common RT pitfalls, helgrind/TSAN |
