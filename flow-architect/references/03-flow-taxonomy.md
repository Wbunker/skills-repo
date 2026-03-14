# A Flow Taxonomy

Reference for classifying event types, understanding producer/consumer roles, choosing between brokers and buses, and understanding event mesh concepts.

---

## Event Type Taxonomy

Urquhart presents a structured taxonomy of event types based on their **semantic purpose** rather than their technical format. Understanding which event type you're working with drives architecture decisions.

### The Four Primary Event Types

#### 1. Notification Events
**Definition**: Signals that something happened, carrying minimal data — just enough to alert consumers that a state change occurred.

Characteristics:
- Small payload — often just an identifier and event type
- Consumer must make a separate call to get full details (if needed)
- Low coupling between producer and consumer
- High fan-out potential — many consumers can react to one notification

Example:
```json
{
  "type": "com.example.order.shipped",
  "id": "evt-12345",
  "source": "/orders/service",
  "time": "2024-01-15T14:23:01Z",
  "datacontenttype": "application/json",
  "data": {
    "orderId": "ord-789"
  }
}
```

Best for:
- Triggering workflows where consumer fetches data from authoritative source
- Cases where the full state is too large or too sensitive to embed in every event
- Simple fan-out notifications (email, push, webhook)

Drawbacks:
- Requires consumer to make an additional API call (reintroduces coupling)
- If the authoritative source is unavailable, consumer cannot process the notification

#### 2. Event-Carried State Transfer (ECST)
**Definition**: Events that carry the complete (or near-complete) state of the changed entity, eliminating the need for consumers to query back.

Characteristics:
- Larger payload — includes all relevant entity fields
- Consumer is self-sufficient to process the event
- Producers must be careful about what to include (avoid over-sharing sensitive data)
- Higher bandwidth requirement

Example:
```json
{
  "type": "com.example.customer.profileUpdated",
  "id": "evt-67890",
  "source": "/customers/service",
  "time": "2024-01-15T14:23:01Z",
  "data": {
    "customerId": "cust-456",
    "email": "new@example.com",
    "name": "Jane Smith",
    "tier": "gold",
    "shippingAddress": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip": "62701"
    },
    "updatedFields": ["email", "shippingAddress"]
  }
}
```

Best for:
- Replication scenarios (downstream replicas of master data)
- Caches and read models that must be kept current
- Eliminating synchronous calls from critical paths

Drawbacks:
- Payload size can be problematic at very high throughput
- Schema evolution complexity (adding/removing fields impacts consumers)
- Sensitive data in events requires careful access control

#### 3. CQRS Events (Command Query Responsibility Segregation)
**Definition**: Events specifically designed to bridge the write model (commands) and read model (queries) in a CQRS architecture. These are the "Q" side materialization events.

Characteristics:
- Represent meaningful business state changes, not technical mutations
- Optimized for the read model's query patterns
- May aggregate multiple domain events into a single denormalized event
- Often produced by an event sourcing system

Example:
```json
{
  "type": "com.example.order.readModelUpdated",
  "id": "evt-11111",
  "data": {
    "orderId": "ord-789",
    "customerId": "cust-456",
    "customerName": "Jane Smith",
    "customerTier": "gold",
    "items": [
      {"sku": "SKU-001", "name": "Widget A", "qty": 2, "price": 29.99}
    ],
    "totalAmount": 59.98,
    "status": "shipped",
    "shippedAt": "2024-01-15T14:23:01Z",
    "estimatedDelivery": "2024-01-18"
  }
}
```

Best for:
- Materializing denormalized views for query optimization
- Decoupling write and read scaling requirements
- Multi-model persistence (write to normalized RDBMS, read from denormalized document store)

#### 4. Request/Reply Events (Asynchronous RPC)
**Definition**: An event-based approximation of synchronous request/response, where the "request" is an event and the "reply" is a correlated response event.

Characteristics:
- Request event includes a `correlationId` or `replyTo` address
- Consumer processes request and publishes a reply to the specified address
- Requester subscribes to its personal reply channel
- Logically synchronous, physically asynchronous

Example:
```json
// Request event
{
  "type": "com.example.creditCheck.requested",
  "id": "evt-req-001",
  "data": {
    "correlationId": "corr-abc123",
    "replyTo": "credit-check-replies.service-a",
    "customerId": "cust-456",
    "requestedAmount": 5000.00
  }
}

// Reply event
{
  "type": "com.example.creditCheck.completed",
  "id": "evt-rep-001",
  "data": {
    "correlationId": "corr-abc123",
    "approved": true,
    "approvedAmount": 5000.00,
    "riskScore": 720
  }
}
```

