# AWS EBS — CLI Reference
For service concepts, see [ebs-capabilities.md](ebs-capabilities.md).

EBS volume and snapshot management uses `aws ec2` commands. The `aws ebs` commands are for the EBS Direct API (read/write snapshot blocks directly).

```bash
# --- Volumes ---
aws ec2 create-volume \
  --availability-zone us-east-1a \
  --volume-type gp3 \
  --size 100 \
  --iops 6000 \
  --throughput 250 \
  --encrypted \
  --kms-key-id alias/my-ebs-key

aws ec2 create-volume \
  --availability-zone us-east-1a \
  --snapshot-id snap-0123456789abcdef0 \
  --volume-type io2 \
  --iops 10000

aws ec2 describe-volumes
aws ec2 describe-volumes --volume-ids vol-0123456789abcdef0
aws ec2 describe-volumes \
  --filters Name=status,Values=available Name=availability-zone,Values=us-east-1a

# Attach and detach
aws ec2 attach-volume \
  --volume-id vol-0123456789abcdef0 \
  --instance-id i-0123456789abcdef0 \
  --device /dev/sdf

aws ec2 detach-volume --volume-id vol-0123456789abcdef0
aws ec2 detach-volume --volume-id vol-0123456789abcdef0 --force

# Modify volume (Elastic Volumes — no downtime required)
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --volume-type gp3 \
  --iops 10000 \
  --throughput 500

aws ec2 describe-volumes-modifications --volume-ids vol-0123456789abcdef0

aws ec2 delete-volume --volume-id vol-0123456789abcdef0

# --- Snapshots ---
aws ec2 create-snapshot \
  --volume-id vol-0123456789abcdef0 \
  --description "Daily backup" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=daily-backup}]'

aws ec2 describe-snapshots --owner-ids self
aws ec2 describe-snapshots --snapshot-ids snap-0123456789abcdef0
aws ec2 describe-snapshots \
  --filters Name=volume-id,Values=vol-0123456789abcdef0 \
  --query 'Snapshots[*].[SnapshotId,StartTime,State]' --output table

aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id snap-0123456789abcdef0 \
  --description "Cross-region copy" \
  --encrypted --kms-key-id alias/my-key \
  --region us-west-2

aws ec2 delete-snapshot --snapshot-id snap-0123456789abcdef0

# Share snapshot with another account
aws ec2 modify-snapshot-attribute \
  --snapshot-id snap-0123456789abcdef0 \
  --attribute createVolumePermission \
  --operation-type add \
  --user-ids 987654321098

# Fast Snapshot Restore (FSR)
aws ec2 enable-fast-snapshot-restores \
  --availability-zones us-east-1a us-east-1b \
  --source-snapshot-ids snap-0123456789abcdef0

aws ec2 disable-fast-snapshot-restores \
  --availability-zones us-east-1a \
  --source-snapshot-ids snap-0123456789abcdef0

aws ec2 describe-fast-snapshot-restores

# Snapshot Archive
aws ec2 archive-snapshot --snapshot-id snap-0123456789abcdef0
aws ec2 restore-snapshot-from-recycle-bin --snapshot-id snap-0123456789abcdef0

# --- Data Lifecycle Manager (DLM) ---
aws dlm create-lifecycle-policy \
  --description "Daily EBS snapshots" \
  --state ENABLED \
  --execution-role-arn arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole \
  --policy-details file://dlm-policy.json

aws dlm get-lifecycle-policies
aws dlm get-lifecycle-policy --policy-id policy-0123456789abcdef0
aws dlm update-lifecycle-policy --policy-id policy-0123456789abcdef0 --state DISABLED
aws dlm delete-lifecycle-policy --policy-id policy-0123456789abcdef0

# --- EBS Direct API (aws ebs) — snapshot block-level access ---
# List all blocks in a snapshot
aws ebs list-snapshot-blocks --snapshot-id snap-0123456789abcdef0

# List blocks that changed between two snapshots
aws ebs list-changed-blocks \
  --first-snapshot-id snap-aaa \
  --second-snapshot-id snap-bbb

# Read a specific block from a snapshot
aws ebs get-snapshot-block \
  --snapshot-id snap-0123456789abcdef0 \
  --block-index 0 \
  --block-token <token-from-list-snapshot-blocks> \
  /tmp/block.bin

# Create snapshot from scratch (programmatic)
SNAPSHOT_ID=$(aws ebs start-snapshot --volume-size 1 --query SnapshotId --output text)
aws ebs put-snapshot-block \
  --snapshot-id "$SNAPSHOT_ID" \
  --block-index 0 \
  --block-token $(openssl rand -base64 32) \
  --data-length 524288 \
  --checksum $(openssl dgst -sha256 -binary /tmp/block.bin | base64) \
  --checksum-algorithm SHA256 \
  --body /tmp/block.bin
aws ebs complete-snapshot --snapshot-id "$SNAPSHOT_ID" --changed-blocks-count 1
```
