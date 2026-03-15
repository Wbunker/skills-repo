# BigQuery — CLI Reference

BigQuery uses the `bq` CLI (bundled with Google Cloud SDK) for most operations, and `gcloud` for IAM, reservations, and Data Transfer Service.

---

## Authentication and Project Setup

```bash
# Set default project for bq commands
bq --project_id=my-project ls

# Or use gcloud config
gcloud config set project my-project

# Application Default Credentials (for scripts)
gcloud auth application-default login
```

---

## Datasets

```bash
# Create a dataset (US multi-region, 90-day table expiration)
bq mk \
  --dataset \
  --location=US \
  --default_table_expiration=7776000 \
  --description="Analytics dataset for marketing data" \
  my-project:my_dataset

# Create dataset in specific region
bq mk --dataset --location=us-central1 my-project:regional_dataset

# List datasets in current project
bq ls

# List datasets in another project
bq ls --project_id=other-project

# Describe a dataset
bq show my-project:my_dataset

# Update dataset description and labels
bq update --description="Updated description" my-project:my_dataset
bq update --set_label env:production my-project:my_dataset
bq update --clear_label env my-project:my_dataset

# Set default table expiration on existing dataset (seconds; 0 = never)
bq update --default_table_expiration=2592000 my-project:my_dataset

# Delete dataset (must be empty unless --recursive)
bq rm --dataset my-project:my_dataset
bq rm --recursive --dataset my-project:my_dataset
```

---

## Tables

```bash
# Create table with inline schema
bq mk --table my-project:my_dataset.my_table \
  user_id:INTEGER,name:STRING,email:STRING,created_at:TIMESTAMP

# Create table from JSON schema file
bq mk --table my-project:my_dataset.my_table ./schema.json

# Create partitioned table (date partitioning on column)
bq mk --table \
  --time_partitioning_type=DAY \
  --time_partitioning_field=event_date \
  --clustering_fields=user_id,country \
  --require_partition_filter=true \
  my-project:my_dataset.events \
  event_id:STRING,user_id:INTEGER,country:STRING,event_date:DATE,payload:STRING

# Create ingestion-time partitioned table
bq mk --table \
  --time_partitioning_type=DAY \
  my-project:my_dataset.logs \
  log_level:STRING,message:STRING

# Create integer-range partitioned table
bq mk --table \
  --range_partitioning=shard_id,0,100,10 \
  my-project:my_dataset.sharded \
  shard_id:INTEGER,data:STRING

# Describe a table (schema, partitioning, stats)
bq show my-project:my_dataset.my_table

# Show just the schema as JSON
bq show --schema my-project:my_dataset.my_table

# Show schema and format as pretty JSON
bq show --schema --format=prettyjson my-project:my_dataset.my_table

# List tables in a dataset
bq ls my-project:my_dataset

# List tables with metadata
bq ls --format=prettyjson my-project:my_dataset

# Copy table
bq cp my-project:my_dataset.source_table my-project:my_dataset.dest_table

# Copy table across projects
bq cp source-project:dataset.table dest-project:dataset.table

# Copy with append
bq cp --append_table source-project:dataset.source dest-project:dataset.dest

# Delete table
bq rm --table my-project:my_dataset.my_table

# Delete table without confirmation prompt
bq rm -f --table my-project:my_dataset.my_table
```

---

## Loading Data

```bash
# Load CSV from GCS
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --autodetect \
  my-project:my_dataset.my_table \
  gs://my-bucket/data/*.csv

# Load CSV with explicit schema
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  my-project:my_dataset.my_table \
  gs://my-bucket/data.csv \
  id:INTEGER,name:STRING,amount:FLOAT,ts:TIMESTAMP

# Load newline-delimited JSON
bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --autodetect \
  my-project:my_dataset.events \
  gs://my-bucket/events/*.json

# Load Avro (schema embedded in file)
bq load \
  --source_format=AVRO \
  my-project:my_dataset.my_table \
  gs://my-bucket/data.avro

# Load Parquet
bq load \
  --source_format=PARQUET \
  my-project:my_dataset.my_table \
  gs://my-bucket/data/*.parquet

# Load with write disposition (append or overwrite)
bq load --replace \
  --source_format=CSV \
  my-project:my_dataset.my_table \
  gs://my-bucket/full_refresh.csv \
  id:INTEGER,value:STRING

bq load --noreplace \
  --source_format=CSV \
  my-project:my_dataset.my_table \
  gs://my-bucket/incremental.csv \
  id:INTEGER,value:STRING

# Load into a specific partition
bq load \
  --source_format=CSV \
  my-project:my_dataset.events\$20240101 \
  gs://my-bucket/2024-01-01/*.csv
```

