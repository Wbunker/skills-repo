# Streaming Systems — The Evolution of Large-Scale Data Processing (Chapter 10)

The final chapter traces the history of large-scale data processing systems, focusing on ten systems and their contributions and limitations. This is the intellectual lineage of modern streaming.

---

## 1. MapReduce (Google, ~2004)

**What it is**: a programming model and execution engine for batch processing at scale on commodity hardware.

**Architecture**:
- **Map**: apply a function to each input record, emitting key-value pairs
- **Shuffle**: sort and group all pairs by key
- **Reduce**: apply a reduction function to each group, emitting output records

**Contributions**:
- **Scalability**: runs on thousands of commodity machines; automatically parallelizes
- **Fault tolerance**: automatic re-execution of failed tasks; no user involvement required
- **Unified programming model**: simple map/reduce abstraction hides distributed systems complexity
- **Democratized large-scale processing**: made petabyte-scale computation practical without specialized hardware

**Limitations**:
- Batch-only: requires bounded input; no streaming
- Low-level API: users must manually chain MapReduce jobs for complex pipelines
- High overhead: disk-based shuffle is expensive; Hadoop MapReduce latency is minutes to hours
- No expressive pipeline composition: multi-step computations require multiple chained MR jobs

---

## 2. Hadoop (Yahoo/Apache, ~2006)

**What it is**: the open-source reimplementation of Google MapReduce + GFS (as HDFS).

**Contributions**:
- **Democratization of large-scale batch processing**: made MapReduce accessible without Google-scale infrastructure budgets
- **Ecosystem catalyst**: spawned Hive, Pig, HBase, and dozens of data tools
- **HDFS**: reliable, distributed file system; the foundation of the Hadoop data lake architecture

**Limitations**:
- Inherited all MapReduce limitations (batch-only, high latency, low-level API)
- YARN resource management complex to operate correctly
- Not designed for interactive queries or streaming

---

## 3. Flume / FlumeJava (Google, ~2010)

**What it is**: a high-level pipeline API built on top of MapReduce, with an optimizer that fuses stages.

**Architecture**:
- User writes a high-level pipeline as a graph of transformations (PCollections + PTransforms)
- The **optimizer** fuses compatible stages to minimize unnecessary shuffle steps
- The optimized pipeline is executed as one or more MapReduce jobs

**Contributions**:
- **Composable pipeline API**: chains of operations expressed as code; much more ergonomic than raw MR
- **Stage fusion**: optimizer automatically merges consecutive nongrouping transforms, eliminating unnecessary disk I/O between stages
- **Conceptual precursor to Beam**: FlumeJava's PCollection and PTransform concepts became the Beam Model's foundation
- **Execution independence**: the pipeline definition is separate from the execution engine; an early form of portability

**Limitations**:
- Still batch-only (executed on MapReduce)
- Optimizer limited to nongrouping fusion; grouping steps still require full MR cycles

---

## 4. Apache Storm (Twitter/Apache, ~2011)

**What it is**: the first widely adopted open-source streaming processing system.

**Architecture**:
- **Topology**: a DAG of Spouts (sources) and Bolts (processing nodes)
- Messages flow between nodes in the DAG in real time
- No built-in state management (operators must manage state themselves)

**Contributions**:
- **Demonstrated that low-latency streaming at scale was possible** on commodity hardware
- **DAG-based topology model**: influenced all subsequent streaming systems
- **Popularized stream processing** as a discipline distinct from batch

**Limitations**:
- **Weak consistency**: offered at-most-once (fast but lossy) or at-least-once (via acking) — no exactly-once
- **No built-in state management**: users must implement their own state stores
- **Processing-time only**: no event-time reasoning, no watermarks, no windowing model
- Required the Lambda Architecture alongside batch for correct results

---

## 5. Apache Spark (Berkeley/Apache, ~2012–2013)

**What it is**: an in-memory batch engine (Spark Core) extended with a micro-batch streaming layer (Spark Streaming 1.x) and later a true streaming API (Structured Streaming).

**Contributions**:
- **RDD model**: Resilient Distributed Datasets — in-memory, fault-tolerant distributed collections; dramatically faster than disk-based MapReduce for iterative algorithms
- **Unified engine**: same engine for batch, ML, graph processing, SQL, and (later) streaming
- **Micro-batch streaming**: Spark Streaming 1.x divides streams into fixed-size time batches; each batch is a standard Spark job → effective exactly-once semantics inherited from batch ACID
- **Structured Streaming**: higher-level continuous processing model with better exactly-once guarantees and SQL integration

**Limitations**:
- **Micro-batch latency floor**: Spark Streaming 1.x minimum latency bounded by batch interval (hundreds of ms to seconds); unacceptable for use cases requiring sub-second latency
- **Spark Streaming 1.x API complexity**: required understanding both RDD API and DStream API
- **Event-time support**: came late (Structured Streaming); early versions were processing-time only

---

## 6. MillWheel (Google, ~2013)

**What it is**: Google's internal general-purpose stream processing system; the direct precursor to Cloud Dataflow.

**Architecture**:
- Graph of computations connected by keyed streams
- Per-key persistent state stored in Bigtable/Spanner
- Centralized watermark service for event-time progress tracking

**Contributions**: MillWheel is the system where most core streaming correctness concepts originated:
- **Exactly-once semantics**: shuffle-level deduplication via record IDs; first major streaming system to achieve this
- **Persistent per-key state**: durable state stored in a distributed KV store; accessible and mutable by each computation
- **Watermarks**: the concept of watermarks as a metric for event-time completeness; MillWheel introduced this to the streaming field
- **Out-of-order processing**: explicit handling of late data via low watermarks and configurable late-data windows
- **Low-latency timers**: per-key timers firing at specific event or processing times

