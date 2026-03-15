# Cloud Load Balancing — Capabilities Reference

## Purpose

Cloud Load Balancing is a fully managed, software-defined load balancing service that distributes traffic across backend instances globally or regionally. It provides automatic scaling, health checking, SSL termination, content-based routing, and integration with Cloud CDN, Cloud Armor, and IAP. There is no pre-warming required — load balancers handle sudden traffic spikes instantly.

---

## Load Balancer Types

| Load Balancer | Scope | Protocol | Backend Types | Use Case |
|---|---|---|---|---|
| **Global external Application LB** | Global | HTTP/HTTPS/HTTP2 | MIG, GKE, Cloud Run, App Engine, NEGs | Internet-facing web apps and APIs needing global anycast IP and multi-region failover |
| **Regional external Application LB** | Regional | HTTP/HTTPS | MIG, GKE, NEGs | Internet-facing web apps constrained to a single region |
| **Classic Application LB** (legacy) | Global | HTTP/HTTPS | MIG, GKE, NEGs | Legacy global LB; prefer Global external Application LB for new deployments |
| **Regional internal Application LB** | Regional | HTTP/HTTPS | MIG, GKE, NEGs | Internal microservices, internal APIs within a VPC |
| **Cross-region internal Application LB** | Global | HTTP/HTTPS | MIG, GKE, NEGs | Internal services that span multiple regions (active-active) |
| **External proxy Network LB** | Regional | SSL/TLS, TCP | MIG, NEGs | Non-HTTP TLS or TCP termination at regional level |
| **External pass-through Network LB** | Regional | TCP, UDP | MIG | High-performance TCP/UDP; passes traffic directly to backends (no proxy); supports preserve client IP |
| **Internal pass-through Network LB** | Regional | TCP, UDP | MIG | Internal TCP/UDP services (e.g., internal NFS, gRPC without HTTP, internal database proxy) |
| **Internal proxy Network LB** | Regional | TCP | MIG, NEGs | Internal SSL/TLS termination |

**Key distinction**:
- **Proxy-based**: LB terminates the connection; establishes new connection to backend. Supports SSL termination, URL routing, health checking at HTTP layer. Client IP requires `X-Forwarded-For` header.
- **Pass-through**: Traffic forwarded directly; backend sees client's original IP. Backend handles the full TCP/UDP connection.

---

## Core Components

### Backend Service

A backend service defines where to send traffic and how to handle it:
- **Backends**: one or more backend groups (MIGs, NEGs) with balancing mode (RATE or UTILIZATION) and capacity scaler
- **Health check**: which health check to use for this backend service
- **Protocol**: how to communicate with backends (HTTP, HTTPS, HTTP/2, gRPC, TCP, SSL)
- **Session affinity**: none, client IP, generated cookie, header, HTTP cookie
- **Timeout**: how long to wait for a backend response before returning an error
- **Logging**: request logging to Cloud Logging
- **Cloud CDN**: enable CDN caching for static assets
- **Cloud Armor**: attach a security policy for WAF/DDoS

### Backend Bucket

An alternative to backend service that serves content from a Cloud Storage bucket:
- Used for static website hosting
- Integrates with Cloud CDN for caching
- URL map routes specific paths to a backend bucket

### Health Checks

Health checks determine whether backends should receive traffic:

| Protocol | Description |
|---|---|
| HTTP | GET request to a path; expects 2xx response |
| HTTPS | Same as HTTP but over TLS |
| HTTP/2 | HTTP/2 health check |
| TCP | TCP connection established successfully |
| SSL | SSL handshake successful |
| gRPC | gRPC health check protocol |

**Key properties**:
- `check-interval`: seconds between probes (default 10s)
- `timeout`: seconds to wait for response (default 10s)
- `healthy-threshold`: consecutive successes before marking healthy (default 2)
- `unhealthy-threshold`: consecutive failures before marking unhealthy (default 2)

### URL Map (Routing Rules)

The URL map routes incoming requests to backend services or backend buckets based on:
- **Host rules**: route by hostname (e.g., `api.example.com` → backend-api, `www.example.com` → backend-web)
- **Path matchers**: route by URL path (e.g., `/api/*` → backend-api, `/static/*` → backend-bucket, `/*` → backend-default)
- **Advanced rules**: route by headers, query parameters, methods (global Application LB)
- **Traffic splitting**: send X% to backend-v1 and Y% to backend-v2 (for canary deployments)
- **Rewrites and redirects**: rewrite URL paths, redirect HTTP → HTTPS

### Target Proxy

Receives traffic from the forwarding rule and routes to the URL map:
- `target-http-proxy`: HTTP (no SSL termination)
- `target-https-proxy`: HTTPS (SSL termination; references SSL certificate)
- `target-ssl-proxy`: SSL termination for non-HTTP (external proxy Network LB)
- `target-tcp-proxy`: TCP proxy

