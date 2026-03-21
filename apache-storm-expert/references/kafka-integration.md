# Storm and Kafka Integration
## Chapter 8: KafkaSpout, Offset Management, and Kafka Topologies

---

## Why Kafka + Storm?

Kafka acts as the **durable, high-throughput message buffer** between producers and Storm topologies. This decoupling provides:

- **Backpressure buffer**: Storm can lag behind producers without losing data
- **Replay capability**: Kafka retains messages; Storm can reprocess from any offset
- **Multiple consumers**: Multiple topologies can independently consume the same Kafka topic
- **Fault tolerance**: If Storm restarts, it resumes from the last committed offset

---

## KafkaSpout (Storm 2.x / storm-kafka-client)

The modern Kafka spout uses the native Kafka consumer client (`kafka-clients` library).

### Dependency

```xml
<dependency>
    <groupId>org.apache.storm</groupId>
    <artifactId>storm-kafka-client</artifactId>
    <version>2.4.0</version>
</dependency>
```

### Basic Configuration

```java
KafkaSpoutConfig<String, String> spoutConfig =
    KafkaSpoutConfig.builder("kafka-broker:9092", "my-topic")
        .setProp(ConsumerConfig.GROUP_ID_CONFIG, "storm-consumer-group")
        .setProp(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
                 StringDeserializer.class)
        .setProp(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                 StringDeserializer.class)
        .setOffsetCommitPeriodMs(10_000)  // commit offsets every 10s
        .setFirstPollOffsetStrategy(LATEST)  // start from latest on first run
        .build();

KafkaSpout<String, String> kafkaSpout = new KafkaSpout<>(spoutConfig);

TopologyBuilder builder = new TopologyBuilder();
builder.setSpout("kafka-spout", kafkaSpout, 2);  // 2 executor threads
```

### First Poll Offset Strategies

| Strategy | Behavior |
|----------|----------|
| `LATEST` | Start from latest message on first run; on restart, resume from committed offset |
| `EARLIEST` | Start from beginning on first run; on restart, resume from committed offset |
| `UNCOMMITTED_LATEST` | Always start from latest, even on restart (skip uncommitted offsets) |
| `UNCOMMITTED_EARLIEST` | Always start from beginning if no committed offset exists |
| `TIMESTAMP` | Start from a specific timestamp |

### Multi-Topic and Pattern Subscription

```java
// Multiple topics
KafkaSpoutConfig.builder("broker:9092", "topic1", "topic2", "topic3")

// Pattern-based subscription
KafkaSpoutConfig.builder("broker:9092", Pattern.compile("events-.*"))
```

---

## Offset Management

The Kafka spout commits offsets back to Kafka using the Kafka consumer group protocol.

### How Offsets Are Committed

1. Storm's acking mechanism tracks which tuples are acked
2. The spout maintains a per-partition map of acked offsets
3. Every `offsetCommitPeriodMs` milliseconds, the spout commits the highest contiguous acked offset per partition
4. On restart, the spout resumes from the last committed offset

**Important**: If a tuple at offset 100 is acked but offset 95 is still in-flight (unacked), offset 95 is the last committed offset — Storm won't skip 95–99 even though 100 is done. This prevents message loss at the cost of some reprocessing.

### Controlling Pending Messages

```java
KafkaSpoutConfig.builder(...)
    .setMaxUncommittedOffsets(10_000_000)  // max un-acked tuples before pausing
    .setPollTimeoutMs(200)                 // Kafka poll timeout
    .build();
```

### ZooKeeper-Based Offset Storage (Legacy storm-kafka)

The older `storm-kafka` library (before storm-kafka-client) stored offsets in ZooKeeper under `/storm/topology/<id>/kafkaspout/...`. Avoid for new deployments — use storm-kafka-client with Kafka native offset commits.

---

## Tuple Structure from KafkaSpout

By default, the KafkaSpout emits a tuple with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `topic` | String | Source Kafka topic |
| `partition` | Integer | Source partition |
| `offset` | Long | Kafka offset of the message |
| `key` | K | Message key (deserialized) |
| `value` | V | Message value (deserialized) |

### Custom Record Translator

To emit different or additional fields:

```java
RecordTranslator<String, String> translator =
    (ConsumerRecord<String, String> record) ->
        new Values(record.value(), record.topic(), record.partition());

KafkaSpoutConfig.builder(...)
    .setRecordTranslator(translator, new Fields("message", "topic", "partition"))
    .build();
```

