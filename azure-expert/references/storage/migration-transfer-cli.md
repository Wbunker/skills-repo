# Azure Storage Migration & Transfer — CLI Reference
For service concepts, see [migration-transfer-capabilities.md](migration-transfer-capabilities.md).

## AzCopy Commands

```bash
# ============================================================
# AUTHENTICATION
# ============================================================

# Login with Managed Identity (system-assigned; recommended for Azure compute)
azcopy login --identity

# Login with User-Assigned Managed Identity
azcopy login --identity \
  --identity-client-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Login with Service Principal (client secret)
azcopy login \
  --service-principal \
  --application-id <app-id> \
  --tenant-id <tenant-id>
# Set AZCOPY_SPA_CLIENT_SECRET env var with the secret

# Interactive login (Entra ID; dev/test)
azcopy login

# Logout
azcopy logout

# ============================================================
# COPY — UPLOAD (local → Azure)
# ============================================================

# Upload single file
azcopy copy './data/file.csv' \
  'https://account.blob.core.windows.net/container/data/file.csv'

# Upload directory recursively
azcopy copy './data/' \
  'https://account.blob.core.windows.net/container/data/' \
  --recursive

# Upload with glob pattern
azcopy copy './logs/*.log' \
  'https://account.blob.core.windows.net/container/logs/'

# Upload and set blob tier
azcopy copy './archive/' \
  'https://account.blob.core.windows.net/container/archive/' \
  --recursive \
  --block-blob-tier Archive        # Hot | Cool | Cold | Archive

# Upload with MD5 verification
azcopy copy './data/file.bin' \
  'https://account.blob.core.windows.net/container/file.bin' \
  --put-md5 \
  --check-md5 FailIfDifferent

# Upload with bandwidth cap (MiB/s)
azcopy copy './data/' \
  'https://account.blob.core.windows.net/container/' \
  --recursive \
  --cap-mbps 100

# ============================================================
# COPY — DOWNLOAD (Azure → local)
# ============================================================

# Download single blob
azcopy copy \
  'https://account.blob.core.windows.net/container/data/file.csv' \
  './downloads/file.csv'

# Download entire container
azcopy copy \
  'https://account.blob.core.windows.net/container/' \
  './local-copy/' \
  --recursive

# Download with pattern filter
azcopy copy \
  'https://account.blob.core.windows.net/container/' \
  './local-copy/' \
  --recursive \
  --include-pattern "*.parquet"

# ============================================================
# COPY — SERVER-SIDE (Azure → Azure; no local bandwidth)
# ============================================================

# Blob to Blob (same account, different container)
azcopy copy \
  'https://account.blob.core.windows.net/src-container/file.txt' \
  'https://account.blob.core.windows.net/dst-container/file.txt'

# Container to container (cross-account; SAS on both)
azcopy copy \
  'https://src.blob.core.windows.net/src-container?<src-sas>' \
  'https://dst.blob.core.windows.net/dst-container?<dst-sas>' \
  --recursive

# S3 to Azure Blob (cross-cloud migration)
azcopy copy \
  'https://s3.amazonaws.com/my-bucket/' \
  'https://account.blob.core.windows.net/container/?<sas>' \
  --recursive \
  --s2s-preserve-access-tier false

# ============================================================
# SYNC (incremental transfer)
# ============================================================

# Sync local directory to blob container (upload only changes)
azcopy sync './data/' \
  'https://account.blob.core.windows.net/container/' \
  --recursive

# Sync and delete destination items not in source
azcopy sync './data/' \
  'https://account.blob.core.windows.net/container/' \
  --recursive \
  --delete-destination true

# Sync blob to blob (cross-account)
azcopy sync \
  'https://src.blob.core.windows.net/container/?<sas>' \
  'https://dst.blob.core.windows.net/container/?<sas>' \
  --recursive

# Sync with modified-time comparison (default: size+lmt)
azcopy sync './data/' \
  'https://account.blob.core.windows.net/container/' \
  --compare-hash MD5

# ============================================================
# LIST AND JOB MANAGEMENT
# ============================================================

# List blobs in container
azcopy list 'https://account.blob.core.windows.net/container/?<sas>'

# List with machine-readable output
azcopy list 'https://account.blob.core.windows.net/container/' \
  --output-type json

# List all jobs
azcopy jobs list

# Show job details and progress
azcopy jobs show <job-id>

# Resume failed/interrupted job
azcopy jobs resume <job-id>

# Clean up completed job plan files
azcopy jobs clean

# Benchmark upload throughput
azcopy bench 'https://account.blob.core.windows.net/container/?<sas>' \
  --file-count 100 \
  --size-per-file 8M

# ============================================================
# ENVIRONMENT VARIABLES (AzCopy tuning)
# ============================================================
# AZCOPY_CONCURRENCY_VALUE     — number of concurrent goroutines (default: auto)
# AZCOPY_BUFFER_GB             — total buffer memory in GB for transfers
# AZCOPY_LOG_LOCATION          — override default log directory
# AZCOPY_JOB_PLAN_LOCATION     — override default job plan directory
# AZCOPY_AUTO_LOGIN_TYPE       — AZCLI | MSI | SPN | DEVICE for auto-auth
```

