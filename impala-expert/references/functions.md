# Impala Functions Reference
## Chapter 6: Built-in Functions, Aggregate Functions, Analytic/Window Functions, UDFs/UDAs

---

## String Functions

| Function | Example | Result |
|----------|---------|--------|
| `CONCAT(s1, s2, ...)` | `CONCAT('Hello', ' ', 'World')` | `'Hello World'` |
| `CONCAT_WS(sep, s1, s2, ...)` | `CONCAT_WS('-', '2024', '01', '15')` | `'2024-01-15'` |
| `LENGTH(s)` | `LENGTH('hello')` | `5` |
| `UPPER(s)` | `UPPER('hello')` | `'HELLO'` |
| `LOWER(s)` | `LOWER('HELLO')` | `'hello'` |
| `TRIM(s)` | `TRIM('  hi  ')` | `'hi'` |
| `LTRIM(s)` | `LTRIM('  hi')` | `'hi'` |
| `RTRIM(s)` | `RTRIM('hi  ')` | `'hi'` |
| `SUBSTR(s, pos, len)` | `SUBSTR('hello', 2, 3)` | `'ell'` |
| `SUBSTRING(s, pos)` | `SUBSTRING('hello', 3)` | `'llo'` |
| `REPLACE(s, old, new)` | `REPLACE('a.b.c', '.', '-')` | `'a-b-c'` |
| `REGEXP_REPLACE(s, pattern, repl)` | `REGEXP_REPLACE(s, '[0-9]+', '#')` | replace all digits |
| `REGEXP_EXTRACT(s, pattern, group)` | `REGEXP_EXTRACT('abc123', '([0-9]+)', 1)` | `'123'` |
| `SPLIT_PART(s, delimiter, n)` | `SPLIT_PART('a/b/c', '/', 2)` | `'b'` |
| `LPAD(s, len, pad)` | `LPAD('42', 5, '0')` | `'00042'` |
| `RPAD(s, len, pad)` | `RPAD('hi', 5, '.')` | `'hi...'` |
| `REVERSE(s)` | `REVERSE('hello')` | `'olleh'` |
| `INSTR(s, sub)` | `INSTR('hello world', 'world')` | `7` |
| `LOCATE(sub, s[, pos])` | `LOCATE('lo', 'hello')` | `4` |
| `REPEAT(s, n)` | `REPEAT('ab', 3)` | `'ababab'` |
| `SPACE(n)` | `SPACE(3)` | `'   '` |
| `INITCAP(s)` | `INITCAP('hello world')` | `'Hello World'` |
| `STRLEFT(s, n)` | `STRLEFT('hello', 3)` | `'hel'` |
| `STRRIGHT(s, n)` | `STRRIGHT('hello', 3)` | `'llo'` |

---

## Numeric Functions

| Function | Description |
|----------|-------------|
| `ABS(x)` | Absolute value |
| `CEIL(x)` / `CEILING(x)` | Round up to integer |
| `FLOOR(x)` | Round down to integer |
| `ROUND(x, d)` | Round to d decimal places |
| `TRUNCATE(x, d)` | Truncate to d decimal places (no rounding) |
| `MOD(x, y)` | Modulo (x % y) |
| `POWER(x, p)` | x raised to the power p |
| `SQRT(x)` | Square root |
| `EXP(x)` | e^x |
| `LN(x)` | Natural logarithm |
| `LOG(base, x)` | Logarithm with given base |
| `LOG2(x)` / `LOG10(x)` | Log base 2 / 10 |
| `SIGN(x)` | -1, 0, or 1 |
| `GREATEST(a, b, ...)` | Maximum of arguments |
| `LEAST(a, b, ...)` | Minimum of arguments |
| `FMOD(x, y)` | Floating-point modulo |
| `RANDOM()` / `RAND()` | Random double 0.0–1.0 |
| `PI()` | 3.14159... |
| `E()` | 2.71828... |
| `BIN(n)` | Integer to binary string |
| `HEX(n)` | Integer to hex string |
| `UNHEX(s)` | Hex string to binary |
| `CONV(n, from_base, to_base)` | Base conversion |
| `PMOD(x, y)` | Positive modulo (always ≥ 0) |

---

## Date and Time Functions

