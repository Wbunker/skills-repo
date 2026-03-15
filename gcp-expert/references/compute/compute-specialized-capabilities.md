# Compute Specialized — Capabilities Reference

CLI reference: [compute-specialized-cli.md](compute-specialized-cli.md)

This document covers specialized compute offerings: TPUs, GPU instances, Bare Metal Solution, Google Cloud VMware Engine (GCVE), Sole-Tenant Nodes, and HPC on GCP.

---

## TPUs (Tensor Processing Units)

### Overview
Custom ASICs designed by Google specifically for neural network inference and training workloads. TPUs deliver higher throughput and better performance-per-dollar than GPUs for compatible ML models, particularly large transformer architectures (BERT, T5, PaLM, Gemini).

### TPU Generations

| Generation | Best For | Form Factor | Key Specs |
|---|---|---|---|
| TPU v4 | Large-scale training (100B+ param models) | Pod slices (8-4096 chips) | 275 TFLOPS BF16 per chip; 32 GB HBM per chip |
| TPU v5e | Cost-optimized training & inference | Pod slices (1-256 chips) | Efficient price/performance for medium models |
| TPU v5p | Maximum training performance | Pod slices (1-8960 chips) | Highest aggregate bandwidth; largest configurations |
| TPU v6e (Trillium) | Next-gen efficiency | Pod slices | ~4x throughput vs v5e; improved MXU |

### TPU VM vs TPU Node
- **TPU VM** (recommended): you SSH directly into a host VM that is co-located with the TPU. Lower latency, direct access to TPU from user code.
- **TPU Node** (legacy): TPU runs as a remote service accessible over gRPC. Higher latency; deprecated approach.

### TPU Pod Slices
Large-scale training uses "pod slices" — a contiguous subslice of the TPU pod interconnected with high-bandwidth ICI (Inter-Chip Interconnect). Specify slice size with topology (e.g., `v4-32` = 32 chips, `v4-1024` = 1024 chips). Chips within a slice communicate at ~340 TB/s aggregate bandwidth.

### Frameworks
- **JAX** (primary): designed for TPU; supports pmap/jit for parallelism. Used for Google's internal models.
- **PyTorch/XLA**: PyTorch models compiled to XLA for TPU execution.
- **TensorFlow**: native TPU support via `tf.distribute.TPUStrategy`.

### TPU Access
- Cloud TPU API or `gcloud compute tpus`
- TPU VMs available in specific zones (us-central1, us-east1, europe-west4 for v4/v5)
- Quotas required; request via Cloud Console or quota increase request

---

## GPUs on Compute Engine

### Available GPU Types

| GPU | vRAM | Use Case | Available Machine Types |
|---|---|---|---|
| NVIDIA T4 | 16 GB | Inference, light training, ML serving | n1-standard-*, g4dn-equivalent |
| NVIDIA V100 | 16 / 32 GB | Training, HPC, molecular simulation | n1-standard-* with accelerator |
| NVIDIA A100 (40 GB) | 40 GB | Large-scale training, HPC | a2-highgpu-1g through a2-megagpu-16g |
| NVIDIA A100 (80 GB) | 80 GB | Very large model training | a2-ultragpu-1g through a2-ultragpu-4g |
| NVIDIA H100 (80 GB) | 80 GB | Generative AI, largest models | a3-highgpu-8g (8 H100s per VM) |
| NVIDIA L4 | 24 GB | Inference, multimedia, light training | g2-standard-* series |

### Multi-GPU Configurations
- A2 machines: up to 16 x A100 40 GB per VM (a2-megagpu-16g) with NVLink for GPU-to-GPU memory sharing
- A3 machines: up to 8 x H100 80 GB per VM (a3-highgpu-8g) with NVLink4
- Multiple VMs can be linked via GPUDirect RDMA (A3) or custom InfiniBand-equivalent interconnect for distributed training

### CUDA and Driver Support
GCE GPU instances support NVIDIA CUDA. Options for CUDA setup:
1. **Deep Learning VM images** (recommended): pre-configured images from `deeplearning-platform-release` project with CUDA, cuDNN, PyTorch/TensorFlow pre-installed
2. **Container-Optimized OS**: install NVIDIA drivers via DaemonSet (for GKE)
3. **Manual installation**: install CUDA toolkit on standard Debian/Ubuntu image

### GPU Reservations
For production ML workloads, create reservations to guarantee GPU capacity. Reservations guarantee availability in a zone; you're billed whether or not instances are running.

