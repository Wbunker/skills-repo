# CloudWatch ServiceLens / Trace Map — Capabilities Reference

For X-Ray CLI commands that drive this feature, see [xray-fis-cli.md](xray-fis-cli.md).
For Application Signals (successor APM layer), see [cloudwatch-capabilities.md](cloudwatch-capabilities.md).

## Current Status

ServiceLens is no longer a standalone menu item. AWS merged it into the CloudWatch **Trace Map** (CloudWatch console → X-Ray Traces → Trace Map). The successor product is **CloudWatch Application Signals**, which extends Trace Map with SLOs, automated service discovery, and ADOT-native instrumentation.

> **Note:** The X-Ray SDK/Daemon entered maintenance mode on 2026-02-25. AWS recommends migrating to OpenTelemetry (ADOT) for new instrumentation.

---

## What Trace Map Adds Over X-Ray Console

| Feature | X-Ray Console | CloudWatch Trace Map |
|---|---|---|
| Service/Trace map | Yes | Yes |
| Node fill color (Green/Red/Yellow/Purple) | Yes | No (outline only) |
| CloudWatch metrics tab per node | No | Yes |
| Alarm/Alerts tab per node | No | Yes |
| Logs Insights pivot from trace | No | Yes |
| Synthetics canary nodes | No | Yes (via Preferences) |
| Cross-account node filtering | No | Yes |
| SQS linked trace dashed edge | No | Yes |
| SQS event-age histogram on edge | No | Yes |
| Group filter dropdown | Yes | Yes |

---

## Prerequisites

| Requirement | Detail |
|---|---|
| X-Ray instrumentation | X-Ray SDK + daemon, or ADOT collector with OTLP export |
| Sampling rules | Default (1 req/sec reservoir + 5% fixed rate) or custom; unsampled requests produce no data |
| IAM permissions | `xray:GetServiceGraph`, `xray:GetTraceSummaries`, `xray:BatchGetTraces`, `cloudwatch:GetMetricData`, `logs:StartQuery` |
| CloudWatch agent | Optional — needed only for custom EC2/ECS metrics in node detail panel |
| Trace ID in logs | App must emit structured logs containing `_X_AMZN_TRACE_ID` or `AWS_XRAY_TRACE_ID` for Logs Insights pivot to work |

---

## Service Map

### Node Coloring (Trace Map — outline, not fill)

| Color | Meaning |
|---|---|
| Red outline | Server faults (5xx) |
| Yellow outline | Client errors (4xx) |
| Purple outline | Throttling (HTTP 429) |
| No outline | Healthy |

### Node Sizing Options

- **Uniform** — all nodes same size
- **Health** — sized by impacted request count
- **Traffic** — sized by total request count

### Filtering

- **X-Ray Group** — select a saved group from the top-left dropdown; applies the group's filter expression to the map
- **Account** — cross-account mode; non-matching accounts are grayed out (not removed)
- **Time range** — standard CloudWatch time picker (relative or absolute)

### Node Click Behavior

Opens a detail panel with three tabs:
- **Metrics** — CloudWatch metrics for that service (Lambda: invocations/errors/throttles/duration; API GW: count/4xx/5xx/latency)
- **Alerts** — CloudWatch alarms associated with the service
- **Response Time Distribution** — histogram

Panel includes **View traces** and **View logs** buttons. Selecting an edge between two nodes shows request volume and latency for that connection. Map capacity: up to 10,000 nodes.

---

## SQS / SNS / EventBridge Passive Trace Linking

**Why X-Ray alone cannot connect async hops:** SQS/SNS/EventBridge are asynchronous — the producer and consumer are separate invocations with separate trace IDs and no continuous HTTP call to propagate a trace header in-band.

**How passive instrumentation solves this:** The queue/topic reads the `X-Amzn-Trace-Id` attribute from messages placed by an instrumented producer and propagates it to the consumer without generating its own trace segments. X-Ray links the producer and consumer traces via shared trace IDs.

**Visual representation:** Appears as a **dashed-line edge** in the Trace Map. Edge detail shows a received-event-age histogram for SQS.

**Limits:** Each segment can link to up to 20 traces; each trace up to 100 links. Exceeding limits produces incomplete traces.

**Applies to:** SQS, SNS, EventBridge, S3 (all passive).

---

## Log Correlation

From a trace detail page, "View logs" opens CloudWatch Logs Insights pre-populated with the log group associated with that service and filtered by trace ID. Requires the application to emit logs containing the trace ID field. Services without a correlated log group (e.g., DynamoDB as a downstream node) do not have a "View logs" link.

---

## Cross-Account Setup (CloudWatch OAM)

**Mechanism:** CloudWatch Observability Access Manager (OAM) — monitoring account aggregates data from source accounts.

**Setup:**
1. In the monitoring account: create a sink (CloudWatch console → Settings → Manage monitoring account); select telemetry types to share (Metrics, Log groups, X-Ray traces, Application Signals, etc.)
2. Generate a CloudFormation template or URL from the monitoring account
3. In each source account: deploy the template or use the URL to create the observability link
4. AWS Organizations can automate onboarding of new accounts

**Limits:**
- Up to 100,000 source accounts per monitoring account
- Up to 5 monitoring accounts per source account
- Scoped to a **single AWS Region** — cross-region requires separate setups per region

**Pricing:** Metrics and log group sharing is free. First trace copy to monitoring account is free; additional monitoring accounts charged per source account.

---

## Supported Services

| Service | Integration Type |
|---|---|
| AWS Lambda | Active + Passive |
| Amazon API Gateway | Active + Passive |
| Amazon SQS | Passive |
| Amazon SNS | Passive |
| Amazon EventBridge | Passive |
| Amazon S3 | Passive |
| ALB | Request tracing (header injection) |
| AWS Elastic Beanstalk | Tooling (daemon bundled) |
| Amazon EC2 | Tooling (daemon manual install) |
| Amazon ECS | Tooling (daemon as sidecar) |
| Amazon EKS | Tooling (ADOT or daemon DaemonSet) |
| AWS App Mesh / Envoy | Active |
| AWS AppSync | Active |
| AWS App Runner | Active |
| AWS Step Functions | Active |
| Amazon Bedrock AgentCore | Active |

DynamoDB, RDS, and other SDK-called services appear as **downstream nodes** derived from subsegments in the calling service's trace — they do not emit their own trace data.

---

## CLI / API

There is no `aws cloudwatch` CLI for Trace Map. All underlying data is served by X-Ray APIs — use `aws xray` commands from [xray-fis-cli.md](xray-fis-cli.md):

| API | Purpose |
|---|---|
| `get-service-graph` | Node/edge topology data that drives the map |
| `get-trace-summaries` | Trace list for a filter expression and time range |
| `batch-get-traces` | Full trace documents by trace ID |
| `get-time-series-service-statistics` | Time-series latency/error/fault/request metrics per service node |
| `get-trace-graph` | Service graph for a specific set of traces |
| `get-insight-summaries` / `get-insight` | X-Ray Insights anomaly detection data |
| `start-trace-retrieval` / `list-retrieved-traces` | Async retrieval for large trace sets |
| `create-group` / `update-group` | Manage X-Ray groups used as map filters |
