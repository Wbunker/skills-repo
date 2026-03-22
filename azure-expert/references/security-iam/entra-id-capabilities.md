# Microsoft Entra ID & RBAC — Capabilities

## Overview

Microsoft Entra ID (formerly Azure Active Directory) is Microsoft's cloud-based identity and access management service. It is the identity provider for Azure, Microsoft 365, and thousands of third-party SaaS applications. Every Azure subscription trusts exactly one Entra ID tenant; one tenant can trust many subscriptions.

---

## Entra ID Fundamentals

### Tenants and Directories

- A **tenant** is a dedicated instance of Entra ID owned by an organization
- Each tenant has a unique `<tenant>.onmicrosoft.com` domain (plus custom verified domains)
- **Tenant ID (GUID)**: primary identifier used in OAuth/OIDC flows and CLI authentication
- **Directory**: synonymous with tenant; the container for all identity objects
- **Subscription association**: subscriptions trust a single tenant; can be moved between tenants (ownership transfer)
- **Multi-tenant**: a single application can be registered to accept identities from multiple tenants

### Identity Objects

| Object Type | Description |
|---|---|
| **User** | Human identity; member (internal) or guest (B2B external) |
| **Group** | Collection of users, service principals, or other groups; security groups or Microsoft 365 groups |
| **Service Principal** | Non-human identity for applications; represents an app registration within a tenant |
| **Managed Identity** | Auto-managed service principal for Azure resources (no credential management) |
| **Application (App Registration)** | Registration of an app; creates application object + service principal in home tenant |
| **Device** | Azure AD joined or registered device |

### License Tiers

| License | Key Features |
|---|---|
| **Free** | MFA (basic), SSO (limited), device management, B2B collaboration (50,000 objects) |
| **Microsoft Entra ID P1** | Conditional Access, group-based licensing, self-service password reset, hybrid identity, MFA (full) |
| **Microsoft Entra ID P2** | P1 + Privileged Identity Management (PIM), Identity Protection, Access Reviews, Entitlement Management |
| **Entra ID Governance** | Advanced lifecycle management, access reviews, entitlement management |

---

## Azure RBAC

Role-Based Access Control (RBAC) is the authorization system for Azure resources. It is separate from Entra ID roles (which control directory objects) and Azure AD/Entra administrative roles.

### Scope Hierarchy

RBAC assignments inherit downward through the scope hierarchy:

```
Management Group (root)
  └── Management Group (level 2–6)
        └── Subscription
              └── Resource Group
                    └── Resource (e.g., Storage Account, VM, Key Vault)
```

An assignment at Management Group scope applies to all subscriptions, resource groups, and resources below it.

### Built-in Roles (Key Roles)

| Role | Scope | Description |
|---|---|---|
| **Owner** | Any | Full access including ability to assign roles; use sparingly |
| **Contributor** | Any | Full access to create/manage resources; cannot assign roles or manage permissions |
| **Reader** | Any | View only; no write access |
| **User Access Administrator** | Any | Manage role assignments only; no resource access |
| **Role Based Access Control Administrator** | Any | Manage RBAC assignments with conditions; less powerful than User Access Administrator |

Service-specific built-in roles (100+ total):
- `Storage Blob Data Contributor`, `Storage Blob Data Reader`
- `Key Vault Secrets Officer`, `Key Vault Secrets User`, `Key Vault Administrator`
- `Virtual Machine Contributor`, `Virtual Machine Administrator Login`
- `AcrPull`, `AcrPush` (Azure Container Registry)
- `Monitoring Contributor`, `Monitoring Reader`
- `Network Contributor`, `SQL DB Contributor`

### Custom Roles

Custom roles are defined in JSON (or Bicep) and can be assigned to any scope in the tenant.

```json
{
  "Name": "Custom VM Operator",
  "Description": "Can start and stop VMs but not create or delete",
  "Actions": [
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/restart/action",
    "Microsoft.Compute/virtualMachines/deallocate/action",
    "Microsoft.Compute/virtualMachines/read"
  ],
  "NotActions": [],
  "DataActions": [],
  "NotDataActions": [],
  "AssignableScopes": ["/subscriptions/<sub-id>"]
}
```

- **Actions**: control plane operations (create/read/update/delete resources)
- **DataActions**: data plane operations (read/write blob data, send queue messages)
- **NotActions**: exclude specific actions from a broader wildcard
- **AssignableScopes**: where the custom role can be assigned (subscription, MG)
- Custom roles count against the 5,000 custom role limit per tenant

### RBAC with Conditions (ABAC)

Attribute-Based Access Control extends RBAC with conditions on role assignments:
- Restrict access based on resource tags, blob index tags, or container names
- Example: `Storage Blob Data Reader` only for blobs tagged `Project=Finance`
- Conditions written in JSON condition expression language
- Currently supported for Storage and some other services

### RBAC Best Practices

- Assign roles to **groups**, not individual users — easier to manage, audit, and scale
- Use **least privilege**: avoid Owner; prefer specific service roles
- Avoid assigning at subscription/MG scope unless truly required
- Use **PIM** for time-bound, just-in-time elevation instead of permanent privileged assignments
- Review assignments regularly with **Access Reviews** (requires P2)
- Use **Contributor** for app service principals, not Owner
- Separate duties: restrict who has `User Access Administrator` role

---

## Managed Identity

Managed Identity eliminates the need to store credentials (passwords, certificates) in code or configuration. Azure automatically rotates the underlying credential.

### Types

