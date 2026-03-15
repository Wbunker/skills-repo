# AWS CloudWatch — Capabilities Reference
For CLI commands, see [cloudwatch-cli.md](cloudwatch-cli.md).

## Amazon CloudWatch

**Purpose**: Observability service providing metrics, alarms, dashboards, and monitoring for AWS resources and custom applications.

### Core Concepts

| Concept | Description |
|---|---|
| **Namespace** | Container for metrics; e.g., `AWS/EC2`, `AWS/Lambda`, `MyApp/Latency` |
| **Metric** | Time-series data point with a name, namespace, and up to 30 dimensions |
| **Dimension** | Name-value pair that identifies a specific metric (e.g., `InstanceId=i-1234`) |
| **Statistic** | Aggregation over a period: Sum, Average, Minimum, Maximum, SampleCount, percentiles |
| **Resolution** | Standard (60-second) or high-resolution (1-second) for custom metrics |
| **Alarm** | Monitors a metric or expression; transitions between OK / ALARM / INSUFFICIENT_DATA states |
| **Composite alarm** | Combines multiple alarms with AND/OR logic; reduces alarm noise |
| **Dashboard** | Customizable widgets displaying metrics, alarms, and logs; supports cross-account/region |
| **Metric math** | Perform calculations on one or more metrics (e.g., `m1/m2 * 100` for error rate percentage) |
| **Anomaly detection** | ML-based band that learns normal metric behavior; alarms when metric falls outside the band |

### Alarm Types

| Type | Description |
|---|---|
| **Static threshold** | Alarm when metric is above/below a fixed value for N out of M data points |
| **Anomaly detection** | Alarm when metric deviates from the expected band by a configurable number of standard deviations |
| **Composite alarm** | Evaluates multiple alarms with Boolean logic; a single pane for complex alert conditions |
| **Metric math alarm** | Alarm on the result of a metric expression across multiple metrics |

### Application Performance Monitoring

| Feature | Description |
|---|---|
| **Application Signals** | Automatic instrumentation for latency, error rate, and request rate KPIs; SLO tracking |
| **CloudWatch Synthetics** | Canaries (Node.js or Python scripts) that simulate user flows on a schedule; detect availability issues before users do |
| **CloudWatch RUM** | Real User Monitoring; JavaScript snippet injects telemetry into web pages; captures page load times, JS errors, HTTP errors |
| **Evidently** | Feature flags and A/B testing; control feature rollout percentages; run experiments with statistical analysis |
| **Contributor Insights** | Analyze log data to identify top-N contributors to a metric (e.g., top IPs generating 5xx errors) |
| **Lambda Insights** | Enhanced monitoring for Lambda: memory, CPU, cold starts, initialization duration; requires Lambda extension layer |
| **Container Insights** | Collect metrics and logs from ECS, EKS, and self-managed Kubernetes; cluster, service, pod, and task granularity |

### Alarm Actions

- **SNS notification** — email, SMS, webhook, Lambda, SQS
- **Auto Scaling** — scale out or in
- **EC2 actions** — stop, terminate, reboot, recover
- **Systems Manager OpsItem** — create an OpsItem for investigation

---

## Amazon CloudWatch Logs

**Purpose**: Centralized log management: ingest, store, search, and route log data from AWS services and custom applications.

### Core Concepts

| Concept | Description |
|---|---|
| **Log group** | Container for log streams sharing the same retention, encryption, and access settings |
| **Log stream** | Ordered sequence of log events from a single source (e.g., one EC2 instance, one Lambda invocation sequence) |
| **Log event** | A record with a timestamp and message |
| **Retention policy** | Per-log-group setting: 1 day to 10 years, or never expire |
| **Metric filter** | Pattern that matches log events and increments a CloudWatch metric (e.g., count ERROR occurrences) |
| **Subscription filter** | Real-time stream of filtered log events delivered to Kinesis, Kinesis Firehose, or Lambda |
| **Logs Insights** | Interactive query engine for log data; purpose-built query language |
| **Log class** | **Standard** (full features, real-time) or **Infrequent Access** (lower cost, subset of features, no live tail) |
| **Field index** | Index on specific log fields to speed up Logs Insights queries by reducing data scanned |
| **Live Tail** | Stream new log events in near-real-time in the console; filter by pattern; for active troubleshooting |
| **Data protection policy** | Automatically detect and mask sensitive data (PII, credentials) in log events |

### Logs Insights Query Syntax

```
# Basic field filtering and sorting
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20

# Aggregate stats
stats count() as errorCount by bin(5m)
| sort errorCount desc

# Parse structured logs
parse @message "* * *" as requestId, status, latency
| stats avg(latency), max(latency) by status
```

### Subscription Filter Destinations

| Destination | Use case |
|---|---|
| **Kinesis Data Streams** | Real-time processing, fan-out to multiple consumers |
| **Kinesis Data Firehose** | Near-real-time delivery to S3, Redshift, OpenSearch, Splunk |
| **AWS Lambda** | Custom real-time processing, alerting, enrichment |
| **Cross-account** | Deliver logs to a centralized logging account via resource policy |

### Export Options

- **Export to S3** (`create-export-task`): asynchronous, up to 12 hours delay; use for historical archival
- **Subscription filter to Firehose → S3**: near-real-time export with transformation
- **CloudWatch Logs Centralization**: replicate log groups across accounts and regions
