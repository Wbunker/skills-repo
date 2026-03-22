# Hive Performance Tuning

## Table of Contents
1. [Execution Engines](#execution-engines)
2. [EXPLAIN Output](#explain-output)
3. [Cost-Based Optimizer (CBO)](#cost-based-optimizer-cbo)
4. [Vectorized Execution](#vectorized-execution)
5. [LLAP (Live Long and Process)](#llap-live-long-and-process)
6. [Join Optimizations](#join-optimizations)
7. [Parallel Execution](#parallel-execution)
8. [Compression and ORC Tuning](#compression-and-orc-tuning)
9. [Query Result Cache](#query-result-cache)
10. [Common Performance Patterns](#common-performance-patterns)

---

## Execution Engines

```sql
-- Set execution engine (session-level)
SET hive.execution.engine = tez;    -- default in Hive 3+; recommended
SET hive.execution.engine = spark;  -- Hive on Spark (Hive 1.1+)
SET hive.execution.engine = mr;     -- Legacy MapReduce; avoid

-- Check current engine
SET hive.execution.engine;

-- Tez AM reuse (avoids JVM startup per query)
SET hive.server2.tez.initialize.default.sessions = true;
SET hive.server2.tez.sessions.per.default.queue = 4;
```

### Why Tez over MapReduce

```
• DAG execution: chains operators without writing intermediate results to HDFS
• In-memory shuffle: avoids MR sort-spill for many query shapes
• Pipelining: map output goes directly to reducer without disk spill
• Container reuse: JVMs reused across tasks — faster startup
• Typical speedup: 5-10x faster than MapReduce for analytical queries
```

---

## EXPLAIN Output

```sql
-- Basic EXPLAIN — shows logical plan
EXPLAIN SELECT user_id, SUM(amount) FROM orders GROUP BY user_id;

-- Extended — physical plan, partition info
EXPLAIN EXTENDED SELECT ...;

-- Dependency — shows table/partition dependencies (useful for scheduling)
EXPLAIN DEPENDENCY SELECT ...;

-- Authorization — shows privilege check plan
EXPLAIN AUTHORIZATION SELECT ...;

-- Vectorization — shows vectorized vs non-vectorized operators
EXPLAIN VECTORIZATION SELECT ...;
EXPLAIN VECTORIZATION ONLY SUMMARY SELECT ...;  -- just the summary

-- Analyze (Hive 2.0+) — runs the query and annotates with runtime stats
-- WARNING: actually executes the query
EXPLAIN ANALYZE SELECT ...;
```

### Key things to look for in EXPLAIN output

```
TableScan               → which table/partition being read
partition filter        → confirms partition pruning activated
Filter Operator         → predicate pushdown occurred
Map Join Operator       → broadcast join (small table in memory)
Merge Join Operator     → sort-merge join (large tables)
Group By Operator       → aggregation
Reduce Output           → data going to reducer (shuffle)
Statistics: Num rows    → CBO has stats (good); or estimated (may be wrong)
```

---

## Cost-Based Optimizer (CBO)

CBO uses table/column statistics to choose optimal join order, join type, and execution strategy.

```sql
-- Enable CBO (default true in Hive 3+)
SET hive.cbo.enable = true;

-- Enable join reordering (CBO puts smaller tables first)
SET hive.optimize.cbo.joinreordering = true;   -- Hive 3.1+

-- Correlated column statistics (for multi-column predicates)
SET hive.stats.fetch.column.stats = true;      -- use column stats from Metastore

-- Require collecting stats first:
ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS user_id, amount, status;

-- Check CBO is working:
EXPLAIN SELECT o.order_id, u.name
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE u.tier = 'premium';
-- If CBO active: join order may flip to scan users first (filtered by tier)
```

---

## Vectorized Execution

Processes 1024 rows per batch instead of one row at a time. Major throughput improvement for ORC-format tables.

```sql
-- Enable vectorization (default true in Hive 3+)
SET hive.vectorized.execution.enabled = true;
SET hive.vectorized.execution.reduce.enabled = true;
SET hive.vectorized.execution.reduce.groupby.enabled = true;

-- Verify a query uses vectorization
EXPLAIN VECTORIZATION SELECT SUM(amount) FROM orders WHERE status = 'shipped';
-- Look for: "Execution mode: vectorized" in operator descriptions

-- Requirements for vectorization:
-- • Table stored as ORC (primary format; Parquet with Hive 3.3+)
-- • Columns are primitive types (not STRUCT/MAP/ARRAY)
-- • Supported operators: scan, filter, project, aggregation, sort, join
-- • Some UDFs disable vectorization if not vectorized-aware

-- Force non-vectorized for debugging:
SET hive.vectorized.execution.enabled = false;
```

---

## LLAP (Live Long and Process)

LLAP is an always-on daemon layer that caches data in memory and runs persistent JVMs. Hive 2.0+; most effective on HDP/CDP distributions.

```sql
-- Use LLAP execution mode
SET hive.execution.mode = llap;    -- route queries through LLAP daemons
SET hive.execution.mode = container;  -- standard Tez containers

-- LLAP queue (YARN queue for LLAP daemons)
SET hive.llap.daemon.queue.name = llap;

-- LLAP I/O cache size (set in llap-daemon-site.xml, not per-query)
-- hive.llap.io.memory.size = 40Gi   (heap reserved for ORC data cache)

-- Check LLAP status (from command line):
-- hive --service llapstatus

-- LLAP is most effective when:
-- • Same data scanned repeatedly (cache hit rate matters)
-- • Interactive BI workloads with subsecond expectations
-- • ORC tables with selective predicates (pushdown + cache = very fast)
```

---

## Join Optimizations

### Map Join (broadcast join)

```sql
-- Auto map join (default: enabled)
SET hive.auto.convert.join = true;
SET hive.mapjoin.smalltable.filesize = 25000000;  -- 25MB threshold for auto-broadcast

-- Force map join with hint
SELECT /*+ MAPJOIN(small_table) */ big.col, small.col
FROM big_table big JOIN small_table small ON big.key = small.key;

-- Increase threshold for larger broadcast tables
SET hive.auto.convert.join.noconditionaltask.size = 100000000;  -- 100MB
```

### Skew join

```sql
-- Handle data skew (one key has disproportionate row count)
SET hive.optimize.skewjoin = true;
SET hive.skewjoin.key = 100000;         -- key is "skewed" if > 100K rows per reducer

-- Skew join splits the skewed key into a separate MapReduce job
-- May increase total job count but prevents one slow reducer

-- Alternative: salt the skew key
-- Add random suffix to skewed key on both sides with CROSS JOIN on random values
```

### Join order hints (when CBO is off)

```sql
-- Pre-CBO tip: put larger tables last (now mostly irrelevant with Tez CBO)
-- With CBO disabled, Hive uses left-to-right join order:
SELECT * FROM small_table s
JOIN large_table l ON s.id = l.id;   -- small first → last table cached

-- With CBO enabled: order doesn't matter; optimizer reorders
```

---

## Parallel Execution

```sql
-- Parallel independent stages in a single query
SET hive.exec.parallel = true;           -- default false
SET hive.exec.parallel.thread.number = 8; -- max parallel stages per query

-- Parallel ORDER BY (local sort in mapper, merge in reducer)
-- Automatic with Tez; no explicit setting needed

-- Reduce tasks
SET hive.exec.reducers.bytes.per.reducer = 256000000;  -- 256MB per reducer (default)
SET hive.exec.reducers.max = 1009;                      -- max reducers per job

-- Force specific reducer count
SET mapreduce.job.reduces = 100;   -- overrides auto-calculation

-- Dynamic partition inserts: limit partition writers per node
SET hive.exec.max.dynamic.partitions.pernode = 100;
SET hive.exec.max.dynamic.partitions = 1000;

-- Mapper memory (for Tez containers)
SET hive.tez.container.size = 4096;         -- MB per container
SET hive.tez.java.opts = -Xmx3276m;         -- JVM heap within container
```

---

## Compression and ORC Tuning

### ORC write settings

```sql
-- Compression (set at table level in TBLPROPERTIES or per-session)
SET hive.exec.orc.compress = SNAPPY;       -- NONE, ZLIB, SNAPPY, ZSTD, LZO
-- SNAPPY: fast read/write, moderate compression
-- ZLIB: better compression, slower (good for cold data)
-- ZSTD: best ratio + good speed (Hive 3.1+ with ORC 1.6+)

-- ORC stripe size (default 64MB)
SET hive.exec.orc.stripe.size = 67108864;

-- ORC block size (should match HDFS block size, default 256MB)
SET hive.exec.orc.block.size = 268435456;

-- Bloom filters (speed up point lookups and range scans)
-- Set at table level:
ALTER TABLE orders SET TBLPROPERTIES (
  'orc.bloom.filter.columns' = 'user_id,status',
  'orc.bloom.filter.fpp' = '0.05'
);

-- ORC row index stride (rows between index entries, default 10000)
SET hive.exec.orc.row.index.stride = 10000;

-- Enable ORC predicate pushdown
SET hive.optimize.index.filter = true;   -- pushes WHERE into ORC reader
SET hive.orc.splits.include.file.footer = true;
```

### Small file problem

```sql
-- Problem: many small files → many mappers → slow queries
-- Cause: dynamic partitioning with small partitions, frequent appends

-- Merge small files after INSERT
SET hive.merge.mapfiles = true;          -- merge small files in map-only jobs
SET hive.merge.mapredfiles = true;       -- merge after map-reduce jobs
SET hive.merge.tezfiles = true;          -- merge after Tez jobs (Hive 2.1+)
SET hive.merge.smallfiles.avgsize = 16000000;   -- trigger if avg file < 16MB
SET hive.merge.size.per.task = 256000000;        -- target merged file size 256MB

-- Check file count:
DESCRIBE FORMATTED orders PARTITION (order_date='2024-01-15');
-- Look for: numFiles

-- Manually compact small files (re-insert data):
INSERT OVERWRITE TABLE orders PARTITION (order_date='2024-01-15')
SELECT * FROM orders WHERE order_date = '2024-01-15';
```

---

## Query Result Cache

Cache results of identical queries to serve repeated requests instantly. Hive 3.1+.

```sql
-- Enable query result cache
SET hive.query.results.cache.enabled = true;   -- default false

-- Cache directory on HDFS
-- hive.query.results.cache.directory = /tmp/hive/_resultscache_

-- Maximum total cache size
SET hive.query.results.cache.max.size = 10737418240;  -- 10GB default

-- Maximum entries
SET hive.query.results.cache.max.entries = 200;       -- default 200

-- Cache is invalidated when source tables are modified
-- Exact query text match required (including whitespace)
-- Not used if query reads non-deterministic functions (RAND(), CURRENT_TIMESTAMP)
-- Check if cache was used: look for "Query was served from cache" in HiveServer2 log
```

---

## Common Performance Patterns

### Diagnose slow query

```sql
-- 1. Check partition pruning
EXPLAIN SELECT ... WHERE event_date = '2024-01-15';
-- Look for "partition filter" — if missing, rewrite WHERE clause

-- 2. Check join type
EXPLAIN SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.user_id;
-- Look for "Map Join" (good) vs "Merge Join" (full shuffle)

-- 3. Force partition scan to verify data volume
SELECT COUNT(*) FROM orders WHERE event_date = '2024-01-15';  -- one partition
SELECT COUNT(*) FROM orders;  -- full table scan

-- 4. Check for data skew
SELECT user_id, COUNT(*) as cnt
FROM orders
GROUP BY user_id
ORDER BY cnt DESC LIMIT 10;
-- If top key has >> average count: skew problem
```

### Optimize aggregation

```sql
-- Partial aggregation in mapper (combiner) — default enabled
SET hive.map.aggr = true;
SET hive.groupby.mapaggr.checkinterval = 100000;  -- rows per aggregation check

-- Multiple passes for high-cardinality GROUP BY
SET hive.groupby.skewindata = true;   -- extra pass to handle skew in GROUP BY
```

### Fetch task (fastest queries)

```sql
-- Simple queries with no aggregation/joins/ORDER BY use Fetch task
-- (no MapReduce/Tez at all — direct file read)
SET hive.fetch.task.conversion = more;  -- enables fetch for more query types
-- Values: none (always use MR), minimal (SELECT *, LIMIT only), more (most simple selects)

-- Verify fetch task used:
-- EXPLAIN output shows "Fetch Operator" instead of "Map Operator"
```

### Partition-aware aggregation pattern

```sql
-- Process large date range: partition-by-partition via script
-- Or use a single query with partition pruning:
SELECT order_date,
       SUM(amount)  AS daily_total,
       COUNT(*)     AS order_count
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY order_date;
-- Scans only 31 partitions instead of all historical data
```
