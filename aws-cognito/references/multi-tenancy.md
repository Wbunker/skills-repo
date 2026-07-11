# Multi-Tenancy

Serving multiple customers (tenants) from Cognito. There is no single "tenant" primitive — you pick an isolation model and enforce it. Choosing right up front matters because some dimensions (a pool's config, a custom attribute's mutability) can't be changed later.

## Table of Contents
1. [Model selection](#model-selection)
2. [The models](#the-models)
3. [The hosted-UI cookie cross-tenant trap](#the-hosted-ui-cookie-cross-tenant-trap)
4. [Quotas are shared](#quotas-are-shared)
5. [Security recommendations](#security-recommendations)

---

## Model selection

| Model | Isolation | Effort | Tenant context in token | Best when |
|---|---|---|---|---|
| **Pool per tenant** | Highest | High | separate pool | Per-tenant config differs (MFA, password policy, branding, IdP); strong isolation; multiple tenants use managed login |
| **App client per tenant** | Medium | Medium | `aud`/`client_id` = tenant client | Universal pool config, but per-tenant IdP or app; users move between apps |
| **Group per tenant** | Medium (via IAM) | Low | `cognito:groups` / `cognito:roles` | Access to **AWS resources** via identity pools is the goal (RBAC → IAM role) |
| **Custom attribute per tenant** | Lowest | High (app-side) | `custom:tenantId` claim | Tenancy is surface-level (branding, layout); one URL for everyone |
| **Custom scope per tenant** | Medium | Medium | tenant-scoped OAuth scopes | API authorization differs per tenant via resource-server scopes |

Rule of thumb: **isolation & per-tenant customization → pool per tenant**; **AWS-resource access → group per tenant**; **lightweight branding only → custom attribute**; **per-tenant IdP/app → app client per tenant**. Models compose (e.g. shared pool + group + custom attribute), and **hybrids are fine** — dedicated pools for a few high-tier tenants alongside a shared pool for the rest.

**Routing a user to the right pool/client** needs a mapping dataset keyed on tenant-identifying input: **subdomain** (`tenant1.app.com`), **verified email domain** (`@tenant1.com`), a **tenant-picker dropdown**, or a **tenant-code** the user enters. Store the tenant→pool/client map outside Cognito and resolve it before you start the auth flow.

## The models

**Pool per tenant** — maximum isolation; independent MFA/password/branding/threat-protection per tenant; the same person signs up separately per tenant (separate profiles). High effort: you must standardize and automate config (CloudFormation/CDK) across many pools, and build UI that routes a user to the right pool.

**App client per tenant** — one shared pool, one app client per tenant. Any user can sign in to any client (one profile), and each client can enable a **tenant-specific IdP**. Universal pool-level settings (triggers, password policy, messaging) apply to all. Good for users who move between apps. Watch the hosted-UI cookie trap below.

**Group per tenant** — one shared pool/app client, a group per tenant. Shines when authentication's real output is **temporary AWS credentials from an identity pool**: group membership (`cognito:groups`, and `cognito:roles`/`cognito:preferred_role` in the ID token) selects the IAM role, e.g. each tenant's group grants read on its own S3 bucket. Low effort for IAM-role selection; beyond that you write app logic (or use AVP) to act on group claims. Note: AVP's `IsAuthorizedWithToken` doesn't natively process group identifiers — parse them in custom code if needed.

**Custom attribute per tenant** — `custom:tenantId` on each user in a shared pool; one distributable URL. After sign-in the app reads the `custom:tenantId` claim to pick assets/branding/features. Not real isolation — anything that must differ at pool/app-client level (MFA, branding) can't be expressed by an attribute. Push authorization to the app or to AVP. The tenant attribute **must be immutable/read-only** (see security).

**Custom scope per tenant** — for **M2M** (client-credentials) tenants. Define tenant scopes on a resource server and grant each tenant's confidential app client only its scopes; access tokens then carry tenant + API-permission scopes. Best practice: make a resource server **exclusive to one app client**. Two request styles:
- **Client-dependent** — omit the `scope` parameter at the token endpoint and the client receives *all* scopes assigned to it (tenancy baked into the client config).
- **Request-dependent** — the app requests only the subset of its scopes it needs per call (`scope=TenantBatch1/tenant1 resource1/readScope`), allowing shared scopes across tenants.

Scopes are formatted `<resource-server-id>/<name>` — parse the *name* consistently for the tenancy decision (the resource-server id usually isn't relevant). Scopes can also drive request logging, indicate which APIs the client may call, and flag active customers. Provision with `AWS::Cognito::UserPoolResourceServer` + a `client_credentials` app client (see [iac.md](iac.md), [backend.md](backend.md#machine-to-machine)).

## The hosted-UI cookie cross-tenant trap

Managed login / hosted UI sets a **one-hour session cookie** scoped to the **user pool**, not the app client. A local user who signs in to one app client can be silently signed into **any other app client in the same pool** within that hour. This breaks isolation for app-client-per-tenant and group/attribute models. Two fixes:
- **Separate tenants into different user pools**, or
- **Use the Cognito user pools API (SDK) for sign-in** instead of hosted UI.

Also enforce **1:1 mapping between a tenant's external IdP and its app client** — a federated user with a valid session cookie can otherwise reach other tenant apps that trust the same IdP.

## Quotas are shared

Cognito [quotas](quotas.md) are **per account + Region**, shared across all tenants in a single-Region design. Size for total tenant volume; buy additional request-rate quota if needed, or split tenants across accounts/Regions for separate quotas (also gives max isolation and lower latency for distributed users). SNS (SMS) and SES (email) config and Lambda triggers are per-Region and shared across tenants in that Region.

## Security recommendations

- **Validate tenancy with Amazon Verified Permissions** — write Cedar policies that check the pool/app-client/group/attribute entitlement before allowing a request ([verified-permissions.md](verified-permissions.md)).
- **Only trust *verified* email/phone** for domain-based tenant routing — never authorize a tenant from an unverified attribute (or one without IdP-provided proof).
- **Tenant-identifying custom attributes must be immutable and read-only to the app client** — immutable values are settable only at user creation/sign-up, preventing a user from moving themselves between tenants.
- **1:1 external IdP ↔ app client** to prevent cross-tenant access via a shared session cookie.
- **Users can't modify the tenant-matching criteria** — lock down the attributes/logic that authorize tenant access; restrict tenant IdP admins from altering user access.
- **Define tenant attributes *in Cognito*, never mapped from the external IdP** — a mapped `custom:tenantId` lets a compromised/misconfigured IdP claim membership in another tenant. Map only user-level attributes (name, email, groups) from IdPs; set tenant context yourself (admin API, or a pre-token-gen trigger keyed on the app client/pool).
- **Custom attributes are identity, not a database** — don't store frequently-changing per-tenant state in them (each change is a rate-limited directory write, capped at 50 attrs/pool). Keep mutable tenant state in your own datastore, keyed on `sub`.
