# API Gateways: Ingress Traffic Management

This reference covers API gateways for managing north-south (ingress) API traffic: when to use one, what they provide, deployment patterns, taxonomy, failure management, anti-patterns, and selection guidance.

## Is an API Gateway the Only Solution?

The three core ingress options -- reverse proxy, load balancer, and API gateway -- overlap significantly.

| Capability | Reverse Proxy | Load Balancer | API Gateway |
|---|---|---|---|
| Request routing | Path/host based | Target group rules | Rich routing, URL rewriting |
| TLS termination | Yes | Yes | Yes |
| Authentication | Basic auth only | Limited | OAuth2, JWT, API keys, mTLS |
| Rate limiting | Per-IP | No | Per-consumer, per-plan |
| Transformation | Header rewriting | No | Full body/header/query |
| Analytics | Access logs | Basic metrics | Per-consumer usage |
| Developer portal | No | No | Yes |

Use a reverse proxy for basic routing and TLS. Use a load balancer when traffic distribution and failover are primary concerns. Use an API gateway when you need API-aware functionality: per-consumer auth, rate limiting, transformation, or lifecycle management. Many architectures combine all three.

## What Is an API Gateway?

An API gateway is a server that acts as the single entry point for API traffic. It sits between external consumers and backend services, applying cross-cutting policies (authentication, rate limiting, transformation) and routing requests to the appropriate backend.

The gateway serves as a **facade** or **adapter** between the external API contract and internal service topology. Consumers interact with a stable external API; the gateway translates requests into internal calls, insulating consumers from backend changes.

```
        Consumers (mobile, web, partners)
                  │
                  ▼
        ┌──────────────────┐
        │   API Gateway     │  ← Single entry point, cross-cutting concerns
        └────────┬─────────┘
     ┌───────────┼───────────┐
     ▼           ▼           ▼
  Service A   Service B   Service C   ← Free to evolve independently
```

## Gateway Functionality

**Request routing and URL rewriting.** Maps external paths to internal endpoints, decoupling the public API surface from service topology. Includes header-based, canary (percentage-based), and content-based routing.

**Authentication and authorization.** Centralizes identity verification: API key validation, JWT signature verification with claim injection, OAuth2 token introspection, mTLS termination. Enforces coarse-grained authorization based on scopes, roles, or subscription tiers.

**Rate limiting and throttling.** Protects backends and enforces fair usage at multiple granularities: global (protect capacity), per-consumer (fair usage), per-endpoint (protect writes), and per-plan (tiered monetization). Common algorithms: fixed window, sliding window, token bucket, leaky bucket.

**Request/response transformation.** Header injection (correlation IDs, consumer metadata), body transformation (XML/JSON conversion, payload reshaping), protocol translation (REST to gRPC), and response aggregation (BFF pattern).

**Caching.** Cache responses for idempotent operations, respecting HTTP headers (`Cache-Control`, `ETag`) or custom per-route policies.

**SSL/TLS termination.** Centralizes certificate management and cipher negotiation. Internal traffic uses plaintext (trusted network) or mTLS (zero trust).

**Observability.** Access logging with consumer identity, metrics per consumer/endpoint, distributed tracing (W3C Trace Context), and API usage analytics.

**API lifecycle management.** Version management, deprecation (`Sunset` headers, eventual 410 Gone), API publishing without redeploying backends.

**Developer portal.** API catalog, interactive documentation, self-service key provisioning, usage dashboards, sandbox environments.

## Deployment Patterns

**Edge gateway (north-south).** Most common. Sits at the network perimeter, handles all external ingress traffic. Enforces security, rate limits, and routing for all inbound API calls.

**Internal gateway (east-west).** Deployed within the network to manage traffic between organizational domains. Useful when internal teams need API governance, versioning, or usage tracking but a full service mesh is not warranted.

**Sidecar / micro gateway.** Lightweight gateway deployed alongside each service or service group. Distributes gateway functionality, reduces blast radius, allows per-service configuration. Closely related to service mesh proxies.

## Integration with Edge Technologies

```
Client → CDN → WAF → Load Balancer → API Gateway → Backend Services
          │      │         │                │
          │      │         │                └─ Auth, rate limiting, routing, analytics
          │      │         └─ Distribute across gateway instances, health checks
          │      └─ Filter malicious requests (SQLi, XSS, OWASP rules)
          └─ Cache static content, absorb DDoS at edge locations
```

Each layer has a distinct responsibility. The CDN handles geographic distribution. The WAF filters attacks before they consume gateway resources. The load balancer ensures gateway cluster HA. The API gateway applies API-specific policies. Collapsing layers creates capability gaps.

## Why Use an API Gateway?

**Reduce coupling.** The gateway acts as an adapter between external contracts and internal topology. Services can be refactored, split, or replaced without breaking consumers.

**Simplify consumption.** Aggregate multiple backend calls into a single endpoint, reducing client complexity and round trips (BFF pattern).

**Protect APIs.** Centralize rate limiting, authentication, input validation, and IP filtering. Consistent enforcement avoids individual services missing security checks.

**Observability.** Single pane of glass for all API traffic: health monitoring, error tracking per consumer, anomalous traffic detection.

**Manage APIs as products.** Publishing, versioning, access control, usage tracking, SLA enforcement, and documentation.

**Monetize APIs.** Per-consumer metering, plan-based rate limits, and billing system integration.

## History of API Gateways

