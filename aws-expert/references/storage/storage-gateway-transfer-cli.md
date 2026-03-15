# AWS Storage Gateway & Transfer Family — CLI Reference

For service concepts, see [storage-gateway-transfer-capabilities.md](storage-gateway-transfer-capabilities.md).

## Storage Gateway

```bash
# --- Gateway activation and management ---
# After deploying gateway VM/appliance on-premises, activate it
aws storagegateway activate-gateway \
  --activation-key <key-from-gateway-local-console> \
  --gateway-name my-file-gateway \
  --gateway-timezone GMT-5:00 \
  --gateway-region us-east-1 \
  --gateway-type FILE_S3

aws storagegateway list-gateways
aws storagegateway describe-gateway-information --gateway-arn arn:aws:storagegateway:...
aws storagegateway update-gateway-information \
  --gateway-arn arn:aws:storagegateway:... \
  --gateway-name new-name

aws storagegateway delete-gateway --gateway-arn arn:aws:storagegateway:...

# Update gateway software
aws storagegateway update-gateway-software-now --gateway-arn arn:aws:storagegateway:...

# --- S3 File Gateway: NFS File Shares ---
aws storagegateway create-nfs-file-share \
  --client-token my-token-123 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-xxx \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --location-arn arn:aws:s3:::my-bucket \
  --default-storage-class S3_STANDARD \
  --kms-encrypted \
  --kms-key arn:aws:kms:us-east-1:123456789012:key/key-id

aws storagegateway list-file-shares --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-nfs-file-shares --file-share-arn-list arn:aws:storagegateway:...
aws storagegateway update-nfs-file-share \
  --file-share-arn arn:aws:storagegateway:... \
  --default-storage-class S3_INTELLIGENT_TIERING
aws storagegateway delete-file-share --file-share-arn arn:aws:storagegateway:...

# --- S3 File Gateway: SMB File Shares ---
aws storagegateway create-smb-file-share \
  --client-token my-token-456 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-xxx \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --location-arn arn:aws:s3:::my-bucket \
  --authentication ActiveDirectory

aws storagegateway describe-smb-file-shares --file-share-arn-list arn:aws:storagegateway:...
aws storagegateway describe-smb-settings --gateway-arn arn:aws:storagegateway:...
aws storagegateway join-domain \
  --gateway-arn arn:aws:storagegateway:... \
  --domain-name MYCOMPANY.COM \
  --user-name Admin \
  --password 'MyPassword'

# Trigger cache refresh (sync S3 changes to file share listing)
aws storagegateway refresh-cache \
  --gateway-arn arn:aws:storagegateway:... \
  --file-share-arn arn:aws:storagegateway:...

# --- Volume Gateway ---
aws storagegateway create-stored-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:... \
  --disk-id /dev/sdb \
  --preserve-existing-data \
  --target-name my-target \
  --network-interface-id 10.0.0.10

aws storagegateway create-cached-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:... \
  --volume-size-in-bytes 107374182400 \
  --target-name my-cached-target \
  --network-interface-id 10.0.0.10 \
  --client-token token-789

aws storagegateway list-volumes --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-stored-iscsi-volumes --volume-arns arn:aws:storagegateway:...
aws storagegateway delete-volume --volume-arn arn:aws:storagegateway:...

# Create snapshot of gateway volume
aws storagegateway create-snapshot \
  --volume-arn arn:aws:storagegateway:... \
  --snapshot-description "Daily snapshot"

# --- Tape Gateway ---
aws storagegateway create-tapes \
  --gateway-arn arn:aws:storagegateway:... \
  --tape-size-in-bytes 107374182400 \
  --client-token token-tape \
  --num-tapes-to-create 2 \
  --tape-barcode-prefix MY

aws storagegateway list-tapes --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-tapes --tape-arns arn:aws:storagegateway:...
aws storagegateway retrieve-tape-archive \
  --tape-arn arn:aws:storagegateway:... \
  --gateway-arn arn:aws:storagegateway:...
aws storagegateway delete-tape --gateway-arn arn:aws:storagegateway:... \
  --tape-arn arn:aws:storagegateway:...

# --- Bandwidth settings ---
aws storagegateway update-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:... \
  --average-upload-rate-limit-in-bits-per-sec 102400 \
  --average-download-rate-limit-in-bits-per-sec 204800
```

