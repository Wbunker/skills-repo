# Running Hudi in Production
## Chapter 8: CLI, Catalog Sync, Monitoring, Callbacks, Performance Tuning

---

## Hudi CLI

The Hudi CLI is an interactive shell for table inspection and management.

```bash
# Launch CLI
bin/hudi-cli.sh

# Connect to a table
hoodie-cli> connect --path s3://bucket/orders/
```

### Common CLI Commands

```bash
# Table info
hoodie-cli> desc

# Show timeline (recent commits)
hoodie-cli> commits show --limit 20

# Show file group details
hoodie-cli> stats filesizes --partitionPath 2024/01/15

# Show compaction plans
hoodie-cli> compactions show all

# Trigger compaction
hoodie-cli> compaction run --parallelism 100 --sparkMaster yarn

# Show clustering plans
hoodie-cli> clusteringplans show

# Run clustering
hoodie-cli> clustering run

# Validate data integrity
hoodie-cli> validate all

# Show record count and size per partition
hoodie-cli> stats wa

# Repair corrupted timeline
hoodie-cli> repair corrupted timeline
```

---

## Catalog Sync

Hudi tables must be registered in a query engine's metastore to be queryable via SQL.

### Hive Metastore Sync

```python
# Enable HMS sync during write
hudi_options = {
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "hms",
    "hoodie.datasource.hive_sync.metastore.uris": "thrift://hive-metastore:9083",
    "hoodie.datasource.hive_sync.database": "hudi_db",
    "hoodie.datasource.hive_sync.table": "orders",
    "hoodie.datasource.hive_sync.partition_fields": "order_date",
    "hoodie.datasource.hive_sync.partition_extractor_class":
        "org.apache.hudi.hive.MultiPartKeysValueExtractor",
    "hoodie.datasource.hive_sync.use_jdbc": "false",
}
```

For MOR tables, Hudi registers **two tables** in HMS:
- `orders` — snapshot view (base + logs merged)
- `orders_ro` — read-optimized view (base files only)

### AWS Glue Catalog Sync

```python
hudi_options = {
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "glue",
    "hoodie.datasource.hive_sync.database": "hudi_db",
    "hoodie.datasource.hive_sync.table": "orders",
    "hoodie.datasource.hive_sync.partition_fields": "order_date",
    "hoodie.datasource.hive_sync.partition_extractor_class":
        "org.apache.hudi.hive.MultiPartKeysValueExtractor",
}
```

Glue sync creates/updates the Glue table definition after each successful commit.

### REST Catalog Sync (Iceberg REST)

For polyglot lakehouse environments using the Iceberg REST Catalog spec:

```python
hudi_options = {
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "jdbc",  # or custom REST sync class
}
```

### Standalone Sync Tool

Run sync independently (useful after bulk operations or repairs):

```bash
spark-submit \
  --class org.apache.hudi.hive.HiveSyncTool \
  hudi-hive-sync-bundle.jar \
  --base-path s3://bucket/orders/ \
  --database hudi_db \
  --table orders \
  --partitioned-by order_date \
  --sync-mode glue
```

---

## Monitoring

### Key Metrics (Prometheus / Graphite)

Hudi emits JMX/Prometheus metrics. Enable:

```python
"hoodie.metrics.on": "true",
"hoodie.metrics.reporter.type": "PROMETHEUS_PUSHGATEWAY",
"hoodie.metrics.pushgateway.host": "pushgateway-host",
"hoodie.metrics.pushgateway.port": "9091",
"hoodie.metrics.pushgateway.job.name": "hudi-orders",
```

#### Write Metrics

| Metric | Description | Alert When |
|--------|-------------|-----------|
| `hoodie.commit.duration_ms` | Time for each commit | Growing trend |
| `hoodie.write.records.written` | Records per commit | Drops to 0 unexpectedly |
| `hoodie.write.bytes.written` | Bytes written per commit | Capacity planning |
| `hoodie.index.lookup.duration_ms` | Index lookup latency | Growing (index degradation) |
| `hoodie.upsert.partitions.written` | Partitions written per commit | Unexpected spikes |

#### Table Service Metrics

| Metric | Description |
|--------|-------------|
| `hoodie.compaction.duration_ms` | Compaction job duration |
| `hoodie.compaction.records.processed` | Records compacted |
| `hoodie.clustering.duration_ms` | Clustering job duration |
| `hoodie.clean.duration_ms` | Cleaning job duration |
| `hoodie.clean.files_deleted` | Files removed per clean |

#### Health Indicators

```python
# Monitor via CLI or metrics:
# 1. Log file count per file group (MOR)
#    → Should decrease after compaction; growing = compaction lag
# 2. Pending compaction instants count
#    → Should stay near 0; growing = compaction not keeping up
# 3. File count per partition
#    → Should stay within target range; explosion = small file problem
# 4. Commit latency trend
#    → Growing = index degradation, table size increase, resource contention
```

### Spark UI / History Server

Key Spark metrics to monitor per Hudi job:

- **Shuffle bytes**: large shuffles indicate upsert parallelism mismatch
- **GC time**: high GC = executor memory too small
- **Executor OOM**: increase `spark.executor.memory` or reduce parallelism
- **Stage duration**: compaction stages should dominate (not index lookup)

---

## Post-Commit Callbacks

Hudi can trigger HTTP callbacks or Kafka messages after each successful commit — useful for downstream notifications, catalog updates, or triggering dependent jobs.

### HTTP Callback

