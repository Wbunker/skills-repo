# AWS CloudWatch Synthetics — CLI Reference
For service concepts, see [cloudwatch-synthetics-capabilities.md](cloudwatch-synthetics-capabilities.md).

```bash
# --- Create a canary ---
aws synthetics create-canary \
  --name my-canary \
  --code '{
    "S3Bucket": "my-canary-scripts",
    "S3Key": "my_canary.zip",
    "Handler": "index.handler"
  }' \
  --artifact-s3-location s3://my-canary-artifacts/prefix/ \
  --execution-role-arn arn:aws:iam::123456789012:role/MyCanaryRole \
  --schedule '{"Expression":"rate(5 minutes)","DurationInSeconds":0}' \
  --runtime-version syn-nodejs-puppeteer-15.0 \
  --run-config '{
    "TimeoutInSeconds": 60,
    "MemoryInMB": 960,
    "ActiveTracing": false,
    "EnvironmentVariables": {
      "APP_URL": "https://example.com",
      "SECRET_NAME": "prod/myapp/creds"
    }
  }' \
  --success-retention-period-in-days 31 \
  --failure-retention-period-in-days 31 \
  --tags Environment=Production,Team=Platform

# Create canary with VPC, KMS encryption, and retries
aws synthetics create-canary \
  --name my-vpc-canary \
  --code '{"S3Bucket":"bucket","S3Key":"canary.zip","Handler":"index.handler"}' \
  --artifact-s3-location s3://my-artifacts/canaries/ \
  --execution-role-arn arn:aws:iam::123456789012:role/CanaryRole \
  --schedule '{
    "Expression": "rate(5 minutes)",
    "DurationInSeconds": 0,
    "RetryConfig": {"MaxRetries": 2}
  }' \
  --runtime-version syn-nodejs-puppeteer-15.0 \
  --vpc-config '{"SubnetIds":["subnet-abc123"],"SecurityGroupIds":["sg-xyz789"]}' \
  --artifact-config '{
    "S3Encryption": {
      "EncryptionMode": "SSE_KMS",
      "KmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/my-key"
    }
  }' \
  --provisioned-resource-cleanup AUTOMATIC

# Create with inline ZIP (max 225 KB)
aws synthetics create-canary \
  --name inline-canary \
  --code "{\"ZipFile\":\"$(base64 -w0 canary.zip)\",\"Handler\":\"index.handler\"}" \
  --artifact-s3-location s3://my-artifacts/inline/ \
  --execution-role-arn arn:aws:iam::123456789012:role/CanaryRole \
  --schedule '{"Expression":"rate(5 minutes)"}' \
  --runtime-version syn-nodejs-puppeteer-15.0

# --- Lifecycle ---
aws synthetics start-canary --name my-canary
aws synthetics stop-canary --name my-canary

# Delete canary (and associated Lambda if --provisioned-resource-cleanup AUTOMATIC was set)
aws synthetics delete-canary --name my-canary

# --- Read canary status ---
aws synthetics get-canary --name my-canary
aws synthetics describe-canaries
aws synthetics describe-canaries --names my-canary my-other-canary
aws synthetics describe-canaries-last-run
aws synthetics describe-canaries-last-run --names my-canary

# Get recent run results
aws synthetics get-canary-runs --name my-canary
aws synthetics get-canary-runs --name my-canary --max-results 5

# List available runtime versions
aws synthetics describe-runtime-versions

# --- Update a canary ---
# Update runtime version
aws synthetics update-canary \
  --name my-canary \
  --runtime-version syn-nodejs-puppeteer-15.0

# Update schedule
aws synthetics update-canary \
  --name my-canary \
  --schedule '{"Expression":"rate(1 minute)"}'

# Update script (reference new S3 key)
aws synthetics update-canary \
  --name my-canary \
  --code '{"S3Bucket":"bucket","S3Key":"new_version.zip","Handler":"index.handler"}'

# --- Safe Canary Updates (Dry Run) ---
# Start a dry run with proposed runtime upgrade
aws synthetics start-canary-dry-run \
  --name my-canary \
  --runtime-version syn-nodejs-puppeteer-15.0
# Returns dry-run-id

# Check dry run status
aws synthetics get-canary --name my-canary --dry-run-id <dry-run-id>

# View dry run results
aws synthetics get-canary-runs --name my-canary --dry-run-id <dry-run-id>

# Commit the update if dry run succeeded
aws synthetics update-canary --name my-canary --dry-run-id <dry-run-id>

# --- Canary Groups ---
# Create a group (global resource, region-agnostic)
aws synthetics create-group --name my-group

# Add a canary to a group
aws synthetics associate-resource \
  --group-identifier my-group \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary

# List groups
aws synthetics list-groups

# Get group details
aws synthetics get-group --group-identifier my-group

# List canaries in a group
aws synthetics list-group-resources --group-identifier my-group

# List groups a canary belongs to
aws synthetics list-associated-groups \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary

# Remove canary from group
aws synthetics disassociate-resource \
  --group-identifier my-group \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary

# Delete group
aws synthetics delete-group --group-identifier my-group

# --- Tags ---
aws synthetics tag-resource \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary \
  --tags Environment=Production,Team=Platform

aws synthetics untag-resource \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary \
  --tag-keys Environment

aws synthetics list-tags-for-resource \
  --resource-arn arn:aws:synthetics:us-east-1:123456789012:canary:my-canary

# --- CloudWatch Alarm on Canary SuccessPercent ---
# Alert if SuccessPercent drops below 100 for 2 consecutive 5-minute periods
aws cloudwatch put-metric-alarm \
  --alarm-name "MyCanary-SuccessPercent-Low" \
  --alarm-description "Canary success rate below 100%" \
  --namespace CloudWatchSynthetics \
  --metric-name SuccessPercent \
  --dimensions Name=CanaryName,Value=my-canary \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 100 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:on-call-topic \
  --ok-actions arn:aws:sns:us-east-1:123456789012:on-call-topic

# Alarm on Duration (latency regression)
aws cloudwatch put-metric-alarm \
  --alarm-name "MyCanary-High-Duration" \
  --namespace CloudWatchSynthetics \
  --metric-name Duration \
  --dimensions Name=CanaryName,Value=my-canary \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 10000 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:on-call-topic
```
