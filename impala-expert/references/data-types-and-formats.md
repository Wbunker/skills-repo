# Data Types and File Formats
## Chapter 4: Primitive Types, DECIMAL, TIMESTAMP, Complex Types, Parquet, ORC, Avro, Text, Compression

---

## Primitive Data Types

### Numeric Types

| Type | Storage | Range | Notes |
|------|---------|-------|-------|
| `TINYINT` | 1 byte | -128 to 127 | Rarely used; limited range |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | |
| `INT` | 4 bytes | -2,147,483,648 to 2,147,483,647 | Default integer choice |
| `BIGINT` | 8 bytes | ±9.2 × 10^18 | Use for IDs, row counts at scale |
| `FLOAT` | 4 bytes | ~7 significant digits | Approximate; avoid for money |
| `DOUBLE` | 8 bytes | ~15 significant digits | Approximate; prefer DECIMAL for finance |
| `DECIMAL(p,s)` | Variable | Exact numeric | `p` = total digits; `s` = decimal places |

**DECIMAL usage:**
```sql
-- DECIMAL(10,2) = up to 8 digits before decimal, 2 after
-- Max: 99999999.99  Min: -99999999.99
amount   DECIMAL(10, 2)   -- prices, amounts
rate     DECIMAL(6,  4)   -- rates like 1.2345
quantity DECIMAL(15, 0)   -- whole numbers needing high precision
```

DECIMAL is stored as a scaled integer internally — exact arithmetic, no floating-point rounding.

### String Types

| Type | Max Length | Notes |
|------|-----------|-------|
| `STRING` | 32,767 bytes (display); effectively unlimited | Primary string type; variable length |
| `VARCHAR(n)` | n characters (max 65,535) | Hive-compatible; Impala treats like STRING internally |
| `CHAR(n)` | n characters (max 255) | Fixed-width; padded with spaces |

**Best practice**: Use `STRING` for most text data. `VARCHAR`/`CHAR` only when Hive compatibility or exact-width semantics are required.

### Boolean and Binary

| Type | Notes |
|------|-------|
| `BOOLEAN` | `true` / `false` / `NULL` |
| `BINARY` | Variable-length bytes; limited function support |

### Date and Time Types

| Type | Format / Notes |
|------|---------------|
| `TIMESTAMP` | Date + time; microsecond precision; **not timezone-aware** |
| `DATE` | Date only (Impala 3.3+); stored as days since epoch |

**TIMESTAMP caveats:**
- Stored in UTC internally but **no timezone conversion** happens automatically
- Functions like `NOW()` return the local server time
- Use `FROM_UTC_TIMESTAMP(ts, 'America/New_York')` for timezone conversion
- Parquet and Avro store timestamps differently — test cross-format queries

```sql
-- Current timestamp
SELECT NOW();
SELECT CURRENT_TIMESTAMP();

-- Cast between types
SELECT CAST('2024-01-15 10:30:00' AS TIMESTAMP);
SELECT CAST(order_date AS DATE);
SELECT CAST(order_date AS STRING);

-- Timezone conversion
SELECT FROM_UTC_TIMESTAMP(ts_col, 'America/Los_Angeles');
SELECT TO_UTC_TIMESTAMP(local_ts, 'America/Los_Angeles');
```

---

## Complex Types (Impala 2.3+)

Complex types allow nested structures within a single row — common in Parquet and Avro data from event streams.

### ARRAY

```sql
-- Table with an array column
CREATE TABLE orders (
    order_id BIGINT,
    items     ARRAY<STRING>
) STORED AS PARQUET;

-- Query: unnest array with JOIN and ITEM
SELECT o.order_id, item
FROM orders o, o.items item
WHERE item = 'Widget A';

-- Unnest preserves row context
SELECT o.order_id, i.pos, i.item
FROM orders o, o.items i
-- i.pos = 0-based index; i.item = value
```

### MAP

```sql
CREATE TABLE user_prefs (
    user_id  BIGINT,
    settings MAP<STRING, STRING>
) STORED AS PARQUET;

-- Query: access by key, or unnest all keys
SELECT user_id, settings['theme'] AS theme FROM user_prefs;

SELECT u.user_id, kv.key, kv.value
FROM user_prefs u, u.settings kv;
```

### STRUCT

```sql
CREATE TABLE events (
    event_id BIGINT,
    location STRUCT<lat: DOUBLE, lon: DOUBLE, city: STRING>
) STORED AS PARQUET;

-- Access struct fields with dot notation
SELECT event_id, location.city, location.lat FROM events;
```

### Nested Complex Types

Complex types can be nested:
```sql
CREATE TABLE orders (
    order_id BIGINT,
    line_items ARRAY<STRUCT<
        sku:      STRING,
        qty:      INT,
        price:    DECIMAL(10,2)
    >>
) STORED AS PARQUET;

SELECT o.order_id, li.sku, li.qty, li.price
FROM orders o, o.line_items li;
```

