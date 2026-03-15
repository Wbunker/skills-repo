# Artifact Registry — CLI

## Repository Management

```bash
# Enable the Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Create a Docker repository (standard)
gcloud artifacts repositories create my-docker-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Production Docker images" \
  --immutable-tags \
  --project=PROJECT_ID

# Create a Docker repository with CMEK
gcloud artifacts repositories create my-secure-repo \
  --repository-format=docker \
  --location=us-central1 \
  --kms-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key

# Create a Maven repository
gcloud artifacts repositories create my-maven-repo \
  --repository-format=maven \
  --location=us-central1 \
  --description="Internal Java packages" \
  --maven-snapshot-version-policy=RELEASE

# Create an npm repository
gcloud artifacts repositories create my-npm-repo \
  --repository-format=npm \
  --location=us-central1

# Create a Python repository
gcloud artifacts repositories create my-python-repo \
  --repository-format=python \
  --location=us-central1

# Create a Helm repository
gcloud artifacts repositories create my-helm-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Helm chart OCI repository"

# Create a generic repository
gcloud artifacts repositories create my-binaries-repo \
  --repository-format=generic \
  --location=us-central1

# Create a REMOTE Docker Hub repository
gcloud artifacts repositories create docker-hub-cache \
  --repository-format=docker \
  --location=us-central1 \
  --mode=REMOTE_REPOSITORY \
  --remote-repo-config-desc="Docker Hub mirror" \
  --remote-docker-repo=DOCKER_HUB

# Create a REMOTE PyPI repository
gcloud artifacts repositories create pypi-cache \
  --repository-format=python \
  --location=us-central1 \
  --mode=REMOTE_REPOSITORY \
  --remote-repo-config-desc="PyPI mirror" \
  --remote-python-repo=PYPI

# Create a REMOTE npm repository
gcloud artifacts repositories create npm-cache \
  --repository-format=npm \
  --location=us-central1 \
  --mode=REMOTE_REPOSITORY \
  --remote-repo-config-desc="npm registry mirror" \
  --remote-npm-repo=NPMJS

# Create a VIRTUAL repository
gcloud artifacts repositories create my-virtual-docker \
  --repository-format=docker \
  --location=us-central1 \
  --mode=VIRTUAL_REPOSITORY \
  --upstream-policy-file=upstream-policy.json
# upstream-policy.json:
# [{"id": "internal", "repository": "projects/P/locations/us-central1/repositories/my-docker-repo", "priority": 100},
#  {"id": "hub-cache", "repository": "projects/P/locations/us-central1/repositories/docker-hub-cache", "priority": 50}]

# List repositories
gcloud artifacts repositories list --location=us-central1

# List repositories in all locations
gcloud artifacts repositories list --location=-

# Describe a repository
gcloud artifacts repositories describe my-docker-repo \
  --location=us-central1

# Delete a repository (must be empty or use --delete-contents)
gcloud artifacts repositories delete my-docker-repo \
  --location=us-central1 \
  --quiet
```

---

## Docker Authentication and Push/Pull

```bash
# Configure Docker credential helper for a specific region
gcloud auth configure-docker us-central1-docker.pkg.dev

# Configure Docker for multiple regions
gcloud auth configure-docker us-central1-docker.pkg.dev,europe-west1-docker.pkg.dev,asia-east1-docker.pkg.dev

# Build and push a Docker image
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.2.3 .
docker push us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.2.3

# Tag an existing local image and push
docker tag my-local-image:latest us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:latest
docker push us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:latest

# Pull an image
docker pull us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.2.3

# Pull by digest (immutable reference)
docker pull us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app@sha256:abc123...
```

---

## Docker Image Management

```bash
# List images in a repository
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo

# List images with vulnerability summary
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo \
  --show-occurrences \
  --occurrence-filter=kind="VULNERABILITY"

# List all tags for a specific image
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app \
  --include-tags

# Describe a specific image (with digests, tags, and metadata)
gcloud artifacts docker images describe \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.2.3

# Describe by digest
gcloud artifacts docker images describe \
  "us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app@sha256:abc123..."

# Delete a specific image tag
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:old-tag \
  --quiet

# Delete a specific digest (and all its tags)
gcloud artifacts docker images delete \
  "us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app@sha256:abc123..." \
  --delete-tags \
  --quiet

# Copy an image from gcr.io to Artifact Registry
gcloud artifacts docker images copy \
  gcr.io/PROJECT_ID/old-image:latest \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/old-image:latest
```

---

## Package Management (Non-Docker)

```bash
# List packages in a repository
gcloud artifacts packages list \
  --repository=my-maven-repo \
  --location=us-central1

# Describe a package
gcloud artifacts packages describe com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1

# Delete a package (all versions)
gcloud artifacts packages delete com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1 \
  --quiet

# List versions of a package
gcloud artifacts versions list \
  --package=com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1

# Describe a specific version
gcloud artifacts versions describe 1.2.3 \
  --package=com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1

# Delete a specific version
gcloud artifacts versions delete 0.9.0-SNAPSHOT \
  --package=com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1 \
  --quiet

# Upload a generic file
gcloud artifacts generic upload \
  --repository=my-binaries-repo \
  --location=us-central1 \
  --package=my-binary \
  --version=1.0.0 \
  --source=./my-binary-linux-amd64

# Download a generic file
gcloud artifacts generic download \
  --repository=my-binaries-repo \
  --location=us-central1 \
  --package=my-binary \
  --version=1.0.0 \
  --destination=./
```

