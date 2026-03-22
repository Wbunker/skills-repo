# HiveQL DML — Data Manipulation Language

## Table of Contents
1. [LOAD DATA](#load-data)
2. [INSERT INTO / INSERT OVERWRITE](#insert-into--insert-overwrite)
3. [Dynamic Partitioning](#dynamic-partitioning)
4. [Multi-Table Insert](#multi-table-insert)
5. [UPDATE](#update)
6. [DELETE](#delete)
7. [MERGE](#merge)
8. [EXPORT / IMPORT](#export--import)

---

## LOAD DATA

Moves files into a Hive table's warehouse directory (or copies from local).
**No data transformation** — files are moved as-is. Table schema must match file format.

```sql
-- Load from HDFS path (moves file into warehouse)
LOAD DATA INPATH 'hdfs:///staging/orders/orders_20240115.csv'
INTO TABLE orders;

-- Overwrite existing data
LOAD DATA INPATH 'hdfs:///staging/orders/orders_20240115.csv'
OVERWRITE INTO TABLE orders;

-- Load from local filesystem (copies to HDFS)
LOAD DATA LOCAL INPATH '/tmp/orders.csv'
INTO TABLE orders;

-- Load into a specific partition
LOAD DATA INPATH 'hdfs:///staging/orders/20240115/'
INTO TABLE orders
PARTITION (event_date='2024-01-15', region='us-east');

-- Load directory (loads all files in directory)
LOAD DATA INPATH 'hdfs:///staging/orders/20240115'
INTO TABLE orders;
```

**Notes:**
- `INPATH` supports glob patterns: `'hdfs:///staging/orders/2024-01-*'`
- Source path must be on same HDFS cluster as warehouse (for move semantics)
- `LOCAL` always copies; non-LOCAL moves (fast on same cluster, no copy)
- LOAD bypasses Tez/MapReduce — it's just a file move

---

## INSERT INTO / INSERT OVERWRITE

### From SELECT
```sql
-- Append to table
INSERT INTO TABLE orders
SELECT order_id, user_id, amount, status, created
FROM raw_orders
WHERE status != 'cancelled';

-- TABLE keyword is optional
INSERT INTO orders
SELECT * FROM raw_orders;

-- Overwrite (replaces ALL data in unpartitioned table)
INSERT OVERWRITE TABLE orders
SELECT * FROM raw_orders;

-- Overwrite specific partition
INSERT OVERWRITE TABLE orders
PARTITION (event_date='2024-01-15')
SELECT order_id, user_id, amount, status, created
FROM raw_orders
WHERE DATE(created) = '2024-01-15';
```

### INSERT VALUES (ACID tables only)
```sql
-- Requires ACID/transactional table
INSERT INTO orders VALUES
  (1001, 42, 99.99, 'pending',  '2024-01-15 10:00:00'),
  (1002, 43, 149.50, 'shipped', '2024-01-15 10:05:00');

-- Single row
INSERT INTO orders (order_id, user_id, amount, status)
VALUES (1003, 44, 29.99, 'pending');
```

---

## Dynamic Partitioning

Write to multiple partitions in one INSERT without specifying values explicitly.

```sql
-- Required settings (set before INSERT)
SET hive.exec.dynamic.partition = true;          -- default true in Hive 2+
SET hive.exec.dynamic.partition.mode = nonstrict; -- allows all-dynamic partitions
-- strict mode (default) requires at least one static partition spec

SET hive.exec.max.dynamic.partitions = 1000;      -- default 1000
SET hive.exec.max.dynamic.partitions.pernode = 100; -- per mapper/reducer

-- Dynamic partition INSERT
-- Partition columns (event_date, region) must be LAST in SELECT list
INSERT OVERWRITE TABLE orders
PARTITION (event_date, region)           -- no values = dynamic
SELECT order_id, user_id, amount, status, created,
       DATE_FORMAT(created, 'yyyy-MM-dd') AS event_date,
       region
FROM raw_orders;

-- Mixed static + dynamic
INSERT OVERWRITE TABLE orders
PARTITION (event_date='2024-01-15', region)   -- date=static, region=dynamic
SELECT order_id, user_id, amount, status, created,
       region
FROM raw_orders
WHERE DATE(created) = '2024-01-15';
```

---

## Multi-Table Insert

One scan, multiple outputs — efficient when source table is large.

```sql
FROM raw_orders
INSERT OVERWRITE TABLE orders_completed
  SELECT * WHERE status = 'completed'
INSERT OVERWRITE TABLE orders_pending
  SELECT * WHERE status = 'pending'
INSERT INTO TABLE orders_archive
  SELECT * WHERE created < '2023-01-01';

-- With different transformations
FROM raw_events re
INSERT INTO TABLE event_summary
  SELECT event_type, COUNT(*), SUM(value)
  GROUP BY event_type
INSERT INTO TABLE event_log
  SELECT event_id, event_type, ts
  WHERE level = 'ERROR';
```

---

## UPDATE

Requires ACID/transactional table (ORC format, `transactional=true`).

```sql
-- Basic update
UPDATE orders SET status = 'shipped' WHERE order_id = 1001;

-- Update multiple columns
UPDATE orders
SET status = 'delivered',
    updated_at = CURRENT_TIMESTAMP
WHERE order_id = 1001;

-- Update with expression
UPDATE orders
SET amount = amount * 0.9  -- 10% discount
WHERE user_id IN (SELECT user_id FROM vip_users);

-- Update with join (using subquery)
UPDATE orders
SET status = 'flagged'
WHERE order_id IN (
  SELECT o.order_id FROM orders o
  JOIN fraud_list f ON o.user_id = f.user_id
);
```

**Limitations:**
- Only works on ACID (transactional) tables — ORC format required
- Cannot update partition columns
- Subqueries in WHERE supported; direct JOIN in UPDATE not supported
- `insert_only` tables do not support UPDATE

---

## DELETE

```sql
-- Delete by condition
DELETE FROM orders WHERE status = 'cancelled' AND created < '2023-01-01';

-- Delete with subquery
DELETE FROM orders
WHERE order_id IN (
  SELECT order_id FROM duplicate_orders
);
```

**Limitations:** Same as UPDATE — ACID tables only, ORC format required.

---

## MERGE

MERGE combines INSERT, UPDATE, and DELETE in one statement based on join condition.
Hive 2.2+; requires ACID table.

```sql
MERGE INTO orders AS target
USING order_updates AS source
ON (target.order_id = source.order_id)

WHEN MATCHED AND source.action = 'update' THEN
  UPDATE SET
    target.status     = source.new_status,
    target.updated_at = source.updated_at

WHEN MATCHED AND source.action = 'delete' THEN
  DELETE

WHEN NOT MATCHED THEN
  INSERT VALUES (
    source.order_id,
    source.user_id,
    source.amount,
    source.status,
    source.created
  );
```

### Common MERGE patterns

```sql
-- Upsert (insert new, update existing)
MERGE INTO dim_users AS t
USING user_updates AS s
ON t.user_id = s.user_id
WHEN MATCHED THEN
  UPDATE SET t.name = s.name, t.email = s.email
WHEN NOT MATCHED THEN
  INSERT VALUES (s.user_id, s.name, s.email, s.created_at);

-- SCD Type 2 (slowly changing dimension)
MERGE INTO dim_product AS t
USING product_changes AS s
ON t.product_id = s.product_id AND t.is_current = TRUE
WHEN MATCHED AND (t.price != s.price OR t.name != s.name) THEN
  UPDATE SET t.is_current = FALSE, t.end_date = CURRENT_DATE
WHEN NOT MATCHED THEN
  INSERT VALUES (s.product_id, s.name, s.price, TRUE, CURRENT_DATE, NULL);
-- Then INSERT the new current rows in a separate statement
```

---

## EXPORT / IMPORT

Exports table data AND metadata (schema) together. Useful for migrating between clusters.

```sql
-- Export to HDFS directory
EXPORT TABLE orders TO 'hdfs:///exports/orders_backup';

-- Export specific partition
EXPORT TABLE orders PARTITION (event_date='2024-01-15')
TO 'hdfs:///exports/orders_20240115';

-- Import (creates table if not exists)
IMPORT TABLE orders FROM 'hdfs:///exports/orders_backup';

-- Import to a different table name
IMPORT TABLE orders_restored FROM 'hdfs:///exports/orders_backup';

-- Import external table
IMPORT EXTERNAL TABLE orders_ext
FROM 'hdfs:///exports/orders_backup'
LOCATION 'hdfs:///warehouse/orders_ext';
```

**EXPORT format:** Creates a `_metadata` file (Thrift-serialized schema) + data files in original format.
**Use cases:** Cluster migration, DR, point-in-time backup. Prefer for Hive-to-Hive transfers over `distcp` alone.
