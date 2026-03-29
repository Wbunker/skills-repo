# Oozie Coordinators
## Chapter 6: Oozie Coordinator

---

## What Is a Coordinator?

A **coordinator** is the scheduling layer above a workflow. It defines when to run a workflow — either on a time schedule, when data arrives, or both. Each scheduled execution is called a **coordinator action**, and each coordinator action runs one instance of the workflow.

```
Coordinator (scheduler)
    │
    │ fires at time T (and optionally when data is ready)
    ▼
Coordinator Action (one execution)
    │
    │ submits
    ▼
Workflow Job (actual work)
```

---

## Coordinator XML Structure

```xml
<coordinator-app name="daily-pipeline"
                 frequency="${coord:days(1)}"
                 start="2024-01-01T00:00Z"
                 end="2025-01-01T00:00Z"
                 timezone="UTC"
                 xmlns="uri:oozie:coordinator:0.4">

  <action>
    <workflow>
      <app-path>${nameNode}/user/me/my-workflow</app-path>
      <configuration>
        <property>
          <name>inputPath</name>
          <value>/data/input/${coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')}</value>
        </property>
        <property>
          <name>outputPath</name>
          <value>/data/output/${coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')}</value>
        </property>
      </configuration>
    </workflow>
  </action>

</coordinator-app>
```

### Top-Level Attributes

| Attribute | Required | Description |
|-----------|---------|-------------|
| `name` | Yes | Display name for the coordinator |
| `frequency` | Yes | How often to fire (minutes, or cron expression) |
| `start` | Yes | First nominal time (ISO 8601, UTC: `2024-01-01T00:00Z`) |
| `end` | Yes | Last nominal time (no more firings after this) |
| `timezone` | Yes | Timezone for time calculations (e.g., `UTC`, `America/New_York`) |

---

## Frequency and Time-Based Triggers

### EL-Based Frequency

Use coordinator EL time functions for common frequencies:

| Expression | Fires Every |
|-----------|-------------|
| `${coord:minutes(15)}` | 15 minutes |
| `${coord:hours(1)}` | 1 hour |
| `${coord:hours(6)}` | 6 hours |
| `${coord:days(1)}` | 1 day |
| `${coord:weeks(1)}` | 1 week |
| `${coord:months(1)}` | 1 calendar month |

The frequency value is in **minutes** when given as a plain number. EL functions return minute values.

### Cron-Based Frequency (Oozie 4.x+)

Use a quartz-style cron expression for more complex schedules:

```xml
frequency="0 8 * * *"    <!-- daily at 8:00 AM -->
frequency="0 6,18 * * *" <!-- 6 AM and 6 PM daily -->
frequency="0 0 1 * *"    <!-- 1st of every month at midnight -->
frequency="0/30 * * * *" <!-- every 30 minutes -->
```

Cron format: `<minute> <hour> <day-of-month> <month> <day-of-week>`

### Nominal Time

The **nominal time** is the scheduled trigger time — the time the coordinator action was supposed to fire. It is used to construct input/output paths and is stable regardless of when the action actually runs.

```xml
<!-- Use nominal time to partition paths by date -->
<value>/data/input/${coord:formatTime(coord:nominalTime(), 'yyyy/MM/dd')}</value>
<!-- e.g., /data/input/2024/03/15 -->
```

Key EL functions for nominal time:

| Function | Returns |
|----------|---------|
| `${coord:nominalTime()}` | Nominal time as a date-time string |
| `${coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')}` | Formatted date string |
| `${coord:dateOffset(coord:nominalTime(), -1, 'DAY')}` | Yesterday's nominal time |
| `${coord:actualTime()}` | Actual execution time |

---

## Coordinator Action Lifecycle

Each coordinator action goes through these states:

| State | Description |
|-------|-------------|
| `WAITING` | Waiting for time or data conditions to be met |
| `READY` | All conditions met; ready to submit workflow |
| `SUBMITTED` | Workflow job submitted to Oozie |
| `RUNNING` | Workflow is executing |
| `SUCCEEDED` | Workflow completed successfully |
| `FAILED` | Workflow failed |
| `KILLED` | Operator killed the action |
| `TIMEDOUT` | Data conditions were never met within timeout window |
| `SKIPPED` | Action was skipped (e.g., due to throttle limit) |

### Throttle

Limit how many coordinator actions can run simultaneously:

```xml
<coordinator-app ... xmlns="uri:oozie:coordinator:0.4">
  <controls>
    <timeout>120</timeout>          <!-- minutes to wait for data before TIMEDOUT -->
    <concurrency>2</concurrency>    <!-- max simultaneous running actions -->
    <execution>FIFO</execution>     <!-- FIFO, LIFO, or LAST_ONLY -->
    <throttle>4</throttle>          <!-- max WAITING actions (older ones are TIMEDOUT) -->
  </controls>
  ...
</coordinator-app>
```

`<execution>LAST_ONLY</execution>` — if multiple actions are waiting, only run the most recent one. Useful for near-realtime coordinators that should stay current.

---

## Submitting and Managing Coordinators

### Submit a Coordinator Job

```bash
# job.properties for a coordinator
oozie.coord.application.path=${nameNode}/user/me/my-coordinator

oozie job -oozie http://oozie:11000/oozie \
          -config job.properties \
          -run
```

### Common CLI Operations

```bash
# Check coordinator job status
oozie job -oozie http://oozie:11000/oozie -info <coord-job-id>

# Check a specific coordinator action
oozie job -oozie http://oozie:11000/oozie -info <coord-job-id>@<action-number>

# Rerun a failed coordinator action
oozie job -oozie http://oozie:11000/oozie \
          -rerun <coord-job-id> \
          -action 3-5 \
          -nocleanup -refresh

# Kill a coordinator job
oozie job -oozie http://oozie:11000/oozie -kill <coord-job-id>

# Suspend / resume
oozie job -oozie http://oozie:11000/oozie -suspend <coord-job-id>
oozie job -oozie http://oozie:11000/oozie -resume <coord-job-id>

# Change end time (extend or shorten the coordinator)
oozie job -oozie http://oozie:11000/oozie \
          -change <coord-job-id> \
          -value endtime=2025-06-01T00:00Z
```

### Rerun Options

| Option | Meaning |
|--------|---------|
| `-action 3-5` | Rerun actions 3, 4, and 5 |
| `-date 2024-01-01T00:00Z::2024-01-03T00:00Z` | Rerun actions in date range |
| `-nocleanup` | Don't delete output before rerunning |
| `-refresh` | Use latest workflow definition from HDFS |

---

## Coordinator Configuration Passed to Workflow

The `<configuration>` block inside the coordinator's `<action>` passes parameters to the triggered workflow. Use this to inject the nominal time, input/output paths, and any other runtime values:

```xml
<action>
  <workflow>
    <app-path>${wfAppPath}</app-path>
    <configuration>
      <property><name>inputPath</name>
        <value>/data/${coord:formatTime(coord:nominalTime(),'yyyy/MM/dd')}/input</value>
      </property>
      <property><name>outputPath</name>
        <value>/data/${coord:formatTime(coord:nominalTime(),'yyyy/MM/dd')}/output</value>
      </property>
      <property><name>nominalDate</name>
        <value>${coord:formatTime(coord:nominalTime(),'yyyy-MM-dd')}</value>
      </property>
    </configuration>
  </workflow>
</action>
```
