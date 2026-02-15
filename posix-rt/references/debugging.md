# Debugging

## Table of Contents
- [RT Debugging Philosophy](#rt-debugging-philosophy)
- [Latency Measurement](#latency-measurement)
- [ftrace](#ftrace)
- [Detecting Priority Inversion](#detecting-priority-inversion)
- [Thread Sanitizer (TSAN)](#thread-sanitizer-tsan)
- [Helgrind](#helgrind)
- [Common RT Bugs and Symptoms](#common-rt-bugs-and-symptoms)
- [Debugging Deadlocks](#debugging-deadlocks)
- [Production Monitoring](#production-monitoring)
- [Debugging Checklist](#debugging-checklist)

## RT Debugging Philosophy

RT bugs fall into categories:

1. **Latency violations** — missed deadlines, jitter
2. **Correctness bugs** — races, deadlocks, priority inversion
3. **Resource exhaustion** — memory, file descriptors, signal queue overflow

The challenge: traditional debugging (printf, gdb breakpoints) often **masks RT bugs** because the debugger changes timing. Use non-intrusive tracing.

## Latency Measurement

### cyclictest — the gold standard
```bash
# Install:
sudo apt install rt-tests

# Basic test:
sudo cyclictest --mlockall --smp --priority=80 \
    --interval=200 --distance=0 --loops=100000 \
    --histogram=100 --histfile=histogram.txt

# Flags:
#   -m / --mlockall    Lock memory
#   -S / --smp         One thread per CPU
#   -p N / --priority  RT priority
#   -i N / --interval  Interval in µs
#   -l N / --loops     Number of iterations
#   -h N / --histogram Histogram with N µs buckets
#   -q / --quiet       Only show summary
```

### Interpreting cyclictest results
```
# /dev/cpu_dma_latency set to 0us
T: 0 ( 1234) P:80 I:200 C: 100000 Min:      1 Act:    3 Avg:    2 Max:      12
T: 1 ( 1235) P:80 I:200 C: 100000 Min:      1 Act:    4 Avg:    3 Max:      45
```
- **Min/Avg/Max**: Scheduling latency in µs
- **Well-tuned PREEMPT_RT**: Max < 50 µs
- **Max > 100 µs**: Investigate interference sources

### hwlatdetect — hardware latency
```bash
sudo hwlatdetect --duration=60 --threshold=10
# Detects SMIs (System Management Interrupts) and other hardware latency
# Threshold in µs — report anything above this
```

### Application-level latency tracking
```c
void measure_jitter(void) {
    struct timespec expected, actual;
    clock_gettime(CLOCK_MONOTONIC, &expected);

    while (running) {
        expected.tv_nsec += PERIOD_NS;
        if (expected.tv_nsec >= 1000000000L) {
            expected.tv_nsec -= 1000000000L;
            expected.tv_sec++;
        }

        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &expected, NULL);

        clock_gettime(CLOCK_MONOTONIC, &actual);
        int64_t latency_ns = timespec_to_ns(timespec_sub(actual, expected));

        update_histogram(latency_ns);
        if (latency_ns > THRESHOLD_NS)
            log_overrun(latency_ns);
    }
}
```

## ftrace

Kernel tracing framework — the most powerful RT debugging tool:

### Function tracer
```bash
# Enable tracing:
echo function > /sys/kernel/debug/tracing/current_tracer

# Trace specific functions:
echo 'schedule' > /sys/kernel/debug/tracing/set_ftrace_filter
echo 'try_to_wake_up' >> /sys/kernel/debug/tracing/set_ftrace_filter

# Filter by PID:
echo $PID > /sys/kernel/debug/tracing/set_ftrace_pid

# Read trace:
cat /sys/kernel/debug/tracing/trace

# Disable:
echo nop > /sys/kernel/debug/tracing/current_tracer
```

### Wakeup latency tracer
```bash
# Measures worst-case scheduling latency:
echo wakeup_rt > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on

# Run workload...

cat /sys/kernel/debug/tracing/tracing_max_latency  # µs
cat /sys/kernel/debug/tracing/trace  # detailed trace of worst case
```

### Function graph tracer
```bash
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo 'sched*' > /sys/kernel/debug/tracing/set_ftrace_filter

# Shows call tree with timing:
#  2) + 10.270 us | schedule();
#  2)   1.543 us  | try_to_wake_up();
```

### trace-cmd (user-friendly frontend)
```bash
# Record:
sudo trace-cmd record -e sched -e irq -p function_graph \
    --func-stack -F ./my_rt_app

# Report:
trace-cmd report | less

# Visualize (with KernelShark):
kernelshark trace.dat
```

### Event tracing
```bash
# List available events:
ls /sys/kernel/debug/tracing/events/

# Enable scheduler events:
echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable
echo 1 > /sys/kernel/debug/tracing/events/sched/sched_wakeup/enable

# Enable IRQ events:
echo 1 > /sys/kernel/debug/tracing/events/irq/irq_handler_entry/enable
echo 1 > /sys/kernel/debug/tracing/events/irq/irq_handler_exit/enable

# Timer events:
echo 1 > /sys/kernel/debug/tracing/events/timer/enable
```

## Detecting Priority Inversion

### Symptoms
- RT thread has unexplained high latency
- RT thread blocks for long periods despite no I/O
- Latency correlates with non-RT workload

### Detection approaches

**PI-aware mutex verification**:
```c
// At startup, verify all mutexes use PI:
void check_mutex_protocol(pthread_mutex_t *mutex) {
    pthread_mutexattr_t attr;
    int protocol;
    // Note: can't query attr from initialized mutex directly
    // Instead, audit code to ensure all mutex init uses PRIO_INHERIT
}
```

**Runtime detection with ftrace**:
```bash
# Trace lock contention:
echo 1 > /sys/kernel/debug/tracing/events/lock/enable

# Or use lockdep (kernel debug option):
# CONFIG_PROVE_LOCKING=y (development kernels only — significant overhead)
```

**perf-based detection**:
```bash
# Trace scheduler events for RT threads:
sudo perf sched record -p $PID -- sleep 10
sudo perf sched latency --sort max
```

## Thread Sanitizer (TSAN)

Compile-time instrumentation for detecting data races:

```bash
gcc -fsanitize=thread -g -O1 -o program program.c -lpthread
# TSAN works with -O1 or -O2, but not -O0 (too slow)
```

### TSAN output example
```
WARNING: ThreadSanitizer: data race (pid=12345)
  Write of size 4 at 0x7f... by thread T2:
    #0 worker_func program.c:42
  Previous read of size 4 at 0x7f... by thread T1:
    #0 main_loop program.c:28

  Location is global 'shared_counter' of size 4
```

### Limitations
- ~5-15x slowdown — NOT suitable for RT latency testing
- May miss races that only manifest under specific timing
- Cannot detect priority inversion or scheduling issues
- Use for correctness validation, not performance validation

### TSAN suppression file
```
# tsan.supp — suppress known false positives:
race:third_party_lib_func
deadlock:known_safe_pattern
```
```bash
TSAN_OPTIONS="suppressions=tsan.supp" ./program
```

## Helgrind

Valgrind-based thread error detector:

```bash
valgrind --tool=helgrind ./program
```

### What Helgrind detects
- Data races (accesses not protected by locks)
- Lock ordering violations (potential deadlocks)
- Misuse of pthreads API (destroying locked mutex, double lock, etc.)
- POSIX API errors

### Limitations
- ~30-100x slowdown
- High false positive rate with lock-free code and atomics
- Does not understand `_Atomic` / `stdatomic.h` (reports false races)
- Use for development, never for production profiling

### DRD (alternative)
```bash
valgrind --tool=drd ./program
# Similar to Helgrind but different detection algorithm
# Fewer false positives with some patterns, more with others
```

## Common RT Bugs and Symptoms

### Page fault in RT path
**Symptom**: Occasional latency spike of 10-1000+ µs
**Cause**: Accessing memory not yet faulted in
**Debug**: `perf stat -e page-faults -p $PID`
**Fix**: `mlockall` + pre-fault stack + pre-allocate buffers

### malloc in RT path
**Symptom**: Intermittent latency spikes, sometimes deadlock
**Cause**: `malloc` takes internal locks, may call `mmap`/`brk`
**Debug**: `ltrace -e malloc,free -p $PID`
**Fix**: Pre-allocate all memory; use a lock-free pool allocator

### Non-PI mutex
**Symptom**: RT thread blocked for duration of non-RT time slice (~4 ms CFS)
**Cause**: RT thread waiting on mutex held by CFS thread with no PI
**Debug**: Audit mutex initialization for `PTHREAD_PRIO_INHERIT`
**Fix**: Set `PTHREAD_PRIO_INHERIT` on all shared mutexes

### Unbounded I/O in RT path
**Symptom**: Sporadic multi-millisecond latency
**Cause**: `printf`, `syslog`, `write` to filesystem
**Debug**: `strace -e trace=write -p $PID`
**Fix**: Log to lock-free ring buffer, drain from non-RT thread

### CPU frequency scaling
**Symptom**: Variable execution time for same computation
**Cause**: CPU frequency changes during execution
**Debug**: `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`
**Fix**: Set `performance` governor or `intel_pstate=disable` + fixed frequency

### Timer tick interference
**Symptom**: Periodic latency spike every 1ms or 4ms
**Cause**: Timer tick on RT CPU
**Debug**: Check `nohz_full` configuration
**Fix**: Add RT CPUs to `nohz_full` boot parameter

### Signal handler doing unsafe operations
**Symptom**: Deadlock or corruption, intermittent
**Cause**: Calling non-async-signal-safe functions from signal handler
**Debug**: Review signal handlers for printf, malloc, mutex operations
**Fix**: Use `signalfd` or `sigwaitinfo` pattern instead

## Debugging Deadlocks

### GDB thread inspection
```bash
gdb -p $PID
(gdb) info threads
(gdb) thread apply all bt    # backtrace of all threads
(gdb) thread 3
(gdb) bt full                # full backtrace with locals
```

### /proc-based deadlock detection
```bash
# Check what a thread is blocked on:
cat /proc/$PID/task/$TID/wchan    # kernel wait channel
cat /proc/$PID/task/$TID/status   # includes voluntary/involuntary switches
cat /proc/$PID/task/$TID/stack    # kernel stack (needs CONFIG_STACKTRACE)
```

### Lock ordering analysis
```c
// Instrument lock acquisition order:
#ifdef DEBUG_LOCKS
#define LOCK(m) do { \
    fprintf(stderr, "LOCK %s at %s:%d\n", #m, __FILE__, __LINE__); \
    pthread_mutex_lock(m); \
} while (0)
#else
#define LOCK(m) pthread_mutex_lock(m)
#endif
```

### lockdep (kernel)
```bash
# Kernel config: CONFIG_PROVE_LOCKING=y
# Reports potential deadlocks based on lock ordering violations
# Significant overhead — development/testing only
dmesg | grep -i "possible recursive locking\|possible circular locking"
```

## Production Monitoring

### Application metrics to track
```c
typedef struct {
    _Atomic uint64_t cycle_count;
    _Atomic uint64_t overrun_count;
    _Atomic int64_t  max_latency_ns;
    _Atomic int64_t  min_latency_ns;
    _Atomic int64_t  sum_latency_ns;
} rt_stats_t;

// Update atomically in RT loop (lockfree):
void update_stats(rt_stats_t *stats, int64_t latency_ns) {
    atomic_fetch_add(&stats->cycle_count, 1);
    if (latency_ns > atomic_load(&stats->max_latency_ns))
        atomic_store(&stats->max_latency_ns, latency_ns);
    atomic_fetch_add(&stats->sum_latency_ns, latency_ns);
}

// Read from monitoring thread (non-RT):
void report_stats(rt_stats_t *stats) {
    uint64_t count = atomic_load(&stats->cycle_count);
    int64_t max_ns = atomic_load(&stats->max_latency_ns);
    int64_t avg_ns = atomic_load(&stats->sum_latency_ns) / count;
    printf("cycles=%lu avg=%ldns max=%ldns\n", count, avg_ns, max_ns);
}
```

### PSI monitoring
```bash
# Set up PSI trigger (Linux 4.20+):
# Notify when CPU pressure > 10% for 1 second:
echo "some 100000 1000000" > /proc/pressure/cpu
# Read the fd to get notified via poll/epoll
```

### perf for continuous monitoring
```bash
# Low-overhead scheduler stats:
perf stat -e context-switches,cpu-migrations,page-faults \
    -p $PID --interval 1000

# Record scheduling events for post-analysis:
sudo perf sched record -p $PID -- sleep 60
sudo perf sched latency --sort max
```

## Debugging Checklist

When an RT application has latency issues:

1. **Verify system setup**: PREEMPT_RT, isolcpus, nohz_full, irqaffinity
2. **Run cyclictest**: Establish baseline — is the system capable?
3. **Run hwlatdetect**: Rule out hardware interference (SMIs)
4. **Check CPU frequency**: `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
5. **Check page faults**: `perf stat -e page-faults -p $PID`
6. **Check syscalls**: `strace -c -p $PID` — any unexpected I/O?
7. **Check mutex protocols**: Audit for `PTHREAD_PRIO_INHERIT`
8. **Trace scheduling**: `trace-cmd record -e sched -p $PID`
9. **Review RT thread code**: No malloc, no printf, no unbounded operations
10. **Check for interference**: Other processes on isolated CPUs? IRQs?
