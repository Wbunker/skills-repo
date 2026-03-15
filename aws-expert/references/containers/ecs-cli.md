# AWS ECS — CLI Reference
For service concepts, see [ecs-capabilities.md](ecs-capabilities.md).

```bash
# --- Clusters ---
aws ecs create-cluster --cluster-name my-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=3

aws ecs list-clusters

aws ecs describe-clusters --clusters my-cluster \
  --include SETTINGS STATISTICS ATTACHMENTS CONFIGURATIONS TAGS

aws ecs update-cluster --cluster my-cluster \
  --settings name=containerInsights,value=enabled

aws ecs delete-cluster --cluster my-cluster

# --- Capacity Providers ---
# Create an EC2 Auto Scaling Group capacity provider
aws ecs create-capacity-provider \
  --name my-asg-cp \
  --auto-scaling-group-provider \
    autoScalingGroupArn=arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:...,\
managedScaling='{status=ENABLED,targetCapacity=75,minimumScalingStepSize=1,maximumScalingStepSize=1000}',\
managedTerminationProtection=ENABLED

aws ecs describe-capacity-providers \
  --capacity-providers my-asg-cp FARGATE FARGATE_SPOT

aws ecs put-cluster-capacity-providers --cluster my-cluster \
  --capacity-providers FARGATE FARGATE_SPOT my-asg-cp \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1

aws ecs update-capacity-provider --name my-asg-cp \
  --auto-scaling-group-provider \
    managedScaling='{status=ENABLED,targetCapacity=80}'

# --- Task Definitions ---
# Register a task definition (Fargate)
aws ecs register-task-definition \
  --family my-app \
  --requires-compatibilities FARGATE \
  --cpu 512 --memory 1024 \
  --network-mode awsvpc \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --task-role-arn arn:aws:iam::123456789012:role/myTaskRole \
  --container-definitions '[
    {
      "name": "app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [{"name": "ENV", "value": "production"}],
      "secrets": [
        {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30, "timeout": 5, "retries": 3, "startPeriod": 60
      },
      "cpu": 256, "memory": 512
    }
  ]'

aws ecs list-task-definitions
aws ecs list-task-definitions --family-prefix my-app --status ACTIVE --sort DESC

aws ecs describe-task-definition --task-definition my-app:3
aws ecs describe-task-definition --task-definition my-app  # latest active revision

# Deregister a specific revision (makes it INACTIVE; tasks still run until stopped)
aws ecs deregister-task-definition --task-definition my-app:1

# Permanently delete INACTIVE revisions (cannot be undone)
aws ecs delete-task-definitions --task-definitions my-app:1 my-app:2

aws ecs list-task-definition-families --family-prefix my

# --- Services ---
# Create a Fargate service
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-svc \
  --task-definition my-app:3 \
  --desired-count 2 \
  --capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=3 \
  --network-configuration \
    'awsvpcConfiguration={subnets=[subnet-aaa,subnet-bbb],securityGroups=[sg-abc],assignPublicIp=DISABLED}' \
  --load-balancers \
    'targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=app,containerPort=8080' \
  --deployment-configuration \
    'minimumHealthyPercent=100,maximumPercent=200' \
  --enable-execute-command

# Update a service (new task definition, scale, or force re-deploy)
aws ecs update-service \
  --cluster my-cluster \
  --service my-svc \
  --task-definition my-app:4 \
  --desired-count 4 \
  --force-new-deployment

# Update service with blue/green CodeDeploy deployment controller
aws ecs update-service \
  --cluster my-cluster \
  --service my-svc \
  --task-definition my-app:5 \
  --deployment-controller type=CODE_DEPLOY

aws ecs list-services --cluster my-cluster
aws ecs list-services-by-namespace --namespace my-namespace

aws ecs describe-services --cluster my-cluster --services my-svc

aws ecs delete-service --cluster my-cluster --service my-svc --force

# Service Connect configuration
aws ecs update-service \
  --cluster my-cluster \
  --service my-svc \
  --service-connect-configuration '{
    "enabled": true,
    "namespace": "my-namespace",
    "services": [{
      "portName": "http",
      "discoveryName": "my-app",
      "clientAliases": [{"port": 80, "dnsName": "my-app"}]
    }]
  }'

# --- Service Auto Scaling (via Application Auto Scaling) ---
# Register ECS service as a scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/my-cluster/my-svc \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 --max-capacity 20

# Target Tracking policy (CPU utilization)
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-target-tracking \
  --service-namespace ecs \
  --resource-id service/my-cluster/my-svc \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 60.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# --- Tasks ---
# Run a one-off task (Fargate)
aws ecs run-task \
  --cluster my-cluster \
  --task-definition my-app:3 \
  --launch-type FARGATE \
  --network-configuration \
    'awsvpcConfiguration={subnets=[subnet-aaa],securityGroups=[sg-abc],assignPublicIp=DISABLED}' \
  --overrides '{"containerOverrides": [{"name": "app", "command": ["python", "migrate.py"]}]}'

# Start a task on a specific container instance (EC2 launch type)
aws ecs start-task \
  --cluster my-cluster \
  --task-definition my-app:3 \
  --container-instances ci-abc123

aws ecs stop-task --cluster my-cluster --task <task-id> --reason "manual stop"

aws ecs list-tasks --cluster my-cluster
aws ecs list-tasks --cluster my-cluster --service-name my-svc
aws ecs list-tasks --cluster my-cluster --desired-status STOPPED

aws ecs describe-tasks --cluster my-cluster --tasks <task-id-1> <task-id-2>

# Task protection (prevent a running task from being stopped by scale-in)
aws ecs update-task-protection \
  --cluster my-cluster \
  --tasks <task-id> \
  --protection-enabled \
  --expires-in-minutes 60

aws ecs get-task-protection --cluster my-cluster --tasks <task-id>

# --- ECS Exec (interactive access to running container) ---
# Requires enableExecuteCommand on the service and ssmmessages permissions on the task role
aws ecs execute-command \
  --cluster my-cluster \
  --task <task-id> \
  --container app \
  --interactive \
  --command "/bin/bash"

# Non-interactive single command
aws ecs execute-command \
  --cluster my-cluster \
  --task <task-id> \
  --container app \
  --command "cat /etc/os-release"

# --- Container Instances (EC2 launch type) ---
aws ecs list-container-instances --cluster my-cluster

aws ecs describe-container-instances \
  --cluster my-cluster \
  --container-instances <instance-arn-1> <instance-arn-2>

# Drain a container instance before deregistering
aws ecs update-container-instances-state \
  --cluster my-cluster \
  --container-instances <instance-arn> \
  --status DRAINING

aws ecs deregister-container-instance \
  --cluster my-cluster \
  --container-instance <instance-arn> \
  --force

aws ecs update-container-agent \
  --cluster my-cluster \
  --container-instance <instance-arn>

# --- Tagging ---
aws ecs tag-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster \
  --tags key=Environment,value=production key=Team,value=platform

aws ecs list-tags-for-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster

aws ecs untag-resource \
  --resource-arn arn:aws:ecs:us-east-1:123456789012:cluster/my-cluster \
  --tag-keys Environment

# --- Service Deployments ---
aws ecs list-service-deployments --cluster my-cluster --service my-svc
aws ecs describe-service-deployments \
  --service-deployment-arns arn:aws:ecs:us-east-1:123456789012:service-deployment/my-cluster/my-svc/abc123
aws ecs stop-service-deployment \
  --service-deployment-arn arn:aws:ecs:us-east-1:123456789012:service-deployment/my-cluster/my-svc/abc123

# --- Account Settings ---
aws ecs put-account-setting-default --name containerInsights --value enabled
aws ecs list-account-settings --effective-settings
```
