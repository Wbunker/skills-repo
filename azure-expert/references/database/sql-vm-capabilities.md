# SQL Server on Azure VMs — Capabilities Reference
For CLI commands, see [sql-vm-cli.md](sql-vm-cli.md).

## SQL Server on Azure VMs (IaaS)

**Purpose**: Run SQL Server inside an Azure Virtual Machine with full OS and SQL Server instance access. Use when you need features unavailable in SQL Managed Instance (specific SQL Server versions, third-party agents, full Windows features) or require a specific OS configuration.

### SQL IaaS Agent Extension

The SQL IaaS Agent Extension registers the VM with the SQL VM resource provider and unlocks Azure-managed benefits:

| Feature | Description |
|---|---|
| **Automated backup** | Integration with Azure Backup for scheduled backups to Azure Storage; VSS-consistent; configurable retention |
| **Automated patching** | Schedule Windows and SQL Server patching maintenance window; reduces unplanned downtime |
| **Entra ID authentication** | Enable Azure AD / Entra ID logins for SQL Server (requires Entra Domain Services or Entra ID-joined machine) |
| **Azure Key Vault integration** | Automatic credential management for SQL Server features using AKV (TDE, Always Encrypted, column encryption) |
| **Flexible licensing** | Switch between PAYG and BYOL (Azure Hybrid Benefit) without redeployment |
| **Storage configuration** | Optimize disk layout (data, log, tempdb on separate Premium SSDs) from Azure Portal |
| **SQL Assessment** | Analyze configuration against SQL Server best practices |
| **Defender for SQL** | Microsoft Defender for SQL on VMs via the extension |

Registration modes:
- **Lightweight**: minimal footprint; only SQL Server version detection; no agent process
- **Full**: all features above; runs SQL IaaS Agent service; recommended for most VMs
- **NoAgent**: for SQL Server 2008/2008 R2; no management features available

---

## Licensing Models

### Pay-As-You-Go (PAYG)

- SQL Server license included in VM hourly cost
- No upfront commitment; flexible for short-term or variable workloads
- Choose Enterprise, Standard, or Web edition in marketplace image

### Azure Hybrid Benefit (BYOL)

- Apply existing SQL Server Software Assurance licenses to Azure VMs
- Reduces cost by ~55% compared to PAYG for Enterprise edition
- License cores: SQL Server Core licenses → Azure VM vCores (1:1 mapping; minimum 4 cores)
- Enable/switch via SQL IaaS extension or VM settings; no redeployment required

### SQL Server Editions on Azure

| Edition | Description | Max vCores/Memory |
|---|---|---|
| **Enterprise** | Full feature set; unlimited virtualization rights (on dedicated hosts) | Unlimited |
| **Standard** | Most features; limited to 4 sockets or 24 cores per instance | 4 sockets / 24 cores |
| **Developer** | Free; full Enterprise features; **not licensed for production** | Unlimited |
| **Express** | Free; limited to 10 GB database size; 1 socket or 4 cores | 1 socket / 4 cores |
| **Web** | Lower cost; web-facing workloads; cannot use AHB | 4 sockets / 16 cores |

---

## High Availability and Disaster Recovery (HADR)

### Always On Availability Groups (AG)

| Feature | Description |
|---|---|
| **AG listener** | Virtual network name (VNN) or distributed network name (DNN); single connection endpoint regardless of primary |
| **Synchronous commit** | Zero data loss; used for same-region replicas; adds latency |
| **Asynchronous commit** | Cross-region replicas; data loss risk (RPO = replication lag); used for DR |
| **Readable secondaries** | Route read workloads to secondary replicas; offload reporting |
| **Automatic failover** | Requires synchronous commit + Windows Server Failover Cluster (WSFC) |
| **Manual failover** | For async replicas; used after disaster |
| **Distributed AG** | Span two independent AGs across different WSFC clusters or regions |

#### AG Setup on Azure

- Requires Windows Server Failover Cluster (WSFC) — domain-joined VMs
- **Azure internal load balancer (ILB)**: required for AG listener in Azure (VMs in same VNet)
- **DNN listener** (preferred): no load balancer needed; resolves directly to primary; lower latency; requires SQL Server 2019 CU8+ or 2022
- Place VMs in **Availability Set** (same fault/update domain) or **Availability Zone** (different AZ; zone-redundant HA)

### Failover Cluster Instances (FCI)

