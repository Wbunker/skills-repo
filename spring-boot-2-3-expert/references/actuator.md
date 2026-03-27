# Spring Boot 2.3 — Actuator

## Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

---

## Built-in Endpoints

| ID | Description | Default HTTP exposed |
|----|-------------|---------------------|
| `health` | Application health status | Yes |
| `info` | Application info | Yes |
| `metrics` | Micrometer metrics | No |
| `env` | All environment properties | No |
| `loggers` | View/set log levels | No |
| `beans` | All Spring beans | No |
| `conditions` | Auto-configuration conditions | No |
| `configprops` | `@ConfigurationProperties` values | No |
| `mappings` | Request mappings | No |
| `httptrace` | Last 100 HTTP exchanges | No |
| `scheduledtasks` | Scheduled tasks | No |
| `auditevents` | Audit events | No |
| `flyway` | Flyway migration info | No |
| `liquibase` | Liquibase migration info | No |
| `sessions` | Spring Session (if in use) | No |
| `shutdown` | Graceful shutdown trigger | No (disabled by default) |
| `threaddump` | Thread dump | No |
| `heapdump` | Heap dump file | No (web only) |
| `prometheus` | Metrics in Prometheus format | No (web only) |

---

## Exposing Endpoints

```properties
# Expose specific endpoints over HTTP
management.endpoints.web.exposure.include=health,info,metrics,loggers

# Expose ALL endpoints
management.endpoints.web.exposure.include=*

# Expose all but exclude sensitive ones
management.endpoints.web.exposure.include=*
management.endpoints.web.exposure.exclude=env,beans,threaddump,heapdump

# Enable shutdown endpoint (disabled by default)
management.endpoint.shutdown.enabled=true

# Disable all by default, opt-in
management.endpoints.enabled-by-default=false
management.endpoint.health.enabled=true
management.endpoint.info.enabled=true
```

**YAML note**: `*` must be quoted in YAML:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

---

## Actuator Base Path and Port

```properties
# Change base path (default: /actuator)
management.endpoints.web.base-path=/manage

# Run actuator on a separate port (for firewall isolation)
management.server.port=8081
management.server.address=127.0.0.1

# Disable HTTP management entirely
management.server.port=-1
```

---

## Health Endpoint

```properties
management.endpoint.health.show-details=always
# Options: never (default), when-authorized, always

management.endpoint.health.show-components=true

# Required roles for when-authorized
management.endpoint.health.roles=ADMIN
```

Response:
```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP", "details": { "database": "PostgreSQL", "validationQuery": "isValid()" } },
    "diskSpace": { "status": "UP", "details": { "total": 499963174912, "free": 91248713728 } },
    "ping": { "status": "UP" }
  }
}
```

---

## Custom Health Indicator

```java
@Component
public class ExternalServiceHealthIndicator implements HealthIndicator {

    private final ExternalServiceClient client;

    public ExternalServiceHealthIndicator(ExternalServiceClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        try {
            boolean up = client.ping();
            if (up) {
                return Health.up()
                    .withDetail("responseTime", "45ms")
                    .build();
            } else {
                return Health.down()
                    .withDetail("reason", "Ping returned false")
                    .build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
// Exposed at /actuator/health/externalService
```

### Reactive Health Indicator (for WebFlux apps)

```java
@Component
public class ReactiveDbHealthIndicator implements ReactiveHealthIndicator {

    @Override
    public Mono<Health> health() {
        return checkDatabase()
            .map(latency -> Health.up()
                .withDetail("latency", latency + "ms").build())
            .onErrorResume(e -> Mono.just(
                Health.down().withException(e).build()));
    }

    private Mono<Long> checkDatabase() {
        long start = System.currentTimeMillis();
        return Mono.just(System.currentTimeMillis() - start);
    }
}
```

---

## Health Groups (Kubernetes Probes — New in 2.3)

```properties
# Kubernetes probes auto-enabled when running in K8s
management.endpoint.health.probes.enabled=true

# Endpoints:
# /actuator/health/liveness   → LivenessState
# /actuator/health/readiness  → ReadinessState

# Customize readiness group
management.endpoint.health.group.readiness.include=readinessState,db,redis

# Custom status HTTP mapping
management.endpoint.health.status.http-mapping.down=503
management.endpoint.health.status.http-mapping.out-of-service=503
```

