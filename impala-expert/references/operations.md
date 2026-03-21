# Cluster Operations and Administration
## Chapter 9: Admission Control, Resource Pools, Memory, Metadata Management, Troubleshooting

---

## Daemon Management

### The Three Daemons

| Daemon | Port (default) | Role | Single or Multi? |
|--------|---------------|------|-----------------|
| `impalad` | 21000 (Beeswax), 21050 (HS2), 25000 (Web UI) | Query planning + execution | One per datanode |
| `statestored` | 24000, 25010 (Web UI) | Cluster membership | One per cluster |
| `catalogd` | 26000, 25020 (Web UI) | Metadata cache + propagation | One per cluster |

### Starting and Stopping (CDH/Cloudera Manager)

```bash
# Via Cloudera Manager: use CM UI or CM API
# Manual start (init.d or systemd)
sudo service impala-server start|stop|restart|status
sudo service impala-state-store start|stop|restart
sudo service impala-catalog start|stop|restart

# Check web UIs
http://impalad-host:25000   # Query list, memory, profiles
http://statestore-host:25010 # Subscriber status
http://catalogd-host:25020  # Catalog contents
```

### Dedicated Coordinator Nodes (Large Clusters)

On large clusters (20+ nodes), designate specific nodes as coordinators to separate planning from execution:

```
# Coordinator impalad (no execution work):
--is_executor=false
--is_coordinator=true

# Executor impalad (no client queries):
--is_executor=true
--is_coordinator=false

# Clients connect only to coordinator nodes
# Coordinator dispatches fragments to executor nodes
```

Benefits: coordinators have predictable memory usage; executors are not burdened by query planning.

---

## Metadata Management

### INVALIDATE METADATA vs. REFRESH

```sql
-- INVALIDATE METADATA: heavy operation
-- Drops ALL cached metadata for the table/database
-- Reloads from Hive Metastore on next query
-- Use when: table schema changed; table created/dropped outside Impala

INVALIDATE METADATA;               -- reload ALL tables (very slow on large clusters)
INVALIDATE METADATA mydb.orders;   -- reload one table (faster)

-- REFRESH: lightweight operation
-- Reloads only file and partition listing metadata
-- Preserves cached statistics
-- Use when: new files added to HDFS/S3; new partitions added via Hive/Spark

REFRESH mydb.orders;
REFRESH mydb.sales_by_day PARTITION (dt='2024-01-15');
REFRESH mydb.orders PARTITION SPEC (dt);  -- refresh all partitions of dt
```

### Metadata Warm-Up

On a fresh catalogd restart, metadata is loaded lazily (on first access). To pre-warm:

```sql
-- Pre-load metadata for all tables in a database
USE mydb;
SHOW TABLES;  -- triggers catalogd to load all table metadata
```

Or use the `catalogd` flag `--load_catalog_in_background=true` to proactively load all metadata at startup.

---

## Admission Control

Admission control is Impala's gate for managing concurrent query execution. It queues or rejects queries that would exceed resource limits.

### How Admission Control Works

```
Query arrives at coordinator
        │
        ▼
Check request pool limits:
  ├── Pool has capacity (mem + concurrency)?
  │       → Admit query immediately
  ├── Pool queue is below max_queued?
  │       → Queue the query; wait for capacity
  └── Queue is full?
              → Reject query with error
```

### Resource Pool Configuration

Pools are defined in fair-scheduler.xml and llama-site.xml (or via Cloudera Manager):

```xml
<!-- fair-scheduler.xml (example) -->
<pool name="bi-team">
  <maxResources>100000 mb, 50 vcores</maxResources>
  <schedulingPolicy>fair</schedulingPolicy>
</pool>

<pool name="etl">
  <maxResources>200000 mb, 100 vcores</maxResources>
</pool>
```

```xml
<!-- llama-site.xml: Impala-specific admission control -->
<property>
  <name>impala.admission-control.pool-default-query-mem-limit.bi-team</name>
  <value>8589934592</value>  <!-- 8 GB per query in bi-team pool -->
</property>
<property>
  <name>impala.admission-control.max-query-mem-limit.bi-team</name>
  <value>17179869184</value> <!-- 16 GB max per query -->
</property>
<property>
  <name>impala.admission-control.max-requests.bi-team</name>
  <value>20</value>          <!-- max 20 concurrent queries -->
</property>
<property>
  <name>impala.admission-control.max-queued-requests.bi-team</name>
  <value>50</value>          <!-- max 50 queries in queue -->
</property>
<property>
  <name>impala.admission-control.queue-timeout-ms.bi-team</name>
  <value>30000</value>       <!-- reject if queued > 30 seconds -->
</property>
```

### Assigning Queries to Pools

```sql
-- Client sets the pool for the session
SET REQUEST_POOL = 'bi-team';

-- Or per-query in code
impala-shell -q "SET REQUEST_POOL='etl'; INSERT INTO ..."
```

Pool selection can also be driven by user/group via Ranger policies or a custom pool assignment function.

---

## Memory Management

### Per-Node Memory Architecture

```
impalad process memory
├── Reserved: process overhead (JVM metadata, statestore/catalogd caches)
├── Query memory (controlled by MEM_LIMIT)
│   ├── Hash tables (joins, aggregations)
│   ├── Sort buffers
│   ├── Scan buffers
│   └── Intermediate exchange buffers
└── Scratch disk (spill location when memory exceeded)
```

### Key Memory Settings

