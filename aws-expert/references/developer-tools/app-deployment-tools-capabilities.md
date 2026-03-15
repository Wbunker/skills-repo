# App Deployment & Low-Code Tools — Capabilities Reference

For CLI commands, see [app-deployment-tools-cli.md](app-deployment-tools-cli.md).

---

## AWS Proton

**Purpose**: Fully managed infrastructure-as-code platform for platform engineering teams; defines standardized environment and service templates that application developers self-serve without needing to author CloudFormation or Terraform directly.

### Core Concepts

| Concept | Description |
|---|---|
| **Environment template** | A versioned IaC template (CloudFormation or Terraform) defining shared infrastructure (VPC, ECS cluster, etc.); platform teams author these |
| **Environment instance** | A deployed instance of an environment template; represents a running shared infrastructure stack (e.g., `prod`, `staging`) |
| **Service template** | A versioned IaC template defining how an application service is deployed within an environment; includes infrastructure and optional pipeline |
| **Service instance** | A deployed instance of a service template within a specific environment instance; represents one running service |
| **Component** | Reusable, independently managed infrastructure attached to an environment or service instance (e.g., an S3 bucket, SQS queue); allows developers to extend managed resources |
| **Template bundle** | A `.tar.gz` archive uploaded to S3 containing the IaC files for a template version |
| **Template version** | Major and minor versioning on templates; minor versions are compatible updates; major versions indicate breaking changes |
| **Pipeline integration** | Service templates can include a CodePipeline definition that Proton provisions alongside the service; enables end-to-end CI/CD from template |
| **Self-managed provisioning** | Proton can delegate provisioning to a customer-managed pipeline rather than provisioning directly; useful for Terraform Cloud, Atlantis, etc. |
| **Sync from Git** | Environment and service templates can sync directly from a Git repository (CodeCommit, GitHub, Bitbucket); Proton detects changes and creates new minor versions automatically |

### Template Provisioning Engines

| Engine | How it works |
|---|---|
| **AWS-managed CloudFormation** | Proton directly calls CloudFormation to provision; no additional setup required |
| **AWS-managed Terraform** | Proton provisions via a Terraform runtime it manages (Terraform Open Source via CodeBuild) |
| **Self-managed (customer pipeline)** | Proton sends provisioning requests to a customer-owned pipeline; customer handles the actual `terraform apply` or other tool |

### Template Version States

`Draft` → `Published` (major/minor); only `Published` versions are available for deployment. Platform teams can deprecate old versions to drive upgrades.

### Proton vs CDK vs SAM

| Tool | Best for | Audience | Abstraction |
|---|---|---|---|
| **AWS Proton** | Multi-team platform engineering; standardized, governed IaC templates developers self-serve | Platform engineers (template authors) + developers (template consumers) | Templates as a product; developers never see raw IaC |
| **AWS CDK** | Infrastructure authored in general-purpose languages (TypeScript, Python, Java, Go); full flexibility | Developers/DevOps comfortable with programming | L1 (raw CFN) through L3 (opinionated constructs) |
| **AWS SAM** | Serverless-focused; shorthand CloudFormation syntax for Lambda, API Gateway, DynamoDB, Step Functions | Serverless developers | CloudFormation extension with serverless defaults |

### Key Workflows

1. Platform team authors a template bundle (IaC files + `schema/schema.yaml` for input parameters) → uploads to S3
2. Register template version in Proton → publish the version
3. Developers create environment/service instances by supplying parameter values through console, CLI, or API
4. Proton provisions resources and tracks deployment status; updates propagate when a new template version is published

---

## AWS Launch Wizard

**Purpose**: Guided deployment service for enterprise applications; automates sizing, validation, and CloudFormation-based provisioning of complex workloads with minimal manual IaC authoring.

### Supported Workloads

| Workload | Description |
|---|---|
| **SQL Server AlwaysOn AG** | SQL Server Always On Availability Groups on EC2; multi-AZ HA with Windows Server Failover Cluster |
| **SQL Server (single node)** | Single-node SQL Server on EC2 for dev/test or smaller workloads |
| **SAP HANA** | SAP HANA database on EC2; includes storage and OS tuning per SAP best practices |
| **SAP NetWeaver** | SAP NetWeaver application layer on EC2; ABAP and Java stacks |
| **Active Directory** | AWS-hosted Microsoft Active Directory on EC2 with DNS and forest configuration |
| **Exchange** | Microsoft Exchange Server on EC2 with DAG configuration |

### Core Concepts

