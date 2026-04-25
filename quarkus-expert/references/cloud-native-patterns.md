# Cloud-Native Application Patterns
## Chapter 10: Health, Metrics, Tracing, Fault Tolerance, Service Discovery

---

## Health Checks — SmallRye Health

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-health</artifactId>
</dependency>
```

### Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /q/health` | Combined liveness + readiness |
| `GET /q/health/live` | Liveness only (is the app alive?) |
| `GET /q/health/ready` | Readiness only (can it serve traffic?) |
| `GET /q/health/started` | Startup probe |

### Built-In Health Checks

Quarkus extensions register health checks automatically:
- Database connectivity (Hibernate, JDBC)
- Kafka broker reachability
- RabbitMQ connection
- Redis connection
- Keycloak reachability

### Custom Health Checks

```java
@Liveness
@ApplicationScoped
public class MyLivenessCheck implements HealthCheck {

    @Override
    public HealthCheckResponse call() {
        if (applicationAlive()) {
            return HealthCheckResponse.up("my-service");
        }
        return HealthCheckResponse.down("my-service");
    }
}

@Readiness
@ApplicationScoped
public class DatabaseReadinessCheck implements HealthCheck {

    @Inject
    DataSource dataSource;

    @Override
    public HealthCheckResponse call() {
        try (Connection c = dataSource.getConnection()) {
            c.createStatement().execute("SELECT 1");
            return HealthCheckResponse.builder()
                .name("database")
                .up()
                .withData("database", "PostgreSQL")
                .build();
        } catch (SQLException e) {
            return HealthCheckResponse.builder()
                .name("database")
                .down()
                .withData("error", e.getMessage())
                .build();
        }
    }
}
```

### Health Response Format

```json
{
  "status": "UP",
  "checks": [
    { "name": "database", "status": "UP", "data": {"database": "PostgreSQL"} },
    { "name": "kafka", "status": "UP" }
  ]
}
```

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /q/health/live
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /q/health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Metrics — Micrometer

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-micrometer-registry-prometheus</artifactId>
</dependency>
```

### Metrics Endpoint

```
GET /q/metrics      → Prometheus text format
```

### Built-In Metrics

JVM, GC, thread pool, HTTP request duration/counts, Hibernate stats, Kafka consumer/producer lag — all registered automatically.

### Custom Metrics

```java
@ApplicationScoped
public class OrderService {

    @Inject
    MeterRegistry registry;

    private final Counter orderCounter;
    private final Timer orderTimer;

    @PostConstruct
    void init() {
        orderCounter = registry.counter("orders.placed.total",
            "status", "success");
        orderTimer = registry.timer("orders.processing.duration");
    }

    public Order placeOrder(Cart cart) {
        return orderTimer.record(() -> {
            Order order = doPlaceOrder(cart);
            orderCounter.increment();
            return order;
        });
    }
}
```

### Annotation-Driven Metrics

```java
@Timed(value = "order.processing", description = "Time to process an order")
@Counted(value = "orders.total", description = "Total orders processed")
public Order placeOrder(Cart cart) { ... }

@Gauge(name = "queue.depth", description = "Number of pending orders")
public long pendingOrders() {
    return orderQueue.size();
}
```

### Gauge for Custom State

```java
Gauge.builder("queue.size", orderQueue, Queue::size)
    .tag("type", "order")
    .register(registry);
```

---

## Distributed Tracing — OpenTelemetry

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-opentelemetry</artifactId>
</dependency>
```

```properties
quarkus.otel.exporter.otlp.traces.endpoint=http://jaeger:4317
quarkus.otel.service.name=order-service
quarkus.otel.traces.sampler=parentbased_always_on
```

### Automatic Instrumentation

HTTP requests, gRPC calls, JDBC queries, Kafka produce/consume, REST client calls — all traced automatically with span creation and propagation.

### Custom Spans

