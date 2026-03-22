# Data Transfer — Capabilities Reference
For CLI commands, see [data-transfer-cli.md](data-transfer-cli.md).

## Azure Data Box Family

**Purpose**: Physical device-based offline data transfer for moving large datasets to Azure when network transfer is impractical (limited bandwidth, time constraints, cost).

### Device Options

| Device | Usable Capacity | Form Factor | Use Case |
|---|---|---|---|
| **Data Box Disk** | 35 TB (up to 5 x 8 TB SSDs) | 2.5" SSD disks | Small/medium datasets; easy shipping |
| **Data Box** | 80 TB | Rugged suitcase appliance | Standard large transfers |
| **Data Box Heavy** | 770 TB | Large pallet-mounted device | Massive transfers; datacenter-scale |

### Data Box Process

1. **Order** device from Azure Portal (under Migrate section)
2. **Receive** device; connect to on-premises network
3. **Copy** data to device (NFS or SMB share; up to 625 MB/s for Heavy)
4. **Ship** device back to Microsoft (pre-paid label included)
5. **Upload**: Microsoft staff uploads data to Azure Blob Storage or Azure Files
6. **Verify** checksums; Microsoft sends completion confirmation
7. **Erase** device using NIST 800-88 standards after upload

### Security

- 256-bit AES hardware encryption on all devices
- Device unlocked only with customer-controlled passphrase from portal
- Erasure after upload; certificate of erasure provided
- Chain of custody tracking

---

## Azure Import/Export Service

**Purpose**: Ship your own hard drives (2.5"/3.5" SATA II/III) to an Azure datacenter for bulk import or export. Lower cost than Data Box but requires customer-supplied hardware and `WAImportExport.exe` tool preparation.

### Use Cases

- **Import**: Copy data from your drives to Azure Blob or Azure Files
- **Export**: Copy data FROM Azure Blob to your drives shipped to you

### Process

- Prepare drives with WAImportExport.exe (creates journal files, encrypts with BitLocker)
- Create Import/Export job in Azure Portal with drive details and BitLocker keys
- Ship drives to Azure datacenter
- Microsoft copies data and returns drives

---

## AzCopy

**Purpose**: High-performance command-line utility for copying data to/from Azure Storage (Blob, Files, ADLS Gen2). Optimized for parallelism, incremental sync, and large-scale transfers.

### Key Features

| Feature | Details |
|---|---|
| **Parallel transfers** | Concurrent uploads/downloads; configurable concurrency (`--cap-mbps`, `--block-size-mb`) |
| **Server-side copy** | Copy between storage accounts without routing through client machine |
| **Incremental sync** | `azcopy sync` — copies only new/changed files |
| **Checkpoint/resume** | Automatically resumes interrupted transfers from checkpoint |
| **SAS or OAuth auth** | Use SAS tokens or Azure AD (`azcopy login`) for auth |
| **Managed identity** | `azcopy login --identity` for managed identity auth from Azure resources |
| **Blob tiers** | Set access tier on upload (`--blob-type BlockBlob --block-blob-tier Archive`) |
| **Include/exclude filters** | `--include-pattern "*.csv"`, `--exclude-path`, `--include-after <date>` |
| **Logging** | `--log-level INFO/WARNING/ERROR/NONE`; per-job log files |
| **Benchmarking** | `azcopy benchmark` to test storage throughput |

### Performance Tips

- Use `--cap-mbps` to avoid saturating network for production systems
- Increase concurrency: `AZCOPY_CONCURRENCY_VALUE=512` environment variable
- Use `--block-size-mb 256` for large files (reduces number of PUT block calls)
- For ADLS Gen2: use `https://account.dfs.core.windows.net` endpoint (not blob)

---

## Azure Storage Migration Service

**Purpose**: Windows Server-based service for migrating file server data (SMB shares) to Azure Files or Windows file servers on Azure VMs. Orchestrated from Windows Admin Center.

### Capabilities

- Inventory source file servers (Windows and Linux Samba servers)
- Transfer files, folders, permissions (ACLs), and shares
- Incremental transfers (sync changed files without full re-copy)
- Cutover: map source shares to destination; clients reconnect automatically
- **Targets**: Azure Files SMB shares, Windows file servers on Azure VMs, Azure Stack HCI file servers

### Components

| Component | Role |
|---|---|
| **Orchestrator** | Windows Server running Windows Admin Center; manages migration jobs |
| **Source proxy** | Lightweight service on source server; Windows and Linux (Samba) supported |
| **Destination proxy** | Service on destination server or Azure VM |

---

## Azure File Sync (Migration Use Case)

**Purpose**: Sync on-premises Windows file server to Azure Files in the cloud, then cut over after sync. Enables phased migration with zero downtime.

### Phased Migration Pattern

```
1. Deploy Azure File Sync agent on source file server
2. Configure sync group: on-premises endpoint → Azure Files endpoint
3. Initial sync: all files replicated to Azure Files (may take days/weeks for large datasets)
4. Ongoing sync: changed files sync continuously (RPO: ~minutes)
5. Cutover: point clients to Azure Files SMB share (or Azure File Sync-connected server at new site)
6. Decommission source server
```

### Cloud Tiering

- Moves infrequently accessed files from on-premises to Azure Files cloud
- Only "stub" (pointer) remains on disk; file retrieved on access
- Frees local disk space while keeping namespace accessible
- Useful during migration to reduce on-premises storage requirements before cutover

---

## Azure Data Factory (Cloud-to-Cloud Transfers)

**Purpose**: ETL/ELT service for cloud-to-cloud data movement between Azure services and 90+ data sources.

### Migration Scenarios

| Source → Target | Notes |
|---|---|
| Amazon S3 → Azure Blob | Parallel partitioned copy; hundreds of TB in hours |
| Google Cloud Storage → Azure Blob | Copy activity with GCS connector |
| On-prem SQL → Azure Synapse | Copy with Self-Hosted Integration Runtime |
| Azure Blob → Azure Data Lake | Copy activity; supports hierarchical namespace |
| Blob → Cosmos DB | Schema mapping with Data Flow transformations |

### Self-Hosted Integration Runtime (SHIR)

- Runs on-premises or on a VM in your network
- Enables ADF to access on-premises data sources without VPN (outbound HTTPS only)
- HA configuration: multiple SHIR nodes for redundancy
- Required for: on-premises SQL Server, Oracle, file systems, SAP

---

## Azure Storage Mover

**Purpose**: Managed migration service for moving file-based data from on-premises (NFS, SMB) to Azure Blob storage or Azure Files. Replaces manual AzCopy scripting for large structured migrations.

### Key Concepts

| Concept | Description |
|---|---|
| **Storage mover** | Top-level resource; houses agents, endpoints, and migration jobs |
| **Agent** | VM (Azure or on-prem) running migration agent software; connects to mover |
| **Source endpoint** | NFS share or SMB share to migrate from |
| **Target endpoint** | Azure Storage container or Azure Files share |
| **Project** | Organizes job definitions and runs |
| **Job definition** | Mapping of source to target with copy settings |
| **Job run** | Execution of a job definition; tracks progress and errors |
