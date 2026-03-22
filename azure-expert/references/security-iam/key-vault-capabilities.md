# Azure Key Vault — Capabilities

## Overview

Azure Key Vault is a cloud service for securely storing and controlling access to secrets (passwords, connection strings), cryptographic keys (RSA, EC), and certificates. It eliminates the need to store sensitive values in application code or configuration files. All access is logged, and access control can be enforced via RBAC or vault access policies.

---

## Key Vault Resources

### Keys

Cryptographic keys used for encryption, signing, and key wrapping operations:

| Algorithm | Key Sizes | HSM-Backed |
|---|---|---|
| RSA | 2048, 3072, 4096 bits | Optional (Premium SKU) |
| EC (Elliptic Curve) | P-256, P-384, P-521, P-256K | Optional (Premium SKU) |
| AES (Oct) | 128, 192, 256 bits | HSM only |

**Operations**:
- **Encrypt/Decrypt**: protect data with asymmetric key
- **Sign/Verify**: generate and verify digital signatures
- **Wrap/Unwrap**: key encryption (envelope encryption pattern)
- **Import**: bring your own key (BYOK) for HSM-backed keys
- **Export**: allowed only if `exportable` flag set and a release policy exists (Secure Key Release)

**Key Attributes**:
- `enabled`: whether the key is active
- `notBefore` / `expires`: time-bounded validity
- `keyOps`: permitted operations (restrict to only needed ops)
- Versioned: each rotation creates a new version; old versions remain accessible by version ID

### Secrets

Arbitrary values (strings up to 25KB): connection strings, passwords, API keys, storage account keys, TLS private keys.

- Maximum value: 25KB
- Versioned: each `set` creates a new version; old versions accessible by version ID
- `contentType`: optional metadata (e.g., `text/plain`, `application/json`, `application/x-pkcs12`)
- `notBefore` / `expires`: time-bounded availability
- Tags: metadata for organization and filtering

### Certificates

Managed TLS/SSL certificates with automated lifecycle:

- **Certificate types**: X.509 certificates with private key stored in vault
- **Issuers**:
  - Self-signed (for development/testing)
  - DigiCert (integrated CA — auto-renew)
  - GlobalSign (integrated CA — auto-renew)
  - Unknown (import existing certificate; no auto-renewal)
- **Auto-renewal**: configure percentage lifetime or days before expiry to trigger renewal
- **Policy**: defines subject, SANs, key type/size, validity period, issuer
- **Export**: certificate (with private key) can be downloaded as PFX/PEM
- Certificates are also accessible as secrets (PFX/PEM) and their public key as a key object

---

## SKUs

| SKU | Key Protection | Target |
|---|---|---|
| **Standard** | Software-protected (FIPS 140-2 Level 1) | General purpose, dev/test, non-regulated |
| **Premium** | HSM-protected keys available (FIPS 140-2 Level 2) | Production, regulated industries |

**Recommendation**: use Premium SKU for any production key that protects sensitive data or where HSM-backed key protection is a compliance requirement.

---

## Azure Managed HSM

Single-tenant, fully managed Hardware Security Module service — not the same as Key Vault Premium.

| Feature | Key Vault Premium | Managed HSM |
|---|---|---|
| HSM level | FIPS 140-2 Level 2 | FIPS 140-2 Level 3 |
| Tenancy | Multi-tenant HSM | Single-tenant HSM |
| HSM admin control | Microsoft managed | Customer controls HSM admin (security domain) |
| Key export control | Customer | Customer (Security Domain protects) |
| Throughput | Standard | Very high (designed for HSM-at-scale) |
| Cost | Per operation | Per provisioned HSM (higher) |

**Use when**: regulatory requirement for FIPS 140-2 Level 3 single-tenant HSM, or full cryptographic control over HSM administration is required.

---

## Access Models

### RBAC (Recommended)

Azure RBAC controls access to Key Vault data plane operations using built-in roles:

| Role | Permissions |
|---|---|
| **Key Vault Administrator** | Full access to keys, secrets, certificates; manage access policies |
| **Key Vault Certificates Officer** | Manage certificates (create, import, delete, rotate) |
| **Key Vault Crypto Officer** | Manage keys (create, import, delete, rotate); cannot use for crypto operations |
| **Key Vault Crypto User** | Use keys for crypto operations (encrypt, decrypt, sign, verify, wrap, unwrap) |
| **Key Vault Crypto Service Encryption User** | Use keys for wrapping/unwrapping only (used by Azure services for CMK) |
| **Key Vault Secrets Officer** | Manage secrets (set, delete, list, backup, restore) |
| **Key Vault Secrets User** | Read secret values; ideal for app service principals and managed identities |
| **Key Vault Reader** | View metadata only; cannot read values |

**Benefits of RBAC over Access Policies**:
- Fine-grained: different roles for different object types (keys vs secrets vs certs)
- Audit trail in Azure Activity Log
- Assignable at vault, resource group, or subscription scope
- Part of standard RBAC infrastructure (same tooling)

### Vault Access Policies (Legacy)

