# AlloyDB — Capabilities Reference

## Purpose

AlloyDB for PostgreSQL is Google Cloud's fully managed, PostgreSQL-compatible database built for demanding enterprise workloads. It delivers up to 4x faster OLTP throughput and up to 100x faster analytical query performance compared to standard PostgreSQL, achieved through a disaggregated storage architecture, an in-memory columnar engine, and a custom storage layer with 6-way replication.

AlloyDB is wire-compatible with PostgreSQL — existing PostgreSQL drivers, tools, and extensions work without modification.

---

## Core Concepts

| Concept | Description |
|---|---|
| Cluster | Top-level resource. Contains instances and represents a single database system. Tied to a VPC network and region. |
| Primary instance | The read/write database instance within a cluster. Handles all DML operations. |
| Read pool instance | Horizontally scalable group of read-only instances. Pool size (number of nodes) is adjustable. Traffic is distributed across pool nodes automatically. |
| Secondary cluster | A cross-region replica cluster for disaster recovery. Can be promoted to primary. |
| AlloyDB Auth Proxy | Connection proxy similar to Cloud SQL Auth Proxy. Handles IAM authentication and SSL. Recommended connection method. |
| Columnar engine | In-memory analytical acceleration layer. Automatically detects and caches frequently accessed data in a columnar format. No query rewrites needed — the query planner routes to columnar engine transparently. |
| AlloyDB Omni | Self-managed AlloyDB that runs on any Kubernetes cluster (on-premises, other clouds, GKE). Uses the same storage engine and columnar engine. |
| AlloyDB AI | Integrated AI capabilities: pgvector extension, embedding generation functions, model endpoint integration, approximate nearest neighbor (ANN) search. |

---

## Architecture

AlloyDB separates compute and storage:

- **Compute layer**: PostgreSQL-compatible database engine running on GCE VMs (primary and read pool instances).
- **Storage layer**: Distributed, regional storage service with 6-way replication across 3 zones in the region. Independent of compute — storage persists if all compute instances fail.
- **Log processing service**: Separate service processes WAL records and applies them to storage asynchronously, offloading work from the primary instance.

This architecture means:
- Read pool instances access the same storage as the primary — no replication lag for reads (unlike Cloud SQL replicas which use async replication).
- PITR is always available (continuous WAL archiving to storage).
- Storage scales independently of compute.

**Columnar engine operation**: Monitors query patterns; automatically populates an in-memory column store for tables/columns accessed by analytical queries. The PostgreSQL query planner detects when a query can be served by the columnar engine and routes accordingly. Cache size is configurable (default: up to 30% of instance memory or an explicit size).

---

## Performance Characteristics

| Metric | AlloyDB | Cloud SQL PostgreSQL |
|---|---|---|
| OLTP throughput | 4x faster | Baseline |
| Analytical queries | Up to 100x faster (columnar engine) | Baseline |
| Failover RTO | < 60 seconds | ~60 seconds |
| RPO | 0 (synchronous storage) | 0 (regional persistent disk for HA) |
| Max instance size | 128 vCPU / 864 GB RAM | 96 vCPU / 624 GB RAM |

---

## High Availability

