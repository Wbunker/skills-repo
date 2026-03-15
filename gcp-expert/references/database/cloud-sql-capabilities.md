# Cloud SQL — Capabilities Reference

## Purpose

Cloud SQL is Google Cloud's fully managed relational database service supporting MySQL, PostgreSQL, and SQL Server. Google handles patching, backups, replication, failover, and storage management. You provision instances, choose your engine version and machine type, and connect applications — infrastructure operations are abstracted away.

---

## Supported Engines and Versions

| Engine | Versions | Notes |
|---|---|---|
| MySQL | 5.7, 8.0, 8.4 | MySQL 5.7 approaching EOL; prefer 8.0 or 8.4 for new instances |
| PostgreSQL | 12, 13, 14, 15, 16 | PostgreSQL 12 approaching EOL; prefer 14+ for new instances |
| SQL Server | 2017, 2019, 2022 | Enterprise, Standard, Web, Express editions; bring-your-own-license (BYOL) not available |

---

## Core Concepts

| Concept | Description |
|---|---|
| Instance | A single Cloud SQL database server (VM + storage). Named, versioned, in a specific region. |
| Database | A logical database schema within an instance. Multiple databases can coexist on one instance. |
| User | A database-level user account. Root/postgres user is created at instance creation; additional users can be added. |
| Machine type | vCPU + RAM selection for the instance. Shared core for dev, Standard or High-memory for production. |
| Storage | Persistent disk (SSD or HDD) attached to the instance. Separate from compute. Auto-increase available. |
| Flag | Database engine parameter (e.g., `max_connections`, `slow_query_log`). Set at instance level. |
| Service account | GCP service account attached to the instance for IAM-based operations (e.g., exporting to GCS). |
| Maintenance window | Configurable day/hour window for disruptive updates (engine patching, infrastructure maintenance). |

---

## Machine Types

| Category | vCPU | RAM | Use Case |
|---|---|---|---|
| Shared core | 1 (shared) | 0.6–1.7 GB | Dev, test, low-traffic apps |
| Standard (db-n1-standard, db-custom) | 1–96 | 3.75 GB/vCPU | General-purpose production |
| High-memory (db-n1-highmem, db-custom) | 2–96 | 6.5 GB/vCPU | Memory-intensive workloads, large caches |

Maximum instance size: 96 vCPUs / 624 GB RAM.

Custom machine types: specify any vCPU/RAM combination within engine limits using `db-custom-N-M` (N vCPUs, M MB RAM).

---

## Storage

| Option | Description |
|---|---|
| SSD | Default; low latency, higher IOPS. Recommended for production. |
| HDD | Lower cost; higher latency. Use only for archival or infrequently accessed data. |
| Auto-increase | Automatically increases storage when 95% full. Increase is permanent (cannot shrink). Minimum 10 GB; maximum 64 TB. |
| IOPS | Proportional to disk size. ~30 IOPS per GB for SSD. |

---

## High Availability (HA)

HA configuration provisions a primary instance and a standby instance in different zones within the same region.

- Standby uses **regional persistent disk** (synchronous replication) — data is written to both zones before the write is acknowledged. RPO = 0.
- Automatic failover within approximately 60 seconds if the primary fails a health check.
- Standby does NOT serve read traffic (use read replicas for read scaling).
- HA is not available for Shared Core machine types.
- HA adds ~2x cost (two instances + regional disk).

**Failover behavior**: DNS updates to point to the standby. Applications must reconnect — persistent connections are dropped. Use exponential backoff in application code.

---

## Read Replicas

| Type | Description |
|---|---|
| In-region read replica | Replica in same region as primary; serves read traffic; used for read scaling and reporting |
| Cross-region read replica | Replica in a different region; disaster recovery; can be promoted to standalone in DR scenarios |
| Cascade replica | Replica of a read replica (reduces load on primary for replication traffic) |
| External replica | On-premises or other-cloud MySQL/PostgreSQL server replicating from Cloud SQL primary |

Read replicas use asynchronous replication. There is potential replication lag; queries reading from replicas may see slightly stale data.

Replicas cannot be directly promoted with zero RPO — use HA for automatic failover. Cross-region replicas are promoted manually for DR.

---

## Connection Methods

| Method | Description | When to Use |
|---|---|---|
| Cloud SQL Auth Proxy | Local proxy binary that handles IAM authentication and SSL encryption. Runs alongside the application. | Recommended for all non-VPC access; GKE, GCE, local dev |
| Private Service Access (PSA) | VPC peering between your VPC and the Cloud SQL managed VPC. Instance gets a private IP in your subnet range. | Production apps in GCE/GKE that need lowest latency; no proxy overhead |
| Public IP + Authorized Networks | Instance has external IP; client CIDRs added to allowlist. | Dev/test with SSL; avoid for production |
| Connector libraries | Language-specific libraries (Java, Python, Go) that embed Cloud SQL Auth Proxy functionality | Cloud Functions, App Engine, Cloud Run without sidecar |
| Serverless VPC Access | Required to reach private IP Cloud SQL from Cloud Run or Cloud Functions | Cloud Run/Functions + private IP |

