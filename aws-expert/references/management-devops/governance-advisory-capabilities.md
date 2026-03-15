# Governance & Advisory Tools — Capabilities Reference

For CLI commands, see [governance-advisory-cli.md](governance-advisory-cli.md).

## AWS Service Catalog

**Purpose**: Create and manage catalogs of approved IT services that end users can self-provision, enabling governance and standardization without requiring direct AWS service access.

### Core Concepts

| Concept | Description |
|---|---|
| **Portfolio** | A collection of approved products; access is granted to IAM users, groups, or roles per portfolio |
| **Product** | An approved IT service backed by a CloudFormation template (or Terraform/CDK); versioned via provisioning artifacts |
| **Provisioning artifact** | A specific version of a product's template; users can be constrained to specific versions |
| **Provisioned product** | A running instance of a launched product; tracked lifecycle (available, under change, tainted, error) |
| **Constraint** | Rules applied to a product within a portfolio at provisioning time |
| **TagOption** | Reusable key/value tag pairs associated with portfolios or products; enforced during provisioning |
| **Service action** | A predefined SSM Automation document end users can execute on their provisioned products (e.g., restart, resize) |

### Constraint Types

| Type | Description |
|---|---|
| **Launch constraint** | IAM role that Service Catalog assumes when launching the product; grants least-privilege provisioning without giving users direct CloudFormation permissions |
| **Notification constraint** | SNS topic to receive stack events for a product |
| **StackSet constraint** | Deploys product across multiple accounts/regions via CloudFormation StackSets |
| **Resource update constraint** | Controls whether end users can update tags on provisioned product resources |

### Portfolio Sharing

| Method | Description |
|---|---|
| **Account sharing** | Share a portfolio with a specific AWS account; recipient account must accept and then grant access |
| **AWS Organizations sharing** | Share with an OU or the entire organization; auto-accept can be enabled for member accounts |
| **Import** | Recipient account imports shared portfolio to make products available locally |

### Key Patterns

- **Launch constraints + least privilege** — product admin creates a launch role with only the permissions needed to provision; end users get self-service without broad IAM permissions
- **Account Factory integration** — Control Tower's Account Factory is built on Service Catalog; used to vend new accounts with standard products
- **Version-pinning** — use provisioning artifact constraints to prevent end users from launching deprecated versions
- **TagOptions** — attach mandatory tags (e.g., `CostCenter`, `Environment`) to enforce tagging policy at provisioning time

---

## AWS Trusted Advisor

**Purpose**: Automated best-practice inspection service that provides real-time recommendations across cost optimization, performance, security, fault tolerance, and service quotas.

### Core Concepts

| Concept | Description |
|---|---|
| **Check** | An individual inspection against a specific best practice; returns status (OK, Warning, Error, Not Available) and affected resources |
| **Check category** | One of five pillars: Cost Optimization, Performance, Security, Fault Tolerance, Service Limits |
| **Recommendation** | Aggregated result of one or more checks with actionable guidance |
| **Lifecycle status** | Current state of a recommendation: `pending_response`, `in_progress`, `dismissed`, `resolved` |
| **Trusted Advisor Priority** | Curated high-priority recommendations surfaced by AWS experts and automated reasoning (Business Support+ and Enterprise) |
| **Organizational view** | Aggregated recommendations across all accounts in an AWS Organization |

### Support Plan Access

| Support Plan | Access |
|---|---|
| **Basic / Developer** | Service Limits category + selected Security and Fault Tolerance checks; manual refresh only |
| **Business Support+** | All checks with automatic refresh; Trusted Advisor API; EventBridge integration |
| **Enterprise** | All checks + Trusted Advisor Priority + dedicated TAM guidance |

### Check Categories

| Category | Examples |
|---|---|
| **Cost Optimization** | Idle EC2 instances, underutilized EBS volumes, unassociated Elastic IPs, Reserved Instance recommendations |
| **Performance** | EC2 instance type optimization, CloudFront content delivery optimization, high-utilization EC2 |
| **Security** | S3 bucket permissions, security groups with unrestricted access, MFA on root, IAM use |
| **Fault Tolerance** | EBS snapshots, RDS Multi-AZ, EC2 availability zone balance, Auto Scaling group health |
| **Service Limits** | Checks approaching or at service quota limits across 50+ services |

### Key Patterns

