# Governance & Security — Chapters 12-14

Access control, data masking, Unity Catalog, metadata management, lineage, and audit logging.

## Table of Contents

- [Access Control](#access-control)
- [Row-Level and Column-Level Security](#row-level-and-column-level-security)
- [Dynamic Data Masking](#dynamic-data-masking)
- [Unity Catalog](#unity-catalog)
- [Data Lineage](#data-lineage)
- [Audit Logging](#audit-logging)
- [Compliance Patterns](#compliance-patterns)

---

## Access Control

### Three-level namespace

Unity Catalog organizes data in a three-level hierarchy:

```
catalog.schema.table
  └── metastore (top-level container)
       └── catalog (maps to business unit, environment, or domain)
            └── schema (maps to project, team, or dataset group)
                 └── table / view / volume / function / model
```

### Granting privileges

```sql
-- Grant catalog-level access
GRANT USE CATALOG ON CATALOG analytics TO `data-team@company.com`;

-- Grant schema-level access
GRANT USE SCHEMA ON SCHEMA analytics.sales TO `sales-analysts@company.com`;

-- Grant table-level access
GRANT SELECT ON TABLE analytics.sales.orders TO `sales-analysts@company.com`;

-- Grant multiple privileges
GRANT SELECT, MODIFY ON TABLE analytics.sales.orders TO `etl-service@company.com`;

-- Revoke
REVOKE SELECT ON TABLE analytics.sales.orders FROM `former-analyst@company.com`;
```

### Privilege types

| Privilege | Applies to | Allows |
|-----------|-----------|--------|
| `USE CATALOG` | Catalog | Browse and reference catalog |
| `USE SCHEMA` | Schema | Browse and reference schema |
| `SELECT` | Table, View | Read data |
| `MODIFY` | Table | INSERT, UPDATE, DELETE, MERGE |
| `CREATE TABLE` | Schema | Create tables in schema |
| `CREATE SCHEMA` | Catalog | Create schemas in catalog |
| `ALL PRIVILEGES` | Any | All applicable privileges |

### Ownership

```sql
-- Transfer ownership
ALTER TABLE analytics.sales.orders SET OWNER TO `data-platform@company.com`;
```

Owners have full control including granting privileges to others. Default owner is the creator.

## Row-Level and Column-Level Security

### Row filters

```sql
-- Create a function that returns a boolean
CREATE FUNCTION analytics.sales.region_filter(region STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('global-team'), true, region = current_user_region());

-- Apply to table
ALTER TABLE analytics.sales.orders SET ROW FILTER analytics.sales.region_filter ON (region);

-- Remove
ALTER TABLE analytics.sales.orders DROP ROW FILTER;
```

Row filters are evaluated for every query. Only rows where the function returns `true` are visible.

### Column masks

```sql
-- Mask SSN: show full value to HR, redacted for everyone else
CREATE FUNCTION analytics.hr.mask_ssn(ssn STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('hr-team'), ssn, CONCAT('XXX-XX-', RIGHT(ssn, 4)));

-- Apply
ALTER TABLE analytics.hr.employees ALTER COLUMN ssn SET MASK analytics.hr.mask_ssn;

-- Remove
ALTER TABLE analytics.hr.employees ALTER COLUMN ssn DROP MASK;
```

## Dynamic Data Masking

Column masks applied via functions provide dynamic masking — the same table shows different data to different users without maintaining separate views or copies.

**Common masking patterns**:

```sql
-- Email: show domain only
CREATE FUNCTION mask_email(email STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), email,
  CONCAT('***@', SPLIT(email, '@')[1]));

-- Phone: last 4 digits
CREATE FUNCTION mask_phone(phone STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('support'), phone,
  CONCAT('***-***-', RIGHT(phone, 4)));

-- Financial: round to nearest thousand
CREATE FUNCTION mask_salary(salary DOUBLE)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('finance'), salary,
  ROUND(salary / 1000) * 1000);

-- Date: year only
CREATE FUNCTION mask_birthdate(dt DATE)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('hr'), dt,
  DATE_TRUNC('year', dt));

-- Full redaction
CREATE FUNCTION redact(val STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), val, '[REDACTED]');
```

## Unity Catalog

Unified governance layer for Databricks — manages all data and AI assets across workspaces.

### Key capabilities

- **Centralized access control**: One place to manage who can access what
- **Data discovery**: Search across all catalogs, schemas, tables with tags and comments
- **Data lineage**: Automatic column-level lineage tracking
- **Audit logging**: Every access and operation is logged
- **Cross-workspace**: Share governed data across Databricks workspaces

### Metastore setup

```sql
-- External location for managed storage
CREATE EXTERNAL LOCATION my_location
URL 's3://my-bucket/data/'
WITH (STORAGE CREDENTIAL my_credential);

-- Create catalog with managed storage
CREATE CATALOG analytics
MANAGED LOCATION 's3://my-bucket/data/analytics/';

-- Create schema
CREATE SCHEMA analytics.sales;
```

### External tables

```sql
-- Register existing Delta table
CREATE TABLE analytics.sales.orders
USING DELTA
LOCATION 's3://existing-bucket/orders/';
```

### Tags and comments

```sql
-- Add comments for discoverability
COMMENT ON TABLE analytics.sales.orders IS 'All customer orders since 2020';
COMMENT ON COLUMN analytics.sales.orders.amount IS 'Order total in USD';

-- Tags for classification
ALTER TABLE analytics.sales.orders SET TAGS ('pii' = 'true', 'domain' = 'sales');
```

## Data Lineage

Unity Catalog automatically tracks lineage at column level:

```
bronze.events.raw_amount  →  silver.events.amount  →  gold.daily_revenue.total_revenue
```

### Lineage capabilities

- **Automatic**: No configuration needed — captured from Spark/SQL operations
- **Column-level**: Tracks which source columns feed which target columns
- **Cross-table**: Follows data through MERGE, INSERT AS SELECT, CTAS
- **Notebook/job tracking**: Links lineage to the notebook or job that produced it
- **Dashboard integration**: See which tables power which dashboards

### Querying lineage (REST API)

```bash
# Get upstream lineage for a table
curl -X GET "https://<workspace>/api/2.0/lineage-tracking/table-lineage" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"table_name": "analytics.sales.gold_orders", "direction": "UPSTREAM"}'
```

## Audit Logging

### System tables (Databricks)

```sql
-- Query audit logs
SELECT
  event_time,
  service_name,
  action_name,
  user_identity.email AS user_email,
  request_params,
  response.status_code
FROM system.access.audit
WHERE event_time > current_timestamp() - INTERVAL 7 DAYS
  AND action_name = 'getTable'
ORDER BY event_time DESC;
```

### Common audit queries

```sql
-- Who accessed a specific table?
SELECT DISTINCT user_identity.email, COUNT(*) as access_count
FROM system.access.audit
WHERE request_params.full_name_arg = 'analytics.sales.orders'
  AND action_name IN ('getTable', 'commandSubmit')
  AND event_time > current_timestamp() - INTERVAL 30 DAYS
GROUP BY user_identity.email;

-- What tables did a user access?
SELECT DISTINCT request_params.full_name_arg AS table_name, action_name
FROM system.access.audit
WHERE user_identity.email = 'analyst@company.com'
  AND event_time > current_timestamp() - INTERVAL 7 DAYS;

-- Failed access attempts (potential security issues)
SELECT event_time, user_identity.email, action_name, request_params, response.error_message
FROM system.access.audit
WHERE response.status_code >= 400
  AND event_time > current_timestamp() - INTERVAL 1 DAY
ORDER BY event_time DESC;
```

### Delta table history as audit trail

```sql
-- Every operation on the table is recorded
DESCRIBE HISTORY analytics.sales.orders;

-- Filter to specific operations
SELECT version, timestamp, operation, operationMetrics, userName
FROM (DESCRIBE HISTORY analytics.sales.orders)
WHERE operation IN ('MERGE', 'DELETE', 'UPDATE')
ORDER BY version DESC;
```

## Compliance Patterns

### GDPR right to erasure

```sql
-- Delete specific user's data
DELETE FROM bronze_events WHERE user_id = 'user-to-forget';
DELETE FROM silver_events WHERE user_id = 'user-to-forget';
DELETE FROM gold_user_metrics WHERE user_id = 'user-to-forget';

-- VACUUM to physically remove files (after retention period)
VACUUM bronze_events;
VACUUM silver_events;
VACUUM gold_user_metrics;
```

**With deletion vectors**: DELETE is fast (no file rewrite). Follow with OPTIMIZE + VACUUM to physically purge.

### GDPR data portability

```python
# Export user's data
user_data = spark.sql("""
    SELECT * FROM silver_events WHERE user_id = 'requesting-user'
""")
user_data.write.format("json").save("/exports/user-requesting-user/")
```

### Data retention policies

```sql
-- Automated retention: delete data older than policy
DELETE FROM bronze_events WHERE event_date < current_date() - INTERVAL 2 YEARS;

-- Schedule as a job that runs daily/weekly
```

### PII inventory

```sql
-- Use tags to track PII columns
ALTER TABLE analytics.hr.employees ALTER COLUMN ssn SET TAGS ('pii' = 'direct');
ALTER TABLE analytics.hr.employees ALTER COLUMN email SET TAGS ('pii' = 'direct');
ALTER TABLE analytics.hr.employees ALTER COLUMN zip_code SET TAGS ('pii' = 'quasi');

-- Query PII inventory via information_schema
SELECT table_name, column_name, tag_value
FROM system.information_schema.column_tags
WHERE tag_name = 'pii';
```
