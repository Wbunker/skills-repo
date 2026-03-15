# IaC & Governance — CLI Reference

---

## Resource Manager: Projects

```bash
# Create a project
gcloud projects create my-new-project \
  --name="My New Project" \
  --organization=123456789

# Create a project in a folder
gcloud projects create my-new-project \
  --name="My New Project" \
  --folder=987654321

# List projects (accessible to current account)
gcloud projects list

# List projects in an organization
gcloud projects list \
  --filter="parent.id=123456789 AND parent.type=organization"

# List projects in a folder
gcloud projects list \
  --filter="parent.id=987654321 AND parent.type=folder"

# Describe a project
gcloud projects describe my-project

# Update project display name
gcloud projects update my-project \
  --name="Updated Display Name"

# Add labels to a project
gcloud projects update my-project \
  --update-labels=env=production,team=backend,cost-center=cc-1234

# Remove labels
gcloud projects update my-project \
  --remove-labels=old-label

# Set a lien (prevent project deletion)
gcloud alpha projects liens create \
  --project=my-project \
  --reason="Locked by production policy — do not delete" \
  --restrictions=resourcemanager.projects.delete

# List liens on a project
gcloud alpha projects liens list --project=my-project

# Remove a lien
gcloud alpha projects liens delete LIEN_NAME

# Delete a project (moves to recycle bin; permanent after 30 days)
gcloud projects delete my-project

# Undelete a project (within 30-day window)
gcloud projects undelete my-project
```

---

## Resource Manager: Folders

```bash
# Create a folder
gcloud resource-manager folders create \
  --display-name="Production" \
  --organization=123456789

# Create a nested folder
gcloud resource-manager folders create \
  --display-name="US Region" \
  --folder=PARENT_FOLDER_ID

# List folders in an organization
gcloud resource-manager folders list \
  --organization=123456789

# List sub-folders
gcloud resource-manager folders list \
  --folder=PARENT_FOLDER_ID

# Describe a folder
gcloud resource-manager folders describe FOLDER_ID

# Update folder display name
gcloud resource-manager folders update FOLDER_ID \
  --display-name="New Folder Name"

# Get IAM policy for a folder
gcloud resource-manager folders get-iam-policy FOLDER_ID

# Add IAM binding to a folder
gcloud resource-manager folders add-iam-policy-binding FOLDER_ID \
  --member="group:devops@example.com" \
  --role="roles/resourcemanager.folderAdmin"

# Delete a folder (must be empty)
gcloud resource-manager folders delete FOLDER_ID
```

---

## Resource Manager: Organization

```bash
# List organizations accessible to current account
gcloud organizations list

# Describe an organization
gcloud organizations describe 123456789

# Get organization IAM policy
gcloud organizations get-iam-policy 123456789

# Add IAM binding at org level
gcloud organizations add-iam-policy-binding 123456789 \
  --member="group:org-admins@example.com" \
  --role="roles/resourcemanager.organizationAdmin"

# Set organization policy (constrain resource locations)
gcloud resource-manager org-policies set-policy \
  --organization=123456789 \
  ./location-policy.yaml

# Get an organization policy
gcloud resource-manager org-policies describe \
  constraints/gcp.resourceLocations \
  --organization=123456789

# List effective org policies on a project
gcloud resource-manager org-policies list \
  --project=my-project
```

---

## Cloud Asset Inventory

