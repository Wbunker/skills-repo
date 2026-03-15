# AWS Database Migration — Capabilities Reference

For CLI commands, see [database-migration-cli.md](database-migration-cli.md).

## AWS Database Migration Service (DMS)

**Purpose**: Managed service to migrate databases to AWS with minimal downtime. Supports homogeneous (same engine) and heterogeneous (different engines) migrations. Can run as a one-time full load or maintain ongoing change data capture (CDC) replication.

### Core Concepts

| Concept | Description |
|---|---|
| **Replication instance** | Managed EC2-like instance that runs the migration engine; you choose the instance class and Multi-AZ |
| **Endpoint** | Connection definition for a source or target database (engine type, host, port, credentials) |
| **Replication task** | Defines what to migrate: which endpoint pair, which tables/schemas, task type, table mappings |
| **Table mappings** | JSON rules specifying which schemas/tables to include/exclude and how to transform them |
| **Change Data Capture (CDC)** | Reads database transaction logs to replicate ongoing changes after full load |
| **DMS Fleet Advisor** | Agentless discovery tool; scans your network for database servers and generates migration recommendations |
| **Serverless replication** | Auto-scales replication capacity; no instance provisioning required; pay per DPU-hour |
| **DMS Schema Conversion** | Built-in schema conversion (simpler than SCT; good for homogeneous and simple heterogeneous migrations) |

### Task Types

| Task Type | Description | Use Case |
|---|---|---|
| **Full load** | One-time copy of all selected data | Initial bulk migration; source stays online but changes not captured |
| **CDC only** | Replicate changes from a specific point in time | Catch up after a manual full load; ongoing replication |
| **Full load + CDC** | Full load followed immediately by CDC | Zero-downtime migration; start replication, full load, then CDC catches up |

### Supported Source Engines

| Engine | Full Load | CDC |
|---|---|---|
| Oracle | Yes | Yes (LogMiner or Binary Reader) |
| SQL Server | Yes | Yes (MS-CDC or backup) |
| MySQL / MariaDB | Yes | Yes (binlog) |
| PostgreSQL | Yes | Yes (logical replication / pglogical) |
| Aurora MySQL | Yes | Yes |
| Aurora PostgreSQL | Yes | Yes |
| IBM Db2 LUW | Yes | Yes |
| SAP ASE (Sybase) | Yes | Yes |
| MongoDB / DocumentDB | Yes | Yes (change streams) |
| Amazon S3 | Yes | Yes (new files as CDC) |
| Microsoft Azure SQL | Yes | Yes |
| Google Cloud SQL (MySQL, PostgreSQL) | Yes | Yes |

### Supported Target Engines

| Engine | Notes |
|---|---|
| Amazon Aurora (MySQL, PostgreSQL) | Common target for open-source migrations |
| Amazon RDS (all engines) | Any RDS-supported engine |
| Amazon Redshift | OLAP target; S3 staging used automatically |
| Amazon DynamoDB | NoSQL target; JSON transformation rules required |
| Amazon S3 | Data lake landing zone; Parquet, CSV, JSON output |
| Amazon OpenSearch | Full-text search target |
| Amazon Kinesis Data Streams | Streaming CDC into real-time pipelines |
| Amazon Neptune | Graph database target |
| Kafka (MSK or self-managed) | CDC streaming target |
| Any of the source engines above | Bidirectional and same-engine supported |

### Replication Instances

| Class | Use Case |
|---|---|
| `t3.micro` / `t3.medium` | Dev/test, small migrations |
| `r5.large` / `r5.xlarge` | Standard production migrations |
| `r5.2xlarge`+ | High-throughput migrations with LOB columns or heavy CDC |

**Multi-AZ replication instances**: AWS maintains a standby replica in a different AZ. Failover is automatic. Use for production migrations where availability matters.

**Storage**: Default 50 GB; increase if large LOB data or long replication runs. Allocated as EBS `gp2`/`gp3`.

### Endpoint Configuration Key Settings

| Setting | Description |
|---|---|
| **Server name / port** | Database host and port |
| **Username / password** | Database credentials (stored encrypted in DMS) |
| **SSL mode** | none, require, verify-ca, verify-full |
| **Extra connection attributes (ECA)** | Engine-specific tuning parameters (e.g., `parallelLoadThreads`, `targetDbType`, `cdcStartPosition`) |
| **Secrets Manager integration** | Store endpoint credentials in Secrets Manager; DMS retrieves at runtime |
| **Oracle-specific**: `useLogminerReader` | Switch between LogMiner and Binary Reader for Oracle CDC |
| **PostgreSQL-specific**: `pluginName` | `pglogical` or `test_decoding` for CDC slot type |
| **SQL Server-specific**: `readBackupOnly` | Read from backup for minimal impact on source |

### Table Mapping Rules

Table mappings use a JSON rules engine:

- **Selection rules**: Include or exclude schemas, tables, columns using wildcards
- **Transformation rules**: Rename schemas/tables/columns, add columns, convert to uppercase/lowercase, remove prefix/suffix
- **Filter rules**: Row-level filtering by column value (e.g., only migrate rows where `region = 'US'`)

### LOB (Large Object) Handling

