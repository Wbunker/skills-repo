# Integration Patterns — Chapter 9

These patterns solve the problem of reliable, consistent integration across bounded context boundaries. The core challenge: distributed systems cannot guarantee atomic operations across multiple services or data stores. These patterns provide solutions without resorting to distributed transactions (2PC/XA), which are fragile and limit availability.

---

## The Dual-Write Problem

Before diving into patterns, understand the root problem:

```
// DANGEROUS — dual write without atomicity
def confirm_order(order_id):
    order.confirm()
    db.save(order)               # step 1: succeeds
    event_bus.publish(OrderConfirmed(...))  # step 2: fails
    # Result: order confirmed in DB, but downstream never notified
```

If the process crashes between the DB write and the message publish, the system is inconsistent. This is the dual-write problem. All three patterns below address it.

---

## Outbox Pattern

### Problem It Solves
Guarantee that a domain event is published **if and only if** the database transaction commits. Eliminate the dual-write problem for event publishing.

### How It Works
1. **Within the same database transaction**: write the aggregate state AND append the event to an `outbox` table.
2. A **separate process (relay/poller)** reads unpublished events from the outbox and publishes them to the message broker.
3. After successful publishing, mark the event as processed (or delete it).

```
-- Outbox table
CREATE TABLE outbox_events (
    id          UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    event_type  VARCHAR(255) NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    published_at TIMESTAMP  -- NULL = not yet published
);

-- In the application service (single transaction):
BEGIN;
UPDATE orders SET status = 'CONFIRMED' WHERE id = ?;
INSERT INTO outbox_events (id, aggregate_id, event_type, payload, created_at)
VALUES (gen_random_uuid(), ?, 'OrderConfirmed', '...', NOW());
COMMIT;
```

**The relay** (runs continuously or on schedule):
- Queries `outbox_events WHERE published_at IS NULL ORDER BY created_at`.
- Publishes each event to the broker.
- Updates `published_at` on success.

### Implementation Variants

**Polling relay**: simple cron job or background thread that polls the outbox. Works well at lower throughput.

**Transaction log tailing (CDC)**: use Change Data Capture (Debezium, AWS DMS) to capture outbox table inserts from the database transaction log. Zero additional DB load; near-real-time; more infrastructure complexity.

### Guarantees
- **At-least-once delivery**: if the relay crashes after publishing but before marking the event as published, it will republish. Consumers must be **idempotent** (handle duplicate events without side effects).
- **Causal ordering within an aggregate**: events for the same aggregate are published in the order they were created.

