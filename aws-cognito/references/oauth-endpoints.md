# OAuth 2.0 / OIDC Endpoint Reference

The full parameter, error, and behavior reference for the user pool authorization server. For the common sign-in **flow** walkthrough (redirect → code → token), see [managed-login.md](managed-login.md#authorization-code-flow); this file is what you consult for advanced params (`prompt`, `resource`), debugging error responses, the `userInfo` scope mapping, and the OIDC issuer choice. Token **verification** is in [backend.md](backend.md#verifying-jwts).

## Table of Contents
1. [OIDC issuer: original vs. updated](#oidc-issuer-original-vs-updated)
2. [/oauth2/authorize parameters](#oauth2authorize-parameters)
3. [/oauth2/token](#oauth2token)
4. [/oauth2/userInfo](#oauth2userinfo)
5. [/oauth2/revoke](#oauth2revoke)
6. [PKCE precisely](#pkce-precisely)
7. [Error responses](#error-responses)

---

## OIDC issuer: original vs. updated

The `iss` claim / discovery base has two forms:

| | **Original** (default) | **Updated** (recommended) |
|---|---|---|
| Format | `https://cognito-idp.<region>.amazonaws.com/<poolId>` | `https://issuer-cognito-idp.<region>.amazonaws.com/<poolId>` |
| JWKS | Region-local | **multi-Region** (resilient; required for [multi-Region replication](multi-region.md)) |
| Caveat | — | **Not compatible with ALB authentication or API Gateway Cognito authorizers** |

Discovery + JWKS live at the **API host**, not your custom domain: `<issuer>/.well-known/openid-configuration` and `/.well-known/jwks.json`. Point OIDC libraries at discovery so an issuer/domain change is picked up automatically — but if you use ALB auth or an API Gateway Cognito authorizer, stay on the **original** issuer.

## /oauth2/authorize parameters

`GET` only, browser-only. Beyond the basics in [managed-login.md](managed-login.md#authorization-code-flow) (`response_type`, `client_id`, `redirect_uri`, `scope`, `state`, `code_challenge`), these are worth knowing:

- **`identity_provider`** — bypass the Cognito page, go straight to an IdP (`COGNITO`, `Google`, `Facebook`, `LoginWithAmazon`, `SignInWithApple`, or your SAML/OIDC provider name). **`idp_identifier`** — same, via a configured alias.
- **`login_hint`** — pre-fill the username field; **forwarded to OIDC IdPs** but *not* to SAML/Apple/Amazon/Google/Facebook.
- **`prompt`** (managed login v2 only) — control existing-session behavior:
  - **`none`** — silent SSO: if a valid session cookie exists, return a code with no UI; else redirect back with **`error=login_required`**. This is how you silently obtain fresh tokens / SSO across app clients in the same pool.
  - **`login`** — force re-authentication even with a session (issues a *new* cookie; doesn't invalidate the old session).
  - **`select_account`** / **`consent`** — no effect on local sign-in; forwarded to the IdP.
  - Combine with spaces: `prompt=login consent`.
- **`resource`** — bind the access token to an API ([resource binding](backend.md#machine-to-machine)); sets the `aud` claim. Value must be `https://`, `http://localhost`, or a custom scheme.
- **`nonce`** — echoed into the ID token for replay protection. **`lang`** — managed-login localization.

**`state` can't be a raw URL-encoded JSON string** — base64-encode it first (same rule on `/logout`). Authorization **codes are valid 5 minutes** and are single-use.

## /oauth2/token

`POST` only, `application/x-www-form-urlencoded`. Grant types (`grant_type`): `authorization_code`, `refresh_token`, `client_credentials`. **A refresh token is only ever returned from `authorization_code`** (and re-issued on refresh only with [rotation](tokens.md#refresh-tokens--rotation) on).

**Client authentication** (confidential clients) — two interchangeable methods:
- **`client_secret_basic`** — `Authorization: Basic base64(client_id:client_secret)` header.
- **`client_secret_post`** — `client_id` + `client_secret` in the form body instead.

Public clients send `client_id` in the body and no secret. `aws_client_metadata` (URL-encoded JSON) reaches the pre-token-gen trigger, but **only on `client_credentials`** ([backend.md](backend.md#machine-to-machine)).

**Negative responses** (`HTTP 400`, `{"error": "..."}`):

| error | Cause |
|---|---|
| `invalid_request` | missing/duplicate/malformed param (e.g. `grant_type=refresh_token` with no `refresh_token`) |
| `invalid_client` | client auth failed (bad id/secret) → `HTTP 401` |
| `invalid_grant` | **refresh token revoked**, **code already consumed / nonexistent**, or **the app client lacks read access to an attribute in the requested scope** (e.g. requesting `email` scope but the client can't read `email_verified`) |
| `unauthorized_client` | client not allowed this grant/flow |
| `unsupported_grant_type` | `grant_type` not one of the three |

That third `invalid_grant` cause is a classic head-scratcher — a scope that references an attribute your app client can't read fails the *token exchange*, not the authorize step.

## /oauth2/userInfo

`GET` (or `POST`), `Authorization: Bearer <access_token>`. Returns user attributes bounded by the token's scopes — **the token must carry `openid`**.

| Scope in access token | userInfo returns |
|---|---|
| `openid` | **all** client-readable attributes |
| `openid profile` | the OIDC profile set (`name`, `given_name`, …, `updated_at`) **+ custom attributes** (that the client can read) |
| `openid email` | `email`, `email_verified` |
| `openid phone` | `phone_number`, `phone_number_verified` |

- **`aws.cognito.signin.user.admin` has no effect here** — and **access tokens from SDK sign-in (`InitiateAuth`) carry no scopes, so userInfo rejects them.** Only tokens from `/oauth2/token` work.
- `email_verified` / `phone_number_verified` come back as **strings** (`"true"`), not booleans.
- Errors: `invalid_request` (400); **`invalid_token` (401)** = access token expired, revoked, or the user globally signed out.

## /oauth2/revoke

`POST`, form-encoded. `token` = the **refresh token** (+ optional `client_id` for public clients, or Basic auth for confidential). Revokes the refresh token **and all access/ID tokens descended from it** ([full semantics in tokens.md](tokens.md#revocation--sign-out)).

- **Revoking an already-revoked or otherwise-invalid token returns `HTTP 200`** (idempotent — don't treat 200 as "was live").
- A non-refresh token → `unsupported_token_type` (400); revocation disabled on the client → `invalid_request` (400); bad client creds → `invalid_client` (401).

## PKCE precisely

Required for public clients ([web-frontend.md](web-frontend.md#raw-oauth-redirect) has a browser skeleton):

1. `code_verifier` = a cryptographically-random string (43–128 chars; AWS's example uses 128).
2. `code_challenge` = **base64url(SHA-256(verifier))** with `=` padding stripped.
3. Send `code_challenge` + `code_challenge_method=S256` to `/authorize`; send the plaintext `code_verifier` to `/token`.

**Cognito supports `S256` only — not `plain`.** Supplying `code_challenge` without `code_challenge_method`, or a method other than `S256`, is rejected as `invalid_request` at the authorize endpoint.

## Error responses

Managed login / federation errors come back **on the `redirect_uri`** as query params: `?error=<name>&error_description=<text>`.

- Authorize-endpoint error names: `invalid_request`, `unauthorized_client` (client can't use that `response_type`), `invalid_scope`, `server_error` (an HTTP 500 that never reaches the browser directly), `login_required` (from `prompt=none`).
- **IdP errors are relayed** with the provider name + HTTP status appended (e.g. `error_description=Google+Error+-+400+...`), including timeouts calling the IdP `/token` or `jwks_uri`. Cognito only relays what OIDC/OAuth IdPs return; **SAML IdP errors are *not* surfaced this way** (Cognito makes no outbound call to a SAML IdP).
- **Don't parse `error_description`** — the strings aren't stable. Log the full URL and page for support; branch only on `error`.
</content>
