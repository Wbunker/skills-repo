# Cloud KMS — Capabilities

## Purpose

Cloud Key Management Service (Cloud KMS) is a cloud-hosted, fully managed key management service for creating, using, rotating, and destroying cryptographic keys. It provides hardware security module (HSM) backing via Cloud HSM for FIPS 140-2 Level 3 validated key storage, and supports integration with external key managers via Cloud External Key Manager (EKM).

---

## Core Concepts

### Key Ring
A logical grouping of CryptoKeys within a **specific region** (or `global`). Key rings cannot be deleted. They serve as the organizational unit for keys and are identified by their location (region) and name. Example: `projects/my-proj/locations/us-central1/keyRings/my-keyring`.

**Important**: The location of a key ring is permanent and determines where key material is stored. Choose the same region as the data you want to protect to minimize latency and comply with data residency requirements.

### CryptoKey
A named key within a key ring. A CryptoKey has a **purpose** that determines its allowed operations and a current **primary version**. CryptoKeys cannot be deleted (only their versions can be destroyed). They are identified as: `projects/my-proj/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key`.

### CryptoKey Version
The actual key material. Each version has a **state**:

| State | Meaning |
|---|---|
| `PENDING_GENERATION` | Key material is being generated (HSM keys only) |
| `ENABLED` | Can be used for cryptographic operations; the `PRIMARY` version is the one used for new encrypt operations |
| `DISABLED` | Cannot be used; material retained for re-enable; cannot decrypt/verify/sign |
| `PENDING_DESTRUCTION` | Scheduled for destruction after a configurable delay (1–120 days) |
| `DESTROYED` | Key material is irrevocably gone; metadata retained |

### Key Purpose

| Purpose | Allowed Operations | Common Use |
|---|---|---|
| `ENCRYPT_DECRYPT` | Encrypt, Decrypt | CMEK, envelope encryption |
| `ASYMMETRIC_SIGN` | AsymmetricSign, GetPublicKey | Code signing, document signing, JWTs |
| `ASYMMETRIC_DECRYPT` | AsymmetricDecrypt, GetPublicKey | Hybrid encryption, decrypting data encrypted with public key |
| `MAC` | MacSign, MacVerify | HMAC message authentication |

---

## Key Algorithms

### Symmetric (ENCRYPT_DECRYPT)
| Algorithm | Key Size | Notes |
|---|---|---|
| `GOOGLE_SYMMETRIC_ENCRYPTION` | 256-bit AES-GCM | Default; use for CMEK and general encryption |

### Asymmetric Signing
| Algorithm | Notes |
|---|---|
| `RSA_SIGN_PKCS1_2048_SHA256` | RSA 2048-bit, PKCS#1 v1.5 |
| `RSA_SIGN_PKCS1_3072_SHA256` | RSA 3072-bit |
| `RSA_SIGN_PKCS1_4096_SHA256` | RSA 4096-bit |
| `RSA_SIGN_PSS_2048_SHA256` | RSA 2048-bit, PSS padding |
| `RSA_SIGN_PSS_4096_SHA512` | RSA 4096-bit, PSS padding |
| `EC_SIGN_P256_SHA256` | NIST P-256 (recommended for new signing workloads) |
| `EC_SIGN_P384_SHA384` | NIST P-384 |
| `EC_SIGN_SECP256K1_SHA256` | secp256k1 (blockchain use cases) |

### Asymmetric Decryption
| Algorithm | Notes |
|---|---|
| `RSA_DECRYPT_OAEP_2048_SHA256` | RSA 2048-bit, OAEP padding |
| `RSA_DECRYPT_OAEP_3072_SHA256` | RSA 3072-bit |
| `RSA_DECRYPT_OAEP_4096_SHA256` | RSA 4096-bit |
| `RSA_DECRYPT_OAEP_4096_SHA512` | RSA 4096-bit, SHA-512 |

### MAC
| Algorithm | Notes |
|---|---|
| `HMAC_SHA256` | 256-bit HMAC-SHA256 |
| `HMAC_SHA512` | 512-bit HMAC-SHA512 |
| `HMAC_SHA224` | 224-bit HMAC-SHA224 |
| `HMAC_SHA384` | 384-bit HMAC-SHA384 |
| `HMAC_SHA1` | SHA-1 HMAC (legacy) |

