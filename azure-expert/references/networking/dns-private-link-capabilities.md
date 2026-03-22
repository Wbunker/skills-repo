# Azure DNS & Private Link — Capabilities

## Overview

This namespace covers DNS services (public and private) and Azure Private Link — the technology enabling private connectivity to Azure PaaS and partner services without traversing the public internet. Correct DNS configuration is the most common failure point when deploying Private Endpoints.

---

## Azure DNS (Public Zones)

Azure DNS hosts authoritative DNS zones for publicly registered domains. It uses anycast routing across 100+ servers in 40+ locations worldwide, providing high availability without geographic single points of failure.

### Key Features

- **Anycast routing**: queries answered by the nearest DNS server cluster
- **100% SLA**: guaranteed availability for DNS resolution
- **Private zone integration**: same CLI and portal experience; public zones are globally accessible
- **Role-based access**: granular control over who can manage DNS records
- **Monitoring**: DNS query volume, record set count metrics via Azure Monitor
- **Audit logs**: track changes to DNS records via Azure Activity Log

### Record Types Supported

| Type | Purpose |
|---|---|
| A | IPv4 address |
| AAAA | IPv6 address |
| CNAME | Canonical name alias |
| MX | Mail exchange |
| NS | Name server delegation |
| PTR | Reverse DNS (pointer) |
| SRV | Service location |
| TXT | Text records (SPF, DKIM, DMARC, domain verification) |
| CAA | Certificate Authority Authorization |
| SOA | Start of Authority (auto-managed) |

### Alias Records

Alias records are an Azure DNS extension that resolve directly to Azure resource IDs instead of IP addresses. Unlike CNAME, alias records can be created at the **zone apex** (root domain, e.g., `example.com`).

Supported targets:
- Azure Public Load Balancer (Standard SKU)
- Azure Traffic Manager profile
- Azure Front Door profile
- Azure CDN endpoint

**Use case**: `example.com` (apex) → Traffic Manager profile. Without alias records, apex CNAME is not allowed by DNS standards.

### Delegation

To use Azure DNS as authoritative for your domain:
1. Create a public DNS zone in Azure DNS
2. Note the four NS records assigned
3. Update your domain registrar's NS records to point to Azure DNS NS servers

### Split-Horizon DNS

Create the same zone name as both public and private — clients on VNet resolve private IPs while internet clients resolve public IPs. Azure DNS supports this natively (different zones with same name at public vs private scope).

---

## Azure Private DNS

Private DNS zones provide name resolution exclusively within linked Azure Virtual Networks. Records are not reachable from the internet.

### Key Concepts

- **Private DNS Zone**: DNS zone visible only within linked VNets (e.g., `internal.example.com`)
- **VNet Link**: associates a private zone with one or more VNets; enables resolution from those VNets
- **Auto-registration**: automatically creates/deletes A records for VM NICs within linked VNets (supported for single private zone per VNet)
- **Maximum links**: 1,000 VNets per private zone; up to 10 private zones can use auto-registration for a VNet

### Private Endpoint DNS Zones

Each Azure PaaS service that supports Private Endpoints uses a specific `privatelink.*` Private DNS Zone. **Correct zone name is required** — using the wrong zone name means Private Endpoint DNS resolution fails.

