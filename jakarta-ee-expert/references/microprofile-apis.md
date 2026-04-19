# MicroProfile APIs — Cloud-Native Extensions

Source: *Pro Cloud-Native Java EE Apps* by Luqman Saeed & Ghazy Abdallah (Apress, 2022/2025), Chapters 7–11. Covers MicroProfile 6.x / 7.0 as used alongside Jakarta EE 10/11.

MicroProfile is a community spec that layers cloud-native capabilities **on top of** Jakarta EE (CDI + REST + JSON-B are shared). All APIs below are available on WildFly, Open Liberty, Payara, Quarkus, Helidon, and TomEE.

---

## MicroProfile Config (Ch 7)

Externalizes configuration so apps run unmodified across environments.

### Config Sources (priority order, highest first)

| Priority | Source | Example |
|----------|--------|---------|
| 500 | System properties | `-Dapp.name=foo` |
| 400 | Environment variables | `APP_NAME=foo` |
| 100 | `microprofile-config.properties` | in `META-INF/` |
| Custom | `ConfigSource` implementations | DB, Vault, Consul |

### Injection

```java
@Inject
@ConfigProperty(name = "app.timeout", defaultValue = "30")
private int timeout;

@Inject
@ConfigProperty(name = "greeting")
private Optional<String> greeting;  // absent when not set
```

### Programmatic Access

```java
Config config = ConfigProvider.getConfig();
int timeout = config.getValue("app.timeout", Integer.class);
Optional<String> val = config.getOptionalValue("key", String.class);
```

### Custom ConfigSource

```java
@ApplicationScoped
public class VaultConfigSource implements ConfigSource {
    @Override public Map<String, String> getProperties() { ... }
    @Override public String getValue(String key) { ... }
    @Override public String getName() { return "vault"; }
    @Override public int getOrdinal() { return 600; }
}
```
Register via `ServiceLoader`: `META-INF/services/org.eclipse.microprofile.config.spi.ConfigSource`.

### Environment Variable Name Mapping

`app.timeout` → env var `APP_TIMEOUT` (dots→underscores, uppercase). MicroProfile performs this mapping automatically.

---

## MicroProfile Fault Tolerance (Ch 8)

Annotation-driven resilience patterns. Apply to CDI beans or JAX-RS resource methods.

### @Retry

```java
@Retry(maxRetries = 3, delay = 200, delayUnit = ChronoUnit.MILLIS,
       retryOn = {IOException.class})
public String callExternalService() { ... }
```

| Attribute | Default | Notes |
|-----------|---------|-------|
| `maxRetries` | 3 | -1 = unlimited |
| `delay` | 0 | Wait between attempts |
| `jitter` | 200ms | Random variation |
| `retryOn` | `{Exception.class}` | Exceptions that trigger retry |
| `abortOn` | `{}` | Exceptions that stop retry |

### @Timeout

```java
@Timeout(value = 2, unit = ChronoUnit.SECONDS)
public String slowCall() { ... }
// Throws TimeoutException if exceeded
```

### @CircuitBreaker

```java
@CircuitBreaker(
    requestVolumeThreshold = 10,   // window size
    failureRatio = 0.5,            // 50% failure opens circuit
    delay = 5000,                  // ms in open state
    successThreshold = 2           // successes to close
)
public String riskyCall() { ... }
```

States: **Closed** (normal) → **Open** (fast-fail) → **Half-Open** (probing).

### @Bulkhead

```java
// Thread pool isolation
@Bulkhead(value = 5, waitingTaskQueue = 10)
public String limitedConcurrency() { ... }

// Semaphore (synchronous)
@Bulkhead(5)
public String semaphoreLimited() { ... }
```

### @Fallback

```java
@Fallback(fallbackMethod = "getFallbackData")
public String getPrimaryData() { ... }

private String getFallbackData() {
    return "cached-default";
}
```

Or use `FallbackHandler`:
```java
@Fallback(MyFallbackHandler.class)
```

### @Asynchronous

Executes method on a separate thread; return type must be `CompletionStage<T>` or `Future<T>`.

```java
@Asynchronous
@Retry(maxRetries = 2)
public CompletionStage<String> asyncCall() {
    return CompletableFuture.supplyAsync(() -> fetchData());
}
```

### Combining Annotations

Order of execution (outer → inner): `@Asynchronous` → `@Bulkhead` → `@CircuitBreaker` → `@Retry` → `@Timeout` → method → `@Fallback`.

---

## MicroProfile Metrics (Ch 9)

Exposes application metrics at `/metrics` (Prometheus format). Integrates with Prometheus + Grafana.

### Metric Types

| Annotation | Type | Description |
|-----------|------|-------------|
| `@Counted` | Counter | Monotonically increasing count |
| `@Timed` | Timer | Tracks duration + call rate |
| `@Metered` | Meter | Call rate (1/5/15 min) |
| `@Gauge` | Gauge | Current value (e.g., queue size) |
| `@ConcurrentGauge` | Gauge | Concurrent invocations |

