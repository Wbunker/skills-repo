# Chapter 5: Enhancement APIs — Config, Fault Tolerance, OpenAPI, JWT

## MicroProfile Config 2.0

### Configuration Sources (priority order, highest wins)

| Source | Priority |
|--------|---------|
| System properties (`-D`) | 400 |
| Environment variables | 300 |
| `microprofile-config.properties` (classpath) | 100 |
| Custom `ConfigSource` | user-defined |

### Injection

```java
@Inject
@ConfigProperty(name = "stock.api.key")
private String apiKey;

// With default value
@Inject
@ConfigProperty(name = "loyalty.gold.threshold", defaultValue = "50000")
private double goldThreshold;

// Optional
@Inject
@ConfigProperty(name = "feature.flag.x")
private Optional<Boolean> featureX;

// Dynamic value (re-read on each call)
@Inject
@ConfigProperty(name = "stock.api.url")
private Provider<String> stockApiUrl;
```

### Programmatic Access

```java
Config config = ConfigProvider.getConfig();
String apiKey = config.getValue("stock.api.key", String.class);
Optional<Integer> timeout = config.getOptionalValue("http.timeout", Integer.class);
```

### Custom ConfigSource

```java
public class VaultConfigSource implements ConfigSource {
    @Override
    public Map<String, String> getProperties() {
        return vaultClient.readAll("secret/myapp");
    }
    @Override
    public String getValue(String propertyName) {
        return vaultClient.read("secret/myapp", propertyName);
    }
    @Override
    public String getName() { return "VaultConfigSource"; }
    @Override
    public int getOrdinal() { return 500; } // higher than system properties
}
```

Register in `META-INF/services/org.eclipse.microprofile.config.spi.ConfigSource`.

### Converters

```java
// Register custom type converter
public class DurationConverter implements Converter<Duration> {
    public Duration convert(String value) { return Duration.parse(value); }
}
```

---

## MicroProfile Fault Tolerance 3.0

All annotations are interceptor bindings — apply to CDI beans or JAX-RS resources.

### @Retry

```java
@Retry(maxRetries = 3, delay = 500, delayUnit = ChronoUnit.MILLIS,
       jitter = 200, retryOn = {IOException.class, TimeoutException.class})
public StockQuote getQuote(String symbol) {
    return client.fetchQuote(symbol);
}
```

### @Timeout

```java
@Timeout(value = 2, unit = ChronoUnit.SECONDS)
public StockQuote getQuote(String symbol) { ... }
```

### @CircuitBreaker

```java
@CircuitBreaker(
    requestVolumeThreshold = 10,   // minimum requests before evaluation
    failureRatio = 0.5,            // 50% failure rate opens the circuit
    delay = 5000,                  // ms to stay open before half-open
    successThreshold = 2           // successes needed to close from half-open
)
public StockQuote getQuote(String symbol) { ... }
```

Circuit states: **Closed** (normal) → **Open** (failing fast) → **Half-Open** (probing) → **Closed**.

### @Bulkhead

```java
// Thread pool isolation
@Bulkhead(value = 10, waitingTaskQueue = 10)
public StockQuote getQuote(String symbol) { ... }
```

### @Fallback

```java
@Fallback(fallbackMethod = "getCachedQuote")
@CircuitBreaker(...)
public StockQuote getQuote(String symbol) { ... }

private StockQuote getCachedQuote(String symbol) {
    return cache.get(symbol); // stale data is better than no data
}
```

### Combining Annotations (execution order)

Interceptor chain (outermost to innermost):
```
Fallback → CircuitBreaker → Retry → Timeout → Bulkhead → method
```

### Configuration Override (no code changes)

```properties
# Disable retry in production
com.example.StockQuoteService/getQuote/Retry/enabled=false
# Adjust timeout
com.example.StockQuoteService/getQuote/Timeout/value=5000
```

---

## MicroProfile OpenAPI 2.0

Generates OpenAPI v3 documentation. Accessible at `/openapi` (YAML) and `/openapi/ui` (Swagger UI with Open Liberty).

### Annotations

```java
@Path("/portfolios")
@Tag(name = "Portfolio", description = "Portfolio management operations")
public class PortfolioResource {

    @GET
    @Path("/{owner}")
    @Operation(summary = "Get a portfolio", description = "Returns the portfolio for the given owner")
    @APIResponse(responseCode = "200", description = "Portfolio found",
        content = @Content(schema = @Schema(implementation = Portfolio.class)))
    @APIResponse(responseCode = "404", description = "Portfolio not found")
    public Portfolio getPortfolio(
        @Parameter(description = "Portfolio owner name", required = true)
        @PathParam("owner") String owner) { ... }
}
```

### Schema Annotations on Model

```java
@Schema(description = "A stock portfolio")
public class Portfolio {
    @Schema(description = "Owner's name", example = "John Doe", required = true)
    private String owner;

    @Schema(description = "Total portfolio value in USD", example = "52341.50")
    private double totalValue;
}
```

### Static OpenAPI File

Place `openapi.yaml` or `openapi.json` in `META-INF/` to merge with generated output.

### Open Liberty Config

```xml
<mpOpenAPI>
    <info title="Stock Trader API" version="1.0" description="Portfolio management API"/>
</mpOpenAPI>
```

---

## MicroProfile JWT 1.2

### Enabling JWT on a Resource

```java
@Path("/portfolios")
@LoginConfig(authMethod = "MP-JWT", realmName = "stock-trader")
@ApplicationScoped
public class PortfolioResource {

    @Inject
    @Claim(standard = Claims.upn)
    private String username;               // upn = user principal name

    @Inject
    @Claim("groups")
    private Set<String> groups;

    @Inject
    private JsonWebToken jwt;              // full token access

    @GET
    @RolesAllowed("StockTrader")
    public Portfolio getPortfolio() {
        return service.find(username);
    }
}
```

### Required JWT Claims

| Claim | Description |
|-------|-------------|
| `iss` | Issuer — must match `mp.jwt.verify.issuer` |
| `sub` | Subject (user ID) |
| `upn` | User principal name (MicroProfile-specific) |
| `groups` | Set of role names |
| `exp` | Expiration time |
| `iat` | Issued at |

### Configuration

```properties
# Public key for verification (PEM or JWKS URL)
mp.jwt.verify.publickey.location=/META-INF/public.pem
mp.jwt.verify.issuer=https://myissuer.example.com
```

Or via JWKS endpoint:
```properties
mp.jwt.verify.publickey.location=https://myissuer.example.com/.well-known/jwks.json
```

### Token Propagation with Rest Client

```java
@RegisterRestClient
@RegisterProvider(JwtPropagationProvider.class)
public interface AccountClient { ... }

// Propagation via ClientHeadersFactory
public class JwtPropagationProvider implements ClientHeadersFactory {
    @Inject
    private JsonWebToken jwt;

    public MultivaluedMap<String, String> update(...) {
        headers.putSingle("Authorization", "Bearer " + jwt.getRawToken());
        return headers;
    }
}
```

### Open Liberty `server.xml` Feature

```xml
<featureManager>
    <feature>mpJwt-1.2</feature>
</featureManager>
```
