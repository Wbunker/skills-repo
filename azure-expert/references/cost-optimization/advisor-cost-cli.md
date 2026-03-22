# Azure Advisor & Cost Management — CLI Reference
For service concepts, see [advisor-cost-capabilities.md](advisor-cost-capabilities.md).

## Azure Cost Management

```bash
# --- Cost queries ---
# Query cost for a subscription in the last 30 days (grouped by service)
az costmanagement query \
  --scope /subscriptions/{subId} \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-granularity None \
  --dataset-grouping name=ServiceName type=Dimension \
  --query "properties.rows" \
  --output json

# Query cost grouped by resource group (last month)
az costmanagement query \
  --scope /subscriptions/{subId} \
  --type ActualCost \
  --timeframe LastMonth \
  --dataset-granularity None \
  --dataset-grouping name=ResourceGroup type=Dimension \
  --output json

# Query daily cost for the current month
az costmanagement query \
  --scope /subscriptions/{subId} \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-granularity Daily \
  --output json

# Query amortized cost (reservations distributed to resources)
az costmanagement query \
  --scope /subscriptions/{subId} \
  --type AmortizedCost \
  --timeframe LastMonth \
  --dataset-granularity None \
  --dataset-grouping name=ResourceId type=Dimension \
  --output json

# Query cost for a specific resource group
az costmanagement query \
  --scope /subscriptions/{subId}/resourceGroups/myRG \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-granularity None \
  --dataset-grouping name=ResourceType type=Dimension \
  --output json

# Query cost filtered to a specific tag value
az costmanagement query \
  --scope /subscriptions/{subId} \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-granularity None \
  --dataset-filter "$(cat <<'EOF'
{
  "and": [
    {
      "dimensions": {
        "name": "TagValue",
        "operator": "In",
        "values": ["production"]
      }
    }
  ]
}
EOF
)" \
  --dataset-grouping name=ServiceName type=Dimension \
  --output json
```

## Cost Management Exports

```bash
# --- Create cost exports to Azure Storage ---
# Create a daily ActualCost export (current month, updated daily)
az costmanagement export create \
  --name DailyActualCost \
  --type ActualCost \
  --scope /subscriptions/{subId} \
  --storage-account-id /subscriptions/{subId}/resourceGroups/costRG/providers/Microsoft.Storage/storageAccounts/costExportsStorage \
  --storage-container costexports \
  --storage-directory subscriptions/{subId} \
  --recurrence Daily \
  --recurrence-period from="2025-01-01T00:00:00Z" to="2026-01-01T00:00:00Z"

# Create a monthly AmortizedCost export (for charge-back with reservations)
az costmanagement export create \
  --name MonthlyAmortized \
  --type AmortizedCost \
  --scope /subscriptions/{subId} \
  --storage-account-id /subscriptions/{subId}/resourceGroups/costRG/providers/Microsoft.Storage/storageAccounts/costExportsStorage \
  --storage-container amortized \
  --recurrence Monthly \
  --recurrence-period from="2025-01-01T00:00:00Z" to="2026-01-01T00:00:00Z"

# Create an export at management group scope (org-wide)
az costmanagement export create \
  --name OrgWideMonthly \
  --type ActualCost \
  --scope /providers/Microsoft.Management/managementGroups/{mgId} \
  --storage-account-id /subscriptions/{subId}/resourceGroups/costRG/providers/Microsoft.Storage/storageAccounts/costExportsStorage \
  --storage-container org-costs \
  --recurrence Monthly \
  --recurrence-period from="2025-01-01T00:00:00Z" to="2026-01-01T00:00:00Z"

# List exports for a scope
az costmanagement export list \
  --scope /subscriptions/{subId} \
  --output table

# Show export details
az costmanagement export show \
  --name DailyActualCost \
  --scope /subscriptions/{subId}

# Manually trigger an export run (ad-hoc export)
az costmanagement export run \
  --name DailyActualCost \
  --scope /subscriptions/{subId}

# Delete an export
az costmanagement export delete \
  --name DailyActualCost \
  --scope /subscriptions/{subId} \
  --yes
```

## Budgets

```bash
# --- Create budgets ---
# Create a monthly budget for a subscription with email alert at 80% and 100%
az consumption budget create \
  --budget-name MonthlyProductionBudget \
  --amount 10000 \
  --time-grain Monthly \
  --start-date 2025-01-01 \
  --end-date 2026-12-31 \
  --resource-group-filter myProdRG \
  --category Cost \
  --email-contacts admin@contoso.com finops@contoso.com

# Create budget with thresholds at 50%, 80%, 100%, and 120% (forecasted)
az consumption budget create \
  --budget-name DevSubscriptionBudget \
  --amount 2000 \
  --time-grain Monthly \
  --start-date 2025-01-01 \
  --end-date 2026-12-31 \
  --category Cost \
  --thresholds 50 80 100 120 \
  --email-contacts dev-lead@contoso.com

# List all budgets in a subscription
az consumption budget list \
  --output table

# Show a specific budget (including current spend and threshold status)
az consumption budget show \
  --budget-name MonthlyProductionBudget \
  --output json

# Delete a budget
az consumption budget delete \
  --budget-name MonthlyProductionBudget
```

