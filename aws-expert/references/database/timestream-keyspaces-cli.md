# AWS Timestream & Keyspaces — CLI Reference
For service concepts, see [timestream-keyspaces-capabilities.md](timestream-keyspaces-capabilities.md).

## Amazon Timestream

```bash
# --- Write (timestream-write) ---
aws timestream-write create-database \
  --database-name MyMetricsDB

aws timestream-write list-databases
aws timestream-write describe-database --database-name MyMetricsDB

aws timestream-write update-database \
  --database-name MyMetricsDB \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/my-cmk

aws timestream-write delete-database --database-name MyMetricsDB

# Create table with memory and magnetic store retention
aws timestream-write create-table \
  --database-name MyMetricsDB \
  --table-name AppMetrics \
  --retention-properties '{
    "MemoryStoreRetentionPeriodInHours": 24,
    "MagneticStoreRetentionPeriodInDays": 365
  }' \
  --magnetic-store-write-properties '{
    "EnableMagneticStoreWrites": true
  }'

aws timestream-write list-tables --database-name MyMetricsDB
aws timestream-write describe-table --database-name MyMetricsDB --table-name AppMetrics

aws timestream-write update-table \
  --database-name MyMetricsDB \
  --table-name AppMetrics \
  --retention-properties '{
    "MemoryStoreRetentionPeriodInHours": 48,
    "MagneticStoreRetentionPeriodInDays": 730
  }'

aws timestream-write delete-table --database-name MyMetricsDB --table-name AppMetrics

# Write records (multi-measure)
aws timestream-write write-records \
  --database-name MyMetricsDB \
  --table-name AppMetrics \
  --common-attributes '{
    "Dimensions": [
      {"Name":"region","Value":"us-east-1"},
      {"Name":"service","Value":"web-server"}
    ],
    "Time": "1705312800000",
    "TimeUnit": "MILLISECONDS"
  }' \
  --records '[
    {
      "MeasureName": "cpu_utilization",
      "MeasureValue": "45.2",
      "MeasureValueType": "DOUBLE"
    },
    {
      "MeasureName": "memory_used_mb",
      "MeasureValue": "2048",
      "MeasureValueType": "BIGINT"
    }
  ]'

# --- Query (timestream-query) ---
aws timestream-query query \
  --query-string "SELECT * FROM \"MyMetricsDB\".\"AppMetrics\" WHERE time >= ago(1h) ORDER BY time DESC LIMIT 10"

# Query with time binning
aws timestream-query query \
  --query-string "
    SELECT
      region,
      bin(time, 5m) AS binned_time,
      AVG(measure_value::double) AS avg_cpu
    FROM \"MyMetricsDB\".\"AppMetrics\"
    WHERE measure_name = 'cpu_utilization'
      AND time >= ago(1h)
    GROUP BY region, bin(time, 5m)
    ORDER BY binned_time DESC
  "

# List query endpoints (for SDK connection)
aws timestream-query describe-endpoints

# --- Scheduled Queries ---
aws timestream-query create-scheduled-query \
  --name HourlyAggregates \
  --query-string "
    SELECT
      bin(time, 1h) AS hour,
      region,
      AVG(measure_value::double) AS avg_cpu
    FROM \"MyMetricsDB\".\"AppMetrics\"
    WHERE measure_name = 'cpu_utilization'
    GROUP BY bin(time, 1h), region
  " \
  --schedule-configuration '{"ScheduleExpression":"cron(0 * * * ? *)"}' \
  --notification-configuration '{"SnsConfiguration":{"TopicArn":"arn:aws:sns:us-east-1:123456789012:ts-alerts"}}' \
  --target-configuration '{
    "TimestreamConfiguration": {
      "DatabaseName": "MyMetricsDB",
      "TableName": "HourlyAggregatesTable",
      "TimeColumn": "hour",
      "DimensionMappings": [{"Name":"region","DimensionValueType":"VARCHAR"}],
      "MeasureNameColumn": "measure_name",
      "MixedMeasureMappings": [{"MeasureValueType":"DOUBLE","TargetMeasureName":"avg_cpu"}]
    }
  }' \
  --scheduled-query-execution-role-arn arn:aws:iam::123456789012:role/TimestreamScheduledQueryRole

aws timestream-query list-scheduled-queries
aws timestream-query describe-scheduled-query --scheduled-query-arn arn:aws:timestream:...

aws timestream-query execute-scheduled-query \
  --scheduled-query-arn arn:aws:timestream:... \
  --invocation-time 2024-01-15T12:00:00Z

aws timestream-query delete-scheduled-query --scheduled-query-arn arn:aws:timestream:...
```

---

## Amazon Keyspaces

```bash
# --- Keyspaces ---
aws keyspaces create-keyspace --keyspace-name mykeyspace

aws keyspaces list-keyspaces
aws keyspaces get-keyspace --keyspace-name mykeyspace

aws keyspaces delete-keyspace --keyspace-name mykeyspace

# --- Tables ---
# Create a table (CQL schema expressed in CLI)
aws keyspaces create-table \
  --keyspace-name mykeyspace \
  --table-name users \
  --schema-definition '{
    "allColumns": [
      {"name":"user_id","type":"uuid"},
      {"name":"email","type":"text"},
      {"name":"created_at","type":"timestamp"},
      {"name":"age","type":"int"}
    ],
    "partitionKeys": [{"name":"user_id"}],
    "clusteringKeys": []
  }' \
  --capacity-specification '{"throughputMode":"PAY_PER_REQUEST"}' \
  --point-in-time-recovery '{"status":"ENABLED"}' \
  --encryption-specification '{"type":"CUSTOMER_MANAGED_KMS_KEY","kmsKeyIdentifier":"arn:aws:kms:us-east-1:123456789012:key/my-cmk"}'

# Provisioned capacity table with clustering key
aws keyspaces create-table \
  --keyspace-name mykeyspace \
  --table-name orders \
  --schema-definition '{
    "allColumns": [
      {"name":"customer_id","type":"uuid"},
      {"name":"order_id","type":"timeuuid"},
      {"name":"status","type":"text"},
      {"name":"total","type":"decimal"}
    ],
    "partitionKeys": [{"name":"customer_id"}],
    "clusteringKeys": [{"name":"order_id","orderBy":"DESC"}]
  }' \
  --capacity-specification '{
    "throughputMode":"PROVISIONED",
    "readCapacityUnits":10,
    "writeCapacityUnits":10
  }'

aws keyspaces list-tables --keyspace-name mykeyspace
aws keyspaces get-table --keyspace-name mykeyspace --table-name users

aws keyspaces update-table \
  --keyspace-name mykeyspace \
  --table-name users \
  --capacity-specification '{"throughputMode":"PAY_PER_REQUEST"}'

# Restore table to point in time
aws keyspaces restore-table \
  --source-keyspace-name mykeyspace \
  --source-table-name users \
  --target-keyspace-name mykeyspace \
  --target-table-name users-restored \
  --restore-timestamp 2024-01-15T10:00:00Z

aws keyspaces delete-table --keyspace-name mykeyspace --table-name users

# --- Tags ---
aws keyspaces tag-resource \
  --resource-arn arn:aws:cassandra:us-east-1:123456789012:/keyspace/mykeyspace/table/users \
  --tags key=Environment,value=production

aws keyspaces list-tags-for-resource \
  --resource-arn arn:aws:cassandra:us-east-1:123456789012:/keyspace/mykeyspace/table/users
```
