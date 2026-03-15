# AWS CUR & Billing — Capabilities Reference
For CLI commands, see [cur-billing-cli.md](cur-billing-cli.md).

## Cost and Usage Report (CUR)

**Purpose**: The most comprehensive AWS cost and usage data available. Delivers detailed billing line items to an S3 bucket in CSV format, updated at least once daily. Foundation for custom cost analytics, FinOps tooling, and showback/chargeback workflows.

### Report Contents

| Column Category | What it contains |
|---|---|
| **identity/** | Line item ID, billing entity |
| **bill/** | Invoice ID, billing period, bill type, payer account |
| **lineItem/** | Line item type, usage start/end, product code, usage amount, unblended/blended cost |
| **pricing/** | Rate code, public on-demand rate, currency |
| **reservation/** | RI ARN, effective cost, amortized upfront/recurring fees |
| **savingsPlan/** | Savings Plan ARN, rate, effective cost (present only if SPs used) |
| **product/** | Service-specific attributes (instance type, region, OS, etc.) |
| **resourceTags/** | User-defined and AWS-generated tags activated for cost allocation |
| **costCategory/** | Values for any configured Cost Categories |

### Delivery Options

| Option | Details |
|---|---|
| **S3 delivery** | Reports written to a customer-specified S3 bucket |
| **Compression** | GZIP or ZIP |
| **Update frequency** | At least once daily; up to 3 times daily; finalized after month-end invoice |
| **Versioning** | Choose to overwrite existing files or create new report versions each update |
| **Aggregation** | Hourly, daily, or monthly line items |

### Integration

| Tool | How it integrates |
|---|---|
| **Amazon Athena** | Partition the S3 data; query with SQL; native Athena integration creates table/views automatically |
| **Amazon QuickSight** | Upload or link from S3 for interactive dashboards |
| **Amazon Redshift** | Load CUR data into Redshift for complex analytics |
| **Third-party tools** | CloudHealth, Apptio, Spot.io, etc. all ingest CUR |

### CUR 2.0 / Data Exports

- **CUR 2.0** (via AWS Data Exports): New format with improved column naming, additional columns, and parquet support
- **Legacy CUR** remains supported but new features are added to CUR 2.0
- Data Exports also supports **FOCUS** (FinOps Open Cost and Usage Specification) format for multi-cloud cost data standardization

---

## AWS Billing Conductor

**Purpose**: Create custom billing rates and pricing for AWS accounts — primarily used by ISVs, MSPs, and internal chargebacks to show customers or business units custom (proforma) pricing while the management account reconciles actual AWS costs separately.

### Key Concepts

| Concept | Description |
|---|---|
| **Billing group** | A set of accounts that share a pricing plan; receives a custom proforma invoice |
| **Pricing plan** | Collection of pricing rules applied to a billing group |
| **Pricing rule** | Define a markup, markdown, or tiering override on a service, usage type, or global scope |
| **Custom line item** | Add flat fees or credits to a billing group's bill (e.g., support fee, discount credit) |
| **Proforma billing** | The custom view of the bill shown to the billing group |
| **Actual billing** | The real AWS bill seen only by the management/payer account |

### Pricing Rule Types

| Rule Type | Use Case |
|---|---|
| **Markup** | Add percentage above AWS rates (e.g., show customers +15% over On-Demand) |
| **Markdown** | Pass discounts to customers (e.g., reflect negotiated EDP discount in proforma bill) |
| **Tiering** | Apply volume-based pricing tiers |

### Key Features

- **Associate/disassociate accounts**: Move accounts between billing groups without affecting actual billing
- **Cost reports per billing group**: View proforma costs per group for invoicing or chargeback
- **Integration with Cost Explorer**: Proforma billing data visible in Cost Explorer for associated accounts
- **Supports all AWS services**: Pricing rules can target specific services, usage types, or apply globally

### Use Cases

- **MSPs**: Bill customers at marked-up rates while retaining volume discount benefits on the actual AWS bill
- **ISVs**: Show SaaS customers their AWS consumption costs at agreed-upon rates
- **Internal chargeback**: Assign standardized rates per department regardless of actual negotiated discounts

---

## Cost Categories

Cost Categories allow you to map your AWS costs and usage into meaningful business categories.

- Defined via rules in the Cost Explorer console or `aws ce create-cost-category-definition`
- Rules can match on service, linked account, tag values, or other dimensions
- Appear as a filterable dimension in Cost Explorer and as columns in CUR (`costCategory/` prefix)
- Useful for showback/chargeback: group costs by team, environment, product line, etc.

---

## AWS Pricing Calculator

**Purpose**: Estimate the monthly cost of a planned AWS architecture before deployment. Accessible at calculator.aws.amazon.com (no AWS account required).

### Key Capabilities

| Feature | Details |
|---|---|
| **Service coverage** | Supports 100+ AWS services with configuration-level pricing |
| **Estimate groups** | Organize resources by group (e.g., "frontend", "database", "networking") |
| **Pricing options** | Compare On-Demand, Reserved Instances, Savings Plans pricing side-by-side |
| **Region selection** | Estimate per-region pricing to optimize placement |
| **Export** | Export estimate to CSV or shareable URL |
| **In-console calculator** | Available in Cost Management console for estimates using your actual negotiated rates and existing commitments |

### Decision Guidance

- Use the **public Pricing Calculator** for architecture planning before an account exists or for sharing estimates with stakeholders
- Use the **in-console Pricing Calculator** for estimates that reflect your actual discount rates, existing RIs, and Savings Plans

---

## Pricing API

**Purpose**: Programmatic access to AWS public pricing data. Used for building cost estimation tools, pre-deployment cost checks, and automated pricing lookups.

- Endpoint: `https://api.pricing.us-east-1.amazonaws.com` (also available in `ap-south-1`)
- Returns pricing in JSON format with full SKU-level detail
- Supports filtering by service attributes (instance type, region, OS, etc.)
- Supports bulk price list file downloads for offline analysis
