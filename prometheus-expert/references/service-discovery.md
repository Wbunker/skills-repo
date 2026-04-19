# Service Discovery

## Overview

Prometheus supports automatic target discovery so you don't have to manually maintain a list of hosts. Discovered targets can be filtered and relabeled before scraping.

## Static Configs (simplest)

```yaml
scrape_configs:
  - job_name: "my-app"
    static_configs:
      - targets: ["host1:8080", "host2:8080"]
        labels:
          env: "production"
          region: "us-east-1"
```

## File-Based Service Discovery

Prometheus watches a file for changes and reloads automatically (no restart needed).

```yaml
scrape_configs:
  - job_name: "file-sd"
    file_sd_configs:
      - files:
          - "/etc/prometheus/targets/*.json"
          - "/etc/prometheus/targets/*.yml"
        refresh_interval: 5m
```

Target file format (JSON):
```json
[
  {
    "targets": ["host1:9100", "host2:9100"],
    "labels": {
      "env": "production",
      "job": "node"
    }
  }
]
```

Target file format (YAML):
```yaml
- targets:
    - host1:9100
    - host2:9100
  labels:
    env: production
    job: node
```

Use file SD when you have an existing CMDB, Ansible inventory, or custom orchestration.

## DNS Service Discovery

```yaml
scrape_configs:
  - job_name: "dns-sd"
    dns_sd_configs:
      - names:
          - "my-service.example.com"        # A record — resolves to IPs
          - "_prometheus._tcp.example.com"   # SRV record — host + port
        type: A      # or SRV
        port: 9100   # required for A records
        refresh_interval: 30s
```

## Consul Service Discovery

```yaml
scrape_configs:
  - job_name: "consul-sd"
    consul_sd_configs:
      - server: "consul:8500"
        token: "your-acl-token"
        services:
          - "my-service"
    relabel_configs:
      - source_labels: [__meta_consul_service]
        target_label: job
      - source_labels: [__meta_consul_node]
        target_label: instance
      - source_labels: [__meta_consul_tags]
        regex: ".*,production,.*"
        action: keep
```

Key `__meta_consul_*` labels: `service`, `node`, `address`, `port`, `tags`, `service_metadata_*`

## EC2 Service Discovery

```yaml
scrape_configs:
  - job_name: "ec2-sd"
    ec2_sd_configs:
      - region: "us-east-1"
        port: 9100
        filters:
          - name: "tag:Environment"
            values: ["production"]
    relabel_configs:
      - source_labels: [__meta_ec2_tag_Name]
        target_label: instance
      - source_labels: [__meta_ec2_instance_type]
        target_label: instance_type
      - source_labels: [__meta_ec2_availability_zone]
        target_label: availability_zone
```

Key `__meta_ec2_*` labels: `instance_id`, `instance_type`, `availability_zone`, `public_ip`, `private_ip`, `tag_*`

## GCE Service Discovery

```yaml
scrape_configs:
  - job_name: "gce-sd"
    gce_sd_configs:
      - project: "my-gcp-project"
        zone: "us-central1-a"
        port: 9100
    relabel_configs:
      - source_labels: [__meta_gce_instance_name]
        target_label: instance
```

## Azure Service Discovery

```yaml
scrape_configs:
  - job_name: "azure-sd"
    azure_sd_configs:
      - environment: AzurePublicCloud
        subscription_id: "..."
        tenant_id: "..."
        client_id: "..."
        client_secret: "..."
        port: 9100
```

## Kubernetes Service Discovery

Kubernetes SD is the most feature-rich. See `references/containers-kubernetes.md` for full Kubernetes coverage.

```yaml
scrape_configs:
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

Roles: `node`, `pod`, `service`, `endpoints`, `endpointslice`, `ingress`

## HTTP Service Discovery

Prometheus fetches a JSON document from an HTTP endpoint and uses it as a target list:

```yaml
scrape_configs:
  - job_name: "http-sd"
    http_sd_configs:
      - url: "http://my-service-registry/api/v1/targets"
        refresh_interval: 30s
```

Response must return the same JSON format as file SD.

## Nomad Service Discovery

```yaml
scrape_configs:
  - job_name: "nomad-sd"
    nomad_sd_configs:
      - server: "http://nomad:4646"
```

## Common Relabeling Patterns for SD

### Keep only instances with a specific tag
```yaml
relabel_configs:
  - source_labels: [__meta_consul_tags]
    regex: ".*metrics.*"
    action: keep
```

### Use metadata as labels
```yaml
relabel_configs:
  - source_labels: [__meta_ec2_tag_Environment]
    target_label: env
  - source_labels: [__meta_ec2_tag_Team]
    target_label: team
```

### Override scrape port from metadata
```yaml
relabel_configs:
  - source_labels: [__address__, __meta_consul_service_port]
    regex: "([^:]+)(?::\\d+)?;(\\d+)"
    replacement: "$1:$2"
    target_label: __address__
```

## Prometheus Operator (Kubernetes)

When using Prometheus Operator, service discovery is configured via CRDs:
- `ServiceMonitor` — scrape Kubernetes Services
- `PodMonitor` — scrape Pods directly
- `ProbeMonitor` — blackbox probing
- `ScrapeConfig` — raw scrape config (new)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 15s
```
