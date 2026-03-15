# CI/CD for Containers — CLI

## Cloud Build

### Submit Builds

```bash
# Build and push an image using Cloud Build (simplest form)
gcloud builds submit \
  --tag=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  .

# Build with a specific tag using commit SHA
gcloud builds submit \
  --tag=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:$(git rev-parse --short HEAD) \
  --region=us-central1 \
  .

# Build with a cloudbuild.yaml config file
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1 \
  .

# Build with substitution variables
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1 \
  --substitutions=_ENV=prod,_VERSION=v2.3.1 \
  .

# Build without submitting source (use a pre-existing GCS object)
gcloud builds submit \
  --config=cloudbuild.yaml \
  --no-source \
  --region=us-central1

# Submit build asynchronously (don't wait for completion)
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1 \
  --async \
  .

# Build with a specific machine type
gcloud builds submit \
  --config=cloudbuild.yaml \
  --machine-type=E2_HIGHCPU_8 \
  --region=us-central1 \
  .
```

### List and Monitor Builds

```bash
# List recent builds
gcloud builds list --region=us-central1 --limit=20

# List builds for a specific trigger
gcloud builds list \
  --region=us-central1 \
  --filter="buildTriggerId=TRIGGER_ID"

# List failed builds
gcloud builds list \
  --region=us-central1 \
  --filter="status=FAILURE" \
  --limit=10

# Describe a build (full details)
gcloud builds describe BUILD_ID --region=us-central1

# Stream logs of a running build
gcloud builds log BUILD_ID --region=us-central1 --stream

# Get logs of a completed build
gcloud builds log BUILD_ID --region=us-central1

# Cancel a running build
gcloud builds cancel BUILD_ID --region=us-central1
```

### Build Triggers

```bash
# Create a trigger from GitHub (Cloud Build GitHub App must be installed)
gcloud builds triggers create github \
  --region=us-central1 \
  --repo-owner=my-org \
  --repo-name=my-app \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=my-app-main-push \
  --description="Build on push to main" \
  --substitutions=_ENV=prod

# Create a trigger on tag push (release trigger)
gcloud builds triggers create github \
  --region=us-central1 \
  --repo-owner=my-org \
  --repo-name=my-app \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config=cloudbuild.yaml \
  --name=my-app-release-tag \
  --substitutions=_ENV=prod

# Create a trigger for pull requests (PR preview builds)
gcloud builds triggers create github \
  --region=us-central1 \
  --repo-owner=my-org \
  --repo-name=my-app \
  --pull-request-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=my-app-pr-check \
  --comment-control=COMMENTS_ENABLED_FOR_EXTERNAL_CONTRIBUTORS_ONLY

# Create a trigger from Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
  --region=us-central1 \
  --repo=my-csr-repo \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=my-csr-trigger

# Create a Pub/Sub trigger
gcloud builds triggers create pubsub \
  --region=us-central1 \
  --topic=projects/PROJECT_ID/topics/my-topic \
  --build-config=cloudbuild.yaml \
  --name=my-pubsub-trigger \
  --substitutions=_BUILD_ID='$(body.message.attributes.buildId)'

# Create a webhook trigger
gcloud builds triggers create webhook \
  --region=us-central1 \
  --build-config=cloudbuild.yaml \
  --name=my-webhook-trigger \
  --secret=projects/PROJECT_ID/secrets/webhook-secret/versions/latest

# List triggers
gcloud builds triggers list --region=us-central1

# Describe a trigger
gcloud builds triggers describe my-app-main-push --region=us-central1

# Manually run a trigger
gcloud builds triggers run my-app-main-push \
  --region=us-central1 \
  --branch=main

# Update a trigger
gcloud builds triggers update my-app-main-push \
  --region=us-central1 \
  --build-config=cloudbuild-updated.yaml

# Delete a trigger
gcloud builds triggers delete my-app-main-push --region=us-central1

# Enable/disable a trigger
gcloud builds triggers enable my-app-main-push --region=us-central1
gcloud builds triggers disable my-app-main-push --region=us-central1
```

### Example cloudbuild.yaml Files

**Build, test, and push Docker image**:

