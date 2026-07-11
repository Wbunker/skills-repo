---
name: aws-cognito
description: Add authentication and authorization to web, mobile, and backend apps with Amazon Cognito. Use for sign-up/sign-in, password/SRP/passwordless/passkey login, MFA, social and enterprise federation (Google, Apple, Facebook, Amazon, SAML, OIDC), hosted UI / managed login OAuth flows, JWT verification and API protection, Lambda triggers, identity pools for temporary AWS credentials, and provisioning pools via CLI, CloudFormation, CDK, or Terraform. Covers Node.js (SDK v3, aws-jwt-verify), Python (boto3), web frontends (Amplify JS, amazon-cognito-identity-js), and Flutter/Amplify. Trigger on: "Cognito", "user pool", "identity pool", "cognito-idp", "hosted UI", "managed login", "verify JWT from Cognito", "protect my API with Cognito", "add login to my app".
---

# Amazon Cognito

Amazon Cognito is AWS's identity platform: a **user directory**, an **OAuth 2.0 / OIDC authentication server**, and an **AWS-credential authorization service**. It has two independent components that are often confused — choosing the right one is the first decision.

## Decision 1: User pool vs. identity pool

| You want to… | Use | Issues |
|---|---|---|
| Authenticate users, get who-they-are, protect your own APIs | **User pool** | JWTs (ID / access / refresh) |
| Give users temporary IAM credentials to call AWS services (S3, DynamoDB) directly | **Identity pool** | AWS creds via STS |
| Both (sign in, then hand out AWS creds) | **User pool → identity pool** | JWT, then swap for AWS creds |

Most apps only need a **user pool**. Reach for an identity pool only when client code must call AWS APIs directly, or you need guest/unauthenticated AWS access. See [references/identity-pools.md](references/identity-pools.md).

## Decision 2: Who runs the login UI?

- **Managed login / hosted UI** (Cognito-hosted pages, OAuth redirect flow) — fastest path; the **only** way to get OAuth 2.0 grants, third-party social/SAML/OIDC federation, SSO across app clients, native passwordless/passkeys, WAF CAPTCHA, and ALB offload. Your app redirects to Cognito and gets tokens back. **Can't** do custom-auth (Lambda challenge) flows, remembered-device auth, or sub-1-hour sessions. See [references/managed-login.md](references/managed-login.md).
- **Your own UI + AWS SDK** (`InitiateAuth`/`RespondToAuthChallenge`) — full control of the screens; required for custom-auth (Lambda challenge) flows, remembered devices, and sub-1-hour sessions. **Can't** do OAuth grants, third-party federation, SSO across app clients, WAF CAPTCHA, or ALB. See [references/auth-flows.md](references/auth-flows.md).

You can mix: SDK for local username/password, redirect to managed login for "Sign in with Google."

## Decision 3: How much authorization logic?

- **Coarse** (is-valid-user, in-group, has-scope) → verify the JWT in your API and branch on `cognito:groups`/`scope`. See [references/backend.md](references/backend.md).
- **Fine-grained** (per-resource, per-action, attribute/context rules, central policy you can change without redeploying) → externalize to **Amazon Verified Permissions** (Cedar policies, `IsAuthorizedWithToken`). See [references/verified-permissions.md](references/verified-permissions.md).
- **AWS-resource access** (client calls S3/DynamoDB directly, gated by IAM) → identity pool ABAC. See [references/identity-pools.md](references/identity-pools.md).

## Serving multiple tenants?

There's no built-in tenant primitive — pick an isolation model (pool / app-client / group / custom-attribute / scope per tenant) early, and beware the shared hosted-UI session cookie. See [references/multi-tenancy.md](references/multi-tenancy.md).

## The three tokens (user pools)

Every successful sign-in returns three JWTs. Understand these before writing any integration code:

- **ID token** — *who the user is*. Claims: `sub`, `email`, `cognito:groups`, custom attrs. `aud` = app client id, `token_use: id`. For your app's UI, not for authorizing APIs.
- **Access token** — *what they can do*. Claims: `scope`, `cognito:groups`, `client_id`, `token_use: access`. **This is what you verify to protect APIs.**
- **Refresh token** — opaque/encrypted; exchange for new ID + access tokens. Lives days–years per app-client config.

