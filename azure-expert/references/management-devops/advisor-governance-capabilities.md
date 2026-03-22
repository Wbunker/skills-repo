# Azure Advisor & Governance — Capabilities

## Azure Advisor

Azure Advisor is a personalized cloud consultant that analyzes your Azure usage and configurations, then recommends best practices to optimize reliability, security, performance, cost, and operational excellence.

**Access**: Azure portal → Advisor, or `az advisor recommendation list`

---

## Advisor Recommendation Pillars

### 1. Reliability (Formerly High Availability)

Recommendations to improve the continuity of business-critical applications:

| Recommendation Type | Examples |
|---|---|
| Availability Zones | Enable zone redundancy for VMs, Storage, SQL DB, App Service |
| Backup | Enable backup for VMs, Azure SQL, Blob Storage soft delete |
| Redundancy | Use availability sets or VMSS for VM workloads |
| Disaster Recovery | Enable geo-replication for Azure SQL, Cosmos DB, Storage |
| Health probes | Configure load balancer health probes correctly |
| Dependency resilience | Circuit breaker patterns, retry policies |

### 2. Security

Security findings surfaced from **Microsoft Defender for Cloud** (formerly Azure Security Center):

| Recommendation Type | Examples |
|---|---|
| Identity | Enable MFA for privileged accounts, disable legacy authentication |
| Network | Close management ports (RDP/SSH) to internet, enable NSG |
| Data | Enable encryption at rest, enable transparent data encryption |
| Compute | Enable Defender for Servers, enable vulnerability assessment |
| Key Vault | Enable soft delete and purge protection |
| Storage | Disable public blob access, enforce HTTPS |

### 3. Performance

Recommendations to improve speed and responsiveness:

| Recommendation Type | Examples |
|---|---|
| Compute | Right-size underutilized VMs, use accelerated networking |
| Database | Enable connection pooling, add missing indexes, enable read replicas |
| Storage | Enable CDN for static content, use Premium storage for high I/O |
| Networking | Use ExpressRoute for high-bandwidth on-premises connectivity |
| Caching | Add Redis cache for frequently read data |
| SQL | Enable Query Store, update statistics, add columnstore indexes |

### 4. Cost

Recommendations to reduce Azure spending:

| Recommendation Type | Examples |
|---|---|
| **Right-size VMs** | Identify and resize underutilized VMs (CPU < 5% avg over 14 days) |
| **Reserved Instances** | Purchase 1-year or 3-year Reserved VM Instances for steady-state workloads |
| **Reserved Capacity** | Reserved capacity for Azure SQL, Cosmos DB, Synapse, Azure Cache |
| **Savings Plans** | Azure Savings Plan for compute (more flexible than RIs) |
| **Unused resources** | Identify unattached disks, idle public IPs, empty App Service Plans |
| **Hybrid Benefit** | Apply Azure Hybrid Benefit (AHUB) to bring Windows Server/SQL Server licenses |
| **Dev/Test** | Use Dev/Test pricing for non-production subscriptions |
| **Storage tiers** | Move infrequently accessed blob data to Cool or Archive tier |
| **Scale down** | Identify oversized resources (VMs, SQL DTUs, App Service Plans) |

### 5. Operational Excellence

Recommendations to improve deployment efficiency and management:

| Recommendation Type | Examples |
|---|---|
| **Service limits** | Alert when approaching subscription/service quotas |
| **Observability** | Enable diagnostic settings, Application Insights |
| **Deprecations** | Use supported VM sizes, update deprecated API versions |
| **IaC adoption** | Manage resources via ARM/Bicep for consistency |
| **Automation** | Use Azure Automation for recurring operational tasks |
| **RBAC** | Remove unused RBAC assignments, use PIM for privileged access |

---

## Advisor Features

### Recommendation Scores

Aggregate scores (0–100) per pillar and overall:
- Score improves as you implement recommendations.
- Track progress over time in Advisor Score dashboard.
- Filter by subscription, resource group, or tag.

### Recommendation Management

