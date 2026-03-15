# Hybrid Connectivity — Capabilities Reference

## Purpose

Hybrid connectivity products connect on-premises networks, other cloud provider networks, and GCP VPCs. The primary products are Cloud Interconnect (dedicated physical connections) and Cloud VPN (IPsec VPN tunnels). Network Connectivity Center provides a hub-and-spoke model for managing these connections at scale.

---

## Cloud Interconnect

Cloud Interconnect provides high-bandwidth, low-latency, dedicated connectivity between your on-premises network and Google's network. Traffic does not traverse the public internet.

### Dedicated Interconnect

| Feature | Description |
|---|---|
| Bandwidth | 10 Gbps or 100 Gbps per circuit |
| Physical connection | Direct cross-connect at a Google colocation facility (PoP) |
| Availability | Google PoPs: 20+ locations globally in major data center campuses |
| Latency | Lower than internet; deterministic (no internet routing variability) |
| SLA | 99.99% with four connections in dual-metro configuration; 99.9% with single connection |
| Private Google Access | Reach all Google APIs privately (not via internet) using routes on the Interconnect |
| VLAN attachments | Each circuit creates a VLAN attachment (Layer 2); up to 16 VLAN attachments per circuit |

**Redundancy configurations**:
- 99.99% SLA: 4 circuits, 2 metros, 2 circuits per metro (each metro has 2 connections to separate Google facilities)
- 99.9% SLA: 2 circuits in the same metro (2 separate edge availability domains)
- <99.9%: single circuit (no SLA)

### Partner Interconnect

For locations not co-located in a Google PoP, or for lower bandwidth requirements:

| Feature | Description |
|---|---|
| Bandwidth | 50 Mbps to 50 Gbps (determined by service provider offering) |
| Connection | Via a service provider (Equinix, AT&T, Lumen, etc.) that has a presence at Google PoPs |
| SLA | 99.99% with dual partner connections; 99.9% with single |
| Setup | Create VLAN attachment in GCP → share pairing key with provider → provider configures their side |
| Activation | After provider activates the circuit; test connectivity |

### Cross-Cloud Interconnect

Dedicated connections to other cloud providers:

| Provider | Description |
|---|---|
| AWS | Dedicated connection between GCP and AWS Direct Connect location |
| Azure | Dedicated connection to Azure ExpressRoute |
| Oracle | Dedicated connection to Oracle Cloud FastConnect |
| Alicloud | Dedicated connection to Alibaba Cloud Express Connect |

Provides lower latency, higher bandwidth, and more consistent throughput than internet-based connectivity for multi-cloud architectures.

---

## Cloud VPN

Cloud VPN provides IPsec VPN tunnels between on-premises networks (or other cloud VPCs) and GCP VPCs over the public internet.

### HA VPN (Recommended)

| Feature | Description |
|---|---|
| SLA | 99.99% availability |
| Architecture | Two HA VPN gateways in GCP; each gateway has two interfaces (external IPs). Minimum two tunnels required for 99.99% SLA |
| Tunnel bandwidth | Up to 3 Gbps per tunnel; aggregate multiple tunnels for higher throughput |
| Routing | BGP dynamic routing via Cloud Router (recommended); static routing also supported |
| IKE | IKEv1 and IKEv2 supported |
| Encryption | AES-128 or AES-256 |

**HA VPN tunnel pairs**: A fully redundant HA VPN setup requires at minimum:
- 1 GCP HA VPN gateway (has 2 interfaces)
- 1 peer VPN gateway (on-premises or other cloud)
- 2 VPN tunnels (one from each GCP interface to the peer gateway)

For maximum redundancy:
- 1 GCP HA VPN gateway
- 2 peer VPN gateways (in different physical locations)
- 4 VPN tunnels (GCP interface 0 → peer 1, GCP interface 0 → peer 2, GCP interface 1 → peer 1, GCP interface 1 → peer 2)

### Classic VPN (Legacy)

| Feature | Description |
|---|---|
| SLA | 99.9% (single tunnel) |
| Architecture | Single VPN gateway with one external IP; one or more tunnels |
| Routing | Static (policy-based) or dynamic BGP (with Cloud Router) |
| Bandwidth | Up to 3 Gbps per tunnel |
| Use case | Legacy setups; when peer device only supports a single endpoint |

**Classic VPN is deprecated for new deployments.** Use HA VPN.

---

## Cloud Router

