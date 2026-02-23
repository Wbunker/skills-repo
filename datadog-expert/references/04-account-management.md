# Account Management

Reference for user management, roles, organizations, SSO, and API keys in Datadog.

## Table of Contents
- [Managing Users](#managing-users)
- [Roles and Permissions](#roles-and-permissions)
- [Organizations](#organizations)
- [Single Sign-On](#single-sign-on)
- [API and Application Keys](#api-and-application-keys)
- [Usage Tracking](#usage-tracking)
- [Best Practices](#best-practices)

## Managing Users

### Invite Users
Organization Settings > Users > Invite Users

User attributes:
- Email address (login identifier)
- Role assignment (one or more roles)
- Team membership

### User Roles (Default)
| Role | Permissions |
|------|------------|
| **Admin** | Full access: manage users, billing, org settings, all data |
| **Standard** | Read/write access to most features; cannot manage users or billing |
| **Read Only** | View dashboards, metrics, logs; cannot create or modify |

## Roles and Permissions

### Custom Roles
Create granular roles with specific permissions:

```
Organization Settings > Roles > New Role
```

**Permission categories:**
- **Dashboards**: create, edit, delete, share
- **Monitors**: create, edit, delete, mute
- **Logs**: read data, write pipelines, manage indexes
- **APM**: read traces, manage retention
- **Synthetics**: create, edit, delete tests
- **Security**: manage rules, view signals
- **Notebooks, SLOs, Incidents**: CRUD operations

### RBAC Best Practices
- Use the principle of least privilege
- Create team-specific roles (e.g., `frontend-team` with APM + RUM access)
- Use role inheritance to build on default roles
- Audit role assignments quarterly

## Organizations

### Multi-Org Accounts
Parent-child organization structure for:
- Large enterprises with separate business units
- MSPs managing multiple customers
- Compliance/data-residency requirements

### Cross-Organization Visibility
- Share dashboards across orgs
- Aggregate billing at parent level
- Maintain data isolation between child orgs

## Single Sign-On

### Supported IdPs
- SAML 2.0 (Okta, OneLogin, Azure AD, PingFederate, Google Workspace)
- Google Authentication
- Active Directory Federation Services (ADFS)

### SAML Setup
1. Get Datadog metadata URL: `https://app.datadoghq.com/account/saml/metadata.xml`
2. Configure IdP with Datadog as a service provider
3. Upload IdP metadata to Datadog (Organization Settings > Login Methods > SAML)
4. Map IdP attributes to Datadog roles

### Enforce SSO
After configuration, optionally require all users to authenticate via SSO (disabling password login).

## API and Application Keys

### API Keys
- Authenticate agent data submission
- One per organization minimum; create per-service or per-team keys
- Scope: send data to Datadog (metrics, traces, logs)

### Application Keys
- Authenticate API calls (reading data, managing resources)
- Tied to a specific user; inherit that user's permissions
- Scope: interact with the Datadog API

### Key Management
```bash
# List API keys
curl -s "https://api.datadoghq.com/api/v2/api_keys" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Create API key
curl -s -X POST "https://api.datadoghq.com/api/v2/api_keys" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{"data":{"type":"api_keys","attributes":{"name":"my-service-key"}}}'
```

### Security
- Rotate keys periodically
- Never commit keys to source control
- Use environment variables or secrets managers (Vault, AWS Secrets Manager)
- Delete keys for offboarded users/services immediately

## Usage Tracking

Monitor consumption to control costs:
- **Plan & Usage** page: view billable hosts, custom metrics, log volume, indexed spans
- **Estimated Usage** metrics: `datadog.estimated_usage.*` — monitor and alert on usage
- **Usage Attribution**: break down costs by tag (team, service, environment)

## Best Practices

- Enforce SSO for all users in production organizations
- Create separate API keys per service/team for audit trail and easy rotation
- Use custom roles to restrict access to sensitive data (security logs, billing)
- Set up usage monitors to alert before hitting plan limits
- Review and clean up inactive users monthly
