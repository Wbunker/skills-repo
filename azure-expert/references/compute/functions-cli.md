# Azure Functions — CLI Reference

For service concepts, see [functions-capabilities.md](functions-capabilities.md).

## Function App — Create and Manage

```bash
# --- Create Function App (Consumption plan, Linux, Python) ---
az functionapp create \
  --resource-group myRG \
  --name myFunctionApp \
  --storage-account mystorageaccount \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.12 \
  --os-type linux \
  --functions-version 4

# Create Function App on Flex Consumption plan (recommended for production)
az functionapp create \
  --resource-group myRG \
  --name myFunctionApp \
  --storage-account mystorageaccount \
  --flexconsumption-location eastus \
  --runtime python \
  --runtime-version 3.12 \
  --functions-version 4

# Create Function App on Premium plan (pre-created EP plan required)
az appservice plan create \
  --resource-group myRG \
  --name myPremiumPlan \
  --location eastus \
  --sku EP1 \
  --is-linux

az functionapp create \
  --resource-group myRG \
  --name myFunctionApp \
  --plan myPremiumPlan \
  --storage-account mystorageaccount \
  --runtime node \
  --runtime-version 20 \
  --functions-version 4

# Create Function App with .NET isolated runtime (Windows)
az functionapp create \
  --resource-group myRG \
  --name myDotNetFunctionApp \
  --storage-account mystorageaccount \
  --consumption-plan-location eastus \
  --runtime dotnet-isolated \
  --runtime-version 8 \
  --os-type windows \
  --functions-version 4

# Create container-based Function App
az functionapp create \
  --resource-group myRG \
  --name myContainerFunctionApp \
  --plan myPremiumPlan \
  --storage-account mystorageaccount \
  --deployment-container-image-name myacr.azurecr.io/myfunc:latest \
  --docker-registry-server-url https://myacr.azurecr.io

# List function apps
az functionapp list --resource-group myRG --output table

# Show function app details
az functionapp show --resource-group myRG --name myFunctionApp

# Delete function app
az functionapp delete --resource-group myRG --name myFunctionApp
```

---

## Function App — Configuration

```bash
# --- Application Settings ---
# Set app settings (environment variables)
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings MY_SETTING=value SERVICE_BUS_CONNECTION="Endpoint=sb://..."

# Set Key Vault reference
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings "MY_SECRET=@Microsoft.KeyVault(VaultName=myVault;SecretName=mySecret)"

# List app settings
az functionapp config appsettings list --resource-group myRG --name myFunctionApp

# Delete app settings
az functionapp config appsettings delete \
  --resource-group myRG \
  --name myFunctionApp \
  --setting-names MY_SETTING

# --- CORS ---
# Add an allowed origin
az functionapp cors add \
  --resource-group myRG \
  --name myFunctionApp \
  --allowed-origins https://myfrontend.azurestaticapps.net

# Show CORS config
az functionapp cors show --resource-group myRG --name myFunctionApp

# Remove an allowed origin
az functionapp cors remove \
  --resource-group myRG \
  --name myFunctionApp \
  --allowed-origins https://oldfrontend.example.com
```

---

## Function App — Keys

```bash
# --- Function Keys ---
# List function-level keys for a specific function
az functionapp function keys list \
  --resource-group myRG \
  --name myFunctionApp \
  --function-name myHttpFunction

# Create or update a function key
az functionapp function keys set \
  --resource-group myRG \
  --name myFunctionApp \
  --function-name myHttpFunction \
  --key-name myClientKey \
  --key-value mySecretKeyValue

# Delete a function key
az functionapp function keys delete \
  --resource-group myRG \
  --name myFunctionApp \
  --function-name myHttpFunction \
  --key-name myClientKey

# --- Host Keys (app-level, apply to all functions) ---
az functionapp keys list \
  --resource-group myRG \
  --name myFunctionApp

# Set a host key
az functionapp keys set \
  --resource-group myRG \
  --name myFunctionApp \
  --key-name mySharedKey \
  --key-type functionKeys \
  --key-value mySharedSecret

# Regenerate default host key
az functionapp keys set \
  --resource-group myRG \
  --name myFunctionApp \
  --key-name default \
  --key-type masterKey
```

---

