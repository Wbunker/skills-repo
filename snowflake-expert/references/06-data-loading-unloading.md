# Data Loading and Unloading

Reference for loading data into and unloading data from Snowflake.

## Table of Contents
- [Data Loading Overview](#data-loading-overview)
- [COPY INTO (Loading)](#copy-into-loading)
- [Snowpipe (Continuous Loading)](#snowpipe-continuous-loading)
- [PUT Command](#put-command)
- [Bulk Loading Patterns](#bulk-loading-patterns)
- [Unloading Data](#unloading-data)
- [Data Loading Best Practices](#data-loading-best-practices)

## Data Loading Overview

### Loading Methods

| Method | Use Case | Automation |
|--------|----------|-----------|
| **COPY INTO** | Bulk batch loading | Scheduled via tasks |
| **Snowpipe** | Continuous streaming | Event-driven (auto-ingest) |
| **INSERT INTO** | Small ad-hoc inserts | Manual |
| **Web UI** | Small file uploads | Manual |
| **SnowSQL PUT + COPY** | Local files to internal stage | CLI |
| **Snowflake Connector** | Spark, Kafka, Python | Application-level |
| **Third-party ETL** | Fivetran, Airbyte, dbt | Tool-dependent |

### Supported File Formats
- **Structured:** CSV, TSV, delimited text
- **Semi-structured:** JSON, Avro, Parquet, ORC, XML

### Compression Support
```
AUTO (default) — Snowflake auto-detects
GZIP, BZ2, BROTLI, ZSTD, DEFLATE, RAW_DEFLATE, LZO (Hadoop), SNAPPY (Parquet), NONE
```

## COPY INTO (Loading)

### Basic COPY INTO
```sql
-- From external stage
COPY INTO my_table
FROM @my_s3_stage/path/
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';

-- From named file format
COPY INTO my_table
FROM @my_stage
FILE_FORMAT = my_csv_format
PATTERN = '.*2024.*\\.csv\\.gz';

-- With transformations during load
COPY INTO my_table (col1, col2, col3, load_ts)
FROM (
  SELECT $1, $2, $3::NUMBER, CURRENT_TIMESTAMP()
  FROM @my_stage
)
FILE_FORMAT = (TYPE = 'CSV');
```

### COPY INTO Options
```sql
COPY INTO my_table FROM @my_stage
  FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = '|' SKIP_HEADER = 1)
  PATTERN = '.*\\.csv'               -- file name pattern
  FILES = ('file1.csv', 'file2.csv') -- specific files
  ON_ERROR = 'CONTINUE'              -- CONTINUE | SKIP_FILE | SKIP_FILE_n | ABORT_STATEMENT
  SIZE_LIMIT = 5000000000            -- bytes, stop after limit
  PURGE = TRUE                       -- delete files after successful load
  FORCE = TRUE                       -- reload previously loaded files
  MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'  -- for semi-structured
  VALIDATION_MODE = 'RETURN_ERRORS'; -- dry run, don't actually load
```

### Loading JSON
```sql
-- Into VARIANT column
CREATE TABLE events (raw VARIANT);

COPY INTO events
FROM @my_stage
FILE_FORMAT = (TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE);

-- Into relational columns (transformation)
COPY INTO events_flat (event_id, user_id, action, ts)
FROM (
  SELECT
    $1:event_id::INT,
    $1:user_id::STRING,
    $1:action::STRING,
    $1:timestamp::TIMESTAMP_NTZ
  FROM @my_stage
)
FILE_FORMAT = (TYPE = 'JSON');
```

### Loading Parquet
```sql
COPY INTO my_table
FROM @my_stage
FILE_FORMAT = (TYPE = 'PARQUET')
MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE';

-- Or with explicit column mapping
COPY INTO my_table (id, name, amount)
FROM (
  SELECT $1:id::INT, $1:name::STRING, $1:amount::FLOAT
  FROM @my_stage
)
FILE_FORMAT = (TYPE = 'PARQUET');
```

### Validating Before Loading
```sql
-- Return first 10 errors without loading
COPY INTO my_table FROM @my_stage
  FILE_FORMAT = my_csv_format
  VALIDATION_MODE = 'RETURN_10_ROWS';

-- Return all errors
COPY INTO my_table FROM @my_stage
  FILE_FORMAT = my_csv_format
  VALIDATION_MODE = 'RETURN_ERRORS';

-- Check load history
SELECT * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'MY_TABLE',
  START_TIME => DATEADD('HOUR', -24, CURRENT_TIMESTAMP())
));
```

## Snowpipe (Continuous Loading)

Snowpipe loads data automatically as files arrive in a stage.

### Creating a Pipe
```sql
CREATE PIPE my_pipe
  AUTO_INGEST = TRUE
  AS
  COPY INTO my_table
  FROM @my_s3_stage
  FILE_FORMAT = (TYPE = 'JSON');
```

### How Auto-Ingest Works
1. Files land in cloud storage (S3, Blob, GCS)
2. Cloud event notification (S3 SQS, Azure Event Grid, GCS Pub/Sub) triggers Snowpipe
3. Snowpipe loads data in micro-batches using serverless compute
4. No warehouse needed — billed per-file based on compute used

### Setting Up S3 Notifications
```sql
-- Get SQS queue ARN for the pipe
SELECT SYSTEM$PIPE_STATUS('my_pipe');

-- The SQS ARN returned is configured as an S3 event notification target
-- S3 → Properties → Event notifications → Send to SQS
-- Events: s3:ObjectCreated:*
```

### Manual Pipe Triggering
```sql
-- Manually trigger for specific files
ALTER PIPE my_pipe REFRESH;

-- Refresh specific prefix
ALTER PIPE my_pipe REFRESH PREFIX = 'data/2024/01/';
```

### Monitoring Pipes
```sql
SELECT SYSTEM$PIPE_STATUS('my_pipe');

SELECT *
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'MY_TABLE',
  START_TIME => DATEADD('HOUR', -1, CURRENT_TIMESTAMP())
));

-- Pipe usage history
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE PIPE_NAME = 'MY_PIPE'
ORDER BY START_TIME DESC;
```

## PUT Command

Upload local files to an internal stage (SnowSQL or Snowflake connectors):

```sql
-- Upload from local filesystem to internal stage
PUT file:///tmp/data/file.csv @my_stage AUTO_COMPRESS = TRUE;

-- Upload with pattern
PUT file:///tmp/data/*.csv @my_stage/subfolder/;

-- Then load
COPY INTO my_table FROM @my_stage FILE_FORMAT = my_csv_format;

-- Download from stage to local (GET)
GET @my_stage/file.csv.gz file:///tmp/output/;
```

## Bulk Loading Patterns

### Full Refresh Pattern
```sql
-- Replace entire table
CREATE OR REPLACE TABLE target AS
SELECT * FROM @my_stage (FILE_FORMAT => my_format);

-- Or with OVERWRITE
INSERT OVERWRITE INTO target
SELECT $1, $2, $3 FROM @my_stage (FILE_FORMAT => my_format);
```

### Incremental Load Pattern
```sql
-- Using streams + tasks
CREATE STREAM source_stream ON TABLE raw_data;

CREATE TASK incremental_load
  WAREHOUSE = ETL_WH
  SCHEDULE = '10 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('source_stream')
  AS
  MERGE INTO target t
  USING source_stream s ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET t.value = s.value, t.updated = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN INSERT (id, value, created) VALUES (s.id, s.value, CURRENT_TIMESTAMP());
```

### Staging Pattern
```sql
-- Land → Stage → Transform → Target
-- 1. Load raw into staging
COPY INTO raw_db.landing.events FROM @ext_stage FILE_FORMAT = json_format;

-- 2. Transform into staging
INSERT INTO raw_db.staging.events_clean
SELECT
  raw:event_id::INT,
  raw:user_id::STRING,
  raw:action::STRING,
  raw:timestamp::TIMESTAMP_NTZ
FROM raw_db.landing.events
WHERE raw:event_id IS NOT NULL;

-- 3. Load into analytics
INSERT INTO analytics_db.marts.event_summary
SELECT action, COUNT(*), DATE_TRUNC('HOUR', event_ts) AS hour
FROM raw_db.staging.events_clean
GROUP BY action, hour;
```

## Unloading Data

### COPY INTO (Unloading)
```sql
-- Unload to internal stage
COPY INTO @my_stage/export/
FROM my_table
FILE_FORMAT = (TYPE = 'CSV' HEADER = TRUE COMPRESSION = 'GZIP');

-- Unload to external stage
COPY INTO @my_s3_stage/output/
FROM (SELECT id, name, amount FROM orders WHERE order_date = '2024-01-15')
FILE_FORMAT = (TYPE = 'PARQUET')
HEADER = TRUE
OVERWRITE = TRUE
MAX_FILE_SIZE = 268435456;  -- 256MB per file

-- Single file output
COPY INTO @my_stage/single_file
FROM my_table
FILE_FORMAT = (TYPE = 'CSV')
SINGLE = TRUE
MAX_FILE_SIZE = 5368709120;  -- 5GB
```

### Unload Options
```sql
OVERWRITE = TRUE             -- overwrite existing files
SINGLE = TRUE                -- single output file
MAX_FILE_SIZE = 268435456    -- max bytes per file (default 16MB)
HEADER = TRUE                -- include column headers
PARTITION BY (col)           -- partition output files by column value
```

## Data Loading Best Practices

1. **Right-size files:** 100-250MB compressed per file is optimal
2. **Avoid row-by-row inserts:** Use COPY INTO for bulk loads
3. **Use appropriate warehouse size:** Match to data volume (larger WH = more parallel threads)
4. **Transform in stages:** Load raw first, transform after (ELT pattern)
5. **Use transient tables for staging:** Save on fail-safe storage costs
6. **Partition source files by date/key:** Enables selective loading with PATTERN
7. **Enable PURGE = TRUE or clean up files:** Avoid reprocessing
8. **Use VALIDATION_MODE for first-time loads:** Catch format issues early
9. **Monitor with COPY_HISTORY:** Track load success/failures
10. **Use Snowpipe for real-time needs:** Avoid warehouse costs for continuous loading
