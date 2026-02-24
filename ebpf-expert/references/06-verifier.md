# The eBPF Verifier

Reference for the eBPF verifier process, log interpretation, control flow, helper validation, memory access checks, and loops.

## Table of Contents
- [Verification Process](#verification-process)
- [The Verifier Log](#the-verifier-log)
- [Control Flow Analysis](#control-flow-analysis)
- [Helper Function Validation](#helper-function-validation)
- [Memory Access Checks](#memory-access-checks)
- [Loops and Bounded Iteration](#loops-and-bounded-iteration)
- [Common Verifier Errors](#common-verifier-errors)

## Verification Process

### What the Verifier Checks
1. **DAG check** — No loops in the control flow graph (pre-5.3) or bounded loops (5.3+)
2. **Simulate execution** — Walk every possible path through the program
3. **Register state tracking** — Track the type and range of every register
4. **Memory safety** — All memory accesses are valid and in-bounds
5. **Helper call validation** — Correct argument types, program has license for GPL helpers
6. **Program terminates** — Maximum 1 million verified instructions (BPF_COMPLEXITY_LIMIT)
7. **Return value** — Program returns a valid value on all paths

### Verification Flow
```
Load program via bpf(BPF_PROG_LOAD, ...)
         │
         ▼
    DAG / CFG Check
    (detect unreachable code, validate jumps)
         │
         ▼
    Simulate All Paths
    (track register states, memory access)
         │
         ▼
    Helper Call Validation
    (check args, license, return types)
         │
         ▼
    Stack Depth Check (≤512 bytes)
         │
         ▼
  ┌──────┴──────┐
  │   ACCEPT    │    → JIT compile → attach
  │   REJECT    │    → return error + verifier log
  └─────────────┘
```

### Complexity Limit
- The verifier explores up to **1 million instructions** (BPF_COMPLEXITY_LIMIT)
- Each instruction on each path counts separately
- If exceeded: `BPF program is too large` or `processed X insns... exceeding limit`
- Mitigations: simplify logic, reduce branches, use BPF-to-BPF calls, use tail calls

## The Verifier Log

### Enabling the Log
```c
// In user space (direct bpf() syscall)
char log_buf[65536];
union bpf_attr attr = {
    .log_buf   = log_buf,
    .log_size  = sizeof(log_buf),
    .log_level = 1,  // 0=off, 1=errors, 2=verbose
};

// In libbpf
LIBBPF_OPTS(bpf_object_open_opts, opts,
    .kernel_log_buf = log_buf,
    .kernel_log_size = sizeof(log_buf),
    .kernel_log_level = 2,  // verbose
);
```

### Reading the Log
```
# Example verifier log output:
func#0 @0
0: (79) r2 = *(u64 *)(r1 +0)     ; R1=ctx(off=0) R2_w=pkt(off=0)
1: (79) r3 = *(u64 *)(r1 +8)     ; R3_w=pkt_end(off=0)
2: (bf) r4 = r2                    ; R4_w=pkt(off=0)
3: (07) r4 += 14                   ; R4_w=pkt(off=14)
4: (2d) if r4 > r3 goto pc+10     ; R3=pkt_end R4=pkt(off=14)
                                    ; TRUE → R4>R3 (past end, bail)
                                    ; FALSE → R4<=R3 (14 bytes safe)
5: (71) r5 = *(u8 *)(r2 +12)      ; safe: within bounds

# Register type notation:
# ctx        — context pointer
# pkt        — packet data pointer
# pkt_end    — packet end pointer
# map_value  — pointer into a BPF map value
# fp-8       — stack pointer, offset -8
# inv        — invalid / uninitialized
# scalar     — known scalar value (with range)
```

## Control Flow Analysis

### Path Exploration
- The verifier explores **every possible path** through the program
- At each branch, it forks state and explores both sides
- States are merged when paths converge (with the most conservative register types)
- Pruning: if a state at an instruction is a subset of a previously verified state, skip it

### State Pruning
```
Path A reaches instruction 10 with: R1=scalar(0,100) R2=pkt
Path B reaches instruction 10 with: R1=scalar(0,50)  R2=pkt
  → B is a subset of A (more restricted R1), so B is pruned
  → Already verified all R1 in [0,100], so [0,50] is safe too
```

### Unreachable Code
```c
// Verifier rejects unreachable instructions
if (condition)
    return 0;
else
    return 1;
// Code here is unreachable → verifier error
```

## Helper Function Validation

### Argument Type Checking
```c
// Each helper has a defined prototype
// e.g., bpf_map_lookup_elem(map, key) expects:
//   arg1: PTR_TO_MAP (a map pointer)
//   arg2: PTR_TO_MAP_KEY (pointer to stack/data of correct size)

// The verifier checks:
// 1. Argument types match the helper's expected types
// 2. Pointers are valid (not NULL where required)
// 3. Buffer sizes are correct
// 4. The program's license permits GPL-only helpers
```

### License Checking
```c
// GPL license required for many helpers
SEC("license") char _license[] = "GPL";
// or "Dual BSD/GPL", "GPL v2", etc.

// GPL-only helpers include:
// bpf_trace_printk, bpf_probe_read_kernel, bpf_get_stackid,
// bpf_override_return, bpf_probe_read_user, many more

// Non-GPL helpers:
// bpf_map_lookup_elem, bpf_map_update_elem, bpf_ktime_get_ns,
// bpf_get_prandom_u32, bpf_redirect
```

### Helper Return Values
```c
// The verifier tracks return value types
void *val = bpf_map_lookup_elem(&my_map, &key);
// val is PTR_TO_MAP_VALUE_OR_NULL

// Must check for NULL before dereferencing
if (val) {
    // Now val is PTR_TO_MAP_VALUE — safe to read/write
    __u64 count = *(__u64 *)val;
}
// Without the NULL check → verifier rejects
```

## Memory Access Checks

### Stack Access
```c
// Stack is 512 bytes, accessed via frame pointer (r10)
// All stack access must be within bounds and properly aligned
int value;                    // r10 - 4
char buf[64];                 // r10 - 68

// Verifier tracks which stack slots are initialized
// Reading uninitialized stack → rejected
```

### Packet Access (Bounds Checking)
```c
SEC("xdp")
int my_xdp(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;

    // MUST check bounds before accessing
    if ((void *)(eth + 1) > data_end)
        return XDP_DROP;

    // Now safe to access eth->h_proto, etc.
    // Verifier knows: data to data + sizeof(ethhdr) is valid

    return XDP_PASS;
}
```

### Map Value Access
```c
// After bpf_map_lookup_elem, must check NULL
struct my_value *val = bpf_map_lookup_elem(&my_map, &key);
if (!val)
    return 0;

// Access within value bounds is safe
val->counter++;

// Access beyond value size → rejected
// char *p = (char *)val;
// *(p + 1000) = 0;  // REJECTED: out of bounds
```

### Context Access
```c
// Each program type has specific context fields
// XDP: ctx->data, ctx->data_end, ctx->data_meta, ctx->ingress_ifindex
// kprobe: struct pt_regs fields (architecture-specific)
// tracepoint: tracepoint-specific fields

// Accessing fields outside the defined context → rejected
```

## Loops and Bounded Iteration

### Before Linux 5.3 — No Loops
```c
// Pre-5.3: any back-edge (loop) is rejected
// Must unroll manually using #pragma unroll
#pragma unroll
for (int i = 0; i < 10; i++) {
    // Compiler unrolls this into 10 copies
}
```

### Linux 5.3+ — Bounded Loops
```c
// Bounded loops are allowed if the verifier can prove termination
for (int i = 0; i < 100; i++) {
    // Verifier checks:
    // 1. Loop variable has known bounds
    // 2. Loop body doesn't modify bounds in unpredictable ways
    // 3. Total instruction count stays within complexity limit
    if (condition) break;
}
```

### bpf_loop Helper (Linux 5.17+)
```c
// Callback-based loop — always passes verification
static int loop_body(u32 index, void *ctx) {
    // Process iteration
    struct loop_ctx *lctx = ctx;
    // ... do work ...
    return 0;  // 0 = continue, 1 = break
}

SEC("kprobe/sys_execve")
int my_prog(struct pt_regs *ctx) {
    struct loop_ctx lctx = { .data = some_data };
    bpf_loop(1000, loop_body, &lctx, 0);
    return 0;
}
```

### bpf_for_each_map_elem (Linux 5.13+)
```c
// Iterate over all map elements
static int process_elem(struct bpf_map *map, void *key, void *value, void *ctx) {
    // Process each element
    return 0;  // 0 = continue, 1 = stop
}

bpf_for_each_map_elem(&my_map, process_elem, &callback_ctx, 0);
```

## Common Verifier Errors

### Error Reference
| Error Message | Cause | Fix |
|--------------|-------|-----|
| `R1 type=inv expected=ctx` | Wrong context type | Check program/section type |
| `invalid access to map value` | Missing NULL check after `bpf_map_lookup_elem` | Add `if (!val) return 0;` |
| `R0 invalid mem access 'scalar'` | Dereferencing non-pointer | Check helper return types |
| `back-edge from insn X to Y` | Unbounded loop (pre-5.3) | Unroll or use bounded loop |
| `unreachable insn X` | Dead code after unconditional jump/return | Remove dead code |
| `program is too large` | Exceeded BPF_COMPLEXITY_LIMIT | Simplify, use tail calls |
| `invalid indirect read from stack` | Reading uninitialized stack | Initialize variables before use |
| `cannot pass map_type X into func` | Wrong map type for helper | Use correct map type |
| `R1 offset is outside of the packet` | Packet access without bounds check | Add `if (data + X > data_end)` check |
| `helper call is not allowed in probe` | Program type doesn't support this helper | Check helper availability per program type |
| `BPF program is too complex` | Too many branches/paths | Reduce complexity, split with tail calls |

### Debugging Strategies
```bash
# 1. Get verbose verifier log
sudo bpftool prog load my_prog.bpf.o /sys/fs/bpf/test log_level 2

# 2. Use bpf_printk for debugging (remove in production)
bpf_printk("value=%d ptr=%p", val, ptr);

# 3. Compile with debug info for better error messages
clang -target bpf -g -O2 -c prog.bpf.c -o prog.bpf.o

# 4. Check BTF is present
bpftool btf dump file prog.bpf.o | head
```