- HA is built into the primary instance architecture — no separate HA configuration step (unlike Cloud SQL's `--availability-type=REGIONAL`).
- The primary instance automatically fails over to a replica within the cluster in under 60 seconds.
- RPO = 0 because storage is synchronous and shared — the failover target reads from the same storage layer.
- During failover, in-flight transactions that were not committed are rolled back.

---

## Read Pool

- Read pool instances share the same storage as the primary — they see committed writes immediately (no async replication lag for committed data).
- Pool size: 1–20 nodes. Each node is a full instance. AlloyDB load-balances connections across nodes.
- Read pool instances are in the same region as the primary cluster.
- Use read pool for:
  - Read-scaling (reporting, analytics, BI tools)
  - Offloading analytical queries from the primary
  - Serving read traffic during primary maintenance

---

## Secondary Cluster (Cross-Region DR)

- A secondary cluster is a full copy of the primary cluster in a different region.
- Replication is asynchronous (log-based) — some replication lag expected.
- Secondary cluster has its own primary instance (read-only until promoted).
- Promotion: promotes the secondary cluster to an independent primary. The original primary cluster is unaffected.
- Use for: regional DR, data sovereignty (read-only copy in a specific region).

---

## AlloyDB AI

AlloyDB AI integrates vector search and model inference directly into the database:

| Feature | Description |
|---|---|
| pgvector extension | Full pgvector support for storing and querying vector embeddings |
| `google_ml_integration` extension | Call Vertex AI models or any HTTP endpoint from SQL |
| Embedding generation | `embedding()` function: `SELECT embedding('text-embedding-004', 'my text')` |
| ANN index | ScaNN-based approximate nearest neighbor index on vector columns for production-scale vector search |
| Model endpoint registration | Register Vertex AI model endpoints; call via SQL function |

Example: Generate embeddings and find similar rows:
```sql
-- Store embeddings
UPDATE products SET embedding_col = embedding('text-embedding-004', description);

-- Nearest neighbor search
SELECT id, description
FROM products
ORDER BY embedding_col <=> embedding('text-embedding-004', 'red leather jacket')
LIMIT 10;
```

---

## AlloyDB Omni

AlloyDB Omni runs on Kubernetes (any environment) and provides the same PostgreSQL-compatible engine with the columnar engine and AlloyDB AI features, without the managed cloud infrastructure.

- Deployed as a container/Helm chart.
- Connects to AlloyDB AI on Vertex AI (requires network connectivity to GCP).
- Use for: on-premises requirements, multi-cloud deployments, local development matching production.

---

## Connection Methods

| Method | Description |
|---|---|
| AlloyDB Auth Proxy | Recommended. Same pattern as Cloud SQL Auth Proxy. IAM-based authentication, handles SSL. |
| Private Service Access | AlloyDB cluster is in a VPC peering with your VPC. Direct private IP connectivity. |
| AlloyDB Connector libraries | Java, Python, Go connectors embedding proxy logic. For Cloud Functions, Cloud Run without sidecar. |

AlloyDB does not support public IP access. All connections must be through Private Service Access or the Auth Proxy (which routes through the PSA connection).

**Connection string via Auth Proxy** (after starting proxy on port 5432):
```
postgresql://user:password@127.0.0.1:5432/dbname
```

---

## Backups and PITR

- **Continuous backups**: WAL-based continuous backup to Google-managed storage. Always enabled. PITR is always available.
- **Automated backups**: Daily full backups. Retention: 1–365 days (default 14 days).
- **On-demand backups**: Manual backup snapshots.
- **PITR**: Restore to any second within the retention window. Creates a new cluster.
- **Cross-region restore**: Restore a backup to a different region (no direct cross-region replication of backups; restore to a new cluster).

---

## Extensions

AlloyDB supports all PostgreSQL extensions plus AlloyDB-specific ones:

- All standard PostgreSQL extensions (PostGIS, pg_cron, pglogical, etc.)
- `pgvector`: vector similarity search
- `google_ml_integration`: AI model integration
- `alloydb_scann`: ScaNN ANN index for vector search

---

## Cloud SQL PostgreSQL vs. AlloyDB — Decision Guide

| Factor | Use Cloud SQL | Use AlloyDB |
|---|---|---|
| Cost sensitivity | Lower cost | Higher cost (premium for performance) |
| OLTP performance | Standard PostgreSQL throughput sufficient | Need 2–4x+ higher throughput |
| Analytical queries | Separate BigQuery for analytics | In-database analytics via columnar engine |
| Database size | Up to 64 TB | Up to 64 TB (same storage limit) |
| AI/vector search | pgvector supported | pgvector + google_ml_integration + ScaNN |
| Connection method | Cloud SQL Auth Proxy or PSA | AlloyDB Auth Proxy or PSA |
| Read scaling | Async read replicas (slight lag) | Read pool (same storage, no lag) |
| Multi-region DR | Cross-region read replicas | Secondary cluster |
| Compatibility | Full PostgreSQL | Full PostgreSQL (wire-compatible) |
| Self-managed option | Cloud SQL does not have an Omni version | AlloyDB Omni for on-prem/other clouds |

---

## Important Constraints

- **Single region per cluster**: Primary and read pool are in one region. Use secondary clusters for cross-region.
- **Private networking only**: No public IP. Requires VPC with Private Service Access configured.
- **Minimum instance size**: 2 vCPUs (no shared-core option). AlloyDB targets production workloads, not dev/test.
- **PostgreSQL versions**: AlloyDB tracks current PostgreSQL major versions. Check documentation for currently supported versions (typically one major version behind latest stable).
- **Connection limits**: Similar to PostgreSQL; use pgBouncer or AlloyDB's built-in connection pooling.
