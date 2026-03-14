# Event Streaming Platforms

Reference for Apache Kafka architecture, Amazon Kinesis, Apache Pulsar, stream processing concepts (stateless vs. stateful), windowing, exactly-once semantics, and log compaction.

---

## Apache Kafka Architecture

### Core Concepts

**Topics**
A topic is a named, append-only, ordered log of events. Topics are the fundamental unit of organization in Kafka.

- Topics are durable: events are persisted to disk
- Topics are immutable: published events cannot be modified or deleted (until retention expires)
- Topics can be read by any number of consumer groups simultaneously
- Topics are organized into partitions for parallelism

**Partitions**
Each topic is divided into one or more partitions. Partitions are the unit of parallelism and ordering.

```
Topic: orders
  Partition 0: [event_0, event_1, event_4, event_7, ...]
  Partition 1: [event_2, event_5, event_8, ...]
  Partition 2: [event_3, event_6, event_9, ...]
```

Key properties:
- Events within a single partition are strictly ordered
- Events across partitions have no ordering guarantee
- A partition can only be consumed by one consumer instance per consumer group (parallelism = min(consumers, partitions))
- Partitions are distributed across Kafka brokers in the cluster

**Partition Key**
When publishing, producers specify a key. All events with the same key go to the same partition, guaranteeing ordering per key:
```python
# All events for order-123 go to the same partition → ordered
producer.produce(
    topic='orders',
    key='order-123',         # Determines partition
    value=event_payload
)
```

**Offsets**
Each event in a partition is assigned a monotonically increasing integer offset. Consumer groups track which offset they've read up to per partition.

```
Partition 0:  [0, 1, 2, 3, 4, 5, 6, 7, ...]
                                   ↑
              Consumer Group A offset: 6 (next to read: 7)
              Consumer Group B offset: 2 (next to read: 3)
```

### Kafka Cluster Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Kafka Cluster                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │   Broker 1   │  │   Broker 2   │  │  Broker 3  ││
│  │ (Controller) │  │              │  │            ││
│  │              │  │              │  │            ││
│  │ P0-Leader    │  │ P1-Leader    │  │ P2-Leader  ││
│  │ P1-Replica   │  │ P2-Replica   │  │ P0-Replica ││
│  │ P2-Replica   │  │ P0-Replica   │  │ P1-Replica ││
│  └──────────────┘  └──────────────┘  └────────────┘│
│                                                      │
│  ZooKeeper / KRaft (metadata and leader election)   │
└─────────────────────────────────────────────────────┘
```

**Replication**
- Each partition has one leader and N-1 followers (N = replication factor, typically 3)
- Producers write to the leader; followers replicate asynchronously
- `acks` setting controls durability:
  - `acks=0`: fire and forget (no guarantee)
  - `acks=1`: leader acknowledges (leader failure = potential loss)
  - `acks=all` (or `-1`): all in-sync replicas acknowledge (strongest durability)

**Consumer Groups**
```python
# Consumer group config
consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['kafka-1:9092'],
    group_id='shipment-notification-service',   # Group ID
    auto_offset_reset='earliest'
)
```
- All consumers with the same `group_id` form one consumer group
- Each partition is assigned to exactly one consumer in the group
- If a consumer fails, its partitions are rebalanced to other group members
- Different consumer groups receive all events independently

### Kafka Configuration Reference

**Producer Settings**
```properties
# Durability vs. latency trade-off
acks=all                          # Strongest durability (slowest)
retries=3                         # Retry on transient failure
retry.backoff.ms=100

# Throughput optimization
batch.size=16384                  # Batch up to 16KB before sending
linger.ms=5                       # Wait up to 5ms to fill batch
compression.type=snappy           # Compress batches

# Idempotent producer (prevents duplicates on retry)
enable.idempotence=true
```

**Consumer Settings**
```properties
# Offset management
enable.auto.commit=false          # Manual commit for exactly-once processing
auto.offset.reset=earliest        # Start from beginning if no committed offset

# Performance
fetch.min.bytes=1                 # Minimum data to fetch per request
fetch.max.wait.ms=500             # Max time to wait for fetch.min.bytes
max.poll.records=500              # Max records per poll()
```

**Topic Configuration**
```bash
# Create topic with 12 partitions, replication factor 3, 7-day retention
kafka-topics.sh --create \
  --topic orders \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete
