# Ops & Incident Tools — Capabilities Reference

For CLI commands, see [ops-incident-cli.md](ops-incident-cli.md).

## AWS Chatbot

**Purpose**: Integrate AWS service notifications and interactive commands into Slack channels and Microsoft Teams channels; enables teams to receive alerts, run diagnostics, and execute operational tasks without leaving their chat tools.

### Core Concepts

| Concept | Description |
|---|---|
| **Chat configuration** | A connection between an AWS account and a specific Slack channel or Teams channel; the unit that defines which notifications are delivered and what permissions are granted |
| **Slack channel configuration** | A chat configuration targeting a Slack workspace channel; identified by workspace ID and channel ID |
| **Microsoft Teams channel configuration** | A chat configuration targeting a Teams tenant, team, and channel; identified by tenant ID, team ID, and channel ID |
| **SNS topic** | The primary notification source; Chatbot subscribes to SNS topics and formats messages for delivery to the chat channel |
| **Guardrails (IAM policy)** | An IAM policy attached to the Chatbot configuration that acts as a permission boundary; any AWS CLI command run from the chat channel is scoped to the intersection of the channel role and the guardrails policy |
| **Channel role (IAM role)** | An IAM role assumed by Chatbot when executing commands on behalf of users in the chat channel; defines the maximum effective permissions |
| **Notification source** | An AWS service that publishes events via SNS or EventBridge that Chatbot can deliver to chat |

### Supported Notification Sources

| Source | How it integrates |
|---|---|
| **Amazon CloudWatch** | Alarms (OK / ALARM / INSUFFICIENT_DATA state changes) via SNS |
| **AWS Security Hub** | Findings and aggregated security events via SNS or EventBridge |
| **AWS Config** | Compliance change notifications via SNS |
| **AWS Budgets** | Budget threshold alerts via SNS |
| **AWS CodePipeline** | Pipeline state change events (started, succeeded, failed) via CloudWatch Events / EventBridge |
| **AWS CodeBuild** | Build state notifications via SNS |
| **AWS CodeDeploy** | Deployment notifications via SNS |
| **AWS CodeCommit** | Repository events (pull requests, comments) via SNS |
| **AWS GuardDuty** | Findings forwarded via EventBridge → SNS |
| **AWS Health** | Personal Health Dashboard events via EventBridge → SNS |
| **Amazon EventBridge** | Any EventBridge rule can route to an SNS topic subscribed by Chatbot |

### Interactive Commands from Chat

| Capability | Details |
|---|---|
| **AWS CLI via chat** | Type `@aws <CLI command>` in the Slack/Teams channel; Chatbot executes the command using the channel role and guardrails |
| **Run SSM Automation runbooks** | Invoke SSM Automation documents directly from the chat channel to start remediation workflows |
| **Invoke Lambda functions** | Run Lambda functions on demand from chat; useful for triggering diagnostic or remediation scripts |
| **CloudWatch alarm actions** | View alarm state, history, and associated metrics from chat |

### Guardrails Design

Guardrails are IAM policy documents that limit which AWS API actions can be called from the chat channel. AWS provides a managed read-only guardrails policy; custom guardrails can allow specific write actions (e.g., `ec2:RebootInstances`, `ssm:StartAutomationExecution`) while blocking sensitive ones (e.g., `iam:*`, `s3:DeleteBucket`). The effective permission is the intersection of the channel IAM role and the guardrails policy.

### Key Patterns

- **CloudWatch alarm → SNS → Chatbot → Slack** — the canonical alerting pipeline; set a CloudWatch alarm action to an SNS topic that Chatbot subscribes to for instant Slack notifications
- **Runbook execution from chat** — pair Chatbot with SSM Automation documents so on-call engineers can trigger standard remediation runbooks (`@aws ssm start-automation-execution`) without console access
- **Read-only guardrails for broad channels** — use AWS-managed read-only guardrails for general ops channels and create tighter custom guardrails for channels with write access
- **Security Hub findings routing** — use EventBridge rules matching Security Hub findings of HIGH/CRITICAL severity → SNS → Chatbot for immediate security team notifications
- **Multi-account notifications** — configure Chatbot in each account and route to the same Slack channel to consolidate alerts across accounts

---

## AWS Incident Manager

**Purpose**: Automate and coordinate incident response workflows; reduces MTTR by automatically engaging responders, running runbooks, and tracking timeline events from a single pane of glass.

### Core Concepts

