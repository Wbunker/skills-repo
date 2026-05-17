# AWS X-Ray / Fault Injection Service — Capabilities Reference

For CLI commands, see [xray-fis-cli.md](xray-fis-cli.md).

## AWS X-Ray

**Purpose**: Distributed tracing service for analyzing and debugging distributed applications; provides end-to-end request visibility across microservices.

### Core Concepts

| Concept | Description |
|---|---|
| **Trace** | An end-to-end record of a request as it travels through all services; composed of segments |
| **Segment** | Data from one service that processed the request; includes timing, metadata, subsegments, and errors |
| **Subsegment** | Detail within a segment for a downstream call (DB query, HTTP call, AWS SDK call) |
| **Annotation** | Key-value pair indexed for filtering traces (e.g., `userId`, `environment`); queryable in console/API |
| **Metadata** | Key-value pairs not indexed; for storing additional context within a trace (not filterable) |
| **Sampling rule** | Rules defining what percentage of requests are traced; reservoir + fixed rate model |
| **Group** | A named filter expression on traces; enables separate sampling rules and metrics per group |
| **Service Map** | Visual graph of services and their connections; shows request rates, error rates, and latency |
| **X-Ray daemon** | Lightweight process that buffers segment documents from SDK and uploads to X-Ray API in batches; runs on EC2, ECS, Lambda (built-in) |
| **X-Ray SDK** | Instruments application code; available for Java, Python, Go, Node.js, Ruby, .NET |

### Instrumentation

> **Note:** The X-Ray SDK/Daemon entered maintenance mode on 2026-02-25. AWS recommends migrating to ADOT + OpenTelemetry SDKs for new instrumentation. See [adot-capabilities.md](adot-capabilities.md) for the full reference.

- **AWS SDK calls**: Automatically traced when using X-Ray SDK wrapper
- **Incoming HTTP requests**: Middleware intercepts and starts a segment per request
- **Lambda**: Active tracing enabled via function configuration; daemon pre-installed; or ADOT Lambda layer
- **ECS**: Sidecar container pattern for the X-Ray daemon; or ADOT Collector sidecar
- **OpenTelemetry (ADOT)**: `awsxray` receiver on UDP 2000 is a drop-in daemon replacement; `awsxray` exporter sends OTel spans to X-Ray — service map renders identically

### Sampling

```
Default rule: 1 reservoir (1 req/sec guaranteed) + 5% fixed rate of remaining requests
Custom rules: Define reservoir size and fixed rate per service name, URL, method, annotation
```

### Filter Expression Syntax

Used in `get-trace-summaries --filter-expression` and group definitions.

**Boolean keywords** — standalone or with `= true/false` or `!`:
`error` | `fault` | `throttle` | `partial`

**Numeric keywords** — support `=`, `!=`, `<`, `<=`, `>`, `>=`:
`responsetime` | `duration` | `http.status`

**String keywords** — support `=`, `!=`, `CONTAINS`, `BEGINSWITH`:
`http.url` | `http.method` | `user` | `name`

**Annotation keyword** — indexed, filterable:
`annotation.key = "value"` or `annotation[key.with.dots] = "value"`

**Complex keywords:**
```
service("name") { filter }        -- apply filter inside a specific service node
edge("source", "dest") { filter } -- apply filter to a specific service edge
```

**Compound operators:** `AND`, `OR`

**Examples:**
```
fault AND responsetime > 5
service("payments") { error }
annotation.version = "2.0" AND http.status = 500
edge("frontend", "api") { throttle }
!error AND http.method = "POST"
```

### X-Ray Insights

**Purpose**: Automated anomaly detection on top of trace groups — detects when a service's fault rate breaches its statistically normal band (dynamic threshold, not a static alarm).

