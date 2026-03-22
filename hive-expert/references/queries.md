# HiveQL Queries — SELECT Reference

## Table of Contents
1. [SELECT Basics](#select-basics)
2. [WHERE and Filtering](#where-and-filtering)
3. [JOINs](#joins)
4. [GROUP BY, HAVING](#group-by-having)
5. [Sorting: ORDER BY, SORT BY, DISTRIBUTE BY, CLUSTER BY](#sorting)
6. [UNION](#union)
7. [Subqueries](#subqueries)
8. [CTEs (WITH clause)](#ctes-with-clause)
9. [LATERAL VIEW and EXPLODE](#lateral-view-and-explode)
10. [Window Functions](#window-functions)
11. [TABLESAMPLE](#tablesample)

---

## SELECT Basics

```sql
SELECT col1, col2, expr AS alias
FROM table_name
WHERE condition
GROUP BY col1
HAVING agg_condition
ORDER BY col1 DESC
LIMIT 100;

-- All columns
SELECT * FROM orders;

-- With table alias
SELECT o.order_id, o.amount FROM orders o;

-- Arithmetic and expressions
SELECT order_id, amount * 1.1 AS amount_with_tax,
       CONCAT(first_name, ' ', last_name) AS full_name
FROM orders;

-- DISTINCT
SELECT DISTINCT status FROM orders;
SELECT COUNT(DISTINCT user_id) FROM orders;

-- LIMIT / OFFSET (Hive 2.0+)
SELECT * FROM orders LIMIT 10;
SELECT * FROM orders LIMIT 10 OFFSET 20;  -- rows 21-30
```

---

## WHERE and Filtering

```sql
-- Comparison operators
WHERE amount > 100
WHERE status = 'shipped'           -- single quotes only
WHERE status != 'cancelled'        -- also: <>
WHERE amount BETWEEN 10 AND 100    -- inclusive
WHERE status IN ('pending', 'shipped', 'delivered')
WHERE status NOT IN ('cancelled', 'refunded')
WHERE name LIKE 'A%'               -- % = any chars, _ = one char
WHERE name RLIKE '^A.*son$'        -- regex (POSIX)
WHERE name REGEXP '^A.*son$'       -- alias for RLIKE

-- NULL checks
WHERE col IS NULL
WHERE col IS NOT NULL

-- NULL-safe equality
WHERE col <=> NULL     -- TRUE when both are NULL
WHERE col1 <=> col2    -- TRUE when both equal or both NULL

-- Boolean
WHERE is_active = TRUE
WHERE is_active                -- same as = TRUE

-- Combining
WHERE amount > 100 AND status = 'shipped'
WHERE status = 'pending' OR status = 'processing'
WHERE NOT (status = 'cancelled')
WHERE (region = 'us-east' OR region = 'us-west') AND amount > 500
```

---

## JOINs

### JOIN types

```sql
-- INNER JOIN (default)
SELECT o.order_id, u.name
FROM orders o
JOIN users u ON o.user_id = u.user_id;

-- Same with INNER keyword
SELECT o.order_id, u.name
FROM orders o
INNER JOIN users u ON o.user_id = u.user_id;

-- LEFT OUTER JOIN
SELECT o.order_id, u.name
FROM orders o
LEFT JOIN users u ON o.user_id = u.user_id;
-- rows from orders with no matching user get u.* = NULL

-- RIGHT OUTER JOIN
SELECT o.order_id, u.name
FROM orders o
RIGHT JOIN users u ON o.user_id = u.user_id;

-- FULL OUTER JOIN
SELECT o.order_id, u.name
FROM orders o
FULL OUTER JOIN users u ON o.user_id = u.user_id;

-- CROSS JOIN (cartesian product — use with extreme care)
SELECT a.val, b.val FROM small_a a CROSS JOIN small_b b;

-- LEFT SEMI JOIN (replaces WHERE col IN (subquery) — more efficient)
-- Returns rows from left table where match exists in right (no right cols in SELECT)
SELECT o.order_id, o.amount
FROM orders o
LEFT SEMI JOIN vip_users v ON o.user_id = v.user_id;
-- Equivalent to: WHERE o.user_id IN (SELECT user_id FROM vip_users)

-- LEFT ANTI JOIN (Hive 3.1+ — NOT IN / NOT EXISTS)
SELECT o.order_id
FROM orders o
LEFT ANTI JOIN cancelled_orders c ON o.order_id = c.order_id;
```

### Multi-table JOINs
```sql
SELECT o.order_id, u.name, p.name AS product
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.created > '2024-01-01';
```

### Map Join (broadcast join) — small table fits in memory
```sql
-- Hint: forces small table to be broadcast to all mappers (no shuffle)
SELECT /*+ MAPJOIN(u) */ o.order_id, u.name
FROM orders o
JOIN users u ON o.user_id = u.user_id;

-- Auto map join (no hint needed when enabled)
SET hive.auto.convert.join = true;            -- default true
SET hive.mapjoin.smalltable.filesize = 25000000; -- 25MB threshold
```

### Bucket Map Join
```sql
-- Both tables bucketed by join key, same number of buckets
SET hive.optimize.bucketmapjoin = true;

-- Sorted Merge Bucket Join (fastest join type — requires SORTED BY)
SET hive.input.format = org.apache.hadoop.hive.ql.io.BucketizedHiveInputFormat;
SET hive.optimize.bucketmapjoin.sortedmerge = true;
```

### JOIN gotchas
```sql
-- Put larger table LAST in pre-Tez (less relevant with Tez + CBO)
-- Tez CBO automatically reorders joins by size

-- Non-equi join (Hive 2.2+)
SELECT a.id, b.id FROM a JOIN b ON a.val BETWEEN b.lo AND b.hi;

-- JOIN on multiple columns
SELECT * FROM orders o JOIN shipments s
ON o.order_id = s.order_id AND o.region = s.region;
```

---

## GROUP BY, HAVING

```sql
-- Basic aggregation
SELECT status, COUNT(*) AS cnt, SUM(amount) AS total
FROM orders
GROUP BY status;

-- Group by expression
SELECT DATE_FORMAT(created, 'yyyy-MM') AS month, SUM(amount)
FROM orders
GROUP BY DATE_FORMAT(created, 'yyyy-MM');

-- HAVING (filters after aggregation)
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 10;

-- ROLLUP (subtotals)
SELECT region, status, SUM(amount)
FROM orders
GROUP BY region, status WITH ROLLUP;
-- Produces: (region,status), (region,NULL), (NULL,NULL)

-- CUBE (all combinations)
SELECT region, status, SUM(amount)
FROM orders
GROUP BY region, status WITH CUBE;
-- Produces: (region,status), (region,NULL), (NULL,status), (NULL,NULL)

-- GROUPING SETS
SELECT region, status, SUM(amount)
FROM orders
GROUP BY GROUPING SETS ((region, status), (region), ());
-- More explicit control than ROLLUP/CUBE

-- GROUPING() function — identifies which columns are aggregated
SELECT region,
       GROUPING(region) AS is_all_regions,
       SUM(amount)
FROM orders
GROUP BY region WITH ROLLUP;
```

---

## Sorting

```sql
-- ORDER BY: global sort (all data goes through 1 reducer) — guaranteed order
SELECT * FROM orders ORDER BY created DESC;
SELECT * FROM orders ORDER BY created DESC NULLS LAST;
SELECT * FROM orders ORDER BY amount DESC, created ASC;
SELECT * FROM orders ORDER BY amount DESC LIMIT 100;  -- TopK optimization

-- SORT BY: sorts within each reducer — NOT globally ordered across reducers
-- Faster than ORDER BY for large datasets when total order not required
SELECT * FROM orders SORT BY created DESC;

-- DISTRIBUTE BY: routes rows to reducers (like partitioning for the reduce phase)
-- All rows with same key go to same reducer (but no sort within reducer)
SELECT * FROM orders DISTRIBUTE BY user_id;

-- CLUSTER BY: DISTRIBUTE BY + SORT BY on same column(s)
-- Rows with same key go to same reducer AND are sorted within reducer
SELECT * FROM orders CLUSTER BY user_id;
-- Equivalent to:
SELECT * FROM orders DISTRIBUTE BY user_id SORT BY user_id;

-- DISTRIBUTE BY + SORT BY (more flexible than CLUSTER BY)
SELECT * FROM orders
DISTRIBUTE BY region
SORT BY region ASC, amount DESC;
```

---

## UNION

```sql
-- UNION ALL (keeps duplicates — faster, no dedup pass)
SELECT order_id, amount FROM orders_2023
UNION ALL
SELECT order_id, amount FROM orders_2024;

-- UNION DISTINCT (deduplicates — equivalent to UNION in standard SQL)
SELECT user_id FROM buyers
UNION
SELECT user_id FROM newsletter_subscribers;

-- Three-way union
SELECT 'completed' AS src, order_id FROM completed_orders
UNION ALL
SELECT 'pending' AS src, order_id FROM pending_orders
UNION ALL
SELECT 'cancelled' AS src, order_id FROM cancelled_orders;
```

---

## Subqueries

```sql
-- Subquery in FROM clause (derived table / inline view)
SELECT t.status, t.cnt
FROM (
  SELECT status, COUNT(*) AS cnt
  FROM orders
  GROUP BY status
) t
WHERE t.cnt > 100;

-- Subquery in WHERE with IN
SELECT order_id FROM orders
WHERE user_id IN (
  SELECT user_id FROM users WHERE tier = 'premium'
);

-- Subquery with NOT IN
SELECT order_id FROM orders
WHERE user_id NOT IN (
  SELECT user_id FROM blocked_users
);
-- WARNING: NOT IN with NULLs in subquery returns empty result
-- Use LEFT ANTI JOIN instead for safety

-- EXISTS subquery (Hive 0.13+)
SELECT o.order_id FROM orders o
WHERE EXISTS (
  SELECT 1 FROM shipments s WHERE s.order_id = o.order_id
);

-- NOT EXISTS
SELECT o.order_id FROM orders o
WHERE NOT EXISTS (
  SELECT 1 FROM shipments s WHERE s.order_id = o.order_id
);

-- Scalar subquery (single value)
SELECT order_id,
       amount,
       (SELECT AVG(amount) FROM orders) AS avg_amount
FROM orders
LIMIT 100;

-- Correlated subquery
SELECT o.order_id, o.amount
FROM orders o
WHERE o.amount > (
  SELECT AVG(o2.amount) FROM orders o2 WHERE o2.user_id = o.user_id
);
```

---

## CTEs (WITH clause)

```sql
-- Single CTE
WITH monthly_totals AS (
  SELECT DATE_FORMAT(created, 'yyyy-MM') AS month,
         SUM(amount) AS total
  FROM orders
  GROUP BY DATE_FORMAT(created, 'yyyy-MM')
)
SELECT month, total,
       total / LAG(total) OVER (ORDER BY month) - 1 AS mom_growth
FROM monthly_totals
ORDER BY month;

-- Multiple CTEs
WITH
active_users AS (
  SELECT user_id FROM users WHERE last_login > '2024-01-01'
),
recent_orders AS (
  SELECT user_id, SUM(amount) AS total_spent
  FROM orders
  WHERE created > '2024-01-01'
  GROUP BY user_id
)
SELECT u.user_id, COALESCE(o.total_spent, 0) AS spent
FROM active_users u
LEFT JOIN recent_orders o ON u.user_id = o.user_id;

-- CTE used multiple times (computed once in most cases)
WITH order_stats AS (
  SELECT user_id,
         COUNT(*) AS order_count,
         SUM(amount) AS total_amount
  FROM orders
  GROUP BY user_id
)
SELECT user_id, order_count, total_amount,
       total_amount / order_count AS avg_order_value
FROM order_stats
WHERE order_count > 5
ORDER BY total_amount DESC;
```

---

## LATERAL VIEW and EXPLODE

Used to unnest arrays, maps, and other collection types into separate rows.

```sql
-- Explode array
SELECT order_id, tag
FROM orders
LATERAL VIEW EXPLODE(tags) tag_table AS tag;

-- Explode map (produces key, value columns)
SELECT order_id, attr_key, attr_value
FROM orders
LATERAL VIEW EXPLODE(attributes) attr_table AS attr_key, attr_value;

-- POSEXPLODE (includes position/index)
SELECT order_id, pos, tag
FROM orders
LATERAL VIEW POSEXPLODE(tags) tag_table AS pos, tag;

-- Multiple LATERAL VIEWs
SELECT order_id, tag, attr_key
FROM orders
LATERAL VIEW EXPLODE(tags) t AS tag
LATERAL VIEW EXPLODE(attributes) a AS attr_key, attr_value;

-- OUTER LATERAL VIEW (keeps rows even when array is empty/NULL)
SELECT order_id, tag
FROM orders
LATERAL VIEW OUTER EXPLODE(tags) tag_table AS tag;
-- Without OUTER: rows with empty/NULL tags are dropped
-- With OUTER: rows with empty/NULL tags produce one row with tag=NULL

-- inline (explode array of structs)
SELECT order_id, item_id, quantity
FROM orders
LATERAL VIEW INLINE(items) item_table AS item_id, product_id, quantity;

-- json_tuple (extract multiple JSON keys at once)
SELECT order_id, event_id, event_name
FROM event_log
LATERAL VIEW json_tuple(payload, 'event_id', 'event_name') j AS event_id, event_name;
```

---

## Window Functions

```sql
-- Syntax: function() OVER ([PARTITION BY ...] [ORDER BY ...] [ROWS/RANGE BETWEEN ...])

-- ROW_NUMBER: unique sequential number per partition
SELECT order_id, user_id, amount,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created DESC) AS rn
FROM orders;

-- Latest order per user
SELECT order_id, user_id, amount
FROM (
  SELECT order_id, user_id, amount,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created DESC) AS rn
  FROM orders
) t WHERE rn = 1;

-- RANK / DENSE_RANK / NTILE
SELECT user_id, amount,
       RANK()       OVER (ORDER BY amount DESC) AS rank,      -- gaps after ties
       DENSE_RANK() OVER (ORDER BY amount DESC) AS denserank, -- no gaps
       NTILE(4)     OVER (ORDER BY amount DESC) AS quartile   -- 4 buckets
FROM orders;

-- LAG / LEAD (access previous/next row)
SELECT order_id, created, amount,
       LAG(amount, 1, 0) OVER (PARTITION BY user_id ORDER BY created) AS prev_amount,
       LEAD(amount, 1)   OVER (PARTITION BY user_id ORDER BY created) AS next_amount
FROM orders;
-- LAG(col, offset, default)

-- FIRST_VALUE / LAST_VALUE
SELECT order_id, user_id, amount,
       FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY created
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS first_order,
       LAST_VALUE(amount)  OVER (PARTITION BY user_id ORDER BY created
                                 ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS last_order
FROM orders;

-- Running totals / moving averages
SELECT order_id, created, amount,
       SUM(amount)  OVER (PARTITION BY user_id ORDER BY created
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
       AVG(amount)  OVER (PARTITION BY user_id ORDER BY created
                          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day_avg
FROM orders;

-- PERCENT_RANK, CUME_DIST
SELECT amount,
       PERCENT_RANK() OVER (ORDER BY amount) AS pct_rank,  -- 0 to 1
       CUME_DIST()    OVER (ORDER BY amount) AS cume_dist  -- cumulative fraction
FROM orders;

-- Frame specifications
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW   -- from start to current
ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING            -- 7-row sliding window
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING    -- current to end
RANGE BETWEEN INTERVAL '7' DAYS PRECEDING AND CURRENT ROW  -- time-based window
```

---

## TABLESAMPLE

```sql
-- Bucket sampling (deterministic — always same sample for same seed)
SELECT * FROM orders TABLESAMPLE(BUCKET 1 OUT OF 10 ON user_id);
-- Returns 1/10 of rows based on hash(user_id)

-- Block sampling (approximate percentage — Hive 0.10+)
SELECT * FROM orders TABLESAMPLE(10 PERCENT);
-- Fast: reads a fraction of HDFS blocks, not row-by-row

-- Row count sampling
SELECT * FROM orders TABLESAMPLE(1000 ROWS);
-- Returns up to 1000 rows (may read more internally)

-- Combined with WHERE
SELECT * FROM orders TABLESAMPLE(BUCKET 3 OUT OF 10 ON rand())
WHERE status = 'completed';

-- On specific column (for reproducible splits)
SELECT * FROM orders TABLESAMPLE(BUCKET 1 OUT OF 5 ON order_id);
```