---

## Complete Kafka → Storm Topology Example

```java
public class KafkaTopology {
    public static void main(String[] args) throws Exception {

        // Kafka spout config
        KafkaSpoutConfig<String, String> spoutConfig =
            KafkaSpoutConfig.builder("kafka-broker:9092", "user-events")
                .setProp(ConsumerConfig.GROUP_ID_CONFIG, "user-event-processor")
                .setProp(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                         StringDeserializer.class)
                .setOffsetCommitPeriodMs(5000)
                .setFirstPollOffsetStrategy(UNCOMMITTED_EARLIEST)
                .build();

        TopologyBuilder builder = new TopologyBuilder();

        // Spout: read from Kafka
        builder.setSpout("kafka-spout", new KafkaSpout<>(spoutConfig), 3);

        // Bolt: parse JSON events
        builder.setBolt("parse-bolt", new JsonParseBolt(), 6)
               .shuffleGrouping("kafka-spout");

        // Bolt: route by event type
        builder.setBolt("route-bolt", new EventRouteBolt(), 4)
               .shuffleGrouping("parse-bolt");

        // Bolt: count events per user (stateful)
        builder.setBolt("count-bolt", new UserEventCountBolt(), 8)
               .fieldsGrouping("route-bolt", new Fields("user_id"));

        // Bolt: persist to HBase
        builder.setBolt("hbase-bolt", new HBasePersistBolt(), 4)
               .shuffleGrouping("count-bolt");

        Config conf = new Config();
        conf.setNumWorkers(4);
        conf.setMaxSpoutPending(5000);

        if (args.length == 0) {
            // Local mode
            LocalCluster cluster = new LocalCluster();
            cluster.submitTopology("kafka-user-events", conf, builder.createTopology());
        } else {
            // Cluster mode
            StormSubmitter.submitTopology(args[0], conf, builder.createTopology());
        }
    }
}
```

---

## Exactly-Once with Kafka + Trident

For exactly-once semantics, use `OpaqueTridentKafkaSpout`:

```java
BrokerHosts brokerHosts = new ZkHosts("zookeeper:2181");
TridentKafkaConfig kafkaConfig = new TridentKafkaConfig(brokerHosts, "my-topic");
kafkaConfig.scheme = new SchemeAsMultiScheme(new StringScheme());

OpaqueTridentKafkaSpout spout = new OpaqueTridentKafkaSpout(kafkaConfig);

TridentTopology topology = new TridentTopology();
TridentState counts = topology
    .newStream("kafka-spout", spout)
    .each(new Fields("str"), new ParseFunction(), new Fields("event"))
    .groupBy(new Fields("event_type"))
    .persistentAggregate(new MemoryMapState.Factory(), new Count(), new Fields("count"));
```

The opaque transactional protocol ensures that even if a batch replays with different Kafka messages (due to broker offset inconsistency), state is updated correctly.

---

## Kafka as a Storm Sink

Write processed results back to Kafka using `KafkaBolt`:

```java
// storm-kafka-client KafkaBolt
Properties producerProps = new Properties();
producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-broker:9092");
producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

KafkaBolt<String, String> kafkaBolt = new KafkaBolt<String, String>()
    .withProducerProperties(producerProps)
    .withTopicSelector(new DefaultTopicSelector("output-topic"))
    .withTupleToKafkaMapper(new FieldNameBasedTupleToKafkaMapper<>("key", "value"));

builder.setBolt("kafka-sink", kafkaBolt, 2)
       .shuffleGrouping("processing-bolt");
```

Tuples emitted to `kafka-sink` must include the fields `"key"` and `"value"` (or as configured in `FieldNameBasedTupleToKafkaMapper`).

---

## Tuning Kafka-Storm Integration

| Parameter | Recommendation |
|-----------|---------------|
| Spout executors | Match Kafka partition count for maximum parallelism |
| `max.poll.records` | Tune based on tuple processing time; lower if bolts are slow |
| `offsetCommitPeriodMs` | 5–10 seconds is typical |
| `maxUncommittedOffsets` | Set relative to `topology.max.spout.pending` |
| Consumer group ID | Use unique group ID per topology to avoid conflicts |
| Kafka partition count | Should be divisible by spout parallelism for even distribution |

**Key rule**: Set spout executor count = Kafka partition count. Kafka assigns one partition per consumer thread. Extra executors sit idle; fewer executors means multiple partitions on one executor (reduces throughput).
