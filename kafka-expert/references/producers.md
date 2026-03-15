# Kafka Producers: Writing Messages to Kafka
## Chapter 3: Producer API, Configuration, Serializers, Partitioners

---

## Producer Overview

The Kafka producer is responsible for publishing records to Kafka topics. It handles:
- Serialization of keys and values
- Partition selection
- Batching for efficiency
- Retry logic and error handling
- Delivery guarantee enforcement

```
Application
    │
    ▼
KafkaProducer
    │
    ├── Serializer (key)
    ├── Serializer (value)
    ├── Partitioner
    ├── RecordAccumulator (batch buffer)
    │
    ▼
NetworkClient → Broker Leader
```

---

## Creating a Producer

```java
Properties props = new Properties();
props.put("bootstrap.servers", "broker1:9092,broker2:9092");
props.put("key.serializer",   "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
```

**`bootstrap.servers`**: Initial brokers for cluster discovery. Include 2–3 for resilience. The producer fetches the full cluster metadata from these.

---

## Sending Messages

### Three Send Modes

**1. Fire and forget** — send and don't check result:
```java
producer.send(new ProducerRecord<>("orders", key, value));
// No error handling — messages can be silently lost
```

**2. Synchronous send** — block until result:
```java
RecordMetadata metadata = producer.send(record).get();
// Throws exception on failure; topic, partition, offset available in metadata
```

**3. Asynchronous with callback** — non-blocking with error handling:
```java
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        log.error("Send failed", exception);
    } else {
        log.debug("Sent to {}-{} @ offset {}",
            metadata.topic(), metadata.partition(), metadata.offset());
    }
});
```

**Best practice**: Always use callbacks. Fire-and-forget silently drops messages; synchronous blocks throughput.

### ProducerRecord

```java
ProducerRecord<String, String> record = new ProducerRecord<>(
    "topic-name",     // required: topic
    "partition-key",  // optional: key (drives partitioning)
    "message-value"   // required: value
);

// With explicit partition:
new ProducerRecord<>("topic", 0, key, value);

// With headers:
record.headers().add("source-system", "payments".getBytes());
```

---

## Critical Producer Configuration

### Delivery Guarantee Configs

| Config | Values | Effect |
|--------|--------|--------|
| `acks` | `0`, `1`, `all`/`-1` | Who must acknowledge before send returns |
| `enable.idempotence` | `true`/`false` | Prevents duplicate sends on retry |
| `retries` | integer | How many times to retry on retriable errors |
| `max.in.flight.requests.per.connection` | integer | Outstanding requests before blocking |

**Recommended safe defaults:**
```properties
acks=all
enable.idempotence=true
retries=2147483647
max.in.flight.requests.per.connection=5
```

With `enable.idempotence=true`:
- Each producer gets a unique PID (Producer ID)
- Each message has a sequence number per partition
- Broker deduplicates messages with the same PID+partition+sequence
- `acks=all` and `retries=MAX` are automatically enforced
- `max.in.flight` is automatically limited to 5

### acks In Depth

```
acks=0:
  Producer sends → returns immediately
  → Broker may not have received it
  → Message may be lost
  → Use case: metrics where loss is acceptable

acks=1:
  Producer → Leader writes to memory → ack
  → Loss if leader crashes before replication
  → Minimum for most use cases

acks=all:
  Producer → Leader writes → all ISR replicate → ack
  → Survives leader failure (as long as at least 1 ISR survives)
  → Always pair with min.insync.replicas=2
```

### Throughput vs. Latency Configs

| Config | Default | Low Latency | High Throughput |
|--------|---------|-------------|----------------|
| `batch.size` | 16,384 bytes | Smaller | 131,072+ bytes |
| `linger.ms` | 0 | 0 | 10–100ms |
| `compression.type` | none | none | snappy/lz4/zstd |
| `buffer.memory` | 33,554,432 | Default | Larger |

**`linger.ms`**: Wait this long for batch to fill before sending. `0` = send immediately (low latency). `5–100` = wait to batch more messages (high throughput).

**`compression.type`**:
- `none` — no compression; fast but uses more bandwidth
- `snappy` — good balance; fast compression, decent ratio
- `lz4` — faster than snappy; slightly worse ratio
- `gzip` — best compression ratio; slowest; good for archival
- `zstd` — best ratio at good speed; recommended for new deployments

### Timeout and Retry Configs

| Config | Default | Notes |
|--------|---------|-------|
| `delivery.timeout.ms` | 120,000ms | Max time from send() call to ack or failure |
| `request.timeout.ms` | 30,000ms | Max time to wait for broker response |
| `retry.backoff.ms` | 100ms | Initial wait between retries |
| `max.block.ms` | 60,000ms | Max time send() blocks when buffer is full |

