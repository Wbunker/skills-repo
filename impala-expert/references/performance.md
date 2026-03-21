# Query Performance and Tuning
## Chapter 5: COMPUTE STATS, EXPLAIN Plans, Join Strategies, Runtime Filters, Memory, Admission Control

---

## The Performance Tuning Workflow

```
1. Run EXPLAIN <query>     → understand plan before executing
2. Run the query           → get results + timing
3. Run SUMMARY             → per-node row counts and timing
4. Run PROFILE (verbose)   → full runtime details if needed
5. Identify bottleneck     → large broadcast, missing stats, skew
6. Fix: COMPUTE STATS / hints / schema change / query rewrite
7. Repeat
```

---

## COMPUTE STATS

Statistics tell the query planner the size of tables and columns — essential for choosing join strategies and estimating cardinality.

```sql
-- Compute stats for a whole table (all columns + table-level)
COMPUTE STATS orders;

-- Compute only table-level stats (row count, file count, size)
COMPUTE STATS orders (table);

-- Compute stats for specific columns
COMPUTE STATS orders (customer_id, amount, order_date);

-- Incremental stats: compute only for new/changed partitions (much faster for large tables)
COMPUTE INCREMENTAL STATS sales_by_day;
COMPUTE INCREMENTAL STATS sales_by_day PARTITION (dt='2024-01-15');

-- Drop stats
DROP STATS orders;
DROP INCREMENTAL STATS sales_by_day PARTITION (dt='2024-01-01');

-- View stats
SHOW TABLE STATS orders;
SHOW COLUMN STATS orders;
```

**What COMPUTE STATS collects:**

| Statistic | Used For |
|-----------|---------|
| Row count (table) | Estimating which join side is smaller |
| Data size (bytes) | Memory estimates, file count |
| Distinct count (per column) | Group-by cardinality, join estimates |
| NULL count (per column) | Cardinality estimates |
| Min / Max (per column) | Range pruning estimates |

**When to run:**
- After loading new data into a table (`INSERT`, `LOAD DATA`)
- After `CTAS` (CREATE TABLE AS SELECT)
- When EXPLAIN shows incorrect cardinality estimates
- After adding new partitions with significant data

---

## EXPLAIN Plans

```sql
EXPLAIN SELECT c.region, SUM(o.amount)
FROM orders o JOIN customers c ON o.customer_id = c.id
GROUP BY c.region;
```

### Reading EXPLAIN Output

```
Estimated Per-Host Requirements: Memory=512MB VCores=2
WARNING: The following tables are missing relevant table and/or column statistics.
  orders, customers
...
PLAN-ROOT SINK
|
06:AGGREGATE [FINALIZE]
|  output: sum(amount)
|  group by: region
|
05:EXCHANGE [UNPARTITIONED]
|
02:AGGREGATE
|  output: sum(amount)
|  group by: region
|
04:HASH JOIN [INNER JOIN, BROADCAST]
|  hash predicates: o.customer_id = c.id
|  runtime filters: RF000 <- c.id
|
|--03:EXCHANGE [BROADCAST]
|  |
|  01:SCAN HDFS [db.customers c]
|     partitions=1/1 files=1 size=2MB
|
00:SCAN HDFS [db.orders o]
   partitions=365/365 files=365 size=50GB
   runtime filters: RF000 -> o.customer_id
```

**Key things to check:**

| Item | What to Look For |
|------|-----------------|
| `BROADCAST` join | Is the broadcast side small? Should it be? |
| `HASH JOIN` (shuffle) | Are both sides large? Good sign. |
| `partitions=N/M` | N=scanned, M=total — is pruning happening? |
| `WARNING: missing statistics` | Run COMPUTE STATS immediately |
| `runtime filters` | Confirm filters are being pushed to scan nodes |
| Memory estimate | Does it fit in admission control pool? |
| Row counts per node | Large numbers indicate expensive operations |

### EXPLAIN Levels

```sql
SET EXPLAIN_LEVEL = 0;  -- Brief (operators only)
SET EXPLAIN_LEVEL = 1;  -- Default (key details)
SET EXPLAIN_LEVEL = 2;  -- Extended (predicates, filters)
SET EXPLAIN_LEVEL = 3;  -- Verbose (all details, for deep debugging)
```

---

## Join Strategies

### Broadcast Join (Default for Small Tables)

One side (the smaller "build" side) is copied entirely to every executor node. The larger side ("probe") is scanned locally.

```
Build side (small): customers (2 MB) → copied to ALL nodes
Probe side (large): orders (50 GB) → each node scans local blocks
→ No network shuffle for the probe side
```

**Impala chooses broadcast when**: build side is below the broadcast threshold (default: smaller than the probe side; ~16 MB threshold if stats are available).

**Force broadcast:**
```sql
SELECT /*+ BROADCAST(c) */ o.order_id, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id;
```

### Shuffle Join (Partitioned Hash Join)

Both sides are repartitioned (shuffled) by the join key hash. Each node only joins rows with matching hash values.

```
orders (50 GB) → each row sent to node based on hash(customer_id)
customers (2 GB) → each row sent to node based on hash(id)
→ Each node joins only its partition of the data
→ More network, but handles large build sides
```

**Force shuffle:**
```sql
SELECT /*+ SHUFFLE */ o.order_id, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id;
```

**Use shuffle when:**
- Both sides are large (build side > broadcast threshold)
- Stats indicate the optimizer is making a wrong broadcast choice
- Getting "out of memory" errors in broadcast joins

