# Azure Virtual Machines — CLI Reference

For service concepts, see [vms-capabilities.md](vms-capabilities.md).

## VM — Lifecycle

```bash
# --- Create VM ---
# Create a simple Linux VM with SSH key auth
az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --vnet-name myVNet \
  --subnet mySubnet \
  --public-ip-address "" \
  --nsg myNSG \
  --os-disk-size-gb 128 \
  --storage-sku Premium_LRS \
  --zone 1 \
  --tags Environment=prod Owner=platform

# Create a Windows VM with password auth
az vm create \
  --resource-group myRG \
  --name myWinVM \
  --image Win2022Datacenter \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --admin-password 'P@ssw0rd123!' \
  --os-disk-size-gb 256 \
  --storage-sku Premium_LRS \
  --zone 2

# Create VM with user-assigned managed identity
az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --assign-identity /subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity \
  --no-wait

# Create VM with custom data (cloud-init)
az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D2s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --custom-data cloud-init.yaml

# Create VM with Availability Zone
az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --zone 1

# Create VM in Availability Set
az vm availability-set create \
  --resource-group myRG \
  --name myAvSet \
  --platform-fault-domain-count 2 \
  --platform-update-domain-count 5

az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --availability-set myAvSet

# Create Spot VM
az vm create \
  --resource-group myRG \
  --name mySpotVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price 0.05

# --- Start / Stop / Deallocate ---
az vm start --resource-group myRG --name myVM
az vm stop --resource-group myRG --name myVM           # OS shutdown; still billed
az vm deallocate --resource-group myRG --name myVM     # Release compute; stops billing
az vm restart --resource-group myRG --name myVM
az vm delete --resource-group myRG --name myVM --yes

# Deallocate all VMs in a resource group
az vm deallocate --ids $(az vm list -g myRG --query "[].id" -o tsv)

# --- List VMs ---
az vm list --output table
az vm list --resource-group myRG --output table
az vm list --query "[?powerState=='VM running']" --output table
```

---

## VM — Information and Status

```bash
# Show VM details
az vm show --resource-group myRG --name myVM
az vm show --resource-group myRG --name myVM --output json

# Get power state and instance view
az vm get-instance-view --resource-group myRG --name myVM
az vm get-instance-view --resource-group myRG --name myVM \
  --query "instanceView.statuses[?starts_with(code,'PowerState/')].displayStatus" \
  --output tsv

# List VM sizes available in a region
az vm list-sizes --location eastus --output table

# List VM sizes available in an availability zone
az vm list-sizes --location eastus --query "[?numberOfCores>=8]" --output table

# List all available marketplace images
az vm image list --output table
az vm image list --publisher Canonical --all --output table
az vm image list --location eastus --publisher MicrosoftWindowsServer --offer WindowsServer --sku 2022-datacenter-g2 --all

# Show a specific image
az vm image show \
  --location eastus \
  --publisher Canonical \
  --offer 0001-com-ubuntu-server-jammy \
  --sku 22_04-lts-gen2 \
  --version latest
```

---

## VM — Updates and Modifications

```bash
# Resize a VM (must be deallocated first for some size changes)
az vm resize \
  --resource-group myRG \
  --name myVM \
  --size Standard_D8s_v5

# Update VM properties
az vm update \
  --resource-group myRG \
  --name myVM \
  --set tags.CostCenter=engineering

# Open a port in the NSG (creates inbound rule)
az vm open-port \
  --resource-group myRG \
  --name myVM \
  --port 443 \
  --priority 1001

# Enable accelerated networking on a NIC
az network nic update \
  --resource-group myRG \
  --name myVMNic \
  --accelerated-networking true
```

---

## VM — Extensions

