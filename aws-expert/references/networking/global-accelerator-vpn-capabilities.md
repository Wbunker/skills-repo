# AWS Global Accelerator & VPN — Capabilities Reference
For CLI commands, see [global-accelerator-vpn-cli.md](global-accelerator-vpn-cli.md).

## AWS Global Accelerator

**Purpose**: Improve availability and performance of applications by routing traffic through the AWS global network using anycast static IP addresses, reducing exposure to the public internet.

### Core Concepts

| Concept | Description |
|---|---|
| **Accelerator** | Top-level resource; provides two static anycast IPv4 addresses (or four for dual-stack); traffic enters AWS network at the nearest edge location |
| **Static IPs** | Global fixed IPs that remain assigned even if the accelerator is disabled; permanently released on accelerator deletion; BYOIP supported |
| **Listener** | Accepts traffic on specified ports/protocols (TCP or UDP) |
| **Endpoint group** | Regional collection of endpoints; one endpoint group per AWS region |
| **Traffic dial** | Per endpoint group percentage (0–100%); reduce to 0% to shift traffic away from a region without removing endpoints (useful for maintenance or failover testing) |
| **Endpoint** | ALB, NLB, EC2 instance, or Elastic IP registered in an endpoint group |
| **Client affinity** | `NONE` (default, distributes across healthy endpoints) or `SOURCE_IP` (routes the same source IP to the same endpoint) |

### Accelerator Types

| Type | Description |
|---|---|
| **Standard** | Improve availability and performance; routes to nearest healthy endpoint group |
| **Custom routing** | Map specific ports to specific destination EC2 instances; deterministic routing for gaming, real-time communication |

### Key Features

- **Health-based routing**: Automatically re-routes to healthy endpoints when failures are detected (near-instant failover, within seconds)
- **Global network**: Traffic travels over AWS backbone from ingress edge location to endpoint region; avoids congested public internet paths
- **ARC integration**: Respects Application Recovery Controller zonal shifts and autoshift for multi-AZ failover
- **DDoS protection**: Protected by AWS Shield Standard by default; eligible for Shield Advanced

### Global Accelerator vs. CloudFront

| | CloudFront | Global Accelerator |
|---|---|---|
| Layer | L7 (HTTP/HTTPS) | L4 (TCP/UDP) |
| Caching | Yes | No |
| Use case | Static/dynamic content delivery | Non-HTTP protocols, IP whitelisting, fast regional failover |
| Static IPs | No (uses DNS) | Yes (anycast) |

---

## AWS VPN

**Purpose**: Encrypted connectivity between your on-premises network or client devices and your AWS VPC or Transit Gateway.

### Site-to-Site VPN

| Concept | Description |
|---|---|
| **Customer Gateway (CGW)** | AWS resource representing your on-premises VPN device; configured with its public IP and routing type |
| **Virtual Private Gateway (VGW)** | AWS-side VPN concentrator attached to a single VPC |
| **Transit Gateway (TGW) attachment** | Preferred for connecting multiple VPCs; attach VPN to TGW instead of VGW |
| **VPN connection** | Two IPsec tunnels between CGW and VGW/TGW for redundancy; each tunnel terminates at a different AWS endpoint in different AZs |
| **IKEv1 / IKEv2** | Both supported; IKEv2 recommended for improved security and reliability |
| **BGP routing** | Dynamic routing; automatically exchange routes; required for Transit Gateway VPN |
| **Static routing** | Manually specify remote network CIDRs; simpler for single-VPC VGW setups |
| **Accelerated VPN** | Route VPN traffic through Global Accelerator for improved performance; available with TGW attachment |

### AWS Client VPN

| Concept | Description |
|---|---|
| **Client VPN endpoint** | Managed OpenVPN-based endpoint; associated with a VPC and subnets |
| **Authentication** | Active Directory (mutual auth), certificate-based (mutual TLS), SAML/SSO (federated) |
| **Authorization rules** | Network-based rules controlling which clients can access which subnets/CIDRs |
| **Split tunneling** | Enable to send only VPC-bound traffic through the VPN; all other traffic uses client's internet directly |
| **Client CIDR** | Non-overlapping CIDR block assigned to connecting clients |
