# Azure Blob Storage & ADLS Gen2 — Capabilities Reference
For CLI commands, see [blob-adls-cli.md](blob-adls-cli.md).

## Azure Blob Storage

**Purpose**: Massively scalable object storage for unstructured data — documents, images, videos, log files, backups, and big data analytics. Foundational layer for Azure Data Lake Storage Gen2 (ADLS Gen2) workloads.

### Storage Account Hierarchy

```
Storage Account → Container → Blob
```

| Level | Description |
|---|---|
| **Storage Account** | Top-level namespace; globally unique name (3–24 lowercase alphanumeric); sets redundancy, performance tier, and access protocols |
| **Container** | Logical grouping of blobs (like a bucket); access level: private, blob (anonymous blob read), or container (anonymous list + read) |
| **Blob** | Individual object; up to 190.7 TiB (block blob); identified by account + container + blob name |

### Blob Types

| Type | Max Size | Use Case |
|---|---|---|
| **Block Blob** | 190.7 TiB (50,000 blocks × 4,000 MiB) | General-purpose objects, files, images, log files, big data; most common type |
| **Append Blob** | 195 GiB | Append-only workloads: logging, audit trails, streaming data |
| **Page Blob** | 8 TiB | Random read/write; backing store for Azure VM OS and data disks (VHD format) |

### Storage Account Types

| Account Type | Supported Services | Performance | Use Case |
|---|---|---|---|
| **General Purpose v2 (GPv2)** | Blob, File, Queue, Table | Standard (HDD-backed) | Recommended default; supports all access tiers |
| **Blob Storage (legacy)** | Blob only | Standard | Legacy; migrate to GPv2 |
| **Premium Block Blob** | Block and Append Blobs only | Premium (SSD) | Low-latency blob workloads, IoT telemetry, AI/ML feature stores |
| **Premium Page Blob** | Page Blobs only | Premium (SSD) | Unmanaged disk scenarios (rare; prefer Managed Disks) |
| **Premium File Shares** | Azure Files only | Premium (SSD) | High-performance SMB/NFS file shares |

### Access Tiers

| Tier | Monthly Storage Cost | Retrieval Cost | Min Duration | Retrieval Latency | Use Case |
|---|---|---|---|---|---|
| **Hot** | Highest | Lowest | None | Milliseconds | Frequently accessed data |
| **Cool** | ~50% less than Hot | Low | 30 days | Milliseconds | Infrequently accessed (at least 30 days) |
| **Cold** | ~50% less than Cool | Medium | 90 days | Milliseconds | Rarely accessed (at least 90 days) |
| **Archive** | Lowest | Highest | 180 days | Hours (rehydration required) | Long-term archival, compliance, backup |

- **Tier scope**: Account-level default tier (Hot or Cool); individual blob-level override supported
- **Archive rehydration**: Must copy or change tier to Hot/Cool/Cold; Standard priority (up to 15 hours); High priority (<1 hour, higher cost)
- **Early deletion charges**: Deleting or changing tier of Cool/Cold/Archive blob before minimum duration incurs pro-rated penalty

### Redundancy Options

| Option | Description | Durability | RPO | RTO | Regions |
|---|---|---|---|---|---|
| **LRS** (Locally Redundant) | 3 copies in one datacenter | 11 nines | N/A | N/A | 1 |
| **ZRS** (Zone-Redundant) | 3 copies across 3 AZs in one region | 12 nines | Near-zero | Minutes | 1 |
| **GRS** (Geo-Redundant) | LRS + async replication to secondary region | 16 nines | <15 min RPO | Hours (Microsoft-initiated failover) | 2 |
| **GZRS** (Geo-Zone-Redundant) | ZRS + async replication to secondary region | 16 nines | <15 min RPO | Hours | 2 |
| **RA-GRS** | GRS + read access to secondary | 16 nines | <15 min RPO | Immediate read; hours for write failover | 2 |
| **RA-GZRS** | GZRS + read access to secondary | 16 nines | <15 min RPO | Immediate read; hours for write failover | 2 |

