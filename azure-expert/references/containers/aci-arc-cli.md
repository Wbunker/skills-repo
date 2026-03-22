# Azure Container Instances & Azure Arc — CLI Reference
For service concepts, see [aci-arc-capabilities.md](aci-arc-capabilities.md).

---

## Azure Container Instances (ACI)

```bash
# --- Create container groups ---
# Create a simple Linux container (public IP, HTTP port)
az container create \
  --resource-group myRG \
  --name mycontainer \
  --image myacr.azurecr.io/myapp:latest \
  --registry-login-server myacr.azurecr.io \
  --registry-username myACRUser \
  --registry-password myACRPassword \
  --dns-name-label myapp-aci-unique \
  --ports 80 \
  --cpu 1 \
  --memory 1.5

# Create using managed identity to pull from ACR
az container create \
  --resource-group myRG \
  --name mycontainer \
  --image myacr.azurecr.io/myapp:latest \
  --assign-identity /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity \
  --acr-identity /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity \
  --ports 8080 \
  --cpu 2 \
  --memory 4

# Create a container with environment variables and secrets
az container create \
  --resource-group myRG \
  --name mycontainer \
  --image myacr.azurecr.io/myapp:latest \
  --environment-variables APP_ENV=production LOG_LEVEL=info \
  --secure-environment-variables DB_PASSWORD=mysecret API_KEY=mysecretkey \
  --cpu 1 \
  --memory 2 \
  --restart-policy OnFailure

# Create a container in a VNet (private, no public IP)
az container create \
  --resource-group myRG \
  --name mycontainer \
  --image myacr.azurecr.io/myapp:latest \
  --vnet myVNet \
  --subnet containerInstancesSubnet \
  --ip-address Private \
  --ports 8080 \
  --cpu 1 \
  --memory 1

# Create with Azure Files volume mount
az container create \
  --resource-group myRG \
  --name mycontainer \
  --image myacr.azurecr.io/myapp:latest \
  --azure-file-volume-account-name myStorageAcct \
  --azure-file-volume-account-key $(az storage account keys list --account-name myStorageAcct --query "[0].value" -o tsv) \
  --azure-file-volume-share-name myfileshare \
  --azure-file-volume-mount-path /mnt/data \
  --cpu 1 \
  --memory 1

# Create a multi-container group (YAML-based)
az container create \
  --resource-group myRG \
  --file container-group.yaml

# Create a Spot priority container (lower cost, evictable)
az container create \
  --resource-group myRG \
  --name myspotcontainer \
  --image myacr.azurecr.io/mybatch:latest \
  --priority Spot \
  --restart-policy Never \
  --cpu 4 \
  --memory 8

# Create a Windows container
az container create \
  --resource-group myRG \
  --name mywincontainer \
  --image mcr.microsoft.com/windows/servercore/iis:windowsservercore-ltsc2022 \
  --os-type Windows \
  --dns-name-label myiis-aci \
  --ports 80 \
  --cpu 2 \
  --memory 4

# --- Inspect and monitor containers ---
# Show container group details (IP, state, containers)
az container show \
  --resource-group myRG \
  --name mycontainer \
  --query "{IP:ipAddress.ip, FQDN:ipAddress.fqdn, State:provisioningState, Containers:containers[*].{Name:name,State:instanceView.currentState.state}}" \
  --output json

# List all container groups in resource group
az container list \
  --resource-group myRG \
  --query "[].{Name:name, State:provisioningState, IP:ipAddress.ip, Location:location}" \
  --output table

# Stream live logs from a container
az container logs \
  --resource-group myRG \
  --name mycontainer \
  --follow

# Get logs from a specific container in a multi-container group
az container logs \
  --resource-group myRG \
  --name mycontainer \
  --container-name sidecar-container

# Execute a command in a running container (interactive shell)
az container exec \
  --resource-group myRG \
  --name mycontainer \
  --exec-command /bin/bash

# Execute a non-interactive command
az container exec \
  --resource-group myRG \
  --name mycontainer \
  --exec-command "ls -la /app"

# Attach to container output streams
az container attach \
  --resource-group myRG \
  --name mycontainer

# --- Lifecycle management ---
# Restart container group (all containers)
az container restart \
  --resource-group myRG \
  --name mycontainer

# Stop container group (deallocate; preserves group definition)
az container stop \
  --resource-group myRG \
  --name mycontainer

# Start a stopped container group
az container start \
  --resource-group myRG \
  --name mycontainer

# Delete a container group
az container delete \
  --resource-group myRG \
  --name mycontainer \
  --yes
```

---

## Azure Arc — Connected Kubernetes

```bash
# --- Connect a Kubernetes cluster to Azure Arc ---
# Install the connectedk8s extension first
az extension add --name connectedk8s

# Connect current kubeconfig context cluster to Azure Arc
az connectedk8s connect \
  --resource-group myRG \
  --name myArcCluster \
  --location eastus

# Connect with custom tags
az connectedk8s connect \
  --resource-group myRG \
  --name myArcCluster \
  --location eastus \
  --tags environment=production owner=platform-team cluster-type=on-premises

# Connect with distribution and infrastructure hints
az connectedk8s connect \
  --resource-group myRG \
  --name myArcCluster \
  --location eastus \
  --distribution eks \
  --infrastructure aws

# List all Arc-connected clusters
az connectedk8s list \
  --resource-group myRG \
  --query "[].{Name:name, Distribution:distribution, ConnectivityStatus:connectivityStatus, Location:location}" \
  --output table

# Show Arc cluster details
az connectedk8s show \
  --resource-group myRG \
  --name myArcCluster

# Enable features on a connected cluster
az connectedk8s enable-features \
  --resource-group myRG \
  --name myArcCluster \
  --features cluster-connect custom-locations azure-rbac

# Update Arc cluster proxy settings
az connectedk8s update \
  --resource-group myRG \
  --name myArcCluster \
  --proxy-http http://myproxy:3128 \
  --proxy-https http://myproxy:3128

# Delete (disconnect) a cluster from Azure Arc
az connectedk8s delete \
  --resource-group myRG \
  --name myArcCluster \
  --yes
```

