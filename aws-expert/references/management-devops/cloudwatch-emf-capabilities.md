# AWS CloudWatch Embedded Metrics Format (EMF) — Capabilities Reference
CLI: use standard `aws logs` commands from [cloudwatch-cli.md](cloudwatch-cli.md) (`put-log-events`, `start-query`, etc.).

## What EMF Is

EMF is a JSON specification that embeds metric definitions directly inside CloudWatch Logs log events. CloudWatch Logs automatically extracts those metrics asynchronously — no separate `PutMetricData` API call, no metric filter to configure. One log line produces both a queryable log record and fully extracted CloudWatch metrics.

**Pipeline:**
1. Application writes a single-line JSON object (EMF spec) to stdout or a socket
2. That JSON enters CloudWatch Logs (via Lambda's built-in forwarding, CloudWatch Agent, or `PutLogEvents`)
3. CloudWatch Logs reads the `_aws` block, extracts each declared metric, and publishes them to CloudWatch Metrics
4. The same event is fully searchable in Logs Insights, including all non-metric properties

**Why EMF instead of `PutMetricData`:**

| | PutMetricData | EMF |
|---|---|---|
| API cost | $0.01 / 1,000 requests | $0 (log ingestion only) |
| Throttle limit | 150 TPS (standard), 1,500 TPS (high-res) | No metric API limit |
| Execution impact | Synchronous HTTPS call | Async stdout/socket write — near zero |
| Context correlation | Metric only, no log record | Metric + full request context in same event |
| High-cardinality data | Not stored with metric | Properties stored in log, queryable via Logs Insights |

Reported real-world impact: 65% reduction in metrics collection costs, plus reduced Lambda duration (blocking HTTPS replaced by `console.log`).

---

## JSON Specification

### Root object rules
- Must be valid JSON, **single line** — no embedded newlines
- Must contain a top-level `_aws` object
- Dimension and metric values must be **root-level fields** (no nested references: `"A.b"` matches literal key `"A.b"`, not `{ "A": { "b": ... } }`)
- Max event size: **1 MB**

### `_aws` metadata block

```json
{
  "_aws": {
    "Timestamp": 1574109732004,
    "CloudWatchMetrics": [
      {
        "Namespace": "MyApp",
        "Dimensions": [["Service"], ["Service", "Region"], []],
        "Metrics": [
          { "Name": "Latency", "Unit": "Milliseconds", "StorageResolution": 60 }
        ]
      }
    ]
  },
  "Service": "PaymentService",
  "Region": "us-east-1",
  "Latency": 135,
  "RequestId": "abc-123",
  "UserId": "u-999"
}
```

| `_aws` field | Type | Required | Notes |
|---|---|---|---|
| `Timestamp` | Number | Yes | Milliseconds since Unix epoch. Range: 2 weeks past – 2 hours future |
| `CloudWatchMetrics` | Array | Yes | Array of MetricDirective objects |
| `LogGroupName` | String | Agent mode only | Required when sending to CloudWatch Agent (not Lambda stdout) |

### MetricDirective object

| Field | Type | Required | Notes |
|---|---|---|---|
| `Namespace` | String | Yes | CloudWatch namespace; 1–1024 chars |
| `Dimensions` | Array of DimensionSet | Yes | 2D array; at least one entry (may include empty `[]` for aggregate) |
| `Metrics` | Array of MetricDefinition | Yes | Max **100** per MetricDirective |

### DimensionSet

An inner array of string keys. Each key must be a root-level string field.

```json
"Dimensions": [
  ["Service", "Operation"],   // creates metric with both dimensions
  ["Service"],                // creates metric with Service only
  []                          // creates aggregate metric with no dimensions
]
```

Each entry creates an **independent CloudWatch metric** with that dimension combination.
- Max **30** dimension keys per DimensionSet
- Dimension name: 1–250 chars (ASCII)
- Dimension value: 1–1024 chars

### MetricDefinition object

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `Name` | String | Yes | — | References a root-level numeric field; 1–1024 chars |
| `Unit` | String | No | `"None"` | See unit list below |
| `StorageResolution` | Integer | No | `60` | `1` = high-resolution (1-second), `60` = standard (1-minute) |

### Valid Unit values

```
Seconds  Microseconds  Milliseconds
Bytes  Kilobytes  Megabytes  Gigabytes  Terabytes
Bits  Kilobits  Megabits  Gigabits  Terabits
Percent  Count  None
Bytes/Second  Kilobytes/Second  Megabytes/Second  Gigabytes/Second  Terabytes/Second
Bits/Second  Kilobits/Second  Megabits/Second  Gigabits/Second  Terabits/Second
Count/Second
```

### Metric values

A metric value is a root-level field matching the `Name` in a MetricDefinition. It can be:
- A single number: `"Latency": 135`
- An array of up to **100** numbers (multiple data points in one event): `"Latency": [95, 102, 88, 110]`

Value range: `8.515920e-109` to `1.174271e+108`. NaN and ±Infinity are not supported.

### Properties (non-metric log context)

Any root-level field not referenced in a MetricDefinition or DimensionSet is a **property** — stored in the log event, searchable in Logs Insights, not published as a CloudWatch metric. Properties can be any JSON type including nested objects.

Use properties for high-cardinality context (RequestId, UserId, OrderId) that would create too many metric dimension combinations if used as dimensions.

---

## Limits Summary

| Constraint | Limit |
|---|---|
| Max event size | 1 MB |
| Max MetricDefinition objects per MetricDirective | 100 |
| Max DimensionSets per MetricDirective | 30 |
| Max dimension keys per DimensionSet | 30 |
| Max array values per metric key | 100 |
| Namespace length | 1–1024 chars |
| Metric name length | 1–1024 chars (SDKs enforce 1–255) |
| Dimension name / value length | 1–250 / 1–1024 chars |
| Timestamp range | 2 weeks past – 2 hours future |
| StorageResolution | `1` (high-res) or `60` (standard) |

---

## Complete Examples

### Minimal

```json
{"_aws":{"Timestamp":1574109732004,"CloudWatchMetrics":[{"Namespace":"MyApp","Dimensions":[["Service"]],"Metrics":[{"Name":"Latency","Unit":"Milliseconds"}]}]},"Service":"OrderService","Latency":100,"RequestId":"abc-123"}
```

### Multi-metric, multiple dimension sets, with properties

```json
{
  "_aws": {
    "Timestamp": 1574109732004,
    "CloudWatchMetrics": [{
      "Namespace": "MyApp/API",
      "Dimensions": [["Service", "Operation"], ["Service"], []],
      "Metrics": [
        { "Name": "ProcessingLatency", "Unit": "Milliseconds", "StorageResolution": 60 },
        { "Name": "ErrorCount", "Unit": "Count" }
      ]
    }]
  },
  "Service": "PaymentService",
  "Operation": "ProcessPayment",
  "ProcessingLatency": 135,
  "ErrorCount": 0,
  "UserId": "u-123456",
  "OrderId": "ord-789abc"
}
```

### High-resolution metric

```json
{
  "_aws": {
    "Timestamp": 1574109732004,
    "CloudWatchMetrics": [{
      "Namespace": "MyApp",
      "Dimensions": [["Host"]],
      "Metrics": [{ "Name": "CpuUsage", "Unit": "Percent", "StorageResolution": 1 }]
    }]
  },
  "Host": "i-1234567890",
  "CpuUsage": 72.5
}
```

### Array of metric values (multiple data points per event)

```json
{
  "_aws": {
    "Timestamp": 1574109732004,
    "CloudWatchMetrics": [{
      "Namespace": "MyApp",
      "Dimensions": [["Service"]],
      "Metrics": [{ "Name": "RequestLatency", "Unit": "Milliseconds" }]
    }]
  },
  "Service": "OrderService",
  "RequestLatency": [45, 62, 38, 91, 55]
}
```

### Agent mode (requires `LogGroupName`)

```json
{
  "_aws": {
    "Timestamp": 1574109732004,
    "LogGroupName": "my-app-metrics",
    "CloudWatchMetrics": [{
      "Namespace": "MyApp",
      "Dimensions": [["Operation"]],
      "Metrics": [{ "Name": "Latency", "Unit": "Milliseconds" }]
    }]
  },
  "Operation": "Aggregator",
  "Latency": 100
}
```

---

## SDK Libraries

### Node.js / TypeScript: `aws-embedded-metrics`

```bash
npm install aws-embedded-metrics
```

**Version note:** Use 4.1.1+, 3.0.2+, or 2.0.7+ for Lambda with JSON log format — earlier versions cause metric loss.

#### `metricScope` decorator (recommended for Lambda)

```javascript
const { metricScope, Unit, StorageResolution } = require("aws-embedded-metrics");

exports.handler = metricScope(metrics =>
  async (event, context) => {
    metrics.setNamespace("MyApp/Orders");
    metrics.putDimensions({ Environment: "prod", FunctionName: context.functionName });
    metrics.putMetric("OrderDuration", Date.now() - start, Unit.Milliseconds, StorageResolution.Standard);
    metrics.putMetric("OrdersProcessed", 1, Unit.Count);
    // Properties: in logs, not in metrics
    metrics.setProperty("RequestId", context.awsRequestId);
    metrics.setProperty("OrderId", event.orderId);
  });
```

#### `createMetricsLogger` (manual flush, non-Lambda)

```javascript
const { createMetricsLogger, Unit } = require("aws-embedded-metrics");

const metrics = createMetricsLogger();
metrics.setNamespace("MyApp");
metrics.putDimensions({ Service: "Aggregator" });
metrics.putMetric("ProcessingLatency", 100, Unit.Milliseconds);
metrics.setProperty("RequestId", "422b1569");
await metrics.flush();
```

#### MetricsLogger API

| Method | Description |
|---|---|
| `putMetric(name, value, unit?, resolution?)` | Add a metric; calling same name multiple times appends array values |
| `setProperty(key, value)` | Add log context (not a metric); value can be any type including object |
| `putDimensions(Record<string,string>)` | Add a dimension set (additive) |
| `setDimensions(dims \| dims[], useDefault?)` | Override all dimensions; `useDefault=false` removes SDK-injected defaults |
| `resetDimensions(useDefault)` | Clear all custom dimensions |
| `setNamespace(string)` | Set CloudWatch namespace |
| `setTimestamp(Date \| number)` | Set event timestamp |
| `flush()` | Write EMF JSON, reset metric values; namespace and default dims preserved |

#### Environment variables (Node.js)

| Variable | Description | Default |
|---|---|---|
| `AWS_EMF_ENVIRONMENT` | Override env detection: `Local`, `Lambda`, `Agent`, `EC2`, `ECS` | Auto-detect |
| `AWS_EMF_AGENT_ENDPOINT` | Agent endpoint URI | `tcp://127.0.0.1:25888` |
| `AWS_EMF_NAMESPACE` | CloudWatch namespace | `aws-embedded-metrics` |
| `AWS_EMF_LOG_GROUP_NAME` | Destination log group (agent mode) | `<ServiceName>-metrics` |
| `AWS_EMF_SERVICE_NAME` | Override service name | Auto-detected |
| `AWS_EMF_ENABLE_DEBUG_LOGGING` | Enable debug logging | `false` |

---

### Python: `aws-embedded-metrics`

```bash
pip3 install aws-embedded-metrics
```

#### `@metric_scope` decorator

```python
from aws_embedded_metrics import metric_scope
from aws_embedded_metrics.storage_resolution import StorageResolution

@metric_scope
def handler(event, context, metrics):
    metrics.set_namespace("MyApp/Service")
    metrics.put_dimensions({"Service": "Aggregator"})
    metrics.put_metric("ProcessingLatency", 100, "Milliseconds", StorageResolution.STANDARD)
    metrics.put_metric("Memory.HeapUsed", 1600424.0, "Bytes", StorageResolution.HIGH)
    metrics.set_property("AccountId", context.invoked_function_arn.split(":")[4])
    metrics.set_property("RequestId", context.aws_request_id)
```

#### MetricsLogger API (Python)

| Method | Description |
|---|---|
| `put_metric(key, value, unit="None", storage_resolution=60)` | Add a metric |
| `set_property(key, value)` | Add log context |
| `put_dimensions(Dict[str,str])` | Add a dimension set |
| `set_dimensions(*dicts, use_default=False)` | Override all dimensions |
| `set_namespace(str)` | Set namespace |
| `set_timestamp(datetime)` | Set timestamp |
| `flush()` | Write and reset; use `flush_preserve_dimensions=True` to keep custom dims |

---

### Java: `aws-embedded-metrics-java`

```xml
<dependency>
  <groupId>software.amazon.cloudwatchlogs</groupId>
  <artifactId>aws-embedded-metrics</artifactId>
</dependency>
```

```java
MetricsLogger metrics = new MetricsLogger();
metrics.putDimensions(DimensionSet.of("Service", "Aggregator"));
metrics.putDimensions(new DimensionSet());  // aggregate (no dimensions)
metrics.putMetric("ProcessingLatency", 100, Unit.MILLISECONDS, StorageResolution.STANDARD);
metrics.putProperty("RequestId", "422b1569");
metrics.flush();

// Graceful shutdown (non-Lambda) — Java buffers async, must drain
environment.getSink().shutdown().orTimeout(10_000L, TimeUnit.MILLISECONDS);
```

---

### .NET / C#: `Amazon.CloudWatch.EMF`

```bash
dotnet add package Amazon.CloudWatch.EMF
```

```csharp
using (var logger = new MetricsLogger()) {  // IDisposable — flushes on Dispose
    var dims = new DimensionSet();
    dims.AddDimension("Service", "aggregator");
    logger.SetDimensions(dims);
    logger.PutMetric("ProcessingLatency", 100, Unit.MILLISECONDS, StorageResolution.STANDARD);
    logger.PutProperty("RequestId", "422b1569");
}

// ASP.NET Core
services.AddEmf();          // DI registration
app.UseEmfMiddleware();     // auto-adds per-request metrics
```

---

## Transport by Environment

### Lambda — no agent needed

Lambda captures stdout and forwards to CloudWatch Logs. SDKs auto-detect Lambda via `AWS_LAMBDA_FUNCTION_NAME` and write to stdout. No `LogGroupName` required in the JSON.

### EC2 / ECS / Kubernetes — CloudWatch Agent required

Application writes to a TCP or UDP socket; CloudWatch Agent listens on **port 25888** and batches events to CloudWatch Logs.

```
AWS_EMF_AGENT_ENDPOINT=tcp://127.0.0.1:25888   # or udp://
```

**Minimum agent version:** 1.230621.0

### Minimal CloudWatch Agent config for EMF

```json
{
  "logs": {
    "metrics_collected": {
      "emf": { }
    }
  }
}
```

### ECS sidecar (awsvpc / host networking)

```json
{
  "containerDefinitions": [
    {
      "name": "webapp",
      "environment": [{ "name": "AWS_EMF_AGENT_ENDPOINT", "value": "tcp://127.0.0.1:25888" }]
    },
    {
      "name": "cwagent",
      "image": "public.ecr.aws/cloudwatch-agent/cloudwatch-agent:latest",
      "portMappings": [{ "protocol": "tcp", "containerPort": 25888 }],
      "environment": [{ "name": "CW_CONFIG_CONTENT", "valueFrom": "cwagentconfig" }]
    }
  ]
}
```

For ECS bridge networking: use container links and `tcp://cwagent:25888`.

### Send EMF manually via UDP (netcat)

```bash
echo '{"_aws":{"Timestamp":1574109732004,"LogGroupName":"my-log-group","CloudWatchMetrics":[{"Namespace":"MyApp","Dimensions":[["Operation"]],"Metrics":[{"Name":"Latency","Unit":"Milliseconds"}]}]},"Operation":"Test","Latency":50}' \
  | nc -u -q1 127.0.0.1 25888
```

`LogGroupName` inside `_aws` is required when sending to the agent.

---

## SDK Auto-Detected Default Dimensions

SDKs inject environment-specific dimensions automatically. Use `setDimensions(yourDims)` without `useDefault=true` to remove them.

| Environment | Default dimensions |
|---|---|
| Lambda | `ServiceName` (function name), `ServiceType` (`AWS::Lambda::Function`), `LogGroup` |
| ECS | `ServiceName`, `ServiceType`, `ClusterName`, `TaskId` |
| EC2 | `ServiceName`, `ServiceType`, `InstanceId`, `ImageId` |
| Generic | `ServiceName`, `ServiceType`, `LogGroup` |

---

## Common Patterns

### High-cardinality context via properties (not dimensions)

```javascript
// WRONG: each unique RequestId creates a separate metric series
metrics.putDimensions({ Service: "PaymentService", RequestId: context.awsRequestId });

// RIGHT: low-cardinality dimension, high-cardinality data as property
metrics.putDimensions({ Service: "PaymentService" });
metrics.setProperty("RequestId", context.awsRequestId);
metrics.setProperty("UserId", event.userId);
```

### Per-endpoint + aggregate dimension sets

```javascript
metrics.setDimensions(
  { Environment: "prod", Endpoint: event.path },  // per-endpoint metric
  { Environment: "prod" }                          // aggregate metric
);
metrics.putMetric("Latency", duration, Unit.Milliseconds);
```

### Lambda cold start detection

```javascript
let isColdStart = true;

exports.handler = metricScope(metrics => async (event, context) => {
  metrics.putMetric("ColdStart", isColdStart ? 1 : 0, Unit.Count);
  metrics.setProperty("IsColdStart", isColdStart);
  isColdStart = false;
});
```

### Error tracking with status code dimension

```javascript
metrics.putDimensions({ Service: "OrderService", StatusCode: String(responseCode) });
metrics.putMetric("RequestCount", 1, Unit.Count);
metrics.putMetric("ErrorCount", responseCode >= 500 ? 1 : 0, Unit.Count);
```

---

## Logs Insights Integration

EMF properties that are not metrics are stored in the log event and fully queryable:

```
# Slow request investigation
filter ProcessingLatency > 500 and Service = "OrderService"
| fields RequestId, UserId, OrderId, ProcessingLatency, @timestamp
| sort ProcessingLatency desc

# P99 latency by service
stats pct(ProcessingLatency, 99) as p99, avg(ProcessingLatency) as avg by Service

# Error analysis by endpoint
filter ErrorCount > 0
| stats count() as Total by Endpoint, StatusCode
| sort Total desc
```

**Monitoring EMF health:** extraction errors appear in namespace `AWS/Logs` as `EMFValidationErrors` and `EMFParsingErrors` — set alarms on these in production.
