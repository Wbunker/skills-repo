# Azure Hybrid Benefit & Spot VMs — CLI Reference
For service concepts, see [hybrid-spot-capabilities.md](hybrid-spot-capabilities.md).

## Azure Hybrid Benefit

```bash
# --- Windows Server Hybrid Benefit ---
# Apply Windows Server AHB when creating a new VM
az vm create \
  --resource-group myRG \
  --name myWindowsVM \
  --image Win2022Datacenter \
  --size Standard_D4s_v5 \
  --license-type Windows_Server \
  --admin-username azureuser \
  --admin-password {password}

# Apply Windows Server AHB to an existing Windows VM
az vm update \
  --resource-group myRG \
  --name myWindowsVM \
  --license-type Windows_Server

# Remove AHB from a VM (revert to PAYG Windows licensing)
az vm update \
  --resource-group myRG \
  --name myWindowsVM \
  --license-type None

# Apply AHB to a Windows VM Scale Set
az vmss create \
  --resource-group myRG \
  --name myWindowsVMSS \
  --image Win2022Datacenter \
  --instance-count 3 \
  --vm-sku Standard_D4s_v5 \
  --license-type Windows_Server

# Update existing VMSS to apply AHB
az vmss update \
  --resource-group myRG \
  --name myWindowsVMSS \
  --license-type Windows_Server

# Verify AHB status on VMs
az vm list \
  --query "[].{Name:name, RG:resourceGroup, LicenseType:licenseType, OS:storageProfile.osDisk.osType}" \
  --output table

# Count all VMs with AHB applied (Windows_Server license type)
az vm list \
  --query "length([?licenseType=='Windows_Server'])" \
  --output tsv

# --- SQL Server Hybrid Benefit ---
# Create SQL Server VM with AHB (BYOL - Bring Your Own License)
az vm create \
  --resource-group myRG \
  --name mySQLVM \
  --image MicrosoftSQLServer:sql2022-ws2022:enterprise:latest \
  --size Standard_E4ds_v5 \
  --license-type Windows_Server \
  --admin-username azureuser \
  --admin-password {password}

# Apply AHB to Azure SQL Database (via SQL VM resource provider for IaaS SQL)
az sql vm update \
  --resource-group myRG \
  --name mySQLVM \
  --license-type AHUB

# Create Azure SQL Managed Instance with AHB
az sql mi create \
  --resource-group myRG \
  --name mySQLMI \
  --location eastus \
  --admin-user sqladmin \
  --admin-password {password} \
  --license-type BasePrice \
  --subnet /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/managedInstanceSubnet \
  --vnet-name myVNet \
  --capacity 8 \
  --edition GeneralPurpose \
  --family Gen5

# Update existing SQL MI to apply AHB (BasePrice = AHB)
az sql mi update \
  --resource-group myRG \
  --name mySQLMI \
  --license-type BasePrice

# Revert SQL MI to PAYG (LicenseIncluded)
az sql mi update \
  --resource-group myRG \
  --name mySQLMI \
  --license-type LicenseIncluded

# Create Azure SQL Database with AHB
az sql db create \
  --resource-group myRG \
  --server mySQLServer \
  --name myDatabase \
  --license-type BasePrice \
  --edition GeneralPurpose \
  --capacity 8 \
  --family Gen5

# Update existing SQL Database to apply AHB
az sql db update \
  --resource-group myRG \
  --server mySQLServer \
  --name myDatabase \
  --license-type BasePrice

# Check SQL DB license type
az sql db show \
  --resource-group myRG \
  --server mySQLServer \
  --name myDatabase \
  --query "licenseType" \
  --output tsv

# --- Linux Hybrid Benefit (RHEL / SUSE) ---
# Create RHEL BYOS VM (apply existing Red Hat subscription)
az vm create \
  --resource-group myRG \
  --name myRHELVM \
  --image RedHat:RHEL:8-lvm-gen2:latest \
  --size Standard_D4s_v5 \
  --license-type RHEL_BYOS \
  --admin-username azureuser \
  --generate-ssh-keys

# Update existing RHEL VM to BYOS (apply AHB)
az vm update \
  --resource-group myRG \
  --name myRHELVM \
  --license-type RHEL_BYOS

# Create SUSE BYOS VM
az vm create \
  --resource-group myRG \
  --name mySUSEVM \
  --image SUSE:sles-15-sp5:gen2:latest \
  --size Standard_D4s_v5 \
  --license-type SLES_BYOS \
  --admin-username azureuser \
  --generate-ssh-keys

# Update existing SUSE VM to BYOS
az vm update \
  --resource-group myRG \
  --name mySUSEVM \
  --license-type SLES_BYOS

# --- AHB for AKS Windows Node Pools ---
# Add Windows node pool with AHB enabled
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name winpool \
  --os-type Windows \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --windows-os-disk-size-gb 128

# Enable Windows AHB on an existing Windows node pool
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name winpool \
  --enable-windows-ahb

# Disable AHB on Windows node pool (revert to PAYG)
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name winpool \
  --disable-windows-ahb
```

## Spot Virtual Machines

