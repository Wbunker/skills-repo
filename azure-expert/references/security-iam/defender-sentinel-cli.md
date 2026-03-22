# Microsoft Defender for Cloud & Sentinel — CLI Reference

---

## Microsoft Defender for Cloud

### Enable and Configure Defender Plans

```bash
# List available Defender pricing plans (resource types)
az security pricing list \
  --output table

# Show current pricing tier for a specific plan
az security pricing show \
  --name VirtualMachines \
  --output json

# Enable Defender for Servers Plan 2
az security pricing create \
  --name VirtualMachines \
  --tier Standard

# Enable Defender for SQL (Azure SQL databases)
az security pricing create \
  --name SqlServers \
  --tier Standard

# Enable Defender for SQL on VMs
az security pricing create \
  --name SqlServerVirtualMachines \
  --tier Standard

# Enable Defender for Storage (Standard includes malware scanning)
az security pricing create \
  --name StorageAccounts \
  --tier Standard

# Enable Defender for Containers (ACR + AKS)
az security pricing create \
  --name Containers \
  --tier Standard

# Enable Defender for App Service
az security pricing create \
  --name AppServices \
  --tier Standard

# Enable Defender for Key Vault
az security pricing create \
  --name KeyVaults \
  --tier Standard

# Enable Defender for Resource Manager
az security pricing create \
  --name Arm \
  --tier Standard

# Enable Defender for DNS
az security pricing create \
  --name Dns \
  --tier Standard

# Enable Defender CSPM (paid CSPM tier)
az security pricing create \
  --name CloudPosture \
  --tier Standard

# Disable a Defender plan (revert to free)
az security pricing create \
  --name VirtualMachines \
  --tier Free
```

### Security Assessments and Recommendations

```bash
# List all security assessments for a subscription
az security assessment list \
  --output table

# Show a specific assessment (get assessment ID from list output)
az security assessment show \
  --name <assessment-name> \
  --assessed-resource-id /subscriptions/<sub>

# List assessments with High severity
az security assessment list \
  --query "[?status.severity=='High']" \
  --output table

# List Secure Score controls
az security secure-score-controls list \
  --output table

# Show Secure Score for the subscription
az security secure-score list \
  --output table

# Show details of a specific Secure Score
az security secure-score show \
  --name ascScore \
  --output json

# List security tasks (recommendations with remediation)
az security task list \
  --output table
```

### Security Contacts

```bash
# Create a security contact (receives email alerts)
az security contact create \
  --name securityContact \
  --emails "security@contoso.com" \
  --phone "+1-555-555-5555" \
  --alert-notifications On \
  --alerts-to-admins On

# Show security contact configuration
az security contact show \
  --name securityContact

# List all security contacts
az security contact list \
  --output table

# Delete a security contact
az security contact delete \
  --name securityContact
```

### Workspace Settings (Log Analytics for Defender)

```bash
# Configure Log Analytics workspace for Defender for Cloud
az security workspace-setting create \
  --name default \
  --target-workspace /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/myWorkspace

# Show current workspace setting
az security workspace-setting show \
  --name default

# List workspace settings
az security workspace-setting list \
  --output table
```

### Advanced Threat Protection (ATP)

```bash
# Enable ATP for Azure Storage
az security atp storage update \
  --storage-account myStorage \
  --resource-group myRG \
  --is-enabled true

# Show ATP status for a storage account
az security atp storage show \
  --storage-account myStorage \
  --resource-group myRG

# Enable ATP for Cosmos DB
az security atp cosmosdb update \
  --cosmosdb-account myCosmos \
  --resource-group myRG \
  --is-enabled true
```

### Just-in-Time (JIT) VM Access

```bash
# Enable JIT policy on a VM
az security jit-policy update \
  --name myJITPolicy \
  --resource-group myRG \
  --location eastus \
  --virtual-machines '[
    {
      "id": "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM",
      "ports": [
        {
          "number": 22,
          "protocol": "TCP",
          "allowedSourceAddressPrefix": "*",
          "maxRequestAccessDuration": "PT3H"
        },
        {
          "number": 3389,
          "protocol": "TCP",
          "allowedSourceAddressPrefix": "*",
          "maxRequestAccessDuration": "PT3H"
        }
      ]
    }
  ]'

# List JIT policies
az security jit-policy list \
  --resource-group myRG \
  --output table

# Show JIT policy for a VM
az security jit-policy show \
  --name myJITPolicy \
  --resource-group myRG

# Request JIT access to a VM (initiate access)
az security jit-request create \
  --virtual-machines '[
    {
      "id": "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/myVM",
      "ports": [
        {
          "number": 22,
          "duration": "PT2H",
          "allowedSourceAddressPrefix": "203.0.113.10"
        }
      ]
    }
  ]' \
  --justification "Investigating production issue" \
  --location eastus

# List JIT access requests
az security jit-request list \
  --output table
```

### Security Alerts

```bash
# List security alerts
az security alert list \
  --output table

# List alerts filtered by subscription location
az security alert list \
  --location eastus \
  --output table

# Show a specific alert
az security alert show \
  --location eastus \
  --name <alert-name>

# Update alert status (dismiss)
az security alert update \
  --location eastus \
  --name <alert-name> \
  --status Dismissed
```

---

## Microsoft Sentinel

Sentinel uses Log Analytics workspace as its backend. First create/have a workspace, then enable Sentinel on it.

### Workspace Creation and Sentinel Enablement

```bash
# Create a Log Analytics workspace for Sentinel
az monitor log-analytics workspace create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --location eastus \
  --sku PerGB2018 \
  --retention-time 90

# Enable Microsoft Sentinel on the workspace
az sentinel workspace create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --location eastus

# List Log Analytics workspaces
az monitor log-analytics workspace list \
  --resource-group myRG \
  --output table

# Show workspace details (including customer ID needed for agents)
az monitor log-analytics workspace show \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --query "{id:id,customerId:customerId,retentionInDays:retentionInDays}"
```

