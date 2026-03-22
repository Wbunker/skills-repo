# Azure Managed Disks — Capabilities Reference
For CLI commands, see [disk-cli.md](disk-cli.md).

## Azure Managed Disks

**Purpose**: Block storage volumes for Azure Virtual Machines. Managed disks abstract the underlying storage account management, provide built-in redundancy, and offer multiple performance and cost tiers to match diverse workload requirements.

### Disk Types

| Type | Short Name | Storage | Max IOPS | Max Throughput | Max Size | Latency | Use Case |
|---|---|---|---|---|---|---|---|
| **Standard HDD** | S (e.g., S10) | Magnetic HDD | 500 IOPS/disk | 60 MiB/s | 32 TiB | ~10ms | Dev/test, non-critical backups, infrequent access |
| **Standard SSD** | E (e.g., E10) | SSD | 6,000 IOPS/disk | 750 MiB/s | 32 TiB | ~2ms | Web servers, lightly used production, entry-level ERP |
| **Premium SSD** | P (e.g., P30) | NVMe SSD | 20,000 IOPS/disk | 900 MiB/s | 32 TiB | <1ms | Most production databases, medium ERP, VDI |
| **Premium SSD v2** | — (no tier names) | NVMe SSD | 80,000 IOPS/disk | 1,200 MiB/s | 64 TiB | <1ms sub-ms | IOPS-intensive: SAP, SQL, Oracle, Redis on VMs |
| **Ultra Disk** | — | NVMe SSD | 400,000 IOPS/disk | 10,000 MiB/s | 64 TiB | <0.5ms | Most demanding: top-tier SAP HANA, HPC, real-time analytics |

### Premium SSD Performance Tiers

- Performance scales with disk size (provisioned IOPS/throughput tied to tier)
- **P-series size tiers**: P1 (4 GiB, 120 IOPS) → P30 (1 TiB, 5,000 IOPS) → P80 (32 TiB, 20,000 IOPS)
- **Performance tier upgrade**: Temporarily increase disk performance beyond base tier without resizing (e.g., P10 disk running at P30 performance); billed at upgraded tier; reset anytime

### Premium SSD v2 Key Differentiators

- **Independently configure** capacity, IOPS, and throughput (not tied to disk size tiers)
- Up to 80,000 IOPS and 1,200 MiB/s per disk
- Sub-millisecond latency for both reads and writes
- Does not support: OS disk for most VM sizes, shared disks, Azure Site Recovery replication, host caching
- Available in selected regions and AZs only; must be deployed in same AZ as VM

### Ultra Disk Key Differentiators

- Fully independent capacity, IOPS, and throughput configuration
- Can change performance settings **while disk is live** (no downtime for performance changes)
- Requires specific VM families supporting Ultra Disk (`-s` suffix VMs)
- Must be deployed in same AZ as VM; not available in all regions
- Does not support: snapshots, disk export, images, scale sets (standard), shared disks across regions, Azure Backup

---

## Disk Roles

| Role | Description | Notes |
|---|---|---|
| **OS Disk** | Boots the operating system; contains the OS volume | Default 127–1,023 GiB depending on image; registered as SATA; max throughput limited by VM SKU |
| **Data Disk** | Additional storage for application data | Up to 32 data disks per VM (varies by VM size); registered as SCSI; LUN-addressed |
| **Temp Disk** | Ephemeral local SSD attached to physical host | **Lost on deallocation, resize, host move**; use for pagefile/swap, temp files; not for persistent data |

### Ephemeral OS Disk

- OS disk stored on local VM host storage (NVMe SSD); no separate managed disk
- Zero cost; lower read latency than remote managed disk OS disk
- OS state lost on deallocation/reimage; suitable for stateless VMs, AKS nodes
- Size limited to VM's temp disk or cache size; image must fit

---

## Disk Encryption

| Method | Key Management | What It Encrypts | Notes |
|---|---|---|---|
| **Server-Side Encryption (SSE) with PMK** | Platform-Managed Key (Microsoft-managed) | Data at rest in Azure storage | Default; automatic; no configuration needed |
| **SSE with CMK** | Customer-Managed Key (Azure Key Vault) | Data at rest in Azure storage | Full control; key rotation, revocation; requires Disk Encryption Set |
| **Azure Disk Encryption (ADE)** | Azure Key Vault (BitLocker on Windows; DM-Crypt on Linux) | OS and data disk volumes in-guest | Encrypts from within VM; required for some compliance standards; managed by VM |
| **Confidential disk encryption** | vTPM-sealed key; hardware-backed | Data in use and at rest | For Confidential VMs; additional security for sensitive workloads |
| **Double encryption at rest** | PMK + CMK (both layers) | Data at rest | Highest assurance; use Disk Encryption Set with `encryptionType=EncryptionAtRestWithPlatformAndCustomerKeys` |

