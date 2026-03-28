# Ch 1–2 — Introduction & Core Concepts

## Table of Contents
- [What Oozie Solves](#what-oozie-solves)
- [Three Job Types](#three-job-types)
- [Architecture](#architecture)
- [Application Deployment Model](#application-deployment-model)
- [EL Expression Language](#el-expression-language)
- [Job States Overview](#job-states-overview)
- [Key Versions](#key-versions)

---

## What Oozie Solves

Oozie orchestrates **multi-step Hadoop data pipelines**. Problems it addresses that cron cannot:

- **Data dependencies**: Don't run until upstream data arrives
- **DAG execution**: Fork parallel jobs, join them, branch on conditions
- **Long-running jobs**: Poll YARN jobs over hours/days without blocking
- **Recovery**: Retry, rerun, resume from failure
- **Scale**: Thousands of coordinator actions per day across hundreds of workflows
- **Auditability**: Full history, logs, and SLA tracking

---

## Three Job Types

| Type | Purpose | XML element | Property key |
|------|---------|-------------|--------------|
| **Workflow** | DAG of actions (single execution) | `<workflow-app>` | `oozie.wf.application.path` |
| **Coordinator** | Repeated workflow runs on time/data triggers | `<coordinator-app>` | `oozie.coord.application.path` |
| **Bundle** | Group of coordinators as a pipeline | `<bundle-app>` | `oozie.bundle.application.path` |

Typical relationship: Bundle → 1..N Coordinators → each triggers a Workflow on each run.

---

## Architecture

```
Client (CLI / REST API)
        │
        ▼
Oozie Server (Tomcat)
  ├── Web Services Layer (REST)
  ├── Workflow Engine (DAG state machine)
  ├── Coordinator Engine (action materialization)
  ├── Bundle Engine
  ├── Action Executor Framework (MR, Hive, Spark, ...)
  │       └── Launches Hadoop jobs via YARN
  ├── JPAService (JPA → JDBC → DB)
  └── CallableQueueService (thread pool)
        │
        ├── Relational DB (MySQL/PostgreSQL/Oracle — stores all job state)
        └── HDFS (stores app definitions, JARs, sharelibs)
```

- Oozie is **stateless** with respect to in-flight jobs: all state is in the DB
- HA is achieved via ZooKeeper (leader election + distributed locks) + shared DB
- Oozie never runs Hadoop code itself — it submits jobs to YARN and polls for completion

---

## Application Deployment Model

All Oozie application files live on **HDFS**, not the local filesystem.

```
hdfs:// .../user/joe/my-workflow/
    workflow.xml          ← DAG definition
    config-default.xml    ← optional property defaults
    lib/
        myapp.jar         ← auto-distributed to all actions
        helper.jar
    scripts/
        process.py        ← referenced via <file> in actions
```

Submission uses `job.properties` (local file) pointing to the HDFS path:
```properties
oozie.wf.application.path=hdfs://namenode:8020/user/joe/my-workflow
```

---

## EL Expression Language

Oozie uses **EL (Expression Language)** for parameterization — `${expr}` syntax everywhere in XML.

Sources of variables (highest → lowest priority):
1. Coordinator/bundle-passed configuration
2. `job.properties` (submission properties)
3. `config-default.xml` (in app HDFS dir)
4. `<parameters>` defaults in workflow XML
5. Built-in EL functions

Built-in variable families:
- `wf:*` — workflow job context (see `ch05-workflows.md`)
- `coord:*` — coordinator context (see `ch06-coordinator-time.md`)
- `fs:*` — HDFS filesystem checks
- `hadoop:*` — Hadoop counters and config
- `hcat:*` — HCatalog partition existence

String utilities available everywhere:
```
${concat(str1, str2)}
${trim(str)}
${replaceAll(str, regex, replacement)}
${urlEncode(str)}
${timestamp()}   → current UTC datetime
${toBoolean(str)}
```

---

## Job States Overview

### Workflow job
`PREP → RUNNING → SUCCEEDED`
                `→ SUSPENDED` (manual)
                `→ KILLED` (manual or kill node)
                `→ FAILED` (system error)

### Workflow action
`PREP → PENDING → SUBMITTED → RUNNING → OK | ERROR | KILLED`

### Coordinator job
`PREP → RUNNING → SUCCEEDED | PAUSED | SUSPENDED | KILLED | FAILED`

### Coordinator action
`WAITING → READY → SUBMITTED → RUNNING → SUCCEEDED | KILLED | FAILED | TIMEDOUT | IGNORED`

`TIMEDOUT` = data never arrived within `<timeout>` window
`IGNORED` = manually marked to skip

### Bundle job
`PREP → RUNNING → SUCCEEDED | DONEWITHERROR | PAUSED | SUSPENDED | KILLED | FAILED`

`DONEWITHERROR` = all done but some non-critical coordinators failed
`FAILED` = a `critical="true"` coordinator failed

---

## Key Versions

| Oozie Version | Hadoop Compatibility | Notable Features |
|--------------|---------------------|-----------------|
| 4.x | Hadoop 2.x / YARN | Coordinator cron, SLA v2, HCatalog |
| 5.x | Hadoop 3.x | Hive2 action, improved HA, Spark 2+ |
| 5.2+ | Hadoop 3.2+ | Schema updates, security improvements |

Always check `oozie.version` in `oozie-site.xml` output of `oozie admin -version`.

Workflow schema: `uri:oozie:workflow:0.5` (current; use this for all new workflows)
Coordinator schema: `uri:oozie:coordinator:0.2`
Bundle schema: `uri:oozie:bundle:0.2`
SLA schema: `uri:oozie:sla:0.2`
