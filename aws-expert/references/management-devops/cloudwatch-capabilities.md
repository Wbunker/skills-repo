# AWS CloudWatch — Capabilities Reference
For CLI commands, see [cloudwatch-cli.md](cloudwatch-cli.md).
For full alarm coverage (all types, actions, composite, suppressor, mute rules, SLOs, pricing), see [cloudwatch-alarms-capabilities.md](cloudwatch-alarms-capabilities.md).

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

See [cloudwatch-alarms-capabilities.md](cloudwatch-alarms-capabilities.md) for full alarm reference.

| Type | Description |
|---|---|
| **Static threshold** | Alarm when metric is above/below a fixed value for N out of M data points |
| **Anomaly detection** | ML-based; alarm when metric deviates from expected band by N standard deviations |
| **Composite alarm** | Evaluates multiple alarms with Boolean logic (`AND`/`OR`/`AT_LEAST`); reduces noise |
| **Metric math alarm** | Alarm on the result of an expression across multiple metrics |
| **Metrics Insights** | SQL-based; dynamically tracks new resources matching a query |
| **PromQL** | Monitors metrics ingested via CloudWatch OTLP endpoint |

### Application Performance Monitoring

| Feature | Description |
|---|---|
| **Application Signals** | Automatic instrumentation for latency, error rate, and request rate KPIs; SLO tracking |
| **CloudWatch Synthetics** | Canaries (Node.js or Python scripts) that simulate user flows on a schedule; detect availability issues before users do. See [cloudwatch-synthetics-capabilities.md](cloudwatch-synthetics-capabilities.md) for full reference. |
| **CloudWatch RUM** | Real User Monitoring; JavaScript snippet injects telemetry into web pages; captures page load times, JS errors, HTTP errors |
| **Evidently** | Feature flags and A/B testing; control feature rollout percentages; run experiments with statistical analysis |
| **Contributor Insights** | Analyze log data to identify top-N contributors to a metric (e.g., top IPs generating 5xx errors) |
| **Lambda Insights** | Enhanced monitoring for Lambda: memory, CPU, cold starts, initialization duration; requires Lambda extension layer |
| **Container Insights** | Collect metrics and logs from ECS, EKS, and self-managed Kubernetes; cluster, service, pod, and task granularity |

### Alarm Actions

- **SNS notification** — email, SMS, webhook, Lambda, SQS
- **Lambda** — invoke directly (contributor-level for Metrics Insights/PromQL alarms)
- **Auto Scaling** — scale out or in (metric alarms only; re-fires every minute while in ALARM)
- **EC2 actions** — stop, terminate, reboot, recover (metric alarms only)
- **Systems Manager OpsItem** — create an OpsItem for investigation
- **Incident Manager** — trigger a response plan
- **CloudWatch Investigations (Amazon Q)** — AI-powered incident investigation

See [cloudwatch-alarms-capabilities.md](cloudwatch-alarms-capabilities.md) for full action support matrix, mute rules, and suppressor alarms.

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
| **Metric filter** | Pattern that matches log events and increments a CloudWatch metric; forward-looking only; max 100/log group. See [cloudwatch-metric-filters-capabilities.md](cloudwatch-metric-filters-capabilities.md) for full reference. |
| **Subscription filter** | Real-time stream of filtered log events delivered to Kinesis, Kinesis Firehose, or Lambda |
| **Logs Insights** | Interactive query engine; supports CWLI, OpenSearch PPL, and OpenSearch SQL; pay per byte scanned. See [cloudwatch-logs-insights-capabilities.md](cloudwatch-logs-insights-capabilities.md) for full reference. |
| **Log class** | **Standard** (full features, real-time) or **Infrequent Access** (lower cost, subset of features, no live tail) |
| **Field index** | Index on specific log fields to speed up Logs Insights queries by reducing data scanned |
| **Live Tail** | Stream new log events in near-real-time in the console; filter by pattern; for active troubleshooting |
| **Data protection policy** | Automatically detect and mask sensitive data (PII, credentials) in log events |

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
