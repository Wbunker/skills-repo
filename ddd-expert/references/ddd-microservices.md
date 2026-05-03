# DDD and Microservices — Chapter 13

Microservices and DDD are frequently conflated, but they are independent concerns. DDD is about modeling; microservices are about deployment. The relationship is: **DDD helps you find the right service boundaries, but it does not mandate microservices**, and microservices do not require DDD.

---

## The Bounded Context / Microservice Relationship

### The Fundamental Rule
**A bounded context and a microservice are NOT the same thing.** A bounded context defines a model boundary; a microservice is a deployment boundary. One bounded context can be implemented as:
- One microservice
- Multiple microservices (when scale or team independence requires further decomposition within the bounded context)
- A module within a monolith (the "modular monolith")

**What is never valid**: a microservice that spans multiple bounded contexts. This creates a distributed monolith — you get the operational costs of microservices without the architectural benefits of clear boundaries.

### Correct Mapping Options

```
Option A: 1 BC → 1 Microservice (most common, simplest)
  [Ordering BC] → [ordering-service]

Option B: 1 BC → Multiple Microservices (scale-driven decomposition)
  [Ordering BC] → [order-write-service] + [order-query-service]
  (CQRS: command and query sides deployed separately)

Option C: Multiple BCs → 1 Deployable (modular monolith — valid starting point)
  [Catalog BC] + [Inventory BC] → [product-management-service]
  (Extract when team/scale requires it)

Option D: NEVER DO THIS
  [Ordering BC + Payment BC] → [order-payment-service]
  (One service spanning two BCs = distributed monolith)
```

---

## When to Split a BC into Multiple Services

Splitting within a bounded context is an operational/scale decision, not a domain modeling decision. Valid reasons to split:

1. **Independent scalability**: the write path and read path have very different throughput requirements (CQRS → separate deployments).
2. **Independent deployment frequency**: one part of the BC changes daily; another rarely changes. Separate them to avoid coupling release cycles.
3. **Technology requirements**: part of the BC needs GPU processing; part needs low-latency in-memory caching.
4. **Team size**: the team maintaining the BC has grown too large for a single codebase (> 8–10 people). Split along internal module lines.
5. **Fault isolation**: one part of the BC can fail without affecting the other (e.g., search index vs. authoritative order store).

**Warning**: if you split a BC because of performance but haven't actually measured the performance problem, you've created unnecessary operational complexity prematurely.

### When to Keep Services Together (Avoid Premature Decomposition)

- The services would need to share a database to enforce invariants → they belong together.
- Calls between services would be synchronous and chatty → the latency cost outweighs the benefit.
- The same team owns all the services → no deployment independence benefit; just operational overhead.
- The product is in early-stage, requirements are unstable → start as a modular monolith; extract services when boundaries stabilize.

---

## Shared Kernel in Microservices

In a microservices context, the shared kernel pattern is especially dangerous. Sharing code across service boundaries creates coupling that defeats the purpose of separate deployments.

### What "Shared Kernel" Looks Like in Microservices
- A shared library (JAR, npm package, Python package) that multiple services import.
- Shared data structures for integration events.
- A shared database table that multiple services write to.

### Rules for Managing Shared Kernel in Microservices

**Shared library — use for:**
- Technical infrastructure (logging, observability utilities, HTTP client wrappers).
- Published Language schemas (event schemas, API contracts — but treat these as versioned contracts, not shared domain logic).

**Shared library — avoid for:**
- Domain logic. If you put domain logic in a shared library, you've coupled your bounded contexts. Each service must own its own domain model.
- Database ORM models. Each service owns its database schema entirely.

**Shared database — never do this:**
- Two microservices sharing a database table is the most common source of distributed monolith. The services look independent but are structurally coupled at the data layer.
- **Each microservice owns its own database** (Database-per-Service pattern). Share data through APIs and events, not through a shared schema.

---

## Event-Driven Integration Between Microservices

Event-driven integration is the preferred integration style between microservices in a DDD context. It aligns with the **Published Language** and **Open-Host Service** context mapping patterns.

### Integration Events vs. Domain Events

**Domain events** (internal to a service):
- Rich objects with domain types.
- Raised by aggregates; dispatched within the service.
- Never published outside the service boundary in raw form.

**Integration events** (published to the message broker):
- Translated from domain events at the service boundary.
- Contain only IDs, primitives, and serializable types.
- Versioned using additive evolution (never remove fields; deprecate, then remove in a major version).
- Use the Published Language: explicit schema (Avro, Protobuf, JSON Schema).

```
# Domain event (internal)
@dataclass
class OrderConfirmed:
    order: Order  # domain object — never serialize this externally
    confirmed_at: datetime

# Integration event (published to Kafka)
@dataclass
class OrderConfirmedV1:
    order_id: str         # ID, not the object
    customer_id: str
    total_amount: Decimal
    currency: str
    confirmed_at: str     # ISO 8601
    schema_version: str = "1.0"
```

### Event-Driven Integration Patterns in Microservices

