# What Is eBPF, and Why Is It Important?

Reference for eBPF history, architecture, kernel relationship, and cloud native context.

## Table of Contents
- [eBPF Origins](#ebpf-origins)
- [From BPF to eBPF](#from-bpf-to-ebpf)
- [The Linux Kernel](#the-linux-kernel)
- [Adding Functionality to the Kernel](#adding-functionality-to-the-kernel)
- [eBPF in Cloud Native Environments](#ebpf-in-cloud-native-environments)

## eBPF Origins

### The Berkeley Packet Filter (BPF)
- Created in 1992 by Steven McCanne and Van Jacobson
- Original purpose: efficient network packet filtering
- Used by `tcpdump` and other packet capture tools
- Ran small programs in a virtual machine inside the kernel
- Filter packets **in kernel space** instead of copying all to user space

### From BPF to eBPF
- **Extended BPF (eBPF)** introduced in Linux 3.18 (2014) by Alexei Starovoitov
- Dramatically expanded beyond packet filtering:
  - More registers (10 general-purpose, up from 2)
  - 64-bit registers (up from 32-bit)
  - Maps for persistent state storage
  - Helper functions for kernel interaction
  - JIT compilation for near-native performance
  - Verifier for safety guarantees

### Evolution Timeline
```
1992  BPF created (packet filtering)
2014  eBPF merged into Linux 3.18
2015  eBPF programs attached to kprobes
2016  XDP (eXpress Data Path) for high-speed networking
2017  BPF Type Format (BTF) introduced
2018  BTF support for maps, libbpf development
2019  BPF trampoline (fentry/fexit), BPF LSM proposals
2020  BPF ring buffer, sleepable BPF programs
2021  BPF timers, Bloom filter maps
2022  BPF kfuncs stabilization, typed pointers
2023+ eBPF Foundation, Windows eBPF, continued evolution
```

### Naming
- "eBPF" is the official name, but commonly just called "BPF"
- The "e" is rarely expanded anymore — eBPF is its own thing
- Not an acronym: it's a technology name like "Linux"

## The Linux Kernel

### Kernel vs User Space
```
┌─────────────────────────────────────┐
│         User Space                   │
│  ┌──────┐  ┌──────┐  ┌──────┐     │
│  │ App  │  │ App  │  │ App  │     │
│  └──┬───┘  └──┬───┘  └──┬───┘     │
│     │         │         │           │
│ ════╪═════════╪═════════╪═══════════│  System Call Interface
│     │         │         │           │
│  ┌──┴─────────┴─────────┴────────┐ │
│  │        Linux Kernel            │ │
│  │  ┌─────────────────────────┐  │ │
│  │  │     eBPF Programs       │  │ │
│  │  │  (sandboxed, verified)  │  │ │
│  │  └─────────────────────────┘  │ │
│  │  Scheduler, FS, Net, Memory   │ │
│  └───────────────────────────────┘ │
│         Hardware                     │
└─────────────────────────────────────┘
```

- The kernel mediates all hardware access
- Applications interact via **system calls** (syscalls)
- Kernel code runs with full privilege (ring 0)
- User space code runs with restricted privilege (ring 3)
- eBPF programs run **inside the kernel** but are **verified for safety**

### Why Kernel Programmability Matters
- Observability: see every syscall, network packet, scheduler event
- Networking: process packets before the full network stack
- Security: enforce policies at the kernel level
- Performance: no context switching to user space

## Adding Functionality to the Kernel

### Traditional Approaches
| Approach | Pros | Cons |
|----------|------|------|
| **Modify kernel source** | Full control | Years to reach distros; risk of bugs |
| **Kernel modules** | Loadable at runtime | No safety guarantees; can crash kernel |
| **User space (via syscalls)** | Safe | Slow (context switches); limited visibility |

### Kernel Modules
```bash
# Traditional kernel module
sudo insmod my_module.ko    # Load
sudo rmmod my_module        # Unload
lsmod                       # List loaded modules
```
- Compile against specific kernel version
- Run with full kernel privileges (can crash the system)
- No safety verification
- Must be recompiled for each kernel version

### Why eBPF Is Different
- **Safe:** Verified before loading — cannot crash the kernel
- **Dynamic:** Load/unload at runtime without reboot
- **Portable:** CO-RE (Compile Once, Run Everywhere) across kernel versions
- **High performance:** JIT-compiled to native machine code
- **Event-driven:** Triggered by specific kernel events
- **No kernel rebuild:** No need to modify or recompile the kernel

## eBPF in Cloud Native Environments

### Why eBPF for Cloud Native
- Containers share the host kernel → one eBPF program observes all containers
- Kubernetes networking can be accelerated with XDP/TC eBPF programs
- Service mesh sidecar overhead eliminated (e.g., Cilium replaces iptables)
- Security policies enforced at kernel level (not bypassable from containers)

### Key eBPF-Based Projects
| Project | Purpose |
|---------|---------|
| **Cilium** | Kubernetes CNI, networking, security, observability |
| **Falco** | Runtime security and threat detection |
| **Tetragon** | Security observability and enforcement |
| **Pixie** | Kubernetes observability (auto-instrumentation) |
| **Katran** | Layer 4 load balancer (Facebook/Meta) |
| **Calico eBPF** | Kubernetes networking data plane |
| **bpftrace** | High-level tracing language |
| **BCC** | eBPF toolkit and library |

### The eBPF Advantage for Operations
```
Without eBPF:
  App → Sidecar Proxy → iptables → Kernel → Network
  (multiple context switches, overhead)

With eBPF:
  App → Kernel (eBPF program) → Network
  (single pass, minimal overhead)
```
