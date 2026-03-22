# Azure DevOps & GitHub Actions — CLI Reference

## Prerequisites

```bash
# Install Azure DevOps CLI extension
az extension add -n azure-devops
az extension update -n azure-devops

az login
az account set --subscription "My Subscription"

# Configure default organization and project (avoid repeating flags)
az devops configure --defaults \
  organization=https://dev.azure.com/myorg \
  project=MyProject

# Verify configuration
az devops configure --list
```

---

## Organization and Project Management

```bash
# List organizations (requires PAT or login)
az devops project list --organization https://dev.azure.com/myorg -o table

# Create a new project
az devops project create \
  --name MyNewProject \
  --organization https://dev.azure.com/myorg \
  --source-control git \
  --process Agile \
  --visibility private \
  --description "New application project"

# Show project details
az devops project show --project MyProject -o table

# Delete project
az devops project delete --id <project-id> --yes
```

---

## Pipelines

```bash
# List pipelines
az pipelines list -o table

# List pipelines with details
az pipelines list --output json

# Show pipeline details
az pipelines show --name "MyPipeline"
az pipelines show --id <pipeline-id>

# Create pipeline from YAML file in repo
az pipelines create \
  --name "MyCI-Pipeline" \
  --yaml-path azure-pipelines.yml \
  --repository MyRepo \
  --repository-type tfsgit \
  --branch main \
  --skip-run

# Create pipeline from GitHub repository
az pipelines create \
  --name "GitHub-Pipeline" \
  --yaml-path azure-pipelines.yml \
  --repository myorg/my-repo \
  --repository-type github \
  --branch main \
  --service-connection <github-service-connection-id>

# Run a pipeline (manual trigger)
az pipelines run --name "MyCI-Pipeline"

# Run with specific branch
az pipelines run --name "MyCI-Pipeline" --branch feature/my-feature

# Run with pipeline variables
az pipelines run \
  --name "MyCI-Pipeline" \
  --variables environment=prod version=1.2.3

# Run with specific stage
az pipelines run \
  --name "MyCI-Pipeline" \
  --stages Deploy

# Show pipeline run details
az pipelines runs show --id <run-id>

# List pipeline runs
az pipelines runs list --pipeline-name "MyCI-Pipeline" --top 10 -o table

# List runs with status filter
az pipelines runs list \
  --pipeline-name "MyCI-Pipeline" \
  --result failed \
  --top 5 \
  -o table

# Cancel a running pipeline
az pipelines runs cancel --id <run-id>

# Update pipeline settings
az pipelines update \
  --name "MyCI-Pipeline" \
  --new-name "MyCI-Pipeline-v2" \
  --description "Updated CI pipeline"

# Delete pipeline
az pipelines delete --id <pipeline-id> --yes
```

---

## Pipeline Variables

```bash
# Create pipeline variable (non-secret)
az pipelines variable create \
  --name myVariable \
  --value myValue \
  --pipeline-name "MyCI-Pipeline" \
  --allow-override true

# Create secret variable (value not readable after creation)
az pipelines variable create \
  --name mySecret \
  --value "supersecret" \
  --pipeline-name "MyCI-Pipeline" \
  --secret true

# List pipeline variables
az pipelines variable list --pipeline-name "MyCI-Pipeline" -o table

# Update variable value
az pipelines variable update \
  --name myVariable \
  --new-value newValue \
  --pipeline-name "MyCI-Pipeline"

# Delete variable
az pipelines variable delete \
  --name myVariable \
  --pipeline-name "MyCI-Pipeline" \
  --yes
```

---

## Variable Groups (Library)

```bash
# Create a variable group
az pipelines variable-group create \
  --name production-secrets \
  --variables apiUrl=https://api.prod.mycompany.com \
  --authorize true

# Create a Key Vault-linked variable group
az pipelines variable-group create \
  --name kv-secrets \
  --authorize true \
  --variables dummy=placeholder  # placeholder required

# Link to Key Vault (configure via portal or REST API — CLI has limited support)
# Use portal: Library → Variable Groups → Link secrets from Azure Key Vault

# List variable groups
az pipelines variable-group list -o table

# Show variable group
az pipelines variable-group show --id <group-id>

# Add variable to group
az pipelines variable-group variable create \
  --group-id <group-id> \
  --name newVar \
  --value newValue

# Update variable in group
az pipelines variable-group variable update \
  --group-id <group-id> \
  --name newVar \
  --new-value updatedValue

# Delete variable group
az pipelines variable-group delete --id <group-id> --yes
```

