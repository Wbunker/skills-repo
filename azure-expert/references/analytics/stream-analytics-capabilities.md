# Azure Stream Analytics — Capabilities

## Service Overview

Azure Stream Analytics (ASA) is a fully managed, serverless real-time stream processing service. It uses a SQL-like query language (SAQL) to transform, filter, aggregate, and route streaming data with sub-second latency. No infrastructure management — define inputs, query, and outputs.

**Key use cases**: Real-time dashboards, anomaly detection, IoT telemetry processing, event routing, streaming ETL, fraud detection.

---

## Architecture

```
Inputs (Event Sources)          ASA Job (SAQL Query)         Outputs (Sinks)
─────────────────────          ────────────────────          ────────────────
Event Hubs  ──────────────►    SELECT, WHERE, GROUP BY  ──►  Power BI
IoT Hub     ──────────────►    Window functions         ──►  Event Hubs
Blob/ADLS   ──────────────►    JOINs, UDFs              ──►  Azure SQL Database
(reference)                    Anomaly detection         ──►  Cosmos DB
                                                         ──►  Blob Storage / ADLS
                                                         ──►  Service Bus
                                                         ──►  Azure Functions
                                                         ──►  Synapse Analytics
```

---

## Inputs

### Streaming Inputs

| Source | Description |
|---|---|
| **Azure Event Hubs** | Recommended for high-throughput streaming — Kafka-compatible endpoint supported |
| **Azure IoT Hub** | Built on Event Hubs; routes IoT device telemetry |
| **Azure Blob Storage / ADLS Gen2** | File-based streaming input (new files trigger processing) |

Configuration requires: connection, consumer group, serialization format (JSON, CSV, Avro, Parquet).

### Reference Data Inputs

Static or slowly changing data joined against the stream:

- **Blob Storage / ADLS**: Latest file in a specified path pattern (refreshed hourly or on custom schedule).
- **SQL Database**: Query refreshed on a schedule.

```sql
-- Join stream with reference data
SELECT s.DeviceId, s.Temperature, d.Location, d.AlertThreshold
FROM SensorStream s TIMESTAMP BY EventEnqueuedUtcTime
JOIN DeviceReference d ON s.DeviceId = d.DeviceId
WHERE s.Temperature > d.AlertThreshold
```

---

## SAQL (Stream Analytics Query Language)

SQL-based query language with streaming-specific extensions.

### Basic Query Pattern

```sql
SELECT
    DeviceId,
    AVG(Temperature) AS AvgTemp,
    MAX(Temperature) AS MaxTemp,
    System.Timestamp() AS WindowEnd
INTO
    OutputPowerBI
FROM
    IoTInput TIMESTAMP BY EventEnqueuedUtcTime
WHERE
    SensorType = 'temperature'
GROUP BY
    DeviceId, TumblingWindow(minute, 5)
```

### TIMESTAMP BY

Specifies which event field to use as the event time (default: arrival time):

```sql
-- Use a field in the event payload as event time
FROM MyInput TIMESTAMP BY EventTime

-- Use arrival time at Event Hubs (default if omitted)
FROM MyInput
```

---

## Windowing Functions

Core concept: aggregate streaming data over time windows.

### Tumbling Window

Non-overlapping, fixed-size time segments — each event belongs to exactly one window.

```sql
-- 5-minute tumbling window: aggregate per device per window
SELECT DeviceId, COUNT(*) AS EventCount, AVG(Value) AS AvgValue
FROM Input TIMESTAMP BY EventTime
GROUP BY DeviceId, TumblingWindow(minute, 5)
```

### Hopping Window

Fixed-size windows that overlap — events can belong to multiple windows.

```sql
-- 10-minute window, hopping every 5 minutes (50% overlap)
SELECT DeviceId, AVG(Value) AS MovingAvg
FROM Input TIMESTAMP BY EventTime
GROUP BY DeviceId, HoppingWindow(minute, 10, 5)
```

### Sliding Window

Generates output whenever an event occurs, over the trailing N duration.

```sql
-- Generate output on every event, looking back 5 minutes
SELECT DeviceId, AVG(Value) AS SlidingAvg
FROM Input TIMESTAMP BY EventTime
GROUP BY DeviceId, SlidingWindow(minute, 5)
```

### Session Window

Dynamic-sized window that closes after a gap of inactivity.

```sql
-- Group events that occur within 1 minute of each other
-- Window closes after 1 minute of silence (max 10 minutes)
SELECT SessionId, COUNT(*) AS EventCount
FROM Input TIMESTAMP BY EventTime
GROUP BY SessionId, SessionWindow(minute, 1, 10)
```

### Snapshot Window

Groups all events with the same timestamp — no time-based window.

```sql
SELECT DeviceId, SUM(Value) AS Total
FROM Input TIMESTAMP BY EventTime
GROUP BY DeviceId, System.Timestamp()
```

---

## Temporal Joins

Join two streaming inputs within a time window (both sides must be within the window duration).

```sql
-- Join orders and payments within 5 minutes of each other
SELECT o.OrderId, o.CustomerId, p.Amount, p.PaymentTime
FROM Orders o TIMESTAMP BY OrderTime
JOIN Payments p TIMESTAMP BY PaymentTime
ON o.OrderId = p.OrderId
AND DATEDIFF(minute, o, p) BETWEEN 0 AND 5
```

