# AWS Cost Explorer & Budgets — Capabilities Reference
For CLI commands, see [cost-explorer-budgets-cli.md](cost-explorer-budgets-cli.md).

## Amazon Cost Explorer

**Purpose**: Visualize, analyze, and forecast AWS cost and usage with up to 13 months of historical data and 18-month forecasts. Accessible via console (free) or API ($0.01 per paginated API request).

### Filters and Dimensions

| Dimension | Examples |
|---|---|
| **Service** | Amazon EC2, Amazon S3, AWS Lambda |
| **Region** | us-east-1, eu-west-1 |
| **Linked account** | Filter to specific member accounts |
| **Usage type** | BoxUsage:t3.medium, DataTransfer-Out |
| **Tag** | Environment=prod, Team=platform |
| **Cost category** | Custom cost groupings defined in Cost Categories |
| **Purchase option** | On-Demand, Reserved, Spot, Savings Plans |

### Time Granularity

| Granularity | Details |
|---|---|
| **Monthly** | Default; up to 13 months of history |
| **Daily** | Drill into day-level trends |
| **Hourly** | Granular analysis; requires enabling hourly granularity in Cost Management preferences |

### Key Reports

| Report | Purpose |
|---|---|
| **Cost and usage** | Core report; filter/group by any dimension |
| **RI coverage** | % of eligible instance hours covered by Reserved Instances |
| **RI utilization** | % of RI commitment actually consumed |
| **Savings Plans coverage** | % of eligible spend covered by Savings Plans |
| **Savings Plans utilization** | % of Savings Plans commitment consumed |
| **Right-sizing recommendations** | EC2 instances eligible for downsizing or termination |
| **RI purchase recommendations** | Optimal RI purchases based on historical usage |
| **Savings Plans purchase recommendations** | Optimal $/hr commitment based on usage patterns |

### Forecasting

- Projects future spend up to **18 months** based on historical trends
- Available at monthly granularity; uses ML model
- Can forecast at account, service, or tag level
- Forecasts are estimates; accuracy improves with longer history

### Cost Anomaly Detection Integration

- Cost Explorer links anomalies to their time series for root cause investigation

### API Access

- Full programmatic access to all Cost Explorer data via `aws ce` CLI namespace
- Endpoint is always `ce.us-east-1.amazonaws.com` regardless of where resources run
- Once enabled, Cost Explorer API cannot be disabled

---

## AWS Budgets

**Purpose**: Set custom cost or usage thresholds and receive alerts (or trigger automated actions) when actual or forecasted spending approaches or exceeds them. Updated up to 3 times daily.

### Budget Types

| Type | What it tracks |
|---|---|
| **Cost budget** | Dollar amount of AWS spend |
| **Usage budget** | Quantity of a specific usage type (e.g., EC2 instance-hours) |
| **RI utilization budget** | % of Reserved Instance commitment consumed; alert when too low |
| **RI coverage budget** | % of instance hours covered by RIs; alert when coverage drops |
| **Savings Plans utilization budget** | % of Savings Plans commitment consumed; alert when too low |
| **Savings Plans coverage budget** | % of eligible spend covered by Savings Plans; alert when coverage drops |

### Alert Types

| Alert Type | When it fires |
|---|---|
| **Actual** | After costs/usage are already incurred and threshold is exceeded |
| **Forecasted** | Before costs/usage are accrued, based on current spending trajectory |

### Notification Channels

- Amazon SNS topics (supports Slack/Chime via SNS integrations)
- Email addresses (up to 10 per notification)
- Both can be configured simultaneously

### Budget Actions

Automatically triggered when a budget threshold is breached:

| Action Type | What it does |
|---|---|
| **Apply IAM policy** | Attaches a deny policy to users/roles to block further provisioning |
| **Apply SCP** | Attaches an SCP to an OU or account to enforce org-wide restrictions |
| **Stop EC2/RDS instances** | Stops running EC2 or RDS instances in the account |

Actions can be set to trigger automatically or require manual approval. Actions can also be manually executed via console or CLI.

### Budget Reports

- Scheduled PDF/CSV reports sent via email on a cadence (daily, weekly, monthly)
- Report a subset of budgets per report; up to 50 budgets per report
- Sent via Amazon SNS or directly to email

---

## AWS Cost Anomaly Detection

**Purpose**: Automatically detect unusual spending patterns using machine learning; alert via email or SNS before costs spiral. Requires at least one cost monitor and at least one alert subscription.

### Monitor Types

