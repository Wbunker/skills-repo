# Ch 3 — Setting Up Oozie

## Table of Contents
- [Prerequisites](#prerequisites)
- [Build & Install](#build--install)
- [oozie-site.xml Key Properties](#oozie-sitexml-key-properties)
- [Database Setup](#database-setup)
- [Shared Library](#shared-library)
- [Kerberos Security](#kerberos-security)
- [High Availability (HA)](#high-availability-ha)
- [Start & Verify](#start--verify)

---

## Prerequisites

- Java 8+
- Hadoop cluster (YARN)
- Maven (if building from source)
- Supported DB: Derby (dev only), MySQL, Oracle, PostgreSQL, SQL Server

**Critical:** Database timezone **must be UTC/GMT** — non-UTC causes DST errors in coordinator action materialization.

---

## Build & Install

```bash
# From source
mvn clean package assembly:single -DskipTests -Puber
tar xzf oozie-*.tar.gz
cd oozie-*

# Or use distro package (HDP, CDH include Oozie pre-built)
```

---

## oozie-site.xml Key Properties

```xml
<!-- Database -->
<property><name>oozie.service.JPAService.jdbc.driver</name>
  <value>com.mysql.jdbc.Driver</value></property>
<property><name>oozie.service.JPAService.jdbc.url</name>
  <value>jdbc:mysql://dbhost:3306/oozie?useSSL=false</value></property>
<property><name>oozie.service.JPAService.jdbc.username</name><value>oozie</value></property>
<property><name>oozie.service.JPAService.jdbc.password</name><value>secret</value></property>
<property><name>oozie.service.JPAService.pool.max.active.conn</name><value>10</value></property>

<!-- Server URL (used in callbacks) -->
<property><name>oozie.base.url</name>
  <value>http://oozie-server:11000/oozie</value></property>

<!-- Hadoop access -->
<property><name>oozie.service.HadoopAccessorService.hadoop.configurations</name>
  <value>*=/etc/hadoop/conf</value></property>

<!-- Action retry defaults -->
<property><name>oozie.action.retries.max</name><value>3</value></property>
<property><name>oozie.action.retry.interval</name><value>10</value></property>
<property><name>oozie.action.retry.policy</name><value>periodic</value></property>
<!-- periodic | exponential -->

<!-- Purge old jobs (days) -->
<property><name>oozie.service.PurgeService.older.than</name><value>30</value></property>
<property><name>oozie.service.PurgeService.coordinator.older.than</name><value>7</value></property>

<!-- Max concurrent running workflows per user -->
<property><name>oozie.service.AuthorizationService.default.group.as.acl</name><value>false</value></property>
```

---

## Database Setup

```bash
# Initialize schema
bin/ooziedb.sh create -sqlfile oozie.sql -run

# Or just generate SQL for DBA review
bin/ooziedb.sh create -sqlfile oozie.sql

# Upgrade existing schema
bin/ooziedb.sh upgrade -run
```

MySQL setup:
```sql
CREATE DATABASE oozie DEFAULT CHARACTER SET utf8;
CREATE USER 'oozie'@'%' IDENTIFIED BY 'secret';
GRANT ALL PRIVILEGES ON oozie.* TO 'oozie'@'%';
```
Add MySQL JDBC JAR to `libext/`.

---

## Shared Library

Shared libraries are JARs on HDFS used by workflow actions (Hive, Pig, Spark, Sqoop, etc.).

```bash
# Deploy sharelib to HDFS
bin/oozie-setup.sh sharelib create -fs hdfs://namenode:8020

# Update sharelib at runtime without restart
oozie admin -sharelibupdate

# List installed sharelibs
oozie admin -shareliblist
oozie admin -shareliblist pig

# Custom sharelib mapping
# oozie-site.xml:
# oozie.service.ShareLibService.mapping.file = /path/to/sharelib.properties
```

In `job.properties`, always add:
```properties
oozie.use.system.libpath=true
```
Without this, Hive/Pig/Spark actions fail with ClassNotFoundException.

---

## Kerberos Security

```xml
<!-- oozie-site.xml -->
<property><name>oozie.authentication.type</name><value>kerberos</value></property>
<property><name>oozie.authentication.kerberos.principal</name>
  <value>HTTP/oozie-host@REALM.COM</value></property>
<property><name>oozie.authentication.kerberos.keytab</name>
  <value>/etc/security/keytabs/spnego.service.keytab</value></property>
<property><name>oozie.authentication.kerberos.name.rules</name>
  <value>DEFAULT</value></property>

<property><name>oozie.service.HadoopAccessorService.kerberos.enabled</name><value>true</value></property>
<property><name>oozie.service.HadoopAccessorService.kerberos.principal</name>
  <value>oozie/oozie-host@REALM.COM</value></property>
<property><name>oozie.service.HadoopAccessorService.keytab.file</name>
  <value>/etc/security/keytabs/oozie.service.keytab</value></property>
```

Hadoop `core-site.xml` must also allow Oozie to proxy users:
```xml
<property><name>hadoop.proxyuser.oozie.hosts</name><value>*</value></property>
<property><name>hadoop.proxyuser.oozie.groups</name><value>*</value></property>
```

---

## High Availability (HA)

Requires: ZooKeeper ensemble (≥3 nodes) + shared database (not Derby).

```xml
<!-- oozie-site.xml on ALL Oozie nodes -->
<property>
  <name>oozie.services.ext</name>
  <value>
    org.apache.oozie.service.ZKLocksService,
    org.apache.oozie.service.ZKXLogStreamingService,
    org.apache.oozie.service.ZKJobsConcurrencyService,
    org.apache.oozie.service.ZKUUIDService
  </value>
</property>
<property><name>oozie.zookeeper.connection.string</name>
  <value>zk1:2181,zk2:2181,zk3:2181</value></property>
<!-- Point to load balancer, not individual host -->
<property><name>oozie.base.url</name>
  <value>http://oozie-lb:11000/oozie</value></property>
<!-- Kerberos ZK: -->
<property><name>oozie.zookeeper.secure</name><value>true</value></property>
```

Check all servers: `oozie admin -servers`

---

## Start & Verify

```bash
bin/oozie-start.sh
bin/oozie-stop.sh
bin/oozie-run.sh   # foreground

# Verify
oozie admin -oozie http://localhost:11000/oozie -status
# → System mode: NORMAL

# Set system mode
oozie admin -systemmode SAFEMODE    # queues new submissions
oozie admin -systemmode NOWEBSERVICE
oozie admin -systemmode NORMAL
```
