# AWS Server Migration — CLI Reference

For service concepts, see [server-migration-capabilities.md](server-migration-capabilities.md).

---

## aws mgn — Application Migration Service

### Source Servers

```bash
# List all source servers
aws mgn describe-source-servers \
  --filters '{"isArchived": false}'

# Get a specific source server
aws mgn describe-source-servers \
  --filters '{"sourceServerIDs": ["s-0123456789abcdef0"]}'

# Update a source server's name
aws mgn update-source-server \
  --source-server-id s-0123456789abcdef0 \
  --name "web-server-01"

# Disconnect a source server from replication (stops agent)
aws mgn disconnect-from-service \
  --source-server-id s-0123456789abcdef0

# Archive a source server (removes from active view)
aws mgn archive-application \
  --application-id app-0123456789abcdef0

# Mark source server as archived
aws mgn mark-as-archived \
  --source-server-id s-0123456789abcdef0

# Delete a source server (must be disconnected first)
aws mgn delete-source-server \
  --source-server-id s-0123456789abcdef0
```

### Replication Configurations

```bash
# Get replication configuration for a source server
aws mgn get-replication-configuration \
  --source-server-id s-0123456789abcdef0

# Update replication configuration (bandwidth throttle, staging area)
aws mgn update-replication-configuration \
  --source-server-id s-0123456789abcdef0 \
  --bandwidth-throttling 100 \
  --replication-server-instance-type t3.small \
  --staging-area-subnet-id subnet-0123456789abcdef0 \
  --staging-area-tags '{"Environment": "staging"}' \
  --use-dedicated-replication-server false \
  --data-plane-routing PRIVATE_IP

# Get replication configuration template (account-level defaults)
aws mgn get-replication-configuration-template \
  --replication-configuration-template-id rct-0123456789abcdef0

# Create a replication configuration template
aws mgn create-replication-configuration-template \
  --staging-area-subnet-id subnet-0123456789abcdef0 \
  --associate-default-security-group true \
  --replication-server-instance-type t3.small \
  --use-dedicated-replication-server false \
  --default-large-staging-disk-type gp3 \
  --bandwidth-throttling 0 \
  --data-plane-routing PRIVATE_IP \
  --create-public-ip false \
  --staging-area-tags '{"Name": "MGN-staging"}'

# Update a replication configuration template
aws mgn update-replication-configuration-template \
  --replication-configuration-template-id rct-0123456789abcdef0 \
  --bandwidth-throttling 200 \
  --replication-server-instance-type t3.medium

# Delete a replication configuration template
aws mgn delete-replication-configuration-template \
  --replication-configuration-template-id rct-0123456789abcdef0
```

### Launch Templates (Launch Configurations)

```bash
# Get launch configuration for a source server
aws mgn get-launch-configuration \
  --source-server-id s-0123456789abcdef0

# Update launch configuration (instance type, licensing, etc.)
aws mgn update-launch-configuration \
  --source-server-id s-0123456789abcdef0 \
  --name "web-server-01-launch-config" \
  --launch-disposition STOPPED \
  --target-instance-type-right-sizing-method BASIC \
  --copy-private-ip true \
  --copy-tags true \
  --licensing '{"osByol": false}' \
  --boot-mode USE_SOURCE \
  --enable-map-auto-tagging true

# Get launch configuration template (account-level defaults)
aws mgn get-launch-configuration-template \
  --launch-configuration-template-id lct-0123456789abcdef0

# Create a launch configuration template
aws mgn create-launch-configuration-template \
  --launch-disposition STOPPED \
  --target-instance-type-right-sizing-method BASIC \
  --copy-private-ip true \
  --copy-tags true \
  --licensing '{"osByol": false}' \
  --enable-map-auto-tagging true

# Update a launch configuration template
aws mgn update-launch-configuration-template \
  --launch-configuration-template-id lct-0123456789abcdef0 \
  --launch-disposition STARTED \
  --target-instance-type-right-sizing-method NONE

# Delete a launch configuration template
aws mgn delete-launch-configuration-template \
  --launch-configuration-template-id lct-0123456789abcdef0
```

### Test & Cutover Jobs

