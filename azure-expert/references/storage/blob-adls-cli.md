# Azure Blob Storage & ADLS Gen2 — CLI Reference
For service concepts, see [blob-adls-capabilities.md](blob-adls-capabilities.md).

## Storage Account Management

```bash
# --- Create Storage Account ---
az storage account create \
  --name mystorageaccount \
  --resource-group myRG \
  --location eastus \
  --sku Standard_RAGZRS \           # LRS | ZRS | GRS | GZRS | RAGRS | RAGZRS
  --kind StorageV2 \                # StorageV2 (recommended) | BlobStorage | BlockBlobStorage | FileStorage
  --access-tier Hot \               # Hot (default) | Cool
  --enable-hierarchical-namespace true \  # Enable ADLS Gen2
  --https-only true \               # Enforce HTTPS
  --allow-shared-key-access false \ # Disable Shared Key; enforce Entra ID
  --min-tls-version TLS1_2

# Create Premium Block Blob account (low-latency blob workloads)
az storage account create \
  --name mypremiumblob \
  --resource-group myRG \
  --location eastus \
  --sku Premium_LRS \
  --kind BlockBlobStorage

# --- Show / List ---
az storage account show --name mystorageaccount --resource-group myRG
az storage account list --resource-group myRG --output table
az storage account list-keys --name mystorageaccount --resource-group myRG

# --- Update Account Settings ---
az storage account update \
  --name mystorageaccount \
  --resource-group myRG \
  --sku Standard_RAGZRS             # Change redundancy tier

az storage account update \
  --name mystorageaccount \
  --resource-group myRG \
  --set kind=StorageV2              # Upgrade GPv1 to GPv2

# Enable soft delete for blobs and containers
az storage account blob-service-properties update \
  --account-name mystorageaccount \
  --resource-group myRG \
  --enable-delete-retention true \
  --delete-retention-days 14 \
  --enable-container-delete-retention true \
  --container-delete-retention-days 7

# Enable versioning and change feed
az storage account blob-service-properties update \
  --account-name mystorageaccount \
  --resource-group myRG \
  --enable-versioning true \
  --enable-change-feed true \
  --change-feed-retention-days 30

# Enable last access time tracking (required for lifecycle last-access rules)
az storage account blob-service-properties update \
  --account-name mystorageaccount \
  --resource-group myRG \
  --enable-last-access-tracking true

# --- Delete ---
az storage account delete --name mystorageaccount --resource-group myRG --yes

# --- Firewall / Network Rules ---
# Restrict to specific VNet subnet
az storage account network-rule add \
  --account-name mystorageaccount \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet

# Allow specific IP range
az storage account network-rule add \
  --account-name mystorageaccount \
  --resource-group myRG \
  --ip-address 203.0.113.0/24

# Set default action to Deny (enforce firewall)
az storage account update \
  --name mystorageaccount \
  --resource-group myRG \
  --default-action Deny
```

---

## Container Operations

```bash
# Set ACCOUNT_KEY or use --auth-mode login for Entra ID
export AZURE_STORAGE_ACCOUNT=mystorageaccount
export AZURE_STORAGE_KEY=$(az storage account keys list \
  --account-name mystorageaccount --resource-group myRG \
  --query '[0].value' --output tsv)

# --- Create Container ---
az storage container create \
  --name mycontainer \
  --account-name mystorageaccount \
  --auth-mode login                 # Use Entra ID (preferred)

az storage container create \
  --name public-assets \
  --account-name mystorageaccount \
  --public-access blob              # blob | container | off

# --- List / Show ---
az storage container list \
  --account-name mystorageaccount \
  --auth-mode login \
  --output table

az storage container show \
  --name mycontainer \
  --account-name mystorageaccount \
  --auth-mode login

# --- Set Permissions ---
az storage container set-permission \
  --name mycontainer \
  --account-name mystorageaccount \
  --public-access off               # Disable anonymous access

# --- Delete ---
az storage container delete \
  --name mycontainer \
  --account-name mystorageaccount \
  --auth-mode login

# --- Immutability Policy ---
az storage container immutability-policy create \
  --account-name mystorageaccount \
  --resource-group myRG \
  --container-name mycontainer \
  --period 365                      # Retention period in days

az storage container immutability-policy lock \
  --account-name mystorageaccount \
  --resource-group myRG \
  --container-name mycontainer \
  --if-match "*"                    # Lock policy (irreversible)

az storage container legal-hold set \
  --account-name mystorageaccount \
  --resource-group myRG \
  --container-name mycontainer \
  --tags case-12345                 # Add legal hold tag
```

---

## Blob Operations

