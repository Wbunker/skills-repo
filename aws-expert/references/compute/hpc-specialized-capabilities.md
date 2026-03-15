# HPC & Specialized Compute — Capabilities Reference

For CLI commands, see [hpc-specialized-cli.md](hpc-specialized-cli.md).

## AWS ParallelCluster / AWS PCS

**Purpose**: AWS ParallelCluster is an open-source cluster management tool that automates the provisioning of HPC clusters on AWS; AWS Parallel Computing Service (PCS) is a fully managed successor that provides Slurm-as-a-service with AWS-managed control plane, compute node groups, and shared storage integrations for tightly coupled MPI and HPC workloads.

### Core Concepts

| Concept | Description |
|---|---|
| **Cluster** | A ParallelCluster or PCS deployment consisting of a head node, one or more compute node groups, and shared storage |
| **Head node** | The login/submission node where users connect and submit jobs; runs the Slurm controller (slurmctld) |
| **Compute node group** | A pool of EC2 instances (an Auto Scaling group) that Slurm dynamically provisions and terminates based on job demand |
| **Queue (partition)** | Slurm partition that maps to one or more compute node groups; jobs are submitted to queues |
| **Slurm** | Industry-standard open-source workload manager and scheduler used by ParallelCluster and PCS to schedule HPC jobs |
| **MPI** | Message Passing Interface; programming model for distributed memory parallelism; requires low-latency inter-node networking (EFA) |
| **EFA** | Elastic Fabric Adapter; high-bandwidth, low-latency OS-bypass network interface for tightly coupled HPC and ML workloads |
| **Shared storage** | NFS/EFS for home directories and software; FSx for Lustre for high-throughput parallel I/O scratch storage |
| **Pre/post install scripts** | Bootstrap scripts (S3 URLs) that run on head or compute nodes during cluster creation or node launch to install software |
| **Cluster config** | YAML file (ParallelCluster) or API resources (PCS) defining instance types, queues, storage, networking, and scheduler settings |
| **PCS cluster** | Managed PCS resource with AWS-owned Slurm control plane; decouples scheduler management from customer infrastructure |
| **PCS compute node group** | Managed fleet of EC2 instances registered to a PCS cluster; supports launch templates and instance group configs |

### Key Features

| Feature | Description |
|---|---|
| **Multi-queue support** | Multiple Slurm partitions with different instance types (e.g., CPU queue, GPU queue, memory-optimized queue) |
| **Dynamic scaling** | Nodes provisioned on job submission and terminated after idle time; `ScaledownIdletime` controls termination delay |
| **Graviton / GPU instances** | Supports hpc7g (Graviton HPC), p4d/p5 (GPU), hpc6id (Intel HPC) instance families optimized for HPC |
| **FSx for Lustre integration** | High-throughput parallel scratch filesystem; auto-import/export with S3; PERSISTENT or SCRATCH deployment types |
| **EFS integration** | Managed NFS for shared home directories and software stacks; lower throughput but fully managed |
| **Custom AMI support** | Use pre-built AMIs with HPC software stacks (Intel MPI, Open MPI, CUDA, NCCL) installed |
| **AWS PCS managed control plane** | PCS manages Slurm daemons, upgrades, and HA; customers manage only compute node groups and job submission |
| **Placement groups** | Cluster placement groups for compute node groups requiring tightest network latency and highest EFA bandwidth |

### Key Patterns

| Pattern | Description |
|---|---|
| **Burst-to-cloud HPC** | Submit jobs to elastic cloud compute while keeping on-premises head node or data lake on S3 |
| **Multi-queue HPC cluster** | CPU partition for serial/parallel jobs + GPU partition for ML training or visualization + high-memory partition for large datasets |
| **FSx for Lustre as scratch** | Linked to S3 bucket; input data auto-imported, output auto-exported; high IOPS for checkpoint and I/O-bound simulations |
| **MPI job with EFA** | Place all nodes in cluster placement group with EFA-enabled instance types (hpc7g, p4d, c5n); submit with `srun --mpi=pmix` |
| **Pre-install script pattern** | Store bootstrap scripts in S3; reference in cluster YAML `CustomActions`; install compilers, MPI libraries, domain software |

---

## AWS SimSpace Weaver

**Purpose**: Fully managed service for running large-scale, stateful spatial simulations across a fleet of compute workers; designed for city-scale agent-based simulations such as traffic, crowd dynamics, emergency response, and game-world simulations where a single server cannot hold the entire simulation state.

### Core Concepts

| Concept | Description |
|---|---|
| **Simulation** | A running instance of a SimSpace Weaver app; AWS manages the underlying compute fleet |
| **App** | The simulation application package (ZIP) containing spatial, custom, and service app code deployed to SimSpace Weaver |
| **Spatial app** | App type that partitions a 2D space into domains; each domain runs on one or more workers; handles agent handoff at domain boundaries |
| **Custom app** | Non-spatial app type for global logic, analytics, or orchestration that runs alongside spatial apps |
| **Service app** | App that exposes a REST endpoint within the simulation for external integration or client streaming |
| **Domain** | A subdivision of the simulation space assigned to a worker; SimSpace Weaver manages domain boundaries and agent migration |
| **Worker** | EC2-backed compute unit that runs a domain or app instance; managed by SimSpace Weaver; scales with simulation size |
| **Clock** | Simulation time mechanism; SimSpace Weaver synchronizes all workers to a common logical clock tick |
| **Snapshot** | Saved simulation state that can be used to restart or replay a simulation from a specific point in time |
| **Streaming** | Mechanism for clients (web, Unity, Unreal) to receive real-time simulation state via the service app REST API |

