# Core Components

This reference covers Istio's core architectural components, including the control plane (istiod), data plane (Envoy proxies), and the mechanisms that connect them.

## istiod: The Unified Control Plane

Starting with Istio 1.5, the control plane was consolidated into a single binary called **istiod**. This replaced the previous microservices architecture that used separate deployments for Pilot, Citadel, and Galley.

### Consolidation Benefits

The monolithic istiod design provides:

- **Simplified operations** - single deployment, easier upgrades, reduced resource overhead
- **Reduced latency** - no inter-component RPC calls
- **Improved reliability** - fewer failure domains, simpler dependencies
- **Lower resource consumption** - shared memory and processes

### Component Functions Within istiod

Despite being a single binary, istiod maintains logical separation of the three core functions:

**Pilot** - Service discovery and traffic management
- Monitors Kubernetes API server for services, endpoints, and Istio configuration
- Translates high-level Istio APIs into Envoy configuration (xDS)
- Distributes configuration to all Envoy proxies via gRPC streams

**Citadel** - Certificate authority and identity management
- Issues and rotates workload certificates for mTLS
- Implements SPIFFE identity standard
- Manages certificate lifecycle via SDS (Secret Discovery Service)

**Galley** - Configuration validation and processing
- Validates Istio configuration before admission
- Implements Kubernetes validating webhook
- Ensures schema compliance and cross-resource consistency

### Service Discovery

istiod performs service discovery by:

1. **Watching Kubernetes resources** - Services, Endpoints/EndpointSlices, Pods, Nodes
2. **Building service registry** - Aggregates discovered services into internal model
3. **Extracting metadata** - Labels, annotations, ports, protocols
4. **Computing clusters** - Groups endpoints by service, subset (DestinationRule), version
5. **Pushing updates** - Sends incremental config changes to proxies via xDS

The service registry supports multiple sources (Kubernetes, Consul, VMs) through the ServiceRegistry abstraction.

### High Availability and Leader Election

For production deployments, istiod runs with multiple replicas (typically 2-3). Key HA mechanisms:

**Leader Election** - Uses Kubernetes lease-based leader election for certain operations:
- Configurable via `LEADER_ELECTION` environment variable
- Leader performs global operations (webhook management, certain validations)
- All replicas serve xDS traffic (no single point of failure)

**Stateless xDS Serving** - Each istiod replica can serve any proxy:
- Proxies connect to service IP (load balanced across replicas)
- Connection re-established automatically if replica fails
- Configuration state derived from Kubernetes API (no local state)

**Graceful Shutdown** - istiod drains connections during pod termination:
- Stops accepting new xDS connections
- Waits for existing streams to complete or timeout
- Proxies reconnect to healthy replicas

## Pilot: Traffic Management Brain

Pilot is the component within istiod responsible for translating Istio's high-level routing rules into low-level Envoy configuration.

### Configuration Translation Pipeline

1. **Watch Istio CRDs** - VirtualService, DestinationRule, Gateway, ServiceEntry, etc.
2. **Validate and process** - Check for conflicts, merge rules, apply defaults
3. **Generate Envoy config** - Create listeners, routes, clusters, endpoints
4. **Optimize and serialize** - Compress, deduplicate, convert to protobuf
5. **Push via xDS** - Send to relevant proxies based on scope

### xDS Protocol (Envoy Discovery Service)

Pilot communicates with Envoy proxies using the xDS protocol, a set of gRPC-based APIs:

**LDS (Listener Discovery Service)**
- Defines network listeners (IP:port combinations)
- Specifies filter chains for traffic processing
- Istio creates listeners for inbound (15006) and outbound (15001) traffic

```yaml
# Conceptual LDS response
listeners:
  - name: 0.0.0.0_15006  # Inbound listener
    address: 0.0.0.0:15006
    filter_chains:
      - filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              route_config: inbound|9080||
  - name: 0.0.0.0_15001  # Outbound listener
    address: 0.0.0.0:15001
    use_original_dst: true
```

**RDS (Route Discovery Service)**
- Defines HTTP routing tables
- Maps host headers to clusters (upstream services)
- Implements VirtualService rules (match conditions, rewrites, retries)

