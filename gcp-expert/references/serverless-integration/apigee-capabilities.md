# Apigee — Capabilities

## Purpose and Overview

Apigee is Google Cloud's enterprise-grade API management platform for designing, securing, deploying, monitoring, and monetizing APIs. It acts as a policy enforcement layer between API consumers (apps, partners, customers) and backend services (Cloud Run, GKE, Compute Engine, on-prem, third-party APIs).

Apigee is appropriate when you need:
- Enterprise security policies (OAuth 2.0, API keys, SAML, JWT validation, threat protection)
- Developer portal with self-service API key management and documentation
- Quota and rate limiting per developer app or API product tier
- API analytics dashboards and export to BigQuery
- Monetization (billing developers for API usage)
- API versioning and lifecycle management
- Complex message transformation (JSON↔XML, XSLT, payload manipulation)
- Multi-cloud and hybrid API gateway deployment

---

## Deployment Options

### Apigee X (Recommended)
- Fully managed by Google in a GCP project.
- Runtime components (message processors, routers) run in a Google-managed VPC, peered to your VPC.
- Management plane (UI, analytics, API) hosted at `apigee.googleapis.com`.
- Supports all Apigee X features: VPC peering, Private Service Connect, Cloud Armor integration, mTLS.
- Requires a minimum commitment (not free-tier friendly); billed by environment and API call volume.

### Apigee Hybrid
- Apigee runtime (message processors) runs in your GKE cluster (on-prem or any cloud).
- Management plane hosted by Google Cloud.
- Use when you need data sovereignty (API traffic never leaves your premises) or ultra-low latency to on-prem backends.
- More operational complexity: you manage GKE, certificates, Apigee runtime upgrades.

### Apigee Edge (Legacy)
- On-premises or private cloud deployment.
- Apigee Edge is in maintenance mode; migrate to Apigee X or Hybrid.

---

## Core Concepts

### Organization
The top-level container in Apigee. One Apigee organization maps to one GCP project. Contains environments, API proxies, API products, developers, and developer apps.

### Environment
A named deployment target within an organization (e.g., `dev`, `staging`, `prod`). API proxies are deployed to specific environments. Each environment has its own base path, virtual hosts, and KVMs. Environment groups map hostnames to environments.

### API Proxy
The core unit of API management. An API proxy intercepts requests at the Apigee gateway and applies a policy pipeline before forwarding to the target backend.

**API Proxy components**:
- **ProxyEndpoint**: defines the inbound connection (base path, virtual host, HTTPS, pre-flow/post-flow policies).
- **TargetEndpoint**: defines the outbound connection to the backend (target URL, load balancing, SSL, pre-flow/post-flow policies).
- **Flows**: request/response pipelines where policies are attached. Conditional flows match specific paths or verbs.
- **Policies**: processing steps attached to flows (see Policy Categories below).
- **Resources**: JavaScript, Python, Java callout JARs, XSLT, OpenAPI specs.

### API Product
A bundle of API proxies (and their allowed paths/verbs) packaged for developer consumption. API products define:
- Which proxy resources are accessible.
- Quota (e.g., 1000 requests/hour).
- OAuth scopes.
- Environment (dev/prod).
- Allowed apps.

Developers subscribe to API products, not directly to proxies.

### Developer and Developer App
A **Developer** represents an external API consumer registered in Apigee (name, email). A **Developer App** is created by a developer to consume API products; it holds the API keys (consumer key/secret) and controls which API products the app can access.

### Developer Portal
Self-service portal where external developers:
- Discover APIs (Catalog with OpenAPI documentation rendered as Swagger UI).
- Register developer accounts.
- Create developer apps and obtain API keys.
- View their quota usage.
- Access usage reports.

