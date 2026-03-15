# AWS Compute Optimizer — CLI Reference
For service concepts, see [compute-optimizer-capabilities.md](compute-optimizer-capabilities.md).

## Compute Optimizer (aws compute-optimizer)

```bash
# --- Enrollment ---

# Check enrollment status for the current account
aws compute-optimizer get-enrollment-status

# Enroll the account in Compute Optimizer
aws compute-optimizer update-enrollment-status --status Active

# Check enrollment for all accounts in the organization (management account)
aws compute-optimizer get-enrollment-statuses-for-organization

# --- Recommendation Preferences ---

# Set CPU utilization threshold preference for EC2 (include 20% headroom)
aws compute-optimizer put-recommendation-preferences \
  --resource-type Ec2Instance \
  --scope '{"name": "AccountId", "value": "123456789012"}' \
  --enhanced-infrastructure-metrics Inactive \
  --cpu-vendor-architectures CURRENT

# Get current recommendation preferences
aws compute-optimizer get-recommendation-preferences \
  --resource-type Ec2Instance

# Get effective preferences (merged account + org level)
aws compute-optimizer get-effective-recommendation-preferences \
  --resource-arn arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0

# --- EC2 Instance Recommendations ---

# Get all EC2 instance recommendations for the account
aws compute-optimizer get-ec2-instance-recommendations

# Get recommendations for specific instances
aws compute-optimizer get-ec2-instance-recommendations \
  --instance-arns \
    arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0 \
    arn:aws:ec2:us-east-1:123456789012:instance/i-abcdef1234567890

# Filter to over-provisioned instances only
aws compute-optimizer get-ec2-instance-recommendations \
  --filters '[{"name": "Finding", "values": ["Overprovisioned"]}]'

# Export all EC2 recommendations to S3
aws compute-optimizer export-ec2-instance-recommendations \
  --s3-destination-config '{
    "bucket": "my-cost-reports-bucket",
    "keyPrefix": "compute-optimizer/ec2/"
  }' \
  --fields AccountId InstanceArn Finding RecommendationOptions

# Check export job status
aws compute-optimizer describe-recommendation-export-jobs

# --- Auto Scaling Group Recommendations ---

aws compute-optimizer get-auto-scaling-group-recommendations

# Filter to over-provisioned ASGs
aws compute-optimizer get-auto-scaling-group-recommendations \
  --filters '[{"name": "Finding", "values": ["Overprovisioned"]}]'

# Export ASG recommendations to S3
aws compute-optimizer export-auto-scaling-group-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/asg/"}'

# --- EBS Volume Recommendations ---

aws compute-optimizer get-ebs-volume-recommendations

# Export EBS volume recommendations
aws compute-optimizer export-ebs-volume-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/ebs/"}'

# --- Lambda Function Recommendations ---

aws compute-optimizer get-lambda-function-recommendations

# Filter to Lambda functions with over-provisioned memory
aws compute-optimizer get-lambda-function-recommendations \
  --filters '[{"name": "Finding", "values": ["Overprovisioned"]}]'

# Export Lambda recommendations
aws compute-optimizer export-lambda-function-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/lambda/"}'

# --- ECS Service Recommendations ---

aws compute-optimizer get-ecs-service-recommendations

# Export ECS service recommendations
aws compute-optimizer export-ecs-service-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/ecs/"}'

# --- RDS Recommendations ---

aws compute-optimizer get-rds-database-recommendations

# Export RDS recommendations
aws compute-optimizer export-rds-database-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/rds/"}'

# --- Idle Resources ---

# Get idle resource recommendations (EC2, EBS, ASG, etc.)
aws compute-optimizer get-idle-recommendations

# Export idle resource recommendations
aws compute-optimizer export-idle-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/idle/"}'

# --- License Recommendations ---

# Get commercial software license recommendations (e.g., SQL Server right-sizing)
aws compute-optimizer get-license-recommendations

# Export license recommendations
aws compute-optimizer export-license-recommendations \
  --s3-destination-config '{"bucket": "my-cost-reports-bucket", "keyPrefix": "compute-optimizer/licenses/"}'

# --- Recommendation Summaries ---

# Get a summary of all recommendations (counts by finding type and resource type)
aws compute-optimizer get-recommendation-summaries
```
