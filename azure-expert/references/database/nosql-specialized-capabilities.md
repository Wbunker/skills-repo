# NoSQL & Specialized Databases — Capabilities Reference
For CLI commands, see [nosql-specialized-cli.md](nosql-specialized-cli.md).

## Azure Table Storage

**Purpose**: Simple, scalable key-value store for structured non-relational data. Part of Azure Storage accounts; extremely cost-effective for workloads requiring fast key-based access without complex queries or relational features.

### Data Model

```
Storage Account → Table → Entity
```

| Component | Description |
|---|---|
| **Table** | Container for entities; no schema enforcement beyond partition key and row key |
| **Entity** | Row; up to 252 custom properties + 3 system properties; max 1 MB per entity |
| **Partition Key** | Grouping key; entities with same partition key in same partition; max 1 MB per partition |
| **Row Key** | Unique within a partition; combination of PartitionKey + RowKey must be globally unique in table |
| **Timestamp** | System property; last modified time; not settable by user |

### Performance Characteristics

- Single entity read/write: single-digit millisecond latency
- Throughput: up to 20,000 entities/second per table (soft limit; raiseable)
- Storage: up to 500 TB per storage account; pay only for data stored
- **Batch transactions**: up to 100 entities per batch; all in same partition; atomic
- Supports OData query protocol; filter by partition key, row key, and custom properties
- Range queries on row key only within a partition (partition key must be specified for efficient queries)

### Access Patterns

| Pattern | Performance |
|---|---|
| Point lookup (exact PK + RK) | O(1); fastest |
| Range scan within partition (PK + RK range) | O(k); fast |
| Cross-partition scan (no PK filter) | O(n); full table scan; use sparingly |
| Property filter (no PK filter) | O(n); full scan; avoid for high-frequency queries |

### Ideal Use Cases

- Storing structured logs, telemetry, events by (date + device/userId) as partition scheme
- Web application user preferences and profile data
- Device registration and IoT metadata (small per-device records)
- Simple lookup tables (reference data, configuration)
- Cost-sensitive workloads where Cosmos DB Table API pricing is too high

### Azure Table Storage vs Cosmos DB Table API

| Feature | Azure Table Storage | Cosmos DB Table API |
|---|---|---|
| **Throughput** | Shared per account | Provisioned RU/s per table |
| **Latency** | Single-digit ms (same region) | Single-digit ms globally |
| **Global distribution** | No | Yes (multi-region) |
| **Automatic indexing** | Primary key only | All properties |
| **SLA** | 99.9% read/write | 99.999% (multi-region) |
| **Cost** | Very low | Higher |
| **Migration path** | Simple migration to Cosmos DB Table API | — |

- Use Cosmos DB Table API for global distribution, higher throughput SLAs, or secondary indexing
- Existing Table Storage SDKs work with Cosmos DB Table API with minimal code changes

---

## Azure Database for MariaDB (Legacy — Deprecated)

**Status**: Azure Database for MariaDB is scheduled for retirement on September 19, 2025. New workloads should not be deployed on MariaDB; existing workloads should migrate.

### Migration Recommendation

- Migrate to **Azure Database for PostgreSQL — Flexible Server** (preferred for most workloads)
- Migrate to **Azure Database for MySQL — Flexible Server** (if MySQL wire compatibility required)
- MariaDB is a MySQL fork; most MySQL-compatible applications work on MySQL Flexible Server

### Migration Path

1. Assess application compatibility: identify MariaDB-specific features (Aria storage engine, SEQUENCE objects, etc.)
2. Dump data using `mysqldump` from MariaDB
3. Restore to MySQL Flexible Server (adjust for syntax differences if any)
4. Update connection strings and test
5. Cutover: point DNS/connection string to new server

---

## Azure SQL Edge

**Purpose**: Lightweight, containerized SQL Server engine optimized for IoT edge devices and industrial scenarios. Runs on ARM and x64 hardware with as little as 500 MB RAM.

### Key Capabilities

| Feature | Description |
|---|---|
| **SQL Server compatibility** | T-SQL compatible; subset of SQL Server 2019 features |
| **Streaming** | Native T-SQL streaming (TSQL Streaming) for real-time data ingestion from sensors, MQTT, Kafka |
| **ML inference** | Run ONNX machine learning models natively with `PREDICT()` function |
| **Time series** | `DATE_BUCKET()` function for time-bucket aggregations; built-in for IoT time-series patterns |
| **Data sync** | Azure Data Factory integration; sync edge data to cloud SQL Server or SQL Database |
| **Container deployment** | Runs as Docker container; deployable via Azure IoT Hub / IoT Edge |
| **Small footprint** | <500 MB RAM minimum; runs on Raspberry Pi, ARM64, x64 |

### Use Cases

