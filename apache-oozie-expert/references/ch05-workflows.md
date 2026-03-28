# Ch 5 — Workflow Applications

## Table of Contents
- [Workflow Structure](#workflow-structure)
- [Control Nodes](#control-nodes)
- [Parameterization](#parameterization)
- [HDFS Application Layout](#hdfs-application-layout)
- [Job Submission](#job-submission)
- [Workflow EL Functions](#workflow-el-functions)
- [Gotchas](#gotchas)

---

## Workflow Structure

```xml
<workflow-app name="my-workflow" xmlns="uri:oozie:workflow:0.5">
  <parameters>
    <property>
      <name>inputDir</name>
      <!-- no <value> = required; error if not provided -->
    </property>
    <property>
      <name>outputDir</name>
      <value>/tmp/default-output</value>
    </property>
  </parameters>
  <global>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <configuration>
      <property><name>mapred.job.queue.name</name><value>default</value></property>
    </configuration>
  </global>

  <start to="first-action"/>

  <action name="first-action">
    ...
    <ok to="end"/>
    <error to="fail"/>
  </action>

  <kill name="fail">
    <message>Workflow failed at [${wf:lastErrorNode()}]: ${wf:errorMessage(wf:lastErrorNode())}</message>
  </kill>
  <end name="end"/>
</workflow-app>
```

`<global>` sets defaults for all actions; per-action config overrides globals.

---

## Control Nodes

### Fork / Join

```xml
<fork name="fork-1">
  <path start="action-a"/>
  <path start="action-b"/>
  <path start="action-c"/>
</fork>

<action name="action-a">...<ok to="join-1"/><error to="fail"/></action>
<action name="action-b">...<ok to="join-1"/><error to="fail"/></action>
<action name="action-c">...<ok to="join-1"/><error to="fail"/></action>

<join name="join-1" to="next-action"/>
```

- Every fork path **must** reach the matching join — skipping a join hangs the workflow indefinitely
- Nested forks are supported; each must have its own join

### Decision

```xml
<decision name="check-size">
  <switch>
    <case to="big-job">${fs:fileSize(outputPath) gt 1000000}</case>
    <case to="small-job">${fs:fileSize(outputPath) le 1000000 and fs:exists(outputPath)}</case>
    <default to="fail"/>
  </switch>
</decision>
```

- Evaluates cases top-to-bottom; first `true` wins
- `<default>` is mandatory

### Kill

```xml
<kill name="fail">
  <message>Pipeline failed: [${wf:lastErrorNode()}] ${wf:errorMessage(wf:lastErrorNode())}</message>
</kill>
```

Terminal node — workflow ends in KILLED state.

---

## Parameterization

### Formal parameters block (schema 0.4+)

```xml
<parameters>
  <property><name>inputDir</name></property>          <!-- required -->
  <property><name>outputDir</name><value>/tmp</value></property>  <!-- optional with default -->
</parameters>
```

Oozie validates all required params at submission time — catches misconfiguration early.

### config-default.xml

Place `config-default.xml` in the workflow app HDFS directory to provide defaults that apply when not overridden by `job.properties`:

```xml
<configuration>
  <property><name>outputDir</name><value>/data/output</value></property>
  <property><name>mapred.job.queue.name</name><value>default</value></property>
</configuration>
```

Priority (highest to lowest): `job.properties` > `config-default.xml` > `<parameters>` defaults

### job.properties

```properties
nameNode=hdfs://namenode:8020
jobTracker=resourcemanager:8032
oozie.wf.application.path=${nameNode}/user/${user.name}/my-workflow
inputDir=/data/input/2024-01-01
outputDir=/data/output/2024-01-01
oozie.use.system.libpath=true
oozie.libpath=${nameNode}/user/oozie/share/lib
```

---

## HDFS Application Layout

```
/user/joe/my-workflow/
├── workflow.xml           (required)
├── config-default.xml     (optional defaults)
└── lib/
    ├── myapp.jar
    └── helper.jar
```

All JARs in `lib/` are automatically added to the distributed cache for every action.

For action-specific JARs not needed by other actions, use `<file>` or `<archive>` within the action instead of `lib/` to avoid unnecessarily loading large JARs.

---

## Job Submission

```bash
# Submit and run immediately
oozie job -oozie http://oozie:11000/oozie -config job.properties -run

# Submit only (stays in PREP state)
oozie job -oozie http://oozie:11000/oozie -config job.properties -submit

# Start a submitted job
oozie job -oozie http://oozie:11000/oozie -start <wf-job-id>

# Dry run (validate + show parameter resolution)
oozie job -oozie http://oozie:11000/oozie -config job.properties -dryrun

# Validate XML locally
oozie validate workflow.xml

# Rerun (skip specific actions)
oozie job -oozie http://oozie:11000/oozie -config job.properties -rerun <wf-job-id>
```

Workflow job states: `PREP → RUNNING → SUCCEEDED | SUSPENDED | KILLED | FAILED`

---

## Workflow EL Functions

```
wf:id()                          — current workflow job ID
wf:name()                        — workflow app name
wf:appPath()                     — HDFS app path
wf:conf(String name)             — property value by name
wf:user()                        — submitting user
wf:group()                       — submitting group
wf:lastErrorNode()               — name of last failed action node
wf:errorCode(String node)        — error code of named node
wf:errorMessage(String node)     — error message of named node
wf:run()                         — run number (increments on rerun)
wf:actionData(String node)['k'] — captured output from action (Map lookup)
wf:actionExternalId(String node) — YARN app ID of action
wf:actionTrackerUri(String node) — ResourceManager tracking URL
wf:actionExternalStatus(String node) — external job status
wf:callback(String stateVar)     — callback URL for custom async actions
wf:transition(String node)       — transition taken by named node

hadoop:counters(String node)     — Hadoop job counters as JSON string
hadoop:conf(String prop)         — Hadoop cluster config value

fs:exists(String path)           — boolean: HDFS path exists
fs:isDir(String path)            — boolean: is a directory
fs:fileSize(String path)         — file size in bytes
fs:blockSize(String path)        — HDFS block size in bytes
fs:dirSize(String path)          — total recursive size of directory

hcat:exists(String uri)          — boolean: HCatalog partition exists

concat(String s1, String s2)     — string concatenation
replaceAll(String src, String regex, String rep)
appendAll(String src, String toAppend, String delim)
trim(String s)
urlEncode(String s)
timestamp()                      — current UTC timestamp (yyyy-MM-ddTHH:mm:ss.SSSZ)
toBoolean(String val)
```

---

## Gotchas

1. **Fork/join deadlock**: Every fork path must arrive at the same join. A path that bypasses the join causes the workflow to hang with no error message.

2. **Formal parameters enforce required values**: Using `<parameters>` block in schema 0.4+ causes submission-time validation — good practice to catch missing config early.

3. **`capture-output` must be Java Properties format**: `key=value` per line. Multi-line values or binary output will break parsing silently.

4. **`<global>` reduces duplication**: Set `job-tracker`, `name-node`, and common properties once in `<global>` instead of repeating in every action.

5. **`wf:run()` for idempotency**: Use `${wf:run()}` in output paths to produce unique paths on rerun — prevents overwriting output from the original run.
