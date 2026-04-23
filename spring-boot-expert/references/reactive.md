# Reactive Programming with Spring Boot

Chapter 10 of *Spring Boot Up & Running* — Project Reactor (Mono/Flux), Spring WebFlux, reactive Spring Data, functional routes, backpressure, testing with StepVerifier.

---

## Why Reactive?

Traditional MVC: one thread per request (blocking). Under high concurrency, threads exhaust the pool and latency spikes.

Reactive: event-loop threads (like Node.js), never blocked. A small number of threads handle thousands of concurrent requests by using non-blocking I/O.

```
Servlet/MVC (Tomcat)            WebFlux (Netty)
────────────────────           ─────────────────
Thread A → request 1           Event loop thread
Thread B → request 2      →   handles all requests
Thread C → request 3           non-blocking I/O
... (200 threads max)           (< 10 threads, infinite concurrency)
```

**When to choose reactive**:
- High I/O concurrency (streaming, long-polling, websockets)
- Need to compose async data from multiple services
- Already using reactive drivers (R2DBC, reactive MongoDB)

**When NOT to choose reactive**:
- Team is new to reactive; debugging is harder
- Using JDBC (blocking) — mixing reactive + blocking breaks the model
- Simple CRUD apps where MVC is sufficient

---

## Project Reactor Fundamentals

Reactor is Spring's reactive library (included with `spring-boot-starter-webflux`).

### Mono and Flux

```
Mono<T>   — 0 or 1 element (like Optional but async)
Flux<T>   — 0 to N elements (async stream)
```

```java
// Mono examples
Mono<String> mono = Mono.just("hello");
Mono<String> empty = Mono.empty();
Mono<String> error = Mono.error(new RuntimeException("fail"));

// Flux examples
Flux<String> flux = Flux.just("a", "b", "c");
Flux<Integer> range = Flux.range(1, 10);
Flux<String> fromList = Flux.fromIterable(List.of("x", "y", "z"));
```

**Nothing happens until you subscribe.** Publishers are lazy.

### Common Operators

```java
// Transform each element
Flux<String> upper = Flux.just("a", "b").map(String::toUpperCase);

// Async transform (returns another Mono/Flux per element)
Flux<Coffee> coffees = Flux.just("1", "2")
        .flatMap(id -> coffeeRepository.findById(id));

// Filter
Flux<Integer> evens = Flux.range(1, 10).filter(n -> n % 2 == 0);

// Take / limit
Flux<Integer> first5 = Flux.range(1, 100).take(5);

// Combine
Flux<String> merged = Flux.merge(flux1, flux2);
Mono<Tuple2<A, B>> zipped = Mono.zip(monoA, monoB);

// Error handling
Mono<Coffee> safe = coffeeMono
        .onErrorReturn(new Coffee("default", "Unknown"))
        .onErrorResume(ex -> Mono.just(fallback));

// Convert empty to error
Mono<Coffee> orElseError = coffeeMono
        .switchIfEmpty(Mono.error(new NotFoundException("coffee not found")));

// Log intermediate signals (debugging)
Flux.range(1, 5).log().subscribe();
```

---

## Spring WebFlux Controllers

WebFlux supports the same `@RestController` annotation style as MVC — just return `Mono` / `Flux` instead of plain objects:

```java
@RestController
@RequestMapping("/api/coffees")
public class CoffeeController {

    private final CoffeeRepository repo;

    @GetMapping
    public Flux<Coffee> getAllCoffees() {
        return repo.findAll();
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<Coffee>> getCoffeeById(@PathVariable String id) {
        return repo.findById(id)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<Coffee> postCoffee(@RequestBody Coffee coffee) {
        return repo.save(coffee);
    }

    @DeleteMapping("/{id}")
    public Mono<Void> deleteCoffee(@PathVariable String id) {
        return repo.deleteById(id);
    }
}
```

---

## Functional Routing (Router Functions)

An alternative to annotation-based controllers — cleaner separation of routing from handling:

```java
@Configuration
public class CoffeeRoutes {

    @Bean
    public RouterFunction<ServerResponse> coffeeRouter(CoffeeHandler handler) {
        return RouterFunctions.route()
                .GET("/api/coffees", handler::getAllCoffees)
                .GET("/api/coffees/{id}", handler::getCoffeeById)
                .POST("/api/coffees", handler::postCoffee)
                .DELETE("/api/coffees/{id}", handler::deleteCoffee)
                .build();
    }
}

@Component
public class CoffeeHandler {

    private final CoffeeRepository repo;

    public Mono<ServerResponse> getAllCoffees(ServerRequest request) {
        return ServerResponse.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(repo.findAll(), Coffee.class);
    }

    public Mono<ServerResponse> getCoffeeById(ServerRequest request) {
        return repo.findById(request.pathVariable("id"))
                .flatMap(coffee -> ServerResponse.ok().bodyValue(coffee))
                .switchIfEmpty(ServerResponse.notFound().build());
    }

    public Mono<ServerResponse> postCoffee(ServerRequest request) {
        return request.bodyToMono(Coffee.class)
                .flatMap(repo::save)
                .flatMap(saved -> ServerResponse.created(
                        URI.create("/api/coffees/" + saved.getId()))
                        .bodyValue(saved));
    }

    public Mono<ServerResponse> deleteCoffee(ServerRequest request) {
        return repo.deleteById(request.pathVariable("id"))
                .flatMap(v -> ServerResponse.noContent().build());
    }
}
```

