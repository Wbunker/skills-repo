# Database Migration Service — Capabilities Reference

## Purpose

Database Migration Service (DMS) is Google Cloud's fully managed service for migrating relational databases to Cloud SQL, AlloyDB, and Cloud Spanner with minimal downtime. DMS handles the complexity of setting up replication, monitoring migration progress, and performing the final cutover. For heterogeneous migrations (Oracle → PostgreSQL), DMS provides a conversion workspace for schema and object transformation.

---

## Supported Migration Paths

| Source | Destination | Migration Type | Notes |
|---|---|---|---|
| MySQL (5.6, 5.7, 8.0) | Cloud SQL for MySQL | Homogeneous | Continuous CDC via binary log |
| PostgreSQL (9.4–15) | Cloud SQL for PostgreSQL | Homogeneous | Continuous CDC via logical replication (pglogical) |
| PostgreSQL (9.4–15) | AlloyDB for PostgreSQL | Homogeneous | Same as → Cloud SQL for PostgreSQL |
| SQL Server (2008–2019) | Cloud SQL for SQL Server | Homogeneous | One-time (dump+restore) or continuous (via log shipping preview) |
| Oracle (11g–19c) | Cloud SQL for PostgreSQL | Heterogeneous | Via Ora2Pg conversion; schema conversion workspace |
| Oracle (11g–19c) | AlloyDB for PostgreSQL | Heterogeneous | Same conversion path as → Cloud SQL PostgreSQL |
| On-prem MySQL/PostgreSQL | Cloud SQL | Homogeneous | Use IP allowlist, VPN, or SSH tunnel for connectivity |
| RDS MySQL/PostgreSQL (AWS) | Cloud SQL / AlloyDB | Homogeneous | Connect via public IP allowlist or Interconnect |
| Cloud SQL (cross-version) | Cloud SQL | Homogeneous | Upgrade MySQL 5.7 → 8.0 or PostgreSQL 13 → 15 |

**Note on Spanner**: Database Migration Service does not directly migrate to Spanner. Use the **Spanner Migration Tool** (Harbourbridge) for Oracle, MySQL, PostgreSQL, and SQL Server → Spanner migrations.

---

## Migration Types

### One-Time Migration (Dump and Restore)

- Full dump of source database, transfer to destination, restore.
- Source database remains live during migration; the destination receives a point-in-time snapshot.
- Downtime required: application must stop writes before final cutover, or accept some data loss.
- Use for: small databases, tolerance for downtime, SQL Server (CDC preview only).

### Continuous Migration (CDC)

- Initial full load, then continuous replication of changes using Change Data Capture (CDC).
- Minimal downtime: application remains live; destination stays in sync.
- Cutover: stop writes to source, wait for destination to catch up, promote destination, redirect application.
- Typical downtime: seconds to minutes for the cutover step.
- Uses:
  - MySQL: binary log replication
  - PostgreSQL: logical replication via `pglogical` extension or native logical replication slots (PostgreSQL 10+)
  - Oracle: LogMiner or Redo log reading via Ora2Pg

---

## Connection Methods

| Method | Description | When to Use |
|---|---|---|
| IP allowlist | Add DMS service IP ranges to source database's firewall. | Source accessible on internet; Cloud SQL source. |
| Forward-SSH tunnel | DMS connects through an SSH bastion host to reach source. | Source behind firewall; SSH jumphost available. |
| VPC peering | Source reachable via Google Cloud VPC peering. | Source in another GCP VPC; no public access. |
| Reverse-SSH tunnel | Source initiates an SSH tunnel to DMS; DMS connects back through it. | Source cannot be reached from GCP; source initiates outbound only. |
| Private connectivity (PSC/VPN/Interconnect) | Source reachable via Cloud VPN or Cloud Interconnect. | On-prem source over dedicated connectivity. |

---

## Connection Profiles

A connection profile stores the connection settings for a source or destination database:

- Source profile: endpoint, port, credentials, SSL certificates
- Destination profile: Cloud SQL instance or AlloyDB cluster reference
- Profiles are reusable across migration jobs

---

## Migration Job Lifecycle

```
1. Create source connection profile
2. Create destination connection profile (or let DMS create Cloud SQL instance)
3. Create migration job (select source, destination, migration type, objects to migrate)
4. Verify migration job (DMS checks connectivity, permissions, binary log settings)
5. Start migration job
   a. Full dump phase: copies all existing data
   b. CDC phase: continuously applies changes from source
6. Monitor replication lag (should approach 0 before cutover)
7. Promote migration job (cutover):
   a. Stop writes to source application
   b. DMS verifies all changes applied
   c. Destination is promoted to a standalone Cloud SQL / AlloyDB instance
   d. Update application connection string to destination
   e. Old source remains unchanged (can be decommissioned after validation)
```

---

## Heterogeneous Migration: Oracle → PostgreSQL

Oracle to PostgreSQL migrations require schema and data type conversion because Oracle and PostgreSQL differ significantly.

