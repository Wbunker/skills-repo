# Ch 6 — Coordinator: Time-Based Scheduling

## Table of Contents
- [Coordinator Concepts](#coordinator-concepts)
- [Coordinator XML Structure](#coordinator-xml-structure)
- [Frequency: EL Functions](#frequency-el-functions)
- [Frequency: Cron Syntax](#frequency-cron-syntax)
- [Controls](#controls)
- [Coordinator EL Functions](#coordinator-el-functions)
- [Submission](#submission)
- [Job States](#job-states)
- [Gotchas](#gotchas)

---

## Coordinator Concepts

A coordinator materializes **actions** (workflow runs) based on **time triggers** and/or **data availability**. Each materialized action is a separate workflow run with its own context.

- **Materialization time** = when Oozie schedules an action (based on `frequency` + `start`)
- **Nominal time** = the scheduled time of an action (used in `${coord:nominalTime()}`)
- **Actual time** = real wall-clock time when the action runs

---

## Coordinator XML Structure

```xml
<coordinator-app name="daily-etl"
                 frequency="${coord:days(1)}"
                 start="2024-01-01T00:00Z"
                 end="2025-01-01T00:00Z"
                 timezone="America/New_York"
                 xmlns="uri:oozie:coordinator:0.2">
  <parameters>
    <property><name>workflowAppPath</name></property>
  </parameters>
  <controls>
    <timeout>60</timeout>
    <concurrency>3</concurrency>
    <execution>FIFO</execution>
    <throttle>12</throttle>
  </controls>
  <action>
    <workflow>
      <app-path>${workflowAppPath}</app-path>
      <configuration>
        <property>
          <name>nominalTime</name>
          <value>${coord:nominalTime()}</value>
        </property>
        <property>
          <name>inputDir</name>
          <value>/data/input/${coord:formatTime(coord:nominalTime(), 'yyyy/MM/dd')}</value>
        </property>
        <property>
          <name>outputDir</name>
          <value>/data/output/${coord:formatTime(coord:nominalTime(), 'yyyy/MM/dd')}</value>
        </property>
      </configuration>
    </workflow>
  </action>
</coordinator-app>
```

---

## Frequency: EL Functions

All EL frequency values are in **minutes**.

| Function | Meaning | Notes |
|----------|---------|-------|
| `${coord:minutes(n)}` | n minutes | Exact |
| `${coord:hours(n)}` | n hours | = n×60 minutes |
| `${coord:days(n)}` | n days | DST-aware (23 or 25 hrs possible) |
| `${coord:months(n)}` | n months | DST-aware, calendar-based |
| `${coord:endOfDays(n)}` | Same as `days(n)` | Shifts first action to next day boundary |
| `${coord:endOfMonths(n)}` | Same as `months(n)` | Shifts first action to next month boundary |

`days()` and `months()` are DST-aware — the actual minute count for a given day may be 1380, 1440, or 1500 minutes near DST transitions. Always use `days(1)` instead of `minutes(1440)` for daily jobs to avoid DST drift.

---

## Frequency: Cron Syntax

Use a 5-field cron expression (no seconds) as the `frequency` attribute directly:

```xml
<coordinator-app name="hourly-job" frequency="0 * * * *" ...>
```

| Expression | Meaning |
|-----------|---------|
| `"0 * * * *"` | Every hour at :00 |
| `"0 8 * * 1-5"` | 8am Mon–Fri |
| `"0/20 9-17 * * 2-5"` | Every 20min, 9am–5pm Tue–Fri |
| `"0 0 1 * *"` | Midnight on 1st of each month |
| `"0 10 * * *"` | Daily at 10am |

**Important:** Cron expressions are evaluated in **Oozie server timezone** (default UTC). For a job at 10am Tokyo time (UTC+9): use `"0 1 * * *"` not `"0 10 * * *"`.

---

## Controls

| Element | Default | Meaning |
|---------|---------|---------|
| `<timeout>` | `-1` | Minutes to wait for input conditions. `-1` = wait forever. `0` = fail immediately if not ready. |
| `<concurrency>` | `1` | Max simultaneously running workflow actions |
| `<execution>` | `FIFO` | Action ordering on catch-up/recovery |
| `<throttle>` | `12` | Max actions in WAITING state at once |

**Execution values:**
- `FIFO` — oldest first (default, safest for historical reprocessing)
- `LIFO` — newest first
- `LAST_ONLY` — skips to the most recent action on catch-up; all intermediate missed actions are IGNORED. Use when only the latest data matters.
- `NONE` — no ordering guarantee

---

## Coordinator EL Functions

```
coord:nominalTime()              — scheduled materialization time (UTC, ISO-8601)
coord:actualTime()               — real wall-clock execution time
coord:formatTime(time, pattern)  — format a time; e.g. coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')
coord:epochTime(time, millis)    — epoch seconds or milliseconds
coord:dateOffset(time, n, unit)  — offset time by n units ('HOUR','DAY','MONTH','YEAR')
coord:dateTzOffset(time, tz)     — convert time to a different timezone
coord:tzOffset()                 — timezone offset of coordinator in minutes

coord:actionId()                 — current coordinator action ID
coord:name()                     — coordinator application name
coord:conf(String prop)          — job property value

coord:user()                     — submitting user
```

Use `coord:formatTime` to build date-partitioned HDFS paths:
```xml
<value>/data/${coord:formatTime(coord:nominalTime(), 'yyyy')}/${coord:formatTime(coord:nominalTime(), 'MM')}/${coord:formatTime(coord:nominalTime(), 'dd')}</value>
```

---

## Submission

`coord.properties`:
```properties
nameNode=hdfs://namenode:8020
jobTracker=resourcemanager:8032
oozie.coord.application.path=${nameNode}/user/${user.name}/daily-etl-coord
workflowAppPath=${nameNode}/user/${user.name}/daily-etl-wf
oozie.use.system.libpath=true
```

```bash
# Submit + start
oozie job -oozie http://oozie:11000/oozie -config coord.properties -run

# Dry run (shows which actions would be materialized)
oozie job -oozie http://oozie:11000/oozie -config coord.properties -dryrun
```

---

## Job States

Coordinator job: `PREP → RUNNING → PAUSED | SUSPENDED | SUCCEEDED | KILLED | FAILED`

Coordinator action (individual run): `WAITING → READY → SUBMITTED → RUNNING → SUCCEEDED | KILLED | FAILED | TIMEDOUT | IGNORED`

---

## Gotchas

1. **Timezone format**: Use `America/Los_Angeles`, never `PST` or `PDT`. Abbreviations silently ignore DST, causing actions to materialize at wrong times.

2. **Database must be UTC**: If the DB timezone is not UTC, DST transitions cause action times to shift by 1 hour.

3. **Zero-action rejection**: If `start`, `end`, and `frequency` produce no actions, Oozie rejects the job at submission with `InvalidCoordinatorAttributeException`.

4. **`LAST_ONLY` is irreversible on missed actions**: Skipped actions are marked IGNORED and cannot be re-materialized automatically. Use only when historical data does not matter.

5. **Change coordinator properties at runtime**:
```bash
oozie job -change <coord-id> -value endtime=2025-06-30T00:00Z
oozie job -change <coord-id> -value concurrency=5
oozie job -change <coord-id> -value pausetime=2024-07-01T00:00Z
oozie job -change <coord-id> -value status=RUNNING    # clear pause
```
