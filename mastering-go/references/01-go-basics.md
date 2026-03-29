# Ch 1 — A Quick Introduction to Go

## Language Characteristics

- Statically typed, compiled, garbage-collected
- Fast compilation; single binary output (statically linked by default)
- Built-in concurrency (goroutines + channels)
- No classes — composition via structs and interfaces
- No exceptions — errors are values
- No operator overloading, no implicit conversions
- First-class functions, closures

## Program Structure

```go
package main          // every executable is in package main

import (
    "fmt"
    "os"
)

func main() {         // entry point — no arguments, no return
    fmt.Println("Hello, Go!")
}
```

Rules:
- Every file starts with `package <name>`
- `main` package + `main()` function = executable
- All other packages = library packages

## The go Toolchain

```bash
go build main.go          # compile to ./main (or main.exe on Windows)
go build -o myapp .       # compile all files in current dir → myapp
go run main.go            # compile + run (no binary left on disk)
go install .              # compile + put binary in $GOPATH/bin
go clean                  # remove build artifacts
```

### Module initialization
```bash
go mod init example.com/myapp    # creates go.mod
go mod tidy                      # adds missing / removes unused deps
go get github.com/pkg@v1.2.3    # add dependency
```

## Input / Output

### fmt package
```go
fmt.Print("no newline")
fmt.Println("with newline")
fmt.Printf("name=%s age=%d\n", name, age)   // formatted

s := fmt.Sprintf("val=%v", x)   // returns string
fmt.Fprintf(os.Stderr, "err: %v\n", err)    // write to writer
```

### Reading from stdin
```go
var x int
fmt.Scan(&x)                  // reads space-separated tokens
fmt.Scanf("%d", &x)           // formatted input
fmt.Scanln(&name, &age)       // reads until newline

scanner := bufio.NewScanner(os.Stdin)
for scanner.Scan() {
    line := scanner.Text()
}
```

### bufio.Scanner for files / stdin
```go
file, err := os.Open("data.txt")
if err != nil { log.Fatal(err) }
defer file.Close()

scanner := bufio.NewScanner(file)
for scanner.Scan() {
    fmt.Println(scanner.Text())
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}
```

## Command-Line Arguments

```go
import "os"

args := os.Args        // []string; os.Args[0] = program name
if len(os.Args) < 2 {
    fmt.Fprintln(os.Stderr, "usage: prog <arg>")
    os.Exit(1)
}
firstArg := os.Args[1]
```

### flag package
```go
import "flag"

name := flag.String("name", "world", "who to greet")
count := flag.Int("n", 1, "repeat count")
flag.Parse()

for i := 0; i < *count; i++ {
    fmt.Println("Hello,", *name)
}
// remaining args after flags: flag.Args()
```

## Logging

```go
import "log"

log.Println("info message")          // timestamps automatically
log.Printf("value: %v", x)
log.Fatal("error")                   // calls os.Exit(1) after printing
log.Fatalf("error: %v", err)
log.Panic("bad")                     // calls panic() after printing

// Custom logger
logger := log.New(os.Stderr, "PREFIX: ", log.LstdFlags|log.Lshortfile)
logger.Println("custom log")
```

### log/slog (Go 1.21+) — structured logging
```go
import "log/slog"

slog.Info("server started", "port", 8080)
slog.Error("connection failed", "err", err)

// JSON handler
handler := slog.NewJSONHandler(os.Stdout, nil)
logger := slog.New(handler)
logger.Info("request", "method", "GET", "path", "/api")
```

## Printing Verbs Reference

| Verb | Meaning |
|------|---------|
| `%v` | Default format |
| `%+v` | Struct with field names |
| `%#v` | Go syntax representation |
| `%T` | Type of value |
| `%d` | Integer (decimal) |
| `%x` | Integer (hex), `%X` uppercase |
| `%b` | Integer (binary) |
| `%f` | Float (decimal), `%e` scientific |
| `%s` | String |
| `%q` | Quoted string |
| `%p` | Pointer address |
| `%t` | Boolean |

## Error Types and Sentinel Errors

```go
import "errors"

// Create simple error
err := errors.New("something went wrong")

// Wrap with context
err2 := fmt.Errorf("operation failed: %w", err)

// Check error chain
if errors.Is(err2, err) { /* true */ }

// Custom error type
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

var ve *ValidationError
if errors.As(someErr, &ve) {
    fmt.Println("field:", ve.Field)
}
```

## Compilation and Build Tags

```go
//go:build linux && amd64     // Go 1.17+ syntax
// +build linux,amd64         // old syntax (still valid)
```

```bash
GOOS=linux GOARCH=amd64 go build -o myapp-linux .   # cross-compile
```

## godoc / go doc

```bash
go doc fmt.Println          # show doc for symbol
go doc -all fmt             # show all docs for package
godoc -http=:6060           # browse docs in browser at localhost:6060
```
