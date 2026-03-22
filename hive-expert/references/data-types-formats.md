# Hive Data Types & File Formats

## Table of Contents
1. [Primitive Types](#primitive-types)
2. [Collection Types](#collection-types)
3. [Type Conversion](#type-conversion)
4. [File Formats](#file-formats)
5. [SerDe Reference](#serde-reference)
6. [ROW FORMAT Syntax](#row-format-syntax)

---

## Primitive Types

| Type | Size | Range / Notes |
|------|------|---------------|
| `TINYINT` | 1 byte | -128 to 127; literal suffix `Y`: `100Y` |
| `SMALLINT` | 2 bytes | -32,768 to 32,767; suffix `S`: `100S` |
| `INT` / `INTEGER` | 4 bytes | -2.1B to 2.1B |
| `BIGINT` | 8 bytes | suffix `L`: `100L` |
| `FLOAT` | 4 bytes | Single-precision IEEE 754 |
| `DOUBLE` / `DOUBLE PRECISION` | 8 bytes | |
| `DECIMAL(p,s)` / `NUMERIC(p,s)` | Variable | Default `DECIMAL(10,0)`; max precision 38 |
| `STRING` | Variable | UTF-8; no length limit |
| `VARCHAR(n)` | Variable | 1–65535 chars; truncates on insert |
| `CHAR(n)` | Fixed | 1–255; right-pads with spaces |
| `BOOLEAN` | 1 bit | `TRUE` / `FALSE` |
| `BINARY` | Variable | Byte array; not comparable |
| `TIMESTAMP` | | `'YYYY-MM-DD HH:MM:SS.fffffffff'`; nanosecond precision; stored as UTC |
| `TIMESTAMP WITH LOCAL TIME ZONE` | | Hive 3.1+; converts to session timezone on read |
| `DATE` | | `'YYYY-MM-DD'`; no time component |
| `INTERVAL` | | `INTERVAL '1' DAY`, `INTERVAL '2-3' YEAR TO MONTH` |

### Numeric literals
```sql
SELECT 1Y, 1S, 1, 1L, 1.0, 1.0BD;  -- TINYINT, SMALLINT, INT, BIGINT, DOUBLE, DECIMAL
```

---

## Collection Types

### ARRAY
```sql
-- Declaration
col ARRAY<STRING>
col ARRAY<INT>

-- Literal
array('a', 'b', 'c')
array(1, 2, 3)

-- Access (0-indexed)
col[0]

-- Check membership
array_contains(col, 'a')  -- returns BOOLEAN

-- Size
size(col)  -- returns INT (-1 if NULL)
```

### MAP
```sql
-- Declaration
col MAP<STRING, INT>

-- Literal
map('k1', 1, 'k2', 2)

-- Access
col['k1']

-- Keys/values
map_keys(col)    -- returns ARRAY<STRING>
map_values(col)  -- returns ARRAY<INT>
size(col)        -- number of entries
```

### STRUCT
```sql
-- Declaration
col STRUCT<name:STRING, age:INT, active:BOOLEAN>

-- Literal
named_struct('name', 'Alice', 'age', 30, 'active', true)

-- Field access (dot notation)
col.name
col.age
```

### UNIONTYPE (rarely used)
```sql
col UNIONTYPE<INT, DOUBLE, STRING>
-- create_union(tag, value1, value2, value3)
-- Access: col.(0) for INT value
```

### Nested collections
```sql
-- Array of structs (common pattern)
col ARRAY<STRUCT<id:INT, value:STRING>>
col[0].id

-- Map of arrays
col MAP<STRING, ARRAY<INT>>
col['key'][0]
```

---

## Type Conversion

### Implicit coercions (automatic)
```
TINYINT → SMALLINT → INT → BIGINT → FLOAT → DOUBLE → DECIMAL → STRING
```
Hive widens automatically in expressions and comparisons. `STRING` can be converted to numeric implicitly if the value parses.

### Explicit CAST
```sql
CAST(col AS BIGINT)
CAST(col AS DECIMAL(18,4))
CAST(col AS STRING)
CAST(col AS TIMESTAMP)          -- from STRING 'yyyy-MM-dd HH:mm:ss'
CAST(col AS DATE)               -- from STRING 'yyyy-MM-dd' or TIMESTAMP
CAST(col AS BOOLEAN)            -- 'true'/'false' strings
CAST('2024-01-15' AS DATE)
```

### NULL handling
- Any operation on NULL returns NULL (except `IS NULL`, `IS NOT NULL`, `COALESCE`, `NVL`)
- `COUNT(*)` counts NULLs; `COUNT(col)` does not
- `NULL = NULL` is NULL (not TRUE) — use `col IS NULL`
- `<=>` (null-safe equality): `NULL <=> NULL` is TRUE

---

## File Formats

### TextFile (default)
```sql
STORED AS TEXTFILE
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY '\t'
  COLLECTION ITEMS TERMINATED BY ','
  MAP KEYS TERMINATED BY ':'
  LINES TERMINATED BY '\n'
  NULL DEFINED AS 'NULL'
```
- Human-readable; poor performance at scale
- Default delimiter: `\001` (Ctrl-A) for fields
- Supports gzip/bzip2/snappy compression (gzip not splittable)

### ORC (Optimized Row Columnar) — **recommended default**
```sql
STORED AS ORC
TBLPROPERTIES (
  'orc.compress'          = 'SNAPPY',   -- NONE, ZLIB, SNAPPY, LZO, ZSTD
  'orc.stripe.size'       = '67108864', -- 64MB default
  'orc.block.size'        = '268435456',-- 256MB default
  'orc.bloom.filter.columns' = 'col1,col2',
  'orc.bloom.filter.fpp'  = '0.05'
)
```
**Why ORC:**
- Columnar storage → reads only needed columns
- Stripe-level min/max statistics → skip stripes without scanning
- Bloom filters → skip stripes for point lookups
- Lightweight indexes built-in
- Required for ACID transactions in Hive
- Best compression ratios of all formats in Hive ecosystem

### Parquet
```sql
STORED AS PARQUET
TBLPROPERTIES (
  'parquet.compression' = 'SNAPPY'  -- UNCOMPRESSED, SNAPPY, GZIP, LZO, ZSTD
)
```
- Columnar; excellent interoperability with Spark, Impala, Presto/Trino, Drill
- Slightly larger files than ORC in typical Hive workloads
- Preferred when data is shared across multiple engines

### Avro
```sql
STORED AS AVRO
TBLPROPERTIES (
  'avro.schema.url' = 'hdfs:///schemas/myschema.avsc'
  -- or inline:
  -- 'avro.schema.literal' = '{"type":"record","name":"..."}'
)
```
- Row-based; good for streaming/Kafka pipelines
- Schema evolution support (add/remove/rename fields with defaults)
- Use `org.apache.hadoop.hive.serde2.avro.AvroSerDe`

### Parquet vs ORC Decision Guide
| Concern | Choose |
|---------|--------|
| Pure Hive workloads | ORC |
| Mixed Hive + Spark + Presto | Parquet |
| ACID transactions required | ORC (required) |
| Schema evolution critical | Avro |
| Maximum compression | ORC (ZLIB/ZSTD) |

### SequenceFile (legacy)
```sql
STORED AS SEQUENCEFILE
```
Binary key-value format; splittable; largely replaced by ORC/Parquet.

### RCFile (legacy)
```sql
STORED AS RCFILE
```
Row-Columnar hybrid; superseded by ORC.

### Iceberg Tables (Hive 4.0+)
```sql
CREATE TABLE iceberg_table (id INT, name STRING)
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler'
TBLPROPERTIES ('write.format.default' = 'orc');  -- orc, parquet, or avro
```

---

## SerDe Reference

SerDe = Serializer/Deserializer. Controls how Hive reads/writes rows.

### LazySimpleSerDe (default for TextFile)
```sql
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  COLLECTION ITEMS TERMINATED BY '|'
  MAP KEYS TERMINATED BY '='
  NULL DEFINED AS ''
```

### OpenCSVSerde (proper CSV with quoting)
```sql
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"',
  'escapeChar'    = '\\'
)
STORED AS TEXTFILE
```
**Note:** OpenCSVSerde treats ALL columns as STRING. CAST after reading.

### JSONSerde
```sql
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
```
- One JSON object per line
- Column names must match JSON keys (case-insensitive)
- Nested JSON maps to STRUCT/ARRAY/MAP types

### RegexSerde (parsing log files)
```sql
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'input.regex' = '(\\d+)\\s+(\\w+)\\s+(.+)',
  'output.format.string' = '%1$s %2$s %3$s'
)
STORED AS TEXTFILE
```

### AvroSerde
```sql
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
STORED AS INPUTFORMAT  'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
           OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
TBLPROPERTIES ('avro.schema.url' = 'hdfs:///schemas/my.avsc')
```

---

## ROW FORMAT Syntax

```sql
-- Delimited (LazySimpleSerDe shorthand)
ROW FORMAT DELIMITED
  [FIELDS TERMINATED BY char]
  [COLLECTION ITEMS TERMINATED BY char]
  [MAP KEYS TERMINATED BY char]
  [LINES TERMINATED BY char]
  [NULL DEFINED AS char]

-- Custom SerDe
ROW FORMAT SERDE 'fully.qualified.SerDeClassName'
[WITH SERDEPROPERTIES ('key' = 'value', ...)]

-- Special characters
'\t'   -- tab
'\001' -- Ctrl-A (Hive default field delimiter)
'\002' -- Ctrl-B (Hive default collection delimiter)
'\003' -- Ctrl-C (Hive default map key delimiter)
```
