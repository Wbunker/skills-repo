# Security
## Chapter 8: Authentication (Kerberos, LDAP), Authorization (Ranger/Sentry), TLS, Auditing

---

## Authentication Overview

Impala supports three authentication mechanisms:

| Method | Suitable For | Protocol |
|--------|-------------|---------|
| **No auth** (default) | Development only; never production | None |
| **Kerberos** | Enterprise/production; MIT Kerberos or Active Directory | GSSAPI/SASL |
| **LDAP** | Production; simpler than Kerberos; AD/OpenLDAP | Simple SASL |

---

## Kerberos Authentication

### How Kerberos Works with Impala

```
Client (analyst)
    │ kinit → gets TGT from KDC
    │
    ▼
impala-shell --kerberos
    │ requests service ticket for impala/impalad-host@REALM
    │
    ▼
impalad validates ticket via keytab file
    │
    ▼
Connection authenticated; Impala knows the user principal
```

### impalad Configuration

```
# impalad startup flags
--principal=impala/impalad-host.example.com@EXAMPLE.COM
--keytab_file=/etc/security/keytabs/impala.service.keytab
--enable_ldap_auth=false
# (Kerberos and LDAP are mutually exclusive)
```

### Client Connection

```bash
# Analyst must have a Kerberos ticket first
kinit analyst@EXAMPLE.COM

# impala-shell with Kerberos
impala-shell -i impala-host --kerberos

# JDBC with Kerberos
jdbc:impala://impala-host:21050/mydb;AuthMech=1;
KrbRealm=EXAMPLE.COM;KrbHostFQDN=impala-host.example.com;
KrbServiceName=impala
```

### Cross-Realm Kerberos

For multi-Kerberos-realm environments (e.g., corp + cloud):
- Requires cross-realm trust configuration in KDC
- Set `--keytab_file` to a keytab valid across realms
- Impala principal must be accessible from client realm

---

## LDAP / Active Directory Authentication

Simpler to set up than Kerberos; uses username/password credentials.

### impalad Configuration

```
# impalad startup flags
--enable_ldap_auth=true
--ldap_uri=ldap://ldap-server.example.com
--ldap_baseDN=ou=users,dc=example,dc=com
--ldap_bind_dn=cn=impala-bind,dc=example,dc=com
--ldap_bind_password_cmd='cat /etc/impala/ldap_bind_password'

# For Active Directory
--ldap_uri=ldap://ad-server.example.com
--ldap_domain=EXAMPLE.COM
# Users authenticate as user@EXAMPLE.COM
```

### Client Connection

```bash
# impala-shell with LDAP
impala-shell -i impala-host --ldap --user=analyst
# (prompts for password)

# Non-interactive
impala-shell -i impala-host --ldap --user=analyst --ldap_password_cmd='echo mypassword'

# JDBC
jdbc:impala://impala-host:21050/mydb;AuthMech=3;UID=analyst;PWD=secret
```

### LDAP + TLS (Recommended)

LDAP credentials travel in plaintext without TLS. Always use `ldaps://` or `--ldap_tls`:

```
--ldap_uri=ldaps://ldap-server.example.com:636
# or
--ldap_tls=true
--ldap_ca_certificate=/etc/ssl/certs/ldap-ca.pem
```

---

## TLS / SSL Wire Encryption

Encrypt all connections between clients ↔ impalad and between impalad ↔ impalad.

### impalad TLS Configuration

```
# Certificate and key files
--ssl_server_certificate=/etc/ssl/certs/impala-server.crt
--ssl_private_key=/etc/ssl/private/impala-server.key
--ssl_client_ca_certificate=/etc/ssl/certs/ca-bundle.crt

# Minimum TLS version (TLS 1.2 minimum recommended)
--ssl_minimum_version=tlsv1.2
```

### Client TLS

```bash
# impala-shell
impala-shell -i impala-host --ssl \
    --ca_cert=/etc/ssl/certs/ca-bundle.crt

# JDBC
jdbc:impala://impala-host:21050/mydb;SSL=1;
SSLTrustStore=/path/to/truststore.jks;SSLTrustStorePwd=changeit
```

---

## Authorization: Apache Ranger (Recommended)

Apache Ranger provides centralized, fine-grained authorization for Impala.

### Ranger Privilege Hierarchy

```
Database → Table → Column

Privileges (coarse to fine):
ALL     → SELECT, INSERT, CREATE, DROP, ALTER, INDEX, LOCK, READ, WRITE
SELECT  → query columns/tables
INSERT  → insert data
CREATE  → create tables/views in a database
DROP    → drop tables/views
ALTER   → modify table schema
REFRESH → INVALIDATE METADATA / REFRESH
```

