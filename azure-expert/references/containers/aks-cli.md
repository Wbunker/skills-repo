# AKS — Advanced CLI Reference
For service concepts, see [aks-capabilities.md](aks-capabilities.md).
For basic cluster creation commands, see [compute/aks-cli.md](../compute/aks-cli.md).

## Node Pool Management

```bash
# --- Add node pools ---
# Add a user node pool (Linux, Standard_D4s_v5)
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --os-type Linux \
  --mode User

# Add a Windows node pool
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name winpool1 \
  --node-count 2 \
  --node-vm-size Standard_D4s_v5 \
  --os-type Windows \
  --mode User

# Add a Spot node pool for batch workloads
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name spotpool \
  --node-count 0 \
  --node-vm-size Standard_D4s_v5 \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 20 \
  --node-taints kubernetes.azure.com/scalesetpriority=spot:NoSchedule \
  --labels workload=batch

# Add a dedicated GPU node pool
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name gpupool \
  --node-count 1 \
  --node-vm-size Standard_NC6s_v3 \
  --node-taints sku=gpu:NoSchedule \
  --labels accelerator=nvidia

# Add a node pool with custom labels and taints
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name frontendpool \
  --node-count 3 \
  --node-vm-size Standard_D2s_v5 \
  --labels environment=prod tier=frontend \
  --node-taints tier=frontend:NoSchedule

# --- Scale node pools ---
# Scale a node pool to a specific count
az aks nodepool scale \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --node-count 5

# Scale user pool to zero (stop workloads, keep pool)
az aks nodepool scale \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --node-count 0

# --- Update node pool autoscaler settings ---
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10

# Disable autoscaler on a node pool
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --disable-cluster-autoscaler

# Update node pool labels
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --labels environment=staging tier=backend

# --- Upgrade node pools ---
# Upgrade node pool Kubernetes version (follows control plane)
az aks nodepool upgrade \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --kubernetes-version 1.30.0

# Upgrade node image only (OS updates, no Kubernetes version change)
az aks nodepool upgrade \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --node-image-only

# --- List and show node pools ---
az aks nodepool list \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --query "[].{Name:name, Mode:mode, Count:count, VMSize:vmSize, K8sVersion:orchestratorVersion, State:provisioningState}" \
  --output table

az aks nodepool show \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1

# --- Delete a node pool ---
az aks nodepool delete \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool1 \
  --yes
```

## Add-ons and Extensions

```bash
# --- Enable add-ons ---
# Enable Azure Monitor Container Insights
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons monitoring \
  --workspace-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace

# Enable Azure Policy for Kubernetes (Gatekeeper)
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons azure-policy

# Enable Key Vault Secrets Provider (CSI driver)
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons azure-keyvault-secrets-provider \
  --enable-secret-rotation \
  --rotation-poll-interval 2m

# Enable Web Application Routing (managed NGINX + DNS + TLS)
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons web_application_routing \
  --dns-zone-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/dnszones/contoso.com

# Enable KEDA (Kubernetes Event Driven Autoscaling)
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons keda

# Enable Dapr
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons dapr

# Enable multiple add-ons at once
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons monitoring,azure-policy,azure-keyvault-secrets-provider

# Disable an add-on
az aks disable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons monitoring
```

## Workload Identity

