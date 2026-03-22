# Running Pig on AWS EMR
_Modern cloud execution — cluster setup, S3 integration, steps, IAM, logging, cost optimization_

## Pig Versions on EMR

| EMR Release | Pig Version | Hadoop Version | Notes |
|-------------|------------|----------------|-------|
| EMR 6.x | 0.17.0 | 3.x | Recommended; S3A default; Tez available |
| EMR 5.x | 0.17.0 | 2.x | Legacy; still supported |

Check current: [AWS EMR Release Guide — Pig](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-pig.html)

## Launch a Cluster with Pig

### AWS CLI

```bash
aws emr create-cluster \
  --name "pig-etl-job" \
  --release-label emr-6.15.0 \
  --applications Name=Pig Name=Hadoop \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --ec2-attributes KeyName=my-key-pair,SubnetId=subnet-xxxxxxxx \
  --service-role EMR_DefaultRole \
  --ec2-attributes InstanceProfile=EMR_EC2_DefaultRole \
  --log-uri s3://my-logs-bucket/emr-logs/ \
  --auto-terminate \
  --region us-east-1
```

### With a Pig Step (run-and-terminate pattern)

```bash
aws emr create-cluster \
  --name "pig-etl-job" \
  --release-label emr-6.15.0 \
  --applications Name=Pig Name=Hadoop \
  --instance-type m5.xlarge \
  --instance-count 5 \
  --ec2-attributes KeyName=my-key-pair,SubnetId=subnet-xxxxxxxx \
  --service-role EMR_DefaultRole \
  --ec2-attributes InstanceProfile=EMR_EC2_DefaultRole \
  --log-uri s3://my-logs/emr-logs/ \
  --auto-terminate \
  --steps '[
    {
      "Name": "Pig Script",
      "ActionOnFailure": "TERMINATE_CLUSTER",
      "HadoopJarStep": {
        "Jar": "command-runner.jar",
        "Args": [
          "pig-script",
          "--run-pig-script",
          "--args",
          "-f", "s3://my-bucket/scripts/myscript.pig",
          "-p", "DATE=2024-01-15",
          "-p", "ENV=prod"
        ]
      }
    }
  ]'
```

### Add a Step to a Running Cluster

```bash
aws emr add-steps \
  --cluster-id j-XXXXXXXXXX \
  --steps '[
    {
      "Name": "Daily Pig ETL",
      "ActionOnFailure": "CONTINUE",
      "HadoopJarStep": {
        "Jar": "command-runner.jar",
        "Args": ["pig-script", "--run-pig-script",
                 "--args", "-f", "s3://my-bucket/scripts/daily.pig",
                 "-p", "DATE=2024-01-15"]
      }
    }
  ]'

# Monitor step
aws emr describe-step --cluster-id j-XXXXX --step-id s-XXXXX
```

## S3 Integration

### Path Conventions

```pig
-- Use s3a:// on EMR 6.x (preferred — uses S3A connector, better performance)
data = LOAD 's3a://my-bucket/data/events/dt=2024-01-15/' USING PigStorage(',') AS (...);

-- s3:// also works on all EMR versions (uses EMRFS)
data = LOAD 's3://my-bucket/data/events/dt=2024-01-15/' USING PigStorage(',') AS (...);

-- Glob patterns
all_jan = LOAD 's3://my-bucket/data/events/dt=2024-01-*/' USING PigStorage(',') AS (...);
multi   = LOAD 's3://my-bucket/data/events/{dt=2024-01-14,dt=2024-01-15}/' USING PigStorage(',') AS (...);

-- Output
STORE result INTO 's3://my-bucket/output/dt=2024-01-15/' USING PigStorage('\t');
```

### S3 Output Behavior

- EMR writes output to a staging location first, then commits atomically
- A `_SUCCESS` file is written on successful completion
- Output directory must NOT exist before the job runs (Pig will fail if it does)
- On failure, partial output may remain — clean up before retrying

```bash
# Delete output before re-run
aws s3 rm s3://my-bucket/output/dt=2024-01-15/ --recursive
```

### EMRFS Consistent View (EMR 5.x only)

EMR 6.x on S3A does not need this — S3A handles consistency.

## IAM Configuration

### EC2 Instance Profile (EMR_EC2_DefaultRole)

