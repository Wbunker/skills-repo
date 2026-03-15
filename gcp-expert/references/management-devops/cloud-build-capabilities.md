# Cloud Build & Cloud Deploy — Capabilities

## Cloud Build

### Purpose

Fully managed CI (Continuous Integration) service that executes build steps as Docker containers. Triggered by source code changes in Cloud Source Repositories, GitHub, GitLab, or Bitbucket. Produces artifacts (Docker images, binaries, test results) published to Artifact Registry or Cloud Storage.

### Core Concepts

| Concept | Description |
|---|---|
| Build | Single execution of a build config; identified by build ID |
| Build step | Container that runs as part of a build; steps run sequentially by default |
| Build config | `cloudbuild.yaml` (or JSON) defining the build steps |
| `/workspace` | Shared volume mounted in all steps; files written here persist across steps |
| Trigger | Rule that starts a build when a source event occurs |
| Substitution variable | Parameterize builds; built-in (`$PROJECT_ID`, `$BRANCH_NAME`, `$SHORT_SHA`) or user-defined (`$_MY_VAR`) |
| Build pool | Private pool: worker VMs in your VPC with custom machine types; default pool: Google-managed |
| Build artifact | Output of a build stored in Artifact Registry or GCS |
| Approval | Require human approval before a build step proceeds |
| Cache | Store and restore build dependencies using Cloud Storage for faster builds |

### cloudbuild.yaml Structure

```yaml
# cloudbuild.yaml — full example
substitutions:
  _REGION: us-central1
  _SERVICE_NAME: my-service
  _IMAGE: ${_REGION}-docker.pkg.dev/${PROJECT_ID}/my-repo/${_SERVICE_NAME}

options:
  machineType: E2_HIGHCPU_8
  logging: CLOUD_LOGGING_ONLY
  dynamicSubstitutions: true

steps:
  # Step 1: Install dependencies and run tests
  - name: node:18
    id: test
    entrypoint: npm
    args: [ci]
    dir: app/

  - name: node:18
    id: unit-tests
    waitFor: [test]
    entrypoint: npm
    args: [run, test]
    dir: app/

  # Step 2: Build Docker image
  - name: gcr.io/cloud-builders/docker
    id: build-image
    waitFor: [unit-tests]
    args:
      - build
      - -t
      - ${_IMAGE}:${SHORT_SHA}
      - -t
      - ${_IMAGE}:latest
      - --cache-from
      - ${_IMAGE}:latest
      - app/

  # Step 3: Run Trivy vulnerability scan
  - name: aquasec/trivy:latest
    id: scan
    waitFor: [build-image]
    args:
      - image
      - --exit-code=1
      - --severity=CRITICAL
      - ${_IMAGE}:${SHORT_SHA}

  # Step 4: Push image to Artifact Registry
  - name: gcr.io/cloud-builders/docker
    id: push
    waitFor: [scan]
    args: [push, --all-tags, ${_IMAGE}]

  # Step 5: Create Cloud Deploy release
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    id: deploy
    waitFor: [push]
    entrypoint: gcloud
    args:
      - deploy
      - releases
      - create
      - release-${SHORT_SHA}
      - --delivery-pipeline=my-pipeline
      - --region=${_REGION}
      - --images=my-service=${_IMAGE}:${SHORT_SHA}

images:
  - ${_IMAGE}:${SHORT_SHA}
  - ${_IMAGE}:latest

artifacts:
  objects:
    location: gs://my-build-artifacts/${BUILD_ID}/
    paths:
      - app/dist/**

timeout: 1200s
```

### Built-in Substitution Variables

| Variable | Value |
|---|---|
| `$PROJECT_ID` | GCP project ID |
| `$BUILD_ID` | Unique build ID |
| `$LOCATION` | Build worker region |
| `$TRIGGER_NAME` | Name of the trigger that started the build |
| `$REPO_NAME` | Repository name |
| `$BRANCH_NAME` | Branch name (for push/PR triggers) |
| `$TAG_NAME` | Git tag (for tag triggers) |
| `$COMMIT_SHA` | Full commit SHA |
| `$SHORT_SHA` | First 7 characters of commit SHA |
| `$REF_NAME` | Git ref |

### Build Triggers

| Trigger Type | Description |
|---|---|
| Push to branch | Fires on commits to specified branch pattern |
| Pull request | Fires when PR is opened or updated (requires GitHub App or webhook) |
| Push new tag | Fires when a matching tag is pushed |
| Manual | Started via gcloud or Cloud Console; no source event |
| Webhook | Custom HTTP webhook; any external event can trigger |
| Pub/Sub message | Build triggered by a Pub/Sub message |

**File path filters**: only fire trigger if changed files match include/exclude glob patterns (e.g., only trigger if `src/**` changes, ignore `docs/**`).

### Build Pools

**Default pool (Google-managed)**:
- Workers not in your VPC; no access to private resources
- Machine types: E2_STANDARD_2 (default), E2_MEDIUM, E2_HIGHCPU_8, E2_HIGHCPU_32, N1_HIGHCPU_8, N1_HIGHCPU_32

