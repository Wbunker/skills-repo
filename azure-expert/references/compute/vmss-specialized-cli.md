# VM Scale Sets & Specialized Compute — CLI Reference

For service concepts, see [vmss-specialized-capabilities.md](vmss-specialized-capabilities.md).

## VM Scale Sets — Create

```bash
# --- Create a Flexible orchestration VMSS (recommended) ---
az vmss create \
  --resource-group myRG \
  --name myVMSS \
  --image Ubuntu2204 \
  --vm-sku Standard_D4s_v5 \
  --instance-count 3 \
  --orchestration-mode Flexible \
  --zones 1 2 3 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --platform-fault-domain-count 1 \
  --storage-sku Premium_LRS

# Create Uniform VMSS with load balancer
az vmss create \
  --resource-group myRG \
  --name myVMSS \
  --image Ubuntu2204 \
  --vm-sku Standard_D4s_v5 \
  --instance-count 2 \
  --orchestration-mode Uniform \
  --zones 1 2 3 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --upgrade-policy-mode Rolling \
  --load-balancer myLB \
  --backend-pool-name myBackendPool

# Create Spot VMSS (evict on delete)
az vmss create \
  --resource-group myRG \
  --name mySpotVMSS \
  --image Ubuntu2204 \
  --vm-sku Standard_D4s_v5 \
  --instance-count 0 \
  --orchestration-mode Flexible \
  --priority Spot \
  --eviction-policy Delete \
  --max-price -1 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub

# List VMSS
az vmss list --resource-group myRG --output table

# Show VMSS details
az vmss show --resource-group myRG --name myVMSS
```

---

## VM Scale Sets — Scale

```bash
# Manually scale to a specific count
az vmss scale \
  --resource-group myRG \
  --name myVMSS \
  --new-capacity 10

# Enable autoscale on a VMSS
az monitor autoscale create \
  --resource-group myRG \
  --name myVMSSAutoscale \
  --resource /subscriptions/.../resourceGroups/myRG/providers/Microsoft.Compute/virtualMachineScaleSets/myVMSS \
  --min-count 2 \
  --max-count 20 \
  --count 3

# Add CPU-based scale-out rule (80% CPU → scale out by 2)
az monitor autoscale rule create \
  --resource-group myRG \
  --autoscale-name myVMSSAutoscale \
  --condition "Percentage CPU > 80 avg 5m" \
  --scale out 2

# Add CPU-based scale-in rule (30% CPU → scale in by 1)
az monitor autoscale rule create \
  --resource-group myRG \
  --autoscale-name myVMSSAutoscale \
  --condition "Percentage CPU < 30 avg 10m" \
  --scale in 1

# Show autoscale settings
az monitor autoscale show --resource-group myRG --name myVMSSAutoscale
```

---

## VM Scale Sets — Update Instances

```bash
# List instances in VMSS
az vmss list-instances \
  --resource-group myRG \
  --name myVMSS \
  --output table

# Update instances to latest VMSS model (after policy/image change)
az vmss update-instances \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids "*"

# Update specific instances
az vmss update-instances \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids 0 1 2

# Reimage instance (clean slate, re-run start config)
az vmss reimage \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids 0

# Reimage all instances
az vmss reimage \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids "*"

# Delete specific instances
az vmss delete-instances \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids 5 6

# Deallocate instances (stops billing for compute)
az vmss deallocate \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids 3 4

# Start deallocated instances
az vmss start \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids 3 4

# Restart instances
az vmss restart \
  --resource-group myRG \
  --name myVMSS \
  --instance-ids "*"
```

---

## VM Scale Sets — Rolling Upgrades

```bash
# Start a rolling upgrade (applies latest VMSS model to all instances)
az vmss rolling-upgrade start \
  --resource-group myRG \
  --name myVMSS

# Cancel an in-progress rolling upgrade
az vmss rolling-upgrade cancel \
  --resource-group myRG \
  --name myVMSS

# Get rolling upgrade status
az vmss rolling-upgrade get-latest \
  --resource-group myRG \
  --name myVMSS

# Update upgrade policy to Rolling
az vmss update \
  --resource-group myRG \
  --name myVMSS \
  --set upgradePolicy.mode=Rolling \
  --set upgradePolicy.rollingUpgradePolicy.maxBatchInstancePercent=20 \
  --set upgradePolicy.rollingUpgradePolicy.maxUnhealthyInstancePercent=20 \
  --set upgradePolicy.rollingUpgradePolicy.maxUnhealthyUpgradedInstancePercent=20 \
  --set upgradePolicy.rollingUpgradePolicy.pauseTimeBetweenBatches=PT5M
```

