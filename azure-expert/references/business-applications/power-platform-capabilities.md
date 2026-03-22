# Power Platform — Capabilities Reference
For CLI commands, see [power-platform-cli.md](power-platform-cli.md).

## Power Platform Overview

**Purpose**: Microsoft's low-code/no-code suite for building business applications, automating processes, analyzing data, and creating AI-powered chatbots — all tightly integrated with Microsoft 365 and Azure services.

### Components

| Component | Purpose |
|---|---|
| **Power Apps** | Build custom apps: canvas apps (custom UX) or model-driven apps (Dataverse-driven) |
| **Power Automate** | Automate workflows (cloud flows) and repetitive UI tasks (RPA desktop flows) |
| **Power BI** | Self-service analytics and business intelligence; reports and dashboards |
| **Copilot Studio** | Build AI-powered chatbots and copilots (formerly Power Virtual Agents) |
| **Power Pages** | Low-code external-facing web portals backed by Dataverse |
| **Dataverse** | Enterprise data platform underlying all Power Platform apps and Dynamics 365 |

---

## Power Apps

### Canvas Apps

- **Design**: Drag-and-drop design on a blank canvas; pixel-perfect layouts for mobile or web
- **Data sources**: 900+ connectors (SharePoint, Dataverse, SQL, Salesforce, Azure Blob, REST APIs, Excel)
- **Formulas**: Excel-like formula language (Power Fx) for logic, navigation, and data manipulation
- **Collections**: In-memory data tables for offline-capable apps
- **Delegation**: Some operations executed server-side (SharePoint, Dataverse, SQL) vs client-side (Excel)
- **Responsive layouts**: Adaptive containers for different screen sizes
- **Offline capability**: `LoadData`/`SaveData` functions for offline scenarios; sync on reconnect

### Model-Driven Apps

- Built on top of Dataverse tables (entities)
- Auto-generates forms, views, dashboards from Dataverse metadata
- Includes: main forms, quick create forms, views (grid + chart), dashboards, business process flows
- Navigation driven by data relationships; no canvas design required
- Suitable for: CRM-like apps, complex business processes, data management tools
- Customizable via no-code UI or Power Platform solution components

### Power Pages (formerly Power Apps Portals)

- External-facing web portals accessible by anonymous or authenticated users
- Authentication: Azure AD B2C / Entra External ID, Azure AD, LinkedIn, Google, local accounts
- Content: pages, forms, lists backed by Dataverse
- Liquid templates for dynamic content rendering
- CDN-backed for performance; custom domain + TLS

---

## Power Automate

### Cloud Flows

| Flow Type | Trigger | Use Case |
|---|---|---|
| **Automated** | Event-driven (email received, file created, record changed) | Background automation triggered by data changes |
| **Instant** | Manual (button in app, Teams, or mobile) | On-demand actions (approve request, send report) |
| **Scheduled** | Time-based (daily, weekly, cron) | Recurring tasks (send weekly digest, archive old data) |

### Built-in Connectors

- Microsoft 365: Outlook, Teams, SharePoint, OneDrive, Planner, To Do, Forms
- Azure: Azure Blob Storage, Azure SQL, Azure Service Bus, Azure DevOps, Azure AI services
- Third-party: Salesforce, ServiceNow, DocuSign, Slack, Jira, Dropbox, Twitter
- 900+ total connectors; premium connectors require Power Automate Premium license

### Desktop Flows (RPA)

- **UI automation**: Record clicks, keystrokes, and window interactions; replay on schedule
- **WinAutomation**: Automate desktop applications (legacy ERP, non-API systems)
- **Web scraping**: Extract data from web pages without API access
- **SAP automation**: Built-in SAP actions
- **Run mode**: Attended (with logged-in user) or unattended (runs in background on bot machine)

### AI Builder

- **Document processing (form recognizer)**: Extract fields from PDFs and images (invoices, receipts, ID documents)
- **Object detection**: Detect objects in images (products on shelves, defects)
- **Text classification**: Categorize text (support ticket routing, sentiment)
- **Prediction**: Classification/regression on Dataverse data
- **Business card reader**: Extract contact info from business card images
- **No ML expertise required**: Point AI Builder at training data, click train, use in flows

---

## Copilot Studio (formerly Power Virtual Agents)

**Purpose**: Build AI-powered chatbots and copilots without code. Publish to Teams, web, mobile, and other channels.

### Key Capabilities

