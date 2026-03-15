# Governance & Security — Chapters 10-12

Write-Audit-Publish, production monitoring, security layers, encryption, access control, and compliance patterns.

## Table of Contents

- [Write-Audit-Publish (WAP)](#write-audit-publish-wap)
- [Production Monitoring](#production-monitoring)
- [Security Architecture](#security-architecture)
- [Encryption](#encryption)
- [Access Control](#access-control)
- [AWS Lake Formation](#aws-lake-formation)
- [Apache Polaris](#apache-polaris)
- [Compliance Patterns](#compliance-patterns)

---

## Write-Audit-Publish (WAP)

A pattern for validating data before making it visible to consumers. Write to a staging branch, audit the data, then publish.

### Enable WAP

```sql
ALTER TABLE catalog.db.events SET TBLPROPERTIES (
  'write.wap.enabled' = 'true'
);
```

### WAP workflow

```sql
-- Step 1: Create a staging branch
ALTER TABLE catalog.db.events CREATE BRANCH staging;

-- Step 2: Write to the staging branch
INSERT INTO catalog.db.events.branch_staging
SELECT * FROM raw_data;

-- Step 3: Audit the staged data
SELECT COUNT(*) FROM catalog.db.events VERSION AS OF 'staging';
SELECT * FROM catalog.db.events VERSION AS OF 'staging'
WHERE amount < 0;  -- check for invalid data

-- Step 4: If valid, fast-forward main to include staged data
CALL catalog.system.fast_forward('db.events', 'main', 'staging');

-- Step 5: Drop the staging branch
ALTER TABLE catalog.db.events DROP BRANCH staging;
```

### WAP with Spark session

```python
# Set WAP ID on session (alternative to branches)
spark.conf.set("spark.wap.id", "job-20240615-001")

# Writes are staged, not immediately visible
df.writeTo("catalog.db.events").append()

# Audit
audit_df = spark.read \
    .option("snapshot-id", staged_snapshot_id) \
    .table("catalog.db.events")

# Publish by cherry-picking
spark.sql(f"CALL catalog.system.cherrypick_snapshot('db.events', {staged_snapshot_id})")
```

### WAP use cases

| Use case | Implementation |
|----------|---------------|
| Data quality gates | Write → validate constraints → publish |
| Pre-production testing | Write to branch → run test queries → fast-forward |
| Regulatory compliance | Audit staged data → approval workflow → publish |
| A/B data pipelines | Write to separate branches → compare → merge winner |

## Production Monitoring

### Key metrics to monitor

```sql
-- Table size and file count
SELECT
  COUNT(*) AS file_count,
  SUM(file_size_in_bytes) / (1024*1024*1024) AS total_gb,
  AVG(file_size_in_bytes) / (1024*1024) AS avg_file_mb
FROM catalog.db.events.files;

-- Snapshot growth rate
SELECT
  snapshot_id,
  committed_at,
  operation,
  summary['added-data-files'] AS added_files,
  summary['added-records'] AS added_records,
  summary['total-data-files'] AS total_files,
  summary['total-records'] AS total_records
FROM catalog.db.events.snapshots
ORDER BY committed_at DESC
LIMIT 20;

-- Delete file accumulation (MOR tables)
SELECT
  content,
  COUNT(*) AS count,
  SUM(file_size_in_bytes) / (1024*1024) AS total_mb
FROM catalog.db.events.all_data_files
GROUP BY content;
-- 0 = data, 1 = position deletes, 2 = equality deletes

-- Partition skew
SELECT
  partition,
  file_count,
  record_count,
  record_count / file_count AS avg_records_per_file
FROM catalog.db.events.partitions
ORDER BY record_count DESC;
```

### Health check alerts

| Condition | Alert | Action |
|-----------|-------|--------|
| avg_file_mb < 32 | Small file problem | Run compaction |
| delete_file_count > data_file_count * 0.5 | Delete file accumulation | Run compaction |
| snapshot_count > 1000 | Snapshot bloat | Expire old snapshots |
| orphan file size growing | Orphan file accumulation | Run orphan file cleanup |
| manifest_count > 10 × partition_count | Manifest bloat | Rewrite manifests |

### Automated maintenance

```python
# Maintenance job (run on schedule)
def run_maintenance(spark, table_name):
    # 1. Compact small files
    spark.sql(f"""
        CALL catalog.system.rewrite_data_files(
            table => '{table_name}',
            options => map(
                'min-file-size-bytes', '67108864',
                'target-file-size-bytes', '536870912'
            )
        )
    """)

    # 2. Expire old snapshots (keep 7 days)
    spark.sql(f"""
        CALL catalog.system.expire_snapshots(
            table => '{table_name}',
            older_than => current_timestamp() - INTERVAL 7 DAYS,
            retain_last => 10
        )
    """)

    # 3. Remove orphan files (older than 3 days)
    spark.sql(f"""
        CALL catalog.system.remove_orphan_files(
            table => '{table_name}',
            older_than => current_timestamp() - INTERVAL 3 DAYS
        )
    """)

    # 4. Rewrite manifests
    spark.sql(f"""
        CALL catalog.system.rewrite_manifests('{table_name}')
    """)
```

## Security Architecture

Iceberg security operates at multiple layers:

```
Application Layer     →  Query engine access control (Trino ACLs, Spark ACLs)
Catalog Layer         →  Catalog-level RBAC (Polaris, Lake Formation, Nessie)
                         Credential vending (catalog provides scoped storage creds)
Metadata Layer        →  Encryption of metadata files
Data Layer            →  Encryption of data files (Parquet/ORC encryption)
Storage Layer         →  Object storage policies (S3 bucket policies, IAM)
                         Server-side encryption (SSE-S3, SSE-KMS, SSE-C)
```

### Defense in depth

| Layer | Mechanism |
|-------|-----------|
| Storage | IAM policies, bucket policies, VPC endpoints |
| Encryption at rest | SSE-S3, SSE-KMS, or client-side encryption |
| Encryption in transit | TLS for all catalog and storage communication |
| Catalog | RBAC, credential vending, namespace permissions |
| Engine | Row/column security, masking, audit logs |

## Encryption

### Storage-level encryption

#### AWS S3

```python
# SSE-S3 (Amazon managed keys)
spark.conf.set("spark.hadoop.fs.s3a.server-side-encryption-algorithm", "AES256")

# SSE-KMS (customer managed keys)
spark.conf.set("spark.hadoop.fs.s3a.server-side-encryption-algorithm", "SSE-KMS")
spark.conf.set("spark.hadoop.fs.s3a.server-side-encryption.key", "arn:aws:kms:...")
```

#### Azure Blob Storage

Azure Storage Service Encryption (SSE) enabled by default. Customer-managed keys via Azure Key Vault.

#### Google Cloud Storage

Default encryption with Google-managed keys. Customer-managed keys via Cloud KMS.

### Parquet column-level encryption (preview)

```python
# Encrypt specific columns
spark.conf.set("parquet.encryption.column.keys",
    "key1:ssn,credit_card;key2:email")
spark.conf.set("parquet.encryption.footer.key", "footer_key")
spark.conf.set("parquet.encryption.kms.client.class",
    "org.apache.parquet.crypto.keytools.InMemoryKmsClient")
```

## Access Control

### Catalog-level access control

Access control depends on the catalog implementation:

| Catalog | Access control |
|---------|---------------|
| REST Catalog | Depends on server implementation (Polaris, Nessie, etc.) |
| Hive Metastore | Ranger, Sentry, or custom authorization |
| AWS Glue | IAM policies, Lake Formation |
| Nessie | Built-in RBAC, branch-level permissions |

### Storage-level access control (S3 example)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/warehouse/db/events/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/team": "analytics"
        }
      }
    }
  ]
}
```

### Credential vending

Modern catalogs (Polaris, REST catalog implementations) support credential vending:

1. Client authenticates with catalog
2. Catalog checks permissions
3. Catalog returns scoped, temporary storage credentials
4. Client uses these credentials to access data files directly
5. Credentials are limited to specific tables/partitions

This avoids giving clients broad storage access.

## AWS Lake Formation

### Fine-grained access control

```python
# Lake Formation provides cell-level security for Iceberg tables
# Configuration is done through AWS Console or API, not SQL

# Lake Formation permissions:
# - Table-level: SELECT, INSERT, DELETE, DESCRIBE, ALTER, DROP
# - Column-level: SELECT on specific columns
# - Row-level: Filter rows based on conditions
# - Cell-level: Combination of row and column filters
```

### Lake Formation with Athena

```sql
-- Tables registered in Lake Formation inherit its permissions
-- No additional configuration in Athena queries
SELECT * FROM db.events;  -- Lake Formation filters rows/columns automatically
```

## Apache Polaris

Open-source catalog with built-in RBAC and credential vending:

### Polaris RBAC model

```
Principal (user/role)
  └── Granted Privileges
       ├── CATALOG_MANAGE_CONTENT → full catalog control
       ├── NAMESPACE_CREATE → create namespaces
       ├── TABLE_READ_DATA → read table data
       ├── TABLE_WRITE_DATA → write table data
       ├── TABLE_CREATE → create tables
       ├── TABLE_DROP → drop tables
       └── VIEW_CREATE → create views
```

### Polaris configuration

```python
# Spark with Polaris catalog
spark.conf.set("spark.sql.catalog.polaris", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.polaris.type", "rest")
spark.conf.set("spark.sql.catalog.polaris.uri", "https://polaris.example.com/api/catalog")
spark.conf.set("spark.sql.catalog.polaris.credential", "client_id:client_secret")
spark.conf.set("spark.sql.catalog.polaris.scope", "PRINCIPAL_ROLE:analyst")
```

## Compliance Patterns

### GDPR right to erasure

```sql
-- Delete specific user's data across tables
DELETE FROM catalog.db.bronze_events WHERE user_id = 'user-to-forget';
DELETE FROM catalog.db.silver_events WHERE user_id = 'user-to-forget';
DELETE FROM catalog.db.gold_metrics WHERE user_id = 'user-to-forget';

-- Compact to physically merge delete files into data files
CALL catalog.system.rewrite_data_files('db.bronze_events');
CALL catalog.system.rewrite_data_files('db.silver_events');

-- Expire old snapshots that reference pre-deletion data
CALL catalog.system.expire_snapshots('db.bronze_events',
    TIMESTAMP '...');

-- Remove orphan files to physically delete old data
CALL catalog.system.remove_orphan_files('db.bronze_events');
```

**Important**: Until snapshots are expired AND orphan files removed, the deleted data still exists on storage.

### GDPR data portability

```python
user_data = spark.sql("""
    SELECT * FROM catalog.db.events WHERE user_id = 'requesting-user'
""")
user_data.write.format("json").save("/exports/user-requesting-user/")
```

### Audit trail

```sql
-- Use snapshot history as audit trail
SELECT
  snapshot_id,
  committed_at,
  operation,
  summary
FROM catalog.db.events.snapshots
ORDER BY committed_at DESC;

-- Tag audit points
ALTER TABLE catalog.db.events CREATE TAG `audit_2024_q2`
  RETAIN 2555 DAYS;  -- 7 years for compliance
```

### Data retention

```sql
-- Delete data beyond retention period
DELETE FROM catalog.db.events
WHERE event_time < current_timestamp() - INTERVAL 2 YEARS;

-- Clean up physical files
CALL catalog.system.rewrite_data_files('db.events');
CALL catalog.system.expire_snapshots('db.events',
    older_than => current_timestamp() - INTERVAL 7 DAYS);
CALL catalog.system.remove_orphan_files('db.events');
```

### PII tracking with table properties

```sql
-- Mark tables containing PII
ALTER TABLE catalog.db.customers SET TBLPROPERTIES (
  'pii.contains' = 'true',
  'pii.columns' = 'email,phone,ssn',
  'pii.classification' = 'confidential',
  'data.owner' = 'privacy-team@company.com',
  'data.retention' = '7 years'
);
```
