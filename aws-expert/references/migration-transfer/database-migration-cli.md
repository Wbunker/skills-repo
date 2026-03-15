# AWS Database Migration — CLI Reference

For service concepts, see [database-migration-capabilities.md](database-migration-capabilities.md).

---

## aws dms — Database Migration Service

### Replication Instances

```bash
# List all replication instances
aws dms describe-replication-instances

# Get details of a specific replication instance
aws dms describe-replication-instances \
  --filters '{"Name": "replication-instance-id", "Values": ["my-repl-instance"]}'

# Create a replication instance
aws dms create-replication-instance \
  --replication-instance-identifier my-repl-instance \
  --replication-instance-class dms.r5.xlarge \
  --allocated-storage 100 \
  --multi-az \
  --publicly-accessible false \
  --replication-subnet-group-identifier my-subnet-group \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --engine-version 3.5.2 \
  --auto-minor-version-upgrade true \
  --tags '[{"Key": "Project", "Value": "Migration2024"}]'

# Modify a replication instance (e.g., resize)
aws dms modify-replication-instance \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance \
  --replication-instance-class dms.r5.2xlarge \
  --allocated-storage 200 \
  --apply-immediately

# Reboot a replication instance
aws dms reboot-replication-instance \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance

# Delete a replication instance
aws dms delete-replication-instance \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance
```

### Replication Subnet Groups

```bash
# List subnet groups
aws dms describe-replication-subnet-groups

# Create a replication subnet group
aws dms create-replication-subnet-group \
  --replication-subnet-group-identifier my-subnet-group \
  --replication-subnet-group-description "DMS subnet group for VPC" \
  --subnet-ids '["subnet-0123456789abcdef0", "subnet-abcdef0123456789"]'

# Modify a subnet group
aws dms modify-replication-subnet-group \
  --replication-subnet-group-identifier my-subnet-group \
  --subnet-ids '["subnet-0123456789abcdef0", "subnet-abcdef0123456789", "subnet-new0123456789"]'

# Delete a subnet group
aws dms delete-replication-subnet-group \
  --replication-subnet-group-identifier my-subnet-group
```

### Endpoints

```bash
# List all endpoints
aws dms describe-endpoints

# Test endpoint connection
aws dms test-connection \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance \
  --endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-oracle-endpoint

# Create a source endpoint — Oracle
aws dms create-endpoint \
  --endpoint-identifier source-oracle \
  --endpoint-type source \
  --engine-name oracle \
  --server-name oracle-db.example.com \
  --port 1521 \
  --database-name ORCL \
  --username dms_user \
  --password "MySecurePass123" \
  --ssl-mode none \
  --extra-connection-attributes "useLogminerReader=N;useBfile=Y;accessAlternateDirectly=false"

# Create a source endpoint — PostgreSQL
aws dms create-endpoint \
  --endpoint-identifier source-postgres \
  --endpoint-type source \
  --engine-name postgres \
  --server-name pg-db.example.com \
  --port 5432 \
  --database-name mydb \
  --username dms_user \
  --password "MySecurePass123" \
  --extra-connection-attributes "pluginName=pglogical;heartbeatEnable=true;heartbeatFrequency=5"

# Create a source endpoint — SQL Server
aws dms create-endpoint \
  --endpoint-identifier source-sqlserver \
  --endpoint-type source \
  --engine-name sqlserver \
  --server-name sqlserver.example.com \
  --port 1433 \
  --database-name AdventureWorks \
  --username dms_user \
  --password "MySecurePass123" \
  --extra-connection-attributes "readBackupOnly=Y"

# Create a source endpoint — MySQL
aws dms create-endpoint \
  --endpoint-identifier source-mysql \
  --endpoint-type source \
  --engine-name mysql \
  --server-name mysql.example.com \
  --port 3306 \
  --username dms_user \
  --password "MySecurePass123"

# Create a target endpoint — Aurora PostgreSQL
aws dms create-endpoint \
  --endpoint-identifier target-aurora-pg \
  --endpoint-type target \
  --engine-name aurora-postgresql \
  --server-name aurora-cluster.cluster-xxxx.us-east-1.rds.amazonaws.com \
  --port 5432 \
  --database-name targetdb \
  --username admin \
  --password "TargetPass123"

# Create a target endpoint — Amazon Redshift
aws dms create-endpoint \
  --endpoint-identifier target-redshift \
  --endpoint-type target \
  --engine-name redshift \
  --server-name my-cluster.xxxx.us-east-1.redshift.amazonaws.com \
  --port 5439 \
  --database-name dev \
  --username awsuser \
  --password "RedshiftPass123" \
  --extra-connection-attributes "bucketName=my-dms-s3-staging;bucketFolder=redshift-staging;serviceAccessRoleArn=arn:aws:iam::123456789012:role/DMS-S3-Role"

# Create a target endpoint — Amazon S3
aws dms create-endpoint \
  --endpoint-identifier target-s3 \
  --endpoint-type target \
  --engine-name s3 \
  --s3-settings '{"BucketArn": "arn:aws:s3:::my-dms-target", "BucketFolder": "migration-output", "ServiceAccessRoleArn": "arn:aws:iam::123456789012:role/DMS-S3-Role", "DataFormat": "parquet", "CompressionType": "GZIP"}'

# Create endpoint using Secrets Manager
aws dms create-endpoint \
  --endpoint-identifier source-oracle-secrets \
  --endpoint-type source \
  --engine-name oracle \
  --database-name ORCL \
  --secrets-manager-access-role-arn arn:aws:iam::123456789012:role/DMS-SecretsManager-Role \
  --secrets-manager-secret-id arn:aws:secretsmanager:us-east-1:123456789012:secret:dms/oracle-source

# Modify an endpoint
aws dms modify-endpoint \
  --endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-oracle \
  --extra-connection-attributes "useLogminerReader=Y"

# Delete an endpoint
aws dms delete-endpoint \
  --endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-oracle
```

