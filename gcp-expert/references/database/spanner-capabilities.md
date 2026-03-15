# Cloud Spanner — Capabilities Reference

## Purpose

Cloud Spanner is Google's fully managed, horizontally scalable, globally distributed relational database. It combines the consistency and SQL semantics of a relational database with the horizontal scale and global distribution of a NoSQL system. Spanner provides external consistency (a stronger form of serializability), enabling ACID transactions across rows, tables, and databases — even across continents.

Use Spanner when you need a relational schema, strong consistency, and the ability to scale out compute and storage independently of each other, across one or more regions.

---

## Core Concepts

| Concept | Description |
|---|---|
| Instance | The top-level resource. Represents allocated compute capacity (nodes or processing units). Instance config determines regional or multi-regional placement. |
| Database | A schema and data container within an instance. A single instance can hold multiple databases. |
| Table | Relational table with a primary key. Schema is defined via DDL. |
| Interleaved table | A child table physically co-located with its parent table. Rows with the same parent key are stored together on the same split. Eliminates cross-split joins for parent-child lookups. |
| Split | Spanner automatically shards tables into splits (ranges of rows) and distributes them across nodes. Spanner manages splits automatically. |
| Node | A unit of compute capacity. 1 node = 1000 processing units. Provides ~2 TB of storage and ~2,000 QPS of writes or ~10,000 QPS of reads. |
| Processing unit (PU) | Fine-grained capacity unit. Minimum 100 PUs. Use PUs for smaller databases to avoid paying for a full node. |
| Commit timestamp | `PENDING_COMMIT_TIMESTAMP()` — a column type that automatically records the transaction commit time. Useful for change data capture and audit tables. |
| Read-write transaction | Full ACID transaction with external consistency. Uses pessimistic locking (two-phase). |
| Read-only transaction | Consistent snapshot read without locks. No commit required. Cheaper and does not contend with writes. |
| Stale read | A read at a specified point in the past (bounded staleness or exact staleness). Avoids leader communication; lower latency; may see slightly outdated data. |
| Multi-region config | An instance configuration that replicates data across multiple geographic regions. Provides higher availability and lower read latency globally, at higher cost. |
| TrueTime | Google's globally synchronized time service (atomic clocks + GPS). Enables Spanner's external consistency guarantee. Not directly exposed to users but underpins all Spanner transactions. |

---

## Instance Capacity: Nodes vs. Processing Units

| Capacity Unit | Size | When to Use |
|---|---|---|
| Processing Unit (PU) | 100 PUs minimum | Databases < 100 GB or dev/test; cost-efficient for small workloads |
| Node | 1000 PUs | Production databases; easier to reason about at scale |

**Scaling**: Spanner scales linearly. Doubling nodes doubles throughput. Storage scales automatically — you do not provision storage separately.

**Storage included**: 1 node includes ~2 TB of storage. Additional storage is charged per GB beyond the included amount.

---

## Instance Configurations (Regional and Multi-Region)

### Regional Configurations

| Config | Region |
|---|---|
| regional-us-central1 | Iowa |
| regional-us-east1 | South Carolina |
| regional-europe-west1 | Belgium |
| regional-asia-east1 | Taiwan |
| (many others) | See full list: `gcloud spanner instance-configs list` |

Regional instances have one leader region. All writes go to the leader; reads can be served from any replica.

### Multi-Region Configurations

| Config | Coverage | Leader Regions |
|---|---|---|
| nam4 | North Virginia + North Carolina | Two US regions |
| nam6 | Six US regions | Two leader regions |
| eur3 | Belgium + Netherlands | Two EU regions |
| eur5 | Five EU regions | Two leader regions |
| asia1 | Tokyo + Osaka | Two Asia-Pacific regions |
| nam-eur-asia1 | North America + Europe + Asia | Global |
| nam11 | Eleven North America regions | ... |

Multi-region instances have two voting regions (leaders) for higher availability. They provide 99.999% SLA. Write latency is higher because Spanner must achieve quorum across regions (network round-trip). Read latency can be lower for global users because reads can be served locally.

---

## Schema Design

### Primary Key Best Practices

Spanner auto-shards tables by primary key range. Monotonically increasing primary keys (auto-increment integers, sequential timestamps) create write hotspots — all new rows land on the same split.

**Avoid**: `INT64 PRIMARY KEY` with auto-increment. `TIMESTAMP PRIMARY KEY` written in order.

**Prefer**:
- UUID v4 (random distribution across splits)
- Hash prefix: prepend `FARM_FINGERPRINT(user_id) % 1000` to PK
- Reverse timestamp for descending time-series
- Bit-reversed sequence: Spanner supports `GET_NEXT_SEQUENCE_VALUE(SEQUENCE seq)` with bit-reversal

### Interleaved Tables

```sql
CREATE TABLE Orders (
  CustomerId INT64 NOT NULL,
  OrderId    INT64 NOT NULL,
  OrderDate  DATE,
) PRIMARY KEY (CustomerId, OrderId),
  INTERLEAVE IN PARENT Customers ON DELETE CASCADE;
```

