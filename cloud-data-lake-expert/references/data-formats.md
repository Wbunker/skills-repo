# Deep Dive on Data Formats
## Chapter 6: Apache Iceberg, Delta Lake, Apache Hudi

---

## Why Open Table Formats Exist

Plain Parquet files on object storage are powerful but limited:
- **No ACID transactions** — concurrent writers corrupt data
- **No schema enforcement** — anyone can write incompatible schemas
- **No efficient updates or deletes** — must rewrite entire partitions
- **No time travel** — can't query historical state
- **Brittle partitioning** — changing partition scheme requires rewriting all data

Open table formats add a **metadata layer** on top of Parquet files that provides these capabilities while preserving the economics of object storage.

```
Open Table Format Architecture:

┌─────────────────────────────────────────────────────────┐
│                    QUERY ENGINES                         │
│         Spark · Trino/Presto · Flink · Athena           │
└─────────────────────┬───────────────────────────────────┘
                      │ read/write via format library
┌─────────────────────▼───────────────────────────────────┐
│              TABLE FORMAT METADATA LAYER                 │
│   Schema · Partitioning · Snapshots · Statistics         │
│   (stored in object storage alongside data)              │
│                                                          │
│   Iceberg: metadata/ dir with JSON + Avro files         │
│   Delta:   _delta_log/ dir with JSON transaction log     │
│   Hudi:    .hoodie/ dir with timeline files              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               PARQUET DATA FILES                         │
│          (on S3 / ADLS Gen2 / GCS)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Apache Iceberg

### Origin and Design Philosophy

Apache Iceberg was created at Netflix to solve the problems of managing large Hive-partitioned tables on S3. Iceberg's design principle: **the table format should be a spec, not a system** — any engine can implement the open spec and read/write Iceberg tables.

**Key design goals:**
- Correct, serializable ACID isolation with concurrent readers and writers
- Schema and partition evolution without rewriting data
- Hidden partitioning — queries don't need to know partition layout
- Full scan elimination using file-level statistics

### Iceberg Architecture

```
Table Metadata (JSON):
  ├── current-snapshot-id: 3820394857
  ├── schemas: [list of all schema versions]
  ├── partition-specs: [all partition spec versions]
  └── snapshots:
       ├── snapshot-3820394857
       │     └── manifest-list.avro
       │           ├── manifest-001.avro → [file-001.parquet, file-002.parquet]
       │           └── manifest-002.avro → [file-003.parquet, file-004.parquet]
       └── snapshot-3820394856 (previous snapshot)
```

**Three-level metadata hierarchy:**
1. **Table metadata JSON** — current schema, partition spec, current snapshot pointer
2. **Manifest list** (per snapshot) — list of manifest files; each has partition-level statistics
3. **Manifest files** — list of data files; each has file-level min/max statistics

This hierarchy enables extremely fast file pruning: the query planner skips manifests (and all their files) where partition-level statistics eliminate any possible match.

### Key Iceberg Features

#### Hidden Partitioning

Traditional Hive partitioning requires queries to include partition columns explicitly. Iceberg hides the partition scheme:

```sql
-- Hive-style (user must know partitioning):
SELECT * FROM orders WHERE year = 2024 AND month = 6 AND day = 30;

-- Iceberg hidden partitioning (query on business column):
SELECT * FROM orders WHERE order_date = '2024-06-30';
-- Iceberg translates to partition filter automatically
```

**Partition transforms:**
- `days(ts)` — partition by day from timestamp
- `hours(ts)` — partition by hour
- `months(ts)` — partition by month
- `years(ts)` — partition by year
- `bucket(N, col)` — hash bucket into N buckets
- `truncate(W, col)` — truncate string/int to width W

#### Schema Evolution

All schema changes are metadata-only operations (no data rewrite):

| Change | Safety | How |
|--------|--------|-----|
| Add column | Safe | New column with default; existing files return null |
| Drop column | Safe | Column hidden from queries; data still in files |
| Rename column | Safe | Column ID preserved; only display name changes |
| Reorder columns | Safe | Metadata-only |
| Widen type | Safe (some) | int→long, float→double supported |
| Narrow type | Unsafe | Not supported without data rewrite |

Iceberg uses **column IDs**, not column names, internally — this is what makes rename safe.

#### Partition Evolution

Change the partition scheme without rewriting existing data:

```sql
-- Original: partitioned by months
ALTER TABLE orders ADD PARTITION FIELD days(order_date);
-- Old data stays in month partitions; new data uses day partitions
-- Query planner handles both transparently
```

#### Time Travel

```sql
-- Query a specific snapshot (by ID or timestamp)
SELECT * FROM orders FOR VERSION AS OF 3820394857;
SELECT * FROM orders FOR TIMESTAMP AS OF '2024-06-01 00:00:00';

-- Show history
SELECT * FROM orders.history;

