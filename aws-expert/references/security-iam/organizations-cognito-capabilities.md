# AWS Organizations & Amazon Cognito — Capabilities Reference
For CLI commands, see [organizations-cognito-cli.md](organizations-cognito-cli.md).

## AWS Organizations

**Purpose**: Manage multiple AWS accounts as a unit; apply governance policies across the org.

### Key Concepts

| Concept | Description |
|---|---|
| **Management account** | The root account; creates the org; not subject to SCPs |
| **Member account** | Any account in the org; subject to SCPs |
| **OU (Organizational Unit)** | Hierarchical grouping of accounts; policies applied to OU affect all child accounts |
| **SCP (Service Control Policy)** | Guardrails; define maximum permissions for accounts in OU/org |
| **Tag policy** | Enforce tag key/value standards across accounts |
| **Backup policy** | Define backup plans and apply them across accounts |
| **AI opt-out policy** | Control whether AWS AI services can use your data |
| **Delegated administrator** | Assign a member account to manage a specific AWS service (e.g., Security Hub) |

### SCP Behavior

- SCPs **do not grant permissions** — they define the maximum allowed
- Management account is **never** affected by SCPs
- An allow in an SCP still requires an allow in the IAM policy
- SCPs affect all principals in member accounts, including root user
- Commonly used to: deny leaving the org, require encryption, restrict regions, deny disabling security services

### Key Patterns

```json
// Deny all actions outside approved regions
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    },
    "ArnNotLike": {
      "aws:PrincipalARN": ["arn:aws:iam::*:role/BreakGlassRole"]
    }
  }
}
```

---

## Amazon Cognito

**Purpose**: Add user authentication and authorization to web and mobile apps.

### Two Services in One

| Service | Description |
|---|---|
| **User Pools** | User directory with sign-up, sign-in, MFA, social federation; issues JWTs |
| **Identity Pools** | Exchange tokens (Cognito, Google, SAML, OIDC) for temporary AWS credentials via STS |

### User Pools — Key Features

| Feature | Description |
|---|---|
| **Hosted UI** | Pre-built sign-in/sign-up pages; supports OAuth 2.0 flows |
| **Social federation** | Sign in with Google, Facebook, Apple, Amazon |
| **SAML/OIDC federation** | Enterprise SSO integration |
| **Lambda triggers** | Customize auth flows (pre-sign-up, pre-authentication, post-confirmation, etc.) |
| **Advanced Security** | Risk-based adaptive authentication; compromised credential detection |
| **App clients** | Configure per-app OAuth scopes, token expiry, redirect URIs |
| **Groups** | Assign users to groups; include group claims in tokens; map to IAM roles |
| **MFA** | TOTP, SMS; required or optional per pool or user |
| **User migration trigger** | Lazily migrate users from legacy user store without password reset |

### Identity Pools — Key Features

- Exchange any supported token for temporary AWS credentials (via STS)
- **Authenticated role**: IAM role for verified users
- **Unauthenticated role**: IAM role for guest users (optional)
- **Role-based access control**: Map Cognito groups or token claims to different IAM roles
- **Attribute access control**: Pass user attributes as session tags for ABAC

### Token Types (User Pools)

| Token | Contents | Typical expiry |
|---|---|---|
| **ID token** | User identity claims (name, email, groups) | 1 hour |
| **Access token** | OAuth scopes; used for API authorization | 1 hour |
| **Refresh token** | Used to obtain new ID/access tokens | 30 days (configurable) |