Child rows are stored physically adjacent to parent rows. A query joining Customers to Orders for a given CustomerId reads from a single split — no distributed join needed. This is the primary pattern for parent-child relationships in Spanner.

### Commit Timestamps

```sql
CREATE TABLE UserEvents (
  UserId     INT64 NOT NULL,
  EventTime  TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
  EventType  STRING(64),
) PRIMARY KEY (UserId, EventTime DESC);
```

Insert with `PENDING_COMMIT_TIMESTAMP()` — Spanner fills in the exact commit time. Use `DESC` ordering to get most-recent events first.

---

## Transaction Types

| Type | Description | When to Use |
|---|---|---|
| Read-write | Full ACID, external consistency. Acquires locks. | Mutations (INSERT, UPDATE, DELETE) |
| Read-only (strong) | Consistent snapshot of current state. No locks. | Reads that need latest data |
| Read-only (bounded staleness) | Read data that was current within the last N seconds. No locks. Can serve from nearest replica. | High-throughput reads where slight staleness is acceptable |
| Read-only (exact staleness) | Read data as of a specific timestamp. | Consistent read at a point in time; analytics |
| Blind write (mutations) | Send mutations without reading first. Fastest for pure writes. | Bulk inserts, streaming data |
| Partitioned DML | Execute DML across large tables in parallel, without holding locks across the full table. | Large bulk UPDATE/DELETE operations |

---

## Spanner Query Language

Spanner uses Google Standard SQL (ANSI 2011 compatible with extensions) and also supports PostgreSQL dialect (for PostgreSQL-compatible syntax).

- Supports `SELECT`, `JOIN`, `GROUP BY`, `HAVING`, `SUBQUERY`, `WITH` (CTEs), `UNNEST` (for ARRAY columns)
- Supports `JSON` column type with `JSON_VALUE`, `JSON_QUERY` functions
- Supports `ARRAY` and `STRUCT` column types
- Does NOT support `AUTO_INCREMENT` / `SERIAL` (use sequences or UUIDs)
- Does NOT support stored procedures (use client-side logic or Spanner operations)
- `INSERT OR UPDATE` (upsert): use `INSERT ... ON CONFLICT DO UPDATE` (PG dialect) or `MERGE` (GSQL dialect)

---

## Change Streams

Spanner Change Streams capture data changes (inserts, updates, deletes) in near real-time. Consumers read the change stream via the Dataflow connector or the `ExecuteStreamingSql` API.

- Define which tables/columns to watch
- Retention: 1 day default, up to 7 days
- Used for: event-driven architectures, CDC to BigQuery, audit logs

---

## Spanner Query Insights

Built-in query performance monitoring:
- Top queries by CPU, latency, count
- Query execution plans
- Lock contention analysis
- Accessible via the GCP Console (Spanner > Query Insights) or the `SPANNER_SYS` system tables

---

## Backup and PITR

| Feature | Description |
|---|---|
| Managed backups | Full database backup. Retained for 1–365 days. Stored in the same region/multi-region config. |
| PITR (Version Retention) | Data retained for 1–7 days. Allows reading or restoring to any timestamp within the window using `AS OF SYSTEM TIME`. |
| Restore | Creates a new database from a backup. Restore to any backup or to a PITR timestamp. |

---

## When to Use Cloud Spanner

| Scenario | Recommendation |
|---|---|
| Global app requiring relational schema and strong consistency | Spanner (multi-region config) |
| High-throughput transactional app in a single region | Spanner (regional) or Cloud SQL |
| Simple single-region relational database | Cloud SQL (lower cost) |
| Time-series or IoT data at high write rates | Bigtable |
| Document model with mobile/web real-time sync | Firestore |
| Analytics-primary workload | BigQuery |

Spanner is more expensive than Cloud SQL for small workloads. The minimum cost is ~$90/month for 1 node or ~$9/month for 100 PUs. For small databases (<1 GB), use 100 PUs.

---

## Important Constraints

- **No auto-increment**: Use UUIDs, bit-reversed sequences, or hash-prefixed keys. Auto-increment creates hotspots.
- **Commit size limit**: 100 MB per transaction (mutations). Use partitioned DML for bulk operations.
- **Schema change concurrency**: Spanner allows zero-downtime schema changes (adding columns, indexes) — the schema change is applied across replicas incrementally while the database is live. Dropping columns or changing column types requires more care.
- **Read-write transaction retries**: Client must implement retry logic for aborted transactions (Spanner retries abound errors). Use client libraries (not raw JDBC) which handle retries automatically.
- **DDL via API only**: Schema changes (`CREATE TABLE`, `ALTER TABLE`) are issued as DDL statements, not SQL within a transaction.
- **Pricing model**: Node-hour + storage GB + network egress. Processing units (PUs) allow finer granularity. Multi-region instances cost ~ 3x regional for the same node count.
- **Joins across large, non-interleaved tables**: Can be expensive if the tables are distributed across splits. Use interleaved tables, index hints, or denormalization for performance-critical join paths.
