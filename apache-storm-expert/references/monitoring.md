# Storm Cluster Monitoring
## Chapter 7: JMX, Metrics, Grafana, and Alerting

---

## Storm UI

The built-in Storm web UI (default port 8080) provides real-time visibility into running topologies.

### Cluster Summary

- Total worker slots / used slots
- Supervisors online / dead
- Running topologies: count, names, uptime

### Topology Summary Page

Key metrics per topology (windows: 10m, 3h, 1d, all-time):

| Metric | Description |
|--------|-------------|
| **Emitted** | Total tuples emitted by all spouts and bolts |
| **Transferred** | Tuples sent between components (through network or in-process) |
| **Acked** | Tuples fully processed and acked back to the spout |
| **Failed** | Tuples that timed out or were explicitly failed |

### Component-Level (Bolt) Metrics

| Metric | Description |
|--------|-------------|
| **Capacity** | `(execute latency × execute count) / (window × 1000)`. Values near 1.0 = saturated |
| **Execute latency (ms)** | Average time to execute one tuple |
| **Process latency (ms)** | Average time from receiving tuple to acking it |
| **Executors** | Number of running executor threads |
| **Tasks** | Number of task instances |

**Capacity interpretation**:
- < 0.5: Healthy headroom
- 0.5–0.8: Normal load
- 0.8–1.0: Near saturation; consider scaling
- ≥ 1.0: Overloaded; tuples queuing; latency rising

### Spout Metrics

| Metric | Description |
|--------|-------------|
| **Complete latency (ms)** | Time from spout emit to full tree ack |
| **Acked** | Successfully completed tuple trees |
| **Failed** | Tuple trees that timed out or failed |

---

## JMX Integration

Storm exposes metrics via **Java Management Extensions (JMX)**, accessible by standard JVM monitoring tools (JConsole, VisualVM, Prometheus JMX Exporter, etc.).

### Enabling JMX on Workers

In `storm.yaml`:
```yaml
worker.childopts: >
  -verbose:gc
  -XX:+PrintGCDetails
  -Dcom.sun.management.jmxremote
  -Dcom.sun.management.jmxremote.port=9999
  -Dcom.sun.management.jmxremote.authenticate=false
  -Dcom.sun.management.jmxremote.ssl=false
```

### JVM Metrics Available via JMX

| MBean Domain | Attributes |
|-------------|------------|
| `java.lang:type=Memory` | `HeapMemoryUsage`, `NonHeapMemoryUsage` |
| `java.lang:type=GarbageCollector` | `CollectionCount`, `CollectionTime` |
| `java.lang:type=Threading` | `ThreadCount`, `PeakThreadCount`, `DaemonThreadCount` |
| `java.lang:type=ClassLoading` | `LoadedClassCount`, `TotalLoadedClassCount` |
| `java.lang:type=OperatingSystem` | `SystemCpuLoad`, `ProcessCpuLoad`, `FreePhysicalMemorySize` |

### Prometheus JMX Exporter

Expose JMX as Prometheus metrics:

```yaml
# jmx_exporter_config.yaml
rules:
  - pattern: "java.lang<type=Memory><HeapMemoryUsage>used"
    name: jvm_heap_used_bytes
  - pattern: "java.lang<type=GarbageCollector,name=(.*)><CollectionTime>"
    name: jvm_gc_collection_seconds_total
    labels:
      gc: "$1"
```

```yaml
# storm.yaml
worker.childopts: >
  -javaagent:/opt/jmx_prometheus_javaagent.jar=7777:/opt/jmx_exporter_config.yaml
```

---

## Storm Built-In Metrics System

Storm has a pluggable metrics API for custom application-level metrics.

### Registering Metrics in a Bolt/Spout

```java
public class MyBolt extends BaseRichBolt {
    private transient CountMetric _countMetric;
    private transient MeanReducer _meanMetric;

    public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
        // Register metric: name, metric impl, time bucket (seconds)
        _countMetric = context.registerMetric("tuple-count",
                                               new CountMetric(), 60);
        _meanMetric = context.registerMetric("process-time-ms",
                                              new MeanReducer(), 60);
    }

    public void execute(Tuple input) {
        long start = System.currentTimeMillis();
        // ... processing ...
        _countMetric.incr();
        _meanMetric.reduce((double)(System.currentTimeMillis() - start));
        collector.ack(input);
    }
}
```

### Built-In Metric Types

