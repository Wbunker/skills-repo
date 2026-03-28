---
name: apache-oozie-expert
description: "Expert knowledge of Apache Oozie workflow scheduler for Hadoop, based on 'Apache Oozie: The Workflow Scheduler for Hadoop' by Islam & Srinivasan (O'Reilly). Use when the user asks about: writing Oozie workflow XML, coordinator jobs, bundle jobs, action types (MapReduce, Hive, Pig, Spark, Shell, FS, Java, Sub-workflow), fork/join, decision nodes, coordinator frequency and cron expressions, data triggers and datasets, done-flag, coord:current/latest/future EL functions, SLA monitoring, Oozie CLI commands, REST API, oozie-site.xml configuration, Kerberos security, HA setup, sharelib, JAR management, custom action executors, custom EL functions, rerun/reprocess strategies, job states, ENEX search, or debugging Oozie failures."
---

# Apache Oozie Expert

Based on *Apache Oozie: The Workflow Scheduler for Hadoop* — Islam & Srinivasan (O'Reilly, 2015) and the official Oozie docs.

## Reference Files by Topic

| Chapter | Topic | File |
|---------|-------|------|
| 1–2 | Core concepts, architecture, three job types, EL, job states | [ch01-02-concepts.md](references/ch01-02-concepts.md) |
| 3 | Server setup, oozie-site.xml, DB, Kerberos, HA | [ch03-setup.md](references/ch03-setup.md) |
| 4 | All action types with XML (MR, Hive, Spark, Shell, FS, Java, SSH, Sqoop…) | [ch04-actions.md](references/ch04-actions.md) |
| 5 | Workflow structure, fork/join, decision, parameterization, EL functions | [ch05-workflows.md](references/ch05-workflows.md) |
| 6 | Coordinator time triggers, frequency EL, cron syntax, controls | [ch06-coordinator-time.md](references/ch06-coordinator-time.md) |
| 7 | Coordinator data triggers, datasets, done-flag, input/output events, HCatalog | [ch07-coordinator-data.md](references/ch07-coordinator-data.md) |
| 8 | Bundle jobs, kick-off-time, multi-coordinator pipelines | [ch08-bundles.md](references/ch08-bundles.md) |
| 9 | SLA monitoring, sharelib management, JAR precedence, advanced topics | [ch09-advanced.md](references/ch09-advanced.md) |
| 10 | Custom EL functions, custom action executors, deployment | [ch10-developer.md](references/ch10-developer.md) |
| 11 | Full CLI reference, REST API, rerun strategies, admin, troubleshooting | [ch11-operations.md](references/ch11-operations.md) |

## Quick Decision Guide

**What are you working on?**

- Writing a workflow XML → [ch05-workflows.md](references/ch05-workflows.md) + [ch04-actions.md](references/ch04-actions.md)
- Scheduling a job on a time interval → [ch06-coordinator-time.md](references/ch06-coordinator-time.md)
- Triggering on data availability / HDFS path → [ch07-coordinator-data.md](references/ch07-coordinator-data.md)
- Managing a pipeline of coordinators → [ch08-bundles.md](references/ch08-bundles.md)
- Setting up or configuring the server → [ch03-setup.md](references/ch03-setup.md)
- CLI commands / REST API / rerun → [ch11-operations.md](references/ch11-operations.md)
- SLA alerts / sharelib issues → [ch09-advanced.md](references/ch09-advanced.md)
- Custom action or EL function → [ch10-developer.md](references/ch10-developer.md)
- New to Oozie / concepts overview → [ch01-02-concepts.md](references/ch01-02-concepts.md)

## Key Facts (No Reference Load Required)

**Three job types:**
- `oozie.wf.application.path` → Workflow (single DAG execution)
- `oozie.coord.application.path` → Coordinator (repeated runs on schedule/data)
- `oozie.bundle.application.path` → Bundle (group of coordinators)

**Every action requires:**
```xml
<ok to="next-node-name"/>
<error to="fail-node-name"/>
```

**Submit any job:**
```bash
oozie job -oozie http://oozie:11000/oozie -config job.properties -run
```

**Three most common gotchas:**
1. Missing `oozie.use.system.libpath=true` → Hive/Pig/Spark ClassNotFoundException
2. Timezone as abbreviation (`PST`) instead of `America/Los_Angeles` → DST drift
3. Fork path not reaching the join → workflow hangs silently
