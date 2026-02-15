# Shared Memory

## Table of Contents
- [POSIX Shared Memory Objects](#posix-shared-memory-objects)
- [mmap Fundamentals](#mmap-fundamentals)
- [Process-Shared Synchronization](#process-shared-synchronization)
- [Memory-Mapped Files](#memory-mapped-files)
- [Shared Memory Patterns](#shared-memory-patterns)
- [Comparison with SysV Shared Memory](#comparison-with-sysv-shared-memory)

## POSIX Shared Memory Objects

Kernel-persistent named memory regions:

```c
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>

// Create or open:
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0660);
if (fd == -1) perror("shm_open");

// Set size (required after creation):
ftruncate(fd, sizeof(shared_data_t));

// Map into address space:
shared_data_t *data = mmap(NULL, sizeof(shared_data_t),
                           PROT_READ | PROT_WRITE,
                           MAP_SHARED, fd, 0);
close(fd);  // fd can be closed after mmap

// Use the shared memory:
data->field = value;

// Unmap:
munmap(data, sizeof(shared_data_t));

// Remove the shared memory object:
shm_unlink("/myshm");
// Like files: object is removed when last mapping is unmapped after unlink
```

Link with `-lrt` (older systems).

### Naming
- Must start with `/`, no additional `/`
- Appears as files in `/dev/shm/` on Linux
- Persistent until `shm_unlink` or system reboot

### Sizing
- `ftruncate` sets the size. Can be called multiple times to grow.
- Growing a mapped region requires `munmap` + `mmap` with new size (or use `mremap` on Linux)
- Shrinking while mapped is dangerous — accessing unmapped pages causes `SIGBUS`

## mmap Fundamentals

```c
void *mmap(void *addr,     // preferred address (NULL = let kernel choose)
           size_t length,  // mapping size
           int prot,       // PROT_READ | PROT_WRITE | PROT_EXEC | PROT_NONE
           int flags,      // MAP_SHARED | MAP_PRIVATE | MAP_ANONYMOUS | ...
           int fd,         // file descriptor (-1 for anonymous)
           off_t offset);  // offset in file (must be page-aligned)
```

### Key flag combinations

| Flags | Use case |
|-------|----------|
| `MAP_SHARED, fd` | Shared memory-mapped file or shm object |
| `MAP_PRIVATE, fd` | Private copy-on-write of file |
| `MAP_SHARED \| MAP_ANONYMOUS, -1` | Shared anonymous memory (parent/child after fork) |
| `MAP_PRIVATE \| MAP_ANONYMOUS, -1` | Private anonymous memory (like malloc) |

### Important behaviors
- **`MAP_SHARED`**: Writes are visible to other processes mapping the same region. Writes are carried through to the underlying file/object.
- **`MAP_PRIVATE`**: Copy-on-write. Writes create private copies of pages. Changes are NOT visible to other processes.
- **Page alignment**: `offset` must be a multiple of page size. `length` is rounded up to page boundary.

### msync — flush to backing store
```c
msync(data, sizeof(shared_data_t), MS_SYNC);   // synchronous flush
msync(data, sizeof(shared_data_t), MS_ASYNC);  // schedule flush
```

### mremap (Linux) — resize without unmapping
```c
#define _GNU_SOURCE
#include <sys/mman.h>

data = mremap(data, old_size, new_size, MREMAP_MAYMOVE);
// Returns new address (may move). Other processes need to re-mmap.
```

### madvise — advise kernel on usage patterns
```c
madvise(addr, length, MADV_SEQUENTIAL);   // reading sequentially
madvise(addr, length, MADV_RANDOM);       // random access
madvise(addr, length, MADV_WILLNEED);     // pre-fault pages
madvise(addr, length, MADV_DONTNEED);     // release pages (contents lost)
madvise(addr, length, MADV_HUGEPAGE);     // use transparent huge pages
```

## Process-Shared Synchronization

When multiple processes access shared memory, they need synchronization primitives **in** the shared memory:

```c
typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t  cond;
    int             data;
    int             ready;
} shared_state_t;

// Initializer process:
int fd = shm_open("/state", O_CREAT | O_RDWR, 0660);
ftruncate(fd, sizeof(shared_state_t));
shared_state_t *state = mmap(NULL, sizeof(shared_state_t),
    PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
close(fd);

// Initialize mutex as process-shared:
pthread_mutexattr_t mattr;
pthread_mutexattr_init(&mattr);
pthread_mutexattr_setpshared(&mattr, PTHREAD_PROCESS_SHARED);
pthread_mutexattr_setrobust(&mattr, PTHREAD_MUTEX_ROBUST);
pthread_mutex_init(&state->lock, &mattr);
pthread_mutexattr_destroy(&mattr);

// Initialize condvar as process-shared:
pthread_condattr_t cattr;
pthread_condattr_init(&cattr);
pthread_condattr_setpshared(&cattr, PTHREAD_PROCESS_SHARED);
pthread_cond_init(&state->cond, &cattr);
pthread_condattr_destroy(&cattr);
```

**Always use `PTHREAD_MUTEX_ROBUST`** with process-shared mutexes — if a process dies while holding the mutex, other processes get `EOWNERDEAD` instead of deadlocking forever.

## Memory-Mapped Files

Use regular files as shared memory:

```c
int fd = open("/tmp/shared_data.bin", O_CREAT | O_RDWR, 0660);
ftruncate(fd, sizeof(shared_data_t));

shared_data_t *data = mmap(NULL, sizeof(shared_data_t),
    PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
close(fd);

// Changes are written back to the file (eventually, or on msync)
```

### Differences from shm_open
| Feature | shm_open | open (file) |
|---------|----------|-------------|
| Backing | tmpfs (`/dev/shm`) — RAM only | Filesystem — persists on disk |
| Performance | No disk I/O | Disk I/O on msync/eviction |
| Persistence | Until unlink/reboot | Until file is deleted |
| Use case | Fast IPC, temporary shared state | Persistent shared data, memory-mapped databases |

## Shared Memory Patterns

### Lock-free ring buffer (single producer, single consumer)
```c
typedef struct {
    _Atomic uint64_t write_pos;
    _Atomic uint64_t read_pos;
    uint64_t capacity;           // power of 2
    char data[];                 // flexible array member
} spsc_ring_t;

// Producer (one thread/process):
void ring_write(spsc_ring_t *r, const void *item, size_t size) {
    uint64_t wp = atomic_load_explicit(&r->write_pos, memory_order_relaxed);
    uint64_t rp = atomic_load_explicit(&r->read_pos, memory_order_acquire);

    if (wp - rp >= r->capacity)
        return;  // full

    memcpy(r->data + (wp % r->capacity) * size, item, size);
    atomic_store_explicit(&r->write_pos, wp + 1, memory_order_release);
}

// Consumer (one thread/process):
int ring_read(spsc_ring_t *r, void *item, size_t size) {
    uint64_t rp = atomic_load_explicit(&r->read_pos, memory_order_relaxed);
    uint64_t wp = atomic_load_explicit(&r->write_pos, memory_order_acquire);

    if (rp >= wp)
        return 0;  // empty

    memcpy(item, r->data + (rp % r->capacity) * size, size);
    atomic_store_explicit(&r->read_pos, rp + 1, memory_order_release);
    return 1;
}
```

### Shared configuration (read-mostly)
```c
typedef struct {
    pthread_rwlock_t lock;
    int version;
    // ... configuration fields ...
} shared_config_t;

// Writer (rare):
pthread_rwlock_wrlock(&config->lock);
config->param = new_value;
config->version++;
pthread_rwlock_unlock(&config->lock);

// Readers (frequent):
pthread_rwlock_rdlock(&config->lock);
int val = config->param;
pthread_rwlock_unlock(&config->lock);
```

### Double-buffered shared memory
```c
typedef struct {
    _Atomic int active_buffer;   // 0 or 1
    sensor_data_t buffers[2];
} double_buffer_t;

// Writer (updates inactive buffer, then swaps):
void update(double_buffer_t *db, const sensor_data_t *new_data) {
    int inactive = !atomic_load(&db->active_buffer);
    db->buffers[inactive] = *new_data;
    atomic_store(&db->active_buffer, inactive);
}

// Reader (reads active buffer — always consistent):
sensor_data_t read_data(double_buffer_t *db) {
    int active = atomic_load(&db->active_buffer);
    return db->buffers[active];
}
```

## Comparison with SysV Shared Memory

| Feature | POSIX shm | SysV shm |
|---------|-----------|----------|
| API | `shm_open` + `mmap` | `shmget` + `shmat` |
| Naming | String (`/name`) | Numeric key (`ftok`) |
| Resize | `ftruncate` | `shmctl` (limited) |
| Visibility | `/dev/shm/` | `ipcs -m` |
| Remove | `shm_unlink` | `shmctl(IPC_RMID)` |
| POSIX standard | Yes | Historical (SysV) |

**Prefer POSIX shared memory** — cleaner API, filesystem namespace, better integration with `mmap`.
