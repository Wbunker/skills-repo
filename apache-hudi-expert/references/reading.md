# Reading from Hudi
## Chapter 4: Query Types, Data Structure, Query Lifecycle, Table Services Overview

---

## How Data Is Structured on Storage

Before understanding queries, understand what the reader actually sees:

### COW Table Storage

```
partition=US/
├── file001_20240101100000.parquet    ← v1 base file (old)
└── file001_20240115120000.parquet    ← v2 base file (current)
```

Reader sees only the latest base file per file group. Older versions exist for time travel.

### MOR Table Storage

```
partition=US/
├── file001_20240101100000.parquet    ← base file (last compaction)
├── file001_20240115120000.log.1      ← log file (records since compaction)
└── file001_20240116090000.log.2      ← another log file
```

Snapshot reader must merge base + all log files for the latest view. Read-optimized reader skips log files.

---

## Query Types

### 1. Snapshot Query

Returns the **complete, current state** of the table — the latest value for every record.

```python
# PySpark
df = spark.read.format("hudi").load("s3://bucket/orders/")

# Spark SQL
SELECT * FROM orders WHERE region = 'US';
```

**COW**: reads only the latest Parquet base file per file group.
**MOR**: reads latest base file + all log files written after it, merges on the fly.

**Cost**: COW is pure Parquet scan. MOR adds merge overhead proportional to log file volume (compaction reduces this).

### 2. Time Travel Query

Returns the **table state at a specific point in time** by reading historical file slices.

```python
# By timestamp
df = spark.read.format("hudi") \
    .option("as.of.instant", "20240115120000000") \
    .load("s3://bucket/orders/")

# By timestamp string
df = spark.read.format("hudi") \
    .option("as.of.instant", "2024-01-15 12:00:00") \
    .load("s3://bucket/orders/")
```

```sql
-- Spark SQL time travel
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 12:00:00';
SELECT * FROM orders VERSION AS OF '20240115120000000';
```

**Retention**: Time travel is limited by the cleaning policy. Old file slices are deleted by the cleaner. Set `hoodie.cleaner.commits.retained` high enough for your time travel window.

### 3. Incremental Query

Returns only **records that changed since a given commit**. Ideal for downstream pipelines that need to process only new/updated data.

```python
df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.read.begin.instanttime", "20240115000000000") \
    .option("hoodie.datasource.read.end.instanttime", "20240116000000000") \
    .load("s3://bucket/orders/")
```

Returns all records written between `beginTime` and `endTime` (inclusive/exclusive depending on config). Omit `endTime` to read up to the latest commit.

**Use case**: Streaming ETL pipeline checkpoints `endTime` and uses it as the next `beginTime`. Processes only the delta each run.

### 4. CDC (Change Data Capture) Query

Returns **change events** — each record includes the operation type and before/after images.

```python
df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.query.incremental.format", "cdc") \
    .option("hoodie.datasource.read.begin.instanttime", "20240115000000000") \
    .load("s3://bucket/orders/")
```

CDC output schema:

| Column | Description |
|--------|-------------|
| `op` | Operation: `I` (insert), `U` (update), `D` (delete) |
| `ts_ms` | Commit timestamp in milliseconds |
| `before` | Row state before the operation (null for inserts) |
| `after` | Row state after the operation (null for deletes) |

**Requirement**: Enable CDC logging on the table:

```python
"hoodie.table.cdc.enabled": "true",
"hoodie.table.cdc.supplemental.logging.mode": "data_before_after"  # or op_key_only
```

### 5. Read-Optimized Query (MOR Only)

Returns only the **base Parquet files** — skips all log files. Maximum read performance but may miss recent writes that haven't been compacted yet.

```python
df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "read_optimized") \
    .load("s3://bucket/orders_mor/")
```

**Tradeoff**: Fastest possible reads (pure Parquet), but data may lag behind the latest snapshot by however many commits have occurred since the last compaction.

**Typical use**: BI/reporting dashboards where slight staleness is acceptable and read latency matters most.

---

## Query Type Summary

| Query Type | Table Type | Returns | Performance | Freshness |
|-----------|-----------|---------|-------------|-----------|
| Snapshot | COW + MOR | Latest complete state | COW: fast; MOR: medium | Always current |
| Time Travel | COW + MOR | State at past instant | Similar to snapshot | Historical |
| Incremental | COW + MOR | Changed records in range | Fast (targeted scan) | Current |
| CDC | COW + MOR | Change events with before/after | Medium | Current |
| Read Optimized | MOR only | Base files only (no logs) | Fastest | Lags by compaction |

