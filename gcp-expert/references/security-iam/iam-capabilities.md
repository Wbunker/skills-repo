# Cloud IAM — Capabilities

## Purpose

Cloud Identity and Access Management (IAM) provides fine-grained, attribute-based access control for all GCP resources using a policy-as-code model. IAM answers the question: "Who can do what on which resource?" Every API call to GCP is evaluated against IAM policies before being allowed or denied.

---

## Resource Hierarchy

GCP uses a hierarchical resource model. IAM policies are attached at any level and **inherited downward**; a policy at a higher level grants access to all resources below it.

```
Organization (domain root)
  └── Folder (optional grouping layer; nestable)
        └── Project (billing and API boundary)
              └── Resource (Cloud Storage bucket, BigQuery dataset, Compute instance, etc.)
```

**Inheritance rules:**
- A principal granted a role at the Organization level has that role on every resource in every project.
- A principal granted a role at the Project level has it on every resource in that project.
- Resource-level bindings are additive; you cannot use allow-policy inheritance to restrict a more permissive parent grant (use IAM Deny policies for that).
- Effective policy at any node = union of all policies from that node up to Organization, plus applicable Deny policies.

---

## Core Concepts

### Principal
The identity that is making a request. Principal types:

| Principal Type | Format | Notes |
|---|---|---|
| Google Account | `user:alice@example.com` | Human user with a Google identity |
| Service Account | `serviceAccount:sa@project.iam.gserviceaccount.com` | Non-human workload identity |
| Google Group | `group:devs@example.com` | Manages many users as one unit |
| Google Workspace / Cloud Identity domain | `domain:example.com` | All users in a domain |
| Workforce Identity pool | `principal://iam.googleapis.com/locations/global/workforcePools/POOL/subject/SUBJECT` | Federated external user |
| Workload Identity pool | `principal://iam.googleapis.com/projects/PROJECT/locations/global/workloadIdentityPools/POOL/subject/SUBJECT` | Federated workload |
| `allAuthenticatedUsers` | special value | Any authenticated Google account (use with caution) |
| `allUsers` | special value | Anyone on the internet, including unauthenticated (use only for public resources) |

### Permission
The atomic unit of access. Format: `service.resource.verb` (e.g., `storage.objects.get`, `bigquery.tables.create`, `compute.instances.start`). Permissions are not granted directly; they are grouped into roles.

### Role
A named collection of permissions. Three types:

| Role Type | Example | Notes |
|---|---|---|
| **Primitive (Basic)** | `roles/owner`, `roles/editor`, `roles/viewer` | Legacy; overly broad; avoid in production |
| **Predefined** | `roles/storage.objectViewer`, `roles/bigquery.dataEditor` | Google-managed, service-specific; preferred |
| **Custom** | `projects/my-proj/roles/myCustomRole` | User-defined; specify exact permissions needed |

### Policy
A policy document attached to a resource. Contains a list of **bindings** (principal → role), an optional `etag` for optimistic concurrency, and an optional `version` (1, 2, or 3 — version 3 is required for IAM Conditions).

```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": ["user:alice@example.com", "group:readers@example.com"],
      "condition": {
        "title": "Expires Jan 1 2026",
        "expression": "request.time < timestamp('2026-01-01T00:00:00Z')"
      }
    }
  ],
  "version": 3,
  "etag": "BwXXXXX"
}
```

---

## IAM Conditions

Attribute-based access control on top of role bindings. Conditions are Common Expression Language (CEL) expressions evaluated at request time. Available attribute categories:

| Attribute | Examples |
|---|---|
| Request time | `request.time < timestamp('2025-12-31T00:00:00Z')` |
| Resource name | `resource.name.startsWith('projects/my-proj/buckets/logs-')` |
| Resource type | `resource.type == 'storage.googleapis.com/Object'` |
| Resource service | `resource.service == 'storage.googleapis.com'` |
| IP address / CIDR | `request.auth.access_levels` (used with VPC SC access levels) |

**Use cases:** temporary access grants, granting access scoped to a specific path prefix, time-bound emergency access.

