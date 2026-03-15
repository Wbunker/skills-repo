# Backup and DR — Capabilities Reference

CLI reference: [backup-dr-cli.md](backup-dr-cli.md)

This document covers three related but distinct services: **Backup and DR Service** (centralized managed backup), **Cloud Storage Transfer Service** (scheduled data transfer), and **Transfer Appliance** (offline large-scale migration).

---

## Backup and DR Service

### Overview
Google Cloud Backup and DR Service is a centralized, managed backup service for protecting GCP workloads including Compute Engine VMs, databases (Cloud SQL, Spanner, AlloyDB), file systems (Filestore), and on-premises workloads. It provides a unified backup management interface, automated backup plans, and application-consistent backups.

### Architecture
- **Backup/recovery appliance**: a managed virtual appliance deployed in your VPC that orchestrates backups. One appliance per project (or shared across projects with appropriate networking).
- **Backup vault**: immutable, access-controlled storage for backup images. Created in a GCP project. Supports WORM (Write Once Read Many) for compliance.
- **Management server**: the central management console for Backup and DR, hosted by Google. Accessed via the Cloud Console UI.
- **Data sources**: workloads registered for backup (VMs, databases, file systems).

### Core Concepts

| Concept | Description |
|---|---|
| Management server | Centralized management UI and API endpoint for Backup and DR. Google-hosted. |
| Backup/recovery appliance | Agent deployed in customer VPC; manages backup scheduling, deduplication, and transfers to backup vault. |
| Backup vault | Immutable, access-controlled repository for backup images. Can be locked (WORM) for compliance. |
| Backup plan | Policy defining which data sources to back up, how frequently, and retention rules. |
| Backup rule | Within a backup plan: specifies schedule, retention, and target backup vault. |
| Data source | A workload registered for backup: Compute Engine VM, Cloud SQL instance, Filestore instance, etc. |
| Recovery point | A specific point-in-time backup that can be used for restore. |
| Application-consistent backup | Backup taken with application coordination (quiesce writes, flush buffers) for databases and VMs. |
| Incremental forever | After initial full backup, only changed blocks are captured. Faster backups and lower storage cost. |

### Supported Workloads

| Workload | Backup Type | Application Consistency |
|---|---|---|
| Compute Engine VMs | Block-level disk image | VSS (Windows) / pre/post scripts (Linux) |
| VMware VMs on GCVE | VMDK-level backup via vSphere API | VSS or filesystem quiesce |
| Cloud SQL (MySQL/PostgreSQL/SQL Server) | Managed backup via Cloud SQL backup API | Application-consistent (managed service) |
| Spanner | Managed export-based backup | Application-consistent |
| AlloyDB | Managed backup (separate from standard AlloyDB backups) | Application-consistent |
| Filestore | NFS snapshot and backup | Filesystem-consistent |
| On-premises (via Backup/Recovery Appliance) | Block-level capture | VSS / agent-based |
| Google Workspace (Vault) | Separate service (Google Vault) | N/A |

### Backup Plan Structure
A backup plan defines:
1. **Backup rules**: one or more rules specifying schedule (hourly, daily, weekly), backup window, and retention period.
2. **Target vault**: which backup vault receives the backup images.
3. **SLA protection**: policies defining RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets with alerting if backups fall behind.

### Retention Policies
- **Backup rule retention**: each rule specifies how many days to retain backups.
- **Expiration**: backups expire automatically when the retention period ends.
- **WORM (locked) vaults**: backups in locked vaults cannot be deleted before expiry, even by admins. Required for FINRA, SEC Rule 17a-4, HIPAA.
- **Multi-level retention**: define rules for daily (7 days), weekly (4 weeks), monthly (12 months) in a single backup plan.

### Deduplication and Compression
Backup and DR performs global deduplication across all backups in a backup vault. Only unique data blocks are stored. Typical reduction ratio: 30-70% depending on workload. Compression further reduces storage cost.

---

## Cloud Storage Transfer Service

### Overview
Managed service for scheduled, large-scale data transfers to and from Cloud Storage. Handles transfers between:
- Cloud Storage buckets (GCS to GCS)
- Amazon S3 to Cloud Storage
- Azure Blob Storage to Cloud Storage
- On-premises to Cloud Storage (using Google-installed Transfer Service agents)
- HTTP/HTTPS URLs to Cloud Storage
- HDFS to Cloud Storage (via agent)

### Core Concepts

| Concept | Description |
|---|---|
| Transfer job | Defines source, destination, schedule, and filter settings. Can run once or on a recurring schedule. |
| Transfer operation | A single execution of a transfer job. Tracks progress (bytes transferred, files transferred, errors). |
| Agent | A Docker container installed on on-premises or cloud VMs that handles transfers from POSIX (on-prem) sources. Multiple agents can run in parallel. |
| Agent pool | A group of agents that execute on-premises transfer jobs. Provides load balancing and redundancy. |
| Bandwidth limit | Per-agent or per-job bandwidth cap to avoid saturating network links. |
| Filter | Include/exclude patterns by filename prefix, suffix, or last modified date. |
| Event-driven transfer | Trigger transfers when new objects appear in S3 or Azure Blob (uses event notifications). |

### Transfer Sources and Destinations

