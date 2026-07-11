# Fine-Grained Authorization with Amazon Verified Permissions (AVP)

JWT verification ([backend.md](backend.md)) proves *who* the user is and carries coarse signals (`scope`, `cognito:groups`). When authorization gets richer than "is in group X" — per-resource, per-action, attribute- and context-dependent rules — externalize it to **Amazon Verified Permissions**. AVP evaluates **Cedar** policies against a Cognito token and returns `Allow`/`Deny`, so authorization logic lives in policies instead of scattered `if` statements.

## Table of Contents
1. [When to reach for AVP](#when-to-reach-for-avp)
2. [The isAuthorizedWithToken call](#the-isauthorizedwithtoken-call)
3. [Setup](#setup)
4. [Access token vs. ID token](#access-token-vs-id-token)
5. [Cedar policy examples](#cedar-policy-examples)
6. [API Gateway–linked policy store](#api-gateway-linked-policy-store)
7. [Gotchas](#gotchas)

---

## When to reach for AVP

| Need | Use |
|---|---|
| "Is this a valid user / in group admins / has scope X" | JWT verify in-app ([backend.md](backend.md)) |
| Per-resource, per-action rules; ABAC; central, auditable policy; policies changeable without redeploy | **AVP** |
| AWS-credential access to S3/DynamoDB gated by IAM | identity pool ABAC ([identity-pools.md](identity-pools.md)) |

AVP and identity-pool "attributes for access control" are both ABAC: AVP returns an allow/deny decision from a JWT (app enforces); identity pools tag an STS session and IAM enforces on AWS API calls.

## The isAuthorizedWithToken call

Pass a Cognito token plus the **Action** and **Resource**; optionally **Context**. AVP resolves the token into a **Principal** and evaluates policies.

```js
import { VerifiedPermissionsClient, IsAuthorizedWithTokenCommand }
  from "@aws-sdk/client-verifiedpermissions";

const avp = new VerifiedPermissionsClient({ region: "us-east-1" });
const res = await avp.send(new IsAuthorizedWithTokenCommand({
  policyStoreId: "PS-EXAMPLE",
  accessToken,                                   // OR identityToken (pick one)
  action:   { actionType: "PetStore::Action", actionId: "get /pets" },
  resource: { entityType: "PetStore::Resource", entityId: "pets" },
  context:  { contextMap: { /* extra attributes for the decision */ } },
}));
res.decision;      // "ALLOW" | "DENY"
```
`BatchIsAuthorizedWithToken` evaluates many action/resource pairs for one principal in a single call.

## Setup

1. Create a **policy store** (Cedar schema + policies).
2. Add your **user pool as an identity source** on the store.
3. **Configure client ID validation** — list the app client IDs AVP should accept (`aud` for ID tokens, `client_id` for access tokens).
4. Choose the **token type** the store processes: `access` or `id` (see below).
5. Define **user and group entity types**; make the user entity a **member of** the group entity so policies can say `principal in Group::"…"`. (API-linked/guided setup wires this automatically.)
6. Write Cedar policies.

Validations AVP performs on each token: identity source configured; `client_id`/`aud` matches; not expired; `token_use` matches the parameter you used (`access`→`accessToken`, `id`→`identityToken`); signature verifies against the pool JWKS.

## Access token vs. ID token

You pick one per policy store:

- **Access token** (recommended for RBAC): carries `scope` + `cognito:groups`. Scopes and other claims become **context** in the request.
- **ID token** (enables ABAC): carries user attributes (`email`, `custom:*`). Attribute claims become **principal attributes** you can test in policy `when` clauses. Combine with `cognito:groups` for RBAC+ABAC.

Enrich either token with a **pre token generation Lambda trigger** ([lambda-triggers.md](lambda-triggers.md)) to add claims (e.g. `custom:costCenter`, tenant id) that your policies need.

## Cedar policy examples

**RBAC by group** — allow the `MyGroup` group to GET pets:
```cedar
permit(
  principal in PetStore::UserGroup::"us-east-1_EXAMPLE|MyGroup",
  action in [ PetStore::Action::"get /pets", PetStore::Action::"get /pets/{petId}" ],
  resource
);
```

**ABAC by attribute** — Finance users from a specific app client may read/write one file:
```cedar
permit(
  principal,
  action in [ExampleCorp::Action::"readFile", ExampleCorp::Action::"writeFile"],
  resource == ExampleCorp::Photo::"example_image.png"
)
when {
  principal.aud == "1234567890example" &&
  principal.custom.costCenter like "Finance*"
};
```

Principal / group identifier formats:
```cedar
// user:  Namespace::User::"<userPoolId>|<sub>"
principal == ExampleCorp::User::"us-east-1_Example|973db890-092c-49e4-a9d0-912a4c0a20c7"
// group: Namespace::Group::"<groupName>"
principal in ExampleCorp::Group::"Finance"
```

## API Gateway–linked policy store

The fastest end-to-end path for protecting a REST API. In the AVP console, **Set up with API Gateway and an identity source**: AVP creates the policy store, adds your user pool as identity source, and attaches a **Lambda authorizer** to the API. The app sends a bearer token; the authorizer calls AVP with the token as **principal** and the request **method + path** as **action**; `cognito:groups` drives RBAC. No verification code to maintain — an alternative to the Cognito user pool authorizer / manual `aws-jwt-verify` authorizer in [backend.md](backend.md).

Specifics worth knowing:
- **Use the access token** (AWS's recommendation) for RBAC — group claims map cleanly; ID token if you need attribute-based rules. Group→principal format is **`<poolId>|<groupName>`** (Cognito) or `<issuerUrl>|<groupName>` (generic OIDC).
- The wizard auto-generates **actions from method+path** (`"get /pets"`, `"delete /admin/{proxy+}"`) — a `{proxy+}` resource collapses many endpoints into one action. It leaves **resource unspecified** (the app itself is the resource) and **defaults to deny**. Deselect groups you don't use so it doesn't generate dead policies.
- **The authorizer caches decisions ~120 s** — a policy change won't take effect until the cache expires or you call **`FlushStageAuthorizersCache`**. Plan for this when testing/rolling out policy updates.
- **Dual-authorizer cost pattern:** AVP calls are billed per request. Put "any authenticated user" routes (e.g. `GET /pets`) behind a **cheap cached Cognito user-pool authorizer**, and reserve the **AVP Lambda authorizer** for the routes that actually need group/attribute-level decisions — cuts chargeable AVP requests.

## Gotchas

- **AVP does not check token revocation or user deletion** — a revoked token or deleted user is still honored until `exp`. Keep access-token lifetimes short; enforce revocation elsewhere if you need it.
- **Reserved claim prefixes:** in a pre-token-gen trigger, don't add *full* claim names `cognito`, `dev`, or `custom` (they must appear only in colon-delimited form like `cognito:username`). Doing so makes authorization requests fail.
- **`token_use` must match the parameter** — passing an access token as `identityToken` (or vice-versa) is rejected.
- **Group claims in ID vs access token** — both carry `cognito:groups`, but only the ID token carries user attributes for ABAC.
- **`IsAuthorizedWithToken` requests need AWS credentials** (it's a signed AWS API call, even though the *user* is identified by the token). Supply them one of three ways: a server backend holding secrets, **identity-pool credentials** for the signed-in user, or by proxying the user request through an access-token-authorized API that appends AWS credentials. A pure browser SPA can't call AVP directly without one of these.
