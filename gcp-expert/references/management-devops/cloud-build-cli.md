# Cloud Build & Cloud Deploy — CLI Reference

---

## Cloud Build

### Submitting Builds

```bash
# Submit a build using cloudbuild.yaml in current directory
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=my-project

# Submit with source directory (packages and uploads source)
gcloud builds submit ./app \
  --config=cloudbuild.yaml \
  --project=my-project

# Submit and wait for completion (synchronous)
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=my-project \
  --async=false

# Submit with substitution variables
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=my-api,_REGION=us-central1,SHORT_SHA=$(git rev-parse --short HEAD) \
  --project=my-project

# Submit a simple Docker build without cloudbuild.yaml
gcloud builds submit \
  --tag=us-central1-docker.pkg.dev/my-project/my-repo/my-image:latest \
  ./app \
  --project=my-project

# Submit build from GCS source archive
gcloud builds submit \
  --no-source \
  --config=cloudbuild.yaml \
  --gcs-source-staging-dir=gs://my-build-staging/source \
  --project=my-project
```

### Listing and Describing Builds

```bash
# List recent builds
gcloud builds list \
  --project=my-project \
  --limit=20

# List builds for a specific trigger
gcloud builds list \
  --filter="trigger_id=my-trigger-id" \
  --project=my-project

# List running builds only
gcloud builds list \
  --filter="status=WORKING" \
  --project=my-project

# Describe a build (full details)
gcloud builds describe BUILD_ID \
  --project=my-project

# Stream build logs
gcloud builds log BUILD_ID \
  --project=my-project

# Stream logs and follow (--stream flag)
gcloud builds log BUILD_ID \
  --stream \
  --project=my-project

# Cancel a running build
gcloud builds cancel BUILD_ID \
  --project=my-project
```

### Build Triggers

```bash
# Create a trigger for push to branch (GitHub)
gcloud builds triggers create github \
  --name=build-on-main \
  --repo-name=my-repo \
  --repo-owner=my-github-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=my-project

# Create a trigger for push to any feature branch
gcloud builds triggers create github \
  --name=build-on-feature \
  --repo-name=my-repo \
  --repo-owner=my-github-org \
  --branch-pattern="^feature/.*$" \
  --build-config=cloudbuild.yaml \
  --project=my-project

# Create a trigger for tag push (release builds)
gcloud builds triggers create github \
  --name=release-on-tag \
  --repo-name=my-repo \
  --repo-owner=my-github-org \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config=cloudbuild.yaml \
  --included-files="src/**,Dockerfile" \
  --project=my-project

# Create a trigger for pull requests
gcloud builds triggers create github \
  --name=pr-check \
  --repo-name=my-repo \
  --repo-owner=my-github-org \
  --pull-request-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --comment-control=COMMENTS_ENABLED_FOR_EXTERNAL_CONTRIBUTORS_ONLY \
  --project=my-project

# Create a manual trigger
gcloud builds triggers create manual \
  --name=manual-deploy \
  --build-config=cloudbuild.yaml \
  --substitutions=_ENV=production \
  --project=my-project

# Create a trigger for Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
  --name=csr-main-build \
  --repo=my-repo \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=my-project

# List triggers
gcloud builds triggers list --project=my-project

# Describe a trigger
gcloud builds triggers describe build-on-main --project=my-project

# Manually run a trigger
gcloud builds triggers run build-on-main \
  --branch=main \
  --project=my-project

# Run a trigger at a specific commit
gcloud builds triggers run build-on-main \
  --sha=abc123def456 \
  --project=my-project

# Update a trigger (e.g., update build config path)
gcloud builds triggers update build-on-main \
  --build-config=ci/cloudbuild-prod.yaml \
  --project=my-project

# Enable/disable a trigger
gcloud builds triggers disable build-on-main --project=my-project
gcloud builds triggers enable build-on-main --project=my-project

# Delete a trigger
gcloud builds triggers delete build-on-main --project=my-project
```

### Worker Pools (Private Pools)

