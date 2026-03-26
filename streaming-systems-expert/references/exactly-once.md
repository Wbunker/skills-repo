# Streaming Systems — Exactly-Once and Side Effects (Chapter 5)

Author of this chapter: Reuven Lax.

## Why Exactly-Once Matters

Early streaming systems (Storm, early Spark Streaming) provided at-most-once or at-least-once delivery. To get correct aggregate results, teams ran a batch system in parallel (Lambda Architecture) and used the batch results as the authoritative version while the streaming results provided low-latency approximations.

The cost of this approach:
- Two codepaths to maintain for every pipeline
- Batch system needed to periodically overwrite streaming results
- Reconciliation logic required at query time
- Fundamentally, streaming was a second-class citizen

Exactly-once semantics eliminate the need for the batch correctness layer.

---

## Accuracy vs. Completeness

**Accuracy**: for the records that have been processed, the results are correct. No record has been double-counted or lost in processing.

**Completeness**: all records that should be in the answer have been included. No late arrivals are missing.

Exactly-once addresses **accuracy**. Completeness is the domain of watermarks, triggers, and allowed lateness.

A system can be exactly-once (accurate) but still produce incomplete results if the watermark fires before all data has arrived.

---

## Side Effects

Exactly-once semantics in the context of a pipeline shuffle (data movement between stages) is well-defined. But pipelines often produce **side effects** — writes to external systems that may not support idempotent or transactional writes.

Examples of side effects:
- Sending an email notification
- Writing to an external database with auto-increment keys
- Publishing to a downstream API
- Incrementing a counter in a non-idempotent store

If a bundle (unit of work) is retried due to failure, side effects fire multiple times. Exactly-once in the pipeline does not protect external systems from duplicate writes unless those systems support idempotent or transactional operations.

**Principle**: side effects that cannot be made idempotent or transactional should be moved to the **sink** — the final output stage — where they can be controlled via transactional commits.

---

## Exactly-Once in Shuffle (Google Cloud Dataflow Approach)

Shuffle is the movement of data between pipeline stages (e.g., between a map and a reduce). Ensuring exactly-once in shuffle means each record is delivered exactly once to the downstream stage, even in the presence of retries.

### Addressing Determinism

Streaming processing code may be nondeterministic (e.g., generating random IDs, capturing current time). If a bundle is retried, nondeterministic code may produce different output.

Dataflow's solution: **checkpoint the output of nondeterministic code**. On the first execution:
1. Run the user code
2. Store the outputs in durable storage (checkpoint)
3. Use the checkpointed outputs for delivery (not the re-executed outputs)

On retry: skip re-running the nondeterministic code; use the checkpointed output instead. This makes the system **effectively deterministic** from the perspective of downstream stages.

### Record ID Catalog (Deduplication)

Each record in the shuffle is assigned a **unique record ID** before it is sent downstream.