| Aspect | Detail |
|---|---|
| **Vs. groups** | Groups are saved filter expressions; Insights operate *on top of* groups. An Insight is an auto-generated incident record; groups are just buckets |
| **Lifecycle** | Created → updated (significant change) → closed; each transition emits an EventBridge event |
| **Notifications** | Route EventBridge events to SNS, Lambda, SQS, or any target |
| **Enabling** | Per group: `InsightsEnabled=true` + optionally `NotificationsEnabled=true` in `--insights-configuration` |

### AWS Application Signals (GA 2024)

**Purpose**: CloudWatch APM layer built on X-Ray traces + CloudWatch metrics + Container Insights. Auto-instruments apps (Java, Python, Node.js) via CloudWatch agent — no code changes required.

**Relationship to X-Ray**: Consumes X-Ray trace data and correlates it with RED metrics (requests, errors, duration) to surface per-operation health. X-Ray remains the underlying trace store.

**SLO/SLI model**:

| Concept | Description |
|---|---|
| **SLI** | Availability or latency metric derived from a service operation; measured from Application Signals data |
| **SLO** | Tracks SLI attainment against a goal over a rolling or calendar window |
| **SLO types** | Period-based (time window) or request-based (ratio of good/total requests) |

### CloudWatch ServiceLens / Trace Map

ServiceLens has been merged into the CloudWatch **Trace Map** (CloudWatch console → X-Ray Traces → Trace Map). It adds CloudWatch metrics tabs, alarm overlays, Logs Insights pivots, cross-account node filtering, and SQS passive trace linking — none of which exist in the standalone X-Ray console.

See [cloudwatch-servicelens-capabilities.md](cloudwatch-servicelens-capabilities.md) for full reference including node coloring, OAM cross-account setup, passive trace linking for SQS/SNS/EventBridge, and the complete feature delta table.

### Service Integrations

**Step Functions**

| Aspect | Detail |
|---|---|
| **Enabling** | Toggle on state machine creation or update via `--tracing-configuration enabled=true` |
| **Required IAM actions** | `xray:PutTraceSegments`, `xray:PutTelemetryRecords`, `xray:GetSamplingRules`, `xray:GetSamplingTargets` |
| **Segment structure** | One segment per execution; each state transition = subsegment; each service integration (Lambda, DynamoDB, SQS…) adds its own subsegment |

**API Gateway**

| Aspect | Detail |
|---|---|
| **Active tracing** | REST APIs only (HTTP APIs have limited support); enabled per stage |
| **Trace header** | API Gateway injects `X-Amzn-Trace-Id: Root=...;Sampled=1` on all inbound requests, forwarding to backends |
| **Sampling** | Active tracing forces sampling of all requests for that stage regardless of SDK sampling rules |
| **Service map** | Shows one node per stage, one node per unique downstream URL path, connected nodes for Lambda/DynamoDB backends |

---

## AWS Fault Injection Service (FIS)

**Purpose**: Managed fault injection service for running controlled chaos engineering experiments to validate application resilience.

### Core Concepts

| Concept | Description |
|---|---|
| **Experiment template** | Defines actions, targets, stop conditions, and IAM role for a fault injection experiment |
| **Action** | A specific fault to inject (e.g., terminate EC2 instances, add CPU stress, throttle network, inject Lambda errors) |
| **Target** | AWS resources the action applies to; selected by resource type, ID, or tags; supports random selection |
| **Stop condition** | CloudWatch alarm that automatically halts the experiment if a safety threshold is breached |
| **Experiment** | A running instance of a template; generates a report with before/after observations |
| **Target account configuration** | Cross-account experiments using delegated accounts |

### Available Action Categories

- **AWS EC2**: Terminate instances, stop instances, reboot instances, CPU/memory stress, network disruption
- **AWS ECS**: Stop tasks, CPU/memory stress on containers
- **AWS EKS**: Terminate nodes, pod stress
- **AWS RDS**: Failover DB cluster, reboot DB instance
- **AWS Lambda**: Inject invocation errors, add invocation latency
- **AWS Networking**: Disrupt connectivity, route table changes
- **AWS Systems Manager**: Run stress via SSM documents (CPU, memory, disk, kill process)