| Action | Description |
|---|---|
| **Remediate** | Take immediate action (click to fix for simple changes) |
| **Postpone** | Snooze recommendation for N days |
| **Dismiss** | Permanently dismiss (if not applicable to your scenario) |
| **Download** | Export recommendations as CSV/Excel |

### Advisor Alerts

Create alerts for new Advisor recommendations:

```bash
az monitor activity-log alert create \
  --name "New-Advisor-Recommendations" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=Recommendation \
  --action-group myActionGroup
```

---

## Azure Service Health

Azure Service Health shows the health of Azure services in your regions and subscriptions.

### Service Health Components

| Component | Description |
|---|---|
| **Service Issues** | Active Azure platform problems affecting your services — outages, partial degradations |
| **Planned Maintenance** | Upcoming maintenance that may affect your resources |
| **Health Advisories** | Changes requiring customer action (deprecations, feature retirements, migration guidance) |
| **Security Advisories** | Security-related communications for Azure services |

### Service Health Alerts

Configure alerts to receive notifications for events affecting your services/regions:

```bash
# Create Service Health alert for your subscription + regions
az monitor activity-log alert create \
  --name "Service-Health-Eastus" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=ServiceHealth \
  --condition regions=eastus,westus2 \
  --action-group myActionGroup \
  --description "Alert for Service Health events in East US and West US 2"

# Alert only for incidents (not maintenance or advisories)
az monitor activity-log alert create \
  --name "Service-Incidents-Only" \
  --resource-group myRG \
  --scope /subscriptions/{sub-id} \
  --condition category=ServiceHealth properties.incidentType=Incident \
  --action-group myActionGroup
```

### Incident Impact

Service Health shows:
- Which of your specific resources are affected.
- Preliminary root cause investigation.
- Mitigation steps taken.
- Final Root Cause Analysis (RCA) after resolution.

---

## Resource Health

Granular health status for individual Azure resources:

| Status | Meaning |
|---|---|
| **Available** | Resource is healthy and operating normally |
| **Unavailable** | Resource is currently unavailable (Azure or customer caused) |
| **Degraded** | Resource is available but operating at reduced capacity |
| **Unknown** | Health data not updated in > 10 minutes |

### Health Events

- **Platform-initiated**: Azure infrastructure issues, maintenance.
- **User-initiated**: Actions taken by you (restart, redeploy).

### Historical Health

View health history for the last 30 days — identify recurring issues and their root causes.

**Access**: Azure portal → Resource blade → Diagnose and solve problems → Resource Health, or REST API.

---

## Activity Log

The Azure Activity Log is a subscription-level platform log recording every operation on Azure resources.

### What is Recorded

- **Administrative**: Resource create/update/delete operations (Azure Portal, CLI, SDKs, ARM templates).
- **Service Health**: Azure service health events.
- **Resource Health**: Individual resource health changes.
- **Alert**: Alert firing and resolution events.
- **Autoscale**: Autoscale engine events.
- **Recommendation**: Advisor recommendation events.
- **Policy**: Azure Policy evaluation results.
- **Security**: Defender for Cloud alerts.

### Activity Log Record Fields

| Field | Description |
|---|---|
| `EventTimestamp` | When the operation occurred |
| `Caller` | User, SP, or system that initiated the operation |
| `OperationName` | Resource type and operation (e.g., `Microsoft.Storage/storageAccounts/write`) |
| `ResourceGroup` | Resource group of the affected resource |
| `ResourceId` | Full ARM resource ID |
| `Status` | Accepted / Started / Succeeded / Failed |
| `SubStatus` | HTTP status code of underlying REST operation |
| `CorrelationId` | Links related operations from same request |

### Activity Log Retention

- **Built-in retention**: 90 days in Activity Log blade.
- **Archive to Log Analytics**: 30–730 days interactive + 7 years archive.
- **Archive to Storage**: Long-term retention in JSON format.
- **Stream to Event Hubs**: Real-time integration with SIEM or custom processing.