```yaml
# Route from VirtualService
route_config:
  virtual_hosts:
    - name: reviews.default.svc.cluster.local:9080
      domains: ["reviews.default.svc.cluster.local", "reviews", "reviews.default"]
      routes:
        - match: { prefix: "/", headers: [{name: "end-user", exact_match: "jason"}] }
          route: { cluster: outbound|9080|v2|reviews.default.svc.cluster.local }
        - match: { prefix: "/" }
          route: { cluster: outbound|9080|v1|reviews.default.svc.cluster.local }
```

**CDS (Cluster Discovery Service)**
- Defines upstream clusters (logical groups of endpoints)
- Specifies load balancing, health checks, circuit breakers
- Each subset from DestinationRule becomes a separate cluster

```yaml
# Cluster configuration
clusters:
  - name: outbound|9080|v1|reviews.default.svc.cluster.local
    type: EDS  # Endpoints from EDS
    lb_policy: LEAST_REQUEST
    circuit_breakers:
      thresholds:
        - max_connections: 1000
          max_requests: 1000
```

**EDS (Endpoint Discovery Service)**
- Provides actual backend IP addresses for clusters
- Dynamically updated as pods scale or move
- Supports locality-aware load balancing

**SDS (Secret Discovery Service)**
- Delivers TLS certificates and keys to Envoy
- Enables certificate rotation without restart
- Managed by Citadel component

### Incremental xDS (Delta xDS)

Istio supports incremental configuration updates to reduce bandwidth and CPU:

- **Resource versioning** - Each resource (listener, route, cluster) has a version
- **Delta computation** - Pilot sends only changed resources
- **ACK/NACK** - Proxies acknowledge updates or reject invalid config
- **Resource warming** - Clusters/endpoints pre-loaded before referenced by routes

This is critical at scale (1000+ services) to avoid full config pushes.

### Configuration Scoping

Pilot optimizes which configuration gets pushed to each proxy:

**Sidecar resource** - Explicitly declares what a workload can reach:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: prod
spec:
  egress:
    - hosts:
      - "./*"  # Only services in same namespace
      - "istio-system/*"
```

**Automatic scoping** - Without Sidecar resource, Pilot infers based on:
- Namespace boundaries
- Service dependencies (derived from ServiceEntry, VirtualService)
- Exported services (exportTo field)

## Citadel: Certificate Authority

Citadel manages the PKI infrastructure for mutual TLS authentication between workloads.

### SPIFFE Identity Standard

Istio implements the SPIFFE (Secure Production Identity Framework For Everyone) standard for workload identity:

**Identity Format**: `spiffe://<trust-domain>/ns/<namespace>/sa/<service-account>`

Example: `spiffe://cluster.local/ns/default/sa/bookinfo-productpage`

Components:
- **Trust domain** - Identifies the Istio mesh (default: `cluster.local`)
- **Namespace** - Kubernetes namespace of the workload
- **Service account** - Kubernetes ServiceAccount running the pod

This identity is encoded in the X.509 certificate's Subject Alternative Name (SAN) field.

### Certificate Issuance Workflow

1. **Proxy startup** - Envoy starts with no certificates
2. **SDS request** - Envoy sends SDS request to istiod via Unix domain socket (for Kubernetes) or via istiod agent
3. **Identity verification** - istiod validates the caller's Kubernetes token (JWT)
4. **Certificate generation** - Citadel generates certificate with:
   - SPIFFE identity in SAN
   - Public key from proxy's CSR
   - Expiration time (default: 24 hours)
   - Signature from Istio CA private key
5. **SDS response** - Certificate and key returned to Envoy
6. **Installation** - Envoy configures TLS contexts with new certificate

```
┌─────────┐                    ┌────────┐                    ┌─────────┐
│  Envoy  │                    │ Agent  │                    │ istiod  │
└────┬────┘                    └───┬────┘                    └────┬────┘
     │                             │                              │
     │ SDS request (unix socket)   │                              │
     │────────────────────────────>│                              │
     │                             │ CSR + K8s token (gRPC)       │
     │                             │─────────────────────────────>│
     │                             │                              │
     │                             │      Validate token          │
     │                             │      Generate cert           │
     │                             │                              │
     │                             │   SDS response (cert + key)  │
     │                             │<─────────────────────────────│
     │  SDS response               │                              │
     │<────────────────────────────│                              │
     │                             │                              │
```