| Source | Destination | Notes |
|---|---|---|
| Cloud Storage | Cloud Storage | Intra-GCP copy/sync; also used for cross-region migration |
| Amazon S3 | Cloud Storage | Uses S3 credentials (HMAC key) or IAM role |
| Azure Blob Storage | Cloud Storage | Uses Azure SAS token |
| HTTP/HTTPS source list | Cloud Storage | List of URLs in a manifest; transfers each URL to GCS |
| POSIX filesystem (on-prem) | Cloud Storage | Requires Transfer Service agents installed on-prem |
| HDFS (Hadoop) | Cloud Storage | Requires Transfer Service agent on Hadoop edge nodes |

### Key Features
- **Scheduled transfers**: run daily, weekly, or one-time at a specific time (cron-like).
- **Event-driven transfers**: trigger automatically when new data arrives in S3 or Azure Blob.
- **Bandwidth throttling**: set MB/s limit per agent to avoid saturating network connections.
- **Filtering**: include/exclude objects by name prefix/suffix, creation date range, or last modified date.
- **Delta transfers**: only transfer new or modified objects (skip already-transferred objects).
- **Google-managed infrastructure**: no servers to manage; Google runs the transfer infrastructure.
- **Audit logging**: all transfer operations logged to Cloud Audit Logs.

### On-Premises Transfer Agents
For POSIX filesystem sources:
1. Create an agent pool in the Cloud Console.
2. Install agents as Docker containers on source servers or VMs.
3. Agents connect to Google-managed transfer infrastructure.
4. Agents run transfers in parallel; more agents = higher aggregate throughput.
5. Individual agent throughput: up to 1 Gbps per agent (network-dependent).

---

## Transfer Appliance

### Overview
Physical hardware appliances shipped to customer premises for offline large-scale data migration to Cloud Storage. Use when uploading data over the internet would take weeks or months due to data volume or bandwidth constraints.

### Models

| Model | Raw Capacity | Usable Capacity | Form Factor |
|---|---|---|---|
| Transfer Appliance TA100 | 100 TB | ~85 TB usable | 1U rack unit |
| Transfer Appliance TA480 | 480 TB | ~400 TB usable | 2U rack unit |

**Rule of thumb**: if transferring >10 TB over a 100 Mbps connection would take >10 days, consider Transfer Appliance.

### Process
1. **Order**: request appliance via Google Cloud Console. Provide shipping address and bucket destination.
2. **Receive**: Google ships the appliance to your location (typically 5-10 business days).
3. **Connect**: rack the appliance, connect to your network. Configure via web UI or CLI on the appliance.
4. **Transfer**: copy data to the appliance using NFS mount or the Transfer Appliance software. AES-256 encryption on all data at rest.
5. **Ship back**: when transfer is complete, ship appliance back to Google data center.
6. **Ingest**: Google ingests data from the appliance to your specified Cloud Storage bucket.
7. **Verify**: Google notifies you when data is available in Cloud Storage.
8. **Erase**: Google performs secure data erasure of the appliance after ingestion.

### Security
- Data encrypted at rest with AES-256.
- Appliance uses a customer-set passphrase; Google cannot access data without the passphrase.
- Secure erase after ingestion (NIST 800-88 compliant).

---

## Native Database Backups (Cross-Reference)

While Backup and DR Service handles centralized backup, each database service has native backup mechanisms:
- **Cloud SQL**: automated daily backups, on-demand backups, point-in-time recovery (PITR) via transaction logs. Managed in Cloud SQL service.
- **Spanner**: managed backups and exports (to Cloud Storage as Avro). PITR via version retention.
- **BigQuery**: table snapshots, time-travel queries (7-day retention). No explicit "backup" needed for most use cases.
- **Firestore**: managed exports to Cloud Storage (Firestore Managed Exports).
- **Bigtable**: managed backups with configurable retention.
- **Alloy DB**: automated backups and PITR similar to Cloud SQL.

---

## Important Patterns & Constraints

**Backup and DR Service:**
- The backup/recovery appliance is a VM in your VPC; ensure appropriate sizing (CPU/RAM/disk) for the volume of backups.
- Backup and DR is not the same as Cloud SQL automated backups—it is an additional layer for enterprise centralized management and compliance.
- WORM-locked vaults are irreversible: once locked, backups cannot be deleted early. Test with unlocked vaults first.
- One management server per region; if you need multi-region backup management, use multiple management servers.
- Backup and DR requires network connectivity between the appliance VPC and source VMs.

**Storage Transfer Service:**
- S3 transfers require either an HMAC access key + secret or cross-account IAM role assumption.
- On-premises transfers require firewall rules to allow agent outbound HTTPS to Google APIs.
- Very large transfers (PB-scale) are better suited to Transfer Appliance; Storage Transfer Service is designed for TB-scale recurring transfers.
- Transfer Service is not real-time streaming; minimum interval is seconds/minutes. For event-driven real-time streaming, use Pub/Sub or Datastream.
- Bandwidth limits apply per agent, not per job; total throughput = bandwidth limit × number of agents.

**Transfer Appliance:**
- Not available in all countries; check shipping availability.
- Lead time: 5-10 business days for appliance delivery; plan accordingly.
- Maximum usable capacity per appliance: ~400 TB (TA480). For petabyte-scale migrations, multiple appliances shipped in parallel.
- Encryption passphrase is critical: if lost, data is unrecoverable. Store securely before transfer.
- Transfer Appliance is a one-way tool (on-premises to GCS only); it does not support exports from GCS.
