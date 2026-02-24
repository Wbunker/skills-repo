---
name: ebpf-expert
description: >
  eBPF expert. Use when the user asks any eBPF question:
  tracing, networking, security, BPF maps, verifier, CO-RE, libbpf, XDP, or eBPF programming.
---

# eBPF Expert

Load only the reference file relevant to the user's question. If a question spans topics, read both files.

## Topic Routing

### Fundamentals
- **What eBPF is, history, BPF vs eBPF, kernel modules, cloud native** → [references/01-what-is-ebpf.md](references/01-what-is-ebpf.md)
- **Hello world, BCC, BPF maps, hash tables, perf/ring buffers, tail calls** → [references/02-hello-world.md](references/02-hello-world.md)
- **eBPF VM, registers, instructions, bytecode, JIT, object files, bpftool** → [references/03-anatomy-of-ebpf-program.md](references/03-anatomy-of-ebpf-program.md)

### System Internals
- **bpf() syscall, loading programs, creating maps, pinning, BPF links** → [references/04-bpf-syscall.md](references/04-bpf-syscall.md)
- **CO-RE, BTF, libbpf, BPF skeletons, portability, relocations** → [references/05-core-btf-libbpf.md](references/05-core-btf-libbpf.md)
- **Verifier, control flow, helper validation, memory access, loops, completion** → [references/06-verifier.md](references/06-verifier.md)

### Program Types & Attachments
- **Program types, attachment types, kprobes, tracepoints, fentry/fexit, LSM, XDP, TC, cgroups** → [references/07-program-attachment-types.md](references/07-program-attachment-types.md)
- **Networking: XDP, TC, packet parsing, load balancing, Kubernetes networking, iptables replacement** → [references/08-networking.md](references/08-networking.md)
- **Security: seccomp, BPF LSM, Cilium Tetragon, syscall tracking, preventative security** → [references/09-security.md](references/09-security.md)

### Programming & Future
- **Programming languages: bpftrace, BCC, C/libbpf, Go, Rust, Aya, testing** → [references/10-programming.md](references/10-programming.md)
- **eBPF Foundation, eBPF for Windows, Linux evolution, platform vision** → [references/11-future-evolution.md](references/11-future-evolution.md)
