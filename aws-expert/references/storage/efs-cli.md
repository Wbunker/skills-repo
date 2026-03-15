# AWS EFS — CLI Reference
For service concepts, see [efs-capabilities.md](efs-capabilities.md).

```bash
# --- File Systems ---
aws efs create-file-system \
  --performance-mode generalPurpose \
  --throughput-mode elastic \
  --encrypted \
  --kms-key-id alias/my-efs-key \
  --tags Key=Name,Value=my-efs

aws efs create-file-system \
  --performance-mode generalPurpose \
  --throughput-mode provisioned \
  --provisioned-throughput-in-mibps 100

aws efs describe-file-systems
aws efs describe-file-systems --file-system-id fs-0123456789abcdef0

# Update throughput mode (e.g., switch to elastic)
aws efs update-file-system \
  --file-system-id fs-0123456789abcdef0 \
  --throughput-mode elastic

aws efs delete-file-system --file-system-id fs-0123456789abcdef0

# --- Mount Targets ---
# Create one mount target per AZ for multi-AZ file systems
aws efs create-mount-target \
  --file-system-id fs-0123456789abcdef0 \
  --subnet-id subnet-0123456789abcdef0 \
  --security-groups sg-0123456789abcdef0

aws efs describe-mount-targets --file-system-id fs-0123456789abcdef0
aws efs describe-mount-target-security-groups --mount-target-id fsmt-0123456789abcdef0

aws efs modify-mount-target-security-groups \
  --mount-target-id fsmt-0123456789abcdef0 \
  --security-groups sg-new

aws efs delete-mount-target --mount-target-id fsmt-0123456789abcdef0

# --- Lifecycle Policy ---
aws efs put-lifecycle-configuration \
  --file-system-id fs-0123456789abcdef0 \
  --lifecycle-policies \
  '[{"TransitionToIA":"AFTER_30_DAYS"},{"TransitionToPrimaryStorageClass":"AFTER_1_ACCESS"}]'

aws efs describe-lifecycle-configuration --file-system-id fs-0123456789abcdef0

# --- Access Points ---
aws efs create-access-point \
  --file-system-id fs-0123456789abcdef0 \
  --posix-user Uid=1000,Gid=1000 \
  --root-directory \
  'Path=/app,CreationInfo={OwnerUid=1000,OwnerGid=1000,Permissions=755}'

aws efs describe-access-points
aws efs describe-access-points --file-system-id fs-0123456789abcdef0
aws efs delete-access-point --access-point-id fsap-0123456789abcdef0

# --- File System Policy (resource-based) ---
aws efs put-file-system-policy \
  --file-system-id fs-0123456789abcdef0 \
  --policy file://efs-policy.json

aws efs describe-file-system-policy --file-system-id fs-0123456789abcdef0

# --- Replication ---
aws efs create-replication-configuration \
  --source-file-system-id fs-source \
  --destinations '[{"Region":"us-west-2"}]'

aws efs describe-replication-configurations --file-system-id fs-source
aws efs delete-replication-configuration --source-file-system-id fs-source

# --- Backups ---
aws efs describe-backup-policy --file-system-id fs-0123456789abcdef0
aws efs put-backup-policy \
  --file-system-id fs-0123456789abcdef0 \
  --backup-policy Status=ENABLED
```