**Reliable publishing**: always use the **Outbox pattern** (see integration-patterns.md). Never publish directly to the broker in the same business transaction that updates the database.

**Idempotent consumers**: every event consumer must be idempotent. Deduplicate using the event ID (store processed event IDs in a deduplication table or use idempotency keys).

**Consumer isolation**: each consumer maintains its own read model / projection. Never share a projection between services.

**Event schema governance**: treat integration event schemas as public APIs. Version them, document them, and communicate breaking changes in advance.

---

## Anti-Corruption Layer in Microservices

The ACL is essential when integrating microservices that have different domain models. It prevents one service's model from polluting another's ubiquitous language.

### Implementation in Microservices

**Option 1: ACL in the consumer service**
The consuming service has a translation layer that maps the upstream service's API responses or events into its own domain model.

```
# In OrderService, consuming from InventoryService:
class InventoryServiceAdapter:  # the ACL
    def get_available_stock(self, product_id: ProductId) -> StockLevel:
        response = self.inventory_client.get_stock(str(product_id))
        # translate InventoryService's "quantity_on_hand" → StockLevel value object
        return StockLevel(
            product_id=product_id,
            available=response["quantity_on_hand"] - response["reserved_quantity"]
        )
```

**Option 2: Dedicated translation service (sidecar / proxy)**
For high-volume or complex translations, a separate service or sidecar handles the translation. Common in event-driven architectures where a dedicated adapter service subscribes to upstream events and re-publishes them in the downstream's language.

**Option 3: ACL at the API gateway**
For external third-party APIs, an API gateway or BFF (Backend for Frontend) can perform translation so downstream services never see the external format.

### When ACL Is Critical in Microservices
- Integrating with a legacy monolith being strangler-figged: the ACL is the strangler's protective shell.
- Integrating with third-party services (payment gateways, shipping providers): their models are never your models.
- When one service is a conformist to a poorly designed upstream: add an ACL instead of polluting your model.

---

## Common Microservices + DDD Mistakes

### Mistake 1: Too-Fine-Grained Services (Nanoservices)
**Symptom**: you have a microservice for each database table. Services have only CRUD endpoints. Every business operation requires synchronous calls to 5–10 services.
**Problem**: you've distributed a single transaction across multiple services without any domain modeling benefit. You get all the latency and operational overhead of microservices, none of the autonomy.
**Fix**: use DDD bounded contexts to find the right grain. A service should contain a complete, coherent slice of the domain, not a single table.

### Mistake 2: Distributed Monolith
**Symptom**: services are deployed separately but cannot be deployed independently. Changing service A requires changing service B simultaneously. Services share a database.
**Problem**: you've taken a monolith and added network latency, distributed tracing complexity, and operational overhead without gaining autonomy.
**Fix**: enforce database-per-service. Services communicate through published APIs and events. If two services always change together, merge them.

### Mistake 3: Ignoring Context Mapping
**Symptom**: services call each other directly, passing rich domain objects. No translation layer. Service A's changes to its data model break service B.
**Problem**: tight coupling at the data model level. You've created implicit shared kernels without the governance.
**Fix**: make integration contracts explicit (integration events with schemas, REST/gRPC with versioned contracts). Add ACLs where necessary.

### Mistake 4: Synchronous Integration Everywhere
**Symptom**: every service call is synchronous REST/gRPC. Availability of Service A depends on Services B, C, D, and E.
**Problem**: cascading failures. If payment service is down, order service is down. Latency adds up multiplicatively.
**Fix**: prefer async event-driven integration between bounded contexts. Use synchronous calls only when the caller genuinely needs an immediate response (e.g., getting a price quote before showing it to a user).

### Mistake 5: Premature Microservices
**Symptom**: you split into microservices before the domain model is stable. Bounded context boundaries are guesses at day 1. You refactor service boundaries constantly.
**Problem**: the cost of changing service boundaries in production is enormous (data migration, API versioning, deployment changes).
**Fix**: start with a modular monolith. Enforce bounded context boundaries in code (separate modules, no cross-module direct object sharing) but deploy as one unit. Extract to microservices when boundaries are stable and operational reasons justify it.

---

## Practical Migration from Monolith to Microservices

1. **Run Big Picture EventStorming** on the monolith to discover actual bounded contexts.
2. **Create the context map** — identify which BCs have the most external dependencies (hardest to extract) vs. fewest (easiest to extract).
3. **Modularize first** — enforce bounded context boundaries within the monolith before extracting. Use package/namespace boundaries; forbid direct cross-module imports.
4. **Extract with the strangler fig** — start with the bounded context that:
   - Has the most independent deployment need, OR
   - Is growing fastest and causing the most merge conflicts, OR
   - Has the clearest, most stable boundary
5. **Add ACL during extraction** — protect the new service from the monolith's model.
6. **Establish the outbox pattern** for all integration events from the new service.
7. **Repeat** — one bounded context at a time.

**Rule of thumb**: if you cannot draw the bounded context boundaries before starting the extraction, you are not ready to extract. Do EventStorming and domain modeling first.