```java
@ApplicationScoped
public class OrderService {

    @Inject
    Tracer tracer;

    public Order placeOrder(Cart cart) {
        Span span = tracer.spanBuilder("place-order")
            .setAttribute("cart.size", cart.items.size())
            .setAttribute("customer.id", cart.customerId)
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            Order order = doPlaceOrder(cart);
            span.setAttribute("order.id", order.id.toString());
            return order;
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### `@WithSpan` Annotation

```java
@WithSpan("validate-inventory")
public boolean checkInventory(@SpanAttribute("product.id") String productId, int qty) {
    return inventoryService.available(productId, qty);
}
```

---

## Fault Tolerance — SmallRye Fault Tolerance

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-fault-tolerance</artifactId>
</dependency>
```

### @Retry

```java
@Retry(maxRetries = 3,
       delay = 200, delayUnit = ChronoUnit.MILLIS,
       retryOn = {IOException.class, TimeoutException.class},
       abortOn = AuthenticationException.class)
public Order callExternalApi(String orderId) {
    return client.getOrder(orderId);
}
```

### @Timeout

```java
@Timeout(value = 5, unit = ChronoUnit.SECONDS)
public List<Product> fetchCatalog() {
    return catalogService.getAll();    // throws TimeoutException if > 5s
}
```

### @Fallback

```java
@Fallback(fallbackMethod = "fallbackCatalog")
@Timeout(value = 2, unit = ChronoUnit.SECONDS)
public List<Product> fetchCatalog() {
    return catalogService.getAll();
}

private List<Product> fallbackCatalog() {
    return cachedCatalog;              // return stale cache on failure
}

// Or use FallbackHandler
@Fallback(FallbackCatalogHandler.class)
public List<Product> fetchCatalog() { ... }
```

### @CircuitBreaker

```java
@CircuitBreaker(
    requestVolumeThreshold = 20,   // minimum requests before tripping
    failureRatio = 0.5,            // 50% failure rate trips the breaker
    delay = 10, delayUnit = ChronoUnit.SECONDS,  // how long to stay open
    successThreshold = 5           // successes in half-open before closing
)
public Order chargePayment(PaymentRequest req) {
    return paymentGateway.charge(req);
}
```

### @Bulkhead

```java
@Bulkhead(
    value = 10,          // max concurrent executions
    waitingTaskQueue = 5 // queue up to 5 waiting calls
)
public Report generateReport(ReportRequest req) {
    return reportEngine.generate(req);
}
```

### Combining Annotations

```java
@Retry(maxRetries = 3)
@CircuitBreaker(requestVolumeThreshold = 10, failureRatio = 0.5)
@Fallback(fallbackMethod = "fallback")
@Timeout(value = 2, unit = ChronoUnit.SECONDS)
public String callService() { ... }

// Execution order: Fallback > Retry > CircuitBreaker > Timeout > method
```

---

## Service Discovery

### Kubernetes DNS (Default)

In Kubernetes, services are resolved by DNS:
```properties
quarkus.rest-client.inventory-api.url=http://inventory-service:8080
```

`inventory-service` resolves via kube-dns to the ClusterIP.

### SmallRye Stork (Client-Side Load Balancing)

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-stork</artifactId>
</dependency>
<dependency>
    <groupId>io.smallrye.stork</groupId>
    <artifactId>stork-service-discovery-consul</artifactId>
</dependency>
```

```properties
# Use stork:// protocol in REST client URL
quarkus.rest-client.inventory-api.url=stork://inventory-service

# Configure service discovery
stork.inventory-service.service-discovery.type=consul
stork.inventory-service.service-discovery.consul-host=localhost
stork.inventory-service.service-discovery.consul-port=8500

# Load balancing strategy
stork.inventory-service.load-balancer.type=round-robin
```

### Kubernetes Service Discovery with Stork

```xml
<dependency>
    <groupId>io.smallrye.stork</groupId>
    <artifactId>stork-service-discovery-kubernetes</artifactId>
</dependency>
```

```properties
stork.inventory-service.service-discovery.type=kubernetes
stork.inventory-service.service-discovery.k8s-namespace=production
```
