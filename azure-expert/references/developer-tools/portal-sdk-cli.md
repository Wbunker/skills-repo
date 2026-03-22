# Azure Portal & SDKs — CLI Reference
For service concepts, see [portal-sdk-capabilities.md](portal-sdk-capabilities.md).

## Azure Resource Graph Queries

```bash
# --- Resource Graph Query ---
# Install extension if needed
az extension add --name resource-graph

# Basic query: list all VMs
az graph query \
  --graph-query "Resources | where type =~ 'microsoft.compute/virtualmachines' | project name, location, resourceGroup"

# List all subscriptions accessible
az graph query \
  --graph-query "ResourceContainers | where type == 'microsoft.resources/subscriptions' | project name, subscriptionId"

# Count resources by type
az graph query \
  --graph-query "Resources | summarize count() by type | order by count_ desc"

# Find resources without required tags
az graph query \
  --graph-query "Resources | where isnull(tags.env) | project name, type, resourceGroup, subscriptionId"

# Find public IPs
az graph query \
  --graph-query "Resources | where type == 'microsoft.network/publicipaddresses' | project name, resourceGroup, properties.ipAddress"

# Query across specific subscriptions
az graph query \
  --graph-query "Resources | where type =~ 'microsoft.storage/storageaccounts' | project name, location" \
  --subscriptions "sub-id-1" "sub-id-2"

# Output as table
az graph query \
  --graph-query "Resources | project name, type, location | limit 20" \
  --output table

# Paginate large result sets
az graph query \
  --graph-query "Resources | project name, type" \
  --first 100 \
  --skip 200
```

## ARM REST API via az rest

```bash
# --- Direct ARM REST API Calls ---
# List resource groups
az rest --method GET \
  --url "https://management.azure.com/subscriptions/{subId}/resourceGroups?api-version=2021-04-01"

# Get a specific resource
az rest --method GET \
  --url "https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?api-version=2023-09-01"

# PATCH a resource (partial update)
az rest --method PATCH \
  --url "https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?api-version=2023-09-01" \
  --body '{"tags": {"env": "prod"}}'

# Call data plane APIs
az rest --method GET \
  --url "https://myaccount.blob.core.windows.net/?comp=list" \
  --resource "https://storage.azure.com/"

# Get ARM token for scripting
TOKEN=$(az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv)
curl -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/{subId}/resourceGroups?api-version=2021-04-01"
```

## Provider Registration

```bash
# --- Resource Provider Management ---
# Register a provider (required before using a service for first time)
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.OperationalInsights

# Check registration status
az provider show --namespace Microsoft.ContainerService --query registrationState -o tsv

# List all registered providers
az provider list --query "[?registrationState=='Registered'].namespace" -o tsv

# List all providers with registration state
az provider list --output table

# Get available resource types and API versions for a provider
az provider show --namespace Microsoft.Compute \
  --query "resourceTypes[?resourceType=='virtualMachines'].{type:resourceType, apiVersions:apiVersions}" \
  -o json

# List all resource types for a namespace
az provider show --namespace Microsoft.Storage \
  --query "resourceTypes[].resourceType" -o tsv
```

## SDK Installation

```bash
# --- Python SDK ---
pip install azure-identity                          # Auth (DefaultAzureCredential, etc.)
pip install azure-mgmt-compute                     # VM/disk control plane
pip install azure-mgmt-network                     # VNet/NSG/LB control plane
pip install azure-mgmt-storage                     # Storage account control plane
pip install azure-mgmt-resource                    # Resource groups, deployments
pip install azure-mgmt-monitor                     # Metrics, logs, alerts
pip install azure-storage-blob                     # Blob storage data plane
pip install azure-storage-queue                    # Queue storage data plane
pip install azure-servicebus                       # Service Bus data plane
pip install azure-keyvault-secrets                 # Key Vault secrets data plane
pip install azure-cosmos                           # Cosmos DB data plane

# --- JavaScript/TypeScript SDK ---
npm install @azure/identity
npm install @azure/arm-compute
npm install @azure/arm-storage
npm install @azure/storage-blob
npm install @azure/service-bus
npm install @azure/keyvault-secrets

# --- .NET SDK ---
dotnet add package Azure.Identity
dotnet add package Azure.ResourceManager
dotnet add package Azure.ResourceManager.Compute
dotnet add package Azure.Storage.Blobs
dotnet add package Azure.Messaging.ServiceBus

# --- Go SDK ---
go get github.com/Azure/azure-sdk-for-go/sdk/azidentity
go get github.com/Azure/azure-sdk-for-go/sdk/resourcemanager/compute/armcompute/v5
go get github.com/Azure/azure-sdk-for-go/sdk/storage/azblob
```

## API Version Discovery

```bash
# Find latest stable API version for a resource type
az provider show \
  --namespace Microsoft.Compute \
  --query "resourceTypes[?resourceType=='virtualMachines'].apiVersions[0]" \
  -o tsv

# Find API versions for storage accounts
az provider show \
  --namespace Microsoft.Storage \
  --query "resourceTypes[?resourceType=='storageAccounts'].apiVersions" \
  -o json
```
