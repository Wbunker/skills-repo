# Backup and DR — CLI Reference

Capabilities reference: [backup-dr-capabilities.md](backup-dr-capabilities.md)

This file covers three services:
1. **Backup and DR Service** — `gcloud backup-dr`
2. **Storage Transfer Service** — `gcloud transfer`
3. **Transfer Appliance** — primarily console-based; notes included

```bash
gcloud config set project my-project-id
```

---

## Backup and DR Service

### Management Servers

```bash
# Create a management server (required before using Backup and DR)
gcloud backup-dr management-servers create my-mgmt-server \
  --location=us-central1 \
  --network=projects/my-project/global/networks/my-vpc

# List management servers
gcloud backup-dr management-servers list --location=us-central1

# Describe a management server (shows UI endpoint, status)
gcloud backup-dr management-servers describe my-mgmt-server \
  --location=us-central1

# Get the management console URI for browser access
gcloud backup-dr management-servers describe my-mgmt-server \
  --location=us-central1 \
  --format="get(managementUri.webUi)"

# Delete a management server
gcloud backup-dr management-servers delete my-mgmt-server \
  --location=us-central1 \
  --quiet
```

### Backup Vaults

```bash
# Create a backup vault (WORM-capable, access-controlled backup repository)
gcloud backup-dr backup-vaults create my-backup-vault \
  --location=us-central1 \
  --backup-minimum-enforced-retention-duration=7d \
  --description="Production backup vault"

# Create a compliance vault with locked retention (WORM - irreversible!)
gcloud backup-dr backup-vaults create my-compliance-vault \
  --location=us-central1 \
  --backup-minimum-enforced-retention-duration=365d \
  --description="7-year compliance retention vault"

# List backup vaults
gcloud backup-dr backup-vaults list --location=us-central1

# Describe a backup vault
gcloud backup-dr backup-vaults describe my-backup-vault --location=us-central1

# Update vault description or retention
gcloud backup-dr backup-vaults update my-backup-vault \
  --location=us-central1 \
  --backup-minimum-enforced-retention-duration=30d

# Delete a backup vault (must be empty of backups)
gcloud backup-dr backup-vaults delete my-backup-vault \
  --location=us-central1 \
  --quiet
```

### Backup Plans

```bash
# Create a backup plan (defines schedule, retention, and vault)
gcloud backup-dr backup-plans create my-vm-backup-plan \
  --location=us-central1 \
  --resource-type=compute.googleapis.com/Instance \
  --backup-vault=my-backup-vault \
  --backup-rule-id=daily-7d,weekly-4w \
  --backup-rule-recurrence='FREQ=DAILY;BYHOUR=2' \
  --backup-rule-retention-days=7

# List backup plans
gcloud backup-dr backup-plans list --location=us-central1

# Describe a backup plan
gcloud backup-dr backup-plans describe my-vm-backup-plan --location=us-central1

# Delete a backup plan (must have no active associations)
gcloud backup-dr backup-plans delete my-vm-backup-plan \
  --location=us-central1 \
  --quiet
```

### Data Sources (Workloads)

```bash
# List data sources registered with Backup and DR
gcloud backup-dr data-sources list \
  --location=us-central1 \
  --backup-vault=my-backup-vault

# Describe a data source
gcloud backup-dr data-sources describe my-data-source \
  --location=us-central1 \
  --backup-vault=my-backup-vault

# Fetch data source from a specific workload
gcloud backup-dr data-sources fetch-access-token my-data-source \
  --location=us-central1 \
  --backup-vault=my-backup-vault
```

### Backup Plan Associations

```bash
# Associate a backup plan with a resource (e.g., a Compute Engine VM)
gcloud backup-dr backup-plan-associations create my-vm-association \
  --location=us-central1 \
  --resource=projects/my-project/zones/us-central1-a/instances/my-vm \
  --backup-plan=projects/my-project/locations/us-central1/backupPlans/my-vm-backup-plan

# List backup plan associations
gcloud backup-dr backup-plan-associations list --location=us-central1

# Describe an association
gcloud backup-dr backup-plan-associations describe my-vm-association \
  --location=us-central1

# Delete an association (stops future backups; does not delete existing backups)
gcloud backup-dr backup-plan-associations delete my-vm-association \
  --location=us-central1 \
  --quiet
```

