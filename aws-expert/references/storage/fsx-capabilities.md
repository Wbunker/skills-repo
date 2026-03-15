# AWS FSx — Capabilities Reference
For CLI commands, see [fsx-cli.md](fsx-cli.md).

## FSx for Lustre

**Purpose**: High-performance parallel file system for compute-intensive workloads (ML, HPC, video processing, financial modeling) with native S3 integration for data repository access.

### Deployment Types

| Type | Data Persistence | Replication | Use Case |
|---|---|---|---|
| **Scratch 1** | Not replicated | No | Temporary; short-term processing; lowest cost |
| **Scratch 2** | Not replicated | No | Temporary; 6x faster baseline throughput than Scratch 1 |
| **Persistent 1** | Replicated within AZ | Yes (within AZ) | Longer-term; throughput-focused; SSD and HDD options |
| **Persistent 2** | Replicated within AZ | Yes (within AZ) | Longer-term; latest generation; higher throughput; SSD storage |

### Storage Options

| Tier | Latency | Use Case |
|---|---|---|
| **SSD** | Sub-millisecond | Small, random I/O; consistent low latency |
| **Intelligent-Tiering** | Sub-ms (hot); higher (cold) | Elastic; cost-effective; optional SSD read cache |
| **HDD** | Single-digit ms | Sequential, large I/O; optional 20% SSD read cache |

### Key Concepts

| Concept | Description |
|---|---|
| **Data repository association (DRA)** | Link file system to an S3 bucket; import existing S3 objects as files; export changes back to S3 |
| **HSM commands** | `hsm_archive` (copy file to S3), `hsm_restore` (import file from S3), `hsm_state` (check file state) |
| **POSIX compliance** | Supports standard Linux file system semantics; read-after-write consistency and file locking |

### Key Features

| Feature | Description |
|---|---|
| **S3 integration** | Transparently presents S3 objects as Lustre files; auto-import on first access or scheduled; export via DRA |
| **Performance** | Sub-millisecond latency; up to multiple TBps throughput; millions of IOPS |
| **Compute access** | EC2 (via Lustre client), EKS (CSI driver), ECS containers; on-premises via Direct Connect/VPN |
| **Encryption** | At rest (KMS); in transit (supported regions) |

### Important Constraints

- Works only with Linux (Amazon Linux 2023/2, RHEL, CentOS, Ubuntu, SUSE); no Windows support
- Scratch file systems do not replicate data; a server failure results in data loss
- Persistent file systems automatically replace failed file servers; data is preserved

---

## FSx for NetApp ONTAP

**Purpose**: Fully managed NetApp ONTAP file system on AWS; supports NFS, SMB, iSCSI, and NVMe protocols; enables migration from on-premises ONTAP with data management features like SnapMirror and tiering.

### Key Concepts

| Concept | Description |
|---|---|
| **File system** | The top-level ONTAP resource; Multi-AZ or Single-AZ deployment |
| **SVM (Storage Virtual Machine)** | Virtual storage server within the file system; provides data access via protocols; isolated namespace |
| **Volume** | ONTAP data container within an SVM; supports thin provisioning, snapshots, cloning, compression |
| **Capacity pool** | Lower-cost tier for infrequently accessed data; automatic tiering from SSD primary storage |
| **SnapMirror** | NetApp's native async replication; used for cross-region DR and data distribution |
| **SnapLock** | WORM compliance; Compliance mode (immutable, even from admins) and Enterprise mode |

### Deployment Options

| Type | Availability | Description |
|---|---|---|
| **Multi-AZ** | High availability | Active/standby across two AZs; automatic failover |
| **Single-AZ** | Optimized cost | Single AZ; suitable for dev/test or cost-sensitive workloads |

### Supported Protocols

NFS (v3, v4.0, v4.1, v4.2), SMB (v2/v3), iSCSI, NVMe over TCP

### Key Features

| Feature | Description |
|---|---|
| **Automatic data tiering** | Transitions infrequently accessed data to capacity pool (lower-cost) storage based on tiering policies |
| **SnapMirror replication** | Async replication to another FSx for ONTAP or on-premises ONTAP for DR |
| **Data efficiency** | Inline compression, deduplication, and compaction reduce storage consumption |
| **Snapshots and clones** | Near-instant point-in-time snapshots; zero-cost clones for dev/test |
| **Active Directory integration** | Authenticate Windows/Linux users via Microsoft Active Directory; Kerberos support |
| **FlexCache** | Caching layer to accelerate reads for distributed teams |
| **Antivirus scanning** | On-demand scanning integration |

### Important Constraints

- All protocols (NFS, SMB, iSCSI) can be served from the same SVM simultaneously
- Petabyte-scale datasets in a single namespace; up to tens of GBps throughput per file system

---

## FSx for OpenZFS

**Purpose**: Fully managed OpenZFS file system for Linux/macOS workloads; enables migration from on-premises ZFS or Linux file servers with high performance, snapshots, and data compression.

### Deployment Options

| Type | Availability | Failover |
|---|---|---|
| **Multi-AZ** | Cross-AZ replication | ~60 seconds |
| **Single-AZ (HA)** | Primary + standby in same AZ | ~60 seconds |
| **Single-AZ (non-HA)** | Self-healing within single AZ | ~30 minutes |

### Key Concepts

| Concept | Description |
|---|---|
| **File system** | Top-level resource; contains one or more volumes |
| **Volume** | Data container with independent quotas, compression settings, and snapshots |
| **Snapshot** | Near-instant point-in-time copy stored locally on the file system; no extra storage cost for unchanged data |
| **Clone** | Writable copy of a snapshot; instant creation; efficient for dev/test |

