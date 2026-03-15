# Streaming — Chapter 8

Spark Structured Streaming, Flink streaming, Kafka Connect, CDC patterns, and incremental reads.

## Table of Contents

- [Spark Structured Streaming](#spark-structured-streaming)
- [Apache Flink Streaming](#apache-flink-streaming)
- [Kafka Connect](#kafka-connect)
- [Change Data Capture (CDC)](#change-data-capture-cdc)
- [Incremental Reads](#incremental-reads)
- [Write-Audit-Publish with Streaming](#write-audit-publish-with-streaming)
- [Streaming Patterns](#streaming-patterns)

---

## Spark Structured Streaming

### Read from Iceberg as streaming source

```python
stream_df = spark.readStream \
    .format("iceberg") \
    .option("stream-from-timestamp", "2024-06-01T00:00:00") \
    .load("catalog.db.events")
```

Key options:

| Option | Description |
|--------|-------------|
| `stream-from-timestamp` | Start from specific timestamp |
| `from-snapshot-id` | Start from specific snapshot |
| `streaming-skip-delete-snapshots` | Skip snapshots with deletes (default false) |
| `streaming-skip-overwrite-snapshots` | Skip overwrite snapshots (default false) |

**Behavior**:
- Processes new append snapshots incrementally
- By default, fails on delete/overwrite snapshots (set skip options to ignore)
- Tracks progress via Spark checkpoints

### Write to Iceberg as streaming sink

```python
stream_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/events") \
    .trigger(processingTime="30 seconds") \
    .toTable("catalog.db.events")
```

**Trigger types**:
- `processingTime="30 seconds"` — micro-batch every 30s
- `availableNow=True` — process all available data, then stop
- `once=True` — deprecated, use `availableNow`

### Fanout writes

Write to a dynamically partitioned table from streaming:

```python
stream_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("fanout-enabled", "true") \
    .option("checkpointLocation", "/checkpoints/events") \
    .toTable("catalog.db.events")
```

`fanout-enabled=true` keeps one writer per partition open simultaneously. Uses more memory but avoids rewriting files.

## Apache Flink Streaming

### Streaming reads

```sql
-- Flink SQL: read Iceberg as streaming source
CREATE TABLE events_stream WITH (
  'connector' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'https://catalog.example.com'
) LIKE catalog.db.events;

SELECT * FROM events_stream /*+ OPTIONS('streaming'='true', 'monitor-interval'='10s') */;
```

```java
// Flink DataStream API
TableLoader tableLoader = TableLoader.fromCatalog(
    catalogLoader, TableIdentifier.of("db", "events"));

DataStream<RowData> stream = FlinkSource.forRowData()
    .tableLoader(tableLoader)
    .streaming(true)
    .monitorInterval(Duration.ofSeconds(10))
    .build();
```

### Streaming writes

```sql
-- Flink SQL: write stream to Iceberg
INSERT INTO catalog.db.events
SELECT * FROM kafka_source;
```

```java
// Flink DataStream API
FlinkSink.forRowData(stream)
    .tableLoader(tableLoader)
    .overwrite(false)
    .build();
```

### Flink upsert mode

```sql
-- Enable upsert mode for CDC streams
CREATE TABLE catalog.db.customers (
  customer_id STRING,
  name STRING,
  email STRING,
  PRIMARY KEY (customer_id) NOT ENFORCED
) WITH (
  'format-version' = '2',
  'write.upsert.enabled' = 'true'
);
```

### Dynamic sink (Flink 2.0+, Iceberg 1.10+)

```java
// Automatic schema evolution from input stream
IcebergDynamicSink.builder()
    .tableLoader(tableLoader)
    .autoEvolveSchema(true)
    .build();
```

## Kafka Connect

### Iceberg Sink Connector

```json
{
  "name": "iceberg-sink",
  "config": {
    "connector.class": "io.tabular.iceberg.connect.IcebergSinkConnector",
    "tasks.max": "4",
    "topics": "events",
    "iceberg.tables": "db.events",
    "iceberg.catalog.type": "rest",
    "iceberg.catalog.uri": "https://catalog.example.com",
    "iceberg.control.commit.interval-ms": "60000",
    "iceberg.control.commit.timeout-ms": "300000"
  }
}
```

### CDC mode with Kafka Connect

```json
{
  "config": {
    "connector.class": "io.tabular.iceberg.connect.IcebergSinkConnector",
    "topics": "dbserver.public.customers",
    "iceberg.tables": "db.customers",
    "iceberg.tables.cdc-field": "op",
    "iceberg.tables.evolve-schema-enabled": "true",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState"
  }
}
```

## Change Data Capture (CDC)

### Debezium → Iceberg pipeline

```
Source DB → Debezium → Kafka → Iceberg Sink Connector → Iceberg table
                                (upsert mode)
```

### CDC with Spark MERGE

```python
# Read CDC events from Kafka
cdc_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "dbserver.public.customers") \
    .load()

# Parse and apply changes using foreachBatch
def apply_cdc(batch_df, batch_id):
    from pyspark.sql.functions import col, from_json

    changes = batch_df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    changes.createOrReplaceTempView("changes")

    spark.sql("""
        MERGE INTO catalog.db.customers target
        USING changes source
        ON target.id = source.id
        WHEN MATCHED AND source.op = 'd'
          THEN DELETE
        WHEN MATCHED
          THEN UPDATE SET *
        WHEN NOT MATCHED AND source.op != 'd'
          THEN INSERT *
    """)

cdc_stream.writeStream \
    .foreachBatch(apply_cdc) \
    .option("checkpointLocation", "/checkpoints/cdc_customers") \
    .trigger(processingTime="30 seconds") \
    .start()
```

### CDC with Flink upsert

```sql
-- Flink CDC source (Debezium format)
CREATE TABLE cdc_source (
  id BIGINT,
  name STRING,
  email STRING,
  PRIMARY KEY (id) NOT ENFORCED
) WITH (
  'connector' = 'kafka',
  'topic' = 'dbserver.public.customers',
  'properties.bootstrap.servers' = 'broker:9092',
  'format' = 'debezium-json'
);

-- Write to Iceberg with upsert
INSERT INTO catalog.db.customers
SELECT * FROM cdc_source;
```

## Incremental Reads

Read only new data since a specific snapshot — enables efficient downstream processing.

### Spark incremental read

```python
# Read appends between two snapshots
df = spark.read \
    .format("iceberg") \
    .option("start-snapshot-id", start_id) \
    .option("end-snapshot-id", end_id) \
    .load("catalog.db.events")
```

### Streaming as incremental read

```python
# Continuously process new appends
spark.readStream \
    .format("iceberg") \
    .option("from-snapshot-id", last_processed_snapshot) \
    .load("catalog.db.events") \
    .writeStream \
    .trigger(availableNow=True) \
    .format("iceberg") \
    .toTable("catalog.db.downstream_table")
```

## Write-Audit-Publish with Streaming

Use branches to validate streaming data before publishing:

```python
# Write to a staging branch
stream_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("branch", "staging") \
    .option("checkpointLocation", "/checkpoints/staging") \
    .trigger(processingTime="1 minute") \
    .toTable("catalog.db.events")
```

```sql
-- Validate staged data
SELECT COUNT(*), MIN(event_time), MAX(event_time)
FROM catalog.db.events VERSION AS OF 'staging';

-- Fast-forward main to include staged data
CALL catalog.system.fast_forward('db.events', 'main', 'staging');
```

## Streaming Patterns

### Exactly-once ingestion from Kafka

```python
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "events") \
    .option("startingOffsets", "latest") \
    .load()

parsed = kafka_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

parsed.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/checkpoints/kafka_events") \
    .trigger(processingTime="30 seconds") \
    .toTable("catalog.db.bronze_events")
```

Exactly-once is guaranteed by Spark checkpoint + Iceberg ACID:
- Checkpoint tracks Kafka offsets
- Iceberg commit is atomic
- Retry replays from last committed offset

### Medallion architecture with Iceberg streaming

```python
# Bronze: raw ingestion
bronze_stream = spark.readStream.format("kafka")...
bronze_stream.writeStream \
    .format("iceberg") \
    .toTable("catalog.db.bronze_events")

# Silver: incremental cleaning
silver_stream = spark.readStream \
    .format("iceberg") \
    .load("catalog.db.bronze_events")

silver_stream \
    .dropDuplicates(["event_id"]) \
    .withColumn("event_date", col("event_time").cast("date")) \
    .writeStream \
    .format("iceberg") \
    .toTable("catalog.db.silver_events")

# Gold: batch aggregation (triggered)
spark.readStream \
    .format("iceberg") \
    .load("catalog.db.silver_events") \
    .groupBy("event_date", "event_type") \
    .count() \
    .writeStream \
    .format("iceberg") \
    .outputMode("complete") \
    .trigger(availableNow=True) \
    .toTable("catalog.db.gold_daily_events")
```

### Handling late data

```python
stream_df \
    .withWatermark("event_time", "1 hour") \
    .groupBy(window("event_time", "10 minutes"), "event_type") \
    .count() \
    .writeStream \
    .format("iceberg") \
    .outputMode("update") \
    .toTable("catalog.db.event_counts")
```
