# Persistent Disk and Hyperdisk — Capabilities Reference

CLI reference: [persistent-disk-cli.md](persistent-disk-cli.md)

## Purpose

High-performance block storage for Compute Engine VMs and GKE nodes. Persistent Disk (PD) and Hyperdisk provide durable, network-attached storage that is independent of VM lifetime. Disks survive VM deletion, can be re-attached, and are automatically replicated within a zone for durability. Hyperdisk is the newer generation that allows independently provisioning capacity, IOPS, and throughput.

---

## Disk Types

| Disk Type | Media | Max Size | Max IOPS | Max Throughput | Key Characteristic |
|---|---|---|---|---|---|
| pd-standard | HDD | 64 TB | 3,000 read / 3,000 write (size-dependent) | 180 MB/s read / 180 MB/s write | Lowest cost; best for sequential, throughput-oriented workloads |
| pd-balanced | SSD | 64 TB | 80,000 read / 80,000 write | 1,200 MB/s read / 400 MB/s write | Best balance of price and performance; default recommendation |
| pd-ssd | SSD | 64 TB | 100,000 read / 100,000 write | 1,200 MB/s read / 400 MB/s write | Higher performance than pd-balanced; latency-sensitive databases |
| pd-extreme | SSD | 64 TB | 350,000 (provisioned) | 7,500 MB/s (provisioned) | Highest PD performance; manually provision IOPS/throughput |
| Hyperdisk Balanced | SSD | 64 TB | 160,000 (provisioned) | 2,400 MB/s (provisioned) | Decouple IOPS/throughput from size; pay for what you provision |
| Hyperdisk Extreme | SSD | 64 TB | 350,000 (provisioned) | 10,000 MB/s (provisioned) | Maximum throughput Hyperdisk; SAP HANA, Oracle DB |
| Hyperdisk Throughput | HDD-equiv | 2 PB per instance | Lower IOPS | 2,400 MB/s (provisioned) | Streaming, throughput-heavy workloads at lower cost than SSD |
| Hyperdisk ML | SSD | 64 TB | 1,200,000 read (provisioned) | 24,000 MB/s read | Read-intensive ML model loading; can be attached to 2,500 VMs simultaneously |
| Local SSD | NVMe | 375 GB per disk (up to 24 disks = 9 TB) | ~680,000 read / 360,000 write per disk | ~2,400 MB/s per disk | Highest I/O; ephemeral (data lost on stop/delete); physically attached to host |

**Performance notes**:
- For Standard/Balanced/SSD PD, actual IOPS and throughput scale with disk size and VM vCPU count.
- Hyperdisk allows provisioning IOPS and throughput independently of size (within limits).
- Local SSD performance does not depend on disk size — it is fixed per disk (NVMe).

---

## Core Concepts

| Concept | Description |
|---|---|
| Disk | A named persistent block device. Zonal disks exist in one zone; regional disks replicate across two zones. |
| Snapshot | A point-in-time copy of a persistent disk. Incremental after the first full snapshot. Stored in Cloud Storage. Zone-independent. |
| Image | A bootable disk image (OS + software). Can be created from a disk or snapshot. Used to create VM boot disks. |
| Snapshot schedule | A resource policy that automates snapshot creation on a cron-like schedule. Attaches to a disk. |
| Multi-writer mode | Allows a PD to be attached to multiple VMs simultaneously in read-write mode. Only supported for `pd-ssd` disks up to 10 TB. Applications must handle concurrent writes (e.g., DRBD, Lustre). |
| Disk encryption | All PD disks are encrypted at rest. Options: Google-managed keys (default), CMEK (Cloud KMS key you manage), CSEK (customer-supplied encryption key). |
| Zonal PD | Single-zone disk. If the zone goes down, the disk is unavailable (but data is not lost). |
| Regional PD | Disk synchronously replicated across two zones in a region. Higher cost; used for HA configurations. |

---

## Regional Persistent Disk

Regional PD maintains synchronous replicas in two zones within a region. Used for high-availability stateful workloads:
- Active/passive database HA (e.g., MySQL primary + replica failover)
- StatefulSet HA in GKE with pod failure in one zone
- Any workload needing fast failover without data re-sync

**Failover process**: when the primary zone goes down, force-attach the regional disk to a VM in the secondary zone using `--force-attach` (marks the primary zone replica as unavailable, continues with secondary). This is a manual or automated (via health check + script) operation — not fully automatic.

**Replication lag**: synchronous replication; writes must commit in both zones before returning success. Slight write latency increase compared to zonal PD.

---

## Snapshots

### Snapshot Behavior
- **First snapshot**: full copy of the disk stored in Cloud Storage.
- **Subsequent snapshots**: incremental — only changed blocks since the last snapshot are copied. Storage cost reflects incremental deltas.
- **Snapshot storage location**: choose multi-region (`us`, `eu`, `asia`) or specific region (`us-central1`). Multi-region snapshots can be used to create disks in any zone in that continent.
- **Snapshot consistency**: for best consistency, pause application writes or unmount the filesystem before snapshotting. GCE also supports crash-consistent snapshots (application not frozen) which is acceptable for most filesystems that support fsck.