---

## Cloud HSM

Cloud HSM provides hardware-backed key storage within FIPS 140-2 Level 3 validated HSMs managed by Google. Key material never leaves the HSM unencrypted.

- **Protection level**: `HSM` (vs `SOFTWARE` for standard KMS)
- Same API surface as standard Cloud KMS; specify `--protection-level=hsm` at key creation.
- Supports all symmetric and asymmetric key purposes.
- No additional management overhead; Google manages the HSM infrastructure.
- Available in most regions.
- Higher cost than software-backed keys.
- Key generation is slightly slower due to HSM entropy.

---

## Cloud External Key Manager (EKM)

Cloud EKM allows you to use keys stored in a **third-party external key manager** (not in Google's infrastructure) to encrypt GCP resources. Google sends a wrapped DEK to the EKM for wrapping/unwrapping rather than ever seeing the raw key material.

### Supported EKM partners
- Thales CipherTrust
- Fortanix Data Security Manager
- Futurex
- Ionic (Machina)
- Unbound Tech (now Dyadic)

### EKM modes
- **Via VPC**: EKM reachable via a VPC and Cloud Interconnect/VPN (key never traverses the internet).
- **Via internet**: EKM reachable via public HTTPS endpoint.

### Key Access Justifications (EKM + KAJ)
Extends EKM so that Google must send a justification reason code with every key use request. The external key manager can approve or deny based on the justification. This enables compliance controls where even Google cannot decrypt data without documented justification.

---

## CMEK (Customer-Managed Encryption Keys)

CMEK allows you to use your own Cloud KMS key (instead of Google's default Google-managed encryption key) to encrypt data in GCP services.

### Services supporting CMEK (partial list)
- Cloud Storage (bucket-level and default object key)
- BigQuery (dataset-level)
- Compute Engine (persistent disks, boot disks, snapshots, images)
- Cloud SQL (instance-level)
- Cloud Spanner
- Cloud Bigtable
- Pub/Sub (topic-level)
- Artifact Registry
- Cloud Build
- Vertex AI datasets, models, training jobs
- Cloud Composer (environments)
- Dataflow (pipelines)
- Kubernetes Engine (etcd encryption)

### CMEK: key requirements
- The service agent (e.g., `service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com` for Cloud Storage) must have `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the CMEK key.
- The KMS key must be in the same region as the resource (with some exceptions; check per-service docs).
- If the key is disabled or destroyed, the encrypted resource becomes inaccessible.

### Enabling CMEK for Cloud Storage
```bash
# Grant the GCS service account permission to use the KMS key
gcloud kms keys add-iam-policy-binding KMS_KEY \
  --location=REGION \
  --keyring=KEYRING \
  --member="serviceAccount:service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" \
  --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Create a bucket with default CMEK
gcloud storage buckets create gs://my-bucket \
  --location=us-central1 \
  --default-encryption-key=projects/PROJECT_ID/locations/REGION/keyRings/KEYRING/cryptoKeys/KMS_KEY
```

### Enabling CMEK for BigQuery
```bash
# Grant the BQ service account permission
gcloud kms keys add-iam-policy-binding KMS_KEY \
  --location=REGION \
  --keyring=KEYRING \
  --member="serviceAccount:bq-PROJECT_NUMBER@bigquery-encryption.iam.gserviceaccount.com" \
  --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Create a dataset with CMEK (via bq CLI)
bq mk \
  --dataset \
  --default_kms_key=projects/PROJECT_ID/locations/REGION/keyRings/KEYRING/cryptoKeys/KMS_KEY \
  PROJECT_ID:my_dataset
```

---

## Envelope Encryption Pattern

Envelope encryption is used when encrypting large data sets directly with KMS would be impractical (KMS is not designed for bulk data encryption; maximum plaintext size is 64 KiB).

### Pattern:
1. Generate a **data encryption key (DEK)** locally (e.g., AES-256-GCM random key).
2. Encrypt the data with the DEK.
3. Call Cloud KMS to **wrap (encrypt) the DEK** with your KMS key encryption key (KEK).
4. Store the wrapped DEK alongside the encrypted data.

### Decryption:
1. Read the wrapped DEK from storage.
2. Call Cloud KMS to **unwrap (decrypt) the DEK**.
3. Decrypt the data with the unwrapped DEK.
4. Destroy the plaintext DEK from memory immediately after use.

This pattern is used by Google Cloud services implementing CMEK internally, and should be used in application code whenever encrypting large data.

---

## Key Rotation

### Automatic rotation
Set a **rotation period** on a symmetric key; Cloud KMS automatically creates a new primary version on schedule. Old versions are retained (ENABLED) so existing ciphertext can still be decrypted.

- Minimum rotation period: 1 day
- Recommendation: 90-day rotation period for CMEK keys; 365 days for low-risk keys
- `--rotation-period` and `--next-rotation-time` set on key creation or update

### Manual rotation
```bash
# Create a new key version manually and set it as primary
gcloud kms keys versions create \
  --location=REGION \
  --keyring=KEYRING \
  --key=KMS_KEY \
  --primary
```

### Re-encryption after rotation
Cloud KMS rotation creates a new primary version, but **does not automatically re-encrypt existing data**. To fully benefit from rotation:
- Re-encrypt existing data by decrypting with the old version and re-encrypting with the new primary.
- GCP-managed CMEK resources (BigQuery tables, GCS objects) need to be explicitly re-encrypted using service-specific commands.

---

## IAM Roles for Cloud KMS

| Role | Permissions | Use |
|---|---|---|
| `roles/cloudkms.admin` | Create/delete keys and key rings, manage IAM | Key administrators |
| `roles/cloudkms.cryptoKeyEncrypterDecrypter` | Encrypt and decrypt | Services using CMEK |
| `roles/cloudkms.cryptoKeyEncrypter` | Encrypt only | Write-only services |
| `roles/cloudkms.cryptoKeyDecrypter` | Decrypt only | Read/decrypt services |
| `roles/cloudkms.signer` | Sign (asymmetric) | Signing workloads |
| `roles/cloudkms.signerVerifier` | Sign and verify | Signing + verification |
| `roles/cloudkms.verifier` | Verify only | Signature verification |
| `roles/cloudkms.publicKeyViewer` | Get public key | Download public keys |
| `roles/cloudkms.viewer` | List and describe keys | Read-only audit |
| `roles/cloudkms.importer` | Import key material | Key import workflows |

---

## Key Import

Cloud KMS supports importing existing key material into a new key version, enabling migration of existing keys into KMS without re-encrypting data.

### Import process:
1. Create an **import job** specifying the import method (`rsa-oaep-3072-sha256-aes-256` is recommended).
2. Download the import job's public key.
3. Wrap your key material using the import job's public key (using a provided wrapping script or manually with OpenSSL).
4. Create a new key version with the wrapped key material.

**Limitations**: imported keys cannot be used for auto-rotation because the imported material is already provisioned.

---

## Best Practices

1. **Use HSM-backed keys for sensitive data** (PCI, healthcare, financial) to satisfy compliance requirements.
2. **Separate key rings per environment** (prod, staging, dev) to minimize blast radius of key compromise.
3. **Apply CMEK to all sensitive GCP services** as a defense-in-depth control.
4. **Enable automatic rotation** with a 90-day period for active encryption keys.
5. **Separate duties**: key administrators (`roles/cloudkms.admin`) should not be the same principals as those who use keys (`roles/cloudkms.cryptoKeyEncrypterDecrypter`).
6. **Monitor key usage** with Cloud Audit Logs (`cloudkms.googleapis.com` data access logs enabled).
7. **Test key destruction** in non-production environments before destroying any production key versions; set destruction delay to the maximum allowed.
8. **Use envelope encryption** in application code; never pass more than 64 KiB of plaintext to the KMS API.
9. **Use EKM with Key Access Justifications** for regulatory environments requiring complete control over Google access.
10. **Grant service agents minimum KMS permissions** — `roles/cloudkms.cryptoKeyEncrypterDecrypter` only where both encrypt and decrypt are needed.