### Certificate Rotation

Certificates are automatically rotated before expiration:

- **Default lifetime** - 24 hours (configurable via `DEFAULT_WORKLOAD_CERT_TTL`)
- **Rotation trigger** - At 50% of lifetime (12 hours by default)
- **Grace period** - Old certificate valid during rotation
- **Zero downtime** - Envoy hot-restarts TLS contexts

Configuration via MeshConfig:
```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    defaultConfig:
      proxyMetadata:
        CERT_ROTATION_MARGIN: "600s"  # Rotate 10 min before expiry
```

### Custom CA Integration

Istio supports plugging in external certificate authorities:

**Intermediate CA Mode** - istiod acts as intermediate CA:
1. Administrator provisions root CA certificate and signing key
2. Install as Kubernetes secret in istio-system namespace
3. istiod uses this to sign workload certificates

```bash
# Create secret with custom CA
kubectl create secret generic cacerts -n istio-system \
  --from-file=ca-cert.pem \
  --from-file=ca-key.pem \
  --from-file=root-cert.pem \
  --from-file=cert-chain.pem
```

**External CA via CSR** - istiod forwards CSRs to external CA:
- Requires custom integration (Cert-Manager, Vault, etc.)
- Uses Kubernetes CSR API or direct CA API
- Greater control over PKI hierarchy

### Trust Domain

The trust domain identifies the boundary of certificate authority trust:

- Default: `cluster.local`
- Configurable via MeshConfig: `trustDomain: "prod.example.com"`
- Multi-cluster meshes can share trust domain (federated identity)
- Trust bundles can span multiple domains (for migration)

Trust domain appears in:
- SPIFFE identity URIs
- Authorization policy rules (source.principal)
- Certificate validation logic

## Galley: Configuration Validation

Galley validates Istio configuration before it's admitted to Kubernetes.

### Validating Webhook

Istio installs a ValidatingWebhookConfiguration that intercepts:
- Istio CRD creates/updates (VirtualService, DestinationRule, etc.)
- ConfigMap changes (mesh config)
- Namespace changes (injection labels)

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: istiod-default-validator
webhooks:
  - name: rev.validation.istio.io
    clientConfig:
      service:
        name: istiod
        namespace: istio-system
        path: /validate
    rules:
      - apiGroups: ["networking.istio.io", "security.istio.io"]
        apiVersions: ["*"]
        operations: ["CREATE", "UPDATE"]
```

### Validation Checks

**Schema validation**:
- Required fields present
- Types match (string, int, duration, etc.)
- Enums have valid values
- Regex patterns compile

**Semantic validation**:
- Port numbers in valid range
- Service references exist (optional warning)
- CIDR blocks well-formed
- Weights sum to 100 (if applicable)

**Cross-resource validation**:
- Gateway references valid in VirtualService
- DestinationRule subsets match labels
- AuthorizationPolicy selectors valid

Example validation error:
```
Error from server: error when creating "virtual-service.yaml":
admission webhook "validation.istio.io" denied the request:
configuration is invalid: weighted routing total does not equal 100
```

### Bypass Validation

For emergency situations, validation can be bypassed with annotation:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
  annotations:
    "validation.istio.io/ignore": "true"  # Skip validation (not recommended)
```

## Envoy Sidecar Architecture

The Envoy proxy is the data plane component that handles all network traffic for a workload.

### Filter Chain Model

Envoy processes traffic through a series of filters:

```
Downstream → Listener → Network Filters → HTTP Connection Manager → HTTP Filters → Upstream
                          ↓                         ↓                      ↓
                    TCP Proxy              Router Filter          AuthN/AuthZ
                    Rate Limit             Retries/Timeout        Fault Injection
                    RBAC                   Rewrites               CORS
```