| Scenario | Description |
|---|---|
| **Manufacturing / Industrial IoT** | Collect and analyze sensor data at the factory floor; local analytics without cloud latency |
| **Retail edge** | Point-of-sale systems; offline-capable with cloud sync when connected |
| **Healthcare devices** | Local patient data processing; privacy-preserving edge analytics |
| **Predictive maintenance** | Run ML models on edge to predict equipment failure without sending all data to cloud |

### Deployment Models

- **Developer**: free; not for production; full feature access for development
- **Premium**: production-licensed; all features

### Architecture Pattern

```
Sensors / PLCs → Azure SQL Edge (edge device) → Azure IoT Hub → Azure SQL Database / Synapse Analytics (cloud)
```

- Edge processes and filters data locally; sends aggregated or relevant data to cloud
- ONNX models deployed from cloud to edge via IoT Hub twin properties or direct methods

---

## Azure Database Migration Service (DMS)

**Purpose**: Managed service for migrating databases from on-premises or other clouds to Azure database services. Supports both online (minimal downtime) and offline (offline cutover) migrations.

### Supported Migration Scenarios

| Source | Target | Mode |
|---|---|---|
| SQL Server (on-premises) | Azure SQL Database | Online / Offline |
| SQL Server (on-premises) | Azure SQL Managed Instance | Online / Offline |
| SQL Server (on-premises) | SQL Server on Azure VMs | Online / Offline |
| Oracle | Azure SQL Database | Offline |
| Oracle | Azure Database for PostgreSQL | Offline |
| MySQL / MariaDB | Azure Database for MySQL | Online / Offline |
| PostgreSQL | Azure Database for PostgreSQL | Online / Offline |
| MongoDB | Azure Cosmos DB (Mongo API) | Online / Offline |
| AWS RDS (MySQL, PostgreSQL, SQL Server) | Azure Database services | Online / Offline |

### DMS Architecture

| Component | Description |
|---|---|
| **DMS Instance** | Regional Azure resource; select SKU (Premium recommended for online migration) |
| **Project** | Migration project within DMS instance; defines source and target connections |
| **Activity (Task)** | Migration task within a project; can be assessment, schema migration, or data migration |
| **Integration Runtime** | Self-hosted IR for accessing on-premises sources via private network |

### Migration Modes

| Mode | Description | Downtime | Use Case |
|---|---|---|---|
| **Online** | Continuous Change Data Capture (CDC); minimal downtime cutover | Minutes | Production systems; low tolerance for downtime |
| **Offline** | Bulk data copy; cutover requires full downtime during migration | Hours–days | Non-production; small databases; scheduled maintenance windows |

### Online Migration Process (SQL Server → SQL MI)

1. Assess source database (Database Migration Assessment tool)
2. Create DMS instance and project
3. Run schema migration (structure only)
4. Start online data migration (full load + CDC)
5. Monitor replication lag (aim for <1 minute lag before cutover)
6. Initiate cutover: stop application writes → complete migration → redirect app to target
7. Validate data and application functionality

### Database Migration Assessment (DMA)

- Free standalone tool for assessing SQL Server databases before migration
- Reports: compatibility issues, feature parity gaps, performance considerations
- Download from Microsoft; run against on-premises SQL Server
- Available as Azure SQL Migration extension in Azure Data Studio (preferred)

---

## Important Patterns & Constraints

### Azure Table Storage

- Entity max size: 1 MB (including property names and values)
- Table name: 3–63 alphanumeric characters; must start with letter
- Property names case-sensitive; no spaces; avoid reserved names (PartitionKey, RowKey, Timestamp, etag)
- Batch operations (EntityGroupTransaction): all entities same partition; max 100 entities; max 4 MB batch size
- Row key and Partition key uniqueness: deleting + re-inserting same PK+RK within 30 seconds may fail (tombstone period)
- OData filter expressions: use `$filter=PartitionKey eq 'X' and RowKey eq 'Y'` for optimal performance

### Azure SQL Edge

- Not a full SQL Server replacement; missing features: replication subscriber (edge can push to cloud), Reporting Services, Analysis Services, full-text search, R/Python extensibility
- Container images: `mcr.microsoft.com/azure-sql-edge`; separate Developer and non-Developer images
- Connectivity: default SQL port 1433 mapped to host; configure SA password via environment variable
- Azure IoT Edge integration: deploy as IoT Edge module; manage via `edgeAgent` and `edgeHub`

### Azure Database Migration Service

- Premium SKU required for online migration (CDC); Standard SKU for offline only
- DMS subnet must be able to reach both source (on-premises via VPN/ExpressRoute) and target Azure service
- Source SQL Server must have CDC enabled at database level for online migration
- MongoDB to Cosmos DB: online migration supports Core (SQL) API as target; Mongo API supported offline
- DMS does not migrate SQL Server Agent jobs, linked servers, or instance-level objects — handle separately
- Large table migrations: partition by date or ID range for faster parallel load; configure in task settings
- Oracle migrations require Oracle Installation Client on DMS self-hosted integration runtime machine
