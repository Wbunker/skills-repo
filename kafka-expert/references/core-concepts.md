# Meet Kafka — Core Concepts
## Chapter 1: Publish/Subscribe Messaging, Topics, Partitions, Brokers

---

## The Publish/Subscribe Messaging Model

Kafka is a **distributed event streaming platform** built on the publish/subscribe messaging model. Publishers (producers) send messages to named channels; subscribers (consumers) read from those channels independently — decoupled in time and scale.

### Why Pub/Sub over Point-to-Point Queues

| Aspect | Point-to-Point Queue | Kafka Pub/Sub |
|--------|---------------------|--------------|
| Consumers | One consumer per message | Many independent consumers per message |
| Replay | Message gone after consumption | Messages retained on disk; replayable |
| Backpressure | Queue depth is the only signal | Consumer lag visible per group |
| Scaling | Single consumer bottleneck | Partition-level parallelism |
| Decoupling | Tight (must drain queue) | Loose (consumers independent of each other) |

### How Kafka Evolved at LinkedIn

Kafka was born at LinkedIn (2010) to solve the problem of individual queue systems proliferating across the organization — each team building their own pipeline between services. The resulting **spaghetti of point-to-point queues** was unmaintainable. Kafka replaced this with a single, unified messaging backbone.

---

## Messages and Batches

### Messages

The fundamental unit in Kafka is a **message** (also called an event or record). A message is:
- An array of bytes (Kafka is schema-agnostic at the broker level)
- Optionally associated with a **key** (also bytes)
- Optionally associated with **headers** (key/value metadata pairs)
- Assigned a **timestamp** (producer-assigned or broker-assigned)

**Keys serve two purposes:**
1. **Partitioning**: Messages with the same key are routed to the same partition (ensuring ordering per key)
2. **Log compaction**: With compacted topics, only the latest message per key is retained

### Batches

Producers group messages into **batches** before sending to the broker. Batching is a fundamental performance mechanism:

```
Producer buffer fills with messages → batch sent to broker → broker writes to disk

Without batching: 1 network round-trip per message → high overhead
With batching:    1 network round-trip per N messages → amortized overhead
```

**Tuning batch size:**
- `batch.size` — max bytes per batch (default 16KB); larger = more throughput, more latency
- `linger.ms` — time to wait for batch to fill (default 0ms); adding delay improves batching
- `buffer.memory` — total producer buffer (default 32MB); back-pressures on full

---

## Schemas

Kafka messages are opaque bytes to the broker. Schema management is the producer/consumer's responsibility. Common approaches:

### Schema Registry Pattern

```
Producer → [serialize with schema] → Kafka → [deserialize with schema] → Consumer
                    ↕                                       ↕
             Schema Registry                         Schema Registry
             (source of truth                        (validates schema
              for schema versions)                    compatibility)
```

**Popular schema formats:**

| Format | Pros | Cons |
|--------|------|------|
| **Apache Avro** | Compact binary; schema evolution; Confluent's default | Requires schema registry; binary not human-readable |
| **Protocol Buffers** | Very compact; cross-language; good tooling | Schema registry needed for Kafka integration |
| **JSON Schema** | Human-readable; widely supported | Larger than binary formats |
| **Plain JSON** | Maximum simplicity | No schema enforcement; brittle at scale |

**Schema evolution compatibility modes:**
- **BACKWARD**: New schema can read old data (consumers upgrade first)
- **FORWARD**: Old schema can read new data (producers upgrade first)
- **FULL**: Both backward and forward (safest; most restrictive)

---

## Topics and Partitions

### Topics

A **topic** is a named logical channel for a category of messages. Topics are the primary unit of organization in Kafka:
- Topics are divided into one or more **partitions**
- Topic names are strings (typically `domain.entity.event`, e.g., `payments.orders.created`)
- Topics have configurable **retention** (time-based or size-based)

### Partitions

A **partition** is an ordered, immutable sequence of messages — a commit log:

```
Partition 0: [offset 0] [offset 1] [offset 2] [offset 3] [offset 4] → newest
Partition 1: [offset 0] [offset 1] [offset 2] → newest
Partition 2: [offset 0] [offset 1] [offset 2] [offset 3] → newest
```

**Key properties:**
- Messages within a partition are **strictly ordered** by offset
- Messages **across partitions** have no guaranteed ordering
- Each partition is stored on **one broker** (the leader)
- Partitions are replicated across `replication.factor` brokers for fault tolerance
- **Partition count cannot be decreased** (only increased)

### Offsets

An **offset** is the sequential position of a message within a partition:
- Offsets are per-partition (not global across the topic)
- Kafka retains messages based on time or size — old messages are deleted, but offsets are never reused
- Consumers track their position using offsets (stored in `__consumer_offsets` topic)

### Choosing Partition Count

```
Partitions = max(
  total_throughput / producer_throughput_per_partition,
  total_throughput / consumer_throughput_per_partition
)
```