Never trust a token you haven't cryptographically verified. See [references/backend.md](references/backend.md) for verification — it is the single most common thing developers get wrong. For the full claim reference, refresh-token rotation, revocation semantics, and caching, see [references/tokens.md](references/tokens.md).

## Quick start (CLI): a working user pool in 3 calls

```bash
# 1. User pool — sign in with email, auto-verify email, optional MFA
POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name MyApp \
  --username-attributes email \
  --auto-verified-attributes email \
  --mfa-configuration OPTIONAL \
  --query 'UserPool.Id' --output text)

# 2. App client — no secret (browser/mobile), SRP + refresh + choice-based
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id "$POOL_ID" \
  --client-name web \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_USER_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --prevent-user-existence-errors ENABLED \
  --query 'UserPoolClient.ClientId' --output text)

# 3. Domain — enables managed login + OAuth endpoints
aws cognito-idp create-user-pool-domain --user-pool-id "$POOL_ID" --domain myapp-$RANDOM
```

`--generate-secret` **only** for confidential clients (server-side apps that can keep a secret). Browser/mobile clients must use `--no-generate-secret`; a secret in a public client is a leak, and the SDKs require a `SECRET_HASH` when one exists.

## Route to the right reference

Load only what the task needs — each reference is self-contained.

| Task | Reference |
|---|---|
| **Getting started**: console quick path, application types, permanent-at-creation settings, official example apps | [references/getting-started.md](references/getting-started.md) |
| Orientation, terminology, feature plans (Lite/Essentials/Plus), threat protection, MFA, attributes, groups | [references/concepts.md](references/concepts.md) |
| **Security hardening**: public-access controls, WAF (rate-limit/CAPTCHA), secrets, least-privilege IAM, token handling, encryption at rest (KMS), scopes, monitoring | [references/security.md](references/security.md) |
| **Quotas & limits**: RPS category quotas, provisioned limits, per-user/per-domain rates, resource caps, token/code validity, MAU billing | [references/quotas.md](references/quotas.md) |
| **Monitoring & auditing**: CloudTrail events, CloudWatch metrics, log export (delivery errors + activity), Logs Insights queries | [references/monitoring.md](references/monitoring.md) |
| **Threat protection** (Plus): compromised-credentials, adaptive auth, risk responses, device fingerprinting, `SetRiskConfiguration`, event logs | [references/threat-protection.md](references/threat-protection.md) |
| **Multi-Region replication**: DR replica pools, primary/secondary, Route 53 failover, prerequisites & limitations | [references/multi-region.md](references/multi-region.md) |
| Provision pools/clients/providers/domains via **CLI** | [references/cli-commands.md](references/cli-commands.md) |
| Provision via **CloudFormation / CDK / Terraform** | [references/iac.md](references/iac.md) |
| Auth flows in depth: SRP, password, **USER_AUTH** choice-based, passwordless (email/SMS OTP), **passkeys/WebAuthn**, custom, admin, refresh | [references/auth-flows.md](references/auth-flows.md) |
| **Backend**: verify JWTs, protect APIs (Express/API Gateway/FastAPI), admin ops, server-side auth, resource servers & scopes, resource binding — Node SDK v3 + Python boto3 | [references/backend.md](references/backend.md) |
| **App clients**: public/confidential, secret rotation, OAuth grants, OIDC scope-narrowing, callback URLs, the update reset-to-defaults trap | [references/app-clients.md](references/app-clients.md) |
| **Tokens deep-dive**: full ID/access claim reference, refresh-token rotation, revocation & sign-out semantics, caching/rate-limits | [references/tokens.md](references/tokens.md) |
| **Fine-grained authorization** with Amazon Verified Permissions (Cedar policies, `IsAuthorizedWithToken`, API Gateway policy stores) | [references/verified-permissions.md](references/verified-permissions.md) |
| **Multi-tenancy**: pool/app-client/group/custom-attribute/scope-per-tenant models, isolation, security | [references/multi-tenancy.md](references/multi-tenancy.md) |
| **Web frontend**: Amplify JS v6, amazon-cognito-identity-js, OAuth code flow in a SPA, token storage/logout | [references/web-frontend.md](references/web-frontend.md) |
| Hosted UI / **managed login**: OAuth endpoints (`/authorize`, `/token`, `/logout`, `/userInfo`, `/revoke`), redirect flow, localization, terms | [references/managed-login.md](references/managed-login.md) |
| **OAuth endpoint reference**: every `/authorize` param (`prompt`/silent-SSO, `login_hint`, `resource`), token/userInfo/revoke behavior & errors, PKCE, OIDC issuer choice | [references/oauth-endpoints.md](references/oauth-endpoints.md) |
| **Domains**: prefix vs custom, ACM/CloudFront/DNS setup, discovery-endpoint location, cookie-hierarchy trap | [references/domains.md](references/domains.md) |
| **Branding**: managed-login branding editor + hosted-UI classic CSS, per-client styles, asset/size limits, API | [references/branding.md](references/branding.md) |
| **User management**: account states, sign-up/confirm, verification, admin users, search, password recovery, import (CSV/JIT), groups | [references/user-management.md](references/user-management.md) |
| **Attributes & aliases**: standard/custom attributes, alias vs username-attribute sign-in, per-client read/write permissions | [references/attributes.md](references/attributes.md) |
| **MFA**: modes/methods, per-user preferences (`SetUserMFAPreference`), the challenge state machine, TOTP/SMS/email setup, gating rules | [references/mfa.md](references/mfa.md) |
| **Remembered devices**: device tracking modes, `ConfirmDevice`, the `DEVICE_SRP_AUTH` flow, management APIs, time-limited trust | [references/devices.md](references/devices.md) |
| **Message delivery**: email (default vs SES), SMS (SNS/sandbox/spend/ExternalId), templates & placeholders, testing | [references/messaging.md](references/messaging.md) |
| **Lambda triggers**: catalog, event shapes, recipes (pre sign-up, pre token gen, migrate user, custom challenge, custom sender) | [references/lambda-triggers.md](references/lambda-triggers.md) |
| **Identity pools**: temporary AWS creds, role/attribute-based access, guest access | [references/identity-pools.md](references/identity-pools.md) |
| **Trusted identity propagation** (IAM Identity Center): token exchange to reach Q Business/Athena/Redshift/S3 Access Grants as the *user* | [references/trusted-identity-propagation.md](references/trusted-identity-propagation.md) |
| **Federation (OIDC + shared)**: OIDC setup, attribute mapping, account linking, IdP routing, federation behaviors | [references/federation.md](references/federation.md) |
| **SAML 2.0 federation**: ACS/SP URN, metadata, SP-vs-IdP-initiated, signing/encryption, SLO, third-party IdPs | [references/saml.md](references/saml.md) |
| Social IdP setup (Google/Apple/Facebook/Amazon console + CLI + mapping) | [references/social-providers.md](references/social-providers.md) |
| **Flutter / Amplify** mobile integration | [references/flutter-amplify.md](references/flutter-amplify.md) |

