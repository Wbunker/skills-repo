# Ch 5 — Exposing Data as a Service

## RESTEasy (Jakarta REST / JAX-RS 3.1)

WildFly ships with **RESTEasy** as its JAX-RS 3.1 implementation. No additional dependencies needed for Jakarta EE deployments.

> **Jakarta EE 9+ namespace change:** All packages changed from `javax.ws.rs.*` → `jakarta.ws.rs.*`

### Application Activation

```java
// Option 1: No web.xml needed — annotate Application class
@ApplicationPath("/api")
public class RestApplication extends Application { }

// Option 2: Empty Application class with web.xml mapping
// web.xml: <servlet-mapping><url-pattern>/api/*</url-pattern></servlet-mapping>
```

### Basic Resource

```java
@Path("/products")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RequestScoped
public class ProductResource {

    @Inject private ProductService service;

    @GET
    public List<Product> findAll(
            @QueryParam("page") @DefaultValue("0") int page,
            @QueryParam("size") @DefaultValue("20") int size) {
        return service.findAll(page, size);
    }

    @GET
    @Path("/{id}")
    public Response findById(@PathParam("id") Long id) {
        return service.findById(id)
            .map(p -> Response.ok(p).build())
            .orElse(Response.status(Status.NOT_FOUND).build());
    }

    @POST
    @ResponseStatus(201)
    public Response create(Product product, @Context UriInfo uriInfo) {
        Product created = service.create(product);
        URI location = uriInfo.getAbsolutePathBuilder()
            .path(created.getId().toString()).build();
        return Response.created(location).entity(created).build();
    }

    @PUT
    @Path("/{id}")
    public Response update(@PathParam("id") Long id, Product product) {
        return service.update(id, product)
            .map(p -> Response.ok(p).build())
            .orElse(Response.status(Status.NOT_FOUND).build());
    }

    @DELETE
    @Path("/{id}")
    public Response delete(@PathParam("id") Long id) {
        service.delete(id);
        return Response.noContent().build();
    }
}
```

### Exception Mapping

```java
@Provider
public class ConstraintViolationMapper
        implements ExceptionMapper<ConstraintViolationException> {
    @Override
    public Response toResponse(ConstraintViolationException e) {
        Map<String, String> errors = e.getConstraintViolations().stream()
            .collect(Collectors.toMap(
                cv -> cv.getPropertyPath().toString(),
                ConstraintViolation::getMessage));
        return Response.status(Status.BAD_REQUEST)
            .entity(errors).build();
    }
}
```

### Filters and Interceptors

```java
// Request filter (e.g., auth check)
@Provider
@Priority(Priorities.AUTHENTICATION)
public class AuthFilter implements ContainerRequestFilter {
    @Override
    public void filter(ContainerRequestContext ctx) {
        String auth = ctx.getHeaderString(HttpHeaders.AUTHORIZATION);
        if (auth == null || !isValid(auth)) {
            ctx.abortWith(Response.status(Status.UNAUTHORIZED).build());
        }
    }
}

// Response filter (e.g., add CORS headers)
@Provider
public class CorsFilter implements ContainerResponseFilter {
    @Override
    public void filter(ContainerRequestContext req, ContainerResponseContext resp) {
        resp.getHeaders().add("Access-Control-Allow-Origin", "*");
    }
}
```

### Content Negotiation

```java
@GET
@Path("/{id}")
@Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
public Product findById(@PathParam("id") Long id) { ... }
// Client sends: Accept: application/xml → returns XML
// Client sends: Accept: application/json → returns JSON
```

### Async REST (Jakarta REST 3.1)

```java
@GET
@Path("/async")
public void asyncGet(@Suspended AsyncResponse response) {
    executor.execute(() -> {
        Product result = expensiveOperation();
        response.resume(result);
    });
}

// Or using CompletionStage
@GET
@Path("/completable")
public CompletionStage<Product> completable() {
    return CompletableFuture.supplyAsync(this::expensiveOperation);
}
```

## MicroProfile REST Client

The MicroProfile REST Client provides a type-safe client that matches your resource interface.

```java
// 1. Define client interface matching the server resource
@RegisterRestClient(baseUri = "http://product-service/api")
@Path("/products")
public interface ProductClient {
    @GET
    List<Product> findAll();

    @GET
    @Path("/{id}")
    Product findById(@PathParam("id") Long id);

    @POST
    Response create(Product product);
}

// 2. Inject and use
@Inject
@RestClient
private ProductClient productClient;

List<Product> products = productClient.findAll();
```

Configure via `microprofile-config.properties`:
```properties
com.example.ProductClient/mp-rest/url=http://product-service:8080/api
com.example.ProductClient/mp-rest/connectTimeout=5000
com.example.ProductClient/mp-rest/readTimeout=10000
```

## MicroProfile OpenAPI 4.0

Automatically generates OpenAPI 3.x spec from JAX-RS annotations.

