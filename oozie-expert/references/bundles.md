# Oozie Bundles
## Chapter 8: Oozie Bundles

---

## What Is a Bundle?

A **bundle** is a collection of coordinators treated as a single unit. It is the pipeline management layer — for when several coordinators are logically part of the same data pipeline and should be started, stopped, and managed together.

```
bundle.xml
  ├── coordinator: ingest-coord
  ├── coordinator: transform-coord
  └── coordinator: load-coord
```

A bundle lets you:
- Start all pipeline coordinators with one submission
- Pause, resume, or kill the entire pipeline together
- Reprocess a date range across all coordinators in the bundle
- Track pipeline health in the Oozie web UI from one place

---

## Bundle XML Structure

```xml
<bundle-app name="daily-pipeline"
            xmlns="uri:oozie:bundle:0.2">

  <controls>
    <kick-off-time>2024-01-01T00:00Z</kick-off-time>
  </controls>

  <coordinator name="ingest">
    <app-path>${nameNode}/user/me/pipeline/ingest-coord</app-path>
    <configuration>
      <property>
        <name>start</name>
        <value>2024-01-01T00:00Z</value>
      </property>
      <property>
        <name>end</name>
        <value>2025-01-01T00:00Z</value>
      </property>
      <property>
        <name>wfPath</name>
        <value>${nameNode}/user/me/pipeline/ingest-wf</value>
      </property>
    </configuration>
  </coordinator>

  <coordinator name="transform">
    <app-path>${nameNode}/user/me/pipeline/transform-coord</app-path>
    <configuration>
      <property>
        <name>start</name>
        <value>2024-01-01T00:00Z</value>
      </property>
      <property>
        <name>end</name>
        <value>2025-01-01T00:00Z</value>
      </property>
      <property>
        <name>wfPath</name>
        <value>${nameNode}/user/me/pipeline/transform-wf</value>
      </property>
    </configuration>
  </coordinator>

  <coordinator name="load">
    <app-path>${nameNode}/user/me/pipeline/load-coord</app-path>
    <configuration>
      <property>
        <name>start</name>
        <value>2024-01-01T00:00Z</value>
      </property>
      <property>
        <name>end</name>
        <value>2025-01-01T00:00Z</value>
      </property>
      <property>
        <name>wfPath</name>
        <value>${nameNode}/user/me/pipeline/load-wf</value>
      </property>
    </configuration>
  </coordinator>

</bundle-app>
```

### kick-off-time

The `<kick-off-time>` in `<controls>` is the time at which Oozie starts all the coordinators in the bundle. If not set, they start immediately upon bundle submission.

---

## Submitting a Bundle

```bash
# job.properties
oozie.bundle.application.path=${nameNode}/user/me/pipeline/bundle.xml

oozie job -oozie http://oozie:11000/oozie \
          -config job.properties \
          -run
```

---

## Bundle Lifecycle States

| State | Description |
|-------|-------------|
| `PREP` | Submitted, waiting for kick-off-time |
| `RUNNING` | At least one coordinator is running |
| `SUSPENDED` | All coordinators suspended |
| `SUCCEEDED` | All coordinators completed successfully |
| `KILLED` | Operator killed the bundle |
| `FAILED` | One or more coordinators failed |
| `DONEWITHERROR` | All done but some failed |

---

## Managing Bundles via CLI

```bash
# View bundle status
oozie job -oozie http://oozie:11000/oozie -info <bundle-job-id>

# Suspend all coordinators
oozie job -oozie http://oozie:11000/oozie -suspend <bundle-job-id>

# Resume all coordinators
oozie job -oozie http://oozie:11000/oozie -resume <bundle-job-id>

# Kill the entire bundle
oozie job -oozie http://oozie:11000/oozie -kill <bundle-job-id>

# Change end time for the entire bundle
oozie job -oozie http://oozie:11000/oozie \
          -change <bundle-job-id> \
          -value endtime=2025-06-01T00:00Z
```

---

## Reprocessing

Reprocessing re-runs a date range of coordinator actions across the bundle — useful for backfills, fixing bad data, or recovering from failures.

```bash
# Rerun all coordinators in bundle for a date range
oozie job -oozie http://oozie:11000/oozie \
          -rerun <bundle-job-id> \
          -date 2024-03-01T00:00Z::2024-03-07T00:00Z \
          -coordinators ingest,transform,load \
          -nocleanup -refresh
```

Options:
- `-coordinators`: comma-separated list of coordinator names to reprocess (omit to reprocess all)
- `-date`: date range in `start::end` format
- `-nocleanup`: do not delete output data before rerunning
- `-refresh`: re-read workflow definitions from HDFS

### Reprocessing Pattern for Bad Data

When upstream data was bad for a date range:
1. Fix the bad source data
2. Re-run the ingest coordinator for the affected dates
3. Re-run transform and load coordinators for the same dates
4. A bundle `-rerun` with all coordinators does all three in one command

---

## Bundle Design Patterns

### Pipeline with Data Dependencies

The most common bundle pattern: each coordinator depends on the output of the previous one via data triggers.

```
bundle.xml
  ├── ingest-coord   (time-triggered: runs at T+0)
  │     └── produces /data/raw/${date}/_SUCCESS
  │
  ├── transform-coord (data-triggered: fires when ingest output is ready)
  │     └── input: /data/raw/${date}
  │     └── produces /data/processed/${date}/_SUCCESS
  │
  └── load-coord     (data-triggered: fires when transform output is ready)
        └── input: /data/processed/${date}
        └── produces /data/final/${date}
```

### Frequency Alignment

All coordinators in a bundle should use the same frequency. Mixed frequencies (e.g., one hourly and one daily) make reprocessing and monitoring complex. If you need different frequencies, use separate bundles.

### Separate Bundles by Logical Pipeline

One bundle per logical pipeline:
- `transactions-bundle`: ingest → enrich → aggregate → report
- `users-bundle`: profile-sync → segment → export

This keeps monitoring clean and allows independent reprocessing of each pipeline.
