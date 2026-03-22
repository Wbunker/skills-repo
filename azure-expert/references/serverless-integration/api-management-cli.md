# Azure API Management — CLI Reference
For service concepts, see [api-management-capabilities.md](api-management-capabilities.md).

## APIM Service Management

```bash
# --- Create and manage APIM instances ---
# Create an APIM instance (Developer tier for dev/test)
az apim create \
  --resource-group myRG \
  --name myApimInstance \
  --publisher-email admin@contoso.com \
  --publisher-name "Contoso API Team" \
  --sku-name Developer \
  --location eastus

# Create a Consumption tier APIM (serverless, no VNet)
az apim create \
  --resource-group myRG \
  --name myApimConsumption \
  --publisher-email admin@contoso.com \
  --publisher-name "Contoso" \
  --sku-name Consumption \
  --location eastus

# Create Premium tier with zone redundancy
az apim create \
  --resource-group myRG \
  --name myApimPremium \
  --publisher-email admin@contoso.com \
  --publisher-name "Contoso" \
  --sku-name Premium \
  --sku-capacity 2 \
  --location eastus \
  --zones 1 2 3

# List all APIM instances in a resource group
az apim list \
  --resource-group myRG \
  --query "[].{Name:name, Sku:sku.name, State:provisioningState, Location:location}" \
  --output table

# List all APIM instances in subscription
az apim list \
  --query "[].{Name:name, RG:resourceGroup, Sku:sku.name}" \
  --output table

# Show details of an APIM instance
az apim show \
  --resource-group myRG \
  --name myApimInstance

# Update APIM (e.g., update publisher email)
az apim update \
  --resource-group myRG \
  --name myApimInstance \
  --publisher-email newadmin@contoso.com

# Delete an APIM instance
az apim delete \
  --resource-group myRG \
  --name myApimInstance \
  --yes

# Check APIM service operation status
az apim check-name-availability \
  --name mydesiredapimname
```

## API Management — APIs

```bash
# --- Create APIs ---
# Create a blank REST API
az apim api create \
  --resource-group myRG \
  --service-name myApimInstance \
  --api-id orders-api \
  --display-name "Orders API" \
  --path "/orders" \
  --protocols https \
  --description "API for managing customer orders"

# Import API from OpenAPI 3.0 specification (URL)
az apim api import \
  --resource-group myRG \
  --service-name myApimInstance \
  --path "/petstore" \
  --specification-format OpenApi \
  --specification-url https://petstore3.swagger.io/api/v3/openapi.json \
  --api-id petstore-api \
  --display-name "Pet Store API"

# Import API from local OpenAPI file
az apim api import \
  --resource-group myRG \
  --service-name myApimInstance \
  --path "/orders" \
  --specification-format OpenApi \
  --specification-path ./openapi.yaml \
  --api-id orders-api

# Import API from WSDL (SOAP)
az apim api import \
  --resource-group myRG \
  --service-name myApimInstance \
  --path "/calculator" \
  --specification-format Wsdl \
  --specification-url http://www.dneonline.com/calculator.asmx?WSDL \
  --api-id calculator-soap-api \
  --api-type soap

# List APIs in an APIM instance
az apim api list \
  --resource-group myRG \
  --service-name myApimInstance \
  --query "[].{ApiId:name, DisplayName:displayName, Path:path}" \
  --output table

# Show a specific API
az apim api show \
  --resource-group myRG \
  --service-name myApimInstance \
  --api-id orders-api

# Delete an API
az apim api delete \
  --resource-group myRG \
  --service-name myApimInstance \
  --api-id orders-api \
  --yes

# --- API Operations ---
# Create an operation on an API
az apim api operation create \
  --resource-group myRG \
  --service-name myApimInstance \
  --api-id orders-api \
  --operation-id get-order-by-id \
  --display-name "Get Order by ID" \
  --method GET \
  --url-template "/orders/{orderId}" \
  --description "Retrieve a single order by its ID"

# List operations for an API
az apim api operation list \
  --resource-group myRG \
  --service-name myApimInstance \
  --api-id orders-api \
  --output table
```

## API Management — Products

