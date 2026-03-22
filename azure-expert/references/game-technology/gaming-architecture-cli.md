# Azure Gaming Architecture — CLI Reference
For service concepts, see [gaming-architecture-capabilities.md](gaming-architecture-capabilities.md).

## AKS for Game Servers

```bash
# --- Create AKS Cluster for Game Servers ---
az aks create \
  --resource-group myGameRG \
  --name myGameCluster \
  --location eastus \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 20 \
  --network-plugin azure \
  --network-policy azure \
  --generate-ssh-keys \
  --attach-acr myGameACR                      # Create game server AKS cluster

# --- Add Dedicated Node Pool for Game Servers ---
az aks nodepool add \
  --resource-group myGameRG \
  --cluster-name myGameCluster \
  --name gameservers \
  --node-count 5 \
  --node-vm-size Standard_D8s_v5 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 50 \
  --labels agones-system=false \
  --node-taints "dedicated=game-server:NoSchedule" \
  --mode User                                 # Add game server node pool

# Add GPU node pool for GPU-accelerated games
az aks nodepool add \
  --resource-group myGameRG \
  --cluster-name myGameCluster \
  --name gpugames \
  --node-count 2 \
  --node-vm-size Standard_NV6ads_A10_v5 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10 \
  --node-taints "dedicated=gpu-game:NoSchedule" \
  --mode User

# --- Connect to AKS Cluster ---
az aks get-credentials \
  --resource-group myGameRG \
  --name myGameCluster                        # Configure kubectl context

az aks get-credentials \
  --resource-group myGameRG \
  --name myGameCluster \
  --overwrite-existing                        # Overwrite existing kubeconfig

# --- AKS Cluster Management ---
az aks list --resource-group myGameRG --output table  # List clusters
az aks show --resource-group myGameRG --name myGameCluster  # Show cluster details

az aks scale \
  --resource-group myGameRG \
  --name myGameCluster \
  --node-count 8 \
  --nodepool-name gameservers                 # Manual scale node pool

az aks upgrade \
  --resource-group myGameRG \
  --name myGameCluster \
  --kubernetes-version 1.30.0                 # Upgrade Kubernetes version

az aks stop --resource-group myGameRG --name myGameCluster   # Stop cluster (save costs)
az aks start --resource-group myGameRG --name myGameCluster  # Start cluster

az aks delete --resource-group myGameRG --name myGameCluster --yes  # Delete cluster
```

## Agones Installation and Management

```bash
# --- Install Agones via Helm ---
# Add Agones Helm repository
helm repo add agones https://agones.dev/chart/stable
helm repo update

# Install Agones (with custom node tolerations for game server nodes)
helm install agones agones/agones \
  --namespace agones-system \
  --create-namespace \
  --set "gameservers.namespaces={default,game-servers}" \
  --set agones.controller.tolerations[0].key=dedicated \
  --set agones.controller.tolerations[0].value=game-server \
  --set agones.controller.tolerations[0].effect=NoSchedule

# Check Agones installation
kubectl get pods --namespace agones-system
kubectl describe agones --namespace agones-system

# Upgrade Agones
helm upgrade agones agones/agones --namespace agones-system

# Uninstall Agones
helm uninstall agones --namespace agones-system

# --- Agones Resource Management ---
# List Fleets
kubectl get fleet

# Get Fleet details
kubectl describe fleet dedicated-game-server

# Scale Fleet manually
kubectl scale fleet dedicated-game-server --replicas=10

# List GameServers
kubectl get gameserver
kubectl get gameserver -o wide                # Show IP and ports

# List GameServer Allocations
kubectl get gameserverallocation

# Allocate a game server (create an allocation request)
kubectl create -f - <<EOF
apiVersion: allocation.agones.dev/v1
kind: GameServerAllocation
metadata:
  name: my-allocation
spec:
  required:
    matchLabels:
      agones.dev/fleet: dedicated-game-server
  preferred:
  - matchLabels:
      region: eastus
EOF

# Check allocation result
kubectl get gameserverallocation my-allocation -o jsonpath='{.status}'

# List FleetAutoscalers
kubectl get fleetautoscaler

# Deploy game server fleet
kubectl apply -f fleet.yaml
kubectl apply -f fleetautoscaler.yaml

# Get game server logs
kubectl logs -l agones.dev/fleet=dedicated-game-server --tail=100 -f

# --- ACR for Game Server Images ---
az acr create \
  --resource-group myGameRG \
  --name myGameACR \
  --sku Premium \
  --location eastus                           # Create Container Registry (Premium for geo-replication)

az acr login --name myGameACR               # Login to ACR

# Push game server image
docker build -t game-server:v1.2.0 .
docker tag game-server:v1.2.0 myGameACR.azurecr.io/game-server:v1.2.0
docker push myGameACR.azurecr.io/game-server:v1.2.0

az acr repository list --name myGameACR --output table  # List images
az acr repository show-tags --name myGameACR --repository game-server  # List tags
```