### Join Ordering

Impala's planner orders joins based on statistics. The smallest table should ideally be the last one listed in the EXPLAIN (innermost build side of the first join).

```sql
-- If planner makes wrong choices, use STRAIGHT_JOIN hint
-- to disable join reordering and use your specified order
SELECT STRAIGHT_JOIN o.order_id, c.name, p.category
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id;
-- Impala joins in exactly this order: orders → customers → products
```

**Best practice**: Run COMPUTE STATS first; let the planner decide. Only use hints when stats don't help.

---

## Runtime Filters

Runtime filters are **Bloom filters** generated from the build side of a join and pushed to the scan nodes of the probe side.

```
Join: orders JOIN customers ON orders.customer_id = customers.id

1. Scan customers → build Bloom filter of all customer_id values
2. Push Bloom filter to orders scan node
3. Orders scan tests each row: does this customer_id pass the Bloom filter?
4. Rows that fail → skipped before reaching join node
```

**Effect**: Can skip entire Parquet row groups if statistics indicate no matching keys.

```sql
-- Control runtime filter behavior
SET RUNTIME_FILTER_MODE = OFF;    -- disable (for debugging)
SET RUNTIME_FILTER_MODE = LOCAL;  -- only local filters (within a fragment)
SET RUNTIME_FILTER_MODE = GLOBAL; -- cross-node filters (default; most powerful)

-- Tuning
SET RUNTIME_BLOOM_FILTER_SIZE = 1048576;  -- Bloom filter size in bytes (1 MB default)
SET MAX_NUM_RUNTIME_FILTERS = 10;         -- max filters per query
```

---

## Partition Pruning

Partition pruning eliminates entire HDFS directories from the scan when predicates match partition columns.

```sql
-- Pruning happens: predicate on partition column
SELECT * FROM sales_by_day WHERE dt = '2024-01-15';
-- → scans only /data/sales/dt=2024-01-15/

-- Pruning works with ranges
SELECT * FROM sales_by_day WHERE dt BETWEEN '2024-01-01' AND '2024-01-31';
-- → scans 31 partitions out of potentially thousands

-- Pruning DOES NOT happen if you apply a function to the partition column
SELECT * FROM sales_by_day WHERE YEAR(dt) = 2024;
-- → scans ALL partitions (function prevents direct comparison)
-- Fix: WHERE dt BETWEEN '2024-01-01' AND '2024-12-31'
```

**EXPLAIN shows pruning:**
```
00:SCAN HDFS [sales_by_day]
   partitions=31/1460 files=31 size=7.8GB
   ^^^^^^^^^^^^^^^^^^
   31 of 1460 partitions scanned = partition pruning working
```

---

## Query Memory Management

### Per-Query Memory Limit

```sql
-- Set for the session
SET MEM_LIMIT = '8g';
SET MEM_LIMIT = 4294967296;  -- bytes
SET MEM_LIMIT = 0;           -- no per-query limit (uses pool limit)

-- View current setting
SET;
```

Memory limit applies per-executor-node. A 8 GB limit on a 10-node cluster = 80 GB total.

### Memory Spilling

When a query exceeds the per-node memory limit, Impala can spill intermediate data to disk:

```sql
-- Enable spilling (default on in CDH 5+)
SET DISABLE_UNSAFE_SPILLS = false;

-- Set scratch space directory (configured in impalad startup)
-- --scratch_dirs=/tmp/impala-scratch
```

Spilling is much slower than in-memory processing. If a query consistently spills:
1. Increase `MEM_LIMIT`
2. Increase admission control pool memory limits
3. Optimize the query (reduce intermediate set sizes)
4. Add nodes to the cluster

### MT_DOP (Multi-Threaded Degree of Parallelism)

```sql
-- Use multiple threads per executor node (Impala 2.10+)
SET MT_DOP = 4;  -- 4 threads per impalad for scan/aggregation
-- Useful for queries on small clusters or when data is in few large files
-- Do NOT use with STRAIGHT_JOIN or when memory is constrained
```

---

## Common Performance Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `SELECT *` on wide tables | Reads all columns unnecessarily | Select only needed columns |
| Function on partition column in WHERE | Disables partition pruning | Rewrite predicate without function |
| Missing COMPUTE STATS | Planner makes wrong join choices | `COMPUTE STATS <table>` |
| Broadcasting a large table | OOM or slow joins | Add broadcast size hint or force shuffle |
| Tiny partitions (<10 MB) | Too many files, metadata overhead | Compaction job; larger partition granularity |
| Very large LIMIT without ORDER BY | Still scans full table | Add predicates to reduce input |
| `COUNT(DISTINCT col)` at huge scale | Requires global dedup | Use `NDV(col)` for approximate count |

---

## SUMMARY and PROFILE

After running a query in impala-shell:

```sql
-- Per-node summary (rows in/out, time per node)
SUMMARY;

-- Full runtime profile (verbose; use for deep debugging)
PROFILE;
```

**SUMMARY output interpretation:**
```
Operator                  #Hosts   Avg Time   Max Time   #Rows   Peak Mem
---------------------------------------------------------------------
09:AGGREGATE              10       2.73s      3.12s      1.2M    156 MB
08:EXCHANGE               10       412ms      512ms      1.2M
07:HASH JOIN              10       18.5s      22.1s      45.6M   2.1 GB  ← bottleneck
...
```

High `Max Time` relative to `Avg Time` = **data skew** — one node gets disproportionately more rows.