---

## Bare Metal Solution

### Overview
Dedicated physical servers deployed in Google-managed data centers, co-located with GCP regions. Connected to GCP via low-latency, high-bandwidth partner interconnect. Use for workloads that require physical hardware with no virtualization layer.

### Key Characteristics
- Physical servers: no hypervisor, direct hardware access
- Connected to GCP via VLAN Attachments over Partner Interconnect (sub-1ms latency to GCP region)
- Google manages power, cooling, hardware maintenance
- Customer manages OS, software stack, and patching
- SSD/HDD options; 10 Gbps to 25 Gbps NIC options

### Use Cases
| Workload | Why Bare Metal |
|---|---|
| SAP HANA | Certified configurations; requires physical NUMA architecture; certification voids if run on VMs |
| Oracle RAC (Real Application Clusters) | Oracle RAC licensing and support requires certified hardware; RAC not supported in VMs |
| Oracle Database with Standard Edition 2 | Oracle SE2 licensing is per physical socket |
| High-performance storage area networks | Direct-attached NVMe, no virtual I/O overhead |
| Compliance-driven workloads requiring physical isolation | No shared hypervisor with other customers |

### Networking Integration
- VMs in GCP VPC can communicate with Bare Metal servers directly over the dedicated interconnect
- Shared VPC supported; private IPs routable between GCP and BMS
- Cannot use Cloud Load Balancing or Cloud CDN with BMS directly; use GCE proxy VMs in front

---

## Google Cloud VMware Engine (GCVE)

### Overview
Run VMware vSphere, NSX-T, vSAN, and HCX natively on dedicated Google Cloud infrastructure. GCVE provides a fully managed VMware SDDC (Software-Defined Data Center) running on bare-metal nodes in Google facilities, connected directly to your GCP VPC.

### Architecture
- **Private cloud**: one or more VMware clusters on dedicated bare-metal nodes
- **Nodes**: custom Intel Xeon-based nodes with vSAN flash storage (e.g., `standard-72` = 72 cores, 576 GB RAM, 15.36 TB raw SSD storage)
- **Networking**: NSX-T manages east-west networking within GCVE; connects to GCP VPC via peered VPC/Cloud Interconnect
- **Management**: customers have full vCenter Server and NSX-T admin access

### Key Features
- **VMware HCX**: workload mobility for live VM migration from on-premises VMware to GCVE with no downtime
- **NSX-T**: full microsegmentation, distributed firewall, load balancing within GCVE
- **vSAN**: hyperconverged storage; Google manages storage hardware and replacements
- **vCenter**: standard vCenter UI and APIs; familiar to VMware administrators
- **Cloud Interconnect / VPN**: connect GCVE private cloud to on-premises VMware or other data centers
- **Direct VPC peering**: GCE VMs in VPC can access GCVE VMs directly via RFC 1918 routing

### Use Cases
- Lift-and-shift of on-premises VMware workloads to GCP with zero application changes
- Data center exit: retire physical VMware infrastructure without re-platforming
- Disaster recovery: use GCVE as DR target for on-premises VMware (VMware Site Recovery Manager)
- Hybrid: keep some workloads on GCVE while using GCP-native services (Cloud SQL, BigQuery, etc.)

### Minimum Configuration
- Minimum 3 nodes per cluster (vSAN requires 3 for fault tolerance)
- Minimum 3 nodes in a private cloud

---

## Sole-Tenant Nodes

### Overview
Physical Compute Engine servers dedicated to a single Google Cloud customer. Unlike regular GCE instances that share physical hosts with other customers, sole-tenant nodes ensure physical isolation.

### Use Cases
| Reason | Description |
|---|---|
| BYOL (Bring Your Own License) | Windows Server and SQL Server licenses tied to physical cores/sockets. Sole-tenant ensures consistent physical core count per BYOL commitment. |
| Regulatory compliance | Some regulations (FedRAMP, HIPAA extensions, SOC 2) require customer-exclusive physical hosts. |
| Performance isolation | Eliminate noisy neighbor effects on shared hosts. |
| Affinity rules | Pin specific VMs to specific physical hosts for latency reasons. |

### Sole-Tenant Node Configuration
1. **Node template**: defines the node type (e.g., `c2-node-60-240` = 60 vCPUs, 240 GB RAM) and affinity labels.
2. **Node group**: a group of sole-tenant nodes created from a node template. Supports autoscaling.
3. **Instance on sole-tenant node**: create a GCE instance with `--node-group` or node affinity labels.

