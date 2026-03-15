# Kafka Consumers: Reading Data from Kafka
## Chapter 4: Consumer API, Consumer Groups, Offsets, Rebalancing

---

## Consumer Overview

Consumers read records from Kafka topics. The consumer API is poll-based: the application calls `poll()` in a loop, which returns batches of records. The consumer handles:
- Subscription to topics or partitions
- Partition assignment within a consumer group
- Offset tracking and committing
- Rebalancing when group membership changes

---

## Consumer Groups

Consumer groups are the core scaling mechanism for consumers.

### How Groups Work

```
Topic: payments (4 partitions: P0, P1, P2, P3)

Group "payment-processor" — 2 consumers:
  Consumer 1 → P0, P1
  Consumer 2 → P2, P3

Group "payment-auditor" — 1 consumer:
  Consumer 3 → P0, P1, P2, P3  (one consumer can read all partitions)

Group "payment-analytics" — 4 consumers:
  Consumer 4  → P0
  Consumer 5  → P1
  Consumer 6  → P2
  Consumer 7  → P3  (maximum parallelism)
```

**Key rules:**
- One partition is assigned to at most one consumer within a group at any time
- Multiple groups read the same topic independently — each with its own offsets
- Adding consumers beyond partition count → idle consumers (waste)
- Removing consumers → partition reassignment (remaining consumers take over)

### Group Coordinator

The **group coordinator** is a broker responsible for managing one or more consumer groups:
- Handles join/leave requests
- Triggers rebalances
- Stores committed offsets in `__consumer_offsets` topic
- Manages heartbeat timeouts

---

## Creating a Consumer

```java
Properties props = new Properties();
props.put("bootstrap.servers", "broker1:9092,broker2:9092");
props.put("group.id", "my-consumer-group");
props.put("key.deserializer",
    "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer",
    "org.apache.kafka.common.serialization.StringDeserializer");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("orders"));
```

**Subscription options:**
```java
// Subscribe to specific topics (dynamic partition assignment)
consumer.subscribe(Arrays.asList("orders", "payments"));

// Subscribe with regex (auto-includes new matching topics)
consumer.subscribe(Pattern.compile("payments-.*"));

// Manually assign specific partitions (no group coordination)
consumer.assign(Arrays.asList(new TopicPartition("orders", 0)));
```

---

## The Poll Loop

```java
try {
    while (true) {
        ConsumerRecords<String, String> records =
            consumer.poll(Duration.ofMillis(100));  // timeout for blocking

        for (ConsumerRecord<String, String> record : records) {
            log.info("topic={}, partition={}, offset={}, key={}, value={}",
                record.topic(), record.partition(), record.offset(),
                record.key(), record.value());
            processRecord(record);
        }
        consumer.commitAsync();  // commit after processing batch
    }
} finally {
    consumer.close();  // ALWAYS close to trigger immediate rebalance
}
```

**`poll()` does more than fetch records:**
- Sends heartbeats to group coordinator
- Triggers rebalances (if group membership changed)
- Fetches metadata updates
- Returns immediately if records are available; blocks up to timeout if not

---

## Offsets and Committing

### What Offsets Represent

Committed offset = **the next record to fetch** (not the last record processed).

```
Partition 0: [0][1][2][3][4][5]
                          ↑
                     Committed offset = 4
                     → Next poll will start at offset 4
                     → Records 0-3 have been processed
```

Offsets are stored in the `__consumer_offsets` Kafka topic — not ZooKeeper (since Kafka 0.9).

### Auto-Commit

```properties
enable.auto.commit=true   # default
auto.commit.interval.ms=5000  # commit every 5 seconds
```

**Risk**: If the consumer crashes between commit intervals, records since last commit are reprocessed (at-least-once). If the consumer commits then crashes before processing, records are lost (at-most-once with certain patterns).

### Manual Commit — Synchronous

```java
consumer.commitSync();  // commits last offset returned by poll()

// Commit specific offsets:
Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
offsets.put(new TopicPartition("orders", 0),
            new OffsetAndMetadata(lastOffset + 1));
consumer.commitSync(offsets);
```

**Blocks** until broker confirms. Retries on retriable errors. Throws on non-retriable.

### Manual Commit — Asynchronous

```java
consumer.commitAsync((offsets, exception) -> {
    if (exception != null) {
        log.error("Commit failed for offsets {}", offsets, exception);
        // No automatic retry — you must handle retry logic
    }
});
```

**Does not block**. Higher throughput. No automatic retry on failure. Use for normal operation; fall back to `commitSync()` on shutdown.

### Combined Strategy (Recommended)

