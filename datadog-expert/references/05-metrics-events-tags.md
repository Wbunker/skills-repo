# Metrics, Events, and Tags

Reference for understanding Datadog's metric types, event system, and tagging strategy.

## Table of Contents
- [Understanding Metrics](#understanding-metrics)
- [Metric Types](#metric-types)
- [Metric Submission](#metric-submission)
- [Events](#events)
- [Tags](#tags)
- [Tagging Strategy](#tagging-strategy)

## Understanding Metrics

A metric is a numerical value tracked over time. Every metric data point consists of:
- **Metric name**: dotted namespace (e.g., `system.cpu.user`, `app.request.latency`)
- **Value**: the numerical measurement
- **Timestamp**: when the measurement was taken
- **Tags**: key:value pairs for filtering and grouping
- **Type**: how the value should be interpreted (count, rate, gauge, etc.)

### Metric Naming Conventions
```
<namespace>.<category>.<measurement>

# Examples:
system.cpu.user          # system namespace, cpu category
app.orders.count         # application namespace
aws.ec2.cpuutilization   # cloud integration namespace
trace.http.request.hits  # APM namespace
```

**Rules:**
- Lowercase, dot-separated
- Max 200 characters
- No spaces; use underscores for multi-word
- Avoid high-cardinality in metric names (use tags instead)

## Metric Types

### COUNT
Number of occurrences in an interval.
```python
# DogStatsD
statsd.increment('app.page.views')
statsd.increment('app.page.views', value=5)
```

### RATE
Count normalized per second.
```python
statsd.increment('app.requests', value=100)
# Displayed as requests/second
```

### GAUGE
Point-in-time value (last value wins per flush interval).
```python
statsd.gauge('app.queue.size', 42)
statsd.gauge('system.disk.free', 1073741824)
```

### HISTOGRAM
Statistical distribution (avg, median, max, 95th percentile, count).
```python
statsd.histogram('app.request.latency', 0.234)
# Generates: app.request.latency.avg, .median, .max, .95percentile, .count
```

### DISTRIBUTION
Global statistical distribution calculated server-side. More accurate than histogram for multi-host aggregation.
```python
statsd.distribution('app.request.latency', 0.234)
```

### SET
Count of unique elements in a group.
```python
statsd.set('app.users.unique', user_id)
```

## Metric Submission

### Via Agent (Integration Checks)
Automatic — configured integrations submit metrics on their collection interval.

### Via DogStatsD (UDP)
```python
from datadog import statsd

statsd.gauge('app.active_users', 150, tags=['env:prod', 'service:web'])
statsd.increment('app.logins', tags=['env:prod', 'method:oauth'])
statsd.histogram('app.latency', 0.042, tags=['env:prod', 'endpoint:/api/users'])
```

### Via REST API
```bash
curl -X POST "https://api.datadoghq.com/api/v2/series" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -d '{
    "series": [{
      "metric": "app.test.metric",
      "type": 1,
      "points": [{"timestamp": 1234567890, "value": 42.0}],
      "tags": ["env:test"]
    }]
  }'
```

## Events

Events capture discrete occurrences — not continuous measurements.

### Event Properties
| Field | Description |
|-------|-------------|
| `title` | Short summary (required) |
| `text` | Detailed description (supports markdown) |
| `priority` | `normal` or `low` |
| `alert_type` | `info`, `warning`, `error`, `success` |
| `tags` | Key:value pairs for filtering |
| `source_type_name` | Integration source |

### Submitting Events
```python
from datadog import api

api.Event.create(
    title='Deployment completed',
    text='Version 2.3.1 deployed to production',
    tags=['env:production', 'service:api'],
    alert_type='success'
)
```

```bash
# Via API
curl -X POST "https://api.datadoghq.com/api/v1/events" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -d '{"title":"Deploy v2.3.1","text":"Deployed to prod","tags":["env:prod"],"alert_type":"success"}'
```

### Event Correlation
Overlay events on dashboard graphs to visualize the impact of deployments, config changes, and incidents on metrics.

## Tags

Tags are key:value pairs attached to metrics, logs, traces, and infrastructure.

### Tag Format
```
key:value

# Examples:
env:production
service:web-api
team:backend
version:2.3.1
region:us-east-1
availability-zone:us-east-1a
instance-type:m5.xlarge
```

### Tag Sources
| Source | How Applied |
|--------|-------------|
| **Agent config** | `tags:` in `datadog.yaml` — applied to all data from that host |
| **Integration config** | `tags:` in integration YAML — applied to that integration's data |
| **Cloud provider** | Auto-imported from AWS/GCP/Azure (instance tags, labels) |
| **Kubernetes** | Pod labels, annotations, namespace, deployment name |
| **DogStatsD** | Passed with each metric submission |
| **Unified Service Tagging** | `DD_ENV`, `DD_SERVICE`, `DD_VERSION` env vars |

### Reserved Tags
| Tag | Purpose |
|-----|---------|
| `env` | Environment (production, staging, dev) |
| `service` | Service name (unified across metrics/traces/logs) |
| `version` | Application version for deployment tracking |
| `host` | Automatically applied by agent |

## Tagging Strategy

### Unified Service Tagging
Apply `env`, `service`, and `version` consistently across all telemetry:

```yaml
# Agent config (datadog.yaml)
tags:
  - env:production

# Application (environment variables)
DD_ENV=production
DD_SERVICE=web-api
DD_VERSION=2.3.1
```

This enables:
- Correlating metrics, traces, and logs for a single service
- Deployment tracking in APM
- Service Catalog population

### Tagging Best Practices
- **Use lowercase** consistently
- **Keep cardinality reasonable** — avoid user IDs or request IDs as tag values
- **Standardize tag keys** across teams (document in a tagging guide)
- **Use Unified Service Tagging** (`env`, `service`, `version`) everywhere
- **Layer tags**: broad (env) > medium (service) > specific (version)
- **Auto-import cloud tags** but be selective to avoid cost from high-cardinality tags
