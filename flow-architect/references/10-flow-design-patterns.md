# Flow Design Patterns

Reference for event sourcing, CQRS, saga pattern (choreography vs. orchestration), outbox pattern, inbox pattern, competing consumers, event-carried state transfer, claim check pattern, and event replay.

---

## Event Sourcing

### What Is Event Sourcing?
Event sourcing is an architectural pattern where **the system's state is derived by replaying a sequence of events** rather than storing and updating current state in a database.

Traditional persistence:
```
User → Service → UPDATE orders SET status='shipped' WHERE id='123'
                 (only current state preserved)
```

Event sourcing:
```
User → Service → APPEND {type: OrderShipped, orderId: '123', timestamp: ...} to event log
                 (full history preserved; current state computed from events)
```

### The Event Store
An event store is the append-only persistence layer for event sourcing. Each aggregate (e.g., an Order) has its own stream of events:

```
Stream: Order-123
  [0] OrderCreated    {orderId: '123', customerId: 'cust-456', items: [...]}
  [1] PaymentReceived {orderId: '123', amount: 59.98, paymentId: 'pay-789'}
  [2] OrderShipped    {orderId: '123', trackingId: '1Z999...', carrier: 'UPS'}
  [3] OrderDelivered  {orderId: '123', deliveredAt: '2024-01-18T10:00:00Z'}

Stream: Order-124
  [0] OrderCreated    {orderId: '124', ...}
  [1] OrderCancelled  {orderId: '124', reason: 'customer_requested', ...}
  [2] RefundIssued    {orderId: '124', amount: 29.99, ...}
```

### Event-Sourced Aggregate Implementation

```python
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = None
        self.items = []
        self.total_amount = 0
        self.version = 0
        self._uncommitted_events = []

    @classmethod
    def from_events(cls, order_id: str, events: list) -> 'Order':
        """Reconstruct aggregate state by replaying events"""
        order = cls(order_id)
        for event in events:
            order._apply(event)
        return order

    def place(self, customer_id: str, items: list):
        """Command: raises events, does not mutate state directly"""
        if self.status is not None:
            raise ValueError("Order already placed")
        total = sum(item['price'] * item['qty'] for item in items)
        self._raise_event({
            'type': 'OrderPlaced',
            'orderId': self.order_id,
            'customerId': customer_id,
            'items': items,
            'totalAmount': total
        })

    def ship(self, tracking_id: str, carrier: str):
        if self.status != 'confirmed':
            raise ValueError(f"Cannot ship order in status {self.status}")
        self._raise_event({
            'type': 'OrderShipped',
            'orderId': self.order_id,
            'trackingId': tracking_id,
            'carrier': carrier
        })

    def _raise_event(self, event: dict):
        """Stage event for commit; apply immediately"""
        self._uncommitted_events.append(event)
        self._apply(event)

    def _apply(self, event: dict):
        """Mutate state from event — must be pure, no side effects"""
        if event['type'] == 'OrderPlaced':
            self.status = 'pending'
            self.items = event['items']
            self.total_amount = event['totalAmount']
            self.version += 1
        elif event['type'] == 'OrderShipped':
            self.status = 'shipped'
            self.version += 1
        # ... handle other event types

    def commit(self, event_store):
        """Persist uncommitted events to the event store"""
        for event in self._uncommitted_events:
            event_store.append(f"Order-{self.order_id}", event, expected_version=self.version)
        self._uncommitted_events.clear()
```

### Snapshots
For aggregates with very long event histories, replaying all events becomes slow. Snapshots periodically capture current state to short-circuit replay:

```python
# Take snapshot every 100 events
if order.version % 100 == 0:
    snapshot_store.save({
        'order_id': order.order_id,
        'version': order.version,
        'snapshot_at': datetime.utcnow().isoformat(),
        'state': order.to_dict()
    })

# Restore from snapshot + subsequent events
snapshot = snapshot_store.get_latest('Order-123')
order = Order.from_snapshot(snapshot)
events_after = event_store.get_events('Order-123', after_version=snapshot['version'])
for event in events_after:
    order._apply(event)
```

### Event Sourcing Benefits and Trade-offs

| Benefit | Trade-off |
|---|---|
| Complete audit trail | Query complexity (requires projections) |
| Time-travel queries | Event schema evolution complexity |
| Bug recovery (replay with fix) | Performance (replay latency for large streams) |
| Natural event integration (events already exist) | Developer mindset shift |
| Optimistic concurrency built-in | Eventual consistency |

---

## CQRS (Command Query Responsibility Segregation)

### CQRS Concept
CQRS separates the **write model** (commands that change state) from the **read model** (queries that return state). In flow systems, events connect the two sides:

