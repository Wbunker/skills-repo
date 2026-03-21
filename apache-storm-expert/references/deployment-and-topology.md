# Storm Deployment and Topology Development
## Chapter 2: Deployment, Topology Options, and Cluster Setup

---

## Local Mode vs. Cluster Mode

### Local Mode (Development)

Runs Storm in a single JVM process — no cluster required. Ideal for development and unit testing.

```java
LocalCluster cluster = new LocalCluster();
cluster.submitTopology("test-topology", conf, builder.createTopology());
Utils.sleep(10000);  // run for 10 seconds
cluster.killTopology("test-topology");
cluster.shutdown();
```

- All components (Nimbus, Supervisors, workers) simulated in one process
- Thread-based parallelism
- No ZooKeeper dependency (uses in-process ZooKeeper)
- Identical topology code — only submission method changes

### Cluster Mode (Production)

Submit to a running Storm cluster via `StormSubmitter`:

```java
StormSubmitter.submitTopology("word-count", conf, builder.createTopology());
```

Requires:
- Running Nimbus (typically `storm nimbus &`)
- Running Supervisors on each worker node (`storm supervisor &`)
- Running ZooKeeper ensemble
- Topology JAR on the submitting machine

---

## Storm Installation

### Prerequisites

- Java 8+ (JDK)
- Python 2.6+ (Storm CLI uses Python)
- Apache ZooKeeper 3.4+

### Configuration: `storm.yaml`

Located at `$STORM_HOME/conf/storm.yaml`. Key settings:

```yaml
# ZooKeeper connection
storm.zookeeper.servers:
  - "zk1.example.com"
  - "zk2.example.com"
storm.zookeeper.port: 2181

# Nimbus host (Storm 1.x single Nimbus)
nimbus.seeds: ["nimbus.example.com"]

# Local directory for Storm data
storm.local.dir: "/var/storm"

# Supervisor slot ports (one per worker process)
supervisor.slots.ports:
  - 6700
  - 6701
  - 6702
  - 6703

# Worker heap memory (MB)
worker.heap.memory.mb: 768

# UI port
ui.port: 8080
```

### Starting the Cluster

```bash
# On Nimbus node
storm nimbus &
storm ui &       # optional Storm UI web interface

# On each Supervisor node
storm supervisor &

# On log viewer nodes (optional)
storm logviewer &
```

---

## Topology Development Workflow

### 1. Build the Topology

```java
TopologyBuilder builder = new TopologyBuilder();

// Add spout: component-id, spout instance, parallelism hint (executors)
builder.setSpout("kafka-spout", new KafkaSpout(kafkaConfig), 2);

// Add bolts with stream groupings
builder.setBolt("parse-bolt", new ParseBolt(), 4)
       .shuffleGrouping("kafka-spout");

builder.setBolt("count-bolt", new CountBolt(), 4)
       .fieldsGrouping("parse-bolt", new Fields("key"));

builder.setBolt("persist-bolt", new HBaseBolt("table", mapper), 2)
       .shuffleGrouping("count-bolt");
```

### 2. Configure the Topology

```java
Config conf = new Config();

// Number of worker JVM processes
conf.setNumWorkers(3);

// Number of acker threads
conf.setNumAckers(2);

// Message timeout (seconds) — tuples not acked within this window are replayed
conf.setMessageTimeoutSecs(30);

// Max spout pending (backpressure) — max un-acked tuples per spout task
conf.setMaxSpoutPending(1000);

// Debug mode (verbose tuple tracking — performance overhead)
conf.setDebug(false);

// Custom config values accessible in bolts/spouts via TopologyContext
conf.put("redis.host", "redis.example.com");
conf.put("hbase.root.dir", "hdfs://namenode:9000/hbase");
```

### 3. Submit the Topology

```bash
# Package as uber-JAR, then:
storm jar target/my-topology-1.0.jar com.example.MyTopology my-topology-name
```

---

## Topology Lifecycle Management

### Submitting

```bash
storm jar topology.jar com.example.WordCountTopology word-count
```

### Checking Status

```bash
storm list
# Shows: topology name, id, status, uptime, num workers, num executors, num tasks
```

### Killing

```bash
storm kill word-count
storm kill word-count -w 30   # wait 30 seconds before killing (drain in-flight tuples)
```

### Deactivating / Reactivating

Deactivating stops spouts from calling `nextTuple()` but keeps the topology running:

```bash
storm deactivate word-count
storm activate word-count
```

### Rebalancing

Adjust parallelism without redeploying the topology:

```bash
# Change number of workers
storm rebalance word-count -n 5

# Change executor count for a specific bolt
storm rebalance word-count -e count-bolt=8

# Combined
storm rebalance word-count -n 5 -e split-bolt=6 -e count-bolt=8
```

Rebalancing causes a brief pause in processing while tasks are reassigned.

---

## Config Class Key Settings

| Config Key | Default | Description |
|-----------|---------|-------------|
| `topology.workers` | 1 | Number of worker JVMs across the cluster |
| `topology.acker.executors` | 1 | Acker threads; set to 0 to disable acking (at-most-once) |
| `topology.message.timeout.secs` | 30 | Seconds before un-acked tuple triggers fail() |
| `topology.max.spout.pending` | null (unlimited) | Max un-acked tuples per spout task; enables backpressure |
| `topology.max.task.parallelism` | null | Cap on any component's parallelism |
| `topology.debug` | false | Logs every emitted/transferred tuple — performance cost |
| `topology.kryo.register` | [] | Custom Kryo serializers for non-standard types |
| `topology.fall.back.on.java.serialization` | true | Fall back to Java serialization for unregistered types |
| `topology.stats.sample.rate` | 0.05 | Fraction of tuples to sample for UI stats |
| `supervisor.worker.timeout.secs` | 30 | Seconds before supervisor declares a worker dead |
| `nimbus.task.timeout.secs` | 30 | Seconds before Nimbus reassigns an unresponsive task |

---

## Multi-Lang Support

Storm supports non-JVM components via the **ShellBolt** and **ShellSpout** mechanism. Components communicate via JSON over stdin/stdout.

```java
// Python bolt
public class PythonBolt extends ShellBolt implements IRichBolt {
    public PythonBolt() {
        super("python", "mybolt.py");
    }
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("result"));
    }
}
```

Python bolt (`mybolt.py`) uses the `streamparse` library or the raw Storm multilang protocol.

**streamparse** is the recommended Python Storm library — provides decorator-based API for spouts and bolts.

---

## Storm UI

Web-based interface at `http://nimbus-host:8080`.

Shows per-topology:
- Status, uptime, workers, executors, tasks
- Topology stats: emitted, transferred, acked, failed tuple counts (10m/3h/1d/all-time windows)
- Component-level: spout/bolt stats, latency, capacity

Capacity metric: `(execute latency ms × execute count) / (window seconds × 1000)`. Values near 1.0 indicate the bolt is saturated.

---

## Packaging Best Practices

- Build an **uber-JAR** (fat JAR with all dependencies) using Maven Shade Plugin or Gradle Shadow Plugin
- Exclude Storm JARs from the uber-JAR (Storm provides them on the classpath):
  ```xml
  <dependency>
      <groupId>org.apache.storm</groupId>
      <artifactId>storm-core</artifactId>
      <version>2.4.0</version>
      <scope>provided</scope>  <!-- do not bundle -->
  </dependency>
  ```
- Exclude conflicting serialization libraries (Kryo version mismatches are a common issue)
