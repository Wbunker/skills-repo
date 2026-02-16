# Advanced Traffic Management with Istio

This reference covers advanced traffic management patterns in Istio, including progressive deployment strategies, resilience patterns, and sophisticated routing techniques. These capabilities leverage Envoy proxy features through Istio's configuration APIs.

## Canary Deployments

Canary deployments gradually shift traffic from a stable version to a new version, allowing validation with production traffic before full rollout. Istio enables fine-grained control over traffic distribution through VirtualService weights.

### Basic Weight-Based Canary

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-canary
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        user-agent:
          regex: '.*Mobile.*'
    route:
    - destination:
        host: reviews
        subset: v2
      weight: 50
    - destination:
        host: reviews
        subset: v1
      weight: 50
  - route:
    - destination:
        host: reviews
        subset: v2
      weight: 10
    - destination:
        host: reviews
        subset: v1
      weight: 90
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

This configuration sends 10% of general traffic to v2, while mobile users see a 50/50 split for additional testing.

### Header-Based Internal Canary

Before exposing a canary to public traffic, test with internal users using header matching:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-internal-canary
spec:
  hosts:
  - product.example.com
  http:
  - match:
    - headers:
        x-canary-user:
          exact: "true"
    route:
    - destination:
        host: product
        subset: v2
  - match:
    - headers:
        x-employee:
          prefix: "eng-"
    route:
    - destination:
        host: product
        subset: v2
      weight: 50
    - destination:
        host: product
        subset: v1
      weight: 50
  - route:
    - destination:
        host: product
        subset: v1
```

Internal canary users with `x-canary-user: true` always receive v2, engineering employees see 50/50, and public traffic goes entirely to v1.

### Progressive Canary Stages

A typical canary progression involves multiple weight adjustments:

1. **Stage 1**: 5% canary traffic, monitor metrics
2. **Stage 2**: 25% canary traffic, validate performance
3. **Stage 3**: 50% canary traffic, check for issues at scale
4. **Stage 4**: 100% canary traffic, complete rollout

Each stage requires updating the VirtualService weight and monitoring before proceeding.

### Automated Canary with Flagger

Flagger automates progressive canary analysis by monitoring metrics and adjusting weights:

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: product
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: product
  progressDeadlineSeconds: 600
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://product-canary:8080/"
```

Flagger creates and manages the VirtualService, incrementing weights while monitoring success rate and latency.

## Circuit Breaking

Circuit breaking prevents cascading failures by limiting concurrent requests and connections to unhealthy services. Istio implements circuit breakers through DestinationRule configuration.

### Connection Pool Circuit Breaking

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-circuit-breaker
spec:
  host: backend
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 3s
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 10
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
        maxRetries: 3
        h2UpgradePolicy: UPGRADE
```

Configuration breakdown:
- `maxConnections`: Maximum TCP connections to backend (100)
- `http1MaxPendingRequests`: Maximum HTTP/1.1 requests queued waiting for connection (10)
- `http2MaxRequests`: Maximum concurrent HTTP/2 requests (100)
- `maxRequestsPerConnection`: Requests per connection before closing (2, forces connection rotation)
- `maxRetries`: Maximum concurrent retry requests (3)

When limits are exceeded, Envoy immediately returns `503 Service Unavailable` without attempting the request.

### Outlier Detection

Outlier detection monitors service instances and temporarily removes unhealthy endpoints from the load balancing pool:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-outlier-detection
spec:
  host: backend
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        http2MaxRequests: 100
    outlierDetection:
      consecutiveGatewayErrors: 5
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
      splitExternalLocalOriginErrors: true
```

Parameters explained:
- `consecutiveGatewayErrors`: Number of 502/503/504 errors before ejection (5)
- `consecutive5xxErrors`: Number of any 5xx errors before ejection (5)
- `interval`: Analysis interval for error detection (10s)
- `baseEjectionTime`: Minimum ejection duration (30s, doubles for subsequent ejections)
- `maxEjectionPercent`: Maximum percentage of hosts that can be ejected (50%)
- `minHealthPercent`: Minimum percentage that must remain healthy (30%, overrides maxEjectionPercent)
- `splitExternalLocalOriginErrors`: Distinguish between upstream (5xx) and local Envoy errors

Envoy implements passive health checking through outlier detection, ejecting hosts based on observed request failures rather than active probes.

### Monitoring Circuit Breaker Events

Circuit breaker tripping generates metrics observable in Prometheus:

