# Visualizing and Analyzing Service Mesh Data

Observability is critical for operating service meshes in production. Istio provides rich telemetry data through metrics, logs, and traces, which can be visualized and analyzed using tools like Grafana, Kiali, and various logging platforms.

## Grafana Dashboards

Grafana provides comprehensive visualization of Istio metrics collected by Prometheus. The Istio distribution includes pre-built dashboards for different aspects of mesh operations.

### Built-in Istio Dashboards

**Mesh Dashboard**
Provides a global view of all services in the mesh. Key panels include:
- Global request volume and success rate
- P50, P90, P95, P99 latency percentiles across the mesh
- Service-to-service request distribution
- HTTP/gRPC response codes distribution
- Top services by request volume, error rate, and latency

**Service Dashboard**
Focuses on individual service metrics:
- Client and server workload request rates
- Client and server success rates
- Request duration percentiles for inbound and outbound traffic
- Request sizes and response sizes
- TCP connection metrics for non-HTTP services
- Workload-level breakdown of traffic sources and destinations

**Workload Dashboard**
Drills into specific workload (deployment/pod) metrics:
- Incoming request volume by source workload
- Success rate of incoming requests
- Request duration distribution
- Outgoing request volume by destination
- Memory and CPU usage correlation with traffic patterns

**Performance Dashboard**
Analyzes mesh infrastructure performance:
- Proxy resource utilization (CPU, memory)
- Istio control plane performance (Pilot, Citadel)
- Config push latency and frequency
- XDS cache hit rates
- Webhook processing times

**Control Plane Dashboard**
Monitors Istiod and control plane health:
- Pilot push errors and conflicts
- Proxy connection status
- Configuration validation errors
- Sidecar injection statistics
- Galley validation webhook metrics

### Deploying Grafana with Istio

Install Grafana as part of Istio addons:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml
```

Or using Helm for production deployments:

```yaml
# grafana-values.yaml
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus.istio-system:9090
      access: proxy
      isDefault: true

dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
    - name: 'istio'
      orgId: 1
      folder: 'Istio'
      type: file
      disableDeletion: false
      options:
        path: /var/lib/grafana/dashboards/istio

persistence:
  enabled: true
  size: 10Gi
  storageClassName: standard

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: istio
  hosts:
    - grafana.example.com
