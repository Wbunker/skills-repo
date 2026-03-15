# Kafka Internals
## Chapters 5–6: KRaft Controller, Replication, Request Handling, Storage, Compaction

---

## Cluster Membership

### KRaft (Kafka Raft) — Kafka 3.x+

**KRaft** replaces ZooKeeper as the metadata and controller management system. In KRaft mode, Kafka manages its own cluster metadata using a Raft consensus protocol.

```
KRaft Architecture:

  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │  CONTROLLER  │   │  CONTROLLER  │   │  CONTROLLER  │
  │  (voter)     │   │  (active     │   │  (voter)     │
  │              │   │   leader)    │   │              │
  └──────────────┘   └──────┬───────┘   └──────────────┘
                             │ Raft log replication
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         BROKER 1       BROKER 2       BROKER 3
         (regular        (regular       (regular
          broker)         broker)        broker)
```

**Combined mode**: A node can be both controller and broker.
**Isolated mode**: Dedicated controller nodes (recommended for large clusters, 3 or 5 nodes).

**Advantages over ZooKeeper:**
- No external dependency to operate and monitor
- Faster controller failover (metadata already replicated via Raft)
- Higher partition limits (ZooKeeper had practical limits around 200K partitions)
- Simpler security model (no separate ZooKeeper ACLs)
- Single protocol for all coordination (Raft instead of ZAB + Kafka protocol)

### The Metadata Log

In KRaft, all cluster metadata (topics, partitions, ISRs, brokers) is stored in an internal Kafka topic `@metadata` replicated via Raft. Every broker subscribes to this topic and has a full view of cluster state.

---

## The Controller

The active controller (one per cluster) is responsible for:

1. **Partition leader election**: When a broker fails, the controller selects a new leader from the ISR for each affected partition
2. **ISR management**: Updates ISR when followers fall behind or catch up
3. **Broker registration**: Handles broker joins and departures
4. **Topic/partition lifecycle**: Creates, modifies, and deletes topics

### Failover

In KRaft, controller failover is fast (milliseconds) because the new controller already has the full metadata log replicated. In ZooKeeper-based Kafka, failover required loading the full state from ZooKeeper, which could take seconds to minutes for large clusters.

---

## Replication

Replication is how Kafka provides fault tolerance. Every partition has:
- One **leader** — handles all reads and writes
- Zero or more **followers** — replicate data from the leader; eligible to become leader

### Replica Lifecycle

```
Producer writes → Leader receives → Leader writes to log
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                          Follower1   Follower2   Follower3
                         (fetch from leader continuously)
```

### ISR (In-Sync Replicas)

**ISR** = replicas that have caught up to the leader within `replica.lag.time.max.ms` (default 30s).

```
replication.factor=3
ISR=[leader, follower1, follower2]  ← all three in sync

follower2 falls behind →
ISR=[leader, follower1]             ← follower2 removed from ISR

follower2 catches up →
ISR=[leader, follower1, follower2]  ← follower2 rejoins ISR
```

**`min.insync.replicas`**: Minimum number of ISR members required before a produce request with `acks=all` is accepted. If ISR drops below this, producers get `NotEnoughReplicasException`.

**Common configuration:**
```
replication.factor=3
min.insync.replicas=2
acks=all (on producer)

→ Can tolerate 1 broker failure without data loss
→ Writes require 2 of 3 replicas to be in sync
```

### Unclean Leader Election

```properties
unclean.leader.election.enable=false  # default, recommended
```

**With `false`** (default): Only ISR members can be elected leader → **no data loss**, but partition is unavailable if all ISR members are down.

**With `true`**: Any replica can be elected leader, even out-of-sync ones → **potential data loss**, but partition remains available.

The right choice depends on whether availability or durability is the higher priority.

---

## Request Handling

All communication in Kafka uses a binary protocol over TCP. Brokers handle requests from producers, consumers, other brokers, and admin clients.

### Request Processing Pipeline

```
Client TCP connection
      │
Network Thread (I/O thread)
      │ → parses request, puts in request queue
Request Queue
      │
Request Handler Thread (I/O thread pool)
      │ → executes request, puts response in response queue
Response Queue
      │
Network Thread
      │ → sends response to client
```

**Key configuration**: `num.network.threads` (default 3) and `num.io.threads` (default 8). Under high load, these may need tuning.

### Produce Requests

1. Broker validates the request (permissions, topic exists, etc.)
2. Writes to the partition leader's log
3. If `acks=all`, waits for followers to replicate
4. Sends acknowledgment

### Fetch Requests

1. Consumer sends a fetch request specifying topic, partition, offset, max bytes
2. Broker checks if enough data is available (considering `fetch.min.bytes`)
3. Uses `sendfile()` (zero-copy) to transfer data from disk to network socket
4. Returns records along with high-water mark (latest committed offset)

