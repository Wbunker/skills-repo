# Azure Virtual Machines — Capabilities Reference

For CLI commands, see [vms-cli.md](vms-cli.md).

## Azure Virtual Machines

**Purpose**: Provides on-demand, scalable IaaS compute in Azure. Foundational building block for lift-and-shift migrations, custom OS workloads, and any workload requiring full OS control.

### Core Concepts

| Concept | Description |
|---|---|
| **Virtual Machine** | A virtual server defined by a VM size (CPU, memory, network, storage) and launched from an image |
| **VM Image** | Preconfigured OS template from Azure Marketplace, Azure Compute Gallery, or custom-captured image |
| **VM Size** | Hardware specification (series, generation); determines vCPUs, memory, temp disk, network, and max disk count |
| **Network Interface (NIC)** | Virtual network adapter attached to a VNet subnet; each VM has at least one NIC |
| **Network Security Group (NSG)** | Stateful firewall rules applied at the NIC or subnet level; controls inbound/outbound traffic |
| **Public IP Address** | Optional static or dynamic IPv4/IPv6 address; can be attached to a NIC or Load Balancer |
| **Managed Disk** | Azure-managed persistent block storage; decoupled from VM lifecycle; supports snapshot and disk sharing |
| **Availability Set** | Logical grouping ensuring VMs are distributed across fault domains (separate racks) and update domains |
| **Availability Zone** | Physically separate datacenters within an Azure region; zone-redundant deployments survive datacenter failure |
| **Proximity Placement Group (PPG)** | Co-locates VMs on the same physical hardware cluster to minimize network latency |
| **User Data / cloud-init** | Bootstrap scripts or cloud-init config run at first boot; supports Linux cloud-init and Windows CustomScriptExtension |
| **VM Extensions** | Post-deployment agents and scripts (monitoring agents, DSC, custom scripts, disk encryption) |
| **Azure Hybrid Benefit** | License mobility — bring existing Windows Server or SQL Server licenses to reduce VM cost by up to 49% |
| **Instance Metadata Service (IMDS)** | REST endpoint at `169.254.169.254` providing identity, VM properties, tags, and managed identity tokens |

---

## Storage Options

| Type | Use Case | Notes |
|---|---|---|
| **OS Disk (Managed)** | Persistent boot volume | Defaults to Premium SSD P30 for most sizes; supports Standard HDD/SSD, Premium SSD v1/v2, Ultra Disk |
| **Data Disk (Managed)** | Additional persistent block storage | Up to 32 TB per disk; attach multiple disks and stripe with Storage Spaces / LVM |
| **Temporary Disk** | Ephemeral scratch space (lost on deallocation) | Size varies by VM family; `/dev/sdb` on Linux, `D:` on Windows; not on all sizes |
| **NVMe Local Disk** | Ultra-low-latency ephemeral NVMe (Lsv3, Ebsv5) | Lost on deallocation; ideal for high-IOPS NoSQL / cache tiers |
| **Azure Files (SMB/NFS)** | Shared network file system across VMs | Fully managed; Standard (HDD) and Premium (SSD) tiers |
| **Azure NetApp Files** | Enterprise NFS/SMB (SAP, HPC, VDI) | Low-latency; sub-millisecond performance tiers |
| **Ultra Disk** | Highest IOPS/throughput for demanding databases | Requires Ultra Disk-compatible VM size; configurable IOPS/MBps without resize |

### Managed Disk Performance Tiers

| Disk Type | Max IOPS | Max Throughput | Typical Use Case |
|---|---|---|---|
| **Standard HDD (LRS/ZRS)** | 500 | 60 MB/s | Dev/test, infrequently accessed data |
| **Standard SSD (LRS/ZRS)** | 6,000 | 750 MB/s | Low-IOPS web servers, light databases |
| **Premium SSD v1** | 20,000 | 900 MB/s | Most production workloads, SQL Server |
| **Premium SSD v2** | 80,000 | 1,200 MB/s | I/O-intensive databases without resize |
| **Ultra Disk** | 400,000 | 10,000 MB/s | SAP HANA, high-throughput databases |

