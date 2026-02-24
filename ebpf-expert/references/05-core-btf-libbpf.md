# CO-RE, BTF, and Libbpf

Reference for Compile Once – Run Everywhere, BPF Type Format, libbpf, BPF skeletons, and portability across kernel versions.

## Table of Contents
- [The Portability Problem](#the-portability-problem)
- [BPF Type Format (BTF)](#bpf-type-format-btf)
- [Compile Once – Run Everywhere (CO-RE)](#compile-once--run-everywhere-co-re)
- [Libbpf](#libbpf)
- [BPF Skeletons](#bpf-skeletons)
- [CO-RE Relocations](#co-re-relocations)

## The Portability Problem

### BCC's Approach (and Its Limitations)
- BCC compiles eBPF C code **at runtime** using embedded Clang/LLVM
- Requires LLVM and kernel headers installed on every target machine
- Compilation adds startup latency and memory overhead
- Short-lived tools pay compilation cost every invocation
- Kernel headers may not match running kernel exactly

### What CO-RE Solves
```
Without CO-RE:
  Source → Compile on target → Load
  (needs compiler + headers on every machine)

With CO-RE:
  Source → Compile once → Distribute binary → Load with relocations
  (only needs BTF on target kernel)
```

## BPF Type Format (BTF)

### What BTF Contains
- Type information for all kernel data structures
- Struct layouts, field offsets, sizes, and types
- Function prototypes and parameters
- Enum definitions and values

### Kernel BTF (vmlinux BTF)
```bash
# Check if kernel has BTF enabled
ls /sys/kernel/btf/vmlinux

# Dump kernel BTF
sudo bpftool btf dump id 1

# Check kernel config
zcat /proc/config.gz | grep CONFIG_DEBUG_INFO_BTF
# CONFIG_DEBUG_INFO_BTF=y           → kernel BTF
# CONFIG_DEBUG_INFO_BTF_MODULES=y   → module BTF
```

### Generating vmlinux.h
```bash
# Generate a header with ALL kernel types from BTF
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# This single header replaces hundreds of kernel headers
# Contains every struct, enum, typedef, and #define
# Specific to the build machine's kernel, but CO-RE handles differences
```

### Using vmlinux.h
```c
// Instead of:
#include <linux/types.h>
#include <linux/sched.h>
#include <linux/fs.h>
// ... many more

// Use:
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
```

### BTF for Maps
```c
// BTF-enabled map definition
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);        // BTF type for key
    __type(value, struct event); // BTF type for value
} events SEC(".maps");

// Enables bpftool pretty-printing:
// sudo bpftool map dump id 5 --pretty
// [{
//     "key": 42,
//     "value": {
//         "pid": 1234,
//         "comm": "bash"
//     }
// }]
```

## Compile Once – Run Everywhere (CO-RE)

### How CO-RE Works
```
Compile time:
  1. Compiler records field access relocations in .BTF.ext
  2. E.g., "access field 'comm' of struct task_struct at offset X"

Load time:
  1. Loader reads target kernel's BTF
  2. Finds actual offset of 'comm' in target kernel's task_struct
  3. Patches eBPF instructions with correct offsets
  4. Loads patched program into kernel
```

### CO-RE Helper Macros
```c
#include <bpf/bpf_core_read.h>

// BPF_CORE_READ — safe, relocatable field access
u32 pid = BPF_CORE_READ(task, tgid);

// Nested reads (follows pointers)
const char *name = BPF_CORE_READ(task, mm, exe_file, f_path.dentry, d_name.name);

// BPF_CORE_READ_STR_INTO — read string fields
char comm[16];
BPF_CORE_READ_STR_INTO(&comm, task, comm);

// bpf_core_field_exists — check if a field exists in running kernel
if (bpf_core_field_exists(task->jobctl)) {
    // field exists in this kernel version
}

// bpf_core_field_size — get field size
int size = bpf_core_field_size(task->comm);

// bpf_core_type_exists — check if a type exists
if (bpf_core_type_exists(struct bpf_link_info)) {
    // type available
}

// bpf_core_enum_value_exists — check enum value
if (bpf_core_enum_value_exists(enum bpf_func_id, BPF_FUNC_get_func_ip)) {
    // helper available
}
```

### Handling Kernel Differences
```c
// Read a field that was renamed between kernel versions
// In older kernels: task_struct->state
// In newer kernels: task_struct->__state
u64 state;
if (bpf_core_field_exists(task->__state))
    state = BPF_CORE_READ(task, __state);
else
    state = BPF_CORE_READ(task, state);
```

### extern Kernel Configurations
```c
// Read kernel config values at load time
extern int LINUX_KERNEL_VERSION __kconfig;
extern bool CONFIG_BPF_JIT __kconfig;

SEC("kprobe/do_sys_open")
int my_prog(struct pt_regs *ctx) {
    if (LINUX_KERNEL_VERSION >= KERNEL_VERSION(5, 15, 0)) {
        // use newer features
    }
    return 0;
}
```

## Libbpf

### What Libbpf Provides
- C library for loading and managing eBPF programs
- Handles ELF parsing, BTF processing, CO-RE relocations
- Creates maps, loads programs, attaches to hooks
- Manages program lifecycle
- The standard way to write production eBPF tools

### Libbpf Workflow
```c
#include <bpf/libbpf.h>
#include "my_prog.skel.h"  // auto-generated skeleton

int main() {
    struct my_prog_bpf *skel;
    int err;

    // 1. Open: parse ELF, prepare maps and programs
    skel = my_prog_bpf__open();
    if (!skel) { /* error */ }

    // 2. (Optional) Set global variables before loading
    skel->rodata->target_pid = getpid();

    // 3. Load: create maps, load programs, CO-RE relocate
    err = my_prog_bpf__load(skel);
    if (err) { /* error */ }

    // 4. Attach: connect programs to hooks
    err = my_prog_bpf__attach(skel);
    if (err) { /* error */ }

    // 5. Use: read maps, poll ring buffers, etc.
    // ...

    // 6. Cleanup
    my_prog_bpf__destroy(skel);
    return 0;
}
```

### Libbpf Naming Conventions
```
Section names determine program type and attachment:
  SEC("kprobe/sys_execve")           → kprobe
  SEC("tracepoint/syscalls/sys_enter_execve") → tracepoint
  SEC("fentry/tcp_connect")          → fentry (BPF trampoline)
  SEC("xdp")                         → XDP
  SEC("tc")                          → traffic control
  SEC("lsm/bprm_check_security")    → LSM hook
  SEC("cgroup/bind4")                → cgroup socket
  SEC("struct_ops/tcp_congestion")   → struct_ops
```

### Error Handling
```c
// Libbpf provides detailed error messages
libbpf_set_print(my_print_fn);  // custom log callback

// Check verifier log on failure
LIBBPF_OPTS(bpf_object_open_opts, open_opts,
    .kernel_log_buf = log_buf,
    .kernel_log_size = sizeof(log_buf),
    .kernel_log_level = 1,
);
```

## BPF Skeletons

### Generating a Skeleton
```bash
# Compile eBPF program
clang -target bpf -g -O2 -c my_prog.bpf.c -o my_prog.bpf.o

# Generate skeleton header
bpftool gen skeleton my_prog.bpf.o > my_prog.skel.h
```

### What the Skeleton Provides
```c
// Auto-generated struct with:
struct my_prog_bpf {
    struct bpf_object_skeleton *skeleton;
    struct bpf_object *obj;

    struct {                    // Maps
        struct bpf_map *events;
        struct bpf_map *counters;
    } maps;

    struct {                    // Programs
        struct bpf_program *handle_exec;
        struct bpf_program *handle_exit;
    } progs;

    struct {                    // Links (after attach)
        struct bpf_link *handle_exec;
        struct bpf_link *handle_exit;
    } links;

    struct my_prog_bpf__rodata {   // Read-only globals
        int target_pid;
    } *rodata;

    struct my_prog_bpf__bss {      // Read-write globals
        long packet_count;
    } *bss;
};

// Auto-generated lifecycle functions:
struct my_prog_bpf *my_prog_bpf__open(void);
int my_prog_bpf__load(struct my_prog_bpf *skel);
int my_prog_bpf__attach(struct my_prog_bpf *skel);
void my_prog_bpf__destroy(struct my_prog_bpf *skel);
```

### Build System Integration
```makefile
# Typical Makefile pattern
ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')

%.bpf.o: %.bpf.c vmlinux.h
	clang -target bpf -D__TARGET_ARCH_$(ARCH) -g -O2 -c $< -o $@

%.skel.h: %.bpf.o
	bpftool gen skeleton $< > $@

%: %.c %.skel.h
	cc -g -Wall -I. -lbpf -lelf -lz $< -o $@
```

## CO-RE Relocations

### Types of Relocations
| Relocation Type | What It Patches |
|----------------|-----------------|
| Field offset | Struct field byte offset |
| Field existence | Whether a field exists |
| Field size | Size of a field |
| Type existence | Whether a type exists |
| Type size | Size of a type |
| Enum value | Numeric value of an enum variant |
| Enum value existence | Whether an enum value exists |

### How Relocations Work Internally
```
1. Compiler emits CO-RE relocations in .BTF.ext section
2. Each relocation records:
   - Instruction offset to patch
   - Access string (e.g., "0:3:2" = first type, field 3, sub-field 2)
   - Kind (field offset, existence, size, etc.)
3. Loader (libbpf):
   a. Reads target kernel's BTF
   b. Matches source types to target types by name
   c. Resolves actual field offsets/sizes in target
   d. Patches instructions before loading into kernel
```

### Limitations
- Target kernel must have BTF enabled (`CONFIG_DEBUG_INFO_BTF=y`)
- Struct/field **names** must match (renames break CO-RE)
- Available since Linux 5.2 (libbpf) / kernel BTF since ~4.18
- Not all distributions enable BTF by default (improving rapidly)
