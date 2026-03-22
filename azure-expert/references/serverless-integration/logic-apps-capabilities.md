# Azure Logic Apps — Capabilities Reference
For CLI commands, see [logic-apps-cli.md](logic-apps-cli.md).

## Azure Logic Apps

**Purpose**: Cloud-based integration platform (iPaaS) for building automated workflows that connect apps, data, services, and systems. Provides a visual designer alongside code-based authoring, with 400+ managed connectors for SaaS, on-premises, and Azure services.

---

## Hosting Models

| Feature | Consumption (Multi-tenant) | Standard (Single-tenant) |
|---|---|---|
| **Tenancy** | Shared Azure infrastructure | Dedicated single-tenant runtime |
| **Pricing** | Per action execution | Per vCPU/memory (App Service / Container Apps) |
| **Workflows per resource** | One workflow per Logic App resource | Multiple workflows per Logic App resource |
| **Stateful/Stateless** | Stateful only | Both stateful and stateless workflows |
| **VNet Integration** | Not supported | Full VNet integration (outbound + inbound private endpoint) |
| **Local development** | Limited (portal-only designer) | Full VS Code + Azure Functions Core Tools |
| **Connectors included** | Managed connectors billed per use | Many premium connectors included in runtime |
| **Deployment** | ARM template / portal | VS Code, ARM, Bicep, GitHub Actions (workflow.json) |
| **Monitoring** | Run history, Azure Monitor | Run history, Application Insights, Azure Monitor |
| **Use case** | Rapid prototyping, lightweight integrations | Enterprise workloads, VNet-required, CI/CD pipelines |

---

## Connector Types

| Type | Description | Examples |
|---|---|---|
| **Built-in** | Run in-process with the Logic Apps runtime; low latency, no outbound connector call | HTTP, Request/Response, Schedule, Variables, Control, Inline Code, Azure Functions (call), Batch |
| **Managed (Azure-hosted)** | Call via Azure connector infrastructure; Microsoft manages, hosted in shared multi-tenant connectors service | Office 365 Outlook, SharePoint, Salesforce, SQL Server (managed), Dynamics 365 |
| **Custom** | User-created connectors backed by any REST or SOAP API with OpenAPI spec | Internal APIs, partner systems, private services |
| **On-premises** | Requires on-premises data gateway (OPDG) for secure connectivity to on-premises data sources | SQL Server, Oracle, File System, BizTalk |

---

## Key Connectors

### Microsoft & Azure Services
| Connector | Common Actions/Triggers |
|---|---|
| **Office 365 Outlook** | Send email, create event, flag message, get attachments |
| **SharePoint** | Create/get/update list items, create file, get file content |
| **Teams** | Post message, create channel, get channel messages |
| **OneDrive / OneDrive for Business** | Create file, get file content, list files |
| **Azure Blob Storage** | Create blob, get blob content, list blobs, delete blob |
| **Azure Service Bus** | Send message, receive message, complete/abandon/dead-letter |
| **Azure Event Grid** | Publish event, subscribe to events |
| **Azure Cosmos DB** | Create/read/upsert/delete document, query documents |
| **Azure Functions** | Call an Azure Function (built-in connector) |
| **Azure Key Vault** | Get secret, set secret |

### Enterprise & SaaS
| Connector | Common Actions/Triggers |
|---|---|
| **Salesforce** | Create/update/query records, subscribe to object changes |
| **SAP** | Send IDoc, BAPI/RFC calls (requires on-premises data gateway or ISE) |
| **ServiceNow** | Create/update incident/record, query records |
| **Dynamics 365** | Create/update/query records, trigger on record change |
| **Oracle Database** | Execute query, insert/update/delete rows |
| **SQL Server** | Execute query/stored procedure, insert/update/delete rows |
| **FTP / SFTP-SSH** | Get/create file, list folder contents |
| **Twilio** | Send SMS, get messages |
| **DocuSign** | Send envelope, get signing status |

---

## Workflow Concepts

### Triggers
A trigger is the event that starts a workflow. Only one trigger per workflow.

| Trigger Type | Examples |
|---|---|
| **Recurrence** | Run on a schedule (every N minutes/hours/days); built-in, no external dependency |
| **HTTP Request** | Expose an HTTP endpoint; other services POST to it to start the workflow |
| **Event-based** | Azure Service Bus, Event Grid, Blob Storage, SQL changes, Salesforce object change |
| **Polling** | Logic Apps polls the source on a schedule; connector determines if new items exist |

### Actions
Actions perform operations after the trigger fires. Workflows execute actions sequentially by default.

| Action Category | Examples |
|---|---|
| **Control flow** | Condition (if/else), Switch (case), For Each (loop), Until (loop), Scope (group), Terminate |
| **Variables** | Initialize Variable, Set Variable, Increment Variable, Append to String/Array Variable |
| **Data operations** | Compose, Parse JSON, Select (project), Filter Array, Join, Create CSV/HTML Table |
| **HTTP** | HTTP action (call any REST endpoint), HTTP + Swagger (with OpenAPI spec) |
| **Connector actions** | Send email, create file, query database, etc. |