**Limitation:** Conditions require policy version 3. Some primitive roles do not support conditions.

---

## IAM Deny Policies

Deny policies are **separate from allow policies** and explicitly block specific principals from using specific permissions, even if another allow policy would otherwise grant access. This is the correct way to implement guardrails that cannot be overridden by project-level admins.

- Attached at Organization, Folder, or Project level.
- Deny rules take precedence over allow rules.
- Supports exemptions: list principals that bypass the deny rule.
- Example: deny `iam.serviceAccounts.create` for all principals except a central platform team, enforcing centralized service account management.

```json
{
  "displayName": "Deny SA creation to all except platform",
  "rules": [
    {
      "denyRule": {
        "deniedPrincipals": ["principalSet://goog/public:all"],
        "exceptionPrincipals": ["group:platform-admins@example.com"],
        "deniedPermissions": ["iam.googleapis.com/serviceAccounts.create"]
      }
    }
  ]
}
```

---

## Service Accounts

Service accounts are identities used by workloads (VMs, Cloud Run services, GKE pods, Cloud Functions, etc.) rather than humans.

### Key properties
- Email format: `name@project-id.iam.gserviceaccount.com`
- Act as both a principal (can be granted roles) and a resource (can have IAM policies on the SA itself)
- Attached to Compute Engine instances, Cloud Run services, Cloud Functions, GKE node pools, etc.
- Maximum 100 service accounts per project (quota can be increased)

### Service Account Keys
- JSON or P12 key files downloaded to authenticate as the SA from outside GCP.
- **Security risk**: key files can be leaked; rotate regularly; audit with Cloud Asset Inventory.
- **Best practice**: avoid SA keys whenever possible; prefer Workload Identity Federation or the metadata server.
- Org policy `constraints/iam.disableServiceAccountKeyCreation` can block key creation organization-wide.

### Service Account Impersonation
A principal with `roles/iam.serviceAccountTokenCreator` on a SA can generate short-lived tokens to impersonate that SA. Useful for local development without key files:
```bash
gcloud auth print-access-token --impersonate-service-account=sa@project.iam.gserviceaccount.com
```

### Default Service Accounts
Compute Engine and App Engine create default SAs with `roles/editor` by default. This is overly permissive. Use the org policy `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` to disable the automatic Editor grant.

---

## Workload Identity Federation

Allows external workloads to impersonate GCP service accounts without creating and managing SA key files. The external identity presents a credential to STS (Security Token Service), which exchanges it for a short-lived GCP access token.

### Supported external identity providers:
- **AWS**: EC2 instance metadata, Lambda role ARN
- **Azure AD**: Managed Identity or service principal OIDC tokens
- **GitHub Actions**: OIDC tokens from GitHub's OIDC provider (`https://token.actions.githubusercontent.com`)
- **GitLab, CircleCI, Terraform Cloud, HashiCorp Vault**: via OIDC
- **Arbitrary OIDC / SAML providers**: any compliant IdP

### How it works:
1. Create a **Workload Identity Pool** (container for external identities).
2. Add a **Provider** to the pool (OIDC or AWS, with attribute mappings and conditions).
3. Grant a GCP **service account** the `roles/iam.workloadIdentityUser` role with the pool subject/attribute as the principal.
4. External workload exchanges its credential for a GCP token via `https://sts.googleapis.com`.

### Attribute mappings and conditions
Map claims from the external token to Google attributes:
```
google.subject = assertion.sub
attribute.repository = assertion.repository
attribute.actor = assertion.actor
```
Condition to restrict to a specific repo:
```
attribute.repository == "my-org/my-repo"
```

---

## Workload Identity for GKE

Kubernetes workloads (pods) on GKE can authenticate as GCP service accounts without SA keys via **Workload Identity**.

