# Hive Security

## Table of Contents
1. [Authentication](#authentication)
2. [Authorization Models](#authorization-models)
3. [SQL Standard Authorization](#sql-standard-authorization)
4. [GRANT / REVOKE](#grant--revoke)
5. [Column-Level Security](#column-level-security)
6. [Row-Level Filtering](#row-level-filtering)
7. [Apache Ranger Integration](#apache-ranger-integration)
8. [Encryption](#encryption)

---

## Authentication

### Kerberos (strong auth for production)

```xml
<!-- hive-site.xml -->
<property>
  <name>hive.server2.authentication</name>
  <value>KERBEROS</value>
</property>
<property>
  <name>hive.server2.authentication.kerberos.principal</name>
  <value>hive/_HOST@EXAMPLE.COM</value>
</property>
<property>
  <name>hive.server2.authentication.kerberos.keytab</name>
  <value>/etc/security/keytabs/hive.service.keytab</value>
</property>
```

```bash
# Kinit before connecting
kinit user@EXAMPLE.COM

# Beeline with Kerberos
beeline -u "jdbc:hive2://hiveserver2:10000/default;principal=hive/_HOST@EXAMPLE.COM"
```

### LDAP authentication

```xml
<property>
  <name>hive.server2.authentication</name>
  <value>LDAP</value>
</property>
<property>
  <name>hive.server2.authentication.ldap.url</name>
  <value>ldap://ldap-server:389</value>
</property>
<property>
  <name>hive.server2.authentication.ldap.baseDN</name>
  <value>ou=users,dc=example,dc=com</value>
</property>
```

### PAM authentication

```xml
<property>
  <name>hive.server2.authentication</name>
  <value>PAM</value>
</property>
<property>
  <name>hive.server2.authentication.pam.services</name>
  <value>sshd,login</value>
</property>
```

### Custom / None (development only)

```xml
<property>
  <name>hive.server2.authentication</name>
  <value>NONE</value>  <!-- No auth — never use in production -->
</property>
```

---

## Authorization Models

Hive supports multiple authorization models (only one active at a time):

| Model | HiveServer2 | Hive CLI | Granularity | Notes |
|-------|-------------|----------|-------------|-------|
| Legacy (default pre-3.0) | Yes | Yes | DB, table, partition | Simple; no column-level |
| SQL Standard | Yes | No | DB, table, column, view | Closest to ANSI SQL |
| Storage-based | Yes | Yes | HDFS path | Delegates to HDFS ACLs |
| Ranger | Yes | No | All + row/column masking | Enterprise; recommended |

### Enable SQL Standard Authorization

```xml
<!-- hive-site.xml -->
<property>
  <name>hive.security.authorization.enabled</name>
  <value>true</value>
</property>
<property>
  <name>hive.security.authorization.manager</name>
  <value>org.apache.hadoop.hive.ql.security.authorization.plugin.sqlstd.SQLStdHiveAuthorizerFactory</value>
</property>
<property>
  <name>hive.users.in.admin.role</name>
  <value>hive,admin</value>
</property>
```

---

## SQL Standard Authorization

Follows ANSI SQL privilege model. Must be enabled (see above).

### Roles

```sql
-- Create/drop roles
CREATE ROLE analyst;
DROP ROLE analyst;

-- Show roles
SHOW ROLES;
SHOW CURRENT ROLES;  -- roles of current user

-- Grant/revoke role membership
GRANT ROLE analyst TO USER alice;
GRANT ROLE analyst TO GROUP data_team;
REVOKE ROLE analyst FROM USER alice;

-- Set active role for session
SET ROLE analyst;
SET ROLE ALL;        -- all granted roles
SET ROLE NONE;       -- no roles (just user privileges)

-- Show role grants
SHOW ROLE GRANT USER alice;
SHOW ROLE GRANT GROUP data_team;
SHOW PRINCIPALS analyst;  -- who has this role
```

---

## GRANT / REVOKE

### Object privileges

```sql
-- Privilege types: SELECT, INSERT, UPDATE, DELETE, ALL PRIVILEGES

-- Grant on table
GRANT SELECT ON TABLE orders TO USER alice;
GRANT INSERT, SELECT ON TABLE orders TO ROLE analyst;
GRANT ALL PRIVILEGES ON TABLE orders TO USER bob;

-- Grant on database
GRANT CREATE ON DATABASE analytics TO ROLE developer;
GRANT SELECT ON DATABASE analytics TO ROLE analyst;

-- Grant on column (column-level security)
GRANT SELECT (order_id, user_id, status) ON TABLE orders TO ROLE analyst;
-- analyst can only SELECT those three columns

-- Grant with admin option (grantee can re-grant)
GRANT SELECT ON TABLE orders TO USER alice WITH GRANT OPTION;

-- Revoke
REVOKE SELECT ON TABLE orders FROM USER alice;
REVOKE ALL PRIVILEGES ON TABLE orders FROM ROLE analyst;
REVOKE GRANT OPTION FOR SELECT ON TABLE orders FROM USER alice;

-- Show grants
SHOW GRANT USER alice;                         -- all grants for alice
SHOW GRANT USER alice ON TABLE orders;          -- grants on specific table
SHOW GRANT ROLE analyst;
SHOW GRANT ON TABLE orders;                    -- all grants on table
```

### URI privileges (for external table LOCATION)

```sql
-- Users need URI privilege to create external tables at that path
GRANT ALL ON URI 'hdfs:///data/raw/events' TO ROLE etl_role;
```

---

## Column-Level Security

Restrict access to specific columns without creating views.

### Using GRANT on columns (SQL Standard)

```sql
-- Allow analyst to see only non-PII columns
GRANT SELECT (order_id, amount, status, created)
ON TABLE orders
TO ROLE analyst;
-- analyst cannot: SELECT user_id, email FROM orders

-- Verify:
-- As analyst:
SELECT order_id, amount FROM orders;  -- OK
SELECT user_id FROM orders;           -- FAILED: privilege denied on column user_id
```

### Using views for column masking (without Ranger)

```sql
-- Create a view that masks sensitive columns
CREATE VIEW orders_masked AS
SELECT order_id,
       amount,
       status,
       created,
       CONCAT('***-', SUBSTR(phone, -4)) AS phone_masked,  -- mask all but last 4
       REGEXP_REPLACE(email, '^[^@]+', '***') AS email_masked
FROM orders;

-- Grant access to view, not base table
GRANT SELECT ON TABLE orders_masked TO ROLE analyst;
REVOKE SELECT ON TABLE orders FROM ROLE analyst;
```

---

## Row-Level Filtering

Without Ranger, row filtering is enforced via views.

```sql
-- Row-level security via view: each user sees only their region's data
CREATE VIEW orders_regional AS
SELECT * FROM orders
WHERE region = CURRENT_USER();  -- user name == region name (contrived example)

-- More realistic: lookup table
CREATE VIEW orders_my_region AS
SELECT o.*
FROM orders o
JOIN user_region_map u ON o.region = u.region
WHERE u.username = CURRENT_USER();
```

For production row-level filtering, use Apache Ranger (see below).

---

## Apache Ranger Integration

Ranger provides centralized policy management with GUI, audit logging, and fine-grained access control including row filtering and column masking.

### Enable Ranger authorization plugin

```xml
<!-- hive-site.xml -->
<property>
  <name>hive.security.authorization.manager</name>
  <value>org.apache.ranger.authorization.hive.authorizer.RangerHiveAuthorizerFactory</value>
</property>
<property>
  <name>hive.security.authorization.enabled</name>
  <value>true</value>
</property>
```

### Ranger policy types for Hive

```
1. Access policies      — GRANT/DENY on database/table/column for users/groups/roles
2. Row filter policies  — WHERE clause applied transparently per user/group
3. Column mask policies — Transform column values per user/group:
   • MASK           → replace with Xs (e.g., "XXXX-1234")
   • MASK_SHOW_LAST_4 → show last 4 chars
   • MASK_SHOW_FIRST_4 → show first 4 chars
   • MASK_HASH      → SHA-256 hash of value
   • MASK_NULL      → return NULL
   • MASK_NONE      → show real value
   • Custom expression (e.g., "substr({col}, 1, 2) || '****'")
```

### Ranger audit

```
All queries logged to Ranger audit (Solr or HDFS)
Audits show: user, time, resource accessed, result (allowed/denied)
```

---

## Encryption

### HDFS Transparent Data Encryption (TDE)

Hive tables stored in HDFS encryption zones are encrypted at rest transparently.

```bash
# Create KMS key (Hadoop KMS)
hadoop key create my-table-key

# Create HDFS encryption zone
hdfs crypto -createZone -keyName my-table-key -path /user/hive/warehouse/secure.db
```

```sql
-- Tables created in this database are automatically in the encryption zone
CREATE DATABASE secure LOCATION 'hdfs:///user/hive/warehouse/secure.db';
CREATE TABLE secure.customers (...) STORED AS ORC;
-- Data is encrypted on disk; reads/writes are transparent to HiveQL
```

### Column encryption at application level

For field-level encryption within Hive data, use AES functions:

```sql
-- Encrypt when writing
INSERT INTO sensitive_table
SELECT user_id,
       AES_ENCRYPT(ssn, unhex(sha2('my-secret-key', 256))) AS ssn_encrypted
FROM raw_data;

-- Decrypt when reading (only privileged users)
SELECT user_id,
       AES_DECRYPT(ssn_encrypted, unhex(sha2('my-secret-key', 256))) AS ssn
FROM sensitive_table;
-- In practice: key comes from a secrets manager, not hardcoded
```

### SSL for HiveServer2 transport

```xml
<property>
  <name>hive.server2.use.SSL</name>
  <value>true</value>
</property>
<property>
  <name>hive.server2.keystore.path</name>
  <value>/etc/hive/conf/hiveserver2.jks</value>
</property>
<property>
  <name>hive.server2.keystore.password</name>
  <value>changeit</value>
</property>
```

```bash
# Beeline with SSL
beeline -u "jdbc:hive2://hiveserver2:10000/default;ssl=true;sslTrustStore=/path/to/truststore.jks;trustStorePassword=changeit"
```
