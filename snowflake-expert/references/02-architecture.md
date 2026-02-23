# Creating and Managing the Snowflake Architecture

Reference for Snowflake's three-layer architecture, virtual warehouses, caching, and billing.

## Table of Contents
- [Traditional Architectures vs Snowflake](#traditional-architectures-vs-snowflake)
- [The Three-Layer Architecture](#the-three-layer-architecture)
- [Cloud Services Layer](#cloud-services-layer)
- [Query Processing (Virtual Warehouse) Layer](#query-processing-virtual-warehouse-layer)
- [Centralized Storage Layer](#centralized-storage-layer)
- [Caching](#caching)
- [Billing Overview](#billing-overview)

## Traditional Architectures vs Snowflake

| Architecture | Description | Snowflake Advantage |
|-------------|-------------|-------------------|
| **Shared-Disk** | Multiple nodes share single storage | Snowflake separates compute from storage |
| **Shared-Nothing** | Each node has own storage | Snowflake avoids data redistribution on resize |
| **NoSQL** | Sacrifices SQL/ACID for scale | Snowflake provides SQL + ACID at scale |

Snowflake combines benefits of shared-disk (centralized storage) and shared-nothing (independent compute) in a unique hybrid architecture.

## The Three-Layer Architecture

```
┌─────────────────────────────────┐
│     Cloud Services Layer        │  ← Authentication, metadata, optimization
├─────────────────────────────────┤
│  Query Processing (Compute)     │  ← Virtual warehouses (independent)
│  ┌─────┐ ┌─────┐ ┌─────┐      │
│  │ VW1 │ │ VW2 │ │ VW3 │      │
│  └─────┘ └─────┘ └─────┘      │
├─────────────────────────────────┤
│   Centralized Storage Layer     │  ← Cloud object storage (S3/Blob/GCS)
│   (Hybrid Columnar)             │
└─────────────────────────────────┘
```

## Cloud Services Layer

Manages all coordination and metadata — runs on Snowflake-managed infrastructure.

### Services Provided
- **Authentication & access control** — login, RBAC, OAuth, SCIM
- **Infrastructure management** — warehouse provisioning, scaling
- **Metadata management** — table stats, micro-partition metadata
- **Query parsing & optimization** — SQL compilation, query plan optimization
- **Transaction management** — ACID compliance, concurrency control
- **Security** — encryption (at rest + in transit), network policies

### Managing Cloud Services
```sql
-- View cloud services usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE SERVICE_TYPE = 'CLOUD_SERVICES';

-- Cloud services billing: charged only if daily usage exceeds 10% of
-- total daily virtual warehouse consumption
```

### Billing for Cloud Services
- Most usage is free (covered by the 10% adjustment)
- Only the excess beyond 10% of daily warehouse credits is billed
- Heavy metadata operations (large SHOW commands, INFORMATION_SCHEMA queries) can generate costs

## Query Processing (Virtual Warehouse) Layer

Virtual warehouses are independent compute clusters that execute queries.

### Virtual Warehouse Sizes

| Size | Servers | Credits/Hour | Typical Use |
|------|---------|-------------|-------------|
| X-Small | 1 | 1 | Dev, simple queries |
| Small | 2 | 2 | Light workloads |
| Medium | 4 | 4 | Moderate workloads |
| Large | 8 | 8 | Complex queries |
| X-Large | 16 | 16 | Heavy ETL |
| 2X-Large | 32 | 32 | Very large workloads |
| 3X-Large | 64 | 64 | Extreme workloads |
| 4X-Large | 128 | 128 | Maximum compute |
| 5X-Large | 256 | 256 | Enterprise-grade |
| 6X-Large | 512 | 512 | Largest available |

**Each size doubles** the servers and credits of the previous size.

### Creating and Managing Warehouses
```sql
-- Create warehouse
CREATE WAREHOUSE ETL_WH
  WITH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300          -- seconds (5 min)
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3       -- multicluster (Enterprise+)
    SCALING_POLICY = 'STANDARD' -- or 'ECONOMY'
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'ETL processing warehouse';

-- Resize warehouse (takes effect on next query)
ALTER WAREHOUSE ETL_WH SET WAREHOUSE_SIZE = 'XLARGE';

-- Suspend/resume
ALTER WAREHOUSE ETL_WH SUSPEND;
ALTER WAREHOUSE ETL_WH RESUME;

-- Drop warehouse
DROP WAREHOUSE IF EXISTS ETL_WH;
```

### Scaling Up vs Scaling Out

**Scaling Up** — increase warehouse size:
- More compute per query
- Better for complex/slow individual queries
- Change takes effect on next query

**Scaling Out** — multicluster warehouses (Enterprise+):
- More clusters running simultaneously
- Better for high concurrency (many users/queries)
- Automatic based on queue load

```sql
-- Multicluster warehouse
ALTER WAREHOUSE ANALYTICS_WH SET
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 5
  SCALING_POLICY = 'STANDARD';

-- STANDARD: favor performance (spin up clusters aggressively)
-- ECONOMY: favor cost (spin up only when queries queue for 6+ min)
```

### Separation of Workloads
```sql
-- Best practice: separate warehouses by workload
CREATE WAREHOUSE ETL_WH     WAREHOUSE_SIZE = 'LARGE';   -- data loading
CREATE WAREHOUSE ANALYST_WH  WAREHOUSE_SIZE = 'MEDIUM';  -- BI queries
CREATE WAREHOUSE DS_WH       WAREHOUSE_SIZE = 'XLARGE';  -- data science
CREATE WAREHOUSE DEV_WH      WAREHOUSE_SIZE = 'XSMALL';  -- development
```

### Billing for Virtual Warehouses
- Billed per second with a **60-second minimum** per startup
- Credits consumed = warehouse size credits × seconds running / 3600
- Suspended warehouses consume **zero** credits
- Set `AUTO_SUSPEND` aggressively for cost control

## Centralized Storage Layer

All data is stored in cloud object storage (S3, Azure Blob, GCS) managed by Snowflake.

### Hybrid Columnar Storage
- Data is automatically organized into **micro-partitions** (50-500MB compressed)
- Each micro-partition stores data in **columnar format**
- Snowflake manages compression, encryption, and metadata automatically
- No DBA maintenance required (no indexes, no vacuuming, no manual partitioning)

### Zero-Copy Cloning
```sql
-- Clone a database, schema, or table instantly (no storage cost until data diverges)
CREATE DATABASE DEV_DB CLONE PROD_DB;
CREATE SCHEMA TEST_SCHEMA CLONE PROD_SCHEMA;
CREATE TABLE TEST_TABLE CLONE PROD_TABLE;

-- Clones share the underlying micro-partitions
-- New writes create new micro-partitions (only new data costs storage)
```

### Time Travel
```sql
-- Query historical data (1 day Standard, up to 90 days Enterprise)
SELECT * FROM my_table AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP);
SELECT * FROM my_table AT(OFFSET => -60*5);  -- 5 minutes ago
SELECT * FROM my_table BEFORE(STATEMENT => '<query_id>');

-- Restore dropped objects
UNDROP TABLE my_table;
UNDROP SCHEMA my_schema;
UNDROP DATABASE my_database;

-- Set retention period
ALTER TABLE my_table SET DATA_RETENTION_TIME_IN_DAYS = 30;
```

### Storage Billing
- Billed monthly per TB of compressed data stored
- Includes active data, time travel data, and fail-safe data (7 days, non-configurable)
- Zero-copy clones: no additional storage until data diverges

## Caching

Snowflake has three caching layers:

### 1. Query Result Cache (Cloud Services Layer)
```sql
-- Results cached for 24 hours
-- Same query, same data → instant result (no warehouse needed)
-- Invalidated when underlying data changes

-- Disable for testing
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
```

### 2. Metadata Cache (Cloud Services Layer)
```sql
-- COUNT(*), MIN(), MAX() on columns often answered from metadata alone
-- No warehouse consumption
SELECT COUNT(*) FROM large_table;  -- answered from metadata
SELECT MIN(created_date) FROM large_table;  -- answered from metadata
```

### 3. Virtual Warehouse Local Disk Cache (Compute Layer)
- SSD cache on warehouse nodes
- Stores recently accessed micro-partitions
- Lost when warehouse is suspended
- Reason to not auto-suspend too aggressively for frequently queried warehouses

### Caching Best Practices
- Keep `AUTO_SUSPEND` at 5-10 minutes for frequently queried warehouses (preserves SSD cache)
- Use `AUTO_SUSPEND = 60` (1 min) for batch/ETL warehouses
- Don't disable result caching unless debugging
- Avoid unnecessary `ORDER BY` (changes result hash, defeats result cache)
