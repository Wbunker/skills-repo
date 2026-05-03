# Architectural Patterns — Chapter 8

Architectural patterns govern how the layers of a bounded context are organized and how dependencies flow. The choice of architectural pattern is independent of, but informed by, the tactical pattern used for business logic.

---

## Layered Architecture

### Structure
Three or four layers with a strict dependency rule: **outer layers depend on inner layers; inner layers do not know about outer layers**.

```
┌─────────────────────────────┐
│  Presentation Layer         │  HTTP controllers, CLI, gRPC handlers
├─────────────────────────────┤
│  Application Layer          │  Use cases, application services,
│                             │  command/query handlers, transactions
├─────────────────────────────┤
│  Domain Layer               │  Aggregates, entities, value objects,
│                             │  domain events, domain services,
│                             │  repository interfaces
├─────────────────────────────┤
│  Infrastructure Layer       │  Repository implementations, DB access,
│                             │  message brokers, external APIs
└─────────────────────────────┘

Dependency direction: ↓ (each layer depends on the one below)
Exception: Domain layer has NO dependencies on infrastructure
```

### Rules
- **Domain layer is the core** — it has no dependencies on infrastructure or application layers.
- **Application layer** orchestrates use cases; it calls domain objects and infrastructure interfaces; it owns transaction boundaries.
- **Infrastructure layer** implements interfaces defined in the domain layer (Dependency Inversion Principle).
- **Presentation layer** maps HTTP/gRPC/message inputs to application service commands and queries.

### When to Use
- Default choice for bounded contexts with moderate complexity.
- Works well with Active Record and Domain Model patterns.
- Clear separation when teams are split by layer.

### Gotchas
- **Leaky abstractions**: infrastructure concerns (ORM annotations, serialization attributes) bleeding into domain objects.
- **Fat application services**: business logic migrating from the domain into application services, producing an anemic domain model.
- **Circular dependencies** between layers are a symptom of wrong layer placement.

---

## Ports and Adapters (Hexagonal Architecture)

### Structure
The application core (domain + application layers) is surrounded by **ports** (interfaces) and **adapters** (implementations). There are two types of ports:

```
                    ┌──────────────────────────────┐
  HTTP Request ─────► Driving Adapter              │
  gRPC Call    ─────► (Controller, CLI, Test)      │
  Message      ─────►                              │
                    │  ┌────────────────────────┐  │
                    │  │  Application Core      │  │
                    │  │  (Domain + App Layer)  │  │
                    │  │                        │  │
                    │  │  Driving Ports         │  │
                    │  │  (Use Case Interfaces) │  │
                    │  │                        │  │
                    │  │  Driven Ports          │  │
                    │  │  (Repo Interfaces,     │  │
                    │  │   Email Port, etc.)    │  │
                    │  └────────────────────────┘  │
                    │              │               │
                    │  Driven Adapters             │
                    │  (DB Repo, Email, S3)   ─────►  DB, Email, S3
                    └──────────────────────────────┘
```

**Driving (primary) ports and adapters**: things that drive the application (HTTP, CLI, test harness). The adapter calls the application's use case interface (driving port).

**Driven (secondary) ports and adapters**: things the application drives (database, email, message broker). The application calls the port (interface); the adapter implements it.

### Benefits
- **Testability**: swap driven adapters with in-memory fakes during tests. No database needed for unit tests.
- **Replaceability**: swap from PostgreSQL to DynamoDB by writing a new driven adapter.
- **Technology independence**: the domain core knows nothing about HTTP, SQL, or message formats.

### When to Use
- Domain Model tactical pattern — the business logic is valuable enough to protect from infrastructure concerns.
- When testability of business logic is a priority.
- Long-lived systems likely to change infrastructure (cloud migrations, database changes).

### Gotchas
- **Over-engineering for simple cases**: Transaction Script or Active Record don't need the full ports-and-adapters treatment.
- **Too many small interfaces**: every external concern doesn't need its own port. Group related capabilities.
- **Port-leaking**: if a port interface returns infrastructure types (e.g., `ResultSet`, `HttpResponse`), it's not a real port.

---

## CQRS (Command Query Responsibility Segregation)

### Concept
Separate the model used for writes (**command model**) from the model used for reads (**query model**). Commands change state; queries return data. They use different models, and often different data stores.