```java
try {
    while (running) {
        records = consumer.poll(Duration.ofMillis(100));
        processRecords(records);
        consumer.commitAsync();          // async for normal operation
    }
    consumer.commitSync();               // sync for clean shutdown
} catch (Exception e) {
    log.error("Unexpected error", e);
} finally {
    try {
        consumer.commitSync();           // last attempt on any exit
    } finally {
        consumer.close();
    }
}
```

---

## Rebalancing

A **rebalance** reassigns partitions among consumers in a group. Triggered by:
- Consumer joins the group
- Consumer leaves (or crashes / heartbeat timeout)
- Topic partition count changes
- New topics matching a subscription regex

### Eager Rebalance (Stop the World)

Default protocol before Kafka 2.4:
1. All consumers **revoke all partitions**
2. All consumers rejoin the group
3. Coordinator assigns partitions fresh
4. All consumers resume

**Problem**: All consumption stops during rebalance (can be seconds to minutes for large groups).

### Cooperative/Incremental Rebalance (Kafka 2.4+)

```properties
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

Only the partitions that need to move are revoked and reassigned. Other consumers keep their partitions and keep processing. Much lower disruption.

### Partition Assignment Strategies

| Strategy | Behavior | Best For |
|----------|---------|---------|
| `RangeAssignor` | Contiguous partitions per consumer per topic | Simple; may be uneven across topics |
| `RoundRobinAssignor` | Partitions assigned round-robin | Even distribution; no stickiness |
| `StickyAssignor` | Minimizes movement; aims for even balance | Reduced rebalance disruption |
| `CooperativeStickyAssignor` | Incremental rebalance + sticky | Best choice for Kafka 2.4+ |

### Rebalance Listeners

```java
consumer.subscribe(topics, new ConsumerRebalanceListener() {
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        // Called before rebalance — commit offsets, flush state
        consumer.commitSync(currentOffsets);
        closeStatefulProcessors(partitions);
    }
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        // Called after rebalance — initialize state for new partitions
        initializeStatefulProcessors(partitions);
    }
});
```

---

## Critical Consumer Configuration

### Timing and Liveness

| Config | Default | Notes |
|--------|---------|-------|
| `session.timeout.ms` | 45,000ms | Heartbeat must be received within this window or consumer is considered dead |
| `heartbeat.interval.ms` | 3,000ms | Frequency of heartbeats; should be ≤ session.timeout/3 |
| `max.poll.interval.ms` | 300,000ms | Max time between poll() calls; triggers rebalance if exceeded |
| `max.poll.records` | 500 | Max records returned per poll; tune to match processing time |

**Critical relationship**: If processing a batch takes longer than `max.poll.interval.ms`, the consumer is considered dead and triggers a rebalance — even if heartbeats are sent from a background thread. Tune `max.poll.records` to ensure batches process within the interval.

### Fetch Configuration

| Config | Default | Notes |
|--------|---------|-------|
| `fetch.min.bytes` | 1 | Min bytes before broker responds; increase for throughput |
| `fetch.max.wait.ms` | 500ms | How long broker waits if `fetch.min.bytes` not satisfied |
| `fetch.max.bytes` | 52,428,800 | Max bytes per fetch request |
| `max.partition.fetch.bytes` | 1,048,576 | Max bytes per partition per fetch |

### Offset Reset Policy

```properties
auto.offset.reset=earliest  # Start from beginning if no committed offset
auto.offset.reset=latest    # Start from newest if no committed offset (default)
auto.offset.reset=none      # Throw exception if no committed offset
```

---

## Standalone Consumers (No Group)

For specific use cases (replay, auditing, testing) you can consume from specific partitions without group coordination:

```java
List<PartitionInfo> partitions = consumer.partitionsFor("orders");
List<TopicPartition> topicPartitions = partitions.stream()
    .map(p -> new TopicPartition(p.topic(), p.partition()))
    .collect(Collectors.toList());

consumer.assign(topicPartitions);

// Seek to specific offset or beginning
consumer.seekToBeginning(topicPartitions);
consumer.seek(new TopicPartition("orders", 0), 100L);
```

No heartbeats, no rebalances — but also no automatic load balancing.

---

## Consumer Best Practices

| Practice | Why |
|---------|-----|
| Use `enable.auto.commit=false` | Explicit control prevents subtle loss/duplicate bugs |
| Always call `consumer.close()` in finally | Triggers immediate partition release; avoids waiting for session timeout |
| Use `CooperativeStickyAssignor` | Reduces rebalance disruption significantly |
| Monitor consumer lag | Lag growing = consumer is falling behind; action needed |
| Keep poll loop tight | Long processing between polls → heartbeat failures → rebalance |
| Use `onPartitionsRevoked` to commit | Prevents reprocessing after rebalance |
| One consumer per thread | KafkaConsumer is NOT thread-safe; use separate consumers or synchronize |
| Test with `kafka-consumer-groups.sh` | Monitor lag per partition per consumer |