### Setup:
1. Enable Workload Identity on the GKE cluster: `--workload-pool=PROJECT_ID.svc.id.goog`
2. Create a Kubernetes ServiceAccount (KSA).
3. Create a GCP ServiceAccount (GSA).
4. Bind: grant the KSA the `roles/iam.workloadIdentityUser` role on the GSA.
   ```bash
   gcloud iam service-accounts add-iam-policy-binding GSA_EMAIL \
     --role=roles/iam.workloadIdentityUser \
     --member="serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]"
   ```
5. Annotate the KSA:
   ```bash
   kubectl annotate serviceaccount KSA_NAME \
     iam.gke.io/gcp-service-account=GSA_EMAIL
   ```
6. Pods using that KSA can now call GCP APIs authenticated as the GSA via the metadata server.

---

## Organization Policies

Org policies are **resource configuration constraints** (not access control) managed via the Organization Policy Service. They enforce what configurations are allowed across your org, regardless of IAM permissions.

### Common built-in constraints:

| Constraint | Effect |
|---|---|
| `constraints/iam.disableServiceAccountKeyCreation` | Block creation of SA key files |
| `constraints/iam.disableServiceAccountKeyUpload` | Block uploading SA keys |
| `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` | Disable auto Editor grant on default SAs |
| `constraints/compute.requireOsLogin` | Require OS Login for SSH to Compute Engine |
| `constraints/compute.restrictCloudNATUsage` | Restrict Cloud NAT usage |
| `constraints/gcp.resourceLocations` | Restrict resource creation to specific regions |
| `constraints/compute.skipDefaultNetworkCreation` | Skip default VPC creation in new projects |
| `constraints/storage.uniformBucketLevelAccess` | Enforce uniform bucket-level access (no ACLs) |
| `constraints/compute.requireShieldedVm` | Require Shielded VMs for Compute Engine |
| `constraints/gcp.restrictCmekCryptoKeyProjects` | Restrict which KMS projects can be used for CMEK |
| `constraints/iam.allowedPolicyMemberDomains` | Restrict IAM bindings to specific domains |

Org policies can be **enforced** (boolean) or set with **allowed/denied value lists** (list constraints). They can be applied at the org, folder, or project level and are inherited. A `restore_default` value resets to Google's default behavior.

---

## IAM Recommender

The IAM Recommender analyzes audit logs for the past 90 days and recommends ways to tighten IAM policies by identifying excessive permissions.

- **Insight types**: `google.iam.policy.Insight` (permission usage), `google.iam.serviceAccountInsight` (SA activity)
- Recommends replacing broad roles with more specific roles or removing bindings entirely.
- Each recommendation has a confidence level (HIGH, MEDIUM, LOW).
- Accept recommendations directly via gcloud or the console; changes are made atomically.

---

## Policy Analyzer

Allows querying IAM policies across your organization to answer questions like:
- "Who has access to this resource?"
- "What resources can this principal access?"
- "Does this principal have this permission on this resource?"

Analyzes policies including conditions and inherited policies across the resource hierarchy. Useful for compliance reviews and access audits. Works with Cloud Asset API.

---

## Best Practices

1. **Principle of least privilege**: grant only the permissions required for the task, on the smallest scope possible.
2. **Use groups, not individuals**: manage access via Google Groups; add/remove group membership rather than changing IAM bindings.
3. **Prefer predefined roles over primitive roles**: `roles/storage.objectCreator` instead of `roles/editor`.
4. **Avoid service account keys**: use Workload Identity Federation for external workloads, attached SAs with the metadata server for GCP workloads.
5. **Enable org policies proactively**: disable SA key creation, restrict regions, disable default network creation.
6. **Use IAM Deny policies** for non-negotiable guardrails that project admins cannot override.
7. **Audit regularly**: use Policy Analyzer, Cloud Audit Logs (Data Access logs for `google.iam.admin.v1`), and IAM Recommender.
8. **Protect highly privileged SAs**: add `roles/iam.serviceAccountUser` and `roles/iam.serviceAccountTokenCreator` only when necessary; monitor for unusual token generation.
9. **Use IAM Conditions** for time-limited access grants (break-glass access, contractors).
10. **Monitor with Security Command Center**: enable Security Health Analytics to detect overly permissive bindings and unused SA keys.
