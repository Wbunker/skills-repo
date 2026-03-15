# AWS Data Transfer — CLI Reference

For service concepts, see [data-transfer-capabilities.md](data-transfer-capabilities.md).

---

## aws datasync — DataSync

### Agents

```bash
# List all agents
aws datasync list-agents

# Describe a specific agent
aws datasync describe-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0

# Activate an agent (after deploying the VM; get activation key from VM local UI)
aws datasync create-agent \
  --activation-key "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE" \
  --agent-name "on-prem-agent-dc1" \
  --tags '[{"Key": "Site", "Value": "Datacenter1"}]' \
  --vpc-endpoint-id vpce-0123456789abcdef0 \
  --subnet-arns '["arn:aws:ec2:us-east-1:123456789012:subnet/subnet-0123456789abcdef0"]' \
  --security-group-arns '["arn:aws:ec2:us-east-1:123456789012:security-group/sg-0123456789abcdef0"]'

# Update agent name
aws datasync update-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0 \
  --name "on-prem-agent-dc1-renamed"

# Delete an agent
aws datasync delete-agent \
  --agent-arn arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0
```

### Locations — NFS

```bash
# Create an NFS location (on-premises NFS share)
aws datasync create-location-nfs \
  --server-hostname 192.168.1.100 \
  --subdirectory /exports/data \
  --on-prem-config '{"AgentArns": ["arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0"]}' \
  --mount-options '{"Version": "NFS4_1"}'

# Describe an NFS location
aws datasync describe-location-nfs \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0

# Update an NFS location
aws datasync update-location-nfs \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-0123456789abcdef0 \
  --subdirectory /exports/data-updated
```

### Locations — SMB

```bash
# Create an SMB location (Windows file share)
aws datasync create-location-smb \
  --server-hostname 192.168.1.101 \
  --subdirectory /share/data \
  --user svc-datasync \
  --domain CORP \
  --password "MySharePass123" \
  --agent-arns '["arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0"]' \
  --mount-options '{"Version": "SMB3"}'

# Describe an SMB location
aws datasync describe-location-smb \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-smb-0123456789
```

### Locations — Amazon S3

```bash
# Create an S3 location
aws datasync create-location-s3 \
  --s3-bucket-arn arn:aws:s3:::my-datasync-target \
  --subdirectory /migration-data \
  --s3-config '{"BucketAccessRoleArn": "arn:aws:iam::123456789012:role/DataSync-S3-Role"}' \
  --s3-storage-class STANDARD

# Create an S3 location with Intelligent-Tiering
aws datasync create-location-s3 \
  --s3-bucket-arn arn:aws:s3:::my-datasync-archive \
  --subdirectory /archive \
  --s3-config '{"BucketAccessRoleArn": "arn:aws:iam::123456789012:role/DataSync-S3-Role"}' \
  --s3-storage-class INTELLIGENT_TIERING

# Describe an S3 location
aws datasync describe-location-s3 \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-s3-0123456789
```

### Locations — Amazon EFS

```bash
# Create an EFS location
aws datasync create-location-efs \
  --efs-filesystem-arn arn:aws:elasticfilesystem:us-east-1:123456789012:file-system/fs-0123456789abcdef0 \
  --ec2-config '{"SubnetArn": "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-0123456789abcdef0", "SecurityGroupArns": ["arn:aws:ec2:us-east-1:123456789012:security-group/sg-0123456789abcdef0"]}' \
  --subdirectory /

# Describe an EFS location
aws datasync describe-location-efs \
  --location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-efs-0123456789
```

### Locations — Amazon FSx

```bash
# Create an FSx for Windows File Server location
aws datasync create-location-fsx-windows \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-0123456789abcdef0 \
  --security-group-arns '["arn:aws:ec2:us-east-1:123456789012:security-group/sg-0123456789abcdef0"]' \
  --subdirectory /share \
  --domain CORP \
  --user svc-datasync \
  --password "FsxPass123"

# Create an FSx for Lustre location
aws datasync create-location-fsx-lustre \
  --fsx-filesystem-arn arn:aws:fsx:us-east-1:123456789012:file-system/fs-lustre-0123456789 \
  --security-group-arns '["arn:aws:ec2:us-east-1:123456789012:security-group/sg-0123456789abcdef0"]' \
  --subdirectory /

# Create an FSx for ONTAP location
aws datasync create-location-fsx-ontap \
  --storage-virtual-machine-arn arn:aws:fsx:us-east-1:123456789012:storage-virtual-machine/svm-0123456789abcdef0 \
  --security-group-arns '["arn:aws:ec2:us-east-1:123456789012:security-group/sg-0123456789abcdef0"]' \
  --subdirectory / \
  --protocol '{"NFS": {"MountOptions": {"Version": "NFS4_1"}}}'
```