```bash
# Create a private worker pool
gcloud builds worker-pools create my-private-pool \
  --region=us-central1 \
  --worker-machine-type=e2-standard-4 \
  --worker-disk-size=100GB \
  --no-public-egress \
  --network=projects/my-project/global/networks/my-vpc \
  --project=my-project

# Create private pool with peered network (access internal resources)
gcloud builds worker-pools create private-pool-peered \
  --region=us-central1 \
  --worker-machine-type=n1-highcpu-8 \
  --worker-disk-size=200GB \
  --network=projects/my-project/global/networks/build-network \
  --project=my-project

# List worker pools
gcloud builds worker-pools list \
  --region=us-central1 \
  --project=my-project

# Describe a worker pool
gcloud builds worker-pools describe my-private-pool \
  --region=us-central1 \
  --project=my-project

# Delete a worker pool
gcloud builds worker-pools delete my-private-pool \
  --region=us-central1 \
  --project=my-project

# Use a private pool in a build submission
gcloud builds submit \
  --config=cloudbuild.yaml \
  --worker-pool=projects/my-project/locations/us-central1/workerPools/my-private-pool \
  --project=my-project
```

---

## Cloud Deploy

### Delivery Pipelines

```bash
# Apply delivery pipeline and targets from YAML file
gcloud deploy apply \
  --file=clouddeploy.yaml \
  --region=us-central1 \
  --project=my-project

# List delivery pipelines
gcloud deploy delivery-pipelines list \
  --region=us-central1 \
  --project=my-project

# Describe a delivery pipeline
gcloud deploy delivery-pipelines describe my-pipeline \
  --region=us-central1 \
  --project=my-project

# Delete a delivery pipeline
gcloud deploy delivery-pipelines delete my-pipeline \
  --region=us-central1 \
  --force \
  --project=my-project
```

### Targets

```bash
# List targets
gcloud deploy targets list \
  --region=us-central1 \
  --project=my-project

# Describe a target
gcloud deploy targets describe production \
  --region=us-central1 \
  --project=my-project

# Delete a target
gcloud deploy targets delete production \
  --region=us-central1 \
  --project=my-project
```

### Releases

```bash
# Create a release (deploys to first target in pipeline)
gcloud deploy releases create release-$(date +%Y%m%d-%H%M%S) \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --images=my-service=us-central1-docker.pkg.dev/my-project/my-repo/my-service:abc1234 \
  --project=my-project

# Create a release with a Skaffold build output file
gcloud deploy releases create release-v1-2-0 \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --build-artifacts=artifacts.json \
  --project=my-project

# Create a release with annotations
gcloud deploy releases create release-v1-2-0 \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --images=my-service=us-central1-docker.pkg.dev/my-project/my-repo/my-service:v1.2.0 \
  --annotations=commit-sha=$(git rev-parse HEAD),deployed-by=cloudbuild \
  --project=my-project

# Create a release and immediately promote past first target
gcloud deploy releases create release-v1-2-0 \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --images=my-service=us-central1-docker.pkg.dev/my-project/my-repo/my-service:v1.2.0 \
  --to-target=staging \
  --project=my-project

# List releases for a pipeline
gcloud deploy releases list \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --project=my-project

# Describe a release
gcloud deploy releases describe release-v1-2-0 \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --project=my-project
```

### Rollouts

```bash
# List rollouts for a release
gcloud deploy rollouts list \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Describe a rollout
gcloud deploy rollouts describe my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Advance a canary rollout to next phase
gcloud deploy rollouts advance my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Approve a rollout (for targets requiring approval)
gcloud deploy rollouts approve my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Reject a rollout
gcloud deploy rollouts reject my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Cancel a rollout
gcloud deploy rollouts cancel my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --project=my-project

# Retry a failed rollout job
gcloud deploy rollouts retry-job my-rollout \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --phase-id=stable \
  --job-id=deploy \
  --project=my-project

# Rollback a target to a previous release
gcloud deploy rollouts create \
  --delivery-pipeline=my-pipeline \
  --region=us-central1 \
  --release=previous-good-release \
  --to-target=production \
  --project=my-project
```

### Promoting Releases

