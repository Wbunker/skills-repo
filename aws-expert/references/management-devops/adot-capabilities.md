# AWS Distro for OpenTelemetry (ADOT) — Capabilities Reference

For CLI commands (EKS add-on, Lambda layer), see [adot-cli.md](adot-cli.md).
For X-Ray traces, see [xray-fis-capabilities.md](xray-fis-capabilities.md).
For CloudWatch EMF metrics, see [cloudwatch-emf-capabilities.md](cloudwatch-emf-capabilities.md).
For AMP integration, see [observability-monitoring-capabilities.md](observability-monitoring-capabilities.md).

## What ADOT Is

ADOT is a secure, AWS-supported **distribution** of the CNCF OpenTelemetry project — not a fork. It tracks upstream OTel and adds:
- AWS-specific receivers and exporters (X-Ray, CloudWatch EMF, AMP)
- AWS resource detectors (EC2, ECS, EKS, Lambda metadata auto-injection)
- X-Ray trace ID format propagation (`awsxray` propagator)
- SigV4 authentication for AWS service calls
- Pre-validated, security-patched collector builds
- Lambda layers and EKS managed add-on packaging

> **Why this matters:** The X-Ray SDK/Daemon entered **maintenance mode on 2026-02-25**. ADOT + OTel SDKs is the recommended path for all new instrumentation.

ADOT enables "instrument once, export anywhere" — the same OTel instrumentation can simultaneously send to X-Ray, CloudWatch, Prometheus, Datadog, and any OTLP-compatible backend.

---

## Components

### ADOT Collector

A distribution of the upstream OTel Collector binary with AWS-specific components compiled in. Runs as a standalone process, Docker container, DaemonSet, sidecar, or Lambda layer. Primary deployment artifact.

**Image:** `public.ecr.aws/aws-observability/aws-otel-collector:latest`

### ADOT SDKs

AWS augmentations on top of standard OTel language SDKs. Not replacement SDKs — they add AWS propagators, resource detectors, and X-Ray ID generators. Supported languages: **Java, Python, Node.js, .NET, Go** (Ruby uses community OTel with AWS exporters).

---

## Collector Pipeline Architecture

`receivers → processors → exporters` with extensions providing cross-cutting services.

### Receivers

| Receiver | Purpose |
|---|---|
| `otlp` | gRPC (4317) and HTTP (4318) — primary OTLP ingestion |
| `awsxray` | UDP 2000 — drop-in replacement for X-Ray daemon; accepts existing X-Ray SDK traffic |
| `prometheus` | Scrapes Prometheus `/metrics` endpoints |
| `awscontainerinsightreceiver` | EKS/ECS infrastructure metrics (CPU, memory, network) |
| `awsecscontainermetricsreceiver` | ECS task/container metrics |
| `statsd` | StatsD UDP metrics |
| `filelog` | Log file tailing |
| `zipkin` / `jaeger` | Alternative trace formats |

### Processors

| Processor | Purpose |
|---|---|
| `batch` | Groups telemetry to reduce API calls; configure `timeout` and `send_batch_size` |
| `memory_limiter` | Prevents OOM; drops data when memory threshold exceeded — put first in pipeline |
| `resourcedetection` | Auto-injects resource attributes (EC2 ID, ECS task ARN, K8s node, Lambda function name) |
| `attributes` | Add/modify/delete span or metric attributes |
| `filter` | Drop or allow telemetry by attribute criteria |
| `k8sattributes` | Enriches with Kubernetes pod/namespace/deployment metadata |
| `tailsampling` | Tail-based sampling decisions after full trace assembly |
| `metricstransform` | Rename metrics, add/remove labels |

### Exporters

| Exporter | Destination |
|---|---|
| `awsxray` | AWS X-Ray |
| `awsemf` | CloudWatch Logs in EMF format → CloudWatch Metrics |
| `prometheusremotewrite` | AMP or any Prometheus remote-write endpoint |
| `awscloudwatchlogs` | CloudWatch Logs directly |
| `otlp` / `otlphttp` | Any OTLP-compatible backend |
| `prometheus` | Exposes a Prometheus scrape endpoint for pull-based collection |
| `datadog` | Datadog APM/metrics |
| `loadbalancing` | Routes to multiple backends by trace ID |

### Extensions

`health_check`, `pprof`, `zpages`, `sigv4auth`, `awsproxy` (X-Ray remote sampling proxy), `ecsobserver`, `filestorage`

### Sample config.yaml

```yaml
extensions:
  health_check:

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  awsxray:
    endpoint: 0.0.0.0:2000
    transport: udp

processors:
  memory_limiter:
    limit_mib: 512
    spike_limit_mib: 128
    check_interval: 5s
  batch/traces:
    timeout: 1s
    send_batch_size: 50
  batch/metrics:
    timeout: 60s

exporters:
  awsxray:
    region: us-east-1
  awsemf:
    region: us-east-1
    namespace: MyApp/Metrics
    log_group_name: /aws/myapp/metrics

service:
  pipelines:
    traces:
      receivers: [otlp, awsxray]
      processors: [memory_limiter, batch/traces]
      exporters: [awsxray]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch/metrics]
      exporters: [awsemf]
  extensions: [health_check]
```

---

## Deployment Patterns

### EKS

| Mode | Use case |
|---|---|
| **DaemonSet** | Infrastructure metrics via `awscontainerinsightreceiver`; one collector per node |
| **Deployment** | Centralized collector for application traces/metrics |
| **Sidecar** | Per-pod collection; defined via `OpenTelemetryCollector` CRD with `mode: sidecar` |
| **EKS Managed Add-on** | Installs the ADOT Operator (Kubernetes controller); operator manages `OpenTelemetryCollector` CRDs |