```bash
# Launch test instances for one or more source servers
aws mgn start-test \
  --source-server-ids '["s-0123456789abcdef0", "s-abcdef0123456789"]'

# Mark test as done (passed or failed)
aws mgn finish-test \
  --source-server-ids '["s-0123456789abcdef0"]'

# Launch cutover instances
aws mgn start-cutover \
  --source-server-ids '["s-0123456789abcdef0"]'

# Finalize cutover (marks servers as complete, triggers cleanup)
aws mgn finalize-cutover \
  --source-server-ids '["s-0123456789abcdef0"]'

# Revert cutover (go back to test state)
aws mgn revert-to-ready-for-cutover-for-recovery \
  --source-server-ids '["s-0123456789abcdef0"]'

# Terminate test instances (not source server)
aws mgn terminate-target-instances \
  --source-server-ids '["s-0123456789abcdef0"]'

# List jobs (test/cutover job history)
aws mgn describe-jobs \
  --filters '{"fromDate": "2024-01-01T00:00:00", "toDate": "2024-12-31T23:59:59"}'
```

### Waves

```bash
# List all waves
aws mgn describe-waves

# Create a wave
aws mgn create-wave \
  --name "Wave-1-WebTier" \
  --description "First cutover wave: web tier servers"

# Update a wave
aws mgn update-wave \
  --wave-id w-0123456789abcdef0 \
  --name "Wave-1-WebTier-Updated"

# Archive a wave
aws mgn archive-wave \
  --wave-id w-0123456789abcdef0

# Delete a wave
aws mgn delete-wave \
  --wave-id w-0123456789abcdef0
```

### Applications

```bash
# List all applications
aws mgn describe-applications

# Create an application
aws mgn create-application \
  --name "MyApp-3Tier" \
  --description "Three-tier web application" \
  --wave-id w-0123456789abcdef0

# Update an application
aws mgn update-application \
  --application-id app-0123456789abcdef0 \
  --name "MyApp-3Tier-Updated" \
  --wave-id w-abcdef0123456789

# Associate source servers with an application
aws mgn associate-source-servers \
  --application-id app-0123456789abcdef0 \
  --source-server-ids '["s-0123456789abcdef0"]'

# Disassociate source servers from an application
aws mgn disassociate-source-servers \
  --application-id app-0123456789abcdef0 \
  --source-server-ids '["s-0123456789abcdef0"]'

# Archive an application
aws mgn archive-application \
  --application-id app-0123456789abcdef0

# Delete an application
aws mgn delete-application \
  --application-id app-0123456789abcdef0
```

### Post-Migration Actions

```bash
# List post-migration actions for a source server
aws mgn list-source-server-actions \
  --source-server-id s-0123456789abcdef0

# Add a post-migration action (SSM document)
aws mgn put-source-server-action \
  --source-server-id s-0123456789abcdef0 \
  --action-id "install-cloudwatch-agent" \
  --action-name "Install CloudWatch Agent" \
  --document-identifier "AmazonCloudWatch-ManageAgent" \
  --document-version "\$DEFAULT" \
  --order 1001 \
  --active true \
  --parameters '{"action": [{"parameterName": "action", "parameterType": "STRING"}]}'

# Remove a post-migration action
aws mgn remove-source-server-action \
  --source-server-id s-0123456789abcdef0 \
  --action-id "install-cloudwatch-agent"

# List template-level post-migration actions
aws mgn list-template-actions \
  --launch-configuration-template-id lct-0123456789abcdef0
```

### MGN Account Settings

```bash
# Initialize MGN in the current account/region (first-time setup)
aws mgn initialize-service

# Get MGN account-level settings
aws mgn get-replication-configuration-template \
  --replication-configuration-template-id rct-0123456789abcdef0

# Tag a resource
aws mgn tag-resource \
  --resource-arn arn:aws:mgn:us-east-1:123456789012:source-server/s-0123456789abcdef0 \
  --tags '{"Project": "Migration2024"}'
```

---

## aws m2 — Mainframe Modernization

### Environments (Managed Runtime Clusters)

```bash
# List all M2 environments
aws m2 list-environments

# Get details of an environment
aws m2 get-environment \
  --environment-id env-0123456789abcdef0

# Create an environment (Micro Focus rehosting engine)
aws m2 create-environment \
  --name "prod-mf-env" \
  --engine-type microfocus \
  --engine-version "8.0.10" \
  --instance-type M2.m5.large \
  --subnet-ids '["subnet-0123456789abcdef0", "subnet-abcdef0123456789"]' \
  --security-group-ids '["sg-0123456789abcdef0"]' \
  --high-availability-config '{"desiredCapacity": 2}' \
  --publicly-accessible false

# Create an environment (Blu Age refactoring engine)
aws m2 create-environment \
  --name "prod-bluage-env" \
  --engine-type bluage \
  --engine-version "3.7.0" \
  --instance-type M2.m5.large \
  --subnet-ids '["subnet-0123456789abcdef0"]' \
  --security-group-ids '["sg-0123456789abcdef0"]'

# Update an environment (scale up instance type)
aws m2 update-environment \
  --environment-id env-0123456789abcdef0 \
  --instance-type M2.m5.xlarge \
  --desired-capacity 2

# Delete an environment
aws m2 delete-environment \
  --environment-id env-0123456789abcdef0
```

