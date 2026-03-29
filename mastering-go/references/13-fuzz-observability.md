# Ch 13 — Fuzz Testing and Observability

## Fuzz Testing (Go 1.18+)

Fuzz testing automatically generates inputs to find edge cases and panics.

### Basic fuzz test
```go
// In a _test.go file
func FuzzReverse(f *testing.F) {
    // Seed corpus — known interesting inputs
    f.Add("hello")
    f.Add("")
    f.Add("日本語")
    f.Add("!@#$%^&*()")

    f.Fuzz(func(t *testing.T, s string) {
        // The property: reversing twice returns original
        reversed := Reverse(s)
        double := Reverse(reversed)
        if s != double {
            t.Errorf("reverse(%q) = %q; double reverse = %q", s, reversed, double)
        }

        // Also test for panics (any panic fails the fuzz test automatically)
    })
}
```

### Running fuzz tests
```bash
# Run seed corpus only (like regular test)
go test -run FuzzReverse ./...

# Run fuzzer (generates random inputs)
go test -fuzz FuzzReverse ./...

# Stop after specific duration
go test -fuzz FuzzReverse -fuzztime=30s ./...

# Limit workers
go test -fuzz FuzzReverse -parallel=4 ./...

# Run with specific corpus entry that previously failed
go test -run FuzzReverse/testdata/corpus/FuzzReverse/abc123 ./...
```

### Corpus files
Failed inputs are automatically saved to:
```
testdata/fuzz/FuzzReverse/<hash>
```

Format (one type per line):
```
go test fuzz v1
string("evil input\x00that crashed")
```

### Fuzz-friendly function signatures
```go
// Supported seed types: string, []byte, int, int8..int64, uint..uint64, float32, float64, bool, rune, byte

func FuzzParse(f *testing.F) {
    f.Add([]byte(`{"key":"value"}`))
    f.Fuzz(func(t *testing.T, data []byte) {
        // Must not panic
        _ , _ = parseJSON(data)
    })
}

func FuzzHTTPRequest(f *testing.F) {
    f.Add("GET", "/path", "body")
    f.Fuzz(func(t *testing.T, method, path, body string) {
        req, err := http.NewRequest(method, "http://example.com"+path,
            strings.NewReader(body))
        if err != nil { return }  // invalid inputs are OK to skip
        handler.ServeHTTP(httptest.NewRecorder(), req)
    })
}
```

### What to fuzz
- Parsers (JSON, XML, CSV, binary protocols)
- Decoders and deserializers
- String/byte manipulation functions
- Cryptographic functions
- Compression/decompression

## Observability

Observability = Logs + Metrics + Traces (the "three pillars")

## Structured Logging (log/slog — Go 1.21)

```go
import "log/slog"

// Default logger — writes to stderr
slog.Info("user logged in", "userID", 123, "ip", "1.2.3.4")
slog.Warn("rate limit approaching", "requests", 950, "limit", 1000)
slog.Error("database error", "err", err, "query", "SELECT ...")
slog.Debug("cache miss", "key", "user:123")

// Structured with groups
logger := slog.With("service", "auth", "version", "1.0")
logger.Info("started")

// JSON handler for production
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
    AddSource: true,  // adds file:line
})
logger = slog.New(handler)
slog.SetDefault(logger)

// Text handler for development
handler = slog.NewTextHandler(os.Stdout, nil)

// Log with context
ctx := context.WithValue(ctx, requestIDKey{}, "req-123")
logger.InfoContext(ctx, "handling request")

// Custom handler to add context values automatically
type contextHandler struct {
    slog.Handler
}
func (h contextHandler) Handle(ctx context.Context, r slog.Record) error {
    if id, ok := ctx.Value(requestIDKey{}).(string); ok {
        r.AddAttrs(slog.String("request_id", id))
    }
    return h.Handler.Handle(ctx, r)
}
```