## Cosmos DB for Game Data

```bash
# --- Create Cosmos DB for Games ---
az cosmosdb create \
  --resource-group myGameRG \
  --name myGameCosmosDB \
  --default-consistency-level Session \
  --locations regionName=eastus failoverPriority=0 \
  --locations regionName=westus failoverPriority=1 \
  --enable-automatic-failover true \
  --kind GlobalDocumentDB                     # Create Cosmos DB with 2-region multi-region writes

# Create with multi-region writes (for global leaderboards)
az cosmosdb create \
  --resource-group myGameRG \
  --name myGlobalGameDB \
  --default-consistency-level Session \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
  --locations regionName=westeurope failoverPriority=1 isZoneRedundant=true \
  --locations regionName=southeastasia failoverPriority=2 isZoneRedundant=true \
  --enable-multiple-write-locations true       # True global multi-master writes

az cosmosdb list --resource-group myGameRG --output table  # List Cosmos DB accounts
az cosmosdb show --resource-group myGameRG --name myGameCosmosDB  # Show details

# --- Database and Containers ---
az cosmosdb sql database create \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --name game-db                              # Create SQL (Core) API database

# Leaderboard container (partition by game mode)
az cosmosdb sql container create \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name leaderboard \
  --partition-key-path /gameMode \
  --throughput 1000                           # Dedicated throughput (low scale dev)

# Leaderboard with autoscale (for variable traffic)
az cosmosdb sql container create \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name leaderboard \
  --partition-key-path /gameMode \
  --max-throughput 10000                      # Autoscale: 1000-10000 RU/s

# Player profile container (partition by playerId)
az cosmosdb sql container create \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name players \
  --partition-key-path /playerId \
  --throughput 400

# Session data container with TTL
az cosmosdb sql container create \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name sessions \
  --partition-key-path /gameId \
  --default-ttl 3600 \
  --throughput 400                            # Auto-delete sessions after 1 hour

az cosmosdb sql container list \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db                     # List containers

# --- Connection Strings ---
az cosmosdb keys list \
  --resource-group myGameRG \
  --name myGameCosmosDB \
  --type keys                                 # Get primary and secondary keys

az cosmosdb keys list \
  --resource-group myGameRG \
  --name myGameCosmosDB \
  --type connection-strings                   # Get full connection strings

# --- Scale and Performance ---
az cosmosdb sql container throughput update \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name leaderboard \
  --throughput 5000                           # Manually scale throughput (for launch spike)

az cosmosdb sql container throughput migrate \
  --resource-group myGameRG \
  --account-name myGameCosmosDB \
  --database-name game-db \
  --name leaderboard \
  --throughput-type autoscale                 # Switch to autoscale throughput

# Add read region for lower latency
az cosmosdb update \
  --resource-group myGameRG \
  --name myGameCosmosDB \
  --locations regionName=eastus failoverPriority=0 \
  --locations regionName=westus failoverPriority=1 \
  --locations regionName=eastasia failoverPriority=2  # Add Asia read region
```

## Azure CDN for Game Content

