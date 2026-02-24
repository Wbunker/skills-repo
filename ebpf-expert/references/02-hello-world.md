# eBPF's "Hello World"

Reference for BCC basics, BPF maps, perf/ring buffers, tail calls, and first eBPF programs.

## Table of Contents
- [BCC Hello World](#bcc-hello-world)
- [BPF Maps](#bpf-maps)
- [Perf and Ring Buffer Maps](#perf-and-ring-buffer-maps)
- [Function Calls](#function-calls)
- [Tail Calls](#tail-calls)

## BCC Hello World

### BCC (BPF Compiler Collection)
- Python/Lua/C++ framework for writing eBPF programs
- Compiles eBPF C code at runtime using LLVM/Clang
- Provides high-level abstractions for maps, events, attachments
- Good for prototyping; not ideal for production (runtime compilation overhead)

### Minimal Hello World
```python
#!/usr/bin/env python3
from bcc import BPF

# eBPF program in C (runs in kernel)
program = r"""
int hello(void *ctx) {
    bpf_trace_printk("Hello World!");
    return 0;
}
"""

# Load and attach to a syscall
b = BPF(text=program)
b.attach_kprobe(event=b.get_syscall_fnname("execve"), fn_name="hello")

# Read output from trace pipe
b.trace_print()
```

### Running
```bash
# Requires root (or CAP_BPF + CAP_PERFMON)
sudo python3 hello.py

# Output appears in trace pipe:
# <task>-<pid> [<cpu>] ... Hello World!
```

### How It Works
1. BCC compiles the C code to eBPF bytecode using Clang/LLVM
2. The bytecode is loaded into the kernel via `bpf()` syscall
3. The verifier checks it for safety
4. The JIT compiler converts it to native machine code
5. It's attached to the `execve` kprobe
6. Every time any process calls `execve`, the eBPF program runs
7. `bpf_trace_printk` writes to `/sys/kernel/debug/tracing/trace_pipe`

## BPF Maps

Maps are key-value data structures shared between eBPF programs (kernel) and user space.

### Map Types
| Map Type | Description | Use Case |
|----------|-------------|----------|
| `BPF_MAP_TYPE_HASH` | Hash table | General key-value storage |
| `BPF_MAP_TYPE_ARRAY` | Array (integer keys) | Fixed-size indexed data |
| `BPF_MAP_TYPE_PERCPU_HASH` | Per-CPU hash table | High-performance counters |
| `BPF_MAP_TYPE_PERCPU_ARRAY` | Per-CPU array | Per-CPU statistics |
| `BPF_MAP_TYPE_PERF_EVENT_ARRAY` | Perf event buffer | Streaming events to user space |
| `BPF_MAP_TYPE_RINGBUF` | Ring buffer | Efficient event streaming |
| `BPF_MAP_TYPE_LRU_HASH` | LRU eviction hash | Bounded-size caches |
| `BPF_MAP_TYPE_LPM_TRIE` | Longest-prefix match | IP routing lookups |
| `BPF_MAP_TYPE_STACK_TRACE` | Stack traces | Profiling |
| `BPF_MAP_TYPE_PROG_ARRAY` | Program references | Tail calls |

### Hash Table Map Example
```python
from bcc import BPF

program = r"""
BPF_HASH(counter_table);

int hello(void *ctx) {
    u64 uid;
    u64 counter = 0;
    u64 *p;

    uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    p = counter_table.lookup(&uid);
    if (p != 0) {
        counter = *p;
    }
    counter++;
    counter_table.update(&uid, &counter);
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event=b.get_syscall_fnname("execve"), fn_name="hello")

# Read map from user space
while True:
    sleep(2)
    s = ""
    for k, v in b["counter_table"].items():
        s += f"  UID {k.value}: {v.value}"
    print(s)
```

### Map Operations (Kernel Side)
```c
// Lookup
void *value = map.lookup(&key);

// Update (insert or overwrite)
map.update(&key, &value);

// Delete
map.delete(&key);

// Lookup and delete atomically
void *value = map.lookup_and_delete(&key);
```

### Map Operations (User Space via bpf() syscall)
```c
// BPF_MAP_LOOKUP_ELEM  — read a value
// BPF_MAP_UPDATE_ELEM  — write a value
// BPF_MAP_DELETE_ELEM  — delete an entry
// BPF_MAP_GET_NEXT_KEY — iterate through keys
```

## Perf and Ring Buffer Maps

### Perf Buffer
```python
program = r"""
BPF_PERF_OUTPUT(events);

struct data_t {
    u32 pid;
    u64 ts;
    char comm[16];
};

int hello(struct pt_regs *ctx) {
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event=b.get_syscall_fnname("execve"), fn_name="hello")

def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"PID={event.pid} COMM={event.comm.decode()}")

b["events"].open_perf_buffer(print_event)
while True:
    b.perf_buffer_poll()
```

### Ring Buffer (Preferred — Linux 5.8+)
```python
program = r"""
BPF_RINGBUF_OUTPUT(events, 1 << 16);  // 64KB ring buffer

struct data_t {
    u32 pid;
    char comm[16];
};

int hello(void *ctx) {
    struct data_t *data;
    data = events.ringbuf_reserve(sizeof(struct data_t));
    if (!data) return 0;

    data->pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&data->comm, sizeof(data->comm));
    events.ringbuf_submit(data, 0);
    return 0;
}
"""
```

### Perf Buffer vs Ring Buffer
| Feature | Perf Buffer | Ring Buffer |
|---------|------------|-------------|
| Per-CPU buffers | Yes (one per CPU) | No (shared) |
| Memory efficiency | Lower (per-CPU allocation) | Higher (shared buffer) |
| Event ordering | Per-CPU only | Global ordering |
| Availability | Linux 4.x+ | Linux 5.8+ |
| Reservation API | No | Yes (reserve + submit/discard) |

## Function Calls

### BPF-to-BPF Calls
```c
// Helper function (called from main eBPF program)
static __attribute__((noinline)) int helper_func(u64 value) {
    // Process value
    return value * 2;
}

int main_prog(void *ctx) {
    u64 result = helper_func(42);
    return 0;
}
```
- Supported since Linux 4.16
- Stack depth limit: 512 bytes total (including nested calls)
- Max 8 nested calls

## Tail Calls

Tail calls allow one eBPF program to call another, replacing the current execution context.

```c
// Program array map for tail calls
BPF_PROG_ARRAY(prog_array, 10);

int entry_prog(void *ctx) {
    // Tail call to program at index 2
    prog_array.call(ctx, 2);
    // If tail call fails, execution continues here
    bpf_trace_printk("Tail call failed or index not set");
    return 0;
}

int tail_prog(void *ctx) {
    bpf_trace_printk("Running tail program!");
    return 0;
}
```

### Tail Call Properties
- The called program **replaces** the caller (no return)
- Same program type required (both must be kprobes, both XDP, etc.)
- Max 33 tail calls in a chain
- Stack is reset — no data passing via stack (use maps instead)
- If the tail call fails (invalid index, missing program), execution continues in the caller
