# AWS Lightsail / Edge Compute — Capabilities Reference

For CLI commands, see [lightsail-graviton-outposts-cli.md](lightsail-graviton-outposts-cli.md).

## Amazon Lightsail

**Purpose**: Simplified cloud platform with predictable monthly pricing for virtual servers, databases, object storage, CDN, and managed containers; designed for simpler workloads and developers getting started with AWS.

### Core Concepts

| Concept | Description |
|---|---|
| **Instance** | Virtual server with a fixed bundle (CPU, RAM, SSD, transfer); billed monthly |
| **Blueprint** | OS or application image (Amazon Linux, Ubuntu, WordPress, LAMP, Node.js, etc.) |
| **Bundle** | Instance size with fixed CPU, RAM, storage, and data transfer allowance |
| **Static IP** | Free static IPv4 address attached to an instance (charged only if unattached) |
| **Snapshot** | Point-in-time backup of an instance or disk; used for recovery or migration |

### Key Differences from EC2

| | Lightsail | EC2 |
|---|---|---|
| Pricing | Fixed monthly bundles | Pay-per-second, many variables |
| Networking | Simplified; data transfer included | Complex VPC; separate transfer billing |
| Instance variety | Limited curated bundles | Hundreds of instance types |
| Management | Simplified console | Full AWS console |
| VPC integration | Peering to VPC available | Native VPC |
| Use case | Simple apps, dev/test, WordPress | Any workload |

### Additional Lightsail Services

- **Managed databases**: MySQL and PostgreSQL with automatic backups and failover
- **Object storage**: S3-compatible buckets with CDN integration
- **CDN distributions**: CloudFront-backed content delivery
- **Load balancers**: Simple HTTP/HTTPS load balancing with TLS termination
- **Container services**: Run Docker containers without managing infrastructure

---

## AWS Graviton

See [aws-silicon-capabilities.md](aws-silicon-capabilities.md) for full Graviton coverage.

---

## AWS Outposts

**Purpose**: Extends AWS infrastructure, services, APIs, and tools to your on-premises facility; enables hybrid architectures with the same AWS APIs and tooling used in the cloud.

### Form Factors

| Form Factor | Size | Compute Scale |
|---|---|---|
| **Outposts Rack** | 42U industry-standard rack | Full server rack; supports widest service set |
| **Outposts Server** | 1U or 2U server | Smaller footprint; for space-constrained sites |

### Supported Services on Outposts Rack

EC2 instances, EBS volumes, ECS clusters, EKS nodes, RDS, ElastiCache, EMR, S3, VPC subnets, ALB, Route 53

### Key Concepts

| Concept | Description |
|---|---|
| **Service Link** | Network route connecting Outpost back to the parent AWS Region; required for operation |
| **Local Gateway (LGW)** | Virtual router enabling communication between Outpost rack and on-premises network |
| **Outpost subnet** | VPC subnet associated with an Outpost; resources in this subnet run on the Outpost |

### Use Cases

- Low-latency workloads requiring proximity to on-premises data or systems
- Local data processing for regulatory or data residency requirements
- Hybrid applications spanning on-premises and AWS regions
- Migration of on-premises workloads using familiar AWS APIs

### Constraints

- Requires a reliable network connection back to the parent AWS Region (Service Link)
- Cannot connect an Outpost to a Local Zone within the same VPC
- AWS owns and manages the hardware; you provide the facility

---

## AWS Local Zones

**Purpose**: Extension of an AWS Region placed closer to large population and industry centers, allowing you to run latency-sensitive applications closer to end users.

### Key Concepts

| Concept | Description |
|---|---|
| **Local Zone** | An extension of a parent AWS Region in a different geographic location (e.g., Los Angeles as an extension of us-west-2) |
| **Opt-in** | Local Zones are not enabled by default; you opt in per Local Zone |
| **Subnet** | Create a subnet in a Local Zone to place resources there; uses the parent Region's VPC |

### Supported Services (subset)

EC2 instances, EBS, ECS, EKS, ALB, VPC, ElastiCache, RDS (limited), FSx

### Use Cases

- Single-digit millisecond latency to users in a metro area
- Media and entertainment: live video production, rendering
- Real-time gaming, financial trading applications
- AR/VR content delivery

### vs. Outposts / Wavelength

| | Local Zones | Outposts | Wavelength |
|---|---|---|---|
| Location | AWS-operated edge facility | Customer premises | 5G carrier edge |
| Ownership | AWS | AWS (hardware on your site) | AWS |
| Latency target | Single-digit ms to metro users | Ultra-low ms to on-premises systems | Sub-ms to 5G devices |
| Use case | Latency to end users in a city | Hybrid on-premises | 5G mobile edge computing |

---

## AWS Wavelength

**Purpose**: Embeds AWS compute and storage within 5G carrier networks, enabling ultra-low latency applications for mobile and connected devices.

### Key Concepts

| Concept | Description |
|---|---|
| **Wavelength Zone** | An AWS infrastructure deployment embedded in a telecommunications provider's 5G network |
| **Carrier gateway** | Provides connectivity from Wavelength Zone to the carrier network and internet |
| **Carrier IP** | Public IP address from the carrier's address space; assigned to instances for 5G traffic |

### How It Works

1. Deploy EC2 instances in a Wavelength Zone subnet
2. Mobile devices on the 5G network connect directly to the carrier gateway
3. Traffic does not leave the carrier network before reaching your application
4. Wavelength Zone connects back to the parent AWS Region via the carrier backbone

### Use Cases

- Real-time game streaming to mobile devices
- Live video streaming and content delivery to 5G devices
- AR/VR applications requiring sub-10ms latency
- Connected vehicle and IoT processing at the network edge
- Interactive live events (sports, concerts)

### Supported Services

EC2 instances, EBS, ECS, EKS, VPC subnets, ALB
