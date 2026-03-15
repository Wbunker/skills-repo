# Secret Manager — Capabilities

## Purpose

Secret Manager is a fully managed, secure service for storing, managing, and accessing sensitive configuration data such as API keys, passwords, database credentials, TLS certificates, and other application secrets. It provides versioned secret storage with IAM access control, audit logging, and automatic rotation notifications.

---

## Core Concepts

### Secret
A named container for sensitive data within a project. A secret does not hold data directly; it holds one or more **versions** of the secret's value. Secrets have metadata including replication policy, labels, annotations, TTL, and rotation schedule.

Secret resource name format: `projects/PROJECT_ID/secrets/SECRET_NAME`

### Secret Version
An immutable payload attached to a secret. Secret versions are numbered sequentially starting at 1. Versions have a **state**:

| State | Meaning |
|---|---|
| `ENABLED` | Can be accessed normally |
| `DISABLED` | Cannot be accessed; use to temporarily suspend a version without destroying it |
| `DESTROYED` | Payload irrevocably deleted; metadata retained; version number is permanently retired |

The special alias `latest` always resolves to the highest-numbered enabled version.

### Replication Policy
Determines where the secret payload is stored. **Must be set at secret creation time and cannot be changed.**

| Policy | Behavior | Use when |
|---|---|---|
| **Automatic** | Google stores replicas in multiple locations globally for high availability | Default for most use cases; Google manages placement |
| **User-Managed** | You specify one or more regions where the secret is replicated | Data residency compliance; specific regional requirements |

For user-managed replication, each specified region can optionally have its own CMEK key.

### Labels and Annotations
- **Labels**: key-value pairs for resource organization and filtering; indexed.
- **Annotations**: key-value pairs for storing structured metadata about a secret (e.g., owning team, rotation contact); not indexed; up to 16 KiB total.

### Checksum Verification
Client applications can pass a CRC32C checksum with the secret payload when creating a version. Secret Manager verifies the checksum on access and returns the verified checksum in the response, detecting any data corruption.

---

## Rotation

Secret Manager supports **notification-based rotation** using Cloud Pub/Sub. Secret Manager does not rotate credentials itself; it sends a notification to a Pub/Sub topic and a Cloud Function or Cloud Run service performs the actual rotation (calling the credential provider, updating the value, and adding a new version).

### Rotation configuration
- `rotation.rotation_period`: how often to send rotation notifications (minimum 1 day).
- `rotation.next_rotation_time`: when the first (or next) notification is sent.
- `topics`: Pub/Sub topic to publish rotation notification events to.

### Rotation workflow
1. Secret Manager sends a Pub/Sub message to the configured topic.
2. A Cloud Function triggered by the topic:
   a. Generates new credentials (calls the database, API, or credential provider).
   b. Adds a new secret version with the new value.
   c. Tests the new version.
   d. Disables or destroys the old version.
3. Applications using `latest` alias automatically pick up the new credentials on next access.

### TTL (Auto-Expiry)
A secret can have a TTL. When the TTL elapses, the secret and all its versions are automatically destroyed. Useful for temporary secrets (e.g., one-time setup credentials).

---

## Regional Secrets

By default, secrets with automatic replication are global (data may be stored anywhere). **Regional secrets** are a separate resource type (`secrets` in a specific region) that constrains secret data to a single GCP region for data residency compliance.

- API endpoint: `secretmanager.REGION.rep.googleapis.com`
- Resource name: `projects/PROJECT_ID/locations/REGION/secrets/SECRET_NAME`
- Support CMEK with regional KMS keys
- Not replicated across regions (single point of failure for that region)

---

## CMEK for Secret Manager

