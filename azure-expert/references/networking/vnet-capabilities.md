# Azure Virtual Network — Capabilities

## Overview

Azure Virtual Network (VNet) is the fundamental building block for private networking in Azure. Every Azure IaaS resource lives in a VNet; PaaS services connect via Service Endpoints or Private Endpoints. Understanding VNet design is prerequisite to designing any production Azure architecture.

---

## VNet Core Concepts

### CIDR Planning and Address Spaces

- A VNet has one or more **address spaces** (CIDR blocks); multiple address spaces can be added after creation
- Subnets carve address space; each subnet must be a subset of a VNet address space
- Azure reserves **5 IPs per subnet**: `.0` (network), `.1` (gateway), `.2` (DNS), `.3` (DNS), `.255` (broadcast)
- Plan for growth: prefer `/16` or larger VNets, `/24`–`/27` subnets depending on service density
- Avoid RFC 1918 overlaps when planning hybrid connectivity or VNet peering
- Address spaces can coexist with IPv6 (dual-stack support; see below)

### Subnets

- Resources in the same subnet share an address range but are isolated by NSGs
- Some services require **dedicated subnets**: `GatewaySubnet` (VPN/ER Gateway), `AzureFirewallSubnet`, `AzureBastionSubnet`, `RouteServerSubnet`
- Subnet delegation: assigns a subnet exclusively to a service (e.g., `Microsoft.Web/serverFarms` for App Service VNet Integration, `Microsoft.DBforPostgreSQL/flexibleServers`)
- Delegated subnets cannot host other resource types

### System Routes

Azure automatically creates system routes for:
- Traffic within the VNet address space (local VNet routing)
- Traffic to internet (0.0.0.0/0 via internet gateway)
- Traffic to specific Azure service prefixes

System routes cannot be deleted, but can be **overridden** with User Defined Routes (UDRs).

---

## Network Security Groups (NSGs)

NSGs are stateful L3/L4 packet filters attached to **subnets** or **network interfaces** (NICs). Subnet-level NSGs are preferred for manageability.

### Rule Structure

| Property | Values | Notes |
|---|---|---|
| Priority | 100–4096 (lower = higher priority) | Rules evaluated in order; first match wins |
| Direction | Inbound / Outbound | Separate rule sets |
| Protocol | TCP, UDP, ICMP, ESP, AH, Any | |
| Source/Destination | IP, CIDR, Service Tag, ASG | Service Tags updated by Microsoft |
| Port | Single, range, or `*` | |
| Action | Allow / Deny | Default deny at end of chain |

### Default Rules (cannot be deleted, priority 65000+)

- `AllowVnetInBound` / `AllowVnetOutBound`: permits all intra-VNet traffic
- `AllowAzureLoadBalancerInBound`: permits ALB health probe traffic
- `DenyAllInBound` / `DenyAllOutBound`: implicit deny-all

### Service Tags

Pre-built IP prefixes maintained by Microsoft for Azure services. Examples:
- `AzureLoadBalancer` — load balancer health probe source
- `Internet` — public internet address space
- `VirtualNetwork` — entire VNet address space including peered VNets
- `Storage`, `Sql`, `AzureActiveDirectory`, `AzureMonitor`, `AppService`, etc.
- `AzureCloud.EastUS` — regional scoping is supported

### Application Security Groups (ASGs)

ASGs allow grouping VMs logically (e.g., `asg-web`, `asg-db`) and referencing those groups in NSG rules instead of IPs. Benefits:
- Rules remain valid even as VMs scale or IPs change
- Self-referencing ASGs enable intra-tier communication rules
- A NIC can belong to multiple ASGs (up to 20)

### NSG Flow Logs

- Version 1: records allowed/denied flows
- Version 2: adds bytes/packets per flow
- Stored in Azure Storage Account; analyzed via **Traffic Analytics** in Log Analytics
- Enable per NSG; required for meaningful network visibility

### Augmented Security Rules

