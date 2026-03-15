# Filestore — Capabilities Reference

CLI reference: [filestore-cli.md](filestore-cli.md)

## Purpose

Managed NFS (Network File System) file shares for applications requiring shared file system access. Filestore provides POSIX-compliant file storage accessible from multiple Compute Engine VMs, GKE nodes, and on-premises systems (via Cloud Interconnect or VPN). No management of NFS servers, storage hardware, or patches is required.

---

## Service Tiers

| Tier | NFS Protocol | Capacity Range | Max IOPS | Throughput | Zones | Use Case |
|---|---|---|---|---|---|---|
| Basic HDD | NFS v3 | 1 TB – 63.9 TB | ~1,000 read / 1,000 write | ~100 MB/s | Single zone | Development, general file sharing, low-IOPS workloads |
| Basic SSD | NFS v3 | 2.5 TB – 63.9 TB | ~60,000 read / 60,000 write | ~1,200 MB/s | Single zone | Performance applications, small-medium shared storage |
| Zonal (formerly High Scale Zonal) | NFS v3 | 1 TB – 100 TB | Up to 660,000 read | Up to 16,000 MB/s | Single zone | High-scale analytics, genomics, media, HPC scratch |
| Enterprise | NFS v3, NFS v4.1 | 1 TB – 10 TB | Up to 120,000 read | Up to 4,096 MB/s | Multi-zone (HA) | Production HA, enterprise apps, home directories |

**Note**: Enterprise tier provides multi-zone redundancy with 99.99% availability SLA. All other tiers are single-zone with 99.9% SLA.

**Regional availability**: Filestore is available in most GCP regions but not all tiers in all regions. Check regional availability in the Cloud Console.

---

## Core Concepts

| Concept | Description |
|---|---|
| Instance | A Filestore managed NFS server. Each instance has one or more file shares accessible via a VPC IP address. |
| File share | An NFS export on the instance. Name is user-defined (e.g., `/vol1`, `/home`). Clients mount this share via `NFS_IP:/share_name`. |
| Snapshot | A point-in-time read-only copy of a file share's data. Stored within the instance (no separate storage pricing; counted toward instance capacity). |
| Backup | A copy of the instance's data stored independently (in Cloud Storage behind the scenes). Backups persist even if the instance is deleted. |
| Replication | Asynchronous cross-region replication for Enterprise tier instances. Creates a replica in another region for disaster recovery. |
| Access tier | Performance configuration of the instance (Basic HDD, Basic SSD, Zonal, Enterprise). Set at creation; can upgrade tier in some cases. |
| NFS mount | Standard Linux NFS mount command: `mount -t nfs -o rw,hard,intr,async INSTANCE_IP:/share_name /mnt/point` |

---

## Protocols

| Protocol | Supported Tiers | Key Features |
|---|---|---|
| NFS v3 | All tiers | Widely supported; stateless; performant for most workloads; requires firewall rule for port 2049 |
| NFS v4.1 | Enterprise only | Stateful; supports stronger consistency; better security (RPCSEC_GSS); Kerberos authentication support |

---

## Networking

- Filestore instances are associated with a VPC network and a specific zone (or multi-zone for Enterprise).
- Clients access the NFS share via a private RFC 1918 IP address assigned to the Filestore instance at creation.
- No external IP; access is always over the VPC.
- Firewall rule required: allow TCP/UDP port 2049 from client IP ranges to the Filestore instance IP.
- Access is controlled by IP-based NFS access rules (source IP ranges) configured on the file share, not GCP IAM.
- For GKE, use the [Filestore CSI driver](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/filestore-file-system) for dynamic provisioning.

### Shared VPC
Filestore instances can be deployed in a Shared VPC environment. The instance lives in the host project's VPC; compute resources in service projects access it over the shared network.

---

## NFS Mount Options

