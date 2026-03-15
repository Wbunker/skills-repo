# Writing to Hudi
## Chapter 3: Write Flow, Operations, Key Generators, Schema Evolution, Bootstrapping

---

## The Write Flow (5 Phases)

Every Hudi write — upsert, insert, delete, or overwrite — passes through the same five phases:

```
Phase 1: START COMMIT
  Create <timestamp>.commit.requested on timeline
  Allocate a new instant

Phase 2: PREPARE RECORDS
  Deduplicate incoming records using precombine field
  (if two records share the same key, keep max(precombine))
  Apply schema validation

Phase 3: PARTITION RECORDS
  For each record: compute partition path + file group assignment
  Use index to look up existing record locations (for upserts)
  Assign new file groups for records with no existing location

Phase 4: WRITE TO STORAGE
  COW: read existing base file + merge + write new Parquet file
  MOR: append records to .log file

Phase 5: COMMIT CHANGES
  Write commit metadata (stats, file paths, schema) to .hoodie/
  Update index entries for newly written records
  Mark instant as completed: <timestamp>.commit (or .deltacommit)
```

---

## Write Operations

### UPSERT (default)

Update existing records; insert new ones. Uses index to distinguish.

```python
hudi_options = {
    "hoodie.table.name": "orders",
    "hoodie.datasource.write.recordkey.field": "order_id",
    "hoodie.datasource.write.partitionpath.field": "region",
    "hoodie.datasource.write.precombine.field": "updated_at",
    "hoodie.datasource.write.operation": "upsert",
}

df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://bucket/orders/")
```

### INSERT

Skip index lookup — treat all records as new. Faster than upsert; may produce duplicates if records already exist.

```python
hudi_options["hoodie.datasource.write.operation"] = "insert"
```

**Use when**: initial load, append-only topics where duplicates are impossible, benchmark testing.

### BULK_INSERT

Optimized for large initial data loads. Sorts and writes data without index lookup. No deduplication.

```python
hudi_options["hoodie.datasource.write.operation"] = "bulk_insert"
# Optionally control parallelism:
hudi_options["hoodie.bulkinsert.shuffle.parallelism"] = "200"
```

**Use when**: migrating an existing dataset to Hudi for the first time.

### DELETE

Remove records by key. Marks records as deleted in the timeline.

```python
hudi_options["hoodie.datasource.write.operation"] = "delete"
# Write a DataFrame with only the keys to delete
keys_df.write.format("hudi").options(**hudi_options).mode("append").save(path)
```

**Soft vs hard delete**: By default, Hudi "tombstones" deleted records (they appear in metadata but are filtered on read). Hard deletes are supported with additional config.

### INSERT_OVERWRITE

Overwrite all records in specific partitions. Does not use index.

```python
hudi_options["hoodie.datasource.write.operation"] = "insert_overwrite"
# Or overwrite entire table:
hudi_options["hoodie.datasource.write.operation"] = "insert_overwrite_table"
```

**Use when**: replacing stale partitions wholesale (daily ETL batch).

### MERGE INTO (Spark SQL)

SQL-level merge with fine-grained matched/not-matched control:

```sql
MERGE INTO orders AS target
USING updates AS source
ON target.order_id = source.order_id
WHEN MATCHED AND source.status = 'CANCELLED' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

---

## Key Generators

Key generators determine how Hudi constructs the record key and partition path from your DataFrame.

### SimpleKeyGenerator (default)

Single record key field, single partition field:

```python
"hoodie.datasource.write.recordkey.field": "order_id",
"hoodie.datasource.write.partitionpath.field": "order_date",
"hoodie.keygen.type": "SIMPLE"
```

### ComplexKeyGenerator

Composite key from multiple fields:

```python
"hoodie.datasource.write.recordkey.field": "order_id,line_item_id",
"hoodie.datasource.write.partitionpath.field": "region,order_date",
"hoodie.keygen.type": "COMPLEX"
```

### TimestampBasedKeyGenerator

Formats a timestamp column into the partition path:

```python
"hoodie.keygen.type": "TIMESTAMP",
"hoodie.deltastreamer.keygen.timebased.timestamp.type": "EPOCHMILLISECONDS",
"hoodie.deltastreamer.keygen.timebased.output.dateformat": "yyyy/MM/dd",
"hoodie.datasource.write.partitionpath.field": "event_time"
# Produces partitions like: 2024/01/15/
```

### CustomKeyGenerator

Mix of field types (simple, timestamp, hive-style):

```python
"hoodie.keygen.type": "CUSTOM",
"hoodie.datasource.write.recordkey.field": "id",
"hoodie.datasource.write.partitionpath.field": "ts:TIMESTAMP:yyyyMMdd,country:SIMPLE"
```

### NonPartitionedKeyGenerator

For non-partitioned tables:

```python
"hoodie.keygen.type": "NON_PARTITIONED"
```

---

## Merge Modes

Merge mode controls how incoming records are combined with existing records when keys match.

### PAYLOAD_COMBINE (default)

Uses the precombine field to pick the winning record. The record with the **highest precombine value** wins.

```python
"hoodie.datasource.write.payload.class": "org.apache.hudi.common.model.DefaultHoodieRecordPayload"
"hoodie.datasource.write.precombine.field": "updated_at"
```

### OVERWRITE_WITH_LATEST

Always use the incoming record, regardless of precombine:

```python
"hoodie.datasource.write.payload.class": "org.apache.hudi.common.model.OverwriteWithLatestAvroPayload"
```

**Use when**: source is authoritative and always sends the correct latest state.

### Custom Payload Class

Implement `HoodieRecordPayload` for arbitrary merge logic (e.g., sum financial amounts, merge JSON fields):

```java
public class MyMergePayload extends BaseAvroPayload {
    @Override
    public Option<IndexedRecord> combineAndGetUpdateValue(
        IndexedRecord currentValue, Schema schema) {
        // custom merge logic
    }
}
```

---

## Schema Evolution on Write

Hudi supports schema evolution without rewriting existing data.

### Supported Changes

| Change | Supported | Notes |
|--------|-----------|-------|
| Add nullable column | Yes | Default null for old records |
| Add column with default | Yes | v0.14+ |
| Rename column | Yes (with config) | |
| Widen type (int→long) | Yes | |
| Drop column | Yes (with config) | Old records retain dropped col |
| Narrow type | No | |
| Change partition column | No | Requires new table |

### Configuration

```python
# Enable schema evolution
"hoodie.schema.on.read.enable": "true",
"hoodie.datasource.write.reconcile.schema": "true",

