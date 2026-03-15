# Migration Hub & Discovery — CLI Reference

For service concepts, see [migration-hub-capabilities.md](migration-hub-capabilities.md).

---

## aws discovery — Application Discovery Service

### Continuous Export

```bash
# Start continuous export to S3 (streams data in Parquet format)
aws discovery start-continuous-export

# Stop continuous export
aws discovery stop-continuous-export \
  --export-id export-0123456789abcdef0

# List continuous exports and their status
aws discovery describe-continuous-exports
```

### Agents & Connectors

```bash
# List all registered agents and connectors
aws discovery describe-agents

# Filter to show only active agents
aws discovery describe-agents \
  --filters '[{"name": "agentHealth", "values": ["HEALTHY"], "condition": "EQUALS"}]'

# List agents with pagination
aws discovery describe-agents \
  --max-results 100

# Start data collection on specific agents
aws discovery start-data-collection-by-agent-ids \
  --agent-ids '["agent-0123456789abcdef0", "agent-abcdef0123456789"]'

# Stop data collection on specific agents
aws discovery stop-data-collection-by-agent-ids \
  --agent-ids '["agent-0123456789abcdef0"]'
```

### Configurations (Servers, Processes, Connections)

```bash
# List server configurations
aws discovery list-configurations \
  --configuration-type SERVER

# List configurations with a filter (e.g., by OS)
aws discovery list-configurations \
  --configuration-type SERVER \
  --filters '[{"name": "server.osName", "values": ["Linux"], "condition": "CONTAINS"}]'

# List process configurations
aws discovery list-configurations \
  --configuration-type PROCESS

# List network connection configurations
aws discovery list-configurations \
  --configuration-type CONNECTION

# Get details for specific configurations
aws discovery describe-configurations \
  --configuration-ids '["d-server-0123456789abcdef0", "d-server-abcdef0123456789"]'
```

### On-Demand Export Tasks

```bash
# Start an export task (exports snapshot to S3 as CSV)
aws discovery start-export-task

# Start an export with time range filter
aws discovery start-export-task \
  --export-data-format '["CSV"]' \
  --filters '[{"name": "agentIds", "values": ["agent-0123456789abcdef0"], "condition": "EQUALS"}]' \
  --start-time 2024-01-01T00:00:00 \
  --end-time 2024-12-31T23:59:59

# List export tasks and check status
aws discovery describe-export-tasks

# Get status of a specific export task
aws discovery describe-export-tasks \
  --export-ids '["export-0123456789abcdef0"]'
```

### Applications

```bash
# Create an application grouping
aws discovery create-application \
  --name "MyApp-3Tier" \
  --description "Three-tier web application"

# List all applications
aws discovery describe-applications

# Associate discovered servers with an application
aws discovery associate-configuration-items-to-application \
  --application-configuration-id d-APPLICATION-0123456789abcdef0 \
  --configuration-ids '["d-server-0123456789abcdef0", "d-server-abcdef0123456789"]'

# Disassociate servers from an application
aws discovery disassociate-configuration-items-from-application \
  --application-configuration-id d-APPLICATION-0123456789abcdef0 \
  --configuration-ids '["d-server-0123456789abcdef0"]'

# Update an application
aws discovery update-application \
  --configuration-id d-APPLICATION-0123456789abcdef0 \
  --name "MyApp-3Tier-Updated" \
  --description "Updated description"

# Delete an application
aws discovery delete-applications \
  --configuration-ids '["d-APPLICATION-0123456789abcdef0"]'
```

### Bulk Import

```bash
# Start a bulk import task from a CSV file in S3
aws discovery start-import-task \
  --name "OnPremInventoryImport-2024" \
  --import-url s3://my-discovery-bucket/imports/server-inventory.csv

# List import tasks
aws discovery describe-import-tasks

# Describe a specific import task
aws discovery describe-import-tasks \
  --filters '[{"name": "taskId", "values": ["import-task-0123456789abcdef0"], "condition": "EQUALS"}]'

# Delete a failed import task
aws discovery delete-import-tasks \
  --import-task-ids '["import-task-0123456789abcdef0"]'
```

