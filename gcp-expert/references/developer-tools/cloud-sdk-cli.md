# Cloud SDK & Shell — CLI

## Installation and Updates

```bash
# Install Cloud SDK (macOS/Linux)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install Cloud SDK (Debian/Ubuntu via apt)
echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  sudo tee /usr/share/keyrings/cloud.google.asc
sudo apt-get update && sudo apt-get install google-cloud-cli

# Install on macOS via Homebrew
brew install --cask google-cloud-sdk

# Check SDK version
gcloud version

# Update all installed components
gcloud components update

# List installed and available components
gcloud components list

# Install a specific component
gcloud components install kubectl
gcloud components install skaffold
gcloud components install alpha
gcloud components install beta
gcloud components install cloud-firestore-emulator
gcloud components install pubsub-emulator
gcloud components install spanner-emulator
gcloud components install bigtable

# Remove a component
gcloud components remove COMPONENT_ID

# Reinstall a component
gcloud components reinstall COMPONENT_ID
```

---

## Authentication

```bash
# Interactive login (opens browser)
gcloud auth login

# Login without browser (for remote/headless environments)
gcloud auth login --no-launch-browser

# Login with a specific account
gcloud auth login user@example.com

# Set Application Default Credentials for local development
gcloud auth application-default login

# Set ADC with a specific quota project
gcloud auth application-default login \
  --billing-project=my-billing-project

# Set quota project for existing ADC
gcloud auth application-default set-quota-project PROJECT_ID

# Activate a service account key (for CI/CD)
gcloud auth activate-service-account \
  --key-file=/path/to/sa-key.json

# Activate SA key from environment variable
gcloud auth activate-service-account \
  --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"

# Print access token (for use in API calls)
gcloud auth print-access-token

# Print ADC access token (application default)
gcloud auth application-default print-access-token

# Print identity token (OIDC token for Cloud Run)
gcloud auth print-identity-token

# List all authenticated accounts
gcloud auth list

# Switch active account
gcloud config set account user@example.com

# Revoke credentials for an account
gcloud auth revoke user@example.com

# Revoke all credentials
gcloud auth revoke --all

# Configure Docker to use gcloud credentials
gcloud auth configure-docker
gcloud auth configure-docker us-central1-docker.pkg.dev,europe-west1-docker.pkg.dev
```

---

## Configurations

```bash
# Create a new named configuration
gcloud config configurations create my-project-config

# List all configurations
gcloud config configurations list

# Activate a configuration
gcloud config configurations activate my-project-config

# Describe a configuration (show all properties)
gcloud config configurations describe my-project-config

# Delete a configuration
gcloud config configurations delete old-config

# Set properties in the active configuration
gcloud config set core/project my-project-id
gcloud config set core/account user@example.com
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud config set run/region us-central1
gcloud config set container/cluster my-cluster
gcloud config set container/cluster_location us-central1

# Unset a property
gcloud config unset compute/zone

# Show all current configuration settings
gcloud config list

# Show a specific property value
gcloud config get-value core/project
gcloud config get-value compute/region

# Override property for a single command
gcloud compute instances list \
  --project=other-project \
  --zone=us-east1-b

# Set impersonation in active config
gcloud config set auth/impersonate_service_account sa@PROJECT.iam.gserviceaccount.com

# Clear impersonation
gcloud config unset auth/impersonate_service_account
```

---

## Project Management

```bash
# List all projects accessible to the current account
gcloud projects list

# List projects with a filter
gcloud projects list --filter="projectId:my-org-*"

# Describe a project
gcloud projects describe my-project-id

# Create a new project
gcloud projects create my-new-project \
  --name="My New Project" \
  --organization=ORGANIZATION_ID \
  --folder=FOLDER_ID

# Set the current project
gcloud config set project my-project-id

# Get the current project
gcloud config get-value project

# Delete a project (moves to pending deletion; 30 days to restore)
gcloud projects delete my-project-id

# Undelete a project (within 30 days)
gcloud projects undelete my-project-id

# Get IAM policy for a project
gcloud projects get-iam-policy my-project-id

# Add IAM binding to a project
gcloud projects add-iam-policy-binding my-project-id \
  --member="user:developer@example.com" \
  --role="roles/viewer"

# Remove IAM binding
gcloud projects remove-iam-policy-binding my-project-id \
  --member="user:developer@example.com" \
  --role="roles/viewer"
```

---

## Service Account Management