```

---

## Log Compaction

### What Is Log Compaction?
Log compaction is a Kafka cleanup policy that retains the **latest event for each key** indefinitely, while still retaining the full history for recent events.

**Standard retention** (delete policy): Events deleted after time window expires.
**Compacted retention**: Latest event per key retained forever; older events for the same key deleted.

```
Before compaction (topic: customer-profiles, key = customerId):
  Offset 0: {customerId: "c1", name: "John Doe", email: "old@email.com"}
  Offset 1: {customerId: "c2", name: "Jane Smith"}
  Offset 2: {customerId: "c1", email: "new@email.com"}   ← newer c1 event
  Offset 3: {customerId: "c3", name: "Bob Jones"}
  Offset 4: {customerId: "c2", tier: "gold"}             ← newer c2 event

After compaction:
  Offset 2: {customerId: "c1", email: "new@email.com"}   ← latest for c1
  Offset 3: {customerId: "c3", name: "Bob Jones"}
  Offset 4: {customerId: "c2", tier: "gold"}             ← latest for c2
```

### Use Cases for Log Compaction
- **Reference data topics**: Latest customer profile, product catalog, configuration
- **Event sourcing snapshots**: Latest aggregate state per entity ID
- **Cache invalidation**: Latest value per cache key
- **Tombstones**: Publishing a `null` payload for a key marks deletion; compaction will eventually remove the key

```bash
# Enable compaction for a topic
kafka-topics.sh --alter \
  --topic customer-profiles \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.1 \
  --config segment.ms=3600000
```

---

## Amazon Kinesis

### Kinesis Architecture
Amazon Kinesis Data Streams is AWS's managed event streaming service:

**Shards** (analogous to Kafka partitions)
- Each shard provides 1 MB/s write, 2 MB/s read
- Partition key hashed to determine shard assignment
- Scale by splitting (increase) or merging (decrease) shards

**Data Retention**
- Default: 24 hours
- Extended: up to 365 days (additional cost)

**Consumers**
- Classic (GetRecords API): poll-based, shared throughput limit across consumers
- Enhanced Fan-Out: dedicated 2 MB/s per consumer — designed for multiple independent consumers

```python
import boto3

kinesis = boto3.client('kinesis', region_name='us-east-1')

# Produce
kinesis.put_record(
    StreamName='orders',
    Data=json.dumps(event_payload),
    PartitionKey='order-123'    # Determines shard
)

# Consume (Lambda trigger is preferred over manual polling)
```

### Kinesis vs. Kafka Trade-offs

| Dimension | Kinesis | Kafka (MSK/Self-Hosted) |
|---|---|---|
| Operations | Fully managed | MSK managed or self-hosted ops |
| Scaling | Manual shard split/merge | Auto-scale with Confluent/MSK |
| Throughput | 1 MB/s per shard | Partition-based, higher ceiling |
| Retention | Max 365 days | Unlimited (with storage) |
| AWS integration | Native (Lambda, Firehose, Analytics) | Integration via connectors |
| Cost model | Per shard-hour + data | MSK per broker-hour |
| Multi-region | Cross-region replication available | MirrorMaker 2 |
| Protocol | AWS proprietary | Kafka protocol (broader ecosystem) |

---

## Apache Pulsar

### Pulsar Architecture Differentiators
Pulsar separates serving and storage layers, unlike Kafka's unified broker:

```
┌────────────────────────────────────┐
│         Pulsar Brokers             │
│  (stateless — any broker handles   │
│   any topic, no data stored)       │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│         Apache BookKeeper          │
│  (distributed storage — replicated │
│   write-ahead log)                 │
└────────────────────────────────────┘
```

Benefits of this separation:
- **Instant topic rebalancing**: Moving a topic to another broker requires no data movement
- **Independent scaling**: Scale compute (brokers) and storage (bookies) independently
- **Geo-replication**: Built-in active-active and active-passive replication across datacenters

**Pulsar Subscriptions**
Pulsar offers four subscription types (more flexible than Kafka's consumer groups):
- **Exclusive**: Single consumer per subscription (like Kafka partition-exclusive)
- **Failover**: Active consumer + standby; standby takes over on failure
- **Shared**: Round-robin delivery across multiple consumers (like SQS competing consumers)
- **Key_Shared**: Events with the same key always go to the same consumer (like Kafka per-key ordering)

**Multi-Tenancy**
Pulsar has built-in multi-tenancy with hierarchical namespacing:
```
persistent://tenant/namespace/topic-name
persistent://acme-corp/orders/order-events
persistent://acme-corp/inventory/stock-updates
```

---

## Stream Processing

### Stateless Stream Processing
Processing each event independently without reference to previous events:

```python
# Stateless: transform each event
def process_event(event):
    return {
        "orderId": event["id"],
        "enrichedStatus": lookup_status_description(event["status"]),
        "processedAt": datetime.utcnow().isoformat()
    }
