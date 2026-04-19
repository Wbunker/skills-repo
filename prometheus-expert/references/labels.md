# Labels, Relabeling, and Cardinality

## Labels Overview

Labels are key=value pairs that distinguish time series with the same metric name.

```promql
http_requests_total{job="api", instance="10.0.0.1:8080", method="GET", status="200"}
```

- Automatically added by Prometheus: `job`, `instance`
- Added by service discovery: varies by SD mechanism
- Added by instrumentation: application-defined
- `__` prefix: internal/temporary labels (stripped before storage)

## Label Selectors in PromQL

```promql
# Exact match
http_requests_total{status="200"}

# Regex match
http_requests_total{status=~"2.."}

# Negative exact match
http_requests_total{status!="500"}

# Negative regex
http_requests_total{status!~"5.."}
```

## Relabeling

Relabeling transforms labels during the scrape pipeline. It happens in two places:

### 1. `relabel_configs` (before scrape — target labels)

Applied to discovered targets. Can drop targets, modify labels, or set the scrape address.

```yaml
scrape_configs:
  - job_name: "my-service"
    relabel_configs:
      # Drop targets in staging environment
      - source_labels: [__meta_consul_tags]
        regex: ".*,staging,.*"
        action: drop

      # Use consul service name as job label
      - source_labels: [__meta_consul_service]
        target_label: job

      # Rewrite metrics path from metadata
      - source_labels: [__meta_consul_service_metadata_metrics_path]
        target_label: __metrics_path__
        regex: (.+)
```

### 2. `metric_relabel_configs` (after scrape — metric labels)

Applied to scraped samples before storage. Can drop expensive metrics, rename labels.

```yaml
scrape_configs:
  - job_name: "my-service"
    metric_relabel_configs:
      # Drop high-cardinality internal metrics
      - source_labels: [__name__]
        regex: "go_gc_.*"
        action: drop

      # Rename a label
      - source_labels: [exported_job]
        target_label: job

      # Keep only specific metrics
      - source_labels: [__name__]
        regex: "http_requests_total|http_request_duration_seconds.*"
        action: keep
```

## Relabeling Actions

| Action | Description |
|--------|-------------|
| `replace` | (default) Set `target_label` from `replacement` (regex capture groups supported) |
| `keep` | Keep targets/samples where `source_labels` match `regex` |
| `drop` | Drop targets/samples where `source_labels` match `regex` |
| `labelmap` | Copy labels matching `regex` to new names per `replacement` |
| `labeldrop` | Remove labels matching `regex` |
| `labelkeep` | Remove labels NOT matching `regex` |
| `hashmod` | Hash `source_labels` and take modulo (for sharding) |
| `lowercase` | Lowercase the label value |
| `uppercase` | Uppercase the label value |

## Common Relabeling Patterns

### Extract port from address
```yaml
- source_labels: [__address__]
  regex: "([^:]+)(?::\\d+)?"
  replacement: "${1}:9100"
  target_label: __address__
```

### Multi-label concatenation
```yaml
- source_labels: [env, region]
  separator: "-"
  target_label: env_region
```

### Strip label prefix
```yaml
- regex: "container_label_com_example_(.*)"
  replacement: "${1}"
  action: labelmap
```

## Cardinality

Cardinality = number of unique time series. High cardinality = memory pressure.

### Calculating cardinality
```promql
# Total number of active time series
prometheus_tsdb_head_series

# Series per job
count by (job) ({__name__=~".+"})

# Top 10 highest cardinality metrics
topk(10, count by (__name__) ({__name__=~".+"}))
```

### Cardinality anti-patterns
- Labels with user IDs, IP addresses, UUIDs, free-form strings
- Labels whose values are timestamps or request IDs
- Unbounded label values (e.g., URL paths without normalization)

### Cardinality best practices
- Keep label value cardinality bounded (< ~100 unique values per label)
- Normalize URL paths before using as labels: `/user/123` → `/user/:id`
- Use `metric_relabel_configs` to drop high-cardinality labels before storage
- Use `--storage.tsdb.max-block-duration` and retention tuning for large deployments

## `honor_labels`

When scraping Pushgateway or federation endpoints, the scraped data already has `job` and `instance` labels. Use `honor_labels: true` to preserve them instead of overwriting with Prometheus's own labels.

```yaml
scrape_configs:
  - job_name: "pushgateway"
    honor_labels: true
    static_configs:
      - targets: ["pushgateway:9091"]
```

## `honor_timestamps`

When `true`, Prometheus uses the timestamps from the scraped data instead of the scrape time. Default `false`. Use with caution — stale timestamps can confuse staleness handling.