| Type | Description | Use When |
|---|---|---|
| **System-Assigned** | Created as part of the Azure resource; deleted when resource is deleted; 1:1 relationship | Simple scenarios, single-resource identity |
| **User-Assigned** | Standalone resource; independently created and managed; can be assigned to multiple resources | Shared identity across resources, pre-authorization before deployment, VMSS scenarios |

### Supported Services

Managed Identity can be enabled on: VMs, VMSS, App Service, Azure Functions, AKS (pods via Workload Identity), Logic Apps, Container Instances, Azure Automation, Service Fabric, API Management, Data Factory, Batch, and more.

### How It Works

1. Enable Managed Identity on a resource → creates a service principal in Entra ID
2. Grant RBAC role to the managed identity's service principal (e.g., `Storage Blob Data Reader`)
3. Code running on the resource requests a token from the Azure Instance Metadata Service (IMDS): `http://169.254.169.254/metadata/identity/oauth2/token`
4. Azure returns a short-lived access token (no password/cert ever stored in code)
5. Use token to authenticate to Azure services (Storage, Key Vault, SQL, etc.)

### Workload Identity Federation

Allows external identity providers (GitHub Actions, Kubernetes service accounts, GitLab, Terraform Cloud) to obtain Entra ID tokens without secrets:

1. Create App Registration in Entra ID with federated credential
2. Configure external IdP to trust Entra ID issuer
3. External workload (e.g., GitHub Action) exchanges its OIDC token for Entra ID access token
4. Use token to authenticate to Azure resources

**Use cases**: GitHub Actions deploying to Azure (no stored service principal secrets), AKS workloads accessing Azure services (via Azure Workload Identity), Terraform Cloud accessing Azure.

---

## Privileged Identity Management (PIM)

PIM provides just-in-time (JIT) privileged access, time-bound role assignments, and approval workflows for both Azure RBAC roles and Entra ID roles. Requires Entra ID P2 license.

### PIM Concepts

| Concept | Description |
|---|---|
| **Eligible assignment** | User can activate the role when needed (not permanently active) |
| **Active assignment** | Role is permanently active (without activation required) |
| **Activation** | User requests activation of eligible role; can require MFA, justification, approval |
| **Role settings** | Maximum activation duration, MFA requirement, approval requirement, notification |
| **Access review** | Periodic review of role assignments; reviewers confirm or remove access |

### PIM Workflow

```
1. Admin makes user Eligible for a role (e.g., Subscription Contributor)
2. When needed, user activates the role via PIM portal or PowerShell
3. Activation may require: MFA, business justification, approval from manager
4. Role becomes Active for 1–8 hours (configurable max duration)
5. After duration expires, role is automatically deactivated
6. All activations logged in Entra ID audit logs
```

### PIM for Groups

- Make a user an eligible member of a security group
- The group has permanent role assignments (e.g., `Key Vault Administrator`)
- JIT group membership grants temporary role access
- Simplifies PIM management for complex role combinations

---

## Conditional Access

Policy-based access control applied at authentication time. Requires Entra ID P1 or P2.

### Policy Structure

```
IF (Assignments match) THEN (Access controls apply)

Assignments:
  - Users and groups (include/exclude)
  - Cloud apps or actions
  - Conditions: sign-in risk, user risk, device platform, location, client app, device state

Controls:
  Grant: require MFA, compliant device, Entra joined device, approved app, ToU
  Session: sign-in frequency, persistent browser session, app-enforced restrictions
```

### Common Policies

| Policy | Description |
|---|---|
| Require MFA for all users | All sign-ins require MFA (exclude break-glass accounts) |
| Require compliant device for corporate apps | Intune device compliance required for M365 access |
| Block legacy authentication | Block basic auth protocols (IMAP, SMTP, POP3) that don't support MFA |
| Require MFA for privileged roles | Extra protection for admin role assignments |
| Block access from risky locations | Named location conditions for geo-blocking |
| Sign-in risk-based MFA | Require MFA when Entra ID detects medium/high sign-in risk |

### Named Locations

- IP ranges: define trusted corporate IP ranges; exclude from MFA policies
- Countries/regions: define geographic locations for geo-blocking policies
- Trusted IPs (MFA): used in per-user MFA configuration (not full Conditional Access)

### Break-Glass Accounts

- Two cloud-only accounts without MFA (or with hardware FIDO2 key)
- Excluded from all Conditional Access policies
- Used only when all other admin access is unavailable
- Stored credentials in physical safe; monitored for any sign-in activity

---

## Microsoft Entra External ID

Unified platform for external identity scenarios:

### B2B Collaboration

- Invite external users (partner employees) as guest users in your tenant
- Guest users sign in with their home identity (Microsoft account, Google, other IdP)
- Appear as `user_type: Guest` in directory
- Subject to Conditional Access policies in your tenant
- **Cross-tenant synchronization**: sync B2B users between your own tenants
- **B2B direct connect**: shared channel with specific organizations without guest account

### Microsoft Entra External ID (formerly Azure AD B2C)

- Customer identity and access management (CIAM) for consumer-facing apps
- Separate tenant type for customer identities
- Custom user journeys (sign-up, sign-in, password reset, profile edit)
- Social identity providers: Google, Facebook, Apple, generic OIDC
- Fully branded login experience
- Custom policies (Identity Experience Framework) for complex scenarios

---

## Entra Application Proxy

- Enables secure remote access to on-premises web applications without VPN
- Azure AD Application Proxy connector runs on-premises (outbound HTTPS only — no inbound firewall rules)
- Users access on-premises apps via `<app>.msappproxy.net` URLs
- Supports single sign-on (Kerberos constrained delegation, header-based, password-based, SAML)
- Conditional Access and MFA applied before user reaches on-premises app
