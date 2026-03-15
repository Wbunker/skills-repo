# Dataflow — Capabilities

## Purpose

Fully managed Apache Beam stream and batch data processing service. Dataflow automatically provisions and manages a worker fleet, handling parallelization, fault tolerance, and scaling without user intervention. Uses the Apache Beam programming model — the same pipeline code runs on both batch and streaming workloads.

---

## Core Concepts

| Concept | Description |
|---|---|
| Pipeline | Directed acyclic graph (DAG) of PTransforms applied to PCollections |
| PCollection | Distributed, immutable dataset; the primary data abstraction in Beam |
| PTransform | Transformation applied to a PCollection; produces zero or more PCollections |
| ParDo | Parallel do: applies a DoFn element-by-element; most flexible transform |
| DoFn | User function executed per element within a ParDo; can emit 0 or many outputs |
| GroupByKey | Aggregates KV pairs by key; triggers shuffle across workers |
| Combine | Associative/commutative aggregation (sum, count, mean); more efficient than GroupByKey |
| Flatten | Merge multiple PCollections of the same type |
| Partition | Split one PCollection into multiple by a function |
| Window | Logical grouping of elements by time; enables streaming aggregations |
| Watermark | Estimate of how far behind real-time the pipeline has processed |
| Trigger | Controls when aggregation results are emitted for a window |
| Side input | Additional read-only input to a ParDo; broadcast data (e.g., lookup table) |
| Runner | Execution backend; Beam supports Dataflow, Direct (local), Spark, Flink runners |
| Job | Running pipeline instance on Dataflow; has job ID, state, metrics |
| Worker | Compute Engine VM executing pipeline steps; auto-scaled by Dataflow |
| Shuffle service | Managed off-worker shuffle for batch jobs; reduces worker disk/memory |
| Streaming Engine | Managed off-worker streaming state; reduces worker memory and disk |

---

## Apache Beam Programming Model

Beam provides a unified model for batch and streaming:

```
Input Source → Read → Transform(s) → Write → Output Sink
```

**Supported languages**: Java, Python, Go (production); Scala (via Scio, community)

**Key source/sink I/O connectors:**
- Cloud Storage (text, Avro, TFRecord)
- BigQuery (read via Storage Read API; write via Storage Write API or file loads)
- Pub/Sub (streaming source and sink)
- Bigtable (read/write)
- Spanner (read/write)
- Kafka (via KafkaIO)
- JDBC (databases)
- Datastore / Firestore

**Execution modes:**
- `--streaming=true` for streaming pipelines (Pub/Sub source required or unbounded)
- Batch (default) for bounded sources (GCS files, BigQuery tables)

---

## Windowing

Windows enable time-based grouping of streaming data:

| Window Type | Description | Use Case |
|---|---|---|
| Fixed (Tumbling) | Non-overlapping fixed-duration windows | Hourly aggregates, per-minute counts |
| Sliding | Overlapping windows; every N seconds of size M | Moving averages |
| Session | Per-key windows bounded by gaps in activity | User session analysis |
| Global | Single window for the entire pipeline (default) | Batch aggregations |

**Late data handling:**
- `AllowedLateness` specifies how long after the watermark to accept late elements
- Triggers control when to fire results: `AfterWatermark`, `AfterProcessingTime`, `AfterCount`, compound triggers
- Accumulation modes: `ACCUMULATING` (include previous pane results) vs `DISCARDING` (only new elements)

---

## Templates

### Classic Templates
- Compiled pipeline stored as a template file in Cloud Storage
- Fixed parameters at pipeline definition time; runtime parameters via ValueProvider
- Deploy once; run many times without recompiling
- Useful for operational simplicity when pipeline logic is stable

### Flex Templates
- Package pipeline as a Docker container image in Artifact Registry
- Dynamic parameters resolved at launch; supports complex schema inference
- Recommended for new pipelines; more flexible than Classic Templates
- `--parameters` passed at runtime map to pipeline options