### Disk Encryption Set (DES)

- Azure resource that links a CMK in Azure Key Vault (or Managed HSM) to disks
- Assign DES to disk at creation or associate after creation (triggers background re-encryption)
- Supports automatic key rotation when configured with Key Vault key rotation policy
- Key Vault must be in same region as disks; Key Vault must have soft delete and purge protection enabled

---

## Shared Disks

- Allows a single managed disk to be attached to multiple VMs simultaneously (read/write)
- Use case: Windows Server Failover Cluster (WSFC) with SQL Server FCI, SAP ASCS/ERS
- Supported disk types: Premium SSD, Premium SSD v2, Ultra Disk
- Requires cluster software (WSFC, Pacemaker) to manage write coordination; Azure does not arbitrate writes
- `maxShares` property controls maximum concurrent attachments (Premium SSD: max 5; Ultra: max 5)

---

## Snapshots

| Feature | Description |
|---|---|
| **Full snapshot** | Complete copy of disk at point in time; stored as page blob in Standard storage by default |
| **Incremental snapshot** | Only changed blocks since last snapshot; same data as full but lower cost and faster creation |
| **Cross-region copy** | Copy snapshots to another region for DR or golden image distribution |
| **Cross-subscription copy** | Share snapshot with another Azure subscription |
| **Snapshot access** | Generate SAS URL to download VHD; export to blob storage |

- **Incremental snapshots strongly recommended**: same recovery capability at fraction of cost
- Snapshots billed only for changed data (incremental) or full disk size
- Disk must not be actively performing I/O for guaranteed consistency (or use application-level quiesce)
- Snapshot storage redundancy: LRS (default) or ZRS (for zone-resilient snapshots)

---

## Disk Bursting

### Credit-Based Bursting (Standard SSD, Premium SSD P1–P20)

- Accumulate burst credits when disk IOPS/throughput below baseline
- Spend credits when workload exceeds baseline; up to burst limit
- Maximum burst: 3,500 IOPS / 170 MiB/s (Standard SSD); 3,500 IOPS / 170 MiB/s (Premium SSD P1–P20)
- Credits accumulate at 1 IOPS-minute per spare IOPS; capped at 30-minute worth of credit

### On-Demand Bursting (Premium SSD P30 and above)

- Burst beyond disk baseline without credit accumulation; pay per burst minute
- Enable per disk: `az disk update --disk-iops-read-write` or `burstingEnabled=true`
- Max burst: 30,000 IOPS / 1,000 MiB/s
- Charged per-second when bursting above baseline (no credit system)

---

## Managed vs Unmanaged Disks

- **Managed Disks**: Microsoft manages storage accounts; automatic placement; fault domain integration; RBAC; required for Availability Sets with FD alignment and AZs
- **Unmanaged Disks**: Stored as page blobs in customer storage accounts; **deprecated; do not use for new deployments**; no AZ support; storage account limits apply

---

## Azure Disk Pool (iSCSI)

- Expose managed disks as iSCSI LUNs to multiple hosts
- Primary use case: Azure VMware Solution (AVS) as external datastore; Azure Kubernetes Service (AKS) with shared storage
- Disk Pool resource manages iSCSI target and client connections
- Supports Ultra Disk, Premium SSD, and Standard SSD (Premium SSD v2 not supported)
- Being superseded by ANF and other storage options for many scenarios

---

## Important Patterns & Constraints

- VM must be the same AZ as Premium SSD v2 and Ultra Disk; cannot use across AZs
- Maximum disk size (32 or 64 TiB) also limited by OS partition table (MBR: 2 TiB; GPT: 18 EiB — use GPT for large disks)
- Changing disk type requires deallocating VM (or online resize for supported SKUs and OS)
- Snapshot of Premium SSD v2 and Ultra Disk: not supported — use application-level backup or Azure Backup agent
- ADE (BitLocker/DM-Crypt) and SSE with CMK are **independent** — both can be applied simultaneously for defense in depth
- Host caching options per disk: None / ReadOnly / ReadWrite; ReadOnly cache for DB data files; ReadWrite for OS disk; None for transaction log disks (latency-sensitive sequential writes)
- VM-level throughput and IOPS caps apply across all attached disks — individual disk limits are ceilings, not guarantees