```
Late 1990s    Hardware LBs (F5 BIG-IP, Citrix NetScaler)
              └─ L4 TCP balancing, SSL offload, expensive appliances

Early 2000s   Application Delivery Controllers (ADCs)
              └─ L7-aware: HTTP routing, content switching, compression

Mid 2000s     Software LBs (HAProxy, Nginx)
              └─ Same L7 capabilities, commodity hardware, open source

Early 2010s   First-Gen API Gateways (Apigee, MuleSoft, 3scale)
              └─ API-specific: key management, portals, analytics, heavyweight

Mid 2010s     Microservices Gateways (Kong, Zuul, Ambassador)
              └─ Lightweight, config-as-code, plugin architectures, K8s-native

Late 2010s+   Service Mesh Integration (Istio, Envoy, Linkerd)
              └─ Gateway as mesh ingress, unified N-S and E-W data plane
```

Generations coexist. Many organizations run hardware LBs at the edge, software gateways for API management, and mesh proxies for internal traffic.

## API Gateway Taxonomy

**Traditional enterprise gateways** (Apigee, MuleSoft, Kong Enterprise, AWS API Gateway, Azure APIM). Full lifecycle management, portals, analytics, monetization. Higher latency, expensive, risk of lock-in.

**Microservices / micro gateways** (Kong OSS, Emissary-Ingress, KrakenD, Tyk OSS, Gloo Edge). Low latency, config-as-code, CI/CD friendly, extensible plugins. Portal and analytics require separate tools.

**Service mesh gateways** (Istio Ingress Gateway, Consul API Gateway, K8s Gateway API). Unified config for ingress and internal traffic, consistent mTLS and observability. Requires mesh adoption.

| Characteristic | Enterprise | Micro Gateway | Mesh Gateway |
|---|---|---|---|
| Audience | API product managers | Developers | Platform/SRE teams |
| Configuration | UI/console | Declarative, GitOps | Kubernetes CRDs |
| Latency | 5-20ms | 1-5ms | 1-5ms |
| Developer portal | Built-in | Separate tool | Not included |
| East-west traffic | No | No | Yes (mesh) |
| Cost | $$$ | $ to $$ | $ (mesh infra) |
| Best for | External API programs | Microservices, internal | Orgs already using mesh |

## Deployment and Failure Management

The gateway is a critical SPOF -- if it fails, all API traffic stops.

**Detecting problems.** Monitor availability (health probes), latency (gateway-only p50/p95/p99), error rate (gateway 502/503 vs passthrough errors), saturation (CPU, memory, connections), and config consistency across instances.

**Mitigating risks.** Run minimum three instances across availability zones. Health-based routing removes unhealthy instances. Canary-deploy config changes. Circuit-break on failing backends. Serve stale cached responses during outages rather than 503. Maintain emergency bypass ability to route directly to backends.

## Common Pitfalls

### API Gateway Loopback

Internal services calling other services back through the external gateway instead of directly.

```
WRONG:   Client → Gateway → Svc A → Gateway → Svc B  (doubles load/latency)
CORRECT: Client → Gateway → Svc A → Svc B             (direct internal call)
```

Doubles gateway load and latency, creates circular dependency, wastes rate limit budget. Services should call each other via service discovery, DNS, or mesh -- never through the external gateway.

### API Gateway as ESB

Moving business logic, orchestration, or complex transformations into the gateway: conditional routing on business rules, composite responses with business logic, or stateful request handling.

The gateway becomes a monolithic coupling point. Business changes require gateway redeployment affecting all APIs. Testing splits between gateway policies and service code.

**Litmus test:** If a business requirements change requires modifying gateway configuration, the gateway is doing too much. Keep it focused on infrastructure concerns. Build dedicated BFF services for aggregation logic.

### Turtles All the Way Down

Multiple gateway layers accumulate: edge GW, internal GW, micro GW, mesh proxy. Each adds 5-20ms latency, debugging complexity, and fragmented configuration.

Audit the traffic path and justify each component. A service mesh gateway can often replace internal + sidecar gateways. Two layers (edge gateway + service mesh) is common and reasonable. Four or more layers indicates organic accumulation that should be rationalized.

## Selecting an API Gateway

### Requirements-Driven Selection

| Category | Key Questions |
|---|---|
| Traffic profile | External or internal? Volume? Latency budget? |
| Security | Auth mechanisms? Compliance (PCI, HIPAA)? WAF integration? |
| API management | Developer portal? Monetization? Self-service keys? |
| Deployment | Kubernetes? Multi-cloud? On-premise? Serverless? |
| Team structure | Central platform team or decentralized? |
| Integration | Identity provider? Observability stack? CI/CD? |
| Budget | OSS acceptable? Commercial support required? |

### Build vs Buy

Building a custom gateway is almost never right. **Build** (extend Envoy/Nginx) only with extremely specific requirements and dedicated platform engineering capacity. **Buy** when requirements map to standard gateway functionality or you need enterprise features expensive to build.

### ADR Approach

Document the selection as an Architecture Decision Record. Evaluate at least three candidates from different categories. Run a 1-2 week proof of concept with the top two using representative traffic. Evaluate operational experience (configure, deploy, debug, upgrade), not just feature checklists.

| If your priority is... | Consider... |
|---|---|
| External API program with portal/monetization | Apigee, Kong Enterprise, Azure APIM |
| Lightweight K8s microservices ingress | Emissary-Ingress, Kong OSS, KrakenD |
| Unified ingress + internal traffic | Istio, Consul mesh gateway |
| Serverless APIs on AWS | AWS API Gateway (HTTP API or REST API) |
| Maximum flexibility and performance | Envoy-based with custom filters |
| Minimal operational overhead | Managed SaaS (Apigee X, AWS API GW, Azure APIM) |
