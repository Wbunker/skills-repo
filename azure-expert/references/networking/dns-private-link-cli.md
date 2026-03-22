# Azure DNS & Private Link — CLI Reference

---

## Azure DNS (Public Zones)

```bash
# Create a public DNS zone
az network dns zone create \
  --name example.com \
  --resource-group myRG

# List DNS zones in a resource group
az network dns zone list \
  --resource-group myRG \
  --output table

# Show zone details (includes name servers for registrar delegation)
az network dns zone show \
  --name example.com \
  --resource-group myRG \
  --query nameServers

# Get name servers for registrar delegation
az network dns zone show \
  --name example.com \
  --resource-group myRG \
  --query "nameServers" \
  --output tsv

# Add an A record
az network dns record-set a add-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name www \
  --ipv4-address 20.30.40.50 \
  --ttl 300

# Add multiple IPs to an A record set
az network dns record-set a add-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name www \
  --ipv4-address 20.30.40.51

# Add a CNAME record
az network dns record-set cname set-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name mail \
  --cname myapp.azurewebsites.net \
  --ttl 300

# Add a TXT record (SPF)
az network dns record-set txt add-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name "@" \
  --value "v=spf1 include:spf.protection.outlook.com -all"

# Add an MX record
az network dns record-set mx add-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name "@" \
  --exchange "mail.protection.outlook.com" \
  --preference 0

# Create an alias record set (zone apex → Traffic Manager)
az network dns record-set a create \
  --zone-name example.com \
  --resource-group myRG \
  --name "@" \
  --ttl 300 \
  --target-resource /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/trafficManagerProfiles/myTMProfile

# Create an alias record for Front Door (apex)
az network dns record-set a create \
  --zone-name example.com \
  --resource-group myRG \
  --name "@" \
  --ttl 300 \
  --target-resource /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Cdn/profiles/myAFDProfile/afdEndpoints/myEndpoint

# List all record sets in a zone
az network dns record-set list \
  --zone-name example.com \
  --resource-group myRG \
  --output table

# Show a specific record set
az network dns record-set a show \
  --zone-name example.com \
  --resource-group myRG \
  --name www

# Remove a specific record from a record set
az network dns record-set a remove-record \
  --zone-name example.com \
  --resource-group myRG \
  --record-set-name www \
  --ipv4-address 20.30.40.50

# Delete an entire record set
az network dns record-set a delete \
  --zone-name example.com \
  --resource-group myRG \
  --name www \
  --yes
```

---

## Azure Private DNS

```bash
# Create a private DNS zone
az network private-dns zone create \
  --name internal.example.com \
  --resource-group myRG

# Create a Private DNS Zone for Private Endpoint (Blob Storage)
az network private-dns zone create \
  --name privatelink.blob.core.windows.net \
  --resource-group myRG

# Link private DNS zone to a VNet (without auto-registration)
az network private-dns link vnet create \
  --name myDNSLink \
  --resource-group myRG \
  --zone-name privatelink.blob.core.windows.net \
  --virtual-network myVNet \
  --registration-enabled false

# Link private DNS zone with auto-registration (VM A records auto-created)
az network private-dns link vnet create \
  --name myAutoRegLink \
  --resource-group myRG \
  --zone-name internal.example.com \
  --virtual-network myVNet \
  --registration-enabled true

# List VNet links for a private zone
az network private-dns link vnet list \
  --zone-name privatelink.blob.core.windows.net \
  --resource-group myRG \
  --output table

# Create an A record in private DNS zone
az network private-dns record-set a create \
  --zone-name internal.example.com \
  --resource-group myRG \
  --name myserver \
  --ttl 300

az network private-dns record-set a add-record \
  --zone-name internal.example.com \
  --resource-group myRG \
  --record-set-name myserver \
  --ipv4-address 10.0.1.10

# List all private DNS zones
az network private-dns zone list \
  --resource-group myRG \
  --output table

# List record sets in a private zone
az network private-dns record-set list \
  --zone-name internal.example.com \
  --resource-group myRG \
  --output table

# Delete a private DNS zone (unlink VNets first)
az network private-dns link vnet delete \
  --name myDNSLink \
  --resource-group myRG \
  --zone-name internal.example.com \
  --yes

az network private-dns zone delete \
  --name internal.example.com \
  --resource-group myRG \
  --yes
```