**Limitations:**
- Complex type columns cannot be used in GROUP BY, ORDER BY, or as join keys directly
- Must unnest first; unnesting can be expensive at scale
- Only supported in Parquet and Avro files

---

## File Formats

### Parquet (Recommended Default)

**Architecture**: Columnar; row groups contain column chunks; dictionary encoding + RLE compression per column.

```sql
CREATE TABLE sales (...) STORED AS PARQUET;
-- With explicit compression:
CREATE TABLE sales (...)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compression'='SNAPPY');
```

**Why Parquet for Impala:**
- Columnar storage → read only the columns in SELECT/WHERE (skip entire column chunks)
- Row group statistics (min/max) → skip entire row groups for range predicates
- Dictionary encoding → highly efficient for low-cardinality columns
- Deeply integrated with Impala's I/O layer (native reader)

**Parquet tuning:**
```sql
-- Set row group size (default 256 MB)
SET PARQUET_FILE_SIZE = '512m';

-- Write larger files for better compression and metadata efficiency
-- Aim for files between 256 MB and 1 GB
```

**Parquet column statistics pushdown example:**
```
Parquet file has row groups of 1M rows each.
Column `amount` has min=100, max=500 in row group 3.
WHERE amount > 1000 → entire row group 3 skipped without reading rows.
```

### ORC

**Architecture**: Similar to Parquet; columnar with stripes. Native format for Hive ACID.

```sql
CREATE TABLE hive_compat (...) STORED AS ORC;
```

- Impala can read ORC files but writes are less optimized than Parquet
- Better if tables are written by Hive with ACID and read by Impala
- Supports ACID operations (via Hive); Impala reads non-ACID ORC only

### Avro

**Architecture**: Row-based; schema embedded in file header or stored in Schema Registry.

```sql
CREATE TABLE events (
    event_id BIGINT,
    payload  STRING
)
STORED AS AVRO
TBLPROPERTIES (
    'avro.schema.literal' = '{
        "type": "record",
        "name": "Event",
        "fields": [
            {"name": "event_id", "type": "long"},
            {"name": "payload", "type": "string"}
        ]
    }'
);
-- Or point to a schema file on HDFS:
-- 'avro.schema.url' = 'hdfs:///schemas/event.avsc'
```

**When to use Avro:**
- Data produced by Kafka Connect or Flume (row-streaming systems)
- Schema evolution is important (Avro handles field additions/removals gracefully)
- Upstream systems write Avro natively

### Text (CSV/TSV)

```sql
CREATE EXTERNAL TABLE raw_orders (
    order_id INT,
    customer STRING,
    amount   DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
LOCATION '/data/raw/orders/';
```

- **No compression metadata** — Impala infers from file extension (`.gz` = gzip)
- Inefficient for analytics; use as staging only, then convert to Parquet
- NULL handling: `NULL DEFINED AS '\N'` (Hive default)

### RCFile / SequenceFile

Legacy formats; avoid for new work. Impala can read but not create RCFile tables directly (use Hive to produce, Impala to read).

---

## Compression Codecs

| Codec | Speed | Ratio | Splittable (Text) | Parquet/ORC |
|-------|-------|-------|-------------------|-------------|
| **Snappy** | Very fast | Moderate | No | Yes (block-level) |
| **LZ4** | Fastest | Moderate | No | Yes |
| **Zstd** | Fast | Good | No | Yes |
| **Gzip** | Slow | Best | No | Yes (block-level) |
| **Bzip2** | Very slow | Best | Yes | Rarely used |
| **None** | N/A | None | Yes | Yes |

**Recommendations:**
- **Parquet**: Snappy (default) or Zstd (better ratio, similar speed)
- **ORC**: Zlib (ORC default) or Snappy
- **Text for HDFS/Hive**: Avoid; if needed, use bzip2 for splittability
- **Avro**: Snappy

```sql
-- Set compression for Parquet writes
SET COMPRESSION_CODEC = snappy;
SET COMPRESSION_CODEC = zstd;
SET COMPRESSION_CODEC = none;

-- Per-table via TBLPROPERTIES
CREATE TABLE t (...) STORED AS PARQUET
TBLPROPERTIES ('parquet.compression' = 'ZSTD');
```

---

## Type Casting and Conversion

```sql
-- Explicit cast
SELECT CAST(amount AS BIGINT);
SELECT CAST('2024-01-15' AS TIMESTAMP);
SELECT CAST(ts_col AS STRING);

-- Implicit conversion (happens automatically)
-- INT → BIGINT → FLOAT → DOUBLE → DECIMAL → STRING
-- Avoid relying on implicit: make casts explicit for clarity

-- TYPEOF (Impala 3.x): return type name
SELECT TYPEOF(amount);  -- returns 'decimal(10,2)'
```

**NULL handling:**
- Any arithmetic with NULL returns NULL: `amount + NULL = NULL`
- Use `COALESCE(amount, 0)` or `IFNULL(amount, 0)` to handle NULLs
- `IS NULL` / `IS NOT NULL` predicates; do NOT use `= NULL`