```yaml
# cloudbuild.yaml
substitutions:
  _IMAGE: us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/my-app
  _REGION: us-central1

steps:
  # Run unit tests
  - name: 'golang:1.22-alpine'
    id: 'unit-tests'
    entrypoint: 'go'
    args: ['test', '-v', '-coverprofile=coverage.out', './...']
    env: ['CGO_ENABLED=0']

  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build'
    waitFor: ['unit-tests']
    args:
      - 'build'
      - '-t'
      - '${_IMAGE}:$COMMIT_SHA'
      - '-t'
      - '${_IMAGE}:latest'
      - '--cache-from'
      - '${_IMAGE}:latest'
      - '--build-arg'
      - 'BUILD_DATE=$BUILD_ID'
      - '.'

  # Scan image for vulnerabilities before pushing
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'scan'
    waitFor: ['build']
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud artifacts docker images scan \
          ${_IMAGE}:$COMMIT_SHA \
          --remote \
          --format=json | tee /workspace/scan-results.json

  # Push the image (only after successful scan)
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push'
    waitFor: ['scan']
    args: ['push', '--all-tags', '${_IMAGE}']

  # Create Cloud Deploy release
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'create-release'
    waitFor: ['push']
    entrypoint: 'gcloud'
    args:
      - 'deploy'
      - 'releases'
      - 'create'
      - 'release-$SHORT_SHA'
      - '--delivery-pipeline=my-app-pipeline'
      - '--region=${_REGION}'
      - '--images=my-app=${_IMAGE}:$COMMIT_SHA'

images:
  - '${_IMAGE}:$COMMIT_SHA'
  - '${_IMAGE}:latest'

options:
  machineType: E2_STANDARD_4
  logging: CLOUD_LOGGING_ONLY

timeout: '1800s'
```

**Multi-service build with parallel steps**:

```yaml
# cloudbuild.yaml
steps:
  # Build frontend and backend in parallel
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build-frontend'
    waitFor: ['-']   # Start immediately
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/frontend:$COMMIT_SHA', './frontend']

  - name: 'gcr.io/cloud-builders/docker'
    id: 'build-backend'
    waitFor: ['-']   # Start immediately (parallel with build-frontend)
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/backend:$COMMIT_SHA', './backend']

  # Push both images after builds complete
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push-frontend'
    waitFor: ['build-frontend']
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/frontend:$COMMIT_SHA']

  - name: 'gcr.io/cloud-builders/docker'
    id: 'push-backend'
    waitFor: ['build-backend']
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/backend:$COMMIT_SHA']

  # Create Cloud Deploy release after both images are pushed
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    waitFor: ['push-frontend', 'push-backend']
    entrypoint: 'gcloud'
    args:
      - 'deploy', 'releases', 'create', 'release-$SHORT_SHA'
      - '--delivery-pipeline=my-app-pipeline'
      - '--region=us-central1'
      - '--images=frontend=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/frontend:$COMMIT_SHA,backend=us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/backend:$COMMIT_SHA'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/frontend:$COMMIT_SHA'
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/my-repo/backend:$COMMIT_SHA'
```

---

## Cloud Deploy

### Register Pipelines and Targets

```bash
# Register/update a delivery pipeline and targets from YAML files
gcloud deploy apply \
  --file=delivery-pipeline.yaml \
  --region=us-central1

gcloud deploy apply \
  --file=targets.yaml \
  --region=us-central1

# Apply multiple files at once
gcloud deploy apply \
  --file=clouddeploy.yaml \
  --region=us-central1
# (clouddeploy.yaml can contain multiple resources separated by ---)

# List delivery pipelines
gcloud deploy delivery-pipelines list --region=us-central1

# Describe a delivery pipeline
gcloud deploy delivery-pipelines describe my-app-pipeline --region=us-central1

# List targets
gcloud deploy targets list --region=us-central1

# Describe a target
gcloud deploy targets describe prod --region=us-central1

# Delete a pipeline
gcloud deploy delivery-pipelines delete my-app-pipeline \
  --region=us-central1 \
  --force    # also deletes releases and rollouts

# Delete a target
gcloud deploy targets delete prod --region=us-central1
```

### Create and Manage Releases

```bash
# Create a release from Skaffold config with a specific image
gcloud deploy releases create release-v1-2-3 \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1 \
  --images=my-app=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v1.2.3

# Create a release with multiple images
gcloud deploy releases create release-$(git rev-parse --short HEAD) \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1 \
  --images=frontend=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/frontend:$SHA,backend=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/backend:$SHA

# Create release and immediately deploy to first target
gcloud deploy releases create release-v1-2-3 \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1 \
  --images=my-app=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v1.2.3 \
  --to-target=dev \
  --annotations=git-commit=abc123,jira-ticket=PROJ-456

# List releases in a pipeline
gcloud deploy releases list \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1

# Describe a release
gcloud deploy releases describe release-v1-2-3 \
  --delivery-pipeline=my-app-pipeline \
  --region=us-central1
```

