# Oozie Concepts
## Chapters 1–2: Introduction, Concepts, Architecture

---

## What Is Oozie?

Apache Oozie is a **server-based workflow scheduler** for Hadoop. It solves the recurring problem of running multi-step Hadoop data pipelines reliably: sequencing jobs, handling failures, triggering on time or data, and managing dependencies between pipelines.

Oozie is not a resource manager (that's YARN) and not a job launcher (that's Hadoop). Oozie is the **orchestration layer** above them.

### Why Oozie Exists

Running a data pipeline without a scheduler means:
- Manual job sequencing via shell scripts with no failure recovery
- No standard way to trigger on data availability
- No dependency tracking between pipelines
- No centralized monitoring of pipeline state

Oozie provides all of these.

---

## The Three Constructs

### Workflow

A **workflow** is a Directed Acyclic Graph (DAG) of actions. It defines what to run and in what order, with conditional branching, parallel execution, and error handling.

- Defined in `workflow.xml`
- Runs once when submitted (or once per coordinator trigger)
- Contains action nodes (Hadoop jobs) and control nodes (fork, join, decision)

### Coordinator

A **coordinator** triggers workflow executions based on time and/or data availability. It is the scheduling layer above a workflow.

- Defined in `coordinator.xml`
- Fires according to a frequency (e.g., every hour) and/or when input datasets are ready
- Each firing creates a **coordinator action**, which runs a workflow

### Bundle

A **bundle** groups multiple coordinators into a single unit. It is the pipeline management layer — for when several coordinators together form a logical data pipeline.

- Defined in `bundle.xml`
- Allows start/pause/resume/kill of all grouped coordinators together
- Supports reprocessing a date range across all coordinators in the bundle

### Hierarchy Summary

```
Bundle
  └── Coordinator A  ──▶  Workflow (runs when triggered)
  └── Coordinator B  ──▶  Workflow (may depend on Coordinator A's output)
```

---

## Parameters, Variables, and EL Functions

### Job Properties

Runtime parameters are passed in a `job.properties` file at submission time:

```properties
nameNode=hdfs://namenode:8020
jobTracker=resourcemanager:8032
queueName=default
inputPath=/user/data/input
outputPath=/user/data/output
oozie.wf.application.path=${nameNode}/user/me/my-workflow
```

These are referenced in XML using EL: `${inputPath}`.

### Expression Language (EL)

Oozie supports a JSP-like EL for dynamic values in XML definitions.

**Built-in variables:**

| Variable | Meaning |
|----------|---------|
| `${nameNode}` | HDFS NameNode URI |
| `${jobTracker}` | YARN ResourceManager address |
| `${wf:id()}` | Current workflow job ID |
| `${wf:name()}` | Workflow application name |
| `${wf:user()}` | User who submitted the job |
| `${wf:lastErrorNode()}` | Name of the last failed action |
| `${wf:errorCode("action")}` | Error code of a named action |
| `${wf:actionData("action")}` | Output properties of a named action |

**Coordinator EL functions:**

| Function | Meaning |
|----------|---------|
| `${coord:minutes(n)}` | n minutes |
| `${coord:hours(n)}` | n × 60 minutes |
| `${coord:days(n)}` | n × 1440 minutes |
| `${coord:months(n)}` | n calendar months |
| `${coord:current(n)}` | Dataset instance at offset n from nominal time |
| `${coord:dataIn("name")}` | Resolved HDFS paths for input dataset |
| `${coord:dataOut("name")}` | Resolved HDFS path for output dataset |
| `${coord:nominalTime()}` | Scheduled trigger time |
| `${coord:actualTime()}` | Actual execution time |

**HDFS EL functions:**

| Function | Returns |
|----------|---------|
| `${fs:exists("/path")}` | true/false |
| `${fs:isDir("/path")}` | true/false |
| `${fs:fileSize("/path")}` | file size in bytes |
| `${fs:blockSize("/path")}` | HDFS block size |

### Parameter Passing Chain

```
job.properties
    │ defines variables
    ▼
coordinator.xml
    │ <configuration> passes params to workflow
    ▼
workflow.xml
    │ uses ${variable} in action definitions
    ▼
Hadoop job execution
```

---

## Application Deployment Model

All Oozie application files must be present in HDFS before submission. The Oozie server reads from HDFS — never from the submitting client's local filesystem.

### Standard Directory Layout

```
/user/<username>/<app-name>/
    workflow.xml           ← workflow definition
    coordinator.xml        ← coordinator definition (if using coordinator)
    bundle.xml             ← bundle definition (if using bundle)
    job.properties         ← submission parameters (kept locally too)
    lib/
        my-udf.jar         ← JARs automatically added to job classpath
        helper-lib.jar
    scripts/
        hive-query.hql     ← Hive scripts
        pig-script.pig      ← Pig scripts
```

### Deployment Steps

```bash
# 1. Upload application to HDFS
hdfs dfs -put -f my-workflow/ /user/me/my-workflow/

# 2. Submit to Oozie
oozie job -oozie http://oozie-server:11000/oozie \
          -config job.properties \
          -run

# 3. Check status
oozie job -oozie http://oozie-server:11000/oozie \
          -info <job-id>
```

---

## Oozie Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Oozie Server                         │
│                                                         │
│  ┌───────────────┐   ┌─────────────────────────────┐   │
│  │  Web Services │   │     Engine Layer             │   │
│  │  (REST API)   │   │  WorkflowEngine              │   │
│  │  (Web UI)     │   │  CoordinatorEngine           │   │
│  └───────────────┘   │  BundleEngine                │   │
│                      └──────────────┬────────────────┘   │
│  ┌───────────────┐                  │                    │
│  │  Oozie CLI    │   ┌──────────────▼────────────────┐   │
│  │  Java Client  │   │  Action Executor Framework    │   │
│  └───────────────┘   │  (per action type plugin)     │   │
│                      └──────────────┬────────────────┘   │
│  ┌───────────────┐                  │                    │
│  │  Oozie DB     │◀─────────────────┘                   │
│  │ (MySQL/Postgres│                                      │
│  │  /Derby)      │                                      │
│  └───────────────┘                                      │
└─────────────────────────────────────────────────────────┘
        │                           │
        ▼                           ▼
   HDFS (app files)         Hadoop/YARN (job execution)
```

### Key Architectural Points

- **Oozie does not execute Hadoop jobs directly** — it submits them to YARN
- **Action execution is asynchronous** — Oozie submits an action, then polls or waits for a callback
- **State is stored in a relational DB** — MySQL, PostgreSQL, or Oracle (Derby for dev only)
- **Oozie server is stateless across restarts** — all state is in the DB; the server can restart without losing jobs
- **Launcher job** — for most action types, Oozie submits a lightweight "launcher" MapReduce job to the cluster, which then runs the actual action

### Synchronous vs. Asynchronous Actions

| Execution Model | Examples | Behavior |
|----------------|---------|----------|
| Asynchronous (callback) | MapReduce, Hive, Pig, Spark | Oozie submits launcher, Hadoop calls back when done |
| Synchronous | FS, Email, HTTP | Oozie executes directly from the server process |
| Sub-workflow | Sub-Workflow | Oozie submits a child workflow job and waits |
