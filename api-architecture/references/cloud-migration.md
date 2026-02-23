# Cloud Migration and API Infrastructure

This reference covers using API infrastructure to evolve toward cloud platforms, including migration strategies, the role of API management during migration, traffic patterns, zero trust security, and future directions for API architecture.

## Cloud Migration Strategies: The 6 Rs

The 6 Rs provide a decision framework for determining how each application or service should move to the cloud. Not every workload benefits from the same approach, and a typical enterprise migration uses several strategies in combination.

### Retain (Revisit)

Keep the application on-premises as-is. This is appropriate when:

- The application has regulatory or compliance constraints that prevent cloud hosting
- The cost of migration exceeds the benefit for this particular workload
- The application is tightly coupled to on-prem hardware (mainframes, specialized appliances)
- A future decommission or replacement is already planned

Retain is not "do nothing forever" -- it means consciously deferring the decision and revisiting it on a regular cadence. Tag retained workloads with a review date.

### Rehost (Lift and Shift)

Move the application to cloud virtual machines or infrastructure with no code changes. The application runs on cloud IaaS exactly as it ran on-prem.

**When to use:** Large legacy estates where speed of migration matters more than optimization. Rehosting moves workloads quickly and establishes a cloud footprint, after which teams can iteratively modernize.

**API implications:** Rehosted services keep existing APIs. The API gateway must now route to cloud-hosted endpoints. DNS and networking changes are the primary concern. Use API gateway routing rules to gradually shift traffic from on-prem to rehosted instances.

### Replatform (Lift, Tinker, and Shift)

Make targeted optimizations during migration without changing core architecture. Common replatforming moves include:

- Swapping a self-managed database for a managed service (e.g., PostgreSQL on EC2 to Amazon RDS)
- Containerizing the application and running it on a managed container platform (ECS, GKE)
- Replacing a local file store with cloud object storage (S3, GCS)
- Switching from self-managed message brokers to managed equivalents (Amazon SQS, Cloud Pub/Sub)

Replatforming captures some cloud benefits (reduced operational burden, better scaling) with moderate effort. API contracts remain unchanged, but the backing implementations shift to managed services.

### Repurchase (Drop and Shop)

Replace a custom or legacy application with a commercial SaaS product. Examples:

- Custom CRM to Salesforce
- Self-hosted email to Google Workspace or Microsoft 365
- Internal HR system to Workday
- Custom monitoring to Datadog or New Relic

**API implications are significant.** The new SaaS product exposes its own API, which likely differs from the legacy system. Teams must build integration layers, update API consumers, and potentially maintain a facade API that translates between the old contract and the new SaaS API during the transition period.

### Refactor / Re-architect

Redesign the application to be cloud-native, taking full advantage of cloud capabilities. This is the most effort-intensive strategy but yields the greatest long-term benefits.

Refactoring typically involves:

- Decomposing monoliths into microservices
- Adopting serverless compute (Lambda, Cloud Functions) for suitable workloads
- Implementing event-driven architectures with managed streaming platforms
- Designing for horizontal scalability and resilience patterns (circuit breakers, bulkheads)
- Building new APIs that reflect cleaner domain boundaries

**When to use:** For strategic, differentiating applications where cloud-native capabilities (auto-scaling, global distribution, managed AI/ML services) provide competitive advantage. Use the strangler fig pattern to incrementally refactor rather than attempting a big-bang rewrite.

### Retire (Decommission)

Identify and turn off applications that are no longer needed. Migration planning often reveals:

- Redundant applications serving the same function
- Applications with no active users or business sponsors
- Test/dev environments that were never cleaned up

Retiring workloads before migration reduces scope, cost, and complexity. From an API perspective, retiring means deprecating and eventually removing API endpoints, which requires clear communication with consumers through deprecation headers, documentation, and sunset timelines.

### Decision Framework

```
                    ┌─────────────────────────────┐
                    │  Is the application needed?  │
                    └──────────────┬──────────────┘
                           No ─────┤───── Yes
                           │               │
                        Retire    ┌────────┴────────┐
                                  │ Can a SaaS       │
                                  │ product replace  │
                                  │ it?              │
                                  └───────┬─────────┘
                                  Yes ────┤──── No
                                  │               │
                              Repurchase  ┌───────┴──────────┐
                                          │ Is it strategic   │
                                          │ and differentiating│
                                          │ enough for major  │
                                          │ investment?       │
                                          └───────┬──────────┘
                                          Yes ────┤──── No
                                          │               │
                                      Refactor   ┌───────┴──────┐
                                                  │ Can it run    │
                                                  │ in the cloud  │
                                                  │ at all?       │
                                                  └──────┬───────┘
                                                  No ────┤──── Yes
                                                  │             │
                                              Retain    ┌──────┴──────┐
                                                        │ Worth minor │
                                                        │ optimization│
                                                        │ effort?     │
                                                        └──────┬─────┘
                                                        Yes ───┤─── No
                                                        │           │
                                                   Replatform   Rehost
```

