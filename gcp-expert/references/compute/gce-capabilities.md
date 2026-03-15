# Google Compute Engine — Capabilities Reference

CLI reference: [gce-cli.md](gce-cli.md)

## Purpose

Resizable virtual machines running on Google's global infrastructure with flexible machine types, custom VM configurations, and deep integration with GCP services. GCE provides full control over the OS, networking, storage, and hardware configuration, making it suitable for workloads that require specific runtime environments, persistent processes, or cannot be containerized easily.

---

## Core Concepts

| Concept | Description |
|---|---|
| Instance | A virtual machine running on Google's infrastructure. Each instance runs in a specific zone. |
| Machine type | Predefined combination of vCPUs and memory (e.g., `n2-standard-4`). Determines CPU platform and available memory. |
| Custom machine type | User-defined vCPU and memory combination (e.g., `custom-6-20480` = 6 vCPUs, 20 GB RAM). Extended memory available as `n2-custom-4-16384-ext`. |
| Image | Boot disk image containing the OS and optionally pre-installed software. Can be public (GCP-managed) or custom (user-created). |
| Instance template | Immutable resource defining instance configuration (machine type, boot disk, network, metadata). Used for MIGs and consistent instance creation. |
| Managed Instance Group (MIG) | Group of identical VMs created from an instance template. Supports autoscaling, autohealing, rolling updates, and stateful workloads. |
| Boot disk | Primary persistent disk attached to an instance, contains the OS. Default size depends on image; can be resized. |
| Persistent disk | Durable network-attached block storage. Can be attached to one (read-write) or multiple (read-only) instances. Independent lifecycle from instances. |
| Spot VM | Highly discounted (60-91% off) VM that GCP can preempt with 30-second notice when capacity is needed. No minimum runtime guarantee. Replaces Preemptible VMs. |
| Preemptible VM | Legacy version of Spot VM. Maximum 24-hour runtime; Spot VMs are preferred for new workloads. |
| Service account | IAM identity attached to an instance, used to authenticate API calls made from that instance to GCP services. |
| Startup script | Script run at instance boot time via instance metadata (`startup-script` or `startup-script-url`). Used for bootstrapping software. |
| VM metadata | Key-value pairs accessible from within an instance at `http://metadata.google.internal/computeMetadata/v1/`. Includes project-level and instance-level metadata. |
| Instance group | Collection of VM instances. Managed Instance Groups (MIGs) use instance templates; unmanaged instance groups contain heterogeneous instances. |
| Sole-tenant node | Physical Compute Engine server dedicated to a single customer. Required for BYOL licensing compliance, strong isolation requirements, or regulatory workloads. |

---

## Machine Series

| Series | Family | Use Case | Key Characteristics |
|---|---|---|---|
| E2 | Cost-optimized | Dev/test, small web apps, low-traffic workloads | Shared-core options (e2-micro, e2-small, e2-medium); up to 32 vCPUs, 128 GB RAM; uses dynamic resource allocation |
| N2 | Balanced (Intel) | General-purpose production workloads | Up to 128 vCPUs, 864 GB RAM; Intel Cascade Lake/Ice Lake; supports confidential VMs |
| N2D | Balanced (AMD) | General-purpose, cost-sensitive production | Up to 224 vCPUs, 896 GB RAM; AMD EPYC Rome/Milan; typically 10-20% cheaper than N2 |
| N4 | Balanced (Intel 4th gen) | General-purpose, newer Intel generation | Intel Sapphire Rapids; up to 208 vCPUs, 1,040 GB RAM; improved per-core performance |
| C3 | Compute-optimized (Intel) | High-performance web, gaming servers, HPC | Intel Sapphire Rapids; up to 176 vCPUs, 352 GB RAM; high per-core frequency |
| C3D | Compute-optimized (AMD) | HPC, batch, gaming servers | AMD EPYC Genoa; up to 360 vCPUs; Local SSD support |
| M3 | Memory-optimized | SAP HANA, in-memory databases, large in-memory analytics | Up to 128 vCPUs, 3,904 GB RAM; highest memory-to-vCPU ratio in GCP |
| A2 | GPU (NVIDIA A100) | ML training, large-scale inference, HPC | 12-96 vCPUs; 1-16 NVIDIA A100 40GB or 80GB GPUs; NVLink |
| A3 | GPU (NVIDIA H100) | Large-scale ML training, generative AI | NVIDIA H100 80GB GPUs; up to 8 GPUs per instance; high-bandwidth interconnect |
| C2 | Compute-optimized (legacy Intel) | HPC, gaming, high-frequency trading | Intel Cascade Lake; up to 60 vCPUs, 240 GB RAM; highest sustained clock speed |
| C2D | Compute-optimized (legacy AMD) | HPC, batch workloads | AMD EPYC Rome; up to 112 vCPUs, 896 GB RAM |

