# Cloud Trace & Cloud Profiler — CLI Reference

Cloud Trace and Cloud Profiler are primarily instrumented via SDKs embedded in applications. CLI and gcloud support is limited; most operations are through the Cloud Console UI or REST APIs. Error Reporting has some gcloud support.

---

## Cloud Trace

### gcloud CLI (limited)

```bash
# Cloud Trace has minimal gcloud CLI support.
# Use the REST API or Cloud Console for most operations.

# List traces for a project (REST API via curl)
TOKEN=$(gcloud auth print-access-token)
PROJECT_ID=my-project

# List recent traces
curl -s "https://cloudtrace.googleapis.com/v1/projects/${PROJECT_ID}/traces" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.traces[] | {traceId: .traceId}'

# Get a specific trace by ID
TRACE_ID="abc123def456abc123def456abc12345"
curl -s "https://cloudtrace.googleapis.com/v1/projects/${PROJECT_ID}/traces/${TRACE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.'

# List traces with filters (time range, URI, minimum latency)
curl -s "https://cloudtrace.googleapis.com/v1/projects/${PROJECT_ID}/traces?filter=+latency:1s&startTime=2024-01-01T00:00:00Z&endTime=2024-01-01T23:59:59Z" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.traces[] | {traceId: .traceId, spans: (.spans | length)}'

# Patch (create) a trace (for manual trace injection)
curl -s -X PATCH \
  "https://cloudtrace.googleapis.com/v1/projects/${PROJECT_ID}/traces" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "traces": [{
      "projectId": "my-project",
      "traceId": "aaaabbbbccccddddeeeeffff00001111",
      "spans": [{
        "spanId": "1",
        "name": "custom-span",
        "startTime": "2024-01-01T10:00:00Z",
        "endTime": "2024-01-01T10:00:01Z",
        "labels": {
          "/http/url": "/api/orders",
          "/http/status_code": "200"
        }
      }]
    }]
  }'
```

### Trace API v2 (BatchWriteSpans)

```bash
# Write spans using Cloud Trace API v2 (preferred for custom instrumentation)
TOKEN=$(gcloud auth print-access-token)

curl -s -X POST \
  "https://cloudtrace.googleapis.com/v2/projects/my-project/traces:batchWrite" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "spans": [{
      "name": "projects/my-project/traces/abc123/spans/span1",
      "spanId": "span1",
      "displayName": {"value": "process-payment"},
      "startTime": "2024-01-01T10:00:00Z",
      "endTime": "2024-01-01T10:00:00.500Z",
      "attributes": {
        "attributeMap": {
          "payment.amount": {"intValue": "100"},
          "payment.currency": {"stringValue": {"value": "USD"}}
        }
      },
      "status": {"code": 0}
    }]
  }'
```

### Correlating Traces with Logs

When writing structured logs, include the trace ID to link them in Cloud Console:

```python
# Python example — structured log with trace correlation
import json
import logging

TRACE_ID = "abc123def456abc123def456abc12345"
PROJECT_ID = "my-project"

entry = {
    "message": "Processing payment",
    "severity": "INFO",
    "logging.googleapis.com/trace": f"projects/{PROJECT_ID}/traces/{TRACE_ID}",
    "logging.googleapis.com/spanId": "span1",
    "logging.googleapis.com/traceSampled": True
}
print(json.dumps(entry))  # stdout → Cloud Logging
```

---

## Cloud Profiler

### gcloud CLI (very limited)

```bash
# Cloud Profiler is almost entirely SDK-based. There is no substantive gcloud CLI.
# Profiles are viewable in the Cloud Console at:
# https://console.cloud.google.com/profiler

# IAM: ensure service account running the profiled app has:
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudprofiler.agent"
```

### Profiler REST API

```bash
TOKEN=$(gcloud auth print-access-token)

# List profile types and services (Cloud Profiler REST API)
curl -s "https://cloudprofiler.googleapis.com/v2/projects/my-project/profiles" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.'

# Create a profile (agent does this automatically; shown for reference)
curl -s -X POST \
  "https://cloudprofiler.googleapis.com/v2/projects/my-project/profiles" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "deployment": {
      "projectId": "my-project",
      "target": "my-service",
      "labels": {"version": "1.0.0", "zone": "us-central1-a"}
    },
    "profileType": ["CPU", "HEAP"]
  }'
```

### Profiler Agent Deployment on GKE

```yaml
# Kubernetes deployment with Profiler agent (Go example)
# The agent starts within the application; no separate sidecar needed.
# For Java, pass agent flags via environment variable:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-java-app
spec:
  template:
    spec:
      containers:
      - name: my-app
        image: gcr.io/my-project/my-java-app:latest
        env:
        - name: JAVA_TOOL_OPTIONS
          value: "-agentpath:/opt/cprof/profiler_java_agent.so=-cprof_service=my-java-app,-cprof_service_version=1.0.0"
```

---

## Error Reporting

```bash
# List error groups (REST API — gcloud has limited support)
TOKEN=$(gcloud auth print-access-token)
PROJECT_ID=my-project

# List active error groups
curl -s "https://clouderrorreporting.googleapis.com/v1beta1/projects/${PROJECT_ID}/groupStats?timeRange.period=PERIOD_1_DAY" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.errorGroupStats[] | {group: .group.groupId, count: .count, firstSeen: .firstSeenTime}'

# List error events for a specific group
GROUP_ID=CMXabcdef
curl -s "https://clouderrorreporting.googleapis.com/v1beta1/projects/${PROJECT_ID}/events?groupId=${GROUP_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq '.errorEvents[] | {time: .eventTime, message: .message}'

# Report an error event via REST API
curl -s -X POST \
  "https://clouderrorreporting.googleapis.com/v1beta1/projects/${PROJECT_ID}/events:report" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "eventTime": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "serviceContext": {
      "service": "my-service",
      "version": "1.0.0"
    },
    "message": "Exception in processOrder\n  at com.example.OrderService.process(OrderService.java:42)\n  at com.example.Main.main(Main.java:15)"
  }'

# gcloud error-reporting (limited commands)
# List events for all error groups
gcloud error-reporting events list \
  --project=my-project

# Delete all error events (use with caution)
gcloud error-reporting events delete-all \
  --project=my-project

# Read errors via Cloud Logging (most practical approach)
gcloud logging read \
  'severity>=ERROR AND resource.type="cloud_run_revision"' \
  --project=my-project \
  --freshness=1h \
  --format=json \
  | jq '.[] | {timestamp: .timestamp, message: .textPayload}'
```

---

## IAM Requirements

```bash
# Cloud Trace: grant trace agent role to service account
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

# Cloud Trace: read traces (for developers/SREs)
gcloud projects add-iam-policy-binding my-project \
  --member="user:developer@example.com" \
  --role="roles/cloudtrace.user"

# Cloud Profiler: grant profiler agent role
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudprofiler.agent"

# Error Reporting: grant editor role (to manage error groups)
gcloud projects add-iam-policy-binding my-project \
  --member="user:developer@example.com" \
  --role="roles/errorreporting.user"

# Key IAM roles:
# roles/cloudtrace.agent  - write traces from application (SA role)
# roles/cloudtrace.user   - read and query traces
# roles/cloudprofiler.agent - write profiles from application (SA role)
# roles/errorreporting.viewer - read error groups
# roles/errorreporting.user   - read and modify error groups (mark resolved)
```