```python
"hoodie.write.commit.callback.on": "true",
"hoodie.write.commit.callback.http.url": "http://my-orchestrator/hudi-event",
"hoodie.write.commit.callback.http.timeout.seconds": "3",
```

Callback payload includes:
```json
{
  "tableName": "orders",
  "basePath": "s3://bucket/orders/",
  "commitTime": "20240115120000000",
  "totalRecordsWritten": 450000,
  "totalBytesWritten": 134217728,
  "commitType": "COMMIT"
}
```

### Kafka Callback

```python
"hoodie.write.commit.callback.on": "true",
"hoodie.write.commit.callback.class": "org.apache.hudi.callback.impl.HoodieWriteCommitKafkaCallback",
"hoodie.write.commit.callback.kafka.bootstrap.servers": "kafka-broker:9092",
"hoodie.write.commit.callback.kafka.topic": "hudi-commit-events",
```

---

## Performance Tuning

### Table Type Selection

```
High write throughput, near-real-time ingestion, CDC sources → MOR
  → Fast writes (log append), compact periodically

Low write frequency, read-heavy analytics → COW
  → No compaction overhead, pure Parquet reads
```

### File Sizing

Target file sizes depend on storage system:

| Storage | Target Size | Config |
|---------|------------|--------|
| S3/GCS/ADLS | 128MB–256MB | `hoodie.parquet.max.file.size=134217728` |
| HDFS | 512MB–1GB | `hoodie.parquet.max.file.size=536870912` |
| MOR base files | 128MB | Keep smaller to limit compaction I/O |

Small file auto-merge threshold:
```python
"hoodie.parquet.small.file.limit": "104857600",  # 100MB — route inserts to files below this
```

### Partitioning Best Practices

- **Partition granularity**: avoid over-partitioning (daily is usually fine; hourly can create too many small files)
- **Partition skew**: if one partition gets 90% of writes, all file groups in that partition become a bottleneck
- **Date-based partitioning**: most writes to latest partition — enable clustering for older partitions

### Write Performance Tuning

```python
# Parallelism — tune to (number of partitions written × cores per executor)
"hoodie.upsert.shuffle.parallelism": "400",
"hoodie.insert.shuffle.parallelism": "400",
"hoodie.bulkinsert.shuffle.parallelism": "400",

# Reduce index lookup cost
"hoodie.bloom.index.parallelism": "200",         # Bloom filter lookup parallelism
"hoodie.metadata.enable": "true",                # Use metadata table for fast file listing

# Tune record caching (avoids re-reading same records)
"hoodie.write.status.storage.level": "MEMORY_AND_DISK_SER",

# Disable unnecessary features for bulk loads
"hoodie.populate.meta.fields": "false",          # skip _hoodie_* meta columns (bulk insert only)
```

### Read Performance Tuning

```python
# Enable column statistics in metadata table for data skipping
"hoodie.metadata.index.column.stats.enable": "true",
"hoodie.metadata.index.column.stats.column.list": "customer_id,order_date,amount",

# Enable Bloom filter in metadata (avoid Parquet footer reads)
"hoodie.metadata.index.bloom.filter.enable": "true",

# MOR: tune merge buffer
"hoodie.compaction.lazy.block.read.enabled": "true",   # lazy reads during compaction
```

### Table Services Tuning

**Compaction:**
```python
# Run after every 5 deltacommits OR when log file size exceeds 1GB
"hoodie.compact.inline.max.delta.commits": "5",
"hoodie.compaction.logfile.size.threshold": "1073741824",

# Parallelism for compaction Spark job
"hoodie.compaction.target.io": "500000000000",    # 500GB I/O budget per run
```

**Clustering:**
```python
"hoodie.clustering.plan.strategy.target.file.max.bytes": "134217728",  # 128MB
"hoodie.clustering.plan.strategy.small.file.limit": "104857600",       # cluster files < 100MB
"hoodie.clustering.plan.strategy.max.num.groups": "30",                # groups per clustering plan
```

**Cleaning:**
```python
"hoodie.cleaner.commits.retained": "20",    # enough for time travel window
"hoodie.cleaner.policy.failed.writes": "LAZY_ROLLBACK",  # rollback failed writes during clean
```

### Engine-Specific Tuning

**Spark:**
```properties
spark.executor.memory=8g
spark.executor.cores=4
spark.executor.instances=20
spark.sql.shuffle.partitions=400
spark.serializer=org.apache.spark.serializer.KryoSerializer
spark.sql.hive.convertMetastoreParquet=false   # prevent Spark from bypassing Hudi reader
```

**Flink:**
```properties
taskmanager.memory.process.size: 8g
taskmanager.numberOfTaskSlots: 4
parallelism.default: 16
state.backend: rocksdb                         # for large state (compaction, clustering)
```

---

## Common Production Issues

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Commit latency growing | Index lookup too slow; table too large | Switch from Bloom to Record-Level index; increase parallelism |
| MOR reads slow | Compaction lagging; too many log files | Increase compaction frequency or resources |
| Small files everywhere | Parallelism too high for data volume | Reduce shuffle parallelism; enable clustering |
| OOM during write | Executor memory too small; parallelism mismatch | Increase executor memory; reduce parallelism |
| `FileNotFoundException` in queries | Cleaner deleted files before query finished | Increase `hoodie.cleaner.commits.retained`; add savepoints |
| Compaction never finishes | Too much data to compact in one run | Use `BoundedIOCompactionStrategy` to limit per run |
| Duplicate records after failure | Retry wrote without idempotency | Ensure `hoodie.write.concurrency.mode=SINGLE_WRITER`; use consistent job IDs |
