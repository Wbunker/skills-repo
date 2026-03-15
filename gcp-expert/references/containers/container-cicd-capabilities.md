# CI/CD for Containers — Capabilities

## Cloud Build

Cloud Build is GCP's fully managed CI/CD execution platform. It runs build steps as Docker containers in isolated environments and is designed for container image building, testing, and multi-step build pipelines.

### Build Configuration

Builds are defined in `cloudbuild.yaml` (YAML) or `cloudbuild.json` (JSON). Each build consists of **steps**, where each step is a Docker container execution. Steps run sequentially by default; parallel steps are supported with `waitFor`.

**cloudbuild.yaml structure**:
```yaml
steps:
  - name: 'IMAGE'         # Docker image to run as the build step
    id: 'STEP_ID'
    entrypoint: 'bash'    # Override container entrypoint
    args: ['...']         # Arguments passed to the entrypoint
    env: ['KEY=VALUE']    # Environment variables
    dir: 'subdir'         # Working directory within the build workspace
    waitFor: ['-']        # '-' means run immediately (parallel); or list step IDs

# Images to push after successful build
images:
  - 'us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:$COMMIT_SHA'
  - 'us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest'

# Files to cache between builds (Cloud Storage)
options:
  machineType: 'E2_HIGHCPU_8'    # Build machine size
  logging: CLOUD_LOGGING_ONLY
  dynamicSubstitutions: true
  defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET

# Substitution variables (overridable at trigger time)
substitutions:
  _ENV: 'dev'
  _REGION: 'us-central1'

timeout: '1200s'  # Max build duration
```

### Built-in Cloud Builders

Google provides pre-built builder images for common tools:
- `gcr.io/cloud-builders/docker`: Docker CLI (build, push, pull, run).
- `gcr.io/cloud-builders/gcloud`: gcloud CLI.
- `gcr.io/cloud-builders/kubectl`: kubectl with GKE credentials.
- `gcr.io/cloud-builders/git`: Git operations.
- `gcr.io/cloud-builders/go`: Go compiler.
- `gcr.io/cloud-builders/mvn`: Maven.
- `gcr.io/cloud-builders/gradle`: Gradle.
- `gcr.io/cloud-builders/npm`: npm.
- `gcr.io/cloud-builders/wget`, `curl`, etc.

Any public or private Docker image can be used as a build step.

### Build Machine Types

- `E2_STANDARD_2` (default): 2 vCPU, 8 GB RAM.
- `E2_STANDARD_4`: 4 vCPU, 16 GB RAM.
- `E2_HIGHCPU_8`: 8 vCPU, 8 GB RAM. Good for parallel test suites.
- `E2_HIGHCPU_32`: 32 vCPU, 32 GB RAM. For large multi-stage builds.
- `N1_HIGHCPU_8`, `N1_HIGHCPU_32`: N1 series, good for memory-intensive builds.

Larger machine types cost more per build minute but reduce wall-clock build time.

### Build Triggers

Cloud Build triggers automatically start builds in response to events:

- **GitHub (via Cloud Build GitHub App)**: push to branch, push tag, pull request. Filter by file path glob (only build when specific directories change).
- **Cloud Source Repositories**: push to branch or tag.
- **Pub/Sub**: trigger on a Pub/Sub message (for custom event-driven builds).
- **Webhook**: trigger via an HTTP POST to a unique URL (for external CI systems, manual triggers, or ChatOps).
- **Manual**: trigger builds on demand from Console or gcloud.

**Branch protection integration**: Cloud Build GitHub App reports build status back to GitHub; use branch protection rules requiring build success before merging PRs.

### Dockerfile Best Practices in Cloud Build

- Use multi-stage builds to minimize final image size: build stage installs build tools; final stage copies only compiled artifacts.
- Use Docker layer caching: `--cache-from` the previously built image to reuse layers that haven't changed. Cloud Build supports caching via `images` field (pushed after each build) + `--cache-from` on the next build.
- Use `kaniko` builder (`gcr.io/kaniko-project/executor`) for rootless, daemon-less image builds — required in environments where Docker-in-Docker is restricted.
- Use `buildpacks` builder (`gcr.io/buildpacks/builder`) for automatic container image creation without a Dockerfile.

### Build Artifacts Beyond Images

