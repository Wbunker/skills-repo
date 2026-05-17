# AWS Distro for OpenTelemetry (ADOT) — CLI Reference

For service concepts and collector config, see [adot-capabilities.md](adot-capabilities.md).

## EKS Managed Add-on

```bash
# Install ADOT operator add-on
aws eks create-addon \
  --addon-name adot \
  --cluster-name my-cluster \
  --service-account-role-arn arn:aws:iam::123456789012:role/ADOTCollectorRole

# Check add-on status (CREATING → ACTIVE)
aws eks describe-addon \
  --addon-name adot \
  --cluster-name my-cluster \
  --query 'addon.status'

# Get available add-on versions
aws eks describe-addon-versions \
  --addon-name adot \
  --query 'addons[0].addonVersions[*].addonVersion'

# Update add-on to a new version
aws eks update-addon \
  --addon-name adot \
  --cluster-name my-cluster \
  --addon-version v0.90.0-eksbuild.1

# Delete add-on
aws eks delete-addon \
  --addon-name adot \
  --cluster-name my-cluster
```

---

## Lambda Layer Management

```bash
# List available ADOT Lambda layers in your region
aws lambda list-layers \
  --query 'Layers[?starts_with(LayerName, `aws-otel`)].[LayerName,LatestMatchingVersion.LayerVersionArn]' \
  --output table

# Get latest version of a specific layer (published by account 901920570463)
aws lambda list-layer-versions \
  --layer-name arn:aws:lambda:us-east-1:901920570463:layer:aws-otel-java-wrapper-amd64-ver-1-32-0 \
  --query 'LayerVersions[0].LayerVersionArn'

# Add ADOT layer to a Lambda function
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:us-east-1:901920570463:layer:aws-otel-java-wrapper-amd64-ver-1-32-0:1

# Set auto-instrumentation wrapper (Python/Node.js)
aws lambda update-function-configuration \
  --function-name my-function \
  --environment 'Variables={AWS_LAMBDA_EXEC_WRAPPER=/opt/otel-instrument}'

# Set auto-instrumentation wrapper (Java)
aws lambda update-function-configuration \
  --function-name my-function \
  --environment 'Variables={AWS_LAMBDA_EXEC_WRAPPER=/opt/otel-handler}'

# Verify layers on a function
aws lambda get-function-configuration \
  --function-name my-function \
  --query '[Layers, Environment.Variables.AWS_LAMBDA_EXEC_WRAPPER]'
```

---

## IAM — Create ADOT Collector Policy

```bash
# Create IAM policy for full ADOT collector (X-Ray + CloudWatch + AMP)
aws iam create-policy \
  --policy-name ADOTCollectorPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "xray:GetSamplingStatisticSummaries"
        ],
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:PutRetentionPolicy"
        ],
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": ["aps:RemoteWrite"],
        "Resource": "*"
      }
    ]
  }'

# Attach to an IAM role (e.g., ECS task role or EC2 instance profile)
aws iam attach-role-policy \
  --role-name ADOTCollectorRole \
  --policy-arn arn:aws:iam::123456789012:policy/ADOTCollectorPolicy
```

---

## ECS — Register Task Definition with ADOT Sidecar

```bash
# Register task definition with ADOT collector as sidecar
aws ecs register-task-definition \
  --family my-app-with-adot \
  --requires-compatibilities FARGATE \
  --network-mode awsvpc \
  --cpu 512 --memory 1024 \
  --task-role-arn arn:aws:iam::123456789012:role/ADOTCollectorRole \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --container-definitions '[
    {
      "name": "my-app",
      "image": "my-app:latest",
      "environment": [
        {"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": "http://localhost:4317"}
      ]
    },
    {
      "name": "aoc-collector",
      "image": "public.ecr.aws/aws-observability/aws-otel-collector:latest",
      "user": "root",
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/adot-collector",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]'
```

---

## Verify Collector Health

```bash
# If health_check extension is enabled (default port 13133)
curl http://localhost:13133/

# Check collector version
curl http://localhost:55679/debug/servicez  # zpages extension

# Pull collector image explicitly
docker pull public.ecr.aws/aws-observability/aws-otel-collector:latest

# Run collector locally for testing
docker run \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 2000:2000/udp \
  -v $(pwd)/config.yaml:/etc/otel/config.yaml \
  -e AWS_REGION=us-east-1 \
  public.ecr.aws/aws-observability/aws-otel-collector:latest \
  --config /etc/otel/config.yaml
```
