# Azure Files — CLI Reference
For service concepts, see [files-capabilities.md](files-capabilities.md).

## File Share Management

```bash
# --- Create File Share (Standard) ---
az storage share create \
  --name myfileshare \
  --account-name mystorageaccount \
  --quota 1024 \                    # Size in GiB (up to 102,400 for large shares)
  --auth-mode login

# Create file share with access tier
az storage share-rm create \
  --name myfileshare \
  --storage-account mystorageaccount \
  --resource-group myRG \
  --quota 1024 \
  --access-tier TransactionOptimized  # TransactionOptimized | Hot | Cool | Premium

# --- Create Premium File Share ---
# First create Premium File Shares storage account
az storage account create \
  --name mypremiumfiles \
  --resource-group myRG \
  --location eastus \
  --sku Premium_LRS \
  --kind FileStorage

az storage share-rm create \
  --name mypremiumshare \
  --storage-account mypremiumfiles \
  --resource-group myRG \
  --quota 1024 \                    # Provisioned size in GiB; determines IOPS and throughput
  --enabled-protocol SMB            # SMB | NFS

# --- List Shares ---
az storage share list \
  --account-name mystorageaccount \
  --auth-mode login \
  --output table

az storage share-rm list \
  --storage-account mystorageaccount \
  --resource-group myRG \
  --output table

# --- Show Share Details ---
az storage share-rm show \
  --name myfileshare \
  --storage-account mystorageaccount \
  --resource-group myRG

# --- Update Share (resize) ---
az storage share-rm update \
  --name myfileshare \
  --storage-account mystorageaccount \
  --resource-group myRG \
  --quota 2048 \                    # Increase provisioned size
  --access-tier Hot

# --- Delete Share ---
az storage share delete \
  --name myfileshare \
  --account-name mystorageaccount \
  --auth-mode login

az storage share-rm delete \
  --name myfileshare \
  --storage-account mystorageaccount \
  --resource-group myRG --yes

# --- Snapshots ---
az storage share snapshot \
  --name myfileshare \
  --account-name mystorageaccount \
  --auth-mode login

az storage share list \
  --account-name mystorageaccount \
  --include-snapshots \
  --auth-mode login

# Restore a file from snapshot
az storage file copy start \
  --account-name mystorageaccount \
  --destination-share myfileshare \
  --destination-path restored/file.txt \
  --source-share myfileshare \
  --source-path file.txt \
  --source-snapshot <snapshot-datetime> \
  --auth-mode login

# --- Statistics ---
az storage share stats \
  --name myfileshare \
  --account-name mystorageaccount \
  --auth-mode login
```

---

## File Operations

```bash
# --- Upload File ---
az storage file upload \
  --account-name mystorageaccount \
  --share-name myfileshare \
  --source ./localfile.txt \
  --path remote/path/file.txt \
  --auth-mode login

# Batch upload
az storage file upload-batch \
  --account-name mystorageaccount \
  --destination myfileshare \
  --source ./local-dir/ \
  --destination-path remote/dir/ \
  --auth-mode login

# --- Download File ---
az storage file download \
  --account-name mystorageaccount \
  --share-name myfileshare \
  --path remote/path/file.txt \
  --dest ./downloaded.txt \
  --auth-mode login

# Batch download
az storage file download-batch \
  --account-name mystorageaccount \
  --source myfileshare \
  --destination ./local-dir/ \
  --auth-mode login

# --- List Files and Directories ---
az storage file list \
  --account-name mystorageaccount \
  --share-name myfileshare \
  --path remote/dir/ \
  --auth-mode login \
  --output table

# --- Create Directory ---
az storage directory create \
  --account-name mystorageaccount \
  --share-name myfileshare \
  --name mydir/subdir \
  --auth-mode login

# --- Delete File ---
az storage file delete \
  --account-name mystorageaccount \
  --share-name myfileshare \
  --path remote/path/file.txt \
  --auth-mode login

# --- Copy File ---
az storage file copy start \
  --account-name mystorageaccount \
  --destination-share myfileshare \
  --destination-path dest/file.txt \
  --source-account-name sourcestorage \
  --source-share sourceshare \
  --source-path source/file.txt \
  --auth-mode login
```

