# Creating and Managing Snowflake Securable Database Objects

Reference for databases, schemas, tables, views, stages, UDFs, stored procedures, streams, and tasks.

## Table of Contents
- [Databases and Schemas](#databases-and-schemas)
- [Tables](#tables)
- [Views](#views)
- [Stages and File Formats](#stages-and-file-formats)
- [UDFs and Stored Procedures](#udfs-and-stored-procedures)
- [Streams](#streams)
- [Tasks](#tasks)
- [Sequences and Pipes](#sequences-and-pipes)

## Databases and Schemas

### Creating Databases
```sql
CREATE DATABASE my_db
  COMMENT = 'Production database'
  DATA_RETENTION_TIME_IN_DAYS = 30;

-- Transient database (no fail-safe, lower storage cost)
CREATE TRANSIENT DATABASE staging_db;

-- From share
CREATE DATABASE shared_db FROM SHARE provider_account.share_name;

-- Clone
CREATE DATABASE dev_db CLONE prod_db;
```

### Creating Schemas
```sql
CREATE SCHEMA my_db.analytics
  COMMENT = 'Analytics mart'
  DATA_RETENTION_TIME_IN_DAYS = 14;

CREATE TRANSIENT SCHEMA my_db.staging;

-- Managed access schema (only schema owner can grant privileges)
CREATE SCHEMA my_db.secure_data WITH MANAGED ACCESS;
```

### INFORMATION_SCHEMA (Database-level metadata)
```sql
-- Available in every database
SELECT * FROM my_db.INFORMATION_SCHEMA.TABLES;
SELECT * FROM my_db.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'MY_TABLE';
SELECT * FROM my_db.INFORMATION_SCHEMA.VIEWS;
SELECT * FROM my_db.INFORMATION_SCHEMA.STAGES;
SELECT * FROM my_db.INFORMATION_SCHEMA.TABLE_PRIVILEGES;

-- Limitations: only covers current database, limited to recent 14 days for some views
```

### ACCOUNT_USAGE Schema (Account-level metadata)
```sql
-- In the shared SNOWFLAKE database (requires ACCOUNTADMIN or granted access)
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE;

-- Up to 365 days of history; 45-minute to 3-hour latency
```

## Tables

### Table Types

| Type | Time Travel | Fail-Safe | Use Case |
|------|------------|-----------|----------|
| **Permanent** | Up to 90 days | 7 days | Production data |
| **Transient** | 0 or 1 day | None | Staging, temp data |
| **Temporary** | 0 or 1 day | None | Session-scoped; dropped at session end |
| **External** | None | None | Query data in external cloud storage |

```sql
-- Permanent table (default)
CREATE TABLE customers (
  customer_id INT AUTOINCREMENT,
  name STRING NOT NULL,
  email STRING,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Transient table
CREATE TRANSIENT TABLE staging_orders (
  raw_data VARIANT
);

-- Temporary table (session-scoped)
CREATE TEMPORARY TABLE temp_results AS
SELECT * FROM orders WHERE order_date = CURRENT_DATE();

-- External table
CREATE EXTERNAL TABLE ext_logs (
  log_date DATE AS (VALUE:log_date::DATE),
  message STRING AS (VALUE:message::STRING)
)
WITH LOCATION = @my_stage/logs/
FILE_FORMAT = (TYPE = 'PARQUET')
AUTO_REFRESH = TRUE;

-- CTAS (Create Table As Select)
CREATE TABLE summary AS
SELECT region, SUM(amount) AS total
FROM sales
GROUP BY region;

-- Clone
CREATE TABLE test_orders CLONE orders;
```

### Common DDL
```sql
-- Add column
ALTER TABLE customers ADD COLUMN phone STRING;

-- Rename column
ALTER TABLE customers RENAME COLUMN phone TO phone_number;

-- Drop column
ALTER TABLE customers DROP COLUMN phone_number;

-- Change column type (limited)
ALTER TABLE customers ALTER COLUMN name SET DATA TYPE VARCHAR(500);

-- Add comment
COMMENT ON TABLE customers IS 'Master customer table';

-- Swap tables (atomic)
ALTER TABLE customers_new SWAP WITH customers;

-- Truncate
TRUNCATE TABLE staging_orders;
```

## Views

### Standard View
```sql
CREATE VIEW active_customers AS
SELECT customer_id, name, email
FROM customers
WHERE status = 'active';
```

### Secure View (hides DDL from non-owners)
```sql
CREATE SECURE VIEW revenue_by_region AS
SELECT region, SUM(amount) AS total_revenue
FROM orders
GROUP BY region;
-- Query plan is not exposed to viewers
-- Used for data sharing and security
```

### Materialized View (Enterprise+)
```sql
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT sale_date, region, SUM(amount) AS daily_total
FROM sales
GROUP BY sale_date, region;

-- Auto-maintained by Snowflake (background service)
-- Costs credits for maintenance
-- Ideal for expensive aggregations queried frequently
```

## Stages and File Formats

### Stage Types

| Stage | Location | Use |
|-------|----------|-----|
| **User** (`@~`) | Per-user internal | Individual file uploads |
| **Table** (`@%table`) | Per-table internal | Direct table loading |
| **Named Internal** | Shared internal | Team/pipeline use |
| **Named External** | S3/Blob/GCS | External data loading |

```sql
-- Named internal stage
CREATE STAGE my_internal_stage
  FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1);

-- Named external stage (S3)
CREATE STAGE my_s3_stage
  URL = 's3://my-bucket/data/'
  STORAGE_INTEGRATION = my_s3_integration
  FILE_FORMAT = (TYPE = 'PARQUET');

-- Named external stage (Azure)
CREATE STAGE my_azure_stage
  URL = 'azure://myaccount.blob.core.windows.net/container/path/'
  STORAGE_INTEGRATION = my_azure_integration;

-- Named external stage (GCS)
CREATE STAGE my_gcs_stage
  URL = 'gcs://my-bucket/data/'
  STORAGE_INTEGRATION = my_gcs_integration;
```

### File Formats
```sql
-- Create reusable file format
CREATE FILE FORMAT csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('NULL', 'null', '')
  EMPTY_FIELD_AS_NULL = TRUE
  COMPRESSION = 'AUTO';

CREATE FILE FORMAT json_format
  TYPE = 'JSON'
  STRIP_OUTER_ARRAY = TRUE
  COMPRESSION = 'AUTO';

CREATE FILE FORMAT parquet_format
  TYPE = 'PARQUET'
  COMPRESSION = 'SNAPPY';

-- List files in stage
LIST @my_stage;
LIST @my_stage/subfolder/;
```

## UDFs and Stored Procedures

### SQL UDF
```sql
CREATE FUNCTION celsius_to_fahrenheit(c FLOAT)
  RETURNS FLOAT
  AS $$ c * 9/5 + 32 $$;

SELECT celsius_to_fahrenheit(100);  -- 212
```

### JavaScript UDF
```sql
CREATE FUNCTION parse_user_agent(ua STRING)
  RETURNS VARIANT
  LANGUAGE JAVASCRIPT
  AS $$
    var result = {};
    if (UA.includes("Chrome")) result.browser = "Chrome";
    else if (UA.includes("Firefox")) result.browser = "Firefox";
    else result.browser = "Other";
    return result;
  $$;
```

### SQL Table Function (UDTF)
```sql
CREATE FUNCTION split_to_rows(input STRING, delimiter STRING)
  RETURNS TABLE(value STRING)
  AS $$
    SELECT VALUE FROM TABLE(SPLIT_TO_TABLE(input, delimiter))
  $$;

SELECT * FROM TABLE(split_to_rows('a,b,c', ','));
```

### Stored Procedure (JavaScript)
```sql
CREATE PROCEDURE load_daily_data(target_date STRING)
  RETURNS STRING
  LANGUAGE JAVASCRIPT
  EXECUTE AS CALLER
  AS $$
    var sql = `COPY INTO my_table FROM @my_stage/dt=${TARGET_DATE}/
               FILE_FORMAT = (TYPE = 'PARQUET')`;
    snowflake.execute({sqlText: sql});
    return 'Load complete for ' + TARGET_DATE;
  $$;

CALL load_daily_data('2024-01-15');
```

### Stored Procedure (Snowflake Scripting / SQL)
```sql
CREATE PROCEDURE cleanup_old_data(days_to_keep INT)
  RETURNS STRING
  LANGUAGE SQL
  AS
  $$
  BEGIN
    DELETE FROM staging_table WHERE created_at < DATEADD('DAY', -:days_to_keep, CURRENT_DATE());
    RETURN 'Cleanup complete';
  END;
  $$;
```

## Streams

Streams track DML changes (inserts, updates, deletes) on tables — used for CDC (Change Data Capture).

```sql
-- Create stream on a table
CREATE STREAM orders_stream ON TABLE orders;

-- Query the stream (shows changes since last DML consumption)
SELECT * FROM orders_stream;
-- Columns: all original columns + METADATA$ACTION, METADATA$ISUPDATE, METADATA$ROW_ID

-- Consume stream (any DML referencing the stream advances the offset)
INSERT INTO orders_history
SELECT *, CURRENT_TIMESTAMP() AS loaded_at
FROM orders_stream
WHERE METADATA$ACTION = 'INSERT';

-- Stream types
CREATE STREAM s1 ON TABLE t1;                    -- Standard (default, tracks all DML)
CREATE STREAM s1 ON TABLE t1 APPEND_ONLY = TRUE; -- Append-only (inserts only, more efficient)

-- Check if stream has data
SELECT SYSTEM$STREAM_HAS_DATA('orders_stream');
```

## Tasks

Tasks schedule SQL execution (like cron jobs within Snowflake).

```sql
-- Simple scheduled task
CREATE TASK daily_summary_task
  WAREHOUSE = ETL_WH
  SCHEDULE = 'USING CRON 0 6 * * * America/New_York'  -- 6am ET daily
  AS
  INSERT INTO daily_summary
  SELECT CURRENT_DATE(), COUNT(*), SUM(amount) FROM orders WHERE order_date = CURRENT_DATE();

-- Task with stream dependency (runs only when stream has data)
CREATE TASK process_orders_task
  WAREHOUSE = ETL_WH
  SCHEDULE = '5 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')
  AS
  INSERT INTO orders_history SELECT * FROM orders_stream;

-- Task tree (parent → child)
CREATE TASK child_task
  WAREHOUSE = ETL_WH
  AFTER parent_task
  AS
  CALL refresh_materialized_tables();

-- Enable/disable tasks (tasks are created suspended by default)
ALTER TASK daily_summary_task RESUME;
ALTER TASK daily_summary_task SUSPEND;

-- View task history
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
ORDER BY SCHEDULED_TIME DESC;
```

### CRON Syntax
```
USING CRON <min> <hour> <day_of_month> <month> <day_of_week> <timezone>
-- Examples:
'USING CRON 0 6 * * * America/New_York'   -- 6am ET daily
'USING CRON 0 */2 * * * UTC'               -- every 2 hours
'USING CRON 0 8 * * MON UTC'               -- 8am UTC every Monday
```

## Sequences and Pipes

### Sequences
```sql
CREATE SEQUENCE order_seq START = 1 INCREMENT = 1;
SELECT order_seq.NEXTVAL;

-- Use in INSERT
INSERT INTO orders (order_id, product)
VALUES (order_seq.NEXTVAL, 'Widget');
```

### Pipes (continuous data loading — see Chapter 6 for detail)
```sql
CREATE PIPE my_pipe
  AUTO_INGEST = TRUE
  AS
  COPY INTO my_table FROM @my_stage
  FILE_FORMAT = (TYPE = 'JSON');

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('my_pipe');
```