| Concept | Description |
|---|---|
| **Response plan** | A template that defines how an incident is handled; specifies title, impact, chat channel, SSM Automation runbook, escalation plan, and engagement contacts |
| **Incident record** | The live record created when an incident is triggered from a response plan; captures status, impact, timeline, related items, and all responder activity |
| **Impact** | Severity level of the incident (1–5, where 1 is critical); determines urgency of engagement |
| **Timeline event** | A timestamped entry on the incident record; auto-generated (incident created, runbook started, contact engaged) or manually added by responders |
| **Related items** | Artifacts linked to an incident record (runbook ARNs, metric graphs, post-incident analysis links, CloudWatch dashboards) |
| **Engagement** | The process of notifying and confirming responders via SSM Contacts; supports PagerDuty, OpsGenie, email, SMS, and voice |
| **Escalation plan** | An SSM Contacts escalation plan that defines a sequence of engagement stages; if a contact does not acknowledge within a timeout, the next stage fires |
| **Replication set** | Defines the AWS Regions where Incident Manager replicates incident data; enables cross-region resilience for the incident management plane |
| **Post-incident analysis** | A structured blameless retrospective attached to a closed incident record; tracks action items and links to timeline evidence |

### Response Plan Structure

| Field | Description |
|---|---|
| **Title** | Template for the incident title; can include dynamic variables |
| **Impact** | Default impact level for incidents created from this plan |
| **Chat channel** | AWS Chatbot channel configuration ARN; all responders collaborate in the linked Slack/Teams channel |
| **Runbook** | SSM Automation document and parameters; starts automatically when the incident opens |
| **Escalation plan** | SSM Contacts escalation plan ARN; engages on-call responders immediately |
| **Tags** | Metadata for categorizing and filtering incidents |

### SSM Contacts Integration

| Concept | Description |
|---|---|
| **Contact** | An individual responder defined in SSM Contacts; has contact channels (email, SMS, voice) and an engagement plan |
| **Contact channel** | A specific delivery endpoint for a contact (email address, phone number); must be activated before use |
| **Engagement plan** | Defines when and how to reach a contact (e.g., try email first, then SMS after 5 minutes) |
| **Escalation plan** | An ordered set of engagement stages referencing contacts; if no acknowledgment within the stage duration, the next stage begins |
| **On-call schedule** | Rotations (daily/weekly) that determine which contact is active at any given time; referenced in escalation plans |
| **PagerDuty / OpsGenie integration** | Incident Manager can engage PagerDuty and OpsGenie services as contacts, triggering alerts in those platforms |

### Incident Lifecycle

1. Incident is triggered (manually via console/CLI, via CloudWatch alarm action, or via EventBridge rule)
2. Incident record is created from the response plan
3. SSM Automation runbook starts automatically
4. Escalation plan engages responders (email/SMS/PagerDuty/OpsGenie)
5. Responders collaborate in the linked Chatbot chat channel
6. Timeline events are added automatically and manually
7. Incident is resolved (status updated to RESOLVED)
8. Post-incident analysis is created and action items are tracked

### Key Patterns

- **CloudWatch alarm → Incident Manager** — set a CloudWatch alarm action to trigger an Incident Manager incident via EventBridge; zero-touch incident creation for known failure modes
- **Auto-remediation runbook** — attach an SSM Automation document that performs initial triage (snapshot, restart, scale out) before any human is paged
- **Multi-region replication** — configure replication sets covering primary and DR regions so the incident management plane remains available during a regional event
- **PagerDuty bridge** — use SSM Contacts PagerDuty integration to preserve existing on-call rotations while gaining Incident Manager's timeline and runbook capabilities
- **Post-incident analysis** — link timeline events to action items in the analysis; integrates with Jira and other ticketing systems via EventBridge notifications

---

## AWS User Notifications

**Purpose**: Centralized service for configuring and delivering AWS account and organizational notifications across multiple channels; provides a single place to manage event rules and delivery without manually wiring SNS topics per service.

### Core Concepts

| Concept | Description |
|---|---|
| **Notification hub** | A regional hub that receives and processes notification events; must be created in each region where you want to receive notifications |
| **Event rule** | A rule that filters AWS events and routes matching events to configured notification channels; defines source service, event type, and optional filter criteria |
| **Notification channel** | A delivery destination for notifications; supported channels include email, SMS, Slack (via Chatbot), Amazon Chime, and EventBridge |
| **Notification event** | An instance of an event that matched a rule and was delivered to channels; has a status (SENT, FAILED) and the event payload |
| **Aggregation** | Groups similar notification events within a time window to reduce noise; configurable per event rule |

### Notification Channel Types

| Channel Type | Details |
|---|---|
| **Email** | Direct email delivery; must be verified before activation |
| **SMS** | Text message delivery via verified phone number |
| **Slack (via Chatbot)** | Routes to a Chatbot Slack channel configuration; reuses existing Chatbot setup |
| **Amazon Chime** | Routes to a Chime webhook |
| **AWS EventBridge** | Publishes notification events to an EventBridge event bus for downstream routing and processing |

### Event Categories