```bash
# --- Upload ---
az storage blob upload \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name path/to/file.txt \
  --file ./localfile.txt \
  --auth-mode login

# Upload with specific tier
az storage blob upload \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name archive/data.csv \
  --file ./data.csv \
  --tier Cool \                     # Hot | Cool | Cold | Archive
  --auth-mode login

# Batch upload directory
az storage blob upload-batch \
  --account-name mystorageaccount \
  --destination mycontainer \
  --source ./local-dir/ \
  --pattern "*.csv" \
  --auth-mode login

# --- Download ---
az storage blob download \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name path/to/file.txt \
  --file ./downloaded.txt \
  --auth-mode login

# Batch download
az storage blob download-batch \
  --account-name mystorageaccount \
  --source mycontainer \
  --destination ./local-dir/ \
  --pattern "logs/*.log" \
  --auth-mode login

# --- List ---
az storage blob list \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --prefix logs/ \
  --include dv \                    # d=deleted, v=versions, s=snapshots, t=tags
  --auth-mode login \
  --output table

# --- Delete ---
az storage blob delete \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name path/to/file.txt \
  --auth-mode login

# Batch delete with filter
az storage blob delete-batch \
  --account-name mystorageaccount \
  --source mycontainer \
  --pattern "logs/2023-*.log" \
  --auth-mode login

# --- Change Access Tier ---
az storage blob set-tier \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name archive/old-data.csv \
  --tier Archive \                  # Hot | Cool | Cold | Archive
  --auth-mode login

# Rehydrate from Archive (standard priority)
az storage blob set-tier \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name archive/old-data.csv \
  --tier Hot \
  --rehydrate-priority Standard     # Standard | High

# --- Copy ---
az storage blob copy start \
  --account-name mystorageaccount \
  --destination-container dest-container \
  --destination-blob dest-file.txt \
  --source-uri "https://source.blob.core.windows.net/source-container/file.txt?<sas-token>" \
  --auth-mode login

# --- Blob Properties & Metadata ---
az storage blob show \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name file.txt \
  --auth-mode login

az storage blob metadata update \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name file.txt \
  --metadata owner=team-a env=prod \
  --auth-mode login

# --- Snapshots ---
az storage blob snapshot \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name file.txt \
  --auth-mode login

# --- Undelete (soft delete recovery) ---
az storage blob undelete \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name file.txt \
  --auth-mode login
```

---

## SAS Token Generation

```bash
# --- Account SAS ---
az storage account generate-sas \
  --account-name mystorageaccount \
  --resource-types sco \            # s=service, c=container, o=object
  --services b \                    # b=blob, f=file, q=queue, t=table
  --permissions rwdlacup \          # r=read, w=write, d=delete, l=list, etc.
  --expiry 2025-12-31 \
  --https-only \
  --output tsv

# --- Container SAS ---
az storage container generate-sas \
  --account-name mystorageaccount \
  --name mycontainer \
  --permissions rl \                # read + list
  --expiry 2025-06-30T00:00:00Z \
  --https-only \
  --auth-mode login \               # User Delegation SAS (Entra ID-backed; preferred)
  --output tsv

# --- Blob SAS ---
az storage blob generate-sas \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name file.txt \
  --permissions r \
  --expiry 2025-01-15T18:00:00Z \
  --https-only \
  --auth-mode login \
  --output tsv
```

---

## ADLS Gen2 (Hierarchical Namespace) Operations

```bash
# --- File System (Container) ---
az storage fs create \
  --name myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login

az storage fs list \
  --account-name myadlsaccount \
  --auth-mode login

az storage fs delete \
  --name myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login --yes

# --- Directory Operations ---
az storage fs directory create \
  --name /data/raw/2024 \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login

az storage fs directory list \
  --name /data \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login

# Move/rename directory (atomic with HNS)
az storage fs directory move \
  --name /data/raw \
  --file-system myfilesystem \
  --new-directory /data/processed \
  --account-name myadlsaccount \
  --auth-mode login

# --- File Upload / Download ---
az storage fs file upload \
  --path /data/raw/2024/events.parquet \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --source ./events.parquet \
  --auth-mode login

az storage fs file download \
  --path /data/raw/2024/events.parquet \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --destination ./events.parquet \
  --auth-mode login

# --- ACL Management ---
# Set ACL on directory (POSIX: owner, group, other + named entries)
az storage fs access set \
  --acl "user::rwx,group::r-x,other::---,user:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:r-x" \
  --path /data/raw \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login

# Show ACL
az storage fs access show \
  --path /data/raw \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login

# Update ACL recursively (apply to all children)
az storage fs access update-recursive \
  --acl "user:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:r-x" \
  --path /data \
  --file-system myfilesystem \
  --account-name myadlsaccount \
  --auth-mode login
```

---

## Lifecycle Management Policy

```bash
# Create lifecycle management policy from JSON file
az storage account management-policy create \
  --account-name mystorageaccount \
  --resource-group myRG \
  --policy @lifecycle-policy.json

# Show existing policy
az storage account management-policy show \
  --account-name mystorageaccount \
  --resource-group myRG

# Delete policy
az storage account management-policy delete \
  --account-name mystorageaccount \
  --resource-group myRG
```

---

## AzCopy — Key Patterns

```bash
# Login with managed identity (for automation in Azure VMs, AKS, etc.)
azcopy login --identity
azcopy login --identity --identity-client-id <client-id>   # User-assigned MI

# Login interactively (dev/test)
azcopy login

# --- Copy: local to blob ---
azcopy copy './localfile.txt' 'https://account.blob.core.windows.net/container/file.txt'
azcopy copy './localdir/' 'https://account.blob.core.windows.net/container/' --recursive

# --- Copy: blob to blob (server-side, no local transfer) ---
azcopy copy \
  'https://src.blob.core.windows.net/container/file.txt?<src-sas>' \
  'https://dst.blob.core.windows.net/container/file.txt?<dst-sas>'

# --- Copy: cross-account blob container ---
azcopy copy \
  'https://src.blob.core.windows.net/container?<sas>' \
  'https://dst.blob.core.windows.net/container?<sas>' \
  --recursive

# --- Sync (incremental; skips unchanged files) ---
azcopy sync './localdir/' 'https://account.blob.core.windows.net/container/' \
  --recursive \
  --delete-destination true         # Remove destination files not in source

# --- List blobs ---
azcopy list 'https://account.blob.core.windows.net/container?<sas>'

# --- Monitor jobs ---
azcopy jobs list
azcopy jobs show <job-id>
azcopy jobs resume <job-id>
```
