# Performance & Optimization — Chapters 6-7

Hidden partitioning, partition transforms, sort orders, compaction, manifest rewriting, snapshot expiry, orphan file cleanup, file sizing, and data skipping.

## Table of Contents

- [Hidden Partitioning](#hidden-partitioning)
- [Partition Transforms](#partition-transforms)
- [Sort Orders](#sort-orders)
- [Compaction (Rewrite Data Files)](#compaction-rewrite-data-files)
- [Rewrite Manifests](#rewrite-manifests)
- [Expire Snapshots](#expire-snapshots)
- [Remove Orphan Files](#remove-orphan-files)
- [File Sizing](#file-sizing)
- [Data Skipping](#data-skipping)
- [Maintenance Schedule](#maintenance-schedule)

---

## Hidden Partitioning

Iceberg separates the physical partition layout from the logical query interface. Users never reference partition columns in queries — Iceberg automatically applies partition pruning.

```sql
-- Table partitioned by month of event_time
CREATE TABLE catalog.db.events (
  id BIGINT,
  event_time TIMESTAMP,
  event_type STRING
) USING iceberg
PARTITIONED BY (months(event_time));

-- Query uses the source column, not the partition column
-- Iceberg automatically prunes to relevant monthly partitions
SELECT * FROM catalog.db.events
WHERE event_time BETWEEN '2024-06-01' AND '2024-06-30';
```

**Benefits**:
- No silent correctness bugs from forgetting partition filter
- No extra partition columns in schema
- Partition layout is an optimization detail, not a query concern
- Can evolve partitions without changing any queries

## Partition Transforms

Iceberg provides built-in transforms applied to source columns:

| Transform | Syntax | Produces | Example |
|-----------|--------|----------|---------|
| Identity | `identity(col)` | Exact value | `identity(region)` → "us-east" |
| Year | `years(col)` | Year integer | `years(ts)` → 2024 |
| Month | `months(col)` | Year-month | `months(ts)` → 2024-06 |
| Day | `days(col)` | Date | `days(ts)` → 2024-06-15 |
| Hour | `hours(col)` | Date-hour | `hours(ts)` → 2024-06-15-10 |
| Bucket | `bucket(N, col)` | Hash bucket 0..N-1 | `bucket(16, user_id)` → 7 |
| Truncate | `truncate(W, col)` | Truncated value | `truncate(10, name)` → "Alex Merce" |

### Multi-column partitioning

```sql
CREATE TABLE catalog.db.events (...)
USING iceberg
PARTITIONED BY (days(event_time), bucket(8, user_id));
```

### Choosing transforms

```
What are the query patterns?
├── Always filter by date range → days(ts) or months(ts)
│   ├── < 10K events/day → months(ts)
│   ├── 10K-10M events/day → days(ts)
│   └── > 10M events/day → hours(ts)
├── Join/filter on high-cardinality key → bucket(N, key)
│   └── N = expected_rows / target_file_size_rows (aim for 128-512MB files)
├── Filter on low-cardinality column → identity(col) if <100 values
└── Combine: days(event_time), bucket(16, user_id)
```

## Sort Orders

Define how rows are sorted within each data file. Improves data skipping and query performance.

```sql
-- Set sort order via table properties
ALTER TABLE catalog.db.events
SET TBLPROPERTIES ('write.distribution-mode' = 'range');

-- Write with sort order (Spark)
ALTER TABLE catalog.db.events WRITE ORDERED BY event_time, event_type;

-- Or unordered
ALTER TABLE catalog.db.events WRITE LOCALLY ORDERED BY event_time;
```

### Distribution modes

| Mode | Behavior | Use case |
|------|----------|----------|
| `none` | No shuffle before write | Fast writes, no ordering |
| `hash` | Hash by partition key | Partition-aligned writes |
| `range` | Range sort by sort columns | Maximizes data skipping |

### Sort order evolution

Sort order changes apply to new writes only. Existing files retain their original sort. Compaction can rewrite old files with the new sort order.

## Compaction (Rewrite Data Files)

Combines small files into larger, optimized files.

### Spark procedure

```sql
-- Basic compaction
CALL catalog.system.rewrite_data_files('db.events');

-- With options
CALL catalog.system.rewrite_data_files(
  table => 'db.events',
  options => map(
    'target-file-size-bytes', '536870912',   -- 512MB
    'min-file-size-bytes', '67108864',       -- 64MB (files smaller are compacted)
    'max-file-size-bytes', '1073741824',     -- 1GB
    'min-input-files', '5'                   -- at least 5 files to trigger compaction
  )
);

-- Compact specific partition only
CALL catalog.system.rewrite_data_files(
  table => 'db.events',
  where => 'event_time >= timestamp ''2024-06-01'' AND event_time < timestamp ''2024-07-01'''
);
```

### Sort-order compaction

```sql
-- Rewrite files with sort order for better data skipping
CALL catalog.system.rewrite_data_files(
  table => 'db.events',
  strategy => 'sort',
  sort_order => 'event_time ASC NULLS LAST, event_type ASC NULLS LAST'
);
```

### Z-order compaction

```sql
-- Z-order for multi-dimensional data skipping
CALL catalog.system.rewrite_data_files(
  table => 'db.events',
  strategy => 'sort',
  sort_order => 'zorder(event_time, user_id)'
);
```

### Compaction frequency

| Scenario | Frequency |
|----------|-----------|
| Streaming (micro-batch) | Every 1-4 hours |
| Batch (daily loads) | After each load |
| After bulk deletes/updates | Immediately (purge delete files) |
| Tables with accumulating MOR delete files | Every 4-8 hours |

## Rewrite Manifests

Optimize manifest file structure for faster query planning:

```sql
CALL catalog.system.rewrite_manifests('db.events');

-- With options
CALL catalog.system.rewrite_manifests(
  table => 'db.events',
  use_caching => true
);
```

**When to run**: After many small writes create many small manifests, increasing planning overhead.

## Expire Snapshots

Remove old snapshots and their associated data/delete files:

```sql
-- Expire snapshots older than a timestamp
CALL catalog.system.expire_snapshots(
  table => 'db.events',
  older_than => TIMESTAMP '2024-06-10 00:00:00'
);

-- Retain at least N snapshots regardless of age
CALL catalog.system.expire_snapshots(
  table => 'db.events',
  older_than => TIMESTAMP '2024-06-10 00:00:00',
  retain_last => 10
);

-- Dry run
CALL catalog.system.expire_snapshots(
  table => 'db.events',
  older_than => TIMESTAMP '2024-06-10 00:00:00',
  stream_results => true
);
```

**Critical**: After expiring snapshots, time travel to expired versions fails. Data files exclusively referenced by expired snapshots are deleted.

**Recommended retention**: Keep snapshots for at least as long as the longest-running query might reference them (typically 1-7 days).

## Remove Orphan Files

Remove data files not referenced by any table metadata:

```sql
CALL catalog.system.remove_orphan_files(
  table => 'db.events'
);

-- With custom retention (default 3 days)
CALL catalog.system.remove_orphan_files(
  table => 'db.events',
  older_than => TIMESTAMP '2024-06-12 00:00:00'
);

-- Dry run — list files without deleting
CALL catalog.system.remove_orphan_files(
  table => 'db.events',
  dry_run => true
);
```

**Caution**:
- Set retention longer than the longest expected write duration
- If a write job is in progress, its files might appear orphaned
- Always dry-run first in production
- Run AFTER expire_snapshots (so you don't delete files still referenced by snapshots)

## File Sizing

### Target file size

```sql
ALTER TABLE catalog.db.events SET TBLPROPERTIES (
  'write.target-file-size-bytes' = '536870912'  -- 512MB
);
```

**Guidelines**:

| Workload | Target file size |
|----------|-----------------|
| Analytics / BI (large scans) | 256 MB – 1 GB |
| Streaming (frequent small writes) | 128 – 256 MB |
| Point lookups | 64 – 128 MB |
| Mixed | 256 MB |

### Diagnosing small file problems

```sql
-- Check file count and sizes
SELECT
  COUNT(*) AS file_count,
  SUM(file_size_in_bytes) / (1024*1024*1024) AS total_gb,
  AVG(file_size_in_bytes) / (1024*1024) AS avg_mb,
  MIN(file_size_in_bytes) / (1024*1024) AS min_mb,
  MAX(file_size_in_bytes) / (1024*1024) AS max_mb
FROM catalog.db.events.files;
```

If `avg_mb` is much smaller than target → run compaction.

### Delete file accumulation

```sql
-- Check delete file overhead
SELECT
  content,
  COUNT(*) AS file_count,
  SUM(file_size_in_bytes) / (1024*1024) AS total_mb
FROM catalog.db.events.all_data_files
GROUP BY content;
-- content 0 = data files, 1 = position deletes, 2 = equality deletes
```

If delete files are numerous → compact to merge them into data files.

## Data Skipping

### How it works

1. **Manifest-list level**: Partition summaries prune entire manifests
2. **Manifest level**: Per-file min/max column statistics prune individual files
3. **File level**: Parquet row group statistics prune row groups within files

### Maximize data skipping

- **Sort data** on commonly filtered columns (sort order or Z-order)
- **Cluster related values** — sorted data has tight min/max ranges per file
- **Use partition transforms** for coarse-grained pruning
- **Keep column statistics** — Iceberg collects min/max/null/NaN for all columns by default
- **Compact regularly** — small files have overlapping ranges, large sorted files have tight ranges

### Column metrics configuration

```sql
-- Collect full statistics for specific columns
ALTER TABLE catalog.db.events SET TBLPROPERTIES (
  'write.metadata.metrics.column.id' = 'full',
  'write.metadata.metrics.column.event_time' = 'full',
  'write.metadata.metrics.default' = 'truncate(16)'  -- truncate long strings
);
```

Modes: `none`, `counts`, `truncate(length)`, `full`.

## Maintenance Schedule

Recommended execution order:

```
1. Compact (rewrite_data_files)    — merge small files and delete files
2. Expire snapshots                — remove old snapshot references
3. Remove orphan files             — clean up unreferenced files
4. Rewrite manifests               — optimize manifest structure
```

| Table profile | Compact | Expire snapshots | Remove orphans | Rewrite manifests |
|--------------|---------|------------------|----------------|-------------------|
| Streaming (continuous) | Every 2-4 hours | Daily | Weekly | Weekly |
| Batch (daily loads) | After each load | Daily | Weekly | Monthly |
| Heavy MOR (many updates) | Every 4-8 hours | Daily | Weekly | Weekly |
| Append-only (growing) | Weekly | Weekly | Monthly | Monthly |
| Rarely updated | Monthly | Monthly | Monthly | Quarterly |