## Role of API Management in Cloud Migration

### API Gateway as Migration Enabler

The API gateway is the single most important infrastructure component during migration. Because all external traffic flows through the gateway, it provides a control point to redirect traffic without changing client behavior.

**Key capabilities during migration:**

- **Traffic splitting:** Route a percentage of requests to the cloud-hosted service while keeping the remainder on-prem. This enables gradual, risk-controlled cutover.
- **Canary routing:** Send a small slice of production traffic to the new deployment, compare error rates and latency, then increase the percentage.
- **Header-based routing:** Route requests based on custom headers, allowing internal testers to hit the cloud deployment while external users remain on the legacy system.
- **Fallback routing:** If the cloud deployment returns errors, automatically fall back to the on-prem instance.

```
                    Clients
                       │
                       ▼
              ┌────────────────┐
              │   API Gateway   │
              │                │
              │  Route rules:  │
              │  90% → on-prem │
              │  10% → cloud   │
              └───┬────────┬───┘
                  │        │
          ┌───────▼──┐  ┌──▼───────┐
          │ On-Prem  │  │  Cloud   │
          │ Service  │  │ Service  │
          └──────────┘  └──────────┘
```

### API Versioning During Migration

Migration often changes API implementations but should preserve contracts. Strategies for managing this:

- **Contract-first design:** Define the API contract in OpenAPI and verify both on-prem and cloud implementations conform to it using contract tests.
- **Parallel running:** Run both implementations simultaneously, compare responses for consistency (shadow traffic or diff testing).
- **Version negotiation:** If the cloud implementation introduces breaking changes, expose it under a new API version (`/v2/`) while maintaining the legacy version. Use the gateway to route version-specific traffic.
- **Deprecation lifecycle:** Once migration is complete, announce deprecation of the old version, provide a sunset timeline, and eventually remove it.

## North-South vs East-West Traffic

### Traditional Distinction

**North-south traffic** flows between external clients and internal services. It crosses the network perimeter and is handled by the API gateway at the edge. Concerns include authentication, rate limiting, TLS termination, and request validation.

**East-west traffic** flows between internal services within the data center or cluster. It is handled by the service mesh. Concerns include service discovery, load balancing, mutual TLS, retries, circuit breaking, and observability.

```
    North-South (external)              East-West (internal)
    ──────────────────────              ────────────────────
    Client → Gateway → Service          Service A ↔ Service B

    Managed by: API Gateway             Managed by: Service Mesh
    Focus: External access control      Focus: Internal reliability
    Auth: OAuth2, API keys              Auth: mTLS, SPIFFE identities
    Rate limiting: Per-client           Rate limiting: Per-service
```

### Blurring Lines

In modern cloud-native architectures, the distinction between north-south and east-west is converging:

- **API gateways moving inward.** Lightweight gateway instances (micro-gateways) deploy alongside services within the cluster, handling both ingress and inter-service routing.
- **Service meshes moving outward.** Mesh ingress gateways (e.g., Istio's ingress gateway) handle external traffic with the same configuration model as internal traffic.
- **Multi-cluster and multi-cloud.** When services span clusters or cloud providers, what was "east-west" traffic between internal services now crosses network boundaries, requiring gateway-like security and routing.
- **Platform mesh convergence.** A unified data plane handles all traffic regardless of direction, applying consistent policies for security, observability, and traffic management.

## Start at the Edge and Work Inward

The recommended migration approach is outside-in:

1. **Deploy an API gateway first.** Place it at the edge of your network as the single entry point. This gives you centralized control over routing, authentication, and observability before anything else moves.

2. **Migrate edge services.** Start with services that have the fewest internal dependencies -- typically BFF (backend-for-frontend) layers or simple API aggregation services.

3. **Progressively migrate deeper services.** As edge services stabilize in the cloud, migrate the services they depend on, working layer by layer toward core domain services and data stores.

4. **Introduce service mesh for internal traffic.** Once multiple services run in the cloud, deploy a service mesh to manage east-west communication with consistent security and observability.

5. **Decommission on-prem infrastructure.** Once all traffic flows through cloud-hosted services, retire the legacy infrastructure.

This approach minimizes risk because the gateway absorbs the complexity of routing between old and new environments, and each layer is validated before the next one migrates.

## Crossing Boundaries: Hybrid and Multi-Cloud Routing

Real-world migrations involve extended periods where services span on-prem data centers, private cloud, and one or more public cloud providers. API infrastructure must handle routing across these boundaries.

**Challenges:**

- **Network latency:** Cross-network calls add latency that did not exist when services were co-located. API gateways and meshes must account for increased timeouts and implement retries judiciously.
- **Security boundaries:** Traffic between environments must be encrypted in transit. Mutual TLS between gateways or mesh proxies on each side provides this.
- **Service discovery:** Services in different environments need a unified discovery mechanism. Options include DNS-based discovery, a shared service registry, or mesh federation (e.g., Istio multi-cluster).
- **Data residency:** Some data cannot leave certain geographic or network boundaries. API routing must respect these constraints.

**Patterns for cross-boundary routing:**

- **Gateway-to-gateway:** Each environment runs its own API gateway. Gateways communicate over encrypted channels, acting as proxies for services in their respective environments.
- **Mesh federation:** Service meshes in different clusters or environments are federated, allowing transparent cross-cluster service discovery and mTLS.
- **API relay:** A lightweight relay service sits at the boundary, forwarding requests and handling protocol translation if needed.

## From Zonal Architecture to Zero Trust

### Traditional Zone-Based Security

The conventional approach to network security is **zonal architecture**: the network is divided into zones of trust, separated by firewalls.

```
┌──────────────────────────────────────────────────────┐
│                    Internet                           │
└──────────────────────┬───────────────────────────────┘
                       │ Firewall
┌──────────────────────▼───────────────────────────────┐
│                      DMZ                             │
│              (Web servers, load balancers)            │
└──────────────────────┬───────────────────────────────┘
                       │ Firewall
┌──────────────────────▼───────────────────────────────┐
│                 Application Zone                      │
│              (Application servers, APIs)              │
└──────────────────────┬───────────────────────────────┘
                       │ Firewall
┌──────────────────────▼───────────────────────────────┐
│                   Data Zone                           │
│              (Databases, storage)                     │
└──────────────────────────────────────────────────────┘
```

Traffic from the internet is filtered at each boundary. The assumption is that traffic within a zone is trusted because the perimeter controls prevent unauthorized access.

### Problems with Zonal Architecture

- **Lateral movement:** Once an attacker breaches the perimeter (phishing, supply chain compromise, insider threat), they can move freely within the trusted zone. This is the attack pattern behind most major breaches.
- **Assumed trust:** Services within a zone communicate without authentication or encryption. Any compromised service can impersonate others or intercept traffic.
- **Static rules:** Firewall rules are based on IP addresses and ports, which are poor proxies for identity in dynamic, containerized environments where IPs change constantly.
- **Cloud incompatibility:** Cloud and container environments blur network boundaries. Pods in Kubernetes share networks. Multi-cloud deployments span multiple network perimeters. The concept of a "trusted internal network" breaks down.

### Zero Trust Principles

Zero trust eliminates the concept of a trusted network. Every request is verified regardless of its origin. The core principles:

1. **Never trust, always verify.** Every request must be authenticated and authorized, even between internal services. Network location grants no implicit trust.

2. **Least privilege access.** Services and users receive the minimum permissions needed for their function. Access is granted per-request based on identity, context, and policy.

3. **Assume breach.** Design as if the network is already compromised. Encrypt all traffic (even internal), segment access, and monitor for anomalous behavior.

4. **Continuous verification.** Authentication is not a one-time gate. Sessions and tokens are short-lived, and authorization is checked on every request.

### Role of Service Mesh in Zero Trust

The service mesh is the primary infrastructure for implementing zero trust in microservice architectures. It provides:

**Automatic mTLS:** The mesh sidecar proxies automatically establish mutual TLS between all services. This provides encryption in transit and cryptographic identity verification without application code changes. Every service-to-service call is both encrypted and authenticated.

**Identity-based policy enforcement:** Instead of firewall rules based on IP addresses, the mesh enforces authorization policies based on service identity (typically SPIFFE/SPIRE identities or Kubernetes service accounts).

```yaml
# Istio AuthorizationPolicy example: only allow orders-service
# to call the payments-service
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payments-access
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payments-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/orders/sa/orders-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charges"]
```

**Observability and audit:** The mesh captures detailed telemetry on every service-to-service call -- who called whom, with what method, what the response code was, and how long it took. This provides the visibility required for continuous verification and anomaly detection.

**Gradual adoption:** Meshes can be deployed incrementally. Start with mTLS in permissive mode (accept both encrypted and plaintext), then shift to strict mode once all services are enrolled.

### Identity-Based vs Network-Based Security

| Aspect | Network-Based (Zonal) | Identity-Based (Zero Trust) |
|--------|----------------------|----------------------------|
| Trust model | Trust by network location | Trust by verified identity |
| Authentication | Implicit (inside the zone) | Explicit (mTLS, JWT, SPIFFE) |
| Authorization | Firewall rules (IP/port) | Policy engine (identity/attributes) |
| Encryption | At zone boundaries only | End-to-end, always on |
| Granularity | Coarse (network segments) | Fine (per-service, per-method) |
| Dynamic environments | Poorly suited | Designed for ephemeral workloads |
| Lateral movement | Easy once perimeter breached | Contained by per-service policies |

## Future Directions

### Async Communication and Event-Driven APIs

Synchronous request-response APIs (REST, gRPC) are not always the right model. Event-driven architectures use asynchronous messaging for decoupled, resilient communication.

**AsyncAPI specification:** Just as OpenAPI describes REST APIs, AsyncAPI provides a machine-readable specification for event-driven APIs. It defines channels, message schemas, and protocol bindings (Kafka, AMQP, WebSocket, MQTT). AsyncAPI enables the same design-first, code-generation workflow for async APIs that OpenAPI enables for REST.

**Event mesh:** An event mesh extends the service mesh concept to asynchronous messaging. It provides dynamic routing of events across environments, protocol bridging, schema governance, and consistent security policies for event-driven traffic. Products like Solace PubSub+ and integrations between service meshes and message brokers are moving in this direction.

### HTTP/3 and QUIC

HTTP/3 replaces TCP with QUIC as the transport protocol. Implications for API infrastructure:

- **Reduced connection latency:** QUIC combines the transport and TLS handshakes into a single round trip (0-RTT for resumed connections). This is significant for API calls from mobile and high-latency networks.
- **No head-of-line blocking:** Unlike HTTP/2 over TCP, where a lost packet blocks all streams on the connection, QUIC streams are independent. A lost packet in one API request does not delay others.
- **Connection migration:** QUIC connections survive network changes (e.g., switching from WiFi to cellular), which matters for mobile API clients.
- **Infrastructure impact:** API gateways, load balancers, and mesh proxies must support QUIC/HTTP/3. Envoy proxy (the data plane behind Istio and many gateways) has added HTTP/3 support. Monitoring tools must understand QUIC traffic.

### Platform-Based Mesh: Convergence

The industry is moving toward a converged platform that unifies API gateway, service mesh, and developer platform capabilities:

- **Single control plane** managing both north-south and east-west traffic with the same configuration model.
- **Unified policy engine** applying security, rate limiting, and routing rules consistently across all traffic regardless of direction.
- **Developer self-service** where teams publish APIs, configure routing, and set policies through a platform portal, abstracting away the underlying gateway and mesh infrastructure.
- **Ambient mesh** architectures (e.g., Istio ambient mode) that eliminate per-pod sidecars in favor of node-level or platform-level proxies, reducing resource overhead and operational complexity.

### Conway's Law and Organizational Design

Conway's Law states that organizations design systems that mirror their communication structures. For API architecture, this means:

- **Team boundaries become API boundaries.** The APIs between services often reflect the organizational boundaries between teams. Well-designed team structures lead to well-designed API boundaries.
- **Inverse Conway maneuver:** Deliberately structure teams to produce the desired system architecture. If you want loosely coupled services with clean API boundaries, organize teams around business domains rather than technical layers.
- **API governance reflects organizational culture.** Centralized API standards work in hierarchical organizations; federated API governance works in autonomous team cultures.

### Decision Types: One-Way and Two-Way Doors

Not all architectural decisions carry equal weight. Amazon's framework of one-way and two-way doors is useful:

**Two-way doors (reversible decisions):** Can be easily undone. Examples: choosing an internal serialization format, picking a specific caching strategy, selecting a logging library. Make these decisions quickly, observe the results, and change course if needed.

**One-way doors (irreversible or costly-to-reverse decisions):** Have lasting consequences. Examples: choosing a public API contract (breaking changes affect external consumers), selecting a cloud provider for core infrastructure, adopting a specific data partitioning strategy. These deserve careful analysis, prototyping, and broader stakeholder input.

**For API architecture specifically:**

| Decision | Door Type | Reasoning |
|----------|-----------|-----------|
| Public API contract shape | One-way | External consumers depend on it; breaking changes are costly |
| Internal service communication protocol | Two-way | Can be changed without affecting external consumers |
| API gateway product selection | Mostly one-way | Deep integration makes switching expensive |
| Service mesh adoption | Two-way (with effort) | Can be incrementally adopted and removed |
| Cloud provider selection | One-way | Data gravity and service dependencies create lock-in |
| API versioning strategy | One-way | Establishes a precedent that consumers rely on |
| Database per service vs shared DB | One-way | Data migration between models is extremely difficult |

The key insight is to spend decision-making effort proportionally. Move fast on two-way doors. Be deliberate on one-way doors. Use techniques like API prototyping, traffic shadowing, and limited rollouts to convert apparent one-way doors into two-way doors wherever possible.
