# Dashboarding with Grafana

## Connecting Prometheus to Grafana

1. In Grafana: **Connections → Data Sources → Add data source → Prometheus**
2. Set URL: `http://prometheus:9090`
3. Adjust scrape interval to match Prometheus's `scrape_interval` (default 15s)
4. Save & Test

## Panel Types for Prometheus

| Panel | Best for |
|-------|----------|
| **Time series** | Rates, counters over time, gauges |
| **Gauge** | Current value vs a range (e.g., CPU %) |
| **Stat** | Single current value (e.g., uptime, version) |
| **Bar gauge** | Ranked comparison of a label group |
| **Table** | Multi-column label breakdowns |
| **Heatmap** | Histogram bucket visualization |
| **Histogram** | Distribution of sampled values |
| **Alert list** | Current firing alerts |

## Query Editor

In the Grafana query editor you can use PromQL directly or use the visual builder.

```promql
# Use $__rate_interval instead of hard-coded windows
rate(http_requests_total{job="$job"}[$__rate_interval])

# Use $__interval for recording rules
rate(http_requests_total[$__interval])
```

**`$__rate_interval`** is the recommended variable — it automatically adjusts to 4× the scrape interval to ensure at least 4 data points in every window.

## Template Variables

Variables let users filter dashboards dynamically.

### Label values variable
```
Name: instance
Type: Query
Query: label_values(up{job="$job"}, instance)
```

### Metric names variable
```
Name: metric
Type: Query
Query: metrics(http_.*)
```

### Using variables in queries
```promql
http_requests_total{job="$job", instance="$instance"}
```

Multi-value variable syntax:
```promql
http_requests_total{instance=~"$instance"}   # regex match for multi-select
```

## Common Dashboard Panels

### Request rate
```promql
sum by (status) (rate(http_requests_total{job="$job"}[$__rate_interval]))
```

### Error rate %
```promql
100 * sum(rate(http_requests_total{job="$job", status=~"5.."}[$__rate_interval]))
    / sum(rate(http_requests_total{job="$job"}[$__rate_interval]))
```

### P50/P95/P99 latency
```promql
histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket{job="$job"}[$__rate_interval])))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{job="$job"}[$__rate_interval])))
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{job="$job"}[$__rate_interval])))
```

### Heatmap (latency distribution)
```promql
sum by (le) (rate(http_request_duration_seconds_bucket{job="$job"}[$__rate_interval]))
```
Set visualization to Heatmap, Format: Heatmap.

### CPU usage per instance
```promql
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle",job="node"}[$__rate_interval])) * 100
```

### Memory used
```promql
node_memory_MemTotal_bytes{instance="$instance"} - node_memory_MemAvailable_bytes{instance="$instance"}
```

## Grafana Alerting vs Prometheus Alerting

- **Prometheus alerting** (recommended): define alert rules in Prometheus, route via Alertmanager. Single source of truth.
- **Grafana alerting**: define alerts in Grafana panels. Good for dashboard-driven workflows; supports multiple data sources.

## Provisioning (as Code)

Grafana supports provisioning dashboards and data sources via YAML:

```yaml
# /etc/grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

```yaml
# /etc/grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1
providers:
  - name: default
    folder: Provisioned
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

## Grafana Mixin Pattern

Kubernetes, Prometheus itself, and many exporters ship **Grafana mixins** — pre-built dashboards + alert rules as Jsonnet libraries.

```bash
# Install jsonnet-bundler
go install github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@latest

# Use a mixin
jb install github.com/kubernetes-monitoring/kubernetes-mixin
jsonnet -J vendor mixin.libsonnet | jq '.[]' > dashboard.json
```

## Useful Community Dashboards (Grafana.com)

| Dashboard ID | Description |
|---|---|
| 1860 | Node Exporter Full |
| 6417 | Kubernetes Cluster (kube-state-metrics) |
| 315 | Kubernetes cluster monitoring |
| 3662 | Prometheus 2.0 Overview |
| 9628 | PostgreSQL Database |
