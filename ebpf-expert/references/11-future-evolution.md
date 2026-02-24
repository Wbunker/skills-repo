# eBPF Future and Evolution

Reference for the eBPF Foundation, eBPF for Windows, Linux kernel evolution, and the platform vision.

## Table of Contents
- [The eBPF Foundation](#the-ebpf-foundation)
- [eBPF for Windows](#ebpf-for-windows)
- [Linux Kernel Evolution](#linux-kernel-evolution)
- [eBPF as a Platform](#ebpf-as-a-platform)

## The eBPF Foundation

### Purpose
- Neutral home for eBPF technology under the Linux Foundation
- Coordinates cross-platform eBPF development
- Promotes eBPF adoption and education
- Manages the eBPF runtime specification

### Founding Members
- Meta (Facebook), Google, Microsoft, Netflix, Isovalent (Cilium)
- Founded in August 2021

### Key Initiatives
- **ebpf.io** — community website and documentation
- **eBPF Summit** — annual conference
- **eBPF runtime specification** — formalize the instruction set and runtime
- **Cross-platform standardization** — enable eBPF beyond Linux

## eBPF for Windows

### Architecture
```
┌─────────────────────────────────┐
│        User Space (Windows)     │
│   ┌─────────┐  ┌────────────┐  │
│   │ Loader  │  │ bpftool    │  │
│   │ (libbpf)│  │ (Windows)  │  │
│   └────┬────┘  └─────┬──────┘  │
│        │              │         │
│ ═══════╪══════════════╪═════════│
│        │              │         │
│   ┌────┴──────────────┴──────┐  │
│   │    eBPF for Windows      │  │
│   │  ┌─────────┐  ┌───────┐ │  │
│   │  │Verifier │  │  JIT  │ │  │
│   │  │(PREVAIL)│  │(uBPF) │ │  │
│   │  └─────────┘  └───────┘ │  │
│   │                          │  │
│   │  Hook points:            │  │
│   │  - XDP (via NIC driver)  │  │
│   │  - Socket bind/connect   │  │
│   │  - Cgroup (containers)   │  │
│   └──────────────────────────┘  │
│         Windows Kernel          │
└─────────────────────────────────┘
```

### Key Differences from Linux
| Aspect | Linux eBPF | Windows eBPF |
|--------|-----------|--------------|
| Verifier | In-kernel | PREVAIL (user space, formal verification) |
| JIT | In-kernel | uBPF (micro BPF, user/kernel space) |
| Hook points | 30+ program types | Subset (XDP, socket, cgroup) |
| Maps | All types | Core types (hash, array, ring buffer) |
| Helpers | 200+ | Subset, growing |
| Maturity | Production (since 2014) | Early/experimental |

### Compatibility Goals
- Same eBPF bytecode runs on both Linux and Windows
- Same libbpf API for loading programs
- Same bpftool commands
- Cross-platform eBPF tooling (Cilium, etc.)
- Leverage existing eBPF ecosystem and knowledge

### Open Source Project
- GitHub: microsoft/ebpf-for-windows
- Built on uBPF (micro BPF runtime) and PREVAIL verifier
- Integrates with Windows Filtering Platform (WFP)
- Supports NIC drivers with XDP-like hooks

## Linux Kernel Evolution

### Recent Additions (by Kernel Version)
| Version | Feature |
|---------|---------|
| 5.2 | CO-RE / BTF-based relocations |
| 5.3 | Bounded loops |
| 5.5 | BPF trampoline (fentry/fexit) |
| 5.6 | BPF LSM, bpf_send_signal |
| 5.7 | BPF links, bpf_task_storage |
| 5.8 | Ring buffer, CAP_BPF |
| 5.9 | Sleepable BPF programs |
| 5.10 | BPF iterator, task-local storage |
| 5.13 | bpf_for_each_map_elem, typed pointers |
| 5.14 | Bloom filter map |
| 5.15 | BPF timers (bpf_timer_init/set_callback/start) |
| 5.17 | bpf_loop helper |
| 5.18 | BPF dynptrs (dynamic pointers) |
| 5.19 | User ring buffer, kfunc stabilization |
| 6.0 | BPF panic, typed pointer improvements |
| 6.1 | BPF memory allocator (bpf_obj_new/drop) |
| 6.2 | BPF exceptions, rbtree, linked list |
| 6.3 | BPF token (delegated operations) |
| 6.4 | Arena maps (shared BPF/user-space memory) |
| 6.6 | BPF cpumask kfuncs |
| 6.12 | Sched_ext (extensible scheduler via BPF) |

### Expanding Capabilities
```
Early eBPF (2014-2016):
  Tracing + simple networking

Mid eBPF (2017-2019):
  + BTF, CO-RE, XDP maturity, BPF trampoline

Modern eBPF (2020-2023):
  + Ring buffers, LSM, timers, iterators, memory allocator
  + Sleepable programs, kfuncs, struct_ops

Future eBPF (2024+):
  + Scheduler extension (sched_ext)
  + Arena maps (shared memory)
  + More kernel subsystem integration
  + Cross-platform (Windows, others)
```

### sched_ext — BPF Schedulers
```c
// Custom CPU scheduler written in eBPF (Linux 6.12+)
// Implements scheduling decisions as BPF struct_ops

SEC("struct_ops/my_enqueue")
void BPF_PROG(my_enqueue, struct task_struct *p, u64 enq_flags) {
    // Custom enqueue logic
    scx_bpf_dispatch(p, SCX_DSQ_GLOBAL, SCX_SLICE_DFL, enq_flags);
}

SEC("struct_ops/my_dispatch")
void BPF_PROG(my_dispatch, s32 cpu, struct task_struct *prev) {
    // Custom dispatch logic
    scx_bpf_consume(SCX_DSQ_GLOBAL);
}

SEC(".struct_ops.link")
struct sched_ext_ops my_ops = {
    .enqueue   = (void *)my_enqueue,
    .dispatch  = (void *)my_dispatch,
    .name      = "my_scheduler",
};
```

## eBPF as a Platform

### The Platform Vision
```
Traditional kernel development:
  Idea → Patch → Review → Merge → Release → Distro adoption
  Timeline: months to years

eBPF platform:
  Idea → Write eBPF program → Load at runtime
  Timeline: hours to days
  No kernel rebuild, no reboot, no risk to system stability
```

### eBPF Ecosystem Stack
```
┌──────────────────────────────────────────┐
│            Applications                   │
│  Cilium, Falco, Tetragon, Pixie, Katran  │
├──────────────────────────────────────────┤
│           Platforms / Runtimes            │
│    Kubernetes, systemd, container runtimes│
├──────────────────────────────────────────┤
│           Libraries / Frameworks          │
│  libbpf, cilium/ebpf, Aya, BCC, bpftrace │
├──────────────────────────────────────────┤
│           eBPF Runtime                    │
│  Verifier, JIT, maps, helpers, kfuncs     │
├──────────────────────────────────────────┤
│           Hook Points                     │
│  kprobes, tracepoints, XDP, TC, LSM,     │
│  cgroups, sched_ext, struct_ops           │
├──────────────────────────────────────────┤
│           OS Kernel                       │
│    Linux, Windows (future: others)        │
└──────────────────────────────────────────┘
```

### Impact Areas
| Area | Examples |
|------|---------|
| **Networking** | Cilium (CNI), Katran (L4 LB), XDP firewalls |
| **Security** | Falco, Tetragon, BPF LSM policies |
| **Observability** | Pixie, Parca (profiling), Hubble |
| **Performance** | Custom schedulers (sched_ext), TCP tuning |
| **Storage** | BPF-based I/O schedulers, file system tracing |
| **Compliance** | Runtime audit, policy enforcement |

### eBPF vs Other Technologies
| Technology | Compared to eBPF |
|-----------|-----------------|
| Kernel modules | eBPF is safe, portable, dynamically loadable |
| SystemTap | eBPF is in-tree, no external dependencies |
| DTrace | eBPF is Linux-native, more program types |
| iptables/nftables | eBPF is programmable, O(1) lookups |
| DPDK | eBPF doesn't require dedicated cores or userspace NIC drivers |
| Service mesh sidecars | eBPF eliminates sidecar overhead |
