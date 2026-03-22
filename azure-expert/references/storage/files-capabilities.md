# Azure Files — Capabilities Reference
For CLI commands, see [files-cli.md](files-cli.md).

## Azure Files

**Purpose**: Fully managed cloud file shares accessible via SMB (Server Message Block) and NFS (Network File System) protocols. Replace or augment on-premises file servers; lift-and-shift legacy applications requiring shared file storage; centralize configuration and log files across VMs.

### Core Concepts

```
Storage Account → File Share → Directory → File
```

| Component | Description |
|---|---|
| **Storage Account** | Container for file shares; use General Purpose v2 (standard) or Premium File Shares (SSD) |
| **File Share** | Top-level container; up to 100 TiB (large file shares); provisioned or pay-as-you-go |
| **Directory** | Hierarchical folder structure within a share |
| **File** | Individual file; up to 4 TiB per file |

### SMB Protocol Support

| Version | Description |
|---|---|
| **SMB 2.1** | Supported from Azure VMs within same region; no encryption in transit |
| **SMB 3.0** | Encryption in transit (AES-128-CCM/GCM); required for cross-region or on-premises access |
| **SMB 3.1.1** | AES-128-GCM encryption; preferred for Windows 10+ and Windows Server 2019+ |

- SMB shares accessible from Windows, Linux, and macOS
- Port 445 must be open from client to storage account endpoint
- Kerberos authentication via Active Directory Domain Services or Entra Domain Services

### NFS 4.1 Protocol Support

- Available only on **Premium File Shares** (SSD storage accounts)
- No gateway required; native NFS mount from Linux VMs
- Supports NFSv4.1 mandatory locking, pseudo-filesystem, and delegation
- Authentication: host-based (IP-based); Kerberos not supported for NFS
- Requires private endpoint or VNet service endpoint (no public NFS access)

### Share Tiers

| Tier | Account Type | Storage | IOPS | Throughput | Use Case |
|---|---|---|---|---|---|
| **Transaction Optimized** | Standard (GPv2) | HDD | Up to 10,000 | Up to 300 MiB/s (large) | General-purpose; high transaction volume; AI training checkpoints |
| **Hot** | Standard (GPv2) | HDD | Up to 10,000 | Up to 300 MiB/s | Frequently accessed general file shares |
| **Cool** | Standard (GPv2) | HDD | Up to 10,000 | Up to 300 MiB/s | Infrequently accessed; lower storage cost, higher access cost |
| **Premium** | Premium File Shares (SSD) | NVMe SSD | Up to 100,000+ | Up to 10 GiB/s | Low-latency (<1ms), IOPS-intensive: databases, DevOps tools, ERP |

- Premium share IOPS provisioned: baseline 3,000 + 1 IOPS per GiB provisioned; burst up to 3x baseline
- Standard shares: pay-as-you-go for storage used; Premium shares: provisioned capacity billing

### Large File Shares

- Standard shares: up to 100 TiB (enabled at storage account level; LRS/ZRS only; not compatible with GRS/GZRS)
- Premium shares: 100 TiB by default
- Large file share accounts: **cannot be changed to GRS/GZRS** after enabling large file shares

---

## Azure File Sync

**Purpose**: Hybrid cloud service that centralizes file shares in Azure while keeping local Windows Server caches. Enables multi-site sync, cloud tiering, and migration scenarios.

### Architecture Components

| Component | Description |
|---|---|
| **Storage Sync Service** | Top-level Azure resource; regional; connects on-premises servers to Azure |
| **Sync Group** | Logical grouping of one cloud endpoint (Azure file share) and one or more server endpoints |
| **Cloud Endpoint** | Azure file share participating in sync; one per sync group |
| **Server Endpoint** | Path on a registered Windows Server (physical or VM) participating in sync |
| **Registered Server** | Windows Server 2012 R2+ registered with Storage Sync Service; stores file share agent |

### Cloud Tiering

- Automatically tiers infrequently accessed files to Azure; keeps hot files local on-premises
- **Volume free space policy**: maintain X% free space on local volume (default 20%)
- **Date policy**: tier files not accessed in N days
- Tiered files appear locally as reparse points; transparently recalled on access
- Background tiering runs every 24 hours or on policy change

### Key Features

| Feature | Description |
|---|---|
| **Multi-site sync** | Multiple server endpoints in a sync group stay in sync via Azure file share as hub |
| **Conflict handling** | Last-writer-wins for concurrent edits; conflict copies preserved |
| **Namespace restore** | Restore entire namespace from Azure before recalling file data |
| **Offline data transfer** | Use Azure Data Box to seed initial data, then sync delta |
| **Change detection** | Server-side: immediate; cloud-side: every 24 hours (triggered by enumeration job) |

### Supported Platforms

- Windows Server 2012 R2, 2016, 2019, 2022; Windows Server Core
- Azure File Sync agent installed on each server endpoint

