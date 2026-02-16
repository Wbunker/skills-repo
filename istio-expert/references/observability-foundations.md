# Establishing Observability Foundations in Istio

Observability is a fundamental capability of Istio, providing deep insights into service behavior without requiring application code changes. Istio's sidecar proxies (Envoy) automatically capture and expose telemetry data for all service-to-service communication.

## Three Pillars of Observability

Istio provides comprehensive observability through three complementary pillars:

### Metrics

Metrics are numerical measurements captured over time intervals. Istio automatically generates a rich set of service-level metrics for all HTTP, HTTP/2, gRPC, and TCP traffic flowing through the mesh. These metrics are exposed in Prometheus format and include:

- Request rates and volumes
- Request durations and latencies
- Request and response sizes
- Connection statistics
- Error rates and status codes

Envoy proxies generate these metrics without any application involvement, making them immediately available upon adding workloads to the mesh.

### Logs

Logs provide detailed records of individual events and requests. Istio generates access logs for each request passing through Envoy proxies. Access logs can be:

- Sent to standard output/error for collection by log aggregators
- Forwarded to OpenTelemetry collectors
- Configured with custom formats and filters
- Enhanced with mesh-specific context (source/destination workload, namespace, etc.)

Access logging is disabled by default to reduce overhead but can be enabled globally or per-workload.

### Distributed Traces

Distributed traces track request flows across multiple services, providing end-to-end visibility into request paths and timing. Istio enables distributed tracing by:

- Generating trace spans for each proxy hop
- Propagating trace context between services
- Integrating with tracing backends (Jaeger, Zipkin, OpenTelemetry)
- Correlating spans across service boundaries

Applications must forward trace headers to maintain trace context continuity across services.

## Standard Istio Metrics

Istio generates a comprehensive set of metrics categorized by protocol:

### HTTP/gRPC Metrics

**istio_requests_total** (Counter)
Total number of requests handled by the proxy. This is the primary metric for calculating request rates and success/error ratios.

Dimensions:
- `reporter`: "source" or "destination" (which proxy reported the metric)
- `source_workload`, `source_workload_namespace`: Origin workload identity
- `destination_workload`, `destination_workload_namespace`: Target workload identity
- `destination_service`, `destination_service_name`, `destination_service_namespace`: Target service
- `request_protocol`: "http", "grpc"
- `response_code`: HTTP status code
- `response_flags`: Envoy response flags (circuit breaker, timeout, etc.)
- `connection_security_policy`: "mutual_tls", "none", "unknown"

**istio_request_duration_milliseconds** (Distribution/Histogram)
Request duration measured at different points in the proxy pipeline.

Same dimensions as istio_requests_total, providing latency percentiles (p50, p90, p95, p99).

**istio_request_bytes** (Distribution/Histogram)
Request body size in bytes.

**istio_response_bytes** (Distribution/Histogram)
Response body size in bytes.

### TCP Metrics

**istio_tcp_sent_bytes_total** (Counter)
Total bytes sent over TCP connections.

**istio_tcp_received_bytes_total** (Counter)
Total bytes received over TCP connections.

**istio_tcp_connections_opened_total** (Counter)
Total TCP connections opened.

**istio_tcp_connections_closed_total** (Counter)
Total TCP connections closed.

TCP metrics include similar dimensional data (source/destination workload, service, security policy) but exclude HTTP-specific attributes like response codes.

### Metric Labels and Cardinality

Istio metrics are heavily dimensioned to enable detailed analysis. However, high-cardinality labels (many unique values) can impact Prometheus performance. Be cautious when adding custom labels with values like:

- User IDs or session IDs
- Arbitrary request paths
- Dynamic version strings

The default Istio metrics are designed for reasonable cardinality in production environments.

## Telemetry API

Istio's Telemetry API provides fine-grained control over observability features through the Telemetry CRD. This API replaces legacy EnvoyFilter-based configurations with a declarative, version-stable interface.

### Telemetry Resource Scope

Telemetry resources can be applied at different scopes:

- **Root namespace** (istio-system): Mesh-wide defaults
- **Namespace**: Applies to all workloads in the namespace
- **Workload**: Selector-based targeting of specific workloads

More specific configurations override broader ones.

### Disabling Metrics

Disable all Istio standard metrics mesh-wide:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: disable-metrics
  namespace: istio-system
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: ALL_METRICS
      disabled: true
```

Disable specific metrics:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: disable-request-size
  namespace: my-namespace
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_SIZE
      disabled: true
```

### Custom Metric Tags

Add custom dimensions to standard metrics:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-tags
  namespace: istio-system
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: ALL_METRICS
      tagOverrides:
        request_path:
          value: "request.path"
        api_version:
          value: "request.headers['x-api-version']"
```

Tag values are CEL expressions evaluated against request attributes.

### Tag Removal

Remove high-cardinality or unnecessary tags:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: remove-response-flags
  namespace: istio-system
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: ALL_METRICS
      tagOverrides:
        response_flags:
          operation: REMOVE
```

### Workload-Specific Metrics Configuration

Target specific workloads using selector:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: frontend-metrics
  namespace: production
