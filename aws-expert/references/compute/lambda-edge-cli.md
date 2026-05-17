# Lambda@Edge — CLI Reference

For service concepts and event structures, see [lambda-edge-capabilities.md](lambda-edge-capabilities.md).

---

## Create and Deploy a Lambda@Edge Function

```bash
# --- Step 1: Create the IAM execution role (must allow both service principals) ---
aws iam create-role \
  --role-name LambdaEdgeExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "Service": ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]
      },
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach basic execution policy (for CloudWatch Logs)
aws iam attach-role-policy \
  --role-name LambdaEdgeExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# --- Step 2: Package and create the function in us-east-1 (REQUIRED region) ---
zip function.zip index.js

aws lambda create-function \
  --function-name my-edge-function \
  --runtime nodejs22.x \
  --role arn:aws:iam::123456789012:role/LambdaEdgeExecutionRole \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --region us-east-1

# --- Step 3: Publish a numbered version ($LATEST cannot be used with CloudFront) ---
aws lambda publish-version \
  --function-name my-edge-function \
  --description "Viewer request URL rewrite v1" \
  --region us-east-1

# Get the version ARN from output: FunctionArn will look like:
# arn:aws:lambda:us-east-1:123456789012:function:my-edge-function:1
```

---

## Associate with a CloudFront Distribution

```bash
# Get the current distribution config (required to update it)
aws cloudfront get-distribution-config \
  --id EDFDVBD6EXAMPLE \
  --query '[ETag, DistributionConfig]' \
  --output json > dist-config.json

# Edit dist-config.json to add LambdaFunctionAssociations to the desired cache behavior:
# Under CacheBehaviors (or DefaultCacheBehavior):
# "LambdaFunctionAssociations": {
#   "Quantity": 1,
#   "Items": [{
#     "LambdaFunctionARN": "arn:aws:lambda:us-east-1:123456789012:function:my-edge-function:1",
#     "EventType": "viewer-request",
#     "IncludeBody": false
#   }]
# }

# Update the distribution (use the ETag from get-distribution-config)
aws cloudfront update-distribution \
  --id EDFDVBD6EXAMPLE \
  --distribution-config file://dist-config.json \
  --if-match E2QWRUHEXAMPLE
```

---

## Manage Function Versions

```bash
# List all versions of an edge function
aws lambda list-versions-by-function \
  --function-name my-edge-function \
  --region us-east-1 \
  --query 'Versions[*].{Version:Version,ARN:FunctionArn,Description:Description}' \
  --output table

# Get details of a specific version
aws lambda get-function \
  --function-name my-edge-function:3 \
  --region us-east-1

# Update function code and publish new version
zip function.zip index.js

aws lambda update-function-code \
  --function-name my-edge-function \
  --zip-file fileb://function.zip \
  --region us-east-1

# Wait for update to propagate before publishing
aws lambda wait function-updated \
  --function-name my-edge-function \
  --region us-east-1

aws lambda publish-version \
  --function-name my-edge-function \
  --description "Add security headers" \
  --region us-east-1
```

---

## View and Query Logs

Lambda@Edge logs are written to CloudWatch in the region where the edge function ran (nearest to the viewer). Log group format: `/aws/lambda/us-east-1.<function-name>`

```bash
# List log groups for a Lambda@Edge function across regions
# (you must check each region where your viewers are)
for region in us-east-1 us-west-2 eu-west-1 ap-northeast-1 ap-southeast-1; do
  echo "=== $region ==="
  aws logs describe-log-groups \
    --log-group-name-prefix "/aws/lambda/us-east-1.my-edge-function" \
    --region $region \
    --query 'logGroups[*].logGroupName' \
    --output text 2>/dev/null
done

# Get recent log events from a specific region
aws logs filter-log-events \
  --log-group-name /aws/lambda/us-east-1.my-edge-function \
  --start-time $(date -d '1 hour ago' +%s000) \
  --region eu-west-1 \
  --limit 50

# Tail logs in real time from a specific region
aws logs tail /aws/lambda/us-east-1.my-edge-function \
  --follow \
  --region us-east-1

# CloudFront validation errors also appear in /aws/cloudfront/LambdaEdge/
aws logs describe-log-groups \
  --log-group-name-prefix /aws/cloudfront/LambdaEdge/ \
  --region us-east-1
```

