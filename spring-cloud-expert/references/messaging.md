---
name: messaging
description: Event-driven architecture with Spring Cloud Stream, binders for Kafka and RabbitMQ, @StreamListener, message channels, consumer groups, partitioning, and event-driven choreography patterns. Chapter 8 of Spring Microservices in Action.
type: reference
---

# Event-Driven Architecture: Spring Cloud Stream

## Why Event-Driven?

Synchronous REST calls create:
- **Temporal coupling** — caller blocks until callee responds
- **Availability coupling** — if B is down, A fails
- **Cascading failures** — slow downstream propagates upstream

Event-driven messaging decouples producers from consumers in time and space. A service publishes an event and continues; consumers process it when ready.

---

## Spring Cloud Stream Concepts

```
┌─────────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Producer Service   │     │    Broker     │     │  Consumer Service   │
│                     │     │  (Kafka /     │     │                     │
│  Source Channel     │────►│  RabbitMQ)   │────►│  Sink Channel       │
│  (output binding)   │     │   Topic /    │     │  (input binding)    │
└─────────────────────┘     │   Exchange   │     └─────────────────────┘
                            └──────────────┘
```

### Core Abstractions
| Abstraction | Role |
|-------------|------|
| **Binder** | Connector to a message broker (Kafka or RabbitMQ) |
| **Channel** | Named logical pipe (decoupled from topic name) |
| **Binding** | Maps a channel to a broker topic/queue |
| **Message** | Payload + headers |

---

## Binder Dependencies

### Kafka
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-stream-kafka</artifactId>
</dependency>
```

### RabbitMQ
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-stream-rabbit</artifactId>
</dependency>
```

---

## Producing Messages (Source)

### Functional Style (Spring Cloud Stream 3.x+)

```java
@SpringBootApplication
public class OrganizationServiceApplication {

    @Bean
    public Supplier<OrganizationChangeModel> sendOrgChangeMessage() {
        return () -> {
            // Called on a schedule or triggered programmatically
            return new OrganizationChangeModel(
                OrganizationChangeModel.ChangeType.UPDATED,
                "org-123",
                UUID.randomUUID().toString()
            );
        };
    }
}
```

### Programmatic Publishing (StreamBridge)

```java
@Service
public class OrganizationService {

    private final StreamBridge streamBridge;

    public OrganizationService(StreamBridge streamBridge) {
        this.streamBridge = streamBridge;
    }

    public Organization updateOrganization(Organization org) {
        Organization saved = orgRepository.save(org);

        OrganizationChangeModel event = new OrganizationChangeModel(
            OrganizationChangeModel.ChangeType.UPDATED,
            org.getId(),
            UUID.randomUUID().toString()
        );
        streamBridge.send("sendOrgChangeMessage-out-0", event);
        return saved;
    }
}
```

### Message Model
```java
public class OrganizationChangeModel {

    public enum ChangeType { CREATED, UPDATED, DELETED }

    private ChangeType changeType;
    private String organizationId;
    private String correlationId;
    private String type;  // Java class name for deserialization

    // constructors, getters, setters...
}
```

---

## Consuming Messages (Sink)

### Functional Style

```java
@SpringBootApplication
public class LicenseServiceApplication {

    @Bean
    public Consumer<OrganizationChangeModel> inboundOrgChanges() {
        return (message) -> {
            logger.debug("Received org change event: type={}, orgId={}",
                message.getChangeType(), message.getOrganizationId());

            switch (message.getChangeType()) {
                case UPDATED -> invalidateOrgCache(message.getOrganizationId());
                case DELETED -> removeOrgFromCache(message.getOrganizationId());
                case CREATED -> {} // No cache action needed
            }
        };
    }
}
```

### Legacy @StreamListener Style (deprecated in 3.x)

```java
@EnableBinding(Sink.class)
@Component
public class OrganizationChangeHandler {

    @StreamListener(Sink.INPUT)
    public void loggerSink(OrganizationChangeModel orgChange) {
        logger.debug("Received message type={}", orgChange.getChangeType());
    }
}
```

---

## Binding Configuration (application.yml)