```promql
# Upstream overflow (circuit opened)
envoy_cluster_upstream_rq_pending_overflow{cluster_name="outbound|8080||backend.default.svc.cluster.local"}

# Connection pool overflow
envoy_cluster_upstream_cx_overflow{cluster_name="outbound|8080||backend.default.svc.cluster.local"}

# Ejected hosts
envoy_cluster_outlier_detection_ejections_active{cluster_name="outbound|8080||backend.default.svc.cluster.local"}
```

## Fault Injection

Fault injection tests application resilience by deliberately introducing errors and delays. This validates retry logic, timeout handling, and circuit breaker configuration.

### Delay Injection

Inject latency to test timeout behavior:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-delay-injection
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        x-chaos-test:
          exact: "delay"
    fault:
      delay:
        percentage:
          value: 100
        fixedDelay: 5s
    route:
    - destination:
        host: reviews
        subset: v1
  - route:
    - destination:
        host: reviews
        subset: v1
```

Requests with `x-chaos-test: delay` header experience a 5-second delay before reaching the reviews service. The `percentage` field allows partial injection (e.g., `value: 10` for 10% of requests).

### Abort Injection

Inject HTTP errors to test error handling:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-abort-injection
spec:
  hosts:
  - ratings
  http:
  - match:
    - headers:
        x-user:
          exact: "chaos-engineer"
    fault:
      abort:
        percentage:
          value: 50
        httpStatus: 503
    route:
    - destination:
        host: ratings
        subset: v1
  - route:
    - destination:
        host: ratings
        subset: v1
```

50% of requests from the chaos-engineer user receive immediate `503 Service Unavailable` responses without reaching the ratings service.

### Combined Delay and Abort

Test complex failure scenarios with combined faults:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-combined-faults
spec:
  hosts:
  - product
  http:
  - match:
    - sourceLabels:
        app: loadtest
    fault:
      delay:
        percentage:
          value: 20
        fixedDelay: 3s
      abort:
        percentage:
          value: 10
        httpStatus: 500
    route:
    - destination:
        host: product
        subset: v1
```

Load testing traffic experiences 3-second delays on 20% of requests and 500 errors on 10% of requests, simulating degraded backend performance.

## Retries

Automatic retries improve reliability by transparently re-attempting failed requests. Istio configures retries through VirtualService specifications.

### Basic Retry Configuration

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: backend-retries
spec:
  hosts:
  - backend
  http:
  - route:
    - destination:
        host: backend
        subset: v1
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

Configuration elements:
- `attempts`: Maximum retry attempts (3 total tries: 1 original + 2 retries)
- `perTryTimeout`: Timeout for each attempt (2s per try)
- `retryOn`: Conditions triggering retry (comma-separated list)

### Retry Conditions

The `retryOn` field accepts multiple conditions:

- `5xx`: Any 5xx response code
- `gateway-error`: 502, 503, or 504 errors
- `reset`: TCP connection reset by peer
- `connect-failure`: Connection refused or timed out
- `refused-stream`: HTTP/2 REFUSED_STREAM error
- `retriable-4xx`: 409 Conflict errors
- `cancelled`: gRPC cancelled status
- `deadline-exceeded`: gRPC deadline exceeded
- `internal`: gRPC internal error
- `resource-exhausted`: gRPC resource exhausted
- `unavailable`: gRPC unavailable status

### Advanced Retry Policy

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-advanced-retries
spec:
  hosts:
  - api.example.com
  http:
  - match:
    - uri:
        prefix: /v1/orders
    route:
    - destination:
        host: orders
        subset: v1
    retries:
      attempts: 5
      perTryTimeout: 1s
      retryOn: 5xx,reset,connect-failure
      retryRemoteLocalities: true
    timeout: 10s
  - route:
    - destination:
        host: api
        subset: v1
    retries:
      attempts: 2
      perTryTimeout: 3s
      retryOn: gateway-error
```

The orders endpoint allows 5 retry attempts with 1-second timeout per try and 10-second overall timeout. The `retryRemoteLocalities` field enables retries to remote zones when local instances fail.

### Retry Budget

Excessive retries can amplify failures. Configure EnvoyFilter to limit retry budget:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: retry-budget
spec:
  configPatches:
  - applyTo: HTTP_ROUTE
    match:
      context: SIDECAR_OUTBOUND
      routeConfiguration:
        vhost:
          name: backend.default.svc.cluster.local:8080
          route:
            name: default
    patch:
      operation: MERGE
      value:
        retry_policy:
          retry_back_off:
            base_interval: 0.025s
            max_interval: 0.25s
          retry_host_predicate:
          - name: envoy.retry_host_predicates.previous_hosts
          host_selection_retry_max_attempts: 3
