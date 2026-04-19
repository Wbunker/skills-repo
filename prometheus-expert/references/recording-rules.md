# Recording Rules

## Purpose

Recording rules pre-compute expensive or frequently-needed PromQL expressions and store the results as new time series. Benefits:
- Faster dashboard loads (query pre-computed data instead of raw metrics)
- Consistent aggregation across dashboards and alerts
- Enables aggregating over high-cardinality data once
- Allows querying data that would otherwise time out

## Syntax

```yaml
# prometheus.yml
rule_files:
  - "rules/*.yml"
```

```yaml
# rules/http_rates.yml
groups:
  - name: http_rates
    interval: 30s    # optional; defaults to global evaluation_interval
    rules:
      - record: job:http_requests:rate5m
        expr: |
          sum by (job) (
            rate(http_requests_total[5m])
          )
        labels:
          source: recording_rule   # optional extra labels

      - record: job:http_errors:rate5m
        expr: |
          sum by (job) (
            rate(http_requests_total{status=~"5.."}[5m])
          )
```

## Naming Convention

The Prometheus community uses the **colon-separated naming convention**:
```
<aggregation_level>:<metric_name>:<operations>
```

Examples:
```
job:http_requests:rate5m              # rate per job over 5m
instance:node_cpu:rate5m             # rate per instance over 5m
job:http_request_duration:p95_5m     # 95th percentile per job over 5m
job_path:http_requests:rate5m        # rate grouped by job and path
```

Levels (from broad to narrow): cluster, job, instance, job_path, etc.

## Recording Rule Groups

Rules in a group are evaluated sequentially, so later rules can reference earlier ones within the same group. Rules across groups evaluate independently and in parallel.

```yaml
groups:
  - name: node_aggregations
    rules:
      # Step 1: per-instance CPU
      - record: instance:node_cpu_usage:rate5m
        expr: |
          1 - avg without (cpu, mode) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          )

      # Step 2: per-job CPU (uses step 1)
      - record: job:node_cpu_usage:avg5m
        expr: avg by (job) (instance:node_cpu_usage:rate5m)
```

## Common Recording Rule Patterns

### HTTP Request Rate
```yaml
- record: job:http_requests:rate5m
  expr: sum by (job) (rate(http_requests_total[5m]))

- record: job:http_errors:rate5m
  expr: sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))

- record: job:http_error_ratio:rate5m
  expr: job:http_errors:rate5m / job:http_requests:rate5m
```

### Histogram Quantiles
```yaml
- record: job:http_request_duration_seconds:p50_5m
  expr: |
    histogram_quantile(0.50,
      sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
    )

- record: job:http_request_duration_seconds:p95_5m
  expr: |
    histogram_quantile(0.95,
      sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
    )

- record: job:http_request_duration_seconds:p99_5m
  expr: |
    histogram_quantile(0.99,
      sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
    )
```

### Node CPU / Memory
```yaml
- record: instance:node_cpu_usage:rate5m
  expr: |
    1 - avg without(cpu, mode) (
      rate(node_cpu_seconds_total{mode="idle"}[5m])
    )

- record: instance:node_memory_used_bytes:avg
  expr: |
    node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

### Kubernetes Pod CPU
```yaml
- record: namespace_pod_container:container_cpu_usage_seconds:rate5m
  expr: |
    sum by (namespace, pod, container) (
      rate(container_cpu_usage_seconds_total{container!=""}[5m])
    )
```

## Rule File Validation

```bash
# Validate rule files before deployment
promtool check rules rules/http_rates.yml

# Test rules against recorded data
promtool test rules tests/http_rates_test.yml
```

## Unit Testing Recording Rules

```yaml
# tests/http_rates_test.yml
rule_files:
  - ../rules/http_rates.yml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{job="api", status="200"}'
        values: "0 60 120 180 240 300"
      - series: 'http_requests_total{job="api", status="500"}'
        values: "0 3 6 9 12 15"
    promql_expr_test:
      - expr: job:http_requests:rate5m
        eval_time: 5m
        exp_samples:
          - labels: '{job="api"}'
            value: 1.0   # (300-0)/(5*60) = 1 req/sec
```

## Reload Rules Without Restart

```bash
# Requires --web.enable-lifecycle
curl -X POST http://localhost:9090/-/reload

# Or via SIGHUP
kill -HUP $(pgrep prometheus)
```

## Best Practices

- Record rules at the **coarsest granularity you'll query** — don't pre-compute per-pod if you only ever query per-job.
- Use recording rules in **alert `expr`** to keep alert expressions readable.
- Set `interval` on rule groups where you need finer granularity than `evaluation_interval`.
- Keep rule groups focused — one group per logical subsystem.
- Test rules with `promtool test rules` as part of CI.
- Record the intermediate steps of complex multi-step queries to make them debuggable.
