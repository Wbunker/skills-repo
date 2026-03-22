# Azure Database for PostgreSQL & MySQL — Capabilities Reference
For CLI commands, see [postgresql-mysql-cli.md](postgresql-mysql-cli.md).

## Azure Database for PostgreSQL — Flexible Server

**Purpose**: Fully managed open-source relational database service based on the community edition of PostgreSQL. Flexible Server architecture gives granular control over compute tiers, maintenance windows, and HA configuration while eliminating infrastructure management.

### Compute Tiers

| Tier | Description | vCores | Use Case |
|---|---|---|---|
| **Burstable** | B-series VMs; credit-based CPU; can burst above baseline | 1–2 vCores (B1ms, B2s, B2ms) | Dev/test, low-traffic apps, small production |
| **General Purpose** | D-series balanced compute/memory | 2–96 vCores | Most production workloads; web apps; SaaS |
| **Memory Optimized** | E-series high memory-to-vCore ratio | 2–96 vCores | High-throughput analytics, in-memory caching, large working sets (Redis-like PgSQL patterns) |

### Storage

- General Purpose SSD (P-series): 32 GiB – 32 TiB; IOPS scale with storage size
- Premium SSD v2 (preview): independent IOPS and throughput configuration; lower latency
- **Storage auto-grow**: automatically expands storage when approaching limit; enabled by default; cannot shrink
- **IOPS scaling**: separate from storage size on newer SKUs (configure IOPS independently)

### High Availability Options

| HA Mode | Description | RPO | RTO | AZ Required |
|---|---|---|---|---|
| **No HA** | Single server; restart if failure | Data loss risk | 60–120s | No |
| **Same-Zone HA** | Primary + standby in same AZ; synchronous replication | ~0 | 60–120s | No |
| **Zone-Redundant HA** | Primary + standby in different AZs; synchronous streaming replication | ~0 | <120s | Yes (multi-AZ region) |

- Standby is hot; not readable; automatic failover via DNS redirect
- Can enable/disable HA after server creation (brief downtime)
- Zone-redundant HA recommended for production in regions with AZs

### Read Replicas

- Asynchronous streaming replication from primary to up to 5 read replicas
- Replicas can be in same region or different regions (cross-region replicas)
- Replicas are readable; use for read offload (reporting, analytics) and DR
- Promote replica to standalone server (breaks replication); useful for major version migration
- **Virtual endpoints**: reader endpoint that automatically routes to readable replicas

### Major Version Upgrades

- In-place major version upgrade (e.g., PG 14 → PG 16) without data migration
- Internally uses `pg_upgrade`; downtime required (typically minutes)
- Test on a restore clone before upgrading production

### Built-in Extensions

| Extension | Purpose |
|---|---|
| **pgvector** | Vector similarity search; semantic search; RAG applications |
| **PostGIS** | Geospatial data types and functions |
| **pg_cron** | Schedule SQL jobs within PostgreSQL (cron syntax) |
| **pg_partman** | Partition management automation |
| **timescaledb** | Time-series data extension (available in selected versions) |
| **pg_stat_statements** | Query performance tracking; execution statistics |
| **pg_repack** | Online table and index reorganization without locks |
| **dblink** | Cross-database queries within same server |
| **uuid-ossp** | UUID generation functions |
| **citext** | Case-insensitive text type |

### PgBouncer (Built-in Connection Pooler)

- Built-in PgBouncer connection pooler; no separate deployment
- Transaction pooling mode (default): connections returned to pool between transactions
- Reduces connection overhead for high-concurrency applications (microservices, serverless)
- Enable via server parameters; access via PgBouncer port (6432)

### Network Access

| Mode | Description |
|---|---|
| **Private access (VNet injection)** | Server deployed in delegated subnet; no public IP; access only from VNet or peered networks |
| **Public access with firewall** | Public endpoint; restrict via IP firewall rules; Private Endpoint also supported |

- Private access recommended for production; simpler network security model
- Can add Private Endpoint to public-access servers for hybrid access
- Delegated subnet: `Microsoft.DBforPostgreSQL/flexibleServers`; minimum /28

### Automated Backups

- Automatic daily full backup + WAL (Write-Ahead Log) archiving
- Retention: 7–35 days (configurable)
- Backup redundancy: LRS or GRS (geo-redundant backup for cross-region restore)
- **Point-in-time restore (PITR)**: restore to any second within retention window; creates new server
- **Geo-restore**: restore from geo-redundant backup to different region; RPO ~1 hour

---

## Azure Database for PostgreSQL Citus (Distributed PostgreSQL)

**Purpose**: Distributed PostgreSQL using the Citus extension. Shards data across worker nodes for horizontal scale-out, enabling multi-tenant SaaS architectures and real-time analytical workloads.

### Architecture

```
Coordinator Node → Worker Nodes (shards distributed by distribution column)
```

