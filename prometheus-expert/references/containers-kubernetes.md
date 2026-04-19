# Containers and Kubernetes

## Monitoring Kubernetes — Component Overview

| Component | What it exposes | Default port |
|-----------|----------------|--------------|
| **kube-apiserver** | API server metrics | 6443 |
| **kube-scheduler** | Scheduling decisions | 10259 |
| **kube-controller-manager** | Controller loop metrics | 10257 |
| **kubelet** | Node agent + container stats | 10250 |
| **cAdvisor** | Container CPU/mem/net/disk | Built into kubelet at `/metrics/cadvisor` |
| **kube-state-metrics** | Kubernetes object state | 8080 |
| **node-exporter** | OS/hardware metrics | 9100 |

## kube-state-metrics

Exposes the *desired state* of Kubernetes objects (Deployments, Pods, etc.) as metrics. This is different from cAdvisor which exposes *resource usage*.

```promql
# Number of desired vs available replicas
kube_deployment_spec_replicas{deployment="my-app"}
kube_deployment_status_replicas_available{deployment="my-app"}

# Are any pods not running?
kube_pod_status_phase{phase!="Running", phase!="Succeeded"}

# Pod restarts
kube_pod_container_status_restarts_total

# Job success/failure
kube_job_status_succeeded
kube_job_status_failed

# Node conditions
kube_node_status_condition{condition="Ready", status="true"}

# PVC usage
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100
```

## cAdvisor (container resources)

Embedded in the kubelet; expose via `/metrics/cadvisor`.

```promql
# CPU usage per container
rate(container_cpu_usage_seconds_total{container!="POD", container!=""}[5m])

# Memory usage per container
container_memory_working_set_bytes{container!="POD", container!=""}

# Memory limit utilization %
container_memory_working_set_bytes / container_spec_memory_limit_bytes * 100

# Network I/O per pod
rate(container_network_receive_bytes_total{pod!=""}[5m])
rate(container_network_transmit_bytes_total{pod!=""}[5m])

# Filesystem usage
container_fs_usage_bytes / container_fs_limit_bytes * 100
```

## Kubernetes Service Discovery Config

### Scrape all pods with annotation

```yaml
scrape_configs:
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with annotation prometheus.io/scrape: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"

      # Use annotation for metrics path
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)

      # Use annotation for port
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: "([^:]+)(?::\\d+)?;(\\d+)"
        replacement: "$1:$2"
        target_label: __address__

      # Add namespace and pod name as labels
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

### Scrape kubelet / cAdvisor

```yaml
scrape_configs:
  - job_name: "kubelet"
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      insecure_skip_verify: true
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        target_label: __metrics_path__
        replacement: /api/v1/nodes/$1/proxy/metrics/cadvisor
```

### Scrape kube-apiserver via endpoints

```yaml
scrape_configs:
  - job_name: "kubernetes-apiservers"
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
```

## Prometheus Operator / kube-prometheus-stack

The recommended way to run Prometheus on Kubernetes. Installs:
- Prometheus Operator (manages Prometheus via CRDs)
- Prometheus instances
- Alertmanager
- kube-state-metrics
- Node Exporter
- Grafana
- Pre-built dashboards and alert rules

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

### ServiceMonitor CRD

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: monitoring
  labels:
    release: kube-prometheus-stack   # must match operator's serviceMonitorSelector
spec:
  namespaceSelector:
    matchNames:
      - default
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
```

### PodMonitor CRD

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: my-batch-jobs
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: batch
  podMetricsEndpoints:
    - port: metrics
```

### PrometheusRule CRD

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-alerts
  labels:
    release: kube-prometheus-stack
spec:
  groups:
    - name: my-app
      rules:
        - alert: HighErrorRate
          expr: |
            rate(http_requests_total{status=~"5.."}[5m]) /
            rate(http_requests_total[5m]) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate on {{ $labels.job }}"
```

## Resource Requests/Limits — Monitoring Approach

```promql
# Containers over memory limit
container_memory_working_set_bytes
  / on(pod, container) group_left
  kube_pod_container_resource_limits{resource="memory"}
> 0.9

# CPU throttling
rate(container_cpu_throttled_seconds_total[5m])
  / rate(container_cpu_usage_seconds_total[5m])
```

## Useful Labels in Kubernetes Monitoring

| Label | Source | Description |
|-------|--------|-------------|
| `namespace` | relabel | Kubernetes namespace |
| `pod` | relabel | Pod name |
| `container` | cAdvisor | Container name |
| `node` | kubelet SD | Node hostname |
| `job` | config | scrape job name |
| `deployment` | kube-state-metrics | Deployment name |
