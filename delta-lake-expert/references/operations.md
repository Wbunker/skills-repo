# Operations & Maintenance — Chapters 3-5

CRUD operations, MERGE, time travel, schema evolution, and table maintenance.

## Table of Contents

- [Create Tables](#create-tables)
- [Read with Time Travel](#read-with-time-travel)
- [Update and Delete](#update-and-delete)
- [MERGE (Upsert)](#merge-upsert)
- [Schema Enforcement and Evolution](#schema-enforcement-and-evolution)
- [Table Maintenance](#table-maintenance)
- [Table Properties](#table-properties)

---

## Create Tables

```sql
-- Managed table
CREATE TABLE events (
  id BIGINT,
  event_type STRING,
  event_date DATE,
  payload STRING
) USING DELTA;

-- With liquid clustering (recommended for new tables)
CREATE TABLE events (
  id BIGINT,
  event_type STRING,
  event_date DATE
) USING DELTA
CLUSTER BY (event_date, event_type);

-- From existing data
CREATE TABLE events USING DELTA AS SELECT * FROM parquet.`/data/events/`;

-- Convert Parquet to Delta (in-place, no data copy)
CONVERT TO DELTA parquet.`/data/events/`;
```

## Read with Time Travel

```sql
-- By version number
SELECT * FROM events VERSION AS OF 5;

-- By timestamp
SELECT * FROM events TIMESTAMP AS OF '2024-06-15T10:00:00';

-- View history
DESCRIBE HISTORY events;

-- Restore to a previous version
RESTORE TABLE events TO VERSION AS OF 5;
RESTORE TABLE events TO TIMESTAMP AS OF '2024-06-15';
```

**Python (delta-rs)**:
```python
dt = DeltaTable("/path/to/table")
df = dt.load_as_version(5).to_pandas()
```

**Retention**: Controlled by `delta.logRetentionDuration` (default 30 days) and `delta.deletedFileRetentionDuration` (default 7 days). VACUUM removes files older than retention.

## Update and Delete

```sql
-- Update
UPDATE events SET event_type = 'click' WHERE event_type = 'clk';

-- Delete
DELETE FROM events WHERE event_date < '2023-01-01';

-- With deletion vectors enabled, these operations are merge-on-read
-- (mark rows as deleted without rewriting files)
```

## MERGE (Upsert)

The most powerful Delta Lake operation. Handles complex upsert, delete, and insert logic in a single atomic operation.

### Basic upsert

```sql
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

### Conditional upsert with delete

```sql
MERGE INTO customers target
USING staged_changes source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.operation = 'DELETE'
  THEN DELETE
WHEN MATCHED AND source.operation = 'UPDATE'
  THEN UPDATE SET
    target.name = source.name,
    target.email = source.email,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED AND source.operation != 'DELETE'
  THEN INSERT (customer_id, name, email, created_at, updated_at)
  VALUES (source.customer_id, source.name, source.email, current_timestamp(), current_timestamp());
```

### SCD Type 2

```sql
-- Step 1: Expire existing current records that have changes
MERGE INTO dim_customer target
USING (
  SELECT s.*, c.customer_sk
  FROM staging s
  JOIN dim_customer c ON s.customer_id = c.customer_id
  WHERE c.is_current = true
    AND (s.name != c.name OR s.email != c.email)
) changes
ON target.customer_sk = changes.customer_sk
WHEN MATCHED THEN UPDATE SET
  is_current = false,
  end_date = current_date();

-- Step 2: Insert new current records
INSERT INTO dim_customer
SELECT
  monotonically_increasing_id() AS customer_sk,
  customer_id, name, email,
  current_date() AS start_date,
  NULL AS end_date,
  true AS is_current
FROM staging s
WHERE NOT EXISTS (
  SELECT 1 FROM dim_customer c
  WHERE c.customer_id = s.customer_id
    AND c.is_current = true
    AND c.name = s.name AND c.email = s.email
);
```

### Deduplication on insert

```sql
MERGE INTO events target
USING new_events source
ON target.event_id = source.event_id
WHEN NOT MATCHED THEN INSERT *;
```

### WHEN NOT MATCHED BY SOURCE (Delta 3.x+)

```sql
-- Delete target rows that don't exist in source (full sync)
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

## Schema Enforcement and Evolution

### Schema enforcement (default)

Delta Lake rejects writes with mismatched schemas:

```python
# This FAILS if df has columns not in the table
df.write.format("delta").mode("append").saveAsTable("events")
# AnalysisException: cannot resolve column 'new_col'
```

### Schema evolution

```python
# Add new columns from source automatically
df.write.format("delta") \
  .option("mergeSchema", "true") \
  .mode("append") \
  .saveAsTable("events")
```

```sql
-- Manual schema changes
ALTER TABLE events ADD COLUMNS (region STRING, score DOUBLE);
ALTER TABLE events DROP COLUMN score;
ALTER TABLE events RENAME COLUMN region TO geo_region;
ALTER TABLE events ALTER COLUMN id TYPE BIGINT;  -- type widening (Delta 3.2+)
```

**Schema evolution in MERGE**: Enable automatic schema evolution for MERGE operations:
```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

### Type widening (Delta 3.2+ / GA in 4.0)

Widen column types without rewriting data:

```sql
ALTER TABLE events SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE events ALTER COLUMN id TYPE BIGINT;  -- INT → BIGINT, no rewrite
```

Supported widenings: `BYTE→SHORT→INT→LONG`, `FLOAT→DOUBLE`, `DATE→TIMESTAMP_NTZ`.

## Table Maintenance

### DESCRIBE and metadata

```sql
DESCRIBE DETAIL events;          -- file count, size, partitioning, properties
DESCRIBE HISTORY events;         -- all commits with timestamps, operations, metrics
SHOW TBLPROPERTIES events;       -- all table properties
```

### RESTORE

```sql
RESTORE TABLE events TO VERSION AS OF 42;
```

Undoes all changes after version 42. Does NOT delete files — creates a new commit that references the old file set. Run VACUUM afterward to reclaim space.

### REPLACE TABLE

```sql
CREATE OR REPLACE TABLE events (...) USING DELTA;
```

Atomically replaces the table schema and data. History is preserved.

## Table Properties

Key properties to set:

```sql
ALTER TABLE events SET TBLPROPERTIES (
  -- Retention
  'delta.logRetentionDuration' = 'interval 30 days',
  'delta.deletedFileRetentionDuration' = 'interval 7 days',

  -- Auto optimization
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',

  -- Change Data Feed
  'delta.enableChangeDataFeed' = 'true',

  -- Deletion vectors
  'delta.enableDeletionVectors' = 'true',

  -- Type widening
  'delta.enableTypeWidening' = 'true',

  -- Target file size (default 1GB)
  'delta.targetFileSize' = '134217728'  -- 128MB for streaming tables
);
```
