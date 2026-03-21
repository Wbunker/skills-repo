# Ecosystem Integration
## Chapter 7: Hive Metastore, HBase, HDFS, S3/ADLS, Spark SQL, JDBC/ODBC

---

## Hive Metastore Integration

Impala and Hive share the **Hive Metastore** (HMS) — the central repository for database, table, and partition definitions. This is the primary integration point in the Hadoop ecosystem.

### How the Shared Metastore Works

```
Hive writes data (ETL job) → Hive DDL creates/modifies tables in HMS
                                     │
                              Hive Metastore DB
                                     │
            catalogd polls HMS → caches metadata → propagates to all impalads
                                     │
                             Impala queries the tables
```

### Schema Compatibility

Tables created in Hive are immediately visible to Impala, and vice versa, **with caveats**:

| Feature | Hive Support | Impala Support |
|---------|-------------|----------------|
| Parquet tables | Yes | Yes (preferred) |
| ORC tables | Yes (ACID too) | Read ORC; no ACID write |
| Avro tables | Yes | Yes |
| Text tables | Yes | Yes |
| SerDe customization | Yes (many SerDes) | Limited (built-in only) |
| Hive-style macros | Yes | No |
| Hive ACID / transactional tables | Yes | Read-only (Impala 3.3+) |
| Bucketing | Yes | Read-only (Impala ignores for optimization) |
| Complex types | Yes | Yes (ARRAY/MAP/STRUCT in Parquet/Avro) |

### Metadata Synchronization

After Hive (or another tool) modifies tables, Impala's catalogd cache must be updated:

```sql
-- Reload all metadata from Hive Metastore (drops all cached metadata)
-- Use when: tables were created/dropped outside Impala; schema changes
INVALIDATE METADATA;                    -- reload everything (slow)
INVALIDATE METADATA my_db.my_table;     -- reload one table (faster)

-- Reload file/partition metadata for one table (keeps column stats)
-- Use when: new files added to HDFS by Hive/Spark; new partitions added
REFRESH my_db.my_table;
REFRESH my_db.my_table PARTITION (dt='2024-01-15');
```

**Rule of thumb:**
- Hive adds new files to an existing partition → `REFRESH table`
- Hive creates a new table or adds a partition definition → `INVALIDATE METADATA table`
- Hive drops/renames a table → `INVALIDATE METADATA` (whole database)

### Common ETL Pattern: Hive Writes, Impala Reads

```bash
# 1. Hive ETL job writes Parquet to HDFS
hive -e "INSERT INTO sales_by_day PARTITION (dt='2024-01-15')
         SELECT order_id, amount FROM orders WHERE ..."

# 2. After job completes, notify Impala
impala-shell -q "REFRESH sales_by_day PARTITION (dt='2024-01-15')"

# 3. Analysts query via Impala
impala-shell -q "SELECT SUM(amount) FROM sales_by_day WHERE dt='2024-01-15'"
```

---

## HBase Integration

Impala can query HBase tables directly using the Hive-HBase storage handler.

### HBase Table as Impala External Table

```sql
-- The HBase table must first be mapped in Hive using HBaseStorageHandler
-- Then it appears in Impala via the shared Hive Metastore

-- In Hive (one-time setup):
CREATE EXTERNAL TABLE hbase_users (
    user_id    STRING,   -- HBase row key
    name       STRING,
    email      STRING,
    country    STRING
)
STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES (
    "hbase.columns.mapping" = ":key,profile:name,profile:email,profile:country"
)
TBLPROPERTIES ("hbase.table.name" = "users");

-- In Impala (after INVALIDATE METADATA):
SELECT * FROM hbase_users WHERE user_id = 'user_12345';
```

### HBase Join Patterns

The primary use case for HBase + Impala is **key-value lookups** joined with HDFS fact tables:

```sql
-- Typical pattern: large HDFS table + small HBase lookup
SELECT e.event_id, e.event_type, u.name, u.country
FROM events e
JOIN hbase_users u ON e.user_id = u.user_id
WHERE e.dt = '2024-01-15';
```

**Performance notes:**
- Impala issues individual row key lookups to HBase for each probe row
- Works well when: HBase table is used as a lookup (small result set per join)
- Avoid: full-scan joins against large HBase tables (very slow; HBase is not columnar)
- The HBase region server must be accessible from all impalad nodes

---

## HDFS Integration

Impala reads data directly from HDFS DataNodes using a short-circuit read mechanism (when running on the same nodes).

### HDFS File Layout Best Practices

```
/user/hive/warehouse/mydb.db/
├── orders/                          ← unpartitioned table
│   ├── part-00000.parquet
│   └── part-00001.parquet
└── sales_by_day/                    ← partitioned table
    ├── dt=2024-01-14/
    │   └── part-00000.parquet
    └── dt=2024-01-15/
        └── part-00000.parquet
```

**File naming**: Impala ignores file names; it scans all files in the partition directory. Files starting with `_` or `.` are skipped (hidden files used by Hive).

### HDFS Commands for Impala Workflows

