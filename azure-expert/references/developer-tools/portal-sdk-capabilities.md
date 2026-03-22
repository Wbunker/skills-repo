# Azure Portal & SDKs — Capabilities Reference
For CLI commands, see [portal-sdk-cli.md](portal-sdk-cli.md).

## Azure Portal

**Purpose**: Unified web-based management interface for all Azure services. Available at portal.azure.com. Provides visual resource management, monitoring dashboards, access control, and integrated Cloud Shell.

### Key Portal Features

| Feature | Description |
|---|---|
| **Customizable dashboards** | Pin tiles (metrics charts, resource lists, markdown) to personal or shared dashboards; export/import as JSON |
| **Resource groups view** | See all resources in a group with cost, health, and activity log |
| **Global search** | Search by resource name, type, or documentation across subscriptions |
| **Integrated Cloud Shell** | Full bash/PowerShell terminal embedded in portal; persistent `$HOME` via Azure Files |
| **Cost Analysis** | Subscription/resource group/resource-level cost breakdown with filters, grouping, and forecast |
| **Access Control (IAM)** | Assign RBAC roles at any scope; view effective permissions; manage PIM (Privileged Identity Management) |
| **Activity Log** | Audit trail of all management plane operations (ARM operations) with 90-day retention |
| **Resource Health** | Per-resource health status and history; integrates with Azure Service Health |
| **Support requests** | Create and track Azure support tickets; embedded diagnostics |
| **Preview features** | Enable experimental features via `portal.azure.com/?feature.<name>=true` query params or Preview Hub |
| **Azure Advisor** | Recommendations for cost, security, reliability, performance, and operational excellence |
| **Resource Graph Explorer** | Run KQL (Kusto Query Language) queries against all Azure resources from the portal |

---

## Azure Resource Explorer

**Purpose**: Low-level JSON browser for every Azure resource, exposing raw ARM API representations. Useful for discovering available properties, API versions, and valid parameter values before writing code or templates.

- URL: `resources.azure.com`
- Navigate the tree: Subscriptions → Resource Groups → Providers → Resource Types → Instances
- View full JSON of any resource as returned by the ARM REST API
- Identify `apiVersion` to use in ARM templates and SDK calls
- See read/write property availability for PATCH vs PUT operations
- Make live GET/PUT/POST/DELETE calls against resources (use with caution)

---

## Azure SDKs

**Purpose**: Language-native client libraries for interacting with Azure services. Split into **control plane** (manage Azure resources — create/update/delete) and **data plane** (interact with service functionality — read blobs, send messages, etc.).

### SDK Architecture Pattern

| Plane | Description | Auth |
|---|---|---|
| **Control plane** | Manage Azure resources via ARM REST API | Azure AD token to `management.azure.com` |
| **Data plane** | Use service functionality | Azure AD token or service-specific key to service endpoint |

### Python SDK

```python
# Install
pip install azure-identity azure-mgmt-compute azure-mgmt-network azure-mgmt-storage

# Control plane: manage resources
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscription_id)
vms = list(compute_client.virtual_machines.list_all())

# Data plane: interact with service
from azure.storage.blob import BlobServiceClient
blob_client = BlobServiceClient(account_url, credential=credential)
```

| Package Pattern | Purpose |
|---|---|
| `azure-mgmt-*` | Control plane (resource management) |
| `azure-*` (non-mgmt) | Data plane (e.g., `azure-storage-blob`, `azure-servicebus`) |
| `azure-identity` | Authentication (`DefaultAzureCredential`, etc.) |

### .NET SDK

```csharp
// Install NuGet packages
// dotnet add package Azure.Identity
// dotnet add package Azure.ResourceManager.Compute

using Azure.Identity;
using Azure.ResourceManager;

var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);
var subscription = await armClient.GetDefaultSubscriptionAsync();
```

| Package Pattern | Purpose |
|---|---|
| `Azure.ResourceManager.*` | Control plane |
| `Azure.*` (non-ResourceManager) | Data plane (e.g., `Azure.Storage.Blobs`, `Azure.Messaging.ServiceBus`) |
| `Azure.Identity` | Authentication |

### Java SDK

| Package Pattern | Purpose |
|---|---|
| `com.azure:azure-resourcemanager` | Control plane (unified package for all resource managers) |
| `com.azure:azure-*` (data plane) | e.g., `azure-storage-blob`, `azure-messaging-servicebus` |
| `com.azure:azure-identity` | Authentication |

