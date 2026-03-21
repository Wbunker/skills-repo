# Schema Design
## Chapters 4–5: Partitioning, Internal vs. External Tables, Table Properties, Schema Evolution

---

## Internal vs. External Tables

### Internal (Managed) Tables

Impala owns the data lifecycle. When you DROP the table, **the data is deleted from HDFS**.

```sql
CREATE TABLE orders (
    order_id BIGINT,
    amount   DECIMAL(10,2)
) STORED AS PARQUET;
-- Data lives at: /user/hive/warehouse/<db>.db/<table>/
```

**Use when:**
- Data is exclusively owned by this Impala/Hive table
- You want DROP TABLE to clean up data automatically
- No other process writes to the underlying HDFS location

### External Tables

Impala registers the schema but does **not** own the data. DROP TABLE removes only the metadata; HDFS files remain.

```sql
CREATE EXTERNAL TABLE events_raw (
    ts      TIMESTAMP,
    user_id BIGINT,
    action  STRING
)
STORED AS PARQUET
LOCATION '/data/events/raw/';
```

**Use when:**
- Data is written by an external process (Spark, Flume, Kafka Connect)
- Multiple tools (Hive + Impala + Spark) share the same files
- You want to point to data without moving it
- Staging tables that are loaded then processed

### Checking Table Type

```sql
DESCRIBE FORMATTED orders;
-- Look for: Table Type: MANAGED_TABLE or EXTERNAL_TABLE
```

---

## Partitioning

### Why Partition?

Partitioning organizes data into subdirectories. Queries with predicates on partition columns can skip entire directories — **partition pruning**.

```
/data/sales/
├── dt=2024-01-01/
│   └── part-00000.parquet
├── dt=2024-01-02/
│   └── part-00000.parquet
└── dt=2024-01-03/
    └── part-00000.parquet

WHERE dt = '2024-01-01'  → only reads dt=2024-01-01/ directory
WHERE dt >= '2024-01-01' → reads only matching partitions
```

### Partitioned Table DDL

```sql
-- Single partition column
CREATE TABLE sales (
    order_id BIGINT,
    amount   DECIMAL(10,2),
    customer STRING
)
PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- Multiple partition columns (hierarchical)
CREATE TABLE events (
    event_id BIGINT,
    user_id  BIGINT,
    payload  STRING
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET;

-- Common pattern: region + date
CREATE TABLE transactions (
    txn_id   BIGINT,
    amount   DECIMAL(12,2)
)
PARTITIONED BY (region STRING, dt STRING)
STORED AS PARQUET;
```

### Partition Column Best Practices

| Recommendation | Reason |
|----------------|--------|
| Low cardinality (date, region, country, status) | High-cardinality = thousands of partitions = metadata overhead |
| Partition files should be > 256 MB each | Small files hurt Parquet scan efficiency (too many open file handles) |
| Avoid partitioning by user_id, session_id, etc. | Millions of partitions = statestore/catalogd memory bloat |
| Use STRING for date partitions (`dt STRING`) | Simpler handling; avoids TIMESTAMP partition parsing issues |
| Max practical partition count: ~100,000 per table | Beyond this, metadata operations (SHOW PARTITIONS, REFRESH) become slow |

### Adding and Managing Partitions

```sql
-- Add single partition
ALTER TABLE sales ADD PARTITION (dt='2024-01-15');

-- Add with explicit location (for external tables or non-standard paths)
ALTER TABLE sales ADD PARTITION (dt='2024-01-15')
    LOCATION '/data/sales/dt=2024-01-15';

-- Add multiple partitions in one statement (Impala 2.x+)
ALTER TABLE sales ADD
    PARTITION (dt='2024-01-16')
    PARTITION (dt='2024-01-17')
    PARTITION (dt='2024-01-18');

-- Drop a partition (drops data if managed table)
ALTER TABLE sales DROP PARTITION (dt='2023-01-01');

-- Recover partitions from HDFS (if partitions exist on disk but not in metastore)
MSCK REPAIR TABLE sales;   -- Hive syntax; in Impala use RECOVER PARTITIONS
ALTER TABLE sales RECOVER PARTITIONS;

-- View partitions
SHOW PARTITIONS sales;

-- Partition-level statistics
COMPUTE INCREMENTAL STATS sales PARTITION (dt='2024-01-15');
```

### Dynamic Partition Inserts

```sql
-- Impala discovers partition values at INSERT time from SELECT output
INSERT INTO sales PARTITION (dt)
SELECT order_id, amount, CAST(order_date AS DATE) AS dt
FROM orders_staging;
```

`SET DYNAMIC_PARTITION_LIMIT = 1000;` — max new partitions per INSERT (default 1000).

---

## Table Properties (TBLPROPERTIES)

