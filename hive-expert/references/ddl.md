# HiveQL DDL — Data Definition Language

## Table of Contents
1. [Databases](#databases)
2. [CREATE TABLE](#create-table)
3. [Managed vs External Tables](#managed-vs-external-tables)
4. [Partitioned Tables](#partitioned-tables)
5. [Bucketed Tables](#bucketed-tables)
6. [CTAS and CREATE LIKE](#ctas-and-create-like)
7. [ALTER TABLE](#alter-table)
8. [DROP / TRUNCATE](#drop--truncate)
9. [SHOW / DESCRIBE](#show--describe)
10. [TBLPROPERTIES Reference](#tblproperties-reference)

---

## Databases

```sql
-- Create
CREATE DATABASE mydb;
CREATE DATABASE IF NOT EXISTS mydb
  COMMENT 'Sales data warehouse'
  LOCATION 'hdfs:///user/hive/warehouse/mydb.db'
  WITH DBPROPERTIES ('owner'='team-data', 'created'='2024-01-01');

-- Navigate
USE mydb;
SHOW DATABASES;
SHOW DATABASES LIKE 'sales*';
DESCRIBE DATABASE mydb;
DESCRIBE DATABASE EXTENDED mydb;

-- Alter
ALTER DATABASE mydb SET DBPROPERTIES ('owner'='new-team');
ALTER DATABASE mydb SET LOCATION 'hdfs:///new/path';  -- Hive 2.2+

-- Drop
DROP DATABASE mydb;
DROP DATABASE IF EXISTS mydb CASCADE;  -- CASCADE drops all tables first
```

---

## CREATE TABLE

### Full syntax
```sql
CREATE [EXTERNAL] TABLE [IF NOT EXISTS] [db.]table_name
  (col_name data_type [COMMENT 'comment'], ...)
  [COMMENT 'table comment']
  [PARTITIONED BY (col_name data_type [COMMENT '...'], ...)]
  [CLUSTERED BY (col_name, ...) [SORTED BY (col_name [ASC|DESC], ...)] INTO n BUCKETS]
  [SKEWED BY (col_name, ...) ON ((val,...), ...) [STORED AS DIRECTORIES]]
  [
    [ROW FORMAT DELIMITED ...]
  | [ROW FORMAT SERDE 'classname' [WITH SERDEPROPERTIES (...)]]
  ]
  [STORED AS file_format]
  [LOCATION 'hdfs_path']
  [TBLPROPERTIES ('key'='value', ...)]
```

### Simple examples

```sql
-- Minimal managed ORC table (Hive 3+ defaults to ORC + ACID)
CREATE TABLE orders (
  order_id  BIGINT,
  user_id   BIGINT,
  amount    DECIMAL(10,2),
  status    STRING,
  created   TIMESTAMP
);

-- External CSV table
CREATE EXTERNAL TABLE raw_logs (
  ts      STRING,
  level   STRING,
  message STRING
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 'hdfs:///data/raw/logs';

-- ORC table with explicit settings
CREATE TABLE events (
  event_id   BIGINT,
  event_type STRING,
  payload    MAP<STRING, STRING>,
  tags       ARRAY<STRING>,
  metadata   STRUCT<source:STRING, version:INT>
)
STORED AS ORC
TBLPROPERTIES (
  'orc.compress' = 'SNAPPY',
  'orc.bloom.filter.columns' = 'event_type'
);
```

---

## Managed vs External Tables

### Hive 3+ behavior (important change from older versions)

| | Managed (default) | External |
|-|-------------------|----------|
| Keyword | none (default) | `EXTERNAL` |
| Default format | ORC + ACID | TextFile (unless specified) |
| `DROP TABLE` | Deletes metadata **and data** | Deletes metadata only; data remains |
| `TRUNCATE TABLE` | Supported | Not supported (Hive 3) |
| ACID / UPDATE / DELETE | Yes (default) | No |
| Typical use | Hive-owned data | Shared data, raw ingestion zone |

```sql
-- Managed table (Hive owns the data)
CREATE TABLE sales (id INT, amount DECIMAL(10,2))
STORED AS ORC;

-- External table (data managed externally)
CREATE EXTERNAL TABLE raw_sales (id INT, amount DECIMAL(10,2))
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs:///landing/sales';

-- Convert managed to external (Hive 4+)
ALTER TABLE sales SET TBLPROPERTIES ('EXTERNAL'='TRUE');

-- External table with auto-purge (delete data on drop, like managed)
CREATE EXTERNAL TABLE ...
TBLPROPERTIES ('external.table.purge'='true');
```

---

## Partitioned Tables

Partitioning physically separates data into subdirectories. Enables **partition pruning** — reads only relevant partitions.

```sql
-- Create partitioned table
CREATE TABLE events (
  event_id   BIGINT,
  event_type STRING,
  user_id    BIGINT
)
PARTITIONED BY (
  event_date STRING,    -- partition columns come LAST and are NOT in the main column list
  region     STRING
)
STORED AS ORC;

-- Partition directory layout:
-- warehouse/events/event_date=2024-01-15/region=us-east/
-- warehouse/events/event_date=2024-01-15/region=eu-west/

-- Add partition manually (for external tables or manual loads)
ALTER TABLE events ADD PARTITION (event_date='2024-01-15', region='us-east')
  LOCATION 'hdfs:///data/events/2024/01/15/us-east';

-- Add multiple partitions at once
ALTER TABLE events ADD
  PARTITION (event_date='2024-01-15', region='us-east')
  PARTITION (event_date='2024-01-15', region='eu-west');

-- Drop partition (drops metadata + data for managed tables)
ALTER TABLE events DROP PARTITION (event_date='2023-01-01');
ALTER TABLE events DROP PARTITION (event_date < '2023-01-01');  -- range drop

-- Repair partitions (re-sync metadata from filesystem — external tables)
MSCK REPAIR TABLE events;
-- or: ALTER TABLE events RECOVER PARTITIONS;

-- Show partitions
SHOW PARTITIONS events;
SHOW PARTITIONS events PARTITION (event_date='2024-01-15');
```

### Partition best practices
- Use `STRING` for date partitions: `event_date STRING` with value `'2024-01-15'`
  (avoids timezone issues with `DATE` type partitions)
- Cardinality guide: thousands of partitions OK, millions causes Metastore strain
- Always filter on partition column in WHERE clause to trigger pruning
- Verify pruning fired: `EXPLAIN` output should show `partition filter`

---

## Bucketed Tables

Bucketing hashes rows into a fixed number of files. Enables efficient `JOIN` and `TABLESAMPLE`.

```sql
CREATE TABLE user_events (
  user_id    BIGINT,
  event_type STRING,
  ts         TIMESTAMP
)
PARTITIONED BY (event_date STRING)
CLUSTERED BY (user_id) SORTED BY (ts DESC) INTO 256 BUCKETS
STORED AS ORC;

-- Rules:
-- 1. CLUSTERED BY column(s) determine bucket assignment (hash % n_buckets)
-- 2. SORTED BY is optional; enables sorted merge joins
-- 3. Number of buckets should be a power of 2; choose so each bucket ≈ 128-256 MB
-- 4. JOIN on bucket column with same number of buckets → Bucket Map Join (very fast)
```

---

## CTAS and CREATE LIKE

```sql
-- CTAS: Create Table As Select (copies data + creates table)
CREATE TABLE orders_2024
STORED AS ORC
AS
SELECT * FROM orders WHERE YEAR(created) = 2024;

-- CTAS with partitioning
CREATE TABLE orders_summary
PARTITIONED BY (order_month STRING)
STORED AS ORC
AS
SELECT order_id, user_id, amount,
       DATE_FORMAT(created, 'yyyy-MM') AS order_month
FROM orders;

-- CREATE LIKE: copies schema only, no data
CREATE TABLE orders_staging
LIKE orders;

-- CREATE LIKE from external table but make it managed
CREATE TABLE orders_managed
LIKE orders_external;  -- inherits columns but not EXTERNAL property
```

---

## ALTER TABLE

### Schema changes
```sql
-- Rename table
ALTER TABLE old_name RENAME TO new_name;

-- Add columns (appended at end, before partition columns)
ALTER TABLE orders ADD COLUMNS (
  coupon_code STRING,
  discount    DECIMAL(5,2)
);

-- Replace all non-partition columns (redefine schema)
ALTER TABLE orders REPLACE COLUMNS (
  order_id  BIGINT,
  user_id   BIGINT,
  amount    DECIMAL(10,2)
);

-- Change/rename a column
ALTER TABLE orders CHANGE COLUMN old_col new_col STRING
  COMMENT 'new comment'
  AFTER amount;          -- reposition (metadata only)

-- Change column type (must be compatible)
ALTER TABLE orders CHANGE COLUMN amount amount DECIMAL(12,2);
```

### Properties and storage
```sql
-- Set table properties
ALTER TABLE orders SET TBLPROPERTIES (
  'comment' = 'Updated table',
  'orc.bloom.filter.columns' = 'user_id,status'
);

-- Unset property
ALTER TABLE orders UNSET TBLPROPERTIES ('unwanted.key');

-- Change file format (metadata only — does NOT convert existing data)
ALTER TABLE orders SET FILEFORMAT ORC;

-- Change SerDe
ALTER TABLE orders SET SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',');

-- Change location
ALTER TABLE orders SET LOCATION 'hdfs:///new/path/orders';
ALTER TABLE orders PARTITION (event_date='2024-01-15')
  SET LOCATION 'hdfs:///archive/orders/2024-01-15';
```

### Partition operations
```sql
-- Rename partition value
ALTER TABLE orders PARTITION (event_date='2024-1-1')
  RENAME TO PARTITION (event_date='2024-01-01');

-- Update partition statistics
ALTER TABLE orders PARTITION (event_date='2024-01-15')
  SET TBLPROPERTIES ('numRows'='1000000');
```

---

## DROP / TRUNCATE

```sql
-- Drop table
DROP TABLE orders;
DROP TABLE IF EXISTS orders;
DROP TABLE orders PURGE;  -- skip Trash, immediate deletion

-- Drop external table (data stays, metadata removed)
DROP TABLE raw_orders;

-- Truncate (managed tables only — removes all data, keeps schema)
TRUNCATE TABLE orders;
TRUNCATE TABLE orders PARTITION (event_date='2024-01-15');

-- Drop database
DROP DATABASE mydb CASCADE;  -- CASCADE required if tables exist
```

---

## SHOW / DESCRIBE

```sql
-- Tables and databases
SHOW DATABASES;
SHOW DATABASES LIKE 'sales*';
SHOW TABLES;
SHOW TABLES IN mydb;
SHOW TABLES LIKE 'order*';
SHOW VIEWS;
SHOW MATERIALIZED VIEWS;
SHOW PARTITIONS orders;
SHOW PARTITIONS orders PARTITION (event_date='2024-01-15');
SHOW FUNCTIONS;
SHOW FUNCTIONS LIKE 'date*';

-- Describe
DESCRIBE orders;                     -- column names and types
DESCRIBE EXTENDED orders;            -- includes storage info as JSON
DESCRIBE FORMATTED orders;           -- human-readable extended info (most useful)
DESCRIBE orders event_date;          -- describe a specific column
DESCRIBE orders PARTITION (event_date='2024-01-15');  -- describe partition

-- Column statistics (after ANALYZE)
DESCRIBE FORMATTED orders.amount;
```

---

## TBLPROPERTIES Reference

```sql
-- ACID / transactional
'transactional'            = 'true'     -- enable ACID (auto for managed ORC in Hive 3+)
'transactional_properties' = 'insert_only'  -- cheaper; no UPDATE/DELETE support

-- ORC tuning
'orc.compress'                  = 'SNAPPY'   -- NONE, ZLIB, SNAPPY, ZSTD, LZO
'orc.stripe.size'               = '67108864' -- bytes (64MB default)
'orc.block.size'                = '268435456'-- bytes (256MB)
'orc.bloom.filter.columns'      = 'col1,col2'
'orc.bloom.filter.fpp'          = '0.05'     -- false positive probability

-- External table behavior
'external.table.purge'          = 'true'     -- delete data on DROP TABLE
'immutable'                     = 'true'     -- prevent INSERT INTO (allow only INSERT OVERWRITE)

-- Skipping header/footer rows
'skip.header.line.count'        = '1'
'skip.footer.line.count'        = '0'

-- Compaction (ACID tables)
'compactor.mapreduce.map.memory.mb' = '2048'

-- Statistics
'numFiles'    -- set by Hive automatically
'numRows'     -- set by ANALYZE TABLE or Hive
'totalSize'   -- set automatically
'rawDataSize' -- set automatically

-- Miscellaneous
'comment'     = 'Table description'
'auto.purge'  = 'true'   -- for managed tables: bypass Trash on overwrite
'EXTERNAL'    = 'TRUE'   -- convert managed → external (Hive 4+)
```