```
Write Side                         Read Side
─────────                         ─────────
Command ─→ Command Handler        Events ─→ Event Handler ─→ Read Store
           │                                                  │
           ▼                                                  ▼
       Aggregate                                         Read Model
           │                                           (denormalized,
           ▼                                            query-optimized)
       Event Store ──────────────────────────────────────────►
       (write store)         (events flow to read side)
```

### When to Use CQRS
Use CQRS when:
- Read and write throughput/scaling requirements differ significantly
- Query shapes are very different from write shapes (normalization vs. denormalization)
- Multiple read models are needed for the same data (reporting, API, search)
- Event sourcing is already in use (natural pairing)

Don't use CQRS for:
- Simple CRUD applications with straightforward read/write patterns
- Teams without event-driven experience (high learning curve)
- Low traffic systems where complexity isn't justified

### CQRS Read Model Projections

```python
class OrderSummaryProjection:
    """Read model: denormalized order summary for API queries"""

    def __init__(self, db: ReadModelDatabase):
        self.db = db

    def handle_order_placed(self, event: dict):
        self.db.upsert('order_summaries', {
            'order_id': event['orderId'],
            'customer_id': event['customerId'],
            'status': 'pending',
            'total_amount': event['totalAmount'],
            'item_count': len(event['items']),
            'placed_at': event['occurredAt']
        })

    def handle_order_shipped(self, event: dict):
        self.db.update('order_summaries',
            where={'order_id': event['orderId']},
            set={
                'status': 'shipped',
                'tracking_id': event['trackingId'],
                'carrier': event['carrier'],
                'shipped_at': event['occurredAt']
            }
        )

    def handle_order_delivered(self, event: dict):
        self.db.update('order_summaries',
            where={'order_id': event['orderId']},
            set={'status': 'delivered', 'delivered_at': event['occurredAt']}
        )
```

---

## Saga Pattern

### What Is a Saga?
A saga is a pattern for managing distributed transactions across multiple services. Each service performs its local transaction and publishes an event. If a step fails, compensating transactions are executed to undo previous steps.

### Choreography-Based Saga
Services react to events and emit their own events. No central coordinator.

```
OrderService ──publishes──► OrderPlaced
                                │
InventoryService ─consumes──────┘
InventoryService ──publishes──► InventoryReserved (success)
                             OR InventoryReservationFailed (failure)
                                │
PaymentService ─consumes────────┘ (only consumes InventoryReserved)
PaymentService ──publishes──► PaymentCompleted (success)
                           OR PaymentFailed (failure)
                                │
OrderService ─consumes──────────┘
  - PaymentCompleted → emit OrderConfirmed
  - PaymentFailed → emit CompensationRequired
                                │
InventoryService ─consumes──────┘ (CompensationRequired)
InventoryService ──publishes──► InventoryReleased
```

**Choreography advantages**:
- Fully decentralized
- Each service independently deployable
- No single point of failure

**Choreography disadvantages**:
- Hard to visualize and debug the overall flow
- Difficult to determine if saga is in a consistent state
- Cyclic dependencies can emerge

### Orchestration-Based Saga
A central saga orchestrator coordinates the steps, calling each service and handling responses.

```python
class OrderProcessingSaga:
    """Orchestrator-based saga for order processing"""

    def __init__(self, inventory_client, payment_client, event_publisher):
        self.inventory = inventory_client
        self.payment = payment_client
        self.publisher = event_publisher

    async def execute(self, order: Order) -> SagaResult:
        saga_id = str(uuid4())

        # Step 1: Reserve inventory
        try:
            reservation = await self.inventory.reserve(
                saga_id=saga_id,
                order_id=order.id,
                items=order.items
            )
        except InventoryError as e:
            await self.publisher.emit('OrderFailed', {
                'orderId': order.id,
                'reason': str(e)
            })
            return SagaResult.FAILED

        # Step 2: Process payment
        try:
            payment = await self.payment.charge(
                saga_id=saga_id,
                order_id=order.id,
                amount=order.total_amount,
                payment_method=order.payment_method
            )
        except PaymentError as e:
            # Compensate: release reserved inventory
            await self.inventory.release(saga_id=saga_id, reservation_id=reservation.id)
            await self.publisher.emit('OrderFailed', {
                'orderId': order.id,
                'reason': str(e)
            })
            return SagaResult.FAILED

        # All steps succeeded
        await self.publisher.emit('OrderConfirmed', {
            'orderId': order.id,
            'reservationId': reservation.id,
            'paymentId': payment.id
        })
        return SagaResult.COMPLETED
```

