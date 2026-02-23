# Monitoring Containers

Reference for monitoring Docker containers and Kubernetes with Datadog.

## Table of Contents
- [Docker Monitoring](#docker-monitoring)
- [Kubernetes Monitoring](#kubernetes-monitoring)
- [Autodiscovery](#autodiscovery)
- [Container Metrics](#container-metrics)
- [Orchestrator Explorer](#orchestrator-explorer)

## Docker Monitoring

### Agent Deployment (Docker)
```bash
docker run -d --name datadog-agent \
  -e DD_API_KEY=<YOUR_API_KEY> \
  -e DD_SITE="datadoghq.com" \
  -e DD_LOGS_ENABLED=true \
  -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
  -e DD_APM_ENABLED=true \
  -e DD_APM_NON_LOCAL_TRAFFIC=true \
  -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC=true \
  -e DD_PROCESS_AGENT_ENABLED=true \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
  -p 8126:8126 \
  -p 8125:8125/udp \
  gcr.io/datadoghq/agent:7
```

### Docker Compose
```yaml
services:
  datadog-agent:
    image: gcr.io/datadoghq/agent:7
    environment:
      - DD_API_KEY=${DD_API_KEY}
      - DD_SITE=datadoghq.com
      - DD_LOGS_ENABLED=true
      - DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true
      - DD_APM_ENABLED=true
      - DD_APM_NON_LOCAL_TRAFFIC=true
      - DD_PROCESS_AGENT_ENABLED=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    ports:
      - "8126:8126"
      - "8125:8125/udp"
```

### Docker Labels for Integration Config
```yaml
services:
  redis:
    image: redis:7
    labels:
      com.datadoghq.ad.check_names: '["redisdb"]'
      com.datadoghq.ad.init_configs: '[{}]'
      com.datadoghq.ad.instances: '[{"host":"%%host%%","port":"6379"}]'
      com.datadoghq.ad.logs: '[{"source":"redis","service":"redis"}]'
```

## Kubernetes Monitoring

### Helm Deployment
```bash
helm repo add datadog https://helm.datadoghq.com

helm install datadog-agent datadog/datadog \
  --set datadog.apiKey=${DD_API_KEY} \
  --set datadog.site="datadoghq.com" \
  --set datadog.logs.enabled=true \
  --set datadog.logs.containerCollectAll=true \
  --set datadog.apm.portEnabled=true \
  --set datadog.processAgent.enabled=true \
  --set datadog.networkMonitoring.enabled=true \
  --set clusterAgent.enabled=true \
  --set clusterAgent.metricsProvider.enabled=true
```

### Helm values.yaml (Comprehensive)
```yaml
datadog:
  apiKey: <YOUR_API_KEY>
  site: datadoghq.com
  clusterName: my-cluster

  tags:
    - env:production
    - team:platform

  logs:
    enabled: true
    containerCollectAll: true

  apm:
    portEnabled: true
    socketEnabled: true

  processAgent:
    enabled: true
    processCollection: true

  networkMonitoring:
    enabled: true

  serviceMonitoring:
    enabled: true

  securityAgent:
    runtime:
      enabled: true

clusterAgent:
  enabled: true
  metricsProvider:
    enabled: true  # HPA based on Datadog metrics
  admissionController:
    enabled: true
    mutateUnlabelled: true  # Auto-inject tracing libs
```

### Datadog Operator
```yaml
apiVersion: datadoghq.com/v2alpha1
kind: DatadogAgent
metadata:
  name: datadog
  namespace: datadog
spec:
  global:
    credentials:
      apiSecret:
        secretName: datadog-secret
        keyName: api-key
    site: datadoghq.com
    clusterName: my-cluster
    tags:
      - env:production

  features:
    apm:
      enabled: true
    logCollection:
      enabled: true
      containerCollectAll: true
    liveProcessCollection:
      enabled: true
    npm:
      enabled: true
    admissionController:
      enabled: true
      mutateUnlabelled: true

  override:
    nodeAgent:
      tolerations:
        - operator: Exists
    clusterAgent:
      replicas: 2
```

## Autodiscovery

Automatically configure integrations for containers/pods based on labels or annotations.

### Kubernetes Annotations
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  template:
    metadata:
      annotations:
        ad.datadoghq.com/redis.check_names: '["redisdb"]'
        ad.datadoghq.com/redis.init_configs: '[{}]'
        ad.datadoghq.com/redis.instances: |
          [{
            "host": "%%host%%",
            "port": "6379",
            "password": "%%env_REDIS_PASSWORD%%"
          }]
        ad.datadoghq.com/redis.logs: '[{"source":"redis","service":"redis"}]'
    spec:
      containers:
        - name: redis
          image: redis:7
```

### Template Variables
| Variable | Description |
|----------|-------------|
| `%%host%%` | Container/pod IP |
| `%%port%%` | Exposed port |
| `%%host_<name>%%` | Specific network host |
| `%%env_<VAR>%%` | Environment variable value |
| `%%kube_namespace%%` | Kubernetes namespace |

### Cluster Agent
The Cluster Agent provides:
- Centralized Autodiscovery dispatch (avoids redundant checks)
- External metrics for HPA
- Cluster-level checks (Kubernetes API server, etcd)
- Admission Controller for auto-injection

## Container Metrics

### Docker Metrics
| Metric | Description |
|--------|-------------|
| `docker.cpu.usage` | CPU usage |
| `docker.cpu.throttled` | CPU throttled time |
| `docker.mem.rss` | Resident memory |
| `docker.mem.limit` | Memory limit |
| `docker.mem.in_use` | Memory utilization % |
| `docker.net.bytes_rcvd` | Network bytes received |
| `docker.net.bytes_sent` | Network bytes sent |
| `docker.io.read_bytes` | Disk read bytes |
| `docker.io.write_bytes` | Disk write bytes |

### Kubernetes Metrics
| Metric | Description |
|--------|-------------|
| `kubernetes.cpu.usage.total` | Pod/container CPU usage |
| `kubernetes.cpu.requests` | CPU requests |
| `kubernetes.cpu.limits` | CPU limits |
| `kubernetes.memory.usage` | Memory usage |
| `kubernetes.memory.requests` | Memory requests |
| `kubernetes.memory.limits` | Memory limits |
| `kubernetes_state.pod.status_phase` | Pod phase (running, pending, etc.) |
| `kubernetes_state.deployment.replicas_available` | Available replicas |
| `kubernetes_state.node.status` | Node readiness |

### Key Tags for Container Metrics
- `kube_namespace`, `kube_deployment`, `kube_daemon_set`, `kube_stateful_set`
- `kube_cluster_name`, `pod_name`, `container_name`, `container_id`
- `image_name`, `image_tag`, `short_image`

## Orchestrator Explorer

Live view of Kubernetes resources in Datadog:
- Pods, Deployments, ReplicaSets, DaemonSets, StatefulSets
- Services, Nodes, Jobs, CronJobs
- Persistent Volumes, ConfigMaps

Enable:
```yaml
datadog:
  orchestratorExplorer:
    enabled: true
```

Use cases:
- Quickly find pods in CrashLoopBackOff
- View resource requests/limits across cluster
- Inspect pod events and conditions
- Correlate with metrics and logs