```bash
# Route Activity Log to all destinations
az monitor diagnostic-settings create \
  --name "ActivityLog-to-all" \
  --resource /subscriptions/{sub-id} \
  --workspace <log-analytics-workspace-id> \
  --storage-account <storage-account-id> \
  --event-hub-rule <event-hub-auth-rule-id> \
  --logs '[{"category": "Administrative", "enabled": true},
           {"category": "Security", "enabled": true},
           {"category": "ServiceHealth", "enabled": true},
           {"category": "Alert", "enabled": true},
           {"category": "Recommendation", "enabled": true},
           {"category": "Policy", "enabled": true},
           {"category": "Autoscale", "enabled": true},
           {"category": "ResourceHealth", "enabled": true}]'
```

### Common KQL Queries on Activity Log

```kusto
// Who deleted a resource in the last 30 days?
AzureActivity
| where TimeGenerated > ago(30d)
| where OperationNameValue endswith "/delete"
| where ActivityStatusValue == "Succeeded"
| project TimeGenerated, Caller, ResourceGroup, Resource, OperationNameValue
| order by TimeGenerated desc

// Failed operations by caller
AzureActivity
| where TimeGenerated > ago(7d)
| where ActivityStatusValue == "Failed"
| summarize FailCount=count() by Caller
| order by FailCount desc

// All operations on a specific resource
AzureActivity
| where TimeGenerated > ago(30d)
| where ResourceId contains "myStorageAccount"
| project TimeGenerated, Caller, OperationNameValue, ActivityStatusValue
| order by TimeGenerated desc

// RBAC changes (role assignments)
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue contains "roleAssignment"
| project TimeGenerated, Caller, ResourceGroup, OperationNameValue, Properties
| order by TimeGenerated desc

// Service Health events affecting my subscription
AzureActivity
| where TimeGenerated > ago(30d)
| where CategoryValue == "ServiceHealth"
| project TimeGenerated, OperationNameValue, Level, Properties
| order by TimeGenerated desc
```

---

## Azure Policy (Governance)

Azure Policy enforces organizational standards and compliance at scale.

### Policy Concepts

| Concept | Description |
|---|---|
| **Policy Definition** | Rule that evaluates resource properties against a condition |
| **Initiative Definition** | Collection of policies grouped for a compliance goal |
| **Assignment** | Apply a policy/initiative to a scope (MG, subscription, RG) |
| **Compliance** | Percentage of resources compliant with assigned policies |
| **Remediation** | Auto-fix non-compliant resources using managed identity |

### Built-in Policy Categories

| Category | Example Policies |
|---|---|
| **General** | Allowed resource types, allowed locations, require tags |
| **Compute** | Allowed VM SKUs, require disk encryption, enable Azure Monitor |
| **Security** | Require HTTPS on Storage, disable public blob access |
| **Monitoring** | Deploy diagnostic settings, require Log Analytics agent |
| **SQL** | Require TDE, enable Advanced Data Security |
| **Network** | Deny RDP from internet, require NSG on subnets |
| **Tags** | Require specific tags, inherit tags from resource group |

### Policy Effect Types

| Effect | Description |
|---|---|
| `Deny` | Block non-compliant resource creation/update |
| `Audit` | Mark as non-compliant, no blocking |
| `AuditIfNotExists` | Audit if related resource doesn't exist |
| `DeployIfNotExists` | Auto-deploy related resource if missing |
| `Modify` | Add/update/remove tags or properties on create/update |
| `Append` | Add fields to resource during create |
| `Disabled` | Policy not evaluated |

### Common Policy Assignments

```bash
# Assign built-in policy: Require HTTPS on Storage Accounts
az policy assignment create \
  --name RequireHTTPS \
  --display-name "Storage accounts should use HTTPS" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9" \
  --scope /subscriptions/{sub-id} \
  --enforcement-mode Default  # or DoNotEnforce (audit only)

# Assign built-in initiative: Azure Security Benchmark
az policy assignment create \
  --name AzureSecurityBenchmark \
  --policy-set-definition "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8" \
  --scope /subscriptions/{sub-id}

# Check compliance state
az policy state summarize --subscription {sub-id}
```