**Network filters** - Layer 4 (TCP/IP):
- `envoy.filters.network.tcp_proxy` - Generic TCP proxying
- `envoy.filters.network.http_connection_manager` - HTTP processing
- `envoy.filters.network.rbac` - Network-level authorization

**HTTP filters** - Layer 7 (HTTP):
- `envoy.filters.http.router` - Routes to upstream clusters
- `envoy.filters.http.fault` - Fault injection
- `envoy.filters.http.cors` - CORS headers
- `envoy.filters.http.jwt_authn` - JWT validation
- `istio_authn` - Istio authentication (peer/request auth)
- `istio_authz` - Istio authorization policies

### HTTP Connection Manager

The HTTP connection manager is the core HTTP processing filter:

```yaml
typed_config:
  "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
  stat_prefix: inbound_0.0.0.0_9080
  route_config:
    name: inbound|9080||
    virtual_hosts: [...]
  http_filters:
    - name: istio.metadata_exchange
    - name: istio.alpn
    - name: envoy.filters.http.cors
    - name: envoy.filters.http.fault
    - name: istio_authn
    - name: istio_authz
    - name: envoy.filters.http.router
```

Key responsibilities:
- HTTP/1.1 and HTTP/2 protocol handling
- Header manipulation
- Filter chain execution
- Route matching
- Tracing context propagation
- Statistics collection

### Key Listeners and Ports

**Port 15001 (Outbound)** - Virtual listener for all outbound traffic:
- Bound to 0.0.0.0:15001
- Uses `useOriginalDst: true` to restore original destination
- Traffic arrives here via iptables REDIRECT
- Routes based on original IP:port (from SO_ORIGINAL_DST socket option)

**Port 15006 (Inbound)** - Virtual listener for all inbound traffic:
- Bound to 0.0.0.0:15006
- Receives traffic redirected by iptables
- Terminates mTLS (if PeerAuthentication requires it)
- Forwards to application container on original port

**Port 15000 (Admin)** - Envoy admin interface:
- Local access only (127.0.0.1:15000)
- Endpoints: /config_dump, /stats, /clusters, /listeners
- Use `istioctl proxy-config` wrapper for convenient access

**Port 15020 (Status)** - Merged Prometheus metrics and health:
- `/healthz/ready` - Readiness endpoint
- Combined stats from Envoy and agent

**Port 15021 (Health)** - Health check server:
- `/healthz/ready` - Kubernetes readiness probe target
- Returns 200 when Envoy and application ready

**Port 15090 (Prometheus)** - Envoy metrics in Prometheus format:
- `/stats/prometheus` - All Envoy metrics
- Scraped by Prometheus (if configured)

### Clusters, Routes, and Endpoints

**Clusters** - Logical service backends:
```yaml
- name: outbound|9080|v1|reviews.default.svc.cluster.local
  type: EDS
  eds_cluster_config:
    service_name: outbound|9080|v1|reviews.default.svc.cluster.local
  connect_timeout: 10s
  lb_policy: LEAST_REQUEST
```

**Routes** - Traffic routing rules:
```yaml
routes:
  - match:
      prefix: /
      headers:
        - name: end-user
          exact_match: jason
    route:
      cluster: outbound|9080|v2|reviews.default.svc.cluster.local
      timeout: 15s
      retry_policy:
        retry_on: 5xx
        num_retries: 3
```

**Endpoints** - Actual pod IPs:
```yaml
endpoints:
  - lb_endpoints:
    - endpoint:
        address:
          socket_address:
            address: 10.244.1.5
            port_value: 9080
      load_balancing_weight: 1
```

## Sidecar Injection

Istio automatically injects the Envoy proxy sidecar into application pods.

### Automatic Injection

Enable automatic injection by labeling the namespace:

```bash
kubectl label namespace default istio-injection=enabled
```

When a pod is created in a labeled namespace:
1. Kubernetes sends pod create request to API server
2. MutatingWebhookConfiguration intercepts the request
3. Webhook calls istiod injection endpoint
4. istiod mutates pod spec to add:
   - Init container (`istio-init`)
   - Sidecar container (`istio-proxy`)
   - Volumes for certificates, logs, etc.
   - Annotations for configuration
