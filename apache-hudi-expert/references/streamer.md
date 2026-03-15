# Hudi Streamer
## Chapter 7: Continuous Ingestion, Sources, Schema Evolution, Data Quality, Operations

---

## What Is Hudi Streamer?

**Hudi Streamer** (formerly DeltaStreamer, renamed in Hudi 0.14) is a production-grade continuous ingestion tool built into the Hudi library. It provides a self-contained Spark application that reads from various sources and writes to Hudi tables with:

- Automatic checkpointing (exactly-once semantics)
- Built-in schema evolution
- Pluggable transformers
- Data quality assurance (DQA)
- Multiple source connectors (Kafka, DFS, JDBC, etc.)

```
Source (Kafka / S3 / JDBC / ...)
         ↓
   Hudi Streamer
   ┌─────────────────────────────────────────────┐
   │  Source Reader    → reads raw records        │
   │  Schema Provider  → resolves schema          │
   │  Transformer      → applies transformations  │
   │  DQA              → validates data quality   │
   │  Key Generator    → computes record key      │
   │  Hudi Write       → upsert/insert to table   │
   │  Checkpoint       → saves read position      │
   └─────────────────────────────────────────────┘
         ↓
   Hudi Table (COW or MOR)
```

---

## Getting Started

### Basic Spark Submit

```bash
spark-submit \
  --class org.apache.hudi.utilities.streamer.HoodieStreamer \
  hudi-utilities-bundle_2.12-*.jar \
  --table-type MERGE_ON_READ \
  --base-path s3://bucket/orders/ \
  --target-table orders \
  --source-class org.apache.hudi.utilities.sources.JsonKafkaSource \
  --source-ordering-field ts \
  --props s3://bucket/config/streamer.properties \
  --schemaprovider-class org.apache.hudi.utilities.schema.SchemaRegistryProvider \
  --continuous \       # run as a long-lived streaming job
  --op UPSERT
```

### Continuous vs One-Shot Mode

| Mode | Flag | Use Case |
|------|------|---------|
| Continuous | `--continuous` | Long-running streaming job; reads as data arrives |
| One-shot | (no flag) | Run once, read available data, exit; schedule via Airflow |

---

## Source Connectors

### Kafka Source

```properties
# streamer.properties
hoodie.streamer.source.kafka.topic=orders-events
hoodie.streamer.kafka.source.maxEvents=500000    # max records per microbatch
bootstrap.servers=kafka-broker:9092
auto.offset.reset=earliest
schema.registry.url=http://schema-registry:8081
```

```bash
--source-class org.apache.hudi.utilities.sources.JsonKafkaSource
# or for Avro:
--source-class org.apache.hudi.utilities.sources.AvroKafkaSource
```

Checkpoints are stored in the Hudi table's `.hoodie/` directory — Kafka offsets committed only after successful Hudi write.

### DFS Source (S3 / HDFS / GCS)

Reads files from object storage — useful for landing zone → Hudi ingestion.

```properties
hoodie.streamer.source.dfs.root=s3://bucket/landing/orders/
hoodie.streamer.source.dfs.filter.dueto.starttime=true  # only files newer than checkpoint
```

```bash
--source-class org.apache.hudi.utilities.sources.ParquetDFSSource
# or:
--source-class org.apache.hudi.utilities.sources.JsonDFSSource
--source-class org.apache.hudi.utilities.sources.CsvDFSSource
```

Checkpoint stores the last processed file path/timestamp.

### JDBC Source

```properties
hoodie.streamer.jdbc.url=jdbc:postgresql://host:5432/mydb
hoodie.streamer.jdbc.user=hudi_user
hoodie.streamer.jdbc.password=secret
hoodie.streamer.jdbc.table.name=orders
hoodie.streamer.jdbc.incr.column.name=updated_at   # incremental column
hoodie.streamer.jdbc.incr.pull=true
```

```bash
--source-class org.apache.hudi.utilities.sources.JdbcSource
```

Reads rows incrementally based on `incr.column.name` (e.g., `updated_at > last_checkpoint_value`).

### S3 Events Source

Reads from S3 event notifications (via SQS) to trigger ingestion when new files land:

```bash
--source-class org.apache.hudi.utilities.sources.S3EventsSource
```

### Debezium Source

Reads Debezium CDC events from Kafka (database change streams):

```bash
--source-class org.apache.hudi.utilities.sources.debezium.PostgresDebeziumSource
# or:
--source-class org.apache.hudi.utilities.sources.debezium.MysqlDebeziumSource
```

Automatically handles Debezium envelope format (before/after/op fields) and maps to Hudi write operations.

---

## Schema Providers

Schema providers tell Streamer what schema incoming records conform to.

### Schema Registry Provider (Confluent)

```properties
hoodie.streamer.schemaprovider.registry.url=http://schema-registry:8081
hoodie.streamer.schemaprovider.registry.schemaconverter=org.apache.hudi.utilities.schema.converter.JsonToAvroSchemaConverter
```

```bash
--schemaprovider-class org.apache.hudi.utilities.schema.SchemaRegistryProvider
```

