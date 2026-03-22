# Azure SQL — Capabilities Reference
For CLI commands, see [azure-sql-cli.md](azure-sql-cli.md).

## Azure SQL Overview

**Purpose**: Family of fully managed SQL Server-compatible database services on Azure. Covers single databases, elastic pools, managed instances, and serverless options — from development workloads to mission-critical enterprise databases.

### Deployment Options

| Option | Description | Compatibility | Best For |
|---|---|---|---|
| **Azure SQL Database (Single DB)** | Fully managed single database; hyperscale architecture | Latest SQL Server stable features | Cloud-native apps; SaaS multi-tenant; variable workloads |
| **Azure SQL Database (Elastic Pool)** | Shared resources (eDTUs or vCores) across multiple databases | Same as Single DB | SaaS with many tenants at varying activity levels |
| **Azure SQL Database (Serverless)** | Auto-scale compute; auto-pause; per-second billing | Same as Single DB | Dev/test; variable unpredictable workloads |
| **Azure SQL Managed Instance** | Full SQL Server instance with VNet integration | Near-complete SQL Server 2022 compatibility | Lift-and-shift legacy SQL Server apps |
| **Instance Pool** | Multiple managed instances sharing compute | Same as Managed Instance | Consolidate many small SQL MI instances efficiently |

---

## Service Tiers and Purchasing Models

### vCore Purchasing Model (Recommended)

| Tier | Storage | IOPS | HA Architecture | Replicas | Use Case |
|---|---|---|---|---|---|
| **General Purpose (GP)** | Remote Premium SSD; 5–8 TiB | Up to 7,000 IOPS | Single replica + remote storage HA | 1 primary | General workloads; cost-optimized |
| **Business Critical (BC)** | Local NVMe SSD; up to 4 TiB | Up to 204,800 IOPS | Always On AG; 4 nodes (3 sync, 1 async) | 1 primary + 3 replicas (1 readable) | High IOPS, low latency; in-memory OLTP; readable secondary included |
| **Hyperscale** | Distributed page server architecture; up to 100 TiB | Up to 204,800 IOPS | Compute separated from storage; multiple replicas | 1 primary + up to 30 named replicas | Very large databases; fast backup/restore; read scale-out |

### DTU Purchasing Model (Legacy)

| Tier | Description |
|---|---|
| **Basic** | Up to 2 GB; 5 DTUs; dev/test small databases |
| **Standard** | Up to 1 TB; 10–3,000 DTUs; most production workloads |
| **Premium** | Up to 4 TB; 125–4,000 DTUs; in-memory OLTP; high-I/O |

- DTU model bundles compute, memory, and I/O into single unit; cannot adjust independently
- **vCore model recommended** for new workloads: transparent resource allocation, Azure Hybrid Benefit, reserved capacity pricing

### Serverless Tier

| Feature | Description |
|---|---|
| **Compute auto-scale** | Scale between min and max vCores based on workload demand; scale in seconds |
| **Auto-pause** | Pause after configured idle period (1 hour to 7 days); resume on next connection |
| **Billing** | Per-second billing for compute when active; storage always billed; pause = storage only |
| **Limitations** | GP tier only; not available for elastic pools; some features require disabling auto-pause |

---

## High Availability Architecture

### General Purpose HA

- Primary replica with attached remote Premium SSD storage
- Automated HA via Azure Service Fabric: failover to standby replica (cold) in ~20–30 seconds
- **Zone-redundant GP**: primary + hot standby replica in different AZ; RPO ~0; RTO <30s

### Business Critical HA

- Built-in Always On Availability Group with 4 nodes (3 in sync, 1 async)
- One readable secondary included at no extra cost (for reporting, read-offload)
- Failover in 2–10 seconds; automatic; transparent to application with retry logic
- **Zone-redundant BC**: nodes spread across AZs; survives AZ failure

### Hyperscale HA

- **Architecture**: Compute layer + log service + page servers (distributed storage) + backup storage
- Compute nodes stateless; attach to page servers; failover in <60 seconds
- **Named replicas**: up to 30 read-scale replicas; independent compute; same shared page server storage
- **High-speed backup**: page server architecture enables backup in minutes regardless of size
- **Fast restore**: from snapshot in minutes (vs hours for traditional backup restore)

---

## Geo-Replication and Failover

### Active Geo-Replication (Single Database)

- Asynchronous replication to up to 4 readable secondary databases in different regions
- Secondaries are fully readable; can be used for read offload, reporting, dev/test
- Manual failover (no automatic); supports planned (zero data loss) and unplanned failover
- Available for vCore and DTU models; single DB only (not Elastic Pool)

### Auto-Failover Groups

- Automatic failover of one or more databases to a secondary region
- Built-in read-write listener DNS: `<fog-name>.database.windows.net` (auto-routes to primary)
- Built-in read-only listener DNS: `<fog-name>.secondary.database.windows.net`
- Configurable grace period before automatic failover (to avoid false positives)
- Supports single databases, elastic pools, and Managed Instances
- **Application transparent**: listener endpoint handles routing without connection string changes after failover

---

## Azure SQL Managed Instance (SQL MI)

**Purpose**: Full SQL Server engine deployed in a VNet-injected managed environment. Near-complete compatibility with on-premises SQL Server 2022, including features unavailable in SQL Database.

