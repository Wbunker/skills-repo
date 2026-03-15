# App Deployment & Low-Code Tools — CLI Reference

For service concepts, see [app-deployment-tools-capabilities.md](app-deployment-tools-capabilities.md).

---

## AWS Proton

```bash
# --- Environment Templates ---
# Create an environment template
aws proton create-environment-template \
  --name my-env-template \
  --display-name "My VPC + ECS Environment" \
  --description "Standard VPC and ECS cluster for microservices"

# Create an environment template version (upload bundle from S3)
aws proton create-environment-template-version \
  --template-name my-env-template \
  --source s3='{bucket=my-proton-bundles,key=my-env-template/v1.0.tar.gz}' \
  --description "Initial version"

# Publish an environment template version (make it available for deployment)
aws proton update-environment-template-version \
  --template-name my-env-template \
  --major-version 1 \
  --minor-version 0 \
  --status PUBLISHED

# List environment templates
aws proton list-environment-templates

# Get environment template details
aws proton get-environment-template --name my-env-template

# List versions of an environment template
aws proton list-environment-template-versions \
  --template-name my-env-template

# Get a specific environment template version
aws proton get-environment-template-version \
  --template-name my-env-template \
  --major-version 1 \
  --minor-version 0

# Delete an environment template version
aws proton delete-environment-template-version \
  --template-name my-env-template \
  --major-version 1 \
  --minor-version 0

# Delete an environment template (all versions must be deleted first)
aws proton delete-environment-template --name my-env-template

# --- Service Templates ---
# Create a service template
aws proton create-service-template \
  --name my-svc-template \
  --display-name "Fargate Service" \
  --description "ECS Fargate service with ALB and CodePipeline" \
  --pipeline-provisioning CUSTOMER_MANAGED  # or omit for Proton-managed pipeline

# Create a service template version
aws proton create-service-template-version \
  --template-name my-svc-template \
  --source s3='{bucket=my-proton-bundles,key=my-svc-template/v1.0.tar.gz}' \
  --compatible-environment-templates '[{"templateName":"my-env-template","majorVersion":"1"}]' \
  --description "Initial version"

# Publish a service template version
aws proton update-service-template-version \
  --template-name my-svc-template \
  --major-version 1 \
  --minor-version 0 \
  --status PUBLISHED

# List service templates
aws proton list-service-templates

# Get service template details
aws proton get-service-template --name my-svc-template

# List versions of a service template
aws proton list-service-template-versions \
  --template-name my-svc-template

# --- Environments ---
# Create an environment instance
aws proton create-environment \
  --name prod \
  --template-name my-env-template \
  --template-major-version 1 \
  --template-minor-version 0 \
  --spec file://prod-env-spec.yaml \
  --proton-service-role-arn arn:aws:iam::123456789012:role/ProtonServiceRole

# Get environment details and deployment status
aws proton get-environment --name prod

# List all environments
aws proton list-environments

# Update an environment (e.g., upgrade template version)
aws proton update-environment \
  --name prod \
  --template-minor-version 1 \
  --deployment-type MINOR_VERSION \
  --spec file://prod-env-spec.yaml

# Delete an environment (all services must be deleted first)
aws proton delete-environment --name prod

# --- Services ---
# Create a service (deploys service instances into one or more environments)
aws proton create-service \
  --name my-api \
  --template-name my-svc-template \
  --template-major-version 1 \
  --spec file://my-api-spec.yaml \
  --repository-connection-arn arn:aws:codestar-connections:us-east-1:123456789012:connection/abc \
  --repository-id myorg/myrepo \
  --branch-name main

# Get service details and deployment status
aws proton get-service --name my-api

# List all services
aws proton list-services

# Update a service (update spec or upgrade template version)
aws proton update-service \
  --name my-api \
  --spec file://my-api-updated-spec.yaml

# List service instances for a service
aws proton list-service-instances \
  --service-name my-api

# Get a service instance
aws proton get-service-instance \
  --service-name my-api \
  --name prod

# Update a service instance (e.g., promote to new minor version)
aws proton update-service-instance \
  --service-name my-api \
  --name prod \
  --deployment-type MINOR_VERSION \
  --template-minor-version 1 \
  --spec file://prod-instance-spec.yaml

# Delete a service
aws proton delete-service --name my-api

# --- Components ---
# Create a component (reusable infrastructure attached to an environment or service instance)
aws proton create-component \
  --name my-s3-bucket \
  --environment-name prod \
  --template-file file://s3-component-template.yaml \
  --manifest file://s3-component-manifest.yaml \
  --spec file://s3-component-spec.yaml

# Get component details
aws proton get-component --name my-s3-bucket

# List components
aws proton list-components

# Update a component
aws proton update-component \
  --name my-s3-bucket \
  --deployment-type CURRENT_VERSION \
  --spec file://s3-component-spec-updated.yaml

# Delete a component
aws proton delete-component --name my-s3-bucket

# --- Git Sync (Sync templates from a repository) ---
# Create a repository link (prerequisite for Git sync)
aws proton create-repository \
  --name myorg/myrepo \
  --provider GITHUB \
  --connection-arn arn:aws:codestar-connections:us-east-1:123456789012:connection/abc \
  --encryption-key alias/aws/proton

# Create a template sync configuration
aws proton create-template-sync-config \
  --template-name my-env-template \
  --template-type ENVIRONMENT \
  --repository-name myorg/myrepo \
  --repository-provider GITHUB \
  --branch main \
  --subdirectory templates/my-env-template

# Get sync configuration
aws proton get-template-sync-config \
  --template-name my-env-template \
  --template-type ENVIRONMENT

# List repositories linked to Proton
aws proton list-repositories
```