| Feature | Description |
|---|---|
| **Generative AI (GPT-4)** | Integrated Azure OpenAI; bots answer from website/document knowledge bases without explicit topics |
| **Topics** | Conversation branches triggered by user intent (keyword or AI-matched) |
| **Actions** | Call Power Automate flows, HTTP endpoints, or Azure OpenAI plugins from bot |
| **Entities** | Slot-filling for structured data collection (name, date, email) |
| **Channels** | Teams, web chat, Facebook Messenger, mobile, custom |
| **Authentication** | Entra ID SSO, custom OAuth for user-specific data access |
| **Orchestrator** | Route to existing Azure Bot Framework skills |
| **Analytics** | Built-in session analytics, topic usage, escalation rates |

---

## Dataverse

**Purpose**: Enterprise-grade, relational data platform underlying Power Platform and Dynamics 365. Provides security, business logic, and OData API without building a custom database.

### Key Concepts

| Concept | Description |
|---|---|
| **Tables** | Structured data containers (like database tables); standard (out-of-box) or custom |
| **Columns** | Fields within a table; typed (text, number, date, lookup, choice, file) |
| **Relationships** | One-to-many and many-to-many; enforced referential integrity |
| **Forms** | UI layout definitions for model-driven apps |
| **Views** | Saved queries with columns and filter criteria |
| **Business rules** | Declarative logic on form fields (show/hide, required, validation) without code |
| **Plugins** | C#/.NET code triggered on record CRUD events (synchronous or asynchronous) |
| **Power Fx** | Low-code formula language for column calculations |
| **OData API** | REST API (`/api/data/v9.2/`) for CRUD operations; Postman/SDK friendly |
| **Dataverse for Teams** | Simplified Dataverse per-team for Teams-embedded apps; no premium license for basic use |

### Row-Level Security

- **Security roles**: Defined set of table/column permissions (Create/Read/Update/Delete at Organization/Business Unit/Team/User scope)
- **Business units**: Hierarchical org structure for data isolation
- **Teams**: Share records and roles across team members
- **Column-level security**: Restrict access to specific sensitive columns

---

## Power BI

**Purpose**: Self-service and enterprise analytics platform. Build interactive reports and dashboards; publish to colleagues, embed in apps.

### Key Concepts

| Concept | Description |
|---|---|
| **Datasets / Semantic models** | Data model with tables, relationships, DAX measures |
| **Reports** | Interactive visualizations built on a semantic model |
| **Dashboards** | Pinned tiles from reports; real-time data tiles |
| **Dataflows** | Reusable ETL pipelines (Power Query in the cloud); write to ADLS Gen2 |
| **DirectQuery** | Live query to source database; always fresh; performance depends on source |
| **Import** | Data cached in Power BI; scheduled refresh up to 48×/day (Premium) |
| **Composite model** | Mix Import and DirectQuery tables in one report |

### Licensing

| License | Capabilities |
|---|---|
| **Power BI Free** | Create and share reports; only individual viewing |
| **Power BI Pro** | Share with colleagues; collaborate on workspaces; $10/user/month |
| **Power BI Premium (per user)** | All Pro features + larger datasets, paginated reports, deployment pipelines; $20/user/month |
| **Power BI Premium (capacity)** | Dedicated capacity; no per-viewer license needed; P1 = 8 vCores; higher tiers for more |
| **Power BI Embedded** | Azure capacity for embedding in custom apps; A-SKU (not P-SKU) |

---

## Environment Strategy and ALM

### Environments

| Environment | Purpose |
|---|---|
| **Default** | Every tenant has one; development sandbox; avoid using for production |
| **Developer** | Individual developer sandbox; free with dev license |
| **Sandbox** | For dev and test; can be reset; trial of 30 days |
| **Production** | For live apps; full SLA; can backup and restore |

### Solutions (ALM)

- **Solution**: Container for customizations (apps, flows, tables, connection references)
- **Publisher**: Namespace prefix for customizations
- **Managed solution**: Deployed to target env; locked for editing; uninstall cleanly
- **Unmanaged solution**: In development environments; fully editable
- **Solution checker**: Validate solution against best practice rules before deployment
- **GitHub Actions / Azure DevOps**: `pac solution export`, `pac solution import`, `pac solution publish` in CI/CD pipelines

---

## Azure Integration

| Integration | Details |
|---|---|
| **Trigger flows from Azure** | Service Bus, Event Grid, HTTP webhooks trigger Power Automate flows |
| **Azure SQL connector** | Cloud flow reads/writes Azure SQL; premium connector |
| **Azure Blob connector** | Read/write files in Blob Storage from flows and canvas apps |
| **Custom connectors** | Wrap any REST/SOAP API as a connector; OpenAPI spec or manual definition |
| **Azure API Management** | Expose backend APIs securely to Power Platform via custom connectors |
| **On-premises data gateway** | Secure bridge for Power Platform to access on-premises SQL, Oracle, file systems |
