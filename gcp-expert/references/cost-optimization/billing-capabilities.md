# GCP Billing & Budgets — Capabilities

## Billing Account

A **Cloud Billing Account** is the financial entity that pays for GCP resource usage. Key characteristics:

- **Linking**: each GCP project must be linked to exactly one billing account; one billing account can pay for many projects
- **Hierarchy**: billing accounts belong to an organization (for enterprise) or a standalone Google account (self-serve)
- **Payment types**:
  - **Self-serve (online)**: credit card or bank account; automatic monthly charge
  - **Invoiced (monthly invoice)**: for enterprises meeting spend thresholds; payment via check/wire; Net 30 terms
- **Sub-accounts**: resellers and distributors can create sub-accounts for customer billing

### Billing Account IAM Roles

| Role | Permissions |
|---|---|
| Billing Account Administrator | Full control: create/delete accounts, link projects, manage payment |
| Billing Account Viewer | View costs, invoices, and account metadata; cannot modify |
| Billing Account Costs Manager | Create/edit budgets; view costs; cannot modify payment or link projects |
| Billing Account User | Link projects to billing account; view account info |
| Project Billing Manager | Manage billing account link for a specific project |

**Best practice**: separate Billing Account Administrator from project owners. Grant developers Billing Account Costs Manager so they can view costs and set budgets without being able to change payment methods.

---

## Budget Alerts

Budgets let you set spending limits with automated notifications. They do not stop spending by default but can trigger automated responses.

### Budget Configuration

- **Scope**: budget can cover an entire billing account, specific projects, specific services, or label-filtered resources
- **Budget amount**:
  - Fixed amount (e.g., $10,000/month)
  - Last month's spend (dynamic; automatically adjusts each month)
  - Custom amount based on forecasted spend
- **Time period**: monthly (most common), quarterly, annual, or custom date range
- **Threshold rules**: define percentage or absolute triggers
  - Example: 50% → 90% → 100% → 120% of budget
  - Threshold type: actual spend OR forecasted spend (alerts before you reach the limit)

### Notification Channels

1. **Email notifications**: automatically email billing account administrators; optionally notify project owners and billing users
2. **Pub/Sub topic**: publish a JSON message to a Cloud Pub/Sub topic; use for programmatic automation:
   - Cloud Function triggered to disable billing on a project (stops all resources)
   - Send Slack/PagerDuty alerts via webhook
   - Scale down non-critical workloads automatically
   - Example budget alert Pub/Sub message includes: `budgetDisplayName`, `costAmount`, `budgetAmount`, `alertThresholdExceeded`

### Budget Alert Pub/Sub Automation Example

Pattern: budget alert → Pub/Sub topic → Cloud Function → disable project billing

```
Budget (90%) → Pub/Sub → Cloud Function →
  if costAmount > budgetAmount:
    billing.projects.updateBillingInfo(project, billingAccountName: "")
    # This disables billing, which stops all paid resources
```

> **Warning**: disabling billing on a project stops ALL resources including VMs, databases, and load balancers. Use carefully; consider scaling down instead of full disable.

---

## Labels and Tags for Cost Allocation

Consistent resource labeling is the foundation of cost allocation reporting.

### Labels vs Tags

| Feature | Labels | Tags |
|---|---|---|
| Scope | Resource-level (per resource) | Organization, folder, or project-level (hierarchical) |
| Appear in billing? | Yes (after ~1 day) | Yes (Org-level tags appear in billing export) |
| Propagate to children? | No (must set on each resource) | Yes (inherited by child resources) |
| Use in IAM conditions? | No | Yes (tags used in IAM conditions and org policies) |

### Label Taxonomy Best Practices

Establish a standard label taxonomy across your organization:

| Label Key | Example Values | Purpose |
|---|---|---|
| `env` | `production`, `staging`, `dev`, `sandbox` | Environment separation |
| `team` | `platform`, `data-engineering`, `backend` | Team ownership |
| `cost-center` | `eng-001`, `mkt-005` | Chargeback/showback |
| `project` | `recommender-v2`, `data-pipeline` | Business project tracking |
| `app` | `web-frontend`, `auth-service` | Application component |
| `owner` | `alice`, `team-infra` | Individual/team owner |

**Enforcement**: use Organization Policies (`constraints/compute.requireLabels`) to enforce required labels on new resources.

### Resources that support labels
- Compute Engine instances, disks, snapshots, images
- GKE clusters and node pools
- Cloud Storage buckets
- Cloud SQL instances
- BigQuery datasets and tables
- Pub/Sub topics and subscriptions
- Cloud Functions, Cloud Run services
- Vertex AI training jobs, models
- Firestore databases
- Cloud Spanner instances
- VPC networks, subnets, forwarding rules

