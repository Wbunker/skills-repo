# Flow Operations

Reference for observability (distributed tracing for events, correlation IDs), schema evolution and compatibility, consumer lag monitoring, backpressure handling, exactly-once vs. at-least-once trade-offs, and operational runbooks.

---

## Observability in Flow Systems

### The Observability Challenge
Traditional observability tools are designed for synchronous request/response. Event-driven systems break the synchronous call chain:

```
HTTP Request: Client → API → ServiceA → ServiceB → Response
  (easy to trace: single thread, correlated spans)

Event-driven: Producer → Kafka → ConsumerA → Kafka → ConsumerB → ???
  (hard to trace: multiple processes, multiple topics, async by nature)
```

The three pillars of observability must be extended for events:
- **Traces**: Correlated spans across producer → broker → consumer boundaries
- **Metrics**: Event throughput, consumer lag, processing time, error rates
- **Logs**: Structured logs with correlation IDs linking events across services

### Distributed Tracing for Events

**W3C Trace Context in Events**
The W3C Trace Context standard (`traceparent`, `tracestate`) can be carried as CloudEvents extensions:

```json
{
  "specversion": "1.0",
  "type": "com.acme.orders.order.placed",
  "id": "evt-12345",
  "source": "https://orders.acme.com",
  "time": "2024-01-15T14:23:01.123Z",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "tracestate": "acme=1,vendor=xyz",
  "data": {"orderId": "ord-123"}
}
```

Format: `traceparent = {version}-{trace-id}-{parent-span-id}-{flags}`
- `version`: always `00`
- `trace-id`: 16-byte globally unique trace ID (hex)
- `parent-span-id`: 8-byte span ID of the producing span
- `flags`: bit flags (01 = sampled)

**Producer Span Creation**:
```python
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer("orders-service")

def publish_order_placed(order: Order):
    with tracer.start_as_current_span("publish.order.placed") as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.destination", "orders-placed")
        span.set_attribute("order.id", order.id)

        # Inject trace context into event headers/extensions
        carrier = {}
        inject(carrier)  # Adds traceparent, tracestate

        event = {
            "specversion": "1.0",
            "type": "com.acme.orders.order.placed",
            "id": str(uuid4()),
            "traceparent": carrier.get("traceparent"),
            "tracestate": carrier.get("tracestate"),
            "data": order.to_dict()
        }
        kafka.produce("orders-placed", value=json.dumps(event))
```

**Consumer Span Creation**:
```python
from opentelemetry.propagate import extract

def consume_order_placed(message):
    # Extract trace context from event
    event = json.loads(message.value)
    carrier = {
        "traceparent": event.get("traceparent"),
        "tracestate": event.get("tracestate")
    }
    ctx = extract(carrier)  # Restore trace context

    # Start a new span as child of the producer's span
    with tracer.start_as_current_span(
        "process.order.placed",
        context=ctx,
        kind=trace.SpanKind.CONSUMER
    ) as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.kafka.consumer.group", "shipment-service")
        span.set_attribute("messaging.kafka.partition", message.partition)
        span.set_attribute("messaging.kafka.offset", message.offset)
        span.set_attribute("order.id", event["data"]["orderId"])

        process_order(event["data"])
```

**Result**: Distributed traces span across producer → Kafka → consumer, visible in Jaeger, Tempo, or Datadog APM.

### Correlation IDs

Beyond W3C Trace Context, business-level correlation IDs link related events across a business process:

```json
{
  "type": "com.acme.shipping.shipment.dispatched",
  "id": "evt-ship-001",
  "data": {
    "shipmentId": "shp-456",
    "orderId": "ord-123",           // Business correlation: links to OrderPlaced
    "sagaId": "saga-order-001",     // Saga correlation: links all saga events
    "correlationId": "order-flow-abc123"  // Request correlation: user's original action
  }
}
```

**Correlation ID propagation**: Each service extracts correlation IDs from incoming events and includes them in all events and log lines it generates:

```python
CORRELATION_KEY = "correlationId"

def process_order_placed(event):
    correlation_id = event['data'].get('correlationId')
    with structlog.contextvars.bound_contextvars(
        correlation_id=correlation_id,
        order_id=event['data']['orderId']
    ):
        logger.info("Processing OrderPlaced event")
        # All log lines within this context automatically include correlation_id
        result = reserve_inventory(event['data']['items'])
        logger.info("Inventory reserved", reservation_id=result.id)

        publish_event({
            'type': 'com.acme.inventory.reservation.created',
            'data': {
                ...result.to_dict(),
                'correlationId': correlation_id  # Propagate forward
            }
        })
```

---

## Schema Evolution and Compatibility