---

## VM Series and Families

| Series | Category | Purpose | AWS Equivalent |
|---|---|---|---|
| **A-series** | General Purpose | Entry-level dev/test; low cost | T2 (light general purpose) |
| **B-series (burstable)** | General Purpose | Burstable CPU via credits; low baseline | T3 / T4g (burstable) |
| **D-series (Dv5, Ddsv5, Dav5)** | General Purpose | Balanced CPU/memory; broadest workload coverage | M-series (m5–m7) |
| **E-series (Ev5, Edsv5)** | Memory Optimized | High memory-to-CPU ratio; SAP, in-memory DBs | R-series (r5–r7) |
| **F-series (Fsv2)** | Compute Optimized | High CPU frequency; gaming, batch, analytics | C-series (c5–c7) |
| **G-series (Gv2)** | Memory + Storage | Large memory + local SSD | X-series |
| **H-series (HBv4, HCv4)** | HPC | High-bandwidth InfiniBand networking; MPI workloads | Hpc-series |
| **L-series (Lsv3)** | Storage Optimized | High-throughput local NVMe; NoSQL, caching | I-series (i3–i4) |
| **M-series (Mv2, Msv3)** | Memory Optimized (extreme) | Up to 11.4 TiB RAM; SAP HANA scale-up | X / U series |
| **N-series (NCv4, NDv4, NVv4)** | GPU | NVIDIA / AMD GPU for AI training, inference, visualization | G / P / Inf-series |
| **D-series with AMD (Dav5)** | General Purpose | AMD EPYC; cost-effective alternative to Intel D-series | M-series with AMD (a-suffix) |
| **E-series with AMD (Eav5)** | Memory Optimized | AMD EPYC high memory | R-series with AMD |
| **Bsv2** | General Purpose (burstable) | Next-gen B-series with higher baseline and burst | T4g (Graviton burstable) |
| **Dpsv6 / Epsv6 (Cobalt 100)** | General Purpose / Memory | Azure first-party Arm64 CPU (Cobalt 100) | M / R with Graviton |

### Key Size Naming Convention

`[Series][Sub-family][Version][Features]_[Size]`

Example: `Standard_D8ds_v5` = D-series, local SSD (d), premium storage (s), v5 generation, 8 vCPUs

Feature suffixes: `s` = premium storage capable, `d` = local temp SSD, `r` = remote NVMe, `i` = isolated (dedicated hardware)

---

## Key Features

| Feature | Description |
|---|---|
| **Azure Bastion** | Fully managed browser-based RDP/SSH without public IP or VPN; Standard tier adds native client and file transfer |
| **Serial Console** | Out-of-band text-mode console for emergency troubleshooting even when network is unreachable |
| **Boot Diagnostics** | Captures serial log and screenshot at boot; stored in a storage account; essential for boot failure diagnosis |
| **VM Extensions** | Post-deployment agents: AMA (Azure Monitor Agent), MDE (Defender), DSC, CustomScript, Key Vault Certificate Sync |
| **Hibernate** | Save VM RAM to OS disk and resume later at reduced cost; supported on select sizes with premium storage |
| **Trusted Launch** | Secure Boot + vTPM for generation 2 VMs; protects against bootkits and rootkits |
| **Confidential VMs (DCasv5, ECasv5)** | AMD SEV-SNP hardware isolation; data encrypted in memory; attestation via Microsoft Azure Attestation |
| **Run Command** | Execute scripts on VMs via ARM without SSH/RDP access; useful for ad-hoc remediation |
| **Automatic VM Guest Patching** | Azure-orchestrated OS patch installation during low-traffic windows |
| **Auto-shutdown** | Schedule VM auto-shutdown to save cost in dev/test environments |
| **Encryption at Host** | End-to-end encryption for all managed disks including temp disk and cache; no performance impact |

---

## Purchasing Options

