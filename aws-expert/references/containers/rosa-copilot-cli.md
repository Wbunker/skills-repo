# ROSA & AWS Copilot — CLI Reference
For service concepts, see [rosa-copilot-capabilities.md](rosa-copilot-capabilities.md).

```bash
# ============================================================
# ROSA CLI
# Install: https://console.redhat.com/openshift/downloads
# Login:   rosa login --token <your-offline-token>
# ============================================================

# --- Prerequisites / account roles ---
# Create IAM account roles (once per AWS account)
rosa create account-roles --mode auto --yes

# List account roles
rosa list account-roles

# Create OIDC configuration (once per cluster for HCP; reusable)
rosa create oidc-config --mode auto --yes

# List OIDC configurations
rosa list oidc-config

# Create operator roles (once per OIDC config / cluster)
rosa create operator-roles \
  --cluster my-rosa-cluster \
  --mode auto \
  --yes

# List operator roles
rosa list operator-roles

# --- Classic cluster ---
rosa create cluster \
  --cluster-name my-rosa-cluster \
  --region us-east-1 \
  --version 4.16 \
  --compute-machine-type m5.xlarge \
  --replicas 3 \
  --multi-az \
  --sts \
  --mode auto \
  --yes

# --- HCP (Hosted Control Plane) cluster ---
rosa create cluster \
  --cluster-name my-hcp-cluster \
  --region us-east-1 \
  --version 4.16 \
  --hosted-cp \
  --oidc-config-id <oidc-config-id> \
  --subnet-ids subnet-aaa,subnet-bbb,subnet-ccc \
  --compute-machine-type m5.xlarge \
  --replicas 2 \
  --sts \
  --mode auto \
  --yes

# --- List and describe clusters ---
rosa list clusters

rosa describe cluster --cluster my-rosa-cluster

rosa describe cluster --cluster my-rosa-cluster \
  --output json | jq '{status: .status.state, version: .version.raw_id}'

# --- Cluster credentials ---
# Create admin user (generates kubeadmin password)
rosa create admin --cluster my-rosa-cluster

# Get kubeconfig
rosa describe cluster --cluster my-rosa-cluster \
  --output json | jq -r '.api.url'
# Then: oc login <api-url> --username kubeadmin --password <password>

# --- Machine pools ---
rosa create machinepool \
  --cluster my-rosa-cluster \
  --name gpu-pool \
  --instance-type p3.2xlarge \
  --replicas 2 \
  --labels node-type=gpu \
  --taints dedicated=gpu:NoSchedule

# Create autoscaling machine pool
rosa create machinepool \
  --cluster my-rosa-cluster \
  --name autoscale-pool \
  --instance-type m5.2xlarge \
  --enable-autoscaling \
  --min-replicas 1 \
  --max-replicas 10 \
  --availability-zone us-east-1a

rosa list machinepools --cluster my-rosa-cluster

rosa describe machinepool \
  --cluster my-rosa-cluster \
  --machinepool autoscale-pool

# Edit machine pool (update replicas or autoscaling bounds)
rosa edit machinepool \
  --cluster my-rosa-cluster \
  --machinepool autoscale-pool \
  --min-replicas 2 \
  --max-replicas 20

rosa delete machinepool \
  --cluster my-rosa-cluster \
  --machinepool gpu-pool \
  --yes

# --- Upgrades ---
# List available upgrade versions
rosa list upgrades --cluster my-rosa-cluster

# Schedule immediate upgrade
rosa upgrade cluster \
  --cluster my-rosa-cluster \
  --version 4.16.15 \
  --yes

# Schedule upgrade at a specific time
rosa upgrade cluster \
  --cluster my-rosa-cluster \
  --version 4.16.15 \
  --schedule-date 2026-04-01 \
  --schedule-time 02:00

# List scheduled upgrades
rosa list upgrades --cluster my-rosa-cluster

# Cancel a scheduled upgrade
rosa delete upgrade --cluster my-rosa-cluster --yes

# --- Upgrade channel ---
rosa edit cluster \
  --cluster my-rosa-cluster \
  --channel-group stable

# --- Ingress ---
rosa list ingresses --cluster my-rosa-cluster

rosa edit ingress \
  --cluster my-rosa-cluster \
  --id <ingress-id> \
  --private  # restrict to private (internal) only

# --- Logging ---
rosa create service-log \
  --cluster my-rosa-cluster \
  --service-name my-app \
  --severity Info \
  --summary "Deployment started"

rosa list service-logs --cluster my-rosa-cluster

# --- Delete cluster ---
rosa delete cluster --cluster my-rosa-cluster --yes

# After deletion, clean up operator roles and OIDC config
rosa delete operator-roles --cluster my-rosa-cluster --mode auto --yes
rosa delete oidc-config --oidc-config-id <oidc-config-id> --mode auto --yes

# ============================================================
# AWS Copilot CLI
# Install: brew install aws/tap/copilot-cli
#          or: curl -Lo copilot https://github.com/aws/copilot-cli/releases/latest/download/copilot-linux
# ============================================================

# --- Application ---
# Initialize a new application (registers app name in SSM)
copilot app init my-app

# List applications
copilot app ls

# Show application summary (services, jobs, environments)
copilot app show --name my-app

# Delete application (tears down all environments and services)
copilot app delete --name my-app --yes

# --- Environments ---
# Initialize a new environment (creates VPC, ECS cluster, ALB via CloudFormation)
copilot env init \
  --name production \
  --app my-app \
  --profile prod-profile \
  --region us-east-1

# Initialize environment using existing VPC and subnets
copilot env init \
  --name staging \
  --app my-app \
  --import-vpc-id vpc-abc123 \
  --import-public-subnets subnet-aaa,subnet-bbb \
  --import-private-subnets subnet-ccc,subnet-ddd

# Deploy (provision) the environment
copilot env deploy --name production --app my-app

# List environments
copilot env ls --app my-app

# Show environment details (VPC, subnets, services deployed)
copilot env show --name production --app my-app

# Delete an environment
copilot env delete --name staging --app my-app --yes

# --- Service initialization ---
# Scaffold a new Load Balanced Web Service
copilot svc init \
  --name api \
  --app my-app \
  --svc-type "Load Balanced Web Service" \
  --dockerfile ./Dockerfile \
  --port 8080

# Scaffold a Backend Service
copilot svc init \
  --name worker-backend \
  --app my-app \
  --svc-type "Backend Service" \
  --dockerfile ./Dockerfile

# Scaffold a Worker Service (auto-creates SQS queue)
copilot svc init \
  --name queue-processor \
  --app my-app \
  --svc-type "Worker Service" \
  --dockerfile ./Dockerfile

# Scaffold a Request-Driven Web Service (App Runner)
copilot svc init \
  --name frontend \
  --app my-app \
  --svc-type "Request-Driven Web Service" \
  --image public.ecr.aws/nginx/nginx:alpine \
  --port 80

# --- Deploy services ---
# Deploy a service to an environment (builds image, pushes to ECR, updates ECS)
copilot svc deploy \
  --name api \
  --app my-app \
  --env production

# Deploy with a specific image tag (skip build)
copilot svc deploy \
  --name api \
  --app my-app \
  --env production \
  --tag v1.2.3

# Deploy all services in the app to an environment
copilot svc deploy --app my-app --env production

# --- Service operations ---
# List services
copilot svc ls --app my-app

# Show service details (tasks, ALB URL, CloudFormation stack)
copilot svc show --name api --app my-app

# Tail service logs (ECS CloudWatch Logs)
copilot svc logs \
  --name api \
  --app my-app \
  --env production \
  --follow

# Tail logs for a specific task
copilot svc logs \
  --name api \
  --app my-app \
  --env production \
  --task-id <task-id> \
  --follow

# Open a shell in a running ECS task (uses ECS Exec)
copilot svc exec \
  --name api \
  --app my-app \
  --env production \
  --command /bin/sh

# Pause (stop) an ECS service
copilot svc pause --name api --app my-app --env production --yes

# Resume a paused service
copilot svc resume --name api --app my-app --env production

# Delete a service
copilot svc delete --name api --app my-app --yes

# --- Jobs ---
# Scaffold a Scheduled Job
copilot job init \
  --name nightly-report \
  --app my-app \
  --job-type "Scheduled Job" \
  --dockerfile ./jobs/report/Dockerfile \
  --schedule "cron(0 2 * * ? *)"

# Deploy a job
copilot job deploy \
  --name nightly-report \
  --app my-app \
  --env production

# Run a job immediately (one-off)
copilot job run \
  --name nightly-report \
  --app my-app \
  --env production

# List jobs
copilot job ls --app my-app

# Show job details
copilot job show --name nightly-report --app my-app

# Tail job logs
copilot job logs \
  --name nightly-report \
  --app my-app \
  --env production \
  --follow

# Delete a job
copilot job delete --name nightly-report --app my-app --yes

# --- Storage addons ---
# Add an S3 bucket addon to a service
copilot storage init \
  --storage-type S3 \
  --name my-bucket \
  --workload api

# Add a DynamoDB table addon
copilot storage init \
  --storage-type DynamoDB \
  --name my-table \
  --workload api \
  --partition-key id:S \
  --sort-key createdAt:N \
  --no-lsi

# Add an Aurora Serverless (PostgreSQL) addon
copilot storage init \
  --storage-type Aurora \
  --name my-db \
  --workload api \
  --db-name appdb \
  --engine PostgreSQL

# --- Pipelines ---
# Initialize a CI/CD pipeline
copilot pipeline init \
  --name my-pipeline \
  --url https://github.com/my-org/my-repo \
  --git-branch main \
  --environments test,staging,production

# Deploy (create/update) the pipeline in CodePipeline
copilot pipeline deploy --name my-pipeline --app my-app

# Show pipeline status and stages
copilot pipeline show --name my-pipeline --app my-app

# List pipelines
copilot pipeline ls --app my-app

# Delete a pipeline
copilot pipeline delete --name my-pipeline --app my-app --yes

# --- Diagnostics ---
# Show overall app status across environments
copilot app show --name my-app

# Check service health and task status
copilot svc status --name api --app my-app --env production

# Check job last run status
copilot job status --name nightly-report --app my-app --env production
```
