# AWS EC2 — Capabilities Reference

For CLI commands, see [ec2-cli.md](ec2-cli.md).

## Amazon EC2

**Purpose**: Provides on-demand, scalable virtual compute capacity in the cloud; the foundational IaaS building block for most AWS workloads.

### Core Concepts

| Concept | Description |
|---|---|
| **Instance** | A virtual server defined by an instance type (CPU, memory, network, storage) and launched from an AMI |
| **AMI** | Amazon Machine Image; preconfigured template containing OS, software, and configuration |
| **Instance type** | Hardware specification (family, generation, size); determines vCPUs, memory, network, and storage |
| **Key pair** | SSH credential pair; AWS stores the public key, you keep the private key |
| **Security group** | Stateful virtual firewall at the instance/ENI level; controls inbound and outbound traffic by protocol/port/IP |
| **Elastic Network Interface (ENI)** | Virtual network card; each instance has a primary ENI; additional ENIs can be attached |
| **Elastic IP (EIP)** | Static public IPv4 address that can be re-mapped to instances or ENIs |
| **User data** | Bootstrap script or cloud-init config run once at first launch |
| **Instance metadata** | EC2 metadata service (IMDS) at `169.254.169.254`; exposes instance identity, IAM credentials, user data |
| **Nitro System** | AWS hypervisor platform for current-generation instances; provides near bare-metal performance |

### Storage Options

| Type | Persistence | Use case |
|---|---|---|
| **Amazon EBS** | Persistent; survives stop/terminate | OS volumes, databases, any stateful data |
| **Instance Store** | Ephemeral; lost on stop/hibernate/terminate | Temporary scratch space, buffer/cache, replicated data |
| **Amazon EFS / FSx** | Shared file system; mounted at OS level | Shared data across instances, NFS workloads |
| **Amazon S3** | Object storage; accessed via SDK/CLI | Artifacts, backups, large unstructured data |

### Key Features

- **EC2 Instance Connect**: Browser or CLI SSH access without managing SSH keys
- **EC2 Serial Console**: Out-of-band console access for troubleshooting unresponsive instances
- **Hibernation**: Save RAM to EBS, resume quickly (supported instance families with encrypted EBS root)
- **Dedicated Hosts**: Physical server dedicated to your use; supports BYOL; billed per host
- **Dedicated Instances**: Instances on single-tenant hardware; no host-level visibility; billed per instance
- **Capacity Reservations**: Reserve capacity in a specific AZ with no term commitment
- **IMDS v2**: Require session-oriented token to access metadata (defense against SSRF)

---

## EC2 Instance Families

**Purpose**: Instance families group instances by workload type; each generation within a family improves price-performance.

### Instance Naming Convention

`[family][generation][processor][attributes].[size]`

Example: `m7g.2xlarge` = M family, 7th gen, Graviton processor, 2x large size.

Processor suffixes: `a` = AMD EPYC, `g` = Graviton (ARM), `i` = Intel, no suffix = Intel (current gen)

Attribute suffixes: `d` = local NVMe SSD, `n` = enhanced network, `b` = EBS-optimized network, `z` = high frequency

### Instance Families by Category

| Family | Category | Optimized For | Common Use Cases |
|---|---|---|---|
| **M** (m5–m8) | General Purpose | Balanced CPU/memory/network | Web servers, app servers, small databases, dev/test |
| **T** (t3, t4g) | General Purpose (burstable) | Baseline + burst CPU | Low-traffic web apps, microservices, CI runners |
| **C** (c5–c8) | Compute Optimized | High-performance processors | HPC, batch processing, gaming, video encoding, ML inference |
| **R** (r5–r8) | Memory Optimized | High memory-to-vCPU ratio | In-memory databases (Redis, Memcached), SAP HANA, real-time analytics |
| **X** (x2, x8) | Memory Optimized (extreme) | Terabytes of RAM | SAP HANA, in-memory big data, large-scale databases |
| **U** (u-3tb1 to u-24tb1) | Memory Optimized (bare metal) | Up to 24 TiB RAM | Largest in-memory databases |
| **z1d** | Memory Optimized (high freq) | Fast cores + NVMe | Financial risk modeling, high-frequency trading |
| **D** (d3, d3en) | Storage Optimized | Dense HDD storage | Distributed file systems, data warehouses, Hadoop |
| **I** (i3–i8, Im4gn, Is4gen) | Storage Optimized | High-speed NVMe SSDs | NoSQL databases (Cassandra, MongoDB), OLTP, cache |
| **H** (h1) | Storage Optimized | HDD throughput | MapReduce, distributed file systems |
| **G** (g4–g7) | Accelerated Computing | NVIDIA GPUs | ML training/inference, video transcoding, 3D graphics |
| **P** (p4, p5, p6) | Accelerated Computing | NVIDIA high-end GPUs | Deep learning training, HPC, scientific simulation |
| **Inf** (inf1, inf2) | Accelerated Computing | AWS Inferentia chips | ML inference at scale, NLP, computer vision |
| **Trn** (trn1, trn2) | Accelerated Computing | AWS Trainium chips | Deep learning model training (PyTorch, TensorFlow) |
| **DL** (dl1, dl2q) | Accelerated Computing | Habana Gaudi GPUs | Deep learning training |
| **F** (f2) | Accelerated Computing | FPGAs | Custom hardware acceleration, genomics, financial analytics |
| **VT** (vt1) | Accelerated Computing | Xilinx video transcoding | Real-time video streaming transcoding |
| **Hpc** (hpc6a, hpc7a, hpc8a) | HPC | EFA networking, high-core | Tightly coupled HPC, CFD, molecular dynamics |

