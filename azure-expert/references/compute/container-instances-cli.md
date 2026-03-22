# Azure Container Instances — CLI Reference

For service concepts, see [container-instances-capabilities.md](container-instances-capabilities.md).

## Container Groups — Create

```bash
# --- Create a simple public container ---
az container create \
  --resource-group myRG \
  --name myContainer \
  --image mcr.microsoft.com/azuredocs/aci-helloworld \
  --dns-name-label mycontainerdns \
  --ports 80 \
  --cpu 1 \
  --memory 1.5

# Create a container with environment variables
az container create \
  --resource-group myRG \
  --name myContainer \
  --image myacr.azurecr.io/myapp:latest \
  --registry-login-server myacr.azurecr.io \
  --registry-username myacr \
  --registry-password $ACR_PASSWORD \
  --environment-variables \
    ENVIRONMENT=production \
    API_BASE_URL=https://api.example.com \
  --secure-environment-variables \
    DB_PASSWORD=$SECRET_PASSWORD \
  --cpu 2 \
  --memory 4 \
  --ports 8080

# Create a Linux container from ACR with managed identity
az container create \
  --resource-group myRG \
  --name myContainer \
  --image myacr.azurecr.io/myapp:latest \
  --assign-identity /subscriptions/.../userAssignedIdentities/myIdentity \
  --acr-identity /subscriptions/.../userAssignedIdentities/myIdentity \
  --cpu 2 \
  --memory 4 \
  --ports 443 \
  --restart-policy OnFailure

# Create a container in a VNet (private IP only)
az container create \
  --resource-group myRG \
  --name myPrivateContainer \
  --image myacr.azurecr.io/myapp:latest \
  --vnet myVNet \
  --subnet myAciSubnet \
  --cpu 2 \
  --memory 4 \
  --restart-policy Never

# Create a batch job container (run once, never restart)
az container create \
  --resource-group myRG \
  --name myBatchJob \
  --image myacr.azurecr.io/myjob:latest \
  --restart-policy Never \
  --cpu 4 \
  --memory 8 \
  --environment-variables JOB_ID=12345

# Create a multi-container group (YAML definition)
az container create \
  --resource-group myRG \
  --file container-group.yaml

# Create with Azure Files volume mount
az container create \
  --resource-group myRG \
  --name myContainer \
  --image myacr.azurecr.io/myapp:latest \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name myfileshare \
  --azure-file-volume-mount-path /mnt/data \
  --cpu 1 \
  --memory 2

# Create a GPU container
az container create \
  --resource-group myRG \
  --name myGpuContainer \
  --image myacr.azurecr.io/ml-inference:latest \
  --gpu-count 1 \
  --gpu-sku V100 \
  --cpu 4 \
  --memory 14 \
  --location eastus

# Create a confidential container group
az container create \
  --resource-group myRG \
  --name myConfidentialContainer \
  --image mcr.microsoft.com/aci/skr:latest \
  --sku Confidential \
  --cpu 2 \
  --memory 4 \
  --cce-policy <base64-encoded-policy>

# List container groups
az container list --resource-group myRG --output table
az container list --output table
```

---

## Container Groups — Status and Info

```bash
# Show container group details
az container show \
  --resource-group myRG \
  --name myContainer

# Show specific properties
az container show \
  --resource-group myRG \
  --name myContainer \
  --query "containers[0].instanceView.currentState" \
  --output json

# Get the public IP and FQDN
az container show \
  --resource-group myRG \
  --name myContainer \
  --query "{IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  --output json

# Get container state and events
az container show \
  --resource-group myRG \
  --name myContainer \
  --query "containers[*].instanceView" \
  --output json
```

---

## Container Groups — Logs and Exec

```bash
# Stream container logs (stdout/stderr)
az container logs \
  --resource-group myRG \
  --name myContainer

# Follow logs in real-time
az container logs \
  --resource-group myRG \
  --name myContainer \
  --follow

# Logs from a specific container in a multi-container group
az container logs \
  --resource-group myRG \
  --name myContainer \
  --container-name sidecar

# Open an interactive shell in a running container
az container exec \
  --resource-group myRG \
  --name myContainer \
  --exec-command "/bin/bash"

# Run a non-interactive command
az container exec \
  --resource-group myRG \
  --name myContainer \
  --exec-command "ls -la /mnt/data"

# Open shell in a specific container in a multi-container group
az container exec \
  --resource-group myRG \
  --name myContainer \
  --container-name myapp \
  --exec-command "/bin/sh"
```

---

## Container Groups — Lifecycle

```bash
# Attach to a running container (stream output)
az container attach \
  --resource-group myRG \
  --name myContainer

# Restart a container group (all containers restart)
az container restart \
  --resource-group myRG \
  --name myContainer

# Stop a container group (keeps the resource, stops billing for compute)
az container stop \
  --resource-group myRG \
  --name myContainer

# Start a stopped container group
az container start \
  --resource-group myRG \
  --name myContainer

# Delete a container group
az container delete \
  --resource-group myRG \
  --name myContainer \
  --yes

# Delete all container groups in a resource group
az container list -g myRG --query "[].name" -o tsv | \
  xargs -I {} az container delete -g myRG -n {} --yes
```

---

## Multi-Container Group YAML

```yaml
# container-group.yaml — example multi-container group with sidecar
apiVersion: 2021-10-01
location: eastus
name: myMultiContainerGroup
properties:
  containers:
  - name: myapp
    properties:
      image: myacr.azurecr.io/myapp:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
      ports:
      - port: 8080
        protocol: TCP
      environmentVariables:
      - name: ENVIRONMENT
        value: production
      volumeMounts:
      - name: datavolume
        mountPath: /mnt/data
  - name: log-forwarder
    properties:
      image: mcr.microsoft.com/azure-monitor/containerinsights/ciprod:latest
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
  initContainers:
  - name: db-migrate
    properties:
      image: myacr.azurecr.io/db-migrator:latest
      command:
      - python
      - migrate.py
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - port: 8080
      protocol: TCP
    dnsNameLabel: myapp-aci
  volumes:
  - name: datavolume
    azureFile:
      shareName: myfileshare
      storageAccountName: mystorageaccount
      storageAccountKey: <storage-key>
type: Microsoft.ContainerInstance/containerGroups
```

```bash
# Deploy from YAML
az container create --resource-group myRG --file container-group.yaml
```