### Applications

```bash
# List all M2 applications
aws m2 list-applications

# Get details of an application
aws m2 get-application \
  --application-id app-0123456789abcdef0

# Create an M2 application
aws m2 create-application \
  --name "payroll-cobol-app" \
  --engine-type microfocus \
  --definition '{"s3Location": "s3://my-m2-bucket/apps/payroll/definition.yaml"}'

# Update application definition (new version)
aws m2 update-application \
  --application-id app-0123456789abcdef0 \
  --definition '{"s3Location": "s3://my-m2-bucket/apps/payroll/definition-v2.yaml"}'

# Delete an application
aws m2 delete-application \
  --application-id app-0123456789abcdef0
```

### Deployments

```bash
# List deployments for an application
aws m2 list-deployments \
  --application-id app-0123456789abcdef0

# Get a specific deployment
aws m2 get-deployment \
  --application-id app-0123456789abcdef0 \
  --deployment-id dep-0123456789abcdef0

# Create a deployment (deploy app version to an environment)
aws m2 create-deployment \
  --application-id app-0123456789abcdef0 \
  --application-version 1 \
  --environment-id env-0123456789abcdef0

# Start an application (after deployment)
aws m2 start-application \
  --application-id app-0123456789abcdef0

# Stop an application
aws m2 stop-application \
  --application-id app-0123456789abcdef0

# Delete an application from environment
aws m2 delete-application-from-environment \
  --application-id app-0123456789abcdef0 \
  --environment-id env-0123456789abcdef0
```

### Batch Jobs

```bash
# List batch job definitions for an application
aws m2 list-batch-job-definitions \
  --application-id app-0123456789abcdef0

# Start a batch job
aws m2 start-batch-job \
  --application-id app-0123456789abcdef0 \
  --batch-job-identifier '{"fileBatchJobIdentifier": {"fileName": "PAYROLL", "folderPath": "/jcl"}}' \
  --job-params '{"PARM1": "VALUE1"}'

# List batch job executions
aws m2 list-batch-job-executions \
  --application-id app-0123456789abcdef0

# Get batch job execution details
aws m2 get-batch-job-execution \
  --application-id app-0123456789abcdef0 \
  --execution-id exec-0123456789abcdef0

# Cancel a batch job execution
aws m2 cancel-batch-job-execution \
  --application-id app-0123456789abcdef0 \
  --execution-id exec-0123456789abcdef0
```

### Data Sets (VSAM / GDG)

```bash
# List data sets for an application
aws m2 list-data-sets \
  --application-id app-0123456789abcdef0

# Get a data set
aws m2 get-data-set-details \
  --application-id app-0123456789abcdef0 \
  --data-set-name "PAYROLL.MASTER"

# Import data sets from S3
aws m2 create-data-set-import-task \
  --application-id app-0123456789abcdef0 \
  --import-config '{"s3Location": "s3://my-m2-bucket/datasets/import-manifest.json"}'

# Get data set import task status
aws m2 get-data-set-import-task \
  --application-id app-0123456789abcdef0 \
  --task-id task-0123456789abcdef0
```

---

## AWS Transform (Console-Driven)

AWS Transform does not have a dedicated `aws transform` CLI service. Transformations are initiated and managed via the AWS Management Console or via integration with AWS CodeCatalyst. Artifacts (source uploads, assessment reports, converted code) are stored in Amazon S3 and can be accessed with standard `aws s3` commands:

```bash
# Upload source code for a Transform project
aws s3 sync ./my-dotnet-app/ s3://my-transform-bucket/projects/my-dotnet-app/

# Download assessment report
aws s3 cp s3://my-transform-bucket/reports/assessment-report.pdf ./

# Download converted code artifacts
aws s3 sync s3://my-transform-bucket/output/my-dotnet-app/ ./converted/
```