### Forwarding Rule

The external entry point — binds an IP address and port to a target proxy or backend service:
- Global forwarding rule: anycast IP, global routing
- Regional forwarding rule: regional IP

### SSL Certificates

| Type | Description |
|---|---|
| Google-managed | Automatically provisioned and renewed by Google. Use domain-validated certificates. Zero ops. |
| Self-managed | Upload your own certificate (PEM format). You manage renewal. |
| Certificate Manager | Manages both Google-managed and self-managed certificates at scale; supports wildcards, Certificate Authority Service integration |

---

## Network Endpoint Groups (NEGs)

NEGs define backend endpoints more granularly than MIGs:

| NEG Type | Description | Use Case |
|---|---|---|
| Zonal NEG | Individual GCE VM NICs or GKE pod IPs in a specific zone | GKE container-native load balancing; fine-grained pod-level LB |
| Serverless NEG | Cloud Run, Cloud Functions, or App Engine services | Route traffic to serverless backends |
| Internet NEG | External IP/hostname backend (outside GCP) | Hybrid/third-party backends behind the GCP LB |
| Private Service Connect NEG | PSC endpoint (internal Google service or partner service) | Access internal services via PSC through the LB |
| Hybrid NEG | On-premises endpoints via Interconnect/VPN | Extend GCP LB to on-prem backends |

### Container-Native Load Balancing (GKE)

Using zonal NEGs with GKE bypasses the kube-proxy (NodePort) layer and routes the load balancer directly to pod IPs:
- Better health checking (per pod, not per node)
- Faster pod drain on scale-down
- Lower latency (one less hop)
- Requires GKE cluster with `--enable-ip-alias` and NEG annotations on Kubernetes Services

---

## Global vs. Regional Load Balancing

| Feature | Global Application LB | Regional Application LB |
|---|---|---|
| IP type | Anycast (single global IP) | Regional IP |
| Traffic routing | Routed to nearest healthy region automatically | Fixed to one region |
| Multi-region failover | Automatic | Manual (need separate LBs per region) |
| Backend regions | Multiple regions | Single region |
| Pricing | Slightly higher (global premium tier) | Regional standard tier available |
| Cloud CDN | Yes | Yes |
| Use case | Global apps, CDN, multi-region HA | Region-constrained apps, data residency |

---

## Session Affinity

| Mode | Description | Use Case |
|---|---|---|
| None (default) | Each request routed independently | Stateless applications |
| Client IP | Same client IP always goes to same backend | Basic stickiness |
| Generated cookie | LB inserts a cookie; sticky by cookie | Stateful web applications |
| Header field | Sticky based on a request header value | Microservices with customer-specific routing |
| HTTP cookie | Sticky based on an existing cookie in the request | Use existing application session cookie |

---

## Integration Points

| Integration | Description |
|---|---|
| Cloud CDN | Enable caching on backend services or backend buckets; edge caching at Google PoPs |
| Cloud Armor | Attach security policy (WAF, DDoS protection) to backend service |
| IAP (Identity-Aware Proxy) | Require Google identity authentication before backend access |
| Cloud Logging | Request-level logging to Cloud Logging |
| Certificate Manager | Centrally managed SSL certificates |
| Traffic Director | Service mesh control plane using LB infrastructure |

---

## Complete Request Flow (Global HTTPS LB)

```
Client
  → DNS resolution: example.com → Anycast IP (e.g., 34.120.x.x)
  → Google edge PoP (nearest to client)
  → Forwarding rule: 34.120.x.x:443
  → Target HTTPS proxy (SSL termination; certificate validated)
  → URL map (route /api/* to api-backend-service, /* to web-backend-service)
  → Cloud Armor security policy evaluation
  → Backend service (api-backend-service): pick healthy backend
  → Health check passes for us-central1 MIG
  → Request forwarded to VM/pod in us-central1
  → Response back to client
```

---

## Important Constraints

- **Global Application LB requires Premium Network Tier**: Standard Tier does not support global routing.
- **Health check source IPs**: Allow health check probes in firewall rules: `130.211.0.0/22` and `35.191.0.0/16`.
- **Backend instance groups must be in VPC**: MIGs attached to a global LB can be in any region but must be GCP VMs.
- **SSL certificate provisioning time**: Google-managed certificates can take up to 60 minutes to provision (DNS must propagate first).
- **URL map limits**: Up to 50 host rules, 10 path rules per path matcher, 25 additional route rules per path matcher.
- **No source IP preservation on proxy LBs**: Proxy-based LBs replace the client IP with the LB IP at the backend. Use `X-Forwarded-For` header or configure backend to log the header. Pass-through LBs preserve client IP.
- **Maximum forwarding rules**: 75 per project (can be increased via quota).