---

## Reactive Spring Data (R2DBC)

For reactive relational database access (non-blocking, unlike JDBC):

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-h2</artifactId>  <!-- or r2dbc-postgresql -->
    <scope>runtime</scope>
</dependency>
```

```properties
spring.r2dbc.url=r2dbc:h2:mem:///testdb
# For PostgreSQL:
spring.r2dbc.url=r2dbc:postgresql://localhost:5432/mydb
spring.r2dbc.username=myuser
spring.r2dbc.password=secret
```

```java
public interface CoffeeRepository extends ReactiveCrudRepository<Coffee, String> {
    Flux<Coffee> findByName(String name);
    Mono<Coffee> findFirstByName(String name);
}
```

`ReactiveCrudRepository` returns `Mono` / `Flux` instead of `Optional` / `List`.

For MongoDB (naturally reactive):
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb-reactive</artifactId>
</dependency>
```

```java
public interface CoffeeRepository extends ReactiveMongoRepository<Coffee, String> { }
```

---

## Server-Sent Events (SSE) Streaming

Reactive makes streaming to clients natural:

```java
@GetMapping(value = "/api/coffees/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<Coffee> streamCoffees() {
    return repo.findAll()
            .delayElements(Duration.ofSeconds(1));  // emit one per second
}
```

---

## Backpressure

Reactor handles backpressure (slow consumer, fast producer) automatically. The consumer signals how many items it can handle:

```java
Flux.range(1, 1000)
    .onBackpressureDrop()          // drop when consumer is slow
    .onBackpressureBuffer(100)     // buffer up to 100
    .onBackpressureLatest()        // keep only latest
    .subscribe(new BaseSubscriber<>() {
        @Override
        protected void hookOnSubscribe(Subscription subscription) {
            request(10);  // request 10 items initially
        }
        @Override
        protected void hookOnNext(Integer value) {
            // process value
            request(1);   // request one more after each
        }
    });
```

---

## Testing with StepVerifier

`StepVerifier` is the reactive testing API included with Reactor:

```java
import reactor.test.StepVerifier;

@Test
void testGetAllCoffees() {
    // Arrange
    given(repo.findAll()).willReturn(Flux.just(
            new Coffee("1", "Espresso"),
            new Coffee("2", "Latte")
    ));

    // Act & Assert
    StepVerifier.create(service.getAllCoffees())
            .expectNextMatches(c -> c.getName().equals("Espresso"))
            .expectNextMatches(c -> c.getName().equals("Latte"))
            .verifyComplete();
}

@Test
void testCoffeeNotFound() {
    given(repo.findById("99")).willReturn(Mono.empty());

    StepVerifier.create(service.getCoffeeById("99"))
            .expectError(CoffeeNotFoundException.class)
            .verify();
}

@Test
void testWithDelay() {
    // Use virtual time to test timed operations without real waiting
    StepVerifier.withVirtualTime(() ->
            Flux.interval(Duration.ofSeconds(1)).take(3))
            .thenAwait(Duration.ofSeconds(3))
            .expectNextCount(3)
            .verifyComplete();
}
```

### WebTestClient for WebFlux

```java
@WebFluxTest(CoffeeController.class)
class CoffeeControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private CoffeeRepository repo;

    @Test
    void getAllCoffees_returnsFlux() {
        given(repo.findAll()).willReturn(Flux.just(new Coffee("1", "Espresso")));

        webTestClient.get().uri("/api/coffees")
                .accept(MediaType.APPLICATION_JSON)
                .exchange()
                .expectStatus().isOk()
                .expectBodyList(Coffee.class)
                .hasSize(1)
                .contains(new Coffee("1", "Espresso"));
    }
}
```

---

## Mixing Reactive and Blocking Code

**Never block inside a reactive pipeline** — it will deadlock or starve the event loop:

```java
// BAD: blocks the Netty event loop thread
Flux<Coffee> bad = Flux.just("1", "2")
        .map(id -> jdbcCoffeeRepository.findById(id));  // BLOCKING JDBC call

// GOOD: offload blocking calls to a bounded elastic scheduler
Flux<Coffee> good = Flux.just("1", "2")
        .flatMap(id -> Mono.fromCallable(() -> jdbcCoffeeRepository.findById(id))
                .subscribeOn(Schedulers.boundedElastic()));
```

`Schedulers.boundedElastic()` is designed for wrapping legacy blocking I/O in reactive code.

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nothing happens | Forgot to subscribe (or chain to a handler that subscribes) | Ensure the pipeline is subscribed; Spring handles this for controller return values |
| `BlockingOperationError` | Called `.block()` on reactive thread | Move to `Schedulers.boundedElastic()` or redesign to stay reactive |
| Flux emits unexpected order | `flatMap` doesn't preserve order | Use `concatMap` instead (sequential, preserves order) |
| Memory pressure | Unbounded `flatMap` concurrency | Use `flatMap(fn, maxConcurrency)` to limit parallel executions |
| `IllegalStateException: Only one subscriber` | `Mono.fromCallable` called multiple times | Cold vs hot publisher — use `share()` or `cache()` for multicast |
