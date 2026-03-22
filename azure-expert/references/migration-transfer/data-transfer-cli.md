# Data Transfer — CLI Reference
For service concepts, see [data-transfer-capabilities.md](data-transfer-capabilities.md).

## Azure Data Box

```bash
# --- Data Box Jobs ---
az databox job create \
  --resource-group myRG \
  --name myDataBoxJob \
  --location eastus \
  --sku DataBox \
  --contact-details contact-name="Jane Smith" phone="+15551234567" email-list="jane@company.com" \
  --shipping-address street-address1="123 Main St" city="Seattle" state-or-province="WA" country="US" postal-code="98101" \
  --storage-account-details storage-account-id=/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorage  # Order Data Box device

az databox job create \
  --resource-group myRG \
  --name myDiskJob \
  --location eastus \
  --sku DataBoxDisk \
  --contact-details contact-name="Jane Smith" phone="+15551234567" email-list="jane@company.com" \
  --shipping-address street-address1="123 Main St" city="Seattle" state-or-province="WA" country="US" postal-code="98101" \
  --storage-account-details storage-account-id=/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorage  # Order Data Box Disk

az databox job list --resource-group myRG      # List all Data Box jobs
az databox job show \
  --resource-group myRG \
  --name myDataBoxJob                          # Show job status and shipping info

az databox job list-credentials \
  --resource-group myRG \
  --name myDataBoxJob                          # Get device unlock passcode and share credentials

az databox job cancel \
  --resource-group myRG \
  --name myDataBoxJob \
  --reason "Wrong destination storage account"  # Cancel a job before device ships

az databox job delete \
  --resource-group myRG \
  --name myDataBoxJob --yes                    # Delete completed job record
```

## Azure Import/Export

```bash
# --- Import/Export Jobs ---
az import-export create \
  --resource-group myRG \
  --name myImportJob \
  --location eastus \
  --type Import \
  --log-level Verbose \
  --backup-drive-manifest true \
  --storage-account myStorageAccount \
  --drive-list drive-id=ABC123 bit-locker-key=ABC123-DEF456... manifest-file=myfile.manifest manifest-hash=<hash>  # Create import job

az import-export list --resource-group myRG    # List import/export jobs
az import-export show \
  --resource-group myRG \
  --name myImportJob                           # Show job details and status

az import-export update \
  --resource-group myRG \
  --name myImportJob \
  --delivery-package carrier-name=UPS tracking-number=1Z999AA10123456784  # Update with shipping tracking number

az import-export delete \
  --resource-group myRG \
  --name myImportJob --yes                     # Delete job

# --- List supported locations ---
az import-export location list                 # Show supported datacenter locations
az import-export location show --name eastus  # Show details for a location
```

## AzCopy

