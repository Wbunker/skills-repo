# Azure Managed Disks — CLI Reference
For service concepts, see [disk-capabilities.md](disk-capabilities.md).

## Disk Management

```bash
# --- Create Managed Disk ---
# Standard HDD
az disk create \
  --name myStandardDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 256 \
  --sku Standard_LRS              # Standard_LRS | StandardSSD_LRS | Premium_LRS | UltraSSD_LRS | PremiumV2_LRS

# Premium SSD with specific size tier
az disk create \
  --name myPremiumDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 1024 \
  --sku Premium_LRS \
  --zone 1                        # Availability Zone (1, 2, or 3)

# Standard SSD with zone redundancy
az disk create \
  --name myZRSDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 512 \
  --sku StandardSSD_ZRS           # Zone-redundant Standard SSD

# Premium SSD v2 (configure IOPS and throughput independently)
az disk create \
  --name myPremiumV2Disk \
  --resource-group myRG \
  --location eastus \
  --size-gb 512 \
  --sku PremiumV2_LRS \
  --disk-iops-read-write 40000 \  # Custom IOPS (up to 80,000)
  --disk-mbps-read-write 600 \    # Custom throughput MiB/s (up to 1,200)
  --zone 1

# Ultra Disk
az disk create \
  --name myUltraDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 1024 \
  --sku UltraSSD_LRS \
  --disk-iops-read-write 100000 \
  --disk-mbps-read-write 2000 \
  --zone 2

# Create disk from snapshot
az disk create \
  --name myRestoredDisk \
  --resource-group myRG \
  --location eastus \
  --source /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Compute/snapshots/mySnapshot

# Create disk from VHD blob
az disk create \
  --name myImportedDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 128 \
  --source https://mystorageaccount.blob.core.windows.net/vhds/myimage.vhd

# Shared disk (for cluster workloads)
az disk create \
  --name mySharedDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 256 \
  --sku Premium_LRS \
  --max-shares 2 \                # Maximum simultaneous attachments
  --zone 1

# --- List Disks ---
az disk list \
  --resource-group myRG \
  --output table

az disk list \
  --query "[?diskState=='Unattached'].[name, diskSizeGb, sku.name]" \
  --output table                  # Find unattached (billable) disks

# --- Show Disk Details ---
az disk show \
  --name myPremiumDisk \
  --resource-group myRG

# --- Update Disk ---
# Resize disk (requires VM deallocation for most disk types)
az disk update \
  --name myPremiumDisk \
  --resource-group myRG \
  --size-gb 2048

# Change SKU (e.g., Standard to Premium)
az disk update \
  --name myStandardDisk \
  --resource-group myRG \
  --sku Premium_LRS

# Update Premium SSD v2 / Ultra Disk IOPS and throughput (online, no downtime)
az disk update \
  --name myPremiumV2Disk \
  --resource-group myRG \
  --disk-iops-read-write 60000 \
  --disk-mbps-read-write 800

# Enable on-demand bursting (Premium SSD P30+)
az disk update \
  --name myPremiumDisk \
  --resource-group myRG \
  --enable-bursting true

# Change performance tier (e.g., P10 disk → P30 performance)
az disk update \
  --name myPremiumDisk \
  --resource-group myRG \
  --set tier=P30

# --- Delete Disk ---
az disk delete \
  --name myPremiumDisk \
  --resource-group myRG --yes

# --- Grant Temporary SAS Access (disk export) ---
az disk grant-access \
  --name myPremiumDisk \
  --resource-group myRG \
  --duration-in-seconds 3600 \    # URL valid for 1 hour
  --access-level Read             # Read | Write

# Revoke SAS access
az disk revoke-access \
  --name myPremiumDisk \
  --resource-group myRG
```

---

## Snapshot Management