```bash
# List available extensions
az vm extension image list --location eastus --output table
az vm extension image list --location eastus --publisher Microsoft.Azure.Monitor --output table

# Install Azure Monitor Agent
az vm extension set \
  --resource-group myRG \
  --vm-name myVM \
  --name AzureMonitorLinuxAgent \
  --publisher Microsoft.Azure.Monitor \
  --version 1.0 \
  --enable-auto-upgrade true

# Install Custom Script Extension (Linux)
az vm extension set \
  --resource-group myRG \
  --vm-name myVM \
  --name CustomScript \
  --publisher Microsoft.Azure.Extensions \
  --settings '{"fileUris":["https://mystorageaccount.blob.core.windows.net/scripts/setup.sh"],"commandToExecute":"bash setup.sh"}'

# List installed extensions
az vm extension list --resource-group myRG --vm-name myVM --output table

# Delete an extension
az vm extension delete \
  --resource-group myRG \
  --vm-name myVM \
  --name CustomScript
```

---

## VM — Disks

```bash
# Create a managed disk
az disk create \
  --resource-group myRG \
  --name myDataDisk \
  --size-gb 512 \
  --sku Premium_LRS \
  --zone 1 \
  --os-type Linux

# Attach an existing managed disk to a VM
az vm disk attach \
  --resource-group myRG \
  --vm-name myVM \
  --name myDataDisk \
  --lun 0

# Detach a disk
az vm disk detach \
  --resource-group myRG \
  --vm-name myVM \
  --name myDataDisk

# Create a disk and attach in one command
az vm disk attach \
  --resource-group myRG \
  --vm-name myVM \
  --new \
  --name myNewDataDisk \
  --size-gb 256 \
  --sku Premium_LRS

# Update disk size (requires disk to be detached or VM deallocated for Standard; Premium supports online resize)
az disk update \
  --resource-group myRG \
  --name myDataDisk \
  --size-gb 1024

# Enable encryption at host
az vm update \
  --resource-group myRG \
  --name myVM \
  --set securityProfile.encryptionAtHost=true
```

---

## VM — Capture and Snapshot

```bash
# Generalize (sysprep) and capture a VM image
az vm generalize --resource-group myRG --name myVM
az vm capture \
  --resource-group myRG \
  --name myVM \
  --vhd-name-prefix myVMImage \
  --overwrite

# Create a snapshot of an OS or data disk
az snapshot create \
  --resource-group myRG \
  --name myVMSnapshot \
  --source /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRG/providers/Microsoft.Compute/disks/myOsDisk \
  --sku Premium_LRS

# Copy snapshot to another region
az snapshot create \
  --resource-group myRG \
  --name myVMSnapshotCopy \
  --source /subscriptions/.../snapshots/myVMSnapshot \
  --location westeurope

# Create a disk from a snapshot
az disk create \
  --resource-group myRG \
  --name myRestoredDisk \
  --source myVMSnapshot \
  --sku Premium_LRS
```

---

## VM — Managed Identity and RBAC

```bash
# Assign system-assigned managed identity
az vm identity assign \
  --resource-group myRG \
  --name myVM

# Assign user-assigned managed identity
az vm identity assign \
  --resource-group myRG \
  --name myVM \
  --identities /subscriptions/.../userAssignedIdentities/myIdentity

# Show VM identity
az vm identity show --resource-group myRG --name myVM

# Grant the VM's managed identity access to a Key Vault
vmPrincipalId=$(az vm show --resource-group myRG --name myVM --query identity.principalId -o tsv)
az keyvault set-policy \
  --name myKeyVault \
  --object-id $vmPrincipalId \
  --secret-permissions get list
```

---

## VM — Serial Console and Diagnostics

```bash
# Enable boot diagnostics (required for serial console and screenshots)
az vm boot-diagnostics enable \
  --resource-group myRG \
  --name myVM

# Get serial console log (boot diagnostics)
az vm boot-diagnostics get-boot-log \
  --resource-group myRG \
  --name myVM

# Run a command on a VM without SSH (Run Command)
az vm run-command invoke \
  --resource-group myRG \
  --name myVM \
  --command-id RunShellScript \
  --scripts "systemctl status nginx"

# Run Command with inline script
az vm run-command invoke \
  --resource-group myRG \
  --name myVM \
  --command-id RunShellScript \
  --scripts @setup.sh

# List available run commands
az vm run-command list --location eastus --output table
```