```bash
# --- Create Spot VMs ---
# Create a Linux Spot VM with Deallocate eviction policy
az vm create \
  --resource-group myRG \
  --name mySpotVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price -1 \
  --admin-username azureuser \
  --generate-ssh-keys

# Create a Spot VM with Delete eviction policy (stateless batch)
az vm create \
  --resource-group myRG \
  --name myBatchSpotVM \
  --image Ubuntu2204 \
  --size Standard_D16s_v5 \
  --priority Spot \
  --eviction-policy Delete \
  --max-price -1 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --no-wait

# Create Spot VM with max price cap ($0.05/hour)
az vm create \
  --resource-group myRG \
  --name myPriceCappedSpotVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price 0.05 \
  --admin-username azureuser \
  --generate-ssh-keys

# Create Windows Spot VM with AHB
az vm create \
  --resource-group myRG \
  --name myWindowsSpotVM \
  --image Win2022Datacenter \
  --size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price -1 \
  --license-type Windows_Server \
  --admin-username azureuser \
  --admin-password {password}

# Simulate eviction (for testing eviction handling)
az vm simulate-eviction \
  --resource-group myRG \
  --name mySpotVM

# List all Spot VMs in a resource group
az vm list \
  --resource-group myRG \
  --query "[?priority=='Spot'].{Name:name, Size:hardwareProfile.vmSize, EvictionPolicy:evictionPolicy, MaxPrice:billingProfile.maxPrice}" \
  --output table
```

## Spot VM Scale Sets

```bash
# --- Create Spot VMSS ---
# Create a Spot VMSS (Linux, Delete eviction)
az vmss create \
  --resource-group myRG \
  --name mySpotVMSS \
  --image Ubuntu2204 \
  --instance-count 3 \
  --vm-sku Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Delete \
  --max-price -1 \
  --admin-username azureuser \
  --generate-ssh-keys

# Create a mixed On-Demand + Spot VMSS
az vmss create \
  --resource-group myRG \
  --name myMixedVMSS \
  --image Ubuntu2204 \
  --instance-count 5 \
  --vm-sku Standard_D4s_v5 \
  --priority Low \
  --eviction-policy Delete \
  --max-price -1 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --orchestration-mode Flexible

# Scale Spot VMSS
az vmss scale \
  --resource-group myRG \
  --name mySpotVMSS \
  --new-capacity 10

# List VMSS instances and their eviction status
az vmss list-instances \
  --resource-group myRG \
  --name mySpotVMSS \
  --query "[].{InstanceId:instanceId, State:provisioningState}" \
  --output table
```

## AKS Spot Node Pools

```bash
# Add a Spot node pool to an existing AKS cluster
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name spotpool \
  --node-count 0 \
  --node-vm-size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 20 \
  --node-taints kubernetes.azure.com/scalesetpriority=spot:NoSchedule \
  --labels workload=batch spot=true

# Add a Spot node pool with specific labels for workload placement
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name gpuspotpool \
  --node-count 0 \
  --node-vm-size Standard_NC6s_v3 \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 10 \
  --node-taints kubernetes.azure.com/scalesetpriority=spot:NoSchedule sku=gpu:NoSchedule \
  --labels workload=ml accelerator=nvidia spot=true

# List node pools and their priority settings
az aks nodepool list \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --query "[].{Name:name, Priority:scaleSetPriority, EvictionPolicy:scaleSetEvictionPolicy, SpotMaxPrice:spotMaxPrice, MinCount:minCount, MaxCount:maxCount}" \
  --output table
```

## B-Series Burstable VMs

```bash
# --- Create B-series VMs (dev/test workloads) ---
# Create a B2s VM for a development environment
az vm create \
  --resource-group devRG \
  --name myDevVM \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username devuser \
  --generate-ssh-keys

# Create a B4ms VM for a dev database
az vm create \
  --resource-group devRG \
  --name myDevDB \
  --image Ubuntu2204 \
  --size Standard_B4ms \
  --admin-username dbuser \
  --generate-ssh-keys

# Create B-series Windows VM for dev with AHB
az vm create \
  --resource-group devRG \
  --name myDevWindowsVM \
  --image Win2022Datacenter \
  --size Standard_B4ms \
  --license-type Windows_Server \
  --admin-username devuser \
  --admin-password {password}

# List available B-series VM sizes in a region
az vm list-sizes \
  --location eastus \
  --query "[?contains(name, '_B')].{Name:name, vCPUs:numberOfCores, RAM_GB:memoryInMb}" \
  --output table

# Resize an existing VM from D-series to B-series (cost savings)
az vm resize \
  --resource-group devRG \
  --name myDevVM \
  --size Standard_B2s
```

## Cost Optimization Audit Commands

```bash
# --- Audit AHB adoption across subscription ---
# Find all Windows VMs NOT using AHB (potential savings)
az vm list \
  --query "[?storageProfile.osDisk.osType=='Windows' && licenseType!='Windows_Server'].{Name:name, RG:resourceGroup, Size:hardwareProfile.vmSize, LicenseType:licenseType}" \
  --output table

# Count VMs by license type for savings assessment
az vm list \
  --query "group_by([].{LicenseType:licenseType, OS:storageProfile.osDisk.osType}, &LicenseType)" \
  --output json

# Find all RHEL VMs not using BYOS
az vm list \
  --query "[?contains(storageProfile.imageReference.offer, 'RHEL') && licenseType!='RHEL_BYOS'].{Name:name, RG:resourceGroup, Offer:storageProfile.imageReference.offer, LicenseType:licenseType}" \
  --output table

# --- Find Spot VM opportunities ---
# Identify VMs running workloads suitable for Spot (batch/dev workloads by tag)
az vm list \
  --show-details \
  --query "[?tags.environment=='development' && priority!='Spot'].{Name:name, RG:resourceGroup, Size:hardwareProfile.vmSize, State:powerState}" \
  --output table

# --- Dev/Test subscription check ---
# Verify subscription offer type (Dev/Test subscriptions have special offer IDs)
az account show \
  --query "{Name:name, SubscriptionId:id, State:state, CloudName:environmentName}" \
  --output json
```
