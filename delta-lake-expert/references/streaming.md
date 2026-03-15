# Streaming — Chapter 7

Streaming ingestion and consumption with Delta Lake, Change Data Feed, Auto Loader, and Delta Live Tables.

## Table of Contents

- [Delta as Streaming Source](#delta-as-streaming-source)
- [Delta as Streaming Sink](#delta-as-streaming-sink)
- [Change Data Feed](#change-data-feed)
- [Auto Loader](#auto-loader)
- [Delta Live Tables](#delta-live-tables)
- [Apache Flink Integration](#apache-flink-integration)
- [Streaming Patterns](#streaming-patterns)

---

## Delta as Streaming Source

Treat a Delta table as a streaming source — automatically tracks which files have been processed:

```python
stream_df = spark.readStream \
    .format("delta") \
    .option("maxFilesPerTrigger", 100)    # rate limit by files
    .option("maxBytesPerTrigger", "10g")  # rate limit by size
    .load("/path/to/delta_table")
```

Key behaviors:
- Only processes new commits (appends) by default
- OPTIMIZE compaction files are marked `dataChange=false` and skipped
- Deletions and updates are NOT propagated (use Change Data Feed for those)
- `startingVersion` or `startingTimestamp` to control where to begin

```python
# Start from a specific version
spark.readStream.format("delta") \
    .option("startingVersion", 42) \
    .load(path)

# Start from a timestamp
spark.readStream.format("delta") \
    .option("startingTimestamp", "2024-06-01") \
    .load(path)
```

## Delta as Streaming Sink

Write streaming data to Delta with ACID guarantees:

```python
stream_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/my_stream") \
    .trigger(availableNow=True)  # process all available, then stop
    .start("/path/to/delta_table")
```

**Output modes**:
- `append` — add new rows (most common)
- `complete` — overwrite table with full result (aggregations)
- `update` — update changed rows (aggregations with watermark)

**Trigger types**:
- `processingTime="10 seconds"` — micro-batch every 10s
- `availableNow=True` — process all available data, then stop (replaces `once=True` with better parallelism)
- `continuous="1 second"` — experimental low-latency mode

**Checkpoint**: Always specify `checkpointLocation`. This tracks stream progress and enables exactly-once semantics.

## Change Data Feed

Captures row-level changes (inserts, updates, deletes) for incremental downstream processing.

### Enable

```sql
ALTER TABLE events SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
-- Or at creation:
CREATE TABLE events (...) TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
```

### Read changes (batch)

```sql
-- By version range
SELECT * FROM table_changes('events', 5, 10);

-- By timestamp range
SELECT * FROM table_changes('events', '2024-06-01', '2024-06-15');
```

### Read changes (streaming)

```python
spark.readStream.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 5) \
    .table("events")
```

### Change types

The `_change_type` column indicates the type of change:

| `_change_type` | Meaning |
|----------------|---------|
| `insert` | New row added |
| `update_preimage` | Row value before update |
| `update_postimage` | Row value after update |
| `delete` | Row removed |

Additional metadata columns: `_commit_version`, `_commit_timestamp`.

### CDF use cases

- **Incremental ETL**: Process only changed rows between silver and gold layers
- **SCD Type 2**: Use `update_preimage`/`update_postimage` to track dimension changes
- **Downstream sync**: Replicate changes to external systems (Elasticsearch, Redis, APIs)
- **Audit trail**: Complete history of every row-level change

## Auto Loader

Managed file ingestion from cloud storage (Databricks feature):

```python
spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/schema/events") \
    .option("cloudFiles.inferColumnTypes", "true") \
    .load("/landing/events/") \
    .writeStream.format("delta") \
    .option("checkpointLocation", "/checkpoints/events") \
    .option("mergeSchema", "true") \
    .trigger(availableNow=True) \
    .start("/bronze/events")
```

Key features:
- **Schema inference and evolution**: Automatically detects and adapts to schema changes
- **File notification mode**: Uses cloud events (S3 SQS, ADLS events) for efficient file discovery
- **Directory listing mode**: Polls storage periodically (no cloud setup needed)
- **Rescue data column**: Captures schema-mismatched data in `_rescued_data` rather than failing

## Delta Live Tables

Declarative pipeline framework (Databricks feature):

```python
import dlt

@dlt.table(comment="Raw events from landing zone")
def bronze_events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/landing/events/")

@dlt.table(comment="Cleaned events")
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
def silver_events():
    return dlt.read_stream("bronze_events") \
        .withColumn("event_date", col("timestamp").cast("date"))

@dlt.table(comment="Daily aggregates")
def gold_daily_events():
    return dlt.read("silver_events") \
        .groupBy("event_date", "event_type") \
        .count()
```

**SCD Type 2 with DLT**:
```python
dlt.create_streaming_table("dim_customer")

dlt.apply_changes(
    target="dim_customer",
    source="staged_changes",
    keys=["customer_id"],
    sequence_by="updated_at",
    track_history_column_list=["name", "email", "address"],
    stored_as_scd_type=2
)
```

## Apache Flink Integration

```java
// Flink Delta Sink
DataStream<RowData> stream = ...;
DeltaSink<RowData> deltaSink = DeltaSink.forRowData(
    new Path("/path/to/delta"),
    new Configuration(),
    rowType
).build();
stream.sinkTo(deltaSink);
```

Also supports Kafka Delta Ingest for direct Kafka → Delta writes without Spark.

## Streaming Patterns

### Exactly-once ingestion from Kafka

```python
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "events") \
    .load()

parsed = kafka_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

parsed.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/kafka_events") \
    .start("/bronze/events")
```

### Incremental silver layer using CDF

```python
# Read only changes from bronze
changes = spark.readStream.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", "latest") \
    .table("bronze_events")

# Apply transformations, write to silver
changes.filter(col("_change_type") != "delete") \
    .writeStream.format("delta") \
    .option("checkpointLocation", "/checkpoints/silver_events") \
    .trigger(availableNow=True) \
    .start("/silver/events")
```

### Handling late data with watermarks

```python
stream_df \
    .withWatermark("event_time", "1 hour") \
    .groupBy(window("event_time", "10 minutes"), "event_type") \
    .count() \
    .writeStream.format("delta") \
    .outputMode("update") \
    .start("/gold/event_counts")
```
