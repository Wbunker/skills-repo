# Flow-Oriented Architecture

Reference for designing systems around flow principles: loose coupling, temporal decoupling, choreography, orchestration, flow contracts, event schema design, and architectural patterns for flow-native systems.

---

## Core Design Principles

### Principle 1: Loose Coupling
Flow-oriented systems decouple producers from consumers in three dimensions:

**Temporal Decoupling**: Producer and consumer do not need to be active simultaneously. The event log or broker serves as the temporal buffer.
```
Producer emits → [Event Log] → Consumer processes (whenever ready)
     T+0                              T+0 to T+∞
```

**Logical Decoupling**: Producer does not know the identity, number, or implementation of its consumers. It emits events; whoever subscribes receives them.

**Deployment Decoupling**: Producers and consumers can be deployed, updated, and scaled independently without coordinated releases.

**How to achieve loose coupling:**
- Never put consumer-specific logic in the producer
- Never have the producer call consumer APIs after emitting an event
- Design events around domain concepts, not consumer needs
- Use schema registries to manage schema evolution independently

### Principle 2: Temporal Decoupling
Design systems to handle consumers that are:
- Temporarily offline (maintenance windows, deployments)
- Processing at different rates than producers
- Processing the same events multiple times (replay)

Implementation requirements:
- **Durable event storage**: Events must persist until all consumers have processed them (or for a defined retention period)
- **Consumer offset management**: Each consumer group tracks its own position in the event log
- **Idempotent consumers**: Processing the same event twice must produce the same result (no duplicate side effects)

### Principle 3: Choreography Over Orchestration
**Orchestration**: A central coordinator tells each service what to do and in what order.
**Choreography**: Services react to events and emit their own events; the workflow emerges from the combination of reactions.

**Orchestration Example** (Saga with central orchestrator):
```
OrderSaga (orchestrator):
  1. Call InventoryService.reserve(orderId, items)
  2. Call PaymentService.charge(orderId, amount)
  3. Call ShippingService.schedule(orderId)
  4. Update order status = CONFIRMED
```
Problems: orchestrator becomes a bottleneck; tight coupling through the orchestrator; hard to evolve independently.

**Choreography Example** (Saga via events):
```
OrderService emits: OrderPlaced {orderId, items, amount}

InventoryService:
  consumes: OrderPlaced
  emits: InventoryReserved {orderId} OR InventoryFailed {orderId, reason}

PaymentService:
  consumes: InventoryReserved
  emits: PaymentCompleted {orderId} OR PaymentFailed {orderId, reason}

ShippingService:
  consumes: PaymentCompleted
  emits: ShipmentScheduled {orderId, trackingId}

OrderService:
  consumes: ShipmentScheduled → update order status = CONFIRMED
  consumes: InventoryFailed, PaymentFailed → compensate
```
Benefits: services are fully autonomous; no central bottleneck; each service can evolve independently.

### Principle 4: Event-First Design
In flow-oriented architecture, the **event schema is the API**. Design the events first, then implement the services.

Event-first design process:
1. Model the business domain as a series of state changes (what happened?)
2. Define the canonical event for each significant state change
3. Determine which service "owns" each event (producer)
4. Identify consumers and what each needs from the event
5. Implement services to produce and consume those events

### Principle 5: Single Source of Truth in the Log
In flow-native systems, **the event log is the source of truth**, not the database. The database (or any other data store) is a derived projection of the event log.

This has significant implications:
- The log is the system of record — any consumer can reconstruct state from events
- Databases are caches of current state, not authoritative stores
- Bugs in consumers can be fixed by replaying events through corrected logic
- New consumers can bootstrap from historical events without migrations

---

## Flow Contracts

### Defining Flow Contracts
A **flow contract** is the formal agreement between an event producer and its consumers. It defines:

1. **Event Schema**: The structure, field names, types, and semantics of the event payload
2. **Delivery Semantics**: What guarantees the producer makes about delivery (at-most-once, at-least-once, exactly-once)
3. **Ordering Guarantees**: Whether events are ordered globally, per-key, or unordered
4. **Versioning Policy**: How the schema will evolve over time and what compatibility guarantees apply
5. **Retention Policy**: How long events are available for replay