### Functional Binding Names
Spring Cloud Stream 3.x auto-names bindings: `{functionName}-in-{index}` / `{functionName}-out-{index}`.

```yaml
spring:
  cloud:
    stream:
      bindings:
        inboundOrgChanges-in-0:
          destination: orgChangeTopic          # Kafka topic or RabbitMQ exchange
          content-type: application/json
          group: licenseGroup                  # Consumer group name

        sendOrgChangeMessage-out-0:
          destination: orgChangeTopic
          content-type: application/json

      kafka:
        binder:
          brokers: kafka:9092
          defaultBrokerPort: 9092

      # OR for RabbitMQ:
      rabbit:
        binder:
          addresses: rabbitmq:5672
          username: guest
          password: guest
```

---

## Consumer Groups

Without consumer groups, every running instance of a service receives every message — leading to duplicate processing.

```yaml
spring:
  cloud:
    stream:
      bindings:
        inboundOrgChanges-in-0:
          destination: orgChangeTopic
          group: licenseGroup    # All license-service instances share this group
```

With `group` set:
- Only **one** instance in the group processes each message
- Kafka uses partition assignment; RabbitMQ uses a shared queue per group

---

## Partitioning (Ordering Guarantees)

To guarantee in-order processing for a given key (e.g., all events for org-123 go to the same partition):

**Producer:**
```yaml
spring:
  cloud:
    stream:
      bindings:
        sendOrgChangeMessage-out-0:
          destination: orgChangeTopic
          producer:
            partition-key-expression: payload.organizationId
            partition-count: 3
```

**Consumer:**
```yaml
spring:
  cloud:
    stream:
      bindings:
        inboundOrgChanges-in-0:
          destination: orgChangeTopic
          group: licenseGroup
          consumer:
            partitioned: true
            instance-count: 3
            instance-index: 0    # Set per instance (0, 1, 2)
```

---

## Event-Driven Patterns

### Cache Invalidation on Change Events

```
Organization service → publishes UPDATED event
License service     → receives event → evicts org from Redis cache
                    → next getLicense call re-fetches fresh org data
```

This avoids polling or tight synchronous coupling for cache coherence.

### Saga (Choreography-Based)

```
Order service    → publishes OrderCreated
Inventory service → receives OrderCreated → reserves stock → publishes StockReserved
Payment service  → receives StockReserved → charges card → publishes PaymentConfirmed
Order service    → receives PaymentConfirmed → marks order CONFIRMED
```

Each service reacts to events; no central orchestrator. Failures publish compensating events.

### Outbox Pattern (Reliability)

Problem: saving to DB and publishing to Kafka are not atomic — one can fail.

Solution:
1. Write the event to an `outbox` table in the same DB transaction as the domain write
2. A separate poller reads the outbox table and publishes to Kafka
3. Mark events as published after successful send

---

## Error Handling and Dead Letters

### Retry

```yaml
spring:
  cloud:
    stream:
      bindings:
        inboundOrgChanges-in-0:
          consumer:
            max-attempts: 3
            back-off-initial-interval: 1000
            back-off-multiplier: 2.0
```

### Dead Letter Queue

```yaml
spring:
  cloud:
    stream:
      rabbit:
        bindings:
          inboundOrgChanges-in-0:
            consumer:
              auto-bind-dlq: true
              dlq-ttl: 5000
              republish-to-dlq: true
```

Failed messages (after max-attempts) are routed to `orgChangeTopic.licenseGroup.dlq`.

---

## Message Headers and Correlation IDs

Spring Cloud Stream preserves custom headers. Propagate correlation IDs for tracing:

**Producer:**
```java
Message<OrganizationChangeModel> message = MessageBuilder
    .withPayload(event)
    .setHeader("correlationId", MDC.get("correlationId"))
    .build();
streamBridge.send("sendOrgChangeMessage-out-0", message);
```

**Consumer:**
```java
@Bean
public Consumer<Message<OrganizationChangeModel>> inboundOrgChanges() {
    return (message) -> {
        String correlationId = (String) message.getHeaders().get("correlationId");
        MDC.put("correlationId", correlationId);
        // process...
    };
}
```