---

## Azure Import/Export Service

```bash
# --- Register Import/Export Provider ---
az provider register --namespace Microsoft.ImportExport

# --- Create Import Job ---
az import-export create \
  --name myImportJob \
  --resource-group myRG \
  --location eastus \
  --type Import \
  --log-level Verbose \
  --storage-account mystorageaccount \
  --return-address '{
    "recipientName": "IT Team",
    "streetAddress1": "1 Microsoft Way",
    "city": "Redmond",
    "stateOrProvince": "WA",
    "postalCode": "98052",
    "countryOrRegion": "US",
    "phone": "425-555-0100",
    "email": "itteam@contoso.com"
  }' \
  --drive-list '[
    {
      "driveId": "ABCDE12345",
      "bitLockerKey": "<bitlocker-key>",
      "manifestFile": "\\\\DRIVE\\dataset1.manifest.xml",
      "manifestHash": "<sha256-hash>",
      "driveHeaderHash": ""
    }
  ]'

# --- Create Export Job ---
az import-export create \
  --name myExportJob \
  --resource-group myRG \
  --location eastus \
  --type Export \
  --storage-account mystorageaccount \
  --export '{
    "blobList": {
      "blobPaths": ["container/path/to/blob1", "container/path/to/blob2"],
      "blobPathPrefixes": ["container/archive/"]
    }
  }' \
  --return-address '{
    "recipientName": "IT Team",
    "streetAddress1": "1 Microsoft Way",
    "city": "Redmond",
    "stateOrProvince": "WA",
    "postalCode": "98052",
    "countryOrRegion": "US",
    "phone": "425-555-0100",
    "email": "itteam@contoso.com"
  }'

# --- List Jobs ---
az import-export list \
  --resource-group myRG \
  --output table

# --- Show Job Status ---
az import-export show \
  --name myImportJob \
  --resource-group myRG

# --- Update Shipping Info (after dropping off drive) ---
az import-export update \
  --name myImportJob \
  --resource-group myRG \
  --carrier-name FedEx \
  --tracking-number 123456789012 \
  --return-carrier FedEx

# --- Delete Completed Job ---
az import-export delete \
  --name myImportJob \
  --resource-group myRG

# --- List Import/Export Locations (datacenters accepting drives) ---
az import-export location list --output table
```

---

## Data Box (Portal/PowerShell focused; key CLI operations)

```bash
# Data Box management is primarily via Azure Portal and PowerShell (Az.DataBox module)
# Some operations available via az databox (preview extension)

# Install databox extension
az extension add --name databox

# --- List Data Box Jobs ---
az databox job list \
  --resource-group myRG \
  --output table

# --- Show Data Box Job ---
az databox job show \
  --name myDataBoxJob \
  --resource-group myRG

# --- List Available SKUs ---
az databox job list-available-skus \
  --location eastus \
  --transfer-type ImportToAzure \
  --country US \
  --output table

# --- Create Data Box Job ---
az databox job create \
  --name myDataBoxJob \
  --resource-group myRG \
  --location eastus \
  --sku DataBox \
  --contact-details '{
    "contactName": "IT Admin",
    "emailList": ["admin@contoso.com"],
    "phone": "425-555-0100"
  }' \
  --shipping-address '{
    "streetAddress1": "1 Microsoft Way",
    "city": "Redmond",
    "stateOrProvince": "WA",
    "country": "US",
    "postalCode": "98052"
  }' \
  --storage-account-details '[{
    "storageAccountId": "/subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/mystorageaccount",
    "dataAccountType": "StorageAccount",
    "sharePassword": ""
  }]'

# --- Cancel Data Box Job ---
az databox job cancel \
  --name myDataBoxJob \
  --resource-group myRG \
  --reason "Migration complete via alternative method"

# --- Delete Data Box Job ---
az databox job delete \
  --name myDataBoxJob \
  --resource-group myRG --yes
```
