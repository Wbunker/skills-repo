# AWS Lambda Error Handling — CLI Reference

For error handling concepts, see [lambda-error-handling-capabilities.md](lambda-error-handling-capabilities.md).

## Async Invocation Config (Retry + Max Age)

```bash
# Set retry attempts and max event age for async invocations
aws lambda put-function-event-invoke-config \
  --function-name my-function \
  --maximum-retry-attempts 1 \
  --maximum-event-age-in-seconds 3600

# Update existing config
aws lambda update-function-event-invoke-config \
  --function-name my-function \
  --maximum-retry-attempts 0

# Get current async invoke config
aws lambda get-function-event-invoke-config \
  --function-name my-function

# Delete (resets to defaults: 2 retries, 6-hour max age)
aws lambda delete-function-event-invoke-config \
  --function-name my-function

# Apply to a specific alias or version
aws lambda put-function-event-invoke-config \
  --function-name my-function:prod \
  --maximum-retry-attempts 2 \
  --maximum-event-age-in-seconds 7200
```

---

## Dead Letter Queue (DLQ)

```bash
# Configure DLQ (SQS or SNS)
aws lambda update-function-configuration \
  --function-name my-function \
  --dead-letter-config TargetArn=arn:aws:sqs:us-east-1:123456789012:my-dlq

# Remove DLQ
aws lambda update-function-configuration \
  --function-name my-function \
  --dead-letter-config TargetArn=

# Verify DLQ config
aws lambda get-function-configuration \
  --function-name my-function \
  --query 'DeadLetterConfig'
```

---

## Lambda Destinations

```bash
# Configure on-failure and on-success destinations for async invocations
aws lambda put-function-event-invoke-config \
  --function-name my-function \
  --destination-config '{
    "OnSuccess": {
      "Destination": "arn:aws:sqs:us-east-1:123456789012:success-queue"
    },
    "OnFailure": {
      "Destination": "arn:aws:sqs:us-east-1:123456789012:failure-queue"
    }
  }'

# On-failure only (e.g., EventBridge)
aws lambda put-function-event-invoke-config \
  --function-name my-function \
  --destination-config '{
    "OnFailure": {
      "Destination": "arn:aws:events:us-east-1:123456789012:event-bus/my-bus"
    }
  }'

# On-failure to S3
aws lambda put-function-event-invoke-config \
  --function-name my-function \
  --destination-config '{
    "OnFailure": {
      "Destination": "arn:aws:s3:::my-failure-bucket"
    }
  }'
```

---

## Event Source Mapping — Error Config

### SQS — Enable Partial Batch Response

```bash
# Create ESM with ReportBatchItemFailures enabled
aws lambda create-event-source-mapping \
  --function-name my-function \
  --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --batch-size 10 \
  --function-response-types ReportBatchItemFailures

# Update existing ESM to enable partial batch response
aws lambda update-event-source-mapping \
  --uuid <esm-uuid> \
  --function-response-types ReportBatchItemFailures

# Disable partial batch response
aws lambda update-event-source-mapping \
  --uuid <esm-uuid> \
  --function-response-types '[]'
```

### Kinesis / DynamoDB Streams — Error Config

```bash
# Create ESM with error handling settings
aws lambda create-event-source-mapping \
  --function-name my-function \
  --event-source-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
  --starting-position LATEST \
  --batch-size 100 \
  --maximum-retry-attempts 3 \
  --maximum-record-age-in-seconds 3600 \
  --bisect-batch-on-function-error \
  --destination-config '{
    "OnFailure": {
      "Destination": "arn:aws:sqs:us-east-1:123456789012:stream-failures"
    }
  }' \
  --function-response-types ReportBatchItemFailures

# Update bisect-on-error on existing ESM
aws lambda update-event-source-mapping \
  --uuid <esm-uuid> \
  --bisect-batch-on-function-error

# Update retry and record age limits
aws lambda update-event-source-mapping \
  --uuid <esm-uuid> \
  --maximum-retry-attempts 5 \
  --maximum-record-age-in-seconds 86400

# Add on-failure destination to existing ESM
aws lambda update-event-source-mapping \
  --uuid <esm-uuid> \
  --destination-config '{
    "OnFailure": {
      "Destination": "arn:aws:sqs:us-east-1:123456789012:kinesis-dlq"
    }
  }'
```

### Get ESM UUID

```bash
# List all ESMs for a function to find the UUID
aws lambda list-event-source-mappings \
  --function-name my-function \
  --query 'EventSourceMappings[*].[UUID, EventSourceArn, State]' \
  --output table
```

---

## Invoke and Inspect Errors

```bash
# Invoke synchronously and capture error header
aws lambda invoke \
  --function-name my-function \
  --payload '{"test": true}' \
  --log-type Tail \
  output.json
# Check for X-Amz-Function-Error in response metadata

# Check FunctionError field in response
aws lambda invoke \
  --function-name my-function \
  --payload '{"test": true}' \
  output.json \
  --query 'FunctionError'

# Invoke async and check queue/destination for errors
aws lambda invoke \
  --function-name my-function \
  --invocation-type Event \
  --payload '{"test": true}' \
  output.json
```

---

## CloudWatch — Query Lambda Error Metrics

```bash
# Get error count for last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Sum

# Get DLQ delivery failures
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name DeadLetterErrors \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Sum

# Get IteratorAge for Kinesis/DynamoDB ESM (rising = backlog)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name IteratorAge \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Maximum
```