```bash
# Create a service account
gcloud iam service-accounts create my-sa \
  --display-name="My Service Account" \
  --description="Used by the data pipeline" \
  --project=my-project-id

# List service accounts
gcloud iam service-accounts list --project=my-project-id

# Describe a service account
gcloud iam service-accounts describe my-sa@my-project-id.iam.gserviceaccount.com

# Enable a disabled service account
gcloud iam service-accounts enable my-sa@my-project-id.iam.gserviceaccount.com

# Disable a service account
gcloud iam service-accounts disable my-sa@my-project-id.iam.gserviceaccount.com

# Delete a service account
gcloud iam service-accounts delete my-sa@my-project-id.iam.gserviceaccount.com

# Create a service account key (avoid in production; use Workload Identity instead)
gcloud iam service-accounts keys create sa-key.json \
  --iam-account=my-sa@my-project-id.iam.gserviceaccount.com \
  --key-file-type=json

# List SA keys
gcloud iam service-accounts keys list \
  --iam-account=my-sa@my-project-id.iam.gserviceaccount.com

# Delete an SA key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=my-sa@my-project-id.iam.gserviceaccount.com

# Grant a role to a service account (on a project)
gcloud projects add-iam-policy-binding my-project-id \
  --member="serviceAccount:my-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Grant the token creator role (for impersonation)
gcloud iam service-accounts add-iam-policy-binding my-sa@my-project-id.iam.gserviceaccount.com \
  --member="user:developer@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"

# Grant Workload Identity User (for Kubernetes Workload Identity)
gcloud iam service-accounts add-iam-policy-binding my-sa@my-project-id.iam.gserviceaccount.com \
  --member="serviceAccount:my-project-id.svc.id.goog[my-namespace/my-ksa]" \
  --role="roles/iam.workloadIdentityUser"
```

---

## Workload Identity Federation

```bash
# Create a Workload Identity Pool (for external OIDC providers)
gcloud iam workload-identity-pools create my-github-pool \
  --location=global \
  --description="GitHub Actions Workload Identity Pool" \
  --display-name="GitHub Actions"

# List pools
gcloud iam workload-identity-pools list --location=global

# Create an OIDC provider for GitHub Actions
gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
  --location=global \
  --workload-identity-pool=my-github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='my-org/my-repo'"

# Get the provider resource name (for GitHub Actions workflow)
gcloud iam workload-identity-pools providers describe github-actions-provider \
  --location=global \
  --workload-identity-pool=my-github-pool \
  --format="value(name)"

# Grant the SA token creator role to the external identity
gcloud iam service-accounts add-iam-policy-binding deploy-sa@PROJECT_ID.iam.gserviceaccount.com \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/my-github-pool/attribute.repository/my-org/my-repo" \
  --role="roles/iam.workloadIdentityUser"
```

---

## Output Formatting and Filtering Examples

```bash
# List instances with custom table columns
gcloud compute instances list \
  --format="table(name,status,zone.basename(),machineType.basename():label=TYPE,networkInterfaces[0].networkIP:label=INTERNAL_IP)"

# Get just one field value (for scripting)
PROJECT_ID=$(gcloud config get-value project)
SERVICE_URL=$(gcloud run services describe my-service --region=us-central1 --format="value(status.url)")

# JSON output and parse with jq
gcloud container clusters list --format=json | jq '.[].name'

# Filter running instances and get their names
gcloud compute instances list \
  --filter="status=RUNNING" \
  --format="value(name)"

# Filter by label
gcloud compute instances list \
  --filter="labels.env=prod AND labels.team=platform"

# Sort by creation time (newest first)
gcloud compute instances list \
  --sort-by="~createTime" \
  --limit=10

# YAML output (for Kubernetes-like inspection)
gcloud run services describe my-service \
  --region=us-central1 \
  --format=yaml

# Get specific nested field
gcloud run services describe my-service \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].image)"

# List with pagination tokens (for scripting large result sets)
gcloud compute instances list \
  --limit=100 \
  --page-size=50 \
  --format="value(name)"
```

---

## Enable/Disable APIs

```bash
# Enable a single API
gcloud services enable run.googleapis.com

# Enable multiple APIs at once
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  cloudtasks.googleapis.com \
  pubsub.googleapis.com \
  eventarc.googleapis.com \
  workflows.googleapis.com

# List all enabled APIs
gcloud services list --enabled

# List enabled APIs (filter to a specific service)
gcloud services list --enabled --filter="NAME:run.googleapis.com"

# Disable an API (use with caution — may break running services)
gcloud services disable run.googleapis.com --force

# Check if an API is enabled
gcloud services list --enabled --format="value(NAME)" | grep run.googleapis.com
```

---

## Diagnostics and Help

```bash
# Show SDK diagnostic information
gcloud info

# Run diagnostics (network, auth, etc.)
gcloud info --run-diagnostics

# Get help for a command
gcloud help compute instances create
gcloud compute instances create --help

# List subcommands for a group
gcloud run --help
gcloud compute instances --help

# Reference: filter expression syntax
gcloud topic filters

# Reference: format expression syntax
gcloud topic formats

# Reference: projection expression syntax
gcloud topic projections

# Reference: resource-keys available for a command
gcloud compute instances list --format="json" | head -1 | python3 -m json.tool

# Debug with HTTP logging (shows raw API requests and responses)
gcloud compute instances list --log-http 2>&1 | head -50

# Set verbosity for troubleshooting
gcloud compute instances list --verbosity=debug
```