---

## Querying

```bash
# Run a query (interactive, results to stdout)
bq query \
  --use_legacy_sql=false \
  'SELECT user_id, COUNT(*) as cnt FROM my-project.my_dataset.events GROUP BY 1 ORDER BY 2 DESC LIMIT 10'

# Run query and write results to a table
bq query \
  --use_legacy_sql=false \
  --destination_table=my-project:my_dataset.results \
  --replace \
  'SELECT * FROM my-project.my_dataset.events WHERE event_date = "2024-01-01"'

# Run query with large results (bypass 128MB limit)
bq query \
  --use_legacy_sql=false \
  --allow_large_results \
  --destination_table=my-project:temp_dataset.large_results \
  'SELECT * FROM my-project.my_dataset.large_table'

# Run query without cache
bq query --use_legacy_sql=false --nocache \
  'SELECT COUNT(*) FROM my-project.my_dataset.my_table'

# Dry run (estimate bytes processed without running)
bq query --use_legacy_sql=false --dry_run \
  'SELECT * FROM my-project.my_dataset.events WHERE event_date = "2024-01-01"'

# Run query from file
bq query --use_legacy_sql=false < query.sql

# Use named parameters
bq query --use_legacy_sql=false \
  --parameter='event_date:DATE:2024-01-01' \
  'SELECT * FROM my-project.my_dataset.events WHERE event_date = @event_date'

# Format output as JSON
bq query --use_legacy_sql=false --format=json \
  'SELECT 1 as num, "hello" as str'
```

---

## Exporting Data

```bash
# Export table to GCS as CSV
bq extract \
  --destination_format=CSV \
  my-project:my_dataset.my_table \
  gs://my-bucket/export/data-*.csv

# Export as compressed CSV
bq extract \
  --destination_format=CSV \
  --compression=GZIP \
  my-project:my_dataset.my_table \
  gs://my-bucket/export/data-*.csv.gz

# Export as Avro
bq extract \
  --destination_format=AVRO \
  my-project:my_dataset.my_table \
  gs://my-bucket/export/data-*.avro

# Export as Parquet
bq extract \
  --destination_format=PARQUET \
  my-project:my_dataset.my_table \
  gs://my-bucket/export/data-*.parquet

# Export as newline-delimited JSON
bq extract \
  --destination_format=NEWLINE_DELIMITED_JSON \
  my-project:my_dataset.my_table \
  gs://my-bucket/export/data-*.json
```

---

## Jobs

```bash
# List recent jobs
bq ls --jobs --all

# List jobs for a project (last 10)
bq ls --jobs -n 10 --project_id=my-project

# Describe a specific job
bq show --job my-project:US.bqjob_r1234567890_00001234567890_1

# Cancel a running job
bq cancel my-project:US.bqjob_r1234567890_00001234567890_1

# Show job statistics (bytes processed, slot time, etc.)
bq show --format=prettyjson --job my-project:US.bqjob_r1234567890_00001234567890_1
```

---

## Schema Operations

```bash
# Evolve schema (add nullable columns only — backwards compatible)
bq update my-project:my_dataset.my_table ./updated_schema.json

# Add a single column via schema update
# (update requires full schema JSON; extract current schema first)
bq show --schema --format=prettyjson my-project:my_dataset.my_table > schema.json
# Edit schema.json to add the new column, then:
bq update my-project:my_dataset.my_table schema.json

# Relax a column from REQUIRED to NULLABLE
bq update --relax_column=field_name my-project:my_dataset.my_table
```

---

## SQL Examples