| Class | Description |
|-------|-------------|
| `CountMetric` | Cumulative counter; resets each time bucket |
| `MeanReducer` | Running mean of double values |
| `MultiCountMetric` | Map of named counters |
| `MultiReducedMetric` | Map of named reducers |
| `AssignableMetric` | Set to an arbitrary long value |

---

## Metric Reporters

### Console Reporter (Development/Debug)

```java
// In topology config
conf.registerMetricsConsumer(LoggingMetricsConsumer.class);
```

Logs metrics to the worker log file every 60 seconds (default).

### Custom Metrics Consumer

Implement `IMetricsConsumer` to send metrics anywhere:

```java
public class InfluxDBMetricsConsumer implements IMetricsConsumer {
    private InfluxDB influxDB;

    public void prepare(Map stormConf, Object registrationArgument,
                        TopologyContext context, IErrorReporter errorReporter) {
        influxDB = InfluxDBFactory.connect("http://influx:8086");
    }

    public void handleDataPoints(TaskInfo taskInfo,
                                 Collection<DataPoint> dataPoints) {
        for (DataPoint dp : dataPoints) {
            Point point = Point.measurement(dp.name)
                .addField("value", (Number) dp.value)
                .tag("topology", taskInfo.srcWorkerHost)
                .build();
            influxDB.write(point);
        }
    }

    public void cleanup() { influxDB.close(); }
}

// Register:
conf.registerMetricsConsumer(InfluxDBMetricsConsumer.class,
                              "http://influx:8086", 1);  // 1 task
```

---

## Grafana Dashboards

Typical Storm + Grafana setup:

```
Storm Worker JMX → Prometheus JMX Exporter → Prometheus → Grafana
Storm Metrics Consumer → InfluxDB → Grafana
Storm Nimbus REST API → custom scraper → Prometheus → Grafana
```

### Key Panels for a Storm Dashboard

**Cluster Overview**:
- Total workers running / total slots
- Active topologies
- Supervisor count

**Per-Topology**:
- Tuples acked/failed per second (rate)
- Complete latency (spout end-to-end)
- Worker JVM heap usage %
- GC time %

**Per-Bolt**:
- Capacity (alert when > 0.8)
- Execute latency ms
- Failed tuples rate

### Sample PromQL Queries

```promql
# Heap usage %
jvm_heap_used_bytes / jvm_heap_max_bytes * 100

# GC time rate (seconds per second)
rate(jvm_gc_collection_seconds_total[1m])

# Alert: high GC time
rate(jvm_gc_collection_seconds_total[5m]) > 0.1
```

---

## Alerting

### Slack Alerting (via custom metrics consumer)

```java
public void handleDataPoints(TaskInfo taskInfo, Collection<DataPoint> dataPoints) {
    for (DataPoint dp : dataPoints) {
        if (dp.name.equals("tuple-fail-rate") && (Double) dp.value > 0.01) {
            SlackClient.send("#storm-alerts",
                String.format("ALERT: %s fail rate %.2f%% on %s",
                    taskInfo.srcComponentId, (Double) dp.value * 100,
                    taskInfo.srcWorkerHost));
        }
    }
}
```

### Alert Thresholds Reference

| Metric | Warning | Critical |
|--------|---------|----------|
| Bolt capacity | > 0.8 | > 0.95 |
| Complete latency | > 2× baseline | > 5× baseline |
| Failed tuple rate | > 0.1% | > 1% |
| Worker heap usage | > 70% | > 85% |
| GC time % | > 5% | > 15% |
| Supervisor heartbeat age | > 20s | > 30s (dead supervisor) |

---

## Troubleshooting via Logs

Storm log locations:
```
$STORM_HOME/logs/nimbus.log         # Nimbus logs
$STORM_HOME/logs/supervisor.log     # Supervisor logs
$STORM_HOME/logs/workers-artifacts/ # Worker logs per topology
  └── <topology-id>/
        └── <port>/
              └── worker.log
```

Enable Storm log viewer for web-based log access at `http://supervisor-host:8000`.

### Common Log Signals

| Log Message | Meaning |
|-------------|---------|
| `"Topology ... is not alive"` | Nimbus lost contact with workers |
| `"Bolt ... is slow"` | Bolt capacity near 1.0; consider scaling |
| `"Timeout ... fail"` | Tuples not acked within `message.timeout.secs` |
| `"Killing worker"` | Supervisor killed worker (OOM, crash, or rebalance) |
| `"java.lang.OutOfMemoryError"` | Worker heap exhausted; increase `worker.heap.memory.mb` |
