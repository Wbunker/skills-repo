# Streaming Systems — The Beam Model (Chapter 2)

## The Four Questions

Every data processing pipeline can be described by four questions:

| Question | Answers | Mechanism |
|----------|---------|-----------|
| **What** results are computed? | Transformations applied to the data | Transforms (nongrouping / grouping) |
| **Where** in event time are results computed? | Time boundaries for aggregation | Windowing |
| **When** in processing time are results materialized? | When output is emitted | Triggers + Watermarks |
| **How** do refinements of results relate? | Relationship between successive outputs for same window | Accumulation |

---

## What: Transformations

**Nongrouping (element-wise) transforms**
- Applied to each element independently
- Output one or more records per input record
- No state accumulation required
- Examples: filter, map, flatMap, projection

**Grouping transforms**
- Combine multiple elements into a single result
- Require accumulating state across records
- Examples: sum, count, join, histogram
- This is where windowing, triggers, and accumulation apply

---

## Where: Windowing

Windowing divides unbounded data into finite chunks for processing.

### Fixed Windows
- Equal-size, non-overlapping slices aligned to absolute time boundaries
- Example: hourly windows 00:00–01:00, 01:00–02:00, ...
- All keys share the same window boundaries (aligned)

### Sliding Windows
- Overlapping windows defined by (size, period)
- Example: 1-hour window every 5 minutes
- Each element appears in `size/period` windows → higher computational cost
- Used for rolling averages, moving aggregates

### Session Windows
- Dynamic, data-driven windows based on activity gaps
- A session ends when there is no activity for longer than the gap timeout
- Window boundaries vary per key; windows can merge as late data arrives
- Natural fit for user session analysis, IoT device activity

### The Global Window
- A single window covering all time
- Used with triggers to get repeated processing-time snapshots
- Useful for building processing-time windowing behavior

---

## When: Watermarks

A **watermark** is an event-time metric representing progress through unbounded data:

> Watermark W(t): all events with event time ≤ t are believed to have arrived.

When the watermark passes the end of a window, that window is considered complete and the **on-time pane** fires.

**Perfect watermark**: guarantees no late data. Possible only when the source has complete knowledge (e.g., bounded files, known-complete partitions).

**Heuristic watermark**: an estimate based on partial knowledge. May be wrong in either direction:
- Too slow → high latency, correct results
- Too fast → low latency, some late data treated as dropped unless triggers account for it

See [watermarks.md](watermarks.md) for full mechanics.

---

## When: Triggers

Triggers declare **when to emit results** for a window. A window can produce multiple outputs (**panes**).

### Trigger Types

**Per-record triggers (repeated update)**
- Fire after every new element arrives in the window
- Highest output frequency; lowest latency
- Downstream must handle many updates

**Processing-time delay triggers**
- Fire after N seconds/minutes of processing time have elapsed
- Throttle output rate; balance latency and volume
- Can be aligned (to processing-time boundaries) or unaligned (relative to first element)

**Watermark (completeness) triggers**
- Fire exactly once when the watermark passes the window's end
- Highest latency; "correct" single output per window
- Fails silently if watermark heuristic is too optimistic (late data is dropped without late trigger)

**Compound triggers**
- Combine multiple trigger types into one
- Most powerful and common production pattern

### Early / On-Time / Late Pattern

The canonical compound trigger for production pipelines:

```
Trigger:
  repeat {
    [early] any of:
      - per-record trigger (speculative results as data arrives)
      - processing-time delay (throttled speculative results)
    [on-time] watermark trigger (authoritative result)
    [late] any of:
      - per-record trigger (corrections for late arrivals)
      - processing-time delay (throttled corrections)
  }
  until: allowed lateness exceeded
```

**Early panes**: speculative results before the watermark; multiple firings; low latency
**On-time pane**: fires when watermark passes window end; the primary "correct" result
**Late panes**: corrections as late data arrives after the watermark

---

## When: Allowed Lateness

Defines how long after the watermark passes that late data will still be incorporated into a window.

```
Window end: W
Watermark passes W at processing time P
Allowed lateness: L

Late data arriving before processing time P + L → incorporated, triggers late pane
Late data arriving after processing time P + L → dropped (garbage collected)
```

**Purpose**: bounds the lifetime of window state in the system, enabling resource cleanup. Without it, state for old windows would accumulate forever.

**Tradeoff**: larger allowed lateness = more late data captured = more memory used for old window state.

---

## How: Accumulation

Accumulation defines how multiple panes for the same window relate.

### Discarding
- Each pane contains only the data that arrived since the last pane
- Previous state is dropped after emission
- Cheapest storage: only the delta is kept between firings
- Downstream must: overwrite/replace previous results, or be able to apply deltas

```
Pane 1: [a, b] → sum=3
Pane 2: [c]    → sum=2   ← only c counted; downstream replaces 3 with 2... wait, should add!
```
Use only when downstream stores only the latest value (key-value upsert) or can handle deltas directly.

### Accumulating
- Each pane contains all data seen so far for the window (cumulative)
- State accumulates; each pane is a full restatement
- Moderate storage cost
- Downstream must: use the latest pane as the authoritative value (overwrite)
- Safe for downstream sums when the new pane replaces the old

```
Pane 1: [a, b] → sum=3
Pane 2: [a, b, c] → sum=5  ← includes prior data; downstream replaces 3 with 5
```

### Accumulating and Retracting
- Each new pane is accompanied by a retraction of the previous pane's value
- Downstream receives both the old value (to undo) and the new value (to apply)
- Most expensive: state for previous emission must be tracked to produce retraction
- Required when downstream cannot distinguish cumulative from delta, or for multi-level joins/aggregations that need undo semantics

```
Pane 1: [a, b] → emit +3
Pane 2: [a, b, c] → emit -3 (retract pane 1), emit +5 (new value)
```

### Choosing Accumulation Mode

| Mode | Storage | Downstream complexity | When to use |
|------|---------|-----------------------|-------------|
| Discarding | Lowest | Must apply deltas | Downstream overwrites latest; or purely additive deltas |
| Accumulating | Medium | Replace with latest | Downstream stores final value per key; latest = truth |
| Accumulating+Retracting | Highest | Handle retract+assert | Multi-level pipelines, joins, or when downstream cannot distinguish cumulative from delta |

---

## Putting It Together: A Worked Example

Scenario: count website visits per hour, with low-latency early results and corrections for late data.

```
What:  Count (grouping transform)
Where: Fixed 1-hour event-time windows
When:  - Early: every 1 minute of processing time (speculative results)
       - On-time: watermark (authoritative count)
       - Late: per record (corrections), within 1 hour of allowed lateness
How:   Accumulating (each pane is a cumulative total)
```

Output behavior:
- Every minute, emit a running count of visits seen so far in the current hour
- When the watermark declares the hour complete, emit the authoritative count
- If late visits arrive within 1 hour past the watermark, emit corrected counts
- After 1 hour of allowed lateness, discard state for that window
