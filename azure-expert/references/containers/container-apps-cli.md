# Azure Container Apps — CLI Reference
For service concepts, see [container-apps-capabilities.md](container-apps-capabilities.md).

## Environment Management

```bash
# --- Create environments ---
# Create a basic Container Apps environment (no custom VNet)
az containerapp env create \
  --resource-group myRG \
  --name myContainerAppEnv \
  --location eastus

# Create environment with Log Analytics workspace
az containerapp env create \
  --resource-group myRG \
  --name myContainerAppEnv \
  --location eastus \
  --logs-workspace-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace \
  --logs-workspace-key $(az monitor log-analytics workspace get-shared-keys --resource-group myRG --workspace-name myWorkspace --query primarySharedKey -o tsv)

# Create environment with custom VNet injection (workload profiles)
az containerapp env create \
  --resource-group myRG \
  --name myContainerAppEnv \
  --location eastus \
  --enable-workload-profiles \
  --infrastructure-subnet-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/containerAppsSubnet

# Create an internal-only environment (no public IP)
az containerapp env create \
  --resource-group myRG \
  --name myInternalEnv \
  --location eastus \
  --internal-only true \
  --infrastructure-subnet-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/containerAppsSubnet

# List environments
az containerapp env list \
  --resource-group myRG \
  --query "[].{Name:name, Location:location, State:provisioningState, DefaultDomain:defaultDomain}" \
  --output table

# Show environment details
az containerapp env show \
  --resource-group myRG \
  --name myContainerAppEnv

# Delete environment (deletes all apps within)
az containerapp env delete \
  --resource-group myRG \
  --name myContainerAppEnv \
  --yes
```

## Container App CRUD

```bash
# --- Create container apps ---
# Create a simple container app (public HTTP ingress)
az containerapp create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name myapp \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 80 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 10

# Create with environment variables and secrets
az containerapp create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name myapi \
  --image myacr.azurecr.io/myapi:latest \
  --registry-server myacr.azurecr.io \
  --registry-identity system \
  --target-port 8080 \
  --ingress external \
  --env-vars "APP_ENV=production" "LOG_LEVEL=info" "DB_PASSWORD=secretref:db-password" \
  --secrets "db-password=mysecretvalue" \
  --min-replicas 1 \
  --max-replicas 20 \
  --cpu 0.5 \
  --memory 1.0Gi

# Create with internal ingress only (service-to-service)
az containerapp create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name mybackend \
  --image myacr.azurecr.io/mybackend:v2.0 \
  --target-port 3000 \
  --ingress internal \
  --min-replicas 1 \
  --max-replicas 5

# Create with Dapr enabled
az containerapp create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name myservice \
  --image myacr.azurecr.io/myservice:latest \
  --target-port 5000 \
  --ingress internal \
  --enable-dapr \
  --dapr-app-id my-service \
  --dapr-app-port 5000 \
  --dapr-app-protocol http

# --- Update container apps ---
# Update container image (creates new revision)
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --image myacr.azurecr.io/myapi:v2.1

# Update scaling parameters
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --min-replicas 2 \
  --max-replicas 50

# Update CPU and memory (creates new revision)
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --cpu 1.0 \
  --memory 2.0Gi

# Enable multiple-revision mode for traffic splitting
az containerapp revision set-mode \
  --resource-group myRG \
  --name myapp \
  --mode multiple

# List container apps
az containerapp list \
  --resource-group myRG \
  --query "[].{Name:name, FQDN:properties.configuration.ingress.fqdn, State:properties.provisioningState}" \
  --output table

# Show container app details
az containerapp show \
  --resource-group myRG \
  --name myapp

# Delete a container app
az containerapp delete \
  --resource-group myRG \
  --name myapp \
  --yes
```

## Revisions and Traffic

```bash
# List revisions for a container app
az containerapp revision list \
  --resource-group myRG \
  --name myapp \
  --query "[].{Name:name, Active:properties.active, TrafficWeight:properties.trafficWeight, Replicas:properties.replicas, CreatedTime:properties.createdTime}" \
  --output table

# Show a specific revision
az containerapp revision show \
  --resource-group myRG \
  --name myapp \
  --revision myapp--abc1234

# Activate a specific revision
az containerapp revision activate \
  --resource-group myRG \
  --name myapp \
  --revision myapp--abc1234

# Deactivate a revision (stops its replicas, saves cost)
az containerapp revision deactivate \
  --resource-group myRG \
  --name myapp \
  --revision myapp--oldrevision

# Restart all replicas of the latest revision
az containerapp revision restart \
  --resource-group myRG \
  --name myapp \
  --revision myapp--abc1234

# Set traffic weight between revisions (canary release)
az containerapp ingress traffic set \
  --resource-group myRG \
  --name myapp \
  --revision-weight myapp--stable=90 myapp--canary=10

# Route 100% to latest revision
az containerapp ingress traffic set \
  --resource-group myRG \
  --name myapp \
  --revision-weight latest=100
```

## Scaling Rules

