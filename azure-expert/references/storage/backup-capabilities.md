# Azure Backup & Recovery — Capabilities Reference
For CLI commands, see [backup-cli.md](backup-cli.md).

## Azure Backup

**Purpose**: Cloud-native backup service providing zero-infrastructure, scalable protection for Azure workloads and on-premises resources. Stores backup data in Recovery Services Vaults with built-in security, compliance, and lifecycle management.

### Recovery Services Vault (RSV)

- Primary container for both Azure Backup and Azure Site Recovery data
- Regional resource (backup data stays in same region as vault, unless Cross-Region Restore enabled)
- **Immutability**: Vault-level immutability prevents deletion or shortening of backup data; Unlocked (reversible) or Locked (irreversible)
- **Soft delete**: Deleted backup data retained 14 additional days at no cost; default enabled; cannot disable in locked vaults
- **Multi-user authorization (MUA)**: Requires additional Resource Guard approval for critical operations (disabling soft delete, deleting vault, stopping protection)
- Storage redundancy: LRS (default), GRS (recommended), or ZRS (for zone-resilient vaults)

### Backup Vault (vs Recovery Services Vault)

- Newer vault type for newer workloads (Blobs, Disks, PostgreSQL, AKS)
- Does not support VM or SQL backup — those remain in Recovery Services Vault
- Uses Azure RBAC natively; no storage account dependency

---

## Supported Workloads

### Azure VMs

| Feature | Details |
|---|---|
| **Agent** | Azure VM Backup uses snapshot-based backup; no agent needed for crash-consistent; optional workload-aware agent (MARS) for app-consistent |
| **Consistency** | Application-consistent (VSS on Windows; pre/post scripts on Linux); crash-consistent fallback |
| **Instant Restore** | Snapshot stored locally for 1–5 days; instant recovery without waiting for vault transfer |
| **Restore options** | Restore to new VM, restore disks only, replace existing VM disk, file-level restore, cross-region restore |
| **Backup frequency** | Daily or multiple per day (Enhanced policy) |
| **Retention** | Daily (up to 9,999), weekly, monthly, yearly; GFS (Grandfather-Father-Son) scheme |

### SQL Server in Azure VMs

| Feature | Details |
|---|---|
| **Agent** | SQL IaaS Agent extension required; workload-aware backup |
| **Backup types** | Full, differential, transaction log |
| **Log backup frequency** | Every 15 minutes (minimum RPO) |
| **Retention** | Up to 99 years |
| **Auto-protection** | Automatically protect new databases added to registered instance |
| **Restore** | Point-in-time restore to any second; restore to alternate SQL instance |

### SAP HANA in Azure VMs

- Backint API integration; SAP-certified backup
- Full, differential, incremental, and log backups
- Log backups every 15 minutes; RPO ~15 minutes
- Restore to original or alternate HANA instance

### Azure Files

- Share-level snapshots via Azure Backup; up to 200 snapshots per share
- Instant restore from snapshot (no data movement)
- Scheduled (daily/weekly/monthly/yearly) retention
- Backup stored in vault (operational backup) or as snapshot on storage account

### Azure Blobs (Operational & Vaulted)

| Type | Description |
|---|---|
| **Operational backup** | Continuous backup using blob versioning and point-in-time restore; data stays in storage account; restore any point within 1–360 days |
| **Vaulted backup** | Periodic snapshots stored in Backup Vault; supports cross-region restore; GRSV support |

### Azure Managed Disks

- Snapshot-based backup stored in Backup Vault (not RSV)
- Incremental snapshots; retain up to 10 years
- Restore to new disk in same or different region (cross-region restore)

### Azure Kubernetes Service (AKS)

- Backup agent (Velero-based) deployed in AKS cluster
- Backs up Kubernetes resources + persistent volume data (Azure Disk or Azure Blob)
- Point-in-time restore; cross-region restore for DR
- Stored in Backup Vault

---

## Backup Policy

| Setting | Description |
|---|---|
| **Schedule** | When to trigger backup: time of day, day of week/month |
| **Retention** | How long to keep each recovery point (daily/weekly/monthly/yearly) |
| **Snapshot retention** | Local snapshot tier: 1–5 days for instant restore (VM backup) |
| **Tier** | Standard policy vs Enhanced policy (multiple backups/day, trusted Azure VM only) |
| **Archive tier** | Move older recovery points (180+ days) to Archive vault tier for cost savings |

### Enhanced Policy vs Standard Policy (Azure VM)

| Feature | Standard Policy | Enhanced Policy |
|---|---|---|
| Backup frequency | Once daily | Up to 6 times/day (every 4 hours) |
| Instant restore | Up to 5 days | Up to 30 days |
| Disk types | All | All |
| Trusted Launch VMs | No | Yes |
| Archive support | Yes | Yes |

---