### Backups (Recovery Points)

```bash
# List backups for a data source
gcloud backup-dr backups list \
  --location=us-central1 \
  --backup-vault=my-backup-vault \
  --data-source=my-data-source

# Describe a backup
gcloud backup-dr backups describe my-backup-20240115 \
  --location=us-central1 \
  --backup-vault=my-backup-vault \
  --data-source=my-data-source

# Restore from a backup (initiates restore job)
gcloud backup-dr backups restore my-backup-20240115 \
  --location=us-central1 \
  --backup-vault=my-backup-vault \
  --data-source=my-data-source \
  --target-resource=projects/my-project/zones/us-central1-a/instances/my-restored-vm

# Delete a specific backup (if not in a locked vault and past minimum retention)
gcloud backup-dr backups delete my-backup-20240101 \
  --location=us-central1 \
  --backup-vault=my-backup-vault \
  --data-source=my-data-source \
  --quiet
```

---

## Storage Transfer Service

### Create Transfer Jobs

```bash
# Create a one-time transfer from Amazon S3 to Cloud Storage
gcloud transfer jobs create \
  s3://my-aws-bucket gs://my-gcp-bucket \
  --name=s3-to-gcs-migration \
  --description="One-time migration from S3" \
  --source-creds-file=s3-credentials.json

# s3-credentials.json format:
# {
#   "access_key_id": "AKIAIOSFODNN7EXAMPLE",
#   "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
# }

# Create a scheduled daily sync from S3 to GCS
gcloud transfer jobs create \
  s3://my-aws-source-bucket gs://my-gcp-dest-bucket \
  --name=daily-s3-sync \
  --description="Daily sync from S3 to GCS" \
  --schedule-repeats-every=1d \
  --schedule-starts=2024-01-15T02:00:00Z \
  --source-creds-file=s3-credentials.json \
  --delete-from=source-after-transfer

# Create a transfer from Azure Blob Storage to GCS
gcloud transfer jobs create \
  azure://my-azure-container gs://my-gcp-bucket \
  --name=azure-to-gcs-migration \
  --source-creds-file=azure-credentials.json

# azure-credentials.json format:
# {
#   "sas_token": "sv=2021-04-10&ss=b&srt=co&sp=rwdlacuptfx&se=...&sig=..."
# }

# Create a GCS to GCS transfer job (cross-bucket or cross-region copy)
gcloud transfer jobs create \
  gs://my-source-bucket gs://my-dest-bucket \
  --name=gcs-to-gcs-copy \
  --description="Cross-region bucket copy" \
  --include-prefixes=data/2024/ \
  --schedule-starts=2024-01-15T00:00:00Z

# Create a one-time GCS to GCS with object filtering
gcloud transfer jobs create \
  gs://my-source-bucket gs://my-dest-bucket \
  --name=filtered-copy \
  --include-prefixes=logs/,reports/ \
  --exclude-prefixes=logs/debug/ \
  --object-conditions-last-modified-since=2024-01-01T00:00:00Z

# Create an on-premises to GCS transfer (requires agents)
gcloud transfer jobs create \
  posix:///mnt/data gs://my-gcp-bucket \
  --name=onprem-to-gcs \
  --source-agent-pool=my-agent-pool \
  --description="On-premises to GCS migration"
```

### Manage Transfer Jobs

```bash
# List all transfer jobs
gcloud transfer jobs list

# List jobs with format
gcloud transfer jobs list \
  --format="table(name,transferSpec.gcsDataSource.bucketName,status.state,latestOperationName)"

# Describe a transfer job
gcloud transfer jobs describe daily-s3-sync

# Run a job immediately (ad-hoc execution)
gcloud transfer jobs run daily-s3-sync

# Pause a scheduled job
gcloud transfer jobs update daily-s3-sync --status=disabled

# Resume a paused job
gcloud transfer jobs update daily-s3-sync --status=enabled

# Update job description
gcloud transfer jobs update daily-s3-sync \
  --description="Updated daily sync from S3 to GCS"

# Delete a transfer job
gcloud transfer jobs delete daily-s3-sync --quiet
```

### Monitor Transfer Operations

