# IaC & Governance — Capabilities

## Terraform (Google Provider)

### Purpose

HashiCorp Terraform with the `google` and `google-beta` providers is the dominant IaC tool for GCP. Defines infrastructure as HCL configuration files; plans changes before applying; stores state to track deployed resources. Preferred over Deployment Manager for new GCP infrastructure.

### Provider Configuration

```hcl
# versions.tf
terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket  = "my-terraform-state-bucket"
    prefix  = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
```

### Authentication

- **Application Default Credentials** (ADC): `gcloud auth application-default login`; used for local development
- **Service Account Key**: JSON key file via `GOOGLE_APPLICATION_CREDENTIALS` env var (avoid; prefer Workload Identity or ADC)
- **Workload Identity / OIDC**: recommended for CI/CD; no key rotation needed; GitHub Actions → Workload Identity Federation

### Key Resource Patterns

```hcl
# IAM: use _member (additive) not _binding (authoritative) to avoid conflicts
resource "google_project_iam_member" "gke_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

# Avoid google_project_iam_binding in shared projects — it overwrites all members for that role

# GKE cluster
resource "google_container_cluster" "primary" {
  name     = "my-cluster"
  location = "us-central1"

  # Use a separately managed node pool; remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.primary.name
  node_count = 3

  node_config {
    machine_type    = "n2-standard-4"
    service_account = google_service_account.gke_sa.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# Cloud SQL
resource "google_sql_database_instance" "postgres" {
  name             = "my-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-custom-2-7680"
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.vpc.self_link
      enable_private_path_for_google_cloud_services = true
    }
  }
  deletion_protection = true
}

# Storage bucket
resource "google_storage_bucket" "data" {
  name          = "${var.project_id}-data"
  location      = "US"
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}
```

### State Management

- Remote state in Cloud Storage is standard practice
- Use separate state files per environment (dev/staging/prod) and per component (networking, compute, data)
- State locking: GCS backend uses object metadata for locking (no additional setup)
- `terraform state mv`, `terraform import`: for refactoring without recreation
- Sensitive outputs: use `sensitive = true` and Secret Manager integration

### Workspace Patterns

| Pattern | Tools | Notes |
|---|---|---|
| Directories | Per-env directories | Simple; explicit; no workspace state isolation |
| Terraform Workspaces | `terraform workspace` | Built-in; use with caution (shared modules; single backend prefix) |
| Terraform Cloud | Remote runs, policy enforcement, RBAC | Enterprise-grade; free tier available |
| Atlantis | Open-source TFC alternative; runs on GKE/GCE | Pull-request workflow |
| Terragrunt | Wrapper for DRY Terraform configs | Popular for multi-account setups |

---

## Cloud Deployment Manager

### Purpose

GCP-native IaC using YAML, Python 2.7, or Jinja2 templates. Predates Terraform; being superseded by Terraform and Config Connector for new projects. Still supported and functional.

### Structure

```yaml
# deployment.yaml
imports:
- path: vm_template.py

resources:
- name: my-vm
  type: vm_template.py
  properties:
    zone: us-central1-a
    machineType: n1-standard-2
    image: projects/debian-cloud/global/images/family/debian-11
    network: global/networks/default
```

```python
# vm_template.py
def GenerateConfig(context):
    resources = [{
        'name': context.env['name'],
        'type': 'compute.v1.instance',
        'properties': {
            'zone': context.properties['zone'],
            'machineType': f"zones/{context.properties['zone']}/machineTypes/{context.properties['machineType']}",
            'disks': [{
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': context.properties['image']
                }
            }],
            'networkInterfaces': [{
                'network': context.properties['network']
            }]
        }
    }]
    return {'resources': resources}
```

**When to use Deployment Manager**: existing legacy deployments; when Terraform is explicitly prohibited; teams deeply familiar with GCP-native tooling.

---

## Config Connector

### Purpose

Kubernetes controller that manages GCP resources via Kubernetes CRDs. Enables GitOps workflows where GCP infrastructure is managed through `kubectl apply` and Kubernetes manifests stored in Git. Runs in GKE and uses Workload Identity for authentication.

### Setup

