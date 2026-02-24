# eBPF for Security

Reference for security observability, seccomp, BPF LSM, Cilium Tetragon, syscall tracking, and preventative security.

## Table of Contents
- [Security Observability](#security-observability)
- [Syscall Tracking](#syscall-tracking)
- [Seccomp and BPF](#seccomp-and-bpf)
- [BPF LSM](#bpf-lsm)
- [Cilium Tetragon](#cilium-tetragon)
- [Preventative Security](#preventative-security)
- [Network Security](#network-security)

## Security Observability

### What eBPF Can Observe
```
File access       — open, read, write, chmod, chown
Process events    — exec, fork, clone, exit
Network activity  — connect, accept, send, recv, DNS queries
Privilege changes — setuid, setgid, capset
Kernel activity   — module loads, BPF program loads
System calls      — every syscall entry and exit
```

### Observability Without Overhead
- No instrumentation code in application
- No sidecar or agent injection into containers
- No log parsing or audit daemon overhead
- One eBPF program observes all processes and containers
- Kernel-level data — cannot be bypassed by user-space evasion

### Container-Aware Tracing
```c
// Get container/cgroup context
SEC("tracepoint/syscalls/sys_enter_execve")
int trace_exec(struct trace_event_raw_sys_enter *ctx) {
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();

    // Get cgroup ID (identifies container)
    u64 cgroup_id = bpf_get_current_cgroup_id();

    // Get namespace info
    u32 pid_ns = BPF_CORE_READ(task, nsproxy, pid_ns_for_children, ns.inum);
    u32 mnt_ns = BPF_CORE_READ(task, nsproxy, mnt_ns, ns.inum);

    // Combined with PID and comm gives full container context
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    return 0;
}
```

## Syscall Tracking

### Tracing Syscall Entry/Exit
```c
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

struct event {
    u32 pid;
    u32 uid;
    u64 cgroup_id;
    char comm[16];
    char filename[256];
};

SEC("tracepoint/syscalls/sys_enter_openat")
int trace_openat(struct trace_event_raw_sys_enter *ctx) {
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    e->pid = bpf_get_current_pid_tgid() >> 32;
    e->uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    e->cgroup_id = bpf_get_current_cgroup_id();
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_probe_read_user_str(e->filename, sizeof(e->filename),
                            (const char *)ctx->args[1]);

    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

### Building a Syscall Audit Trail
```c
// Track sensitive syscalls for security monitoring
// execve       — process execution
// openat       — file access
// connect      — outbound network connections
// accept       — inbound network connections
// ptrace       — process debugging/injection
// mount        — filesystem mounting
// init_module  — kernel module loading
// bpf          — BPF program loading
// setuid/setgid — privilege changes
```

## Seccomp and BPF

### Seccomp-BPF
```c
// Seccomp-BPF is NOT eBPF — it's classic BPF (cBPF)
// Used to filter syscalls per process

// Seccomp modes:
// SECCOMP_MODE_STRICT  — only read, write, exit, sigreturn
// SECCOMP_MODE_FILTER  — custom BPF filter per syscall

// Filter returns:
// SECCOMP_RET_ALLOW    — allow the syscall
// SECCOMP_RET_KILL     — kill the process
// SECCOMP_RET_TRAP     — send SIGSYS signal
// SECCOMP_RET_ERRNO    — return an error (specified errno)
// SECCOMP_RET_LOG      — allow but log
// SECCOMP_RET_TRACE    — notify a ptrace tracer
// SECCOMP_RET_USER_NOTIF — send to user-space notification handler
```

### Seccomp vs eBPF LSM
| Feature | Seccomp-BPF | BPF LSM |
|---------|------------|---------|
| BPF type | Classic BPF (cBPF) | Extended BPF (eBPF) |
| Scope | Syscall filtering only | Any LSM hook (200+) |
| Context | Syscall number + args | Rich kernel objects |
| Maps | No | Yes (hash, array, etc.) |
| Helpers | None | Full eBPF helper set |
| Granularity | Per-process | System-wide or per-cgroup |
| Performance | Very fast | Fast (BPF trampoline) |
| Best for | Container sandboxing | Dynamic security policy |

### Seccomp in Container Runtimes
```json
// Docker/OCI seccomp profile (JSON)
{
    "defaultAction": "SCMP_ACT_ERRNO",
    "syscalls": [
        {
            "names": ["read", "write", "open", "close", "stat", "fstat",
                       "mmap", "mprotect", "munmap", "brk", "ioctl",
                       "exit_group", "execve"],
            "action": "SCMP_ACT_ALLOW"
        }
    ]
}
```

## BPF LSM

### Linux Security Modules Architecture
```
Syscall → LSM hook → SELinux → AppArmor → BPF LSM → allow/deny
                         │          │          │
                    (each LSM can deny independently)
```

### BPF LSM Programs
```c
// Deny execution of a specific binary
SEC("lsm/bprm_check_security")
int BPF_PROG(restrict_exec, struct linux_binprm *bprm, int ret) {
    if (ret != 0) return ret;  // respect prior LSM denials

    const char *filename = BPF_CORE_READ(bprm, filename);
    char buf[256];
    bpf_probe_read_kernel_str(buf, sizeof(buf), filename);

    // Block a specific binary
    if (buf[0] == '/' && buf[1] == 't' && buf[2] == 'm' &&
        buf[3] == 'p' && buf[4] == '/') {
        return -EPERM;  // deny execution from /tmp
    }

    return 0;  // allow
}

// Restrict file access
SEC("lsm/file_open")
int BPF_PROG(restrict_open, struct file *file, int ret) {
    if (ret != 0) return ret;

    // Get file path components
    struct path f_path = BPF_CORE_READ(file, f_path);
    struct dentry *dentry = f_path.dentry;
    char name[64];
    BPF_CORE_READ_STR_INTO(&name, dentry, d_name.name);

    // Check for sensitive files
    // Block access to /etc/shadow from non-root
    u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    if (uid != 0 && /* is shadow file */) {
        return -EACCES;
    }

    return 0;
}
```

### Available LSM Hooks (Selection)
| Hook | When Triggered |
|------|---------------|
| `bprm_check_security` | Before executing a binary |
| `file_open` | Opening a file |
| `file_permission` | Reading/writing a file |
| `file_ioctl` | Ioctl on a file |
| `task_alloc` | Creating a new task |
| `task_fix_setuid` | setuid call |
| `socket_create` | Creating a socket |
| `socket_connect` | Connecting a socket |
| `socket_bind` | Binding a socket |
| `socket_sendmsg` | Sending on a socket |
| `sb_mount` | Mounting a filesystem |
| `bpf` | Loading BPF programs/maps |
| `locked_down` | Kernel lockdown operations |

## Cilium Tetragon

### What Tetragon Provides
- Runtime security observability and enforcement
- Kernel-level process, file, and network monitoring
- TracingPolicy CRD for Kubernetes-native configuration
- Real-time event stream with full context (process tree, container, pod)
- Policy enforcement (kill process, send signal, override return)

### TracingPolicy Example
```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: file-monitoring
spec:
  kprobes:
  - call: "security_file_open"
    syscall: false
    args:
    - index: 0
      type: "file"
    selectors:
    - matchArgs:
      - index: 0
        operator: "Prefix"
        values:
        - "/etc/shadow"
        - "/etc/passwd"
      matchActions:
      - action: GetUrl
        argUrl: 0
```

### Tetragon Event Types
```
process_exec     — new process execution
process_exit     — process termination
process_kprobe   — kernel function call
process_tracepoint — tracepoint hit
process_loader   — shared library loading
```

### Enforcement Actions
```yaml
# Kill the process
matchActions:
- action: Sigkill

# Send a signal
matchActions:
- action: Signal
  argSig: 9

# Override return value (deny syscall)
matchActions:
- action: Override
  argError: -1
```

## Preventative Security

### Detection vs Prevention
```
Detection (observability):
  Event → eBPF program → log/alert → user space → response
  (milliseconds to seconds delay)

Prevention (enforcement):
  Event → eBPF program → block immediately
  (microseconds, synchronous)
```

### Enforcement Points
| Mechanism | Granularity | When |
|-----------|------------|------|
| Seccomp | Per-process syscall filter | Before syscall executes |
| BPF LSM | Per-LSM-hook policy | At security check points |
| XDP | Per-packet network filter | Before network stack |
| TC | Per-packet with sk_buff | After sk_buff allocation |
| Cgroup | Per-cgroup socket/network | Socket/network operations |

### Process Execution Control
```c
// Using BPF LSM to enforce an allow-list
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, char[256]);  // binary path
    __type(value, u8);       // 1 = allowed
} allowed_binaries SEC(".maps");

SEC("lsm/bprm_check_security")
int BPF_PROG(exec_allowlist, struct linux_binprm *bprm, int ret) {
    if (ret != 0) return ret;

    char path[256] = {};
    bpf_probe_read_kernel_str(path, sizeof(path),
                              BPF_CORE_READ(bprm, filename));

    u8 *allowed = bpf_map_lookup_elem(&allowed_binaries, path);
    if (!allowed)
        return -EPERM;  // not in allow list → deny

    return 0;
}
```

## Network Security

### Network-Level Enforcement
```c
// Drop connections to known-bad IPs
struct {
    __uint(type, BPF_MAP_TYPE_LPM_TRIE);
    __uint(max_entries, 10000);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, struct lpm_key);
    __type(value, u8);
} blocked_cidrs SEC(".maps");

struct lpm_key {
    __u32 prefixlen;
    __u32 addr;
};

SEC("xdp")
int block_ips(struct xdp_md *ctx) {
    // Parse to get source IP...
    struct lpm_key key = {
        .prefixlen = 32,
        .addr = ip->saddr,
    };

    if (bpf_map_lookup_elem(&blocked_cidrs, &key))
        return XDP_DROP;

    return XDP_PASS;
}
```

### DNS Monitoring
```c
// Monitor DNS queries for threat detection
SEC("xdp")
int dns_monitor(struct xdp_md *ctx) {
    // Parse Ethernet → IP → UDP → check port 53
    // Extract DNS query name
    // Log or block suspicious domains
    return XDP_PASS;
}
```

### Detecting Container Escapes
```c
// Monitor for common container escape patterns:
// 1. Mounting host filesystem
// 2. Loading kernel modules
// 3. Accessing /proc/sysrq-trigger
// 4. Using nsenter or unshare
// 5. Ptrace from container to host process

SEC("lsm/sb_mount")
int BPF_PROG(detect_mount, const char *dev_name,
             const struct path *path, const char *type,
             unsigned long flags, void *data, int ret) {
    // Check if mount is from within a container namespace
    // Alert if container tries to mount host paths
    return 0;  // log only, or return -EPERM to block
}
```