```

This configuration adds exponential backoff (25ms to 250ms) and avoids retrying the same failing host.

## Timeouts

Timeouts prevent requests from blocking indefinitely, enabling fast failure and retry opportunities. Istio configures timeouts at multiple levels.

### Request Timeout

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: backend-timeout
spec:
  hosts:
  - backend
  http:
  - route:
    - destination:
        host: backend
        subset: v1
    timeout: 5s
```

The request must complete within 5 seconds or Envoy returns `504 Gateway Timeout`.

### Per-Route Timeouts

Different routes can have different timeout requirements:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-route-timeouts
spec:
  hosts:
  - api.example.com
  http:
  - match:
    - uri:
        prefix: /v1/reports
    route:
    - destination:
        host: reports
        subset: v1
    timeout: 60s
  - match:
    - uri:
        prefix: /v1/search
    route:
    - destination:
        host: search
        subset: v1
    timeout: 3s
  - route:
    - destination:
        host: api
        subset: v1
    timeout: 10s
```

Report generation allows 60 seconds, search queries timeout at 3 seconds, and default operations timeout at 10 seconds.

### Timeout and Retry Interaction

When combining timeouts and retries, consider the total time budget:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: backend-timeout-retry
spec:
  hosts:
  - backend
  http:
  - route:
    - destination:
        host: backend
        subset: v1
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
      retryOn: 5xx,reset
```

Each retry attempt has a 3-second timeout, allowing 3 attempts within the 10-second overall timeout. The third attempt must complete by the 10-second deadline even if it hasn't reached its 3-second perTryTimeout.

### Idle Timeout

Configure idle timeout in DestinationRule to close inactive connections:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-idle-timeout
spec:
  host: backend
  trafficPolicy:
    connectionPool:
      tcp:
        connectTimeout: 5s
      http:
        idleTimeout: 60s
```

HTTP connections idle for 60 seconds are closed, releasing resources.

## Traffic Mirroring

Traffic mirroring (shadowing) duplicates production traffic to a secondary service for testing without affecting user responses. The mirrored service processes requests, but responses are discarded.

### Basic Mirroring

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-mirror
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 100
    mirror:
      host: reviews
      subset: v2
    mirrorPercentage:
      value: 100
```

All production traffic goes to v1, while 100% is mirrored to v2. Responses from v2 are ignored, ensuring no impact on user experience.

### Partial Mirroring

Mirror a percentage of traffic to reduce load on the shadow service:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-partial-mirror
spec:
  hosts:
  - product.example.com
  http:
  - route:
    - destination:
        host: product
        subset: stable
    mirror:
      host: product
      subset: experimental
    mirrorPercentage:
      value: 10
```

Only 10% of production traffic is mirrored to the experimental version, reducing resource consumption while still providing realistic testing data.

### Use Cases for Mirroring

1. **Performance Testing**: Validate that a new version handles production load patterns
2. **Regression Testing**: Compare outputs between versions to detect differences
3. **Capacity Planning**: Measure resource consumption under real traffic
4. **Database Migration**: Test new database queries with production parameters
5. **Bug Investigation**: Reproduce production issues in a safe environment

### Mirroring Semantics

Traffic mirroring uses fire-and-forget semantics:
- Mirrored requests are sent asynchronously
- Responses are discarded and don't affect user-facing latency
- Errors from the mirror service don't impact production requests
- Host headers can be modified with `mirrorPercent` for shadow service routing

## Rate Limiting

Rate limiting protects services from overload by restricting request rates. Istio supports both local (per-proxy) and global (cluster-wide) rate limiting.

### Local Rate Limiting with EnvoyFilter

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: local-ratelimit
  namespace: default
spec:
  workloadSelector:
    labels:
      app: api
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
            subFilter:
              name: envoy.filters.http.router
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          '@type': type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          stat_prefix: http_local_rate_limiter
          token_bucket:
            max_tokens: 100
            tokens_per_fill: 100
            fill_interval: 60s
          filter_enabled:
            runtime_key: local_rate_limit_enabled
            default_value:
              numerator: 100
              denominator: HUNDRED
          filter_enforced:
            runtime_key: local_rate_limit_enforced
            default_value:
              numerator: 100
              denominator: HUNDRED
          response_headers_to_add:
          - append: false
            header:
              key: x-local-rate-limit
              value: 'true'
```

This configuration limits each proxy instance to 100 requests per minute using a token bucket algorithm. When the limit is exceeded, Envoy returns `429 Too Many Requests`.

### Per-Route Rate Limiting