```bash
# Enable Config Connector on a GKE cluster (Autopilot: built-in option)
gcloud container clusters update my-cluster \
  --update-addons=ConfigConnector=ENABLED \
  --region=us-central1

# Create a service account for Config Connector to use
gcloud iam service-accounts create config-connector-sa \
  --project=my-project

gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:config-connector-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/owner"

# Bind KSA to GSA via Workload Identity
gcloud iam service-accounts add-iam-policy-binding config-connector-sa@my-project.iam.gserviceaccount.com \
  --member="serviceAccount:my-project.svc.id.goog[cnrm-system/cnrm-controller-manager-my-project]" \
  --role="roles/iam.workloadIdentityUser"
```

### Example CRDs

```yaml
# Create a Cloud Storage bucket via Config Connector
apiVersion: storage.cnrm.cloud.google.com/v1beta1
kind: StorageBucket
metadata:
  name: my-config-connector-bucket
  namespace: config-connector
  annotations:
    cnrm.cloud.google.com/project-id: my-project
spec:
  location: US
  uniformBucketLevelAccess: true
  versioning:
    enabled: true

---
# Create a Pub/Sub topic via Config Connector
apiVersion: pubsub.cnrm.cloud.google.com/v1beta1
kind: PubSubTopic
metadata:
  name: my-topic
  namespace: config-connector
  annotations:
    cnrm.cloud.google.com/project-id: my-project
spec:
  resourceID: my-topic

---
# Create a BigQuery dataset
apiVersion: bigquery.cnrm.cloud.google.com/v1beta1
kind: BigQueryDataset
metadata:
  name: my-dataset
  namespace: config-connector
spec:
  location: US
  defaultTableExpirationMs: 7776000000
```

---

## Resource Manager

### Organization Hierarchy

```
Organization (org ID)
├── Folders (optional grouping)
│   ├── Folder: Production
│   │   ├── Project: my-prod-app
│   │   └── Project: my-prod-data
│   └── Folder: Development
│       └── Project: my-dev-app
└── Projects (outside folders)
    └── Project: shared-services
```

### Key Features

- **Projects**: billing and IAM boundary; most GCP resources live in a project
- **Labels**: key-value tags on projects, resources; used for cost allocation, automation, filtering
- **Tags** (newer): structured key-value pairs with IAM policies; conditional IAM bindings; more powerful than labels
- **Liens**: prevent accidental project deletion by placing a lien on the project; must be removed before deletion
- **Organization policies**: constraints applied at org/folder/project level (e.g., restrict resource locations, disable service account key creation, require CMEK)

---

## Cloud Asset Inventory

### Purpose

Tracks all GCP resources and IAM policies across an organization in real-time. Supports point-in-time snapshots, historical change queries, real-time Pub/Sub feeds, and policy analysis.

### Key Capabilities

- **Search**: full-text search across all resources; filter by type, project, label
- **Export**: snapshot of all resources or IAM policies to BigQuery or GCS
- **Real-time feed**: Pub/Sub notifications on resource changes
- **Policy analysis**: analyze IAM policy bindings to answer "who can do what on which resources"
- **Effective IAM**: resolve inherited IAM policies across org/folder/project hierarchy
- **Asset types**: 250+ supported asset types (compute instances, buckets, GKE clusters, IAM policies, etc.)

---

## Recommender

AI/ML-powered recommendations for cost, security, reliability, and performance:

| Recommender | Recommendation Type |
|---|---|
| VM machine type | Rightsize oversized Compute Engine instances |
| Idle VM | Identify and stop VMs with low CPU/network |
| Idle custom role | Identify IAM custom roles with no recent use |
| IAM excess permissions | Replace broad roles with least-privilege alternatives |
| Unattended project | Projects with low activity; consider deletion |
| Committed use discount | Recommend CUD based on usage patterns |
| BigQuery slot commitment | Recommend slot reservation based on query patterns |
| Firewall rule | Remove overly permissive or unused firewall rules |
| GKE node pool | Rightsize GKE node pools |

### Active Assist

Umbrella branding for Recommender + Insights + proactive health:
- **Insights**: observations without a specific recommendation action (e.g., "this SA was not used in 90 days")
- **Recommendations**: specific actions to take (e.g., "remove unused role binding")
- **Proactive health**: early warnings before they become incidents
