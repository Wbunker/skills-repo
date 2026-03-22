# Windows 365 & Remote Desktop Services — CLI Reference
For service concepts, see [w365-rds-capabilities.md](w365-rds-capabilities.md).

> **Note**: Windows 365 is managed via Microsoft Intune and Microsoft Graph API. There is no `az` CLI support for Windows 365 Cloud PC provisioning or lifecycle management. RDS on Azure is managed using standard `az vm` commands for the underlying VMs plus Windows DSC or PowerShell for RDS role configuration.

## Windows 365 — Microsoft Graph API

```bash
# Windows 365 Cloud PC management is done via Microsoft Graph API
# Endpoint: https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/...

# --- Via az rest (Graph API proxy) ---
# List all Cloud PCs
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs" \
  --resource "https://graph.microsoft.com"

# Get a specific Cloud PC
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs/{cloudPcId}" \
  --resource "https://graph.microsoft.com"

# Reprovision a Cloud PC (factory reset)
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs/{cloudPcId}/reprovision" \
  --resource "https://graph.microsoft.com"

# Restart a Cloud PC
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs/{cloudPcId}/reboot" \
  --resource "https://graph.microsoft.com"

# Get provisioning policies
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/provisioningPolicies" \
  --resource "https://graph.microsoft.com"

# Get supported Cloud PC images
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/supportedRegions" \
  --resource "https://graph.microsoft.com"

# Get Cloud PC connectivity health checks
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/cloudPCs/{cloudPcId}/runHealthChecks" \
  --resource "https://graph.microsoft.com"

# Assign a provisioning policy to a group
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/deviceManagement/virtualEndpoint/provisioningPolicies/{policyId}/assign" \
  --resource "https://graph.microsoft.com" \
  --body '{
    "assignments": [{
      "id": "group-id",
      "target": {
        "@odata.type": "#microsoft.graph.cloudPcManagementGroupAssignmentTarget",
        "groupId": "<entra-group-id>"
      }
    }]
  }'
```

## Windows 365 — PowerShell (Intune / Graph)

```powershell
# Install Microsoft.Graph module
Install-Module Microsoft.Graph -Scope CurrentUser

# Connect with required scopes
Connect-MgGraph -Scopes "CloudPC.ReadWrite.All", "DeviceManagementConfiguration.ReadWrite.All"

# List all Cloud PCs
Get-MgDeviceManagementVirtualEndpointCloudPC | Select-Object DisplayName, Status, UserPrincipalName, ManagedDeviceName

# Get specific Cloud PC
Get-MgDeviceManagementVirtualEndpointCloudPC -CloudPCId "<cloud-pc-id>"

# Reprovision Cloud PC
Invoke-MgReprovisionDeviceManagementVirtualEndpointCloudPC -CloudPCId "<cloud-pc-id>"

# Get provisioning policies
Get-MgDeviceManagementVirtualEndpointProvisioningPolicy

# Create a provisioning policy (Enterprise tier)
New-MgDeviceManagementVirtualEndpointProvisioningPolicy -BodyParameter @{
    displayName = "Engineering Cloud PCs"
    description = "Cloud PCs for engineering team"
    domainJoinConfiguration = @{
        type = "azureADJoin"
    }
    imageId = "MicrosoftWindowsDesktop_windows-ent-cpc_win11-22h2-ent-cpc-os"
    imageType = "gallery"
    onPremisesConnectionId = $null  # null for Microsoft-hosted network
}

# List on-premises network connections (for customer VNet)
Get-MgDeviceManagementVirtualEndpointOnPremisesConnection

# Get supported Cloud PC sizes
Get-MgDeviceManagementVirtualEndpointSupportedRegion
```

## RDS on Azure — VM Infrastructure

