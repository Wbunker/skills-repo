# AWS Secrets Manager, ACM & CloudHSM — CLI Reference
For service concepts, see [secrets-acm-cloudhsm-capabilities.md](secrets-acm-cloudhsm-capabilities.md).

## AWS Secrets Manager

```bash
# --- Create and manage secrets ---
aws secretsmanager create-secret \
  --name prod/myapp/database \
  --description "Production DB credentials" \
  --secret-string '{"username":"admin","password":"s3cr3t"}' \
  --kms-key-id alias/my-key \
  --tags Key=Environment,Value=Production

# From file
aws secretsmanager create-secret \
  --name prod/myapp/apikey \
  --secret-string file://secret.json

aws secretsmanager list-secrets
aws secretsmanager describe-secret --secret-id prod/myapp/database
aws secretsmanager update-secret \
  --secret-id prod/myapp/database \
  --secret-string '{"username":"admin","password":"newpassword"}'
aws secretsmanager delete-secret \
  --secret-id prod/myapp/database \
  --recovery-window-in-days 30  # or --force-delete-without-recovery

# --- Retrieve secrets ---
aws secretsmanager get-secret-value --secret-id prod/myapp/database
aws secretsmanager get-secret-value \
  --secret-id prod/myapp/database \
  --version-stage AWSPREVIOUS  # get previous version

# --- Rotation ---
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database \
  --rotate-immediately  # rotate now and enable ongoing rotation

# Built-in rotation for RDS (managed rotation)
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database
  # If using native rotation (RDS), Secrets Manager handles Lambda automatically

aws secretsmanager describe-secret --secret-id prod/myapp/database  # check RotationEnabled

# Cancel rotation
aws secretsmanager cancel-rotate-secret --secret-id prod/myapp/database

# --- Versions ---
aws secretsmanager list-secret-version-ids --secret-id prod/myapp/database
aws secretsmanager update-secret-version-stage \
  --secret-id prod/myapp/database \
  --version-stage AWSCURRENT \
  --move-to-version-id version-id \
  --remove-from-version-id old-version-id

# --- Resource policy ---
aws secretsmanager put-resource-policy \
  --secret-id prod/myapp/database \
  --resource-policy file://secret-policy.json \
  --block-public-policy
aws secretsmanager get-resource-policy --secret-id prod/myapp/database
aws secretsmanager delete-resource-policy --secret-id prod/myapp/database

# --- Replication ---
aws secretsmanager replicate-secret-to-regions \
  --secret-id prod/myapp/database \
  --add-replica-regions Region=us-west-2 Region=eu-west-1
aws secretsmanager remove-regions-from-replication \
  --secret-id prod/myapp/database \
  --remove-replica-regions us-west-2
aws secretsmanager stop-replication-to-replica --secret-id replica-arn
```

---

## AWS Certificate Manager

```bash
# --- Request certificates ---
# Public cert - DNS validation
aws acm request-certificate \
  --domain-name myapp.example.com \
  --subject-alternative-names "*.myapp.example.com" "api.example.com" \
  --validation-method DNS \
  --idempotency-token myapp-cert-2024

# Public cert - Email validation
aws acm request-certificate \
  --domain-name myapp.example.com \
  --validation-method EMAIL

aws acm list-certificates
aws acm describe-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm get-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm delete-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm renew-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx

# Get DNS validation records (to add to Route 53 or other DNS)
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --query 'Certificate.DomainValidationOptions[*].ResourceRecord'

# Add validation CNAME to Route 53 automatically
aws acm add-tags-to-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --tags Key=Environment,Value=Production
aws acm list-tags-for-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm remove-tags-from-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --tags Key=Environment

# --- Import certificate ---
aws acm import-certificate \
  --certificate fileb://certificate.pem \
  --private-key fileb://private.key \
  --certificate-chain fileb://chain.pem

# Update imported cert (re-import with same ARN)
aws acm import-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --certificate fileb://new-certificate.pem \
  --private-key fileb://new-private.key \
  --certificate-chain fileb://new-chain.pem

# --- Private CA certs ---
aws acm request-certificate \
  --domain-name internal.example.com \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/xxx \
  --validation-method NONE  # private CA; no domain validation needed
```

---

## AWS CloudHSM

```bash
# --- Cluster management ---
aws cloudhsmv2 create-cluster \
  --hsm-type hsm2m.medium \
  --subnet-ids subnet-xxxxxxxx subnet-yyyyyyyy
aws cloudhsmv2 describe-clusters
aws cloudhsmv2 describe-clusters \
  --filters clusterIds=cluster-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 delete-cluster --cluster-id cluster-xxxxxxxxxxxxxxxxx

# --- HSM instances ---
aws cloudhsmv2 create-hsm \
  --cluster-id cluster-xxxxxxxxxxxxxxxxx \
  --availability-zone us-east-1a
aws cloudhsmv2 describe-clusters  # see HSMs under each cluster
aws cloudhsmv2 delete-hsm \
  --cluster-id cluster-xxxxxxxxxxxxxxxxx \
  --hsm-id hsm-xxxxxxxxxxxxxxxxx

# --- Initialization (first-time setup) ---
# 1. Get cluster CSR
aws cloudhsmv2 describe-clusters \
  --filters clusterIds=cluster-xxx \
  --query 'Clusters[0].Certificates.ClusterCsr' \
  --output text > cluster.csr
# 2. Sign CSR with your CA → cluster-cert.pem
# 3. Initialize
aws cloudhsmv2 initialize-cluster \
  --cluster-id cluster-xxx \
  --signed-cert file://cluster-cert.pem \
  --trust-anchor file://ca-cert.pem

# --- Backups ---
aws cloudhsmv2 list-tags --resource-id cluster-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 describe-backups
aws cloudhsmv2 copy-backup-to-region \
  --destination-region us-west-2 \
  --backup-id backup-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 delete-backup --backup-id backup-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 restore-backup --backup-id backup-xxxxxxxxxxxxxxxxx

# --- Tags ---
aws cloudhsmv2 tag-resource \
  --resource-id cluster-xxxxxxxxxxxxxxxxx \
  --tag-list Key=Environment,Value=Production
aws cloudhsmv2 untag-resource \
  --resource-id cluster-xxxxxxxxxxxxxxxxx \
  --tag-key-list Environment
```
