# Leveraging Snowflake Access Controls

Reference for RBAC, roles, privileges, user management, and multi-account strategy.

## Table of Contents
- [RBAC Overview](#rbac-overview)
- [System-Defined Roles](#system-defined-roles)
- [Custom Roles](#custom-roles)
- [Role Hierarchy](#role-hierarchy)
- [Granting Privileges](#granting-privileges)
- [User Management](#user-management)
- [SCIM Integration](#scim-integration)
- [Multi-Account Strategy](#multi-account-strategy)

## RBAC Overview

Snowflake uses Role-Based Access Control. Every action requires a privilege, privileges are granted to roles, and roles are granted to users.

```
User → Role → Privileges → Objects
```

**Key principles:**
- Users don't own objects — roles do
- A user's active role determines what they can do
- Roles form a hierarchy — parent roles inherit child role privileges
- Principle of least privilege: grant minimum access needed

## System-Defined Roles

| Role | Purpose |
|------|---------|
| **ORGADMIN** | Organization-level management (multi-account) |
| **ACCOUNTADMIN** | Top-level account role (combines SYSADMIN + SECURITYADMIN). Use sparingly. |
| **SECURITYADMIN** | Manage grants, roles, users. Can manage any grant in the account. |
| **USERADMIN** | Create and manage users and roles (but not grants on objects) |
| **SYSADMIN** | Create and manage databases, warehouses, and other objects |
| **PUBLIC** | Automatically granted to every user. Minimal default access. |

### Role Hierarchy (default)
```
ACCOUNTADMIN
├── SECURITYADMIN
│   └── USERADMIN
└── SYSADMIN
    └── (custom roles should be granted here)
        └── PUBLIC
```

**Best practices:**
- Don't use ACCOUNTADMIN for daily work
- Create custom roles for specific workloads
- Grant all custom roles up to SYSADMIN (so SYSADMIN can manage their objects)
- Use SECURITYADMIN or USERADMIN for user/role management

## Custom Roles

### Functional Roles (Business/IT)
```sql
-- Business roles
CREATE ROLE DATA_ANALYST;
CREATE ROLE DATA_ENGINEER;
CREATE ROLE DATA_SCIENTIST;
CREATE ROLE BI_DEVELOPER;

-- Grant to SYSADMIN hierarchy
GRANT ROLE DATA_ANALYST TO ROLE SYSADMIN;
GRANT ROLE DATA_ENGINEER TO ROLE SYSADMIN;
GRANT ROLE DATA_SCIENTIST TO ROLE SYSADMIN;
```

### Object Access Roles (fine-grained)
```sql
-- Read-only access to specific schema
CREATE ROLE ANALYTICS_READ;
GRANT USAGE ON DATABASE analytics_db TO ROLE ANALYTICS_READ;
GRANT USAGE ON SCHEMA analytics_db.marts TO ROLE ANALYTICS_READ;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics_db.marts TO ROLE ANALYTICS_READ;
GRANT SELECT ON FUTURE TABLES IN SCHEMA analytics_db.marts TO ROLE ANALYTICS_READ;

-- Read-write for ETL
CREATE ROLE RAW_WRITE;
GRANT USAGE ON DATABASE raw_db TO ROLE RAW_WRITE;
GRANT USAGE ON SCHEMA raw_db.landing TO ROLE RAW_WRITE;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA raw_db.landing TO ROLE RAW_WRITE;
GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA raw_db.landing TO ROLE RAW_WRITE;

-- Compose functional roles from object access roles
GRANT ROLE ANALYTICS_READ TO ROLE DATA_ANALYST;
GRANT ROLE RAW_WRITE TO ROLE DATA_ENGINEER;
GRANT ROLE ANALYTICS_READ TO ROLE DATA_ENGINEER;
```

### Service Account Roles
```sql
CREATE ROLE SVC_ETL_ROLE;
GRANT ROLE RAW_WRITE TO ROLE SVC_ETL_ROLE;
GRANT USAGE ON WAREHOUSE ETL_WH TO ROLE SVC_ETL_ROLE;
GRANT OPERATE ON WAREHOUSE ETL_WH TO ROLE SVC_ETL_ROLE;

-- Service account user
CREATE USER svc_etl_user
  PASSWORD = ''
  RSA_PUBLIC_KEY = '<public_key>'
  DEFAULT_ROLE = SVC_ETL_ROLE
  DEFAULT_WAREHOUSE = ETL_WH;

GRANT ROLE SVC_ETL_ROLE TO USER svc_etl_user;
```

## Role Hierarchy

```sql
-- Build hierarchy
GRANT ROLE ANALYTICS_READ TO ROLE DATA_ANALYST;
GRANT ROLE DATA_ANALYST TO ROLE SYSADMIN;

-- View role hierarchy
SHOW GRANTS OF ROLE DATA_ANALYST;       -- who has this role
SHOW GRANTS TO ROLE DATA_ANALYST;       -- what this role can do
SHOW GRANTS ON DATABASE analytics_db;   -- who can access this database

-- Account usage view
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE GRANTEE_NAME = 'DATA_ANALYST';
```

## Granting Privileges

### Database Privileges
```sql
GRANT USAGE ON DATABASE my_db TO ROLE analyst;
GRANT CREATE SCHEMA ON DATABASE my_db TO ROLE engineer;
GRANT ALL PRIVILEGES ON DATABASE my_db TO ROLE admin_role;
```

### Schema Privileges
```sql
GRANT USAGE ON SCHEMA my_db.public TO ROLE analyst;
GRANT CREATE TABLE ON SCHEMA my_db.public TO ROLE engineer;
GRANT CREATE VIEW ON SCHEMA my_db.public TO ROLE engineer;
```

### Table/View Privileges
```sql
GRANT SELECT ON TABLE my_table TO ROLE analyst;
GRANT INSERT, UPDATE, DELETE ON TABLE my_table TO ROLE engineer;
GRANT SELECT ON ALL TABLES IN SCHEMA my_schema TO ROLE analyst;
GRANT SELECT ON FUTURE TABLES IN SCHEMA my_schema TO ROLE analyst;  -- auto-grant on new tables
```

### Warehouse Privileges
```sql
GRANT USAGE ON WAREHOUSE my_wh TO ROLE analyst;     -- can use it
GRANT OPERATE ON WAREHOUSE my_wh TO ROLE engineer;  -- can start/stop/resize
GRANT MONITOR ON WAREHOUSE my_wh TO ROLE admin;     -- can view usage
GRANT MODIFY ON WAREHOUSE my_wh TO ROLE admin;      -- can change properties
```

### Revoking Privileges
```sql
REVOKE SELECT ON TABLE my_table FROM ROLE analyst;
REVOKE ALL PRIVILEGES ON DATABASE my_db FROM ROLE old_role;
REVOKE ROLE analyst FROM USER bob;
```

## User Management

```sql
-- Create user
CREATE USER alice
  PASSWORD = 'StrongP@ss123'
  DEFAULT_ROLE = DATA_ANALYST
  DEFAULT_WAREHOUSE = ANALYST_WH
  DEFAULT_NAMESPACE = ANALYTICS_DB.MARTS
  MUST_CHANGE_PASSWORD = TRUE
  EMAIL = 'alice@company.com'
  DISPLAY_NAME = 'Alice Smith';

-- Assign roles
GRANT ROLE DATA_ANALYST TO USER alice;
GRANT ROLE BI_DEVELOPER TO USER alice;

-- Modify user
ALTER USER alice SET DEFAULT_WAREHOUSE = NEW_WH;
ALTER USER alice SET DISABLED = TRUE;   -- disable login
ALTER USER alice SET DISABLED = FALSE;  -- re-enable

-- Reset password
ALTER USER alice SET PASSWORD = 'NewP@ss456' MUST_CHANGE_PASSWORD = TRUE;

-- Key pair authentication
ALTER USER alice SET RSA_PUBLIC_KEY = '<public_key_string>';

-- Drop user
DROP USER IF EXISTS old_user;

-- List users
SHOW USERS;
```

### Multi-Factor Authentication (MFA)
```sql
-- MFA is per-user, enabled via Snowsight or Duo
-- Enforce MFA for a user
ALTER USER alice SET MINS_TO_BYPASS_MFA = 0;  -- no bypass

-- Network policies (IP whitelisting)
CREATE NETWORK POLICY office_only
  ALLOWED_IP_LIST = ('10.0.0.0/8', '192.168.1.0/24')
  BLOCKED_IP_LIST = ();

ALTER ACCOUNT SET NETWORK_POLICY = office_only;
-- Or per-user:
ALTER USER alice SET NETWORK_POLICY = office_only;
```

## SCIM Integration

SCIM (System for Cross-domain Identity Management) syncs users and groups from an IdP (Okta, Azure AD, etc.).

```sql
-- Create SCIM integration
CREATE SECURITY INTEGRATION scim_okta
  TYPE = SCIM
  SCIM_CLIENT = 'OKTA'
  RUN_AS_ROLE = 'SECURITYADMIN';

-- SCIM auto-provisions:
-- - Users (create/update/deactivate)
-- - Groups → Snowflake roles
-- - Group membership → role grants
```

## Multi-Account Strategy

For large organizations with multiple Snowflake accounts:

```sql
-- Organization-level operations (ORGADMIN role)
-- Manage accounts, enable replication, view org-wide usage

-- Create a new account in the org
-- (done via Snowflake support or org admin UI)

-- Database replication across accounts
ALTER DATABASE my_db ENABLE REPLICATION TO ACCOUNTS org.account2;

-- On target account:
CREATE DATABASE my_db AS REPLICA OF org.account1.my_db;
ALTER DATABASE my_db REFRESH;

-- Failover
ALTER DATABASE my_db ENABLE FAILOVER TO ACCOUNTS org.account2;
-- On target: ALTER DATABASE my_db PRIMARY;
```
