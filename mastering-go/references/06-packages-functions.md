# Ch 6 — Go Packages and Functions

## Packages

```
myapp/
├── go.mod
├── main.go
└── internal/
    └── util/
        └── util.go   // package util
```

```go
// util.go
package util

// Exported — uppercase
func Add(a, b int) int { return a + b }

// Unexported — lowercase (package-private)
func helper() {}
```

### Package naming rules
- Lowercase, short, no underscores (`httputil` not `http_util`)
- Package name ≠ directory name (though usually same)
- Avoid `common`, `util`, `misc` — use specific names
- `internal/` directory: only importable by parent tree

### init() function
```go
func init() {
    // Runs automatically before main(), after var declarations
    // Each file can have multiple init() functions
    // Cannot be called explicitly
    setupDatabase()
    loadConfig()
}
```

Order: package-level vars → init() → main()

## Modules (go.mod)

```
module example.com/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jmoiron/sqlx v1.3.5
)
```

```bash
go mod init example.com/myapp
go get github.com/pkg@v1.2.3       # add dependency
go get github.com/pkg@latest        # upgrade
go mod tidy                         # clean up unused deps
go mod download                     # pre-download deps
go mod vendor                       # copy deps to ./vendor
go list -m all                      # list all modules
go mod graph                        # dependency graph
```

### Replace directive (local development)
```go
replace example.com/mylib => ../mylib
```

### Workspaces (Go 1.18+) — go.work
```go
// go.work
go 1.21

use (
    ./myapp
    ./mylib
)
```
```bash
go work init ./myapp ./mylib
go work use ./anothermod
go work sync
```
Workspaces let multiple modules work together without publishing.

## Functions

```go
// Basic
func add(a, b int) int { return a + b }

// Multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Named return values
func minMax(s []int) (min, max int) {
    min, max = s[0], s[0]
    for _, v := range s[1:] {
        if v < min { min = v }
        if v > max { max = v }
    }
    return  // naked return
}
```

### Variadic functions
```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
sum(1, 2, 3)
nums := []int{1, 2, 3}
sum(nums...)   // spread slice
```

### Functions as values
```go
// Function type
type Transformer func(string) string

// Higher-order function
func apply(s string, fns ...Transformer) string {
    for _, fn := range fns {
        s = fn(s)
    }
    return s
}

result := apply("hello",
    strings.ToUpper,
    func(s string) string { return s + "!" },
)
```

### Closures
```go
func makeCounter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}
c := makeCounter()
c()  // 1
c()  // 2

// Closure captures by reference — loop variable gotcha
funcs := make([]func(), 3)
for i := 0; i < 3; i++ {
    i := i  // shadow with new variable (Go 1.22+ loop vars are per-iteration)
    funcs[i] = func() { fmt.Println(i) }
}
```

## defer

```go
// Runs when enclosing function returns (LIFO order)
func processFile(name string) error {
    f, err := os.Open(name)
    if err != nil { return err }
    defer f.Close()     // guaranteed cleanup

    // ... use f
    return nil
}

// Multiple defers — LIFO
func example() {
    defer fmt.Println("third")
    defer fmt.Println("second")
    defer fmt.Println("first")
    // Output: first, second, third
}

// Defer arguments evaluated immediately
x := 10
defer fmt.Println(x)   // prints 10, not whatever x is later
x = 20

// Defer with named return values
func double(x int) (result int) {
    defer func() { result *= 2 }()
    result = x
    return   // result = x*2 after defer
}
```

## panic and recover

```go
// panic — stops normal execution, runs deferred functions, unwinds stack
func mustPositive(n int) int {
    if n <= 0 {
        panic(fmt.Sprintf("expected positive, got %d", n))
    }
    return n
}

// recover — catch panics (only useful inside deferred function)
func safeDiv(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("recovered: %v", r)
        }
    }()
    return a / b, nil
}

// Middleware pattern — recover from panics in HTTP handlers
func safeHandler(h http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if r := recover(); r != nil {
                http.Error(w, "Internal Server Error", 500)
                log.Printf("panic: %v\n%s", r, debug.Stack())
            }
        }()
        h(w, r)
    }
}
```

Use panic only for truly unrecoverable programmer errors (index out of bounds, nil pointer). Prefer returning errors for expected failure modes.

## SQLite3 Integration (example)

```go
import (
    "database/sql"
    _ "github.com/mattn/go-sqlite3"
)

db, err := sql.Open("sqlite3", "./mydb.sqlite")
if err != nil { log.Fatal(err) }
defer db.Close()

// Create table
db.Exec(`CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)`)

// Insert
res, err := db.Exec("INSERT INTO users(name) VALUES(?)", "Alice")
id, _ := res.LastInsertId()

// Query
rows, err := db.Query("SELECT id, name FROM users")
defer rows.Close()
for rows.Next() {
    var id int
    var name string
    rows.Scan(&id, &name)
    fmt.Println(id, name)
}

// Single row
var name string
db.QueryRow("SELECT name FROM users WHERE id = ?", 1).Scan(&name)
```

## Documentation

```go
// Package comment — appears before package declaration
// Package mathutil provides mathematical utility functions.
package mathutil

// Function comment — starts with function name
// Add returns the sum of two integers.
func Add(a, b int) int { return a + b }

// Deprecated — signals to tools and IDEs
// Deprecated: Use NewAdd instead.
func OldAdd(a, b int) int { return a + b }

// Example functions — tested by go test
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output:
    // 3
}
```

```bash
go doc mathutil.Add       # show doc
go doc -all mathutil      # all exported symbols
```

## Useful Stdlib Packages

| Package | Purpose |
|---------|---------|
| `fmt` | Formatted I/O |
| `os` | OS interface (files, env, signals) |
| `io` | I/O primitives |
| `bufio` | Buffered I/O |
| `strings` | String manipulation |
| `strconv` | String conversions |
| `math` | Math functions |
| `sort` | Sorting |
| `errors` | Error creation/wrapping |
| `log` | Simple logging |
| `log/slog` | Structured logging (1.21+) |
| `time` | Time/duration |
| `sync` | Synchronization primitives |
| `context` | Cancellation, deadlines |
| `encoding/json` | JSON encode/decode |
| `net/http` | HTTP client/server |
| `path/filepath` | File path manipulation |
| `crypto/rand` | Cryptographically secure random |