Kubernetes deployment probe configuration:
```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

---

## Metrics (Micrometer)

Spring Boot auto-configures Micrometer with a composite `MeterRegistry`.

### Auto-collected metrics

- JVM: `jvm.memory.max`, `jvm.gc.pause`, `jvm.threads.live`
- CPU: `system.cpu.usage`, `process.cpu.usage`
- HTTP server: `http.server.requests` (count, sum, max by status, method, uri)
- HTTP client: `http.client.requests` (via RestTemplate/WebClient builder)
- DataSource: `hikaricp.connections.*`
- Logback: `logback.events` by level

### Prometheus export

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```properties
management.endpoints.web.exposure.include=prometheus
management.metrics.export.prometheus.enabled=true
```

Access: `GET /actuator/prometheus`

### Common tags (applied to all metrics)

```properties
management.metrics.tags.application=myapp
management.metrics.tags.environment=production
management.metrics.tags.region=us-east-1
```

Or programmatically:
```java
@Bean
MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
    return registry -> registry.config()
        .commonTags("application", "myapp", "region", "us-east-1");
}
```

### Custom metrics

```java
@Component
public class OrderMetrics {

    private final Counter orderCounter;
    private final Gauge pendingOrdersGauge;
    private final Timer orderProcessingTimer;

    public OrderMetrics(MeterRegistry registry, OrderRepository orderRepo) {
        this.orderCounter = Counter.builder("orders.created")
            .description("Total orders created")
            .tag("type", "online")
            .register(registry);

        this.pendingOrdersGauge = Gauge.builder("orders.pending",
                orderRepo, OrderRepository::countPending)
            .description("Current pending orders")
            .register(registry);

        this.orderProcessingTimer = Timer.builder("orders.processing.time")
            .description("Order processing duration")
            .register(registry);
    }

    public void recordOrderCreated() {
        orderCounter.increment();
    }

    public void recordProcessingTime(Duration duration) {
        orderProcessingTimer.record(duration);
    }
}

// MeterBinder approach (preferred for library code)
@Bean
MeterBinder queueSize(Queue queue) {
    return registry -> Gauge.builder("queue.size", queue::size)
        .description("Queue depth")
        .register(registry);
}
```

### @Timed annotation on controllers/services

```java
@RestController
@Timed           // times all methods in this controller
public class OrderController {

    @GetMapping("/api/orders")
    @Timed(value = "api.orders.list", description = "List orders",
           extraTags = {"endpoint", "list"})
    public List<Order> listOrders() { }
}
```

### Query metrics endpoint

```bash
GET /actuator/metrics                           # list all metric names
GET /actuator/metrics/jvm.memory.max            # specific metric
GET /actuator/metrics/http.server.requests?tag=status:200  # with tag filter
```

---

## Loggers Endpoint

```bash
# Get all loggers
GET /actuator/loggers

# Get specific logger
GET /actuator/loggers/com.example.service.UserService

# Dynamically change log level at runtime
POST /actuator/loggers/com.example.service.UserService
Content-Type: application/json
{"configuredLevel": "DEBUG"}

# Reset to default
POST /actuator/loggers/com.example.service.UserService
{"configuredLevel": null}
```

---

## Info Endpoint

```properties
# Static info
info.app.name=My Application
info.app.version=1.0.0
info.app.description=User Management Service

# Build info (requires spring-boot-maven-plugin buildInfo goal)
# exposes build.version, build.artifact, build.group, build.time
```

Maven build-info:
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>build-info</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

Custom info contributor:
```java
@Component
public class AppInfoContributor implements InfoContributor {

    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("app", Map.of(
            "name", "My App",
            "version", "1.0.0",
            "features", List.of("users", "orders")
        ));
    }
}
```

---

## Custom Endpoints

```java
@Endpoint(id = "cache")
@Component
public class CacheEndpoint {

    private final CacheManager cacheManager;

    public CacheEndpoint(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }

    @ReadOperation
    public Map<String, Object> cacheInfo() {
        Map<String, Object> info = new LinkedHashMap<>();
        for (String name : cacheManager.getCacheNames()) {
            Cache cache = cacheManager.getCache(name);
            info.put(name, Map.of("name", name));
        }
        return info;
    }

    @DeleteOperation
    public void evictAll() {
        cacheManager.getCacheNames()
            .forEach(name -> cacheManager.getCache(name).clear());
    }

    @WriteOperation
    public void evictCache(@Selector String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) cache.clear();
    }
}
// Available at: GET /actuator/cache, DELETE /actuator/cache, DELETE /actuator/cache/{cacheName}
```

---

## Endpoint Cache TTL

```properties
management.endpoint.beans.cache.time-to-live=10s
management.endpoint.conditions.cache.time-to-live=30s
```

---

## Actuator Security

```java
@Configuration
public class ActuatorSecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeRequests(requests -> requests
                .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                .requestMatchers(EndpointRequest.to("prometheus")).permitAll()
                .anyRequest().hasRole("ACTUATOR")
            )
            .httpBasic();
    }
}
```
