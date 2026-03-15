# Bigtable — Capabilities Reference

## Purpose

Cloud Bigtable is Google's fully managed, petabyte-scale NoSQL wide-column database designed for high-throughput, low-latency workloads. It is the same database that powers Google Search indexing, Google Maps, Gmail, and Google Analytics. Bigtable excels at analytical and operational workloads requiring millions of reads/writes per second with single-digit millisecond latency at any scale.

Bigtable is HBase-compatible: applications using the Apache HBase API can connect to Bigtable with minimal code changes.

---

## Core Concepts

| Concept | Description |
|---|---|
| Instance | The top-level resource. Contains one or more clusters. Shared across all tables in the instance. |
| Cluster | A group of Bigtable nodes in a single zone. An instance can have 1–8 clusters across different zones or regions for HA and replication. |
| Node | A single Bigtable server. Determines throughput capacity. SSD: ~10,000 QPS per node at <10ms. HDD: lower QPS, higher latency. |
| Table | A collection of rows. Each row is uniquely identified by a row key. Tables are sparse — not all rows need the same columns. |
| Row | A single data record, identified by a unique row key (arbitrary bytes, max 4 KB). |
| Column family | A group of columns. Defined at table creation/schema time. Column families have garbage collection policies. Max ~100 column families per table. |
| Column qualifier | The column name within a column family. Can be arbitrary bytes. Created dynamically — no pre-declaration needed. Qualifiers count toward the row key for indexing. |
| Cell | The value at a specific (row key, column family, column qualifier, timestamp). Each cell can hold multiple timestamped versions. |
| Timestamp | Each cell value has a 64-bit integer timestamp (microseconds since epoch by default). Multiple versions of the same cell are stored, ordered by timestamp descending. |
| Row key | Byte string identifying a row. Rows are sorted lexicographically by row key. All reads and writes are based on row key. The only supported index. |
| App profile | Routing policy for connecting applications to clusters. Controls single-cluster routing vs. multi-cluster routing, and read/write routing for replication. |
| Garbage collection (GC) policy | Per-column-family policy that determines which cell versions are retained. Based on version count, age, or a union/intersection of both. |
| Replication | Automatic asynchronous replication of data across clusters in the same instance. |

---

## Data Model

Bigtable's data model is a sorted map of maps:

```
Table
├── Row: "com.google.cloud#2024-03-01#event-001"
│   ├── cf:stats
│   │   ├── "clicks" @ t=1709280000000000 → "142"
│   │   ├── "clicks" @ t=1709193600000000 → "98"   (older version)
│   │   └── "views"  @ t=1709280000000000 → "3500"
│   └── cf:meta
│       ├── "source"  @ t=1709280000000000 → "organic"
│       └── "country" @ t=1709280000000000 → "US"
├── Row: "com.google.cloud#2024-03-01#event-002"
│   └── ...
```

Key characteristics:
- Rows are sorted lexicographically by row key — this is the primary access pattern.
- Scans read contiguous ranges of rows — design row keys so related data is adjacent.
- Columns are sparse — a row only stores cells that have been written; absent columns cost nothing.
- Multiple versions of a cell are stored and pruned by GC policy.

---

## Row Key Design

Row key design is the most critical performance decision in Bigtable. Poor key design leads to hot tablets (all traffic hitting one server).

### Anti-Patterns

| Anti-Pattern | Problem |
|---|---|
| Sequential integers (1, 2, 3...) | All new writes go to the last tablet — hotspot |
| Timestamps as prefix (2024-03-01-...) | Newest data always on the same tablet — hotspot |
| Domain names forward (google.com) | Google gets all traffic; com gets all traffic |
| Low-cardinality prefix | All rows with same prefix on same tablet |

### Good Patterns

| Pattern | Example | Use Case |
|---|---|---|
| Reverse domain | `com.google.cloud` | Website data — distributes across alphabet |
| Hash prefix | `a1b2c3d4#user-12345` | Distribute random user IDs |
| Field promotion | `region#date#device` | Query by region + date range |
| Reverse timestamp | `9999999999999 - timestamp` | Get most-recent data first via scan |
| Salted prefix | `FARM_FINGERPRINT(key) % 100 # key` | Distribute writes evenly |

**Reverse timestamp pattern** is common for time-series: the most-recent events sort first (lowest prefix), enabling a scan to return the N most recent events without a full table scan.

### Example Row Key for IoT Telemetry

```
{device_id_hash}#{device_id}#{reverse_timestamp}
e.g.: 7f3a2c#sensor-device-001#9007199254739990
```

This distributes writes evenly (hash prefix), groups all data for a device together (device_id), and returns most-recent readings first (reverse timestamp).

---

## Storage Types

| Type | Latency | IOPS | Cost | Use Case |
|---|---|---|---|---|
| SSD | < 10ms (p99 < 6ms) | ~10,000 QPS/node | Higher | Real-time serving, operational, sub-10ms latency required |
| HDD | 10–200ms | ~500 QPS/node | Lower (3x cheaper) | Batch analytics, archival, infrequently accessed historical data |

