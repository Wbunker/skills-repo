# AWS Transit Gateway — Capabilities Reference
For CLI commands, see [transit-gateway-cli.md](transit-gateway-cli.md).

## AWS Transit Gateway

**Purpose**: Regional hub-and-spoke network transit service that simplifies connecting multiple VPCs, VPNs, and Direct Connect connections without full-mesh peering.

### Attachment Types

| Attachment | Description |
|---|---|
| **VPC** | Attach a VPC; requires at least one subnet per AZ for the TGW ENI |
| **VPN** | Attach a Site-to-Site VPN; supports BGP or static routing |
| **Direct Connect Gateway** | Attach via a transit VIF; enables hybrid connectivity |
| **Transit Gateway peering** | Connect two TGWs (same or different regions/accounts) using static routing |
| **Connect** | Attach SD-WAN appliances or network function VMs via GRE/BGP for higher throughput |

### Route Tables

- Each TGW has a **default route table** used by all new attachments unless customized
- Create **additional route tables** to isolate traffic (e.g., separate production and development VPCs; spoke VPCs that can reach shared services but not each other)
- Each attachment has exactly **one association** (route table it routes from) and optionally one or more **propagations** (route tables it advertises routes to)
- BGP propagation: VPN and Direct Connect Gateway attachments propagate routes dynamically; VPC attachments require static routes

### MTU

| Connection type | MTU |
|---|---|
| VPC, Direct Connect, TGW Connect, peering | 8500 bytes |
| VPN connections | 1500 bytes |

### Key Features

| Feature | Description |
|---|---|
| **Multicast** | Enable multicast on a TGW; create multicast domains; associate VPC subnets; sources and group members are ENIs |
| **Network Manager** | Centralized dashboard to monitor global network topology across TGWs, VPNs, and Direct Connect; integrates with SD-WAN |
| **Inter-region peering** | Peer TGWs across regions for global connectivity; uses AWS global backbone; static routes only; no transitive routing between peered TGWs |
| **Encryption control** | Enforce encryption-in-transit for all traffic across attached VPCs |
| **Flexible cost allocation** | Data processing charges allocated to the source attachment account; configurable |
