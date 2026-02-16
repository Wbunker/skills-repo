# Advanced Traffic Routing with Ingress

## Why Ingress

Without Ingress, exposing services externally requires individual LoadBalancer services, each provisioning a separate cloud load balancer. This is expensive and unmanageable at scale. Ingress consolidates external access through a single entry point that provides Layer 7 (HTTP/HTTPS) routing, TLS termination, name-based virtual hosting, and path-based routing. A single load balancer can route to dozens of backend services based on hostnames and URL paths.

The Ingress model separates concerns: the **Ingress resource** declares routing rules declaratively, while an **Ingress controller** (a reverse proxy running inside the cluster) implements them.

## Ingress Controllers

An Ingress resource does nothing without a controller watching for it. The controller is a pod running a reverse proxy that reads Ingress objects and configures itself accordingly.

### NGINX Ingress Controller

The most widely deployed controller. Install via Helm:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.replicaCount=2
```

This creates a Deployment, a LoadBalancer Service, and the necessary RBAC. The controller watches Ingress resources with `ingressClassName: nginx` and rebuilds its `nginx.conf` on every change.

### Traefik

Traefik offers a Kubernetes-native experience with its own CRDs. Install via Helm:

```bash
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik --namespace traefik --create-namespace
```

Traefik supports standard Ingress resources but also provides `IngressRoute` CRDs for advanced configuration that avoids annotation sprawl:

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: app-route
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`app.example.com`) && PathPrefix(`/api`)
      kind: Rule
      services:
        - name: api-service
          port: 80
      middlewares:
        - name: rate-limit
  tls:
    certResolver: letsencrypt
```

### Other Controllers

**HAProxy Ingress** -- High-performance option with fine-grained rate limiting and connection-level controls. Preferred in latency-sensitive environments.

**Contour** -- Uses Envoy as the data plane. Provides its own `HTTPProxy` CRD with support for traffic delegation across namespaces, enabling multi-team self-service routing.

**Ambassador/Emissary-Ingress** -- Envoy-based, API gateway focused. Configures via `Mapping` CRDs. Well suited for gRPC and WebSocket workloads.

### Cloud-Specific Controllers

**GKE Ingress** -- Default on GKE. Provisions Google Cloud HTTP(S) Load Balancers. Set `ingressClassName: gce`. Supports BackendConfig CRDs for health checks and CDN.

**AWS Load Balancer Controller** -- Provisions ALBs for Ingress and NLBs for LoadBalancer Services. Annotate with `alb.ingress.kubernetes.io/scheme: internet-facing`. Supports target-type `ip` for direct pod routing.

**Azure AGIC** -- Integrates with Azure Application Gateway. Supports WAF policies, autoscaling, and Azure-native TLS management.

## Ingress Resource Spec

### Basic Structure

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  defaultBackend:
    service:
      name: default-service
      port:
        number: 80
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls-secret
```

### Key Fields

**ingressClassName** -- Selects which controller handles this resource. Replaced the deprecated `kubernetes.io/ingress.class` annotation. Each controller registers an `IngressClass` object at install time.

**defaultBackend** -- Catches all requests that match no rule. Useful for custom 404 pages.

**rules** -- Each rule targets a hostname. Omitting `host` matches all hostnames. Each rule contains HTTP paths.

**pathType** values:

| Type | Behavior |
|---|---|
| `Exact` | Matches the URL path exactly. `/foo` does not match `/foo/`. |
| `Prefix` | Matches based on URL path prefix split by `/`. `/api` matches `/api`, `/api/`, and `/api/users`. |
| `ImplementationSpecific` | Matching depends on the controller. Avoid for portability. |

**tls** -- Associates hostnames with a Kubernetes Secret containing `tls.crt` and `tls.key`. The controller terminates TLS using these certificates.

## Path-Based Routing

Route different URL paths to different backend services behind a single hostname:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-routing
spec:
  ingressClassName: nginx
  rules:
    - host: store.example.com
      http:
        paths:
          - path: /products
            pathType: Prefix
            backend:
              service:
                name: product-service
                port:
                  number: 80
          - path: /cart
            pathType: Prefix
            backend:
              service:
                name: cart-service
                port:
                  number: 80
          - path: /checkout
            pathType: Exact
            backend:
              service:
                name: checkout-service
                port:
                  number: 443
```

Paths are evaluated longest-match-first. A request to `/products/123` matches the `/products` Prefix rule. A request to `/checkout` matches the Exact rule, but `/checkout/confirm` does not.

## Host-Based (Virtual Hosting) Routing

Route traffic by hostname, allowing multiple domains to share a single IP address:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: virtual-hosting
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
    - host: admin.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-dashboard
                port:
                  number: 3000
    - host: docs.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: docs-service
                port:
                  number: 80
```

The controller inspects the `Host` header to determine which rule applies. All three hostnames resolve to the same external IP (the controller's LoadBalancer).

## TLS Termination

### Creating TLS Secrets Manually

```bash
kubectl create secret tls app-tls-secret \
  --cert=tls.crt \
  --key=tls.key \
  --namespace=default
```

The Secret must contain exactly two keys: `tls.crt` (the full certificate chain, PEM-encoded) and `tls.key` (the private key, PEM-encoded). The Secret must exist in the same namespace as the Ingress.

### Automatic Certificates with cert-manager

cert-manager automates certificate issuance and renewal from Let's Encrypt and other ACME providers.

Install cert-manager:

```bash
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true
```

Create a ClusterIssuer for Let's Encrypt:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v2.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            ingressClassName: nginx
```

Then annotate the Ingress to trigger automatic certificate provisioning:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls-auto
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-service
                port:
                  number: 80