Both automatic and user-managed replication support CMEK:
- Specify a Cloud KMS key when creating a secret (or per-region for user-managed replication).
- The Secret Manager service agent (`service-PROJECT_NUMBER@gcp-sa-secretmanager.iam.gserviceaccount.com`) must have `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the KMS key.
- If the KMS key is disabled or destroyed, the secret becomes inaccessible.

---

## Access Control

Secret Manager uses Cloud IAM for access control. Grant access at the **secret level** (preferred for least-privilege) or at the **project level**.

### IAM Roles

| Role | Permissions | Use |
|---|---|---|
| `roles/secretmanager.admin` | Full control (CRUD secrets, manage versions, IAM) | Secret administrators |
| `roles/secretmanager.secretAccessor` | `secretmanager.versions.access` | Applications reading secrets |
| `roles/secretmanager.secretVersionAdder` | `secretmanager.versions.add` | Rotation automation adding new versions |
| `roles/secretmanager.secretVersionManager` | Add, enable, disable, destroy versions | Rotation and lifecycle management |
| `roles/secretmanager.viewer` | List secrets and versions, view metadata (not payloads) | Auditors, monitoring tools |

**Best practice**: grant `roles/secretmanager.secretAccessor` on individual secrets to specific service accounts rather than at the project level.

### Secret-level IAM example
```bash
gcloud secrets add-iam-policy-binding my-db-password \
  --member="serviceAccount:app-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Audit Logging

Secret Manager generates Cloud Audit Logs for:
- **Admin Activity**: creating, updating, deleting secrets and versions; changing IAM policies.
- **Data Access**: accessing secret version payloads (must be enabled; disabled by default).

Enabling data access audit logs for Secret Manager is critical for compliance and detecting unauthorized access. Each access log entry includes: timestamp, principal, secret resource, and version accessed.

---

## Integration Patterns

### Cloud Run
Two methods to make secrets available in Cloud Run:

1. **Environment variables**: Secret Manager injects the secret value as an environment variable at container start. Value is read once at startup.
   - Configure in Cloud Run service definition: secret ref → env var name.
   - Reference a specific version or `latest`.

2. **Mounted volume**: Secret version is mounted as a file inside the container at a specified path.
   - Applications read the file; can detect rotation if they re-read the file.
   - More secure than env vars (not visible in `docker inspect` output).

### GKE — External Secrets Operator
The External Secrets Operator (ESO) synchronizes Secret Manager secrets into Kubernetes Secrets automatically. ESO uses Workload Identity to authenticate. Preferred for cloud-native GKE workflows.

### GKE — Secret Manager CSI Driver
The `secrets-store-csi-driver-provider-gcp` mounts Secret Manager secrets as files into pods without creating Kubernetes Secrets (which are stored in etcd and visible to cluster admins).

### Cloud Functions
Access secrets via:
- Environment variables (same as Cloud Run, configured at deploy time).
- The Secret Manager client library within the function code for dynamic access.

### Compute Engine
Service accounts attached to Compute Engine instances access secrets via the Secret Manager API (or gcloud CLI) with the instance SA having `roles/secretmanager.secretAccessor`.

---

## Secret Manager vs HashiCorp Vault

| Feature | Secret Manager | HashiCorp Vault |
|---|---|---|
| Deployment | Fully managed SaaS | Self-hosted or HCP Vault |
| Credentials | Static secrets + rotation notifications | Dynamic secrets (e.g., short-lived DB credentials generated on demand) |
| Auth methods | GCP IAM | Many (LDAP, JWT, AppRole, cloud IAM, etc.) |
| Multi-cloud | GCP-native only | Multi-cloud and on-prem |
| PKI / CA | Not built-in (use CAS) | Built-in PKI secret engine |
| Operational overhead | None | Significant (HA, storage backend, unsealing, upgrades) |
| Cost | Pay per secret version access | Infrastructure + HCP licensing |
| Best for | GCP-native workloads | Multi-cloud, complex dynamic secrets, existing Vault users |

---

## Best Practices

1. **Grant access at the secret level** using IAM bindings on individual secrets, not broad project-level roles.
2. **Use the `latest` version alias carefully**: pinning to a specific version ensures stability but requires code changes to rotate; using `latest` enables seamless rotation but means a bad rotation silently breaks apps.
3. **Enable Data Access audit logs** for Secret Manager to track every secret read.
4. **Configure rotation notifications** for all secrets with long-lived credentials; do not manually manage expiry.
5. **Use CMEK** for secrets subject to compliance requirements (PCI DSS, HIPAA).
6. **Use regional secrets** when you have data residency requirements that prohibit global replication.
7. **Destroy old versions** after rotation is verified; do not leave old versions enabled indefinitely.
8. **Do not store secrets in environment variables of build systems** — inject them at runtime via Secret Manager.
9. **Use annotations** to store rotation contact, owning team, and linked resource information for operational hygiene.
10. **Test rotation automation** regularly; a rotation procedure that fails silently can result in expired credentials in production.
