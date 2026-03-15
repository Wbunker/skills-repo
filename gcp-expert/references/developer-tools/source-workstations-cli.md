# Source Repositories & Cloud Workstations — CLI

## Cloud Source Repositories

### Repository Management

```bash
# Enable Cloud Source Repositories API
gcloud services enable sourcerepo.googleapis.com

# Create a new repository
gcloud source repos create my-app-repo \
  --project=my-project-id

# List repositories in the project
gcloud source repos list --project=my-project-id

# Describe a repository
gcloud source repos describe my-app-repo --project=my-project-id

# Clone a repository (authenticates via gcloud automatically)
gcloud source repos clone my-app-repo \
  --project=my-project-id \
  ~/projects/my-app-repo

# Clone and set default upstream
gcloud source repos clone my-app-repo \
  --project=my-project-id

# Add a Cloud Source Repository as a remote to an existing git repo
git remote add origin \
  https://source.developers.google.com/p/my-project-id/r/my-app-repo

# Configure git credential helper for CSR (HTTPS auth)
git config --global credential.https://source.developers.google.com.helper gcloud.sh

# Push initial code to the repository
git push -u origin main

# Delete a repository
gcloud source repos delete my-app-repo \
  --project=my-project-id \
  --quiet
```

### Repository Mirroring

Mirroring is configured in the GCP Console (Source Repositories > Create Repository > "Connect external repository"). The CLI does not directly support creating mirror configurations, but you can manage permissions:

```bash
# Add IAM policy for a developer on a specific repo
gcloud source repos add-iam-policy-binding my-app-repo \
  --project=my-project-id \
  --member="user:developer@example.com" \
  --role="roles/source.writer"

# Grant reader access to a service account
gcloud source repos add-iam-policy-binding my-app-repo \
  --project=my-project-id \
  --member="serviceAccount:my-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/source.reader"

# Get IAM policy for a repository
gcloud source repos get-iam-policy my-app-repo \
  --project=my-project-id

# Remove an IAM binding
gcloud source repos remove-iam-policy-binding my-app-repo \
  --project=my-project-id \
  --member="user:ex-developer@example.com" \
  --role="roles/source.writer"
```

### Cloud Build Trigger from CSR

```bash
# Create a Cloud Build trigger on CSR branch push
gcloud builds triggers create cloud-source-repositories \
  --region=us-central1 \
  --repo=my-app-repo \
  --repo-type=CLOUD_SOURCE_REPOSITORIES \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=my-project-id \
  --name=my-app-csr-trigger

# Create trigger on tag push
gcloud builds triggers create cloud-source-repositories \
  --region=us-central1 \
  --repo=my-app-repo \
  --repo-type=CLOUD_SOURCE_REPOSITORIES \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config=cloudbuild-release.yaml \
  --project=my-project-id \
  --name=my-app-release-trigger

# List triggers
gcloud builds triggers list --region=us-central1 --project=my-project-id

# Manually run a CSR trigger against a specific branch
gcloud builds triggers run my-app-csr-trigger \
  --region=us-central1 \
  --branch=main

# Delete a trigger
gcloud builds triggers delete my-app-csr-trigger \
  --region=us-central1 \
  --project=my-project-id
```

---

## Cloud Workstations

### Workstation Clusters

```bash
# Enable Cloud Workstations API
gcloud services enable workstations.googleapis.com

# Create a workstation cluster (provisions GKE infrastructure in your VPC; takes ~10 min)
gcloud workstations clusters create my-dev-cluster \
  --location=us-central1 \
  --network=projects/my-project-id/global/networks/my-vpc \
  --subnetwork=projects/my-project-id/regions/us-central1/subnetworks/my-subnet \
  --project=my-project-id

# Create a cluster with private cluster (no public IP on GKE nodes)
gcloud workstations clusters create my-private-cluster \
  --location=us-central1 \
  --network=projects/my-project-id/global/networks/my-vpc \
  --subnetwork=projects/my-project-id/regions/us-central1/subnetworks/my-subnet \
  --enable-private-cluster \
  --project=my-project-id

# List clusters
gcloud workstations clusters list --location=us-central1 --project=my-project-id

# Describe a cluster
gcloud workstations clusters describe my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id

# Delete a cluster (must delete all workstations first)
gcloud workstations clusters delete my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id
```

### Workstation Configurations

