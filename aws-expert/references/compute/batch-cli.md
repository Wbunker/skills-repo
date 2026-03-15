# AWS Batch — CLI Reference

For service concepts, see [batch-capabilities.md](batch-capabilities.md).

## AWS Batch

```bash
# --- Compute Environments ---
# Managed EC2 compute environment (Spot + On-Demand mix)
aws batch create-compute-environment \
  --compute-environment-name my-batch-ce \
  --type MANAGED \
  --state ENABLED \
  --compute-resources '{
    "type": "SPOT",
    "allocationStrategy": "SPOT_CAPACITY_OPTIMIZED",
    "minvCpus": 0,
    "maxvCpus": 256,
    "instanceRole": "arn:aws:iam::123456789012:instance-profile/ecsInstanceRole",
    "instanceTypes": ["m5", "c5", "r5"],
    "subnets": ["subnet-0abc123", "subnet-0def456"],
    "securityGroupIds": ["sg-0abc123def456789"],
    "bidPercentage": 60,
    "spotIamFleetRole": "arn:aws:iam::123456789012:role/AmazonEC2SpotFleetRole",
    "tags": {"Project": "data-pipeline"}
  }' \
  --service-role arn:aws:iam::123456789012:role/AWSBatchServiceRole

# Managed Fargate compute environment
aws batch create-compute-environment \
  --compute-environment-name my-fargate-ce \
  --type MANAGED \
  --state ENABLED \
  --compute-resources '{
    "type": "FARGATE",
    "maxvCpus": 256,
    "subnets": ["subnet-0abc123", "subnet-0def456"],
    "securityGroupIds": ["sg-0abc123def456789"]
  }' \
  --service-role arn:aws:iam::123456789012:role/AWSBatchServiceRole

aws batch describe-compute-environments
aws batch describe-compute-environments --compute-environments my-batch-ce

aws batch update-compute-environment \
  --compute-environment my-batch-ce \
  --state ENABLED \
  --compute-resources '{"maxvCpus": 512}'

aws batch delete-compute-environment --compute-environment my-batch-ce

# --- Job Queues ---
aws batch create-job-queue \
  --job-queue-name my-job-queue \
  --state ENABLED \
  --priority 100 \
  --compute-environment-order '[
    {"order": 1, "computeEnvironment": "my-batch-ce"}
  ]'

# Job queue with multiple compute environments (ordered failover)
aws batch create-job-queue \
  --job-queue-name my-multi-ce-queue \
  --state ENABLED \
  --priority 50 \
  --compute-environment-order '[
    {"order": 1, "computeEnvironment": "my-spot-ce"},
    {"order": 2, "computeEnvironment": "my-ondemand-ce"}
  ]'

aws batch describe-job-queues
aws batch update-job-queue --job-queue my-job-queue --state DISABLED
aws batch delete-job-queue --job-queue my-job-queue

# --- Job Definitions ---
aws batch register-job-definition \
  --job-definition-name my-job-def \
  --type container \
  --container-properties '{
    "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-batch-image:latest",
    "vcpus": 4,
    "memory": 8192,
    "jobRoleArn": "arn:aws:iam::123456789012:role/BatchJobRole",
    "environment": [
      {"name": "S3_BUCKET", "value": "my-data-bucket"}
    ],
    "mountPoints": [{"containerPath": "/tmp/data", "readOnly": false, "sourceVolume": "scratch"}],
    "volumes": [{"name": "scratch", "host": {"sourcePath": "/tmp/batch-scratch"}}],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/batch/job",
        "awslogs-region": "us-east-1"
      }
    }
  }' \
  --timeout '{"attemptDurationSeconds": 3600}' \
  --retry-strategy '{"attempts": 3, "evaluateOnExit": [{"onReason": "CannotPullContainerError:*", "action": "RETRY"}]}'

aws batch describe-job-definitions
aws batch describe-job-definitions --job-definition-name my-job-def
aws batch deregister-job-definition --job-definition my-job-def:1

# --- Submit Jobs ---
# Standard job
aws batch submit-job \
  --job-name my-processing-job \
  --job-queue my-job-queue \
  --job-definition my-job-def:1 \
  --container-overrides '{
    "vcpus": 8,
    "memory": 16384,
    "environment": [{"name": "INPUT_FILE", "value": "s3://my-bucket/data/file.csv"}]
  }'

# Array job (100 child jobs, each with different array index)
aws batch submit-job \
  --job-name my-array-job \
  --job-queue my-job-queue \
  --job-definition my-job-def:1 \
  --array-properties '{"size": 100}'

# Job with dependency (run after another job succeeds)
aws batch submit-job \
  --job-name downstream-job \
  --job-queue my-job-queue \
  --job-definition my-job-def:1 \
  --depends-on '[{"jobId":"12345678-abcd-1234-abcd-123456789012","type":"SEQUENTIAL"}]'

# --- Describe and Monitor Jobs ---
aws batch describe-jobs --jobs 12345678-abcd-1234-abcd-123456789012
aws batch list-jobs --job-queue my-job-queue --job-status RUNNING
aws batch list-jobs --job-queue my-job-queue --job-status FAILED

aws batch cancel-job \
  --job-id 12345678-abcd-1234-abcd-123456789012 \
  --reason "Manual cancellation"

aws batch terminate-job \
  --job-id 12345678-abcd-1234-abcd-123456789012 \
  --reason "Force terminate"

# --- Scheduling Policies (Fair-Share) ---
aws batch create-scheduling-policy \
  --name my-fair-share-policy \
  --fairshare-policy '{
    "shareDecaySeconds": 3600,
    "computeReservation": 10,
    "shareDistribution": [
      {"shareIdentifier": "team-a", "weightFactor": 1.0},
      {"shareIdentifier": "team-b", "weightFactor": 2.0}
    ]
  }'

aws batch describe-scheduling-policies --arns arn:aws:batch:us-east-1:123456789012:scheduling-policy/my-fair-share-policy
aws batch list-scheduling-policies
aws batch delete-scheduling-policy --arn arn:aws:batch:us-east-1:123456789012:scheduling-policy/my-fair-share-policy
```
