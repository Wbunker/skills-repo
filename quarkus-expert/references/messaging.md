# Quarkus Messaging
## Chapter 9: MicroProfile Reactive Messaging, Kafka, RabbitMQ, Acknowledgment

---

## MicroProfile Reactive Messaging

Quarkus messaging is built on **SmallRye Reactive Messaging**, an implementation of MicroProfile Reactive Messaging. The model is channel-based: beans declare `@Incoming` and `@Outgoing` channels; connectors bind channels to brokers.

```
Producer bean              Channel (in-memory or broker)       Consumer bean
─────────────              ─────────────────────────────       ─────────────
@Outgoing("orders") ──►  "orders" channel  ──►  @Incoming("orders")
```

---

## Kafka

### Dependencies

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-reactive-messaging-kafka</artifactId>
</dependency>
```

Dev Services start a Kafka container automatically when no `bootstrap.servers` is configured.

### Producing Messages

```java
@ApplicationScoped
public class OrderProducer {

    @Channel("orders")
    Emitter<Order> emitter;             // inject emitter for programmatic send

    public void placeOrder(Order order) {
        emitter.send(order);            // fire and forget
    }

    // With completion callback
    public CompletionStage<Void> placeOrderAsync(Order order) {
        return emitter.send(order);
    }
}
```

```java
// Using @Outgoing in a method (reactive source)
@ApplicationScoped
public class PriceGenerator {

    @Outgoing("prices")
    public Multi<Double> generate() {
        return Multi.createFrom().ticks()
            .every(Duration.ofSeconds(1))
            .map(tick -> Math.random() * 100);
    }
}
```

### Consuming Messages

```java
@ApplicationScoped
public class OrderConsumer {

    @Incoming("orders")
    public void consume(Order order) {          // simple, blocking consumer
        process(order);
    }

    @Incoming("orders")
    public Uni<Void> consumeReactive(Order order) {  // reactive consumer
        return processAsync(order);
    }
}
```

### Processing (Incoming → Outgoing)

```java
@ApplicationScoped
public class OrderProcessor {

    @Incoming("orders")
    @Outgoing("invoices")
    public Invoice process(Order order) {
        return invoiceService.createFrom(order);
    }

    @Incoming("orders")
    @Outgoing("invoices")
    public Uni<Invoice> processReactive(Order order) {
        return invoiceService.createFromAsync(order);
    }

    // Stream processing
    @Incoming("orders")
    @Outgoing("invoices")
    public Multi<Invoice> processStream(Multi<Order> orders) {
        return orders
            .filter(o -> o.amount > 0)
            .map(o -> invoiceService.createFrom(o));
    }
}
```

### Kafka Configuration

```properties
# Incoming (consumer)
mp.messaging.incoming.orders.connector=smallrye-kafka
mp.messaging.incoming.orders.topic=orders-topic
mp.messaging.incoming.orders.group.id=order-service
mp.messaging.incoming.orders.auto.offset.reset=earliest
mp.messaging.incoming.orders.value.deserializer=io.quarkus.kafka.client.serialization.JsonbDeserializer

# Outgoing (producer)
mp.messaging.outgoing.invoices.connector=smallrye-kafka
mp.messaging.outgoing.invoices.topic=invoices-topic
mp.messaging.outgoing.invoices.value.serializer=io.quarkus.kafka.client.serialization.JsonbSerializer

# Bootstrap servers (default: Dev Service auto-assigns)
kafka.bootstrap.servers=localhost:9092
```

### Kafka-Specific Features

```java
// Access Kafka record metadata
@Incoming("orders")
public void consume(Message<Order> message) {
    IncomingKafkaRecordMetadata<String, Order> meta =
        message.getMetadata(IncomingKafkaRecordMetadata.class).get();

    String topic = meta.getTopic();
    int partition = meta.getPartition();
    long offset = meta.getOffset();
    String key = meta.getKey();

    Order order = message.getPayload();
    process(order);
    message.ack();      // manual acknowledgment
}

// Set outgoing key and headers
@Outgoing("orders")
public Message<Order> produce(Order order) {
    return Message.of(order)
        .addMetadata(OutgoingKafkaRecordMetadata.<String>builder()
            .withKey(order.customerId)
            .withTopic("orders-" + order.region)
            .build());
}
```

### Serialization

```java
// Quarkus-generated deserializer for your type
@io.quarkus.kafka.client.serialization.JsonbDeserializer
public class OrderDeserializer extends JsonbDeserializer<Order> {
    public OrderDeserializer() { super(Order.class); }
}
```

Or use Jackson:
```properties
mp.messaging.incoming.orders.value.deserializer=io.quarkus.kafka.client.serialization.ObjectMapperDeserializer
```

---

## RabbitMQ

### Dependencies

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-reactive-messaging-rabbitmq</artifactId>
</dependency>
```

