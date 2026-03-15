# Performance & Optimization — Chapters 10-11

Liquid clustering, Z-ordering, file compaction, VACUUM, Bloom filters, and design patterns for cost and throughput.

## Table of Contents

- [Data Layout Strategies](#data-layout-strategies)
- [OPTIMIZE and Compaction](#optimize-and-compaction)
- [VACUUM](#vacuum)
- [Bloom Filters](#bloom-filters)
- [File Size Tuning](#file-size-tuning)
- [Query Performance](#query-performance)
- [Cost Optimization Patterns](#cost-optimization-patterns)
- [High-Throughput Ingestion](#high-throughput-ingestion)

---

## Data Layout Strategies

### Liquid clustering (recommended — Delta 3.0+)

Replaces partitioning and Z-ordering with an adaptive, incremental approach:

```sql
-- At creation
CREATE TABLE events (
  id BIGINT,
  event_type STRING,
  event_date DATE,
  region STRING
) USING DELTA
CLUSTER BY (event_date, event_type);

-- Change clustering columns without rewriting data
ALTER TABLE events CLUSTER BY (event_date, region);

-- Remove clustering
ALTER TABLE events CLUSTER BY NONE;
```

**How it works**:
- OPTIMIZE incrementally rewrites data into clustered files
- No need to choose between partitioning and Z-ordering — liquid clustering subsumes both
- Clustering is applied lazily — only newly written or compacted files are reorganized
- Supports up to 4 clustering columns

**When to use liquid clustering vs partitioning**:

| Scenario | Recommendation |
|----------|---------------|
| New table | Liquid clustering |
| High-cardinality filter columns | Liquid clustering |
| Low-cardinality filter column (<1000 values) | Either (liquid clustering still preferred) |
| Existing partitioned table working well | Keep partitioning |
| Need to filter on different columns over time | Liquid clustering (can change columns) |
| Streaming with frequent small writes | Liquid clustering (handles small files better) |

### Z-ordering (legacy — use liquid clustering for new tables)

Co-locates related data in the same files for multi-dimensional data skipping:

```sql
-- Z-order on specific columns (run after OPTIMIZE)
OPTIMIZE events ZORDER BY (event_date, event_type);
```

**Characteristics**:
- Best with 1-4 columns
- Diminishing returns beyond 4 columns
- Must be reapplied after every OPTIMIZE
- Cannot be combined with partitioning on the same columns

### Partitioning (legacy)

```sql
CREATE TABLE events (...) USING DELTA PARTITIONED BY (event_date);
```

**When partitioning still makes sense**:
- Very low cardinality column (region with <20 values)
- Partition pruning gives definitive file elimination (vs statistical skipping)
- Existing large tables where migration cost is prohibitive

**Partitioning pitfalls**:
- Too many partitions → small file problem (each partition must have files)
- Too few partitions → no benefit
- Cannot change partition columns without rewriting the entire table
- Rule of thumb: each partition should contain at least 1 GB of data

## OPTIMIZE and Compaction

### Basic compaction

```sql
-- Compact small files into larger ones
OPTIMIZE events;

-- Compact specific partition only
OPTIMIZE events WHERE event_date = '2024-06-15';
```

### Predictive optimization (Databricks)

```sql
-- Enable auto-OPTIMIZE and auto-VACUUM
ALTER TABLE events SET TBLPROPERTIES ('delta.enablePredictiveOptimization' = 'true');
```

Databricks automatically determines when to OPTIMIZE and VACUUM based on table activity patterns.

### Auto-compaction

```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',   -- coalesce small writes
  'delta.autoOptimize.autoCompact' = 'true'       -- compact after writes
);
```

- `optimizeWrite`: Coalesces small files during writes (adds write latency)
- `autoCompact`: Runs a lightweight OPTIMIZE after writes (asynchronous)
- Neither replaces periodic full OPTIMIZE — they reduce the problem, not eliminate it

### OPTIMIZE frequency guidelines

| Table type | OPTIMIZE frequency |
|-----------|-------------------|
| Streaming (continuous) | Every 1-6 hours |
| Streaming (triggered) | After each trigger batch |
| Batch (daily loads) | After each load |
| Batch (hourly loads) | Every 4-6 hours or after each load |
| Rarely updated | Weekly or on-demand |

## VACUUM

Removes data files no longer referenced by the transaction log:

```sql
-- Dry run (default) — shows what would be deleted
VACUUM events;

-- Delete files older than retention period
VACUUM events RETAIN 168 HOURS;  -- 7 days (default)
```

### Retention period

```sql
-- Set retention (default 7 days)
ALTER TABLE events SET TBLPROPERTIES (
  'delta.deletedFileRetentionDuration' = 'interval 7 days'
);
```

**Critical rules**:
- Never set retention below 7 days in production — concurrent readers may still need old files
- After VACUUM, time travel to versions older than the retention period fails
- VACUUM does not delete transaction log files — those are controlled by `delta.logRetentionDuration`

### VACUUM vs log retention

| Setting | Controls | Default |
|---------|----------|---------|
| `delta.deletedFileRetentionDuration` | How long VACUUM keeps unreferenced data files | 7 days |
| `delta.logRetentionDuration` | How long transaction log JSON files are kept | 30 days |
| Checkpoint interval | How often checkpoint Parquet files are created | Every 10 commits |

### VACUUM frequency guidelines

| Table type | VACUUM frequency |
|-----------|-----------------|
| High-churn (many updates/deletes) | Daily |
| Moderate updates | Weekly |
| Append-only | Monthly or less |
| Tables with deletion vectors | After OPTIMIZE (purge first, then VACUUM) |

## Bloom Filters

Probabilistic index for point lookups (exact match queries):

```sql
-- Create bloom filter index
CREATE BLOOMFILTER INDEX ON TABLE events FOR COLUMNS (user_id OPTIONS (fpp = 0.01, numItems = 10000000));

-- Drop
DROP BLOOMFILTER INDEX ON TABLE events FOR COLUMNS (user_id);
```

**When to use**:
- High-cardinality columns used in `WHERE col = value` filters
- Columns not used for clustering or partitioning
- Point lookups (not range queries)

**Parameters**:
- `fpp` (false positive probability): Lower = more accurate, larger index. Default 0.1.
- `numItems`: Expected distinct values. Over-estimate slightly for safety.

**Trade-offs**:
- Adds write overhead (index must be maintained)
- Increases storage (bloom filter files alongside data)
- Only helps exact match — no benefit for range, LIKE, or IN queries
- Liquid clustering data skipping often makes Bloom filters unnecessary

## File Size Tuning

### Target file size

```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.targetFileSize' = '134217728'  -- 128 MB
);
```

**Guidelines**:

| Workload | Target file size |
|----------|-----------------|
| BI/analytics (large scans) | 512 MB – 1 GB (default) |
| Streaming (frequent small writes) | 64 – 128 MB |
| Point lookups | 32 – 64 MB |
| Mixed workload | 128 – 256 MB |

### Diagnosing small file problems

```sql
-- Check file count and average size
DESCRIBE DETAIL events;

-- If numFiles is very high and sizeInBytes/numFiles is small → small file problem
```

**Fix**:
1. Run `OPTIMIZE` to compact
2. Set `delta.autoOptimize.optimizeWrite = true`
3. Repartition before writing: `df.repartition(numPartitions).write...`
4. Use `trigger(availableNow=True)` instead of micro-batches for streaming

## Query Performance

### Data skipping

Delta Lake automatically collects min/max statistics for the first 32 columns of each data file. Queries with predicates on these columns skip files whose min/max range doesn't overlap.

```sql
-- Control how many columns get statistics
ALTER TABLE events SET TBLPROPERTIES ('delta.dataSkippingNumIndexedCols' = 32);
```

**Maximize data skipping**:
- Put frequently filtered columns first in schema (within the indexed column limit)
- Use liquid clustering on filter columns
- Avoid high-cardinality string columns in the first 32 positions (unless they're filtered on)

### Caching

```sql
-- Databricks: cache frequently queried table
CACHE SELECT * FROM events WHERE event_date >= current_date() - 7;
```

### Photon engine (Databricks)

Vectorized C++ query engine. No code changes needed — significant speedup for scans, joins, and aggregations. Enabled by choosing a Photon-compatible cluster type.

## Cost Optimization Patterns

### Storage cost reduction

1. **VACUUM regularly** — remove unreferenced files
2. **Reduce retention** — if time travel beyond 7 days isn't needed, keep the default
3. **Use liquid clustering** — avoids small file proliferation from over-partitioning
4. **Compress effectively** — Parquet with ZSTD (default in modern Delta) balances size and speed

### Compute cost reduction

1. **Partition/cluster elimination** — ensure queries hit the right layout
2. **Predicate pushdown** — filter early in the query plan
3. **Column pruning** — select only needed columns
4. **Incremental processing** — use CDF instead of full table scans
5. **`availableNow` trigger** — processes all available data and stops (no idle cluster)

### Write amplification reduction

1. **Enable deletion vectors** — avoid full file rewrites for UPDATE/DELETE/MERGE
2. **Liquid clustering** — incremental reorganization vs full Z-order rewrites
3. **Targeted OPTIMIZE** — compact only affected partitions
4. **Append-only bronze** — avoid updates on ingestion tables

## High-Throughput Ingestion

### Streaming best practices

```python
# Optimal streaming configuration
stream.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/my_stream") \
    .option("maxRecordsPerFile", 1000000)          # control file size
    .trigger(processingTime="30 seconds")           # balance latency vs throughput
    .start("/path/to/table")
```

### Batch ingestion at scale

```python
# Repartition to control output files
df.repartition(200) \
    .write.format("delta") \
    .mode("append") \
    .save("/path/to/table")

# Or coalesce for fewer, larger files
df.coalesce(50) \
    .write.format("delta") \
    .mode("append") \
    .save("/path/to/table")
```

### Multi-cluster writes

- Use optimistic concurrency for independent writes to different partitions/clusters
- For overlapping writes, consider `WriteSerializable` isolation level
- On S3: use DynamoDB log store or coordinated commits for safe concurrent writes
- Monitor commit retry metrics for conflict rates
