# Anatomy of an eBPF Program

Reference for the eBPF virtual machine, registers, instructions, bytecode, JIT compilation, and bpftool.

## Table of Contents
- [The eBPF Virtual Machine](#the-ebpf-virtual-machine)
- [Compiling eBPF Programs](#compiling-ebpf-programs)
- [Inspecting eBPF Programs](#inspecting-ebpf-programs)
- [Loading and Attaching](#loading-and-attaching)
- [Global Variables](#global-variables)
- [BPF to BPF Calls](#bpf-to-bpf-calls)

## The eBPF Virtual Machine

### eBPF Registers
| Register | Purpose |
|----------|---------|
| `r0` | Return value from helper functions and program exit code |
| `r1` | First argument / pointer to context |
| `r2`–`r5` | Arguments to helper functions |
| `r6`–`r9` | Callee-saved registers (preserved across calls) |
| `r10` | Read-only frame pointer (stack access) |

- 10 general-purpose 64-bit registers
- `r1` holds the **context pointer** when the program starts
- Context type depends on program type (e.g., `struct xdp_md *` for XDP)

### eBPF Instructions
```
Each instruction is 8 bytes (64 bits):
┌──────────┬──────┬──────┬────────┬───────────────┐
│ opcode   │ dst  │ src  │ offset │ immediate     │
│ (8 bits) │(4 b) │(4 b) │(16 b)  │ (32 bits)     │
└──────────┴──────┴──────┴────────┴───────────────┘

Instruction classes:
- ALU (32-bit): add, sub, mul, div, mod, and, or, xor, shift
- ALU64 (64-bit): same operations on 64-bit registers
- Memory: load, store (1/2/4/8 byte)
- Branch: jump if equal, not equal, greater, less, etc.
- Call: helper function calls, BPF-to-BPF calls
```

### JIT Compilation
- The verifier first validates eBPF bytecode
- Then the JIT compiler converts bytecode to native machine instructions
- Available on x86_64, ARM64, s390x, RISC-V, and more
- Near-native performance (no interpretation overhead)

```bash
# Check if JIT is enabled
cat /proc/sys/net/core/bpf_jit_enable
# 0 = disabled, 1 = enabled, 2 = enabled with debug output

# Enable JIT
sudo sysctl net.core.bpf_jit_enable=1
```

## Compiling eBPF Programs

### Using Clang/LLVM
```bash
# Compile C to eBPF object file
clang -target bpf -D __TARGET_ARCH_x86 \
  -I/usr/include/x86_64-linux-gnu \
  -Wall -O2 -g \
  -c hello.bpf.c -o hello.bpf.o

# Flags:
# -target bpf       → generate eBPF bytecode
# -O2               → optimization (required for verifier compatibility)
# -g                → debug info (needed for BTF/CO-RE)
# -D __TARGET_ARCH  → target architecture for CO-RE
```

### Object File Contents
```bash
# Inspect ELF sections
llvm-objdump -h hello.bpf.o
# Sections include:
# .text            → default program section
# xdp              → XDP program section
# kprobe/...       → kprobe program section
# .maps            → map definitions
# .rodata          → read-only data (global constants)
# .bss             → zero-initialized global data
# .BTF             → BPF Type Format data
# .BTF.ext         → BTF extension data (line info, func info)
```

## Inspecting eBPF Programs

### bpftool — The Swiss Army Knife
```bash
# List loaded programs
sudo bpftool prog list
# Output: ID, type, name, tag, loaded_at, map_ids

# Show program details
sudo bpftool prog show id 42

# Dump translated bytecode
sudo bpftool prog dump xlated id 42

# Dump JIT-compiled machine code
sudo bpftool prog dump jited id 42

# List maps
sudo bpftool map list

# Show map contents
sudo bpftool map dump id 5

# Read specific map entry
sudo bpftool map lookup id 5 key 0x01 0x00 0x00 0x00

# Show BTF info
sudo bpftool btf list
sudo bpftool btf dump id 1

# Pretty-print map with BTF
sudo bpftool map dump id 5 --pretty

# Show program in DOT format (for visualization)
sudo bpftool prog dump xlated id 42 visual > prog.dot
dot -Tpng prog.dot -o prog.png
```

### BPF Program Tag
```bash
# Tag is a hash of the program instructions
# Same source → same tag (regardless of when loaded)
# Useful for identifying program versions
sudo bpftool prog show id 42
# ... tag: abc123def456...
```

### Using /sys/kernel/debug/tracing
```bash
# Read trace pipe (output from bpf_trace_printk)
sudo cat /sys/kernel/debug/tracing/trace_pipe

# Check available kprobes
sudo cat /sys/kernel/debug/tracing/available_filter_functions

# Check available tracepoints
sudo cat /sys/kernel/debug/tracing/available_events
```

## Loading and Attaching

### Lifecycle
```
1. Compile:  C source → eBPF bytecode (.o ELF file)
2. Load:     bpf(BPF_PROG_LOAD, ...) → kernel validates and JIT-compiles
3. Attach:   Connect to hook point (kprobe, tracepoint, XDP, etc.)
4. Run:      Triggered by kernel events
5. Detach:   Disconnect from hook point
6. Unload:   Reference count drops to 0 → kernel frees program
```

### Reference Counting
- Programs stay loaded as long as references exist:
  - File descriptors (from the loading process)
  - BPF links (persistent attachments)
  - Pinned paths in BPF filesystem
- When all references are gone, the kernel frees the program

### BPF Filesystem (Pinning)
```bash
# Pin a program so it persists after the loader exits
sudo bpftool prog pin id 42 /sys/fs/bpf/my_prog

# Pin a map
sudo bpftool map pin id 5 /sys/fs/bpf/my_map

# Access pinned objects
sudo bpftool prog show pinned /sys/fs/bpf/my_prog

# Unpin (remove the pin, may free the object)
sudo rm /sys/fs/bpf/my_prog
```

## Global Variables

```c
// Read-only global (stored in .rodata section)
const volatile int target_pid = 0;

// Read-write global (stored in .bss or .data section)
int packet_count = 0;

int my_prog(void *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (target_pid && pid != target_pid)
        return 0;

    __sync_fetch_and_add(&packet_count, 1);
    return 0;
}
```

- User space can set `const volatile` globals before loading
- Read-write globals can be updated at runtime via map operations
- Backed by internal BPF array maps

## BPF to BPF Calls

```c
// Static helper function (inlined or called)
static __noinline int process_event(u32 pid) {
    // Do something with pid
    return pid > 1000 ? 1 : 0;
}

SEC("kprobe/sys_execve")
int my_prog(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (process_event(pid)) {
        bpf_printk("Interesting PID: %d", pid);
    }
    return 0;
}
```

### Constraints
- Maximum stack depth: 512 bytes across all nested calls
- Maximum call depth: 8 levels
- All functions must be in the same eBPF program (ELF object)
- Static functions can be inlined by the compiler (no call overhead)
