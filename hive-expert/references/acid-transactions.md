# Hive ACID Transactions

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Creating ACID Tables](#creating-acid-tables)
4. [Transaction Configuration](#transaction-configuration)
5. [Compaction](#compaction)
6. [INSERT_ONLY Tables](#insert_only-tables)
7. [Limitations](#limitations)

---

## Overview

Hive ACID (Atomicity, Consistency, Isolation, Durability) provides row-level INSERT, UPDATE, DELETE, and MERGE operations. Hive 3.0+ enables full ACID for managed ORC tables by default.

**Key versions:**
- Hive 0.13: Initial ACID support (limited)
- Hive 1.x/2.x: ACID available but not default; required explicit `transactional=true`
- Hive 3.0+: Full ACID is **default** for managed ORC tables; `strict` locking

**How it works:**
- Delta directories accumulate changes (inserts, deletes recorded as separate files)
- Base directory holds compacted data
- Read-time merge combines base + deltas to produce current state
- Compaction consolidates deltas into base periodically

---

## Requirements

```
1. Table format:      ORC only (no Parquet, Avro, TextFile)
2. Table type:        Managed (not External)
3. No bucketing req:  NOT required for full ACID in Hive 3+
                      (required for Hive 2.x)
4. Metastore:         Must use RDBMS (not Derby for production)
5. Engine:            Tez (default) or Spark (Hive 3.1+)
                      MapReduce NOT supported for ACID writes
```

---

## Creating ACID Tables

### Hive 3+ (automatic for managed ORC)

```sql
-- In Hive 3+, this is ACID by default:
CREATE TABLE orders (
  order_id  BIGINT,
  user_id   BIGINT,
  amount    DECIMAL(10,2),
  status    STRING,
  created   TIMESTAMP
)
STORED AS ORC;
-- transactional=true is set automatically

-- Verify:
DESCRIBE FORMATTED orders;
-- Look for: transactional = true in Table Parameters
```

### Explicit ACID declaration (all versions)

```sql
CREATE TABLE orders (
  order_id BIGINT,
  status   STRING
)
STORED AS ORC
TBLPROPERTIES ('transactional' = 'true');
```

### Partitioned ACID table

```sql
CREATE TABLE events (
  event_id   BIGINT,
  event_type STRING,
  user_id    BIGINT
)
PARTITIONED BY (event_date STRING)
STORED AS ORC
TBLPROPERTIES ('transactional' = 'true');
```

---

## Transaction Configuration

```sql
-- Enable ACID (required for Hive 2.x; auto in 3+)
SET hive.support.concurrency = true;
SET hive.enforce.bucketing = true;              -- Hive 2.x only
SET hive.exec.dynamic.partition.mode = nonstrict;
SET hive.txn.manager = org.apache.hadoop.hive.ql.lockmgr.DbTxnManager;

-- In hive-site.xml for server-level config:
hive.txn.manager = org.apache.hadoop.hive.ql.lockmgr.DbTxnManager
hive.compactor.initiator.on = true       -- run initiator on this HiveServer2
hive.compactor.cleaner.on = true         -- run cleaner on this HiveServer2
hive.compactor.worker.threads = 1        -- compaction worker threads

-- Isolation level
SET hive.txn.isolationlevel = snapshot;  -- default: snapshot isolation

-- Lock timeout
SET hive.lock.sleep.between.retries = 60s;
SET hive.lock.numretries = 100;
```

### Showing transactions and locks

```sql
SHOW TRANSACTIONS;
SHOW LOCKS;
SHOW LOCKS orders;                          -- locks on specific table
SHOW LOCKS orders PARTITION (event_date='2024-01-15');
SHOW COMPACTIONS;                           -- current compaction jobs
```

---

## Compaction

Compaction merges delta files into base files to maintain read performance. Two types:

### Minor Compaction
- Merges delta files together (not into base)
- Faster; no base rewrite
- Result: fewer delta files, base unchanged

### Major Compaction
- Merges all deltas into a new base file
- Removes delete markers permanently
- Slower but optimal read performance after completion

### Manual compaction

```sql
-- Request minor compaction
ALTER TABLE orders COMPACT 'minor';

-- Request major compaction
ALTER TABLE orders COMPACT 'major';

-- Compact specific partition
ALTER TABLE orders PARTITION (event_date='2024-01-15') COMPACT 'major';

-- With options (Hive 3.1+)
ALTER TABLE orders COMPACT 'major'
  WITH OVERWRITE TBLPROPERTIES (
    'compactor.mapreduce.map.memory.mb' = '4096'
  );

-- Wait for compaction to complete
SHOW COMPACTIONS;
-- Check State column: initiated → working → ready for cleaning → succeeded
```

### Auto-compaction thresholds

```sql
-- Set per-table (in TBLPROPERTIES or hive-site.xml)
'hive.compactor.delta.num.threshold'  = '10'   -- minor if > 10 deltas
'hive.compactor.delta.pct.threshold'  = '0.1'  -- major if deltas > 10% of base size

-- Global defaults (hive-site.xml):
hive.compactor.check.interval = 300s           -- how often initiator checks
hive.compactor.initiator.on = true
hive.compactor.worker.threads = 1
```

### Compaction housekeeping

```sql
-- After major compaction, cleaner removes old delta/base directories
-- Cleaner respects open transactions — won't delete files still in use

-- Force cleanup check (rarely needed)
-- Typically automatic when hive.compactor.cleaner.on = true
```

---

## INSERT_ONLY Tables

Cheaper alternative: no UPDATE/DELETE support, but better write performance.

```sql
-- INSERT_ONLY: supports only INSERT, not UPDATE/DELETE/MERGE
CREATE TABLE events_append (
  event_id   BIGINT,
  event_type STRING,
  ts         TIMESTAMP
)
STORED AS ORC
TBLPROPERTIES ('transactional' = 'true', 'transactional_properties' = 'insert_only');

-- Benefits vs full ACID:
-- • Faster writes (no row-id column overhead)
-- • No split-update merge read cost
-- • Supports more file formats if ORC not needed: TextFile, Parquet with insert_only

-- Drawbacks:
-- • No UPDATE, DELETE, MERGE
-- • Compaction not applicable (no delta merge needed)
```

---

## Limitations

```
Full ACID tables:
• ORC only — no other storage formats
• Managed tables only — not external
• No UPDATE/DELETE on partition columns
• No direct JOIN in UPDATE (use subquery)
• Subqueries in WHERE clause for UPDATE/DELETE
• Row-level locking granularity (snapshot isolation)

Performance considerations:
• Read overhead: Hive merges base + deltas at read time
• Write overhead: Row-id column added (hidden _row_id STRUCT)
• Large numbers of small deltas → poor read performance before compaction
• Run major compaction after bulk loading or heavy UPDATE/DELETE workloads

Versioning:
• Hive 2.x: requires CLUSTERED BY (bucketed); Hive 3.0+ does not
• MapReduce engine: cannot write to ACID tables (use Tez or Spark)
• Hive 3.0+: default full ACID for managed ORC — be aware when migrating 2.x tables

External tables:
• Cannot have ACID transactions
• Use INSERT OVERWRITE + partitions for append-only ETL patterns
```

### Checking table ACID status

```sql
-- See if table is transactional and what type
DESCRIBE FORMATTED my_table;

-- Look for in "Table Parameters":
-- transactional             = true
-- transactional_properties  = default  (full ACID)
--                           = insert_only  (insert-only ACID)

-- Or via query:
SELECT TBL_NAME, PARAM_VALUE
FROM TBLS t JOIN TABLE_PARAMS tp ON t.TBL_ID = tp.TBL_ID
WHERE tp.PARAM_KEY = 'transactional'
  AND tp.PARAM_VALUE = 'true';
-- (queries Metastore DB directly)
```
