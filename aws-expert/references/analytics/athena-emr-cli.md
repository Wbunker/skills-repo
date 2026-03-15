# AWS Athena & EMR — CLI Reference
For service concepts, see [athena-emr-capabilities.md](athena-emr-capabilities.md).

## Amazon Athena

```bash
# --- Query execution ---
aws athena start-query-execution \
  --query-string "SELECT * FROM my_db.my_table WHERE dt = '2024-01-01' LIMIT 100" \
  --query-execution-context Database=my_db \
  --result-configuration OutputLocation=s3://my-bucket/athena-results/ \
  --work-group primary

aws athena get-query-execution \
  --query-execution-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

aws athena get-query-results \
  --query-execution-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

aws athena stop-query-execution \
  --query-execution-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

aws athena list-query-executions --work-group primary --max-results 10

# --- CTAS pattern ---
aws athena start-query-execution \
  --query-string "CREATE TABLE my_db.clean_table
    WITH (format='PARQUET', partitioned_by=ARRAY['dt'],
          external_location='s3://my-bucket/clean/')
    AS SELECT * FROM my_db.raw_table" \
  --result-configuration OutputLocation=s3://my-bucket/athena-results/

# --- Workgroups ---
aws athena create-work-group \
  --name analytics-team \
  --configuration '{
    "ResultConfiguration": {"OutputLocation": "s3://my-bucket/results/"},
    "EnforceWorkGroupConfiguration": true,
    "BytesScannedCutoffPerQuery": 10737418240,
    "PublishCloudWatchMetricsEnabled": true
  }'

aws athena get-work-group --work-group analytics-team
aws athena list-work-groups

aws athena update-work-group \
  --work-group analytics-team \
  --configuration-updates 'EnforceWorkGroupConfiguration=true'

aws athena delete-work-group --work-group analytics-team --recursive-delete-option

# --- Named queries ---
aws athena create-named-query \
  --name daily-order-count \
  --database orders_db \
  --query-string "SELECT COUNT(*) FROM orders WHERE dt = '{{dt}}'" \
  --work-group analytics-team

aws athena list-named-queries --work-group analytics-team
aws athena get-named-query --named-query-id a1b2c3d4-...
aws athena batch-get-named-query --named-query-ids a1b2c3d4-... b2c3d4e5-...
aws athena delete-named-query --named-query-id a1b2c3d4-...

# --- Prepared statements ---
aws athena create-prepared-statement \
  --work-group analytics-team \
  --statement-name get_orders_by_region \
  --query-statement "SELECT * FROM orders WHERE region = ? AND dt = ?"

aws athena list-prepared-statements --work-group analytics-team
aws athena get-prepared-statement --work-group analytics-team --statement-name get_orders_by_region

# Execute a prepared statement
aws athena start-query-execution \
  --query-string "EXECUTE get_orders_by_region USING 'us-east-1', '2024-01-01'" \
  --work-group analytics-team \
  --result-configuration OutputLocation=s3://my-bucket/results/

# --- Data catalogs (federated query) ---
aws athena create-data-catalog \
  --name my-glue-catalog \
  --type GLUE \
  --parameters catalog=AwsDataCatalog

aws athena create-data-catalog \
  --name rds-connector \
  --type LAMBDA \
  --parameters function=arn:aws:lambda:us-east-1:123456789012:function:rds-connector

aws athena list-data-catalogs
aws athena get-data-catalog --name rds-connector
aws athena delete-data-catalog --name rds-connector

# --- Capacity reservations ---
aws athena create-capacity-reservation \
  --name team-reservation \
  --target-dpus 24

aws athena get-capacity-reservation --name team-reservation
aws athena list-capacity-reservations
aws athena delete-capacity-reservation --name team-reservation
```

---

## Amazon EMR (on EC2)

