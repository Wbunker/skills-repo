# Integration Services — Capabilities

## Application Integration (iPaaS)

Application Integration is Google Cloud's Integration Platform as a Service (iPaaS) — a fully managed, no-code/low-code integration platform for connecting GCP services, SaaS applications, and on-premises systems.

### Core Design Model

Integrations are built using a **visual workflow designer** in the GCP console. An integration is a sequence of tasks executed based on triggers and conditions. The data model is based on integration variables (typed: string, int, double, boolean, JSON, proto message, string array, etc.) passed between tasks.

### Triggers

Events that start an integration execution:
- **API Trigger**: synchronous HTTP(S) invocation; returns a response; unique trigger ID maps to a URL endpoint; suitable for request-response patterns.
- **Pub/Sub Trigger**: executes on messages published to a Pub/Sub topic; asynchronous; no response returned.
- **Cloud Scheduler Trigger**: cron-based scheduling; creates a Cloud Scheduler job automatically.
- **Eventarc Trigger**: executes when an Eventarc event fires (Cloud Storage, Audit Logs, etc.).
- **Salesforce Trigger**: executes on Salesforce platform events or CDC (Change Data Capture) events; requires a Salesforce connection.
- **SFTP Trigger**: polls or watches an SFTP server for new/modified files; requires an SFTP connection.

### Tasks

Processing steps within an integration:
- **Call Integration**: invoke a sub-integration synchronously or asynchronously; pass and receive variables; enables modular integration design.
- **Call REST Endpoint**: HTTP request to any REST API with authentication (API key, OAuth 2.0, service account); map response fields to integration variables.
- **Call Connector**: invoke an Integration Connector to read/write data in a connected SaaS system (Salesforce, ServiceNow, SAP, etc.).
- **Data Mapping**: transform and map data between variables; convert types; construct JSON/proto objects; use built-in functions (string, date, arithmetic, array operations).
- **Loop**: iterate over an array variable; execute nested tasks per element; accumulate results.
- **Decision (Switch)**: conditional branching based on variable values or expressions.
- **Suspend**: pause integration and wait for a callback (human approval, external system response); resume with a result.
- **Throw Error**: raise an application error to trigger error handling.
- **Cloud Functions Task**: invoke a Cloud Function for custom code execution.
- **Cloud Run Task**: invoke a Cloud Run service.
- **BigQuery Execute Query**: run a BigQuery SQL query; return results.
- **Pub/Sub Publish**: publish a message to a Pub/Sub topic.
- **Send Email**: send email via SendGrid or SMTP connection.

### Error Handling

Each task can have a retry policy (fixed or exponential backoff) and an error handler (a separate task graph executed on failure). Integration-level error handlers catch unhandled errors. Failed executions are captured in the execution history with full variable state for debugging.

### Execution History and Monitoring

- All executions are logged with start/end time, status, trigger, and per-task execution trace.
- Variable values at each task step are visible in the execution trace for debugging.
- Cloud Monitoring metrics: execution count, success rate, latency; create alerting policies on failure rate.
- Logs exported to Cloud Logging.

### Versioning and Deployment

- Integrations have versioned snapshots; publish a version to make it live; previous versions retained.
- Environments: integrations are scoped to a region; no built-in multi-environment (dev/prod) separation — use separate GCP projects.
- CI/CD: export integration as JSON; import via API; integrate into Cloud Build pipelines.

---

## Integration Connectors

Integration Connectors is a managed connectivity layer providing 200+ pre-built connectors to SaaS applications, databases, and enterprise systems.

### Supported Connector Categories

**CRM & Sales**: Salesforce (objects, platform events, bulk API), HubSpot, Zoho CRM, Microsoft Dynamics 365, SugarCRM.

**ITSM & DevOps**: ServiceNow (tables, incidents, change requests), Jira (issues, projects, boards), GitHub (repos, issues, PRs), GitLab, PagerDuty, Zendesk.

**ERP & Finance**: SAP (BAPI, IDoc, OData), Oracle ERP Cloud, Microsoft Dynamics 365 Finance, NetSuite, Workday.

**Marketing & Productivity**: Marketo, Mailchimp, Slack (channels, messages), Microsoft Teams, Google Workspace (Drive, Sheets, Docs, Calendar, Gmail, Admin SDK), Asana, Monday.com, Smartsheet.

**Databases**: MySQL, PostgreSQL, SQL Server, Oracle DB, Spanner, BigQuery, Snowflake, Teradata.

**Storage & Files**: SFTP, FTP, FTPS, Box, Dropbox, SharePoint, OneDrive, AWS S3.

**Messaging**: Kafka, RabbitMQ, ActiveMQ, IBM MQ.

### Connection Management

