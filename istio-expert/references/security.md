# Securing Microservices with Istio

## Mutual TLS (mTLS)

Istio provides **automatic mutual TLS** between all mesh workloads. Each workload gets a cryptographic identity via SPIFFE certificates issued by istiod's built-in CA.

### How It Works

1. istiod watches for new service accounts in Kubernetes
2. When a workload starts, the Envoy sidecar requests a certificate from istiod via SDS (Secret Discovery Service)
3. istiod issues an X.509 certificate with a SPIFFE identity
4. Envoy uses the certificate for mTLS with other sidecars
5. Certificates rotate automatically (default: 24h lifetime)

### SPIFFE Identity

Every workload gets an identity in SPIFFE format:

```
spiffe://<trust-domain>/ns/<namespace>/sa/<service-account>
```

Example: `spiffe://cluster.local/ns/default/sa/reviews`

### Auto mTLS

By default, Istio uses **auto mTLS** — sidecars automatically use mTLS when both sides have sidecars, and fall back to plaintext when the destination has no sidecar. No configuration required.

### Migration Strategy: Permissive → Strict

1. **Start with PERMISSIVE** (default) — accepts both mTLS and plaintext
2. Monitor with Kiali/metrics to verify all traffic is mTLS
3. **Switch to STRICT** — reject any non-mTLS traffic

```yaml
# Step 1: Verify current state
# Check in Kiali or query:
# istio_requests_total{connection_security_policy="mutual_tls"}

# Step 2: Enable STRICT per namespace first
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: my-namespace
spec:
  mtls:
    mode: STRICT

# Step 3: Enable mesh-wide after validating all namespaces
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

## PeerAuthentication

Controls mTLS behavior at mesh, namespace, and workload levels.

### Modes

| Mode | Behavior |
|------|----------|
| `UNSET` | Inherits from parent (namespace → mesh) |
| `DISABLE` | No mTLS (plaintext only) |
| `PERMISSIVE` | Accepts both mTLS and plaintext |
| `STRICT` | Requires mTLS, rejects plaintext |

### Precedence Rules

Workload-level > Namespace-level > Mesh-level (istio-system)

### Workload-Level with Port Exception

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: db-policy
  namespace: database
spec:
  selector:
    matchLabels:
      app: mysql
  mtls:
    mode: STRICT
  portLevelMtls:
    3306:
      mode: PERMISSIVE   # allow non-mesh clients on this port
```

### Namespace-Level

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

## RequestAuthentication

Validates JSON Web Tokens (JWTs) on incoming requests.

```yaml
apiVersion: security.istio.io/v1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: frontend
  jwtRules:
  - issuer: "https://accounts.google.com"
    jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
    audiences:
    - "my-app.example.com"
    fromHeaders:
    - name: Authorization
      prefix: "Bearer "
    fromParams:
    - "access_token"
    forwardOriginalToken: true
    outputPayloadToHeader: "x-jwt-payload"
    outputClaimToHeaders:
    - header: "x-jwt-sub"
      claim: "sub"
    - header: "x-jwt-email"
      claim: "email"
```

### Multiple JWT Providers

```yaml
spec:
  jwtRules:
  - issuer: "https://accounts.google.com"
    jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
  - issuer: "https://auth.mycompany.com"
    jwksUri: "https://auth.mycompany.com/.well-known/jwks.json"
```

**Important**: `RequestAuthentication` only *validates* tokens present on requests. It does NOT *require* tokens. To require authentication, combine with `AuthorizationPolicy`.

### Requiring Authentication

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: require-jwt
  namespace: default
spec:
  selector:
    matchLabels:
      app: frontend
  action: DENY
  rules:
  - from:
    - source:
        notRequestPrincipals: ["*"]   # deny if no valid JWT principal
```

## AuthorizationPolicy

Fine-grained access control at L4 and L7.

### Actions

| Action | Behavior |
|--------|----------|
| `ALLOW` | Allow matching requests (default deny if any ALLOW exists) |
| `DENY` | Deny matching requests (evaluated before ALLOW) |
| `CUSTOM` | Delegate to external authorizer |
| `AUDIT` | Log matching requests (does not affect allow/deny) |

### Evaluation Order

1. **CUSTOM** policies evaluated first
2. **DENY** policies — if any match, request denied
3. **ALLOW** policies — if any exist, request must match at least one
4. If no policies at all, request allowed (default allow)

### Deny-All Baseline

```yaml
# Deny all traffic in namespace by default
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: production
spec: {}   # empty spec = deny all
```

### Allow Specific Traffic

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend-to-api
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-server
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/*"]
  - from:
    - source:
        namespaces: ["monitoring"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/healthz", "/metrics"]
```

### Source Fields

| Field | Description |
|-------|-------------|
| `principals` | SPIFFE identity of source (`cluster.local/ns/X/sa/Y`) |
| `notPrincipals` | Negative match |
| `namespaces` | Source namespace |
| `notNamespaces` | Negative match |
| `ipBlocks` | Source IP CIDR |
| `notIpBlocks` | Negative match |
| `remoteIpBlocks` | Original client IP (through proxies) |
| `requestPrincipals` | JWT principal (`iss/sub`) |
| `notRequestPrincipals` | Negative match |

### Operation Fields