**Ordering with retries**: Without idempotence, retries can reorder messages if `max.in.flight > 1`. With `enable.idempotence=true`, ordering is preserved up to 5 in-flight requests.

---

## Serializers

Serializers convert Java objects to bytes. Must match deserializers on the consumer.

### Built-in Serializers

```java
// String
StringSerializer
// Integer, Long, Double, Bytes, ByteArray, ByteBuffer, UUID
IntegerSerializer, LongSerializer, ...
```

### Avro Serializer (Schema Registry)

```java
props.put("value.serializer",
    "io.confluent.kafka.serializers.KafkaAvroSerializer");
props.put("schema.registry.url", "http://schema-registry:8081");

// Produces Avro binary with schema ID prefixed (5 bytes)
// Consumer uses KafkaAvroDeserializer to fetch schema and deserialize
```

**Why Avro + Schema Registry?**
- Schema stored once in registry; message only contains schema ID (4 bytes overhead)
- Schema evolution enforced at registry (no breaking changes without approval)
- Cross-language support
- Compact binary format

---

## Partitioners

The partitioner determines which partition a message goes to.

### Default Partitioner

```
If partition is explicitly specified → use that partition
Else if key is not null → hash(key) % numPartitions
Else → sticky partitioning (fill current batch; then round-robin)
```

**Key-based partitioning guarantees**: All messages with the same key go to the same partition → strict ordering per key.

**Sticky partitioner** (default for null keys, Kafka 2.4+): Fills the current batch fully before moving to the next partition. Better batching than pure round-robin.

### Custom Partitioner

```java
public class RegionPartitioner implements Partitioner {
    public int partition(String topic, Object key, byte[] keyBytes,
                         Object value, byte[] valueBytes, Cluster cluster) {
        String region = extractRegion((String) key);
        List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
        int numPartitions = partitions.size();
        // Route US to first half, EU to second half
        if ("US".equals(region)) {
            return Math.abs(key.hashCode()) % (numPartitions / 2);
        } else {
            return (numPartitions / 2) + Math.abs(key.hashCode()) % (numPartitions / 2);
        }
    }
}
```

Register with: `props.put("partitioner.class", RegionPartitioner.class.getName());`

---

## Error Handling

### Retriable vs. Non-Retriable Errors

| Error Type | Examples | Behavior |
|-----------|---------|---------|
| **Retriable** | `LeaderNotAvailableException`, `NotEnoughReplicasException`, network timeout | Producer retries automatically if `retries > 0` |
| **Non-retriable** | `InvalidTopicException`, `RecordTooLargeException`, serialization error | Fails immediately; no retry |

**Important**: `NotEnoughReplicasException` is retriable — if broker can't satisfy `min.insync.replicas`, producer retries until the condition clears or `delivery.timeout.ms` expires.

### Handling in Callbacks

```java
producer.send(record, (metadata, exception) -> {
    if (exception instanceof RetriableException) {
        // Will be retried automatically by the producer
        // This callback fires with the final failure after retries exhausted
        handleRetriableFailure(record, exception);
    } else if (exception != null) {
        // Non-retriable: log and dead-letter the record
        deadLetterQueue.send(record);
        log.error("Non-retriable error", exception);
    }
});
```

---

## Producer Interceptors

Interceptors allow modifying or observing records before sending and after ack:

```java
public class AuditInterceptor implements ProducerInterceptor<String, String> {
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        // Add tracing header
        record.headers().add("trace-id", UUID.randomUUID().toString().getBytes());
        return record;
    }
    public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
        metrics.recordSend(metadata.topic(), exception == null);
    }
}

props.put("interceptor.classes", AuditInterceptor.class.getName());
```

---

## Producer Best Practices

| Practice | Why |
|---------|-----|
| Always use callbacks, never fire-and-forget | Silent loss is the hardest bug to find |
| Set `enable.idempotence=true` | Free deduplication; no performance cost |
| Set `acks=all` with `min.insync.replicas=2` | Survives broker failure without data loss |
| Set `delivery.timeout.ms` explicitly | Know your max acceptable latency for failure |
| Use Avro/Protobuf + Schema Registry | Schema evolution, compact encoding, cross-service contracts |
| Include source context in headers | Tracing, auditing, debugging |
| Monitor `record-send-rate`, `record-error-rate`, `request-latency-avg` | Producer health visibility |
| Test with `kafka-producer-perf-test.sh` | Baseline throughput before tuning |
