---
name: apache-hudi-expert
description: Apache Hudi table format expertise covering timeline architecture, COW vs MOR table types, write/read operations, query types (snapshot, incremental, CDC, time travel), indexing strategies, table services (compaction, clustering, cleaning), Hudi Streamer ingestion, concurrency control (OCC/NBCC/MVCC), production tuning, and lakehouse architecture. Use when designing Hudi tables, choosing between COW and MOR, configuring indexes, implementing CDC pipelines, tuning compaction and clustering, managing multiwriter concurrency, or building medallion architecture lakehouses.
---

# Apache Hudi Expert

Based on "Apache Hudi: The Definitive Guide" by Shiyan Xu, Prashant Wason, Bhavani Sudha Saktheeswaran, and Rebecca Bilbro (O'Reilly, 2025).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HUDI TABLE                                │
│                                                                  │
│  .hoodie/                    ← TIMELINE (commit log)             │
│  ├── <ts>.commit             ← completed commit metadata         │
│  ├── <ts>.deltacommit        ← MOR log write                     │
│  ├── <ts>.compaction         ← compaction plan                   │
│  ├── <ts>.clean              ← cleaning action                   │
│  └── .hoodie_properties      ← table config                      │
│                                                                  │
│  partition=2024/01/          ← DATA FILES                        │
│  ├── <fileId>_<ts>.parquet   ← base file (COW & MOR)            │
│  └── <fileId>_<ts>.log       ← log file (MOR only, Avro)        │
│                                                                  │
│  FILE GROUP = one fileId across all versions                     │
│  FILE SLICE = base file + log files for one snapshot             │
└─────────────────────────────────────────────────────────────────┘

COW TABLE:                          MOR TABLE:
Write → rewrite Parquet base file   Write → append to .log file
Read  → read Parquet directly       Read  → merge base + logs (Snapshot)
                                    Read  → base only, no merge (Read Optimized)
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Architecture, timeline, table types, Hudi stack, getting started | [foundations.md](references/foundations.md) |
| Write flow, upsert/insert/delete/MERGE, key generators, schema evolution | [writing.md](references/writing.md) |
| Query types: snapshot, time travel, incremental, CDC, read-optimized | [reading.md](references/reading.md) |
| Bloom filter, record-level, bucket, HBase index — selection guide | [indexing.md](references/indexing.md) |
| Compaction, clustering, cleaning, deployment modes, layout optimization | [maintenance.md](references/maintenance.md) |
| Hudi Streamer (DeltaStreamer), Kafka/DFS/JDBC sources, schema evolution | [streamer.md](references/streamer.md) |
| CLI, catalog sync, monitoring, performance tuning, file sizing | [production.md](references/production.md) |
| OCC, NBCC, MVCC, multiwriter, three-step commit, locking | [concurrency.md](references/concurrency.md) |
| Medallion architecture, end-to-end lakehouse, Bronze/Silver/Gold/AI | [lakehouse.md](references/lakehouse.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–2 | Timeline, COW vs MOR, file groups/slices, Hudi stack, table design, first operations |
| `writing.md` | 3 | Write flow (5 phases), upsert/insert/delete/MERGE/overwrite, key generators, merge modes, bootstrapping |
| `reading.md` | 4 | Data structure on storage, snapshot/time-travel/incremental/CDC/read-optimized queries, query lifecycle |
| `indexing.md` | 5 | Bloom filter, record-level index, bucket index, HBase index, trade-off matrix, selection decision tree |
| `maintenance.md` | 6 | Compaction (MOR), clustering (COW+MOR), cleaning, inline/async/standalone deployment, layout strategies |
| `streamer.md` | 7 | Hudi Streamer architecture, sources (Kafka/DFS/JDBC), transformers, schema evolution, checkpointing, DQA |
| `production.md` | 8 | CLI operations, catalog sync (Hive/Glue/REST), monitoring, callbacks, file sizing, write/read/engine tuning |
| `concurrency.md` | 9 | Why concurrency is hard, OCC/NBCC/MVCC, three-step commit, conflict detection, locking providers, multiwriter |
| `lakehouse.md` | 10 | Medallion architecture, Bronze/Silver/Gold/AI layers, end-to-end pipeline design |

## Decision Trees

### COW vs MOR

```
What is your dominant workload?
├── Read-heavy, few updates (dashboards, BI reporting)
│   → Copy-on-Write (COW)
│     Writes rewrite full Parquet files (slow writes)
│     Reads are pure Parquet scan (fast, no merge overhead)
│
├── Write-heavy, high-frequency upserts (CDC, streaming)
│   → Merge-on-Read (MOR)
│     Writes append to .log files (fast writes)
│     Snapshot reads merge base + logs (slower reads)
│     Run compaction to convert logs → Parquet periodically
│
├── Need read-optimized AND near-real-time views?
│   → MOR (two query types available):
│     Read Optimized (RO): base Parquet only, max performance
│     Snapshot: base + logs merged, always current
│
└── Streaming ingestion with Kafka?
    → MOR + Hudi Streamer
      Log file writes match Kafka throughput patterns
```

### Index Selection

```
What is your key lookup pattern?
├── Single partition, record key known → Bloom Filter (default)
│   Fast probabilistic lookup within partition
│   Good: batch upserts to partitioned tables
│   Bad: global dedup across partitions
│
├── Global unique keys (cross-partition dedup)
│   ├── Medium scale (< billions of records) → Record-Level Index
│   │   Exact lookup, stored in Hudi metadata table
│   └── Very large scale, HBase cluster available → HBase Index
│       External index, fastest global lookup
│
├── Even key distribution, high write throughput
│   → Bucket Index
│   Consistent hash: no lookup needed at all
│   Keys always land in same file group bucket
│   Bad: hard to change bucket count later
│
└── Existing Hive/DynamoDB records to bootstrap?
    → Use Bootstrap operation first, then choose index
```

### Table Service Deployment Mode

```
How should compaction/clustering/cleaning run?
├── Simple pipelines, single Spark job
│   → Inline mode (hoodie.compact.inline=true)
│     Runs synchronously after each commit
│     Easy to configure; blocks writer between commits
│
├── High-throughput streaming, writer must not block
│   → Async mode
│     Schedule in writer job, execute in separate Spark job
│     Writer continues; services run in parallel
│
└── Dedicated maintenance jobs, separate from writers
    → Standalone mode (HoodieTableServiceManager / CLI)
      Full control over timing and resources
      Required for multiwriter setups
```

### Query Type Selection

```
What data do you need?
├── Latest complete view of the table → Snapshot Query
├── State at a specific past time → Time Travel Query
│     AS OF TIMESTAMP '2024-01-15 10:00:00'
├── Changes since last checkpoint (streaming pipelines) → Incremental Query
│     Returns only new/changed records since a beginTime
├── Full change events with before/after images → CDC Query
│     Returns op type (I/U/D) + before + after row images
└── Maximum read performance, slight staleness OK → Read Optimized (MOR only)
      Reads base Parquet files only; skips uncompacted logs
```

## Key Concepts

| Term | Definition |
|------|-----------|
| Timeline | Ordered log of all table actions in `.hoodie/`; source of truth for table state |
| Instant | A single action on the timeline (commit, deltacommit, compaction, clean, rollback) |
| File Group | All versions of a logical data file, identified by a stable fileId |
| File Slice | One version of a file group: a base file + any log files written since |
| Record Key | Unique identifier for a row within a partition |
| Precombine Field | Ordering field; when duplicate keys exist, the record with max value wins |
| COW | Copy-on-Write: writes rewrite Parquet base files; reads are pure Parquet scans |
| MOR | Merge-on-Read: writes append to Avro log files; reads merge on the fly |
| Compaction | MOR-only: merges log files into Parquet base files to reduce read overhead |
| Clustering | Reorganizes data across file groups for better layout (like Z-ordering) |
| Cleaning | Removes old file slices beyond retention policy to reclaim storage |
| Hudi Streamer | Continuous ingestion tool (formerly DeltaStreamer); reads from Kafka/DFS/JDBC |
| Bootstrap | Converts existing Parquet tables to Hudi without full data rewrite |
| OCC | Optimistic Concurrency Control: write freely, detect conflicts at commit |
| NBCC | Non-Blocking Concurrency Control: concurrent writes with finer conflict detection |

## Critical Config Quick Reference

```properties
# Table type
hoodie.table.type=COPY_ON_WRITE           # or MERGE_ON_READ

# Record identity
hoodie.datasource.write.recordkey.field=id
hoodie.datasource.write.partitionpath.field=date
hoodie.datasource.write.precombine.field=updated_at

# Write operation
hoodie.datasource.write.operation=upsert  # insert | bulk_insert | delete | insert_overwrite

# Index
hoodie.index.type=BLOOM                   # RECORD_LEVEL | BUCKET | HBASE | GLOBAL_BLOOM

# Compaction (MOR)
hoodie.compact.inline=true
hoodie.compact.inline.max.delta.commits=5

# Cleaning
hoodie.cleaner.commits.retained=10
```
