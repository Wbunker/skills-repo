# Azure Functions — Capabilities Reference
For CLI commands, see [functions-cli.md](functions-cli.md).

## Azure Functions

**Purpose**: Event-driven serverless compute that runs code on-demand without provisioning or managing infrastructure. Scales automatically; billing is based on execution count, duration, and memory consumed (depending on hosting plan).

---

## Hosting Plans

| Plan | Scale | Cold Start | VNet Integration | Max Execution | Billing |
|---|---|---|---|---|---|
| **Consumption** | Scale to zero, automatic | Yes (can be seconds) | Limited (requires Premium for full VNet) | 5 min default, 10 min max | Per-execution (GB-s + invocations) |
| **Flex Consumption** | Scale to zero, per-instance concurrency | Reduced vs Consumption | Private networking supported | 60 min max | Pay-per-use, per-instance |
| **Premium (Elastic Premium)** | Always-ready instances + elastic scale | No cold start | Full VNet integration | 60 min max (unlimited with `functionTimeout -1`) | Per-instance (pre-warmed + elastic) |
| **App Service Plan** | Fixed (or App Service autoscale) | No (always on) | Full VNet (inherits from ASP) | Unlimited | Shared with App Service Plan |
| **Container Apps** | KEDA-based event-driven | Configurable | Full VNet, Dapr | Configurable | Container Apps consumption/dedicated |

### Consumption Plan Details
- Default timeout: 5 minutes; configurable up to 10 minutes via `functionTimeout` in `host.json`
- Scale controller monitors event source metrics and adds/removes instances dynamically
- Maximum scale: 200 instances per function app (default); configurable lower with `WEBSITE_MAX_DYNAMIC_APPLICATION_SCALE_OUT`
- VNet integration limited: requires regional VNet integration add-on (not available in base Consumption)
- Cold starts: initialization of new execution environment adds latency (typically 1–10+ seconds depending on runtime and package size)

### Flex Consumption Plan (New Default)
- Introduced as the next-generation serverless plan replacing standard Consumption for new workloads
- Per-instance concurrency: configure how many concurrent executions run per instance (reduces cold starts from parallelism)
- Private networking: supports VNet integration out of the box — inbound private endpoint, outbound VNet routing
- Faster cold starts vs standard Consumption due to improved instance initialization
- Maximum execution: 60 minutes
- Scale to zero: yes, with configurable always-ready instance count for key functions
- Billing: pay-per-use, metered per active instance second

### Premium (Elastic Premium) Plan Details
- Instance sizes: **EP1** (1 vCPU, 3.5 GB RAM), **EP2** (2 vCPU, 7 GB RAM), **EP3** (4 vCPU, 14 GB RAM)
- Always-ready instances: perpetually warm instances that eliminate cold starts; additional instances added elastically
- Pre-warmed instances: additional standby instances added before demand spikes (configurable)
- Full VNet integration: regional VNet integration for outbound; inbound private endpoint available
- Larger instance sizes support memory-intensive workloads
- Perpetual run support: set `functionTimeout` to `-1` for unlimited duration (long-running orchestrations)
- Supports VNET_ROUTE_ALL_ENABLED to route all outbound traffic through VNet

### App Service Plan
- Run Functions on an existing App Service Plan (shared or dedicated)
- No automatic scaling unless App Service autoscale rules are configured
- Best for: always-on requirements, predictable and stable workloads, co-hosting with web apps
- AlwaysOn setting must be enabled to prevent idle timeout recycling
- Supports any App Service Plan tier (Free through Isolated)

### Container Apps Hosting
- Deploy function app as a container into an Azure Container Apps environment
- Full Kubernetes-based infrastructure: VNet injection, Dapr sidecar, KEDA event-driven scaling
- Workload profiles (consumption or dedicated) for resource allocation
- Enables Functions alongside other Container Apps microservices in the same environment

---

## Triggers

