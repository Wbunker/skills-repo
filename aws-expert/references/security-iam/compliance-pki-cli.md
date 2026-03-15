# Compliance & PKI — CLI Reference
For service concepts, see [compliance-pki-capabilities.md](compliance-pki-capabilities.md).

## AWS Artifact

```bash
# --- List and retrieve reports ---
aws artifact list-reports
aws artifact get-report-metadata --report-id r-abc123
aws artifact get-term-for-report --report-id r-abc123

# Download a report (generates a pre-signed S3 URL)
aws artifact get-report \
  --report-id r-abc123 \
  --term-token <token-from-get-term-for-report>

# List report versions
aws artifact list-report-versions --report-id r-abc123

# --- Agreements ---
aws artifact list-customer-agreements

# --- Account settings ---
aws artifact get-account-settings
aws artifact put-account-settings \
  --notification-subscription-status SUBSCRIBED
```

---

## AWS Audit Manager

```bash
# --- Enable Audit Manager ---
aws auditmanager register-account
aws auditmanager get-account-status

# --- List and use prebuilt frameworks ---
aws auditmanager list-assessment-frameworks \
  --framework-type Standard  # Standard = prebuilt; Custom = user-defined

aws auditmanager get-assessment-framework \
  --framework-id arn:aws:auditmanager:us-east-1::framework/PCI-DSS

# --- Create an assessment ---
aws auditmanager create-assessment \
  --name "Q4-PCI-Audit" \
  --description "PCI DSS assessment for Q4" \
  --assessment-reports-destination destinationType=S3,destination=s3://my-audit-bucket \
  --scope '{"awsAccounts":[{"id":"123456789012"}],"awsServices":[{"serviceName":"S3"},{"serviceName":"RDS"}]}' \
  --roles '[{"roleType":"PROCESS_OWNER","roleArn":"arn:aws:iam::123456789012:role/AuditManagerRole"}]' \
  --framework-id arn:aws:auditmanager:us-east-1::framework/PCI-DSS

aws auditmanager list-assessments
aws auditmanager get-assessment --assessment-id <id>

# Deactivate assessment to stop evidence collection
aws auditmanager update-assessment-status \
  --assessment-id <id> \
  --status INACTIVE

# --- Generate an assessment report ---
aws auditmanager create-assessment-report \
  --name "PCI-Q4-Report" \
  --assessment-id <id>

aws auditmanager get-assessment-report-url \
  --assessment-id <id> \
  --assessment-report-id <report-id>

aws auditmanager validate-assessment-report-integrity \
  --s3-relative-path "s3://my-audit-bucket/report.pdf"

# --- Evidence ---
aws auditmanager get-evidence \
  --assessment-id <id> \
  --control-set-id <control-set-id> \
  --control-id <control-id> \
  --evidence-folder-id <folder-id> \
  --evidence-id <evidence-id>

# Upload manual evidence (file)
aws auditmanager get-evidence-file-upload-url \
  --file-name policy-screenshot.png
# Then upload to the returned pre-signed URL

# Import manual evidence
aws auditmanager batch-import-evidence-to-assessment-control \
  --assessment-id <id> \
  --control-set-id <control-set-id> \
  --control-id <control-id> \
  --manual-evidence '[{"s3ResourcePath":"s3://my-audit-bucket/evidence/policy.pdf"}]'

# --- Custom framework ---
aws auditmanager create-assessment-framework \
  --name "Internal-SOC2-Lite" \
  --control-sets file://control-sets.json

# --- Settings (e.g. default S3 bucket for reports) ---
aws auditmanager get-settings --attribute ALL
aws auditmanager update-settings \
  --default-assessment-reports-destination \
    destinationType=S3,destination=s3://my-central-audit-bucket \
  --default-process-owners '[{"roleType":"PROCESS_OWNER","roleArn":"arn:aws:iam::123456789012:role/AuditRole"}]'
```

---

## AWS Private Certificate Authority (AWS Private CA)

