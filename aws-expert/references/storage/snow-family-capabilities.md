# AWS Snow Family — Capabilities Reference

For CLI commands, see [snow-family-cli.md](snow-family-cli.md).

## AWS Snow Family

**Purpose**: Physical edge computing and data transfer devices for moving large amounts of data to/from AWS when network transfer is impractical (bandwidth-limited, time-constrained, disconnected environments).

### Device Comparison

| Device | Storage | Compute | Use Case |
|---|---|---|---|
| **Snowcone** | 8 TB HDD or 14 TB SSD | 2 vCPU, 4 GB RAM | Smallest; highly portable; edge computing in rugged/space-constrained environments; DataSync-compatible |
| **Snowball Edge Storage Optimized** | 80 TB usable (210 TB raw) | 40 vCPU, 80 GB RAM | Large-scale data migration; local storage; moderate compute |
| **Snowball Edge Compute Optimized** | 28 TB NVMe SSD | 52 vCPU, 208 GB RAM; optional GPU | High-performance edge compute: ML inference, video analysis, autonomous vehicles |
| **Snowmobile** | Up to 100 PB | N/A | Exabyte-scale migration; 45-foot shipping container; AWS-managed transport |

### Key Concepts

| Concept | Description |
|---|---|
| **Job** | An order for a Snow device; Import Job (ship data to AWS), Export Job (ship data from AWS), or Local Compute and Storage |
| **OpsHub** | GUI application for managing Snow devices locally |
| **S3 adapter** | S3-compatible API on Snow devices for local S3-style access |
| **EC2 AMIs** | Run EC2-compatible instances locally on Snowball Edge/Snowcone |

### Key Features

| Feature | Description |
|---|---|
| **Edge compute** | Run Lambda functions, EC2 instances, or ECS tasks locally on the device |
| **Encryption** | All data encrypted at rest (256-bit); keys managed by KMS; tamper-evident enclosure |
| **Clustering** | Cluster Snowball Edge devices (5–10) for higher aggregate storage/compute |
| **DataSync agent** | Snowcone ships with DataSync agent pre-installed for online transfer after local collection |

### When to Choose Snow vs DataSync

| Scenario | Recommendation |
|---|---|
| >10 TB, slow/costly network, time-sensitive | Snow Family |
| Ongoing, repeated transfer with adequate bandwidth | DataSync |
| Edge compute in disconnected environment | Snow Family |
| Data center migration to AWS | Snowball Edge or Snowmobile |

## AWS Snow Family

**Purpose**: Physical edge computing and data transfer devices for moving large amounts of data to/from AWS when network transfer is impractical (bandwidth-limited, time-constrained, disconnected environments).

### Device Comparison

| Device | Storage | Compute | Use Case |
|---|---|---|---|
| **Snowcone** | 8 TB HDD or 14 TB SSD | 2 vCPU, 4 GB RAM | Smallest; highly portable; edge computing in rugged/space-constrained environments; DataSync-compatible |
| **Snowball Edge Storage Optimized** | 80 TB usable (210 TB raw) | 40 vCPU, 80 GB RAM | Large-scale data migration; local storage; moderate compute |
| **Snowball Edge Compute Optimized** | 28 TB NVMe SSD | 52 vCPU, 208 GB RAM; optional GPU | High-performance edge compute: ML inference, video analysis, autonomous vehicles |
| **Snowmobile** | Up to 100 PB | N/A | Exabyte-scale migration; 45-foot shipping container; AWS-managed transport |

### Key Concepts

| Concept | Description |
|---|---|
| **Job** | An order for a Snow device; Import Job (ship data to AWS), Export Job (ship data from AWS), or Local Compute and Storage |
| **OpsHub** | GUI application for managing Snow devices locally |
| **S3 adapter** | S3-compatible API on Snow devices for local S3-style access |
| **EC2 AMIs** | Run EC2-compatible instances locally on Snowball Edge/Snowcone |

### Key Features

| Feature | Description |
|---|---|
| **Edge compute** | Run Lambda functions, EC2 instances, or ECS tasks locally on the device |
| **Encryption** | All data encrypted at rest (256-bit); keys managed by KMS; tamper-evident enclosure |
| **Clustering** | Cluster Snowball Edge devices (5–10) for higher aggregate storage/compute |
| **DataSync agent** | Snowcone ships with DataSync agent pre-installed for online transfer after local collection |

### When to Choose Snow vs DataSync

| Scenario | Recommendation |
|---|---|
| >10 TB, slow/costly network, time-sensitive | Snow Family |
| Ongoing, repeated transfer with adequate bandwidth | DataSync |
| Edge compute in disconnected environment | Snow Family |
| Data center migration to AWS | Snowball Edge or Snowmobile |