**Limitations**:
- Internal to Google; not publicly available
- Complex operational model (dependency on Bigtable, centralized watermark aggregation)

---

## 7. Google Cloud Dataflow (~2015)

**What it is**: the public manifestation of Google's internal streaming work; a managed, serverless unified batch+streaming processing service.

**Architecture**:
- User writes pipelines using the Dataflow SDK (later donated to Apache as the Beam SDK)
- Pipelines are executed by the Dataflow managed service (no cluster management required)
- Unified model: same pipeline code runs in batch mode (for bounded data) or streaming mode (for unbounded data)

**Contributions**:
- **The Dataflow Model**: unified batch and streaming under a single programming model (the What/Where/When/How framework described throughout this book)
- **Serverless**: no cluster provisioning; the service handles scaling, fault recovery, and optimization
- **Melded Flume + MillWheel**: FlumeJava's composable pipeline API + MillWheel's streaming guarantees
- **Open-sourced as Apache Beam**: made the Dataflow Model available to the broader community

**Limitations**:
- Managed service (GCP lock-in for the runner); the open-source Beam SDK solves the portability issue

---

## 8. Apache Kafka (LinkedIn/Apache, ~2011, maturing 2013+)

**What it is**: a durable, replayable, distributed log for stream transport.

**Architecture**:
- Topics partitioned across brokers
- Producers append records; consumers read at their own pace with offset tracking
- Configurable retention; log compaction for key-value semantics
- Kafka Streams: a stream processing library built on top of Kafka

**Contributions**:
- **Durability and replayability**: unlike ephemeral message queues, Kafka retains records for configurable periods; consumers can replay from any offset
- **Foundation for exactly-once across other systems**: Kafka's replayability enables source checkpointing, which is required for end-to-end exactly-once in Flink, Spark, Storm, and Kafka Streams
- **Popularization of streams-and-tables theory**: Kafka's engineering team (notably Jay Kreps) published influential work on log-structured data and the streams-and-tables duality
- **Kafka Streams and ksqlDB**: brought stream processing directly into the Kafka ecosystem

**Limitations**:
- Kafka itself is a transport system, not a processing system; rich transformations require Kafka Streams or external systems
- Exactly-once in Kafka Streams (idempotent producers + transactions) came later (Kafka 0.11+)

---

## 9. Apache Flink (~2014–2015)

**What it is**: the first fully open-source stream processing system with Dataflow/Beam-equivalent semantics.

**Architecture**:
- True streaming (not micro-batch): records are processed one at a time as they arrive
- Chandy-Lamport distributed snapshots for exactly-once state checkpointing
- Operator-level watermarks propagated in-band with data
- Rich state backends: in-memory (HashMap), RocksDB (embedded KV store for large state)

**Contributions**:
- **First open-source system with full Dataflow Model semantics**: watermarks, event-time windowing, exactly-once, persistent state — all available in open source
- **Chandy-Lamport snapshots**: barrier-based distributed checkpointing provides exactly-once without centralized coordination
- **Savepoints**: named, portable checkpoints that enable pipeline upgrades, A/B testing, and time travel
- **Rapid adoption**: became the leading open-source streaming system ca. 2015–2016

**Limitations**:
- Flink's SQL support lagged behind its DataStream API for several years
- Stateful stream processing with large state requires careful RocksDB tuning

---

## 10. Apache Beam (~2016)

**What it is**: a unified programming model and portability layer for data processing pipelines.

**Architecture**:
- **SDK**: the Beam SDK (available in Java, Python, Go) provides the PCollection/PTransform/Pipeline API
- **Runners**: pluggable execution backends — Apache Flink, Apache Spark, Google Cloud Dataflow, Apache Apex, etc.
- **Portability**: a pipeline written with the Beam SDK can run on any supported runner without code changes

**Contributions**:
- **Unified batch + streaming model**: the Beam Model (What/Where/When/How) handles both uniformly
- **Portability**: write once, run anywhere — pipelines are not tied to a specific execution engine
- **Lingua franca for programmatic data processing**: Beam is becoming a standard API that multiple engines implement
- **Formalization of the streaming model**: the Beam project formalized and documented the watermark, trigger, and accumulation concepts as a standard model

**Limitations**:
- Portability abstraction has a cost: advanced features of specific runners may not be accessible via the Beam API
- Python SDK performance historically lagged the Java SDK
- Cross-language pipelines (mixing Java + Python operators in one pipeline) add operational complexity

---

## The Lineage

```
MapReduce (2004)
    └── Hadoop (2006) — open source
    └── FlumeJava (2010) — composable API + optimizer
            └── Cloud Dataflow (2015) — unified batch+streaming, serverless
                    └── Apache Beam (2016) — open standard SDK + multiple runners

MillWheel (2013) — exactly-once, watermarks, persistent state
    └── Cloud Dataflow (2015) — merged Flume + MillWheel

Storm (2011) — first open-source streaming
Spark (2012) — in-memory batch + micro-batch streaming

Kafka (2011) — durable log; replayability; streams-and-tables theory

Flink (2014) — first open-source system with full Dataflow semantics
```

The evolution moves consistently toward: **correctness** (exactly-once), **expressiveness** (unified batch+streaming), **portability** (Beam), and **accessibility** (managed services, SQL interfaces).
