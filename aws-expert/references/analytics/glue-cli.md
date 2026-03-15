# AWS Glue — CLI Reference
For service concepts, see [glue-capabilities.md](glue-capabilities.md).

## AWS Glue

```bash
# --- Data Catalog: databases ---
aws glue create-database \
  --database-input '{"Name": "my_db", "Description": "Analytics database"}'

aws glue get-database --name my_db
aws glue list-databases
aws glue delete-database --name my_db

# --- Data Catalog: tables ---
aws glue create-table \
  --database-name my_db \
  --table-input '{
    "Name": "orders",
    "StorageDescriptor": {
      "Columns": [
        {"Name": "order_id", "Type": "string"},
        {"Name": "amount", "Type": "double"}
      ],
      "Location": "s3://my-bucket/orders/",
      "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
      "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
      "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"}
    },
    "PartitionKeys": [{"Name": "dt", "Type": "string"}]
  }'

aws glue get-tables --database-name my_db
aws glue delete-table --database-name my_db --name orders

# --- Crawlers ---
aws glue create-crawler \
  --name my-s3-crawler \
  --role arn:aws:iam::123456789012:role/GlueCrawlerRole \
  --database-name my_db \
  --targets '{"S3Targets": [{"Path": "s3://my-bucket/data/"}]}' \
  --schedule 'cron(0 6 * * ? *)'

aws glue start-crawler --name my-s3-crawler
aws glue stop-crawler --name my-s3-crawler
aws glue get-crawler --name my-s3-crawler
aws glue list-crawlers
aws glue delete-crawler --name my-s3-crawler

# --- ETL jobs ---
aws glue create-job \
  --name my-etl-job \
  --role arn:aws:iam::123456789012:role/GlueJobRole \
  --command '{
    "Name": "glueetl",
    "ScriptLocation": "s3://my-bucket/scripts/my_job.py",
    "PythonVersion": "3"
  }' \
  --default-arguments '{
    "--enable-metrics": "true",
    "--enable-job-insights": "true",
    "--job-bookmark-option": "job-bookmark-enable"
  }' \
  --glue-version "4.0" \
  --number-of-workers 5 \
  --worker-type G.1X

aws glue start-job-run \
  --job-name my-etl-job \
  --arguments '{"--input_path": "s3://my-bucket/raw/", "--output_path": "s3://my-bucket/clean/"}'

aws glue get-job-run --job-name my-etl-job --run-id jr_abc123
aws glue get-job-runs --job-name my-etl-job
aws glue batch-stop-job-run --job-name my-etl-job --job-run-ids jr_abc123
aws glue delete-job --job-name my-etl-job

# --- Connections ---
aws glue create-connection \
  --connection-input '{
    "Name": "my-rds-connection",
    "ConnectionType": "JDBC",
    "ConnectionProperties": {
      "JDBC_CONNECTION_URL": "jdbc:mysql://mydb.cluster.us-east-1.rds.amazonaws.com:3306/mydb",
      "USERNAME": "admin",
      "PASSWORD": "secret"
    },
    "PhysicalConnectionRequirements": {
      "SubnetId": "subnet-abc",
      "SecurityGroupIdList": ["sg-abc"],
      "AvailabilityZone": "us-east-1a"
    }
  }'

aws glue get-connection --name my-rds-connection
aws glue delete-connection --connection-name my-rds-connection

# --- Triggers ---
aws glue create-trigger \
  --name nightly-trigger \
  --type SCHEDULED \
  --schedule 'cron(0 2 * * ? *)' \
  --actions '[{"JobName": "my-etl-job"}]'

aws glue create-trigger \
  --name on-success-trigger \
  --type CONDITIONAL \
  --predicate '{"Conditions": [{"LogicalOperator": "EQUALS", "JobName": "upstream-job", "State": "SUCCEEDED"}]}' \
  --actions '[{"JobName": "downstream-job"}]'

aws glue start-trigger --name nightly-trigger
aws glue stop-trigger --name nightly-trigger
aws glue delete-trigger --name nightly-trigger

# --- Workflows ---
aws glue create-workflow --name my-pipeline --description "Daily ETL pipeline"

aws glue start-workflow-run --name my-pipeline
aws glue get-workflow-run --name my-pipeline --run-id wr_abc123
aws glue stop-workflow-run --name my-pipeline --run-id wr_abc123
aws glue delete-workflow --name my-pipeline

# --- Data Quality ---
aws glue create-data-quality-ruleset \
  --name orders-quality-rules \
  --ruleset 'Rules = [
    Completeness "order_id" >= 0.99,
    Uniqueness "order_id" = 1.0,
    ColumnValues "amount" > 0
  ]' \
  --target-table '{"DatabaseName": "my_db", "TableName": "orders"}'

aws glue start-data-quality-ruleset-evaluation-run \
  --data-source '{"GlueTable": {"DatabaseName": "my_db", "TableName": "orders"}}' \
  --role arn:aws:iam::123456789012:role/GlueJobRole \
  --ruleset-names orders-quality-rules

aws glue list-data-quality-rulesets
aws glue get-data-quality-ruleset --name orders-quality-rules
aws glue delete-data-quality-ruleset --name orders-quality-rules
```

---

## AWS Data Pipeline (Legacy)

> **Note**: AWS Data Pipeline is in maintenance mode and unavailable to new customers. Prefer AWS Glue or Step Functions for new workloads.

```bash
# --- Pipeline management ---
aws datapipeline create-pipeline \
  --name my-pipeline \
  --unique-id my-pipeline-token \
  --description "Daily S3 to Redshift load"

aws datapipeline list-pipelines
aws datapipeline describe-pipelines --pipeline-ids df-0123456789ABCDEF

# --- Upload pipeline definition ---
aws datapipeline put-pipeline-definition \
  --pipeline-id df-0123456789ABCDEF \
  --pipeline-definition file://pipeline-definition.json

aws datapipeline get-pipeline-definition --pipeline-id df-0123456789ABCDEF

# Validate definition without saving
aws datapipeline put-pipeline-definition \
  --pipeline-id df-0123456789ABCDEF \
  --pipeline-definition file://pipeline-definition.json \
  --parameter-values file://parameters.json

# --- Activate and control ---
aws datapipeline activate-pipeline --pipeline-id df-0123456789ABCDEF

# Activate with a specific run date
aws datapipeline activate-pipeline \
  --pipeline-id df-0123456789ABCDEF \
  --start-timestamp 2024-01-01T00:00:00Z

aws datapipeline deactivate-pipeline --pipeline-id df-0123456789ABCDEF

# --- Monitor pipeline runs ---
aws datapipeline list-runs --pipeline-id df-0123456789ABCDEF

aws datapipeline list-runs \
  --pipeline-id df-0123456789ABCDEF \
  --status RUNNING

# Describe individual pipeline objects (activities, data nodes, etc.)
aws datapipeline describe-objects \
  --pipeline-id df-0123456789ABCDEF \
  --object-ids ActivityId_ABC123

# --- Tagging ---
aws datapipeline add-tags \
  --pipeline-id df-0123456789ABCDEF \
  --tags key=Environment,value=prod key=Team,value=data

aws datapipeline remove-tags \
  --pipeline-id df-0123456789ABCDEF \
  --tag-keys Environment

# --- Delete ---
aws datapipeline delete-pipeline --pipeline-id df-0123456789ABCDEF
```
