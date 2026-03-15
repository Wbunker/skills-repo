# AWS EBS — Capabilities Reference
For CLI commands, see [ebs-cli.md](ebs-cli.md).

## Amazon EBS

**Purpose**: Persistent block storage volumes for EC2 instances; behaves like a local hard drive; survives instance stop/terminate; supports snapshotting.

### Volume Types

| Volume Type | Category | Max Size | Max IOPS | Max Throughput | Use Case |
|---|---|---|---|---|---|
| **gp3** | SSD | 16 TiB | 16,000 | 1,000 MBps | General purpose; independently tune IOPS/throughput; default for most workloads |
| **gp2** | SSD | 16 TiB | 16,000 | 250 MBps | General purpose; IOPS scales with size (3 IOPS/GB); legacy |
| **io2 Block Express** | SSD | 64 TiB | 256,000 | 4,000 MBps | Mission-critical; highest performance; 99.999% durability |
| **io2 / io1** | SSD | 16 TiB | 64,000 | 1,000 MBps | I/O-intensive databases (Oracle, SQL Server, MySQL) |
| **st1** | HDD | 16 TiB | 500 | 500 MBps | Throughput-intensive; sequential workloads (data warehouses, ETL, log processing) |
| **sc1** | HDD | 16 TiB | 250 | 250 MBps | Coldest, lowest-cost HDD; infrequently accessed workloads |

**Notes**: HDD volumes (st1, sc1) cannot be used as boot volumes. gp3 allows independent IOPS/throughput tuning without increasing storage size.

### Key Concepts

| Concept | Description |
|---|---|
| **Volume** | Block-level storage device; attached to one EC2 instance at a time (except Multi-Attach) |
| **Snapshot** | Point-in-time backup stored in S3 (managed by EBS); incremental; can be copied across regions |
| **Fast Snapshot Restore (FSR)** | Pre-warms snapshot data so volumes restored from it achieve full performance immediately; charged per AZ per snapshot |
| **Snapshot Archive** | Lower-cost tier for snapshots retained ≥90 days; 75% cost reduction; 24–72 hour restore time |
| **Multi-Attach** | Attach a single io2/io1 volume to up to 16 EC2 instances in the same AZ; requires cluster-aware filesystem |
| **Elastic Volumes** | Dynamically modify volume size, type, and IOPS/throughput without detaching or stopping the instance |
| **Encryption** | AES-256; applies to data at rest, data in transit, snapshots; uses KMS key (AWS managed or CMK) |
| **Data Lifecycle Manager (DLM)** | Policy-based automation for creating, retaining, copying, and deleting EBS snapshots and AMIs |

### Key Features

| Feature | Description |
|---|---|
| **Durability** | io2 Block Express: 99.999% (0.001% AFR); all others: 99.8–99.9% (0.1–0.2% AFR) |
| **Recycle Bin** | Recover accidentally deleted snapshots and AMIs within a configurable retention window |
| **EBS Direct APIs** | Read/write snapshot blocks directly without creating a volume; useful for backup software |
| **Cross-region snapshot copy** | Copy snapshots to other regions for DR; encryption state and KMS key can be changed during copy |
| **AMI** | Amazon Machine Image baked from a snapshot; used to launch pre-configured EC2 instances |

### Important Patterns & Constraints

- Volumes must be in the same AZ as the EC2 instance they attach to
- To move a volume to another AZ/region, create a snapshot first, then restore in the target location
- gp3 baseline: 3,000 IOPS and 125 MBps included; additional IOPS/throughput charged separately
- io2/io1 charged per provisioned IOPS-month regardless of usage
- Snapshots are incremental; deleting intermediate snapshots does not lose data (reference counting)
- DLM policies support cross-region copy and cross-account sharing