---

## aws migrationhub — Migration Hub Tracking

### Home Region (aws migrationhub-config)

```bash
# Set the Migration Hub home region (one-time, per account)
aws migrationhub-config create-home-region-control \
  --home-region us-east-1 \
  --target '{"Type": "ACCOUNT"}'

# Get the current home region setting
aws migrationhub-config describe-home-region-controls

# Get home region (simplified)
aws migrationhub-config get-home-region
```

### Progress Update Streams

```bash
# Create a progress update stream (identifies the migration tool)
aws migrationhub create-progress-update-stream \
  --progress-update-stream-name "MyMigrationTool"

# List all progress update streams
aws migrationhub list-progress-update-streams

# Delete a progress update stream
aws migrationhub delete-progress-update-stream \
  --progress-update-stream-name "MyMigrationTool"
```

### Migration Tasks

```bash
# List all migration tasks across all streams
aws migrationhub list-migration-tasks

# List migration tasks for a specific stream
aws migrationhub list-migration-tasks \
  --resource-name "arn:aws:migrationhub:us-east-1:123456789012:progressupdatestream/MyMigrationTool"

# Describe a specific migration task
aws migrationhub describe-migration-task \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost"

# Import migration task (registers a task in Migration Hub)
aws migrationhub import-migration-task \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost"

# Notify task state change
aws migrationhub notify-migration-task-state \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost" \
  --task '{"Status": "IN_PROGRESS", "StatusDetail": "Replication in progress", "ProgressPercent": 45}' \
  --update-date-time 2024-06-01T12:00:00

# Put resource attributes (link migrated resource to Migration Hub)
aws migrationhub put-resource-attributes \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost" \
  --resource-attribute-list '[{"Type": "IPV4_ADDRESS", "Value": "10.0.1.100"}, {"Type": "FQDN", "Value": "server-01.corp.example.com"}]'

# Associate a created AWS resource (e.g., EC2) with the migration task
aws migrationhub associate-created-artifact \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost" \
  --created-artifact '{"Name": "arn:aws:ec2:us-east-1:123456789012:instance/i-0123456789abcdef0", "Description": "Migrated EC2 instance"}'

# Disassociate a created artifact
aws migrationhub disassociate-created-artifact \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost" \
  --created-artifact-name "arn:aws:ec2:us-east-1:123456789012:instance/i-0123456789abcdef0"

# List created artifacts for a migration task
aws migrationhub list-created-artifacts \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost"
```

### Applications

```bash
# List all applications in Migration Hub
aws migrationhub list-applications

# Describe application state
aws migrationhub describe-application-state \
  --application-id app-0123456789abcdef0

# Notify application state change
aws migrationhub notify-application-state \
  --application-id app-0123456789abcdef0 \
  --status IN_PROGRESS

# Associate a discovered server with a Migration Hub application
aws migrationhub associate-discovered-resource \
  --progress-update-stream "MyMigrationTool" \
  --migration-task-name "server-01-rehost" \
  --discovered-resource '{"ConfigurationId": "d-server-0123456789abcdef0", "Description": "On-prem web server"}'
```

---

## aws migrationhuborchestrator — Migration Hub Orchestrator

### Workflows

```bash
# List all workflows
aws migrationhuborchestrator list-workflows

# Get a specific workflow
aws migrationhuborchestrator get-workflow \
  --id wf-0123456789abcdef0

# Create a workflow from a template
aws migrationhuborchestrator create-workflow \
  --name "SAP-Migration-2024" \
  --description "SAP HANA migration to AWS" \
  --template-id "MGN-SQL-SERVER-TO-RDS" \
  --application-configure-id app-0123456789abcdef0 \
  --input-parameters '{"SourceServerID": {"integerValue": 0}, "TargetAccountID": {"stringValue": "123456789012"}}'

# Update a workflow
aws migrationhuborchestrator update-workflow \
  --id wf-0123456789abcdef0 \
  --name "SAP-Migration-2024-Updated" \
  --description "Updated description" \
  --input-parameters '{}'

# Start a workflow execution
aws migrationhuborchestrator start-workflow \
  --id wf-0123456789abcdef0

# Stop (pause) a running workflow
aws migrationhuborchestrator stop-workflow \
  --id wf-0123456789abcdef0

# Retry a failed workflow
aws migrationhuborchestrator retry-workflow-step \
  --workflow-id wf-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0 \
  --id step-0123456789abcdef0

# Delete a workflow
aws migrationhuborchestrator delete-workflow \
  --id wf-0123456789abcdef0
```

