# Workloads for the Snowflake Data Cloud

Reference for data engineering, data lake, Snowpark, Streamlit, data science, Unistore, and hybrid tables.

## Table of Contents
- [Data Engineering](#data-engineering)
- [Data Warehousing](#data-warehousing)
- [Data Lake](#data-lake)
- [Data Collaboration and Monetization](#data-collaboration-and-monetization)
- [Data Applications and Streamlit](#data-applications-and-streamlit)
- [Snowpark](#snowpark)
- [Data Science](#data-science)
- [Cybersecurity and SIEM](#cybersecurity-and-siem)
- [Unistore and Hybrid Tables](#unistore-and-hybrid-tables)

## Data Engineering

### Core Capabilities
- **Streams** — CDC (Change Data Capture) for tracking table changes
- **Tasks** — Scheduled SQL execution (cron-like)
- **Snowpipe** — Continuous serverless ingestion
- **COPY INTO** — Batch loading from stages
- **External tables** — Query data in place without loading

### ELT Pattern (preferred in Snowflake)
```
Extract → Load (raw) → Transform (in Snowflake)

1. Land raw data into staging tables/stages
2. Use SQL, tasks, streams to transform
3. Load into analytical models (star/snowflake schema)
```

### Integration with dbt
```yaml
# dbt_project.yml for Snowflake
name: my_analytics
profile: snowflake_profile

models:
  my_analytics:
    staging:
      materialized: view
    marts:
      materialized: table
```

```sql
-- dbt model example (models/marts/daily_revenue.sql)
{{ config(materialized='table', cluster_by=['order_date']) }}

SELECT
  DATE_TRUNC('DAY', order_date) AS order_date,
  region,
  SUM(amount) AS daily_revenue
FROM {{ ref('stg_orders') }}
GROUP BY 1, 2
```

### Data Vault 2.0 Modeling
Data Vault is a modeling methodology suited for enterprise data warehousing:

| Component | Purpose | Example |
|-----------|---------|---------|
| **Hub** | Business keys (unique entities) | Hub_Customer (customer_bk) |
| **Link** | Relationships between hubs | Link_Order_Customer |
| **Satellite** | Descriptive attributes (versioned) | Sat_Customer_Details |

```sql
-- Hub table
CREATE TABLE hub_customer (
  hub_customer_hk BINARY(32),    -- hash key
  customer_bk STRING,             -- business key
  load_date TIMESTAMP_NTZ,
  record_source STRING
);

-- Satellite table (tracks changes)
CREATE TABLE sat_customer_details (
  hub_customer_hk BINARY(32),
  load_date TIMESTAMP_NTZ,
  name STRING,
  email STRING,
  hash_diff BINARY(32),          -- hash of all descriptive fields
  record_source STRING
);
```

## Data Warehousing

### Star Schema Pattern
```sql
-- Fact table
CREATE TABLE fact_sales (
  sale_id INT,
  date_key INT,
  customer_key INT,
  product_key INT,
  amount DECIMAL(12,2),
  quantity INT
);

-- Dimension tables
CREATE TABLE dim_date (date_key INT, full_date DATE, year INT, quarter INT, month INT);
CREATE TABLE dim_customer (customer_key INT, name STRING, region STRING, segment STRING);
CREATE TABLE dim_product (product_key INT, name STRING, category STRING, brand STRING);
```

### Common Analytics Patterns
```sql
-- Year-over-year comparison
SELECT
  d.month,
  SUM(CASE WHEN d.year = 2024 THEN f.amount END) AS revenue_2024,
  SUM(CASE WHEN d.year = 2023 THEN f.amount END) AS revenue_2023,
  ROUND((revenue_2024 - revenue_2023) / revenue_2023 * 100, 1) AS yoy_pct
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year IN (2023, 2024)
GROUP BY d.month
ORDER BY d.month;

-- Running total
SELECT
  order_date,
  daily_revenue,
  SUM(daily_revenue) OVER (ORDER BY order_date) AS running_total
FROM daily_revenue;

-- Moving average
SELECT
  order_date,
  daily_revenue,
  AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7day
FROM daily_revenue;
```

## Data Lake

### External Tables (query data in place)
```sql
-- Query Parquet files in S3 without loading
CREATE EXTERNAL TABLE ext_events (
  event_date DATE AS (VALUE:event_date::DATE),
  event_type STRING AS (VALUE:event_type::STRING),
  user_id STRING AS (VALUE:user_id::STRING),
  payload VARIANT AS (VALUE:payload)
)
WITH LOCATION = @my_s3_stage/events/
FILE_FORMAT = (TYPE = 'PARQUET')
AUTO_REFRESH = TRUE
PARTITION BY (event_date);
```

### Data Lake vs Data Warehouse in Snowflake
| Feature | External Table (Lake) | Native Table (Warehouse) |
|---------|----------------------|------------------------|
| Data location | Customer's cloud storage | Snowflake-managed storage |
| Performance | Slower (no pruning metadata) | Faster (micro-partition pruning) |
| Maintenance | Customer manages files | Snowflake manages storage |
| Cost | Storage in customer account | Storage in Snowflake |
| Schema evolution | Flexible | Structured |
| Updates | Append-only (new files) | Full DML |

### Iceberg Tables (Apache Iceberg integration)
```sql
-- Create Iceberg table managed by Snowflake
CREATE ICEBERG TABLE my_iceberg_table (
  id INT,
  name STRING,
  amount DECIMAL(12,2)
)
CATALOG = 'SNOWFLAKE'
EXTERNAL_VOLUME = 'my_volume'
BASE_LOCATION = 'my_iceberg_data/';

-- Or reference external Iceberg catalog
CREATE ICEBERG TABLE ext_iceberg
  CATALOG = 'my_glue_catalog'
  EXTERNAL_VOLUME = 'my_volume'
  CATALOG_TABLE_NAME = 'my_table';
```

## Data Collaboration and Monetization

### Data Sharing Workload Types
- **Direct sharing** — B2B data exchange
- **Marketplace** — public/private data products
- **Clean rooms** — privacy-preserving analytics
- **Data monetization** — sell data as a product

### Compliance for Data Sharing
- GDPR, HIPAA, PCI compliance considerations
- Use masking policies and row access policies on shared views
- Audit with ACCESS_HISTORY
- Data residency: share within same region or replicate with awareness

## Data Applications and Streamlit

### Streamlit in Snowflake
Build data applications directly inside Snowflake using Python.

```python
# Streamlit app in Snowflake
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.title("Sales Dashboard")

# Query data
df = session.sql("""
    SELECT region, SUM(amount) AS total
    FROM sales
    GROUP BY region
    ORDER BY total DESC
""").to_pandas()

# Display chart
st.bar_chart(df.set_index("REGION"))

# Interactive filter
region = st.selectbox("Select Region", df["REGION"].tolist())
detail = session.sql(f"""
    SELECT product, SUM(amount) AS total
    FROM sales WHERE region = '{region}'
    GROUP BY product ORDER BY total DESC
""").to_pandas()
st.dataframe(detail)
```

### Key Streamlit Features
- Runs natively in Snowflake (no external infrastructure)
- Uses Snowpark for data access
- Supports charts, tables, maps, forms, file uploads
- Role-based access control
- Share apps with other Snowflake users

## Snowpark

Snowpark allows developers to write data processing in Python, Java, or Scala that runs inside Snowflake.

### Snowpark Python
```python
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, sum as sum_, avg, when

# Connect
session = Session.builder.configs({
    "account": "xy12345",
    "user": "alice",
    "password": "...",
    "database": "my_db",
    "schema": "public",
    "warehouse": "compute_wh"
}).create()

# DataFrame API (lazily evaluated, pushes computation to Snowflake)
df = session.table("orders")
result = (df
    .filter(col("order_date") >= "2024-01-01")
    .group_by("region")
    .agg(
        sum_("amount").alias("total_revenue"),
        avg("amount").alias("avg_order")
    )
    .sort(col("total_revenue").desc())
)

result.show()

# Write results
result.write.mode("overwrite").save_as_table("revenue_by_region")
```

### Snowpark UDFs and Stored Procedures
```python
# Register UDF
from snowflake.snowpark.functions import udf
from snowflake.snowpark.types import StringType

@udf(name="classify_amount", is_permanent=True, stage_location="@my_stage",
     replace=True, packages=["snowflake-snowpark-python"])
def classify_amount(amount: float) -> str:
    if amount > 1000: return "high"
    elif amount > 100: return "medium"
    else: return "low"

# Use in query
df.select("order_id", classify_amount(col("amount")).alias("category")).show()
```

### Snowpark ML
```python
from snowflake.ml.modeling.linear_model import LinearRegression

# Train model in Snowflake
model = LinearRegression(input_cols=["feature1", "feature2"], label_cols=["target"])
model.fit(train_df)

# Predict
predictions = model.predict(test_df)
```

## Apache Spark Integration

### Connecting Snowflake with Spark
```python
# Spark connector configuration
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SnowflakeSpark") \
    .config("spark.jars.packages", "net.snowflake:spark-snowflake_2.12:2.12.0-spark_3.4") \
    .getOrCreate()

sfOptions = {
    "sfURL": "xy12345.snowflakecomputing.com",
    "sfUser": "alice",
    "sfPassword": "...",
    "sfDatabase": "my_db",
    "sfSchema": "public",
    "sfWarehouse": "compute_wh"
}

# Read from Snowflake into Spark DataFrame
df = spark.read \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("query", "SELECT * FROM orders WHERE order_date >= '2024-01-01'") \
    .load()

# Or read entire table
df = spark.read \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "orders") \
    .load()
```

### Writing Spark Data to Snowflake
```python
# Write Spark DataFrame to Snowflake
df_transformed.write \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "processed_orders") \
    .mode("overwrite") \
    .save()

# Append mode
df_new.write \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "orders") \
    .mode("append") \
    .save()
```

### Spark vs Snowpark
| Feature | Spark Connector | Snowpark |
|---------|----------------|----------|
| Execution engine | Spark cluster | Snowflake warehouse |
| Infrastructure | Customer-managed Spark | Serverless (Snowflake) |
| Best for | Existing Spark pipelines, ML at scale | Native Snowflake processing |
| Cost model | Spark cluster + Snowflake compute | Snowflake compute only |
| Language | Python, Scala, Java, R | Python, Java, Scala |
| Data movement | Reads/writes between systems | Stays in Snowflake |

## Data Science

### ML in Snowflake
- **Snowpark ML:** Scikit-learn-compatible API running in Snowflake
- **ML Functions:** Built-in forecasting, anomaly detection, classification
- **Feature Store:** Manage ML features
- **Model Registry:** Track and deploy models

### Built-in ML Functions
```sql
-- Time series forecasting
CREATE SNOWFLAKE.ML.FORECAST my_forecast (
  INPUT_DATA => SYSTEM$REFERENCE('TABLE', 'daily_revenue'),
  TIMESTAMP_COLNAME => 'DATE',
  TARGET_COLNAME => 'REVENUE'
);

-- Get predictions
CALL my_forecast!FORECAST(FORECASTING_PERIODS => 30);

-- Anomaly detection
CREATE SNOWFLAKE.ML.ANOMALY_DETECTION my_detector (...);

-- Classification
CREATE SNOWFLAKE.ML.CLASSIFICATION my_classifier (...);
```

## Cybersecurity and SIEM

### Snowflake as a Security Data Lake
- Ingest security logs (firewall, IDS, endpoint, cloud audit)
- Store in VARIANT columns (semi-structured)
- Analyze with SQL (faster and cheaper than SIEM for large volumes)
- Combine with threat intelligence from Marketplace

```sql
-- Query security logs
SELECT
  raw:timestamp::TIMESTAMP AS event_time,
  raw:source_ip::STRING AS src_ip,
  raw:destination_ip::STRING AS dst_ip,
  raw:event_type::STRING AS event_type
FROM security_logs
WHERE raw:severity::INT >= 7
  AND event_time >= DATEADD('HOUR', -1, CURRENT_TIMESTAMP())
ORDER BY event_time DESC;
```

### SIEM vs Snowflake
| Feature | Traditional SIEM | Snowflake |
|---------|-----------------|-----------|
| Cost | Expensive per GB/day | Pay for storage + compute |
| Retention | Usually 30-90 days | Unlimited |
| Query speed | Varies | Scales with warehouse |
| Scale | Limited | Elastic |
| Best for | Real-time alerts | Investigation, hunting, compliance |

## Unistore and Hybrid Tables

### Hybrid Tables (Unistore workload)
Hybrid tables support **transactional (OLTP)** workloads alongside analytical queries.

```sql
-- Create hybrid table
CREATE HYBRID TABLE user_sessions (
  session_id VARCHAR(36) PRIMARY KEY,
  user_id INT,
  started_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  metadata VARIANT,
  INDEX idx_user (user_id)
);

-- Supports fast point lookups and row-level operations
SELECT * FROM user_sessions WHERE session_id = 'abc-123';
INSERT INTO user_sessions (session_id, user_id) VALUES ('def-456', 42);
UPDATE user_sessions SET metadata = PARSE_JSON('{"active":true}') WHERE session_id = 'abc-123';
DELETE FROM user_sessions WHERE started_at < DATEADD('DAY', -7, CURRENT_TIMESTAMP());
```

### Hybrid vs Standard Tables
| Feature | Standard Table | Hybrid Table |
|---------|---------------|-------------|
| Storage | Micro-partitions (columnar) | Row-store + columnar |
| Point lookups | Slower (scan partitions) | Fast (indexed) |
| Bulk analytics | Optimized | Supported but not primary |
| Primary key | Not enforced | Enforced |
| Secondary indexes | Not available | Supported |
| Consistency | Eventual (within statement) | Row-level ACID |
| Use case | Analytics, warehousing | Application state, OLTP |

### When to Use Hybrid Tables
- Application backends requiring fast single-row reads/writes
- Session stores, user profiles, configuration tables
- Operational data that also needs analytical querying
- Replacing separate OLTP databases for simpler architecture
