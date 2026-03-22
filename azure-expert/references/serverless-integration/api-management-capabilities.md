# Azure API Management — Capabilities Reference
For CLI commands, see [api-management-cli.md](api-management-cli.md).

## Azure API Management (APIM)

**Purpose**: Full-lifecycle API management platform — publish, secure, transform, monitor, and monetize APIs. Acts as a managed API gateway between API consumers (clients) and backend services.

---

## Service Tiers

| Tier | Use Case | VNet | Scale | Notes |
|---|---|---|---|---|
| **Consumption** | Lightweight, serverless | None | Scale to zero, per-call billing | No developer portal, no built-in cache |
| **Developer** | Non-production dev/test | Supported (external/internal) | 1 unit (no SLA) | Full feature set; not for production |
| **Basic** | Entry-level production | External mode only | Up to 2 units | Limited throughput, no multi-region |
| **Standard** | Production workloads | External mode only | Up to 4 units | Moderate throughput, single region |
| **Premium** | Enterprise, multi-region | Internal + external injection | Up to 31 units | Zone redundancy, multi-region, self-hosted gateway |
| **Basic v2** | New tier, faster provisioning | Built-in VNet integration | Auto-scale | Replaces Basic in new deployments |
| **Standard v2** | New tier, faster provisioning | Built-in VNet integration | Auto-scale | Replaces Standard in new deployments |

### VNet Modes (Premium / v2)
| Mode | Description |
|---|---|
| **External** | APIM accessible from internet and VNet; backends in VNet accessible via VNet routing |
| **Internal** | APIM only accessible from within VNet; public internet access blocked; requires internal load balancer |

---

## Core Concepts

| Concept | Description |
|---|---|
| **API** | A set of operations (endpoints) published to consumers; imported from OpenAPI, WSDL, or created manually |
| **Operation** | A single HTTP method + path (e.g., `GET /orders/{id}`) within an API |
| **Product** | A bundle of one or more APIs with a usage plan; consumers subscribe to products |
| **Subscription** | A key-based access grant to a product; subscriptions generate primary + secondary keys |
| **Developer** | A user registered in the developer portal who can subscribe to products |
| **Backend** | The actual service APIM proxies to; can be a URL, Azure Function, App Service, Container Apps, etc. |
| **Named Values** | Key-value store for secrets and configuration (plain text, Key Vault reference, or secret) |
| **Gateway** | The component that processes API requests and applies policies |

---

## Developer Portal

- Fully customizable web portal for API consumers: documentation, try-it console, sign-up, subscriptions
- Auto-generated from API definitions imported into APIM
- Customizable with custom CSS, pages, and widgets via built-in CMS
- Supports Azure AD B2C or Entra ID for developer sign-in
- Can publish as self-managed (host yourself) or Azure-managed
- Consumption tier does not include developer portal

---

## Policy System

Policies are XML-based rules applied to API requests and responses at the gateway. Policies execute in a pipeline: **inbound → backend → outbound → on-error**.

### Policy Scopes (inheritance)
```
Global (all APIs)
  └── Product
        └── API
              └── Operation
```
Lower scopes can inherit (`<base />`) or override parent policies.

### Inbound Policies (request processing)

| Policy | Description |
|---|---|
| `validate-jwt` | Validate JWT token; check issuer, audience, required claims |
| `oauth2-token-validation` | Validate OAuth2 tokens against an authorization server |
| `check-header` | Verify a required HTTP header is present and has expected value |
| `subscription-key-required` | Enforce subscription key (`Ocp-Apim-Subscription-Key` header or `subscription-key` query param) |
| `rate-limit` | Limit calls per subscription per time window (e.g., 100 calls/minute) |
| `rate-limit-by-key` | Rate limit by arbitrary key (IP address, JWT claim, header value) |
| `quota` | Set total call or bandwidth quota per subscription per billing period |
| `quota-by-key` | Quota by arbitrary key |
| `ip-filter` | Allow or deny requests based on caller IP or IP range |
| `rewrite-uri` | Rewrite the request URL path before forwarding to backend |
| `set-header` | Add, modify, or remove request headers |
| `set-query-parameter` | Add, modify, or remove query string parameters |
| `cors` | Handle Cross-Origin Resource Sharing preflight and actual requests |
| `cache-lookup` | Check response cache before forwarding to backend |
| `authentication-basic` | Authenticate to backend with Basic auth |
| `authentication-certificate` | Authenticate to backend with client certificate |
| `authentication-managed-identity` | Authenticate to backend using APIM's managed identity (get token) |
| `mock-response` | Return a mock response without calling the backend (for testing) |

### Outbound Policies (response processing)

| Policy | Description |
|---|---|
| `cache-store` | Store response in cache for subsequent cache-lookup hits |
| `set-header` | Add, modify, or remove response headers |
| `find-and-replace` | String substitution in response body |
| `xml-to-json` | Convert XML response body to JSON |
| `json-to-xml` | Convert JSON response body to XML |
| `redirect-content-urls` | Rewrite URLs in response body (e.g., replace backend hostname with APIM hostname) |

### Backend Policies

| Policy | Description |
|---|---|
| `forward-request` | Forward the request to the backend service (required in backend section) |
| `set-backend-service` | Dynamically change the backend URL or use a named backend |
| `retry` | Retry backend requests on specified HTTP status codes or exceptions |
| `limit-concurrency` | Limit concurrent backend calls |

