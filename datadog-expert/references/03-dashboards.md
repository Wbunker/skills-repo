# The Datadog Dashboard

Reference for navigating and building Datadog dashboards, using the Metrics Explorer, and working with visualizations.

## Table of Contents
- [Infrastructure List](#infrastructure-list)
- [Events](#events)
- [Metrics Explorer](#metrics-explorer)
- [Dashboards](#dashboards)
- [Integrations Menu](#integrations-menu)
- [Monitors Overview](#monitors-overview)
- [Advanced Features](#advanced-features)

## Infrastructure List

The Infrastructure List shows all reporting hosts with:
- Hostname, aliases, tags
- Installed integrations and their status
- Agent version
- Cloud provider metadata (instance type, region, AZ)

**Filtering:** Use tag-based filtering (`env:production`, `service:api`) to narrow the list.

**Host Map:** Visual representation of infrastructure grouped and colored by tags/metrics. Useful for spotting outliers across large fleets.

## Events

The Event Stream aggregates events from all sources:
- Agent events (start, stop, errors)
- Integration events (deployments, config changes)
- Monitor alerts and recoveries
- Custom events via API or DogStatsD

**Event Query Syntax:**
```
sources:kubernetes status:error priority:normal
tags:env:production,service:api
```

**Event Overlays:** Overlay events on dashboard graphs to correlate deployments with metric changes.

## Metrics Explorer

Interactive tool for ad-hoc metric exploration without building a full dashboard.

### Query Structure
```
<aggregation>:<metric_name>{<tag_filters>} by {<group_by_tags>}
```

**Examples:**
```
avg:system.cpu.user{env:production} by {host}
sum:trace.http.request.hits{service:web-app} by {resource_name}
max:docker.mem.rss{container_name:myapp}
```

### Aggregation Functions
| Function | Description |
|----------|-------------|
| `avg` | Average across all sources |
| `sum` | Sum across all sources |
| `min` | Minimum value |
| `max` | Maximum value |
| `count` | Count of data points |

### Space vs. Time Aggregation
- **Space aggregation**: How to combine values from multiple hosts/tags (avg, sum, min, max)
- **Time aggregation**: How to roll up values within a time bucket (avg, sum, min, max, count)

## Dashboards

### Dashboard Types

| Type | Use Case |
|------|----------|
| **Screenboard** | Free-form layout, mixed widget sizes, status boards for TVs |
| **Timeboard** | Synchronized time, all graphs share the same timeframe, debugging |

### Common Widgets

| Widget | Purpose |
|--------|---------|
| **Timeseries** | Line/bar/area graph of metrics over time |
| **Query Value** | Single number (current value of a metric) |
| **Top List** | Ranked list of tag values by a metric |
| **Heatmap** | Distribution of a metric across tags |
| **Distribution** | Histogram of metric values |
| **Change** | Shows metric change over a time period |
| **Host Map** | Visual infrastructure overview |
| **SLO** | Service Level Objective status |
| **Log Stream** | Live log tail |
| **Trace Map** | Service dependency visualization |
| **Alert Graph** | Monitor status visualization |
| **Free Text** | Markdown-formatted notes |
| **Group** | Container to organize widgets |

### Dashboard JSON API
Export/import dashboards as JSON:
```bash
# Export
curl -s "https://api.datadoghq.com/api/v1/dashboard/<dashboard_id>" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Import
curl -s -X POST "https://api.datadoghq.com/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @dashboard.json
```

### Dashboard Best Practices
- **Use template variables** for dynamic filtering (e.g., `$env`, `$service`)
- **Group related widgets** using the Group widget
- **Add event overlays** for deploy markers
- **Use notebook-style layouts** for investigation dashboards
- **Clone OOTB dashboards** and customize rather than building from scratch
- **Apply consistent naming**: `[Team] Service - Category` (e.g., `[Platform] API Gateway - Performance`)

## Integrations Menu

Access installed integrations, browse available ones, and configure new integrations.

**Integration types:**
- **Agent-based**: Configured via YAML in `conf.d/`, agent collects the data
- **Crawler/API-based**: Datadog polls external APIs (AWS, GCP, etc.)
- **Library-based**: Instrumentation libraries in application code (APM)

## Monitors Overview

Quick access to all configured monitors, their status, and alert history. Full monitor details in [07-monitors-and-alerts.md](07-monitors-and-alerts.md).

## Advanced Features

### Notebooks
Combine markdown narrative with live graphs for investigations and postmortems. Graphs auto-update but can be pinned to a specific timeframe.

### Service Level Objectives (SLOs)
Define target uptime/latency objectives. Track error budgets. Alert when burn rate exceeds thresholds.

### Saved Views
Store frequently used filter combinations for quick access across Infrastructure List, Logs, APM, etc.