| Category | Description |
|---|---|
| **Management events** | Account-level events such as root user sign-in, password policy changes, or service quota changes |
| **Configuration changes** | Resource configuration state changes (e.g., EC2 instance state change, S3 bucket ACL change) |
| **Operational events** | Service health and operational alerts (e.g., CloudWatch alarms, EC2 scheduled maintenance) |

### Scope

| Scope | Description |
|---|---|
| **Account-level** | Notifications apply to resources and events in a single AWS account |
| **Organization-level** | Notifications apply across all accounts in an AWS Organization; managed from the management account or a delegated administrator |

### Aggregation

Event rules can be configured to aggregate similar events. When aggregation is enabled, multiple matching events within the configured time window are grouped into a single notification, reducing alert fatigue. Aggregation is configured per event rule with a time window (e.g., 5 minutes, 1 hour).

### Key Patterns

- **Organization-wide alerting** — create organization-level event rules in the management account to deliver security and health alerts to a central email or Slack channel without per-account configuration
- **Aggregation for noisy services** — enable aggregation on high-volume event rules (e.g., EC2 state changes in auto-scaling groups) to receive a single grouped notification instead of one per instance
- **EventBridge forwarding** — use EventBridge as a notification channel to fan out notifications to Lambda, SQS, or other services for custom processing and ticketing
- **Multi-channel delivery** — configure the same event rule to deliver to both email (for archival) and Slack (for real-time response)

---

## AWS Quick Setup

**Purpose**: Simplify configuration of AWS services at scale using pre-built configuration types; automates SSM Agent installation, patch management, inventory collection, and CloudWatch agent deployment across fleets of EC2 instances, OUs, or tagged resources.

### Core Concepts

| Concept | Description |
|---|---|
| **Configuration manager** | The top-level Quick Setup resource; represents a specific configuration type applied to a set of targets with defined parameters |
| **Configuration type** | The category of setup being automated (e.g., host management, patch policy, CloudWatch agent, IAM Identity Center access) |
| **Deployment targets** | Defines which accounts and OUs (for multi-account) or which instances (by tag or resource group) receive the configuration |
| **State Manager association** | The SSM State Manager association created and managed by Quick Setup to continuously enforce the desired configuration state |
| **Deployment status** | Per-target status of the Quick Setup deployment (Deploying, Success, Failed) |

### Supported Configuration Types

| Configuration Type | What it does |
|---|---|
| **Host management** | Installs/updates SSM Agent, enables inventory collection, configures default patch baseline, installs CloudWatch agent, configures update schedule |
| **Patch policy** | Defines and applies a patch baseline and maintenance window across targeted instances; integrates with Patch Manager |
| **CloudWatch agent** | Deploys and configures the CloudWatch unified agent on EC2 instances for metrics and log collection |
| **IAM Identity Center** | Configures permission sets and assignments for IAM Identity Center across accounts |
| **Distributor packages** | Deploys custom SSM Distributor packages to a fleet |
| **OpsCenter** | Enables OpsCenter and configures operational insights rules |

### Host Management Configuration Details

| Setting | Description |
|---|---|
| **Update SSM Agent** | Schedules automatic SSM Agent updates on a defined frequency |
| **Collect inventory** | Enables SSM Inventory collection (applications, network config, Windows updates, custom inventory) |
| **Scan for patches** | Runs patch compliance scans without installing patches |
| **Install patches** | Applies patches on a schedule using the default or custom patch baseline |
| **Install CloudWatch agent** | Deploys the CloudWatch unified agent and applies a configuration |
| **Update CloudWatch agent** | Keeps the CloudWatch agent at the latest version |

### Deployment Target Options

| Target Type | Description |
|---|---|
| **Entire organization** | Applies to all accounts in the AWS Organization (requires AWS Organizations integration) |
| **Specific OUs** | Applies to all accounts within selected Organizational Units |
| **Specific accounts** | Applies to a manually specified list of AWS accounts |
| **Tagged instances** | Applies to EC2 instances matching specific tag key/value pairs within target accounts |
| **Entire Region** | Applies to all EC2 instances in a selected region within target accounts |

### Key Patterns

- **Fleet-wide SSM Agent health** — use host management Quick Setup targeting the organization to ensure every EC2 instance has a current SSM Agent, enabling Session Manager, Run Command, and Patch Manager without manual intervention
- **Centralized patch policy** — create a patch policy configuration manager at the OU level so all new accounts automatically inherit the correct patch baseline and maintenance window
- **CloudWatch agent rollout** — use Quick Setup to deploy the CloudWatch agent configuration from Parameter Store (AmazonCloudWatch-linux or custom config) to all instances without SSM Run Command scripting
- **Incremental adoption** — start with a specific OU or tag target, verify results via the configuration manager deployment status, then expand to broader targets

---

