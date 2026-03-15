# Cloud KMS — CLI Reference

## Key Rings

```bash
# Create a key ring in a specific region
gcloud kms keyrings create my-keyring \
  --location=us-central1

# Create a global key ring (use sparingly; prefer regional)
gcloud kms keyrings create global-keyring \
  --location=global

# List key rings in a location
gcloud kms keyrings list \
  --location=us-central1

# Describe a key ring
gcloud kms keyrings describe my-keyring \
  --location=us-central1

# Get IAM policy on a key ring
gcloud kms keyrings get-iam-policy my-keyring \
  --location=us-central1

# Grant a role on a key ring (applies to all keys within it)
gcloud kms keyrings add-iam-policy-binding my-keyring \
  --location=us-central1 \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

---

## Symmetric Keys (ENCRYPT_DECRYPT)

```bash
# Create a software-backed symmetric key with 90-day auto-rotation
gcloud kms keys create my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption \
  --rotation-period=7776000s \
  --next-rotation-time="2025-06-01T00:00:00Z"

# Create an HSM-backed symmetric key
gcloud kms keys create my-hsm-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption \
  --protection-level=hsm \
  --rotation-period=7776000s

# Create a symmetric key for CMEK (no auto-rotation; managed manually)
gcloud kms keys create cmek-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption \
  --protection-level=software

# List keys in a key ring
gcloud kms keys list \
  --location=us-central1 \
  --keyring=my-keyring

# Describe a key
gcloud kms keys describe my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring

# Update rotation period on an existing key
gcloud kms keys update my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --rotation-period=15552000s \
  --next-rotation-time="2026-01-01T00:00:00Z"

# Remove automatic rotation (set rotation period to 0)
gcloud kms keys update my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --remove-rotation-schedule

# Set key labels
gcloud kms keys update my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --update-labels=env=production,team=platform
```

---

## Asymmetric Keys

```bash
# Create an asymmetric signing key (EC P-256, software-backed)
gcloud kms keys create my-signing-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=asymmetric-signing \
  --default-algorithm=ec-sign-p256-sha256

# Create an RSA 4096 signing key (HSM-backed)
gcloud kms keys create my-rsa-signing-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=asymmetric-signing \
  --default-algorithm=rsa-sign-pkcs1-4096-sha256 \
  --protection-level=hsm

# Create an asymmetric decryption key (RSA 3072 OAEP)
gcloud kms keys create my-decrypt-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=asymmetric-encryption \
  --default-algorithm=rsa-decrypt-oaep-3072-sha256

# Get the public key for an asymmetric key version
gcloud kms keys versions get-public-key 1 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-signing-key \
  --output-file=public-key.pem
```

---

## MAC Keys

```bash
# Create an HMAC-SHA256 key
gcloud kms keys create my-mac-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=mac \
  --default-algorithm=hmac-sha256

# Sign a message with an HMAC key
gcloud kms mac-sign \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-mac-key \
  --version=1 \
  --input-file=message.txt \
  --signature-file=message.sig

# Verify an HMAC signature
gcloud kms mac-verify \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-mac-key \
  --version=1 \
  --input-file=message.txt \
  --signature-file=message.sig
```

---

## Key Versions

```bash
# List all versions of a key
gcloud kms keys versions list \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Describe a specific version
gcloud kms keys versions describe 1 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Create a new key version manually (for manual rotation)
gcloud kms keys versions create \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Create a new version and immediately set it as primary
gcloud kms keys versions create \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --primary

# Set an existing version as the primary
gcloud kms keys set-primary-version my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --version=3

# Disable a key version (blocks use; can be re-enabled)
gcloud kms keys versions disable 2 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Re-enable a disabled key version
gcloud kms keys versions enable 2 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Schedule a key version for destruction (default 24-hour delay)
gcloud kms keys versions destroy 2 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Restore a key version that is PENDING_DESTRUCTION (before the delay expires)
gcloud kms keys versions restore 2 \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key

# Update the destruction wait duration on a key (1–120 days)
gcloud kms keys update my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --destroy-scheduled-duration=604800s
```

---

## Encrypt and Decrypt

```bash
# Encrypt a file with a symmetric key
gcloud kms encrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --plaintext-file=secret.txt \
  --ciphertext-file=secret.enc

# Encrypt using a specific key version
gcloud kms encrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --version=3 \
  --plaintext-file=secret.txt \
  --ciphertext-file=secret.enc

# Encrypt with additional authenticated data (AAD) for integrity binding
gcloud kms encrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --plaintext-file=secret.txt \
  --ciphertext-file=secret.enc \
  --additional-authenticated-data="my-context-string"

# Decrypt a file
gcloud kms decrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --ciphertext-file=secret.enc \
  --plaintext-file=decrypted.txt

# Decrypt with AAD (must match what was used during encryption)
gcloud kms decrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --ciphertext-file=secret.enc \
  --plaintext-file=decrypted.txt \
  --additional-authenticated-data="my-context-string"

# Asymmetric signing — sign a file
gcloud kms asymmetric-sign \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-signing-key \
  --version=1 \
  --digest-algorithm=sha256 \
  --input-file=file-to-sign.txt \
  --signature-file=file.sig

