# Azure Container Registry (ACR) — CLI Reference
For service concepts, see [acr-capabilities.md](acr-capabilities.md).

## Registry Management

```bash
# --- Create and manage registries ---
# Create a Basic ACR (dev/test)
az acr create \
  --resource-group myRG \
  --name myACR \
  --sku Basic \
  --location eastus

# Create a Standard ACR (production)
az acr create \
  --resource-group myRG \
  --name myACR \
  --sku Standard \
  --location eastus

# Create a Premium ACR (geo-replication, private link, content trust)
az acr create \
  --resource-group myRG \
  --name myACR \
  --sku Premium \
  --location eastus \
  --zone-redundancy Enabled

# List all registries in a resource group
az acr list \
  --resource-group myRG \
  --query "[].{Name:name, Sku:sku.name, LoginServer:loginServer, Location:location}" \
  --output table

# Show registry details
az acr show \
  --resource-group myRG \
  --name myACR

# Update a registry (e.g., upgrade tier)
az acr update \
  --resource-group myRG \
  --name myACR \
  --sku Premium

# Delete a registry
az acr delete \
  --resource-group myRG \
  --name myACR \
  --yes

# Disable public network access (private endpoint only)
az acr update \
  --resource-group myRG \
  --name myACR \
  --public-network-enabled false

# Enable admin user (for quick testing only)
az acr update \
  --resource-group myRG \
  --name myACR \
  --admin-enabled true
```

## Authentication and Login

```bash
# Interactive login (developer, uses Azure AD credentials)
az acr login --name myACR

# Login with --expose-token (get raw token for non-Docker clients)
az acr login \
  --name myACR \
  --expose-token \
  --output tsv \
  --query accessToken

# Show admin credentials (admin account must be enabled)
az acr credential show \
  --name myACR

# Regenerate admin password
az acr credential renew \
  --name myACR \
  --password-name password

# Get the full login server URL
az acr show \
  --name myACR \
  --query loginServer \
  --output tsv

# Assign AcrPull role to a service principal
az role assignment create \
  --assignee {service-principal-object-id} \
  --scope $(az acr show --name myACR --query id -o tsv) \
  --role AcrPull

# Assign AcrPush to a managed identity
az role assignment create \
  --assignee-object-id {managed-identity-object-id} \
  --assignee-principal-type ServicePrincipal \
  --scope $(az acr show --name myACR --query id -o tsv) \
  --role AcrPush
```

## Image and Repository Management

```bash
# --- Repositories ---
# List all repositories in a registry
az acr repository list \
  --name myACR \
  --output table

# Show tags for a repository
az acr repository show-tags \
  --name myACR \
  --repository myapp \
  --orderby time_desc \
  --output table

# Show detailed manifest info for a specific tag
az acr repository show-manifests \
  --name myACR \
  --repository myapp \
  --detail \
  --query "[].{Digest:digest, Tags:tags, Size:imageSize, Created:timestamp}" \
  --output table

# Delete a specific tag
az acr repository delete \
  --name myACR \
  --image myapp:oldtag \
  --yes

# Delete all untagged manifests (housekeeping)
az acr repository show-manifests \
  --name myACR \
  --repository myapp \
  --query "[?tags[0]==null].digest" \
  --output tsv | xargs -I {} az acr repository delete --name myACR --image myapp@{} --yes

# Delete an entire repository
az acr repository delete \
  --name myACR \
  --repository myapp \
  --yes

# --- Import images ---
# Import image from Docker Hub into ACR (no local Docker needed)
az acr import \
  --name myACR \
  --source docker.io/library/nginx:latest \
  --image nginx:latest

# Import from another ACR
az acr import \
  --name myACR \
  --source sourceacr.azurecr.io/myapp:v1.0 \
  --image myapp:v1.0

# Import from a public registry with a different tag
az acr import \
  --name myACR \
  --source mcr.microsoft.com/dotnet/aspnet:8.0 \
  --image dotnet-aspnet:8.0
```

## ACR Tasks (Build Automation)

