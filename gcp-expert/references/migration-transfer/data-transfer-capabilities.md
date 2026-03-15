# Data Transfer — Capabilities

## Storage Transfer Service

**Storage Transfer Service** is a fully managed data movement service for transferring data into and between cloud storage systems at scale.

### Supported Transfer Sources and Destinations

| Source | Destination | Use Case |
|---|---|---|
| Amazon S3 | Cloud Storage | Migrate data from AWS |
| Azure Blob Storage | Cloud Storage | Migrate data from Azure |
| Cloud Storage | Cloud Storage | Cross-region or cross-project copy |
| HTTP/HTTPS URL list | Cloud Storage | Download from web sources |
| POSIX filesystem (on-premises) | Cloud Storage | On-premises to cloud migration |
| Cloud Storage | Amazon S3 | Copy data back to AWS (bidirectional) |

### Transfer Agents (On-Premises)

For transferring from on-premises POSIX filesystems:
- Install **Transfer Service agents** on Linux hosts in your datacenter
- Agents run as Docker containers; pull from GCR
- Multiple agents can run in parallel across multiple hosts for higher throughput
- Agents use TLS to communicate with the Transfer Service API
- Typical throughput: 100MB/s per agent per 1Gbps network link

### Key Features

**Scheduling:**
- One-time transfer (run now)
- Recurring transfers (daily, weekly, custom CRON schedule)
- Transfer window (only transfer during specified hours to avoid network contention)

**Filtering:**
- Include/exclude by object name prefix
- Include/exclude by last modification time
- Include/exclude by minimum/maximum object size

**Deletion options:**
- Delete source objects after successful transfer (for move operations)
- Delete destination objects not found in source (for sync operations)
- Default: copy only (no deletion)

**Event-driven transfers:**
- Trigger transfers automatically when objects are added to S3 or GCS buckets (via EventGrid/SQS for S3, Pub/Sub notifications for GCS)
- Near-real-time data replication between cloud storage systems

**Bandwidth controls:**
- Limit bandwidth for on-premises agent transfers to avoid saturating WAN links
- Set transfer window to transfer only during off-hours

**Checksumming and verification:**
- MD5 checksums verified end-to-end
- Transfer jobs report object counts, byte counts, and failure details

### Pricing
- Free for transfers into GCP (ingress)
- Charged for transfer operations when source is outside GCP (per-GB operations fee)
- Egress charges apply for data leaving GCP

---

## Transfer Appliance

**Transfer Appliance** is a high-capacity physical storage device that Google ships to your location for offline data transfer when network bandwidth is insufficient for online transfer.

### Use Cases

Calculate whether to use Transfer Appliance:
- At 100Mbps sustained: 100TB takes ~100 days over the network
- At 1Gbps sustained: 100TB takes ~10 days over the network
- Transfer Appliance: 100TB in ~1-2 weeks total (ship + ingest + copy)

**Use Transfer Appliance when:**
- Data set is larger than 100TB
- Available network bandwidth would require more than 1 week to transfer
- Transferring PBs of data (use multiple appliances in parallel)
- Data is sensitive and you prefer not to transfer over internet

### Appliance Models

| Model | Raw Capacity | Usable Capacity | Form Factor |
|---|---|---|---|
| TA40 | 40TB | ~40TB | 1U rack unit |
| TA300 | 300TB | ~300TB | 2U rack unit |
| TA480 | 480TB | ~480TB | 4U rack unit |

### Workflow

1. **Order**: request appliance from Cloud Console (Billing > Transfer Appliance); provide shipping address and delivery window
2. **Receive**: Google ships appliance; typically 3-5 business days in US
3. **Connect**: rack the appliance; connect to your network (10GbE or 25GbE); power on
4. **Capture key**: appliance uses hardware security module; register with online key server to unlock
5. **Transfer data**: use NFS mount, SMB share, or the Transfer Appliance management tool; AES-256 encryption in transit to appliance
6. **Ship back**: appliance auto-erases when key is revoked; ship back to Google
7. **Ingest**: Google ingests data to your specified Cloud Storage bucket within the target region; notification when complete
8. **Verify**: Google provides manifest; verify object counts and checksums

