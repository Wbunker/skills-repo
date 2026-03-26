# Streaming Systems — Streams and Tables (Chapter 6)

This chapter is described by the authors as the conceptual heart of the book — a general theory that unifies batch and streaming processing under a single model.

## The Core Duality

**Table**: data at rest. A snapshot of accumulated state, identified by some key. A database table, a key-value store, a materialized view.

**Stream**: data in motion. A log of changes or events, ordered by time. A changelog, an event log, a Kafka topic.

The key insight: **tables and streams are two views of the same underlying data**.

```
Table → observe changes over time → Stream (changelog of the table)
Stream → group/accumulate over time → Table (materialization of the stream)
```

---

## The Four Fundamental Operations

### Streams → Tables (Grouping)
Any operation that **accumulates** data from a stream into a result produces a table:
- `GROUP BY` aggregation
- Windowed aggregations
- Joins that accumulate matching records
- Any stateful reduction

The stream feeds records into the table; the table grows (or changes) as records arrive.

### Tables → Streams (Triggering / Ungrouping)
Observing **changes to a table** produces a stream:
- A trigger fires on a window → emits the window result → this is a table-to-stream operation
- A database CDC (change data capture) stream is a table-to-stream operation
- Materializing a view at a point in time produces a snapshot stream

Triggers in the Beam model are precisely the table-to-stream mechanism.

### Streams → Streams (Nongrouping transforms)
Operations that process each element independently without accumulating state:
- Filter
- Map / flatMap
- Element-wise projections

These do not require tables; they pass through a pure stream-to-stream transformation.

### Tables → Tables (Materialized view / batch)
A batch job transforms one table into another:
- Read a full table, apply transformations, write a new table
- This is a degenerate case: the input stream is fully consumed (bounded), the output is materialized

---

## A Streams-and-Tables Analysis of MapReduce

MapReduce can be fully described in terms of streams and tables:

**Map phase**:
- Input: a table (files on HDFS)
- Table → Stream: read the table, emit each record as a stream event
- Apply nongrouping transforms (the map function)
- Output: a stream of key-value pairs

**Shuffle phase**:
- Group (sort + partition) the key-value stream by key
- Nongrouping (element-wise movement) followed by grouping: stream → table
- This is the stream-to-table operation

**Reduce phase**:
- Input: a table of grouped key-value lists
- Table → Stream: read each group as an input stream
- Apply reduction (the reduce function): stream → table (the output key-value table)
- Write results back to HDFS: table

The entire MapReduce pipeline is: Table → Stream → (nongrouping transforms) → Table (via shuffle) → Stream → Table (via reduce) → Table (output materialization).

**Key insight from this analysis**: batch and streaming are not fundamentally different. Batch processing is just a special case where the input stream is bounded (finite), the processing blocks until the bounded input is complete, and the output is materialized at the end. Streaming generalizes this to unbounded inputs with ongoing output materialization.

---

## Reconciling Batch and Streaming

Two questions the S&T model answers:

**1. How does batch processing fit into the streaming model?**
Batch is the degenerate case where:
- Input is bounded → the "stream" is finite
- Processing blocks until input is exhausted → equivalent to a single trigger on window close
- Output is materialized once → a single table write at the end
Batch = streaming with a perfect watermark (bounded input), a single watermark trigger, and accumulating mode.

**2. How do streams relate to bounded/unbounded data?**
Streams can be bounded or unbounded. The distinction is about cardinality of the underlying data, not about whether the processing model is batch or streaming. The S&T model handles both uniformly.

---

## What, Where, When, and How in a Streams-and-Tables World

### What: Transformations
- Nongrouping transforms: stream → stream (no tables involved)
- Grouping transforms: stream → table

### Where: Windowing
Windowing determines **which grouping bucket** a stream record falls into. It is an attribute of the grouping operation (stream → table). The window defines the key space of the output table.

### When: Triggers
Triggers are the **table → stream** operation. They declare when to materialize the current state of a table bucket (window) into an output stream record.

Without triggers: the table accumulates forever and never produces output.
With triggers: the table periodically emits its current state as output stream records.

### How: Accumulation
Accumulation describes how **successive materializations** of the same table bucket relate. The three modes (discarding, accumulating, accumulating+retracting) define the semantic relationship between successive trigger firings for the same window.

---

## The General Theory of Stream-Table Relativity

The book's most general formulation:

> All data processing is the movement of data between states of rest (tables) and motion (streams), via nongrouping transforms (stream→stream), grouping transforms (stream→table), and ungrouping (table→stream via triggers).

**Batch processing**: bounded stream → table (via grouping) → bounded stream (via read) → table (output)
**Streaming processing**: unbounded stream → table (via windowed grouping) → stream (via triggers) → ...

Both fit the same model. The difference is only in the cardinality of the input stream and the timing of materializations.

---

## Implications for System Design

**If streams and tables are equivalent views of the same data**:
- A Kafka topic is both a stream (reading records in order) and a table (the log compacted to latest value per key)
- A database table is both a table (reading the current state) and a stream (reading the CDC log)
- Any system that only speaks "streams" or only speaks "tables" is artificially limiting its expressiveness

**For API design**:
- An ideal processing API provides operations for all four transformations: stream→stream, stream→table (grouping), table→stream (triggers), table→table (batch materialization)
- Beam provides this; SQL (with TVR extensions from Chapter 8) can provide this

**For debugging**:
- Performance problems often arise at the stream→table boundary (grouping is expensive; state grows)
- Latency problems often arise at the table→stream boundary (triggers fire late; watermark is slow)
- Correctness problems often arise from wrong accumulation mode assumptions