A single rule can reference multiple source/destination IPs, port ranges, and service tags — reducing the number of rules needed.

---

## Route Tables (User Defined Routes)

### Custom Routes

UDRs override system routes to control traffic flow. Common use cases:
- Force all outbound internet traffic through Azure Firewall (forced tunneling)
- Route traffic between spokes through a hub NVA or firewall
- Override BGP-learned routes from VPN/ExpressRoute Gateways

### Route Properties

| Property | Options |
|---|---|
| Address prefix | CIDR block to match |
| Next hop type | VirtualAppliance, Internet, VirtualNetworkGateway, VnetLocal, None |
| Next hop IP | Required for VirtualAppliance (must be in same or peered VNet) |

### Forced Tunneling

Route `0.0.0.0/0` to a `VirtualAppliance` (Azure Firewall, NVA) or `VirtualNetworkGateway` to force all internet-bound traffic through inspection. Required for compliance in regulated environments.

### BGP Route Propagation

On route tables, `Disable BGP route propagation` can be toggled. When disabled, routes learned from VPN/ExpressRoute Gateways are not propagated to subnets using that route table — useful when UDRs should take full control.

---

## VNet Peering

### Regional Peering

- Low-latency, high-bandwidth direct connection between two VNets in the same region
- Traffic stays on Microsoft backbone, not the public internet
- Non-transitive: VNet A ↔ VNet B ↔ VNet C does NOT allow A ↔ C without explicit A-C peering (or hub-spoke with route forwarding)
- Peering is directional: two peering links required (A→B and B→A), both must be created

### Global Peering

- Same as regional, but across Azure regions
- Data transfer charges apply for cross-region traffic
- Used in multi-region hub-spoke topologies

### Peering Configuration Options

| Option | Description |
|---|---|
| Allow traffic to remote VNet | Required on both sides to enable communication |
| Allow forwarded traffic | Allows traffic forwarded from another VNet (needed in hub-spoke) |
| Allow gateway transit | Hub allows spokes to use its VPN/ER Gateway |
| Use remote gateway | Spoke uses hub's gateway (only one gateway per VNet allowed) |

---

## Hub-Spoke Topology

The recommended architecture for most enterprise Azure deployments:

```
                    ┌─────────────────────────────┐
                    │         Hub VNet             │
                    │  ┌──────────┐ ┌───────────┐  │
                    │  │  Azure   │ │  VPN/ER   │  │
                    │  │ Firewall │ │  Gateway  │  │
                    │  └──────────┘ └───────────┘  │
                    │  ┌──────────┐                 │
                    │  │ Bastion  │                 │
                    │  └──────────┘                 │
                    └──────────┬──────────────────┘
                               │ VNet Peering
               ┌───────────────┼───────────────┐
               │               │               │
        ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
        │  Spoke VNet │ │  Spoke VNet │ │  Spoke VNet │
        │   (Prod)    │ │   (Dev)     │ │   (Shared)  │
        └─────────────┘ └─────────────┘ └─────────────┘
```

- **Hub VNet**: centralized shared services — Azure Firewall, Bastion, VPN/ExpressRoute Gateway, DNS
- **Spoke VNets**: workload isolation; peered to hub with `Allow gateway transit` (hub) and `Use remote gateway` (spoke)
- UDRs in spokes route `0.0.0.0/0` to Azure Firewall in hub
- Hub-spoke requires explicit peering between spoke pairs if direct communication needed (or route through firewall)

---

## Service Endpoints

- Extends VNet identity to Azure PaaS services over the Azure backbone (not internet)
- Traffic from VNet subnet to the PaaS service stays on Microsoft backbone
- The PaaS resource's firewall can restrict access to VNet subnets only
- Supported services: Azure Storage, Azure SQL, Azure Cosmos DB, Azure Key Vault, Azure Service Bus, Azure Event Hubs, etc.
- **Limitation**: the PaaS endpoint remains a public IP; Service Endpoints only affect routing and firewall rules — not a private IP inside your VNet
- **Recommendation**: prefer Private Endpoints for new workloads; Service Endpoints suitable for simple VNet-restriction scenarios

