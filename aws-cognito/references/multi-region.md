# Multi-Region Replication (MRR)

Business-continuity / DR: run a **replica user pool** in a second Region that shares one user directory and can serve authentication during a primary-Region outage. A specialized availability feature — distinct from the SMS/SES alternate-Region *routing* in [messaging.md](messaging.md).

## Architecture

- Replicas **share one user pool ID**. The **primary** is authoritative for admin config and all **writes** (sign-up, admin-create, password reset, profile edits). **Secondary** replicas are read/auth-only.
- A new secondary starts **`INACTIVE`** — configure regional settings, then flip to `ACTIVE` for production.
- At most **one secondary** per user directory.
- Primary→secondary sync is **eventually consistent** (brief delay on settings + directory updates).

## Prerequisites

- **Essentials or Plus** feature plan (not Lite) — MRR is a paid add-on.
- A **multi-Region KMS customer-managed key**, present in every replica Region.
- A **multi-Region ("updated") OIDC issuer** (`issuer-cognito-idp.<region>...`) so tokens validate consistently across Regions — **but it's incompatible with ALB auth and API Gateway Cognito authorizers** ([oauth-endpoints.md](oauth-endpoints.md#oidc-issuer-original-vs-updated)).
- **Eligibility:** MRR needs Cognito's next-gen infrastructure. Older pools are ineligible until AWS upgrades them — the console shows config options on eligible pools, an exception message on others.

## Regional vs. synced settings

Only these can differ per replica (everything else is set on the primary and synced):

`Email config` · `Threat-protection email config` · `SMS config` · `Lambda triggers` · `Tags` · `Log-export config` · `AWS WAF web ACL`.

## Limitations

- **No user creation in a secondary** (sign-up or admin). A federated user can sign in to a secondary during failover **only if they've signed in to the primary before**.
- **No password reset / profile edit in a secondary** — disable those in your UI during failover, re-enable when the primary is healthy.
- **TOTP MFA isn't supported in a secondary** — TOTP users can only authenticate while the primary Region is serving.
- **Failed-login lockout counts aren't synced** — each replica counts independently.
- **Automatic failover requires a [custom domain](domains.md)** (it's the endpoint that serves the OAuth/`/authorize`/`/token` endpoints and handles IdP responses). Prefix domains can only be tested manually per-Region.

## Setup & failover

Create and activate the replica:
```jsonc
// CreateUserPoolReplica
{ "UserPoolId": "us-east-1_EXAMPLE", "RegionName": "us-west-2",
  "UserPoolTags": { "Environment": "Production" } }
// → Replica.Status starts "PENDING_CREATE", Role "SECONDARY"

// UpdateUserPoolReplica — go live
{ "UserPoolId": "us-east-1_EXAMPLE", "RegionName": "us-west-2", "Status": "ACTIVE" }
```

**Failover is driven by a Route 53 health check** you attach to the custom domain (`UpdateUserPoolDomain` with `Routing.Failover.{SecondaryRegion, PrimaryRoute53HealthCheckId}`, or console **Domain → Edit multi-Region failover**). **You own what the health check tests.** When it goes unhealthy, Cognito serves the custom domain (managed login + auth) from the secondary; when healthy, it routes back to primary. The DNS CNAME still points at the CloudFront alias; the health check — not DNS — decides which replica answers.

**API/SDK callers have no custom domain**, so **your app** must route calls to the right Regional service endpoint — reuse the same Route 53 health check as the signal, ideally decided in a backend/BFF rather than a bare SPA.
</content>
