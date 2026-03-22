# Hive CLI & Configuration

## Table of Contents
1. [Beeline Connection](#beeline-connection)
2. [Beeline Usage](#beeline-usage)
3. [Variable Substitution](#variable-substitution)
4. [hiverc Initialization File](#hiverc-initialization-file)
5. [Key Configuration Properties](#key-configuration-properties)
6. [SET Command Reference](#set-command-reference)

---

## Beeline Connection

Beeline is the current Hive CLI (replaced `hive` CLI in Hive 2.x). Connects to HiveServer2 over JDBC.

### Basic connection

```bash
# Interactive mode
beeline -u "jdbc:hive2://hiveserver2-host:10000/default" -n username -p password

# With Kerberos
beeline -u "jdbc:hive2://hiveserver2-host:10000/default;principal=hive/_HOST@REALM.COM"

# With SSL
beeline -u "jdbc:hive2://host:10000/default;ssl=true;sslTrustStore=/path/truststore.jks;trustStorePassword=changeit"

# Connect to specific database
beeline -u "jdbc:hive2://host:10000/mydb"

# Run a single query and exit
beeline -u "jdbc:hive2://host:10000/default" -e "SELECT COUNT(*) FROM orders"

# Run a query file and exit
beeline -u "jdbc:hive2://host:10000/default" -f /path/to/query.sql

# Non-interactive (no header, no progress output — good for scripts)
beeline -u "jdbc:hive2://host:10000/default" \
  --outputformat=tsv2 \
  --showHeader=false \
  --silent=true \
  -e "SELECT order_id, amount FROM orders LIMIT 10"
```

### Output formats

```bash
# --outputformat options:
table       # default: ASCII table
tsv         # tab-separated
tsv2        # tab-separated with header
csv         # comma-separated
csv2        # comma-separated with header
dsv         # delimiter-separated (specify with --delimiterForDSV=|)
json        # JSON array of objects
jsonfile    # one JSON per line
vertical    # one column per line (like MySQL \G)

beeline -u "..." --outputformat=csv2 -e "SELECT * FROM orders LIMIT 5"
```

### HS2 High Availability (ZooKeeper)

```bash
# Connect through ZooKeeper for HA
beeline -u "jdbc:hive2://zk1:2181,zk2:2181,zk3:2181/default;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2"
```

---

## Beeline Usage

### Interactive commands

```sql
-- Connect (within beeline shell)
!connect jdbc:hive2://host:10000/default

-- Disconnect
!close

-- List connections
!list

-- Run file
!run /path/to/script.sql

-- Execute shell command
!sh ls -la /tmp

-- Quit
!quit
!exit

-- Show current settings
!set

-- Change output format
!set outputformat csv2

-- Toggle silent mode (hide progress)
!set silent true
```

### Scripting with Beeline

```bash
#!/bin/bash
# ETL script using Beeline

HIVESERVER="jdbc:hive2://hiveserver2:10000/default"

# Run SQL file
beeline -u "$HIVESERVER" \
  --silent=true \
  --showHeader=false \
  --outputformat=tsv2 \
  -f /opt/etl/load_daily.sql \
  2>/var/log/hive/etl_$(date +%Y%m%d).log

# Check exit code
if [ $? -ne 0 ]; then
  echo "Hive job failed"
  exit 1
fi

# Inline query with variable (passed as hiveconf)
beeline -u "$HIVESERVER" \
  --hiveconf run_date=2024-01-15 \
  -e "INSERT OVERWRITE TABLE orders_archive
      PARTITION (archive_date='\${hiveconf:run_date}')
      SELECT * FROM orders WHERE order_date='\${hiveconf:run_date}'"
```

---

## Variable Substitution

Hive supports variable substitution in queries using `${namespace:varname}` syntax.

### hiveconf — configuration variables

```bash
# Set from command line
beeline -u "..." --hiveconf mydb=analytics --hiveconf run_date=2024-01-15

# Or: beeline -u "..." --hiveconf mydb=analytics
# Then in query:
```

```sql
SELECT * FROM ${hiveconf:mydb}.orders
WHERE order_date = '${hiveconf:run_date}';
```

### hivevar — user variables

```bash
beeline -u "..." --hivevar start_date=2024-01-01 --hivevar end_date=2024-01-31
```

```sql
-- In query file (reference with ${hivevar:name} or just ${name})
SELECT * FROM orders
WHERE order_date BETWEEN '${hivevar:start_date}' AND '${hivevar:end_date}';
```

### SET within queries

```sql
-- Set variable in session
SET hivevar:my_table = orders;
SET hiveconf:run_date = 2024-01-15;

-- Use it
SELECT * FROM ${hivevar:my_table} WHERE order_date = '${hiveconf:run_date}';

-- System variables (read-only)
${system:user.name}    -- OS user running the job
${system:java.io.tmpdir}

-- env variables
${env:HOME}
${env:JAVA_HOME}

-- Disable variable substitution (if $ appears in data)
SET hive.variable.substitute = false;
```

---

## hiverc Initialization File

`$HOME/.hiverc` (or specified with `--hiverc` / `-i` flag) runs automatically at Hive startup.

```sql
-- ~/.hiverc example

-- Set default database
USE analytics;

-- Set execution engine
SET hive.execution.engine = tez;

-- Enable CBO
SET hive.cbo.enable = true;

-- Enable auto map join
SET hive.auto.convert.join = true;
SET hive.mapjoin.smalltable.filesize = 50000000;  -- 50MB

-- Useful display settings for interactive use
SET hive.cli.print.header = true;           -- show column names in output
SET hive.cli.print.current.db = true;       -- show DB in prompt
SET hive.resultset.use.unique.column.names = true;

-- Enable parallel execution
SET hive.exec.parallel = true;
SET hive.exec.parallel.thread.number = 8;

-- Dynamic partitioning
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;
```

---

## Key Configuration Properties

These are the most important properties in `hive-site.xml` (or set per-session with `SET`).

### Execution

```properties
hive.execution.engine = tez                    # tez (default), spark, mr
hive.tez.container.size = 4096                 # MB per Tez container
hive.tez.java.opts = -Xmx3276m                 # JVM heap in Tez container
hive.server2.tez.initialize.default.sessions=true  # warm session pool
hive.server2.tez.sessions.per.default.queue = 4    # pre-warmed session count
```

### Query optimization

```properties
hive.cbo.enable = true                          # Cost-based optimizer
hive.auto.convert.join = true                   # Auto map join for small tables
hive.mapjoin.smalltable.filesize = 25000000     # 25MB map join threshold
hive.optimize.reducededuplication = true        # Remove redundant reducers
hive.exec.parallel = true                       # Parallel independent stages
hive.exec.parallel.thread.number = 8
hive.vectorized.execution.enabled = true        # Vectorized execution
```

### Partitions and dynamic insert

```properties
hive.exec.dynamic.partition = true
hive.exec.dynamic.partition.mode = nonstrict    # All partitions can be dynamic
hive.exec.max.dynamic.partitions = 1000
hive.exec.max.dynamic.partitions.pernode = 100
```

### ACID and transactions

```properties
hive.support.concurrency = true
hive.txn.manager = org.apache.hadoop.hive.ql.lockmgr.DbTxnManager
hive.compactor.initiator.on = true
hive.compactor.worker.threads = 1
hive.compactor.cleaner.on = true
```

### Metastore connection

```properties
javax.jdo.option.ConnectionURL = jdbc:mysql://metastore-host:3306/hive_metastore?useSSL=false
javax.jdo.option.ConnectionDriverName = com.mysql.jdbc.Driver
javax.jdo.option.ConnectionUserName = hive
javax.jdo.option.ConnectionPassword = hive_password
hive.metastore.uris = thrift://metastore-host:9083   # remote metastore
```

### HiveServer2

```properties
hive.server2.thrift.bind.host = 0.0.0.0
hive.server2.thrift.port = 10000
hive.server2.authentication = KERBEROS                # or LDAP, PAM, NONE
hive.server2.enable.doAs = true                       # impersonate query user
hive.server2.max.start.attempts = 30
```

### Logging and stats

```properties
hive.stats.autogather = true                    # auto-collect table stats on insert
hive.stats.column.autogather = false            # column stats (expensive; off by default)
hive.fetch.task.conversion = more               # use Fetch task for simple queries
```

---

## SET Command Reference

```sql
-- Show all settings
SET;

-- Show specific setting
SET hive.execution.engine;

-- Set a property
SET hive.execution.engine = tez;
SET mapreduce.job.reduces = 50;

-- Show only non-default settings
SET -v;  -- verbose: shows all, including default values

-- Useful diagnostic sets
SET hive.query.id;            -- unique ID of current/last query
SET hive.session.id;          -- current HiveServer2 session ID
SET hive.start.cleanup.scratchdir = true;  -- clean temp files on start

-- Common tuning sets for interactive sessions
SET hive.cli.print.header = true;
SET hive.resultset.use.unique.column.names = true;
SET hive.exec.dynamic.partition.mode = nonstrict;
SET hive.auto.convert.join = true;
SET hive.exec.parallel = true;

-- Reset to default (Hive 3.0+)
RESET;                         -- reset ALL settings to defaults
RESET hive.execution.engine;   -- reset specific setting
```

### HiveServer2 connection string parameters

```
jdbc:hive2://host:port/database
  ;user=username
  ;password=password
  ;ssl=true
  ;sslTrustStore=/path/truststore.jks
  ;trustStorePassword=pass
  ;principal=hive/_HOST@REALM.COM       (Kerberos)
  ;hive.server2.proxy.user=other_user   (impersonation)
  ;transportMode=http                    (HTTP mode; default is binary)
  ;httpPath=cliservice                   (HTTP endpoint for HTTP mode)
  ;serviceDiscoveryMode=zooKeeper        (ZK HA)
  ;zooKeeperNamespace=hiveserver2        (ZK path)
```
