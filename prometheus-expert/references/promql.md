# PromQL — Prometheus Query Language

## Data Types

| Type | Description | Example |
|------|-------------|---------|
| **Instant vector** | Set of time series, one sample per series at a point in time | `http_requests_total` |
| **Range vector** | Set of time series over a time window | `http_requests_total[5m]` |
| **Scalar** | Single float64 number | `1.5` |
| **String** | String literal (rarely used) | `"hello"` |

## Selectors

```promql
# All time series for metric
http_requests_total

# Filtered by label
http_requests_total{job="api", status="200"}

# Regex match
http_requests_total{status=~"2.."}

# With offset (look back in time)
http_requests_total offset 5m

# With @ modifier (absolute timestamp)
http_requests_total @ 1609459200
```

## Range Vectors

Range vector selectors return all samples within the bracket duration:
```promql
http_requests_total[5m]    # samples from last 5 minutes
rate(http_requests_total[5m])  # per-second rate over 5m window
```

Duration units: `ms`, `s`, `m`, `h`, `d`, `w`, `y`

## Operators

### Arithmetic
```promql
node_memory_MemTotal_bytes - node_memory_MemFree_bytes
http_requests_total * 1000
```

### Comparison (filter or boolean)
```promql
http_requests_total > 100         # filter: keep series where value > 100
http_requests_total > bool 100    # return 0/1 instead of filtering
```

Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`

### Logical/Set
```promql
http_requests_total or http_errors_total    # union
http_requests_total and http_errors_total   # intersection (same labels)
http_requests_total unless http_errors_total  # difference
```

### Vector Matching
```promql
# One-to-one: labels must match exactly
method_code:http_errors:rate5m / method_code:http_requests:rate5m

# Many-to-one with on() / ignoring()
http_errors_total / ignoring(status) group_left http_requests_total

# on() restricts matching labels; ignoring() excludes labels from matching
```

## Key Functions

### Rate and Delta
```promql
rate(http_requests_total[5m])          # per-second rate (for counters, handles resets)
irate(http_requests_total[5m])         # instantaneous rate (last two samples)
increase(http_requests_total[1h])      # total increase over window
delta(node_cpu_temp_celsius[10m])      # change for gauges
idelta(node_cpu_temp_celsius[10m])     # instantaneous delta
```

**Rule**: use `rate()` not `irate()` for alerting — `irate()` is too spiky. Use `rate()` windows >= 4x the scrape interval.

### Aggregation
```promql
sum(http_requests_total)                          # sum all series
sum by (status) (http_requests_total)             # sum, grouped by status
sum without (instance) (http_requests_total)      # sum, drop instance label
avg(node_cpu_seconds_total)
max(node_cpu_seconds_total)
min(node_cpu_seconds_total)
count(up == 1)                                    # count of up targets
count_values("version", build_info)              # count by label value
topk(5, rate(http_requests_total[5m]))           # top 5 series
bottomk(5, node_filesystem_avail_bytes)
stddev(http_request_duration_seconds_sum)
```

### Time and Staleness
```promql
time()                        # current Unix timestamp as scalar
timestamp(up)                 # timestamp of the last sample for each series
absent(up{job="api"})        # returns 1 if no series match (useful for alerting on missing targets)
absent_over_time(up[5m])     # returns 1 if no samples in the window
```

### Math
```promql
round(x, 0.1)       # round to nearest 0.1
clamp(x, 0, 100)    # clamp value between min and max
clamp_min(x, 0)
clamp_max(x, 100)
abs(x)
sqrt(x)
exp(x)
ln(x)
log2(x)
log10(x)
```

### Histogram Functions
```promql
# Calculate quantile from histogram buckets
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Native histograms (Prometheus >= 2.40)
histogram_quantile(0.95, rate(http_request_duration_seconds[5m]))

# Fraction of requests under 300ms
sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m]))
  / sum(rate(http_request_duration_seconds_count[5m]))
```

### Label Manipulation
```promql
label_replace(up, "host", "$1", "instance", "(.*):.*")  # extract host from instance
label_join(up, "address", ":", "host", "port")          # join labels into new label
```

### Subqueries
```promql
# Max rate over the last hour, evaluated at 1m resolution
max_over_time(rate(http_requests_total[5m])[1h:1m])
```

Syntax: `<expr>[<range>:<resolution>]`

### Predict
```promql
# Predict disk full in 4 hours using linear regression
predict_linear(node_filesystem_avail_bytes[1h], 4 * 3600) < 0
```

### Changes and Resets
```promql
changes(process_start_time_seconds[1h])      # how many times a gauge changed
resets(http_requests_total[1h])              # how many counter resets
deriv(node_cpu_temp_celsius[10m])            # per-second derivative (linear regression)
```

## Practical Patterns

### Error rate
```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))
```

### Apdex score
```promql
(
  sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m]))
  + sum(rate(http_request_duration_seconds_bucket{le="1.2"}[5m]))
) / 2 / sum(rate(http_request_duration_seconds_count[5m]))
```

### CPU usage (%)
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory usage
```promql
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

### Disk fill rate / time remaining
```promql
predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"}[6h], 4 * 3600)
```

## Recording Rules

Pre-compute expensive queries and store results as new metrics:

```yaml
groups:
  - name: http_rates
    interval: 30s   # optional override
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))

      - record: job:http_errors:rate5m
        expr: sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
```

Naming convention: `level:metric:operations` — e.g., `job:http_requests:rate5m`

See `references/recording-rules.md` for more detail.
