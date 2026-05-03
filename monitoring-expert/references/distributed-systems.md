# Distributed Systems Monitoring
## Chapter 10: Distributed Tracing, Microservices, Service Maps

---

## Why Distributed Systems Are Different

In a monolithic application, a slow request means the application is slow. In a distributed system, a slow request could be caused by any of dozens of services, networks, or shared dependencies.

**The core problem:** Metrics and logs are per-service. But user requests cross many services. Correlating what happened to one request across the whole system is impossible with metrics alone.

This is what distributed tracing solves.

---

## Distributed Tracing

Distributed tracing records the path of a request through every service it touches, capturing:
- Which services handled it
- How long each service took
- What calls each service made
- Where time was actually spent

### Concepts

**Trace**
A complete record of a single request's journey from entry point to final response. Identified by a unique `trace_id`.

**Span**
A single unit of work within a trace. Every service call, database query, or external API call becomes a span. Identified by a `span_id`.

**Parent-Child Relationship**
Spans form a tree. A request to Service A spawns spans in Service B, C, D. Service A's span is the parent; B, C, D are children.

```
Trace: a1b2c3d4
│
├─ Span: API Gateway (50ms total)
│   │
│   ├─ Span: Auth Service (5ms)
│   │
│   ├─ Span: Order Service (40ms)
│   │   │
│   │   ├─ Span: DB query: get_order (3ms)
│   │   │
│   │   └─ Span: Payment Service (35ms)  ← bottleneck
│   │       │
│   │       └─ Span: Stripe API call (32ms)
│   │
│   └─ Span: Notification Service (2ms)
```

This waterfall view immediately identifies the bottleneck: the Stripe API call accounts for 64% of total latency.

### Context Propagation

For tracing to work, the `trace_id` and `span_id` must be passed with every inter-service call — via HTTP headers, message queue headers, or gRPC metadata.

Standard propagation formats:
- **W3C Trace Context** (`traceparent` header) — current standard; recommended for new systems
- **B3 Propagation** — Zipkin format; widely supported legacy standard
- **Jaeger propagation** — Jaeger-specific; avoid for new systems

All services must use the same propagation format. A single service that doesn't forward trace headers breaks the trace for all downstream calls.

### Sampling

Tracing every request produces enormous data volume. Use sampling:

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **Head sampling** | Decide at trace start whether to record | Simple; may miss rare errors |
| **Tail sampling** | Record everything; decide at end whether to keep (based on outcome) | Keeps errors and slow traces; complex |
| **Rate limiting** | Keep N traces per second regardless of rate | Prevents storage explosion |
| **Priority sampling** | Always keep error traces; sample success traces | Good default for most systems |

Recommended default: keep 100% of error traces, 1–10% of success traces.

---

## Tracing Infrastructure

### Components

**Instrumentation library** (in each service)
- Creates and manages spans
- Propagates context in outgoing calls
- Sends completed spans to a collector

**Collector / Agent**
- Receives spans from services
- Batches and forwards to backend
- Optionally applies sampling decisions

**Backend / Storage**
- Stores traces
- Indexes for search
- Provides query API

**UI**
- Trace waterfall view
- Service map
- Search by trace ID, service, latency range, error status

### Common Tracing Stacks

| Stack | Notes |
|-------|-------|
| **Jaeger + OpenTelemetry** | Open source; CNCF projects; strong ecosystem |
| **Zipkin** | Older open source standard; widely supported |
| **Tempo + Grafana** | Cost-efficient storage; integrates with Grafana stack |
| **Datadog APM** | SaaS; auto-instrumentation; excellent UI; expensive |
| **AWS X-Ray** | AWS-native; good for AWS-heavy architectures |
| **Honeycomb** | Advanced query capabilities; tail sampling; premium pricing |

### OpenTelemetry

OpenTelemetry is the vendor-neutral standard for instrumentation (metrics, traces, logs). It replaces vendor-specific SDKs.

Using OpenTelemetry means you can switch backends without re-instrumenting your application. For new projects: instrument with OpenTelemetry, deploy to any backend.

---

## Microservice Monitoring Strategy

### Service-Level Indicators per Service

Each microservice should expose:
- Request rate, error rate, p99 latency (RED method)
- Dependency health (is each downstream dependency reachable?)
- Internal resource utilization (CPU, memory, connection pool)

### Service Maps / Dependency Graphs

A service map visualizes which services call which, with health indicators:

```
[Browser]
    │
    ▼
[API Gateway] ──────► [Auth Service]
    │
    ├──► [Order Service] ──► [Order DB]
    │         │
    │         └──► [Payment Service] ──► [Stripe API]
    │                   │
    │                   └──► [Fraud Service]
    │
    └──► [Notification Service] ──► [SendGrid]
```

Use service maps to identify:
- Critical path dependencies (anything on the hot path to user-visible operations)
- Single points of failure (dependencies with no fallback)
- Unexpected connections (service calling something it shouldn't)

### Failure Mode Monitoring in Distributed Systems

Distributed systems fail in ways monoliths don't. Monitor for:

| Failure Mode | How to Detect |
|-------------|---------------|
| **Cascading failures** | Error rates rising across multiple services simultaneously |
| **Partial degradation** | One endpoint failing while others succeed; use per-endpoint error rates |
| **Retry storms** | Unusual spike in outgoing request rate from one service |
| **Timeout cascades** | Latency rising across services in the same call chain |
| **Data inconsistency** | Business metric divergences (orders placed ≠ inventory decrements) |

### Health Checks

Every service should expose a health check endpoint:
- `/health` or `/healthz` — binary up/down (suitable for load balancer routing)
- `/ready` or `/readyz` — ready to receive traffic (e.g., warmed up, dependencies available)
- `/metrics` — Prometheus-format metrics endpoint (if using Prometheus)

Kubernetes uses liveness probes (is it up?) and readiness probes (is it ready for traffic?) — these map directly to `/health` and `/ready`.

---

## Correlating Signals

The full picture of a distributed system incident requires all three signal types:

```
Metrics: "Error rate on order service spiked at 14:23"
    │
    ├── Find example trace_id from logs at 14:23
    │
    ▼
Traces: "Span for payment service shows 30s timeout"
    │
    ├── Narrow to payment service logs at 14:23
    │
    ▼
Logs: "ERROR: Database connection pool exhausted — all 50 connections in use"
    │
    └── Root cause identified: payment DB connection pool exhausted
```

This is why all three signals must use the same `trace_id` / correlation ID. Without it, you are pattern-matching by timestamp, which is imprecise and time-consuming.

---

## Synthetic Monitoring in Distributed Systems

Don't rely only on real user traffic to detect issues. Run synthetic checks that exercise critical paths:

- **Smoke tests** after every deploy: does the core user journey work?
- **Canary requests** from outside the production network: are services reachable externally?
- **Cross-region checks**: is every deployment region responding correctly?

Synthetic checks detect configuration errors, network partitions, and certificate expiry before real users encounter them.