```bash
# --- Deploy RDS Session Host VM ---
az vm create \
  --resource-group myRDSRG \
  --name RDSH01 \
  --image Win2022Datacenter \
  --size Standard_D8s_v5 \
  --admin-username rdadmin \
  --admin-password "TempPass123!" \
  --vnet-name myVNet \
  --subnet RDSSubnet \
  --public-ip-address "" \
  --nsg "" \
  --license-type Windows_Server                  # Deploy RDS Session Host VM (hybrid benefit)

az vm create \
  --resource-group myRDSRG \
  --name RDCB01 \
  --image Win2022Datacenter \
  --size Standard_D4s_v5 \
  --admin-username rdadmin \
  --admin-password "TempPass123!" \
  --vnet-name myVNet \
  --subnet RDSSubnet \
  --public-ip-address ""                         # Deploy RD Connection Broker VM

az vm create \
  --resource-group myRDSRG \
  --name RDGW01 \
  --image Win2022Datacenter \
  --size Standard_D4s_v5 \
  --admin-username rdadmin \
  --admin-password "TempPass123!" \
  --vnet-name myVNet \
  --subnet GatewaySubnet \
  --public-ip-address RDGW-PublicIP \
  --public-ip-sku Standard                       # Deploy RD Gateway VM with public IP

# --- Bulk Session Host Creation ---
for i in $(seq 1 5); do
  az vm create \
    --resource-group myRDSRG \
    --name "RDSH0${i}" \
    --image Win2022Datacenter \
    --size Standard_D8s_v5 \
    --admin-username rdadmin \
    --admin-password "TempPass123!" \
    --vnet-name myVNet \
    --subnet RDSSubnet \
    --no-wait \
    --license-type Windows_Server
done
az vm wait --resource-group myRDSRG --name RDSH05 --created   # Wait for last VM

# --- VM Extensions for RDS Role Installation ---
# Install RD-RD-Server role via Custom Script Extension
az vm extension set \
  --resource-group myRDSRG \
  --vm-name RDSH01 \
  --name CustomScriptExtension \
  --publisher Microsoft.Compute \
  --settings '{"commandToExecute": "powershell -Command \"Install-WindowsFeature -Name RDS-RD-Server -IncludeManagementTools\""}'

# --- Domain Join (PowerShell DSC Extension) ---
az vm extension set \
  --resource-group myRDSRG \
  --vm-name RDSH01 \
  --name JsonADDomainExtension \
  --publisher Microsoft.Compute \
  --version 1.3 \
  --settings '{
    "Name": "company.local",
    "OUPath": "OU=RDS,OU=Servers,DC=company,DC=local",
    "User": "company\\domainadmin",
    "Restart": "true",
    "Options": "3"
  }' \
  --protected-settings '{"Password": "DomainAdminPassword123!"}'

# --- Load Balancer for Session Hosts ---
az network lb create \
  --resource-group myRDSRG \
  --name rds-internal-lb \
  --sku Standard \
  --frontend-ip-name RDS-Frontend \
  --private-ip-address 10.0.1.100 \
  --vnet-name myVNet \
  --subnet RDSSubnet \
  --backend-pool-name RDS-Backend               # Internal LB for session host RDP

az network lb probe create \
  --resource-group myRDSRG \
  --lb-name rds-internal-lb \
  --name rdp-probe \
  --protocol Tcp \
  --port 3389

az network lb rule create \
  --resource-group myRDSRG \
  --lb-name rds-internal-lb \
  --name rdp-rule \
  --frontend-ip-name RDS-Frontend \
  --backend-pool-name RDS-Backend \
  --probe-name rdp-probe \
  --protocol Tcp \
  --frontend-port 3389 \
  --backend-port 3389
```

## RDS on Azure — PowerShell Configuration

```powershell
# --- Install RDS Roles (run on designated VMs) ---

# On Connection Broker VM
Install-WindowsFeature -Name RDS-Connection-Broker -IncludeManagementTools

# On Session Host VMs
Install-WindowsFeature -Name RDS-RD-Server -IncludeManagementTools

# On Web Access VM
Install-WindowsFeature -Name RDS-Web-Access -IncludeManagementTools

# On Gateway VM
Install-WindowsFeature -Name RDS-Gateway, RDS-Licensing -IncludeManagementTools

# --- Create RDS Deployment (from Connection Broker) ---
Import-Module RemoteDesktop

New-RDSessionDeployment `
  -ConnectionBroker "RDCB01.company.local" `
  -WebAccessServer "RDWA01.company.local" `
  -SessionHost @("RDSH01.company.local", "RDSH02.company.local", "RDSH03.company.local")

# --- Add Gateway and Licensing ---
Add-RDServer -Server "RDGW01.company.local" -Role RDS-GATEWAY -ConnectionBroker "RDCB01.company.local" -GatewayExternalFqdn "rdgateway.company.com"
Add-RDServer -Server "RDCB01.company.local" -Role RDS-LICENSING -ConnectionBroker "RDCB01.company.local"

# Configure licensing mode
Set-RDLicenseConfiguration `
  -LicenseServer "RDCB01.company.local" `
  -Mode PerUser `
  -ConnectionBroker "RDCB01.company.local"

# --- Create Session Collection ---
New-RDSessionCollection `
  -CollectionName "Standard Desktops" `
  -ConnectionBroker "RDCB01.company.local" `
  -SessionHost @("RDSH01.company.local", "RDSH02.company.local") `
  -CollectionDescription "Standard Windows desktops for office users"

# --- Publish RemoteApp ---
New-RDRemoteApp `
  -CollectionName "Standard Desktops" `
  -DisplayName "Microsoft Excel" `
  -FilePath "C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE" `
  -ConnectionBroker "RDCB01.company.local"

# --- Get Collection Info ---
Get-RDSessionCollection -ConnectionBroker "RDCB01.company.local"
Get-RDUserSession -CollectionName "Standard Desktops" -ConnectionBroker "RDCB01.company.local"

# Disconnect a user session
Disconnect-RDUser -HostServer "RDSH01.company.local" -UnifiedSessionID 3 -Force
```
