# Getting Started

Reference for Snowflake setup, Snowsight UI, worksheets, and initial configuration.

## Table of Contents
- [Snowflake Editions](#snowflake-editions)
- [Snowsight Web UI](#snowsight-web-ui)
- [Worksheets](#worksheets)
- [Context Setting](#context-setting)
- [Account Setup](#account-setup)
- [Snowflake Community & Certifications](#snowflake-community--certifications)

## Snowflake Editions

| Edition | Key Features |
|---------|-------------|
| **Standard** | Core features, time travel (1 day), secure data sharing |
| **Enterprise** | Multi-cluster warehouses, 90-day time travel, materialized views, column-level security, search optimization |
| **Business Critical** | HIPAA/PCI compliance, Tri-Secret Secure encryption, database failover/failback, private connectivity |
| **Virtual Private Snowflake (VPS)** | Dedicated virtual servers, highest level of isolation and security |

**Cloud platforms supported:** AWS, Azure, Google Cloud Platform (GCP)

**Regions:** Multiple regions per cloud provider; cross-cloud data sharing via Snowgrid

## Snowsight Web UI

Snowsight is Snowflake's modern web interface.

### Key UI Areas
- **Worksheets** — SQL editor for writing and running queries
- **Dashboards** — Visual dashboards from query results
- **Data** — Browse databases, schemas, tables, views
- **Marketplace** — Discover and acquire shared datasets
- **Activity** — Query history, copy history, task history
- **Admin** — Warehouses, resource monitors, users, roles, billing

### Snowsight Preferences
```
User Menu → Preferences
- Default role
- Default warehouse
- Default namespace (database.schema)
- Notifications settings
- Session timeout
```

### URL Format
```
https://<account_identifier>.<region>.<cloud>.snowflakecomputing.com
# Example:
https://xy12345.us-east-1.aws.snowflakecomputing.com
```

### Account Identifiers
```sql
-- Organization-based (preferred)
<org_name>-<account_name>

-- Legacy locator-based
<account_locator>.<region>.<cloud>

-- Find your account identifier
SELECT CURRENT_ACCOUNT();
SELECT CURRENT_ORGANIZATION_NAME();
```

## Worksheets

### Creating and Managing Worksheets
- Click **+ Worksheet** to create a new SQL worksheet
- Worksheets auto-save and persist across sessions
- Organize worksheets into folders
- Share worksheets with other users

### Running Queries
```sql
-- Run all statements: Ctrl+Shift+Enter (Cmd+Shift+Enter on Mac)
-- Run selected statement: Ctrl+Enter (Cmd+Enter on Mac)
-- Run single statement at cursor: place cursor, Ctrl+Enter
```

### Worksheet Features
- **Autocomplete** — table names, column names, functions
- **Query history** — access previous queries from worksheet
- **Results panel** — tabular results, chart view, download
- **Variables** — use `:variable_name` syntax for parameterized queries
- **Keyboard shortcuts** — format SQL, comment/uncomment, find/replace

### Using Variables
```sql
-- Set variable
SET my_var = 'production';

-- Use variable
SELECT * FROM my_table WHERE environment = $my_var;

-- Session variable via worksheet
-- Type :start_date in your query, Snowsight prompts for a value
SELECT * FROM sales WHERE sale_date >= :start_date;
```

## Context Setting

Every worksheet needs a role, warehouse, database, and schema context.

```sql
-- Set role context
USE ROLE SYSADMIN;

-- Set warehouse context
USE WAREHOUSE COMPUTE_WH;

-- Set database context
USE DATABASE MY_DB;

-- Set schema context
USE SCHEMA MY_DB.PUBLIC;

-- Set all at once
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE MY_DB;
USE SCHEMA PUBLIC;

-- Or use fully qualified names (no USE needed)
SELECT * FROM MY_DB.PUBLIC.MY_TABLE;
```

### Session Parameters
```sql
-- View current context
SELECT CURRENT_ROLE();
SELECT CURRENT_WAREHOUSE();
SELECT CURRENT_DATABASE();
SELECT CURRENT_SCHEMA();
SELECT CURRENT_SESSION();
SELECT CURRENT_USER();

-- Set session parameters
ALTER SESSION SET QUERY_TAG = 'etl_daily_load';
ALTER SESSION SET TIMEZONE = 'America/New_York';
ALTER SESSION SET TIMESTAMP_INPUT_FORMAT = 'YYYY-MM-DD HH24:MI:SS';
```

## Account Setup

### Setting Up a Trial Account
1. Go to signup.snowflake.com
2. Choose cloud provider and region
3. Select edition (Enterprise recommended for trials)
4. 30-day free trial with $400 in credits

### Initial Configuration Checklist
```sql
-- 1. Create a custom admin warehouse
CREATE WAREHOUSE ADMIN_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- 2. Create databases
CREATE DATABASE RAW_DB COMMENT = 'Raw ingested data';
CREATE DATABASE ANALYTICS_DB COMMENT = 'Transformed analytics data';

-- 3. Create schemas
CREATE SCHEMA RAW_DB.LANDING;
CREATE SCHEMA RAW_DB.STAGING;
CREATE SCHEMA ANALYTICS_DB.MARTS;

-- 4. Create custom roles
CREATE ROLE DATA_ENGINEER;
CREATE ROLE DATA_ANALYST;
GRANT ROLE DATA_ENGINEER TO ROLE SYSADMIN;
GRANT ROLE DATA_ANALYST TO ROLE SYSADMIN;
```

## Snowflake Community & Certifications

### Certifications
| Certification | Level | Focus |
|--------------|-------|-------|
| SnowPro Core | Foundational | Overall Snowflake knowledge |
| SnowPro Advanced: Architect | Advanced | Architecture & design |
| SnowPro Advanced: Data Engineer | Advanced | Data pipelines & transformation |
| SnowPro Advanced: Administrator | Advanced | Account management & security |
| SnowPro Advanced: Data Analyst | Advanced | Analytics & reporting |

### Resources
- **Snowflake Documentation**: docs.snowflake.com
- **Snowflake Community**: community.snowflake.com
- **Snowflake University**: Free training courses
- **GitHub**: Sample code and quickstarts
- **Snowflake Summit**: Annual conference