5. Modified pod spec returned and pod created

### Manual Injection

For environments without webhook access:

```bash
# Inject into deployment YAML
istioctl kube-inject -f deployment.yaml | kubectl apply -f -

# Inject entire directory
istioctl kube-inject -f ./manifests/ | kubectl apply -f -
```

The `kube-inject` command:
- Reads original pod spec
- Applies same injection template as webhook
- Outputs modified YAML
- Does not modify cluster state directly

### Injection Webhook Configuration

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: istio-sidecar-injector
webhooks:
  - name: rev.namespace.sidecar-injector.istio.io
    clientConfig:
      service:
        name: istiod
        namespace: istio-system
        path: /inject
    namespaceSelector:
      matchLabels:
        istio-injection: enabled
```

### Init Container (istio-init)

The `istio-init` container runs before application containers and sets up iptables rules:

```yaml
initContainers:
  - name: istio-init
    image: proxyv2
    command: ["pilot-agent", "istio-iptables"]
    args:
      - "-p"
      - "15001"  # Outbound port
      - "-z"
      - "15006"  # Inbound port
      - "-u"
      - "1337"   # Proxy UID (exclude from redirect)
      - "-m"
      - "REDIRECT"
      - "-i"
      - "*"      # Capture all outbound traffic
      - "-b"
      - "*"      # Capture all inbound ports
    securityContext:
      capabilities:
        add:
          - NET_ADMIN  # Required for iptables
          - NET_RAW
```

**iptables rules created**:
- PREROUTING: Redirect inbound traffic to 15006
- OUTPUT: Redirect outbound traffic to 15001
- Exclude traffic from proxy UID (avoid loops)
- Exclude certain ports (Prometheus, health checks)

### Sidecar Container (istio-proxy)

The main proxy container:

```yaml
containers:
  - name: istio-proxy
    image: proxyv2
    args:
      - proxy
      - sidecar
      - --domain
      - $(POD_NAMESPACE).svc.cluster.local
      - --proxyLogLevel=warning
      - --proxyComponentLogLevel=misc:error
      - --log_output_level=default:info
    env:
      - name: JWT_POLICY
        value: third-party-jwt
      - name: PILOT_CERT_PROVIDER
        value: istiod
      - name: CA_ADDR
        value: istiod.istio-system.svc:15012
      - name: ISTIO_META_MESH_ID
        value: cluster.local
    resources:
      limits:
        cpu: 2000m
        memory: 1024Mi
      requests:
        cpu: 10m
        memory: 40Mi
    volumeMounts:
      - name: workload-socket
        mountPath: /var/run/secrets/workload-spiffe-uds
      - name: istiod-ca-cert
        mountPath: /var/run/secrets/istio
```

## Istio CNI Plugin

The CNI (Container Network Interface) plugin is an alternative to the init container approach.

### How CNI Plugin Works

Instead of using an init container with NET_ADMIN capability:

1. **Node-level installation** - CNI plugin binary installed on each node
2. **Kubelet integration** - Kubelet calls CNI plugin during pod setup
3. **Namespace network setup** - CNI plugin sets up pod network namespace
4. **iptables configuration** - Plugin configures iptables in pod namespace
5. **Pod starts** - Application and sidecar containers start with rules already in place

```
Without CNI:                          With CNI:
┌─────────────────┐                   ┌─────────────────┐
│  istio-init     │                   │                 │
│  (NET_ADMIN)    │                   │  No init needed │
│  sets iptables  │                   │                 │
└────────┬────────┘                   └─────────────────┘
         │
         ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│  istio-proxy    │                   │  istio-proxy    │
│  App container  │                   │  App container  │
└─────────────────┘                   └─────────────────┘
                                               ▲
                                               │
                                      ┌────────┴────────┐
                                      │  CNI plugin     │
                                      │  (node level)   │
                                      └─────────────────┘
