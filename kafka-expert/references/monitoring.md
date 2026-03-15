# Monitoring Kafka
## Chapter 11: Metrics, JMX, Consumer Lag, Alerting, Observability

---

## Monitoring Philosophy

Kafka exposes thousands of metrics via JMX. The challenge isn't collecting metrics — it's knowing **which ones matter** and **what thresholds to alert on**. Effective Kafka monitoring requires:

1. **Cluster health** — is the cluster operational?
2. **Producer health** — are producers sending successfully?
3. **Consumer health** — are consumers keeping up?
4. **Performance** — is the cluster performing within SLAs?
5. **Capacity** — are we approaching limits?

---

## Metrics Collection

### JMX

Kafka exposes all metrics via **JMX (Java Management Extensions)**. Enable remote JMX:

```bash
export JMX_PORT=9999
# Or in kafka-server-start.sh:
KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote \
  -Dcom.sun.management.jmxremote.authenticate=false \
  -Dcom.sun.management.jmxremote.ssl=false \
  -Dcom.sun.management.jmxremote.port=9999"
```

JMX MBean naming: `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec`

### Prometheus + JMX Exporter (Recommended)

The **JMX Exporter** (Prometheus Java agent) scrapes JMX and exposes metrics in Prometheus format:

```bash
# Start Kafka with JMX Exporter agent
export KAFKA_OPTS="-javaagent:/opt/jmx_exporter/jmx_prometheus_javaagent.jar=7071:/opt/jmx_exporter/kafka.yml"
```

Metrics then available at `http://broker:7071/metrics` for Prometheus scraping.

**Grafana dashboards**: Confluent and the community maintain pre-built Grafana dashboards for Kafka. Start with the Grafana.com dashboard ID 7589 (Kafka Overview).

### Kafka Exporter (Consumer Lag)

The `kafka-exporter` project provides detailed consumer lag metrics beyond what the JMX exporter captures:

```yaml
# prometheus scrape config
- job_name: kafka-exporter
  static_configs:
    - targets: ['kafka-exporter:9308']
```

---

## Broker Metrics

### Cluster-Level Health (Alert On These)

| Metric | MBean | Normal | Alert |
|--------|-------|--------|-------|
| **UnderReplicatedPartitions** | `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | 0 | > 0 |
| **OfflinePartitionsCount** | `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | 0 | > 0 |
| **ActiveControllerCount** | `kafka.controller:type=KafkaController,name=ActiveControllerCount` | 1 | ≠ 1 |
| **UncleanLeaderElectionsPerSec** | `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec` | 0 | > 0 |

**`UnderReplicatedPartitions > 0`**: A replica is not caught up. Could indicate broker overload, disk issues, or network problems. This is the single most important broker health signal.

**`OfflinePartitionsCount > 0`**: A partition has no leader — producers and consumers will get errors for that partition. Critical severity.

**`ActiveControllerCount ≠ 1`**: 0 means no controller (cluster cannot function); 2 means split-brain (should not happen). Both are critical.

### Throughput Metrics

| Metric | MBean Pattern | Notes |
|--------|--------------|-------|
| **Messages in/sec** | `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec` | Total + per-topic variants |
| **Bytes in/sec** | `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec` | Monitor for capacity planning |
| **Bytes out/sec** | `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec` | Includes replication traffic |
| **Replication bytes in/sec** | `kafka.server:type=BrokerTopicMetrics,name=ReplicationBytesInPerSec` | Follower fetch traffic |

**Expected**: Bytes out ≈ (Bytes in × replication_factor) + (consumer read traffic)

### Request Metrics

| Metric | What It Indicates |
|--------|-----------------|
| `RequestHandlerAvgIdlePercent` | % of time I/O threads are idle; low % means overloaded |
| `NetworkProcessorAvgIdlePercent` | % of time network threads are idle |
| `Produce:RequestsPerSec` | Produce request rate |
| `FetchConsumer:RequestsPerSec` | Consumer fetch rate |
| `Produce:TotalTimeMs` (99th percentile) | P99 produce latency; alert if growing |

**Alert**: `RequestHandlerAvgIdlePercent < 20%` — broker I/O threads are overloaded.

### Disk and Storage

| Metric | Notes |
|--------|-------|
| Disk usage % (OS-level) | Alert at 70%, critical at 85% — Kafka needs headroom |
| `LogEndOffset` per partition | Tracks write progress |
| `LogFlushRateAndTimeMs` | If explicit flush is enabled, monitor its performance |

---

## Producer Metrics

Monitor from the **producer application side** (JMX on the producer process):

| Metric | MBean | Alert |
|--------|-------|-------|
| **record-error-rate** | `kafka.producer:type=producer-metrics,name=record-error-rate` | > 0 (any errors) |
| **record-retry-rate** | `kafka.producer:type=producer-metrics,name=record-retry-rate` | Growing (indicates broker issues) |
| **request-latency-avg** | `kafka.producer:type=producer-metrics,name=request-latency-avg` | SLA-dependent |
| **outgoing-byte-rate** | `kafka.producer:type=producer-metrics,name=outgoing-byte-rate` | Capacity check |
| **buffer-available-bytes** | `kafka.producer:type=producer-metrics,name=buffer-available-bytes` | Alert if near 0 (producer blocked) |
| **batch-size-avg** | `kafka.producer:type=producer-metrics,name=batch-size-avg` | Sanity check against config |