| Mode | Description |
|---|---|
| **Limited LOB mode** | Truncates LOBs to a max size (default 32 KB); fastest |
| **Full LOB mode** | Migrates full LOB size; slowest; inline fetch from source |
| **Inline LOB mode** | Fetches LOBs in same row pass if under threshold; hybrid |

### DMS Fleet Advisor

- **Purpose**: Discovery and assessment before migration planning
- Deploys a lightweight collector agent on a Windows server in your network
- Scans network for Oracle, SQL Server, MySQL, PostgreSQL, and other databases
- Generates inventory of database versions, schemas, sizes, object counts
- Produces migration recommendations (target engine, DMS task feasibility)
- Collector data stored in S3; analysis in DMS Fleet Advisor console

### Serverless Replication

- No replication instance to provision or manage
- Specify min/max capacity units (DPUs: 1–256)
- DMS auto-scales within the range based on workload
- Billed per DPU-hour consumed
- Supports full load, CDC, and full load + CDC
- Available for most engine pairs; check current docs for exceptions
- Uses same endpoint and table mapping concepts as instance-based DMS

### DMS Schema Conversion (Console-based)

- Embedded in DMS console (separate from SCT desktop tool)
- Suitable for homogeneous migrations and simpler heterogeneous migrations
- Converts DDL (tables, views, indexes, stored procedures) automatically
- Assessment report shows conversion success rate and manual items
- Integrates directly with DMS migration tasks

---

## AWS Schema Conversion Tool (SCT)

**Purpose**: Desktop application (Java-based; runs on Windows, Linux, macOS) for assessing and converting database schemas and code from one engine to another before migration. Handles complex schema objects that DMS cannot automatically convert.

### Core Concepts

| Concept | Description |
|---|---|
| **Project** | SCT workspace connecting a source database and target database |
| **Assessment report** | HTML/PDF report showing object conversion success rate, incompatible objects, estimated effort |
| **Converted schema** | DDL scripts generated for the target database; can be applied directly or saved to files |
| **Extension packs** | AWS-provided stored procedure libraries that emulate source database functionality on the target (e.g., Oracle built-ins on PostgreSQL) |
| **Action items** | Objects SCT cannot auto-convert; require manual remediation; categorized by severity |

### OLTP Conversion Paths (Supported)

| Source | Target |
|---|---|
| Oracle | Amazon Aurora PostgreSQL, Amazon RDS for PostgreSQL, Aurora MySQL, RDS MySQL |
| Oracle | Amazon RDS for Oracle (same engine, change options) |
| SQL Server | Aurora MySQL, Aurora PostgreSQL, RDS PostgreSQL, RDS MySQL |
| MySQL | Aurora PostgreSQL, RDS PostgreSQL |
| PostgreSQL | Aurora MySQL, RDS MySQL, Aurora PostgreSQL (version upgrade) |
| IBM Db2 LUW | Aurora MySQL, Aurora PostgreSQL, RDS PostgreSQL |
| SAP ASE | Aurora MySQL, Aurora PostgreSQL, RDS MySQL |

### OLAP Conversion Paths (Data Warehouse)

| Source | Target |
|---|---|
| Oracle Data Warehouse | Amazon Redshift |
| Teradata | Amazon Redshift |
| Microsoft SQL Server DW | Amazon Redshift |
| Netezza | Amazon Redshift |
| Greenplum | Amazon Redshift |
| Vertica | Amazon Redshift |
| IBM Db2 DW | Amazon Redshift |

### Assessment Report Details

The SCT assessment report includes:
- **Conversion summary**: Percentage of objects automatically converted
- **Action items by category**: Storage procedures, functions, triggers, views, indexes
- **Severity levels**: Simple (auto-converted), Medium (minor edits), High (significant rewrite), Critical (manual only)
- **Estimated effort**: Hours/days of manual work for unconverted items
- **Extension pack recommendations**: Which AWS extension packs to install on the target

### Extension Packs

Extension packs are sets of schemas, functions, and procedures installed on the target database that replicate proprietary source database behaviors:

| Source | Extension Pack Purpose |
|---|---|
| Oracle | `DBMS_*` package equivalents for PostgreSQL, sequence emulation, date functions |
| SQL Server | `sys.*` compatibility views, `CONVERT()` equivalents for PostgreSQL/MySQL |
| Teradata | Date arithmetic, string functions for Redshift |

Extension packs are installed automatically by SCT when applying the converted schema.

### SCT Data Extraction Agents

For large data warehouse migrations (especially Teradata → Redshift), SCT provides **Data Extraction Agents**:
- Java agents installed on servers close to the source
- Extract data in parallel, compress, and upload to S3
- Redshift then loads from S3 via COPY command
- Agent tasks managed from SCT console
- Supports partitioned extraction for very large tables

### When to Use SCT vs DMS Schema Conversion

| Scenario | Tool |
|---|---|
| Complex stored procedures, triggers, functions | SCT desktop (richer IDE, manual editing) |
| Simple schema migration, few custom objects | DMS Schema Conversion (console) |
| Data warehouse migration (Teradata, Netezza) | SCT desktop only |
| Ongoing schema changes during live migration | DMS Schema Conversion |
| Detailed assessment report for project planning | SCT desktop |