### Gotchas
- **Outbox table grows**: purge processed events regularly. Keep enough history for debugging.
- **Consumer idempotency is required**: the outbox guarantees at-least-once, not exactly-once.
- **Relay is a single point of failure** unless made highly available (use multiple relay instances with leader election or Debezium's distributed mode).
- **Polling adds latency**: event delivery is not instantaneous with polling relay. CDC tailing reduces this.

---

## Saga Pattern

### Problem It Solves
Coordinate a long-running, multi-step business process that spans multiple bounded contexts (or aggregates), where each step may fail and needs a compensation strategy to undo completed steps.

### What a Saga Is
A saga is a sequence of local transactions. Each local transaction updates the state of one aggregate (or service) and publishes an event (or sends a command) to trigger the next step. If a step fails, compensating transactions undo the prior steps.

**Key distinction**: sagas do NOT use distributed transactions. Each step commits independently. Consistency is achieved through compensation, not locks.

### Choreography Saga

Each service listens for events and reacts by executing its local transaction and publishing its own event.

```
Order Service:
  ON SubmitOrder → creates order (PENDING) → publishes OrderCreated

Inventory Service:
  ON OrderCreated → reserves stock → publishes StockReserved (or StockReservationFailed)

Payment Service:
  ON StockReserved → charges payment → publishes PaymentCharged (or PaymentFailed)

Order Service:
  ON PaymentCharged → confirms order → publishes OrderConfirmed
  ON PaymentFailed  → cancels order → publishes OrderCancelled

Inventory Service:
  ON OrderCancelled → releases reserved stock (compensation)
```

**When to use choreography**:
- Fewer steps (2–4 participants).
- Low coupling between participants is a priority.
- No complex rollback logic needed.
- Teams are autonomous and don't want a central coordinator.

**Cons**:
- Workflow logic is scattered across services.
- Hard to observe end-to-end saga state.
- Adding a new step requires multiple services to change.
- Cyclic dependencies can develop.

### Orchestration Saga

A central **saga orchestrator** (often implemented as a state machine) drives the workflow by sending commands and handling responses.

```
OrderSaga (Orchestrator):
  State: PENDING_STOCK_RESERVATION
  Step 1: Send ReserveStock command → Inventory Service
          ON StockReserved       → advance to PENDING_PAYMENT
          ON StockReservationFailed → send CancelOrder, advance to CANCELLED

  State: PENDING_PAYMENT
  Step 2: Send ChargePayment command → Payment Service
          ON PaymentCharged      → send ConfirmOrder, advance to COMPLETED
          ON PaymentFailed       → send ReleaseStock, send CancelOrder, advance to CANCELLED
```

**When to use orchestration**:
- Complex workflows with many steps.
- Non-trivial compensation logic.
- Need for centralized observability of saga state.
- Workflow spans many services with varying failure modes.

**Cons**:
- Orchestrator can become a coupling point.
- Requires the orchestrator to be highly available.
- More code to write and maintain.

### Compensating Transactions

A **compensating transaction** semantically undoes the effect of a completed local transaction. It is NOT a technical rollback — the original transaction already committed.

Examples:
- `ReserveStock` → compensated by `ReleaseStock`
- `ChargePayment` → compensated by `RefundPayment`
- `CreateOrder` → compensated by `CancelOrder`

**Design guidance**:
- Not every step is compensatable (e.g., "send email" can't be unsent). For non-compensatable steps, put them last in the sequence so you only reach them when all prior steps have succeeded.
- Compensating transactions may also fail. Plan for this (retry with exponential backoff, dead letter queue, human intervention workflow).
- Idempotency applies here too: a compensation command may be sent more than once.

---

## Process Manager

### How It Differs from a Saga
Both process managers and sagas coordinate multi-step business processes. The distinction:

| | Saga | Process Manager |
|--|------|----------------|
| Triggers | Reacts to events | Reacts to events AND commands |
| State | Per-instance state | Per-instance state + rich domain logic |
| Routing | Routes to next step | Routes to multiple possible paths based on state |
| Complexity | Sequential or simple branching | Complex conditional workflows |
| Boundaries | Usually within one domain | Can span domains; has its own identity |

A **process manager** is essentially a domain object in its own right. It has identity (a process ID), maintains its own state, contains domain logic about what happens next, and can send both commands and events.

```
class OrderFulfillmentProcess:
    def __init__(self, process_id: ProcessId, order_id: OrderId):
        self.id = process_id
        self.order_id = order_id
        self.state = FulfillmentState.AWAITING_PAYMENT
        self.events = []

    def handle_payment_received(self, event: PaymentReceived):
        if self.state != FulfillmentState.AWAITING_PAYMENT:
            return  # idempotent
        self.state = FulfillmentState.AWAITING_SHIPMENT
        self.events.append(InitiateShipment(self.order_id))

    def handle_shipment_failed(self, event: ShipmentFailed):
        if event.retry_count < 3:
            self.events.append(RetryShipment(self.order_id, event.retry_count + 1))
        else:
            self.state = FulfillmentState.FAILED
            self.events.append(RefundOrder(self.order_id))
```

### When to Use Process Manager
- The workflow has complex branching logic that doesn't fit the simple "next step" model of a saga.
- The process spans a long time (days, weeks) and needs durable state.
- The process has its own domain identity and lifecycle (e.g., an insurance claim, a hiring process, a trade settlement).
- You need to correlate events from multiple sources (e.g., "wait for both payment AND inventory confirmation before proceeding").

---

## Pattern Selection Guide

| Scenario | Pattern |
|---------|---------|
| Guarantee event published when DB commits | Outbox |
| Simple multi-step workflow, few services | Choreography Saga |
| Complex multi-step workflow, many services | Orchestration Saga |
| Long-running, stateful business process with complex routing | Process Manager |
| All cross-BC writes | Outbox (always; the foundation for the other patterns) |

### Combining Patterns
These patterns are complementary, not mutually exclusive:
- An **orchestration saga** uses the **outbox** to reliably send its commands.
- A **process manager** uses the **outbox** to reliably publish its output events.
- A **choreography saga** depends on the **outbox** in each participant service to ensure events are reliably published.

The outbox is the foundation. Sagas and process managers sit on top of it.