### Machine Naming Convention

```
n2-standard-4
│   │        └── vCPU count
│   └── family: standard (balanced ratio), highmem (more memory), highcpu (more CPU)
└── series: n2, e2, c3, m3, a2, etc.

Custom:
custom-6-20480          = 6 vCPUs, 20 GB RAM (N1 custom)
n2-custom-8-32768       = 8 vCPUs, 32 GB RAM (N2 custom)
n2-custom-8-32768-ext   = 8 vCPUs, 32 GB RAM with extended memory
```

---

## Disk Options

| Disk Type | Media | IOPS (read/write) | Throughput | Use Case |
|---|---|---|---|---|
| pd-standard | HDD | Up to 3,000 / 3,000 (size-dependent) | 180 MB/s read | Low-cost bulk storage, sequential workloads |
| pd-balanced | SSD | Up to 80,000 / 80,000 (size-dependent) | 1,200 MB/s read | General-purpose; good balance of cost/performance |
| pd-ssd | SSD | Up to 100,000 / 100,000 | 1,200 MB/s read | High-performance databases, latency-sensitive apps |
| pd-extreme | SSD | Up to 350,000 / 350,000 (provisioned) | 7,500 MB/s | Highest performance PD; manually provisioned IOPS/throughput |
| Hyperdisk Balanced | SSD | Up to 160,000 / 160,000 (provisioned) | 2,400 MB/s | Workloads needing independent IOPS/throughput provisioning |
| Hyperdisk Extreme | SSD | Up to 350,000 / 350,000 (provisioned) | 10,000 MB/s | Databases requiring maximum throughput, SAP HANA |
| Hyperdisk Throughput | HDD-equivalent | Lower IOPS | Up to 2,400 MB/s | Large streaming/throughput workloads at lower cost |
| Hyperdisk ML | SSD | Up to 1,200,000 read | Up to 24,000 MB/s | Read-heavy ML model loading; attach to many VMs simultaneously |
| Local SSD | NVMe SSD | ~680,000 read / 360,000 write per disk | ~2,400 MB/s | Ephemeral scratch space; highest single-VM I/O; data lost on stop/terminate |

**Hyperdisk** allows independently provisioning capacity, IOPS, and throughput—decoupling performance from disk size. Requires N2, C3, or newer machine families.

**Local SSD** is physically attached to the hypervisor host. Data persists across reboots but is lost on instance stop or delete. Must be created at instance creation time; 375 GB per disk, up to 24 disks per instance (9 TB).

---

## Key Features

### Live Migration
GCE automatically live-migrates running instances during host maintenance events (hardware updates, software patching). The VM continues running during migration with no user intervention. Not available for Spot VMs or instances with Local SSDs by default.

### Custom Machine Types
Create instances with precise vCPU and memory allocations. Requirements:
- vCPUs: 1 or any even number up to the series maximum
- Memory: 0.9 GB to 6.5 GB per vCPU (standard range); extended memory available up to 24 GB/vCPU
- Extended memory incurs a surcharge

### Nested Virtualization
Run a hypervisor (KVM) inside a GCE VM. Enabled via instance metadata flag `--enable-nested-virtualization`. Requires Intel Haswell or later platform (not available on N1 VMs using Sandy Bridge).

### Shielded VMs
Hardened VMs verifying integrity of the boot process:
- **Secure Boot**: prevents loading unsigned bootloaders/kernels
- **vTPM (Virtual Trusted Platform Module)**: generates attestation keys, protects secrets
- **Integrity Monitoring**: compares current boot with known-good baseline; alerts on changes

### Confidential VMs
Encrypts data in use (memory encryption) using AMD SEV (Secure Encrypted Virtualization). Available on N2D, C2D machine series. Data remains encrypted in RAM even from the hypervisor. Use for sensitive regulated workloads.

### Compact Placement Policy
Requests that instances be physically co-located on the same host cluster (low latency, high bandwidth between instances). Useful for HPC and tightly-coupled distributed computing. Created separately and referenced at instance creation.