| Trigger | Description | Key Configuration |
|---|---|---|
| **HTTP** | Invokes function via HTTP request; default entry point for APIs | Auth level: anonymous, function, admin |
| **Timer** | Runs on CRON schedule | CRON expression (6-field: seconds optional) |
| **Blob Storage** | Fires on blob create/modify in container | Container path with `{name}` blobPathPattern |
| **Queue Storage** | Fires on message arrival in Azure Storage queue | Queue name, poison queue auto-created |
| **Service Bus** | Fires on Service Bus queue or topic subscription message | Queue/topic name, connection string or managed identity |
| **Event Hubs** | Fires on Event Hubs event batch | Consumer group, event hub name, cardinality (one/many) |
| **Cosmos DB** | Change feed trigger; fires on document inserts/updates | Container, lease container |
| **Event Grid** | Fires on Event Grid event delivery | System or custom topic subscription |
| **SignalR** | Negotiate and message triggers for real-time apps | Hub name |
| **Kafka** | Fires on Kafka topic messages | Broker, topic, consumer group |
| **SQL** | Fires on SQL table changes (change tracking) | Table name, connection string |
| **Durable orchestrator** | Entry point for Durable Functions orchestration | Orchestrator function name |
| **Durable activity** | Activity function called by orchestrator | Called via `context.df.callActivity` |
| **Durable entity** | Actor-model entity trigger | Entity name, entity key |

---

## Bindings

Bindings eliminate boilerplate code for connecting to Azure services. Declared in `function.json` (in-process) or via attributes/annotations (isolated worker / Java).

| Direction | Purpose | Examples |
|---|---|---|
| **Input** | Read data into the function at invocation time | Blob input, Cosmos DB document lookup, Table Storage, SQL query |
| **Output** | Write data from the function to a destination | Blob output, Queue Storage message, Service Bus message, Cosmos DB upsert, Event Hubs publish, SignalR message |

- Multiple output bindings supported (e.g., write to queue AND Cosmos DB in same function)
- Managed Identity authentication preferred over connection strings: set `credential: "managedidentity"` in binding config; assign appropriate role on target service

---

## Durable Functions

Durable Functions is an extension for building stateful, long-running workflows on top of Azure Functions using an orchestrator/activity model backed by a durable task framework.

### Orchestration Patterns

| Pattern | Description | Use Case |
|---|---|---|
| **Function Chaining** | Call activities sequentially; output of one feeds next | Sequential data pipeline |
| **Fan-out/Fan-in** | Dispatch multiple parallel activities; wait for all (or any) | Parallel processing with aggregation |
| **Async HTTP API** | Start long-running operation; client polls status endpoint | Long jobs with progress tracking |
| **Monitor** | Flexible recurring check that adapts timing | Status polling, condition wait |
| **Human Interaction** | Pause orchestration waiting for external event (approval) | Approval workflows, human-in-the-loop |
| **Aggregator (Entities)** | Accumulate state over time from multiple events | Stateful counters, session aggregation |

### Orchestrator Functions
- Must be **deterministic**: same inputs always produce same outputs across replay
- Avoid: `DateTime.Now` (use `context.df.currentUtcDateTime`), random numbers, I/O calls outside activities
- Replay mechanism: orchestrator replays from event history on each wake-up — history stored in task hub storage
- Key APIs:
  - `context.df.callActivity(name, input)` — call an activity function
  - `context.df.Task.all([...tasks])` — fan-in, wait for all tasks (parallel)
  - `context.df.Task.any([...tasks])` — wait for first completed task
  - `context.df.waitForExternalEvent(name)` — pause until external event arrives
  - `context.df.createTimer(deadline)` — durable timer (survives restarts)
  - `context.df.continueAsNew(input)` — restart orchestration (prevent history bloat for eternal workflows)

### Entity Functions (Actors)
- Stateful objects with explicit identity (entity name + key)
- Persist state across calls; support sequential signal/call semantics
- `context.df.callEntity(entityId, operationName, operationInput)` — call from orchestrator
- `context.df.signalEntity(entityId, operationName, operationInput)` — one-way fire-and-forget signal
- Use cases: distributed counters, shopping carts, device state, session aggregation

### Durable Storage Backends

| Backend | Description | Best For |
|---|---|---|
| **Azure Storage** (default) | Queues, tables, blobs in Azure Storage account | General use, simple setup |
| **Netherite** | Event Hubs + Cosmos DB; high-throughput, low-latency | High-scale, throughput-intensive orchestrations |
| **MSSQL** | SQL Server / Azure SQL Database storage | Existing SQL infrastructure, rich query on history |

