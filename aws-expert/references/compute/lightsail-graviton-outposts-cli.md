# AWS Lightsail / Edge Compute — CLI Reference

For service concepts, see [lightsail-graviton-outposts-capabilities.md](lightsail-graviton-outposts-capabilities.md).

## AWS Graviton

See [aws-silicon-cli.md](aws-silicon-cli.md) for Graviton CLI commands.

---

## Amazon Lightsail

```bash
# --- Blueprints and Bundles (lookup before creating) ---
aws lightsail get-blueprints --output table
aws lightsail get-bundles --output table

# --- Instances ---
# Create a Linux instance (WordPress)
aws lightsail create-instances \
  --instance-names my-wordpress-site \
  --availability-zone us-east-1a \
  --blueprint-id wordpress \
  --bundle-id medium_3_0 \
  --key-pair-name my-lightsail-key

# Create a plain Amazon Linux 2023 instance
aws lightsail create-instances \
  --instance-names my-app-server \
  --availability-zone us-east-1a \
  --blueprint-id amazon_linux_2023 \
  --bundle-id nano_3_0

aws lightsail get-instances
aws lightsail get-instance --instance-name my-app-server
aws lightsail get-instance-state --instance-name my-app-server
aws lightsail start-instance --instance-name my-app-server
aws lightsail stop-instance --instance-name my-app-server
aws lightsail reboot-instance --instance-name my-app-server
aws lightsail delete-instance --instance-name my-app-server --force-delete-add-ons

# Get SSH access details
aws lightsail get-instance-access-details --instance-name my-app-server --protocol ssh

# --- Instance Snapshots ---
aws lightsail create-instance-snapshot \
  --instance-name my-app-server \
  --instance-snapshot-name my-app-server-backup-$(date +%Y%m%d)

aws lightsail get-instance-snapshots
aws lightsail get-instance-snapshot --instance-snapshot-name my-app-server-backup-20260101

# Restore instance from snapshot
aws lightsail create-instances-from-snapshot \
  --instance-names my-app-server-restored \
  --availability-zone us-east-1b \
  --bundle-id medium_3_0 \
  --instance-snapshot-name my-app-server-backup-20260101

aws lightsail delete-instance-snapshot --instance-snapshot-name my-app-server-backup-20260101

# --- Static IPs ---
aws lightsail allocate-static-ip --static-ip-name my-static-ip
aws lightsail attach-static-ip \
  --static-ip-name my-static-ip \
  --instance-name my-app-server
aws lightsail get-static-ips
aws lightsail detach-static-ip --static-ip-name my-static-ip
aws lightsail release-static-ip --static-ip-name my-static-ip

# --- Firewall (Port Rules) ---
aws lightsail open-instance-public-ports \
  --instance-name my-app-server \
  --port-info '{"fromPort":443,"toPort":443,"protocol":"tcp"}'

aws lightsail get-instance-port-states --instance-name my-app-server

aws lightsail close-instance-public-ports \
  --instance-name my-app-server \
  --port-info '{"fromPort":8080,"toPort":8080,"protocol":"tcp"}'

# --- Key Pairs ---
aws lightsail create-key-pair --key-pair-name my-lightsail-key
aws lightsail get-key-pairs
aws lightsail delete-key-pair --key-pair-name my-lightsail-key

# --- Load Balancers ---
aws lightsail create-load-balancer \
  --load-balancer-name my-lb \
  --instance-port 80 \
  --health-check-path /health

aws lightsail attach-instances-to-load-balancer \
  --load-balancer-name my-lb \
  --instance-names my-app-server

aws lightsail get-load-balancers
aws lightsail get-load-balancer --load-balancer-name my-lb
aws lightsail detach-instances-from-load-balancer \
  --load-balancer-name my-lb \
  --instance-names my-app-server
aws lightsail delete-load-balancer --load-balancer-name my-lb

# --- Managed Databases ---
aws lightsail create-relational-database \
  --relational-database-name my-db \
  --availability-zone us-east-1a \
  --relational-database-blueprint-id mysql_8_0 \
  --relational-database-bundle-id micro_2_0 \
  --master-database-name mydb \
  --master-username admin

aws lightsail get-relational-databases
aws lightsail stop-relational-database --relational-database-name my-db
aws lightsail start-relational-database --relational-database-name my-db
aws lightsail delete-relational-database --relational-database-name my-db

# --- Containers ---
aws lightsail get-container-service-powers
aws lightsail create-container-service \
  --service-name my-container-service \
  --power nano \
  --scale 1

aws lightsail create-container-service-deployment \
  --service-name my-container-service \
  --containers '{
    "app": {
      "image": "nginx:latest",
      "ports": {"80": "HTTP"},
      "environment": {"ENV": "prod"}
    }
  }' \
  --public-endpoint '{"containerName":"app","containerPort":80,"healthCheck":{"path":"/"}}'

aws lightsail get-container-services
aws lightsail get-container-service-deployments --service-name my-container-service
aws lightsail delete-container-service --service-name my-container-service

# --- Storage Buckets ---
aws lightsail create-bucket --bucket-name my-lightsail-bucket --bundle-id small_1_0
aws lightsail get-buckets
aws lightsail delete-bucket --bucket-name my-lightsail-bucket
```

