# Maintaining and Optimizing Hudi Tables
## Chapter 6: Compaction, Clustering, Cleaning, Deployment Modes, Layout Optimization

---

## Table Services Overview

Hudi provides three table services that run as background operations to maintain performance and manage storage:

```
┌─────────────────────────────────────────────────────────────┐
│  SERVICE     │  PURPOSE                    │  TABLE TYPE    │
├─────────────────────────────────────────────────────────────┤
│  Compaction  │  Merge log files → Parquet  │  MOR only      │
│  Clustering  │  Reorganize file layout     │  COW + MOR     │
│  Cleaning    │  Delete old file versions   │  COW + MOR     │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Modes

Each table service can be deployed in three modes:

### Inline Mode

Service runs synchronously **within the writer job**, after each commit.

```python
# Compaction inline
"hoodie.compact.inline": "true",
"hoodie.compact.inline.max.delta.commits": "5",   # compact after every 5 deltacommits

# Clustering inline
"hoodie.clustering.inline": "true",
"hoodie.clustering.inline.max.commits": "4",       # cluster after every 4 commits

# Cleaning inline
"hoodie.clean.automatic": "true",                  # always inline by default
"hoodie.clean.async": "false",
```

**Pros:** Simple — no separate job to manage.
**Cons:** Adds latency to each writer commit. For high-frequency streaming, this is usually unacceptable.

### Async Mode

Service is **scheduled** by the writer job (creates a plan on the timeline) but **executed** by a separate concurrent Spark job.

```python
# Schedule compaction in writer
"hoodie.compact.inline": "false",
"hoodie.compact.schedule.inline": "true",
"hoodie.compact.inline.max.delta.commits": "5",

# Separate async executor (standalone Spark job)
# spark-submit ... --class org.apache.hudi.utilities.HoodieCompactor \
#   --mode scheduleAndExecute \
#   --base-path s3://bucket/orders/
```

**Pros:** Writer is not blocked. Services run in parallel.
**Cons:** Two jobs to coordinate. Requires multiwriter concurrency support (see `concurrency.md`).

### Standalone Mode

Services run entirely independently — no schedule or execution in the writer job. Triggered via CLI or separate orchestration (Airflow, etc.).

```bash
# Schedule compaction plan
spark-submit ... org.apache.hudi.utilities.HoodieCompactor \
  --mode schedule \
  --base-path s3://bucket/orders/

# Execute compaction plan
spark-submit ... org.apache.hudi.utilities.HoodieCompactor \
  --mode execute \
  --base-path s3://bucket/orders/

# Or schedule + execute in one step
spark-submit ... org.apache.hudi.utilities.HoodieCompactor \
  --mode scheduleAndExecute \
  --base-path s3://bucket/orders/
```

**Pros:** Full resource and timing control. Required for most production setups.
**Cons:** External orchestration needed.

---

## Compaction (MOR Tables Only)

Compaction merges accumulated `.log` files back into Parquet base files, restoring read performance on MOR tables.

```
Before compaction (MOR partition):
  file001_20240101.parquet    ← base file (old)
  file001_20240101.log.1      ← 50K records
  file001_20240101.log.2      ← 80K records
  file001_20240101.log.3      ← 60K records

Snapshot read must merge all 4 files (slow)

After compaction:
  file001_20240115.parquet    ← new base file with all merged records

Snapshot read: pure Parquet scan (fast)
```

### Compaction Plan

Compaction works in two steps:
1. **Schedule**: Writer creates a compaction plan (`.compaction.requested` on timeline) listing which log files to compact
2. **Execute**: Executor reads the plan, performs the merge, writes new Parquet, commits

### Key Compaction Configs

```python
"hoodie.compact.inline": "false",                        # run async, not inline
"hoodie.compact.inline.max.delta.commits": "5",          # trigger after N deltacommits
"hoodie.compaction.strategy": "org.apache.hudi.table.action.compact.strategy.LogFileSizeBasedCompactionStrategy",
"hoodie.compaction.logfile.size.threshold": "1073741824", # 1GB: compact when logs reach this size
"hoodie.compaction.target.io": "500000000000",           # bytes of I/O per compaction run
"hoodie.parquet.max.file.size": "134217728",             # 128MB target file size
```

### Compaction Strategies

| Strategy | Behavior | Best For |
|----------|----------|---------|
| `UnBoundedCompactionStrategy` | Compact all pending log files | Small tables, infrequent runs |
| `LogFileSizeBasedCompactionStrategy` | Compact file groups whose log files exceed threshold | Large tables with uneven write patterns |
| `BoundedIOCompactionStrategy` | Limit total I/O per run | Resource-constrained environments |

---

## Clustering

Clustering reorganizes data across file groups to optimize the physical layout for query patterns. Available for both COW and MOR tables.

```
Before clustering:
  Many small files from frequent inserts:
  part=US/ [2MB] [3MB] [1MB] [4MB] [2MB]
  Records unsorted; no locality for common query patterns

After clustering:
  Fewer, larger files sorted by common query column:
  part=US/ [128MB sorted by customer_id] [128MB sorted by customer_id]
  Queries filtering by customer_id skip most files
```

### What Clustering Does

1. Groups small files into larger files (fixes the small file problem)
2. Sorts data within files by specified columns (improves data skipping)
3. Does NOT change partition layout — only reorganizes within partitions

### Clustering Configuration

```python
# Enable and trigger
"hoodie.clustering.inline": "false",
"hoodie.clustering.async.enabled": "true",
"hoodie.clustering.inline.max.commits": "4",

