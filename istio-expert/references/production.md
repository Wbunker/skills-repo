# Deploying Istio in Production

This reference covers production deployment strategies, installation methods, upgrade approaches, performance tuning, and high availability configurations for Istio service mesh based on Chapter 8 of Practical Istio.

## Installation Methods

Istio provides multiple installation methods, each suited for different operational requirements.

### istioctl install

The primary CLI-based installation method. Provides interactive validation and direct cluster manipulation.

```bash
# Install with default profile
istioctl install --set profile=production

# Install with custom configuration
istioctl install --set profile=default \
  --set values.global.proxy.resources.requests.cpu=100m \
  --set values.global.proxy.resources.requests.memory=128Mi

# Install with IstioOperator manifest
istioctl install -f istiooperator.yaml

# Verify installation
istioctl verify-install

# Show differences before applying
istioctl install --dry-run -f istiooperator.yaml
```

**Advantages**: Built-in validation, profile support, generates full manifests, simple rollback.

**Use when**: Manual operations are acceptable, need validation before apply, prefer declarative configuration.

### Helm Charts

GitOps-friendly installation using Helm charts. Separates base components from istiod deployment.

```bash
# Add Istio Helm repository
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# Install base components (CRDs, cluster roles)
helm install istio-base istio/base -n istio-system --create-namespace

# Install istiod control plane
helm install istiod istio/istiod -n istio-system \
  --set global.proxy.resources.requests.cpu=100m \
  --set global.proxy.resources.requests.memory=128Mi

# Install ingress gateway
helm install istio-ingress istio/gateway -n istio-ingress --create-namespace
```

**Advantages**: Native GitOps integration (ArgoCD, Flux), version control, templating, rollback via Helm.

**Use when**: GitOps workflow required, need template flexibility, managing multiple environments.

### IstioOperator CRD

Kubernetes-native operator pattern. Deploy operator, then manage via IstioOperator custom resources.

```bash
# Install operator
istioctl operator init

# Apply IstioOperator resource
kubectl apply -f - <<EOF
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: production-config
  namespace: istio-system
spec:
  profile: default
  components:
    pilot:
      k8s:
        replicaCount: 3
EOF

# Operator reconciles to desired state
```

**Advantages**: Continuous reconciliation, self-healing, Kubernetes-native, day-2 operations.

**Use when**: Want automatic drift correction, prefer operator pattern, need continuous enforcement.

### Comparison Matrix

| Method | GitOps | Reconciliation | Complexity | Rollback |
|--------|--------|----------------|------------|----------|
| istioctl | Manual | One-time | Low | Manual |
| Helm | Native | Via operator | Medium | helm rollback |
| Operator | Native | Continuous | Medium | Edit CR |

**Production recommendation**: Use Helm for GitOps environments or istioctl with IstioOperator manifests for declarative configuration. Avoid operator unless continuous reconciliation is required.

## IstioOperator Configuration

The IstioOperator CRD provides fine-grained control over Istio installation.

### Core Structure

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: production-install
  namespace: istio-system
spec:
  # Installation profile (base configuration)
  profile: default

  # Istio mesh-wide configuration
  meshConfig:
    accessLogFile: /dev/stdout
    defaultConfig:
      tracing:
        sampling: 1.0
      holdApplicationUntilProxyStarts: true
    enableTracing: true

  # Component-level configuration
  components:
    pilot:
      enabled: true
      k8s:
        replicaCount: 3
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
        env:
        - name: PILOT_TRACE_SAMPLING
          value: "1.0"

    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        replicaCount: 3
        service:
          type: LoadBalancer

    egressGateways:
    - name: istio-egressgateway
      enabled: false

    cni:
      enabled: false

  # Values overlay (Helm values passthrough)
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2000m
            memory: 1024Mi
        logLevel: warning
      tracer:
        zipkin:
          address: zipkin.istio-system:9411
```

### Component Configuration

#### Pilot (istiod)

Control plane component responsible for configuration distribution and certificate management.

```yaml
components:
  pilot:
    enabled: true
    k8s:
      replicaCount: 3
      resources:
        requests:
          cpu: 500m
          memory: 2Gi
        limits:
          cpu: 2000m
          memory: 4Gi
      hpaSpec:
        minReplicas: 3
        maxReplicas: 10
        metrics:
        - type: Resource
          resource:
            name: cpu
            targetAverageUtilization: 80
      podDisruptionBudget:
        minAvailable: 2
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: istiod
            topologyKey: kubernetes.io/hostname
      env:
      - name: PILOT_ENABLE_WORKLOAD_ENTRY_AUTOREGISTRATION
        value: "true"
      - name: PILOT_ENABLE_WORKLOAD_ENTRY_HEALTHCHECKS
        value: "true"
