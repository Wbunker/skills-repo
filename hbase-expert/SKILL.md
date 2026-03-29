---
name: hbase-expert
description: "Expert knowledge of Apache HBase — the distributed, scalable, big data store built on Hadoop/HDFS. Based on 'HBase: The Definitive Guide' by Lars George (O'Reilly) and the Apache HBase Reference Guide (current). Use when the user asks about: HBase data model (tables, row keys, column families, cells, versions), shell commands, Java client API (Put/Get/Scan/Delete), filters, counters, coprocessors, admin API, schema design and row key patterns, MapReduce integration, bulk loading, architecture (HMaster, RegionServer, ZooKeeper, WAL, MemStore, HFile), region splits and compactions, security (Kerberos, ACLs, visibility labels), performance tuning, replication, snapshots, backup/restore, cluster administration, monitoring, or troubleshooting HBase issues."
---

# Apache HBase Expert

Based on *HBase: The Definitive Guide* by Lars George (O'Reilly) and the [Apache HBase Reference Guide](https://hbase.apache.org/book.html) (current stable).

## Architecture Overview

```
                          ┌─────────────────────────────────────────┐
                          │             ZooKeeper Quorum             │
                          │  (active master election, region state,  │
                          │   server health, distributed locks)      │
                          └────────────┬────────────────────────────┘
                                       │
               ┌───────────────────────▼──────────────────────────┐
               │                   HMaster                         │
               │  • Table/namespace DDL                            │
               │  • Region assignment & load balancing             │
               │  • Schema changes, splits coordination            │
               │  • Monitoring RegionServers                       │
               └───────────┬──────────────────────────────────────┘
                           │  assigns regions
       ┌───────────────────┼──────────────────────┐
       ▼                   ▼                       ▼
┌────────────┐      ┌────────────┐         ┌────────────┐
│RegionServer│      │RegionServer│   ...   │RegionServer│
│ Region 1   │      │ Region 2   │         │ Region N   │
│ ─────────  │      │ ─────────  │         │ ─────────  │
│ MemStore   │      │ MemStore   │         │ MemStore   │
│ BlockCache │      │ BlockCache │         │ BlockCache │
│ WAL (HLog) │      │ WAL (HLog) │         │ WAL (HLog) │
└──────┬─────┘      └──────┬─────┘         └──────┬─────┘
       │  flush             │ flush                │ flush
       ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────┐
│                   HDFS / HFiles                          │
│           (actual persistent storage layer)              │
└─────────────────────────────────────────────────────────┘
```

## Quick Decision Guide — Load the Right Reference

**What are you working on?**

| Task | Reference File |
|------|---------------|
| HBase concepts, data model, architecture overview | [ch01-02-intro-architecture.md](references/ch01-02-intro-architecture.md) |
| Installation, configuration, run modes, hbase-site.xml | [ch03-install-config.md](references/ch03-install-config.md) |
| Shell commands, basic Java API (Put/Get/Scan/Delete), batch ops | [ch04-client-api-basics.md](references/ch04-client-api-basics.md) |
| Filters, counters, coprocessors, advanced client patterns | [ch05-client-api-advanced.md](references/ch05-client-api-advanced.md) |
| Admin API, table/namespace management, cluster ops | [ch06-client-api-admin.md](references/ch06-client-api-admin.md) |
| MapReduce integration, bulk load, TableInputFormat/OutputFormat | [ch07-mapreduce.md](references/ch07-mapreduce.md) |
| Schema design, row key patterns, hotspot avoidance | [ch08-schema-design.md](references/ch08-schema-design.md) |
| Kerberos, ACLs, visibility labels, cell-level security | [ch09-security.md](references/ch09-security.md) |
| JVM tuning, compression, caching, hardware, benchmarking | [ch10-performance.md](references/ch10-performance.md) |
| Replication, snapshots, backup/restore, monitoring, troubleshooting | [ch11-operations.md](references/ch11-operations.md) |

## Key Facts (No Reference Load Required)

**Data model in one sentence:**
Rows are addressed by `(table, row key, column family:qualifier, timestamp)` → cell value (byte[]).

**Shell quick-start:**
```bash
hbase shell
> create 'mytable', 'cf'
> put 'mytable', 'row1', 'cf:col1', 'value1'
> get 'mytable', 'row1'
> scan 'mytable'
> disable 'mytable'; drop 'mytable'
```

**Three most common design mistakes:**
1. **Hotspotting** — sequential/timestamp row keys route all writes to one region; use salting, hashing, or reverse-timestamp
2. **Too many column families** — each CF flushes independently; keep to 1–3 CFs per table
3. **Wide rows vs. tall tables** — favor tall-and-narrow over wide rows for scan efficiency

**Write path in brief:** Client → RegionServer WAL → MemStore → (flush when full) → HFile on HDFS

**Read path in brief:** BlockCache → MemStore → HFile(s) on HDFS (via bloom filters + row key index)
