# Apache Storm Foundations
## Chapter 1: Real-Time Processing and Storm Introduction

---

## Why Real-Time Processing?

Batch processing (MapReduce/Hive) introduces inherent latency — results arrive minutes or hours after the events occur. Real-time use cases demand sub-second or second-level latency:

- Fraud detection (flag a transaction before it clears)
- Real-time dashboards and alerting
- Log aggregation and anomaly detection
- Social media analytics (trending topics, sentiment)
- IoT sensor stream processing
- Recommendation engines that react to current behavior

Apache Storm provides **continuous, low-latency stream processing** with horizontal scalability and fault tolerance.

---

## What Is Apache Storm?

Apache Storm is a **distributed, fault-tolerant, real-time computation system**. Key characteristics:

- **Unbounded streams**: Processes data continuously; no concept of a "final" result
- **Horizontal scalability**: Add workers to handle more data
- **Fault tolerance**: Nimbus detects failed tasks and reassigns them automatically
- **Guaranteed message processing**: At-least-once delivery via the acking mechanism
- **Language agnostic**: JVM-native; multi-lang support via Thrift/JSON protocol (Python, Ruby, etc.)
- **Low latency**: Sub-second end-to-end for simple topologies

---

## Cluster Architecture

### Nimbus (Master)

- Single master process (like Hadoop's NameNode / YARN ResourceManager)
- Responsibilities:
  - Distributes topology JAR to worker nodes
  - Assigns tasks to Supervisors via ZooKeeper
  - Monitors topology health; reassigns failed tasks
  - Stateless by design — if Nimbus crashes, running topologies continue; it can restart and re-read state from ZooKeeper
- Storm 2.x supports **Nimbus HA** (multiple Nimbus, leader election via ZooKeeper)

### Supervisor (Worker Node)

- Runs on every worker node in the cluster
- Responsibilities:
  - Listens for task assignments from Nimbus (via ZooKeeper)
  - Spawns and kills **worker processes** (JVMs) as directed
  - Reports heartbeats to ZooKeeper
- Stateless; safe to kill/restart without losing topology state

### Worker Process

- A JVM process spawned by the Supervisor
- Each worker belongs to exactly one topology
- Contains one or more **executors** (threads)
- Multiple workers per Supervisor possible (configured by Supervisor slots)

### Executor

- A thread within a worker process
- Runs one or more **tasks** of a single spout or bolt component
- Default: one executor per component (controlled by parallelism hint)

### Task

- The actual running instance of a spout or bolt
- Default: one task per executor
- Separating tasks from executors allows rebalancing without redeploying

### ZooKeeper

- External coordination service (Apache ZooKeeper ensemble)
- Stores:
  - Topology assignment state (which tasks on which workers)
  - Supervisor heartbeats
  - Nimbus leadership (Storm 2.x HA)
- Nimbus and Supervisors communicate exclusively through ZooKeeper — they never talk directly

---

## Core Primitives

### Tuple

The fundamental data unit in Storm. A tuple is an **ordered list of named fields**:

```java
// Declaring output fields
public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("word", "count"));
}

// Emitting a tuple
collector.emit(new Values("hello", 1));
```

Field types: any Java-serializable object. Storm uses Kryo serialization by default.

### Stream

An **unbounded sequence of tuples** flowing between components. Each stream has a unique ID (default stream ID is "default"). A spout or bolt can emit to multiple named streams.

### Spout

The **data source** of a topology. Spouts read from external systems and emit tuples into the topology.

Key interface methods:

```java
public interface IRichSpout {
    void open(Map conf, TopologyContext context, SpoutOutputCollector collector);
    void nextTuple();           // Called repeatedly; emit one tuple per call
    void ack(Object msgId);     // Called when tuple tree fully processed
    void fail(Object msgId);    // Called on timeout or explicit fail; replay the tuple
    void close();
}
```

**Reliability contract**: Assign a `msgId` when emitting to enable acking. If no `msgId` (null), Storm does not track the tuple — fire-and-forget.

Common spout implementations:
- `KafkaSpout` — reads from Kafka topics
- `FileSpout` — reads from files (testing)
- Custom spout reading from databases, queues, APIs

### Bolt

The **processing unit** of a topology. Bolts receive tuples, apply logic, and optionally emit new tuples.

Key interface methods:

```java
public interface IRichBolt {
    void prepare(Map conf, TopologyContext context, OutputCollector collector);
    void execute(Tuple input);  // Called for every incoming tuple
    void cleanup();
}
```

**Anchoring**: To maintain at-least-once guarantees, bolts must anchor output tuples to their input tuple:

```java
public void execute(Tuple input) {
    String word = input.getStringByField("word");
    collector.emit(input, new Values(word.toUpperCase())); // anchored
    collector.ack(input);
}
```

If the bolt does not need to emit, it still must ack or fail the input tuple.

### Topology

A **directed acyclic graph (DAG)** of spouts and bolts. The unit of deployment in Storm.

```java
TopologyBuilder builder = new TopologyBuilder();
builder.setSpout("sentence-spout", new SentenceSpout(), 2);      // 2 executors
builder.setBolt("split-bolt", new SplitBolt(), 4)                // 4 executors
       .shuffleGrouping("sentence-spout");
builder.setBolt("count-bolt", new CountBolt(), 4)                 // 4 executors
       .fieldsGrouping("split-bolt", new Fields("word"));

Config conf = new Config();
conf.setNumWorkers(2);
StormSubmitter.submitTopology("word-count", conf, builder.createTopology());
```

---

## Reliability: The Acking Mechanism

Storm tracks every tuple through the topology using an **XOR-based checksum tree**:

1. When a spout emits tuple `T` with `msgId`, Storm creates a tracking entry
2. When a bolt anchors and emits from `T`, the child tuple is added to the tracking tree
3. When all tuples in the tree are acked, the spout's `ack(msgId)` is called
4. If any tuple in the tree fails or times out (`topology.message.timeout.secs`, default 30s), the spout's `fail(msgId)` is called and the spout can replay

**XOR trick**: Storm stores only a 64-bit XOR value per tuple tree. Acking a tuple XORs its ID into the value. When the value reaches zero, the tree is fully acked. Constant memory regardless of tree size.

**Ackers**: Special acker bolts (one task per acker) maintain the XOR table. `topology.acker.executors` controls the number of acker threads.

### Reliability Levels

| Approach | How | Guarantee |
|----------|-----|-----------|
| Acked emission with msgId | `spout.emit(tuple, msgId)` + bolt acks | At-least-once |
| Fire and forget | `spout.emit(tuple)` (no msgId) | At-most-once |
| Trident | Transactional spout + state | Exactly-once |

---

## Storm vs. Other Systems

| Dimension | Storm | Spark Streaming | Kafka Streams | Flink |
|-----------|-------|-----------------|---------------|-------|
| **Model** | Per-tuple (record-at-a-time) | Micro-batch | Per-record | Per-record |
| **Latency** | Sub-second | 0.5–2s (batch interval) | Sub-second | Sub-second |
| **State** | Via Trident | RDD checkpoints | RocksDB | Managed state |
| **Exactly-once** | Trident only | Yes | Yes | Yes |
| **Deployment** | Nimbus/Supervisor | YARN/Standalone | Embedded in app | JobManager/TaskManager |
| **Language** | Java (multi-lang via Thrift) | Scala/Java/Python | Java/Scala | Java/Scala |
| **Maturity** | Mature (Twitter origin) | Very mature | Mature | Mature |

---

## Getting Started: Hello World Topology

```java
// Spout: emits random sentences
public class RandomSentenceSpout extends BaseRichSpout {
    SpoutOutputCollector _collector;
    Random _rand;
    String[] sentences = {"the cow jumped over the moon",
                          "an apple a day keeps the doctor away"};

    public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
        _collector = collector;
        _rand = new Random();
    }

    public void nextTuple() {
        Utils.sleep(100);
        String sentence = sentences[_rand.nextInt(sentences.length)];
        _collector.emit(new Values(sentence), sentence); // msgId = sentence
    }

    public void ack(Object id) {}
    public void fail(Object id) {}

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("sentence"));
    }
}

// Bolt: splits sentences into words
public class SplitSentenceBolt extends BaseRichBolt {
    OutputCollector _collector;

    public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
        _collector = collector;
    }

    public void execute(Tuple tuple) {
        String sentence = tuple.getStringByField("sentence");
        for (String word : sentence.split(" ")) {
            _collector.emit(tuple, new Values(word));  // anchored
        }
        _collector.ack(tuple);
    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("word"));
    }
}
```
