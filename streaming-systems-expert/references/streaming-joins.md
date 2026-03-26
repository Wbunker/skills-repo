# Streaming Systems — Streaming Joins (Chapter 9)

## All Joins Are Streaming Joins

The chapter's central thesis: **all joins are fundamentally grouping operations**. Therefore, all joins can be expressed as streaming joins.

Recall from the streams-and-tables model (Chapter 6): grouping operations convert a stream into a table. A join groups records from two streams by a join key and accumulates matching pairs. This is the same operation whether the input is bounded or unbounded.

**Corollary**: a "batch join" is just a streaming join where the input streams are bounded. The join algorithm is the same; only the input cardinality differs.

---

## Unwindowed Joins

Unwindowed joins operate over the **complete unbounded history** of both input streams, with no time-based scoping. Every record from stream L is potentially joinable with every record from stream R that shares the same key.

In the streams-and-tables model: both L and R contribute to a table keyed by the join key. The join result is triggered when matching records exist in both tables.

For all unwindowed join types, consider:
- Stream L (left input)
- Stream R (right input)
- Join key: some attribute common to both streams

### FULL OUTER Join

Emit a result for every record in L and every record in R, whether or not a match exists.

```
L: (key=A, val=1) arrives → emit (key=A, L=1, R=null)
R: (key=A, val=2) arrives → emit retraction of (key=A, L=1, R=null),
                              emit (key=A, L=1, R=2)
```

Behavior over time:
- When an L record arrives with no matching R: emit partial result with R=null
- When the matching R later arrives: retract the partial result; emit the complete result
- And vice versa for R arriving first

This requires retractions: partial results must be retracted when they are superseded by complete results. The accumulating-and-retracting mode is implied.

### LEFT OUTER Join

Like FULL OUTER, but only records in L are guaranteed to appear in the output. Records in R with no matching L are discarded.

```
L: (key=A, val=1) arrives → emit (key=A, L=1, R=null)
R: (key=A, val=2) arrives → retract (key=A, L=1, R=null), emit (key=A, L=1, R=2)
R: (key=B, val=3) arrives → no matching L exists; discard
```

Still requires retractions for L records that initially have no matching R.

### RIGHT OUTER Join

Mirror of LEFT OUTER: R records are guaranteed to appear; L records with no match are discarded.

### INNER Join

Only emit results where both L and R have a matching record. No partial results.

```
L: (key=A, val=1) arrives → buffer in state; no output yet
R: (key=A, val=2) arrives → match found; emit (key=A, L=1, R=2)
R: (key=B, val=3) arrives → buffer in state; no output yet
```

INNER joins require less state complexity than OUTER joins because no retractions are needed — results are only emitted when complete. However, state for unmatched records accumulates until a match arrives (or until allowed lateness/GC).

### ANTI Join

Emit records from L that have **no matching record in R**. The logical complement of the INNER join from L's perspective.

```
L: (key=A, val=1) arrives → emit (key=A, L=1) (no R match yet)
R: (key=A, val=2) arrives → retract (key=A, L=1) (R match found; L no longer qualifies)
```

ANTI joins require retractions: when an L record initially has no match (and is emitted), it must be retracted if an R match later arrives.

### SEMI Join

Emit records from L for which **at least one matching record exists in R**. Like INNER join output, but only including L's columns.

```
L: (key=A, val=1) arrives → buffer; no output yet
R: (key=A, val=2) arrives → match found; emit (key=A, L=1)  ← only L's columns
R: (key=A, val=3) arrives → already matched key=A; no additional output
```

SEMI joins deduplicate on the existence of any match — only the first R match triggers output for each L record.

---

## Windowed Joins

Windowed joins scope the join to records that fall within the **same time window**. This bounds the state each side must accumulate, unlike unwindowed joins which must hold state indefinitely.

### Fixed-Window Joins

Assign each record from L and R to a fixed event-time window. Only join records that fall in the same window.

```
Window: 1-hour fixed windows
L: (key=A, event_time=10:15, val=1) → window [10:00, 11:00)
R: (key=A, event_time=10:45, val=2) → window [10:00, 11:00)
→ Match: same key, same window → emit

L: (key=A, event_time=10:15, val=1) → window [10:00, 11:00)
R: (key=A, event_time=11:05, val=3) → window [11:00, 12:00)
→ No match: different windows → no emit
```

**Advantages**:
- State is bounded: each window holds state only for records in that window's time range
- Windows close and state is GC'd after allowed lateness
- Well-suited for joining two streams of concurrent events (e.g., clicks and impressions in the same minute)

**Disadvantages**:
- Records near window boundaries may miss matches that cross the boundary
- Requires both streams to have accurate event times

### Temporal Validity Joins

A **temporal validity join** models the concept of **slowly-changing dimensions** or **point-in-time correctness**. One stream (the "fact" stream) is joined to another stream (the "dimension" stream) where each dimension record is valid from its timestamp until the next update.

Use case: joining a stream of product purchases to a price catalog, where prices change over time. A purchase at 10:15 should use the price that was active at 10:15 — not the current price.

Model:
- Dimension stream: each record is valid from its event time until the next record for the same key
- Fact stream: join each fact record to the dimension record that was valid at the fact's event time

```
Price catalog (dimension):
  (product=A, price=10.00, effective_time=08:00)  ← valid 08:00 to 14:00
  (product=A, price=12.00, effective_time=14:00)  ← valid 14:00 onwards

Purchase stream (fact):
  (product=A, quantity=3, event_time=10:15) → join to price $10.00 → total $30.00
  (product=A, quantity=2, event_time=15:30) → join to price $12.00 → total $24.00
```

**Implementation**:
- The dimension stream is materialized into a table (accumulated state per key)
- Each dimension record replaces the previous for its key, with the previous record's validity range closed at the new record's timestamp
- Fact records are looked up against the table using the fact's event time to find the applicable dimension version

This is a natural fit for the streams-and-tables model: the dimension stream feeds a table; the fact stream is joined to that table with a time-based predicate.

**Temporal validity joins are the streaming equivalent of SQL's point-in-time joins** (also called "AS OF" joins in some SQL dialects).

---

## Join State and GC

All streaming joins require state:
- Unwindowed joins: state can grow without bound (every unmatched record is held)
- Windowed joins: state is bounded by window size + allowed lateness
- Temporal validity joins: dimension state = one record per key (constant size); fact-side GC via watermark

For unwindowed joins, allowed lateness (or an explicit GC policy) is essential to prevent unbounded state growth. Without GC, records that never find a match would be held in state forever.

---

## Summary

| Join Type | Output includes | Retractions required? | State bounded? |
|-----------|----------------|----------------------|----------------|
| FULL OUTER (unwindowed) | All L + all R (partial until matched) | Yes | No (without GC) |
| LEFT OUTER (unwindowed) | All L (partial until R arrives) | Yes (for L) | No (without GC) |
| RIGHT OUTER (unwindowed) | All R (partial until L arrives) | Yes (for R) | No (without GC) |
| INNER (unwindowed) | Only matched pairs | No | No (without GC) |
| ANTI (unwindowed) | L with no R match | Yes | No (without GC) |
| SEMI (unwindowed) | L with ≥1 R match | No | No (without GC) |
| Fixed-window join | Matched pairs within same window | Depends on join type | Yes (window + lateness) |
| Temporal validity join | Fact joined to valid dimension version | Depends | Dimension: Yes; Fact: with watermark |
