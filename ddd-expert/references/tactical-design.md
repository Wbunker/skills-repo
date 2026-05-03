# Tactical Design — Chapters 5–7

Tactical design provides the building blocks for implementing domain logic inside a bounded context. The central question is: **which pattern matches the complexity of this subdomain?** Mismatching the pattern to the complexity is the most common tactical mistake.

---

## Business Logic Patterns Overview

| Pattern | Complexity | State | Typical Subdomain |
|---------|-----------|-------|------------------|
| Transaction Script | Low | Procedural | Generic, simple supporting |
| Active Record | Low-medium | Object + DB row | Supporting |
| Domain Model | High | Rich objects, invariants | Core, complex supporting |
| Event Sourcing | High + temporal | Event log | Core needing audit/replay |

---

## Transaction Script (Chapter 5)

### When to Use
- ETL-style operations: extract data, transform it, save it.
- Simple CRUD with minimal business rules.
- Batch jobs, data migrations, simple integrations.
- Generic subdomains where logic is straightforward.

### Structure
A **transaction script** is a procedure (function or method) that retrieves data from the database, processes it, and writes results back — all within a single transaction. Each use case is one procedure.

```
class OrderReportService:
    def generate_monthly_report(self, month: Month) -> Report:
        rows = self.db.query("SELECT * FROM orders WHERE month = ?", month)
        total = sum(r.amount for r in rows)
        return Report(month=month, total=total, count=len(rows))
```

### Gotchas
- **Transaction scripts grow** — as logic is added, they become god procedures. Watch for duplication across scripts (extract to shared helpers, not a domain model).
- **No invariant protection** — nothing stops invalid state from being written to the DB. Acceptable for simple logic; dangerous for complex logic.
- **Do not mix with domain model** — if you start extracting business rules into objects, migrate to Active Record or Domain Model. Hybrid patterns are hard to maintain.

---

## Active Record (Chapter 5)

### When to Use
- Business objects that map closely to database rows.
- Object graph needs to be navigated, not just rows.
- Business logic exists but is not deeply complex (validation, simple calculations, status transitions).
- Supporting subdomains with moderate logic.

### Structure
An **active record** is an object that wraps a database row and contains business logic that operates on that row. It knows how to save, update, and delete itself (ORM-style: Rails ActiveRecord, Django models, JPA entities used as active records).

```
class Customer:
    def upgrade_to_premium(self):
        if self.total_purchases < 1000:
            raise ValueError("Insufficient purchases for premium")
        self.tier = "PREMIUM"
        self.save()  # active record saves itself
```

### Gotchas
- **Anemic domain model risk** — if you put all logic in services and leave active records as just data, you get an anemic domain model that's neither transaction script nor domain model. Pick one.
- **Persistence concerns leak into domain** — `save()` in business logic couples logic to storage. Acceptable in active record pattern but don't mistake it for a proper domain model.
- **Relationships cause lazy loading traps** — navigating relationships triggers additional queries. Monitor for N+1 problems.

---

## Domain Model (Chapter 6)

The **domain model** pattern is used when business logic is complex enough that a purely procedural approach becomes unmaintainable. It captures business rules in objects that have both state and behavior, protected by invariants.

### Core Building Blocks

#### Entities
- Defined by **identity**, not by attributes.
- The same entity remains the "same" even if attributes change (a Customer is still the same Customer after changing their address).
- Identity is usually a globally unique ID (UUID preferred over sequential IDs — avoids coupling to DB).
- Entities can change over time.

#### Value Objects
- Defined entirely by their **attributes**; no identity.
- **Immutable**: change by replacing, not mutating.
- **Side-effect free**: operations return new value objects.
- Examples: Money, DateRange, EmailAddress, Address, Color, Quantity.

```
# Entity — has identity
class Order:
    def __init__(self, order_id: OrderId):
        self.id = order_id  # identity persists
        self.status = OrderStatus.PENDING

# Value Object — defined by value, immutable
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

**When entity vs. value object?**
- Does the object need to be tracked over time? → Entity
- Is the object equal to another with the same attributes? → Value Object
- Can two instances represent "the same thing" even with identical attributes? → Entity (e.g., two $10 bills are the same value but different physical objects — context determines which abstraction to use)

#### Aggregates

An **aggregate** is a cluster of domain objects (entities + value objects) treated as a single unit for data changes. Every aggregate has one **aggregate root** (an entity) that is the only entry point for external code.

**Aggregate design rules (Vernon + Khononov):**

1. **Protect invariants within a single transaction.** All objects that must be consistent together belong in the same aggregate. One aggregate = one transaction.

2. **Design small aggregates.** Start with the aggregate root and only include what's strictly needed to enforce invariants. Small aggregates = better performance, fewer concurrency conflicts.

3. **Reference other aggregates by ID only.** Never hold an object reference to another aggregate. This enforces transaction boundaries and prevents lazy loading leakage.

4. **Use eventual consistency between aggregates.** If an action must span multiple aggregates, model it as a domain event + reaction (saga or process manager), not a distributed transaction.

**Additional Khononov heuristics:**
- **Named constructors**: use factory methods on the aggregate root, not public constructors, to enforce invariants at creation time.
- **Aggregate invariants in the language**: if you can't state the invariant clearly in the ubiquitous language, you may have the wrong aggregate.
- **Aggregate as consistency boundary**: ask "what must be true together, always?" — that cluster is your aggregate.

```
class Order:  # aggregate root
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id  # reference by ID, not object
        self._lines: list[OrderLine] = []
        self._status = OrderStatus.PENDING
        self._events: list[DomainEvent] = []

    def add_line(self, product_id: ProductId, qty: Quantity, price: Money):
        if self._status != OrderStatus.PENDING:
            raise DomainException("Cannot add line to non-pending order")
        line = OrderLine(product_id, qty, price)  # entity inside aggregate
        self._lines.append(line)

    def confirm(self):
        if not self._lines:
            raise DomainException("Cannot confirm empty order")
        self._status = OrderStatus.CONFIRMED
        self._events.append(OrderConfirmed(self._id, datetime.utcnow()))

    def pop_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