Cloud Build can produce non-image artifacts:
- Maven/npm/Python packages pushed to Artifact Registry.
- Build output files uploaded to Cloud Storage.
- Test reports exported to Cloud Storage (viewable in Cloud Build UI).
- SBOM (Software Bill of Materials) generated with `syft` or `trivy` build steps.

---

## Cloud Deploy

Cloud Deploy is GCP's fully managed continuous delivery service for GKE, GKE Autopilot, Cloud Run, and Anthos. It provides release management, deployment tracking, approval gates, and rollback capabilities.

### Core Concepts

**Delivery Pipeline**: defines the release path (ordered list of targets). Each target is a deployment environment (dev → staging → prod). Defined in a `delivery-pipeline.yaml` and registered with Cloud Deploy.

**Target**: a deployment destination (a GKE cluster, Cloud Run region, or Anthos cluster). Each target has a unique name and deployment configuration. Targets can require approval before a rollout proceeds.

**Release**: a specific version of your application, created from a Skaffold configuration and a set of container image tags. A release is immutable — the same release can be promoted through targets.

**Rollout**: the deployment of a release to a specific target. A rollout tracks the deployment status. Rollouts can be in states: PENDING_APPROVAL, IN_PROGRESS, SUCCEEDED, FAILED.

**Promotion**: advancing a release from one target to the next in the pipeline sequence. Can be automatic (pipeline-level automation) or manual.

### Delivery Pipeline YAML

```yaml
# delivery-pipeline.yaml
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: my-app-pipeline
  labels:
    app: my-app
description: My application delivery pipeline
serialPipeline:
  stages:
    - targetId: dev
      profiles: [dev]
    - targetId: staging
      profiles: [staging]
      strategy:
        canary:
          runtimeConfig:
            cloudRun:
              automaticTrafficControl: true
          canaryDeployment:
            percentages: [25, 50, 75]
            verify: true
    - targetId: prod
      profiles: [prod]
      strategy:
        standard:
          verify: true
```

### Target YAML

```yaml
# targets.yaml
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: dev
  labels:
    env: dev
description: Development environment
run:
  location: projects/PROJECT_ID/locations/us-central1
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: staging
description: Staging environment
requireApproval: false
run:
  location: projects/PROJECT_ID/locations/us-central1
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: prod
description: Production environment
requireApproval: true    # Manual approval required before prod rollout
run:
  location: projects/PROJECT_ID/locations/us-central1
```

### Skaffold Integration

Skaffold is the render and deploy tool underlying Cloud Deploy. Every Cloud Deploy release is tied to a Skaffold configuration (`skaffold.yaml`). Skaffold handles:
- **Rendering**: substituting image tags into Kubernetes manifests (Helm, Kustomize, or raw YAML) or Cloud Run service YAML.
- **Deploying**: applying rendered manifests to the target cluster or Cloud Run region.
- **Verification**: running post-deployment tests (using container-based test runners).

### Rollback

Cloud Deploy tracks the history of rollouts per target. To roll back, create a new rollout using the previous release — no code change required. The previous release's manifests (with the previous image tags) are re-applied to the target.

### Canary Deployments in Cloud Deploy

Cloud Deploy supports native canary deployments for Cloud Run and GKE:
- For Cloud Run: automatic traffic splitting between the new and existing revision.
- For GKE: `kubectl rollout` with partial pod count updates or custom Kubernetes rollout strategies.
- The canary percentages are defined in the delivery pipeline stages.
- Verification step (post-deployment test) can be configured to run after each canary increment; failure triggers automatic rollback.

---

## Skaffold

Skaffold is an open-source command-line tool (developed by Google) that automates the build, push, and deploy lifecycle for containerized applications, primarily targeting Kubernetes and Cloud Run.

### Skaffold Configuration (skaffold.yaml)

```yaml
# skaffold.yaml
apiVersion: skaffold/v4beta11
kind: Config
metadata:
  name: my-app

build:
  artifacts:
    - image: my-app
      docker:
        dockerfile: Dockerfile
  tagPolicy:
    gitCommit: {}
  platforms:
    - linux/amd64

manifests:
  kustomize:
    paths:
      - k8s/overlays/dev    # or k8s/overlays/staging, prod

deploy:
  kubectl: {}
  # or:
  # cloudrun:
  #   projectid: PROJECT_ID
  #   region: us-central1

profiles:
  - name: dev
    manifests:
      kustomize:
        paths: [k8s/overlays/dev]
  - name: staging
    manifests:
      kustomize:
        paths: [k8s/overlays/staging]
  - name: prod
    manifests:
      kustomize:
        paths: [k8s/overlays/prod]

verify:
  - name: integration-test
    container:
      name: integration-test
      image: my-integration-test
      command: ["/test/run-tests.sh"]
```