| Model | Commitment | Discount vs PAYG | Best For |
|---|---|---|---|
| **Pay-as-you-go (PAYG)** | None | — | Dev/test, unpredictable workloads, short-term |
| **Azure Reserved VM Instances (1yr)** | 1 year, specific VM family + region | ~36–40% | Steady-state production with known VM size |
| **Azure Reserved VM Instances (3yr)** | 3 years, specific VM family + region | ~55–65% | Long-running stable workloads |
| **Azure Savings Plans (1yr)** | 1 year, hourly spend commit, flexible | ~11–50% | Flexible — applies across VM sizes, AKS nodes, Functions |
| **Azure Savings Plans (3yr)** | 3 years, hourly spend commit | ~17–65% | Maximum discount with flexibility |
| **Azure Spot VMs** | None (preemptible) | Up to ~90% | Fault-tolerant batch, CI/CD, rendering, dev/test |
| **Azure Hybrid Benefit (Windows Server)** | Existing license required | Up to ~49% | Migrate on-prem Windows Server licenses with SA |
| **Azure Hybrid Benefit (SQL Server)** | Existing license required | Eliminates SQL license cost | SQL Server VMs; stack with Reserved Instances |
| **Azure Dev/Test pricing** | Visual Studio subscription required | ~45–55% | Dev and test environments only |

### Azure Hybrid Benefit Details

- **Windows Server Standard**: covers up to 2 Azure VMs (up to 16 cores each)
- **Windows Server Datacenter**: unlimited Azure VMs
- **SQL Server Standard**: covers 1 Azure SQL / SQL Managed Instance vCore
- **SQL Server Enterprise**: covers 4 vCores of Azure SQL

---

## Availability Options

### Availability Sets

Logical groups distributing VMs across fault domains (FD) and update domains (UD) within a single datacenter:

- Up to 3 **fault domains** (separate power, network, cooling — different racks)
- Up to 20 **update domains** (batched maintenance windows; only 1 UD rebooted at a time)
- Guarantees 99.95% SLA for two or more VMs in an availability set
- No cost for the availability set itself
- Cannot combine with Availability Zones

### Availability Zones

Physically separate datacenters (with independent power, cooling, networking) within an Azure region:

- Supports zone-redundant deployments for VMs (pin instances to Zone 1, 2, or 3)
- Guarantees 99.99% SLA for two or more VMs across different zones
- Available in most Azure regions (check zone availability per region)
- Preferred over Availability Sets for new deployments — zone-redundant resources span zones automatically

### Proximity Placement Groups (PPG)

- Co-locates VMs within the same physical Azure host cluster to minimize network latency
- Essential for latency-sensitive tiers (database + app server co-location, HPC MPI workloads)
- Can be combined with Availability Sets or Availability Zones
- VM sizes must be available in the PPG's target datacenter

---

## Important Azure-Specific Nuances

- **Deallocation vs. Stop**: `Stop` (OS shutdown) keeps the VM allocated and charges continue; `Deallocate` releases compute and stops billing for VM, but storage costs remain. Use `az vm deallocate` to stop billing.
- **Accelerated Networking**: SR-IOV for sub-millisecond latency and up to 30 Gbps; required for most production VMs; enabled by default on D/E/F/N-series v4+.
- **Ultra Disk requirements**: VM must be in an availability zone and use an Ultra-compatible size (e.g., Esv3, Dsv3, M-series). Not available in all regions.
- **Premium Storage**: Requires `s`-suffix VM sizes (e.g., `Standard_D8s_v5`, not `Standard_D8_v5`). Without `s`, you cannot attach Premium SSD disks.
- **Generation 2 VMs**: Required for Trusted Launch, Confidential VMs, Ultra Disk, and some large memory sizes. Most modern marketplace images support Gen2.
- **Zone-pinned reservations**: Reserved Instances can be scoped to a zone, resource group, subscription, or management group — scope determines where the discount applies.
- **Linux licensing**: Azure provides pay-as-you-go Linux images (RHEL, SUSE) with no separate licensing overhead; Ubuntu, Debian, and AL2023-equivalent images are included.