### Node Types
- `n2-node-80-640`: N2 nodes (Intel), 80 vCPUs, 640 GB RAM
- `c2-node-60-240`: Compute-optimized, 60 vCPUs, 240 GB
- `m3-node-128-1952`: Memory-optimized, 128 vCPUs, 1952 GB RAM
- Custom node types available by contacting Google Cloud

### Restart Behavior on Sole-Tenant Nodes
Configure `--restart-type=restart-node-on-any-server` or `restart-node-on-minimal-servers` to control whether a preempted/restarted instance can move to a different physical host (within the node group) or must stay on the same host.

---

## HPC on GCP

### Overview
Google Cloud supports large-scale HPC workloads using specialized hardware (C3, C2, N2 for compute), high-bandwidth networking, and Google-managed scheduler integration.

### Key HPC Components

**Compute-Optimized Instances for HPC:**
- `c3-standard-176`: 176 vCPUs, Intel Sapphire Rapids, highest single-socket frequency
- `c2-standard-60`: 60 vCPUs, Intel Cascade Lake, historically common for MPI workloads
- `c3d-standard-360`: 360 vCPUs, AMD EPYC Genoa (highest vCPU count per VM)

**Networking:**
- **Compact Placement Policy**: requests physical co-location of VMs on the same host cluster, minimizing inter-node latency (< 1μs between co-located VMs)
- **GPUDirect RDMA** (A3 + H100): direct GPU-to-GPU communication across nodes without CPU involvement; ~400 Gbps cross-node bandwidth
- **Tier 1 networking**: up to 200 Gbps VM network bandwidth on C3 and A3 instances

**Google Cloud HPC Toolkit:**
- Open-source Terraform + Ansible framework for deploying HPC environments on GCP
- Pre-built blueprints for Slurm, PBS, OpenMPI, GROMACS, WRF, OpenFOAM
- GitHub: `github.com/GoogleCloudPlatform/hpc-toolkit`
- Creates Slurm clusters with auto-scaling partitions backed by GCE MIGs

**Slurm on GCP:**
- Slurm workload manager with Cloud Scheduler Slurm Plugin
- Dynamic node provisioning: Slurm automatically allocates GCE VMs when jobs are submitted and terminates them when idle
- Supports heterogeneous partitions: CPU-only, GPU, high-memory partitions in one cluster
- Deployed via HPC Toolkit or manually

**Parallel Filesystem Options:**
- **Lustre on GCP**: deploy Intel Lustre (DDN EXAScaler) via Cloud Marketplace on GCE VMs; high-throughput parallel file access
- **VAST Data/WekaFS**: ISV solutions for high-performance parallel NAS on GCP
- **Filestore High Scale**: Google-managed NFS at petabyte scale; simpler but lower performance than Lustre

**MPI and Network Libraries:**
- **Intel MPI**, **OpenMPI**, **MPICH** all supported
- For maximum performance: use Compact Placement Policy + C3 instances + RDMA-capable NICs
- GPUDirect RDMA enables NCCL (NVIDIA Collective Communications Library) for distributed GPU training

---

## Important Patterns & Constraints

**TPUs:**
- TPU VMs require specific zones and may need capacity reservations for large pod slices
- JAX programs need `jax.devices()` to verify TPU detection at startup
- TPU VMs may not support all PyTorch operators; test compatibility before large training runs

**GPUs:**
- GPU quota must be requested per zone; default quota is 0 GPUs in most projects
- `--maintenance-policy=TERMINATE` is required for GPU instances (no live migration)
- NVIDIA drivers must be installed; Deep Learning VM images simplify this
- For distributed training across multiple GPU VMs, use GKE with GPUDirect RDMA or Vertex AI for managed training

**GCVE:**
- GCVE nodes are billed hourly at a high per-node rate regardless of VM utilization within the cluster
- HCX migration may take significant bandwidth; plan migration windows
- GCVE is not available in all regions; check current availability

**Bare Metal:**
- Procurement lead time: BMS orders may take weeks to fulfill; not instant provisioning
- OS installation is customer responsibility; Google provides out-of-band management access
- No SLA for BMS hardware failures; Google provides hardware replacement SLAs but not uptime SLAs for customer software

**Sole-Tenant Nodes:**
- Node types are zonal; availability may be limited in some zones
- Billing starts when the node is created, regardless of whether instances run on it
- BYOL requires documentation; contact Google account team for BYOL pricing arrangements
