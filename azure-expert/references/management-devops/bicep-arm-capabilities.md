# Bicep & ARM Templates — Capabilities

## Service Overview

Bicep is Azure's domain-specific language (DSL) for declarative infrastructure-as-code. It transpiles to ARM (Azure Resource Manager) JSON templates and provides a cleaner, more maintainable authoring experience. ARM Templates remain the underlying deployment mechanism.

**Recommendation**: Use Bicep for all new IaC work on Azure. ARM JSON is still valid but verbose; Bicep is the preferred authoring format.

---

## Bicep Language

### Basic Syntax

```bicep
// Target scope (default: resourceGroup)
targetScope = 'resourceGroup'

// Parameters
@description('The location for all resources')
@allowed(['eastus', 'westus2', 'uksouth'])
param location string = resourceGroup().location

@description('The SKU for the storage account')
param storageSkuName string = 'Standard_LRS'

@secure()  // value not logged, not returned in outputs
param adminPassword string

@minLength(3)
@maxLength(24)
param storageAccountName string

// Variables
var storagePrefix = 'stg${uniqueString(resourceGroup().id)}'

// Resource declaration
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageSkuName
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// Outputs
output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
output primaryEndpoint string = storageAccount.properties.primaryEndpoints.blob
```

### Decorators

```bicep
@description('Human-readable description for the parameter')
@allowed(['Standard_LRS', 'Standard_GRS', 'Premium_LRS'])
@secure()                              // hides from logs and outputs
@minLength(3)
@maxLength(24)
@minValue(1)
@maxValue(100)
@batchSize(3)                          // on resource loops: deploy N at a time
```

### Expressions and Functions

```bicep
// String interpolation
var name = 'storage-${environment}-${uniqueString(resourceGroup().id)}'

// Conditional deployment
resource pip 'Microsoft.Network/publicIPAddresses@2023-05-01' = if (deployPublicIP) {
  name: 'pip-${appName}'
  location: location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

// Resource copy (array loop)
resource storageAccounts 'Microsoft.Storage/storageAccounts@2023-01-01' = [for i in range(0, 3): {
  name: 'storage${i}${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {}
}]

// Object loop
var regions = ['eastus', 'westus2', 'uksouth']
resource rgs 'Microsoft.Resources/resourceGroups@2022-09-01' = [for region in regions: {
  name: 'rg-app-${region}'
  location: region
}]

// Conditional expression (ternary)
var skuName = environment == 'prod' ? 'Premium_LRS' : 'Standard_LRS'

// Reference existing resources
resource existingVnet 'Microsoft.Network/virtualNetworks@2023-05-01' existing = {
  name: 'myExistingVnet'
  scope: resourceGroup('other-rg')  // cross-RG reference
}

// Dependencies
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = { /* ... */ }

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: 'mywebapp'
  location: location
  properties: {
    serverFarmId: appServicePlan.id  // implicit dependency via property reference
  }
  dependsOn: [appServicePlan]        // explicit dependency (when needed)
}
```

---

## Target Scopes

Bicep files can deploy to different Azure scopes:

| Scope | `targetScope` | CLI Command |
|---|---|---|
| Resource Group | `resourceGroup` (default) | `az deployment group create` |
| Subscription | `subscription` | `az deployment sub create` |
| Management Group | `managementGroup` | `az deployment mg create` |
| Tenant | `tenant` | `az deployment tenant create` |

```bicep
// Subscription-scoped deployment (e.g., creating resource groups)
targetScope = 'subscription'

param location string = deployment().location

resource myRG 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-my-app'
  location: location
  tags: { environment: 'production' }
}

// Then deploy resource group-level resources using a module
module appModule './modules/app.bicep' = {
  name: 'appDeployment'
  scope: myRG
  params: {
    location: location
  }
}
```

---

## Modules

Reusable Bicep files for modular, composable deployments:

```bicep
// main.bicep — consuming a module
module storageModule './modules/storage.bicep' = {
  name: 'storageDeployment'    // deployment name (must be unique within parent)
  params: {
    storageAccountName: storageAccountName
    location: location
    skuName: 'Standard_LRS'
  }
}

// Use module output
output storageId string = storageModule.outputs.storageAccountId
```

