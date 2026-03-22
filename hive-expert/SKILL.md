---
name: hive-expert
description: >
  Expert-level Apache Hive knowledge for writing HiveQL, designing schemas, tuning queries,
  and administering Hive deployments. Use when the user asks about: HiveQL syntax (DDL, DML,
  SELECT, JOINs, window functions, CTEs), Hive data types, file formats (ORC, Parquet, Avro),
  partitioning and bucketing, ACID transactions, UDFs, performance tuning, Tez/Spark execution
  engines, Beeline CLI, Hive Metastore, security (Ranger, Kerberos), schema design patterns,
  or migrating/comparing Hive to Spark SQL / Presto / Trino. Covers Hive 2.x through 4.x.
  Organized after "Programming Hive" by Edward Capriolo (O'Reilly).
---

# Hive Expert

Apache Hive: SQL-on-Hadoop batch analytics engine. Translates HiveQL into execution plans
run on Tez (recommended), Spark, or MapReduce. Current stable: Hive 4.x.

## Architecture at a Glance

```
Client (Beeline / JDBC)
    │
    ▼
HiveServer2  ──► Metastore (MySQL/Postgres)
    │
    ▼
Compiler → Optimizer (CBO via Calcite) → Execution Engine
                                              │
                               ┌──────────────┼──────────────┐
                             Tez           Spark           MR (deprecated Hive 4)
                               │
                           HDFS / S3 / ADLS / GCS
```

- **Metastore**: stores table/partition/column metadata; shared by Hive, Spark, Impala, Trino
- **HiveServer2**: JDBC/ODBC endpoint; replaced HiveServer1 (now removed)
- **LLAP** (Live Long and Process): persistent daemon for sub-second queries; optional
- **Beeline**: current CLI (`beeline -u jdbc:hive2://host:10000`); `hive` CLI deprecated

## Quick Reference — Common Tasks

| Task | Load this reference |
|------|-------------------|
| Write DDL (CREATE/ALTER/DROP tables, partitions) | [references/ddl.md](references/ddl.md) |
| Load data, INSERT, UPDATE, DELETE, MERGE | [references/dml.md](references/dml.md) |
| Write SELECT queries, JOINs, aggregations, window functions | [references/queries.md](references/queries.md) |
| Built-in functions (string, date, math, aggregate, collection) | [references/functions.md](references/functions.md) |
| Data types, file formats, ORC, Parquet, SerDes | [references/data-types-formats.md](references/data-types-formats.md) |
| ACID transactions, UPDATE/DELETE/MERGE, compaction | [references/acid-transactions.md](references/acid-transactions.md) |
| Views and materialized views | [references/views.md](references/views.md) |
| Schema design: partitions, buckets, statistics | [references/schema-design.md](references/schema-design.md) |
| Performance tuning: Tez, CBO, vectorization, joins | [references/tuning.md](references/tuning.md) |
| Write UDFs, UDAFs, UDTFs | [references/udfs.md](references/udfs.md) |
| TRANSFORM...USING streaming | [references/streaming.md](references/streaming.md) |
| Security: auth, GRANT/REVOKE, Ranger | [references/security.md](references/security.md) |
| Beeline CLI, hiveconf/hivevar, key config properties | [references/cli-config.md](references/cli-config.md) |

## Key Hive vs SQL Differences

- `ORDER BY` = global sort (1 reducer); `SORT BY` = per-reducer sort; `DISTRIBUTE BY` = route rows to reducers
- `LEFT SEMI JOIN` replaces `WHERE col IN (subquery)` — more efficient
- No primary keys or unique constraints — enforced by application
- Managed tables (Hive 3+): default ORC + ACID; `DROP TABLE` deletes data
- External tables: `DROP TABLE` deletes metadata only; data stays
- Dynamic partitioning requires `SET hive.exec.dynamic.partition.mode=nonstrict`
- String literal: single quotes only — `'value'`, not `"value"`

## Version Notes

| Feature | Added |
|---------|-------|
| ACID INSERT/UPDATE/DELETE | Hive 0.14 (INSERT), Hive 2.0 (full) |
| MERGE | Hive 2.2 |
| CTE (WITH clause) | Hive 0.13 |
| Window functions | Hive 0.11 |
| Materialized views | Hive 3.0 |
| Managed tables auto-ACID | Hive 3.0 |
| Query result caching | Hive 3.1 |
| MapReduce deprecated | Hive 4.0 |
| Iceberg table support | Hive 4.0 |