### The Schema Evolution Challenge
Event schemas must evolve as business requirements change, but:
- Old events in the log must remain readable
- Old consumers may not support the new schema immediately
- Deployments are rolling — new and old producers/consumers run simultaneously

### Compatibility Types

**Backward Compatibility (Default Recommendation)**
New schema can read events produced with the old schema.
Safe operations:
- Add optional fields with defaults
- Remove required fields (consumers may expect them — communicate deprecation)

```json
// v1 schema
{"orderId": "ord-123", "amount": 59.98}

// v2 schema (backward compatible — new consumer can read v1 events)
{
  "orderId": "ord-123",
  "amount": 59.98,
  "currency": "USD",      // New optional field with default
  "promoCode": null       // New optional field, nullable
}
```

**Forward Compatibility**
Old schema can read events produced with the new schema. New producers can add new optional fields that old consumers simply ignore.

**Full Compatibility**
Both backward and forward compatible. Only adding optional fields is safe.

### Schema Registry Compatibility Enforcement
```bash
# Set subject compatibility to BACKWARD
curl -X PUT http://schema-registry:8081/config/orders-placed-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility": "BACKWARD"}'

# Test a new schema version before deployment
curl -X POST http://schema-registry:8081/compatibility/subjects/orders-placed-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{...new schema JSON...}"}'

# Response: {"is_compatible": true}
```

### Breaking Change Migration Playbook

When a breaking change is unavoidable:

1. **Announce**: Notify all consumer teams with 30/60/90-day timeline
2. **Create v2 topic**: `orders-placed-v2` parallel to `orders-placed` (v1)
3. **Dual-publish**: Producer publishes to both v1 and v2
4. **Consumer migration**: Consumer teams update to consume from v2
5. **Deprecation**: After all consumers migrated, stop publishing to v1
6. **Decommission**: After v1 retention window, delete v1 topic

```
Week 1-2:   Create v2 topic; producer dual-publishes v1 + v2
Week 3-6:   Consumer teams migrate to v2 (tracked in catalog)
Week 7:     Verify all consumer groups reading from v2 only
Week 8:     Stop publishing to v1
Week 10:    Delete v1 topic (after 2-week retention window)
```

---

## Consumer Lag Monitoring

### What Is Consumer Lag?
Consumer lag is the difference between the last offset in a partition and the last committed offset of a consumer group. It represents how far behind the consumer is.

```
Partition 0:  [..., offset 9990, offset 9991, offset 9992, offset 9993, offset 9994]
                                                                              ↑
                                                                     Log End Offset: 9994

Consumer Group "shipment-service" committed offset: 9980
Consumer Lag for Partition 0: 9994 - 9980 = 14 messages
```

### Lag Monitoring with Kafka Tools

```bash
# Check lag for all partitions in a consumer group
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe \
  --group shipment-service

# Output:
# GROUP               TOPIC          PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# shipment-service    orders-placed  0          9980            9994            14
# shipment-service    orders-placed  1          12450           12455           5
# shipment-service    orders-placed  2          8890            8890            0
```

### Lag Metrics and Alerting

Expose lag metrics to Prometheus via Kafka Exporter or Confluent's JMX metrics:

```yaml
# Prometheus alert rule for consumer lag
groups:
  - name: kafka-consumer-lag
    rules:
      - alert: KafkaConsumerLagHigh
        expr: |
          kafka_consumer_group_lag{group="shipment-service"} > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Consumer group {{ $labels.group }} is lagging"
          description: "Lag is {{ $value }} messages on {{ $labels.topic }}/{{ $labels.partition }}"

      - alert: KafkaConsumerLagCritical
        expr: |
          kafka_consumer_group_lag{group="shipment-service"} > 100000
        for: 2m
        labels:
          severity: critical
```

**Lag-based autoscaling (KEDA)**:
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: shipment-service-scaler
spec:
  scaleTargetRef:
    name: shipment-service
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: shipment-service
        topic: orders-placed
        lagThreshold: "1000"         # Scale up when lag > 1000 per partition
        activationLagThreshold: "10"
```

---

## Backpressure Handling

### What Is Backpressure?
Backpressure occurs when a consumer cannot process events as fast as the producer emits them. Without backpressure handling, consumer lag grows unboundedly, memory pressure increases, and eventually the consumer falls over.

### Kafka's Natural Backpressure
Kafka consumers control their own consumption rate via poll intervals:
```python
consumer = KafkaConsumer(
    'orders-placed',
    max_poll_records=100,            # Process at most 100 records per poll
    max_poll_interval_ms=300000,     # Rebalance if poll not called within 5 minutes
    fetch_max_bytes=52428800,        # Max 50MB per fetch request
)

for messages in consumer:
    # Consumer naturally slows down if processing takes time
    # Kafka doesn't push more until consumer polls again
    process_batch(messages)
    consumer.commit()