### Ranger Policy Examples

```
Policy: BI Team - Read Sales
  Database: sales_db
  Table: orders, products, customers
  Columns: *  (or specify column list)
  Users/Groups: bi-team
  Permissions: SELECT

Policy: Deny PII Columns
  Database: *
  Table: *
  Columns: ssn, credit_card, dob
  Users/Groups: public
  Permissions: SELECT (deny)

Policy: ETL Write Access
  Database: staging_db
  Table: *
  Users/Groups: etl-service-account
  Permissions: ALL
```

### Column Masking

Ranger can mask sensitive columns for users without explicit access:

```
Masking Policy: Mask SSN for non-PII users
  Column: customers.ssn
  Masking Type: MASK (show XXX-XX-XXXX)
  Users: {NOT IN} pii-authorized-group
```

Impala applies masking at query time — users see masked values transparently.

### Row-Level Filtering

Restrict which rows a user can see:

```
Row Filter Policy: Regional data isolation
  Table: orders
  Filter: region = current_user_region()
  Groups: regional-analysts
```

---

## Authorization: Apache Sentry (Legacy)

Older Hadoop clusters may use Sentry instead of Ranger. The core model is similar:

```sql
-- Sentry managed via SQL (Impala-based Sentry)
-- Grant SELECT on a table
GRANT SELECT ON TABLE sales_db.orders TO ROLE analyst_role;

-- Create and assign roles
CREATE ROLE bi_analyst;
GRANT ROLE bi_analyst TO GROUP bi-team-ldap-group;
GRANT SELECT ON DATABASE sales_db TO ROLE bi_analyst;

-- Revoke
REVOKE SELECT ON TABLE orders FROM ROLE bi_analyst;

-- Show grants
SHOW GRANT ROLE bi_analyst;
SHOW GRANT USER jsmith;
```

### Object Hierarchy for Grants

```
SERVER → DATABASE → TABLE → COLUMN (Ranger/Sentry 2.x)

GRANT ALL ON SERVER TO ROLE admin_role;
GRANT SELECT ON DATABASE sales_db TO ROLE analyst_role;
GRANT SELECT (order_id, amount, dt) ON TABLE orders TO ROLE read_only_role;
```

---

## Audit Logging

Impala writes audit logs when Ranger or Sentry is configured.

### What Impala Audits

- All SQL queries (SELECT, INSERT, DDL)
- User identity (authenticated principal)
- Timestamp, database, table, columns accessed
- Query status (success/failure/impersonation)

### Audit Log Location

```
# Default: /var/log/impala/audit/ (one file per impalad)
# Format: JSON, one event per line
{
  "query_id": "a1b2c3",
  "session_user": "analyst@EXAMPLE.COM",
  "effective_user": "analyst",
  "statement": "SELECT order_id, amount FROM orders WHERE dt='2024-01-15'",
  "status": "OK",
  "databases": ["sales_db"],
  "tables": ["orders"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Audit logs can be forwarded to HDFS, a SIEM, or Apache Atlas for centralized tracking.

---

## User Impersonation

Impala supports delegated impersonation — a service account can execute queries on behalf of an end user.

```
HUE web server authenticates user as "alice"
HUE connects to Impala as service account "hue"
HUE sets: SET IMPERSONATED_USER = alice;
Impala runs the query with alice's Ranger/Sentry permissions
```

Configuration:
```
# impalad startup
--authorized_proxy_user_config=hue=*   # hue can impersonate any user
--authorized_proxy_group_config=hue=*  # hue can impersonate any group
```

---

## Security Hardening Checklist

```
Authentication
[ ] Enable Kerberos (preferred) or LDAP with TLS
[ ] Never run without authentication in multi-user environments
[ ] Rotate service keytabs/passwords on schedule

Authorization
[ ] Deploy Apache Ranger (or Sentry) with Impala plugin
[ ] Deny public access to tables with PII/sensitive data
[ ] Apply column masking policies for regulated data
[ ] Use row filters for multi-tenant data isolation

Transport Encryption
[ ] Enable TLS 1.2+ on all impalad ↔ client connections
[ ] Enable TLS for impalad ↔ impalad internal communication
[ ] Use ldaps:// for LDAP

Audit
[ ] Verify audit logs are being written
[ ] Centralize audit logs to SIEM or HDFS
[ ] Alert on access to sensitive tables

Network
[ ] Restrict impalad ports (21000, 21050, 25000) to authorized clients
[ ] Use private networking for inter-daemon communication
[ ] Disable direct HDFS access for end users; route through Impala
```
