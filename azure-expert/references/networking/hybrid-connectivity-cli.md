# Azure Hybrid Connectivity — CLI Reference

---

## ExpressRoute

```bash
# Create an ExpressRoute circuit
az network express-route create \
  --name myERCircuit \
  --resource-group myRG \
  --location eastus \
  --bandwidth 1000 \
  --peering-location "Silicon Valley" \
  --provider "Equinix" \
  --sku-family MeteredData \
  --sku-tier Standard

# Create ExpressRoute circuit (Premium tier, unlimited data)
az network express-route create \
  --name myERCircuitPremium \
  --resource-group myRG \
  --location eastus \
  --bandwidth 10000 \
  --peering-location "Ashburn" \
  --provider "Equinix" \
  --sku-family UnlimitedData \
  --sku-tier Premium

# List all ExpressRoute circuits
az network express-route list \
  --resource-group myRG \
  --output table

# Show circuit details (including service key for provider)
az network express-route show \
  --name myERCircuit \
  --resource-group myRG

# Get service key (share with connectivity provider to provision circuit)
az network express-route show \
  --name myERCircuit \
  --resource-group myRG \
  --query serviceKey \
  --output tsv

# Configure Azure Private Peering on the circuit
az network express-route peering create \
  --circuit-name myERCircuit \
  --resource-group myRG \
  --peering-type AzurePrivatePeering \
  --peer-asn 65020 \
  --primary-peer-subnet 192.168.100.0/30 \
  --secondary-peer-subnet 192.168.100.4/30 \
  --vlan-id 100

# Configure Microsoft Peering (for M365 / Azure PaaS public endpoints)
az network express-route peering create \
  --circuit-name myERCircuit \
  --resource-group myRG \
  --peering-type MicrosoftPeering \
  --peer-asn 65020 \
  --primary-peer-subnet 192.168.200.0/30 \
  --secondary-peer-subnet 192.168.200.4/30 \
  --vlan-id 200 \
  --advertised-public-prefixes 203.0.113.0/24 \
  --customer-asn 65020 \
  --routing-registry-name ARIN

# List peerings on a circuit
az network express-route peering list \
  --circuit-name myERCircuit \
  --resource-group myRG \
  --output table

# Create ExpressRoute Virtual Network Gateway (zone-redundant)
az network public-ip create \
  --name myERGWPublicIP \
  --resource-group myRG \
  --sku Standard \
  --zone 1 2 3

az network vnet-gateway create \
  --name myERGateway \
  --resource-group myRG \
  --vnet myHubVNet \
  --gateway-type ExpressRoute \
  --sku ErGw2AZ \
  --public-ip-addresses myERGWPublicIP \
  --location eastus \
  --no-wait

# Connect ExpressRoute circuit to VNet Gateway
az network vpn-connection create \
  --name myERConnection \
  --resource-group myRG \
  --vnet-gateway1 myERGateway \
  --express-route-circuit2 myERCircuit \
  --routing-weight 10

# Enable Global Reach between two ExpressRoute circuits
az network express-route peering connection create \
  --circuit-name myERCircuit1 \
  --resource-group myRG \
  --peering-name AzurePrivatePeering \
  --name GlobalReachToCircuit2 \
  --peer-circuit /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/expressRouteCircuits/myERCircuit2 \
  --address-prefix 192.168.10.0/29

# Show circuit provider provisioning state
az network express-route show \
  --name myERCircuit \
  --resource-group myRG \
  --query "{serviceProviderProvisioningState:serviceProviderProvisioningState, circuitProvisioningState:circuitProvisioningState}"
```

---

## VPN Gateway