```

The pull model is Kafka's built-in backpressure mechanism. Consumers read at their own pace; lag is a natural consequence that triggers operational response (scale out, optimize).

### Backpressure in Push-Based Systems
For push-based brokers (RabbitMQ, ActiveMQ), use `prefetch` to limit in-flight messages:

```python
# RabbitMQ: prefetch count limits messages delivered before ACK
channel.basic_qos(prefetch_count=10)   # Max 10 unacknowledged messages per consumer

# Consumer processes one at a time
def callback(ch, method, properties, body):
    process_event(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # ACK unlocks next message
```

### Flow Control Strategies

**Consumer-side throttling**:
```python
import time
from threading import Semaphore

semaphore = Semaphore(10)  # Max 10 concurrent processing tasks

def process_event_async(event):
    with semaphore:          # Blocks if 10 events already in flight
        do_processing(event)

for message in consumer:
    process_event_async(message.value)
```

**Selective processing during overload**:
```python
LAG_THRESHOLD_SKIP_LOW_PRIORITY = 50000

def should_process_event(event, current_lag):
    if current_lag > LAG_THRESHOLD_SKIP_LOW_PRIORITY:
        # Under load: process only high-priority events
        return event['data'].get('priority') == 'high'
    return True
```

**Exponential backoff on downstream errors**:
```python
def process_with_backoff(event, max_retries=5):
    for attempt in range(max_retries):
        try:
            result = call_downstream_service(event)
            return result
        except TemporaryError as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Attempt {attempt+1} failed, retrying in {wait_time}s")
            time.sleep(wait_time)
    raise MaxRetriesExceeded(f"Failed after {max_retries} attempts")
```

---

## Exactly-Once vs. At-Least-Once Trade-offs

### Delivery Semantics Comparison

| Aspect | At-Most-Once | At-Least-Once | Exactly-Once |
|---|---|---|---|
| Message loss | Possible | None | None |
| Duplicates | None | Possible | None |
| Performance overhead | Lowest | Low | ~20-30% higher |
| Implementation complexity | Lowest | Low-Medium | High |
| Use case | Metrics sampling | Most production | Financial, idempotency-critical |

### At-Least-Once (Default for Most Production)
```python
consumer = KafkaConsumer(
    'orders-placed',
    enable_auto_commit=False,    # Manual commit for control
    group_id='shipment-service'
)

for message in consumer:
    try:
        process_event(message.value)
        consumer.commit()         # Commit AFTER successful processing
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Don't commit — message will be redelivered
        # Consumer MUST be idempotent!
```

**Idempotency implementation**:
```python
processed_events = redis.Redis()  # Shared across instances

def process_event(event):
    event_id = event['id']

    # Idempotency check using Redis with TTL
    if processed_events.set(
        f"processed:{event_id}",
        "1",
        nx=True,         # Only set if not exists
        ex=86400         # Expire after 24 hours (covers max retry window)
    ):
        # Not yet processed — process now
        do_processing(event)
    else:
        logger.info(f"Duplicate event {event_id}, skipping")
```

### Exactly-Once (Kafka Transactions)
```python
producer = KafkaProducer(
    enable_idempotence=True,
    transactional_id='order-processor-instance-1',  # Unique per producer instance
    acks='all'
)

producer.init_transactions()

for message in consumer:
    producer.begin_transaction()
    try:
        # Read-process-write in one atomic transaction
        result = process_event(message.value)

        producer.send('processed-orders', value=result)

        # Commit consumer offset within the same transaction
        producer.send_offsets_to_transaction(
            {TopicPartition(message.topic, message.partition): message.offset + 1},
            group_metadata=consumer.consumer_group_metadata()
        )

        producer.commit_transaction()
    except Exception as e:
        producer.abort_transaction()
        raise
```

**When EOS is worth the cost**:
- Financial transactions where duplicate processing = double charge
- Inventory operations where duplicate reservation = oversell
- Aggregations where duplicate counting = wrong metrics
- Any case where idempotency is difficult to implement externally

**When at-least-once + idempotency is sufficient**:
- Most notification use cases (idempotent: dedup by event ID)
- Most data replication (idempotent: upsert by primary key)
- Event sourcing (idempotent: check event ID before appending)

---

## Operational Runbooks

### Runbook: Consumer Group Falling Behind

**Symptoms**: Consumer lag growing consistently; processing time per event increasing; alerts firing.

**Diagnosis**:
```bash
# Check current lag
kafka-consumer-groups.sh --describe --group <group-name> --bootstrap-server kafka:9092

# Check consumer processing time (via metrics)
# Check downstream service latency
# Check consumer instance count
```

**Remediation steps**:
1. Identify bottleneck: CPU, memory, downstream service latency, or partition count
2. If CPU/memory: scale out consumer instances (up to partition count)
3. If downstream latency: add caching, circuit breaker, or async processing
4. If partition count limits parallelism: increase partitions (requires careful consumer group restart)
5. If temporary backlog: let it catch up (monitor recovery rate); if not recovering, add instances

### Runbook: Dead Letter Queue Growing

**Symptoms**: DLQ message count increasing; alerts on DLQ depth.

**Diagnosis**:
```bash
# For Kafka: check consumer error logs
kubectl logs -l app=<consumer-name> --tail=100

# For RabbitMQ: inspect DLQ messages via management UI
# Check error type distribution
```

**Remediation steps**:
1. Inspect a sample of DLQ messages — identify error type
2. Categorize: schema error, transient error, business logic error, poison pill
3. For schema errors: deploy consumer fix, replay from DLQ
4. For transient errors: replay DLQ (errors should succeed now)
5. For poison pills: extract problematic messages to separate store; replay the rest
6. After fix deployed, drain DLQ:
```bash
# RabbitMQ: move DLQ messages back to main queue
rabbitmq-shovel --source-queue order-dlq --destination-queue order-processor
```

### Runbook: Producer Unable to Publish (Kafka Full/Slow)

**Symptoms**: Producer errors; throughput drops; `TimeoutException` on produce calls.

**Diagnosis**:
```bash
# Check broker disk usage
kafka-log-dirs.sh --bootstrap-server kafka:9092 --describe | grep -E "logDir|size"

# Check broker health
kafka-broker-api-versions.sh --bootstrap-server kafka:9092

# Check under-replicated partitions
kafka-topics.sh --bootstrap-server kafka:9092 --describe --under-replicated-partitions
```

**Remediation steps**:
1. If disk full: emergency retention reduction or log deletion
2. If under-replicated partitions: check failed broker nodes; restart if needed
3. If producer slow due to acks=all: verify in-sync replicas count (ISR)
4. If topic throttled: check producer/consumer quotas

### Runbook: Schema Registry Unavailable

**Symptoms**: Producers failing with schema registry connection errors; consumers can't deserialize messages.

**Impact assessment**:
- Producers with local schema caching: continue producing (cached schemas)
- Consumers with local schema caching: continue consuming (cached schemas)
- First-time producers/consumers with no cache: fail immediately

**Remediation steps**:
1. Verify schema registry pods are running: `kubectl get pods -n kafka`
2. Check schema registry health: `curl http://schema-registry:8081/`
3. Check database connectivity (schema registry uses Kafka topics for storage)
4. Restart schema registry pods if unhealthy
5. If schema registry is down for extended period: deploy consumers in "schema-less" mode (bypass registry, use known local schemas)

### Runbook: Event Replay Required

**Trigger**: Consumer bug discovered; events were processed incorrectly.

**Steps**:
1. Stop the consumer (do not process new events while replaying)
2. Fix the bug and deploy the corrected consumer
3. Enable `REPLAY_MODE=true` in consumer environment (suppresses external side effects)
4. Reset consumer group offset to replay start point:
```bash
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --group <group-name> \
  --reset-offsets \
  --to-datetime 2024-01-15T00:00:00.000 \
  --topic <topic-name> \
  --execute
```
5. Restart consumer with increased parallelism for faster catch-up
6. Monitor lag decreasing to zero
7. Disable `REPLAY_MODE`
8. Resume normal operation
9. Post-mortem: analyze why the bug occurred, add test coverage

---

## Key Operational Metrics Dashboard

```
┌─────────────────────────────────────────────────┐
│           Flow Operations Dashboard              │
├─────────────────┬───────────────────────────────┤
│ Producer Health │ Events/sec per topic           │
│                 │ Producer error rate            │
│                 │ Publish latency P50/P99        │
├─────────────────┼───────────────────────────────┤
│ Consumer Health │ Consumer lag per group/topic   │
│                 │ Processing rate (events/sec)   │
│                 │ Processing latency P50/P99     │
│                 │ Error rate per consumer group  │
├─────────────────┼───────────────────────────────┤
│ Broker Health   │ Disk usage per broker          │
│                 │ Under-replicated partitions    │
│                 │ Network I/O per broker         │
│                 │ Request rate per broker        │
├─────────────────┼───────────────────────────────┤
│ Schema Registry │ Schema registration rate       │
│                 │ Schema validation errors       │
│                 │ Registry availability          │
├─────────────────┼───────────────────────────────┤
│ DLQ / Errors   │ DLQ depth per consumer         │
│                 │ Dead letter rate trend         │
│                 │ Error type distribution        │
└─────────────────┴───────────────────────────────┘
```
