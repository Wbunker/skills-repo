# Azure Monitor — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"

# Install log-analytics extension if needed
az extension add -n log-analytics
```

---

## Log Analytics Workspace

```bash
# Create a Log Analytics workspace
az monitor log-analytics workspace create \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --location eastus \
  --sku PerGB2018 \
  --retention-time 90 \
  --tags environment=production

# Show workspace details (workspace ID, customer ID)
az monitor log-analytics workspace show \
  --workspace-name myLogWorkspace \
  --resource-group myRG

# Get workspace ID (needed for diagnostic settings)
az monitor log-analytics workspace show \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --query id -o tsv

# Get workspace GUID (customer ID)
az monitor log-analytics workspace show \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --query customerId -o tsv

# Get primary shared key
az monitor log-analytics workspace get-shared-keys \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --query primarySharedKey -o tsv

# List workspaces in resource group
az monitor log-analytics workspace list \
  --resource-group myRG \
  -o table

# Update retention period
az monitor log-analytics workspace update \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --retention-time 180

# Delete workspace (soft delete — 14 days to recover)
az monitor log-analytics workspace delete \
  --workspace-name myLogWorkspace \
  --resource-group myRG \
  --yes

# Recover a soft-deleted workspace
az monitor log-analytics workspace recover \
  --workspace-name myLogWorkspace \
  --resource-group myRG
```

---

## KQL Queries via CLI

```bash
# Run a KQL query against a workspace
az monitor log-analytics query \
  --workspace myLogWorkspace \
  --analytics-query "AzureActivity | where TimeGenerated > ago(1h) | summarize count() by OperationName | order by count_ desc | take 10" \
  --resource-group myRG

# Run query with time span
az monitor log-analytics query \
  --workspace myLogWorkspace \
  --analytics-query "AzureActivity | where OperationNameValue contains 'delete' | project TimeGenerated, Caller, ResourceGroup, OperationNameValue" \
  --resource-group myRG \
  --timespan P1D  # ISO 8601 duration: P1D = last 1 day

# Run query from file
az monitor log-analytics query \
  --workspace myLogWorkspace \
  --analytics-query @query.kql \
  --resource-group myRG \
  --output table

# Query with specific time range
az monitor log-analytics query \
  --workspace myLogWorkspace \
  --analytics-query "Heartbeat | summarize count() by Computer" \
  --resource-group myRG \
  --timespan "2024-01-01T00:00:00Z/2024-01-02T00:00:00Z"
```

---

## Diagnostic Settings

```bash
# Enable diagnostic settings for a storage account
RESOURCE_ID=$(az storage account show --name mystorageaccount --resource-group myRG --query id -o tsv)
WORKSPACE_ID=$(az monitor log-analytics workspace show --workspace-name myLogWorkspace --resource-group myRG --query id -o tsv)

az monitor diagnostic-settings create \
  --name storage-diagnostics \
  --resource $RESOURCE_ID \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category": "StorageRead", "enabled": true, "retentionPolicy": {"enabled": false, "days": 0}},
    {"category": "StorageWrite", "enabled": true, "retentionPolicy": {"enabled": false, "days": 0}},
    {"category": "StorageDelete", "enabled": true, "retentionPolicy": {"enabled": false, "days": 0}}
  ]' \
  --metrics '[{"category": "Transaction", "enabled": true}]'

# Enable for Key Vault (send to both Log Analytics and Storage)
STORAGE_ID=$(az storage account show --name myarchive --resource-group myRG --query id -o tsv)

az monitor diagnostic-settings create \
  --name keyvault-diagnostics \
  --resource $(az keyvault show --name myKV --resource-group myRG --query id -o tsv) \
  --workspace $WORKSPACE_ID \
  --storage-account $STORAGE_ID \
  --logs '[{"category": "AuditEvent", "enabled": true, "retentionPolicy": {"enabled": true, "days": 365}}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'

# Enable for Azure SQL Database
az monitor diagnostic-settings create \
  --name sql-diagnostics \
  --resource $(az sql db show --server myserver --name mydb --resource-group myRG --query id -o tsv) \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category": "SQLInsights", "enabled": true},
    {"category": "QueryStoreRuntimeStatistics", "enabled": true},
    {"category": "Errors", "enabled": true},
    {"category": "Timeouts", "enabled": true}
  ]' \
  --metrics '[{"category": "Basic", "enabled": true}]'

