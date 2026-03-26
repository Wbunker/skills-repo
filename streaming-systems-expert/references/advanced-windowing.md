# Streaming Systems — Advanced Windowing (Chapter 4)

## Processing-Time Windows

Processing-time windowing assigns events to windows based on **when they arrive at the pipeline** (wall-clock time), not when they occurred (event time). This is simpler but semantically less correct for event-time analysis.

Two ways to implement processing-time windows in a system that is natively event-time-aware:

---

### Processing-Time Windowing via Triggers

Use a **global event-time window** (a single window covering all time) and fire it on a processing-time trigger.

```
Window:   Global (all event times)
Trigger:  Repeat every N seconds of processing time
Accum:    Discarding (each trigger gives independent snapshot)
```

Behavior:
- All data accumulates in one global bucket
- Every N seconds, the trigger fires, emitting a snapshot of current state
- The discarding accumulation mode ensures each snapshot is independent
- Produces processing-time windows implicitly — each snapshot covers what arrived since the last snapshot

**Advantage**: flexible; works even if event times are missing or meaningless.

**Disadvantage**: the output timestamp of the global window is indeterminate — you lose event-time attribution entirely. Window boundaries are defined by processing-time trigger firings, not by data content.

---

### Processing-Time Windowing via Ingress Time

Stamp each incoming event with its **arrival time at the source** as its event time, overriding any embedded event timestamp.

```
Source: stamp event.event_time = now()  (processing time at ingress)
Then:   use standard event-time fixed windows
```

**Advantage**: simplifies downstream processing — standard event-time windowing just works because event times equal ingress times.

**Disadvantage**:
- Destroys actual event-time information — cannot reconstruct when events actually occurred
- Ordering within windows is by ingress order, not occurrence order
- Any event-time skew is hidden; windows appear "correct" but are semantically wrong for event-time analysis

**When to use**: when actual event times are unavailable (events have no embedded timestamp) and you only need processing-time semantics.

---

## Session Windows

Sessions are **data-driven**, **gap-based** windows that group related activity together.

### Definition
A session window for a key is the contiguous span of activity separated by periods of inactivity. Formally:
- If two events for the same key are within the **gap timeout** of each other (in event time), they belong to the same session
- If the gap between consecutive events exceeds the timeout, a new session begins

### Properties
- Session windows are **per-key** — different keys have completely independent sessions
- Window boundaries are not fixed — they emerge from the data
- Windows can **merge** as late data arrives and fills gaps that previously separated two sessions

### Merging Behavior
When a new record arrives that fills the gap between two previously separate session windows:
1. Both existing windows merge into one larger window
2. The merged window's state is the combination of both
3. The trigger and accumulation mode for the merged window continues from this point

This merging behavior is unique to session windows and requires the system to track potentially many open session windows per key simultaneously.

### Practical Considerations
- **Gap timeout**: the single most important parameter; too small → sessions fragmented; too large → distinct activities merged
- **State size**: each active session holds accumulated state; many active sessions = significant memory
- **Late data**: can cause session merges long after sessions appeared closed — plan allowed lateness accordingly

---

## Custom Windowing

Custom windowing allows defining arbitrary window assignment and merging logic beyond fixed, sliding, and session window types.

### Variations on Fixed Windows

**Unaligned fixed windows**
- Fixed window size but window boundaries are **offset per key** rather than shared across all keys
- Example: 1-hour windows, but key A's windows are 00:00–01:00 while key B's are 00:13–01:13 (offset by hash of key)

Why: Aligned fixed windows create resource spikes when all windows for all keys fire simultaneously at each hour boundary. Unaligned windows spread the load across time.

**Tradeoff**: unaligned windows make cross-key aggregation harder (different keys' windows don't align) but improve resource utilization significantly in high-cardinality scenarios.

**Per-element/key fixed windows**
- Each key has a configurable window size stored as metadata
- Example: customer-specific reporting windows (customer A wants 15-minute windows, customer B wants 1-hour windows)

Implementation: embed the window size in the key or look it up from a side input at windowing time.

**Tradeoff**: significant implementation complexity; no longer possible to share window state across keys even for the same time range.

---

### Variations on Session Windows

**Bounded sessions by duration**
- Sessions are capped at a maximum time duration regardless of activity
- If activity is continuous for longer than the cap, the session splits at the cap boundary
- Use case: prevent very long sessions from accumulating unbounded state (e.g., a continuously active robot or bot)

**Bounded sessions by element count**
- Sessions are capped at a maximum number of elements
- When the count limit is reached, the session closes and a new one begins
- Use case: batch processing with bounded resource usage; micro-batch behavior with session semantics

**Bounded sessions by other dimensions**
- Custom merging logic: close a session if total value exceeds a threshold, if a specific event type occurs, etc.
- Fully general: any predicate on accumulated session state can be used to split or close a session

---

## Windowing Summary

| Window Type | Boundary | State per Key | Merging | Best For |
|-------------|----------|---------------|---------|----------|
| Fixed (aligned) | Fixed time slices | One window per slice | No | Regular time-based aggregation |
| Fixed (unaligned) | Key-offset time slices | One window per slice | No | High-cardinality; smooth resource usage |
| Sliding | Overlapping fixed slices | Multiple overlapping windows | No | Rolling averages |
| Session | Gap-based, data-driven | One per active session | Yes (on late data) | User activity, IoT bursts |
| Processing-time (trigger) | Processing-time snapshots | Global window + trigger | No | Legacy compatibility; no event-time needs |
| Processing-time (ingress) | Fixed on ingress-stamped time | Same as fixed | No | No embedded event times available |
| Custom | Arbitrary | Arbitrary | Optional | Special business logic |
