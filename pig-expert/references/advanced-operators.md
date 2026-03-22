# Advanced Operators
_Ch. 5 of "Programming Pig" — Nested FOREACH, FLATTEN, advanced joins, macros, stream_

## Nested FOREACH

Nested FOREACH lets you apply relational operators (FILTER, DISTINCT, ORDER, LIMIT) to a bag inside a FOREACH block. This is one of Pig's most powerful patterns.

```pig
-- Syntax: use {} block after FOREACH relation
result = FOREACH grouped {
    -- Operations inside {} apply to the bag for each group
    active   = FILTER events BY status == 'active';
    uniq     = DISTINCT active.category;
    sorted   = ORDER active BY timestamp DESC;
    recent   = LIMIT sorted 5;
    GENERATE
        group       AS user_id,
        COUNT(active)  AS active_count,
        COUNT(uniq)    AS distinct_categories,
        recent         AS recent_events;
};
```

**Rules for nested FOREACH:**
- Only `FILTER`, `DISTINCT`, `ORDER BY`, `LIMIT`, and `FOREACH` are allowed inside the block
- Cannot use `GROUP`, `JOIN`, or `COGROUP` inside a nested block
- Intermediate aliases (like `active`, `uniq`) are local to the block

## FLATTEN

```pig
-- Flatten a tuple: expands tuple fields into top-level fields
data = FOREACH nested GENERATE id, FLATTEN(attrs) AS (country:chararray, age:int);
-- Input:  (1, ('US', 30))
-- Output: (1, 'US', 30)

-- Flatten a bag: creates one row per bag element (cross-product with other fields)
exploded = FOREACH grouped GENERATE FLATTEN(events) AS (ts:long, amt:float);
-- Input:  (user1, {(t1, 5.0), (t2, 3.0)})
-- Output: (user1, t1, 5.0)
--         (user1, t2, 3.0)

-- Flatten multiple bags: produces Cartesian product of bags
-- Use carefully — can cause data explosion
cross = FOREACH data GENERATE FLATTEN(bag_a), FLATTEN(bag_b);
```

## Replicated JOIN Deep Dive

```pig
-- Best for: fact table JOIN small dimension table
-- The small relation is distributed to every mapper as a hash map
-- Result: map-only job, no shuffle

orders = LOAD 's3://bucket/orders/' AS (order_id:int, user_id:int, amount:float);
users  = LOAD 's3://bucket/users/'  AS (id:int, name:chararray, tier:chararray);

-- small relation MUST be last
enriched = JOIN orders BY user_id, users BY id USING 'replicated';

-- Multiple small relations supported
result = JOIN large BY k, dim1 BY k, dim2 BY k USING 'replicated';
-- All non-first relations are replicated
```

## Skewed JOIN Deep Dive

```pig
-- Handles hot keys by sampling data to detect skew
-- Splits large groups across multiple reducers
skewed = JOIN a BY key, b BY key USING 'skewed';

-- Configuration:
SET pig.skewedjoin.reduce.memusage 0.3;  -- fraction of heap for in-memory tuples
SET pig.skewedJoin.factor 5;             -- how many tasks to split a skewed group into

-- Note: more overhead than default join — only use when keys are genuinely skewed
```

## Merge JOIN

```pig
-- Requirements: both inputs MUST be:
--   1. Sorted on the join key
--   2. Loaded with a loader that supports IndexableLoadFunc (e.g., PigStorage after indexing)
-- Result: map-only job (no reduce phase)

-- Typical workflow:
sorted_a = ORDER large_a BY key;
STORE sorted_a INTO 'hdfs/sorted_a' USING PigStorage('\t');
-- (run a separate job to build index, or use pre-sorted input)

merged = JOIN sorted_a BY key, sorted_b BY key USING 'merge';
```

## MAPREDUCE (Streaming to Hadoop Jobs)

```pig
-- Embed a custom MapReduce job within a Pig script
-- Useful for operations not expressible in Pig Latin
result = MAPREDUCE 'myjar.jar'
    STORE input INTO 'tmp/input' USING PigStorage()
    LOAD  'tmp/output' USING PigStorage() AS (k:chararray, v:int)
    `hadoop jar myjar.jar com.example.MyJob tmp/input tmp/output`;
```

## STREAM

```pig
-- Pipe data through an external command (Python, bash, etc.)
DEFINE preprocess `python3 normalize.py` SHIP('normalize.py');

cleaned = STREAM raw_data THROUGH preprocess AS (id:int, value:float);

-- SHIP: upload local files to cluster for use in streaming
-- INPUT/OUTPUT schemas must be tab-delimited by default
```

## Macros (Pig 0.9+)

Macros allow you to define reusable Pig Latin templates.

```pig
-- Define a macro (typically in a separate .pig file)
DEFINE clean_and_filter(data, min_score) RETURNS result {
    filtered = FILTER $data BY score >= $min_score;
    $result  = FOREACH filtered GENERATE id, name, score;
};

-- Use the macro
clean = clean_and_filter(raw, 50.0);

-- Import macros from a file
IMPORT 'macros/common.pig';
```

**Macro limitations:**
- Cannot define macros inside other macros
- Parameters are positional, not named
- Macros are expanded at compile time (not runtime)

## REGISTER and DEFINE

```pig
-- Register a JAR containing UDFs
REGISTER 'myudfs.jar';
REGISTER 's3://bucket/libs/piggybank-0.17.0.jar';  -- from S3
REGISTER 'gs://bucket/libs/piggybank-0.17.0.jar';  -- from GCS

-- Define an alias with constructor args
DEFINE CsvExcelLoader org.apache.pig.piggybank.storage.CSVExcelStorage(',', 'NO_MULTILINE', 'UNIX');
DEFINE MyEval com.example.MyEvalFunc('param1', 'param2');

-- Use in script
data = LOAD 'path/' USING CsvExcelLoader() AS (...);
result = FOREACH data GENERATE id, MyEval(name) AS normalized_name;
```

## Script Parameters and Substitution

```pig
-- Parameters substituted at runtime
-- Default values:
%default DATE '2024-01-01';
%default ENV 'prod';

-- Declare (no default — must be provided or script fails)
%declare THRESHOLD 0.5;

-- Use in script
data = LOAD 's3://bucket/$ENV/events/$DATE/';
filtered = FILTER data BY score > $THRESHOLD;
```

```bash
# Pass from command line
pig -param DATE=2024-03-01 -param ENV=staging myscript.pig

# From file
pig -param_file run_params.txt myscript.pig
```

## SET Properties for Performance

```pig
-- Parallelism (number of reducers for GROUP, JOIN, ORDER, etc.)
SET default_parallel 50;

-- Override for a specific operation
result = GROUP data BY key PARALLEL 100;

-- Combiner (enabled by default for SUM, COUNT, etc.)
SET pig.exec.nocombiner false;  -- ensure combiner is on

-- Tez execution (if cluster supports it)
SET exectype tez;

-- Memory for reduce tasks (MapReduce)
SET mapreduce.reduce.memory.mb 4096;
SET mapreduce.reduce.java.opts -Xmx3072m;

-- Spill thresholds
SET pig.cachedbag.memusage 0.2;
SET pig.skewedjoin.reduce.memusage 0.3;
```
