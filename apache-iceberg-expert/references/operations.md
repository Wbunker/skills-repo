# Operations — Chapters 4-5

DDL, DML, MERGE, schema evolution, partition evolution, time travel, snapshots, branching, and tagging.

## Table of Contents

- [DDL Operations](#ddl-operations)
- [DML Operations](#dml-operations)
- [MERGE](#merge)
- [Schema Evolution](#schema-evolution)
- [Partition Evolution](#partition-evolution)
- [Time Travel](#time-travel)
- [Snapshots](#snapshots)
- [Branching and Tagging](#branching-and-tagging)
- [Rollback and Restore](#rollback-and-restore)
- [Metadata Tables](#metadata-tables)

---

## DDL Operations

### Create tables

```sql
-- Basic table
CREATE TABLE catalog.db.events (
  id BIGINT,
  event_type STRING,
  event_time TIMESTAMP,
  payload STRING
) USING iceberg;

-- With partitioning
CREATE TABLE catalog.db.events (
  id BIGINT,
  event_type STRING,
  event_time TIMESTAMP
) USING iceberg
PARTITIONED BY (days(event_time), bucket(16, event_type));

-- With sort order
CREATE TABLE catalog.db.events (
  id BIGINT,
  event_type STRING,
  event_time TIMESTAMP
) USING iceberg
PARTITIONED BY (days(event_time))
TBLPROPERTIES ('write.distribution-mode' = 'range');

-- From existing data (CTAS)
CREATE TABLE catalog.db.events_v2
USING iceberg
AS SELECT * FROM catalog.db.events;
```

### Alter tables

```sql
-- Add columns
ALTER TABLE catalog.db.events ADD COLUMNS (region STRING, score DOUBLE);

-- Drop column
ALTER TABLE catalog.db.events DROP COLUMN score;

-- Rename column
ALTER TABLE catalog.db.events RENAME COLUMN region TO geo_region;

-- Change column type (widening only)
ALTER TABLE catalog.db.events ALTER COLUMN id TYPE BIGINT;

-- Reorder columns
ALTER TABLE catalog.db.events ALTER COLUMN geo_region AFTER event_type;

-- Add column inside struct
ALTER TABLE catalog.db.events ADD COLUMNS (metadata.source STRING);

-- Set table properties
ALTER TABLE catalog.db.events SET TBLPROPERTIES (
  'write.format.default' = 'parquet',
  'write.parquet.compression-codec' = 'zstd'
);

-- Change partition spec (partition evolution)
ALTER TABLE catalog.db.events ADD PARTITION FIELD months(event_time);
ALTER TABLE catalog.db.events DROP PARTITION FIELD days(event_time);
```

### Drop tables

```sql
-- Drop table (metadata only — does NOT delete data files)
DROP TABLE catalog.db.events;

-- Purge table (metadata AND data files)
DROP TABLE catalog.db.events PURGE;
```

## DML Operations

### INSERT

```sql
-- Append
INSERT INTO catalog.db.events VALUES (1, 'click', current_timestamp(), '{}');

-- Insert from query
INSERT INTO catalog.db.events
SELECT * FROM staging.events WHERE event_date = '2024-06-15';

-- Overwrite matching partitions (dynamic)
INSERT OVERWRITE catalog.db.events
SELECT * FROM staging.events;

-- Overwrite specific partition (static)
INSERT OVERWRITE catalog.db.events
PARTITION (event_date = '2024-06-15')
SELECT id, event_type, event_time, payload FROM staging.events;
```

### UPDATE

```sql
UPDATE catalog.db.events
SET event_type = 'click'
WHERE event_type = 'clk';
```

With **copy-on-write**: Rewrites all affected data files.
With **merge-on-read**: Writes position delete files + new data files for updated rows.

### DELETE

```sql
DELETE FROM catalog.db.events
WHERE event_time < timestamp '2023-01-01 00:00:00';
```

With **copy-on-write**: Rewrites affected files without deleted rows.
With **merge-on-read**: Writes delete files marking removed rows.

## MERGE

Atomic upsert combining INSERT, UPDATE, and DELETE:

### Basic upsert

```sql
MERGE INTO catalog.db.events target
USING staging.events source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

### Conditional upsert with delete

```sql
MERGE INTO catalog.db.customers target
USING staging.changes source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.op = 'D'
  THEN DELETE
WHEN MATCHED AND source.op = 'U'
  THEN UPDATE SET
    name = source.name,
    email = source.email,
    updated_at = current_timestamp()
WHEN NOT MATCHED AND source.op != 'D'
  THEN INSERT (customer_id, name, email, created_at, updated_at)
  VALUES (source.customer_id, source.name, source.email, current_timestamp(), current_timestamp());
```

### Deduplication on insert

```sql
MERGE INTO catalog.db.events target
USING new_events source
ON target.event_id = source.event_id
WHEN NOT MATCHED THEN INSERT *;
```

### SCD Type 2 pattern

```sql
-- Step 1: Close existing current records that have changes
MERGE INTO catalog.db.dim_customer target
USING (
  SELECT s.*, c.surrogate_key
  FROM staging s
  JOIN catalog.db.dim_customer c
    ON s.customer_id = c.customer_id
  WHERE c.is_current = true
    AND (s.name != c.name OR s.email != c.email)
) changes
ON target.surrogate_key = changes.surrogate_key
WHEN MATCHED THEN UPDATE SET
  is_current = false,
  end_date = current_date();

-- Step 2: Insert new current records
INSERT INTO catalog.db.dim_customer
SELECT
  uuid() AS surrogate_key,
  customer_id, name, email,
  current_date() AS start_date,
  NULL AS end_date,
  true AS is_current
FROM staging s
WHERE NOT EXISTS (
  SELECT 1 FROM catalog.db.dim_customer c
  WHERE c.customer_id = s.customer_id
    AND c.is_current = true
    AND c.name = s.name AND c.email = s.email
);
```

## Schema Evolution

Iceberg tracks columns by unique integer IDs, not names. This enables safe schema changes without rewriting data.

### Safe operations (metadata-only, no data rewrite)

| Operation | Effect |
|-----------|--------|
| Add column | New column ID assigned. Existing files return NULL for new column. |
| Drop column | Column ID marked as deleted. Existing files still contain data but it's ignored. |
| Rename column | Same column ID, different name. All existing data is accessible. |
| Reorder columns | Display order changes. No effect on stored data. |
| Widen type | INT→LONG, FLOAT→DOUBLE. Readers upcast on read. |
| Make required column optional | Remove NOT NULL constraint. |

### Column ID tracking

```
Column "name" has ID 3
  ↓ rename to "full_name" → still ID 3, all data accessible
  ↓ drop "full_name" → ID 3 marked deleted
  ↓ add new "name" column → gets ID 7, no conflict with old ID 3
```

This prevents the "column reuse" bug where dropping and re-adding a column with the same name accidentally reads old data.

## Partition Evolution

Change how a table is partitioned without rewriting existing data. New data uses the new partition spec; old data keeps the old spec.

```sql
-- Start with daily partitioning
CREATE TABLE catalog.db.events (...) PARTITIONED BY (days(event_time));

-- Later, switch to hourly as data volume grows
ALTER TABLE catalog.db.events ADD PARTITION FIELD hours(event_time);
ALTER TABLE catalog.db.events DROP PARTITION FIELD days(event_time);
```

**How it works**:
- Each data file records which partition spec it was written with
- Query planning evaluates predicates against all partition specs
- Old files are pruned by old spec, new files by new spec
- No data migration or rewrite needed

## Time Travel

### Query historical snapshots

```sql
-- By snapshot ID
SELECT * FROM catalog.db.events VERSION AS OF 1234567890;

-- By timestamp
SELECT * FROM catalog.db.events TIMESTAMP AS OF '2024-06-15 10:00:00';

-- Spark DataFrame API
spark.read.option("snapshot-id", 1234567890).table("catalog.db.events")
spark.read.option("as-of-timestamp", "1719100000000").table("catalog.db.events")
```

### View snapshot history

```sql
SELECT * FROM catalog.db.events.history;
SELECT * FROM catalog.db.events.snapshots;
```

## Snapshots

Every write operation creates a new immutable snapshot:

```
Snapshot 1 (append) → Snapshot 2 (append) → Snapshot 3 (delete) → Snapshot 4 (merge)
```

Each snapshot contains:
- Snapshot ID (unique)
- Timestamp
- Operation type (append, overwrite, delete, replace)
- Manifest list reference
- Summary (records added/deleted/updated)

### Snapshot retention

```sql
-- Expire snapshots older than 5 days (Spark procedure)
CALL catalog.system.expire_snapshots('db.events', TIMESTAMP '2024-06-10 00:00:00');

-- Keep at least N snapshots
CALL catalog.system.expire_snapshots(
  table => 'db.events',
  older_than => TIMESTAMP '2024-06-10 00:00:00',
  retain_last => 10
);
```

## Branching and Tagging

Git-like version control for tables.

### Tags (immutable references)

```sql
-- Create a tag on current snapshot
ALTER TABLE catalog.db.events CREATE TAG `end_of_q2_2024`;

-- Create tag on specific snapshot
ALTER TABLE catalog.db.events CREATE TAG `model_training_v3`
  AS OF VERSION 1234567890;

-- Set tag retention
ALTER TABLE catalog.db.events CREATE TAG `audit_2024`
  AS OF VERSION 1234567890
  RETAIN 365 DAYS;

-- Read from tag
SELECT * FROM catalog.db.events VERSION AS OF 'end_of_q2_2024';

-- Drop tag
ALTER TABLE catalog.db.events DROP TAG `end_of_q2_2024`;
```

### Branches (mutable references)

```sql
-- Create branch from current state
ALTER TABLE catalog.db.events CREATE BRANCH `etl_staging`;

-- Write to branch
INSERT INTO catalog.db.events.branch_etl_staging VALUES (...);

-- Read from branch
SELECT * FROM catalog.db.events VERSION AS OF 'etl_staging';

-- Set branch snapshot retention
ALTER TABLE catalog.db.events CREATE BRANCH `experiment`
  RETAIN 7 DAYS
  WITH SNAPSHOT RETENTION 2 DAYS;

-- Drop branch
ALTER TABLE catalog.db.events DROP BRANCH `etl_staging`;
```

### Use cases

| Pattern | Implementation |
|---------|---------------|
| Audit snapshots | Tag at end of each reporting period |
| ML training data | Tag the exact snapshot used for training |
| Write-Audit-Publish (WAP) | Write to branch, validate, fast-forward main |
| A/B testing data | Separate branches for experimental pipelines |
| Rollback point | Tag before risky migrations |

## Rollback and Restore

### Rollback to snapshot

```sql
-- Rollback to specific snapshot (Spark procedure)
CALL catalog.system.rollback_to_snapshot('db.events', 1234567890);

-- Rollback to timestamp
CALL catalog.system.rollback_to_timestamp('db.events', TIMESTAMP '2024-06-15 10:00:00');
```

Rollback creates a new snapshot that points to the same manifest list as the target snapshot. It does not delete any files.

### Cherry-pick snapshot

```sql
-- Apply changes from one snapshot on top of current
CALL catalog.system.cherrypick_snapshot('db.events', 1234567891);
```

Only works for `append` operations (wap snapshots).

## Metadata Tables

Iceberg exposes internal metadata as queryable tables:

```sql
-- Snapshot history
SELECT * FROM catalog.db.events.history;

-- All snapshots with details
SELECT * FROM catalog.db.events.snapshots;

-- Data files in current snapshot
SELECT * FROM catalog.db.events.files;

-- All data files across all snapshots
SELECT * FROM catalog.db.events.all_data_files;

-- Manifests
SELECT * FROM catalog.db.events.manifests;
SELECT * FROM catalog.db.events.all_manifests;

-- Partitions with stats
SELECT * FROM catalog.db.events.partitions;

-- Metadata log entries
SELECT * FROM catalog.db.events.metadata_log_entries;

-- References (branches and tags)
SELECT * FROM catalog.db.events.refs;

-- All entries (manifest entries)
SELECT * FROM catalog.db.events.entries;
```

### Useful metadata queries

```sql
-- Find large data files
SELECT file_path, file_size_in_bytes, record_count
FROM catalog.db.events.files
ORDER BY file_size_in_bytes DESC
LIMIT 20;

-- Partition stats
SELECT partition, record_count, file_count
FROM catalog.db.events.partitions
ORDER BY record_count DESC;

-- Recent snapshot operations
SELECT snapshot_id, committed_at, operation, summary
FROM catalog.db.events.snapshots
ORDER BY committed_at DESC
LIMIT 10;
```
