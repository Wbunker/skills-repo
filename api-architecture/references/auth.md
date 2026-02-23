# API Authentication and Authorization

This reference covers securing APIs, based on Chapter 7 of *Mastering API Architecture* by James Gough. It addresses verifying identity (authentication), enforcing permissions (authorization), and the protocols and token formats that connect them.

## Authentication vs Authorization

Authentication ("authn") answers *who are you?* Authorization ("authz") answers *what are you allowed to do?*

| Concern        | Question              | Mechanism                         | HTTP Failure |
|----------------|-----------------------|-----------------------------------|--------------|
| Authentication | Who is the caller?    | Tokens, certificates, credentials | 401          |
| Authorization  | Is the action allowed?| Roles, scopes, policies           | 403          |

A common mistake is collapsing both into a single check. When entangled, changing access policies requires modifying identity verification logic. Keep them in separate middleware or gateway layers.

## End-User Authentication with Tokens

### Session Tokens

An opaque identifier issued after login. The server stores session state and looks up the token on each request.

```
POST /login
{"username": "alice", "password": "s3cret"}

HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
```

Well-suited to traditional web apps. Less practical for distributed APIs because every validating service must share the session store.

### Bearer Tokens

A self-contained or reference token presented in the `Authorization` header. Possession alone is sufficient for access.

```
GET /api/orders
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

Bearer tokens (especially JWTs) are the API standard because they require no server-side state. The tradeoff: revocation before expiry needs additional infrastructure (deny lists, short lifetimes with refresh tokens).

### Token Lifecycle

1. **Issuance** -- Authorization server issues a token after successful authentication.
2. **Transmission** -- Over TLS in the `Authorization` header. Never in query strings (URLs are logged).
3. **Validation** -- Resource server verifies signature, expiration, issuer, and audience on every request.
4. **Renewal** -- Short-lived access tokens renewed via refresh tokens without re-authentication.
5. **Revocation** -- Invalidated on logout, credential compromise, or permission changes.

## System-to-System Authentication

### API Keys

A long-lived secret identifying a calling application, not a user.

```
GET /api/weather?city=london
X-API-Key: ak_live_7f3a9b2c4d5e6f7890abcdef12345678
```

Appropriate for server-to-server calls where the calling system is trusted and the key is stored securely.

### Client Certificates (mTLS)

Mutual TLS authenticates both sides at the transport layer. The client presents a certificate signed by a trusted CA.

```
curl --cert client.pem --key client-key.pem https://api.internal.example.com/data
```

The strongest system-to-system mechanism. Common in service meshes (Istio, Linkerd) and zero-trust architectures. Operational cost is certificate lifecycle management via PKI or SPIFFE/SPIRE.

### Service Accounts

An identity representing a machine rather than a human. Authenticates via the OAuth2 client credentials grant and receives tokens scoped to its specific permissions.

## Why You Should Not Mix Keys and Users

API keys and user tokens represent different trust models.

| Property     | API Key                   | User Token                     |
|--------------|---------------------------|--------------------------------|
| Represents   | An application            | A human identity               |
| Granularity  | Coarse (entire app)       | Fine (per-user permissions)    |
| Lifetime     | Long-lived (months/years) | Short-lived (minutes/hours)    |
| Revocation   | Manual rotation           | Automatic expiry, refresh flow |
| Audit trail  | Which app called          | Which user acted               |

When an API key acts on behalf of a user, you lose per-user authorization, individual audit trails, and single-user revocation. API keys identify the application; user tokens identify the person. Never substitute one for the other.

## OAuth2

OAuth2 (RFC 6749) is a delegation framework allowing a user to grant an application limited access to a resource without sharing credentials.

### Authorization Server Role

The central trust anchor: authenticates users, issues tokens, publishes cryptographic keys for validation. It sits outside the request path -- clients obtain tokens before calling resource servers.

```
Client --> Auth Server: "I need access to user's photos"
Auth Server --> User: "Do you approve?"
User --> Auth Server: "Yes"
Auth Server --> Client: access token
Client --> Resource Server: GET /photos (with token)
Resource Server: validates token via Auth Server's public keys
```

### JSON Web Tokens (JWT)

A JWT (RFC 7519) has three Base64URL-encoded parts separated by dots: header, payload, signature.

**Header:**
```json
{"alg": "RS256", "typ": "JWT", "kid": "key-2024-01"}
```

**Payload:**
```json
{
  "iss": "https://auth.example.com",
  "sub": "user_123",
  "aud": "api.example.com",
  "exp": 1716239022,
  "iat": 1716235422,
  "nbf": 1716235422,
  "scope": "read:orders write:orders"
}
```

**Registered claims:** `iss` (issuer), `sub` (subject/principal), `aud` (intended recipient -- always validate), `exp` (expiration), `iat` (issued at), `nbf` (not valid before).

**Signing algorithms:**
- **RS256** (RSA + SHA-256) -- Asymmetric. Most widely supported. Sign with private key, validate with public key.
- **ES256** (ECDSA + SHA-256) -- Asymmetric with smaller keys. Preferred for new systems.
- **HS256** (HMAC + SHA-256) -- Symmetric. Avoid in distributed systems since every validator needs the signing secret.

Always use asymmetric algorithms in production. Fetch public keys from the JWKS endpoint and cache with rotation logic.

### OAuth2 Terminology

- **Resource Owner** -- The user who owns the data and grants access.
- **Client** -- The application requesting access on the user's behalf.
- **Authorization Server** -- Issues tokens after authentication and consent.
- **Resource Server** -- The API that validates access tokens.
- **Scope** -- A permission string (e.g., `read:orders`).
- **Grant** -- The method for obtaining an access token.

### ADR: Should I Consider Using OAuth2?

**Context:** The system requires authenticated API access for external clients, mobile apps, or third-party integrations.

**Decision:** Adopt OAuth2 when multiple client types exist, third-party access is required, or a standardized authorization framework is needed. For purely internal service-to-service communication in a trusted network, mTLS or simpler token schemes may suffice.

**Consequences:** Introduces protocol complexity and requires an authorization server. Provides a proven, interoperable framework with broad library and provider support.

### Authorization Code Grant

The recommended flow for all user-facing clients.

```
1. Client redirects user to Auth Server:
   GET /authorize?response_type=code&client_id=app1
       &redirect_uri=https://app.example.com/callback
       &scope=read:orders&state=xyz
       &code_challenge=E9Melhoa...&code_challenge_method=S256

