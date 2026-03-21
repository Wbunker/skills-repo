# Trident — Exactly-Once Stateful Stream Processing
## Chapters 4–5: Trident Introduction and Trident Topology Patterns

---

## What Is Trident?

Trident is a **high-level micro-batch API** built on top of core Storm that provides:

- **Exactly-once processing semantics** (each tuple processed and reflected in state exactly once, even with retries)
- **Stateful operations** with pluggable state backends
- **SQL-like functional API**: filter, map, groupBy, aggregate, join, merge
- **Automatic batching** — Trident batches tuples and commits state in atomic transactions

Trident trades raw per-tuple latency for correctness guarantees. Batch commit intervals (typically 1–10 seconds) introduce higher latency than core Storm but provide stronger semantics.

---

## Trident vs. Core Storm

| Dimension | Core Storm | Trident |
|-----------|-----------|---------|
| Processing model | Per-tuple | Micro-batch |
| Delivery guarantee | At-least-once | Exactly-once (with transactional spout) |
| State | Manual, error-prone | Built-in TridentState |
| API | Java spout/bolt | Functional (filter/map/groupBy/aggregate) |
| Latency | Sub-second | 1–10s (batch interval) |
| Complexity | Lower | Higher |

---

## Trident Spout Types

### Non-Transactional Spout

No atomicity guarantees. If a batch is replayed, the same tuples may or may not reappear. Used only with idempotent operations.

### Transactional Spout

Each batch has a **transaction ID (txid)**. If a batch with the same txid is replayed, it contains exactly the same tuples. Enables exactly-once with proper state logic.

```
Batch 1: txid=1, tuples=[A, B, C]
Batch 2: txid=2, tuples=[D, E, F]
Replay of Batch 1: txid=1, tuples=[A, B, C]  ← identical
```

State update rule: only apply the update if `txid > lastCommittedTxid`.

### Opaque Transactional Spout

Weaker guarantee: a replayed batch may contain different tuples than the original, but it has the same txid. The state logic must store both the current and previous values to handle this case correctly.

Most Kafka-based spouts (e.g., `OpaqueTridentKafkaSpout`) are opaque transactional.

---

## TridentTopology API

```java
TridentTopology topology = new TridentTopology();

// From a spout
TridentState wordCounts = topology
    .newStream("spout", new FixedBatchSpout(...))
    .each(new Fields("sentence"), new SplitFunction(), new Fields("word"))
    .groupBy(new Fields("word"))
    .persistentAggregate(new MemoryMapState.Factory(),
                         new Count(),
                         new Fields("count"));

// DRPC (distributed RPC) query against the state
topology.newDRPCStream("words", drpc)
    .each(new Fields("args"), new Split(), new Fields("word"))
    .groupBy(new Fields("word"))
    .stateQuery(wordCounts, new Fields("word"), new MapGet(), new Fields("count"))
    .each(new Fields("count"), new FilterNull())
    .aggregate(new Fields("count"), new Sum(), new Fields("sum"));
```

---

## Trident Operations

### Functions

Transform one tuple into zero or more new tuples. Input fields are passed in; output fields are appended.

```java
public class SplitFunction extends BaseFunction {
    public void execute(TridentTuple tuple, TridentCollector collector) {
        String sentence = tuple.getString(0);
        for (String word : sentence.split(" ")) {
            collector.emit(new Values(word));
        }
    }
}

stream.each(new Fields("sentence"), new SplitFunction(), new Fields("word"));
```

### Filters

Keep or discard tuples based on a predicate. No output fields — tuple passes or is dropped.

```java
public class LongWordFilter extends BaseFilter {
    public boolean isKeep(TridentTuple tuple) {
        return tuple.getString(0).length() > 5;
    }
}

stream.each(new Fields("word"), new LongWordFilter());
```

### Projections

Select only specified fields from tuples:

```java
stream.project(new Fields("word", "count"));
```

### Aggregations

**Aggregate** (no groupBy): combines all tuples in a batch into one result.

```java
stream.aggregate(new Fields("value"), new Sum(), new Fields("total"));
```

**GroupBy + persistentAggregate**: group tuples by key, aggregate per group, persist result to state.

```java
stream.groupBy(new Fields("word"))
      .persistentAggregate(stateFactory, new Count(), new Fields("count"));
```

Built-in aggregators:
- `Count()` — count tuples per group
- `Sum()` — sum a numeric field
- `Min()` / `Max()`
- `First()` — first tuple per group

**CombinerAggregator**: split into `init`, `combine`, `zero` for distributed partial aggregation:

```java
public class MySum implements CombinerAggregator<Long> {
    public Long init(TridentTuple tuple) { return tuple.getLong(0); }
    public Long combine(Long val1, Long val2) { return val1 + val2; }
    public Long zero() { return 0L; }
}
```

**ReducerAggregator**: less composable but simpler for complex aggregations.

### Merging and Joining

```java
// Merge two streams (same fields)
topology.merge(stream1, stream2);

// Join two streams (within a batch)
topology.join(stream1, new Fields("id"),
              stream2, new Fields("id"),
              new Fields("id", "val1", "val2"));
```

---

## Trident State

Trident State enables **fault-tolerant stateful processing**. State is updated in a commit/abort pattern tied to batch transaction IDs.

### State Types

| Type | Guarantee | Use Case |
|------|-----------|----------|
| `NonTransactionalMap` | None (best effort) | Simple counting; idempotent ops |
| `TransactionalMap` | Exactly-once (txid stored with value) | Exactly-once counts with transactional spout |
| `OpaqueMap` | Exactly-once (stores previous + current value) | Opaque transactional spout (Kafka) |

### MemoryMapState (in-process, testing only)

```java
TridentState counts = stream
    .groupBy(new Fields("word"))
    .persistentAggregate(new MemoryMapState.Factory(), new Count(), new Fields("count"));
```

### Redis State

```java
// Using storm-redis
RedisState.Options opts = new RedisState.Options();
opts.host = "redis.example.com";
opts.port = 6379;

TridentState counts = stream
    .groupBy(new Fields("word"))
    .persistentAggregate(new RedisMapState.opaque(opts), new Count(), new Fields("count"));
```

### Cassandra / HBase State

Use community connectors (e.g., `storm-hbase` or custom `IBackingMap` implementation). The key pattern: implement `IBackingMap<T>` with `multiGet` and `multiPut` operations.

### Custom State Backend

```java
public class MyStateFactory implements StateFactory {
    public State makeState(Map conf, IMetricsContext metrics,
                           int partitionIndex, int numPartitions) {
        return new MyState(...);
    }
}

public class MyState implements ITridentState {
    public void beginCommit(Long txid) { ... }
    public void commit(Long txid) { ... }
    // implement OpaqueMap or TransactionalMap interface
}
```

---

## DRPC — Distributed Remote Procedure Call

Trident topologies can serve synchronous queries against live state via DRPC:

```
Client → DRPC Server → Trident DRPC Stream → State Query → Response
```

```java
// Server side: define DRPC stream
topology.newDRPCStream("get-count", drpc)
    .stateQuery(wordCounts, new Fields("args"), new MapGet(), new Fields("count"));

// Client side: query the running topology
DRPCClient client = new DRPCClient(conf, "drpc-server", 3772);
String result = client.execute("get-count", "hello");
```

DRPC is useful for serving real-time aggregation results to downstream APIs without a separate query database.

---

## Trident Topology Patterns

### Real-Time Count + Query

```
KafkaSpout → split → groupBy(word) → persistentAggregate(count) → Redis state
                                                                  ↑
                                                          DRPC query interface
```

### Windowed Aggregation

Trident does not have native windowing (unlike Flink/Spark). Implement windowed counts using:
- **Sliding window via TTL-based Redis keys**: expire keys after window duration
- **Time-bucketed fields grouping**: include time bucket in the groupBy key
- **External Esper integration**: embed Esper CEP engine in a bolt (see ecosystem-integration.md)

### Enrichment with External Lookup

```java
stream.each(new Fields("user_id"),
            new ExternalLookupFunction(redisClient),
            new Fields("user_profile"))
      .each(new Fields("user_profile", "event"),
            new EnrichFunction(),
            new Fields("enriched_event"));
```

### Deduplication

Use a state backend with TTL: on each tuple, check if ID exists in state; if yes, filter; if no, write and pass through.

---

## Exactly-Once Guarantee: How It Works

1. Trident assigns each batch a monotonically increasing `txid`
2. Before updating state, check: `if (txid == state.lastCommittedTxid + 1) { apply update; commit(txid); }`
3. For opaque spouts: store both `prevValue` and `currValue`; on replay, check if stored `txid == current txid` — if so, return `currValue` (already applied); else apply from `prevValue`
4. State backends must implement the appropriate interface (`ITridentState`, `OpaqueMap`, `TransactionalMap`) to honor these semantics

The guarantee only holds **end-to-end if**:
- The spout is transactional or opaque transactional
- The state backend correctly implements the txid-check pattern
- External writes are idempotent or gated by txid