---

## Private Endpoints

Private Endpoints project an Azure PaaS service as a **private IP address within your VNet**. This is the preferred connectivity model for PaaS in zero-trust architectures.

### How It Works

1. A private endpoint NIC is created in your subnet with a private IP
2. DNS must resolve the service's public FQDN to the private IP (critical!)
3. The PaaS service's public access can be fully disabled after private endpoint creation

### DNS Configuration (Critical)

Each PaaS service has a specific Private DNS Zone name. Traffic resolution path:

```
App queries storage.blob.core.windows.net
→ Azure DNS returns CNAME: storage.privatelink.blob.core.windows.net
→ Private DNS Zone privatelink.blob.core.windows.net → 10.0.1.4 (private IP)
```

Common Private DNS Zone names:
| Service | Private DNS Zone |
|---|---|
| Blob Storage | `privatelink.blob.core.windows.net` |
| Azure SQL | `privatelink.database.windows.net` |
| Key Vault | `privatelink.vaultcore.azure.net` |
| ACR | `privatelink.azurecr.io` |
| AKS API | `privatelink.<region>.azmk8s.io` |
| Cosmos DB (SQL) | `privatelink.documents.azure.com` |
| Service Bus | `privatelink.servicebus.windows.net` |
| App Service | `privatelink.azurewebsites.net` |

- Private DNS Zones must be linked to the VNet where resolution occurs
- In hub-spoke: create Private DNS Zones in hub and link to all spokes
- For hybrid (on-premises): use Azure DNS Private Resolver or DNS forwarder VMs

---

## NAT Gateway

Provides outbound SNAT for private subnet resources (VMs, containers) that need internet access **without** a Load Balancer or public IPs on each VM.

### Key Characteristics

- Supports up to **16 public IP addresses** per NAT Gateway
- Each public IP provides **64,512 SNAT ports** (total: up to ~1M ports per NAT Gateway)
- Zone-redundant or zonal deployment
- Associated to subnets; all outbound from that subnet uses NAT Gateway
- Idle timeout: 4–120 minutes (default 4 min)
- NAT Gateway does NOT support inbound connections
- If a subnet has both a Load Balancer outbound rule and NAT Gateway, NAT Gateway takes precedence

---

## VNet Integration for App Service / Azure Functions

- Enables **outbound** connectivity from App Service / Functions to resources in a VNet
- Does NOT enable inbound connections from VNet to App Service (use Private Endpoints for that)
- Requires a delegated subnet (`Microsoft.Web/serverFarms`)
- Regional VNet Integration: App Service in same region as VNet (preferred)
- Route All traffic: force all outbound (including internet) through VNet (enables UDR/Firewall inspection)
- Required for accessing Private Endpoint-protected resources from App Service

---

## Azure Virtual Network Manager (AVNM)

Centralized management of VNets at scale across subscriptions and management groups.

### Features

- **Security Admin Rules**: centrally enforced NSG-like rules that override or complement resource-level NSGs; useful for organization-wide deny rules (e.g., block all SSH from internet)
- **Connectivity Configurations**: define hub-spoke or mesh topologies declaratively; AVNM manages peering automatically
- **Network Groups**: dynamic or static grouping of VNets (can use Azure Policy conditions)
- Supports management group scope for enterprise-wide governance

---

## IPv6 Dual-Stack Support

- VNets support dual-stack (IPv4 + IPv6) address spaces
- Subnets can be dual-stack with both an IPv4 and IPv6 prefix
- IPv6 prefixes: `/64` required for subnets
- Public IPv6 Load Balancer and VM public IP support
- NSG rules support IPv6 source/destination
- VNet peering supports dual-stack
- Limitation: not all Azure services support IPv6 (check per-service documentation)
