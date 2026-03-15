# AWS VPC — Capabilities Reference
For CLI commands, see [vpc-cli.md](vpc-cli.md).

## Amazon VPC

**Purpose**: Provision a logically isolated virtual network within AWS where you define the IP space, subnets, routing, and network controls.

### Core Concepts

| Concept | Description |
|---|---|
| **VPC** | Logically isolated virtual network; no charge for the VPC itself |
| **CIDR block** | IPv4 or IPv6 address range assigned to the VPC (e.g., `10.0.0.0/16`); up to 5 CIDR blocks per VPC |
| **Subnet** | Range of IPs within a VPC; must reside in a single Availability Zone |
| **Public subnet** | Has a route to an Internet Gateway; resources can have public IPs |
| **Private subnet** | No direct internet route; use NAT Gateway for outbound internet access |
| **Isolated subnet** | No internet route and no NAT; purely internal (e.g., database tier) |
| **Route table** | Determines where traffic is directed from subnets or gateways; each subnet associates with exactly one route table |
| **Internet Gateway (IGW)** | Enables two-way internet communication for resources with public IPs; horizontally scaled, redundant, no bandwidth constraints |
| **NAT Gateway** | AWS-managed NAT; allows private subnet resources to initiate outbound internet connections; charged per hour + data; not suitable for inbound |
| **NAT instance** | EC2 instance running NAT software; you manage patching and HA; cheaper at low traffic but operationally heavier |
| **Default VPC** | Pre-configured VPC in every region per account; all subnets public by default |

### Security Controls

| Control | Stateful? | Scope | Evaluation |
|---|---|---|---|
| **Security group** | Stateful (return traffic automatically allowed) | Network interface (instance level) | All rules evaluated; implicit deny |
| **Network ACL (NACL)** | Stateless (return traffic must be explicitly allowed) | Subnet level | Rules evaluated in ascending numeric order; first match wins |

**Security Group rule components**: protocol, port range, source (IP/CIDR/security group ID) for inbound; protocol, port range, destination for outbound.

**NACL rule numbering**: Rules numbered 1–32766; recommended to use increments of 10 or 100 to allow insertion. One NACL can associate with multiple subnets; a subnet has exactly one NACL.

**Ephemeral ports**: Because NACLs are stateless, outbound NACL rules must allow ephemeral ports (1024–65535) to permit response traffic from the internet to your instances.

### VPC Connectivity Options

| Option | Use case |
|---|---|
| **VPC Peering** | Direct, private routing between two VPCs (same account, cross-account, cross-region); **no transitive routing**; no overlapping CIDRs |
| **Transit Gateway** | Hub-and-spoke for connecting many VPCs and on-premises; supports transitive routing |
| **VPC Endpoints (Gateway)** | Private access to S3 and DynamoDB; free; uses route table entries |
| **VPC Endpoints (Interface)** | Private access to AWS services and endpoint services via ENI with private IP (PrivateLink) |
| **Site-to-Site VPN** | Encrypted tunnel over the internet to on-premises; uses virtual private gateway or Transit Gateway |
| **Direct Connect** | Dedicated physical connection to AWS |

### VPC Peering Limitations

- **No transitive routing**: If VPC A peers with VPC B and VPC B peers with VPC C, VPC A cannot reach VPC C through B.
- **No overlapping CIDR blocks**: Peered VPCs must have non-overlapping IP ranges.
- **Route table entries required**: Both sides must add routes for the other VPC's CIDR pointing to the peering connection.
- **Inter-region peering**: Supported; traffic is encrypted in transit and stays on the AWS global backbone.

### VPC Endpoints

| Type | Services | Mechanism |
|---|---|---|
| **Gateway endpoint** | S3, DynamoDB only | Route table entry; free; no PrivateLink |
| **Interface endpoint** | 100+ AWS services, endpoint services | ENI with private IP; per-hour + data charges; DNS resolution |
| **Gateway Load Balancer endpoint** | Inline virtual appliances | Route table; redirects traffic through GWLB |

**Interface endpoint DNS**: Private DNS enabled by default; overrides the service's public DNS to resolve to the endpoint's private IP within the VPC.

### Additional VPC Features

| Feature | Description |
|---|---|
| **VPC Flow Logs** | Capture metadata about IP traffic to/from network interfaces; publish to CloudWatch Logs, S3, or Kinesis Firehose; does not capture packet payload |
| **Traffic Mirroring** | Copy actual packet data from ENIs for deep packet inspection; targets can be ENIs or NLBs |
| **VPC Sharing (RAM)** | Share subnets with other accounts in the same AWS Organization using AWS Resource Access Manager; owner manages the VPC/subnets; participants launch resources into shared subnets |
| **DHCP Options Sets** | Customize domain name, DNS servers (up to 4), NTP servers, NetBIOS settings for the VPC; only one DHCP option set per VPC at a time |
| **Elastic IP (EIP)** | Static public IPv4 address; associated with an account until explicitly released; charged when allocated but not associated |
| **IPv6** | Dual-stack or IPv6-only subnets; Egress-Only Internet Gateway for IPv6 outbound-only (equivalent of NAT for IPv6) |
