# Snowflake SQL Commands, Data Types, and Functions

Reference for SQL command categories, data types, query syntax, operators, and functions.

## Table of Contents
- [SQL Command Categories](#sql-command-categories)
- [DDL Commands](#ddl-commands)
- [DML Commands](#dml-commands)
- [Query Syntax and Operators](#query-syntax-and-operators)
- [Data Types](#data-types)
- [Semi-Structured Data](#semi-structured-data)
- [Functions](#functions)
- [Query Performance Tips](#query-performance-tips)

## SQL Command Categories

| Category | Purpose | Examples |
|----------|---------|---------|
| **DDL** | Define objects | CREATE, ALTER, DROP, SHOW, DESCRIBE |
| **DML** | Modify data | INSERT, UPDATE, DELETE, MERGE, TRUNCATE |
| **DQL** | Query data | SELECT |
| **DCL** | Control access | GRANT, REVOKE |
| **TCL** | Transaction control | BEGIN, COMMIT, ROLLBACK |

## DDL Commands

```sql
-- CREATE
CREATE TABLE orders (id INT, amount FLOAT, created TIMESTAMP_NTZ);
CREATE VIEW active_orders AS SELECT * FROM orders WHERE status = 'active';
CREATE WAREHOUSE analytics_wh WITH WAREHOUSE_SIZE = 'MEDIUM';

-- ALTER
ALTER TABLE orders ADD COLUMN region STRING;
ALTER WAREHOUSE analytics_wh SET WAREHOUSE_SIZE = 'LARGE';
ALTER TABLE orders CLUSTER BY (region, created);

-- DROP
DROP TABLE IF EXISTS temp_data;
DROP WAREHOUSE old_wh;

-- SHOW (list objects)
SHOW TABLES IN SCHEMA my_db.public;
SHOW WAREHOUSES;
SHOW ROLES;
SHOW GRANTS TO ROLE analyst;
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE my_db;

-- DESCRIBE (object metadata)
DESCRIBE TABLE orders;
DESC TABLE orders;
DESCRIBE STAGE my_stage;
DESCRIBE VIEW active_orders;
```

## DML Commands

### INSERT
```sql
-- Single row
INSERT INTO customers (name, email) VALUES ('Alice', 'alice@example.com');

-- Multiple rows
INSERT INTO customers (name, email) VALUES
  ('Bob', 'bob@example.com'),
  ('Carol', 'carol@example.com');

-- INSERT INTO ... SELECT
INSERT INTO summary SELECT region, SUM(amount) FROM orders GROUP BY region;

-- INSERT ALL (multi-table insert)
INSERT ALL
  WHEN amount > 1000 THEN INTO high_value_orders
  WHEN amount <= 1000 THEN INTO standard_orders
SELECT * FROM new_orders;

-- INSERT OVERWRITE (replace all data)
INSERT OVERWRITE INTO summary SELECT region, SUM(amount) FROM orders GROUP BY region;
```

### UPDATE
```sql
UPDATE customers SET status = 'inactive' WHERE last_login < '2023-01-01';

-- Update with join
UPDATE orders o
SET o.region = c.region
FROM customers c
WHERE o.customer_id = c.customer_id;
```

### DELETE
```sql
DELETE FROM orders WHERE status = 'cancelled';

-- Delete with subquery
DELETE FROM orders WHERE customer_id IN (
  SELECT customer_id FROM customers WHERE status = 'deleted'
);
```

### MERGE (Upsert)
```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED AND s.action = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET
  t.name = s.name,
  t.amount = s.amount,
  t.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (id, name, amount, created_at)
  VALUES (s.id, s.name, s.amount, CURRENT_TIMESTAMP());
```

### Transactions
```sql
BEGIN TRANSACTION;
  INSERT INTO audit_log VALUES (CURRENT_TIMESTAMP(), 'start_transfer');
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
  INSERT INTO audit_log VALUES (CURRENT_TIMESTAMP(), 'end_transfer');
COMMIT;

-- Rollback on error
BEGIN;
  -- operations...
ROLLBACK;
```

## Query Syntax and Operators

### SELECT Syntax
```sql
SELECT [DISTINCT]
  column1,
  column2,
  aggregate_function(column3) AS alias
FROM table1
  [JOIN table2 ON condition]
  [WHERE filter_condition]
  [GROUP BY grouping_columns]
  [HAVING aggregate_condition]
  [QUALIFY window_condition]   -- Snowflake extension
  [ORDER BY sort_columns [ASC|DESC] [NULLS FIRST|LAST]]
  [LIMIT n [OFFSET m]];
```

### QUALIFY (filter window functions)
```sql
-- Get latest order per customer (Snowflake-specific clause)
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- Equivalent to subquery approach but cleaner
```

### Common Table Expressions (CTEs)
```sql
WITH monthly_sales AS (
  SELECT DATE_TRUNC('MONTH', sale_date) AS month,
         SUM(amount) AS total
  FROM sales
  GROUP BY 1
),
ranked AS (
  SELECT *, RANK() OVER (ORDER BY total DESC) AS rank
  FROM monthly_sales
)
SELECT * FROM ranked WHERE rank <= 5;
```

### Lateral Joins
```sql
-- LATERAL FLATTEN for semi-structured data
SELECT c.name, f.value::STRING AS tag
FROM customers c,
LATERAL FLATTEN(input => c.tags) f;
```

### Set Operators
```sql
SELECT * FROM table1 UNION ALL SELECT * FROM table2;     -- all rows
SELECT * FROM table1 UNION SELECT * FROM table2;         -- distinct
SELECT * FROM table1 INTERSECT SELECT * FROM table2;     -- common rows
SELECT * FROM table1 EXCEPT SELECT * FROM table2;        -- in table1 not table2
SELECT * FROM table1 MINUS SELECT * FROM table2;         -- same as EXCEPT
```

### Sampling
```sql
-- Row-based sampling
SELECT * FROM large_table SAMPLE (1000 ROWS);

-- Percentage-based sampling
SELECT * FROM large_table SAMPLE (10);  -- ~10% of rows

-- Bernoulli (row-level) vs Block (partition-level)
SELECT * FROM large_table SAMPLE BERNOULLI (10);  -- exact percentage
SELECT * FROM large_table SAMPLE BLOCK (10);       -- faster, approximate
```

## Data Types

### Numeric
| Type | Description |
|------|------------|
| `NUMBER(p,s)` / `DECIMAL` / `INT` | Fixed-point (up to 38 digits) |
| `FLOAT` / `DOUBLE` | 64-bit floating point |

### String
| Type | Description |
|------|------------|
| `VARCHAR(n)` / `STRING` / `TEXT` | Up to 16MB (default max) |
| `CHAR(n)` | Fixed-length |
| `BINARY` / `VARBINARY` | Binary data |

### Date/Time
| Type | Description |
|------|------------|
| `DATE` | Date only (no time) |
| `TIME` | Time only (no date) |
| `TIMESTAMP_NTZ` | No timezone (default TIMESTAMP) |
| `TIMESTAMP_LTZ` | Local timezone |
| `TIMESTAMP_TZ` | Explicit timezone stored |

### Boolean
```sql
-- TRUE, FALSE, NULL
SELECT * FROM users WHERE is_active = TRUE;
```

## Semi-Structured Data

Snowflake natively supports JSON, Avro, Parquet, and ORC.

### VARIANT Type
```sql
-- Store any semi-structured data
CREATE TABLE events (
  event_id INT,
  payload VARIANT
);

-- Insert JSON
INSERT INTO events SELECT 1, PARSE_JSON('{"user":"alice","action":"login","ts":"2024-01-15"}');

-- Query nested fields
SELECT
  payload:user::STRING AS user_name,
  payload:action::STRING AS action,
  payload:ts::TIMESTAMP AS event_time
FROM events;

-- Nested access
SELECT payload:address.city::STRING FROM events;
SELECT payload:tags[0]::STRING FROM events;  -- array index
```

### OBJECT and ARRAY Types
```sql
-- OBJECT: key-value pairs
SELECT OBJECT_CONSTRUCT('name', 'Alice', 'age', 30);

-- ARRAY
SELECT ARRAY_CONSTRUCT(1, 2, 3);
SELECT ARRAY_AGG(column1) FROM my_table;
```

### FLATTEN (explode arrays/objects)
```sql
-- Flatten array
SELECT e.event_id, f.value::STRING AS tag
FROM events e,
LATERAL FLATTEN(input => e.payload:tags) f;

-- Flatten nested object
SELECT e.event_id, f.key, f.value
FROM events e,
LATERAL FLATTEN(input => e.payload:metadata) f;

-- Recursive flatten
SELECT f.path, f.key, f.value
FROM events e,
LATERAL FLATTEN(input => e.payload, RECURSIVE => TRUE) f;
```

## Functions

### Aggregate Functions
```sql
COUNT(*), COUNT(DISTINCT col), SUM(col), AVG(col), MIN(col), MAX(col)
MEDIAN(col), MODE(col), STDDEV(col), VARIANCE(col)
LISTAGG(col, ','), ARRAY_AGG(col), OBJECT_AGG(key, value)
APPROX_COUNT_DISTINCT(col)  -- HyperLogLog approximation
```

### Window Functions
```sql
ROW_NUMBER() OVER (PARTITION BY col ORDER BY col2)
RANK() OVER (...)
DENSE_RANK() OVER (...)
LAG(col, 1) OVER (ORDER BY col2)
LEAD(col, 1) OVER (ORDER BY col2)
FIRST_VALUE(col) OVER (...)
LAST_VALUE(col) OVER (...)
NTH_VALUE(col, n) OVER (...)
SUM(col) OVER (PARTITION BY g ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```

### String Functions
```sql
CONCAT(a, b), a || b
UPPER(s), LOWER(s), INITCAP(s)
TRIM(s), LTRIM(s), RTRIM(s)
SUBSTRING(s, start, length), LEFT(s, n), RIGHT(s, n)
REPLACE(s, old, new), TRANSLATE(s, from, to)
SPLIT(s, delimiter), SPLIT_PART(s, delimiter, part)
REGEXP_LIKE(s, pattern), REGEXP_REPLACE(s, pattern, replacement)
REGEXP_SUBSTR(s, pattern), REGEXP_COUNT(s, pattern)
LENGTH(s), POSITION(substr IN s), CONTAINS(s, substr)
STARTSWITH(s, prefix), ENDSWITH(s, suffix)
```

### Date/Time Functions
```sql
CURRENT_DATE(), CURRENT_TIMESTAMP(), CURRENT_TIME()
DATEADD('DAY', 7, date_col), DATEDIFF('DAY', start, end)
DATE_TRUNC('MONTH', ts), DATE_PART('YEAR', ts)
TO_DATE(s, format), TO_TIMESTAMP(s, format)
YEAR(d), MONTH(d), DAY(d), DAYOFWEEK(d), DAYOFYEAR(d)
LAST_DAY(d), NEXT_DAY(d, 'MO')
TIMESTAMPADD('HOUR', 3, ts), TIMESTAMPDIFF('MINUTE', ts1, ts2)
```

### Conversion Functions
```sql
CAST(expr AS type), expr::type
TO_VARCHAR(expr, format), TO_NUMBER(s), TO_DECIMAL(s, p, s)
TO_DATE(s), TO_TIMESTAMP(s), TO_TIME(s)
TRY_CAST(expr AS type)  -- returns NULL on failure instead of error
TRY_TO_NUMBER(s), TRY_TO_DATE(s), TRY_TO_TIMESTAMP(s)
```

### Conditional Functions
```sql
CASE WHEN cond THEN result ELSE default END
IFF(condition, true_val, false_val)  -- Snowflake shorthand for simple CASE
COALESCE(a, b, c), NVL(a, b), NVL2(a, if_not_null, if_null)
NULLIF(a, b), ZEROIFNULL(a), IFNULL(a, b)
DECODE(expr, val1, result1, val2, result2, ..., default)
```

## Advanced Analytics Patterns

### Trend Analysis
```sql
-- Month-over-month growth
SELECT
  DATE_TRUNC('MONTH', order_date) AS month,
  SUM(amount) AS revenue,
  LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('MONTH', order_date)) AS prev_month,
  ROUND((revenue - prev_month) / prev_month * 100, 2) AS mom_growth_pct
FROM orders
GROUP BY 1
ORDER BY 1;

-- Year-over-year comparison by month
SELECT
  MONTH(order_date) AS month_num,
  SUM(CASE WHEN YEAR(order_date) = 2024 THEN amount END) AS rev_2024,
  SUM(CASE WHEN YEAR(order_date) = 2023 THEN amount END) AS rev_2023,
  ROUND((rev_2024 - rev_2023) / NULLIF(rev_2023, 0) * 100, 1) AS yoy_pct
FROM orders
WHERE YEAR(order_date) IN (2023, 2024)
GROUP BY 1
ORDER BY 1;

-- Cumulative distribution / running percentage
SELECT
  region,
  revenue,
  SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative,
  ROUND(cumulative / SUM(revenue) OVER () * 100, 1) AS cumulative_pct
FROM (SELECT region, SUM(amount) AS revenue FROM orders GROUP BY region);
```

### Temporal Analytics
```sql
-- Sessionization (gap-based sessions using CONDITIONAL_TRUE_EVENT)
SELECT
  user_id,
  event_time,
  CONDITIONAL_TRUE_EVENT(
    DATEDIFF('MINUTE', LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time), event_time) > 30
  ) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM events;

-- Time-weighted averages
SELECT
  sensor_id,
  SUM(value * duration_seconds) / SUM(duration_seconds) AS time_weighted_avg
FROM (
  SELECT
    sensor_id, value,
    DATEDIFF('SECOND', reading_time,
      LEAD(reading_time) OVER (PARTITION BY sensor_id ORDER BY reading_time)
    ) AS duration_seconds
  FROM sensor_readings
);

-- Gaps and islands (find consecutive date ranges)
SELECT
  user_id,
  MIN(active_date) AS range_start,
  MAX(active_date) AS range_end,
  COUNT(*) AS consecutive_days
FROM (
  SELECT *,
    DATEADD('DAY',
      -ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY active_date),
      active_date
    ) AS grp
  FROM user_activity
)
GROUP BY user_id, grp
ORDER BY user_id, range_start;
```

### Advanced Window Frames
```sql
-- Moving average with explicit frame
SELECT
  order_date,
  amount,
  AVG(amount) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7day,
  AVG(amount) OVER (ORDER BY order_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30day
FROM daily_revenue;

-- Running total with partitioned reset
SELECT
  fiscal_quarter,
  order_date,
  amount,
  SUM(amount) OVER (PARTITION BY fiscal_quarter ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS qtd_revenue
FROM orders;

-- Percent of total within partition
SELECT
  region,
  product,
  revenue,
  ROUND(revenue / SUM(revenue) OVER (PARTITION BY region) * 100, 1) AS pct_of_region
FROM product_revenue;

-- NTILE for bucketing
SELECT
  customer_id,
  total_spend,
  NTILE(4) OVER (ORDER BY total_spend DESC) AS spend_quartile
FROM customer_summary;
```

## Query Performance Tips

```sql
-- Use EXPLAIN to see query plan
EXPLAIN SELECT * FROM orders WHERE region = 'US';

-- Query profiler (in Snowsight UI) — shows execution graph and statistics

-- Avoid SELECT * in production
-- Use WHERE clauses that align with clustering keys
-- Use LIMIT during development
-- Use APPROX_COUNT_DISTINCT for large cardinality counts
-- Avoid excessive subqueries; prefer CTEs or QUALIFY
```
