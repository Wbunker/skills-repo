# Scalable Data Lakes
## Chapter 4: Strategies for Scale While Optimizing for Cost

---

## The Scalability Challenge

Cloud object storage scales infinitely — but the **ecosystem around it** does not automatically scale well. As data lakes grow from gigabytes to petabytes, several problems emerge:

```
Symptoms of a data lake that hasn't scaled its design:
├── Queries take hours instead of minutes
├── Small file proliferation → millions of tiny files
├── Partition directories with 100K+ objects
├── Compaction jobs overwhelm compute clusters
├── Cost per query increases with data volume
└── Schema changes break downstream jobs
```

Scaling a data lake requires deliberate design of partitioning, file sizing, compaction, and data organization — not just adding more storage.

---

## The Small File Problem

### What It Is

Small files are the #1 scalability killer in data lakes. They arise when:
- Streaming pipelines write one file per micro-batch (every 30 seconds = 2,880 files/day)
- CDC tools write individual record updates as small files
- Failed jobs create partial, tiny files
- Poor partitioning schemes create many low-cardinality partition directories

### Why Small Files Are Harmful

| Impact | Cause |
|--------|-------|
| **Slow query planning** | Query engine must open and read metadata for each file |
| **High API costs** | Each S3 GET request costs money; millions of files = millions of requests |
| **Driver memory pressure** | Spark driver tracks one task per file; millions of files exhaust driver memory |
| **Poor read parallelism** | Spark assigns one task per file; tiny files waste executor slots |
| **Slow listing** | S3 LIST operations on directories with 100K+ objects are slow |

### The Target File Size

| Engine | Target File Size | Rationale |
|--------|-----------------|-----------|
| Spark batch | 128MB – 1GB | Optimal Parquet row group / task granularity |
| Athena / Presto | 128MB – 512MB | Query planning overhead per file |
| Streaming landing | 32MB – 128MB | Accept small; compact immediately after |

Files smaller than ~32MB are generally harmful. Files larger than ~2GB reduce parallelism.

---

## Partitioning Strategies

Partitioning is the most important design decision for query performance and cost at scale. A partition tells the query engine: "all data for predicate X is in this directory — skip everything else."

### Partitioning Fundamentals

```
Unpartitioned table:
s3://lake/fact_orders/
  part-00000.parquet  (100GB, all data)

→ Any query scans 100GB

Partitioned by date:
s3://lake/fact_orders/
  year=2024/month=06/day=30/part-00000.parquet  (280MB)
  year=2024/month=06/day=29/part-00000.parquet  (275MB)
  ...

→ Query WHERE order_date = '2024-06-30' scans only 280MB
```

### Choosing the Right Partition Column(s)

**Good partition columns:**
- Columns frequently used in WHERE clauses by consumers
- Low-to-medium cardinality (days, months, regions, status codes — not user IDs)
- Time-based columns for time-series data (almost always partition by date/time)

**Bad partition columns:**
- High cardinality (user_id, transaction_id) — creates millions of partitions, each nearly empty
- Columns never queried as filters
- Boolean columns (only 2 values → 2 partitions, no selectivity benefit)

### Common Partition Schemes

| Data Type | Recommended Partition | Example |
|-----------|----------------------|---------|
| Event/transaction data | `year` + `month` + `day` | `year=2024/month=06/day=30/` |
| High-volume streaming | `year` + `month` + `day` + `hour` | `year=2024/month=06/day=30/hour=14/` |
| Regional data | `region` + `date` | `region=us-east-1/date=2024-06-30/` |
| Domain-partitioned | `domain` + `date` | `domain=sales/date=2024-06-30/` |
| Slowly-changing dims | `snapshot_date` | `snapshot_date=2024-06-30/` |

### Partition Evolution with Open Table Formats

With Hive-style partitioning on raw object storage, changing the partition scheme requires rewriting all data. Open table formats solve this:

- **Apache Iceberg**: Hidden partitioning — partition scheme is stored in metadata; can be changed without rewriting data. Partition evolution is a metadata-only operation.
- **Delta Lake**: Supports partition changes but requires `REPLACE TABLE` for scheme changes.
- **Apache Hudi**: Partition evolution supported in newer versions.

---

## File Compaction

Compaction is the process of merging many small files into fewer, larger, optimally-sized files. It is essential maintenance for data lakes receiving frequent small writes.

### When to Compact

| Trigger | Description |
|---------|-------------|
| **Time-based** | Nightly compaction job on previous day's data |
| **File count threshold** | Compact when a partition has >N files |
| **File size threshold** | Compact when average file size drops below X MB |
| **Post-streaming** | Compact immediately after streaming micro-batches are sealed |

### Compaction Approaches

**Manual (without table format):**
```python
# Spark: read many small files, write as fewer large files
df = spark.read.parquet("s3://lake/staging/orders/date=2024-06-30/")
df.coalesce(4).write.mode("overwrite").parquet("s3://lake/staging/orders/date=2024-06-30/")
```

**Automatic (with open table formats):**
- **Apache Iceberg**: `OPTIMIZE` command (Spark/Trino) rewrites small files; metadata updated atomically
- **Delta Lake**: `OPTIMIZE` command; `AUTO OPTIMIZE` for automated background compaction (Databricks)
- **Apache Hudi**: Built-in compaction as part of the write path (async or synchronous)