# List diagnostic settings for a resource
az monitor diagnostic-settings list \
  --resource $RESOURCE_ID \
  -o table

# Delete diagnostic settings
az monitor diagnostic-settings delete \
  --name storage-diagnostics \
  --resource $RESOURCE_ID
```

---

## Alerts

### Metric Alerts

```bash
# Create metric alert (static threshold — CPU > 90% for 5 min)
az monitor metrics alert create \
  --name "High CPU Alert" \
  --resource-group myRG \
  --scopes $(az vm show --name myVM --resource-group myRG --query id -o tsv) \
  --condition "avg Percentage CPU > 90" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Alert when CPU exceeds 90%" \
  --action myActionGroup

# Create metric alert with dynamic threshold
az monitor metrics alert create \
  --name "Dynamic HTTP Alert" \
  --resource-group myRG \
  --scopes $(az appservice plan show --name myPlan --resource-group myRG --query id -o tsv) \
  --condition "avg Http5xx > dynamic medium 2 of 4 since 2025-01-01T00:00:00Z" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --action myActionGroup

# List metric alerts
az monitor metrics alert list \
  --resource-group myRG \
  -o table

# Show metric alert
az monitor metrics alert show \
  --name "High CPU Alert" \
  --resource-group myRG

# Update alert (change threshold)
az monitor metrics alert update \
  --name "High CPU Alert" \
  --resource-group myRG \
  --add-condition "avg Percentage CPU > 95"

# Delete alert
az monitor metrics alert delete \
  --name "High CPU Alert" \
  --resource-group myRG
```

### Log Alerts (KQL-based)

```bash
# Create log alert (query-based)
WORKSPACE_ID=$(az monitor log-analytics workspace show --workspace-name myLogWorkspace --resource-group myRG --query id -o tsv)

az monitor scheduled-query create \
  --name "Failed Requests Alert" \
  --resource-group myRG \
  --scopes $WORKSPACE_ID \
  --condition-query "AppRequests | where TimeGenerated > ago(5m) | where Success == false | summarize FailCount=count() | where FailCount > 10" \
  --condition-threshold 0 \
  --condition-operator GreaterThan \
  --condition-time-aggregation Count \
  --evaluation-frequency PT5M \
  --window-duration PT5M \
  --severity 2 \
  --action-groups myActionGroup \
  --description "Alert when more than 10 requests fail in 5 minutes"

# List log alerts
az monitor scheduled-query list \
  --resource-group myRG \
  -o table

# Show log alert
az monitor scheduled-query show \
  --name "Failed Requests Alert" \
  --resource-group myRG

# Delete log alert
az monitor scheduled-query delete \
  --name "Failed Requests Alert" \
  --resource-group myRG \
  --yes
```

### Activity Log Alerts

```bash
# Alert on Service Health incidents
az monitor activity-log alert create \
  --name "Service Health Alert" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=ServiceHealth \
  --action-group myActionGroup \
  --description "Alert on Azure service health events"

# Alert when a specific operation occurs (VM deleted)
az monitor activity-log alert create \
  --name "VM Delete Alert" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id}/resourceGroups/myRG \
  --condition category=Administrative operationName=Microsoft.Compute/virtualMachines/delete status=Succeeded \
  --action-group myActionGroup

# List activity log alerts
az monitor activity-log alert list \
  --resource-group myRG \
  -o table

# Enable/disable alert
az monitor activity-log alert update \
  --name "VM Delete Alert" \
  --resource-group myRG \
  --enabled false

# Delete alert
az monitor activity-log alert delete \
  --name "VM Delete Alert" \
  --resource-group myRG
```

---

## Action Groups

```bash
# Create an action group with email and webhook
az monitor action-group create \
  --name myActionGroup \
  --resource-group myRG \
  --short-name myAG \
  --action email OnCallEngineer "oncall@mycompany.com" \
  --action sms OnCallSMS 1 5551234567 \
  --action webhook MyWebhook https://my-alerts.mycompany.com/webhook true

# Create action group with Azure Function
az monitor action-group create \
  --name myFuncActionGroup \
  --resource-group myRG \
  --short-name funcAG \
  --action azurefunction MyFunc \
    /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{func}/functions/{funcname} \
    false