SSD storage is recommended for all production serving use cases. HDD is appropriate for large batch analytics where latency is not critical.

---

## Performance Characteristics

| Metric | Value |
|---|---|
| SSD QPS per node | ~10,000 reads or ~10,000 writes |
| SSD read latency | < 6ms (p99) with properly designed row keys |
| Scaling | Linear — doubling nodes doubles throughput |
| Minimum for production | 3 nodes (for SSD); 1 node for development |
| Maximum table size | Unlimited (petabytes) |
| Maximum row size | 256 MB (but rows > 10 MB impact performance) |
| Maximum row key size | 4 KB |
| Maximum cell value size | 100 MB (values > 1 MB impact performance) |

**Bigtable requires a warm-up period**: After adding nodes or during initial data loads, Bigtable needs time to redistribute tablets and optimize. Performance reaches steady state after ~20 minutes for new nodes.

---

## Replication

Bigtable supports multi-cluster replication for high availability and geographic distribution:

| Topology | Description |
|---|---|
| Single cluster | No replication. All reads/writes to one cluster. |
| Multi-cluster (same region, different zones) | HA: automatic failover if a zone fails. Both clusters store all data. |
| Multi-cluster (different regions) | Geographic distribution. Reduced latency for global users. Serves as DR. |

**Replication is asynchronous**: There is a replication lag (typically <1 minute for same-region; seconds to minutes for cross-region). Applications must tolerate eventual consistency for cross-cluster reads.

### App Profiles and Routing

| Routing Policy | Description |
|---|---|
| Single-cluster routing | All requests go to a specific cluster. Consistent reads. |
| Multi-cluster routing (any cluster) | Requests routed to nearest/available cluster. Lower latency for reads. May see stale data on failover. |
| Read/write routing | Writes go to one cluster; reads go to another. Useful for separating batch reads from serving. |

---

## Garbage Collection Policies

GC policies are set per column family. Bigtable automatically deletes cells that don't match the policy.

| Policy Type | Description | Example |
|---|---|---|
| Max versions | Keep only the N most recent versions of each cell | Keep last 3 versions |
| Max age | Delete cells older than N seconds/days | Delete cells older than 30 days |
| Union | Delete if EITHER max versions OR max age criteria met | Delete if >3 versions OR >30 days old |
| Intersection | Delete only if BOTH criteria met | Delete if >3 versions AND >30 days old |

**Union** is the most common policy for time-series: keep at most N recent versions and don't retain old data beyond a time window.

---

## Use Cases

| Use Case | Why Bigtable |
|---|---|
| Time-series (metrics, monitoring) | High write throughput; scan by time range via row key design |
| IoT telemetry | Millions of devices writing simultaneously; low latency |
| Financial trading data | Sub-millisecond read latency; ordered by instrument + time |
| AdTech (click/impression streams) | Petabyte-scale; high write throughput; fast aggregation scans |
| ML feature store | Fast reads for feature serving; bulk writes for feature computation |
| Graph data | Wide rows represent adjacency lists; fast random access |
| Personalization (user activity) | User data co-located by user ID; fast per-user reads |
| HBase migration | Drop-in HBase API compatibility |

---

## Bigtable vs. Other Databases

| Factor | Bigtable | Firestore | Cloud SQL | Spanner |
|---|---|---|---|---|
| Data model | Wide-column | Document | Relational | Relational |
| Max throughput | Millions QPS | ~10K writes/s | ~50K TPS | Millions TPS (with nodes) |
| Latency | < 6ms (SSD) | 10–100ms | 1–10ms | 10–100ms |
| Query model | Row key + scan | Rich queries | Full SQL | Full SQL |
| Schema | Schemaless (column families) | Schemaless | Fixed | Fixed |
| Real-time sync | No | Yes | No | No |
| Strong consistency | Single cluster only | Yes | Yes | Yes (global) |
| Best for | High-throughput analytics/IoT | Mobile/web apps | OLTP relational | Global relational |

---

## Important Constraints

- **No secondary indexes**: The only supported access pattern is by row key and row key range scans. Design your row key to support your primary query pattern.
- **No cross-row transactions**: Bigtable supports atomic operations within a single row (conditional mutations using check-and-mutate). Cross-row transactions are not supported.
- **No SQL**: Bigtable uses the HBase API or Bigtable client libraries. No SQL query language. Use BigQuery (via Bigtable connector) for SQL analytics.
- **Replication lag**: Multi-cluster replication is asynchronous. Do not rely on cross-cluster strong consistency.
- **Minimum 3 nodes for production**: Single-node and 2-node clusters are acceptable for dev; production requires 3+ nodes for performance and SLAs.
- **Column families at table creation**: Column families are defined at table schema time (unlike column qualifiers which are dynamic). You cannot add column families without modifying the table schema.
- **Tablet hot-spotting**: Poor row key design concentrates load on a single tablet. Monitor Bigtable Key Visualizer to detect hotspots.
