# Azure Network Security & Access — Capabilities

## Overview

This namespace covers network-layer security services: Azure Firewall for stateful inspection and FQDN filtering, Azure Bastion for secure VM access without exposing RDP/SSH to the internet, DDoS Protection for volumetric attack mitigation, and Network Watcher for network monitoring and diagnostics.

---

## Azure Firewall

Azure Firewall is a cloud-native, fully managed stateful firewall service with built-in high availability and unlimited cloud scalability. It is the preferred network security control in hub-spoke and Virtual WAN architectures.

### SKUs

| SKU | Target | Key Features |
|---|---|---|
| **Basic** | Small/dev environments | Network rules, application rules (FQDN), DNAT — no IDPS/TLS inspection |
| **Standard** | Enterprise workloads | Threat intelligence filtering, FQDN tags, custom DNS, DNS proxy, forced tunneling |
| **Premium** | Highly regulated, high-security | Standard + IDPS, TLS inspection, URL filtering, web categories |

### Rule Types (processed in order)

| Rule Type | Layer | Description |
|---|---|---|
| **DNAT Rules** | L4 inbound | Destination NAT: translate inbound traffic to internal IPs (e.g., inbound RDP via public IP) |
| **Network Rules** | L3/L4 | IP/port-based allow/deny; protocol (TCP, UDP, ICMP, Any) |
| **Application Rules** | L7 | FQDN-based (e.g., `*.microsoft.com`), HTTP/HTTPS/MSSQL, with or without TLS inspection |

**Rule priority**: DNAT → Network → Application. Within each type: lower priority number = evaluated first.

### Azure Firewall Manager

Centralized policy management for multiple Azure Firewall instances:
- **Firewall Policy**: standalone resource containing DNAT, network, and application rule collections
- **Policy hierarchy**: parent policy (global) → child policy (regional/team); parent rules cannot be overridden by child
- **Secured Virtual Hub**: Azure Firewall deployed in Virtual WAN hub, managed via Firewall Manager
- **Third-party NVAs**: Firewall Manager supports partner NVAs (Check Point, Palo Alto) in secured hub

### Azure Firewall Premium Features

#### IDPS (Intrusion Detection and Prevention System)

- Signature-based detection of attack patterns (45,000+ signatures, updated automatically)
- Modes per signature: Alert (log only), Deny (block and log), Off
- Category-based filtering: enable/disable entire threat categories (e.g., malware, exploit kits)
- Custom signatures: add organization-specific detection rules

#### TLS Inspection

- Intercepts and decrypts outbound TLS traffic for application rule inspection
- Requires an intermediate CA certificate stored in Key Vault
- Traffic re-encrypted after inspection before forwarding to destination
- Enables FQDN filtering and IDPS on HTTPS traffic (otherwise only SNI is visible)

#### URL Filtering

- Exact URL matching (not just FQDN): `www.example.com/allowed-path` vs `www.example.com/blocked-path`
- Requires TLS inspection for HTTPS traffic

#### Web Categories

- Classify allowed/denied traffic by content category (social media, gambling, malware, etc.)
- Backed by Microsoft's threat intelligence and URL categorization database
- Applied in application rules; supports overrides for specific FQDNs

### Azure Firewall Deployment Patterns

#### Hub-Spoke (Traditional VNet)

```
GatewaySubnet     AzureFirewallSubnet    AzureBastionSubnet
     │                    │                      │
     └────────────────────┴──────────────────────┘
                      Hub VNet
                          │
              ┌───────────┼───────────┐
              │           │           │
           Spoke1      Spoke2      Spoke3
```

- UDRs in all spoke subnets: `0.0.0.0/0` → Azure Firewall private IP (forced tunneling)
- UDR in `GatewaySubnet`: routes to spoke VNet CIDRs via Firewall (optional; prevents bypass)

#### Secure Virtual Hub (Virtual WAN)

- Azure Firewall deployed inside the vWAN hub
- Routing Intent in hub: all internet traffic + private traffic through Firewall automatically
- Eliminates manual UDR management across all spoke VNets

