# BigQuery — Capabilities

## Purpose

Fully managed, serverless, multi-petabyte data warehouse and analytics engine. Google's flagship data product. Separates compute (slots) from storage (Capacitor columnar format), enabling independent scaling. Natively integrates with the broader GCP data ecosystem and supports cross-cloud analytics via BigQuery Omni.

---

## Core Concepts

| Concept | Description |
|---|---|
| Project | Billing and IAM boundary for BigQuery resources |
| Dataset | Container for tables/views; has region, labels, default table expiration, access controls |
| Table | Native table, external table, materialized view, snapshot, or clone |
| View | Logical SQL view; no data storage; can be authorized views (cross-dataset security) |
| Column | Field with type; supports nested STRUCT and repeated ARRAY types |
| Partition | Table divided by column or ingestion time; enables partition pruning to reduce bytes scanned |
| Cluster | Physical sort order within partition (up to 4 columns); improves filter/aggregation performance |
| Job | Unit of work: query, load, export, or copy; asynchronous; tracked by job ID |
| Slot | Virtual CPU for query execution; on-demand and reservation-based allocation |
| Reservation | Dedicated slot capacity assigned to projects/folders via assignments |
| Edition | Standard, Enterprise, Enterprise Plus — differentiate by slot flexibility, BI Engine, CMEK, multi-region |
| Storage (active) | Data modified in past 90 days; standard storage pricing |
| Storage (long-term) | Data unmodified for 90+ days; ~50% cost reduction applied automatically |
| Row-level security | Row access policies filtering rows based on user/group identity |
| Column-level security | Policy tags via Data Catalog; column masking and fine-grained access |
| Data Masking | Masking rules on policy-tagged columns (nullify, default value, SHA256, email mask) |

---

## Storage Formats

- **Native storage**: Capacitor (proprietary columnar format); highly compressed; optimized for analytical scans
- **External table formats**: ORC, Parquet, Avro, CSV, JSON (newline-delimited), Google Sheets
- **BigLake**: unified storage layer for external tables across Cloud Storage, Amazon S3, Azure Blob; enforces BigQuery IAM and column-level security on files stored outside BigQuery; uses Storage Read API
- **Table snapshots**: point-in-time read-only copies; low cost (delta storage); useful for backup before DDL operations
- **Table clones**: writable copies backed by delta storage; full table if diverged significantly

---

## Partitioning and Clustering

**Partitioning strategies:**

| Type | Partition Column | Notes |
|---|---|---|
| Ingestion-time | `_PARTITIONTIME` (pseudo-column) | Auto-assigned on load/insert |
| DATE/TIMESTAMP column | User-defined DATE or TIMESTAMP column | Most common; requires column in WHERE for pruning |
| INTEGER range | User-defined INTEGER column | Define start, end, interval |

**Clustering:**
- Up to 4 columns; specified at table creation or via DDL
- Columns ordered by selectivity (highest cardinality first recommended)
- BigQuery automatically re-clusters tables in the background (automatic reclustering)
- Benefits: reduces bytes scanned for filter/aggregation queries; speeds sorts and joins

**Best practice**: partition first on date/time column, then cluster on high-cardinality filter columns. Use `INFORMATION_SCHEMA.PARTITIONS` to inspect partition metadata.

---

## Query Types and SQL Capabilities