```

### Security Benefits

**Reduced pod privileges**:
- No NET_ADMIN capability required in pod
- Follows principle of least privilege
- Reduces attack surface

**Cluster security policies**:
- Some clusters (OpenShift, GKE Autopilot) restrict privileged containers
- CNI plugin runs with node-level privileges (outside pod context)
- Pods can run with more restrictive security contexts

### Installation

```bash
# Install Istio with CNI enabled
istioctl install --set components.cni.enabled=true
```

This deploys:
- **istio-cni-node** DaemonSet - Installs CNI plugin on each node
- CNI configuration file - Tells Kubelet to invoke Istio CNI
- ServiceAccount with node-level permissions

## Proxy Ports Reference

| Port  | Name       | Protocol | Purpose                                      |
|-------|------------|----------|----------------------------------------------|
| 15000 | admin      | HTTP     | Envoy admin interface (localhost only)       |
| 15001 | outbound   | TCP      | Outbound traffic interception                |
| 15006 | inbound    | TCP      | Inbound traffic interception                 |
| 15008 | tunnel     | HTTP/2   | Secure tunnel to control plane (HBONE)       |
| 15009 | http-proxy | HTTP     | Explicit HTTP proxy (rarely used)            |
| 15020 | status     | HTTP     | Merged Prometheus + health                   |
| 15021 | health     | HTTP     | Health check endpoint                        |
| 15090 | prometheus | HTTP     | Envoy Prometheus metrics                     |

## Resource Annotations

Annotations control sidecar injection and proxy behavior.

### Injection Control

```yaml
metadata:
  annotations:
    # Disable injection for this pod
    sidecar.istio.io/inject: "false"

    # Custom injection template
    inject.istio.io/templates: "sidecar,custom-bootstrap"
```

### Proxy Configuration

```yaml
metadata:
  annotations:
    # Resource limits/requests
    sidecar.istio.io/proxyCPU: "100m"
    sidecar.istio.io/proxyCPULimit: "2000m"
    sidecar.istio.io/proxyMemory: "128Mi"
    sidecar.istio.io/proxyMemoryLimit: "1Gi"

    # Traffic control
    traffic.sidecar.istio.io/includeOutboundIPRanges: "10.0.0.0/8"
    traffic.sidecar.istio.io/excludeOutboundIPRanges: "169.254.169.254/32"
    traffic.sidecar.istio.io/includeInboundPorts: "80,443"
    traffic.sidecar.istio.io/excludeInboundPorts: "8080,8081"
    traffic.sidecar.istio.io/excludeOutboundPorts: "3306,6379"

    # Proxy image
    sidecar.istio.io/proxyImage: "gcr.io/istio-release/proxyv2:1.20.0"

    # Logging
    sidecar.istio.io/logLevel: "debug"
    sidecar.istio.io/componentLogLevel: "rbac:debug,jwt:debug"
```

### Readiness and Liveness

```yaml
metadata:
  annotations:
    # Wait for proxy ready before app starts
    proxy.istio.io/config: |
      holdApplicationUntilProxyStarts: true

    # Custom readiness probe
    sidecar.istio.io/rewriteAppHTTPProbers: "true"

    # Status port for health checks
    status.sidecar.istio.io/port: "15021"
```

### Status and Metadata

```yaml
metadata:
  annotations:
    # Istio version (set by injector)
    sidecar.istio.io/status: |
      {
        "initContainers": ["istio-init"],
        "containers": ["istio-proxy"],
        "volumes": ["workload-socket","credential-socket","workload-certs","istiod-ca-cert"]
      }

    # Prometheus scraping
    prometheus.io/scrape: "true"
    prometheus.io/port: "15020"
    prometheus.io/path: "/stats/prometheus"
```

### Network Configuration

```yaml
metadata:
  annotations:
    # Disable DNS proxying
    proxy.istio.io/config: |
      proxyMetadata:
        ISTIO_META_DNS_CAPTURE: "false"

    # Disable automatic protocol detection
    sidecar.istio.io/enableCoreDump: "true"

    # Custom stats tags
    sidecar.istio.io/statsInclusionPrefixes: "cluster.outbound,cluster_manager,listener_manager"
```

These annotations provide fine-grained control over sidecar injection and proxy behavior without modifying global mesh configuration.