# Strategy: which files to cluster
"hoodie.clustering.plan.strategy.class":
    "org.apache.hudi.table.action.cluster.strategy.SparkSizeBasedClusteringPlanStrategy",
"hoodie.clustering.plan.strategy.target.file.max.bytes": "134217728",   # 128MB
"hoodie.clustering.plan.strategy.small.file.limit": "104857600",        # files < 100MB
"hoodie.clustering.plan.strategy.max.bytes.per.group": "2147483648",    # 2GB per cluster group

# Sort order within clustered files
"hoodie.clustering.plan.strategy.sort.columns": "customer_id,order_date",

# Execution strategy
"hoodie.clustering.execution.strategy.class":
    "org.apache.hudi.client.clustering.run.strategy.SparkSortAndSizeExecutionStrategy",
```

### Clustering vs Compaction

| Aspect | Compaction | Clustering |
|--------|-----------|-----------|
| Table type | MOR only | COW + MOR |
| Input | Base file + log files | Base files only |
| Output | New Parquet base file | Reorganized Parquet files |
| Purpose | Eliminate log file merge overhead | Improve file layout for queries |
| Concurrency | Runs alongside writers (with MVCC) | Blocks writers on affected file groups |

---

## Cleaning

Cleaning removes old file slices from the table to reclaim storage. Without cleaning, every historical version of every file is retained indefinitely.

```
Timeline state:
  20240101.commit  → file001_v1.parquet
  20240108.commit  → file001_v2.parquet
  20240115.commit  → file001_v3.parquet (current)

With hoodie.cleaner.commits.retained=2:
  Cleaner runs → deletes file001_v1.parquet
  Only v2 and v3 retained
  Time travel to 20240101 is no longer possible
```

### Cleaning Policies

**KEEP_LATEST_COMMITS** (default): retain the last N commit instants worth of file slices.

```python
"hoodie.cleaner.policy": "KEEP_LATEST_COMMITS",
"hoodie.cleaner.commits.retained": "10",    # keep last 10 commits
```

**KEEP_LATEST_FILE_VERSIONS**: retain the last N versions of each file group.

```python
"hoodie.cleaner.policy": "KEEP_LATEST_FILE_VERSIONS",
"hoodie.cleaner.fileversions.retained": "3",
```

**KEEP_LATEST_BY_HOURS**: retain all file slices written within the past N hours.

```python
"hoodie.cleaner.policy": "KEEP_LATEST_BY_HOURS",
"hoodie.cleaner.hours.retained": "24",
```

### Savepoints

Savepoints pin a specific instant, preventing the cleaner from removing its file slices even if they fall outside the retention window. Useful for long-running time travel use cases.

```bash
# Create a savepoint
hoodie-cli> savepoint create --commit 20240101100000000 --sparkMaster yarn

# Delete a savepoint (re-enables cleaning of that instant's files)
hoodie-cli> savepoint delete --commit 20240101100000000
```

---

## Layout Optimization Strategies

### Z-Ordering (Multi-Dimensional Clustering)

Z-ordering interleaves the bits of multiple sort columns so records close in value across all columns are co-located. Better than sorting by one column when queries filter on multiple dimensions.

```python
"hoodie.clustering.plan.strategy.sort.columns": "customer_id,product_category,order_date",
# With Z-ordering execution strategy:
"hoodie.clustering.execution.strategy.class":
    "org.apache.hudi.client.clustering.run.strategy.SparkZOrderingClusteringExecutionStrategy",
```

**When Z-ordering wins over single-column sort**: queries filter on 2–4 columns of roughly equal selectivity (e.g., customer_id AND region AND product_category).

### File Sizing Guidelines

| Workload | Target File Size | Rationale |
|---------|-----------------|-----------|
| HDFS/local | 512MB–1GB | Match HDFS block size |
| S3/ADLS/GCS | 128MB–256MB | Avoid object storage listing overhead |
| Streaming MOR | 64MB–128MB base | Log files accumulate; compact frequently |

### Small File Problem Prevention

Hudi auto-merges small files during upserts (routing new inserts to undersized file groups). Key configs:

```python
"hoodie.parquet.small.file.limit": "104857600",  # 100MB: files below this get new inserts routed to them
"hoodie.parquet.max.file.size": "134217728",     # 128MB: target size after merge
"hoodie.copyonwrite.insert.split.size": "500000", # records per file group for new inserts
```

If small files still accumulate, trigger clustering to consolidate.

---

## Production Table Maintenance Checklist

```
MOR Tables:
□ Compaction scheduled (inline or async)
  □ Trigger: every 5-10 deltacommits or when log size > 1GB
  □ Monitor: hoodie_timeline_* metrics, log file count per file group

□ Cleaning configured
  □ KEEP_LATEST_COMMITS with enough retention for time travel SLA
  □ Savepoints for any long-running analyses

□ Clustering (optional but recommended)
  □ Run weekly or when small files accumulate
  □ Sort by most common query filter columns

COW Tables:
□ Cleaning configured (same as MOR)
□ Clustering configured if small file problem exists
□ Monitor file size distribution (avoid files < 50MB)

All Tables:
□ Metadata table enabled (file listing + column stats)
□ Monitor storage growth (cleaning lag = storage bloat)
□ Alert on compaction lag > X commits for MOR
```