| Field | Description |
|-------|-------------|
| `hosts` | Destination host |
| `ports` | Destination port |
| `methods` | HTTP method (GET, POST, etc.) |
| `paths` | URL path (supports `*` wildcard) |

### When Conditions

Match on any request attribute:

```yaml
rules:
- when:
  - key: request.headers[x-custom-header]
    values: ["allowed-value"]
  - key: source.ip
    notValues: ["10.0.0.0/8"]
```

Common keys: `request.headers[name]`, `source.ip`, `source.namespace`, `source.principal`, `request.auth.claims[name]`, `destination.port`.

### L4 Policy (TCP)

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: allow-tcp
spec:
  selector:
    matchLabels:
      app: database
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/backend/sa/api"]
    to:
    - operation:
        ports: ["5432"]
```

### Custom External Authorization

```yaml
# First, define the ext_authz provider in meshConfig:
# extensionProviders:
# - name: "my-ext-authz"
#   envoyExtAuthzGrpc:
#     service: "ext-authz.auth.svc.cluster.local"
#     port: 9000

apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: ext-authz
spec:
  selector:
    matchLabels:
      app: frontend
  action: CUSTOM
  provider:
    name: my-ext-authz
  rules:
  - to:
    - operation:
        paths: ["/admin/*"]
```

## Certificate Management

### Default Istio CA

istiod acts as the CA, using a self-signed root certificate. Certificates are delivered to Envoy via SDS.

### Custom CA Integration

**Using cert-manager as Istio CA:**

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: istio-ca
  namespace: istio-system
spec:
  ca:
    secretName: istio-ca-secret
```

**Plugging in an intermediate CA:**

```bash
# Create secret with custom CA cert chain
kubectl create secret generic cacerts -n istio-system \
  --from-file=ca-cert.pem \
  --from-file=ca-key.pem \
  --from-file=root-cert.pem \
  --from-file=cert-chain.pem
```

istiod detects the `cacerts` secret and uses it as the signing CA.

### Certificate Rotation

- Default certificate lifetime: 24 hours
- Rotation happens automatically at ~50% of lifetime
- Configurable via `pilot` environment variables or mesh config

```yaml
meshConfig:
  defaultConfig:
    proxyMetadata:
      SECRET_TTL: "12h"  # certificate lifetime
```

### Trust Domain

```yaml
meshConfig:
  trustDomain: "my-company.com"
  trustDomainAliases:
  - "old-domain.com"     # accept certs from old domain during migration
  - "cluster-2.my.com"   # cross-cluster trust
```

## Zero-Trust Security Patterns

### Defense in Depth

```yaml
# 1. Enforce mTLS mesh-wide
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
---
# 2. Deny-all baseline per sensitive namespace
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: sensitive-ns
spec: {}
---
# 3. Selective allow rules
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: allow-specific
  namespace: sensitive-ns
spec:
  selector:
    matchLabels:
      app: payment
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/checkout/sa/checkout-svc"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charge"]
```

## Egress Security

### Controlling External Traffic

```yaml
# Register external service
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  ports:
  - number: 443
    name: https
    protocol: TLS
  resolution: DNS
  location: MESH_EXTERNAL
---
# Route through egress gateway
apiVersion: networking.istio.io/v1
kind: Gateway
metadata:
  name: egress-gateway
spec:
  selector:
    istio: egressgateway
  servers:
  - port:
      number: 443
      name: tls
      protocol: TLS
    hosts:
    - api.external.com
    tls:
      mode: PASSTHROUGH
---
# VirtualService to route via egress gateway
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: external-api-via-egress
spec:
  hosts:
  - api.external.com
  gateways:
  - mesh
  - egress-gateway
  tls:
  - match:
    - gateways: [mesh]
      port: 443
      sniHosts: [api.external.com]
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        port:
          number: 443
  - match:
    - gateways: [egress-gateway]
      port: 443
      sniHosts: [api.external.com]
    route:
    - destination:
        host: api.external.com
        port:
          number: 443
```

### TLS Origination

For services that only speak HTTP internally but need HTTPS externally:

```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: external-api-tls
spec:
  host: api.external.com
  trafficPolicy:
    tls:
      mode: SIMPLE   # Envoy originates TLS to external service
```

### Deny All Egress (Registry Only)

```yaml
meshConfig:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY   # only allow traffic to services in the registry
```

With this setting, all external access must be explicitly registered via `ServiceEntry`.

## Security Debugging

```bash
# Check mTLS status between services
istioctl x authz check <pod-name>

# View certificate info
istioctl proxy-config secret <pod-name>

# Check if peer authentication is applied
istioctl x describe pod <pod-name>

# Debug authorization policies
istioctl proxy-config log <pod-name> --level rbac:debug
kubectl logs <pod-name> -c istio-proxy | grep "rbac"
```

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Connection refused between services | STRICT mTLS with missing sidecar | Ensure both pods have sidecars or use PERMISSIVE |
| 403 Forbidden | AuthorizationPolicy denying | Check `istioctl x authz check`, verify principal names |
| JWT validation fails | Wrong issuer/audience/JWKS URL | Verify JWT claims match RequestAuthentication config |
| mTLS handshake failure | Trust domain mismatch | Check trust domain config, add aliases if migrating |
| Intermittent 503s after enabling STRICT | Some pods missing sidecars | Check all communicating pods have injection enabled |