### File-Based Schema Provider

```properties
hoodie.streamer.schemaprovider.source.schema.file=s3://bucket/schemas/orders.avsc
hoodie.streamer.schemaprovider.target.schema.file=s3://bucket/schemas/orders-target.avsc
```

```bash
--schemaprovider-class org.apache.hudi.utilities.schema.FilebasedSchemaProvider
```

### Inline Schema Provider

Define schema directly in properties (for simple cases):

```bash
--schemaprovider-class org.apache.hudi.utilities.schema.SparkAvroSchemaProvider
```

---

## Transformers

Transformers apply transformations between source read and Hudi write. Multiple transformers can be chained.

### SQL Transformer

Apply any Spark SQL expression:

```properties
hoodie.streamer.transformer.sql=SELECT order_id, customer_id, amount * 1.1 AS amount_with_tax, CURRENT_TIMESTAMP() AS processed_at FROM <SRC>
```

```bash
--transformer-class org.apache.hudi.utilities.transform.SqlQueryBasedTransformer
```

### FlattenHierarchyTransformer

Flatten nested JSON/Avro structures:

```bash
--transformer-class org.apache.hudi.utilities.transform.FlatteningTransformer
```

### Chaining Transformers

```properties
hoodie.streamer.transformer.class=org.apache.hudi.utilities.transform.SqlQueryBasedTransformer,org.apache.hudi.utilities.transform.FlatteningTransformer
```

---

## Schema Evolution on Write

When the source schema changes (new column added), Hudi Streamer handles it automatically if configured:

```properties
hoodie.schema.on.read.enable=true
hoodie.datasource.write.reconcile.schema=true
```

**Supported schema changes** (same as direct write API — see `writing.md`):
- Add nullable column (new column defaults to null for existing records)
- Widen numeric types (int → long)
- Add column with default value (Hudi 0.14+)

**Unsupported**: changing partition columns, narrowing types, rename without config.

### Handling Heterogeneous Events

When a Kafka topic carries multiple event types with different schemas:

```properties
# Use a schema provider that can dynamically resolve schema per record
hoodie.streamer.schemaprovider.class=org.apache.hudi.utilities.schema.SchemaRegistryProvider
# Schema Registry subject naming strategy per event type
```

Or use a SQL transformer to normalize to a common schema before writing.

---

## Data Quality Assurance (DQA)

Hudi Streamer supports DQA rules that validate records before writing. Failed records can be routed to a dead-letter queue.

```properties
# Enable DQA
hoodie.streamer.dqa.enabled=true
hoodie.streamer.dqa.config.file=s3://bucket/config/dqa-rules.yaml
```

Example DQA rules file:
```yaml
rules:
  - field: order_id
    type: NOT_NULL
  - field: amount
    type: RANGE
    min: 0
    max: 1000000
  - field: customer_id
    type: REGEX
    pattern: "^[A-Z]{2}\\d{8}$"
```

Failed records are either:
- Dropped (logged)
- Routed to a dead-letter Hudi table or Kafka topic

---

## Operational Options

### Checkpointing

Checkpoints are stored in the Hudi commit metadata under `.hoodie/`. On restart, Streamer reads the last checkpoint and resumes from there.

```properties
# Override checkpoint (force re-read from a specific position)
hoodie.streamer.checkpoint.force.skip=true
hoodie.datasource.write.payload.class=...
```

```bash
# Reset checkpoint via CLI
hoodie-cli> set --conf hoodie.streamer.checkpoint.key=20240115100000000
```

### Rate Limiting

```properties
hoodie.streamer.source.kafka.maxEvents=100000    # max records per batch
hoodie.streamer.ingest.batch.size=50000          # records per write batch
hoodie.streamer.min.sync.interval.seconds=60     # minimum time between syncs
```

### Error Handling

```properties
hoodie.streamer.kafka.source.maxReattempts=3       # retry failed Kafka reads
hoodie.datasource.write.ignore.failed.partition=true  # skip bad partitions vs fail job
```

### Multi-Table Ingestion

Run multiple Streamer instances (one per Hudi table) via **HoodieMultiTableStreamer**:

```bash
spark-submit \
  --class org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer \
  hudi-utilities-bundle.jar \
  --base-config-path s3://bucket/config/base.properties \
  --table-config-paths s3://bucket/config/orders.properties,s3://bucket/config/products.properties
```

Each table config specifies its own source, schema, key generator, and Hudi table properties.

---

## Common Kafka → Hudi Pattern

```
Kafka Topic: order-events (Avro, Schema Registry)
         ↓
Hudi Streamer (continuous mode)
  Source: AvroKafkaSource
  Schema: SchemaRegistryProvider
  Transform: SQL (add processed_at column)
  Key: order_id | Partition: order_date
  Operation: UPSERT
  Table type: MOR (high write throughput)
         ↓
Hudi MOR Table: s3://datalake/orders/
  Compaction: async, every 10 deltacommits
  Cleaning: retain 20 commits
         ↓
Query via Trino / Athena (snapshot or read-optimized)
```
