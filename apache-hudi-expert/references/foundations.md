# Apache Hudi Foundations
## Chapters 1–2: Architecture, Table Types, Hudi Stack, Getting Started

---

## What Is Apache Hudi?

Hudi (Hadoop Upserts Deletes and Incrementals) was created at Uber to solve a core problem: **how do you efficiently upsert and delete individual records in a data lake built on immutable file formats like Parquet?**

Traditional data lakes treated files as immutable — updates meant rewriting entire partitions. Hudi adds a transactional layer that enables:
- Row-level upserts and deletes
- ACID transactions on object storage
- Incremental data consumption (only process what changed)
- Time travel and snapshot isolation

---

## The Hudi Stack

```
┌──────────────────────────────────────────────────────┐
│  USER ACCESS                                          │
│  Spark SQL │ Trino │ Presto │ Athena │ BigQuery      │
├──────────────────────────────────────────────────────┤
│  PROGRAMMING API                                      │
│  DataSource API │ Hudi Streamer │ HoodieJavaClient    │
├──────────────────────────────────────────────────────┤
│  STORAGE ENGINE                                       │
│  Write flow │ Indexing │ Table services               │
│  Concurrency control │ Schema evolution               │
├──────────────────────────────────────────────────────┤
│  TABLE FORMAT LAYER                                   │
│  Native Table Format: Timeline + File Layout          │
│  Pluggable Table Format: Iceberg/Delta compatibility  │
├──────────────────────────────────────────────────────┤
│  OBJECT STORAGE                                       │
│         S3  │  ADLS  │  GCS  │  HDFS                 │
└──────────────────────────────────────────────────────┘
```

**Pluggable Table Format** allows Hudi's write/read engine to work with Iceberg or Delta Lake table formats — Hudi's storage engine capabilities (indexing, table services, Streamer) can be layered on top of those formats.

---

## The Timeline

The timeline is Hudi's **commit log** — the source of truth for all table state. It lives in the `.hoodie/` directory at the table root.

```
.hoodie/
├── 20240115100000000.commit          ← completed write
├── 20240115100000000.commit.requested ← write started
├── 20240115110000000.deltacommit     ← MOR log write
├── 20240115120000000.compaction.requested ← compaction plan
├── 20240115120000000.commit          ← compaction completed
├── 20240115130000000.clean           ← cleaning completed
├── 20240115140000000.rollback        ← failed write rolled back
└── .hoodie_properties                ← table config (type, name, etc.)
```

### Instant States

Each action on the timeline has three states:

| State | File Suffix | Meaning |
|-------|------------|---------|
| Requested | `.requested` | Action is planned but not started |
| Inflight | `.inflight` | Action is in progress |
| Completed | (no suffix) | Action is successfully committed |

A write that fails leaves `.inflight` files. On the next write, Hudi detects and rolls back the incomplete inflight instant.

### Action Types

| Action | Description |
|--------|-------------|
| `commit` | COW write completed |
| `deltacommit` | MOR log write completed |
| `compaction` | MOR log files merged into Parquet base |
| `clean` | Old file versions removed |
| `rollback` | Failed write undone |
| `clustering` | File reorganization completed |
| `savepoint` | Checkpoint preventing cleaning before this instant |

---

## File Layout

```
s3://bucket/my-table/
├── .hoodie/                           ← timeline
├── partition=2024-01-15/
│   ├── <fileId1>_<timestamp>.parquet  ← base file
│   ├── <fileId1>_<timestamp>.log      ← log file (MOR only)
│   └── <fileId2>_<timestamp>.parquet  ← another file group
└── partition=2024-01-16/
    └── <fileId3>_<timestamp>.parquet
```

### File Group

A **file group** is identified by a stable `fileId` and contains all versions of a logical data shard within a partition:

```
File Group (fileId = abc123):
  Version 1: abc123_20240101.parquet               ← base file v1
  Version 2: abc123_20240115.parquet               ← base file v2 (after compaction)
             abc123_20240115.log                   ← log file (MOR writes since v2)
             abc123_20240116.log
```

### File Slice

A **file slice** is the set of files representing the table state at a given instant:
- **Latest file slice**: the newest base file + all log files written after it
- **Historical file slice**: an older base file (used for time travel)

---

## Copy-on-Write (COW) vs Merge-on-Read (MOR)

### Copy-on-Write

```
Upsert incoming records
        ↓
Find affected file groups (via index lookup)
        ↓
Rewrite entire Parquet base file with merged records
        ↓
Commit: new .parquet file is the current file slice
```