#### Domain Events

A **domain event** records something that happened in the domain. It is:
- **Immutable** — past tense, never changed.
- **Named in the past tense** in the ubiquitous language: `OrderConfirmed`, `PaymentFailed`, `InventoryReserved`.
- **Contains all relevant data** for consumers to act without querying back.

**Design guidance:**
- Include the aggregate ID, timestamp, and enough context for consumers.
- Do NOT include mutable references or lazy-loaded data.
- Raise domain events from the aggregate, not from application services.
- Aggregate collects events internally; application service dispatches them after committing the transaction.

**Domain events vs. integration events:**
- Domain events: internal to the bounded context; rich with domain objects.
- Integration events: cross-context; serialized; use published language (IDs, primitives, strings).

#### Repositories

A **repository** provides the illusion that the domain model works with an in-memory collection of aggregates, hiding all persistence details.

```
class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
```

**Rules:**
- One repository per aggregate root.
- Repository interface belongs to the domain layer; implementation belongs to infrastructure.
- Never expose query methods that leak persistence concerns (no `find_all_with_join()`).
- For complex read needs, use a separate query service or CQRS read model, not the repository.

#### Domain Services

A **domain service** contains domain logic that doesn't naturally belong to any single aggregate or value object.

**When to use:**
- The operation involves multiple aggregates.
- The operation requires infrastructure (e.g., calling an external pricing API), but the logic is domain logic.
- Naming the operation as a method on an aggregate feels forced.

```
class PricingService:  # domain service
    def calculate_order_price(
        self, order: Order, customer: Customer, catalog: ProductCatalog
    ) -> Money:
        # complex pricing logic spanning multiple aggregates
        ...
```

**Domain service vs. application service:**
- Domain service: contains **business logic**; operates on domain objects; has no knowledge of HTTP, message queues, or use case orchestration.
- Application service: orchestrates **use case flow**; calls domain services and aggregates; handles transaction boundaries; has no business logic.

---

## Event Sourcing (Chapter 7)

### What It Is
Instead of persisting the current state of an aggregate, **event sourcing** persists the full sequence of domain events that led to that state. The current state is derived by replaying events.

```
# Instead of storing: { order_id: 1, status: "CONFIRMED", total: 100 }
# Store:
[
  OrderCreated(order_id=1, customer_id=42, ts=...),
  OrderLineAdded(order_id=1, product_id=7, qty=2, price=50, ts=...),
  OrderConfirmed(order_id=1, ts=...)
]
```

### When to Use
- **Audit requirements**: regulators or business need a complete, tamper-evident history (finance, healthcare, legal).
- **Temporal queries**: "What did this order look like on Tuesday?" — impossible with state-based models without additional audit tables.
- **Event replay**: rebuild read models, fix bugs by replaying events with corrected logic.
- **Time travel debugging**: reproduce production bugs by replaying to a specific point.
- **Core subdomains** with high complexity and high value.

### Structure

**Event store**: append-only log. Each event has a stream ID (aggregate ID), sequence number, event type, payload (JSON/Avro), and timestamp. Never update or delete events.

**Projections (read models)**: derived views built by consuming the event stream. A projection handles each event type and updates a read model. Projections can be rebuilt from scratch by replaying events.

**Aggregate reconstitution**: load all events for an aggregate ID, replay them in order to rebuild current state. Optimization: use snapshots (periodically checkpoint state, replay only events after the snapshot).

### Gotchas
- **Schema evolution is hard** — events are immutable. Use upcasting (transform old events to new schema at read time), versioned events, or weak schema (JSON with optional fields).
- **Performance** — reconstituting large aggregates from thousands of events is slow. Use snapshots.
- **Query complexity** — you can't query an event store like a relational DB. All reads go through projections.
- **Eventual consistency** — projections may lag. Design UX and API contracts accordingly.
- **Do not event-source everything** — applying event sourcing to a simple CRUD entity (like a User profile) is engineering waste. Reserve it for aggregates where the event history is genuinely valuable.
- **Deleting data (GDPR)** — immutable events conflict with right-to-erasure requirements. Use crypto-shredding (encrypt PII with a per-user key; delete the key to "erase" the data).

### Comparison: State-Based vs. Event Sourced

| | State-Based | Event Sourced |
|--|------------|--------------|
| Storage | Current state (rows) | Event log (append-only) |
| Query model | SQL on current state | Projections (eventual) |
| History | Lost (or audit table hack) | First-class |
| Schema evolution | ALTER TABLE | Event upcasting |
| Complexity | Lower | Higher |
| Debugging | Limited | Powerful (replay) |
| GDPR | Easy (delete row) | Crypto-shredding needed |
