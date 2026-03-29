# Workflow Applications
## Chapter 5: Workflow Applications

---

## Workflow XML Structure

A workflow is defined in `workflow.xml`. It must have exactly one `<start>`, one or more `<action>` nodes, and at least one `<end>` and one `<kill>` node.

```xml
<workflow-app name="my-workflow" xmlns="uri:oozie:workflow:0.5">

  <start to="first-action"/>

  <action name="first-action">
    <map-reduce>
      <!-- action config -->
    </map-reduce>
    <ok to="second-action"/>
    <error to="fail"/>
  </action>

  <action name="second-action">
    <hive xmlns="uri:oozie:hive-action:0.5">
      <!-- action config -->
    </hive>
    <ok to="end"/>
    <error to="fail"/>
  </action>

  <kill name="fail">
    <message>Workflow failed, error: ${wf:errorMessage(wf:lastErrorNode())}</message>
  </kill>

  <end name="end"/>

</workflow-app>
```

---

## Control Nodes

### start

The entry point. Exactly one per workflow. `to` attribute names the first action or control node to execute.

```xml
<start to="first-step"/>
```

### end

Marks successful completion. Exactly one per workflow (typically; you can have multiple `<end>` nodes if different paths succeed).

```xml
<end name="end"/>
```

### kill

Terminates the workflow in a failed state. The `<message>` is logged and visible in the Oozie web UI. Best practice: include `${wf:errorMessage(wf:lastErrorNode())}`.

```xml
<kill name="fail">
  <message>Job failed at node [${wf:lastErrorNode()}]: ${wf:errorMessage(wf:lastErrorNode())}</message>
</kill>
```

### fork and join

`<fork>` splits execution into parallel paths. Each path runs independently. `<join>` waits for all forked paths to complete before proceeding.

```xml
<fork name="parallel-steps">
  <path start="step-a"/>
  <path start="step-b"/>
  <path start="step-c"/>
</fork>

<action name="step-a"> ... <ok to="join-point"/> ... </action>
<action name="step-b"> ... <ok to="join-point"/> ... </action>
<action name="step-c"> ... <ok to="join-point"/> ... </action>

<join name="join-point" to="next-step"/>
```

Rules:
- Every fork must have exactly one matching join
- All paths from a fork must converge at the same join node
- Forks and joins can be nested

### decision

Routes execution to one of N paths based on EL predicate evaluation. Uses JSP switch-like syntax with `<case>` and `<default>`.

```xml
<decision name="check-size">
  <switch>
    <case to="large-job">${fs:fileSize(inputPath) gt 1073741824}</case>
    <case to="medium-job">${fs:fileSize(inputPath) gt 104857600}</case>
    <default to="small-job"/>
  </switch>
</decision>
```

Only the first matching `<case>` is taken. `<default>` is required.

---

## Action Nodes

Every action node has three required elements:

```xml
<action name="my-step">
  <action-type-config>
    ...
  </action-type-config>
  <ok to="next-step"/>         <!-- where to go on success -->
  <error to="fail-handler"/>   <!-- where to go on failure -->
</action>
```

### Action Lifecycle

```
PREP → RUNNING → OK     (success path → transitions to ok-to)
              → ERROR   (failure path → transitions to error-to)
              → KILLED  (operator kills workflow)
```

Within an action:
1. Oozie submits the action (often via a launcher job on YARN)
2. Action executes on the Hadoop cluster
3. Hadoop calls back Oozie with success or failure (callback URL mechanism)
4. Oozie transitions the workflow to the next node

### Retry Configuration

Add retry attributes to any action node to automatically retry on transient failures:

```xml
<action name="my-step" retry-max="3" retry-interval="2">
  <map-reduce>
    ...
  </map-reduce>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

- `retry-max`: maximum number of retry attempts (default: 0)
- `retry-interval`: minutes between retries (default: 10)

---

## Workflow Lifecycle States

| State | Description |
|-------|-------------|
| `PREP` | Submitted but not yet running |
| `RUNNING` | Currently executing |
| `SUSPENDED` | Paused by operator |
| `SUCCEEDED` | Reached `<end>` node |
| `KILLED` | Operator killed it |
| `FAILED` | Hit `<kill>` node or unrecoverable error |

State transitions:

```
PREP → RUNNING → SUCCEEDED
              → FAILED
              → KILLED
RUNNING → SUSPENDED → RUNNING  (operator suspend/resume)
```

---

## Workflow Configuration Block

Every workflow can receive configuration parameters via `<configuration>`:

```xml
<workflow-app name="my-workflow" xmlns="uri:oozie:workflow:0.5">

  <global>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <configuration>
      <property>
        <name>mapreduce.job.queuename</name>
        <value>${queueName}</value>
      </property>
    </configuration>
  </global>

  ...
</workflow-app>
```

The `<global>` block sets defaults for all actions in the workflow. Individual actions can override these.

---

## Credentials (Secure Cluster)

On Kerberos-secured clusters, actions that access HCatalog, HBase, or other secured services need credentials:

```xml
<credentials>
  <credential name="hive-creds" type="hcat">
    <property>
      <name>hcat.metastore.uri</name>
      <value>${hcatUri}</value>
    </property>
    <property>
      <name>hcat.metastore.principal</name>
      <value>${hcatPrincipal}</value>
    </property>
  </credential>
</credentials>

<action name="hive-step" cred="hive-creds">
  <hive xmlns="uri:oozie:hive-action:0.5">
    ...
  </hive>
  ...
</action>
```

---

## Common Workflow Patterns

### Sequential Pipeline

```xml
<start to="ingest"/>
<action name="ingest"> ... <ok to="transform"/> ... </action>
<action name="transform"> ... <ok to="load"/> ... </action>
<action name="load"> ... <ok to="end"/> ... </action>
<end name="end"/>
```

### Parallel then Join

```xml
<start to="fork-1"/>
<fork name="fork-1">
  <path start="job-a"/>
  <path start="job-b"/>
</fork>
<action name="job-a"> ... <ok to="join-1"/> ... </action>
<action name="job-b"> ... <ok to="join-1"/> ... </action>
<join name="join-1" to="aggregate"/>
<action name="aggregate"> ... <ok to="end"/> ... </action>
<end name="end"/>
```

### Conditional Branch with Error Notification

```xml
<action name="process"> ...
  <ok to="check-output"/>
  <error to="notify-fail"/>
</action>

<decision name="check-output">
  <switch>
    <case to="end">${fs:exists(outputPath)}</case>
    <default to="notify-fail"/>
  </switch>
</decision>

<action name="notify-fail">
  <email xmlns="uri:oozie:email-action:0.1">
    <to>${alertEmail}</to>
    <subject>Workflow Failed</subject>
    <body>Failed at: ${wf:lastErrorNode()}</body>
  </email>
  <ok to="fail"/>
  <error to="fail"/>
</action>

<kill name="fail">
  <message>Pipeline failed: ${wf:errorMessage(wf:lastErrorNode())}</message>
</kill>
```