## Azure Arc — Kubernetes Extensions

```bash
# --- Install extensions on Arc-connected clusters ---
# Install Flux GitOps extension
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name flux \
  --extension-type microsoft.flux \
  --scope cluster

# Install Azure Monitor Container Insights extension
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name azuremonitor-containers \
  --extension-type microsoft.azuremonitor.containers \
  --configuration-settings logAnalyticsWorkspaceResourceID=/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace

# Install Defender for Containers extension
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name microsoft-defender \
  --extension-type microsoft.azuredefender.kubernetes \
  --scope cluster \
  --release-train stable

# Install Azure Policy (Gatekeeper) extension
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name azure-policy \
  --extension-type microsoft.policyinsights \
  --scope cluster

# Install Key Vault CSI driver
az k8s-extension create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name akvsecretsprovider \
  --extension-type microsoft.azurekeyvaultsecretsprovider

# List extensions on a cluster
az k8s-extension list \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --output table

# Show extension details
az k8s-extension show \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name flux

# Delete an extension
az k8s-extension delete \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name flux \
  --yes
```

## Azure Arc — GitOps (Flux Configurations)

```bash
# Install k8s-configuration extension
az extension add --name k8s-configuration

# Create a Flux GitOps configuration on an Arc cluster
az k8s-configuration flux create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name cluster-config \
  --namespace flux-system \
  --scope cluster \
  --url https://github.com/myorg/cluster-config.git \
  --branch main \
  --kustomization name=infra path=./clusters/production prune=true

# Create configuration with Helm release kustomization
az k8s-configuration flux create \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name app-config \
  --namespace flux-system \
  --scope cluster \
  --url https://github.com/myorg/app-manifests.git \
  --branch release/1.2 \
  --kustomization name=apps path=./helm-releases force=true prune=true \
  --kustomization name=namespaces path=./namespaces prune=true

# List Flux configurations
az k8s-configuration flux list \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --output table

# Show Flux configuration and sync status
az k8s-configuration flux show \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name cluster-config

# Delete a Flux configuration (does not delete deployed resources by default)
az k8s-configuration flux delete \
  --resource-group myRG \
  --cluster-name myArcCluster \
  --cluster-type connectedClusters \
  --name cluster-config \
  --yes
```

## Azure Arc — Servers

```bash
# Install the connectedmachine extension
az extension add --name connectedmachine

# List all Arc-enabled servers in a resource group
az connectedmachine list \
  --resource-group myRG \
  --query "[].{Name:name, OS:osType, Status:status, AgentVersion:agentVersion, Location:location}" \
  --output table

# Show a specific Arc-enabled server
az connectedmachine show \
  --resource-group myRG \
  --name myOnPremServer

# Install a VM extension on an Arc server
az connectedmachine extension create \
  --resource-group myRG \
  --machine-name myOnPremServer \
  --location eastus \
  --name AzureMonitorWindowsAgent \
  --publisher Microsoft.Azure.Monitor \
  --type AzureMonitorWindowsAgent \
  --type-handler-version 1.0

# Install Log Analytics (MMA) agent extension
az connectedmachine extension create \
  --resource-group myRG \
  --machine-name myOnPremLinuxServer \
  --location eastus \
  --name OmsAgentForLinux \
  --publisher Microsoft.EnterpriseCloud.Monitoring \
  --type OmsAgentForLinux \
  --settings "{\"workspaceId\": \"{workspaceId}\"}" \
  --protected-settings "{\"workspaceKey\": \"{workspaceKey}\"}"

# List extensions installed on an Arc server
az connectedmachine extension list \
  --resource-group myRG \
  --machine-name myOnPremServer \
  --output table

# Show extension status
az connectedmachine extension show \
  --resource-group myRG \
  --machine-name myOnPremServer \
  --name AzureMonitorWindowsAgent

# Delete an extension from an Arc server
az connectedmachine extension delete \
  --resource-group myRG \
  --machine-name myOnPremServer \
  --name OmsAgentForLinux \
  --yes
```

## Azure Arc — Data Services

```bash
# Install arcdata extension
az extension add --name arcdata

# Create an Arc data controller (direct connected mode)
az arcdata dc create \
  --resource-group myRG \
  --name myDataController \
  --location eastus \
  --connectivity-mode direct \
  --k8s-namespace arc-data \
  --profile-name azure-arc-aks-premium-storage \
  --storage-class managed-premium \
  --cluster-name myArcCluster

# List Arc data controllers
az arcdata dc list \
  --resource-group myRG \
  --output table

# Create an Arc-enabled SQL Managed Instance (General Purpose)
az sql mi-arc create \
  --name my-sql-mi \
  --resource-group myRG \
  --location eastus \
  --custom-location myCustomLocation \
  --cores-request 2 \
  --cores-limit 4 \
  --memory-request 4Gi \
  --memory-limit 8Gi \
  --tier GeneralPurpose

# List Arc SQL Managed Instances
az sql mi-arc list \
  --resource-group myRG \
  --output table

# Show Arc SQL MI details
az sql mi-arc show \
  --name my-sql-mi \
  --resource-group myRG
```