### Sole-Tenant Nodes
Dedicated physical hosts. You can run instances exclusively on a node template you define. Supports BYOL (Bring Your Own License) for Windows Server and SQL Server. Instances can be configured to restart on the same physical host after maintenance.

---

## Managed Instance Groups (MIGs)

MIGs create and manage multiple identical instances from a single instance template.

### Types
- **Zonal MIG**: all instances in one zone; simpler, lower latency within group
- **Regional MIG**: instances distributed across up to 3 zones in a region; higher availability

### Autoscaling
Configure policies based on:
- CPU utilization target (e.g., 60%)
- HTTP load balancing utilization
- Cloud Monitoring metrics (custom or predefined)
- Cloud Pub/Sub queue depth
- Schedule-based (proactive scaling)

Minimum and maximum instance counts are always required.

### Autohealing
Attach a health check (HTTP, HTTPS, TCP) to a MIG. If an instance fails health checks for the configured initial delay + consecutive failure threshold, the MIG automatically recreates it.

### Rolling Updates (Updater)
When updating the instance template:
- **Automatic**: GCP performs rolling replacement at the configured speed (max surge, max unavailable)
- **Selective**: manually trigger update on specific instances
- **Canary**: deploy new template to a subset of instances first

### Stateful MIGs
For workloads with per-instance state (e.g., databases, Kafka brokers):
- Preserve specific disk identifiers and IPs across recreation
- Per-instance configs override the group template for specific instances
- Used for Cassandra, Zookeeper, and stateful legacy apps

---

## Pricing

| Model | Description | Discount |
|---|---|---|
| On-demand | Pay per second (minimum 1 minute); no commitment | Baseline |
| Sustained Use Discounts (SUD) | Automatic discounts for running an instance type >25% of the month in a region. 100% usage = ~30% discount on N1/N2; applied per series/region, not per instance. | Up to ~30% |
| Committed Use Discounts (CUD) | 1-year or 3-year commitment for a resource type (vCPU/RAM) in a region. Resource-based (not instance-specific). | 37% (1yr) / 55% (3yr) on N1; similar for others |
| Spot VMs | Heavily discounted capacity that may be preempted. 30-second eviction notice. No SLAs, no live migration. | 60-91% off on-demand |
| Free tier | e2-micro instance: 1 instance per month free (US regions only, excluding N. Virginia) | N/A |

**Note**: SUDs and CUDs are mutually exclusive on the same usage. CUDs are applied first; remaining usage gets SUD. Cannot combine both on the same resource.

---

## When to Use

- Full OS control is required (custom kernel, kernel modules, specific OS distribution)
- Persistent background processes or daemons that must always run
- Stateful workloads that are difficult to containerize
- Existing VM-based applications being lifted and shifted to GCP
- BYOL licensing requirements (Windows Server, SQL Server, RHEL)
- High-performance computing requiring specific hardware (GPUs, TPUs, Local SSDs)
- Database servers (MySQL, PostgreSQL, SQL Server, MongoDB) requiring persistent, high-IOPS storage
- CI/CD build agents needing ephemeral but configurable environments

---

## Important Patterns & Constraints

- **Instance creation time**: typically 20-60 seconds; use MIGs with pre-warmed min instances to avoid cold starts in autoscaling.
- **Disk resize only grows**: persistent disks can be resized larger but not smaller; OS-level filesystem resize is a separate step.
- **Snapshots are not backups**: snapshots are incremental and stored in Cloud Storage but do not protect against accidental deletion unless you use locked retention policies.
- **Default service account**: instances get the default Compute Engine service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`) with Editor role—restrict this in production by assigning a custom service account with least-privilege IAM roles.
- **Quota limits**: each project has per-region quotas for CPUs, GPUs, IP addresses, and disk; check and request quota increases before large deployments.
- **Preemption risk**: Spot VMs can be preempted at any time; design workloads to checkpoint state (Cloud Storage, Persistent Disk) and retry.
- **SSH keys**: prefer OS Login (links SSH keys to Google identities via IAM) over metadata-based SSH keys for centralized access management.
- **Instance metadata server**: accessible only from within the instance at `169.254.169.254`; no authentication required from within the VM—never write secrets to instance metadata.
- **Startup script failures**: if a startup script exits non-zero, the instance still boots; check serial console or Cloud Logging for diagnostics.
- **MIG health check initial delay**: must be long enough for the application to start; too short causes unnecessary recreation loops.
- **Regional MIG distribution**: by default uses `EVEN` or `BALANCED` distribution; configure `ANY_SINGLE_ZONE` only for zonal MIGs.
