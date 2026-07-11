# App Client Configuration

Everything you set **per app client**: client type & secret, OAuth grants, scopes, callback URLs, and the update-safety rules. Auth flows are in [auth-flows.md](auth-flows.md); attribute read/write permissions in [attributes.md](attributes.md#attribute-permissions-per-app-client); token lifetimes/rotation/revocation in [tokens.md](tokens.md); custom scopes & resource servers in [backend.md](backend.md#machine-to-machine); which settings are permanent in [getting-started.md](getting-started.md#decisions-you-cant-undo).

## Table of Contents
1. [Client types & secrets](#client-types--secrets)
2. [OAuth grants](#oauth-grants)
3. [OIDC scopes & the narrowing rule](#oidc-scopes--the-narrowing-rule)
4. [Callback, sign-out & default redirect URLs](#callback-sign-out--default-redirect-urls)
5. [Updating clients & pools safely](#updating-clients--pools-safely)

---

## Client types & secrets

A pool has many app clients — one per application/platform/tenant, each with its own client id. Two OAuth types (RFC 6749):

- **Public** — browser/mobile, no server, **no secret**. SPA/Mobile console templates.
- **Confidential** — server-side, holds a **client secret**. Traditional-web/M2M console templates, or `GenerateSecret: true` in `CreateUserPoolClient`. A secret forces `SECRET_HASH` on unauthenticated calls; **required** for `client_credentials`.

**Secret rotation (two-secret support):** an app client can hold **up to two secrets at once**, so you can rotate without downtime — `AddUserPoolClientSecret` (Cognito-generated or your own value), cut traffic over, then `DeleteUserPoolClientSecret`. You **can't** delete the only secret, and you **can't change/regenerate** an existing secret in place (add a second, then delete the first). Secrets are fixed at creation otherwise — changing "has a secret at all" means a new client.

**CloudFront proxy for public clients** — you can front the Cognito API with a **CloudFront + Lambda@Edge** proxy so a "public" app effectively uses a confidential client: point the app at the CloudFront distribution; **Lambda@Edge computes the `SECRET_HASH`** (HMAC-SHA256 of `username`+`clientId` keyed by a secret pulled from **Secrets Manager** and cached) and injects it before forwarding to Cognito. This also lets you attach **WAF** (allowlist → denylist → rate-limit rules) and rate-limit the auth API. Two caveats: with **threat protection on**, the proxy must call the **`AdminInitiateAuth`/`AdminRespondToAuthChallenge`** (authenticated) operations and set **`EnablePropagateAdditionalUserContextData`** so the real client IP still reaches adaptive auth; and the proxy **only covers the SDK API** — hosted UI / OAuth / federation bypass it.

## OAuth grants

Requires a [domain](domains.md). Set `AllowedOAuthFlowsUserPoolClient: true` plus `AllowedOAuthFlows`:

| Grant | Returns | Use | Notes |
|---|---|---|---|
| **Authorization code** | ID + access + refresh | Web/SPA/mobile | Most secure — tokens never in the browser URL. **Public clients: use code + PKCE and enable *only* this flow.** |
| **Implicit** | ID + access (no refresh) | Legacy/test | No PKCE, no refresh token; avoid for new apps. Can be enabled alongside code. |
| **Client credentials** | access only (no ID) | M2M | Requires a secret; **can't** coexist with code/implicit on the same client; issues **custom scopes only**. See [backend.md](backend.md#machine-to-machine). |

`InitiateAuth`/`AdminInitiateAuth` (SDK sign-in) are separate from these OAuth grants and only ever yield the `aws.cognito.signin.user.admin` scope — custom/OIDC scopes require the OAuth endpoints.

**Cognito doesn't support OAuth extension grants** (RFC 8628 **device authorization grant**, token exchange, etc.). For a smart-TV/CLI/IoT **device flow**, build it yourself — API Gateway + Lambda + DynamoDB mint a `device_code`/`user_code`, poll a `/token` endpoint (`grant_type=urn:ietf:params:oauth:grant-type:device_code`, states `authorization_pending`/`slow_down`/`expired`), and after the user approves on a second device, the Lambda **exchanges a stored Cognito authorization code** at `/oauth2/token` and returns the JWTs. (For enterprise token-exchange to AWS analytics services, see [trusted-identity-propagation.md](trusted-identity-propagation.md).)

## OIDC scopes & the narrowing rule

Choose the scopes an app client may request (`AllowedOAuthScopes`). Standard OIDC scopes govern **what user data the ID token and `userInfo` return**:

- **`openid`** — mandatory for OIDC; returns the ID token + `sub`. **Requesting `openid` *alone* returns *all* client-readable attributes** in the ID token and `userInfo`.
- **Adding `email` / `phone` / `profile` narrows** the response to just those attributes (`email`→`email`+`email_verified`; `phone`→`phone_number`+`phone_number_verified`; `profile`→all readable attrs). Counter-intuitive: **more scopes = fewer attributes** than bare `openid`. `email`/`phone`/`profile` can only be requested together with `openid`.
- **`aws.cognito.signin.user.admin`** — authorizes the Cognito self-service API (read/write own attributes, MFA prefs, devices), bounded by the client's attribute permissions. For **both** API access *and* `userInfo`, request `openid` + `aws.cognito.signin.user.admin` (the admin scope alone can't hit `userInfo`).
- **Custom scopes** (`resource-server-id/scope`) authorize your own APIs — see [backend.md](backend.md#machine-to-machine).

## Callback, sign-out & default redirect URLs

- **Allowed callback URLs** (`CallbackURLs`) — where Cognito redirects after sign-in. Absolute URI, pre-registered, **no fragment**. **HTTPS required** except `http://localhost` (testing); custom app schemes like `myapp://example` are allowed.
- **Allowed sign-out URLs** (`LogoutURLs`) — post-sign-out redirect targets.
- **Default redirect URI** (`DefaultRedirectURI`) — used when an authorize request omits `redirect_uri` (third-party IdP links). Must also be one of the `CallbackURLs`. Only needed when a client has one IdP and multiple callback URLs.

CLI tip: pass URL lists as JSON so the CLI doesn't treat them as file refs — `--callback-urls '["https://example.com"]'`.

## Updating clients & pools safely

**The single most dangerous automation gotcha in Cognito:** `UpdateUserPool` and `UpdateUserPoolClient` are **full-replacement** operations. *Any parameter you omit is reset to its default.* Submitting an update with just the one field you want to change will silently wipe your **Lambda triggers, attribute schema, email/SMS config, OAuth settings**, etc. (The console avoids this by re-sending the whole config for you; SDK/CDK/CLI/CloudFormation callers must do the same.)

**Safe read-modify-write pattern:**
1. `DescribeUserPool` (or `DescribeUserPoolClient`) to capture current state.
2. Strip the read-only/output-only fields the update API rejects: `Arn`, `CreationDate`, `LastModifiedDate`, `Id`, `Name`, `Status`, `SchemaAttributes`, `EstimatedNumberOfUsers`, `EmailConfigurationFailure`, `SmsConfigurationFailure`, and **`Domain`/`CustomDomain`** (change those with `UpdateUserPoolDomain` instead).
3. Modify only the fields you want.
4. Send the full object back via `UpdateUserPool`/`UpdateUserPoolClient`.

Generate a blank input template with `aws cognito-idp update-user-pool --generate-cli-skeleton --output json` (or `update-user-pool-client`), or feed the trimmed describe output into `--cli-input-json`.

Also: an unrelated account change (a deleted SES identity, a WAF/IAM permission change) can make an update **fail** because a *current* parameter is now invalid — read the error, fix the named setting, retry.

**Settings you can't change on an existing client/pool** (need a new resource): whether the client has a **secret**, sign-in identifiers, username case sensitivity, required attributes, and custom-attribute deletion. Full list + which are console- vs SDK-only in [getting-started.md](getting-started.md#decisions-you-cant-undo). Note the pool **name** *is* now editable (it wasn't historically), and once **SMS is activated it can't be deactivated** (individual SMS uses — MFA, verification, invitations — can still be toggled).

## Analytics (Amazon Pinpoint) — deprecated

App clients have an `AnalyticsConfiguration` (`AnalyticsMetadata`/`AnalyticsEndpointId` on sign-up/in API calls) that streams sign-up/sign-in/failure and DAU/MAU data to an Amazon Pinpoint project (local users only; not federated or managed-login users; Pinpoint project usually in us-east-1). **Amazon Pinpoint reaches end of support on 2026-10-30** — don't build new analytics on it. Use CloudWatch metrics/logs or threat-protection activity-log export instead ([security.md](security.md#monitoring--logging)).
</content>