Apigee X includes an integrated portal (Apigee's built-in portal) or integration with Drupal/Pantheon-based portal. Publish API products to the portal to make them discoverable.

---

## Policy Categories

### Traffic Management
- **Quota**: enforce request limits per time window (minute/hour/day/month) per developer app, API product, or custom key. Distributed quota counter across all message processors.
- **Spike Arrest**: protect backends from sudden traffic bursts; smooths requests over time (per-second or per-minute rate). Unlike Quota, Spike Arrest does not maintain a counter — it enforces a smooth rate.
- **Response Cache**: cache backend responses at the proxy layer to reduce backend load; cache key based on request URL/headers/variables; TTL configurable.
- **Concurrent Rate Limit**: limit concurrent connections to a target (useful for protecting legacy backends with limited thread capacity).

### Security
- **OAuthV2**: OAuth 2.0 authorization code, client credentials, implicit, and password grant flows; token generation and validation; scopes enforcement; refresh tokens.
- **VerifyAPIKey**: validate an API key from request header or query param against Apigee's developer app registry; populate flow variables with app metadata.
- **JWT (Generate/Verify/Decode)**: generate JWTs signed with RSA/HMAC; verify incoming JWTs; decode without verification.
- **SAML Assertion**: validate SAML 2.0 tokens from enterprise identity providers.
- **HMAC (Generate/Verify)**: message integrity validation.
- **JSON Threat Protection**: detect JSON payload attacks (excessive nesting depth, array length, string length).
- **XML Threat Protection**: detect XML attacks (entity expansion, element depth).
- **Regular Expression Protection**: detect injection attacks in request parameters using regex patterns.
- **CORS**: set Cross-Origin Resource Sharing headers for browser-based API consumers.
- **BasicAuthentication**: encode/decode Base64 credentials; translate Basic Auth to downstream auth method.

### Mediation
- **AssignMessage**: create/modify/remove request/response headers, body, query params, form params. Copy variables into messages.
- **ExtractVariables**: extract data from request/response using JSONPath, XPath, URI template, form params, headers into flow variables.
- **XMLToJSON / JSONToXML**: transform message body between formats.
- **XSLT Transform**: apply XSL stylesheet to XML request/response.
- **MessageLogging**: log to Syslog, Cloud Logging, or Sumo Logic; can log asynchronously (post-response, no latency impact).
- **RaiseFault**: generate a custom error response (HTTP status, body, headers) from a policy; used in fault rules.
- **KeyValueMapOperations**: read/write from Key-Value Maps (KVM) — per-organization or per-environment persistent key-value store; use for runtime configuration, secrets, shared data.

### Extension
- **ServiceCallout**: make a synchronous HTTP callout to an external service (Cloud Run, internal API, third-party) mid-flow; use the response in subsequent policies.
- **JavaCallout**: execute Java code within the proxy flow for complex transformations or integrations not achievable with built-in policies.
- **JavaScript**: execute JavaScript (Rhino engine) for lightweight data manipulation, conditional logic.
- **Python**: execute Python scripts (Jython) for scripting needs.
- **FlowCallout**: call a shared flow (reusable set of policies) from a proxy flow.

### Shared Flows
Reusable policy bundles (e.g., standard authentication + logging flow) that can be called from multiple proxies via FlowCallout. Changes to the shared flow apply to all proxies using it — avoids policy duplication.

---

## Analytics

Apigee provides built-in analytics dashboards (no configuration required):
- **API Metrics dashboard**: total traffic, error rate, latency percentiles, cache hit rate per proxy.
- **Developer Engagement**: traffic by developer app, API product.
- **Traffic Composition**: breakdown by status code, proxy, target, verb.
- **Error Analysis**: 4xx and 5xx error breakdown by type and proxy.
- **Custom Reports**: build queries over Apigee analytics data (dimensions: proxy, developer, app, country, client IP; metrics: traffic, latency, errors).

**Export to BigQuery**: configure Apigee analytics data export to BigQuery or Cloud Storage for long-term retention and custom BI/ML analysis. Exports are daily snapshots or streaming.

---

## Monetization

Apigee X includes monetization for API providers who want to charge developers for API usage:
- **Rate Plans**: define pricing per API product (flat fee, variable based on call volume, revenue share).
- **Billing Documents**: generate invoices for developer apps.
- **Developer Accounts**: developers add payment details; Apigee charges based on rate plan.
- Use case: building a public API marketplace where third-party developers pay per API call.

---

## Apigee vs Cloud Endpoints vs API Gateway

| Criterion | Apigee X | Cloud Endpoints | API Gateway |
|---|---|---|---|
| Target audience | Enterprise API programs, external developers | Developers building GCP-hosted APIs | Lightweight HTTP API gateway for serverless |
| Setup complexity | High (org, env, proxies, portal) | Medium (OpenAPI YAML, deploy ESP) | Low (OpenAPI YAML, gateway resource) |
| Policy richness | 50+ policies, shared flows, KVM, monetization | Auth (API key, JWT), logging, tracing | Auth (API key, JWT), rate limiting |
| Developer portal | Yes (built-in) | No (manual documentation) | No |
| Analytics | Built-in dashboards + BigQuery export | Google Cloud Monitoring metrics | Google Cloud Monitoring metrics |
| Monetization | Yes | No | No |
| Hybrid/on-prem | Yes (Apigee Hybrid) | No | No |
| Cost | Per-call pricing + environment fee | ESP container cost (Cloud Run/GKE) | Per-call pricing |
| Backends | Any HTTP/HTTPS | Cloud Run, GKE, GCE, App Engine | Cloud Run, Cloud Functions, App Engine |

**Decision rule**:
- External API program with developers, quota, portal, monetization → **Apigee X**
- Simple OpenAPI/gRPC API on Cloud Run/GKE with auth + tracing → **Cloud Endpoints**
- Lightweight HTTP API on Cloud Functions/Cloud Run, want a managed gateway → **API Gateway**
