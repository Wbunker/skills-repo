# Cloud Trace & Cloud Profiler — Capabilities

## Cloud Trace

### Purpose

Distributed tracing system for collecting, analyzing, and visualizing latency data from applications. Cloud Trace tracks how requests propagate through microservices and identifies latency bottlenecks. Integrates with Cloud Logging (correlated logs), Cloud Monitoring (metrics), and supports OpenTelemetry for vendor-neutral instrumentation.

### Core Concepts

| Concept | Description |
|---|---|
| Trace | Complete record of a request's journey across services; identified by a trace ID |
| Span | Single operation within a trace (HTTP call, DB query, function execution); has start time and duration |
| Root span | First span in a trace; represents the top-level request |
| Child span | Span nested under another span; represents downstream calls |
| Trace ID | 128-bit hex identifier propagated across service boundaries via HTTP headers |
| Span ID | 64-bit hex identifier for an individual span |
| W3C Trace Context | Standard HTTP header format (`traceparent`, `tracestate`) for propagating trace context |
| Trace sampling | Fraction of requests traced (1/QPS, or configurable percentage); reduce overhead |
| Latency distribution | Histogram of request latency across all traced requests; p50/p95/p99 percentiles |
| Analysis report | Comparison of latency distributions between time periods or request types |

### Auto-Instrumentation (GCP Services)

These GCP services automatically send traces to Cloud Trace without code changes:
- **App Engine (Standard and Flexible)**: all inbound HTTP requests traced
- **Cloud Run**: request traces automatically captured; latency visible per revision
- **Cloud Functions**: function invocations traced
- **Cloud Endpoints / API Gateway**: API call traces

### Manual Instrumentation

For non-auto-instrumented services (GCE, GKE, custom backends):

**OpenTelemetry (recommended):**
```python
# Python — OpenTelemetry with Google Cloud exporter
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

def handle_request(request):
    with tracer.start_as_current_span("process-order") as span:
        span.set_attribute("order.id", request.order_id)
        result = process_order(request)
        span.set_attribute("order.status", result.status)
        return result
```

**Cloud Trace Client Library:**
```python
# Python — Cloud Trace v2 client library
from google.cloud import trace_v2
client = trace_v2.TraceServiceClient()
# Build and send trace manually (lower level; prefer OTel)
```

**Supported Languages**: Go, Java, Python, Node.js, Ruby, PHP, C#

### Trace Propagation

For distributed tracing to work across services, the trace context must be propagated:
- **W3C Trace Context** (recommended): `traceparent` and `tracestate` headers
- **B3 propagation** (legacy Zipkin): `X-B3-TraceId`, `X-B3-SpanId`, `X-B3-Sampled`
- **Cloud Trace format**: `X-Cloud-Trace-Context: TRACE_ID/SPAN_ID;o=TRACE_TRUE`

OpenTelemetry propagators handle this automatically when configured.

### Trace Analysis Features

- **Latency distribution view**: scatter plot and histogram of request latency; identify outliers
- **Analysis reports**: compare latency between date ranges, revisions, or URL patterns
- **Heatmap**: visualize latency trends over time
- **Trace details**: waterfall diagram of spans; identify which span contributes most to latency
- **Log correlation**: linked log entries appear in trace timeline (requires same `trace` field in log entry)

### Integration with Cloud Logging

When a Cloud Run or GKE application sets the `trace` field on log entries:
```json
{
  "message": "Processing order",
  "trace": "projects/my-project/traces/abc123def456",
  "span_id": "span12345",
  "logging.googleapis.com/trace": "projects/my-project/traces/abc123def456"
}
```
Cloud Logging and Cloud Trace display correlated entries in the same timeline.

---

## Cloud Profiler

### Purpose

Continuous CPU and memory profiling for production applications with negligible overhead (<1% CPU impact). Cloud Profiler collects statistical profiles over time, enables flame graph visualization, and supports comparison across deployments.

### Profile Types

