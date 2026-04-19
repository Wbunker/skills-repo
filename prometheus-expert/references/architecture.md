# Prometheus Architecture & Data Model

## What Is Prometheus?

Prometheus is an open-source systems monitoring and alerting toolkit originally built at SoundCloud. It is now a CNCF graduated project.

Key characteristics:
- **Pull-based**: Prometheus scrapes HTTP endpoints (`/metrics`) at configurable intervals.
- **Single-binary server**: no external dependencies (no ZooKeeper, no Kafka).
- **Time-series database (TSDB)**: data stored locally on disk in a custom columnar format.
- **Dimensional data model**: metrics identified by name + label set.

## Data Model

Every sample is a `(labels, timestamp, value)` triple. Labels are the primary grouping mechanism.

```
<metric_name>{<label_name>="<label_value>", ...} <float64_value> [<unix_ms_timestamp>]
```

Example:
```
http_requests_total{method="POST", handler="/api/v1/push", status="200"} 1234 1704067200000
```

- **metric_name**: snake_case, describes what is measured.
- **label names**: snake_case, alphanumeric + underscore.
- **Label values**: UTF-8 strings.
- The empty label set `{}` identifies the metric name alone.
- `__` prefix is reserved for internal Prometheus use.

## Metric Types (client-side concept)

| Type | Description | Use case |
|------|-------------|----------|
| **Counter** | Monotonically increasing float64 | Requests, errors, bytes sent |
| **Gauge** | Arbitrary float64, can go up or down | CPU temp, queue depth, memory |
| **Histogram** | Observations in configurable buckets + `_sum` + `_count` | Request latency, response sizes |
| **Summary** | Quantiles computed client-side + `_sum` + `_count` | Latency when buckets aren't known upfront |

Prefer **Histogram** over Summary in most cases — Histograms are aggregatable across instances; Summaries are not.

## TSDB Internals

- Data organized in **2-hour blocks** on disk; current data written to an in-memory head block.
- Each block: `chunks/` (compressed samples), `index/` (label index), `meta.json`, `tombstones`.
- **Compaction** merges older blocks and applies tombstone deletions.
- Default retention: **15 days** (configurable via `--storage.tsdb.retention.time` or `--storage.tsdb.retention.size`).
- TSDB WAL (write-ahead log) protects in-memory data across restarts.

## Prometheus Components

```
           +-----------+
           |  Targets  |  (apps, exporters, /metrics)
           +-----+-----+
                 | scrape (HTTP pull)
           +-----v-----+
           |  Prometheus|  (scrape, store, query, alert)
           |   Server  |
           +--+-----+--+
              |     |
      rules/  |     | remote_write
      alerts  |     v
              |  +----------+
              |  | Remote   |  (Thanos, Mimir, VictoriaMetrics)
              |  | Storage  |
              |  +----------+
              |
        +-----v------+
        |Alertmanager|
        +-----+------+
              |
        (email, Slack, PagerDuty…)

                 Grafana <-- PromQL queries --> Prometheus
```

## Scrape Lifecycle

1. Prometheus evaluates `scrape_configs` to discover targets.
2. At each scrape interval it performs an HTTP GET to `<scheme>://<host>:<port><metrics_path>`.
3. Successful response is parsed; each line becomes a time-series sample.
4. Samples stored in TSDB with automatic `job` and `instance` labels added.
5. Scrape metadata (`up`, `scrape_duration_seconds`, `scrape_samples_post_metric_relabeling`) auto-generated.

## Key Configuration File Sections

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: "example"
    static_configs:
      - targets: ["localhost:8080"]
```