---

## Geospatial Functions

```sql
-- Check if device location is within a geofence
SELECT DeviceId, Latitude, Longitude
FROM Input TIMESTAMP BY EventTime
WHERE ST_Within(
    CreatePoint(Latitude, Longitude),
    CreatePolygon(
        CreatePoint(47.60, -122.35),
        CreatePoint(47.60, -122.25),
        CreatePoint(47.65, -122.25),
        CreatePoint(47.65, -122.35),
        CreatePoint(47.60, -122.35)
    )
) = 1

-- Distance between two points in meters
SELECT ST_Distance(CreatePoint(47.60, -122.35), CreatePoint(47.65, -122.25)) AS DistanceMeters
```

---

## Built-in Anomaly Detection

ML-based anomaly detection functions requiring no model training:

```sql
-- Spike and dip anomaly detection
SELECT
    DeviceId,
    Temperature,
    AnomalyDetection_SpikeAndDip(Temperature, 95, 120, 'spikesanddips')
        OVER(PARTITION BY DeviceId LIMIT DURATION(second, 120)) AS SpikeAndDipScore
FROM Input TIMESTAMP BY EventTime

-- Change point detection (detects regime changes)
SELECT
    DeviceId,
    Temperature,
    AnomalyDetection_ChangePoint(Temperature, 80, 1200)
        OVER(PARTITION BY DeviceId LIMIT DURATION(second, 1200)) AS ChangePointScore
FROM Input TIMESTAMP BY EventTime
```

---

## User-Defined Functions (UDFs)

### JavaScript UDFs

```javascript
// Custom JavaScript function
function multiply(a, b) {
    return a * b;
}
```

```sql
-- Use in SAQL query
SELECT DeviceId, udf.multiply(Value, ConversionFactor) AS ConvertedValue
FROM Input
```

### C# UDFs (Custom Deserialization)

- C# functions available in ASA with Edge and cloud deployments.
- Used for custom deserialization of non-standard message formats.

---

## Outputs

| Output | Use Case | Notes |
|---|---|---|
| **Azure Event Hubs** | Route enriched events to another hub | Fan-out pattern |
| **Azure Service Bus** | Route to queues/topics for message processing | Ordered delivery |
| **Azure SQL Database** | Persist aggregated results | Upsert support |
| **Azure Cosmos DB** | NoSQL sink with flexible schema | JSON document output |
| **Azure Blob Storage / ADLS Gen2** | Data lake sink, batch analytics | Parquet/CSV/JSON output |
| **Power BI** | Real-time streaming dataset | Live dashboard refresh |
| **Azure Synapse Analytics** | Load to dedicated or serverless SQL | COPY command optimized |
| **Azure Functions** | Custom processing/routing | Any downstream action |
| **Azure Table Storage** | Simple key-value output | Low cost |
| **Azure Data Explorer (ADX)** | Log/telemetry analytics | KQL querying |

### Power BI Output

- Creates a streaming dataset in Power BI workspace.
- Powers real-time push tiles on dashboards.
- No polling — data pushed immediately on each aggregation window.

---

## Error Handling and Output Policy

| Policy | Behavior |
|---|---|
| **Retry** (default) | Retry failed output operations indefinitely — job may fall behind |
| **Drop** | Discard events that fail output — job keeps up, events lost |

Configure per output in job settings.

---

## Compatibility Level

Version that controls query parsing behavior and feature availability:

| Level | Description |
|---|---|
| 1.0 | Legacy — for existing jobs migrated from older versions |
| 1.2 | Current recommendation — improved geo functions, null handling |

---

## Streaming Units (SUs)

Compute resource allocation for an ASA job:

- 1 SU = ~1 MB/s throughput (approximate — varies by query complexity).
- More SUs = more parallelism, higher throughput, lower latency.
- 6 SUs = minimum for production (allows partitioned query parallelism).
- **Auto-scale**: Configure min/max SUs for automatic scaling based on throughput.
- Monitor: CPU utilization, watermark delay, input/output event rate metrics.

### Query Partitioning for Scale

Partition By aligns processing with input partitions for horizontal scaling:

```sql
-- Partitioned query (scales to partition count automatically)
SELECT PartitionId, DeviceId, COUNT(*) AS Count
FROM Input PARTITION BY PartitionId
GROUP BY PartitionId, DeviceId, TumblingWindow(minute, 1)
```

---

## ASA on Edge (IoT Edge)

Deploy Stream Analytics jobs on Azure IoT Edge devices:

- Process data locally on edge device — reduce latency, reduce bandwidth.
- Same SAQL query language as cloud ASA.
- Package as IoT Edge module.
- Outputs: local storage, IoT Hub (upstream), Event Hubs.
- Use cases: local filtering before cloud upload, real-time on-device alerting.

---

## Shared vs. Dedicated Clusters

| Option | Description |
|---|---|
| **Shared (Standard)** | Multitenant — pay per SU per hour |
| **ASA Cluster (Dedicated)** | Dedicated compute for multiple jobs, private endpoints, lowest latency; minimum 36 SUs, monthly commitment |

ASA Cluster benefits:
- **Private endpoints**: Connect inputs/outputs in private VNets without public internet.
- **Custom code**: Deploy custom deserialization assemblies.
- Multiple jobs share cluster resources — consolidate small jobs.