### Key Differentiators from SQL Database

| Feature | SQL Database | SQL MI |
|---|---|---|
| **SQL Server Agent** | No | Yes |
| **Cross-database queries** | No (same server) | Yes |
| **Linked Servers** | No | Yes |
| **CLR assemblies** | Limited | Yes (safe assemblies) |
| **Replication** | Transactional (subscriber only) | Full (publisher, distributor, subscriber) |
| **Service Broker** | No | Yes |
| **SSRS, SSAS, SSIS** | No | Partial (via integration) |
| **VNet native integration** | No (private endpoint) | Yes (VNet injection) |
| **Instance-scoped features** | No | Yes (logins, linked servers, agent jobs) |

### SQL MI Architecture

- Deployed into dedicated subnet in Azure VNet; all traffic stays in VNet
- Management endpoint: publicly accessible for Azure management plane only (SSL)
- **Business Critical** and **General Purpose** service tiers (same as SQL Database)
- Instance size: 4–80 vCores; storage up to 16 TiB
- **Maintenance window**: configure specific windows for patching

### SQL MI Link (Hybrid)

- Replication link between on-premises SQL Server (2016+) and SQL MI in Azure
- Use for: online migration to Azure; hybrid read-scale; DR for on-premises SQL Server
- Based on Always On Availability Groups technology
- One-way (SQL Server → MI) or bidirectional (with AG on both sides)

---

## Security

### Encryption

| Feature | Description |
|---|---|
| **Transparent Data Encryption (TDE)** | Encrypts database files at rest; on by default; PMK or CMK (via Azure Key Vault) |
| **Always Encrypted** | Client-side column-level encryption; keys never leave client; Azure Key Vault integration |
| **Dynamic Data Masking (DDM)** | Obfuscates sensitive data in query results for non-privileged users; no schema changes |
| **Row-Level Security (RLS)** | Filter rows based on user context; enforced in database engine |

### Threat Protection

| Feature | Description |
|---|---|
| **Microsoft Defender for SQL** | Anomaly detection; SQL injection alerts; unusual access pattern detection |
| **Advanced Threat Protection** | Part of Defender for SQL; vulnerability assessment; detects SQL injection, brute force, privilege abuse |
| **Azure Defender Vulnerability Assessment** | Automated scan for misconfigurations and vulnerabilities; baseline tracking |
| **Audit** | Track all database events to Log Analytics, Storage Account, or Event Hub |

### Ledger Tables

- Cryptographically verifiable append-only tables (using blockchain-like SHA-256 hash chaining)
- **Updatable ledger tables**: full audit history stored in separate history table; tamper-evident
- **Append-only ledger tables**: INSERT only; ideal for financial transactions, votes, audit records
- Database digest exported to Azure Confidential Ledger or Azure Storage for independent verification

---

## Intelligence and Performance

### Automatic Tuning

| Feature | Description |
|---|---|
| **Automatic index management** | Recommends and auto-applies CREATE INDEX; monitors impact; rolls back if negative |
| **Plan regression correction** | Detects query plan regressions after SQL Server updates; forces last-known good plan |
| **Query Store** | Built-in query performance history; plan forcing; regression detection; always on in Azure SQL |

### Intelligent Query Processing

- Adaptive query processing (batch mode memory grant feedback, interleaved execution)
- Approximate query processing (`APPROX_COUNT_DISTINCT`)
- In-memory OLTP (Business Critical tier): memory-optimized tables and natively compiled procedures

### Elastic Jobs (SQL Database)

- Managed job orchestration for SQL Database; schedule T-SQL across multiple databases
- Similar to SQL Server Agent but cloud-native; targets elastic pool databases, shards
- Components: Job Agent, Job Database, Target Groups, Steps

### SQL Data Sync

- Sync data bidirectionally between SQL Database and SQL Server (on-premises or Azure VM)
- Hub-and-spoke topology; conflict resolution: hub wins or member wins
- Use case: replicate subset of data to edge locations or on-premises

---

## Elastic Pool

- Shared pool of eDTUs or vCores across multiple databases
- Individual databases can burst to pool max; prevented from starving each other
- **Per-database min/max settings**: guarantee minimum resources; cap maximum per database
- Cost savings when databases have staggered peak usage (SaaS multi-tenant pattern)
- Up to 500 databases per Standard/Premium pool; 100 per Basic pool

---

## Important Patterns & Constraints

- SQL Database and SQL MI logical servers are different resources; MI is VNet-injected
- Auto-failover groups require that both primary and secondary servers/instances are in different regions
- Hyperscale cannot currently be downgraded to other service tiers (migration requires export/import)
- Business Critical readable secondary counts toward license but is included in BC pricing
- TDE with CMK: if Key Vault access lost, database becomes inaccessible — ensure Key Vault high availability (GRS, soft delete, purge protection)
- SQL MI subnet must be delegated to `Microsoft.Sql/managedInstances`; minimum /27 subnet; management ports 9000, 9003, 1438, 1440, 1452 must be open
- SQL MI deployment and scaling operations take 4–6 hours; plan maintenance windows
- Serverless auto-pause: connections during pause trigger warm-up (~45 seconds); not suitable for latency-sensitive applications
- Azure Hybrid Benefit for SQL Server: use existing SQL Server licenses to reduce SQL Database/MI vCore costs by up to 55%