```bash
# Update min/max replicas
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --min-replicas 0 \
  --max-replicas 30

# Add HTTP scaling rule (scale on concurrent requests)
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=50

# Add KEDA Service Bus scaling rule
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --scale-rule-name sb-rule \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata queueName=myQueue namespace=myServiceBusNS messageCount=10 \
  --scale-rule-auth "connection=servicebus-connection-secret"

# Add CPU-based scaling rule
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata type=Utilization value=70
```

## Jobs

```bash
# --- Create jobs ---
# Create a manual job
az containerapp job create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name mybatchjob \
  --image myacr.azurecr.io/mybatchprocessor:latest \
  --trigger-type Manual \
  --replica-timeout 1800 \
  --replica-retry-limit 3 \
  --parallelism 1 \
  --replica-completion-count 1

# Create a scheduled job (cron)
az containerapp job create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name nightly-report \
  --image myacr.azurecr.io/reports:latest \
  --trigger-type Schedule \
  --cron-expression "0 2 * * *" \
  --replica-timeout 3600 \
  --replica-retry-limit 1

# Create an event-triggered job (Service Bus queue)
az containerapp job create \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --name queue-processor \
  --image myacr.azurecr.io/processor:latest \
  --trigger-type Event \
  --replica-timeout 300 \
  --min-executions 0 \
  --max-executions 20 \
  --scale-rule-name sb-rule \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata queueName=myQueue namespace=myServiceBusNS messageCount=1 \
  --scale-rule-auth "connection=servicebus-secret"

# --- Manage jobs ---
# Manually trigger a job execution
az containerapp job start \
  --resource-group myRG \
  --name mybatchjob

# List job executions
az containerapp job execution list \
  --resource-group myRG \
  --name mybatchjob \
  --query "[].{ExecutionId:name, Status:properties.status, StartTime:properties.startTime}" \
  --output table

# Show a specific execution
az containerapp job execution show \
  --resource-group myRG \
  --name mybatchjob \
  --job-execution-name mybatchjob-execution-abc123

# Stop an in-progress execution
az containerapp job stop \
  --resource-group myRG \
  --name mybatchjob \
  --job-execution-name mybatchjob-execution-abc123

# Delete a job
az containerapp job delete \
  --resource-group myRG \
  --name mybatchjob \
  --yes
```

## Secrets, Ingress, and Dapr

```bash
# --- Secrets ---
# Set secrets on a container app
az containerapp secret set \
  --resource-group myRG \
  --name myapp \
  --secrets db-password=supersecret api-key=myapikey123

# Set a Key Vault reference secret (using managed identity)
az containerapp secret set \
  --resource-group myRG \
  --name myapp \
  --secrets "db-connection=keyvaultref:https://myKV.vault.azure.net/secrets/DbConnectionString,identityref:/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"

# List secrets (values hidden)
az containerapp secret list \
  --resource-group myRG \
  --name myapp \
  --output table

# --- Ingress ---
# Enable/update ingress on a container app
az containerapp ingress update \
  --resource-group myRG \
  --name myapp \
  --type external \
  --target-port 8080 \
  --transport http

# Enable ingress (if not set at creation)
az containerapp ingress enable \
  --resource-group myRG \
  --name myapp \
  --type external \
  --target-port 3000

# Disable ingress (no HTTP endpoint)
az containerapp ingress disable \
  --resource-group myRG \
  --name myapp

# Add a custom hostname
az containerapp hostname add \
  --resource-group myRG \
  --name myapp \
  --hostname api.contoso.com

# List hostnames and their TLS status
az containerapp hostname list \
  --resource-group myRG \
  --name myapp \
  --output table

# Bind managed TLS certificate to custom hostname
az containerapp hostname bind \
  --resource-group myRG \
  --name myapp \
  --hostname api.contoso.com \
  --environment myContainerAppEnv \
  --validation-method CNAME

# --- Dapr Components ---
# Set a Dapr pub/sub component on the environment
az containerapp env dapr-component set \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --dapr-component-name pubsub \
  --yaml @dapr-pubsub-component.yaml

# List Dapr components in environment
az containerapp env dapr-component list \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --output table

# Show a Dapr component
az containerapp env dapr-component show \
  --resource-group myRG \
  --environment myContainerAppEnv \
  --dapr-component-name pubsub

# Enable/configure Dapr on an existing app
az containerapp update \
  --resource-group myRG \
  --name myapp \
  --enable-dapr \
  --dapr-app-id my-service \
  --dapr-app-port 8080 \
  --dapr-app-protocol grpc
```

## Logs and Diagnostics

```bash
# Stream live logs for a container app
az containerapp logs show \
  --resource-group myRG \
  --name myapp \
  --follow

# Show past logs (last 50 lines)
az containerapp logs show \
  --resource-group myRG \
  --name myapp \
  --tail 50

# Show logs for a specific revision
az containerapp logs show \
  --resource-group myRG \
  --name myapp \
  --revision myapp--abc1234

# Show system logs for the environment
az containerapp env logs show \
  --resource-group myRG \
  --name myContainerAppEnv

# Open an interactive shell in a running container
az containerapp exec \
  --resource-group myRG \
  --name myapp \
  --command /bin/sh

# Show container app metrics (replica count, requests, etc.)
az monitor metrics list \
  --resource /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.App/containerApps/myapp \
  --metric "Replicas" \
  --interval PT1M \
  --output table
```
