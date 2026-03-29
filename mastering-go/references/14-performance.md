# Ch 14 — Efficiency and Performance

## Benchmarking Methodology

```bash
# Run benchmarks
go test -bench=. -benchmem -benchtime=10s ./...

# Compare two versions (benchstat)
go test -bench=. -count=10 -benchmem ./... > old.txt
# ... make change ...
go test -bench=. -count=10 -benchmem ./... > new.txt
go install golang.org/x/perf/cmd/benchstat@latest
benchstat old.txt new.txt
```

### Reading benchmark output
```
BenchmarkFoo-8    5000000    234 ns/op    48 B/op    2 allocs/op
│              │  │         │            │           └─ heap allocs per op
│              │  │         │            └─ bytes allocated per op
│              │  │         └─ nanoseconds per operation
│              │  └─ iterations run
│              └─ GOMAXPROCS
└─ benchmark name
```

## Memory Management

### Escape analysis
```bash
go build -gcflags="-m" ./...        # show escape analysis
go build -gcflags="-m -m" ./...     # verbose escape analysis
```

Variables escape to the heap when:
- Taken address and outlive the function: `return &x`
- Assigned to interface: `var i any = myStruct`
- Sent on channel: `ch <- &x`
- Stored in heap-allocated data structure
- Too large for stack (typically >32KB)

```go
// Stays on stack (no allocation)
func noEscape() int {
    x := 42
    return x
}

// Escapes to heap
func escapes() *int {
    x := 42
    return &x   // x must live beyond function
}
```

### Reducing allocations

```go
// Pre-allocate slices
s := make([]int, 0, expectedSize)

// Pre-allocate maps
m := make(map[string]int, expectedSize)

// Reuse buffers with sync.Pool
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}
buf := bufPool.Get().(*bytes.Buffer)
buf.Reset()
defer bufPool.Put(buf)

// String builder (avoid repeated concatenation)
var sb strings.Builder
sb.Grow(estimatedLength)
for _, s := range parts {
    sb.WriteString(s)
}
result := sb.String()

// Avoid unnecessary interface boxing
// Bad: fmt.Sprintf("%d", n) — boxes n
// Good: strconv.Itoa(n)     — no allocation for simple cases
```

## Go Memory Model

The memory model defines when writes in one goroutine are visible to another.

### Happens-before relationships
- Within a goroutine: program order
- Channel send **happens before** the corresponding receive completes
- Closing a channel **happens before** receive that returns zero value
- `sync.Mutex` Unlock **happens before** next Lock
- `sync.WaitGroup` Done **happens before** Wait returns
- `sync.Once` Do **happens before** any After-Do return

```go
// Safe: channel provides synchronization
var data int
ready := make(chan struct{})
go func() {
    data = 42       // write
    close(ready)    // signal
}()
<-ready             // wait for signal
fmt.Println(data)   // safe to read: 42

// UNSAFE: no synchronization
var data int
go func() { data = 42 }()
fmt.Println(data)   // DATA RACE — undefined behavior
```

## sync/atomic for Lock-Free Programming

```go
import "sync/atomic"

// Atomic counter
type Counter struct {
    n int64
}
func (c *Counter) Inc() { atomic.AddInt64(&c.n, 1) }
func (c *Counter) Get() int64 { return atomic.LoadInt64(&c.n) }

// atomic.Value — store/load arbitrary values safely
var cfg atomic.Value

// Writer goroutine
cfg.Store(newConfig)

// Reader goroutines (no lock needed)
current := cfg.Load().(Config)

// CAS (Compare-And-Swap) for lock-free algorithms
func (c *Counter) CompareAndIncrement(old, new int64) bool {
    return atomic.CompareAndSwapInt64(&c.n, old, new)
}
```

## CPU Profiling — Finding Hotspots

```bash
# Collect CPU profile
go test -cpuprofile=cpu.out -bench=BenchmarkFoo .

# Or from running program (HTTP pprof)
curl -o cpu.out http://localhost:6060/debug/pprof/profile?seconds=30

# Analyze
go tool pprof -http=:8081 cpu.out
```

