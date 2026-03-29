# Ch 8 — Go Concurrency

## Goroutines

A goroutine is a lightweight thread managed by the Go runtime (starts ~2KB stack, grows as needed).

```go
// Launch goroutine
go func() {
    fmt.Println("in goroutine")
}()

go doWork(arg1, arg2)   // runs doWork concurrently

// Arguments evaluated immediately at go statement
x := 10
go func(n int) {
    fmt.Println(n)   // prints 10, not whatever x becomes later
}(x)
```

**Key rule:** `main()` returning kills all goroutines. Use synchronization to wait.

## Channels

Channels are the primary communication mechanism between goroutines.

```go
// Create
ch := make(chan int)          // unbuffered (synchronous)
ch := make(chan int, 10)      // buffered (async up to capacity)
var ch chan int                // nil channel — send/receive blocks forever

// Send
ch <- 42

// Receive
v := <-ch
v, ok := <-ch   // ok = false if channel closed and empty

// Close — signals no more sends
close(ch)
// Sending to closed channel → panic
// Receiving from closed empty channel → zero value, ok=false

// Range over channel (receives until closed)
for v := range ch {
    fmt.Println(v)
}
```

### Directional channel types
```go
func producer(ch chan<- int) {  // send-only
    ch <- 42
}
func consumer(ch <-chan int) {  // receive-only
    v := <-ch
}
// Converts bidirectional → directional automatically
```

## select Statement

```go
select {
case v := <-ch1:
    fmt.Println("from ch1:", v)
case ch2 <- 42:
    fmt.Println("sent to ch2")
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("no channels ready") // non-blocking
}
```

## sync Package

### sync.WaitGroup — wait for goroutines
```go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        doWork(id)
    }(i)
}
wg.Wait()   // block until all Done() calls
```

### sync.Mutex — exclusive lock
```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
```

### sync.RWMutex — readers/writer lock
```go
var rw sync.RWMutex

// Multiple concurrent readers
rw.RLock()
defer rw.RUnlock()
// ... read

// Exclusive writer
rw.Lock()
defer rw.Unlock()
// ... write
```

### sync.Once — run once
```go
var once sync.Once
var instance *Singleton

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
    })
    return instance
}
```

### sync.Map — concurrent-safe map
```go
var m sync.Map

m.Store("key", "value")
v, ok := m.Load("key")
m.LoadOrStore("key", "default")
m.Delete("key")
m.Range(func(k, v interface{}) bool {
    fmt.Println(k, v)
    return true   // continue iteration
})
```

### sync.Pool — object reuse pool
```go
var pool = sync.Pool{
    New: func() interface{} { return &bytes.Buffer{} },
}

buf := pool.Get().(*bytes.Buffer)
buf.Reset()
defer pool.Put(buf)
// ... use buf
```

## Pipelines

```go
// Stage 1: generate
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Stage 2: transform
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Compose
c := generate(2, 3, 4)
out := square(c)
for v := range out {
    fmt.Println(v)  // 4, 9, 16
}
```

## Fan-Out / Fan-In

```go
// Fan-out: distribute work across N workers
func fanOut(in <-chan Work, n int) []<-chan Result {
    channels := make([]<-chan Result, n)
    for i := 0; i < n; i++ {
        channels[i] = worker(in)
    }
    return channels
}

// Fan-in: merge multiple channels into one
func merge(channels ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    merged := make(chan int)

    output := func(c <-chan int) {
        defer wg.Done()
        for v := range c {
            merged <- v
        }
    }

    wg.Add(len(channels))
    for _, c := range channels {
        go output(c)
    }

    go func() {
        wg.Wait()
        close(merged)
    }()
    return merged
}
```

## Worker Pool

```go
func workerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    go func() {
        wg.Wait()
        close(results)
    }()
}

jobs := make(chan Job, 100)
results := make(chan Result, 100)
workerPool(jobs, results, runtime.NumCPU())
```

## context Package — Cancellation and Deadlines

```go
import "context"

// Cancel context
ctx, cancel := context.WithCancel(context.Background())
defer cancel()   // always defer cancel to avoid resource leak

// Deadline / timeout
ctx, cancel = context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

ctx, cancel = context.WithDeadline(context.Background(), time.Now().Add(5*time.Second))
defer cancel()

// Pass context to functions
resp, err := http.NewRequestWithContext(ctx, "GET", url, nil)

// Check cancellation
select {
case <-ctx.Done():
    return ctx.Err()   // context.Canceled or context.DeadlineExceeded
default:
    // continue
}

// Values in context (use sparingly — for request-scoped data only)
type keyType struct{}
ctx = context.WithValue(ctx, keyType{}, "request-id-123")
val := ctx.Value(keyType{}).(string)
```

## sync/atomic — Lock-Free Operations

```go
import "sync/atomic"

var counter int64

atomic.AddInt64(&counter, 1)
atomic.AddInt64(&counter, -1)
val := atomic.LoadInt64(&counter)
atomic.StoreInt64(&counter, 0)
swapped := atomic.CompareAndSwapInt64(&counter, old, new)

// atomic.Value for arbitrary types
var config atomic.Value
config.Store(NewConfig())
current := config.Load().(Config)
```

## Race Detector

```bash
go test -race ./...
go run -race main.go
go build -race -o myapp .
```

The race detector adds ~5-10x overhead. Run during testing, not production.

## Common Concurrency Patterns

### Semaphore (limit concurrency)
```go
sem := make(chan struct{}, 10)  // max 10 concurrent

func doWithLimit(work func()) {
    sem <- struct{}{}
    defer func() { <-sem }()
    work()
}
```

### Done channel (cancellation signal)
```go
done := make(chan struct{})

go func() {
    select {
    case <-done:
        return
    case v := <-work:
        process(v)
    }
}()

close(done)  // broadcast cancellation to all receivers
```

### errgroup (Go 1.17+)
```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(context.Background())

g.Go(func() error {
    return fetchFromDB(ctx)
})
g.Go(func() error {
    return fetchFromAPI(ctx)
})

if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

## Go Scheduler (GOMAXPROCS)

```go
import "runtime"

runtime.GOMAXPROCS(runtime.NumCPU())   // use all CPUs (default since Go 1.5)
runtime.NumGoroutine()                  // current goroutine count
runtime.Gosched()                       // yield CPU to other goroutines

// Print goroutine count periodically for debugging
go func() {
    for range time.Tick(5 * time.Second) {
        fmt.Println("goroutines:", runtime.NumGoroutine())
    }
}()
```