```bash
# Search all resources across a project
gcloud asset search-all-resources \
  --scope=projects/my-project \
  --asset-types=compute.googleapis.com/Instance,storage.googleapis.com/Bucket \
  --query="state:RUNNING" \
  --project=my-project

# Search all resources across an organization
gcloud asset search-all-resources \
  --scope=organizations/123456789 \
  --asset-types=compute.googleapis.com/Instance \
  --query="labels.env:production"

# Search all IAM policies matching a member
gcloud asset search-all-iam-policies \
  --scope=organizations/123456789 \
  --query="policy.role:roles/owner" \
  --project=my-project

# Search IAM policies granted to a specific user
gcloud asset search-all-iam-policies \
  --scope=organizations/123456789 \
  --query="policy.member:user:admin@example.com"

# Export asset inventory snapshot to BigQuery
gcloud asset export \
  --project=my-project \
  --billing-project=my-project \
  --output-bigquery-table=my-project:asset_inventory.resources \
  --content-type=resource \
  --asset-types=compute.googleapis.com/Instance,container.googleapis.com/Cluster \
  --snapshot-time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Export IAM policy snapshot to BigQuery
gcloud asset export \
  --organization=123456789 \
  --billing-project=my-project \
  --output-bigquery-table=my-project:asset_inventory.iam_policies \
  --content-type=iam-policy

# Export to Cloud Storage
gcloud asset export \
  --project=my-project \
  --billing-project=my-project \
  --output-path=gs://my-asset-bucket/snapshots/resources.json \
  --content-type=resource

# Create a real-time feed (Pub/Sub notifications on resource changes)
gcloud asset feeds create my-resource-feed \
  --project=my-project \
  --pubsub-topic=projects/my-project/topics/asset-changes \
  --asset-types=compute.googleapis.com/Instance \
  --content-type=resource

# Create a feed for IAM policy changes
gcloud asset feeds create iam-policy-feed \
  --organization=123456789 \
  --pubsub-topic=projects/my-project/topics/iam-changes \
  --content-type=iam-policy

# List feeds
gcloud asset feeds list --project=my-project

# Describe a feed
gcloud asset feeds describe my-resource-feed --project=my-project

# Delete a feed
gcloud asset feeds delete my-resource-feed --project=my-project

# Analyze IAM policy (who can do what)
gcloud asset analyze-iam-policy \
  --organization=123456789 \
  --identity="user:admin@example.com" \
  --full-resource-name="//cloudresourcemanager.googleapis.com/projects/my-project"

# Get all effective IAM roles for a service account
gcloud asset analyze-iam-policy \
  --project=my-project \
  --identity="serviceAccount:my-sa@my-project.iam.gserviceaccount.com"
```

---

## Recommender

```bash
# List IAM recommendations for a project (find excess permissions)
gcloud recommender recommendations list \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --format=table"(name,description,stateInfo.state)"

# List VM rightsizing recommendations
gcloud recommender recommendations list \
  --project=my-project \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --format=table"(name,description,primaryImpact.costProjection.cost.units)"

# List idle VM recommendations
gcloud recommender recommendations list \
  --project=my-project \
  --recommender=google.compute.instance.IdleResourceRecommender \
  --location=us-central1

# List recommendations for committed use discounts
gcloud recommender recommendations list \
  --project=my-project \
  --recommender=google.compute.commitment.UsageCommitmentRecommender \
  --location=us-central1

# Describe a recommendation (full details)
gcloud recommender recommendations describe RECOMMENDATION_ID \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global

# Mark a recommendation as claimed (in progress)
gcloud recommender recommendations mark-claimed RECOMMENDATION_ID \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --etag=RECOMMENDATION_ETAG

# Mark a recommendation as succeeded (completed)
gcloud recommender recommendations mark-succeeded RECOMMENDATION_ID \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --etag=RECOMMENDATION_ETAG

# Mark a recommendation as failed
gcloud recommender recommendations mark-failed RECOMMENDATION_ID \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --etag=RECOMMENDATION_ETAG

# Mark a recommendation as dismissed
gcloud recommender recommendations mark-dismissed RECOMMENDATION_ID \
  --project=my-project \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --etag=RECOMMENDATION_ETAG

# List IAM insights (observations about IAM usage)
gcloud recommender insights list \
  --project=my-project \
  --insight-type=google.iam.policy.Insight \
  --location=global
```

---

## Deployment Manager

