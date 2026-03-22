# App Modernization — CLI Reference
For service concepts, see [app-modernization-capabilities.md](app-modernization-capabilities.md).

## Azure Static Web Apps

```bash
# --- Create Static Web App from Git Repository ---
az staticwebapp create \
  --resource-group myRG \
  --name myStaticWebApp \
  --location "East US 2" \
  --source "https://github.com/myorg/myapp" \
  --branch main \
  --app-location "/" \
  --output-location "dist" \
  --api-location "api" \
  --login-with-github                          # Create SWA with GitHub Actions CI/CD

az staticwebapp create \
  --resource-group myRG \
  --name myStaticWebApp \
  --location "East US 2" \
  --sku Standard                               # Create SWA (manual deployment, no Git)

az staticwebapp list --resource-group myRG    # List static web apps
az staticwebapp show \
  --resource-group myRG \
  --name myStaticWebApp                        # Show SWA details

az staticwebapp delete \
  --resource-group myRG \
  --name myStaticWebApp --yes                  # Delete SWA

# --- Environments (Preview/Staging) ---
az staticwebapp environment list \
  --resource-group myRG \
  --name myStaticWebApp                        # List all environments (production + PRs)

az staticwebapp environment show \
  --resource-group myRG \
  --name myStaticWebApp \
  --environment-name production                # Show specific environment

az staticwebapp environment delete \
  --resource-group myRG \
  --name myStaticWebApp \
  --environment-name 12                        # Delete a PR preview environment

# --- App Settings ---
az staticwebapp appsettings set \
  --resource-group myRG \
  --name myStaticWebApp \
  --setting-names API_BASE_URL="https://api.example.com" DATABASE_URL="...secrets..."  # Set app settings

az staticwebapp appsettings list \
  --resource-group myRG \
  --name myStaticWebApp                        # List all app settings

az staticwebapp appsettings delete \
  --resource-group myRG \
  --name myStaticWebApp \
  --setting-names OLD_SETTING                  # Delete an app setting

# --- Custom Domains ---
az staticwebapp hostname set \
  --resource-group myRG \
  --name myStaticWebApp \
  --hostname "www.myapp.com"                   # Add custom domain (start domain validation)

az staticwebapp hostname list \
  --resource-group myRG \
  --name myStaticWebApp                        # List custom domains

az staticwebapp hostname delete \
  --resource-group myRG \
  --name myStaticWebApp \
  --hostname "old.myapp.com"                   # Remove custom domain

# --- Secrets (for Functions) ---
az staticwebapp secrets list \
  --resource-group myRG \
  --name myStaticWebApp                        # List deployment tokens
```

## SWA CLI (Local Development)

```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# --- Initialize ---
swa init                                       # Interactive SWA configuration wizard
swa init --yes                                 # Use defaults

# --- Local Development ---
swa start                                      # Start SWA emulator (reads swa-cli.config.json)
swa start ./dist --api-location ./api          # Start with specific paths
swa start http://localhost:3000 --api-location ./api  # Proxy to dev server (e.g., Vite/React)

# --- Deploy ---
swa login                                      # Authenticate to Azure
swa deploy \
  --app-location ./dist \
  --api-location ./api \
  --resource-group myRG \
  --app-name myStaticWebApp \
  --env production                             # Deploy to production environment

swa deploy \
  --deployment-token <token>                   # Deploy with deployment token (CI/CD)
```

## Azure Spring Apps

```bash
# Install Spring Apps extension
az extension add --name spring

# --- Spring Apps Instance ---
az spring create \
  --resource-group myRG \
  --name mySpringApps \
  --location eastus \
  --sku Standard                               # Create Azure Spring Apps (Standard tier)

az spring create \
  --resource-group myRG \
  --name myEntSpringApps \
  --location eastus \
  --sku Enterprise                             # Create Enterprise tier (Tanzu components)

az spring list --resource-group myRG          # List Spring Apps instances
az spring show --resource-group myRG --name mySpringApps  # Show instance details
az spring delete --resource-group myRG --name mySpringApps --yes  # Delete

# --- App Management ---
az spring app create \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --instance-count 2 \
  --memory 1Gi \
  --cpu 500m                                   # Create Spring app with 2 instances

az spring app create \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --assign-endpoint true                       # Create app with public endpoint

az spring app list \
  --resource-group myRG \
  --service mySpringApps                       # List apps in instance

az spring app show \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api                                # Show app status

# --- Deploy Spring Boot JAR ---
az spring app deploy \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --artifact-path ./target/my-api-1.0.0.jar   # Deploy JAR artifact

az spring app deploy \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --artifact-path ./target/my-api.jar \
  --env SPRING_PROFILES_ACTIVE=prod \
  --jvm-options "-Xmx512m"                    # Deploy with env vars and JVM options

az spring app deploy \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --source-path .                              # Build and deploy from source (using Buildpacks)

# --- Scaling ---
az spring app scale \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --instance-count 5 \
  --memory 2Gi \
  --cpu 1000m                                  # Scale to 5 instances with 2 GB RAM each

# --- Log Streaming ---
az spring app logs \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --follow                                     # Stream live logs

az spring app logs \
  --resource-group myRG \
  --service mySpringApps \
  --name my-api \
  --lines 100                                  # Show last 100 log lines

# --- Service Bindings ---
az spring connection create redis \
  --resource-group myRG \
  --service mySpringApps \
  --app my-api \
  --target-resource-group myRG \
  --server my-redis-cache \
  --database 0 \
  --client-type springBoot                     # Bind Azure Cache for Redis to Spring app

# --- Config Server ---
az spring config-server git set \
  --resource-group myRG \
  --name mySpringApps \
  --uri "https://github.com/myorg/spring-config" \
  --label main \
  --search-paths config                        # Configure Spring Cloud Config Server
```

## Azure Container Registry (for Containerization)

```bash
# --- Create ACR for migrated containerized apps ---
az acr create \
  --resource-group myRG \
  --name myMigrationACR \
  --sku Basic \
  --admin-enabled true                         # Create ACR for storing migrated app images

# Login to ACR
az acr login --name myMigrationACR

# List images pushed by containerization tool
az acr repository list --name myMigrationACR --output table

az acr repository show-tags \
  --name myMigrationACR \
  --repository my-migrated-app                 # Show image tags for an app
```

## Logic Apps (Standard Tier Migration)

```bash
# --- Logic Apps Standard ---
az logicapp create \
  --resource-group myRG \
  --name myLogicAppStd \
  --storage-account myStorageAccount \
  --plan myAppServicePlan                      # Create Logic App Standard

az logicapp list --resource-group myRG        # List Logic Apps (Standard)
az logicapp show --resource-group myRG --name myLogicAppStd  # Show details

# Deploy workflow from ZIP
az logicapp deployment source config-zip \
  --resource-group myRG \
  --name myLogicAppStd \
  --src ./workflows.zip                        # Deploy workflows from ZIP package

az logicapp start --resource-group myRG --name myLogicAppStd   # Start Logic App
az logicapp stop --resource-group myRG --name myLogicAppStd    # Stop Logic App
az logicapp delete --resource-group myRG --name myLogicAppStd --yes  # Delete
```