```bash
# Create a standard developer configuration
gcloud workstations configs create standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --machine-type=e2-standard-4 \
  --pd-disk-size=50 \
  --pd-disk-type=pd-ssd \
  --container-predefined-image=codeoss \
  --idle-timeout=7200s \
  --running-timeout=43200s \
  --project=my-project-id

# Available predefined images:
# codeoss              - Code OSS (VS Code open source) base editor
# clion                - JetBrains CLion
# goland               - JetBrains GoLand
# intellij-ultimate    - JetBrains IntelliJ IDEA Ultimate
# phpstorm             - JetBrains PhpStorm
# pycharm              - JetBrains PyCharm Professional
# rider                - JetBrains Rider
# rubymine             - JetBrains RubyMine
# webstorm             - JetBrains WebStorm

# Create a configuration with a custom container image
gcloud workstations configs create ml-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --machine-type=n1-standard-8 \
  --pd-disk-size=100 \
  --pd-disk-type=pd-ssd \
  --container-custom-image=us-central1-docker.pkg.dev/my-project/dev-images/ml-workstation:latest \
  --idle-timeout=3600s \
  --running-timeout=86400s \
  --project=my-project-id \
  --service-account=workstation-sa@my-project-id.iam.gserviceaccount.com

# Create a configuration with GPU
gcloud workstations configs create gpu-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --machine-type=n1-standard-8 \
  --accelerator-type=nvidia-tesla-t4 \
  --accelerator-count=1 \
  --pd-disk-size=100 \
  --pd-disk-type=pd-ssd \
  --container-predefined-image=codeoss \
  --project=my-project-id

# Create an ephemeral configuration (no persistent disk)
gcloud workstations configs create ephemeral-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --machine-type=e2-standard-4 \
  --container-predefined-image=codeoss \
  --no-persistent-directories \
  --project=my-project-id

# List configurations
gcloud workstations configs list \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id

# Describe a configuration
gcloud workstations configs describe standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id

# Update a configuration (e.g., change machine type)
gcloud workstations configs update standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --machine-type=e2-standard-8 \
  --project=my-project-id

# Delete a configuration
gcloud workstations configs delete standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id

# Grant IAM access so users can use a configuration
gcloud workstations configs add-iam-policy-binding standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id \
  --member="user:developer@example.com" \
  --role="roles/workstations.user"
```

### Workstation Instance Management

```bash
# Create a workstation instance for a specific user
gcloud workstations create my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id \
  --labels=developer=johndoe,team=backend

# List all workstations
gcloud workstations list \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# List workstations across all configs in a cluster
gcloud workstations list \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id

# Describe a workstation (see state, URL)
gcloud workstations describe my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# Start a workstation
gcloud workstations start my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# Stop a workstation
gcloud workstations stop my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# Delete a workstation
gcloud workstations delete my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# Get a workstation access URL
gcloud workstations start-access my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id
```

### SSH and TCP Tunnel

```bash
# SSH into a workstation
gcloud workstations ssh my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# SSH with port forwarding (forward workstation port 8080 to local 8080)
gcloud workstations ssh my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id \
  -- -L 8080:localhost:8080

# Start a TCP tunnel to a port on the workstation (for VS Code Remote-SSH)
gcloud workstations start-tcp-tunnel my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id \
  --local-host-port=localhost:22 \
  --remote-port=22

# Generate SSH config for use with VS Code Remote-SSH
# Add to ~/.ssh/config:
# Host my-workstation
#   User user
#   ProxyCommand gcloud workstations start-tcp-tunnel my-workstation \
#     --cluster=my-dev-cluster \
#     --config=standard-dev \
#     --location=us-central1 \
#     --project=my-project-id \
#     --local-host-port=- \
#     --remote-port=22
```

### Workstation IAM

```bash
# Grant workstation admin (manage all workstations in config)
gcloud workstations configs add-iam-policy-binding standard-dev \
  --cluster=my-dev-cluster \
  --location=us-central1 \
  --project=my-project-id \
  --member="serviceAccount:workstation-admin-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/workstations.admin"

# Grant workstation user access to a specific workstation
gcloud workstations add-iam-policy-binding my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id \
  --member="user:developer@example.com" \
  --role="roles/workstations.user"

# Get IAM policy for a workstation
gcloud workstations get-iam-policy my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id

# Revoke user access
gcloud workstations remove-iam-policy-binding my-workstation \
  --cluster=my-dev-cluster \
  --config=standard-dev \
  --location=us-central1 \
  --project=my-project-id \
  --member="user:ex-developer@example.com" \
  --role="roles/workstations.user"
```
