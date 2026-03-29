# Ch 1–2 — Introduction & Architecture

## Table of Contents
- [Why HBase](#why-hbase)
- [HBase vs. RDBMS](#hbase-vs-rdbms)
- [Data Model](#data-model)
- [Namespaces](#namespaces)
- [Physical Storage Model](#physical-storage-model)
- [Architecture Components](#architecture-components)
- [Write Path](#write-path)
- [Read Path](#read-path)
- [ACID Properties](#acid-properties)
- [HBase Versions & Current Status](#hbase-versions--current-status)

---

## Why HBase

HBase targets use cases that outgrow RDBMS and need:

- **Random read/write access to billions of rows** at low latency (HDFS is batch-only)
- **Sparse, wide tables** where most cells are empty (stored compactly — null columns take no space)
- **Variable schema** — columns can differ per row with no schema migrations
- **Linear horizontal scaling** — add RegionServers to increase capacity and throughput
- **Tight Hadoop integration** — scan tables directly from MapReduce/Spark

HBase is **not** suitable for: complex relational queries, joins, secondary indexes (without Phoenix), or OLAP workloads.

---

## HBase vs. RDBMS

| Concern | RDBMS | HBase |
|---------|-------|-------|
| Schema | Fixed, rigid | Schema-flexible (column qualifiers dynamic) |
| Scaling | Vertical / complex sharding | Horizontal, auto-sharding into regions |
| Joins | Native SQL joins | Application-level denormalization |
| Transactions | Multi-row ACID | Single-row ACID only |
| Index | Rich secondary indexes | Primary index (row key) only |
| Access | SQL | Row key lookup + range scan |
| Consistency | Strong | Strong within a region |
| Best for | Structured, relational data | Wide, sparse, high-throughput random access |

---

## Data Model

### Logical View

```
Table: "web_analytics"

RowKey           | cf:page_title        | cf:bytes | metrics:views | metrics:clicks
─────────────────────────────────────────────────────────────────────────────────
example.com/home | "Home Page"          | 45320    | 100023        | 8901
example.com/about| "About Us"           | 12340    |               | 412
example.com/blog | "Blog"               | 98710    | 55200         |
```

### Fundamental Concepts

| Term | Description |
|------|-------------|
| **Table** | Logical grouping of rows; sharded into regions |
| **Row** | Sorted by row key (lexicographic byte order); atomic read/write at row level |
| **Row Key** | The primary index — a byte[] used to uniquely identify and locate a row |
| **Column Family (CF)** | Physical grouping of columns; defined at table creation; stored together on disk |
| **Column Qualifier** | Column name within a CF (dynamic — no pre-declaration needed) |
| **Column** | `family:qualifier` notation (e.g., `cf:username`) |
| **Cell** | Intersection of row + column; stores a byte[] value at a specific timestamp |
| **Version / Timestamp** | Each cell can have multiple timestamped versions; default retention = 1 |
| **Namespace** | Table grouping mechanism (like a database in RDBMS); supports quotas and permissions |

### Cell Coordinates

Every piece of data is addressed by exactly 4 dimensions:

```
{table, row key, column family:qualifier, timestamp} → byte[] value
```

Cells are sorted within a row by: `column family → qualifier → timestamp (descending)`

### Data Types

HBase stores everything as **raw bytes**. There are no native int/string/date types.
Use `Bytes.toBytes(value)` / `Bytes.to*(byte[])` from `org.apache.hadoop.hbase.util.Bytes`.

---

## Namespaces

```
hbase shell:
> create_namespace 'prod'
> create_namespace 'dev', {'hbase.namespace.quota.maxtables' => '10'}
> list_namespace
> create 'prod:orders', 'cf'
> drop_namespace 'dev'   # must be empty first
```

Built-in namespaces:
- `hbase` — system tables (`hbase:meta`, `hbase:namespace`)
- `default` — tables with no explicit namespace (`mytable` = `default:mytable`)

---

## Physical Storage Model

### HFile Layout

```
Data Blocks (key-value pairs sorted by row key → CF → qualifier → timestamp)
    ↓ compressed in blocks (default 64KB)
Meta Blocks (bloom filters, timestamps)
File Info
Data Block Index (sparse index of first key per block)
Meta Block Index
Trailer (offsets to all sections)
```

- HFiles are **immutable** — never modified in place; compaction merges them
- Each CF has its own set of HFiles per region
- Data blocks are loaded into the **BlockCache** (on-heap or BucketCache off-heap) on access

### Region Layout

```
Region (a contiguous range of row keys within a table)
  └── Store (one per column family)
        ├── MemStore (in-memory write buffer, per CF)
        └── StoreFiles (HFiles on HDFS, per CF)
```

---

## Architecture Components

### HMaster

- Assigns regions to RegionServers at startup and after failures
- Coordinates DDL operations (CREATE TABLE, ALTER TABLE, DROP TABLE)
- Runs the **load balancer** (default every 5 minutes)
- Handles region splits and merges coordination
- Does **not** participate in data reads or writes

### RegionServer

- Serves reads and writes for its assigned regions
- Manages the WAL (Write-Ahead Log), MemStores, and BlockCache
- Performs region splits when a region exceeds `hbase.hregion.max.filesize`
- Reports health to ZooKeeper via heartbeats

### ZooKeeper

- Stores: active HMaster location, RegionServer registry, root region location
- Provides distributed locks for split/merge coordination
- Detects RegionServer failures via ephemeral nodes
- Required: odd number of quorum nodes (3 or 5 for HA)

### hbase:meta Table

- Special system table that maps every region to its serving RegionServer
- Stored in a region on a RegionServer like any other table
- Clients cache this mapping (with ZooKeeper pointing to meta region location)
- Cache is invalidated on region splits / RegionServer failover

---

## Write Path

```
1. Client calls table.put(put)
2. Client looks up region location (ZooKeeper → meta cache → RegionServer)
3. RegionServer writes to WAL (Write-Ahead Log) on HDFS — for durability
4. RegionServer writes to MemStore (in-memory sorted buffer for that CF)
5. Put() returns to client

When MemStore reaches hbase.hregion.memstore.flush.size (default 128MB):
6. MemStore flushes to a new HFile on HDFS
7. WAL is rolled (old WAL entries no longer needed for replay)

Periodically:
8. Minor compaction merges a few small HFiles into one larger HFile
9. Major compaction rewrites ALL HFiles for a region into one — removes deletes/TTL
```

**Durability options** (`Durability` enum on `Mutation`):
- `USE_DEFAULT` / `SYNC_WAL` — sync WAL before returning (default, safest)
- `ASYNC_WAL` — async WAL write (higher throughput, risk of data loss on crash)
- `SKIP_WAL` — no WAL (fastest; data loss on RegionServer crash)
- `FSYNC_WAL` — fsync to disk (slowest; rarely needed)

---

## Read Path

```
1. Client calls table.get(get) or table.getScanner(scan)
2. Client resolves region location
3. RegionServer checks:
   a. BlockCache (LRU, in-memory) → return if hit
   b. MemStore (unflushed recent writes) → merge into result
   c. HFiles on HDFS (via Bloom filter to skip irrelevant files)
      → load relevant data blocks into BlockCache
4. Merge results across all levels, apply version filtering → return to client
```

**Bloom filters** (per HFile) can skip an entire file if the row key / row+col is absent.
Configure per CF: `BLOOMFILTER => 'ROW'` (default) or `'ROWCOL'` (for column-level lookups).

---

## ACID Properties

| Property | HBase Behavior |
|----------|---------------|
| **Atomicity** | Single-row mutations are atomic (all cells in a Put succeed or fail together) |
| **Consistency** | Strong consistency within a region; no eventual consistency model |
| **Isolation** | Row-level; concurrent puts to same row are serialized by the RegionServer |
| **Durability** | Guaranteed by WAL + HDFS replication (default); configurable via `Durability` |

> **Multi-row transactions are NOT supported natively.**
> For cross-row consistency, use `checkAndPut` / `checkAndMutate` for compare-and-swap,
> or use Apache Tephra / Apache Omid for multi-row transactions.

**Atomic CAS operations:**
```java
// Only write if the column doesn't exist (optimistic locking pattern)
boolean success = table.checkAndMutate(row, family, qualifier,
    CompareOperator.EQUAL, null, put);
```

---

## HBase Versions & Current Status

| Version | Key Features |
|---------|-------------|
| 0.94.x | Stable baseline (Lars George book era) |
| 0.98.x | Namespaces, cell-level security |
| 1.0 | Stable API (`Connection`/`Table` replace `HTable`/`HTablePool`) |
| 1.x | Cell-level tags, visibility labels, quota management |
| 2.0 | Async client, in-memory compaction, improved MOB (Medium Objects) support |
| 2.x | Procedure v2 (master procedures), RegionServer groups, HBCK2 |
| 3.x | Java 8+ required, improved performance, active development |

**Current Apache HBase docs:** https://hbase.apache.org/book.html
**Latest stable release:** Check https://hbase.apache.org/ for current version.

### API Migration Note (0.x → 1.x+)

| Old (0.x) | New (1.0+) |
|-----------|-----------|
| `new HTable(conf, tableName)` | `connection.getTable(TableName.valueOf(name))` |
| `HTablePool` | `Connection` (thread-safe, long-lived) |
| `HBaseAdmin` | `connection.getAdmin()` |
| `HConnection` | `Connection` |

```java
// Modern connection pattern (1.0+)
Configuration conf = HBaseConfiguration.create();
try (Connection connection = ConnectionFactory.createConnection(conf);
     Table table = connection.getTable(TableName.valueOf("mytable"))) {
    // use table
}
```
