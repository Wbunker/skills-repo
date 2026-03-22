# Azure Storage Migration & Transfer — Capabilities Reference
For CLI commands, see [migration-transfer-cli.md](migration-transfer-cli.md).

## AzCopy

**Purpose**: Command-line utility for high-performance data transfer to and from Azure Blob Storage, Azure Files, and Amazon S3. Designed for automation, scripting, and bulk data movement.

### Key Capabilities

| Feature | Description |
|---|---|
| **Server-side copy** | Copy between Azure storage accounts without routing data through local machine; uses Put Block from URL |
| **Resumable transfers** | Jobs tracked in journal files; resume interrupted transfers with `azcopy jobs resume` |
| **Parallel processing** | Automatically parallelizes transfers; configurable via `--cap-mbps` and `AZCOPY_CONCURRENCY_VALUE` |
| **Sync** | Incremental sync; only transfers changed/missing files; supports `--delete-destination` |
| **Benchmark** | `azcopy bench` to test upload/download throughput to a storage account |
| **Glob patterns** | Include/exclude files using `--include-pattern` and `--exclude-pattern` |

### Authentication Modes

| Method | Command | Use Case |
|---|---|---|
| **Managed Identity** | `azcopy login --identity` | Azure VMs, AKS, App Service with system-assigned MI |
| **User-Assigned MI** | `azcopy login --identity --identity-client-id <id>` | User-assigned managed identity |
| **Service Principal** | `azcopy login --service-principal --application-id <id> --tenant-id <id>` | Automation pipelines |
| **Interactive (Entra ID)** | `azcopy login` | Dev/test; opens browser for OAuth flow |
| **SAS Token** | Append `?<sas>` to URL | Third-party access; no login required |
| **Account Key** | `AZCOPY_ACCOUNT_KEY` env var | Legacy; less secure |

### Common Transfer Patterns

```bash
# Local to Blob (upload)
azcopy copy './data/*.parquet' 'https://account.blob.core.windows.net/container/data/'

# Blob to local (download)
azcopy copy 'https://account.blob.core.windows.net/container/data/' './local/' --recursive

# Blob to Blob (server-side; no local bandwidth)
azcopy copy 'https://src.blob.core.windows.net/src-container?<sas>' \
  'https://dst.blob.core.windows.net/dst-container?<sas>' --recursive

# Sync directory to blob (incremental)
azcopy sync './local/' 'https://account.blob.core.windows.net/container/' \
  --recursive --delete-destination true

# S3 to Azure Blob (cross-cloud migration)
azcopy copy 'https://s3.amazonaws.com/my-bucket/' \
  'https://account.blob.core.windows.net/container/?<sas>' --recursive

# Set blob tier during copy
azcopy copy './archive/' 'https://account.blob.core.windows.net/container/' \
  --block-blob-tier Archive --recursive
```

---

## Azure Storage Explorer

**Purpose**: GUI application for Windows, macOS, and Linux. Manage Azure Blob, File, Queue, Table, and Cosmos DB storage visually. Supports SAS, account keys, Entra ID, and emulator connections.

### Key Features

| Feature | Description |
|---|---|
| **Cross-protocol browsing** | Navigate Blob containers, ADLS Gen2 file systems, Azure File shares, Tables, Queues |
| **Drag-and-drop upload/download** | Intuitive file operations; multipart upload handled automatically |
| **SAS generation** | Generate SAS tokens for containers and blobs directly in UI |
| **Snapshot management** | Browse, create, and restore blob and file share snapshots |
| **Soft delete recovery** | Browse and restore soft-deleted blobs and containers |
| **Access control editor** | Manage ADLS Gen2 ACLs visually |
| **AzCopy integration** | Large transfers use AzCopy engine behind the scenes |
| **Emulator support** | Connect to Azurite (local emulator) for development |

---

## Azure Data Box Family

**Purpose**: Physical appliance family for offline data transfer to Azure when network bandwidth or time makes online transfer impractical. Microsoft ships device to customer; customer loads data; device shipped back and uploaded to Azure.

### Device Comparison

| Device | Usable Capacity | Interface | Use Case | Transfer Speed |
|---|---|---|---|---|
| **Data Box Disk** | 35 TiB (up to 5 × 8 TiB SSDs) | USB 3.0 / SATA | Small datasets (<35 TiB); easy; no infrastructure | ~430 MiB/s per disk |
| **Data Box** | 80 TiB | 1/10 GbE, 25 GbE, 40 GbE NIC | Medium datasets (40–80 TiB) | Up to 1 Gbps |
| **Data Box Heavy** | 770 TiB | 40 GbE NIC × 2 | Large datasets (hundreds of TB); NAS migration | Up to 1 Gbps per port |

### Data Box Workflow