### Locations — HDFS

```bash
# Create an HDFS location
aws datasync create-location-hdfs \
  --name-nodes '[{"Hostname": "namenode1.internal", "Port": 8020}]' \
  --block-size 134217728 \
  --replication-factor 3 \
  --subdirectory /user/migration \
  --authentication-type KERBEROS \
  --kerberos-principal "datasync@INTERNAL.EXAMPLE.COM" \
  --kerberos-keytab fileb://datasync.keytab \
  --kerberos-krb5-conf fileb://krb5.conf \
  --agent-arns '["arn:aws:datasync:us-east-1:123456789012:agent/agent-0123456789abcdef0"]'
```

### Tasks

```bash
# List all tasks
aws datasync list-tasks

# Describe a task
aws datasync describe-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Create a task (NFS source to S3 destination)
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-nfs-0123456789 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-s3-0123456789 \
  --name "on-prem-nfs-to-s3" \
  --cloud-watch-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/datasync/task \
  --options '{"VerifyMode": "ONLY_FILES_TRANSFERRED", "OverwriteMode": "ALWAYS", "Atime": "BEST_EFFORT", "Mtime": "PRESERVE", "Uid": "NONE", "Gid": "NONE", "PreserveDeletedFiles": "PRESERVE", "PreserveDevices": "NONE", "PosixPermissions": "NONE", "BytesPerSecond": -1, "TaskQueueing": "ENABLED", "LogLevel": "TRANSFER", "TransferMode": "CHANGED"}' \
  --schedule '{"ScheduleExpression": "cron(0 2 * * ? *)"}' \
  --tags '[{"Key": "Project", "Value": "Migration2024"}]'

# Update a task (change bandwidth throttle)
aws datasync update-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --options '{"BytesPerSecond": 104857600}'

# Delete a task
aws datasync delete-task \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0
```

### Task Executions

```bash
# Start a task execution (manual run)
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Start with override options (transfer all files this run only)
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0 \
  --override-options '{"TransferMode": "ALL", "BytesPerSecond": -1}'

# List task executions for a task
aws datasync list-task-executions \
  --task-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0

# Describe a task execution (check status, bytes transferred)
aws datasync describe-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0

# Cancel a running task execution
aws datasync cancel-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0

# Update execution bandwidth throttle while running
aws datasync update-task-execution \
  --task-execution-arn arn:aws:datasync:us-east-1:123456789012:task/task-0123456789abcdef0/execution/exec-0123456789abcdef0 \
  --options '{"BytesPerSecond": 52428800}'
```

### Filters

```bash
# Create a task with include/exclude filters
aws datasync create-task \
  --source-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-nfs-0123456789 \
  --destination-location-arn arn:aws:datasync:us-east-1:123456789012:location/loc-s3-0123456789 \
  --name "filtered-task" \
  --includes '[{"FilterType": "SIMPLE_PATTERN", "Value": "*.csv|*.parquet"}]' \
  --excludes '[{"FilterType": "SIMPLE_PATTERN", "Value": "*.tmp|*.log"}]'
```

---

## aws snowball — Snow Family

### Jobs

