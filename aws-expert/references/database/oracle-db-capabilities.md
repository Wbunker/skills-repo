# Oracle Database@AWS — Capabilities Reference
For CLI commands, see [oracle-db-cli.md](oracle-db-cli.md).

## Oracle Database@AWS

**Purpose**: Oracle Exadata infrastructure physically hosted inside AWS data centers, managed by Oracle Cloud Infrastructure (OCI), and connected to customer VPCs via private networking. Enables enterprises to run Oracle Database workloads — including RAC, Data Guard, and Autonomous Database — with low-latency access to AWS services, without re-platforming or giving up Oracle features.

---

### Core Concepts

| Concept | Description |
|---|---|
| **OCI Child Site** | An OCI availability domain physically located in an AWS data center (AZ). AWS hosts the hardware; OCI provisions and maintains it. |
| **Oracle Exadata Infrastructure** | The underlying platform of database servers and storage servers interconnected via RDMA over Converged Ethernet (RoCE). Pre-configured, full-stack hardware+software. |
| **ODB Network** | A private, isolated network (with a CIDR range) that hosts Exadata VM Clusters and Autonomous VM Clusters within a single AWS AZ. Separate from VPCs. |
| **ODB Peering** | A network connection between an Amazon VPC and an ODB Network. Enables EC2 instances to communicate with Exadata databases privately, without traversing the internet. Not the same as VPC peering. |
| **Cloud VM Cluster** | A set of tightly coupled Exadata VMs, each with Oracle Database Enterprise Edition, Oracle RAC, and Oracle Grid Infrastructure installed. Customer manages the database layer. |
| **Autonomous VM Cluster** | Exadata VMs running Oracle Autonomous AI Database. Oracle manages the full stack — infrastructure, OS, Grid, and database — including patching, scaling, and backups. |
| **Exadata Database Service** | The non-autonomous tier: Oracle manages cloud automation; the customer manages the Oracle database, patching schedule, and configuration. |
| **Oracle Autonomous AI Database** | Fully managed, machine-learning-driven database service on Exadata. No human database administration required. |

---

### Key Features

| Feature | Description |
|---|---|
| **Oracle RAC** | Real Application Clusters available out of the box on VM Clusters; not available in RDS for Oracle |
| **Oracle Grid Infrastructure** | Included in every Exadata VM Cluster; provides cluster management, ASM storage, and RAC |
| **Data Guard** | Supported for physical standby and hybrid DR configurations (on-premises ↔ Oracle Database@AWS) |
| **GoldenGate** | Supported for CDC-based replication and low-downtime migrations into and out of the service |
| **Oracle Zero Downtime Migration (ZDM)** | Supported migration tool; automates Data Guard, RMAN, or GoldenGate-based migrations |
| **Autonomous Recovery Service** | Oracle-managed backup service for Exadata Database Service workloads |
| **Amazon S3 backup integration** | Mandatory S3 access for managed backups; optional direct S3 access for import/export |
| **Zero-ETL with Amazon Redshift** | Real-time replication from Oracle Database@AWS to Redshift with no ETL pipeline; no cross-network egress charges |
| **AWS KMS for TDE** | Transparent Data Encryption master keys managed through AWS KMS for unified key management |
| **Amazon CloudWatch** | Performance and operational metrics available via CloudWatch |
| **Amazon EventBridge** | Automation triggers on database events |
| **VPC Lattice integration** | Connect services across VPCs and on-premises to ODB networks; access S3 and Redshift from Exadata workloads |
| **AWS Transit Gateway / Cloud WAN** | Route traffic from ODB networks to multiple VPCs or on-premises through a central gateway |
| **IAM integration** | IAM roles can be associated to ODB resources |
| **AWS Marketplace billing** | Single invoice for Oracle + AWS infrastructure costs; usage counts toward AWS commitments |
| **Oracle Support Rewards** | Database@AWS spend accrues Oracle Support Rewards, same as eligible OCI spend |

---

### Supported Oracle Database Versions

| Version | Tier |
|---|---|
| Oracle Database 19c | Exadata Database Service (VM Cluster) and Autonomous AI Database |
| Oracle AI Database 26ai | Exadata Database Service (VM Cluster) and Autonomous AI Database |

> Note: Oracle 21c is not listed as a supported version for Oracle Database@AWS. Oracle 19c remains the primary long-term support release. Oracle AI Database 26ai is the next generation release.

---

### Networking Architecture

```
AWS Availability Zone
├── OCI Child Site (Exadata hardware hosted by AWS, managed by OCI)
│   ├── Oracle Exadata Infrastructure (X11M)
│   │   ├── Database Servers
│   │   └── Storage Servers
│   └── ODB Network (private CIDR, client subnet + backup subnet)
│       └── Cloud VM Cluster / Autonomous VM Cluster
└── Amazon VPC
    ├── EC2 Application Servers
    └── ODB Peering Connection (odbpcx-...) ← routes privately to ODB Network
```

- ODB Peering supports up to **45 peering connections** per ODB network
- ODB Peering supports **cross-account** via AWS RAM
- VPC route tables must be updated manually after peering creation (`aws ec2 create-route`)
- No ingress/egress charges for data movement between OCI and AWS

