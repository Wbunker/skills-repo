# Instrumentation
## Chapter 8: StatsD, Application Metrics, Tagging Conventions

---

## What Is Instrumentation?

Instrumentation is the act of adding code or configuration to a system to emit observable signals — metrics, logs, or traces. Without instrumentation, a system is a black box.

**Two approaches:**
- **Code-level instrumentation** — developers add metric calls inside application code
- **Agent-based instrumentation** — a sidecar or agent collects metrics from the outside (OS-level, network-level)

Both are necessary. Agent-based collection covers infrastructure; code-level instrumentation captures business behavior.

---

## StatsD

StatsD is a lightweight UDP-based protocol for sending application metrics from code to a collection daemon. Developed at Etsy, it is now a de facto standard supported by virtually every metrics backend.

### How StatsD Works

```
Application code
    │
    │ UDP packet (fire-and-forget)
    ▼
StatsD daemon
    │
    │ aggregates over flush interval (default 10s)
    ▼
Metrics backend (Graphite, InfluxDB, Prometheus, Datadog, etc.)
```

**Key property:** UDP means the application does not block waiting for the metrics system. If the StatsD daemon is down, metrics are lost silently — which is acceptable; monitoring should not be able to take down your application.

### Metric Types in StatsD

#### Counter (`c`)

Tracks how many times something happens. StatsD aggregates into a rate over the flush interval.

```
# Format: <metric_name>:<value>|<type>
payments.processed:1|c
http.requests:1|c
errors.database:1|c
```

Use for: events you want to count and compute rates on.

#### Gauge (`g`)

Reports a current value. StatsD uses the last value seen in the flush interval.

```
queue.depth:42|g
active.sessions:1204|g
cpu.utilization:67.3|g
```

Use for: current state of a resource or buffer.

#### Timer (`ms`)

Records a duration. StatsD computes min, max, mean, percentiles over the flush interval.

```
# Value is milliseconds
http.request.duration:145|ms
db.query.duration:23|ms
checkout.flow.duration:1832|ms
```

Use for: anything you want to measure latency or duration for.

#### Set (`s`)

Counts unique values seen in the flush interval.

```
# Count unique users in this interval
active.users:user-12345|s
```

Use sparingly — sets are expensive to compute at high cardinality.

#### Sampling

For very high-frequency events, sample to reduce UDP packet volume:

```
# Send 10% of the time; StatsD multiplies by 10
http.requests:1|c|@0.1
```

Only use sampling for counters and timers. Do not sample gauges.

---

## Instrumentation Patterns

### Timing Code Blocks

```python
# Python example (pseudocode)
import statsd
client = statsd.StatsClient('localhost', 8125)

with client.timer('checkout.process_payment'):
    result = process_payment(order)
```

Measure anything that interacts with external systems (databases, APIs, queues) and any critical business process.

### Counting Events with Outcomes

Track both the event and its outcome as separate metrics or via tagging:

```
# Two counters: one for total, one for failures
payments.attempted:1|c
payments.failed:1|c   # only when failed

# Or with tagging (backends that support it)
payments.processed:1|c|#outcome:success
payments.processed:1|c|#outcome:failure
```

### Measuring Queue Depth as a Gauge

```python
# Emit periodically in a background thread
def report_queue_depth():
    while True:
        depth = queue.size()
        client.gauge('jobs.queue.depth', depth)
        time.sleep(10)
```

### Tracking External Dependency Latency

Every call to an external system should be timed and its outcome tracked:

```python
start = time.time()
try:
    response = external_api.call(payload)
    client.incr('external_api.success')
except ExternalAPIError:
    client.incr('external_api.error')
finally:
    duration_ms = (time.time() - start) * 1000
    client.timing('external_api.latency', duration_ms)
```

---

## Tagging Conventions

Tags (also called labels or dimensions) allow you to slice metrics by arbitrary attributes without creating separate metric names.

### Standard Tags

Apply consistently across all services:

| Tag | Values | Purpose |
|-----|--------|---------|
| `env` | production, staging, development | Filter by environment |
| `service` | api, worker, scheduler | Filter by service |
| `region` | us-east-1, eu-west-1 | Filter by deployment region |
| `version` | 1.4.2, git-sha | Correlate metrics with deploys |
| `status` | success, failure, timeout | Outcome classification |
| `method` | GET, POST | For HTTP metrics |
| `endpoint` | /checkout, /api/v2/users | Grouped route (not raw URL) |

### High-Cardinality Warning

Tags with unbounded or very high cardinality cause storage and query performance problems:

- **Safe:** `env`, `region`, `service`, `status` (< 100 unique values)
- **Dangerous:** `user_id`, `request_id`, `ip_address` (millions of unique values)
- **Use logs or tracing instead** for per-request or per-user detail

### Endpoint Normalization

Always normalize URL paths to remove variable segments:

```
# Wrong (creates one metric series per user)
/api/users/12345/orders
/api/users/67890/orders

# Right (one metric series for the endpoint pattern)
/api/users/{id}/orders
```

---

## What to Instrument

### Always Instrument

- Every HTTP endpoint (request count, duration, error rate)
- Every external service call (latency, error rate)
- Every database query type (duration by query category, error rate)
- Every background job (duration, success/failure, queue depth)
- Every cache interaction (hit rate, miss rate, latency)
- Critical business events (orders placed, payments processed, signups completed)

### Instrumentation Debt

Under-instrumented systems produce reactive monitoring — you discover problems when users report them. Treat instrumentation like testing: it is part of the definition of done for new code.

**Checklist for new code:**
- [ ] New HTTP endpoints emit request count, duration, error rate
- [ ] New external service calls emit latency and error rate
- [ ] New background jobs emit execution time and outcome
- [ ] New business-critical events emit counters
- [ ] Any new resource that can saturate emits a gauge

---

## Client Libraries

StatsD clients are available for essentially every language. Most metrics backends also provide their own clients with extended capabilities (histograms, native tagging).

| Language | StatsD Client | Native Prometheus/Datadog |
|----------|--------------|---------------------------|
| Python | `statsd` | `prometheus_client`, `datadog` |
| Go | `alexcesaro/statsd` | `prometheus/client_golang` |
| Node.js | `node-statsd` | `prom-client` |
| Ruby | `statsd-ruby` | `prometheus-client` |
| Java | `java-dogstatsd-client` | Micrometer |
| .NET | `StatsdClient` | `prometheus-net` |

For new projects, prefer native instrumentation libraries over StatsD when your backend supports it — they offer better type safety, histogram support, and avoid the UDP aggregation delay.
