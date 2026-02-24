# eBPF Programming

Reference for programming languages and frameworks: bpftrace, BCC, C/libbpf, Go, Rust, Aya, and testing strategies.

## Table of Contents
- [Language Landscape](#language-landscape)
- [bpftrace](#bpftrace)
- [BCC (Python/Lua/C++)](#bcc-pythonluac)
- [C and libbpf](#c-and-libbpf)
- [Go](#go)
- [Rust](#rust)
- [Testing eBPF Programs](#testing-ebpf-programs)
- [Managing Multiple Programs](#managing-multiple-programs)

## Language Landscape

### Choosing a Framework
| Framework | Language | Best For | Production Ready |
|-----------|----------|----------|-----------------|
| **bpftrace** | Custom DSL | One-liners, ad-hoc tracing | Tracing tools |
| **BCC** | Python + C | Prototyping, scripting | Use libbpf instead |
| **libbpf (C)** | C | Production tools, low-level control | Yes |
| **cilium/ebpf** | Go | Go services, Kubernetes tools | Yes |
| **libbpfgo** | Go | Go wrapper around libbpf | Yes |
| **Aya** | Rust | Rust tools, safety-focused | Yes |
| **libbpf-rs** | Rust | Rust wrapper around libbpf | Yes |

### Decision Guide
```
Ad-hoc investigation / one-liners?
  → bpftrace

Quick prototype / scripting?
  → BCC (Python)

Production tool in C?
  → libbpf + CO-RE + skeleton

Production tool in Go?
  → cilium/ebpf (pure Go) or libbpfgo (cgo)

Production tool in Rust?
  → Aya (pure Rust) or libbpf-rs (FFI)
```

## bpftrace

### What bpftrace Is
- High-level tracing language for eBPF
- Inspired by awk and DTrace
- One-liners and scripts for system analysis
- Compiles to eBPF bytecode under the hood

### One-Liner Examples
```bash
# Trace all syscalls by process
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'

# Trace file opens with filename
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# Count syscalls by type
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[args->id] = count(); }'

# Histogram of read() sizes
bpftrace -e 'tracepoint:syscalls:sys_exit_read /args->ret > 0/ { @bytes = hist(args->ret); }'

# Trace TCP connections
bpftrace -e 'kprobe:tcp_connect { @[comm] = count(); }'

# Profile CPU stack samples at 99 Hz
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'

# Trace block I/O latency
bpftrace -e 'kprobe:blk_account_io_start { @start[arg0] = nsecs; }
             kprobe:blk_account_io_done /@start[arg0]/ {
               @usecs = hist((nsecs - @start[arg0]) / 1000);
               delete(@start[arg0]);
             }'
```

### bpftrace Script
```bpftrace
#!/usr/bin/env bpftrace

// execsnoop.bt — trace process execution
tracepoint:syscalls:sys_enter_execve
{
    printf("%-8d %-6d %-16s ", elapsed / 1e6, pid, comm);
    join(args->argv);
}
```

### bpftrace Built-in Variables
| Variable | Description |
|----------|-------------|
| `pid` | Process ID |
| `tid` | Thread ID |
| `uid` | User ID |
| `comm` | Process name (16 chars) |
| `nsecs` | Nanosecond timestamp |
| `elapsed` | Nanoseconds since bpftrace start |
| `kstack` | Kernel stack trace |
| `ustack` | User-space stack trace |
| `args` | Tracepoint arguments |
| `retval` | Return value (kretprobe) |
| `func` | Current function name |
| `curtask` | Current task_struct pointer |
| `cgroup` | Cgroup ID |

### bpftrace Map Functions
```bpftrace
@scalar = count();        // Increment counter
@scalar = sum(val);       // Sum values
@scalar = min(val);       // Track minimum
@scalar = max(val);       // Track maximum
@scalar = avg(val);       // Average
@scalar = stats(val);     // count, avg, total
@hist = hist(val);        // Power-of-2 histogram
@hist = lhist(val, min, max, step);  // Linear histogram
```

## BCC (Python/Lua/C++)

### BCC Architecture
```
Python/Lua user space  →  C kernel program (string)
        ↓                        ↓
    BCC runtime          LLVM/Clang (at runtime)
        ↓                        ↓
    Manages maps          eBPF bytecode
    Reads events                 ↓
    Pretty prints          Kernel loads + verifies
```

### BCC Example
```python
from bcc import BPF

# C program runs in kernel
prog = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct event {
    u32 pid;
    u32 ppid;
    char comm[TASK_COMM_LEN];
    char filename[256];
};

BPF_RINGBUF_OUTPUT(events, 1 << 16);

TRACEPOINT_PROBE(syscalls, sys_enter_execve) {
    struct event *e = events.ringbuf_reserve(sizeof(struct event));
    if (!e) return 0;

    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    e->pid = bpf_get_current_pid_tgid() >> 32;
    e->ppid = task->real_parent->tgid;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_probe_read_user_str(e->filename, sizeof(e->filename), args->filename);

    events.ringbuf_submit(e, 0);
    return 0;
}
"""

b = BPF(text=prog)

def handle_event(ctx, data, size):
    event = b["events"].event(data)
    print(f"PID={event.pid} PPID={event.ppid} "
          f"COMM={event.comm.decode()} FILE={event.filename.decode()}")

b["events"].open_ring_buffer(handle_event)
while True:
    b.ring_buffer_poll()
```

### Why BCC Is Being Replaced
- Runtime compilation: needs LLVM/Clang + kernel headers on target
- Memory overhead: LLVM consumes 100+ MB RAM
- Startup latency: compilation takes seconds
- No CO-RE: must match exact kernel headers
- libbpf + CO-RE solves all these problems

## C and libbpf

### Project Structure
```
my_tool/
├── Makefile
├── vmlinux.h            # Generated from kernel BTF
├── my_tool.bpf.c        # eBPF kernel program
├── my_tool.c            # User space loader/logic
└── my_tool.h            # Shared types (events, map keys)
```

### Kernel Side (my_tool.bpf.c)
```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "my_tool.h"

// Global config (set from user space before load)
const volatile pid_t target_pid = 0;

// Maps
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

// Program
SEC("fentry/do_sys_openat2")
int BPF_PROG(trace_open, int dfd, struct filename *name,
             struct open_how *how) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (target_pid && pid != target_pid)
        return 0;

    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    e->pid = pid;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    BPF_CORE_READ_STR_INTO(&e->filename, name, name);
    bpf_ringbuf_submit(e, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

### User Space (my_tool.c)
```c
#include <stdio.h>
#include <signal.h>
#include <bpf/libbpf.h>
#include "my_tool.skel.h"
#include "my_tool.h"

static volatile bool exiting = false;

static void sig_handler(int sig) { exiting = true; }

static int handle_event(void *ctx, void *data, size_t data_sz) {
    struct event *e = data;
    printf("PID=%-6d COMM=%-16s FILE=%s\n",
           e->pid, e->comm, e->filename);
    return 0;
}

int main(int argc, char **argv) {
    struct my_tool_bpf *skel;
    struct ring_buffer *rb;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // Open
    skel = my_tool_bpf__open();
    if (!skel) { fprintf(stderr, "Failed to open\n"); return 1; }

    // Set config before load
    skel->rodata->target_pid = 0;  // 0 = all pids

    // Load
    if (my_tool_bpf__load(skel)) {
        fprintf(stderr, "Failed to load\n");
        goto cleanup;
    }

    // Attach
    if (my_tool_bpf__attach(skel)) {
        fprintf(stderr, "Failed to attach\n");
        goto cleanup;
    }

    // Set up ring buffer polling
    rb = ring_buffer__new(bpf_map__fd(skel->maps.events),
                          handle_event, NULL, NULL);

    while (!exiting)
        ring_buffer__poll(rb, 100);

cleanup:
    ring_buffer__free(rb);
    my_tool_bpf__destroy(skel);
    return 0;
}
```

## Go

### cilium/ebpf (Pure Go)
```go
package main

import (
    "log"
    "github.com/cilium/ebpf"
    "github.com/cilium/ebpf/link"
    "github.com/cilium/ebpf/ringbuf"
)

//go:generate go run github.com/cilium/ebpf/cmd/bpf2go -target amd64 counter ./counter.bpf.c

func main() {
    // Load compiled eBPF objects
    objs := counterObjects{}
    if err := loadCounterObjects(&objs, nil); err != nil {
        log.Fatal(err)
    }
    defer objs.Close()

    // Attach to kprobe
    kp, err := link.Kprobe("sys_execve", objs.CountExec, nil)
    if err != nil {
        log.Fatal(err)
    }
    defer kp.Close()

    // Read ring buffer
    rd, err := ringbuf.NewReader(objs.Events)
    if err != nil {
        log.Fatal(err)
    }
    defer rd.Close()

    for {
        record, err := rd.Read()
        if err != nil {
            log.Fatal(err)
        }
        // Parse record.RawSample
        log.Printf("event: %v", record.RawSample)
    }
}
```

### cilium/ebpf Features
- Pure Go (no cgo dependency)
- `bpf2go` generates Go bindings from compiled eBPF objects
- Type-safe map access
- CO-RE support
- Ring buffer and perf buffer readers
- Comprehensive link types (kprobe, tracepoint, XDP, TC, etc.)

### libbpfgo (cgo wrapper)
```go
package main

import (
    "fmt"
    bpf "github.com/aquasecurity/libbpfgo"
)

func main() {
    bpfModule, err := bpf.NewModuleFromFile("my_prog.bpf.o")
    if err != nil { panic(err) }
    defer bpfModule.Close()

    if err := bpfModule.BPFLoadObject(); err != nil {
        panic(err)
    }

    prog, err := bpfModule.GetProgram("trace_exec")
    if err != nil { panic(err) }

    _, err = prog.AttachKprobe("__x64_sys_execve")
    if err != nil { panic(err) }

    // Read events from ring buffer
    eventsChannel := make(chan []byte)
    rb, err := bpfModule.InitRingBuf("events", eventsChannel)
    if err != nil { panic(err) }
    rb.Poll(300)

    for data := range eventsChannel {
        fmt.Printf("Event: %v\n", data)
    }
}
```

## Rust

### Aya (Pure Rust)
```rust
// eBPF kernel program (aya-bpf)
#![no_std]
#![no_main]

use aya_bpf::{
    macros::{kprobe, map},
    maps::RingBuf,
    programs::ProbeContext,
    helpers::bpf_get_current_pid_tgid,
};

#[map]
static EVENTS: RingBuf = RingBuf::with_byte_size(256 * 1024, 0);

#[kprobe]
pub fn trace_exec(ctx: ProbeContext) -> u32 {
    let pid = (bpf_get_current_pid_tgid() >> 32) as u32;

    if let Some(mut buf) = EVENTS.reserve::<Event>(0) {
        unsafe {
            let event = buf.as_mut_ptr();
            (*event).pid = pid;
        }
        buf.submit(0);
    }
    0
}
```

```rust
// User space (aya)
use aya::{Bpf, programs::KProbe, maps::RingBuf};
use std::convert::TryInto;

fn main() -> anyhow::Result<()> {
    let mut bpf = Bpf::load_file("my_prog.bpf.o")?;

    let program: &mut KProbe = bpf.program_mut("trace_exec")
        .unwrap().try_into()?;
    program.load()?;
    program.attach("__x64_sys_execve", 0)?;

    let mut ring_buf = RingBuf::try_from(bpf.map_mut("EVENTS").unwrap())?;

    loop {
        if let Some(item) = ring_buf.next() {
            // Process event
            println!("Event received: {} bytes", item.len());
        }
    }
}
```

### Aya Advantages
- Pure Rust — no C toolchain or libbpf dependency
- Rust type safety for both kernel and user-space code
- `cargo` build system integration
- Cross-compilation support
- No `vmlinux.h` needed (uses `aya-tool` for BTF generation)

### libbpf-rs (Rust FFI to libbpf)
```rust
use libbpf_rs::skel::SkelBuilder;

mod my_prog {
    include!(concat!(env!("OUT_DIR"), "/my_prog.skel.rs"));
}

fn main() -> anyhow::Result<()> {
    let builder = my_prog::MyProgSkelBuilder::default();
    let open = builder.open()?;
    let mut skel = open.load()?;
    skel.attach()?;

    // Use skeleton's typed map/program accessors
    let rb = libbpf_rs::RingBufferBuilder::new()
        .add(skel.maps().events(), |data| {
            println!("event: {:?}", data);
            0
        })?
        .build()?;

    loop { rb.poll(std::time::Duration::from_millis(100))?; }
}
```

## Testing eBPF Programs

### Unit Testing Strategies
```c
// 1. BPF_PROG_TEST_RUN — execute eBPF programs from user space
union bpf_attr attr = {
    .test = {
        .prog_fd   = prog_fd,
        .data_in   = input_packet,
        .data_size_in = sizeof(input_packet),
        .data_out  = output_packet,
        .data_size_out = sizeof(output_packet),
    },
};
bpf(BPF_PROG_TEST_RUN, &attr, sizeof(attr));
// Check attr.test.retval (e.g., XDP_DROP, XDP_PASS)
```

```go
// Using cilium/ebpf in Go tests
func TestXDPDrop(t *testing.T) {
    prog := loadProgram(t, "xdp_drop")

    ret, _, err := prog.Test(makePacket())
    if err != nil { t.Fatal(err) }
    if ret != 1 { // XDP_DROP
        t.Errorf("expected XDP_DROP, got %d", ret)
    }
}
```

### Integration Testing
```bash
# Use network namespaces for isolated testing
ip netns add test_ns
ip link add veth0 type veth peer name veth1
ip link set veth1 netns test_ns

# Load XDP program on veth0
ip link set dev veth0 xdp obj prog.bpf.o sec xdp

# Send test traffic from namespace
ip netns exec test_ns ping -c 1 192.168.1.1

# Verify behavior (check maps, counters, etc.)
sudo bpftool map dump id <map_id>

# Cleanup
ip netns del test_ns
```

### Debugging Techniques
```bash
# 1. bpf_printk (kernel trace pipe)
sudo cat /sys/kernel/debug/tracing/trace_pipe

# 2. bpftool prog tracelog
sudo bpftool prog tracelog

# 3. Dump program with source annotations
sudo bpftool prog dump xlated id 42 linum

# 4. Check verifier log
sudo bpftool prog load prog.bpf.o /sys/fs/bpf/test log_level 2
```

## Managing Multiple Programs

### Tail Calls for Program Chaining
```c
// Dispatch table
struct {
    __uint(type, BPF_MAP_TYPE_PROG_ARRAY);
    __uint(max_entries, 10);
    __type(key, __u32);
    __type(value, __u32);
} progs SEC(".maps");

SEC("xdp")
int dispatcher(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    __u32 idx;
    switch (bpf_ntohs(eth->h_proto)) {
        case ETH_P_IP:   idx = 0; break;
        case ETH_P_IPV6: idx = 1; break;
        case ETH_P_ARP:  idx = 2; break;
        default: return XDP_PASS;
    }

    bpf_tail_call(ctx, &progs, idx);
    return XDP_PASS;  // fallback if tail call fails
}
```

### Multiple Programs in One Object
```c
// Multiple SEC programs in the same .bpf.c file
SEC("fentry/tcp_connect")
int BPF_PROG(trace_connect, struct sock *sk) { /* ... */ return 0; }

SEC("fexit/tcp_connect")
int BPF_PROG(trace_connect_ret, struct sock *sk, int ret) { /* ... */ return 0; }

SEC("tracepoint/syscalls/sys_enter_execve")
int trace_exec(struct trace_event_raw_sys_enter *ctx) { /* ... */ return 0; }

// All compiled into one .bpf.o, loaded together by skeleton
// skel->progs.trace_connect, skel->progs.trace_exec, etc.
```
