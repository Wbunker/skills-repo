# Ch 15 — Changes in Recent Go Versions

## Go 1.18 (February 2022)

- **Generics** — type parameters, constraints, `~` tilde operator
- **Fuzz testing** — `go test -fuzz`, `f.Fuzz()`, corpus management
- **Workspace mode** — `go.work`, `go work init/use/sync`
- `any` as alias for `interface{}`
- `comparable` constraint for `==`/`!=`

## Go 1.19 (August 2022)

- **`GOMEMLIMIT`** — soft memory limit (`debug.SetMemoryLimit`)
- **`go doc` improvements** — links in documentation
- Atomic types: `atomic.Int32`, `atomic.Int64`, `atomic.Uint32`, etc.
- `net/http` — improved HTTP/2 server push handling

```go
import "sync/atomic"

var counter atomic.Int64
counter.Add(1)
counter.Load()
counter.Store(0)
counter.CompareAndSwap(0, 1)
counter.Swap(42)
```

## Go 1.20 (February 2023)

- **Slice-to-array conversion** — `[3]int(s)` (was `*[3]int(s)` in 1.17)
- **`errors.Join`** — combine multiple errors
- **`http.ResponseController`** — fine-grained response control
- `comparable` now includes non-strictly comparable types in some contexts
- `crypto/ecdh` — new package for elliptic curve Diffie-Hellman
- `PGO (Profile-Guided Optimization)** — preliminary support

```go
// errors.Join (1.20)
err := errors.Join(err1, err2, err3)
// errors.Is/As works on joined errors

// Slice to array (1.20 — no pointer needed)
s := []int{1, 2, 3, 4, 5}
arr := [3]int(s)   // [1 2 3]
```

## Go 1.21 (August 2023)

- **`slices` package** — generic slice operations (`Sort`, `Contains`, `Max`, etc.)
- **`maps` package** — generic map operations (`Clone`, `Keys`, `Equal`, etc.)
- **`cmp` package** — `cmp.Compare`, `cmp.Less`, `cmp.Ordered`
- **`log/slog`** — structured logging with JSON/text handlers
- **`min` and `max` builtins** — built-in for Ordered types
- **`clear` builtin** — zero out slice or delete all map keys
- **Go toolchain management** — `toolchain` directive in go.mod
- Panic on nil pointer in `any` conversion

```go
// min/max builtins (1.21)
x := min(a, b)
y := max(a, b, c, d)

// clear builtin (1.21)
clear(mySlice)   // zero all elements (len preserved)
clear(myMap)     // delete all keys

// slog (1.21)
slog.Info("hello", "key", "value")
```

## Go 1.22 (February 2024)

- **Enhanced `net/http` routing** — method+path patterns (`"GET /api/users/{id}"`)
- **`r.PathValue("id")`** — extract path parameters
- **Loop variable capture fix** — each iteration creates new loop variable (no more `i := i` idiom)
- **`math/rand/v2`** — improved random number package
- **`go test -cover` improvements** — coverage of functions not called by tests shown
- **`for range N`** — range over integer

```go
// Range over integer (1.22)
for i := range 5 {
    fmt.Println(i)   // 0, 1, 2, 3, 4
}

// New routing (1.22)
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)

// math/rand/v2 (1.22)
import "math/rand/v2"
n := rand.IntN(100)
f := rand.Float64()
rand.N(100 * time.Millisecond)  // random duration
```

## Go 1.23 (August 2024)

- **Range over functions (iterators)** — `range` over `func(yield func(V) bool) bool`
- **`iter` package** — iterator types and utilities (`iter.Seq`, `iter.Seq2`)
- **`maps.All`, `maps.Keys`, `maps.Values`** — return iterators
- **`slices.All`, `slices.Values`, `slices.Collect`** — iterator support
- **`unique` package** — canonical values (interning)
- **Timer/Ticker changes** — `Reset` now always drains channel
- **`go env -changed`** — show only changed env vars

```go
// Custom iterator (1.23)
func Fibonacci() iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for {
            if !yield(a) { return }
            a, b = b, a+b
        }
    }
}

for n := range Fibonacci() {
    if n > 100 { break }
    fmt.Println(n)
}

// Collect iterator into slice
import "slices"
fibs := slices.Collect(Fibonacci())

// unique package (1.23)
import "unique"
h1 := unique.Make("hello")
h2 := unique.Make("hello")
h1 == h2   // true — same canonical value
```

## Go 1.24 (February 2025)

- **Generic type aliases** — `type MySlice[T any] = []T`
- **`os.Root`** — scoped filesystem access (prevent path traversal)
- **`sync.Map` improvements** — more efficient under contention
- **`crypto/mlkem`** — post-quantum key encapsulation (ML-KEM)
- **`tool` directive in go.mod** — track tool dependencies
- **Weak pointers** — `weak.Pointer[T]` for cache-friendly patterns
- **Finalizers** — `runtime.AddCleanup` (replacement for `SetFinalizer`)

```go
// Generic type alias (1.24)
type Set[T comparable] = map[T]struct{}

// os.Root — safe file access within directory (1.24)
root, err := os.OpenRoot("/safe/dir")
f, err := root.Open("file.txt")  // cannot escape the root

// weak pointer (1.24)
import "weak"
ptr := weak.Make(&myObject)
// ... later
if obj := ptr.Value(); obj != nil {
    // still alive
}

// tool directive in go.mod (1.24)
// go.mod:
// tool golang.org/x/tools/cmd/stringer
// go tool stringer -type=MyType
```

## Profile-Guided Optimization (PGO)

Available since Go 1.20, stable in 1.21+:

```bash
# 1. Build instrumented binary
go build -o myapp .

# 2. Collect profile from production
curl -o default.pgo http://localhost:6060/debug/pprof/profile?seconds=30

# 3. Rebuild with PGO
go build -pgo=default.pgo -o myapp .
# or auto-detect: place default.pgo in package directory
```

PGO typically provides 2-7% speedup by optimizing hot code paths (better inlining decisions, devirtualization).

## Garbage Collector Evolution

| Version | GC Change |
|---------|-----------|
| 1.5 | Concurrent GC — STW < 10ms |
| 1.8 | Hybrid barrier — STW < 1ms |
| 1.14 | Asynchronous preemption |
| 1.17 | Register-based ABI (faster calls) |
| 1.19 | GOMEMLIMIT soft memory cap |
| 1.21 | Improved GC pacing |

See [Appendix: The Go Garbage Collector](#gc-appendix) section in the book for tricolor mark-and-sweep details.

## Deprecations and Removals

| Feature | Status |
|---------|--------|
| `rand.Seed()` | Deprecated 1.20 — global source auto-seeded |
| `io/ioutil` package | Deprecated 1.16 — use `io` and `os` directly |
| `ioutil.ReadFile` | → `os.ReadFile` |
| `ioutil.WriteFile` | → `os.WriteFile` |
| `ioutil.ReadAll` | → `io.ReadAll` |
| `ioutil.TempFile` | → `os.CreateTemp` |
| `ioutil.TempDir` | → `os.MkdirTemp` |
| `ioutil.Discard` | → `io.Discard` |
| `ioutil.NopCloser` | → `io.NopCloser` |
