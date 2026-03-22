# Azure Monitor — Capabilities

## Service Overview

Azure Monitor is the unified observability platform for Azure — collecting, analyzing, and acting on telemetry from cloud and on-premises environments. It provides metrics, logs, distributed traces, alerting, and visualization across all Azure services and custom applications.

---

## Azure Monitor Data Platform

```
Data Sources              Data Platform              Analyze & Act
────────────────         ─────────────             ───────────────
Azure Resources    ────► Metrics (time-series)     ► Metrics Explorer
Applications       ────► Logs (Log Analytics)      ► Log Analytics
VMs/Containers     ────► Traces (Application       ► Application Insights
Network            ────►   Insights)               ► Dashboards
Custom sources     ────► Change data               ► Workbooks
                                                   ► Alerts
                                                   ► Autoscale
```

---

## Metrics

Time-series numerical data collected from Azure resources:

### Characteristics

| Property | Value |
|---|---|
| **Retention** | 93 days at native resolution |
| **Granularity** | 1-minute intervals (some services: 5 seconds) |
| **Latency** | Near real-time (typically < 3 minutes) |
| **Cost** | Free for standard platform metrics |

### Platform Metrics vs. Custom Metrics

| Type | Description |
|---|---|
| **Platform metrics** | Auto-collected from Azure resources (CPU, memory, requests, etc.) — free |
| **Custom metrics** | Application-emitted metrics via App Insights SDK or REST API — billed per metric series |

### Metric Aggregations

- **Average**: Mean value over interval.
- **Sum**: Total over interval.
- **Count**: Number of data points.
- **Min/Max**: Extremes over interval.
- **P50/P90/P95/P99**: Percentiles (for latency, duration metrics).

### Metrics Explorer

Interactive metric visualization in Azure portal:
- Add multiple metrics per chart.
- Apply filters by dimension (resource ID, region, API endpoint, HTTP status, etc.).
- Time range: 1 hour to 30 days.
- Split by dimension for per-resource breakdown.

---

## Logs (Log Analytics)

Structured log storage with KQL querying — the primary diagnostic and analytics layer.

### Log Analytics Workspace

- Central repository for logs from multiple sources.
- **Retention**: 30 days default (configurable 30–730 days interactive + 7 years archive).
- **Cost model**: Ingestion volume (GB/day) + interactive retention beyond 30 days.
- **Commitment tiers**: Discount for committed ingestion (100 GB/day+).

### Log Tables

| Category | Examples |
|---|---|
| Azure Diagnostics | AzureActivity, AzureDiagnostics, AzureMetrics |
| Resource-specific | StorageBlobLogs, AzureFirewallApplicationRule, KeyVaultAuditLogs |
| App Insights | AppRequests, AppExceptions, AppDependencies, AppTraces |
| Azure AD / Entra | SigninLogs, AuditLogs |
| Security | SecurityAlert, SecurityEvent, SecurityIncident |
| Containers | ContainerLog, ContainerInsights, KubePodInventory |

### Table Plans

| Plan | Interactive Retention | Query Cost | Best For |
|---|---|---|---|
| **Analytics** | Up to 730 days | Standard | Frequently queried operational logs |
| **Basic** | 8 days interactive | Cheaper | High-volume noisy logs (debug, verbose) |
| **Auxiliary (preview)** | 30 days | Cheapest | Compliance archiving, bulk ingest |

### Archive Tier

- After interactive retention expires, data moves to archive (up to 7 years total).
- Queries against archived data via Search Jobs (asynchronous).
- Cost: ~$0.002/GB/month.

---

## KQL Essentials

```kusto
// Basics
TableName
| where TimeGenerated > ago(1h)                      // time filter (always first)
| where ResourceGroup == "myRG"                      // string equality
| where StatusCode >= 400                            // numeric comparison
| where Message contains "timeout"                   // substring match
| where Message !contains "health"                   // negation
| where Category in ("Error", "Critical")            // multi-value filter

// Projection and transformation
| project TimeGenerated, ResourceId, StatusCode, DurationMs
| project-away _ResourceId, TenantId               // exclude columns
| extend DurationSec = DurationMs / 1000.0          // computed column
| extend Success = StatusCode < 400                 // boolean expression
| parse Message with "User=" User " Action=" Action // extract from string

// Aggregation
| summarize Count=count(), AvgDuration=avg(DurationMs), P95=percentile(DurationMs, 95)
    by ResourceId, bin(TimeGenerated, 5m)
| summarize ErrorCount=countif(StatusCode >= 500)
    by ResourceGroup

// Sorting and limiting
| order by Count desc
| top 10 by ErrorCount

// Joins
TableA
| join kind=leftouter (TableB | project Id, Name) on $left.ResourceId == $right.Id

// Rendering
| render timechart          // time series chart
| render barchart           // bar chart
| render piechart           // pie chart
| render table              // table view

// Useful functions
| extend ParsedUrl = parse_url(Url)
| extend Region = split(ResourceId, "/")[4]         // extract from path
| extend Hour = hourofday(TimeGenerated)
| where TimeGenerated between (datetime(2024-01-01) .. datetime(2024-02-01))
| mvexpand Tags                                     // expand array column
```

