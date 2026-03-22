# Database Migration Service — Capabilities Reference
For CLI commands, see [dms-cli.md](dms-cli.md).

## Azure Database Migration Service (DMS)

**Purpose**: Fully managed service for migrating databases from on-premises or other clouds to Azure managed database services with minimal downtime. Handles schema migration, data migration, and change data capture for online migrations.

### Service Tiers

| Tier | Use Case | Throughput |
|---|---|---|
| **Standard (4 vCore)** | Small to medium databases; offline migrations | Up to 4 vCores for migration tasks |
| **Premium (4 vCore)** | Online migrations requiring CDC; larger databases | CDC-capable; up to 4 vCores |
| **Premium (8 vCore)** | High-throughput online migrations; large databases | Higher parallelism |

### Migration Types

| Type | Downtime | Mechanism | Use Case |
|---|---|---|---|
| **Offline (one-time)** | Full downtime during cutover | Bulk data copy; no sync after initial load | Dev/test; small databases; acceptable downtime window |
| **Online (minimal downtime)** | Minutes at cutover only | Initial load + CDC (Change Data Capture) sync | Production; zero/near-zero downtime requirement |

### Supported Migration Scenarios

#### SQL Server Migrations

| Source | Target | Online | Offline |
|---|---|---|---|
| SQL Server (on-prem) | Azure SQL Database | Yes | Yes |
| SQL Server (on-prem) | Azure SQL Managed Instance | Yes | Yes |
| SQL Server (on-prem) | SQL Server on Azure VM | No (use backup/restore) | Backup/restore |
| Amazon RDS SQL Server | Azure SQL Database | Yes | Yes |
| Amazon RDS SQL Server | Azure SQL Managed Instance | Yes | Yes |

#### Open Source Database Migrations

| Source | Target | Online | Offline |
|---|---|---|---|
| MySQL (on-prem/RDS) | Azure Database for MySQL | Yes | Yes |
| PostgreSQL (on-prem/RDS) | Azure Database for PostgreSQL | Yes | Yes |
| Oracle | Azure Database for PostgreSQL | Yes | Yes |
| MongoDB | Azure Cosmos DB for MongoDB | Yes | Yes |

#### Cache/NoSQL

| Source | Target | Notes |
|---|---|---|
| Redis (on-prem) | Azure Cache for Redis | Online migration via Redis replication |
| MongoDB | Azure Cosmos DB | DMS activity or native mongodump/mongorestore |

---

## Migration Process

### Pre-migration Steps

1. **Assessment**: Use Azure Migrate database assessment (replaces standalone DMA tool) or SQL Server Migration Assistant (SSMA) for Oracle/MySQL/PostgreSQL/Access → SQL
2. **SKU recommendation**: Azure Migrate provides target SKU recommendations based on workload performance
3. **Schema migration**: Use Database Schema Conversion Toolkit or SSMA to convert schema before data migration
4. **Networking**: DMS requires connectivity to source (via ExpressRoute, VPN, or firewall rules allowing DMS subnet)
5. **Prerequisite permissions**: Source DB user needs data read + CDC permissions; target needs DDL/DML permissions

### Online Migration CDC Requirements

| Requirement | SQL Server | MySQL | PostgreSQL |
|---|---|---|---|
| **CDC on source** | Enable SQL Server CDC on database | Enable binary logging (`binlog_format=ROW`) | Enable logical replication (`wal_level=logical`) |
| **Source permissions** | `db_owner` or `CONTROL DATABASE` | `REPLICATION SLAVE`, `REPLICATION CLIENT`, `SELECT` | `REPLICATION` privilege; SELECT on tables |
| **Target** | db_owner on target database | CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT | Same schema/table names; no active connections |

### Migration Activity States

`Waiting` → `Running` → `Ready to cutover` → `Completing cutover` → `Completed`

- **Ready to cutover**: All changes synced; DMS is in continuous sync mode; trigger cutover when ready
- **Cutover**: Stop writes to source; wait for final sync; DMS switches to completed
- **Post-migration**: Update connection strings; enable HA features; validate application

---

## Database Migration Assessment

### Azure Migrate Database Assessment (Portal-based)

- Discover SQL Server instances via Azure Migrate appliance
- Assess compatibility with Azure SQL DB / SQL MI / SQL Server on VM
- Reports: breaking changes, behavior changes, deprecated features
- Provides migration complexity score (ready / ready with conditions / not ready)

### SQL Server Migration Assistant (SSMA)

| Source | Target |
|---|---|
| Oracle | Azure SQL Database / SQL Managed Instance |
| MySQL | Azure SQL Database / SQL Managed Instance |
| PostgreSQL | Azure SQL Database / SQL Managed Instance |
| Microsoft Access | Azure SQL Database |
| SAP ASE | Azure SQL Database / SQL Managed Instance |
| DB2 | Azure SQL Database / SQL Managed Instance |

- Schema assessment and conversion
- Data type mapping
- Object-level compatibility report
- T-SQL conversion with error flagging
- Downloadable tool (Windows); not a cloud service

---

## SKU Recommendations

- Part of Azure Migrate database assessment workflow
- Collects performance counters (CPU, memory, disk I/O, log activity) from source SQL Server
- Recommends optimal Azure SQL DB, SQL MI, or SQL Server on VM SKU
- Considers: DTU vs vCore pricing, storage size, IOPS requirements, HA tier
- Output: Recommended SKU + monthly cost estimate per database