Cloud SQL Auth Proxy v2 is the current version. It authenticates using Application Default Credentials (ADC) or a service account key, and uses the Cloud SQL Admin API to retrieve ephemeral certificates.

---

## Backup and Recovery

| Type | Description |
|---|---|
| Automated backup | Daily backup taken during a configurable 4-hour window. Stored in regional or multi-regional Cloud Storage. Default retention: 7 backups. Configurable up to 365. |
| On-demand backup | Manually triggered backup. Not automatically deleted; persists until you delete it. |
| Binary log (MySQL) / WAL archiving (PostgreSQL) | Enables Point-in-Time Recovery (PITR). MySQL uses binary log; PostgreSQL uses WAL archives to Cloud Storage. |
| PITR | Restore to any second within the retention window (default 7 days). Creates a new instance. |
| Export to Cloud Storage | SQL dump or CSV export to GCS bucket. Useful for cross-project or cross-region copies. |

**PITR prerequisite**: Binary log / WAL archiving must be enabled before the incident. Enable this on all production instances.

---

## PostgreSQL Extensions

Common extensions available in Cloud SQL for PostgreSQL:

| Extension | Use Case |
|---|---|
| pgvector | Vector similarity search; AI/ML embeddings |
| PostGIS | Geospatial queries |
| pg_cron | Scheduled SQL jobs within the database |
| pglogical | Logical replication |
| uuid-ossp | UUID generation |
| pg_trgm | Trigram fuzzy text search |
| hstore | Key-value pairs in a column |
| tablefunc | Crosstab (pivot) queries |
| pg_partman | Partition management |
| plpgsql | PL/pgSQL procedural language (default enabled) |

Enable with: `CREATE EXTENSION IF NOT EXISTS pgvector;`

---

## Flags (Engine Parameters)

Set at the instance level. Examples:

**MySQL**:
- `max_connections`: default varies by machine type (~100–4000)
- `slow_query_log`: `on`/`off`
- `long_query_time`: seconds threshold for slow query log
- `innodb_buffer_pool_size`: typically set to 70% of RAM

**PostgreSQL**:
- `max_connections`: default 100; adjust based on machine type
- `log_min_duration_statement`: log queries slower than N milliseconds
- `work_mem`: per-sort/hash operation memory
- `shared_buffers`: controlled by Cloud SQL (not directly settable); use `cloudsql.enable_pgaudit` for audit logging

**SQL Server**:
- `max degree of parallelism (MAXDOP)`
- `cost threshold for parallelism`
- `remote access`

---

## When to Use Cloud SQL vs. Alternatives

| Scenario | Recommended Service |
|---|---|
| Single-region relational database, standard OLTP | Cloud SQL |
| High-performance PostgreSQL, need columnar analytics or 4x faster OLTP | AlloyDB |
| Global scale relational database, multi-region strong consistency | Cloud Spanner |
| Document database, mobile/web real-time sync | Firestore |
| High-throughput wide-column NoSQL at petabyte scale | Bigtable |
| Lift-and-shift MySQL/PostgreSQL from on-premises | Cloud SQL (use DMS for migration) |
| Existing PostgreSQL app with >500 GB data and heavy read/write mix | Consider AlloyDB |

---

## Important Constraints and Patterns

- **Single-region only**: Cloud SQL instances are single-region. For multi-region active-active, use Cloud Spanner or set up cross-region read replicas with manual failover.
- **Connection limits**: Each machine type has a maximum connection count (e.g., 1 vCPU = ~25 connections, 4 vCPU = ~100, 16 vCPU = ~400 for PostgreSQL). Use PgBouncer or Cloud SQL Proxy's connection pooling for high-concurrency apps.
- **Storage cannot shrink**: Auto-increase is permanent. Size your initial storage appropriately or use manual storage management.
- **HA failover drops connections**: Applications must implement reconnection logic. Connection pools (HikariCP, SQLAlchemy with pool_pre_ping) handle this automatically.
- **Maintenance windows**: Schedule in off-peak hours. Maintenance causes 1–7 minutes of downtime (or failover if HA is enabled).
- **Private IP requires VPC peering**: Once enabled, private IP persists; public IP can be disabled afterward.
- **IAM database authentication**: Available for PostgreSQL and MySQL (not SQL Server). Use IAM service accounts instead of password-based database users. Requires Cloud SQL IAM Logins flag enabled.
- **Max storage**: 64 TB per instance. For larger datasets, consider Cloud Spanner or split across multiple instances.
