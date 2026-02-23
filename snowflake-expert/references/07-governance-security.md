# Data Governance, Account Security, and Data Protection

Reference for security, data governance, masking, tagging, row-level security, and replication.

## Table of Contents
- [Security Overview](#security-overview)
- [Network Security](#network-security)
- [Encryption](#encryption)
- [Data Protection and Recovery](#data-protection-and-recovery)
- [Replication and Failover](#replication-and-failover)
- [Object Tagging](#object-tagging)
- [Data Classification](#data-classification)
- [Data Masking](#data-masking)
- [Row Access Policies](#row-access-policies)
- [Secure Views and UDFs](#secure-views-and-udfs)

## Security Overview

Snowflake security is multi-layered:
1. **Network** — IP whitelisting, private connectivity
2. **Authentication** — password, MFA, key pair, SSO/SAML, OAuth
3. **Authorization** — RBAC (roles and privileges)
4. **Encryption** — at rest (AES-256) and in transit (TLS 1.2)
5. **Data governance** — masking, tagging, row-level security, classification

## Network Security

### Network Policies (IP Whitelisting)
```sql
-- Create policy
CREATE NETWORK POLICY corporate_policy
  ALLOWED_IP_LIST = ('10.0.0.0/8', '172.16.0.0/12', '203.0.113.50')
  BLOCKED_IP_LIST = ('10.0.0.99');

-- Apply to entire account
ALTER ACCOUNT SET NETWORK_POLICY = corporate_policy;

-- Apply to specific user
ALTER USER alice SET NETWORK_POLICY = strict_policy;

-- Remove
ALTER ACCOUNT UNSET NETWORK_POLICY;
```

### Private Connectivity
- **AWS PrivateLink** — direct VPC-to-Snowflake connection (Business Critical+)
- **Azure Private Link** — direct VNet-to-Snowflake
- **GCP Private Service Connect** — direct VPC access
- Eliminates data traversal over public internet

### SSO / SAML / OAuth
```sql
-- SAML integration (Okta, Azure AD, etc.)
CREATE SECURITY INTEGRATION saml_okta
  TYPE = SAML2
  SAML2_ISSUER = 'http://www.okta.com/...'
  SAML2_SSO_URL = 'https://company.okta.com/app/...'
  SAML2_PROVIDER = 'OKTA'
  SAML2_X509_CERT = '<certificate>';

-- OAuth integration
CREATE SECURITY INTEGRATION oauth_custom
  TYPE = OAUTH
  OAUTH_CLIENT = 'CUSTOM'
  OAUTH_REDIRECT_URI = 'https://myapp.com/callback'
  ENABLED = TRUE;
```

## Encryption

### At Rest
- **AES-256** encryption for all data (automatic, always on)
- Snowflake manages encryption keys by default
- **Tri-Secret Secure** (Business Critical+): customer-managed key wraps Snowflake key
  - AWS KMS, Azure Key Vault, or GCP Cloud KMS

### In Transit
- **TLS 1.2** for all network communication
- Applies to client connections, internal data movement, and replication

### Key Rotation
```sql
-- Snowflake automatically rotates encryption keys
-- Tri-Secret Secure: customer manages root key rotation schedule
-- Periodic rekeying available for compliance
ALTER ACCOUNT SET PERIODIC_DATA_REKEYING = TRUE;
```

## Data Protection and Recovery

### Time Travel
```sql
-- Query point-in-time data
SELECT * FROM orders AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP_NTZ);
SELECT * FROM orders AT(OFFSET => -3600);  -- 1 hour ago
SELECT * FROM orders BEFORE(STATEMENT => '<query_id>');

-- Restore from Time Travel
CREATE TABLE orders_restored CLONE orders AT(TIMESTAMP => '2024-01-15 10:00:00');

-- Undrop (within retention period)
UNDROP TABLE deleted_table;
UNDROP SCHEMA deleted_schema;
UNDROP DATABASE deleted_db;

-- Retention period (Standard: 0-1 day, Enterprise: 0-90 days)
ALTER TABLE orders SET DATA_RETENTION_TIME_IN_DAYS = 30;
ALTER TABLE temp_data SET DATA_RETENTION_TIME_IN_DAYS = 0;  -- disable
```

### Time Travel Debugging Workflows
```sql
-- Clone entire database at a point-in-time for debugging
CREATE DATABASE debug_db CLONE prod_db
  AT(TIMESTAMP => '2024-01-15 08:00:00'::TIMESTAMP_NTZ);
-- Dev team investigates against the clone without affecting production

-- Compare current vs historical data to find what changed
SELECT 'current' AS source, COUNT(*) AS cnt, SUM(amount) AS total
FROM orders
UNION ALL
SELECT 'before_incident', COUNT(*), SUM(amount)
FROM orders AT(TIMESTAMP => '2024-01-15 08:00:00'::TIMESTAMP_NTZ);

-- Find rows that were deleted or modified
SELECT *
FROM orders BEFORE(STATEMENT => '<problematic_query_id>')
MINUS
SELECT *
FROM orders;

-- Restore a single table from Time Travel
CREATE TABLE orders_fixed CLONE orders
  BEFORE(STATEMENT => '<bad_delete_query_id>');
-- Validate, then swap
ALTER TABLE orders_fixed SWAP WITH orders;
DROP TABLE orders_fixed;

-- Check Time Travel storage impact
SELECT
  TABLE_NAME,
  ACTIVE_BYTES / POWER(1024,3) AS active_gb,
  TIME_TRAVEL_BYTES / POWER(1024,3) AS time_travel_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE TIME_TRAVEL_BYTES > 0
ORDER BY TIME_TRAVEL_BYTES DESC;
```

### Fail-Safe
- **7 days** of additional recovery after Time Travel expires
- Snowflake-only access (submit support ticket)
- Non-configurable, always active for permanent tables
- Transient and temporary tables: no fail-safe

### ACCESS_HISTORY
```sql
-- Monitor who accessed what (Enterprise+)
SELECT
  QUERY_ID,
  USER_NAME,
  DIRECT_OBJECTS_ACCESSED,
  BASE_OBJECTS_ACCESSED,
  OBJECTS_MODIFIED
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE QUERY_START_TIME > DATEADD('DAY', -7, CURRENT_TIMESTAMP())
ORDER BY QUERY_START_TIME DESC;
```

## Replication and Failover

### Database Replication
```sql
-- Enable replication on source
ALTER DATABASE prod_db ENABLE REPLICATION TO ACCOUNTS org.backup_account;

-- On target account: create replica
CREATE DATABASE prod_db AS REPLICA OF org.primary_account.prod_db;

-- Refresh replica
ALTER DATABASE prod_db REFRESH;

-- Schedule refresh
CREATE TASK refresh_replica
  WAREHOUSE = ADMIN_WH
  SCHEDULE = '10 MINUTE'
  AS ALTER DATABASE prod_db REFRESH;
```

### Failover (Business Critical+)
```sql
-- Enable failover on source
ALTER DATABASE prod_db ENABLE FAILOVER TO ACCOUNTS org.dr_account;

-- Promote replica to primary (on DR account)
ALTER DATABASE prod_db PRIMARY;

-- Failback: reverse the process
```

### Account-Level Replication
```sql
-- Replicate account-level objects (users, roles, warehouses, etc.)
CREATE FAILOVER GROUP fg1
  OBJECT_TYPES = DATABASES, ROLES, USERS, WAREHOUSES, INTEGRATIONS
  ALLOWED_DATABASES = prod_db, analytics_db
  ALLOWED_ACCOUNTS = org.dr_account
  REPLICATION_SCHEDULE = '10 MINUTE';
```

## Object Tagging

Tags attach metadata to Snowflake objects for governance, compliance, and cost tracking.

```sql
-- Create tag
CREATE TAG sensitivity ALLOWED_VALUES = ('public', 'internal', 'confidential', 'restricted');
CREATE TAG cost_center;
CREATE TAG data_owner;

-- Apply tags
ALTER TABLE customers SET TAG sensitivity = 'confidential';
ALTER TABLE customers ALTER COLUMN email SET TAG sensitivity = 'restricted';
ALTER TABLE customers ALTER COLUMN name SET TAG sensitivity = 'internal';
ALTER WAREHOUSE analytics_wh SET TAG cost_center = 'analytics-team';

-- Query tags
SELECT * FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('customers', 'TABLE'));

-- Find all objects with a specific tag value
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE TAG_NAME = 'SENSITIVITY' AND TAG_VALUE = 'confidential';

-- Tag-based access (combine with masking policies)
```

## Data Classification

Automatically detect and classify sensitive data (Enterprise+).

```sql
-- Classify columns in a table
SELECT SYSTEM$CLASSIFY('my_db.public.customers', {'auto_tag': true});

-- View classification results
SELECT * FROM TABLE(
  INFORMATION_SCHEMA.TAG_REFERENCES('customers', 'TABLE')
);

-- Classification categories: IDENTIFIER, QUASI_IDENTIFIER, SENSITIVE
-- Semantic categories: NAME, EMAIL, PHONE, SSN, etc.
```

## Data Masking

Dynamic Data Masking applies transformations at query time based on the user's role.

### Column-Level Masking
```sql
-- Create masking policy
CREATE MASKING POLICY email_mask AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DATA_ENGINEER', 'ACCOUNTADMIN') THEN val
    ELSE REGEXP_REPLACE(val, '.+@', '***@')
  END;

-- Apply to column
ALTER TABLE customers ALTER COLUMN email SET MASKING POLICY email_mask;

-- Full mask for SSN
CREATE MASKING POLICY ssn_mask AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('HR_ADMIN') THEN val
    ELSE '***-**-' || RIGHT(val, 4)
  END;

ALTER TABLE employees ALTER COLUMN ssn SET MASKING POLICY ssn_mask;

-- Numeric masking
CREATE MASKING POLICY salary_mask AS (val NUMBER) RETURNS NUMBER ->
  CASE
    WHEN CURRENT_ROLE() IN ('HR_ADMIN', 'FINANCE') THEN val
    ELSE 0
  END;

-- Remove masking policy
ALTER TABLE customers ALTER COLUMN email UNSET MASKING POLICY;

-- View policies
SHOW MASKING POLICIES;
```

### Conditional Masking with Tags
```sql
-- Policy that references the column's tag
CREATE MASKING POLICY tag_based_mask AS (val STRING) RETURNS STRING ->
  CASE
    WHEN SYSTEM$GET_TAG_ON_CURRENT_COLUMN('sensitivity') = 'restricted'
      AND CURRENT_ROLE() NOT IN ('DATA_ENGINEER')
    THEN '****'
    ELSE val
  END;
```

## Row Access Policies

Row-level security filters rows based on the querying user's role.

```sql
-- Create row access policy
CREATE ROW ACCESS POLICY region_policy AS (region_val STRING) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'ACCOUNTADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'US_ANALYST' AND region_val = 'US' THEN TRUE
    WHEN CURRENT_ROLE() = 'EU_ANALYST' AND region_val = 'EU' THEN TRUE
    ELSE FALSE
  END;

-- Apply to table
ALTER TABLE orders ADD ROW ACCESS POLICY region_policy ON (region);

-- Using mapping table (more maintainable)
CREATE ROW ACCESS POLICY role_region_policy AS (region_val STRING) RETURNS BOOLEAN ->
  EXISTS (
    SELECT 1 FROM role_region_mapping
    WHERE role_name = CURRENT_ROLE()
    AND allowed_region = region_val
  );

-- Remove
ALTER TABLE orders DROP ROW ACCESS POLICY region_policy;
```

## Secure Views and UDFs

```sql
-- Secure view: hides definition, prevents optimizer from exposing filtered data
CREATE SECURE VIEW customer_view AS
SELECT customer_id, name, region
FROM customers
WHERE region = 'US';

-- Secure UDF: hides implementation
CREATE SECURE FUNCTION mask_email(email STRING)
  RETURNS STRING
  AS $$ REGEXP_REPLACE(email, '.+@', '***@') $$;

-- Used in data sharing: consumers can't see underlying logic
```

### Object Dependencies
```sql
-- View what objects a view depends on
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
WHERE REFERENCING_OBJECT_NAME = 'MY_VIEW';
```