---

## Activity Log

Subscription-level audit trail of all resource operations:

- **What**: Every create, update, delete, action on Azure resources.
- **Who**: Caller identity (user, service principal, managed identity).
- **When**: Timestamp of the operation.
- **Retention**: 90 days (built-in); extend by routing to Log Analytics/Storage.
- **Tables in Log Analytics**: `AzureActivity`

```kusto
// Find who deleted a resource group
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue =~ "Microsoft.Resources/resourceGroups/delete"
| where ActivityStatusValue == "Succeeded"
| project TimeGenerated, Caller, ResourceGroup, OperationNameValue
```

---

## Application Insights

APM (Application Performance Monitoring) for web applications and services.

### Key Features

| Feature | Description |
|---|---|
| **Request tracking** | HTTP request rate, duration, failure rate |
| **Dependency tracking** | SQL, HTTP, Redis, Service Bus calls — latency and failures |
| **Exception tracking** | Unhandled exceptions with stack traces |
| **Custom events** | Track business events (UserPurchased, ItemViewed) |
| **Custom metrics** | Custom numeric measurements |
| **Live Metrics Stream** | Real-time metrics with < 1 second latency |
| **Distributed tracing** | End-to-end request traces across microservices |
| **Availability tests** | URL ping tests and multi-step synthetic tests |
| **Sampling** | Adaptive or fixed-rate sampling to reduce volume |
| **User flows** | Visualize user navigation through your app |
| **Funnels** | Conversion rate analysis |
| **Cohorts** | Group users by behavior for retention analysis |

### Workspace-based vs. Classic

| Type | Description |
|---|---|
| **Workspace-based** | Data stored in Log Analytics workspace — current standard |
| **Classic** | Legacy — data in dedicated App Insights store; being retired |

Always use workspace-based for new deployments.

### SDK Integration

```python
# Python (FastAPI/Flask)
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor(
    connection_string="InstrumentationKey=xxx;IngestionEndpoint=https://eastus.in.applicationinsights.azure.com/"
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process-order") as span:
    span.set_attribute("order.id", order_id)
    span.set_attribute("order.value", order_value)
    # ... processing logic
```

```javascript
// JavaScript/Node.js
const { useAzureMonitor } = require("@azure/monitor-opentelemetry");
useAzureMonitor({ azureMonitorExporterOptions: { connectionString: "..." } });
```

### Availability Tests

| Type | Description |
|---|---|
| **URL ping test** | Simple HTTP GET to URL — check status code and response content |
| **Standard test** | More control — custom headers, POST body, TLS check, follow redirects |
| **Multi-step web test** | Multi-page user journey (requires Visual Studio Enterprise) |
| **Custom TrackAvailability** | SDK-based from custom locations or private networks |

---

## Data Collection

### Azure Monitor Agent (AMA)

Replacement for legacy MMA (Microsoft Monitoring Agent) and OMS agent:

- Single agent for Windows and Linux VMs.
- Configured via **Data Collection Rules (DCR)** — what to collect and where to send.
- Supports: Windows Event Logs, Syslog, Performance Counters, custom log files.
- Managed via Azure Arc for on-premises servers.

### Data Collection Rules (DCR)

```json
{
  "dataSources": {
    "performanceCounters": [{
      "streams": ["Microsoft-Perf"],
      "scheduledTransferPeriod": "PT1M",
      "samplingFrequencyInSeconds": 60,
      "counterSpecifiers": [
        "\\Processor Information(_Total)\\% Processor Time",
        "\\Memory\\Available Bytes"
      ]
    }],
    "windowsEventLogs": [{
      "streams": ["Microsoft-Event"],
      "xPathQueries": ["System!*[System[EventID=1000]]", "Application!*[System[(Level=2)]]"]
    }]
  },
  "destinations": {
    "logAnalytics": [{"workspaceResourceId": "<workspace-id>", "name": "myWorkspace"}]
  },
  "dataFlows": [{"streams": ["Microsoft-Perf", "Microsoft-Event"], "destinations": ["myWorkspace"]}]
}
```