**Practical guidelines:**
- More partitions = more parallelism, but more overhead (leader election time, open file handles)
- Aim for partitions sized to handle 2–3× expected peak throughput
- A partition can typically sustain 10–50 MB/s depending on disk and network
- Rule of thumb: ≤ 4,000 partitions per broker; ≤ 200,000 per cluster

---

## Producers and Consumers

### Producers

Producers **write** messages to Kafka topics. A producer:
- Creates `ProducerRecord` objects specifying topic, optional partition/key, value
- Serializes key and value to bytes
- Determines the partition (via partitioner)
- Batches records and sends to the leader broker

### Consumers

Consumers **read** messages from Kafka topics. A consumer:
- Subscribes to one or more topics
- Polls for batches of records
- Processes records
- Commits offsets to track progress

### Consumer Groups

**Consumer groups** are the mechanism for parallel consumption and load balancing:

```
Topic: orders (3 partitions)

Consumer Group A (3 consumers — 1:1 ratio):
  Consumer A1 → Partition 0
  Consumer A2 → Partition 1
  Consumer A3 → Partition 2

Consumer Group B (1 consumer — all partitions):
  Consumer B1 → Partition 0, 1, 2

Consumer Group C (6 consumers — over-provisioned):
  Consumer C1 → Partition 0
  Consumer C2 → Partition 1
  Consumer C3 → Partition 2
  Consumer C4,C5,C6 → IDLE (more consumers than partitions = waste)
```

**Key rule**: Max useful parallelism = number of partitions. Extra consumers are idle.

---

## Brokers and Clusters

### Brokers

A **broker** is a single Kafka server. It:
- Receives messages from producers
- Stores messages on disk
- Serves fetch requests from consumers
- Manages partition leadership and replication

Each broker handles hundreds of thousands of partitions and millions of messages per second with appropriate hardware.

### Clusters

A **Kafka cluster** is a group of brokers working together:
- One broker acts as the **controller** (manages partition leadership, ISR)
- Brokers exchange metadata (which broker has which partition leaders)
- ZooKeeper (pre-3.x) or **KRaft** (3.x+) manages cluster metadata and controller election

### The Controller

The controller is a special broker role:
- Manages partition leader election (when a broker fails)
- Maintains the ISR (In-Sync Replicas) list
- Handles broker joins and departures

In **KRaft mode** (Kafka 3.x+), controller nodes run a Raft consensus protocol internally — no ZooKeeper dependency. This simplifies operations dramatically.

### Replication

```
replication.factor=3 means: 1 leader + 2 followers for each partition

Leader Broker:   receives all writes, serves all reads
Follower Broker: replicates from leader; serves reads only if configured
                 promotes to leader if current leader fails
```

**ISR (In-Sync Replicas)**: replicas that have caught up to the leader within `replica.lag.time.max.ms`. Only ISR members are eligible for leader election (unless `unclean.leader.election.enable=true`).

### Multiple Clusters

Multiple Kafka clusters are used for:
- **Geo-replication**: clusters in different regions (active/passive or active/active)
- **Isolation**: separate prod/staging, separate by security domain
- **Scale limits**: when a single cluster hits practical limits

MirrorMaker 2 replicates data between clusters (see `cross-cluster.md`).

---

## Why Kafka?

### Multiple Producers, Multiple Consumers

Unlike a queue where a message is consumed once, Kafka allows any number of independent consumer groups to read the same topic — at their own pace, without interfering with each other.

### Disk-Based Retention

Messages persist on disk for a configurable period (default 7 days). This enables:
- **Replay**: consumers can re-read from any offset
- **Decoupled scaling**: consumers can be offline temporarily and catch up
- **Debugging**: inspect past messages

### Scalable

Kafka scales horizontally:
- Add brokers to increase capacity
- Add partitions to increase throughput (within a topic)
- Producers and consumers scale independently

### High Performance

Kafka achieves high throughput through:
- **Sequential disk I/O**: log-structured storage reads/writes sequentially (fast on both HDD and SSD)
- **Zero-copy transfer**: `sendfile()` syscall bypasses user space for network-to-disk transfers
- **Batching**: amortizes network round-trip overhead
- **Compression**: reduces network and disk I/O (lz4, snappy, gzip, zstd)

---

## Use Cases

| Use Case | How Kafka Helps |
|----------|----------------|
| **Activity tracking** | User events (clicks, views) → Kafka → real-time and batch analytics |
| **Messaging** | Replace traditional message queues with ordered, replayable streams |
| **Metrics and monitoring** | Aggregate metrics from services; stream to monitoring systems |
| **Log aggregation** | Collect logs from all services; route to Elasticsearch, S3, etc. |
| **Stream processing** | Transform, enrich, aggregate events in real time with Kafka Streams |
| **Event sourcing** | Kafka as the system of record for state changes; replay to rebuild state |
| **CDC (Change Data Capture)** | Database changes → Kafka via Debezium → downstream consumers |
| **Microservices integration** | Async, decoupled service communication without point-to-point RPC |