| Service | Group ID | Private DNS Zone |
|---|---|---|
| Azure Blob Storage | `blob` | `privatelink.blob.core.windows.net` |
| Azure Queue Storage | `queue` | `privatelink.queue.core.windows.net` |
| Azure Table Storage | `table` | `privatelink.table.core.windows.net` |
| Azure File Storage | `file` | `privatelink.file.core.windows.net` |
| Azure Data Lake Gen2 | `dfs` | `privatelink.dfs.core.windows.net` |
| Azure SQL Database | `sqlServer` | `privatelink.database.windows.net` |
| Azure Cosmos DB (SQL) | `Sql` | `privatelink.documents.azure.com` |
| Azure Cosmos DB (MongoDB) | `MongoDB` | `privatelink.mongo.cosmos.azure.com` |
| Azure Key Vault | `vault` | `privatelink.vaultcore.azure.net` |
| Azure Container Registry | `registry` | `privatelink.azurecr.io` |
| Azure Kubernetes Service | — | `privatelink.<region>.azmk8s.io` |
| Azure Service Bus | `namespace` | `privatelink.servicebus.windows.net` |
| Azure Event Hubs | `namespace` | `privatelink.servicebus.windows.net` |
| Azure App Service / Functions | `sites` | `privatelink.azurewebsites.net` |
| Azure Monitor (Log Analytics) | `azuremonitor` | `privatelink.monitor.azure.com` |
| Azure Cognitive Services | `account` | `privatelink.cognitiveservices.azure.com` |
| Azure OpenAI | `account` | `privatelink.openai.azure.com` |

### Private Endpoint DNS Resolution Flow

```
1. Client queries: myaccount.blob.core.windows.net
2. Azure DNS returns CNAME: myaccount.privatelink.blob.core.windows.net
3. Private DNS Zone (privatelink.blob.core.windows.net) returns A record: 10.0.1.5
4. Client connects to 10.0.1.5 (Private Endpoint NIC in VNet)
```

If step 3 fails (zone not linked, record missing), Azure DNS returns the public IP instead — connection bypasses Private Endpoint.

### Hub-Spoke DNS Architecture

Recommended pattern for enterprise hub-spoke:
1. Create all `privatelink.*` Private DNS Zones in a central **DNS subscription or hub resource group**
2. Link each zone to the **hub VNet** (and optionally all spoke VNets, or use DNS Private Resolver)
3. When Private Endpoints are created in spoke VNets, use **DNS Zone Groups** to auto-register records in the centralized zones

```
Hub VNet (DNS resource group)
├── privatelink.blob.core.windows.net → linked to Hub VNet
├── privatelink.database.windows.net → linked to Hub VNet
└── privatelink.vaultcore.azure.net → linked to Hub VNet

Spoke1 VNet (app workload)
└── Private Endpoint: myblob → NIC IP 10.1.1.4
    └── DNS Zone Group → auto-creates A record in hub zone
```

---

## Azure DNS Private Resolver

Azure DNS Private Resolver enables conditional DNS forwarding between on-premises and Azure without deploying and managing DNS forwarder VMs. It is a fully managed, highly available service.

### Architecture

```
On-Premises DNS → [Inbound Endpoint IP: 10.0.0.4] → Azure DNS Private Resolver
Azure VMs → Azure DNS → [Outbound Endpoint] → Forwarding Ruleset → On-Premises DNS (192.168.1.1)
```

### Components

| Component | Description |
|---|---|
| **Inbound Endpoint** | Private IP in your VNet; on-premises DNS servers forward queries here; resolves against Azure DNS and linked Private DNS Zones |
| **Outbound Endpoint** | Private IP in a dedicated subnet; forwards queries to external DNS servers per ruleset rules |
| **DNS Forwarding Ruleset** | Set of conditional forwarding rules (domain → target DNS server); linked to VNets |
| **Forwarding Rule** | `domain_suffix → [DNS server IP:port]`; e.g., `corp.example.com → 192.168.1.1:53` |

### Required Subnets

- Inbound Endpoint subnet: minimum `/28`; delegate to `Microsoft.Network/dnsResolvers`
- Outbound Endpoint subnet: minimum `/28`; separate from inbound subnet

### Use Cases

| Scenario | Solution |
|---|---|
| On-premises resolves Azure Private DNS zones | Configure on-premises DNS conditional forwarder → Inbound Endpoint IP |
| Azure VMs resolve on-premises domains | Create forwarding ruleset with rule for corp domain → on-premises DNS; link to VNets |
| Hub-spoke centralized DNS | Deploy resolver in hub; link forwarding ruleset to all spoke VNets |

### DNS Private Resolver vs DNS Forwarder VMs

