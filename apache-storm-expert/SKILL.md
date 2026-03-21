---
name: apache-storm-expert
description: Expert on Apache Storm — real-time stream processing architecture, topology development, Trident, parallelism, stream groupings, scheduling, monitoring, and integration with Kafka/Hadoop/HBase/Redis/Elasticsearch. Use when designing Storm topologies, writing spouts/bolts, configuring Trident for exactly-once semantics, tuning parallelism, monitoring clusters, or integrating Storm with external systems. Based on "Mastering Apache Storm" by Ankit Jain (Packt).
---

# Apache Storm Expert

Based on "Mastering Apache Storm" by Ankit Jain (Packt Publishing).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STORM CLUSTER                                 │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                       NIMBUS (master)                        │    │
│  │  - Distributes code to workers                               │    │
│  │  - Assigns tasks to Supervisors                              │    │
│  │  - Monitors for failures; reassigns on failure               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│              ┌───────────────┼───────────────┐                      │
│              ▼               ▼               ▼                      │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │
│  │  SUPERVISOR    │ │  SUPERVISOR    │ │  SUPERVISOR    │          │
│  │  (worker node) │ │  (worker node) │ │  (worker node) │          │
│  │                │ │                │ │                │          │
│  │  Worker  Worker│ │  Worker  Worker│ │  Worker  Worker│          │
│  │  Process Process│ │  Process Process│ │  Process Process│         │
│  │  (JVM)   (JVM) │ │  (JVM)   (JVM) │ │  (JVM)   (JVM) │         │
│  │   │Executors│  │ │   │Executors│  │ │   │Executors│  │         │
│  │   │ Tasks   │  │ │   │ Tasks   │  │ │   │ Tasks   │  │         │
│  └────────────────┘ └────────────────┘ └────────────────┘          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    ZOOKEEPER ENSEMBLE                         │    │
│  │  - Coordinates Nimbus ↔ Supervisor state                     │    │
│  │  - Stores topology metadata and heartbeats                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘

TOPOLOGY DATA FLOW:
  Spout (data source)
     │  emits tuples
     ▼
  Bolt (transform/filter/aggregate)
     │  emits tuples
     ▼
  Bolt (persist/forward)
     │
     ▼
  External sink (HBase, Redis, Elasticsearch, Kafka, HDFS)
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Storm concepts, architecture, Nimbus/Supervisor/ZooKeeper, spouts, bolts, topologies, at-least-once semantics, acking | [foundations.md](references/foundations.md) |
| Deploying Storm, local vs. cluster mode, topology lifecycle, config options, submitting/killing topologies | [deployment-and-topology.md](references/deployment-and-topology.md) |
| Parallelism hints, workers/executors/tasks, stream groupings (shuffle, fields, all, global, direct) | [parallelism-and-groupings.md](references/parallelism-and-groupings.md) |
| Trident API, exactly-once semantics, stateful operations, Trident State, Trident spouts, aggregations, filters | [trident.md](references/trident.md) |
| Storm scheduler, resource allocation, multi-tenant scheduling, custom schedulers | [scheduling.md](references/scheduling.md) |
| Cluster monitoring, JMX metrics, metric reporters, Grafana, alerting, custom metrics | [monitoring.md](references/monitoring.md) |
| Kafka-Storm integration, KafkaSpout, topology deployment with Kafka sources | [kafka-integration.md](references/kafka-integration.md) |
| Hadoop/HDFS, HBase, Redis, Elasticsearch, Esper integration bolts and patterns | [ecosystem-integration.md](references/ecosystem-integration.md) |
| Log processing patterns, Twitter streaming, ML on streams, real-world topology examples | [real-world-patterns.md](references/real-world-patterns.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | Ch. 1 | Storm introduction, real-time processing motivation, Nimbus/Supervisor/ZooKeeper roles, spout/bolt/topology primitives, tuple lifecycle, acking, reliability |
| `deployment-and-topology.md` | Ch. 2 | Local vs. cluster mode, Storm installation, topology development workflow, Config class, submitting/killing/monitoring topologies, multi-lang support |
| `parallelism-and-groupings.md` | Ch. 3 | Workers, executors, tasks, parallelism hints, rebalancing, stream groupings (shuffle, fields, all, global, none, local-or-shuffle, direct), data partitioning |
| `trident.md` | Ch. 4–5 | Trident motivation, transactional spouts, opaque transactional spouts, exactly-once semantics, TridentState, TridentTopology, operations (filter, function, aggregation, groupBy), persistence backends |
| `scheduling.md` | Ch. 6 | Default scheduler, isolation scheduler, resource-aware scheduler (RAS), custom scheduler API, multi-tenant Storm, topology priority |
| `monitoring.md` | Ch. 7 | Storm UI, JMX integration, built-in metrics, metric reporters (console, CSV, JMX), Grafana dashboards, alerting (Slack/email), custom IMetric implementations |
| `kafka-integration.md` | Ch. 8 | KafkaSpout configuration, offset management, Kafka topology patterns, parallel consumers, exactly-once with Kafka + Trident |
| `ecosystem-integration.md` | Ch. 9–10 | HDFS bolt (HDFS integration), HBase bolt (HBase writes), Storm-Hadoop patterns, Redis state/bolt, Elasticsearch bolt, Esper windowing, integration topology patterns |
| `real-world-patterns.md` | Ch. 11–12 | Apache log parsing topology, Twitter Streaming API spout, tweet ingestion → Kafka → Storm, sentiment analysis, real-time ML integration, end-to-end pipeline patterns |

## Core Decision Trees

### Which Stream Grouping Should I Use?

```
What is the distribution requirement for tuples?
├── Each task receives an equal random share of tuples
│   └── Shuffle Grouping
│       └── Good for stateless operations (filtering, transformation)
├── Tuples with the same field value must go to the same task
│   └── Fields Grouping
│       └── grouping(new Fields("user_id"))
│       └── Required for stateful ops: counting, session tracking
├── Every bolt task must receive every tuple
│   └── All Grouping
│       └── Use sparingly; replicates all traffic to all tasks
├── Only one task receives all tuples (global aggregation)
│   └── Global Grouping
│       └── Single point; use for final reduce step only
├── Tasks on same worker process first, else shuffle
│   └── Local or Shuffle Grouping
│       └── Reduces network overhead for co-located tasks
└── Caller designates the exact task
    └── Direct Grouping
        └── Must use emitDirect(); advanced use only
```

### At-Least-Once vs. Exactly-Once — Which Do I Need?

```
What are your delivery semantics requirements?
├── Duplicates are acceptable (idempotent writes, counters with dedup)
│   └── Core Storm (spout + ack)
│       ├── Spout: nextTuple() + ack() + fail()
│       ├── Bolt: OutputCollector.ack(inputTuple)
│       └── message.timeout.secs controls replay window
├── No duplicates — counts/state must be exact
│   └── Trident
│       ├── Use TridentTopology + transactional or opaque spout
│       ├── Trident batches and commits state atomically
│       └── State backend must support idempotent updates
└── Duplicates acceptable, but need micro-batch aggregations
    └── Trident without persistent state
        └── Simpler than full Trident state; still batches
```

### How Many Workers/Executors/Tasks?

```
I need to increase throughput — where is the bottleneck?
├── Spout is slow (not keeping up with source)
│   └── Increase spout parallelism hint
│       └── builder.setSpout("spout", new MySpout(), <N>)
├── Bolt is the bottleneck (high execute latency)
│   └── Increase bolt executor count
│       └── builder.setBolt("bolt", new MyBolt(), <N>)
├── Worker processes hitting JVM/GC limits
│   └── Add more workers (topology.workers config)
│       └── Each worker = one JVM process on a Supervisor
└── Tasks > executors? (rebalance possible)
    └── Set tasks >= executors to allow future rebalance
        └── rebalance <topology> -n <workers> -e <bolt>=<executors>
```

### Should I Use Core Storm or Trident?

```
Evaluate your use case:
├── Simple stateless transform / filter / route
│   └── Core Storm bolts — simpler, lower latency
├── Need windowed aggregations (counts, sums over time)
│   └── Trident with groupBy + persistentAggregate
├── Need exactly-once state updates
│   └── Trident + opaque transactional spout
├── Joining two streams
│   └── Trident join operations or CoordBolt pattern in core
└── Complex ML scoring on every tuple
    └── Core Storm bolt (load model once, score per tuple)
        └── Or Trident function wrapping model inference
```

## Key Concepts Quick Reference

### Core Terminology

| Term | Definition |
|------|-----------|
| **Topology** | A directed acyclic graph (DAG) of spouts and bolts; the unit of deployment in Storm |
| **Spout** | Source of the data stream; reads from external systems and emits tuples |
| **Bolt** | Processing unit; consumes tuples, applies logic, optionally emits new tuples |
| **Tuple** | The basic message unit; an ordered list of named values |
| **Stream** | An unbounded sequence of tuples |
| **Nimbus** | Master daemon; distributes topology code, assigns tasks, monitors failures |
| **Supervisor** | Worker-node daemon; spawns/kills worker processes as directed by Nimbus |
| **Worker** | A JVM process on a Supervisor that runs one or more executors |
| **Executor** | A thread within a worker; runs one or more tasks |
| **Task** | The actual instance of a spout or bolt (smallest unit of parallelism) |
| **ZooKeeper** | Coordinates Nimbus ↔ Supervisor; stores topology state and heartbeats |
| **Acker** | Special bolt that tracks the tuple tree; triggers ack or fail on spout |
| **Stream grouping** | Defines how tuples are routed from one bolt to the next |
| **Trident** | High-level micro-batch API over Storm for stateful, exactly-once processing |

### Tuple Acking — How Storm Achieves Reliability

```
Spout emits tuple (msgId assigned)
    │
    ├── Bolt 1 receives tuple → anchors new tuple → acks input
    │       │
    │       └── Bolt 2 receives tuple → acks input
    │               │
    │               └── All tuples in tree acked → Spout.ack(msgId) called
    │
    └── Any bolt fails() or timeout → Spout.fail(msgId) called
            └── Spout replays the original tuple
```

XOR-based acking: each tuple tree tracked with 64-bit XOR checksum. Zero = fully acked. Constant memory overhead regardless of tree size.

### Parallelism Hierarchy

```
Topology
  └── Workers (JVM processes, one per Supervisor slot)
        └── Executors (threads within a worker)
              └── Tasks (spout/bolt instances; default 1 per executor)
```

- `topology.workers` — number of worker processes cluster-wide
- Parallelism hint on `setSpout`/`setBolt` — number of executor threads
- `setNumTasks()` — total tasks (can be > executors for rebalance headroom)
