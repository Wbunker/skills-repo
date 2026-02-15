# Memory Locking

## Table of Contents
- [Why Lock Memory](#why-lock-memory)
- [mlockall](#mlockall)
- [mlock and mlock2](#mlock-and-mlock2)
- [Pre-Faulting](#pre-faulting)
- [Stack Pre-Allocation](#stack-pre-allocation)
- [Heap Strategy for RT](#heap-strategy-for-rt)
- [Huge Pages](#huge-pages)
- [Resource Limits](#resource-limits)
- [Complete RT Memory Setup](#complete-rt-memory-setup)

## Why Lock Memory

Page faults are the enemy of deterministic latency. A page fault triggers:
1. Kernel trap (~1 µs)
2. Page allocation (~1–10 µs)
3. Possible disk I/O for swap (~1–10 ms)

For RT tasks, even a single page fault during the critical path is unacceptable. Memory locking prevents the kernel from evicting pages to swap.

## mlockall

Lock all current and/or future pages:

```c
#include <sys/mman.h>

// Lock everything — call early in main():
if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
    perror("mlockall");
    // Requires CAP_IPC_LOCK or sufficient RLIMIT_MEMLOCK
}
```

### Flags

| Flag | Effect |
|------|--------|
| `MCL_CURRENT` | Lock all pages currently mapped (code, data, stack, mmap) |
| `MCL_FUTURE` | Lock all pages mapped in the future (malloc, mmap, stack growth) |
| `MCL_ONFAULT` | (Linux 4.4+) With `MCL_FUTURE`, lock pages only when first accessed |

### MCL_CURRENT | MCL_FUTURE
The standard RT pattern. Ensures no page faults ever occur. Downside: immediately faults in ALL mapped pages, which increases startup time and RSS.

### MCL_CURRENT | MCL_FUTURE | MCL_ONFAULT
Compromise: future pages are locked on first access rather than at mapping time. Reduces startup cost but means the first access to each new page still causes a (minor) page fault. Acceptable if you pre-fault during initialization.

### Unlocking
```c
munlockall();  // unlock all pages
```

## mlock and mlock2

Lock specific address ranges:

```c
// Lock a region:
void *buf = malloc(BUFFER_SIZE);
mlock(buf, BUFFER_SIZE);

// Unlock:
munlock(buf, BUFFER_SIZE);

// mlock2 (Linux 4.4+, glibc 2.27+):
mlock2(buf, BUFFER_SIZE, MLOCK_ONFAULT);
// MLOCK_ONFAULT: lock on first access, not immediately
```

### When to use mlock vs mlockall
- **mlockall**: Simplest for dedicated RT applications
- **mlock**: When only specific buffers need determinism, or when memory is constrained
- Use `mlock` for large data buffers allocated after `mlockall` if `MCL_ONFAULT` is used and you want immediate locking

## Pre-Faulting

After `mlockall(MCL_CURRENT | MCL_FUTURE)`, existing pages are faulted in. But newly allocated memory still needs to be touched to fault it in if using `MCL_ONFAULT`, and stack pages need explicit pre-faulting regardless.

### Pre-fault a buffer
```c
void prefault_buffer(void *buf, size_t size) {
    volatile char *p = (volatile char *)buf;
    size_t page_size = sysconf(_SC_PAGESIZE);
    for (size_t i = 0; i < size; i += page_size)
        p[i] = p[i];  // read + write to fault in the page
}
```

### Pre-fault with madvise
```c
// Hint the kernel to pre-fault:
madvise(buf, size, MADV_WILLNEED);
// Note: this is a hint, not a guarantee. mlock is the guarantee.
```

## Stack Pre-Allocation

Thread stacks grow on demand. An RT thread must pre-fault its entire stack:

```c
void prefault_stack(size_t stack_size) {
    volatile char dummy[stack_size];
    memset((void *)dummy, 0, stack_size);
    // Forces all stack pages to be allocated and faulted in
}

void *rt_thread(void *arg) {
    // First thing: pre-fault the stack
    prefault_stack(THREAD_STACK_SIZE - 4096);  // leave room for this frame

    // Now enter the RT loop — no more page faults
    while (running) {
        do_rt_work();
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    return NULL;
}
```

### Set and pre-fault thread stack explicitly
```c
size_t stack_size = 512 * 1024;  // 512 KB

// Allocate stack:
void *stack = mmap(NULL, stack_size, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);
mlock(stack, stack_size);
memset(stack, 0, stack_size);  // pre-fault all pages

pthread_attr_t attr;
pthread_attr_init(&attr);
pthread_attr_setstack(&attr, stack, stack_size);
pthread_create(&tid, &attr, rt_thread, NULL);
```

## Heap Strategy for RT

**Rule**: Never call `malloc`, `free`, `realloc`, `calloc` from an RT thread after initialization.

These functions:
- May take locks internally (glibc malloc uses arenas with mutexes)
- May call `mmap`/`brk` to grow the heap
- May trigger page faults
- Have unbounded worst-case execution time

### Pre-allocation pattern
```c
// During initialization (before RT loop):
typedef struct {
    char *buffers;
    int *free_list;
    int free_count;
    size_t buf_size;
    pthread_mutex_t lock;  // with PRIO_INHERIT for RT
} rt_pool_t;

void pool_init(rt_pool_t *pool, int count, size_t buf_size) {
    pool->buf_size = buf_size;
    pool->buffers = malloc(count * buf_size);
    pool->free_list = malloc(count * sizeof(int));
    pool->free_count = count;
    for (int i = 0; i < count; i++)
        pool->free_list[i] = i;

    // Lock and pre-fault:
    mlock(pool->buffers, count * buf_size);
    memset(pool->buffers, 0, count * buf_size);
}

// RT-safe allocation (bounded time):
void *pool_alloc(rt_pool_t *pool) {
    pthread_mutex_lock(&pool->lock);
    if (pool->free_count == 0) {
        pthread_mutex_unlock(&pool->lock);
        return NULL;
    }
    int idx = pool->free_list[--pool->free_count];
    pthread_mutex_unlock(&pool->lock);
    return pool->buffers + idx * pool->buf_size;
}

void pool_free(rt_pool_t *pool, void *ptr) {
    int idx = ((char *)ptr - pool->buffers) / pool->buf_size;
    pthread_mutex_lock(&pool->lock);
    pool->free_list[pool->free_count++] = idx;
    pthread_mutex_unlock(&pool->lock);
}
```

### tcmalloc / jemalloc consideration
These allocators have per-thread caches that reduce lock contention, but they still call `mmap` and have non-deterministic paths. Not suitable for hard RT critical sections.

## Huge Pages

Reduce TLB misses for large memory regions:

### Transparent Huge Pages (THP)
```c
// Hint to kernel:
madvise(addr, size, MADV_HUGEPAGE);

// Or at mmap time:
void *addr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
```

### Explicit huge pages
```bash
# Reserve huge pages at boot:
# /etc/sysctl.conf:
vm.nr_hugepages = 128    # 128 × 2MB = 256MB

# Or at runtime:
echo 128 > /proc/sys/vm/nr_hugepages
```

```c
// Use with mmap:
void *addr = mmap(NULL, 2 * 1024 * 1024, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);

// Or via hugetlbfs:
int fd = open("/mnt/hugetlbfs/myfile", O_CREAT | O_RDWR, 0660);
void *addr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
```

**For RT**: Huge pages reduce TLB pressure and are pre-allocated (no page faults during use). Good for large buffers in RT applications.

**Caution with THP for RT**: Transparent huge page compaction runs asynchronously and can cause latency spikes. For hard RT, prefer explicit huge pages or disable THP on RT CPUs.

## Resource Limits

```c
#include <sys/resource.h>

// Check current memlock limit:
struct rlimit rl;
getrlimit(RLIMIT_MEMLOCK, &rl);
printf("soft: %lu, hard: %lu\n", rl.rlim_cur, rl.rlim_max);

// Set (requires privilege or user config):
rl.rlim_cur = RLIM_INFINITY;
rl.rlim_max = RLIM_INFINITY;
setrlimit(RLIMIT_MEMLOCK, &rl);
```

### System configuration
```bash
# /etc/security/limits.conf:
@realtime hard memlock unlimited
@realtime hard rtprio 99

# Or per-user:
username hard memlock unlimited
```

### Capabilities
```bash
# Grant memory locking capability:
sudo setcap cap_ipc_lock=eip ./my_rt_app

# Or cap_sys_nice for scheduling + cap_ipc_lock for memory:
sudo setcap cap_sys_nice,cap_ipc_lock=eip ./my_rt_app
```

## Complete RT Memory Setup

```c
#include <sys/mman.h>
#include <sys/resource.h>
#include <string.h>
#include <sched.h>

void rt_memory_init(void) {
    // 1. Set memlock limit:
    struct rlimit rl = { RLIM_INFINITY, RLIM_INFINITY };
    setrlimit(RLIMIT_MEMLOCK, &rl);

    // 2. Lock all current and future memory:
    if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
        perror("mlockall failed — check CAP_IPC_LOCK or RLIMIT_MEMLOCK");
        // Non-fatal: continue but log warning
    }

    // 3. Pre-fault the stack (in main thread):
    {
        volatile char stack[512 * 1024];
        memset((void *)stack, 0, sizeof(stack));
    }

    // 4. Pre-allocate and pre-fault all application buffers:
    // ... app-specific ...

    // 5. Disable core dumps (optional — avoids unexpected I/O):
    struct rlimit core = { 0, 0 };
    setrlimit(RLIMIT_CORE, &core);
}
```

Call `rt_memory_init()` early in `main()`, before creating any RT threads.