**Private pools**:
- Worker VMs provisioned in your VPC via VPC peering
- Access private Artifact Registry, Cloud SQL, internal services
- Custom machine types
- No additional charges beyond machine time

### Caching Strategies

- **Docker layer cache**: `--cache-from` flag in docker build pulls previous image for layer reuse
- **Cloud Storage cache**: store `node_modules`, Maven `.m2`, pip cache in GCS; restore at build start
- **Kaniko**: Google-provided builder for rootless, cache-efficient Docker builds from within Kubernetes

---

## Cloud Deploy

### Purpose

Managed continuous delivery (CD) service for GKE, GKE Autopilot, Cloud Run, Anthos, and Kubernetes. Automates the promotion of releases through an ordered sequence of deployment targets (e.g., dev → staging → prod) with integrated approval gates, rollback, and audit trail.

### Core Concepts

| Concept | Description |
|---|---|
| Delivery pipeline | Defines the ordered sequence of targets for a release to progress through |
| Target | Deployment destination: GKE cluster, Cloud Run region, Anthos cluster, or multi-target |
| Release | Immutable snapshot of the artifacts to deploy; created once, promoted across targets |
| Rollout | Deployment of a release to a specific target; has state (in-progress, succeeded, failed) |
| Skaffold | Tool used by Cloud Deploy to render and deploy manifests; `skaffold.yaml` required |
| Render | Process of substituting image references into Kubernetes/Cloud Run manifests |
| Approval | Gate between pipeline stages; requires explicit human approval in Cloud Console/CLI |
| Rollback | Deploy a previous release to a target |
| Automation | Automated promotion between stages based on conditions (experimental) |
| Canary | Deploy to a fraction of traffic; gradually promote |

### Delivery Pipeline Example

```yaml
# clouddeploy.yaml
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: my-pipeline
  annotations:
    description: "Backend service pipeline"
serialPipeline:
  stages:
  - targetId: dev
    profiles: [dev]
  - targetId: staging
    profiles: [staging]
  - targetId: production
    profiles: [production]
    strategy:
      canary:
        runtimeConfig:
          cloudRun:
            automaticTrafficControl: true
        canaryDeployment:
          percentages: [25, 50]
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: dev
gke:
  cluster: projects/my-project/locations/us-central1/clusters/dev-cluster
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: staging
requireApproval: false
gke:
  cluster: projects/my-project/locations/us-central1/clusters/staging-cluster
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: production
requireApproval: true   # human approval required before deployment
gke:
  cluster: projects/my-project/locations/us-central1/clusters/prod-cluster
```

### Skaffold Integration

Cloud Deploy uses Skaffold for rendering and deploying:

```yaml
# skaffold.yaml
apiVersion: skaffold/v3
kind: Config
metadata:
  name: my-service
build:
  artifacts:
  - image: my-service
    docker:
      dockerfile: Dockerfile
deploy:
  kubectl:
    manifests:
    - k8s/*.yaml
profiles:
- name: dev
  patches:
  - op: replace
    path: /deploy/kubectl/manifests
    value: [k8s/dev/*.yaml]
- name: production
  patches:
  - op: replace
    path: /deploy/kubectl/manifests
    value: [k8s/prod/*.yaml]
```

### Release Lifecycle

```
Cloud Build (CI)
  → builds image, pushes to Artifact Registry
  → gcloud deploy releases create (creates Release)
      → auto-deploys to first target (dev)
          → rollout succeeds
      → promote to staging (automatic or manual)
          → rollout succeeds
      → promote to production (requires approval)
          → approver reviews → approves
          → rollout to production
```

---

## Artifact Registry

### Purpose

Unified artifact management for Docker images, Maven JARs, npm packages, Python wheels, Go modules, Helm charts, apt packages, and yum packages. Regional service with IAM, CMEK, VPC Service Controls, and integrated vulnerability scanning.

### Key Features

- **Repository types**: Standard (managed storage), Remote (proxy/cache upstream registries), Virtual (union view over multiple repos)
- **Remote repositories**: cache Docker Hub, Maven Central, npm Registry, PyPI, etc. behind Artifact Registry; air-gapped builds
- **Virtual repositories**: present multiple repositories as a single endpoint with priority ordering
- **Vulnerability scanning**: automatic Container Analysis scanning for Docker images; CVE database
- **Binary Authorization**: integrate with Artifact Registry to enforce only attested images run in GKE
- **Cleanup policies**: automated deletion of old/untagged images based on age, tag prefix, keep-latest-N rules

### Repository Formats

| Format | Use Case |
|---|---|
| Docker | Container images |
| Maven | Java artifacts (JARs, WARs, POMs) |
| npm | Node.js packages |
| PyPI | Python packages |
| Go | Go modules |
| Helm | Kubernetes Helm charts |
| apt | Debian packages |
| yum | RPM packages for RHEL/CentOS |
| Generic | Arbitrary files, binaries, archives |