```bash
# --- Authentication ---
azcopy login                                   # Interactive browser login
azcopy login --tenant-id <tenantId>           # Login to specific tenant
azcopy login --identity                        # Managed identity (from Azure resource)
azcopy login --identity --identity-client-id <clientId>  # User-assigned managed identity
azcopy logout

# --- Copy Operations ---
# Upload local file to blob
azcopy copy '/local/data/file.csv' \
  'https://myaccount.blob.core.windows.net/mycontainer/file.csv?<SAS>'

# Upload folder to blob container (recursive)
azcopy copy '/local/data/*' \
  'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' \
  --recursive

# Upload to ADLS Gen2 (use dfs endpoint)
azcopy copy '/local/data/*' \
  'https://myaccount.dfs.core.windows.net/myfilesystem/folder?<SAS>' \
  --recursive

# Download from blob to local
azcopy copy \
  'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' \
  '/local/download' \
  --recursive

# Server-side copy between storage accounts (no data through client)
azcopy copy \
  'https://source.blob.core.windows.net/container?<SAS-source>' \
  'https://dest.blob.core.windows.net/container?<SAS-dest>' \
  --recursive

# Copy from S3 to Azure Blob
azcopy copy \
  'https://s3.amazonaws.com/mybucket?<AWS-SAS>' \
  'https://myaccount.blob.core.windows.net/mycontainer?<Azure-SAS>' \
  --recursive

# --- Sync Operations (incremental) ---
azcopy sync '/local/data' \
  'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' \
  --recursive                                  # Sync: copy new/changed only

azcopy sync '/local/data' \
  'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' \
  --recursive \
  --delete-destination true                    # Sync: also delete files not in source

azcopy sync \
  'https://source.blob.core.windows.net/container?<SAS>' \
  'https://dest.blob.core.windows.net/container?<SAS>' \
  --recursive                                  # Sync between storage accounts

# --- Performance Options ---
azcopy copy '/local/data/*' 'https://...' \
  --recursive \
  --cap-mbps 100 \
  --block-size-mb 256 \
  --put-md5                                   # Cap bandwidth; large block size; store MD5

# Set concurrency via environment variable
export AZCOPY_CONCURRENCY_VALUE=512
azcopy copy '/local/data/*' 'https://...' --recursive

# --- Filtering ---
azcopy copy '/local/data/*' 'https://...' \
  --include-pattern "*.csv;*.parquet" \
  --recursive                                  # Only copy CSV and Parquet files

azcopy copy 'https://source/container?<SAS>' '/local/dest' \
  --include-after "2024-01-01T00:00:00Z" \
  --recursive                                  # Only files modified after date

azcopy copy '/local/data/*' 'https://...' \
  --exclude-path "logs;temp" \
  --recursive                                  # Exclude specific paths

# --- Archive/Blob Tier ---
azcopy copy '/local/archive/*' \
  'https://myaccount.blob.core.windows.net/cold-storage?<SAS>' \
  --recursive \
  --blob-type BlockBlob \
  --block-blob-tier Archive                    # Upload directly to Archive tier

# --- List and Remove ---
azcopy list 'https://myaccount.blob.core.windows.net/mycontainer?<SAS>'  # List blobs
azcopy remove 'https://myaccount.blob.core.windows.net/mycontainer/old-data?<SAS>' --recursive  # Delete

# --- Benchmark ---
azcopy benchmark 'https://myaccount.blob.core.windows.net/bench?<SAS>'  # Test upload throughput

# --- Job Management ---
azcopy jobs list                               # List all AzCopy jobs
azcopy jobs show <job-id>                      # Show job status
azcopy jobs resume <job-id>                    # Resume interrupted job
azcopy jobs clean                              # Clean up completed job logs
```

## Azure Storage Mover

```bash
# Install extension
az extension add --name storage-mover

# --- Storage Mover ---
az storage-mover create \
  --resource-group myRG \
  --name myStorageMover \
  --location eastus \
  --description "NFS to Azure Blob migration"  # Create storage mover

az storage-mover list --resource-group myRG    # List storage movers

# --- Agents ---
az storage-mover agent register \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --name myAgent \
  --arc-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.HybridCompute/machines/myAgentVM  # Register agent VM

az storage-mover agent list \
  --resource-group myRG \
  --storage-mover-name myStorageMover          # List registered agents

# --- Source Endpoints ---
az storage-mover endpoint create-for-nfs \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --name source-nfs \
  --host "10.0.0.100" \
  --export "/data/files"                       # NFS source endpoint

az storage-mover endpoint create-for-smb \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --name source-smb \
  --host "fileserver.company.local" \
  --share-name "data"                          # SMB source endpoint

# --- Target Endpoints ---
az storage-mover endpoint create-for-storage-container \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --name target-blob \
  --storage-account-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorage \
  --blob-container-name migration-data         # Azure Blob target endpoint

# --- Projects and Jobs ---
az storage-mover project create \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --name myMigrationProject                    # Create migration project

az storage-mover job-definition create \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --project-name myMigrationProject \
  --name nfs-to-blob-job \
  --source-name source-nfs \
  --target-name target-blob \
  --agent-name myAgent \
  --copy-mode Additive                         # Create job definition (Additive or Mirror)

az storage-mover job-run start \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --project-name myMigrationProject \
  --job-definition-name nfs-to-blob-job        # Start a migration job run

az storage-mover job-run list \
  --resource-group myRG \
  --storage-mover-name myStorageMover \
  --project-name myMigrationProject \
  --job-definition-name nfs-to-blob-job        # List job runs (history)
```
