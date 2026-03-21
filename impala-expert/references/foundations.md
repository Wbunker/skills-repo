# Apache Impala Foundations
## Chapter 1: Architecture, MPP Model, Use Cases, Impala vs. Alternatives

---

## What Is Impala?

Apache Impala is a **massively parallel processing (MPP) SQL query engine** that runs natively on Apache Hadoop. It enables low-latency, interactive SQL queries directly against data stored in HDFS, Apache HBase, Amazon S3, and other compatible storage systems — without requiring data movement or transformation into a proprietary format.

Key characteristics:
- **Daemon-based**: Always-running processes (no MapReduce startup overhead)
- **Native C++ execution**: Compiled query fragments; no JVM per query
- **Shared-nothing MPP**: Each node scans local data; data shuffled only as needed
- **Hive Metastore compatible**: Reads the same table definitions as Hive; tables are interchangeable

---

## The Three Core Daemons

### impalad

The primary Impala daemon. One instance runs on each **datanode** in the cluster.

**Three roles in one process:**

| Role | Description |
|------|-------------|
| **Planner/Coordinator** | Receives the client query; parses, analyzes, and generates the distributed query plan; dispatches plan fragments to executors; aggregates and returns results |
| **Executor** | Runs plan fragments on behalf of other coordinators; scans local HDFS data blocks |
| **Backend** | Manages memory, caching, and local resources for the node |

Any impalad can accept a client connection and act as coordinator. For large clusters, designating dedicated coordinator nodes (not running executor workloads) improves scalability.

### statestore (statestored)

A single daemon (typically on the master node) that provides **cluster membership and pub/sub messaging**:
- Tracks which impalads are alive and healthy
- Broadcasts updates to all subscribers (impalads, catalogd)
- Does **not** persist state — if it restarts, impalads continue running queries but can't get new membership updates until it recovers
- Failure of statestore does not immediately kill running queries

### catalogd

A single daemon that acts as a **metadata proxy** between Hive Metastore and the Impala cluster:
- Caches database, table, and partition metadata from the Hive Metastore
- Propagates DDL changes (CREATE TABLE, ALTER TABLE, etc.) to all impalads via the statestore
- Without catalogd, each impalad would need to independently poll Hive Metastore on every query

**DDL propagation flow:**
```
Client issues CREATE TABLE
    → Coordinator impalad writes to Hive Metastore
    → catalogd detects change, updates its cache
    → catalogd broadcasts update via statestore
    → All impalads refresh their local metadata cache
```

---

## Distributed Query Execution Model

### Query Lifecycle

```
1. Client connects to any impalad (coordinator)
2. Coordinator: parses SQL → semantic analysis against catalog cache
3. Coordinator: single-node plan → distributed plan (fragments)
4. Coordinator: dispatches fragments to executor impalads
5. Executors: scan local HDFS blocks → apply filters/projections
6. Exchange operators: shuffle/broadcast intermediate results between nodes
7. Final aggregation at coordinator
8. Results streamed back to client
```

### Plan Fragments

A **fragment** is the unit of parallel work. Each fragment:
- Runs on one impalad instance
- Contains one or more plan nodes (scan, hash join, aggregate, exchange)
- Communicates with other fragments via **exchange nodes**

Exchange types:
- **BROADCAST**: Small table copied to all executor nodes (broadcast join)
- **HASH**: Rows distributed by hash of join/group-by key (shuffle join / repartition)
- **UNPARTITIONED**: All rows sent to one node (final aggregation)

### Runtime Filters

Impala generates **Bloom filters** during query execution to accelerate joins:
- Build side of a hash join generates a Bloom filter of its keys
- Filter is pushed to scan nodes on the probe side
- Scan nodes skip entire data blocks/row groups that cannot match
- Dramatically reduces I/O for selective joins on large fact tables

---

## Impala vs. Alternatives

| Dimension | Impala | Hive | Spark SQL | Presto/Trino |
|-----------|--------|------|-----------|-------------|
| **Execution engine** | Native C++ MPP daemons | MapReduce or Tez | JVM (Spark core) | JVM MPP daemons |
| **Startup overhead** | Near-zero (always running) | High (MR/Tez job launch) | Medium (Spark context) | Near-zero (always running) |
| **Latency** | Sub-second to seconds | Minutes | Seconds to minutes | Sub-second to seconds |
| **Throughput (large scans)** | High | Very high (MR scales) | High | High |
| **HDFS data sharing** | Yes (shared Hive Metastore) | Yes | Yes | Yes |
| **Updates/deletes** | Via Kudu or INSERT OVERWRITE | Hive ACID (ORC) | Delta Lake / Iceberg | Via connectors |
| **Fault tolerance** | None (query fails if node dies) | Full (MR restarts tasks) | Full (RDD lineage) | Partial |
| **Best for** | Interactive BI, ad-hoc queries | Batch ETL, very large jobs | Unified batch+stream | Interactive queries |

**When to choose Impala:**
- BI tools / dashboards requiring sub-second response
- Ad-hoc exploratory SQL by analysts
- Data already in HDFS/S3 in Parquet or ORC format
- Existing Hive tables you want to query interactively

**When Impala is not the right choice:**
- Very long-running batch ETL (Hive/Spark handles fault tolerance better)
- Frequent row-level updates (use Kudu-backed Impala tables or a transactional system)
- Complex iterative ML workloads (use Spark)

---

## Use Cases

| Use Case | Why Impala |
|----------|-----------|
| **Interactive analytics on HDFS data** | Low latency; analysts get results in seconds not minutes |
| **BI tool backend (Tableau, Looker, Power BI)** | JDBC/ODBC support; ANSI SQL; fast enough for interactive dashboards |
| **Data exploration / ad-hoc SQL** | impala-shell for immediate queries; no job submission overhead |
| **Federated queries (HDFS + HBase)** | Join HBase key-value store with large HDFS fact tables |
| **Shared schema with Hive** | ETL writes with Hive; Impala serves read queries — same tables |
| **Cloud data lake queries (S3/ADLS)** | Same SQL interface; data stays in object storage |

---

## Impala and the Hadoop Ecosystem

```
┌────────────────────────────────────────────────────────┐
│                  HADOOP ECOSYSTEM                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │               STORAGE LAYER                       │   │
│  │   HDFS · S3 · ADLS · GCS · Kudu                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           METADATA (Hive Metastore)               │   │
│  │   Shared by Impala, Hive, Spark SQL               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  IMPALA  │  │   HIVE   │  │  SPARK   │              │
│  │ (fast    │  │ (batch   │  │ (unified │              │
│  │  reads)  │  │  ETL)    │  │  engine) │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────────────────────────────────────────┘
```

Impala does **not** replace the Hadoop ecosystem — it complements it by providing a fast SQL layer over data that other tools produce and consume.