-- Show snapshots
SELECT * FROM orders.snapshots;
```

#### ACID Guarantees

Iceberg provides **serializable isolation**:
- Concurrent writers use **optimistic concurrency** — each writer reads the current snapshot, writes files, then atomically swaps the snapshot pointer
- If two writers conflict, one retries
- Readers always see a consistent snapshot — never partial writes

### Iceberg Table Maintenance

```sql
-- Compact small files
CALL catalog.system.rewrite_data_files('db.orders');

-- Expire old snapshots (reclaim storage)
CALL catalog.system.expire_snapshots('db.orders',
  TIMESTAMP '2024-01-01 00:00:00');

-- Remove orphan files (files not referenced by any snapshot)
CALL catalog.system.remove_orphan_files('db.orders');
```

### Iceberg Catalogs

Iceberg needs a catalog to track which metadata file is current for each table:

| Catalog | Description |
|---------|-------------|
| **Hive Metastore** | Traditional; widely supported |
| **AWS Glue Catalog** | AWS-native; integrates with Athena, EMR |
| **Apache Polaris** | Open-source Iceberg REST catalog (Apache incubating) |
| **Nessie** | Git-like branching for data lake tables |
| **REST catalog** | Vendor-neutral REST API spec; many implementations |

---

## Delta Lake

### Origin and Design Philosophy

Delta Lake was created by Databricks to bring reliability to data lakes. It uses a **transaction log** (the Delta Log) to provide ACID guarantees and is the native format for the Databricks platform.

**Key design goals:**
- ACID transactions with multi-statement atomicity
- Scalable metadata handling for tables with billions of files
- Time travel and audit history
- DML operations (UPDATE, DELETE, MERGE) on object storage

### Delta Lake Architecture

```
s3://my-table/
├── _delta_log/
│   ├── 00000000000000000000.json   (initial commit)
│   ├── 00000000000000000001.json   (add files)
│   ├── 00000000000000000002.json   (OPTIMIZE)
│   ├── 00000000000000000010.checkpoint.parquet  (checkpoint)
│   └── _last_checkpoint
├── part-00000-abc.snappy.parquet
├── part-00001-def.snappy.parquet
└── ...
```

**The Delta Log** is a sequence of JSON commit files. Each commit records:
- Files added
- Files removed
- Schema changes
- Statistics

Every 10 commits, Delta creates a **checkpoint** (Parquet file) with the full table state for fast recovery.

### Key Delta Lake Features

#### DML Operations

```sql
-- UPDATE
UPDATE orders SET status = 'cancelled' WHERE order_id = 12345;

-- DELETE
DELETE FROM orders WHERE order_date < '2020-01-01';

-- MERGE (upsert — powerful for CDC)
MERGE INTO orders AS target
USING updates AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

MERGE is the most powerful operation — it handles CDC patterns elegantly.

#### OPTIMIZE and Z-Ordering

```sql
-- Compact small files
OPTIMIZE orders;

-- Z-order by frequently-filtered columns within partitions
OPTIMIZE orders ZORDER BY (customer_id, product_id);
```

Z-ordering co-locates related rows within files, enabling aggressive row group skipping for queries filtering on those columns.

#### Time Travel

```sql
-- Query by version number
SELECT * FROM orders VERSION AS OF 10;

-- Query by timestamp
SELECT * FROM orders TIMESTAMP AS OF '2024-06-01';

-- Restore to a previous version
RESTORE TABLE orders TO VERSION AS OF 5;
```

#### Auto Optimize (Databricks)

Databricks-specific feature that automatically runs compaction and indexing on write:
```sql
ALTER TABLE orders SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

#### Schema Enforcement and Evolution

```python
# Schema enforcement — reject writes with incompatible schema (default)
df.write.format("delta").mode("append").save("/path/to/table")
# → fails if df schema doesn't match table schema

# Schema evolution — merge new columns automatically
df.write.format("delta").option("mergeSchema", "true").mode("append").save("/path")
```

### Delta Lake Table Maintenance

```sql
-- Remove old files no longer referenced
VACUUM orders RETAIN 168 HOURS;  -- keep 7 days of history

-- Describe history
DESCRIBE HISTORY orders;

-- Get table details
DESCRIBE DETAIL orders;
```

### Delta Sharing

Delta Sharing is an open protocol for sharing Delta tables with external consumers without copying data:
- Provider shares a Delta table via a sharing server
- Consumer reads the table with any Delta-compatible client
- Access controlled at table/partition/column level
- Works across clouds and organizations

---

## Apache Hudi

### Origin and Design Philosophy

Apache Hudi (Hadoop Upserts Deletes and Incrementals) was created by Uber to handle high-velocity upserts for data that arrives from operational databases — specifically designed for CDC and near-real-time use cases.

**Key design goals:**
- Efficient record-level upserts at high throughput
- Near-real-time ingestion with low latency
- Incremental processing (efficiently process only changed records)
- GDPR compliance (efficient deletes by primary key)

### Hudi Table Types

Hudi offers two table types with different read/write trade-offs:

#### Copy-on-Write (COW)

```
Write path: Read old file → merge with new records → write new file
Read path:  Read final merged file (no extra work)

Trade-off: Slow writes; fast reads
Best for:  Analytical workloads where reads dominate
```

#### Merge-on-Read (MOR)

```
Write path: Append delta (changes) to log file (fast)
Read path:  Read base Parquet + merge with log files on the fly

