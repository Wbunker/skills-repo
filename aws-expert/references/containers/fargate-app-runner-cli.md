# AWS Fargate & App Runner — CLI Reference
For service concepts, see [fargate-app-runner-capabilities.md](fargate-app-runner-capabilities.md).

> Note: Fargate is not managed via its own CLI; Fargate tasks and pods are launched through `aws ecs` (see [ecs-cli.md](ecs-cli.md)) and `aws eks` (see [eks-cli.md](eks-cli.md)) respectively. The CLI commands below cover AWS App Runner (`aws apprunner`).

## App Runner

```bash
# --- Services ---
# Create a service from a container image in ECR
aws apprunner create-service \
  --service-name my-api \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {"ENV": "production"},
        "RuntimeEnvironmentSecrets": {"DB_PASSWORD": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"}
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::123456789012:role/AppRunnerECRAccessRole"
    }
  }' \
  --instance-configuration 'Cpu=1 vCPU,Memory=2 GB' \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/my-asc/1/abc \
  --instance-role-arn arn:aws:iam::123456789012:role/AppRunnerInstanceRole

# Create a service from source code (GitHub)
aws apprunner create-service \
  --service-name my-web-app \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/my-org/my-repo",
      "SourceCodeVersion": {"Type": "BRANCH", "Value": "main"},
      "CodeConfiguration": {
        "ConfigurationSource": "REPOSITORY",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "python app.py",
          "Port": "8080"
        }
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "ConnectionArn": "arn:aws:apprunner:us-east-1:123456789012:connection/github-conn/abc"
    }
  }'

aws apprunner list-services

aws apprunner describe-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

# Update service (new image tag, instance size, environment variables)
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --instance-configuration 'Cpu=2 vCPU,Memory=4 GB'

# Trigger a manual deployment
aws apprunner start-deployment \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

# Pause and resume (stops billing for instance hours; useful for non-prod)
aws apprunner pause-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

aws apprunner resume-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

aws apprunner delete-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

# --- Auto Scaling Configuration ---
aws apprunner create-auto-scaling-configuration \
  --auto-scaling-configuration-name my-asc \
  --min-size 1 \
  --max-size 25 \
  --max-concurrency 100

aws apprunner list-auto-scaling-configurations
aws apprunner list-auto-scaling-configurations \
  --auto-scaling-configuration-name my-asc

aws apprunner describe-auto-scaling-configuration \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/my-asc/1/abc

aws apprunner update-default-auto-scaling-configuration \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/my-asc/1/abc

aws apprunner list-services-for-auto-scaling-configuration \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/my-asc/1/abc

aws apprunner delete-auto-scaling-configuration \
  --auto-scaling-configuration-arn arn:aws:apprunner:us-east-1:123456789012:autoscalingconfiguration/my-asc/1/abc

# --- Custom Domains ---
aws apprunner associate-custom-domain \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --domain-name api.example.com \
  --enable-www-subdomain  # also associate www.api.example.com

# Get DNS validation records to add to your DNS provider
aws apprunner describe-custom-domains \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

aws apprunner disassociate-custom-domain \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --domain-name api.example.com

# --- VPC Connector (outbound to VPC resources) ---
aws apprunner create-vpc-connector \
  --vpc-connector-name my-vpc-connector \
  --subnets subnet-private-aaa subnet-private-bbb \
  --security-groups sg-app-runner-outbound

aws apprunner list-vpc-connectors

aws apprunner describe-vpc-connector \
  --vpc-connector-arn arn:aws:apprunner:us-east-1:123456789012:vpcconnector/my-vpc-connector/1/abc

# Attach VPC connector to a service
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --network-configuration '{
    "EgressConfiguration": {
      "EgressType": "VPC",
      "VpcConnectorArn": "arn:aws:apprunner:us-east-1:123456789012:vpcconnector/my-vpc-connector/1/abc"
    }
  }'

aws apprunner delete-vpc-connector \
  --vpc-connector-arn arn:aws:apprunner:us-east-1:123456789012:vpcconnector/my-vpc-connector/1/abc

# --- VPC Ingress Connection (restrict inbound to a VPC) ---
aws apprunner create-vpc-ingress-connection \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --vpc-ingress-connection-name my-ingress-conn \
  --ingress-vpc-configuration VpcId=vpc-abc123,VpcEndpointId=vpce-xyz

aws apprunner list-vpc-ingress-connections
aws apprunner describe-vpc-ingress-connection \
  --vpc-ingress-connection-arn arn:aws:apprunner:us-east-1:123456789012:vpcingressconnection/my-ingress-conn/abc

aws apprunner delete-vpc-ingress-connection \
  --vpc-ingress-connection-arn arn:aws:apprunner:us-east-1:123456789012:vpcingressconnection/my-ingress-conn/abc

# --- Connections (GitHub / Bitbucket) ---
aws apprunner create-connection \
  --connection-name github-conn \
  --provider-type GITHUB

aws apprunner list-connections
aws apprunner delete-connection \
  --connection-arn arn:aws:apprunner:us-east-1:123456789012:connection/github-conn/abc

# --- Observability Configuration ---
aws apprunner create-observability-configuration \
  --observability-configuration-name my-obs-config \
  --trace-configuration vendor=AWSXRAY

aws apprunner list-observability-configurations
aws apprunner describe-observability-configuration \
  --observability-configuration-arn arn:aws:apprunner:us-east-1:123456789012:observabilityconfiguration/my-obs-config/1/abc

# Attach observability config to a service
aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --observability-configuration '{
    "ObservabilityEnabled": true,
    "ObservabilityConfigurationArn": "arn:aws:apprunner:us-east-1:123456789012:observabilityconfiguration/my-obs-config/1/abc"
  }'

aws apprunner delete-observability-configuration \
  --observability-configuration-arn arn:aws:apprunner:us-east-1:123456789012:observabilityconfiguration/my-obs-config/1/abc

# --- Operations ---
aws apprunner list-operations \
  --service-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

# --- Tagging ---
aws apprunner tag-resource \
  --resource-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --tags Key=Environment,Value=production

aws apprunner list-tags-for-resource \
  --resource-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc

aws apprunner untag-resource \
  --resource-arn arn:aws:apprunner:us-east-1:123456789012:service/my-api/abc \
  --tag-keys Environment
```
