---
name: streaming-systems-expert
description: Expert on large-scale streaming data processing — the Beam Model, watermarks, triggers, accumulation, streams-and-tables theory, exactly-once semantics, persistent state, streaming SQL, streaming joins, and the history of stream processing systems. Use when designing streaming pipelines, reasoning about event time vs. processing time, choosing windowing strategies, configuring watermarks and triggers, implementing exactly-once guarantees, managing pipeline state, or understanding how systems like Dataflow, Flink, Spark, and Kafka relate. Based on "Streaming Systems" by Tyler Akidau, Slava Chernyak, and Reuven Lax (O'Reilly, 2018).
---

# Streaming Systems Expert

Based on *Streaming Systems: The What, Where, When, and How of Large-Scale Data Processing*
by Tyler Akidau, Slava Chernyak, and Reuven Lax (O'Reilly, 2018).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE BEAM MODEL                                    │
│                                                                      │
│  WHAT are you computing?   → Transformations (grouping/nongrouping) │
│  WHERE in event time?      → Windowing (fixed/sliding/session)      │
│  WHEN in processing time?  → Triggers + Watermarks                  │
│  HOW do refinements relate?→ Accumulation (discard/accum/retract)   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │         STREAMS AND TABLES          │
         │                                     │
         │  Stream ──[grouping]──► Table       │
         │  Table  ──[trigger]──►  Stream      │
         │                                     │
         │  Nongrouping ops: stream → stream   │
         │  Grouping ops:    stream → table    │
         └────────────────────────────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │             TIME DOMAINS            │
         │                                     │
         │  Event Time ────────────────────►  │
         │       │  ↑ skew/lag varies          │
         │  Processing Time ───────────────►  │
         │                                     │
         │  Watermark = oldest unprocessed     │
         │             event time (heuristic   │
         │             or perfect)             │
         └────────────────────────────────────┘
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Streaming terminology, bounded vs. unbounded, event time vs. processing time, data processing patterns | [foundations.md](references/foundations.md) |
| What/Where/When/How framework, triggers, watermarks, accumulation modes, allowed lateness | [beam-model.md](references/beam-model.md) |
| Watermark mechanics, creation (perfect/heuristic), propagation, percentile watermarks, processing-time watermarks | [watermarks.md](references/watermarks.md) |
| Processing-time windows, session windows, custom windowing, unaligned windows | [advanced-windowing.md](references/advanced-windowing.md) |
| Exactly-once semantics, shuffle deduplication, idempotent/transactional sinks, Flink snapshots, Spark micro-batch | [exactly-once.md](references/exactly-once.md) |
| Streams-and-tables theory, MapReduce analysis, unifying batch and streaming, TVR generalization | [streams-and-tables.md](references/streams-and-tables.md) |
| Persistent state, raw grouping, incremental combining, generalized state API, timers, conversion attribution | [persistent-state.md](references/persistent-state.md) |
| Streaming SQL, time-varying relations, temporal operators, SELECT STREAM vs SELECT TABLE | [streaming-sql.md](references/streaming-sql.md) |
| Streaming joins (INNER, OUTER, ANTI, SEMI), windowed joins, temporal validity joins | [streaming-joins.md](references/streaming-joins.md) |
| History: MapReduce, Hadoop, Flume, Storm, Spark, MillWheel, Dataflow, Kafka, Flink, Beam | [history.md](references/history.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | Ch. 1 | Streaming terminology, cardinality, bounded/unbounded, event time vs. processing time, Lambda Architecture critique, processing patterns |
| `beam-model.md` | Ch. 2 | What/Where/When/How questions, windowing, triggers (per-record, watermark, compound), early/on-time/late panes, allowed lateness, accumulation modes |
| `watermarks.md` | Ch. 3 | Watermark definition, perfect vs. heuristic creation, propagation through stages, output timestamps, percentile watermarks, processing-time watermarks, Dataflow/Flink/Pub/Sub case studies |
| `advanced-windowing.md` | Ch. 4 | Processing-time windows via triggers vs. ingress time, session windows, custom windowing, unaligned fixed windows, per-element windows, bounded sessions |
| `exactly-once.md` | Ch. 5 | Why exactly-once matters, accuracy vs. completeness, side effects, shuffle deduplication, Bloom filters, GC, source checkpointing, idempotent/transactional sinks, Flink Chandy-Lamport, Spark micro-batch |
| `streams-and-tables.md` | Ch. 6 | Stream/table duality, streams→tables (grouping), tables→streams (triggers), MapReduce analysis, nongrouping/grouping ops, windowing in S&T model, general theory of stream-table relativity |
| `persistent-state.md` | Ch. 7 | Failure and correctness motivation, raw grouping, incremental combining (CombineFn), generalized state + timers API, conversion attribution case study |
| `streaming-sql.md` | Ch. 8 | Relational algebra foundations, time-varying relations (TVRs), stream-biased vs. table-biased approaches, SELECT STREAM/TABLE, temporal operators, WHERE vs. GROUP BY windowing |
| `streaming-joins.md` | Ch. 9 | Joins as grouping operations, unwindowed joins (FULL/LEFT/RIGHT OUTER, INNER, ANTI, SEMI), fixed-window joins, temporal validity joins (slowly-changing dimensions) |
| `history.md` | Ch. 10 | MapReduce, Hadoop, Flume/FlumeJava, Storm, Spark, MillWheel, Cloud Dataflow, Kafka, Flink, Beam — contributions and limitations of each |

## Core Decision Trees

### What Windowing Strategy Do You Need?

```
What is the temporal structure of your computation?
│
├── No temporal grouping needed (pure element-wise transforms)
│   └── No windowing — nongrouping transformation
│       → stream-to-stream operation; no state accumulation
│
├── Align windows to fixed time boundaries (hourly reports, daily batches)
│   └── Fixed windows
│       ├── Aligned (default) — all keys share same window boundaries
│       │   → resource spikes at window boundaries; simpler reasoning
│       └── Unaligned — per-key offset boundaries
│           → smooths resource usage; trades simplicity for efficiency
│
├── Overlapping windows (rolling averages, sliding aggregates)
│   └── Sliding windows — window size + slide period
│       → each element appears in multiple windows; higher cost
│
├── Activity-based grouping (user sessions, event bursts)
│   └── Session windows — gap-based, data-driven
│       ├── Unbounded sessions (gap timeout only)
│       ├── Bounded by duration — cap session length
│       └── Bounded by element count — cap session size
│
└── Processing-time snapshots (legacy batch compatibility, no event-time skew)
    └── Processing-time windows
        ├── Via triggers — global event-time window + processing-time trigger
        └── Via ingress time — stamp events with arrival time at source
            → simpler but loses event-time ordering
```

### When Should Results Be Materialized? (Trigger Choice)

```
When do you want output from a window?
│
├── As fast as possible (low latency, accept multiple updates)
│   └── Per-record trigger (repeated update)
│       → highest throughput of partial results; downstream must handle restatement
│
├── On a processing-time delay (throttle output rate)
│   └── Processing-time trigger (aligned or unaligned delay)
│       → reduces output volume; good for dashboards with refresh limits
│
├── When input is believed complete (correctness over latency)
│   └── Watermark trigger (on-time pane only)
│       → highest latency; loses data if watermark heuristic is wrong
│
└── Balance latency, completeness, and late data
    └── Compound early/on-time/late trigger
        ├── Early: per-record or per-delay (speculative results)
        ├── On-time: watermark passage (authoritative result)
        └── Late: per-record or per-delay (corrections for late arrivals)
            → pair with allowed lateness to bound late firings
```

### Which Accumulation Mode?

```
How should multiple panes for the same window relate?
│
├── Each pane is independent; downstream overwrites previous
│   └── Discarding — cheapest; requires downstream overwrite semantics
│       → use when downstream stores only the latest value (key-value store)
│
├── Each pane includes all prior data (cumulative totals)
│   └── Accumulating — moderate cost; downstream must handle cumulative values
│       → use when downstream sums or aggregates across panes (e.g., counters)
│
└── Each pane corrects the previous via retraction
    └── Accumulating and Retracting — most expensive; most correct
        → required when downstream cannot distinguish cumulative from delta
           or when joins and multi-level aggregations need undo signals
```

### Exactly-Once: Which Mechanism?

```
What is your exactly-once requirement?
│
├── Within the pipeline shuffle (internal correctness)
│   └── Shuffle-level deduplication
│       ├── Assign unique record IDs upstream
│       ├── Downstream catalogs seen IDs per key (with Bloom filter optimization)
│       └── GC catalog entries after watermark passes
│
├── At the source (replay/resume after failure)
│   └── Source checkpointing
│       → source API must support offset-based or token-based replay
│
└── At the sink (no duplicate external writes)
    ├── Idempotent sinks — writes are safe to repeat
    │   → files (overwrite), key-value stores (upsert), Pub/Sub (dedup by ID)
    └── Transactional sinks — atomic commit of a batch of records
        → BigQuery load jobs, database transactions
        → wrap in windowed commit; one transaction per window/bundle
```

## Key Concepts Quick Reference

| Concept | Definition |
|---------|-----------|
| **Event time** | The time at which an event actually occurred, embedded in the data |
| **Processing time** | The time at which an event is observed by the pipeline |
| **Skew** | The gap between event time and processing time at any instant |
| **Watermark** | Monotonically increasing timestamp: all events with event time ≤ watermark are believed to have arrived |
| **Trigger** | Declaration of when a window's accumulated results should be emitted |
| **Pane** | A single emission of results for a window; windows can produce multiple panes |
| **Accumulation** | How successive panes for a window relate: discarding, accumulating, accumulating+retracting |
| **Allowed lateness** | Maximum delay past the watermark that late data will still be incorporated |
| **Fixed window** | Non-overlapping time slices of equal duration |
| **Sliding window** | Overlapping windows with fixed size and slide period |
| **Session window** | Data-driven gap-based windows; merges overlapping activity spans |
| **Stream** | Data in motion; a changelog or event log |
| **Table** | Data at rest; a snapshot keyed by some dimension |
| **TVR** | Time-Varying Relation — a relation that evolves over time; unifies streams and tables in SQL |
| **CombineFn** | Associative+commutative incremental combiner enabling partial aggregation |
| **Ingress time** | Processing time stamped at source input; proxy for event time when event time is unavailable |