```sql
-- Current date/time
NOW()                    -- current datetime as TIMESTAMP
CURRENT_TIMESTAMP()      -- same as NOW()
CURRENT_DATE()           -- current date (DATE type)
UNIX_TIMESTAMP()         -- current Unix epoch seconds

-- Extract components
YEAR(ts)                 -- 2024
MONTH(ts)                -- 1–12
DAY(ts) / DAYOFMONTH(ts) -- 1–31
HOUR(ts)                 -- 0–23
MINUTE(ts)               -- 0–59
SECOND(ts)               -- 0–59
DAYOFWEEK(ts)            -- 1=Sunday, 7=Saturday
DAYOFYEAR(ts)            -- 1–366
WEEKOFYEAR(ts)           -- 1–53
QUARTER(ts)              -- 1–4

-- Date arithmetic
DATE_ADD(ts, INTERVAL n unit)    -- add interval
DATE_SUB(ts, INTERVAL n unit)    -- subtract interval
DATEDIFF(end_ts, start_ts)       -- days between two timestamps
DAYS_ADD(ts, n)                  -- add n days
DAYS_SUB(ts, n)                  -- subtract n days
MONTHS_ADD(ts, n)                -- add n months
MONTHS_SUB(ts, n)                -- subtract n months
YEARS_ADD(ts, n)
HOURS_ADD(ts, n)
MINUTES_ADD(ts, n)
SECONDS_ADD(ts, n)

-- Formatting and parsing
TO_DATE(ts)                      -- extract DATE part as STRING 'YYYY-MM-DD'
FROM_UNIXTIME(epoch)             -- epoch → TIMESTAMP
UNIX_TIMESTAMP(ts)               -- TIMESTAMP → epoch
DATE_FORMAT(ts, format)          -- format timestamp (MySQL-style format strings)
-- Example: DATE_FORMAT(NOW(), 'yyyy-MM-dd') → '2024-01-15'

-- Truncation
TRUNC(ts, unit)                  -- truncate to unit ('YYYY','MM','DD','HH','MI')
-- TRUNC(NOW(), 'MM') → first day of current month
DATE_TRUNC(unit, ts)             -- Postgres-style; TRUNC equivalent

-- Timezone
FROM_UTC_TIMESTAMP(ts, tz)       -- convert from UTC to local tz
TO_UTC_TIMESTAMP(ts, tz)         -- convert local tz to UTC
-- Example: FROM_UTC_TIMESTAMP(event_time, 'America/New_York')
```

---

## Conditional and NULL-Handling Functions

```sql
-- CASE expressions
CASE WHEN condition THEN result
     WHEN condition THEN result
     ELSE default_result
END

CASE expression
    WHEN value1 THEN result1
    WHEN value2 THEN result2
    ELSE default
END

-- NULL-handling
COALESCE(a, b, c, ...)    -- first non-NULL value
IFNULL(expr, default)     -- return default if expr is NULL (alias: NVL)
NULLIF(a, b)              -- return NULL if a = b; else return a
IF(cond, true_val, false_val)   -- ternary IF
IIF(cond, true_val, false_val)  -- alias for IF
ISNULL(expr)              -- 1 if NULL, 0 if not (use IS NULL in predicates)

-- Type-safe comparisons
DECODE(expr, val1, res1, val2, res2, ..., default)  -- Oracle-style CASE
ZEROIFNULL(expr)          -- return 0 if NULL
NULLIFZERO(expr)          -- return NULL if 0
```

---

## Type Conversion Functions

```sql
CAST(expr AS type)                    -- explicit cast
TYPEOF(expr)                          -- return type name as string (Impala 3.x+)

-- String ↔ numeric
CAST('123' AS INT)
CAST(order_id AS STRING)

-- String ↔ timestamp
CAST('2024-01-15 10:30:00' AS TIMESTAMP)
CAST(ts AS STRING)

-- Numeric precision
CAST(amount AS DECIMAL(10,2))

-- PARSE_URL: extract component from URL string
PARSE_URL(url, 'HOST')
PARSE_URL(url, 'PATH')
PARSE_URL(url, 'QUERY')
PARSE_URL(url, 'QUERY', 'key')   -- extract specific query param
```

---

## Aggregate Functions

```sql
-- Standard aggregates
COUNT(*)                  -- all rows
COUNT(col)                -- non-NULL values only
COUNT(DISTINCT col)       -- distinct non-NULL values (exact; can be slow)
SUM(col)
AVG(col)
MIN(col)
MAX(col)

-- Approximate aggregates (much faster at scale)
NDV(col)                  -- approximate count distinct (uses HyperLogLog)
APPX_MEDIAN(col)          -- approximate median
STDDEV(col) / STDDEV_SAMP(col)
VARIANCE(col) / VAR_SAMP(col)

-- Aggregating into collections
GROUP_CONCAT(col)                         -- concatenate values with comma
GROUP_CONCAT(col, separator)              -- with custom separator
GROUP_CONCAT(col ORDER BY col2 SEPARATOR ',')

-- Conditional aggregation
COUNT(IF(status = 'active', 1, NULL))    -- count matching rows
SUM(IF(region = 'US', amount, 0))        -- conditional sum
MAX(IF(type = 'premium', revenue, NULL)) -- conditional max
```

---

## Analytic (Window) Functions

Window functions compute values across a "window" of rows relative to each current row — without collapsing rows like GROUP BY does.

### Syntax