---

## Environments

```bash
# Create an environment
az pipelines environment create \
  --name production \
  --description "Production deployment environment"

# List environments
az pipelines environment list -o table

# Show environment
az pipelines environment show --name production

# Delete environment
az pipelines environment delete --id <env-id> --yes
```

---

## Service Endpoints (Service Connections)

```bash
# List service connections
az devops service-endpoint list -o table

# Create Azure Resource Manager service connection (Workload Identity Federation)
az devops service-endpoint azurerm create \
  --azure-rm-service-principal-id <app-registration-client-id> \
  --azure-rm-subscription-id <subscription-id> \
  --azure-rm-subscription-name "My Subscription" \
  --azure-rm-tenant-id <tenant-id> \
  --name "azure-prod-connection" \
  --workload-identity-federation-issuer https://vstoken.dev.azure.com/myorg \
  --workload-identity-federation-subject sc://myorg/MyProject/azure-prod-connection

# Create service connection with service principal secret
az devops service-endpoint azurerm create \
  --azure-rm-service-principal-id <client-id> \
  --azure-rm-service-principal-certificate-path ./cert.pem \
  --azure-rm-subscription-id <sub-id> \
  --azure-rm-subscription-name "My Subscription" \
  --azure-rm-tenant-id <tenant-id> \
  --name "azure-dev-connection"

# Show service connection details
az devops service-endpoint show --id <connection-id>

# Update service connection
az devops service-endpoint update --id <connection-id>

# Grant access to all pipelines
az devops service-endpoint update \
  --id <connection-id> \
  --enable-for-all true

# Delete service connection
az devops service-endpoint delete --id <connection-id> --yes
```

---

## Azure Repos

```bash
# List repositories
az repos list -o table

# Create a repository
az repos create --name MyNewRepo

# Show repository details (clone URLs, default branch)
az repos show --repository MyRepo

# Update repository (rename, change default branch)
az repos update \
  --repository MyRepo \
  --name MyRenamedRepo \
  --default-branch main

# Delete repository
az repos delete --id <repo-id> --yes

# Import a repository (from GitHub)
az repos import create \
  --git-source-url https://github.com/myorg/my-repo.git \
  --repository MyImportedRepo

# List branches
az repos ref list --repository MyRepo --filter heads -o table

# Create a branch policy (require minimum reviewers)
az repos policy approver-count create \
  --repository-id <repo-id> \
  --branch main \
  --blocking true \
  --enabled true \
  --minimum-approver-count 2 \
  --creator-vote-counts false \
  --allow-downvotes false \
  --reset-on-source-push true

# Create required status check policy (require pipeline success)
az repos policy build create \
  --repository-id <repo-id> \
  --branch main \
  --blocking true \
  --enabled true \
  --build-definition-id <pipeline-id> \
  --display-name "CI Required" \
  --queue-on-source-update-only false \
  --manual-queue-only false \
  --valid-duration 720

# List branch policies
az repos policy list --branch main --repository MyRepo -o table
```

---

## Pull Requests

```bash
# Create a pull request
az repos pr create \
  --repository MyRepo \
  --source-branch feature/my-feature \
  --target-branch main \
  --title "Add new feature" \
  --description "This PR adds the new feature X" \
  --reviewers "user@mycompany.com" "team@mycompany.com" \
  --auto-complete false \
  --squash true

# List pull requests
az repos pr list -o table

# List PRs by status
az repos pr list --status active -o table
az repos pr list --status completed --top 10 -o table

# Show PR details
az repos pr show --id <pr-id>

# Approve a PR
az repos pr update \
  --id <pr-id> \
  --status approved  # or rejected, waiting

# Vote on PR (from CLI)
az repos pr reviewer add \
  --id <pr-id> \
  --reviewers "user@mycompany.com"

# Complete (merge) a PR
az repos pr update \
  --id <pr-id> \
  --status completed \
  --merge-strategy squash \
  --delete-source-branch true

# Abandon a PR
az repos pr update --id <pr-id> --status abandoned

# Add a comment to PR
az repos pr reviewers add --id <pr-id> --reviewers "reviewer@mycompany.com"

# Add work item link to PR
az repos pr work-item add --id <pr-id> --work-items <work-item-id>
```

