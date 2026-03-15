# AWS STS & IAM Identity Center — Capabilities Reference
For CLI commands, see [sts-identity-center-cli.md](sts-identity-center-cli.md).

## AWS STS

**Purpose**: Issues temporary security credentials for roles, federated users, and cross-account access.

### Key Operations

| Operation | Use |
|---|---|
| `AssumeRole` | Assume a role in same or different account |
| `AssumeRoleWithWebIdentity` | OIDC federation (GitHub Actions, Google, Cognito) |
| `AssumeRoleWithSAML` | SAML 2.0 federation (Okta, ADFS, Azure AD) |
| `GetSessionToken` | Temporary creds for IAM user (useful for MFA enforcement) |
| `GetFederationToken` | Long-lived temp creds for custom identity broker |
| `DecodeAuthorizationMessage` | Decode encoded error messages from authorization failures |

### Temporary Credential Duration

- `AssumeRole`: 15 min – 12 hours (default 1 hour; max set on role)
- `GetSessionToken`: 15 min – 36 hours
- `GetFederationToken`: 15 min – 36 hours

---

## AWS IAM Identity Center

**Purpose**: Centralized SSO for the AWS console, CLI, and business applications (formerly AWS SSO).

### Key Concepts

| Concept | Description |
|---|---|
| **Instance** | The Identity Center deployment (one per org, or account-level for standalone) |
| **Permission set** | A collection of IAM policies; becomes an IAM role in each account when assigned |
| **Account assignment** | Maps a user/group + permission set → AWS account |
| **Application assignment** | Maps a user/group → SAML/OIDC application |
| **Identity source** | Where users/groups are managed: built-in directory, Active Directory, or external IdP |

### Identity Sources

| Source | Description |
|---|---|
| **Identity Center directory** | Built-in; manage users/groups directly in Identity Center |
| **Active Directory** | AWS Managed AD or self-managed AD via AD Connector |
| **External IdP** | Any SAML 2.0 provider (Okta, Azure AD, Ping) via automatic provisioning (SCIM) |

### Capabilities

- **Multi-account access**: One login → access to all assigned AWS accounts with the right permission set
- **CLI SSO integration**: `aws sso login` + `aws configure sso` for local credentials
- **Trusted identity propagation**: Pass the user's identity to data services (Redshift, S3 Access Grants, EMR) for fine-grained data access control
- **ABAC support**: Tag users and use `aws:PrincipalTag` in permission set policies
- **MFA**: Enforce at the Identity Center level (TOTP, FIDO2/WebAuthn, SMS)
- **Access portal**: Managed web portal for users to sign in and access assigned accounts/apps
