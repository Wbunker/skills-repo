# Spring Boot in Production

Chapter 9 of *Spring Boot Up & Running* — Actuator deep dive, custom health indicators, Micrometer metrics, Prometheus, distributed tracing, log correlation.

---

## Actuator in Production

Expose only what is safe externally; run full actuator on a separate internal port:

```properties
# Application on 8080, actuator management on 8081 (internal network only)
server.port=8080
management.server.port=8081

# Expose only safe endpoints on 8081
management.endpoints.web.exposure.include=health,info,metrics,prometheus,loggers

# Health endpoint behavior
management.endpoint.health.show-details=when-authorized
management.endpoint.health.roles=ACTUATOR_ADMIN
```

---

## Liveness vs. Readiness Probes

Spring Boot 2.3+ exposes distinct probes for Kubernetes:

| Probe | Path | Meaning |
|-------|------|---------|
| Liveness | `/actuator/health/liveness` | App is alive; if DOWN, kill and restart the pod |
| Readiness | `/actuator/health/readiness` | App is ready to receive traffic; if DOWN, remove from load balancer |

```properties
management.endpoint.health.probes.enabled=true
management.health.livenessstate.enabled=true
management.health.readinessstate.enabled=true
```

Manually change readiness (e.g., during warm-up):
```java
@Autowired
private ApplicationEventPublisher publisher;

public void markNotReady() {
    publisher.publishEvent(new AvailabilityChangeEvent<>(this, ReadinessState.REFUSING_TRAFFIC));
}
public void markReady() {
    publisher.publishEvent(new AvailabilityChangeEvent<>(this, ReadinessState.ACCEPTING_TRAFFIC));
}
```

---

## Micrometer Metrics

Spring Boot auto-configures Micrometer, a vendor-neutral metrics facade. JVM, Tomcat, Spring MVC, datasource, and cache metrics are collected automatically.

### Viewing Metrics

```bash
# List all available metrics
GET /actuator/metrics

# Get a specific metric
GET /actuator/metrics/http.server.requests

# Filter by tags
GET /actuator/metrics/http.server.requests?tag=uri:/api/coffees&tag=status:200
```

### Custom Metrics

```java
@Service
public class CoffeeService {

    private final Counter ordersCreated;
    private final Timer orderProcessingTime;
    private final Gauge inventoryGauge;

    public CoffeeService(MeterRegistry registry, CoffeeRepository repo) {
        this.ordersCreated = Counter.builder("coffee.orders.created")
                .description("Total coffee orders created")
                .tag("region", "us-east")
                .register(registry);

        this.orderProcessingTime = Timer.builder("coffee.order.processing.time")
                .description("Time to process a coffee order")
                .register(registry);

        // Gauge automatically tracks the current value
        Gauge.builder("coffee.inventory.count", repo, CoffeeRepository::count)
                .description("Current coffee inventory count")
                .register(registry);
    }

    public Coffee createOrder(Coffee coffee) {
        return orderProcessingTime.record(() -> {
            Coffee saved = repository.save(coffee);
            ordersCreated.increment();
            return saved;
        });
    }
}
```

Common metric types:
- **Counter** — monotonically increasing count (requests, errors, events)
- **Gauge** — current value that goes up and down (queue depth, memory)
- **Timer** — latency + count + throughput
- **DistributionSummary** — like Timer but for non-time values (payload sizes)

---

## Prometheus Integration

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

Expose the Prometheus scrape endpoint:
```properties
management.endpoints.web.exposure.include=prometheus,health,info
```

Metrics are available at `GET /actuator/prometheus` in Prometheus text format.

Prometheus scrape config:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'spring-boot-app'
    static_configs:
      - targets: ['myapp:8080']
    metrics_path: '/actuator/prometheus'
    scrape_interval: 15s
```

---

## Distributed Tracing

### Spring Boot 3.x (Micrometer Tracing)

Spring Boot 3 uses Micrometer Tracing (replaces Spring Cloud Sleuth):

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```properties
management.tracing.sampling.probability=1.0   # 100% sampling (dev)
management.tracing.sampling.probability=0.1   # 10% sampling (prod)
management.zipkin.tracing.endpoint=http://zipkin:9411/api/v2/spans
```

### Spring Boot 2.x (Spring Cloud Sleuth)

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

---

## Log Correlation

With tracing enabled, Spring Boot injects `traceId` and `spanId` into MDC automatically. Configure your log pattern to include them:

```properties
# application.properties
logging.pattern.console=%d{HH:mm:ss} %-5level [%X{traceId:-},%X{spanId:-}] %logger{36} - %msg%n
```

This makes it trivial to find all logs for a single request across multiple services in your log aggregator (ELK stack, Grafana Loki, etc.).

---

## Custom Actuator Endpoints

```java
@Component
@Endpoint(id = "coffee-stats")
public class CoffeeStatsEndpoint {

    private final CoffeeRepository repo;

    @ReadOperation
    public Map<String, Object> stats() {
        return Map.of(
            "totalCoffees", repo.count(),
            "timestamp", Instant.now()
        );
    }

    @ReadOperation
    public Map<String, Object> statsByOrigin(@Selector String origin) {
        return Map.of("origin", origin, "count", repo.countByOrigin(origin));
    }

    @WriteOperation
    public void resetStats() {
        // POST /actuator/coffee-stats
    }
}
```

Access at: `GET /actuator/coffee-stats`

---

## JVM Tuning for Containers

The Spring Boot Maven/Gradle plugin with Buildpacks includes a **memory calculator** that sets JVM flags automatically based on container memory limits. For manual tuning:

```bash
# Set heap to 75% of container memory limit; leave room for non-heap
java -XX:MaxRAMPercentage=75.0 -jar myapp.jar

# Useful flags for containerized JVMs
java \
  -XX:MaxRAMPercentage=75.0 \
  -XX:InitialRAMPercentage=50.0 \
  -XX:+UseContainerSupport \
  -XX:+ExitOnOutOfMemoryError \
  -jar myapp.jar
```

**Spring Boot 3.2 + Virtual Threads (Project Loom)**:
```properties
spring.threads.virtual.enabled=true
```
This switches Tomcat's request handling to virtual threads — handles high concurrency without reactive programming.

---

## Key Production Checklist

```
Before deploying to production:
├── [ ] spring.jpa.hibernate.ddl-auto=validate (not create/update)
├── [ ] Secrets externalized (not in application.properties)
├── [ ] spring.datasource.password via env var or secrets manager
├── [ ] Actuator on internal port only (management.server.port)
├── [ ] health, readiness, liveness probes configured
├── [ ] Micrometer + Prometheus metrics exposed
├── [ ] Distributed tracing configured (sampling ≤ 10% in prod)
├── [ ] Graceful shutdown enabled (server.shutdown=graceful)
├── [ ] HTTPS only (spring.security.require-ssl=true or load balancer)
├── [ ] CSRF enabled for browser-facing endpoints
├── [ ] Meaningful info.app.* properties set
└── [ ] Memory limits set and JVM -XX:MaxRAMPercentage configured
```
