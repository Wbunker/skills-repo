# Concurrency Control in Hudi
## Chapter 9: OCC, NBCC, MVCC, Multiwriter, Three-Step Commit, Locking

---

## Why Concurrency Is Harder in Data Lakehouses

Traditional databases use in-memory locking managers. Object storage (S3, ADLS) has no built-in locking:

```
S3 has no:
  ✗ Row-level locks
  ✗ Table-level locks
  ✗ Atomic multi-file updates
  ✗ Read-your-own-writes consistency (in all regions)

Hudi must build concurrency control on top of object storage
using the Timeline as a distributed coordination mechanism.
```

**Concurrency scenarios in Hudi:**

1. **Multiple writers** writing to the same table simultaneously
2. **Writer + table service** (compaction/clustering) running concurrently
3. **Reader + writer** (always safe — readers see snapshots)

---

## The Three-Step Commit Protocol

Every Hudi write (regardless of concurrency mode) uses a three-step commit to ensure atomicity:

```
Step 1: REQUESTED
  Create <timestamp>.commit.requested on the timeline
  → Announces intent to write
  → Timeline is visible to other writers

Step 2: INFLIGHT
  Create <timestamp>.commit.inflight on the timeline
  Write data files to storage
  → If this step fails, .inflight remains → rollback on next write

Step 3: COMPLETED
  Write commit metadata (stats, file paths, new schema)
  Create <timestamp>.commit on the timeline
  → Atomically replaces .inflight
  → Commit is visible to readers
```

**Failure recovery**: On the next write attempt, Hudi detects any `.inflight` instants older than a threshold and rolls them back before proceeding.

---

## Concurrency Modes

### Single Writer (Default)

One writer writes at a time. Table services (compaction, clustering) must not run concurrently.

```python
"hoodie.write.concurrency.mode": "SINGLE_WRITER"
```

```
Writer Job A:   [write] [write] [write] ...
Compactor:      (must not run while Writer A is active)
```

**Safe pattern**: run compaction inline (after each commit) or in a separate time window.

---

### Optimistic Concurrency Control (OCC)

Multiple writers write concurrently. Conflicts are detected at **commit time**. If two writers modified the same file, the second commit fails and must retry.

```python
"hoodie.write.concurrency.mode": "OPTIMISTIC_CONCURRENCY_CONTROL",
"hoodie.write.lock.provider": "org.apache.hudi.client.transaction.lock.ZookeeperBasedLockProvider",
"hoodie.write.lock.zookeeper.url": "zk1:2181,zk2:2181,zk3:2181",
"hoodie.write.lock.zookeeper.lock_key": "/hudi/locks/orders",
```

**Conflict detection:**
```
Writer A commits files: [file001, file003]
Writer B tries to commit files: [file003, file005]  ← conflict on file003!
→ Writer B's commit rejected
→ Writer B must retry (re-read affected data, re-apply changes)
```

**Conflict resolution**: "last writer wins" — no automatic merge of conflicting writes. Application must handle retry logic.

**Locking providers:**
| Provider | Config Value | Notes |
|----------|-------------|-------|
| ZooKeeper | `ZookeeperBasedLockProvider` | External ZK cluster required |
| AWS DynamoDB | `DynamoDBBasedLockProvider` | Managed; good for AWS |
| Hudi Fileystem | `FileSystemBasedLockProvider` | Uses S3/HDFS for lock files; simple |
| In-process | `InProcessLockProvider` | Single JVM only; not for distributed |

**DynamoDB Lock Provider:**
```python
"hoodie.write.lock.provider": "org.apache.hudi.aws.transaction.lock.DynamoDBBasedLockProvider",
"hoodie.write.lock.dynamodb.table": "hudi-lock-table",
"hoodie.write.lock.dynamodb.region": "us-east-1",
"hoodie.write.lock.dynamodb.endpoint_url": "https://dynamodb.us-east-1.amazonaws.com",
```

**When to use OCC:**
- Low write contention (writers operate on different partitions most of the time)
- Occasional concurrent writes acceptable with retry
- Cannot tolerate single-writer bottleneck

---

### Non-Blocking Concurrency Control (NBCC)

Finer-grained conflict detection than OCC. Writers check for conflicts at the **file group level** rather than the transaction level, allowing more writes to proceed without conflict.

```python
"hoodie.write.concurrency.mode": "NON_BLOCKING_CONCURRENCY_CONTROL",
"hoodie.write.lock.provider": "org.apache.hudi.client.transaction.lock.ZookeeperBasedLockProvider",
```

