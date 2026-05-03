# Communications
## Chapter 4: REST, REST Clients, GraphQL, gRPC, Streaming

---

## REST with RESTEasy Reactive

Quarkus uses **RESTEasy Reactive** (JAX-RS 3.1 on Vert.x) — same annotations as classic JAX-RS but runs on the reactive event loop for better scalability.

### Basic Resource

```java
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;

@Path("/fruits")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class FruitResource {

    @GET
    public List<Fruit> list() {
        return Fruit.listAll();              // Panache
    }

    @GET
    @Path("/{id}")
    public Fruit get(@PathParam("id") Long id) {
        return Fruit.findById(id);
    }

    @POST
    @Transactional
    public Response create(Fruit fruit) {
        fruit.persist();
        return Response.created(URI.create("/fruits/" + fruit.id)).build();
    }

    @PUT
    @Path("/{id}")
    @Transactional
    public Fruit update(@PathParam("id") Long id, Fruit update) {
        Fruit existing = Fruit.findByIdOrElseThrow(id);
        existing.name = update.name;
        return existing;
    }

    @DELETE
    @Path("/{id}")
    @Transactional
    public void delete(@PathParam("id") Long id) {
        Fruit.deleteById(id);
    }
}
```

### Query and Header Parameters

```java
@GET
public List<Fruit> search(
    @QueryParam("name") String name,                    // ?name=apple
    @DefaultValue("10") @QueryParam("limit") int limit,
    @HeaderParam("X-Tenant-ID") String tenantId,
    @BeanParam FruitFilter filter                       // group params in POJO
) { ... }
```

### Response Codes and Error Handling

```java
// Explicit response
return Response.ok(fruit).build();           // 200
return Response.status(404).build();         // 404
return Response.created(uri).entity(dto).build(); // 201

// Exception mappers
@Provider
public class NotFoundMapper implements ExceptionMapper<NotFoundException> {
    @Override
    public Response toResponse(NotFoundException e) {
        return Response.status(404)
            .entity(new ErrorDTO(e.getMessage()))
            .build();
    }
}
```

### Blocking vs. Non-Blocking

```java
// Default: runs on event loop (must not block)
@GET
public Uni<List<Fruit>> listAsync() {
    return Fruit.listAll();           // reactive Panache
}

// Blocking allowed: runs on worker thread
@GET
@Blocking
public List<Fruit> listBlocking() {
    return Fruit.listAll();           // blocking Panache
}
```

### Content Negotiation and Jackson

```java
// Jackson customization via CDI producer
@Singleton
public class JacksonCustomizer implements ObjectMapperCustomizer {
    @Override
    public void customize(ObjectMapper mapper) {
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }
}
```

```properties
quarkus.jackson.serialization-inclusion=non-null
quarkus.jackson.fail-on-unknown-properties=false
```

---

## REST Clients (MicroProfile + RESTEasy Reactive)

### Define a Client Interface

```java
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@Path("/api")
@RegisterRestClient(configKey = "weather-api")
@Produces(MediaType.APPLICATION_JSON)
public interface WeatherClient {

    @GET
    @Path("/weather/{city}")
    WeatherData getWeather(@PathParam("city") String city);

    @GET
    @Path("/forecast")
    List<Forecast> getForecast(@QueryParam("days") int days);
}
```

### Configure and Inject

```properties
quarkus.rest-client.weather-api.url=https://api.weather.example.com
quarkus.rest-client.weather-api.scope=ApplicationScoped
quarkus.rest-client.weather-api.connect-timeout=2000
quarkus.rest-client.weather-api.read-timeout=5000
```

```java
@ApplicationScoped
public class WeatherService {

    @RestClient
    WeatherClient weatherClient;

    public WeatherData getCurrentWeather(String city) {
        return weatherClient.getWeather(city);
    }
}
```

### Reactive REST Client

```java
@RegisterRestClient(configKey = "weather-api")
public interface WeatherClient {

    @GET
    @Path("/weather/{city}")
    Uni<WeatherData> getWeather(@PathParam("city") String city);
}
```

### Client Request/Response Filters

```java
@Provider
public class AuthHeaderFilter implements ClientRequestFilter {
    @Override
    public void filter(ClientRequestContext ctx) {
        ctx.getHeaders().add("Authorization", "Bearer " + getToken());
    }
}
```

