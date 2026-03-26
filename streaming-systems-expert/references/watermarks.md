# Streaming Systems — Watermarks (Chapter 3)

Author of this chapter: Slava Chernyak.

## Definition

A **watermark** is a monotonically increasing timestamp that represents event-time progress through an unbounded data stream:

> **W(t)**: all data with event time ≤ t is believed to have been received by the pipeline.

When the watermark advances past time T, the system declares: "I am confident (or sufficiently confident) that no more data with event time ≤ T will arrive."

This is the mechanism by which streaming systems answer the question: **"Is a window complete?"**

### Formal Properties
- Monotonically increasing: watermarks never move backward
- Represents a lower bound on the event times yet to be seen
- Does not prevent late data from arriving — it just signals expected completeness

---

## Source Watermark Creation

Watermarks are created at data sources and propagate through the pipeline.

### Perfect Watermark Creation

Possible when the source has **complete knowledge** of all data and its event times.

Examples:
- A finite file of log records with known timestamps
- A database snapshot with a known max event time
- A statically partitioned queue where all messages are present

With a perfect watermark: no late data will ever arrive past the watermark. The system can safely discard state and produce exact results. Triggers on the watermark produce perfectly correct outputs.

**Tradeoff**: perfect watermarks are only possible for bounded or fully-known sources. Most real streaming sources cannot provide them.

### Heuristic Watermark Creation

Produces an estimate of event-time completeness based on partial knowledge.

Common heuristics:
- Track the maximum event timestamp seen in recent data
- Subtract a fixed lag (e.g., 5 minutes) to account for typical skew: `watermark = max_event_time - lag`
- Use partition-level progress tracking (e.g., per-shard lag in Kafka)
- Track percentiles of event timestamps rather than the minimum

**Risk**: heuristic watermarks can be wrong:
- **Too slow** (conservative): watermark lags behind actual progress → unnecessary latency before windows fire
- **Too fast** (optimistic): watermark advances ahead of actual completeness → late data arrives after the watermark, producing late panes or dropped data

The allowed lateness setting (see [beam-model.md](beam-model.md)) handles heuristic watermark imprecision by giving windows a grace period after the watermark fires.

---

## Watermark Propagation

In a multi-stage pipeline, each stage has:
- **Input watermark**: the minimum watermark across all upstream inputs
- **Output watermark**: the minimum of:
  - The input watermark
  - The event times of all data currently held in-flight within this stage (not yet emitted)

```
Source → Stage A → Stage B → Stage C → Sink

Input watermark of Stage B = output watermark of Stage A
Output watermark of Stage A = min(input watermark of A, held event times in A)
```

This ensures that downstream stages correctly account for data that upstream stages are still processing.

### Understanding Watermark Propagation

Key insight: **a stage cannot advance its output watermark past the event time of data it is currently holding**.

If a stage buffers data (e.g., for windowing), its output watermark is held back by the oldest buffered event time. Only when data is emitted downstream does the output watermark advance.

This creates a natural propagation delay through pipeline stages. The overall end-to-end watermark is the minimum across all stages.

### Watermark Propagation and Output Timestamps

When a window fires and emits a result, that result record needs an event timestamp. The timestamp assigned to the output record determines how downstream stages treat it.

Common output timestamp strategies:
- **End of window**: use the window's end time as the output event timestamp
  - Semantically correct: "this aggregate represents events up to T"
  - Most common choice
- **Start of window**: use the window's start time
- **Max event time in window**: use the latest event timestamp seen in the window data

The choice matters because it determines how the output record is treated by downstream windows.

### The Tricky Case of Overlapping Windows

Sliding windows create an edge case. A single input event contributes to multiple overlapping output windows. The output watermark must be held back until all overlapping windows have fired — otherwise, an upstream stage's output watermark could advance past a window that still holds data.

This means sliding windows with many overlaps can create significant watermark propagation delay through a pipeline.

---

## Percentile Watermarks

Instead of tracking the minimum event time of all in-flight data, track a **percentile** of event times.

For example, a 99th-percentile watermark advances as soon as 99% of expected data has arrived, ignoring the slowest 1%.

**Benefits**:
- Dramatically reduces latency for the common case (99% of data arrives on time)
- Avoids stalling the entire pipeline on the single slowest record

**Tradeoff**:
- The 1% of data that arrives late will always produce late panes
- Results are not perfectly complete — the percentile determines the accuracy/latency tradeoff
- Best suited for use cases where missing 1% of data is acceptable (e.g., analytics, not billing)

---

## Processing-Time Watermarks

A separate watermark that tracks **processing-time progress** rather than event-time progress.

**Purpose**: detecting pipeline health, not data completeness.

A processing-time watermark answers: "Is the pipeline keeping up with data arrival? Is there a stuck stage?"

If the processing-time watermark stalls (stops advancing), it indicates:
- A stage is not making progress (stuck, crashed, or overwhelmed)
- The pipeline has fallen behind the rate of incoming data

**Use cases**:
- Monitoring and alerting on pipeline health
- Distinguishing between "the watermark is stalled because data has an old event time" vs. "the watermark is stalled because the pipeline itself is stuck"
- Setting timeouts for stages that should complete within a processing-time bound

Processing-time watermarks and event-time watermarks serve different purposes and should not be conflated.

---

## Case Studies

### Watermarks in Google Cloud Dataflow

Dataflow uses a **centralized watermark aggregation service**:
- Each worker reports the minimum event time of data it holds
- The service aggregates these reports to produce a global watermark
- Workers receive watermark updates and trigger window firings accordingly

Challenges:
- Aggregation service must be highly available (watermark stalls if it goes down)
- Workers report at intervals — watermark lags behind actual minimum slightly
- Dataflow uses a distributed barrier mechanism to ensure consistency

### Watermarks in Apache Flink

Flink uses a **decentralized, in-band watermark propagation** model:
- Watermark records are injected directly into the data stream as special records
- Each operator tracks the minimum watermark across all its input streams
- No centralized coordinator; watermarks flow with the data

Implications:
- Watermarks are as fresh as the data itself — low latency
- With multiple input streams, the watermark is bounded by the slowest input
- If one input partition stalls completely, the watermark stalls entirely
- Flink provides idle source detection to handle stalled partitions

### Source Watermarks for Google Cloud Pub/Sub

Pub/Sub is an unordered, at-least-once messaging system. Generating watermarks is challenging because:
- Messages may be delivered out of order
- Messages may be redelivered
- Retention is limited (7 days default); no guaranteed ordering within a subscription

Dataflow's approach:
- Track the oldest unacknowledged message timestamp across all Pub/Sub partitions
- Use that as the watermark basis (with a lag for delivery jitter)
- This is inherently heuristic — Pub/Sub cannot provide ordering guarantees

---

## Watermark Summary

| Property | Perfect Watermark | Heuristic Watermark |
|----------|-------------------|---------------------|
| Source knowledge required | Complete | Partial |
| Late data possible | No | Yes |
| Typical sources | Bounded files, known-complete queues | Kafka, Pub/Sub, network logs |
| Latency | Higher (waits for true completion) | Configurable (lag parameter) |
| Correctness | Perfect | Approximate (tunable by lag + allowed lateness) |
