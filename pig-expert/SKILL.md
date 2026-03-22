---
name: pig-expert
description: Expert on Apache Pig Latin scripting — language syntax, relational operators, UDFs, I/O formats, and cloud execution on AWS EMR and GCP Dataproc. Use when writing Pig Latin scripts, optimizing pipelines, loading/storing data in cloud storage (S3, GCS), running jobs on managed cloud clusters, or writing custom UDFs. Based on "Programming Pig" by Daniel Dai (O'Reilly), with modern cloud focus.
---

# Apache Pig Expert

Based on "Programming Pig" by Daniel Dai (O'Reilly), with modern focus on AWS EMR and GCP Dataproc execution.

> **Note on currency:** Pig 0.17+ is the stable release. AWS EMR and GCP Dataproc both support Pig as a managed component. While Pig Latin itself is stable, cloud integration patterns (S3/GCS paths, cluster configs, IAM) are the primary modern concern.

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Pig Latin syntax, data types, relations, bags, tuples, maps | [pig-latin-basics.md](references/pig-latin-basics.md) |
| FOREACH, FILTER, GROUP, JOIN, COGROUP, ORDER, DISTINCT, LIMIT | [relational-operators.md](references/relational-operators.md) |
| Nested FOREACH, replicated join, skewed join, merge join, FLATTEN | [advanced-operators.md](references/advanced-operators.md) |
| LOAD/STORE with PigStorage, ORC, Parquet, Avro, JSON, HCatalog/Hive Metastore | [input-output.md](references/input-output.md) |
| Writing UDFs in Python, Java, or JavaScript; Eval/Filter/Aggregate/LoadFunc | [udfs.md](references/udfs.md) |
| Running Pig on AWS EMR — cluster launch, S3 paths, steps, IAM, logging | [aws-emr.md](references/aws-emr.md) |
| Running Pig on GCP Dataproc — cluster launch, GCS paths, jobs, IAM, logging | [gcp-dataproc.md](references/gcp-dataproc.md) |
| ILLUSTRATE, DESCRIBE, EXPLAIN, job counters, profiling, multi-query optimization | [diagnostics-performance.md](references/diagnostics-performance.md) |

## Core Decision Trees

### Where Should This Pig Job Run?

```
What is your cloud environment?
├── AWS
│   ├── Short-lived job (run and terminate) → EMR Serverless (Pig not supported)
│   │   └── Use EMR on EC2 with auto-termination instead
│   ├── Repeatable pipeline → EMR on EC2 cluster + Step (pig-script)
│   └── Interactive development → EMR Studio / SSH + Pig interactive shell
│       → See references/aws-emr.md
│
└── GCP
    ├── Short-lived job → Dataproc Serverless (Pig not supported natively)
    │   └── Use Dataproc on Compute Engine with single-node or autoscaling cluster
    ├── Repeatable pipeline → Dataproc Job submission (pig job type)
    └── Interactive → Dataproc cluster + SSH + pig -x mapreduce
        → See references/gcp-dataproc.md
```

### Which JOIN Type Should I Use?

```
What do you know about your data?
├── One relation is small (fits in memory, ~100MB or less)
│   └── Replicated join: JOIN large BY key, small BY key USING 'replicated'
│       → Fastest; small side broadcast to all map tasks
│
├── One or more keys have extreme data skew (hot keys)
│   └── Skewed join: JOIN a BY key, b BY key USING 'skewed'
│       → Samples data to detect skew; more overhead but avoids reducer OOM
│
├── Both inputs pre-sorted on the join key (merge join)
│   └── Merge join: JOIN a BY key, b BY key USING 'merge'
│       → Map-only job; requires sorted, indexed input
│
└── General case (unsorted, no size advantage)
    └── Default join (hash join via reduce)
        → JOIN a BY key, b BY key
```

### FOREACH or FILTER First?

```
Are you reducing rows or transforming columns?
├── Reducing rows → FILTER early, before FOREACH
│   └── Smaller data into subsequent steps; never project-then-filter
│
├── Transforming/deriving columns → FOREACH after FILTER
│   └── GENERATE only needed fields to minimize tuple width
│
└── Both needed?
    └── FILTER → FOREACH (project needed columns) → GROUP/JOIN
        → Reduces shuffle data volume significantly
```

### Local Mode vs. MapReduce vs. Tez?

```
What execution engine is available?
├── Local testing / small data (< 1GB)
│   └── pig -x local myscript.pig
│       → No Hadoop needed; runs in single JVM
│
├── AWS EMR (Hadoop 3.x based clusters)
│   └── Default: MapReduce (pig -x mapreduce)
│       → Tez available on EMR 6.x: pig -x tez
│
└── GCP Dataproc (Hadoop 3.x, Spark/Tez available)
    └── Default: MapReduce
        → Tez available if enabled at cluster creation
        → Prefer Tez: fewer disk spills, DAG optimization
```

## Key Concepts Quick Reference

### Pig Data Model

| Type | Description | Example |
|------|-------------|---------|
| **atom** | Scalar value (int, long, float, double, chararray, bytearray, boolean, datetime, biginteger, bigdecimal) | `42`, `'hello'` |
| **tuple** | Ordered set of fields | `(1, 'alice', 3.5)` |
| **bag** | Unordered collection of tuples (may contain duplicates) | `{(1,'a'),(2,'b')}` |
| **map** | Key-value pairs; keys are always chararray | `['name'#'alice','age'#30]` |
| **relation** | A bag at the top level (has a schema) | Result of any Pig statement |

### Pig Latin Script Skeleton

```pig
-- 1. Load
raw = LOAD 's3://bucket/path/' USING PigStorage(',')
      AS (id:int, name:chararray, amount:float);

-- 2. Filter early
filtered = FILTER raw BY amount > 0.0;

-- 3. Project only needed fields
projected = FOREACH filtered GENERATE id, name, amount;

-- 4. Group / Join
grouped = GROUP projected BY name;

-- 5. Aggregate
result = FOREACH grouped GENERATE
    group          AS name,
    COUNT(projected) AS cnt,
    SUM(projected.amount) AS total;

-- 6. Sort and limit (optional)
sorted = ORDER result BY total DESC;
top10  = LIMIT sorted 10;

-- 7. Store
STORE top10 INTO 's3://bucket/output/' USING PigStorage('\t');
```

### Common Built-in Functions

| Category | Functions |
|----------|-----------|
| **Math** | ABS, CEIL, EXP, FLOOR, LOG, ROUND, SQRT, CBRT |
| **String** | CONCAT, LOWER, UPPER, TRIM, SUBSTRING, REPLACE, INDEXOF, LAST_INDEX_OF, REGEX_EXTRACT, STRSPLIT, TOKENIZE |
| **Bag/Tuple** | COUNT, COUNT_STAR, SUM, MAX, MIN, AVG, TOBAG, TOTUPLE, TOMAP, TOP |
| **Date/Time** | CurrentTime, GetYear, GetMonth, GetDay, GetHour, GetMinute, ToDate, ToString |
| **Type casting** | (int), (long), (float), (double), (chararray), (bytearray) |

### Pig Parameters (Scripting)

```bash
# Pass parameters at runtime
pig -param DATE=2024-01-15 -param ENV=prod myscript.pig

# Or from a parameter file
pig -param_file params.txt myscript.pig
```

```pig
-- In script, reference with $
raw = LOAD 's3://bucket/$ENV/events/$DATE/' USING PigStorage(',');
```

## Alternatives to Consider

Pig is a stable, proven tool but has been largely superseded for new workloads:

| Use Case | Modern Alternative |
|----------|--------------------|
| Ad-hoc batch ETL on cloud | Apache Spark (PySpark), Dataflow/Beam |
| SQL-style analytics | Hive on EMR/Dataproc, BigQuery, Athena |
| Streaming ETL | Spark Structured Streaming, Apache Flink |
| Simple data movement | AWS Glue ETL, Dataproc Serverless |

**Use Pig when:** you have existing Pig scripts to maintain/migrate, a team with Pig expertise, or a workflow requiring Pig's bag-oriented data model that would be verbose in SQL.