### Configuration

```properties
# Connection
rabbitmq-host=localhost
rabbitmq-port=5672
rabbitmq-username=guest
rabbitmq-password=guest

# Incoming
mp.messaging.incoming.orders.connector=smallrye-rabbitmq
mp.messaging.incoming.orders.queue.name=order-queue
mp.messaging.incoming.orders.exchange.name=orders-exchange
mp.messaging.incoming.orders.routing-keys=order.placed

# Outgoing
mp.messaging.outgoing.invoices.connector=smallrye-rabbitmq
mp.messaging.outgoing.invoices.exchange.name=invoices-exchange
mp.messaging.outgoing.invoices.default-routing-key=invoice.created
```

### Consuming from RabbitMQ

```java
@ApplicationScoped
public class RabbitOrderConsumer {

    @Incoming("orders")
    public void consume(JsonObject orderJson) {
        Order order = orderJson.mapTo(Order.class);
        process(order);
    }
}
```

---

## Message Acknowledgment

### Automatic Acknowledgment (Default)

```java
@Incoming("orders")
public void consume(Order order) {
    process(order);
    // ack is sent automatically after method returns normally
    // nack is sent if method throws
}
```

### Manual Acknowledgment

```java
@Incoming("orders")
public CompletionStage<Void> consumeWithAck(Message<Order> message) {
    try {
        process(message.getPayload());
        return message.ack();       // acknowledge: remove from queue
    } catch (Exception e) {
        return message.nack(e);     // negative ack: retry or DLQ
    }
}
```

### Acknowledgment Strategies

```properties
# Per-channel ack strategy
mp.messaging.incoming.orders.ack-strategy=post      # default: ack after processing
mp.messaging.incoming.orders.ack-strategy=pre       # ack before processing (at-most-once)
mp.messaging.incoming.orders.ack-strategy=none      # manual only
mp.messaging.incoming.orders.ack-strategy=latest    # batch: ack the latest offset
```

---

## Dead Letter Queue (DLQ)

```properties
# Kafka DLQ
mp.messaging.incoming.orders.dead-letter-queue.topic=orders-dlq
mp.messaging.incoming.orders.failure-strategy=dead-letter-queue

# RabbitMQ DLQ
mp.messaging.incoming.orders.dead-letter-queue.exchange.name=orders-dlq
mp.messaging.incoming.orders.failure-strategy=dead-letter-queue
```

---

## In-Memory Channels (No Broker)

For communicating between beans without a broker:

```java
@ApplicationScoped
public class EventBridge {

    @Channel("internal-events")
    Emitter<Event> emitter;

    public void publish(Event event) {
        emitter.send(event);
    }
}

@ApplicationScoped
public class EventHandler {

    @Incoming("internal-events")
    public void handle(Event event) {
        // no broker; direct bean-to-bean within same JVM
    }
}
```

---

## Health Checks for Messaging

SmallRye Reactive Messaging exposes health automatically:

```
GET /q/health/ready
→ checks that all channels are connected to their brokers
```

---

## Dev UI for Messaging

In dev mode (`http://localhost:8080/q/dev`):
- **Kafka**: browse topics, view messages, publish test messages
- **RabbitMQ**: view exchanges, queues, bindings

---

## Common Patterns

### Batch Processing

```java
@Incoming("orders")
@Outgoing("batched-invoices")
public Multi<List<Order>> batch(Multi<Order> orders) {
    return orders.group().intoLists().of(100, Duration.ofSeconds(5));
}
```

### Fan-Out (One Incoming, Multiple Outgoing)

```java
@Incoming("events")
@Outgoing("type-a-events")
@Outgoing("type-b-events")
public Message<Event> route(Message<Event> message) {
    Event event = message.getPayload();
    String channel = event.type.equals("A") ? "type-a-events" : "type-b-events";
    return message.addMetadata(OutgoingKafkaRecordMetadata.builder()
        .withTopic(channel).build());
}
```

### Filtering

```java
@Incoming("all-orders")
@Outgoing("high-value-orders")
@Acknowledgment(Acknowledgment.Strategy.PRE_PROCESSING)
public Order filter(Order order) {
    if (order.amount < 1000) {
        throw new MessageFilterException(); // filtered out, not forwarded
    }
    return order;
}
```
