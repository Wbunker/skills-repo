# Migration Hub & Discovery — Capabilities Reference

For CLI commands, see [migration-hub-cli.md](migration-hub-cli.md).

## AWS Application Discovery Service

**Purpose**: Collects server inventory, utilization, and dependency data from on-premises environments to inform migration planning. Supports two discovery modes: agentless (via Discovery Connector) and agent-based (via Discovery Agent).

### Discovery Modes

| Mode | Mechanism | Data Collected | Best For |
|---|---|---|---|
| **Agentless (Discovery Connector)** | Virtual appliance deployed in VMware vCenter; communicates with vCenter API | VM metadata, CPU/RAM/disk allocation, network interfaces, vCenter topology | VMware environments; no OS-level access required |
| **Agent-based (Discovery Agent)** | Lightweight agent installed on each server (Windows or Linux) | Server specs, CPU/RAM/disk utilization, running processes, network connections, inbound/outbound TCP connections | Physical servers, non-VMware VMs, detailed dependency mapping |
| **Bulk import (CSV)** | Upload spreadsheet of server data manually | Any data you supply | Known inventories without direct server access |

### Data Collected

| Category | Details |
|---|---|
| **Server specs** | Hostname, OS type and version, CPU count, total RAM, total disk capacity |
| **Utilization** | Average and peak CPU utilization, RAM utilization, disk read/write throughput, network I/O |
| **Network dependencies** | Inbound and outbound TCP connections between servers; source IP, destination IP, destination port, process name |
| **Running processes** | Process name, path, CPU and memory consumption per process (agent-based only) |

### Data Export

- Discovered data is stored in the Application Discovery Service data store (per-account, per-region)
- **Continuous export to S3**: Enable `StartContinuousExport`; data streams to a customer-owned S3 bucket in Apache Parquet format for Athena querying
- **On-demand export**: `StartExportTask` exports a snapshot to S3 as CSV files
- Migration Hub automatically ingests discovery data when both services are used in the same home region

### Migration Hub Integration

- Discovered servers appear automatically in Migration Hub's server inventory when the home region matches
- Servers can be grouped into Migration Hub applications directly from the discovery data
- Network dependency data informs application grouping decisions

### Bulk Import via CSV

- Download the CSV template from the console or documentation
- Populate columns: ExternalId, IPAddress, HostName, OS, RAM, CPU, NumberOfCores, NumberOfDisks, DiskCapacity
- Upload via `StartImportTask`; servers appear in inventory after processing
- Useful for importing data from third-party discovery tools (e.g., Flexera, ServiceNow CMDB)

---

## AWS Migration Hub

**Purpose**: Central tracking dashboard for server and application migrations across AWS migration tools. Provides a single pane of glass for migration status regardless of which migration service is doing the work.

### Home Region

- Migration Hub data (server inventory, application groupings, migration task progress) is stored in a single AWS region called the **home region**
- Supported home regions: `us-east-1` (US East N. Virginia) and `eu-central-1` (Europe Frankfurt)
- Home region must be set once per account before use; it cannot be changed after migration tasks are recorded
- All integrated migration tools must be configured to report to the same home region
- Set via the Migration Hub console or via `aws migrationhub-config put-home-region`

### Application Grouping

- Servers discovered via Application Discovery Service or imported manually can be grouped into **applications** in Migration Hub
- An application represents a logical workload (e.g., a three-tier web app with web, app, and database servers)
- Applications provide a unit of tracking: overall status is derived from the status of all servers within the application

### Migration Task Tracking

Migration Hub aggregates task status reported by integrated services. Progress states:

| State | Meaning |
|---|---|
| **Not Started** | Migration task created but no action taken |
| **In Progress** | Active migration underway |
| **Completed** | Migration finished successfully |
| **Failed** | Migration encountered a terminal error |

### Integrated Migration Services

| Service | Integration |
|---|---|
| **AWS Application Migration Service (MGN)** | Reports per-server replication and cutover status |
| **AWS Database Migration Service (DMS)** | Reports replication task progress |
| **AWS Server Migration Service (SMS)** | Legacy; reports replication run status (SMS is deprecated in favor of MGN) |
| **CloudEndure Migration** | Legacy; reports replication and cutover status (superseded by MGN) |