### Manage Rollouts

```bash
# Promote a release to the next target in the pipeline
gcloud deploy releases promote \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1 \
  --to-target=staging    # optional: specify target if not next in sequence

# Promote with description
gcloud deploy releases promote \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1 \
  --rollout-description="Promoted after staging validation"

# List rollouts for a release
gcloud deploy rollouts list \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Describe a rollout
gcloud deploy rollouts describe ROLLOUT_NAME \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Approve a rollout (for targets requiring approval)
gcloud deploy rollouts approve ROLLOUT_NAME \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Reject a rollout
gcloud deploy rollouts reject ROLLOUT_NAME \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Cancel a running rollout
gcloud deploy rollouts cancel ROLLOUT_NAME \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Retry a failed rollout
gcloud deploy rollouts retry ROLLOUT_NAME \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --region=us-central1

# Rollback: deploy the previous successful release to a target
gcloud deploy rollouts list \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-2 \   # previous release
  --region=us-central1

gcloud deploy releases promote \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-2 \
  --region=us-central1 \
  --to-target=prod \
  --rollout-description="Rollback to v1.2.2 due to prod issue"
```

### Cloud Deploy Job Runs (Verification)

```bash
# List job runs for a rollout (verify, predeploy, postdeploy)
gcloud deploy job-runs list \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --rollout=ROLLOUT_NAME \
  --region=us-central1

# Describe a job run (see verification results)
gcloud deploy job-runs describe JOB_RUN_ID \
  --delivery-pipeline=my-app-pipeline \
  --release=release-v1-2-3 \
  --rollout=ROLLOUT_NAME \
  --region=us-central1
```

---

## Skaffold CLI

Skaffold is a separate CLI tool, not part of gcloud.

```bash
# Install Skaffold
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
chmod +x skaffold
sudo mv skaffold /usr/local/bin

# Or install via gcloud (if available as component)
gcloud components install skaffold

# Verify installation
skaffold version

# Initialize Skaffold config from existing Kubernetes manifests
skaffold init --generate-manifests

# Local development mode (file watch + auto-rebuild + deploy)
skaffold dev \
  --port-forward \
  --trigger=polling

# Build images and push to registry
skaffold build \
  --file-output=build-artifacts.json \
  --tag=$(git rev-parse --short HEAD)

# Render Kubernetes manifests with image substitution
skaffold render \
  --build-artifacts=build-artifacts.json \
  --output=rendered-manifests.yaml \
  --profile=prod

# Deploy pre-rendered manifests
skaffold deploy \
  --build-artifacts=build-artifacts.json \
  --profile=prod

# Run (build + push + deploy) with a specific profile
skaffold run \
  --profile=staging \
  --tag=v1.2.3

# Run post-deployment verification
skaffold verify \
  --build-artifacts=build-artifacts.json \
  --profile=prod

# Clean up resources deployed by Skaffold
skaffold delete --profile=dev

# Debug mode (attach debugger to running containers)
skaffold debug \
  --port-forward \
  --profile=dev

# Build for a specific platform
skaffold build \
  --platform=linux/amd64 \
  --tag=$(git rev-parse --short HEAD)

# Use Cloud Build as the builder (instead of local Docker)
# In skaffold.yaml: build.googleCloudBuild.projectId = PROJECT_ID
skaffold build --profile=cloudbuild-profile
```

---

## Cloud Build Private Pools

```bash
# Create a private pool (dedicated build workers in your VPC)
gcloud builds worker-pools create my-private-pool \
  --region=us-central1 \
  --peered-network=projects/PROJECT_ID/global/networks/my-vpc \
  --worker-machine-type=e2-standard-4 \
  --worker-disk-size=100

# List private pools
gcloud builds worker-pools list --region=us-central1

# Describe a pool
gcloud builds worker-pools describe my-private-pool --region=us-central1

# Use a private pool in a build trigger
gcloud builds triggers create github \
  --region=us-central1 \
  --repo-owner=my-org \
  --repo-name=my-app \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --worker-pool=projects/PROJECT_ID/locations/us-central1/workerPools/my-private-pool \
  --name=my-private-build

# Delete a pool
gcloud builds worker-pools delete my-private-pool --region=us-central1
```
