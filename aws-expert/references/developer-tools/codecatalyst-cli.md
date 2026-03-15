# Amazon CodeCatalyst — CLI Reference

For service concepts, see [codecatalyst-capabilities.md](codecatalyst-capabilities.md).

**Note**: The `aws codecatalyst` CLI requires an active CodeCatalyst Space and that the calling IAM identity has a linked CodeCatalyst user. Most `aws codecatalyst` commands require `--space-name` and often `--project-name`.

```bash
# --- Spaces ---
# List spaces the caller has access to
aws codecatalyst list-spaces

# Get details of a specific space
aws codecatalyst get-space --name MySpace

# --- Projects ---
# Create a project in a space
aws codecatalyst create-project \
  --space-name MySpace \
  --display-name "My New Project" \
  --description "Project description"

# List projects in a space
aws codecatalyst list-projects \
  --space-name MySpace

# Get project details
aws codecatalyst get-project \
  --space-name MySpace \
  --name my-new-project

# Delete a project
aws codecatalyst delete-project \
  --space-name MySpace \
  --name my-new-project

# --- Source Repositories ---
# Create a source repository
aws codecatalyst create-source-repository \
  --space-name MySpace \
  --project-name my-project \
  --name my-service-repo \
  --description "Service source code"

# List source repositories in a project
aws codecatalyst list-source-repositories \
  --space-name MySpace \
  --project-name my-project

# Get source repository details
aws codecatalyst get-source-repository \
  --space-name MySpace \
  --project-name my-project \
  --name my-service-repo

# Get clone URL for a repository (use with git clone)
aws codecatalyst get-source-repository-clone-urls \
  --space-name MySpace \
  --project-name my-project \
  --source-repository-name my-service-repo

# List branches in a source repository
aws codecatalyst list-source-repository-branches \
  --space-name MySpace \
  --project-name my-project \
  --source-repository-name my-service-repo

# --- Dev Environments ---
# Create a dev environment (VS Code SSH)
aws codecatalyst create-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --ides '[{"name":"VSCode","runtime":"public.ecr.aws/jetbrains/gateway"}]' \
  --instance-type dev.standard1.medium \
  --persistent-storage sizeInGiB=32 \
  --repositories '[{"repositoryName":"my-service-repo","branchName":"feature/my-feature"}]' \
  --inactivity-timeout-minutes 30

# Create a dev environment (JetBrains Gateway)
aws codecatalyst create-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --ides '[{"name":"IntelliJ","runtime":"public.ecr.aws/jetbrains/gateway"}]' \
  --instance-type dev.standard1.large \
  --persistent-storage sizeInGiB=64 \
  --repositories '[{"repositoryName":"my-service-repo","branchName":"main"}]'

# List dev environments in a project
aws codecatalyst list-dev-environments \
  --space-name MySpace \
  --project-name my-project

# List dev environments across all projects in a space
aws codecatalyst list-dev-environments \
  --space-name MySpace

# Get dev environment details and status
aws codecatalyst get-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id>

# Start a stopped dev environment
aws codecatalyst start-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id>

# Start a dev environment session (get connection token for IDE)
aws codecatalyst start-dev-environment-session \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id> \
  --session-configuration sessionType=SSH

# Stop a running dev environment
aws codecatalyst stop-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id>

# Stop a specific session within a dev environment
aws codecatalyst stop-dev-environment-session \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id> \
  --session-id <session-id>

# Update a dev environment (change instance type or inactivity timeout)
aws codecatalyst update-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id> \
  --instance-type dev.standard1.xlarge \
  --inactivity-timeout-minutes 60

# Delete a dev environment
aws codecatalyst delete-dev-environment \
  --space-name MySpace \
  --project-name my-project \
  --id <dev-environment-id>

# --- Workflows ---
# Create a workflow (from a YAML definition file)
aws codecatalyst create-workflow \
  --space-name MySpace \
  --project-name my-project \
  --source-repository-name my-service-repo \
  --definition file://workflow.yaml

# List workflows in a project
aws codecatalyst list-workflows \
  --space-name MySpace \
  --project-name my-project

# Get workflow details
aws codecatalyst get-workflow \
  --space-name MySpace \
  --project-name my-project \
  --id <workflow-id>

# Start a workflow run (manual trigger)
aws codecatalyst start-workflow-run \
  --space-name MySpace \
  --project-name my-project \
  --workflow-id <workflow-id>

# Stop a running workflow run
aws codecatalyst stop-workflow-run \
  --space-name MySpace \
  --project-name my-project \
  --id <workflow-run-id>

# Delete a workflow
aws codecatalyst delete-workflow \
  --space-name MySpace \
  --project-name my-project \
  --id <workflow-id>

# --- Workflow Runs ---
# List workflow runs
aws codecatalyst list-workflow-runs \
  --space-name MySpace \
  --project-name my-project \
  --workflow-id <workflow-id>

# Get workflow run details (status, start/end time, actions)
aws codecatalyst get-workflow-run \
  --space-name MySpace \
  --project-name my-project \
  --id <workflow-run-id>

# --- Access Tokens ---
# Create a personal access token (PAT) for API/Git authentication
aws codecatalyst create-access-token \
  --name my-token \
  --expires-time 2024-12-31T23:59:59Z

# List access tokens for the calling user
aws codecatalyst list-access-tokens

# Delete an access token
aws codecatalyst delete-access-token \
  --id <token-id>

# --- Subscriptions & Billing ---
# Get subscription details for a space
aws codecatalyst get-subscription \
  --space-name MySpace
```