Trade-off: Fast writes; reads do work at query time
Best for:  Near-real-time ingestion; CDC; streaming
```

### Hudi Architecture

```
.hoodie/
├── hoodie.properties         (table configuration)
├── timeline/
│   ├── 20240630143022.commit      (commit metadata)
│   ├── 20240630143022.deltacommit (MOR delta commit)
│   └── 20240630143022.compaction  (compaction plan)
data/
├── base-files/               (COW or MOR base Parquet files)
└── log-files/                (MOR delta log files, Avro)
```

**The Timeline**: Hudi's core abstraction — ordered sequence of actions (commits, compactions, cleans) that defines the table's history.

### Key Hudi Features

#### Upsert Operations

```python
# High-throughput upsert — Hudi's primary use case
(df.write
  .format("hudi")
  .option("hoodie.table.name", "orders")
  .option("hoodie.datasource.write.operation", "upsert")
  .option("hoodie.datasource.write.recordkey.field", "order_id")
  .option("hoodie.datasource.write.precombine.field", "updated_at")
  .option("hoodie.datasource.write.partitionpath.field", "order_date")
  .mode("append")
  .save("s3://lake/orders"))
```

The `precombine.field` determines which record "wins" when there are duplicates with the same primary key — typically the latest timestamp.

#### Incremental Queries

Hudi's most distinctive feature: efficiently query only records that changed since a given point:

```python
# Read only records changed after a specific commit
incremental_df = (spark.read
  .format("hudi")
  .option("hoodie.datasource.query.type", "incremental")
  .option("hoodie.datasource.read.begin.instanttime", "20240629000000")
  .load("s3://lake/orders"))
# Returns only rows committed after 2024-06-29 00:00:00
```

This makes CDC pipelines efficient: downstream consumers don't need to scan the full table.

#### Compaction (MOR tables)

MOR tables accumulate log files over time; compaction merges them into base files:

```python
# Async compaction (recommended for production)
.option("hoodie.compact.inline", "false")
.option("hoodie.compact.async.inline", "true")
.option("hoodie.compact.inline.max.delta.commits", "5")
```

#### Cleaning (Managing Storage)

```python
# Automatically clean old file versions
.option("hoodie.cleaner.policy", "KEEP_LATEST_COMMITS")
.option("hoodie.cleaner.commits.retained", "10")
```

---

## Format Comparison Matrix

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---------|---------------|------------|-------------|
| **ACID transactions** | Yes | Yes | Yes |
| **Schema evolution** | Excellent (column IDs) | Good | Good |
| **Partition evolution** | Yes (hidden partitioning) | Limited | Limited |
| **Time travel** | Yes | Yes | Yes |
| **DML (UPDATE/DELETE/MERGE)** | Yes | Yes | Yes |
| **Upsert performance** | Good | Good | Excellent (built for this) |
| **Incremental queries** | Limited | Limited | Excellent (native) |
| **Streaming support** | Good | Good | Excellent (MOR) |
| **Multi-engine support** | Excellent | Good (outside Databricks) | Good |
| **AWS integration** | Excellent (Glue, Athena) | Good | Good |
| **Databricks integration** | Good | Excellent (native) | Good |
| **Open governance** | Apache (fully open) | Linux Foundation | Apache (fully open) |
| **Catalog options** | Many (REST, Glue, Hive) | Unity, Hive | Hive |
| **Z-ordering / clustering** | Sort orders | ZORDER | Clustering |
| **Table maintenance** | OPTIMIZE, expire_snapshots | OPTIMIZE, VACUUM | Compaction, clean |

---

## Choosing a Format

```
Decision: Which open table format?

Are you on Databricks?
  Yes → Delta Lake is the natural choice (native integration, Auto Optimize, Unity Catalog)
  No  → continue...

Primary workload: CDC / near-real-time upserts from operational DB?
  Yes → Apache Hudi (built for record-level upserts, MOR for latency, incremental queries)
  No  → continue...

Multi-cloud or multi-engine requirement?
  Yes → Apache Iceberg (broadest engine support: Spark, Trino, Flink, Athena, BigQuery, Snowflake)
  No  → continue...

AWS-centric?
  Yes → Apache Iceberg (Glue, Athena, EMR native support; AWS endorses Iceberg)
  No  → Apache Iceberg or Delta Lake depending on team familiarity

Streaming + lakehouse unified?
  Kafka → Hudi or Iceberg + Flink (both have strong Flink connectors)
```

### Interoperability (2024–2026 Trend)

The formats are converging on interoperability:
- **Apache XTable (formerly OneTable)**: Translates between Iceberg, Delta, and Hudi metadata automatically — a table written as Iceberg can be read as Delta without copying data
- **Delta UniForm**: Generates Iceberg metadata alongside Delta log — allows Iceberg-native engines to read Delta tables
- **Iceberg REST catalog**: Emerging standard that all formats can register with

The practical implication: format choice matters less than it did in 2022, as interoperability tooling reduces lock-in.
