# Security Best Practices (User Pools)

Hardening a user pool. Baseline: apply least privilege to admin operations, protect application/user secrets, and put AWS WAF in front of a public-facing pool. Token verification lives in [backend.md](backend.md); this file is configuration and operational hardening.

## Table of Contents
1. [Controlling public access](#controlling-public-access)
2. [Network protection (WAF) & SMS abuse](#network-protection-waf--sms-abuse)
3. [Secrets](#secrets)
4. [Least-privilege IAM](#least-privilege-iam)
5. [Token handling](#token-handling)
6. [Data protection & encryption](#data-protection--encryption)
7. [Which IdPs to trust](#which-idps-to-trust)
8. [Scopes](#scopes)
9. [Input & attribute hygiene](#input--attribute-hygiene)
10. [Monitoring & logging](#monitoring--logging)
11. [Checklist](#checklist)

---

## Controlling public access

A pool with self-service sign-up is open to the internet — anyone can `SignUp`/`InitiateAuth` or use managed login. Levers to constrain that surface:

| Setting | Where | Effect | API param |
|---|---|---|---|
| Self-service sign-up | pool | Off ⇒ admins create all users | `AdminCreateUserConfig.AllowAdminCreateUserOnly` |
| Admin confirmation | pool | Require admin to confirm new users | `AccountRecoverySetting` / `admin_only` |
| **Prevent user existence errors** | app client | Hide "user not found" (stops account enumeration) | `PreventUserExistenceErrors: ENABLED` |
| Client secret | app client | Require secret hash on auth calls | `GenerateSecret` |
| Supported IdPs | app client | Exclude local or federated users per client | `SupportedIdentityProviders` |
| Domain / authorization server | pool | **Creating *any* domain exposes public webpages**; omit a domain for SDK-only | `CreateUserPoolDomain` |
| WAF web ACL | pool | Filter/CAPTCHA/block before requests hit Cognito | `AssociateWebACL` |
| Threat protection | pool/client | Auto-block or force MFA on risk (Plus plan) | `SetRiskConfiguration` |

Key nuance: **if you want SDK-only auth, don't create a domain** — a domain turns on public sign-in pages for every app client.

**Other pool safeguards:**
- **Deletion protection** (`DeletionProtection: ACTIVE`) — blocks pool deletion until you flip it to `Inactive` via `UpdateUserPool` (else `DeleteUserPool` → `InvalidParameterException`; the console offers to deactivate + delete in one prompt). **Console-created pools default to `ACTIVE`; API/CLI-created pools default to `INACTIVE`** — set it explicitly in IaC.
- **Multi-Region replication** — replica pool in a second Region for DR/failover ([multi-region.md](multi-region.md)); distinct from SMS/SES alternate-Region routing.
- **Case sensitivity** — case-insensitive pools stop `JohnD` vs `johnd` duplicate accounts; fixed at creation ([getting-started.md](getting-started.md#decisions-you-cant-undo)).
- **MFA & adaptive auth** — require or risk-trigger a second factor ([mfa.md](mfa.md), [threat-protection.md](threat-protection.md)); trust devices to skip it ([devices.md](devices.md)).

### User existence errors (anti-enumeration)

`PreventUserExistenceErrors` stops attackers probing which accounts exist. **Default is `LEGACY` (disabled) via the API/CLI, but `ENABLED` in the console** — set it on every client.

- **`ENABLED`**: password flows (`USER_PASSWORD_AUTH`/`ADMIN_USER_PASSWORD_AUTH` and `USER_AUTH`'s `PASSWORD`) return `NotAuthorizedException` "Incorrect username or password" for a bad *or nonexistent* user — never `UserNotFoundException`. `ForgotPassword` returns a **simulated** `CodeDeliveryDetails` for unknown/disabled users; imported users get the generic error instead of `PasswordResetRequiredException`.
- **Choice-based `USER_AUTH` is *unaffected*** by this setting — it always returns a *random* valid challenge for a nonexistent user (you can't suppress it via config), so it never leaks existence anyway.
- **SRP caveat:** existence suppression is only reliable for `USER_SRP_AUTH`/`PASSWORD_SRP` in pools **without alias attributes** — with aliases, use the username-password flows, which fully suppress. (SRP returns a deterministic simulated salt + UUID for unknown users.)
- **`SignUp` always throws `UsernameExistsException`** for a taken *username* — but in an **alias-attribute** pool, a duplicate *email/phone* does **not** error at `SignUp` (it errors as `AliasExistsException` only at `ConfirmSignUp`, after proving ownership), so the public `SignUp` API can't be used to enumerate emails/phones.
- **Lambda triggers** (pre-auth, custom-auth, migrate) receive a `UserNotFound: true` flag so you can simulate challenges for nonexistent users in `CUSTOM_AUTH`.

## Network protection (WAF) & SMS abuse

**AWS WAF web ACLs** front managed login / classic hosted UI **and** the public (unauthenticated / session- / access-token-authorized) API operations — `Admin*` IAM-authorized ops are out of scope. This is your **volumetric / rate-limit** layer; app-layer risk scoring is [threat protection](threat-protection.md), which explicitly does **not** rate-limit.

- **Available on all feature plans** (threat protection is Plus-only) and complements it. One web ACL per pool, same Region, billed separately. **Bot Control** managed rules are effective on the token/auth endpoints (esp. against M2M/credential abuse).
- **Associate with the WAFv2 `AssociateWebACL` API** — there's no Cognito-native op. IAM needs `cognito-idp:AssociateWebACL`/`GetWebACLForResource`/`ListResourcesForWebACL` **plus** `wafv2:*` equivalents (these `cognito-idp` actions are permission-only, not real API calls). New web ACLs take seconds–minutes to propagate (`WAFUnavailableEntityException` until then).
- **Blocked requests don't count toward the request-rate quota** — WAF runs *before* API throttling, so it's a real cost/DDoS lever.
- **WAF can't see PII** — usernames, passwords, emails, phone numbers aren't forwarded. Match on IP, user-agent, headers, path, and the **operation** (`x-amzn-cognito-operation-name`) / client (`x-amzn-cognito-client-id`) headers.
- **Rule-action results:** managed login can show a **CAPTCHA** and a custom status/body; API `Block`/`CAPTCHA` returns **`ForbiddenException`**. Custom block responses only apply to the **first** managed-login request.
- **You can't attach an ACL using WAF Fraud Control ATP** (`AWS-AWSManagedRulesATPRuleSet`) to a user pool.
- **Gotcha — CAPTCHA breaks managed-login TOTP setup**: exclude `x-amzn-cognito-operation-name` values `AssociateSoftwareToken` and `VerifySoftwareToken` from any CAPTCHA rule ([mfa.md](mfa.md)).
**SMS pumping / sign-up fraud** — public sign-up + SMS codes can be abused to inflate SMS traffic (toll fraud) and your bill. Defend in layers:
- **Cap the blast radius:** set **SNS/End User Messaging monthly spend limits** (a hard cost ceiling) and **SMS Protect country rules** (allow/block/filter by destination country) so high-risk regions can't be targeted.
- **Block bots at the edge:** WAF **targeted Bot Control**, IP deny-lists, rate-based rules, and **JA3/JA4 TLS-fingerprint** matches (catch a client across rotating IPs).
- **Validate before you spend an SMS:** in a **pre sign-up trigger**, reject **VoIP/invalid/unsupported-region** numbers (phone-number validation) and suspicious area codes; require a **CAPTCHA token passed via `ClientMetadata`** on `SignUp` and verify it there.
- **Detect:** alarm on `UserCreation` rate and SMS volume; a gap between `SignUp`/`ResendConfirmationCode` and completed **`ConfirmSignUp`** (unfinished verifications) is the classic pumping signature — query it in CloudTrail ([monitoring.md](monitoring.md)).
- **Reduce SMS dependence:** prefer **email OTP/MFA or passkeys**; use **user-initiated OTP** (user texts *your* number) or a **custom SMS sender** to route through a channel you control.

## Secrets

- **App client secret** — only for confidential clients (server-side) and M2M, where the app is the sole holder. Store it encrypted / in AWS Secrets Manager. **Never embed a secret in a public (browser/mobile) client** — it's inspectable and lets attackers create users and trigger password resets.
- **Passwords** — treat as opaque; pass straight through to the pool. Never put passwords or hashes in local storage. Prefer **passkeys**; if you must use passwords, use **SRP + MFA**, not `USER_PASSWORD_AUTH`.
- **AWS credentials** — server-side only. Never encode in public clients or commit to version control (GitHub). Use temporary credentials.
- **PKCE code verifier** — generate a **new random verifier per authorization request**; never static/predictable, never exposed to the user. Required protection for public-client authorization-code flows ([managed-login.md](managed-login.md)).

## Least-privilege IAM

Two facts that surprise people (see the [authorization models table](auth-flows.md#authorization-models)):
- **Only `Admin*` (server-side) operations are IAM-gated.** Public/token-authorized operations like `InitiateAuth`, `SignUp`, `GetUser` **ignore IAM** — you can't restrict them with a policy. Control those with app-client settings instead.
- **Resource granularity is the pool (and identity pool) only** — you **cannot** scope IAM permissions to an individual app client. Permissions apply across all clients in the pool. If your security model needs per-tenant admin separation, use **one user pool per tenant** ([multi-tenancy.md](multi-tenancy.md)).

Scope admin roles tightly. Example — a "pool-config admin" that manages IdPs/resource servers/app clients/domain but not users:
```json
{
  "Effect": "Allow",
  "Action": [
    "cognito-idp:CreateIdentityProvider", "cognito-idp:UpdateIdentityProvider", "cognito-idp:DeleteIdentityProvider",
    "cognito-idp:CreateResourceServer", "cognito-idp:UpdateResourceServer", "cognito-idp:DeleteResourceServer",
    "cognito-idp:UpdateUserPoolClient", "cognito-idp:CreateUserPoolDomain", "cognito-idp:UpdateUserPoolDomain",
    "cognito-idp:Describe*", "cognito-idp:List*", "cognito-idp:SetUICustomization", "cognito-idp:UpdateManagedLoginBranding"
  ],
  "Resource": "arn:aws:cognito-idp:us-west-2:123456789012:userpool/us-west-2_EXAMPLE"
}
```
Grant a separate role the `AdminAddUserToGroup`/`AdminCreateUser`/`AdminInitiateAuth`/`AdminSetUserPassword`/`RevokeToken`/… actions for user management + server-side auth.

## Token handling

- **Don't store ID or access tokens in local storage** — they carry group/attribute data you may not want exposed, and localStorage is XSS-reachable. Keep access tokens in memory; refresh tokens in an httpOnly cookie (BFF) when possible ([web-frontend.md](web-frontend.md)).
- **Revoke refresh tokens** on sign-out or when a session should not persist (`RevokeToken` / `AdminUserGlobalSignOut`).
- **Only authorize with tokens you independently verify** as valid and unexpired ([backend.md](backend.md)). Refresh tokens are pool-encrypted and opaque.

## Data protection & encryption

- **In transit:** all Cognito endpoints require **TLS 1.2** (1.3 recommended), PFS ciphers. Managed login is served from AWS-managed CloudFront — don't pin its certs ([managed-login.md](managed-login.md)).
- **At rest (default):** all user-pool and identity-pool data is encrypted with an **AWS-owned key** automatically. Identity pools **can't** change this.
- **At rest (customer-managed key):** user pools can instead use a **customer-managed KMS key** — required for [multi-Region replication](multi-region.md). Constraints: **symmetric**, **same Region** as the pool, referenced by **key ARN (not alias)**; single- or multi-Region keys allowed. Set via `KeyConfiguration` (`KeyType: CUSTOMER_MANAGED_KEY | AWS_OWNED_KEY`, `KmsKeyArn`) on `Create/UpdateUserPool` — a `DescribeUserPool` with no `KeyConfiguration` means AWS-owned. The **key policy must trust the `cognito-idp.amazonaws.com` + `identitystore.amazonaws.com` service principals** (scoped by `aws:SourceArn` = pool ARN and the `kms:EncryptionContext:aws:cognito-idp:userpool-arn`); add `logs`/`delivery.logs` grants if you also encrypt exported logs.
- **Searchable encryption:** Cognito can HMAC-index PII attributes (`sub`, `email`, `phone_number`, `given_name`, `family_name`, `name`, `username`, `preferred_username`, `cognito:user_status`) so `ListUsers` filters still work under encryption — computed with the pool's KMS key.
- **Next-gen infrastructure** (rolling out, no action needed) is what unlocks customer-managed keys, MRR, and scale to tens of millions of users / thousands of TPS per pool.
- **Never put PII/secrets in free-form attribute fields** — they can surface in diagnostic logs, and Cognito does **not** auto-mask them (only passwords/tokens are redacted in CloudTrail; see [monitoring.md](monitoring.md#cloudtrail)).

## Which IdPs to trust

- **SAML / OIDC** IdPs can create users, set attributes, and reach your resources — appropriate for B2B/enterprise where you or your customer controls the directory.
- **Social** IdPs let anyone on the internet in. Only enable a social IdP on an app client when you're ready for **public** sign-up.

## Scopes

Request the **minimum scopes** an app needs. Notable ones:
- `aws.cognito.signin.user.admin` — present in all SDK-auth access tokens; authorizes **self-service** profile ops (`GetUser`, `UpdateUserAttributes`). Its power is bounded by the app client's per-attribute read/write permissions.
- `openid` — requests an **ID token**; omit it and Cognito issues only access (+ refresh) tokens. Requested alone it returns all userInfo attributes; adding `profile`/`email`/`phone` narrows the returned attributes to those scopes.

## Input & attribute hygiene

- Validate user-submitted **string attribute** values client-side before writing them — guard against injecting unwanted data into your directory or into the emails/SMS Cognito sends.
- When mapping IdP claims to pool attributes, **only map secure, predictable IdP attributes** ([federation.md](federation.md)).
- Set attributes that gate authorization (e.g. tenant id) as **immutable / read-only to the app client**.

## Monitoring & logging

Full detail — CloudTrail event types, CloudWatch metrics, and log export — in **[monitoring.md](monitoring.md)**. Security highlights:
- **CloudTrail** audits both the API (`AwsApiCall`) and managed-login endpoints (`AwsServiceEvent`, e.g. `Token_POST`); use Logs Insights to spot credential-stuffing (top IPs on `NotAuthorizedException`) and dormant M2M clients.
- **`userNotification` log export** (any plan) surfaces email/SMS **delivery failures**; **`userAuthEvents`** (Plus + threat protection) exports risk/activity logs ([threat-protection.md](threat-protection.md#event-history-feedback--log-export)).
- Alarm on the `AWS/Usage` `ThrottleCount` metric to catch quota exhaustion ([quotas.md](quotas.md)).
- (Amazon Pinpoint analytics is **deprecated** — EOL 2026-10-30; use CloudWatch/threat-protection logs instead. See [app-clients.md](app-clients.md).)

## Checklist

- [ ] `PreventUserExistenceErrors: ENABLED` on every app client
- [ ] No secret on public clients; secrets in Secrets Manager
- [ ] No domain if SDK-only; WAF on public pools
- [ ] Tokens verified server-side; ID/access tokens not in localStorage; refresh tokens revoked on sign-out
- [ ] Passkeys or SRP+MFA, never plain `USER_PASSWORD_AUTH` for real users
- [ ] Admin IAM roles least-privileged; per-tenant admin separation ⇒ pool per tenant
- [ ] Social IdPs enabled only when public sign-up is intended
- [ ] Minimum scopes; tenant-identifying attributes immutable