# Allow column drops (optional)
"hoodie.schema.allow.auto.evolution.column.drop": "true"
```

### Schema Registry Integration

For Kafka-sourced pipelines, integrate with Confluent Schema Registry via Hudi Streamer (see `streamer.md`).

---

## Bootstrapping Existing Data

Bootstrap converts an existing Parquet table to Hudi without copying all data.

```
Existing Parquet files (terabytes)
        ↓
Bootstrap creates:
  .hoodie/ timeline with BOOTSTRAP instant
  Index entries mapping record keys → existing file locations
  New Parquet files NOT written (files referenced in-place)
        ↓
Result: Hudi table backed by original files
Future writes: Hudi write flow applies normally
```

### Bootstrap Types

**FULL_RECORD bootstrap**: copies all data — generates full Hudi files with all columns. Slower but enables all Hudi features immediately.

**METADATA_ONLY bootstrap**: keeps original files in place, adds only key metadata. Faster; existing files are read-only references.

### Bootstrap Command

```python
hudi_options = {
    "hoodie.datasource.write.operation": "bootstrap",
    "hoodie.bootstrap.base.path": "s3://bucket/existing-parquet-table/",
    "hoodie.bootstrap.keygen.class": "org.apache.hudi.keygen.SimpleKeyGenerator",
    "hoodie.datasource.write.recordkey.field": "id",
    "hoodie.datasource.write.partitionpath.field": "date",
    "hoodie.bootstrap.mode.selector": "org.apache.hudi.client.bootstrap.selector.MetadataOnlyBootstrapModeSelector",
    # Or for FULL_RECORD:
    # "hoodie.bootstrap.mode.selector": "org.apache.hudi.client.bootstrap.selector.FullRecordBootstrapModeSelector"
}

spark.emptyDataFrame.write.format("hudi") \
    .options(**hudi_options) \
    .mode("overwrite") \
    .save("s3://bucket/new-hudi-table/")
```

---

## Write Performance Tuning

| Config | Default | Guidance |
|--------|---------|---------|
| `hoodie.write.concurrency.mode` | SINGLE_WRITER | Change for multiwriter |
| `hoodie.upsert.shuffle.parallelism` | 1500 | Tune to partition count × cores |
| `hoodie.insert.shuffle.parallelism` | 1500 | Same |
| `hoodie.bulkinsert.shuffle.parallelism` | 1500 | For bulk_insert |
| `hoodie.parquet.max.file.size` | 120MB | Target base file size |
| `hoodie.parquet.small.file.limit` | 104857600 (100MB) | Files below this get merged |
| `hoodie.copyonwrite.insert.split.size` | 500000 | Records per file group for inserts |
| `hoodie.embed.timeline.server` | true | Keep true; embeds timeline server in driver |

### Avoiding Small Files

Hudi auto-packs small files by routing new inserts to existing file groups that are below `hoodie.parquet.small.file.limit`. This is automatic but depends on correct parallelism settings.

If small files are accumulating:
1. Check `hoodie.upsert.shuffle.parallelism` — too high creates too many file groups
2. Enable clustering to consolidate small files after the fact (see `maintenance.md`)
