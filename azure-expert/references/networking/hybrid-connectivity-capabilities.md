# Azure Hybrid Connectivity — Capabilities

## Overview

Hybrid connectivity bridges on-premises data centers and branch offices to Azure. The three primary services are ExpressRoute (private dedicated circuit), VPN Gateway (encrypted internet tunnels), and Azure Virtual WAN (managed hub-and-spoke at cloud scale).

---

## ExpressRoute

ExpressRoute provides **private, dedicated connectivity** to Azure — traffic does not traverse the public internet. It is the preferred connectivity option for large-scale enterprise workloads, compliance-sensitive environments, and high-throughput data transfers.

### Circuit Fundamentals

- **Circuit**: represents a physical connection through a connectivity provider; billed independently of VNet connections
- **Bandwidth options**: 50 Mbps, 100 Mbps, 200 Mbps, 500 Mbps, 1 Gbps, 2 Gbps, 5 Gbps, 10 Gbps, 100 Gbps
- **Circuit SKU tiers**:
  - **Local**: connect to Azure regions adjacent to the peering location; unlimited data (inbound + outbound)
  - **Standard**: connect to Azure regions in the same geopolitical region
  - **Premium**: global connectivity (any Azure region), Microsoft 365 connectivity, larger route table (10K routes)

### Peering Types

| Peering Type | Purpose |
|---|---|
| **Azure Private Peering** | Connect to Azure VNets (IaaS) via VNet Gateways; private IPs |
| **Microsoft Peering** | Connect to Microsoft 365, Dynamics 365, Azure PaaS public endpoints via BGP |

> Azure Public Peering is deprecated; use Microsoft Peering for public Azure services.

### Connectivity Models

| Model | Description |
|---|---|
| **Co-location** | Collocate equipment in a provider-neutral facility; provider connects to Microsoft enterprise edge (MSEE) |
| **Point-to-Point Ethernet** | Dedicated Layer 2 or Layer 3 link from on-premises to MSEE via a provider |
| **Any-to-Any (IPVPN)** | MPLS WAN provider adds Azure as a site; natural extension of existing WAN |
| **ExpressRoute Direct** | Direct 10G/100G physical port on MSEE (bypass provider); for ultra-high-bandwidth |

### VNet Gateway for ExpressRoute

- Requires an **ExpressRoute Virtual Network Gateway** (not VPN Gateway) in a `GatewaySubnet`
- Gateway SKUs for ExpressRoute: `ErGw1AZ`, `ErGw2AZ`, `ErGw3AZ` (zone-redundant), `UltraPerformance`
  - `ErGw3AZ`: up to 10 Gbps; `UltraPerformance`: up to 16 Gbps
- A single gateway can have multiple circuit connections (up to 10)
- **Gateway transit**: VNet peered spokes can route traffic through hub's ER Gateway

### ExpressRoute Global Reach

- Connect two on-premises sites **via Microsoft backbone** (site A → Azure → site B)
- Requires both circuits to have Microsoft Peering or Private Peering configured
- Must be supported by connectivity provider and in supported countries
- Traffic stays fully on Microsoft's network (not internet)

### ExpressRoute FastPath

- Bypasses the Virtual Network Gateway for data plane traffic (gateway still needed for control plane)
- Available with `UltraPerformance` or `ErGw3AZ` gateway SKUs
- Supports: Direct connections and ER Global Reach
- Reduces latency by eliminating the gateway hop in the data path
- Limitation: does not support UDRs or Private Endpoints on the gateway subnet

### ExpressRoute Direct

- Direct physical connectivity at 10 Gbps or 100 Gbps from customer's router to MSEE
- Eliminates connectivity provider in the link (enterprise directly leases port capacity)
- Supports multiple ExpressRoute circuits on the same physical port pair (sub-rate circuits)
- MACSec encryption at Layer 2 on the link
- Ideal for: massive data migration, regulated industries, private peering to Azure at scale

### Redundancy and High Availability

