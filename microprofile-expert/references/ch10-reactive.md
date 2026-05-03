# Chapter 10: Reactive Cloud-Native Applications

## Imperative vs. Reactive

| | Imperative | Reactive |
|---|---|---|
| Execution | Blocking — thread waits for I/O | Non-blocking — thread freed during I/O |
| Scaling | One thread per request; limited by thread pool | Fewer threads handle more concurrent work |
| Complexity | Familiar sequential code | Async pipelines; harder to reason about |
| Best for | CRUD-heavy services, simple request/response | High-throughput I/O, event-driven systems |

MicroProfile enables reactive patterns without abandoning familiar Java idioms.

---

## MicroProfile Context Propagation 1.2

Propagates thread context (CDI, Security, Transaction, Application) across async boundaries (CompletableFuture, ExecutorService, reactive streams).

### Problem

```java
// CDI injection, security context, etc. are NOT available in async threads by default
CompletableFuture.runAsync(() -> {
    // @RequestScoped beans, JWT principal — unavailable here
});
```

### Solution

```java
@Inject
ManagedExecutorService executor;  // context-aware executor

public CompletableFuture<Double> getValueAsync(String owner) {
    return executor.supplyAsync(() -> {
        // CDI injection, security context propagated here
        return portfolioService.calculateValue(owner);
    });
}
```

### Configuration

```java
// Specify which context types to propagate
ManagedExecutorService executor = ManagedExecutorBuilder.instance()
    .propagated(ThreadContext.SECURITY, ThreadContext.CDI)
    .cleared(ThreadContext.TRANSACTION)
    .build();
```

### JAX-RS Async with Context Propagation

```java
@GET
@Path("/{owner}/value")
public CompletionStage<Double> getValueAsync(@PathParam("owner") String owner) {
    return executor.supplyAsync(() -> portfolioService.calculateValue(owner));
}
```

Open Liberty `server.xml` feature:

```xml
<feature>mpContextPropagation-1.2</feature>
```

---

## MicroProfile Reactive Messaging 2.0

Decouples services through a messaging channel. Connectors bridge to external brokers (Kafka, AMQP, MQTT).

### Core Concepts

- **Channel**: named pipe through which messages flow
- **@Incoming**: method consumes from a channel
- **@Outgoing**: method produces to a channel
- **Message**: wrapper around payload with metadata and ack/nack

### Simple Bean Example

```java
@ApplicationScoped
public class TradeProcessor {

    // Consume from "trade-requests" channel, produce to "trade-results"
    @Incoming("trade-requests")
    @Outgoing("trade-results")
    public TradeResult processTrade(Trade trade) {
        return tradeService.execute(trade);
    }
}
```

### Kafka Connector Configuration

```properties
# microprofile-config.properties

# Incoming — consume from Kafka topic
mp.messaging.incoming.trade-requests.connector=liberty-kafka
mp.messaging.incoming.trade-requests.topic=trade-requests
mp.messaging.incoming.trade-requests.bootstrap.servers=kafka:9092
mp.messaging.incoming.trade-requests.group.id=portfolio-group
mp.messaging.incoming.trade-requests.auto.offset.reset=earliest
mp.messaging.incoming.trade-requests.value.deserializer=com.example.TradeDeserializer

# Outgoing — produce to Kafka topic
mp.messaging.outgoing.trade-results.connector=liberty-kafka
mp.messaging.outgoing.trade-results.topic=trade-results
mp.messaging.outgoing.trade-results.bootstrap.servers=kafka:9092
mp.messaging.outgoing.trade-results.value.serializer=com.example.TradeResultSerializer
```

### Reactive Streams (Publisher/Subscriber)

```java
@Incoming("raw-quotes")
@Outgoing("filtered-quotes")
public PublisherBuilder<StockQuote> filterActiveStocks(
        PublisherBuilder<StockQuote> quotes) {
    return quotes
        .filter(q -> q.getVolume() > 1000)
        .map(q -> enrichWithSentiment(q));
}
```

### Explicit Message Handling (Ack Control)

```java
@Incoming("trade-requests")
public CompletionStage<Void> processTradeWithAck(Message<Trade> message) {
    Trade trade = message.getPayload();
    try {
        tradeService.execute(trade);
        return message.ack();        // explicit acknowledgement
    } catch (NonRetryableException e) {
        return message.nack(e);      // nack — dead letter queue
    }
}
```

### Emitter — Producing Messages Imperatively

```java
@Inject
@Channel("trade-requests")
private Emitter<Trade> tradeEmitter;

public void submitTrade(Trade trade) {
    tradeEmitter.send(Message.of(trade)
        .addMetadata(OutgoingKafkaRecordMetadata.<String>builder()
            .withKey(trade.getOwner())
            .build()));
}
```

### Error Handling and Dead Letter Queue

```properties
mp.messaging.incoming.trade-requests.failure-strategy=dead-letter-queue
mp.messaging.incoming.trade-requests.dead-letter-queue.topic=trade-requests-dlq
```

### Open Liberty Feature

```xml
<featureManager>
    <feature>mpReactiveMessaging-2.0</feature>
</featureManager>
```

---

## Reactive Patterns in the Stock Trader App

### Trade History (Event Sourcing)

```
Portfolio Service
    │  (Emitter)
    ▼
Kafka topic: trade-events
    │  (@Incoming)
    ▼
Trade History Service  → persist to database
```

### Notification (Fan-out)

```
Portfolio Service
    │ (emit loyalty-change)
    ▼
Kafka topic: loyalty-changes
    ├──▶ Notification-Twitter Service
    └──▶ Notification-Slack Service
```

The portfolio service fires and forgets — it does not wait for notification delivery.

---

## Backpressure

Reactive Messaging respects Reactive Streams backpressure. When a consumer is slow, the framework buffers or drops messages depending on the overflow strategy:

```java
@Inject
@Channel("trade-requests")
@OnOverflow(value = OnOverflow.Strategy.BUFFER, bufferSize = 100)
private Emitter<Trade> tradeEmitter;
```

Strategies: `BUFFER`, `DROP`, `FAIL`, `UNBOUNDED_BUFFER`, `LATEST`, `NONE`.