**High-water mark**: Consumers can only read up to the high-water mark — the offset replicated to all ISR members. This prevents consumers from reading uncommitted data.

### Leader Epochs

Leader epochs track which leader wrote which data, preventing data inconsistency after leader failures. Each leadership change increments the epoch. Followers use leader epochs to detect and discard data that was written by a leader that was then replaced.

---

## Physical Storage

### Log Files

Kafka stores data in log segments on disk:

```
/kafka-logs/
└── orders-0/               ← topic "orders", partition 0
    ├── 00000000000000000000.log    ← segment file (messages)
    ├── 00000000000000000000.index  ← offset index
    ├── 00000000000000000000.timeindex  ← timestamp index
    ├── 00000000000001500000.log    ← newer segment
    ├── 00000000000001500000.index
    └── 00000000000001500000.timeindex
```

Each segment file name is the base offset of the first record in that segment.

**Segment management:**
- `log.segment.bytes` (default 1GB): Roll to new segment when this size is reached
- `log.roll.ms` / `log.roll.hours` (default 7 days): Roll to new segment after this time
- Only the **active segment** (newest) is being written to; older segments are immutable

### Indexes

Kafka maintains two index files per segment for efficient seeking:

**Offset index** (`.index`): Maps logical offset → physical byte position in the log file. Sparse — not every offset indexed.

**Time index** (`.timeindex`): Maps timestamp → offset. Enables seeking by timestamp (`offsetsForTimes()` consumer API).

Index lookup:
1. Binary search in index to find nearest entry
2. Scan forward in log file from that byte position

### File Format

Each message on disk contains:
```
Offset (8 bytes)
Message size (4 bytes)
CRC (4 bytes)
Magic byte (version, 1 byte)
Attributes (compression codec, timestamp type, 1 byte)
Timestamp (8 bytes)
Key length (4 bytes)
Key (variable)
Value length (4 bytes)
Value (variable)
```

Since Kafka 0.11: messages stored in **RecordBatch** format, enabling header support, improved compression, and idempotent/transactional writes.

---

## Retention

### Time-Based Retention

```properties
log.retention.hours=168        # 7 days (default)
log.retention.minutes=1440     # minutes take precedence over hours
log.retention.ms=86400000      # ms takes precedence over minutes
```

Segments older than the retention period are deleted (entire segment, not individual messages).

### Size-Based Retention

```properties
log.retention.bytes=1073741824  # 1 GB per partition (default: -1, unlimited)
```

When partition size exceeds this limit, oldest segments are deleted.

### Compacted Topics

**Log compaction** retains the **latest value for each key** indefinitely (plus the tombstone period for deleted keys).

```
Uncompacted (time-based retention):
Offset 0: key=user1, value={"name":"Alice"}
Offset 1: key=user2, value={"name":"Bob"}
Offset 2: key=user1, value={"name":"Alice Smith"}  ← update
Offset 3: key=user1, value=null                    ← delete (tombstone)

After compaction:
Offset 1: key=user2, value={"name":"Bob"}          ← retained (latest)
Offset 3: key=user1, value=null                    ← tombstone retained temporarily
```

**Use cases**: Database changelogs, cache warming, materialized views, event sourcing.

**Configuration:**
```properties
log.cleanup.policy=compact          # or "delete" (default) or "compact,delete"
min.cleanable.dirty.ratio=0.5       # compact when 50% of log is dirty
delete.retention.ms=86400000        # tombstones retained for 24h before deletion
```

---

## Tiered Storage

Kafka 3.6+ supports **tiered storage**: automatically offloads older log segments to cheap object storage (S3, GCS, ADLS) while keeping recent segments on local disk.

```
Broker Local Disk:      Hot data (recent segments)
                        → Fast reads; low latency
Object Storage (S3):    Warm/cold data (older segments)
                        → Cheap storage; higher read latency
```

**Benefits:**
- Dramatically reduces broker disk requirements
- Enables much longer retention without expensive local storage
- Consumers transparently read from either tier
- Replication factor can be reduced for old data (object storage has its own redundancy)

**Configuration:**
```properties
remote.log.storage.system.enable=true
remote.storage.manager.class.name=org.apache.kafka.server.log.remote.storage.RemoteLogStorageManager
```
(Specific implementation class varies by storage provider and Kafka distribution)

---

## Partition Allocation

When a topic is created, Kafka distributes partitions across brokers:

**Round-robin with rack awareness:**
1. Assign leader replicas across brokers in round-robin order
2. Assign follower replicas ensuring they're on different racks than the leader (if rack awareness configured)

**Rack awareness:** Configure `broker.rack` on each broker. Kafka ensures leader and followers are spread across racks — a single rack failure doesn't take down all ISR members.

```properties
# On each broker:
broker.rack=rack-1   # or rack-2, rack-3
```
