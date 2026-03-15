---
name: delta-lake-expert
description: >
  Delta Lake expert covering ACID lakehouse operations, performance tuning, streaming,
  governance, and architecture. Based on "Delta Lake: The Definitive Guide" (Denny Lee et al.,
  O'Reilly 2024). Use when: implementing Delta Lake tables, writing MERGE/UPDATE/DELETE
  operations, tuning performance (liquid clustering, Z-ordering, OPTIMIZE, VACUUM), designing
  medallion architectures, setting up streaming pipelines with Delta, configuring Change Data
  Feed, implementing SCD Type 2, comparing Delta vs Iceberg vs Hudi, or troubleshooting Delta
  Lake issues. Triggers on: /delta-lake-expert, "Delta Lake", "delta table", "OPTIMIZE",
  "VACUUM", "liquid clustering", "Z-order", "medallion architecture", "Change Data Feed",
  "UniForm", "deletion vectors", "time travel", "schema evolution", or "lakehouse".
---

# Delta Lake Expert

Expert guidance for Delta Lake — the open-source ACID storage layer for data lakehouses. Covers Delta Lake through version 4.0, including liquid clustering, UniForm, deletion vectors, coordinated commits, and the Variant type.

## Architecture at a Glance

```
Delta Table
├── _delta_log/                    ← Transaction log (single source of truth)
│   ├── 000000.json                ← Commit 0: table creation
│   ├── 000001.json                ← Commit 1: data write
│   ├── ...
│   └── 000010.checkpoint.parquet  ← Checkpoint every 10 commits
├── part-00000-*.parquet           ← Data files (Parquet format)
├── part-00001-*.parquet
└── deletion_vector_*.bin          ← Deletion vector bitmaps (if enabled)
```

Every write creates a JSON commit in `_delta_log/`. Readers replay the log to determine which files are valid. MVCC ensures readers never see partial writes.

## Quick Reference

| Operation | SQL | When to read |
|-----------|-----|-------------|
| Create / Read / Update / Delete | `CREATE TABLE`, `SELECT`, `UPDATE`, `DELETE` | `references/operations.md` (Ch 3-5) |
| MERGE (upsert, SCD2, dedup) | `MERGE INTO target USING source ON ...` | `references/operations.md` (Ch 3-5) |
| Time Travel | `SELECT * FROM t VERSION AS OF 5` | `references/operations.md` (Ch 3-5) |
| OPTIMIZE / VACUUM | `OPTIMIZE t`, `VACUUM t RETAIN 168 HOURS` | `references/performance.md` (Ch 10-11) |
| Liquid Clustering | `CREATE TABLE t (...) CLUSTER BY (col)` | `references/performance.md` (Ch 10-11) |
| Z-Ordering | `OPTIMIZE t ZORDER BY (col)` | `references/performance.md` (Ch 10-11) |
| Streaming (source/sink) | `readStream`/`writeStream` | `references/streaming.md` (Ch 7) |
| Change Data Feed | `table_changes('t', version)` | `references/streaming.md` (Ch 7) |
| Schema enforcement/evolution | `mergeSchema`, `ALTER TABLE` | `references/operations.md` (Ch 3-5) |
| UniForm / Deletion Vectors | Table properties | `references/advanced-features.md` (Ch 6, 8) |
| Medallion Architecture | Bronze → Silver → Gold | `references/architecture.md` (Ch 9) |
| Governance / Security / Sharing | RBAC, RLS, Delta Sharing | `references/governance.md` (Ch 12-14) |

## Reference Files

| File | Chapters | When to read |
|------|----------|-------------|
| `references/foundations.md` | Ch 1-2 | Delta Lake internals, transaction protocol, MVCC, setup |
| `references/operations.md` | Ch 3-5 | CRUD, MERGE, time travel, schema evolution, table maintenance |
| `references/streaming.md` | Ch 7 | Streaming ingestion/consumption, CDF, Auto Loader, DLT |
| `references/advanced-features.md` | Ch 6, 8 | Native apps, deletion vectors, UniForm, generated columns, constraints |
| `references/architecture.md` | Ch 9 | Medallion architecture, lakehouse design, Delta Sharing protocol |
| `references/performance.md` | Ch 10-11 | Liquid clustering, Z-ordering, file sizing, OPTIMIZE, VACUUM, Bloom filters, design patterns |
| `references/governance.md` | Ch 12-14 | Security, RBAC, data masking, metadata management, Unity Catalog, data lineage |

## Decision Trees

### "Which clustering strategy?"

```
New table? ──yes──→ Use CLUSTER BY (liquid clustering)
  │
  no
  │
Existing Z-ordered table?
  │
  ├─ Query patterns stable ──→ Keep Z-ordering, migrate when convenient
  │
  └─ Query patterns evolving ──→ Migrate to liquid clustering
     (ALTER TABLE t CLUSTER BY (new_cols))

Hive-partitioned table?
  │
  ├─ Low cardinality (<1000 values) ──→ Keep partitioning
  │
  └─ High cardinality or evolving ──→ Migrate to liquid clustering
     (incompatible with Hive partitioning — requires table rewrite)
```

### "How to handle small files?"

```
Streaming ingestion? ──yes──→ Enable auto compaction + optimized writes
  │                           delta.autoOptimize.autoCompact = true
  no                          delta.autoOptimize.optimizeWrite = true
  │
Batch loads? ──yes──→ Schedule OPTIMIZE nightly
  │                   Use predicate-based: OPTIMIZE t WHERE date = '...'
  no
  │
Table > 1TB? ──yes──→ Both: auto compaction + scheduled OPTIMIZE
```

### "VACUUM frequency?"

```
High-volume streaming ──→ Daily VACUUM, 168h retention
Batch (daily loads)   ──→ Weekly VACUUM, 168h retention
Slowly changing data  ──→ Monthly VACUUM, 720h retention
Long-running queries  ──→ Increase retention to cover max query duration
```

## Version Quick Reference

| Version | Key Features |
|---------|-------------|
| **3.0** | Liquid clustering (preview), UniForm (preview), deletion vectors (preview) |
| **3.2** | Liquid clustering GA, UniForm Hudi support, type widening (preview), inventory vacuum |
| **4.0** | Coordinated commits (preview), Variant type (preview), type widening GA, row tracking, UniForm GA, delta-rs 1.0 |

## Format Comparison

| Feature | Delta Lake | Apache Iceberg | Apache Hudi |
|---------|-----------|---------------|-------------|
| ACID | Yes | Yes | Yes |
| Time travel | Version + timestamp | Snapshot-based | Timeline-based |
| Schema evolution | Full | Full | Full |
| Partition evolution | Via liquid clustering | Hidden partitioning (native) | Coarse + fine clustering |
| Streaming | Strong (Spark, Flink) | Growing | Strong (DeltaStreamer) |
| Incremental reads | CDF (full CDC) | Appends only (native) | Full CDC |
| Cross-format | UniForm (Iceberg + Hudi) | None | Native Iceberg support |
| Best for | Spark-centric, Databricks | Multi-engine analytics | High-throughput CDC |
