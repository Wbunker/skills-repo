# Impala SQL Reference
## Chapters 2–3: impala-shell, DDL, DML, SELECT, JOINs, Subqueries, CTEs

---

## Connecting with impala-shell

```bash
# Basic connection
impala-shell -i <impalad-host>

# With database
impala-shell -i host:21000 -d mydb

# Run a single query and exit
impala-shell -i host -q "SELECT COUNT(*) FROM orders"

# Run a SQL file
impala-shell -i host -f queries.sql

# With Kerberos
impala-shell -i host --kerberos

# With LDAP
impala-shell -i host --ldap --user=analyst --password=secret

# Output as delimited CSV
impala-shell -i host --delimited --output_delimiter=',' -q "SELECT ..."

# Quiet mode (suppress INFO messages)
impala-shell -i host -B -q "SELECT ..."
```

### Useful impala-shell Commands

| Command | Effect |
|---------|--------|
| `CONNECT <host>` | Connect to a different impalad |
| `USE <db>` | Switch database |
| `SHOW DATABASES` | List databases |
| `SHOW TABLES` | List tables in current db |
| `DESCRIBE <table>` | Show column names and types |
| `DESCRIBE FORMATTED <table>` | Extended metadata (file format, location, stats) |
| `EXPLAIN <query>` | Show distributed query plan |
| `SUMMARY` | After query: show per-node timing/rows |
| `PROFILE` | After query: full runtime profile (verbose) |
| `SET` | Show all query options |
| `SET MEM_LIMIT=4g` | Set query memory limit for session |
| `INVALIDATE METADATA` | Reload all metadata from Hive Metastore |
| `REFRESH <table>` | Reload file metadata for one table |

---

## DDL: Databases

```sql
-- Create a database
CREATE DATABASE IF NOT EXISTS sales;
CREATE DATABASE analytics LOCATION '/user/hive/warehouse/analytics.db';

-- Switch
USE sales;

-- Drop
DROP DATABASE IF EXISTS old_db CASCADE;  -- CASCADE drops contained tables
```

---

## DDL: Tables

### CREATE TABLE

```sql
-- Internal (managed) table — Impala owns the data; DROP TABLE deletes data
CREATE TABLE orders (
    order_id   BIGINT,
    customer   STRING,
    amount     DECIMAL(10,2),
    order_date TIMESTAMP
)
STORED AS PARQUET;

-- External table — Impala does NOT delete data on DROP TABLE
CREATE EXTERNAL TABLE orders_ext (
    order_id BIGINT,
    customer STRING,
    amount   DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
LOCATION '/data/orders/';

-- Partitioned table
CREATE TABLE sales_by_day (
    order_id BIGINT,
    amount   DECIMAL(10,2)
)
PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- CREATE TABLE LIKE (copy schema, no data)
CREATE TABLE orders_backup LIKE orders;

-- CREATE TABLE AS SELECT (CTAS)
CREATE TABLE top_customers
STORED AS PARQUET
AS SELECT customer, SUM(amount) AS total FROM orders GROUP BY customer;
```

### STORED AS Options

| Clause | Format | Best for |
|--------|--------|---------|
| `STORED AS PARQUET` | Apache Parquet | Analytics (default recommendation) |
| `STORED AS ORC` | Apache ORC | Hive ACID tables; read-heavy analytics |
| `STORED AS AVRO` | Apache Avro | Schema evolution; row-based pipelines |
| `STORED AS TEXTFILE` | Delimited text | Staging, interoperability |
| `STORED AS RCFILE` | Record Columnar File | Legacy Hive workloads |
| `STORED AS SEQUENCEFILE` | Hadoop SequenceFile | Legacy MapReduce output |

### ALTER TABLE

```sql
-- Add columns
ALTER TABLE orders ADD COLUMNS (region STRING, priority INT);

-- Drop column (Impala 3.x+)
ALTER TABLE orders DROP COLUMN priority;

-- Rename table
ALTER TABLE orders RENAME TO orders_v1;

-- Change HDFS location (external tables)
ALTER TABLE orders SET LOCATION '/new/path/orders';

-- Change file format
ALTER TABLE orders SET FILEFORMAT PARQUET;

-- Add table properties
ALTER TABLE orders SET TBLPROPERTIES ('comment'='Order fact table');

-- Add partitions manually
ALTER TABLE sales_by_day ADD PARTITION (dt='2024-01-01');
ALTER TABLE sales_by_day ADD IF NOT EXISTS PARTITION (dt='2024-01-01')
    LOCATION '/data/sales/dt=2024-01-01';

-- Drop partition
ALTER TABLE sales_by_day DROP PARTITION (dt='2023-01-01');
```

---

## DDL: Views

```sql
-- Create view
CREATE VIEW vw_recent_orders AS
SELECT order_id, customer, amount
FROM orders
WHERE order_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS);

-- Alter view
ALTER VIEW vw_recent_orders AS
SELECT order_id, customer, amount, region
FROM orders
WHERE order_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS);

-- Drop view
DROP VIEW IF EXISTS vw_recent_orders;
```

---

## DML: Loading and Inserting Data

### INSERT

