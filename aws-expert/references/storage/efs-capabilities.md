# AWS EFS — Capabilities Reference
For CLI commands, see [efs-cli.md](efs-cli.md).

## Amazon EFS

**Purpose**: Fully managed, scalable NFS file system for Linux workloads; shared access across multiple EC2 instances, ECS tasks, EKS pods, and Lambda functions simultaneously.

### Key Concepts

| Concept | Description |
|---|---|
| **File system** | The EFS resource; scales elastically to petabytes; Regional (multi-AZ) or One Zone |
| **Mount target** | Network endpoint in a VPC subnet; one per AZ; used by EC2/containers to mount via NFS |
| **Access point** | Application-specific entry point enforcing a specific POSIX user identity and root directory |
| **Replication** | Asynchronous replication to another EFS file system in same or different region |

### File System Types

| Type | Availability | Use Case |
|---|---|---|
| **Regional** | Multi-AZ (redundant across ≥2 AZs) | Production workloads; highest availability |
| **One Zone** | Single AZ | Cost savings; dev/test; data that can be recreated |

### Performance Modes

| Mode | Latency | Use Case |
|---|---|---|
| **General Purpose** | Lowest (sub-ms) | Web serving, CMS, home directories, general file serving; recommended default |
| **Max I/O** | Higher latency | Highly parallelized workloads; thousands of concurrent clients; big data |

### Throughput Modes

| Mode | Description |
|---|---|
| **Elastic** | Automatically scales up/down based on workload; recommended for spiky or unpredictable workloads; charged per GB transferred |
| **Provisioned** | Set a fixed throughput level (MBps) regardless of storage size; pay for provisioned amount |
| **Bursting** | Throughput scales with storage size; earns and spends burst credits; legacy option |

### Storage Classes

| Class | Description |
|---|---|
| **EFS Standard** | Frequently accessed data; multi-AZ |
| **EFS Standard-IA** | Infrequently accessed data; multi-AZ; per-GB retrieval fee |
| **EFS One Zone** | Frequently accessed; single AZ |
| **EFS One Zone-IA** | Infrequently accessed; single AZ; lowest cost |

### Key Features

| Feature | Description |
|---|---|
| **Lifecycle management** | Automatically move files to IA storage class after N days of no access (7/14/30/60/90 days); move back on first access |
| **Encryption** | At rest (KMS) and in transit (TLS) |
| **POSIX permissions** | Standard Unix file permissions; IAM authorization for NFS clients also supported |
| **Access points** | Enforce a POSIX user ID, group ID, and root directory path; simplify access for containerized apps |
| **Replication** | Continuous async replication; RPO typically minutes; supports cross-region and cross-account |

### Important Constraints

- Supports NFS v4.0 and v4.1; not supported on Windows EC2 instances
- Mount targets must be in the same VPC; cross-VPC access via VPC peering or Transit Gateway
