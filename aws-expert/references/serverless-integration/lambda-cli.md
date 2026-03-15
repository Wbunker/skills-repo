# AWS Lambda — CLI Reference
For service concepts, see [lambda-capabilities.md](lambda-capabilities.md).

## Lambda

```bash
# --- Create and deploy ---
aws lambda create-function \
  --function-name my-function \
  --runtime python3.12 \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# Create from container image
aws lambda create-function \
  --function-name my-container-function \
  --package-type Image \
  --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/my-image:latest \
  --role arn:aws:iam::123456789012:role/lambda-role

# Update function code (zip)
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

# Update function code (S3)
aws lambda update-function-code \
  --function-name my-function \
  --s3-bucket my-bucket \
  --s3-key function.zip \
  --s3-object-version versionId

# Update configuration
aws lambda update-function-configuration \
  --function-name my-function \
  --timeout 60 \
  --memory-size 512 \
  --environment "Variables={KEY=value,OTHER=value2}"

# --- Versions and aliases ---
aws lambda publish-version \
  --function-name my-function \
  --description "v1.2.0 release"

aws lambda list-versions-by-function --function-name my-function

aws lambda create-alias \
  --function-name my-function \
  --name prod \
  --function-version 3

# Alias with traffic routing (canary)
aws lambda update-alias \
  --function-name my-function \
  --name prod \
  --function-version 4 \
  --routing-config AdditionalVersionWeights={"3"=0.1}

# --- Invocation ---
aws lambda invoke \
  --function-name my-function \
  --payload '{"key":"value"}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# Async invocation
aws lambda invoke \
  --function-name my-function \
  --invocation-type Event \
  --payload '{"key":"value"}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# Invoke by alias
aws lambda invoke \
  --function-name my-function:prod \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# --- Event source mappings ---
# SQS trigger
aws lambda create-event-source-mapping \
  --function-name my-function \
  --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --batch-size 10 \
  --maximum-batching-window-in-seconds 5

# Kinesis trigger with bisect on error and destination
aws lambda create-event-source-mapping \
  --function-name my-function \
  --event-source-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
  --starting-position LATEST \
  --batch-size 100 \
  --bisect-batch-on-function-error \
  --maximum-retry-attempts 3 \
  --destination-config '{"OnFailure":{"Destination":"arn:aws:sqs:us-east-1:123456789012:dlq"}}'

# With event filter
aws lambda create-event-source-mapping \
  --function-name my-function \
  --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --filter-criteria '{"Filters":[{"Pattern":"{\"body\":{\"status\":[\"PENDING\"]}}"}]}'

aws lambda update-event-source-mapping \
  --uuid a1b2c3d4-1234-1234-1234-a1b2c3d4e5f6 \
  --batch-size 20 \
  --enabled

aws lambda delete-event-source-mapping \
  --uuid a1b2c3d4-1234-1234-1234-a1b2c3d4e5f6

aws lambda list-event-source-mappings --function-name my-function

# --- Concurrency ---
# Reserved concurrency
aws lambda put-function-concurrency \
  --function-name my-function \
  --reserved-concurrent-executions 100

aws lambda delete-function-concurrency --function-name my-function

# Provisioned concurrency (on an alias)
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod \
  --provisioned-concurrent-executions 50

aws lambda delete-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod

aws lambda get-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod

aws lambda get-account-settings  # check account-level concurrency quota

# --- Function URLs ---
aws lambda create-function-url-config \
  --function-name my-function \
  --qualifier prod \
  --auth-type AWS_IAM \
  --cors-config '{"AllowOrigins":["https://example.com"],"AllowMethods":["GET","POST"],"MaxAge":300}'

aws lambda get-function-url-config --function-name my-function --qualifier prod
aws lambda update-function-url-config --function-name my-function --qualifier prod --auth-type NONE
aws lambda delete-function-url-config --function-name my-function --qualifier prod
aws lambda list-function-url-configs --function-name my-function

# --- Async invocation destinations ---
aws lambda put-function-event-invoke-config \
  --function-name my-function \
  --maximum-retry-attempts 2 \
  --maximum-event-age-in-seconds 3600 \
  --destination-config '{
    "OnSuccess":{"Destination":"arn:aws:sqs:us-east-1:123456789012:success-queue"},
    "OnFailure":{"Destination":"arn:aws:sns:us-east-1:123456789012:failure-topic"}
  }'

# --- Resource-based policies ---
# Allow API Gateway to invoke function
aws lambda add-permission \
  --function-name my-function \
  --statement-id allow-apigw \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:api-id/*/GET/resource"

# Allow EventBridge rule
aws lambda add-permission \
  --function-name my-function \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:123456789012:rule/my-rule

aws lambda remove-permission --function-name my-function --statement-id allow-apigw
aws lambda get-policy --function-name my-function

# --- Layers ---
aws lambda publish-layer-version \
  --layer-name my-layer \
  --description "Shared dependencies" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.12 python3.11

aws lambda list-layers --compatible-runtime python3.12
aws lambda list-layer-versions --layer-name my-layer
aws lambda get-layer-version --layer-name my-layer --version-number 3

# Share layer with another account
aws lambda add-layer-version-permission \
  --layer-name my-layer \
  --version-number 3 \
  --statement-id share-with-account \
  --action lambda:GetLayerVersion \
  --principal 987654321098

# --- Querying and management ---
aws lambda list-functions --max-items 100
aws lambda get-function --function-name my-function
aws lambda get-function-configuration --function-name my-function
aws lambda delete-function --function-name my-function
aws lambda tag-resource \
  --resource arn:aws:lambda:us-east-1:123456789012:function:my-function \
  --tags Env=prod,Team=platform

# SnapStart configuration
aws lambda update-function-configuration \
  --function-name my-java-function \
  --snap-start ApplyOn=PublishedVersions
```
