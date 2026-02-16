# Traffic Management Fundamentals

Istio provides powerful traffic management capabilities through a set of Custom Resource Definitions (CRDs) that control routing, resilience, and load balancing for service mesh traffic. This reference covers the core traffic management resources and patterns.

## VirtualService

VirtualService is the primary resource for configuring how requests are routed to services within the mesh. It defines a set of traffic routing rules to apply when a host is addressed.

### Core Components

**Hosts**: The destination hosts to which traffic is being sent. Can be a DNS name with wildcard prefix or a fully qualified domain name.

**Gateways**: Specifies which gateways and sidecars the routing rules should apply to. Reserved name `mesh` refers to all sidecars in the mesh.

**HTTP Routes**: Ordered list of route rules for HTTP/1.1, HTTP2, and gRPC traffic.

**TCP Routes**: Ordered list of route rules for TCP traffic.

**TLS Routes**: Ordered list of route rules for TLS/HTTPS traffic using SNI.

### Match Conditions

VirtualService supports sophisticated matching logic:

**URI Matching**:
- `exact`: Exact string match
- `prefix`: Prefix-based match
- `regex`: ECMAScript style regex match

**Header Matching**: Match on HTTP headers with exact, prefix, or regex matching.

**Method Matching**: Match specific HTTP methods (GET, POST, etc.).

**Query Parameters**: Match on query string parameters.

**Source Labels**: Match based on source workload labels.

**Port**: Match requests targeting specific ports.

### Complete VirtualService Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
  namespace: default
spec:
  hosts:
  - reviews.default.svc.cluster.local
  gateways:
  - mesh
  - ingress-gateway
  http:
  - name: "reviews-v2-route"
    match:
    - headers:
        user-agent:
          regex: ".*Mobile.*"
      uri:
        prefix: "/api/reviews"
      queryParams:
        version:
          exact: "beta"
      method:
        exact: "GET"
      sourceLabels:
        app: productpage
        version: v1
    route:
    - destination:
        host: reviews.default.svc.cluster.local
        subset: v2
        port:
          number: 9080
      weight: 100
      headers:
        request:
          add:
            x-custom-header: "mobile-user"
          set:
            x-envoy-upstream-rq-timeout-ms: "1000"
          remove:
          - x-legacy-header
        response:
          add:
            x-response-source: "reviews-v2"
    rewrite:
      uri: "/reviews"
      authority: "reviews-internal.svc.cluster.local"
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: "5xx,reset,connect-failure,refused-stream"
      retryRemoteLocalities: false
    fault:
      delay:
        percentage:
          value: 10.0
        fixedDelay: 5s
      abort:
        percentage:
          value: 5.0
        httpStatus: 503
    corsPolicy:
      allowOrigins:
      - exact: "https://example.com"
      - prefix: "https://*.example.com"
      allowMethods:
      - GET
      - POST
      - OPTIONS
      allowHeaders:
      - content-type
      - authorization
      maxAge: "24h"
      allowCredentials: true
  - name: "reviews-default-route"
    route:
    - destination:
        host: reviews.default.svc.cluster.local
        subset: v1
      weight: 80
    - destination:
        host: reviews.default.svc.cluster.local
        subset: v3
      weight: 20
```

### Redirect Configuration

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: redirect-example
spec:
  hosts:
  - oldservice.example.com
  http:
  - match:
    - uri:
        prefix: "/old-api"
    redirect:
      uri: "/new-api"
      authority: newservice.example.com
      scheme: https
      redirectCode: 301
```

### Delegated VirtualServices

VirtualServices can delegate routing to other VirtualServices, enabling modular configuration:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: root-vs
spec:
  hosts:
  - api.example.com
  gateways:
  - api-gateway
  http:
  - match:
    - uri:
        prefix: "/reviews"
    delegate:
      name: reviews-vs
      namespace: reviews-ns
  - match:
    - uri:
        prefix: "/ratings"
    delegate:
      name: ratings-vs
      namespace: ratings-ns
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-vs
  namespace: reviews-ns
spec:
  hosts:
  - api.example.com
  http:
  - match:
    - uri:
        prefix: "/reviews/v2"
    route:
    - destination:
        host: reviews.reviews-ns.svc.cluster.local
        subset: v2
  - route:
    - destination:
        host: reviews.reviews-ns.svc.cluster.local
        subset: v1