```java
@RegisterRestClient
@RegisterProvider(AuthHeaderFilter.class)
public interface SecureClient { ... }
```

---

## GraphQL with SmallRye GraphQL

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-graphql</artifactId>
</dependency>
```

### GraphQL API

```java
import org.eclipse.microprofile.graphql.*;

@GraphQLApi
public class FilmResource {

    @Inject
    FilmService filmService;

    @Query("allFilms")
    @Description("Get all films")
    public List<Film> getAllFilms() {
        return filmService.getAllFilms();
    }

    @Query
    public Film film(@Name("filmId") int id) {
        return filmService.getFilm(id);
    }

    @Mutation
    public Film createFilm(Film film) {
        return filmService.save(film);
    }

    @Mutation
    public boolean deleteFilm(@Name("filmId") int id) {
        return filmService.delete(id);
    }
}
```

### Subscriptions (Reactive)

```java
@Subscription
public Multi<Film> filmAdded() {
    return filmService.filmAddedStream();
}
```

### GraphQL UI

Available at `http://localhost:8080/q/graphql-ui` in dev mode.

```properties
quarkus.smallrye-graphql.ui.always-include=true   # Include in prod
```

---

## gRPC

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-grpc</artifactId>
</dependency>
```

### Define Service in .proto

```protobuf
// src/main/proto/helloworld.proto
syntax = "proto3";

option java_package = "com.example.grpc";
option java_outer_classname = "HelloWorldProto";

package helloworld;

service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
    rpc SayHelloStreaming (HelloRequest) returns (stream HelloReply);
}

message HelloRequest {
    string name = 1;
}

message HelloReply {
    string message = 1;
}
```

Quarkus generates Java stubs from `.proto` at build time.

### Implement gRPC Service

```java
import io.quarkus.grpc.GrpcService;

@GrpcService
public class GreeterService implements Greeter {

    @Override
    public Uni<HelloReply> sayHello(HelloRequest request) {
        return Uni.createFrom().item(
            HelloReply.newBuilder()
                .setMessage("Hello " + request.getName())
                .build()
        );
    }

    @Override
    public Multi<HelloReply> sayHelloStreaming(HelloRequest request) {
        return Multi.createFrom().items(
            HelloReply.newBuilder().setMessage("Hello " + request.getName()).build(),
            HelloReply.newBuilder().setMessage("Goodbye " + request.getName()).build()
        );
    }
}
```

### Inject gRPC Client

```java
@ApplicationScoped
public class GreeterClient {

    @GrpcClient("greeter")
    Greeter client;

    public String greet(String name) {
        return client.sayHello(
            HelloRequest.newBuilder().setName(name).build()
        ).await().indefinitely().getMessage();
    }
}
```

```properties
quarkus.grpc.clients.greeter.host=localhost
quarkus.grpc.clients.greeter.port=9000
```

---

## Server-Sent Events (SSE) / Streaming

```java
@GET
@Path("/stream")
@Produces(MediaType.SERVER_SENT_EVENTS)
@SseElementType(MediaType.APPLICATION_JSON)
public Multi<Fruit> stream() {
    return fruitService.streamAllFruits();   // returns Multi<Fruit>
}
```

### HTTP/1.1 Chunked Streaming

```java
@GET
@Path("/chunked")
@Produces(MediaType.APPLICATION_OCTET_STREAM)
public Multi<byte[]> chunked() {
    return Multi.createFrom().items(chunk1, chunk2, chunk3);
}
```

---

## OpenAPI / Swagger

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-openapi</artifactId>
</dependency>
```

```properties
# Endpoints
# /q/openapi      → OpenAPI 3 YAML/JSON spec
# /q/swagger-ui   → Swagger UI (dev mode only by default)

quarkus.swagger-ui.always-include=true    # Enable in prod
quarkus.smallrye-openapi.info-title=My API
quarkus.smallrye-openapi.info-version=1.0
```

```java
// Annotate resources
@Operation(summary = "List all fruits")
@APIResponse(responseCode = "200", description = "All fruits returned")
@GET
public List<Fruit> list() { ... }
```
