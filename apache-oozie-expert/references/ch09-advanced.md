# Ch 9 — Advanced Topics

## Table of Contents
- [SLA Monitoring](#sla-monitoring)
- [Sharelib Management](#sharelib-management)
- [JAR Loading Precedence](#jar-loading-precedence)
- [Cron-Type Scheduling](#cron-type-scheduling)
- [HCatalog Deep Dive](#hcatalog-deep-dive)
- [MapReduce New API](#mapreduce-new-api)

---

## SLA Monitoring

SLA tracks whether workflows and coordinator actions meet start/end/duration targets.

### Enable SLA in oozie-site.xml

```xml
<property>
  <name>oozie.service.EventHandlerService.event.listeners</name>
  <value>
    org.apache.oozie.sla.listener.SLAJobEventListener,
    org.apache.oozie.sla.listener.SLAEmailEventListener
  </value>
</property>
<property>
  <name>oozie.sla.service.SLAService.capacity</name>
  <value>5000</value>
</property>
```

### SLA XML (workflow schema 0.5 required)

```xml
<workflow-app name="sla-workflow" xmlns="uri:oozie:workflow:0.5"
              xmlns:sla="uri:oozie:sla:0.2">
  ...
  <action name="etl-job">
    <map-reduce>...</map-reduce>
    <ok to="end"/>
    <error to="fail"/>
    <sla:info>
      <sla:nominal-time>${nominal_time}</sla:nominal-time>
      <sla:should-start>${10 * MINUTES}</sla:should-start>
      <sla:should-end>${2 * HOURS}</sla:should-end>
      <sla:max-duration>${90 * MINUTES}</sla:max-duration>
      <sla:alert-events>start_miss,end_miss,duration_miss</sla:alert-events>
      <sla:alert-contact>ops@example.com,oncall@example.com</sla:alert-contact>
    </sla:info>
  </action>
  ...
</workflow-app>
```

Workflow-level SLA (outside actions):
```xml
<workflow-app name="sla-workflow" xmlns="uri:oozie:workflow:0.5"
              xmlns:sla="uri:oozie:sla:0.2">
  <sla:info>
    <sla:nominal-time>${nominal_time}</sla:nominal-time>
    <sla:should-end>${3 * HOURS}</sla:should-end>
    <sla:alert-events>end_miss</sla:alert-events>
    <sla:alert-contact>ops@example.com</sla:alert-contact>
  </sla:info>
  <start to="first-action"/>
  ...
</workflow-app>
```

### SLA Fields

| Field | Meaning |
|-------|---------|
| `nominal-time` | Reference time for SLA calculations (usually `${coord:nominalTime()}`) |
| `should-start` | How many minutes after nominal-time the job should start by |
| `should-end` | How many minutes after nominal-time the job should complete by |
| `max-duration` | Maximum allowed run duration in minutes |
| `alert-events` | Comma-sep: `start_miss`, `end_miss`, `duration_miss` |
| `alert-contact` | Comma-sep email addresses |

### SLA Statuses

`NOT_STARTED` → `IN_PROCESS` → `MET` or `MISS`

Event types: `START_MET`, `START_MISS`, `END_MET`, `END_MISS`, `DURATION_MET`, `DURATION_MISS`

### Runtime SLA Modification

```bash
# Change should-end deadline
oozie job -oozie http://oozie:11000/oozie -action sla-change <job-id> -value should-end=2024-01-01T12:00Z

# Disable SLA for specific actions
oozie job -oozie http://oozie:11000/oozie -action sla-disable <coord-id> -action-list 3-5

# Enable SLA
oozie job -oozie http://oozie:11000/oozie -action sla-enable <coord-id> -action-list 1,14,17-20
```

### SLA REST API

```
GET /v2/sla?jobid=<id>&app-name=my-workflow&nominal-start=2024-01-01T00:00Z&nominal-end=2024-01-02T00:00Z
```

---

## Sharelib Management

Sharelibs are JARs on HDFS used by Hive, Pig, Spark, Sqoop actions.

```bash
# Deploy sharelib (run after Oozie upgrade or adding new JARs)
bin/oozie-setup.sh sharelib create -fs hdfs://namenode:8020

# Add custom JARs to existing sharelib
hdfs dfs -put myjar.jar /user/oozie/share/lib/lib_<timestamp>/hive/

# Hot-update without Oozie restart
oozie admin -sharelibupdate

# List available sharelibs
oozie admin -shareliblist
oozie admin -shareliblist spark

# Check which sharelib version is active
oozie admin -shareliblist | grep "Available ShareLib"
```

Custom sharelib mapping (`oozie-site.xml`):
```xml
<property>
  <name>oozie.service.ShareLibService.mapping.file</name>
  <value>hdfs://namenode/user/oozie/sharelib-mapping.properties</value>
</property>
```

`sharelib-mapping.properties`:
```properties
oozie.sharelib.for.hive=hdfs://namenode/user/oozie/custom/hive-libs
oozie.sharelib.for.spark=hdfs://namenode/user/oozie/custom/spark-libs
```

**Job property to enable**: `oozie.use.system.libpath=true` (required for all sharelib-backed actions)

---

## JAR Loading Precedence

When Oozie resolves JARs for an action, this is the priority order (highest → lowest):

1. `<file>` / `<archive>` elements in the action XML (symlinked into working dir)
2. Workflow app's `lib/` directory (HDFS)
3. Sharelib for the action type (if `oozie.use.system.libpath=true`)
4. Oozie server classpath

Use action-level `<file>` for action-specific dependencies to avoid JAR conflicts:
```xml
<hive ...>
  <file>${nameNode}/jars/custom-udf.jar#custom-udf.jar</file>
</hive>
```

The `#local_name` part is the symlink name in the working directory.

---

## Cron-Type Scheduling

See `ch06-coordinator-time.md` for the full cron syntax table. Key notes for advanced use:

**Cron with data triggers** — combine cron frequency with data inputs:
```xml
<coordinator-app name="hourly-with-data-check"
                 frequency="0 * * * *"
                 start="2024-01-01T00:00Z"
                 end="2025-01-01T00:00Z"
                 timezone="UTC"
                 xmlns="uri:oozie:coordinator:0.2">
  <!-- ...datasets, input-events, etc... -->
</coordinator-app>
```

Cron coordinators can have both time-based and data-based triggers.

**Cron uses Oozie server timezone by default.** To get local-time behavior, set the `timezone` attribute of the coordinator to the target timezone — but cron field evaluation still uses server time. Safest practice: always use UTC and compute local offsets manually.

---

## HCatalog Deep Dive

See `ch07-coordinator-data.md` for basic HCatalog dataset setup.

Advanced HCatalog EL functions:
```
coord:databaseIn('name')                          — database name from input event
coord:databaseOut('name')                         — database name from output event
coord:tableIn('name')                             — table name from input event
coord:tableOut('name')                            — table name from output event
coord:dataInPartitionFilter('name', 'hive')       — Hive partition filter string, e.g. dt='2024-01-01'
coord:dataInPartitionFilter('name', 'pig')        — Pig partition filter
coord:dataInPartitionFilter('name', 'java-properties')  — Java properties format
coord:dataOutPartitions('name')                   — output partition map
coord:dataInPartitionMin('name', 'dt')            — minimum partition value across range
coord:dataInPartitionMax('name', 'dt')            — maximum partition value across range
```

Oozie config for HCatalog:
```xml
<property>
  <name>oozie.service.ProxyUserService.proxyuser.hive.hosts</name><value>*</value>
</property>
<property>
  <name>oozie.service.ProxyUserService.proxyuser.hive.groups</name><value>*</value>
</property>
```

---

## MapReduce New API

For Hadoop 2+ YARN jobs using the `org.apache.hadoop.mapreduce` (new) API instead of `org.apache.hadoop.mapred` (old):

```xml
<map-reduce>
  <job-tracker>${jobTracker}</job-tracker>
  <name-node>${nameNode}</name-node>
  <configuration>
    <!-- New API mapper/reducer (mapreduce.* namespace) -->
    <property><name>mapreduce.job.inputformat.class</name><value>org.apache.hadoop.mapreduce.lib.input.TextInputFormat</value></property>
    <property><name>mapreduce.input.fileinputformat.inputdir</name><value>${inputDir}</value></property>
    <property><name>mapreduce.output.fileoutputformat.outputdir</name><value>${outputDir}</value></property>
    <property><name>mapreduce.job.map.class</name><value>org.example.NewApiMapper</value></property>
    <property><name>mapreduce.job.reduce.class</name><value>org.example.NewApiReducer</value></property>
    <!-- Output key/value types -->
    <property><name>mapreduce.job.output.key.class</name><value>org.apache.hadoop.io.Text</value></property>
    <property><name>mapreduce.job.output.value.class</name><value>org.apache.hadoop.io.IntWritable</value></property>
  </configuration>
</map-reduce>
```