---

## Work Items (Azure Boards)

```bash
# Create a user story
az boards work-item create \
  --title "As a user, I can reset my password" \
  --type "User Story" \
  --iteration "MyProject\\Sprint 1" \
  --assigned-to "dev@mycompany.com" \
  --description "Implement password reset flow"

# Create a bug
az boards work-item create \
  --title "Login fails for SSO users" \
  --type Bug \
  --assigned-to "dev@mycompany.com" \
  --priority 1

# Create a task
az boards work-item create \
  --title "Implement password reset endpoint" \
  --type Task \
  --assigned-to "dev@mycompany.com"

# Show work item
az boards work-item show --id <work-item-id>

# Update work item (change state, assignee, etc.)
az boards work-item update \
  --id <work-item-id> \
  --state Active \
  --assigned-to "newdev@mycompany.com"

# Mark as completed
az boards work-item update --id <work-item-id> --state Closed

# Run a saved query
az boards query --id <query-id> -o table

# Link work items (parent-child)
az boards work-item relation add \
  --id <child-id> \
  --relation-type Parent \
  --target-id <parent-id>

# Delete work item (moves to recycle bin)
az boards work-item delete --id <work-item-id> --yes
```

---

## Azure Artifacts

```bash
# List feeds
az artifacts universal list-packages --feed myfeed

# Create feed
az artifacts feed create --name myfeed

# Delete feed
az artifacts feed delete --feed myfeed --yes

# Publish universal package (generic file artifact)
az artifacts universal publish \
  --organization https://dev.azure.com/myorg \
  --project MyProject \
  --scope project \
  --feed myfeed \
  --name mypackage \
  --version 1.0.0 \
  --path ./dist/ \
  --description "My universal package"

# Download universal package
az artifacts universal download \
  --organization https://dev.azure.com/myorg \
  --project MyProject \
  --scope project \
  --feed myfeed \
  --name mypackage \
  --version 1.0.0 \
  --path ./downloaded/

# List package versions
az artifacts universal list-packages \
  --organization https://dev.azure.com/myorg \
  --project MyProject \
  --scope project \
  --feed myfeed \
  --package-name mypackage \
  -o table
```

---

## GitHub Actions Authentication Setup

```bash
# Set up OIDC for GitHub Actions (Workload Identity Federation)

# Step 1: Create app registration
APP_ID=$(az ad app create \
  --display-name "GitHub-Actions-MyRepo" \
  --query appId -o tsv)

echo "Client ID: $APP_ID"

# Step 2: Create service principal
SP_OBJECT_ID=$(az ad sp create --id $APP_ID --query id -o tsv)

# Step 3: Assign role (Contributor to subscription)
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role Contributor \
  --scope /subscriptions/$(az account show --query id -o tsv)

# Or more restricted scope:
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role Contributor \
  --scope /subscriptions/$(az account show --query id -o tsv)/resourceGroups/myRG

# Step 4: Add federated credential for main branch pushes
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/my-repo:ref:refs/heads/main",
    "description": "Main branch deploys",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Add for pull requests
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "pull-requests",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/my-repo:pull_request",
    "description": "PR validation",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Add for a specific environment
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "production-env",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/my-repo:environment:production",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Step 5: Output values to store as GitHub secrets
echo "AZURE_CLIENT_ID: $APP_ID"
echo "AZURE_TENANT_ID: $(az account show --query tenantId -o tsv)"
echo "AZURE_SUBSCRIPTION_ID: $(az account show --query id -o tsv)"
```