1. Order device via Azure Portal
2. Microsoft ships device (FIPS 140-2 compliant; hardware encryption)
3. Connect to on-premises network; copy data via SMB, NFS, REST, or Data Copy Service
4. Ship device back to Azure datacenter
5. Microsoft uploads data to designated storage account; device securely wiped

### Supported Transfer Destinations

- Azure Blob Storage (Block Blob, Page Blob)
- Azure Files (SMB)
- Azure Managed Disks (from VHD files)

### Data Box for Import vs Export

| Direction | Description |
|---|---|
| **Import** | On-premises → Azure (most common); seed initial dataset for migration or DR |
| **Export** | Azure → On-premises; retrieve archived data; regulatory compliance; cross-cloud migration |

---

## Azure Import/Export Service

**Purpose**: Ship your own drives (SATA HDD or SSD) to Azure datacenters for bulk data import to Blob Storage or Azure Files, or export from Blob Storage to drives. Use when Data Box appliances are unavailable or for specific compliance scenarios.

### Workflow

**Import (on-premises → Azure)**:
1. Prepare drives using `WAImportExport` tool (offline encryption, journal file, manifest)
2. Create import job in Azure Portal or CLI
3. Ship drives to Azure datacenter
4. Microsoft uploads data; marks job Complete
5. Return drives (optional)

**Export (Azure → on-premises)**:
1. Create export job specifying blobs to export
2. Ship blank drives to Azure datacenter
3. Microsoft copies blobs to drives
4. Drives shipped back

### Supported Scenarios

- Import to Blob Storage (Block Blob, Page Blob) and Azure Files
- Export from Blob Storage only
- Drives: 2.5" or 3.5" SATA II/III HDD; 2.5" SSD
- BitLocker encryption mandatory on all drives

---

## Azure File Sync for Migration

**Purpose**: Use Azure File Sync as a migration tool to move on-premises file server data to Azure Files with minimal downtime.

### Migration Pattern

1. **Install Azure File Sync agent** on source file server
2. **Create sync group** with cloud endpoint (Azure file share) and server endpoint (on-premises path)
3. **Initial sync**: all data replicates to Azure file share (can take days/weeks for large datasets)
4. **Enable cloud tiering** to free local space while keeping namespace accessible
5. **Cutover**: reconfigure clients to mount Azure file share directly (or via another server endpoint); remove old server endpoint
6. **Pre-seeding with Data Box**: use Data Box to seed Azure file share first; then connect Azure File Sync to sync only delta changes

### Benefits for Migration

- Zero downtime (sync runs continuously; cutover is fast)
- Can use multiple server endpoints for gradual migration
- Pre-seeding with Data Box dramatically reduces initial sync time for large shares

---

## Storage Migration Service (Windows Server)

**Purpose**: Windows Server feature (also available in Windows Admin Center) for migrating file servers to newer Windows Server versions or to Azure Files, with inventory, transfer, and cutover capabilities.

### Capabilities

| Feature | Description |
|---|---|
| **Inventory** | Discover shares, permissions, and data from source servers |
| **Data transfer** | Robocopy-based transfer; multiple passes to sync changes |
| **Cutover** | Transfer network identity (name, IP) from source to destination; transparent to clients |
| **Azure Files target** | Migrate directly to Azure Files share as destination |
| **Source support** | Windows Server, Samba (Linux), NetApp ONTAP, Dell EMC Isilon |

### Supported Migration Paths

- Windows Server 2003+ → Windows Server 2019/2022
- Windows Server → Azure VM running Windows Server
- NAS appliances (Samba, NetApp, EMC) → Windows Server or Azure Files

---

## Important Patterns & Constraints

- **AzCopy version**: Always use latest release; significant performance and feature improvements between versions
- **AzCopy log and plan files**: Stored in `%USERPROFILE%\.azcopy` (Windows) or `~/.azcopy` (Linux/macOS); clean up periodically
- **Data Box lead time**: Allow 5–7 business days for device delivery; plan accordingly for migration projects
- **Import/Export tool (WAImportExport)**: Only runs on Windows; 64-bit required; encrypt with BitLocker before generating journal
- **Data Box vs Import/Export**: Data Box is simpler (Microsoft-provided device, automatic encryption); Import/Export requires customer drives and BitLocker preparation
- **Azure File Sync bandwidth throttling**: Configure network limits to avoid saturating WAN links during initial sync
- **Cross-region AzCopy**: Egress charges apply when copying between regions; server-side copy still incurs egress from source region
- **AzCopy `--overwrite`**: Set to `ifSourceNewer` for safe incremental syncs that don't overwrite newer destination files
- **Storage Migration Service cutover**: Requires Windows Admin Center or PowerShell; not available via Azure CLI