```sql
-- INSERT INTO (append)
INSERT INTO orders VALUES
    (1001, 'ACME Corp', 250.00, '2024-01-15 10:30:00'),
    (1002, 'Globex', 175.50, '2024-01-15 11:00:00');

-- INSERT INTO from SELECT (append)
INSERT INTO orders SELECT * FROM orders_staging WHERE validated = true;

-- INSERT OVERWRITE (replace entire table or partition)
INSERT OVERWRITE orders SELECT * FROM orders_new;

-- INSERT OVERWRITE a specific partition
INSERT OVERWRITE sales_by_day PARTITION (dt='2024-01-15')
SELECT order_id, amount FROM orders WHERE CAST(order_date AS DATE) = '2024-01-15';

-- Dynamic partition insert (partition column in SELECT)
INSERT INTO sales_by_day PARTITION (dt)
SELECT order_id, amount, CAST(order_date AS DATE) AS dt FROM orders;
```

### LOAD DATA

```sql
-- Load from HDFS path into table (moves files)
LOAD DATA INPATH '/staging/orders_20240115.parquet' INTO TABLE orders;

-- Overwrite
LOAD DATA INPATH '/staging/orders_20240115.parquet' OVERWRITE INTO TABLE orders;

-- Load into partition
LOAD DATA INPATH '/staging/20240115/' INTO TABLE sales_by_day PARTITION (dt='2024-01-15');
```

**Note**: `LOAD DATA` moves HDFS files — the source path is deleted. For external tables pointing to shared paths, prefer `REFRESH` after files are placed by other processes.

### UPSERT (Kudu tables only)

```sql
-- UPSERT inserts if key not found; updates if key exists
UPSERT INTO kudu_orders (order_id, customer, amount)
VALUES (1001, 'ACME Corp', 300.00);

-- DELETE (Kudu only)
DELETE FROM kudu_orders WHERE order_id = 1001;

-- UPDATE (Kudu only)
UPDATE kudu_orders SET amount = 350.00 WHERE order_id = 1001;
```

---

## SELECT: Query Syntax

### Basic Structure

```sql
SELECT [DISTINCT] select_list
FROM   table_ref [JOIN ...]
WHERE  condition
GROUP  BY expression_list
HAVING condition
ORDER  BY expression_list [ASC|DESC] [NULLS FIRST|LAST]
LIMIT  n
OFFSET m;
```

### JOINs

```sql
-- INNER JOIN
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.id;

-- LEFT OUTER JOIN
SELECT c.name, o.order_id
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;

-- CROSS JOIN (cartesian — use with caution)
SELECT a.region, b.product FROM regions a CROSS JOIN products b;

-- Self-join
SELECT a.order_id, b.order_id AS related
FROM orders a JOIN orders b ON a.customer_id = b.customer_id AND a.order_id <> b.order_id;
```

**Join hint syntax:**
```sql
-- Force broadcast join (small table replicated to all nodes)
SELECT /*+ BROADCAST(small_table) */ *
FROM large_table JOIN small_table ON ...

-- Force shuffle join (both sides repartitioned by join key)
SELECT /*+ SHUFFLE */ *
FROM orders JOIN customers ON orders.customer_id = customers.id
```

### Subqueries

```sql
-- Scalar subquery in WHERE
SELECT * FROM orders
WHERE amount > (SELECT AVG(amount) FROM orders);

-- IN subquery
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE amount > 1000);

-- NOT IN subquery
SELECT * FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders WHERE YEAR(order_date) = 2024);

-- EXISTS
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Correlated subquery in SELECT (use sparingly — can be slow)
SELECT c.name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count
FROM customers c;
```

### CTEs (Common Table Expressions)

```sql
-- Single CTE
WITH monthly_totals AS (
    SELECT YEAR(order_date) AS yr, MONTH(order_date) AS mo, SUM(amount) AS total
    FROM orders
    GROUP BY 1, 2
)
SELECT * FROM monthly_totals WHERE yr = 2024 ORDER BY mo;

-- Multiple CTEs
WITH
top_customers AS (
    SELECT customer_id, SUM(amount) AS lifetime_value
    FROM orders
    GROUP BY customer_id
    HAVING SUM(amount) > 10000
),
enriched AS (
    SELECT t.customer_id, t.lifetime_value, c.name, c.region
    FROM top_customers t
    JOIN customers c ON t.customer_id = c.id
)
SELECT region, COUNT(*) AS count, AVG(lifetime_value) AS avg_ltv
FROM enriched
GROUP BY region
ORDER BY avg_ltv DESC;
```

### Set Operations

```sql
UNION ALL   -- combine all rows (includes duplicates; faster)
UNION       -- combine with deduplication
INTERSECT   -- rows in both result sets
EXCEPT      -- rows in first but not second

SELECT customer_id FROM orders_2023
UNION ALL
SELECT customer_id FROM orders_2024;
```

### LIMIT and OFFSET

```sql
-- Top 10 orders
SELECT * FROM orders ORDER BY amount DESC LIMIT 10;

-- Pagination
SELECT * FROM orders ORDER BY order_id LIMIT 20 OFFSET 40;  -- page 3
```

---

## Query Options (Session-Level)

```sql
-- Memory limit per query
SET MEM_LIMIT = '4g';
SET MEM_LIMIT = 0;          -- no limit (uses admission control pool)

-- Disable codegen for short queries (faster startup)
SET DISABLE_CODEGEN = true;

-- Parallelism within a node (multi-threaded execution)
SET MT_DOP = 4;

-- Request pool for admission control
SET REQUEST_POOL = 'bi-team';

-- Disable runtime filters (for debugging)
SET RUNTIME_FILTER_MODE = OFF;

-- Maximum scan range (for testing partition pruning)
SET NUM_NODES = 1;          -- force single-node execution

-- Reset all options
SET ALL;
```