EKS managed add-on prerequisites:
- Kubernetes 1.21+
- cert-manager (for admission webhook TLS)
- IRSA configured for the collector's service account

### ECS

Sidecar pattern — ADOT Collector runs as a second container in the same task definition. App containers send to `localhost:4317`.

```json
{
  "name": "aoc-collector",
  "image": "public.ecr.aws/aws-observability/aws-otel-collector:latest",
  "user": "root",
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/adot-collector",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs"
    }
  }
}
```

### EC2

Install from RPM/Deb package or run the Docker image as a standalone process.

### Lambda

Attach the ADOT Lambda layer to the function. Enable auto-instrumentation via environment variable — **no code changes required**.

**Layer ARN format:**
```
arn:aws:lambda:<region>:901920570463:layer:aws-otel-<lang>-wrapper-<arch>-ver-<version>:<layer-version>
```
Account `901920570463` is the ADOT layer publisher account (consistent across all regions).

**Auto-instrumentation env vars:**

| Runtime | `AWS_LAMBDA_EXEC_WRAPPER` value |
|---|---|
| Python, Node.js | `/opt/otel-instrument` |
| Java (standard handler) | `/opt/otel-handler` |
| Java (proxy/stream/SQS) | `/opt/otel-proxy-handler` / `/opt/otel-stream-handler` / `/opt/otel-sqs-handler` |

Supported runtimes: Java 8/11/17, Python (multiple), Node.js, .NET.

Disable Application Signals: `OTEL_AWS_APPLICATION_SIGNALS_ENABLED=false`

---

## X-Ray Integration

### Replacing the X-Ray Daemon

The `awsxray` receiver listens on UDP 2000 — same address and port as the X-Ray daemon. Point existing X-Ray SDK agents at the ADOT Collector without any SDK change.

### Trace ID Format

X-Ray uses a custom format: `1-{unix-hex-time}-{96-bit-id}` (e.g., `1-5759e988-bd862e3fe1be46a994272793`).
W3C TraceContext uses a 128-bit hex ID. The ADOT `awsxray` propagator handles conversion transparently.

**Important:** X-Ray rejects trace IDs older than 30 days.

### X-Ray Sampling Rules

Supported via the `awsproxy` extension, which proxies sampling rule requests to the X-Ray API. OTel SDKs can use centrally managed X-Ray sampling rules without a direct X-Ray SDK dependency.

### Mixed Environments

In environments where some services still use X-Ray SDK, configure both propagators:
```
OTEL_PROPAGATORS=tracecontext,baggage,xray
```

---

## CloudWatch Integration (`awsemf` Exporter)

Writes OTel metrics to CloudWatch Logs in EMF format. CloudWatch automatically extracts them into CloudWatch Metrics.

```yaml
exporters:
  awsemf:
    region: us-east-1
    namespace: MyApp/Metrics
    log_group_name: /aws/myapp/metrics
    log_stream_name: otel-stream
    log_retention: 30
    dimension_rollup_option: "ZeroAndSingleDimensionRollup"
    # Options: ZeroAndSingleDimensionRollup | SingleDimensionRollupOnly | NoDimensionRollup
```

Flow: OTel SDK → OTLP → Collector → `awsemf` exporter → CloudWatch Logs → CloudWatch Metrics

---

## AMP Integration (`prometheusremotewrite` Exporter)

```yaml
extensions:
  sigv4auth:
    service: "aps"
    region: "us-east-1"

exporters:
  prometheusremotewrite:
    endpoint: "https://<workspace-id>.aps-workspaces.<region>.amazonaws.com/workspaces/<id>/api/v1/remote_write"
    auth:
      authenticator: sigv4auth

service:
  extensions: [sigv4auth]
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheusremotewrite]
```

---

## IAM Requirements

| Exporter / Use case | Required IAM actions |
|---|---|
| `awsxray` | `xray:PutTraceSegments`, `xray:PutTelemetryRecords`, `xray:GetSamplingRules`, `xray:GetSamplingTargets`, `xray:GetSamplingStatisticSummaries` |
| `awsemf` | `logs:PutLogEvents`, `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:DescribeLogStreams`, `logs:DescribeLogGroups`, `logs:PutRetentionPolicy` |
| `prometheusremotewrite` (AMP) | `aps:RemoteWrite` |
| X-Ray sampling proxy (`awsproxy`) | `xray:GetSamplingRules`, `xray:GetSamplingTargets` |
| SSM config provider | `ssm:GetParameters` |

All resource scopes are `"*"` in the baseline ADOT policy.

---

## Migration from X-Ray SDK

| Aspect | X-Ray SDK | ADOT + OTel SDK |
|---|---|---|
| Trace propagation header | `X-Amzn-Trace-Id` (X-Ray format) | W3C `traceparent` + `awsxray` propagator |
| Segment creation API | `AWSXRay.beginSegment()` / `endSegment()` | `Tracer.startSpan()` / `span.end()` |
| Daemon/collector address | X-Ray daemon UDP 2000 | ADOT Collector OTLP 4317 or UDP 2000 |
| Sampling config | X-Ray sampling rules (direct SDK) | X-Ray sampling rules via `awsproxy` extension |
| X-Ray console service map | Native | Identical — `awsxray` exporter translates OTel spans to X-Ray segments |
| Dependency | `aws-xray-sdk-*` | `opentelemetry-sdk` + AWS OTel components |