Best for:
- Long-running processes that shouldn't block HTTP threads
- Request processing that spans service boundaries asynchronously
- Workflows with SLA requirements where a response is guaranteed but timing is flexible

Drawbacks:
- More complex than simple HTTP call
- Requires managing correlation and timeout handling
- Not suited for truly low-latency synchronous interactions

---

## Producers and Consumers

### Producer Patterns

**Domain Event Producer**
The owning service emits events as a side effect of domain operations:
```
OrderService.placeOrder()
  → create order record
  → publish OrderPlaced event
  → return order ID
```
The event is a natural byproduct of the business operation. The service "owns" the event schema.

**Outbox Producer (Transactional)**
Writes the event to a local "outbox" table in the same transaction as the domain operation, then a relay process publishes from the outbox to the event stream:
```
BEGIN TRANSACTION
  INSERT INTO orders ...
  INSERT INTO outbox (event_type, payload) VALUES (...)
COMMIT

-- Separate relay process:
SELECT * FROM outbox WHERE published = false
  → publish to Kafka
  → mark published = true
```
Guarantees exactly-once publishing even if the process crashes mid-operation.

**CDC Producer (Change Data Capture)**
Uses database log shipping (Debezium, AWS DMS) to capture row-level changes as events:
- Does not require application code changes
- Captures all changes including those from legacy applications
- Events are lower-level (table rows) rather than domain events
- Requires transformation layer to produce meaningful business events

**Saga Coordinator Producer**
Emits events to drive multi-step distributed transactions:
```
OrderSagaCoordinator:
  publishes: OrderProcessingStarted
  consumes: InventoryReserved → publishes PaymentRequested
  consumes: PaymentCompleted → publishes OrderConfirmed
  consumes: PaymentFailed → publishes InventoryReleaseRequested
```

### Consumer Patterns

**Competing Consumers (Queue Semantics)**
Multiple instances of the same consumer share a single subscription. Each message is delivered to exactly one instance. Enables horizontal scaling of event processing.
```
OrderShipped events
  → Consumer Group: ShipmentNotificationService
    → Instance 1 (processes event A)
    → Instance 2 (processes event B)
    → Instance 3 (processes event C)
```

**Independent Consumer Groups (Log Semantics)**
Multiple separate consumers each receive all events from the same stream. Each consumer group maintains its own offset/position.
```
OrderShipped events
  → Consumer Group: ShipmentNotificationService (all events)
  → Consumer Group: WarehouseAnalytics (all events)
  → Consumer Group: CarrierIntegration (all events)
```
This is a core differentiator of streaming platforms vs. traditional message queues.

**Event Sourcing Consumer**
Replays the full event log from the beginning to reconstruct current state. Enables:
- Rebuilding read models after bugs
- Creating new read models from historical events
- Audit and compliance queries

**Projection Consumer**
Maintains a materialized view (projection) of aggregated event state:
```
Consumes: OrderPlaced, OrderItemAdded, OrderShipped, OrderDelivered
Maintains: orders table with current status per orderId
Updates: incrementally as each event arrives
```

---

## Brokers vs. Buses vs. Event Logs

### Message Broker
A **message broker** routes and delivers messages between producers and consumers. It is the intermediary:

Characteristics:
- Smart routing (content-based, topic-based, header-based)
- Messages typically deleted after acknowledgment
- Push-based delivery to consumers
- Dead letter queue for failed messages
- Examples: RabbitMQ, ActiveMQ, Amazon SQS

Best for:
- Task queues where each message processed by one consumer
- Routing based on message content
- Point-to-point messaging with delivery guarantees

### Message Bus / Event Bus
A **message bus** is a lighter-weight concept — a shared channel that multiple producers and consumers connect to. Often used within a single application (in-process event bus) or within a single system boundary.

Characteristics:
- Often in-process or local
- No persistence guarantees
- Simple publish/subscribe
- Examples: Spring ApplicationEventPublisher, Guava EventBus, MediatR

Best for:
- Decoupling components within a single service
- Domain event dispatch within a bounded context
- Simple async processing within a monolith

### Event Streaming Log
An **event log** is an append-only, ordered, durable record of events. Consumers read by position (offset):