### Key Features

| Feature | Description |
|---|---|
| **Multi-server spatial partitioning** | Divides simulation space across multiple EC2 instances; agents move between domains transparently |
| **Managed compute fleet** | AWS provisions, scales, and manages the worker fleet; no EC2 management required |
| **REST API for simulation control** | Start, stop, describe simulations and apps; query entity state; push events via REST or SDK |
| **Snapshot and replay** | Save simulation state to S3 snapshots; restart from snapshot for reproducibility or disaster recovery |
| **Client streaming integration** | Service apps expose HTTP endpoints; Unity/Unreal/web clients poll or stream simulation state in real time |
| **ServiceQuotas** | Configurable quotas for maximum workers per simulation, simulation duration, and concurrent simulations per account |
| **IAM integration** | Fine-grained IAM policies control who can start/stop simulations and access simulation data |

### Key Patterns

| Pattern | Description |
|---|---|
| **City-scale traffic simulation** | Thousands of vehicles across a city partitioned into spatial domains; each domain simulates a neighborhood; agents handed off at boundaries |
| **Emergency response simulation** | Model evacuation routes, resource allocation, and crowd flows for city-scale emergency planning scenarios |
| **Game world simulation** | Massively multiplayer game environment exceeding single-server capacity; persistent world simulation with real-time client updates |
| **Digital twin** | Pair SimSpace Weaver with IoT data ingestion (Kinesis, IoT Core) to run a continuously updated simulation mirroring a physical environment |
| **Batch scenario analysis** | Run multiple concurrent simulations with different parameters; compare outcomes for urban planning or logistics optimization |

---

## AWS Elastic VMware Service (EVS)

**Purpose**: Fully managed service that runs VMware vSphere (vCenter, vSAN, NSX-T) on AWS dedicated bare-metal EC2 instances, enabling customers to run existing VMware workloads on AWS infrastructure without re-architecting VMs, while integrating with native AWS services.

### Core Concepts

| Concept | Description |
|---|---|
| **EVS environment** | A deployment of vSphere on AWS dedicated bare-metal instances; contains a vCenter Server, vSAN datastore, and NSX-T networking |
| **vSphere cluster** | Group of dedicated bare-metal EC2 hosts managed by vCenter as a single compute resource pool |
| **vCenter Server** | VMware management plane deployed inside the EVS environment; manages VMs, hosts, clusters, and policies |
| **vSAN** | VMware vSAN hyper-converged storage using local NVMe SSDs on bare-metal hosts; provides shared datastore across cluster hosts |
| **NSX-T** | VMware software-defined networking and security fabric; provides micro-segmentation, distributed firewall, and overlay networking |
| **Dedicated bare metal** | AWS i4i or similar high-storage bare-metal instances allocated exclusively to one customer for EVS; provides hardware-level isolation |
| **SDDC** | Software-Defined Data Center; the full vSphere stack (compute + storage + networking) running inside AWS |
| **Stretched cluster** | Optional configuration spanning two AWS Availability Zones for vSAN cross-AZ redundancy and VM failover |
| **Direct Connect integration** | EVS environments connect to on-premises data centers via AWS Direct Connect for hybrid cloud or migration scenarios |
| **HCX** | VMware HCX (optional); live migration of VMs from on-premises vSphere to EVS without downtime; handles network extension |

### Key Features

| Feature | Description |
|---|---|
| **No VM re-architecture required** | Existing VMware VMs run unchanged; same vSphere tools, APIs, and management workflows |
| **Native AWS service integration** | EVS VMs can access S3, RDS, ELB, and other AWS services via VPC peering or PrivateLink |
| **vSAN hyper-converged storage** | Local NVMe storage pooled across hosts via vSAN; no separate SAN required; vSAN policies control redundancy |
| **NSX-T micro-segmentation** | Distributed firewall rules at VM NIC level; east-west security without hairpinning through a perimeter firewall |
| **Dedicated hardware** | Bare-metal hosts not shared with other customers; meets strict compliance and performance isolation requirements |
| **Licensing** | VMware licenses (vSphere, vSAN, NSX-T) are included in the EVS pricing; no separate VMware license procurement needed |
| **Direct Connect hybrid** | Connect EVS to on-premises VMware via Direct Connect + HCX for workload migration, burst, or hybrid operation |
| **Snapshot and backup** | Use VMware-native tools (vSphere snapshots, VADP-compatible backup) or AWS Backup for VM protection |

### Key Patterns

| Pattern | Description |
|---|---|
| **Lift-and-shift VMware migration** | Migrate on-premises vSphere VMs to EVS via HCX live migration; no application changes; retain VMware tooling |
| **Data center exit** | Decommission on-premises VMware infrastructure; run workloads in EVS long-term or as a step toward re-architecting to native AWS |
| **Disaster recovery target** | Use EVS as a DR site for on-premises VMware; replicate VMs via vSphere Replication or HCX; fail over without bare-metal investment |
| **Regulatory / compliance workloads** | Run workloads requiring VMware certification, dedicated hardware isolation, or specific VMware ecosystem software on AWS |
| **Hybrid VMware operations** | Maintain consistent vSphere management plane across on-premises and AWS; use single vCenter to manage both environments |