```

## DestinationRule

DestinationRule defines policies that apply to traffic intended for a service after routing has occurred. It configures load balancing, connection pool sizes, outlier detection, and TLS settings.

### Core Components

**Host**: Name of the service to which the policies apply.

**TrafficPolicy**: Default traffic policies for all subsets.

**Subsets**: Named sets of endpoints, typically defined by pod labels, representing service versions.

### Complete DestinationRule Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-destination
  namespace: default
spec:
  host: reviews.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: "x-user-id"
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30ms
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
        maxRetries: 3
        h2UpgradePolicy: UPGRADE
        idleTimeout: 3600s
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
      consecutiveGatewayErrors: 5
      consecutiveLocalOriginFailures: 5
    tls:
      mode: ISTIO_MUTUAL
      sni: reviews.default.svc.cluster.local
      subjectAltNames:
      - spiffe://cluster.local/ns/default/sa/reviews
  subsets:
  - name: v1
    labels:
      version: v1
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      loadBalancer:
        simple: LEAST_REQUEST
      connectionPool:
        tcp:
          maxConnections: 200
  - name: v3
    labels:
      version: v3
    trafficPolicy:
      loadBalancer:
        simple: RANDOM
```

### Load Balancer Settings

**ROUND_ROBIN**: Round robin policy, distributing requests evenly across endpoints.

**LEAST_REQUEST**: Routes to endpoints with the fewest active requests. Can specify `choiceCount` for performance optimization.

**RANDOM**: Routes to a random endpoint.

**PASSTHROUGH**: Forwards the connection to the original IP address requested by the caller without doing any load balancing.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: lb-examples
spec:
  host: myservice.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST
      # Alternative: least request with choice count
      # leastRequest:
      #   choiceCount: 2
```

### Connection Pool Settings

**TCP Settings**:
- `maxConnections`: Maximum number of HTTP1/TCP connections to a destination
- `connectTimeout`: TCP connection timeout
- `tcpKeepalive`: TCP keepalive configuration

**HTTP Settings**:
- `http1MaxPendingRequests`: Maximum pending requests to a destination (HTTP/1.1 only)
- `http2MaxRequests`: Maximum requests to a destination (HTTP/2+)
- `maxRequestsPerConnection`: Maximum requests per connection to a backend
- `maxRetries`: Maximum number of retries
- `h2UpgradePolicy`: Policy for upgrading HTTP/1.1 connections to HTTP/2
- `idleTimeout`: Idle timeout for upstream connection pool connections

### Outlier Detection

Outlier detection removes unhealthy hosts from the load balancing pool:

```yaml
outlierDetection:
  consecutive5xxErrors: 5           # Number of 5xx errors before ejection
  consecutiveGatewayErrors: 5       # Number of gateway errors (502, 503, 504)
  consecutiveLocalOriginFailures: 5 # Local origin failures before ejection
  interval: 10s                     # Time interval for analysis
  baseEjectionTime: 30s             # Minimum ejection duration
  maxEjectionPercent: 50            # Maximum % of hosts that can be ejected
  minHealthPercent: 40              # Minimum % of healthy hosts required
  splitExternalLocalOriginErrors: false
```

### TLS Settings

**DISABLE**: No TLS connection to upstream.

**SIMPLE**: Originate a TLS connection to the upstream endpoint.

**MUTUAL**: Secure connections with mutual TLS by presenting client certificates.

**ISTIO_MUTUAL**: Use Istio's automatic mTLS certificates.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: tls-example
spec:
  host: external-service.com
  trafficPolicy:
    tls:
      mode: SIMPLE
      caCertificates: /etc/certs/ca.crt
      sni: external-service.com
  subsets:
  - name: mtls-subset
    trafficPolicy:
      tls:
        mode: MUTUAL
        clientCertificate: /etc/certs/client.crt
        privateKey: /etc/certs/client.key
        caCertificates: /etc/certs/ca.crt
```

## Gateway

Gateway configures a load balancer operating at the edge of the mesh for receiving incoming or outgoing HTTP/TCP connections. It describes exposed ports, protocols, and TLS settings.

### Complete Gateway Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: ingress-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway  # Use Istio's default ingress gateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "example.com"
    - "*.example.com"
    tls:
      httpsRedirect: true  # Redirect HTTP to HTTPS
  - port:
      number: 443
      name: https-default
      protocol: HTTPS
    hosts:
    - "example.com"
    tls:
      mode: SIMPLE
      credentialName: example-com-cert  # K8s secret in same namespace
      minProtocolVersion: TLSV1_2
      maxProtocolVersion: TLSV1_3
      cipherSuites:
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-RSA-AES256-GCM-SHA384
  - port:
      number: 443
      name: https-mtls
      protocol: HTTPS
    hosts:
    - "secure.example.com"
    tls:
      mode: MUTUAL
      credentialName: secure-example-mtls-cert
      minProtocolVersion: TLSV1_3
  - port:
      number: 443
      name: https-passthrough
      protocol: TLS
    hosts:
    - "passthrough.example.com"
    tls:
      mode: PASSTHROUGH
  - port:
      number: 27017
      name: mongo
      protocol: MONGO
    hosts:
    - "*"
  - port:
      number: 3306
      name: mysql
      protocol: TCP
    hosts:
    - "mysql.example.com"