**How NBCC differs from OCC:**
```
OCC: Writer A locks, writes, releases → Writer B detects file-level conflict → fail

NBCC: Writer A and B both proceed independently
      At commit:
        Writer A writes its file groups
        Writer B writes its file groups
        If A and B wrote DIFFERENT file groups → both succeed (no conflict)
        If A and B wrote the SAME file group → second writer detects conflict
          → Second writer performs record-level merge rather than failing
```

NBCC uses **partial commit** — only the non-conflicting portions of a write commit; conflicting records are re-tried at record level.

**When to use NBCC:**
- Multiple writers writing to the same table but different partitions
- High-throughput pipelines where OCC retry overhead is unacceptable
- Complex CDC pipelines with many parallel partition writers

---

### MVCC (Multi-Version Concurrency Control)

Used internally by Hudi when **a writer and a table service run concurrently**. Not configured directly; enabled automatically when async table services are active.

```
Writer:        [write deltacommit-001] [write deltacommit-002] ...
Compactor:          [read file slices] → [compact] → [commit]
                    ↑ reads a snapshot of the table at compaction start
                    ↑ does not interfere with writer's ongoing writes
```

**How it works:**
- Compactor takes a **snapshot** of the file slices at compaction-plan time
- Writer continues writing new log files to the same file groups
- Compactor produces a new base file from the snapshot
- After compaction commits: new base file + log files written after the snapshot are the current file slice

Writer and compactor both succeed without conflicts because:
- Writer writes new log files
- Compactor produces a base file from an older snapshot
- These do not conflict — they operate on different parts of the file slice

**Enable async table services (uses MVCC internally):**
```python
"hoodie.write.concurrency.mode": "OPTIMISTIC_CONCURRENCY_CONTROL",
# + async compaction enabled
"hoodie.compact.inline": "false",
"hoodie.compact.schedule.inline": "true",
# Run separate compaction job concurrently
```

---

## Multiwriter Scenarios

### Scenario 1: Single Writer + Table Services (Simple Default)

```
Topology: One Spark writer job, compaction/clustering in separate time windows
Mode: SINGLE_WRITER
Services: Inline or standalone (non-concurrent)
Risk: None — sequential operations
```

### Scenario 2: Multiple Independent Partition Writers + OCC

```
Topology: Writer-A handles partition=US, Writer-B handles partition=EU
Mode: OPTIMISTIC_CONCURRENCY_CONTROL + ZooKeeper/DynamoDB lock
Risk: Low — writers operate on different partitions (conflicts rare)
Retry: Application-level retry on commit failure
```

### Scenario 3: Writer + Async Compaction (MVCC)

```
Topology: Streaming writer (continuous) + separate compaction job
Mode: OPTIMISTIC_CONCURRENCY_CONTROL
Services: Async compaction (schedule inline, execute separately)
Conflict: Writer writes new log files; compactor reads old file slices → no conflict
```

### Scenario 4: Multiple CDC Pipeline Writers + NBCC

```
Topology: Many Hudi Streamer instances writing to same table from different Kafka partitions
Mode: NON_BLOCKING_CONCURRENCY_CONTROL
Services: Async table services
Risk: Occasional record-level conflicts when same record key appears in multiple writers
Resolution: NBCC handles per-record merge
```

---

## Conflict Detection Internals

### How Hudi Detects Conflicts

At commit time, Hudi compares the current writer's written file groups against all commits that completed **after** the writer started:

```
Writer A started at t=100, commits at t=200
Commits that happened between t=100 and t=200:
  Writer B committed file groups [f001, f003] at t=150

Writer A wrote file groups [f002, f003]
→ f003 overlap detected → CONFLICT → Writer A's commit rejected (OCC)
```

### The Lock Lifecycle

```
Writer acquires lock (ZK/DynamoDB)
        ↓
Check for pending inflight instants (rollback stale ones)
        ↓
Write data files (no lock held during I/O)
        ↓
Re-acquire lock for commit
        ↓
Read timeline: check for conflicts with commits since writer started
        ↓
If no conflict: write commit file → release lock
If conflict: release lock, fail commit, application retries
```

Lock is held only during the short commit phase, not during the (potentially long) write I/O phase. This minimizes lock contention.

---

## Best Practices for Multiwriter

| Practice | Why |
|----------|-----|
| Use partition-aligned writers | Writers on different partitions almost never conflict |
| Keep writer granularity coarse | One writer per logical topic/source; avoid many tiny writers |
| Use DynamoDB lock for AWS | Managed, HA, no ZK cluster to maintain |
| Enable async table services | Don't block writers with inline compaction in multiwriter setups |
| Set `hoodie.write.lock.wait.time.ms` appropriately | Too short = excessive retries; too long = latency |
| Monitor conflict/retry rate | High conflict rate signals writer topology redesign |
| Avoid writes to same partition from multiple writers | Unless NBCC; OCC will produce frequent conflicts |
