---
name: api-architecture
description: >
  Expert-level API architecture guidance covering REST API design, gRPC,
  GraphQL, OpenAPI specifications, API gateways, service mesh, API security,
  testing strategies, and evolutionary architecture. Use when the user is
  working with API design, REST APIs, RESTful services, HTTP APIs, OpenAPI
  (Swagger), API versioning, API pagination, API error handling, Richardson
  Maturity Model, API gateways (Kong, Ambassador, Apigee, AWS API Gateway),
  service mesh (Istio, Linkerd, Consul), API authentication, OAuth2, JWT,
  OIDC, API threat modeling, STRIDE, OWASP API Security, API testing,
  contract testing (Pact), API deployment strategies (canary, blue-green,
  traffic mirroring), API lifecycle management, API-first design, or any
  topic related to designing, operating, and evolving API-based systems.
  Also triggers on discussions of north-south vs east-west traffic, API
  specifications, code generation from APIs, API standards, zero trust
  architecture for APIs, strangler fig pattern, or migrating monoliths to
  API-driven microservices.
---

# API Architecture Expert

## Core Concept

API architecture is the discipline of **designing, operating, and evolving API-based systems** that enable reliable communication between services, teams, and organizations. It spans the full lifecycle from API design and specification through traffic management, security, testing, deployment, and architectural evolution.

## The Four Pillars of API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Architecture                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │    DESIGN     │  │   TRAFFIC    │  │    SECURITY &    │  │
│  │              │  │  MANAGEMENT  │  │    OPERATIONS    │  │
│  │ REST, RPC,   │  │             │  │                  │  │
│  │ GraphQL,     │  │ API gateway, │  │ Auth, threat     │  │
│  │ OpenAPI,     │  │ service mesh,│  │ modeling, deploy, │  │
│  │ versioning   │  │ load balance │  │ observability    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    EVOLUTION                             ││
│  │  Strangler fig, decomposition, cloud migration, fitness ││
│  │  functions, API seams, zero trust                       ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## API Style Comparison

| Style | Format | Transport | Strengths | Best For |
|-------|--------|-----------|-----------|----------|
| **REST** | JSON/XML | HTTP/1.1+ | Ubiquitous, cacheable, stateless | Public APIs, CRUD, web |
| **gRPC** | Protobuf | HTTP/2 | Performance, streaming, code gen | Internal services, high throughput |
| **GraphQL** | JSON | HTTP | Flexible queries, no over-fetching | Frontend-driven, complex graphs |
| **AsyncAPI** | Various | AMQP/Kafka/etc | Event-driven, decoupled | Event streaming, pub/sub |

## Richardson Maturity Model

```
Level 3: Hypermedia Controls (HATEOAS) ← links in responses guide clients
Level 2: HTTP Verbs                    ← proper use of GET/POST/PUT/DELETE + status codes
Level 1: Resources                     ← distinct URIs for different resources
Level 0: The Swamp of POX             ← single URI, single verb (RPC-over-HTTP)
```

Most production APIs target **Level 2**. Level 3 (HATEOAS) adds discoverability but is rarely fully implemented.

## REST API Design Quick Reference

```
GET    /orders              → List orders (200)
GET    /orders/{id}         → Get single order (200, 404)
POST   /orders              → Create order (201, 400)
PUT    /orders/{id}         → Replace order (200, 404)
PATCH  /orders/{id}         → Partial update (200, 404)
DELETE /orders/{id}         → Delete order (204, 404)
```

**Pagination:** `GET /orders?offset=0&limit=25` or cursor-based `?cursor=abc123`
**Filtering:** `GET /orders?status=shipped&created_after=2024-01-01`
**Error format:**
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Field 'email' must be a valid email address",
  "instance": "/orders/12345"
}
```

## API Traffic Flow

```
                External Clients
                      │
                      ▼
              ┌───────────────┐
              │  API Gateway   │  ← North-South traffic (ingress)
              │  (rate limit,  │     Auth, routing, TLS termination
              │   auth, route) │
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │Service A │  │Service B │  │Service C │
   │         │◄►│         │◄►│         │  ← East-West traffic
   └─────────┘  └─────────┘  └─────────┘    (service mesh)
```

## Key Decision Records

| Decision | Options | Guidance |
|----------|---------|----------|
| API style | REST vs gRPC vs GraphQL | REST for public/external; gRPC for internal high-perf; GraphQL for flexible frontends |
| Versioning | URL path vs header vs query param | URL path (`/v1/`) is simplest and most common |
| Gateway | Traditional vs micro vs mesh | Match to org size and deployment model |
| Auth | API keys vs OAuth2 vs mTLS | OAuth2 for user-facing; mTLS for service-to-service; API keys for simple cases |
| Testing | Contract vs integration vs E2E | Contract testing for API boundaries; integration for critical paths |

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **API Design** | [references/api-design.md](references/api-design.md) | REST, RPC, GraphQL, OpenAPI specs, versioning, pagination, error handling, API standards, code generation (Ch 1) |
| **API Testing** | [references/testing.md](references/testing.md) | Test strategies, contract testing (Pact), component testing, integration testing, E2E testing, Testcontainers (Ch 2) |
| **API Gateways** | [references/api-gateways.md](references/api-gateways.md) | Gateway types, functionality, deployment patterns, pitfalls (ESB, loopback), selection criteria (Ch 3) |
| **Service Mesh** | [references/service-mesh.md](references/service-mesh.md) | Mesh concepts, routing, observability, security, Istio/Linkerd/Consul, implementation challenges (Ch 4) |
| **Deployment & Release** | [references/deployment-release.md](references/deployment-release.md) | Canary releases, blue-green, traffic mirroring, feature flags, observability, release strategies (Ch 5) |
| **Threat Modeling** | [references/threat-modeling.md](references/threat-modeling.md) | OWASP API Security, STRIDE methodology, threat modeling process, API-specific attack vectors (Ch 6) |
| **Authentication & Authorization** | [references/auth.md](references/auth.md) | OAuth2 grants, JWT, OIDC, SAML, API keys, scopes, authorization enforcement (Ch 7) |
| **Evolutionary Architecture** | [references/evolutionary-architecture.md](references/evolutionary-architecture.md) | Strangler fig, facade/adapter, API layer cake, decomposition, fitness functions, domain boundaries (Ch 8) |
| **Cloud Migration** | [references/cloud-migration.md](references/cloud-migration.md) | Migration strategies (6 Rs), zero trust, zonal architecture, API management at the edge (Ch 9) |
| **REST API Standards** | [references/api-standards.md](references/api-standards.md) | Industry standards from Microsoft, Google, Zalando; naming conventions, URL design, HTTP methods, pagination patterns, error formats |
