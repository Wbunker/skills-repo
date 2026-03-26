# Streaming Systems — Streaming SQL (Chapter 8)

Note: This chapter is described by the authors as largely aspirational at the time of publication (2018). It proposes a theoretical vision for what streaming SQL should be, rather than documenting an existing implementation.

## What Is Streaming SQL?

Classic SQL operates on **tables** — snapshots of data at a point in time. A query returns a result set (another table snapshot). This is the **table-biased** view of data.

For streaming, we want SQL to operate on **continuously evolving data** and produce **continuously updating results**. The challenge: SQL's relational algebra was designed for static sets, not for data that changes over time.

The chapter argues that the right foundation for streaming SQL is **Time-Varying Relations (TVRs)** — an extension of classical relations that incorporates the temporal dimension.

---

## Relational Algebra Foundations

Classical relational algebra operates on **relations**: sets of tuples (rows). SQL is a surface language over relational algebra.

Key operations:
- **Selection** (WHERE): filter rows
- **Projection** (SELECT columns): restrict columns
- **Join**: combine two relations based on a predicate
- **Group-by/aggregate**: partition rows into groups and apply aggregate functions

All operations take relations as input and produce relations as output. The model is **closed**: relations in, relations out. This is the mathematical basis for SQL's composability.

**Problem**: relations are sets of tuples at a single point in time. They have no concept of "the data changed" or "a new row arrived."

---

## Time-Varying Relations (TVRs)

A **Time-Varying Relation** is a relation that evolves over time. Rather than a static set of tuples, a TVR is a function:

```
TVR(t) → Relation   for all t ∈ time
```

At any point in time t, a TVR produces the relation that was true at that time.

**Examples**:
- A database table with an edit history is a TVR: at time t, it contains the rows that existed at t
- A streaming Kafka topic is a TVR: at time t, it contains all messages up to offset corresponding to t
- A Beam windowed aggregation is a TVR: at any processing time t, the current best estimate of each window's aggregate

**Key insight**: **all streams and tables are TVRs**. They are different representations of the same underlying concept. A table is a TVR you query at a specific time; a stream is a TVR you query as it changes.

**Why this matters**: if all data is TVRs, then relational algebra applied to TVRs unifies streaming and batch SQL under one model.

---

## Stream-Biased vs. Table-Biased Approaches

### The Beam Model: Stream-Biased

The Beam Model defaults to **stream** as the primary representation:
- The physical view of a computation is a stream (records flowing through)
- Tables are explicit materializations of stream state
- To get a table, you must explicitly accumulate and materialize a stream

In stream-biased SQL, a query on a TVR returns a **stream of changes** to the result. This is like SQL applied to a changelog.

### Classic SQL: Table-Biased

Classic SQL defaults to **table** as the primary representation:
- Queries operate on tables and return tables (static snapshots)
- Streaming is an afterthought — many streaming SQL systems (Flink SQL, Spark SQL) add streaming as an extension to table-based SQL

In table-biased SQL, a query on a TVR conceptually returns a **table snapshot** at the current moment. To get continuous updates, you need special syntax (e.g., `EMIT CHANGES` in ksqlDB).

### The Author's Argument

Neither bias is correct in isolation. A robust streaming SQL should:
- Let the user choose whether they want a stream (continuous changes) or a table (current snapshot) as the query output
- Use explicit keywords to make this choice syntactically visible

---

## Looking Forward: Toward Robust Streaming SQL

The chapter proposes several extensions to classical SQL to make it streaming-capable.

### Stream and Table Selection

Add explicit keywords to choose the physical view of a TVR:

```sql
-- Returns a continuously updating stream of changes to the result
SELECT STREAM order_id, total FROM orders WHERE status = 'shipped';

-- Returns the current snapshot of the result as a table
SELECT TABLE order_id, total FROM orders WHERE status = 'shipped';
```

`SELECT STREAM`: I want a changelog of how the result changes over time.
`SELECT TABLE`: I want the current state of the result.

Both operate on the same underlying TVR. The difference is in how the output is physically represented.

### Temporal Operators

**WHERE clause windowing** (per-row time filtering):
```sql
-- Select all rows where event_time is within the last hour
SELECT * FROM events
WHERE event_time > CURRENT_TIMESTAMP - INTERVAL '1 hour'
```
This is a **filter** on event time — not a window aggregation. The window here is a sliding per-row filter.

**GROUP BY windowing** (aggregation windows):
```sql
-- Count events per hour (tumbling window)
SELECT TUMBLE_START(event_time, INTERVAL '1 hour') AS window_start,
       COUNT(*) AS event_count
FROM events
GROUP BY TUMBLE(event_time, INTERVAL '1 hour')
```
This is the standard windowed aggregation. The window is defined in the GROUP BY clause.

**HAVING as trigger analog**:
```sql
-- Only emit groups when count exceeds a threshold
SELECT user_id, COUNT(*) as cnt
FROM events
GROUP BY user_id
HAVING COUNT(*) > 100
```
`HAVING` acts as a filter on the grouped table — semantically similar to a trigger that only fires when a condition is met.

### Mapping SQL Constructs to Beam Model

| SQL Construct | Beam Model Equivalent |
|---------------|----------------------|
| `SELECT` (nongrouping) | Nongrouping transform (element-wise) |
| `GROUP BY` | Windowed grouping transform (stream → table) |
| `SELECT STREAM` (output) | Table-to-stream trigger |
| `SELECT TABLE` (output) | Table materialization |
| `WHERE` on time column | Row-level time filter |
| `HAVING` | Trigger condition on grouped table |
| Window function in `GROUP BY` | Window assignment (Where in Beam model) |
| Watermark (implicit) | When in Beam model |
| Retraction/upsert semantics | How (accumulation mode) |

---

## Time-Varying Relations in Practice

**TVR operators are closed**: applying any relational algebra operation to TVRs produces another TVR.

This means:
- A join of two TVRs produces a TVR
- A group-by aggregation of a TVR produces a TVR
- SQL queries on TVRs compose just like SQL queries on static tables

The result is a unified relational model that handles:
- **Batch queries**: query a TVR at a specific historical time → returns a static relation
- **Streaming queries**: query a TVR continuously → returns an ongoing stream of relation changes
- **Mixed queries**: join a historical table (static TVR) with a live stream (evolving TVR)

This is the theoretical foundation the authors believe streaming SQL should be built on.

---

## State of Streaming SQL (as of book publication, 2018)

At time of publication, no major system fully implemented the TVR model:
- **Apache Flink SQL**: windowed aggregations, basic streaming joins; table-biased; improving rapidly
- **Apache Kafka / ksqlDB**: stream-biased; some streaming SQL capabilities; limited time semantics
- **Google BigQuery**: table-biased; no native streaming SQL at the time
- **Apache Calcite**: the underlying SQL parser/optimizer used by many systems; adding streaming extensions

The authors' conclusion: the field was converging toward better streaming SQL, but no system had yet fully realized the TVR vision.