---

## Snapshots

| Feature | Description |
|---|---|
| **Share-level snapshots** | Point-in-time read-only copy of entire file share; captured incrementally (only changed blocks) |
| **Frequency** | Manual or scheduled via Backup policies (Azure Backup integration) |
| **Retention** | Up to 200 snapshots per share |
| **Access** | Browse via `.snapshot` directory (Linux) or Previous Versions (Windows SMB) |
| **Restore** | Restore individual files or entire share from snapshot |
| **VSS integration** | Windows Volume Shadow Copy Service; enables application-consistent snapshots via Azure Backup |

---

## Authentication and Authorization

### Identity-Based Authentication

| Method | Protocol | Description |
|---|---|---|
| **Active Directory Domain Services (AD DS)** | SMB | On-premises AD; join storage account to domain; Kerberos tickets; supports hybrid identity |
| **Entra Domain Services (Entra DS)** | SMB | Cloud-managed AD; for cloud-only or Entra ID tenants; Kerberos authentication |
| **Entra ID (preview)** | SMB | Direct Entra ID Kerberos; passwordless access for hybrid-joined devices |
| **Local users** | NFS, SFTP | Host-based authentication; no Kerberos for NFS |

### Permission Model (SMB)

- **Share-level RBAC**: Storage File Data SMB Share Reader/Contributor/Elevated Contributor roles assigned on the share
- **Directory/File ACLs**: Windows NTFS-style ACLs; set via File Explorer or `icacls`; replicated to Azure and enforced by SMB layer
- Effective permission = more restrictive of share-level RBAC and file-level ACL

### Secure Access

- **Private Endpoint**: Expose file share via private IP in VNet; eliminates public internet exposure; required for NFS
- **Service Endpoint**: Route traffic via Microsoft backbone; not fully private (public IP still used)
- **Firewall rules**: Restrict to specific VNets and IP ranges; enable trusted Azure services
- Disable Shared Key access to enforce identity-based authentication

---

## Azure NetApp Files (ANF)

**Purpose**: Enterprise-grade NFS (v3, v4.1) and SMB file services built on NetApp ONTAP technology. Designed for latency-sensitive, high-performance workloads that require sub-millisecond response times and enterprise storage features.

### Use Cases

| Workload | Protocol | Notes |
|---|---|---|
| **Oracle Database** | NFS v3/v4.1 | dNFS; SAP Oracle certified |
| **SAP HANA** | NFS v4.1 | SAP HANA TDI certified; latency <1ms |
| **High-Performance Computing** | NFS v3 | Research, simulation, rendering |
| **Virtual Desktops (AVD)** | SMB | FSLogix profile containers |
| **General Enterprise NAS** | NFS / SMB | Replace on-premises NAS appliances |

### Architecture

| Component | Description |
|---|---|
| **NetApp Account** | Regional container for capacity pools |
| **Capacity Pool** | Provisioned throughput pool (4–500 TiB); service level determines throughput per TiB |
| **Volume** | Individual file share backed by capacity pool; up to 100 TiB |
| **Snapshot** | NetApp ONTAP snapshots; near-instantaneous; efficient storage (only delta) |

### Service Levels

| Level | Throughput | Use Case |
|---|---|---|
| **Standard** | 16 MiB/s per TiB | General file services |
| **Premium** | 64 MiB/s per TiB | Databases, ERP, VDI |
| **Ultra** | 128 MiB/s per TiB | Latency-critical: SAP HANA, Oracle |

### Key Features

- **Cross-region replication**: async volume replication for DR; RPO minutes
- **Cross-zone replication**: sync replication across AZs (zonal volumes)
- **Volume snapshots and clones**: instant; space-efficient; used for DevTest clones
- **Dynamic service level change**: move volume between Standard/Premium/Ultra without downtime
- **Cool access tiering**: tier infrequently accessed data to lower-cost storage within ANF
- **Application Volume Groups**: pre-validated layouts for SAP HANA, Oracle (simplified deployment)
- **Backup**: ANF Backup feature for long-term retention separate from snapshots

---

## Important Patterns & Constraints

- Standard file shares require port 445 to be open; many ISPs block this port — use VPN or ExpressRoute for on-premises access
- Large file shares (>5 TiB) on Standard accounts require LRS or ZRS; incompatible with GRS/GZRS
- NFS 4.1 requires Premium tier and private endpoint or VNet service endpoint
- Azure File Sync requires Windows Server; Linux servers not supported as sync endpoints
- ANF volumes must be in a delegated subnet (`Microsoft.NetApp/volumes`); minimum /28 subnet
- SMB Multichannel (multiple NIC/queue pairs) available on Premium shares for higher throughput
- Cloud tiering requires at least 64 GiB per volume on the local server endpoint
- Cannot mix SMB and NFS protocols on the same file share (protocol chosen at share creation)
