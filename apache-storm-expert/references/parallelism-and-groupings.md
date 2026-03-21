# Storm Parallelism and Data Partitioning
## Chapter 3: Workers, Executors, Tasks, and Stream Groupings

---

## The Parallelism Hierarchy

```
Topology
  └── Workers      (JVM processes, spread across Supervisor nodes)
        └── Executors  (threads within a worker)
              └── Tasks    (spout/bolt instances; run within an executor)
```

### Workers

- A **worker process** is a JVM spawned by a Supervisor
- Each worker belongs to exactly one topology
- Workers from different topologies can coexist on the same Supervisor node
- Configured via `topology.workers` in Config (total workers for the topology across the cluster)
- Number of Supervisor slots limits how many workers can run on that node

### Executors

- An **executor** is a thread within a worker process
- Runs one or more tasks of a single component (a given spout or bolt type)
- Set via the parallelism hint argument to `setSpout()` / `setBolt()`
- Number of executors = number of parallel threads for that component

### Tasks

- A **task** is a running instance of a spout or bolt
- Default: `numTasks == numExecutors` (one task per executor)
- Set higher tasks than executors to pre-allocate capacity for rebalancing without restart
- Configured via `.setNumTasks(n)` on the component builder

```java
// 2 executor threads, 4 task instances
// 2 tasks share each executor thread
builder.setBolt("my-bolt", new MyBolt(), 2).setNumTasks(4)
       .shuffleGrouping("my-spout");
```

### Calculating Total Parallelism

| Component | Executors | Tasks |
|-----------|-----------|-------|
| sentence-spout | 1 | 1 |
| split-bolt | 2 | 2 |
| count-bolt | 4 | 4 |
| **Total** | **7 executor threads** | **7 tasks** |

These 7 executors are distributed across `topology.workers` JVM processes.

---

## Stream Groupings

Stream groupings define **how tuples are routed** from the output of one component to the input tasks of the next component.

### Shuffle Grouping

Tuples distributed uniformly and randomly across all target tasks. Each task gets an equal share.

```java
builder.setBolt("parse-bolt", new ParseBolt(), 4)
       .shuffleGrouping("source-spout");
```

**Use when**: The operation is stateless (filtering, transformation, parsing). No affinity required.

### Fields Grouping

Tuples with the **same value for the specified field(s)** always go to the same task. Consistent hashing by field value.

```java
builder.setBolt("count-bolt", new CountBolt(), 4)
       .fieldsGrouping("split-bolt", new Fields("word"));
```

**Use when**: The operation is stateful — you need all tuples for a given key to arrive at the same task (counting, joining, session tracking).

**Warning**: If field cardinality is low (e.g., boolean field), some tasks receive far more tuples than others → data skew.

### All Grouping

Every tuple is sent to **all tasks** of the receiving component. Replicates the stream.

```java
builder.setBolt("broadcast-bolt", new AlertBolt(), 3)
       .allGrouping("signal-spout");
```

**Use when**: Broadcasting a signal or configuration update to all instances. Use sparingly — multiplies traffic.

### Global Grouping

All tuples are routed to the **task with the lowest task ID** (effectively a single task). Provides a global reduce point.

```java
builder.setBolt("final-count-bolt", new FinalCountBolt(), 1)
       .globalGrouping("partial-count-bolt");
```

**Use when**: Final aggregation step where results from all upstream tasks must be combined into one. Creates a bottleneck — keep this bolt fast.

### Local or Shuffle Grouping

If the target component has tasks in the same worker process as the emitter, tuples are sent locally. Otherwise, behaves like shuffle grouping.

```java
builder.setBolt("enrich-bolt", new EnrichBolt(), 4)
       .localOrShuffleGrouping("parse-bolt");
```

**Use when**: Reducing inter-process network traffic. Useful for co-located fast operations.

### None Grouping

Currently equivalent to shuffle grouping. Reserved for future use where Storm may optimize routing.

```java
builder.setBolt("my-bolt", new MyBolt(), 4)
       .noneGrouping("my-spout");
```

### Direct Grouping

The **emitting component explicitly designates** which task receives each tuple using `emitDirect()`.

```java
// In emitting bolt:
collector.emitDirect(targetTaskId, streamId, new Values(data));
```

```java
// Subscribing bolt:
builder.setBolt("direct-consumer", new ConsumerBolt(), 4)
       .directGrouping("routing-bolt");
```

**Use when**: You have custom routing logic that cannot be expressed as field hashing. Advanced use case.

### Custom Grouping

Implement `CustomStreamGrouping` to define arbitrary routing logic:

```java
public class MyGrouping implements CustomStreamGrouping {
    public void prepare(WorkerTopologyContext context, GlobalStreamId stream,
                        List<Integer> targetTasks) { ... }

    public List<Integer> chooseTasks(int taskId, List<Object> values) {
        // return list of target task IDs for this tuple
    }
}

builder.setBolt("custom-bolt", new MyBolt(), 4)
       .customGrouping("source-bolt", new MyGrouping());
```

---

## Grouping Summary Table

| Grouping | Distribution | Stateful? | Notes |
|----------|-------------|-----------|-------|
| Shuffle | Random uniform | No | Best for stateless ops |
| Fields | By field hash | Yes | Required for per-key state |
| All | Every task | — | Broadcast; use sparingly |
| Global | Single task (min ID) | Yes | Final reduce; bottleneck risk |
| Local or Shuffle | Local-first, else random | No | Reduces network I/O |
| None | Random (like shuffle) | No | Reserved |
| Direct | Caller-chosen task | Yes | Advanced custom routing |
| Custom | Arbitrary logic | Either | Implement CustomStreamGrouping |

---

## Data Skew and How to Handle It

**Problem**: Fields grouping on a low-cardinality or skewed field causes some tasks to receive far more tuples than others.

**Detection**: Storm UI bolt capacity > 0.9 on some tasks, much lower on others.

**Solutions**:

1. **Partial aggregation + merge**: Each task partially aggregates, then a small global grouping task merges results.

```
split-bolt (shuffle) → partial-count-bolt (fields by word, 4 tasks)
                     → merge-count-bolt (global, 1 task)
```

2. **Two-level fields grouping with salt**: Add a random salt suffix to the key for first-level grouping, strip it for second level.

3. **Increase executor count** for the skewed bolt to absorb more load per task.

---

## Practical Tuning Guidance

### Identifying the Bottleneck

Storm UI → Topology → Bolt stats:

- **Capacity** ≈ 1.0: This bolt is the bottleneck (fully saturated)
- **Execute latency** high: Bolt processing is slow per tuple
- **Failed tuples**: Tuples timing out or explicitly failed

### Increasing Throughput

```
Bottleneck: spout → increase spout parallelism hint
Bottleneck: bolt  → increase bolt parallelism hint (rebalance)
Bottleneck: worker GC → add more workers (topology.workers)
Spout emitting too fast → set topology.max.spout.pending to backpressure
```

### Rebalancing Without Restart

```bash
storm rebalance <topology-name> -n <num-workers> -e <component>=<num-executors>

# Example: increase count-bolt from 4 to 8 executors, increase workers from 2 to 4
storm rebalance word-count -n 4 -e count-bolt=8
```

Rebalance is a live operation — brief processing pause, then resumes.

### Rules of Thumb

- Start with 1 worker per physical node; increase if GC or memory is not the bottleneck
- Parallelism hint: start at number of CPU cores available per bolt type
- Set `topology.max.spout.pending` to control memory consumption under high-latency bolt conditions
- Keep executor counts as powers of 2 for clean hash distribution with fields grouping