Apply different rate limits to specific routes:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: route-ratelimit
spec:
  workloadSelector:
    labels:
      app: api
  configPatches:
  - applyTo: VIRTUAL_HOST
    match:
      context: SIDECAR_INBOUND
    patch:
      operation: MERGE
      value:
        rate_limits:
        - actions:
          - request_headers:
              header_name: x-api-key
              descriptor_key: api_key
        - actions:
          - remote_address: {}
  - applyTo: HTTP_ROUTE
    match:
      context: SIDECAR_INBOUND
      routeConfiguration:
        vhost:
          route:
            name: default
    patch:
      operation: MERGE
      value:
        route:
          rate_limits:
          - actions:
            - header_value_match:
                descriptor_value: premium
                headers:
                - name: x-tier
                  exact_match: premium
```

This configuration rate-limits based on API key and remote address, with special handling for premium tier users.

### Global Rate Limiting

Global rate limiting requires a central rate limit service and more complex configuration:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: global-ratelimit
spec:
  workloadSelector:
    labels:
      app: api
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
            subFilter:
              name: envoy.filters.http.router
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.ratelimit
        typed_config:
          '@type': type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
          domain: production
          failure_mode_deny: false
          rate_limit_service:
            grpc_service:
              envoy_grpc:
                cluster_name: rate_limit_cluster
            transport_api_version: V3
  - applyTo: CLUSTER
    patch:
      operation: ADD
      value:
        name: rate_limit_cluster
        connect_timeout: 0.25s
        lb_policy: ROUND_ROBIN
        http2_protocol_options: {}
        load_assignment:
          cluster_name: rate_limit_cluster
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: ratelimit.istio-system.svc.cluster.local
                    port_value: 8081
```

Global rate limiting enforces limits across all proxy instances by consulting a central service, enabling per-user or per-tenant quotas.

## Locality Load Balancing

Locality-aware load balancing routes traffic preferentially to nearby service instances, reducing latency and improving availability during partial failures.

### Locality Configuration

Kubernetes nodes have locality labels:
- `topology.kubernetes.io/region`: Cloud provider region (e.g., us-west-2)
- `topology.kubernetes.io/zone`: Availability zone (e.g., us-west-2a)

Istio derives endpoint locality from these node labels.