### Storage Options

| Tier | Description |
|---|---|
| **SSD** | High performance; pay for provisioned capacity |
| **Intelligent-Tiering** | Elastic; pay only for data stored; auto-tiering |

### Key Features

| Feature | Description |
|---|---|
| **NFS protocol** | v3, v4.0, v4.1, v4.2; accessible from Linux, Windows, macOS, and containers |
| **Data compression** | Inline transparent compression reduces storage consumption |
| **Performance** | Up to 2 million IOPS; hundreds of microseconds latency; up to 21 GBps throughput (in-memory/NVMe cache) |
| **Automatic daily backups** | Stored on S3; cross-region copy supported |
| **Thin provisioning** | Allocate capacity on demand; user/group quotas supported |
| **Encryption** | At rest (KMS); automatic in-transit encryption from supported EC2 instances |
| **IPv6 support** | Supports both IPv4-only and dual-stack (IPv4+IPv6) |

---

## FSx for Windows File Server

**Purpose**: Fully managed Windows-native file system; supports SMB protocol with Active Directory integration; designed for Windows workloads including home directories, business applications, and data analytics.

### Key Concepts

| Concept | Description |
|---|---|
| **Active Directory (AD)** | Required for user authentication and access control; supports AWS Managed AD or self-managed (on-premises) AD |
| **DFS Namespaces** | Distribute shared folders across file systems and servers under a single namespace; improves availability and load distribution |
| **Shadow copies** | VSS-based point-in-time copies of data; users can restore previous file versions self-service |
| **Multi-AZ** | Active and standby file servers in separate AZs; automatic failover within 30 seconds |
| **Single-AZ** | High availability within a single AZ; automatic failure detection and recovery |

### Supported Protocols

SMB versions 2.0 to 3.1.1; data in transit encrypted with SMB Kerberos session keys; accessible from Windows (Server 2008+, Windows 7+) and current Linux versions

### Storage Options

| Type | Use Case |
|---|---|
| **SSD** | Latency-sensitive workloads: databases, media processing, data analytics |
| **HDD** | Broad-spectrum workloads: home directories, departmental shares, content management |

### Key Features

| Feature | Description |
|---|---|
| **Active Directory integration** | Domain join during creation; authenticate users via AWS Managed AD or self-managed AD via AD Connector |
| **DFS Namespaces** | Consolidate multiple file shares into a single logical namespace; supports DFS Replication |
| **Shadow copies** | Scheduled VSS snapshots; users restore files self-service via Windows Previous Versions |
| **Storage/throughput independent** | Provision storage capacity (GiB), SSD IOPS, and throughput (MBps) independently; modify without downtime |
| **On-premises access** | Access via AWS Direct Connect or VPN |
| **Encryption** | At rest (KMS) and in transit (SMB Kerberos) |

### Use Cases

Business applications, home directories, web serving, content management, software build environments, media processing

---

## Amazon File Cache

**Purpose**: Fully managed, high-speed Lustre-based cache on AWS that provides a unified, high-performance access layer over data stored on-premises (NFS) or in Amazon S3 — without requiring data migration; designed to burst on-premises HPC and ML workloads to AWS.

### Key Concepts

| Concept | Description |
|---|---|
| **File cache** | The top-level resource; Lustre-based; deployed in a single AZ; presents a unified POSIX file system interface |
| **Deployment type** | `CACHE_1` — the only supported deployment type; single AZ with automatic file server replacement on failure |
| **Data repository association (DRA)** | Links the cache to a data source (NFS or S3); data loads on first access; up to 8 DRAs per cache; all DRAs must be the same type (all S3 or all NFS) |
| **Automatic eviction** | Unused cached data is automatically released to free space; no write-back (cache is read-only from the data source perspective unless HSM export is used) |
| **Metadata volume** | A separate 2.4 TiB MDT storage volume is always provisioned alongside data storage |

### Performance

| Dimension | Value |
|---|---|
| **Throughput** | 1,000 MB/s per TiB of storage capacity (e.g., 1.2 TiB = 1,200 MB/s; 9.6 TiB = 9,600 MB/s) |
| **Latency** | Sub-millisecond |
| **Storage capacity** | 1.2 TiB, 2.4 TiB, or increments of 2.4 TiB; SSD only |

### Supported Data Sources

| Source | Protocol | Notes |
|---|---|---|
| **Amazon S3** | S3 API | Data loads on first access; cache path cannot be root (`/`) |
| **On-premises NFS** | NFSv3 | Up to 500 subdirectories per DRA; cache path can be root only if one DRA is configured |
| **AWS-hosted NFS** | NFSv3 | Same NFSv3 constraints as on-premises |

### Key Features

| Feature | Description |
|---|---|
| **No data migration** | Data remains in source (S3 or NFS); cache is populated on demand |
| **Unified namespace** | Multiple NFS exports or S3 prefixes presented as a single Lustre file system |
| **Compute access** | EC2 (via Lustre client), ECS (Docker on EC2), EKS (CSI driver); Linux only |
| **Pre-loading** | Optional explicit pre-load before workload starts to avoid cold-start latency |
| **Encryption** | At rest (AWS KMS) and in transit |
| **Cross-AZ access** | EC2 instances in other AZs in the same VPC can access the cache (with appropriate networking) |

### Important Constraints

- Linux only — no Windows support (requires Lustre client)
- Single-AZ deployment; not highly available across AZs
- Data is not written back to the source repository from the cache automatically (HSM `hsm_archive` required for explicit export)
- Cannot mix S3 and NFS data repository associations on the same cache
- Automatic import/export policies are not supported (unlike FSx for Lustre Persistent file systems)