```

cert-manager creates a `Certificate` resource, completes the ACME HTTP-01 challenge by creating a temporary Ingress, stores the issued certificate in the `app-tls-auto` Secret, and renews it before expiry.

## Common NGINX Ingress Annotations

Annotations customize per-Ingress behavior in the NGINX controller. All use the `nginx.ingress.kubernetes.io/` prefix.

```yaml
metadata:
  annotations:
    # Rewrite the URL path before forwarding to the backend.
    # With path /api(/|$)(.*), rewrites to /$2 so /api/users -> /users
    nginx.ingress.kubernetes.io/rewrite-target: /$2

    # Force HTTPS redirect (enabled by default when TLS is configured)
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # Maximum allowed request body size (default 1m)
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"

    # Rate limiting: requests per second from a single IP
    nginx.ingress.kubernetes.io/limit-rps: "10"

    # Basic authentication
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth-secret
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"

    # Custom timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

    # CORS
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.example.com"
```

Create the basic auth secret from an htpasswd file:

```bash
htpasswd -c auth admin
kubectl create secret generic basic-auth-secret --from-file=auth
```

## Kubernetes Gateway API

The Gateway API is the successor to Ingress. It graduated to GA (v1.0) in October 2023 and addresses the limitations of Ingress: annotation sprawl, lack of standardized advanced features, and no role separation.

### Core Resources

**GatewayClass** -- Defines a class of Gateways, similar to IngressClass. Managed by infrastructure providers.

**Gateway** -- Requests a load balancer with specific listeners. Managed by cluster operators.

**HTTPRoute** -- Defines routing rules. Managed by application developers.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: production
spec:
  controllerName: gateway.nginx.org/nginx-gateway-controller
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: main-gateway
  namespace: infra
spec:
  gatewayClassName: production
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - name: wildcard-tls
      allowedRoutes:
        namespaces:
          from: All
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-routes
  namespace: app-team
spec:
  parentRefs:
    - name: main-gateway
      namespace: infra
  hostnames:
    - "app.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
          headers:
            - name: X-Api-Version
              value: v2
      backendRefs:
        - name: api-v2
          port: 8080
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-v1
          port: 8080
          weight: 90
        - name: api-v2
          port: 8080
          weight: 10
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: frontend
          port: 80
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            add:
              - name: X-Forwarded-Proto
                value: https
```

### Role-Oriented Design

The Gateway API separates concerns across organizational roles:

| Role | Resources | Responsibility |
|---|---|---|
| Infrastructure provider | GatewayClass | Defines available gateway implementations |
| Cluster operator | Gateway | Provisions load balancers, configures listeners and TLS |
| Application developer | HTTPRoute, GRPCRoute | Defines routing for their services |

This separation lets application teams manage their own routes without needing access to cluster-wide infrastructure configuration. A Gateway in one namespace can accept routes from other namespaces via `allowedRoutes`.

### Comparison with Ingress

| Feature | Ingress | Gateway API |
|---|---|---|
| Header-based routing | Annotation-dependent | Native `headers` matching |
| Traffic splitting | Not supported | Native `weight` on backendRefs |
| Request/response modification | Annotation-dependent | Native `filters` |
| Role separation | None | GatewayClass / Gateway / Route |
| Protocol support | HTTP/HTTPS only | HTTP, HTTPS, gRPC, TCP, TLS |
| Cross-namespace routing | Not supported | Native via parentRefs / allowedRoutes |

The Gateway API does not deprecate Ingress. Both coexist, and Ingress remains fully supported for simple use cases.

## Troubleshooting Ingress

### 404 Not Found

The request reached the controller but no rule matched.

```bash
# Check that the Ingress rules match the request hostname and path
kubectl get ingress app-ingress -o yaml

# Verify the Ingress is using the correct ingressClassName
kubectl get ingressclass

# Confirm the controller picked up the resource
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

Common causes: missing `host` that does not match the request's `Host` header, `Exact` pathType where `Prefix` was intended, DNS not pointing to the controller's external IP.

### 502 Bad Gateway

The controller received the request but could not reach the backend.

```bash
# Verify the backend service exists and has endpoints
kubectl get svc api-service
kubectl get endpoints api-service

# Check that pods are Running and passing readiness probes
kubectl get pods -l app=api-service

# Test connectivity from the controller pod
kubectl exec -n ingress-nginx deploy/ingress-nginx-controller -- \
  curl -s http://api-service.default.svc.cluster.local:8080/health
```

Common causes: service port mismatch (Ingress references port 80 but service listens on 8080), no ready endpoints, failing readiness probes, NetworkPolicy blocking traffic from the controller namespace.

### TLS Issues

```bash
# Verify the TLS secret exists and has the correct keys
kubectl get secret app-tls-secret -o jsonpath='{.data}' | jq 'keys'

# Decode and inspect the certificate
kubectl get secret app-tls-secret -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -subject -dates

# Check cert-manager certificate status
kubectl get certificate -A
kubectl describe certificate app-tls-auto
```

Common causes: Secret in the wrong namespace, certificate does not cover the requested hostname (SAN mismatch), expired certificate, cert-manager challenge failing due to DNS or firewall rules.

### General Debugging Steps

```bash
# View controller configuration (NGINX)
kubectl exec -n ingress-nginx deploy/ingress-nginx-controller -- \
  cat /etc/nginx/nginx.conf | grep -A 20 "server_name app.example.com"

# Watch Ingress events for errors
kubectl describe ingress app-ingress

# Check controller metrics endpoint for error rates
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller-metrics 10254
curl localhost:10254/metrics | grep nginx_ingress_controller_requests
```
