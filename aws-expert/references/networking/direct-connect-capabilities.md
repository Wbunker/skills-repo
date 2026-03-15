# AWS Direct Connect — Capabilities Reference
For CLI commands, see [direct-connect-cli.md](direct-connect-cli.md).

## AWS Direct Connect

**Purpose**: Dedicated private network connection between your on-premises environment and AWS, bypassing the public internet for consistent performance and reduced data transfer costs.

### Connection Types

| Type | Description |
|---|---|
| **Dedicated connection** | Physical connection from 1 Gbps to 400 Gbps; ordered directly from AWS; you receive a dedicated port |
| **Hosted connection** | Sub-1 Gbps (50 Mbps–500 Mbps) or 1–10 Gbps; provisioned by an AWS Direct Connect Partner; faster to provision |

**Physical requirements**: Single-mode fiber; 1000BASE-LX (1G), 10GBASE-LR (10G), 100GBASE-LR4 (100G), 400GBASE-LR4 (400G). BGP with MD5 authentication. 802.1Q VLAN encapsulation.

### Virtual Interfaces (VIFs)

| VIF Type | Access | Use |
|---|---|---|
| **Private VIF** | A single VPC via Virtual Private Gateway | Connect to private IP resources in one VPC in the same region |
| **Public VIF** | All AWS public IPs globally | Access all AWS public endpoints (S3, DynamoDB, EC2 public IPs) over Direct Connect |
| **Transit VIF** | One or more Transit Gateways via Direct Connect Gateway | Connect to multiple VPCs across regions and accounts |

### Direct Connect Gateway

- Global resource; no regional constraint
- Associates with private VIFs or transit VIFs
- Enables access to VPCs across multiple regions and multiple AWS accounts from a single Direct Connect connection
- **SiteLink**: Routes traffic between on-premises locations through AWS Direct Connect Gateway without traversing AWS Regions (Direct Connect location to Direct Connect location)

### Resilience Recommendations

| Level | Architecture |
|---|---|
| **Development** | Single connection at a single location |
| **High resilience** | Two connections at a single location; protects against device failure |
| **Maximum resilience** | Two connections each at two separate Direct Connect locations; protects against location failure |

### Link Aggregation Groups (LAG)

- Aggregate multiple Direct Connect connections into a single managed connection
- All connections in a LAG must use the same bandwidth and terminate at the same Direct Connect endpoint
- Provides increased bandwidth and failover within the LAG
