# Cross-Cluster Data Mirroring
## Chapter 9: MirrorMaker 2, Geo-Replication Patterns, Use Cases

---

## Why Cross-Cluster Replication?

A single Kafka cluster cannot always serve all needs:

| Reason | Description |
|--------|-------------|
| **Geographic distribution** | Low-latency reads for users in multiple regions |
| **Disaster recovery** | Failover cluster if primary cluster fails |
**Data sovereignty** | Data must reside in a specific country/region |
| **Workload isolation** | Separate prod cluster from analytics or testing |
| **Compliance** | Keep sensitive data within a specific security boundary |
| **Aggregation** | Collect data from edge/regional clusters into a central cluster |

---

## MirrorMaker 2 (MM2)

**MirrorMaker 2** is the standard Kafka tool for cross-cluster replication. It's built on top of Kafka Connect and replicates:
- Messages (records)
- Topic configurations
- Consumer group offsets (for transparent failover)

### Architecture

```
SOURCE CLUSTER                    DESTINATION CLUSTER
──────────────                    ───────────────────
Topic: orders         →  MM2  →   Topic: source.orders
Topic: customers      →  MM2  →   Topic: source.customers
Consumer group lags   →  MM2  →   Offset sync (for failover)
Topic configs         →  MM2  →   Topic config sync
```

MM2 **prefixes** replicated topic names with the source cluster alias (e.g., `us-east.orders`). This avoids naming conflicts and makes the origin clear.

### Configuration

MM2 is configured as a Kafka Connect cluster with special connectors:

```properties
# mm2.properties

# Cluster aliases
clusters=us-east, eu-west

# Cluster connection details
us-east.bootstrap.servers=us-east-broker1:9092,us-east-broker2:9092
eu-west.bootstrap.servers=eu-west-broker1:9092,eu-west-broker2:9092

# Replication flows (source->destination)
us-east->eu-west.enabled=true
eu-west->us-east.enabled=true  # for active-active

# What to replicate
us-east->eu-west.topics=orders,customers,payments
us-east->eu-west.topics.blacklist=internal-.*

# Sync settings
us-east->eu-west.sync.topic.configs.enabled=true
us-east->eu-west.sync.group.offsets.enabled=true

# Replication factor on destination
replication.factor=3
```

### Running MM2

```bash
# As standalone
bin/mirror-maker.sh --config mm2.properties

# As Kafka Connect distributed worker
bin/connect-distributed.sh connect-distributed.properties mm2.properties
```

---

## Replication Patterns

### Active-Passive (Primary/Backup)

```
       WRITES                              READS
       ┌───┐                              ┌───┐
Users  → Primary Cluster   →  MM2  →  Standby Cluster
         (active)                        (passive)
```

**Characteristics:**
- All traffic goes to the primary cluster
- Standby cluster is an up-to-date copy
- On failover: consumers redirect to standby cluster
- Consumer offset sync allows resuming near the current position after failover
- **RPO** (Recovery Point Objective): Small — offset sync runs continuously; lag depends on MM2 configuration
- **RTO** (Recovery Time Objective): Time to redirect consumers and producers

**Use case**: Disaster recovery; the standby is rarely (ideally never) used for production.

**Failover steps:**
1. Stop producers writing to primary (or let them timeout)
2. Consumers read from standby's replicated topics (using translated offsets)
3. Producers redirect to standby
4. If primary recovers: re-replicate or promote standby to primary

### Active-Active (Multi-Master)

```
Users (US) → Cluster US-EAST ←──── MM2 (bidirectional) ────→ Cluster EU-WEST ← Users (EU)
                    │                                                    │
                    └──────── MM2 replicates each direction ────────────┘
```

**Characteristics:**
- Both clusters accept reads and writes
- Each cluster has its own topics + replicas from the other cluster
- Users routed to nearest cluster
- No global ordering across clusters (inherent in distributed writes)
- Cycle detection: MM2 doesn't re-replicate a message it already replicated (via provenance headers)

