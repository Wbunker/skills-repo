# Hive Schema Design

## Table of Contents
1. [Partitioning Strategy](#partitioning-strategy)
2. [Bucketing Strategy](#bucketing-strategy)
3. [Table Statistics](#table-statistics)
4. [Data Modeling Patterns](#data-modeling-patterns)
5. [When to Use Complex Types](#when-to-use-complex-types)

---

## Partitioning Strategy

Partitioning physically separates data into subdirectories. Properly used, it enables **partition pruning** — reading only matching partitions instead of the full table.

### Choosing partition columns

```sql
-- GOOD: partition by date — most queries filter by date
CREATE TABLE events (
  event_id   BIGINT,
  event_type STRING,
  user_id    BIGINT
)
PARTITIONED BY (event_date STRING)   -- STRING preferred over DATE (timezone safety)
STORED AS ORC;

-- BAD: partition by high-cardinality column (user_id has millions of values)
-- → millions of partitions → Metastore overload, small files problem
CREATE TABLE events (event_id BIGINT)
PARTITIONED BY (user_id BIGINT);    -- ← don't do this

-- BAD: no pruning benefit — no query filters on this column
CREATE TABLE events (
  event_id  BIGINT,
  event_type STRING  -- rarely used in WHERE
)
PARTITIONED BY (event_type STRING);  -- ← rarely beneficial
```

### Partition cardinality guide

```
Target: thousands of partitions per table
OK:     daily partitions for 3-5 years = ~1,000-1,800 partitions
OK:     (date, region) with 10 regions = ~18,000 partitions
Strain: millions of partitions (hourly + fine-grained secondary key)
Limit:  No hard limit, but Metastore queries slow >100,000 partitions
Fix:    Coarser time granularity; reduce secondary partition columns

Rule of thumb:
  # partitions × avg partition size ≈ total table size
  Each partition should be ≥ 1 HDFS block (128-256 MB)
  Partitions smaller than 1 block → small file problem
```

### Multi-level partitioning

```sql
-- Two-level: date + region (good if queries filter both)
CREATE TABLE orders (
  order_id BIGINT,
  user_id  BIGINT,
  amount   DECIMAL(10,2)
)
PARTITIONED BY (
  order_date STRING,    -- higher cardinality first
  region     STRING
)
STORED AS ORC;

-- Query that benefits (prunes both levels):
SELECT SUM(amount) FROM orders
WHERE order_date = '2024-01-15' AND region = 'us-east';

-- Query that only prunes date (still good):
SELECT SUM(amount) FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';
-- → scans all regions for those dates, but skips all other dates
```

### Partition best practices

```sql
-- 1. Always use STRING for date partitions — avoids timezone issues
PARTITIONED BY (event_date STRING)  -- value: '2024-01-15'
-- not: PARTITIONED BY (event_date DATE)

-- 2. Always filter on partition column in WHERE to trigger pruning
SELECT * FROM events WHERE event_date = '2024-01-15';  -- pruned
SELECT * FROM events WHERE YEAR(event_date) = 2024;    -- NOT pruned (function on partition col)

-- 3. Verify pruning with EXPLAIN
EXPLAIN SELECT * FROM events WHERE event_date = '2024-01-15';
-- Look for: "partition filter" in the plan output

-- 4. Use dynamic partitioning for ETL — partition columns LAST in SELECT
SET hive.exec.dynamic.partition.mode = nonstrict;
INSERT OVERWRITE TABLE events PARTITION (event_date)
SELECT event_id, event_type, user_id,
       DATE_FORMAT(ts, 'yyyy-MM-dd') AS event_date  -- partition col last
FROM raw_events;

-- 5. Repair after manual HDFS data load
MSCK REPAIR TABLE events;   -- discovers new partitions from filesystem
```

---

## Bucketing Strategy

Bucketing hashes rows into a fixed number of files per partition (or table). Enables efficient JOIN and TABLESAMPLE without scanning all data.

### Choosing bucket count and column

```sql
-- Bucket by the JOIN column for best performance
CREATE TABLE orders (
  order_id BIGINT,
  user_id  BIGINT,
  amount   DECIMAL(10,2)
)
PARTITIONED BY (order_date STRING)
CLUSTERED BY (user_id) INTO 256 BUCKETS
STORED AS ORC;

CREATE TABLE users (
  user_id BIGINT,
  name    STRING
)
CLUSTERED BY (user_id) INTO 256 BUCKETS  -- same column, same count
STORED AS ORC;

-- Now JOIN on user_id uses Bucket Map Join (very fast):
SELECT /*+ MAPJOIN(u) */ o.order_id, u.name
FROM orders o JOIN users u ON o.user_id = u.user_id;
```

### Bucket count guidelines

```
• Must be identical on both tables for Bucket Map Join
• Power of 2 recommended: 64, 128, 256, 512
• Target bucket size: 128-256 MB when full
  → total_table_size_GB × 1024 / target_bucket_MB ≈ num_buckets
  → 256 GB table / 256 MB = 1024 buckets
• Sorted merge bucket join: also requires SORTED BY on join column
  → fastest join type; needs both tables bucketed + sorted identically
```

### Sorted merge bucket join

```sql
CREATE TABLE user_events (
  user_id    BIGINT,
  event_type STRING,
  ts         TIMESTAMP
)
PARTITIONED BY (event_date STRING)
CLUSTERED BY (user_id) SORTED BY (user_id ASC) INTO 256 BUCKETS
STORED AS ORC;

-- Enable sorted merge bucket join
SET hive.optimize.bucketmapjoin.sortedmerge = true;
SET hive.input.format = org.apache.hadoop.hive.ql.io.BucketizedHiveInputFormat;
```

---

## Table Statistics

Statistics let the CBO (Cost-Based Optimizer) make better query plans. Essential for join ordering, partition pruning decisions, and aggregation strategies.

### Collecting statistics

```sql
-- Collect table-level statistics (row count, file count, total size)
ANALYZE TABLE orders COMPUTE STATISTICS;

-- Collect column-level statistics (min, max, NDV, nulls)
ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS;

-- Specific columns only
ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS user_id, amount, status;

-- For partitioned tables — analyze specific partition
ANALYZE TABLE orders PARTITION (order_date='2024-01-15') COMPUTE STATISTICS;
ANALYZE TABLE orders PARTITION (order_date='2024-01-15') COMPUTE STATISTICS FOR COLUMNS;

-- All partitions (Hive 3.2+ — uses noscan flag for fast file stats)
ANALYZE TABLE orders PARTITION (order_date) COMPUTE STATISTICS NOSCAN;
-- NOSCAN: uses filesystem metadata only (fast); no row count
```

### Viewing statistics

```sql
-- Table stats
DESCRIBE FORMATTED orders;
-- Look for: numRows, numFiles, totalSize in Table Parameters

-- Column stats
DESCRIBE FORMATTED orders.amount;
-- Shows: min, max, num_nulls, num_distincts, avg_col_len (strings), max_col_len

-- Hive automatically updates stats on INSERT OVERWRITE and CTAS (Hive 3+)
-- For INSERT INTO: stats may become stale — re-run ANALYZE
```

### Auto-statistics configuration

```sql
-- Hive 3+: auto-gather stats on INSERT/OVERWRITE
SET hive.stats.autogather = true;           -- default true
SET hive.stats.column.autogather = false;   -- column stats off by default (expensive)

-- Enable column stats auto-gather for new tables (adds overhead to writes)
SET hive.stats.column.autogather = true;

-- CBO uses stats when available:
SET hive.cbo.enable = true;   -- default true in Hive 3+
```

---

## Data Modeling Patterns

### Star schema in Hive

```sql
-- Fact table: large, partitioned, bucketed on dimension FK
CREATE TABLE fact_orders (
  order_id   BIGINT,
  user_id    BIGINT,    -- bucket by this for user-dimension joins
  product_id BIGINT,
  amount     DECIMAL(10,2),
  quantity   INT
)
PARTITIONED BY (order_date STRING)
CLUSTERED BY (user_id) INTO 256 BUCKETS
STORED AS ORC;

-- Dimension tables: small-ish, no partitioning usually
CREATE TABLE dim_users (
  user_id BIGINT,
  name    STRING,
  tier    STRING,
  country STRING
)
CLUSTERED BY (user_id) INTO 256 BUCKETS  -- match fact table bucket count
STORED AS ORC;

-- Dimension join uses Bucket Map Join (fast)
-- Small dimension can also use /*+ MAPJOIN(du) */ for broadcast
```

### Denormalized wide tables

```sql
-- Flat, pre-joined table for faster analytical queries
-- Trade: storage vs join cost at query time
CREATE TABLE orders_wide (
  order_id     BIGINT,
  order_date   STRING,   -- partition key
  amount       DECIMAL(10,2),
  -- user fields (denormalized)
  user_id      BIGINT,
  user_name    STRING,
  user_country STRING,
  user_tier    STRING,
  -- product fields (denormalized)
  product_id   BIGINT,
  product_name STRING,
  category     STRING
)
PARTITIONED BY (order_date STRING)
STORED AS ORC;
-- Populate via nightly JOIN job, query with no JOINs needed
```

### Slowly Changing Dimensions (SCD)

```sql
-- SCD Type 2: keep full history with effective dates
CREATE TABLE dim_product (
  surrogate_key BIGINT,   -- synthetic PK (sequence or hash)
  product_id    BIGINT,   -- natural key
  name          STRING,
  price         DECIMAL(10,2),
  is_current    BOOLEAN,
  effective_date DATE,
  end_date       DATE     -- NULL for current record
)
STORED AS ORC
TBLPROPERTIES ('transactional' = 'true');

-- Update via MERGE (ACID required):
MERGE INTO dim_product AS t
USING product_updates AS s
ON t.product_id = s.product_id AND t.is_current = TRUE
WHEN MATCHED AND (t.price != s.price OR t.name != s.name) THEN
  UPDATE SET t.is_current = FALSE, t.end_date = CURRENT_DATE
WHEN NOT MATCHED THEN
  INSERT VALUES (s.surrogate_key, s.product_id, s.name, s.price, TRUE, CURRENT_DATE, NULL);
```

---

## When to Use Complex Types

### ARRAY — multiple values of same type

```sql
-- Use when: a row naturally has an ordered list of homogeneous items
CREATE TABLE products (
  product_id BIGINT,
  tags       ARRAY<STRING>,          -- ['electronics', 'sale', 'featured']
  prices_30d ARRAY<DECIMAL(10,2)>    -- historical price points
)
STORED AS ORC;

-- Access:
SELECT product_id, tags[0] AS primary_tag, size(tags) AS tag_count FROM products;

-- Unnest for filtering/aggregation:
SELECT product_id, tag
FROM products
LATERAL VIEW EXPLODE(tags) t AS tag
WHERE tag = 'sale';
```

### MAP — key-value pairs with dynamic keys

```sql
-- Use when: keys vary per row (can't define as fixed columns)
CREATE TABLE events (
  event_id   BIGINT,
  properties MAP<STRING, STRING>  -- {'user_agent': 'Chrome', 'ip': '1.2.3.4'}
)
STORED AS ORC;

-- Access known key:
SELECT event_id, properties['user_agent'] FROM events;

-- Iterate keys:
SELECT event_id, key, value
FROM events
LATERAL VIEW EXPLODE(properties) p AS key, value;
```

### STRUCT — named fields, known at table creation

```sql
-- Use when: sub-fields are fixed and named (like a nested record)
CREATE TABLE orders (
  order_id BIGINT,
  address  STRUCT<
    street:  STRING,
    city:    STRING,
    state:   STRING,
    zip:     STRING
  >
)
STORED AS ORC;

-- Access field:
SELECT order_id, address.city, address.state FROM orders;
```

### When NOT to use complex types

```
• When you need to filter/join on nested values frequently
  → Flatten into columns; complex type access is slower
• When the schema needs to evolve often
  → MAP<STRING,STRING> is flexible but loses type safety
• When cardinality of array is very high (thousands of elements per row)
  → Consider a separate child table instead
• When using TextFile/CSV format
  → Complex types serialize awkwardly in delimited formats; use ORC/Parquet
```