- Every ExpressRoute circuit has two connections (primary + secondary) for redundancy
- Active-active configuration: both paths carry traffic simultaneously (recommended)
- Dual-circuit architecture: two circuits at different peering locations for maximum HA
- BFD (Bidirectional Forwarding Detection): fast link failure detection (sub-second)

---

## VPN Gateway

Encrypted **IPsec/IKE tunnels** over the public internet. Lower cost and simpler than ExpressRoute; suitable for branch connectivity, P2S remote access, and environments where private connectivity is not required.

### Gateway SKUs

| SKU | Throughput | Max S2S Tunnels | IKEv2 P2S | Zone-Redundant |
|---|---|---|---|---|
| Basic | 100 Mbps | 10 | No | No |
| VpnGw1 | 650 Mbps | 30 | 250 | No |
| VpnGw2 | 1 Gbps | 30 | 500 | No |
| VpnGw3 | 1.25 Gbps | 30 | 1,000 | No |
| VpnGw1AZ | 650 Mbps | 30 | 250 | Yes |
| VpnGw2AZ | 1 Gbps | 30 | 500 | Yes |
| VpnGw3AZ | 1.25 Gbps | 30 | 1,000 | Yes |
| VpnGw4 / 4AZ | 5 Gbps | 100 | 5,000 | Optional |
| VpnGw5 / 5AZ | 10 Gbps | 100 | 10,000 | Optional |

> Use AZ SKUs (zone-redundant) for production. Avoid Basic SKU (limited features, no SLA).

### Connection Types

#### Site-to-Site (S2S)

- IPsec/IKEv2 tunnel between on-premises VPN device and Azure VPN Gateway
- Requires a **Local Network Gateway** resource representing on-premises VPN device (public IP + address space)
- Policy-based VPN (IKEv1, static routing): basic compatibility, single tunnel
- Route-based VPN (IKEv2, dynamic): multiple tunnels, BGP support, P2S, VNet-to-VNet — always use route-based for new deployments
- IKEv1/v2 custom policies: configure specific cipher suites, DH groups, integrity algorithms

#### Point-to-Site (P2S)

Remote access VPN for individual clients (remote workers):

| Protocol | Notes |
|---|---|
| **OpenVPN (TLS)** | Cross-platform (Windows, macOS, Linux, iOS, Android); uses TCP 443 or UDP 1194 |
| **SSTP** | Windows-only; uses TCP 443 (firewall-friendly) |
| **IKEv2** | macOS and iOS native; UDP 500/4500 |

- Authentication: Azure certificate, Azure AD (Entra ID), RADIUS (supports MFA via NPS extension)
- Client address pool: CIDR block assigned to VPN clients (separate from VNet address space)
- Entra ID authentication: allows Conditional Access policies to apply to VPN connections

#### VNet-to-VNet

- IPsec tunnel between two Azure VNets (different regions or subscriptions)
- Alternative to VNet peering; useful when policy requires encrypted transit or connecting across tenants
- Managed via VPN Gateway; simpler than peering across tenants

### BGP Support

- Dynamic routing with BGP (Border Gateway Protocol)
- Enables automatic route exchange between on-premises and Azure
- ASN: assign private ASN (64512–65535) to VPN Gateway; use different ASN for on-premises
- BGP peers: VPN Gateway BGP peer IP (from `GatewaySubnet`) and on-premises BGP peer IP
- Required for active-active VPN Gateway configurations

### Active-Active vs Active-Standby

| Mode | Description |
|---|---|
| **Active-Standby** (default) | Primary tunnel active; standby takes over during failover (10–15s planned, 60–90s unplanned) |
| **Active-Active** | Both tunnel endpoints active simultaneously; requires BGP; provides sub-second failover with BGP fast convergence |

Active-active requires two public IPs on the gateway and two on-premises VPN device endpoints.

---

## Azure Virtual WAN

