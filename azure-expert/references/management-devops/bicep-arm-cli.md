# Bicep & ARM Templates — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"

# Install/upgrade Bicep
az bicep install          # installs latest version
az bicep upgrade          # upgrade to latest
az bicep version          # show installed version

# Install VS Code Bicep extension (recommended for development)
code --install-extension ms-azuretools.vscode-bicep
```

---

## Bicep Build and Decompile

```bash
# Compile Bicep to ARM JSON
az bicep build --file main.bicep
# Produces main.json in same directory

# Compile to specific output path
az bicep build --file main.bicep --outfile ./output/main.json

# Compile all Bicep files in a directory
az bicep build --file ./infra/*.bicep

# Decompile ARM JSON to Bicep (best-effort — may need manual cleanup)
az bicep decompile --file main.json
# Produces main.bicep in same directory

# Decompile with force overwrite
az bicep decompile --file main.json --force

# Generate parameter file from Bicep
az bicep generate-params --file main.bicep --output-format bicepparam
az bicep generate-params --file main.bicep --output-format json

# Publish module to registry
az bicep publish \
  --file modules/storage.bicep \
  --target br:myacr.azurecr.io/bicep/modules/storage:v1.0 \
  --documentationUri "https://github.com/myorg/bicep-modules/blob/main/storage/README.md"

# Restore modules referenced in Bicep file
az bicep restore --file main.bicep

# Lint a Bicep file
az bicep lint --file main.bicep

# Format a Bicep file
az bicep format --file main.bicep
```

---

## Resource Group Deployments

```bash
# Basic deployment
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep

# With .bicepparam parameter file
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam

# With JSON parameter file
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.json

# Inline parameters (override specific values)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --parameters storageAccountName=overridevalue environment=prod

# Named deployment (for tracking)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --name "deploy-$(date +%Y%m%d%H%M%S)" \
  --parameters @params.bicepparam

# Complete mode (DANGEROUS — deletes resources not in template)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --mode Complete \
  --parameters @params.bicepparam

# Deploy and wait for completion (default behavior)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --no-wait  # don't wait for completion

# Get outputs from a deployment
az deployment group show \
  --resource-group myRG \
  --name myDeployment \
  --query properties.outputs

# Get specific output value
az deployment group show \
  --resource-group myRG \
  --name myDeployment \
  --query "properties.outputs.storageAccountName.value" -o tsv

# Validate template without deploying
az deployment group validate \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam

# What-If (preview changes)
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam

# What-If with result format (FullResourcePayloads shows full resource state)
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --result-format FullResourcePayloads

# Confirm then deploy
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --confirm-with-what-if

# List deployments in resource group
az deployment group list \
  --resource-group myRG \
  -o table

# Show deployment details
az deployment group show \
  --resource-group myRG \
  --name myDeployment

# List deployment operations (detailed steps)
az deployment operation group list \
  --resource-group myRG \
  --name myDeployment \
  -o table

# Delete a deployment (from history only — resources remain)
az deployment group delete \
  --resource-group myRG \
  --name oldDeployment
```

---

## Subscription Deployments

```bash
# Deploy at subscription scope (creates resource groups, policy assignments, etc.)
az deployment sub create \
  --location eastus \
  --template-file subscription.bicep \
  --parameters @sub-params.bicepparam \
  --name "sub-deploy-$(date +%Y%m%d)"

# What-If for subscription deployment
az deployment sub what-if \
  --location eastus \
  --template-file subscription.bicep \
  --parameters @sub-params.bicepparam

# Validate
az deployment sub validate \
  --location eastus \
  --template-file subscription.bicep \
  --parameters @sub-params.bicepparam

# List subscription deployments
az deployment sub list -o table

# Show deployment
az deployment sub show --name mySubDeploy

# Get operations
az deployment operation sub list --name mySubDeploy -o table
```

---

## Management Group Deployments

```bash
# Deploy at management group scope (policy, RBAC at MG level)
az deployment mg create \
  --management-group-id myManagementGroup \
  --location eastus \
  --template-file mg-policy.bicep \
  --parameters @mg-params.bicepparam

# What-If
az deployment mg what-if \
  --management-group-id myManagementGroup \
  --location eastus \
  --template-file mg-policy.bicep

# List MG deployments
az deployment mg list --management-group-id myManagementGroup -o table
```

---

## Tenant Deployments

```bash
# Deploy at tenant scope (management groups, tenant-level policy)
az deployment tenant create \
  --location eastus \
  --template-file tenant.bicep \
  --parameters @tenant-params.bicepparam

# What-If
az deployment tenant what-if \
  --location eastus \
  --template-file tenant.bicep

# List tenant deployments
az deployment tenant list -o table
```

---

## Deployment Stacks

```bash
# --- Resource Group Stacks ---

# Create stack with deny-delete protection
az stack group create \
  --name myAppStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --deny-settings-mode DenyDelete \
  --deny-settings-apply-to-child-scopes \
  --action-on-unmanage detachAll \
  --description "Application infrastructure stack"

# Options for --deny-settings-mode:
# None — no deny assignments
# DenyDelete — prevent deletion
# DenyWriteAndDelete — prevent modification and deletion

# Options for --action-on-unmanage (when resources removed from template):
# detachAll — keep resources but remove from stack management
# deleteAll — delete resources removed from template
# deleteResources — delete resources, detach resource groups

# Update a stack (redeploy with new template/params)
az stack group create \
  --name myAppStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --deny-settings-mode DenyDelete

# Show stack (what resources are managed)
az stack group show \
  --name myAppStack \
  --resource-group myRG

# List stacks
az stack group list \
  --resource-group myRG \
  -o table

# Export stack as Bicep (recover template from stack)
az stack group export \
  --name myAppStack \
  --resource-group myRG

# Delete stack and all managed resources
az stack group delete \
  --name myAppStack \
  --resource-group myRG \
  --action-on-unmanage deleteAll \
  --yes

# Delete stack but keep resources (detach)
az stack group delete \
  --name myAppStack \
  --resource-group myRG \
  --action-on-unmanage detachAll \
  --yes

# --- Subscription Stacks ---

az stack sub create \
  --name myOrgStack \
  --location eastus \
  --template-file subscription.bicep \
  --parameters @sub-params.bicepparam \
  --deny-settings-mode None \
  --action-on-unmanage detachAll

az stack sub show --name myOrgStack
az stack sub list -o table

az stack sub delete \
  --name myOrgStack \
  --action-on-unmanage deleteAll \
  --yes
```

---

## Template Specs

```bash
# Create a Template Spec (from Bicep file)
az ts create \
  --name myAppTemplate \
  --version "1.0" \
  --resource-group ts-rg \
  --location eastus \
  --template-file main.bicep \
  --display-name "My Application Template" \
  --description "Deploys the complete application stack"

# Create new version of existing Template Spec
az ts create \
  --name myAppTemplate \
  --version "1.1" \
  --resource-group ts-rg \
  --location eastus \
  --template-file main.bicep

# List Template Specs in resource group
az ts list \
  --resource-group ts-rg \
  -o table

# List versions of a Template Spec
az ts show \
  --name myAppTemplate \
  --resource-group ts-rg

# Get Template Spec ID for deployment
TEMPLATE_SPEC_ID=$(az ts show \
  --name myAppTemplate \
  --resource-group ts-rg \
  --version "1.0" \
  --query id -o tsv)

# Deploy from Template Spec
az deployment group create \
  --resource-group myTargetRG \
  --template-spec $TEMPLATE_SPEC_ID \
  --parameters @params.bicepparam \
  --name "deploy-from-spec"

# Export Template Spec to files
az ts export \
  --name myAppTemplate \
  --version "1.0" \
  --resource-group ts-rg \
  --output-folder ./exported-template

# Delete specific version
az ts delete \
  --name myAppTemplate \
  --version "1.0" \
  --resource-group ts-rg \
  --yes

# Delete all versions
az ts delete \
  --name myAppTemplate \
  --resource-group ts-rg \
  --yes
```

---

## Bicep Registry (Private)

```bash
# Login to ACR for Bicep registry
az acr login --name myacr

# Publish module to private registry
az bicep publish \
  --file modules/storage.bicep \
  --target br:myacr.azurecr.io/bicep/modules/storage:v1.0

# List modules in ACR registry
az acr repository list --name myacr --query "[?starts_with(@, 'bicep/')]" -o table

# List tags (versions) for a module
az acr repository show-tags \
  --name myacr \
  --repository bicep/modules/storage \
  -o table
```

---

## Useful ARM/Bicep Debugging Commands

```bash
# Show what resources are deployed in a resource group
az resource list --resource-group myRG -o table

# Get resource in JSON (includes all properties)
az resource show \
  --resource-group myRG \
  --resource-type Microsoft.Storage/storageAccounts \
  --name mystorageaccount

# Export current resource group as ARM template
az group export \
  --resource-group myRG \
  --include-parameter-default-value \
  > exported-rg.json

# Convert exported ARM template to Bicep
az bicep decompile --file exported-rg.json

# Check if resource exists (useful in scripts)
if az resource show --ids /subscriptions/{sub}/resourceGroups/{rg}/providers/... &>/dev/null; then
  echo "Resource exists"
else
  echo "Resource not found"
fi
```