### Snapshot Schedules (Resource Policies)
Create automatic snapshot schedules attached to disks:
- Frequency: hourly, daily, or weekly
- Start time: UTC hour/minute
- Retention: max number of snapshots to keep (older ones deleted automatically)
- On-source-disk-delete: keep or delete associated snapshots

---

## Performance Characteristics

### pd-standard (HDD)
- Throughput scales with disk size: 0.09 MB/s read per GB provisioned (min 0.36 MB/s, max 180 MB/s)
- IOPS: 0.75 IOPS/GB (min 1, max 3,000)
- Suitable for: batch processing, sequential reads/writes, logs, low-cost bulk storage

### pd-balanced (SSD)
- IOPS: 6 IOPS/GB (min 1, max 80,000)
- Throughput: 0.28 MB/s/GB read (max 1,200 MB/s), 0.28 MB/s/GB write (max 400 MB/s)
- Suitable for: most application workloads, boot disks, web servers, small-medium databases

### pd-ssd (SSD)
- IOPS: 30 IOPS/GB (min 1, max 100,000)
- Throughput: same as pd-balanced at max
- Higher IOPS-per-GB ratio makes it more cost-efficient for IOPS-intensive databases at smaller sizes

### pd-extreme (SSD)
- Manually provisioned IOPS (up to 350,000) and throughput (up to 7,500 MB/s)
- Requires N2, N2D, C2, C2D, or newer machine family
- Use for highest-performance databases requiring consistent low latency

### Hyperdisk Balanced
- Decouple performance from capacity: provision 1 to 160,000 IOPS, 1 to 2,400 MB/s throughput, and capacity independently
- Requires C3, N2, or newer machine families
- Can change provisioned IOPS/throughput after disk creation (without detaching)

### Hyperdisk ML
- Up to 1,200,000 read IOPS and 24,000 MB/s read throughput
- Can be attached to up to 2,500 VMs in read-only mode simultaneously
- Purpose-built for serving large ML models (e.g., loading LLM weights across many inference VMs)

---

## When to Use Each Disk Type

| Scenario | Recommended Disk |
|---|---|
| Boot disk for a general-purpose VM | pd-balanced |
| Development or test VMs, low-budget | pd-standard |
| MySQL/PostgreSQL production database | pd-ssd or Hyperdisk Balanced |
| SAP HANA or Oracle on bare metal/VMs | Hyperdisk Extreme or pd-extreme |
| ML model serving (read-heavy, many VMs) | Hyperdisk ML |
| Kafka, Elasticsearch, Cassandra | pd-ssd or Hyperdisk Balanced |
| High-IOPS with variable performance needs | Hyperdisk Balanced (tune without resize) |
| HPC scratch space (ephemeral) | Local SSD |
| Large streaming/analytics data store | pd-standard or Hyperdisk Throughput |
| HA failover (requires zone redundancy) | Regional pd-ssd or Regional Hyperdisk Balanced |

---

## Important Patterns & Constraints

- **Disks cannot be shrunk**: you can only increase disk size, never decrease. Plan capacity with room to grow.
- **Online resize requires filesystem expansion**: after `gcloud compute disks resize`, run OS-level commands (`resize2fs`, `xfs_growfs`) to expand the filesystem to use the new space.
- **Boot disk auto-delete**: by default, the boot disk is deleted when the VM is deleted (`--auto-delete=true`). For data persistence, attach separate data disks with `--auto-delete=no`.
- **Local SSD is ephemeral**: data on Local SSD is lost when the VM stops, is deleted, or is live-migrated. Use Local SSD only for scratch/cache that can be rebuilt.
- **Multi-writer mode limitations**: only pd-ssd ≤ 10 TB; application must handle concurrent writes correctly. Not compatible with most filesystems (use cluster filesystems like OCFS2 or raw block access).
- **Snapshot source disk can stay online**: snapshots are crash-consistent by default and can be taken from a running disk. For databases, use application-consistent snapshots (quiesce writes first).
- **Regional disk failover is manual**: you must run `gcloud compute instances attach-disk --force-attach` to fail over to the secondary zone.
- **Hyperdisk requires newer machine families**: not compatible with N1, E2, or older machine series.
- **CMEK key deletion risks**: if you delete the CMEK key used to encrypt a disk, the disk data is permanently unrecoverable. Use key destruction with a delay (default 30-day scheduled deletion).
- **Snapshot schedules are resource policies**: they can be shared across multiple disks and must be in the same region as the disk.
- **Disk IOPS and VM IOPS limits**: the VM itself has a maximum IOPS limit that may be lower than the disk's limit. Always check both disk specs and VM specs for the bottleneck.
