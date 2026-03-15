# AWS Tagging Strategy — Capabilities Reference
For CLI commands, see [tagging-strategy-cli.md](tagging-strategy-cli.md).

## Cost Allocation Tags

**Purpose**: Label AWS resources with key-value tags that, once activated for billing, appear as columns in Cost Explorer and CUR reports — enabling cost visibility by team, environment, project, or any business dimension.

### Tag Types

| Type | Prefix | Who creates | Examples |
|---|---|---|---|
| **AWS-generated** | `aws:` | AWS or AWS Marketplace ISVs | `aws:createdBy` (tracks which principal created the resource) |
| **User-defined** | `user:` | You | `user:Environment`, `user:CostCenter` |

### Activation

- Tags must be **explicitly activated** in the Billing and Cost Management console before they appear in reports
- Activation can take up to **24 hours** to propagate
- Only management accounts (in an org) or standalone accounts can manage cost allocation tags
- Activated tags apply retroactively to historical data in CUR/Cost Explorer

### Key Features

| Feature | Details |
|---|---|
| **Tag Editor** | Console tool for viewing and managing tags across all resources and regions |
| **Tag policies (Organizations)** | Enforce tag key capitalization and value constraints across accounts; non-compliant resources flagged |
| **AWS Config rules** | `required-tags` rule detects resources missing mandatory tags |
| **Backfill** | Can backfill cost allocation tags to apply them retroactively to past CUR data |
| **Tag compliance report** | Generate compliance reports via `aws resourcegroupstaggingapi start-report-creation` |

### Governance

- Activated tags appear as filterable dimensions in Cost Explorer and as columns in CUR
- Untagged resources still appear in reports as a separate row (tagged: empty value)
- Best practice: keep tag values consistent in format (e.g., always lowercase for environment values)

---

## Tagging Strategy

**Purpose**: A consistent, enforced tagging taxonomy is the foundation of cost allocation, showback/chargeback, and resource governance.

### Recommended Mandatory Tags

| Tag Key | Purpose | Example Values |
|---|---|---|
| `Environment` | Distinguish prod/non-prod for cost separation | `prod`, `staging`, `dev`, `sandbox` |
| `Owner` | Identify responsible team or individual | `platform-team`, `alice@example.com` |
| `CostCenter` | Map to finance/chargeback codes | `CC-1234`, `engineering` |
| `Project` | Associate with business initiative | `checkout-redesign`, `data-platform` |
| `Application` | Associate with application or service name | `payments-api`, `recommendation-engine` |

### Tag Automation Methods

| Method | How it works |
|---|---|
| **CloudFormation / CDK** | Define tags on stack; propagated to all created resources |
| **Tag policies (Organizations)** | Enforce key/value standards across accounts; flagged in compliance reports |
| **AWS Config `required-tags` rule** | Detect resources missing mandatory tag keys; trigger auto-remediation via SSM |
| **Resource Groups Tagging API** | Bulk-tag resources across services and regions |
| **Launch templates / AMI tags** | Pre-tag EC2 instances at launch |
| **IAM condition: `aws:RequestTag`** | Require tags at resource creation time via IAM deny policy |

### Enforcement Pattern (Deny without Tags)

```json
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Resource": "arn:aws:ec2:*:*:instance/*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestTag/Environment": ["prod", "staging", "dev", "sandbox"]
    }
  }
}
```