```bash
# List all Snow jobs
aws snowball list-jobs

# Describe a specific job
aws snowball describe-job \
  --job-id JID-0123456789abcdef0

# Create a Snowball Edge import job (transfer data TO AWS)
aws snowball create-job \
  --job-type IMPORT \
  --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::my-snowball-target", "KeyRange": {}}]}' \
  --description "Datacenter migration - batch 1" \
  --address-id ADID-0123456789abcdef0 \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --role-arn arn:aws:iam::123456789012:role/Snowball-Import-Role \
  --snowball-capacity-preference T80 \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --shipping-option SECOND_DAY

# Create a Snowball Edge export job (transfer data FROM AWS)
aws snowball create-job \
  --job-type EXPORT \
  --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::my-export-bucket", "KeyRange": {"BeginMarker": "", "EndMarker": ""}}]}' \
  --description "Export dataset for field deployment" \
  --address-id ADID-0123456789abcdef0 \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --role-arn arn:aws:iam::123456789012:role/Snowball-Export-Role \
  --snowball-type EDGE_COMPUTE_OPTIMIZED \
  --shipping-option SECOND_DAY

# Create a Snowball Edge local compute job (no data transfer, just edge compute)
aws snowball create-job \
  --job-type LOCAL_USE \
  --description "Edge compute deployment - remote site" \
  --address-id ADID-0123456789abcdef0 \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --snowball-type EDGE_COMPUTE_OPTIMIZED \
  --shipping-option SECOND_DAY

# Cancel a job (only possible in WithCustomer or New state)
aws snowball cancel-job \
  --job-id JID-0123456789abcdef0

# Describe job list (more detail than list-jobs)
aws snowball describe-jobs \
  --job-ids '["JID-0123456789abcdef0", "JID-abcdef0123456789"]'
```

### Addresses

```bash
# List shipping addresses
aws snowball list-cluster-jobs

# Create a shipping address
aws snowball create-address \
  --address '{
    "Name": "John Smith",
    "Company": "Example Corp",
    "Street1": "123 Main Street",
    "City": "Seattle",
    "StateOrProvince": "WA",
    "PostalCode": "98101",
    "Country": "US",
    "PhoneNumber": "206-555-1234",
    "IsRestricted": false
  }'

# Describe a shipping address
aws snowball describe-address \
  --address-id ADID-0123456789abcdef0

# List all addresses
aws snowball describe-addresses
```

### Manifest & Unlock Code

```bash
# Get the job manifest (download to use with Snowball client)
aws snowball get-job-manifest \
  --job-id JID-0123456789abcdef0
# Returns a presigned URL; download with curl

# Get the unlock code (used with OpsHub or Snowball client to unlock device)
aws snowball get-job-unlock-code \
  --job-id JID-0123456789abcdef0
```

### Clusters (Snowball Edge clustering)

```bash
# Create a cluster job (5-10 Snowball Edge devices)
aws snowball create-cluster \
  --job-type IMPORT \
  --resources '{"S3Resources": [{"BucketArn": "arn:aws:s3:::my-cluster-target"}]}' \
  --description "10-device cluster migration" \
  --address-id ADID-0123456789abcdef0 \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --role-arn arn:aws:iam::123456789012:role/Snowball-Import-Role \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --shipping-option SECOND_DAY \
  --on-device-service-configuration '{"NFSOnDeviceService": {"StorageLimit": 0, "StorageUnit": "TB"}}'

# List cluster jobs
aws snowball list-cluster-jobs \
  --cluster-id CID-0123456789abcdef0

# Describe a cluster
aws snowball describe-cluster \
  --cluster-id CID-0123456789abcdef0

# Update a cluster (add resources before cluster is In Use)
aws snowball update-cluster \
  --cluster-id CID-0123456789abcdef0 \
  --description "Updated cluster description"

# Cancel a cluster
aws snowball cancel-cluster \
  --cluster-id CID-0123456789abcdef0
```

### Long-Term Pricing

```bash
# List long-term pricing options
aws snowball list-long-term-pricing

# Get details on a long-term pricing entry
aws snowball get-long-term-pricing \
  --long-term-pricing-id LTP-0123456789abcdef0

# Create a long-term pricing entry (1-year or 3-year)
aws snowball create-long-term-pricing \
  --long-term-pricing-type ONE_YEAR \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --is-long-term-pricing-auto-renew true

# Update a long-term pricing entry (assign to a job)
aws snowball update-long-term-pricing \
  --long-term-pricing-id LTP-0123456789abcdef0 \
  --replacement-job JID-0123456789abcdef0
```

---

## aws transfer — Transfer Family

### Servers