```bash
# Enable OIDC issuer and workload identity on existing cluster
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-oidc-issuer \
  --enable-workload-identity

# Get the OIDC issuer URL (needed for federated credential)
az aks show \
  --resource-group myRG \
  --name myAKSCluster \
  --query "oidcIssuerProfile.issuerUrl" \
  --output tsv

# Create a user-assigned managed identity for the workload
az identity create \
  --resource-group myRG \
  --name myWorkloadIdentity

# Get identity details
IDENTITY_CLIENT_ID=$(az identity show --resource-group myRG --name myWorkloadIdentity --query clientId -o tsv)
IDENTITY_OBJECT_ID=$(az identity show --resource-group myRG --name myWorkloadIdentity --query principalId -o tsv)
OIDC_ISSUER=$(az aks show --resource-group myRG --name myAKSCluster --query "oidcIssuerProfile.issuerUrl" -o tsv)

# Create federated identity credential (link K8s SA to managed identity)
az identity federated-credential create \
  --name myFederatedCredential \
  --identity-name myWorkloadIdentity \
  --resource-group myRG \
  --issuer ${OIDC_ISSUER} \
  --subject "system:serviceaccount:my-namespace:my-service-account" \
  --audiences api://AzureADTokenExchange

# Assign RBAC role to the managed identity on a resource
az role assignment create \
  --assignee-object-id ${IDENTITY_OBJECT_ID} \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorageAcct
```

## Cluster Upgrades

```bash
# List available Kubernetes versions in a region
az aks get-versions \
  --location eastus \
  --output table

# Upgrade AKS control plane Kubernetes version
az aks upgrade \
  --resource-group myRG \
  --name myAKSCluster \
  --kubernetes-version 1.30.0 \
  --yes

# Upgrade control plane only (not node pools)
az aks upgrade \
  --resource-group myRG \
  --name myAKSCluster \
  --kubernetes-version 1.30.0 \
  --control-plane-only \
  --yes

# Upgrade node image only for all node pools
az aks upgrade \
  --resource-group myRG \
  --name myAKSCluster \
  --node-image-only \
  --yes

# Set auto-upgrade channel
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --auto-upgrade-channel patch

# Configure node OS upgrade channel
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --node-os-upgrade-channel NodeImage

# Add a planned maintenance window
az aks maintenanceconfiguration add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name default \
  --weekday Saturday \
  --start-hour 2

# List maintenance configurations
az aks maintenanceconfiguration list \
  --resource-group myRG \
  --cluster-name myAKSCluster
```

## GitOps / Flux

```bash
# Enable Flux GitOps extension on AKS cluster
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --cluster-type managedClusters \
  --extension-type microsoft.flux \
  --name flux \
  --scope cluster

# Create a Flux configuration (connect cluster to Git repo)
az k8s-configuration flux create \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --cluster-type managedClusters \
  --name cluster-config \
  --namespace flux-system \
  --scope cluster \
  --url https://github.com/myorg/my-cluster-config \
  --branch main \
  --kustomization name=apps path=./clusters/production prune=true

# List Flux configurations
az k8s-configuration flux list \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --cluster-type managedClusters

# Show Flux configuration state
az k8s-configuration flux show \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --cluster-type managedClusters \
  --name cluster-config
```

## Cluster Lifecycle Operations

```bash
# Get cluster credentials (merge into ~/.kube/config)
az aks get-credentials \
  --resource-group myRG \
  --name myAKSCluster \
  --overwrite-existing

# Get admin credentials (bypass RBAC)
az aks get-credentials \
  --resource-group myRG \
  --name myAKSCluster \
  --admin

# Stop a cluster (deallocate all nodes, preserve state — cost savings)
az aks stop \
  --resource-group myRG \
  --name myAKSCluster

# Start a previously stopped cluster
az aks start \
  --resource-group myRG \
  --name myAKSCluster

# Enable Node Auto-Provisioner (Karpenter-based)
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --node-provisioning-mode Auto

# Enable Azure Container Storage (block volume pool)
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-azure-container-storage azureDisk

# Update cluster autoscaler profile
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --cluster-autoscaler-profile \
    scale-down-unneeded-time=10m \
    scan-interval=10s \
    max-node-provision-time=15m

# Show cluster details
az aks show \
  --resource-group myRG \
  --name myAKSCluster \
  --query "{K8sVersion:kubernetesVersion, FQDN:fqdn, ProvisioningState:provisioningState, NetworkPlugin:networkProfile.networkPlugin, OIDCIssuer:oidcIssuerProfile.issuerUrl}" \
  --output json

# List node image versions available
az aks nodepool get-upgrades \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --nodepool-name userpool1
```
