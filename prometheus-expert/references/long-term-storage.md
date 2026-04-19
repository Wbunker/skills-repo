# Long-Term Storage

## Why Prometheus Needs External Storage

Prometheus's local TSDB is optimized for recent data:
- Default retention: 15 days
- Single-node (no built-in replication or HA)
- Not designed for multi-year retention or global queries across many Prometheus instances

For long-term storage, use **remote_write** to send data to an external system.

## Remote Write

```yaml
# prometheus.yml
remote_write:
  - url: "http://thanos-receive:19291/api/v1/receive"
    queue_config:
      max_samples_per_send: 10000
      max_shards: 200
      capacity: 2500
    write_relabel_configs:
      # Drop high-cardinality metrics before sending
      - source_labels: [__name__]
        regex: "go_gc_.*"
        action: drop
    tls_config:
      cert_file: /etc/prometheus/tls/client.crt
      key_file: /etc/prometheus/tls/client.key
    basic_auth:
      username: prometheus
      password_file: /etc/prometheus/secrets/remote-write-password
```

### Queue Config Tuning

| Parameter | Default | Description |
|-----------|---------|-------------|
| `capacity` | 2500 | Number of samples to buffer in memory per shard |
| `max_shards` | 200 | Max parallelism (shards) |
| `min_shards` | 1 | Min shards |
| `max_samples_per_send` | 500 | Batch size |
| `batch_send_deadline` | 5s | Max time before sending a batch |
| `min_backoff` | 30ms | Initial retry backoff |
| `max_backoff` | 5s | Max retry backoff |

Monitor remote write health:
```promql
# Queue capacity utilization
prometheus_remote_storage_queue_highest_sent_timestamp_seconds
prometheus_remote_storage_samples_pending
prometheus_remote_storage_samples_failed_total
prometheus_remote_storage_samples_dropped_total
rate(prometheus_remote_storage_sent_batch_duration_seconds_sum[5m])
  / rate(prometheus_remote_storage_sent_batch_duration_seconds_count[5m])
```

## Remote Read

```yaml
remote_read:
  - url: "http://thanos-query:10902/api/v1/read"
    read_recent: false  # only use remote for data older than local retention
```

## Thanos

The most popular open-source long-term storage solution for Prometheus.

### Components

| Component | Role |
|-----------|------|
| **Sidecar** | Uploads Prometheus blocks to object storage |
| **Store Gateway** | Serves data from object storage |
| **Querier** | Global query layer (deduplicates across Prometheus instances) |
| **Compactor** | Downsamples and compacts object storage data |
| **Ruler** | Evaluates recording/alert rules against long-term data |
| **Receive** | Remote write endpoint (for agents without sidecars) |

### Sidecar Pattern

```yaml
# Prometheus flags
--storage.tsdb.min-block-duration=2h
--storage.tsdb.max-block-duration=2h  # disables compaction (Thanos compacts)

# Thanos sidecar
thanos sidecar \
  --prometheus.url=http://localhost:9090 \
  --tsdb.path=/prometheus \
  --objstore.config-file=/etc/thanos/bucket.yml \
  --grpc-address=0.0.0.0:10901 \
  --http-address=0.0.0.0:10902
```

### Object Store Config

```yaml
# bucket.yml — AWS S3
type: S3
config:
  bucket: "my-thanos-bucket"
  endpoint: "s3.amazonaws.com"
  region: "us-east-1"
  # Uses AWS credentials from env / instance profile

# GCS
type: GCS
config:
  bucket: "my-thanos-bucket"

# Azure Blob
type: AZURE
config:
  storage_account: "mystorageaccount"
  storage_account_key: "..."
  container: "thanos"
```

### Querier (Global View)

```bash
thanos query \
  --http-address=0.0.0.0:10902 \
  --endpoint=prometheus1:10901 \
  --endpoint=prometheus2:10901 \
  --endpoint=thanos-store:10901 \
  --query.replica-label=replica   # deduplicate by this label
```

Grafana datasource → Thanos Querier (same PromQL interface as Prometheus).

### Downsampling

Thanos Compactor creates downsampled resolutions automatically:
- Raw: original scrape interval
- 5m: after 40 hours of data
- 1h: after 10 days of data

This dramatically reduces query time and storage for long time ranges.

## Grafana Mimir (Cortex successor)

Horizontally scalable, multi-tenant Prometheus storage. Good for very large deployments.

```bash
# Docker Compose quickstart
docker run -p 9009:9009 grafana/mimir \
  --ingester.ring.replication-factor=1 \
  --common.storage.backend=filesystem \
  --common.storage.filesystem.dir=/data

# Remote write endpoint
remote_write:
  - url: http://mimir:9009/api/v1/push
    headers:
      X-Scope-OrgID: my-tenant
```

Key Mimir concepts:
- **Distributor**: receives remote writes, shards across ingesters
- **Ingester**: stores recent data in memory, flushes to object store
- **Store Gateway**: serves data from object store
- **Querier**: processes queries
- **Compactor**: background compaction of object store data
- **Ruler**: evaluates recording and alert rules

## VictoriaMetrics

Drop-in Prometheus-compatible long-term storage. High compression, fast queries.

```bash
# Single-node
victoria-metrics \
  -retentionPeriod=12 \   # months
  -storageDataPath=/data

# Remote write endpoint
remote_write:
  - url: http://victoriametrics:8428/api/v1/write

# MetricsQL (PromQL superset) for querying
```

## Choosing a Solution

| Solution | Best for |
|----------|----------|
| **Thanos Sidecar** | Existing Prometheus deployment, object storage already available |
| **Thanos Receive** | Agent mode, no direct object storage access from Prometheus |
| **Grafana Mimir** | Very large scale, multi-tenancy, SaaS-like deployment |
| **VictoriaMetrics** | Simplicity, high compression, single operator |
| **Grafana Cloud** | Managed SaaS, minimal operational overhead |
| **AWS Managed Prometheus** | AWS-native, no self-hosting |

## Prometheus Agent Mode

Prometheus in agent mode only scrapes and remote_writes — it stores no data locally. Ideal for edge or resource-constrained environments.

```bash
prometheus --enable-feature=agent \
  --config.file=prometheus-agent.yml
```

In agent mode: no local storage, no alerting rules, no recording rules — only scraping and remote write.