---

## Language Support

| Language | Worker Model | Notes |
|---|---|---|
| C# | In-process (.NET 6) or Isolated worker (.NET 8+) | Isolated worker recommended for .NET 8+ (separate process, better isolation) |
| Python | Isolated worker (v2 programming model recommended) | v2 model uses decorators, single `function_app.py` file |
| JavaScript / TypeScript | Isolated worker (Node.js v4 model recommended) | v4 model uses exported functions, no `function.json` |
| Java | Isolated worker | Annotations-based (`@FunctionName`, `@HttpTrigger`) |
| PowerShell | Isolated worker | `profile.ps1` for initialization; supports Az module |
| Go | Custom handler | HTTP-based custom handler process |
| Rust | Custom handler | HTTP-based custom handler process |

---

## Deployment Methods

| Method | Description |
|---|---|
| **ZIP deploy** | Upload ZIP via `az functionapp deployment source config-zip` or REST API; fastest for CI/CD |
| **func CLI** | `func azure functionapp publish` from local project; handles ZIP creation and upload |
| **VS Code** | Azure Functions extension; one-click deploy with auto-publish |
| **GitHub Actions** | `Azure/functions-action` marketplace action; integrates with OIDC/service principal auth |
| **Azure DevOps** | Azure Functions deploy task; supports slot deployment |
| **Container image** | Build image with Azure Functions base image; deploy to Premium or Container Apps hosting |
| **Deployment slots** | Staging slots for zero-downtime deployment; swap slots with `az functionapp deployment slot swap` |

---

## Cold Start Mitigation Strategies

- **Premium Plan**: always-ready instances eliminate cold starts entirely; pre-warmed instances absorb sudden scale
- **Flex Consumption**: reduced cold start latency vs standard Consumption; configurable always-ready instance count per function
- **Reduce package size**: smaller deployment packages load faster; use `WEBSITE_RUN_FROM_PACKAGE=1` for read-only mounting
- **Isolated worker model**: .NET isolated worker starts faster than in-process for cold invocations
- **FUNCTIONS_WORKER_PROCESS_COUNT**: increase worker process count (for in-process C# or Python) to handle concurrency without new cold starts

---

## Managed Identity & Security

- **Managed Identity**: preferred authentication method for all binding connections
  - System-assigned: created with function app, tied to its lifecycle
  - User-assigned: shared identity, survives function app deletion
  - Configure in binding: `"credential": "managedidentity"` in `host.json` connection config
  - Assign RBAC role on target resource (e.g., `Storage Blob Data Contributor`, `Azure Service Bus Data Receiver`)
- **Function keys**: host keys (all functions), function keys (per function), master key (admin)
  - Retrieve via `az functionapp keys list` or `az functionapp function keys list`
- **Application Settings**: encrypted at rest; use Key Vault references `@Microsoft.KeyVault(SecretUri=...)` for secrets
- **Network security**: IP restrictions, private endpoints (inbound), VNet integration (outbound), service endpoints

---

## Monitoring & Diagnostics

- **Application Insights**: integrated by default; tracks invocations, exceptions, dependencies, custom telemetry
  - `APPLICATIONINSIGHTS_CONNECTION_STRING` app setting links function app to Application Insights resource
  - Live Metrics Stream: real-time view of invocations, failures, server load
- **Log streaming**: `func azure functionapp logstream` or `az webapp log tail` for real-time log output
- **Diagnostic Settings**: route function app logs and metrics to Log Analytics, Storage, or Event Hubs
- **Azure Monitor Alerts**: alert on `FunctionExecutionCount`, `FunctionExecutionUnits`, error rates

---

## Key Configuration Files

| File | Purpose |
|---|---|
| `host.json` | Global function app config: logging, extension versions, concurrency, retry policies |
| `local.settings.json` | Local development settings (NOT deployed); contains connection strings for local emulators |
| `function.json` | Per-function trigger/binding config (in-process model; v2/v4 models use code attributes instead) |
| `requirements.txt` / `pom.xml` / `package.json` | Language-specific dependency manifests |
