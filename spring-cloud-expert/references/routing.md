---
name: routing
description: API gateway patterns, Zuul pre/route/post filters, dynamic routing, Spring Cloud Gateway predicates and filter chains, rate limiting at the gateway. Chapter 6 of Spring Microservices in Action.
type: reference
---

# Service Routing: Zuul and Spring Cloud Gateway

## Why an API Gateway?

Without a gateway, clients must know every service's location. Gateways provide:
- **Single entry point** — one DNS name for all clients
- **Cross-cutting enforcement** — auth, rate limiting, CORS in one place
- **Protocol translation** — HTTP/2 externally → HTTP/1.1 internally
- **Request aggregation** — combine multiple service responses (BFF pattern)
- **Dynamic routing** — route by path, header, or payload without redeployment

---

## Zuul (Netflix, Servlet-based)

Zuul 1.x ships with Spring Cloud Netflix and uses a blocking, servlet-based architecture. Suitable for most workloads; replaced by Spring Cloud Gateway for reactive/high-concurrency needs.

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-zuul</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

### Enable Zuul
```java
@SpringBootApplication
@EnableZuulProxy
public class GatewayApplication { ... }
```

`@EnableZuulProxy` also enables Eureka client and Ribbon — Zuul auto-discovers services.

### Auto-routing via Eureka
With Eureka on the classpath, Zuul routes `/organization-service/**` to any registered instance of `organization-service` automatically. No explicit route config needed.

```
Client: GET /organization-service/v1/organizations/1234
Zuul: → resolves organization-service in Eureka → forwards to instance
```

### Explicit Route Configuration
```yaml
zuul:
  ignored-services: '*'          # Disable auto-routes; use explicit only
  prefix: /api                   # Prepend /api to all routes
  routes:
    organization-service:
      path: /organization/**
      serviceId: organization-service   # Eureka service name
      strip-prefix: true                # Remove /organization from forwarded path
    license-service:
      path: /license/**
      url: http://license-service:8080  # Direct URL (bypasses Eureka)
```

---

## Zuul Filter Types

Filters are the core extension point. Each request passes through all filters in sequence.

```
Request → [PRE filters] → [ROUTING filter] → Service
                                              ↓
Response ← [POST filters] ← [ERROR filter] ←─┘
```

| Type | Runs | Use for |
|------|------|---------|
| **pre** | Before routing | Auth, request logging, correlation IDs, header injection |
| **routing** | Performs the forward | Custom routing logic (rarely overridden) |
| **post** | After response received | Response logging, header addition, CORS headers |
| **error** | On any exception | Unified error response formatting |

### Writing a Pre-filter (Correlation ID)

```java
@Component
public class TrackingFilter extends ZuulFilter {

    private static final Logger logger = LoggerFactory.getLogger(TrackingFilter.class);
    private static final String CORRELATION_ID = "tmx-correlation-id";

    @Override
    public String filterType() { return "pre"; }

    @Override
    public int filterOrder() { return 1; }

    @Override
    public boolean shouldFilter() { return true; }

    @Override
    public Object run() {
        HttpServletRequest request =
            RequestContext.getCurrentContext().getRequest();

        if (request.getHeader(CORRELATION_ID) == null) {
            String correlationId = UUID.randomUUID().toString();
            RequestContext.getCurrentContext()
                .addZuulRequestHeader(CORRELATION_ID, correlationId);
            logger.debug("Generating correlation ID: {}", correlationId);
        }
        return null;
    }
}
```

### Writing a Post-filter (Response Header)

```java
@Component
public class ResponseFilter extends ZuulFilter {

    @Override
    public String filterType() { return "post"; }

    @Override
    public int filterOrder() { return 1; }

    @Override
    public boolean shouldFilter() { return true; }

    @Override
    public Object run() {
        RequestContext ctx = RequestContext.getCurrentContext();
        String correlationId = ctx.getRequest().getHeader("tmx-correlation-id");
        ctx.getResponse().addHeader("tmx-correlation-id", correlationId);
        return null;
    }
}
```

---