| Storage Option | Description |
|---|---|
| **Azure Shared Disks** | Premium SSD or Ultra Disk with `maxShares > 1`; simplest shared storage; no extra licenses |
| **Storage Spaces Direct (S2D)** | Pool local NVMe disks across nodes; higher performance; Windows Server Datacenter license required |
| **Azure NetApp Files (ANF)** | Enterprise NFS/SMB shared storage; low latency; SAP HANA FCI supported |
| **Premium File Share** | Azure Files Premium SMB; simple; lower IOPS than dedicated disks |

- FCI provides instance-level HA (SQL Server instance fails over, not individual databases)
- WSFC required; minimum 2 nodes; both nodes access same shared storage
- FCI + AG (layered): FCI at bottom for storage HA, AG on top for geo-replication

### Log Shipping

- Oldest HA/DR method; transaction log backups copied to secondary and restored
- Simple; no cluster required; readable secondary (STANDBY mode) possible
- Higher RPO (frequency of log backup) and RTO (restore time) compared to AG

---

## VM Sizes for SQL Server

### Memory-Optimized (Recommended for Production Databases)

| Series | Description | Use Case |
|---|---|---|
| **M-series** | Up to 12 TB RAM; 416+ vCores; highest memory | SAP HANA on SQL Server, in-memory OLTP, data warehouse |
| **E-series (Ebs_v5, Eds_v5)** | High memory-to-vCore ratio; local NVMe options | Most SQL Server production workloads |
| **Standard_E16bds_v5** | 16 vCores, 128 GiB RAM, local NVMe | Excellent SQL Server price/performance |

### General Purpose

| Series | Description |
|---|---|
| **D-series (Dds_v5, Dbs_v5)** | Balanced compute/memory; local NVMe | Dev/test, smaller production |
| **B-series** | Burstable; credit-based CPU | Dev/test only |

### Disk Recommendations for SQL Server

| Disk | Purpose | Recommendation |
|---|---|---|
| **Data files (.mdf, .ndf)** | Application data | Premium SSD P30+; ReadOnly caching |
| **Transaction log (.ldf)** | Sequential writes; low latency critical | Premium SSD; **No caching** (None) |
| **TempDB** | Temporary data; high I/O | **Local NVMe temp disk** (`/dev/nvme0n1` on Ev5); or Premium SSD with None caching |
| **Backup** | Backup files | Standard SSD or Blob Storage via AzCopy |

- Stripe multiple Premium SSDs using Windows Storage Spaces for higher IOPS/throughput
- RAID 0 (striped): no redundancy but maximum performance (protect via Azure managed disk redundancy + SQL backups)
- Separate data, log, and tempdb disks for optimal I/O patterns

---

## SQL Server Configuration Best Practices

### Memory

- Set **max server memory** to leave ~10% (or 4 GB minimum) for OS
- E.g., 64 GB VM → set max server memory = 57,344 MB

### Processor

- **Max Degree of Parallelism (MAXDOP)**: set to number of physical cores per NUMA node (use SQL Server MAXDOP recommendation)
- **Cost Threshold for Parallelism**: raise from default 5 to 50+ for OLTP workloads

### Networking

- Enable **Jumbo Frames** (9000 MTU) for AG synchronous replication traffic
- Place AG replicas in same VNet (or peered VNet); avoid cross-region synchronous commit

---

## Azure Site Recovery (ASR) for SQL VM

- ASR replicates entire VM (including SQL Server and databases) asynchronously
- Not supported for Ultra Disk or Premium SSD v2
- Use for unplanned DR; complement with SQL AG for planned failover
- RPO ~2 minutes; RTO depends on VM size and disk count

---

## Important Patterns & Constraints

- SQL IaaS Agent extension requires VM to be running during registration; lightweight mode can register offline
- Azure Hybrid Benefit licensing: a 4-vCore Standard license covers a 4-vCore Azure VM; Enterprise allows unlimited virtualization on dedicated hardware only
- WSFC requires domain membership or workgroup cluster (SQL Server 2022+) — plan AD DS or Entra DS
- AG listener with ILB: set `RegisterAllProvidersIP=0` and `HostRecordTTL=300` in PowerShell after cluster creation; or use DNN listener (simpler, preferred)
- Temp disk (D: drive on Windows, /mnt on Linux) is **ephemeral** — do not place SQL data files or persistent data here; use for TempDB only with proper configuration
- Storage Spaces Direct (S2D) for FCI requires Windows Server Datacenter edition licensing; verify before choosing
- Log shipping across regions: ensure SQL Server version compatibility; Standard edition supports log shipping
- SQL Server 2022 and later support non-domain WSFC (workgroup clusters) with certificates for authentication
- Always use Accelerated Networking on SQL VM NICs for lowest network latency between cluster nodes