### Workflow Templates

```bash
# List available workflow templates
aws migrationhuborchestrator list-templates

# Get details of a specific template
aws migrationhuborchestrator get-template \
  --id "MGN-SQL-SERVER-TO-RDS"

# List steps in a template
aws migrationhuborchestrator list-template-steps \
  --template-id "MGN-SQL-SERVER-TO-RDS" \
  --step-group-id sg-0123456789abcdef0

# Get a specific template step
aws migrationhuborchestrator get-template-step \
  --template-id "MGN-SQL-SERVER-TO-RDS" \
  --step-group-id sg-0123456789abcdef0 \
  --id step-0123456789abcdef0

# List template step groups
aws migrationhuborchestrator list-template-step-groups \
  --template-id "MGN-SQL-SERVER-TO-RDS"
```

### Workflow Step Groups

```bash
# List step groups in a workflow
aws migrationhuborchestrator list-workflow-step-groups \
  --workflow-id wf-0123456789abcdef0

# Get a specific step group
aws migrationhuborchestrator get-workflow-step-group \
  --workflow-id wf-0123456789abcdef0 \
  --id sg-0123456789abcdef0

# Create a custom step group
aws migrationhuborchestrator create-workflow-step-group \
  --workflow-id wf-0123456789abcdef0 \
  --name "Post-Migration Validation" \
  --description "Steps to validate the migrated environment"

# Update a step group
aws migrationhuborchestrator update-workflow-step-group \
  --workflow-id wf-0123456789abcdef0 \
  --id sg-0123456789abcdef0 \
  --name "Post-Migration Validation Updated"

# Delete a step group
aws migrationhuborchestrator delete-workflow-step-group \
  --workflow-id wf-0123456789abcdef0 \
  --id sg-0123456789abcdef0
```

### Workflow Steps

```bash
# List steps in a step group
aws migrationhuborchestrator list-workflow-steps \
  --workflow-id wf-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0

# Get a specific step
aws migrationhuborchestrator get-workflow-step \
  --workflow-id wf-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0 \
  --id step-0123456789abcdef0

# Create a custom workflow step (automated)
aws migrationhuborchestrator create-workflow-step \
  --name "Validate Application" \
  --step-group-id sg-0123456789abcdef0 \
  --workflow-id wf-0123456789abcdef0 \
  --step-action-type AUTOMATED \
  --description "Run automated validation script via SSM" \
  --workflow-step-automation-configuration '{"scriptLocationS3Bucket": "my-orchestrator-bucket", "scriptLocationS3Key": {"linux": "scripts/validate.sh"}, "command": {"linux": "bash validate.sh"}, "runEnvironment": "AWS", "targetType": "SINGLE"}'

# Create a manual workflow step
aws migrationhuborchestrator create-workflow-step \
  --name "Sign-off Validation" \
  --step-group-id sg-0123456789abcdef0 \
  --workflow-id wf-0123456789abcdef0 \
  --step-action-type MANUAL \
  --description "Stakeholder approval required before cutover"

# Update a workflow step
aws migrationhuborchestrator update-workflow-step \
  --id step-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0 \
  --workflow-id wf-0123456789abcdef0 \
  --name "Validate Application Updated" \
  --status COMPLETE

# Delete a workflow step
aws migrationhuborchestrator delete-workflow-step \
  --id step-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0 \
  --workflow-id wf-0123456789abcdef0
```

### Plugins