# Asymmetric signing — verify a signature (using OpenSSL with the exported public key)
# (verification is done client-side since KMS does not have a verify API for asymmetric-sign keys)
openssl dgst -sha256 -verify public-key.pem -signature file.sig file-to-sign.txt

# Asymmetric decryption — decrypt with KMS private key
gcloud kms asymmetric-decrypt \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-decrypt-key \
  --version=1 \
  --ciphertext-file=encrypted.bin \
  --plaintext-file=decrypted.txt
```

---

## IAM on Keys

```bash
# Grant encrypt/decrypt on a specific key
gcloud kms keys add-iam-policy-binding my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Grant encrypt-only (write workloads)
gcloud kms keys add-iam-policy-binding my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:writer-sa@project.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypter"

# Grant signer role on an asymmetric key
gcloud kms keys add-iam-policy-binding my-signing-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:signing-sa@project.iam.gserviceaccount.com" \
  --role="roles/cloudkms.signer"

# Get IAM policy on a key
gcloud kms keys get-iam-policy my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring

# Remove a binding from a key
gcloud kms keys remove-iam-policy-binding my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Grant a service account permission to use a KMS key for CMEK (BigQuery example)
gcloud kms keys add-iam-policy-binding my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:bq-PROJECT_NUMBER@bigquery-encryption.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Grant Cloud Storage service agent permission for CMEK
gcloud kms keys add-iam-policy-binding my-sym-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member="serviceAccount:service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

---

## CMEK Examples

```bash
# Enable CMEK on a Cloud Storage bucket (new bucket)
gcloud storage buckets create gs://my-cmek-bucket \
  --location=us-central1 \
  --default-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key

# Update default encryption key on an existing bucket
gcloud storage buckets update gs://my-existing-bucket \
  --default-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key

# Create a Compute Engine disk with CMEK
gcloud compute disks create my-encrypted-disk \
  --zone=us-central1-a \
  --size=100GB \
  --kms-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key

# Create a Compute Engine instance with CMEK boot disk
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=n2-standard-4 \
  --boot-disk-kms-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key \
  --image-family=debian-12 \
  --image-project=debian-cloud

# Enable CMEK on a Cloud SQL instance (set at instance creation)
gcloud sql instances create my-sql-instance \
  --database-version=POSTGRES_15 \
  --region=us-central1 \
  --tier=db-n1-standard-4 \
  --disk-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key

# Create a Pub/Sub topic with CMEK
gcloud pubsub topics create my-topic \
  --message-storage-policy-allowed-regions=us-central1 \
  --topic-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-sym-key
```

---

## Key Import Jobs

```bash
# Create an import job to bring external key material into KMS
gcloud kms import-jobs create my-import-job \
  --location=us-central1 \
  --keyring=my-keyring \
  --import-method=rsa-oaep-3072-sha256-aes-256 \
  --protection-level=software

# Describe the import job (to get the public key for wrapping)
gcloud kms import-jobs describe my-import-job \
  --location=us-central1 \
  --keyring=my-keyring

# Get just the public key from the import job
gcloud kms import-jobs describe my-import-job \
  --location=us-central1 \
  --keyring=my-keyring \
  --format="value(publicKey.pem)"

# List import jobs
gcloud kms import-jobs list \
  --location=us-central1 \
  --keyring=my-keyring

# Import wrapped key material into a key version
gcloud kms keys versions import \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-sym-key \
  --import-job=my-import-job \
  --algorithm=google-symmetric-encryption \
  --wrapped-key-file=wrapped-key.bin
```

---

## External Key Manager (EKM)

```bash
# Create an EKM key (requires EKM service configured separately)
gcloud kms keys create my-ekm-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption \
  --protection-level=external \
  --default-algorithm=external-symmetric-encryption \
  --skip-initial-version-creation

# Create an EKM key version pointing to external key URI
gcloud kms keys versions create \
  --location=us-central1 \
  --keyring=my-keyring \
  --key=my-ekm-key \
  --external-key-uri="https://ekm.example.com/v1/projects/PROJECT/keys/KEY_ID/cryptoKeyVersions/1"

# List EKM configs (VPC-hosted EKM configuration)
gcloud kms ekmconfig describe \
  --location=us-central1

# Update the EKM service resolver
gcloud kms ekmconfig update \
  --location=us-central1 \
  --keymanagementserviceresolvers=ekm-resolver-name
```

---

## Monitoring Key Usage

```bash
# Enable data access audit logs for KMS (via gcloud logging — set in organization IAM audit config)
# Typically configured in the GCP Console IAM & Admin > Audit Logs

# List recent KMS operations from Cloud Audit Logs
gcloud logging read \
  'resource.type="cloudkms_cryptokey" AND logName:"cloudaudit.googleapis.com%2Fdata_access"' \
  --project=PROJECT_ID \
  --limit=50 \
  --format="table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)"

# Check for upcoming key rotations
gcloud kms keys list \
  --location=us-central1 \
  --keyring=my-keyring \
  --filter="nextRotationTime<2025-12-31" \
  --format="table(name,nextRotationTime,rotationPeriod)"
```
