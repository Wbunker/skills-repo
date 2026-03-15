# Data Transfer — CLI Reference

## Storage Transfer Service

### Create transfer jobs

```bash
# One-time transfer from Amazon S3 to Cloud Storage
gcloud transfer jobs create \
  s3://my-aws-bucket \
  gs://my-gcs-bucket \
  --source-creds-file=aws-creds.json \
  --project=my-project \
  --job-type=FILES \
  --description="One-time S3 to GCS migration"

# Scheduled recurring transfer (daily at 02:00 UTC)
gcloud transfer jobs create \
  s3://my-aws-bucket/exports/ \
  gs://my-gcs-bucket/imports/ \
  --source-creds-file=aws-creds.json \
  --schedule-starts=2025-01-01T02:00:00Z \
  --schedule-repeats-every=24h \
  --project=my-project \
  --description="Daily S3 sync"

# Transfer from Azure Blob Storage to GCS
gcloud transfer jobs create \
  https://myaccount.blob.core.windows.net/mycontainer \
  gs://my-gcs-bucket \
  --source-creds-file=azure-creds.json \
  --project=my-project

# Transfer with include/exclude prefixes
gcloud transfer jobs create \
  gs://source-bucket \
  gs://destination-bucket \
  --include-prefixes=data/2024/,data/2025/ \
  --exclude-prefixes=data/2024/temp/ \
  --project=my-project

# Transfer with modification time filter (only objects modified after date)
gcloud transfer jobs create \
  s3://my-aws-bucket \
  gs://my-gcs-bucket \
  --source-creds-file=aws-creds.json \
  --last-modified-since=2024-01-01T00:00:00Z \
  --project=my-project

# Transfer from on-premises POSIX filesystem (requires agents)
gcloud transfer jobs create \
  posix:///mnt/nas/data \
  gs://my-gcs-bucket/nas-data/ \
  --source-agent-pool=my-onprem-agent-pool \
  --project=my-project

# Transfer GCS to GCS with delete-unmatched (sync behavior)
gcloud transfer jobs create \
  gs://source-bucket \
  gs://replica-bucket \
  --delete-from=destination-if-unique \
  --project=my-project
```

### AWS credentials file format (for S3 transfers)
```json
{
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

### Manage transfer jobs

```bash
# List transfer jobs
gcloud transfer jobs list --project=my-project \
  --format="table(name,description,status,lastModificationTime)"

# Describe a job (shows schedule, source, destination, config)
gcloud transfer jobs describe JOB_NAME --project=my-project

# Run a job immediately (one-off execution outside schedule)
gcloud transfer jobs run JOB_NAME --project=my-project

# Update a job (change schedule, description)
gcloud transfer jobs update JOB_NAME \
  --description="Updated description" \
  --project=my-project

# Pause a scheduled job
gcloud transfer jobs update JOB_NAME \
  --status=disabled \
  --project=my-project

# Re-enable a paused job
gcloud transfer jobs update JOB_NAME \
  --status=enabled \
  --project=my-project

# Delete a transfer job
gcloud transfer jobs delete JOB_NAME --project=my-project

# List operations (individual runs) for a job
gcloud transfer operations list \
  --job-name=JOB_NAME \
  --project=my-project \
  --format="table(name,status,counters.objectsFoundFromSource,counters.bytesFoundFromSource)"

# Describe a specific operation
gcloud transfer operations describe OPERATION_NAME --project=my-project

# Pause a running operation
gcloud transfer operations pause OPERATION_NAME --project=my-project

# Resume a paused operation
gcloud transfer operations resume OPERATION_NAME --project=my-project
```

### Install Transfer Service agents (for on-premises)

```bash
# Create an agent pool for on-premises agents
gcloud transfer agent-pools create my-onprem-agent-pool \
  --project=my-project \
  --display-name="On-premises NAS agents"

# Install agent on an on-premises Linux host (requires Docker)
gcloud transfer agents install \
  --pool=my-onprem-agent-pool \
  --count=4 \
  --project=my-project
# This generates and runs docker run commands for Transfer Service agents

# List agent pools
gcloud transfer agent-pools list --project=my-project

# Describe an agent pool
gcloud transfer agent-pools describe my-onprem-agent-pool --project=my-project
```

---

## BigQuery Data Transfer Service

```bash
# List available data sources
gcloud bigquery data-transfers list-configs \
  --location=us \
  --project=my-project

# List available data source types
gcloud bigquery data-transfers list-data-sources \
  --location=us \
  --project=my-project \
  --format="table(dataSourceId,displayName)"

# Create a Google Ads transfer
gcloud bigquery data-transfers create \
  --data-source=google_ads \
  --location=us \
  --target-dataset=google_ads_data \
  --display-name="Google Ads Daily Import" \
  --schedule="every 24 hours" \
  --params='{"customer_id":"123-456-7890","table_filter":"ALL"}' \
  --project=my-project