```bash
# List registered plugins (MGN plugin, AWS CLI plugin)
aws migrationhuborchestrator list-plugins

# Get details of a specific plugin
aws migrationhuborchestrator get-workflow-step \
  --workflow-id wf-0123456789abcdef0 \
  --step-group-id sg-0123456789abcdef0 \
  --id step-0123456789abcdef0
```

---

## aws migration-hub-refactor-spaces — Refactor Spaces

### Environments

```bash
# List all Refactor Spaces environments
aws migration-hub-refactor-spaces list-environments

# Get a specific environment
aws migration-hub-refactor-spaces get-environment \
  --environment-identifier env-0123456789abcdef0

# Create an environment
aws migration-hub-refactor-spaces create-environment \
  --name "MyApp-Refactor-Env" \
  --description "Refactor Spaces environment for MyApp strangler-fig migration" \
  --network-fabric-type TRANSIT_GATEWAY

# Tag an environment
aws migration-hub-refactor-spaces tag-resource \
  --resource-arn arn:aws:refactor-spaces:us-east-1:123456789012:environment/env-0123456789abcdef0 \
  --tags '{"Project": "Modernization2024"}'

# Delete an environment
aws migration-hub-refactor-spaces delete-environment \
  --environment-identifier env-0123456789abcdef0
```

### Applications

```bash
# List applications in an environment
aws migration-hub-refactor-spaces list-applications \
  --environment-identifier env-0123456789abcdef0

# Get a specific application
aws migration-hub-refactor-spaces get-application \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0

# Create an application (provisions API Gateway and NLB)
aws migration-hub-refactor-spaces create-application \
  --environment-identifier env-0123456789abcdef0 \
  --name "MyApp" \
  --proxy-type API_GATEWAY \
  --vpc-id vpc-0123456789abcdef0 \
  --api-gateway-proxy '{"endpointType": "REGIONAL", "stageName": "prod"}'

# Delete an application
aws migration-hub-refactor-spaces delete-application \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0
```

### Services

```bash
# List services in an application
aws migration-hub-refactor-spaces list-services \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0

# Get a specific service
aws migration-hub-refactor-spaces get-service \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --service-identifier svc-0123456789abcdef0

# Create a service pointing to a URL (existing monolith)
aws migration-hub-refactor-spaces create-service \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --name "monolith" \
  --endpoint-type URL \
  --url-endpoint '{"url": "http://10.0.1.100:8080", "healthUrl": "http://10.0.1.100:8080/health"}' \
  --vpc-id vpc-0123456789abcdef0

# Create a service pointing to a Lambda function (new microservice)
aws migration-hub-refactor-spaces create-service \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --name "orders-microservice" \
  --endpoint-type LAMBDA \
  --lambda-endpoint '{"arn": "arn:aws:lambda:us-east-1:123456789012:function:orders-handler"}'

# Delete a service
aws migration-hub-refactor-spaces delete-service \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --service-identifier svc-0123456789abcdef0
```

### Routes

```bash
# List routes for an application
aws migration-hub-refactor-spaces list-routes \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0

# Get a specific route
aws migration-hub-refactor-spaces get-route \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --route-identifier route-0123456789abcdef0

# Create the default route (catch-all; points to monolith)
aws migration-hub-refactor-spaces create-route \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --service-identifier svc-0123456789abcdef0 \
  --route-type DEFAULT

# Create a URI path route (points /api/orders to microservice)
aws migration-hub-refactor-spaces create-route \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --service-identifier svc-abcdef0123456789 \
  --route-type URI_PATH \
  --uri-path-route '{"sourcePath": "/api/orders", "activationState": "ACTIVE", "includeChildPaths": true, "methods": ["GET", "POST", "PUT", "DELETE"]}'

# Update a route (activate or deactivate)
aws migration-hub-refactor-spaces update-route \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --route-identifier route-0123456789abcdef0 \
  --activation-state INACTIVE

# Delete a route
aws migration-hub-refactor-spaces delete-route \
  --environment-identifier env-0123456789abcdef0 \
  --application-identifier app-0123456789abcdef0 \
  --route-identifier route-0123456789abcdef0
```

