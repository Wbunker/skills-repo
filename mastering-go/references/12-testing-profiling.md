# Ch 12 — Code Testing and Profiling

## go test Basics

```bash
go test ./...                 # run all tests
go test ./pkg/...             # specific package tree
go test -v ./...              # verbose output
go test -run TestFoo ./...    # filter by test name (regex)
go test -run TestFoo/subtest  # run specific subtest
go test -count=3 ./...        # run each test 3 times
go test -timeout 30s ./...    # set test timeout
go test -short ./...          # skip long tests (check t.Short())
go test -race ./...           # race detector
go test -cover ./...          # coverage summary
go test -coverprofile=c.out ./... && go tool cover -html=c.out
```

## Writing Tests

```go
import "testing"

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2,3) = %d; want %d", got, want)
    }
}

// Table-driven tests (idiomatic Go)
func TestMultiply(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 6},
        {"zero", 0, 5, 0},
        {"negative", -2, 3, -6},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Multiply(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Multiply(%d,%d) = %d; want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}

// Setup / teardown
func TestMain(m *testing.M) {
    setup()
    code := m.Run()
    teardown()
    os.Exit(code)
}

// Skip slow tests
func TestSlowOperation(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping slow test")
    }
    // ... long test
}
```

## Subtests and Parallel Tests

```go
func TestParallel(t *testing.T) {
    tests := []struct{ name, input, want string }{...}
    for _, tt := range tests {
        tt := tt  // capture range var (Go < 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()   // run subtests concurrently
            got := process(tt.input)
            if got != tt.want {
                t.Errorf("got %q; want %q", got, tt.want)
            }
        })
    }
}
```

## Helper Functions

```go
func assertEqual[T comparable](t *testing.T, got, want T) {
    t.Helper()  // marks this as helper — error points to caller
    if got != want {
        t.Errorf("got %v; want %v", got, want)
    }
}
```

## testify Library

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestWithTestify(t *testing.T) {
    result, err := SomeFunc()

    require.NoError(t, err)          // stops test on failure
    assert.Equal(t, 42, result)      // continues on failure
    assert.NotNil(t, result)
    assert.True(t, result > 0)
    assert.Contains(t, "hello world", "world")
    assert.Len(t, slice, 3)
    assert.ElementsMatch(t, []int{1,2,3}, []int{3,1,2})
    assert.ErrorIs(t, err, ErrNotFound)
    assert.ErrorAs(t, err, &myErr)
}

// Mock with testify/mock
type MockDB struct { mock.Mock }
func (m *MockDB) GetUser(id string) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

db := &MockDB{}
db.On("GetUser", "123").Return(&User{Name: "Alice"}, nil)
```

## Example Functions (tested by go test)

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output:
    // 3
}

func ExampleDivide() {
    fmt.Println(Divide(10, 3))
    // Output:
    // 3.3333333333333335 <nil>
}
```

## Benchmarks

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(2, 3)
    }
}

// With setup
func BenchmarkProcess(b *testing.B) {
    data := generateLargeDataset()
    b.ResetTimer()  // exclude setup time
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// Sub-benchmarks
func BenchmarkSort(b *testing.B) {
    sizes := []int{100, 1000, 10000}
    for _, n := range sizes {
        b.Run(fmt.Sprintf("n=%d", n), func(b *testing.B) {
            data := make([]int, n)
            rand.Read((*(*[8]byte)(unsafe.Pointer(&data[0]))[:]))
            b.ResetTimer()
            for i := 0; i < b.N; i++ {
                slices.Sort(slices.Clone(data))
            }
        })
    }
}
```

```bash
go test -bench=. -benchmem ./...       # run all benchmarks
go test -bench=BenchmarkSort -count=5  # run N times for stable results
go test -bench=. -benchtime=10s        # run for 10s total
go test -bench=. -cpuprofile=cpu.out   # profile during bench
```

Benchmark output:
```
BenchmarkAdd-8    1000000000    0.3 ns/op
BenchmarkSort/n=100-8    100000    15234 ns/op    0 B/op    0 allocs/op
```

## pprof Profiling

### CPU profiling
```go
import "runtime/pprof"

f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
// ... run workload
```

### Memory profiling
```go
f, _ := os.Create("mem.prof")
runtime.GC()
pprof.WriteHeapProfile(f)
f.Close()
```

### HTTP pprof endpoint (add to server)
```go
import _ "net/http/pprof"  // registers /debug/pprof/ routes
// or manually:
mux.HandleFunc("/debug/pprof/", pprof.Index)
mux.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
mux.HandleFunc("/debug/pprof/profile", pprof.Profile)
mux.HandleFunc("/debug/pprof/symbol", pprof.Symbol)
mux.HandleFunc("/debug/pprof/trace", pprof.Trace)
```

### Analyzing profiles
```bash
go tool pprof cpu.prof
# Interactive:
(pprof) top10
(pprof) list myFunc
(pprof) web        # open flame graph in browser

# Direct web UI
go tool pprof -http=:8081 cpu.prof

# From live server
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof http://localhost:6060/debug/pprof/heap
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

## Execution Tracer

```go
import "runtime/trace"

f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// ... run workload
```

```bash
go tool trace trace.out   # opens browser UI
```

## Cross-Compilation

```bash
# Environment variables
GOOS    # linux, darwin, windows, freebsd, android, ios
GOARCH  # amd64, arm64, arm, 386, mips, wasm

# Examples
GOOS=linux   GOARCH=amd64  go build -o myapp-linux-amd64 .
GOOS=darwin  GOARCH=arm64  go build -o myapp-darwin-arm64 .
GOOS=windows GOARCH=amd64  go build -o myapp.exe .
GOOS=js      GOARCH=wasm   go build -o main.wasm .

# CGO — disabled by default for cross-compilation
CGO_ENABLED=0 GOOS=linux go build -o myapp .

# Build for all platforms
for os in linux darwin windows; do
  for arch in amd64 arm64; do
    GOOS=$os GOARCH=$arch go build -o dist/myapp-$os-$arch .
  done
done
```

## Build Tags / Constraints

```go
//go:build linux
//go:build !cgo
//go:build go1.21
//go:build linux && (amd64 || arm64)

// File naming also works:
// myfile_linux.go         — compiled only on Linux
// myfile_linux_amd64.go   — compiled only on Linux/amd64
// myfile_test.go          — compiled only during go test
```

## Testable Examples (documented behavior)

```go
// In package doc.go or separate example_test.go file
package mylib_test

import "fmt"

func Example() {
    fmt.Println("Hello from example")
    // Output:
    // Hello from example
}

func ExampleStack_Push() {
    s := &Stack[int]{}
    s.Push(1)
    s.Push(2)
    fmt.Println(s.Len())
    // Output:
    // 2
}
```
