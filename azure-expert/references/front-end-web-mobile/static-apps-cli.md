# Static Web Apps & App Service — CLI Reference
For service concepts, see [static-apps-capabilities.md](static-apps-capabilities.md).

## Azure Static Web Apps

```bash
# --- Create Static Web App ---
# From GitHub repository (auto-creates GitHub Actions workflow)
az staticwebapp create \
  --resource-group myRG \
  --name myStaticApp \
  --location "East US 2" \
  --source "https://github.com/myorg/myapp" \
  --branch main \
  --app-location "/" \
  --output-location "dist" \
  --api-location "api" \
  --login-with-github                          # Interactive GitHub auth

# Create with Azure DevOps source
az staticwebapp create \
  --resource-group myRG \
  --name myStaticApp \
  --location "East US 2" \
  --source "https://dev.azure.com/myorg/myproject/_git/myrepo" \
  --branch main \
  --app-location "/" \
  --output-location "build" \
  --login-with-ado

# Create empty SWA (manual/CLI deployment)
az staticwebapp create \
  --resource-group myRG \
  --name myStaticApp \
  --location "East US 2" \
  --sku Standard                               # Standard tier for production

az staticwebapp list --resource-group myRG    # List all static web apps
az staticwebapp show --resource-group myRG --name myStaticApp  # Show details

az staticwebapp delete \
  --resource-group myRG \
  --name myStaticApp \
  --no-wait --yes                              # Delete SWA

# --- Environments ---
az staticwebapp environment list \
  --resource-group myRG \
  --name myStaticApp                           # List all environments (production + PR previews)

az staticwebapp environment show \
  --resource-group myRG \
  --name myStaticApp \
  --environment-name default                   # Show production environment

az staticwebapp environment delete \
  --resource-group myRG \
  --name myStaticApp \
  --environment-name 42                        # Delete PR #42 preview environment

# --- App Settings ---
az staticwebapp appsettings set \
  --resource-group myRG \
  --name myStaticApp \
  --setting-names \
    API_KEY="abc123" \
    BACKEND_URL="https://api.example.com" \
    FEATURE_FLAG="true"                        # Set multiple app settings

az staticwebapp appsettings list \
  --resource-group myRG \
  --name myStaticApp                           # List all app settings

az staticwebapp appsettings delete \
  --resource-group myRG \
  --name myStaticApp \
  --setting-names DEPRECATED_SETTING           # Delete app setting

# --- Custom Domains ---
az staticwebapp hostname set \
  --resource-group myRG \
  --name myStaticApp \
  --hostname "www.myapp.com"                   # Add custom domain (CNAME or A record)

az staticwebapp hostname set \
  --resource-group myRG \
  --name myStaticApp \
  --hostname "myapp.com"                       # Apex domain (requires TXT record validation)

az staticwebapp hostname list \
  --resource-group myRG \
  --name myStaticApp                           # List custom domains and validation status

az staticwebapp hostname delete \
  --resource-group myRG \
  --name myStaticApp \
  --hostname "old.myapp.com"                   # Remove custom domain

# --- Secrets/Deployment Token ---
az staticwebapp secrets list \
  --resource-group myRG \
  --name myStaticApp                           # Get deployment token (for CI/CD)

az staticwebapp secrets reset-api-key \
  --resource-group myRG \
  --name myStaticApp                           # Rotate deployment token

# --- Backend (Linked Functions) ---
az staticwebapp backends link \
  --resource-group myRG \
  --name myStaticApp \
  --environment-name default \
  --backend-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Web/sites/myFunctionApp  # Link existing Functions app

az staticwebapp backends show \
  --resource-group myRG \
  --name myStaticApp \
  --environment-name default                   # Show linked backend

az staticwebapp backends unlink \
  --resource-group myRG \
  --name myStaticApp \
  --environment-name default                   # Remove linked backend
```

## SWA CLI (Local Development)

```bash
# --- Install ---
npm install -g @azure/static-web-apps-cli

# --- Initialize Project ---
swa init                                       # Interactive setup wizard; creates swa-cli.config.json
swa init --yes                                 # Accept all defaults

# --- Local Development ---
swa start                                      # Start emulator with config from swa-cli.config.json

swa start ./dist \
  --api-location ./api                         # Serve built files with Functions emulator

swa start http://localhost:3000 \
  --api-location ./api                         # Proxy to Vite/webpack dev server

swa start http://localhost:3000 \
  --api-location http://localhost:7071         # Proxy both frontend and existing Functions

# --- Authentication Emulation (local) ---
swa start ./dist \
  --api-location ./api \
  --swa-config-location .                      # Load staticwebapp.config.json for auth rules

# Simulate logged-in user: navigate to /.auth/login/github in browser during local dev

# --- Deploy ---
swa login \
  --tenant-id <tenantId> \
  --client-id <clientId> \
  --client-secret <secret>                     # Service principal auth (for CI/CD)

swa login                                      # Interactive browser login

swa deploy \
  --app-location ./dist \
  --api-location ./api \
  --resource-group myRG \
  --app-name myStaticApp \
  --env production                             # Deploy to production

swa deploy \
  --app-location ./dist \
  --deployment-token <token>                   # Deploy using deployment token (CI/CD)

swa deploy \
  --app-location ./dist \
  --env staging                                # Deploy to named staging environment

# Build and deploy in one command
swa build && swa deploy

# --- Config Validation ---
swa validate --config-file ./staticwebapp.config.json  # Validate config file
```