- Each connection is a named, configured instance of a connector (e.g., "salesforce-prod-connection" using OAuth 2.0 and org URL for your Salesforce production org).
- Connections are managed in the **Connection Manager** in the GCP console.
- Connections store credentials in Secret Manager; the connection configuration references secret versions.
- Connections support **Private Service Connect** for private connectivity to on-premises systems or systems in a VPC without exposing traffic to the internet.

### Usage in Application Integration

- Add a "Call Connector" task in an Application Integration workflow.
- Select the connection, entity (e.g., Salesforce Account), and action (list, get, create, update, delete, or execute a custom action).
- Map connector input/output to integration variables.

### Usage in Workflows

- Workflows can call Integration Connectors via the Connectors API REST endpoint.
- The `googleapis.integrations.v1` connector in Workflows can execute Application Integrations.

---

## Cloud Endpoints

Cloud Endpoints is an API gateway for APIs hosted on GCP that provides authentication, monitoring, logging, and tracing using the **Extensible Service Proxy (ESP)** or **ESP V2** (based on Envoy).

### How It Works

1. Define your API using **OpenAPI 2.0** (REST) or **proto** (gRPC) specification.
2. Deploy the spec to **Service Management** (`gcloud endpoints services deploy`); this creates a managed service configuration with a version ID.
3. Run the ESP/ESPV2 as a sidecar in front of your backend (Cloud Run, GKE sidecar container, Compute Engine, App Engine flexible).
4. ESP validates incoming requests against the service configuration before forwarding to the backend.

### Supported Backends

- **Cloud Run**: ESPV2 runs as a sidecar container in the Cloud Run service; or run as a separate Cloud Run service in front of the backend.
- **GKE**: ESPV2 deployed as a Kubernetes sidecar or as a Deployment with a Service.
- **Compute Engine**: ESPV2 runs on the same VM or as a separate VM.
- **App Engine Flexible**: ESP added as a second container.

### Features

- **Authentication**: API key validation (for registered developer apps), JWT validation (Google Identity, Auth0, Firebase Auth, custom), service account authentication.
- **Request Logging**: all requests logged to Cloud Logging with request/response headers and status.
- **Distributed Tracing**: Cloud Trace integration; trace spans for each request through ESP to backend.
- **Rate Limiting**: per-consumer quota enforcement defined in the service config (`x-google-quota` OpenAPI extension).
- **HTTPS**: ESP handles TLS termination; backend communication can be HTTP.
- **API Versioning**: multiple service configs (versions) can exist; rollback by redeploying a previous config.

### OpenAPI Extensions

Cloud Endpoints uses Google-specific OpenAPI extensions:
- `x-google-backend`: specify the backend URL (for Cloud Run backend with ESP as separate service).
- `x-google-quota`: define quota limits (method-level and consumer-level).
- `x-google-security`: specify authentication requirements (api_key, jwt).
- `x-google-management`: specify the service name.

### vs API Gateway

| Criterion | Cloud Endpoints (ESPV2) | API Gateway |
|---|---|---|
| Proxy mode | Sidecar or standalone ESP container | Fully managed (no container to run) |
| Backend | Cloud Run, GKE, GCE, App Engine Flex | Cloud Run, Cloud Functions, App Engine |
| gRPC support | Yes (native transcoding) | No (REST/OpenAPI only) |
| Setup | Deploy spec + run ESP container | Deploy spec + create gateway resource |
| WebSocket | Supported via Envoy | Not supported |
| Price | ESP container cost only | Per million API calls |

---

## API Gateway

API Gateway is a fully managed serverless gateway for HTTP APIs backed by Cloud Run, Cloud Functions, or App Engine. It requires no ESP container — you deploy an OpenAPI 2.0 spec and Google manages the gateway infrastructure.

### Key Features

- **Managed infrastructure**: no VM, container, or proxy to run; Google scales the gateway automatically.
- **OpenAPI 2.0**: define routes, backends, security in a YAML spec using `x-google-backend` extension.
- **Authentication**: API key, JWT (Firebase Auth, Google Identity, Auth0, Okta).
- **Rate limiting**: per-consumer quota via `x-google-quota` extension.
- **Cloud Logging & Monitoring**: automatic request logging and metrics (request count, latency, errors).
- **Multiple backends**: different routes in the spec can point to different Cloud Run services or Cloud Functions.

### API Gateway Concepts

- **API**: top-level resource representing your API (name, managed service name).
- **API Config**: a versioned deployment of an OpenAPI spec; immutable once created; referenced by a gateway.
- **Gateway**: the deployed endpoint that serves traffic; points to a specific API config; has a default hostname (`GATEWAY_ID-HASH.REGION.gateway.dev`).

### Limitations vs Apigee

- No developer portal.
- No monetization.
- No complex transformation policies.
- No analytics dashboards (only Cloud Monitoring metrics).
- No shared flows or policy reuse.
- WebSocket not supported.