Recommended mount options for Linux clients:
```bash
# Standard mount
sudo mount -t nfs -o rw,hard,intr,timeo=600,retrans=3 \
  FILESTORE_IP:/share_name /mnt/filestore

# High-performance async mount (for throughput-heavy workloads)
sudo mount -t nfs -o rw,hard,async,noatime,nodiratime,timeo=600 \
  FILESTORE_IP:/share_name /mnt/filestore

# Add to /etc/fstab for persistent mount
FILESTORE_IP:/share_name  /mnt/filestore  nfs  defaults,hard  0  0
```

---

## Use Cases

| Use Case | Recommended Tier | Notes |
|---|---|---|
| Development/test shared filesystem | Basic HDD or Basic SSD | Cheapest; adequate for non-production |
| Home directories for Google Workspace or Linux users | Enterprise | HA required; NFS v4.1 for stronger consistency |
| CMS (WordPress, Drupal) shared content | Basic SSD | Multiple web servers sharing wp-content |
| Genomics pipelines (GATK, BWA, samtools) | Zonal (High Scale) | Very high throughput for genome processing |
| HPC cluster scratch filesystem (Slurm) | Zonal (High Scale) | Shared scratch for MPI jobs |
| Media rendering and VFX | Zonal (High Scale) | Multi-worker rendering farms |
| Lift-and-shift of on-premises NAS | Enterprise or Basic SSD | Depends on HA and performance needs |
| Machine learning training data | Zonal (High Scale) | High-throughput parallel reads from many VMs |

---

## vs Cloud Storage

| Attribute | Filestore | Cloud Storage |
|---|---|---|
| Access pattern | POSIX file system (read/write/seek/truncate) | Object storage (PUT/GET/DELETE entire objects) |
| Protocol | NFS v3 / v4.1 | HTTPS REST API / FUSE (gcsfuse) |
| Concurrency | Concurrent reads and writes via NFS | Concurrent reads; object-level write lock |
| Latency | Low (sub-millisecond within same zone) | Higher (REST API round trip) |
| Max file size | Limited by volume capacity | 5 TB per object |
| Use case | Applications expecting a filesystem (POSIX) | Web assets, data lake, backups, archives |
| Cost | Higher (dedicated capacity) | Lower (pay per actual storage used) |
| Global distribution | Regional / zonal only | Multi-region available |

---

## Important Patterns & Constraints

- **Capacity must be provisioned**: unlike Cloud Storage, you pay for provisioned capacity even if files don't fill it. Right-size the instance.
- **Tier is fixed at creation (mostly)**: you can upgrade from Basic HDD to Basic SSD, but you cannot downgrade. Switching to Enterprise or Zonal requires a new instance + data migration.
- **Single file share per instance (Basic HDD/SSD)**: Basic HDD and Basic SSD support only one file share per instance. Enterprise and Zonal support up to 10 shares.
- **IP-based access control**: Filestore uses NFS access rules based on IP ranges, not IAM. Restrict access by ensuring only known client IP ranges are allowed in the file share configuration.
- **Zone affinity**: for best performance, deploy Filestore instances in the same zone as compute clients (especially Basic tiers). Enterprise is multi-zone and connects to clients in any zone in the region.
- **Snapshot quota**: Basic instances have limited snapshot slots (1 scheduled + 5 manual). Enterprise has higher limits.
- **Backup is separate from snapshots**: snapshots are in-instance point-in-time copies; backups are durable, cross-instance copies that survive instance deletion. Use backups for DR.
- **GKE CSI driver**: for GKE, use the Filestore CSI driver with StorageClass type `filestore.csi.storage.gke.io`. Supports both `ReadWriteMany` (shared NFS) and `ReadWriteOnce` (dedicated per PVC).
- **Deletion is permanent**: deleting a Filestore instance deletes all data. Snapshots within the instance are also deleted. Backups stored independently survive.
- **Performance tuning**: for Zonal tier high-throughput workloads, use large file sizes, sequential I/O, and many parallel workers reading different files to maximize throughput.