| Dimension | AWS Managed | Customer Managed |
|---|---|---|
| **AWS services** | Auto-tracks all services; new services included automatically | N/A |
| **Linked accounts** | Tracks all member accounts automatically (mgmt account only) | Up to 10 specific accounts |
| **Cost allocation tags** | Tracks all values for a tag key automatically | Up to 10 specific tag values |
| **Cost categories** | Tracks all values in a cost category | Up to 1 specific cost category value |

- **AWS Managed monitors** track up to 5,000 values; apply same threshold across all tracked values
- **Customer Managed monitors** allow different thresholds per value; max 10 values per monitor

### Alert Subscriptions

| Frequency | Details |
|---|---|
| **Individual alerts** | Immediate notification upon anomaly detection; requires SNS topic; multiple per day possible |
| **Daily summaries** | Email at 00:00 UTC; top 10 anomalies by cost impact from the previous day |
| **Weekly summaries** | One email per week covering all anomalies from that week |

### Threshold Configuration

- **Absolute threshold**: Alert when total cost impact exceeds a dollar amount (e.g., $500)
- **Percentage threshold**: Alert when impact % exceeds a value — formula: `(actual - expected) / expected × 100`
- Multiple thresholds can be combined with AND/OR logic

### Root Cause Analysis

Each detected anomaly surfaces:
- Service, linked account, region, and usage type contributing most to the anomaly
- Expected spend (ML baseline) vs. actual spend
- Cost impact ($) and impact percentage
- Severity assessment (Low/High based on historical pattern consistency)

---

## AWS Cost Optimization Hub

**Purpose**: Single dashboard consolidating cost optimization recommendations across your AWS organization — rightsizing, Savings Plans, Reserved Instances, and idle/unused resources — with estimated after-discount savings.

### Recommendation Categories

| Category | Examples |
|---|---|
| **Resource rightsizing** | EC2 instances, ECS tasks, Lambda memory, EBS volumes, Auto Scaling groups |
| **Idle resource deletion** | Underutilized EC2, unattached EBS volumes, idle NAT Gateways |
| **Savings Plans** | Compute Savings Plans, EC2 Instance Savings Plans, SageMaker Savings Plans |
| **Reserved Instances** | EC2, RDS, OpenSearch, Redshift, ElastiCache, MemoryDB, DynamoDB reserved capacity |

### Supported Resource Types

20+ resource types including: EC2, Auto Scaling groups, EBS volumes, Lambda, ECS on Fargate, RDS instances and storage, Aurora cluster storage, NAT Gateways.

### Key Features

| Feature | Details |
|---|---|
| **After-discount savings** | Estimates incorporate your specific pricing, discounts, and existing commitments |
| **Deduplication** | Avoids double-counting savings from multiple recommendations on the same resource |
| **Filtering and sorting** | Filter by resource type, account, region, recommendation type, and savings amount |
| **Multi-account support** | Enable from management account to aggregate across the organization |
| **API access** | Programmatic access via AWS Billing and Cost Management API |

### Decision Guidance

- Use Cost Optimization Hub as the starting point for identifying where the largest savings opportunities exist
- Drill into Compute Optimizer for detailed per-resource rightsizing analysis
- Drill into Cost Explorer for RI/SP coverage and utilization reporting

---

## Cost Optimization Quick Wins

A prioritized summary of the highest-impact cost reduction levers.

| Optimization Lever | Typical Savings | How | Effort |
|---|---|---|---|
| **Right-size EC2 instances** | 20–40% of EC2 spend | Use Compute Optimizer findings; downsize over-provisioned instances | Medium |
| **Purchase Savings Plans** | 30–66% vs. On-Demand | Commit baseline compute usage to Compute Savings Plans | Low |
| **Use Spot Instances** | 60–90% vs. On-Demand | Migrate batch, CI/CD, stateless workloads to Spot | Medium |
| **Delete idle/unused resources** | Varies | Terminate stopped instances, unattached EBS volumes, idle load balancers, unused Elastic IPs | Low |
| **S3 lifecycle policies** | 30–70% of S3 storage | Move infrequently accessed data to S3-IA or Glacier tiers automatically | Low |
| **Purchase Reserved Instances** | 30–72% vs. On-Demand | For stable, predictable non-EC2 workloads (RDS, Redshift, ElastiCache) | Low |
| **Migrate to Graviton** | ~20% vs. x86 equivalent | Follow Compute Optimizer Graviton recommendations | Medium |
| **Enable Cost Anomaly Detection** | Prevent unexpected spend | Create service and linked-account monitors with alert subscriptions | Very Low |
| **Implement mandatory tagging** | Indirectly reduces waste | Tag enforcement enables accountability; reduces orphaned resources | Medium |
| **Review data transfer costs** | 10–30% of networking | Move cross-AZ traffic to same-AZ; use VPC endpoints; enable S3 Transfer Acceleration only where needed | High |
