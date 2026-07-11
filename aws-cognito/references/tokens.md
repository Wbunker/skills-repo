# Tokens Deep-Dive (Claims, Refresh, Revocation, Caching)

The full token lifecycle beyond the summary in [concepts.md](concepts.md#tokens). JWT **verification** code lives in [backend.md](backend.md#verifying-jwts); token **storage** in the browser is in [web-frontend.md](web-frontend.md#token-storage--security). This file covers claim reference, refresh-token rotation, revocation semantics, and caching/rate-limit strategy.

## Table of Contents
1. [Claim reference (ID vs. access)](#claim-reference)
2. [Two signing keys — a verification gotcha](#two-signing-keys)
3. [The 1-hour managed-login cookie floor](#managed-login-cookie-floor)
4. [Refresh tokens & rotation](#refresh-tokens--rotation)
5. [Revocation & sign-out](#revocation--sign-out)
6. [Caching & rate limits](#caching--rate-limits)

---

## Claim reference

Both ID and access tokens are RS256 JWTs (`header.payload.signature`, header = `{kid, alg:"RS256"}`). Shared claims: `sub`, `iss`, `token_use`, `auth_time`, `exp`, `iat`, `jti`, `origin_jti`, `cognito:groups`.

| Claim | ID token | Access token | Notes |
|---|---|---|---|
| `token_use` | `id` | `access` | **Always check this** — an ID token must never authorize an API |
| audience | `aud` = app client id | `client_id` = app client id | Same value, different claim name |
| `scope` | — | ✓ | OAuth scopes; drives API/userInfo/self-service authorization |
| `username` | `cognito:username` | `username` | Not unique — never key on it |
| `sub` | ✓ | ✓ | Stable UUID-ish id; **don't strictly validate its format** (not RFC-UUID) |
| `email`, custom attrs | ✓ | — | Identity data lives in the **ID** token only |
| `cognito:roles`, `cognito:preferred_role` | ✓ | — | From group IAM roles (identity-pool role selection) |
| `identities` | ✓ | — | Array of linked federated profiles (provider, userId, dateCreated) |
| `nonce` | ✓ | — | Replay guard; echoes the `authorize` request param (auto-generated for third-party IdP sign-in) |
| `device_key` | — | ✓ | Present when device remembering is on |
| `version` | — | `2` | Access-token schema version |
| `aud` (access) | — | optional | The API URL — **only** present if the app requested a resource-server [resource binding](backend.md#machine-to-machine) |

- **Custom attributes** (`custom:` prefix) appear in the **ID token** only, written **as strings** regardless of type.
- **Access tokens from Cognito API sign-in** (not the OAuth token endpoint) carry only the `aws.cognito.signin.user.admin` scope. Only tokens from the token endpoint can carry your custom/resource scopes.
- The `aws.cognito.signin.user.admin` scope = permission to read/write attributes, list auth factors, set MFA prefs, manage devices — bounded by the app client's attribute read/write permissions ([attributes.md](attributes.md#attribute-permissions-per-app-client)).
- Add custom claims / scopes at runtime with a [pre token generation trigger](lambda-triggers.md) (access-token customization needs Essentials/Plus).

## Two signing keys

**Cognito signs ID and access tokens with *different* keys.** Each pool has two RSA key pairs; the `kid` in an access token won't match the `kid` in the ID token from the same session. Both keys are published at the same `jwks.json`. Implication: **verify each token type independently** — don't assume one `kid` or cache lookup covers both. (`aws-jwt-verify` and `PyJWKClient` handle this automatically by matching `kid` per token.) Keys can rotate — cache by `kid` and refresh on a miss.

Expiry can be checked without decoding: an access token with the `aws.cognito.signin.user.admin` scope returns an error from `GetUser` or the `userInfo` endpoint once expired.

## Managed-login cookie floor

**Managed login sets a browser session cookie valid for 1 hour.** Setting ID/access token lifetimes *below* 1 hour does **not** shorten this — a user whose tokens expire mid-hour can silently refresh (or re-authenticate) with no credential prompt until the cookie expires. So a "5-minute token" is not a 5-minute session for managed-login users. Custom-app (SDK) token refresh does **not** renew this cookie, and the cookie doesn't auto-expire on sign-out — after `GlobalSignOut` you must redirect managed-login users to the [Logout endpoint](managed-login.md) to clear it, or they can re-establish a session from the still-valid cookie.

## Refresh tokens & rotation

Refresh tokens are **opaque/encrypted** (not JWTs). Default lifetime **30 days**, configurable **60 minutes–10 years** per app client. Three ways to redeem one for new ID+access tokens:

| Method | When | Notes |
|---|---|---|
| `GetTokensFromRefreshToken` | rotation **on** or off | The modern API; also returns a new refresh token when rotation is on |
| `InitiateAuth`/`AdminInitiateAuth` `REFRESH_TOKEN_AUTH` | rotation **off only** | Legacy flow; **incompatible with rotation** |
| OAuth token endpoint `grant_type=refresh_token` | either | Needs a domain; returns a new refresh token when rotation is on |

- Confidential clients (with a secret) must send `SECRET_HASH` (API flows) or HTTP Basic auth (token endpoint).
- With **device remembering** on ([devices.md](devices.md)), you must pass the `device_key` in `GetTokensFromRefreshToken`; if the user has none, Cognito issues one you must then reuse.
- You can pass `ClientMetadata` through `GetTokensFromRefreshToken` to the pre-token-generation trigger.

### Refresh token rotation

**Security best practice — enable it.** Each successful refresh invalidates the old refresh token and issues a brand-new one alongside the new ID+access tokens. Configure per app client:

```json
"RefreshTokenRotation": { "Feature": "ENABLED", "RetryGracePeriodSeconds": 10 }
```

- `RetryGracePeriodSeconds` (0–60) keeps the rotated-out token briefly valid so an in-flight retry doesn't fail.
- **Rotation is incompatible with `REFRESH_TOKEN_AUTH`** — you must disable that flow on the app client and refresh exclusively via `GetTokensFromRefreshToken`.
- Enabling rotation (like enabling revocation) adds `jti`/`origin_jti` to ID+access tokens, enlarging them.

## Revocation & sign-out

| Operation | Auth | Scope of effect |
|---|---|---|
| `RevokeToken` / `/oauth2/revoke` endpoint | client id (+secret if any) | The given refresh token + **all** ID/access tokens it issued (incl. the initial ones). Other refresh tokens untouched. |
| `GlobalSignOut` | user's **access token** | **All** of that user's refresh/ID/access tokens. Self-service ("sign out everywhere"). |
| `AdminUserGlobalSignOut` | **IAM** credentials | All of a target user's tokens. Admin can sign out anyone. |
| `AdminDisableUser` | IAM | Revokes tokens **and** blocks sign-in ([user-management.md](user-management.md#find--manage-users)) |

**The critical gotcha:** revocation only stops a token from working on **Cognito API calls** (`GetUser`, refresh, etc.). A revoked **access token still passes signature + expiry verification in any JWT library** — so *your own resource server keeps accepting it until it expires*. Revocation is not a kill-switch for tokens your API validates offline. Defenses: keep access-token lifetimes short (15–60 min); for immediate cutoff, check a revocation/deny list server-side rather than relying on Cognito revocation alone.

Other facts:
- **Token revocation is enabled by default** on new app clients (console/CLI/API). It's a prerequisite for `RevokeToken`/`GlobalSignOut` to work; enabling it adds `jti`/`origin_jti`.
- Revoking a refresh token does **not** affect the user's *other* refresh tokens (i.e. their other device sessions) — only `GlobalSignOut`/`AdminUserGlobalSignOut` hit everything.
- Disabling revocation later does **not** un-revoke already-revoked tokens; re-enabling a disabled user doesn't reactivate its revoked tokens.
- The revoke endpoint is available once the pool has a [domain](domains.md) (Cognito-hosted or custom).

## Caching & rate limits

Cognito rate-limits token issuance; the token endpoint (OAuth) and service endpoints (`InitiateAuth`, etc.) have **separate** [quotas](quotas.md). To stay under them:

- **Reuse tokens for ~75% of their lifetime**, then refresh — don't fetch a new token per request. Client apps cache **in memory**; server apps use an **encrypted** cache.
- On throttling, apply **exponential backoff + retry**.
- **M2M caching proxy:** the client-credentials grant is high-volume and easy to rate-limit when microservices scale horizontally on shared credentials. Put **API Gateway in front of `/oauth2/token`** as an HTTP proxy with a cache keyed on the `scope` parameter **+** the `Authorization` header (client id/secret). Set the cache TTL **shorter than the access-token lifetime**. The app only changes its token URL to the API Gateway invoke URL — no app-code logic. (ElastiCache/Redis or DynamoDB work as alternative caches.)
</content>
</invoke>
