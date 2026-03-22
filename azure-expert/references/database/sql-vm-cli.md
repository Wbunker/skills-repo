# SQL Server on Azure VMs — CLI Reference
For service concepts, see [sql-vm-capabilities.md](sql-vm-capabilities.md).

## SQL VM Resource Provider

```bash
# --- Register SQL IaaS Extension (existing VM) ---
# Full mode (recommended; enables all SQL IaaS features)
az sql vm create \
  --name mySQLVM \
  --resource-group myRG \
  --location eastus \
  --license-type PAYG \             # PAYG | AHUB (Azure Hybrid Benefit) | DR (free DR replica)
  --sql-mgmt-type Full \            # Full | LightWeight | NoAgent
  --image-sku Enterprise            # Developer | Express | Standard | Enterprise | Web

# Register existing VM (without deploying new image)
az sql vm create \
  --name myExistingVM \
  --resource-group myRG \
  --location eastus \
  --license-type AHUB \
  --sql-mgmt-type Full

# --- List SQL VMs ---
az sql vm list \
  --resource-group myRG \
  --output table

az sql vm list \
  --output table                    # All SQL VMs in subscription

# --- Show SQL VM Details ---
az sql vm show \
  --name mySQLVM \
  --resource-group myRG \
  --expand '*'                      # Include all nested properties

# --- Update SQL VM ---
# Switch licensing (PAYG ↔ AHUB)
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --license-type AHUB

# Change management mode
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --sql-mgmt-type Full

# Configure automated backup
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --backup-schedule-type Manual \   # Manual | Automated
  --full-backup-frequency Weekly \  # Daily | Weekly
  --full-backup-start-time 2 \      # Hour (UTC) for full backup
  --full-backup-window-hours 4 \    # Window duration in hours
  --log-backup-frequency 60 \       # Log backup interval in minutes
  --retention-period 14 \           # Days
  --storage-account-url https://mystorageaccount.blob.core.windows.net/ \
  --storage-key <storage-key> \
  --enable-auto-backup true

# Configure automated patching
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --day-of-week Sunday \
  --maintenance-window-start-hour 2 \
  --maintenance-window-duration 120 \  # Minutes
  --enable-auto-patching true

# --- Delete SQL VM Registration (does not delete underlying VM) ---
az sql vm delete \
  --name mySQLVM \
  --resource-group myRG --yes
```

---

## SQL VM Availability Group (AG) Group

```bash
# --- Create SQL VM Group (WSFC) ---
az sql vm group create \
  --name mySQLVMGroup \
  --resource-group myRG \
  --location eastus \
  --image-offer SQL2022-WS2022 \
  --image-sku Enterprise \
  --domain-fqdn contoso.local \
  --operator-acc "CONTOSO\\SQLOperator" \
  --bootstrap-acc "CONTOSO\\SQLBootstrap" \
  --service-acc "CONTOSO\\SQLService" \
  --sa-key <storage-account-key> \
  --storage-account-url https://mystorageaccount.blob.core.windows.net/ \
  --cluster-subnet-type SingleSubnet   # SingleSubnet | MultiSubnet

# --- Add SQL VMs to Group ---
az sql vm add-to-group \
  --name mySQLVM1 \
  --resource-group myRG \
  --sqlvm-group mySQLVMGroup \
  --bootstrap-acc-pwd <password> \
  --operator-acc-pwd <password> \
  --service-acc-pwd <password>

az sql vm add-to-group \
  --name mySQLVM2 \
  --resource-group myRG \
  --sqlvm-group mySQLVMGroup \
  --bootstrap-acc-pwd <password> \
  --operator-acc-pwd <password> \
  --service-acc-pwd <password>

# --- List SQL VMs in Group ---
az sql vm list \
  --resource-group myRG \
  --query "[?sqlVirtualMachineGroup!=null].[name, sqlVirtualMachineGroup.id]" \
  --output table

# --- Show Group Details ---
az sql vm group show \
  --name mySQLVMGroup \
  --resource-group myRG

# --- List All SQL VM Groups ---
az sql vm group list \
  --resource-group myRG \
  --output table

# --- Create Availability Group Listener (via az sql vm group ag-listener) ---
az sql vm group ag-listener create \
  --name myAGListener \
  --resource-group myRG \
  --ag-name myAG \
  --group-name mySQLVMGroup \
  --ip-address 10.0.1.100 \
  --load-balancer /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Network/loadBalancers/mySQLLB \
  --probe-port 59999 \
  --subnet /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet \
  --sqlvms mySQLVM1 mySQLVM2

# --- Show AG Listener ---
az sql vm group ag-listener show \
  --name myAGListener \
  --resource-group myRG \
  --group-name mySQLVMGroup

# --- List AG Listeners ---
az sql vm group ag-listener list \
  --resource-group myRG \
  --group-name mySQLVMGroup \
  --output table
```