---

## Azure DNS Private Resolver

```bash
# Create a DNS Private Resolver (requires two dedicated subnets: inbound and outbound)
# First, create the VNet subnets with proper delegations

# Create inbound subnet with delegation
az network vnet subnet create \
  --name DnsResolverInboundSubnet \
  --vnet-name myHubVNet \
  --resource-group myRG \
  --address-prefixes 10.0.10.0/28 \
  --delegations Microsoft.Network/dnsResolvers

# Create outbound subnet with delegation
az network vnet subnet create \
  --name DnsResolverOutboundSubnet \
  --vnet-name myHubVNet \
  --resource-group myRG \
  --address-prefixes 10.0.10.16/28 \
  --delegations Microsoft.Network/dnsResolvers

# Create the DNS Resolver
az dns-resolver create \
  --dns-resolver-name myDNSResolver \
  --resource-group myRG \
  --location eastus \
  --id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/myHubVNet

# Create an inbound endpoint (on-premises DNS forwards queries here)
az dns-resolver inbound-endpoint create \
  --dns-resolver-name myDNSResolver \
  --resource-group myRG \
  --inbound-endpoint-name myInboundEndpoint \
  --location eastus \
  --ip-configurations '[{"private-ip-allocation-method":"Dynamic","id":"/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/myHubVNet/subnets/DnsResolverInboundSubnet"}]'

# Show inbound endpoint (get the private IP to use on on-premises DNS forwarder)
az dns-resolver inbound-endpoint show \
  --dns-resolver-name myDNSResolver \
  --resource-group myRG \
  --inbound-endpoint-name myInboundEndpoint \
  --query ipConfigurations[0].privateIpAddress \
  --output tsv

# Create an outbound endpoint (Azure sends queries to on-premises through here)
az dns-resolver outbound-endpoint create \
  --dns-resolver-name myDNSResolver \
  --resource-group myRG \
  --outbound-endpoint-name myOutboundEndpoint \
  --location eastus \
  --id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/myHubVNet/subnets/DnsResolverOutboundSubnet

# Create a forwarding ruleset (container for forwarding rules)
az dns-resolver forwarding-ruleset create \
  --forwarding-ruleset-name myForwardingRuleset \
  --resource-group myRG \
  --location eastus \
  --outbound-endpoints '[{"id":"/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/dnsResolvers/myDNSResolver/outboundEndpoints/myOutboundEndpoint"}]'

# Add a forwarding rule: corp.example.com → on-premises DNS
az dns-resolver forwarding-rule create \
  --forwarding-ruleset-name myForwardingRuleset \
  --resource-group myRG \
  --forwarding-rule-name CorpDomain \
  --domain-name "corp.example.com." \
  --target-dns-servers '[{"ip-address":"192.168.1.1","port":53},{"ip-address":"192.168.1.2","port":53}]' \
  --forwarding-rule-state Enabled

# Link forwarding ruleset to spoke VNets (so spoke VMs use forwarding rules)
az dns-resolver vnet-link create \
  --forwarding-ruleset-name myForwardingRuleset \
  --resource-group myRG \
  --vnet-link-name Spoke1Link \
  --id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/SpokeVNet1

# List DNS resolvers
az dns-resolver list \
  --resource-group myRG \
  --output table

# List inbound endpoints
az dns-resolver inbound-endpoint list \
  --dns-resolver-name myDNSResolver \
  --resource-group myRG \
  --output table

# List forwarding rulesets
az dns-resolver forwarding-ruleset list \
  --resource-group myRG \
  --output table

# List forwarding rules in a ruleset
az dns-resolver forwarding-rule list \
  --forwarding-ruleset-name myForwardingRuleset \
  --resource-group myRG \
  --output table
```

---

