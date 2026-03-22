# Pig Latin Basics
_Ch. 1–3 of "Programming Pig" — Language fundamentals, data model, types, LOAD, basic operators_

## Data Types

### Scalar Types

| Type | Size | Notes |
|------|------|-------|
| `int` | 32-bit signed | Java Integer |
| `long` | 64-bit signed | Java Long; default for COUNT |
| `float` | 32-bit IEEE | Java Float |
| `double` | 64-bit IEEE | Java Double; default for AVG |
| `chararray` | UTF-8 string | Java String |
| `bytearray` | Raw bytes | Default when type unknown |
| `boolean` | true/false | Pig 0.10+ |
| `datetime` | ISO-8601 | Pig 0.10+ |
| `biginteger` | Arbitrary precision | Pig 0.11+ |
| `bigdecimal` | Arbitrary precision decimal | Pig 0.11+ |

### Complex Types

```pig
-- Tuple: ordered, fixed-width record
(1, 'alice', 3.5)

-- Bag: unordered collection of tuples
{(1,'a'), (2,'b'), (1,'c')}

-- Map: string keys, any-type values
['name'#'alice', 'score'#42]
```

## Schema Declaration

```pig
-- Explicit schema on LOAD
data = LOAD 'path/' USING PigStorage(',')
       AS (id:int, name:chararray, score:float);

-- Nested schema
events = LOAD 'path/' AS (
    user_id:int,
    attrs:tuple(country:chararray, age:int),
    tags:bag{t:(tag:chararray)}
);

-- Map field
meta = LOAD 'path/' AS (id:int, props:map[]);
-- Access map: props#'key'
```

## LOAD Statement

```pig
-- TSV (default delimiter is \t)
a = LOAD 'path/' USING PigStorage('\t') AS (f1:int, f2:chararray);

-- CSV
b = LOAD 'path/' USING PigStorage(',') AS (...);

-- Multiple files / glob
c = LOAD 'path/2024/*/events/' USING PigStorage(',') AS (...);

-- No schema (fields accessed as $0, $1, ...)
d = LOAD 'path/' USING PigStorage(',');
val = FOREACH d GENERATE $0, $2;

-- Cloud storage (AWS S3)
s3_data = LOAD 's3://my-bucket/data/events/' USING PigStorage(',') AS (...);

-- Cloud storage (GCP GCS)
gcs_data = LOAD 'gs://my-bucket/data/events/' USING PigStorage(',') AS (...);

-- JSON (requires JsonLoader — built-in since Pig 0.8)
json_data = LOAD 'path/' USING JsonLoader('id:int, name:chararray, score:float');

-- Text lines
lines = LOAD 'path/' USING TextLoader() AS (line:chararray);
```

## STORE Statement

```pig
-- TSV output
STORE result INTO 'output/path/' USING PigStorage('\t');

-- CSV output
STORE result INTO 'output/path/' USING PigStorage(',');

-- S3 output
STORE result INTO 's3://bucket/output/' USING PigStorage('\t');

-- GCS output
STORE result INTO 'gs://bucket/output/' USING PigStorage('\t');
```

## DUMP and DESCRIBE (Interactive)

```pig
-- Print relation to console (triggers execution)
DUMP result;

-- Print schema without executing
DESCRIBE result;

-- Print logical plan
EXPLAIN result;
```

## FOREACH / GENERATE — Basic Projection

```pig
-- Project specific fields
proj = FOREACH data GENERATE id, name;

-- Computed field
enriched = FOREACH data GENERATE id, name, score * 1.1 AS adjusted_score:float;

-- Flatten a tuple field
flat = FOREACH data GENERATE id, FLATTEN(attrs) AS (country:chararray, age:int);

-- Flatten a bag field (creates one row per bag element)
exploded = FOREACH events GENERATE user_id, FLATTEN(tags) AS tag:chararray;

-- Access map field
val = FOREACH data GENERATE id, props#'region' AS region:chararray;
```

## FILTER

```pig
-- Comparison operators: ==, !=, >, >=, <, <=
filtered = FILTER data BY score > 50.0;

-- Logical operators: AND, OR, NOT
multi = FILTER data BY score > 50.0 AND country == 'US';

-- Null checks
non_null = FILTER data BY name IS NOT NULL;
nulls = FILTER data BY name IS NULL;

-- Regex match
matched = FILTER data BY name MATCHES '.*bunker.*';

-- Test membership (Pig 0.16+)
subset = FILTER data BY id IN (1, 2, 3);
```

## Type Casting

```pig
cast = FOREACH data GENERATE (int)$0 AS id, (float)$2 AS score;

-- Safe cast from bytearray
safe = FOREACH data GENERATE (chararray)raw_field AS name;
```

## Comments and Script Structure

```pig
-- Single line comment

/* Multi-line
   comment */

-- SET to configure runtime properties
SET default_parallel 20;
SET job.name 'my-pig-job';
SET mapreduce.job.queuename 'default';

-- REGISTER a UDF jar
REGISTER 'myudfs.jar';
-- Or from HDFS/S3/GCS:
REGISTER 's3://bucket/libs/myudfs.jar';

-- DEFINE an alias for a UDF
DEFINE MyFunc com.example.MyEvalFunc();
```

## Null Handling

```pig
-- Arithmetic with null propagates null
-- Use a CASE expression or conditional UDF to replace nulls

-- Replace null with 0
no_null = FOREACH data GENERATE id,
    (score IS NULL ? 0.0 : score) AS score:float;
```
