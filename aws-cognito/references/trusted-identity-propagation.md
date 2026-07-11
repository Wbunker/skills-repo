# Trusted Identity Propagation (IAM Identity Center)

Propagate a **signed-in user's identity** (not just an app's IAM role) into AWS analytics/data services so they authorize on the *user's* group memberships and grants. Use when a Cognito-authenticated user must reach **Amazon Q Business, Athena, Redshift, QuickSight, AWS Lake Formation, or S3 Access Grants** with per-user/per-group access. This is distinct from [identity pools](identity-pools.md) (which map to a *shared* IAM role) — here the downstream service sees the actual user via **IAM Identity Center (IdC)**.

## How it works

Cognito acts as a **trusted token issuer** to IAM Identity Center; the app swaps a Cognito token for an IdC token, then opens an **identity-enhanced STS session**:

1. User signs in to your app via Cognito (often Cognito itself federates to IdC over SAML, auto-provisioning the profile — no separate directory to maintain).
2. App receives a Cognito **JWT** (ID or access token) with a claim that maps to an **existing IdC user** — typically `email` (or an external ID).
3. App calls the OIDC **token-exchange** (`CreateTokenWithIAM`) to swap the Cognito JWT for an **IdC token**. A given token can be **exchanged only once**.
4. App assumes an IAM role and calls `sts:AssumeRole`/`sts:SetContext` (via `sso-oidc`) to attach the IdC context, producing an **identity-aware** session.
5. App calls the data service (e.g. Q Business) with that session; the service authorizes on the **user's IdC identity + group memberships**, applying fine-grained grants.

## Setup essentials

- In **IAM Identity Center → trusted token issuers**, register your Cognito user pool by its **OIDC issuer URL** ([oauth-endpoints.md](oauth-endpoints.md#oidc-issuer-original-vs-updated)) and map the Cognito claim (e.g. `email`) → the IdC user attribute.
- Create an **IdC OAuth application** that grants token-exchange **only** for specific trusted issuers and **audiences** (the app client). Scope it tightly.
- The Cognito user must correspond to a **provisioned IdC user** — the claim you map must resolve to a real IdC identity, or the exchange fails.

## Non-obvious points

- **Exchange-once:** each Cognito token yields exactly one IdC token — re-exchanging is rejected; refresh the Cognito session for a new one.
- **Two authorization layers:** the IAM role gates *what the app can call*; the propagated IdC identity gates *what the user can see* — both apply.
- This is an **enterprise/analytics** pattern; for ordinary API authorization use JWT verification ([backend.md](backend.md)) or [Verified Permissions](verified-permissions.md); for direct AWS-resource access with a shared role use an [identity pool](identity-pools.md).
</content>