### Threat Intelligence

- IP/domain blocklist maintained by Microsoft Cyber Security division
- Modes: Alert (log and allow), Alert and Deny (log and block)
- Applied before rule collections (highest priority)

### DNS Proxy

- Azure Firewall acts as DNS server for VNet; forwards to Azure DNS or custom DNS
- Required for FQDN-based network rules (resolves FQDNs to IPs for rule matching)
- Configure VNet's DNS servers to point to Firewall private IP

### FQDN Tags

Pre-built groups of FQDNs for Microsoft services:
- `WindowsUpdate`, `Windows Diagnostics`, `MicrosoftActiveProtectionService`, `AppServiceEnvironment`, etc.
- Use in application rules to allow service traffic without maintaining IP lists

---

## Azure Bastion

Azure Bastion provides browser-based RDP and SSH access to VMs over TLS (port 443) without requiring public IPs on VMs, VPN connections, or jump servers exposed to the internet.

### Architecture

- Deployed into a dedicated `AzureBastionSubnet` (minimum `/26`) within the VNet
- Connects to VM's private IP using the Azure backbone
- Client connects to Azure portal or native client; Bastion handles RDP/SSH proxying
- VMs require no public IP, no NSG rule for RDP/SSH from internet

### SKUs

| Feature | Basic | Standard | Premium |
|---|---|---|---|
| RDP/SSH via browser | Yes | Yes | Yes |
| Shareable link | No | Yes | Yes |
| Scale units (concurrent sessions) | 2 (25 sessions) | Up to 50 scale units | Up to 50 scale units |
| Native client support | No | Yes | Yes |
| File transfer (up/down) | No | Yes | Yes |
| Copy/paste | Text only | Full (file in Standard) | Full |
| IP-based connection | No | Yes (connect by IP, not VM resource) | Yes |
| Private-only Bastion | No | No | Yes |
| Session recording | No | No | Yes |
| Audit logs | No | No | Yes |

### Key Features

- **Native client support (Standard+)**: use local RDP/SSH client (mstsc, OpenSSH) via Bastion tunnel instead of browser; better performance and feature parity
- **Shareable link**: generate time-limited link for accessing a specific VM without requiring portal access
- **IP-based connection**: connect to any VM private IP in VNet or peered VNets without specifying VM resource ID
- **Session recording (Premium)**: capture and store RDP/SSH sessions for compliance and audit
- **Private-only Bastion (Premium)**: deploy without a public IP; access Bastion itself via Private Endpoint

### NSG Requirements for Bastion

For the `AzureBastionSubnet`:
- Inbound: Allow `GatewayManager` on 443, Allow `AzureLoadBalancer` on 443, Allow `Internet` on 443 (for browser clients)
- Outbound: Allow `VirtualNetwork` on 3389, 22; Allow `AzureCloud` on 443

### Connecting via Azure CLI (Bastion Tunnel)

```bash
az network bastion ssh --name myBastion --resource-group myRG --target-resource-id <vmId> --auth-type AAD
az network bastion rdp --name myBastion --resource-group myRG --target-resource-id <vmId>
az network bastion tunnel --name myBastion --resource-group myRG --target-resource-id <vmId> --resource-port 22 --port 2222
```

---

## DDoS Protection

Azure DDoS Protection defends against distributed denial-of-service attacks targeting Azure public IPs.

### Protection Tiers

| Tier | Cost | Coverage | SLA Guarantee | Features |
|---|---|---|---|---|
| **Network Protection** (formerly Standard) | ~$2,944/month + data | All public IPs in the VNet | Yes | Adaptive tuning, attack analytics, rapid response, cost protection |
| **IP Protection** | ~$199/month per protected IP | Single public IP resource | Yes | Same protection as Network, per-IP billing |
| **Infrastructure Protection** (free) | Free | All Azure resources | No | Basic volumetric attack mitigation only; no telemetry |

> DDoS Network Protection covers all public IPs within protected VNets in the subscription (not just one VNet).