| Profile Type | What It Measures | Languages |
|---|---|---|
| CPU time | Time spent executing code (wall clock minus idle) | Go, Java, Python, Node.js, Ruby |
| Wall time | Total elapsed time including blocking (I/O wait, locks) | Go, Java |
| Heap (allocated) | Memory currently allocated (live objects at sample time) | Go, Java, Node.js |
| Heap (in use) | Memory in use since last GC (Go) | Go |
| Contention | Time threads spent waiting for locks | Go, Java |
| Threads | Number of active threads | Java |

### Agent Setup

**Go:**
```go
import "cloud.google.com/go/profiler"
// In main():
profiler.Start(profiler.Config{
    Service:        "my-service",
    ServiceVersion: "1.0.0",
    ProjectID:      "my-project",
})
```

**Java:**
```bash
# Add to JVM startup flags
-agentpath:/opt/cprof/profiler_java_agent.so=-cprof_service=my-service,-cprof_service_version=1.0.0,-cprof_project_id=my-project
```

**Python:**
```python
import googlecloudprofiler
googlecloudprofiler.start(
    service='my-service',
    service_version='1.0.0',
    project_id='my-project'
)
```

**Node.js:**
```javascript
require('@google-cloud/profiler').start({
  serviceContext: {
    service: 'my-service',
    version: '1.0.0',
  },
});
```

**Ruby:**
```ruby
require "cloud_profiler_agent"
CloudProfilerAgent.start(
  service: "my-service",
  service_version: "1.0.0"
)
```

### Flame Graph Reading

- X-axis: proportion of samples (wider = more time spent)
- Y-axis: call stack depth (bottom = program entry; top = currently executing function)
- Color: usually indicates source file or library; not performance
- Identify: wide flat areas at the top = hot code paths; optimize these first

### Profile Comparison

- Compare profiles from two time periods (before/after a deployment)
- Differential flame graph highlights functions that got faster (green) or slower (red)
- Useful for validating optimization efforts or identifying regressions

---

## Error Reporting

### Purpose

Automatically aggregates, deduplicates, and notifies on application errors. Parses stack traces from Cloud Logging entries and groups them into error groups (same root cause). Provides a dashboard of active errors, their frequency, affected users, and first/last occurrence.

### Supported Error Sources

| Source | How |
|---|---|
| Cloud Run | Automatic: uncaught exceptions in logs |
| App Engine | Automatic: standard error reporting |
| Cloud Functions | Automatic: uncaught exceptions |
| GKE / GCE | Via Ops Agent + Cloud Logging; structured log entries with stack traces |
| Error Reporting API | Manual: send error events directly via client library or REST API |

### Error Reporting API (manual instrumentation)

```python
from google.cloud import error_reporting

client = error_reporting.Client(project="my-project", service="my-service")

try:
    # risky operation
    result = divide(10, 0)
except Exception:
    client.report_exception(
        http_context=error_reporting.HTTPContext(
            method="GET",
            url="/api/compute",
            user_agent="Mozilla/5.0",
            response_status_code=500
        )
    )

# Report a simple string message
client.report("Custom error message from my service")
```

### Log Format for Auto-Detection

Error Reporting detects errors in Cloud Logging when the log entry contains:
- `severity` of ERROR or higher
- A stack trace in `message`, `textPayload`, or `jsonPayload.message`
- Recognized stack trace format for Python, Java, Go, Node.js, Ruby, PHP, .NET

---

## OpenTelemetry Integration

GCP supports OpenTelemetry (OTel) as a first-class observability standard:

- **Traces**: Cloud Trace accepts traces from OpenTelemetry SDKs and Collector
- **Metrics**: Cloud Monitoring accepts metrics from OTel SDK (via `google-cloud-opentelemetry` exporter)
- **Logs**: Cloud Logging accepts OTel log records via the Ops Agent OTel pipeline
- **OTel Collector**: run as a sidecar or DaemonSet; receive OTel signals from apps; forward to GCP

### OTel Collector GCP Exporter Configuration

```yaml
# OpenTelemetry Collector config (collector-config.yaml)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s

exporters:
  googlecloud:
    project: my-project

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [googlecloud]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [googlecloud]
```
