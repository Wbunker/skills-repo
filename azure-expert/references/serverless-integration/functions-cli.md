# Azure Functions — CLI Reference
For service concepts, see [functions-capabilities.md](functions-capabilities.md).

## Azure CLI — Function App Management

```bash
# --- Create function apps ---
# Create a Consumption plan function app (Linux, Python 3.11)
az functionapp create \
  --resource-group myRG \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name myFunctionApp \
  --storage-account myStorageAcct \
  --os-type Linux

# Create a Premium (Elastic Premium) plan function app
az functionapp create \
  --resource-group myRG \
  --plan myElasticPremiumPlan \
  --runtime node \
  --runtime-version 20 \
  --functions-version 4 \
  --name myPremiumFunctionApp \
  --storage-account myStorageAcct \
  --os-type Linux

# Create an App Service Plan first (for App Service hosted functions)
az appservice plan create \
  --resource-group myRG \
  --name myAppServicePlan \
  --sku P1v3 \
  --is-linux

# Create Flex Consumption function app
az functionapp create \
  --resource-group myRG \
  --name myFlexApp \
  --storage-account myStorageAcct \
  --flexconsumption-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4

# List all function apps in subscription
az functionapp list \
  --query "[].{Name:name, RG:resourceGroup, State:state, Location:location}" \
  --output table

# List function apps in a resource group
az functionapp list \
  --resource-group myRG \
  --output table

# Show details of a specific function app
az functionapp show \
  --resource-group myRG \
  --name myFunctionApp

# Delete a function app
az functionapp delete \
  --resource-group myRG \
  --name myFunctionApp

# --- Application Settings (Environment Variables) ---
# Set one or more app settings
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings KEY1=value1 KEY2=value2

# Set a Key Vault reference as an app setting
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings "MySecret=@Microsoft.KeyVault(SecretUri=https://myKV.vault.azure.net/secrets/mySecret/)"

# List all app settings
az functionapp config appsettings list \
  --resource-group myRG \
  --name myFunctionApp \
  --output table

# Delete an app setting
az functionapp config appsettings delete \
  --resource-group myRG \
  --name myFunctionApp \
  --setting-names KEY1

# Update function app properties (e.g., disable public access)
az functionapp update \
  --resource-group myRG \
  --name myFunctionApp \
  --set publicNetworkAccess=Disabled

# --- Networking ---
# Add VNet integration (outbound)
az functionapp vnet-integration add \
  --resource-group myRG \
  --name myFunctionApp \
  --vnet myVNet \
  --subnet mySubnet

# List VNet integrations
az functionapp vnet-integration list \
  --resource-group myRG \
  --name myFunctionApp

# Route all outbound traffic through VNet
az functionapp config appsettings set \
  --resource-group myRG \
  --name myFunctionApp \
  --settings WEBSITE_VNET_ROUTE_ALL=1

# Add IP restriction (inbound allow-list)
az functionapp config access-restriction add \
  --resource-group myRG \
  --name myFunctionApp \
  --rule-name "AllowCorporate" \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 100

# --- Managed Identity ---
# Enable system-assigned managed identity
az functionapp identity assign \
  --resource-group myRG \
  --name myFunctionApp

# Enable user-assigned managed identity
az functionapp identity assign \
  --resource-group myRG \
  --name myFunctionApp \
  --identities /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity

# Show identity details
az functionapp identity show \
  --resource-group myRG \
  --name myFunctionApp

# --- Function Keys ---
# List host-level keys for a function app
az functionapp keys list \
  --resource-group myRG \
  --name myFunctionApp

# List function-level keys for a specific function
az functionapp function keys list \
  --resource-group myRG \
  --name myFunctionApp \
  --function-name myHttpFunction

# Create or update a named function key
az functionapp function keys set \
  --resource-group myRG \
  --name myFunctionApp \
  --function-name myHttpFunction \
  --key-name myApiClient \
  --key-value "mysecretkey123"

# --- Deployment Slots ---
# Create a deployment slot
az functionapp deployment slot create \
  --resource-group myRG \
  --name myFunctionApp \
  --slot staging

# List deployment slots
az functionapp deployment slot list \
  --resource-group myRG \
  --name myFunctionApp

# Swap slots (staging → production)
az functionapp deployment slot swap \
  --resource-group myRG \
  --name myFunctionApp \
  --slot staging \
  --target-slot production

# --- ZIP Deployment ---
# Deploy a ZIP package to a function app
az functionapp deployment source config-zip \
  --resource-group myRG \
  --name myFunctionApp \
  --src ./function-package.zip

# Deploy to a specific slot
az functionapp deployment source config-zip \
  --resource-group myRG \
  --name myFunctionApp \
  --slot staging \
  --src ./function-package.zip

# --- Container Image Deployment ---
# Update function app to use a container image
az functionapp config container set \
  --resource-group myRG \
  --name myFunctionApp \
  --docker-custom-image-name myacr.azurecr.io/myfunctionimage:latest \
  --docker-registry-server-url https://myacr.azurecr.io
```

## func CLI — Local Development and Publishing

```bash
# --- Project Initialization ---
# Initialize a new Functions project (Python v2 model)
func init myProject --worker-runtime python --model V2

# Initialize a Node.js project (v4 model)
func init myProject --worker-runtime node --language typescript

# Initialize a .NET isolated worker project
func init myProject --worker-runtime dotnet-isolated

# Create a new function in the current project
func new --name MyHttpTrigger --template "HTTP trigger" --authlevel anonymous

# Create a timer-triggered function
func new --name MyTimerTrigger --template "Timer trigger"

# Create a Blob Storage triggered function
func new --name MyBlobTrigger --template "Blob trigger"

# --- Local Run ---
# Start the local Functions runtime (uses local.settings.json)
func start

# Start with a specific port
func start --port 7072

# Start and watch for file changes
func start --verbose

# --- Publish to Azure ---
# Publish function app to Azure (builds and deploys)
func azure functionapp publish myFunctionApp

# Publish with remote build (dependencies installed in Azure)
func azure functionapp publish myFunctionApp --build remote

# Publish without bundler (for Python, install dependencies first)
func azure functionapp publish myFunctionApp --no-build

# Publish to a specific slot
func azure functionapp publish myFunctionApp --slot staging

# --- Log Streaming ---
# Stream live logs from a function app
func azure functionapp logstream myFunctionApp

# Stream logs filtered to a specific function
func azure functionapp logstream myFunctionApp --filter MyHttpTrigger
```
