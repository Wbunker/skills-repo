# Azure Network Security & Access — CLI Reference

---

## Azure Firewall

```bash
# Create Azure Firewall Premium with policy (in hub VNet)
# First, create the Firewall subnet public IP
az network public-ip create \
  --name myFirewallPublicIP \
  --resource-group myRG \
  --sku Standard \
  --zone 1 2 3

# Create an Azure Firewall Policy (Premium SKU)
az network firewall policy create \
  --name myFirewallPolicy \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --threat-intel-mode Alert \
  --dns-servers 168.63.129.16 \
  --enable-dns-proxy true

# Create Azure Firewall Premium (zone-redundant)
az network firewall create \
  --name myAzureFirewall \
  --resource-group myRG \
  --location eastus \
  --sku AZFW_VNet \
  --tier Premium \
  --firewall-policy myFirewallPolicy \
  --zones 1 2 3

# Configure Firewall IP in hub VNet's AzureFirewallSubnet
az network firewall ip-config create \
  --firewall-name myAzureFirewall \
  --resource-group myRG \
  --name myFirewallIPConfig \
  --vnet-name myHubVNet \
  --subnet AzureFirewallSubnet \
  --public-ip-address myFirewallPublicIP

# Get the firewall private IP (needed for UDR next-hop)
az network firewall show \
  --name myAzureFirewall \
  --resource-group myRG \
  --query ipConfigurations[0].privateIPAddress \
  --output tsv

# Create a rule collection group (required container for rule collections)
az network firewall policy rule-collection-group create \
  --name DefaultRuleCollectionGroup \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --priority 100

# Add a network rule collection (allow internal spoke-to-spoke traffic)
az network firewall policy rule-collection-group collection add-filter-collection \
  --name AllowInternalTraffic \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --rule-collection-group-name DefaultRuleCollectionGroup \
  --collection-priority 100 \
  --action Allow \
  --rule-type NetworkRule \
  --rule-name AllowSpokeToSpoke \
  --source-addresses 10.1.0.0/24 10.2.0.0/24 \
  --destination-addresses 10.1.0.0/24 10.2.0.0/24 \
  --ip-protocols TCP UDP \
  --destination-ports "*"

# Add an application rule collection (allow internet browsing to specific FQDNs)
az network firewall policy rule-collection-group collection add-filter-collection \
  --name AllowInternetAccess \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --rule-collection-group-name DefaultRuleCollectionGroup \
  --collection-priority 200 \
  --action Allow \
  --rule-type ApplicationRule \
  --rule-name AllowWindowsUpdate \
  --source-addresses 10.0.0.0/8 \
  --fqdn-tags WindowsUpdate

# Add an application rule for specific FQDNs
az network firewall policy rule-collection-group collection add-filter-collection \
  --name AllowSpecificFQDNs \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --rule-collection-group-name DefaultRuleCollectionGroup \
  --collection-priority 300 \
  --action Allow \
  --rule-type ApplicationRule \
  --rule-name AllowAzureServices \
  --source-addresses 10.0.0.0/8 \
  --target-fqdns "*.azure.com" "*.microsoft.com" \
  --protocols "Https:443"

# Add a DNAT rule collection (inbound RDP via public IP)
az network firewall policy rule-collection-group collection add-nat-collection \
  --name InboundDNAT \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --rule-collection-group-name DefaultRuleCollectionGroup \
  --collection-priority 50 \
  --action DNAT \
  --rule-name RDPToVM1 \
  --source-addresses "*" \
  --destination-addresses 20.30.40.50 \
  --destination-ports 3389 \
  --ip-protocols TCP \
  --translated-address 10.0.1.4 \
  --translated-port 3389

# List rule collection groups
az network firewall policy rule-collection-group list \
  --policy-name myFirewallPolicy \
  --resource-group myRG \
  --output table

# Show firewall operational state
az network firewall show \
  --name myAzureFirewall \
  --resource-group myRG \
  --query "{name:name, provisioningState:provisioningState, threatIntelMode:threatIntelMode}"

# List all firewalls
az network firewall list \
  --resource-group myRG \
  --output table

# Create a child Firewall Policy (inherits from parent)
az network firewall policy create \
  --name myChildPolicy \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --base-policy /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/firewallPolicies/myFirewallPolicy

# Enable IDPS on Firewall Policy (Premium)
az network firewall policy update \
  --name myFirewallPolicy \
  --resource-group myRG \
  --idps-mode Deny
```

---

## Azure Bastion

```bash
# Create Azure Bastion Standard SKU (with shareable link and native client support)
# First create the public IP for Bastion
az network public-ip create \
  --name myBastionPublicIP \
  --resource-group myRG \
  --sku Standard \
  --zone 1 2 3 \
  --location eastus

# Create Bastion Standard with scale units
az network bastion create \
  --name myBastion \
  --resource-group myRG \
  --location eastus \
  --vnet-name myHubVNet \
  --public-ip-address myBastionPublicIP \
  --sku Standard \
  --scale-units 10 \
  --enable-ip-connect true \
  --enable-shareable-link true \
  --enable-file-copy true \
  --enable-tunneling true

# Create Bastion Basic SKU (minimal cost)
az network bastion create \
  --name myBastionBasic \
  --resource-group myRG \
  --location eastus \
  --vnet-name myHubVNet \
  --public-ip-address myBastionPublicIP2 \
  --sku Basic

# Connect to VM via SSH using Bastion (AAD authentication)
az network bastion ssh \
  --name myBastion \
  --resource-group myRG \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM \
  --auth-type AAD

# Connect to VM via SSH with username and key
az network bastion ssh \
  --name myBastion \
  --resource-group myRG \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM \
  --auth-type ssh-key \
  --username azureuser \
  --ssh-key ~/.ssh/id_rsa

# Open RDP session via Bastion (opens browser)
az network bastion rdp \
  --name myBastion \
  --resource-group myRG \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myWindowsVM

# Create a Bastion tunnel for local RDP/SSH client
az network bastion tunnel \
  --name myBastion \
  --resource-group myRG \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM \
  --resource-port 22 \
  --port 2222
# Then: ssh azureuser@127.0.0.1 -p 2222

# Update Bastion scale units (increase for more concurrent sessions)
az network bastion update \
  --name myBastion \
  --resource-group myRG \
  --scale-units 20

# Show Bastion details
az network bastion show \
  --name myBastion \
  --resource-group myRG

# List all Bastions
az network bastion list \
  --resource-group myRG \
  --output table
```