## Azure App Service

```bash
# --- App Service Plan ---
az appservice plan create \
  --resource-group myRG \
  --name myAppPlan \
  --location eastus \
  --sku P2v3 \
  --is-linux                                   # Create Premium v3 Linux plan

az appservice plan create \
  --resource-group myRG \
  --name myWindowsPlan \
  --location eastus \
  --sku S2                                     # Windows Standard plan

az appservice plan list --resource-group myRG --output table  # List plans
az appservice plan show --resource-group myRG --name myAppPlan

az appservice plan update \
  --resource-group myRG \
  --name myAppPlan \
  --sku P3v3                                   # Scale up plan

az appservice plan delete \
  --resource-group myRG \
  --name myAppPlan --yes                       # Delete plan

# --- Web App ---
az webapp create \
  --resource-group myRG \
  --plan myAppPlan \
  --name myWebApp \
  --runtime "NODE:20-lts"                      # Create Node.js web app

az webapp create \
  --resource-group myRG \
  --plan myAppPlan \
  --name myPythonApp \
  --runtime "PYTHON:3.12"                      # Create Python web app

az webapp create \
  --resource-group myRG \
  --plan myAppPlan \
  --name myDotNetApp \
  --runtime "DOTNET:8"                         # Create .NET 8 web app

az webapp create \
  --resource-group myRG \
  --plan myAppPlan \
  --name myContainerApp \
  --deployment-container-image-name myacr.azurecr.io/myapp:latest  # Create from container

az webapp list --resource-group myRG --output table
az webapp show --resource-group myRG --name myWebApp

az webapp delete --resource-group myRG --name myWebApp --yes

# --- Deployment ---
az webapp deployment source config-zip \
  --resource-group myRG \
  --name myWebApp \
  --src ./app.zip                              # Deploy from ZIP file

az webapp up \
  --resource-group myRG \
  --name myWebApp \
  --runtime "NODE:20-lts" \
  --location eastus                            # Build and deploy from current directory

az webapp deployment source config \
  --resource-group myRG \
  --name myWebApp \
  --repo-url "https://github.com/myorg/myapp" \
  --branch main \
  --manual-integration                         # Configure Git deployment

# --- Deployment Slots ---
az webapp deployment slot create \
  --resource-group myRG \
  --name myWebApp \
  --slot staging                               # Create staging slot

az webapp deployment source config-zip \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --src ./app.zip                              # Deploy to staging slot

az webapp deployment slot swap \
  --resource-group myRG \
  --name myWebApp \
  --slot staging \
  --target-slot production                     # Swap staging to production

az webapp deployment slot list \
  --resource-group myRG \
  --name myWebApp                              # List all slots

az webapp deployment slot delete \
  --resource-group myRG \
  --name myWebApp \
  --slot staging                               # Delete slot

# --- Configuration ---
az webapp config appsettings set \
  --resource-group myRG \
  --name myWebApp \
  --settings NODE_ENV=production MONGODB_URI=mongodb://...  # Set app settings

az webapp config appsettings list \
  --resource-group myRG \
  --name myWebApp                              # List app settings

az webapp config connection-string set \
  --resource-group myRG \
  --name myWebApp \
  --settings DefaultConnection="Server=...;Database=..." \
  --connection-string-type SQLAzure            # Set connection strings

# --- Scaling ---
az webapp config set \
  --resource-group myRG \
  --name myWebApp \
  --number-of-workers 3                        # Set instance count (manual scale)

az monitor autoscale create \
  --resource-group myRG \
  --resource myWebApp \
  --resource-type Microsoft.Web/sites \
  --name myAppAutoscale \
  --min-count 2 --max-count 10 --count 2      # Create autoscale setting

# --- Logging ---
az webapp log config \
  --resource-group myRG \
  --name myWebApp \
  --application-logging filesystem \
  --level information                          # Enable app logging

az webapp log tail \
  --resource-group myRG \
  --name myWebApp                              # Stream live logs

az webapp log download \
  --resource-group myRG \
  --name myWebApp                              # Download log archive
```
