# Data Trigger Coordinators
## Chapter 7: Data Trigger Coordinator

---

## What Are Data Triggers?

A **data trigger** causes a coordinator action to wait until specified input data is available before submitting the workflow. The coordinator polls the defined data locations and only fires when all required data is present.

This solves a fundamental pipeline problem: downstream jobs should not start until upstream jobs have produced their output.

```
Upstream pipeline writes /data/2024-03-15/_SUCCESS
                               │
Coordinator polls for file presence
                               │
                               ▼
Coordinator action transitions WAITING → READY → SUBMITTED
```

---

## Datasets

A **dataset** describes where data lives and how it is partitioned by time. The coordinator uses the dataset definition to compute the expected path for each nominal time.

### HDFS Dataset

```xml
<datasets>
  <dataset name="input-data"
           frequency="${coord:days(1)}"
           initial-instance="2024-01-01T00:00Z"
           timezone="UTC">
    <uri-template>/data/input/${YEAR}/${MONTH}/${DAY}</uri-template>
    <done-flag>_SUCCESS</done-flag>
  </dataset>
</datasets>
```

- `uri-template`: path template with time variables (`${YEAR}`, `${MONTH}`, `${DAY}`, `${HOUR}`, `${MINUTE}`)
- `done-flag`: filename whose existence signals the dataset partition is complete. If empty (`<done-flag/>`), Oozie checks for the directory itself rather than a flag file.
- `frequency`: how frequently the dataset is produced (must match the upstream pipeline's frequency)
- `initial-instance`: earliest dataset instance (nominal time of the first partition)

### HCatalog Dataset

For Hive metastore partition availability:

```xml
<dataset name="hcat-input"
         frequency="${coord:days(1)}"
         initial-instance="2024-01-01T00:00Z"
         timezone="UTC">
  <uri-template>
    hcat://metastore:9083/mydb/orders/dt=${YEAR}-${MONTH}-${DAY}
  </uri-template>
</dataset>
```

Oozie registers a JMS listener with HCatalog and is notified when the partition is added — no polling needed.

---

## Input and Output Events

### Input Events

`<input-events>` declares what data must exist before the coordinator action fires:

```xml
<input-events>
  <data-in name="raw-input" dataset="input-data">
    <instance>${coord:current(0)}</instance>
  </data-in>
</input-events>
```

- `${coord:current(0)}`: the dataset instance at the current nominal time (today's partition)
- `${coord:current(-1)}`: yesterday's partition
- `${coord:current(-7)}` through `${coord:current(0)}`: the last 7 days' partitions

### Multiple Input Instances (Range)

```xml
<data-in name="last-7-days" dataset="daily-input">
  <start-instance>${coord:current(-6)}</start-instance>
  <end-instance>${coord:current(0)}</end-instance>
</data-in>
```

All instances in the range must be present for the action to fire.

### Multiple Datasets

```xml
<input-events>
  <data-in name="transactions" dataset="txn-data">
    <instance>${coord:current(0)}</instance>
  </data-in>
  <data-in name="reference" dataset="ref-data">
    <instance>${coord:current(0)}</instance>
  </data-in>
</input-events>
```

Both datasets must be available before the action fires.

### Output Events

`<output-events>` declares what data this coordinator action will produce:

```xml
<output-events>
  <data-out name="processed-output" dataset="output-data">
    <instance>${coord:current(0)}</instance>
  </data-out>
</output-events>
```

This is used by downstream coordinators that declare this dataset as their input — creating an implicit dependency chain.

---

## Full Data Trigger Coordinator Example

```xml
<coordinator-app name="daily-transform"
                 frequency="${coord:days(1)}"
                 start="2024-01-01T00:00Z"
                 end="2025-01-01T00:00Z"
                 timezone="UTC"
                 xmlns="uri:oozie:coordinator:0.4">

  <controls>
    <timeout>480</timeout>       <!-- wait up to 8 hours for data -->
    <concurrency>1</concurrency>
    <execution>FIFO</execution>
  </controls>

  <datasets>
    <dataset name="raw-events"
             frequency="${coord:days(1)}"
             initial-instance="2024-01-01T00:00Z"
             timezone="UTC">
      <uri-template>/data/raw/${YEAR}/${MONTH}/${DAY}</uri-template>
      <done-flag>_SUCCESS</done-flag>
    </dataset>

    <dataset name="processed-events"
             frequency="${coord:days(1)}"
             initial-instance="2024-01-01T00:00Z"
             timezone="UTC">
      <uri-template>/data/processed/${YEAR}/${MONTH}/${DAY}</uri-template>
      <done-flag>_SUCCESS</done-flag>
    </dataset>
  </datasets>

  <input-events>
    <data-in name="input" dataset="raw-events">
      <instance>${coord:current(0)}</instance>
    </data-in>
  </input-events>

  <output-events>
    <data-out name="output" dataset="processed-events">
      <instance>${coord:current(0)}</instance>
    </data-out>
  </output-events>

  <action>
    <workflow>
      <app-path>${wfPath}</app-path>
      <configuration>
        <property>
          <name>inputPath</name>
          <value>${coord:dataIn("input")}</value>
        </property>
        <property>
          <name>outputPath</name>
          <value>${coord:dataOut("output")}</value>
        </property>
      </configuration>
    </workflow>
  </action>

</coordinator-app>
```

---

## Data Availability EL Functions

| Function | Returns |
|----------|---------|
| `${coord:dataIn("name")}` | Comma-separated resolved HDFS paths for the named input |
| `${coord:dataOut("name")}` | Resolved HDFS path for the named output |
| `${coord:current(n)}` | Dataset instance at offset n (0=current, -1=previous, etc.) |
| `${coord:latest(-1)}` | Most recently available dataset instance before nominal time |
| `${coord:future(1, 24)}` | Next available instance within 24 hours after nominal time |
| `${coord:offset(n, "HOUR")}` | Dataset instance offset by n hours |

### Using dataIn in the Workflow

`${coord:dataIn("input")}` resolves to one or more HDFS paths (comma-separated for ranges). Pass it to the workflow and use it as the input directory:

```xml
<property>
  <name>inputPath</name>
  <value>${coord:dataIn("input")}</value>
</property>
```

In the workflow action: `<arg>--inputPath</arg><arg>${inputPath}</arg>`

---

## Dataset Dependency Chain (Pipeline Pattern)

When coordinators are chained — one produces output that the next consumes — the datasets create an implicit dependency:

```
CoordA: produces /data/stage1/${YEAR}/${MONTH}/${DAY}
                        │
                        │ CoordB <input-events> references stage1 dataset
                        ▼
CoordB: consumes /data/stage1/..., produces /data/stage2/${YEAR}/${MONTH}/${DAY}
                        │
                        │ CoordC <input-events> references stage2 dataset
                        ▼
CoordC: consumes /data/stage2/..., produces final output
```

Each coordinator's `<timeout>` must accommodate the upstream pipeline's total runtime. Group these in a **bundle** for coordinated management.

---

## HCatalog-Based Dependencies (Push-Based)

With HDFS datasets, Oozie polls for the `_SUCCESS` file at intervals. With HCatalog datasets, HCatalog pushes a JMS notification to Oozie when a partition is added — no polling delay.

Configure JMS in `oozie-site.xml`:

```xml
<property>
  <name>oozie.service.HCatAccessorService.jmsconnectioninfo</name>
  <value>hcat://metastore:9083#java.naming.factory.initial=...</value>
</property>
```

HCatalog partition dependency fires as soon as `ALTER TABLE ADD PARTITION` is executed by the upstream job — typically much faster than polling.