### Compaction Best Practices

1. **Run compaction after streaming, before batch consumers query**
2. **Don't compact actively-written partitions** — creates conflicts with concurrent writers
3. **Compact by partition** — don't compact the entire table at once; parallelize per partition
4. **Combine compaction with `VACUUM`/`EXPIRE_SNAPSHOTS`** — remove obsolete files after compaction
5. **Monitor file count** — set alerts when partition file counts exceed threshold

---

## Scaling Data Ingestion

### Batch Ingestion Scaling

| Problem | Solution |
|---------|---------|
| Source query takes too long | Partition extraction by date range; parallel extraction |
| Single-threaded ingestion | Parallelize with Spark distributed reads |
| Large files from source → bad partition sizes | Repartition during write |
| Historical backfill takes days | Backfill in parallel by date range partitions |

**Spark partitioned extraction pattern:**
```python
# Extract from JDBC in parallel by partition column
df = (spark.read.format("jdbc")
  .option("url", jdbc_url)
  .option("dbtable", "orders")
  .option("partitionColumn", "order_date")
  .option("lowerBound", "2020-01-01")
  .option("upperBound", "2024-12-31")
  .option("numPartitions", 96)  # parallel reads
  .load())
```

### Streaming Ingestion Scaling

Streaming workloads (Kafka → lake) face unique challenges:

| Challenge | Solution |
|-----------|---------|
| Small files per micro-batch | Write to staging with small files; compact to curated |
| Schema changes in stream | Schema registry (Confluent) + Iceberg schema evolution |
| Out-of-order late arrivals | Watermarking in Spark Structured Streaming / Flink |
| Exactly-once delivery | Kafka transactions + Iceberg/Delta atomic commits |

### CDC (Change Data Capture) Scaling

CDC streams changes (inserts, updates, deletes) from operational databases to the lake:

```
Operational DB (MySQL/Postgres/Oracle)
         │
    [Debezium CDC]
         │
    Kafka topics (change events)
         │
    [Spark/Flink consumer]
         │
    Apache Hudi / Iceberg MOR table
    (Merge-on-Read: efficient upserts)
```

**Merge-on-Read (MOR)** tables are essential for CDC at scale:
- Writes are fast: append change deltas to log files
- Reads merge base files + delta logs on the fly
- Periodic compaction consolidates into clean base files

---

## Data Organization at Scale

### Managing a Large Table Catalog

As data lakes grow, catalog management becomes critical:

| Problem | Solution |
|---------|---------|
| Thousands of tables, hard to find | Domain-based naming conventions; catalog with search |
| Stale/abandoned tables | Regular catalog audits; table age + last-access metadata |
| Conflicting table names | Namespace hierarchy (domain.subdomain.table) |
| Unknown owners | Ownership metadata required at table creation |

### Handling Schema Evolution at Scale

As data formats change upstream, the lake must accommodate without breaking consumers:

| Change Type | Safe? | How to Handle |
|------------|-------|--------------|
| Add new column | Safe | Iceberg/Delta/Hudi support backward-compatible column additions |
| Rename column | Breaking | Add new column; keep old; deprecate with warning |
| Change data type | Breaking | New column with new type; migration job |
| Remove column | Breaking | Soft-delete (null + deprecation notice); hard delete after consumers migrate |
| Change partitioning | Breaking (raw) | Iceberg partition evolution; or create new table version |

### Scaling Governance

Governance practices that work for 10 tables break at 10,000. Scale governance by:

1. **Automated classification** — tag data at ingestion using ML-based classifiers or regex patterns
2. **Policy inheritance** — a zone-level policy applies to all tables in that zone unless overridden
3. **Stewardship at the domain level** — one steward per domain, not per table
4. **Quality checks in pipelines** — shift quality left; catch issues before data reaches curated zone
5. **Usage-based curation** — prioritize documentation for the 20% of tables that get 80% of queries

---

## Cost Optimization at Scale

### The Storage Cost Curve

As data volumes grow, storage optimization becomes the dominant lever:

```
At 10TB:   Storage ~$230/month → optimize compute first
At 1PB:    Storage ~$23,000/month → optimize storage aggressively
At 10PB:   Storage ~$230,000/month → tiering and lifecycle policies are critical
```

### Tiering Strategy at Scale

| Zone | Hot Tier Duration | Warm Tier | Cold Tier |
|------|-----------------|-----------|-----------|
| Raw/Landing | 7 days | 30 days (IA) | 90+ days (Glacier) |
| Staging | 30 days | 90 days (IA) | 1 year (Glacier) |
| Curated | 1 year | 3 years (IA) | Archive |

### Query Cost Optimization at Scale

With query engines that charge per byte scanned (Athena: $5/TB):

| Optimization | Bytes Scanned Reduction |
|-------------|------------------------|
| Parquet vs. CSV | 87% reduction (columnar reads only needed columns) |
| Snappy compression | 70% size reduction |
| Date partitioning | 99% reduction for time-bounded queries |
| Predicate pushdown | Skips unnecessary row groups |
| Materialized views | Pre-aggregate common queries |

The combination of Parquet + compression + good partitioning can reduce query costs by 95–99% versus scanning raw CSV data.