```

#### Ingress Gateways

```yaml
components:
  ingressGateways:
  - name: istio-ingressgateway
    enabled: true
    k8s:
      replicaCount: 3
      resources:
        requests:
          cpu: 500m
          memory: 256Mi
        limits:
          cpu: 2000m
          memory: 1024Mi
      service:
        type: LoadBalancer
        ports:
        - port: 80
          targetPort: 8080
          name: http2
        - port: 443
          targetPort: 8443
          name: https
        - port: 15021
          targetPort: 15021
          name: status-port
      podDisruptionBudget:
        minAvailable: 2
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: istio-ingressgateway
              topologyKey: topology.kubernetes.io/zone
```

#### CNI Plugin

Required for OpenShift or when pods lack NET_ADMIN capability.

```yaml
components:
  cni:
    enabled: true
    namespace: kube-system
    k8s:
      tolerations:
      - operator: Exists
```

### MeshConfig Options

```yaml
meshConfig:
  # Access logging
  accessLogFile: /dev/stdout
  accessLogFormat: |
    [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%"
    %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION%
    "%REQ(X-FORWARDED-FOR)%" "%REQ(USER-AGENT)%" "%REQ(X-REQUEST-ID)%"

  # Default proxy configuration
  defaultConfig:
    holdApplicationUntilProxyStarts: true
    proxyMetadata:
      ISTIO_META_DNS_CAPTURE: "true"
      ISTIO_META_DNS_AUTO_ALLOCATE: "true"
    concurrency: 2
    discoveryAddress: istiod.istio-system.svc:15012
    tracing:
      sampling: 1.0
      zipkin:
        address: zipkin.istio-system:9411

  # Traffic management
  enableTracing: true
  enablePrometheusMerge: true
  defaultProviders:
    metrics:
    - prometheus
    tracing:
    - zipkin

  # mTLS settings
  enableAutoMtls: true

  # Service discovery
  serviceSettings:
  - settings:
      clusterLocal: false
    hosts:
    - "*.svc.cluster.local"

  # Certificate configuration
  certificates:
  - secretName: dns.example.com-certs
    dnsNames:
    - example.com
    - "*.example.com"
```

### Values Overlay

The `values` field passes through to Helm chart values for additional customization.

```yaml
values:
  global:
    istioNamespace: istio-system
    proxy:
      autoInject: enabled
      clusterDomain: cluster.local
      componentLogLevel: misc:error
      logLevel: warning
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 2000m
          memory: 1024Mi
      holdApplicationUntilProxyStarts: true
      lifecycle:
        preStop:
          exec:
            command:
            - sh
            - -c
            - sleep 15
    proxy_init:
      resources:
        requests:
          cpu: 10m
          memory: 10Mi
        limits:
          cpu: 100m
          memory: 50Mi
  pilot:
    autoscaleEnabled: true
    autoscaleMin: 3
    autoscaleMax: 10
    cpu:
      targetAverageUtilization: 80
    traceSampling: 1.0
  gateways:
    istio-ingressgateway:
      autoscaleEnabled: true
      autoscaleMin: 3
      autoscaleMax: 10
```

## Installation Profiles

Istio provides built-in profiles for different deployment scenarios.

### Profile Comparison

| Component | default | demo | minimal | remote | empty | ambient |
|-----------|---------|------|---------|--------|-------|---------|
| istiod | X | X | X | | | X |
| Ingress Gateway | X | X | | | | X |
| Egress Gateway | | X | | | | |
| CNI | | | | | | X |
| Ztunnel | | | | | | X |

### Default Profile

Production-ready baseline with single control plane and ingress gateway.

```bash
istioctl install --set profile=default

# Components: istiod (1 replica), istio-ingressgateway (1 replica)
# Resource limits: Moderate
# Features: mTLS enabled, telemetry enabled
```

### Demo Profile

Development and demonstration with all features enabled. Not for production.

```bash
istioctl install --set profile=demo

# Components: istiod, ingress gateway, egress gateway
# Resource limits: Low
# Features: All enabled, high tracing rate (100%)
# WARNING: No HA, minimal resources, insecure defaults
```

### Minimal Profile

Only control plane, no gateways. For environments with external ingress.

```bash
istioctl install --set profile=minimal

# Components: istiod only
# Use when: Bringing your own ingress controller
```

### Remote Profile

For multi-cluster remote clusters sharing control plane from primary cluster.

```bash
istioctl install --set profile=remote \
  --set values.global.remotePilotAddress=istiod.istio-system.svc.cluster.local

# Components: None (connects to remote istiod)
# Use when: Primary-remote multi-cluster topology
```

### Empty Profile

Base for custom configurations. No components installed by default.

```bash
istioctl install --set profile=empty -f custom-components.yaml
```

### Ambient Profile

For ambient mesh mode using ztunnel (sidecar-less data plane).

```bash
istioctl install --set profile=ambient

# Components: istiod, CNI, ztunnel (DaemonSet), ingress gateway
# Use when: Deploying ambient mesh instead of sidecar mode
```

### Production Profile Recommendations

```yaml
# Recommended production profile customization
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: production
spec:
  profile: default
  components:
    pilot:
      k8s:
        replicaCount: 3
        hpaSpec:
          minReplicas: 3
          maxReplicas: 10
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        podDisruptionBudget:
          minAvailable: 2
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        replicaCount: 3
        hpaSpec:
          minReplicas: 3
          maxReplicas: 10
        podDisruptionBudget:
          minAvailable: 2
  meshConfig:
    accessLogFile: /dev/stdout
    defaultConfig:
      holdApplicationUntilProxyStarts: true
      tracing:
        sampling: 1.0  # Reduce to 0.01 (1%) in production
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2000m
            memory: 1024Mi
```

## Revision-Based Upgrades (Canary)

Revision-based upgrades enable zero-downtime canary upgrades by running multiple control plane versions simultaneously.

### Installing Multiple Revisions

```bash
# Install stable revision
istioctl install --set revision=stable --set profile=default

# Install canary revision (new version)
istioctl install --set revision=canary --set profile=default

# List installed revisions
kubectl get mutatingwebhookconfigurations -l 'app=sidecar-injector'
```

### Revision Labels and Namespace Migration

Control which control plane version manages namespace by labeling namespaces.

```bash
# Label namespace for stable revision
kubectl label namespace production istio.io/rev=stable

# Remove default injection label (if present)
kubectl label namespace production istio-injection-

# Restart pods to use stable revision
kubectl rollout restart deployment -n production

# Verify pods use stable revision
kubectl get pods -n production -o jsonpath='{.items[*].metadata.labels.istio\.io/rev}'

# Migrate to canary revision
kubectl label namespace production istio.io/rev=canary --overwrite
kubectl rollout restart deployment -n production

# Verify canary proxy version
istioctl proxy-status
```

### Gradual Migration Strategy

```bash
# Phase 1: Install canary revision
istioctl install --set revision=canary-1-20 --set profile=default

# Phase 2: Migrate test namespaces
kubectl label namespace test istio.io/rev=canary-1-20
kubectl rollout restart deployment -n test

# Validate for 24-48 hours, monitor metrics

# Phase 3: Migrate staging namespaces
kubectl label namespace staging istio.io/rev=canary-1-20
kubectl rollout restart deployment -n staging

# Validate for 48 hours

# Phase 4: Migrate production namespaces (gradually)
for ns in prod-service-a prod-service-b prod-service-c; do
  kubectl label namespace $ns istio.io/rev=canary-1-20 --overwrite
  kubectl rollout restart deployment -n $ns
  # Wait and validate before next namespace
  sleep 3600
done

# Phase 5: Make canary the new stable
kubectl label namespace prod-service-a istio.io/rev=stable --overwrite
# Re-install canary as stable revision
istioctl install --set revision=stable --set profile=default

# Phase 6: Remove old revision (after all namespaces migrated)
istioctl uninstall --revision=1-19 --purge
```

### Rollback Procedure

```bash
# If issues detected, rollback to previous revision
kubectl label namespace production istio.io/rev=stable --overwrite
kubectl rollout restart deployment -n production

# Remove problematic canary revision
istioctl uninstall --revision=canary-1-20 --purge
```

### Tag-Based Revision Management

```bash
# Create revision tag for easier management
istioctl tag set prod-stable --revision stable
istioctl tag set prod-canary --revision canary-1-20

# Use tags in namespace labels
kubectl label namespace production istio.io/rev=prod-stable

# Update tag to point to new revision (no namespace relabeling needed)
istioctl tag set prod-stable --revision canary-1-20 --overwrite

# List tags
istioctl tag list
```

## Multi-Cluster Deployment

Istio supports multiple topologies for spanning service mesh across clusters.

### Topology Types

#### Multi-Primary (Single Network)

All clusters have their own control plane and share the same network (pod-to-pod connectivity).

```bash
# Cluster 1
kubectl config use-context cluster1
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1 \
  --set values.global.network=network1

# Cluster 2
kubectl config use-context cluster2
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster2 \
  --set values.global.network=network1

# Install cross-cluster secrets for endpoint discovery
istioctl create-remote-secret --context=cluster1 --name=cluster1 | \
  kubectl apply -f - --context=cluster2

istioctl create-remote-secret --context=cluster2 --name=cluster2 | \
  kubectl apply -f - --context=cluster1
```

#### Primary-Remote

Primary cluster has control plane, remote clusters use remote control plane.

```bash
# Primary cluster
kubectl config use-context cluster1
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1 \
  --set values.global.network=network1

# Create remote secret for primary
istioctl create-remote-secret --context=cluster1 --name=cluster1 | \
  kubectl apply -f - --context=cluster1

# Remote cluster
kubectl config use-context cluster2
istioctl install --set profile=remote \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster2 \
  --set values.global.network=network1 \
  --set values.global.remotePilotAddress=istiod.istio-system.svc.cluster.local

# Create remote secret for primary to discover remote endpoints
istioctl create-remote-secret --context=cluster2 --name=cluster2 | \
  kubectl apply -f - --context=cluster1
```

#### Multi-Network

Clusters on different networks require east-west gateway for cross-cluster traffic.

```bash
# Cluster 1 (network1)
kubectl config use-context cluster1
istioctl install --set profile=default \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1 \
  --set values.global.network=network1

# Install east-west gateway
kubectl apply -f - <<EOF
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: eastwest
spec:
  profile: empty
  components:
    ingressGateways:
    - name: istio-eastwestgateway
      label:
        istio: eastwestgateway
        app: istio-eastwestgateway
        topology.istio.io/network: network1
      enabled: true
      k8s:
        env:
        - name: ISTIO_META_REQUESTED_NETWORK_VIEW
          value: network1
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
EOF

# Expose services via east-west gateway
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: cross-network-gateway
  namespace: istio-system
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
EOF

# Repeat for cluster 2 with network=network2
```

### Cross-Cluster Trust (Shared Root CA)

```bash
# Generate intermediate certificates from common root
# Cluster 1
kubectl create namespace istio-system --context=cluster1
kubectl create secret generic cacerts -n istio-system \
  --from-file=ca-cert.pem \
  --from-file=ca-key.pem \
  --from-file=root-cert.pem \
  --from-file=cert-chain.pem \
  --context=cluster1

# Cluster 2 (same root)
kubectl create namespace istio-system --context=cluster2
kubectl create secret generic cacerts -n istio-system \
  --from-file=ca-cert.pem \
  --from-file=ca-key.pem \
  --from-file=root-cert.pem \
  --from-file=cert-chain.pem \
  --context=cluster2
```

## Performance Tuning

### Proxy Resource Management

```yaml
# Global proxy defaults
values:
  global:
    proxy:
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 2000m
          memory: 1024Mi
      concurrency: 2  # Envoy worker threads (default: 2, 0 = auto)

# Per-pod annotation override
metadata:
  annotations:
    sidecar.istio.io/proxyCPU: "200m"
    sidecar.istio.io/proxyMemory: "256Mi"
    sidecar.istio.io/proxyCPULimit: "1000m"
    sidecar.istio.io/proxyMemoryLimit: "512Mi"
```

### Reduce Tracing Sampling Rate

```yaml
meshConfig:
  defaultConfig:
    tracing:
      sampling: 1.0  # 1% sampling in production (100.0 for dev)
  enableTracing: true
```

### Sidecar CRD for Configuration Scoping

Reduce proxy configuration size by limiting egress hosts.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: production
spec:
  egress:
  - hosts:
    - "./*"  # Same namespace
    - "istio-system/*"  # Istio components
    - "logging/*"  # Logging services
    - "monitoring/*"  # Monitoring services
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY  # Only allow mesh services, block external
```

### Disable Unused Features

```yaml
meshConfig:
  # Disable access logging in production
  accessLogFile: ""

  # Disable protocol sniffing (if protocols are explicit)
  protocolDetectionTimeout: 0s

  defaultConfig:
    # Reduce stats for memory savings
    proxyStatsMatcher:
      inclusionRegexps:
      - "cluster\\..*\\.upstream_rq_total"
      - "cluster\\..*\\.upstream_rq_time"
      exclusionRegexps:
      - "cluster\\..*\\.internal\\..*"
```

### Envoy Stats Trimming

```yaml
# Annotation to control stats
metadata:
  annotations:
    sidecar.istio.io/statsInclusionPrefixes: "cluster.outbound,cluster_manager,listener_manager,http_mixer_filter,tcp_mixer_filter,server,cluster.xds-grpc"
    sidecar.istio.io/statsInclusionSuffixes: "upstream_rq_1xx,upstream_rq_2xx,upstream_rq_3xx,upstream_rq_4xx,upstream_rq_5xx"
```

## Scaling istiod

### Horizontal Pod Autoscaler

```yaml
components:
  pilot:
    k8s:
      hpaSpec:
        minReplicas: 3
        maxReplicas: 10
        metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 80
        - type: Resource
          resource:
            name: memory
            target:
              type: Utilization
              averageUtilization: 80
        behavior:
          scaleDown:
            stabilizationWindowSeconds: 300
            policies:
            - type: Percent
              value: 50
              periodSeconds: 60
```

### Resource Requirements by Cluster Size

| Cluster Size | istiod CPU | istiod Memory | Min Replicas |
|--------------|------------|---------------|--------------|
| < 50 pods | 500m | 2Gi | 2 |
| 50-500 pods | 1000m | 2Gi | 3 |
| 500-2000 pods | 2000m | 4Gi | 3 |
| 2000+ pods | 4000m | 8Gi | 5 |

### XDS Push Throttling

```yaml
components:
  pilot:
    k8s:
      env:
      - name: PILOT_PUSH_THROTTLE
        value: "100"  # Max pushes/second
      - name: PILOT_MAX_REQUESTS_PER_SECOND
        value: "25"  # Rate limit for XDS requests
      - name: PILOT_DEBOUNCE_AFTER
        value: "100ms"  # Debounce config updates
      - name: PILOT_DEBOUNCE_MAX
        value: "10s"  # Max debounce delay
```

## Resource Management

### Global Proxy Defaults

```yaml
values:
  global:
    proxy:
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 2000m
          memory: 1024Mi
      lifecycle:
        preStop:
          exec:
            command:
            - sh
            - -c
            - sleep 15  # Allow time for endpoint removal propagation
    proxy_init:
      resources:
        requests:
          cpu: 10m
          memory: 10Mi
        limits:
          cpu: 100m
          memory: 50Mi
```

### Per-Pod Resource Overrides

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  annotations:
    # Sidecar resources
    sidecar.istio.io/proxyCPU: "200m"
    sidecar.istio.io/proxyMemory: "256Mi"
    sidecar.istio.io/proxyCPULimit: "1000m"
    sidecar.istio.io/proxyMemoryLimit: "512Mi"

    # Init container resources
    sidecar.istio.io/proxyCPUInit: "50m"
    sidecar.istio.io/proxyMemoryInit: "50Mi"
spec:
  containers:
  - name: myapp
    image: myapp:latest
```

## High Availability

### istiod High Availability

```yaml
components:
  pilot:
    k8s:
      replicaCount: 3  # Minimum for HA
      podDisruptionBudget:
        minAvailable: 2  # Ensure 2 replicas during disruptions
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: istiod
            topologyKey: kubernetes.io/hostname
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: istiod
              topologyKey: topology.kubernetes.io/zone
      resources:
        requests:
          cpu: 500m
          memory: 2Gi
        limits:
          cpu: 2000m
          memory: 4Gi
```

### Ingress Gateway High Availability

```yaml
components:
  ingressGateways:
  - name: istio-ingressgateway
    enabled: true
    k8s:
      replicaCount: 3
      hpaSpec:
        minReplicas: 3
        maxReplicas: 10
        metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 80
      podDisruptionBudget:
        minAvailable: 2
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: istio-ingressgateway
              topologyKey: topology.kubernetes.io/zone
      service:
        type: LoadBalancer
        externalTrafficPolicy: Local  # Preserve source IP
```

### Multi-Zone Deployment

```yaml
components:
  pilot:
    k8s:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: istiod
            topologyKey: kubernetes.io/hostname
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: istiod
              topologyKey: topology.kubernetes.io/zone
```

### Graceful Shutdown

```yaml
meshConfig:
  defaultConfig:
    terminationDrainDuration: 30s  # Drain connections before shutdown

values:
  global:
    proxy:
      lifecycle:
        preStop:
          exec:
            command:
            - sh
            - -c
            - sleep 15  # Wait for endpoint removal propagation
```

## Upgrade Strategies

### Pre-Upgrade Checks

```bash
# Verify current installation health
istioctl verify-install

# Check for upgrade compatibility
istioctl x precheck

# Review deprecated APIs
istioctl analyze --all-namespaces

# Check proxy versions
istioctl proxy-status

# Generate upgrade diff
istioctl install --dry-run --set revision=1-20-0 | kubectl diff -f -
```

### In-Place Upgrade

Direct upgrade of control plane. Causes brief control plane unavailability but data plane continues.

```bash
# Backup current configuration
kubectl get iop -n istio-system -o yaml > istio-config-backup.yaml

# Upgrade istioctl binary
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -

# Perform upgrade
istioctl upgrade

# Verify upgrade
istioctl version
kubectl get pods -n istio-system

# Rolling restart data plane (proxies)
kubectl rollout restart deployment -n production
```

**Downtime**: Brief control plane API unavailability (xDS). Data plane unaffected.

**Use when**: Non-production, small clusters, acceptable brief control plane disruption.

### Canary Upgrade (Recommended)

Install new control plane revision alongside existing, gradually migrate namespaces.

```bash
# Install canary revision
istioctl install --set revision=1-20-0 --set profile=default

# Verify both revisions running
kubectl get pods -n istio-system -l app=istiod

# Migrate test namespace
kubectl label namespace test istio.io/rev=1-20-0 --overwrite
kubectl rollout restart deployment -n test

# Validate test workloads for 24-48 hours
istioctl proxy-status
kubectl logs -n test <pod> -c istio-proxy

# Gradually migrate production namespaces
kubectl label namespace prod-a istio.io/rev=1-20-0 --overwrite
kubectl rollout restart deployment -n prod-a
# Wait, monitor, validate

kubectl label namespace prod-b istio.io/rev=1-20-0 --overwrite
kubectl rollout restart deployment -n prod-b
# Wait, monitor, validate

# After all namespaces migrated, remove old revision
istioctl uninstall --revision=1-19-0 --purge
```

**Downtime**: Zero (blue-green control plane).

**Use when**: Production, large clusters, need rollback capability.

### Blue-Green Control Plane

Similar to canary but with full environment swap.

```bash
# Install green revision
istioctl install --set revision=green --set profile=default

# Migrate all namespaces at once (during maintenance window)
for ns in $(kubectl get ns -l istio-injection=enabled -o jsonpath='{.items[*].metadata.name}'); do
  kubectl label namespace $ns istio.io/rev=green --overwrite
  kubectl label namespace $ns istio-injection-
done

# Rolling restart all
kubectl rollout restart deployment --all-namespaces

# Validate, then remove blue
istioctl uninstall --revision=blue --purge
```

### Data Plane Rolling Restart

After control plane upgrade, proxies need restart to use new version.

```bash
# Restart specific namespace
kubectl rollout restart deployment -n production

# Restart all deployments in mesh
for ns in $(kubectl get ns -l istio-injection=enabled -o jsonpath='{.items[*].metadata.name}'); do
  kubectl rollout restart deployment -n $ns
done

# Verify proxy versions match control plane
istioctl proxy-status

# Check for outdated proxies
istioctl proxy-status | grep -v "Synced"
```

### Rollback Procedure

```bash
# If canary upgrade fails, rollback namespace labels
kubectl label namespace production istio.io/rev=1-19-0 --overwrite
kubectl rollout restart deployment -n production

# Remove failed canary revision
istioctl uninstall --revision=1-20-0 --purge

# If in-place upgrade fails, restore from backup
kubectl apply -f istio-config-backup.yaml
```

### Upgrade Best Practices

1. Always test in non-production first
2. Review release notes for breaking changes
3. Run pre-upgrade checks
4. Use canary upgrades for production
5. Monitor metrics during migration
6. Keep old revision running until validation complete
7. Document rollback procedure
8. Automate proxy restarts with gradual rollout
9. Maintain minimum 2 istiod replicas during upgrade
10. Schedule upgrades during low-traffic windows
