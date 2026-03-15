# Performance Optimization for Data Lakes
## Chapter 5: Query Performance, Storage Optimization, Compute Tuning

---

## The Performance Problem in Data Lakes

Data lakes trade performance for flexibility. Object storage (S3/ADLS/GCS) has higher latency than local disk and no native indexing. Without careful design, queries that take seconds in a data warehouse can take hours on a data lake.

```
Root causes of poor data lake performance:
├── No pruning → full table scan on every query
├── Small files → too many tasks, driver overhead
├── Wrong file format → reading unnecessary columns/rows
├── Data skew → a few large tasks bottleneck the job
├── Under-resourced cluster → tasks queue instead of running
└── Missing statistics → query planner makes poor decisions
```

The good news: each of these is addressable with the right techniques.

---

## Storage-Layer Optimizations

Storage optimization is the highest-leverage performance work because it benefits every query, regardless of compute engine.

### File Format Selection

| Format | Layout | Best For | Key Advantage |
|--------|--------|----------|---------------|
| **Parquet** | Columnar | Analytics, BI, ML features | Column pruning; row group skipping |
| **ORC** | Columnar | Hive/Spark analytics | Similar to Parquet; better for Hive |
| **Avro** | Row | Streaming, serialization | Fast row-level writes; schema registry friendly |
| **CSV/JSON** | Row | Interoperability only | Human-readable; no query optimization |
| **Delta / Iceberg / Hudi** | Columnar + metadata | Lakehouse | All Parquet benefits + ACID + statistics |

**Rule**: Use Parquet (or an open table format on top of Parquet) for all analytics workloads. Never store analytics data as CSV or JSON.

### Columnar Format Internals (Why Parquet Is Fast)

```
Row-oriented (CSV):        Columnar (Parquet):
─────────────────          ──────────────────
Row 1: A, B, C, D          Column A: a1, a2, a3, a4
Row 2: A, B, C, D          Column B: b1, b2, b3, b4
Row 3: A, B, C, D          Column C: c1, c2, c3, c4
Row 4: A, B, C, D          Column D: d1, d2, d3, d4

SELECT A, B FROM table:
CSV: read all 4 columns     Parquet: read only A + B columns
     for every row               → 50% less I/O
```

**Row group skipping**: Parquet stores min/max statistics per row group (default 128MB). Query engines skip row groups where:
```
WHERE order_amount > 1000
→ Skip row groups where max(order_amount) < 1000
→ Often 90%+ of row groups skipped for selective filters
```

### Compression Codecs

| Codec | Speed | Ratio | Best For |
|-------|-------|-------|---------|
| **Snappy** | Fast | Moderate (~50%) | Parquet analytics (default recommendation) |
| **GZIP/Zlib** | Slow | High (~70%) | Archives where read latency is acceptable |
| **LZ4** | Very fast | Low (~30%) | Real-time / low-latency workloads |
| **ZSTD** | Fast | High (~65%) | Good balance; increasingly preferred |
| **Uncompressed** | N/A | None | Only for testing |

**Recommendation**: Use **Snappy** for curated zone (fast decompression = fast queries). Use **GZIP or ZSTD** for raw/archive zone (smaller storage = lower cost).

---

## Partitioning for Query Performance

Partitioning is covered in depth in `scalability.md`, but its performance impact warrants emphasis here.

### Partition Pruning in Practice

```sql
-- Table: fact_orders partitioned by year/month/day
-- Table size: 10TB

-- Without pruning (no partition filter):
SELECT SUM(amount) FROM fact_orders WHERE customer_id = 123;
-- Scans: 10TB → takes 20 minutes, costs $50 (Athena)

-- With partition pruning:
SELECT SUM(amount) FROM fact_orders
WHERE order_date = '2024-06-30' AND customer_id = 123;
-- Scans: 280MB (one day's partition) → takes 3 seconds, costs $0.001
```

### Z-Ordering / Clustering (Within Partitions)

When queries filter on columns that are NOT partition keys, Z-ordering can dramatically reduce scans within a partition:

