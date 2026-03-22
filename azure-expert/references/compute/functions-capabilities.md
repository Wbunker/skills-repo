# Azure Functions — Capabilities Reference

For CLI commands, see [functions-cli.md](functions-cli.md).

## Azure Functions

**Purpose**: Event-driven serverless compute that runs code in response to triggers. Supports scale-to-zero, pay-per-execution pricing, and deep integration with Azure services via bindings. Supports .NET, Node.js, Python, Java, PowerShell, and custom handlers.

---

## Hosting Plans

| Plan | Cold Start | Scale | Max Scale | Timeout | Best For |
|---|---|---|---|---|---|
| **Consumption** | Yes (~1–3s) | Per-event | 200 instances | 5 min (10 min max) | Spiky or infrequent workloads; lowest cost |
| **Flex Consumption** | Minimal | Per-event + pre-provisioned instances | 1000+ | 30 min default | New default for production; best balance of cost + performance |
| **Premium (EP1/EP2/EP3)** | No (always warm) | Per-event | 100 instances | Unlimited | Latency-sensitive, VNet integration, extended duration |
| **App Service Plan (Dedicated)** | No | Manual / auto-scale | Plan max | Unlimited | Run alongside web apps; predictable cost; WebJobs replacement |
| **Container Apps** | Minimal | KEDA-driven | KEDA target | Unlimited | Custom runtimes, sidecar patterns, DAPR integration |

### Flex Consumption (Recommended for Production)

- Pre-provisioned instances (always ready, no cold start) + burst capacity
- Per-execution billing during burst + per-instance billing for pre-provisioned
- Supports larger instance sizes (4 vCPU / 8 GB RAM) vs Consumption (1 vCPU / 1.5 GB)
- VNet integration supported natively
- Concurrency controls per instance (limit parallel executions)

---

## Triggers

Triggers define what event starts function execution. Each function has exactly one trigger.

| Trigger | Description | Common Use Case |
|---|---|---|
| **HTTP** | Invoked by HTTP/HTTPS request | REST APIs, webhooks, async API patterns |
| **Timer** | CRON schedule | Scheduled jobs, data cleanup, report generation |
| **Blob Storage** | New/updated blob in a container | File processing, image resizing, ETL |
| **Queue Storage** | New message in Azure Queue Storage | Simple task queues, decoupled processing |
| **Service Bus (Queue/Topic)** | Message from Service Bus queue or topic subscription | Enterprise async messaging, ordered processing |
| **Event Hub** | Batch of events from Event Hubs | Real-time telemetry processing, IoT data |
| **Cosmos DB** | Change feed from a Cosmos DB container | Real-time data propagation, event sourcing |
| **Event Grid** | Event from Event Grid topic or system topic | Azure resource events, custom domain events |
| **Timer (Durable)** | Internal durable timer | Long-running orchestrations |
| **Entity** | Durable entity activation | Stateful actor patterns |
| **Kafka** | Messages from Kafka topic (Premium/Dedicated) | Legacy Kafka integration |
| **SignalR** | Connection events for real-time messaging | Chat, live dashboards |
| **RabbitMQ** | Messages from RabbitMQ queue | On-premises messaging integration |
| **Dapr** | Dapr service invocation and pub/sub | Cloud-native microservice integration |

---

## Bindings

Bindings declaratively connect a function to other services without requiring SDK code. Each function can have multiple input and output bindings.

### Input Bindings (read data into function)

| Binding | Description |
|---|---|
| **Blob Storage (input)** | Read a blob based on a path or trigger metadata |
| **Cosmos DB (input)** | Read one or multiple documents from a container |
| **Table Storage (input)** | Read entities from Table Storage |
| **SignalR (input)** | Get connection info for SignalR client |
| **SendGrid (input)** | Template-based email configuration |

### Output Bindings (write data from function)

| Binding | Description |
|---|---|
| **Blob Storage (output)** | Write a blob to a container |
| **Queue Storage (output)** | Send a message to a Queue |
| **Service Bus (output)** | Send a message to a queue or topic |
| **Event Hub (output)** | Send an event to Event Hubs |
| **Cosmos DB (output)** | Upsert one or multiple documents |
| **Table Storage (output)** | Write entities |
| **HTTP Response (output)** | Return HTTP response (HTTP-triggered functions) |
| **SignalR (output)** | Send real-time messages to connected clients |
| **SendGrid (output)** | Send email |
| **Twilio (output)** | Send SMS |
| **Event Grid (output)** | Publish events to Event Grid |

---

## Durable Functions

Durable Functions extends Azure Functions with stateful workflows using an orchestrator-worker pattern. State is persisted in Azure Storage automatically.

### Core Patterns

| Pattern | Description | Use Case |
|---|---|---|
| **Function Chaining** | Call functions sequentially; output of one is input of next | Multi-step data processing pipelines |
| **Fan-Out / Fan-In** | Spawn multiple parallel activity functions; wait for all to complete | Parallel data processing, batch API calls |
| **Async HTTP API** | Start long-running job; return 202 with status URI; poll for completion | Processing large files, ML training jobs |
| **Monitoring** | Periodic polling until condition is met (e.g., external status) | Job status polling, approval workflows |
| **Human Interaction** | Wait for external event (approval, user input) with timeout and escalation | Approval workflows, multi-step forms |
| **Aggregator (Stateful)** | Accumulate events over time into a single entity | Session aggregation, real-time metrics |
| **Eternal Orchestration** | Orchestrator restarts itself in a loop | Long-running monitoring, recurring jobs |