## High-value gotchas

- **Verify `token_use` and `client_id`/`aud`, not just the signature.** A valid signature only proves Cognito issued the token — an access token accepted where you meant an ID token (or vice versa), or a token from a different app client, is a real vulnerability. See [references/backend.md](references/backend.md).
- **Username is immutable and defaults to a UUID (`sub`).** If users sign in with email, set `--username-attributes email` at pool creation — it can't be changed later. Plan aliases up front.
- **Several settings are permanent and console-locked.** Sign-in identifiers, required attributes, whether a client has a secret, **username case sensitivity** (console pools are always case-insensitive), and **`preferred_username` aliasing** can't be changed after creation — and case sensitivity / `preferred_username` alias can *only* be set by creating the pool via SDK/IaC, not the console. Once **SMS is activated it can't be deactivated**. See [references/getting-started.md](references/getting-started.md).
- **`UpdateUserPool`/`UpdateUserPoolClient` reset every omitted parameter to its default** — a partial update silently wipes your Lambda triggers, attribute schema, and email/SMS config. Always `Describe*` → modify the full object → `Update*` (the console does this for you; SDK/CDK/CLI/CloudFormation callers must too). See [references/app-clients.md](references/app-clients.md#updating-clients--pools-safely).
- **Password auth flows are per-app-client.** A flow not in `ExplicitAuthFlows` fails with `NotAuthorizedException`, even with correct credentials. `ALLOW_USER_SRP_AUTH` ≠ `ALLOW_USER_PASSWORD_AUTH`.
- **Custom auth (Lambda challenge) and third-party federation are mutually exclusive with each other's channel:** custom auth is SDK-only (no managed login); federation is managed-login-only (no SDK). Design around this early.
- **App-client secret changes the flow.** With a secret you must send a `SECRET_HASH` (HMAC-SHA256 of `username+clientId` keyed by the secret) on every unauthenticated call. Prefer no secret for public clients.
- **`prevent-user-existence-errors ENABLED`** avoids leaking which emails are registered — set it on every client. **The API/CLI default is `LEGACY` (disabled)** even though the console enables it. Behavior matrix (SRP-with-aliases caveat, `SignUp` enumeration, choice-based auth exemption) in [references/security.md](references/security.md).
- **Creating any user pool domain exposes public sign-in pages** for every app client. If you want SDK-only auth, don't create a domain.
- **Only `Admin*` API operations are IAM-gated**; `InitiateAuth`/`SignUp`/`GetUser` ignore IAM. Control the public surface with app-client settings, not IAM policies. IAM resource granularity is pool-level — you can't scope to one app client.
- **New pools default to the Essentials plan**, and enabling threat protection (`AdvancedSecurityMode`) forces the Plus plan.
- **Compromised-credentials detection only sees plaintext-password flows** (`USER_PASSWORD_AUTH`/`ADMIN_USER_PASSWORD_AUTH`) — it's **blind to SRP and custom auth**, since Cognito never gets the plaintext. Adaptive auth still covers SRP. Threat protection also never rate-limits (use WAF) and doesn't apply to federated or M2M sign-in. See [references/threat-protection.md](references/threat-protection.md).
- **A WAF CAPTCHA rule breaks managed-login TOTP enrollment** — exclude the `AssociateSoftwareToken`/`VerifySoftwareToken` operation-name headers from the CAPTCHA action. And **WAF-blocked requests don't count toward the request quota** (WAF runs before throttling). See [references/security.md](references/security.md#network-protection-waf--sms-abuse).
- **Some standards need a proxy — Cognito doesn't do them natively:** OAuth **extension grants** (RFC 8628 device flow → API Gateway+Lambda+DynamoDB), **`private_key_jwt`** client auth to an OIDC IdP (→ Lambda that signs an RFC 7523 assertion), `client_secret_basic` for OIDC IdPs (use `client_secret_post`), and a **client secret on a public client** (→ CloudFront/Lambda@Edge `SECRET_HASH` proxy). See [references/app-clients.md](references/app-clients.md) / [references/federation.md](references/federation.md).
- **A `/token` `invalid_grant` can mean your app client can't read a scoped attribute** — e.g. requesting the `email` scope when the client lacks read access to `email_verified` fails the *code exchange*, not the authorize step. Also `invalid_grant` = consumed code or revoked refresh token. And the **"updated" multi-Region OIDC issuer is incompatible with ALB auth and API Gateway Cognito authorizers** — stay on the original issuer there. See [references/oauth-endpoints.md](references/oauth-endpoints.md).
- **Signing keys rotate**, and **ID vs. access tokens are signed with different keys** — cache JWKS by `kid`, refresh on a miss, and verify each token type independently. `aws-jwt-verify` handles this for you.
- **Revoking a token isn't a kill-switch for your API.** A revoked access token still passes signature + `exp` verification in any JWT library — revocation only blocks Cognito's own API calls. Your resource server keeps accepting it until it expires, so keep lifetimes short (or check a deny list). Enable **refresh-token rotation**; it's incompatible with `REFRESH_TOKEN_AUTH` (use `GetTokensFromRefreshToken`). See [references/tokens.md](references/tokens.md).
- **Managed login sets a 1-hour session cookie.** Token lifetimes below 1 hour don't shorten the managed-login session — users silently re-authenticate from the cookie until it expires, and it survives `GlobalSignOut` until you redirect them to `/logout`. See [references/tokens.md](references/tokens.md#managed-login-cookie-floor).
- **SAML `NameID` must be stable and is case-sensitive.** Any change to its value — even letter case, or an email if you mapped `NameID` to email — creates a *new* user profile and locks the user out. Map it to a persistent, unchanging identifier. See [references/saml.md](references/saml.md#things-to-know).
- **Federated (mapped) emails are unverified** and a mapped **immutable** attribute makes sign-in fail. Map `email_verified` from the IdP; keep mapped attributes mutable + writable. See [references/federation.md](references/federation.md#attribute-mapping).
- **Custom domains must be a subdomain** (not a root/TLD), need an ACM cert **in us-east-1**, and require the parent domain to have a DNS `A` record. See [references/domains.md](references/domains.md).
- **5 failed passwords → exponential lockout** (`2^(n-5)` seconds, ~15 min cap). Don't build retry loops that trip it.
- **Post-confirmation triggers don't fire for admin-created users**, and pre-sign-up auto-verify flags are ignored for `AdminCreateUser` — don't rely on them to provision or verify admin-created accounts. See [references/lambda-triggers.md](references/lambda-triggers.md).
- **A user with no verified email/phone can't recover a forgotten password** — always verify (or auto-verify) at least one contact method. In an **MFA pool a user's MFA channel can't also be their recovery channel**, so single-contact users get locked out — require both `email` and `phone_number`. Account states differ by entry path (self-signup→`UNCONFIRMED`, admin→`FORCE_CHANGE_PASSWORD`, import→`RESET_REQUIRED`). See [references/user-management.md](references/user-management.md).
- **Sign-in aliases vs. username attributes are fixed at pool creation**; custom attributes can't be deleted/renamed and **aren't searchable** by `ListUsers`; identify users by immutable `sub`, never a mutable sign-in attribute. **Case sensitivity is also creation-fixed** — the API/CLI default is case-*sensitive* while the console makes case-*insensitive* pools (which also lowercase-flatten `userInfo`/`GetUser`/Lambda outputs). See [references/attributes.md](references/attributes.md#case-sensitivity).
- **API rate limits are pooled by category, per account+Region** — e.g. all sign-in ops share the `UserAuthentication` budget (default 120 RPS) across every pool in the Region; a hot `SignUp` path and a hot admin script can throttle each other. Raise adjustable categories yourself with `UpdateProvisionedLimit` (billed for provisioned capacity), and remember `AdminGetUser` marks a user active (bills as MAU) while `ListUsers` doesn't. See [references/quotas.md](references/quotas.md).
- **Production email needs Amazon SES** (`EmailSendingAccount: DEVELOPER`); the default has low volume caps, can't do custom FROM/HTML, and **permanently suppresses hard-bounced addresses on an AWS-managed list you can't edit**. **New accounts are in the SMS sandbox** (verified numbers only, $1/mo spend cap). Reusing an existing **SMS IAM role for MFA** requires a matching `sts:ExternalId` on the role trust policy and the pool. See [references/messaging.md](references/messaging.md).
- **There's no native "last sign-in" attribute.** To find/disable inactive users, record activity yourself in a **post-authentication trigger** → external store (DynamoDB TTL+Streams → `AdminDisableUser`), or reconstruct from CloudTrail. Don't write last-login into a custom attribute (rate-limited directory writes; attributes are identity, not activity logs). See [references/user-management.md](references/user-management.md#detecting-inactive-users).
- **A new user's *first* sign-in issues tokens even in a required-MFA pool** — confirming the sign-up verification message counts as the second factor that once; MFA enrolment is prompted on later sign-ins. Don't assume the first session was MFA-gated. See [references/mfa.md](references/mfa.md).
