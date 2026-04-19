# Getting Started with Prometheus

## Installation

### Binary
```bash
# Download from https://prometheus.io/download/
tar xvfz prometheus-*.tar.gz
cd prometheus-*/
./prometheus --config.file=prometheus.yml
```

### Docker
```bash
docker run -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Kubernetes (kube-prometheus-stack Helm chart)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
```

## Minimal prometheus.yml

```yaml
global:
  scrape_interval: 15s       # How often to scrape targets
  evaluation_interval: 15s   # How often to evaluate rules

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]  # Prometheus scrapes itself
```

## Important CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--config.file` | `prometheus.yml` | Config file path |
| `--storage.tsdb.path` | `data/` | Local data directory |
| `--storage.tsdb.retention.time` | `15d` | How long to keep data |
| `--storage.tsdb.retention.size` | `0` (disabled) | Max size (e.g. `10GB`) |
| `--web.listen-address` | `0.0.0.0:9090` | Address to listen on |
| `--web.external-url` | — | Public URL (needed for alerts) |
| `--web.enable-admin-api` | false | Enable admin endpoints (delete series) |
| `--log.level` | `info` | `debug`, `info`, `warn`, `error` |

## Configuration Reloading

```bash
# Send SIGHUP
kill -HUP <pid>

# Or POST to /-/reload (requires --web.enable-lifecycle)
curl -X POST http://localhost:9090/-/reload
```

## Verification

- Web UI: `http://localhost:9090`
- Metrics: `http://localhost:9090/metrics`
- Targets page: `http://localhost:9090/targets`
- Config page: `http://localhost:9090/config`

## First Queries to Try

```promql
# Is Prometheus up?
up

# How many samples ingested per second?
rate(prometheus_tsdb_head_samples_appended_total[5m])

# How many active series?
prometheus_tsdb_head_series

# How long is the config reload taking?
prometheus_config_last_reload_successful
```

## Common Scrape Config Patterns

### With basic auth
```yaml
scrape_configs:
  - job_name: "my-app"
    basic_auth:
      username: "prom"
      password_file: /etc/prometheus/secrets/password
    static_configs:
      - targets: ["myapp:8080"]
```

### With TLS
```yaml
scrape_configs:
  - job_name: "secure-app"
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/ca.crt
      insecure_skip_verify: false
    static_configs:
      - targets: ["secureapp:8443"]
```

### Non-default metrics path
```yaml
scrape_configs:
  - job_name: "haproxy"
    metrics_path: /haproxy?stats;csv
    static_configs:
      - targets: ["haproxy:1936"]
```

## Pushgateway (for short-lived jobs)

```bash
# Push a metric
echo "job_duration_seconds 30.5" | \
  curl --data-binary @- http://pushgateway:9091/metrics/job/batch_import

# Prometheus scrape config for Pushgateway
scrape_configs:
  - job_name: "pushgateway"
    honor_labels: true   # preserve labels set by the job
    static_configs:
      - targets: ["pushgateway:9091"]
```

Use Pushgateway only for batch/cron jobs that exit before Prometheus can scrape them. Do not use it as a general-purpose event bus.