---

### Management Responsibilities

| Layer | Exadata Database Service | Autonomous AI Database |
|---|---|---|
| Exadata hardware | OCI provisions and maintains; AWS hosts | OCI provisions and maintains; AWS hosts |
| OS & Grid Infrastructure | Customer patches on own schedule | Oracle manages (automated) |
| Oracle Database software | Customer manages and patches | Oracle manages (automated) |
| Database provisioning | AWS console / CLI / API + OCI APIs | AWS console / CLI / API + OCI APIs |
| Backups | Customer configures (S3 or OCI ARS) | Oracle automates |
| Performance tuning | Customer responsibility | Oracle applies best practices |
| Support escalation | Joint Oracle + AWS support | Joint Oracle + AWS support |

---

### Comparison: Oracle Deployment Options on AWS

| Dimension | Oracle Database@AWS | RDS for Oracle | Self-Managed Oracle on EC2 |
|---|---|---|---|
| **Infrastructure** | Oracle Exadata in AWS DC | AWS-managed RDS instances | Customer-managed EC2 instances |
| **Oracle RAC** | Yes | No | Yes (with manual setup) |
| **Exadata performance** | Yes (Smart Scan, RDMA) | No | No |
| **Data Guard** | Yes | Limited (Multi-AZ standby only) | Yes (full control) |
| **GoldenGate** | Yes | Yes | Yes |
| **Autonomous / self-managing DB** | Yes (Autonomous AI tier) | No | No |
| **OS / DB patching** | Customer (Exadata tier) or Oracle (Autonomous) | AWS manages | Customer manages |
| **Oracle licensing** | BYOL or License Included | BYOL or License Included | BYOL (customer responsibility) |
| **Billing** | Oracle costs + AWS infra; single AWS Marketplace invoice | AWS hourly (includes license or BYOL) | EC2 + storage; Oracle license separate |
| **Max control** | High (Exadata tier) | Low | Full |
| **Operational overhead** | Medium (Exadata) / Low (Autonomous) | Low | High |
| **VPC connectivity** | ODB Peering (private) | Native VPC | Native VPC |
| **Best for** | Exadata migrations, RAC, mission-critical Oracle | Managed Oracle without RAC/Exadata | RAC on standard compute, full DBA control |

---

### Migration Patterns

| Tool | Description | Best For |
|---|---|---|
| **Oracle Data Guard** | Physical standby sync; minimal-downtime switchover | Lift-and-shift Exadata migrations; RPO near-zero |
| **Oracle GoldenGate** | CDC-based logical replication; supports heterogeneous sources | Migrations with transformation, cross-platform, or long parallel-run windows |
| **RMAN** | Backup/restore-based migration | Full database copy; acceptable downtime window |
| **Oracle Zero Downtime Migration (ZDM)** | Orchestration tool wrapping Data Guard/GoldenGate/RMAN | Automated, near-zero-downtime migrations from on-premises or OCI |
| **Oracle Data Pump** | Logical export/import | Schema or subset migrations; smaller databases |
| **Transportable Tablespaces** | Copy tablespaces across databases | Moving large tablespace sets with limited downtime |

---

### CDK / SDK Integration

Oracle Database@AWS is provisioned through the `odb` service namespace in the AWS SDK and CLI. Infrastructure-as-code is supported via:

- **AWS CloudFormation**: provision Exadata infrastructure, VM clusters, and ODB networks declaratively
- **AWS CDK**: use L1 constructs backed by CloudFormation resource types for `odb` resources
- **Terraform (HashiCorp AWS provider)**: supported for Oracle Database@AWS resource management
- **AWS SDK (all languages)**: `odb` service client for programmatic control of Exadata infrastructure and networking
- **OCI APIs / CLI**: required for Oracle-layer operations (database creation, patching, Data Guard configuration) after AWS-layer infrastructure is provisioned

> The division of responsibility is reflected in tooling: AWS tools (console, CLI, CloudFormation, CDK) manage infrastructure — Exadata hardware, ODB networks, peering. OCI tools manage the database layer — DB creation, patching, backups, Data Guard.

---

### When to Use Oracle Database@AWS

- Existing on-premises Oracle Exadata workloads that need AWS proximity without re-platforming
- Applications requiring Oracle RAC for horizontal scale-out or high availability
- Enterprises with Oracle Database Enterprise Edition licenses (BYOL) wanting Exadata performance in AWS
- Regulated industries (government, banking, healthcare) requiring Oracle-supported infrastructure with joint Oracle+AWS SLAs
- Workloads needing low-latency access to S3, Lambda, ECS, or Redshift from an Oracle database without internet traversal
- Oracle shops wanting Autonomous Database capabilities (self-tuning, self-patching) on dedicated Exadata hardware

### When NOT to Use Oracle Database@AWS

- Standard Oracle OLTP with no RAC requirement and no existing Exadata investment → **RDS for Oracle** is simpler and cheaper
- Teams wanting full OS-level control without Oracle-managed infrastructure → **Oracle on EC2**
- Non-Oracle workloads or teams planning to migrate away from Oracle → **Aurora PostgreSQL** or other engines
- Workloads that fit within a single instance and don't require Exadata Smart Scan or RoCE networking