The older model; still supported but not recommended for new deployments:
- Permission types: Key Permissions (`get`, `list`, `create`, `delete`, `sign`, `verify`, `encrypt`, `decrypt`, `wrapKey`, `unwrapKey`, `import`, `backup`, `restore`, `purge`)
- Secret Permissions (`get`, `list`, `set`, `delete`, `backup`, `restore`, `recover`, `purge`)
- Certificate Permissions (`get`, `list`, `create`, `import`, `delete`, `update`, `managecontacts`, `getissuers`, `setissuers`, `deleteissuers`, `manageissuers`, `recover`, `backup`, `restore`, `purge`)
- Max 1,024 access policies per vault
- Enable RBAC: `az keyvault update --enable-rbac-authorization true` (migrates from access policies to RBAC)

---

## Security Features

### Soft Delete

- Enabled by default (cannot be disabled for new vaults)
- Deleted vault objects retained for 7–90 days (default 90)
- Recoverable via `recover` operation during retention period
- `az keyvault secret recover --name mySecret --vault-name myVault`

### Purge Protection

- Prevents **permanent deletion** during soft delete retention period
- Once enabled, cannot be disabled for the vault's lifetime
- Required for Customer-Managed Key scenarios (prevents accidental key loss → data loss)
- Enable: `az keyvault update --enable-purge-protection true`

### Key Vault Firewall

Control which networks can access the vault's data plane:

- **Allow trusted Microsoft services**: bypass firewall for select Azure services (Azure Backup, Azure Monitor, Disk Encryption, ARM for template deployments, Event Grid); always enable this
- **Selected networks**: specify VNet subnets (via Service Endpoints) and/or IP address ranges
- **Private Endpoint**: deploy a Private Endpoint in your VNet; disable public access entirely for zero-trust
- **Default action**: `Deny` (all traffic denied unless matched by above rules)

**Recommendation for production**: Private Endpoint + disable public access (`--default-action Deny` + `--public-network-access Disabled`).

---

## Key Rotation

Automated key rotation reduces risk from key compromise:

- **Rotation policy**: set on the key; defines rotation schedule (days after creation or lifetime percentage)
- **Auto-rotation**: creates a new key version on schedule; old version remains for decryption
- **Notification events**: Event Grid events on key near-expiry and key rotated; trigger automation
- **Azure Monitor alerts**: alert on `DaysBeforeKeyExpiry` metric

### Rotation in Customer-Managed Key Scenarios

When Azure services use Key Vault CMK:
1. Key rotated in Key Vault → new version created
2. Service automatically detects new key version and re-wraps data encryption key
3. No data re-encryption required (envelope encryption pattern)

---

## Secrets Integration Patterns

### Key Vault References (App Service / Functions)

Reference Key Vault secrets directly in App Service configuration without reading the secret in code:

```
@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/mySecret/)
@Microsoft.KeyVault(VaultName=myvault;SecretName=mySecret)
```

- App Service's system-assigned or user-assigned managed identity must have `Key Vault Secrets User` role
- App Service fetches secret value at runtime; rotates automatically when secret updates

### AKS — Key Vault CSI Driver (Secrets Store CSI Driver)

Mount Key Vault secrets as Kubernetes volumes or environment variables:

1. Enable Key Vault CSI Driver add-on: `az aks enable-addons --addons azure-keyvault-secrets-provider`
2. Create `SecretProviderClass` manifest referencing vault, secrets/keys/certs
3. Pod mounts the secret as a file volume or Kubernetes Secret

### ARM/Bicep Parameter Files

Reference Key Vault secrets in ARM/Bicep deployments:

```json
{
  "adminPassword": {
    "reference": {
      "keyVault": { "id": "<key-vault-resource-id>" },
      "secretName": "vmAdminPassword"
    }
  }
}
```

### Azure Pipelines / GitHub Actions

- Azure DevOps: Key Vault task (`AzureKeyVault@2`) fetches secrets as pipeline variables
- GitHub Actions: `Azure/get-keyvault-secrets` action or use Managed Identity + OIDC token

---

## Customer-Managed Keys (CMK)

Bring your own encryption key to Azure services. The service wraps its data encryption key (DEK) using your key encryption key (KEK) stored in Key Vault. You control key lifecycle:

| Service | CMK Support |
|---|---|
| Azure Storage | Blobs, Files, Queues, Tables (storage account level or per-container) |
| Azure SQL Database / Managed Instance | Transparent Data Encryption (TDE) with CMK |
| Azure Cosmos DB | Account-level CMK |
| Azure Disk Encryption | VM OS and data disks (server-side or ADE agent) |
| Azure Kubernetes Service | etcd CMK, OS disk CMK |
| Azure Backup | Backup vault encryption |
| Azure Monitor (Log Analytics) | Workspace CMK (requires dedicated cluster) |

**CMK Requirements**:
- Key Vault Premium (or Managed HSM) with purge protection enabled
- Key never expires (or manage expiry with automation)
- Service principal/managed identity has `Key Vault Crypto Service Encryption User` role
- Firewall rules allow the service to access the vault (or Private Endpoint)