### VPC Links (Environment VPC Associations)

```bash
# List VPCs associated with an environment
aws migration-hub-refactor-spaces list-environment-vpcs \
  --environment-identifier env-0123456789abcdef0
```

---

## aws migrationhubstrategy — Migration Hub Strategy Recommendations

### Assessment

```bash
# Start a portfolio assessment (initiates data collection analysis)
aws migrationhubstrategy start-assessment

# Get assessment status and results
aws migrationhubstrategy get-assessment \
  --id assessment-0123456789abcdef0

# Get the portfolio summary (aggregate strategy distribution)
aws migrationhubstrategy get-portfolio-summary
```

### Portfolio Preferences

```bash
# Get current portfolio preferences (prioritization, licensing, etc.)
aws migrationhubstrategy get-portfolio-preferences

# Set portfolio preferences
aws migrationhubstrategy put-portfolio-preferences \
  --prioritize-business-goals '{"businessGoals": {"speedOfMigration": 3, "reduceOperationalOverheadWithManagedServices": 2, "modernizeInfrastructureWithCloudNativeTechnologies": 2, "licenseCostReduction": 3}}' \
  --application-preferences '{"awsManagedResources": {"targetDestination": ["AWS Elastic BeanStalk"]}}' \
  --database-preferences '{"databaseManagementPreference": "AWS-managed", "heterogeneousMigration": {"targetDatabaseEngineList": ["Amazon Aurora", "Amazon RDS"]}}'
```

### Servers

```bash
# List all servers in the portfolio
aws migrationhubstrategy list-servers

# List servers with filters
aws migrationhubstrategy list-servers \
  --filter-value "WindowsServer" \
  --sort '{"name": "name", "order": "ASC"}'

# Get details and recommendations for a specific server
aws migrationhubstrategy get-server-details \
  --server-id server-0123456789abcdef0

# Get server strategies (recommended migration strategies for a server)
aws migrationhubstrategy list-server-strategies \
  --server-id server-0123456789abcdef0
```

### Application Components

```bash
# List all application components
aws migrationhubstrategy list-application-components

# List with filters
aws migrationhubstrategy list-application-components \
  --application-component-criteria "APP_NAME" \
  --filter-value "payroll"

# Get details and recommendations for an application component
aws migrationhubstrategy get-application-component-details \
  --application-component-id comp-0123456789abcdef0

# Get strategies for an application component
aws migrationhubstrategy list-application-component-strategies \
  --application-component-id comp-0123456789abcdef0

# Update the strategy recommendation for an application component
aws migrationhubstrategy update-application-component-config \
  --application-component-id comp-0123456789abcdef0 \
  --inclusion-status includeInAssessment \
  --strategy-option '{"strategy": "Replatform", "toolName": "App2Container", "targetDestination": "AWS Elastic Container Service (ECS)", "isPreferred": true}'
```

### Import File Tasks (Bulk Data Import)

```bash
# Start an import file task (upload server data from a file)
aws migrationhubstrategy start-import-file-task \
  --name "OnPremInventory-2024" \
  --s3-bucket my-strategy-bucket \
  --s3-key imports/server-inventory.xlsx

# List all import file tasks
aws migrationhubstrategy list-import-file-task

# Get status of a specific import task
aws migrationhubstrategy get-import-file-task \
  --id import-task-0123456789abcdef0
```

### Report Generation

```bash
# Start generating a recommendation report
aws migrationhubstrategy start-recommendation-report-generation \
  --output-format Excel \
  --group-id-filter '[{"name": "ExternalId", "value": "my-portfolio"}]'

# Get the status and download URL of a generated report
aws migrationhubstrategy get-recommendation-report-details \
  --id report-0123456789abcdef0

# List all generated reports
aws migrationhubstrategy list-recommendation-report-generation-tasks
```

### Collectors

```bash
# List registered collectors (on-premises data collection agents)
aws migrationhubstrategy list-collectors

# Get details of a specific collector
aws migrationhubstrategy get-server-details \
  --server-id server-0123456789abcdef0
```
