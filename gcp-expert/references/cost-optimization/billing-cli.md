# GCP Billing & Budgets — CLI Reference

## Billing Accounts

### List billing accounts
```bash
# List all billing accounts accessible to current user
gcloud billing accounts list

# List with specific format
gcloud billing accounts list \
  --format="table(name,displayName,open,masterBillingAccount)"

# Filter to open accounts only
gcloud billing accounts list --filter="open=true"
```

### Describe a billing account
```bash
gcloud billing accounts describe 012345-678901-ABCDEF
```

### IAM Policy on billing account
```bash
# View IAM policy
gcloud billing accounts get-iam-policy 012345-678901-ABCDEF

# Add a member to Billing Account Viewer role
gcloud billing accounts add-iam-policy-binding 012345-678901-ABCDEF \
  --member=user:finance@example.com \
  --role=roles/billing.viewer

# Add member to Billing Account Costs Manager
gcloud billing accounts add-iam-policy-binding 012345-678901-ABCDEF \
  --member=group:dev-leads@example.com \
  --role=roles/billing.costsManager

# Remove a member from a role
gcloud billing accounts remove-iam-policy-binding 012345-678901-ABCDEF \
  --member=user:olduser@example.com \
  --role=roles/billing.admin

# Set (replace) entire IAM policy from file
gcloud billing accounts set-iam-policy 012345-678901-ABCDEF policy.json
```

---

## Project Billing Association

### Link a project to a billing account
```bash
gcloud billing projects link my-project-id \
  --billing-account=012345-678901-ABCDEF
```

### Describe billing info for a project
```bash
gcloud billing projects describe my-project-id
# Returns: billingAccountName, billingEnabled (true/false), name, projectId
```

### List all projects linked to a billing account
```bash
gcloud billing projects list \
  --billing-account=012345-678901-ABCDEF

gcloud billing projects list \
  --billing-account=012345-678901-ABCDEF \
  --format="table(projectId,billingEnabled)"
```

### Disable billing on a project (stops all paid resources — use with caution)
```bash
# Unlink project from billing account (disables billing)
gcloud billing projects unlink my-project-id
```

---

## Budget Management

### Create a budget
```bash
# Simple monthly budget with email alerts at 50%, 90%, 100%
gcloud billing budgets create \
  --billing-account=012345-678901-ABCDEF \
  --display-name="Dev Environment Monthly Budget" \
  --budget-amount=500USD \
  --threshold-rules=percent=0.5,basis=CURRENT_SPEND \
  --threshold-rules=percent=0.9,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.0,basis=CURRENT_SPEND

# Budget scoped to specific projects
gcloud billing budgets create \
  --billing-account=012345-678901-ABCDEF \
  --display-name="Team Platform Budget" \
  --budget-amount=2000USD \
  --projects=projects/my-platform-project \
  --threshold-rules=percent=0.5,basis=CURRENT_SPEND \
  --threshold-rules=percent=0.9,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.0,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.2,basis=CURRENT_SPEND

# Budget with Pub/Sub notification for automation
gcloud billing budgets create \
  --billing-account=012345-678901-ABCDEF \
  --display-name="Sandbox Auto-Disable Budget" \
  --budget-amount=100USD \
  --threshold-rules=percent=1.0,basis=CURRENT_SPEND \
  --notifications-rule-pubsub-topic=projects/my-project/topics/billing-alerts \
  --notifications-rule-schema-version=1.0

# Budget based on last month's spend (dynamic)
gcloud billing budgets create \
  --billing-account=012345-678901-ABCDEF \
  --display-name="Dynamic Last Month Budget" \
  --last-period-amount \
  --threshold-rules=percent=1.1,basis=FORECASTED_SPEND

# Budget scoped to specific services (Compute Engine + BigQuery)
gcloud billing budgets create \
  --billing-account=012345-678901-ABCDEF \
  --display-name="Compute and BQ Budget" \
  --budget-amount=5000USD \
  --services=services/6F81-5844-456A,services/95FF-2EF5-5EA1 \
  --threshold-rules=percent=0.8,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.0,basis=CURRENT_SPEND
```

### List budgets
```bash
gcloud billing budgets list \
  --billing-account=012345-678901-ABCDEF

gcloud billing budgets list \
  --billing-account=012345-678901-ABCDEF \
  --format="table(name,displayName,amount.specifiedAmount.currencyCode,amount.specifiedAmount.units)"
```

### Describe a budget
```bash
gcloud billing budgets describe BUDGET_ID \
  --billing-account=012345-678901-ABCDEF
```

### Update a budget
```bash
# Increase budget amount
gcloud billing budgets update BUDGET_ID \
  --billing-account=012345-678901-ABCDEF \
  --budget-amount=1000USD

# Add a new threshold rule
gcloud billing budgets update BUDGET_ID \
  --billing-account=012345-678901-ABCDEF \
  --threshold-rules=percent=0.5,basis=CURRENT_SPEND \
  --threshold-rules=percent=0.9,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.0,basis=CURRENT_SPEND \
  --threshold-rules=percent=1.5,basis=CURRENT_SPEND
```