- Secondary region is auto-paired by Azure (e.g., East US → West US)
- Customer-initiated account failover promotes secondary to primary; use for DR scenarios
- ZRS and GZRS not available in all regions

### Lifecycle Management Policies

Rules applied at account level; evaluated daily; conditions and actions:

```json
{
  "rules": [
    {
      "name": "move-to-archive",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": { "blobTypes": ["blockBlob"], "prefixMatch": ["logs/"] },
        "actions": {
          "baseBlob": {
            "tierToCool": { "daysAfterModificationGreaterThan": 30 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 90 },
            "delete": { "daysAfterModificationGreaterThan": 365 }
          },
          "snapshot": { "delete": { "daysAfterCreationGreaterThan": 90 } }
        }
      }
    }
  ]
}
```

- Rules can match on blob type, prefix, blob index tags, and last access time (if tracking enabled)
- Actions: `tierToCool`, `tierToCold`, `tierToArchive`, `delete` for base blob, snapshots, and versions
- `enableLastAccessTimeTracking` must be enabled for last-access-based rules

---

## Azure Data Lake Storage Gen2 (ADLS Gen2)

**Purpose**: Enterprise-grade analytics storage combining Azure Blob Storage with a hierarchical namespace (HNS). Provides file-system semantics, POSIX-compliant ACLs, and native Hadoop compatibility for big data workloads.

### Enabling Hierarchical Namespace

- Enabled at storage account creation time; **cannot be changed after account creation**
- HNS converts flat blob namespace into a true directory tree
- Required for ADLS Gen2 operations (`az storage fs` commands)

### Key Features

| Feature | Description |
|---|---|
| **Hierarchical Namespace (HNS)** | True directory structure with atomic renames and deletes; O(1) directory operations vs O(n) in flat namespace |
| **POSIX ACLs** | Fine-grained access control at file and directory level; owner, group, and other; Entra ID identities |
| **Hadoop Compatibility** | ABFS driver (Azure Blob File System) integrates with HDInsight, Azure Databricks, Synapse Analytics, Apache Spark |
| **Delta Lake Support** | Optimized for Delta Lake and Apache Iceberg table formats; supports time travel and ACID transactions |
| **Multi-protocol Access** | Access same data via Blob REST API, ADLS Gen2 REST API, HDFS (via ABFS), SFTP, and NFS 3.0 |
| **Shared Access** | Same data accessible to batch (Databricks/Synapse) and streaming (Event Hubs Capture) simultaneously |

### ADLS Gen2 Access Control Model

- **RBAC**: Coarse-grained at storage account, container, or blob level; roles: Storage Blob Data Owner, Contributor, Reader
- **ACLs**: Fine-grained at file/directory level; evaluated after RBAC; POSIX-style access ACL + default ACL (inherited)
- **Superuser**: Storage Blob Data Owner has superuser privileges; can change ACLs of any file/directory
- **Umask**: Default ACL mask applied during object creation

---

## Security

### Authentication Methods

| Method | Description | Recommended For |
|---|---|---|
| **Azure AD + RBAC** | Entra ID identities (users, service principals, managed identities); built-in roles | Production workloads; preferred over Shared Key |
| **Shared Key (Account Key)** | Base64-encoded HMAC-SHA256; full access to account | Legacy; disable when possible via `AllowSharedKeyAccess=false` |
| **SAS Tokens** | Service SAS, Account SAS, User Delegation SAS; time-limited, scoped permissions | Temporary delegated access; User Delegation SAS preferred (backed by Entra ID) |
| **Anonymous Access** | Container or blob-level public access; disabled by default at account level | Public static web content only |

### Network Security