```bash
# --- Create Snapshot ---
# Incremental snapshot (recommended)
az snapshot create \
  --name mySnapshot \
  --resource-group myRG \
  --location eastus \
  --source /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Compute/disks/myDisk \
  --incremental true              # Strongly recommended; default is full

# Zone-redundant snapshot
az snapshot create \
  --name myZRSSnapshot \
  --resource-group myRG \
  --location eastus \
  --source /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Compute/disks/myDisk \
  --incremental true \
  --sku Standard_ZRS              # Standard_LRS | Standard_ZRS | Premium_LRS

# Snapshot from running VM OS disk (application-consistent via pre/post scripts)
DISK_ID=$(az vm show --name myVM --resource-group myRG --query 'storageProfile.osDisk.managedDisk.id' --output tsv)
az snapshot create \
  --name myOSSnapshot \
  --resource-group myRG \
  --location eastus \
  --source "$DISK_ID" \
  --incremental true

# --- List Snapshots ---
az snapshot list \
  --resource-group myRG \
  --output table

az snapshot list \
  --query "[?name contains 'myVM'].[name, diskSizeGb, timeCreated]" \
  --output table

# --- Show Snapshot ---
az snapshot show \
  --name mySnapshot \
  --resource-group myRG

# --- Copy Snapshot to Another Region ---
az snapshot create \
  --name mySnapshotCopy \
  --resource-group myRG-WestUS \
  --location westus \
  --source /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Compute/snapshots/mySnapshot \
  --copy-start false              # true = background copy; false = synchronous

# --- Export Snapshot to Storage (SAS) ---
az snapshot grant-access \
  --name mySnapshot \
  --resource-group myRG \
  --duration-in-seconds 7200 \
  --access-level Read

az snapshot revoke-access \
  --name mySnapshot \
  --resource-group myRG

# --- Delete Snapshot ---
az snapshot delete \
  --name mySnapshot \
  --resource-group myRG --yes
```

---

## VM Disk Attachment

```bash
# --- Attach Data Disk to VM ---
az vm disk attach \
  --vm-name myVM \
  --resource-group myRG \
  --disk myDataDisk \
  --lun 0 \                       # Logical Unit Number (0-63)
  --caching ReadOnly              # None | ReadOnly | ReadWrite

# Attach new (auto-created) data disk
az vm disk attach \
  --vm-name myVM \
  --resource-group myRG \
  --new \
  --size-gb 512 \
  --sku Premium_LRS \
  --lun 1

# --- Detach Data Disk from VM ---
az vm disk detach \
  --vm-name myVM \
  --resource-group myRG \
  --name myDataDisk

# --- List VM Disks ---
az vm show \
  --name myVM \
  --resource-group myRG \
  --query 'storageProfile' \
  --output json

# --- Update OS Disk Cache Setting ---
az vm update \
  --name myVM \
  --resource-group myRG \
  --set storageProfile.osDisk.caching=ReadWrite

# --- Enable Ultra Disk on VM (requires VM reallocation) ---
az vm update \
  --name myVM \
  --resource-group myRG \
  --ultra-ssd-enabled true
```

---

## Disk Encryption

```bash
# --- Create Disk Encryption Set (CMK) ---
# First, create Key Vault with required settings
az keyvault create \
  --name myKeyVault \
  --resource-group myRG \
  --location eastus \
  --enable-purge-protection true \
  --enable-soft-delete true

# Create key in Key Vault
az keyvault key create \
  --vault-name myKeyVault \
  --name myDiskKey \
  --protection software           # software | hsm

# Create Disk Encryption Set
az disk encryption set create \
  --name myDES \
  --resource-group myRG \
  --location eastus \
  --key-url https://myKeyVault.vault.azure.net/keys/myDiskKey/<version> \
  --source-vault myKeyVault \
  --encryption-type EncryptionAtRestWithCustomerKey  # or EncryptionAtRestWithPlatformAndCustomerKeys (double)

# Grant DES access to Key Vault
DES_IDENTITY=$(az disk encryption set show --name myDES --resource-group myRG --query identity.principalId --output tsv)
az keyvault set-policy \
  --name myKeyVault \
  --object-id "$DES_IDENTITY" \
  --key-permissions wrapKey unwrapKey get

# Create encrypted disk using DES
az disk create \
  --name myEncryptedDisk \
  --resource-group myRG \
  --location eastus \
  --size-gb 256 \
  --sku Premium_LRS \
  --disk-encryption-set myDES

# --- Azure Disk Encryption (ADE — BitLocker / DM-Crypt) ---
# Enable ADE on VM (requires Key Vault)
az vm encryption enable \
  --resource-group myRG \
  --name myVM \
  --disk-encryption-keyvault myKeyVault \
  --key-encryption-key myKEK \    # Optional: Key Encryption Key
  --volume-type All               # OS | Data | All

# Check ADE status
az vm encryption show \
  --resource-group myRG \
  --name myVM

# Disable ADE (data disks only; OS disk cannot be decrypted without reimaging)
az vm encryption disable \
  --resource-group myRG \
  --name myVM \
  --volume-type Data
```
