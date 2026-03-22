# Azure Advisor & Cost Management — Capabilities Reference
For CLI commands, see [advisor-cost-cli.md](advisor-cost-cli.md).

## Microsoft Cost Management + Billing

**Purpose**: Built-in Azure service for monitoring, allocating, and optimizing cloud spending. Provides visibility into cost and usage data, budget controls, and actionable savings recommendations.

---

## Cost Analysis

Interactive spending exploration across any scope in your Azure environment.

### Scopes
| Scope | Description |
|---|---|
| **Management Group** | Cross-subscription aggregated view (enterprise-wide) |
| **Billing Account / Enrollment** | EA agreement-level view; full charge-back data |
| **Subscription** | All costs within one subscription |
| **Resource Group** | Costs for resources in a specific RG |
| **Resource** | Individual resource cost breakdown |

### Cost Analysis Views

| View | Description |
|---|---|
| **Actual cost** | Real cash spend as billed; reservations appear as one-time purchase |
| **Amortized cost** | Reservation and Savings Plan costs distributed daily across consuming resources; preferred for charge-back |
| **Budget vs actual** | Side-by-side actual spend vs configured budget |
| **Cost by resource** | Granular per-resource cost breakdown |
| **Cost by service** | Aggregated by Azure service type (Compute, Storage, Networking, etc.) |
| **Cost by tag** | Cost grouped by tag key-value; requires consistent tagging policy |
| **Forecast** | 30-day spend forecast based on historical trend |

### Grouping and Filtering Dimensions

Cost Analysis can group and filter by:
- Resource group, resource, service name, meter category, meter subcategory
- Location/region, subscription
- Tag values (any tag applied to resources)
- Charge type (usage, purchase, refund, adjustment)
- Resource type (e.g., `Microsoft.Compute/virtualMachines`)
- Publisher type (Azure, Marketplace, reservation)

### Tagging Strategy for Cost Allocation

Consistent resource tagging enables meaningful cost breakdown:

| Tag Key | Purpose | Example Values |
|---|---|---|
| `CostCenter` | Financial charge-back to business unit | `cc-1234`, `marketing`, `engineering` |
| `Environment` | Separate prod vs dev/test spend | `production`, `staging`, `development` |
| `Application` | Per-application cost tracking | `crm-system`, `data-platform` |
| `Owner` | Resource owner accountability | `john.doe@contoso.com`, `platform-team` |
| `Project` | Project-based billing | `project-alpha`, `migration-2025` |

**Enforce tagging via Azure Policy:**
```json
{
  "if": {
    "field": "[concat('tags[', parameters('tagName'), ']')]",
    "exists": "false"
  },
  "then": {
    "effect": "deny"
  }
}
```
Use built-in policy `"Require a tag on resource groups"` to block resource group creation without required tags.

---

## Budgets

Set spend thresholds with automated alerts and action triggers.

### Budget Configuration

| Setting | Description |
|---|---|
| **Amount** | Monthly, quarterly, or annual budget in local currency |
| **Time period** | Month (most common), Quarter, Annual, Custom date range |
| **Scope** | Subscription, resource group, management group, or billing scope |
| **Filters** | Narrow budget to specific services, resource groups, tags, or locations |

### Budget Alerts

| Alert Type | Threshold | Action |
|---|---|---|
| **Actual** | X% of budget has been spent | Notification (email) or action group |
| **Forecasted** | Forecast predicts X% of budget will be spent | Notification or action group |
| **Budget reset** | Budget resets (new period starts) | Notification |

### Action Groups with Budgets

When a budget alert fires, it can trigger an action group to:
- Send email notifications to cost owners
- Send SMS or push notification
- Call a Logic App (e.g., to enforce policy, stop VMs, or notify Slack)
- Call an Azure Function (e.g., deallocate dev VMs when budget exceeded)
- Send to Event Hub for downstream processing

```json
{
  "actionGroups": [
    {
      "actionGroupId": "/subscriptions/{subId}/resourceGroups/myRG/providers/microsoft.insights/actionGroups/costAlerts",
      "webhookProperties": {
        "budgetName": "MonthlyDevBudget"
      }
    }
  ]
}
```

---

## Cost Alerts

| Alert Type | Description | Trigger |
|---|---|---|
| **Budget alerts** | Spending exceeds budget threshold | Configurable % of budget |
| **Anomaly alerts** | AI/ML detects unusual spending spike vs baseline | Automated; no threshold configuration needed |
| **Credit alerts** | Azure credit balance is low (Enterprise only) | Configurable % of credit remaining |
| **Department spending quota alerts** | Department quota approaching limit (EA only) | Configurable % |

### Anomaly Detection
- Azure automatically establishes a spending baseline from historical patterns
- Alerts when actual spend deviates significantly from expected pattern
- Useful for detecting runaway resources, unexpected new costs, or billing errors
- Configure recipients in Cost Management → Cost Alerts → Anomaly Alerts

---

## Cost Allocation

Enable charge-back and show-back for shared costs.