| Feature | Description |
|---|---|
| **Firewall rules** | Restrict access to specific IP ranges and Azure Virtual Networks via service endpoints |
| **Private Endpoints** | Bring storage account into VNet via private IP; recommended for data exfiltration prevention |
| **Trusted Services** | Allow Azure services (Backup, HDInsight, etc.) to bypass firewall |
| **Defender for Storage** | Anomaly detection, malware scanning (on upload), sensitive data threat detection |

### Data Protection

| Feature | Description |
|---|---|
| **Encryption at rest** | AES-256 by default (platform-managed keys); customer-managed keys (CMK) via Azure Key Vault |
| **Encryption in transit** | HTTPS enforced (`EnableHttpsTrafficOnly=true`); TLS 1.2 minimum recommended |
| **Infrastructure encryption** | Double encryption: service-level + infrastructure-level for highly sensitive data |

---

## Performance & Advanced Features

### Blob Index Tags

- Up to 10 key-value tags per blob; indexed for fast filtering across containers
- Query with `az storage blob list --include=t` or Find Blobs by Tags API
- Use for multi-dimensional object categorization without full scan

### Blob Versioning

- Automatically maintains prior versions of a blob on modification or deletion
- Access previous version via version ID
- Lifecycle rules can expire non-current versions

### Soft Delete

- **Blob soft delete**: Retain deleted blobs for 1–365 days; restore with `az storage blob undelete`
- **Container soft delete**: Retain deleted containers; restore entire container
- **File share soft delete**: Retain deleted file shares (separate feature in Azure Files)

### Change Feed

- Ordered, durable, immutable log of all change events (create, modify, delete) to blobs and blob properties
- Stored as Apache Avro files in `$blobchangefeed` container
- Use cases: audit, CDC (Change Data Capture), replication pipelines, archival

### Object Replication

- Asynchronous replication of block blobs between storage accounts (same or different region, same or different subscription)
- Requires versioning enabled on source and destination
- Filter by container prefix; RPO depends on blob size and change rate (no guaranteed SLA)

### Static Website Hosting

- Serves content from `$web` container; custom index and error document
- Integrate with Azure CDN (now Azure Front Door / CDN) for global delivery and custom domains with HTTPS

### SFTP Support

- Native SFTP access to blob storage (HNS required)
- Local users with password or SSH key authentication; mapped to specific containers
- Use for legacy SFTP-based data ingestion pipelines

### NFS 3.0 Protocol Support

- Expose blob storage as NFS mount (HNS required; Premium Block Blob account for production)
- Supports read/write; no locking (stateless NFS)
- Use for Linux HPC workloads needing POSIX-like access to blob data

### Immutability Policies (WORM)

| Policy Type | Description |
|---|---|
| **Time-based retention** | Lock blobs for defined period; no delete or overwrite; supports regulatory compliance (SEC 17a-4, FINRA) |
| **Legal hold** | Indefinite retention until explicitly cleared; no time limit |
| **Immutability at version level** | Apply to individual blob versions; more granular than container-level |

- Policies can be set at container or blob version level
- Container-level locked policies **cannot be removed or shortened**

### Batch Operations

- `az storage blob batch` for bulk download, upload, delete with glob-like filters
- Blob Batch REST API for server-side bulk delete/set-tier on millions of objects in a single request

---

## Important Patterns & Constraints

- Storage account name must be globally unique, 3–24 lowercase alphanumeric characters
- Maximum 250 storage accounts per region per subscription (soft limit; raiseable)
- Blob name (including path) up to 1,024 characters; avoid trailing dots and slashes
- HNS cannot be enabled or disabled after account creation — plan upfront
- Archive blobs cannot be read directly; must rehydrate to Hot/Cool/Cold first
- LRS and ZRS data remains in primary region; only GRS/GZRS variants replicate cross-region
- Changing redundancy (e.g., LRS → GRS) is live with no data loss but may take hours to complete
- Shared Key access should be disabled for ADLS Gen2 security best practice; use Entra ID + ACLs