2. User authenticates and consents.

3. Auth Server redirects back:
   GET /callback?code=SplxlOBeZQQYbYS6WxSbIA&state=xyz

4. Client exchanges code for tokens (server-side):
   POST /token
   grant_type=authorization_code&code=SplxlOBeZQQYbYS6WxSbIA
   &redirect_uri=https://app.example.com/callback
   &client_id=app1&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r...

5. Response:
   {"access_token":"eyJ...","refresh_token":"dGhp...","expires_in":3600}
```

**PKCE (Proof Key for Code Exchange, RFC 7636)** prevents authorization code interception. The client generates a random `code_verifier`, derives a `code_challenge` (SHA-256 hash), and sends the challenge with the auth request. On token exchange, it sends the verifier. The server confirms they match. Now recommended for all clients.

### Refresh Tokens

Access tokens are short-lived (5-60 min). Refresh tokens obtain new access tokens without user interaction.

```
POST /token
grant_type=refresh_token&refresh_token=dGhp...&client_id=app1
```

**Rotation:** Each use issues a new refresh token and invalidates the old one. Reuse of a rotated token triggers revocation of the entire token family (detects theft).

**Storage:** Encrypted server-side sessions for web apps, OS keychain for mobile. Never localStorage.

### Client Credentials Grant

For service-to-service authentication with no user involved.

```
POST /token
Authorization: Basic base64(client_id:client_secret)
grant_type=client_credentials&scope=read:inventory
```

The resulting token represents the service identity, not a user.

### Additional Grants

- **Device Code** (RFC 8628) -- For limited-input devices (smart TVs, CLIs). Device displays a code; user authorizes via browser on a separate device.
- **Implicit** (deprecated) -- Returned tokens in URL fragment. Deprecated in OAuth 2.1 due to leakage risks. Use authorization code with PKCE.
- **Resource Owner Password** (deprecated) -- Client collects user credentials directly. Defeats OAuth2's delegation purpose.

### ADR: Choosing Which OAuth2 Grants to Support

| Client Type                 | Recommended Grant              |
|-----------------------------|--------------------------------|
| Server-side web application | Authorization Code with PKCE   |
| Single-page application     | Authorization Code with PKCE   |
| Native mobile application   | Authorization Code with PKCE   |
| Service-to-service          | Client Credentials             |
| CLI / IoT device            | Device Code                    |

Do not enable implicit or resource owner password grants. Minimize attack surface by enabling only the grants your clients need.

### OAuth2 Scopes

Scopes define access boundaries. Requested by the client, consented to by the user, enforced by the resource server.

**Convention:** `resource:action` -- e.g., `read:orders`, `write:orders`, `admin:users`.

**Granularity:** Start coarse (`orders`) and refine (`read:orders`, `write:orders:own`) as requirements demand. Fine-grained scopes increase token size and consent complexity.

**Enforcement:**
```python
@require_scope("read:orders")
def list_orders(request):
    return Order.objects.filter(owner=request.token.sub)
```

## Authorization Enforcement

### RBAC (Role-Based Access Control)

Users are assigned roles; roles carry permissions.

```json
{"sub": "user_123", "roles": ["order_manager"], "scope": "read:orders write:orders"}
```

Straightforward, but becomes unwieldy when permissions depend on resource attributes (e.g., "managers edit only their department's orders").

### ABAC (Attribute-Based Access Control)

Decisions based on attributes of the subject, resource, action, and environment.

```
ALLOW if subject.department == resource.department
    AND subject.clearance >= resource.classification
    AND environment.time within business_hours
