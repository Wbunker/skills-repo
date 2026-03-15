# Engine Integrations — Chapter 9

Configuration and usage for Spark, Trino, Flink, Athena, Dremio, Snowflake, StarRocks, EMR, and DuckDB.

## Table of Contents

- [Apache Spark](#apache-spark)
- [Trino / Presto](#trino--presto)
- [Apache Flink](#apache-flink)
- [Amazon Athena](#amazon-athena)
- [Amazon EMR](#amazon-emr)
- [Dremio](#dremio)
- [Snowflake](#snowflake)
- [StarRocks](#starrocks)
- [DuckDB](#duckdb)
- [Multi-Engine Concurrency](#multi-engine-concurrency)

---

## Apache Spark

The most mature and feature-complete Iceberg integration.

### Setup

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("iceberg") \
    .config("spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.my_catalog",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.my_catalog.type", "rest") \
    .config("spark.sql.catalog.my_catalog.uri",
            "https://catalog.example.com") \
    .getOrCreate()
```

### Version compatibility

| Spark | Iceberg runtime |
|-------|----------------|
| 3.5 | `iceberg-spark-runtime-3.5_2.12` |
| 3.4 | `iceberg-spark-runtime-3.4_2.12` |
| 4.0 | `iceberg-spark-runtime-4.0_2.13` (Iceberg 1.7+) |

### Spark DDL/DML

All standard SQL operations are supported via the Iceberg Spark extensions:

```sql
-- Use catalog
USE my_catalog;

-- Full DDL
CREATE TABLE my_catalog.db.events (...) USING iceberg;
ALTER TABLE my_catalog.db.events ADD COLUMNS (...);

-- Full DML
INSERT INTO my_catalog.db.events VALUES (...);
UPDATE my_catalog.db.events SET ... WHERE ...;
DELETE FROM my_catalog.db.events WHERE ...;
MERGE INTO my_catalog.db.events target USING ... ON ...;
```

### Spark procedures

```sql
-- Compaction
CALL my_catalog.system.rewrite_data_files('db.events');

-- Expire snapshots
CALL my_catalog.system.expire_snapshots('db.events', TIMESTAMP '2024-06-01');

-- Remove orphan files
CALL my_catalog.system.remove_orphan_files('db.events');

-- Rewrite manifests
CALL my_catalog.system.rewrite_manifests('db.events');

-- Rollback
CALL my_catalog.system.rollback_to_snapshot('db.events', 1234567890);
CALL my_catalog.system.rollback_to_timestamp('db.events', TIMESTAMP '2024-06-15');

-- Cherry-pick
CALL my_catalog.system.cherrypick_snapshot('db.events', 1234567891);

-- Create/replace tag
CALL my_catalog.system.create_tag('db.events', 'v1.0', 1234567890);

-- Create branch
CALL my_catalog.system.create_branch('db.events', 'staging');

-- Fast-forward branch
CALL my_catalog.system.fast_forward('db.events', 'main', 'staging');

-- Set current snapshot
CALL my_catalog.system.set_current_snapshot('db.events', 1234567890);
```

### Spark write properties

```python
df.writeTo("my_catalog.db.events") \
    .option("write-format", "parquet") \
    .option("target-file-size-bytes", str(512 * 1024 * 1024)) \
    .option("compression-codec", "zstd") \
    .append()
```

### Spark COW vs MOR configuration

```python
# Table-level default
spark.sql("""
  ALTER TABLE my_catalog.db.events SET TBLPROPERTIES (
    'write.delete.mode' = 'merge-on-read',
    'write.update.mode' = 'merge-on-read',
    'write.merge.mode' = 'merge-on-read'
  )
""")
```

## Trino / Presto

### Trino setup

```properties
# /etc/trino/catalog/iceberg.properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=https://catalog.example.com

# Or Hive Metastore
# iceberg.catalog.type=hive_metastore
# hive.metastore.uri=thrift://metastore:9083

# Or Glue
# iceberg.catalog.type=glue
# iceberg.glue.region=us-east-1
```

### Trino operations

```sql
-- DDL
CREATE TABLE iceberg.db.events (
  id BIGINT,
  event_type VARCHAR,
  event_time TIMESTAMP(6) WITH TIME ZONE
) WITH (
  format = 'PARQUET',
  partitioning = ARRAY['day(event_time)']
);

-- DML
INSERT INTO iceberg.db.events VALUES (...);
DELETE FROM iceberg.db.events WHERE event_time < TIMESTAMP '2023-01-01';
UPDATE iceberg.db.events SET event_type = 'click' WHERE event_type = 'clk';
MERGE INTO iceberg.db.events target USING ...;

-- Time travel
SELECT * FROM iceberg.db.events FOR VERSION AS OF 1234567890;
SELECT * FROM iceberg.db.events FOR TIMESTAMP AS OF TIMESTAMP '2024-06-15 10:00:00 UTC';

-- Metadata tables
SELECT * FROM iceberg.db."events$snapshots";
SELECT * FROM iceberg.db."events$manifests";
SELECT * FROM iceberg.db."events$files";
SELECT * FROM iceberg.db."events$history";
SELECT * FROM iceberg.db."events$partitions";

-- Maintenance
ALTER TABLE iceberg.db.events EXECUTE expire_snapshots(retention_threshold => '7d');
ALTER TABLE iceberg.db.events EXECUTE remove_orphan_files(retention_threshold => '7d');
ALTER TABLE iceberg.db.events EXECUTE optimize WHERE event_time > current_date - INTERVAL '7' DAY;
```

### Trino table properties

```sql
CREATE TABLE iceberg.db.events (...) WITH (
  format = 'PARQUET',
  partitioning = ARRAY['day(event_time)', 'bucket(user_id, 16)'],
  sorted_by = ARRAY['event_time'],
  format_version = 2
);
```

## Apache Flink

### Flink catalog setup

```sql
CREATE CATALOG iceberg_catalog WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'https://catalog.example.com'
);

USE CATALOG iceberg_catalog;
```

```java
// Java API
Map<String, String> props = new HashMap<>();
props.put("type", "iceberg");
props.put("catalog-type", "rest");
props.put("uri", "https://catalog.example.com");

CatalogLoader catalogLoader = CatalogLoader.rest("iceberg", props, conf);
```

### Flink operations

```sql
-- DDL
CREATE TABLE db.events (
  id BIGINT,
  event_type STRING,
  event_time TIMESTAMP(3)
) WITH (
  'format-version' = '2',
  'write.upsert.enabled' = 'true'
);

-- DML (batch mode)
INSERT INTO db.events SELECT * FROM source_table;
INSERT OVERWRITE db.events SELECT * FROM source_table;

-- Streaming mode
SET 'execution.runtime-mode' = 'streaming';
INSERT INTO db.events SELECT * FROM kafka_source;
```

### Flink streaming options

| Property | Description | Default |
|----------|-------------|---------|
| `streaming` | Enable streaming read | false |
| `monitor-interval` | How often to check for new snapshots | 60s |
| `streaming-skip-overwrite-snapshots` | Skip overwrite snapshots | false |

## Amazon Athena

### Setup

Athena uses AWS Glue Catalog as the Iceberg catalog. No additional configuration needed for tables registered in Glue.

### Athena operations

```sql
-- Create table
CREATE TABLE db.events (
  id bigint,
  event_type string,
  event_time timestamp
)
PARTITIONED BY (day(event_time))
LOCATION 's3://my-bucket/events/'
TBLPROPERTIES ('table_type' = 'ICEBERG');

-- DML
INSERT INTO db.events VALUES (...);
UPDATE db.events SET event_type = 'click' WHERE event_type = 'clk';
DELETE FROM db.events WHERE event_time < timestamp '2023-01-01';
MERGE INTO db.events target USING ...;

-- Time travel
SELECT * FROM db.events FOR SYSTEM_TIME AS OF TIMESTAMP '2024-06-15 10:00:00';
SELECT * FROM db.events FOR SYSTEM_VERSION AS OF 1234567890;

-- Maintenance
OPTIMIZE db.events REWRITE DATA USING BIN_PACK;
OPTIMIZE db.events REWRITE DATA USING BIN_PACK WHERE event_time > current_date - interval '7' day;
VACUUM db.events;
```

### Athena table properties

```sql
ALTER TABLE db.events SET TBLPROPERTIES (
  'optimize_rewrite_min_data_file_size_bytes' = '67108864',
  'optimize_rewrite_max_data_file_size_bytes' = '536870912',
  'optimize_rewrite_data_file_threshold' = '5',
  'vacuum_max_snapshot_age_seconds' = '604800'
);
```

## Amazon EMR

### EMR Spark configuration

```python
# EMR 6.5+ has native Iceberg support
spark = SparkSession.builder \
    .config("spark.sql.catalog.glue_catalog",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl",
            "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse",
            "s3://my-bucket/warehouse/") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .getOrCreate()
```

EMR 7.12+ supports Iceberg v3 (deletion vectors, new types).

## Dremio

### Dremio configuration

Dremio has native Iceberg support. Tables can be:
- Created directly in Dremio's lakehouse
- Accessed from external catalogs (Glue, Hive, Nessie)

```sql
-- Create table
CREATE TABLE dremio_lakehouse.db.events (
  id BIGINT,
  event_type VARCHAR,
  event_time TIMESTAMP
) PARTITION BY (DAY(event_time));

-- Reflections for acceleration
ALTER TABLE db.events CREATE AGGREGATE REFLECTION agg_ref
USING DIMENSIONS (event_date, event_type) MEASURES (id (COUNT));
```

### Dremio Arctic (Nessie-based catalog)

```sql
-- Work on a branch
USE BRANCH dev IN dremio_lakehouse;
-- Make changes
INSERT INTO db.events VALUES (...);
-- Merge when ready
MERGE BRANCH dev INTO main IN dremio_lakehouse;
```

## Snowflake

### Snowflake Iceberg tables

```sql
-- External Iceberg table (read from S3 via Glue catalog)
CREATE ICEBERG TABLE db.events
  EXTERNAL_VOLUME = 'my_s3_volume'
  CATALOG = 'glue_catalog'
  CATALOG_TABLE_NAME = 'db.events';

-- Managed Iceberg table (Snowflake manages files)
CREATE ICEBERG TABLE db.events (
  id NUMBER,
  event_type VARCHAR,
  event_time TIMESTAMP_NTZ
)
  CATALOG = 'SNOWFLAKE'
  EXTERNAL_VOLUME = 'my_s3_volume'
  BASE_LOCATION = 'events/';

-- Query
SELECT * FROM db.events WHERE event_time > '2024-06-01';
```

## StarRocks

### StarRocks configuration

```sql
-- Create external catalog
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
  "type" = "iceberg",
  "iceberg.catalog.type" = "rest",
  "iceberg.catalog.uri" = "https://catalog.example.com"
);

-- Query
SELECT * FROM iceberg_catalog.db.events
WHERE event_time > '2024-06-01';
```

StarRocks 4.0+ optimizations:
- Global shuffle for non-overlapping writes
- Vectorized C++ execution engine
- CBO for Iceberg scan optimization
- 3-5x faster than Trino for analytical queries (TPC-H benchmarks)

## DuckDB

### DuckDB setup

```sql
INSTALL iceberg;
LOAD iceberg;

-- Read directly from metadata
SELECT * FROM iceberg_scan('s3://bucket/warehouse/db/events');

-- With catalog
ATTACH 'https://catalog.example.com' AS iceberg_cat (TYPE ICEBERG);
SELECT * FROM iceberg_cat.db.events;
```

DuckDB provides fast local analytics over Iceberg tables. Read-only in most configurations.

## Multi-Engine Concurrency

Iceberg supports concurrent reads and writes from multiple engines because:

1. **Atomic metadata swaps**: Catalog ensures only one writer commits at a time
2. **Optimistic concurrency**: Writers check for conflicts at commit time
3. **Snapshot isolation**: Readers see a consistent snapshot regardless of concurrent writes
4. **Engine-agnostic format**: Any engine can read/write the same Parquet + metadata files

### Conflict resolution

When two writers conflict:
1. First writer commits successfully
2. Second writer detects stale metadata
3. Second writer retries from latest metadata
4. If changes don't overlap (different files/partitions), retry succeeds
5. If changes overlap, operation fails and must be retried by application

### Common multi-engine patterns

| Pattern | Engines | Notes |
|---------|---------|-------|
| Spark writes, Trino reads | Spark + Trino | Most common. Spark handles ETL, Trino serves BI. |
| Flink streams, Spark compacts | Flink + Spark | Flink for real-time, Spark for maintenance. |
| Athena queries, EMR writes | Athena + EMR | Serverless queries, managed cluster writes. |
| Multiple Spark clusters | Spark + Spark | OCC handles conflicts. Use REST catalog for coordination. |