---

## Transfer Family

```bash
# --- Servers ---
aws transfer create-server \
  --protocols SFTP \
  --endpoint-type PUBLIC \
  --identity-provider-type SERVICE_MANAGED

# Private VPC endpoint (recommended for production)
aws transfer create-server \
  --protocols SFTP FTPS \
  --endpoint-type VPC \
  --endpoint-details VpcId=vpc-xxx,SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx \
  --identity-provider-type AWS_DIRECTORY_SERVICE \
  --directory-id d-xxxxxxxxxxxx \
  --certificate arn:aws:acm:us-east-1:123456789012:certificate/cert-id

aws transfer list-servers
aws transfer describe-server --server-id s-0123456789abcdef0
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --protocols SFTP FTPS FTPS

aws transfer start-server --server-id s-0123456789abcdef0
aws transfer stop-server --server-id s-0123456789abcdef0
aws transfer delete-server --server-id s-0123456789abcdef0

# --- Users ---
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --role arn:aws:iam::123456789012:role/TransferUserRole \
  --home-directory /my-bucket/users/alice \
  --home-directory-type PATH

# Logical home directory mapping (hide real bucket path from user)
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name bob \
  --role arn:aws:iam::123456789012:role/TransferUserRole \
  --home-directory-type LOGICAL \
  --home-directory-mappings Entry=/,Target=/my-bucket/users/bob

aws transfer list-users --server-id s-0123456789abcdef0
aws transfer describe-user --server-id s-0123456789abcdef0 --user-name alice
aws transfer update-user \
  --server-id s-0123456789abcdef0 --user-name alice \
  --policy file://scope-down-policy.json

aws transfer delete-user --server-id s-0123456789abcdef0 --user-name alice

# SSH public key management
aws transfer import-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-body "ssh-rsa AAAA..."

aws transfer list-users --server-id s-0123456789abcdef0 \
  --query 'Users[*].[UserName,HomeDirectory]' --output table

aws transfer delete-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-id key-0123456789abcdef0

# --- Workflows (post-upload processing) ---
aws transfer create-workflow \
  --steps file://workflow-steps.json \
  --description "Scan and tag uploads"

# Associate workflow with server
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --workflow-details \
  'OnUpload=[{WorkflowId=w-xxx,ExecutionRole=arn:aws:iam::123456789012:role/WorkflowRole}]'

aws transfer list-workflows
aws transfer describe-workflow --workflow-id w-0123456789abcdef0
aws transfer delete-workflow --workflow-id w-0123456789abcdef0

# --- Connectors (outbound SFTP / AS2) ---
aws transfer create-connector \
  --url sftp://partner.example.com \
  --sftp-config '{"UserSecretId":"arn:aws:secretsmanager:us-east-1:123456789012:secret:sftp-creds"}' \
  --access-role arn:aws:iam::123456789012:role/ConnectorRole

aws transfer create-connector \
  --url https://partner.example.com \
  --as2-config \
  'LocalProfileId=p-xxx,PartnerProfileId=p-yyy,MessageSubject=MyMessage,Compression=DISABLED,EncryptionAlgorithm=AES256_CBC,SigningAlgorithm=SHA256,MdnSigningAlgorithm=SHA256,MdnResponse=SYNC'

aws transfer list-connectors
aws transfer describe-connector --connector-id c-0123456789abcdef0
aws transfer delete-connector --connector-id c-0123456789abcdef0

# Start outbound file transfer via connector
aws transfer start-file-transfer \
  --connector-id c-0123456789abcdef0 \
  --send-file-paths /my-bucket/outbound/file.csv \
  --retrieve-file-paths /my-bucket/inbound/

# --- Certificates (for AS2 and FTPS) ---
aws transfer import-certificate \
  --usage SIGNING \
  --certificate file://cert.pem \
  --private-key file://private.pem \
  --certificate-chain file://chain.pem

aws transfer list-certificates
aws transfer describe-certificate --certificate-id cert-0123456789abcdef0
aws transfer delete-certificate --certificate-id cert-0123456789abcdef0
```

## Storage Gateway

