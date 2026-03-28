# Ch 8 — Oozie Bundles

## Table of Contents
- [Bundle Concepts](#bundle-concepts)
- [Bundle XML Structure](#bundle-xml-structure)
- [kick-off-time](#kick-off-time)
- [Submission](#submission)
- [Bundle Management (CLI)](#bundle-management-cli)
- [Bundle States](#bundle-states)
- [Gotchas](#gotchas)

---

## Bundle Concepts

A **bundle** packages multiple coordinators into a single logical unit — a data pipeline. Benefits:
- Submit/suspend/resume/kill all coordinators in one command
- Shared parameterization across coordinators
- Single `kick-off-time` for the whole pipeline
- `critical="true"` coordinators mark the bundle as CRITICAL if they fail

Use bundles when you have multiple coordinators that form a dependency chain and need to be managed as a unit.

---

## Bundle XML Structure

```xml
<bundle-app name="daily-pipeline" xmlns="uri:oozie:bundle:0.2">
  <parameters>
    <property>
      <name>START_TIME</name>
      <!-- required; no default -->
    </property>
    <property>
      <name>END_TIME</name>
      <value>2099-01-01T00:00Z</value>
    </property>
    <property>
      <name>nameNode</name>
    </property>
  </parameters>

  <controls>
    <kick-off-time>${START_TIME}</kick-off-time>
  </controls>

  <!-- Ingestion coordinator — critical to the pipeline -->
  <coordinator name="ingestion" critical="true">
    <app-path>${nameNode}/pipelines/ingestion-coord</app-path>
    <configuration>
      <property><name>start</name><value>${START_TIME}</value></property>
      <property><name>end</name><value>${END_TIME}</value></property>
    </configuration>
  </coordinator>

  <!-- Processing depends on ingestion output (via data trigger) -->
  <coordinator name="processing">
    <app-path>${nameNode}/pipelines/processing-coord</app-path>
    <configuration>
      <property><name>start</name><value>${START_TIME}</value></property>
      <property><name>end</name><value>${END_TIME}</value></property>
    </configuration>
  </coordinator>

  <!-- Reporting -->
  <coordinator name="reporting">
    <app-path>${nameNode}/pipelines/reporting-coord</app-path>
    <configuration>
      <property><name>start</name><value>${START_TIME}</value></property>
      <property><name>end</name><value>${END_TIME}</value></property>
    </configuration>
  </coordinator>
</bundle-app>
```

---

## kick-off-time

- `<kick-off-time>` controls when Oozie starts the coordinators inside the bundle
- Default: `NOW` (coordinators start immediately on bundle submission)
- Set to a future time to stage a bundle for a scheduled launch
- The coordinators' own `start`/`end` times are independent of `kick-off-time`
- `kick-off-time` only affects *when coordinators are activated*, not *when they run actions*

---

## Submission

`bundle.properties`:
```properties
nameNode=hdfs://namenode:8020
jobTracker=resourcemanager:8032
oozie.bundle.application.path=${nameNode}/user/${user.name}/daily-pipeline
START_TIME=2024-01-01T00:00Z
END_TIME=2025-01-01T00:00Z
oozie.use.system.libpath=true
```

```bash
# Submit and run
oozie job -oozie http://oozie:11000/oozie -config bundle.properties -run

# Dry run
oozie job -oozie http://oozie:11000/oozie -config bundle.properties -dryrun
```

---

## Bundle Management (CLI)

```bash
# List bundles
oozie jobs -jobtype bundle

# Status
oozie job -info <bundle-id>

# Suspend entire pipeline
oozie job -suspend <bundle-id>

# Resume
oozie job -resume <bundle-id>

# Kill
oozie job -kill <bundle-id>

# Rerun specific coordinator within bundle
oozie job -rerun <bundle-id> -coordinator ingestion
oozie job -rerun <bundle-id> -coordinator ingestion -nocleanup -refresh

# Bulk status across bundle
oozie jobs -bulk 'bundle=daily-pipeline;actionstatus=FAILED' -verbose

# Change kick-off-time
oozie job -change <bundle-id> -value kickofftime=2024-02-01T00:00Z

# Pause bundle
oozie job -change <bundle-id> -value pausetime=2024-06-01T00:00Z
```

**`-nocleanup`**: Skip deletion of output dirs before rerun
**`-refresh`**: Re-read the coordinator/workflow XML from HDFS (picks up definition changes)

---

## Bundle States

Bundle job: `PREP → RUNNING → PAUSED | SUSPENDED | SUCCEEDED | DONEWITHERROR | FAILED | KILLED`

`DONEWITHERROR` = all coordinators ended, but at least one failed (and none were `critical="true"`)
`FAILED` = a `critical="true"` coordinator failed

---

## Gotchas

1. **`critical="true"` escalates failures**: If a coordinator marked critical enters FAILED state, the entire bundle is marked FAILED. Non-critical coordinator failures result in `DONEWITHERROR` bundle state only.

2. **Coordinators run independently**: The bundle does not enforce execution ordering between coordinators. Use data triggers (datasets + `<input-events>`) in downstream coordinators to create actual data dependencies.

3. **Schema version matters**: `xmlns="uri:oozie:bundle:0.2"` enables formal `<parameters>` block validation. Schema 0.1 does not support `<parameters>`.

4. **`kick-off-time` cannot be changed once running**: Set it correctly before submission. After a bundle is running, `pausetime` and `endtime` can be changed but `kick-off-time` cannot.