```

Operations: filter, map, flatMap, branch, merge
Frameworks: Kafka Streams (filter/map), Apache Flink (DataStream), Kafka Connect (transformations)

### Stateful Stream Processing
Processing that requires accumulating state across events:

**Aggregations**
```python
# Count orders per customer in the last hour
# Requires maintaining running counts per customerId, keyed by window
SELECT customerId, COUNT(*) as orderCount
FROM orders_stream
GROUP BY customerId
WINDOW TUMBLING (SIZE 1 HOUR)
```

**Joins**
```python
# Enrich order events with customer data from a table
SELECT o.orderId, o.amount, c.tier, c.email
FROM orders_stream o
JOIN customers_table c ON o.customerId = c.customerId
```

**Aggregation State Stores (Kafka Streams)**
```java
KTable<String, Long> orderCountPerCustomer = ordersStream
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .count(Materialized.as("order-counts-store"));
```

### Windowing Strategies

**Tumbling Windows** (fixed, non-overlapping)
```
Events:  e1 e2 e3 | e4 e5 | e6 e7 e8 e9
Windows: [  W1   ] [  W2 ] [    W3    ]
         0      1h  1h   2h  2h      3h
```
Use for: hourly/daily aggregations, periodic metrics

**Hopping Windows** (fixed size, overlapping)
```
Events:  e1 e2 e3 e4 e5 e6 e7
Windows: [  W1: 0-1h  ]
              [  W2: 30m-1.5h ]
                   [  W3: 1h-2h  ]
```
Use for: rolling averages (moving 1-hour window updated every 15 minutes)

**Sliding Windows** (event-time based, triggered per event)
A window for every pair of events within a time range of each other.
Use for: "events occurring within 5 minutes of each other"

**Session Windows** (activity-based, variable size)
```
Events:  e1 e2 e3  [gap > 30min]  e4 e5  [gap > 30min]  e6
Windows: [  Session 1  ]           [Sess2]                [S3]
```
Use for: user sessions (group activity separated by inactivity gaps)

### Exactly-Once Semantics

Three delivery guarantees in order of increasing difficulty and cost:

**At-Most-Once**
- Producer sends without retry; consumer does not re-process on failure
- Events may be lost; never duplicated
- Use when: event loss is acceptable (metrics sampling, best-effort notifications)

**At-Least-Once**
- Producer retries on failure; consumer may see duplicates
- No events lost; duplicates possible
- Use when: missing events is unacceptable; consumer is idempotent
- Default for most production Kafka deployments

**Exactly-Once (EOS)**
- Each event processed exactly once, end-to-end
- Kafka mechanism: idempotent producers + transactions

```java
// Exactly-once in Kafka Streams (read-process-write)
Properties props = new Properties();
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
          StreamsConfig.EXACTLY_ONCE_V2);  // Requires Kafka 2.5+

// For producer-only exactly-once:
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-transactional-id");

producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("output-topic", key, value));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

**EOS Cost**:
- ~20-30% throughput reduction vs. at-least-once
- Higher latency (waits for all ISR to acknowledge)
- Only guaranteed within Kafka ecosystem (not across Kafka + external database atomically without two-phase commit or outbox pattern)

---

## Kafka Streams vs. Apache Flink

| Dimension | Kafka Streams | Apache Flink |
|---|---|---|
| Deployment | Library (runs in your app) | Separate cluster |
| State backend | RocksDB (embedded) | RocksDB, heap, or remote |
| Checkpointing | Committed offsets + changelogs | Distributed snapshots |
| Exactly-once | Yes (within Kafka) | Yes (including external sinks) |
| SQL support | ksqlDB (separate) | Flink SQL (built-in) |
| Complexity | Low-medium | Medium-high |
| Best for | Kafka-native stream processing | Complex stateful, multi-source |
| Windowing | Tumbling, Hopping, Session | All + custom |
| Event time | Yes | Yes (superior watermark control) |

---

## Sizing and Performance Guidelines

### Kafka Topic Sizing
```
Partitions = max(target throughput / throughput per partition, target consumer parallelism)

Target throughput: 50 MB/s
Typical partition throughput: 10 MB/s
Consumer parallelism needed: 8

Partitions = max(50/10, 8) = max(5, 8) = 8 partitions (round up to power of 2: 8)
```

### Retention Sizing
```
Required storage per topic = retention_days * daily_throughput_gb * replication_factor

Example:
  3 days * 50 GB/day * 3 replicas = 450 GB per topic
```

### Consumer Lag Alerting
Alert when consumer lag exceeds:
- Time-sensitive consumers: lag > 30 seconds worth of events
- Batch-tolerant consumers: lag > 5 minutes worth of events
- SLA-critical consumers: lag > configured SLA threshold

```bash
# Check consumer group lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group shipment-notification-service
```
