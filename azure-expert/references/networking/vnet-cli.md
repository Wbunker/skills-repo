# Azure Virtual Network — CLI Reference

All commands use the `az` CLI. Set defaults with `az configure --defaults group=<rg> location=<region>` to reduce repetition.

---

## VNet Operations

```bash
# Create a VNet with a specific address space
az network vnet create \
  --name myVNet \
  --resource-group myRG \
  --location eastus \
  --address-prefixes 10.0.0.0/16 \
  --tags Environment=Prod Team=Platform

# Add a second address space to an existing VNet
az network vnet update \
  --name myVNet \
  --resource-group myRG \
  --add addressSpace.addressPrefixes "10.1.0.0/16"

# List all VNets in a resource group
az network vnet list \
  --resource-group myRG \
  --output table

# Show VNet details (address space, subnets, peerings)
az network vnet show \
  --name myVNet \
  --resource-group myRG

# Check if two address spaces overlap
az network vnet check-ip-address \
  --name myVNet \
  --resource-group myRG \
  --ip-address 10.0.1.4

# Delete a VNet (will fail if subnets contain resources)
az network vnet delete \
  --name myVNet \
  --resource-group myRG
```

---

## Subnet Operations

```bash
# Create a subnet
az network vnet subnet create \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --address-prefixes 10.0.1.0/24

# Create a subnet with NSG and route table
az network vnet subnet create \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --address-prefixes 10.0.2.0/24 \
  --network-security-group myNSG \
  --route-table myRouteTable

# Create a delegated subnet for App Service VNet Integration
az network vnet subnet create \
  --name appServiceSubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --address-prefixes 10.0.3.0/24 \
  --delegations Microsoft.Web/serverFarms

# Update subnet: attach NSG, route table, or add service endpoints
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --network-security-group myNSG \
  --route-table myRouteTable \
  --service-endpoints Microsoft.Storage Microsoft.Sql

# Update subnet: attach NAT Gateway
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --nat-gateway myNATGateway

# List subnets in a VNet
az network vnet subnet list \
  --vnet-name myVNet \
  --resource-group myRG \
  --output table

# Delete a subnet
az network vnet subnet delete \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG
```

---

## Network Security Groups (NSGs)

```bash
# Create an NSG
az network nsg create \
  --name myNSG \
  --resource-group myRG \
  --location eastus

# Create an inbound allow rule (lower priority = higher precedence)
az network nsg rule create \
  --nsg-name myNSG \
  --resource-group myRG \
  --name AllowHTTPS \
  --priority 100 \
  --direction Inbound \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 443 \
  --access Allow

# Create a rule denying all inbound SSH from internet
az network nsg rule create \
  --nsg-name myNSG \
  --resource-group myRG \
  --name DenySSHFromInternet \
  --priority 200 \
  --direction Inbound \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --destination-port-ranges 22 \
  --access Deny

# Create a rule using Application Security Groups (ASGs)
az network nsg rule create \
  --nsg-name myNSG \
  --resource-group myRG \
  --name AllowWebToDb \
  --priority 300 \
  --direction Inbound \
  --source-asgs myWebASG \
  --destination-asgs myDbASG \
  --destination-port-ranges 1433 \
  --protocol Tcp \
  --access Allow

# Update an existing NSG rule (change priority or access)
az network nsg rule update \
  --nsg-name myNSG \
  --resource-group myRG \
  --name AllowHTTPS \
  --priority 110

# List all NSG rules
az network nsg rule list \
  --nsg-name myNSG \
  --resource-group myRG \
  --output table

# Delete an NSG rule
az network nsg rule delete \
  --nsg-name myNSG \
  --resource-group myRG \
  --name AllowHTTPS

# Create Application Security Group
az network asg create \
  --name myWebASG \
  --resource-group myRG

# Configure NSG flow logs (v2)
az network watcher flow-log create \
  --name myFlowLog \
  --nsg myNSG \
  --resource-group myRG \
  --storage-account myStorageAccount \
  --enabled true \
  --format JSON \
  --log-version 2 \
  --retention 90 \
  --traffic-analytics true \
  --workspace myLogAnalyticsWorkspace \
  --workspace-resource-group myRG \
  --interval 10
```

---

## Route Tables (UDRs)

