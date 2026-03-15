# AWS Compute Optimizer — Capabilities Reference
For CLI commands, see [compute-optimizer-cli.md](compute-optimizer-cli.md).

## Right-Sizing and Compute Optimizer

**Purpose**: Identify over-provisioned, under-provisioned, and idle compute resources and receive specific recommendations for right-sized alternatives to reduce cost without sacrificing performance.

### AWS Compute Optimizer

**Supported Resource Types**

| Resource | Recommendations Provided |
|---|---|
| **EC2 instances** | Right-size to optimal instance type/size; migrate to Graviton |
| **EC2 Auto Scaling groups** | Optimal instance configuration for the group |
| **EBS volumes** | Right-size volume type and IOPS |
| **AWS Lambda functions** | Optimal memory configuration |
| **ECS services on Fargate** | Optimal CPU/memory configuration for tasks |
| **Amazon RDS / Aurora** | Instance right-sizing (newer feature) |
| **Commercial software licenses** | SQL Server license right-sizing |

**Finding Types**

| Finding | Meaning |
|---|---|
| **Over-provisioned** | Resource has more capacity than needed; can be downsized |
| **Under-provisioned** | Resource is constrained; may need upsizing for performance |
| **Optimized** | Resource is appropriately sized |
| **Insufficient data** | Not enough CloudWatch metrics yet (requires ~14 days) |

**Key Features**

- **Default lookback period**: 14 days of CloudWatch metrics
- **Enhanced Infrastructure Metrics** (paid add-on): extends lookback to 93 days for more accurate recommendations
- **External Metrics Ingestion**: integrate Datadog or Dynatrace metrics for better EC2 recommendations
- **Graviton migration recommendations**: identifies EC2 instances that can migrate to ARM-based Graviton for additional savings (typically 20% lower cost vs. comparable x86)
- **Export recommendations**: CSV export for tracking, prioritization, and sharing
- **Multi-account**: Delegated administrator can aggregate recommendations across an AWS Organization

### Right-Sizing in Cost Explorer

- **Right-sizing recommendations** tab shows EC2 instances that can be downsized or terminated
- Incorporates Reserved Instance and Savings Plans pricing into savings estimates
- Integrates with Compute Optimizer for consistent recommendation data

### Decision Guidance

- Use Compute Optimizer for deep per-resource analysis and Graviton recommendations
- Use Cost Explorer right-sizing for a quick high-level view with RI/SP-adjusted savings estimates
- Prioritize over-provisioned instances with the highest estimated monthly savings first
