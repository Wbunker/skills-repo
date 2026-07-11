# Identity Pools (Temporary AWS Credentials)

Use an identity pool when client code must call AWS services directly (S3, DynamoDB, etc.) or you need guest access. It exchanges a trusted token (usually a user pool ID token) for temporary AWS credentials from STS, scoped by an IAM role. If your app only calls **your own** API, you don't need this — a user pool alone is enough ([backend.md](backend.md)). If you need a data service to authorize on the **individual user's** identity/group grants (Q Business, Athena, Redshift, S3 Access Grants) rather than a shared role, use [trusted identity propagation](trusted-identity-propagation.md) instead.

## Table of Contents
1. [Model](#model)
2. [Create an identity pool](#create-an-identity-pool)
3. [IAM roles & trust policy](#iam-roles--trust-policy)
4. [Get credentials (client)](#get-credentials-client)
5. [Role selection: default, rules, group-based](#role-selection)
6. [Attribute-based access control (ABAC)](#attribute-based-access-control-abac)
7. [Guest access & gotchas](#guest-access--gotchas)

---

## Model

```
User pool sign-in → ID token (JWT)
        │
        ▼
Identity pool  ── validates token, picks an IAM role ──►  AWS STS
        │                                                    │
        ▼                                                    ▼
   Cognito identity id (us-east-1:uuid)              temporary AWS creds
                                                     (AccessKeyId/SecretKey/SessionToken)
```

Two APIs on the client: `GetId` (get/lookup the identity id) then `GetCredentialsForIdentity`. Amplify does both under the hood.

## Create an identity pool

Linked to a user pool:
```bash
aws cognito-identity create-identity-pool \
  --identity-pool-name MyAppIdentity \
  --no-allow-unauthenticated-identities \
  --cognito-identity-providers \
    ProviderName="cognito-idp.us-east-1.amazonaws.com/us-east-1_EXAMPLE",ClientId="1example23456789",ServerSideTokenCheck=true
```

Direct social providers (no user pool):
```bash
aws cognito-identity create-identity-pool \
  --identity-pool-name MyAppIdentity \
  --allow-unauthenticated-identities \
  --supported-login-providers \
    accounts.google.com="<google-client-id>",graph.facebook.com="<fb-app-id>"
```

Then attach roles:
```bash
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id us-east-1:POOL-UUID \
  --roles authenticated=arn:aws:iam::111111111111:role/MyApp_Auth_Role,unauthenticated=arn:aws:iam::111111111111:role/MyApp_Guest_Role
```

## IAM roles & trust policy

The role's **trust policy** must trust `cognito-identity.amazonaws.com` via web identity, scoped to your identity pool and the `authenticated` (or `unauthenticated`) amr — so the role can only be assumed in your pool's context:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "cognito-identity.amazonaws.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "cognito-identity.amazonaws.com:aud": "us-east-1:POOL-UUID" },
      "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" }
    }
  }]
}
```

The **permissions policy** grants the actual AWS access. Scope tightly — prefer per-user isolation with policy variables:
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-bucket/${cognito-identity.amazonaws.com:sub}/*"
}
```
`${cognito-identity.amazonaws.com:sub}` restricts each user to their own S3 prefix.

## Get credentials (client)

With Amplify configured for both pools, `fetchAuthSession()` returns AWS creds:
```js
import { fetchAuthSession } from "aws-amplify/auth";
const { credentials, identityId } = await fetchAuthSession();
// credentials.accessKeyId / secretAccessKey / sessionToken → feed to an AWS SDK client
```
Amplify config addition:
```js
Amplify.configure({
  Auth: { Cognito: {
    userPoolId: "us-east-1_EXAMPLE",
    userPoolClientId: "1example23456789",
    identityPoolId: "us-east-1:POOL-UUID",
    allowGuestAccess: true,   // enables unauthenticated creds
  }},
});
```

Raw SDK: `GetId` → `GetCredentialsForIdentity` with a `Logins` map keyed by the user pool issuer:
```
Logins = { "cognito-idp.us-east-1.amazonaws.com/us-east-1_EXAMPLE": <idToken> }
```

### Basic (classic) vs. enhanced flow

- **Enhanced flow** (recommended, default): the identity pool selects the IAM role and applies principal tags per your configured logic; the client calls just `GetCredentialsForIdentity`. Fewer requests, role/tag logic centralized in the pool.
- **Basic (classic) flow**: the client gets an OpenID token (`GetOpenIdToken`) and calls `sts:AssumeRoleWithWebIdentity` itself, choosing the role. More control, more client responsibility; needed for advanced custom role logic.

Prefer enhanced unless you specifically need the client to pick the role.

### Developer-authenticated identities

For a custom/legacy authentication system that isn't a SAML/OIDC/social IdP: authenticate the user in **your** backend, then call `GetOpenIdTokenForDeveloperIdentity` with your **developer credentials** (IAM keys) and a `Logins` key of your chosen developer provider name (e.g. `login.myapp.com`) mapped to your system's **external user id**. The pool trusts your backend's assertion and returns an **OpenID token + a Cognito identity id** that it permanently **maps to that external id** (reuse the same external id to get the same identity). The client then exchanges the OpenID token via `sts:AssumeRoleWithWebIdentity`. Use to bridge a bespoke identity store into Cognito-issued AWS creds without federation.
- **Validate the third-party/legacy token in your backend first** (e.g. call the provider's `/me` endpoint) — `GetOpenIdTokenForDeveloperIdentity` trusts your call implicitly, so the security gate is *your* verification before it.
- **Identity ids are per-Region** — the same external id yields different ids in different Regions (fine unless you assume one global id).

## Role selection

Three strategies (set via `set-identity-pool-roles` / `RoleMappings`):
- **Default** — every authenticated user gets the `authenticated` role. Simplest.
- **Rule-based** — match a token claim (e.g. `custom:dept == "eng"`) to different roles. Each rule is Claim + Operator + Value + Role.
- **Group-based (recommended with user pools)** — the user pool group's assigned IAM role (via group precedence) is used. Set `AmbiguousRoleResolution` and choose "Choose role from token" (`cognito:preferred_role`/`cognito:roles`).

**Role resolution** — when no rule matches, choose to either **deny credentials** or fall back to the **authenticated (default) role**. Deny is the stricter, usually safer default for tenant/role isolation.

## Attribute-based access control (ABAC)

Instead of many roles, map token claims to **principal tags** on the STS session, then gate resources with `aws:PrincipalTag` conditions:
```bash
aws cognito-identity set-principal-tag-attribute-map \
  --identity-pool-id us-east-1:POOL-UUID \
  --identity-provider-name "cognito-idp.us-east-1.amazonaws.com/us-east-1_EXAMPLE" \
  --use-defaults false \
  --principal-tags department=custom:dept,tier=custom:tier
```
```json
{ "Effect": "Allow", "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::data/*",
  "Condition": { "StringEquals": { "s3:ExistingObjectTag/department": "${aws:PrincipalTag/department}" } } }
```
One role, permissions that scale with attributes.

## Guest access & gotchas

- **Guest/unauthenticated** creds come from the `unauthenticated` role when `--allow-unauthenticated-identities` is on. Keep that role's permissions minimal.
- **`ServerSideTokenCheck=true`** makes the identity pool verify with the user pool on each credential request (catches disabled/deleted users) at a small latency cost.
- Identity pools issue **AWS credentials, not JWTs** — don't try to "verify" them like a token; IAM enforces them.
- The identity pool `aud` in role trust is the **identity pool id**, not the app client id — a common copy-paste mistake.
- Credentials last up to 1 hour; re-fetch before expiry (Amplify handles this).
- A **custom developer provider** name can't be modified or deleted after the identity pool is created — get it right at creation.
- Console trust setup asks for **Authenticated access**, **Guest access**, or both; guest access enables the `unauthenticated` role path.
