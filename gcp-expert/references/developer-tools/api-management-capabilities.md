# API Management — Capabilities

## Overview

GCP offers a layered set of API management solutions. This file covers the developer-tools-facing aspects: Cloud Endpoints (OpenAPI/gRPC proxy), API Gateway (managed serverless gateway), API key management, and service consumer quotas. See `serverless-integration/apigee-capabilities.md` for enterprise Apigee features.

---

## Cloud Endpoints

Cloud Endpoints is an API management system for APIs hosted on GCP. It uses the **Extensible Service Proxy V2 (ESPv2)**, an Envoy-based proxy that runs as a container sidecar or standalone service alongside your backend.

### How Cloud Endpoints Works

1. **Define your API**: write an OpenAPI 2.0 spec (for REST) or a proto file (for gRPC) with GCP-specific extensions.
2. **Deploy the API spec**: `gcloud endpoints services deploy openapi.yaml` registers the spec with Google's Service Management API, creating a versioned service configuration.
3. **Deploy ESPv2**: run the ESPv2 container alongside your backend. ESPv2 intercepts all incoming requests, validates them against the service configuration, enforces authentication, logs to Cloud Logging, traces to Cloud Trace, and enforces quota.
4. **Configure your DNS**: point `api.endpoints.PROJECT_ID.cloud.goog` (or your custom domain) to the ESPv2 endpoint.

### OpenAPI Extensions for Cloud Endpoints

- **`x-google-backend`**: specify the backend URL when ESPv2 is deployed as a separate service (not sidecar).
  ```yaml
  x-google-backend:
    address: https://my-backend-service.example.com
    jwt_audience: https://my-backend-service.example.com
  ```

- **`x-google-endpoints`**: define the service's endpoint hostname (for custom domains).
  ```yaml
  x-google-endpoints:
  - name: my-api.endpoints.PROJECT_ID.cloud.goog
    allowCors: false
  ```

- **`x-google-quota`**: define quota metrics and limits applied per consumer (per API key or per project).
  ```yaml
  x-google-management:
    metrics:
      - name: "read-requests"
        valueType: INT64
        metricKind: DELTA
    quota:
      limits:
        - name: read-requests-per-minute
          metric: read-requests
          unit: 1/min/{project}
          values:
            STANDARD: 100
  ```

- **`x-google-security`**: define security requirements (API key, Firebase Auth JWT, Google Identity).

### Authentication Options

**API Key**:
```yaml
securityDefinitions:
  api_key:
    type: apiKey
    name: key
    in: query
security:
  - api_key: []
```
API keys are validated against keys created in the API & Services > Credentials console.

**Firebase Auth JWT**:
```yaml
securityDefinitions:
  firebase:
    authorizationUrl: ""
    flow: implicit
    type: oauth2
    x-google-issuer: https://securetoken.google.com/PROJECT_ID
    x-google-jwks_uri: https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com
    x-google-audiences: PROJECT_ID
security:
  - firebase: []
```

**Google Identity (service-to-service)**:
```yaml
securityDefinitions:
  google_id_token:
    authorizationUrl: ""
    flow: implicit
    type: oauth2
    x-google-issuer: https://accounts.google.com
    x-google-jwks_uri: https://www.googleapis.com/oauth2/v3/certs
    x-google-audiences: https://my-api.endpoints.PROJECT_ID.cloud.goog
```

### gRPC APIs with Cloud Endpoints

For gRPC backends, define the API using a **proto file** with a corresponding **service configuration YAML**:

```yaml
# api_config.yaml
type: google.api.Service
config_version: 3
name: my-grpc-api.endpoints.PROJECT_ID.cloud.goog
title: My gRPC API
apis:
  - name: my.package.MyService
usage:
  rules:
    - selector: "*"
      allow_unregistered_calls: false
authentication:
  providers:
    - id: google_service_account
      jwks_uri: https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT
      issuer: YOUR_SERVICE_ACCOUNT
  rules:
    - selector: "*"
      requirements:
        - provider_id: google_service_account
backend:
  rules:
    - selector: "*"
      address: grpc://my-grpc-backend.internal:50051
```

Deploy: `gcloud endpoints services deploy proto-descriptor-set.pb api_config.yaml`

### ESPv2 Deployment on Cloud Run

When deploying ESPv2 as a separate Cloud Run service fronting a backend Cloud Run service:
- ESPv2 handles TLS, auth, logging, quotas.
- The backend Cloud Run service is private (no direct external access).
- ESPv2 authenticates to the backend Cloud Run service using a service account with `roles/run.invoker`.

### Monitoring and Logging

Cloud Endpoints automatically sends the following to GCP observability tools:
- **Cloud Logging**: every request logged with method, path, status code, latency, request/response sizes, API key, authenticated user.
- **Cloud Trace**: distributed traces with spans for each ESPv2 request.
- **Cloud Monitoring**: API metrics available in Endpoints dashboard (request count, error rate, latency percentiles, quota usage).

---

## API Gateway

