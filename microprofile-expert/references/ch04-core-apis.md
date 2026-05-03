# Chapter 4: Core MicroProfile APIs

## JAX-RS — RESTful Web Services

### Resource Class

```java
@Path("/portfolios")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@ApplicationScoped
public class PortfolioResource {

    @GET
    @Path("/{owner}")
    public Portfolio getPortfolio(@PathParam("owner") String owner) {
        return portfolioService.find(owner);
    }

    @POST
    @Path("/{owner}")
    public Response createPortfolio(@PathParam("owner") String owner) {
        portfolioService.create(owner);
        return Response.status(Response.Status.CREATED).build();
    }

    @DELETE
    @Path("/{owner}")
    public Response deletePortfolio(@PathParam("owner") String owner) {
        portfolioService.delete(owner);
        return Response.noContent().build();
    }
}
```

### Application Class

```java
@ApplicationPath("/api")
public class RestApplication extends Application {}
```

### Key Annotations

| Annotation | Purpose |
|-----------|---------|
| `@Path` | Maps URI path |
| `@GET`, `@POST`, `@PUT`, `@DELETE`, `@PATCH` | HTTP method binding |
| `@PathParam` | URI template variable |
| `@QueryParam` | Query string parameter |
| `@HeaderParam` | HTTP header injection |
| `@Produces` / `@Consumes` | Media type negotiation |
| `@Context` | Inject JAX-RS context objects (UriInfo, HttpHeaders) |

---

## CDI — Contexts and Dependency Injection

### Scopes

| Annotation | Lifetime |
|-----------|---------|
| `@ApplicationScoped` | One instance per application |
| `@RequestScoped` | One instance per HTTP request |
| `@SessionScoped` | One instance per HTTP session |
| `@Dependent` | Default; lifecycle follows the injecting bean |

### Injection

```java
@ApplicationScoped
public class PortfolioService {

    @Inject
    private StockQuoteClient stockQuoteClient;

    @Inject
    @ConfigProperty(name = "loyalty.threshold.gold")
    private double goldThreshold;
}
```

### CDI Events

```java
// Fire
@Inject
private Event<LoyaltyChangeEvent> loyaltyEvent;
loyaltyEvent.fire(new LoyaltyChangeEvent(owner, newTier));

// Observe
public void onLoyaltyChange(@Observes LoyaltyChangeEvent event) {
    notificationService.notify(event);
}
```

### Interceptors

```java
@InterceptorBinding
@Target({METHOD, TYPE})
@Retention(RUNTIME)
public @interface Logged {}

@Logged
@Interceptor
@Priority(Interceptor.Priority.APPLICATION)
public class LoggingInterceptor {
    @AroundInvoke
    public Object log(InvocationContext ctx) throws Exception {
        Logger.getLogger(ctx.getTarget().getClass().getName())
              .info("Calling: " + ctx.getMethod().getName());
        return ctx.proceed();
    }
}
```

---

## JSON-B — JSON Binding

### Basic Usage

```java
Jsonb jsonb = JsonbBuilder.create();

// Serialize
String json = jsonb.toJson(portfolio);

// Deserialize
Portfolio p = jsonb.fromJson(jsonString, Portfolio.class);
```

### Customization Annotations

```java
public class Portfolio {
    @JsonbProperty("owner_name")      // rename field in JSON
    private String ownerName;

    @JsonbTransient                    // exclude from JSON
    private String internalId;

    @JsonbDateFormat("yyyy-MM-dd")    // date format
    private LocalDate createdDate;

    @JsonbNumberFormat("#,##0.00")    // number format
    private double totalValue;
}
```

### Custom Adapter

```java
public class MoneyAdapter implements JsonbAdapter<BigDecimal, String> {
    public String adaptToJson(BigDecimal obj) { return obj.toPlainString(); }
    public BigDecimal adaptFromJson(String obj) { return new BigDecimal(obj); }
}
```

---

## JSON-P — JSON Processing

### Builder API

```java
JsonObject portfolio = Json.createObjectBuilder()
    .add("owner", "John")
    .add("value", 50000.00)
    .add("stocks", Json.createArrayBuilder()
        .add(Json.createObjectBuilder()
            .add("symbol", "AAPL")
            .add("shares", 10)))
    .build();
```

### Streaming API (large documents)

```java
try (JsonParser parser = Json.createParser(inputStream)) {
    while (parser.hasNext()) {
        JsonParser.Event event = parser.next();
        if (event == JsonParser.Event.KEY_NAME && "owner".equals(parser.getString())) {
            parser.next();
            String owner = parser.getString();
        }
    }
}
```

### JSON Pointer and Patch

```java
// Pointer — navigate to a value
JsonPointer pointer = Json.createPointer("/stocks/0/symbol");
JsonString symbol = (JsonString) pointer.getValue(portfolio);

// Patch — modify a JSON document
JsonPatch patch = Json.createPatchBuilder()
    .replace("/value", 55000.00)
    .build();
JsonObject updated = patch.apply(portfolio);
```

---

## MicroProfile Rest Client

Type-safe HTTP client built on JAX-RS. Define an interface; the runtime generates the implementation.

### Interface Definition

```java
@RegisterRestClient(baseUri = "https://api.iexcloud.io/v1")
@Path("/stock")
public interface StockQuoteClient {

    @GET
    @Path("/{symbol}/quote")
    @Produces(MediaType.APPLICATION_JSON)
    StockQuote getQuote(@PathParam("symbol") String symbol);
}
```

### Injection

```java
@Inject
@RestClient
private StockQuoteClient stockQuoteClient;
```

### Configuration (microprofile-config.properties)

```properties
# Override base URI at runtime
com.example.StockQuoteClient/mp-rest/url=https://api.iexcloud.io/v1
com.example.StockQuoteClient/mp-rest/connectTimeout=5000
com.example.StockQuoteClient/mp-rest/readTimeout=10000
```

### Programmatic Usage

```java
StockQuoteClient client = RestClientBuilder.newBuilder()
    .baseUri(URI.create("https://api.iexcloud.io/v1"))
    .connectTimeout(5, TimeUnit.SECONDS)
    .build(StockQuoteClient.class);
```

### Adding Headers (ClientHeadersFactory)

```java
@RegisterProvider(AuthHeadersFactory.class)
@RegisterRestClient
public interface StockQuoteClient { ... }

public class AuthHeadersFactory implements ClientHeadersFactory {
    public MultivaluedMap<String, String> update(
            MultivaluedMap<String, String> incomingHeaders,
            MultivaluedMap<String, String> clientOutgoingHeaders) {
        clientOutgoingHeaders.putSingle("Authorization", "Bearer " + getToken());
        return clientOutgoingHeaders;
    }
}
```