```bash
# Create a route table (disable BGP route propagation for full UDR control)
az network route-table create \
  --name myRouteTable \
  --resource-group myRG \
  --location eastus \
  --disable-bgp-route-propagation true

# Add a route: force internet traffic to Azure Firewall
az network route-table route create \
  --route-table-name myRouteTable \
  --resource-group myRG \
  --name ForceInternetToFirewall \
  --address-prefix 0.0.0.0/0 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.0.4  # Azure Firewall private IP

# Add a route: specific CIDR to an NVA
az network route-table route create \
  --route-table-name myRouteTable \
  --resource-group myRG \
  --name RouteToOnPrem \
  --address-prefix 192.168.0.0/16 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.0.5

# Add a route: send traffic to internet directly (bypass NVA)
az network route-table route create \
  --route-table-name myRouteTable \
  --resource-group myRG \
  --name AllowDirectInternet \
  --address-prefix 13.107.4.0/24 \
  --next-hop-type Internet

# List routes in a route table
az network route-table route list \
  --route-table-name myRouteTable \
  --resource-group myRG \
  --output table

# Show effective routes on a NIC (actual routing, including system routes)
az network nic show-effective-route-table \
  --name myNIC \
  --resource-group myRG \
  --output table

# Associate route table with a subnet
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --route-table myRouteTable
```

---

## VNet Peering

```bash
# Create peering from VNet A to VNet B (must also create reverse)
az network vnet peering create \
  --name VNetA-to-VNetB \
  --vnet-name VNetA \
  --resource-group myRG \
  --remote-vnet VNetB \
  --allow-vnet-access true

# Create the reverse peering (VNet B to VNet A)
az network vnet peering create \
  --name VNetB-to-VNetA \
  --vnet-name VNetB \
  --resource-group myRG \
  --remote-vnet VNetA \
  --allow-vnet-access true

# Hub-spoke peering: hub allows gateway transit, spoke uses remote gateway
# Hub side (allows transit through VPN/ER Gateway):
az network vnet peering create \
  --name Hub-to-Spoke \
  --vnet-name HubVNet \
  --resource-group myRG \
  --remote-vnet SpokeVNet \
  --allow-vnet-access true \
  --allow-gateway-transit true \
  --allow-forwarded-traffic true

# Spoke side (uses hub's gateway):
az network vnet peering create \
  --name Spoke-to-Hub \
  --vnet-name SpokeVNet \
  --resource-group myRG \
  --remote-vnet HubVNet \
  --allow-vnet-access true \
  --use-remote-gateways true \
  --allow-forwarded-traffic true

# List peerings for a VNet
az network vnet peering list \
  --vnet-name myVNet \
  --resource-group myRG \
  --output table

# Show peering state (Connected / Disconnected / Initiated)
az network vnet peering show \
  --name VNetA-to-VNetB \
  --vnet-name VNetA \
  --resource-group myRG

# Delete a peering
az network vnet peering delete \
  --name VNetA-to-VNetB \
  --vnet-name VNetA \
  --resource-group myRG
```

---

## Private Endpoints

```bash
# Create a private endpoint for Azure Storage Blob
az network private-endpoint create \
  --name myBlobPE \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/myStorage \
  --group-id blob \
  --connection-name myBlobConnection

# Create Private DNS Zone for Blob Storage
az network private-dns zone create \
  --name privatelink.blob.core.windows.net \
  --resource-group myRG

# Link Private DNS Zone to VNet (enable auto-registration if needed)
az network private-dns link vnet create \
  --name myDNSLink \
  --resource-group myRG \
  --zone-name privatelink.blob.core.windows.net \
  --virtual-network myVNet \
  --registration-enabled false

# Create DNS zone group (auto-creates DNS record when PE is created)
az network private-endpoint dns-zone-group create \
  --endpoint-name myBlobPE \
  --resource-group myRG \
  --name myZoneGroup \
  --private-dns-zone privatelink.blob.core.windows.net \
  --zone-name blob

# List private endpoints in a resource group
az network private-endpoint list \
  --resource-group myRG \
  --output table

# Show private endpoint details (includes private IP)
az network private-endpoint show \
  --name myBlobPE \
  --resource-group myRG
```

---

## NAT Gateway

```bash
# Create a public IP for NAT Gateway
az network public-ip create \
  --name myNATPublicIP \
  --resource-group myRG \
  --sku Standard \
  --allocation-method Static \
  --zone 1 2 3

# Create NAT Gateway
az network nat gateway create \
  --name myNATGateway \
  --resource-group myRG \
  --location eastus \
  --sku Standard \
  --idle-timeout 10 \
  --zone 1

# Associate public IP with NAT Gateway
az network nat gateway update \
  --name myNATGateway \
  --resource-group myRG \
  --public-ip-addresses myNATPublicIP

# Attach NAT Gateway to a subnet
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --nat-gateway myNATGateway

# Remove NAT Gateway from subnet
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --nat-gateway ""
```

---

## Service Endpoints

```bash
# Enable service endpoints on a subnet (multiple services)
az network vnet subnet update \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --service-endpoints Microsoft.Storage Microsoft.Sql Microsoft.KeyVault

# List service endpoints configured on a subnet
az network vnet subnet show \
  --name mySubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --query serviceEndpoints

# Add VNet rule to a Storage Account (restrict access to subnet)
az storage account network-rule add \
  --account-name myStorage \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet

# Show available service endpoint types by region
az network vnet list-endpoint-services \
  --location eastus \
  --output table
```