---

## Query Lifecycle in Distributed Query Engines

How a query engine (Trino, Spark, Athena) executes a Hudi snapshot query:

```
1. CATALOG LOOKUP
   Query engine asks HMS/Glue/REST catalog for table location
   Gets: s3://bucket/orders/

2. TIMELINE READ
   Read .hoodie/ directory to find latest commit instant
   Determine which file slices are valid for that instant

3. METADATA TABLE LOOKUP (if enabled)
   Read Hudi metadata table (stored in .hoodie/metadata/)
   Get file listing without listing S3 (much faster than S3 ListObjects)
   Get column statistics for data skipping

4. FILE PLANNING
   Identify relevant file slices (partitions + files)
   Apply partition pruning (WHERE region = 'US' → skip other partitions)
   Apply file-level statistics filtering (Bloom filter, min/max)

5. SPLIT GENERATION
   Each file slice becomes a scan split (unit of parallel work)

6. PARALLEL EXECUTION
   Each executor reads its assigned splits
   COW: read Parquet directly
   MOR: read base + apply log file records (merge)

7. RESULT ASSEMBLY
   Assemble results from all executors
```

### Metadata Table

Hudi maintains an internal metadata table at `<table_path>/.hoodie/metadata/` that stores:
- **Files listing**: avoids expensive S3 ListObjects calls
- **Column statistics**: min/max/null counts per column per file (for data skipping)
- **Bloom filter index**: per-file Bloom filters for record key lookup
- **Record-level index**: (if enabled) maps every record key to its file location

Enable the metadata table:

```python
"hoodie.metadata.enable": "true",
"hoodie.metadata.index.column.stats.enable": "true",   # column stats for data skipping
"hoodie.metadata.index.bloom.filter.enable": "true"    # Bloom filter in metadata
```

---

## Data Skipping

### Partition Pruning

Hudi uses Hive-style partition directories. Query engines automatically prune partitions using WHERE clause predicates:

```sql
-- This query only scans partition=US/ directories
SELECT * FROM orders WHERE region = 'US' AND order_date = '2024-01-15';
```

### File-Level Data Skipping

With column statistics enabled in the metadata table:
- Each file's min/max values for indexed columns are recorded
- A query with `WHERE amount > 1000` skips files where `max(amount) < 1000`
- Works across all engines that read the metadata table

### Bloom Filter Lookup

For point lookups by record key:
- Bloom filter per file group quickly eliminates files that definitely don't contain a key
- Avoids scanning all files; only reads files where the filter says "maybe"
- False positive rate is tunable: `hoodie.bloom.filter.fpp` (default 0.000000001)

---

## Table Services Overview (Read Perspective)

Table services exist to maintain query performance over time. Brief overview here; details in `maintenance.md`.

**Compaction** (MOR only): merges accumulated log files into Parquet base files. Directly improves snapshot query performance by eliminating in-flight merge overhead.

**Clustering**: reorganizes data files for better layout (co-locate related records). Improves data skipping and scan efficiency. Available for both COW and MOR.

**Cleaning**: removes old file slices and log files. Frees storage but limits time travel window.

---

## Reading from Non-Spark Engines

### Trino / Presto

```sql
-- Register Hudi table in Hive Metastore, then query:
SELECT * FROM hudi.orders WHERE region = 'US';

-- Incremental reads via Hive input format
-- (snapshot queries work natively; incremental requires Hudi input format connector)
```

### AWS Athena

```sql
-- Athena supports Hudi snapshot queries natively via Glue catalog
SELECT * FROM "hudi_db"."orders" WHERE region = 'US';
```

Athena supports COW snapshot queries out of the box. MOR requires configuring the read-optimized or snapshot query type in table properties.

### Apache Flink

```java
// Flink SQL
tableEnv.executeSql(
    "CREATE TABLE orders (" +
    "  order_id BIGINT," +
    "  amount DOUBLE," +
    "  ts TIMESTAMP(3)" +
    ") WITH (" +
    "  'connector' = 'hudi'," +
    "  'path' = 's3://bucket/orders/'," +
    "  'table.type' = 'MERGE_ON_READ'" +
    ")"
);
// Streaming reads: Flink can read Hudi as a streaming source (incremental)
tableEnv.executeSql("SELECT * FROM orders").print();
```