| | DNS Private Resolver | DNS Forwarder VMs |
|---|---|---|
| Managed | Yes (fully managed) | No (customer-managed) |
| HA | Built-in, zone-redundant | Manual (2 VMs, custom HA) |
| Maintenance | None | OS patching, VM lifecycle |
| Scaling | Automatic | Manual |
| Cost | Per resolver + endpoint + queries | VM compute cost |

---

## Azure Private Link

Private Link is the underlying technology that enables Private Endpoints. It also allows service providers to expose their own services privately via Private Link Service.

### Private Endpoint (Consumer Side)

- Creates a NIC with a private IP in the consumer's VNet
- Connects to a specific Azure PaaS resource or Private Link Service
- DNS must be configured to resolve the service FQDN to the private IP
- Network policies (NSG, route tables) on PE subnet are disabled by default; must explicitly enable:
  ```bash
  az network vnet subnet update --disable-private-endpoint-network-policies false
  ```
- Private Endpoint NIC can have NSG attached when network policies enabled
- Supports across subscriptions and tenants (with approval workflow)

### Private Link Service (Provider Side)

Private Link Service exposes **your own** Standard Load Balancer-backed service to other Azure customers via their Private Endpoints.

#### How It Works

1. Service owner deploys app behind a Standard Internal Load Balancer
2. Create a Private Link Service (PLS) referencing the ILB frontend
3. Consumers create a Private Endpoint pointing to the PLS resource ID or alias
4. Service owner approves or auto-approves the connection
5. Consumer DNS resolves PE FQDN to private IP in their VNet

#### NAT IPs

- Private Link Service translates consumer private IPs to a provider-controlled NAT IP range
- Prevents IP address overlap between consumer and provider VNets
- NAT subnet: dedicated `/29` or larger subnet in provider VNet, delegated to `Microsoft.Network/privateLinkServices`

#### Connection Approval

| Mode | Description |
|---|---|
| **Auto-approval** | Consumer connections from listed subscriptions automatically approved |
| **Manual approval** | Service owner reviews and approves/rejects each connection request |

#### Alias

- PLS gets a globally unique alias (`<name>.<GUID>.centralus.azure.privatelinkservice`)
- Share alias with consumers to create Private Endpoints (no ARM resource ID needed)
- Alias can be used across tenants

### Private Endpoint Connection States

| State | Description |
|---|---|
| Pending | Consumer created PE; awaiting provider approval |
| Approved | Connection active; traffic flowing |
| Rejected | Provider rejected; connection not functional |
| Disconnected | Provider disconnected approved connection |

### Private Endpoint DNS Zone Groups

DNS Zone Groups link a Private Endpoint to one or more Private DNS Zones, automating A record creation when the PE is created and deletion when the PE is removed.

```bash
# Zone group auto-creates an A record in the linked zone
az network private-endpoint dns-zone-group create \
  --endpoint-name myBlobPE \
  --resource-group myRG \
  --name myZoneGroup \
  --private-dns-zone privatelink.blob.core.windows.net \
  --zone-name blob
```

Benefits:
- Eliminates manual DNS record management
- Record automatically deleted if PE is deleted
- Supports multiple zones per zone group (for services with multiple sub-resources)

---

## Troubleshooting Private Endpoint DNS

Common issues and resolution:

| Symptom | Likely Cause | Resolution |
|---|---|---|
| `nslookup` returns public IP from VNet | Private DNS Zone not linked to VNet | Link zone to VNet |
| DNS resolves correctly from VNet but not from on-premises | On-premises DNS not forwarding to Azure | Configure conditional forwarder to DNS Private Resolver inbound endpoint |
| Private Endpoint shows `Approved` but connections fail | NSG on PE subnet blocking traffic | Enable network policies; add NSG rule allowing traffic on required ports |
| PE created but no A record in Private DNS Zone | DNS Zone Group not configured | Create DNS Zone Group linking PE to correct private zone |
| Wrong zone name used | DNS resolution falls through to public IP | Use exact zone name from Private DNS Zone table above |