- **Write**: expensive (full file rewrite for any update)
- **Read**: fast (pure Parquet scan, no merge)
- **Best for**: read-heavy workloads, infrequent updates, BI/analytics

### Merge-on-Read

```
Upsert incoming records
        ↓
Append new/changed records to .log file (Avro format)
        ↓
Commit: deltacommit instant on timeline

At read time (Snapshot query):
  base file + log files → merged on the fly by reader
```

- **Write**: fast (append to log only)
- **Read**: slower for snapshot (merge overhead); fast for read-optimized (base only)
- **Best for**: streaming ingestion, high-frequency upserts, CDC workloads

| Aspect | COW | MOR |
|--------|-----|-----|
| Write latency | High (file rewrite) | Low (log append) |
| Read latency | Low (pure Parquet) | Medium-High (snapshot merge) |
| Storage amplification | Medium (versioned base files) | High before compaction |
| Compaction needed | No | Yes |
| Query types | Snapshot, Time Travel, Incremental | All + Read Optimized |

---

## Getting Started

### Initialize Spark Session

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("hudi-quickstart") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .config("spark.sql.extensions",
            "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .getOrCreate()
```

### Create a Table

```sql
-- COW table (default)
CREATE TABLE purchases (
    purchase_id  BIGINT,
    customer_id  BIGINT,
    amount       DOUBLE,
    category     STRING,
    ts           TIMESTAMP
) USING hudi
PARTITIONED BY (category)
TBLPROPERTIES (
    'hoodie.table.name'                      = 'purchases',
    'hoodie.datasource.write.recordkey.field' = 'purchase_id',
    'hoodie.datasource.write.precombine.field'= 'ts'
);

-- MOR table
CREATE TABLE purchases_mor (...)
USING hudi
TBLPROPERTIES (
    'hoodie.table.type' = 'MERGE_ON_READ',
    ...
);
```

### Basic Operations

```python
# Upsert (default operation)
df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(table_path)

# Query latest snapshot
spark.read.format("hudi").load(table_path).show()

# Time travel
spark.read.format("hudi") \
    .option("as.of.instant", "20240115100000000") \
    .load(table_path)
```

### Key Table Properties

```properties
hoodie.table.name=purchases
hoodie.table.type=COPY_ON_WRITE          # or MERGE_ON_READ
hoodie.datasource.write.recordkey.field=purchase_id
hoodie.datasource.write.partitionpath.field=category
hoodie.datasource.write.precombine.field=ts
hoodie.datasource.write.hive_style_partitioning=true
```

---

## Table Design Decisions

### Choosing Record Key Fields

- Must be **unique within a partition** (unless using global index)
- Composite keys: `hoodie.datasource.write.recordkey.field=col1,col2`
- Immutable once table is created

### Choosing the Precombine Field

- Used to resolve duplicates when multiple records share the same key
- Record with the **maximum value** of this field wins
- Typically: `updated_at`, `event_timestamp`, `version`, `sequence_number`

### Choosing Partition Columns

- Same tradeoffs as Iceberg/Delta: avoid over-partitioning (too many small files)
- Common schemes: `date`, `country`, `category`, `year/month/day`
- Hudi supports Hive-style partitioning (`partition=value/`) by default

---

## Hudi vs Iceberg vs Delta Lake

| Capability | Hudi | Iceberg | Delta Lake |
|-----------|------|---------|------------|
| Origin | Uber | Netflix | Databricks |
| Write model | COW + MOR | COW + MOR (via delete files) | COW + deletion vectors |
| Timeline/log | `.hoodie/` action log | Metadata JSON + manifests | `_delta_log/` JSON |
| Indexing | Bloom, bucket, record-level, HBase | Metadata table stats | Data skipping stats |
| Incremental reads | Native (core feature) | Via snapshots | Via CDF (Change Data Feed) |
| Compaction | Native table service | `rewriteDataFiles` action | `OPTIMIZE` command |
| Streaming ingestion | Hudi Streamer (built-in tool) | External (Flink, Spark SS) | External (Spark SS) |
| Concurrency | OCC / NBCC / MVCC | Optimistic per catalog | Optimistic |
| Hidden partitioning | No | Yes | No |
| Partition evolution | Limited | Yes (metadata-only) | No |
| Multi-engine support | Good (growing) | Excellent (30+ engines) | Good (Spark-centric) |
