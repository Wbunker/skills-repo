# Event-driven IoT Integration — Capabilities Reference
For CLI commands, see [iot-integration-cli.md](iot-integration-cli.md).

## IoT Hub Message Routing to Event Hubs

**Purpose**: Fan out IoT device telemetry to downstream consumers at scale. IoT Hub's built-in endpoint is Event Hubs-compatible; custom routing enables parallel delivery to multiple targets.

### Built-in Event Hubs-Compatible Endpoint

- Every IoT Hub has a built-in Event Hubs-compatible endpoint at `{iot-hub}.servicebus.windows.net`
- Accessible via Event Hubs SDK, AMQP, or Kafka (IoT Hub supports Kafka protocol)
- 1–7 day message retention
- 1–32 partitions (set at creation; cannot change)
- Consumer groups for multiple independent readers

### Custom Routing to Event Hubs

```
IoT Hub → Message Route (filter condition) → Custom Event Hub Endpoint → Stream Analytics / Azure Functions / custom consumers
```

- Route filtered messages to dedicated Event Hubs per data type (alerts vs telemetry)
- Route to multiple Event Hubs in parallel using multiple routes
- No routing condition = all messages (same as fallback route)

---

## Azure Stream Analytics for IoT

**Purpose**: Real-time stream processing of IoT telemetry with SQL-like query language. Aggregates, filters, enriches, and routes IoT data without managing infrastructure.

### Key Capabilities

| Capability | Details |
|---|---|
| **Inputs** | IoT Hub, Event Hubs, Blob Storage (reference data) |
| **Outputs** | Cosmos DB, SQL Database, Blob/ADLS, Power BI, Azure Functions, Event Hubs, Service Bus, Azure Synapse |
| **Windowing** | Tumbling (non-overlapping), Hopping (overlapping), Sliding (event-driven), Session (gap-based), Snapshot |
| **Reference data** | Static lookup tables (device metadata from Blob) joined with streaming data |
| **ML scoring** | Call Azure ML endpoints from SQL query with `ML()` function |
| **Temporal joins** | Join two streams within a time window |
| **Geospatial** | Built-in geofencing and geospatial functions |
| **Compatibility levels** | 1.0, 1.1, 1.2 — affects SQL syntax and function availability |

### Common IoT Patterns

```sql
-- Alert when temperature exceeds threshold for sustained period (tumbling window)
SELECT deviceId, AVG(temperature) AS avgTemp, System.Timestamp() AS windowEnd
FROM IoTHubInput TIMESTAMP BY EventEnqueuedUtcTime
WHERE temperature > 80
GROUP BY deviceId, TumblingWindow(second, 30)
HAVING AVG(temperature) > 80

-- Count messages per device per minute (hopping window)
SELECT deviceId, COUNT(*) AS messageCount
FROM IoTHubInput
GROUP BY deviceId, HoppingWindow(second, 60, 10)

-- Detect anomalies using ML
SELECT deviceId, AnomalyDetection_SpikeAndDip(temperature, 95, 120, 'spikesanddips')
FROM IoTHubInput
GROUP BY deviceId, SlidingWindow(second, 120)
```

---

## Azure Data Explorer (ADX) for IoT Time-Series Analytics

**Purpose**: Replacement for the retired Time Series Insights (TSI). ADX provides high-performance time-series ingestion, storage, and KQL-based analytics for IoT telemetry at petabyte scale.

### Migration from Time Series Insights

- TSI was officially retired in March 2025
- ADX replaces TSI for all IoT time-series use cases
- ADX Dashboards replace TSI Explorer for visualization
- **Ingestion path**: IoT Hub → Event Hubs → ADX (via Event Hubs ingestion connector) or direct IoT Hub ingestion

### ADX for IoT Patterns

```kusto
// Average temperature by device over last 24h
Telemetry
| where timestamp > ago(24h)
| summarize avg(temperature) by deviceId, bin(timestamp, 1h)
| render timechart

// Find devices not reporting in last 10 minutes (dead device detection)
let expected = Telemetry | where timestamp > ago(1h) | summarize by deviceId;
let recent = Telemetry | where timestamp > ago(10m) | summarize by deviceId;
expected | join kind=leftanti recent on deviceId

// Anomaly detection
Telemetry
| make-series temperature=avg(temperature) on timestamp from ago(7d) to now() step 1h by deviceId
| extend anomalies = series_decompose_anomalies(temperature, 1.5, -1, 'linefit')
```

### IoT Hub to ADX Ingestion

