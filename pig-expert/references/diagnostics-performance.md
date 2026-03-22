# Diagnostics and Performance
_Ch. 9 of "Programming Pig" — ILLUSTRATE, DESCRIBE, EXPLAIN, multi-query optimization, parallelism tuning_

## Diagnostic Commands

### DESCRIBE — Inspect Schema

```pig
raw = LOAD 'path/' USING PigStorage(',') AS (id:int, name:chararray, amount:float);
filtered = FILTER raw BY amount > 0;
grouped = GROUP filtered BY name;

-- Check schema at any point (no job execution)
DESCRIBE raw;
-- raw: {id: int, name: chararray, amount: float}

DESCRIBE grouped;
-- grouped: {group: chararray, filtered: {(id: int, name: chararray, amount: float)}}
```

### EXPLAIN — View Execution Plan

```pig
-- Print logical, physical, and MapReduce plans to stdout
EXPLAIN result;

-- Save to files (useful for large plans)
EXPLAIN -out /tmp/explain_output -dot result;
-- Generates DOT files for GraphViz visualization

-- Explain with Tez engine
EXPLAIN -exectype tez result;

-- Check multi-query optimization (see if Pig merged multiple scans)
EXPLAIN -script myscript.pig;
```

**Reading EXPLAIN output:**
- **Logical Plan**: what operations Pig will perform
- **Physical Plan**: how operations map to MR tasks (MapReduce or Tez DAG)
- **MapReduce Plan**: the actual jobs — look here for unexpected extra jobs

### ILLUSTRATE — Trace Execution with Sample Data

```pig
-- Generates a small synthetic dataset and traces it through your script
-- Does NOT run a MapReduce job
ILLUSTRATE result;

-- Useful for: understanding FLATTEN behavior, verifying joins, checking nulls
-- Note: may not reflect actual data distribution or edge cases
```

### DUMP — Execute and Print

```pig
-- Triggers full execution; prints results to stdout
-- Use only on small datasets or for debugging
DUMP (LIMIT result 20);
```

## Performance Optimization

### 1. Filter Early and Project Narrow

```pig
-- BAD: project then filter
wide = FOREACH data GENERATE *;
filtered = FILTER wide BY status == 'active';

-- GOOD: filter first, then project only needed fields
filtered = FILTER data BY status == 'active';
narrow = FOREACH filtered GENERATE id, name, amount;
```

### 2. Use Replicated JOIN for Small Tables

```pig
-- Default join: requires shuffle of both relations
-- Replicated join: broadcasts small table to all mappers (no shuffle needed)
result = JOIN large BY key, small BY key USING 'replicated';
-- Rule of thumb: small table < 100MB (or fits in task heap)
```

### 3. Set Parallelism Explicitly

```pig
-- Default: Pig estimates based on input size, may be wrong
SET default_parallel 50;

-- Override per operation
grouped = GROUP events BY user_id PARALLEL 100;
sorted  = ORDER events BY ts PARALLEL 50;
joined  = JOIN a BY key, b BY key PARALLEL 80;

-- Calculate: target ~256MB input per reducer
-- parallelism = total_input_bytes / (256 * 1024 * 1024)
```

### 4. Enable Multi-Query Optimization

Multi-query optimization lets Pig read input once for multiple STORE operations.

```pig
-- Both stores share a single scan of 'input'
a_result = FILTER input BY type == 'A';
b_result = FILTER input BY type == 'B';
STORE a_result INTO 'output/a/';
STORE b_result INTO 'output/b/';
-- Pig generates 1 MR job instead of 2

-- Disable if causing issues:
SET opt.multiquery false;
```

### 5. Use Algebraic UDFs for Aggregation

Algebraic UDFs run in the combiner (map-side partial aggregation), dramatically reducing shuffle volume. See `udfs.md` for implementation details.

### 6. Combiner Configuration

```pig
-- Ensure combiner is enabled (it is by default for built-in aggregations)
SET pig.exec.nocombiner false;

-- Pig built-ins that use the combiner automatically:
-- COUNT, SUM, MIN, MAX, AVG, COUNT_STAR
-- Custom UDFs must implement Algebraic to use combiner
```

### 7. Reduce Memory Pressure

```pig
-- Increase spill threshold (fraction of heap before spilling to disk)
SET pig.cachedbag.memusage 0.2;       -- default 0.2 (20% of heap per bag)
SET pig.skewedjoin.reduce.memusage 0.3;

-- For jobs with OOM errors in reducers:
-- Increase reduce heap via cluster config, not Pig settings
-- mapreduce.reduce.java.opts=-Xmx6g
```

