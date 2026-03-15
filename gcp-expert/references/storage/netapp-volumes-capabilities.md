# NetApp Cloud Volumes — Capabilities Reference

See also: [netapp-volumes-cli.md](netapp-volumes-cli.md)

---

## Purpose

NetApp Cloud Volumes (Google Cloud NetApp Volumes / GCNV) is an enterprise-grade, fully managed file storage service on Google Cloud built on NetApp ONTAP technology. It provides advanced data management capabilities — snapshots, clones, cross-region replication, deduplication, compression, and dual-protocol NFS/SMB access — well beyond what Cloud Filestore offers. It is the preferred choice for SAP HANA, Windows file server migrations, HPC workloads, and any workload already relying on ONTAP capabilities on-premises.

---

## Core Concepts

| Concept | Description |
|---|---|
| Volume | The primary storage unit; an NFS share or SMB share (or both) mounted by clients. Provisioned within a storage pool. |
| Pool (Storage Pool / Capacity Pool) | A block of provisioned capacity within a region and service level that contains one or more volumes. |
| Service Type | The product variant: CVS-SW (software, zonal, NFS-only) or CVS-Performance / GCNV (SSD, zonal, NFS + SMB). |
| Protocol | The access protocol(s) for a volume: NFS v3, NFS v4.1, SMB/CIFS, or dual-protocol (NFS + SMB simultaneously). |
| Snapshot | An ONTAP-native, instant, space-efficient read-only copy of a volume at a point in time. Stored within the volume's allocated capacity. |
| Snapshot Policy | A schedule-based policy defining how often snapshots are taken and how many copies to retain per frequency tier (hourly, daily, weekly, monthly). |
| Replication | Asynchronous cross-region replication of a volume to a destination pool in another Google Cloud region; used for DR. |
| ONTAP | NetApp's storage operating system underlying the service; provides enterprise data management (dedup, compression, clones, replication). |
| QoS | Quality of Service; throughput limits (MiB/s) are determined by the service level and allocated capacity. |
| Active Directory Integration | Domain-join for SMB volumes; enables Windows ACL-based permissions and Kerberos authentication for NFS v4.1. |
| Export Policy | A set of IP-based rules controlling NFS client access to a volume (read-only, read-write, or no access per CIDR). |
| SMB Share | A Windows-compatible file share exposed from the volume; access controlled via Windows ACLs and AD permissions. |
| FlexClone | An ONTAP instant writable clone of a volume or snapshot; space-efficient (only changes consume new space). |
| LDAP Integration | Unix user and group mapping via LDAP; required for consistent UID/GID resolution in dual-protocol volumes. |

---

## Service Types

| Type | Description | Use Case |
|---|---|---|
| CVS-SW (Software) | Zonal; cost-optimized; NFS v3/v4.1 only; lower performance tier; smaller minimum volume size | Dev/test, smaller workloads, general-purpose NFS |
| CVS-Performance | Zonal; high-performance SSD backend; NFS v3/v4.1 + SMB/CIFS; multiple service levels (Standard, Premium, Extreme) | Production databases, SAP HANA, HPC, Windows file servers |
| Google Cloud NetApp Volumes (GCNV) | Newer unified product branding replacing CVS; regional HA option available; full ONTAP feature set; managed via gcloud netapp commands | Enterprise production workloads, regulated industries, lift-and-shift of on-premises NetApp |

> Note: GCNV is the current strategic name. "CVS-Performance" and "CVS-SW" are legacy designations. New deployments should use the GCNV terminology and gcloud netapp CLI.

---

## Service Levels (CVS-Performance / GCNV)

Throughput scales linearly with allocated volume capacity.

| Service Level | Throughput per TiB | Typical Use Case |
|---|---|---|
| Standard | 16 MiB/s per TiB | General workloads, home directories, content repositories |
| Premium | 64 MiB/s per TiB | Databases, analytics, enterprise applications |
| Extreme | 128 MiB/s per TiB | SAP HANA, HPC, latency-sensitive high-throughput workloads |

Example: A 4 TiB Premium volume delivers up to 256 MiB/s throughput. To increase throughput, increase the allocated capacity (even if storage is not fully used).

---

## Key Features

### ONTAP Snapshots