# Create an Amazon S3 transfer to BigQuery
gcloud bigquery data-transfers create \
  --data-source=amazon_s3 \
  --location=us \
  --target-dataset=s3_imports \
  --display-name="S3 Daily Import" \
  --schedule="every 24 hours" \
  --params='{"destination_table_name_template":"my_table_{run_time|\"%Y%m%d\"}","data_path_template":"s3://my-bucket/data/*.parquet","access_key_id":"AKIAIOSFODNN7EXAMPLE","secret_access_key":"SECRET","file_format":"PARQUET"}' \
  --project=my-project

# Create a BigQuery cross-region dataset copy
gcloud bigquery data-transfers create \
  --data-source=cross_region_copy \
  --location=eu \
  --target-dataset=us_data_replica \
  --display-name="US to EU BQ copy" \
  --schedule="every 24 hours" \
  --params='{"source_project_id":"my-source-project","source_dataset_id":"my_dataset","overwrite_destination_table":true}' \
  --project=my-eu-project

# List all transfer configurations
gcloud bigquery data-transfers list-configs \
  --location=us \
  --project=my-project \
  --format="table(name,displayName,dataSourceId,nextRunTime,state)"

# Describe a transfer config
gcloud bigquery data-transfers describe TRANSFER_CONFIG_NAME \
  --location=us \
  --project=my-project

# Update a transfer config
gcloud bigquery data-transfers update TRANSFER_CONFIG_NAME \
  --location=us \
  --display-name="Updated display name" \
  --project=my-project

# Delete a transfer config
gcloud bigquery data-transfers delete TRANSFER_CONFIG_NAME \
  --location=us \
  --project=my-project

# Trigger an immediate transfer run
gcloud bigquery data-transfers run TRANSFER_CONFIG_NAME \
  --location=us \
  --project=my-project

# List transfer runs (history of executions)
gcloud bigquery data-transfers runs list TRANSFER_CONFIG_NAME \
  --location=us \
  --project=my-project \
  --format="table(name,runTime,state,errorStatus)"

# Backfill: schedule runs for a historical date range
gcloud bigquery data-transfers schedule-runs TRANSFER_CONFIG_NAME \
  --location=us \
  --start-time=2024-01-01T00:00:00Z \
  --end-time=2024-03-31T23:59:59Z \
  --project=my-project

# View logs for a specific run
gcloud bigquery data-transfers runs list TRANSFER_CONFIG_NAME \
  --location=us \
  --project=my-project \
  --format="value(name)" | head -1 | \
  xargs -I {} gcloud bigquery data-transfers runs describe {} \
  --location=us --project=my-project
```

---

## Cloud Storage rsync (gcloud storage)

```bash
# Upload a local directory to GCS (incremental; skips unchanged files)
gcloud storage rsync /local/data/ gs://my-bucket/data/ --recursive

# Download from GCS to local
gcloud storage rsync gs://my-bucket/data/ /local/data/ --recursive

# Sync between two GCS buckets
gcloud storage rsync gs://source-bucket/ gs://destination-bucket/ --recursive

# Mirror sync: delete destination objects not in source
gcloud storage rsync gs://source-bucket/ gs://destination-bucket/ \
  --recursive \
  --delete-unmatched-destination-objects

# Dry run: preview without making changes
gcloud storage rsync gs://source-bucket/ gs://destination-bucket/ \
  --recursive \
  --dry-run

# Exclude patterns (regex)
gcloud storage rsync /local/data/ gs://my-bucket/ \
  --recursive \
  --exclude=".*\.tmp$|.*\.log$|.*/\.git/.*"

# Include only specific patterns (exclusive with --exclude)
gcloud storage rsync /local/data/ gs://my-bucket/ \
  --recursive \
  --include=".*\.parquet$|.*\.csv$"

# Limit parallelism (useful for rate limiting)
gcloud storage rsync gs://source/ gs://dest/ \
  --recursive \
  --transfers=10

# Check what would be transferred
gcloud storage rsync gs://source-bucket/ gs://dest-bucket/ \
  --recursive \
  --dry-run \
  2>&1 | grep "Would copy"
```

---

## Transfer Appliance

Transfer Appliance is primarily ordered and managed through the Cloud Console, but the following CLI commands are available:

```bash
# List Transfer Appliance jobs
gcloud transfer appliances jobs list --project=my-project

# Describe a Transfer Appliance job (shows shipping status, capacity, etc.)
gcloud transfer appliances jobs describe JOB_NAME --project=my-project

# Note: appliance ordering, key management, and finalization
# are performed via the Cloud Console (Storage > Transfer Appliances)
# or the Storage Transfer API directly
```

---

## Datastream (for CDC replication)

```bash
# See database/database-migration-cli.md for full Datastream CLI reference
# Quick reference for data transfer context:

# List Datastream streams (ongoing CDC replication jobs)
gcloud datastream streams list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName,state,backfillStrategy)"

# Start a stream
gcloud datastream streams update my-stream \
  --location=us-central1 \
  --state=RUNNING \
  --project=my-project

# Pause a stream
gcloud datastream streams update my-stream \
  --location=us-central1 \
  --state=PAUSED \
  --project=my-project
```
