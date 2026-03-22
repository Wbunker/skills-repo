# Azure Migrate — CLI Reference
For service concepts, see [azure-migrate-capabilities.md](azure-migrate-capabilities.md).

> **Note**: Azure Migrate is primarily managed through the Azure Portal for most operations (appliance setup, dependency visualization, assessment review). CLI support is limited; PowerShell modules provide bulk operation support.

## Azure Migrate Projects

```bash
# Install migrate extension
az extension add --name migrate

# --- Project Management ---
az migrate project create \
  --resource-group myRG \
  --name myMigrateProject \
  --location eastus \
  --e-tag "*"                                   # Create Azure Migrate project

az migrate project list \
  --resource-group myRG                         # List migrate projects

az migrate project show \
  --resource-group myRG \
  --name myMigrateProject                       # Show project details

az migrate project delete \
  --resource-group myRG \
  --name myMigrateProject --yes                 # Delete migrate project

# --- Discovered Machines ---
az migrate machine list \
  --resource-group myRG \
  --project-name myMigrateProject               # List discovered machines

az migrate machine show \
  --resource-group myRG \
  --project-name myMigrateProject \
  --name machine-id                             # Show specific machine details

# --- Assessments ---
az migrate assessment create \
  --resource-group myRG \
  --project-name myMigrateProject \
  --group-name myServerGroup \
  --assessment-name myAssessment \
  --target-location eastus \
  --currency USD \
  --azure-offer-code MSAZR0003P \
  --pricing-tier Standard \
  --azure-hybrid-use-benefit Yes \
  --reserved-instance ThreeYear               # Create VM assessment for a group

az migrate assessment list \
  --resource-group myRG \
  --project-name myMigrateProject \
  --group-name myServerGroup                  # List assessments in a group

# --- Groups ---
az migrate group create \
  --resource-group myRG \
  --project-name myMigrateProject \
  --name myServerGroup                        # Create assessment group

az migrate group list \
  --resource-group myRG \
  --project-name myMigrateProject             # List groups in project
```

## Azure Site Recovery (Server Migration — Agent-based)

```bash
# --- Replication Policy ---
az site-recovery replication-policy create \
  --resource-group myRG \
  --vault-name myRecoveryVault \
  --policy-name 24hr-policy \
  --recovery-point-history 1440 \
  --app-consistent-frequency-in-minutes 60 \
  --crash-consistent-frequency-in-minutes 5  # Create replication policy

az site-recovery replication-policy list \
  --resource-group myRG \
  --vault-name myRecoveryVault                # List replication policies

# --- Recovery Services Vault (required for agent-based migration) ---
az backup vault create \
  --resource-group myRG \
  --name myRecoveryVault \
  --location eastus                           # Create Recovery Services vault

az backup vault list --resource-group myRG   # List Recovery Services vaults

# --- Protected Items ---
az site-recovery protected-item list \
  --resource-group myRG \
  --vault-name myRecoveryVault \
  --fabric-name myFabric \
  --protection-container-name myContainer    # List replicating machines

az site-recovery protected-item show \
  --resource-group myRG \
  --vault-name myRecoveryVault \
  --fabric-name myFabric \
  --protection-container-name myContainer \
  --name myServer                            # Show replication status for a server
```

## PowerShell Bulk Operations

```powershell
# --- Install Az.Migrate module ---
Install-Module -Name Az.Migrate -Scope CurrentUser -Force
Import-Module Az.Migrate

# --- Initialize Migrate Project ---
$project = Get-AzMigrateProject -ResourceGroupName myRG -ProjectName myMigrateProject

# --- List Discovered Servers ---
$servers = Get-AzMigrateDiscoveredServer -ResourceGroupName myRG -ProjectName myMigrateProject
$servers | Select-Object DisplayName, NumberOfCores, MemoryInMb, OperatingSystemName

# --- Bulk Assessment ---
New-AzMigrateServerAssessment `
  -ResourceGroupName myRG `
  -ProjectName myMigrateProject `
  -GroupName myServerGroup `
  -AssessmentName bulk-assessment `
  -TargetLocation eastus `
  -AzureHybridUseBenefit Yes `
  -ReservedInstance ThreeYear

# --- Initiate Replication (Agentless VMware) ---
$diskMapping = New-AzMigrateDiskMapping -DiskID "disk001" -DiskType Premium_LRS
New-AzMigrateServerReplication `
  -SourceMachineId "/subscriptions/.../machines/myServer" `
  -TargetResourceGroupId "/subscriptions/.../resourceGroups/TargetRG" `
  -TargetNetworkId "/subscriptions/.../virtualNetworks/myVNet" `
  -TargetSubnetName "default" `
  -TargetVMName "myMigratedVM" `
  -DiskToInclude $diskMapping

# --- Check Replication Status ---
Get-AzMigrateServerReplication -TargetObjectID "/subscriptions/.../replicatingMachines/myServer"

# --- Test Migration ---
Start-AzMigrateTestMigration `
  -InputObject $replicatingMachine `
  -TestNetworkId "/subscriptions/.../virtualNetworks/testVNet"

# --- Cutover ---
Start-AzMigrateMigration -InputObject $replicatingMachine

# --- Complete Migration (removes replication) ---
Complete-AzMigrateTestMigration -InputObject $replicatingMachine
```

## AzCopy for Data Migration

```bash
# Upload files to Azure Storage
azcopy copy '/local/path/*' 'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' --recursive

# Download from Azure Storage
azcopy copy 'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' '/local/path' --recursive

# Sync source to destination (incremental)
azcopy sync '/local/path' 'https://myaccount.blob.core.windows.net/mycontainer?<SAS>' --recursive

# Copy between storage accounts (server-side)
azcopy copy \
  'https://source.blob.core.windows.net/container?<SAS>' \
  'https://dest.blob.core.windows.net/container?<SAS>' \
  --recursive

# Login with managed identity or CLI auth
azcopy login --tenant-id mytenantid
azcopy login --identity  # managed identity
```