### Attack Types Mitigated

| Attack Type | Description |
|---|---|
| **Volumetric** | Flood attacks (UDP floods, ICMP floods, spoofed floods); exhaust network bandwidth |
| **Protocol** | Exploit weaknesses in L3/L4 (SYN floods, reflected UDP attacks, Smurf attacks) |
| **Resource (Application) layer** | HTTP/HTTPS floods targeting application logic; requires WAF (App Gateway/AFD) for full coverage |

### Key Features (Network/IP Protection)

- **Adaptive real-time tuning**: baselines normal traffic patterns per public IP and triggers on anomalies
- **Attack telemetry**: real-time metrics in Azure Monitor; alert on `Under DDoS attack` metric
- **Attack analytics**: post-attack reports with attack vectors, traffic volumes, and mitigation actions
- **DDoS Rapid Response (DRR) team**: direct access to Microsoft security engineers during active attacks (Network Protection only)
- **Cost protection credit**: Azure credit for scale-out costs incurred during attack (Network Protection only)
- **Multi-layered defense**: combine with Azure Firewall and Application Gateway WAF for L3–L7 coverage

### DDoS Diagnostic Logs

- `DDoSProtectionNotifications`: alerts when public IP is under attack or protection disabled
- `DDoSMitigationFlowLogs`: detailed flow-level data during active mitigation
- `DDoSMitigationReports`: aggregated reports on active attacks
- Send to Log Analytics, Storage Account, or Event Hub

---

## Network Watcher

Network Watcher is a suite of network monitoring, diagnostic, and logging tools for Azure virtual networks.

### Diagnostics Tools

| Tool | Purpose |
|---|---|
| **IP Flow Verify** | Check if a packet is allowed/denied by NSG rules for a specific flow (5-tuple) |
| **Next Hop** | Determine next hop type and IP for a packet from a VM to a destination IP |
| **Security Group View** | List all NSG rules applied to a VM NIC and associated subnet |
| **VPN Troubleshoot** | Diagnose VPN Gateway and connection issues; retrieve logs |
| **Connection Troubleshoot** | Test connectivity from VM to endpoint (VM, FQDN, port); returns hop-by-hop path |
| **Packet Capture** | Capture packets on VM NIC; filter by IP, port, protocol; store to Storage or VM |
| **Network Topology** | Visual representation of resources and connections in a VNet |

### Monitoring Tools

| Tool | Purpose |
|---|---|
| **NSG Flow Logs** | Per-flow logs for allowed/denied traffic through NSGs (v1: basic, v2: with bytes/packets) |
| **Traffic Analytics** | Log Analytics-based analysis of NSG flow logs; geo-maps, top talkers, flow trends |
| **Connection Monitor** | Continuous probing between sources (VMs, VMSS, on-premises via VPN/ER) and destinations; latency and packet loss over time |
| **Network Performance Monitor** (legacy) | Being replaced by Connection Monitor |

### IP Flow Verify Details

- Input: VM resource ID, direction (Inbound/Outbound), protocol, local IP/port, remote IP/port
- Output: which NSG rule (allow/deny) matched the flow and its name
- Use case: debugging connectivity issues — find which NSG rule is blocking traffic

### Connection Monitor

- Replaces legacy Network Performance Monitor and Connection Troubleshoot (one-time tests)
- Continuous end-to-end monitoring; results in Log Analytics
- Sources: Azure VMs, VMSS, Arc-enabled on-premises servers
- Destinations: URL, IP address, Azure resource (by ARM ID)
- Metrics: checks per minute, round-trip latency, packet loss percentage
- Alerts: Azure Monitor alerts on connectivity degradation

### Packet Capture

- Agent-based (Network Watcher extension on VM) or agentless (for supported VMs)
- Capture filters: local IP, remote IP, local port, remote port, protocol
- Storage: Azure Storage Account blob (for analysis) or local file on VM
- Maximum capture duration: 5 hours; maximum file size: 1 GB
- Download and analyze with Wireshark or similar tools
