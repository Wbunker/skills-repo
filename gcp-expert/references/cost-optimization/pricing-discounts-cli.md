# GCP Pricing & Discounts — CLI Reference

## Committed Use Discounts (CUDs)

### Create a resource-based CUD
```bash
# Commit to 64 vCPUs and 256GB memory in us-central1 for 1 year (GENERAL_PURPOSE covers N1/N2/E2)
gcloud compute commitments create my-commitment \
  --plan=12-month \
  --resources=vcpu=64,memory=256GB \
  --region=us-central1 \
  --type=GENERAL_PURPOSE

# 3-year commitment for accelerator-optimized workloads (A2 instances)
gcloud compute commitments create gpu-commitment \
  --plan=36-month \
  --resources=vcpu=96,memory=1360GB \
  --region=us-central1 \
  --type=ACCELERATOR_OPTIMIZED
```

### List and describe commitments
```bash
# List all commitments in a region
gcloud compute commitments list --region=us-central1

# List all commitments across all regions
gcloud compute commitments list --global

# Describe a specific commitment
gcloud compute commitments describe my-commitment --region=us-central1
```

### Update a commitment (add reservations)
```bash
# Update commitment to include a specific reservation
gcloud compute commitments update-reservations my-commitment \
  --region=us-central1 \
  --reservations=reservation-name=my-reservation,vm-count=10,machine-type=n2-standard-8,zone=us-central1-a
```

### View commitment utilization
```bash
# Describe shows status, plan, end time, and resource commitments
gcloud compute commitments describe my-commitment \
  --region=us-central1 \
  --format="yaml(name,plan,status,endTimestamp,resources)"
```

---

## Reservations

Reservations guarantee VM capacity in a specific zone (separate from CUDs but can be combined).

### Create a reservation
```bash
# Reserve 20 n2-standard-4 instances in us-central1-a
gcloud compute reservations create my-reservation \
  --machine-type=n2-standard-4 \
  --vm-count=20 \
  --zone=us-central1-a

# Reservation with specific min-cpu-platform
gcloud compute reservations create high-perf-reservation \
  --machine-type=n2-standard-16 \
  --vm-count=5 \
  --zone=us-central1-a \
  --min-cpu-platform="Intel Cascade Lake"

# Shared reservation (accessible to specific projects in org)
gcloud compute reservations create shared-reservation \
  --machine-type=n2-standard-8 \
  --vm-count=10 \
  --zone=us-central1-a \
  --share-setting=projects \
  --share-with=project-id-1,project-id-2
```

### List and manage reservations
```bash
gcloud compute reservations list --zones=us-central1-a
gcloud compute reservations describe my-reservation --zone=us-central1-a
gcloud compute reservations delete my-reservation --zone=us-central1-a
```

---

## Spot VMs

### Create a Spot VM
```bash
# Basic Spot VM (termination action: STOP)
gcloud compute instances create spot-worker-1 \
  --machine-type=n2-standard-4 \
  --zone=us-central1-a \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --image-family=debian-12 \
  --image-project=debian-cloud

# Spot VM with DELETE on termination (for stateless batch workers)
gcloud compute instances create batch-worker \
  --machine-type=c2-standard-8 \
  --zone=us-central1-a \
  --provisioning-model=SPOT \
  --instance-termination-action=DELETE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --no-restart-on-failure \
  --maintenance-policy=TERMINATE
```

### Create a Managed Instance Group with Spot VMs
```bash
# Instance template for Spot VM
gcloud compute instance-templates create spot-worker-template \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP

# Create MIG using Spot template
gcloud compute instance-groups managed create spot-worker-group \
  --template=spot-worker-template \
  --size=5 \
  --zone=us-central1-a

# Mixed policy MIG (some standard, some Spot for fallback reliability)
gcloud compute instance-groups managed create mixed-worker-group \
  --template=standard-worker-template \
  --size=3 \
  --zone=us-central1-a

gcloud compute instance-groups managed set-autoscaling mixed-worker-group \
  --zone=us-central1-a \
  --max-num-replicas=20 \
  --min-num-replicas=3

# Update MIG with Spot mix policy
gcloud beta compute instance-groups managed update mixed-worker-group \
  --zone=us-central1-a \
  --balancing-mode=SPOT_PREFERRED
```

---

## Viewing Quota and Pricing Metadata

### Check regional quotas (vCPU, in-use IPs, etc.)
```bash
# View all quotas for a region
gcloud compute regions describe us-central1 \
  --format="table(quotas.metric,quotas.limit,quotas.usage)"

# Check specific quota
gcloud compute regions describe us-central1 \
  --format="table(quotas[metric=CPUS].limit,quotas[metric=CPUS].usage)"
```

### Enable Pricing API and list SKUs (alpha)
```bash
# List available pricing SKUs for Compute Engine (alpha, limited scope)
gcloud alpha billing catalogs list-services

# Describe a service's SKUs
gcloud alpha billing catalogs list-skus \
  --service=6F81-5844-456A \
  --filter="category.resourceFamily=Compute"
```

> **Note**: For detailed pricing lookups, use the [Cloud Billing Catalog API](https://cloud.google.com/billing/v1/how-tos/catalog-api) REST endpoint or the [GCP Pricing Calculator](https://cloud.google.com/products/calculator). The gcloud alpha billing catalogs commands have limited coverage.

---

## Applying Labels for Discount Tracking

Labels are used for cost allocation and appear in billing export. Apply them consistently to all resources.

```bash
# Add labels to a running VM
gcloud compute instances add-labels my-vm \
  --zone=us-central1-a \
  --labels=env=production,team=platform,cost-center=eng-01

# Add labels to a GCS bucket
gcloud storage buckets update gs://my-bucket \
  --update-labels=env=production,team=data

# Add labels to a Cloud SQL instance
gcloud sql instances patch my-sql-instance \
  --update-labels=env=production,team=backend

# Add labels to a GKE cluster
gcloud container clusters update my-cluster \
  --zone=us-central1-a \
  --update-labels=env=production,team=platform

# List all Compute Engine instances with a specific label
gcloud compute instances list \
  --filter="labels.env=production" \
  --format="table(name,zone,machineType,status)"
```

---

## Checking Sustained Use Discount Impact

SUDs are applied automatically and reflected in your billing. To evaluate:

```bash
# Export billing to BigQuery first (see billing-cli.md), then query:
# bq query --use_legacy_sql=false '
# SELECT
#   service.description,
#   sku.description,
#   SUM(cost) as total_cost,
#   SUM(credits.amount) as total_credits
# FROM `PROJECT.DATASET.gcp_billing_export_v1_ACCOUNT_ID`
# WHERE
#   credits.type = "SUSTAINED_USAGE_DISCOUNT"
#   AND DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
# GROUP BY 1, 2
# ORDER BY total_credits ASC
# '

# View SUD credits in billing console via:
# Billing > Reports > Filter by Credit type > Sustained use discounts
echo "SUDs are automatic; verify via billing export BigQuery queries or Console reports"
```
