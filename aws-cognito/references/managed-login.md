# Managed Login & Hosted UI (OAuth 2.0)

Cognito-hosted sign-in pages and the OAuth/OIDC endpoints they expose. Required for social/SAML/OIDC federation and for passkeys. For building your own UI instead, see [auth-flows.md](auth-flows.md).

## Table of Contents
1. [Managed login vs. classic hosted UI](#managed-login-vs-classic-hosted-ui)
2. [Domains](#domains)
3. [OAuth endpoints](#oauth-endpoints)
4. [Authorization code flow (step by step)](#authorization-code-flow)
5. [Logout](#logout)
6. [Federated / direct-IdP sign-in](#federated-sign-in)
7. [Localization & terms documents](#localization--terms-documents)
8. [Gotchas](#gotchas)

---

## Managed login vs. classic hosted UI

Both are Cognito-hosted pages activated by adding a **domain**. They share the same OAuth endpoints.

| | Managed login (v2) | Hosted UI (classic) |
|---|---|---|
| Branding | No-code visual editor, dark mode, backgrounds | Logo + limited CSS file |
| Passkeys / WebAuthn | ✓ | ✗ |
| Passwordless OTP | ✓ | ✗ |
| Localization | ✓ (Essentials+) | ✗ |
| Feature plan | Essentials or Plus | any (only option on Lite) |

Set the branding version on the domain (`--managed-login-version 2` for managed login, `1` for classic). Switching versions logs everyone out.

## Domains

A prefix domain (`<prefix>.auth.<region>.amazoncognito.com`, instant) or a custom domain you own (ACM cert in us-east-1 + CloudFront + DNS). All app clients in the pool serve pages on the domain. Full setup — custom-domain DNS/ACM/CloudFront prerequisites, the domain-hierarchy cookie trap, running both domains, cert rotation — is in **[domains.md](domains.md)**.

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id "$POOL_ID" --domain myapp-auth --managed-login-version 2
```

## OAuth endpoints

Base = your domain. These are standard OAuth 2.0 / OIDC:

| Endpoint | Purpose |
|---|---|
| `GET /oauth2/authorize` | Start sign-in; returns a code (or token for implicit) |
| `POST /oauth2/token` | Exchange code (or refresh token, or client creds) for tokens |
| `GET /oauth2/userInfo` | User attributes for a valid access token |
| `GET /logout` | Clear the Cognito session cookie, redirect out |
| `POST /oauth2/revoke` | Revoke a refresh token |
| `GET /.well-known/openid-configuration` | OIDC discovery document |
| `GET /.well-known/jwks.json` | Public signing keys (at the `cognito-idp` API host, not the domain) |

App-client OAuth settings must permit what you request: `--allowed-o-auth-flows code`, `--allowed-o-auth-scopes openid email profile`, `--allowed-o-auth-flows-user-pool-client`, and matching `--callback-urls` / `--logout-urls`.

**Interactive UI pages** (browser-only, activated by the domain; you can't call them programmatically): `/login`, `/logout`, `/signup` (same params as `/authorize`), `/forgotPassword` → `/confirmforgotPassword`, `/confirm` → `/resendcode`, `/confirmUser` (email-link verification landing), and `/passkeys/add` (**managed-login v2 only**). Most are redirect-only internal steps; originate every session at `/oauth2/authorize`, not these paths. All endpoints accept **IPv4 and IPv6**.

**Best practice: use OIDC auto-discovery.** Point your OIDC library at `/.well-known/openid-configuration` and let it discover the authorize/token/jwks endpoints, rather than hardcoding them. The discovery path isn't tied to your domain string, so if you later change the user pool domain, auto-discovering clients pick it up automatically. Prefer a certified OIDC relying-party library.

For the **full endpoint reference** — every `/authorize` parameter (`prompt` for silent SSO, `login_hint`, `resource`), token-endpoint grant types & error codes, the `userInfo` scope→claim map, revoke semantics, PKCE precision, the OIDC error catalog, and the **original-vs-updated issuer** choice — see [oauth-endpoints.md](oauth-endpoints.md).

## What the pages show (config-driven)

You **can't edit managed login fields directly** — the user pool + app client configuration determines what appears:
- **Sign-in identifiers** (pool) — which username formats the sign-in form accepts (email-only pool ⇒ email-only field).
- **Required attributes** (pool) — which fields the sign-up form prompts for.
- **Choice-based sign-in options** (pool) — whether passkey / email-OTP / SMS-OTP appear (needs a managed-login domain and a plan above Lite).
- **MFA** (pool) — required ⇒ pages prompt to set up + complete MFA; off/optional ⇒ no prompt.
- **Account recovery** (pool) — whether a "forgot password" link shows.
- **Assigned IdPs + auth methods** (app client) — which IdP buttons and which local methods render. An IdP must be *enabled on the app client* to appear.

## Authorization code flow

The recommended flow for web apps (use **PKCE** for SPAs/public clients; a client secret for confidential server apps).

**1. Redirect the user to `/authorize`:**
```
https://<domain>/oauth2/authorize
  ?response_type=code
  &client_id=<clientId>
  &redirect_uri=https://app.example.com/callback   # must be in callback-urls
  &scope=openid+email+profile
  &state=<csrf-random>
  &code_challenge=<base64url(sha256(verifier))>     # PKCE (public clients)
  &code_challenge_method=S256
```

**2. Cognito redirects back with a code:**
```
https://app.example.com/callback?code=<authCode>&state=<csrf-random>
```
Validate `state` matches what you sent.

**3. Exchange the code at `/token`:**
```bash
# Public client (PKCE, no secret):
curl -X POST https://<domain>/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d "client_id=$CLIENT_ID" \
  -d 'redirect_uri=https://app.example.com/callback' \
  -d "code=$CODE" \
  -d "code_verifier=$VERIFIER"

# Confidential client (secret via HTTP Basic):
curl -X POST https://<domain>/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d 'grant_type=authorization_code' \
  -d 'redirect_uri=https://app.example.com/callback' \
  -d "code=$CODE"
```
Response: `{ id_token, access_token, refresh_token, expires_in, token_type }`. Then **verify** the tokens ([backend.md](backend.md)).

**4. Refresh later:**
```bash
curl -X POST https://<domain>/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "grant_type=refresh_token&client_id=$CLIENT_ID&refresh_token=$RT"
```

Grant types by client:
- **SPA / mobile (public)** → authorization code **+ PKCE**. Never implicit (`response_type=token`) — deprecated and leaks tokens in the URL.
- **Server-rendered web (confidential)** → authorization code + secret.
- **Service-to-service** → `client_credentials` (see [backend.md](backend.md)).

## Logout

Redirect to `/logout` to clear Cognito's session cookie:
```
https://<domain>/logout?client_id=<clientId>&logout_uri=https://app.example.com/signed-out
```
`logout_uri` must be in the app client's `--logout-urls`. A `/logout` request requires **either** `logout_uri` **or** `redirect_uri`:
- **`logout_uri`** → sign out and redirect to a static sign-out page (needs `client_id`).
- **`redirect_uri` + `response_type`** (+ `client_id`/`scope`/`state`) → sign out **and immediately bounce to `/login`** to re-authenticate — here `redirect_uri` is the *post-sign-in* callback, not a sign-out page. Handy for "switch user."
- **If you pass both, `logout_uri` wins** and `redirect_uri` is ignored.
- `state` can't be a URL-encoded JSON string — base64-encode it first (applies to `/authorize` too).

Caveats: logout does **not** sign the user out of the external **OIDC/social IdP** — redirect them to that provider's own logout too. For **SAML** with single-logout configured, Cognito routes through `saml2/logout` first ([saml.md](saml.md)). And logging out does **not** invalidate already-issued JWTs — they remain valid until `exp`; to kill sessions immediately, revoke the refresh token and keep access-token lifetimes short.

## Federated sign-in

To send a user straight to an external IdP (skip the Cognito page), add `identity_provider` to `/authorize`:
```
https://<domain>/oauth2/authorize?identity_provider=Google&response_type=code&client_id=<id>&redirect_uri=<cb>&scope=openid+email+profile
```
The provider must be configured on the pool and listed in the client's `--supported-identity-providers`. IdP setup: [social-providers.md](social-providers.md). The provider's own callback in Cognito is always `https://<domain>/oauth2/idpresponse`.

## Localization & terms documents

- **Localization** (Essentials+, managed login only): add `lang=<code>` to the `/authorize` URL; Cognito then sets a `lang` cookie so the choice persists. 13 languages (`de en es fr id nl it ja ko pt-BR zh-CN zh-TW`). The user's choice isn't passed to custom email/SMS sender triggers — infer language there from the `locale` attribute or app client instead.
- **Terms documents:** configure a **Terms of use** *and* a **Privacy policy** URL (per-language, via `CreateTerms`) and the sign-up page renders "By signing up, you agree to our Terms of use and Privacy policy." **Both** must be set or neither shows.

## Gotchas

- **The 1-hour session cookie.** After interactive sign-in Cognito sets a cookie; re-hitting `/authorize` within an hour silently re-issues tokens without prompting. It does not extend on use.
- **iOS "block all cookies" breaks managed login** — the pages are cookie-based (`XSRF-TOKEN`, `csrf-state`, `cognito`, `lang`, `page-data`). For users who might disable cookies, build native auth with an AWS SDK instead.
- **A programmatically-created app client has no branding** — managed login is unavailable for it until you call `CreateManagedLoginBranding` (console-created clients get a default style automatically). Full styling (branding editor + classic CSS, asset/size limits, API workflow): [branding.md](branding.md).
- **No custom CORS.** Managed login returns `Access-Control-Allow-Origin: *` on `/token`, `/revoke`, `/userInfo` only; implement CORS in your app, not Cognito.
- **`redirect_uri` must match exactly** (scheme, host, path, trailing slash) an entry in `--callback-urls`, or you get `redirect_mismatch`.
- **Managed login can't do custom auth** (Lambda challenge) flows — those are SDK-only.
- **Managed login handles sign-up/in/MFA/password reset only** — not profile edits or MFA-preference changes; build those in your app.
- **TLS 1.2 required** for managed login on both prefix and custom domains.
- **Don't pin TLS certificates.** AWS rotates the leaf/intermediate certs for Cognito domains without notice — pinning a leaf or intermediate will break your app. If you must pin, pin the [Amazon root CAs](https://www.amazontrust.com/repository/) instead.
