# AWS API Gateway — Capabilities Reference
For CLI commands, see [api-gateway-cli.md](api-gateway-cli.md).

## Amazon API Gateway

**Purpose**: Create, publish, maintain, monitor, and secure APIs at any scale. Handles traffic management, authorization, throttling, monitoring, and API versioning.

### API Types Comparison

| Feature | REST API | HTTP API | WebSocket API |
|---|---|---|---|
| **Protocol** | HTTP/S | HTTP/S | WebSocket (RFC 6455) |
| **Latency** | ~6 ms | ~1 ms | N/A |
| **Cost** | Higher | ~70% cheaper than REST | Per message + connection |
| **Lambda proxy** | Yes | Yes | Yes |
| **Lambda non-proxy** | Yes | No | No |
| **HTTP integration** | Yes | Yes | Yes |
| **AWS service integration** | Yes | No | No |
| **Mock integration** | Yes | No | No |
| **Cognito authorizer** | Yes | Via JWT authorizer | No |
| **Lambda authorizer (TOKEN/REQUEST)** | Yes | Yes | Yes |
| **JWT authorizer** | No | Yes | No |
| **Usage plans / API keys** | Yes | No | No |
| **Request validation** | Yes | No | No |
| **Response mapping (VTL)** | Yes | No | No |
| **Caching** | Yes | No | No |
| **Canary deployments** | Yes | No | No |
| **Private API (VPC endpoint)** | Yes | No | No |
| **mTLS** | Yes | Yes | No |
| **CORS** | Manual or automatic | Automatic | No |
| **WebSocket routes** | No | No | $connect / $disconnect / $default / custom |

### Integration Types (REST API)

| Type | Description |
|---|---|
| **Lambda proxy** | Lambda receives full request (headers, body, query params, context); must return a structured response object |
| **Lambda non-proxy (custom)** | VTL mapping templates transform request before Lambda and response after; precise control |
| **HTTP** | Forward to any HTTP endpoint; optionally transform with VTL |
| **AWS service** | Direct integration with AWS services (DynamoDB, SQS, SNS, Kinesis, S3) without Lambda |
| **Mock** | Return a hardcoded response without a backend; useful for CORS preflight, testing, or stub APIs |

### Authorizers

| Authorizer | API type | How it works |
|---|---|---|
| **Cognito User Pool** | REST | Validates Cognito JWT; no Lambda invocation |
| **Lambda TOKEN** | REST | Passes bearer token to Lambda; Lambda returns Allow/Deny policy |
| **Lambda REQUEST** | REST, HTTP | Passes full request context (headers, query params) to Lambda |
| **JWT (OIDC/OAuth 2.0)** | HTTP | Validates JWT against JWKS endpoint; no Lambda invocation |

**Authorizer caching**: Results cached by token or identity source for 0–3,600 seconds (default 300 s).

### Stages and Deployments

- **REST API**: Changes require an explicit deployment to a stage; multiple stages supported (dev, staging, prod)
- **HTTP API**: Auto-deploy option available; creates a new deployment on every change
- **Stage variables**: Key-value pairs available in VTL templates and Lambda ARNs (e.g., point a stage to a different Lambda alias)
- **Canary deployments** (REST): Split traffic between current and canary deployment; promote or rollback independently

### Usage Plans and API Keys (REST only)

- Associate an API key with a usage plan
- Usage plan defines: throttle (requests per second + burst), quota (requests per day/week/month)
- Useful for metering API consumers or enforcing per-customer limits

### Throttling and Quotas

| Limit | Default |
|---|---|
| Account-level (10,000 RPS) | Shared across all APIs in the region |
| Stage-level throttle | Set per stage; overrides account default for that API |
| Method-level throttle | Set per route; overrides stage throttle |

Throttled requests receive HTTP 429.

### Caching (REST API only)

- Enable per-stage; TTL 0–3,600 s (default 300 s)
- Cache size: 0.5 GB – 237 GB
- Clients can invalidate cache with `Cache-Control: max-age=0` header (requires explicit permission)
- Cached by method + query params + headers (configurable)

### Request/Response Mapping Templates (VTL) — REST API

Velocity Template Language (VTL) transforms the request before it reaches the integration and/or transforms the response before returning to the client. Used to:
- Reshape JSON payloads
- Extract query parameters into the integration request body
- Map HTTP status codes from integration responses

### WebSocket API Routes

| Route | Triggered when |
|---|---|
| `$connect` | Client establishes WebSocket connection |
| `$disconnect` | Client or server closes connection |
| `$default` | Message does not match any defined route key |
| Custom route | Message body contains a matching route selection expression value |

### Private APIs

Deploy an API accessible only within a VPC via an Interface VPC Endpoint (`execute-api`). Use resource policy to restrict access to specific VPCs or VPC endpoints.
