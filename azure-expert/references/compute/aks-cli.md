# Azure Kubernetes Service (AKS) — CLI Reference

For service concepts, see [aks-capabilities.md](aks-capabilities.md).

## AKS Cluster — Create

```bash
# --- Create a basic AKS cluster ---
az aks create \
  --resource-group myRG \
  --name myAKSCluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --zones 1 2 3 \
  --enable-managed-identity \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --generate-ssh-keys

# Create cluster with monitoring and policy add-ons
az aks create \
  --resource-group myRG \
  --name myAKSCluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --zones 1 2 3 \
  --enable-managed-identity \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --enable-addons monitoring,azure-policy,azure-keyvault-secrets-provider \
  --workspace-resource-id /subscriptions/.../resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --network-policy cilium \
  --auto-upgrade-channel patch \
  --node-os-upgrade-channel NodeImage \
  --generate-ssh-keys

# Create private cluster (API server not publicly accessible)
az aks create \
  --resource-group myRG \
  --name myPrivateAKSCluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --enable-private-cluster \
  --enable-managed-identity \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --generate-ssh-keys

# List available Kubernetes versions in a region
az aks get-versions --location eastus --output table
```

---

## AKS Cluster — Access and Info

```bash
# Download kubeconfig credentials
az aks get-credentials \
  --resource-group myRG \
  --name myAKSCluster

# Overwrite existing kubeconfig context
az aks get-credentials \
  --resource-group myRG \
  --name myAKSCluster \
  --overwrite-existing

# Get admin credentials (local account — use only for break-glass)
az aks get-credentials \
  --resource-group myRG \
  --name myAKSCluster \
  --admin

# Show cluster details
az aks show --resource-group myRG --name myAKSCluster

# Show cluster OIDC issuer URL (required for Workload Identity)
az aks show \
  --resource-group myRG \
  --name myAKSCluster \
  --query oidcIssuerProfile.issuerUrl \
  --output tsv

# List all AKS clusters in subscription
az aks list --output table
```

---

## AKS — Node Pools

```bash
# --- Add a user node pool ---
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool \
  --node-count 3 \
  --node-vm-size Standard_D8s_v5 \
  --zones 1 2 3 \
  --mode User \
  --labels workload=application tier=backend \
  --node-taints dedicated=backend:NoSchedule

# Add a Spot node pool
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
  --max-count 20

# Add a Windows node pool
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name winpool \
  --os-type Windows \
  --node-count 2 \
  --node-vm-size Standard_D4s_v5

# Enable cluster autoscaler on a node pool
az aks nodepool update \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 20

# Manually scale a node pool
az aks nodepool scale \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool \
  --node-count 5

# List node pools
az aks nodepool list \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --output table

# Delete a node pool
az aks nodepool delete \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool \
  --no-wait
```

---

## AKS — Upgrades

```bash
# List available upgrade versions
az aks get-upgrades \
  --resource-group myRG \
  --name myAKSCluster \
  --output table

# Upgrade control plane only
az aks upgrade \
  --resource-group myRG \
  --name myAKSCluster \
  --kubernetes-version 1.31.0 \
  --control-plane-only

# Upgrade control plane and all node pools
az aks upgrade \
  --resource-group myRG \
  --name myAKSCluster \
  --kubernetes-version 1.31.0

# Upgrade a specific node pool
az aks nodepool upgrade \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name userpool \
  --kubernetes-version 1.31.0 \
  --max-surge 33%

# Set auto-upgrade channel
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --auto-upgrade-channel patch

# Set node OS auto-upgrade channel
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --node-os-upgrade-channel NodeImage
```

---

## AKS — Add-ons and Features

