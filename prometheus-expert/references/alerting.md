# Alerting Rules

## Overview

Alerting rules are PromQL expressions that, when true, fire an alert. Prometheus evaluates them on every `evaluation_interval` and sends firing alerts to Alertmanager.

## Syntax

```yaml
# rules/alerts.yml
groups:
  - name: example
    rules:
      - alert: HighErrorRate
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: |
            Error rate is {{ $value | humanizePercentage }} on {{ $labels.job }}.
            This has been above 5% for 5 minutes.
          runbook_url: "https://runbooks.example.com/high-error-rate"
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `alert` | Yes | Alert name (PascalCase by convention) |
| `expr` | Yes | PromQL expression — fires when any returned series has a non-zero value |
| `for` | No | Pending duration before firing (prevents flapping) |
| `labels` | No | Extra labels merged onto the alert |
| `annotations` | No | Human-readable info; support Go template syntax |

## Alert States

1. **Inactive** — expression evaluates to no samples or zero
2. **Pending** — expression is true but `for` duration not yet elapsed
3. **Firing** — `for` duration elapsed; alert sent to Alertmanager

## Template Variables in Annotations

```
{{ $labels.job }}              # label from the alert
{{ $labels.instance }}
{{ $value }}                   # the numeric value of the expression
{{ $value | humanize }}        # human-readable: 1234 → 1.23k
{{ $value | humanizePercentage }}  # 0.05 → 5%
{{ $value | humanizeDuration }}    # 93784 → 1d 2h 3m 4s
```

## Alert Naming Conventions

PascalCase, descriptive:
```
HighErrorRate
DiskWillFillIn4Hours
InstanceDown
PrometheusConfigReloadFailed
KubePodCrashLooping
```

## Common Alert Patterns

### Instance down
```yaml
- alert: InstanceDown
  expr: up == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Instance {{ $labels.instance }} is down"
    description: "{{ $labels.instance }} ({{ $labels.job }}) has been down for 5 minutes."
```

### Missing scrape target (absent)
```yaml
- alert: PrometheusMissingTarget
  expr: absent(up{job="my-critical-service"})
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "No targets for job my-critical-service"
```

### High CPU
```yaml
- alert: HighCPUUsage
  expr: |
    100 - avg by (instance) (
      rate(node_cpu_seconds_total{mode="idle"}[5m])
    ) * 100 > 85
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "High CPU on {{ $labels.instance }}"
    description: "CPU usage is {{ $value | humanize }}% for 15m."
```

### Disk filling up
```yaml
- alert: DiskWillFillIn4Hours
  expr: predict_linear(node_filesystem_avail_bytes[1h], 4 * 3600) < 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Disk full predicted in 4h on {{ $labels.instance }}"
    description: "Filesystem {{ $labels.mountpoint }} will fill within 4 hours."
```

### High memory
```yaml
- alert: HighMemoryUsage
  expr: |
    (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
    / node_memory_MemTotal_bytes > 0.90
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage on {{ $labels.instance }}"
```

### SLO violation — error budget
```yaml
- alert: ErrorBudgetBurning
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      / sum(rate(http_requests_total[1h]))
    ) > (1 - 0.999) * 14.4   # 14.4x burn rate on 99.9% SLO
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Error budget burning at high rate"
```

### Kubernetes pod crash looping
```yaml
- alert: KubePodCrashLooping
  expr: |
    increase(kube_pod_container_status_restarts_total[15m]) > 3
  for: 15m
  labels:
    severity: critical
  annotations:
    summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"
```

## Inhibition (in Alertmanager)

Use inhibition to suppress downstream alerts when a root cause alert is firing. Example: suppress all app alerts when the node is down.

See `references/alertmanager.md` for inhibit_rules.

## Alert Testing

```bash
# Validate rule files
promtool check rules rules/alerts.yml

# Unit test alerts
promtool test rules tests/alerts_test.yml
```

Test file example:
```yaml
rule_files:
  - ../rules/alerts.yml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'up{job="api", instance="host1:8080"}'
        values: "1 1 0 0 0 0 0"   # goes down at minute 2
    alert_rule_test:
      - eval_time: 6m
        alertname: InstanceDown
        exp_alerts:
          - exp_labels:
              job: api
              instance: "host1:8080"
              severity: critical
            exp_annotations:
              summary: "Instance host1:8080 is down"
```

## Severity Levels (Convention)

| Severity | Meaning | Page? |
|----------|---------|-------|
| `critical` | Production impact, SLO at risk | Yes — immediate |
| `warning` | Needs attention soon, not yet impacting | Yes — business hours |
| `info` | Informational, no action needed | No |

Set via `labels.severity` and use in Alertmanager routing.