### Replication Tasks

```bash
# List all replication tasks
aws dms describe-replication-tasks

# Create a full-load + CDC replication task
aws dms create-replication-task \
  --replication-task-identifier my-migration-task \
  --source-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-oracle \
  --target-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:target-aurora-pg \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance \
  --migration-type full-load-and-cdc \
  --table-mappings '{"rules": [{"rule-type": "selection", "rule-id": "1", "rule-name": "include-all", "object-locator": {"schema-name": "%", "table-name": "%"}, "rule-action": "include"}]}' \
  --replication-task-settings '{"TargetMetadata": {"TargetSchema": "", "SupportLobs": true, "FullLobMode": false, "LobChunkSize": 64, "LimitedSizeLobMode": true, "LobMaxSize": 32768}, "FullLoadSettings": {"TargetTablePrepMode": "DO_NOTHING", "CreatePkAfterFullLoad": false, "StopTaskCachedChangesApplied": false, "StopTaskCachedChangesNotApplied": false, "MaxFullLoadSubTasks": 8, "TransactionConsistencyTimeout": 600, "CommitRate": 50000}, "Logging": {"EnableLogging": true, "LogComponents": [{"Id": "SOURCE_UNLOAD", "Severity": "LOGGER_SEVERITY_DEFAULT"}, {"Id": "TARGET_LOAD", "Severity": "LOGGER_SEVERITY_DEFAULT"}]}}'

# Create a CDC-only task starting from a specific position
aws dms create-replication-task \
  --replication-task-identifier cdc-only-task \
  --source-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-postgres \
  --target-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:target-aurora-pg \
  --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:my-repl-instance \
  --migration-type cdc \
  --cdc-start-time 2024-03-01T00:00:00 \
  --table-mappings file://table-mappings.json

# Start a replication task
aws dms start-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task \
  --start-replication-task-type start-replication

# Reload (restart from scratch)
aws dms start-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task \
  --start-replication-task-type reload-target

# Resume a stopped task
aws dms start-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task \
  --start-replication-task-type resume-processing

# Stop a replication task
aws dms stop-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task

# Modify a replication task
aws dms modify-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task \
  --migration-type full-load \
  --table-mappings file://updated-table-mappings.json

# Describe task table statistics (per-table row counts)
aws dms describe-table-statistics \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task

# Delete a replication task
aws dms delete-replication-task \
  --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:my-migration-task
```

### Serverless Replication

```bash
# List serverless replications
aws dms describe-replications

# Create a serverless replication config
aws dms create-replication-config \
  --replication-config-identifier my-serverless-replication \
  --source-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:source-oracle \
  --target-endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:target-aurora-pg \
  --compute-config '{"MinCapacityUnits": 2, "MaxCapacityUnits": 16, "MultiAZ": false, "ReplicationSubnetGroupId": "my-subnet-group", "VpcSecurityGroupIds": ["sg-0123456789abcdef0"]}' \
  --replication-type full-load-and-cdc \
  --table-mappings file://table-mappings.json

# Start serverless replication
aws dms start-replication \
  --replication-config-arn arn:aws:dms:us-east-1:123456789012:replication-config:my-serverless-replication \
  --start-replication-type start-replication

# Stop serverless replication
aws dms stop-replication \
  --replication-config-arn arn:aws:dms:us-east-1:123456789012:replication-config:my-serverless-replication

# Describe serverless replication table stats
aws dms describe-replication-table-statistics \
  --replication-config-arn arn:aws:dms:us-east-1:123456789012:replication-config:my-serverless-replication

# Delete a serverless replication config
aws dms delete-replication-config \
  --replication-config-arn arn:aws:dms:us-east-1:123456789012:replication-config:my-serverless-replication
```