spec:
  selector:
    matchLabels:
      app: frontend
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_DURATION
      tagOverrides:
        user_agent:
          value: "request.headers['user-agent']"
```

## Access Logging

Access logs provide detailed request-level information for debugging and audit purposes.

### Enabling Access Logs

Enable access logs mesh-wide with custom format:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-access-logs
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: envoy
```

This uses the default Envoy text format. The access logs are written to the proxy's stdout.

### Custom Access Log Format

Define custom JSON format for structured logging:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: json-access-logs
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: envoy
    filter:
      expression: "response.code >= 400"
    formatters:
    - labels:
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        protocol: "%PROTOCOL%"
        response_code: "%RESPONSE_CODE%"
        response_flags: "%RESPONSE_FLAGS%"
        bytes_received: "%BYTES_RECEIVED%"
        bytes_sent: "%BYTES_SENT%"
        duration: "%DURATION%"
        upstream_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
        upstream_cluster: "%UPSTREAM_CLUSTER%"
        source_workload: "%DOWNSTREAM_PEER_WORKLOAD%"
        destination_workload: "%UPSTREAM_PEER_WORKLOAD%"
```

### Access Log Filtering

Log only errors:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: error-logs-only
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: envoy
    filter:
      expression: "response.code >= 500"
```

Filter expression uses CEL (Common Expression Language) with access to request and response attributes.

### OpenTelemetry Access Logs

Send access logs to OpenTelemetry collector:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: otel-access-logs
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: otel
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio
  namespace: istio-system
data:
  mesh: |
    extensionProviders:
    - name: otel
      envoyOtelAls:
        service: opentelemetry-collector.observability.svc.cluster.local
        port: 4317
```

### Per-Workload Access Logging

Enable access logs only for specific workloads:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: payment-access-logs
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  accessLogging:
  - providers:
    - name: envoy
```

## Distributed Tracing

Distributed tracing enables tracking requests across multiple services, providing visibility into call graphs, latencies, and failure points.

### How Istio Enables Tracing

Istio proxies automatically:
1. Generate span data for inbound and outbound requests
2. Add trace context headers to outgoing requests
3. Send span data to configured tracing backends
4. Correlate spans using trace IDs

### Application Responsibilities

Applications must propagate trace context headers between services. The following headers must be forwarded:

**B3 Headers (widely supported):**
- `x-b3-traceid`: Unique trace identifier
- `x-b3-spanid`: Current span identifier
- `x-b3-parentspanid`: Parent span identifier
- `x-b3-sampled`: Sampling decision (0 or 1)
- `x-b3-flags`: Debug flag

**W3C Trace Context (recommended):**
- `traceparent`: Combined trace/span/flags header
- `tracestate`: Vendor-specific trace metadata

**Additional headers:**
- `x-request-id`: Request correlation ID

Example Python code for header propagation:

```python
import requests

TRACE_HEADERS = [
    'x-request-id',
    'x-b3-traceid',
    'x-b3-spanid',
    'x-b3-parentspanid',
    'x-b3-sampled',
    'x-b3-flags',
    'traceparent',
    'tracestate'
]

def forward_request(incoming_headers, url):
    headers = {
        h: incoming_headers.get(h)
        for h in TRACE_HEADERS
        if incoming_headers.get(h)
    }
    return requests.get(url, headers=headers)
```

### Configuring Tracing Backend

Enable tracing with Jaeger backend:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-tracing
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
    randomSamplingPercentage: 1.0
    customTags:
      environment:
        literal:
          value: "production"
      cluster:
        environment:
          name: CLUSTER_NAME
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio
  namespace: istio-system
data:
  mesh: |
    extensionProviders:
    - name: jaeger
      zipkin:
        service: jaeger-collector.observability.svc.cluster.local
        port: 9411
```

### Sampling Rates

Control trace sampling to balance observability with overhead:

**1% sampling (production default):**
```yaml
spec:
  tracing:
  - randomSamplingPercentage: 1.0
```

**100% sampling (development/debugging):**
```yaml
spec:
  tracing:
  - randomSamplingPercentage: 100.0
```

**Per-workload sampling:**
```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: high-value-tracing
  namespace: production
spec:
  selector:
    matchLabels:
      tier: critical
  tracing:
  - randomSamplingPercentage: 10.0
```

### Custom Span Tags

Enrich traces with custom metadata:

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-trace-tags
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
    customTags:
      user_id:
        header:
          name: x-user-id
      tenant:
        header:
          name: x-tenant-id
      request_size:
        literal:
          value: "request.size"
```

### OpenTelemetry Tracing

Use OpenTelemetry collector for vendor-neutral tracing:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio
  namespace: istio-system
data:
  mesh: |
    extensionProviders:
    - name: otel-tracing
      opentelemetry:
        service: opentelemetry-collector.observability.svc.cluster.local
        port: 4317
---
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: otel-tracing
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: otel-tracing
    randomSamplingPercentage: 5.0
