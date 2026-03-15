# Administering Kafka
## Chapters 2, 10: AdminClient API, Topic Management, Partition Ops, Quotas, Tuning

---

## AdminClient API (Chapter 2)

The `AdminClient` provides a programmatic interface for all cluster administration — the same operations available via CLI tools, but accessible from application code.

### Creating an AdminClient

```java
Properties props = new Properties();
props.put("bootstrap.servers", "broker1:9092,broker2:9092");
props.put("request.timeout.ms", "30000");

AdminClient admin = AdminClient.create(props);
// ALWAYS close when done
try (AdminClient admin = AdminClient.create(props)) {
    // operations...
}
```

The AdminClient API is **asynchronous and eventually consistent** — operations return `Future`-like objects. The cluster's state may not immediately reflect changes.

### Topic Management

```java
// Create topics
NewTopic newTopic = new NewTopic("orders", 12, (short) 3);
newTopic.configs(Map.of(
    "retention.ms", "604800000",  // 7 days
    "cleanup.policy", "delete"
));
admin.createTopics(Collections.singletonList(newTopic)).all().get();

// List topics
Set<String> topics = admin.listTopics().names().get();

// Describe topics (partitions, leaders, ISRs)
Map<String, TopicDescription> descriptions =
    admin.describeTopics(Collections.singletonList("orders")).all().get();

// Delete topics
admin.deleteTopics(Collections.singletonList("old-topic")).all().get();
```

### Configuration Management

```java
// Get current broker config
ConfigResource brokerResource = new ConfigResource(ConfigResource.Type.BROKER, "1");
Config brokerConfig = admin.describeConfigs(Collections.singletonList(brokerResource))
    .all().get().get(brokerResource);

// Update topic config
ConfigResource topicResource = new ConfigResource(ConfigResource.Type.TOPIC, "orders");
ConfigEntry entry = new ConfigEntry("retention.ms", "86400000");
AlterConfigOp op = new AlterConfigOp(entry, AlterConfigOp.OpType.SET);
admin.incrementalAlterConfigs(Map.of(topicResource, List.of(op))).all().get();
```

### Consumer Group Management

```java
// List consumer groups
List<ConsumerGroupListing> groups = admin.listConsumerGroups()
    .all().get().stream().collect(Collectors.toList());

// Describe consumer group (offsets, lag per partition)
Map<TopicPartition, OffsetAndMetadata> offsets =
    admin.listConsumerGroupOffsets("my-group")
        .partitionsToOffsetAndMetadata().get();

// Reset consumer group offsets (group must be stopped)
Map<TopicPartition, OffsetAndMetadata> resetTo = new HashMap<>();
resetTo.put(new TopicPartition("orders", 0), new OffsetAndMetadata(0));
admin.alterConsumerGroupOffsets("my-group", resetTo).all().get();

// Delete consumer group (must be inactive)
admin.deleteConsumerGroups(Collections.singletonList("old-group")).all().get();
```

### Advanced Operations

```java
// Add partitions to a topic (increases, never decreases)
Map<String, NewPartitions> newPartitions =
    Map.of("orders", NewPartitions.increaseTo(24));
admin.createPartitions(newPartitions).all().get();

// Delete records before an offset (free disk space)
Map<TopicPartition, RecordsToDelete> recordsToDelete = new HashMap<>();
recordsToDelete.put(
    new TopicPartition("orders", 0),
    RecordsToDelete.beforeOffset(1000L)
);
admin.deleteRecords(recordsToDelete).all().get();

// Trigger preferred leader election
admin.electLeaders(ElectionType.PREFERRED, null).all().get();

// Reassign replicas
// (complex — see CLI section below for practical usage)
```

---

## CLI Administration

For ad-hoc operations, Kafka ships with CLI tools:

### Topic Operations

```bash
# Create topic
kafka-topics.sh --bootstrap-server broker:9092 \
  --create --topic orders \
  --partitions 12 --replication-factor 3 \
  --config retention.ms=604800000

# List topics
kafka-topics.sh --bootstrap-server broker:9092 --list

# Describe topic (partitions, leaders, ISRs)
kafka-topics.sh --bootstrap-server broker:9092 --describe --topic orders

# Alter topic config
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type topics --entity-name orders \
  --alter --add-config retention.ms=86400000

# Delete topic
kafka-topics.sh --bootstrap-server broker:9092 --delete --topic old-topic

# Increase partition count
kafka-topics.sh --bootstrap-server broker:9092 \
  --alter --topic orders --partitions 24
```

### Consumer Group Operations

```bash
# List groups
kafka-consumer-groups.sh --bootstrap-server broker:9092 --list

# Describe group (offsets, lag per partition)
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --describe --group my-group

# Reset offsets to beginning (group must be stopped)
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --group my-group --topic orders \
  --reset-offsets --to-earliest --execute

# Reset to specific offset
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --group my-group --topic orders:0 \
  --reset-offsets --to-offset 1000 --execute

# Reset to timestamp
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --group my-group --topic orders \
  --reset-offsets --to-datetime 2024-06-30T00:00:00.000 --execute
```

### Partition Reassignment

Moving partitions between brokers (for rebalancing load or decommissioning a broker):

```bash
# 1. Generate a reassignment plan
kafka-reassign-partitions.sh --bootstrap-server broker:9092 \
  --broker-list "1,2,3" \
  --topics-to-move-json-file topics.json \
  --generate > reassignment.json

# 2. Execute the reassignment
kafka-reassign-partitions.sh --bootstrap-server broker:9092 \
  --reassignment-json-file reassignment.json \
  --execute

# 3. Verify completion
kafka-reassign-partitions.sh --bootstrap-server broker:9092 \
  --reassignment-json-file reassignment.json \
  --verify
```

