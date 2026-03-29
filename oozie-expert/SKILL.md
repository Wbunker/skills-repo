---
name: oozie-expert
description: Apache Oozie expertise covering workflow scheduling, coordinators, bundles, action types (MapReduce, Hive, Pig, Spark, Sqoop, Shell, Java, FS), data triggers, time-based triggers, deployment, security (Kerberos), high availability, REST API, CLI, monitoring, and tuning. Use when designing Oozie workflows, writing coordinator XML, managing data pipelines, debugging job failures, configuring Oozie on a Hadoop cluster, or building bundle-based data pipelines. Based on "Apache Oozie: The Workflow Scheduler for Hadoop" by Mohammad Kamrul Islam and Aravind Srinivasan (O'Reilly, 2015).
---

# Apache Oozie Expert

Based on: *Apache Oozie: The Workflow Scheduler for Hadoop* by Mohammad Kamrul Islam and Aravind Srinivasan (O'Reilly, 2015).

Oozie is a server-based workflow scheduler for Hadoop that orchestrates sequences of Hadoop jobs (MapReduce, Hive, Pig, Spark, etc.) using time and data triggers.

## Oozie Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         OOZIE SERVER                                  │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │
│  │   BUNDLE     │   │  COORDINATOR │   │       WORKFLOW           │  │
│  │  (pipeline   │──▶│  (time +     │──▶│  (DAG of actions)        │  │
│  │   manager)   │   │  data trigger│   │                          │  │
│  └──────────────┘   └──────────────┘   │  start ──▶ action1       │  │
│                                        │           ──▶ fork        │  │
│                                        │              ├─▶ action2  │  │
│                                        │              └─▶ action3  │  │
│                                        │           ──▶ join        │  │
│                                        │           ──▶ end         │  │
│                                        └──────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     ACTION EXECUTORS                           │  │
│  │  MapReduce · Hive · Pig · Spark · Sqoop · Java · Shell · FS   │  │
│  │  Email · SSH · DistCp · Sub-Workflow · HTTP                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │
│  │  Oozie DB    │   │   HDFS       │   │  Hadoop Cluster          │  │
│  │ (job state)  │   │ (app deploy) │   │  (job execution)         │  │
│  └──────────────┘   └──────────────┘   └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Oozie concepts, workflow/coordinator/bundle model, parameters, variables, architecture | [concepts.md](references/concepts.md) |
| Workflow XML, control nodes (start/end/fork/join/decision/kill), lifecycle, error handling | [workflows.md](references/workflows.md) |
| Action types: MapReduce, Java, Hive, Pig, Spark, Sqoop, Shell, FS, Email, Sub-Workflow | [actions.md](references/actions.md) |
| Coordinator XML, time-based triggers, cron scheduling, coordinator action lifecycle | [coordinators.md](references/coordinators.md) |
| Data trigger coordinators, datasets, HCatalog dependencies, data availability functions | [data-triggers.md](references/data-triggers.md) |
| Bundles, pipeline management, reprocessing, bundle lifecycle | [bundles.md](references/bundles.md) |
| Deployment, oozie-site.xml, shared libraries, CLI, REST API, monitoring, HA, security, tuning, debugging | [operations.md](references/operations.md) |

## Reference Files

| File | Chapters | Key Topics |
|------|----------|-----------|
| `concepts.md` | 1–2 | Oozie purpose, workflow/coordinator/bundle model, parameters, EL functions, application deployment model, architecture |
| `workflows.md` | 5 | Workflow XML schema, control nodes, action nodes, fork/join, decision, error transitions, workflow lifecycle |
| `actions.md` | 4 | MapReduce, Java, Hive, Pig, Spark, Sqoop, Shell, FS, Email, SSH, DistCp, Sub-Workflow action definitions |
| `coordinators.md` | 6 | Coordinator XML, time-based trigger, cron scheduling, frequency, start/end times, coordinator action lifecycle |
| `data-triggers.md` | 7 | Data availability triggers, datasets, input/output data, HCatalog partition dependency, EL data functions |
| `bundles.md` | 8 | Bundle XML, pipeline orchestration, coordinator grouping, reprocessing, pause/resume |
| `operations.md` | 3, 9 | Installation, oozie-site.xml, shared libraries, Oozie CLI, REST API, Java client, monitoring, JMS, HA, Kerberos security, JVM tuning, debugging, custom extensions |

## Core Decision Trees

### Which Oozie Construct Do I Need?

```
What are you trying to schedule?
├── A single sequence of Hadoop jobs, run on demand
│   └── Workflow (workflow.xml)
├── A workflow that runs on a time schedule
│   └── Coordinator (coordinator.xml) with time-based trigger
├── A workflow that runs when data arrives in HDFS/HCatalog
│   └── Coordinator with data availability trigger
├── Both time AND data (run at T only if data is ready)
│   └── Coordinator with both triggers
└── Multiple coordinators that form a pipeline together
    └── Bundle (bundle.xml) groups and manages them
```

### Which Action Type?

```
What does the step need to do?
├── Run a MapReduce job → <map-reduce>
├── Run arbitrary Java code → <java>
├── Run a Hive query or script → <hive> or <hive2>
├── Run a Pig script → <pig>
├── Run a Spark job → <spark>
├── Import/export data with Sqoop → <sqoop>
├── Run a shell script → <shell>
├── Manipulate HDFS files (mkdir/move/delete/chmod) → <fs>
├── Copy between clusters → <distcp>
├── Send an email notification → <email>
├── Call another workflow → <sub-workflow>
└── Make an HTTP call → <http>
```

### Workflow Error Handling?

```
What should happen when an action fails?
├── Stop the entire workflow → transition to <kill> node
├── Retry the action → add retry-max and retry-interval attributes
├── Skip to a different action → use error-to transition
├── Run cleanup/notification before stopping
│   └── Add an action before <kill> (e.g., send email, cleanup FS)
└── Different handling per error type
    └── Use <decision> node on ${wf:errorCode("actionName")}
```

### Coordinator Trigger Strategy?

```
How should the coordinator fire?
├── At fixed time intervals (hourly, daily, etc.)
│   └── frequency="${coord:hours(1)}" or cron expression
├── When input data is available in HDFS
│   └── <data-in> with dataset pointing to HDFS path
├── When HCatalog partition is ready
│   └── <data-in> with HCatalog URI
└── Both: at scheduled time AND only if data is ready
    └── Set frequency + <input-events> with <data-in>
    └── Coordinator waits until both conditions are met
```

## Key Concepts

### The Three-Layer Model
```
Bundle     — groups multiple coordinators into a pipeline; manages lifecycle together
  └── Coordinator — triggers workflow executions based on time and/or data
        └── Workflow — defines the DAG of actions to run
```

### Application Deployment Model
All Oozie applications are deployed to HDFS before submission. The Oozie server reads XML definitions from HDFS — not from the client machine.

```
Local machine                 HDFS                        Oozie Server
workflow.xml  ──hdfs dfs─▶  /user/me/my-app/           reads from HDFS
job.properties               workflow.xml               submits to Hadoop
lib/*.jar                    lib/*.jar
coordinator.xml              coordinator.xml
```

### Expression Language (EL)
Oozie uses a JSP-like EL for parameterization:
```
${coord:current(0)}          current dataset instance
${coord:hours(1)}            1 hour in minutes (for frequency)
${wf:actionData("step1")}    output from a previous action
${fs:exists("/path")}        HDFS file existence check
${jobTracker}                built-in variable for cluster
```

### Workflow Node Types
| Node Type | Purpose |
|-----------|---------|
| `<start>` | Entry point — exactly one per workflow |
| `<end>` | Successful completion |
| `<kill>` | Failure termination with message |
| `<action>` | Executes a Hadoop action; has ok-to and error-to |
| `<fork>` | Splits execution into parallel paths |
| `<join>` | Waits for all forked paths to complete |
| `<decision>` | Routes to one of N paths based on EL predicates |
