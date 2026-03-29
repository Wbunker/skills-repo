---
name: mastering-go
description: >
  Expert-level Go programming assistance grounded in "Mastering Go" (4th ed.) by Mihalis Tsoukalos.
  Use when the user is writing or debugging Go code, asking about Go syntax, types, interfaces,
  goroutines, channels, concurrency patterns, HTTP servers, REST APIs, TCP/IP networking,
  WebSocket, generics, reflection, testing, profiling, fuzz testing, observability, or performance.
  Also triggers on: go mod, go build, go test, go run, go generate, defer, panic/recover,
  goroutine leaks, race conditions, context cancellation, io.Reader/Writer, cobra CLI,
  UNIX signals, file I/O, benchmarking, cross-compilation, eBPF with Go, or any Go standard
  library package (fmt, net/http, sync, context, os, io, bufio, encoding/json, etc.).
---

# Mastering Go Expert

Load only the reference file(s) relevant to the user's question. Read multiple files if the question spans topics.

## Topic Routing

### Fundamentals
- **Go introduction, compilation, go toolchain, program structure, fmt/os/log, command-line args, basic I/O** → [references/01-go-basics.md](references/01-go-basics.md)
- **Numeric types, bool, string, rune, byte, arrays, slices, pointers, constants, iota, time/date** → [references/02-data-types.md](references/02-data-types.md)
- **Maps, structs, struct embedding, anonymous fields, regular expressions, CSV, JSON basics, data persistence** → [references/03-composite-types.md](references/03-composite-types.md)

### Type System
- **Generics, type parameters, type constraints, cmp/slices/maps packages, generic data structures** → [references/04-generics.md](references/04-generics.md)
- **Interfaces, duck typing, type methods, sort.Interface, empty interface (any), type assertions, type switches, reflection** → [references/05-interfaces-reflection.md](references/05-interfaces-reflection.md)

### Code Organization
- **Packages, modules (go.mod), init(), functions, variadic, closures, defer, panic/recover, workspaces (go.work)** → [references/06-packages-functions.md](references/06-packages-functions.md)

### Systems Programming
- **UNIX signals, os.Signal, syscall, file I/O, os.File, io.Reader/Writer, bufio, filepath, cobra/viper CLI** → [references/07-systems-programming.md](references/07-systems-programming.md)

### Concurrency
- **Goroutines, channels (buffered/unbuffered), select, pipelines, fan-out/fan-in, sync.Mutex/RWMutex, sync.WaitGroup, atomic, context, worker pools, race detector** → [references/08-concurrency.md](references/08-concurrency.md)

### Networking & Web
- **net/http, HTTP servers, handlers, middleware, web clients, http.Client, Prometheus metrics** → [references/09-web-services.md](references/09-web-services.md)
- **net package, TCP/IP, UDP, UNIX sockets, WebSocket, RabbitMQ, protocol design** → [references/10-networking.md](references/10-networking.md)
- **REST API design, RESTful servers, routing, request/response patterns, Swagger, binary upload/download** → [references/11-rest-apis.md](references/11-rest-apis.md)

### Quality & Performance
- **go test, table-driven tests, testify, example functions, benchmarks, pprof profiling, cross-compilation** → [references/12-testing-profiling.md](references/12-testing-profiling.md)
- **Fuzz testing (go test -fuzz), corpus, observability, structured logging (slog), metrics, tracing** → [references/13-fuzz-observability.md](references/13-fuzz-observability.md)
- **Performance optimization, memory model, sync/atomic, eBPF with Go, escape analysis, GC tuning, GODEBUG** → [references/14-performance.md](references/14-performance.md)

### Language Evolution
- **Go 1.18–1.23 new features, toolchain changes, slog, arena allocator, range-over-func, min/max builtins** → [references/15-recent-versions.md](references/15-recent-versions.md)

---

## Always-Available Quick Reference

### Go Type Zero Values
| Type | Zero Value |
|------|-----------|
| `bool` | `false` |
| integers, floats | `0` |
| `string` | `""` |
| pointer, slice, map, chan, func, interface | `nil` |
| struct | all fields at their zero values |

### Key Compile-Time Rules
- Unused local variables → compile error
- Unused imports → compile error
- Exported identifiers start with uppercase
- `:=` for declaration+assignment (inside functions only); `var` at package level
- No implicit type conversions between numeric types

### Error Handling Idiom
```go
result, err := someFunc()
if err != nil {
    return fmt.Errorf("context: %w", err)  // %w wraps for errors.Is/As
}
```

### go Toolchain Cheat Sheet
| Command | Purpose |
|---------|---------|
| `go build ./...` | Compile all packages |
| `go run main.go` | Compile + run |
| `go test ./...` | Run all tests |
| `go test -race ./...` | Run with race detector |
| `go mod tidy` | Sync go.mod/go.sum |
| `go vet ./...` | Static analysis |
| `go doc pkg.Symbol` | Show documentation |
| `go generate ./...` | Run //go:generate directives |
| `go install tool@version` | Install a tool |