- Instant, space-efficient, policy-based point-in-time copies stored within the volume.
- Only changed blocks consume additional space; the snapshot itself has zero overhead at creation.
- Accessible from clients via the hidden `.snapshot` directory (NFS) or `~snapshot` share (SMB).
- Snapshot policies define per-frequency schedules:
  - Hourly: take a snapshot every N minutes past the hour; keep X copies.
  - Daily: take at a specific hour/minute; keep X copies.
  - Weekly: take on a specific day/hour/minute; keep X copies.
  - Monthly: take on a specific day of month; keep X copies.
- Volumes can be reverted to any snapshot (full revert) or individual files restored from the `.snapshot` directory.

### Cross-Region Replication

- Asynchronous replication of a source volume to a destination volume in another Google Cloud region.
- Replication schedule options: every 10 minutes, hourly, daily.
- RPO is determined by the replication schedule and data change rate.
- DR failover: reverse the replication relationship to promote the destination to read-write.
- Data travels over Google's private network (not the public internet); encrypted in transit with TLS.
- Destination volume is read-only until failover is initiated.

### Dual-Protocol Access

- A single volume is simultaneously accessible via NFS (v3 or v4.1) and SMB/CIFS.
- Unified permission model: security style can be set to NTFS (Windows ACLs dominate) or Unix (Unix permissions dominate).
- LDAP provides UID/GID mapping for Unix users accessing an NTFS-style volume, and vice versa.
- Eliminates the need to maintain separate NFS and SMB volumes for mixed Linux/Windows workloads.

### Active Directory Integration

- Required for any SMB volume.
- The service domain-joins a computer account into the specified AD domain using a service account.
- Supports multiple DNS servers for resilience.
- Kerberos authentication for NFS v4.1: provides stronger security than AUTH_SYS (IP-based) used with NFS v3.
- NetBIOS prefix defines the computer account name created in AD.

### Backup (NetApp Cloud Backup / Volume Backup)

- Volume-level backups written to Google Cloud Storage; independent of snapshots.
- Backup policies define frequency and retention.
- Restores can target the same volume or a new volume.
- Backup storage is billed separately from volume capacity.

### FlexClone (Volume Clones)

- Instantly create a fully writable clone of a volume from any snapshot.
- Space-efficient: the clone shares data blocks with the parent and only new writes consume additional space.
- Use cases: test/dev environments, pre-production data copies, parallel processing pipelines.
- Clones appear as independent volumes after creation and can be resized or snapshotted independently.

### Export Policies (NFS Access Control)

- One or more rules per volume; evaluated in order.
- Each rule specifies: allowed client CIDR(s), access type (READ_ONLY, READ_WRITE, NO_ACCESS), protocol version(s) (NFSv3, NFSv4), root access squashing.
- Supports Kerberos5 (authentication only), Kerberos5i (integrity), Kerberos5p (privacy + encryption) for NFSv4.1.

### SMB Share Permissions

- Windows ACL-based permissions (NTFS DACLs) on files and directories.
- Access-based enumeration (ABE): users only see files/directories they have permission to access.
- SMB share-level permissions layered on top of NTFS file-level permissions.
- Shadow Copies: accessible via Windows Previous Versions from ONTAP snapshots.

### LDAP Integration

- Required for dual-protocol volumes to resolve Unix UIDs/GIDs for AD users (and AD SIDs for Unix users).
- Supports RFC 2307 schema (uidNumber, gidNumber attributes in AD).
- LDAP signing and channel binding for security.

### Deduplication and Compression

- Inline and post-process deduplication: removes duplicate data blocks, reducing effective storage consumption.
- Inline and post-process compression: reduces data size before or after writing to disk.
- Both are enabled by default and transparent to clients; reduce effective storage cost for compressible datasets.

---

## NetApp Cloud Volumes vs Cloud Filestore