- **Event Hubs connector**: IoT Hub built-in endpoint → ADX Event Hubs ingestion (managed, low-latency)
- **IoT Hub connector**: Native ADX connector (preview) directly from IoT Hub
- **Streaming ingestion**: <1 second latency for real-time dashboards (at higher cost)
- **Batching ingestion**: Default; optimized for throughput; ~5 minute latency

---

## Azure Functions Triggered by IoT Hub

**Purpose**: Serverless compute for processing individual IoT messages: device-to-twin updates, alert processing, device command dispatch, data enrichment.

```csharp
// IoT Hub trigger (Event Hubs trigger on built-in endpoint)
[FunctionName("ProcessIoTMessage")]
public static async Task Run(
    [EventHubTrigger("messages/events", Connection = "IoTHubConnectionString")] EventData[] events,
    [CosmosDB("iotdb", "telemetry", Connection = "CosmosDBConnection")] IAsyncCollector<dynamic> output,
    ILogger log)
{
    foreach (var eventData in events)
    {
        var messageBody = Encoding.UTF8.GetString(eventData.Body.Array);
        var telemetry = JsonConvert.DeserializeObject<TelemetryData>(messageBody);
        await output.AddAsync(telemetry);
    }
}
```

- **Batching**: Function receives array of events per invocation (checkpointing per batch)
- **Partition processing**: Each function instance processes one partition; scale up to partition count
- **IoT Hub SDKs**: Use `ServiceClient` and `RegistryManager` from within Functions to send C2D messages, update twins

---

## Azure Notification Hubs

**Purpose**: Cross-platform push notification infrastructure for mobile applications. Abstracts platform-specific notification services (APNs, FCM, WNS) behind a single API. Scale to 500M+ devices.

### Supported Platforms

| Platform | Notification Service |
|---|---|
| iOS | Apple Push Notification service (APNs) |
| Android | Firebase Cloud Messaging (FCM / FCM v1) |
| Windows | Windows Notification Service (WNS) |
| Kindle | Amazon Device Messaging (ADM) |
| Baidu | Baidu Cloud Push |

### Key Concepts

| Concept | Description |
|---|---|
| **Namespace** | Container for notification hubs; billing and quota unit |
| **Hub** | Instance within a namespace; bound to one app |
| **Registration** | Device registers its platform handle (APNs token, FCM registration ID) with the hub |
| **Installation** | Preferred over registrations; supports tags and templates; server-managed |
| **Tags** | Labels on registrations (e.g., `userId:123`, `topic:sports`) for targeted sends |
| **Templates** | Per-device message format definition; allows sending platform-agnostic payloads |
| **Scheduled notifications** | Send notifications at a future time |
| **Direct send** | Send to a specific device handle (bypasses registration) |

### Send Patterns

```
Broadcast: Send to ALL registered devices
Tag expression: Send to devices matching "tag1 && (tag2 || tag3)"
Template: Send platform-agnostic body; each device receives platform-specific format
```

---

## Azure RTOS

**Purpose**: Real-time operating system (RTOS) for microcontrollers. Microsoft's embedded OS suite for resource-constrained IoT devices.

### Components

| Component | Description |
|---|---|
| **ThreadX** | Core RTOS kernel; preemptive scheduling, priority inversion protection; certified (IEC 61508 SIL 4, DO-178C DAL A) |
| **NetX Duo** | Dual IPv4/IPv6 TCP/IP stack with TLS, MQTT, HTTP, CoAP clients |
| **FileX** | FAT-compatible file system |
| **GUIX** | Embedded GUI framework |
| **TraceX** | System-level trace visualization for debugging |
| **USBX** | USB host/device/OTG stack |

### Azure RTOS + IoT Hub Integration

- **Azure IoT C SDK**: Runs on Azure RTOS; enables MQTT connection to IoT Hub
- **Plug and Play (PnP)**: DTDL model embedding for automatic device discovery
- Eclipse ThreadX: Microsoft open-sourced Azure RTOS as Eclipse ThreadX under Eclipse Foundation

---

## MQTT Broker via Azure Event Grid Namespaces

**Purpose**: Native MQTT broker capability in Azure Event Grid Namespaces. Enables IoT devices to communicate using MQTT without IoT Hub, with Event Grid routing to cloud services.

### Key Capabilities

- MQTT v3.1.1 and v5.0 support
- Client authentication: X.509 certificates, managed identities
- Topic spaces with wildcard subscriptions
- Routing MQTT messages to Event Hubs, Service Bus, Event Grid topics for further processing
- No-code fan-out from MQTT to multiple cloud consumers
- Suitable for: B2C IoT scenarios, flexible MQTT architectures, IoT without device management needs