---

## Billing Export to BigQuery

**Billing export** streams your detailed cost data to a BigQuery dataset for advanced analysis, visualization, and chargebacks.

### Export Types

| Export Type | Granularity | Latency | Notes |
|---|---|---|---|
| Standard usage cost export | Daily; resource-level cost rows | ~1 day | Includes labels, project, service, SKU, usage amount, cost, credits |
| Detailed usage cost export | Daily; includes resource-level metadata (instance name, disk name, etc.) | ~1 day | More granular; larger dataset |
| Pricing export | Current SKU pricing | Near real-time | All GCP SKUs and prices |

### BigQuery Export Schema (key columns)
- `billing_account_id` — billing account that incurred the cost
- `project.id`, `project.name` — GCP project
- `service.description` — GCP service name (Compute Engine, BigQuery, etc.)
- `sku.description` — specific SKU (N2 Instance Core running, etc.)
- `usage_start_time`, `usage_end_time` — when usage occurred
- `usage.amount`, `usage.unit` — quantity and unit (hours, gibibytes, etc.)
- `cost` — before credits
- `credits` — array of credits applied (CUD, SUD, free tier, etc.)
- `labels` — array of label key/value pairs
- `resource.name` — specific resource name (for detailed export)
- `location.region`, `location.zone` — where resource ran

### Useful BigQuery Billing Queries

**Monthly cost by service:**
```sql
SELECT
  service.description AS service,
  SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
FROM `PROJECT.DATASET.gcp_billing_export_v1_ACCOUNT_ID`
WHERE DATE(_PARTITIONTIME) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY service
ORDER BY net_cost DESC;
```

**Cost by label (team):**
```sql
SELECT
  (SELECT value FROM UNNEST(labels) WHERE key = 'team') AS team,
  SUM(cost) AS total_cost
FROM `PROJECT.DATASET.gcp_billing_export_v1_ACCOUNT_ID`
WHERE DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY team
ORDER BY total_cost DESC;
```

**Credits by type (CUD, SUD, free tier):**
```sql
SELECT
  credit.type,
  SUM(credit.amount) AS total_credit
FROM `PROJECT.DATASET.gcp_billing_export_v1_ACCOUNT_ID`,
  UNNEST(credits) AS credit
WHERE DATE(_PARTITIONTIME) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY credit.type;
```

---

## Cost Breakdown and Visualization

### Cloud Billing Console Reports

Access at: **Billing > Reports**

- Filter by: time range, project, service, SKU, label, location
- View by: service, project, SKU, region, or label
- Chart types: bar chart (total), trend line, stacked area
- Compare periods: month-over-month or custom

### Looker Studio (Data Studio) Integration

- Connect Looker Studio to your billing export BigQuery dataset
- Pre-built [GCP billing dashboard template](https://datastudio.google.com/c/u/0/reporting/0B7GT7ZGPu9koUGtkN3RUZGF3YUU) available
- Build custom dashboards: cost by team (label), project, environment
- Share with stakeholders without granting GCP console access

### Cost Table Export (Invoice)

- **Billing > Cost table**: filterable monthly cost breakdown by project
- Export to CSV for spreadsheet analysis
- **Invoices/Statements**: downloadable PDF invoices; credit notes

---

## Cost Management Best Practices

1. **Enable billing export to BigQuery** on day one — retroactive data is not available
2. **Set budgets with Pub/Sub** for every project; auto-disable billing on sandbox/dev projects at 100%
3. **Label every resource** from creation; use org policy to enforce required labels
4. **Use Active Assist recommendations** weekly; review idle resources, rightsizing, CUD opportunities
5. **Schedule dev/staging VMs to stop overnight** using Cloud Scheduler + Cloud Functions
6. **Right-size before committing** to CUDs; run workloads for 30+ days to establish baselines
7. **Enable CUD sharing** at the billing account level to maximize discount utilization across projects
8. **Use Spot VMs** for all batch/fault-tolerant workloads; design stateless or checkpointed jobs
9. **Partition and cluster BigQuery tables**; avoid SELECT * on large tables
10. **Review egress costs**: co-locate compute and data in the same region; use Private Google Access
11. **Set lifecycle policies on Cloud Storage** to transition data to cheaper storage classes (Nearline, Coldline, Archive)
12. **Use Committed Use for predictable workloads** after validating with 30+ days of actual usage data