## AWS Systems Manager for SAP

**Purpose**: Discover, register, manage, and operate SAP HANA and SAP NetWeaver systems running on AWS using native AWS tooling; enables backup, restore, start/stop, system refresh, and HANA System Replication management through SSM documents and integrated AWS services.

### Core Concepts

| Concept | Description |
|---|---|
| **Application** | An SAP system registered with SSM for SAP; identified by application type (HANA, SAP_ABAP) and SID |
| **Component** | A logical component within an SAP application (e.g., ABAP Central Services, Primary Application Server) |
| **Database** | An SAP HANA database instance registered with SSM for SAP; linked to an application |
| **Operation** | An async task performed by SSM for SAP (start, stop, backup, restore, system refresh); has a status and logs |
| **SSM document for SAP** | AWS-managed SSM Automation documents prefixed `AWSSAP-*` that implement SAP operations (backup, restore, start, stop) |
| **SAP monitoring** | CloudWatch metrics and dashboards for SAP HANA system health, memory usage, disk I/O, and replication lag |

### Supported SAP System Types

| Type | Description |
|---|---|
| **SAP HANA** | In-memory database; supports discovery, registration, backup/restore, start/stop, system replication management |
| **SAP NetWeaver (ABAP)** | ABAP application server stack; supports discovery, registration, start/stop |
| **SAP S/4HANA** | Full S/4HANA systems (ABAP stack with HANA database); managed as a combined application + database |

### Key Operations

| Operation | Description |
|---|---|
| **Register application** | Discovers and registers an SAP system running on EC2; requires SSM Agent and the SAP Data Provider for AWS installed on the host |
| **Start/Stop application** | Gracefully starts or stops SAP HANA or NetWeaver instances using SSM Automation documents |
| **Backup database** | Triggers a HANA backup to Amazon S3 using HANA backint integration; metadata tracked in SSM for SAP |
| **Restore database** | Restores a HANA database from a backup stored in S3 |
| **System refresh** | Clones production HANA data to a target (QA/dev) system; automates the HANA system refresh workflow |
| **HANA SR management** | Monitors and manages HANA System Replication (primary/secondary status, replication lag, takeover) |

### HANA System Replication (SR)

| Concept | Description |
|---|---|
| **Primary** | The active HANA instance; receives all write transactions |
| **Secondary** | The standby instance receiving redo log shipping from primary |
| **Replication mode** | Sync, async, or syncmem; controls when primary acknowledges commits relative to secondary confirmation |
| **Takeover** | Promotes the secondary to primary; can be triggered manually via SSM for SAP or automated via a CloudWatch alarm |
| **Replication lag** | Monitored via CloudWatch metrics published by SSM for SAP; triggers alarms when lag exceeds thresholds |

### Prerequisites

| Requirement | Details |
|---|---|
| **SSM Agent** | Must be installed and running on all EC2 instances hosting SAP workloads |
| **SAP Data Provider for AWS** | AWS SAP Data Provider agent must be installed; provides SAP system metadata to SSM for SAP |
| **IAM role** | EC2 instance profile with `AmazonSSMForSAPFullAccess` or equivalent permissions |
| **Secrets Manager** | HANA system credentials stored in Secrets Manager; SSM for SAP retrieves credentials at operation time |
| **S3 bucket** | Required for database backup storage; HANA backint configuration must point to the target bucket |

### CloudWatch Integration

SSM for SAP publishes HANA-specific metrics to CloudWatch under the `AWS/SSMForSAP` namespace:

| Metric | Description |
|---|---|
| `HANAReplicationStatus` | Status of HANA SR (0 = OK, non-zero = issue) |
| `HANAServiceStatus` | Health of individual HANA services (indexserver, nameserver) |
| `HANADiskUsage` | HANA data and log volume disk utilization |
| `HANAMemoryUsage` | HANA memory consumption vs. allocated memory |

### Key Patterns

- **Automated HANA backup to S3** — register the HANA database with SSM for SAP, configure HANA backint to S3, and schedule periodic backups via SSM Automation; backups are cataloged and restorable through the SSM for SAP API
- **System refresh automation** — use the system refresh operation to replace QA HANA data with a copy of production; automates the 10+ manual steps of a traditional HANA system refresh into a single API call
- **SR monitoring with auto-takeover** — publish HANA SR metrics to CloudWatch, create an alarm on `HANAReplicationStatus`, and trigger an SSM Automation runbook to perform takeover if replication breaks beyond a threshold
- **Secrets Manager for credentials** — store HANA system user (SYSTEM or dedicated backup user) credentials in Secrets Manager; rotate them with Secrets Manager rotation without updating SSM for SAP configuration
- **Unified fleet view** — use `list-applications` and `list-databases` to build a centralized inventory of all SAP systems running across multiple accounts and regions
