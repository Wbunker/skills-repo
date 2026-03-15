# AWS Lambda — CLI Reference

For service concepts, see [lambda-capabilities.md](lambda-capabilities.md).

## AWS Lambda

```bash
# --- Create Function ---
# From a zip file
aws lambda create-function \
  --function-name my-api-handler \
  --runtime python3.13 \
  --role arn:aws:iam::123456789012:role/LambdaExecutionRole \
  --handler app.handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment "Variables={LOG_LEVEL=INFO,TABLE_NAME=my-table}" \
  --architectures arm64 \
  --description "API request handler"

# From a container image in ECR
aws lambda create-function \
  --function-name my-container-function \
  --package-type Image \
  --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest \
  --role arn:aws:iam::123456789012:role/LambdaExecutionRole \
  --timeout 60 \
  --memory-size 1024

# --- Describe and List Functions ---
aws lambda get-function --function-name my-api-handler
aws lambda get-function-configuration --function-name my-api-handler
aws lambda list-functions
aws lambda list-functions --function-version ALL

# --- Update Function Code ---
aws lambda update-function-code \
  --function-name my-api-handler \
  --zip-file fileb://function.zip

aws lambda update-function-code \
  --function-name my-api-handler \
  --s3-bucket my-deployment-bucket \
  --s3-key functions/my-api-handler-v2.zip

# Update container image
aws lambda update-function-code \
  --function-name my-container-function \
  --image-uri 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:v2

# --- Update Function Configuration ---
aws lambda update-function-configuration \
  --function-name my-api-handler \
  --timeout 60 \
  --memory-size 1024 \
  --environment "Variables={LOG_LEVEL=DEBUG,TABLE_NAME=my-table}" \
  --ephemeral-storage '{"Size": 2048}'

# --- Invoke Function ---
# Synchronous invocation
aws lambda invoke \
  --function-name my-api-handler \
  --payload '{"action":"test","data":"hello"}' \
  --cli-binary-format raw-in-base64-out \
  output.json
cat output.json

# Asynchronous invocation (Event)
aws lambda invoke \
  --function-name my-api-handler \
  --invocation-type Event \
  --payload '{"records":[{"id":1},{"id":2}]}' \
  --cli-binary-format raw-in-base64-out \
  /dev/null

# Dry run (validate permissions without executing)
aws lambda invoke \
  --function-name my-api-handler \
  --invocation-type DryRun \
  /dev/null

# --- Versions and Aliases ---
# Publish a version (immutable snapshot)
aws lambda publish-version \
  --function-name my-api-handler \
  --description "Stable v1.2.0 release"

aws lambda list-versions-by-function --function-name my-api-handler

# Create an alias pointing to a version
aws lambda create-alias \
  --function-name my-api-handler \
  --name prod \
  --function-version 3 \
  --description "Production alias"

# Weighted alias for canary deployment (10% to v4)
aws lambda update-alias \
  --function-name my-api-handler \
  --name prod \
  --function-version 3 \
  --routing-config '{"AdditionalVersionWeights":{"4":0.1}}'

aws lambda list-aliases --function-name my-api-handler
aws lambda get-alias --function-name my-api-handler --name prod
aws lambda delete-alias --function-name my-api-handler --name prod

# --- Concurrency ---
# Reserve concurrency for a function (also caps maximum)
aws lambda put-function-concurrency \
  --function-name my-api-handler \
  --reserved-concurrent-executions 200

aws lambda get-function-concurrency --function-name my-api-handler
aws lambda delete-function-concurrency --function-name my-api-handler

# Provisioned concurrency (on a version or alias)
aws lambda put-provisioned-concurrency-config \
  --function-name my-api-handler \
  --qualifier prod \
  --provisioned-concurrent-executions 50

aws lambda get-provisioned-concurrency-config \
  --function-name my-api-handler \
  --qualifier prod

aws lambda list-provisioned-concurrency-configs --function-name my-api-handler
aws lambda delete-provisioned-concurrency-config \
  --function-name my-api-handler \
  --qualifier prod

# Check account-level concurrency settings
aws lambda get-account-settings

# --- Layers ---
# Publish a new layer version
aws lambda publish-layer-version \
  --layer-name my-dependencies \
  --description "Python dependencies for data processing" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.12 python3.13 \
  --compatible-architectures x86_64 arm64

aws lambda list-layers
aws lambda list-layer-versions --layer-name my-dependencies
aws lambda get-layer-version --layer-name my-dependencies --version-number 3

# Grant cross-account layer usage
aws lambda add-layer-version-permission \
  --layer-name my-dependencies \
  --version-number 3 \
  --statement-id allow-org \
  --action lambda:GetLayerVersion \
  --principal "*" \
  --organization-id o-abc123def456

aws lambda delete-layer-version --layer-name my-dependencies --version-number 1

# --- Event Source Mappings ---
# SQS trigger
aws lambda create-event-source-mapping \
  --function-name my-api-handler \
  --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --batch-size 10 \
  --maximum-batching-window-in-seconds 5 \
  --function-response-types ReportBatchItemFailures

# Kinesis trigger with filtering
aws lambda create-event-source-mapping \
  --function-name my-stream-processor \
  --event-source-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
  --starting-position LATEST \
  --batch-size 100 \
  --bisect-batch-on-function-error \
  --maximum-retry-attempts 3 \
  --destination-config '{"OnFailure":{"Destination":"arn:aws:sqs:us-east-1:123456789012:failures-queue"}}' \
  --filter-criteria '{"Filters":[{"Pattern":"{\"data\":{\"eventType\":[\"ORDER_PLACED\"]}}"}]}'

# DynamoDB Streams trigger
aws lambda create-event-source-mapping \
  --function-name my-ddb-processor \
  --event-source-arn arn:aws:dynamodb:us-east-1:123456789012:table/my-table/stream/2024-01-01T00:00:00.000 \
  --starting-position TRIM_HORIZON \
  --batch-size 50 \
  --parallelization-factor 5

aws lambda list-event-source-mappings --function-name my-api-handler
aws lambda get-event-source-mapping --uuid abc12345-6789-def0-1234-abcdef012345
aws lambda update-event-source-mapping \
  --uuid abc12345-6789-def0-1234-abcdef012345 \
  --batch-size 20
aws lambda delete-event-source-mapping --uuid abc12345-6789-def0-1234-abcdef012345

# --- Asynchronous Invocation Config (Destinations) ---
aws lambda put-function-event-invoke-config \
  --function-name my-api-handler \
  --maximum-event-age-in-seconds 3600 \
  --maximum-retry-attempts 2 \
  --destination-config '{
    "OnSuccess": {"Destination": "arn:aws:sns:us-east-1:123456789012:success-topic"},
    "OnFailure": {"Destination": "arn:aws:sqs:us-east-1:123456789012:failure-queue"}
  }'

aws lambda get-function-event-invoke-config --function-name my-api-handler
aws lambda delete-function-event-invoke-config --function-name my-api-handler

# --- Function URLs ---
aws lambda create-function-url-config \
  --function-name my-api-handler \
  --qualifier prod \
  --auth-type AWS_IAM \
  --cors '{
    "AllowCredentials": false,
    "AllowHeaders": ["*"],
    "AllowMethods": ["GET","POST"],
    "AllowOrigins": ["https://example.com"],
    "MaxAge": 3600
  }'

# Public function URL (no auth)
aws lambda create-function-url-config \
  --function-name my-public-handler \
  --auth-type NONE

aws lambda get-function-url-config --function-name my-api-handler --qualifier prod
aws lambda list-function-url-configs --function-name my-api-handler
aws lambda delete-function-url-config --function-name my-api-handler --qualifier prod

# --- Resource-Based Permissions ---
# Allow API Gateway to invoke a function
aws lambda add-permission \
  --function-name my-api-handler \
  --statement-id allow-api-gateway \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:abc123/*"

# Allow another account to invoke
aws lambda add-permission \
  --function-name my-api-handler \
  --statement-id allow-cross-account \
  --action lambda:InvokeFunction \
  --principal 987654321098

aws lambda get-policy --function-name my-api-handler
aws lambda remove-permission --function-name my-api-handler --statement-id allow-api-gateway

# --- Delete Function ---
aws lambda delete-function --function-name my-api-handler
aws lambda delete-function --function-name my-api-handler --qualifier 1  # delete specific version
```