---

## Tags

```bash
# List all tags for an image
gcloud artifacts tags list \
  --package=my-app \
  --version=sha256:abc123... \
  --repository=my-docker-repo \
  --location=us-central1

# Create a tag on a specific digest
gcloud artifacts tags create stable \
  --package=my-app \
  --version=sha256:abc123... \
  --repository=my-docker-repo \
  --location=us-central1

# Delete a tag
gcloud artifacts tags delete stable \
  --package=my-app \
  --repository=my-docker-repo \
  --location=us-central1
```

---

## Vulnerability Scanning

```bash
# List vulnerabilities for a specific image
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:v1.2.3 \
  --show-occurrences \
  --occurrence-filter='kind="VULNERABILITY"'

# Get vulnerability summary using Container Analysis
gcloud artifacts vulnerabilities list \
  --resource=https://us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app@sha256:abc123...

# Scan a local image before pushing (on-demand scan via Cloud Build step)
# In cloudbuild.yaml:
# - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
#   entrypoint: 'gcloud'
#   args: ['artifacts', 'docker', 'images', 'scan',
#          'us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/my-app:$SHORT_SHA',
#          '--remote',
#          '--format=json']

# Filter images with CRITICAL vulnerabilities
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo \
  --show-occurrences \
  --occurrence-filter='kind="VULNERABILITY" AND vulnerability.severity="CRITICAL"'

# Enable continuous scanning on a repository (rescans daily)
gcloud artifacts repositories update my-docker-repo \
  --location=us-central1 \
  --update-labels=scanning=enabled
# Note: continuous scanning is enabled via the Artifact Analysis API settings
gcloud services enable containeranalysis.googleapis.com
```

---

## Cleanup Policies

```bash
# Set a cleanup policy on a repository
gcloud artifacts repositories set-cleanup-policies my-docker-repo \
  --location=us-central1 \
  --policy=cleanup-policy.json

# cleanup-policy.json example:
# [
#   {
#     "name": "delete-untagged-old",
#     "action": {"type": "Delete"},
#     "condition": {
#       "tagState": "UNTAGGED",
#       "olderThan": "7d"
#     }
#   },
#   {
#     "name": "keep-recent-releases",
#     "action": {"type": "Keep"},
#     "mostRecentVersions": {
#       "keepCount": 10,
#       "packageNamePrefixes": ["my-app"]
#     }
#   },
#   {
#     "name": "delete-dev-tags-old",
#     "action": {"type": "Delete"},
#     "condition": {
#       "tagState": "TAGGED",
#       "tagPrefixes": ["dev-", "branch-"],
#       "olderThan": "1d"
#     }
#   }
# ]

# List cleanup policies for a repository
gcloud artifacts repositories list-cleanup-policies my-docker-repo \
  --location=us-central1

# Delete cleanup policies
gcloud artifacts repositories delete-cleanup-policies my-docker-repo \
  --location=us-central1 \
  --policy=delete-untagged-old
```

---

## IAM for Artifact Registry

```bash
# Grant reader access to a specific repository (for GKE/Cloud Run service accounts)
gcloud artifacts repositories add-iam-policy-binding my-docker-repo \
  --location=us-central1 \
  --member="serviceAccount:my-gke-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"

# Grant writer access for CI/CD service account
gcloud artifacts repositories add-iam-policy-binding my-docker-repo \
  --location=us-central1 \
  --member="serviceAccount:cloudbuild-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Get IAM policy for a repository
gcloud artifacts repositories get-iam-policy my-docker-repo \
  --location=us-central1

# Grant access to all Compute Engine default service accounts in an org
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"
```

---

## gcr.io Migration

```bash
# Enable gcr.io redirect to Artifact Registry
gcloud artifacts settings enable-upgrade-redirection \
  --project=PROJECT_ID

# Disable gcr.io redirect
gcloud artifacts settings disable-upgrade-redirection \
  --project=PROJECT_ID

# Check gcr.io redirect status
gcloud artifacts settings describe --project=PROJECT_ID

# Copy an image from gcr.io to Artifact Registry using gcrane (faster for bulk)
# Install gcrane: go install github.com/google/go-containerregistry/cmd/gcrane@latest
gcrane copy gcr.io/PROJECT_ID/IMAGE:TAG \
  us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/IMAGE:TAG

# Bulk copy all images from gcr.io to Artifact Registry
gcrane ls gcr.io/PROJECT_ID | while read image; do
  gcrane copy "gcr.io/PROJECT_ID/$image" \
    "us-central1-docker.pkg.dev/PROJECT_ID/my-docker-repo/$image"
done
```
