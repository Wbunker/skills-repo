# Advanced Features — Chapters 6, 8

Native application development, deletion vectors, UniForm, generated columns, constraints, and the Variant type.

## Table of Contents

- [Deletion Vectors](#deletion-vectors)
- [UniForm (Universal Format)](#uniform-universal-format)
- [Generated Columns](#generated-columns)
- [Constraints](#constraints)
- [Variant Type](#variant-type)
- [Row Tracking](#row-tracking)
- [Coordinated Commits](#coordinated-commits)
- [Native Applications (Python / Rust)](#native-applications)

---

## Deletion Vectors

Marks rows as deleted without rewriting data files. Converts DELETE, UPDATE, and MERGE from copy-on-write to merge-on-read.

### Enable

```sql
ALTER TABLE events SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');
```

### How it works

1. A DELETE/UPDATE/MERGE identifies rows to remove
2. Instead of rewriting the entire Parquet file, a bitmap file (`.bin`) is written alongside the data file
3. Reads apply the bitmap to filter out deleted rows
4. OPTIMIZE eventually purges deletion vectors by rewriting affected files

### Benefits

- **Dramatic write speedup**: DELETE/UPDATE/MERGE write only a small bitmap instead of rewriting entire data files
- **Reduced write amplification**: Especially impactful on large tables with small updates
- **Improved merge performance**: MERGE operations are significantly faster

### Purging deletion vectors

```sql
-- Compact files and remove deletion vectors
OPTIMIZE events;

-- Force purge without compaction
REORG TABLE events APPLY (PURGE);
```

### Trade-offs

- Slight read overhead (must check bitmaps) — mitigated in Delta 3.2+ with predicate pushdown
- Accumulating unpurged deletion vectors degrades read performance over time
- Schedule regular OPTIMIZE to keep read performance stable

## UniForm (Universal Format)

Write once in Delta format, auto-generate Iceberg and Hudi metadata for cross-engine reads.

### Enable

```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.universalFormat.enabledFormats' = 'iceberg'         -- Iceberg only
  -- 'delta.universalFormat.enabledFormats' = 'iceberg,hudi' -- Both
);

-- Or at creation
CREATE TABLE events (...) USING DELTA
TBLPROPERTIES ('delta.universalFormat.enabledFormats' = 'iceberg');
```

### How it works

- After every Delta commit, UniForm asynchronously generates Iceberg metadata (and/or Hudi metadata)
- No data duplication — same Parquet files, just additional metadata
- Iceberg clients (Trino, Athena, BigQuery, Snowflake) can read the table as if it were native Iceberg
- GA in Delta 4.0

### Requirements

- Requires column mapping (`delta.columnMapping.mode = 'name'`)
- Automatically enabled when UniForm is activated

## Generated Columns

Columns whose values are automatically computed from other columns:

```sql
CREATE TABLE events (
  id BIGINT,
  event_time TIMESTAMP,
  event_date DATE GENERATED ALWAYS AS (CAST(event_time AS DATE)),
  event_year INT GENERATED ALWAYS AS (YEAR(event_time))
) USING DELTA;
```

Use cases:
- Partition columns derived from timestamps
- Computed fields for data skipping (Z-ordering/clustering targets)
- Denormalized fields for common queries

## Constraints

### NOT NULL

```sql
ALTER TABLE events ALTER COLUMN id SET NOT NULL;
```

### CHECK constraints

```sql
ALTER TABLE events ADD CONSTRAINT valid_amount CHECK (amount > 0);
ALTER TABLE events ADD CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'pending'));

-- Drop constraint
ALTER TABLE events DROP CONSTRAINT valid_amount;
```

CHECK constraints are enforced on every write (INSERT, UPDATE, MERGE). Violating rows cause the entire transaction to fail.

### Identity columns (Delta 4.0+)

```sql
CREATE TABLE events (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  event_type STRING,
  payload STRING
) USING DELTA;
```

Auto-incrementing unique identifiers. Values are guaranteed unique but not necessarily contiguous.

## Variant Type

Semi-structured data type (Delta 4.0, preview) for schema-on-read workloads:

```sql
CREATE TABLE iot_events (
  device_id STRING,
  timestamp TIMESTAMP,
  payload VARIANT  -- flexible JSON-like data
) USING DELTA;

-- Insert
INSERT INTO iot_events VALUES ('d1', now(), PARSE_JSON('{"temp": 72.5, "humidity": 45}'));

-- Query with path extraction
SELECT device_id, payload:temp::DOUBLE AS temperature
FROM iot_events
WHERE payload:humidity::INT > 40;
```

**Shredded Variants** (preview): Extract frequently queried fields as physical columns with statistics for data skipping, while keeping the full Variant for schema flexibility.

## Row Tracking

Track individual rows across operations (Delta 4.0):

```sql
ALTER TABLE events SET TBLPROPERTIES ('delta.enableRowTracking' = 'true');
```

Each row gets a stable row ID that persists across updates, compaction, and clustering. Enables efficient Change Data Feed — CDF can track changes at the row level rather than file level.

## Coordinated Commits

Centralized commit coordination for multi-engine writes (Delta 4.0, preview):

```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.coordinatedCommits.commitCoordinatorName' = 'dynamodb',
  'delta.coordinatedCommits.commitCoordinatorConf' = '{"tableName": "delta_commits"}'
);
```

Uses a commit coordinator (currently DynamoDB-based) instead of filesystem-level atomic operations. Enables:
- Multi-cloud writes to the same table
- Multi-engine writes (Spark + Flink + custom apps)
- Future: multi-statement and multi-table transactions

## Native Applications

### Python (delta-rs / deltalake)

```python
from deltalake import DeltaTable, write_deltalake
import pandas as pd

# Write
df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
write_deltalake("s3://bucket/table", df, mode="append",
                storage_options={"AWS_REGION": "us-east-1"})

# Read
dt = DeltaTable("s3://bucket/table")
df = dt.to_pandas()

# Time travel
df_v2 = dt.load_as_version(2).to_pandas()

# Merge
dt.merge(
    source=new_df,
    predicate="target.id = source.id",
    source_alias="source",
    target_alias="target"
).when_matched_update_all() \
 .when_not_matched_insert_all() \
 .execute()

# Optimize and vacuum
dt.optimize.compact()
dt.optimize.z_order(["id"])
dt.vacuum(retention_hours=168)
```

### Rust (delta-rs)

```rust
use deltalake::open_table;

#[tokio::main]
async fn main() {
    let table = open_table("s3://bucket/table").await.unwrap();
    println!("Version: {}", table.version());
    println!("Files: {:?}", table.get_files());
}
```

### AWS Lambda pattern

```python
# Lambda function for serverless Delta Lake writes
import json
from deltalake import write_deltalake
import pandas as pd

def handler(event, context):
    records = [json.loads(r["body"]) for r in event["Records"]]
    df = pd.DataFrame(records)
    write_deltalake(
        "s3://bucket/events",
        df,
        mode="append",
        storage_options={"AWS_ALLOW_HTTP": "true"}
    )
    return {"statusCode": 200}
```

**Concurrent writes on S3**: S3 lacks atomic rename. Use DynamoDB-based log store (`delta.logStore.class`) or coordinated commits for safe concurrent writes.