```bash
# Check data location
hdfs dfs -ls /user/hive/warehouse/mydb.db/orders/

# Load files into table location (then REFRESH)
hdfs dfs -put local_file.parquet /user/hive/warehouse/mydb.db/orders/
impala-shell -q "REFRESH orders"

# Check file sizes (ensure files are reasonably sized, not tiny)
hdfs dfs -ls -h /user/hive/warehouse/mydb.db/orders/

# Remove old partition
hdfs dfs -rm -r /user/hive/warehouse/mydb.db/sales_by_day/dt=2023-01-01/
impala-shell -q "ALTER TABLE sales_by_day DROP PARTITION (dt='2023-01-01')"
```

---

## Amazon S3 / Azure ADLS / Object Storage

Impala can read from and write to cloud object storage using HDFS-compatible connectors.

### S3-Backed Tables

```sql
-- External table pointing to S3
CREATE EXTERNAL TABLE s3_orders (
    order_id BIGINT,
    customer STRING,
    amount   DOUBLE
)
STORED AS PARQUET
LOCATION 's3a://my-bucket/data/orders/';

-- Partitioned external table on S3
CREATE EXTERNAL TABLE s3_sales (
    order_id BIGINT,
    amount   DECIMAL(10,2)
)
PARTITIONED BY (dt STRING)
STORED AS PARQUET
LOCATION 's3a://my-bucket/data/sales/';

-- Recover partitions from S3 directory structure
ALTER TABLE s3_sales RECOVER PARTITIONS;
```

**S3 configuration (in core-site.xml or Impala startup):**
```xml
<property>
  <name>fs.s3a.access.key</name>
  <value>AKIAIOSFODNN7EXAMPLE</value>
</property>
<property>
  <name>fs.s3a.secret.key</name>
  <value>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</value>
</property>
<!-- Or use IAM role-based auth (preferred) -->
<property>
  <name>fs.s3a.aws.credentials.provider</name>
  <value>com.amazonaws.auth.InstanceProfileCredentialsProvider</value>
</property>
```

**S3 performance tips:**
- Use `s3a://` (not `s3://` or `s3n://`) — s3a is the modern, performant connector
- Parquet with large row groups (256 MB+) reduces S3 request count
- Avoid many tiny files — S3 LIST operations are expensive
- Co-locate impalad and S3 in the same AWS region to reduce latency

### ADLS Gen2 (Azure)

```sql
CREATE EXTERNAL TABLE adls_sales (...)
STORED AS PARQUET
LOCATION 'abfss://container@account.dfs.core.windows.net/data/sales/';
```

---

## Apache Spark Interoperability

Impala and Spark share the Hive Metastore — tables created in either are visible to both.

### Common Patterns

**Spark writes → Impala reads:**
```python
# PySpark: write Parquet to HDFS with Hive metastore registration
df.write \
  .mode('overwrite') \
  .option('path', '/user/hive/warehouse/mydb.db/orders/') \
  .saveAsTable('mydb.orders')

# Then in Impala:
# INVALIDATE METADATA mydb.orders;
# SELECT * FROM mydb.orders;
```

**Impala writes → Spark reads:**
```sql
-- Impala creates and populates a table
INSERT INTO parquet_results SELECT ...;
```
```python
# Spark reads it
df = spark.table('mydb.parquet_results')
```

**Delta Lake / Iceberg with Impala (Impala 4.x+):**
- Impala 4.x adds read support for Iceberg tables
- Impala can read Iceberg tables registered in the Hive Metastore
- Write support is limited; prefer Spark for Iceberg writes

---

## JDBC / ODBC Connectivity

### Connection Parameters

| Parameter | Value |
|-----------|-------|
| Driver | Cloudera Impala JDBC Driver or open-source ImpalaJDBC |
| Port | 21050 (HiveServer2 protocol; default) |
| Protocol | Binary (default) or HTTP |
| URL | `jdbc:impala://host:21050/database` |

### JDBC Connection String Examples

```java
// Basic
String url = "jdbc:impala://impala-host:21050/analytics";

// With Kerberos
String url = "jdbc:impala://impala-host:21050/analytics;AuthMech=1;" +
             "KrbRealm=EXAMPLE.COM;KrbHostFQDN=impala-host;" +
             "KrbServiceName=impala";

// With LDAP
String url = "jdbc:impala://impala-host:21050/analytics;AuthMech=3;" +
             "UID=analyst;PWD=secret";

// With SSL
String url = "jdbc:impala://impala-host:21050/analytics;SSL=1;" +
             "SSLTrustStore=/path/to/truststore.jks";
```

### ODBC (BI Tools — Tableau, Power BI, Looker)

1. Install Cloudera Impala ODBC Driver
2. Configure DSN with host, port (21050), database, auth method
3. Set `UseNativeQuery=1` for Tableau to pass SQL directly
4. For best performance with Tableau: use Parquet tables + COMPUTE STATS

### HiveServer2 Protocol

Impala exposes the HiveServer2 (HS2) protocol on port 21050. Most tools that support Hive via JDBC/ODBC also support Impala via the same driver infrastructure — just change the hostname/port.

### Programmatic Access (Python)

```python
from impala.dbapi import connect

conn = connect(host='impala-host', port=21050, database='analytics')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM orders WHERE dt = "2024-01-15"')
print(cursor.fetchone())

# With pandas
from impala.util import as_pandas
cursor.execute('SELECT * FROM orders LIMIT 1000')
df = as_pandas(cursor)
```
Install: `pip install impyla`