---

## Deploying SQL Server VM from Marketplace

```bash
# --- List SQL Server VM Images ---
az vm image list \
  --publisher MicrosoftSQLServer \
  --all \
  --output table | head -50

# List specific SQL Server version offers
az vm image list-offers \
  --publisher MicrosoftSQLServer \
  --location eastus \
  --output table

# List SKUs for SQL 2022 on Windows Server 2022
az vm image list-skus \
  --publisher MicrosoftSQLServer \
  --offer SQL2022-WS2022 \
  --location eastus \
  --output table

# --- Deploy SQL Server VM from Marketplace ---
# Create VM with SQL Server 2022 Enterprise on Windows Server 2022
az vm create \
  --name mySQLVM \
  --resource-group myRG \
  --location eastus \
  --image MicrosoftSQLServer:SQL2022-WS2022:enterprise:latest \
  --size Standard_E16bds_v5 \       # Memory-optimized; local NVMe for TempDB
  --admin-username azureuser \
  --admin-password 'P@ssw0rd123!' \
  --vnet-name myVNet \
  --subnet mySubnet \
  --nsg-name mySQLNSG \
  --accelerated-networking true \   # Required for lowest latency cluster traffic
  --public-ip-sku Standard

# --- Configure Disks for SQL Server Best Practice ---
# Add Premium SSD for SQL data files (ReadOnly caching)
az vm disk attach \
  --vm-name mySQLVM \
  --resource-group myRG \
  --new \
  --name mySQLDataDisk \
  --size-gb 1024 \
  --sku Premium_LRS \
  --lun 0 \
  --caching ReadOnly

# Add Premium SSD for SQL log files (No caching)
az vm disk attach \
  --vm-name mySQLVM \
  --resource-group myRG \
  --new \
  --name mySQLLogDisk \
  --size-gb 512 \
  --sku Premium_LRS \
  --lun 1 \
  --caching None

# Immediately register with SQL IaaS extension after VM creation
az sql vm create \
  --name mySQLVM \
  --resource-group myRG \
  --location eastus \
  --license-type PAYG \
  --sql-mgmt-type Full \
  --image-sku Enterprise
```

---

## Storage Optimization via SQL IaaS Extension

```bash
# --- Configure Storage via SQL VM Resource ---
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --data-path 'F:\SQLData' \
  --log-path 'G:\SQLLog' \
  --temp-db-path 'D:\SQLTempDB' \   # D: is local NVMe on Ev5 / Ebds_v5
  --disk-count 2 \
  --disk-configuration-type NEW     # NEW | EXTEND | ADD

# --- View SQL VM Storage Configuration ---
az sql vm show \
  --name mySQLVM \
  --resource-group myRG \
  --query storageConfigurationSettings
```

---

## SQL Assessment

```bash
# --- Run SQL Best Practice Assessment ---
az sql vm start-assessment \
  --name mySQLVM \
  --resource-group myRG

# --- Enable Scheduled Assessment ---
az sql vm update \
  --name mySQLVM \
  --resource-group myRG \
  --assessment-weekly-interval 1 \  # Run weekly
  --assessment-day-of-week Sunday \
  --assessment-start-time-local 02:00 \
  --workspace-rg myRG \
  --workspace-name myLogAnalyticsWorkspace \
  --enable-assessment true
```

---

## Network Security for SQL Server VMs

```bash
# --- Create NSG Rules for SQL Server ---
# Allow SQL Server from app subnet
az network nsg rule create \
  --nsg-name mySQLNSG \
  --resource-group myRG \
  --name AllowSQLFromApp \
  --priority 100 \
  --protocol Tcp \
  --source-address-prefixes 10.0.2.0/24 \  # App subnet
  --destination-port-ranges 1433 \
  --access Allow

# Allow AG endpoint (mirroring traffic between cluster nodes)
az network nsg rule create \
  --nsg-name mySQLNSG \
  --resource-group myRG \
  --name AllowAGEndpoint \
  --priority 110 \
  --protocol Tcp \
  --source-address-prefixes 10.0.1.0/24 \  # SQL subnet (inter-node)
  --destination-port-ranges 5022 \
  --access Allow

# Allow WSFC (cluster communication)
az network nsg rule create \
  --nsg-name mySQLNSG \
  --resource-group myRG \
  --name AllowWSFC \
  --priority 120 \
  --protocol Tcp \
  --source-address-prefixes 10.0.1.0/24 \
  --destination-port-ranges 1433 3343 \
  --access Allow
```