### Security

- AES-256 hardware encryption at rest on appliance
- Cloud HSM-backed key; key destroyed when job completes (remote wipe before return shipping)
- Data never decrypted until it reaches GCP and is written to Cloud Storage

---

## BigQuery Data Transfer Service

The **BigQuery Data Transfer Service (BQDTS)** automates loading external data into BigQuery on a scheduled basis, without custom ETL code.

### Connectors (Data Sources)

**Google Marketing and Ads:**
- Google Ads (formerly Google AdWords) — campaign, ad group, keyword performance
- Display & Video 360 (DV360)
- Search Ads 360 (SA360)
- YouTube Channel and YouTube Content Owner reports
- Google Analytics 4 (event data)
- Campaign Manager 360

**Third-Party SaaS:**
- Salesforce (reports and objects)
- Facebook Ads
- Teradata (via partner connector)
- Amazon Redshift (full migration + incremental)
- Amazon S3 (scheduled import to BigQuery)
- Azure Blob Storage

**Cross-Region BigQuery:**
- Copy BigQuery datasets between regions (US to EU, etc.)
- Useful for disaster recovery and data locality compliance

### Scheduled Transfer Configuration

Each transfer config specifies:
- **Data source**: which connector and credentials
- **Dataset destination**: BigQuery dataset and project
- **Schedule**: daily, weekly, or custom interval; start/end time
- **Backfill range**: load historical data from a date range (for first-time setup)
- **Notification**: Pub/Sub topic for transfer completion/failure events

### How Transfers Work

- Transfer service runs in Google's infrastructure; no agents to maintain
- Data loaded in append or overwrite mode depending on connector
- Partitioned tables: data loaded into date-partitioned tables (e.g., `my_dataset.google_ads_YYYYMMDD`)
- Failed transfers: automatic retry; manual trigger for specific date ranges
- Transfer logs: available in Cloud Logging under `bigquery.googleapis.com/transfer_config`

### Amazon Redshift to BigQuery Migration

Special case for large-scale warehouse migration:
1. Configure Redshift export to S3 (unload to Parquet or CSV)
2. BQDTS S3 connector imports from S3 to BigQuery
3. One-time historical load + ongoing incremental for any remaining data in Redshift
4. Alternative: use Datastream for CDC-based replication if Redshift is still active during migration

---

## Datastream (CDC)

**Datastream** provides Change Data Capture (CDC) replication for ongoing, low-latency streaming of database changes to GCP.

> Primary documentation: see `database/database-migration-capabilities.md`

Brief summary for data transfer context:
- Sources: MySQL, PostgreSQL, Oracle, SQL Server (managed or on-premises)
- Destinations: Cloud Storage (for Dataflow processing), BigQuery (direct streaming), AlloyDB
- Use case: continuous replication during and after database migration; real-time analytics from operational databases; event-driven architecture with CDC events in Pub/Sub
- Replication lag: typically seconds to minutes

---

## gcloud storage rsync

For smaller-scale or scripted transfers between Cloud Storage buckets or from local to GCS:

```bash
# Sync local directory to GCS (add --delete-unmatched-destination-objects to mirror)
gcloud storage rsync /local/data/ gs://my-bucket/data/ --recursive

# Sync between two GCS buckets (cross-region copy)
gcloud storage rsync gs://source-bucket/ gs://destination-bucket/ --recursive

# Dry run to preview what would be copied
gcloud storage rsync gs://source-bucket/ gs://destination-bucket/ --recursive --dry-run

# Exclude certain file patterns
gcloud storage rsync /local/data/ gs://my-bucket/ --recursive \
  --exclude=".*\.tmp$|.*\.log$"
```

`gcloud storage rsync` uses checksums to skip already-transferred objects, making it efficient for incremental syncs.
