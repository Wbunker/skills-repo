# Federation and Cross-DC Monitoring

## What Is Federation?

Federation allows one Prometheus server to scrape a subset of metrics from another Prometheus server. The scraping server stores the federated metrics locally.

Use cases:
- Hierarchical federation: global Prometheus aggregates from datacenter-level Prometheus instances
- Cross-team aggregation: central monitoring team queries all team Prometheus instances
- Cross-DC monitoring with aggregated dashboards

## Federation Endpoint

Every Prometheus server exposes `/federate`:

```
GET /federate?match[]=<series_selector>&match[]=<series_selector>
```

Returns a text exposition document with the matched series.

```bash
# Fetch all http_requests_total metrics from a Prometheus instance
curl 'http://prometheus1:9090/federate?match[]=http_requests_total'

# Multiple selectors
curl 'http://prometheus1:9090/federate?match[]={job="api"}&match[]=up'
```

## Hierarchical Federation

```
┌──────────────────────────────────────────────────────┐
│                  Global Prometheus                    │
│  Scrapes /federate from DC-level Prometheus servers  │
└────────────────┬─────────────────┬───────────────────┘
                 │                 │
         ┌───────▼───────┐ ┌───────▼───────┐
         │  DC1 Prometheus│ │  DC2 Prometheus│
         │ (scrapes local │ │ (scrapes local │
         │   targets)     │ │   targets)     │
         └───────────────┘ └───────────────┘
```

### Global Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: "federate"
    scrape_interval: 15s
    honor_labels: true    # preserve original job/instance labels
    metrics_path: /federate
    params:
      match[]:
        - '{job="api"}'                          # all api metrics
        - 'http_requests_total'                  # specific metric
        - '{__name__=~"job:.*"}'                 # only recording rules
    static_configs:
      - targets:
          - "dc1-prometheus:9090"
          - "dc2-prometheus:9090"
        labels:
          datacenter: "dc1"   # add datacenter label
      - targets:
          - "dc2-prometheus:9090"
        labels:
          datacenter: "dc2"
```

**Always use `honor_labels: true` for federation** — otherwise `job` and `instance` labels from the source are overwritten.

## What to Federate

Federate selectively — only aggregate the metrics you need globally:

**Good to federate:**
- Recording rule results: `{__name__=~"job:.*"}` — pre-aggregated, low cardinality
- Key SLI/SLO metrics
- Alerting rule expressions (if you want global alerting)

**Avoid federating:**
- Raw high-cardinality metrics (e.g., per-request histograms)
- All metrics (`{__name__=~".+"}`) — will overwhelm the global server

## Cross-DC Alerting

Two patterns:

### Pattern 1: Alert at the DC level
Each DC Prometheus fires its own alerts. Alertmanagers in each DC deduplicate and route.

```
DC1: Prometheus → Alertmanager1
DC2: Prometheus → Alertmanager2
                    ↕ (cluster gossip)
         PagerDuty / Slack (deduped)
```

Pros: resilient — no single point of failure for alerting.

### Pattern 2: Alert at the global level
Federate aggregated metrics to global Prometheus. Alert from the global server only.

```
Global Prometheus (with recording rule results from each DC)
        → Global Alertmanager → PagerDuty
```

Pros: single set of alert rules. Cons: global Prometheus is now on the critical path.

## Federation vs Thanos

| | Federation | Thanos / Mimir |
|--|--|--|
| Architecture | Pull (global scrapes /federate) | Push (sidecar/remote_write) or sidecar reads |
| Latency | Adds one scrape delay | Near-real-time (sidecar) |
| Cardinality | Must pre-aggregate | Can handle high cardinality |
| Long-term retention | Local only | Object storage (years) |
| HA | Manual setup | Built-in deduplication |
| Operational complexity | Low | Higher |

**Recommendation**: Use federation for simple cross-team/cross-DC aggregation of pre-aggregated metrics. Use Thanos or Mimir for true long-term storage, HA, and global querying of raw data.

## Prometheus Remote Write for Cross-DC

An alternative to federation for moving data across DCs:

```yaml
# DC-local Prometheus
remote_write:
  - url: "http://global-prometheus-or-thanos:9091/api/v1/write"
    write_relabel_configs:
      # Only send aggregated recording rules
      - source_labels: [__name__]
        regex: "job:.*|instance:.*"
        action: keep
```

This avoids the additional scrape delay of federation and is more reliable under network partitions (queue with backpressure).

## Limiting Federation Exposure

Protect the `/federate` endpoint:

```yaml
# web.yml (Prometheus >= 2.24)
basic_auth_users:
  global-prometheus: $2y$12$...
```

Or use network-level controls (firewall, VPN, mTLS).

## Monitoring the Global View

After federation, you can write cross-DC queries:

```promql
# Total requests across all DCs
sum by (job) (http_requests_total)

# Per-DC comparison
sum by (datacenter, job) (http_requests_total)

# Which DC has the highest error rate?
topk(3, sum by (datacenter) (
  rate(http_requests_total{status=~"5.."}[5m])
))
```
