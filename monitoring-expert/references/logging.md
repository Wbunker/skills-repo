# Logging
## Chapter 9: Log Levels, Structured Logging, Log Pipelines, Retention

---

## The Role of Logging

Metrics tell you that something is wrong. Logs tell you why.

Metrics are aggregates — they summarize behavior across many requests. Logs are discrete events — they capture the specific context of each occurrence. Both are necessary; neither substitutes for the other.

**When to use metrics vs. logs:**

| Use Metrics When | Use Logs When |
|-----------------|---------------|
| Counting frequency of events | Understanding specific event details |
| Measuring latency distributions | Debugging a specific failed request |
| Alerting on thresholds | Audit trail of who did what |
| Trending over time | Capturing error context and stack traces |

---

## Log Levels

### Standard Levels

| Level | Use For | Examples |
|-------|---------|----------|
| **FATAL** | Process cannot continue; crash imminent | Unrecoverable configuration error on startup |
| **ERROR** | Operation failed; requires attention | Payment processing failed; database write rejected |
| **WARN** | Unexpected but handled; potential problem | Retry #3 of 5 succeeded; deprecated API called |
| **INFO** | Normal significant events | Service started; user logged in; job completed |
| **DEBUG** | Detailed diagnostic information | Request parameters; intermediate computation values |
| **TRACE** | Extremely detailed; internal flow | Function entry/exit; variable values per iteration |

### Level Selection Rules

- **ERROR** should fire for conditions a human must eventually investigate
- **WARN** should fire for conditions the system handled but that indicate something to watch
- **INFO** should be readable as a narrative of normal operation
- **DEBUG** should be disabled in production by default; enable dynamically for investigation
- **TRACE** is rarely appropriate in production even temporarily

**Anti-patterns:**
- Using ERROR for every exception, including expected ones (e.g., validation errors → WARN or INFO)
- Using INFO for high-frequency events (creates log flooding, hides important events)
- Not logging at ERROR when a background job silently fails

---

## Structured Logging

Structured logs emit machine-readable key-value pairs rather than free-form text strings. This is the most impactful logging improvement for operational observability.

### Unstructured (Avoid in Production)

```
2024-01-15 14:23:01 ERROR Payment failed for user 12345: timeout connecting to Stripe after 5 seconds
```

Problems: parsing requires regex; fields are unreliable; searching across large volumes is slow.

### Structured (Preferred)

```json
{
  "timestamp": "2024-01-15T14:23:01.234Z",
  "level": "ERROR",
  "message": "Payment processing failed",
  "service": "checkout-api",
  "user_id": "12345",
  "provider": "stripe",
  "error_type": "timeout",
  "duration_ms": 5002,
  "trace_id": "abc-def-123",
  "environment": "production"
}
```

Benefits: fields are directly queryable; dashboards can aggregate on `error_type` or `provider`; correlation with traces via `trace_id`.

### Standard Fields

Include consistently in every log event:

| Field | Description |
|-------|-------------|
| `timestamp` | ISO 8601 with milliseconds and timezone |
| `level` | Log level string |
| `service` | Emitting service name |
| `environment` | production / staging / development |
| `trace_id` | Distributed trace ID (if applicable) |
| `request_id` | Per-request correlation ID |
| `user_id` | Authenticated user (if applicable, respecting privacy) |
| `message` | Human-readable summary of the event |

### Correlation IDs

Generate a unique ID at the boundary of each request and pass it through all downstream calls and log entries. This allows you to find all log events associated with a single request across multiple services.

```
Request arrives at API gateway
    │
    ├── Generate: trace_id = "a1b2c3d4"
    ├── Pass as header: X-Trace-Id: a1b2c3d4
    │
    ▼ API service logs with trace_id="a1b2c3d4"
    ▼ DB service logs with trace_id="a1b2c3d4"
    ▼ Queue worker logs with trace_id="a1b2c3d4"
```

All logs for one user request now retrievable with: `trace_id = "a1b2c3d4"`

---

## What to Log

### Always Log

- Service startup and shutdown (with configuration summary)
- Incoming requests (method, path, status code, duration — but not request body)
- Outgoing calls to external services (target, duration, outcome)
- Authentication events (login, logout, failed attempts, permission denials)
- State transitions for important entities (order created, payment processed, job failed)
- All ERROR conditions with full context

### Be Selective About

- Successful operations (log at INFO sparingly; high volume → noise)
- Individual database queries (DEBUG level at most; production volume is enormous)
- Request/response bodies (privacy and storage concerns; use sampling if needed)

### Never Log

- Passwords, tokens, secrets, or API keys
- Full credit card numbers or payment credentials (partial masking only)
- PII that is not necessary for operational purposes (GDPR, CCPA compliance)
- Health check requests (generates enormous noise at INFO level)

---

## Log Pipelines

### Pipeline Architecture

```
Application instances
    │ (structured log output to stdout/stderr or file)
    ▼
Log collection agent (Fluentd, Logstash, Filebeat, Vector)
    │ (parse, enrich, route)
    ▼
Log aggregation / indexing (Elasticsearch, OpenSearch, Loki, Splunk)
    │ (store, index, make searchable)
    ▼
Search / visualization layer (Kibana, Grafana, Splunk UI)
    │
    ├── Human search and investigation
    ├── Log-based alerting (pattern matches)
    └── Log-derived metrics (count events over time)
```

### Agent Responsibilities

The collection agent should:
- Parse structured logs (JSON or key-value) into indexable fields
- Add environment-level enrichment (host, region, service version)
- Buffer during backend outages without dropping logs
- Route logs to different destinations based on level or service

### Common Stacks

| Stack | Use Case |
|-------|---------|
| ELK (Elasticsearch + Logstash + Kibana) | Self-hosted; full control; high operational overhead |
| EFK (Elasticsearch + Fluentd + Kibana) | Self-hosted; Fluentd is lighter than Logstash |
| Grafana Loki + Grafana | Metrics-first shops; Loki is cost-efficient; less powerful queries |
| Datadog Logs | SaaS; integrates with Datadog metrics; expensive at scale |
| Splunk | Enterprise; powerful queries; very expensive |

---

## Log-Based Alerting

Logs can trigger alerts when specific patterns appear.

### When to Alert on Logs vs. Metrics

Alert on logs when:
- A specific error message indicates a critical failure (e.g., "Payment gateway unreachable")
- A sequence of events indicates a problem (failed logins from same IP)
- The event is rare enough that a counter metric would be misleading

Prefer metrics for alerting when volume allows — log-based alerting has higher latency and is more brittle to log format changes.

### Log Alert Patterns

- **Count threshold:** "More than 10 events matching `level=ERROR AND service=checkout` in 5 minutes"
- **Absence alert:** "No events matching `message=health_check_ok` in 2 minutes" (service stopped logging)
- **Pattern match:** Any event matching `message=*database connection pool exhausted*`

---

## Retention Policy

Storage costs scale with log volume. Define retention before production traffic begins.

| Log Type | Recommended Retention |
|----------|-----------------------|
| Application debug/info logs | 7–30 days |
| Application error logs | 30–90 days |
| Access logs (HTTP) | 90 days |
| Security / audit logs | 1–7 years (regulatory dependent) |
| Compliance-critical logs | Per compliance requirement |

Implement tiered storage: recent logs in fast storage (hot), older logs in cheap object storage (cold), with search still possible but slower.