---

## VM Scale Sets — General Updates

```bash
# Change VM SKU (resize VMSS)
az vmss update \
  --resource-group myRG \
  --name myVMSS \
  --set sku.name=Standard_D8s_v5

# Update image reference
az vmss update \
  --resource-group myRG \
  --name myVMSS \
  --set virtualMachineProfile.storageProfile.imageReference.version=latest

# Enable terminate notification (grace period for scale-in)
az vmss update \
  --resource-group myRG \
  --name myVMSS \
  --set virtualMachineProfile.scheduledEventsProfile.terminateNotificationProfile.enable=true \
  --set virtualMachineProfile.scheduledEventsProfile.terminateNotificationProfile.notBeforeTimeout=PT10M

# Set scale-in policy
az vmss update \
  --resource-group myRG \
  --name myVMSS \
  --scale-in-policy OldestVM

# Delete VMSS
az vmss delete --resource-group myRG --name myVMSS --yes
```

---

## Azure Spring Apps — Create and Deploy

```bash
# Create an Azure Spring Apps instance (Standard tier)
az spring create \
  --resource-group myRG \
  --name mySpringApps \
  --location eastus \
  --sku Standard

# Create an Azure Spring Apps instance (Enterprise tier with Tanzu)
az spring create \
  --resource-group myRG \
  --name myEnterpriseSpring \
  --location eastus \
  --sku Enterprise

# Create an app in Azure Spring Apps
az spring app create \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --instance-count 2 \
  --memory 2Gi \
  --cpu 1

# Deploy a JAR to the app
az spring app deploy \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --artifact-path ./target/myapp-1.0.jar \
  --jvm-options="-Xms512m -Xmx1024m"

# Deploy from source code
az spring app deploy \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --source-path ./

# Scale app instances
az spring app scale \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --instance-count 5

# Show app details and URL
az spring app show \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp

# List apps
az spring app list \
  --resource-group myRG \
  --service mySpringApps \
  --output table

# Stream app logs
az spring app logs \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --follow

# Create a blue-green deployment (deployment slot)
az spring app deployment create \
  --resource-group myRG \
  --service mySpringApps \
  --app myapp \
  --name green \
  --artifact-path ./target/myapp-2.0.jar

# Swap green deployment to active
az spring app set-deployment \
  --resource-group myRG \
  --service mySpringApps \
  --name myapp \
  --deployment green

# Configure Config Server (Standard tier)
az spring config-server git set \
  --resource-group myRG \
  --name mySpringApps \
  --uri https://github.com/myorg/config-repo \
  --label main \
  --search-paths myapp

# Delete Azure Spring Apps service
az spring delete \
  --resource-group myRG \
  --name mySpringApps \
  --yes
```

---

## Azure Dedicated Host — Create

```bash
# Create a Dedicated Host Group
az vm host group create \
  --resource-group myRG \
  --name myHostGroup \
  --platform-fault-domain-count 2 \
  --zone 1 \
  --automatic-placement true

# List available Dedicated Host SKUs
az vm host group list-available-sizes \
  --resource-group myRG \
  --name myHostGroup \
  --location eastus \
  --output table

# Create a Dedicated Host
az vm host create \
  --resource-group myRG \
  --host-group myHostGroup \
  --name myDedicatedHost \
  --sku DSv5-Type1 \
  --platform-fault-domain 0 \
  --auto-replace-on-failure true

# Place a VM on a dedicated host group (auto-placement)
az vm create \
  --resource-group myRG \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_D4s_v5 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --host-group /subscriptions/.../hostGroups/myHostGroup

# Show host utilization
az vm host show \
  --resource-group myRG \
  --host-group myHostGroup \
  --name myDedicatedHost

# List hosts in a group
az vm host list \
  --resource-group myRG \
  --host-group myHostGroup \
  --output table
```
