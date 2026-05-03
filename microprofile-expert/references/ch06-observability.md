# Chapter 6: Observability — Health, Metrics, OpenTracing

## MicroProfile Health 3.1

Exposes HTTP endpoints that Kubernetes uses for liveness and readiness probes.

### Endpoints

| Endpoint | Kubernetes Probe | Purpose |
|----------|-----------------|---------|
| `/health/live` | Liveness | Is the process healthy? (restart if failing) |
| `/health/ready` | Readiness | Is the service ready for traffic? |
| `/health/started` | Startup | Has startup completed? |
| `/health` | — | All checks combined |

### Writing Health Checks

```java
@Liveness
@ApplicationScoped
public class ServiceLivenessCheck implements HealthCheck {
    @Override
    public HealthCheckResponse call() {
        // Check internal state (e.g., deadlock, OOM)
        boolean alive = checkInternalState();
        return HealthCheckResponse.named("service-alive")
            .status(alive)
            .withData("memoryUsedMB", getUsedMemoryMB())
            .build();
    }
}

@Readiness
@ApplicationScoped
public class DatabaseReadinessCheck implements HealthCheck {
    @Inject
    private DataSource ds;

    @Override
    public HealthCheckResponse call() {
        try (Connection c = ds.getConnection()) {
            c.isValid(1);
            return HealthCheckResponse.named("database-ready").up().build();
        } catch (SQLException e) {
            return HealthCheckResponse.named("database-ready").down()
                .withData("error", e.getMessage()).build();
        }
    }
}
```

### Response Format

```json
{
  "status": "UP",
  "checks": [
    { "name": "service-alive", "status": "UP", "data": { "memoryUsedMB": 128 } },
    { "name": "database-ready", "status": "UP" }
  ]
}
```

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 9080
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/ready
    port: 9080
  initialDelaySeconds: 20
  periodSeconds: 5
```

---

## MicroProfile Metrics 3.0

Exposes metrics at `/metrics`. Supports Prometheus format (default) and JSON.

### Metric Types

| Type | Description | Example |
|------|-------------|---------|
| `@Counted` | Monotonically increasing count | Total requests |
| `@Timed` | Duration statistics (mean, max, percentiles) | Request duration |
| `@Gauge` | Current value | Active sessions |
| `@Metered` | Rate of events | Requests per second |
| `@ConcurrentGauge` | Current concurrent invocations | Parallel DB queries |
| `@SimplyTimed` | Simplified timer (no percentiles) | Quick response time |

### Annotations

```java
@Path("/portfolios")
@ApplicationScoped
public class PortfolioResource {

    @GET
    @Counted(name = "portfolio.get.total",
             description = "Total portfolio GET requests",
             absolute = true)
    @Timed(name = "portfolio.get.time",
           description = "Portfolio GET response time",
           unit = MetricUnits.MILLISECONDS,
           absolute = true)
    public Portfolio getPortfolio(@PathParam("owner") String owner) { ... }

    @Gauge(name = "portfolio.active.count",
           unit = MetricUnits.NONE,
           description = "Number of active portfolios",
           absolute = true)
    public long getActivePortfolioCount() {
        return service.countActive();
    }
}
```

### Programmatic Registration

```java
@Inject
private MetricRegistry registry;

public void init() {
    Counter counter = registry.counter(
        Metadata.builder()
            .withName("portfolio.trade.count")
            .withDescription("Total trades executed")
            .build()
    );
    counter.inc();
}
```

### Metric Scopes

| Scope | Path | Contents |
|-------|------|---------|
| `base` | `/metrics/base` | JVM, thread, heap metrics (spec-mandated) |
| `vendor` | `/metrics/vendor` | Runtime-specific (Open Liberty) |
| `application` | `/metrics/application` | Your application metrics |

### Prometheus Output Example

```
# HELP portfolio_get_total_total Total portfolio GET requests
# TYPE portfolio_get_total_total counter
portfolio_get_total_total 42.0
# HELP portfolio_get_time_seconds Portfolio GET response time
portfolio_get_time_seconds_count 42.0
portfolio_get_time_seconds{quantile="0.5"} 0.012
portfolio_get_time_seconds{quantile="0.95"} 0.087
```

---

## MicroProfile OpenTracing 2.0

Distributed tracing using the OpenTracing API. Integrates with Jaeger, Zipkin, etc.

> Note: OpenTracing is superseded by OpenTelemetry in newer MicroProfile versions. MicroProfile Telemetry 1.0 aligns with OpenTelemetry.

### Automatic Instrumentation

All JAX-RS endpoints are automatically traced — no annotations required. Each inbound request creates a span. Outbound Rest Client calls propagate trace context via HTTP headers (B3 or W3C TraceContext).

### Manual Spans

```java
@Inject
private Tracer tracer;

public StockQuote getQuote(String symbol) {
    try (Scope scope = tracer.buildSpan("fetch-stock-price")
            .withTag("stock.symbol", symbol)
            .startActive(true)) {

        scope.span().log("Calling external stock API");
        StockQuote quote = client.fetchQuote(symbol);
        scope.span().setTag("quote.price", quote.getPrice());
        return quote;

    } catch (Exception e) {
        tracer.activeSpan().setTag(Tags.ERROR, true);
        tracer.activeSpan().log(Map.of(Fields.EVENT, "error",
                                       Fields.MESSAGE, e.getMessage()));
        throw e;
    }
}
```

### @Traced Annotation

```java
@Traced(operationName = "portfolio-valuation")
public double calculateValue(String owner) { ... }

// Disable tracing for a method
@Traced(value = false)
public String healthEndpoint() { ... }
```

### Jaeger Configuration (Open Liberty)

```properties
JAEGER_ENDPOINT=http://jaeger-collector:14268/api/traces
JAEGER_SERVICE_NAME=portfolio-service
JAEGER_SAMPLER_TYPE=const
JAEGER_SAMPLER_PARAM=1
```

```xml
<featureManager>
    <feature>mpOpenTracing-2.0</feature>
</featureManager>
```

### Trace Propagation Headers

The runtime automatically extracts incoming trace context from:
- B3 headers (`X-B3-TraceId`, `X-B3-SpanId`, `X-B3-Sampled`)
- W3C TraceContext (`traceparent`, `tracestate`)

And injects them into outbound Rest Client calls, creating a connected trace across services.
