# Cloud Monitoring — Capabilities

## Purpose

Full-stack observability platform for GCP services, multi-cloud (AWS), and on-premises infrastructure. Provides metrics collection, alerting, dashboards, uptime monitoring, SLO tracking, and Managed Prometheus. Integrates natively with all GCP services (automatic metrics ingestion without configuration) and supports custom instrumentation via OpenTelemetry and the Cloud Monitoring API.

---

## Core Concepts

| Concept | Description |
|---|---|
| Metric | Named, typed time-series measurement (e.g., `compute.googleapis.com/instance/cpu/utilization`) |
| Metric type | Fully qualified metric name; defines type (gauge, delta, cumulative), units, labels |
| Monitored resource | The GCP resource emitting metrics (gce_instance, k8s_container, gcs_bucket, etc.) |
| Metric descriptor | Schema for a metric type: labels, value type, units, display name |
| Time series | Sequence of data points for a specific metric + resource + label combination |
| Alignment period | Time interval for aggregating time series points (e.g., align to 60-second buckets) |
| Aligner | Function applied within an alignment period (ALIGN_MEAN, ALIGN_SUM, ALIGN_MAX, ALIGN_RATE) |
| Reducer | Function combining multiple time series into one (REDUCE_SUM, REDUCE_MEAN, REDUCE_COUNT) |
| Alerting policy | Conditions + notification channels that fire when a condition is met |
| Notification channel | Where to send alert notifications (email, PagerDuty, Slack, Pub/Sub, webhook, Cloud Mobile App) |
| Uptime check | Periodic HTTP/HTTPS/TCP probe from global locations; alerts if check fails |
| Dashboard | Collection of widgets displaying metrics, charts, logs, SLOs |
| SLO | Service Level Objective: target availability or latency target for a service |
| SLI | Service Level Indicator: the metric measured to evaluate SLO compliance |
| Error budget | Remaining tolerance for SLO violation within a period (e.g., 0.1% in 30 days) |
| Workspace | Metrics scope; one project hosts the workspace; other projects added as monitored projects |
| Snooze | Temporarily suppress an alerting policy's notifications |

---

## Metric Types

### Built-in GCP Metrics (automatic)
- **Compute Engine**: CPU utilization, disk I/O, network throughput, memory (via Ops Agent)
- **GKE/Kubernetes**: container CPU/memory/restart count, node resource usage, pod count
- **Cloud SQL**: connections, queries/sec, disk utilization, replication lag
- **Cloud Storage**: request count, bytes transferred, object count
- **BigQuery**: slot utilization, bytes processed, table row count
- **Cloud Run**: request count, latency, container instance count, CPU allocation
- **Cloud Functions**: execution count, execution time, error count
- **Pub/Sub**: undelivered message count, oldest unacked message age, publish/subscribe rates

### Custom Metrics
- Send via Cloud Monitoring API, OpenTelemetry Collector, or client libraries
- Up to 10,000 custom metric types per project
- Custom metric types: `custom.googleapis.com/` prefix
- Types: GAUGE (snapshot), CUMULATIVE (monotonically increasing), DELTA (change since last point)

### Log-Based Metrics
- Created from Cloud Logging via filter expressions
- Counter metrics: count log entries matching a filter
- Distribution metrics: extract numeric values from log fields (e.g., response latency)
- Appear as `logging.googleapis.com/user/` metrics

---

## Managed Service for Prometheus (GMP)

Fully managed Prometheus monitoring for GKE and other compute:

- **Drop-in replacement**: use existing Prometheus scrape configs and recording/alerting rules
- **Global query service**: query across all GKE clusters globally with a single PromQL query
- **Long-term retention**: metrics stored in Cloud Monarch (Google's time-series DB); no data loss
- **Components**:
  - `PodMonitoring` CRD: defines scrape targets per-namespace
  - `ClusterPodMonitoring` CRD: cluster-wide scrape targets
  - `Rules` CRD: Prometheus recording and alerting rules
  - Managed Collector: DaemonSet deploying prometheus-engine collectors
- **Query**: use Cloud Monitoring Query Language (MQL) or PromQL via the GMP frontend service
- **Grafana integration**: configure Grafana datasource pointing to GMP frontend
- **Alerting**: GMP rules trigger Cloud Monitoring alerts via managed rules

```yaml
# Example PodMonitoring CRD
apiVersion: monitoring.googleapis.com/v1
kind: PodMonitoring
metadata:
  name: my-app-monitoring
  namespace: production
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

## SLO Monitoring

### Concepts
- **SLI (Service Level Indicator)**: the metric measured (e.g., % of requests with latency < 200ms, % of successful requests)
- **SLO (Service Level Objective)**: target for the SLI over a rolling window (e.g., 99.9% of requests succeed over 30 days)
- **Error budget**: (1 - SLO target) × window = total allowed failures (e.g., 0.1% × 30 days = 43.2 minutes)
- **Error budget burn rate**: how quickly the error budget is being consumed vs. expected rate (1.0 = normal)

### SLI Types
- **Request-based**: count of good requests / total requests (availability, latency)
- **Windows-based**: fraction of time windows where performance was good

### Burn Rate Alerting
- **Fast burn**: 2 alert windows (short = 5 min, long = 1 hour); fires at 14× burn rate; indicates immediate production impact
- **Slow burn**: 2 alert windows (short = 6 hours, long = 3 days); fires at 1× burn rate; indicates budget is slowly draining
- Google SRE recommended: 4 alerts (2 fast burn + 2 slow burn) per SLO

---

## Alerting Policies

### Condition Types
- **Metric threshold**: alert when metric value exceeds/drops below threshold for a duration
- **Metric absence**: alert when metric stops reporting (service down detection)
- **Log-based metric**: alert on count of specific log patterns
- **Uptime check failure**: alert when uptime check fails from specified locations
- **Prometheus alerting rule**: alert triggered by PromQL expression in GMP

### Notification Channels
| Channel | Use Case |
|---|---|
| Email | Simple alerts; on-call distribution lists |
| PagerDuty | Production incident management |
| OpsGenie | Incident management alternative |
| Slack | Team channels; real-time notification |
| Pub/Sub | Custom webhook integrations; route to any HTTPS service |
| Webhook | Direct HTTPS POST to your endpoint |
| Cloud Mobile App | Google Cloud mobile app push notification |
| SMS | Via Webhook to SMS gateway |

### Alert Policy Best Practices
- Use `duration` to avoid flapping on transient spikes (alert if condition persists for 5 minutes)
- Set appropriate alignment periods (longer = less sensitive to spikes)
- Document runbooks in alert policy documentation fields
- Group related conditions in one policy when they represent the same incident
- Use `combiner=OR` for multi-condition policies that fire independently

---

## Uptime Checks

- HTTP/HTTPS/TCP checks from multiple global locations (configurable subset)
- **HTTP checks**: verify response code, optionally match content in response body
- **HTTPS checks**: verify TLS certificate validity; check expiry
- **TCP checks**: verify port is open and accepting connections
- Check intervals: 1, 5, 10, or 15 minutes
- Alert when: N out of M locations fail (configurable threshold)
- Latency metrics automatically created: `monitoring.googleapis.com/uptime_check/request_latency`

---

## Ops Agent

Unified agent for Compute Engine VMs replacing the legacy Stackdriver Logging and Monitoring agents:

- **Logging**: collects OS and application logs; sends to Cloud Logging
- **Metrics**: collects system metrics (memory, disk, process); sends to Cloud Monitoring
- **Protocol**: uses OpenTelemetry Collector internally
- **Installation**:
  ```bash
  # Debian/Ubuntu
  curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
  sudo bash add-google-cloud-ops-agent-repo.sh --also-install

  # RHEL/CentOS
  curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
  sudo bash add-google-cloud-ops-agent-repo.sh --also-install

  # Windows (PowerShell)
  (New-Object Net.WebClient).DownloadFile("https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.ps1", "$env:UserProfile\add-google-cloud-ops-agent-repo.ps1")
  Invoke-Expression "$env:UserProfile\add-google-cloud-ops-agent-repo.ps1 -AlsoInstall"
  ```
- **Configuration** (`/etc/google-cloud-ops-agent/config.yaml`): define log collection paths, log parsers, metric collection, custom pipelines

---

## Metrics Explorer and Dashboards

- **Metrics Explorer**: ad-hoc metric querying in Cloud Console; supports MQL (Monitoring Query Language) and PromQL
- **MQL**: Google's typed query language for metrics; supports joins, time shifting, rate calculations
- **Dashboards**: drag-drop widget layout; charts (line, bar, heatmap), scorecard, text, alert summary, SLO summary, log panel
- **Dashboard JSON**: dashboards are JSON; import/export via CLI; version control dashboards as code
- **Predefined dashboards**: GCP provides dashboards for GCE, GKE, Cloud SQL, Cloud Run, App Engine, etc.

---

## Pricing

- First 150 MB of metrics data per project per month: free
- Custom metrics, external metrics (AWS): per metric-data-point ingested
- Monitoring API calls: per request
- Alerting: no additional charge for alerting policy evaluation
- SLO monitoring: included with Cloud Monitoring