The instance profile attached to EMR nodes determines what S3 buckets are accessible. Add a policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-data-bucket",
        "arn:aws:s3:::my-data-bucket/*",
        "arn:aws:s3:::my-output-bucket",
        "arn:aws:s3:::my-output-bucket/*"
      ]
    }
  ]
}
```

### AWS Glue Data Catalog

To use Glue as the Hive Metastore (for HCatLoader):

```bash
aws emr create-cluster \
  --configurations '[
    {
      "Classification": "hive-site",
      "Properties": {
        "hive.metastore.client.factory.class":
          "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
      }
    }
  ]' \
  ...
```

The instance profile must also have `glue:GetTable`, `glue:GetDatabase` permissions.

## Logging and Debugging

### Log Location

```bash
# Cluster logs in S3 (set via --log-uri)
s3://my-logs-bucket/emr-logs/<cluster-id>/steps/<step-id>/

# Key files:
# stdout       — Pig output / DUMP results
# stderr       — Pig errors, stack traces
# controller   — Step controller log
# syslog       — Hadoop application log
```

```bash
# Download logs via CLI
aws s3 cp s3://my-logs-bucket/emr-logs/j-XXXXX/steps/s-XXXXX/ ./logs/ --recursive

# Or stream from cluster directly (SSH)
yarn logs -applicationId application_XXXXXXX_XXXX
```

### Interactive Debugging (SSH)

```bash
# SSH to master node
ssh -i my-key.pem hadoop@<master-public-dns>

# Start Pig shell
pig -x mapreduce   # full Hadoop mode
pig -x local       # local mode for small-data testing

# Run script manually
pig -x mapreduce -f s3://bucket/scripts/myscript.pig -p DATE=2024-01-15
```

## Cluster Sizing Guidelines

| Data Size | Cluster Type | Instance Type | Node Count |
|-----------|-------------|---------------|------------|
| < 10 GB | Dev/test | m5.xlarge | 1 master + 2 core |
| 10–100 GB | Small prod | m5.2xlarge | 1 master + 4–8 core |
| 100 GB–1 TB | Medium prod | m5.4xlarge or r5.2xlarge | 1 master + 8–20 core |
| > 1 TB | Large prod | r5.4xlarge | 1 master + 20+ core; consider spot |

### Spot Instances for Cost Savings

```bash
aws emr create-cluster \
  --instance-fleets '[
    {
      "Name": "Master",
      "InstanceFleetType": "MASTER",
      "TargetOnDemandCapacity": 1,
      "InstanceTypeConfigs": [{"InstanceType": "m5.xlarge"}]
    },
    {
      "Name": "Core",
      "InstanceFleetType": "CORE",
      "TargetOnDemandCapacity": 2,
      "TargetSpotCapacity": 6,
      "InstanceTypeConfigs": [
        {"InstanceType": "m5.2xlarge", "BidPriceAsPercentageOfOnDemandPrice": 80},
        {"InstanceType": "m5a.2xlarge", "BidPriceAsPercentageOfOnDemandPrice": 80}
      ]
    }
  ]' \
  ...
```

## Configuration Tuning on EMR

```bash
# Pass pig-site configuration at cluster creation
aws emr create-cluster \
  --configurations '[
    {
      "Classification": "pig-properties",
      "Properties": {
        "pig.exec.reducers.bytes.per.reducer": "268435456",
        "pig.exec.nocombiner": "false",
        "pig.tmpfilecompression": "true",
        "pig.tmpfilecompression.codec": "lzo"
      }
    },
    {
      "Classification": "mapred-site",
      "Properties": {
        "mapreduce.map.memory.mb": "4096",
        "mapreduce.reduce.memory.mb": "8192",
        "mapreduce.map.java.opts": "-Xmx3276m",
        "mapreduce.reduce.java.opts": "-Xmx6553m"
      }
    }
  ]' \
  ...
```

## Orchestration with AWS

### Step Functions

```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::elasticmapreduce:addStep.sync",
  "Parameters": {
    "ClusterId": "j-XXXXXXXXXX",
    "Step": {
      "Name": "Pig ETL",
      "ActionOnFailure": "CONTINUE",
      "HadoopJarStep": {
        "Jar": "command-runner.jar",
        "Args": ["pig-script", "--run-pig-script",
                 "--args", "-f", "s3://bucket/scripts/etl.pig",
                 "-p", "DATE.$": "$.date"]
      }
    }
  }
}
```

### Airflow with EMRAddStepsOperator

```python
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator

pig_step = EmrAddStepsOperator(
    task_id='run_pig',
    job_flow_id='j-XXXXXXXXXX',
    steps=[{
        'Name': 'Pig ETL',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['pig-script', '--run-pig-script',
                     '--args', '-f', 's3://bucket/scripts/etl.pig',
                     '-p', f'DATE={ds}'],
        },
    }],
)
```