### Conversion Workspace

The DMS conversion workspace provides:
- **Schema import**: connects to Oracle, extracts schema (tables, indexes, constraints, views, procedures, functions, triggers)
- **Automatic conversion**: converts Oracle SQL to PostgreSQL SQL where possible
- **Conversion issues**: flags objects that cannot be automatically converted (Oracle-specific PL/SQL, specific data types)
- **Manual editing**: edit the generated PostgreSQL DDL within the workspace
- **Semantic mapping rules**: define custom mappings (e.g., rename schemas, transform data types)
- **Assessment report**: summary of conversion readiness (what converted automatically, what needs manual work)

### Common Oracle → PostgreSQL Conversion Issues

| Oracle Construct | PostgreSQL Equivalent | Notes |
|---|---|---|
| `NUMBER(p,s)` | `NUMERIC(p,s)` | Auto-converted |
| `VARCHAR2(n)` | `VARCHAR(n)` | Auto-converted |
| `DATE` (includes time) | `TIMESTAMP` | Oracle DATE includes time; PostgreSQL DATE is date-only |
| `ROWNUM` | `ROW_NUMBER()` or `LIMIT` | Requires manual rewrite |
| `SEQUENCE.NEXTVAL` | `nextval('sequence')` | Partially auto-converted |
| PL/SQL packages | Multiple PL/pgSQL functions | Requires manual work |
| Oracle-specific functions | PostgreSQL equivalents | Requires manual mapping |
| Partitioning syntax | PostgreSQL partitioning | Syntax differs; partial auto-conversion |
| `CONNECT BY` (hierarchical queries) | Recursive CTEs | Manual rewrite required |
| Database links | Foreign data wrappers (FDW) | Manual configuration |

---

## Datastream (CDC Streaming to BigQuery)

Datastream is a related service for streaming database changes to Google Cloud — used when the destination is BigQuery or Cloud Storage rather than Cloud SQL.

| Feature | Description |
|---|---|
| Sources | MySQL, PostgreSQL, Oracle, SQL Server |
| Destinations | BigQuery (direct), Cloud Storage (in Avro or JSON format) |
| Protocol | CDC (binary log / logical replication / Redo log) |
| Latency | Near real-time (seconds to minutes) |
| Use case | Real-time analytics, data lake ingestion, event-driven pipelines |
| vs. DMS | DMS migrates to Cloud SQL/AlloyDB; Datastream streams changes to BigQuery/GCS for analytics |

---

## Pre-Migration Requirements

### MySQL Source

- Binary log must be enabled: `binlog_format = ROW`
- `binlog_row_image = FULL`
- `expire_logs_days` or `binlog_expire_logs_seconds` set to retain logs for migration duration
- DMS service account must have `REPLICATION SLAVE`, `REPLICATION CLIENT` grants

### PostgreSQL Source

- `wal_level = logical`
- `max_replication_slots` ≥ 1 (DMS creates a replication slot)
- `max_wal_senders` ≥ 1
- Replication permission for the DMS user: `GRANT REPLICATION` or superuser

### Oracle Source (for heterogeneous)

- `ARCHIVELOG` mode enabled
- Supplemental logging enabled: `ALTER DATABASE ADD SUPPLEMENTAL LOG DATA`
- DMS user must have `SELECT ANY TRANSACTION`, `SELECT ANY TABLE`, `LOGMINING` privileges
- Oracle 11g minimum; 12c+ recommended

---

## Post-Migration Validation

After promoting the migration job, validate the destination:

1. **Row count comparison**: compare row counts in source and destination tables
2. **Checksum comparison**: for critical tables, compare checksums or use DMS data validation feature
3. **Application smoke test**: run key application queries against the destination
4. **Performance testing**: run production-level queries; check query plans; add indexes as needed
5. **Constraints and sequences**: verify foreign key constraints, sequences start values, and triggers
6. **SSL certificates**: update application connection strings with destination credentials

---

## Important Constraints

- **Destination must be pre-created or auto-created by DMS**: For Cloud SQL destinations, DMS can auto-create the instance or use a pre-existing one.
- **Replication user privileges**: The source database user used for migration must have replication permissions. Do not use the application user.
- **Binary log retention**: MySQL source must retain binary logs for the entire duration of the migration. Set retention to at least 7 days.
- **Large objects**: Oracle LOBs (BLOB, CLOB) may have conversion limitations. Test large object migration separately.
- **One-to-one database mapping**: A migration job migrates one source database to one destination. For instances with multiple databases, create separate migration jobs per database.
- **Network latency**: High latency between source and DMS can increase replication lag. Use private connectivity (VPN, Interconnect) for large databases.
- **Downtime for promotion**: Even with continuous migration, a short downtime window is needed to stop writes and promote. Plan for this in your cutover runbook.
- **Spanner not supported**: For Spanner migrations, use the separate Spanner Migration Tool (Harbourbridge): `github.com/GoogleCloudPlatform/spanner-migration-tool`.