| Feature | Cloud Filestore | NetApp Cloud Volumes |
|---|---|---|
| Protocol | NFS v3 / NFS v4.1 | NFS v3, NFS v4.1, SMB/CIFS, Dual-protocol |
| Snapshots | Yes (limited, per-instance) | ONTAP snapshots (instant, space-efficient, policy-based) |
| Cross-Region Replication | Limited (Filestore Enterprise only) | Full async cross-region replication with DR failover |
| ONTAP Features | No | Yes: FlexClone, deduplication, compression, replication |
| Active Directory / SMB | No | Yes: native SMB, AD domain join, Kerberos NFS |
| Dual-Protocol | No | Yes (NFS + SMB on same volume) |
| Volume Clones | No | Yes (FlexClone, instant, space-efficient) |
| Performance Scaling | Tier-based (Basic/High Scale/Enterprise) | Linear with capacity × service level |
| SAP HANA Certification | No | Yes (certified NetApp storage for SAP) |
| Minimum Volume Size | 1 TiB (Basic HDD) | 100 GiB (CVS-SW), 1 TiB (CVS-Performance/GCNV) |
| Cost | Lower | Higher (justified by enterprise feature set) |
| Management | gcloud filestore | gcloud netapp / Google Cloud Console |

---

## Use Cases

- **SAP HANA and SAP Applications**: NetApp Cloud Volumes is SAP-certified. Provides the low latency, high throughput, and snapshot/clone capabilities required for SAP HANA data/log volumes and SAP application layers.
- **Windows File Server Migration**: Lift-and-shift of on-premises Windows file servers. SMB shares with native Windows ACL permissions, AD integration, and shadow copy (Previous Versions) support make the transition seamless.
- **Dual-Protocol Shared Storage**: Applications with mixed Linux (NFS) and Windows (SMB) clients reading/writing the same data. Unified permissions via LDAP and AD avoid data sync overhead.
- **HPC Scratch Volumes**: Extreme service level delivers up to 128 MiB/s per TiB; large volumes achieve hundreds of GiB/s throughput for parallel workloads.
- **Application Data with ONTAP Snapshot/Clone Workflows**: CI/CD pipelines, database refresh workflows, and test environment provisioning benefit from instant, space-efficient FlexClone volumes from production snapshots.
- **Lift-and-Shift of On-Premises NetApp Storage**: Workloads running on on-premises NetApp FAS/AFF systems can replicate directly to GCNV using SnapMirror, enabling phased migrations with minimal cutover windows.
- **Disaster Recovery**: Cross-region replication with configurable RPO (10 minutes to daily); DR failover by reversing the replication relationship.

---

## Pricing

- Billed per **GiB allocated** per month, not per GiB used. Allocate only what is needed.
- Price varies by service level: Standard < Premium < Extreme.
- CVS-SW is the lowest-cost tier; CVS-Performance/GCNV at Premium or Extreme is significantly higher.
- Cross-region replication: additional charges for replication data transfer and destination pool capacity.
- Snapshots: snapshot data that exceeds the volume's allocated capacity is billed as additional capacity.
- Backup: separate billing for backup data stored in Cloud Storage.
- No ingress/egress charges for mounting from VMs in the same region/VPC.

---

## Important Patterns and Constraints

- **Zonal by default**: GCNV volumes are single-zone. For high availability and DR, configure cross-region replication to a pool in a second region or use the regional HA option where available.
- **Minimum volume sizes**: CVS-SW minimum is 100 GiB; CVS-Performance and GCNV minimum is 1 TiB. Volumes smaller than 1 TiB on CVS-Performance still incur the 1 TiB minimum billing.
- **Storage pool sizing**: The storage pool must have sufficient free capacity to accommodate all volumes within it. Pool capacity cannot be automatically expanded; update the pool's capacity as needed.
- **Management interfaces**: Managed via Google Cloud Console and gcloud netapp CLI (preferred for new deployments). Legacy NetApp Cloud Manager (BlueXP) is also supported but should not be used alongside the gcloud-native approach for the same resources.
- **Deduplication and compression**: Enabled by default. The effective storage ratio depends on the data type; incompressible data (video, encrypted files) will not benefit.
- **Network access**: Volumes are accessible only from VMs within the same VPC (or a peered VPC) using private IP addresses. No public IP access.
- **Cross-region replication traffic**: Uses Google's private backbone network; data encrypted in transit. Not subject to standard internet egress pricing.
- **Active Directory prerequisite**: SMB volumes and Kerberos NFS require an Active Directory configuration to be created in the same region before the volume is created.
- **LDAP requirement for dual-protocol**: A properly configured LDAP server (typically AD with RFC 2307 attributes) is required for consistent UID/GID resolution in dual-protocol volumes.
- **Quota and limits**: Project-level quotas apply to number of pools, volumes, replications, and total capacity. Request quota increases via Cloud Console before large-scale deployments.