### Flow Contract Example (AsyncAPI format)
```yaml
asyncapi: '2.6.0'
info:
  title: Order Events API
  version: '1.0.0'
  description: Events produced by the Order Management Service

channels:
  orders.placed:
    description: Emitted when a customer places a new order
    subscribe:
      message:
        $ref: '#/components/messages/OrderPlaced'

  orders.shipped:
    description: Emitted when an order is handed to carrier
    subscribe:
      message:
        $ref: '#/components/messages/OrderShipped'

components:
  messages:
    OrderPlaced:
      name: OrderPlaced
      contentType: application/json
      payload:
        type: object
        required: [orderId, customerId, items, totalAmount, placedAt]
        properties:
          orderId:
            type: string
            format: uuid
            description: Unique identifier for the order
          customerId:
            type: string
            description: Identifier of the placing customer
          items:
            type: array
            items:
              $ref: '#/components/schemas/OrderItem'
          totalAmount:
            type: number
            format: double
          currency:
            type: string
            default: USD
          placedAt:
            type: string
            format: date-time
```

### Contract Governance
- Event schemas should be versioned in a schema registry (Confluent Schema Registry, AWS Glue, Apicurio)
- Breaking changes require a new major version (new topic/channel) or explicit migration
- Non-breaking changes (adding optional fields) can be deployed with backward-compatible schema evolution
- Consumer teams should be notified of schema changes via a schema change event or catalog

---

## Event Schema Design

### Schema Design Principles

**Include enough context for consumers to act without callbacks**
```json
// Weak schema - consumer must call back to get details
{
  "type": "OrderShipped",
  "orderId": "ord-123"
}

// Strong schema - consumer has what it needs
{
  "type": "OrderShipped",
  "orderId": "ord-123",
  "customerId": "cust-456",
  "customerEmail": "jane@example.com",
  "trackingNumber": "1Z999AA10123456784",
  "carrier": "UPS",
  "estimatedDelivery": "2024-01-18",
  "shippedAt": "2024-01-15T14:23:01Z"
}
```

**Use business keys, not internal database IDs**
- `orderId`, `customerId`, `productId` should be stable business identifiers
- Not database auto-increment IDs that vary by environment

**Carry the time the event occurred, not just when it was processed**
```json
{
  "occurredAt": "2024-01-15T14:23:01.123Z",   // When the business event happened
  "publishedAt": "2024-01-15T14:23:01.456Z"   // When it was put on the stream
}
```

**Use ISO standards for common types**
- Timestamps: ISO 8601 (`2024-01-15T14:23:01.123Z`)
- Amounts: numeric with explicit currency field (never embed currency in amount string)
- Countries: ISO 3166-1 alpha-2 codes
- Languages: BCP 47 tags

**Design for schema evolution from the start**
```json
// Version field enables consumers to handle multiple schema versions
{
  "specversion": "1.0",
  "schemaversion": "2.1.0",
  "type": "com.example.order.placed",
  ...
}
```

### Naming Conventions
Use a reverse-DNS namespace pattern for event types to avoid collisions:
```
com.{company}.{domain}.{entity}.{past-tense-verb}

Examples:
  com.acme.orders.order.placed
  com.acme.inventory.item.reserved
  com.acme.payments.charge.completed
  com.acme.shipping.shipment.dispatched
```

### Schema Evolution Strategies

**Backward-Compatible Changes (Safe)**
- Add new optional fields with defaults
- Add new values to enums (consumers must handle unknown values)
- Add new optional nested objects

**Breaking Changes (Require versioning)**
- Remove fields that consumers depend on
- Rename fields
- Change field types
- Change the semantics of a field

**Evolution Process**:
```
1. Add new field as optional (v1 compatible)
2. Deploy producers to populate new field
3. Update consumers to use new field
4. Once all consumers updated, old field can be deprecated
5. After deprecation window, old field removed in v2
```

---

## Architectural Patterns for Flow-Native Systems

