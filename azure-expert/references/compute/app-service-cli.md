# Azure App Service — CLI Reference

For service concepts, see [app-service-capabilities.md](app-service-capabilities.md).

## App Service Plan

```bash
# --- Create App Service Plan ---
# Linux Premium v3 plan (recommended for production)
az appservice plan create \
  --resource-group myRG \
  --name myPlan \
  --location eastus \
  --sku P1v3 \
  --is-linux

# Windows Standard plan
az appservice plan create \
  --resource-group myRG \
  --name myWinPlan \
  --location eastus \
  --sku S2

# Zone-redundant plan (requires Premium v3 or Isolated v2)
az appservice plan create \
  --resource-group myRG \
  --name myZonePlan \
  --location eastus \
  --sku P2v3 \
  --is-linux \
  --zone-redundant

# List App Service Plans
az appservice plan list --resource-group myRG --output table

# Update plan SKU
az appservice plan update \
  --resource-group myRG \
  --name myPlan \
  --sku P2v3

# Delete plan
az appservice plan delete --resource-group myRG --name myPlan --yes
```

---

## Web App — Create and Manage

```bash
# --- Create Web App ---
# Python app on Linux
az webapp create \
  --resource-group myRG \
  --plan myPlan \
  --name myWebApp \
  --runtime "PYTHON:3.12"

# .NET 8 app on Linux
az webapp create \
  --resource-group myRG \
  --plan myPlan \
  --name myDotNetApp \
  --runtime "DOTNETCORE:8.0"

# Node.js app on Linux
az webapp create \
  --resource-group myRG \
  --plan myPlan \
  --name myNodeApp \
  --runtime "NODE:20-lts"

# Container from Azure Container Registry
az webapp create \
  --resource-group myRG \
  --plan myPlan \
  --name myContainerApp \
  --deployment-container-image-name myacr.azurecr.io/myapp:latest

# List available runtimes
az webapp list-runtimes --os-type linux
az webapp list-runtimes --os-type windows

# List web apps
az webapp list --resource-group myRG --output table

# Show web app details
az webapp show --resource-group myRG --name myWebApp

# Delete web app
az webapp delete --resource-group myRG --name myWebApp
```

---

## Web App — Configuration

```bash
# --- Application Settings ---
# Set individual app settings (environment variables)
az webapp config appsettings set \
  --resource-group myRG \
  --name myWebApp \
  --settings DATABASE_URL="postgresql://..." NODE_ENV="production"

# Set a Key Vault reference (passwordless secrets)
az webapp config appsettings set \
  --resource-group myRG \
  --name myWebApp \
  --settings "MY_SECRET=@Microsoft.KeyVault(VaultName=myVault;SecretName=mySecret)"

# List app settings
az webapp config appsettings list --resource-group myRG --name myWebApp

# Delete an app setting
az webapp config appsettings delete \
  --resource-group myRG \
  --name myWebApp \
  --setting-names MY_SECRET

# --- Connection Strings ---
az webapp config connection-string set \
  --resource-group myRG \
  --name myWebApp \
  --connection-string-type SQLAzure \
  --settings MyDb="Server=tcp:myserver.database.windows.net;..."

# --- General Settings ---
# Enable Always On, set min TLS, enable HTTPS only
az webapp config set \
  --resource-group myRG \
  --name myWebApp \
  --always-on true \
  --min-tls-version 1.2 \
  --ftps-state Disabled \
  --http20-enabled true

# Set startup command (Linux)
az webapp config set \
  --resource-group myRG \
  --name myWebApp \
  --startup-file "gunicorn --bind 0.0.0.0:8000 app:app"

# Enable HTTPS only
az webapp update \
  --resource-group myRG \
  --name myWebApp \
  --https-only true
```

---

## Web App — Deployment Slots

```bash
# --- Create Deployment Slot ---
az webapp deployment slot create \
  --resource-group myRG \
  --name myWebApp \
  --slot staging

# List slots
az webapp deployment slot list --resource-group myRG --name myWebApp --output table

# Set app settings on a slot
az webapp config appsettings set \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --settings ENVIRONMENT=staging

# Deploy to staging slot (ZIP deploy)
az webapp deploy \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --src-path ./dist.zip \
  --type zip

# Swap staging to production
az webapp deployment slot swap \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --target-slot production

# Preview swap (phase 1 only — warms up but doesn't swap)
az webapp deployment slot swap \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --action preview

# Complete a swap preview
az webapp deployment slot swap \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --action swap

# Route 10% of traffic to staging for canary testing
az webapp traffic-routing set \
  --resource-group myRG \
  --name myWebApp \
  --distribution staging=10

# Clear traffic routing (100% to production)
az webapp traffic-routing clear --resource-group myRG --name myWebApp

# Delete slot
az webapp deployment slot delete \
  --resource-group myRG \
  --name myWebApp \
  --slot staging
```

