# Hive Streaming: TRANSFORM...USING

## Table of Contents
1. [TRANSFORM Syntax](#transform-syntax)
2. [Python Examples](#python-examples)
3. [Script File Pattern](#script-file-pattern)
4. [SerDe for Input/Output](#serde-for-inputoutput)
5. [When to Use vs Java UDFs](#when-to-use-vs-java-udfs)

---

## TRANSFORM Syntax

`TRANSFORM...USING` pipes rows to an external process (stdin/stdout) and reads output back as columns. Works with any executable (Python, Perl, bash, compiled binaries).

```sql
-- Basic syntax
SELECT TRANSFORM(col1, col2, ...)
  USING 'command'
AS (out_col1 type, out_col2 type, ...)
FROM table_name;

-- Input columns are written to the process as tab-separated values (\t delimiter)
-- Process reads from stdin, writes tab-separated results to stdout
-- Each output line becomes one row

-- With ROW FORMAT (customize delimiters)
SELECT TRANSFORM(col1, col2)
  ROW FORMAT DELIMITED FIELDS TERMINATED BY ','   -- input format to process
  USING 'python3 my_script.py'
  ROW FORMAT DELIMITED FIELDS TERMINATED BY ','   -- output format from process
AS (result_col STRING, score DOUBLE)
FROM my_table;
```

### Full syntax

```sql
SELECT TRANSFORM(input_cols)
  [ROW FORMAT DELIMITED
    [FIELDS TERMINATED BY char]
    [COLLECTION ITEMS TERMINATED BY char]
    [MAP KEYS TERMINATED BY char]
    [LINES TERMINATED BY char]
    [NULL DEFINED AS char]]
  | [ROW FORMAT SERDE serde_classname [WITH SERDEPROPERTIES (...)]]
  USING 'command'
  [AS (col_name col_type, ...)]
  [ROW FORMAT ...]  -- for output
FROM table_name
[WHERE condition];
```

---

## Python Examples

### Simple transformation (uppercase)

```sql
SELECT TRANSFORM(order_id, status)
  USING 'python3 -c "
import sys
for line in sys.stdin:
    line = line.rstrip(\"\\n\")
    fields = line.split(\"\\t\")
    print(fields[0] + \"\\t\" + fields[1].upper())
"'
AS (order_id BIGINT, status_upper STRING)
FROM orders
LIMIT 100;
```

### Bucketed streaming (DISTRIBUTE BY + TRANSFORM)

```sql
-- DISTRIBUTE BY ensures all rows for same user go to same process instance
-- SORT BY ensures they arrive in order for stateful processing
SELECT TRANSFORM(user_id, created, amount)
  USING 'python3 sessionize.py'
AS (user_id BIGINT, session_id STRING, session_amount DOUBLE)
FROM orders
DISTRIBUTE BY user_id
SORT BY user_id, created;
```

This is the key pattern for stateful per-key operations — equivalent to writing a custom reducer.

### Map-only TRANSFORM (no reducer)

```sql
-- SELECT TRANSFORM without GROUP BY / DISTRIBUTE BY → runs as mapper only
SELECT TRANSFORM(raw_line)
  USING 'python3 parse_log.py'
AS (ts TIMESTAMP, level STRING, message STRING)
FROM raw_logs;
```

---

## Script File Pattern

For anything beyond a one-liner, use a script file on HDFS.

### Python script (parse_log.py)

```python
#!/usr/bin/env python3
import sys
import re
import json

LOG_PATTERN = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)'
)

for line in sys.stdin:
    line = line.rstrip('\n')
    m = LOG_PATTERN.match(line)
    if m:
        ts, level, msg = m.group(1), m.group(2), m.group(3)
        # Output: tab-separated columns
        print('\t'.join([ts, level, msg.replace('\t', ' ')]))
    else:
        # Malformed line: emit nulls
        print('\t'.join(['\\N', '\\N', line[:200].replace('\t', ' ')]))
```

### Register and use

```sql
-- Upload script to HDFS once
-- hdfs dfs -put parse_log.py hdfs:///user/hive/scripts/

-- Add script to distributed cache for this session
ADD FILE hdfs:///user/hive/scripts/parse_log.py;
-- or local: ADD FILE /path/to/parse_log.py;

-- Use in TRANSFORM
SELECT TRANSFORM(raw_line)
  USING 'python3 parse_log.py'
AS (ts STRING, level STRING, message STRING)
FROM raw_logs
WHERE dt = '2024-01-15';

-- Script runs as the Hive job user (not hive user) — check permissions
```

### Multi-file scripts (with dependencies)

```sql
-- Add multiple files
ADD FILE hdfs:///user/hive/scripts/transform.py;
ADD FILE hdfs:///user/hive/scripts/utils.py;  -- imported by transform.py

-- Or use ADD ARCHIVE for a directory:
ADD ARCHIVE hdfs:///user/hive/scripts/my_package.tar.gz;
-- The archive is extracted; scripts run from extracted directory
USING 'python3 my_package/transform.py'
```

---

## SerDe for Input/Output

By default, TRANSFORM uses tab (`\t`) as field separator and `\N` for NULL.

```sql
-- Customize NULL representation
SELECT TRANSFORM(col1, col2)
  ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    NULL DEFINED AS ''
  USING 'python3 script.py'
  ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    NULL DEFINED AS ''
AS (result STRING)
FROM my_table;

-- Using LazyBinarySerDe for binary data (faster, less overhead)
SELECT TRANSFORM(col1)
  ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
  WITH SERDEPROPERTIES ('field.delim'='\t', 'serialization.null.format'='\\N')
  USING 'python3 script.py'
  ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
  WITH SERDEPROPERTIES ('field.delim'='\t')
AS (result STRING)
FROM my_table;
```

### NULL handling in scripts

```python
# \N is Hive's default NULL marker
NULL_MARKER = '\\N'

for line in sys.stdin:
    fields = line.rstrip('\n').split('\t')
    # Check for NULL
    val = None if fields[0] == NULL_MARKER else fields[0]
    # Emit NULL
    result = '\\N' if val is None else process(val)
    print(result)
```

---

## When to Use vs Java UDFs

| | TRANSFORM / Python | Java GenericUDF |
|--|-------------------|-----------------|
| Development speed | Fast (Python) | Slower (compile, JAR deploy) |
| Performance | Slower (process fork, serialization) | Faster (in-JVM) |
| Stateful streaming | Excellent (DISTRIBUTE BY + SORT BY) | Not natural |
| Complex types | Harder (serialize/deserialize manually) | Native (ObjectInspectors) |
| Vectorization | Not supported | Supported |
| Deployment | Script on HDFS, ADD FILE | JAR on HDFS, CREATE FUNCTION |
| Error handling | Harder (stderr only) | Full Java exception handling |
| **Best for** | Prototyping, Python libraries (pandas, ML models), log parsing | Production aggregations, type-aware transformations |

### Pattern: ML model scoring in TRANSFORM

```python
#!/usr/bin/env python3
# score_model.py — load a sklearn model and score rows
import sys
import pickle
import numpy as np

# Load model once on startup
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

for line in sys.stdin:
    fields = line.rstrip('\n').split('\t')
    if len(fields) < 3:
        print('\\N')
        continue
    features = np.array([float(x) if x != '\\N' else 0.0 for x in fields], ndmin=2)
    score = model.predict_proba(features)[0][1]
    print(f'{score:.6f}')
```

```sql
ADD FILE hdfs:///models/model.pkl;
ADD FILE hdfs:///scripts/score_model.py;

SELECT TRANSFORM(feature1, feature2, feature3)
  USING 'python3 score_model.py'
AS (score DOUBLE)
FROM feature_table
WHERE event_date = '2024-01-15';
```
