# Clocks & Timers

## Table of Contents
- [POSIX Clocks](#posix-clocks)
- [Reading Clocks](#reading-clocks)
- [Sleeping](#sleeping)
- [POSIX Timers](#posix-timers)
- [timerfd (Linux)](#timerfd-linux)
- [Periodic Loop Patterns](#periodic-loop-patterns)
- [Timestamp Arithmetic](#timestamp-arithmetic)
- [High-Resolution Timing](#high-resolution-timing)

## POSIX Clocks

| Clock | Description | Use for |
|-------|-------------|---------|
| `CLOCK_REALTIME` | Wall-clock time. Can jump (NTP, `settimeofday`) | Timestamps, logging, file times |
| `CLOCK_MONOTONIC` | Steady clock since unspecified epoch. Never jumps | Intervals, deadlines, timeouts |
| `CLOCK_MONOTONIC_RAW` | Like MONOTONIC but not adjusted by NTP (Linux) | Benchmarking, hardware timing |
| `CLOCK_BOOTTIME` | Like MONOTONIC but includes suspend time (Linux) | Timeouts that should include sleep |
| `CLOCK_REALTIME_COARSE` | Fast but ~1ms resolution (Linux) | When speed > precision |
| `CLOCK_MONOTONIC_COARSE` | Fast but ~1ms resolution (Linux) | When speed > precision |
| `CLOCK_PROCESS_CPUTIME_ID` | CPU time consumed by process | Profiling |
| `CLOCK_THREAD_CPUTIME_ID` | CPU time consumed by thread | Profiling |

**Rule**: Use `CLOCK_MONOTONIC` for all RT timing. Use `CLOCK_REALTIME` only when you need wall-clock time (logging, external systems). Never use `CLOCK_REALTIME` for intervals or deadlines — NTP adjustments can cause jumps.

## Reading Clocks

```c
#include <time.h>

struct timespec ts;
clock_gettime(CLOCK_MONOTONIC, &ts);
// ts.tv_sec  = seconds
// ts.tv_nsec = nanoseconds (0–999999999)

// Clock resolution:
struct timespec res;
clock_getres(CLOCK_MONOTONIC, &res);
// Typically 1 ns on modern Linux (doesn't mean 1 ns accuracy)
```

### Deprecated alternatives
```c
// OLD — deprecated in POSIX.1-2008, removed in 2024:
struct timeval tv;
gettimeofday(&tv, NULL);  // microsecond resolution only

// REPLACE WITH:
struct timespec ts;
clock_gettime(CLOCK_REALTIME, &ts);
```

## Sleeping

### clock_nanosleep (preferred for RT)
```c
// Relative sleep:
struct timespec dur = { .tv_sec = 0, .tv_nsec = 500000 };  // 500 µs
clock_nanosleep(CLOCK_MONOTONIC, 0, &dur, NULL);

// Absolute sleep (CRITICAL for periodic loops):
struct timespec wakeup;
clock_gettime(CLOCK_MONOTONIC, &wakeup);
wakeup.tv_sec += 1;
clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &wakeup, NULL);
```

**Why absolute sleep matters**: Relative sleep accumulates drift. If your loop body takes variable time, `sleep(period)` sleeps *after* the work, so each cycle is `work_time + period`. Absolute sleep targets the next wall-clock instant, so drift is bounded.

### nanosleep (older)
```c
struct timespec req = { .tv_sec = 0, .tv_nsec = 1000000 };  // 1 ms
struct timespec rem;
while (nanosleep(&req, &rem) == -1 && errno == EINTR)
    req = rem;  // interrupted by signal, sleep the remainder
```
Uses `CLOCK_REALTIME` implicitly. Prefer `clock_nanosleep` with `CLOCK_MONOTONIC`.

## POSIX Timers

Create a timer that fires signals or spawns threads:

```c
#include <signal.h>
#include <time.h>

// Signal-based notification:
struct sigevent sev = {
    .sigev_notify = SIGEV_SIGNAL,
    .sigev_signo = SIGRTMIN,
    .sigev_value.sival_ptr = &my_data,
};

timer_t timerid;
timer_create(CLOCK_MONOTONIC, &sev, &timerid);

// Thread-based notification:
struct sigevent sev_thread = {
    .sigev_notify = SIGEV_THREAD,
    .sigev_notify_function = timer_handler,
    .sigev_value.sival_ptr = &my_data,
    .sigev_notify_attributes = NULL,  // or pthread_attr_t*
};
timer_create(CLOCK_MONOTONIC, &sev_thread, &timerid);
```

### Arming the timer
```c
struct itimerspec its = {
    .it_value = { .tv_sec = 1, .tv_nsec = 0 },      // first fire: 1s
    .it_interval = { .tv_sec = 0, .tv_nsec = 10000000 }, // repeat: 10ms
};

// Relative:
timer_settime(timerid, 0, &its, NULL);

// Absolute:
timer_settime(timerid, TIMER_ABSTIME, &its, NULL);
```

### Checking overruns
```c
int overruns = timer_getoverrun(timerid);
// Number of timer expirations that occurred between signal generation
// and delivery. Critical for detecting if RT processing can't keep up.
```

### Cleanup
```c
timer_delete(timerid);
```

### Notification types

| `sigev_notify` | Behavior |
|---------------|----------|
| `SIGEV_SIGNAL` | Deliver signal `sigev_signo` |
| `SIGEV_THREAD` | Call `sigev_notify_function` in new thread |
| `SIGEV_NONE` | No notification (poll with `timer_gettime`) |
| `SIGEV_THREAD_ID` | Signal to specific thread (Linux, use with `sigev_notify_thread_id`) |

For RT, prefer `SIGEV_SIGNAL` with `sigwaitinfo` in a dedicated thread, or use `timerfd`.

## timerfd (Linux)

Expose timers as file descriptors — integrates with `epoll`, `poll`, `select`, and `io_uring`:

```c
#include <sys/timerfd.h>

// Create:
int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);

// Arm (periodic 10ms):
struct itimerspec its = {
    .it_value    = { .tv_sec = 0, .tv_nsec = 10000000 },
    .it_interval = { .tv_sec = 0, .tv_nsec = 10000000 },
};
timerfd_settime(tfd, 0, &its, NULL);

// Wait for timer:
uint64_t expirations;
read(tfd, &expirations, sizeof(expirations));
// expirations = number of times the timer fired since last read
// If > 1, you missed deadlines

// With epoll:
struct epoll_event ev = { .events = EPOLLIN, .data.fd = tfd };
epoll_ctl(epfd, EPOLL_CTL_ADD, tfd, &ev);
```

### timerfd vs POSIX timers
| Feature | POSIX timer | timerfd |
|---------|------------|---------|
| Notification | Signal or thread | File descriptor |
| Event loop integration | Difficult | Natural (epoll/poll) |
| Overrun detection | `timer_getoverrun` | Read count > 1 |
| Portability | POSIX standard | Linux-specific |
| Recommended for | Simple periodic tasks | Event-driven architectures |

## Periodic Loop Patterns

### Pattern 1: Absolute clock_nanosleep (simplest, recommended)
```c
void *periodic_thread(void *arg) {
    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);

    while (running) {
        // Advance to next period:
        next.tv_nsec += PERIOD_NS;
        while (next.tv_nsec >= 1000000000L) {
            next.tv_nsec -= 1000000000L;
            next.tv_sec++;
        }

        // Do work:
        do_rt_work();

        // Sleep until next period:
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    return NULL;
}
```

### Pattern 2: timerfd with epoll (event-driven)
```c
void event_loop(int tfd) {
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    struct epoll_event ev = { .events = EPOLLIN, .data.fd = tfd };
    epoll_ctl(epfd, EPOLL_CTL_ADD, tfd, &ev);

    while (running) {
        struct epoll_event events[8];
        int n = epoll_wait(epfd, events, 8, -1);
        for (int i = 0; i < n; i++) {
            if (events[i].data.fd == tfd) {
                uint64_t exp;
                read(tfd, &exp, sizeof(exp));
                if (exp > 1)
                    log_overrun(exp - 1);
                do_rt_work();
            }
        }
    }
}
```

### Pattern 3: Signal-driven (Gallmeister pattern)
```c
void periodic_with_signals(void) {
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIGRTMIN);
    pthread_sigmask(SIG_BLOCK, &set, NULL);

    timer_t timerid;
    struct sigevent sev = {
        .sigev_notify = SIGEV_SIGNAL,
        .sigev_signo = SIGRTMIN,
    };
    timer_create(CLOCK_MONOTONIC, &sev, &timerid);

    struct itimerspec its = {
        .it_value    = { .tv_nsec = PERIOD_NS },
        .it_interval = { .tv_nsec = PERIOD_NS },
    };
    timer_settime(timerid, 0, &its, NULL);

    while (running) {
        siginfo_t info;
        sigwaitinfo(&set, &info);
        int overrun = timer_getoverrun(timerid);
        do_rt_work();
    }
}
```

## Timestamp Arithmetic

### Comparing timespecs
```c
static inline int timespec_cmp(const struct timespec *a,
                                const struct timespec *b) {
    if (a->tv_sec != b->tv_sec)
        return (a->tv_sec > b->tv_sec) ? 1 : -1;
    if (a->tv_nsec != b->tv_nsec)
        return (a->tv_nsec > b->tv_nsec) ? 1 : -1;
    return 0;
}
```

### Adding / subtracting
```c
static inline struct timespec timespec_add(struct timespec a,
                                            struct timespec b) {
    struct timespec result = {
        .tv_sec = a.tv_sec + b.tv_sec,
        .tv_nsec = a.tv_nsec + b.tv_nsec,
    };
    if (result.tv_nsec >= 1000000000L) {
        result.tv_nsec -= 1000000000L;
        result.tv_sec++;
    }
    return result;
}

static inline struct timespec timespec_sub(struct timespec a,
                                            struct timespec b) {
    struct timespec result = {
        .tv_sec = a.tv_sec - b.tv_sec,
        .tv_nsec = a.tv_nsec - b.tv_nsec,
    };
    if (result.tv_nsec < 0) {
        result.tv_nsec += 1000000000L;
        result.tv_sec--;
    }
    return result;
}
```

### Converting
```c
// timespec → nanoseconds:
static inline int64_t timespec_to_ns(struct timespec ts) {
    return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

// nanoseconds → timespec:
static inline struct timespec ns_to_timespec(int64_t ns) {
    return (struct timespec){
        .tv_sec = ns / 1000000000LL,
        .tv_nsec = ns % 1000000000LL,
    };
}
```

## High-Resolution Timing

### VDSO optimization
`clock_gettime(CLOCK_MONOTONIC)` on Linux uses VDSO — no syscall, reads from a shared kernel page. Extremely fast (~20 ns). The `_COARSE` variants are even faster (~5 ns) with ~1 ms resolution.

### TSC-based timing (x86, for micro-benchmarks)
```c
#include <x86intrin.h>

uint64_t start = __rdtsc();
// ... work ...
uint64_t end = __rdtsc();
uint64_t cycles = end - start;

// Convert to nanoseconds (approximate):
// cycles * 1e9 / tsc_frequency
```

Use `CLOCK_MONOTONIC_RAW` for benchmarks where NTP adjustment matters. Use TSC only for sub-microsecond measurements in controlled environments.