```bash
# Promote a release from one target to the next in the pipeline
gcloud deploy releases promote \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --to-target=staging \
  --project=my-project

# Promote to production (will pend approval if required)
gcloud deploy releases promote \
  --delivery-pipeline=my-pipeline \
  --release=release-v1-2-0 \
  --region=us-central1 \
  --to-target=production \
  --project=my-project
```

---

## Artifact Registry

```bash
# Create a Docker repository
gcloud artifacts repositories create my-docker-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for my-project" \
  --project=my-project

# Create a Maven repository
gcloud artifacts repositories create my-maven-repo \
  --repository-format=maven \
  --location=us-central1 \
  --project=my-project

# Create an npm repository
gcloud artifacts repositories create my-npm-repo \
  --repository-format=npm \
  --location=us-central1 \
  --project=my-project

# Create a Remote repository (proxy Docker Hub)
gcloud artifacts repositories create dockerhub-proxy \
  --repository-format=docker \
  --location=us-central1 \
  --mode=remote-repository \
  --remote-repo-config-desc="Docker Hub proxy" \
  --remote-docker-repo=DOCKER_HUB \
  --project=my-project

# Create a virtual repository
gcloud artifacts repositories create virtual-docker \
  --repository-format=docker \
  --location=us-central1 \
  --mode=virtual-repository \
  --upstream-policy=priority=100,id=my-docker-repo,repository=projects/my-project/locations/us-central1/repositories/my-docker-repo \
  --upstream-policy=priority=50,id=dockerhub-proxy,repository=projects/my-project/locations/us-central1/repositories/dockerhub-proxy \
  --project=my-project

# Create repository with CMEK
gcloud artifacts repositories create encrypted-repo \
  --repository-format=docker \
  --location=us-central1 \
  --kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --project=my-project

# List repositories
gcloud artifacts repositories list \
  --location=us-central1 \
  --project=my-project

# Describe a repository
gcloud artifacts repositories describe my-docker-repo \
  --location=us-central1 \
  --project=my-project

# Delete a repository
gcloud artifacts repositories delete my-docker-repo \
  --location=us-central1 \
  --project=my-project

# Configure Docker authentication for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Configure Docker auth for multiple regions
gcloud auth configure-docker \
  us-central1-docker.pkg.dev,us-east1-docker.pkg.dev,europe-west1-docker.pkg.dev

# List Docker images in a repository
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/my-project/my-docker-repo \
  --project=my-project

# List images with versions/digests
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/my-project/my-docker-repo \
  --include-tags \
  --project=my-project

# List packages (for non-Docker repos)
gcloud artifacts packages list \
  --repository=my-maven-repo \
  --location=us-central1 \
  --project=my-project

# List versions of a package
gcloud artifacts versions list \
  --package=com.example:my-library \
  --repository=my-maven-repo \
  --location=us-central1 \
  --project=my-project

# List tags on a Docker image
gcloud artifacts tags list \
  --package=my-service \
  --repository=my-docker-repo \
  --location=us-central1 \
  --project=my-project

# Delete a specific Docker image version
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/my-project/my-docker-repo/my-service:old-tag \
  --project=my-project

# List vulnerability scanning results for an image
gcloud artifacts vulnerabilities list \
  us-central1-docker.pkg.dev/my-project/my-docker-repo/my-service:latest \
  --project=my-project

# List only CRITICAL and HIGH vulnerabilities
gcloud artifacts vulnerabilities list \
  us-central1-docker.pkg.dev/my-project/my-docker-repo/my-service:latest \
  --filter="vulnerability.effectiveSeverity:(CRITICAL HIGH)" \
  --project=my-project

# Grant read access to a repository (for GKE nodes pulling images)
gcloud artifacts repositories add-iam-policy-binding my-docker-repo \
  --location=us-central1 \
  --member="serviceAccount:gke-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader" \
  --project=my-project

# IAM roles:
# roles/artifactregistry.admin       - full control
# roles/artifactregistry.repoAdmin   - manage specific repository
# roles/artifactregistry.writer      - push artifacts
# roles/artifactregistry.reader      - pull artifacts
# roles/artifactregistry.createOnPushWriter - pull and push new repositories
```