```sql
function_name(args) OVER (
    [PARTITION BY partition_expr, ...]
    [ORDER BY order_expr [ASC|DESC] [NULLS FIRST|LAST], ...]
    [ROWS|RANGE BETWEEN frame_start AND frame_end]
)
```

### Ranking Functions

```sql
-- ROW_NUMBER: unique sequential number per partition
SELECT customer_id, order_date, amount,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn
FROM orders;

-- RANK: same rank for ties; gaps after ties
SELECT customer_id, amount,
       RANK() OVER (ORDER BY amount DESC) AS rank_pos
FROM orders;

-- DENSE_RANK: same rank for ties; no gaps
SELECT customer_id, amount,
       DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank_pos
FROM orders;

-- NTILE: assign rows to n buckets
SELECT customer_id, amount,
       NTILE(4) OVER (ORDER BY amount DESC) AS quartile
FROM orders;
-- quartile 1 = top 25%, 4 = bottom 25%

-- PERCENT_RANK: relative rank 0.0 to 1.0
-- CUME_DIST: cumulative distribution 0.0 to 1.0
```

### Lead and Lag

```sql
-- LAG: access previous row's value
SELECT order_date, amount,
       LAG(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_amount,
       amount - LAG(amount, 1, 0) OVER (PARTITION BY customer_id ORDER BY order_date) AS delta
FROM orders;

-- LEAD: access next row's value
SELECT order_date, amount,
       LEAD(amount, 1) OVER (ORDER BY order_date) AS next_amount
FROM orders;

-- LAG(col, offset, default_if_null)
```

### Running Totals and Moving Averages

```sql
-- Running total within partition
SELECT customer_id, order_date, amount,
       SUM(amount) OVER (
           PARTITION BY customer_id
           ORDER BY order_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders;

-- 7-day moving average
SELECT dt, revenue,
       AVG(revenue) OVER (
           ORDER BY dt
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS avg_7day
FROM daily_revenue;

-- First and last value in window
FIRST_VALUE(col) OVER (PARTITION BY ... ORDER BY ...)
LAST_VALUE(col)  OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
```

### Frame Clauses

| Frame | Meaning |
|-------|---------|
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | All rows from partition start to current row |
| `ROWS BETWEEN 3 PRECEDING AND CURRENT ROW` | Current row + 3 preceding rows |
| `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` | 3-row sliding window |
| `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING` | Current row to end of partition |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | Entire partition |

---

## User-Defined Functions (UDFs and UDAs)

### C++ UDFs (Recommended for Performance)

```cpp
// my_udf.cc
#include <udf/udf.h>
using namespace impala_udf;

StringVal MyUpper(FunctionContext* ctx, const StringVal& input) {
    if (input.is_null) return StringVal::null();
    StringVal result(ctx, input.len);
    for (int i = 0; i < input.len; ++i)
        result.ptr[i] = toupper(input.ptr[i]);
    return result;
}
```

```sql
-- Register the UDF
CREATE FUNCTION my_upper(STRING) RETURNS STRING
LOCATION '/user/impala/udfs/my_udf.so'
SYMBOL='MyUpper';

-- Use it
SELECT my_upper(name) FROM customers;

-- Drop it
DROP FUNCTION my_upper(STRING);
```

### Java UDFs (Simpler; Slower than C++)

```java
// MyUDF.java
import com.cloudera.impala.extdatasource.thrift.TGetNextParams;
import org.apache.hadoop.hive.ql.exec.UDF;
import org.apache.hadoop.io.Text;

public class MyUpperUDF extends UDF {
    public Text evaluate(Text input) {
        if (input == null) return null;
        return new Text(input.toString().toUpperCase());
    }
}
```

```sql
CREATE FUNCTION my_upper_java(STRING) RETURNS STRING
LOCATION '/user/impala/udfs/myudf.jar'
SYMBOL='com.example.MyUpperUDF';
```

### UDAs (User-Defined Aggregates)

UDAs require init, update, merge, serialize/deserialize, and finalize functions — a C++ implementation is strongly recommended. Used for custom aggregation logic not covered by built-in aggregates.

```sql
CREATE AGGREGATE FUNCTION my_sum(DOUBLE) RETURNS DOUBLE
LOCATION '/user/impala/udas/my_uda.so'
UPDATE_FN='MyUpdate'
INIT_FN='MyInit'
MERGE_FN='MyMerge'
FINALIZE_FN='MyFinalize';
```

### UDF Best Practices

- Register UDFs per database (or in a shared library database for org-wide functions)
- C++ UDFs are 10–100x faster than Java UDFs for tight loops
- Handle NULL inputs explicitly — always check `input.is_null`
- Allocate output buffers with `ctx->Allocate()` — Impala manages memory lifecycle
- Store `.so` / `.jar` files on HDFS, accessible to all impalad nodes