```bash
# List all Transfer Family servers
aws transfer list-servers

# Describe a server
aws transfer describe-server \
  --server-id s-0123456789abcdef0

# Create an SFTP server (Service Managed, VPC internal)
aws transfer create-server \
  --protocols SFTP \
  --identity-provider-type SERVICE_MANAGED \
  --endpoint-type VPC \
  --endpoint-details '{"VpcId": "vpc-0123456789abcdef0", "SubnetIds": ["subnet-0123456789abcdef0"], "SecurityGroupIds": ["sg-0123456789abcdef0"]}' \
  --logging-role arn:aws:iam::123456789012:role/TransferFamily-Logging-Role \
  --tags '[{"Key": "Name", "Value": "sftp-prod"}]'

# Create a public SFTP server
aws transfer create-server \
  --protocols SFTP \
  --identity-provider-type SERVICE_MANAGED \
  --endpoint-type PUBLIC \
  --logging-role arn:aws:iam::123456789012:role/TransferFamily-Logging-Role

# Create an SFTP/FTPS multi-protocol server with custom Lambda identity provider
aws transfer create-server \
  --protocols SFTP FTPS \
  --identity-provider-type API_GATEWAY \
  --identity-provider-details '{"Url": "https://api-id.execute-api.us-east-1.amazonaws.com/prod", "InvocationRole": "arn:aws:iam::123456789012:role/TransferFamily-IdP-Role"}' \
  --endpoint-type VPC \
  --endpoint-details '{"VpcId": "vpc-0123456789abcdef0", "SubnetIds": ["subnet-0123456789abcdef0"], "SecurityGroupIds": ["sg-0123456789abcdef0"]}' \
  --certificate arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --logging-role arn:aws:iam::123456789012:role/TransferFamily-Logging-Role

# Create an AS2 server
aws transfer create-server \
  --protocols AS2 \
  --endpoint-type VPC \
  --endpoint-details '{"VpcId": "vpc-0123456789abcdef0", "SubnetIds": ["subnet-0123456789abcdef0"], "SecurityGroupIds": ["sg-0123456789abcdef0"]}'

# Update a server (e.g., update security policy)
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --security-policy-name TransferSecurityPolicy-2024-01

# Start a stopped server
aws transfer start-server \
  --server-id s-0123456789abcdef0

# Stop a server
aws transfer stop-server \
  --server-id s-0123456789abcdef0

# Delete a server
aws transfer delete-server \
  --server-id s-0123456789abcdef0
```

### Users

```bash
# List users for a server
aws transfer list-users \
  --server-id s-0123456789abcdef0

# Describe a user
aws transfer describe-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice

# Create a user (S3 home directory)
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --home-directory /my-sftp-bucket/alice \
  --home-directory-type PATH \
  --role arn:aws:iam::123456789012:role/TransferFamily-User-Role

# Create a user with logical home directory mapping (hides S3 bucket structure)
aws transfer create-user \
  --server-id s-0123456789abcdef0 \
  --user-name bob \
  --home-directory /my-sftp-bucket \
  --home-directory-type LOGICAL \
  --home-directory-mappings '[{"Entry": "/", "Target": "/my-sftp-bucket/bob"}]' \
  --role arn:aws:iam::123456789012:role/TransferFamily-User-Role

# Update a user (change IAM role or home directory)
aws transfer update-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --role arn:aws:iam::123456789012:role/TransferFamily-User-Role-New

# Delete a user
aws transfer delete-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice
```

### SSH Keys (SFTP)

```bash
# Import an SSH public key for a user
aws transfer import-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-body "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... alice@laptop"

# List SSH public keys for a user
aws transfer describe-user \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --query 'User.SshPublicKeys'

# Delete an SSH public key
aws transfer delete-ssh-public-key \
  --server-id s-0123456789abcdef0 \
  --user-name alice \
  --ssh-public-key-id key-0123456789abcdef0
```

### Workflows (Post-Upload Processing)