```bash
# --- CDN Profile and Endpoints ---
az cdn profile create \
  --resource-group myGameRG \
  --name myGameCDN \
  --location global \
  --sku Standard_Microsoft                    # Create Microsoft CDN profile

az cdn profile create \
  --resource-group myGameRG \
  --name myGameCDNPremium \
  --location global \
  --sku Premium_Verizon                       # Create Verizon Premium CDN (advanced rules)

az cdn profile list --resource-group myGameRG --output table  # List CDN profiles

# Create CDN endpoint for game patches (from Blob Storage)
az cdn endpoint create \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches \
  --location global \
  --origin "mystorageacct.blob.core.windows.net" \
  --origin-host-header "mystorageacct.blob.core.windows.net" \
  --query-string-caching-behavior IgnoreQueryString \
  --content-types-to-compress "application/octet-stream" \
  --is-compression-enabled true               # CDN for game patch files

# Create CDN endpoint for game assets (textures, sounds)
az cdn endpoint create \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-assets \
  --location global \
  --origin "mystorageacct.blob.core.windows.net" \
  --origin-path "/game-assets" \
  --query-string-caching-behavior UseQueryString  # Query string for cache busting

az cdn endpoint list \
  --resource-group myGameRG \
  --profile-name myGameCDN --output table     # List CDN endpoints

az cdn endpoint show \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches                         # Show endpoint details

# --- Cache Management ---
# Purge specific files (after patch update)
az cdn endpoint purge \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches \
  --content-paths "/v1.5.2/patch-windows.zip" "/v1.5.2/patch-linux.tar.gz"

# Purge entire cache (full refresh)
az cdn endpoint purge \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-assets \
  --content-paths "/*"

# Load files into cache proactively
az cdn endpoint load \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches \
  --content-paths "/v1.5.2/patch-windows.zip"  # Pre-warm cache on release day

# --- Custom Domains ---
az cdn custom-domain create \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --endpoint-name game-patches \
  --hostname "patches.mygame.com" \
  --name patches-domain                       # Add custom domain

az cdn custom-domain enable-https \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --endpoint-name game-patches \
  --name patches-domain \
  --min-tls-version "1.2"                     # Enable HTTPS with managed certificate

# Add another origin (failover)
az cdn origin add \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --endpoint-name game-patches \
  --name secondary-origin \
  --host-name "mystorageacct2.blob.core.windows.net" \
  --priority 2 \
  --weight 100                                # Secondary origin (failover)

# --- Monitor CDN ---
az monitor metrics list \
  --resource /subscriptions/{subId}/resourceGroups/myGameRG/providers/Microsoft.Cdn/profiles/myGameCDN/endpoints/game-patches \
  --metric "ByteHitRatio" "RequestCount" \
  --output table                              # View CDN metrics

az cdn endpoint stop \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches                         # Stop endpoint temporarily

az cdn endpoint start \
  --resource-group myGameRG \
  --profile-name myGameCDN \
  --name game-patches                         # Start endpoint
```

## Azure Batch for Game Build Pipelines

```bash
# --- Azure Batch for Game Builds ---
az batch account create \
  --resource-group myGameRG \
  --name myGameBuildBatch \
  --location eastus \
  --storage-account myStorageAcct             # Create Batch account

az batch account login \
  --resource-group myGameRG \
  --name myGameBuildBatch                     # Login to Batch account for subsequent commands

# Create pool with Spot VMs for cost-efficient builds
az batch pool create \
  --id game-build-pool \
  --image canonical:ubuntuserver:18.04-lts \
  --node-agent-sku-id "batch.node.ubuntu 18.04" \
  --vm-size Standard_D8s_v5 \
  --target-dedicated-nodes 0 \
  --target-low-priority-nodes 10 \
  --auto-scale-formula "pendingTaskSamplePercent = $PendingTasks.GetSamplePercent(180 * TimeInterval_Second); pendingTaskSamples = pendingTaskSamplePercent < 70 ? startingNumberOfVMs : avg($PendingTasks.GetSample(180 * TimeInterval_Second)); $TargetLowPriorityNodes=min(maxNumberofVMs, pendingTaskSamples);"  # Autoscale based on pending tasks

# Create build job
az batch job create \
  --id shader-compile-job \
  --pool-id game-build-pool

# Add build task
az batch task create \
  --job-id shader-compile-job \
  --task-id compile-vertex-shaders \
  --command-line "/bin/bash -c 'glslangValidator -V *.vert -o *.spv'" \
  --resource-files blob-source=https://mystorageacct.blob.core.windows.net/shaders?sas file-path=shaders/

az batch task list --job-id shader-compile-job --output table  # Monitor build tasks
az batch job delete --job-id shader-compile-job --yes           # Clean up job
```