```

```bash
helm install grafana grafana/grafana -n istio-system -f grafana-values.yaml
```

### Custom Dashboard Creation

Create dashboards for specific Istio metrics:

```json
{
  "dashboard": {
    "title": "Service Latency SLO",
    "panels": [
      {
        "title": "Request Success Rate (SLI)",
        "targets": [
          {
            "expr": "sum(rate(istio_requests_total{destination_service=\"myservice.default.svc.cluster.local\",response_code!~\"5.*\"}[5m])) / sum(rate(istio_requests_total{destination_service=\"myservice.default.svc.cluster.local\"}[5m]))"
          }
        ],
        "type": "stat",
        "thresholds": [
          {"value": 0.99, "color": "green"},
          {"value": 0.95, "color": "yellow"},
          {"value": 0, "color": "red"}
        ]
      },
      {
        "title": "P99 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket{destination_service=\"myservice.default.svc.cluster.local\"}[5m])) by (le))"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Alerting on Istio Metrics

Configure Grafana alerts for critical conditions:

```yaml
# Alert for high error rate
- name: High Error Rate
  rules:
  - alert: ServiceErrorRateHigh
    expr: |
      (sum(rate(istio_requests_total{response_code=~"5.*"}[5m])) by (destination_service_name)
      /
      sum(rate(istio_requests_total[5m])) by (destination_service_name)) > 0.05
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Service {{ $labels.destination_service_name }} has high error rate"
      description: "Error rate is {{ $value | humanizePercentage }}"

# Alert for high latency
- name: High Latency
  rules:
  - alert: ServiceLatencyHigh
    expr: |
      histogram_quantile(0.99,
        sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (destination_service_name, le)
      ) > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Service {{ $labels.destination_service_name }} has high P99 latency"
      description: "P99 latency is {{ $value }}ms"
```

## Kiali

Kiali is the service mesh observability console for Istio, providing visualization, validation, and configuration management capabilities.

### Service Graph Visualization

Kiali displays real-time service topology with various graph types:

**Versioned App Graph**: Shows applications with version information
**Workload Graph**: Displays deployments and workloads
**Service Graph**: Shows Kubernetes services

Graph features:
- Traffic flow animation with request rates
- Response time indicators
- Error rate highlighting
- Protocol identification (HTTP, gRPC, TCP)
- Traffic percentage distribution
- Security badges (mTLS, authorization policies)

### Configuration Validation

Kiali validates Istio configurations and highlights issues:

**Validation Rules**:
- Gateway selector mismatches
- VirtualService host conflicts
- DestinationRule subset misconfigurations
- Invalid RBAC policies
- Mutual TLS conflicts
- PeerAuthentication policy issues

Example validation errors shown in UI:
- "VirtualService host not found in the mesh"
- "DestinationRule subset not referenced by any VirtualService"
- "Multiple VirtualServices define the same host"
- "Gateway selector doesn't match any gateway deployment"

### Istio Config Wizards

Kiali provides wizards for common Istio configurations:

**Traffic Management Wizards**:
- Request Routing: Create weighted routes and match conditions
- Fault Injection: Add delays and aborts
- Traffic Shifting: A/B testing and canary deployments
- Request Timeouts: Configure timeout policies
- Circuit Breaking: Set connection pool and outlier detection

**Security Wizards**:
- Authorization Policy: Create allow/deny rules
- PeerAuthentication: Enable/disable mTLS
- RequestAuthentication: Configure JWT validation

### Health Indicators

Kiali shows health status for services and workloads:

**Health Criteria**:
- Request success rate (configurable threshold, default >95%)
- Request error rate
- Workload pod status
- Proxy sync status with control plane
- Configuration validation status

**Health States**:
- Healthy (green): All metrics within normal ranges
- Degraded (orange): Some issues detected
- Failure (red): Critical issues present
- Idle (gray): No recent traffic

### Distributed Tracing Integration

Kiali integrates with Jaeger for trace visualization:

```yaml
# Kiali CR with Jaeger integration
apiVersion: kiali.io/v1alpha1
kind: Kiali
metadata:
  name: kiali
spec:
  external_services:
    tracing:
      enabled: true
      in_cluster_url: 'http://jaeger-query.istio-system:16686'
      url: 'https://jaeger.example.com'
      use_grpc: true
      namespace_selector: true
```

Features:
- Click service in graph to view traces
- Span duration correlation with metrics
- Error span highlighting
- Service dependency extraction from traces

### Deploying Kiali

**Quick Installation**:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml
```

**Production Deployment with Operator**:

```yaml
# kiali-operator.yaml
apiVersion: kiali.io/v1alpha1
kind: Kiali
metadata:
  name: kiali
  namespace: istio-system
spec:
  auth:
    strategy: openid
    openid:
      client_id: "kiali"
      issuer_uri: "https://auth.example.com"
  deployment:
    accessible_namespaces:
    - '**'
    ingress_enabled: true
    ingress:
      class_name: istio
      override_yaml:
        metadata:
          annotations:
            cert-manager.io/cluster-issuer: letsencrypt-prod
        spec:
          rules:
          - host: kiali.example.com
            http:
              paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: kiali
                    port:
                      number: 20001
  external_services:
    prometheus:
      url: "http://prometheus.istio-system:9090"
    grafana:
      enabled: true
      in_cluster_url: "http://grafana.istio-system:3000"
      url: "https://grafana.example.com"
    tracing:
      enabled: true
      in_cluster_url: "http://jaeger-query.istio-system:16686"
```

```bash
kubectl apply -f kiali-operator.yaml
```

### Authentication Methods

**Anonymous**: No authentication (development only)

```yaml
spec:
  auth:
    strategy: anonymous
```

**Token**: Kubernetes ServiceAccount token

```yaml
spec:
  auth:
    strategy: token
```

**OpenID Connect**: Enterprise SSO integration

```yaml
spec:
  auth:
    strategy: openid
    openid:
      client_id: "kiali-client"
      client_secret: "secret"
      issuer_uri: "https://keycloak.example.com/auth/realms/master"
      scopes: ["openid", "profile", "email"]
      username_claim: "preferred_username"
```

### Key Views

**Graph View**:
- Namespace selection and filtering
- Display options (traffic animation, security badges, service nodes)
- Find/Hide features for complex graphs
- Time range selection
- Legend for icons and colors

**Workloads View**:
- Pod health and status
- Resource utilization
- Associated services
- Istio configuration applied
- Logs access

**Services View**:
- Service health score
- Request metrics (rate, duration, error rate)
- Inbound/outbound traffic breakdown
- Associated workloads
- VirtualServices and DestinationRules

**Istio Config View**:
- All Istio resources in namespace
- Validation status with error details
- YAML viewer and editor
- Configuration wizards
- Cross-reference checking

## Logging Architecture

Istio generates detailed access logs from Envoy sidecars, providing request-level observability.

### Access Log Collection

Enable access logging in Istio mesh configuration:

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    accessLogFile: /dev/stdout
    accessLogEncoding: JSON
    accessLogFormat: |
      {
        "start_time": "%START_TIME%",
        "method": "%REQ(:METHOD)%",
        "path": "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%",
        "protocol": "%PROTOCOL%",
        "response_code": "%RESPONSE_CODE%",
        "response_flags": "%RESPONSE_FLAGS%",
        "bytes_received": "%BYTES_RECEIVED%",
        "bytes_sent": "%BYTES_SENT%",
        "duration": "%DURATION%",
        "upstream_service_time": "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%",
        "x_forwarded_for": "%REQ(X-FORWARDED-FOR)%",
        "user_agent": "%REQ(USER-AGENT)%",
        "request_id": "%REQ(X-REQUEST-ID)%",
        "authority": "%REQ(:AUTHORITY)%",
        "upstream_host": "%UPSTREAM_HOST%",
        "upstream_cluster": "%UPSTREAM_CLUSTER%",
        "upstream_local_address": "%UPSTREAM_LOCAL_ADDRESS%",
        "downstream_local_address": "%DOWNSTREAM_LOCAL_ADDRESS%",
        "downstream_remote_address": "%DOWNSTREAM_REMOTE_ADDRESS%",
        "route_name": "%ROUTE_NAME%"
      }
```

### Structured Logging

JSON format enables easy parsing and querying:

```json
{
  "start_time": "2024-01-15T10:30:45.123Z",
  "method": "GET",
  "path": "/api/users/123",
  "protocol": "HTTP/1.1",
  "response_code": 200,
  "response_flags": "-",
  "bytes_received": 0,
  "bytes_sent": 1234,
  "duration": 45,
  "upstream_service_time": "42",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "authority": "api.example.com",
  "upstream_host": "10.244.0.15:8080",
  "upstream_cluster": "outbound|8080||userservice.default.svc.cluster.local",
  "route_name": "default"
}
```

### Envoy Access Log Format Customization

Customize log fields per workload using Telemetry API:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-access-logs
  namespace: default
spec:
  accessLogging:
  - providers:
    - name: envoy
    filter:
      expression: response.code >= 400
```

### Key Log Fields

**Upstream Host**: The actual backend pod that handled the request
- Format: `IP:PORT`
- Useful for identifying which pod instance served the request
- Critical for debugging pod-specific issues

**Response Code**: HTTP status code returned
- 2xx: Success
- 3xx: Redirection
- 4xx: Client errors
- 5xx: Server errors

**Response Flags**: Envoy-specific flags indicating request processing details (see Response Flags section)

**Duration**: Total request duration in milliseconds
- Includes Envoy overhead, network time, and upstream processing

**Upstream Service Time**: Time spent in the upstream service
- Compare with duration to identify Envoy/network overhead

**Route Name**: The Istio route matched for this request
- Correlates with VirtualService route definitions
- Helps debug routing issues

## Log Aggregation

Centralized log aggregation enables searching, filtering, and analyzing access logs across the mesh.

### EFK Stack Integration

**Elasticsearch, Fluentd, Kibana** is a common stack for Kubernetes logging:

```yaml
# Fluentd DaemonSet for collecting Istio logs
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: logging
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*_istio-proxy-*.log
      pos_file /var/log/istio-proxy.log.pos
      tag istio.*
      <parse>
        @type json
        time_key time
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>

    <filter istio.**>
      @type parser
      key_name log
      <parse>
        @type json
      </parse>
    </filter>

    <filter istio.**>
      @type record_transformer
      <record>
        cluster_name "production"
        mesh_id "mesh1"
      </record>
    </filter>

    <match istio.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      logstash_format true
      logstash_prefix istio
      <buffer>
        @type file
        path /var/log/fluentd-buffers/istio.buffer
        flush_mode interval
        retry_type exponential_backoff
        flush_interval 5s
      </buffer>
    </match>
```

**Kibana Index Pattern**:
Create index pattern `istio-*` to query access logs with fields:
- `response_code`
- `response_flags`
- `upstream_cluster`
- `duration`
- `method`
- `path`

### Loki/Promtail/Grafana Integration

**Promtail Configuration** for Istio logs:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: logging
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0

    positions:
      filename: /tmp/positions.yaml

    clients:
      - url: http://loki.logging:3100/loki/api/v1/push

    scrape_configs:
    - job_name: istio-proxy
      kubernetes_sd_configs:
      - role: pod

      pipeline_stages:
      - docker: {}
      - json:
          expressions:
            response_code: response_code
            response_flags: response_flags
            duration: duration
            method: method
            path: path
            upstream_cluster: upstream_cluster
      - labels:
          response_code:
          response_flags:
          method:
          upstream_cluster:

      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_container_name]
        action: keep
        regex: istio-proxy
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

**Loki Query Examples**:

```logql
# All 5xx errors in last hour
{container="istio-proxy"} | json | response_code >= 500

# Slow requests (>1s) to specific service
{container="istio-proxy"} | json | upstream_cluster=~".*userservice.*" | duration > 1000

# Requests with response flags (errors)
{container="istio-proxy"} | json | response_flags != "-"

# Rate of errors by service
sum(rate({container="istio-proxy"} | json | response_code >= 500 [5m])) by (upstream_cluster)
```

### Log Pipeline Architecture

**Collection**: Promtail/Fluentd DaemonSets on each node
**Aggregation**: Loki/Elasticsearch for storage and indexing
**Visualization**: Grafana/Kibana for querying and dashboards
**Alerting**: Alert rules on log patterns

Best practices:
- Use structured JSON logging for easy parsing
- Index critical fields (response_code, upstream_cluster, response_flags)
- Set retention policies based on volume (7-30 days typical)
- Use sampling for high-traffic services if needed
- Configure log levels appropriately (INFO for production)

### Parsing Envoy Access Logs

Extract meaningful information from access logs:

```python
# Example Python parser
import json

def parse_istio_access_log(log_line):
    """Parse Istio access log and extract key metrics"""
    log = json.loads(log_line)

    return {
        'timestamp': log['start_time'],
        'service': extract_service_from_cluster(log['upstream_cluster']),
        'method': log['method'],
        'path': log['path'],
        'status': int(log['response_code']),
        'duration_ms': int(log['duration']),
        'is_error': int(log['response_code']) >= 400,
        'has_failure': log['response_flags'] != '-',
        'failure_type': parse_response_flags(log['response_flags'])
    }

def extract_service_from_cluster(cluster):
    """Extract service name from Envoy cluster format"""
    # outbound|8080||userservice.default.svc.cluster.local
    if '||' in cluster:
        return cluster.split('||')[1]
    return cluster
```

## Response Flags

Envoy response flags indicate why a request failed or was handled unusually. Critical for debugging.

### Common Response Flags

**UH (Upstream Host Unhealthy)**
- No healthy upstream host to handle request
- Causes: All pods failing health checks, circuit breaker open
- Debug: Check pod health, review outlier detection config

**UF (Upstream Connection Failure)**
- Failed to connect to upstream
- Causes: Network issues, pod not ready, wrong port
- Debug: Check network policies, pod status, service endpoints

**UO (Upstream Overflow)**
- Circuit breaker triggered (too many connections/requests)
- Causes: Connection pool limits exceeded
- Debug: Review DestinationRule connection pool settings

**NR (No Route)**
- No route configured for the request
- Causes: Missing VirtualService, wrong host header
- Debug: Check VirtualService hosts and match conditions

**URX (Upstream Retry Limit Exceeded)**
- Request retried maximum times and still failed
- Causes: Upstream consistently failing, retry policy too aggressive
- Debug: Check upstream service health, review retry policy

**NC (No Cluster)**
- Cluster not found for request
- Causes: DestinationRule references non-existent service
- Debug: Verify service exists, check DestinationRule configuration

**DT (Downstream Connection Termination)**
- Client closed connection before response
- Causes: Client timeout, network interruption
- Debug: Check client timeout settings, network stability

**DC (Downstream Connection Timeout)**
- Downstream connection idle timeout
- Causes: Client not sending data, keep-alive timeout
- Debug: Review idle timeout settings

**LH (Local Service Unhealthy)**
- Local service health check failed
- Causes: Application health check endpoint failing
- Debug: Check application health endpoint

**UT (Upstream Request Timeout)**
- Upstream service didn't respond within timeout
- Causes: Slow upstream, timeout too short
- Debug: Review timeout configuration, upstream performance

**LR (Local Reset)**
- Local Envoy reset the request
- Causes: Invalid request, configuration issue
- Debug: Check Envoy logs for details

**RL (Rate Limited)**
- Request rate limited
- Causes: Rate limit policy triggered
- Debug: Review EnvoyFilter rate limit configuration

**UAEX (Unauthorized External Service)**
- Request to external service not allowed
- Causes: ServiceEntry missing, egress not configured
- Debug: Check ServiceEntry configuration, mesh egress mode

**RLSE (Rate Limit Service Error)**
- Rate limit service unavailable
- Causes: Rate limit server down
- Debug: Check rate limit service status

### Debugging with Response Flags

Query logs for specific failure patterns:

```bash
# Find all UH errors (unhealthy upstream)
kubectl logs -l app=myapp -c istio-proxy | grep '"response_flags":"UH"'

# Count errors by response flag type
kubectl logs -l app=myapp -c istio-proxy | \
  jq -r '.response_flags' | \
  grep -v '^-$' | \
  sort | uniq -c | sort -rn
```

Create alerts for critical flags:

```yaml
- alert: UpstreamConnectionFailures
  expr: |
    sum(rate(istio_requests_total{response_flags=~".*UF.*"}[5m])) by (destination_service_name) > 0
  for: 2m
  annotations:
    summary: "Service {{ $labels.destination_service_name }} experiencing upstream connection failures"
```

## Alerting Patterns

Effective alerting on Istio metrics prevents incidents and enables quick response.

### Prometheus Alerting Rules for Istio

**High Error Rate Alert**:

```yaml
groups:
- name: istio_service_health
  interval: 30s
  rules:
  - alert: HighServiceErrorRate
    expr: |
      (
        sum(rate(istio_requests_total{reporter="destination",response_code=~"5.*"}[5m])) by (destination_service_namespace, destination_service_name)
        /
        sum(rate(istio_requests_total{reporter="destination"}[5m])) by (destination_service_namespace, destination_service_name)
      ) > 0.05
    for: 2m
    labels:
      severity: critical
      team: platform
    annotations:
      summary: "High error rate for {{ $labels.destination_service_name }}"
      description: "Service {{ $labels.destination_service_name }} in namespace {{ $labels.destination_service_namespace }} has error rate of {{ $value | humanizePercentage }}"
      runbook_url: "https://wiki.example.com/runbooks/high-error-rate"
```

**High Latency Alert**:

```yaml
  - alert: HighServiceLatency
    expr: |
      histogram_quantile(0.99,
        sum(rate(istio_request_duration_milliseconds_bucket{reporter="destination"}[5m])) by (destination_service_namespace, destination_service_name, le)
      ) > 1000
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "High P99 latency for {{ $labels.destination_service_name }}"
      description: "Service {{ $labels.destination_service_name }} P99 latency is {{ $value }}ms"
```

**Circuit Breaker Trips**:

```yaml
  - alert: CircuitBreakerTripping
    expr: |
      sum(rate(istio_requests_total{response_flags=~".*UO.*"}[5m])) by (destination_service_name) > 0
    for: 1m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "Circuit breaker tripping for {{ $labels.destination_service_name }}"
      description: "Service {{ $labels.destination_service_name }} circuit breaker is triggering due to overflow"
```

**mTLS Failures**:

```yaml
  - alert: MutualTLSFailures
    expr: |
      sum(rate(istio_requests_total{response_code="000"}[5m])) by (source_workload, destination_service_name) > 0
    for: 2m
    labels:
      severity: critical
      team: security
    annotations:
      summary: "mTLS failures between {{ $labels.source_workload }} and {{ $labels.destination_service_name }}"
      description: "Mutual TLS handshake failures detected"
```

**Low Traffic Anomaly**:

```yaml
  - alert: ServiceTrafficDropped
    expr: |
      (
        sum(rate(istio_requests_total[5m])) by (destination_service_name)
        <
        sum(rate(istio_requests_total[5m] offset 1h)) by (destination_service_name) * 0.5
      )
      and
      sum(rate(istio_requests_total[5m] offset 1h)) by (destination_service_name) > 1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Traffic drop detected for {{ $labels.destination_service_name }}"
      description: "Traffic is 50% lower than 1 hour ago"
```

### Alert Routing

Configure Alertmanager for routing:

```yaml
route:
  receiver: 'default'
  group_by: ['alertname', 'destination_service_name']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  routes:
  - match:
      severity: critical
      team: platform
    receiver: 'pagerduty-platform'
    continue: true
  - match:
      severity: critical
    receiver: 'slack-critical'
  - match:
      severity: warning
    receiver: 'slack-warnings'

receivers:
- name: 'default'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/XXX'
    channel: '#istio-alerts'
```

### PagerDuty/Slack Integration

**PagerDuty Integration**:

```yaml
receivers:
- name: 'pagerduty-platform'
  pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_KEY'
    description: '{{ .GroupLabels.alertname }}: {{ .GroupLabels.destination_service_name }}'
    details:
      firing: '{{ .Alerts.Firing | len }}'
      resolved: '{{ .Alerts.Resolved | len }}'
      service: '{{ .GroupLabels.destination_service_name }}'
      namespace: '{{ .GroupLabels.destination_service_namespace }}'
```

**Slack Integration with Rich Formatting**:

```yaml
receivers:
- name: 'slack-critical'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/XXX'
    channel: '#istio-critical'
    title: 'Istio Alert: {{ .GroupLabels.alertname }}'
    text: |
      {{ range .Alerts }}
      *Service:* {{ .Labels.destination_service_name }}
      *Namespace:* {{ .Labels.destination_service_namespace }}
      *Severity:* {{ .Labels.severity }}
      *Description:* {{ .Annotations.description }}
      *Runbook:* {{ .Annotations.runbook_url }}
      {{ end }}
    color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
```

## Debugging with Observability

Correlating metrics, logs, and traces enables efficient troubleshooting in production.

### Correlating Metrics, Logs, and Traces

**Unified Debugging Workflow**:

1. **Metrics**: Identify anomalies (high latency, error rate spike)
2. **Logs**: Find specific failing requests using filters
3. **Traces**: Analyze request path and identify bottleneck

**Example: High Latency Investigation**:

```bash
# Step 1: Confirm in Grafana (metrics)
# Query: histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket{destination_service="userservice"}[5m])) by (le))
# Result: P99 latency jumped from 100ms to 2000ms

# Step 2: Find slow requests in logs
kubectl logs -l app=userservice -c istio-proxy --tail=1000 | \
  jq 'select(.duration > 1000) | {path, duration, upstream_service_time, response_flags}'

# Step 3: Get trace ID from slow request
# Find trace_id field in log entry

# Step 4: View trace in Jaeger
# Open trace in Jaeger UI to see span breakdown
```

### Troubleshooting Latency Issues

**Identify Latency Source**:

Compare access log fields:
- `duration`: Total request time (including Envoy)
- `upstream_service_time`: Time in application only

```bash
# If duration >> upstream_service_time: Network/Envoy overhead
# If duration ≈ upstream_service_time: Application slow

# Find requests with high Envoy overhead
kubectl logs -l app=myapp -c istio-proxy | \
  jq 'select(.duration - .upstream_service_time > 100) | {duration, upstream_service_time, diff: (.duration - .upstream_service_time)}'
```

**Check for Retries**:

```promql
# Retry rate
sum(rate(istio_requests_total{response_flags=~".*URX.*"}[5m])) by (destination_service_name)
```

### Identifying Failing Services

**Service Dependency Errors**:

```bash
# Find which upstream services are failing
kubectl logs -l app=frontend -c istio-proxy | \
  jq 'select(.response_code >= 500) | .upstream_cluster' | \
  sort | uniq -c | sort -rn
```

**Circuit Breaker Status**:

```promql
# Services with circuit breaker trips
sum(rate(istio_requests_total{response_flags=~".*UO.*"}[5m])) by (destination_service_name)
```

**Unhealthy Upstreams**:

```bash
# Find UH (unhealthy upstream) errors
kubectl logs -l app=api-gateway -c istio-proxy | \
  grep '"response_flags":"UH"' | \
  jq '{time: .start_time, service: .upstream_cluster, path: .path}'
```

### Common Debugging Workflows

**Workflow 1: Service Returns 503**

1. Check Grafana: Confirm error rate spike
2. Check logs for response_flags:
   - `UH`: Check pod health, outlier detection
   - `UF`: Check network connectivity, endpoints
   - `UO`: Check circuit breaker settings
   - `NR`: Check VirtualService configuration
3. Check Kiali: Validate configuration, view service graph
4. Check control plane: `istioctl proxy-status` for sync issues

**Workflow 2: Intermittent Timeouts**

1. Check Grafana: Identify P99 latency spikes
2. Query logs for timeout errors (`UT` response flag)
3. Review trace in Jaeger: Find slow span
4. Check DestinationRule timeout configuration
5. Compare with application actual processing time

**Workflow 3: mTLS Connection Failures**

1. Check for response_code="000" in metrics
2. Check logs for connection reset errors
3. Verify PeerAuthentication mode (STRICT vs PERMISSIVE)
4. Check certificate validity: `istioctl proxy-config secret`
5. Review Kiali security badges

**Workflow 4: Traffic Not Reaching Service**

1. Check Kiali graph: Verify traffic flow
2. Check VirtualService: Verify host and match rules
3. Check Gateway: Verify selector and hosts
4. Check logs for `NR` (no route) response flag
5. Validate with: `istioctl analyze`

These observability tools and debugging workflows enable teams to maintain reliable service mesh operations, quickly identify issues, and understand system behavior in production environments.
