# Streaming Systems — The Practicalities of Persistent State (Chapter 7)

## Why Persistent State?

Long-running streaming pipelines face a fundamental constraint: **failures are inevitable**. Machines fail, networks partition, processes crash. Any pipeline that runs for days or months will experience failures.

Without persistent state:
- On failure, the pipeline must reprocess all historical data from the source to reconstruct its current state
- This is expensive (reprocessing hours or days of data) and slow (recovery time scales with data volume)
- For some sources (no replay, short retention), it is impossible

With persistent state:
- On failure, restore the last checkpointed state and reprocess only the data since the last checkpoint
- Recovery time is bounded by checkpoint frequency and recent data volume

Persistent state serves two purposes:
1. **Correctness**: ensure the pipeline produces the right answer even after failures
2. **Efficiency**: avoid redundant computation by storing partial results

---

## Implicit State

Implicit state is state managed automatically by the pipeline framework on behalf of the user — the user specifies the aggregation logic, and the framework handles storage and recovery.

### Raw Grouping

Buffer all input elements for a key and window until the window is triggered, then apply the aggregation function to the complete list.

```
State: List<Element> per (key, window)
On new element: append to list
On trigger: apply aggregation function to full list; emit result
```

**Advantages**:
- Maximum flexibility: any aggregation function works, including non-associative ones
- Simple to implement
- Supports retractions trivially (just re-aggregate the updated list)

**Disadvantages**:
- State size grows with the number of elements per (key, window)
- For large windows or high-cardinality keys, state can be very large
- High checkpoint I/O cost (must checkpoint the full list)

Raw grouping is the default when no optimization is possible.

### Incremental Combining

For aggregations that are **associative and commutative** (sums, counts, max, min, histograms, HyperLogLog), the framework can apply the function **incrementally** as each element arrives.

```
State: PartialAggregate per (key, window)
On new element: state = combine(state, new_element)
On trigger: emit finalize(state)
```

The `CombineFn` interface (in Apache Beam) formalizes this:
- `createAccumulator()`: create an empty partial aggregate
- `addInput(accumulator, input)`: fold one input element into the accumulator
- `mergeAccumulators(accumulators)`: combine multiple partial accumulators (enables parallel partitioning)
- `extractOutput(accumulator)`: produce the final result from the accumulator

**Advantages**:
- State size is bounded: always a single partial aggregate per (key, window), regardless of element count
- Much lower checkpoint I/O: only the partial aggregate is checkpointed, not the full input list
- Enables partial aggregation before shuffle (like MapReduce combiner)

**Disadvantages**:
- Only works for associative and commutative functions
- Retractions require maintaining more state (the accumulator must support undo)
- Cannot recover individual input elements after they are combined

**Examples of combinable aggregations**: sum, count, min, max, average (as sum+count), set union, HyperLogLog, count-min sketch, Bloom filter.

**Examples of non-combinable aggregations**: median (requires all values), top-N distinct values (requires full list), any order-dependent operation.

---

## Generalized State

When implicit state (raw grouping or incremental combining) is not sufficient, the framework can expose **explicit state and timer APIs** that give the user full control over what state is stored and when logic fires.

Apache Beam's state and timers API:

### State Types
- `ValueState<T>`: a single mutable value per key
- `BagState<T>`: an unordered collection of elements per key (like raw grouping)
- `MapState<K, V>`: a key-value map per processing key
- `SetState<T>`: a set of values per key
- `CombiningState<T, A, R>`: a state that applies a CombineFn incrementally (like incremental combining, but explicit)

### Timers
- **Event-time timers**: fire when the watermark advances past a specified event time
  - Use for: triggering logic at a specific point in event time (e.g., "close this session if the watermark passes the gap boundary")
- **Processing-time timers**: fire when processing time advances past a specified processing time
  - Use for: rate-limiting, periodic cleanup, processing-time-bounded timeouts

Timers enable **time-driven state transitions** — logic that fires not when a record arrives, but when time advances.

---

## Case Study: Conversion Attribution

### The Problem

In digital advertising, **conversion attribution** means: when a user converts (completes a purchase, signs up, etc.), which advertising impression or visit should receive credit?

A simplified model:
1. User sees an impression (ad view) → logged as an **impression event**
2. User visits the website (organic or from the ad) → logged as a **visit event**
3. User converts → logged as a **goal event**
4. Attribution: find the most recent impression/visit before the goal and credit it

This requires:
- Joining three streams (impressions, visits, goals) on user ID
- The join is asymmetric: goal events reference the *most recent prior* impression/visit, not a concurrent one
- The relevant impression/visit may arrive before OR after the goal (due to event-time skew)
- State must be maintained per user across potentially many events

### Why Implicit State Is Insufficient

- **Raw grouping**: would buffer all impressions and visits for all users indefinitely — unbounded state
- **Incremental combining**: CombineFn cannot express "find the most recent prior event and attribute it" — the logic is not associative/commutative
- **Standard windowing**: a fixed window covers a bounded time range, but the impression and goal may be in different windows; session windows could work but don't naturally span the impression-to-goal gap in a single key

### Conversion Attribution with Apache Beam (Generalized State)

Implementation using Beam's state and timers API:

**State per user key**:
- `ValueState<Impression>` or `BagState<Impression>`: most recent impression(s) for this user
- `ValueState<Visit>` or `BagState<Visit>`: most recent visit(s) for this user
- `ValueState<Boolean>`: whether a goal has been seen

**Logic**:
1. On impression event: update the impression state (keep most recent or buffer recent N)
2. On visit event: update the visit state
3. On goal event:
   - If impression/visit state is populated: attribute now; emit attribution record; clear state
   - If not yet populated (impression arrives after goal): set a flag in state; wait
4. On impression/visit event when goal flag is set: attribute retroactively; emit; clear state

**Watermark timer** (for cleanup):
- When the watermark advances past `event_time + allowed_lateness` for a user session:
  - If a goal was seen but no attribution made: emit an "unattributed" record
  - Clear all state for this user to prevent unbounded growth

**Why this works**:
- State is bounded: each user key holds only recent impressions, visits, and a goal flag — not the full event history
- Watermark timers handle garbage collection without waiting for arbitrary processing-time delays
- The logic correctly handles out-of-order arrival (goal before impression or impression before goal)

### Four-Step Algorithm

1. **Buffer impressions and visits**: as they arrive, store in per-user state
2. **Wait for goal**: on goal arrival, check state for prior impressions/visits
3. **Attribute if possible**: if prior data exists, emit attribution; if not, wait
4. **Garbage collect**: watermark timer fires; emit unattributed if needed; clear state

---

## Choosing Between State Approaches

| Approach | State size | Flexibility | When to use |
|----------|-----------|-------------|-------------|
| Raw grouping | Proportional to element count | Maximum | Non-combinable aggregations; need all inputs for final computation |
| Incremental combining | Constant (single accumulator) | Only associative+commutative | Sums, counts, min, max, sketches |
| Generalized state | User-defined | Maximum | Complex join semantics, multi-stream correlation, custom time-driven logic |