Key views in pprof UI:
- **Top** — functions with most CPU time (flat vs cumulative)
- **Flame graph** — visual call stack breakdown
- **Source** — annotated source code
- **Graph** — call graph with edge weights

## Memory Profiling — Allocation Hotspots

```bash
go test -memprofile=mem.out -bench=BenchmarkFoo .
go tool pprof -http=:8081 mem.out

# From live server
curl -o heap.out http://localhost:6060/debug/pprof/heap
go tool pprof -http=:8081 heap.out
```

Profile types:
- `inuse_space` — currently allocated bytes (default)
- `alloc_space` — all-time allocated bytes (find allocation hotspots)
- `inuse_objects` — object count in use
- `alloc_objects` — all-time object count

## eBPF with Go

eBPF allows running sandboxed programs in the Linux kernel for tracing and profiling.

### cilium/ebpf
```go
import "github.com/cilium/ebpf"

// Load compiled eBPF program
spec, err := ebpf.LoadCollectionSpec("myprogram.bpf.o")
coll, err := ebpf.NewCollection(spec)
defer coll.Close()

// Attach to kprobe
prog := coll.Programs["kprobe_sys_execve"]
link, err := link.Kprobe("sys_execve", prog, nil)
defer link.Close()

// Read from eBPF map
m := coll.Maps["events"]
var key uint32
var value uint64
m.Lookup(&key, &value)
```

### bpftrace (ad-hoc tracing, not Go-specific)
```bash
# Trace Go function calls
bpftrace -e 'uprobe:/path/to/myapp:main.processRequest { @[comm] = count(); }'

# Latency histogram
bpftrace -e 'uprobe:myapp:main.serve { @start[tid] = nsecs; }
             uretprobe:myapp:main.serve /@start[tid]/ {
               @latency = hist(nsecs - @start[tid]); delete(@start[tid]); }'
```

### go-perf / perf for profiling
```bash
perf record -g -p $(pidof myapp)
perf report --stdio
```

## GC Tuning

```go
import "runtime"
import "runtime/debug"

// GOGC — GC target percentage (default 100 = gc when heap doubles)
// Set via env: GOGC=200 ./myapp
debug.SetGCPercent(200)   // less frequent GC, more memory
debug.SetGCPercent(50)    // more frequent GC, less memory
debug.SetGCPercent(-1)    // disable GC (manual only)

// GOMEMLIMIT — hard memory limit (Go 1.19+)
// GOMEMLIMIT=512MiB ./myapp
debug.SetMemoryLimit(512 * 1024 * 1024)

// Force GC
runtime.GC()

// Disable GC temporarily (e.g., during latency-sensitive section)
debug.SetGCPercent(-1)
criticalWork()
debug.SetGCPercent(100)
runtime.GC()
```

## GODEBUG Performance Flags

```bash
GOGC=off                  # disable GC entirely
GOMEMLIMIT=1GiB           # memory limit
GOMAXPROCS=4              # number of OS threads
GOFLAGS=-trimpath         # reproducible builds
GODEBUG=gctrace=1         # GC trace output
GODEBUG=madvdontneed=0    # memory return to OS behavior
```

## Performance Patterns

### Batch processing
```go
// Process in batches to reduce overhead
const batchSize = 100
for i := 0; i < len(items); i += batchSize {
    end := i + batchSize
    if end > len(items) { end = len(items) }
    processBatch(items[i:end])
}
```

### Avoid interface{} / any boxing in hot paths
```go
// Slow — boxes int on every call
func sum(nums []interface{}) int {
    total := 0
    for _, n := range nums {
        total += n.(int)
    }
    return total
}

// Fast — no boxing
func sumTyped(nums []int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
```

### Inlining
```bash
go build -gcflags="-m" 2>&1 | grep "inlining"
```
Functions ≤80 "nodes" are inlined automatically. To prevent inlining:
```go
//go:noinline
func expensiveDebugFunction() { ... }
```

### Loop optimizations
```go
// Hoist invariant computations out of loop
n := len(s)
for i := 0; i < n; i++ {  // not len(s) each iteration
    process(s[i])
}

// Prefer range for slices (compiler can optimize bounds checks)
for i, v := range s {
    process(v)
}
```