```
# impalad startup flags
--mem_limit=80%              # fraction of system RAM reserved for impalad
                              # leave ~20% for OS + HDFS DataNode

--scratch_dirs=/tmp/impala-scratch,/data/impala-scratch
                              # comma-separated; data spills here when MEM_LIMIT exceeded

--max_spilled_partitions=128  # max partitions that can spill for a single operator
```

### Query-Level Memory Control

```sql
-- Hard limit per query (per node)
SET MEM_LIMIT = '8g';

-- Admission control sets a default if MEM_LIMIT = 0 (pool default)
SET MEM_LIMIT = 0;

-- Check memory usage after query
PROFILE;
-- Look for: "Peak Memory Usage" per node
```

### Memory Pressure Symptoms

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `Memory limit exceeded` error | MEM_LIMIT too low | Increase MEM_LIMIT or pool limit |
| Query spilling to disk (very slow) | Memory insufficient for in-memory hash/sort | Increase MEM_LIMIT; optimize query |
| `OutOfMemory` kills impalad process | `--mem_limit` set too high; OS OOM killer | Reduce `--mem_limit` to leave room for OS |
| Broadcast join OOM | Large table broadcasted | Force shuffle join; run COMPUTE STATS |
| Long queue times | Pool max concurrent too low | Increase pool concurrency limits |

---

## Common Operations

### Compacting Small Files

Small files degrade Parquet read performance (too many open file handles, poor compression):

```sql
-- Rewrite partition to consolidate small files into one large file
INSERT OVERWRITE sales_by_day PARTITION (dt='2024-01-15')
SELECT order_id, amount FROM sales_by_day WHERE dt='2024-01-15';

-- Or for whole table (expensive for large tables)
INSERT OVERWRITE sales_by_day PARTITION (dt)
SELECT order_id, amount, dt FROM sales_by_day;
```

### Partition Maintenance

```sql
-- List partitions and their sizes
SHOW PARTITIONS sales_by_day;

-- Drop old partitions (data retention policy)
ALTER TABLE sales_by_day DROP PARTITION (dt < '2023-01-01');

-- Recover partitions added outside Impala (e.g., by Spark writing S3 paths)
ALTER TABLE s3_sales RECOVER PARTITIONS;

-- Move partition to new location
ALTER TABLE sales_by_day PARTITION (dt='2024-01-15')
SET LOCATION '/new/path/dt=2024-01-15';
```

### Statistics Maintenance

```sql
-- Refresh stats after significant data changes
COMPUTE INCREMENTAL STATS sales_by_day;        -- only changed partitions
COMPUTE INCREMENTAL STATS sales_by_day PARTITION (dt='2024-01-15');

-- View current stats
SHOW TABLE STATS sales_by_day;
SHOW COLUMN STATS sales_by_day;
```

---

## Troubleshooting Common Errors

### Query Errors

| Error | Common Cause | Fix |
|-------|-------------|-----|
| `AnalysisException: Table does not exist` | Metadata not loaded | `INVALIDATE METADATA db.table` |
| `NotAuthorizedException` | Ranger/Sentry permission missing | Grant SELECT on table to user/role |
| `Memory limit exceeded` | MEM_LIMIT too low | `SET MEM_LIMIT='16g'` |
| `Disk I/O error reading from HDFS` | DataNode failure; HDFS issue | Check HDFS health; hadoop fsck |
| `Backend ... unreachable` | impalad died on that node | Check impalad logs on that node |
| `Row size ... exceeds limit` | Row contains very large STRING | `SET MAX_ROW_SIZE = '32m'` |
| `Cancelled` | Query cancelled manually or by timeout | Rerun; check admission control queue timeout |
| `IllegalStateException in exchange` | Network issue or node failure | Retry; check cluster health |

### Performance Issues

```sql
-- Step 1: Check for missing stats
EXPLAIN SELECT ...;
-- Look for: "WARNING: The following tables are missing ... statistics"
-- Fix: COMPUTE STATS <tables>

-- Step 2: Check partition pruning
EXPLAIN SELECT ...;
-- Look for: "partitions=X/Y" — is X << Y?
-- If not: rewrite WHERE to use partition column directly

-- Step 3: Check join strategy
EXPLAIN SELECT ...;
-- Look for unexpected BROADCAST of a large table
-- Fix: COMPUTE STATS; or add hint /*+ SHUFFLE */

-- Step 4: Run SUMMARY after query
-- Look for node with Max Time >> Avg Time (data skew)

-- Step 5: Check slow scans
-- Look for scan nodes reading all files despite filters
-- Cause: predicate not pushed to scan (function on column, type mismatch)
```

### impalad Log Locations

```bash
# Default log directory
/var/log/impalad/impalad.ERROR    # errors only
/var/log/impalad/impalad.WARNING  # warnings
/var/log/impalad/impalad.INFO     # all logs (very verbose)

# Query-specific logs: use Web UI
http://impalad-host:25000/queries  # running and recently completed queries
http://impalad-host:25000/memz     # memory breakdown
```

---

## Web UI Reference

| URL | Contents |
|-----|---------|
| `http://impalad:25000/` | Overview: mem, threads, connections |
| `http://impalad:25000/queries` | Running and completed queries |
| `http://impalad:25000/query_profile?query_id=<id>` | Full query profile |
| `http://impalad:25000/memz` | Memory allocation breakdown |
| `http://impalad:25000/admission` | Admission control pool status |
| `http://statestore:25010/` | Subscriber list; heartbeat status |
| `http://catalogd:25020/` | Catalog contents; metadata cache |
