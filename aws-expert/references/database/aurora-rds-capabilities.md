# AWS Aurora & RDS — Capabilities Reference
For CLI commands, see [aurora-rds-cli.md](aurora-rds-cli.md).

## Amazon Aurora

**Purpose**: MySQL- and PostgreSQL-compatible relational database engine purpose-built for the cloud; delivers up to 5× the throughput of MySQL and 3× the throughput of PostgreSQL on the same hardware.

### Key Concepts

| Concept | Description |
|---|---|
| **DB Cluster** | One writer instance + up to 15 Aurora Replicas sharing a single cluster volume |
| **Cluster Volume** | Distributed SSD storage spanning 3 AZs; 6 copies of data (2 per AZ); auto-grows up to 128 TiB |
| **Aurora Replica** | Read-only instance sharing cluster storage; failover target; replica lag typically in single-digit ms |
| **Aurora Serverless v2** | Fine-grained capacity scaling in increments of 0.5 ACUs; scales to zero; shares cluster with provisioned instances |
| **Aurora Global Database** | One primary region + up to 5 secondary regions; replication lag < 1 second; support for managed failover |
| **Backtrack** | Rewind a cluster to any point in time within the backtrack window (hours) without restoring from snapshot (Aurora MySQL only) |
| **Parallel Query** | Pushes query processing to the storage layer; improves analytical query performance without a separate analytics cluster |
| **I/O-Optimized** | Pricing configuration that includes I/O at no extra charge; cost-effective when I/O > 25% of total bill |
| **RDS Proxy (Aurora)** | Connection pooler for Aurora; reduces connection overhead for Lambda/serverless workloads |

### Endpoints

| Endpoint | Routes To | Use Case |
|---|---|---|
| **Cluster endpoint** | Current writer instance | All writes; failover-aware |
| **Reader endpoint** | Load-balanced across all Aurora Replicas | Read scale-out |
| **Instance endpoint** | Specific DB instance | Diagnostics, pinned reads |
| **Custom endpoint** | User-defined subset of instances | Route analytics to larger replicas |

### Key Features

| Feature | Description |
|---|---|
| **Storage replication** | 6 copies of data across 3 AZs; tolerates loss of 2 copies for writes, 3 for reads |
| **Automated failover** | Promotes a replica in < 30 seconds; no data loss for replica-based failover |
| **Aurora Serverless v2** | Scales in 0.5-ACU increments; mix with provisioned instances in same cluster |
| **Global Database** | Cross-region replication < 1 s; RPO near-zero; managed planned/unplanned failover |
| **Backtrack** | Rewind without restore; window up to 72 hours (MySQL only) |
| **Aurora ML** | Direct SQL queries to SageMaker (regression/classification) and Comprehend (sentiment analysis) |
| **Aurora Parallel Query** | Offloads full-table scan to storage layer; no ETL pipeline needed for mixed OLTP/analytics |
| **I/O-Optimized storage** | Flat pricing for predictable I/O-heavy workloads; saves cost vs standard when I/O > ~25% of bill |
| **Point-in-time restore** | Restore cluster to any second within backup retention window (1–35 days) |
| **Fast cloning** | Clone a cluster in minutes using copy-on-write; only changed pages are stored separately |

### When to Use Aurora

- Drop-in MySQL/PostgreSQL replacement with higher performance and availability requirements
- Need near-zero-RPO cross-region DR (Global Database)
- Serverless or variable-traffic applications (Aurora Serverless v2)
- Mixed OLTP + occasional analytics on same data (Parallel Query)
- Latency-sensitive apps where connection pooling matters (RDS Proxy)

---

## Amazon RDS

**Purpose**: Managed relational database service supporting six database engines; handles provisioning, patching, backups, and failover so teams focus on applications rather than DB administration.

### Supported Engines

| Engine | Notes |
|---|---|
| **MySQL** | Most common open-source RDBMS |
| **PostgreSQL** | Full-featured open-source RDBMS; best OSS Aurora analog |
| **MariaDB** | MySQL fork with additional storage engines |
| **Oracle** | Enterprise Oracle Database; Bring Your Own License (BYOL) or License Included |
| **Microsoft SQL Server** | Express, Web, Standard, Enterprise editions |
| **IBM Db2** | Standard, Advanced editions |

### Key Concepts

| Concept | Description |
|---|---|
| **DB Instance** | Isolated database environment running a single engine; the fundamental unit |
| **Multi-AZ DB Instance** | One primary + one synchronous standby in a different AZ; standby does NOT serve reads; automatic failover |
| **Multi-AZ DB Cluster** | One writer + two reader instances across three separate AZs; readers serve read traffic |
| **Read Replica** | Asynchronous copy of the primary; serves reads; can be cross-region; can be promoted |
| **RDS Proxy** | Fully managed connection pool; reduces connection overhead; integrates with Secrets Manager; IAM auth |
| **Parameter Group** | Container for DB engine configuration parameters; applied to DB instances |
| **Option Group** | Container for optional engine features (Oracle, SQL Server specific) |
| **Automated Backup** | Daily snapshot + transaction logs; enables point-in-time restore within retention window (0–35 days) |
| **DB Snapshot** | Manual, user-initiated snapshot; retained until explicitly deleted |

### Key Features

| Feature | Description |
|---|---|
| **Multi-AZ DB Instance** | Synchronous standby; automatic failover in 60–120 s; no data loss |
| **Multi-AZ DB Cluster** | Two readers in separate AZs; failover in < 35 s; readers offload read traffic |
| **Read Replicas** | Up to 15 replicas (MySQL/MariaDB); cross-region replicas for DR and latency |
| **RDS Proxy** | Pools and shares database connections; reduces failover time; Secrets Manager integration |
| **Performance Insights** | Database load visualization by wait event, SQL, user, host; 7-day free retention |
| **Enhanced Monitoring** | Real-time OS-level metrics (CPU per process, filesystem, network) at 1–60 s intervals |
| **Automated backups** | Continuous transaction log backups; restore to any second within retention window |
| **Storage autoscaling** | Automatically increases storage when free space is low (set a max threshold) |
| **Encryption at rest** | AES-256 via AWS KMS; must be enabled at creation; includes backups, replicas, snapshots |
| **IAM DB Authentication** | Authenticate to MySQL/PostgreSQL using IAM tokens instead of passwords |

### When to Use RDS

- Standard relational workloads where Aurora's cost premium isn't justified
- Engine-specific requirements: Oracle, SQL Server, Db2, or specific MySQL/PostgreSQL versions
- Lift-and-shift of on-premises relational databases
- Moderate-scale OLTP where managed operations are the primary requirement