### Delete a budget
```bash
gcloud billing budgets delete BUDGET_ID \
  --billing-account=012345-678901-ABCDEF
```

---

## Billing Export Setup (BigQuery)

Billing export is configured in the Cloud Console (Billing > Billing export > BigQuery export), but you can set up the BigQuery dataset via CLI:

```bash
# Create the BigQuery dataset for billing export
bq --location=US mk --dataset \
  --description="GCP billing export" \
  my-billing-project:billing_export

# Grant Billing Export service account write access
# (done automatically when you configure export in console)
# The SA is: billing-export-bigquery@system.gserviceaccount.com

# Verify dataset exists and has correct permissions
bq show --format=prettyjson my-billing-project:billing_export
```

---

## Querying Billing Data in BigQuery

```bash
# Run a cost-by-project query (last 30 days)
bq query --use_legacy_sql=false \
  --project_id=my-billing-project \
'SELECT
  project.id AS project_id,
  SUM(cost) AS total_cost,
  SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS total_credits
FROM `my-billing-project.billing_export.gcp_billing_export_v1_012345_678901_ABCDEF`
WHERE DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY project_id
ORDER BY total_cost DESC
LIMIT 20'

# Cost by service this month
bq query --use_legacy_sql=false \
  --project_id=my-billing-project \
'SELECT
  service.description,
  SUM(cost) AS total_cost
FROM `my-billing-project.billing_export.gcp_billing_export_v1_012345_678901_ABCDEF`
WHERE DATE(_PARTITIONTIME) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY 1
ORDER BY total_cost DESC'
```

---

## Labels Management

```bash
# Add labels to a Compute Engine instance
gcloud compute instances add-labels my-instance \
  --zone=us-central1-a \
  --labels=env=production,team=platform,cost-center=eng-001

# Remove a label from an instance
gcloud compute instances remove-labels my-instance \
  --zone=us-central1-a \
  --labels=old-label

# Add labels to a GCS bucket
gcloud storage buckets update gs://my-data-bucket \
  --update-labels=env=production,team=data,cost-center=data-001

# Add labels to a Cloud SQL instance
gcloud sql instances patch my-sql-db \
  --update-labels=env=production,team=backend

# Add labels to a Pub/Sub topic
gcloud pubsub topics update my-topic \
  --update-labels=env=production,team=events

# Add labels to a BigQuery dataset
bq update --set_label env:production --set_label team:analytics \
  my-project:my_dataset

# Add labels to a Cloud Run service
gcloud run services update my-service \
  --region=us-central1 \
  --update-labels=env=production,team=backend

# List all VMs with specific label
gcloud compute instances list \
  --filter="labels.env=production AND labels.team=platform" \
  --format="table(name,zone,machineType,status)"

# List all Cloud Storage buckets by team label
gcloud storage buckets list \
  --filter="labels.team=data" \
  --format="table(name,location,storageClass)"
```

---

## Cloud Scheduler: Stop Dev VMs Overnight

Automate VM shutdown to reduce costs in non-production environments:

```bash
# Create service account for scheduler
gcloud iam service-accounts create vm-scheduler \
  --display-name="VM Scheduler SA"

# Grant compute.instanceAdmin to stop/start VMs
gcloud projects add-iam-policy-binding my-dev-project \
  --member=serviceAccount:vm-scheduler@my-dev-project.iam.gserviceaccount.com \
  --role=roles/compute.instanceAdmin.v1

# Create Cloud Scheduler job to stop all dev VMs at 8pm (Mon-Fri)
gcloud scheduler jobs create http stop-dev-vms \
  --location=us-central1 \
  --schedule="0 20 * * 1-5" \
  --time-zone="America/Chicago" \
  --uri="https://compute.googleapis.com/compute/v1/projects/my-dev-project/zones/us-central1-a/instances/dev-vm-1/stop" \
  --message-body="{}" \
  --oauth-service-account-email=vm-scheduler@my-dev-project.iam.gserviceaccount.com \
  --oauth-token-scope=https://www.googleapis.com/auth/compute

# Create job to start VMs at 8am (Mon-Fri)
gcloud scheduler jobs create http start-dev-vms \
  --location=us-central1 \
  --schedule="0 8 * * 1-5" \
  --time-zone="America/Chicago" \
  --uri="https://compute.googleapis.com/compute/v1/projects/my-dev-project/zones/us-central1-a/instances/dev-vm-1/start" \
  --message-body="{}" \
  --oauth-service-account-email=vm-scheduler@my-dev-project.iam.gserviceaccount.com \
  --oauth-token-scope=https://www.googleapis.com/auth/compute
```