```

### TLS Termination Modes

**SIMPLE**: Standard TLS termination. Gateway presents server certificate to clients.

**MUTUAL**: Mutual TLS. Gateway validates client certificates.

**PASSTHROUGH**: TLS handshake forwarded to backend. No termination at gateway.

**AUTO_PASSTHROUGH**: Similar to PASSTHROUGH but uses SNI value to route to the appropriate backend.

### Binding VirtualService to Gateway

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-vs
spec:
  hosts:
  - "api.example.com"
  gateways:
  - istio-system/ingress-gateway  # Reference gateway in another namespace
  - mesh                            # Also apply to mesh-internal traffic
  http:
  - match:
    - uri:
        prefix: "/v1"
    route:
    - destination:
        host: api-v1.default.svc.cluster.local
        port:
          number: 8080
```

### Multiple Gateways

You can expose services through multiple gateways for different purposes:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: external-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https-external
      protocol: HTTPS
    hosts:
    - "api.example.com"
    tls:
      mode: SIMPLE
      credentialName: external-cert
---
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: internal-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway-internal
  servers:
  - port:
      number: 443
      name: https-internal
      protocol: HTTPS
    hosts:
    - "internal.example.com"
    tls:
      mode: MUTUAL
      credentialName: internal-mtls-cert
```

## ServiceEntry

ServiceEntry enables adding entries to Istio's internal service registry, making external services part of the mesh or adding services not discovered automatically.

### Complete ServiceEntry Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-database
  namespace: default
spec:
  hosts:
  - postgres.external.com
  ports:
  - number: 5432
    name: postgres
    protocol: TCP
  location: MESH_EXTERNAL
  resolution: DNS
  endpoints:
  - address: postgres-1.external.com
    ports:
      postgres: 5432
    labels:
      region: us-east
  - address: postgres-2.external.com
    ports:
      postgres: 5432
    labels:
      region: us-west
---
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  - "*.api.external.com"
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
---
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: legacy-vm-service
spec:
  hosts:
  - legacy-service.internal
  addresses:
  - 10.1.2.0/24
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  - number: 9090
    name: metrics
    protocol: HTTP
  location: MESH_INTERNAL
  resolution: STATIC
  endpoints:
  - address: 10.1.2.10
    labels:
      version: v1
      env: prod
  - address: 10.1.2.11
    labels:
      version: v2
      env: prod
  workloadSelector:
    labels:
      app: legacy-service
```

### Location Settings

**MESH_EXTERNAL**: Service is external to the mesh. Typically used for external APIs, databases, or third-party services.

**MESH_INTERNAL**: Service is part of the mesh. Used for VM workloads or services that should be treated as mesh members.

### Resolution Settings

**NONE**: No resolution. Assumes the client already has the correct IP address.

**STATIC**: Use the static endpoints specified in the ServiceEntry.

**DNS**: Resolve DNS and use returned IPs for load balancing.

**DNS_ROUND_ROBIN**: Resolve DNS but treat all returned IPs as equal (no health checking).

### Exporting ServiceEntry

Control which namespaces can see the ServiceEntry:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: shared-database
  namespace: infrastructure
spec:
  hosts:
  - shared-db.example.com
  ports:
  - number: 3306
    name: mysql
    protocol: TCP
  location: MESH_EXTERNAL
  resolution: DNS
  exportTo:
  - "."              # Current namespace only
  - "team-a"         # Specific namespace
  - "team-b"
  # Use "*" for all namespaces (default)
```

### ServiceEntry with Workload Selector

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: vm-workload
spec:
  hosts:
  - vm-service.internal
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  location: MESH_INTERNAL
  resolution: STATIC
  workloadSelector:
    labels:
      app: vm-service
      type: vm
```

## Sidecar Resource

The Sidecar resource configures sidecar proxies attached to workloads in the mesh. It controls the set of services visible to the sidecar and the ports exposed by the workload.