```java
@Path("/products")
@Tag(name = "Products", description = "Product management API")
public class ProductResource {

    @GET
    @Operation(summary = "List all products")
    @APIResponse(responseCode = "200",
                 content = @Content(mediaType = "application/json",
                 schema = @Schema(type = SchemaType.ARRAY,
                                  implementation = Product.class)))
    public List<Product> findAll() { ... }
}
```

Access the spec at:
- `/openapi` — OpenAPI YAML
- `/openapi?format=json` — OpenAPI JSON
- `/swagger-ui` — Swagger UI (if enabled)

Configure in `microprofile-config.properties`:
```properties
mp.openapi.servers=/api
mp.openapi.info.title=My API
mp.openapi.info.version=1.0.0
```

## SOAP Web Services (JAX-WS / Apache CXF)

WildFly ships Apache CXF for JAX-WS.

### Service Implementation

```java
@WebService(name = "ProductService",
            serviceName = "ProductServiceWS",
            targetNamespace = "http://example.com/products")
public class ProductWebService {

    @Inject private ProductService service;

    @WebMethod(operationName = "getProduct")
    @WebResult(name = "product")
    public ProductDTO getProduct(
            @WebParam(name = "productId") Long id) {
        return service.findById(id)
            .map(ProductDTO::from)
            .orElseThrow(() -> new RuntimeException("Not found"));
    }

    @WebMethod
    public List<ProductDTO> getAllProducts() {
        return service.findAll().stream()
            .map(ProductDTO::from)
            .collect(Collectors.toList());
    }
}
```

WSDL auto-generated at: `http://localhost:8080/myapp/ProductServiceWS?wsdl`

### Contract-First (WSDL-to-Java)

```bash
# Generate client stubs from WSDL
wsimport -keep -s src/main/java \
         http://remote-service/service?wsdl
```

Or with CXF wsdl2java Maven plugin:
```xml
<plugin>
  <groupId>org.apache.cxf</groupId>
  <artifactId>cxf-codegen-plugin</artifactId>
  <executions>
    <execution>
      <goals><goal>wsdl2java</goal></goals>
      <configuration>
        <wsdlOptions>
          <wsdlOption><wsdl>src/main/resources/service.wsdl</wsdl></wsdlOption>
        </wsdlOptions>
      </configuration>
    </execution>
  </executions>
</plugin>
```

## MicroProfile Fault Tolerance 4.1

```java
@ApplicationScoped
public class ProductClient {

    @Retry(maxRetries = 3, delay = 200, jitter = 50)
    @Timeout(1000)
    @Fallback(fallbackMethod = "fallbackProducts")
    @CircuitBreaker(requestVolumeThreshold = 10,
                    failureRatio = 0.5,
                    delay = 5000)
    @Bulkhead(5)
    public List<Product> fetchProducts() {
        return remoteService.getProducts();
    }

    public List<Product> fallbackProducts() {
        return cachedProducts;
    }
}
```

## MicroProfile Config

Externalize configuration (no hardcoded values in JARs):

```java
@Inject
@ConfigProperty(name = "product.cache.ttl", defaultValue = "300")
private int cacheTtl;

@Inject
@ConfigProperty(name = "remote.service.url")
private String serviceUrl;
```

Config sources (priority order, highest first):
1. System properties (`-Dkey=value`)
2. Environment variables (`KEY=value`)
3. `META-INF/microprofile-config.properties`
4. `microprofile-config.properties` in classpath

## REST Design Patterns

### HATEOAS with Jakarta REST

```java
@GET
@Path("/{id}")
public Response findById(@PathParam("id") Long id, @Context UriInfo uriInfo) {
    Product p = service.findById(id);
    Link self = Link.fromUriBuilder(uriInfo.getAbsolutePathBuilder())
        .rel("self").build();
    Link orders = Link.fromUri(uriInfo.getBaseUri() + "orders?productId=" + id)
        .rel("orders").build();
    return Response.ok(p).links(self, orders).build();
}
```

### Pagination Response Pattern

```java
@GET
public Response findAll(@QueryParam("page") int page,
                        @QueryParam("size") int size,
                        @Context UriInfo uriInfo) {
    Page<Product> result = service.findAll(page, size);
    return Response.ok(result.getContent())
        .header("X-Total-Count", result.getTotalElements())
        .header("X-Page", page)
        .header("X-Page-Size", size)
        .build();
}
```

## JAX-RS vs REST Client Decision

```
Making an outbound call to another service?
├── Strong typing, shared interface → MicroProfile REST Client
├── Dynamic URLs or flexible → RESTEasy Client (jakarta.ws.rs.client)
└── Legacy code → Apache HttpClient / OkHttp (avoid when possible)

Exposing a service?
├── JSON/HTTP REST → JAX-RS resource class
├── SOAP (legacy integration) → JAX-WS @WebService
└── gRPC → Quarkus gRPC extension (not in base WildFly)
```