### Annotation Usage

```java
@Counted(name = "orderCount", description = "Total orders placed",
         tags = {"type=online"})
public void placeOrder(Order order) { ... }

@Timed(name = "checkoutDuration", description = "Time to checkout")
public Receipt checkout(Cart cart) { ... }

@Gauge(name = "queueDepth", unit = MetricUnits.NONE)
public int getQueueDepth() { return queue.size(); }
```

### Programmatic Registration

```java
@Inject MetricRegistry registry;

Counter counter = registry.counter("custom.counter");
counter.inc();

Timer timer = registry.timer("custom.timer");
try (Timer.Context ctx = timer.time()) {
    doWork();
}
```

### Metric Scopes

- `/metrics/application` — your app metrics
- `/metrics/base` — JVM, GC, thread, heap (required by spec)
- `/metrics/vendor` — server-specific (optional)

### Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'jakarta-ee-app'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['app:8080']
```

---

## MicroProfile Health (Ch 10)

Exposes liveness and readiness probes for Kubernetes. Implements `/health`, `/health/live`, `/health/ready`, `/health/started`.

### HealthCheck Interface

```java
@ApplicationScoped
@Liveness
public class AppLivenessCheck implements HealthCheck {
    @Override
    public HealthCheckResponse call() {
        return HealthCheckResponse.named("app-live")
            .up()
            .withData("heap-used", Runtime.getRuntime().totalMemory())
            .build();
    }
}

@ApplicationScoped
@Readiness
public class DatabaseReadinessCheck implements HealthCheck {
    @Inject DataSource ds;

    @Override
    public HealthCheckResponse call() {
        try (Connection c = ds.getConnection()) {
            return HealthCheckResponse.named("db-ready").up().build();
        } catch (SQLException e) {
            return HealthCheckResponse.named("db-ready").down()
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
    { "name": "app-live", "status": "UP", "data": { "heap-used": 104857600 } },
    { "name": "db-ready", "status": "UP" }
  ]
}
```

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
```

### @Startup (MicroProfile Health 3.1+)

```java
@Startup
public class InitializationCheck implements HealthCheck {
    @Override public HealthCheckResponse call() {
        // Called once; pod stays pending until UP
        return initialized ? HealthCheckResponse.up("init") 
                           : HealthCheckResponse.down("init");
    }
}
```

---

## MicroProfile JWT Auth (Ch 11)

Propagates JWT Bearer tokens across microservices; maps JWT claims to Jakarta Security roles.

### Application Configuration

```java
@LoginConfig(authMethod = "MP-JWT", realmName = "jwt-realm")
@ApplicationPath("/api")
public class JwtApplication extends Application { }
```

`microprofile-config.properties`:
```properties
mp.jwt.verify.publickey.location=/META-INF/public.pem
mp.jwt.verify.issuer=https://auth.example.com
```

### Claim Injection

```java
@RequestScoped
public class OrderResource {

    @Inject @Claim("sub")
    private String subject;

    @Inject @Claim("groups")
    private Set<String> groups;

    @Inject @Claim(standard = Claims.iat)
    private Long issuedAt;

    @Inject
    private JsonWebToken jwt;  // full token

    @GET @RolesAllowed("admin")
    public Response adminOnly() {
        String upn = jwt.getName();  // preferred_username or sub
        return Response.ok(upn).build();
    }
}
```

### Standard JWT Claims

| Claim | Type | Description |
|-------|------|-------------|
| `iss` | String | Issuer (verified against config) |
| `sub` | String | Subject (user identifier) |
| `upn` | String | User principal name (MP-specific) |
| `groups` | Set<String> | Roles (mapped to `@RolesAllowed`) |
| `exp` | Long | Expiry (validated automatically) |
| `iat` | Long | Issued-at |

### Key Verification Options

```properties
# Option 1: inline PEM
mp.jwt.verify.publickey=MIIBIjANBgkq...

# Option 2: JWKS URL
mp.jwt.verify.publickey.location=https://auth.example.com/.well-known/jwks.json

# Option 3: local file
mp.jwt.verify.publickey.location=/META-INF/public.pem
```

### Token Generation (test / issuer side)

```java
// Using smallrye-jwt or nimbus-jose-jwt
PrivateKey pk = loadPrivateKey("private.pem");
String token = Jwt.issuer("https://auth.example.com")
    .subject("alice")
    .groups(Set.of("user", "admin"))
    .expiresIn(Duration.ofHours(1))
    .sign(pk);
```

### MicroProfile JWT + Microservice Propagation

Pass token in `Authorization: Bearer <token>` header. Use **MicroProfile REST Client** to propagate automatically:

```java
@RegisterRestClient
@RegisterClientHeaders  // propagates all incoming headers incl. Authorization
public interface InventoryClient {
    @GET @Path("/items/{id}")
    Item getItem(@PathParam("id") long id);
}
```