### Common Policy Patterns

**JWT Validation with Entra ID:**
```xml
<inbound>
  <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
    <openid-config url="https://login.microsoftonline.com/{tenantId}/v2.0/.well-known/openid-configuration" />
    <required-claims>
      <claim name="aud">
        <value>{your-api-app-id-uri}</value>
      </claim>
    </required-claims>
  </validate-jwt>
  <base />
</inbound>
```

**Rate limiting per subscription key:**
```xml
<inbound>
  <rate-limit calls="100" renewal-period="60" />
  <quota calls="1000" renewal-period="86400" />
  <base />
</inbound>
```

**Add backend auth header (managed identity):**
```xml
<inbound>
  <authentication-managed-identity resource="https://management.azure.com/" />
  <base />
</inbound>
```

**Transform JSON response to add/remove fields:**
```xml
<outbound>
  <set-body>@{
    var body = context.Response.Body.As<JObject>();
    body.Remove("internalId");
    return body.ToString();
  }</set-body>
  <base />
</outbound>
```

---

## API Import Formats

| Format | Description |
|---|---|
| **OpenAPI 2.0 (Swagger)** | Import REST API from Swagger JSON/YAML |
| **OpenAPI 3.0** | Import REST API from OpenAPI 3.0 JSON/YAML |
| **WSDL/SOAP** | Import SOAP service; APIM can act as SOAP pass-through or convert SOAP→REST |
| **GraphQL** | Import GraphQL schema; APIM acts as GraphQL gateway |
| **OData** | Import OData service metadata |
| **Azure Functions** | Directly import HTTP-triggered Azure Functions (auto-generates operations) |
| **App Service** | Import from Azure App Service (App Service reads OpenAPI spec) |
| **Logic Apps** | Import HTTP-triggered Logic Apps workflows |
| **Container Apps** | Import from Azure Container Apps (uses app's OpenAPI spec) |

---

## Gateway Options

| Gateway Type | Description | Use Case |
|---|---|---|
| **Managed (cloud)** | Fully Azure-hosted gateway in APIM service region | Standard cloud APIs |
| **Self-hosted gateway** | Containerized gateway deployed on customer infrastructure | On-premises, edge, or arc-connected K8s; keep API traffic local |

### Self-hosted Gateway
- Run as Docker container or Kubernetes deployment
- Connects back to APIM control plane for configuration sync
- Supports all policies except cache (unless external Redis cache configured)
- Kubernetes deployment: use Helm chart from APIM docs
- Use cases: on-premises APIs (avoid exposing backend to internet), low-latency edge scenarios, compliance (data residency)

---

## Multi-region Deployment (Premium)

- Deploy APIM to multiple Azure regions: one primary + N additional regions
- Azure Traffic Manager or Azure Front Door routes traffic to closest APIM gateway
- Each regional gateway independently processes API calls; configurations replicate from primary
- Backends can be regional (different backend URLs per region) or global
- Zone redundancy: within a single region, deploy gateway units across availability zones

---

## Azure API Center

- Catalog and govern all APIs across the organization (not just APIM-managed APIs)
- Register APIs from any source: APIM, custom apps, partners, 3rd-party gateways
- API inventory: versioning, lifecycle stages, environments, definitions
- Governance: compliance checks, API design rules (linting), custom metadata
- Complements APIM — APIM manages the gateway; API Center manages the catalog

---

## Monitoring & Analytics

| Feature | Description |
|---|---|
| **Built-in analytics** | APIM portal dashboard: requests, latency, failures, geography, top APIs, top operations |
| **Azure Monitor** | Metrics (TotalRequests, SuccessfulRequests, FailedRequests, Capacity, Latency) |
| **Application Insights** | Full distributed tracing, custom events, request sampling; configure per API or globally |
| **Resource logs** | GatewayLogs, WebSocketConnectionLogs — route to Log Analytics, Storage, Event Hubs |
| **APIM Inspector** | Per-request trace showing each policy execution step (enable with `Ocp-Apim-Trace: true` header) |

### Useful Log Analytics Queries
```kusto
-- API call failures in last hour
ApiManagementGatewayLogs
| where TimeGenerated > ago(1h)
| where IsRequestSuccess == false
| project TimeGenerated, ApiId, OperationId, ResponseCode, LastError, ClientIp
| order by TimeGenerated desc

-- Top 10 slowest operations
ApiManagementGatewayLogs
| where TimeGenerated > ago(24h)
| summarize AvgLatency = avg(TotalTime), CallCount = count() by ApiId, OperationId
| top 10 by AvgLatency desc
```

---

## Security Best Practices

- Always validate JWT tokens at the gateway using `validate-jwt` policy; never trust unvalidated tokens
- Use Named Values with Key Vault references for all secrets (backend API keys, connection strings)
- Enable managed identity on APIM and use it to authenticate to backends — eliminate static credentials
- Use `ip-filter` policy to restrict management plane access to known CIDR ranges
- Deploy in internal VNet mode (Premium) for APIs that should never be internet-accessible
- Enable Defender for APIs (Microsoft Defender for Cloud) for threat detection and API security posture
- Rotate subscription keys regularly; use dual-key rotation (primary/secondary) for zero-downtime rotation
