# Hive Views

## Table of Contents
1. [Standard Views](#standard-views)
2. [Materialized Views](#materialized-views)
3. [Automatic Query Rewriting](#automatic-query-rewriting)

---

## Standard Views

Views are logical constructs — stored queries with no physical data. Hive evaluates the view definition inline at query time.

### Create and manage views

```sql
-- Create view
CREATE VIEW order_summary AS
SELECT user_id,
       COUNT(*) AS order_count,
       SUM(amount) AS total_spent
FROM orders
WHERE status != 'cancelled'
GROUP BY user_id;

-- Create with column aliases
CREATE VIEW vw_active_orders (order_ref, customer, total)
AS
SELECT order_id, CONCAT(first_name, ' ', last_name), amount
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'active';

-- IF NOT EXISTS
CREATE VIEW IF NOT EXISTS order_summary AS
SELECT ...;

-- Replace existing view
CREATE OR REPLACE VIEW order_summary AS
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id;

-- Alter view query
ALTER VIEW order_summary AS
SELECT user_id, COUNT(*) AS order_count, MAX(amount) AS max_order
FROM orders
GROUP BY user_id;

-- Rename view
ALTER VIEW order_summary RENAME TO vw_order_summary;

-- Set view properties
ALTER VIEW vw_order_summary SET TBLPROPERTIES ('comment' = 'Updated view');

-- Drop view
DROP VIEW vw_order_summary;
DROP VIEW IF EXISTS vw_order_summary;
```

### Query views

```sql
-- Use just like a table
SELECT * FROM order_summary WHERE total_spent > 1000;

-- Views can be joined, subqueried, etc.
SELECT u.name, os.order_count
FROM users u
JOIN order_summary os ON u.user_id = os.user_id
WHERE os.order_count > 5;

-- Show views
SHOW VIEWS;
SHOW VIEWS IN mydb;
SHOW VIEWS LIKE 'vw_order*';

-- Describe view
DESCRIBE vw_order_summary;
DESCRIBE EXTENDED vw_order_summary;  -- shows view definition
DESCRIBE FORMATTED vw_order_summary; -- includes Table Type: VIRTUAL_VIEW
```

### View behavior and limitations

```
• Views are read-only — no INSERT/UPDATE/DELETE/LOAD DATA
• No partition pruning propagation (can't prune base table via view WHERE)
  → Use partitioned tables directly if pruning is critical
• No TABLESAMPLE on views
• Views can reference other views (nested views supported)
• Column types fixed at CREATE time; schema changes to base table may break view
• ORDER BY in a view definition may not work as expected — apply ORDER BY in outer query
• LATERAL VIEW and window functions work inside view definitions
```

---

## Materialized Views

Materialized views (MVs) store pre-computed query results physically. Hive 3.0+.

**When to use:**
- Repeated aggregation queries on large tables (star schema rollups)
- Queries that benefit from pre-joined data
- Automatic query rewriting — let Hive use MV without changing application queries

### Create materialized views

```sql
-- Basic materialized view
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT DATE_FORMAT(created, 'yyyy-MM-dd') AS sale_date,
       SUM(amount) AS total_sales,
       COUNT(*) AS order_count
FROM orders
GROUP BY DATE_FORMAT(created, 'yyyy-MM-dd');

-- With storage options
CREATE MATERIALIZED VIEW mv_user_stats
STORED AS ORC
TBLPROPERTIES ('orc.compress' = 'SNAPPY')
AS
SELECT user_id,
       COUNT(*) AS order_count,
       SUM(amount) AS total_spent,
       MAX(created) AS last_order
FROM orders
GROUP BY user_id;

-- Disable automatic rewriting for this MV
CREATE MATERIALIZED VIEW mv_daily_sales
DISABLE REWRITE
AS
SELECT ...;

-- Partitioned materialized view (Hive 3.2+)
CREATE MATERIALIZED VIEW mv_sales_by_region
PARTITIONED ON (region)
AS
SELECT region, SUM(amount) AS total
FROM orders
GROUP BY region;
```

### Manage materialized views

```sql
-- Rebuild (refresh data from source tables)
ALTER MATERIALIZED VIEW mv_daily_sales REBUILD;

-- Enable/disable automatic query rewriting
ALTER MATERIALIZED VIEW mv_daily_sales ENABLE REWRITE;
ALTER MATERIALIZED VIEW mv_daily_sales DISABLE REWRITE;

-- Drop
DROP MATERIALIZED VIEW mv_daily_sales;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_sales;

-- Show materialized views
SHOW MATERIALIZED VIEWS;
SHOW MATERIALIZED VIEWS IN mydb;

-- Describe
DESCRIBE FORMATTED mv_daily_sales;
-- Table Type: MATERIALIZED_VIEW
```

### Freshness and staleness

```sql
-- MVs become "stale" after source table changes
-- Hive tracks source table write IDs to detect staleness

-- Check if MV is up to date
DESCRIBE FORMATTED mv_daily_sales;
-- Look for: rewriting.enabled and whether it's marked outdated

-- MVs with outdated data are NOT used for automatic rewriting by default
-- To allow stale MVs for rewriting:
SET hive.materializedview.rewriting.incremental = true;
-- (Hive 3.1+ — incremental rebuild instead of full rebuild)
```

---

## Automatic Query Rewriting

When `ENABLE REWRITE` is set on a materialized view, Hive's query optimizer can transparently redirect queries to use the MV instead of scanning base tables.

```sql
-- Prerequisite: CBO must be enabled (default in Hive 3+)
SET hive.cbo.enable = true;
SET hive.materializedview.rewriting = true;  -- default true in Hive 3+

-- Create MV with rewriting enabled
CREATE MATERIALIZED VIEW mv_user_totals
ENABLE REWRITE
AS
SELECT user_id, SUM(amount) AS total_spent
FROM orders
GROUP BY user_id;

-- This query can now be transparently rewritten to use mv_user_totals:
SELECT user_id, SUM(amount) FROM orders GROUP BY user_id;
-- Hive optimizer detects equivalence and rewrites to: SELECT * FROM mv_user_totals

-- Check if rewriting happened using EXPLAIN
EXPLAIN
SELECT user_id, SUM(amount) FROM orders GROUP BY user_id;
-- If rewritten: output shows TableScan on mv_user_totals, not orders
```

### Rewriting requirements

```
• CBO (hive.cbo.enable = true) must be on
• MV must not be stale (source tables not modified since last REBUILD)
• Query must be structurally equivalent to (or subsumable by) the MV definition
• Supported rewrites:
  - Exact match: query same as MV definition
  - Subsumption: query is a more-filtered version of MV
  - Join rewriting: queries involving joins that the MV pre-joined
  - Aggregate rewriting: rollup from fine-grained MV to coarser aggregation
• Not supported: queries that require data the MV doesn't contain
```

### MV vs standard view performance comparison

| | Standard View | Materialized View |
|--|--------------|-------------------|
| Storage | No physical data | Stores pre-computed rows |
| Query speed | Same as base table scan | Fast (pre-aggregated) |
| Data freshness | Always current | Stale until REBUILD |
| REBUILD required | No | Yes, after source changes |
| Automatic rewrite | No | Yes (ENABLE REWRITE) |
| Partition pruning | No (re-executes full view) | Yes (if partitioned) |
| Use case | Simplify complex queries | Accelerate repeated aggregations |