## Private Link Service (Provider)

```bash
# Create a Private Link Service (requires Standard Internal Load Balancer)
# First disable private link service network policies on the NAT subnet
az network vnet subnet update \
  --name PrivateLinkServiceSubnet \
  --vnet-name myVNet \
  --resource-group myRG \
  --disable-private-link-service-network-policies true

# Create the Private Link Service
az network private-link-service create \
  --name myPrivateLinkService \
  --resource-group myRG \
  --location eastus \
  --vnet-name myVNet \
  --subnet PrivateLinkServiceSubnet \
  --lb-name myInternalLoadBalancer \
  --lb-frontend-ip-configs myFrontend \
  --auto-approval-subscriptions "<consumer-sub-id-1>" "<consumer-sub-id-2>"

# List Private Link Services
az network private-link-service list \
  --resource-group myRG \
  --output table

# Show PLS details (includes alias for sharing with consumers)
az network private-link-service show \
  --name myPrivateLinkService \
  --resource-group myRG \
  --query alias \
  --output tsv

# List pending Private Endpoint connections to the PLS
az network private-link-service list-connections \
  --name myPrivateLinkService \
  --resource-group myRG \
  --output table

# Approve a pending Private Endpoint connection
az network private-link-service update-private-endpoint-connection \
  --name myPrivateLinkService \
  --resource-group myRG \
  --endpoint-connections [{"name":"<connection-name>","privateLinkServiceConnectionState":{"status":"Approved","description":"Approved by admin"}}]

# Reject a Private Endpoint connection
az network private-link-service reject-endpoint-connection \
  --name myPrivateLinkService \
  --resource-group myRG \
  --endpoint-name "<connection-name>"

# Delete a Private Link Service
az network private-link-service delete \
  --name myPrivateLinkService \
  --resource-group myRG \
  --yes
```

---

## Private Endpoints (Consumer)

```bash
# Create a Private Endpoint for Azure Key Vault
az network private-endpoint create \
  --name myKVPrivateEndpoint \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault \
  --group-id vault \
  --connection-name myKVConnection \
  --location eastus

# Create a Private Endpoint for Azure SQL Database
az network private-endpoint create \
  --name mySQLPrivateEndpoint \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Sql/servers/mySQLServer \
  --group-id sqlServer \
  --connection-name mySQLConnection

# Create a Private Endpoint for a Private Link Service (cross-tenant)
az network private-endpoint create \
  --name myPLSEndpoint \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/privateLinkServices/myPrivateLinkService \
  --connection-name myPLSConnection \
  --request-message "Requesting access to partner service"

# Get private IP of a Private Endpoint NIC
az network private-endpoint show \
  --name myKVPrivateEndpoint \
  --resource-group myRG \
  --query customDnsConfigs[0].ipAddresses \
  --output tsv

# Add DNS Zone Group to Private Endpoint (auto-creates DNS record)
az network private-endpoint dns-zone-group create \
  --endpoint-name myKVPrivateEndpoint \
  --resource-group myRG \
  --name myKVZoneGroup \
  --private-dns-zone privatelink.vaultcore.azure.net \
  --zone-name vault

# Add DNS Zone Group for Storage (multiple sub-resources)
az network private-endpoint dns-zone-group create \
  --endpoint-name myStoragePrivateEndpoint \
  --resource-group myRG \
  --name myStorageZoneGroup \
  --private-dns-zone privatelink.blob.core.windows.net \
  --zone-name blob

# List all Private Endpoints
az network private-endpoint list \
  --resource-group myRG \
  --output table

# Show Private Endpoint connection state
az network private-endpoint show \
  --name myKVPrivateEndpoint \
  --resource-group myRG \
  --query "{name:name,state:privateLinkServiceConnections[0].privateLinkServiceConnectionState.status}"

# Delete a Private Endpoint
az network private-endpoint delete \
  --name myKVPrivateEndpoint \
  --resource-group myRG \
  --yes

# List available Private Link resources for a service
az network private-link-resource list \
  --id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/myStorage \
  --output table
```
