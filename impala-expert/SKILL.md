---
name: impala-expert
description: Expert on Apache Impala — architecture, SQL DDL/DML, data types and file formats, schema design, query performance tuning, built-in functions, Hadoop ecosystem integration, security, and cluster operations. Use when writing Impala SQL, designing schemas, tuning query performance, integrating with HDFS/Hive/HBase/S3, configuring security, or administering Impala clusters. Based on "Getting Started with Impala" by John Russell (O'Reilly).
---

# Apache Impala Expert

Based on "Getting Started with Impala" by John Russell (O'Reilly).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IMPALA CLUSTER                                │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  IMPALAD     │  │  IMPALAD     │  │  IMPALAD     │  (one per    │
│  │  (node 1)    │  │  (node 2)    │  │  (node 3)    │   datanode)  │
│  │              │  │              │  │              │              │
│  │  Query       │  │  Query       │  │  Query       │              │
│  │  Planner     │  │  Executor    │  │  Executor    │              │
│  │  Coordinator │  │              │  │              │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                       │
│         └─────────────────┼──────────────────┘                      │
│                           │                                          │
│  ┌────────────────────────▼──────────────────────────────────────┐  │
│  │                   STATESTORE DAEMON                            │  │
│  │          (tracks which impalads are alive;                     │  │
│  │           distributes membership/topic updates)                │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                   CATALOGD DAEMON                               │  │
│  │          (caches Hive Metastore metadata;                       │  │
│  │           propagates DDL changes to all impalads)               │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────┐    ┌───────────────────────────────────────┐  │
│  │  HIVE METASTORE   │    │  HDFS / S3 / ADLS (data storage)      │  │
│  │  (schema catalog) │    │  Parquet · ORC · Text · Avro · RC     │  │
│  └───────────────────┘    └───────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

Client connections: impala-shell · JDBC/ODBC · HUE
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| What is Impala, MPP model, impalad/statestore/catalogd, use cases vs. Hive/Spark | [foundations.md](references/foundations.md) |
| SELECT, JOIN, subqueries, CTEs, DDL (CREATE/ALTER/DROP), DML (INSERT/LOAD), UPSERT | [sql-reference.md](references/sql-reference.md) |
| Data types (INT, STRING, DECIMAL, TIMESTAMP, complex), file formats (Parquet, ORC, Text, Avro), compression | [data-types-and-formats.md](references/data-types-and-formats.md) |
| Partitioning, internal vs. external tables, bucketing, table properties, schema evolution | [schema-design.md](references/schema-design.md) |
| COMPUTE STATS, EXPLAIN plans, query hints, broadcast vs. shuffle joins, admission control tuning | [performance.md](references/performance.md) |
| Built-in functions, aggregate functions, analytic/window functions, UDFs/UDAs | [functions.md](references/functions.md) |
| Hive metastore, HBase integration, HDFS/S3, Spark interoperability, JDBC/ODBC | [ecosystem-integration.md](references/ecosystem-integration.md) |
| Kerberos, LDAP, Ranger/Sentry authorization, TLS/SSL, row-level security | [security.md](references/security.md) |
| Admission control, resource pools, memory management, INVALIDATE METADATA, troubleshooting | [operations.md](references/operations.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | Ch. 1 | Impala architecture, MPP execution model, impalad/statestore/catalogd roles, query lifecycle, use cases, Impala vs. Hive/Spark SQL |
| `sql-reference.md` | Ch. 2–3 | impala-shell, SQL syntax reference, SELECT/JOIN/subquery/CTE, DDL (database/table/view/index), DML (INSERT/LOAD DATA/UPSERT), transactions |
| `data-types-and-formats.md` | Ch. 4 | Primitive types, DECIMAL precision, TIMESTAMP handling, complex types (ARRAY/MAP/STRUCT), Parquet, ORC, Text, Avro, RCFile, SequenceFile, compression codecs |
| `schema-design.md` | Ch. 4–5 | Partition design, internal vs. external tables, partition pruning, bucketing, STORED AS, LOCATION, table properties, schema evolution, partition management |
| `performance.md` | Ch. 5 | COMPUTE STATS, EXPLAIN output, query profiles, broadcast vs. shuffle joins, join order hints, runtime filters, query memory limits, partitioning for performance |
| `functions.md` | Ch. 6 | String/math/date/conditional/type functions, aggregate functions, analytic (window) functions, UDF/UDA authoring in C++ and Java |
| `ecosystem-integration.md` | Ch. 7 | Hive metastore compatibility, HBase lookup tables, HDFS operations, S3/ADLS object storage, Spark SQL interop, JDBC/ODBC connectivity |
| `security.md` | Ch. 8 | Kerberos authentication, LDAP/AD integration, Apache Ranger / Sentry authorization, TLS wire encryption, audit logging, column masking, row filters |
| `operations.md` | Ch. 9 | Catalogd/statestore management, INVALIDATE METADATA / REFRESH, admission control, resource pools, memory spilling, Impala daemon tuning, common errors |

## Core Decision Trees

### Which File Format Should I Use?

```
What is your primary workload?
├── Analytical queries (SELECT, aggregations, BI tools)
│   └── Parquet (default choice)
│       ├── Best compression + columnar pushdown
│       ├── STORED AS PARQUET
│       └── Use snappy or zstd compression
├── Need updates / ACID transactions
│   └── ORC (better for Hive ACID; Impala read-only for ORC+ACID)
│       └── Consider Kudu for mutable data in Impala
├── Interoperability with many tools (Hive, Pig, Spark)
│   └── Avro (row-based; good for schema evolution)
│       └── Add TBLPROPERTIES ('avro.schema.url'=...)
├── Simple ETL staging / human-readable
│   └── Text (CSV/TSV)
│       └── FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'
└── Legacy Hadoop workloads
    └── RCFile or SequenceFile (rarely needed for new work)
```

### Should I Use Partitioning?

```
How will queries filter this table?
├── Always filter on a date/region/category column
│   └── Partition by that column
│       ├── Date: PARTITION BY (year INT, month INT) or (dt STRING)
│       ├── High-cardinality column? → Do NOT partition
│       │   └── Thousands of partitions = metadata overhead
│       └── Aim for partitions > 256 MB each for Parquet efficiency
├── No consistent filter column
│   └── Skip partitioning; rely on columnar + stats
└── Need to update individual rows?
    └── Consider Apache Kudu instead of HDFS-backed tables
```

### How to Speed Up a Slow Query?

```
Run EXPLAIN <query> — check the plan first
│
├── "BROADCAST" join on a large table?
│   └── Table stats missing → run COMPUTE STATS on both tables
│       └── Or add hint: SELECT /*+ SHUFFLE */ ...
│
├── Full table scan (no partition pruning)?
│   └── Predicate doesn't match partition columns
│       └── Rewrite WHERE clause to use partition key
│
├── Very large intermediate result sets?
│   └── Check EXPLAIN for data skew; consider repartitioning
│       └── SET NUM_NODES=1 for debugging; SET MT_DOP for parallelism
│
├── Missing column statistics?
│   └── COMPUTE STATS <table>;   -- or per-partition
│       └── Re-run EXPLAIN to verify join order changed
│
└── Memory exceeded / spilling to disk?
    └── SET MEM_LIMIT='8g';
        └── Or tune admission control pool limits
```

### Authentication Choice?

```
What identity provider do you have?
├── MIT Kerberos / Active Directory with Kerberos
│   └── Enable Kerberos authentication on impalad
│       └── kinit required before impala-shell; JDBC uses principal=
├── LDAP / Active Directory (no Kerberos)
│   └── --enable_ldap_auth on impalad
│       └── impala-shell --ldap --user=<user>
└── Development / internal only
    └── No auth (default) — never in production
```

## Key Concepts Quick Reference

### Core Terminology

| Term | Definition |
|------|-----------|
| **impalad** | The main daemon; one per datanode; acts as planner, coordinator, and executor |
| **statestore** | Tracks cluster membership; broadcasts health/topic updates to all impalads |
| **catalogd** | Caches Hive Metastore metadata; propagates DDL changes cluster-wide |
| **coordinator** | The impalad that receives the query, plans it, and aggregates results |
| **fragment** | A unit of work in the distributed query plan; runs on one impalad |
| **admission control** | Gate that queues/rejects queries based on memory/concurrency limits |
| **runtime filter** | Bloom filter generated from a build-side join; pushed to scan nodes to skip rows |
| **COMPUTE STATS** | Collects table/column statistics used by the query planner for cardinality estimates |
| **INVALIDATE METADATA** | Forces catalogd to reload metadata from Hive Metastore (heavier; drops all cached info) |
| **REFRESH** | Reloads file/partition metadata for a specific table (lighter than INVALIDATE) |

### MPP Query Execution at a Glance

```
Client → Coordinator impalad
           │
           ├── Parse + Analyze SQL (against catalogd cache)
           ├── Generate distributed plan (fragments)
           ├── Dispatch fragments to executor impalads
           │       Each executor scans local HDFS data blocks
           │       Exchange operators shuffle/broadcast between nodes
           └── Aggregate partial results → return to client
```

No MapReduce. No intermediate disk writes (unless memory spills). Results stream back directly.