API Gateway is a fully managed API gateway service. Unlike Cloud Endpoints (which requires running ESPv2), API Gateway is serverless — Google manages all the proxy infrastructure.

### Key Features

- **No container to manage**: upload an OpenAPI spec; Google provisions and scales the gateway.
- **OpenAPI 2.0 support**: define routes, backends, and security in a YAML spec.
- **Multiple backends per spec**: different routes in the same spec can point to different Cloud Run services, Cloud Functions, or App Engine backends.
- **Authentication**: API keys, Firebase Auth JWT, Google Identity (OAuth2), Auth0, Okta (any OIDC provider configurable via `x-google-backend` authentication settings).
- **Cloud Logging**: all requests logged automatically.
- **Cloud Monitoring**: request count, latency, and error metrics.
- **Rate limiting**: per-consumer quota via `x-google-quota` extension (same as Cloud Endpoints).

### API Gateway Concepts vs Cloud Endpoints

| Aspect | Cloud Endpoints | API Gateway |
|---|---|---|
| Proxy | ESPv2 (Envoy) container you manage | Google-managed, serverless |
| gRPC | Yes (native gRPC + REST transcoding) | No (REST only) |
| WebSocket | Yes (via Envoy) | No |
| Custom middleware | Yes (via Envoy filters, if customized) | No |
| Latency | Very low (sidecar path) | Low-medium (managed hop) |
| Pricing | Only compute for ESPv2 container | Per API call |

### API Gateway vs Apigee

| Aspect | API Gateway | Apigee X |
|---|---|---|
| Developer portal | No | Yes |
| Policy library | Basic auth + quota | 50+ enterprise policies |
| Analytics | Cloud Monitoring metrics | Built-in dashboards + BigQuery export |
| Monetization | No | Yes |
| Hybrid/on-prem | No | Yes (Apigee Hybrid) |
| Price | Per million calls | Per-call + environment fee |

---

## API Keys Management

GCP API keys are simple string credentials used by client applications to identify themselves to GCP APIs and Cloud Endpoints/API Gateway APIs. Unlike OAuth tokens, they do not represent a user identity.

### Creating and Managing API Keys

API keys are created in the **APIs & Services > Credentials** console page, or via the `gcloud alpha services api-keys` command group.

**Key restrictions**: API keys should always be restricted to:
- **Application restrictions**: HTTP referrers (web apps), IP addresses (server-to-server), Android/iOS app signatures.
- **API restrictions**: limit the key to specific APIs (e.g., only `Maps JavaScript API` or your Cloud Endpoints service).

### API Key Use Cases

- Identifying a web or mobile client application to a public API.
- Rate limiting and quota enforcement per client app.
- Tracking usage by application.

### API Key Limitations

- API keys do not authenticate a user — they identify an application, not a person.
- Do not use API keys for server-to-server calls where service account credentials (OAuth 2.0) are more appropriate.
- Do not embed API keys in source code repositories (use Secret Manager or build-time injection).

---

## Service Consumer Quotas

GCP APIs have quotas (limits on API call rates or resource usage) that protect the platform from overuse and ensure fair sharing. Two types:

### System Quotas (GCP-managed)
Google defines default quotas per API per project. Examples:
- Compute Engine: 800 CPUs per region per project.
- Cloud Run: 1000 services per project per region.
- Firestore: 10,000 reads/second per database.

Request quota increases via the Quotas console (`IAM & Admin > Quotas`).

### Custom API Quotas (Cloud Endpoints / API Gateway)

When you build an API with Cloud Endpoints or API Gateway, you can define per-consumer quotas in the service configuration. These quotas limit how many requests a specific consumer (API key or project) can make to your API.

**Consumer quota groups**:
- Per API key: `1/min/{api_key}` — 1000 requests per minute per unique API key.
- Per project: `1/min/{project}` — 1000 requests per minute per consumer GCP project.

**Quota override**: grant specific consumers a higher quota limit via the Service Management API or `gcloud` (`gcloud services quota override`).

**Quota monitoring**: use Cloud Monitoring to alert when a consumer approaches their quota limit.

---

## API Version Management Patterns

### URL Path Versioning
Most common approach. Version in the URL path: `/v1/users`, `/v2/users`.
- Clients choose their version explicitly.
- Multiple versions can coexist.
- In Cloud Endpoints: use multiple path prefixes in the OpenAPI spec; route to different backend services.
- In API Gateway: use `x-google-backend` at the path level to route v1 and v2 to different Cloud Run services.

### Header Versioning
Version specified in a request header (e.g., `API-Version: 2`). Less visible than URL versioning; harder to route in API Gateway/Endpoints without custom ESPv2 configuration.

### Deprecation Strategy
1. Introduce v2 alongside v1.
2. Document the deprecation timeline.
3. Add `Deprecation` and `Sunset` HTTP headers to v1 responses indicating the end-of-life date.
4. Monitor v1 traffic; notify active consumers.
5. After the sunset date, return `410 Gone` from v1 endpoints.