### Durable Entity Functions

- Stateful actors; addressable by entity ID
- Can be called directly or by orchestrators
- State persists automatically in Table Storage
- Useful for: counters, shopping carts, game state, rate limiters

### Durable Function Components

| Component | Description |
|---|---|
| **Orchestrator Function** | Defines the workflow using durable APIs; must be deterministic |
| **Activity Function** | Performs the actual work; called by orchestrator |
| **Entity Function** | Stateful actor with operations |
| **Client Function** | Starts orchestrations and sends events; any trigger type |
| **Task Hub** | Isolated namespace in storage for orchestration state |

---

## Cold Start Mitigation

| Strategy | Plan | Description |
|---|---|---|
| **Pre-provisioned instances** | Flex Consumption | Reserve N always-warm instances; pay per-instance/hour |
| **Premium Plan (always on)** | Premium | Minimum 1 pre-warmed instance; no cold starts |
| **App Service Plan** | Dedicated | No cold starts; fixed compute |
| **Keep-alive pings** | Consumption | Timer trigger pings the function to keep it warm; limited effectiveness |
| **Smaller deployment package** | Any | Reduce load time; avoid large dependencies at module level |
| **.NET Isolated Worker** | Any | Faster startup than in-process .NET |
| **Python async workers** | Any | Use async/await; avoid blocking I/O at import time |

---

## Deployment

### Deployment Methods

| Method | Description |
|---|---|
| **ZIP Deploy** | Upload a ZIP via Kudu or `az functionapp deploy`; most common CI/CD approach |
| **Azure Functions Core Tools** | `func azure functionapp publish` for local development deployment |
| **GitHub Actions** | `azure/functions-action` workflow action; builds and deploys automatically |
| **Azure DevOps** | `AzureFunctionApp@2` task in Pipelines |
| **Container (Docker)** | Push a custom container to ACR; requires Premium or Dedicated plan or Container Apps |
| **Terraform / Bicep** | Deploy function app infrastructure + ZipDeploy artifact |

### Deployment Slots

- Supported on Premium and App Service Plan hosting
- Same slot swap mechanics as App Service (staging → production atomic swap)
- Slot-specific settings (e.g., staging storage account, feature flags)
- Not supported on Consumption or Flex Consumption plans

---

## Managed Identity Integration

Functions can authenticate to Azure services without credentials using managed identity:

```json
// local.settings.json — development connection strings use identity by default
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

- Service Bus trigger/binding: set `connection` to identity-based connection string prefix
- Storage trigger/binding: use `AzureWebJobsStorage__accountName` instead of connection string
- Cosmos DB binding: use `accountEndpoint` instead of connection string

---

## Networking

| Feature | Consumption | Flex | Premium | App Service |
|---|---|---|---|---|
| **Inbound Private Endpoint** | No | Yes | Yes | Yes |
| **Outbound VNet Integration** | No | Yes | Yes | Yes |
| **IP restrictions** | Yes | Yes | Yes | Yes |
| **Private site access** | Yes | Yes | Yes | Yes |

- **Flex Consumption VNet**: Built-in VNet integration; function instances run in your VNet; no separate subnet delegation complexity
- **Premium VNet Integration**: Requires dedicated subnet delegation; supports full outbound VNet access including Private Endpoints

---

## Scaling Behavior

| Plan | Scale Unit | Scale Trigger | Scale-to-Zero |
|---|---|---|---|
| **Consumption** | Individual function app | Queue depth, event rate | Yes (after idle) |
| **Flex Consumption** | Individual function app | Queue depth, event rate | Yes (burst instances); pre-provisioned always up |
| **Premium** | Plan-level (shared across apps in plan) | Event rate + minimum instances | No (minimum 1 always warm) |
| **App Service** | Plan-level | Auto-scale rules (CPU/memory/schedule) | No |

---

## Key Configuration Settings

| Setting | Description |
|---|---|
| `FUNCTIONS_WORKER_RUNTIME` | Runtime language: `dotnet-isolated`, `node`, `python`, `java`, `powershell`, `custom` |
| `AzureWebJobsStorage` | Storage account for Durable Functions, host coordination, blob/queue triggers |
| `WEBSITE_RUN_FROM_PACKAGE` | Run function from ZIP package URL or value `1` (from `d:/home/data/SitePackages/`) |
| `FUNCTIONS_EXTENSION_VERSION` | Host version: `~4` (current); `~3` (legacy) |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights telemetry (preferred over instrumentation key) |
| `WEBSITE_MAX_DYNAMIC_APPLICATION_SCALE_OUT` | Cap max instances (Consumption plan) |
| `AzureFunctionsJobHost__extensions__serviceBus__prefetchCount` | Service Bus prefetch tuning |