**Topic naming:**
```
Cluster US: topic "orders" (US-written)
            topic "eu-west.orders" (replicated from EU)

Cluster EU: topic "orders" (EU-written)
            topic "us-east.orders" (replicated from US)
```

**Use cases**: Global applications where each region primarily serves local users; low-latency writes everywhere; geo-redundancy.

**Challenges:**
- Merging data from two clusters requires careful key design to avoid conflicts
- No global offset ordering — consumer apps must handle this
- Total order not guaranteed

### Hub-and-Spoke

```
Edge Cluster 1 ──→ ┐
Edge Cluster 2 ──→ ├──→  Central / Hub Cluster
Edge Cluster 3 ──→ ┘
```

**Use case**: IoT, retail, manufacturing — edge clusters collect local data; hub aggregates for central analytics.

**Characteristics:**
- Edge clusters are small, simple (1–3 brokers)
- Hub cluster is large, fully governed
- Data flows one-way: edges → hub
- Hub topics are named `edge1.telemetry`, `edge2.telemetry`, etc.

### Aggregate Mirror (Fan-In)

Similar to hub-and-spoke but for organizational aggregation:

```
Regional Cluster A ──→ ┐
Regional Cluster B ──→ ├──→  Enterprise Analytics Cluster
Regional Cluster C ──→ ┘
```

---

## Offset Translation

One of MM2's most important features: **translating consumer group offsets** between clusters.

When a consumer group has committed offset 1000 on the source cluster, MM2 maintains a mapping:
```
source cluster partition 0, offset 1000 → destination cluster partition 0, offset 1005
```
(Offsets differ because replicated topics may have different segment structure.)

MM2 exposes the `RemoteClusterUtils` and `MirrorClient` API for offset translation:

```java
// Translate source offsets to destination cluster offsets for failover
Map<TopicPartition, Long> offsets = MirrorClient.translateOffsets(
    destAdminClient,
    "us-east",        // source cluster alias
    sourceOffsets,    // consumer group's last committed offsets on source
    Duration.ofSeconds(30)
);
consumer.assign(translatedPartitions);
consumer.seek(partition, translatedOffset);
```

---

## MM2 Monitoring

Key metrics to monitor for MM2 health:

| Metric | What It Indicates |
|--------|------------------|
| `replication-latency-ms` | Lag between write on source and read on destination |
| `records-lag` | How many records MM2 is behind on source |
| `record-count` | Records replicated per second |
| `byte-count` | Bytes replicated per second |
| Task status (via Connect REST API) | Whether MM2 tasks are RUNNING or FAILED |

**Alert on**: `replication-latency-ms` growing; tasks in FAILED state.

---

## MirrorMaker 1 vs. MirrorMaker 2

| Aspect | MirrorMaker 1 | MirrorMaker 2 |
|--------|--------------|--------------|
| Implementation | Simple consumer + producer | Kafka Connect framework |
| Offset sync | Manual/ad-hoc | Automatic with `MirrorCheckpointConnector` |
| Topic config sync | Not supported | Automatic with `MirrorHeartbeatConnector` |
| Cluster topology | One pair at a time | Multiple clusters, multiple flows |
| Monitoring | Limited | Full Connect REST API + metrics |
| Active-active | Requires external tooling | Built-in cycle detection |
| Status | Deprecated in Kafka 3.x | Current standard |

**Always use MirrorMaker 2** for new deployments.

---

## When NOT to Use Kafka Replication

Cross-cluster replication adds operational complexity. Consider alternatives:

| Scenario | Alternative |
|----------|-------------|
| Single region with multiple AZs | One cluster with `broker.rack` — no MM2 needed |
| Tiered storage | Remote segments on S3 — consumers read from either tier |
| Dev/staging isolation | Separate clusters with no MM2 — different data entirely |
| Analytics workload isolation | Kafka Connect sink to data lake — not cluster replication |