```bash
# --- Create a CA ---
# Create a root CA
aws acm-pca create-certificate-authority \
  --certificate-authority-type ROOT \
  --certificate-authority-configuration \
    'KeyAlgorithm=RSA_2048,SigningAlgorithm=SHA256WITHRSA,Subject={Country=US,Organization=MyOrg,CommonName=MyOrg Root CA}' \
  --revocation-configuration \
    'CrlConfiguration={Enabled=true,ExpirationInDays=7,S3BucketName=my-crl-bucket}' \
  --tags Key=Environment,Value=Production

# Create a subordinate CA (recommended for issuing end-entity certs)
aws acm-pca create-certificate-authority \
  --certificate-authority-type SUBORDINATE \
  --certificate-authority-configuration \
    'KeyAlgorithm=EC_prime256v1,SigningAlgorithm=SHA256WITHECDSA,Subject={Country=US,Organization=MyOrg,CommonName=MyOrg Issuing CA}'

aws acm-pca list-certificate-authorities
aws acm-pca describe-certificate-authority \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/xxx

# --- Activate a subordinate CA ---
# 1. Get the CSR
aws acm-pca get-certificate-authority-csr \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --output text > subordinate.csr

# 2. Sign the CSR with the root CA
aws acm-pca issue-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/root-xxx \
  --csr fileb://subordinate.csr \
  --signing-algorithm SHA256WITHRSA \
  --template-arn arn:aws:acm-pca:::template/SubordinateCACertificate_PathLen0/V1 \
  --validity Value=10,Type=YEARS

# 3. Get the signed cert and chain
aws acm-pca get-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/root-xxx \
  --certificate-arn arn:aws:acm-pca:us-east-1:123456789012:certificate/xxx

# 4. Import signed cert into the subordinate CA
aws acm-pca import-certificate-authority-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --certificate fileb://subordinate-cert.pem \
  --certificate-chain fileb://root-cert.pem

# --- Issue end-entity certificates ---
# Issue a certificate (returns certificate ARN; use get-certificate to retrieve PEM)
aws acm-pca issue-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --csr fileb://server.csr \
  --signing-algorithm SHA256WITHECDSA \
  --validity Value=365,Type=DAYS \
  --idempotency-token my-server-cert-2024

aws acm-pca get-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --certificate-arn arn:aws:acm-pca:us-east-1:123456789012:certificate/yyy

# --- Revocation ---
aws acm-pca revoke-certificate \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --certificate-serial 67:07:44:... \
  --revocation-reason KEY_COMPROMISE

# --- Audit report (lists all issued/revoked certs) ---
aws acm-pca create-certificate-authority-audit-report \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --s3-bucket-name my-audit-bucket \
  --audit-report-response-format JSON

aws acm-pca describe-certificate-authority-audit-report \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --audit-report-id <report-id>

# --- Cross-account sharing ---
# Grant another account permission to issue certs from this CA
aws acm-pca put-policy \
  --resource-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --policy file://cross-account-policy.json

aws acm-pca get-policy \
  --resource-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx

# Create RAM share for cross-account CA sharing
aws acm-pca create-permission \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --principal 234567890123 \
  --actions IssueCertificate GetCertificate ListPermissions

aws acm-pca list-permissions \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx

# --- Delete and restore ---
# Disable first, then delete (10–30 day recovery window)
aws acm-pca update-certificate-authority \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --status DISABLED

aws acm-pca delete-certificate-authority \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx \
  --permanent-deletion-time-in-days 14

aws acm-pca restore-certificate-authority \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/sub-xxx
```

---

## AWS Payment Cryptography

```bash
# Control plane: key management (aws payment-cryptography)
# Data plane: cryptographic operations (aws payment-cryptography-data)

# --- Control plane: key management ---
# Create a key (generated in HSM)
aws payment-cryptography create-key \
  --key-attributes \
    KeyAlgorithm=TDES_3KEY,KeyClass=SYMMETRIC_KEY,KeyUsage=TR31_P0_PIN_ENCRYPTION,KeyModesOfUse='{Decrypt=true,Encrypt=true,Wrap=true,Unwrap=true}' \
  --exportable \
  --tags Key=Environment,Value=Production

aws payment-cryptography list-keys
aws payment-cryptography get-key --key-identifier arn:aws:payment-cryptography:us-east-1:123456789012:key/xxx

# Create an alias
aws payment-cryptography create-alias \
  --alias-name alias/prod-pin-encryption-key \
  --key-arn arn:aws:payment-cryptography:us-east-1:123456789012:key/xxx

aws payment-cryptography list-aliases
aws payment-cryptography update-alias \
  --alias-name alias/prod-pin-encryption-key \
  --key-arn arn:aws:payment-cryptography:us-east-1:123456789012:key/yyy  # re-point alias to new key

# Enable / disable a key
aws payment-cryptography start-key-usage \
  --key-identifier alias/prod-pin-encryption-key
aws payment-cryptography stop-key-usage \
  --key-identifier alias/prod-pin-encryption-key

# Delete a key (7–83 day waiting period)
aws payment-cryptography delete-key \
  --key-identifier alias/prod-pin-encryption-key \
  --delete-key-in-days 30

aws payment-cryptography restore-key \
  --key-identifier arn:aws:payment-cryptography:us-east-1:123456789012:key/xxx

# --- Key import (TR-31 / TR-34) ---
# Get parameters for TR-34 import (returns wrapping key cert)
aws payment-cryptography get-parameters-for-import \
  --key-material-type TR34_KEY_BLOCK \
  --wrapping-key-algorithm RSA_2048

# Import a key via TR-31 key block
aws payment-cryptography import-key \
  --key-material \
    'Tr31KeyBlock={WrappedKeyBlock=<tr31-block>,WrappingKeyIdentifier=alias/kek}'

# Import a key via TR-34
aws payment-cryptography import-key \
  --key-material \
    'Tr34KeyBlock={CertificateAuthorityPublicKeyIdentifier=arn:...,KeyBlockFormat=X9_TR34_2012,SigningKeyCertificate=<pem>,WrappedKeyBlock=<tr34-block>,WrappingKeyCertificate=<pem>}'

# --- Key export (TR-31) ---
aws payment-cryptography get-parameters-for-export \
  --key-material-type TR31_KEY_BLOCK \
  --signing-key-algorithm RSA_2048

aws payment-cryptography export-key \
  --key-material \
    'Tr31KeyBlock={WrappingKeyIdentifier=alias/kek}' \
  --export-key-identifier alias/prod-pin-encryption-key

# --- Multi-region replication ---
aws payment-cryptography add-key-replication-regions \
  --key-identifier alias/prod-pin-encryption-key \
  --replication-regions us-west-2 eu-west-1

# --- Data plane: cryptographic operations ---
# Translate PIN data between encryption keys / PIN block formats
aws payment-cryptography-data translate-pin-data \
  --incoming-translation-attributes \
    'IsoFormat0={PrimaryAccountNumber=1234567890123456}' \
  --incoming-key-identifier alias/acquiring-pin-key \
  --incoming-wrapped-key 'WrappedKeyMaterial={DukptIpek={KeySerialNumber=<ksn>,PekId=<pek>}}' \
  --outgoing-translation-attributes 'IsoFormat3={}' \
  --outgoing-key-identifier alias/issuer-pin-key

# Encrypt cardholder data
aws payment-cryptography-data encrypt-data \
  --key-identifier alias/data-encryption-key \
  --plain-text <hex-encoded-plaintext> \
  --encryption-attributes 'Dukpt={DukptKeyDerivationType=AES_128,KeySerialNumber=<ksn>,Mode=CBC,DukptKeyVariant=REQUEST}'

# Generate a MAC for a payment message
aws payment-cryptography-data generate-mac \
  --key-identifier alias/mac-key \
  --message-data <hex-encoded-message> \
  --generation-attributes 'Algorithm=ISO9797_ALGORITHM3'

# Verify a MAC
aws payment-cryptography-data verify-mac \
  --key-identifier alias/mac-key \
  --message-data <hex-encoded-message> \
  --mac <hex-encoded-mac> \
  --verification-attributes 'Algorithm=ISO9797_ALGORITHM3'

# Generate CVV/CVV2
aws payment-cryptography-data generate-card-validation-data \
  --key-identifier alias/cvk \
  --primary-account-number 1234567890123456 \
  --generation-attributes 'Cvv={CardExpiryDate=2412}'

# Verify EMV authentication request cryptogram (ARQC)
aws payment-cryptography-data verify-auth-request-cryptogram \
  --key-identifier alias/udk \
  --transaction-data <hex-data> \
  --auth-request-cryptogram <hex-arqc> \
  --major-key-derivation-mode EMV_OPTION_A \
  --session-key-derivation-attributes 'EmvCommon={ApplicationCryptogram=<hex>,PanSequenceNumber=01,PrimaryAccountNumber=1234567890123456}'
```