### Skaffold Workflow Modes

**`skaffold dev`** (local development):
- Watches source code for changes.
- Automatically rebuilds and redeploys on file change.
- Streams logs from deployed containers.
- Cleans up resources when the process is killed (Ctrl+C).
- Works with local Docker (builds locally) + `minikube` or `kind` cluster.
- With `--trigger=polling` or `--trigger=notify` (inotify).

**`skaffold build`**: build and tag images; push to registry. Used in CI to produce images for Cloud Deploy.

**`skaffold render`**: render Kubernetes manifests with image tags substituted. Produces a hydrated manifest file that Cloud Deploy can apply.

**`skaffold deploy`**: deploy pre-built images from a rendered manifest. Used by Cloud Deploy during rollout.

**`skaffold run`**: build + push + deploy in one step. For CI/CD pipelines that don't use Cloud Deploy.

**`skaffold verify`**: run post-deployment verification tests defined in `skaffold.yaml`.

### HotReload with Skaffold (File Sync)

Skaffold file sync avoids full image rebuild for certain file changes:
- **Infer**: automatically syncs files that don't require a rebuild (non-compiled assets).
- **Manual sync**: specify glob patterns of files to sync directly into running containers without rebuilding.

Useful for: frontend asset changes (CSS, HTML templates), Python/Node.js hot reload in development.

---

## GitOps with Config Sync

For production GKE clusters, a GitOps approach using Config Sync is often preferred over imperative `kubectl apply` or Cloud Deploy for Kubernetes:

1. **Source of truth**: Kubernetes manifests in Git (GitHub, GitLab, Cloud Source Repositories).
2. **Config Sync**: continuously watches the Git repository; applies changes to the cluster when commits land on the watched branch.
3. **CI pipeline (Cloud Build)**: runs tests; if passing, updates the image tag in the Kubernetes manifest (Kustomize `setImage` or Helm values) and pushes the commit to Git.
4. **Config Sync**: picks up the Git commit and applies the new manifest to the cluster.

**Benefits over Cloud Deploy for Kubernetes**:
- Any change to the cluster state requires a PR (code review, audit trail).
- Drift detection: manual changes to the cluster are automatically reverted.
- Multi-cluster: same Git repo manages multiple clusters.

**Config Sync + Cloud Deploy**: these are not mutually exclusive. Use Cloud Deploy for release management, approval gates, and promotion workflow; use Config Sync as the actual deployment mechanism by having Cloud Deploy update a Git manifest as the final step.

---

## Container Security Best Practices in CI/CD

### Distroless Images
Use `gcr.io/distroless/base-debian12` or language-specific distroless images (`gcr.io/distroless/java21-debian12`) as the final stage base in multi-stage builds. Distroless images contain only the application and runtime libraries — no shell, no package manager, no `/tmp`. This dramatically reduces attack surface and CVE count.

### Multi-Stage Builds
```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# Final stage: distroless
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

### Non-Root User
Always run the container process as a non-root user. Specify `USER 1000:1000` (or a named non-root user) in the Dockerfile. For distroless images, use `:nonroot` tag.

### Read-Only Filesystem
Set `readOnlyRootFilesystem: true` in the Kubernetes pod spec security context. Mount writable volumes explicitly only where needed (`/tmp`, log directories). Prevents an attacker from writing malicious files to the container filesystem.

### Resource Limits
Always set CPU and memory `requests` and `limits` in Kubernetes pod specs. Prevents a misbehaving pod from starving other pods (memory) or consuming all node CPU (CPU). Required by Policy Controller constraints and GKE Autopilot.

### SBOM and Signing
- Generate SBOM (Software Bill of Materials) with `syft` in Cloud Build.
- Sign images with `cosign` (Sigstore) in Cloud Build.
- Store attestations in Artifact Registry (OCI attestation).
- Enforce with Binary Authorization policies requiring `cosign` attestation.