### Certificates (SSL/TLS)

```bash
# List certificates
aws dms describe-certificates

# Import a certificate
aws dms import-certificate \
  --certificate-identifier my-source-ca \
  --certificate-pem file://ca-cert.pem

# Delete a certificate
aws dms delete-certificate \
  --certificate-arn arn:aws:dms:us-east-1:123456789012:cert:my-source-ca
```

### Event Subscriptions

```bash
# List event subscriptions
aws dms describe-event-subscriptions

# Create an event subscription (SNS notifications for task state changes)
aws dms create-event-subscription \
  --subscription-name dms-task-events \
  --sns-topic-arn arn:aws:sns:us-east-1:123456789012:dms-alerts \
  --source-type replication-task \
  --event-categories '["stateChange", "failure", "deletion"]' \
  --source-ids '["my-migration-task"]' \
  --enabled

# Modify an event subscription
aws dms modify-event-subscription \
  --subscription-name dms-task-events \
  --event-categories '["stateChange", "failure", "deletion", "creation"]'

# Delete an event subscription
aws dms delete-event-subscription \
  --subscription-name dms-task-events
```

### Fleet Advisor (Database Discovery)

```bash
# List Fleet Advisor collectors
aws dms describe-fleet-advisor-collectors

# Create a Fleet Advisor collector
aws dms create-fleet-advisor-collector \
  --collector-name my-network-collector \
  --description "Collector for on-premises datacenter" \
  --service-access-role-arn arn:aws:iam::123456789012:role/DMS-FleetAdvisor-Role \
  --s3-bucket-name my-fleet-advisor-bucket

# Describe Fleet Advisor databases (discovered databases)
aws dms describe-fleet-advisor-databases

# List Fleet Advisor schemas (discovered schemas)
aws dms describe-fleet-advisor-schemas

# Generate recommendations for a set of databases
aws dms start-recommendations \
  --database-id 12345678-1234-1234-1234-123456789012 \
  --settings '{"instanceSizingStrategy": "active", "workloadType": "production"}'

# Describe generated recommendations
aws dms describe-recommendations

# Delete a collector
aws dms delete-fleet-advisor-collector \
  --collector-referenced-id 12345678-1234-1234-1234-123456789012
```

### DMS Schema Conversion (Console API)

```bash
# List migration projects (DMS Schema Conversion uses migration projects)
aws dms describe-migration-projects

# Create a migration project
aws dms create-migration-project \
  --migration-project-name my-oracle-to-aurora-project \
  --source-data-provider-descriptors '[{"DataProviderArn": "arn:aws:dms:us-east-1:123456789012:data-provider:source-oracle-dp", "SecretsManagerSecretId": "arn:aws:secretsmanager:us-east-1:123456789012:secret:dms/oracle"}]' \
  --target-data-provider-descriptors '[{"DataProviderArn": "arn:aws:dms:us-east-1:123456789012:data-provider:target-aurora-dp", "SecretsManagerSecretId": "arn:aws:secretsmanager:us-east-1:123456789012:secret:dms/aurora"}]' \
  --instance-profile-arn arn:aws:dms:us-east-1:123456789012:instance-profile:my-instance-profile \
  --schema-conversion-application-attributes '{"S3BucketPath": "s3://my-dms-schema-bucket/projects", "S3BucketRoleArn": "arn:aws:iam::123456789012:role/DMS-S3-Role"}'

# Create a conversion action (run schema conversion)
aws dms start-metadata-model-conversion \
  --migration-project-arn arn:aws:dms:us-east-1:123456789012:migration-project:my-oracle-to-aurora-project \
  --selection-rules '{"filters": [{"filterType": "source", "attribute": "schema-name", "filter-operator": "eq", "value": "HR"}]}'

# Describe conversion tasks
aws dms describe-metadata-model-conversions \
  --migration-project-arn arn:aws:dms:us-east-1:123456789012:migration-project:my-oracle-to-aurora-project

# Export schema conversion artifacts to S3
aws dms export-metadata-model-assessment \
  --migration-project-arn arn:aws:dms:us-east-1:123456789012:migration-project:my-oracle-to-aurora-project \
  --selection-rules '{"filters": [{"filterType": "source", "attribute": "schema-name", "filter-operator": "eq", "value": "HR"}]}' \
  --file-name "assessment-report" \
  --assessment-report-types '["pdf", "csv"]'
```