### Complete Sidecar Example

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: default
spec:
  workloadSelector:
    labels:
      app: productpage
      version: v1
  ingress:
  - port:
      number: 9080
      protocol: HTTP
      name: http
    defaultEndpoint: 0.0.0.0:9080
    captureMode: DEFAULT
  - port:
      number: 3000
      protocol: HTTP
      name: http-alt
    defaultEndpoint: unix:///var/run/someuds.sock
    captureMode: NONE
  egress:
  - port:
      number: 443
      protocol: HTTPS
      name: https-external
    bind: 0.0.0.0
    captureMode: DEFAULT
    hosts:
    - "./*"                                    # All services in the same namespace
    - "istio-system/*"                         # All services in istio-system
    - "*/reviews.default.svc.cluster.local"   # Specific service in any namespace
  - port:
      number: 27017
      protocol: MONGO
      name: mongo
    hosts:
    - "*/mongodb.external.com"
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY  # Only allow traffic to services in the registry
```

### Workload Selector

If `workloadSelector` is omitted, the Sidecar configuration applies to all workloads in the namespace:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: namespace-default
  namespace: production
spec:
  # No workloadSelector - applies to all workloads in namespace
  egress:
  - hosts:
    - "./*"
    - "istio-system/*"
    - "shared-services/*"
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY
```

### Outbound Traffic Policy

**ALLOW_ANY**: Allow connections to unknown services. This is the default behavior.

**REGISTRY_ONLY**: Only allow outbound traffic to services defined in the service registry.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: strict-egress
  namespace: secure-namespace
spec:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY
    egressProxy:
      host: egress-gateway.istio-system.svc.cluster.local
      subset: v1
      port:
        number: 443
```

### Limiting Namespace Visibility

Reduce Envoy configuration size by limiting visible services:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: minimal-config
  namespace: microservice-a
spec:
  workloadSelector:
    labels:
      app: microservice-a
  egress:
  - hosts:
    - "./microservice-b.microservice-a.svc.cluster.local"
    - "./microservice-c.microservice-a.svc.cluster.local"
    - "istio-system/istio-telemetry.istio-system.svc.cluster.local"
```

### Ingress Listeners

Configure how workloads accept incoming connections:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: ingress-config
  namespace: default
spec:
  workloadSelector:
    labels:
      app: api-server
  ingress:
  - port:
      number: 8080
      protocol: HTTP
      name: http
    defaultEndpoint: 127.0.0.1:8080
    captureMode: DEFAULT
  - port:
      number: 8443
      protocol: HTTPS
      name: https
    defaultEndpoint: 127.0.0.1:8443
    captureMode: DEFAULT
    tls:
      mode: SIMPLE
      credentialName: api-server-cert
```

## Load Balancing

Istio provides multiple load balancing algorithms to distribute traffic across service endpoints.

### Simple Load Balancers

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: load-balancer-examples
spec:
  host: myservice.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN  # LEAST_REQUEST, RANDOM, PASSTHROUGH
```

### Consistent Hashing

Consistent hashing ensures the same backend handles requests based on specific attributes:

#### HTTP Header-Based Hashing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-session-affinity
spec:
  host: webapp.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: "x-user-id"
```

#### HTTP Cookie-Based Hashing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: cookie-affinity
spec:
  host: webapp.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpCookie:
          name: "session-id"
          ttl: 3600s
          path: "/api"
```

#### Source IP-Based Hashing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: source-ip-affinity
spec:
  host: stateful-service.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        useSourceIp: true
```

#### Query Parameter-Based Hashing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: query-param-affinity
spec:
  host: api.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpQueryParameterName: "tenant-id"
```

#### Ring Hash with Minimum Ring Size

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ring-hash-config
spec:
  host: distributed-cache.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: "x-cache-key"
        minimumRingSize: 1024
```

### Locality Load Balancing

Prefer endpoints in the same locality (zone/region):

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: locality-lb
spec:
  host: global-service.default.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-east-1/us-east-1a/*
          to:
            "us-east-1/us-east-1a/*": 80
            "us-east-1/us-east-1b/*": 20
        failover:
        - from: us-east-1
          to: us-west-1
```

## Traffic Splitting Patterns

Istio enables sophisticated traffic management patterns for deployments, testing, and migrations.

### Version-Based Routing

Route traffic to specific versions based on headers:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: version-routing
spec:
  hosts:
  - api.default.svc.cluster.local
  http:
  - match:
    - headers:
        x-api-version:
          exact: "v2"
    route:
    - destination:
        host: api.default.svc.cluster.local
        subset: v2
  - route:
    - destination:
        host: api.default.svc.cluster.local
        subset: v1
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-subsets
spec:
  host: api.default.svc.cluster.local
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Header-Based Routing