```bash
# List recent operations for a job
gcloud transfer operations list --job-names=daily-s3-sync

# Describe a specific operation (shows progress, bytes transferred)
gcloud transfer operations describe OPERATION_NAME

# List operations with status
gcloud transfer operations list \
  --filter="status.state=IN_PROGRESS" \
  --format="table(name,transferJobName,status.state,counters.objectsFoundFromSource)"

# Pause an in-progress operation
gcloud transfer operations pause OPERATION_NAME

# Resume a paused operation
gcloud transfer operations resume OPERATION_NAME

# Cancel an in-progress operation
gcloud transfer operations cancel OPERATION_NAME
```

### On-Premises Transfer Agents

```bash
# Create an agent pool (prerequisite for on-prem transfers)
gcloud transfer agent-pools create my-agent-pool \
  --display-name="On-prem datacenter agents" \
  --bandwidth-limit=500  # 500 MB/s per agent

# List agent pools
gcloud transfer agent-pools list

# Describe an agent pool
gcloud transfer agent-pools describe my-agent-pool

# Install agents (run on each on-prem server — requires Docker)
# Get the agent installation command:
gcloud transfer agent-pools get-agent-env-vars my-agent-pool

# Typical agent install command (Docker):
# docker run --ulimit memlock=64000000 --detach --rm \
#   -v /transfer_root:/transfer_root \
#   gcr.io/cloud-ingest/tsop-agent:latest \
#   --project-id=my-project \
#   --agent-pool=projects/my-project/agentPools/my-agent-pool \
#   --hostname-prefix=agent-$(hostname)

# Update agent pool bandwidth limit
gcloud transfer agent-pools update my-agent-pool \
  --bandwidth-limit=1000  # MB/s

# Delete an agent pool (agents must be stopped first)
gcloud transfer agent-pools delete my-agent-pool --quiet
```

---

## Example: Complete S3-to-GCS Migration Job

```bash
# Step 1: Create destination bucket
gcloud storage buckets create gs://my-migration-dest \
  --location=us-central1 \
  --uniform-bucket-level-access

# Step 2: Grant Transfer Service SA access to destination bucket
PROJECT_NUMBER=$(gcloud projects describe my-project --format="get(projectNumber)")
gcloud storage buckets add-iam-policy-binding gs://my-migration-dest \
  --member=serviceAccount:project-${PROJECT_NUMBER}@storage-transfer-service.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin

# Step 3: Create S3 credentials file
cat > s3-creds.json << 'EOF'
{
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
EOF

# Step 4: Create and run the transfer job
gcloud transfer jobs create \
  s3://my-source-s3-bucket gs://my-migration-dest \
  --name=s3-full-migration \
  --description="Full migration from S3 to GCS" \
  --source-creds-file=s3-creds.json

# Step 5: Run the job immediately
gcloud transfer jobs run s3-full-migration

# Step 6: Monitor progress
watch -n 30 'gcloud transfer operations list \
  --job-names=s3-full-migration \
  --format="table(status.state,counters.objectsFoundFromSource,counters.objectsCopiedToSink,counters.bytesFoundFromSource,counters.bytesCopiedToSink)"'
```

---

## Transfer Appliance (Process Overview)

Transfer Appliance ordering and management is primarily done through the Google Cloud Console. The CLI does not have direct appliance management commands.

**Process:**
1. Navigate to **Cloud Console > Storage > Transfer Appliance**.
2. Click **Order Appliance**, specify model (TA100 or TA480), shipping address, destination bucket.
3. Google ships the appliance (5-10 business days).
4. Rack and connect the appliance to your network.
5. Access the appliance management UI via browser (appliance has its own web server).
6. Copy data using NFS mount or the appliance's copy utility:
   ```bash
   # Mount the appliance NFS share
   sudo mount -t nfs APPLIANCE_IP:/transfer /mnt/appliance

   # Copy data to the appliance
   rsync -avP --checksum /data/large-dataset/ /mnt/appliance/dataset/
   ```
7. When copy is complete, mark the transfer complete in the Cloud Console.
8. Ship appliance back to Google using pre-paid shipping label.
9. Google ingests data (typically 2-5 days after receipt) and notifies you.
10. Verify data in Cloud Storage:
    ```bash
    gcloud storage ls --recursive gs://my-destination-bucket/ | wc -l
    gcloud storage du -sh gs://my-destination-bucket/
    ```
