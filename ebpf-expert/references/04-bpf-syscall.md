# The bpf() System Call

Reference for the bpf() syscall, loading BTF data, creating maps, loading programs, pinning, BPF links, and ring buffers.

## Table of Contents
- [The bpf() Syscall](#the-bpf-syscall)
- [Loading BTF Data](#loading-btf-data)
- [Creating Maps](#creating-maps)
- [Loading Programs](#loading-programs)
- [Modifying Maps from User Space](#modifying-maps-from-user-space)
- [BPF Program Pinning](#bpf-program-pinning)
- [BPF Links](#bpf-links)

## The bpf() Syscall

### Syscall Signature
```c
#include <linux/bpf.h>

int bpf(int cmd, union bpf_attr *attr, unsigned int size);
// cmd:  operation to perform
// attr: pointer to command-specific parameters
// size: size of the attr union
```

### Key Commands
| Command | Purpose |
|---------|---------|
| `BPF_PROG_LOAD` | Load an eBPF program into the kernel |
| `BPF_MAP_CREATE` | Create a new BPF map |
| `BPF_MAP_LOOKUP_ELEM` | Read a value from a map |
| `BPF_MAP_UPDATE_ELEM` | Write a value to a map |
| `BPF_MAP_DELETE_ELEM` | Delete an entry from a map |
| `BPF_MAP_GET_NEXT_KEY` | Iterate through map keys |
| `BPF_PROG_ATTACH` | Attach a program to a hook |
| `BPF_PROG_DETACH` | Detach a program from a hook |
| `BPF_OBJ_PIN` | Pin an object to BPF filesystem |
| `BPF_OBJ_GET` | Retrieve a pinned object |
| `BPF_BTF_LOAD` | Load BTF type information |
| `BPF_LINK_CREATE` | Create a BPF link (persistent attachment) |

### strace Observation
```bash
# Trace bpf() syscalls made by a loader
sudo strace -e bpf ./loader

# Example output:
# bpf(BPF_BTF_LOAD, ...) = 3
# bpf(BPF_MAP_CREATE, {map_type=BPF_MAP_TYPE_HASH, ...}) = 4
# bpf(BPF_PROG_LOAD, {prog_type=BPF_PROG_TYPE_KPROBE, ...}) = 5
# bpf(BPF_LINK_CREATE, {prog_fd=5, ...}) = 6
```

### Capabilities Required
```bash
# Full root access
sudo ./my_bpf_program

# Or specific capabilities (Linux 5.8+)
# CAP_BPF          — load programs and create maps
# CAP_PERFMON      — attach to perf events, kprobes, tracepoints
# CAP_NET_ADMIN    — network-related BPF (XDP, TC, sockets)
# CAP_SYS_ADMIN    — still needed for some operations

# Grant capabilities to a binary
sudo setcap cap_bpf,cap_perfmon=ep ./my_bpf_program
```

## Loading BTF Data

### What BTF Provides
- Type information for maps (key/value types)
- Type information for program parameters
- Line and function info for debugging
- Enables `bpftool` pretty-printing
- Required for CO-RE relocations

### BTF Loading Sequence
```
1. bpf(BPF_BTF_LOAD, ...) → returns BTF fd
2. BTF fd referenced when creating maps and loading programs
3. Kernel uses BTF for type-aware operations
```

```bash
# Inspect BTF data in an object file
bpftool btf dump file hello.bpf.o

# List loaded BTF objects
sudo bpftool btf list

# Dump kernel's BTF (vmlinux BTF)
sudo bpftool btf dump id 1
```

## Creating Maps

### Map Creation via bpf()
```c
union bpf_attr attr = {
    .map_type    = BPF_MAP_TYPE_HASH,
    .key_size    = sizeof(__u32),
    .value_size  = sizeof(__u64),
    .max_entries = 1024,
    .map_flags   = 0,
    .btf_fd      = btf_fd,           // BTF file descriptor
    .btf_key_type_id   = key_type,   // BTF type for key
    .btf_value_type_id = val_type,   // BTF type for value
};

int map_fd = bpf(BPF_MAP_CREATE, &attr, sizeof(attr));
```

### Map File Descriptors
- `bpf()` returns a file descriptor for each created map
- File descriptors are process-local
- When all fds are closed (and no pins/links), the map is freed
- The loader must keep fds open or pin the maps

### libbpf Map Definitions (Modern Style)
```c
// In the eBPF program (C)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u64);
} my_map SEC(".maps");
```

## Loading Programs

### Program Load Sequence
```
1. bpf(BPF_BTF_LOAD, btf_data)           → btf_fd
2. bpf(BPF_MAP_CREATE, map_attrs)         → map_fd (for each map)
3. Relocate map references in bytecode     (loader patches instructions)
4. bpf(BPF_PROG_LOAD, prog_attrs)         → prog_fd
5. Verifier checks the program
6. JIT compiles if enabled
7. Program is ready to attach
```

### Program Load Attributes
```c
union bpf_attr attr = {
    .prog_type      = BPF_PROG_TYPE_KPROBE,
    .insn_cnt       = insn_count,
    .insns          = ptr_to_instructions,
    .license        = "GPL",            // Required for GPL helpers
    .log_buf        = log_buffer,       // Verifier log output
    .log_size       = LOG_BUF_SIZE,
    .log_level       = 1,               // Verbosity (0-2)
    .expected_attach_type = BPF_TRACE_KPROBE_MULTI,
};
```

### Verifier Log
```bash
# If loading fails, the verifier log explains why
# Common errors:
# - "R1 type=inv expected=ctx"  → wrong context type
# - "invalid access to map value" → unchecked null pointer
# - "back-edge from insn X to Y" → unbounded loop (pre-5.3)
# - "unreachable insn X"         → dead code after unconditional jump
```

## Modifying Maps from User Space

### Reading and Writing Map Entries
```c
// Lookup
union bpf_attr attr = {
    .map_fd = map_fd,
    .key    = ptr_to_key,
    .value  = ptr_to_value,  // output buffer
};
bpf(BPF_MAP_LOOKUP_ELEM, &attr, sizeof(attr));

// Update
union bpf_attr attr = {
    .map_fd = map_fd,
    .key    = ptr_to_key,
    .value  = ptr_to_value,
    .flags  = BPF_ANY,  // BPF_ANY, BPF_NOEXIST, BPF_EXIST
};
bpf(BPF_MAP_UPDATE_ELEM, &attr, sizeof(attr));

// Delete
union bpf_attr attr = {
    .map_fd = map_fd,
    .key    = ptr_to_key,
};
bpf(BPF_MAP_DELETE_ELEM, &attr, sizeof(attr));
```

### Iterating Map Keys
```c
// Get first key (pass NULL as key)
bpf(BPF_MAP_GET_NEXT_KEY, &{.map_fd=fd, .key=NULL, .next_key=&key});

// Iterate through all keys
while (bpf(BPF_MAP_GET_NEXT_KEY, &attr) == 0) {
    // Process key
    prev_key = key;
}
```

### bpftool Map Operations
```bash
# Read all entries
sudo bpftool map dump id 5

# Lookup specific key
sudo bpftool map lookup id 5 key 0x01 0x00 0x00 0x00

# Update entry
sudo bpftool map update id 5 key 0x01 0x00 0x00 0x00 \
    value 0x0a 0x00 0x00 0x00

# Delete entry
sudo bpftool map delete id 5 key 0x01 0x00 0x00 0x00
```

## BPF Program Pinning

### The BPF Filesystem
```bash
# Usually mounted at /sys/fs/bpf
mount -t bpf bpf /sys/fs/bpf

# Check if mounted
mount | grep bpf
```

### Pinning Objects
```c
// Pin a program
union bpf_attr attr = {
    .pathname = "/sys/fs/bpf/my_prog",
    .bpf_fd   = prog_fd,
};
bpf(BPF_OBJ_PIN, &attr, sizeof(attr));

// Retrieve a pinned object
union bpf_attr attr = {
    .pathname = "/sys/fs/bpf/my_prog",
};
int fd = bpf(BPF_OBJ_GET, &attr, sizeof(attr));
```

### Why Pinning Matters
- Without pinning, programs/maps are freed when the loader process exits
- Pinning creates a reference in the BPF filesystem
- Allows other processes to access the same maps/programs
- Enables persistent eBPF programs that survive process restarts
- `rm /sys/fs/bpf/my_prog` removes the pin (may free the object)

## BPF Links

### What BPF Links Provide
- A more robust attachment mechanism (Linux 5.7+)
- Owns the attachment — detaches automatically when the link fd is closed
- Can be pinned to the BPF filesystem for persistence
- Provides consistent lifecycle management

### Link vs Traditional Attachment
```
Traditional:
  prog_fd → attach to hook → manual detach needed
  If loader crashes → program stays attached (orphaned)

BPF Links:
  prog_fd → create link → link_fd
  If loader crashes → link fd closes → auto-detach
  If link is pinned → persists across process restarts
```

### Creating a Link
```c
union bpf_attr attr = {
    .link_create = {
        .prog_fd        = prog_fd,
        .target_fd      = target_fd,  // e.g., cgroup fd
        .attach_type    = BPF_CGROUP_INET_INGRESS,
    },
};
int link_fd = bpf(BPF_LINK_CREATE, &attr, sizeof(attr));

// Pin the link for persistence
bpf(BPF_OBJ_PIN, &{.pathname="/sys/fs/bpf/my_link", .bpf_fd=link_fd});
```

### Link Operations
```bash
# List links
sudo bpftool link list

# Show link details
sudo bpftool link show id 1

# Pin a link
sudo bpftool link pin id 1 /sys/fs/bpf/my_link

# Detach (unpin)
sudo rm /sys/fs/bpf/my_link
```

### Ring Buffer Event Flow
```c
// Kernel side: reserve, write, submit
struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
if (!e) return 0;
e->pid = bpf_get_current_pid_tgid() >> 32;
bpf_ringbuf_submit(e, 0);

// Or discard if conditions aren't met
bpf_ringbuf_discard(e, 0);
```

```c
// User space: poll for events
int ring_buffer_fd = bpf_map__fd(skel->maps.events);
struct ring_buffer *rb = ring_buffer__new(ring_buffer_fd, handle_event, NULL, NULL);
while (!exiting) {
    ring_buffer__poll(rb, 100 /* timeout ms */);
}
ring_buffer__free(rb);
```
