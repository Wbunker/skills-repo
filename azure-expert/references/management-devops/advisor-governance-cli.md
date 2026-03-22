# Azure Advisor & Governance — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"
```

---

## Azure Advisor

```bash
# List all recommendations for current subscription
az advisor recommendation list \
  -o table

# List recommendations with details
az advisor recommendation list \
  --output json | jq '.[] | {category: .category, impact: .impact, resourceId: .resourceId, problem: .shortDescription.problem}'

# Filter by category
az advisor recommendation list \
  --category Cost \
  -o table

az advisor recommendation list \
  --category Security \
  -o table

az advisor recommendation list \
  --category Reliability \
  -o table

az advisor recommendation list \
  --category Performance \
  -o table

az advisor recommendation list \
  --category OperationalExcellence \
  -o table

# Filter by impact level
az advisor recommendation list \
  --category Cost \
  --query "[?impact=='High']" \
  -o table

# Filter for specific resource group
az advisor recommendation list \
  --query "[?contains(resourceGroup, 'myRG')]" \
  -o table

# Show specific recommendation details
az advisor recommendation show \
  --recommendation-name <recommendation-name> \
  --resource-group myRG \
  --recommendation-id <recommendation-id>

# Show Advisor score by category
az advisor score list \
  -o table

# Show Advisor score for specific category
az advisor score list \
  --query "[?categoryName=='Cost'].score" \
  -o tsv

# Disable a specific recommendation (suppress)
az advisor recommendation disable \
  --recommendation-name <recommendation-name> \
  --resource-group myRG \
  --days 30  # snooze for 30 days (0 = permanent)

# Re-enable a previously disabled recommendation
az advisor recommendation enable \
  --recommendation-name <recommendation-name> \
  --resource-group myRG

# Generate recommendations (trigger fresh analysis)
az advisor recommendation generate \
  --subscription <sub-id>
```

---

## Service Health (via Activity Log and Monitor)

Service Health events are accessed via the Azure Monitor Activity Log and REST API. The Azure CLI does not have dedicated `az servicehealth` commands.

```bash
# List recent Service Health events from Activity Log
az monitor activity-log list \
  --subscription {sub-id} \
  --start-time "2024-01-01T00:00:00Z" \
  --query "[?category.value=='ServiceHealth']" \
  --output table

# Service Health events in specific region
az monitor activity-log list \
  --subscription {sub-id} \
  --start-time "2024-01-01T00:00:00Z" \
  --query "[?category.value=='ServiceHealth' && contains(resourceId, 'eastus')]" \
  --output json

# Create Service Health alert (via Activity Log Alert)
az monitor activity-log alert create \
  --name "Service-Health-Alert" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=ServiceHealth \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv) \
  --description "Alert on all Service Health events"

# Alert on Service Health for specific regions
az monitor activity-log alert create \
  --name "EastUS-Service-Health" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=ServiceHealth \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv) \
  --description "Alert on Service Health in East US"

# Alert only for active incidents (not maintenance/advisory)
az monitor activity-log alert create \
  --name "Service-Incidents-Only" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition "category=ServiceHealth and properties.incidentType=Incident" \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv)

# Query Service Health events via Log Analytics (if Activity Log routed to workspace)
az monitor log-analytics query \
  --workspace myLogWorkspace \
  --resource-group myRG \
  --analytics-query "
    AzureActivity
    | where TimeGenerated > ago(30d)
    | where CategoryValue == 'ServiceHealth'
    | project TimeGenerated, OperationNameValue, Level, Properties
    | order by TimeGenerated desc
  "
```

---

## Activity Log

```bash
# List activity log events (current subscription, last 24 hours)
az monitor activity-log list \
  --start-time "$(date -u -d '24 hours ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-24H '+%Y-%m-%dT%H:%M:%SZ')" \
  -o table

# List activity log for specific resource group
az monitor activity-log list \
  --resource-group myRG \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-02T00:00:00Z" \
  -o table

# Filter to failed operations
az monitor activity-log list \
  --resource-group myRG \
  --start-time "2024-01-01T00:00:00Z" \
  --status Failed \
  -o table

# Filter by operation name
az monitor activity-log list \
  --resource-group myRG \
  --start-time "2024-01-01T00:00:00Z" \
  --query "[?operationName.localizedValue contains 'delete']" \
  -o table

# Filter by caller (specific user or service principal)
az monitor activity-log list \
  --caller "user@mycompany.com" \
  --start-time "2024-01-01T00:00:00Z" \
  -o table

# Filter by resource provider
az monitor activity-log list \
  --resource-provider Microsoft.KeyVault \
  --start-time "2024-01-01T00:00:00Z" \
  -o table

# Show detailed information for specific event
az monitor activity-log list \
  --resource-group myRG \
  --start-time "2024-01-01T00:00:00Z" \
  --status Failed \
  --output json | jq '.[] | {time: .eventTimestamp, caller: .caller, operation: .operationName.localizedValue, status: .status.localizedValue, error: .properties.statusMessage}'

# Create Activity Log alert for specific operations
az monitor activity-log alert create \
  --name "VM-Delete-Alert" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id}/resourceGroups/myRG \
  --condition category=Administrative operationName=Microsoft.Compute/virtualMachines/delete status=Succeeded \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv) \
  --description "Alert when a VM is deleted in myRG"