**Throttle replication during reassignment** to avoid impacting producers/consumers:
```bash
# Set throttle (bytes/sec per broker)
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type brokers --entity-default \
  --alter --add-config 'leader.replication.throttled.rate=50000000,follower.replication.throttled.rate=50000000'

# Remove throttle when done
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type brokers --entity-default \
  --alter --delete-config leader.replication.throttled.rate,follower.replication.throttled.rate
```

---

## Quotas

Quotas prevent rogue producers/consumers from starving other clients.

### Types of Quotas

| Quota Type | Scope | Config Key |
|-----------|-------|-----------|
| **Producer rate** | Bytes/sec per producer | `producer_byte_rate` |
| **Consumer rate** | Bytes/sec per consumer | `consumer_byte_rate` |
| **Request rate** | % of broker thread time | `request_percentage` |

### Setting Quotas

```bash
# Quota per client ID
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type clients --entity-name analytics-consumer \
  --alter --add-config consumer_byte_rate=10485760  # 10 MB/s

# Default quota for all clients
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type clients --entity-default \
  --alter --add-config consumer_byte_rate=52428800  # 50 MB/s

# Per-user quota (with authentication)
kafka-configs.sh --bootstrap-server broker:9092 \
  --entity-type users --entity-name analytics-user \
  --alter --add-config consumer_byte_rate=104857600  # 100 MB/s
```

When a client exceeds its quota, the broker throttles it — introducing artificial delay in responses rather than rejecting requests.

---

## Broker Configuration and Tuning

### Hardware Recommendations

| Component | Recommendation | Notes |
|-----------|---------------|-------|
| **Disk** | Local SSDs or fast HDDs | Kafka is disk-I/O bound for write-heavy workloads |
| **Disk layout** | Multiple mount points | More disks → more parallel I/O (`log.dirs`) |
| **Memory** | 32–64 GB RAM | Kafka relies heavily on OS page cache; JVM heap is small |
| **CPU** | 16–32 cores | For compression/decompression; typically not CPU-bound |
| **Network** | 10 GbE | For replication and high-throughput topics |
| **OS** | Linux | Kafka is optimized for Linux; production always Linux |

### Key Broker Configs

```properties
# Storage
log.dirs=/data/kafka-logs-1,/data/kafka-logs-2  # multiple disks
log.retention.hours=168
log.segment.bytes=1073741824  # 1GB segments
log.roll.hours=168

# Replication
default.replication.factor=3
min.insync.replicas=2
unclean.leader.election.enable=false

# Network
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Controller (KRaft mode)
process.roles=broker,controller  # combined mode
controller.quorum.voters=1@broker1:9093,2@broker2:9093,3@broker3:9093
```

### JVM Settings

```bash
KAFKA_HEAP_OPTS="-Xmx6g -Xms6g"
KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 \
  -XX:InitiatingHeapOccupancyPercent=35 -XX:+ExplicitGCInvokesConcurrent \
  -Djava.awt.headless=true"
```

**Heap sizing**: Keep Kafka JVM heap at 4–8 GB. More heap means more GC pressure and less memory available for OS page cache (which is critical for Kafka performance).

### OS Settings

```bash
# Increase open file descriptors (each partition = multiple files)
ulimit -n 100000
# In /etc/security/limits.conf:
kafka soft nofile 100000
kafka hard nofile 100000

# Disable swapping (page cache eviction is better)
vm.swappiness=1

# Improve page cache behavior for Kafka sequential I/O
vm.dirty_background_ratio=5
vm.dirty_ratio=60

# TCP settings for high-throughput
net.core.rmem_default=1048576
net.core.wmem_default=1048576
net.ipv4.tcp_rmem=4096 1048576 16777216
net.ipv4.tcp_wmem=4096 1048576 16777216
```

---

## Useful Admin Recipes

### Find the Leader for a Partition

```bash
kafka-topics.sh --bootstrap-server broker:9092 \
  --describe --topic orders | grep "Partition: 0"
# Output: Topic: orders Partition: 0 Leader: 2 Replicas: 2,1,3 Isr: 2,1,3
```

### Produce and Consume from CLI (Testing)

```bash
# Produce
kafka-console-producer.sh --bootstrap-server broker:9092 \
  --topic test --property parse.key=true --property key.separator=:

# Consume from beginning
kafka-console-consumer.sh --bootstrap-server broker:9092 \
  --topic test --from-beginning --property print.key=true

# Consume with key and headers
kafka-console-consumer.sh --bootstrap-server broker:9092 \
  --topic test --from-beginning \
  --formatter kafka.tools.DefaultMessageFormatter \
  --property print.key=true --property print.headers=true
```

### Check Under-Replicated Partitions

```bash
kafka-topics.sh --bootstrap-server broker:9092 \
  --describe --under-replicated-partitions
# Empty = healthy. Any output = action required.
```

### Performance Testing

```bash
# Producer throughput test
kafka-producer-perf-test.sh \
  --topic perf-test --num-records 1000000 \
  --record-size 1000 --throughput -1 \
  --producer-props bootstrap.servers=broker:9092 acks=all

# Consumer throughput test
kafka-consumer-perf-test.sh \
  --bootstrap-server broker:9092 \
  --topic perf-test --messages 1000000 --group perf-group
```
