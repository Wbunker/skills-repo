# Cognito Concepts & Terminology

## Table of Contents
1. [User pools vs. identity pools](#user-pools-vs-identity-pools)
2. [Core terminology](#core-terminology)
3. [Tokens](#tokens)
4. [Feature plans (Lite / Essentials / Plus)](#feature-plans)
5. [Threat protection](#threat-protection)
6. [MFA](#mfa)
7. [User attributes & groups](#user-attributes--groups)
8. [Common scenarios](#common-scenarios)

---

## User pools vs. identity pools

They are separate services with separate APIs and independent lifecycles.

| | User pool (`cognito-idp`) | Identity pool (`cognito-identity`) |
|---|---|---|
| Purpose | Authenticate users; a directory + OIDC IdP | Hand out temporary AWS credentials |
| Output | ID / access / refresh **JWTs** | AWS creds from STS |
| API prefix | `aws cognito-idp …` | `aws cognito-identity …` |
| ID format | `us-east-1_XXXXXXXXX` | `us-east-1:uuid` |
| Directory? | Yes (stores users) | No (maps identities to IAM roles) |
| Federation | SAML, OIDC, social → issues its own JWTs | SAML, OIDC, social, **or a user pool** → issues AWS creds |

**Together:** user signs in to the user pool (gets JWTs) → app passes the ID token to the identity pool → identity pool returns AWS creds scoped by an IAM role. Only needed when client code calls AWS services directly.

## Core terminology

- **User pool** — a user directory and authorization server.
- **App client** — per-application config inside a pool: allowed auth flows, OAuth scopes, callback URLs, token lifetimes, optional secret. A pool has many app clients (web, mobile, server). Full configuration reference: [app-clients.md](app-clients.md).
- **App client secret** — for confidential (server-side) clients only. Forces a `SECRET_HASH` on unauthenticated API calls. Never use in browser/mobile.
- **Domain** — a hostname (`prefix.auth.region.amazoncognito.com` or a custom domain) that turns on managed login + OAuth endpoints.
- **Managed login / hosted UI** — Cognito-hosted sign-in pages. Managed login is the modern version (branding editor, passkeys, dark mode); hosted UI (classic) is the older, simpler one.
- **Local user** — created directly in the pool (signed up or admin-created). Authoritative here.
- **Federated user** — signs in through an external IdP; Cognito maps their claims into a local profile + its own JWTs.
- **Linked user** — a federated user whose identity has been *merged* with a local user so they share one profile and `sub` (account linking; see [federation.md](federation.md)).
- **Public app vs. confidential app** — public = self-contained on a device with no secret (SPA/mobile); confidential/server-side = runs on a server and can hold a secret (traditional web). Secret ⇒ `SECRET_HASH` on auth calls.
- **Identity provider (IdP)** — an external source of identity: Google, Apple, Facebook, Amazon, SAML 2.0, or generic OIDC.
- **Scope** — OAuth 2.0 permission string in the access token (`openid`, `email`, `profile`, `aws.cognito.signin.user.admin`, or custom resource-server scopes).
- **Resource server** — a named API with custom scopes you define (e.g. `myapi/read`), so access tokens can authorize your own endpoints.
- **Feature plan / tier** — Lite, Essentials, or Plus; gates features and pricing (see below).

**Distinctions worth pinning down:**
- **Confirmation vs. verification** — *verification* proves a user owns an email/phone (they submit a code sent to it). *Confirmation* is the broader gate that lets a new user sign in (usually accomplished by verification, or done by an admin).
- **Choice-based vs. client-based (declarative) authentication** — choice-based (`USER_AUTH`) offers the user a menu of factors at sign-in (password, OTP, passkey); client-based means your app decides the one flow up front (`USER_SRP_AUTH`, etc.). Only choice-based exposes passwordless/passkeys. See [auth-flows.md](auth-flows.md).
- **Device authentication** — a remembered, trusted device can substitute for the MFA step on later sign-ins.
- **Managed authorization server** — the OIDC/OAuth engine behind both managed login and the classic hosted UI; both share the same `/oauth2/*` endpoints and differ only in the UI/feature set.

## Tokens

All three are returned on sign-in. They are JWTs except the refresh token (opaque/encrypted).

| Token | Use it for | Key claims | Default lifetime |
|---|---|---|---|
| **ID** | Reading user identity in your app UI | `sub`, `email`, `cognito:groups`, `aud`, `token_use:id` | 1 hour (5 min–1 day) |
| **Access** | **Authorizing API calls** | `scope`, `cognito:groups`, `client_id`, `token_use:access` | 1 hour (5 min–1 day) |
| **Refresh** | Getting fresh ID + access tokens | opaque | 30 days (1 hour–10 years) |

- `sub` is the stable, immutable user id. Use it as your DB foreign key, not email/username.
- `cognito:groups` appears in both ID and access tokens.
- Customize claims with a [pre token generation Lambda trigger](lambda-triggers.md).
- Access-token customization (event v2) requires Essentials or Plus.
- Enabling token revocation adds `jti`/`origin_jti` claims (larger tokens) — plan storage.

Full claim reference, refresh-token **rotation**, revocation semantics (and why a revoked token still passes signature checks), the two-signing-keys gotcha, and caching/rate-limit strategy: [tokens.md](tokens.md).

## Feature plans

Set with `--user-pool-tier LITE|ESSENTIALS|PLUS` on create/update. **New pools default to Essentials** (not Lite). A plan applies to a whole pool — you can't set it per app client, and different pools in an account can differ. Each tier is a superset of the one below.

| Feature | Lite | Essentials | Plus |
|---|---|---|---|
| Sign-up/in, groups, social/SAML/OIDC, OAuth2 server, M2M client-credentials, resource servers, CSV/JIT user import | ✓ | ✓ | ✓ |
| MFA with **SMS + authenticator app (TOTP)** | ✓ | ✓ | ✓ |
| **ID-token** customization, Lambda triggers, classic hosted UI, CSS customization | ✓ | ✓ | ✓ |
| **Managed login** (visual branding editor, dark mode) + localization | — | ✓ | ✓ |
| **Email MFA** | — | ✓ | ✓ |
| **Passwordless** (email/SMS OTP), **passkeys** (FIDO2) | — | ✓ | ✓ |
| **Choice-based auth** (`USER_AUTH`) | — | ✓ | ✓ |
| **Access-token** customization (pre-token-gen v2/v3) | — | ✓ | ✓ |
| **Password history** / reuse prevention | — | ✓ | ✓ |
| **Threat protection**: compromised creds, adaptive auth, activity logging + export | — | — | ✓ |

Rule of thumb: **Lite** = lowest cost, API-only or classic UI, no passwordless/passkeys; **Essentials** = the default, most apps (modern UI + passwordless + choice-based); **Plus** = adds security intelligence.

**Pricing drivers** (see [AWS Cognito pricing](https://aws.amazon.com/cognito/pricing)): monthly active users (MAUs), the feature plan, requests/sec to the API, federated (SAML/OIDC) MAUs, and M2M app clients/pools doing client-credentials grants.

**Setting `AdvancedSecurityMode` to `AUDIT` or `ENFORCED` forces the tier to `PLUS`** (and defaults it to PLUS).

**Downgrading requires turning features off first** — the console tells you which. Before you can leave a tier you must: remove the pre-token-gen **access-token** trigger (or replace with a `V1_0` ID-token-only trigger), disable all **threat protection** features, disable **log export** (Log streaming), and deselect **email MFA**. See [AWS docs: turning off features to change plans].

## Threat protection

Available on the **Plus** plan (`AdvancedSecurityMode` `AUDIT`/`ENFORCED`). Capabilities: **compromised-credentials** detection, **adaptive authentication** (risk-scored responses), **IP allow/block** lists, and **activity-log export**. Start in **audit** mode (log only) for ≥2 weeks, then **enforce**. Doesn't cover federated or M2M sign-in; for volumetric attacks use WAF.

Full treatment — compromised-creds flow coverage, adaptive-auth responses, device/context fingerprinting, `SetRiskConfiguration`, event history & feedback, log export: [threat-protection.md](threat-protection.md).

## MFA

- Factors: **SMS**, **email** (Essentials/Plus + SES), **TOTP** (authenticator app), and passkeys with user verification (`MULTI_FACTOR_WITH_USER_VERIFICATION`).
- Pool setting: `--mfa-configuration OFF | ON | OPTIONAL`. `ON` = required for all; `OPTIONAL` = per-user opt-in (and required for adaptive auth).
- In SDK flows, MFA appears as an `SMS_MFA`/`EMAIL_OTP`/`SOFTWARE_TOKEN_MFA` challenge from `InitiateAuth`; respond with `RespondToAuthChallenge`.
- A user who signs in with an OTP **first factor** can't then add MFA in the same session.

Per-user preferences (`SetUserMFAPreference`), the challenge state machine, per-factor setup (TOTP `AssociateSoftwareToken`), and the gating/lockout rules: [mfa.md](mfa.md). Trusting a device to skip MFA: [devices.md](devices.md).

## User attributes & groups

- **Standard attributes** follow OIDC: `email`, `phone_number`, `name`, `given_name`, `family_name`, `picture`, etc. Mark required at pool creation only. **Custom attributes** (`custom:` prefix) — up to 50, can't be deleted/renamed. Sign-in **aliases** vs **username attributes**, and per-app-client read/write permissions: full treatment in [attributes.md](attributes.md).
- `email_verified` / `phone_number_verified` gate password recovery and some flows.
- **Groups** (`aws cognito-idp create-group`) can carry a precedence and an IAM role (used when exchanging tokens at an identity pool). Membership shows up as `cognito:groups`. Full treatment (precedence rules, role selection, limits) in [user-management.md](user-management.md#groups).
- **Account states** — a user is `UNCONFIRMED`, `CONFIRMED`, `FORCE_CHANGE_PASSWORD`, `RESET_REQUIRED`, `EXTERNAL_PROVIDER`, or `DISABLED` depending on how they were created. See [user-management.md](user-management.md#account-states).

## Common scenarios

The six canonical Cognito architectures (which component each uses):

| Scenario | Components | Notes |
|---|---|---|
| **Authenticate app users** | user pool | Direct or federated sign-in; app receives JWTs |
| **Protect your own backend/API** | user pool | Verify access tokens server-side; use groups/scopes ([backend.md](backend.md)) |
| **API Gateway + Lambda** | user pool | Cognito authorizer validates tokens; map `cognito:groups` → IAM roles ([backend.md](backend.md#protect-api-gateway)) |
| **Client calls AWS services** (S3/DynamoDB) | user pool **+** identity pool | Exchange JWT for temporary AWS creds ([identity-pools.md](identity-pools.md)) |
| **Third-party/guest → AWS access** | identity pool | IdP token (or nothing for guest) → AWS creds |
| **AWS AppSync (GraphQL)** | user pool *or* identity pool | `AMAZON_COGNITO_USER_POOLS` authz with a JWT, or `AWS_IAM` authz with identity-pool creds |

Other patterns:
- **"Sign in with Google/Apple"** → user pool + domain + IdP + managed login redirect ([managed-login.md](managed-login.md), [social-providers.md](social-providers.md)).
- **Enterprise SSO** → user pool + external IdP: SAML ([saml.md](saml.md)), OIDC ([federation.md](federation.md)).
- **Fine-grained / policy-based authorization** → user pool tokens + Amazon Verified Permissions ([verified-permissions.md](verified-permissions.md)).
- **Service-to-service (no user)** → user pool resource server + `client_credentials` ([backend.md](backend.md#machine-to-machine)).
- **Guest/anonymous AWS access** → identity pool with unauthenticated identities.
- **Migrating an existing user directory** → migrate-user Lambda trigger ([lambda-triggers.md](lambda-triggers.md)).
- **Multiple customers/tenants** → pick an isolation model ([multi-tenancy.md](multi-tenancy.md)).
