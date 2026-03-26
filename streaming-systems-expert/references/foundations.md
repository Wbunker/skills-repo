# Streaming Systems — Foundations (Chapter 1)

## What Is Streaming?

Streaming is a type of data processing engine designed for **unbounded data** — datasets that are infinite in size and grow continuously. The term is often overloaded; the book distinguishes two axes:

### Cardinality
- **Bounded data**: finite datasets; processing has a defined end point (traditional batch)
- **Unbounded data**: infinite, ever-growing datasets; processing never fully completes

### Constitution
- **Streams**: data in motion — individual records flowing as they arrive
- **Tables**: data at rest — a snapshot of accumulated state at some point in time

These axes are orthogonal. Batch systems operate on bounded data; streaming systems handle unbounded data. But the same underlying stream-and-table model applies to both.

---

## On the Limitations of Streaming (Corrected)

The common assertion that streaming systems are approximate, low-latency, high-throughput alternatives to batch is historically accurate but no longer technically necessary. Two things were missing:

1. **Correctness** — the ability to produce accurate results equivalent to a batch computation
2. **Tools for reasoning about time** — specifically event time vs. processing time

Modern streaming systems (MillWheel, Dataflow, Flink) address both. The Lambda Architecture (running batch and streaming in parallel and merging results) exists to paper over these gaps — it is a workaround for inadequate streaming systems, not a fundamental requirement.

---

## Event Time vs. Processing Time

### Definitions
- **Event time**: the time at which an event actually occurred; embedded in the data record
- **Processing time**: the time at which the pipeline observes the event; wall-clock time of arrival

### The Gap: Skew
Event time and processing time are never equal in practice. The difference — **skew** — varies due to:
- Network transit delays
- Processing backlog
- Distributed system scheduling
- Source batching (e.g., mobile apps that buffer events offline)

Skew is non-deterministic and can be arbitrarily large.

### Implications
- Processing-time windowing is simple but produces results that depend on **when** data arrives, not **when events happened** — results are meaningless for event-time analysis
- Event-time windowing produces semantically correct results but requires handling **out-of-order data** and answering: when is a window complete?

```
Event time:      ──────────────────────────►
                    ↑                ↑
Processing time: ──────────────────────────►
                 |← skew varies here →|
```

---

## Data Processing Patterns

### Bounded Data
Classic batch processing: read all data, apply transformations, write output. Straightforward because the dataset is complete and finite. MapReduce, Spark batch, and SQL on tables are examples.

### Unbounded Data: Batch Approaches
Batch systems handle unbounded data by repeatedly processing bounded slices:

**Fixed windows (repeated batch runs)**
- Slice the unbounded stream into fixed time windows (e.g., hourly)
- Run a batch job over each window when it is believed complete
- Simple but:
  - Requires waiting for a window to "close" — introduces latency equal to the window size
  - Late-arriving data lands in the wrong window or is dropped
  - No in-window freshness

**Sessions via batching**
- Sessions require grouping activity within a gap — hard to express as simple time slices
- Approximated by taking a batch window larger than the max session gap and post-processing
- Inelegant; still suffers from the fixed-window latency/correctness tradeoffs

### Unbounded Data: Streaming Approaches

**Time-agnostic processing**
- No temporal reasoning at all; process each element as it arrives
- Filters, maps, projections — purely element-wise
- Completely correct by nature; no windowing complexity

**Approximation algorithms**
- Streaming k-means clustering, Top-N, HyperLogLog, count-min sketch
- Process unbounded data with bounded memory
- Tradeoff: approximate answers; low latency
- Useful when exact results are not required

**Windowing by processing time**
- Assign events to windows based on when they arrive at the pipeline
- Simple: no need to track event time; windows close cleanly at wall-clock boundaries
- Incorrect for event-time analysis: the window contains whatever arrived, not what happened

**Windowing by event time**
- Assign events to windows based on their embedded event timestamps
- Semantically correct: window contains what happened during that time period
- The gold standard for most analytics use cases
- Core challenge: **completeness** — how do you know when all events for a window have arrived?
  - You can't know with certainty for unbounded, skewed data
  - The watermark is the answer: a heuristic or perfect estimate of event-time completeness

---

## Why Event-Time Windowing Is Hard

The fundamental tension:

- **Completeness**: you want to wait until all data for a window has arrived before emitting results
- **Latency**: waiting longer increases result delay
- **Unbounded data**: for infinite streams, there is no guaranteed "all data has arrived" moment

This is the problem that watermarks (Chapter 3) and triggers (Chapter 2) solve: they decouple the notion of "when is a window complete enough to emit" from the physical arrival of data.

---

## Key Terminology Summary

| Term | Meaning |
|------|---------|
| Bounded data | Finite dataset; has a defined end |
| Unbounded data | Infinite, continuously growing dataset |
| Event time | Timestamp when the event occurred (in the data) |
| Processing time | Timestamp when the pipeline sees the event |
| Skew | Gap between event time and processing time |
| Lambda Architecture | Parallel batch + streaming systems merged at query time; a workaround for weak streaming |
| Windowing | Subdividing a dataset along temporal or other boundaries for aggregation |
