# AWS Backup & DataSync — CLI Reference

For service concepts, see [backup-datasync-capabilities.md](backup-datasync-capabilities.md).

## AWS Backup

```bash
# --- Backup Plans ---
aws backup create-backup-plan --backup-plan file://backup-plan.json

# Example backup plan (daily backup, 35-day retention, copy to us-west-2)
cat > backup-plan.json <<'EOF'
{
  "BackupPlan": {
    "BackupPlanName": "daily-backup-plan",
    "Rules": [{
      "RuleName": "daily-rule",
      "TargetBackupVaultName": "default",
      "ScheduleExpression": "cron(0 5 ? * * *)",
      "StartWindowMinutes": 60,
      "CompletionWindowMinutes": 180,
      "Lifecycle": {"DeleteAfterDays": 35},
      "CopyActions": [{
        "DestinationBackupVaultArn": "arn:aws:backup:us-west-2:123456789012:backup-vault:default",
        "Lifecycle": {"DeleteAfterDays": 90}
      }]
    }]
  }
}
EOF

aws backup list-backup-plans
aws backup get-backup-plan --backup-plan-id plan-0123456789abcdef0
aws backup update-backup-plan \
  --backup-plan-id plan-0123456789abcdef0 \
  --backup-plan file://updated-plan.json
aws backup delete-backup-plan --backup-plan-id plan-0123456789abcdef0

# --- Resource Assignments (what gets backed up) ---
aws backup create-backup-selection \
  --backup-plan-id plan-0123456789abcdef0 \
  --backup-selection file://selection.json

# Example: all resources tagged env=prod
cat > selection.json <<'EOF'
{
  "SelectionName": "prod-resources",
  "IamRoleArn": "arn:aws:iam::123456789012:role/AWSBackupDefaultServiceRole",
  "ListOfTags": [{"ConditionType": "STRINGEQUALS", "ConditionKey": "env", "ConditionValue": "prod"}]
}
EOF

aws backup list-backup-selections --backup-plan-id plan-0123456789abcdef0
aws backup delete-backup-selection \
  --backup-plan-id plan-0123456789abcdef0 \
  --selection-id sel-0123456789abcdef0

# --- Backup Vaults ---
aws backup create-backup-vault \
  --backup-vault-name my-vault \
  --encryption-key-arn arn:aws:kms:us-east-1:123456789012:key/key-id

aws backup list-backup-vaults
aws backup describe-backup-vault --backup-vault-name my-vault
aws backup delete-backup-vault --backup-vault-name my-vault

# Vault Lock (WORM — prevents deletion)
aws backup put-backup-vault-lock-configuration \
  --backup-vault-name my-vault \
  --min-retention-days 7 \
  --max-retention-days 365

# Vault access policy
aws backup put-backup-vault-access-policy \
  --backup-vault-name my-vault \
  --policy file://vault-policy.json

# --- On-Demand Backup Jobs ---
aws backup start-backup-job \
  --backup-vault-name my-vault \
  --resource-arn arn:aws:ec2:us-east-1:123456789012:instance/i-0123456789abcdef0 \
  --iam-role-arn arn:aws:iam::123456789012:role/AWSBackupDefaultServiceRole \
  --start-window-minutes 60 \
  --lifecycle DeleteAfterDays=30

aws backup list-backup-jobs
aws backup list-backup-jobs --by-state RUNNING
aws backup describe-backup-job --backup-job-id job-0123456789abcdef0
aws backup stop-backup-job --backup-job-id job-0123456789abcdef0

# --- Recovery Points ---
aws backup list-recovery-points-by-backup-vault --backup-vault-name my-vault
aws backup describe-recovery-point \
  --backup-vault-name my-vault \
  --recovery-point-arn arn:aws:backup:us-east-1:123456789012:recovery-point:rp-xxx

aws backup delete-recovery-point \
  --backup-vault-name my-vault \
  --recovery-point-arn arn:aws:backup:us-east-1:123456789012:recovery-point:rp-xxx

# --- Restore ---
aws backup start-restore-job \
  --recovery-point-arn arn:aws:backup:us-east-1:123456789012:recovery-point:rp-xxx \
  --iam-role-arn arn:aws:iam::123456789012:role/AWSBackupDefaultServiceRole \
  --metadata file://restore-metadata.json

aws backup list-restore-jobs
aws backup describe-restore-job --restore-job-id restore-0123456789abcdef0

# --- Legal Hold ---
aws backup create-legal-hold \
  --title "Legal hold for investigation" \
  --description "Hold backup data for audit" \
  --recovery-point-selection file://rp-selection.json

aws backup list-legal-holds
aws backup cancel-legal-hold \
  --legal-hold-id hold-0123456789abcdef0 \
  --cancel-description "Investigation complete"

# --- Cross-account copy ---
# (Requires AWS Organizations; add cross-account policy to destination vault)
aws backup put-backup-vault-access-policy \
  --backup-vault-name destination-vault \
  --policy file://cross-account-vault-policy.json
```