## Usage Data

```bash
# --- Consumption usage queries ---
# List usage for a subscription in the last month
az consumption usage list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --query "[].{Date:usageStart, Resource:instanceName, Cost:pretaxCost, Currency:currency, Meter:meterName}" \
  --output table

# List usage filtered to a specific resource group
az consumption usage list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --query "[?contains(instanceId, 'myProductionRG')].{Date:usageStart, Resource:instanceName, Cost:pretaxCost}" \
  --output table

# Get top 20 most expensive resources last month
az consumption usage list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --query "sort_by([].{Resource:instanceName, RG:resourceGroup, Cost:pretaxCost}, &Cost) | reverse(@) | [0:20]" \
  --output table

# List marketplace usage (3rd-party charges)
az consumption marketplace list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --query "[].{Date:usageStart, Publisher:publisherName, Plan:planName, Cost:pretaxCost}" \
  --output table
```

## Azure Advisor — Cost Recommendations

```bash
# --- List Advisor recommendations ---
# List all Cost category recommendations in subscription
az advisor recommendation list \
  --category Cost \
  --output table

# List recommendations with full details
az advisor recommendation list \
  --category Cost \
  --query "[].{ResourceId:resourceId, ResourceType:resourceType, Impact:impact, ShortDesc:shortDescription.solution, Savings:extendedProperties.annualSavingsAmount}" \
  --output table

# List only High impact cost recommendations
az advisor recommendation list \
  --category Cost \
  --query "[?impact=='High'].{ResourceId:resourceId, Impact:impact, Solution:shortDescription.solution}" \
  --output table

# List recommendations for a specific resource group
az advisor recommendation list \
  --category Cost \
  --resource-group myRG \
  --output table

# Show full recommendation details (problem, solution, potential savings)
az advisor recommendation describe \
  --recommendation-id {recommendation-id} \
  --resource-group myRG \
  --resource-name myVM \
  --resource-type Microsoft.Compute/virtualMachines

# Dismiss a recommendation (suppress for 1 day, 7 days, etc.)
az advisor recommendation disable \
  --recommendation-id {recommendation-id} \
  --resource-group myRG \
  --resource-name myVM \
  --resource-type Microsoft.Compute/virtualMachines \
  --days 7

# Re-enable a dismissed recommendation
az advisor recommendation enable \
  --recommendation-id {recommendation-id} \
  --resource-group myRG \
  --resource-name myVM \
  --resource-type Microsoft.Compute/virtualMachines

# --- Configure Advisor settings ---
# Configure VM right-sizing CPU threshold (default is 5%)
az advisor configuration update \
  --low-cpu-threshold 15 \
  --resource-group myRG

# --- Advisor score ---
# Get Advisor score by category
az advisor score list \
  --output table

# Get Advisor score for a specific category
az advisor score show \
  --category Cost
```

## Cost Governance Helper Commands

```bash
# --- Identify untagged resources (cost allocation gap) ---
# Find resources missing a required tag (e.g., CostCenter)
az resource list \
  --query "[?tags.CostCenter == null].{Name:name, RG:resourceGroup, Type:type}" \
  --output table

# Find resources missing ALL tags
az resource list \
  --query "[?!tags].{Name:name, RG:resourceGroup, Type:type, Location:location}" \
  --output table

# --- Find idle/orphaned resources ---
# Find unattached managed disks (potential waste)
az disk list \
  --query "[?managedBy == null].{Name:name, RG:resourceGroup, SKU:sku.name, SizeGB:diskSizeGb, Location:location}" \
  --output table

# Find unattached public IPs
az network public-ip list \
  --query "[?ipConfiguration == null].{Name:name, RG:resourceGroup, SKU:sku.name, Location:location}" \
  --output table

# Find empty App Service Plans (no apps)
az appservice plan list \
  --query "[?numberOfSites==\`0\`].{Name:name, RG:resourceGroup, SKU:sku.name, Location:location}" \
  --output table

# Find stopped VMs that are still incurring disk costs
az vm list \
  --show-details \
  --query "[?powerState=='VM deallocated'].{Name:name, RG:resourceGroup, Size:hardwareProfile.vmSize, OS:storageProfile.osDisk.osType}" \
  --output table

# --- Auto-shutdown for dev VMs ---
# Enable auto-shutdown at 7 PM UTC for a VM
az vm auto-shutdown \
  --resource-group devRG \
  --name myDevVM \
  --time 1900

# Disable auto-shutdown
az vm auto-shutdown \
  --resource-group devRG \
  --name myDevVM \
  --off

# --- Storage lifecycle analysis ---
# List storage accounts and their access tier
az storage account list \
  --query "[].{Name:name, RG:resourceGroup, Kind:kind, AccessTier:accessTier, SKU:sku.name}" \
  --output table
```
