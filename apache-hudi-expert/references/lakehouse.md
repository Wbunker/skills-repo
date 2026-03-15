# Building an End-to-End Lakehouse Solution
## Chapter 10: Medallion Architecture, Bronze/Silver/Gold/AI Layers, End-to-End Design

---

## The Medallion Architecture with Hudi

The medallion (multi-layer) architecture organizes a lakehouse into progressive data quality tiers. Hudi is well-suited to this pattern because its incremental query capability efficiently propagates changes from one layer to the next.

```
                    SOURCES
         ┌──────────────────────────┐
         │ Kafka │ RDBMS │ APIs │  │
         │ IoT   │ Files │ CDC  │  │
         └──────────────────────────┘
                      ↓
         ┌────────────────────────────┐
         │        BRONZE LAYER        │
         │  Raw ingestion, no transforms│
         │  Hudi MOR + Hudi Streamer   │
         │  Preserve all source data   │
         └────────────────────────────┘
                      ↓ Incremental reads
         ┌────────────────────────────┐
         │        SILVER LAYER        │
         │  Cleansed, joined, enriched │
         │  Hudi COW or MOR            │
         │  Validated, deduplicated    │
         └────────────────────────────┘
                      ↓ Incremental reads
         ┌────────────────────────────┐
         │         GOLD LAYER         │
         │  Business-level aggregates  │
         │  Hudi COW                   │
         │  Optimized for BI/reporting │
         └────────────────────────────┘
                      ↓
         ┌────────────────────────────┐
         │       BUSINESS/AI LAYER    │
         │  Feature stores, ML models │
         │  Dashboards, APIs           │
         └────────────────────────────┘
```

---

## Bronze Layer: Raw Ingestion

**Goal**: Land data from all sources with minimal transformation. Preserve the exact source record.

**Hudi Configuration:**

```python
# MOR for high-throughput streaming ingestion
hudi_bronze = {
    "hoodie.table.type": "MERGE_ON_READ",
    "hoodie.datasource.write.operation": "insert",  # or upsert if dedup needed
    "hoodie.parquet.max.file.size": "134217728",
    # Partition by ingestion date (not source date) for predictable file sizes
    "hoodie.datasource.write.partitionpath.field": "ingest_date",
}
```

**Ingestion patterns:**

```
Kafka → Hudi Streamer → Bronze MOR table
  Operation: INSERT (preserve all events, including duplicates)
  Partition: ingest_date (daily or hourly)
  Dedup: deferred to Silver layer

RDBMS → Debezium → Kafka → Hudi Streamer → Bronze MOR table
  Operation: UPSERT (apply CDC changes)
  Partition: updated_date
  Record key: source primary key
```

**Bronze best practices:**
- Retain source schema as-is; add only `_ingest_timestamp` and `_source_system` meta columns
- Never transform or filter — Bronze is the audit layer
- Partition by ingestion time, not source event time (more predictable file sizes)
- Set long retention (`hoodie.cleaner.commits.retained=100+`) for compliance/auditing
- Enable CDC logging for complete change history

---

## Silver Layer: Cleansed and Enriched

**Goal**: Clean, validated, joined, and deduplicated data ready for analytical use.

**Hudi Configuration:**

```python
# COW for most Silver tables (read-heavy analytics after ETL)
hudi_silver = {
    "hoodie.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.index.type": "RECORD_INDEX",             # global dedup across partitions
    # Partition by business date
    "hoodie.datasource.write.partitionpath.field": "event_date",
    "hoodie.metadata.index.column.stats.enable": "true",
}
```

**Silver processing pattern (Spark batch or streaming):**

```python
# Read incrementally from Bronze
bronze_df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.read.begin.instanttime", last_checkpoint) \
    .load("s3://lake/bronze/orders/")

# Transform
silver_df = bronze_df \
    .filter(col("amount") > 0) \
    .dropDuplicates(["order_id"]) \
    .join(customers_df, "customer_id", "left") \
    .withColumn("event_date", to_date(col("event_timestamp")))

# Write to Silver
silver_df.write.format("hudi") \
    .options(**hudi_silver) \
    .mode("append") \
    .save("s3://lake/silver/orders/")

# Save checkpoint
save_checkpoint(spark.read.format("hudi").load("s3://lake/silver/orders/") \
    .select(max("_hoodie_commit_time")).first()[0])
```

**Silver transformations:**
- Deduplication by record key
- Data type casting and validation
- Schema standardization (rename columns, normalize values)
- Enrichment joins (e.g., add customer_name from customers table)
- SCD (Slowly Changing Dimension) management for reference tables

---

## Gold Layer: Business Aggregates

**Goal**: Pre-computed aggregates and business metrics ready for BI tools and dashboards.

**Hudi Configuration:**

```python
# COW optimized for read performance
hudi_gold = {
    "hoodie.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.operation": "upsert",
    # Clustering for optimal read layout
    "hoodie.clustering.inline": "true",
    "hoodie.clustering.plan.strategy.sort.columns": "region,product_category",
    "hoodie.metadata.index.column.stats.enable": "true",
}
```