- **EventBridge integration** — route Trusted Advisor check status change events to SNS/Lambda for automated remediation workflows
- **Organizational view** — enable in the management account to see recommendations aggregated across all member accounts without switching accounts
- **Lifecycle tracking** — use `update-recommendation-lifecycle` to track remediation progress; mark items `in_progress` or `resolved` for accountability
- **Config-powered checks** — some Trusted Advisor security checks are powered by AWS Config rules; enabling Config improves coverage

---

## AWS Health Dashboard

**Purpose**: Provides personalized, real-time visibility into the health of AWS services and resources, surfacing events that may affect your specific workloads.

### Core Concepts

| Concept | Description |
|---|---|
| **Service Health Dashboard** | Public status page showing general AWS service availability across regions; no account context |
| **Personal Health Dashboard** | Account-specific view of events that affect your resources or account; requires authentication |
| **Health event** | A notification about a change in availability or health of an AWS service or resource |
| **Affected entity** | A specific AWS resource (e.g., EC2 instance ID, RDS cluster ARN) impacted by an event |
| **Event type** | Classifies events by service, category, and type code (e.g., `AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED`) |
| **Organizational view** | See Health events across all accounts in an AWS Organization from the management account |

### Event Categories

| Category | Description |
|---|---|
| **Issue** | Degradation or outage currently affecting AWS infrastructure |
| **Scheduled Change** | Planned maintenance that may require action (e.g., instance retirement, certificate rotation) |
| **Account Notification** | Billing, security, or compliance notices specific to your account |

### Health API vs Dashboard

| Feature | Requires |
|---|---|
| Console Personal Health Dashboard | Any AWS account (free) |
| AWS Health API | Business, Enterprise On-Ramp, or Enterprise Support plan |
| EventBridge integration | Any AWS account (free) |
| Organizational view | Business+ support; Organizations enabled |

### Key Patterns

- **EventBridge automation** — subscribe to `aws.health` events in EventBridge to trigger Lambda for automated incident response (e.g., open PagerDuty ticket, notify Slack)
- **Scheduled change preparation** — poll `describe-events` with category filter `scheduledChange` to pre-emptively remediate before maintenance windows
- **Multi-account visibility** — enable organizational view in the management account; use `describe-events-for-organization` to aggregate events across all accounts
- **Event filtering** — filter by service, region, event status (`open`, `closed`, `upcoming`), and entity ARN to scope notifications to relevant workloads

---

## AWS License Manager

**Purpose**: Centralized software license tracking and governance across AWS and on-premises infrastructure, supporting BYOL, seller-issued licenses, and Marketplace/Data Exchange entitlements.

### Core Concepts

| Concept | Description |
|---|---|
| **License configuration** | Rules defining how a license should be counted (vCPUs, cores, sockets, instances); attached to AMIs, launch templates, or resource groups |
| **License rule** | Hard limit (blocks launch when exceeded) or soft limit (alerts when exceeded) on license consumption |
| **Managed entitlement** | A cryptographically verified license issued by an ISV; supports perpetual, floating, subscription, usage-based, and node-locked models |
| **Grant** | Delegates use rights of a managed entitlement to another AWS account |
| **Checkout/check-in** | Application-level API calls to consume and release floating license entitlements at runtime |
| **License type conversion** | Switch EC2 instances between AWS-provided (License Included) and BYOL without redeployment |
| **User-based subscription** | Per-user subscription model for supported software (e.g., Visual Studio); centrally managed per-user allocation |

### License Tracking Dimensions

| Dimension | Use case |
|---|---|
| **vCPUs** | Microsoft SQL Server, Oracle Database on virtualized infrastructure |
| **Physical cores** | Software requiring core-based licensing |
| **Sockets** | Processors/sockets for server software |
| **Instances** | Per-machine licensing |

### Key Patterns

- **AMI association** — attach a license configuration to an AMI; every EC2 instance launched from that AMI automatically consumes a license count
- **Hard limits** — set hard limits on license configurations to prevent over-licensing; instances exceeding the limit cannot launch
- **BYOL on Dedicated Hosts** — License Manager allocates Dedicated Hosts and tracks host-level licenses for SQL Server and Windows Server
- **License type conversion** — use `create-license-conversion-task` to convert running instances between License Included and BYOL without downtime
- **Cross-account grants** — management account creates a managed license and distributes grants to member accounts; member accounts must accept grants before use
- **Inventory discovery** — integrates with Systems Manager Inventory to discover on-premises license consumption alongside AWS resources

---

## AWS Resource Explorer

**Purpose**: Search and discover AWS resources across accounts and regions from a single interface, without needing to know which region a resource is in.

### Core Concepts

