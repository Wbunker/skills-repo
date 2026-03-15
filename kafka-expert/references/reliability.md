# Reliable Data Delivery
## Chapter 7: Delivery Guarantees, Idempotent Producer, Transactions, Exactly-Once

---

## Delivery Guarantee Overview

Kafka offers three levels of delivery guarantee depending on configuration:

| Guarantee | Description | Producer Config | Risk |
|-----------|-------------|----------------|------|
| **At-most-once** | Message delivered 0 or 1 times | `acks=0` or `acks=1`, no retry | Loss possible |
| **At-least-once** | Message delivered 1 or more times | `acks=all`, `retries>0` | Duplicates possible |
| **Exactly-once** | Message delivered exactly once | Idempotent + transactions | Highest complexity |

---

## Producer Reliability

### What Can Go Wrong

```
Producer sends message → Network timeout → Producer doesn't know:
  Did the broker receive it? → Retry → Broker MAY have received it → DUPLICATE
  Did the broker not receive it? → Retry → Normal delivery → OK

Solution: Idempotent producer assigns a sequence number.
Broker deduplicates if it sees the same sequence again.
```

### Idempotent Producer

```properties
enable.idempotence=true
```

**How it works:**
1. Each producer instance receives a unique **Producer ID (PID)** from the broker at startup
2. Each message has a **sequence number** per partition (monotonically increasing)
3. The broker deduplicates: if it receives PID=5, partition=0, seq=100 twice, it stores it once
4. On retry, producer sends same PID + seq → broker recognizes duplicate and ignores it

**Guarantees:**
- Exactly-once **per producer session** (new PID on restart → restart can still produce duplicates)
- Within a session, no duplicates even with retries
- Preserves ordering with up to 5 in-flight requests

**Forced settings** (automatically applied with `enable.idempotence=true`):
- `acks=all`
- `retries=MAX_INT`
- `max.in.flight.requests.per.connection ≤ 5`

### Transactions (End-to-End Exactly-Once)

Transactions allow atomic, all-or-nothing writes across multiple partitions and topics.

**Use case**: Read from topic A, process, write to topic B — either both happen or neither.

```java
// Producer setup
props.put("transactional.id", "payment-processor-1");  // unique per producer
producer.initTransactions();

// Transaction lifecycle
try {
    producer.beginTransaction();

    // Write to multiple topics atomically
    producer.send(new ProducerRecord<>("processed-orders", key, value));
    producer.send(new ProducerRecord<>("order-audit-log", key, auditValue));

    // Commit consumer offsets atomically with the transaction
    producer.sendOffsetsToTransaction(currentOffsets, consumerGroupMetadata);

    producer.commitTransaction();

} catch (ProducerFencedException | InvalidProducerEpochException e) {
    // Another producer with same transactional.id took over — abort
    producer.close();
} catch (KafkaException e) {
    producer.abortTransaction();
}
```

**Transaction coordinator**: A broker acts as coordinator for each `transactional.id`. It manages the two-phase commit protocol.

**`sendOffsetsToTransaction`**: Commits consumer offsets as part of the transaction. If the transaction aborts, offsets are not committed → consumer reprocesses from last committed offset → exactly-once end-to-end.

### Isolation Level

Consumers must be configured to only read **committed** transactional messages:

```properties
isolation.level=read_committed  # default is read_uncommitted
```

`read_committed` consumers wait until a transaction is committed before seeing its messages. They never see aborted transaction messages.

**Trade-off**: With `read_committed`, consumers may lag behind producers who have open transactions.

---

## Consumer Reliability

### What Can Go Wrong

| Scenario | Effect |
|----------|--------|
| Process record → crash before commit | Record reprocessed on restart (at-least-once) |
| Commit offset → crash before processing | Record skipped (at-most-once) |
| Long processing → rebalance → commit fails | Record processed twice by two consumers |
| Rebalance with no `onPartitionsRevoked` | Offsets for revoked partitions not committed |

### At-Least-Once Consumer Pattern