```sql
-- Set properties on create
CREATE TABLE orders (...)
STORED AS PARQUET
TBLPROPERTIES (
    'comment'             = 'Daily order fact table',
    'parquet.compression' = 'SNAPPY',
    'owner'               = 'data-engineering'
);

-- Set/change after creation
ALTER TABLE orders SET TBLPROPERTIES ('comment' = 'Updated description');

-- For Avro: inline schema or HDFS reference
ALTER TABLE events SET TBLPROPERTIES (
    'avro.schema.url' = 'hdfs:///schemas/event_v2.avsc'
);

-- Enable stats auto-compute (CDH 6+)
ALTER TABLE orders SET TBLPROPERTIES ('impala.enable.stats.extrapolation' = 'true');
```

---

## Schema Evolution

### Adding Columns

```sql
-- Add to end of column list (safest)
ALTER TABLE orders ADD COLUMNS (discount DECIMAL(5,2), promo_code STRING);

-- Parquet: new columns return NULL for existing files (compatible)
-- Text: new columns return NULL if row has fewer fields
-- Avro: new columns with defaults are forward-compatible
```

### Renaming Columns (Hive Metastore only)

```sql
ALTER TABLE orders CHANGE old_name new_name STRING;
-- WARNING: This changes only the metastore name, not the Parquet field name.
-- Parquet reads by ordinal position (old) or field name (new readers).
-- Can cause misalignment. Prefer adding new columns over renaming.
```

### Changing Column Types

```sql
ALTER TABLE orders CHANGE amount amount DOUBLE;
-- Safe: TINYINT → SMALLINT → INT → BIGINT → FLOAT → DOUBLE → STRING (widening)
-- Unsafe: narrowing conversions (BIGINT → INT), or STRING → numeric
-- Parquet: type change only affects metastore; actual file bytes unchanged
--          Impala will try to cast at read time
```

### Schema Evolution with Parquet

Parquet fields are matched by **name** (in Impala and modern readers). Adding/removing columns from a schema is safe if:
- New columns have default values or queries tolerate NULL
- Removed columns are no longer referenced in queries
- Column types only widen

### Schema Evolution with Avro

Avro has formal compatibility rules:
- **Backward-compatible**: add optional fields (with default); remove fields
- **Forward-compatible**: add fields (readers can ignore); remove optional fields
- **Full**: both backward and forward

For Avro tables in Impala, update the schema file on HDFS and run:
```sql
ALTER TABLE events SET TBLPROPERTIES ('avro.schema.url' = 'hdfs:///schemas/event_v3.avsc');
REFRESH events;
```

---

## Bucketing

Impala supports the Hive bucketing syntax for compatibility, but **does not use it for query optimization** the way Hive does. Bucketed tables created in Hive can be read by Impala normally.

```sql
-- Hive syntax (for compatibility); Impala ignores bucket hint for optimization
CREATE TABLE orders_bucketed (
    order_id BIGINT,
    customer STRING
)
CLUSTERED BY (order_id) INTO 32 BUCKETS
STORED AS PARQUET;
```

For Impala-native data distribution optimization, use **Apache Kudu** (which has true hash and range partitioning) or rely on partition pruning + file-level statistics.

---

## Table Design Patterns

### Date Partitioned Fact Table (Standard Pattern)

```sql
CREATE TABLE fact_orders (
    order_id     BIGINT,
    customer_id  BIGINT,
    product_id   BIGINT,
    quantity     INT,
    unit_price   DECIMAL(10,2),
    total_amount DECIMAL(12,2)
)
PARTITIONED BY (dt STRING)   -- 'YYYY-MM-DD'
STORED AS PARQUET
TBLPROPERTIES ('parquet.compression' = 'SNAPPY');
```

### Multi-Level Partitioned Table

```sql
CREATE TABLE logs (
    log_id   BIGINT,
    severity STRING,
    message  STRING
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET;
-- Path: /warehouse/logs/year=2024/month=1/day=15/
-- Good when queries often filter by year only, or year+month, or full date
```

### External Staging Table

```sql
-- Point to a landing zone; data arrives from ETL pipelines
CREATE EXTERNAL TABLE staging_events (
    raw_json STRING
)
STORED AS TEXTFILE
LOCATION '/landing/events/';
-- After new files arrive, run: REFRESH staging_events;
```

### CTAS (Create Table As Select) for Transformations

```sql
-- Build a new optimized table from staging
CREATE TABLE fact_events
PARTITIONED BY (dt STRING)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compression' = 'ZSTD')
AS
SELECT
    CAST(event_id     AS BIGINT) AS event_id,
    CAST(user_id      AS BIGINT) AS user_id,
    event_type,
    CAST(event_time   AS TIMESTAMP) AS event_time,
    CAST(event_date   AS STRING) AS dt
FROM staging_events_parsed;
```

### Kudu-Backed Table (Mutable Data)

```sql
-- Requires Kudu storage engine; supports INSERT/UPDATE/DELETE/UPSERT
CREATE TABLE mutable_users (
    user_id  BIGINT,
    name     STRING,
    email    STRING,
    updated  TIMESTAMP
)
PRIMARY KEY (user_id)
PARTITION BY HASH(user_id) PARTITIONS 16
STORED AS KUDU;
```