```bash
# Create a VPN Gateway (route-based, zone-redundant) — deployment takes 30-45 min
az network public-ip create \
  --name myVPNGWPublicIP \
  --resource-group myRG \
  --sku Standard \
  --zone 1 2 3

az network vnet-gateway create \
  --name myVPNGateway \
  --resource-group myRG \
  --vnet myHubVNet \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw2AZ \
  --public-ip-addresses myVPNGWPublicIP \
  --location eastus \
  --no-wait

# Create active-active VPN Gateway (requires two public IPs and BGP)
az network public-ip create \
  --name myVPNGWPublicIP2 \
  --resource-group myRG \
  --sku Standard

az network vnet-gateway create \
  --name myVPNGatewayAA \
  --resource-group myRG \
  --vnet myHubVNet \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw2AZ \
  --public-ip-addresses myVPNGWPublicIP myVPNGWPublicIP2 \
  --asn 65010 \
  --bgp-peering-address 10.100.255.4 \
  --location eastus \
  --no-wait

# Check VPN Gateway provisioning status
az network vnet-gateway show \
  --name myVPNGateway \
  --resource-group myRG \
  --query provisioningState \
  --output tsv

# Create a Local Network Gateway (represents on-premises VPN device)
az network local-gateway create \
  --name myLocalGateway \
  --resource-group myRG \
  --gateway-ip-address 203.0.113.10 \
  --local-address-prefixes 192.168.0.0/16 10.10.0.0/16 \
  --location eastus

# Create Local Network Gateway with BGP
az network local-gateway create \
  --name myLocalGatewayBGP \
  --resource-group myRG \
  --gateway-ip-address 203.0.113.10 \
  --local-address-prefixes 0.0.0.0/0 \
  --bgp-peering-address 192.168.1.1 \
  --asn 65020 \
  --location eastus

# Create Site-to-Site VPN connection
az network vpn-connection create \
  --name myS2SConnection \
  --resource-group myRG \
  --vnet-gateway1 myVPNGateway \
  --local-gateway2 myLocalGateway \
  --shared-key "SuperSecretPreSharedKey123!" \
  --connection-type IPsec \
  --enable-bgp false

# Create S2S connection with BGP
az network vpn-connection create \
  --name myS2SConnectionBGP \
  --resource-group myRG \
  --vnet-gateway1 myVPNGateway \
  --local-gateway2 myLocalGatewayBGP \
  --shared-key "SuperSecretPreSharedKey123!" \
  --connection-type IPsec \
  --enable-bgp true

# Configure IKEv2 custom policy on connection
az network vpn-connection ipsec-policy add \
  --connection-name myS2SConnection \
  --resource-group myRG \
  --ike-encryption AES256 \
  --ike-integrity SHA256 \
  --dh-group DHGroup14 \
  --ipsec-encryption AES256 \
  --ipsec-integrity SHA256 \
  --pfs-group PFS14 \
  --sa-lifetime 3600 \
  --sa-max-size 102400000

# Configure Point-to-Site VPN (OpenVPN with Entra ID auth)
az network vnet-gateway update \
  --name myVPNGateway \
  --resource-group myRG \
  --client-protocol OpenVPN \
  --address-prefixes 172.16.0.0/24 \
  --aad-tenant https://login.microsoftonline.com/<tenant-id>/ \
  --aad-audience 41b23e61-6c1e-4545-b367-cd054e0ed4b4 \
  --aad-issuer https://sts.windows.net/<tenant-id>/

# List all VPN connections
az network vpn-connection list \
  --resource-group myRG \
  --output table

# Show VPN connection status
az network vpn-connection show \
  --name myS2SConnection \
  --resource-group myRG \
  --query connectionStatus

# Get shared key for a connection
az network vpn-connection shared-key show \
  --connection-name myS2SConnection \
  --resource-group myRG

# Reset VPN connection (force re-establishment)
az network vpn-connection reset \
  --name myS2SConnection \
  --resource-group myRG

# Download VPN client configuration package (P2S)
az network vnet-gateway vpn-client generate \
  --name myVPNGateway \
  --resource-group myRG \
  --authentication-method EAPTLS
```

---

## Azure Virtual WAN

```bash
# Create a Virtual WAN (Standard tier)
az network vwan create \
  --name myVirtualWAN \
  --resource-group myRG \
  --location eastus \
  --type Standard

# List Virtual WANs
az network vwan list \
  --resource-group myRG \
  --output table

# Create a Virtual Hub in East US
az network vhub create \
  --name myEastUSHub \
  --resource-group myRG \
  --location eastus \
  --vwan myVirtualWAN \
  --address-prefix 10.100.0.0/23 \
  --sku Standard \
  --no-wait

# Create a Virtual Hub in West Europe (multi-region)
az network vhub create \
  --name myEuropeHub \
  --resource-group myRG \
  --location westeurope \
  --vwan myVirtualWAN \
  --address-prefix 10.101.0.0/23 \
  --sku Standard \
  --no-wait

# Show hub provisioning status
az network vhub show \
  --name myEastUSHub \
  --resource-group myRG \
  --query provisioningState

# Connect a spoke VNet to the hub
az network vhub connection create \
  --name SpokeVNet-Connection \
  --resource-group myRG \
  --vhub-name myEastUSHub \
  --remote-vnet /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/SpokeVNet \
  --internet-security true

# List VNet connections to a hub
az network vhub connection list \
  --vhub-name myEastUSHub \
  --resource-group myRG \
  --output table

# Create a VPN Gateway in the hub (for branch S2S connections)
az network vpn-gateway create \
  --name myHubVPNGateway \
  --resource-group myRG \
  --location eastus \
  --vhub myEastUSHub \
  --no-wait

# Create a VPN site (branch office)
az network vpn-site create \
  --name myBranchSite \
  --resource-group myRG \
  --location eastus \
  --virtual-wan myVirtualWAN \
  --ip-address 203.0.113.20 \
  --device-vendor Cisco \
  --device-model ASR1001 \
  --link-speed 100 \
  --address-prefixes 10.50.0.0/16

# Connect VPN site to hub
az network vpn-gateway connection create \
  --name myBranchConnection \
  --resource-group myRG \
  --gateway-name myHubVPNGateway \
  --vpn-site /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/vpnSites/myBranchSite \
  --shared-key "BranchPreSharedKey123!"

# Create custom routing table in hub
az network vhub route-table create \
  --name myCustomRouteTable \
  --vhub-name myEastUSHub \
  --resource-group myRG \
  --labels production

# Show effective routes in hub
az network vhub get-effective-routes \
  --name myEastUSHub \
  --resource-group myRG \
  --resource-type HubVirtualNetworkConnection \
  --resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualHubs/myEastUSHub/hubVirtualNetworkConnections/SpokeVNet-Connection

# List all vWAN resources
az network vwan list --output table
az network vhub list --output table
az network vpn-gateway list --resource-group myRG --output table
az network vpn-site list --resource-group myRG --output table
```