# Update action group (add recipient)
az monitor action-group update \
  --name myActionGroup \
  --resource-group myRG \
  --add-action email SecondaryEngineer "secondary@mycompany.com"

# List action groups
az monitor action-group list \
  --resource-group myRG \
  -o table

# Enable/disable action group
az monitor action-group enable-receiver \
  --action-group myActionGroup \
  --receiver-name OnCallEngineer \
  --resource-group myRG

# Delete action group
az monitor action-group delete \
  --name myActionGroup \
  --resource-group myRG
```

---

## Autoscale

```bash
# Create autoscale setting for a VM Scale Set
VMSS_ID=$(az vmss show --name myVMSS --resource-group myRG --query id -o tsv)

az monitor autoscale create \
  --resource $VMSS_ID \
  --resource-group myRG \
  --name myVMSS-autoscale \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Add scale-out rule (CPU > 75% → add 1 instance)
az monitor autoscale rule create \
  --autoscale-name myVMSS-autoscale \
  --resource-group myRG \
  --condition "Percentage CPU > 75 avg 5m" \
  --scale out 1 \
  --cooldown 5

# Add scale-in rule (CPU < 25% → remove 1 instance)
az monitor autoscale rule create \
  --autoscale-name myVMSS-autoscale \
  --resource-group myRG \
  --condition "Percentage CPU < 25 avg 10m" \
  --scale in 1 \
  --cooldown 10

# Add a scheduled profile (weekend scale-in)
az monitor autoscale profile create \
  --autoscale-name myVMSS-autoscale \
  --resource-group myRG \
  --name weekend \
  --min-count 1 \
  --max-count 4 \
  --count 1 \
  --recurrence week sa su \
  --timezone "Pacific Standard Time" \
  --start 00:00 \
  --end 23:59

# Show autoscale settings
az monitor autoscale show \
  --name myVMSS-autoscale \
  --resource-group myRG

# List autoscale settings
az monitor autoscale list \
  --resource-group myRG \
  -o table

# Delete autoscale
az monitor autoscale delete \
  --name myVMSS-autoscale \
  --resource-group myRG
```

---

## Application Insights

```bash
# Create workspace-based Application Insights
WORKSPACE_ID=$(az monitor log-analytics workspace show --workspace-name myLogWorkspace --resource-group myRG --query id -o tsv)

az monitor app-insights component create \
  --app myAppInsights \
  --resource-group myRG \
  --location eastus \
  --workspace $WORKSPACE_ID \
  --kind web \
  --application-type web

# Get instrumentation key and connection string
az monitor app-insights component show \
  --app myAppInsights \
  --resource-group myRG \
  --query "instrumentationKey" -o tsv

az monitor app-insights component show \
  --app myAppInsights \
  --resource-group myRG \
  --query "connectionString" -o tsv

# Query App Insights data (Analytics API)
az monitor app-insights query \
  --apps myAppInsights \
  --resource-group myRG \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by resultCode | order by count_ desc"

# Show specific metrics
az monitor app-insights metrics show \
  --apps myAppInsights \
  --resource-group myRG \
  --metric requests/count \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-02T00:00:00Z" \
  --aggregation count \
  --interval PT1H

# List App Insights components
az monitor app-insights component list \
  --resource-group myRG \
  -o table

# Delete App Insights component
az monitor app-insights component delete \
  --app myAppInsights \
  --resource-group myRG
```

---

## Metrics Query

```bash
# List available metrics for a resource
az monitor metrics list-definitions \
  --resource $(az vm show --name myVM --resource-group myRG --query id -o tsv) \
  -o table

# Query metric values
az monitor metrics list \
  --resource $(az vm show --name myVM --resource-group myRG --query id -o tsv) \
  --metric "Percentage CPU" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-02T00:00:00Z" \
  --interval PT1H \
  --aggregation Average \
  -o table

# Query storage account transactions by response type
az monitor metrics list \
  --resource $(az storage account show --name mystorageaccount --resource-group myRG --query id -o tsv) \
  --metric Transactions \
  --filter "ResponseType eq 'Success'" \
  --aggregation Total \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-02T00:00:00Z" \
  --interval PT5M
```

---

## Activity Log

```bash
# List recent activity log events
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

# Filter to a specific resource type
az monitor activity-log list \
  --resource-group myRG \
  --resource-provider Microsoft.KeyVault \
  --start-time "2024-01-01T00:00:00Z" \
  -o table
```