### Google-Provided Templates (use as starting points)
- Pub/Sub to BigQuery
- Pub/Sub to Cloud Storage
- Cloud Storage Text to BigQuery
- BigQuery to Cloud Storage (export)
- Datastream to BigQuery (CDC)
- Cloud Spanner to BigQuery
- Bulk Compress/Decompress Cloud Storage Files
- Kafka to BigQuery

---

## Dataflow SQL

- Write Beam pipelines using SQL syntax in BigQuery-like dialect
- Sources: Pub/Sub topics, BigQuery tables, Cloud Storage
- Supports windowed aggregations, joins between streaming and batch
- Launch via Cloud Console or `gcloud dataflow sql query` command
- Good for analytics teams who prefer SQL over Java/Python pipeline code

---

## Shuffle Service (Batch)

- Managed shuffle infrastructure hosted off worker VMs
- Benefits: workers need less disk and memory; faster shuffle; better utilization
- Enabled by default for batch jobs in supported regions
- `--experiments=shuffle_mode=service` (may be set automatically)

---

## Streaming Engine

- Managed off-worker state for streaming pipelines
- Moves window state, timers, and aggregation buffers off worker memory to managed service
- Benefits: smaller worker VMs; faster autoscaling; more predictable memory usage
- Enable: `--enable_streaming_engine` flag
- Recommended for all new streaming pipelines

---

## Auto-Scaling

**Batch jobs:**
- Horizontal: adds/removes workers based on backlog and throughput
- Vertical autoscaling: Dataflow Prime (newer) automatically selects optimal machine type per stage
- `--autoscalingAlgorithm=THROUGHPUT_BASED` (default for batch)

**Streaming jobs:**
- Scales based on Pub/Sub backlog or throughput
- Set `--maxNumWorkers` to cap costs
- Streaming Engine enables faster scale-up response

**Worker configuration:**
- `--workerMachineType`: e.g., `n1-standard-4`, `n2-highmem-8`
- `--numWorkers`: initial worker count
- `--maxNumWorkers`: autoscaling ceiling
- `--diskSizeGb`: persistent disk per worker (batch)
- `--workerRegion` / `--workerZone`: worker placement

---

## Dataflow vs Dataproc

| Dimension | Dataflow | Dataproc |
|---|---|---|
| Programming model | Apache Beam (unified batch/stream) | Spark, Hadoop, Flink, Hive, Pig |
| Cluster management | Fully managed, serverless | Manages clusters (or Serverless Spark) |
| Streaming | Native, first-class | Spark Streaming; less flexible |
| Existing code | Requires rewrite to Beam | Run existing Spark/Hadoop code as-is |
| Startup time | ~2-3 min | ~90 sec (standard cluster already running: immediate) |
| Best for | New streaming pipelines, Apache Beam workloads | Lift-and-shift Spark/Hadoop; Spark ML; HBase |

---

## Stateful Processing

- `DoFn` can maintain per-key state and timers (`@StateId`, `@TimerId` in Java; `ReadModifyWriteStateSpec`, `CombiningStateSpec` in Python)
- Enables: deduplication, sessionization, exactly-once semantics, per-key rate limiting
- State is durable; survives worker restarts
- With Streaming Engine: state stored in managed service, not worker memory

---

## Security

- Workers run in a GCP project VPC; can specify `--network` and `--subnetwork`
- Private IP workers: `--no-use-public-ips` (requires Cloud NAT for package downloads)
- Service account: `--serviceAccount` (defaults to Compute Engine default SA; use dedicated SA)
- Customer-managed encryption keys (CMEK): `--dataflowKmsKey`
- VPC Service Controls: Dataflow jobs respect VPC-SC perimeter

---

## Monitoring and Observability

- Job graph visible in Dataflow UI; step-level throughput, latency, errors
- Metrics: elements added, elements remaining, system lag (streaming), worker CPU
- Cloud Monitoring: Dataflow metrics namespace `dataflow.googleapis.com`
- Cloud Logging: worker logs, pipeline logs (severity-filtered)
- Job snapshots: capture streaming pipeline state for restarts without data loss