### Analytics Rules

```bash
# List all analytics rules in Sentinel
az sentinel alert-rule list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --output table

# Show a specific analytics rule
az sentinel alert-rule show \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --rule-id <rule-id>

# Create a scheduled analytics rule (KQL-based detection)
az sentinel alert-rule create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --rule-id myDetectionRule \
  --etag "" \
  --kind Scheduled \
  --display-name "Failed logins followed by success from same IP" \
  --description "Detects brute force followed by successful authentication" \
  --severity High \
  --enabled true \
  --query "SignInLogs | where ResultType != '0' | summarize FailCount=count(), Users=make_set(UserPrincipalName) by IPAddress, bin(TimeGenerated, 5m) | where FailCount > 10 | join kind=inner (SignInLogs | where ResultType == '0') on IPAddress" \
  --query-frequency PT5M \
  --query-period PT1H \
  --trigger-operator GreaterThan \
  --trigger-threshold 0 \
  --suppression-duration PT1H \
  --suppression-enabled false \
  --tactics "CredentialAccess" "InitialAccess"

# Delete an analytics rule
az sentinel alert-rule delete \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --rule-id myDetectionRule \
  --yes
```

### Data Connectors

```bash
# List all data connectors
az sentinel data-connector list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --output table

# Create Azure Active Directory (Entra ID) sign-in logs connector
az sentinel data-connector create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --connector-id AzureActiveDirectory \
  --kind AzureActiveDirectory \
  --tenant-id <tenant-id> \
  --state Enabled

# Create Azure Activity logs connector
az sentinel data-connector create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --connector-id AzureActivity \
  --kind AzureActivity \
  --subscription-id <sub-id>

# Show data connector details
az sentinel data-connector show \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --connector-id AzureActiveDirectory

# Delete a data connector
az sentinel data-connector delete \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --connector-id AzureActivity \
  --yes
```

### Incidents

```bash
# List Sentinel incidents
az sentinel incident list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --output table

# List only active High-severity incidents
az sentinel incident list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --filter "properties/status eq 'Active' and properties/severity eq 'High'" \
  --output table

# Show a specific incident
az sentinel incident show \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id <incident-id>

# Update incident (assign owner, change status)
az sentinel incident update \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id <incident-id> \
  --status Active \
  --severity High \
  --owner '{"objectId": "<user-object-id>"}' \
  --classification TruePositive \
  --classification-comment "Confirmed malicious activity"

# Close an incident as False Positive
az sentinel incident update \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id <incident-id> \
  --status Closed \
  --classification FalsePositive \
  --classification-comment "Expected test activity from security team"

# Create a manual incident
az sentinel incident create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id myManualIncident \
  --title "Manual investigation: suspicious activity in storage" \
  --description "Suspicious access pattern detected via manual review" \
  --severity Medium \
  --status Active

# List incident alerts
az sentinel incident alert list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id <incident-id> \
  --output table

# List incident entities (users, IPs, hosts)
az sentinel incident entity list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --incident-id <incident-id> \
  --output table
```

### Automation Rules

```bash
# List automation rules
az sentinel automation-rule list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --output table

# Create an automation rule (auto-close known false positives)
az sentinel automation-rule create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --automation-rule-id myAutoRule \
  --display-name "Auto-close expected scanner alerts" \
  --order 100 \
  --enabled true \
  --triggers-on Incidents \
  --triggers-when Created \
  --conditions '[{
    "conditionType": "Property",
    "conditionProperties": {
      "propertyName": "IncidentRuleName",
      "operator": "Contains",
      "propertyValues": ["Scanner Sweep"]
    }
  }]' \
  --actions '[{
    "order": 1,
    "actionType": "ModifyProperties",
    "actionConfiguration": {
      "status": "Closed",
      "classification": "BenignPositive",
      "classificationComment": "Expected network scanner activity"
    }
  }]'

# Delete an automation rule
az sentinel automation-rule delete \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --automation-rule-id myAutoRule \
  --yes
```

### Threat Intelligence

```bash
# List threat intelligence indicators
az sentinel threat-intelligence indicator list \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --output table

# Create a threat intelligence indicator (IOC)
az sentinel threat-intelligence indicator create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --indicator-id myIOC \
  --kind indicator \
  --display-name "Known Malicious IP" \
  --pattern "[ipv4-addr:value = '198.51.100.0']" \
  --pattern-type ipv4-addr \
  --threat-types malicious-activity \
  --confidence 90 \
  --labels MaliciousIP

# Query threat intelligence (search for specific indicators)
az sentinel threat-intelligence indicator query-indicators \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --pattern-types ipv4-addr url domain-name
```

---

## Log Analytics Workspace Operations

```bash
# Run a KQL query against the workspace
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "SecurityAlert | where TimeGenerated > ago(24h) | summarize count() by AlertName | order by count_ desc | take 10"

# Run a query with time range
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "SignInLogs | where ResultType != '0' | summarize count() by UserPrincipalName" \
  --timespan "PT24H"

# Update workspace retention period
az monitor log-analytics workspace update \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --retention-time 365

# Configure data export (export specific tables to Storage or Event Hub)
az monitor log-analytics workspace data-export create \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --data-export-name SecurityExport \
  --destination /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.EventHub/namespaces/myEHNamespace \
  --tables SecurityAlert SecurityIncident SignInLogs \
  --enable true

# Get workspace resource ID (needed for Sentinel operations)
az monitor log-analytics workspace show \
  --workspace-name mySentinelWorkspace \
  --resource-group myRG \
  --query id \
  --output tsv
```