---

## Web App — Deploy

```bash
# ZIP deploy (CI/CD standard approach)
az webapp deploy \
  --resource-group myRG \
  --name myWebApp \
  --src-path ./app.zip \
  --type zip

# Deploy from a URL
az webapp deploy \
  --resource-group myRG \
  --name myWebApp \
  --src-url https://mystorageaccount.blob.core.windows.net/artifacts/app.zip \
  --type zip

# Deploy a WAR file (Java / Tomcat)
az webapp deploy \
  --resource-group myRG \
  --name myJavaApp \
  --src-path ./target/myapp.war \
  --type war

# Update container image for a container-based web app
az webapp config container set \
  --resource-group myRG \
  --name myContainerApp \
  --container-image-name myacr.azurecr.io/myapp:v2.0.0 \
  --container-registry-url https://myacr.azurecr.io

# Configure continuous deployment from ACR
az webapp deployment container config \
  --resource-group myRG \
  --name myContainerApp \
  --enable-cd true
```

---

## Web App — Logging

```bash
# Enable application logging (filesystem — temporary, 12 hours)
az webapp log config \
  --resource-group myRG \
  --name myWebApp \
  --application-logging filesystem \
  --level information

# Enable web server logging
az webapp log config \
  --resource-group myRG \
  --name myWebApp \
  --web-server-logging filesystem

# Stream live logs to terminal
az webapp log tail --resource-group myRG --name myWebApp

# Download logs as ZIP
az webapp log download \
  --resource-group myRG \
  --name myWebApp \
  --log-file logs.zip

# Show log configuration
az webapp log show --resource-group myRG --name myWebApp
```

---

## Web App — Networking

```bash
# --- VNet Integration (outbound) ---
az webapp vnet-integration add \
  --resource-group myRG \
  --name myWebApp \
  --vnet myVNet \
  --subnet myAppSubnet

az webapp vnet-integration list --resource-group myRG --name myWebApp

az webapp vnet-integration remove --resource-group myRG --name myWebApp

# --- IP Restrictions (inbound) ---
# Add an IP restriction rule (allow only specific CIDR)
az webapp config access-restriction add \
  --resource-group myRG \
  --name myWebApp \
  --rule-name AllowOffice \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 100

# Allow Front Door Service Tag (front-end via Front Door only)
az webapp config access-restriction add \
  --resource-group myRG \
  --name myWebApp \
  --rule-name AllowFrontDoor \
  --action Allow \
  --service-tag AzureFrontDoor.Backend \
  --priority 200

# Show access restrictions
az webapp config access-restriction show --resource-group myRG --name myWebApp

# --- Private Endpoint ---
az network private-endpoint create \
  --resource-group myRG \
  --name myWebAppPE \
  --vnet-name myVNet \
  --subnet myEndpointSubnet \
  --private-connection-resource-id /subscriptions/.../sites/myWebApp \
  --group-id sites \
  --connection-name myWebAppConn
```

---

## Web App — Authentication (EasyAuth)

```bash
# Enable Entra ID (AAD) authentication
az webapp auth update \
  --resource-group myRG \
  --name myWebApp \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-allowed-token-audiences https://mywebapp.azurewebsites.net

# Show auth configuration
az webapp auth show --resource-group myRG --name myWebApp

# Configure via auth config V2 (newer API)
az webapp auth config-version upgrade --resource-group myRG --name myWebApp

# Disable authentication
az webapp auth update --resource-group myRG --name myWebApp --enabled false
```

---

## Web App — Managed Identity

```bash
# Enable system-assigned managed identity
az webapp identity assign \
  --resource-group myRG \
  --name myWebApp

# Assign user-assigned managed identity
az webapp identity assign \
  --resource-group myRG \
  --name myWebApp \
  --identities /subscriptions/.../userAssignedIdentities/myIdentity

# Show identity
az webapp identity show --resource-group myRG --name myWebApp

# Grant the web app identity access to Key Vault
appPrincipalId=$(az webapp identity show -g myRG -n myWebApp --query principalId -o tsv)
az keyvault set-policy \
  --name myKeyVault \
  --object-id $appPrincipalId \
  --secret-permissions get list
```