- **Standard SQL (GoogleSQL)**: ANSI 2011 compliant; default and recommended dialect
- **Legacy SQL**: deprecated; avoid in new code; some older features not in Standard SQL
- **DML**: `INSERT`, `UPDATE`, `DELETE`, `MERGE` (upsert); row-level mutations; best effort for small changes; use `MERGE` for CDC patterns
- **DDL**: `CREATE TABLE`, `CREATE VIEW`, `CREATE MATERIALIZED VIEW`, `ALTER TABLE`, `DROP TABLE`, `CREATE SCHEMA`
- **Scripting**: `DECLARE`, `SET`, `IF/ELSEIF/ELSE`, `LOOP`, `WHILE`, `FOR ... IN`, `CALL` (stored procedures); procedural logic in SQL
- **Stored Procedures**: `CREATE PROCEDURE`; reusable SQL logic; supports transactions (`BEGIN TRANSACTION / COMMIT / ROLLBACK`)
- **UDFs (SQL)**: `CREATE FUNCTION` in SQL; scalar or table-valued
- **UDFs (JavaScript)**: `CREATE FUNCTION ... LANGUAGE js`; for custom logic not expressible in SQL; slightly slower than SQL UDFs
- **Remote Functions**: call Cloud Functions or Cloud Run from SQL via connection; enables ML inference, custom logic
- **CTEs**: `WITH clause`; supported including recursive CTEs
- **Window functions**: `OVER (PARTITION BY ... ORDER BY ...)`, `ROW_NUMBER()`, `RANK()`, `NTILE()`, `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`
- **ARRAY and STRUCT**: first-class types; `UNNEST()` to flatten arrays; nested and repeated fields
- **Geographic functions**: `ST_GEOGPOINT`, `ST_DISTANCE`, `ST_WITHIN`, `ST_INTERSECTS`, `GEOGRAPHY` type; BigQuery GIS

---

## Materialized Views

- Pre-computed query results stored as physical tables
- Automatically refreshed when base table data changes (smart incremental refresh)
- Used transparently by optimizer even when query targets base table (query rewrite)
- Limitations: single base table (no joins), no UDFs, subset of SQL supported
- Use cases: pre-aggregate large fact tables for dashboards; accelerate BI tools

---

## BigQuery ML

Train and run ML models directly using SQL — no data movement required.

| Model Type | `CREATE MODEL OPTIONS(model_type=...)` |
|---|---|
| Linear regression | `'linear_reg'` |
| Logistic regression | `'logistic_reg'` |
| K-means clustering | `'kmeans'` |
| Matrix factorization | `'matrix_factorization'` |
| XGBoost (boosted trees) | `'boosted_tree_classifier'` / `'boosted_tree_regressor'` |
| Deep neural network | `'dnn_classifier'` / `'dnn_regressor'` |
| ARIMA+ (time series) | `'arima_plus'` |
| AutoML Tables (Vertex) | `'automl_classifier'` / `'automl_regressor'` — imports Vertex AutoML |
| Imported TF/ONNX model | `'tensorflow'` / `'onnx'` — bring pre-trained model |

Key functions: `ML.PREDICT()`, `ML.EVALUATE()`, `ML.TRAINING_INFO()`, `ML.FEATURE_IMPORTANCE()`, `ML.EXPLAIN_PREDICT()`

---

## BigQuery Omni

- Query data in **Amazon S3** and **Azure Blob Storage** without moving data to GCP
- Uses Anthos infrastructure deployed in AWS/Azure regions
- Appears as external tables in BigQuery; standard SQL interface
- Limitations: subset of BigQuery features; compute runs in the remote cloud region (data gravity)
- Use cases: cross-cloud analytics, phased migrations, regulatory data residency requirements

---

## BI Engine

- In-memory analysis layer for BigQuery; sub-second query response
- Reservation-based: purchase GB of BI Engine capacity per project/region
- Works transparently with Looker Studio, Looker, and direct BigQuery queries
- Partial acceleration: eligible portions of query run in-memory; rest falls back to standard execution
- Best for: dashboard queries with repeated filters on the same dataset

---

## Streaming Ingestion

| Method | Throughput | Semantics | Notes |
|---|---|---|---|
| `insertAll` (legacy streaming) | High | At-least-once | Small per-row cost; data available immediately; rows in streaming buffer not in `TABLE_DATE_RANGE` |
| Storage Write API (default stream) | Very high | At-least-once | Lower cost than insertAll; recommended replacement |
| Storage Write API (committed stream) | Very high | Exactly-once | Use for deduplication guarantees |
| Storage Write API (pending stream) | Batch | Exactly-once + atomic | Commit entire stream atomically; use for transactional loads |
| Pub/Sub → Dataflow → BigQuery | High | Configurable | Standard production pattern for event streaming pipelines |