```bash
# --- Gateway activation and management ---
# After deploying gateway VM/appliance on-premises, activate it
aws storagegateway activate-gateway \
  --activation-key <key-from-gateway-local-console> \
  --gateway-name my-file-gateway \
  --gateway-timezone GMT-5:00 \
  --gateway-region us-east-1 \
  --gateway-type FILE_S3

aws storagegateway list-gateways
aws storagegateway describe-gateway-information --gateway-arn arn:aws:storagegateway:...
aws storagegateway update-gateway-information \
  --gateway-arn arn:aws:storagegateway:... \
  --gateway-name new-name

aws storagegateway delete-gateway --gateway-arn arn:aws:storagegateway:...

# Update gateway software
aws storagegateway update-gateway-software-now --gateway-arn arn:aws:storagegateway:...

# --- S3 File Gateway: NFS File Shares ---
aws storagegateway create-nfs-file-share \
  --client-token my-token-123 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-xxx \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --location-arn arn:aws:s3:::my-bucket \
  --default-storage-class S3_STANDARD \
  --kms-encrypted \
  --kms-key arn:aws:kms:us-east-1:123456789012:key/key-id

aws storagegateway list-file-shares --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-nfs-file-shares --file-share-arn-list arn:aws:storagegateway:...
aws storagegateway update-nfs-file-share \
  --file-share-arn arn:aws:storagegateway:... \
  --default-storage-class S3_INTELLIGENT_TIERING
aws storagegateway delete-file-share --file-share-arn arn:aws:storagegateway:...

# --- S3 File Gateway: SMB File Shares ---
aws storagegateway create-smb-file-share \
  --client-token my-token-456 \
  --gateway-arn arn:aws:storagegateway:us-east-1:123456789012:gateway/sgw-xxx \
  --role arn:aws:iam::123456789012:role/StorageGatewayRole \
  --location-arn arn:aws:s3:::my-bucket \
  --authentication ActiveDirectory

aws storagegateway describe-smb-file-shares --file-share-arn-list arn:aws:storagegateway:...
aws storagegateway describe-smb-settings --gateway-arn arn:aws:storagegateway:...
aws storagegateway join-domain \
  --gateway-arn arn:aws:storagegateway:... \
  --domain-name MYCOMPANY.COM \
  --user-name Admin \
  --password 'MyPassword'

# Trigger cache refresh (sync S3 changes to file share listing)
aws storagegateway refresh-cache \
  --gateway-arn arn:aws:storagegateway:... \
  --file-share-arn arn:aws:storagegateway:...

# --- Volume Gateway ---
aws storagegateway create-stored-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:... \
  --disk-id /dev/sdb \
  --preserve-existing-data \
  --target-name my-target \
  --network-interface-id 10.0.0.10

aws storagegateway create-cached-iscsi-volume \
  --gateway-arn arn:aws:storagegateway:... \
  --volume-size-in-bytes 107374182400 \
  --target-name my-cached-target \
  --network-interface-id 10.0.0.10 \
  --client-token token-789

aws storagegateway list-volumes --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-stored-iscsi-volumes --volume-arns arn:aws:storagegateway:...
aws storagegateway delete-volume --volume-arn arn:aws:storagegateway:...

# Create snapshot of gateway volume
aws storagegateway create-snapshot \
  --volume-arn arn:aws:storagegateway:... \
  --snapshot-description "Daily snapshot"

# --- Tape Gateway ---
aws storagegateway create-tapes \
  --gateway-arn arn:aws:storagegateway:... \
  --tape-size-in-bytes 107374182400 \
  --client-token token-tape \
  --num-tapes-to-create 2 \
  --tape-barcode-prefix MY

aws storagegateway list-tapes --gateway-arn arn:aws:storagegateway:...
aws storagegateway describe-tapes --tape-arns arn:aws:storagegateway:...
aws storagegateway retrieve-tape-archive \
  --tape-arn arn:aws:storagegateway:... \
  --gateway-arn arn:aws:storagegateway:...
aws storagegateway delete-tape --gateway-arn arn:aws:storagegateway:... \
  --tape-arn arn:aws:storagegateway:...

# --- Bandwidth settings ---
aws storagegateway update-bandwidth-rate-limit \
  --gateway-arn arn:aws:storagegateway:... \
  --average-upload-rate-limit-in-bits-per-sec 102400 \
  --average-download-rate-limit-in-bits-per-sec 204800
```

