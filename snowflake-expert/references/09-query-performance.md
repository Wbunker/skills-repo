# Analyzing and Improving Snowflake Query Performance

Reference for query profiling, micro-partitions, clustering, materialized views, search optimization, parallelization, cache tuning, warehouse sizing, and migration performance.

## Table of Contents
- [Analyzing Query Performance](#analyzing-query-performance)
- [Deep Query Profile Interpretation](#deep-query-profile-interpretation)
- [Micro-Partitions](#micro-partitions)
- [Data Clustering](#data-clustering)
- [Materialized Views](#materialized-views)
- [Search Optimization Service](#search-optimization-service)
- [Cache Tuning Strategies](#cache-tuning-strategies)
- [Warehouse Right-Sizing Methodology](#warehouse-right-sizing-methodology)
- [Parallelization and Scan Set Distribution](#parallelization-and-scan-set-distribution)
- [Migration Performance and Baselining](#migration-performance-and-baselining)
- [Optimization Techniques Compared](#optimization-techniques-compared)

## Analyzing Query Performance

### Query Profile (Snowsight)
1. Run query in Snowsight
2. Click **Query Profile** tab in results
3. Examine the execution graph:
   - **TableScan** — micro-partitions scanned vs total
   - **Filter** — rows filtered
   - **Join** — join strategy and row counts
   - **Sort** — sort operations
   - **Aggregate** — grouping operations
   - **Result** — final output

**Key metrics:**
- **Partitions scanned vs total** — lower ratio = better pruning
- **Bytes scanned** — less = faster and cheaper
- **Spillage to local/remote storage** — indicates warehouse too small
- **Percentage scanned from cache** — higher = faster

### QUERY_HISTORY Profiling
```sql
-- Recent query performance
SELECT
  QUERY_ID,
  QUERY_TEXT,
  USER_NAME,
  WAREHOUSE_NAME,
  EXECUTION_STATUS,
  TOTAL_ELAPSED_TIME / 1000 AS elapsed_sec,
  BYTES_SCANNED / POWER(1024, 3) AS gb_scanned,
  ROWS_PRODUCED,
  PARTITIONS_SCANNED,
  PARTITIONS_TOTAL,
  BYTES_SPILLED_TO_LOCAL_STORAGE / POWER(1024, 2) AS mb_spilled_local,
  BYTES_SPILLED_TO_REMOTE_STORAGE / POWER(1024, 2) AS mb_spilled_remote,
  PERCENTAGE_SCANNED_FROM_CACHE
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('HOUR', -24, CURRENT_TIMESTAMP())
ORDER BY TOTAL_ELAPSED_TIME DESC
LIMIT 20;
```

### EXPLAIN Plan
```sql
EXPLAIN
SELECT region, SUM(amount)
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY region;

-- Output shows: operations, partitions, expressions, join strategies
```

### HASH() for Testing Equivalence
```sql
-- Verify two tables have identical data
SELECT HASH_AGG(*) FROM table_a;
SELECT HASH_AGG(*) FROM table_b;
-- Same hash = same data
```

### Common Performance Problems
| Symptom | Cause | Fix |
|---------|-------|-----|
| High partitions scanned / total | Poor pruning | Add clustering key |
| Spillage to local storage | Warehouse too small | Increase size or optimize query |
| Spillage to remote storage | Severely undersized | Increase warehouse size significantly |
| Query queuing | Too many concurrent queries | Scale out (multicluster) |
| Slow metadata operations | Large SHOW/DESCRIBE results | Filter queries, use ACCOUNT_USAGE |
| Exploding joins | Cartesian or many-to-many | Fix join conditions |

## Deep Query Profile Interpretation

The Query Profile is the primary tool for diagnosing performance issues. Understanding each operator node is critical for tuning.

### Operator Node Types
| Operator | What It Does | What to Watch |
|----------|-------------|--------------|
| **TableScan** | Reads micro-partitions | Partitions scanned vs total; high ratio = poor pruning |
| **Filter** | Applies WHERE conditions | Rows in vs rows out; low selectivity = consider different approach |
| **JoinFilter** | Bloom filter from build side | Rows eliminated; higher = better join filter effectiveness |
| **Join** (Hash) | Hash join between datasets | Build vs probe side sizes; spillage indicates memory pressure |
| **Join** (Merge) | Merge join on sorted data | Used for sorted inputs; efficient for range joins |
| **Aggregate** | GROUP BY / aggregation | Spillage here = too many groups for memory |
| **Sort** | ORDER BY operations | Spillage = memory pressure; consider removing unnecessary sorts |
| **SortWithLimit** | Top-N queries | Efficient; Snowflake avoids full sort |
| **WindowFunction** | OVER() clauses | Partition size drives memory; large partitions may spill |
| **UnionAll** | Combines result sets | Check for asymmetric branch execution times |
| **Result** | Final output | Row count and bytes returned |
| **WithClause** / **WithReference** | CTE materialization | CTEs referenced multiple times are materialized once |
| **Flatten** | LATERAL FLATTEN | Explosion factor: rows out / rows in |
| **ExternalScan** | External table reads | Slower than native; no pruning metadata |

### Reading Execution Time Breakdown
```
Query Profile → Statistics tab:
┌─────────────────────────────────────────┐
│ Processing:       65%  ← CPU time       │
│ Local Disk I/O:   20%  ← SSD cache miss │
│ Remote Disk I/O:  10%  ← Cloud storage  │
│ Synchronization:   3%  ← Thread sync    │
│ Initialization:    2%  ← Startup        │
└─────────────────────────────────────────┘

- High Processing %: query is compute-bound (scale up warehouse)
- High Remote Disk I/O: data not cached (check pruning, warm cache)
- High Local Disk I/O: large scan from SSD cache
- High Synchronization: thread contention (check parallelism)
```

### Spillage Diagnosis
```sql
-- Find queries with spillage (undersized warehouse)
SELECT
  QUERY_ID,
  WAREHOUSE_SIZE,
  TOTAL_ELAPSED_TIME / 1000 AS elapsed_sec,
  BYTES_SPILLED_TO_LOCAL_STORAGE / POWER(1024, 3) AS gb_spilled_local,
  BYTES_SPILLED_TO_REMOTE_STORAGE / POWER(1024, 3) AS gb_spilled_remote,
  BYTES_SCANNED / POWER(1024, 3) AS gb_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE BYTES_SPILLED_TO_LOCAL_STORAGE > 0
  OR BYTES_SPILLED_TO_REMOTE_STORAGE > 0
ORDER BY BYTES_SPILLED_TO_REMOTE_STORAGE DESC
LIMIT 20;

-- Spillage guidelines:
-- Local spill only: try one size larger warehouse
-- Remote spill: warehouse significantly undersized; scale up 2+ sizes
-- Both: reduce data volume first (better filters, pre-aggregation)
```

### Join Explosion Detection
```sql
-- Detect queries where output rows >> input rows (Cartesian/fan-out)
SELECT
  QUERY_ID,
  QUERY_TEXT,
  ROWS_PRODUCED,
  PARTITIONS_SCANNED,
  TOTAL_ELAPSED_TIME / 1000 AS elapsed_sec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE ROWS_PRODUCED > 100000000  -- 100M+ rows produced
  AND START_TIME >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
ORDER BY ROWS_PRODUCED DESC;
```

## Micro-Partitions

Snowflake automatically divides table data into micro-partitions.

### Characteristics
- **Size:** 50-500 MB of uncompressed data per partition
- **Format:** Columnar (PAX hybrid)
- **Immutable:** Never updated in place; DML creates new partitions
- **Metadata:** Min/max values, distinct counts, null counts per column per partition
- **Automatic:** No manual management needed

### How Pruning Works
```
Query: SELECT * FROM orders WHERE order_date = '2024-01-15'

Snowflake checks metadata:
- Partition 1: order_date min=2024-01-01, max=2024-01-10 → SKIP
- Partition 2: order_date min=2024-01-11, max=2024-01-20 → SCAN
- Partition 3: order_date min=2024-01-21, max=2024-01-31 → SKIP

Only Partition 2 is read from storage → massive I/O savings
```

### Viewing Partition Info
```sql
-- Check clustering quality for a column
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(order_date)');
-- Returns: total_partition_count, average_overlap, average_depth
```

### DML Impact on Micro-Partitions
- **INSERT:** Creates new micro-partitions; data is naturally ordered by insertion order
- **UPDATE/DELETE:** Marks old partitions as deleted, creates new ones with modified data
- **MERGE:** Combination of INSERT + UPDATE/DELETE effects
- Frequent small DML operations degrade natural clustering over time
- **Best practice:** Batch DML operations to create fewer, larger micro-partitions

### Natural Clustering vs Explicit Clustering
```
Natural clustering: Data inserted in time-order automatically clusters by time columns.
Good for: append-only tables loaded in chronological order.

Natural clustering degrades when:
- Rows are updated/deleted frequently (new partitions may span wide value ranges)
- Data is loaded out of order (e.g., late-arriving data)
- Multiple columns are filtered but data only clusters naturally by one

Monitor natural clustering before adding explicit keys:
```
```sql
-- Check if natural clustering is sufficient
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(order_date)');
-- If average_depth is 1-2, natural clustering is fine — don't add a key
-- If average_depth > 5, consider adding a clustering key
```

## Data Clustering

When natural data ordering doesn't align with query patterns, explicit clustering helps.

### Clustering Key Concepts
- A clustering key defines the column(s) by which data should be physically co-located
- Snowflake's **automatic clustering** service re-organizes data in the background
- Costs serverless credits but dramatically improves query pruning

### Choosing Clustering Keys
**Good candidates:**
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- Date/timestamp columns for time-series data
- Low-to-medium cardinality columns (region, status, date)

**Poor candidates:**
- Very high cardinality columns (user_id, UUID) — unless combined with other columns
- Columns rarely filtered on
- Too many columns (max 3-4 is typical)

### Creating and Managing Clustering Keys
```sql
-- Add clustering key to existing table
ALTER TABLE orders CLUSTER BY (order_date, region);

-- Create table with clustering key
CREATE TABLE events (
  event_id INT,
  event_date DATE,
  category STRING,
  payload VARIANT
)
CLUSTER BY (event_date, category);

-- Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(order_date, region)');
-- Returns JSON with:
-- - total_partition_count
-- - total_constant_partition_count (perfectly clustered)
-- - average_overlaps
-- - average_depth
-- Depth 1-2 is well clustered; depth >5 may need clustering

-- Suspend automatic clustering (to save costs)
ALTER TABLE orders SUSPEND RECLUSTER;

-- Resume
ALTER TABLE orders RESUME RECLUSTER;

-- Drop clustering key
ALTER TABLE orders DROP CLUSTERING KEY;
```

### Clustering Depth and Width
- **Depth:** average number of overlapping partitions for a given value range
  - Depth = 1 → perfect clustering (each value range in exactly one partition)
  - Depth > 5 → significant overlap, queries scan more partitions than necessary
- **Width:** number of partitions that overlap for a given range
- **Overlap:** percentage of partitions that overlap with at least one other

### Monitoring Clustering Costs
```sql
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE TABLE_NAME = 'ORDERS'
ORDER BY START_TIME DESC;
```

## Materialized Views

Pre-computed query results maintained automatically by Snowflake (Enterprise+).

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
  DATE_TRUNC('DAY', order_date) AS sale_date,
  region,
  COUNT(*) AS order_count,
  SUM(amount) AS total_amount
FROM orders
GROUP BY 1, 2;

-- Queries automatically use the MV when beneficial (query rewrite)
SELECT region, SUM(total_amount)
FROM mv_daily_sales
WHERE sale_date >= '2024-01-01'
GROUP BY region;
-- ↑ Snowflake may route this through the MV automatically

-- Check maintenance cost
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY
WHERE MATERIALIZED_VIEW_NAME = 'MV_DAILY_SALES'
ORDER BY START_TIME DESC;
```

### Materialized View Limitations
- No joins (single table only)
- No window functions, UDFs, HAVING, ORDER BY, LIMIT
- No nested subqueries
- Supported: SELECT, FROM, WHERE, GROUP BY, aggregate functions
- Maintained by serverless compute (costs credits)

### When to Use
- Expensive aggregations queried frequently
- Base table changes infrequently relative to reads
- Query patterns are predictable and repetitive

## Search Optimization Service

Improves point-lookup queries on large tables (Enterprise+).

```sql
-- Enable search optimization
ALTER TABLE customers ADD SEARCH OPTIMIZATION;

-- Enable for specific columns
ALTER TABLE customers ADD SEARCH OPTIMIZATION
  ON EQUALITY(email),
  ON EQUALITY(customer_id),
  ON SUBSTRING(name);

-- Optimizes these patterns:
-- WHERE email = 'alice@example.com'        → equality
-- WHERE customer_id IN (1, 2, 3)           → equality
-- WHERE name LIKE '%alice%'                → substring
-- WHERE payload:key = 'value'              → semi-structured equality
-- WHERE geo_col WITHIN(...)                → geospatial

-- Check status
SELECT SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('customers');

-- Monitor costs
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY
ORDER BY START_TIME DESC;

-- Disable
ALTER TABLE customers DROP SEARCH OPTIMIZATION;
```

### Search Optimization vs Clustering
| Feature | Clustering | Search Optimization |
|---------|-----------|-------------------|
| Best for | Range queries, time series | Point lookups, equality, substring |
| Query pattern | `WHERE date BETWEEN x AND y` | `WHERE id = 123` |
| Maintenance | Automatic reclustering | Background indexing |
| Cost | Serverless credits | Serverless credits + storage |
| Columns | 3-4 max | Many columns simultaneously |

## Cache Tuning Strategies

### Result Cache Optimization
```sql
-- Result cache returns results in <100ms with zero compute cost
-- Conditions for cache hit:
-- 1. Exact same SQL text (including whitespace and casing)
-- 2. Same role and warehouse context
-- 3. Underlying data unchanged
-- 4. Within 24-hour window

-- Maximize result cache hits:
-- Use parameterized views instead of ad-hoc SQL variations
-- Standardize query formatting across tools
-- Avoid unnecessary column aliases that vary between users

-- Check cache hit rate
SELECT
  COUNT_IF(PERCENTAGE_SCANNED_FROM_CACHE = 0 AND BYTES_SCANNED = 0) AS result_cache_hits,
  COUNT(*) AS total_queries,
  ROUND(result_cache_hits / total_queries * 100, 1) AS cache_hit_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
  AND QUERY_TYPE = 'SELECT';
```

### Warehouse SSD Cache Optimization
```sql
-- SSD cache stores recently scanned micro-partitions on local disk
-- Persists while warehouse is running; lost on suspend

-- Strategies to maximize SSD cache effectiveness:
-- 1. Route similar queries to the same warehouse
-- 2. Set auto-suspend to 5-10 min for interactive warehouses
-- 3. Avoid mixing unrelated workloads on the same warehouse

-- Monitor cache effectiveness
SELECT
  WAREHOUSE_NAME,
  AVG(PERCENTAGE_SCANNED_FROM_CACHE) AS avg_cache_pct,
  COUNT(*) AS query_count
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
  AND WAREHOUSE_NAME IS NOT NULL
GROUP BY WAREHOUSE_NAME
ORDER BY avg_cache_pct ASC;
-- Low avg_cache_pct = warehouse suspended too often or workloads too diverse
```

### Metadata Cache
```sql
-- These queries are answered from metadata alone (zero compute):
SELECT COUNT(*) FROM large_table;
SELECT MIN(date_col), MAX(date_col) FROM large_table;
SELECT COUNT(DISTINCT col) FROM large_table;  -- approximate from metadata

-- Metadata queries are free — use them for data profiling
```

## Warehouse Right-Sizing Methodology

### Step-by-Step Right-Sizing
1. **Start small** — begin with X-Small or Small
2. **Run representative workload** — typical queries, not just simple ones
3. **Check Query Profile** for spillage and execution time
4. **Scale up one size** if spillage occurs or query time is unacceptable
5. **Repeat** until performance meets SLA without spillage
6. **Scale back down** if no spillage and performance exceeds needs

```sql
-- Compare query performance across warehouse sizes
-- Run same query on different sized warehouses and compare
SELECT
  WAREHOUSE_SIZE,
  COUNT(*) AS query_count,
  AVG(TOTAL_ELAPSED_TIME) / 1000 AS avg_elapsed_sec,
  AVG(BYTES_SPILLED_TO_LOCAL_STORAGE) / POWER(1024, 2) AS avg_spill_mb,
  AVG(CREDITS_USED_COMPUTE) AS avg_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT LIKE '%specific_pattern%'
  AND START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_SIZE
ORDER BY WAREHOUSE_SIZE;

-- Doubling warehouse size ≠ halving query time
-- Improvement depends on whether query is I/O bound or compute bound
-- I/O-bound: scales linearly (more nodes = more parallel I/O)
-- Compute-bound: scales well for parallelizable operations
-- Single-thread bottleneck: no improvement from larger warehouse
```

### Workload Isolation Patterns
| Workload | Recommended Size | Auto-Suspend | Scaling Policy |
|----------|-----------------|-------------|---------------|
| **ETL/ELT** | Large-XL | 60s | N/A (single cluster) |
| **BI/Dashboards** | Medium-Large | 300s | Standard (multicluster) |
| **Ad-hoc Analytics** | Small-Medium | 300s | Economy (multicluster) |
| **Data Science** | XL-2XL | 60s | N/A |
| **Development** | X-Small | 60s | N/A |
| **Snowpipe** | Serverless | N/A | N/A |

## Parallelization and Scan Set Distribution

### How Snowflake Parallelizes Queries
- Each warehouse node processes a subset of micro-partitions in parallel
- Larger warehouses = more nodes = more parallel scan threads
- Snowflake distributes work across nodes based on micro-partition assignment

### Parallelism Bottlenecks
```
Symptoms of poor parallelization (visible in Query Profile):
- One operator takes 90%+ of execution time while others are idle
- Skewed data distribution (one node processes much more than others)
- Serial operations that cannot be parallelized

Common causes:
1. Single-row operations (point lookups on unclustered data)
2. Highly skewed join keys (one key value has millions of rows)
3. Large ORDER BY without LIMIT (requires global sort)
4. Scalar subqueries evaluated per row
5. Non-parallelizable UDFs
```

### Improving Parallelism
```sql
-- Replace correlated subqueries with joins
-- BAD: scalar subquery evaluated per row
SELECT
  o.order_id,
  (SELECT MAX(amount) FROM line_items l WHERE l.order_id = o.order_id) AS max_item
FROM orders o;

-- GOOD: join-based approach (fully parallel)
SELECT o.order_id, li.max_amount
FROM orders o
LEFT JOIN (
  SELECT order_id, MAX(amount) AS max_amount
  FROM line_items GROUP BY order_id
) li ON o.order_id = li.order_id;

-- Pre-filter large tables before joining
-- BAD: join then filter
SELECT * FROM fact_table f
JOIN dim_table d ON f.dim_key = d.dim_key
WHERE f.date_col >= '2024-01-01';

-- GOOD: filter then join (reduces scan set for join)
SELECT * FROM (
  SELECT * FROM fact_table WHERE date_col >= '2024-01-01'
) f
JOIN dim_table d ON f.dim_key = d.dim_key;

-- Use QUALIFY to avoid self-joins for deduplication
-- BAD: subquery + join
SELECT * FROM orders
WHERE order_id IN (
  SELECT order_id FROM (
    SELECT order_id, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
  ) WHERE rn = 1
);

-- GOOD: single-pass with QUALIFY
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;
```

### Data Skew Detection
```sql
-- Check for skewed join keys
SELECT
  join_key_column,
  COUNT(*) AS row_count
FROM large_table
GROUP BY join_key_column
ORDER BY row_count DESC
LIMIT 20;
-- If top key has orders of magnitude more rows than average, consider
-- splitting the query or pre-aggregating the skewed key
```

## Migration Performance and Baselining

### Performance Baselining
When migrating to Snowflake or tuning an existing deployment, establish baselines first.

```sql
-- Capture baseline metrics for key queries
CREATE TABLE performance_baseline AS
SELECT
  QUERY_ID,
  QUERY_TEXT,
  WAREHOUSE_NAME,
  WAREHOUSE_SIZE,
  TOTAL_ELAPSED_TIME,
  EXECUTION_TIME,
  COMPILATION_TIME,
  BYTES_SCANNED,
  ROWS_PRODUCED,
  PARTITIONS_SCANNED,
  PARTITIONS_TOTAL,
  BYTES_SPILLED_TO_LOCAL_STORAGE,
  BYTES_SPILLED_TO_REMOTE_STORAGE,
  PERCENTAGE_SCANNED_FROM_CACHE,
  QUERY_TAG,
  START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
  AND EXECUTION_STATUS = 'SUCCESS'
  AND QUERY_TYPE = 'SELECT';
```

### Using QUERY_TAG for Tracking
```sql
-- Tag queries for before/after comparison
ALTER SESSION SET QUERY_TAG = 'baseline_v1';
-- Run queries...

-- After tuning:
ALTER SESSION SET QUERY_TAG = 'tuned_v1';
-- Run same queries...

-- Compare
SELECT
  QUERY_TAG,
  AVG(TOTAL_ELAPSED_TIME) / 1000 AS avg_elapsed_sec,
  AVG(BYTES_SCANNED) / POWER(1024, 3) AS avg_gb_scanned,
  AVG(PARTITIONS_SCANNED::FLOAT / NULLIF(PARTITIONS_TOTAL, 0)) AS avg_prune_ratio,
  SUM(CREDITS_USED_COMPUTE) AS total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TAG IN ('baseline_v1', 'tuned_v1')
GROUP BY QUERY_TAG;
```

### Common Migration Performance Issues
| Issue | Symptom | Resolution |
|-------|---------|------------|
| **Missing clustering** | High partition scan ratios | Add clustering keys matching common filters |
| **Over-normalized schema** | Many joins per query | Denormalize frequently joined tables |
| **Row-by-row processing** | Slow procedural code | Rewrite as set-based SQL |
| **Oracle/SQL Server habits** | Unnecessary hints, cursors | Remove; let Snowflake optimizer decide |
| **Wrong warehouse size** | Spillage or idle compute | Right-size per workload type |
| **SELECT *** | Excessive bytes scanned | Select only needed columns |
| **No result caching** | Same queries re-scan data | Standardize SQL for cache hits |

### Client-Side Performance
- **Driver configuration:** Use latest JDBC/ODBC/Python driver versions
- **Result set size:** Use `LIMIT` or server-side pagination for large results
- **Network latency:** Choose Snowflake region closest to application
- **Connection pooling:** Reuse sessions to avoid authentication overhead
- **Fetch size:** Tune result batch size for JDBC/ODBC drivers (default may be suboptimal)

## Optimization Techniques Compared

| Technique | Cost | Best For | Edition |
|-----------|------|----------|---------|
| **Query result cache** | Free | Repeated identical queries | All |
| **Warehouse sizing** | Compute | All queries | All |
| **Clustering keys** | Serverless | Range scans, time-series filters | Enterprise+ |
| **Materialized views** | Serverless + storage | Expensive repeated aggregations | Enterprise+ |
| **Search optimization** | Serverless + storage | Point lookups on large tables | Enterprise+ |

### General Optimization Checklist
1. Check Query Profile for partition scan ratios
2. Add clustering keys for poorly-pruned filters
3. Consider materialized views for repeated expensive aggregations
4. Use search optimization for point lookups
5. Right-size warehouses (check spillage)
6. Use QUALIFY instead of subqueries for window function filters
7. Avoid `SELECT *` — select only needed columns
8. Use `LIMIT` during development
9. Pre-filter before joins
10. Use `APPROX_COUNT_DISTINCT` for large cardinality counts