**Orchestration advantages**:
- Explicit, visualizable workflow
- Easier to add/remove steps
- Centralized saga state tracking
- Easier debugging (one place to look)

**Orchestration disadvantages**:
- Orchestrator can become a bottleneck
- Orchestrator coupled to all participating services
- Single point of failure (unless orchestrator itself is highly available)

### Saga Decision Framework

| Factor | Use Choreography | Use Orchestration |
|---|---|---|
| Team autonomy | High | Low |
| Number of steps | Few (2-3) | Many (5+) |
| Compensation complexity | Simple | Complex |
| Visibility/debugging needs | Low | High |
| Cross-team coordination | Minimal | Significant |
| Services are owned by same team | No | Yes |

---

## Outbox Pattern

### The Dual-Write Problem
When a service must atomically update its database AND publish an event, it faces the dual-write problem:

```
# Dangerous: NOT atomic — what if step 2 fails?
db.save(order)           # Step 1: write to database
kafka.publish(event)     # Step 2: publish event

# Order saved but event never published → inconsistency
```

### Outbox Solution
Write the event to an "outbox" table in the same database transaction as the domain data. A separate relay process reads from the outbox and publishes to the event stream.

```python
# Step 1: Write domain data + outbox event in one transaction
with db.transaction():
    db.execute("INSERT INTO orders VALUES (...)")
    db.execute("""
        INSERT INTO outbox (id, event_type, aggregate_id, payload, created_at, published)
        VALUES (?, ?, ?, ?, ?, false)
    """, (str(uuid4()), 'OrderPlaced', order_id, json.dumps(event), datetime.utcnow()))
# Transaction commits: both order and outbox entry saved atomically

# Step 2: Relay process (separate process/thread)
def relay_outbox():
    while True:
        events = db.execute("""
            SELECT * FROM outbox
            WHERE published = false
            ORDER BY created_at
            LIMIT 100
            FOR UPDATE SKIP LOCKED
        """)
        for event in events:
            kafka.produce(
                topic=event['event_type'].lower(),
                key=event['aggregate_id'],
                value=event['payload']
            )
            db.execute("UPDATE outbox SET published = true WHERE id = ?", event['id'])
        time.sleep(0.1)
```

### Outbox with Change Data Capture
Instead of a polling relay, use CDC (Debezium) to capture outbox changes from the database transaction log:

```json
// Debezium Outbox Event Router configuration
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "transforms": "outbox",
  "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
  "transforms.outbox.table.field.event.id": "id",
  "transforms.outbox.table.field.event.key": "aggregate_id",
  "transforms.outbox.table.field.event.type": "event_type",
  "transforms.outbox.table.field.event.payload": "payload",
  "transforms.outbox.route.topic.replacement": "outbox.event.${routedByValue}"
}
```

CDC-based outbox eliminates polling latency and is more efficient than polling.

---

## Inbox Pattern

### What Is the Inbox Pattern?
The inbox pattern is the consumer-side complement to the outbox. It provides idempotent event processing by recording received events before processing:

```python
def process_event(event: dict):
    event_id = event['id']

    # Check inbox first (idempotency check)
    with db.transaction():
        existing = db.execute(
            "SELECT id FROM inbox WHERE event_id = ?", event_id
        ).fetchone()

        if existing:
            logger.info(f"Event {event_id} already processed, skipping")
            return

        # Record in inbox BEFORE processing
        db.execute(
            "INSERT INTO inbox (event_id, event_type, received_at) VALUES (?, ?, ?)",
            event_id, event['type'], datetime.utcnow()
        )

    # Process the event (outside transaction to allow retry if processing fails)
    try:
        apply_event_to_domain(event)

        # Mark as successfully processed
        db.execute(
            "UPDATE inbox SET processed_at = ?, status = 'success' WHERE event_id = ?",
            datetime.utcnow(), event_id
        )
    except Exception as e:
        db.execute(
            "UPDATE inbox SET status = 'failed', error = ? WHERE event_id = ?",
            str(e), event_id
        )
        raise  # Re-raise to trigger retry
```

---

## Competing Consumers

### Pattern
Multiple instances of the same consumer share a partitioned topic or queue. Each event is processed by exactly one consumer instance. Enables horizontal scaling of event processing.

**Kafka Competing Consumers**:
```python
# All instances share the same group_id
# Kafka assigns partitions across instances
consumer = KafkaConsumer(
    'order-events',
    group_id='order-fulfillment-service',    # Shared group ID
    bootstrap_servers=['kafka:9092'],
    max_poll_records=50                       # Process 50 events per poll
)

# Each instance processes events from its assigned partitions only
for message in consumer:
    process_order_event(message.value)
    consumer.commit()
```

