# Alertmanager

## Overview

Alertmanager receives alerts from Prometheus (and other sources), then:
1. **Groups** related alerts into single notifications
2. **Deduplicates** repeated alerts
3. **Routes** alert groups to the right receiver
4. **Silences** alerts matching a matcher
5. **Inhibits** downstream alerts when root-cause alerts fire

Port: **9093** | UI: `http://alertmanager:9093`

## Basic Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: "smtp.example.com:587"
  smtp_from: "alerts@example.com"

route:
  group_by: ["alertname", "job"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: "default"
  routes:
    - matchers:
        - severity = "critical"
      receiver: "pagerduty"
      continue: false

    - matchers:
        - severity = "warning"
      receiver: "slack-warnings"

receivers:
  - name: "default"
    email_configs:
      - to: "oncall@example.com"

  - name: "pagerduty"
    pagerduty_configs:
      - service_key: "<integration-key>"
        severity: "{{ if eq .CommonLabels.severity \"critical\" }}critical{{ else }}warning{{ end }}"

  - name: "slack-warnings"
    slack_configs:
      - api_url: "https://hooks.slack.com/services/..."
        channel: "#alerts"
        title: "{{ .CommonAnnotations.summary }}"
        text: "{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}"

inhibit_rules:
  - source_matchers:
      - alertname = "NodeDown"
    target_matchers:
      - severity = "warning"
    equal: ["instance"]
```

## Route Tree

Alerts traverse the route tree top-down. The first matching route wins unless `continue: true`.

```yaml
route:
  receiver: default           # catch-all
  group_by: [alertname]
  routes:
    - matchers:
        - team = "frontend"
      receiver: frontend-slack
      routes:
        - matchers:
            - severity = "critical"
          receiver: frontend-pagerduty   # more specific — wins

    - matchers:
        - team = "backend"
      receiver: backend-slack
```

## Timing Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `group_wait` | 30s | Wait before sending first notification for a new group (allows more alerts to batch) |
| `group_interval` | 5m | Minimum time between notifications for an existing group |
| `repeat_interval` | 4h | How often to re-send a notification for a still-firing alert |
| `resolve_timeout` | 5m | Time after last Prometheus evaluation before an alert is considered resolved |

## Grouping

Alerts with the same label values for `group_by` labels are batched into one notification.

```yaml
route:
  group_by: ["alertname", "cluster", "service"]
```

Use `group_by: ["..."]` (three dots) to group by all labels (no batching).

## Matchers Syntax

New style (>= 0.22, recommended):
```yaml
matchers:
  - alertname = "HighErrorRate"      # exact match
  - severity =~ "critical|warning"   # regex match
  - team != "platform"               # negative match
  - severity !~ "info"               # negative regex
```

Old style (still supported):
```yaml
match:
  severity: critical
match_re:
  service: "^(api|frontend)$"
```

## Receivers

### Email
```yaml
receivers:
  - name: "email"
    email_configs:
      - to: "team@example.com"
        require_tls: true
        auth_username: "alerts@example.com"
        auth_password_file: /etc/alertmanager/secrets/smtp-password
        headers:
          Subject: "[{{ .Status | toUpper }}] {{ .CommonAnnotations.summary }}"
        html: '{{ template "email.default.html" . }}'
```

### Slack
```yaml
receivers:
  - name: "slack"
    slack_configs:
      - api_url: "https://hooks.slack.com/services/T.../B.../..."
        channel: "#alerts-prod"
        color: '{{ if eq .Status "firing" }}{{ if eq .CommonLabels.severity "critical" }}danger{{ else }}warning{{ end }}{{ else }}good{{ end }}'
        title: "{{ .CommonAnnotations.summary }}"
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Runbook:* {{ .Annotations.runbook_url }}
          {{ end }}
        send_resolved: true
```

### PagerDuty
```yaml
receivers:
  - name: "pagerduty"
    pagerduty_configs:
      - routing_key: "<PD-routing-key>"
        severity: '{{ .CommonLabels.severity }}'
        description: "{{ .CommonAnnotations.summary }}"
        details:
          firing: '{{ .Alerts.Firing | len }}'
          instance: '{{ .CommonLabels.instance }}'
```

### OpsGenie
```yaml
receivers:
  - name: "opsgenie"
    opsgenie_configs:
      - api_key: "<api-key>"
        priority: '{{ if eq .CommonLabels.severity "critical" }}P1{{ else }}P2{{ end }}'
```

### Webhook
```yaml
receivers:
  - name: "webhook"
    webhook_configs:
      - url: "http://my-service/alert-hook"
        send_resolved: true
        http_config:
          bearer_token_file: /etc/alertmanager/token
```

## Inhibition Rules

Suppress target alerts when a source alert is firing with matching labels.

```yaml
inhibit_rules:
  # Suppress warnings on a node when the node is down
  - source_matchers:
      - alertname = "NodeDown"
    target_matchers:
      - severity = "warning"
    equal: ["instance"]   # must match on instance label

  # Suppress all app alerts when the cluster is in maintenance
  - source_matchers:
      - alertname = "ClusterMaintenanceWindow"
    target_matchers: []   # suppresses everything
```

## Silences

Silences mute alerts matching a set of matchers for a time window. Managed via UI or API.

```bash
# Create silence via API
curl -s -X POST http://alertmanager:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "instance", "value": "host1:9100", "isRegex": false}],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T04:00:00Z",
    "createdBy": "ops-team",
    "comment": "Planned maintenance"
  }'

# List silences
curl http://alertmanager:9093/api/v2/silences

# Delete silence
curl -X DELETE http://alertmanager:9093/api/v2/silence/<silence-id>
```

## High Availability

Run multiple Alertmanager instances with gossip-based clustering:

```bash
alertmanager \
  --config.file=alertmanager.yml \
  --cluster.listen-address=0.0.0.0:9094 \
  --cluster.peer=alertmanager2:9094 \
  --cluster.peer=alertmanager3:9094
```

Configure Prometheus to send to all instances:
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "alertmanager1:9093"
            - "alertmanager2:9093"
            - "alertmanager3:9093"
```

Alertmanager deduplicates notifications across the cluster.

## Prometheus → Alertmanager Config

```yaml
# prometheus.yml
alerting:
  alertmanagers:
    - scheme: http
      static_configs:
        - targets: ["alertmanager:9093"]
      # Or with service discovery:
    - kubernetes_sd_configs:
        - role: pod
      relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app]
          action: keep
          regex: alertmanager

global:
  # How often to re-send alerts to Alertmanager
  evaluation_interval: 15s
```

## Useful CLI Commands

```bash
# Check config
amtool check-config alertmanager.yml

# Test alert routing (dry run)
amtool --alertmanager.url=http://localhost:9093 config routes test \
  --verify.receivers=pagerduty \
  alertname="HighErrorRate" severity="critical"

# Fire a test alert
amtool --alertmanager.url=http://localhost:9093 alert add \
  alertname="TestAlert" severity="warning" instance="test"

# List active alerts
amtool --alertmanager.url=http://localhost:9093 alert query

# Create silence
amtool --alertmanager.url=http://localhost:9093 silence add \
  alertname="HighErrorRate" --duration=2h --comment="Investigating"
```
