---
name: kafka-expert
description: Expert on Apache Kafka — architecture, producers, consumers, internals, reliable delivery, Kafka Connect, stream processing, operations, monitoring, and security. Use when designing Kafka architectures, configuring producers/consumers, debugging delivery issues, setting up Kafka Connect pipelines, building with Kafka Streams, operating and monitoring clusters, or securing Kafka. Based on "Kafka: The Definitive Guide" 2nd edition by Gwen Shapira, Todd Palino, Rajini Sivaram, and Krit Petty (O'Reilly, 2021).
---

# Apache Kafka Expert

Based on "Kafka: The Definitive Guide" 2nd Edition by Gwen Shapira, Todd Palino, Rajini Sivaram, and Krit Petty (O'Reilly, 2021).

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                       KAFKA CLUSTER                                   │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │  BROKER 1          BROKER 2          BROKER 3               │    │
│   │  ─────────         ─────────         ─────────              │    │
│   │  Topic A P0 L      Topic A P0 F      Topic A P1 F           │    │
│   │  Topic A P1 F      Topic A P1 L      Topic A P0 F           │    │
│   │  Topic B P0 L      Topic B P0 F      Topic B P1 L           │    │
│   │         (L=Leader  F=Follower)                               │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│   ┌─────────────────┐              ┌───────────────────────┐         │
│   │  KRaft / ZK     │              │   SCHEMA REGISTRY     │         │
│   │  (controller)   │              │   (Avro/Protobuf/JSON)│         │
│   └─────────────────┘              └───────────────────────┘         │
└──────────────┬────────────────────────────────┬──────────────────────┘
               │                                │
   ┌───────────▼──────────┐       ┌─────────────▼──────────┐
   │     PRODUCERS        │       │      CONSUMERS          │
   │  acks=all · retries  │       │  group.id · offsets     │
   │  idempotent · batch  │       │  rebalance · lag        │
   └──────────────────────┘       └────────────────────────┘
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Kafka concepts, pub/sub model, topics, partitions, brokers, use cases | [core-concepts.md](references/core-concepts.md) |
| Producer API, configs (acks, retries, batch), serializers, partitioners | [producers.md](references/producers.md) |
| Consumer API, consumer groups, offsets, rebalancing, configs | [consumers.md](references/consumers.md) |
| KRaft controller, replication, request handling, storage, log compaction | [internals.md](references/internals.md) |
| Exactly-once, idempotent producer, transactions, consumer reliability | [reliability.md](references/reliability.md) |
| Kafka Connect, connectors, transforms (SMTs), data pipelines | [connect-and-pipelines.md](references/connect-and-pipelines.md) |
| Cross-cluster mirroring, MirrorMaker 2, geo-replication patterns | [cross-cluster.md](references/cross-cluster.md) |
| AdminClient API, broker/topic ops, partition reassignment, quotas, tuning | [operations.md](references/operations.md) |
| Metrics, JMX, consumer lag, broker health, alerting, monitoring tools | [monitoring.md](references/monitoring.md) |
| TLS encryption, SASL authentication, ACLs, authorization | [security.md](references/security.md) |
| Kafka Streams API, stateful/stateless ops, windowing, exactly-once streams | [streams.md](references/streams.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `core-concepts.md` | Ch. 1 | Pub/sub model, messages, schemas, topics, partitions, offsets, brokers, clusters, use cases |
| `producers.md` | Ch. 3 | KafkaProducer, ProducerRecord, send modes, acks, retries, idempotence, serializers, partitioners, key configs |
| `consumers.md` | Ch. 4 | KafkaConsumer, consumer groups, partition assignment, offsets, commit strategies, rebalancing, configs |
| `internals.md` | Ch. 5–6 | KRaft controller, cluster membership, leader election, replication protocol, request handling, log storage, compaction, tiered storage |
| `reliability.md` | Ch. 7 | Delivery guarantees (at-most/at-least/exactly-once), idempotent producer, transactions, consumer reliability patterns |
| `connect-and-pipelines.md` | Ch. 8 | Kafka Connect architecture, source/sink connectors, SMTs, schema registry integration, pipeline design |
| `cross-cluster.md` | Ch. 9 | MirrorMaker 2, active/active, active/passive replication, hub-and-spoke, use cases and tradeoffs |
| `operations.md` | Ch. 2, 10 | AdminClient API, topic management, partition reassignment, leader election, quotas, broker tuning, hardware |
| `monitoring.md` | Ch. 11 | Broker metrics, producer/consumer metrics, consumer lag, JMX, Prometheus/Grafana, alerting thresholds |
| `security.md` | Ch. 12 | TLS/SSL encryption, SASL mechanisms (PLAIN, SCRAM, GSSAPI, OAUTHBEARER), ACLs, authorization, audit |
| `streams.md` | Ch. 13–14 | Kafka Streams topology, KStream/KTable, stateful ops, windowing, exactly-once processing, interactive queries |

## Core Decision Trees

### Which Delivery Guarantee Do You Need?

```
What happens if a message is lost?
├── Lost messages are acceptable (metrics, logs, non-critical)
│   └── At-most-once: acks=0 or acks=1, no retries
│       → Highest throughput, lowest latency
│
├── Duplicates are acceptable but losses are not
│   └── At-least-once: acks=all, retries=MAX, enable.idempotence=false
│       → Default choice for most event-driven systems
│
└── Neither losses nor duplicates acceptable
    └── Exactly-once:
        ├── Producer only: enable.idempotence=true (idempotent producer)
        └── End-to-end: transactional.id set + Kafka Streams EOS
            → isolation.level=read_committed on consumers
```

### How Many Partitions?

```
What drives your partition count decision?
├── Target throughput per topic
│   └── partitions = max(target MB/s ÷ producer throughput per partition,
│                         target MB/s ÷ consumer throughput per partition)
├── Consumer parallelism ceiling
│   └── Max parallel consumers = partition count (one partition per consumer)
├── Broker capacity
│   └── Rule of thumb: ≤ 4,000 partitions per broker; ≤ 200,000 per cluster
└── Retention and storage
    └── More partitions = more open file handles; watch OS limits (ulimit -n)

Start conservative — you can add partitions later (but can't remove them).
Avoid over-partitioning: 10s of partitions per topic is usually enough.
```

### Producer acks Setting?

```
What is your durability requirement?
├── acks=0 → Fire and forget; no acknowledgment; possible loss even if broker is healthy
├── acks=1 → Leader acknowledges; loss possible if leader fails before replication
└── acks=all (or -1) → All in-sync replicas acknowledge; highest durability
    └── Pair with min.insync.replicas=2 on the broker/topic
```

### Consumer Offset Commit Strategy?

```
When should offsets be committed?
├── Auto-commit (enable.auto.commit=true)
│   └── Simple; risk of at-least-once duplicates or at-most-once loss
│       depending on crash timing
├── Manual commit after processing (commitSync)
│   └── At-least-once; blocks until broker confirms commit
├── Manual async commit (commitAsync)
│   └── At-least-once; higher throughput; no retry on failure
└── Commit specific offsets per partition
    └── Finest control; needed for exactly-once with external state stores
```

## Key Concepts Quick Reference

### Core Terminology

| Term | Definition |
|------|-----------|
| **Topic** | Named stream of records; logical grouping |
| **Partition** | Ordered, immutable log; unit of parallelism |
| **Offset** | Unique sequential ID of a record within a partition |
| **Broker** | A Kafka server; hosts partitions |
| **Leader** | Partition replica that handles all reads/writes |
| **Follower** | Replica that replicates from leader; can become leader |
| **ISR** | In-Sync Replicas — replicas caught up to the leader |
| **Consumer Group** | Set of consumers sharing partition assignment for a topic |
| **Lag** | Gap between latest offset produced and last committed by a consumer |
| **KRaft** | Kafka's Raft-based controller replacing ZooKeeper (Kafka 3.x+) |
| **Log Compaction** | Retention policy keeping only the latest value per key |

### Critical Config Quick Picks

**Producer — safety:**
```
acks=all
enable.idempotence=true
retries=2147483647
max.in.flight.requests.per.connection=5
```

**Consumer — safety:**
```
enable.auto.commit=false
isolation.level=read_committed  (if using transactions)
max.poll.interval.ms=300000     (must finish processing before this)
```

**Broker — durability:**
```
min.insync.replicas=2           (with replication.factor=3)
unclean.leader.election.enable=false
log.retention.hours=168         (7 days default)
```