Route based on user identity, roles, or custom headers:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: header-routing
spec:
  hosts:
  - webapp.default.svc.cluster.local
  http:
  - match:
    - headers:
        x-user-role:
          exact: "beta-tester"
    route:
    - destination:
        host: webapp.default.svc.cluster.local
        subset: canary
  - match:
    - headers:
        x-user-role:
          exact: "internal"
    route:
    - destination:
        host: webapp.default.svc.cluster.local
        subset: staging
  - route:
    - destination:
        host: webapp.default.svc.cluster.local
        subset: stable
```

### Percentage-Based Traffic Splitting

Gradually shift traffic between versions:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: canary-deployment
spec:
  hosts:
  - reviews.default.svc.cluster.local
  http:
  - route:
    - destination:
        host: reviews.default.svc.cluster.local
        subset: v1
      weight: 90
    - destination:
        host: reviews.default.svc.cluster.local
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-destination
spec:
  host: reviews.default.svc.cluster.local
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Blue-Green Deployment

Instant cutover between versions:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: blue-green
spec:
  hosts:
  - payment.default.svc.cluster.local
  http:
  - route:
    - destination:
        host: payment.default.svc.cluster.local
        subset: green  # Change to 'blue' for rollback
      weight: 100
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-destination
spec:
  host: payment.default.svc.cluster.local
  subsets:
  - name: blue
    labels:
      version: blue
  - name: green
    labels:
      version: green
```

### A/B Testing

Route specific user segments to different versions:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ab-testing
spec:
  hosts:
  - frontend.default.svc.cluster.local
  http:
  - match:
    - headers:
        cookie:
          regex: "^(.*?;)?(experiment=variant-a)(;.*)?$"
    route:
    - destination:
        host: frontend.default.svc.cluster.local
        subset: variant-a
  - match:
    - headers:
        cookie:
          regex: "^(.*?;)?(experiment=variant-b)(;.*)?$"
    route:
    - destination:
        host: frontend.default.svc.cluster.local
        subset: variant-b
  - route:
    - destination:
        host: frontend.default.svc.cluster.local
        subset: control
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: frontend-destination
spec:
  host: frontend.default.svc.cluster.local
  subsets:
  - name: control
    labels:
      version: control
  - name: variant-a
    labels:
      version: variant-a
  - name: variant-b
    labels:
      version: variant-b
```

### Progressive Canary with Mirroring

Test new version with mirrored production traffic before routing live traffic:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: canary-with-mirror
spec:
  hosts:
  - analytics.default.svc.cluster.local
  http:
  - route:
    - destination:
        host: analytics.default.svc.cluster.local
        subset: stable
      weight: 95
    - destination:
        host: analytics.default.svc.cluster.local
        subset: canary
      weight: 5
    mirror:
      host: analytics.default.svc.cluster.local
      subset: canary
    mirrorPercentage:
      value: 100.0
```

### Multi-Dimensional Traffic Splitting

Combine multiple routing criteria:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: multi-dimensional-routing
spec:
  hosts:
  - recommendation.default.svc.cluster.local
  http:
  - match:
    - headers:
        x-user-tier:
          exact: "premium"
      sourceLabels:
        app: mobile-app
        version: v2
    route:
    - destination:
        host: recommendation.default.svc.cluster.local
        subset: ml-enhanced
  - match:
    - headers:
        x-user-tier:
          exact: "premium"
    route:
    - destination:
        host: recommendation.default.svc.cluster.local
        subset: advanced
  - match:
    - sourceLabels:
        app: mobile-app
    route:
    - destination:
        host: recommendation.default.svc.cluster.local
        subset: mobile-optimized
  - route:
    - destination:
        host: recommendation.default.svc.cluster.local
        subset: standard
```

## Best Practices

1. **Ordering Matters**: VirtualService rules are evaluated in order. Place more specific rules before general ones.

2. **Use Subsets Consistently**: Define subsets in DestinationRule before referencing them in VirtualService.

3. **Limit Sidecar Scope**: Use Sidecar resources to reduce Envoy configuration size, especially in large clusters.

4. **Export Control**: Use `exportTo` to control which namespaces can access ServiceEntry resources.

5. **Connection Pooling**: Configure connection pools based on your service's capacity and expected load.

6. **Outlier Detection**: Enable outlier detection to automatically remove unhealthy endpoints from load balancing.

7. **TLS Settings**: Use `ISTIO_MUTUAL` for mesh-internal traffic and configure appropriate modes for external services.

8. **Timeouts and Retries**: Set appropriate timeout and retry policies to prevent cascading failures.

9. **Locality Awareness**: Use locality load balancing for multi-region deployments to reduce latency and costs.

10. **Testing Traffic Patterns**: Use fault injection and mirroring to test new versions safely before routing production traffic.