---

## Consumer Metrics and Lag

Consumer lag is the most actionable consumer health signal.

### Consumer Lag

**Lag** = Latest offset on the partition − Consumer's committed offset

```
Partition: [0][1][2][3][4][5][6][7][8][9]
                                    ↑
                              Latest offset = 9
               ↑
        Committed offset = 3

Lag = 9 - 3 = 6
```

**High lag** = consumer is falling behind producers. Causes:
- Consumer processing is too slow (scale out consumers or optimize processing)
- Consumer is stuck (crashed, deadlocked, long GC pause)
- Upstream spike in produce volume

### Monitoring Lag

```bash
# CLI
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --describe --group my-group

# Output:
GROUP        TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
my-group     orders   0          1500            1506            6
my-group     orders   1          2300            2300            0
my-group     orders   2          1100            1200            100  ← lag growing
```

**Alert patterns:**
- Lag > N messages (fixed threshold based on acceptable delay)
- Lag **growing** over time (even if small — trend matters)
- Lag on specific partitions while others are at 0 (indicates skew or consumer stuck)

### Consumer JMX Metrics

| Metric | MBean | Notes |
|--------|-------|-------|
| **records-lag-max** | `kafka.consumer:type=consumer-fetch-manager-metrics,name=records-lag-max` | Worst lag across partitions |
| **fetch-rate** | `kafka.consumer:type=consumer-fetch-manager-metrics,name=fetch-rate` | Fetch requests per second |
| **records-consumed-rate** | `kafka.consumer:type=consumer-fetch-manager-metrics,name=records-consumed-rate` | Records processed per second |
| **commit-rate** | `kafka.consumer:type=consumer-coordinator-metrics,name=commit-rate` | Offset commits per second |
| **join-rate** | `kafka.consumer:type=consumer-coordinator-metrics,name=join-rate` | Group rejoins per second; high = frequent rebalances |
| **sync-rate** | `kafka.consumer:type=consumer-coordinator-metrics,name=sync-rate` | Group syncs per second; high = frequent rebalances |

**Alert on**: `join-rate > 0` for extended periods — indicates excessive rebalancing.

---

## End-to-End Latency

Measure the time from event creation to consumer processing:

**Approach 1**: Include event timestamp in message. Consumer records processing timestamp. Difference = end-to-end latency.

**Approach 2**: Use `kafka-producer-perf-test.sh` and `kafka-consumer-perf-test.sh` for baseline measurement.

**Approach 3**: Distributed tracing (OpenTelemetry) with trace context propagated through Kafka headers.

---

## Log and Tooling

### Kafka Broker Logs

```
# Key log files
server.log           — Broker lifecycle, errors, warnings
controller.log       — Controller elections, partition movements
state-change.log     — ISR changes, leader elections
kafka-request.log    — All requests (if enabled; verbose)
```

**Alert patterns in server.log:**
- `ERROR` or `FATAL` messages → immediate investigation
- Repeated `[ReplicaManager] Partition ... is under replicated` → ISR problems
- `RequestHandlerPool: 25% idle` → broker overload

### Useful CLI Checks

```bash
# Check which topics have under-replicated partitions
kafka-topics.sh --bootstrap-server broker:9092 \
  --describe --under-replicated-partitions

# Check which topics have offline partitions
kafka-topics.sh --bootstrap-server broker:9092 \
  --describe --unavailable-partitions

# Check consumer group status
kafka-consumer-groups.sh --bootstrap-server broker:9092 \
  --describe --all-groups

# Dump log segment contents (debugging)
kafka-dump-log.sh --files /data/kafka-logs/orders-0/00000000000000000000.log \
  --print-data-log
```

---

## Alerting Summary

### Critical (Page Immediately)

| Alert | Condition |
|-------|-----------|
| Partition offline | `OfflinePartitionsCount > 0` |
| No active controller | `ActiveControllerCount ≠ 1` |
| Broker down | Broker JMX unreachable |
| Disk full | Disk usage > 85% |

### Warning (Investigate Soon)

| Alert | Condition |
|-------|-----------|
| Under-replicated partitions | `UnderReplicatedPartitions > 0` for > 5 min |
| ISR shrinking | `IsrShrinksPerSec > 0` sustained |
| Consumer lag growing | Lag trend increasing for > 10 min |
| Producer errors | `record-error-rate > 0` |
| Broker I/O overloaded | `RequestHandlerAvgIdlePercent < 20%` |

### Informational (Trend and Capacity)

| Alert | Condition |
|-------|-----------|
| Disk at 70% | Plan expansion |
| Message rate near capacity | Plan scaling |
| Frequent rebalances | `join-rate > 0` sustained |
