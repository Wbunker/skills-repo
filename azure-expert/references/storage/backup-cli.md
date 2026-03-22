# Azure Backup & Recovery — CLI Reference
For service concepts, see [backup-capabilities.md](backup-capabilities.md).

## Recovery Services Vault

```bash
# --- Create Vault ---
az backup vault create \
  --name myRecoveryVault \
  --resource-group myRG \
  --location eastus

# Set storage redundancy (default is GeoRedundant)
az backup vault backup-properties set \
  --name myRecoveryVault \
  --resource-group myRG \
  --backup-storage-redundancy GeoRedundant  # LocallyRedundant | GeoRedundant | ZoneRedundant

# Enable Cross-Region Restore
az backup vault backup-properties set \
  --name myRecoveryVault \
  --resource-group myRG \
  --cross-region-restore-flag true

# Enable soft delete (default enabled)
az backup vault update \
  --name myRecoveryVault \
  --resource-group myRG \
  --soft-delete-feature-state Enable  # Enable | Disable | AlwaysOn (locked)

# --- List / Show Vaults ---
az backup vault list \
  --resource-group myRG \
  --output table

az backup vault show \
  --name myRecoveryVault \
  --resource-group myRG

# --- Delete Vault ---
az backup vault delete \
  --name myRecoveryVault \
  --resource-group myRG --yes
```

---

## Backup Policy

```bash
# --- List Available Policy Templates ---
az backup policy list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --output table

# Show default VM policy details
az backup policy show \
  --name DefaultPolicy \
  --vault-name myRecoveryVault \
  --resource-group myRG

# --- Create Custom VM Backup Policy (JSON) ---
# Get default policy template to modify
az backup policy get-default-for-vm \
  --vault-name myRecoveryVault \
  --resource-group myRG > vm-policy.json

# Create policy from JSON
az backup policy create \
  --name myVMPolicy \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --backup-management-type AzureIaasVM \
  --policy @vm-policy.json

# --- Delete Policy ---
az backup policy delete \
  --name myVMPolicy \
  --vault-name myRecoveryVault \
  --resource-group myRG
```

---

## Azure VM Backup

```bash
# --- Enable Backup for VM ---
az backup protection enable-for-vm \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --vm myVM \
  --policy-name DefaultPolicy

# Enable backup for VM in different resource group
az backup protection enable-for-vm \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --vm /subscriptions/<sub-id>/resourceGroups/vmRG/providers/Microsoft.Compute/virtualMachines/myVM \
  --policy-name myVMPolicy

# --- Trigger On-Demand Backup ---
az backup protection backup-now \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --backup-management-type AzureIaasVM \
  --retain-until 2025-12-31        # Retention date for this recovery point

# --- List Protected VMs ---
az backup container list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --backup-management-type AzureIaasVM \
  --output table

# --- List Recovery Points for a VM ---
az backup recoverypoint list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --backup-management-type AzureIaasVM \
  --output table

# --- List Backup Jobs ---
az backup job list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --output table

az backup job list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --status Failed \                # InProgress | Completed | Failed | Cancelled
  --output table

# Wait for job to complete
az backup job wait \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --job <job-id>

# --- Restore VM Disks ---
az backup restore restore-disks \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --storage-account myStorageAccount \
  --rp-name <recovery-point-name> \
  --target-resource-group myTargetRG

# Restore to new VM from template (after restore-disks completes)
# az deployment group create --template-file <template-from-storage-account>

# --- Restore Files from VM Backup ---
az backup restore files mount-rp \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --rp-name <recovery-point-name>

# Unmount after file recovery
az backup restore files unmount-rp \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --rp-name <recovery-point-name>

# --- Stop Protection ---
# Stop protection and retain existing backup data
az backup protection disable \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --backup-management-type AzureIaasVM \
  --yes

# Stop protection and delete all backup data
az backup protection disable \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name myVM \
  --item-name myVM \
  --backup-management-type AzureIaasVM \
  --delete-backup-data true \
  --yes
```

---

## SQL Server in Azure VM Backup

```bash
# --- Register SQL VM with Vault ---
az backup container register \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --workload-type SQLDataBase \
  --backup-management-type AzureWorkload \
  --resource-id /subscriptions/<sub-id>/resourceGroups/vmRG/providers/Microsoft.Compute/virtualMachines/mySQLVM

# --- List Discovered Databases ---
az backup protectable-item list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --workload-type SQLDataBase \
  --backup-management-type AzureWorkload \
  --output table

# --- Enable SQL Database Backup ---
az backup protection enable-for-azurewl \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --policy-name SQLPolicy \
  --protectable-item-type SQLDatabase \
  --protectable-item-name "mySQLVM;mssqlserver;mydb" \
  --server-name mySQLVM \
  --workload-type SQLDataBase

# --- List SQL Containers ---
az backup container list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --backup-management-type AzureWorkload \
  --output table

# --- Point-in-Time Restore SQL ---
az backup restore restore-azurewl \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --rp-name <recovery-point> \
  --restore-config @restore-config.json
```

---

## Azure Files Backup

```bash
# --- Enable Azure Files Backup ---
az backup protection enable-for-azurefileshare \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --storage-account mystorageaccount \
  --azure-file-share myfileshare \
  --policy-name AzureFileSharePolicy

# --- List Protected File Shares ---
az backup container list \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --backup-management-type AzureStorage \
  --output table

# --- Restore File Share ---
az backup restore restore-azurefileshare \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name "StorageContainer;storage;myRG;mystorageaccount" \
  --item-name "AzureFileShare;myfileshare" \
  --restore-mode OriginalLocation \
  --rp-name <recovery-point> \
  --resolve-conflict Overwrite

# Restore specific files
az backup restore restore-azurefiles \
  --vault-name myRecoveryVault \
  --resource-group myRG \
  --container-name "StorageContainer;storage;myRG;mystorageaccount" \
  --item-name "AzureFileShare;myfileshare" \
  --rp-name <recovery-point> \
  --restore-mode OriginalLocation \
  --source-file-type File \
  --source-file-path "dir/file.txt" \
  --resolve-conflict Overwrite
```

---

## Azure Site Recovery (ASR)

```bash
# --- Create ASR Vault (in target/DR region) ---
az recovery-services vault create \
  --name myASRVault \
  --resource-group myDR-RG \
  --location westus                 # DR target region

# --- Enable ASR Replication for Azure VM ---
# Note: Full ASR setup is complex; use Azure Portal or ARM template for initial configuration
# CLI supports status and management operations

# --- List Replication Protected Items ---
az resource list \
  --resource-type Microsoft.RecoveryServices/vaults/replicationProtectedItems \
  --resource-group myDR-RG \
  --output table

# --- Check ASR Job Status ---
az resource show \
  --ids "/subscriptions/<sub>/resourceGroups/myDR-RG/providers/Microsoft.RecoveryServices/vaults/myASRVault/replicationJobs/<job-id>"

# --- Trigger Test Failover (via REST; CLI has limited ASR support) ---
# Use az rest for ASR operations not exposed in CLI
az rest \
  --method post \
  --uri "https://management.azure.com/subscriptions/<sub>/resourceGroups/myDR-RG/providers/Microsoft.RecoveryServices/vaults/myASRVault/replicationProtectedItems/<item>/testFailover?api-version=2023-04-01" \
  --body @test-failover.json
```