---

## Pricing Model

| Component | On-Demand | Capacity (Slot Reservations) |
|---|---|---|
| Query compute | Per TB bytes processed | Per slot-hour (reservation) |
| Storage (active) | Per GB/month | Same |
| Storage (long-term) | ~50% of active rate | Same |
| Streaming inserts | Per GB inserted | Same |
| Storage API | Per TB read | Same |

**Editions**: Standard (autoscale slots), Enterprise (CMEK, BI Engine included, VPC-SC), Enterprise Plus (max reservation, cross-region disaster recovery). Commitments: 1-year or 3-year for discounts.

---

## Performance Best Practices

1. Always filter on the partition column in `WHERE` clauses to enable partition pruning
2. Use clustering on columns frequently used in `WHERE`, `GROUP BY`, and `JOIN` predicates
3. Avoid `SELECT *` — specify required columns to reduce bytes scanned
4. Use `INFORMATION_SCHEMA.JOBS_BY_PROJECT` to analyze query costs and patterns
5. Prefer `MERGE` over separate `DELETE` + `INSERT` for upsert patterns
6. Use `WITH` CTEs to improve readability; BigQuery inlines them (not materialized unless `MATERIALIZE` hint)
7. Use `APPROX_COUNT_DISTINCT()` instead of `COUNT(DISTINCT ...)` for large cardinality estimates
8. Avoid cross joins and self joins on large tables; use window functions instead
9. For Looker/BI dashboards, enable BI Engine reservations
10. Use `INFORMATION_SCHEMA.PARTITIONS` to verify partition pruning is effective

---

## Data Governance

- **Column-level security**: create policy tags in Data Catalog Taxonomy; assign to columns; grant `datacatalog.categoryFineGrainedReader` to authorized users; unauthorized users see masked values
- **Data Masking rules**: nullify, default value, SHA256 hash, last 4 digits, email mask — defined per policy tag
- **Row-level security**: `CREATE ROW ACCESS POLICY` with `GRANT TO` clause; filter rows for specific users/groups
- **Authorized views**: allow a view in one dataset to access tables in another dataset without granting access to underlying tables
- **Authorized datasets**: entire dataset can be authorized to access another dataset
- **Data Catalog integration**: auto-discovers BigQuery assets; tags, tag templates, business metadata
- **Dataplex integration**: data quality rules, data lineage tracking, auto-discovery
- **Sensitive Data Protection (DLP)**: scan BigQuery tables for PII, credentials, and sensitive data; de-identify results

---

## Scheduling and Automation

- **Scheduled queries**: BigQuery-native query scheduling; hourly/daily/weekly/custom cron; writes results to destination table; uses BigQuery Data Transfer Service infrastructure
- **BigQuery Data Transfer Service**: managed connectors for Google Ads, Campaign Manager, YouTube, Google Play, Salesforce, Amazon S3, Teradata, Redshift — scheduled data imports into BigQuery
- **Reservations and workload management**: assign projects/folders to reservations; idle slot sharing; autoscale reservations (scale up/down within bounds)

---

## Integration Points

- **Looker / Looker Studio**: BI and visualization
- **Vertex AI**: export data to Vertex; BQML imports Vertex AutoML; Feature Store reads from BigQuery
- **Dataflow**: BigQuery I/O connector for streaming and batch pipelines
- **Dataproc**: BigQuery connector for Spark jobs
- **Cloud Storage**: load/export data; external tables
- **Pub/Sub**: streaming ingestion pattern via Dataflow
- **Data Catalog / Dataplex**: metadata, governance, lineage
- **Cloud Composer**: orchestrate BigQuery jobs with Airflow BigQueryOperator