---

## AWS Signer

```bash
# --- Platforms ---
# List all available signing platforms (e.g., AWSLambda-SHA384-ECDSA)
aws signer list-signing-platforms

# --- Signing profiles ---
# Create (or update) a signing profile on a given platform
aws signer put-signing-profile \
  --profile-name MyLambdaSigningProfile \
  --platform-id AWSLambda-SHA384-ECDSA \
  --signature-validity-period Value=12,Type=MONTHS

aws signer get-signing-profile \
  --profile-name MyLambdaSigningProfile

aws signer list-signing-profiles
aws signer list-signing-profiles \
  --platform-id AWSLambda-SHA384-ECDSA \
  --statuses Active

# Revoke a signing profile (all future signatures from this profile are invalid)
aws signer cancel-signing-profile \
  --profile-name MyLambdaSigningProfile

aws signer revoke-signing-profile \
  --profile-name MyLambdaSigningProfile \
  --profile-version <version> \
  --reason "Key compromise" \
  --effective-time $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Signing jobs ---
# Start a signing job (source and destination are S3)
aws signer start-signing-job \
  --source 'S3={bucketName=my-source-bucket,key=my-lambda.zip,version=abc123}' \
  --destination 'S3={bucketName=my-signed-bucket,prefix=signed/}' \
  --profile-name MyLambdaSigningProfile

aws signer describe-signing-job \
  --job-id <job-id>

aws signer list-signing-jobs
aws signer list-signing-jobs \
  --platform-id AWSLambda-SHA384-ECDSA \
  --status Succeeded

# Revoke a specific signature (by job ID)
aws signer revoke-signature \
  --job-id <job-id> \
  --reason "Artifact compromised"

# --- Profile permissions (cross-account signing) ---
# Grant another account permission to use this signing profile
aws signer add-profile-permission \
  --profile-name MyLambdaSigningProfile \
  --action signer:StartSigningJob \
  --principal 234567890123 \
  --statement-id AllowCrossAccountSigning

aws signer get-revocation-status \
  --certificate-hashes <hash> \
  --job-arn arn:aws:signer:us-east-1:123456789012:/signing-profiles/MyLambdaSigningProfile/revocation-status \
  --platform-id AWSLambda-SHA384-ECDSA \
  --profile-version-arns arn:aws:signer:us-east-1:123456789012:/signing-profiles/MyLambdaSigningProfile/<version> \
  --signature-timestamp $(date -u +"%Y-%m-%dT%H:%M:%SZ")
```
