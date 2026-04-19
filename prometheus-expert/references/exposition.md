# Exposition Format

## Overview

Prometheus scrapes targets by fetching their `/metrics` HTTP endpoint. The response is in the **Prometheus text exposition format** (or protobuf, negotiated via Accept header).

## Text Format

Plain UTF-8, one sample per line. MIME type: `text/plain; version=0.0.4`.

```
# HELP http_requests_total The total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total{method="post",code="200"} 1027 1395066363000
http_requests_total{method="post",code="400"}    3 1395066363000

# HELP http_request_duration_seconds A histogram of the request duration.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.05"} 24054
http_request_duration_seconds_bucket{le="0.1"}  33444
http_request_duration_seconds_bucket{le="0.25"} 100392
http_request_duration_seconds_bucket{le="0.5"}  129389
http_request_duration_seconds_bucket{le="1"}    133988
http_request_duration_seconds_bucket{le="+Inf"} 144320
http_request_duration_seconds_sum  53423
http_request_duration_seconds_count 144320

# HELP rpc_duration_seconds A summary of RPC durations.
# TYPE rpc_duration_seconds summary
rpc_duration_seconds{quantile="0.01"} 3102
rpc_duration_seconds{quantile="0.05"} 3272
rpc_duration_seconds{quantile="0.5"}  4773
rpc_duration_seconds{quantile="0.9"}  9001
rpc_duration_seconds{quantile="0.99"} 76656
rpc_duration_seconds_sum 1.7560473e+07
rpc_duration_seconds_count 2693
```

### Line Syntax
```
metric_name ["{" label_name "=" `"` label_value `"` { "," label_name "=" `"` label_value `"` } [","] "}"] value [timestamp]
```

- Timestamp is Unix milliseconds (optional; Prometheus uses scrape time if absent).
- `# HELP` and `# TYPE` lines are optional but strongly recommended.
- Valid TYPE values: `counter`, `gauge`, `histogram`, `summary`, `untyped`.

## OpenMetrics Format

An evolution of the text format, now an IETF standard. MIME: `application/openmetrics-text; version=1.0.0`.

Key differences:
- Counters must have a `_total` suffix (enforced, not just convention).
- `# EOF` required at end of output.
- Supports `exemplars` (trace IDs attached to histogram observations).
- `created` timestamp support for counters/histograms/summaries.

```
# HELP http_requests_total HTTP requests
# TYPE http_requests_total counter
http_requests_total_total{method="GET"} 1234.0 # {trace_id="abc123"} 1.0 1690000000.000
# EOF
```

Prometheus will negotiate OpenMetrics if the client advertises it in Accept header (Prometheus >= 2.23).

## Protobuf Format

Binary format, more efficient. Negotiated via `Accept: application/vnd.google.protobuf;proto=io.prometheus.client.MetricFamily;encoding=delimited`.

Most client libraries support both text and protobuf. The protobuf format is preferred for high-cardinality targets.

## Writing a Custom Exporter

Minimal Go exporter pattern:
```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

type myCollector struct {
    myMetric *prometheus.Desc
}

func newMyCollector() *myCollector {
    return &myCollector{
        myMetric: prometheus.NewDesc(
            "my_metric",
            "Description of my metric.",
            []string{"label1"}, nil,
        ),
    }
}

func (c *myCollector) Describe(ch chan<- *prometheus.Desc) {
    ch <- c.myMetric
}

func (c *myCollector) Collect(ch chan<- prometheus.Metric) {
    value := fetchMyValue()
    ch <- prometheus.MustNewConstMetric(c.myMetric, prometheus.GaugeValue, value, "val1")
}

func main() {
    prometheus.MustRegister(newMyCollector())
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9100", nil)
}
```

## Textfile Collector (Node Exporter)

Write files to a directory; Node Exporter will pick them up:
```bash
# Write from a cron job
cat > /var/lib/node_exporter/textfile_collector/my_job.prom << 'EOF'
# HELP my_batch_last_run_timestamp Unix timestamp of last successful batch run.
# TYPE my_batch_last_run_timestamp gauge
my_batch_last_run_timestamp $(date +%s)
EOF
```

Files must have `.prom` extension and be valid Prometheus text format.

## Scrape Best Practices

- Keep scrape duration well under `scrape_interval` (check `scrape_duration_seconds`).
- Avoid generating metrics dynamically per request — pre-register all metric descriptors at startup.
- Compression: Prometheus supports `Accept-Encoding: gzip`; most libraries respond with gzip automatically.
- Set `Content-Type` response header correctly so Prometheus can choose the right parser.
