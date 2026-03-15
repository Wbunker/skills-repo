# AWS Verified Permissions & KMS — Capabilities Reference
For CLI commands, see [verified-permissions-kms-cli.md](verified-permissions-kms-cli.md).

## Amazon Verified Permissions

**Purpose**: Fine-grained authorization service for your own applications using the Cedar policy language.

### Key Concepts

| Concept | Description |
|---|---|
| **Policy store** | Container for policies and the schema |
| **Schema** | Defines entity types (User, Photo, Album), their attributes, and valid action types |
| **Policy** | Cedar statements granting or forbidding principals to perform actions on resources |
| **Policy template** | Parameterized policy for creating many similar policies (e.g., share with specific user) |
| **Entity** | A principal (User) or resource (Photo) with typed attributes |
| **IsAuthorized API** | Real-time authorization decision: ALLOW or DENY |

### Cedar Policy Example

```cedar
// Allow premium users to view any photo
permit (
  principal in Group::"premium-users",
  action == Action::"ViewPhoto",
  resource
);

// Deny viewing photos in albums marked private
forbid (
  principal,
  action == Action::"ViewPhoto",
  resource
) when {
  resource.album.isPrivate == true &&
  !(principal in resource.album.owners)
};
```

### When to Use Verified Permissions vs IAM

| Use IAM | Use Verified Permissions |
|---|---|
| Controlling access to AWS services | Controlling access within your own application |
| AWS console/API access | App-level resource authorization (e.g., "can user X view document Y?") |
| EC2, S3, Lambda permissions | SaaS authorization logic, multi-tenant apps |

---

## AWS KMS

**Purpose**: Managed service for creating, controlling, and auditing cryptographic keys.

### Key Types

| Type | Description |
|---|---|
| **AWS managed key** | Created automatically by AWS services; you cannot manage directly; free |
| **Customer managed key (CMK)** | You create and control; $1/month per key; supports rotation, policies, grants |
| **AWS owned key** | Owned and managed entirely by AWS; no cost, no visibility |
| **Asymmetric key** | RSA or ECC key pairs for encryption or signing (cannot be used by AWS services for envelope encryption) |
| **HMAC key** | For generating and verifying Hash-based Message Authentication Codes |
| **Multi-region key** | Same key material replicated to multiple regions; one primary, replicas in others |

### Key Features

| Feature | Description |
|---|---|
| **Envelope encryption** | KMS encrypts a data key; data key encrypts the data; standard pattern for large data |
| **Key policy** | Resource-based policy on the key; must explicitly allow account root or no one can use it |
| **Grants** | Delegate key usage to AWS services or principals without modifying key policy |
| **Key rotation** | Automatic annual rotation for symmetric CMKs (key ID stays the same; old backing keys retained) |
| **Key aliases** | Friendly names for keys (`alias/my-key`); use instead of ARN in app config |
| **CloudTrail integration** | Every KMS API call logged; use for compliance and forensics |
| **Cross-account usage** | Key policy allows other account; grantee adds KMS permissions to their IAM policy |
| **Custom key store** | Back CMKs with AWS CloudHSM cluster you own; for regulatory requirements |

### Common Encryption Pattern (Envelope)

```
Application → GenerateDataKey(CMK) → KMS returns [plaintext_key, encrypted_key]
Application → Encrypt data with plaintext_key (in memory)
Application → Store encrypted_data + encrypted_key together
Application → Discard plaintext_key

Decrypt: Send encrypted_key to KMS Decrypt → get plaintext_key → decrypt data
```
