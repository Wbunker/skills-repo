# eBPF Program and Attachment Types

Reference for program types, context arguments, helper functions, kfuncs, and all attachment points.

## Table of Contents
- [Program Types Overview](#program-types-overview)
- [Context Arguments](#context-arguments)
- [Helper Functions and kfuncs](#helper-functions-and-kfuncs)
- [Tracing Programs](#tracing-programs)
- [Networking Programs](#networking-programs)
- [Security Programs](#security-programs)
- [Cgroup Programs](#cgroup-programs)

## Program Types Overview

### Key Program Types
| Program Type | Attachment | Context | Use Case |
|-------------|------------|---------|----------|
| `BPF_PROG_TYPE_KPROBE` | Kernel function entry/return | `struct pt_regs *` | Dynamic tracing |
| `BPF_PROG_TYPE_TRACEPOINT` | Static tracepoints | Tracepoint-specific struct | Stable kernel tracing |
| `BPF_PROG_TYPE_RAW_TRACEPOINT` | Raw tracepoints | `struct bpf_raw_tracepoint_args *` | Lower-overhead tracing |
| `BPF_PROG_TYPE_PERF_EVENT` | Perf events | `struct bpf_perf_event_data *` | Hardware/software events |
| `BPF_PROG_TYPE_TRACING` | fentry/fexit/fmod_ret | Function-specific (BTF) | BPF trampoline tracing |
| `BPF_PROG_TYPE_XDP` | Network interface (ingress) | `struct xdp_md *` | High-speed packet processing |
| `BPF_PROG_TYPE_SCHED_CLS` | TC (traffic control) | `struct __sk_buff *` | Packet filtering/mangling |
| `BPF_PROG_TYPE_SCHED_ACT` | TC action | `struct __sk_buff *` | TC action processing |
| `BPF_PROG_TYPE_SOCKET_FILTER` | Socket | `struct __sk_buff *` | Socket-level filtering |
| `BPF_PROG_TYPE_CGROUP_SKB` | Cgroup socket buffer | `struct __sk_buff *` | Per-cgroup network policy |
| `BPF_PROG_TYPE_CGROUP_SOCK` | Cgroup socket ops | `struct bpf_sock *` | Socket creation/bind control |
| `BPF_PROG_TYPE_SOCK_OPS` | TCP/UDP events | `struct bpf_sock_ops *` | Socket tuning |
| `BPF_PROG_TYPE_SK_SKB` | Sockmap/sockhash | `struct __sk_buff *` | Socket redirection |
| `BPF_PROG_TYPE_LSM` | LSM hooks | Hook-specific (BTF) | Security enforcement |
| `BPF_PROG_TYPE_STRUCT_OPS` | Kernel struct_ops | Implementation-specific | Custom TCP congestion, schedulers |
| `BPF_PROG_TYPE_SYSCALL` | User-initiated | Depends on usage | BPF from user space |

### Querying Available Types
```bash
# List supported program types
sudo bpftool feature probe | grep program_type

# List supported map types
sudo bpftool feature probe | grep map_type

# List supported helpers per program type
sudo bpftool feature probe | grep helper
```

## Context Arguments

### Context by Program Type
```c
// Kprobe — architecture-specific registers
SEC("kprobe/sys_execve")
int probe(struct pt_regs *ctx) {
    // Access function arguments via PT_REGS macros
    const char *filename = (const char *)PT_REGS_PARM1(ctx);
    return 0;
}

// Tracepoint — defined per tracepoint
SEC("tracepoint/syscalls/sys_enter_execve")
int trace(struct trace_event_raw_sys_enter *ctx) {
    // ctx->args[0] = filename, ctx->args[1] = argv, etc.
    return 0;
}

// XDP — packet metadata
SEC("xdp")
int xdp_prog(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    // ctx->ingress_ifindex, ctx->rx_queue_index
    return XDP_PASS;
}

// fentry/fexit — direct function args via BTF
SEC("fentry/tcp_connect")
int BPF_PROG(trace_connect, struct sock *sk) {
    // Direct access to function parameters — no PT_REGS needed
    u16 dport = sk->__sk_common.skc_dport;
    return 0;
}
```

## Helper Functions and kfuncs

### Commonly Used Helpers
| Helper | Purpose |
|--------|---------|
| `bpf_map_lookup_elem` | Read map entry |
| `bpf_map_update_elem` | Write map entry |
| `bpf_map_delete_elem` | Delete map entry |
| `bpf_probe_read_kernel` | Read kernel memory safely |
| `bpf_probe_read_user` | Read user space memory safely |
| `bpf_get_current_pid_tgid` | Get current PID and TGID |
| `bpf_get_current_comm` | Get current process name |
| `bpf_get_current_uid_gid` | Get current UID and GID |
| `bpf_ktime_get_ns` | Monotonic clock (nanoseconds) |
| `bpf_trace_printk` | Debug print to trace pipe |
| `bpf_ringbuf_reserve` | Reserve ring buffer space |
| `bpf_ringbuf_submit` | Submit ring buffer entry |
| `bpf_perf_event_output` | Send event via perf buffer |
| `bpf_get_stackid` | Capture stack trace |
| `bpf_redirect` | Redirect packet to interface |
| `bpf_redirect_map` | Redirect via map (XDP/TC) |
| `bpf_skb_store_bytes` | Modify packet data (TC) |
| `bpf_xdp_adjust_head` | Adjust packet head (XDP) |
| `bpf_tail_call` | Tail call to another program |
| `bpf_get_func_ip` | Get function instruction pointer |
| `bpf_snprintf` | Format string into buffer |
| `bpf_timer_init` | Initialize a BPF timer |

### kfuncs (Kernel Functions)
```c
// kfuncs are a newer alternative to BPF helpers
// - Defined as regular kernel functions
// - Registered for BPF use without modifying UAPI
// - Easier to add new functionality
// - Can be module-specific

// Example kfuncs:
// bpf_task_acquire / bpf_task_release — reference-counted task access
// bpf_cgroup_acquire / bpf_cgroup_release — cgroup access
// bpf_cpumask_create / bpf_cpumask_release — CPU mask operations
```

## Tracing Programs

### kprobes and kretprobes
```c
// Attach to any kernel function (dynamic)
SEC("kprobe/do_sys_openat2")
int trace_open(struct pt_regs *ctx) {
    // Entry: access function arguments
    const char *pathname = (const char *)PT_REGS_PARM2(ctx);
    char buf[256];
    bpf_probe_read_user_str(buf, sizeof(buf), pathname);
    return 0;
}

SEC("kretprobe/do_sys_openat2")
int trace_open_ret(struct pt_regs *ctx) {
    // Return: access return value
    int ret = PT_REGS_RC(ctx);
    return 0;
}
```

### fentry/fexit (BPF Trampoline, Linux 5.5+)
```c
// Direct function argument access via BTF — no PT_REGS
SEC("fentry/do_sys_openat2")
int BPF_PROG(trace_open, int dfd, const char *filename,
             struct open_how *how) {
    // Arguments directly available, type-safe
    bpf_printk("open: %s", filename);
    return 0;
}

SEC("fexit/do_sys_openat2")
int BPF_PROG(trace_open_ret, int dfd, const char *filename,
             struct open_how *how, long ret) {
    // Both arguments AND return value available
    bpf_printk("open(%s) = %ld", filename, ret);
    return 0;
}
```

### fentry vs kprobe
| Feature | kprobe | fentry |
|---------|--------|--------|
| Overhead | Higher (int3 breakpoint) | Lower (direct call via trampoline) |
| Arg access | Via PT_REGS (architecture-specific) | Direct, type-safe via BTF |
| Return value | Separate kretprobe | Same fexit gets args + return |
| Stability | Attach to any symbol | Requires BTF |
| Availability | Linux 4.x+ | Linux 5.5+ |

### Tracepoints
```c
// Static instrumentation points (stable API)
SEC("tracepoint/sched/sched_process_exec")
int trace_exec(struct trace_event_raw_sched_process_exec *ctx) {
    // Fields defined by the tracepoint format
    // cat /sys/kernel/debug/tracing/events/sched/sched_process_exec/format
    return 0;
}

// Raw tracepoints (lower overhead, less stable)
SEC("raw_tracepoint/sched_process_exec")
int raw_trace_exec(struct bpf_raw_tracepoint_args *ctx) {
    struct linux_binprm *bprm = (struct linux_binprm *)ctx->args[0];
    return 0;
}
```

### User Space Probes (uprobes)
```c
// Attach to user space function
SEC("uprobe//usr/lib/libssl.so.3/SSL_write")
int trace_ssl_write(struct pt_regs *ctx) {
    void *buf = (void *)PT_REGS_PARM2(ctx);
    int len = (int)PT_REGS_PARM3(ctx);
    // Can read unencrypted data before SSL processes it
    return 0;
}

// User statically-defined tracing (USDT)
SEC("usdt/libc.so.6:libc:memory_malloc_retry")
int trace_malloc(struct pt_regs *ctx) {
    return 0;
}
```

## Networking Programs

### XDP
```c
SEC("xdp")
int my_xdp(struct xdp_md *ctx) {
    // Return values:
    // XDP_PASS     — continue to kernel network stack
    // XDP_DROP     — drop the packet
    // XDP_TX       — send back out the same interface
    // XDP_REDIRECT — redirect to another interface/CPU
    // XDP_ABORTED  — error, drop with trace point
    return XDP_PASS;
}
```

### TC (Traffic Control)
```c
SEC("tc")
int my_tc(struct __sk_buff *skb) {
    // __sk_buff is a mirror of sk_buff with BPF-accessible fields
    // skb->data, skb->data_end, skb->len, skb->protocol
    // skb->ifindex, skb->mark, skb->priority

    // Return values:
    // TC_ACT_OK        — continue processing
    // TC_ACT_SHOT      — drop the packet
    // TC_ACT_REDIRECT  — redirect
    // TC_ACT_UNSPEC    — use default action

    return TC_ACT_OK;
}
```

### Attaching TC Programs
```bash
# Create a clsact qdisc (required)
tc qdisc add dev eth0 clsact

# Attach to ingress
tc filter add dev eth0 ingress bpf da obj prog.bpf.o sec tc

# Attach to egress
tc filter add dev eth0 egress bpf da obj prog.bpf.o sec tc

# List attached filters
tc filter show dev eth0 ingress
```

## Security Programs

### BPF LSM (Linux Security Modules, Linux 5.7+)
```c
// Attach to LSM hooks for security enforcement
SEC("lsm/bprm_check_security")
int BPF_PROG(check_exec, struct linux_binprm *bprm, int ret) {
    // Return 0 to allow, negative errno to deny
    // 'ret' is the result from prior LSM modules
    if (ret != 0)
        return ret;  // respect prior denials

    // Custom policy logic
    return 0;  // allow
}

SEC("lsm/file_open")
int BPF_PROG(check_open, struct file *file, int ret) {
    if (ret != 0)
        return ret;
    // Check file path, UID, etc.
    return 0;
}
```

### Enabling BPF LSM
```bash
# Must be enabled in kernel config and boot params
# CONFIG_BPF_LSM=y
# Boot with: lsm=...,bpf (add bpf to LSM list)

# Check current LSMs
cat /sys/kernel/security/lsm
# lockdown,capability,landlock,yama,apparmor,bpf
```

## Cgroup Programs

### Cgroup Socket Programs
```c
// Control socket creation per cgroup
SEC("cgroup/sock_create")
int cgroup_sock(struct bpf_sock *sk) {
    // Return 1 to allow, 0 to deny
    if (sk->type == SOCK_RAW)
        return 0;  // deny raw sockets
    return 1;
}

// Control bind per cgroup
SEC("cgroup/bind4")
int cgroup_bind4(struct bpf_sock_addr *ctx) {
    // Can inspect and modify bind address/port
    return 1;  // allow
}

// Network policy per cgroup (ingress/egress)
SEC("cgroup_skb/egress")
int cgroup_egress(struct __sk_buff *skb) {
    // Return 1 to allow, 0 to drop
    return 1;
}
```

### Attaching to Cgroups
```bash
# Attach program to a cgroup
sudo bpftool cgroup attach /sys/fs/cgroup/my_group connect4 \
    pinned /sys/fs/bpf/my_prog

# List cgroup attachments
sudo bpftool cgroup show /sys/fs/cgroup/my_group

# Detach
sudo bpftool cgroup detach /sys/fs/cgroup/my_group connect4 \
    pinned /sys/fs/bpf/my_prog
```

### Multi-Attach and Ordering
- Multiple eBPF programs can attach to the same cgroup hook
- Execution order: parent cgroup programs run before child cgroup programs
- `BPF_F_ALLOW_MULTI` flag enables multiple programs per attach point
- `BPF_F_ALLOW_OVERRIDE` lets child cgroup programs override parent decisions
