# Managing Logs Using Datadog

Reference for log collection, processing, indexing, and analysis with Datadog Log Management.

## Table of Contents
- [Log Collection](#log-collection)
- [Log Processing](#log-processing)
- [Log Indexes and Archives](#log-indexes-and-archives)
- [Log Search and Analytics](#log-search-and-analytics)
- [Log Monitors](#log-monitors)
- [Logging Without Limits](#logging-without-limits)

## Log Collection

### Enable Log Collection
In `datadog.yaml`:
```yaml
logs_enabled: true
```

### File-Based Collection
```yaml
# /etc/datadog-agent/conf.d/<service>.d/conf.yaml
logs:
  - type: file
    path: /var/log/myapp/*.log
    service: myapp
    source: python
    tags:
      - env:production
```

### Journal/Syslog
```yaml
logs:
  - type: journald
    container_mode: true
    include_units:
      - myservice.service
```

### TCP/UDP
```yaml
logs:
  - type: tcp
    port: 10514
    service: syslog
    source: syslog
```

### Docker Container Logs
```yaml
# Collect all container logs
DD_LOGS_ENABLED=true
DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true
```

Per-container control with labels:
```yaml
labels:
  com.datadoghq.ad.logs: '[{"source":"nginx","service":"web","tags":["env:prod"]}]'
```

Exclude containers:
```yaml
DD_CONTAINER_EXCLUDE_LOGS="name:datadog-agent image:gcr.io/datadoghq/agent"
```

### Kubernetes Pod Logs
```yaml
# Pod annotation
metadata:
  annotations:
    ad.datadoghq.com/<container>.logs: |
      [{
        "source": "java",
        "service": "myapp",
        "log_processing_rules": [{
          "type": "multi_line",
          "name": "java_stacktrace",
          "pattern": "\\d{4}-\\d{2}-\\d{2}"
        }]
      }]
```

### Multi-Line Logs
```yaml
logs:
  - type: file
    path: /var/log/myapp/app.log
    service: myapp
    source: java
    log_processing_rules:
      - type: multi_line
        name: java_multi_line
        pattern: '^\d{4}-\d{2}-\d{2}'  # New log entry starts with date
```

### Scrubbing Sensitive Data
```yaml
logs:
  - type: file
    path: /var/log/myapp/*.log
    service: myapp
    source: python
    log_processing_rules:
      - type: mask_sequences
        name: mask_credit_cards
        replace_placeholder: "[REDACTED_CC]"
        pattern: '\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
      - type: mask_sequences
        name: mask_emails
        replace_placeholder: "[REDACTED_EMAIL]"
        pattern: '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```

## Log Processing

### Pipelines
Processing pipelines parse, enrich, and transform logs before indexing.

**Built-in pipelines:** Auto-detected for common sources (Nginx, Apache, PostgreSQL, Python, Java, etc.)

### Common Processors

| Processor | Purpose |
|-----------|---------|
| **Grok Parser** | Extract structured fields from unstructured logs |
| **Date Remapper** | Set the official log timestamp |
| **Status Remapper** | Set the log severity level |
| **Service Remapper** | Set the service name |
| **Message Remapper** | Set the log message |
| **Attribute Remapper** | Rename or copy attributes |
| **URL Parser** | Parse URL components |
| **User-Agent Parser** | Parse browser/device info |
| **Category Processor** | Categorize logs by rules |
| **Arithmetic Processor** | Compute new attributes |
| **String Builder** | Build new attributes from templates |
| **Lookup Processor** | Map values using a lookup table |

### Grok Parser Example
Log format: `2024-01-15 10:30:45 INFO [myapp] Request processed in 234ms`

```
parsing_rule %{date("yyyy-MM-dd HH:mm:ss"):timestamp} %{word:level} \[%{word:service}\] %{data:message}
```

### Standard Attributes
Use Datadog's standard attribute naming for correlation:
| Attribute | Standard Name |
|-----------|--------------|
| Duration | `duration` |
| HTTP method | `http.method` |
| HTTP status | `http.status_code` |
| HTTP URL | `http.url` |
| User ID | `usr.id` |
| Error message | `error.message` |
| Error stack | `error.stack` |

## Log Indexes and Archives

### Indexes
Control which logs are indexed (searchable in Datadog) and for how long.

```
Logs > Configuration > Indexes

Index: production-errors
  Filter: status:(error OR critical) env:production
  Retention: 30 days
  Daily quota: 10,000,000 events

Index: production-all
  Filter: env:production
  Retention: 15 days
  Daily quota: 50,000,000 events

Index: default (catch-all)
  Filter: *
  Retention: 7 days
```

**Index order matters** — logs match the first index whose filter applies.

### Exclusion Filters
Reduce index volume without losing data:
```
Index: production-all
  Exclusion: health checks
    Filter: @http.url:/health
    Rate: exclude 100%

  Exclusion: debug logs
    Filter: status:debug
    Rate: exclude 100%
```

### Archives
Store all logs long-term in cloud storage (even unindexed logs):
- **S3**: `s3://my-bucket/datadog-logs/`
- **GCS**: `gs://my-bucket/datadog-logs/`
- **Azure Blob**: blob storage container
- **Rehydration**: Restore archived logs back into Datadog for investigation

## Log Search and Analytics

### Search Syntax
```
# Full-text search
error connection timeout

# Attribute search
@http.status_code:500
@duration:>1000
service:myapp status:error

# Wildcards
@http.url:/api/users/*
service:my*

# Boolean operators
service:api AND status:error
service:api OR service:web
NOT status:info

# Range
@duration:[100 TO 500]
@http.status_code:[400 TO 499]
```

### Log Analytics
Aggregate and visualize log data:
```
# Count errors by service over time
count by service where status:error

# Average request duration by endpoint
avg(@duration) by @http.url where service:api

# Top 10 error messages
top(@error.message, 10) where status:error
```

### Saved Views
Store frequently used searches with specific columns, filters, and time ranges for quick access.

## Log Monitors

### Log Count Monitor
```
Alert when error log volume exceeds threshold:
Query: logs("service:api status:error").index("production").rollup("count").last("5m") > 100
```

### Log Analytics Monitor
```
Alert when average request duration exceeds threshold:
Query: logs("service:api").index("production").rollup("avg", "@duration").by("@http.url").last("5m") > 5000
```

## Logging Without Limits

Datadog's approach to cost-effective log management:

1. **Ingest everything** — All logs are ingested and processed
2. **Index selectively** — Only index logs you need to search (use exclusion filters)
3. **Archive everything** — Store all logs in cheap cloud storage
4. **Generate metrics from logs** — Create custom metrics from log patterns without indexing
5. **Rehydrate on demand** — Restore archived logs when needed for investigation

### Log-Based Metrics
Create metrics from logs without indexing:
```
Logs > Generate Metrics

Metric: app.errors.count
  Query: service:api status:error
  Group by: @http.url, @error.type
  Type: count

Metric: app.request.duration.p95
  Query: service:api
  Measure: @duration
  Group by: @http.url
  Type: distribution
```

This is cost-effective: you pay for metric storage (cheap) instead of log indexing (expensive).