---

## Transfer Family

```bash
# --- Servers ---
aws transfer create-server \
  --protocols SFTP \
  --endpoint-type PUBLIC \
  --identity-provider-type SERVICE_MANAGED

# Private VPC endpoint (recommended for production)
aws transfer create-server \
  --protocols SFTP FTPS \
  --endpoint-type VPC \
  --endpoint-details VpcId=vpc-xxx,SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx \
  --identity-provider-type AWS_DIRECTORY_SERVICE \
  --directory-id d-xxxxxxxxxxxx \
  --certificate arn:aws:acm:us-east-1:123456789012:certificate/cert-id

aws transfer list-servers
aws transfer describe-server --server-id s-0123456789abcdef0
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --protocols SFTP FTPS FTPS

aws transfer start-server --server-id s-0123456789abcdef0
aws transfer stop-server --server-id s-0123456789abcdef0
aws transfer delete-server --server-id s-0123456789abcdef0

# --- Users ---
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --role arn:aws:iam::123456789012:role/TransferUserRole \
  --home-directory /my-bucket/users/alice \
  --home-directory-type PATH

# Logical home directory mapping (hide real bucket path from user)
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name bob \
  --role arn:aws:iam::123456789012:role/TransferUserRole \
  --home-directory-type LOGICAL \
  --home-directory-mappings Entry=/,Target=/my-bucket/users/bob

aws transfer list-users --server-id s-0123456789abcdef0
aws transfer describe-user --server-id s-0123456789abcdef0 --user-name alice
aws transfer update-user \
  --server-id s-0123456789abcdef0 --user-name alice \
  --policy file://scope-down-policy.json

aws transfer delete-user --server-id s-0123456789abcdef0 --user-name alice

# SSH public key management
aws transfer import-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-body "ssh-rsa AAAA..."

aws transfer list-users --server-id s-0123456789abcdef0 \
  --query 'Users[*].[UserName,HomeDirectory]' --output table

aws transfer delete-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-id key-0123456789abcdef0

# --- Workflows (post-upload processing) ---
aws transfer create-workflow \
  --steps file://workflow-steps.json \
  --description "Scan and tag uploads"

# Associate workflow with server
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --workflow-details \
  'OnUpload=[{WorkflowId=w-xxx,ExecutionRole=arn:aws:iam::123456789012:role/WorkflowRole}]'

aws transfer list-workflows
aws transfer describe-workflow --workflow-id w-0123456789abcdef0
aws transfer delete-workflow --workflow-id w-0123456789abcdef0

# --- Connectors (outbound SFTP / AS2) ---
aws transfer create-connector \
  --url sftp://partner.example.com \
  --sftp-config '{"UserSecretId":"arn:aws:secretsmanager:us-east-1:123456789012:secret:sftp-creds"}' \
  --access-role arn:aws:iam::123456789012:role/ConnectorRole

aws transfer create-connector \
  --url https://partner.example.com \
  --as2-config \
  'LocalProfileId=p-xxx,PartnerProfileId=p-yyy,MessageSubject=MyMessage,Compression=DISABLED,EncryptionAlgorithm=AES256_CBC,SigningAlgorithm=SHA256,MdnSigningAlgorithm=SHA256,MdnResponse=SYNC'

aws transfer list-connectors
aws transfer describe-connector --connector-id c-0123456789abcdef0
aws transfer delete-connector --connector-id c-0123456789abcdef0

# Start outbound file transfer via connector
aws transfer start-file-transfer \
  --connector-id c-0123456789abcdef0 \
  --send-file-paths /my-bucket/outbound/file.csv \
  --retrieve-file-paths /my-bucket/inbound/

# --- Certificates (for AS2 and FTPS) ---
aws transfer import-certificate \
  --usage SIGNING \
  --certificate file://cert.pem \
  --private-key file://private.pem \
  --certificate-chain file://chain.pem

aws transfer list-certificates
aws transfer describe-certificate --certificate-id cert-0123456789abcdef0
aws transfer delete-certificate --certificate-id cert-0123456789abcdef0
```