Virtual WAN (vWAN) is a managed hub-and-spoke networking service that automates branch connectivity, VNet routing, and security at scale across regions.

### vWAN Types

| Type | Features |
|---|---|
| **Basic** | S2S VPN only; no ER, P2S, or Secure Virtual Hub |
| **Standard** | Full feature set: S2S, P2S, ExpressRoute, Secure Virtual Hub, any-to-any routing |

### Virtual Hub

- Managed hub VNet (you do not own the VNet CIDR); address range assigned at creation (e.g., `10.100.0.0/23`)
- Deployed per region; multiple hubs in a vWAN span regions
- Each hub can host: VPN Gateway, ExpressRoute Gateway, P2S Gateway, Azure Firewall (Secure Virtual Hub)

### Secure Virtual Hub

- Azure Firewall deployed inside the vWAN hub
- Managed via **Azure Firewall Manager**: centralized policy across all hubs
- **Routing Intent**: configure all internet and/or private traffic through Azure Firewall automatically
- Replaces manual UDR management in traditional hub-spoke
- Supports third-party NVA in hub (via managed NVA deployment)

### Any-to-Any Routing

vWAN automatically enables routing between all connected entities:
- Branch ↔ Branch (via hub)
- Branch ↔ VNet
- VNet ↔ VNet (within same hub region; cross-hub requires additional config)
- Regional isolation: custom routing tables can segment traffic

### Connectivity Options in vWAN

| Connection Type | Description |
|---|---|
| **VPN sites** | S2S IPsec from branch VPN devices |
| **P2S VPN** | Remote clients via OpenVPN, IKEv2, or SSTP |
| **ExpressRoute circuits** | Connect circuits to vWAN hub ER Gateway |
| **VNet connections** | Peer spoke VNets to the hub |
| **SD-WAN integration** | Partner NVAs (Barracuda, Citrix, VMware SD-WAN) in the hub |

### vWAN Routing Tables

- **Default** route table: all VNet connections and branches use by default
- **None** route table: isolates connection (no routing)
- **Custom** route tables: segment traffic (e.g., isolate dev/prod spokes from each other)
- **Static routes**: add specific prefixes to route tables for on-premises destinations

---

## Azure Route Server

Enables BGP route exchange between an NVA (Network Virtual Appliance) running in a VNet and Azure networking, eliminating the need for manually maintained UDRs.

### How It Works

1. Deploy Route Server in a dedicated `RouteServerSubnet` in hub VNet
2. NVA peers with Route Server via BGP
3. NVA advertises on-premises routes to Route Server
4. Route Server propagates those routes to all peered VNets (spoke VNets)
5. Azure routes are propagated to the NVA, enabling dynamic routing

### Use Cases

- Dynamic routing with third-party NVAs (Cisco, Palo Alto, Check Point, etc.) in hub-spoke
- On-premises route changes automatically reflected in Azure without manual UDR updates
- Multi-NVA active-active configurations with ECMP

### Route Server vs VPN Gateway BGP

- Route Server: for NVA-to-Azure BGP in a VNet (not for on-premises direct connectivity)
- VPN Gateway BGP: for on-premises VPN device-to-Azure BGP (S2S connectivity)
- Route Server + VPN Gateway together: NVA dynamically learns and re-advertises VPN routes

---

## Connectivity Decision Guide

| Scenario | Recommended Solution |
|---|---|
| Single small branch, internet connectivity acceptable | VPN Gateway S2S (VpnGw1 or VpnGw2) |
| Multiple branches, SD-WAN | Azure Virtual WAN with partner SD-WAN NVA |
| Private, high-bandwidth enterprise connection | ExpressRoute Standard/Premium |
| Ultra-high bandwidth (>10 Gbps) | ExpressRoute Direct |
| Remote worker access | VPN Gateway P2S (OpenVPN + Entra ID auth) |
| Multi-region enterprise at scale | Virtual WAN Standard with Secure Virtual Hub |
| Dynamic routing with third-party NVA | Azure Route Server |
