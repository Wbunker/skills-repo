# VM Scale Sets & Specialized Compute — Capabilities Reference

For CLI commands, see [vmss-specialized-cli.md](vmss-specialized-cli.md).

## VM Scale Sets (VMSS)

**Purpose**: Automatically manage and scale a group of identical VMs. VMSS supports both manual and automatic scaling, rolling upgrades, and integration with Azure Load Balancer and Application Gateway.

---

### Orchestration Modes

| Mode | Description | Use Case |
|---|---|---|
| **Uniform** | All VMs are identical; managed as a fleet; supports large-scale (up to 1000 instances) | Stateless workloads, web tier, batch worker pools |
| **Flexible** | Mix of VM types; more control over individual instances; supports up to 1000 instances | Stateful workloads, zonal spreading, mixing instance types |

**Recommendation**: Flexible orchestration for new deployments — supports zonal spreading and individual VM operations natively.

---

### Scaling Policies

| Policy Type | Description |
|---|---|
| **Manual scaling** | Set instance count directly via portal, CLI, or ARM |
| **Metric-based autoscale** | Scale on CPU %, memory %, queue depth, custom metrics via Azure Monitor |
| **Schedule-based autoscale** | Pre-scale for known traffic patterns (business hours, weekends) |
| **Predictive autoscale** | ML-based proactive scaling before load arrives (requires metric history) |

### Scale-In Policy

Controls which instances are removed when scaling in:

| Policy | Behavior |
|---|---|
| `Default` | Balance across AZs then fault domains; prefer newest instances |
| `NewestVM` | Remove newest instance first; prefer older stable instances |
| `OldestVM` | Remove oldest instance first; minimize disruption to long-running instances |

---

### Upgrade Policies

| Policy | Behavior |
|---|---|
| **Manual** | Instances not upgraded automatically; you explicitly upgrade instances |
| **Automatic** | Azure upgrades instances as soon as update is available; may cause brief disruption |
| **Rolling** | Upgrade instances in batches; configurable batch size and pause time; preferred for production |

#### Rolling Upgrade Configuration

- `maxBatchInstancePercent`: Max percentage of instances upgraded simultaneously (default 20%)
- `maxUnhealthyInstancePercent`: Max % of instances that can be unhealthy during upgrade
- `maxUnhealthyUpgradedInstancePercent`: Max % of upgraded instances that can be unhealthy
- `pauseTimeBetweenBatches`: Wait time between upgrade batches (e.g., `PT5M`)
- Health probe required for safe rolling upgrades (Application Gateway or load balancer health probe)

---

### Overprovisioning

VMSS can provision extra VMs and delete them after the target count is reached:

- Reduces provisioning time by avoiding retries when VMs fail to start
- Extra VMs are not billed (they're terminated before billing starts)
- Default: enabled (5% extra); set `overprovision: false` for Spot or strictly-sized deployments

---

### Instance Protection

Available in Flexible orchestration:

- **Protect from scale-in**: Instance won't be removed during scale-in operations
- **Protect from scale-set actions**: Instance won't be affected by rolling upgrades or scale-set-wide operations
- Use case: protecting instances running long-running stateful tasks

---

### Terminate Notification

- VMSS sends a metadata notification before terminating an instance during scale-in
- Default 5-minute window; configurable up to 15 minutes
- Instance polls IMDS for termination event; application can drain connections gracefully

---

### Spot VMs in VMSS

- **Eviction policy**: `Deallocate` (keep instance, deallocated state) or `Delete` (remove instance)
- **Max price**: Bid price in $/hour; `-1` means no limit (Azure Spot market price)
- Spot VMSS cannot combine with standard (dedicated) instances in Uniform mode; use mixed instance policies
- **Spot priority**: Use Azure Spot Restore policy to automatically replace evicted instances when capacity is available

---

### Scaling Limits

| SKU | Max Instances | Availability |
|---|---|---|
| Standard VMSS | 1,000 per scale set | All regions |
| Flexible orchestration | 1,000 per scale set | All regions |
| Large-scale VMSS (regional) | 1,000 per region per subscription (default quota) | Request increase |

---

## Azure Spring Apps

**Purpose**: Fully managed Spring Boot and Spring Cloud platform. Developers deploy Spring applications; Azure manages infrastructure, service discovery, config server, and circuit breakers.

### Tiers

| Tier | Features | Use Case |
|---|---|---|
| **Basic** | Spring Boot apps; low cost | Dev/test |
| **Standard** | Auto-scaling, custom domains, VNet, monitoring | General production |
| **Enterprise** | VMware Tanzu components (API Gateway, Config Server, Service Registry, Spring Cloud Gateway) | Enterprise Spring workloads |

### Key Components

| Component | Description |
|---|---|
| **Spring Cloud Config Server** | Centralized external configuration (Git-backed) |
| **Spring Cloud Service Registry (Eureka)** | Managed service discovery |
| **Spring Cloud Circuit Breaker (Resilience4j)** | Circuit breaker pattern |
| **Spring Cloud Gateway** | API gateway with routing, rate limiting (Enterprise tier) |
| **Application Performance Monitoring** | New Relic, Dynatrace, AppDynamics integrations (Enterprise) |
| **Tanzu Service Mesh** | Istio-based service mesh (Enterprise) |

### Deployment Model

- Deployers push a JAR, WAR, or source code; platform builds and runs it
- Blue-green deployments via active/inactive deployment slots
- Auto-scale based on CPU, memory, or custom metrics
- Built-in managed identity for Key Vault and Storage access

---

## Azure CycleCloud (HPC Clusters)

**Purpose**: Orchestrate and manage HPC cluster workloads (Slurm, PBS Professional, Grid Engine, LSF, HPC Pack) on Azure VMs. CycleCloud handles node provisioning, auto-scaling, and job scheduler integration.

### Architecture

- **CycleCloud Server**: Management VM running the CycleCloud web UI and API
- **Cluster templates**: Define HPC cluster topology (scheduler, compute nodes, storage)
- **Auto-scaling**: CycleCloud monitors job queue depth and scales compute nodes automatically
- **Burst to cloud**: Extend on-premises HPC clusters with Azure burst nodes
- **Storage integration**: ADLS Gen2, Azure Files, Azure Blob, Lustre (Azure Managed Lustre), BeeGFS

### Supported Schedulers

| Scheduler | Notes |
|---|---|
| **Slurm** | Most common OSS HPC scheduler; native CycleCloud template |
| **PBS Professional** | Altair PBS; commercial option |
| **Grid Engine** | Open-source Grid Engine / Son of Grid Engine |
| **LSF (IBM)** | IBM Spectrum LSF; enterprise |
| **HPC Pack** | Microsoft HPC Pack (Windows HPC) |

### HPC VM Families for CycleCloud

| Series | Feature | Use Case |
|---|---|---|
| **HBv4** | AMD EPYC Genoa, 200 Gb/s HDR InfiniBand | Molecular dynamics, CFD, financial risk |
| **HCv3** | Intel Xeon, 200 Gb/s InfiniBand | General MPI, reservoir simulation |
| **NDv4/ND96asr_v4** | NVIDIA A100 80 GB, InfiniBand | Deep learning training, AI HPC |
| **NVv4** | AMD Radeon MI25 GPU | Remote visualization |
| **Lsv3** | Local NVMe SSDs | High-IOPS scratch storage |

---

## Azure VMware Solution (AVS)

**Purpose**: Run VMware vSphere workloads natively on dedicated Azure bare-metal infrastructure. Enables lift-and-shift of VMware workloads without refactoring.

### Architecture

- Dedicated bare-metal Azure nodes running VMware ESXi, vCenter, vSAN, and NSX-T
- Managed by Microsoft; vSphere/vCenter access for customers
- Native Azure connectivity via ExpressRoute (mandatory for production)
- Network bridging via Azure Route Server for hybrid connectivity

### Key Features

| Feature | Description |
|---|---|
| **vSAN** | Software-defined storage across AVS nodes |
| **NSX-T** | Software-defined networking and micro-segmentation |
| **HCX** | VMware HCX for live migration from on-premises vSphere to AVS |
| **ExpressRoute Global Reach** | Connect on-premises to AVS directly via ExpressRoute |
| **Azure native services** | Access Azure services (Blob, Key Vault, Monitor) from AVS workloads |
| **Scale** | 3–16 nodes per cluster; multiple clusters per private cloud |

---

## Azure Dedicated Hosts

**Purpose**: Physical servers dedicated to a single customer. All VMs on the host are yours. Required for BYOL, regulatory isolation, and hardware compliance.

### Concepts

| Concept | Description |
|---|---|
| **Host Group** | Logical container for dedicated hosts; spans availability zones or fault domains |
| **Dedicated Host** | A physical server within a host group; supports a specific VM size family |
| **Fault domains** | Host groups have 1–3 fault domains; hosts within the group are spread across FDs |
| **Host SKU** | Determines which VM sizes can run on the host (e.g., `DSv5-Type1` hosts Dsv5 VMs) |
| **Auto-placement** | Let Azure automatically assign VMs to hosts in a host group |
| **License type** | Windows Server and SQL Server licenses applied per host for BYOL |

### Billing

- Billed per host (includes all VM capacity); VMs on dedicated hosts have no additional compute charge
- Hosts are billed even when no VMs are running (capacity is reserved)
- Reserved Instances and Savings Plans apply to dedicated hosts

---

## Azure HPC Cache

**Purpose**: NFS caching layer for HPC workloads that need to access large datasets stored in Azure Blob or NFS storage with low-latency random I/O.

### Key Features

- Aggregates multiple storage targets into a single NFS mount point
- Caches frequently accessed data on high-performance SSD within the cache
- Transparent to HPC applications — standard NFS v3 client
- Scale: 3 to 21+ cache nodes; up to 100 Gbps throughput
- Storage targets: Azure Blob (via NFS 3.0 or block blob), NFS servers on-premises or Azure
- Use case: Genomics pipelines, rendering, seismic processing with large reference datasets