### Discovery Data Import

- Server inventory from Application Discovery Service is visible in Migration Hub when the home region matches
- Servers can also be added manually or via bulk import
- Servers transition from "discovered" to "in progress" to "completed" as migration tools report task progress

### Server & Application Inventory View

- **Servers view**: Lists all discovered or imported servers with their current migration status and associated application
- **Applications view**: Shows each application's overall status (percentage of servers completed), grouped progress, and direct links to the migration tasks

---

## AWS Migration Hub Orchestrator

**Purpose**: Workflow automation service that coordinates multi-step migration workflows. Provides pre-built templates for common migration patterns and orchestrates both automated and manual steps across AWS services.

### Core Concepts

| Concept | Description |
|---|---|
| **Workflow** | A named migration project based on a template; contains step groups and steps |
| **Template** | Pre-built workflow definition for a specific migration pattern (e.g., SAP on AWS, SQL Server to AWS) |
| **Step group** | A named phase within a workflow (e.g., "Pre-migration", "Migration", "Post-migration") |
| **Step** | An individual task within a step group; can be automated or manual |
| **Plugin** | Software component installed in the source environment that enables Orchestrator to execute steps remotely |

### Workflow Templates

| Template | Use Case |
|---|---|
| **SAP on AWS** | End-to-end migration of SAP HANA and SAP NetWeaver workloads to AWS |
| **SQL Server on AWS** | Migration of SQL Server databases to Amazon RDS for SQL Server or EC2 |
| **Generic migration** | Customizable template for workloads without a purpose-built template |

### Plugins

| Plugin | Description |
|---|---|
| **MGN plugin** | Installed on source servers alongside the MGN replication agent; enables Orchestrator to trigger MGN test launches, cutover, and finalization |
| **AWS CLI plugin** | Runs AWS CLI commands as workflow steps; used for steps that invoke AWS services (e.g., creating RDS instances, modifying security groups) |

### Workflow Steps

- **Automated steps**: Executed by Orchestrator without human intervention; invoke AWS API calls, run SSM documents, or trigger MGN/DMS actions via plugins
- **Manual steps**: Pauses the workflow and waits for a human to mark the step complete; used for tasks requiring human judgment (e.g., validation sign-off, firewall change requests)
- Steps have configurable inputs (parameters), outputs (exported values used by downstream steps), and completion statuses

### Step Groups

- Step groups represent phases of the migration workflow
- Steps within a step group execute sequentially by default
- A step group does not proceed until all steps in the current group complete
- Custom step groups can be added to any template-based workflow

### Instance Deployment & Cutover Orchestration

- Orchestrator tracks MGN source server state and triggers test launches and cutovers at the appropriate workflow step
- Cutover orchestration sequences: pre-cutover validation → MGN cutover → post-cutover configuration (SSM documents) → validation → finalization
- Supports coordinating cutovers across multiple servers in a defined order

### Status Tracking

- Workflow execution status: `NOT_STARTED`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `FAILED`, `DELETING`
- Step status: `AWAITING_DEPENDENCIES`, `READY`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `PAUSED`
- CloudWatch Events emitted on workflow and step state transitions for external monitoring

---

## AWS Migration Hub Refactor Spaces

**Purpose**: Managed service for implementing the strangler-fig pattern during application modernization. Provides the networking infrastructure (API Gateway, NLB, VPC routing) to incrementally route traffic between a monolithic application and new microservices.

### Core Concepts

| Concept | Description |
|---|---|
| **Environment** | Top-level container for a Refactor Spaces deployment; spans one or more AWS accounts via AWS RAM sharing |
| **Application** | A logical application within an environment; owns an API Gateway and associated routing infrastructure |
| **Service** | A backend target (Lambda function, URL endpoint, or ECS service) that handles routed traffic |
| **Route** | A traffic routing rule that maps requests to a service based on URI path or as a default fallback |

### Route Types