---

## DataSync

```bash
# --- Agents ---
# Deploy agent as VM on-premises or as EC2, then activate with the endpoint IP
aws datasync create-agent \
  --activation-key <key-from-agent-UI> \
  --agent-name my-datacenter-agent \
  --tags Key=env,Value=prod

aws datasync list-agents
aws datasync describe-agent --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-xxx
aws datasync delete-agent --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-xxx

# --- Locations ---

# NFS server (on-premises)
aws datasync create-location-nfs \
  --server-hostname nfs.mycompany.com \
  --subdirectory /exports/data \
  --on-prem-config AgentArns=arn:aws:datasync:us-east-1:123456789012:agent/agent-xxx

# SMB server (on-premises)
aws datasync create-location-smb \
  --server-hostname smb.mycompany.com \
  --subdirectory '/share/data' \
  --user transferuser \
  --password 'MyPassword' \
  --domain MYCOMPANY \
  --agent-arns arn:aws:datasync:us-east-1:123456789012:agent/agent-xxx

# Amazon S3
aws datasync create-location-s3 \
  --s3-bucket-arn arn:aws:s3:::my-bucket \
  --subdirectory /prefix \
  --s3-config BucketAccessRoleArn=arn:aws:iam::123456789012:role/DataSyncS3Role \
  --s3-storage-class STANDARD

# Amazon EFS
aws datasync create-location-efs \
  --efs-filesystem-arn arn:aws:elasticfilesystem:us-east-1:123456789012:file-system/fs-xxx \
  --ec2-config SubnetArn=arn:aws:ec2:us-east-1:123456789012:subnet/subnet-xxx,SecurityGroupArns=arn:aws:ec2:us-east-1:123456789012:security-group/sg-xxx

# FSx for Windows
aws datasync create-location-fsx-windows \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-xxx \
  --security-group-arns arn:aws:ec2:us-east-1:123456789012:security-group/sg-xxx \
  --user Admin \
  --password 'MyPassword' \
  --domain MYCOMPANY

# FSx for OpenZFS
aws datasync create-location-fsx-open-zfs \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-xxx \
  --security-group-arns arn:aws:ec2:us-east-1:123456789012:security-group/sg-xxx \
  --protocol '{"NFS":{"MountOptions":{"Version":"NFS4_1"}}}'

aws datasync list-locations
aws datasync describe-location-s3 --location-arn arn:aws:datasync:...
aws datasync delete-location --location-arn arn:aws:datasync:...

# --- Tasks ---
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-src \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-dst \
  --name my-migration-task \
  --options \
  'VerifyMode=ONLY_FILES_TRANSFERRED,OverwriteMode=ALWAYS,PreserveDeletedFiles=REMOVE,LogLevel=TRANSFER' \
  --schedule ScheduleExpression="cron(0 2 ? * MON-FRI *)"

aws datasync list-tasks
aws datasync describe-task --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx

aws datasync update-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx \
  --schedule ScheduleExpression="cron(0 0 * * ? *)"

aws datasync delete-task --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx

# --- Task Executions ---
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx

# Start with overridden options (e.g., dry run check)
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx \
  --override-options 'VerifyMode=ONLY_FILES_TRANSFERRED,LogLevel=TRANSFER'

aws datasync list-task-executions --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx
aws datasync describe-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx/execution/exec-xxx

aws datasync cancel-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-xxx/execution/exec-xxx
```