---

## AWS Launch Wizard

```bash
# --- Workloads ---
# List available workloads
aws launchwizard list-workloads

# Get workload details
aws launchwizard get-workload \
  --workload-name SQLServerAlwaysOn

# List deployment patterns for a workload
aws launchwizard list-workload-deployment-patterns \
  --workload-name SQLServerAlwaysOn

# Get a specific deployment pattern (includes parameter schema)
aws launchwizard get-workload-deployment-pattern \
  --workload-name SQLServerAlwaysOn \
  --deployment-pattern-name ActiveDirectoryManagedAD

# --- Deployments ---
# Create a deployment
aws launchwizard create-deployment \
  --workload-name SQLServerAlwaysOn \
  --deployment-pattern-name ActiveDirectoryManagedAD \
  --name prod-sql-ag \
  --specifications file://sql-ag-specs.json

# Get deployment details and status
aws launchwizard get-deployment \
  --deployment-id dep-abc1234567890

# List all deployments
aws launchwizard list-deployments

# List deployments for a specific workload
aws launchwizard list-deployments \
  --filters '[{"name":"WORKLOAD_NAME","values":["SQLServerAlwaysOn"]}]'

# List deployment events (provisioning timeline and error details)
aws launchwizard list-deployment-events \
  --deployment-id dep-abc1234567890

# Delete a deployment (terminates CloudFormation stacks and all provisioned resources)
aws launchwizard delete-deployment \
  --deployment-id dep-abc1234567890

# --- Tags ---
# Tag a deployment
aws launchwizard tag-resource \
  --resource-arn arn:aws:launchwizard:us-east-1:123456789012:deployment/dep-abc1234567890 \
  --tags Env=prod,Team=platform

# List tags for a deployment
aws launchwizard list-tags-for-resource \
  --resource-arn arn:aws:launchwizard:us-east-1:123456789012:deployment/dep-abc1234567890
```

---

## AWS App Studio

> **Note**: App Studio is primarily a console-based, browser-driven low-code builder. Application creation and editing are performed through the App Studio web UI. The AWS CLI surface for App Studio is limited.

```bash
# List App Studio apps (if CLI is available in your region/version)
aws appstudio list-apps

# Get app details
aws appstudio get-app \
  --app-id <app-id>

# List data sources configured for an app
aws appstudio list-data-sources \
  --app-id <app-id>

# Publish an app (make the latest version available to users)
aws appstudio publish-app \
  --app-id <app-id>
```

> For most App Studio operations — creating apps, building pages, configuring components, authoring automations — use the App Studio console at `https://studio.us-east-1.amazonaws.com/` (region-specific URL).

---

## AWS re:Post Private

> **Note**: re:Post Private space creation and member management are the primary CLI-accessible operations. Day-to-day use (asking questions, posting answers, moderating content) is console/web-based.

```bash
# --- Spaces ---
# Create a private re:Post space
aws repostspace create-space \
  --name my-company-repost \
  --subdomain my-company \
  --tier BASIC    # BASIC or STANDARD
  --description "Internal developer Q&A community"

# Get space details
aws repostspace get-space \
  --space-id spc-abc1234567890

# List all spaces in the account
aws repostspace list-spaces

# Update a space
aws repostspace update-space \
  --space-id spc-abc1234567890 \
  --description "Updated description" \
  --role EXPERT   # default role for new members

# Delete a space
aws repostspace delete-space \
  --space-id spc-abc1234567890

# --- Member / Role Management ---
# Register an admin for the space (IAM Identity Center user)
aws repostspace register-admin \
  --space-id spc-abc1234567890 \
  --admin-id <iam-identity-center-user-id>

# Deregister an admin
aws repostspace deregister-admin \
  --space-id spc-abc1234567890 \
  --admin-id <iam-identity-center-user-id>

# Create batch role assignments (add multiple members with a role at once)
aws repostspace create-batch-role \
  --space-id spc-abc1234567890 \
  --accessor-ids <user-id-1> <user-id-2> \
  --role EXPERT   # EXPERT | MODERATOR | SUPPORTREQUESTOR

# Delete batch role assignments (remove role from multiple members)
aws repostspace delete-batch-role \
  --space-id spc-abc1234567890 \
  --accessor-ids <user-id-1> <user-id-2> \
  --role EXPERT

# List members of a space
aws repostspace list-spaces   # space-level; per-member listing via console

# --- Tags ---
# Tag a space
aws repostspace tag-resource \
  --resource-arn arn:aws:repostspace:us-east-1:123456789012:space/spc-abc1234567890 \
  --tags Env=prod,Team=platform

# List tags for a space
aws repostspace list-tags-for-resource \
  --resource-arn arn:aws:repostspace:us-east-1:123456789012:space/spc-abc1234567890
```