| Route Type | Description |
|---|---|
| **Default route** | Catches all requests not matched by a URI path route; typically points to the existing monolith |
| **URI path route** | Matches requests by URI prefix (e.g., `/api/orders`); routes matching traffic to a new microservice |

### Strangler-Fig Pattern Support

1. Deploy Refactor Spaces environment and application; point default route at the existing monolith
2. Build a new microservice for one feature/module
3. Create a URI path route pointing that path to the new microservice
4. Traffic for that path is now served by the microservice; all other traffic still hits the monolith
5. Repeat for additional modules until the monolith is fully replaced

### Infrastructure Provisioned

| Component | Role |
|---|---|
| **Amazon API Gateway** | Receives inbound HTTP/HTTPS requests; applies routing rules |
| **Network Load Balancer (NLB)** | Forwards matched traffic to services within the VPC |
| **VPC route tables** | Managed by Refactor Spaces to route traffic between accounts/VPCs in the environment |

### Cross-Account Service Support

- An environment can span multiple AWS accounts using AWS Resource Access Manager (RAM)
- Services in member accounts are registered into the environment; Refactor Spaces handles the cross-account VPC connectivity automatically
- Enables the new microservices to live in a separate AWS account from the monolith

### VPC Lattice Integration Path

- Refactor Spaces provisions NLB and API Gateway for routing today
- AWS VPC Lattice is the longer-term service-to-service networking primitive; migration paths from Refactor Spaces to VPC Lattice are supported as the services evolve

---

## AWS Migration Hub Strategy Recommendations

**Purpose**: Analyzes on-premises server and application portfolio to generate migration strategy recommendations. Evaluates each application component against the 7 Rs framework and produces a business case.

### Portfolio Assessment Flow

1. Install the Migration Hub Strategy Recommendations collector on a server in the on-premises environment (agent-based data collection)
2. Collector gathers application data: running processes, installed software, server utilization, IIS/SQL Server configurations, .NET and Java application details
3. Data is sent to Migration Hub Strategy Recommendations for analysis
4. Service generates strategy recommendations per application component

### Server Analysis (Agent-Based Data Collection)

- Collector identifies application components from running processes and installed software
- Captures: OS version, installed applications, .NET/Java runtime versions, database engines, web server configs
- Collects utilization metrics to inform right-sizing and modernization feasibility
- No network sniffing; process-level analysis only

### Anti-Pattern Detection

The service identifies patterns that indicate poor fit for a given strategy:

| Anti-Pattern | Description |
|---|---|
| **Hard-coded IP addresses** | Detected in config files; indicates replatforming risk |
| **End-of-support OS/runtime** | Windows Server 2008, .NET Framework 2.0, etc.; flags modernization urgency |
| **Database engine mismatch** | Detects heterogeneous database dependencies that complicate migration |
| **Mainframe dependencies** | Flags applications with COBOL/VSAM dependencies |

### Strategy Recommendations — The 7 Rs

| Strategy (R) | Description |
|---|---|
| **Retire** | Decommission the application; no migration needed |
| **Retain** | Keep on-premises for now; revisit later |
| **Rehost** | Lift-and-shift to EC2 with no code changes (use MGN) |
| **Relocate** | Move to AWS without OS changes (VMware Cloud on AWS) |
| **Replatform** | Migrate with minor optimizations (e.g., move to RDS, Elastic Beanstalk) |
| **Refactor** | Re-architect for cloud-native services (containers, serverless) |
| **Repurchase** | Replace with a SaaS product (e.g., move to Salesforce, ServiceNow) |

The service assigns a recommended R and a confidence level (HIGH, MEDIUM, LOW) per application component based on collected data and anti-pattern analysis.

### Application Component Analysis

- Application components are automatically identified from discovered processes and software
- Each component is linked to source servers, ports, and detected dependencies
- Components can be manually created, merged, or split in the console
- Dependencies between components are mapped to inform grouping and sequencing

### Business Case Generation

- Aggregates recommendations across the full portfolio
- Estimates on-premises cost (TCO) vs. AWS cost for each strategy
- Produces a business case report (PDF/Excel) downloadable from the console
- Inputs: data center costs, server details, estimated utilization, AWS pricing; outputs: 3-year cost comparison, potential savings