```

## Prometheus Integration

Istio metrics are exposed in Prometheus format on each Envoy proxy at port 15090 (`/stats/prometheus`).

### ServiceMonitor Configuration

Configure Prometheus Operator to scrape Istio metrics:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: istio-mesh-metrics
  namespace: istio-system
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  endpoints:
  - port: http-envoy-prom
    interval: 30s
    path: /stats/prometheus
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_name]
      targetLabel: pod_name
    - sourceLabels: [__meta_kubernetes_namespace]
      targetLabel: namespace
```

### Scrape All Mesh Workloads

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: istio-proxies
  namespace: istio-system
spec:
  selector:
    matchExpressions:
    - key: istio-prometheus-ignore
      operator: DoesNotExist
  podMetricsEndpoints:
  - port: http-envoy-prom
    interval: 30s
    path: /stats/prometheus
    relabelings:
    - action: keep
      sourceLabels: [__meta_kubernetes_pod_container_name]
      regex: istio-proxy
    - sourceLabels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:15020
      targetLabel: __address__
```

### Recording Rules

Create aggregated metrics for dashboard performance:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: istio-recording-rules
  namespace: istio-system
spec:
  groups:
  - name: istio.recording_rules
    interval: 30s
    rules:
    - record: istio:requests:rate5m
      expr: |
        sum(rate(istio_requests_total{reporter="destination"}[5m]))
        by (destination_service_name, destination_service_namespace, response_code)

    - record: istio:request_duration:p50
      expr: |
        histogram_quantile(0.50,
          sum(rate(istio_request_duration_milliseconds_bucket{reporter="destination"}[5m]))
          by (destination_service_name, le)
        )

    - record: istio:request_duration:p95
      expr: |
        histogram_quantile(0.95,
          sum(rate(istio_request_duration_milliseconds_bucket{reporter="destination"}[5m]))
          by (destination_service_name, le)
        )

    - record: istio:request_duration:p99
      expr: |
        histogram_quantile(0.99,
          sum(rate(istio_request_duration_milliseconds_bucket{reporter="destination"}[5m]))
          by (destination_service_name, le)
        )
```

### Federation for Multi-Cluster

Federate Istio metrics across clusters:

```yaml
scrape_configs:
- job_name: 'federate-cluster-east'
  scrape_interval: 30s
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
    - '{__name__=~"istio_.*"}'
  static_configs:
  - targets:
    - 'prometheus.cluster-east.example.com:9090'
    labels:
      cluster: 'east'
```

## Health Checking

Istio integrates with Kubernetes health probes while providing application isolation from the sidecar proxy.

### Kubernetes Health Probe Flow

When a sidecar is present:

1. Kubelet sends health probe request to pod IP and probe port
2. Istio sidecar intercepts the request (via iptables rules)
3. Sidecar forwards request to application container
4. Application responds to sidecar
5. Sidecar returns response to kubelet

This flow is transparent to both kubelet and application.

### Health Probe Rewriting

Istio automatically rewrites health probe configuration during injection:

**Original pod spec:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:v1
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
```

**After sidecar injection:**
The pod's probes are rewritten to use a dedicated health check port (15021) on the sidecar, and the sidecar is configured to proxy these requests to the original application endpoints.

### Disable Health Probe Rewrite

If you need direct health checking (bypass sidecar):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  annotations:
    sidecar.istio.io/rewriteAppHTTPProbers: "false"
spec:
  containers:
  - name: app
    image: myapp:v1
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
```

### Envoy Health Endpoints

Envoy proxy exposes its own health endpoints:

- `/healthz/ready`: Proxy is ready to accept traffic (15021)
- Includes application health check status
- Used by Kubernetes readiness probes

Example direct query:
```bash
kubectl exec -it pod-name -c istio-proxy -- curl localhost:15021/healthz/ready
```

### Startup Probes with Istio

For applications with slow startup:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: slow-starter
spec:
  containers:
  - name: app
    image: myapp:v1
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
```

Istio handles all three probe types (startup, liveness, readiness) with transparent rewriting.

## Best Practices

### Metrics

1. **Monitor cardinality**: Use Prometheus metrics to track series count (`prometheus_tsdb_symbol_table_size_bytes`)
2. **Use recording rules**: Pre-aggregate common queries for dashboard performance
3. **Disable unused metrics**: Reduce overhead by disabling metrics not used in your environment
4. **Consistent labeling**: Maintain consistent label naming across custom tags

### Logging

1. **Enable selectively**: Use workload selectors to log only critical services
2. **Filter noise**: Use CEL expressions to exclude health checks and successful requests
3. **Structured format**: Use JSON for easier parsing by log aggregators
4. **Sample high-volume**: Consider sampling access logs for very high-traffic services

### Tracing

1. **Appropriate sampling**: Balance cost and coverage (1-10% for production)
2. **Propagate headers**: Ensure all services forward trace context headers
3. **Add business context**: Use custom tags for user IDs, tenant IDs, transaction IDs
4. **Monitor backend load**: Tracing backends can become bottlenecks at high sampling rates

### Integration

1. **Centralize configuration**: Use mesh-wide Telemetry resources in istio-system
2. **Layer overrides**: Apply specific configurations at namespace or workload level
3. **Version telemetry configs**: Track changes to observability configuration
4. **Test before production**: Validate custom metrics and logs in staging environments