Cloud Router manages BGP sessions for dynamic routing with VPN and Interconnect:

| Feature | Description |
|---|---|
| BGP ASN | Assign a private ASN to Cloud Router (64512–65534 or 4200000000–4294967294) |
| Route advertisement | Advertise GCP subnet routes to on-premises via BGP; learn on-premises routes |
| Custom route advertisement | Advertise specific CIDRs (beyond subnets) — used for Private Google Access ranges, aggregated routes |
| Regional scope | One Cloud Router per region; manages all dynamic routes for VPN tunnels and Interconnect VLAN attachments in that region |
| Global routing mode | With VPC global routing mode, Cloud Router in one region can learn and distribute routes from all regions |
| NAT integration | Cloud Router hosts Cloud NAT configurations |

---

## Network Connectivity Center (NCC)

NCC provides a hub-and-spoke model for connecting multiple networks:

| Concept | Description |
|---|---|
| Hub | Central resource in a GCP project that manages the topology |
| Spoke | A network resource (VPN tunnel, Interconnect VLAN attachment, VPC network, appliance) connected to the hub |
| VPC spoke | Connects a GCP VPC to the hub |
| VPN spoke | Connects HA VPN tunnels to the hub |
| Interconnect spoke | Connects Interconnect VLAN attachments to the hub |
| Router appliance spoke | Connects a GCE VM running a third-party router/firewall (SD-WAN appliance) to the hub |

**NCC use cases**:
- Connect multiple on-premises sites to a central GCP hub (replacing full-mesh VPN/Interconnect)
- Enable transitive routing between spokes (site A → hub → site B)
- SD-WAN integration via router appliance spokes
- Centralize network connectivity management

---

## Hybrid Connectivity Decision Guide

| Scenario | Recommendation |
|---|---|
| Production, dedicated, high bandwidth (>1 Gbps) | Dedicated Interconnect (if co-located at Google PoP) |
| Production, not at Google PoP, <50 Gbps | Partner Interconnect |
| Dev/test, small data transfer, quick setup | HA VPN |
| On-premises to GCP, <1 Gbps, acceptable internet latency | HA VPN |
| Multi-cloud (AWS ↔ GCP) at high bandwidth | Cross-Cloud Interconnect |
| Multi-site WAN with SD-WAN appliances | Network Connectivity Center with Router Appliance spokes |
| Connect multiple on-prem sites to GCP hub | Network Connectivity Center (VPN or Interconnect spokes) |

---

## Private Google Access over Hybrid Connectivity

When connected to GCP via Interconnect or VPN, on-premises hosts can reach Google APIs without going through the internet:

1. Configure `private.googleapis.com` or `restricted.googleapis.com` DNS to resolve to `199.36.153.8/30` or `199.36.153.4/30`
2. Advertise a route to those ranges via Cloud Router to on-premises
3. On-premises requests to `storage.googleapis.com`, `bigquery.googleapis.com`, etc. route through the VPN/Interconnect without internet exposure

---

## MTU Considerations

| Connection Type | Recommended MTU |
|---|---|
| Dedicated Interconnect | 1500 (jumbo frames up to 8896 supported on some configs) |
| Partner Interconnect | 1440 (overhead for provider tagging) |
| HA VPN | 1460 (1500 minus 40 bytes for IPsec/IKE headers) |
| Classic VPN | 1460 |

Set MTU on the VPC subnet to match the connection type. Mismatched MTU causes packet fragmentation and reduced throughput.

---

## Important Constraints

- **Dedicated Interconnect requires physical presence at a Google PoP**: You or your colocation provider must have space in a supported facility. Not available in all locations — check Google's PoP list.
- **VLAN attachment provisioning time**: After ordering Dedicated Interconnect, physical cross-connect provisioning takes days to weeks. Partner Interconnect can be faster.
- **HA VPN BGP sessions**: Each tunnel requires a BGP session with a separate BGP peer IP (/30 or /29 link-local range for each tunnel). Plan IP space accordingly.
- **Cloud Router ASN**: Once set, Cloud Router ASN cannot be changed without deleting and recreating the Cloud Router.
- **Routing convergence**: BGP convergence after a link failure takes 60–90 seconds by default. Use BFD (Bidirectional Forwarding Detection) to reduce failover time to ~1 second.
- **VPN throughput per tunnel**: Maximum 3 Gbps per tunnel. Use ECMP (multiple tunnels) for higher aggregate throughput.