**Gold layer examples:**

```sql
-- Daily revenue by region and category
SELECT
    order_date,
    region,
    product_category,
    SUM(amount) AS total_revenue,
    COUNT(*) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM silver.orders
WHERE order_date >= date_sub(current_date(), 90)
GROUP BY order_date, region, product_category;
-- → Write result as Hudi table: gold.daily_revenue
```

**Gold layer patterns:**
- Aggregated at the grain needed by BI consumers (not over-aggregated)
- Refreshed incrementally from Silver using Hudi incremental reads
- Registered in Glue/HMS for direct Athena/Trino/Redshift Spectrum access
- Clustering on most common filter dimensions (region, date, category)
- Smaller retention (fewer historical versions needed)

---

## Business/AI Layer

**Goal**: Serve ML features, dashboards, APIs, and data products.

### Feature Store Integration

```python
# Read from Gold as features
features_df = spark.read.format("hudi").load("s3://lake/gold/customer_features/")

# Write to feature store (e.g., Feast, Tecton, SageMaker Feature Store)
# Or maintain a Hudi table as the feature store backing store:
hudi_features = {
    "hoodie.table.type": "COPY_ON_WRITE",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.index.type": "RECORD_INDEX",        # point lookup by entity ID
    "hoodie.metadata.record.index.enable": "true",
}
features_df.write.format("hudi").options(**hudi_features).mode("append").save("s3://lake/features/")
```

### Serving Online Lookups

Hudi tables can serve low-latency point lookups via:
- DynamoDB sync (replicate Hudi records to DynamoDB for online serving)
- Flink streaming read → Redis/DynamoDB pipeline
- Query via Athena (lower throughput, acceptable for batch serving)

---

## End-to-End Pipeline: Complete Example

```
Orders CDC from PostgreSQL
         ↓
Debezium → Kafka topic: order-cdc-events
         ↓
Hudi Streamer (continuous)
  Source: PostgresDebeziumSource
  Operation: UPSERT
  Table: Bronze MOR (s3://lake/bronze/orders/)
  Partition: ingest_date
         ↓ Incremental reads (every 15 min, Airflow)
Spark Silver Job
  Read: incremental from Bronze
  Transform: dedup, validate, join customers
  Write: Silver COW (s3://lake/silver/orders/)
         ↓ Incremental reads (every hour, Airflow)
Spark Gold Job
  Read: incremental from Silver
  Aggregate: daily revenue by region/category
  Write: Gold COW (s3://lake/gold/daily_revenue/)
         ↓
Athena / Trino / Redshift Spectrum
  Registered in Glue Catalog
  Queried by Tableau / QuickSight / Superset
         ↓
SageMaker
  Reads Gold features for model training
  Writes predictions back to Hudi predictions table
```

---

## Architecture Decision Points

### When to Use Hudi for Each Layer

| Layer | Hudi Table Type | Write Operation | Index | Sync |
|-------|----------------|----------------|-------|------|
| Bronze | MOR | INSERT/UPSERT | Bloom (partition-local) | Optional |
| Silver | COW | UPSERT | Record-Level (global dedup) | HMS/Glue |
| Gold | COW | UPSERT | Bloom or Record-Level | HMS/Glue |
| Features | COW | UPSERT | Record-Level (point lookup) | HMS/Glue |

### Incremental Processing Strategy

```
Option A: Micro-batch (recommended for most use cases)
  Airflow DAG runs every 15-60 min
  Each run: read incremental from upstream, write to downstream
  Checkpoint: last processed Hudi commit time
  Latency: 15-60 min end-to-end

Option B: Continuous streaming
  Spark Structured Streaming or Flink
  Hudi as source (streaming read) + sink (streaming write)
  Latency: seconds to minutes
  Complexity: higher (stream management, state, backpressure)

Option C: Daily batch
  Simple Spark job, processes yesterday's partition
  No checkpointing complexity
  Latency: 1 day (acceptable for Gold/reporting)
```

### Multi-Tenant Lakehouse

For organizations with multiple teams writing to shared Hudi tables:

```python
# Separate namespaces per team
s3://lake/bronze/team-payments/orders/
s3://lake/bronze/team-logistics/shipments/

# Shared Silver with access controls
s3://lake/silver/orders/          ← written by platform team

# IAM policies control who can write to each path
# Catalog-level permissions via Lake Formation or Ranger
```

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Writing raw + transformed in one job to same table | Mixing concerns, hard to replay | Separate Bronze and Silver tables |
| Full table reads instead of incremental | Scales poorly as Bronze grows | Use `hoodie.datasource.query.type=incremental` |
| Over-partitioning Gold layer | Thousands of tiny partitions, slow queries | Coarser partitions (monthly vs daily) in Gold |
| Running compaction inline on MOR in streaming job | Blocks streaming throughput | Async compaction with separate Spark job |
| Single large table for all events | All teams blocked by one table's SLAs | Separate tables per domain; federate at query layer |
| Skipping Bronze layer | No audit trail, no replay capability | Always land raw data first |
