---
name: resiliency
description: Client resiliency patterns, Netflix Hystrix @HystrixCommand, circuit breaker states, thread pool and semaphore isolation, fallback methods, bulkheads, and Resilience4j equivalents. Chapter 5 of Spring Microservices in Action.
type: reference
---

# Client Resiliency Patterns

## Why Client Resiliency?

In microservice architectures, service calls cross the network. Networks fail, downstream services slow down, and cascading failures can take down entire systems. Client resiliency patterns protect callers from these failures.

### The Four Client Resiliency Patterns (Carnell)
1. **Client-side load balancing** — don't call a known-bad instance (Ribbon)
2. **Circuit breaker** — stop calling a failing service; fail fast
3. **Fallback** — return a sensible default when the real call fails
4. **Bulkhead** — isolate thread pools so one slow service can't exhaust all threads

---

## Circuit Breaker States

```
        [CLOSED] ──────────────────────────────────────────────┐
           │  Normal operation; calls pass through             │
           │  Failure counter increments on errors             │
           │                                                   │
           ▼ (failure threshold exceeded)                      │
        [OPEN] ─────────────────────────────────────────────► │
           │  All calls fail immediately (fallback)            │
           │  Timer starts                                     │
           │                                                   │
           ▼ (timer expires)                                   │
        [HALF-OPEN]                                            │
           │  Single probe call allowed                        │
           ├─ success ──────────────────────────────────────► CLOSED
           └─ failure ──────────────────────────────────────► OPEN
```

---

## Netflix Hystrix

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-hystrix</artifactId>
</dependency>
```

### Enable Hystrix
```java
@SpringBootApplication
@EnableCircuitBreaker
public class LicenseServiceApplication { ... }
```

### Basic Circuit Breaker

```java
@HystrixCommand
public Organization getOrganization(String organizationId) {
    return restTemplate.getForObject(
        "http://organization-service/v1/organizations/{orgId}",
        Organization.class, organizationId);
}
```

Any exception thrown by the method trips the breaker. After threshold, calls fail immediately.

### Fallback Method

```java
@HystrixCommand(fallbackMethod = "buildFallbackOrganization")
public Organization getOrganization(String organizationId) {
    return restTemplate.getForObject(
        "http://organization-service/v1/organizations/{orgId}",
        Organization.class, organizationId);
}

private Organization buildFallbackOrganization(String organizationId) {
    Organization org = new Organization();
    org.setId(organizationId);
    org.setName("Sorry, no information currently available");
    return org;
}
```

The fallback method **must have the same signature** as the protected method (same params and return type).

### Configuring Circuit Breaker Parameters

```java
@HystrixCommand(
    fallbackMethod = "buildFallbackOrganization",
    commandProperties = {
        @HystrixProperty(name = "execution.isolation.thread.timeoutInMilliseconds",
                         value = "3000"),
        @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold",
                         value = "10"),          // Min calls before evaluating
        @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage",
                         value = "75"),          // % failures to open
        @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds",
                         value = "7000"),        // Time in OPEN before HALF-OPEN
        @HystrixProperty(name = "metrics.rollingStats.timeInMilliseconds",
                         value = "15000")        // Rolling window
    }
)
public Organization getOrganization(String organizationId) { ... }
```

### Thread Pool Isolation (Bulkhead)

Each `@HystrixCommand` group runs in a dedicated thread pool by default. This prevents a slow `organization-service` from consuming all threads and blocking calls to `license-service`.

```java
@HystrixCommand(
    fallbackMethod = "buildFallbackOrganization",
    threadPoolKey = "organizationByIdThreadPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "30"),
        @HystrixProperty(name = "maxQueueSize", value = "10")
    }
)
public Organization getOrganization(String organizationId) { ... }
```

### Semaphore Isolation
Use when Hystrix is called from code that is already async (e.g., reactive). Limits concurrent calls without separate threads.

```java
@HystrixCommand(
    commandProperties = {
        @HystrixProperty(
            name = "execution.isolation.strategy",
            value = "SEMAPHORE")
    }
)
```

### Hystrix Dashboard
Add `spring-cloud-starter-netflix-hystrix-dashboard`. Streams metrics via SSE at `/actuator/hystrix.stream`. Turbine aggregates streams from multiple instances.

---

## Resilience4j (Modern Replacement)

Netflix Hystrix entered maintenance mode in 2018. Spring Cloud 2020+ recommends Resilience4j.

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-resilience4j</artifactId>
</dependency>
<!-- For AOP-based annotations: -->
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot2</artifactId>
</dependency>
```

### Circuit Breaker

```java
@CircuitBreaker(name = "organizationService",
                fallbackMethod = "buildFallbackOrganization")
public Organization getOrganization(String organizationId) {
    return restTemplate.getForObject(...);
}

private Organization buildFallbackOrganization(String organizationId, Throwable t) {
    // fallback logic
}
```

**`application.yml` configuration:**
```yaml
resilience4j:
  circuitbreaker:
    instances:
      organizationService:
        sliding-window-size: 10
        failure-rate-threshold: 50       # % failures to open
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
```

### Retry

```java
@Retry(name = "retryOrganizationService",
       fallbackMethod = "buildFallbackOrganization")
public Organization getOrganization(String organizationId) { ... }
```

```yaml
resilience4j:
  retry:
    instances:
      retryOrganizationService:
        max-attempts: 3
        wait-duration: 1s
        retry-exceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
```

### Bulkhead (Thread Pool)

```java
@Bulkhead(name = "organizationService",
          type = Bulkhead.Type.THREADPOOL)
public CompletableFuture<Organization> getOrganization(String organizationId) {
    // must be async for THREADPOOL type
}
```

```yaml
resilience4j:
  thread-pool-bulkhead:
    instances:
      organizationService:
        max-thread-pool-size: 10
        core-thread-pool-size: 5
        queue-capacity: 25
```

### Rate Limiter

```java
@RateLimiter(name = "organizationService")
public Organization getOrganization(String organizationId) { ... }
```

```yaml
resilience4j:
  ratelimiter:
    instances:
      organizationService:
        limit-for-period: 100
        limit-refresh-period: 1s
        timeout-duration: 500ms
```

### Combining Annotations (Order Matters)

```java
@CircuitBreaker(name = "org", fallbackMethod = "fallback")
@Retry(name = "org")
@RateLimiter(name = "org")
public Organization getOrganization(String organizationId) { ... }
```

Outer wrapper executes first. Recommended order: `RateLimiter → CircuitBreaker → Retry → Bulkhead`.

---

## Hystrix vs. Resilience4j Comparison

| Feature | Hystrix | Resilience4j |
|---------|---------|-------------|
| Circuit breaker | Yes | Yes |
| Fallback | Yes | Yes |
| Timeout | Yes | Via `TimeLimiter` |
| Bulkhead | Thread pool + semaphore | Thread pool + semaphore |
| Retry | No (use Spring Retry) | Yes |
| Rate limiter | No | Yes |
| Reactive support | Limited | First-class |
| Maintenance status | End-of-life | Active |

---

## Best Practices

- **Always provide a fallback** — even if it returns empty/stale data; fail-open is better than no data
- **Size thread pools carefully** — too small causes unnecessary failures; too large wastes resources
- **Monitor circuit state** — add Micrometer metrics; alert when a breaker opens
- **Don't wrap everything** — only wrap calls that cross a network boundary
- **Log fallback invocations** — treat them as degraded-mode indicators, not silent successes
- **Test circuit opening** — write integration tests that verify fallback behavior