# Alert on Key Vault access policy changes
az monitor activity-log alert create \
  --name "KV-Policy-Change" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=Administrative operationName=Microsoft.KeyVault/vaults/accessPolicies/write \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv)

# Alert on RBAC role assignment creation
az monitor activity-log alert create \
  --name "RBAC-Assignment-Alert" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=Administrative operationName=Microsoft.Authorization/roleAssignments/write status=Succeeded \
  --action-group $(az monitor action-group show --name myActionGroup --resource-group myRG --query id -o tsv)

# List all activity log alerts
az monitor activity-log alert list \
  --resource-group myRG \
  -o table

# Enable/disable an alert
az monitor activity-log alert update \
  --name "VM-Delete-Alert" \
  --resource-group myRG \
  --enabled false

# Delete an alert
az monitor activity-log alert delete \
  --name "VM-Delete-Alert" \
  --resource-group myRG
```

---

## Resource Health (via REST API)

Resource Health does not have full Azure CLI support. Use the REST API or Azure portal.

```bash
# Get current health status of a VM
RESOURCE_ID="/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/myVM"
TOKEN=$(az account get-access-token --query accessToken -o tsv)

curl -s "https://management.azure.com${RESOURCE_ID}/providers/Microsoft.ResourceHealth/availabilityStatuses/current?api-version=2022-10-01" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '{resourceId: .id, status: .properties.availabilityState, reason: .properties.reasonType, summary: .properties.summary}'

# List health history for a resource
curl -s "https://management.azure.com${RESOURCE_ID}/providers/Microsoft.ResourceHealth/availabilityStatuses?api-version=2022-10-01" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.value[] | {time: .properties.occurredTime, status: .properties.availabilityState, reason: .properties.reasonType}'

# Get health status for all resources in subscription
curl -s "https://management.azure.com/subscriptions/{sub}/providers/Microsoft.ResourceHealth/availabilityStatuses?api-version=2022-10-01" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.value[] | select(.properties.availabilityState != "Available") | {resource: .name, status: .properties.availabilityState}'
```

---

## Azure Policy

```bash
# List built-in policy definitions (filter by category)
az policy definition list \
  --query "[?policyType=='BuiltIn' && metadata.category=='Storage']" \
  --output table

# Search for specific policy
az policy definition list \
  --query "[?contains(displayName, 'HTTPS')]" \
  -o table

# Show policy definition details
az policy definition show \
  --name "404c3081-a854-4457-ae30-26a93ef643f9"  # built-in HTTPS storage policy

# Create custom policy definition
az policy definition create \
  --name "require-resource-tags" \
  --display-name "Require specific tags on resources" \
  --description "Requires environment and team tags on all resources" \
  --rules @policy-rules.json \
  --params @policy-params.json \
  --mode Indexed \
  --metadata '{"category": "Tags"}'

# List policy assignments
az policy assignment list \
  --scope /subscriptions/{sub-id} \
  -o table

# Assign a built-in policy
az policy assignment create \
  --name "require-https-storage" \
  --display-name "Storage accounts must use HTTPS" \
  --policy "404c3081-a854-4457-ae30-26a93ef643f9" \
  --scope /subscriptions/{sub-id} \
  --enforcement-mode Default

# Assign policy to resource group only
az policy assignment create \
  --name "require-tags-myrg" \
  --display-name "Require tags in myRG" \
  --policy "require-resource-tags" \
  --scope /subscriptions/{sub-id}/resourceGroups/myRG \
  --params '{"tagName": {"value": "environment"}}'

# Assign in audit mode (no enforcement, just reporting)
az policy assignment create \
  --name "audit-no-public-storage" \
  --policy "4fa4b6c0-31ca-4c0d-b10d-24b96f62a751" \
  --scope /subscriptions/{sub-id} \
  --enforcement-mode DoNotEnforce

# Show policy compliance state
az policy state summarize \
  --subscription {sub-id}

# Show non-compliant resources for an assignment
az policy state list \
  --policy-assignment "require-https-storage" \
  --filter "complianceState eq 'NonCompliant'" \
  -o table

# Create remediation task for non-compliant resources
az policy remediation create \
  --name remediate-https-storage \
  --policy-assignment "require-https-storage" \
  --resource-group myRG

# List remediation tasks
az policy remediation list -o table

# Show remediation status
az policy remediation show --name remediate-https-storage

# Delete policy assignment
az policy assignment delete \
  --name "require-https-storage" \
  --scope /subscriptions/{sub-id}
```

---

## Azure Advisor Score Report Script

```bash
#!/bin/bash
# Generate Advisor recommendation report

echo "=== Azure Advisor Recommendations Summary ==="
echo ""

for category in Cost Security Reliability Performance OperationalExcellence; do
  echo "--- $category ---"
  COUNT=$(az advisor recommendation list --category $category --query "length(@)" -o tsv 2>/dev/null)
  HIGH=$(az advisor recommendation list --category $category --query "[?impact=='High'] | length(@)" -o tsv 2>/dev/null)
  echo "Total: $COUNT | High Impact: $HIGH"
  az advisor recommendation list --category $category \
    --query "[?impact=='High'].{ResourceGroup:resourceGroup, Problem:shortDescription.problem}" \
    -o table 2>/dev/null | head -10
  echo ""
done

echo "=== Overall Score ==="
az advisor score list -o table
```