```bash
# List workflows
aws transfer list-workflows

# Describe a workflow
aws transfer describe-workflow \
  --workflow-id w-0123456789abcdef0

# Create a workflow (copy then tag then delete original = move)
aws transfer create-workflow \
  --description "Copy, tag, then delete original" \
  --steps '[
    {
      "Type": "COPY",
      "CopyStepDetails": {
        "Name": "CopyToProcessed",
        "DestinationFileLocation": {
          "S3FileLocation": {
            "Bucket": "my-processed-bucket",
            "Key": "${transfer:UserName}/${transfer:UploadDate}/${transfer:FilePath}"
          }
        },
        "OverwriteExisting": "FALSE"
      }
    },
    {
      "Type": "TAG",
      "TagStepDetails": {
        "Name": "TagWithUploader",
        "Tags": [{"Key": "UploadedBy", "Value": "${transfer:UserName}"}]
      }
    },
    {
      "Type": "DELETE",
      "DeleteStepDetails": {
        "Name": "DeleteOriginal",
        "SourceFileLocation": "${original.file}"
      }
    }
  ]'

# Associate a workflow with a server
aws transfer update-server \
  --server-id s-0123456789abcdef0 \
  --workflow-details '{"OnUpload": [{"WorkflowId": "w-0123456789abcdef0", "ExecutionRole": "arn:aws:iam::123456789012:role/TransferFamily-Workflow-Role"}]}'

# Delete a workflow
aws transfer delete-workflow \
  --workflow-id w-0123456789abcdef0
```

### Connectors (SFTP & AS2 Outbound)

```bash
# List connectors
aws transfer list-connectors

# Describe a connector
aws transfer describe-connector \
  --connector-id c-0123456789abcdef0

# Create an SFTP connector (send files to external SFTP server)
aws transfer create-connector \
  --url "sftp://partner-sftp.example.com" \
  --sftp-config '{"UserSecretId": "arn:aws:secretsmanager:us-east-1:123456789012:secret:transfer/sftp-partner-key", "TrustedHostKeys": ["partner-sftp.example.com ssh-rsa AAAAB3NzaC1yc2E..."]}' \
  --access-role arn:aws:iam::123456789012:role/TransferFamily-Connector-Role \
  --logging-role arn:aws:iam::123456789012:role/TransferFamily-Logging-Role

# Create an AS2 connector (send AS2 messages to trading partner)
aws transfer create-connector \
  --url "https://partner-as2.example.com/as2" \
  --as2-config '{
    "LocalProfileId": "p-0123456789abcdef0",
    "PartnerProfileId": "p-abcdef0123456789",
    "MessageSubject": "EDI Order",
    "Compression": "ZLIB",
    "EncryptionAlgorithm": "AES256_CBC",
    "SigningAlgorithm": "SHA256",
    "MdnSigningAlgorithm": "SHA256",
    "MdnResponse": "SYNC"
  }' \
  --access-role arn:aws:iam::123456789012:role/TransferFamily-Connector-Role

# Send a file using an SFTP or AS2 connector
aws transfer start-file-transfer \
  --connector-id c-0123456789abcdef0 \
  --send-file-paths '["s3://my-sftp-bucket/outbound/invoice.xml"]' \
  --remote-directory-path /inbound

# Delete a connector
aws transfer delete-connector \
  --connector-id c-0123456789abcdef0
```

### Certificates & Profiles (AS2)

```bash
# Import a certificate (AS2 signing/encryption)
aws transfer import-certificate \
  --usage SIGNING \
  --certificate file://my-cert.pem \
  --private-key file://my-private-key.pem \
  --certificate-chain file://ca-chain.pem

# List certificates
aws transfer list-certificates

# Describe a certificate
aws transfer describe-certificate \
  --certificate-id cert-0123456789abcdef0

# Delete a certificate
aws transfer delete-certificate \
  --certificate-id cert-0123456789abcdef0

# Create a local AS2 profile (your identity)
aws transfer create-profile \
  --as2-id "MY-COMPANY-AS2-ID" \
  --profile-type LOCAL \
  --certificate-ids '["cert-0123456789abcdef0"]'

# Create a partner AS2 profile
aws transfer create-profile \
  --as2-id "PARTNER-COMPANY-AS2-ID" \
  --profile-type PARTNER \
  --certificate-ids '["cert-partner-0123456789"]'

# List profiles
aws transfer list-profiles

# Create an AS2 agreement (inbound)
aws transfer create-agreement \
  --server-id s-0123456789abcdef0 \
  --local-profile-id p-0123456789abcdef0 \
  --partner-profile-id p-abcdef0123456789 \
  --base-directory /my-sftp-bucket/as2-inbound \
  --access-role arn:aws:iam::123456789012:role/TransferFamily-AS2-Role

# List agreements
aws transfer list-agreements \
  --server-id s-0123456789abcdef0

# Delete an agreement
aws transfer delete-agreement \
  --server-id s-0123456789abcdef0 \
  --agreement-id a-0123456789abcdef0
```
