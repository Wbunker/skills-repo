---
name: apache-iceberg-expert
description: Apache Iceberg table format expertise covering architecture, metadata layers, catalog management, schema/partition evolution, row-level operations, streaming, engine integrations, performance tuning, and governance. Use when working with Iceberg tables, designing lakehouse architectures, choosing between COW and MOR strategies, configuring catalogs (REST, Glue, Hive, Nessie), optimizing query performance, managing table maintenance, or comparing Iceberg with Delta Lake and Hudi.
---

# Apache Iceberg Expert

Based on "Apache Iceberg: The Definitive Guide" by Tomer Shiran, Jason Hughes, and Alex Merced (O'Reilly, 2024).

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CATALOG LAYER                     │
│   REST Catalog │ Hive Metastore │ Glue │ Nessie     │
│   (tracks current metadata pointer per table)        │
├─────────────────────────────────────────────────────┤
│                   METADATA LAYER                     │
│  metadata.json → manifest-list.avro → manifest.avro  │
│        │              │                    │          │
│    schema,         snapshot →          data file      │
│    partitions,     manifest           listings with   │
│    properties,     references         column stats    │
│    snapshots                          & partitions    │
│                                                      │
│  Puffin files: statistics, deletion vectors (v3)     │
├─────────────────────────────────────────────────────┤
│                     DATA LAYER                       │
│  Parquet / ORC / Avro data files                     │
│  Position delete files (v2) │ Equality delete (v2)   │
│  Deletion vectors in Puffin (v3)                     │
├─────────────────────────────────────────────────────┤
│              OBJECT STORAGE                          │
│         S3  │  ADLS  │  GCS  │  HDFS                │
└─────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Metadata layers, data files, delete files, catalogs | [foundations.md](references/foundations.md) |
| DDL, DML, MERGE, time travel, branching & tagging | [operations.md](references/operations.md) |
| Hidden partitioning, sort orders, compaction, file sizing | [performance.md](references/performance.md) |
| Spark/Flink Streaming, Kafka Connect, CDC | [streaming.md](references/streaming.md) |
| Spark, Trino, Flink, Athena, Dremio, Snowflake config | [engines.md](references/engines.md) |
| WAP pattern, security, encryption, access control | [governance.md](references/governance.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1-3 | Three-layer architecture, metadata/manifest/data files, Puffin stats, catalog types, format versions (v1/v2/v3), delete file types |
| `operations.md` | 4-5 | CREATE/ALTER/DROP, INSERT/UPDATE/DELETE/MERGE, COW vs MOR, schema evolution, partition evolution, time travel, snapshots, branching, tagging, restore |
| `performance.md` | 6-7 | Hidden partitioning, partition transforms, sort orders, compaction, rewrite manifests, expire snapshots, orphan file cleanup, file sizing, data skipping, Bloom filters |
| `streaming.md` | 8 | Spark Structured Streaming, Flink streaming, Kafka Connect, CDC patterns, incremental reads, WAP with streaming |
| `engines.md` | 9 | Spark, Trino/Presto, Flink, Athena, Dremio, Snowflake, StarRocks, EMR, DuckDB configuration and usage |
| `governance.md` | 10-12 | Write-Audit-Publish, production monitoring, security layers, encryption, RBAC, AWS Lake Formation, compliance patterns |

## Decision Trees

### COW vs MOR

```
What is your workload?
├── Read-heavy, few updates → Copy-on-Write (COW)
│   └── Reads are fast (no reconciliation), writes rewrite entire files
├── Write-heavy, frequent updates → Merge-on-Read (MOR)
│   └── Writes are fast (delete files only), reads reconcile at query time
├── Mixed → Configure per operation:
│   ├── DELETE → MOR (small deletes are common)
│   ├── UPDATE → depends on update size
│   │   ├── Small updates (few rows) → MOR
│   │   └── Large updates (many rows) → COW
│   └── MERGE → MOR (typically many small changes)
└── Using v3? → Deletion vectors give MOR benefits with less read overhead
```

### Catalog Selection

```
Which catalog?
├── New deployment, multi-engine → REST Catalog (vendor-neutral standard)
├── Existing Hadoop ecosystem → Hive Metastore
├── AWS-native, serverless → AWS Glue Catalog
├── Need Git-style versioning → Project Nessie
│   └── Multi-table atomic commits, branches, tags at catalog level
└── Simple, self-contained → JDBC Catalog
```

### Partition Strategy

```
How to partition?
├── Query always filters on date? → identity(date) or month(ts) or day(ts)
├── High-cardinality join key? → bucket(N, column)
├── Need to change later? → Iceberg partition evolution (metadata-only)
├── Current partitions too small? → Evolve to coarser granularity
├── Current partitions too large? → Evolve to finer granularity
└── Not sure? → Start with hidden partitioning on most common filter column
    └── Evolve later without rewriting data
```

## Format Version Reference

| Feature | v1 | v2 | v3 |
|---------|:--:|:--:|:--:|
| Snapshots & time travel | Y | Y | Y |
| Schema evolution | Y | Y | Y |
| Hidden partitioning | Y | Y | Y |
| Partition evolution | Y | Y | Y |
| Position delete files | - | Y | Y |
| Equality delete files | - | Y | Y |
| Deletion vectors | - | - | Y |
| VARIANT type | - | - | Y |
| GEOMETRY/GEOGRAPHY | - | - | Y |
| Nanosecond timestamps | - | - | Y |
| Default column values | - | - | Y |
| Multi-arg transforms | - | - | Y |

## Format Comparison

| Capability | Iceberg | Delta Lake | Hudi |
|-----------|---------|------------|------|
| Origin | Netflix | Databricks | Uber |
| Data files | Parquet/ORC/Avro | Parquet only | Parquet/ORC |
| Metadata | JSON + Avro manifests | JSON/Parquet log | Avro timeline |
| Hidden partitioning | Yes | No | No |
| Partition evolution | Yes (metadata-only) | No | Limited |
| Schema evolution | Column-ID based | Column-name based | Column-name based |
| Row-level ops | COW + MOR + deletion vectors | Deletion vectors | COW + MOR |
| Engine support | 30+ engines | Spark-centric + growing | Spark/Flink/Presto |
| Catalog standard | REST Catalog spec | Unity Catalog | Timeline server |
| Branching/tagging | Native | None | None |
| Streaming | Flink, Spark SS | Spark SS, Flink | Spark SS, Flink |