### The Strangler Fig Pattern for Flow Migration
Incrementally migrate a legacy system to flow by:
1. Adding an event producer to the legacy system (via CDC or outbox)
2. Building new consumers that read from the event stream instead of calling the legacy system
3. Gradually routing more and more reads to event-derived stores
4. Decommissioning legacy integration points once consumers are fully migrated

```
Phase 1: Legacy system → [CDC/Outbox] → Event Stream
                                              ↓
                              New consumers read events

Phase 2: Old API calls → New consumers use event-derived data
         (legacy API still exists as fallback)

Phase 3: Legacy integration removed
         Event stream is the integration layer
```

### Event-Driven Microservices Architecture
Each microservice:
- Owns its domain data (no shared databases)
- Publishes events when its domain state changes
- Subscribes to events from other domains it needs
- Maintains its own derived state from subscribed events

```
┌─────────────────────────────────────────────────┐
│                  Event Stream                    │
│  (Kafka/Pulsar topics per domain)               │
└─────┬────────┬────────┬────────┬───────┬────────┘
      │        │        │        │       │
   Orders  Inventory  Payments  Ship   Notify
   Service  Service   Service   Svc    Svc
```

Each service is independently deployable. Communication is exclusively via events — no synchronous service-to-service calls in the core business flows.

### Lambda Architecture (Batch + Speed Layers)
For analytics use cases requiring both historical accuracy and real-time freshness:
```
Raw Events → Batch Layer (Spark/Hadoop): full history, accurate, slow
           → Speed Layer (Kafka Streams/Flink): recent events, fast, approximate
           → Serving Layer: merges batch + speed layer results for queries
```
Note: The Kappa architecture simplifies this by using the event log for both batch reprocessing and streaming, eliminating the separate batch layer.

### Kappa Architecture (Stream-Only)
```
Event Log (Kafka with long retention)
    ↓           ↓
  Real-time   Reprocessing (replay from beginning
  consumers   with new logic when needed)
    ↓                 ↓
  Current state    New derived views
```
Preferred for most flow-native systems where the event log is the source of truth.

### CQRS Architecture with Event Sourcing
```
Write Side:                    Read Side:
Command → Validate          Events → Projector → Read Model
       → Apply domain logic              ↓
       → Emit events                  Query Store
       → Store in event log             (optimized for reads)
```

---

## Anti-Patterns in Flow Architecture

### The Anemic Event
Events that carry only IDs force consumers to make synchronous calls:
```json
// Anemic - consumer must call back
{"type": "OrderShipped", "orderId": "123"}

// Rich - consumer self-sufficient
{"type": "OrderShipped", "orderId": "123", "trackingId": "...", "customerId": "..."}
```

### The God Topic
Putting all events from all services on a single topic/channel:
- No isolation between domains
- All consumers receive all events (filtering overhead)
- Schema evolution impacts all consumers
- Access control is all-or-nothing
**Fix**: One topic per event type or per domain aggregate.

### Tight Schema Coupling
Sharing schema definitions as compiled code (Java classes, protobuf generated code) across service repositories:
- A schema change requires coordinated builds across all consumer repositories
- Defeats the independent deployability benefit of flow
**Fix**: Use a schema registry as the single source of truth. Consumers reference schemas by ID/version, not by importing from producer's codebase.

### Synchronous Fallback Under Pressure
Defaulting to synchronous API calls when event infrastructure is unavailable or slow:
- Creates implicit dependency that undermines the resilience benefits
- Often manifests as "emergency" integrations that become permanent
**Fix**: Design consumers to degrade gracefully when lagging, not fall back to synchronous calls.

### Missing Idempotency
Consumers that produce side effects without checking for duplicate event delivery:
- At-least-once delivery (the common guarantee) means duplicates happen
- Non-idempotent consumers produce duplicate emails, double charges, duplicate records
**Fix**: Every consumer must check: "Have I already processed this event ID?" before applying side effects.

```python
def process_order_shipped(event):
    event_id = event['id']

    # Idempotency check
    if processed_events.contains(event_id):
        logger.info(f"Duplicate event {event_id} - skipping")
        return

    # Process the event
    send_shipping_notification(event['data'])

    # Record as processed (atomically with the side effect if possible)
    processed_events.add(event_id)
```