---

## AWS Elastic Disaster Recovery (DRS)

```bash
# --- Initialization (run once per Region) ---
aws drs initialize-service

# --- Replication Configuration (applied before agent install) ---
aws drs get-replication-configuration \
  --source-server-id s-0123456789abcdef0

aws drs update-replication-configuration \
  --source-server-id s-0123456789abcdef0 \
  --replication-servers-security-groups-i-ds sg-0123456789abcdef0 \
  --replication-subnet-id subnet-0123456789abcdef0 \
  --ebs-encryption EBS_DEFAULT \
  --default-large-staging-disk-type GP3 \
  --pit-policy '[
    {"enabled": true, "interval": 10, "retentionDuration": 60, "ruleID": 1, "units": "MINUTE"},
    {"enabled": true, "interval": 1,  "retentionDuration": 24, "ruleID": 2, "units": "HOUR"},
    {"enabled": true, "interval": 1,  "retentionDuration": 3,  "ruleID": 3, "units": "DAY"}
  ]'

# --- Source Servers ---
# List all source servers and their replication state
aws drs describe-source-servers \
  --filters '{"isArchived": false}'

# Disconnect a source server from replication
aws drs disconnect-source-server \
  --source-server-id s-0123456789abcdef0

# --- Launch Settings (configure before drill/recovery) ---
aws drs get-launch-configuration \
  --source-server-id s-0123456789abcdef0

aws drs update-launch-configuration \
  --source-server-id s-0123456789abcdef0 \
  --launch-disposition STARTED \
  --target-instance-type-right-sizing-method BASIC \
  --copy-private-ip \
  --copy-tags

# --- Drill / Recovery ---
# Launch recovery instances (drill or actual recovery)
aws drs start-recovery \
  --source-servers '[
    {"sourceServerID": "s-0123456789abcdef0", "recoverySnapshotID": "pit-latest"}
  ]' \
  --is-drill true

# Launch from a specific point-in-time snapshot
aws drs start-recovery \
  --source-servers '[
    {"sourceServerID": "s-0123456789abcdef0", "recoverySnapshotID": "snap-0123456789abcdef0"}
  ]' \
  --is-drill false

# Describe recovery instances
aws drs describe-recovery-instances

# Terminate drill/recovery instances after testing
aws drs terminate-recovery-instances \
  --recovery-instance-i-ds i-0123456789abcdef0

# --- Failback ---
# Reverse replication: start replicating data back from AWS to original site
aws drs reverse-replication \
  --recovery-instance-id i-0123456789abcdef0

# Get failback replication configuration
aws drs get-failback-replication-configuration \
  --recovery-instance-id i-0123456789abcdef0

# Launch failback to original or alternate source
aws drs start-failback-launch \
  --recovery-instance-i-ds i-0123456789abcdef0 \
  --tags Key=purpose,Value=failback

# Stop failback when complete
aws drs stop-failback \
  --recovery-instance-id i-0123456789abcdef0

# --- Jobs and Monitoring ---
aws drs describe-jobs
aws drs describe-jobs \
  --filters 'fromDate=2025-01-01T00:00:00Z,toDate=2025-12-31T23:59:59Z'

aws drs describe-job-log-items \
  --job-id drsjob-0123456789abcdef0
```
