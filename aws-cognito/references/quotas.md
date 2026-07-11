# Quotas & Limits

The numeric limits you actually hit, plus the request-rate model. All quotas are **per account, per Region** (a Tokyo increase doesn't help N. Virginia). Track usage in the **Service Quotas** console; adjustable RPS categories also expose a self-service provisioning API.

## Table of Contents
1. [API request-rate quotas (RPS)](#api-request-rate-quotas-rps)
2. [Provisioned limits (self-service RPS)](#provisioned-limits-self-service-rps)
3. [Per-user & per-domain limits](#per-user--per-domain-limits)
4. [Resource limits](#resource-limits)
5. [Session, token & code validity](#session-token--code-validity)
6. [Monthly active users (MAU)](#monthly-active-users-mau)

---

## API request-rate quotas (RPS)

Operations are **pooled by category** — one shared RPS budget per category across all pools in the account+Region. Defaults (RPS), most-hit ones:

| Category | Default | Adjustable | Includes |
|---|---|---|---|
| **UserAuthentication** | 120 | yes | `InitiateAuth`, `AdminInitiateAuth`, `RespondToAuthChallenge`, hosted-UI sign-in |
| **UserCreation** | 50 | yes | `SignUp`, `ConfirmSignUp`, `AdminCreateUser`, `AdminConfirmSignUp` |
| **UserFederation** | 25 | yes | IdP-response ops (all SAML; OIDC/social token results) |
| **UserAccountRecovery** | 30 | no | password reset/change |
| **UserRead** | 120 | yes | read a user |
| **UserToken** | 120 | yes | token management |
| **UserList** | 30 | no | `ListUsers` |
| **ClientAuthentication** | 150 | no | **M2M `client_credentials`** token requests |
| **LimitManagement** | 1 | no | the provisioning API itself |

- **`RespondToAuthChallenge` gets 3× the `UserAuthentication` limit** (to absorb multi-round MFA/custom-auth challenges); overflow beyond 3 responses/auth spills back into the category. A `NEW_PASSWORD_REQUIRED` response counts toward `UserAccountRecovery`, not `UserAuthentication`.
- Some `UserPool*Resource*`/`UserPoolClient*` categories are additionally capped at **5 RPS per single user pool**.
- On throttling, back off + retry (SDKs do this), cache tokens/JWKS, and offload hot custom attributes to your own DB. Raising a Cognito category may require **raising SES/SNS quotas too**.

## Provisioned limits (self-service RPS)

Adjustable categories use a **two-tier** model — raise the *account-level max* once via Service Quotas (some auto-approved, else ~10 days), then set your live rate yourself with **`UpdateProvisionedLimit`** (takes effect immediately; `GetProvisionedLimit` reads it). `LimitDefinition` = `{LimitClass: "API_CATEGORY", Attributes: {Category: "UserAuthentication"}}`.

- **You're billed for provisioned capacity above the free default**, prorated by time — drop it back down when the surge ends.
- **Managed-login pools can't provision `UserAuthentication`/`UserFederation`** via the API — use a Service Quotas request instead.
- IAM: `cognito-idp:GetProvisionedLimit`/`UpdateProvisionedLimit`. Cross-account not supported.

## Per-user & per-domain limits

**Per user** (not adjustable): **10 RPS read** (`GetUser`, `InitiateAuth`, `RespondToAuthChallenge`, `GetDevice`) and **10 RPS write** (`UpdateUserAttributes`, …) — a single user can't be hammered faster than this.

**Per user-pool domain** (managed login / OAuth endpoints, not adjustable):

| Limit | Default |
|---|---|
| Requests from one source IP → one domain | 300 RPS |
| Requests for one app-client ID → one domain | 300 RPS |
| Requests to one domain (total) | 500 RPS |
| `jwks.json` requests (account/Region) | 50,000 RPS |

## Resource limits

| Resource | Default | Adjustable → max |
|---|---|---|
| Users per pool | 40,000,000 | yes → contact AWS |
| User pools per Region | 1,000 | yes → 10,000 |
| App clients per pool | 1,000 | yes → 10,000 |
| Identity providers per pool | 300 | yes → 1,000 |
| Resource servers per pool | 25 | yes → 300 |
| **Custom attributes per pool** | **50** | **no** |
| Chars per attribute value | 2,048 | no |
| Custom-attribute name length | 20 | no |
| Groups per pool | 10,000 | no |
| Groups per user | 100 | no |
| Linked identities per user | 5 | no |
| Passkeys per user | 20 | no |
| Callback/logout URLs per app client | 100 each | no |
| Scopes per resource server / per app client | 100 / 50 | no |
| **Custom domains per Region** | **4** | no |
| SAML response length | 100,000 chars | no |
| Pre-token-gen combined claims+scopes changes | 5,000 | yes |
| Default-config emails/day (account) | 50 | no (use SES) |

CSV import: 16,000 chars/row, 100 MB file, 500,000 users, 1,000 jobs/pool ([user-management.md](user-management.md#importing-users)).

## Session, token & code validity

| Artifact | Range |
|---|---|
| ID / access token | 5 min – 1 day |
| Refresh token | 1 hour – 3,650 days (10 yr) |
| Hosted-UI/managed-login session cookie | **1 hour (fixed)** ([tokens.md](tokens.md#managed-login-cookie-floor)) |
| Auth-flow session token (between challenges) | 3–15 min |
| Sign-up / attribute-verification code | 24 hours |
| MFA code | 3–15 min |
| Forgot-password code | 1 hour |

Per-user/hour code caps: `ForgotPassword`/`ConfirmForgotPassword` 5–20 (risk-scaled), `ResendConfirmationCode` 5, `ConfirmSignUp` 15, `ChangePassword` 5, `GetUserAttributeVerificationCode` 5, `VerifyUserAttribute` 15.

## Monthly active users (MAU)

Billing unit. A user is an MAU if, in a calendar month, **any** of these touch them: sign-up/admin-create, confirmation/verification, **sign-in or challenge response**, sign-out/revocation, self-service or admin password *set*, attribute/group change, or `AdminGetUser`.

- **Not** MAU-generating: **CSV import**, `AdminResetUserPassword`, `ListUsers`, and access-token-authorized self-service ops (though the sign-in that issued the token already counted them).
- **`AdminGetUser` counts a user as active (costs); `ListUsers` doesn't** — bulk-read with `ListUsers` or an external store, not per-user `AdminGetUser`.
- **Federated (SAML/OIDC) linked users bill as `EnterpriseMAU`.** Feature-plan changes mid-month bill each MAU at the **highest-priced tier** they were active under.
- Review MAUs in the Billing console (filter service = Cognito) — the key input to right-sizing RPS quotas.
</content>
