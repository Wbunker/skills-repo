# Hive Built-in Functions Reference

## Table of Contents
1. [Math Functions](#math-functions)
2. [String Functions](#string-functions)
3. [Date & Time Functions](#date--time-functions)
4. [Conditional Functions](#conditional-functions)
5. [Type Conversion](#type-conversion)
6. [Collection Functions](#collection-functions)
7. [Aggregate Functions](#aggregate-functions)
8. [Table-Generating Functions (UDTFs)](#table-generating-functions)
9. [Misc / System Functions](#misc--system-functions)

---

## Math Functions

```sql
-- Basic
ROUND(3.14159, 2)       -- 3.14
ROUND(3.5)              -- 4 (rounds half up)
FLOOR(3.7)              -- 3
CEIL(3.2) / CEILING(3.2)-- 4
ABS(-5)                 -- 5
SIGN(-3)                -- -1, SIGN(0)=0, SIGN(3)=1
POSITIVE(x)             -- x
NEGATIVE(x)             -- -x

-- Power / log
SQRT(16)                -- 4.0
POW(2, 10) / POWER(2,10)-- 1024.0
EXP(1)                  -- 2.718...
LN(2.718)               -- ~1.0 (natural log)
LOG(10, 100)            -- 2.0 (log base 10 of 100)
LOG2(8)                 -- 3.0
LOG10(1000)             -- 3.0

-- Trigonometry
SIN(x), COS(x), TAN(x)
ASIN(x), ACOS(x), ATAN(x)
ATAN2(y, x)             -- angle of (x,y) vector
DEGREES(radians)
RADIANS(degrees)
PI()                    -- 3.14159...

-- Integer arithmetic
PMOD(9, 4)              -- 1 (positive modulo, always ≥ 0)
DIV(9, 4)               -- 2 (integer division)
9 % 4                   -- 1 (modulo operator)

-- Random
RAND()                  -- 0.0 to 1.0
RAND(42)                -- seeded random (same seed = same value per row)

-- Rounding variants
BROUND(2.5)             -- 2 (banker's rounding — round half to even)
BROUND(3.5)             -- 4

-- Hex/bin
HEX(255)                -- 'ff'
UNHEX('ff')             -- binary 255
BIN(13)                 -- '1101'
CONV('ff', 16, 10)      -- '255' (convert base 16 → base 10)
```

---

## String Functions

```sql
-- Length
LENGTH('hello')          -- 5 (character length)
OCTET_LENGTH('hello')    -- 5 (byte length)

-- Case
UPPER('hello')           -- 'HELLO'
LOWER('HELLO')           -- 'hello'
INITCAP('hello world')   -- 'Hello World'  (Hive 1.1+)

-- Trim
TRIM('  hi  ')           -- 'hi'
LTRIM('  hi  ')          -- 'hi  '
RTRIM('  hi  ')          -- '  hi'

-- Pad
LPAD('hi', 5, '*')       -- '***hi'
RPAD('hi', 5, '*')       -- 'hi***'

-- Concat
CONCAT('a', 'b', 'c')    -- 'abc'
CONCAT_WS('-', 'a', 'b', 'c')  -- 'a-b-c' (skips NULLs)
CONCAT_WS(',', COLLECT_LIST(col))  -- aggregate to delimited string

-- Substring
SUBSTR('hello', 2)       -- 'ello' (1-indexed)
SUBSTR('hello', 2, 3)    -- 'ell' (start, length)
SUBSTRING_INDEX('a.b.c', '.', 2)  -- 'a.b' (first 2 parts)

-- Search
INSTR('hello', 'l')      -- 3 (first occurrence, 0 if not found)
LOCATE('l', 'hello')     -- 3
LOCATE('l', 'hello', 4)  -- 4 (start from position 4)

-- Replace
REPLACE('hello world', 'world', 'hive')  -- 'hello hive'
REGEXP_REPLACE('abc123', '[0-9]+', '')    -- 'abc'
TRANSLATE('hello', 'aeiou', '*****')      -- 'h*ll*'

-- Extract with regex
REGEXP_EXTRACT('2024-01-15', '(\\d{4})-(\\d{2})-(\\d{2})', 1)  -- '2024' (group 1)
REGEXP_EXTRACT('2024-01-15', '(\\d{4})-(\\d{2})-(\\d{2})', 0)  -- '2024-01-15' (full match)

-- Split
SPLIT('a,b,c', ',')              -- ['a','b','c'] (returns ARRAY<STRING>)
SPLIT('a,b,c', ',')[0]           -- 'a'

-- Reverse
REVERSE('hello')          -- 'olleh'

-- Repeat
REPEAT('ab', 3)           -- 'ababab'

-- Space
SPACE(5)                  -- '     '

-- String checks
STR_TO_MAP('k1=v1,k2=v2', ',', '=')   -- MAP<STRING,STRING>

-- Format
PRINTF('%05d', 42)        -- '00042'
FORMAT_NUMBER(1234567.89, 2)  -- '1,234,567.89'

-- Encoding
BASE64(binary_col)        -- base64 encode
UNBASE64(string_col)      -- base64 decode (returns BINARY)
ENCODE('hello', 'UTF-8')  -- string to BINARY
DECODE(binary_col, 'UTF-8')-- BINARY to STRING

-- ASCII / char
ASCII('A')                -- 65
CHR(65)                   -- 'A'

-- URL parsing
PARSE_URL('http://example.com/path?k=v', 'HOST')    -- 'example.com'
PARSE_URL('http://example.com/path?k=v', 'PATH')    -- '/path'
PARSE_URL('http://example.com/path?k=v', 'QUERY')   -- 'k=v'
PARSE_URL('http://example.com/path?k=v', 'QUERY', 'k') -- 'v'
-- Parts: PROTOCOL, HOST, PATH, QUERY, REF, AUTHORITY, FILE, USERINFO
```

---

## Date & Time Functions

```sql
-- Current date/time
CURRENT_DATE                        -- DATE '2024-01-15'
CURRENT_TIMESTAMP                   -- TIMESTAMP '2024-01-15 10:30:00'
NOW()                               -- alias for CURRENT_TIMESTAMP

-- Extract components
YEAR('2024-01-15')                  -- 2024
MONTH('2024-01-15')                 -- 1
DAY('2024-01-15') / DAYOFMONTH(...)-- 15
HOUR(ts), MINUTE(ts), SECOND(ts)
WEEKOFYEAR('2024-01-15')            -- 3
QUARTER('2024-04-01')               -- 2
DAYOFWEEK('2024-01-15')             -- 2 (1=Sunday ... 7=Saturday)

-- Convert
TO_DATE('2024-01-15 10:30:00')      -- DATE '2024-01-15' (extract date part)
UNIX_TIMESTAMP()                    -- current epoch seconds (INT)
UNIX_TIMESTAMP('2024-01-15 10:30:00') -- epoch of given timestamp
UNIX_TIMESTAMP('2024-01-15', 'yyyy-MM-dd') -- custom format
FROM_UNIXTIME(1705312200)           -- '2024-01-15 10:30:00'
FROM_UNIXTIME(epoch, 'yyyy-MM-dd')  -- formatted string

-- Arithmetic
DATEDIFF('2024-01-20', '2024-01-15')  -- 5 (days: end - start)
DATE_ADD('2024-01-15', 7)            -- '2024-01-22'
DATE_SUB('2024-01-15', 7)            -- '2024-01-08'
ADD_MONTHS('2024-01-31', 1)          -- '2024-02-29' (handles month-end)
MONTHS_BETWEEN('2024-03-01', '2024-01-01')  -- 2.0

-- Format
DATE_FORMAT('2024-01-15', 'yyyy/MM/dd')    -- '2024/01/15'
DATE_FORMAT(ts, 'EEE MMM dd')             -- 'Mon Jan 15'

-- Truncate (round down)
TRUNC('2024-01-15', 'MM')           -- '2024-01-01' (first of month)
TRUNC('2024-01-15', 'YYYY')         -- '2024-01-01' (first of year)
TRUNC('2024-01-15', 'DD')           -- '2024-01-15' (day, same as TO_DATE)
DATE_TRUNC('MONTH', ts)             -- Hive 3+, similar to TRUNC

-- End/next day
LAST_DAY('2024-01-15')              -- '2024-01-31'
NEXT_DAY('2024-01-15', 'MONDAY')    -- '2024-01-22' (next Monday)

-- Timezone (Hive 2+)
CONVERT_TZ(ts, 'UTC', 'America/New_York')  -- convert timezone
FROM_UTC_TIMESTAMP(ts, 'America/New_York') -- UTC → local
TO_UTC_TIMESTAMP(ts, 'America/New_York')   -- local → UTC
```

---

## Conditional Functions

```sql
-- IF
IF(amount > 100, 'large', 'small')
IF(col IS NULL, 'default', col)

-- CASE WHEN
CASE status
  WHEN 'pending'  THEN 1
  WHEN 'shipped'  THEN 2
  WHEN 'delivered'THEN 3
  ELSE 0
END

CASE
  WHEN amount > 1000 THEN 'premium'
  WHEN amount > 100  THEN 'standard'
  ELSE 'small'
END AS tier

-- COALESCE (returns first non-NULL)
COALESCE(col1, col2, col3, 'default')

-- NVL (2-arg COALESCE)
NVL(col, 'default')
NVL2(col, 'not_null_val', 'null_val')  -- IF col IS NOT NULL THEN ... ELSE ...

-- NULLIF (returns NULL if equal)
NULLIF(amount, 0)          -- returns NULL if amount=0 (avoid division by zero)
amount / NULLIF(divisor, 0)-- safe division

-- DECODE (Oracle-style equality check)
DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown')

-- IIF (alias for IF in some contexts)
IIF(condition, true_val, false_val)

-- ASSERT_TRUE (throws exception if false — useful in data validation)
ASSERT_TRUE(amount >= 0)

-- GREATEST / LEAST
GREATEST(a, b, c)          -- max of values (ignores NULLs)
LEAST(a, b, c)             -- min of values (ignores NULLs)
```

---

## Type Conversion

```sql
CAST(col AS BIGINT)
CAST(col AS DECIMAL(18,4))
CAST(col AS STRING)
CAST(col AS BOOLEAN)
CAST(col AS TIMESTAMP)      -- from 'yyyy-MM-dd HH:mm:ss' string
CAST(col AS DATE)           -- from 'yyyy-MM-dd' string or TIMESTAMP
CAST(col AS BINARY)
CAST(col AS FLOAT)

-- Implicit: Hive widens automatically in comparisons
-- 1 = '1' → TRUE (STRING coerced to numeric)

-- String to number: fails quietly (returns NULL) on bad input
CAST('abc' AS INT)          -- NULL
CAST('3.14' AS DOUBLE)      -- 3.14
```

---

## Collection Functions

```sql
-- Array
SIZE(array_col)                    -- length (-1 if NULL)
ARRAY_CONTAINS(col, 'value')       -- BOOLEAN
SORT_ARRAY(col)                    -- sorted copy (ascending)
SORT_ARRAY(col, false)             -- descending sort (Hive 2.4+)
REVERSE(array_col)                 -- reversed array
ARRAY(1, 2, 3)                     -- create array literal
ARRAY_DISTINCT(col)                -- remove duplicates (Hive 2.1+)
ARRAY_UNION(a1, a2)                -- union two arrays (Hive 3.1+)
ARRAY_INTERSECT(a1, a2)            -- intersection (Hive 3.1+)
ARRAY_EXCEPT(a1, a2)               -- elements in a1 not in a2 (Hive 3.1+)
SLICE(col, 2, 3)                   -- elements 2–4 (Hive 3.1+)

-- Map
SIZE(map_col)                      -- entry count
MAP_KEYS(col)                      -- ARRAY<K>
MAP_VALUES(col)                    -- ARRAY<V>
MAP(k1, v1, k2, v2)               -- create map literal

-- Struct
STRUCT(val1, val2)                 -- positional struct
NAMED_STRUCT('a', 1, 'b', 'x')    -- named struct
```

---

## Aggregate Functions

```sql
-- Standard
COUNT(*)                    -- all rows including NULLs
COUNT(col)                  -- non-NULL rows
COUNT(DISTINCT col)
SUM(amount)
AVG(amount)
MIN(amount), MAX(amount)
MIN_BY(col, order_col)      -- value of col where order_col is minimum (Hive 4+)
MAX_BY(col, order_col)      -- value of col where order_col is maximum (Hive 4+)

-- Statistical
VARIANCE(col) / VAR_POP(col)    -- population variance
VAR_SAMP(col)                   -- sample variance
STDDEV_POP(col)                 -- population std dev
STDDEV(col) / STDDEV_SAMP(col)  -- sample std dev
COVAR_POP(x, y)                 -- population covariance
COVAR_SAMP(x, y)                -- sample covariance
CORR(x, y)                      -- Pearson correlation coefficient

-- Percentile
PERCENTILE(col, 0.5)            -- exact median (works on INTEGER only)
PERCENTILE(col, ARRAY(0.25, 0.5, 0.75))  -- multiple percentiles
PERCENTILE_APPROX(col, 0.5)     -- approximate (works on DOUBLE, faster)
PERCENTILE_APPROX(col, 0.5, 1000)  -- 1000 = accuracy (higher = more accurate)

-- Histogram
HISTOGRAM_NUMERIC(col, 10)      -- 10-bin histogram; returns ARRAY<STRUCT<x,y>>

-- Collection aggregates
COLLECT_LIST(col)               -- ARRAY of all values (preserves duplicates)
COLLECT_SET(col)                -- ARRAY of distinct values (no guaranteed order)

-- String aggregation
CONCAT_WS(',', COLLECT_LIST(col))   -- comma-delimited string of values (common pattern)

-- Conditional aggregates
SUM(IF(status='shipped', amount, 0))          -- conditional sum
COUNT(IF(status='pending', 1, NULL))          -- conditional count
SUM(CASE WHEN region='us' THEN amount END)    -- CASE in aggregate
```

---

## Table-Generating Functions

Used with `LATERAL VIEW` to produce multiple rows from one:

```sql
-- EXPLODE array → one row per element
LATERAL VIEW EXPLODE(tags) t AS tag

-- EXPLODE map → one row per key-value pair
LATERAL VIEW EXPLODE(attrs) a AS attr_key, attr_value

-- POSEXPLODE → adds position index (0-based)
LATERAL VIEW POSEXPLODE(tags) t AS pos, tag

-- INLINE → explode array of structs (one row per struct, columns per field)
LATERAL VIEW INLINE(items) i AS item_id, qty, price

-- STACK(n, v1, v2, ...) → n rows from list of values
SELECT stack(3, 'a', 1, 'b', 2, 'c', 3) AS (letter, num);

-- JSON_TUPLE → extract multiple JSON fields at once
LATERAL VIEW JSON_TUPLE(json_col, 'id', 'name', 'ts') j AS id, name, ts

-- PARSE_URL_TUPLE → extract multiple URL components
LATERAL VIEW PARSE_URL_TUPLE(url_col, 'HOST', 'PATH', 'QUERY:id') p AS host, path, id

-- OUTER modifier (keep rows with empty/NULL collections)
LATERAL VIEW OUTER EXPLODE(tags) t AS tag
```

---

## Misc / System Functions

```sql
-- Identity and session
CURRENT_USER()          -- 'alice'
CURRENT_DATABASE()      -- 'mydb'
LOGGED_IN_USER()        -- actual login user (may differ from current_user in delegation)
VERSION()               -- Hive version string

-- Hashing
HASH(col)               -- integer hash code
MD5(col)                -- MD5 hex string
SHA1(col) / SHA(col)    -- SHA-1 hex string
SHA2(col, 256)          -- SHA-2 (256-bit); bits: 224, 256, 384, 512
CRC32(col)              -- CRC32 checksum

-- Encryption (Hive 2.1+)
AES_ENCRYPT(col, key)   -- returns BINARY
AES_DECRYPT(col, key)   -- returns BINARY

-- Data masking (Hive 3.1+, often used with Ranger)
MASK(col)                           -- 'XxXxXx' style mask
MASK_FIRST_N(col, 4)               -- mask first 4 chars
MASK_LAST_N(col, 4)                -- mask last 4 chars
MASK_SHOW_FIRST_N(col, 4)          -- show first 4, mask rest
MASK_SHOW_LAST_N(col, 4)           -- show last 4, mask rest
MASK_HASH(col)                     -- consistent hash-based mask

-- JSON
GET_JSON_OBJECT(json_col, '$.field')         -- extract by JSONPath
GET_JSON_OBJECT(json_col, '$.arr[0].name')   -- nested path

-- Misc
REFLECT('java.lang.Math', 'abs', -5)   -- call Java method
UUID()                                  -- generate random UUID (Hive 4.0+)
NULLIF(a, b)                            -- NULL if a=b, else a
```