| Concept | Description |
|---|---|
| **Index** | A per-region database of resource metadata; must be created in each region you want to search |
| **Local index** | Stores resource data for a single region; enables region-scoped search only |
| **Aggregator index** | A single designated index (one per account) that replicates data from all local indexes; enables cross-region search |
| **View** | A filter applied to search results; controls which resource types and tags are returned; can be shared with IAM principals |
| **Default view** | The view used for searches when no view ARN is explicitly specified; also powers the Console unified search bar |
| **Multi-account search** | Aggregator index in a management account replicates from member account indexes; requires Organizations |

### Index Types Compared

| Feature | Local Index | Aggregator Index |
|---|---|---|
| Cross-region search | No | Yes |
| Multi-account search | No | Yes (with Organizations) |
| Count per account | One per region | One per account total |
| Replication lag | N/A | Up to 1 hour on initial sync |

### Search Query Syntax

Resource Explorer supports a structured query syntax:

| Syntax | Example |
|---|---|
| Free text | `my-bucket-name` |
| Property filter | `resourcetype:AWS::S3::Bucket` |
| Tag filter | `tag.Env=prod` |
| Region filter | `region:us-east-1` |
| Combined | `resourcetype:AWS::EC2::Instance tag.Env=prod region:us-east-1` |

### Key Patterns

- **Aggregator + Organizations** — deploy aggregator index in the management account and local indexes in every region/account; enables true org-wide resource inventory
- **Tagging compliance** — use Resource Explorer to identify resources missing required tags by searching for `NOT tag.CostCenter=*`
- **Console search integration** — associating a default view in each region enhances the AWS Console search bar to show resources in addition to service pages
- **Automation** — use `search` API in CI/CD pipelines or Lambda to dynamically discover resource ARNs without hardcoding

---

## AWS Well-Architected Tool

**Purpose**: Structured framework for reviewing workload architectures against AWS best practices across six pillars; produces prioritized improvement plans.

### Core Concepts

| Concept | Description |
|---|---|
| **Workload** | The system or application being reviewed; scoped by accounts, regions, and architectural description |
| **Lens** | A set of questions and best practices applied to a workload review; defines the review framework |
| **Pillar** | One of the six Well-Architected Framework pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability |
| **Answer** | A response to a specific lens question; each answer includes selected best practices and a notes field |
| **High-risk issue (HRI)** | A best practice that is not followed and is flagged as high impact; displayed prominently in the report |
| **Medium-risk issue (MRI)** | A best practice not followed with moderate impact |
| **Milestone** | A saved snapshot of a workload review at a point in time; used to track improvement over time |
| **Improvement plan** | Prioritized list of HRIs and MRIs with links to guidance; exported as PDF or viewed in console |

### Available Lenses

| Lens | Focus |
|---|---|
| **AWS Well-Architected Framework** | Core six-pillar review; applies to all workloads |
| **Serverless Application Lens** | Specific guidance for Lambda, API Gateway, DynamoDB workloads |
| **SaaS Lens** | Multi-tenancy, tenant isolation, onboarding, metering |
| **Machine Learning Lens** | Data preparation, model training, deployment, monitoring |
| **Financial Services Lens** | Regulatory compliance, data security for financial workloads |
| **Custom lens** | Organization-defined questions and best practices; imported via JSON |

### Key Patterns

- **Milestone tracking** — create a milestone before starting remediation work and another after; compare milestone summaries to quantify risk reduction
- **Custom lenses** — encode internal architecture standards as a custom lens JSON; distribute to teams via `import-lens` + `associate-lenses` for consistent internal reviews
- **Shared reviews** — share a workload with other IAM principals (read-only or contributor) for collaborative multi-team reviews
- **Service Catalog AppRegistry integration** — link Well-Architected workloads to AppRegistry application metadata for unified application governance
- **Consolidated report** — use `get-consolidated-report` to produce an account-wide summary PDF of all workload risk profiles

### CDK / SDK Integration

```typescript
// Programmatically create a workload and associate lenses
import { WellArchitectedClient, CreateWorkloadCommand } from "@aws-sdk/client-wellarchitected";

const client = new WellArchitectedClient({ region: "us-east-1" });

await client.send(new CreateWorkloadCommand({
  WorkloadName: "my-ecommerce-platform",
  Description: "Primary e-commerce platform review",
  Environment: "PRODUCTION",
  ReviewOwner: "platform-team@example.com",
  Lenses: ["wellarchitected", "serverless"],
  AccountIds: ["123456789012"],
  AwsRegions: ["us-east-1", "eu-west-1"],
}));
```
