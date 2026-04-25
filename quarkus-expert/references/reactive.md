# Reactive Programming
## Chapter 8: Mutiny API, Reactive Engines, Virtual Threads, Back-Pressure

---

## Why Reactive in Quarkus?

Traditional thread-per-request model: each blocked I/O call (DB query, HTTP call) pins a thread. At 500 concurrent requests, you need 500 threads × ~1 MB stack = 500 MB just for stacks.

Reactive model: a small thread pool (event loop, ~N_CPU threads) handles all I/O callbacks. No thread is blocked. Same hardware, 10–100× more concurrent connections.

```
Thread-per-request:
  Request 1 → Thread 1 [-----DB wait------][respond]
  Request 2 → Thread 2 [-----DB wait------][respond]
  (thread blocked during DB wait)

Reactive event loop:
  Request 1 → enqueue DB call → release thread
  Request 2 → enqueue DB call → release thread
  DB responds → callback → respond to Request 1
  DB responds → callback → respond to Request 2
  (same 2 threads handled both requests)
```

---

## Mutiny — Quarkus's Reactive Library

Quarkus uses **SmallRye Mutiny** as its reactive API. Two core types:

| Type | Represents |
|---|---|
| `Uni<T>` | 0 or 1 item (eventually), like `CompletableFuture<T>` |
| `Multi<T>` | 0..N items over time, like `Publisher<T>` |

---

## Uni — Single Async Result

### Creating Uni

```java
// From a value
Uni<String> hello = Uni.createFrom().item("Hello");

// From a supplier (lazy)
Uni<String> lazy = Uni.createFrom().item(() -> computeValue());

// From a failure
Uni<String> failed = Uni.createFrom().failure(new RuntimeException("oops"));

// From CompletionStage
Uni<String> fromFuture = Uni.createFrom()
    .completionStage(someCompletableFuture());

// Empty (null)
Uni<Void> empty = Uni.createFrom().voidItem();
```

### Transforming Uni

```java
Uni<String> result = Uni.createFrom().item("hello")
    .map(s -> s.toUpperCase())                    // sync transform
    .flatMap(s -> fetchFromDb(s))                  // async transform (returns Uni)
    .onItem().transform(s -> "Result: " + s)
    .onItem().transformToUni(s -> callApi(s));
```

### Error Handling

```java
Uni<String> safe = uni
    .onFailure().recoverWithItem("fallback")        // recover with value
    .onFailure().recoverWithUni(e -> fallbackUni()) // recover with another Uni
    .onFailure(IOException.class).retry().atMost(3) // retry on specific exception
    .onFailure().transform(e -> new BusinessException(e)); // rethrow differently
```

### Combining Uni

```java
// Combine two Unis — wait for both, combine results
Uni<String> combined = Uni.combine().all()
    .unis(fetchUser(id), fetchOrders(id))
    .asTuple()
    .map(tuple -> tuple.getItem1().getName() + ": " + tuple.getItem2().size());

// First to complete wins
Uni<String> first = Uni.combine().any().of(fastSource(), slowSource());
```

### Awaiting (Use Only in Tests / Blocking Contexts)

```java
String value = uni.await().indefinitely();          // blocks forever
String value = uni.await().atMost(Duration.ofSeconds(5));
```

---

## Multi — Stream of Items

### Creating Multi

```java
// From items
Multi<String> items = Multi.createFrom().items("a", "b", "c");

// From iterable
Multi<Fruit> fruits = Multi.createFrom().iterable(fruitList);

// Periodic emission
Multi<Long> ticks = Multi.createTimePeriod().every(Duration.ofSeconds(1));

// From publisher
Multi<String> fromPublisher = Multi.createFrom().publisher(reactivePublisher);
```

### Processing Multi

```java
Multi<String> result = Multi.createFrom().items("hello", "world", "quarkus")
    .filter(s -> s.length() > 4)                    // filter items
    .map(s -> s.toUpperCase())                       // transform each
    .flatMap(s -> Multi.createFrom().items(s, s))    // fan out
    .select().first(5)                               // take first 5
    .collect().asList()                              // collect to Uni<List>
    .onItem().transform(list -> String.join(", ", list));
```

### Collecting Multi