### Conditions
- Boolean expression evaluating dynamic content from previous steps
- If/else branching: two branches execute different action sets
- Switch statement: multiple case branches based on a single expression value

### Loops
- **For Each**: iterate over an array; configurable concurrency (parallel iterations)
- **Until**: repeat actions until condition is true; configurable count and timeout limits

### Parallel Branches
- Add parallel branches in the designer; actions in different branches execute simultaneously
- Join conditions: all branches complete before proceeding (implicit join)

### Scopes (Try-Catch-Finally Pattern)
- Scope action groups child actions; scope status reflects combined child status
- Configure "Run After" settings on subsequent actions to handle scope success, failure, skipped, or timeout
- Pattern: Scope (try) → Catch scope with `runAfter: Failed` → Finally actions with `runAfter: Succeeded, Failed, Skipped`

### Variables
- Declared at workflow level with `Initialize Variable`; scoped to the entire workflow run
- Types: String, Integer, Float, Boolean, Array, Object
- Actions: Set, Increment, Decrement, Append

---

## Enterprise Integration Pack (EIP)

For B2B and EDI workflows requiring trading partner management and message processing standards.

### Components
| Component | Description |
|---|---|
| **Integration Account** | Azure resource that stores B2B artifacts: partners, agreements, schemas, maps, certificates |
| **Trading Partners** | Organizations that exchange B2B messages; defined with business identities (AS2, X12, EDIFACT qualifiers) |
| **Agreements** | Rules for message exchange between two partners; defines encoding, decoding, acknowledgement settings |
| **Schemas** | XML schemas (XSD) for validating message structure |
| **Maps** | XSLT or Liquid transforms for message transformation (XML→XML, JSON→JSON, XML→JSON) |
| **Certificates** | Public/private certificates for message signing and encryption |

### Supported Standards
- **AS2**: HTTP-based secure messaging with MDN acknowledgement, signing, encryption
- **X12**: EDI standard (North America); support for 270/271 (eligibility), 810 (invoice), 850 (purchase order), 856 (ASN), etc.
- **EDIFACT**: EDI standard (international); decode/encode interchanges, functional acknowledgements
- **Liquid Templates**: JSON/XML transformation using Liquid template language (DotLiquid)
- **XML Validation**: validate XML messages against XSD schemas

### Integration Account Tiers
| Tier | Use | Artifact Limits |
|---|---|---|
| **Free** | Development and testing | Very limited |
| **Basic** | Simple message processing, partner mgmt | 250 agreements, limited throughput |
| **Standard** | Full B2B, high throughput | Unlimited agreements, higher throughput |

---

## ISE (Integration Service Environment) — Deprecated
- Dedicated, VNet-injected Logic Apps runtime (private IP, no shared infrastructure)
- Microsoft has **deprecated ISE**; existing ISEs supported until November 2024
- Migration path: Logic Apps Standard with VNet integration provides equivalent capabilities

---

## Monitoring and Diagnostics

| Feature | Description |
|---|---|
| **Run history** | Every workflow run is recorded with trigger, action inputs/outputs, duration, status |
| **Resubmit failed runs** | Re-trigger a failed run with the same trigger payload (Consumption); useful for transient failures |
| **Live view** | Real-time monitoring of in-progress runs in the portal designer |
| **Azure Monitor Logs** | Route diagnostics to Log Analytics workspace; query with KQL |
| **Application Insights** | Standard workflows on App Service infrastructure support App Insights integration |
| **Diagnostic Settings** | Export metrics and logs to Storage, Event Hubs, or Log Analytics |

### Key Log Analytics Queries
```kusto
-- Failed Logic App runs in last 24 hours
AzureDiagnostics
| where ResourceType == "WORKFLOWS/RUNS" and status_s == "Failed"
| where TimeGenerated > ago(24h)
| project TimeGenerated, resource_workflowName_s, error_message_s
| order by TimeGenerated desc

-- Action failures by workflow
AzureDiagnostics
| where ResourceType == "WORKFLOWS/RUNS/ACTIONS" and status_s == "Failed"
| summarize FailureCount = count() by resource_workflowName_s, resource_actionName_s
| order by FailureCount desc
```

---

## CI/CD and Infrastructure as Code

### Consumption (ARM Template)
- Export Logic App as ARM template from portal
- Parameters for connection strings, URLs, resource names
- Deploy with `az deployment group create`

### Standard (Code-based)
- Each workflow stored as `workflow.json` in VS Code project structure
- Full Git version control of workflow definitions
- Deploy as ZIP package or container image
- `connections.json` defines managed connector references
- Environment-specific parameters via `parameters.json`
- GitHub Actions: `Azure/logicapps-action` or generic ZIP deploy action
- Azure DevOps: use `AzureFunctionApp` task with Logic Apps Standard runtime type

### Project Structure (Standard)
```
myLogicApp/
├── host.json                  # Runtime configuration
├── connections.json           # Managed API connections
├── parameters.json            # Environment parameters
├── workflow1/
│   └── workflow.json          # Workflow definition
└── workflow2/
    └── workflow.json
```