## Spring Cloud Gateway (Reactive, Modern)

Spring Cloud Gateway is built on Spring WebFlux and Project Reactor. It replaces Zuul for new projects requiring non-blocking I/O.

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

**Note:** Spring Cloud Gateway uses WebFlux. Do **not** add `spring-boot-starter-web` (Tomcat) — they conflict.

### Route Configuration (YAML)

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: organization-service
          uri: lb://organization-service    # lb:// = Eureka service name
          predicates:
            - Path=/organization/**
          filters:
            - StripPrefix=1                 # Remove first path segment

        - id: license-service
          uri: lb://license-service
          predicates:
            - Path=/license/**
            - Header=X-Api-Version, v2     # Only match v2 header
          filters:
            - AddRequestHeader=X-Request-Source, gateway
            - AddResponseHeader=X-Gateway-Version, 1.0
```

### Built-in Predicates
| Predicate | Matches on |
|-----------|-----------|
| `Path=/foo/**` | URL path pattern |
| `Method=GET,POST` | HTTP method |
| `Header=name, value` | Request header regex |
| `Query=param, value` | Query parameter regex |
| `Host=**.example.com` | Host header pattern |
| `Before=datetime` | Before a point in time |
| `After=datetime` | After a point in time |
| `Weight=group, 8` | Weighted routing (A/B, canary) |

### Built-in Filters
| Filter | Effect |
|--------|--------|
| `StripPrefix=N` | Remove N path segments |
| `AddRequestHeader=K, V` | Add header to upstream request |
| `AddResponseHeader=K, V` | Add header to client response |
| `SetStatus=404` | Override response status |
| `RewritePath=/old, /new` | Regex rewrite |
| `RequestRateLimiter` | Token bucket rate limiting |
| `CircuitBreaker` | Resilience4j circuit breaker |

### Custom Global Filter

```java
@Component
public class TrackingFilter implements GlobalFilter, Ordered {

    private static final String CORRELATION_ID = "tmx-correlation-id";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();

        if (!request.getHeaders().containsKey(CORRELATION_ID)) {
            String correlationId = UUID.randomUUID().toString();
            request = request.mutate()
                .header(CORRELATION_ID, correlationId)
                .build();
            exchange = exchange.mutate().request(request).build();
        }
        return chain.filter(exchange);
    }

    @Override
    public int getOrder() { return -1; }  // Run before all other filters
}
```

### Rate Limiting with Redis

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis-reactive</artifactId>
</dependency>
```

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: license-service
          uri: lb://license-service
          predicates:
            - Path=/license/**
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10   # tokens/sec
                redis-rate-limiter.burstCapacity: 20   # max burst
                key-resolver: "#{@userKeyResolver}"    # SpEL bean ref
```

```java
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest().getRemoteAddress().getAddress().getHostAddress()
    );
}
```

---

## Zuul vs. Spring Cloud Gateway

| Aspect | Zuul 1.x | Spring Cloud Gateway |
|--------|----------|----------------------|
| I/O model | Blocking (servlet) | Non-blocking (WebFlux) |
| Throughput | Moderate | Higher under load |
| Filter model | `ZuulFilter` classes | `GatewayFilter` / `GlobalFilter` |
| Route config | Java + YAML | YAML or Java DSL |
| Circuit breaker | Hystrix | Resilience4j |
| Actuator integration | `/routes` endpoint | `/actuator/gateway/routes` |
| Spring Boot 3 | Not supported | Supported |

**Recommendation:** Use Spring Cloud Gateway for new projects. Use Zuul only when maintaining pre-2020 applications.

---

## Gateway Actuator Endpoints (Spring Cloud Gateway)

```
GET  /actuator/gateway/routes           # All configured routes
GET  /actuator/gateway/routes/{id}      # Single route details
POST /actuator/gateway/refresh          # Reload route definitions
GET  /actuator/gateway/globalfilters    # All global filters with order
GET  /actuator/gateway/routefilters     # Available route filter factories
```

Enable in `application.yml`:
```yaml
management:
  endpoint:
    gateway:
      enabled: true
```