```bash
# --- Products ---
# Create a product (published, requires subscription)
az apim product create \
  --resource-group myRG \
  --service-name myApimInstance \
  --product-name "Starter" \
  --product-id starter-product \
  --description "Starter plan with rate limits" \
  --state published \
  --subscription-required true \
  --subscriptions-limit 10

# Create a free, open product (no subscription required)
az apim product create \
  --resource-group myRG \
  --service-name myApimInstance \
  --product-name "Free" \
  --product-id free-product \
  --state published \
  --subscription-required false

# Add an API to a product
az apim product api add \
  --resource-group myRG \
  --service-name myApimInstance \
  --product-id starter-product \
  --api-id orders-api

# List products
az apim product list \
  --resource-group myRG \
  --service-name myApimInstance \
  --output table

# List APIs in a product
az apim product api list \
  --resource-group myRG \
  --service-name myApimInstance \
  --product-id starter-product
```

## API Management — Named Values

```bash
# Create a plain-text named value (configuration constant)
az apim nv create \
  --resource-group myRG \
  --service-name myApimInstance \
  --named-value-id backend-timeout \
  --display-name "Backend Timeout" \
  --value "30"

# Create a secret named value (masked in portal)
az apim nv create \
  --resource-group myRG \
  --service-name myApimInstance \
  --named-value-id backend-api-key \
  --display-name "Backend API Key" \
  --value "supersecretapikey123" \
  --secret true

# Create a named value backed by Key Vault secret
az apim nv create \
  --resource-group myRG \
  --service-name myApimInstance \
  --named-value-id backend-api-key \
  --display-name "Backend API Key" \
  --secret true \
  --key-vault-secret-identifier "https://myKV.vault.azure.net/secrets/BackendApiKey"

# List named values
az apim nv list \
  --resource-group myRG \
  --service-name myApimInstance \
  --query "[].{Id:name, DisplayName:displayName, Secret:secret}" \
  --output table

# Update a named value
az apim nv update \
  --resource-group myRG \
  --service-name myApimInstance \
  --named-value-id backend-api-key \
  --value "newrotatedkeyvalue"

# Delete a named value
az apim nv delete \
  --resource-group myRG \
  --service-name myApimInstance \
  --named-value-id backend-api-key \
  --yes
```

## API Management — Subscriptions & Gateway

```bash
# --- Subscriptions ---
# List all subscriptions
az apim subscriptions list \
  --resource-group myRG \
  --service-name myApimInstance \
  --query "[].{Name:name, DisplayName:displayName, ProductId:scope, State:state}" \
  --output table

# Create a subscription for a product
az apim subscriptions create \
  --resource-group myRG \
  --service-name myApimInstance \
  --display-name "Contoso App Subscription" \
  --scope "/products/starter-product" \
  --user-id /users/1

# --- Self-hosted Gateway ---
# Create a self-hosted gateway resource in APIM
az apim gateway create \
  --resource-group myRG \
  --service-name myApimInstance \
  --gateway-id my-onprem-gateway \
  --description "Self-hosted gateway for on-premises datacenter" \
  --location-data name="datacenter-east"

# List self-hosted gateways
az apim gateway list \
  --resource-group myRG \
  --service-name myApimInstance \
  --output table

# Show self-hosted gateway details
az apim gateway show \
  --resource-group myRG \
  --service-name myApimInstance \
  --gateway-id my-onprem-gateway

# Generate gateway token (for self-hosted gateway authentication)
az apim gateway token generate \
  --resource-group myRG \
  --service-name myApimInstance \
  --gateway-id my-onprem-gateway \
  --key-type primary \
  --expiry 2025-12-31T00:00:00Z

# Add an API to a self-hosted gateway
az apim gateway api add \
  --resource-group myRG \
  --service-name myApimInstance \
  --gateway-id my-onprem-gateway \
  --api-id orders-api

# List APIs on a self-hosted gateway
az apim gateway api list \
  --resource-group myRG \
  --service-name myApimInstance \
  --gateway-id my-onprem-gateway

# --- Managed Identity for APIM ---
# Assign system-assigned managed identity (for Key Vault access, backend auth)
az apim update \
  --resource-group myRG \
  --name myApimInstance \
  --enable-managed-identity true

# --- Backup and Restore ---
# Backup APIM configuration to Azure Storage
az apim backup \
  --resource-group myRG \
  --name myApimInstance \
  --backup-name apim-backup-20241201 \
  --storage-account-name myStorageAcct \
  --storage-account-container apim-backups \
  --storage-account-key $(az storage account keys list --account-name myStorageAcct --query "[0].value" -o tsv)

# Restore APIM from backup
az apim restore \
  --resource-group myRG \
  --name myApimInstance \
  --backup-name apim-backup-20241201 \
  --storage-account-name myStorageAcct \
  --storage-account-container apim-backups \
  --storage-account-key $(az storage account keys list --account-name myStorageAcct --query "[0].value" -o tsv)
```
