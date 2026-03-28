# Ch 11 — Oozie Operations

## Table of Contents
- [CLI Reference](#cli-reference)
- [REST API Reference](#rest-api-reference)
- [Rerun Strategies](#rerun-strategies)
- [Server Administration](#server-administration)
- [Troubleshooting](#troubleshooting)

---

## CLI Reference

```bash
export OOZIE_URL=http://oozie-server:11000/oozie

# ── Submit & Control ──────────────────────────────────────────────

oozie job -config job.properties -run          # submit + start
oozie job -config job.properties -submit       # submit only (PREP)
oozie job -start <job-id>                      # start a PREP job
oozie job -suspend <job-id>
oozie job -resume <job-id>
oozie job -kill <job-id>
oozie job -kill <coord-id> -action 1,3-4,7-40
oozie job -kill <coord-id> -date 2024-01-01T00:00Z::2024-06-30T23:59Z
oozie job -change <coord-id> -value endtime=2025-01-01T00:00Z
oozie job -change <coord-id> -value concurrency=5
oozie job -change <coord-id> -value pausetime=2024-07-01T00:00Z
oozie job -change <coord-id> -value status=RUNNING   # clear pause

# ── Info & Logs ───────────────────────────────────────────────────

oozie job -info <job-id>
oozie job -info <job-id> -len 50 -offset 1           # paginate actions
oozie job -info <coord-id> -filter "status=RUNNING;nominaltime>=2024-06-01T00:00Z"
oozie job -info <coord-id> -allruns                  # show all rerun attempts
oozie job -definition <job-id>                       # show application XML
oozie job -log <job-id>
oozie job -log <coord-id> -action 1,3-4
oozie job -log <job-id> -logfilter "loglevel=ERROR;limit=10;recent=1h"
oozie job -errorlog <job-id>                         # errors only

# ── Rerun ─────────────────────────────────────────────────────────

# Workflow rerun
oozie job -config job.properties -rerun <wf-job-id>

# Coordinator action rerun
oozie job -rerun <coord-id> -action 1,3-4
oozie job -rerun <coord-id> -action 1-5 -nocleanup
oozie job -rerun <coord-id> -action 1-5 -refresh     # re-read coord XML
oozie job -rerun <coord-id> -date 2024-01-01T00:00Z::2024-01-31T23:59Z

# Bundle coordinator rerun
oozie job -rerun <bundle-id> -coordinator ingestion-coord -nocleanup

# Ignore failed coordinator actions (mark as IGNORED instead of FAILED)
oozie job -ignore <coord-id> -action 1,3-4

# ── Update ───────────────────────────────────────────────────────

oozie job -config job.properties -update <coord-id>           # apply new coord XML
oozie job -config job.properties -update <coord-id> -dryrun  # preview changes

# ── List Jobs ────────────────────────────────────────────────────

oozie jobs -len 50 -offset 1
oozie jobs -filter "status=RUNNING;user=joe;name=daily-etl"
oozie jobs -jobtype coordinator -len 100
oozie jobs -jobtype bundle
oozie jobs -bulk 'bundle=daily-pipeline;actionstatus=FAILED' -verbose

# ── Dry Run & Validate ────────────────────────────────────────────

oozie job -config job.properties -dryrun
oozie validate /local/path/to/workflow.xml    # local validation
oozie validate hdfs://namenode/path/coord.xml

# ── Admin ─────────────────────────────────────────────────────────

oozie admin -status
oozie admin -version
oozie admin -systemmode NORMAL
oozie admin -systemmode SAFEMODE      # accept no new submissions
oozie admin -systemmode NOWEBSERVICE
oozie admin -queuedump
oozie admin -servers                  # HA: list all servers
oozie admin -shareliblist
oozie admin -shareliblist pig
oozie admin -sharelibupdate
```

---

## REST API Reference

Base: `http://oozie-server:11000/oozie`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/jobs` | Submit job (XML config body) |
| PUT | `/v1/job/{id}?action=start` | Start |
| PUT | `/v1/job/{id}?action=suspend` | Suspend |
| PUT | `/v1/job/{id}?action=resume` | Resume |
| PUT | `/v1/job/{id}?action=kill` | Kill |
| PUT | `/v1/job/{id}?action=rerun` | Rerun workflow |
| PUT | `/v1/job/{id}?action=coord-rerun&type=action&scope=1-3&refresh=true&nocleanup=false` | Rerun coord actions |
| PUT | `/v1/job/{id}?action=coord-rerun&type=date&scope=2024-01-01T00:00Z::2024-01-31T23:59Z` | Rerun by date range |
| PUT | `/v1/job/{id}?action=change&value=endtime%3D2025-01-01T00%3A00Z` | Change coord |
| PUT | `/v2/job/{id}?action=update` | Update coordinator definition |
| PUT | `/v2/job/{id}?action=ignore&type=action&scope=1,3-4` | Ignore failed actions |
| PUT | `/v2/job/{id}?action=sla-change&value=should-end%3D2024-01-01T12%3A00Z` | Modify SLA |
| GET | `/v1/job/{id}?show=info` | Job info (JSON) |
| GET | `/v1/job/{id}?show=definition` | XML definition |
| GET | `/v1/job/{id}?show=log` | Full log |
| GET | `/v1/job/{id}?show=errorlog` | Error log only |
| GET | `/v1/job/{id}?show=graph&format=png` | DAG image |
| GET | `/v2/job/{id}?show=missing-dependencies` | Missing coord input paths |
| GET | `/v1/jobs?filter=status%3DRUNNING%3Buser%3Djoe&offset=1&len=50` | List jobs |
| GET | `/v1/admin/status` | Server status |
| GET | `/v2/admin/metrics` | Server metrics (JVM, queue, etc.) |
| GET | `/v2/admin/available-oozie-servers` | HA server list |
| GET | `/v2/admin/list_sharelib` | Sharelib listing |
| PUT | `/v2/admin/update_sharelib` | Hot-update sharelib |
| POST | `/v2/validate?file=hdfs%3A%2F%2Fnn%2Fpath%2Fworkflow.xml` | Validate XML |
| PUT | `/v1/jobs?action=kill&filter=name%3Dcron-coord` | Bulk kill by filter |

Submit example:
```bash
curl -X POST http://oozie:11000/oozie/v1/jobs \
  -H "Content-Type: application/xml;charset=UTF-8" \
  -d @job-config.xml
```

---

## Rerun Strategies

### Workflow rerun

```bash
# Full rerun from start
oozie job -config job.properties -rerun <wf-id>
```

To skip already-succeeded actions, add to `job.properties`:
```properties
oozie.wf.rerun.skip.nodes=action1,action2
```

### Coordinator action rerun

```bash
# By action number
oozie job -rerun <coord-id> -action 1,3-4,7-10

# By date range (nominaltime)
oozie job -rerun <coord-id> -date 2024-01-01T00:00Z::2024-01-31T23:59Z

# Flags
-nocleanup     # don't delete output dirs first (useful if you want to inspect old output)
-refresh       # re-read coordinator/workflow XML from HDFS (pick up definition changes)
```

### Ignore vs. kill failed actions

```bash
# Mark FAILED/TIMEDOUT actions as IGNORED (useful when data is irreparably missing)
oozie job -ignore <coord-id> -action 1,3-4

# These actions now have status IGNORED and don't block the coordinator
```

---

## Server Administration

### Purge old jobs

```xml
<!-- oozie-site.xml -->
<property><name>oozie.service.PurgeService.older.than</name><value>30</value></property>
<property><name>oozie.service.PurgeService.coordinator.older.than</name><value>7</value></property>
<property><name>oozie.service.PurgeService.bundle.older.than</name><value>7</value></property>
<property><name>oozie.service.PurgeService.purge.old.coord.action</name><value>false</value></property>
```

### Tuning thread pools

```xml
<property><name>oozie.service.CallableQueueService.queue.size</name><value>10000</value></property>
<property><name>oozie.service.CallableQueueService.threads</name><value>50</value></property>
<property><name>oozie.service.CallableQueueService.callable.concurrency</name><value>3</value></property>
```

### Database connection pool

```xml
<property><name>oozie.service.JPAService.pool.max.active.conn</name><value>10</value></property>
<property><name>oozie.service.JPAService.pool.max.idle.conn</name><value>5</value></property>
<property><name>oozie.service.JPAService.pool.min.idle.conn</name><value>1</value></property>
```

---

## Troubleshooting

### Get missing data dependencies

```bash
# What HDFS paths is this coordinator action still waiting for?
oozie job -info <coord-action-id>   # look for "Missing Dependencies"

# Via REST:
curl http://oozie:11000/oozie/v2/job/<coord-action-id>?show=missing-dependencies
```

### Check queue depth

```bash
oozie admin -queuedump
```

### Common failure patterns

| Symptom | Likely cause |
|---------|-------------|
| Coordinator actions stuck in WAITING | Input `done-flag` not written; check `missing-dependencies` |
| Actions stuck in SUBMITTED | YARN queue full; ResourceManager overloaded |
| `ClassNotFoundException` in Hive/Pig action | `oozie.use.system.libpath=true` missing from job.properties |
| `PERMISSION_DENIED` on HDFS | Oozie server user can't proxy-user for the submitting user; check `hadoop.proxyuser.oozie.*` in core-site.xml |
| Coordinator materializes at wrong time | Timezone mismatch; database not UTC; DST issue |
| `InvalidCoordinatorAttributeException` at submit | `start`+`frequency`+`end` produces zero actions |
| Workflow hangs after fork | A fork path is not reaching the join node |