```bash
# Create a deployment from a YAML config
gcloud deployment-manager deployments create my-deployment \
  --config=deployment.yaml \
  --project=my-project

# Create a deployment with properties
gcloud deployment-manager deployments create my-deployment \
  --template=vm_template.py \
  --properties=zone:us-central1-a,machineType:n1-standard-2 \
  --project=my-project

# Preview a deployment (shows planned changes without applying)
gcloud deployment-manager deployments create my-deployment \
  --config=deployment.yaml \
  --preview \
  --project=my-project

# Cancel a preview (discard planned changes)
gcloud deployment-manager deployments cancel-preview my-deployment \
  --project=my-project

# Update an existing deployment
gcloud deployment-manager deployments update my-deployment \
  --config=updated-deployment.yaml \
  --project=my-project

# Update with preview first
gcloud deployment-manager deployments update my-deployment \
  --config=updated-deployment.yaml \
  --preview \
  --project=my-project

# List deployments
gcloud deployment-manager deployments list --project=my-project

# Describe a deployment
gcloud deployment-manager deployments describe my-deployment \
  --project=my-project

# List resources in a deployment
gcloud deployment-manager resources list \
  --deployment=my-deployment \
  --project=my-project

# List manifests (versions of a deployment)
gcloud deployment-manager manifests list \
  --deployment=my-deployment \
  --project=my-project

# Delete a deployment and all its resources
gcloud deployment-manager deployments delete my-deployment \
  --project=my-project

# Delete deployment but keep resources
gcloud deployment-manager deployments delete my-deployment \
  --delete-policy=ABANDON \
  --project=my-project
```

---

## Terraform with GCS Backend

```bash
# Initialize Terraform with GCS backend
# (backend config in versions.tf: bucket = "my-terraform-state-bucket")
terraform init

# Create GCS bucket for Terraform state (one-time setup)
gcloud storage buckets create gs://my-terraform-state-bucket \
  --location=us-central1 \
  --uniform-bucket-level-access \
  --public-access-prevention \
  --project=my-project

# Enable versioning on state bucket (allows state recovery)
gcloud storage buckets update gs://my-terraform-state-bucket \
  --versioning

# Initialize with backend config override
terraform init \
  -backend-config="bucket=my-terraform-state-bucket" \
  -backend-config="prefix=terraform/production"

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Apply with specific var file
terraform apply \
  -var-file=environments/production.tfvars

# Destroy all resources in state
terraform destroy \
  -var-file=environments/production.tfvars

# Import an existing GCP resource into Terraform state
terraform import google_storage_bucket.my_bucket my-project/my-existing-bucket

# Show current state
terraform show

# List resources in state
terraform state list

# Move a resource in state (for refactoring)
terraform state mv \
  module.old_name.google_compute_instance.vm \
  module.new_name.google_compute_instance.vm

# Remove a resource from state (without destroying)
terraform state rm google_compute_instance.my_vm

# Refresh state to match real infrastructure
terraform refresh

# Format HCL files
terraform fmt -recursive

# Validate configuration
terraform validate

# Upgrade providers
terraform init -upgrade

# Service account for Terraform (grant necessary permissions)
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account" \
  --project=my-project

gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:terraform-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/editor"

# Grant SA access to state bucket
gcloud storage buckets add-iam-policy-binding gs://my-terraform-state-bucket \
  --member="serviceAccount:terraform-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

---

## Organization Policy Service

```bash
# List all available constraints
gcloud resource-manager org-policies list-available-constraints \
  --organization=123456789

# Get current policy for a constraint on a project
gcloud resource-manager org-policies describe \
  constraints/compute.requireOsLogin \
  --project=my-project

# Set a boolean constraint (enforce)
gcloud resource-manager org-policies enable-enforce \
  constraints/compute.requireOsLogin \
  --project=my-project

# Set a boolean constraint (disable enforcement)
gcloud resource-manager org-policies disable-enforce \
  constraints/compute.requireOsLogin \
  --project=my-project

# Set a list constraint (restrict resource locations)
cat > location-policy.yaml << 'EOF'
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
  - in:us-locations
  - in:europe-locations
EOF

gcloud resource-manager org-policies set-policy \
  --organization=123456789 \
  ./location-policy.yaml

# Restrict external IPs on VMs
cat > no-external-ip.yaml << 'EOF'
constraint: constraints/compute.vmExternalIpAccess
listPolicy:
  allValues: DENY
EOF

gcloud resource-manager org-policies set-policy \
  --project=my-project \
  ./no-external-ip.yaml

# Delete an org policy (restores inheritance from parent)
gcloud resource-manager org-policies delete \
  constraints/compute.requireOsLogin \
  --project=my-project
```