```bash
# --- Create cluster ---
aws emr create-cluster \
  --name "My Spark Cluster" \
  --release-label emr-7.1.0 \
  --applications Name=Spark Name=Hive \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --log-uri s3://my-bucket/emr-logs/ \
  --ec2-attributes KeyName=my-key-pair,SubnetId=subnet-0123456789abcdef0

# Instance fleet (mixed instance types with Spot)
aws emr create-cluster \
  --name "Fleet Cluster" \
  --release-label emr-7.1.0 \
  --applications Name=Spark \
  --instance-fleets '[
    {
      "Name": "MasterFleet",
      "InstanceFleetType": "MASTER",
      "TargetOnDemandCapacity": 1,
      "InstanceTypeConfigs": [{"InstanceType": "m5.xlarge"}]
    },
    {
      "Name": "CoreFleet",
      "InstanceFleetType": "CORE",
      "TargetOnDemandCapacity": 2,
      "TargetSpotCapacity": 4,
      "InstanceTypeConfigs": [
        {"InstanceType": "m5.xlarge", "WeightedCapacity": 1},
        {"InstanceType": "m5.2xlarge", "WeightedCapacity": 2}
      ],
      "LaunchSpecifications": {
        "SpotSpecification": {"TimeoutDurationMinutes": 10, "TimeoutAction": "SWITCH_TO_ON_DEMAND"}
      }
    }
  ]' \
  --use-default-roles \
  --log-uri s3://my-bucket/emr-logs/

# --- Cluster operations ---
aws emr describe-cluster --cluster-id j-ABCDEFGHIJKLM
aws emr list-clusters --active
aws emr list-clusters --cluster-states RUNNING WAITING

aws emr modify-cluster \
  --cluster-id j-ABCDEFGHIJKLM \
  --step-concurrency-level 5

aws emr terminate-clusters --cluster-ids j-ABCDEFGHIJKLM j-NOPQRSTUVWXYZ

# --- Steps (jobs) ---
aws emr add-steps \
  --cluster-id j-ABCDEFGHIJKLM \
  --steps '[
    {
      "Name": "My Spark Job",
      "Type": "CUSTOM_JAR",
      "Jar": "command-runner.jar",
      "ActionOnFailure": "CONTINUE",
      "Args": [
        "spark-submit",
        "--deploy-mode", "cluster",
        "s3://my-bucket/scripts/my_job.py",
        "--input", "s3://my-bucket/input/",
        "--output", "s3://my-bucket/output/"
      ]
    }
  ]'

aws emr list-steps --cluster-id j-ABCDEFGHIJKLM
aws emr describe-step --cluster-id j-ABCDEFGHIJKLM --step-id s-ABCDEFGHIJKLM
aws emr cancel-steps --cluster-id j-ABCDEFGHIJKLM --step-ids s-ABCDEFGHIJKLM

# --- Scaling ---
aws emr add-instance-fleet \
  --cluster-id j-ABCDEFGHIJKLM \
  --instance-fleet '{
    "Name": "TaskFleet",
    "InstanceFleetType": "TASK",
    "TargetSpotCapacity": 10,
    "InstanceTypeConfigs": [{"InstanceType": "m5.xlarge", "WeightedCapacity": 1}]
  }'

# Managed scaling policy
aws emr put-managed-scaling-policy \
  --cluster-id j-ABCDEFGHIJKLM \
  --managed-scaling-policy '{
    "ComputeLimits": {
      "UnitType": "Instances",
      "MinimumCapacityUnits": 2,
      "MaximumCapacityUnits": 20,
      "MaximumOnDemandCapacityUnits": 5
    }
  }'
```

---

## Amazon EMR Serverless

```bash
# --- Application lifecycle ---
aws emr-serverless create-application \
  --name my-spark-app \
  --release-label emr-7.1.0 \
  --type SPARK \
  --initial-capacity '{
    "DRIVER": {"WorkerCount": 1, "WorkerConfiguration": {"CPU": "2vCPU", "Memory": "4GB"}},
    "EXECUTOR": {"WorkerCount": 5, "WorkerConfiguration": {"CPU": "4vCPU", "Memory": "8GB"}}
  }' \
  --network-configuration '{"subnetIds": ["subnet-abc"], "securityGroupIds": ["sg-abc"]}'

aws emr-serverless get-application --application-id 00f12345abcdef00
aws emr-serverless list-applications

aws emr-serverless start-application --application-id 00f12345abcdef00
aws emr-serverless stop-application --application-id 00f12345abcdef00
aws emr-serverless delete-application --application-id 00f12345abcdef00

# --- Job runs ---
aws emr-serverless start-job-run \
  --application-id 00f12345abcdef00 \
  --execution-role-arn arn:aws:iam::123456789012:role/EMRServerlessRole \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://my-bucket/scripts/my_job.py",
      "entryPointArguments": ["--input", "s3://my-bucket/input/"],
      "sparkSubmitParameters": "--conf spark.executor.cores=4 --conf spark.executor.memory=8g"
    }
  }' \
  --configuration-overrides '{
    "monitoringConfiguration": {
      "s3MonitoringConfiguration": {"logUri": "s3://my-bucket/emr-serverless-logs/"}
    }
  }'

aws emr-serverless get-job-run \
  --application-id 00f12345abcdef00 \
  --job-run-id 00f12345run000001

aws emr-serverless list-job-runs --application-id 00f12345abcdef00
aws emr-serverless list-job-runs --application-id 00f12345abcdef00 --states RUNNING PENDING

aws emr-serverless cancel-job-run \
  --application-id 00f12345abcdef00 \
  --job-run-id 00f12345run000001
```