## Azure Site Recovery (ASR)

**Purpose**: Disaster recovery replication for Azure VMs (and on-premises VMware/Hyper-V/physical servers) to a secondary Azure region. Continuous replication with RPO typically 2 minutes; RTO within SLA defined by cutover process.

### ASR Architecture (Azure VM to Azure)

| Component | Description |
|---|---|
| **Source region** | Production Azure region with VMs to protect |
| **Target region** | DR region; paired region or any region |
| **Recovery Services Vault** | Created in target region; stores replication metadata and ASR configuration |
| **Cache Storage Account** | Temporary storage in source region; replication data staged before transfer |
| **Replica Managed Disks** | Maintained in target region; updated continuously from source |
| **Recovery Plan** | Ordered runbook for failover; can include Azure Automation scripts, manual steps |

### ASR Replication Key Concepts

| Concept | Description |
|---|---|
| **Replication** | Continuous block-level replication via ASR Mobility Service; crash-consistent every 5 min; app-consistent every 1–12 hours |
| **RPO** | Typically 2 minutes for crash-consistent; up to 1 hour for app-consistent (configurable) |
| **Test Failover** | Run a DR drill using isolated test network; no impact to production replication |
| **Planned Failover** | Zero data loss; sync before cutover; used for planned maintenance |
| **Unplanned Failover** | Trigger during disaster; uses latest recovery point (crash/app-consistent) |
| **Failback** | Reverse replication from DR region back to original primary after recovery |

### Supported Replication Scenarios

| Source | Target | Notes |
|---|---|---|
| Azure VM | Azure VM (different region) | Native; no additional agents for most scenarios |
| Azure VM (Zone to Zone) | Same region, different AZ | Protects against AZ-level failure within a region |
| On-premises VMware | Azure | Configuration Server + Process Server + Mobility Service |
| On-premises Hyper-V | Azure | Hyper-V Recovery Manager or standalone provider |
| Physical servers | Azure | Same as VMware with Physical Server provider |

### Recovery Plans

- Define failover order for multi-tier applications (web → app → database)
- Group VMs into ordered steps; add pre/post Azure Automation scripts
- Customize for each failover type (test, planned, unplanned)
- Test failover validates DR readiness without disrupting production

---

## Backup Center

**Purpose**: Unified governance and management console for all Azure Backup and Site Recovery configurations across subscriptions, resource groups, vaults, and workloads.

| Feature | Description |
|---|---|
| **Unified view** | All backup jobs, alerts, policies, and protected items across vaults |
| **At-scale operations** | Configure backup, modify policies, run jobs across multiple vaults simultaneously |
| **Reports** | Azure Monitor-based reports; Backup reports for historical analysis (cost, usage, compliance) |
| **Alert management** | Consolidated alert view; integrate with Azure Monitor alerts and action groups |
| **Governance** | Azure Policy integration to enforce backup on VMs at scale |

---

## Cross-Region Restore (CRR)

- Restore backup data to a secondary (paired) region even when primary region is unavailable
- Requires: vault storage redundancy set to GRS; CRR enabled on vault
- Supported workloads: Azure VMs, SQL Server in VMs, SAP HANA in VMs
- Adds replication lag (typically hours); secondary region data is "secondary copy"
- Use case: regional disaster; regulatory requirement for geographic redundancy

---

## Security and Compliance

| Feature | Description |
|---|---|
| **Soft delete** | 14-day grace period for deleted backup data; no additional cost; alerts on suspicious deletions |
| **Vault immutability** | Prevent policy weakening and backup deletion; Unlocked (reversible) or Locked (permanent) |
| **Multi-user authorization (MUA)** | Require approval from Resource Guard (separate subscription) for destructive operations |
| **Encryption** | Backup data encrypted at rest; platform-managed keys by default; CMK supported for vault encryption |
| **Private Endpoints** | Backup traffic flows via private IP; no public internet; recommended for regulated environments |
| **RBAC roles** | Backup Contributor, Backup Operator, Backup Reader; scope to vault level |

---

## Important Patterns & Constraints

- Recovery Services Vault must be in same region as backed-up Azure VMs (except Cross-Subscription Restore scenarios)
- SQL Server backup requires SQL IaaS Agent extension and `AzureBackupWindowsWorkload` extension on VM
- Azure Blob operational backup requires blob versioning and point-in-time restore enabled on storage account
- ASR replication data and cache storage account must be in source region; vault in target region
- ASR zone-to-zone replication uses same vault in same region (not cross-region)
- Ultra Disk and Premium SSD v2 are not supported by Azure Site Recovery — use application-level replication (SQL AG, HANA HSR)
- Backup center is a management view only; actual backup configuration still per-vault
- Disabling soft delete requires MUA if vault immutability is locked
- Instant restore snapshot and vault recovery point are independent; vault copy may lag hours behind snapshot