### Diagnostic Settings

Route resource-specific logs and metrics to Log Analytics, Storage, or Event Hubs:

```bash
az monitor diagnostic-settings create \
  --name myDiagSettings \
  --resource <resource-id> \
  --workspace <log-analytics-workspace-id> \
  --logs '[{"category": "StorageRead", "enabled": true}, {"category": "StorageWrite", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```

---

## Alerts

### Metric Alerts

Trigger when a metric crosses a threshold:

- **Static threshold**: Alert when CPU > 90% for 5 minutes.
- **Dynamic threshold** (ML-based): Alert when metric deviates from learned baseline — adapts to diurnal patterns. Reduces false positives for cyclical workloads.
- **Evaluation frequency**: How often the condition is checked (1–60 minutes).
- **Aggregation period**: Window over which metric is aggregated.

### Log Alerts (KQL-based)

- Run a KQL query on a schedule; alert if results meet condition.
- **Count**: Alert if query returns > N rows.
- **Metric measurement**: Alert when aggregated value exceeds threshold per dimension.
- **Resolve**: Log alerts auto-resolve when condition is no longer met (configurable).

```kusto
// Log alert query: failed requests > 10 in 5 minutes
AppRequests
| where TimeGenerated > ago(5m)
| where Success == false
| summarize FailCount=count() by cloud_RoleName
| where FailCount > 10
```

### Activity Log Alerts

Alert on Azure resource operations:
- Service health events (outages, maintenance, advisories).
- Specific resource operations (VM deleted, Key Vault access policy changed).
- Policy compliance changes.

### Action Groups

Reusable notification and action configurations:

| Action Type | Description |
|---|---|
| Email/SMS/Push/Voice | Notify team members |
| Azure Function | Custom processing logic |
| Logic App | Complex workflow |
| Webhook | POST to any HTTP endpoint |
| Event Hubs | Publish to event stream |
| ITSM | Create ticket in ServiceNow/Jira |
| Automation Runbook | Execute Azure Automation |
| Secure Webhook | Authenticated webhook |

---

## Autoscale

Scale VM Scale Sets and App Service Plans based on metrics or schedules:

```json
{
  "profiles": [{
    "name": "Default",
    "capacity": {"minimum": "2", "maximum": "10", "default": "2"},
    "rules": [
      {
        "metricTrigger": {
          "metricName": "Percentage CPU",
          "operator": "GreaterThan",
          "threshold": 75,
          "timeWindow": "PT5M",
          "statistic": "Average"
        },
        "scaleAction": {"direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT5M"}
      },
      {
        "metricTrigger": {
          "metricName": "Percentage CPU",
          "operator": "LessThan",
          "threshold": 25,
          "timeWindow": "PT10M",
          "statistic": "Average"
        },
        "scaleAction": {"direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT10M"}
      }
    ]
  }]
}
```

---

## Workbooks

Interactive reports combining queries, metrics, text, and parameters:

- Pre-built workbooks: VM Insights, Container Insights, Key Vault, SQL Insights, Azure Firewall.
- Custom workbooks: Combine multiple Log Analytics queries, metrics charts, markdown text.
- **Parameters**: Interactive filters that drive query results.
- **Steps**: Tables, charts, tiles, text, links, ARM template deployment.
- Share as Azure resource — access controlled by RBAC.

---

## Container Insights

AKS and Arc-enabled Kubernetes monitoring:

- **Node metrics**: CPU/memory utilization per node.
- **Pod metrics**: CPU/memory utilization per pod and container.
- **Log collection**: Container stdout/stderr via Azure Monitor Agent.
- **Live Data stream**: Real-time logs and events from kubectl.
- **Recommended alerts**: Node CPU > 95%, Node memory > 85%, OOM kills, Pod restart count.

```kusto
// Container Insights: Top pods by CPU
KubePodInventory
| where TimeGenerated > ago(1h)
| join kind=inner (
    Perf
    | where ObjectName == "K8SContainer"
    | where CounterName == "cpuUsageNanoCores"
    | summarize AvgCPU=avg(CounterValue) by InstanceName, bin(TimeGenerated, 1m)
) on InstanceName
| project TimeGenerated, PodName=Name, Namespace, AvgCPU
| order by AvgCPU desc
```

---

## VM Insights

Comprehensive VM monitoring:

- **Performance**: CPU, memory, disk I/O, network I/O — per disk and NIC.
- **Map**: Dependency mapping — visualize which processes/services a VM connects to.
- Pre-built charts and workbooks.
- Requires Azure Monitor Agent and Dependency Agent (for Map).