```bash
# --- Quick tasks (on-demand build + push) ---
# Build and push from current directory
az acr build \
  --registry myACR \
  --image myapp:latest \
  .

# Build with a specific Dockerfile and image tag
az acr build \
  --registry myACR \
  --image myapp:$(git rev-parse --short HEAD) \
  --file Dockerfile.prod \
  .

# Build from remote GitHub repository
az acr build \
  --registry myACR \
  --image myapp:latest \
  https://github.com/myorg/myrepo.git#main

# Build for a specific platform (cross-compilation)
az acr build \
  --registry myACR \
  --image myapp:latest-arm64 \
  --platform linux/arm64 \
  .

# --- Create persistent ACR Tasks ---
# Create a task triggered by GitHub commit
az acr task create \
  --registry myACR \
  --name build-on-commit \
  --image myapp:{{.Run.ID}} \
  --context https://github.com/myorg/myrepo.git#main \
  --file Dockerfile \
  --git-access-token {GITHUB_PAT}

# Create a task with base image update trigger
az acr task create \
  --registry myACR \
  --name build-on-base-update \
  --image myapp:latest \
  --context https://github.com/myorg/myapp.git#main \
  --file Dockerfile \
  --base-image-trigger-enabled true \
  --git-access-token {GITHUB_PAT}

# Create a multi-step task from YAML file
az acr task create \
  --registry myACR \
  --name multi-step-build \
  --context https://github.com/myorg/myrepo.git#main \
  --file acr-task.yaml \
  --git-access-token {GITHUB_PAT}

# Add a timer trigger to an existing task
az acr task timer add \
  --registry myACR \
  --name build-on-commit \
  --timer-name nightly \
  --schedule "0 2 * * *"

# --- Manage tasks ---
# List all tasks in a registry
az acr task list \
  --registry myACR \
  --output table

# Show task details
az acr task show \
  --registry myACR \
  --name build-on-commit

# Manually trigger a task run
az acr task run \
  --registry myACR \
  --name build-on-commit

# List task runs (run history)
az acr task list-runs \
  --registry myACR \
  --name build-on-commit \
  --output table

# Stream logs from a specific run
az acr task logs \
  --registry myACR \
  --run-id ca1

# Delete a task
az acr task delete \
  --registry myACR \
  --name build-on-commit \
  --yes
```

## Geo-replication

```bash
# Add a replica in another region (Premium only)
az acr replication create \
  --registry myACR \
  --location westeurope

# Add a replica with zone redundancy
az acr replication create \
  --registry myACR \
  --location eastus2 \
  --zone-redundancy Enabled

# List all replications
az acr replication list \
  --registry myACR \
  --output table

# Show replication status
az acr replication show \
  --registry myACR \
  --name westeurope

# Delete a replication
az acr replication delete \
  --registry myACR \
  --name westeurope \
  --yes
```

## Webhooks

```bash
# Create a webhook (fire on image push)
az acr webhook create \
  --registry myACR \
  --name push-notify \
  --uri https://myapp.contoso.com/api/acr-webhook \
  --actions push \
  --headers "Authorization=Bearer mytoken"

# Create a webhook for push and delete events, scoped to a repository
az acr webhook create \
  --registry myACR \
  --name repo-webhook \
  --uri https://myapp.contoso.com/api/acr-webhook \
  --actions push delete \
  --scope myapp:*

# List webhooks
az acr webhook list \
  --registry myACR \
  --output table

# Test a webhook (send a ping)
az acr webhook ping \
  --registry myACR \
  --name push-notify

# Show webhook event history
az acr webhook list-events \
  --registry myACR \
  --name push-notify \
  --output table

# Delete a webhook
az acr webhook delete \
  --registry myACR \
  --name push-notify
```

## Repository-Scoped Tokens and Scope Maps

```bash
# Create a scope map (read-only on one repo)
az acr scope-map create \
  --registry myACR \
  --name pullonly-scopemap \
  --repository myapp content/read metadata/read \
  --description "Read-only access to myapp repository"

# Create a scope map with push access
az acr scope-map create \
  --registry myACR \
  --name pushpull-scopemap \
  --repository myapp content/read content/write metadata/read metadata/write

# Create a token using a scope map
az acr token create \
  --registry myACR \
  --name pullonly-token \
  --scope-map pullonly-scopemap

# List tokens
az acr token list \
  --registry myACR \
  --output table

# Generate credentials for a token
az acr token credential generate \
  --registry myACR \
  --name pullonly-token \
  --password1

# Delete a token
az acr token delete \
  --registry myACR \
  --name pullonly-token \
  --yes

# --- Private Endpoint ---
# Create a private endpoint for ACR
az network private-endpoint create \
  --resource-group myRG \
  --name myACRPrivateEndpoint \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az acr show --name myACR --query id -o tsv) \
  --group-id registry \
  --connection-name myACRConnection
```