```java
Uni<List<String>> list    = multi.collect().asList();
Uni<Map<K,V>>    map      = multi.collect().asMap(item -> item.key());
Uni<String>      joined   = multi.collect().with(Collectors.joining(", "));
Uni<Long>        count    = multi.collect().with(Collectors.counting());
```

### Error Recovery

```java
Multi<String> safe = multi
    .onFailure().recoverWithItem("fallback-item")
    .onFailure().recoverWithMulti(Multi.createFrom().items("a", "b"))
    .onFailure().retry().atMost(3);
```

### Back-Pressure

```java
// Request a specific number of items
multi.subscribe().with(
    item -> process(item),          // item handler
    failure -> log.error(failure),  // failure handler
    () -> log.info("Done")          // completion handler
);

// Control demand explicitly
Multi<String> controlled = multi
    .onOverflow().buffer(100)       // buffer 100 items if consumer is slow
    .onOverflow().drop();           // drop items if consumer is slow
```

---

## Using Reactive in JAX-RS Endpoints

```java
@Path("/fruits")
public class FruitResource {

    // Uni response — async, non-blocking
    @GET
    @Path("/{id}")
    public Uni<Fruit> get(@PathParam("id") Long id) {
        return Fruit.findById(id);
    }

    // Multi response — streaming
    @GET
    @Produces(MediaType.SERVER_SENT_EVENTS)
    public Multi<Fruit> stream() {
        return Fruit.streamAll();
    }

    // Combine multiple async calls
    @GET
    @Path("/with-orders/{id}")
    public Uni<FruitWithOrders> getWithOrders(@PathParam("id") Long id) {
        return Uni.combine().all()
            .unis(Fruit.findById(id), Order.find("fruitId", id).list())
            .asTuple()
            .map(t -> new FruitWithOrders(t.getItem1(), t.getItem2()));
    }
}
```

---

## Virtual Threads (Project Loom)

Virtual threads (Java 21+) let you write blocking-style code that runs with reactive efficiency. No Mutiny needed.

```java
@Path("/fruits")
public class FruitResource {

    @GET
    @RunOnVirtualThread          // runs on a virtual thread — can block freely
    public List<Fruit> list() {
        // This looks blocking but a virtual thread is pinned, not an OS thread
        return Fruit.listAll();  // blocking Panache call — fine on virtual thread
    }
}
```

### Virtual Threads vs. Reactive vs. Blocking

| Approach | Thread | Blocks OS Thread? | Code Style |
|---|---|---|---|
| Worker thread (`@Blocking`) | Platform thread | Yes | Imperative |
| Reactive (Mutiny) | Event loop | No | Functional/reactive |
| Virtual thread (`@RunOnVirtualThread`) | Virtual thread | No | Imperative |

**Rule:** prefer virtual threads for I/O-bound code in Java 21+; use Mutiny for complex reactive pipelines, streaming, or when you need back-pressure control.

---

## Reactive Context Propagation

CDI request context and Quarkus `Context` values propagate automatically across Mutiny pipelines in Quarkus 3.x+. No manual context passing needed for `@RequestScoped` beans.

```java
// @RequestScoped bean accessible inside Uni pipeline
@ApplicationScoped
public class MyService {

    @Inject
    @RequestScoped
    RequestContext ctx;    // automatically propagated into Uni callbacks
}
```

---

## Common Patterns

### Timeout

```java
Uni<Result> withTimeout = uni
    .ifNoItem().after(Duration.ofSeconds(5))
    .failWith(new TimeoutException("Too slow"));
```

### Retry with Backoff

```java
Uni<Result> withRetry = uni
    .onFailure(IOException.class)
    .retry()
    .withBackOff(Duration.ofMillis(100), Duration.ofSeconds(2))
    .atMost(5);
```

### Memoize / Cache

```java
Uni<Config> cachedConfig = loadConfig()
    .memoize().indefinitely();   // compute once, reuse result
```

### Converting Between Uni and CompletableFuture

```java
// Uni → CompletableFuture
CompletableFuture<String> cf = uni.subscribeAsCompletionStage();

// CompletableFuture → Uni
Uni<String> uni = Uni.createFrom().completionStage(cf);
```