```bicep
// modules/storage.bicep — the module file
@description('Storage account name')
param storageAccountName string

param location string
param skuName string = 'Standard_LRS'

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: { name: skuName }
  kind: 'StorageV2'
  properties: { supportsHttpsTrafficOnly: true }
}

output storageAccountId string = storage.id
output storageAccountName string = storage.name
```

---

## Azure Verified Modules (AVM)

Microsoft-curated, tested, and maintained Bicep modules for common Azure resources.

- **Registry**: `br/public:avm/res/<provider>/<resource>:<version>`
- Available at: [aka.ms/avm](https://aka.ms/avm)
- Enforces best practices (naming, tagging, diagnostics, RBAC) out of the box.

```bicep
// Use AVM module for Azure Container Registry
module acr 'br/public:avm/res/container-registry/registry:0.3.1' = {
  name: 'acrDeployment'
  params: {
    name: 'myacr${uniqueString(resourceGroup().id)}'
    location: location
    acrSku: 'Standard'
    acrAdminUserEnabled: false
    managedIdentities: { systemAssigned: true }
    diagnosticSettings: [{
      workspaceResourceId: logAnalyticsWorkspace.id
    }]
  }
}

// Use AVM module for Key Vault
module keyVault 'br/public:avm/res/key-vault/vault:0.6.2' = {
  name: 'kvDeployment'
  params: {
    name: 'kv-${uniqueString(resourceGroup().id)}'
    location: location
    enablePurgeProtection: true
    enableRbacAuthorization: true
    softDeleteRetentionInDays: 90
    diagnosticSettings: [{ workspaceResourceId: logAnalyticsWorkspace.id }]
  }
}
```

---

## Bicep Registry

Store and share Bicep modules in a registry:

```bicep
// Reference module from private Azure Container Registry
module myModule 'br:myacr.azurecr.io/bicep/modules/storage:v1.0' = {
  name: 'storageDeployment'
  params: { /* ... */ }
}

// Reference from public Microsoft registry
module avm 'br/public:avm/res/storage/storage-account:0.9.0' = {
  name: 'storageDeployment'
  params: { /* ... */ }
}
```

```bash
# Publish a module to a registry
az bicep publish \
  --file modules/storage.bicep \
  --target br:myacr.azurecr.io/bicep/modules/storage:v1.0

# Restore modules (download referenced modules locally)
az bicep restore --file main.bicep
```

---

## Parameter Files

### `.bicepparam` Files (Recommended)

```bicep
// main.bicepparam
using './main.bicep'

param location = 'eastus'
param storageAccountName = 'mystorageaccount'
param environment = 'production'
param adminPassword = readEnvironmentVariable('ADMIN_PASSWORD')  // from env var
```

### Traditional `parameters.json`

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": { "value": "eastus" },
    "storageAccountName": { "value": "mystorageaccount" },
    "adminPassword": { "reference": { "keyVault": { "id": "/subscriptions/.../vaults/myKV" }, "secretName": "adminPassword" } }
  }
}
```

---

## Deployment Modes

| Mode | Behavior | Risk |
|---|---|---|
| **Incremental** (default) | Adds/updates resources in template; resources in Azure not in template are left unchanged | Safe for most scenarios |
| **Complete** | Deletes resources in Azure not in template (within scope) | High — can delete production resources |

```bash
# Explicitly specify mode (Incremental is default)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --mode Incremental

# Complete mode — use with extreme caution
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --mode Complete
```

---

## What-If

Preview changes before deploying — shows resource add/modify/delete/ignore operations:

```bash
# What-If for resource group deployment
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam

# What-If for subscription deployment
az deployment sub what-if \
  --location eastus \
  --template-file main.bicep

# Confirm and deploy in one command
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --confirm-with-what-if   # shows what-if then prompts for confirmation
```

---

## Deployment Stacks

Manage a set of resources as a unit — enables lifecycle management with protect-on-delete:

```bash
# Create a deployment stack (with deny-assignments)
az stack group create \
  --name myAppStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam \
  --deny-settings-mode DenyDelete \          # prevent deletion of stack resources
  --deny-settings-apply-to-child-scopes \    # apply to child resources too
  --action-on-unmanage detachAll             # what to do with resources removed from template

# Update stack (re-deploy with changes)
az stack group create \
  --name myAppStack \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.bicepparam

# Show stack
az stack group show \
  --name myAppStack \
  --resource-group myRG