---

## Savings Plans

```bash
# --- Browse Savings Plans Offerings ---
# List available Compute Savings Plans
aws savingsplans describe-savings-plans-offerings \
  --plan-types COMPUTE_SP \
  --payment-options ALL_UPFRONT NO_UPFRONT PARTIAL_UPFRONT \
  --durations 31536000 94608000

# List EC2 Instance Savings Plans
aws savingsplans describe-savings-plans-offerings \
  --plan-types EC2_INSTANCE_SP \
  --filters attribute=instanceFamily,values=m7g attribute=region,values=us-east-1

# List rates for a specific offering
aws savingsplans describe-savings-plans-offering-rates \
  --savings-plan-offering-ids abc12345-6789-def0-1234-abcdef012345

# --- Purchase Savings Plans ---
aws savingsplans create-savings-plan \
  --savings-plan-offering-id abc12345-6789-def0-1234-abcdef012345 \
  --commitment 1.50 \
  --tags '{"Owner":"platform-team","Project":"cost-optimization"}'

# --- Describe Purchased Savings Plans ---
aws savingsplans describe-savings-plans
aws savingsplans describe-savings-plans \
  --states ACTIVE \
  --filters attribute=savingsPlanType,values=COMPUTE_SP

# Get rates for a purchased plan (shows discount rates by service/usage type)
aws savingsplans describe-savings-plan-rates \
  --savings-plan-id sp-0abc123def456789

# --- Manage Savings Plans ---
aws savingsplans return-savings-plan --savings-plan-id sp-0abc123def456789  # within return window only
aws savingsplans delete-queued-savings-plan --savings-plan-id sp-0abc123def456789

# Tagging
aws savingsplans tag-resource \
  --resource-arn arn:aws:savingsplans::123456789012:savingsplan/sp-0abc123def456789 \
  --tags '{"CostCenter":"engineering"}'
aws savingsplans list-tags-for-resource \
  --resource-arn arn:aws:savingsplans::123456789012:savingsplan/sp-0abc123def456789
```

---

## Compute Optimizer

```bash
# --- EC2 Instance Recommendations ---
aws compute-optimizer get-ec2-instance-recommendations \
  --account-ids 123456789012

# Filter by finding (OVER_PROVISIONED, UNDER_PROVISIONED, OPTIMIZED, NOT_OPTIMIZED)
aws compute-optimizer get-ec2-instance-recommendations \
  --filters Name=finding,Values=OVER_PROVISIONED

# Get projected metrics for a recommended instance type
aws compute-optimizer get-ec2-recommendation-projected-metrics \
  --instance-arn arn:aws:ec2:us-east-1:123456789012:instance/i-0abc123def456789 \
  --stat Maximum \
  --period 3600 \
  --start-time "2026-01-01T00:00:00Z" \
  --end-time "2026-02-01T00:00:00Z" \
  --recommendation-preferences '{"cpuVendorArchitectures":["AWS_ARM64"]}'

# --- Lambda Function Recommendations ---
aws compute-optimizer get-lambda-function-recommendations
aws compute-optimizer get-lambda-function-recommendations \
  --filters Name=finding,Values=OVER_PROVISIONED

# --- ECS Service Recommendations ---
aws compute-optimizer get-ecs-service-recommendations
aws compute-optimizer get-ecs-service-recommendation-projected-metrics \
  --service-arn arn:aws:ecs:us-east-1:123456789012:service/my-cluster/my-service \
  --stat Maximum \
  --period 3600 \
  --start-time "2026-01-01T00:00:00Z" \
  --end-time "2026-02-01T00:00:00Z"

# --- Auto Scaling Group Recommendations ---
aws compute-optimizer get-auto-scaling-group-recommendations
aws compute-optimizer get-auto-scaling-group-recommendations \
  --filters Name=finding,Values=OVER_PROVISIONED
```