### Log levels
```go
slog.LevelDebug  // -4
slog.LevelInfo   // 0
slog.LevelWarn   // 4
slog.LevelError  // 8
```

## Metrics (Prometheus + expvar)

### expvar — built-in metrics
```go
import "expvar"

var (
    requestCount  = expvar.NewInt("requests_total")
    errorCount    = expvar.NewInt("errors_total")
    activeConns   = expvar.NewInt("active_connections")
    avgLatency    = expvar.NewFloat("avg_latency_ms")
)

// Auto-exposed at GET /debug/vars (import _ "expvar" or register handler)
import _ "expvar"
// or: mux.Handle("/debug/vars", expvar.Handler())

requestCount.Add(1)
activeConns.Add(1)
defer activeConns.Add(-1)
```

### Prometheus (client_golang)
```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request latency",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "path", "status"},
    )
    inFlightGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "http_in_flight_requests",
        Help: "Current in-flight requests",
    })
)

func init() {
    prometheus.MustRegister(httpDuration, inFlightGauge)
}

func instrumentedHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        inFlightGauge.Inc()
        defer inFlightGauge.Dec()

        rw := &statusResponseWriter{ResponseWriter: w, status: 200}
        next.ServeHTTP(rw, r)

        httpDuration.WithLabelValues(
            r.Method, r.URL.Path, strconv.Itoa(rw.status),
        ).Observe(time.Since(start).Seconds())
    })
}

mux.Handle("/metrics", promhttp.Handler())
```

## Distributed Tracing (OpenTelemetry)

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/trace"
)

// Initialize tracer provider (Jaeger, Zipkin, OTLP...)
tp := initTracerProvider()
defer tp.Shutdown(ctx)
otel.SetTracerProvider(tp)

tracer := otel.Tracer("my-service")

// Create spans
func processRequest(ctx context.Context, id string) error {
    ctx, span := tracer.Start(ctx, "processRequest",
        trace.WithAttributes(attribute.String("request.id", id)))
    defer span.End()

    // Propagate context to downstream calls
    result, err := fetchData(ctx, id)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return err
    }
    span.SetAttributes(attribute.Int("result.count", len(result)))
    return nil
}

// HTTP middleware — propagate trace context
otelhttp.NewHandler(mux, "server")
```

## Health Check Endpoints

```go
type HealthStatus struct {
    Status   string            `json:"status"`
    Checks   map[string]string `json:"checks"`
    Version  string            `json:"version"`
}

func healthHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        checks := map[string]string{}
        status := "ok"

        ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
        defer cancel()

        if err := db.PingContext(ctx); err != nil {
            checks["database"] = "unhealthy: " + err.Error()
            status = "degraded"
        } else {
            checks["database"] = "healthy"
        }

        code := http.StatusOK
        if status != "ok" {
            code = http.StatusServiceUnavailable
        }
        respondJSON(w, code, HealthStatus{
            Status:  status,
            Checks:  checks,
            Version: "1.0.0",
        })
    }
}
```

## Runtime Metrics

```go
import "runtime"

var m runtime.MemStats
runtime.ReadMemStats(&m)

fmt.Printf("Alloc = %v MB\n", m.Alloc/1024/1024)
fmt.Printf("TotalAlloc = %v MB\n", m.TotalAlloc/1024/1024)
fmt.Printf("Sys = %v MB\n", m.Sys/1024/1024)
fmt.Printf("NumGC = %v\n", m.NumGC)
fmt.Printf("Goroutines = %d\n", runtime.NumGoroutine())
```

## GODEBUG Environment Variable

```bash
GODEBUG=gctrace=1 ./myapp      # print GC events to stderr
GODEBUG=schedtrace=1000        # print scheduler info every 1000ms
GODEBUG=memprofilerate=1       # profile every allocation
GODEBUG=netdns=2               # verbose DNS resolution
GODEBUG=http2debug=2           # verbose HTTP/2 debugging
```