**Z-ordering** (Delta Lake) / **Sorting** (Iceberg) / **Clustering** (BigQuery): co-locates rows with similar values of a column within files, enabling row group skipping.

```sql
-- Delta Lake: Z-order on customer_id within date partitions
OPTIMIZE fact_orders ZORDER BY (customer_id);

-- Apache Iceberg: Sort order at write time
CREATE TABLE fact_orders (...)
PARTITIONED BY (days(order_date))
WITH (sorted_by = ARRAY['customer_id']);
```

After Z-ordering, a filter on `customer_id = 123` can skip 90–99% of row groups within the date partition.

---

## Query Engine Optimizations

### Predicate Pushdown

The query engine pushes filter conditions down to the storage layer, which reads only matching row groups or files.

**How it works:**
1. Query planner sees `WHERE amount > 1000`
2. Reads Parquet min/max statistics for `amount` per row group
3. Skips row groups where `max(amount) <= 1000`
4. Only reads row groups that might contain matching rows

**Ensure predicate pushdown works:**
- Use supported filter expressions (equality, range, IN lists)
- Store statistics (Parquet writes them automatically; ensure not disabled)
- Use formats that expose statistics (Parquet, ORC — not CSV/JSON)

### Column Pruning

Query engines that support column pruning read only the columns referenced in the query.

```sql
-- Only reads 2 columns from a 50-column table:
SELECT customer_id, order_total FROM fact_orders WHERE order_date = '2024-06-30';
-- I/O reduction: 96% (2/50 columns)
```

**Ensure column pruning:**
- Use Parquet or ORC (columnar storage required)
- Reference only needed columns in SELECT; avoid `SELECT *`
- Consider physical column ordering — frequently queried columns first

### Join Optimization

Joins are the most expensive operation in distributed query engines.

| Join Type | When to Use | Mechanism |
|-----------|-------------|-----------|
| **Broadcast join** | Small table (<256MB) joined to large table | Small table broadcast to all executors; no shuffle |
| **Sort-merge join** | Large-to-large table joins | Both sides sorted and merged; expensive shuffle |
| **Bucket join** | Pre-bucketed tables on join key | Avoids shuffle entirely; requires setup |

**Broadcast join example (Spark):**
```python
from pyspark.sql.functions import broadcast

result = large_fact_df.join(
    broadcast(small_dim_df),
    "customer_id"
)
# Hint: small_dim_df is broadcast to all executors
# Result: no shuffle, very fast join
```

**Pre-bucketing for repeated joins:**
```sql
-- Write data bucketed by join key
CREATE TABLE fact_orders USING DELTA
CLUSTERED BY (customer_id) INTO 128 BUCKETS;

-- Subsequent joins on customer_id skip the shuffle
```

---

## Caching Strategies

### In-Memory Caching (Spark)

Cache frequently-accessed DataFrames to avoid repeated reads from object storage:

```python
# Cache a commonly joined dimension table
dim_customer = spark.read.format("iceberg").table("dim.customer")
dim_customer.cache()  # or .persist(StorageLevel.MEMORY_AND_DISK)
dim_customer.count()  # materialize the cache

# Subsequent uses of dim_customer read from cache, not S3
```

**When to cache:**
- Small-to-medium dimension tables used in multiple joins in the same job
- Reference data that changes infrequently
- DataFrames that result from expensive computations reused downstream

**When NOT to cache:**
- Data larger than available executor memory → spills to disk, degrades performance
- Data used only once → caching overhead exceeds benefit
- Streaming data → continuously changing

### Query Result Caching

| Engine | Caching Mechanism |
|--------|-----------------|
| **Amazon Athena** | Automatic result reuse (same query within 60 min) |
| **Google BigQuery** | BI Engine in-memory cache; query result cache (24 hours) |
| **Databricks** | Delta cache (local SSD caching of cloud storage data) |
| **Trino/Presto** | Result caching plugins; Alluxio data orchestration layer |

### Alluxio — Tiered Caching Layer

Alluxio sits between the compute engine and object storage, caching frequently-accessed data on local SSDs:

```
Compute (Spark/Presto) → Alluxio (local SSD cache) → S3/ADLS/GCS
                              ↑
                        Cache hit → 10–100x faster than S3 read
                        Cache miss → read from S3, populate cache
```

Effective for workloads with hot data accessed repeatedly (e.g., ML training iterations over the same dataset).

---

## Compute-Layer Optimizations

### Spark Executor Configuration

| Parameter | Recommendation | Rationale |
|-----------|---------------|-----------|
| `spark.executor.memory` | 4–8GB per core | Avoid GC pressure; leave headroom |
| `spark.executor.cores` | 4–5 per executor | Balance parallelism and memory sharing |
| `spark.sql.shuffle.partitions` | 2–3× cluster core count | Avoid shuffle bottlenecks |
| `spark.default.parallelism` | 2–3× cluster core count | Match available parallelism |

**Adaptive Query Execution (AQE)** — enable in Spark 3.x for automatic optimization:
```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

AQE automatically:
- Coalesces small shuffle partitions after joins
- Handles data skew by splitting large partitions
- Switches join strategies based on runtime size estimates

### Data Skew

Data skew occurs when one partition has far more data than others, causing one task to run while others are idle.

**Detection:**
```
Spark UI → Stage Details → Task Metrics
If max task duration >> median task duration → skew present
```

**Solutions:**

| Technique | When to Use |
|-----------|-------------|
| **Salting** | Skew on join key; add random salt to distribute |
| **AQE skew join** | Spark 3.x; automatic for most cases |
| **Repartition** | After filter that reduces data; repartition to even distribution |
| **Broadcast join** | When one side is small; eliminates shuffle entirely |

**Salting example:**
```python
from pyspark.sql.functions import concat, lit, (rand() * 10).cast("int")

# Add salt to both sides of the join
fact_with_salt = fact_df.withColumn("salt", (rand() * 10).cast("int"))
    .withColumn("customer_id_salted", concat("customer_id", lit("_"), "salt"))

dim_exploded = dim_df.crossJoin(spark.range(10).withColumnRenamed("id", "salt"))
    .withColumn("customer_id_salted", concat("customer_id", lit("_"), "salt"))

result = fact_with_salt.join(dim_exploded, "customer_id_salted")
```

### Autoscaling Compute

Don't run a large cluster when idle. Use autoscaling:

| Cloud | Autoscaling Option |
|-------|------------------|
| **AWS EMR** | EMR Managed Scaling (adds/removes nodes based on queue depth) |
| **Databricks** | Cluster autoscaling (min/max workers configured) |
| **Google Dataproc** | Autoscaling policies (YARN resource utilization) |
| **Serverless** | Athena, BigQuery — no cluster management; auto-scales |

**Spot/preemptible instances** for batch workloads:
- 60–90% cheaper than on-demand
- Risk: instances can be interrupted (design jobs to checkpoint and restart)
- Strategy: use on-demand for driver/master nodes; spot for workers

---

## Performance Monitoring

### Key Metrics to Track

| Metric | Threshold | Action If Exceeded |
|--------|-----------|-------------------|
| Query scan bytes | >10% of table size for filtered queries | Review partitioning and file stats |
| Task duration skew | Max task >3× median | Investigate data skew |
| Shuffle bytes | >10GB for typical queries | Review join strategy |
| File count per partition | >1,000 files | Run compaction |
| GC time % | >10% of executor time | Reduce executor memory pressure |
| S3 API error rate | >0.1% | Investigate throttling; add retries |

### Query Profiling Workflow

```
1. Identify slow query
   └── Spark UI → SQL tab → execution plan

2. Check partitioning
   └── Is partition pruning happening?
   └── How many files/bytes scanned?

3. Check statistics
   └── Are row group min/max stats present?
   └── Is the query planner using them?

4. Check skew
   └── Task duration distribution in Stage Details
   └── Is one task 10× slower than others?

5. Check join strategy
   └── Is a large shuffle happening that could be broadcast?

6. Tune and re-measure
   └── Change one thing at a time
   └── Compare scan bytes and wall-clock time
```