```

More expressive than RBAC but requires a policy engine and attribute availability at decision time.

### Policy Engines

Externalize authorization from application code.

**OPA (Open Policy Agent) with Rego:**
```rego
package orders.authz
default allow = false
allow {
    input.method == "GET"
    input.path == ["api", "orders"]
    "read:orders" == input.token.scope[_]
}
```

**Cedar (AWS):**
```
permit(
    principal in Role::"order_manager",
    action in [Action::"ReadOrder", Action::"CreateOrder"],
    resource in Department::"electronics"
);
```

Policy engines provide auditable, testable, independently deployable authorization logic.

### Where to Enforce

- **API Gateway** -- Token validation, expiration, audience, coarse scope checks. Reject unauthorized requests before they reach backends.
- **Middleware** -- Scope and role checks at the route/controller level. Where most authorization logic lives.
- **Application Layer** -- Fine-grained, business-logic authorization (e.g., "users cancel only their own orders"). Requires domain knowledge the gateway cannot have.

Never rely on a single layer. Defense in depth protects against misconfiguration.

## OpenID Connect (OIDC)

An identity layer built on OAuth2. OAuth2 handles authorization (delegated access); OIDC adds standardized authentication (proving identity).

### ID Token vs Access Token

- **ID token** -- JWT for the client. Contains authentication claims (who, when, how). Used to establish a client-side session.
- **Access token** -- For the resource server. The client treats it as opaque and forwards it to APIs.

Never send the ID token to a resource server. Never use the access token for client-side identity.

### UserInfo Endpoint

Returns claims about the authenticated user:

```
GET /userinfo
Authorization: Bearer eyJ...

{"sub": "user_123", "name": "Alice Smith", "email": "alice@example.com"}
```

### Discovery Document

Published at `/.well-known/openid-configuration`:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "userinfo_endpoint": "https://auth.example.com/userinfo",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "scopes_supported": ["openid", "profile", "email"]
}
```

Clients and resource servers use this for automatic configuration: JWKS URI, endpoints, supported scopes.

### Common Providers

- **Auth0** -- Developer-focused, extensive SDKs, quick integration.
- **Okta** -- Enterprise identity for workforce and customer identity.
- **Keycloak** -- Open-source, self-hosted, full-featured. On-premises control.
- **Azure AD (Entra ID)** -- Microsoft ecosystem, Azure and Office 365 integration.
- **Google Identity** -- Consumer-facing OAuth2/OIDC for Google accounts.

## SAML 2.0

XML-based authentication protocol predating OAuth2/OIDC. Still relevant in enterprise environments with legacy IdPs (ADFS, Shibboleth).

| Aspect          | SAML 2.0                   | OIDC                        |
|-----------------|----------------------------|-----------------------------|
| Token format    | XML assertions             | JSON (JWT)                  |
| Transport       | Browser redirects, POST    | Browser redirects, REST     |
| Complexity      | High (XML, signatures)     | Moderate                    |
| Mobile support  | Poor                       | Native SDK support          |
| API suitability | Low (designed for web SSO) | High (designed for APIs)    |

For new API architectures, prefer OIDC. Use SAML when integrating with existing enterprise infrastructure, and consider a SAML-to-OIDC bridge in front of your APIs.

## API Key Best Practices

- **Rotation** -- Support multiple active keys per client for zero-downtime rotation with a deprecation period.
- **Scoping** -- Minimum permissions per key. Read-only keys should not have write access.
- **Rate limiting** -- Tie limits to keys. Protects against abuse and accidental overuse.
- **Never embed in URLs** -- Query strings appear in logs and browser history. Use `X-API-Key` or `Authorization` headers.
- **Prefix keys** -- `pk_live_`, `sk_test_` prefixes enable identification of leaked keys by type and environment.
- **Monitor** -- Track per-key usage patterns. Alert on anomalies (spikes, unexpected IPs).

## Token Security

**Storage:**
- Server-side web apps: Encrypted server-side sessions. Never expose tokens to the browser.
- SPAs: `httpOnly`, `Secure`, `SameSite=Strict` cookies via a backend-for-frontend (BFF) pattern. Never localStorage.
- Mobile: Platform keychain (iOS Keychain, Android Keystore).

**Transmission:**
- Always TLS. No exceptions.
- `Authorization: Bearer` header only. Not query strings or request bodies.
- Certificate pinning for mobile apps.

**Validation:**
- Verify signature against JWKS public keys.
- Check `exp`, `iss`, `aud` on every request.
- Validate scopes and roles before processing.
- Allow 30-60 second clock skew tolerance for time-based claims.

**Revocation:**
- Short lifetimes (5-15 min) limit stolen-token exposure.
- Immediate revocation via deny lists or token introspection (RFC 7662).
- Revoke refresh tokens on password change, account deactivation, or suspected compromise.
- OAuth2 revocation endpoint (RFC 7009) for proactive client-side invalidation.