# List stacks
az stack group list \
  --resource-group myRG \
  -o table

# Delete stack and all managed resources
az stack group delete \
  --name myAppStack \
  --resource-group myRG \
  --action-on-unmanage deleteAll \  # delete all resources managed by stack
  --yes

# Subscription-scoped stack
az stack sub create \
  --name myOrgStack \
  --location eastus \
  --template-file subscription.bicep \
  --parameters @sub-params.bicepparam \
  --deny-settings-mode None

az stack sub delete \
  --name myOrgStack \
  --action-on-unmanage deleteAll \
  --yes
```

---

## Template Specs

Versioned ARM/Bicep templates stored in Azure — shareable across organization:

```bash
# Create a Template Spec (from Bicep file)
az ts create \
  --name myTemplateSpec \
  --version v1.0 \
  --resource-group myTemplateSpecsRG \
  --location eastus \
  --template-file main.bicep \
  --description "Standard app deployment template v1.0"

# List Template Specs
az ts list \
  --resource-group myTemplateSpecsRG \
  -o table

# Show Template Spec versions
az ts show \
  --name myTemplateSpec \
  --resource-group myTemplateSpecsRG

# Deploy from a Template Spec
az deployment group create \
  --resource-group myTargetRG \
  --template-spec $(az ts show --name myTemplateSpec --resource-group myTemplateSpecsRG --version v1.0 --query id -o tsv) \
  --parameters @params.bicepparam

# Reference Template Spec in Bicep as a module
module fromSpec 'ts:myTemplateSpecsRG/myTemplateSpec/v1.0' = {
  name: 'myDeployment'
  params: { /* ... */ }
}

# Delete a Template Spec version
az ts delete \
  --name myTemplateSpec \
  --version v1.0 \
  --resource-group myTemplateSpecsRG \
  --yes
```

---

## IaC Tool Comparison

| Dimension | Bicep | Terraform | Pulumi |
|---|---|---|---|
| **Language** | Bicep DSL (transpiles to ARM JSON) | HCL | Python, TypeScript, Go, C#, Java |
| **Azure support** | Day-0 (immediate new features) | Days to weeks lag | Days to weeks lag |
| **State management** | No state file (ARM is source of truth) | State file (local or remote) | State file (Pulumi Cloud) |
| **Multi-cloud** | Azure only | Yes | Yes |
| **Learning curve** | Low (Azure-specific knowledge maps directly) | Medium | Medium-High (programming language required) |
| **Modules/reuse** | Bicep modules, AVM | Terraform modules registry | Standard language packages |
| **Best for** | Azure-only organizations, Azure-first teams | Multi-cloud, existing Terraform expertise | Code-first teams wanting full language power |

---

## CI/CD Patterns

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
    paths: ['infra/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # required for OIDC
      contents: read

    steps:
    - uses: actions/checkout@v4

    - name: Azure Login (OIDC - no secrets)
      uses: azure/login@v2
      with:
        client-id: ${{ secrets.AZURE_CLIENT_ID }}
        tenant-id: ${{ secrets.AZURE_TENANT_ID }}
        subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

    - name: What-If
      uses: azure/arm-deploy@v2
      with:
        resourceGroupName: myRG
        template: ./infra/main.bicep
        parameters: ./infra/params.bicepparam
        additionalArguments: '--what-if'

    - name: Deploy
      uses: azure/arm-deploy@v2
      with:
        resourceGroupName: myRG
        template: ./infra/main.bicep
        parameters: ./infra/params.bicepparam
```

### Azure Pipelines

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main]
  paths:
    include: [infra/]

jobs:
- job: Deploy
  pool:
    vmImage: ubuntu-latest
  steps:
  - task: AzureCLI@2
    displayName: 'What-If'
    inputs:
      azureSubscription: 'my-azure-service-connection'
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        az deployment group what-if \
          --resource-group $(ResourceGroup) \
          --template-file infra/main.bicep \
          --parameters @infra/params.$(Environment).bicepparam

  - task: AzureCLI@2
    displayName: 'Deploy Bicep'
    inputs:
      azureSubscription: 'my-azure-service-connection'
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        az deployment group create \
          --resource-group $(ResourceGroup) \
          --template-file infra/main.bicep \
          --parameters @infra/params.$(Environment).bicepparam \
          --name deploy-$(Build.BuildId)
```