## Function App — Managed Identity

```bash
# Enable system-assigned managed identity
az functionapp identity assign \
  --resource-group myRG \
  --name myFunctionApp

# Assign user-assigned managed identity
az functionapp identity assign \
  --resource-group myRG \
  --name myFunctionApp \
  --identities /subscriptions/.../userAssignedIdentities/myIdentity

# Show identity
az functionapp identity show --resource-group myRG --name myFunctionApp

# Grant function app identity access to Service Bus (for identity-based connections)
funcPrincipalId=$(az functionapp identity show -g myRG -n myFunctionApp --query principalId -o tsv)
sbNamespaceId=$(az servicebus namespace show -g myRG -n myServiceBusNamespace --query id -o tsv)
az role assignment create \
  --assignee $funcPrincipalId \
  --role "Azure Service Bus Data Receiver" \
  --scope $sbNamespaceId

# Grant access to Storage Account (for identity-based AzureWebJobsStorage)
storageId=$(az storage account show -g myRG -n mystorageaccount --query id -o tsv)
az role assignment create \
  --assignee $funcPrincipalId \
  --role "Storage Blob Data Contributor" \
  --scope $storageId
```

---

## Function App — Deploy

```bash
# Deploy using Azure Functions Core Tools
func azure functionapp publish myFunctionApp

# Deploy and build remotely on Azure (for Python/Node.js without local build)
func azure functionapp publish myFunctionApp --build remote

# Deploy a pre-built ZIP using az CLI
az functionapp deploy \
  --resource-group myRG \
  --name myFunctionApp \
  --src-path ./function_app.zip \
  --type zip

# Deploy a container image update
az functionapp config container set \
  --resource-group myRG \
  --name myContainerFunctionApp \
  --image myacr.azurecr.io/myfunc:v2.0.0

# Enable run-from-package (recommended for Consumption plans)
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings WEBSITE_RUN_FROM_PACKAGE=1
```

---

## Azure Functions Core Tools (func)

```bash
# Initialize a new function app project
func init myFunctionProject --worker-runtime python
func init myFunctionProject --worker-runtime dotnet-isolated
func init myFunctionProject --worker-runtime node --language typescript

# Create a new function in the project
func new --name MyHttpFunction --template "HTTP trigger" --authlevel anonymous
func new --name MyTimerFunction --template "Timer trigger"
func new --name MyBlobFunction --template "Azure Blob Storage trigger"
func new --name MyServiceBusFunction --template "Azure Service Bus Queue trigger"
func new --name MyEventHubFunction --template "Azure Event Hub trigger"

# Run function app locally
func start
func start --port 7072

# Run with local Azure Storage emulation (Azurite)
func start --port 7071

# Deploy to Azure from Core Tools
func azure functionapp publish myFunctionApp
func azure functionapp publish myFunctionApp --build remote --force

# List functions in an app
func azure functionapp list-functions myFunctionApp
```

---

## Durable Functions — Management

```bash
# Install Durable Functions extension (in project)
func extensions install --package Microsoft.Azure.WebJobs.Extensions.DurableTask

# Query orchestration instance status
az rest \
  --method GET \
  --uri "https://myFunctionApp.azurewebsites.net/runtime/webhooks/durabletask/instances/{instanceId}?code={masterKey}"

# Terminate an orchestration
az rest \
  --method DELETE \
  --uri "https://myFunctionApp.azurewebsites.net/runtime/webhooks/durabletask/instances/{instanceId}/terminate?reason=manual&code={masterKey}"
```

---

## Function App — Scaling and Performance

```bash
# Set maximum scale-out for Consumption plan
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings WEBSITE_MAX_DYNAMIC_APPLICATION_SCALE_OUT=50

# Configure pre-provisioned instances (Flex Consumption)
az functionapp scale config set \
  --resource-group myRG \
  --name myFunctionApp \
  --maximum-instance-count 100 \
  --instance-memory 2048

# Configure always-ready instances (Flex Consumption)
az functionapp scale config always-ready set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings myHttpFunction=2

# Show scaling config
az functionapp scale config show --resource-group myRG --name myFunctionApp

# Show function app logs (streaming)
az webapp log tail --resource-group myRG --name myFunctionApp
```
