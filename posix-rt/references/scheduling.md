# Scheduling

## Table of Contents
- [Scheduling Policies](#scheduling-policies)
- [Setting Thread Scheduling](#setting-thread-scheduling)
- [Setting Process Scheduling](#setting-process-scheduling)
- [CPU Affinity](#cpu-affinity)
- [SCHED_DEADLINE (Linux)](#sched_deadline-linux)
- [Priority Design Guidelines](#priority-design-guidelines)
- [Yielding and Preemption](#yielding-and-preemption)
- [Processor Sets and cgroups](#processor-sets-and-cgroups)

## Scheduling Policies

| Policy | Type | Priority Range | Behavior |
|--------|------|---------------|----------|
| `SCHED_OTHER` (CFS) | Normal | 0 (nice: -20 to 19) | Time-sharing, fair scheduling |
| `SCHED_BATCH` | Normal | 0 | Optimized for batch CPU-bound tasks |
| `SCHED_IDLE` | Normal | 0 | Very low priority, runs only when nothing else needs CPU |
| `SCHED_FIFO` | Real-time | 1–99 | Run until blocked, preempted by higher priority, or yield |
| `SCHED_RR` | Real-time | 1–99 | Like FIFO with time quantum (default ~100ms on Linux) |
| `SCHED_DEADLINE` | Real-time | 0 (uses runtime/deadline/period) | EDF — highest priority, above FIFO/RR |

RT policies (FIFO/RR/DEADLINE) always preempt normal policies. Within RT policies, higher numeric priority wins.

### SCHED_FIFO
- Highest-priority runnable FIFO thread runs until it blocks or yields
- If multiple threads share the same priority, they queue FIFO — no preemption among same-priority threads
- Use for deterministic, latency-critical tasks

### SCHED_RR
- Same as FIFO but with a time slice among equal-priority threads
- When the quantum expires, the thread goes to the back of its priority queue
- Query quantum: `sched_rr_get_interval(pid, &timespec)`
- Use when multiple threads at the same priority need fair sharing

### When to use each
- **Control loop, data acquisition**: `SCHED_FIFO` — maximum determinism
- **Multiple workers at same priority**: `SCHED_RR` — fair sharing
- **Periodic tasks with known budgets**: `SCHED_DEADLINE` — admission-controlled
- **Everything else**: `SCHED_OTHER`

## Setting Thread Scheduling

### At creation time
```c
pthread_attr_t attr;
pthread_attr_init(&attr);

// CRITICAL: must set explicit scheduling, otherwise attrs are inherited:
pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
pthread_attr_setschedpolicy(&attr, SCHED_FIFO);

struct sched_param param = { .sched_priority = 50 };
pthread_attr_setschedparam(&attr, &param);

pthread_create(&tid, &attr, func, arg);
pthread_attr_destroy(&attr);
```

### At runtime
```c
struct sched_param param = { .sched_priority = 50 };
int ret = pthread_setschedparam(tid, SCHED_FIFO, &param);
if (ret != 0) {
    // EPERM if lacking CAP_SYS_NICE
}

// Change only priority (keep policy):
param.sched_priority = 60;
pthread_setschedprio(tid, 60);
```

### Query current scheduling
```c
int policy;
struct sched_param param;
pthread_getschedparam(tid, &policy, &param);

// Valid priority range for a policy:
int min = sched_get_priority_min(SCHED_FIFO);  // typically 1
int max = sched_get_priority_max(SCHED_FIFO);  // typically 99
```

## Setting Process Scheduling

```c
#include <sched.h>

struct sched_param param = { .sched_priority = 50 };
sched_setscheduler(0, SCHED_FIFO, &param);  // 0 = calling process

// For a specific pid:
sched_setscheduler(pid, SCHED_RR, &param);
```

### Privileges
Real-time scheduling requires `CAP_SYS_NICE`:
```bash
# Grant capability to binary:
sudo setcap cap_sys_nice=eip ./my_rt_app

# Or run as root (not recommended for production)

# Or set RLIMIT_RTPRIO in /etc/security/limits.conf:
# @realtime hard rtprio 99
# @realtime hard memlock unlimited
```

### RLIMIT_RTTIME safeguard (Linux)
Prevents a runaway RT thread from locking up the system:
```c
#include <sys/resource.h>
struct rlimit rl = { .rlim_cur = 100000, .rlim_max = 100000 }; // 100ms
setrlimit(RLIMIT_RTTIME, &rl);
// Thread gets SIGXCPU after 100ms of CPU without blocking
```

## CPU Affinity

Pin threads to specific CPUs to reduce cache misses, prevent migration, and isolate RT work:

```c
#include <sched.h>

// Set affinity:
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(2, &cpuset);  // pin to CPU 2
CPU_SET(3, &cpuset);  // also allow CPU 3

// For threads (Linux-specific):
pthread_setaffinity_np(tid, sizeof(cpuset), &cpuset);

// For processes (POSIX-adjacent):
sched_setaffinity(0, sizeof(cpuset), &cpuset);

// Query:
CPU_ISSET(2, &cpuset);  // true if CPU 2 is in the set
```

### CPU set operations
```c
cpu_set_t a, b, result;
CPU_AND(&result, &a, &b);    // intersection
CPU_OR(&result, &a, &b);     // union
CPU_XOR(&result, &a, &b);    // symmetric difference
CPU_EQUAL(&a, &b);            // equality test
CPU_COUNT(&a);                 // number of CPUs in set
```

### Large CPU sets (> 1024 CPUs)
```c
cpu_set_t *set = CPU_ALLOC(4096);
size_t size = CPU_ALLOC_SIZE(4096);
CPU_ZERO_S(size, set);
CPU_SET_S(2048, size, set);
sched_setaffinity(0, size, set);
CPU_FREE(set);
```

### RT affinity pattern
```c
// Isolate CPU 3 for RT (combine with kernel boot params):
cpu_set_t rt_cpus;
CPU_ZERO(&rt_cpus);
CPU_SET(3, &rt_cpus);
pthread_setaffinity_np(rt_thread, sizeof(rt_cpus), &rt_cpus);

// Keep non-RT threads off isolated CPUs:
cpu_set_t normal_cpus;
CPU_ZERO(&normal_cpus);
CPU_SET(0, &normal_cpus);
CPU_SET(1, &normal_cpus);
pthread_setaffinity_np(worker_thread, sizeof(normal_cpus), &normal_cpus);
```

## SCHED_DEADLINE (Linux)

Earliest Deadline First scheduling. Linux 3.14+. Highest-priority policy — preempts even SCHED_FIFO 99.

### Parameters
- **Runtime**: worst-case execution time per period
- **Deadline**: relative deadline within the period
- **Period**: how often the task runs

```c
#include <linux/sched.h>
#include <sys/syscall.h>

struct sched_attr {
    uint32_t size;
    uint32_t sched_policy;
    uint64_t sched_flags;
    int32_t  sched_nice;
    uint32_t sched_priority;
    uint64_t sched_runtime;    // nanoseconds
    uint64_t sched_deadline;   // nanoseconds
    uint64_t sched_period;     // nanoseconds
};

struct sched_attr attr = {
    .size = sizeof(attr),
    .sched_policy = SCHED_DEADLINE,
    .sched_runtime  =  5000000,   //  5 ms
    .sched_deadline = 10000000,   // 10 ms
    .sched_period   = 20000000,   // 20 ms (50 Hz)
};

// No glibc wrapper — use syscall directly:
syscall(SYS_sched_setattr, 0, &attr, 0);
```

### Admission control
The kernel rejects `sched_setattr` if total utilization (sum of runtime/period across all DEADLINE tasks per CPU) would exceed a threshold (default ~95%):
```bash
# Adjust: /proc/sys/kernel/sched_rt_runtime_us (default 950000)
#         /proc/sys/kernel/sched_rt_period_us  (default 1000000)
```

### Constraints
- DEADLINE threads cannot use `fork()`
- Cannot hold RT mutexes across `sched_yield()`
- Each DEADLINE thread is pinned to its affinity mask — can't migrate freely
- Must call `sched_yield()` at the end of each period to signal completion

## Priority Design Guidelines

### Recommended priority assignment
```
Priority 99: System watchdog / safety shutdown
Priority 90: Interrupt handling threads (if managed in userspace)
Priority 80: Hard real-time control loops
Priority 70: Sensor data acquisition
Priority 60: Communication / network RT tasks
Priority 50: Soft real-time processing
Priority 40: Logging, monitoring
Priority 1-30: Available for application
Priority 0: SCHED_OTHER (non-RT)
```

### Rules of thumb
- Leave priority 99 for kernel threads and safety monitors
- Group related threads at the same priority and use `SCHED_RR` if they need fairness
- Keep the number of distinct priority levels small — complexity grows with levels
- Document your priority scheme and enforce it centrally
- Every RT thread should have a bounded execution time — use `RLIMIT_RTTIME`

## Yielding and Preemption

```c
sched_yield();  // give up CPU to another same-priority runnable thread
```

- For `SCHED_FIFO`: moves to back of same-priority queue
- For `SCHED_RR`: same as FIFO yield (resets quantum)
- For `SCHED_OTHER`: implementation-defined (often a no-op on Linux)
- For `SCHED_DEADLINE`: signals "done for this period"

**Avoid `sched_yield` in general RT code** — if you're yielding, your design likely needs restructuring (use condition variables, semaphores, or deadline scheduling instead).

## Processor Sets and cgroups

### cgroups v2 CPU control
```bash
# Create RT cgroup:
mkdir /sys/fs/cgroup/rt-tasks
echo "+cpu" > /sys/fs/cgroup/rt-tasks/cgroup.subtree_control

# Set CPU quota:
echo "5000 10000" > /sys/fs/cgroup/rt-tasks/cpu.max  # 50% of one CPU

# Assign process:
echo $PID > /sys/fs/cgroup/rt-tasks/cgroup.procs
```

### cpuset controller (cgroups v2)
```bash
echo "+cpuset" > /sys/fs/cgroup/cgroup.subtree_control
mkdir /sys/fs/cgroup/rt-partition

echo "2-3" > /sys/fs/cgroup/rt-partition/cpuset.cpus
echo "0" > /sys/fs/cgroup/rt-partition/cpuset.mems
echo $PID > /sys/fs/cgroup/rt-partition/cgroup.procs
```

Combine kernel CPU isolation (`isolcpus`) with cgroups cpuset for maximum determinism.