**Scaling**: Adding instances causes Kafka to rebalance partition assignments. Scale up during high load, scale down during off-peak.

**Consumer Group Lag**: Monitor lag per consumer group to determine if additional instances are needed.

---

## Claim Check Pattern

### Problem
Large payloads (images, documents, large JSON) in events:
- Increase message storage costs in the broker
- Slow down producer (waiting for large message acknowledgment)
- Cause consumer memory pressure
- Create issues with broker message size limits (Kafka default max: 1MB)

### Solution
Store the large payload in external storage; include only a reference (claim check) in the event:

```python
def publish_document_processed_event(order_id: str, document: bytes) -> None:
    # Store document in S3
    document_key = f"documents/{order_id}/{str(uuid4())}.pdf"
    s3.put_object(
        Bucket='document-store',
        Key=document_key,
        Body=document,
        ServerSideEncryption='AES256'
    )

    # Publish event with claim check (reference only)
    event = {
        "specversion": "1.0",
        "type": "com.acme.documents.document.processed",
        "id": str(uuid4()),
        "source": "https://documents.acme.com",
        "time": datetime.utcnow().isoformat() + "Z",
        "data": {
            "orderId": order_id,
            "documentRef": {               # Claim check
                "uri": f"s3://document-store/{document_key}",
                "contentType": "application/pdf",
                "sizeBytes": len(document),
                "expiresAt": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        }
    }
    kafka.produce('document-events', value=json.dumps(event))

def consume_document_event(event: dict) -> None:
    # Consumer retrieves document using claim check
    doc_ref = event['data']['documentRef']
    bucket, key = parse_s3_uri(doc_ref['uri'])
    document = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    # Process document...
```

The CloudEvents `dataref` extension formalizes this pattern with a standard attribute.

---

## Event-Carried State Transfer (ECST)

### Pattern
Events carry the full current state of the entity, enabling consumers to maintain their own read models without querying the producer:

```json
{
  "type": "com.acme.customers.customer.profileUpdated",
  "id": "evt-12345",
  "data": {
    "customerId": "cust-789",
    "email": "new@example.com",
    "name": "Jane Smith",
    "tier": "gold",
    "loyaltyPoints": 1250,
    "updatedAt": "2024-01-15T14:23:01Z",
    "updatedFields": ["email"]             // Hints about what changed
  }
}
```

**Consumer**: Maintains a local customer table, updated directly from events:
```python
def handle_customer_profile_updated(event):
    db.execute("""
        INSERT INTO customers (id, email, name, tier, loyalty_points, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
            email = excluded.email,
            name = excluded.name,
            tier = excluded.tier,
            loyalty_points = excluded.loyalty_points,
            updated_at = excluded.updated_at
    """, event['customerId'], event['email'], event['name'],
         event['tier'], event['loyaltyPoints'], event['updatedAt'])
```

**Result**: Consumer is never blocked by Producer API being slow or unavailable.

---

## Event Replay

### When to Use Event Replay
- **Bug fix recovery**: Consumer had a bug and processed events incorrectly — replay to reprocess correctly
- **New consumer onboarding**: A new service needs historical events to build its initial state
- **Read model rebuild**: After schema change, rebuild a projection from scratch
- **Audit queries**: Answer "what was the state of X at time T?"

### Kafka Replay Mechanics
```python
# Reset consumer group offset to beginning for replay
from kafka.admin import KafkaAdminClient
from kafka import TopicPartition

admin = KafkaAdminClient(bootstrap_servers=['kafka:9092'])

# Reset to beginning of all partitions
admin.alter_consumer_group_offsets(
    'shipment-service',
    {
        TopicPartition('orders-placed', partition): OffsetAndMetadata(0, None)
        for partition in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    }
)

# Or replay from specific timestamp
offsets_for_times = consumer.offsets_for_times({
    TopicPartition('orders-placed', p): int(datetime(2024, 1, 1).timestamp() * 1000)
    for p in range(12)
})
```

### Replay Safety Considerations
- **Idempotent consumers**: Essential — events will be processed twice (original + replay)
- **External side effects**: Suppress side effects during replay (don't re-send emails, don't re-charge customers)
- **Ordering**: Replay in order; parallel replay across partitions requires careful state management
- **Performance**: Replay can produce high load — use separate consumer group with throttled processing during replay

```python
REPLAY_MODE = os.getenv('REPLAY_MODE', 'false').lower() == 'true'

def process_order_shipped(event):
    update_order_status_in_db(event)    # Idempotent: always safe

    if not REPLAY_MODE:
        send_shipping_notification(event)  # Side effect: skip during replay
        notify_carrier_system(event)       # External call: skip during replay
```
