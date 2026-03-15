# Lakehouse Architecture — Chapter 9

Lakehouse design principles, the Medallion Architecture, and the Delta Sharing protocol.

## Table of Contents

- [The Lakehouse Concept](#the-lakehouse-concept)
- [Medallion Architecture](#medallion-architecture)
- [Delta Sharing Protocol](#delta-sharing-protocol)

---

## The Lakehouse Concept

A lakehouse combines the best of data warehouses (ACID, schema enforcement, governance) with data lakes (open formats, low-cost storage, ML/DS workloads):

```
Data Warehouse:  Structured + ACID + fast SQL  → but: proprietary, expensive, siloed
Data Lake:       Open formats + cheap storage   → but: no ACID, schema chaos, swamp risk
Lakehouse:       Open formats + ACID + governance + fast SQL + ML
```

Delta Lake enables the lakehouse by adding a transaction layer to cloud object storage. Key principles:
- **Open standards**: Parquet data, JSON/Parquet log — no vendor lock-in
- **Single copy of data**: One table serves BI, ML, streaming, and API workloads
- **Schema enforcement**: Prevents the "data swamp" problem
- **ACID transactions**: Prevents corrupt or partial reads
- **Governance built in**: Row/column-level security, audit trails, lineage

## Medallion Architecture

The canonical data organization pattern for lakehouses. Data flows through three tiers with increasing quality:

```
Sources           Bronze              Silver              Gold
─────────    ────────────────    ────────────────    ────────────────
Kafka     →  Raw events        → Cleaned events   → Daily aggregates
  APIs    →  (append-only)     → (deduplicated)   → (dimensional models)
  Files   →  (schema enforced) → (conformed types)→ (business metrics)
  CDC     →                    → (joined/enriched)→
```

### Bronze (Raw)

- **Purpose**: Land data exactly as received from sources
- **Operations**: Append-only ingestion, minimal transformation
- **Schema**: Enforce source schema (reject malformed records or rescue to `_rescued_data`)
- **Retention**: Long (months/years) — serves as audit trail and reprocessing source
- **Features**: Auto Loader for file ingestion, Kafka connector for streaming, schema enforcement

```python
# Bronze: ingest raw JSON files
spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/schemas/events") \
    .load("/landing/events/") \
    .writeStream.format("delta") \
    .option("checkpointLocation", "/checkpoints/bronze_events") \
    .start("/bronze/events")
```

### Silver (Cleaned)

- **Purpose**: Cleaned, conformed, enterprise-wide datasets
- **Operations**: Deduplication, type casting, null handling, joins, data quality checks
- **Schema**: Evolved schema with standardized types and naming
- **Features**: MERGE for upserts, Change Data Feed for incremental processing, expectations/constraints

```python
# Silver: deduplicate and clean
spark.readStream.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", "latest") \
    .table("bronze_events") \
    .filter(col("_change_type").isin("insert", "update_postimage")) \
    .withColumn("event_date", col("timestamp").cast("date")) \
    .dropDuplicates(["event_id"]) \
    .writeStream.format("delta") \
    .option("checkpointLocation", "/checkpoints/silver_events") \
    .trigger(availableNow=True) \
    .toTable("silver_events")
```

### Gold (Business)

- **Purpose**: Business-level aggregates, metrics, dimensional models optimized for consumption
- **Operations**: Aggregations, window functions, dimensional modeling (star schema)
- **Optimization**: Liquid clustering or Z-ordering on common query columns
- **Features**: Materialized views, OPTIMIZE for BI query performance

```sql
-- Gold: daily event aggregates
CREATE OR REPLACE TABLE gold_daily_events
USING DELTA
CLUSTER BY (event_date)
AS
SELECT
  event_date,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM silver_events
GROUP BY event_date, event_type;
```

### Cross-layer patterns

| Pattern | How |
|---------|-----|
| Incremental processing | CDF from bronze → silver, CDF from silver → gold |
| Full refresh | Overwrite gold tables on schedule |
| Backfill | Reprocess bronze from specific version, propagate through silver → gold |
| Data quality | CHECK constraints on silver, DLT expectations, `_rescued_data` in bronze |

## Delta Sharing Protocol

An open protocol for secure cross-organization data sharing without copying data.

### Architecture

```
Data Provider                    Data Recipient
─────────────                    ──────────────
Delta table on cloud storage  →  Sharing Server (REST API)  →  Client (Pandas, Spark, Power BI)
                                 ├── Shares
                                 ├── Schemas
                                 └── Tables
```

### Provider setup

```sql
-- Create a share
CREATE SHARE customer_share;

-- Add tables to the share
ALTER SHARE customer_share ADD TABLE gold_customers;
ALTER SHARE customer_share ADD TABLE gold_orders;

-- Create a recipient
CREATE RECIPIENT partner_org;

-- Grant access
GRANT SELECT ON SHARE customer_share TO RECIPIENT partner_org;
```

### Recipient access

```python
# Python client
import delta_sharing

profile = "config.share"  # contains endpoint + token
client = delta_sharing.SharingClient(profile)

# List shares
shares = client.list_shares()

# Read as Pandas
df = delta_sharing.load_as_pandas(f"{profile}#my_share.default.customers")

# Read as Spark
df = delta_sharing.load_as_spark(f"{profile}#my_share.default.customers")
```

### Key properties

- **No data copying**: Recipients read directly from provider's storage via pre-signed URLs
- **Token-based auth**: Recipients authenticate with bearer tokens
- **Live data**: Recipients always see the latest version of shared tables
- **Streaming support**: Recipients can consume shares as streaming sources
- **Audit**: Providers can track who accesses what and when