```sql
-- Partition pruning: filter on partition column
SELECT user_id, SUM(revenue) AS total_revenue
FROM `my-project.my_dataset.orders`
WHERE order_date BETWEEN DATE('2024-01-01') AND DATE('2024-01-31')
GROUP BY user_id;

-- Window function: running total per user
SELECT
  user_id,
  event_date,
  revenue,
  SUM(revenue) OVER (PARTITION BY user_id ORDER BY event_date) AS running_total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_date DESC) AS recency_rank
FROM `my-project.my_dataset.orders`;

-- ARRAY and STRUCT with UNNEST
SELECT
  user_id,
  tag
FROM `my-project.my_dataset.users`,
UNNEST(tags) AS tag;

-- CTE + MERGE for upsert
MERGE `my-project.my_dataset.customers` T
USING (
  SELECT customer_id, name, email, updated_at
  FROM `my-project.my_dataset.customers_staging`
) S
ON T.customer_id = S.customer_id
WHEN MATCHED AND S.updated_at > T.updated_at THEN
  UPDATE SET name = S.name, email = S.email, updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, email, updated_at)
  VALUES (S.customer_id, S.name, S.email, S.updated_at);

-- Scripting with variables
DECLARE cutoff_date DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY);
DECLARE row_count INT64;

DELETE FROM `my-project.my_dataset.events`
WHERE event_date < cutoff_date;

SET row_count = @@row_count;
SELECT CONCAT('Deleted ', CAST(row_count AS STRING), ' rows') AS result;

-- Create materialized view
CREATE MATERIALIZED VIEW `my-project.my_dataset.daily_revenue_mv`
PARTITION BY order_date
CLUSTER BY region
AS
SELECT
  DATE(order_timestamp) AS order_date,
  region,
  SUM(revenue) AS total_revenue,
  COUNT(*) AS order_count
FROM `my-project.my_dataset.orders`
GROUP BY 1, 2;

-- Create row access policy (row-level security)
CREATE ROW ACCESS POLICY sales_region_filter
ON `my-project.my_dataset.sales`
GRANT TO ("group:apac-team@example.com")
FILTER USING (region = 'APAC');

-- Approximate count for high cardinality
SELECT
  DATE(event_date) AS day,
  APPROX_COUNT_DISTINCT(user_id) AS approx_unique_users
FROM `my-project.my_dataset.events`
GROUP BY 1
ORDER BY 1;
```

---

## IAM for BigQuery

```bash
# Grant BigQuery Data Viewer on a dataset (gcloud approach via project IAM)
gcloud projects add-iam-policy-binding my-project \
  --member="user:analyst@example.com" \
  --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User (required to run queries)
gcloud projects add-iam-policy-binding my-project \
  --member="user:analyst@example.com" \
  --role="roles/bigquery.jobUser"

# Dataset-level IAM via bq update (JSON access object)
# Get current ACL
bq show --format=prettyjson my-project:my_dataset | jq '.access'

# Common BigQuery IAM roles:
# roles/bigquery.admin           - full admin
# roles/bigquery.dataOwner       - manage dataset tables, read/write data
# roles/bigquery.dataEditor      - read/write data, not manage dataset
# roles/bigquery.dataViewer      - read data only
# roles/bigquery.jobUser         - run jobs (queries) in the project
# roles/bigquery.user            - jobUser + dataViewer on own project
# roles/bigquery.readSessionUser - BigQuery Storage Read API
```

---

## Reservations and Capacity

```bash
# Create a capacity commitment (monthly, 100 slots)
gcloud bigquery reservations capacity-commitments create \
  --location=us-central1 \
  --slot-count=100 \
  --plan=MONTHLY \
  --project=my-project

# List capacity commitments
gcloud bigquery reservations capacity-commitments list \
  --location=us-central1 \
  --project=my-project

# Create a reservation (named pool of slots)
gcloud bigquery reservations create my-reservation \
  --location=us-central1 \
  --slot-count=100 \
  --project=my-project

# List reservations
gcloud bigquery reservations list \
  --location=us-central1 \
  --project=my-project

# Create assignment (assign project to reservation)
gcloud bigquery reservations assignments create \
  --reservation=my-reservation \
  --assignee-type=PROJECT \
  --assignee-id=my-project \
  --job-type=QUERY \
  --location=us-central1 \
  --project=my-project

# List assignments
gcloud bigquery reservations assignments list \
  --reservation=my-reservation \
  --location=us-central1 \
  --project=my-project
```

---

## BigQuery Storage Read API

```bash
# Run query using Storage Read API for faster result retrieval (Python example flag)
bq query --use_legacy_sql=false \
  --format=csv \
  'SELECT * FROM my-project.my_dataset.my_table LIMIT 1000'

# The Storage Read API is primarily used via client libraries:
# Python: from google.cloud import bigquery_storage
# Java: com.google.cloud.bigquery.storage.v1
# Go: cloud.google.com/go/bigquery/storage/apiv1
```

---

## INFORMATION_SCHEMA Queries

```sql
-- Inspect partition metadata
SELECT
  table_name,
  partition_id,
  total_rows,
  total_logical_bytes,
  last_modified_time
FROM `my-project.my_dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'events'
ORDER BY partition_id DESC;

-- Recent job history with cost
SELECT
  job_id,
  user_email,
  query,
  total_bytes_processed,
  total_slot_ms,
  creation_time,
  end_time
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND job_type = 'QUERY'
ORDER BY total_bytes_processed DESC
LIMIT 20;

-- Table storage sizes
SELECT
  table_id,
  ROUND(size_bytes / POW(10, 9), 2) AS size_gb,
  row_count,
  last_modified_time
FROM `my-project.my_dataset.__TABLES__`
ORDER BY size_bytes DESC;
```