```java
consumer.subscribe(topics, new ConsumerRebalanceListener() {
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        // Commit offsets for revoked partitions before losing ownership
        commitOffsets(partitions);
    }
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        // No action needed for at-least-once
    }
});

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processRecord(record);
        // Track offset to commit after each record
        offsetsToCommit.put(
            new TopicPartition(record.topic(), record.partition()),
            new OffsetAndMetadata(record.offset() + 1)
        );
    }
    consumer.commitAsync(offsetsToCommit, callback);
    offsetsToCommit.clear();
}
```

### Exactly-Once Consumer (with External State)

If writing to an external system (database, file), achieving exactly-once requires idempotent writes in the external system:

```
Pattern 1: Idempotent writes
  → Write with a unique key derived from the Kafka offset
  → Duplicate processing produces same result → idempotent

Pattern 2: Transactional writes (if external system supports it)
  → Open DB transaction
  → Write record to DB
  → Store offset in DB (same transaction)
  → Commit DB transaction
  → ONLY then: consumer does NOT commit to Kafka
     (offset stored in DB is the ground truth)
```

**Pattern 2 is how Kafka Streams achieves exactly-once**: it uses an internal state store and commits Kafka offsets and state atomically using Kafka transactions.

---

## Broker Reliability Settings

### Replication Settings

```properties
# Per-broker configuration
default.replication.factor=3           # replicate every new topic 3 ways
min.insync.replicas=2                  # require 2 ISR for acks=all to succeed
unclean.leader.election.enable=false   # only ISR members become leaders
auto.leader.rebalance.enable=true      # rebalance leaders after broker recovery
```

### Durability Settings

```properties
log.flush.interval.messages=1          # fsync every N messages (default: never)
log.flush.interval.ms=1000             # fsync every N ms (default: never)
```

**NOTE**: Kafka delegates durability to the OS page cache by default — no explicit fsync. This is intentional: replication provides durability; fsync adds latency. Explicit fsync is almost never recommended for Kafka.

---

## Validating Reliability

### Testing Strategies

**Chaos testing**: Kill brokers, introduce network partitions, restart consumers — verify no data is lost or duplicated.

```bash
# Kill broker:
kill -9 $(cat /var/run/kafka/kafka.pid)

# Verify no gap in consumer:
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --group my-group --describe
# Check: are all offsets advancing? Any lag growing?
```

**Idempotent write test**: Produce the same record multiple times; verify consumer sees it once.

**Transaction test**: Begin transaction, produce to two topics, abort → verify neither appears; commit → verify both appear.

### Key Metrics for Reliability

| Metric | Normal | Alert |
|--------|--------|-------|
| `UnderReplicatedPartitions` | 0 | > 0 (a replica is behind) |
| `OfflinePartitionsCount` | 0 | > 0 (no leader for a partition) |
| `ActiveControllerCount` | 1 | ≠ 1 (no controller or split-brain) |
| `IsrShrinksPerSec` | 0 | > 0 (replicas falling out of ISR) |
| Consumer lag | Stable low | Growing (consumer can't keep up) |

---

## Reliability Checklist

**Producer:**
- [ ] `acks=all`
- [ ] `enable.idempotence=true`
- [ ] Callback used for every `send()` — errors logged or handled
- [ ] `delivery.timeout.ms` set to match application SLA
- [ ] Dead letter queue for non-retriable failures

**Broker:**
- [ ] `replication.factor ≥ 3` for critical topics
- [ ] `min.insync.replicas=2`
- [ ] `unclean.leader.election.enable=false`
- [ ] Controller availability monitored
- [ ] Disk space monitored (fills = partition goes offline)

**Consumer:**
- [ ] `enable.auto.commit=false`
- [ ] `onPartitionsRevoked` commits offsets before rebalance
- [ ] `isolation.level=read_committed` if using transactions
- [ ] `max.poll.records` tuned to finish processing within `max.poll.interval.ms`
- [ ] Consumer lag monitored per partition per group
