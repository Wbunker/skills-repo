# Ch 7 — Coordinator: Data Triggers

## Table of Contents
- [Data Availability Trigger](#data-availability-trigger)
- [Dataset Definition](#dataset-definition)
- [done-flag Behavior](#done-flag-behavior)
- [Input & Output Events](#input--output-events)
- [Data EL Functions](#data-el-functions)
- [URI Template Variables](#uri-template-variables)
- [HCatalog Integration](#hcatalog-integration)
- [Full Example](#full-example)
- [Gotchas](#gotchas)

---

## Data Availability Trigger

A coordinator can wait for input HDFS paths (or HCatalog partitions) to exist before launching a workflow action. The action remains in `WAITING` state until all declared inputs are satisfied or `<timeout>` expires.

---

## Dataset Definition

Datasets describe time-partitioned HDFS directories (or HCatalog tables).

```xml
<datasets>
  <dataset name="raw-logs"
           frequency="${coord:days(1)}"
           initial-instance="2024-01-01T00:00Z"
           timezone="UTC">
    <uri-template>
      hdfs://namenode:8020/data/logs/${YEAR}/${MONTH}/${DAY}
    </uri-template>
    <done-flag>_SUCCESS</done-flag>
  </dataset>

  <dataset name="processed-output"
           frequency="${coord:days(1)}"
           initial-instance="2024-01-01T00:00Z"
           timezone="UTC">
    <uri-template>
      hdfs://namenode:8020/data/processed/${YEAR}/${MONTH}/${DAY}
    </uri-template>
    <done-flag></done-flag>  <!-- directory existence is sufficient -->
  </dataset>
</datasets>
```

Datasets can also be in a shared `datasets.xml` file and included:
```xml
<include>${nameNode}/shared/datasets.xml</include>
```

---

## done-flag Behavior

| `<done-flag>` value | Trigger condition |
|--------------------|-------------------|
| Omitted | `_SUCCESS` file must exist in directory |
| `_SUCCESS` | `_SUCCESS` file must exist |
| `""` (empty string) | Directory must exist (any content) |
| `"myfile.done"` | Named file must exist in directory |

Empty done-flag is common for downstream datasets that Oozie itself writes — no `_SUCCESS` marker is created by Oozie.

---

## Input & Output Events

```xml
<input-events>
  <data-in name="daily-input" dataset="raw-logs">
    <instance>${coord:current(0)}</instance>
  </data-in>
</input-events>

<output-events>
  <data-out name="daily-output" dataset="processed-output">
    <instance>${coord:current(0)}</instance>
  </data-out>
</output-events>

<action>
  <workflow>
    <app-path>${workflowAppPath}</app-path>
    <configuration>
      <property>
        <name>inputPath</name>
        <value>${coord:dataIn('daily-input')}</value>
      </property>
      <property>
        <name>outputPath</name>
        <value>${coord:dataOut('daily-output')}</value>
      </property>
    </configuration>
  </workflow>
</action>
```

`coord:dataIn('name')` resolves to the comma-separated list of all input URIs (useful for ranges).
`coord:dataOut('name')` resolves to the single output URI.

---

## Data EL Functions

| Function | Meaning |
|----------|---------|
| `${coord:current(0)}` | This action's nominal time dataset instance |
| `${coord:current(-1)}` | Previous instance |
| `${coord:current(-N)}` | N instances back |
| `${coord:latest(0)}` | Most recently available instance at runtime |
| `${coord:latest(-N)}` | Nth most recently available instance |
| `${coord:future(1, 24)}` | Next instance, look-ahead max 24 hours |
| `${coord:offset(N, 'HOUR')}` | Instance offset by N hours |
| `${coord:offset(N, 'DAY')}` | Instance offset by N days |

**Range of instances** (loads a window of data):
```xml
<data-in name="last-7-days" dataset="raw-logs">
  <start-instance>${coord:current(-6)}</start-instance>
  <end-instance>${coord:current(0)}</end-instance>
</data-in>
```
`coord:dataIn('last-7-days')` returns comma-separated paths for all 7 instances.

`coord:latest(0)` vs `coord:current(0)`:
- `current(0)` — always the nominal time instance (may not exist yet)
- `latest(0)` — the most recently available instance at the moment the action is about to run (useful for "process whatever is newest")

---

## URI Template Variables

Date component variables (UTC-based):

| Variable | Format |
|----------|--------|
| `${YEAR}` | 4-digit year, e.g. `2024` |
| `${MONTH}` | 2-digit month, e.g. `01`–`12` |
| `${DAY}` | 2-digit day, e.g. `01`–`31` |
| `${HOUR}` | 2-digit hour, e.g. `00`–`23` |
| `${MINUTE}` | 2-digit minute, e.g. `00`–`59` |

---

## HCatalog Integration

Use HCatalog partition availability instead of HDFS path existence:

```xml
<dataset name="hcat-events"
         frequency="${coord:days(1)}"
         initial-instance="2024-01-01T00:00Z"
         timezone="UTC">
  <uri-template>
    hcat://metastore:9083/mydb/events/dt=${YEAR}-${MONTH}-${DAY}
  </uri-template>
  <!-- no done-flag: HCatalog triggers on partition registration -->
</dataset>
```

HCatalog-specific EL functions in workflow action config:
```xml
<property><name>db</name><value>${coord:databaseIn('hcat-events')}</value></property>
<property><name>table</name><value>${coord:tableIn('hcat-events')}</value></property>
<property><name>partFilter</name><value>${coord:dataInPartitionFilter('hcat-events', 'hive')}</value></property>
<!-- partFilter resolves to: dt='2024-01-01' -->
```

HCatalog requires Oozie to be built with HCatalog support and `oozie.service.ProxyUserService.proxyuser.*` configured.

---

## Full Example

```xml
<coordinator-app name="data-triggered-etl"
                 frequency="${coord:days(1)}"
                 start="2024-01-01T00:00Z"
                 end="2025-01-01T00:00Z"
                 timezone="UTC"
                 xmlns="uri:oozie:coordinator:0.2">
  <controls>
    <timeout>120</timeout>
    <concurrency>2</concurrency>
    <execution>FIFO</execution>
  </controls>

  <datasets>
    <dataset name="input-data" frequency="${coord:days(1)}"
             initial-instance="2024-01-01T00:00Z" timezone="UTC">
      <uri-template>hdfs://nn:8020/data/raw/${YEAR}/${MONTH}/${DAY}</uri-template>
      <done-flag>_SUCCESS</done-flag>
    </dataset>
    <dataset name="output-data" frequency="${coord:days(1)}"
             initial-instance="2024-01-01T00:00Z" timezone="UTC">
      <uri-template>hdfs://nn:8020/data/processed/${YEAR}/${MONTH}/${DAY}</uri-template>
      <done-flag></done-flag>
    </dataset>
  </datasets>

  <input-events>
    <data-in name="in" dataset="input-data">
      <instance>${coord:current(0)}</instance>
    </data-in>
  </input-events>
  <output-events>
    <data-out name="out" dataset="output-data">
      <instance>${coord:current(0)}</instance>
    </data-out>
  </output-events>

  <action>
    <workflow>
      <app-path>${workflowAppPath}</app-path>
      <configuration>
        <property><name>inputPath</name><value>${coord:dataIn('in')}</value></property>
        <property><name>outputPath</name><value>${coord:dataOut('out')}</value></property>
        <property><name>date</name><value>${coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')}</value></property>
      </configuration>
    </workflow>
  </action>
</coordinator-app>
```

---

## Gotchas

1. **`done-flag` default is `_SUCCESS`**: If upstream jobs don't write `_SUCCESS`, actions wait forever (or until `<timeout>`). Set `<done-flag></done-flag>` for directory-based triggers.

2. **`coord:latest(0)` vs `coord:current(0)`**: `latest(0)` resolves at action runtime to the most recently available instance — it can change between check cycles. `current(0)` is deterministic (always the nominal time instance).

3. **Input events cause WAITING**: The action stays WAITING until all `<data-in>` paths satisfy their `done-flag`. With `<timeout>-1</timeout>` this waits forever; ensure upstream jobs always land data or set a reasonable timeout.

4. **URI template variables are UTC**: Even if the coordinator timezone is `America/New_York`, `${YEAR}/${MONTH}/${DAY}` in a URI template always uses UTC. Use `coord:formatTime(coord:nominalTime(), 'yyyy')` etc. if you need local-timezone paths.