| Feature | Description |
|---|---|
| **Cost allocation rules** | Redistribute costs from a shared subscription/RG to target subscriptions/RGs based on rules |
| **Split by percentage** | Allocate X% of shared service cost to each business unit |
| **Split by tag** | Proportionally split shared costs based on resource tags in target scopes |
| **Amortized view** | Show-back reservation costs distributed across consuming resources |

**Use case**: A central IT subscription runs shared services (Azure Firewall, VPN Gateway, DNS). Cost allocation rules redistribute these shared costs proportionally to each business unit subscription for accurate charge-back.

---

## Cost Exports

Schedule automated export of cost and usage data to Azure Blob Storage for analysis in external tools.

| Export Type | Description |
|---|---|
| **Daily export of month-to-date costs** | Current month costs updated daily (good for real-time dashboards) |
| **Daily export of last billing period** | Previous month's final costs (good for permanent records) |
| **Weekly export** | Cost data updated weekly |

**Export format**: CSV files; compatible with Power BI, Excel, Databricks, Synapse, and custom analytics pipelines.

```bash
# Create a daily cost export to Storage Account
az costmanagement export create \
  --name dailyCostExport \
  --type ActualCost \
  --scope /subscriptions/{subId} \
  --storage-account-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/costexports \
  --storage-container costdata \
  --recurrence Daily \
  --recurrence-period from="2024-01-01T00:00:00Z" to="2025-12-31T00:00:00Z"
```

---

## Azure Advisor — Cost Recommendations

Azure Advisor analyzes your resource usage telemetry and generates actionable cost recommendations.

### VM Right-sizing and Shutdown

| Recommendation | Logic | Action |
|---|---|---|
| **Shut down underutilized VMs** | Max CPU ≤5% AND max network ≤2% for 7+ days (default thresholds; configurable) | Deallocate VM (preserves disk) |
| **Right-size underutilized VMs** | CPU/memory consistently below capacity; suggests smaller SKU | Resize to smaller VM size |
| **Resize or shut down VMs on extended hours** | Usage pattern analysis; suggests scheduling start/stop | Use Azure Automation runbook for start/stop schedule |

**Configure Advisor thresholds:**
- Default: CPU ≤5% and network ≤2%; configurable to 5%, 10%, 15%, or 20% CPU threshold
- Lookback period: 7, 14, 21, or 30 days (longer lookback = fewer false positives)

### Other Cost Recommendations

| Category | Recommendation | Example |
|---|---|---|
| **Reservations** | Buy Reserved Instances for consistently running VMs | "Buy 3-year RI for Standard_D4s_v5 in East US — save $X/month" |
| **Unattached disks** | Delete unattached managed disks (no VM attached) | Delete orphaned Premium SSD disks |
| **Idle resources** | Delete or downgrade idle App Service Plans, load balancers, VPN gateways | App Service Plan with 0 requests for 30 days |
| **Storage lifecycle** | Move cold blob data to Archive/Cool tier | Blobs not accessed in 30 days |
| **Cheaper alternatives** | Migrate to burstable VMs (B-series) for variable CPU | Standard_D2s → Standard_B2s for dev VMs |
| **Savings Plans** | Buy Compute Savings Plan for consistent compute spend | "Commit $X/hour for 1-year Savings Plan" |
| **Azure Hybrid Benefit** | Apply AHB to Windows VMs with existing licenses | Save ~40% on Windows compute cost |
| **Marketplace** | Optimize marketplace resource usage | Unused 3rd-party software |

### Advisor Score

- Advisor provides an **Advisor Score** (0–100) across 5 pillars: Reliability, Security, Operational Excellence, Performance, Cost
- Cost score represents % of Advisor cost recommendations you've implemented
- Use as a KPI for FinOps maturity; track improvement over time

---

## Azure Cost Management Power BI Connector

- Direct Power BI connection to Cost Management data (no export to Storage required)
- Built-in report templates: Cost Analysis, Reservation Utilization, Amortized Cost
- Refresh on schedule; share with stakeholders without Azure portal access
- **Scopes**: Billing Account (EA/MCA), Management Group, Subscription

### Key Power BI Reports

| Report | Description |
|---|---|
| **Cost Analysis** | Monthly trend, by service, by resource group, by tag |
| **Reservation Summary** | Utilization %, waste, savings vs PAYG |
| **Budget vs Actual** | Budget tracking with forecast overlay |
| **Amortized Cost by Resource** | See RI cost distributed to consuming resources for charge-back |

---

## FinOps Best Practices

| Practice | Description |
|---|---|
| **Tagging enforcement** | Deny resource creation without required tags via Azure Policy |
| **Budget per workload** | Set budget at resource group or subscription level per workload |
| **Anomaly alert recipients** | Add FinOps team and workload owners to anomaly alert distribution |
| **Monthly RI utilization review** | Target >85% utilization across all reservations |
| **Rightsizing before reserving** | Rightsize VMs using Advisor before purchasing Reserved Instances |
| **Cost export + Power BI** | Automated daily export + Power BI for exec-level dashboards |
| **Dev/Test subscription** | Use Dev/Test subscription type for non-production (pay Linux PAYG rates for Windows) |
| **Auto-shutdown for dev VMs** | Auto-shutdown non-production VMs outside business hours |
| **Lifecycle policies on Storage** | Move blobs to Cool/Archive tier based on last-access time |