### 8. Compress Intermediate Data

```pig
-- Enable intermediate compression (reduces shuffle I/O)
SET mapreduce.map.output.compress true;
SET mapreduce.map.output.compress.codec org.apache.hadoop.io.compress.SnappyCodec;

-- Enable temp file compression
SET pig.tmpfilecompression true;
SET pig.tmpfilecompression.codec lzo;  -- or snappy, gz
```

### 9. Tez Execution Engine

Tez builds a DAG of tasks rather than chaining MR jobs, avoiding intermediate HDFS writes.

```pig
-- Enable Tez (if available on cluster)
SET exectype tez;

-- Or launch with:
-- pig -x tez myscript.pig

-- On EMR: available in EMR 6.x; add --optional-components Tez at cluster creation
-- On Dataproc: add --optional-components=TEZ at cluster creation
```

**Tez advantages:**
- Fewer disk spills between operations
- Better DAG optimization (e.g., broadcast joins without replicated join hint)
- Shorter job completion time for multi-step scripts

### 10. ORDER BY Optimization

```pig
-- ORDER BY always requires a full sort (reduce phase) — expensive
-- Only sort when necessary (e.g., before LIMIT for top-N, or before merge join)

-- Top-N without full sort is not possible in standard Pig
-- Use nested FOREACH with ORDER + LIMIT per group instead
top_per_group = FOREACH (GROUP events BY user_id) {
    sorted = ORDER events BY score DESC;
    top3 = LIMIT sorted 3;
    GENERATE group AS user_id, top3;
};
-- This is more efficient than a global ORDER + LIMIT for per-group top-N
```

## Diagnosing Common Problems

### Job Runs Slowly

```
Symptoms: many MR jobs, slow reducers, OOM errors
Diagnosis steps:
1. EXPLAIN result; → count MapReduce jobs; unexpected joins/groups?
2. Check reducer count: too few causes hot reducers; too many causes overhead
3. Check combiner: is it running? Check job counters in YARN UI
4. Check skew: one reducer taking 10x longer? → use 'skewed' join or SPLIT
```

### Schema Errors / Null Results

```
Symptoms: DUMP shows nulls where data expected, or schema mismatch errors
Diagnosis:
1. DESCRIBE at each step to trace schema changes
2. ILLUSTRATE to trace a single record through transformations
3. Check FLATTEN usage — flattening a null bag produces zero rows
4. Check JOIN type — inner join drops non-matching rows
```

### OOM in Reducers

```
Symptoms: task killed, "Java heap space" in logs
Solutions:
1. Reduce GROUP BY cardinality or split into smaller groups
2. Use Algebraic UDF to push aggregation to map side
3. Use AccumulatorFunc instead of EvalFunc for bag aggregation
4. Increase reduce heap: mapreduce.reduce.java.opts=-Xmx8g
5. For joins: switch to replicated (for small tables) or skewed (for hot keys)
```

### Too Many Small Output Files

```
Symptoms: output directory has thousands of tiny files (common from large parallelism)
Solution: add a consolidation step with low parallelism
result = ORDER final BY id PARALLEL 1;
STORE result INTO 'output/';
-- Or use a coalesce pass with PigStorage
```

## Job Counters and Metrics

In YARN ResourceManager UI (or EMR/Dataproc equivalents):

| Counter | What It Tells You |
|---------|------------------|
| `COMBINE_INPUT_RECORDS` | Records entering combiner; 0 = combiner not running |
| `REDUCE_INPUT_RECORDS` | Records reaching reducers; high = shuffle-heavy |
| `SPILLED_RECORDS` | Disk spills; high = memory pressure |
| Map task progress | If maps are slow, data skew in input splits |
| Reduce task progress | If one reducer much slower, key skew |

```bash
# On EMR — YARN UI accessible via SSH tunnel or EMR console
# On Dataproc — Cloud Monitoring / job details in GCP console
gcloud dataproc jobs describe <job-id> --region=us-central1
```

## Local Mode for Development

```bash
# Run entirely locally — no Hadoop needed
pig -x local myscript.pig

# With parameters
pig -x local -p DATE=2024-01-15 myscript.pig

# Interactive shell
pig -x local
grunt> data = LOAD 'local_sample.csv' USING PigStorage(',') AS (id:int, name:chararray);
grunt> DUMP data;
grunt> DESCRIBE data;
grunt> ILLUSTRATE data;
```

**Local mode limitations:**
- No HDFS access (use local file paths)
- No distributed execution (single JVM)
- S3/GCS paths do not work without additional classpath setup
- Use for syntax checking and logic validation only