| Concept | Description |
|---|---|
| **Deployment** | A single provisioning run of a supported workload; records inputs, events, and provisioned resources |
| **Deployment sizing** | Launch Wizard recommends EC2 instance types and storage based on workload-specific sizing inputs (e.g., SAPS for SAP, IOPS for SQL) |
| **Pre-deployment validation** | Validates account quotas, VPC/subnet availability, and IAM permissions before any resources are created |
| **CloudFormation provisioning** | All infrastructure is created via CloudFormation stacks managed by Launch Wizard; stacks are visible in the CloudFormation console |
| **Cost estimation** | Provides an estimated monthly cost for the deployment before provisioning begins |
| **Deployment events** | Timeline of provisioning steps with status and error messages; useful for troubleshooting failed deployments |
| **SSM integration** | Uses AWS Systems Manager (Run Command, Parameter Store) for post-deployment configuration and OS-level setup tasks |

### Deployment Lifecycle

`Configure` (workload inputs + sizing) → `Validate` (pre-deployment checks) → `Provision` (CloudFormation stacks) → `Configure` (SSM post-config) → `Completed` or `Failed`

### Key Constraints

- Launch Wizard manages the CloudFormation stacks it creates; modifying those stacks outside Launch Wizard is not supported
- Deletion of a deployment triggers deletion of the underlying CloudFormation stacks and all provisioned resources
- Supported regions vary by workload; check the Launch Wizard console for regional availability

---

## AWS App Studio

**Purpose**: Generative AI–powered low-code builder for creating internal business applications (forms, dashboards, approval workflows) without writing application code; targets business analysts and citizen developers.

### Core Concepts

| Concept | Description |
|---|---|
| **App** | The top-level container for a business application; has pages, data sources, and automations |
| **Page** | A screen within an app; composed of UI components arranged visually |
| **Component** | A UI element on a page; built-in types: table, form, chart, text, button, and more |
| **Data source** | A connection to a backend: DynamoDB tables, Aurora Serverless (via Data API), or REST APIs |
| **Automation** | Event-driven logic (triggers + actions); e.g., on form submit → write to DynamoDB → send email via SES |
| **Trigger** | The event that starts an automation: button click, form submission, record change, scheduled time |
| **Action** | A step in an automation: query data source, create/update/delete record, invoke API, send notification |
| **AI-generated UI** | Describe an app in natural language; App Studio generates pages and components automatically; refine in the visual editor |
| **Publishing** | Apps are published to a URL accessible to team members; republish to push updates |
| **Access control** | Team members are added via IAM Identity Center; roles control who can build vs. use apps |
| **Connector integration** | Pre-built connectors to AWS services (DynamoDB, S3, SNS) and REST APIs; custom connectors via OpenAPI spec |

### When to Use App Studio vs. Other Low-Code Options

| Tool | Best for |
|---|---|
| **App Studio** | Internal business apps with AWS data sources; citizen developers; no frontend coding |
| **Amplify Studio** | Customer-facing React apps with AWS backend; developers comfortable with React |
| **Honeycode** (discontinued) | Simple spreadsheet-style apps; no longer available |

---

## AWS re:Post Private

**Purpose**: A private, managed Q&A knowledge community platform for enterprises; brings the re:Post model (Stack Overflow-style Q&A with AWS expert content) into a company's own private environment.

### Core Concepts

| Concept | Description |
|---|---|
| **Space** | A private re:Post community instance provisioned for an organization; isolated from the public re:Post site |
| **Question** | A posted inquiry; supports Markdown formatting, code blocks, and tags |
| **Answer** | A response to a question; community members upvote answers; accepted answers are marked as resolved |
| **Official answer** | An answer explicitly marked as authoritative by a space administrator or designated expert |
| **Tag** | A topic label applied to questions; enables filtering and organizing content by service or domain |
| **Badge system** | Reputation badges awarded for community contributions (questions asked, answers given, upvotes received) |
| **Expert network** | Designated subject-matter experts who are notified of questions matching their topics; encouraged to provide official answers |
| **Search** | Full-text search across all questions, answers, and tags within the private space |
| **Content moderation** | Administrators can edit, close, or remove inappropriate or off-topic content |
| **SSO via IAM Identity Center** | Members authenticate through AWS IAM Identity Center; no separate user database required |
| **Metrics dashboard** | Usage analytics: questions asked, answers given, response times, active users, top contributors |
| **Slack / Teams integration** | Notifications for new questions or answers posted to configured Slack channels or Microsoft Teams channels |

### Private vs. Public re:Post

| Dimension | Public re:Post (repost.aws) | re:Post Private |
|---|---|---|
| **Audience** | Open internet; any AWS user | Private to the organization's IAM Identity Center users |
| **Content** | Public AWS Q&A; AWS official answers | Internal company knowledge; internal official answers |
| **Access control** | Public read; account required to post | IAM Identity Center SSO; admin-managed membership |
| **Branding** | AWS branded | Can be customized with company name and logo |
| **Pricing** | Free | Charged per space/member |

### Typical Use Cases

- Internal developer portal for teams working on AWS architectures
- Centralized knowledge base replacing ad hoc Slack channels for technical questions
- Onboarding new engineers with a searchable, moderated answer repository
- Capturing institutional knowledge from internal AWS experts