The downstream stage maintains a **catalog of record IDs already processed** per key:
1. When a record arrives, check its ID against the catalog
2. If seen before: discard (it's a retry/duplicate)
3. If not seen: process and add ID to the catalog

**Challenge**: the catalog can grow without bound. Bloom filters are used to make this efficient.

### Bloom Filters

The catalog is backed by a **Bloom filter** — a space-efficient probabilistic data structure that answers "have I seen this ID before?":
- No false negatives: if the filter says "not seen," the ID is definitely new
- Small false positive rate: if the filter says "seen," the ID was probably seen (occasionally wrong)
- False positives → unnecessary duplicate discards (safe but wastes work)
- False negatives → impossible → no missed duplicates

The Bloom filter dramatically reduces the cost of catalog lookups. Only when the filter reports a potential duplicate does the system do a full catalog lookup.

### Garbage Collection

The ID catalog must eventually be cleaned up to prevent unbounded growth.

GC strategy: when the **watermark** advances past the point at which a record could have been produced, its ID is safe to remove from the catalog. No new retries producing that record ID will arrive after the watermark has passed.

This ties exactly-once GC to the watermark mechanism — another reason watermarks are central to the streaming model.

### Graph Optimization: Stage Fusion

Retries are expensive because they require re-reading from durable storage. Dataflow reduces retry surface area by **fusing** multiple pipeline stages that can run together into a single stage.

Fused stages share memory and communicate directly without shuffle. The deduplication catalog is only needed at fusion boundaries (true shuffle points), not within a fused subgraph.

---

## Exactly-Once in Sources

For a pipeline to produce exactly-once results end-to-end, the source must support **replay**:
- After a failure, the pipeline must be able to re-read exactly the data that was in-flight
- This requires offset-based or token-based checkpointing at the source

Example: Kafka sources checkpoint consumer offsets. On restart, the pipeline rewinds to the last committed offset and re-reads from there. Combined with shuffle deduplication, this gives exactly-once end-to-end.

Sources that do not support replay (e.g., a pure push source with no replay) cannot provide exactly-once without an external log (write to Kafka first, then consume from Kafka).

---

## Exactly-Once in Sinks

Sinks are where pipeline results leave the system. Exactly-once requires that sink writes are not duplicated even if the final stage retries.

### Idempotent Sinks
A sink is **idempotent** if writing the same record multiple times produces the same result as writing it once.

Examples:
- **Files**: overwriting the same file with the same content is idempotent
- **Key-value stores**: setting a key to the same value is idempotent (upsert semantics)
- **Google Cloud Pub/Sub**: assign a deduplication ID to each message; Pub/Sub deduplicates within a time window

Idempotent sinks are the simplest solution — no coordination required.

### Transactional Sinks
For non-idempotent sinks, use **transactions**:
1. Batch a window's output into a single transaction
2. Commit the transaction atomically
3. If the stage retries, the transaction is not yet committed; the retry can attempt the same transaction again

**Google BigQuery**: Dataflow uses BigQuery load jobs. Each bundle produces a staging file; the load job is atomic. On retry, the staging file is overwritten and re-loaded.

**Database transactions**: wrap all writes for a bundle in a BEGIN/COMMIT. On retry, use an idempotent transaction ID to detect and skip already-committed transactions.

---

## Apache Flink: Distributed Snapshots

Flink uses a different approach based on the **Chandy-Lamport distributed snapshot algorithm**:

1. A **checkpoint coordinator** periodically injects **barrier records** into all source streams
2. Barriers flow downstream through all pipeline stages with the data
3. When a stage receives a barrier on all input streams, it:
   - Takes a snapshot of its current state (checkpoints to durable storage)
   - Forwards the barrier downstream
4. When all stages have checkpointed, the checkpoint is complete and considered committed

On failure:
- The pipeline rolls back to the last complete checkpoint
- All sources rewind to the offset corresponding to that checkpoint
- Processing resumes from the checkpoint state

**Key property**: since all state is snapshotted atomically across all stages simultaneously (via barriers), rollback to a checkpoint restores a globally consistent state. Combined with source replay, this gives exactly-once end-to-end.

**Tradeoff**: checkpoint frequency determines the recovery cost (more frequent = lower re-processing on failure) and throughput overhead (barriers create coordination overhead).

---

## Apache Spark: Micro-Batch Model

Spark Streaming (1.x) and Structured Streaming use a **micro-batch** model:
- Input stream is divided into small batches (e.g., 100ms–1s intervals)
- Each batch is processed as a standard Spark batch job
- Batch jobs are atomic and idempotent by construction
- Offsets for each batch are committed only after successful completion

This provides effective exactly-once semantics by leveraging the batch engine's ACID properties. The tradeoff is increased latency (bounded below by batch interval) and higher overhead per-record compared to pure streaming.

Structured Streaming improves on Spark Streaming 1.x by providing a higher-level API with more explicit exactly-once semantics.

---

## Exactly-Once Summary

| Mechanism | Approach | Overhead | Used In |
|-----------|----------|----------|---------|
| Shuffle deduplication | Record ID catalogs + Bloom filters | Per-record ID storage and lookup | Dataflow |
| Distributed snapshots | Chandy-Lamport barriers + state checkpoints | Periodic checkpoint I/O | Flink |
| Micro-batch | Treat each batch as atomic Spark job | Batch latency floor | Spark Streaming |
| Idempotent sinks | Natural deduplication by overwrite/upsert | None (by design) | Any sink with idempotent semantics |
| Transactional sinks | Atomic commit per bundle/window | Transaction coordination overhead | Databases, BigQuery |