### T-Series Burstable Instances

T instances earn CPU credits during idle periods and spend them during bursts. Key behavior:
- **Standard mode**: Cannot burst above baseline if credits exhausted (default for t3)
- **Unlimited mode**: Can burst indefinitely; charged for surplus credits if sustained; default for t3a and t4g
- 1 CPU credit = 1 vCPU running at 100% for 1 minute

---

## AMIs and Launch Templates

**Purpose**: AMIs are the source images for instances; Launch Templates capture full instance configuration for repeatable, version-controlled launches.

### AMI Concepts

| Concept | Description |
|---|---|
| **AMI** | Regional resource containing a root volume snapshot, permissions, and block device mappings |
| **Public AMI** | Available to all AWS accounts; includes AWS-provided Amazon Linux, Ubuntu, Windows AMIs |
| **Private AMI** | Default; only available to the owning account |
| **Shared AMI** | Shared with specific accounts or made public by the owner |
| **Community AMI** | User-contributed AMIs available publicly |
| **AWS Marketplace AMI** | Commercial AMIs with software licensing via AWS Marketplace |
| **Snapshot backing** | Most AMIs are EBS-backed (root volume is a snapshot); instance store-backed AMIs are legacy |
| **EC2 Image Builder** | Pipeline service for automating AMI creation, testing, and distribution |

### Launch Templates vs. Launch Configurations

| | Launch Template | Launch Configuration |
|---|---|---|
| Versioning | Yes; multiple named versions | No; must create new |
| Spot + On-Demand | Yes (mixed instances policy) | No |
| T2/T3 unlimited mode | Yes | No |
| Instance metadata options (IMDSv2) | Yes | No |
| Recommended | Yes | Legacy only |

### Key Launch Template Parameters

- Instance type, AMI ID, key pair, security groups, subnet/network interfaces
- IAM instance profile, user data, tags, placement group
- EBS volume specifications (type, size, encryption, delete-on-termination)
- Spot options (max price, interruption behavior)
- Metadata options (IMDS version, hop limit, endpoint state)

---

## EC2 Placement Groups

**Purpose**: Control how instances are placed on underlying hardware to optimize for performance or availability.

### Placement Group Types

| Type | Strategy | Use Case | Constraints |
|---|---|---|---|
| **Cluster** | Pack instances close together in a single AZ | Low-latency, high-throughput HPC; tightly coupled node-to-node communication | Single AZ only; limited instance types; best launched all at once |
| **Partition** | Divide into logical partitions across separate hardware racks | Large distributed systems (Hadoop, Cassandra, Kafka); partition-aware replication | Up to 7 partitions per AZ; instances can query which partition they are in |
| **Spread** | Place each instance on distinct underlying hardware | Small groups of critical instances requiring maximum isolation | Max 7 running instances per AZ per group |

### Rules

- An instance can belong to only one placement group at a time
- Placement groups cannot be merged
- Dedicated Hosts cannot be launched in placement groups
- No charge to create or use placement groups

---

## EC2 Purchasing Options

**Purpose**: Choose the right pricing model to balance cost, flexibility, and capacity commitments.

### Purchasing Model Comparison

| Model | Commitment | Discount vs On-Demand | Best For |
|---|---|---|---|
| **On-Demand** | None | — | Unpredictable workloads, short-term, dev/test |
| **Reserved Instances (Standard)** | 1 or 3 years, specific instance config | Up to ~72% | Steady-state production workloads with known type/region |
| **Reserved Instances (Convertible)** | 1 or 3 years, can exchange | Up to ~66% | Steady-state but may need to change instance type |
| **Savings Plans (Compute)** | 1 or 3 years, $/hour commit | Up to ~66% | Flexible; applies to EC2 (any region/family/OS), Lambda, Fargate |
| **Savings Plans (EC2 Instance)** | 1 or 3 years, specific instance family + region | Up to ~72% | Highest discount; less flexible than Compute Savings Plans |
| **Spot Instances** | None | Up to ~90% | Fault-tolerant, flexible timing, interruptible workloads |
| **Dedicated Hosts** | On-Demand or Savings Plan | — | BYOL compliance, regulatory isolation |
| **Capacity Reservations** | None (pay regardless of use) | — | Guarantee capacity in AZ for critical launches |

### Spot Instance Key Behaviors

- Spot price varies continuously based on supply and demand; set by AWS
- AWS provides a **2-minute interruption notice** before reclaiming the instance
- Interruption actions: terminate (default), stop, or hibernate (EBS-backed instances)
- **Spot Fleet**: Launch and maintain a target capacity across multiple instance types and AZs
- **EC2 Fleet**: Launch a combination of Spot and On-Demand instances across types/AZs
- **Rebalance recommendation**: Early signal of elevated interruption risk before the 2-minute notice
- Spot Instances are **not covered by Savings Plans** or Reserved Instance pricing
- **Allocation strategies**: `lowest-price`, `diversified`, `capacity-optimized`, `price-capacity-optimized` (recommended)

### Reserved Instance Concepts

- **Zonal RI**: Reserves capacity in a specific AZ and applies to that instance type
- **Regional RI**: Applies the discount across any AZ in the region (no capacity reservation)
- **RI Marketplace**: Sell unused Standard RIs to other AWS customers
- RI does not automatically apply — it discounts the bill for matching On-Demand usage