```
         Commands                        Queries
    ┌──────────────┐               ┌──────────────┐
    │ Command      │               │ Query        │
    │ Handler      │               │ Handler      │
    └──────┬───────┘               └──────┬───────┘
           │                              │
    ┌──────▼───────┐               ┌──────▼───────┐
    │ Domain       │               │ Read Model   │
    │ Model        │               │ (Projection) │
    │ (Aggregates) │               │              │
    └──────┬───────┘               └──────┬───────┘
           │                              │
    ┌──────▼───────┐               ┌──────▼───────┐
    │ Write Store  │──domain evt──►│ Read Store   │
    │ (normalized  │               │ (denormalized│
    │  relational) │               │  for queries)│
    └──────────────┘               └──────────────┘
```

### When to Use
- **Read/write ratio is heavily skewed toward reads** — optimize each side independently.
- **Query complexity** — the normalized write model requires expensive joins for read use cases.
- **Event sourcing** — the event store is the write model; projections are the read models. CQRS and event sourcing are often paired.
- **Scalability** — read and write sides can be scaled independently.

### Projections
A **projection** is a read model built by consuming domain events. Each event handler updates a denormalized view optimized for a specific query. Projections can be:
- **Synchronous** (same transaction as the command): simple, consistent, but couples read/write performance.
- **Asynchronous** (event consumer updates read store): eventually consistent; decoupled; enables multiple independent projections.

### Eventual Consistency Tradeoffs
- After a command, the read model may not immediately reflect the change.
- Design UX to handle this: optimistic UI updates, "pending" states, explicit consistency indicators.
- Set expectations: "Your order has been placed. It may take a moment to appear in your order history."
- For operations that require immediate consistency (e.g., showing the user what they just submitted), return data from the command response, not from the read model.

### When NOT to Use
- Simple CRUD applications — the overhead of two models is waste.
- When eventual consistency is unacceptable for the use case.
- Small teams without the capacity to maintain two models.

### Gotchas
- **Projection drift**: projections can get out of sync if events are lost or out of order. Use event sourcing + replay to recover.
- **No transactions across command and query stores**: you cannot update both atomically. Embrace eventual consistency.
- **Over-applying CQRS**: not every aggregate needs separate read models. Use CQRS selectively for complex query use cases.

---

## Event-Driven Architecture

### Event Types

**Domain events** (internal to a bounded context):
- Raised by aggregates.
- Rich with domain objects and value objects.
- Used to trigger side effects within the same bounded context (e.g., update a projection, send a notification).
- Not published externally in raw form.

**Integration events** (crossing bounded context boundaries):
- Serialized, schema-versioned messages.
- Contain IDs and primitives, not domain objects.
- Published via message broker (Kafka, RabbitMQ, SNS/SQS).
- Correspond to the **Published Language** context mapping pattern.

### Choreography vs. Orchestration

**Choreography** (event-driven / reactive):
```
Order Service     ─── OrderConfirmed ───►  Inventory Service
                                           (reacts: reserves stock)
                  ◄── StockReserved ──────
                                           Payment Service
                  ─── PaymentRequired ──► (reacts: charges card)
```
- No central coordinator.
- Services react to events from other services.
- **Pros**: loose coupling, high autonomy, easy to add new consumers.
- **Cons**: workflow logic is distributed; hard to observe end-to-end state; hard to handle compensation.

**Orchestration** (explicit coordinator):
```
Order Saga (Orchestrator)
  ├── → ReserveInventory command → Inventory Service
  ├── ← InventoryReserved event
  ├── → ChargePayment command → Payment Service
  ├── ← PaymentCharged event
  └── → ConfirmOrder command → Order Service
```
- A central process manager or saga coordinates the workflow.
- **Pros**: workflow logic is explicit and visible; easier to handle compensation; easier to monitor.
- **Cons**: coordinator becomes a coupling point; potential single point of failure.

### Which Pattern for Which Bounded Context Type?

| Subdomain Type | Recommended Pattern |
|----------------|---------------------|
| Core | Ports & Adapters + CQRS (if read complexity warrants) |
| Supporting | Layered Architecture (or Ports & Adapters) |
| Generic | Layered or Transaction Script with minimal architecture |
| Event-sourced core | Ports & Adapters + CQRS + Event-Driven |

### Gotchas
- **Dual-write problem**: writing to the database AND publishing an event in separate operations risks inconsistency. Use the **Outbox pattern** (see integration-patterns.md).
- **Event ordering**: distributed message brokers don't guarantee global order. Design consumers to be idempotent.
- **Schema evolution**: integration events are public contracts. Version carefully; never remove fields; use additive changes.
- **Event overload**: publishing every domain event as an integration event creates tight coupling. Publish only what consumers genuinely need.