### Distribute Traffic by Locality

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-locality
spec:
  host: backend
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-west-2/us-west-2a/*
          to:
            "us-west-2/us-west-2a/*": 80
            "us-west-2/us-west-2b/*": 20
        - from: us-west-2/us-west-2b/*
          to:
            "us-west-2/us-west-2b/*": 80
            "us-west-2/us-west-2a/*": 20
```

Clients in zone 2a send 80% of traffic to local endpoints and 20% to zone 2b, achieving soft locality preference while maintaining cross-zone redundancy.

### Failover Configuration

Configure locality-based failover for graceful degradation:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-locality-failover
spec:
  host: backend
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        failover:
        - from: us-west-2
          to: us-east-1
    outlierDetection:
      consecutiveErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

When outlier detection removes all healthy endpoints in us-west-2, traffic fails over to us-east-1. Without outlier detection, failover only occurs when zero healthy endpoints exist in the primary locality.

### Failover Priority

Configure multi-level failover:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: backend-failover-priority
spec:
  host: backend
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        failoverPriority:
        - "topology.kubernetes.io/zone"
        - "topology.kubernetes.io/region"
```

Traffic fails over first to other zones in the same region, then to other regions only if all zones in the primary region are unhealthy.

## Multi-Cluster Routing

Multi-cluster deployments enable high availability, geographic distribution, and disaster recovery. Istio provides service discovery and routing across cluster boundaries.

### East-West Gateway

Multi-cluster communication requires an east-west gateway exposing services:

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  components:
    ingressGateways:
    - name: istio-eastwestgateway
      label:
        istio: eastwestgateway
        app: istio-eastwestgateway
      enabled: true
      k8s:
        env:
        - name: ISTIO_META_ROUTER_MODE
          value: "sni-dnat"
        service:
          ports:
          - name: status-port
            port: 15021
            targetPort: 15021
          - name: tls
            port: 15443
            targetPort: 15443
          - name: tls-istiod
            port: 15012
            targetPort: 15012
          - name: tls-webhook
            port: 15017
            targetPort: 15017
```

The east-west gateway uses SNI-based routing to expose services to remote clusters without requiring individual gateway configurations per service.

### Gateway for Cross-Cluster Services

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: cross-network-gateway
spec:
  selector:
    istio: eastwestgateway
  servers:
  - port:
      number: 15443
      name: tls
      protocol: TLS
    tls:
      mode: AUTO_PASSTHROUGH
    hosts:
    - "*.local"
```

This gateway accepts TLS connections on port 15443 and routes based on SNI, enabling transparent cross-cluster service access.

### Multi-Primary Mesh

In a multi-primary configuration, each cluster runs its own control plane:

```bash
# Install Istio on cluster1
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1 \
  --set values.global.network=network1

# Install Istio on cluster2
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster2 \
  --set values.global.network=network2

# Enable endpoint discovery
istioctl x create-remote-secret --name=cluster1 | \
  kubectl apply -f - --context=cluster2

istioctl x create-remote-secret --name=cluster2 | \
  kubectl apply -f - --context=cluster1
```

Each cluster discovers services in remote clusters through API server secrets, creating a unified service registry.

### Primary-Remote Configuration

In primary-remote topology, the primary cluster hosts the control plane:

```bash
# Install control plane on primary cluster
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=primary \
  --set values.global.network=network1

# Configure remote cluster
istioctl install --set profile=remote \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=remote \
  --set values.global.network=network2 \
  --set values.istiodRemote.injectionURL=https://primary-istiod:15017/inject
```

Remote clusters use the primary control plane for configuration but maintain local data plane proxies.

### Cross-Cluster Service Discovery

Service endpoints from all clusters appear in the unified service registry:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: backend-multi-cluster
spec:
  hosts:
  - backend.default.svc.cluster.local
  location: MESH_INTERNAL
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: backend.default.svc.cluster1.local
    locality: us-west-2/us-west-2a
    labels:
      cluster: cluster1
  - address: backend.default.svc.cluster2.local
    locality: us-east-1/us-east-1a
    labels:
      cluster: cluster2
```

VirtualServices and DestinationRules apply across clusters, enabling unified traffic management.

## Request Hedging and Advanced Timeout Patterns

Hedging sends duplicate requests after a timeout to improve tail latency without waiting for the initial request to fail.

### Hedging with Early Request

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: hedging-policy
spec:
  workloadSelector:
    labels:
      app: api
  configPatches:
  - applyTo: HTTP_ROUTE
    match:
      context: SIDECAR_OUTBOUND
      routeConfiguration:
        vhost:
          name: backend.default.svc.cluster.local:8080
    patch:
      operation: MERGE
      value:
        route:
          hedge_policy:
            hedge_on_per_try_timeout: true
            initial_requests: 1
            additional_request_chance:
              numerator: 25
              denominator: HUNDRED
        timeout: 5s
        retry_policy:
          perTryTimeout: 2s
          numRetries: 2
```

If the initial request doesn't complete within 2 seconds (perTryTimeout), Envoy has a 25% chance of sending a hedged request to a different backend instance. The first successful response is returned to the client.

### Adaptive Timeout with Percentile

Configure timeouts based on observed latency distribution:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: adaptive-timeout
spec:
  workloadSelector:
    labels:
      app: api
  configPatches:
  - applyTo: CLUSTER
    match:
      context: SIDECAR_OUTBOUND
      cluster:
        name: "outbound|8080||backend.default.svc.cluster.local"
    patch:
      operation: MERGE
      value:
        circuit_breakers:
          thresholds:
          - priority: DEFAULT
            retry_budget:
              budget_percent:
                value: 20.0
              min_retry_concurrency: 10
        track_cluster_stats:
          timeout_budgets: true
```

This configuration tracks timeout statistics and adjusts retry behavior based on actual service performance, enabling adaptive resilience.

### Budget-Based Timeout

Allocate time budgets across service tiers:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: tiered-timeouts
spec:
  hosts:
  - api.example.com
  http:
  - match:
    - uri:
        prefix: /v1/critical
    route:
    - destination:
        host: critical-service
    timeout: 2s
    retries:
      attempts: 1
      perTryTimeout: 1s
  - match:
    - uri:
        prefix: /v1/standard
    route:
    - destination:
        host: standard-service
    timeout: 5s
    retries:
      attempts: 2
      perTryTimeout: 2s
  - match:
    - uri:
        prefix: /v1/batch
    route:
    - destination:
        host: batch-service
    timeout: 30s
    retries:
      attempts: 0
```

Critical services receive aggressive timeouts (2s total) for fast failure, standard services allow moderate latency (5s), and batch operations permit extended processing (30s).

These advanced traffic management patterns enable sophisticated deployment strategies, resilience mechanisms, and routing policies that handle production complexity while maintaining service reliability and performance.