---

## Azure File Sync

```bash
# --- Create Storage Sync Service ---
az storagesync service create \
  --name mySyncService \
  --resource-group myRG \
  --location eastus

az storagesync service show \
  --name mySyncService \
  --resource-group myRG

az storagesync service list \
  --resource-group myRG

# --- Create Sync Group ---
az storagesync sync-group create \
  --name mySyncGroup \
  --storage-sync-service mySyncService \
  --resource-group myRG

# --- Create Cloud Endpoint (Azure File Share) ---
az storagesync sync-group cloud-endpoint create \
  --name myCloudEndpoint \
  --sync-group-name mySyncGroup \
  --storage-sync-service mySyncService \
  --resource-group myRG \
  --storage-account /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/mystorageaccount \
  --azure-file-share-name myfileshare

# --- Create Server Endpoint (on registered server) ---
az storagesync sync-group server-endpoint create \
  --name myServerEndpoint \
  --sync-group-name mySyncGroup \
  --storage-sync-service mySyncService \
  --resource-group myRG \
  --server-id /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.StorageSync/storageSyncServices/mySyncService/registeredServers/<server-id> \
  --server-local-path "D:\\SyncFolder" \
  --cloud-tiering Enabled \
  --volume-free-space-percent 20 \  # Minimum free space on local volume
  --tier-files-older-than-days 30   # Tier files not accessed in 30 days

# --- List Registered Servers ---
az storagesync registered-server list \
  --storage-sync-service mySyncService \
  --resource-group myRG

# --- Show Sync Status ---
az storagesync sync-group server-endpoint show \
  --name myServerEndpoint \
  --sync-group-name mySyncGroup \
  --storage-sync-service mySyncService \
  --resource-group myRG

# --- Delete Server Endpoint ---
az storagesync sync-group server-endpoint delete \
  --name myServerEndpoint \
  --sync-group-name mySyncGroup \
  --storage-sync-service mySyncService \
  --resource-group myRG --yes
```

---

## Azure NetApp Files

```bash
# --- Register NetApp Resource Provider ---
az provider register --namespace Microsoft.NetApp

# --- Create NetApp Account ---
az netappfiles account create \
  --name myNetAppAccount \
  --resource-group myRG \
  --location eastus

az netappfiles account list \
  --resource-group myRG

# --- Create Capacity Pool ---
az netappfiles pool create \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --resource-group myRG \
  --location eastus \
  --size 4 \                        # Size in TiB (minimum 4 TiB)
  --service-level Premium           # Standard | Premium | Ultra

az netappfiles pool list \
  --account-name myNetAppAccount \
  --resource-group myRG \
  --output table

# --- Delegate Subnet for NetApp ---
az network vnet subnet update \
  --name anf-subnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --delegations Microsoft.NetApp/volumes

# --- Create Volume (NFS) ---
az netappfiles volume create \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --name myVolume \
  --resource-group myRG \
  --location eastus \
  --vnet myVNet \
  --subnet anf-subnet \
  --usage-threshold 1024 \          # Size in GiB
  --protocol-types NFSv4.1 \        # NFSv3 | NFSv4.1 | CIFS (SMB)
  --file-path myvolume \            # NFS export path
  --allowed-clients 10.0.0.0/24    # Allowed IP range

# --- Create Volume (SMB) ---
az netappfiles volume create \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --name mySmbVolume \
  --resource-group myRG \
  --location eastus \
  --vnet myVNet \
  --subnet anf-subnet \
  --usage-threshold 2048 \
  --protocol-types CIFS \
  --file-path mysmbvolume

# --- Snapshot ---
az netappfiles snapshot create \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --volume-name myVolume \
  --name mysnapshot \
  --resource-group myRG \
  --location eastus

az netappfiles snapshot list \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --volume-name myVolume \
  --resource-group myRG

# --- Cross-Region Replication ---
az netappfiles volume replication approve \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --volume-name myVolume \
  --resource-group myRG \
  --remote-volume-resource-id <dest-volume-resource-id>

az netappfiles volume replication status \
  --account-name myNetAppAccount \
  --pool-name myPool \
  --volume-name myVolume \
  --resource-group myRG
```