| Component | Description |
|---|---|
| **Coordinator** | Routes queries; holds metadata; entry point for all connections |
| **Worker nodes** | Hold data shards; execute parallel query fragments |
| **Distribution column** | Column used to shard table (e.g., `tenant_id`); determines data placement |
| **Reference tables** | Small tables replicated to all workers; join with distributed tables |

### Use Cases

| Pattern | Description |
|---|---|
| **Multi-tenant SaaS** | Shard by `tenant_id`; queries stay local to shard; tenant isolation |
| **Real-time analytics** | Columnar storage (`create_columnar_table`); analytical queries parallelized across workers |
| **Time-series** | Combine with pg_partman for distributed time-partitioned tables |

### Key Features

- Columnar storage for append-only analytics tables (10x compression)
- Distributed `GROUP BY`, `DISTINCT`, `ORDER BY`, aggregates (pushed down to workers)
- Online rebalancing: add/remove worker nodes without downtime
- Co-location: related tables sharded on same column placed on same worker for local JOINs

---

## Azure Database for MySQL — Flexible Server

**Purpose**: Fully managed MySQL community edition service. Similar architecture to PostgreSQL Flexible Server with MySQL-specific features.

### Compute Tiers

| Tier | vCores | Use Case |
|---|---|---|
| **Burstable** | 1–2 vCores | Dev/test, low-traffic |
| **General Purpose** | 2–64 vCores | Most production workloads |
| **Business Critical** | 2–64 vCores | High memory, fast storage (NVMe), latency-sensitive |

### High Availability

| HA Mode | Description |
|---|---|
| **Same-Zone HA** | Primary + standby in same AZ; synchronous replication; automatic failover |
| **Zone-Redundant HA** | Primary + standby in different AZs; automatic failover; preferred for production |

### Key Features

| Feature | Description |
|---|---|
| **Read replicas** | Up to 5 async replicas; same or cross-region |
| **Binlog access** | Access MySQL binary log for CDC pipelines and replication to external systems |
| **ProxySQL** | Third-party proxy (deploy separately) for connection pooling and query routing |
| **InnoDB engine** | Default engine; ACID transactions; foreign keys |
| **Point-in-time restore** | Restore to any second within retention window (1–35 days) |
| **Slow query log** | Enable for performance troubleshooting via server parameters |

### Supported Versions

- MySQL 5.7, 8.0, 8.4 (versions track community releases)
- In-place major version upgrade: 5.7 → 8.0 supported (test thoroughly; breaking changes)

### Network Access

- Same as PostgreSQL Flexible Server: private access (VNet injection) or public access with firewall
- Delegated subnet: `Microsoft.DBforMySQL/flexibleServers`

---

## Microsoft Defender for Open-Source Databases

- Anomaly detection for PostgreSQL and MySQL Flexible Server
- Alerts: SQL injection, anomalous access patterns, privilege escalation, unusual location access
- Enabled per server via Microsoft Defender for Cloud
- Integrates with Azure Monitor and Security Center alerts

---

## Common Operational Patterns

### Connection Management

- PostgreSQL: use `max_connections` parameter carefully; each connection uses ~5–10 MB RAM; use PgBouncer (built-in) for pooling
- MySQL: configure `max_connections`; use connection pool in application (e.g., ProxySQL)

### Performance Tuning Parameters (PostgreSQL)

| Parameter | Description |
|---|---|
| `shared_buffers` | Memory for caching; typically 25% of total RAM |
| `effective_cache_size` | Estimate of OS + shared_buffers cache; affects query planner |
| `work_mem` | Memory per sort/hash operation; multiply by concurrent queries |
| `max_wal_size` | Size of WAL before checkpoint triggered |
| `autovacuum_*` | Tune aggressiveness of autovacuum for high-churn tables |

### Performance Tuning Parameters (MySQL)

| Parameter | Description |
|---|---|
| `innodb_buffer_pool_size` | Main buffer pool; set to 70–80% of RAM for dedicated DB servers |
| `innodb_log_file_size` | Redo log size; larger = fewer checkpoints; more crash recovery time |
| `query_cache_size` | Deprecated in MySQL 8.0; set to 0 |
| `max_connections` | Maximum concurrent connections |
| `long_query_time` | Threshold for slow query log (seconds) |

---

## Important Patterns & Constraints

- PostgreSQL and MySQL Flexible Servers cannot be downgraded to lower major versions
- Storage auto-grow cannot be disabled once enabled on MySQL Flexible Server
- Read replicas are eventually consistent; do not use for reads requiring strong consistency with primary
- Zone-redundant HA requires the region to have at least 2 AZs
- Private VNet access cannot be changed after server creation (public ↔ private not reversible)
- Citus coordinator node is a single point of contact; scale coordinator vCores for high-concurrency SaaS
- pg_cron jobs run as the superuser role; use with care for security; schedule low-frequency administrative tasks only
- PITR creates a **new server** — it does not restore in-place; plan application connection string updates accordingly
- pgvector queries: use IVFFlat or HNSW indexes for approximate nearest neighbor; exact search (`<->` operator without index) is O(n)