```java
// Maven dependency
// <dependency><groupId>com.azure</groupId><artifactId>azure-identity</artifactId></dependency>
TokenCredential credential = new DefaultAzureCredentialBuilder().build();
AzureResourceManager azure = AzureResourceManager.authenticate(credential, profile).withDefaultSubscription();
```

### JavaScript / TypeScript SDK

| Package Pattern | Purpose |
|---|---|
| `@azure/arm-*` | Control plane (e.g., `@azure/arm-compute`, `@azure/arm-storage`) |
| `@azure/*` (non-arm) | Data plane (e.g., `@azure/storage-blob`, `@azure/service-bus`) |
| `@azure/identity` | Authentication |

```typescript
import { DefaultAzureCredential } from "@azure/identity";
import { ComputeManagementClient } from "@azure/arm-compute";

const credential = new DefaultAzureCredential();
const client = new ComputeManagementClient(credential, subscriptionId);
```

### Go SDK

```go
// go get github.com/Azure/azure-sdk-for-go/sdk/azidentity
// go get github.com/Azure/azure-sdk-for-go/sdk/resourcemanager/compute/armcompute

import (
    "github.com/Azure/azure-sdk-for-go/sdk/azidentity"
    "github.com/Azure/azure-sdk-for-go/sdk/resourcemanager/compute/armcompute/v5"
)

cred, _ := azidentity.NewDefaultAzureCredential(nil)
client, _ := armcompute.NewVirtualMachinesClient(subscriptionID, cred, nil)
```

---

## DefaultAzureCredential

**Purpose**: The recommended credential type for all production Azure code. Tries multiple authentication methods in order, enabling the same code to run locally (using CLI auth) and in production (using Managed Identity) without modification.

### Authentication Chain (in order)

| Method | When Used |
|---|---|
| **EnvironmentCredential** | `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET` (or cert/OIDC token) set |
| **WorkloadIdentityCredential** | `AZURE_FEDERATED_TOKEN_FILE` set (AKS Workload Identity) |
| **ManagedIdentityCredential** | Running on Azure resource with managed identity enabled |
| **SharedTokenCacheCredential** | Visual Studio token cache (Windows) |
| **VisualStudioCodeCredential** | VS Code Azure Account extension signed in |
| **AzureCliCredential** | `az login` has been run |
| **AzurePowerShellCredential** | `Connect-AzAccount` has been run |
| **InteractiveBrowserCredential** | Falls through to browser prompt (if enabled) |

---

## ARM REST API

**Purpose**: The underlying REST API that all Azure SDKs, CLI, and Portal use. Useful for direct HTTP access, discovering new APIs, and troubleshooting.

### Key Concepts

| Concept | Details |
|---|---|
| **Base URL** | `https://management.azure.com` |
| **Auth header** | `Authorization: Bearer <token>` (Azure AD token) |
| **API version** | Every request requires `?api-version=YYYY-MM-DD` parameter |
| **Long-running operations** | `202 Accepted` response + `Location` / `Azure-AsyncOperation` header for polling |
| **Resource URL pattern** | `/subscriptions/{subId}/resourceGroups/{rg}/providers/{namespace}/{type}/{name}` |

```bash
# Example: list VMs via ARM REST API using az rest
az rest --method GET \
  --url "https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines?api-version=2023-09-01"
```

---

## Azure Resource Graph

**Purpose**: Query all Azure resources across subscriptions at scale using Kusto Query Language (KQL). Returns results in seconds even across thousands of subscriptions.

```kusto
-- Find all VMs in eastus
Resources
| where type =~ 'microsoft.compute/virtualmachines'
| where location == 'eastus'
| project name, resourceGroup, location, properties.hardwareProfile.vmSize

-- Find resources without tags
Resources
| where isnull(tags) or array_length(bag_keys(tags)) == 0
| project name, type, resourceGroup

-- Count resources by type
Resources
| summarize count() by type
| order by count_ desc
```

### API Version Discovery

```bash
# Find valid API versions for a resource type
az provider show \
  --namespace Microsoft.Compute \
  --query "resourceTypes[?resourceType=='virtualMachines'].apiVersions[]" \
  -o tsv

# List all resource types for a provider
az provider show --namespace Microsoft.Storage \
  --query "resourceTypes[].resourceType" -o tsv
```
