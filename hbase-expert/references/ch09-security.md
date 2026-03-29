# Ch 9 — Security

## Table of Contents
- [Security Model Overview](#security-model-overview)
- [Kerberos Authentication](#kerberos-authentication)
- [Authorization — ACLs](#authorization--acls)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [Cell-Level Security & Visibility Labels](#cell-level-security--visibility-labels)
- [Transparent Data Encryption (TDE)](#transparent-data-encryption-tde)
- [Audit Logging](#audit-logging)
- [Network Encryption (TLS/SSL)](#network-encryption-tlsssl)
- [Security Checklist](#security-checklist)

---

## Security Model Overview

HBase security is multi-layered:

```
Layer 1: Network Encryption (TLS/SSL)
    ↓ encrypts data in transit (client ↔ RS, RS ↔ RS, RS ↔ HMaster)

Layer 2: Authentication (Kerberos / SASL)
    ↓ verifies identity of clients and servers

Layer 3: Authorization (ACLs)
    ↓ controls who can read/write/admin at table/CF/cell level

Layer 4: Cell-Level Security (Visibility Labels)
    ↓ multi-level security labels on individual cells
```

Security requires the `hbase-server` JAR and appropriate configuration in `hbase-site.xml`.

---

## Kerberos Authentication

### Prerequisites

- MIT Kerberos or Active Directory KDC
- Hadoop secured with Kerberos (HDFS + YARN)
- Service principals for each HBase node

### Create Kerberos Principals

```bash
# Create HBase service principals
kadmin.local -q "addprinc -randkey hbase/master.example.com@EXAMPLE.COM"
kadmin.local -q "addprinc -randkey hbase/rs1.example.com@EXAMPLE.COM"
kadmin.local -q "addprinc -randkey hbase/rs2.example.com@EXAMPLE.COM"

# Create keytab files
kadmin.local -q "ktadd -k /etc/hbase/conf/hbase.keytab hbase/master.example.com@EXAMPLE.COM"
kadmin.local -q "ktadd -k /etc/hbase/conf/hbase.keytab hbase/rs1.example.com@EXAMPLE.COM"
```

### hbase-site.xml for Kerberos

```xml
<!-- Enable Kerberos authentication -->
<property>
  <name>hbase.security.authentication</name>
  <value>kerberos</value>
</property>

<!-- Enable authorization (required to use ACLs) -->
<property>
  <name>hbase.security.authorization</name>
  <value>true</value>
</property>

<!-- Server-side Kerberos principal (matches keytab) -->
<property>
  <name>hbase.master.kerberos.principal</name>
  <value>hbase/_HOST@EXAMPLE.COM</value>
</property>
<property>
  <name>hbase.regionserver.kerberos.principal</name>
  <value>hbase/_HOST@EXAMPLE.COM</value>
</property>

<!-- Keytab locations -->
<property>
  <name>hbase.master.keytab.file</name>
  <value>/etc/hbase/conf/hbase.keytab</value>
</property>
<property>
  <name>hbase.regionserver.keytab.file</name>
  <value>/etc/hbase/conf/hbase.keytab</value>
</property>

<!-- ZooKeeper authentication -->
<property>
  <name>hbase.zookeeper.quorum</name>
  <value>zk1,zk2,zk3</value>
</property>
<property>
  <name>hbase.zookeeper.property.authProvider.1</name>
  <value>org.apache.zookeeper.server.auth.SASLAuthenticationProvider</value>
</property>
```

### Client Authentication

```java
// Java client with Kerberos
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.security.authentication", "kerberos");
conf.set("hadoop.security.authentication", "kerberos");

// Log in with keytab
UserGroupInformation.setConfiguration(conf);
UserGroupInformation.loginUserFromKeytab(
    "hbase-client@EXAMPLE.COM",
    "/path/to/client.keytab"
);

Connection connection = ConnectionFactory.createConnection(conf);
```

```bash
# Command line: kinit first
kinit -kt /path/to/client.keytab hbase-client@EXAMPLE.COM
hbase shell
```

---

## Authorization — ACLs

Requires `hbase.security.authorization=true` and the `AccessController` coprocessor.

### Enable AccessController

```xml
<!-- hbase-site.xml -->
<property>
  <name>hbase.coprocessor.master.classes</name>
  <value>org.apache.hadoop.hbase.security.access.AccessController</value>
</property>
<property>
  <name>hbase.coprocessor.region.classes</name>
  <value>org.apache.hadoop.hbase.security.access.AccessController</value>
</property>
<property>
  <name>hbase.coprocessor.regionserver.classes</name>
  <value>org.apache.hadoop.hbase.security.access.AccessController</value>
</property>
```

### Permission Levels

| Permission | Code | Scope |
|------------|------|-------|
| Read | R | Can read data |
| Write | W | Can write/delete data |
| Execute | X | Can execute coprocessor endpoints |
| Create | C | Can create/drop tables, alter schemas |
| Admin | A | Can enable/disable, manage permissions |

### Shell ACL Commands

```ruby
# Grant permissions
# Syntax: grant 'user', 'permissions', 'table', 'CF', 'qualifier'

# Global admin (all permissions on all tables)
grant 'alice', 'RWXCA'

# Table-level read+write
grant 'bob', 'RW', 'orders'

# Column-family level
grant 'reporting_user', 'R', 'orders', 'cf'

# Column-level (specific qualifier)
grant 'audit_user', 'R', 'orders', 'cf', 'status'

# Namespace-level
grant 'dev_team', 'RWC', '@dev_namespace'

# Revoke permissions
revoke 'bob', 'orders'
revoke 'reporting_user', 'orders', 'cf'

# View permissions
user_permission 'orders'
user_permission '@dev_namespace'
user_permission            # global permissions
```

### Java API for ACL Management

```java
try (Connection connection = ConnectionFactory.createConnection(conf);
     Admin admin = connection.getAdmin()) {

    // Grant table-level read permission
    UserPermission perm = new UserPermission(
        "bob",
        Permission.newBuilder(TableName.valueOf("orders"))
            .withActions(Permission.Action.READ, Permission.Action.WRITE)
            .build()
    );
    admin.grant(perm, false);

    // Grant CF-level permission
    UserPermission cfPerm = new UserPermission(
        "reporting_user",
        Permission.newBuilder(TableName.valueOf("orders"))
            .withFamily(Bytes.toBytes("cf"))
            .withActions(Permission.Action.READ)
            .build()
    );
    admin.grant(cfPerm, false);

    // Revoke
    admin.revoke(perm);

    // List permissions
    List<UserPermission> perms = admin.getUserPermissions(
        GetUserPermissionsRequest.newBuilder(TableName.valueOf("orders")).build()
    );
}
```

---

## Role-Based Access Control (RBAC)

HBase supports roles for easier permission management:

```ruby
# Create role
add_labels ['developer', 'analyst', 'admin']

# Assign permissions to role
grant '@developer', 'RW', 'orders'
grant '@analyst', 'R', 'orders'

# Assign user to role (via Ranger or shell if supported)
# Note: native RBAC is often managed through Apache Ranger
```

**Apache Ranger** is the recommended way to manage HBase RBAC at scale:
- Centralized policy management for Hadoop ecosystem
- Attribute-based policies
- Audit trail for all access decisions
- Integration with LDAP/AD for group-based policies

---

## Cell-Level Security & Visibility Labels

Cell-level security allows individual cells to have **security labels**. Only users with the appropriate clearance can see those cells.

### Enable VisibilityController

```xml
<property>
  <name>hbase.coprocessor.master.classes</name>
  <value>org.apache.hadoop.hbase.security.access.AccessController,
         org.apache.hadoop.hbase.security.visibility.VisibilityController</value>
</property>
<property>
  <name>hbase.coprocessor.region.classes</name>
  <value>org.apache.hadoop.hbase.security.access.AccessController,
         org.apache.hadoop.hbase.security.visibility.VisibilityController</value>
</property>
```

### Create Visibility Labels

```ruby
# In HBase shell (as super user)
add_labels ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET']
set_auths 'alice', ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET']
set_auths 'bob',   ['PUBLIC', 'INTERNAL']
get_auths 'alice'
```

### Write Cells with Labels

```java
Put put = new Put(Bytes.toBytes("order-001"));
put.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"),
              Bytes.toBytes("shipped"));

// Tag this cell as CONFIDENTIAL
CellVisibility visibility = new CellVisibility("CONFIDENTIAL");
put.setCellVisibility(visibility);

// Complex expression: PUBLIC AND NOT INTERNAL
put.setCellVisibility(new CellVisibility("PUBLIC & !INTERNAL"));

// OR expression
put.setCellVisibility(new CellVisibility("PUBLIC | INTERNAL"));

table.put(put);
```

### Read with Authorization

```java
// Set the active user's labels for this scan/get
Authorizations authorizations = new Authorizations("PUBLIC", "INTERNAL");

Get get = new Get(Bytes.toBytes("order-001"));
get.setAuthorizations(authorizations);  // only cells matching user's labels are returned

Scan scan = new Scan();
scan.setAuthorizations(authorizations);
```

### Visibility Label Expression Grammar

```
LABEL          → a defined label string
EXPR           → LABEL | '(' EXPR ')' | '!' EXPR | EXPR '&' EXPR | EXPR '|' EXPR

Examples:
  "PUBLIC"                    → cells tagged PUBLIC
  "PUBLIC & INTERNAL"         → cells tagged with BOTH
  "PUBLIC | INTERNAL"         → cells tagged with EITHER
  "CONFIDENTIAL & !SECRET"    → CONFIDENTIAL but not SECRET
  "(PUBLIC | INTERNAL) & !SECRET"
```

---

## Transparent Data Encryption (TDE)

Encrypts HFiles and WAL at rest (AES-128 or AES-256).

```xml
<!-- hbase-site.xml -->
<property>
  <name>hbase.crypto.keyprovider</name>
  <value>org.apache.hadoop.hbase.io.crypto.KeyStoreKeyProvider</value>
</property>
<property>
  <name>hbase.crypto.keyprovider.parameters</name>
  <value>jceks:///etc/hbase/conf/hbase.jks?password=changeit</value>
</property>
<property>
  <name>hbase.crypto.master.key.name</name>
  <value>hbase-master-key</value>
</property>
```

Enable per column family:

```java
ColumnFamilyDescriptor cf = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("cf"))
    .setEncryptionType("AES")
    .setEncryptionKey(EncryptionUtil.wrapKey(conf, "cf-encryption-key", keyBytes))
    .build();
```

Shell:
```ruby
create 'secure_orders',
  {NAME => 'cf', ENCRYPTION => 'AES', ENCRYPTION_KEY => '<wrapped-key>'}
```

---

## Audit Logging

AccessController logs access events via Log4j. Configure in `log4j.properties`:

```properties
log4j.logger.SecurityLogger=INFO,RFAS
log4j.appender.RFAS=org.apache.log4j.RollingFileAppender
log4j.appender.RFAS.File=${hbase.log.dir}/hbase-audit.log
log4j.appender.RFAS.MaxFileSize=10MB
log4j.appender.RFAS.MaxBackupIndex=10
log4j.appender.RFAS.layout=org.apache.log4j.PatternLayout
log4j.appender.RFAS.layout.ConversionPattern=%d{ISO8601} %p %c: %m%n
```

Audit log entries include: timestamp, user, action, table/CF/qualifier, result (ALLOWED/DENIED).

For enterprise audit needs, integrate with **Apache Ranger Audit** (writes to HDFS/Solr/Kafka).

---

## Network Encryption (TLS/SSL)

```xml
<!-- hbase-site.xml: enable TLS for all RPC -->
<property>
  <name>hbase.rpc.protection</name>
  <value>privacy</value>  <!-- authentication = auth only; integrity = auth+checksum; privacy = encrypted -->
</property>

<!-- For REST server -->
<property>
  <name>hbase.rest.ssl.enabled</name>
  <value>true</value>
</property>
<property>
  <name>hbase.rest.ssl.keystore.store</name>
  <value>/etc/hbase/conf/hbase.keystore</value>
</property>
<property>
  <name>hbase.rest.ssl.keystore.password</name>
  <value>changeit</value>
</property>

<!-- For Thrift server -->
<property>
  <name>hbase.thrift.ssl.enabled</name>
  <value>true</value>
</property>
```

With Kerberos, RPC protection defaults to `authentication`. Set to `privacy` for full encryption.

---

## Security Checklist

| Item | Status |
|------|--------|
| Kerberos enabled (`hbase.security.authentication=kerberos`) | |
| Authorization enabled (`hbase.security.authorization=true`) | |
| AccessController coprocessor loaded on master + RS | |
| HDFS security enabled (Kerberos for DataNode/NameNode) | |
| ZooKeeper ACLs configured | |
| Service keytabs in place with correct permissions | |
| NTP synchronized across all nodes (critical for Kerberos) | |
| Minimum required permissions granted (principle of least privilege) | |
| Visibility labels configured for sensitive tables | |
| Audit logging enabled and log rotation configured | |
| Network encryption (`hbase.rpc.protection=privacy`) enabled | |
| Encryption at rest enabled for sensitive column families | |
| Regular keytab rotation scheduled | |