```bash
# Enable add-ons on an existing cluster
az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons monitoring \
  --workspace-resource-id /subscriptions/.../workspaces/myWorkspace

az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons azure-policy

az aks enable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons azure-keyvault-secrets-provider \
  --enable-secret-rotation

# Disable an add-on
az aks disable-addons \
  --resource-group myRG \
  --name myAKSCluster \
  --addons monitoring

# Enable KEDA add-on
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-keda

# Enable Workload Identity on existing cluster
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-oidc-issuer \
  --enable-workload-identity

# Enable Blob CSI driver
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-blob-driver

# Enable Disk CSI driver (default; shown for completeness)
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --enable-disk-driver

# Enable cluster autoscaler profile settings
az aks update \
  --resource-group myRG \
  --name myAKSCluster \
  --cluster-autoscaler-profile \
    scan-interval=10s \
    scale-down-delay-after-add=5m \
    scale-down-unneeded-time=5m

# List installed add-ons
az aks show \
  --resource-group myRG \
  --name myAKSCluster \
  --query addonProfiles
```

---

## AKS — Workload Identity Setup

```bash
# Step 1: Get OIDC issuer URL
OIDC_ISSUER=$(az aks show -g myRG -n myAKSCluster --query oidcIssuerProfile.issuerUrl -o tsv)

# Step 2: Create user-assigned managed identity
az identity create \
  --resource-group myRG \
  --name myWorkloadIdentity

CLIENT_ID=$(az identity show -g myRG -n myWorkloadIdentity --query clientId -o tsv)
PRINCIPAL_ID=$(az identity show -g myRG -n myWorkloadIdentity --query principalId -o tsv)

# Step 3: Grant identity access to target resource (e.g., Key Vault)
az keyvault set-policy \
  --name myKeyVault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list

# Step 4: Create Kubernetes service account with annotation
kubectl create serviceaccount workload-sa -n myapp
kubectl annotate serviceaccount workload-sa -n myapp \
  azure.workload.identity/client-id=$CLIENT_ID

# Step 5: Create federated identity credential
az identity federated-credential create \
  --resource-group myRG \
  --identity-name myWorkloadIdentity \
  --name myFederatedCredential \
  --issuer $OIDC_ISSUER \
  --subject system:serviceaccount:myapp:workload-sa \
  --audience api://AzureADTokenExchange
```

---

## AKS — kubectl Integration

```bash
# Standard kubectl commands work after get-credentials
kubectl get nodes -o wide
kubectl get pods --all-namespaces
kubectl get deployments -n myapp
kubectl describe pod mypod -n myapp
kubectl logs mypod -n myapp --follow
kubectl exec -it mypod -n myapp -- /bin/bash

# Check resource usage
kubectl top nodes
kubectl top pods -n myapp

# Apply manifests
kubectl apply -f ./k8s/
kubectl apply -f https://raw.githubusercontent.com/.../deployment.yaml

# Port-forward for local debugging
kubectl port-forward svc/myservice 8080:80 -n myapp

# Get cluster info
kubectl cluster-info
kubectl get events -n myapp --sort-by='.lastTimestamp'

# Drain a node for maintenance
kubectl drain nodename --ignore-daemonsets --delete-emptydir-data
kubectl uncordon nodename
```

---

## AKS — Misc Operations

```bash
# Stop cluster (preserves config; no charge for control plane or nodes)
az aks stop --resource-group myRG --name myAKSCluster

# Start cluster
az aks start --resource-group myRG --name myAKSCluster

# Rotate cluster certificates
az aks rotate-certs --resource-group myRG --name myAKSCluster

# Check cluster health
az aks check-acr \
  --resource-group myRG \
  --name myAKSCluster \
  --acr myacr.azurecr.io

# Get managed outbound IP (for firewall allowlisting)
az aks show \
  --resource-group myRG \
  --name myAKSCluster \
  --query networkProfile.loadBalancerProfile.effectiveOutboundIPs[].id \
  --output tsv

# Delete cluster
az aks delete \
  --resource-group myRG \
  --name myAKSCluster \
  --yes \
  --no-wait
```