---

## CloudFormation / SAM Deployment

```yaml
# SAM template for a Lambda@Edge function
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  EdgeFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: my-viewer-request-handler
      Handler: index.handler
      Runtime: nodejs22.x
      Role: !GetAtt EdgeFunctionRole.Arn
      # Must be in us-east-1 when deployed
      AutoPublishAlias: live   # Creates a new version on each deploy

  EdgeFunctionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
                - edgelambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          LambdaFunctionAssociations:
            - EventType: viewer-request
              LambdaFunctionARN: !Ref EdgeFunction.Version  # versioned ARN
              IncludeBody: false
          # ... other cache behavior config
        # ... other distribution config
```

---

## Service-Linked Roles

```bash
# Manually create the replicator service-linked role (normally auto-created on first trigger)
aws iam create-service-linked-role \
  --aws-service-name replicator.lambda.amazonaws.com

# Manually create the CloudFront logger service-linked role
aws iam create-service-linked-role \
  --aws-service-name logger.cloudfront.amazonaws.com

# Verify service-linked roles exist
aws iam get-role --role-name AWSServiceRoleForLambdaReplicator
aws iam get-role --role-name AWSServiceRoleForCloudFrontLogger
```

---

## Inspect Distribution Lambda@Edge Associations

```bash
# List all Lambda@Edge associations for a distribution
aws cloudfront get-distribution \
  --id EDFDVBD6EXAMPLE \
  --query 'Distribution.DistributionConfig.DefaultCacheBehavior.LambdaFunctionAssociations'

# List associations across all cache behaviors
aws cloudfront get-distribution \
  --id EDFDVBD6EXAMPLE \
  --query 'Distribution.DistributionConfig.CacheBehaviors.Items[*].{Path:PathPattern,Lambda:LambdaFunctionAssociations.Items[*]}' \
  --output json

# List all distributions that use a specific Lambda function
aws cloudfront list-distributions-by-lambda-function \
  --lambda-function-arn arn:aws:lambda:us-east-1:123456789012:function:my-edge-function:3
```

---

## Remove Lambda@Edge Associations

To delete a Lambda@Edge function, you must first disassociate it from all distributions and wait for replicas to be cleaned up.

```bash
# Step 1: Update distribution to remove the Lambda@Edge association
# (edit dist-config.json to set LambdaFunctionAssociations Quantity: 0 and Items: [])
aws cloudfront update-distribution \
  --id EDFDVBD6EXAMPLE \
  --distribution-config file://dist-config-no-lambda.json \
  --if-match E2QWRUHEXAMPLE

# Step 2: Wait for distribution to deploy
aws cloudfront wait distribution-deployed --id EDFDVBD6EXAMPLE

# Step 3: Wait for Lambda@Edge replicas to be automatically deleted
# (AWS deletes replicas within a few hours after disassociation)
# Check replica status
aws lambda list-functions \
  --region eu-west-1 \
  --query 'Functions[?starts_with(FunctionName, `us-east-1.my-edge-function`)]'

# Step 4: Once replicas are gone, delete the function
aws lambda delete-function \
  --function-name my-edge-function \
  --region us-east-1
```

---

## Test a Lambda@Edge Function Locally

```bash
# Create a test event JSON (viewer-request format)
cat > test-event.json << 'EOF'
{
  "Records": [{
    "cf": {
      "config": {
        "distributionDomainName": "d111111abcdef8.cloudfront.net",
        "distributionId": "EDFDVBD6EXAMPLE",
        "eventType": "viewer-request",
        "requestId": "test-request-id-001"
      },
      "request": {
        "clientIp": "203.0.113.178",
        "method": "GET",
        "uri": "/old-path/image.jpg",
        "querystring": "size=large",
        "headers": {
          "host": [{ "key": "Host", "value": "d111111abcdef8.cloudfront.net" }],
          "user-agent": [{ "key": "User-Agent", "value": "curl/7.66.0" }]
        }
      }
    }
  }]
}
EOF

# Invoke the Lambda function with the test event (using $LATEST in us-east-1 for testing)
aws lambda invoke \
  --function-name my-edge-function \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-event.json \
  --region us-east-1 \
  response.json

cat response.json | jq .
```
