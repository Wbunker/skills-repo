# Instrumentation — Client Libraries

## Philosophy

White-box monitoring: instrument the code you own so it exposes meaningful internal metrics directly. This is superior to log-scraping or black-box probing for most purposes.

## Official Client Libraries

| Language | Library | Import |
|----------|---------|--------|
| Go | `prometheus/client_golang` | `github.com/prometheus/client_golang/prometheus` |
| Java | `prometheus/client_java` (v1.x) | `io.prometheus:prometheus-metrics-core` |
| Python | `prometheus/client_python` | `prometheus_client` |
| Ruby | `prometheus/client_ruby` | `prometheus/client` |

## Go Instrumentation

### Counter
```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var requestsTotal = promauto.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total number of HTTP requests.",
    },
    []string{"method", "status"},
)

// Usage
requestsTotal.WithLabelValues("GET", "200").Inc()
```

### Gauge
```go
var activeConnections = promauto.NewGauge(prometheus.GaugeOpts{
    Name: "active_connections",
    Help: "Current number of active connections.",
})

activeConnections.Set(42)
activeConnections.Inc()
activeConnections.Dec()
```

### Histogram
```go
var requestDuration = promauto.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request latency.",
        Buckets: prometheus.DefBuckets, // .005 .01 .025 .05 .1 .25 .5 1 2.5 5 10
    },
    []string{"handler"},
)

// Usage — observe a duration
timer := prometheus.NewTimer(requestDuration.WithLabelValues("/api/v1/query"))
defer timer.ObserveDuration()
```

### Custom Buckets
```go
Buckets: prometheus.LinearBuckets(0, 50, 10),        // 0, 50, 100, … 450
Buckets: prometheus.ExponentialBuckets(0.1, 2, 10),  // 0.1, 0.2, 0.4, …
Buckets: []float64{0.01, 0.05, 0.1, 0.5, 1.0, 5.0},
```

### Exposing the HTTP handler
```go
import "github.com/prometheus/client_golang/prometheus/promhttp"

http.Handle("/metrics", promhttp.Handler())
http.ListenAndServe(":8080", nil)
```

## Python Instrumentation

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

requests_total.labels(method='GET', status='200').inc()

with request_duration.time():
    do_work()

start_http_server(8000)  # exposes /metrics on port 8000
```

## Java Instrumentation (v1.x)

```java
import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.exporter.httpserver.HTTPServer;

Counter requestsTotal = Counter.builder()
    .name("http_requests_total")
    .help("Total HTTP requests")
    .labelNames("method", "status")
    .register();

requestsTotal.labelValues("GET", "200").inc();

HTTPServer server = HTTPServer.builder().port(8080).buildAndStart();
```

## Naming Conventions

- Format: `<namespace>_<subsystem>_<name>_<unit>`
- Use base units: `seconds`, `bytes`, `ratios` (not `milliseconds`, `megabytes`, `percentages`)
- Counters end in `_total`
- Histograms produce `_bucket`, `_sum`, `_count` automatically
- Gauges describing a ratio: `_ratio` (0.0–1.0)

Examples:
```
http_requests_total
http_request_duration_seconds
process_resident_memory_bytes
go_goroutines
queue_length
```

## What to Instrument

### The Four Golden Signals (Google SRE Book)
1. **Latency** — time to service a request (Histogram)
2. **Traffic** — requests per second (Counter → rate())
3. **Errors** — error rate (Counter → rate())
4. **Saturation** — how full the system is (Gauge)

### USE Method (Brendan Gregg)
For resources (CPU, memory, disk, network):
1. **Utilization** — percent of time busy
2. **Saturation** — work queued/waiting
3. **Errors** — error events

### RED Method
For services:
1. **Rate** — requests per second
2. **Errors** — error rate
3. **Duration** — latency distribution

## Cardinality Warning

High cardinality = many unique label value combinations = memory/disk explosion.

**Never use as label values:**
- User IDs, session tokens, email addresses
- IP addresses (unbounded)
- Timestamps or request IDs
- Free-form strings from user input

Good: `status="200"`, `method="GET"`, `region="us-east-1"`
Bad: `user_id="abc123"`, `request_id="uuid-..."`, `url="/user/42"`
