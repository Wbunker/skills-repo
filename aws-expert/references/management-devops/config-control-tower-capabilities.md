# AWS Config / Control Tower — Capabilities Reference

For CLI commands, see [config-control-tower-cli.md](config-control-tower-cli.md).

## AWS Config

**Purpose**: Continuous recording and evaluation of AWS resource configurations; enables compliance auditing, change tracking, and security analysis.

### Core Concepts

| Concept | Description |
|---|---|
| **Configuration recorder** | Records configuration changes for specified resource types; one per account per region |
| **Configuration item (CI)** | Point-in-time snapshot of a resource's configuration, relationships, and metadata |
| **Configuration history** | All CIs for a resource over time; queryable via API; delivered to S3 |
| **Configuration snapshot** | Complete dump of all recorded resources at a point in time; delivered to S3 |
| **Config rule** | Evaluates resource configurations against desired state; returns COMPLIANT or NON_COMPLIANT |
| **Conformance pack** | Collection of Config rules and remediation actions deployed as a single entity from a YAML template |
| **Aggregator** | Collects Config data from multiple accounts and/or regions into a single account |
| **Remediation action** | SSM Automation document triggered on non-compliance; manual (wait for approval) or automatic |
| **Resource relationships** | Config maps relationships between resources (e.g., EC2 instance → security group → VPC) |
| **Advanced query** | SQL-like queries against current resource configuration state using the Config Query Language |

### Config Rule Types

| Type | Description |
|---|---|
| **AWS managed rules** | Pre-built rules maintained by AWS (e.g., `s3-bucket-public-read-prohibited`, `encrypted-volumes`) |
| **Custom Lambda rules** | Lambda function evaluates resources; triggered by configuration change or on a schedule |
| **Custom Guard rules** | Use CloudFormation Guard (cfn-guard) DSL for policy-as-code evaluation |
| **Proactive rules** | Evaluate resources **before** they are created, using the CloudFormation hook integration |

### Evaluation Trigger Types

| Trigger | When it runs |
|---|---|
| **Configuration change** | Fires when a matching resource type changes |
| **Periodic** | Runs on a schedule (1h, 3h, 6h, 12h, 24h) regardless of changes |
| **Hybrid** | Both configuration change and periodic |

### Key Patterns

- **Conformance packs** for CIS Benchmark, PCI DSS, HIPAA, NIST — deploy the entire control set at once
- **Aggregator + Organizations** — see compliance posture across all accounts in a single dashboard
- **Automatic remediation** — chain Config rule → SSM Automation to auto-fix non-compliant resources (e.g., enable S3 versioning)
- **Config + Security Hub** — Config findings surfaced in Security Hub for centralized security posture

---

## AWS Control Tower

**Purpose**: Automated, opinionated setup and governance for a multi-account AWS environment based on AWS best practices.

### Core Concepts

| Concept | Description |
|---|---|
| **Landing zone** | A well-architected, multi-account AWS environment; the overall Control Tower setup |
| **Organizational unit (OU)** | Hierarchical grouping of accounts; Control Tower pre-creates Security and Sandbox OUs |
| **Control (guardrail)** | A policy rule applied to an OU; expressed in plain English; implemented as an SCP or Config rule |
| **Account Factory** | Service Catalog-backed mechanism for vending new AWS accounts with standard configurations |
| **Enrollment** | Bringing an existing AWS account under Control Tower governance |

### Pre-configured OUs

| OU | Purpose |
|---|---|
| **Security** | Contains the Log Archive account (centralized CloudTrail/Config logs) and Audit account (cross-account read access) |
| **Sandbox** | For experimentation; less restrictive guardrails |
| **Custom OUs** | Created by you to mirror organizational structure (e.g., Workloads, Infrastructure) |

### Control Types

| Type | Implementation | When it fires |
|---|---|---|
| **Preventive** | Service Control Policy (SCP) | Before an action; denies non-compliant API calls |
| **Detective** | AWS Config rule | After the fact; identifies non-compliant resource configurations |
| **Proactive** | CloudFormation hook | Before resource provisioning; blocks non-compliant stacks |

### Control Guidance Levels

| Level | Description |
|---|---|
| **Mandatory** | Always enabled; cannot be disabled |
| **Strongly recommended** | Best practices; AWS recommends enabling but not required |
| **Elective** | Optional; for specific use cases or regulatory requirements |

### Account Factory and Extensions

| Feature | Description |
|---|---|
| **Account Factory** | Self-service provisioning of new accounts via Service Catalog; applies baseline configuration via customization |
| **Account Factory for Terraform (AFT)** | IaC-driven account vending using Terraform; git-based workflow triggers account provisioning pipeline |
| **CfCT (Customizations for Control Tower)** | Deploy additional CloudFormation StackSets and SCPs alongside Control Tower; pipeline triggered from a config manifest |
| **Enroll existing accounts** | Bring accounts already in the Organization under Control Tower governance; applies baseline controls |
