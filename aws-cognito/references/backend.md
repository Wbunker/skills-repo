# Backend Integration (Node.js & Python)

Verifying Cognito tokens, protecting APIs, and doing admin/server-side operations. This is where security bugs live — read [Verifying JWTs](#verifying-jwts) carefully.

## Table of Contents
1. [Verifying JWTs](#verifying-jwts)
2. [Protect an Express API](#protect-an-express-api)
3. [Protect API Gateway](#protect-api-gateway)
4. [Protect a Python API (FastAPI/Flask)](#protect-a-python-api)
5. [Admin & server-side operations](#admin--server-side-operations)
6. [Machine-to-machine (client credentials)](#machine-to-machine)

---

## Verifying JWTs

A valid signature only proves Cognito issued the token. You **must also** check `token_use`, `client_id`/`aud`, `iss`, and `exp`. Skipping these is the #1 Cognito security bug (accepting an ID token where an access token is required, or a token from another app client).

**What to verify on every request:**
1. Signature — against the pool's public key (`kid` → JWKS).
2. `exp` — not expired.
3. `iss` — exactly `https://cognito-idp.<region>.amazonaws.com/<userPoolId>`.
4. `token_use` — `access` for API authorization; `id` only for identity/UI.
5. Audience — access token: `client_id`; ID token: `aud`. Must equal your app client id.
6. (Optional) `scope` or `cognito:groups` for authorization decisions.

JWKS URL (public, cache it, keyed by `kid`, refresh on miss — keys rotate):
```
https://cognito-idp.<region>.amazonaws.com/<userPoolId>/.well-known/jwks.json
```

Two things the library handles but you should know: **ID and access tokens are signed with different keys** (the two `kid`s in one session won't match — verify each type independently), and **revoking a token does not stop your API from accepting it** — a revoked JWT still passes signature+`exp` checks until it expires, so keep lifetimes short. See [tokens.md](tokens.md#two-signing-keys) and [tokens.md](tokens.md#revocation--sign-out).

### Node.js — aws-jwt-verify (recommended)

AWS's own library; handles JWKS caching, rotation, and all the claim checks.

```bash
npm install aws-jwt-verify
```

```js
import { CognitoJwtVerifier } from "aws-jwt-verify";

// Verify ACCESS tokens for API authorization
const verifier = CognitoJwtVerifier.create({
  userPoolId: "us-east-1_EXAMPLE",
  tokenUse: "access",          // enforces token_use === "access"
  clientId: "1example23456789", // enforces the audience
  // scope: "myapi/read",       // optional: require a scope
});

try {
  const payload = await verifier.verify(accessToken);
  // payload.sub, payload.scope, payload["cognito:groups"]
} catch {
  // reject: malformed, expired, wrong pool/client/use, or bad signature
}
```

Multi-audience or ID+access:
```js
const verifier = CognitoJwtVerifier.create({
  userPoolId: "us-east-1_EXAMPLE",
  tokenUse: null,                    // accept either; you then branch on payload.token_use
  clientId: ["webClientId", "mobileClientId"],
});
```

### Python — verifying manually (PyJWT + PyJWKClient)

boto3 has no built-in verifier; use PyJWT.

```bash
pip install "pyjwt[crypto]"
```

```python
import jwt
from jwt import PyJWKClient

REGION = "us-east-1"
POOL_ID = "us-east-1_EXAMPLE"
CLIENT_ID = "1example23456789"
ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_jwks = PyJWKClient(JWKS_URL)  # caches keys, refreshes on unknown kid

def verify_access_token(token: str) -> dict:
    signing_key = _jwks.get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=ISSUER,
        options={"verify_aud": False},  # access tokens use client_id, not aud
    )
    if claims.get("token_use") != "access":
        raise ValueError("not an access token")
    if claims.get("client_id") != CLIENT_ID:
        raise ValueError("wrong app client")
    return claims  # exp/iss already enforced by jwt.decode
```

For **ID** tokens: keep `verify_aud=True` and pass `audience=CLIENT_ID`, and require `token_use == "id"`.

## Protect an Express API

```js
import { CognitoJwtVerifier } from "aws-jwt-verify";

const verifier = CognitoJwtVerifier.create({
  userPoolId: process.env.USER_POOL_ID,
  tokenUse: "access",
  clientId: process.env.CLIENT_ID,
});

export async function requireAuth(req, res, next) {
  const auth = req.headers.authorization || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
  if (!token) return res.status(401).json({ error: "missing token" });
  try {
    req.user = await verifier.verify(token);
    next();
  } catch {
    res.status(401).json({ error: "invalid token" });
  }
}

// Authorization by group:
export const requireGroup = (group) => (req, res, next) =>
  (req.user["cognito:groups"] || []).includes(group)
    ? next()
    : res.status(403).json({ error: "forbidden" });

// app.get("/admin", requireAuth, requireGroup("admins"), handler);
```

## Protect API Gateway

Two managed options — no verification code needed:

- **Cognito user pool authorizer** (REST/HTTP API): attach the pool; API Gateway validates the token and rejects unauthorized requests. Send the token in the `Authorization` header.
- **JWT authorizer** (HTTP API): configure issuer `https://cognito-idp.<region>.amazonaws.com/<poolId>` and audience = app client id(s). Optionally require scopes per route.

Use a **Lambda authorizer** with `aws-jwt-verify` only when you need custom logic (per-tenant checks, dynamic policy).

**Defense in depth for microservices:** an edge check (ALB/API Gateway authorizer) isn't enough — **re-verify the access token inside each microservice** (`aws-jwt-verify` against JWKS, cached) and enforce **per-service scopes** (e.g. `myapi/orders.read`) so a compromised or misrouted internal caller can't act unchecked. Short-lived access tokens beat long-lived API keys for service-to-service calls; cache JWKS to keep verification latency nominal.

**Other AWS services accept Cognito directly:**
- **AWS AppSync (GraphQL)** — set the API's authorization mode to `AMAZON_COGNITO_USER_POOLS` (send the JWT; AppSync validates it and can gate fields by `cognito:groups`), or `AWS_IAM` with identity-pool credentials.
- **Application Load Balancer** — ALB can offload OIDC authentication to a user pool, redirecting unauthenticated users to managed login before requests reach your targets.

For rules richer than group/scope checks (per-resource, per-action, attribute- and context-based, centrally managed policy), externalize authorization to **Amazon Verified Permissions** instead of hand-coding it — an API Gateway–linked policy store adds the Lambda authorizer for you. See [verified-permissions.md](verified-permissions.md).

## Protect a Python API

FastAPI dependency:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer()

def current_user(cred: HTTPAuthorizationCredentials = Security(bearer)) -> dict:
    try:
        return verify_access_token(cred.credentials)  # from the verifier above
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")

# @app.get("/me")
# def me(user: dict = Depends(current_user)): return {"sub": user["sub"]}
```

## Admin & server-side operations

Use `AdminXxx` operations from a trusted backend with IAM permissions (`cognito-idp:Admin*`). These bypass client-side flows.

Node SDK v3:
```js
import {
  CognitoIdentityProviderClient, AdminCreateUserCommand,
  AdminSetUserPasswordCommand, AdminAddUserToGroupCommand,
  AdminGetUserCommand, AdminDeleteUserCommand, ListUsersCommand,
} from "@aws-sdk/client-cognito-identity-provider";

const c = new CognitoIdentityProviderClient({ region: "us-east-1" });

await c.send(new AdminCreateUserCommand({
  UserPoolId: POOL_ID, Username: "user@example.com",
  UserAttributes: [
    { Name: "email", Value: "user@example.com" },
    { Name: "email_verified", Value: "true" },
  ],
  MessageAction: "SUPPRESS",          // don't email a temp password
}));

await c.send(new AdminSetUserPasswordCommand({
  UserPoolId: POOL_ID, Username: "user@example.com",
  Password: "Str0ng!Pass", Permanent: true, // skip FORCE_CHANGE_PASSWORD
}));
```

Python (boto3):
```python
import boto3
c = boto3.client("cognito-idp")

c.admin_create_user(UserPoolId=POOL_ID, Username=email,
    UserAttributes=[{"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"}],
    MessageAction="SUPPRESS")
c.admin_set_user_password(UserPoolId=POOL_ID, Username=email,
    Password=pw, Permanent=True)
c.admin_add_user_to_group(UserPoolId=POOL_ID, Username=email, GroupName="admins")

# Paginate users:
for page in c.get_paginator("list_users").paginate(UserPoolId=POOL_ID):
    for u in page["Users"]:
        ...
```

Common admin ops: `AdminInitiateAuth`, `AdminRespondToAuthChallenge`, `AdminUpdateUserAttributes`, `AdminDisableUser`/`AdminEnableUser`, `AdminUserGlobalSignOut` (revoke all sessions), `AdminResetUserPassword`, `AdminListGroupsForUser`.

## Machine-to-machine

**Resource servers & custom scopes** — a *resource server* names one API and defines the custom OAuth scopes it exposes. Scopes are formatted `<resource-server-identifier>/<name>` (e.g. `myapi/read`). Assign scopes to an app client; access tokens then carry only the client's permitted scopes in the `scope` claim, which your API checks. Define one with the CLI or `AWS::Cognito::UserPoolResourceServer` ([iac.md](iac.md)):
```bash
aws cognito-idp create-resource-server --user-pool-id "$POOL_ID" \
  --identifier myapi --name myapi \
  --scopes ScopeName=read,ScopeDescription="read access" ScopeName=write,ScopeDescription="write access"
```

For service-to-service auth (no user), use the **client credentials** OAuth grant. Requires a domain, an app client **with a secret**, a resource server with custom scopes, and `allowed-o-auth-flows client_credentials`.

```bash
curl -X POST https://<domain>/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d 'grant_type=client_credentials&scope=myapi/read'
# → { "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }
```

The returned access token has no user (`sub` = the app client); verify it with `tokenUse: "access"` and check `scope`. This grant is billed per-request on M2M pricing (per active client-credentials app client + token-request volume, not MAUs). Cache tokens to cut requests — see the [API Gateway M2M caching proxy](tokens.md#caching--rate-limits).

**Scope model facts worth knowing:**
- **Resource server identifier** is any string (`myapi`), but URL-like identifiers (`https://api.example.com`) enlarge every access token — keep them short unless you need [resource binding](#resource-binding). Scope claim format is `<identifier>/<scopeName>`.
- **Deleting a scope** from a resource server marks it **inactive**, not removed — Cognito just omits it from tokens; re-adding reactivates it. But requesting a scope your **app client** isn't associated with **fails authentication** outright.
- **SDK sign-in never issues custom scopes.** `InitiateAuth`/`AdminInitiateAuth` only ever put `aws.cognito.signin.user.admin` in the `scope` claim; custom scopes require the OAuth token/authorize endpoints.
- **Pass client metadata to the pre-token-gen trigger in M2M**: token-endpoint client-credentials requests have no `RespondToAuthChallenge` to carry `ClientMetadata`, so send an `aws_client_metadata` form parameter (URL-encoded JSON) in the POST body.

### Resource binding

Resource binding (RFC 8707 "resource indicators") lets a client declare **which API a token is for**, so an API can reject tokens minted for something else. Add a `resource` parameter to the `/oauth2/authorize` request; Cognito validates it (must be a URL following the same scheme rules as callback URLs, or a resource-server identifier in URL form) and sets it as the access token **`aud`** claim. Your API then checks `aud`. One resource per request; refresh grants carry the original `aud` forward. **Managed-login only** (authorization-code/implicit grants) — **not** available in SDK auth, and **not** with client-credentials M2M grants.

### AI agents acting on behalf of a user

A common agentic pattern: an AI agent authenticates as a **machine** (client-credentials) but must act **on behalf of a signed-in human**. Carry the user's identity *inside* the agent's own token rather than re-authenticating per user:

1. Agent requests a client-credentials token and passes the human's access token (and any app id) via **`aws_client_metadata`** — e.g. `{"onBehalfOfToken":"<user-access-token>","callerApp":"ChatApp"}` (URL-encoded).
2. A **pre-token-generation trigger** (event **v3**, `TokenGeneration_ClientCredentials` source) verifies the user token isn't expired/tampered, extracts `sub`/groups, and injects them as **custom claims** (`onBehalfOf`, `callerApp`) into the agent's access token — alongside the scopes (`crossDomainService/read`, …) the agent is allowed.
3. Downstream, **AVP `IsAuthorizedWithToken`** ([verified-permissions.md](verified-permissions.md)) evaluates the agent token: the resource owner must equal the `onBehalfOf` user **and** `callerApp` must be an authorized initiator.

Use **separate user pools** for human users vs. agent (machine) identities — distinct security controls and audit boundaries.

### Monitoring & securing M2M

- **Audit which app clients are actually used** — client-credentials token requests appear in CloudTrail as `Token_POST`. A CloudWatch Logs Insights query surfaces active vs. dormant clients (dormant secrets are attack surface — rotate/remove them):
  ```
  fields additionalEventData.clientId as client_id, additionalEventData.responseParameters.status as status
  | filter additionalEventData.requestParameters.grant_type.0="client_credentials"
      and eventName="Token_POST" and status="200"
  | stats count(*) as count, latest(eventTime) as lastUsed by client_id
  ```
- **WAF on the token endpoint** — enable AWS WAF (Bot Control managed rules) on the pool; front the caching proxy with custom headers + a WAF allow-list, and encrypt the API Gateway cache at rest. Add mTLS/extra authorizers for regulated workloads.
- **Least privilege** — minimal custom scopes per client, secrets in **Secrets Manager** (retrieved at runtime), and **per-tenant app clients** for multi-tenant M2M ([multi-tenancy.md](multi-tenancy.md)).