---

## DDoS Protection

```bash
# Create a DDoS Network Protection plan
az network ddos-protection create \
  --name myDDoSPlan \
  --resource-group myRG \
  --location eastus \
  --sku-name NetworkProtection

# Associate DDoS Network Protection plan with a VNet
az network vnet update \
  --name myVNet \
  --resource-group myRG \
  --ddos-protection true \
  --ddos-protection-plan myDDoSPlan

# Enable DDoS IP Protection on a specific public IP
az network public-ip update \
  --name myPublicIP \
  --resource-group myRG \
  --ddos-protection-mode VirtualNetworkInherited

# Enable DDoS IP Protection (standalone per-IP, no plan required)
az network public-ip update \
  --name myPublicIP \
  --resource-group myRG \
  --ddos-protection-mode Enabled

# Show DDoS protection plan details
az network ddos-protection show \
  --name myDDoSPlan \
  --resource-group myRG

# List all DDoS protection plans
az network ddos-protection list \
  --resource-group myRG \
  --output table

# Check DDoS protection status on a VNet
az network vnet show \
  --name myVNet \
  --resource-group myRG \
  --query "ddosProtectionPlan"

# Create alert for DDoS attack (using Azure Monitor)
az monitor metrics alert create \
  --name DDoSAttackAlert \
  --resource-group myRG \
  --scopes /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/publicIPAddresses/myPublicIP \
  --condition "avg UnderDDoSAttack >= 1" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "Alert when public IP is under DDoS attack"
```

---

## Network Watcher

```bash
# Enable Network Watcher for a region (usually auto-enabled)
az network watcher configure \
  --resource-group NetworkWatcherRG \
  --locations eastus westus \
  --enabled true

# List Network Watchers
az network watcher list \
  --output table

# IP Flow Verify: check if NSG allows/denies a specific flow
az network watcher test-ip-flow \
  --vm myVM \
  --resource-group myRG \
  --direction Inbound \
  --protocol TCP \
  --local-ip 10.0.1.4 \
  --local-port 80 \
  --remote-ip 203.0.113.10 \
  --remote-port 4321

# Next Hop: find next hop for a packet from a VM to a destination IP
az network watcher show-next-hop \
  --vm myVM \
  --resource-group myRG \
  --source-ip 10.0.1.4 \
  --dest-ip 8.8.8.8

# Security Group View: list all effective NSG rules on a VM
az network watcher show-security-group-view \
  --vm myVM \
  --resource-group myRG

# Connection Troubleshoot: test connectivity from VM to endpoint
az network watcher test-connectivity \
  --source-resource myVM \
  --resource-group myRG \
  --dest-resource myTargetVM \
  --dest-resource-group myTargetRG \
  --protocol Tcp \
  --dest-port 443

# Connection Troubleshoot: test VM to external URL
az network watcher test-connectivity \
  --source-resource myVM \
  --resource-group myRG \
  --dest-address "https://www.microsoft.com" \
  --protocol Https

# Create packet capture on a VM
az network watcher packet-capture create \
  --name myPacketCapture \
  --vm myVM \
  --resource-group myRG \
  --storage-account myStorageAccount \
  --time-limit 300 \
  --filters '[{"protocol":"TCP","remoteIPAddress":"0.0.0.0/0","localIPAddress":"10.0.1.4","remotePort":"443"}]'

# Show packet capture status
az network watcher packet-capture show \
  --name myPacketCapture \
  --vm myVM \
  --resource-group myRG

# Stop packet capture
az network watcher packet-capture stop \
  --name myPacketCapture \
  --vm myVM \
  --resource-group myRG

# Get network topology of a VNet
az network watcher show-topology \
  --resource-group myRG \
  --vnet myVNet

# Configure NSG flow logs (version 2 with Traffic Analytics)
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

# Show flow log configuration
az network watcher flow-log show \
  --name myFlowLog \
  --resource-group myRG

# List flow logs for a Network Watcher
az network watcher flow-log list \
  --resource-group myRG \
  --location eastus \
  --output table

# Create Connection Monitor for continuous connectivity testing
az network watcher connection-monitor create \
  --name myConnectionMonitor \
  --resource-group myRG \
  --location eastus \
  --test-group-name myTestGroup \
  --source-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM \
  --dest-address "https://www.microsoft.com" \
  --dest-port 443 \
  --protocol Https \
  --test-config-name HttpsTest \
  --frequency 60 \
  --preferred-ip-version IPv4

# List connection monitors
az network watcher connection-monitor list \
  --resource-group myRG \
  --location eastus \
  --output table

# Troubleshoot VPN Gateway or connection
az network watcher troubleshooting start \
  --resource-group myRG \
  --resource myVPNGateway \
  --resource-type vnetGateway \
  --storage-account myStorageAccount \
  --storage-path https://myStorageAccount.blob.core.windows.net/troubleshoot
```
