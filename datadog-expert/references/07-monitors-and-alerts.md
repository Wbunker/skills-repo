# Monitors and Alerts

Reference for creating, managing, and optimizing Datadog monitors and alert notifications.

## Table of Contents
- [Monitor Types](#monitor-types)
- [Creating Monitors](#creating-monitors)
- [Alert Conditions](#alert-conditions)
- [Notifications](#notifications)
- [Monitor Management](#monitor-management)
- [Downtimes](#downtimes)
- [Best Practices](#best-practices)

## Monitor Types

| Type | Use Case |
|------|----------|
| **Metric** | Alert on any metric crossing a threshold |
| **Anomaly** | Detect deviations from historical patterns (ML-based) |
| **Outlier** | Find hosts/services behaving differently from peers |
| **Forecast** | Predict when a metric will cross a threshold |
| **APM** | Alert on trace metrics (latency, error rate, throughput) |
| **Log** | Alert on log volume, patterns, or specific messages |
| **Process** | Alert when a process stops running or exceeds resource limits |
| **Network** | Alert on TCP/HTTP check failures |
| **Integration** | Alert from specific integration metrics |
| **Composite** | Combine multiple monitors with boolean logic (A && B) |
| **SLO** | Alert on SLO burn rate or remaining error budget |
| **Event** | Alert on event patterns or frequency |
| **Watchdog** | Auto-detected anomalies (no configuration needed) |
| **CI** | Alert on CI pipeline failures or performance |

## Creating Monitors

### Metric Monitor Example
```
Monitor: High CPU Usage
Query: avg(last_5m):avg:system.cpu.user{env:production} by {host} > 90
Warning: > 80
Critical: > 90
Notify: @slack-ops-alerts @pagerduty-oncall
```

### Query Syntax
```
<aggregation>(last_<timeframe>):<space_agg>:<metric>{<filters>} by {<groups>} <comparator> <threshold>
```

**Components:**
- **Time aggregation**: `avg`, `sum`, `min`, `max`, `count` over `last_Xm/h/d`
- **Space aggregation**: `avg`, `sum`, `min`, `max` across tag groups
- **Filters**: tag-based (e.g., `env:production,service:api`)
- **Group by**: evaluate per tag value (e.g., `by {host}`)

### Anomaly Monitor
```
Query: avg(last_4h):anomalies(avg:system.cpu.user{env:production}, 'agile', 3)
```

Algorithms:
- **Basic**: Simple lagging window comparison
- **Agile**: Quickly adapts to level shifts
- **Robust**: Resilient to transient spikes

### Composite Monitor
```
Monitor A: CPU > 80% (ID: 12345)
Monitor B: Memory > 90% (ID: 67890)

Composite: A && B  →  Alert when BOTH are critical
Formula: 12345 && 67890
```

## Alert Conditions

### Evaluation Window
- **Rolling window**: `last_5m`, `last_15m`, `last_1h`
- **Calendar window**: Evaluate on fixed calendar boundaries

### Thresholds
- **Warning**: Early signal, lower urgency
- **Critical**: Immediate attention needed
- **Recovery thresholds**: Separate thresholds for clearing alerts (prevents flapping)
  - Warning recovery: value at which warning resolves
  - Critical recovery: value at which critical resolves

### Advanced Conditions
- **No data**: Alert if no data received for X minutes
- **Require full window**: Only alert if data covers entire evaluation window
- **Evaluation delay**: Delay evaluation to account for late-arriving data (common with cloud metrics)
- **New group delay**: Delay alerting for newly discovered groups (prevent false positives on new hosts)

## Notifications

### Message Syntax (Markdown + Template Variables)
```
{{#is_alert}}
**CRITICAL**: CPU usage on {{host.name}} is {{value}}%
Environment: {{host.env}}
Service: {{host.service}}

Dashboard: https://app.datadoghq.com/dashboard/xxx
Runbook: https://wiki.example.com/runbooks/high-cpu
{{/is_alert}}

{{#is_warning}}
**WARNING**: CPU trending high on {{host.name}} ({{value}}%)
{{/is_warning}}

{{#is_recovery}}
**RESOLVED**: CPU on {{host.name}} returned to normal ({{value}}%)
{{/is_recovery}}
```

### Notification Targets
```
@slack-channel-name          # Slack channel
@pagerduty-service-name      # PagerDuty
@teams-channel               # Microsoft Teams
@opsgenie-service             # Opsgenie
@webhook-name                 # Custom webhook
@user@example.com             # Email
```

### Renotification
- Set renotification interval (e.g., every 30 minutes while alert is active)
- Escalate to different targets after N renotifications
- Include updated snapshot graphs in renotifications

## Monitor Management

### Tags on Monitors
Apply tags to monitors for organization and filtering:
```
team:backend
service:api
env:production
priority:p1
```

### Manage Monitors API
```bash
# List all monitors
curl -s "https://api.datadoghq.com/api/v1/monitor" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Create monitor
curl -s -X POST "https://api.datadoghq.com/api/v1/monitor" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{
    "name": "High CPU on {{host.name}}",
    "type": "metric alert",
    "query": "avg(last_5m):avg:system.cpu.user{env:production} by {host} > 90",
    "message": "CPU is {{value}}% on {{host.name}} @slack-ops",
    "tags": ["team:platform", "env:production"],
    "options": {
      "thresholds": {"critical": 90, "warning": 80},
      "notify_no_data": true,
      "no_data_timeframe": 10,
      "renotify_interval": 30
    }
  }'

# Mute a monitor
curl -s -X POST "https://api.datadoghq.com/api/v1/monitor/<monitor_id>/mute" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"
```

### Terraform
```hcl
resource "datadog_monitor" "high_cpu" {
  name    = "High CPU on {{host.name}}"
  type    = "metric alert"
  query   = "avg(last_5m):avg:system.cpu.user{env:production} by {host} > 90"
  message = "CPU is {{value}}% @slack-ops"

  monitor_thresholds {
    critical = 90
    warning  = 80
  }

  notify_no_data    = true
  no_data_timeframe = 10
  renotify_interval = 30
  tags              = ["team:platform", "env:production"]
}
```

## Downtimes

Schedule alert suppression during maintenance:
```bash
curl -s -X POST "https://api.datadoghq.com/api/v1/downtime" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{
    "scope": "env:production,service:api",
    "start": 1234567890,
    "end": 1234571490,
    "message": "Scheduled maintenance window"
  }'
```

Recurring downtimes: Use `recurrence` field for weekly maintenance windows.

## Best Practices

- **Alert on symptoms, not causes** — Alert on user-facing impact (error rate, latency) not internal mechanics
- **Use recovery thresholds** to prevent flapping (e.g., alert at 90%, recover at 80%)
- **Set evaluation delay** for cloud metrics (15-60s) to avoid false positives from late data
- **Include runbook links** in every alert message
- **Tag monitors** with `team`, `service`, `priority` for filtering and ownership
- **Use composite monitors** instead of duplicate single-metric monitors
- **Review monitors quarterly** — delete or update stale monitors
- **Avoid alert fatigue** — every alert should be actionable; if no one acts on it, remove it
- **Use anomaly detection** for metrics without obvious static thresholds (traffic patterns, seasonal loads)