Characteristics:
- Events persist regardless of consumer state
- Multiple independent consumer groups
- Pull-based consumption at consumer's pace
- Strict ordering within partition
- Examples: Apache Kafka, Apache Pulsar, Amazon Kinesis

Best for:
- Multi-consumer fan-out at scale
- Event replay and reprocessing
- Event sourcing
- Stream processing (joins, aggregations, windowing)

### Comparison Matrix

| Dimension | Message Broker | Message Bus | Event Log |
|---|---|---|---|
| Message retention | Until ACK | None (in-memory) | Configurable (hours to forever) |
| Consumer model | Push | Push/in-process | Pull (consumer-driven) |
| Multiple consumer groups | Complex | Yes (in-process) | Native |
| Ordering | Best effort | In-process order | Per partition |
| Throughput | Medium | High (local) | Very high |
| Replay | No | No | Yes |
| State | Stateful (queues) | Stateless | Stateful (offsets) |
| Best for | Task queues, routing | In-service decoupling | High-throughput multi-consumer |

---

## Event Mesh Concepts

### What Is an Event Mesh?
An **event mesh** is a dynamically routable, highly available infrastructure layer that enables any-to-any event distribution across distributed environments (cloud regions, data centers, edge locations, SaaS platforms).

The event mesh is the "World-Wide Flow" infrastructure vision: a network of interconnected event brokers/streaming nodes that can route events globally based on subscriptions, regardless of where producers or consumers are located.

### Event Mesh Components

**Event Brokers / Nodes**
Individual event brokers (e.g., Solace PubSub+, NATS) that form the mesh. Each node:
- Accepts connections from producers and consumers
- Participates in federated routing with other mesh nodes
- Handles local delivery with low latency

**Dynamic Subscriptions**
Consumers express subscriptions using topic hierarchies or wildcards:
```
# Subscribe to all order events from US region
orders/us/*/placed

# Subscribe to all critical alerts across regions
alerts/*/critical
```
The mesh routes matching events to the subscriber regardless of which node the producer is connected to.

**Bridging and Protocol Translation**
Event meshes often bridge across protocols:
- MQTT devices → AMQP enterprise systems → Kafka streaming platform
- Cloud-to-cloud event routing via webhooks/HTTP adapters
- Legacy MQ systems bridged into the mesh

### Event Mesh vs. Event Streaming Platform

| Dimension | Event Mesh | Event Streaming Platform |
|---|---|---|
| Geographic scope | Multi-region, global | Typically single region/cluster |
| Protocol support | Multi-protocol (MQTT, AMQP, REST) | Kafka/Pulsar native protocol |
| Use case | IoT, edge, distributed enterprise | High-throughput analytics, event sourcing |
| Retention | Short to medium | Long / infinite |
| Topology | Distributed mesh | Centralized cluster |
| Example products | Solace, NATS, HiveMQ | Kafka, Pulsar, Kinesis |

---

## Taxonomy Decision Trees

### Which Event Type Should I Use?

```
Does the consumer need the full entity state to process the event?
├── No → Is this triggering a workflow?
│   ├── Yes → Notification Event
│   └── No (async RPC) → Request/Reply Event
└── Yes → Is this for a CQRS read model?
    ├── Yes → CQRS Event
    └── No → Event-Carried State Transfer
```

### Which Infrastructure Should I Use?

```
Do I need multiple independent consumer groups reading all events?
├── No → Is this task queue (one consumer per message)?
│   ├── Yes → Message Broker (RabbitMQ/SQS)
│   └── No → Message Bus (in-process/EventBridge)
└── Yes → Do I need event replay / reprocessing?
    ├── Yes → Event Streaming Log (Kafka/Pulsar)
    └── No → Topic-based Pub/Sub (SNS/Pub Sub/EventBridge)

Is this cross-region or cross-cloud or IoT at edge?
└── Yes → Consider Event Mesh (NATS/Solace)
```

### Kafka vs. Broker vs. Bus Quick Reference

| Scenario | Recommended |
|---|---|
| Background job processing (one worker per job) | SQS / RabbitMQ |
| Email/SMS notification fan-out | SNS / EventBridge |
| In-service domain event decoupling | In-process event bus |
| Multi-team event sharing at high throughput | Kafka / Pulsar |
| IoT telemetry at edge | MQTT broker → Kafka bridge |
| Event sourcing + audit trail | Kafka / Pulsar |
| Cross-region global event routing | NATS / Solace event mesh |
