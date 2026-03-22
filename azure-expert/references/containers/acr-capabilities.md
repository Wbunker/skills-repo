# Azure Container Registry (ACR) — Capabilities Reference
For CLI commands, see [acr-cli.md](acr-cli.md).

## Azure Container Registry

**Purpose**: Private, managed OCI-compliant container registry for building, storing, scanning, and deploying container images and other OCI artifacts. Eliminates dependency on Docker Hub for enterprise workloads.

---

## Service Tiers

| Feature | Basic | Standard | Premium |
|---|---|---|---|
| **Storage** | 10 GB | 100 GB | 500 GB (expandable) |
| **Throughput** | Low | Moderate | High |
| **Geo-replication** | No | No | Yes |
| **Private Endpoint** | No | No | Yes |
| **Customer-managed keys** | No | No | Yes |
| **Content trust / Notation** | No | No | Yes |
| **Dedicated data endpoints** | No | No | Yes |
| **Zone redundancy** | No | No | Yes |
| **Repository-scoped tokens** | No | No | Yes |
| **Use case** | Dev/test, CI pipelines | Production | Enterprise, multi-region, compliance |

---

## Geo-replication (Premium)

- Replicate a single registry to multiple Azure regions; each region gets a replica with full read/write capability
- **Pull from closest replica**: clients pull images from their nearest regional replica — reduced latency, no cross-region egress fees within replicated regions
- **Push to any replica**: pushes replicate to all other regions automatically
- **Zero additional egress fees**: traffic between replicated regions within the same registry is free
- **Consistent tags**: same image tag serves the same digest across all regions
- Use cases: multi-region AKS clusters, global CI/CD pipelines, disaster recovery

```bash
# Add a replica to another region
az acr replication create \
  --registry myACR \
  --location westeurope
```

---

## ACR Tasks

Cloud-based container build automation. Run image builds, tests, and push pipelines without a local Docker daemon or dedicated build agent.

### Task Types

| Task Type | Trigger | Description |
|---|---|---|
| **Quick task** | Manual (`az acr build`) | One-off build and push; no task resource created |
| **Automatic triggered task** | Git commit, base image update, timer | Persistent task definition; runs on trigger |
| **Multi-step task** | Any trigger | YAML-defined pipeline with multiple steps (build, test, push, conditional logic) |

### Quick Tasks
```bash
# Build and push from current directory (no Dockerfile setup needed locally)
az acr build \
  --registry myACR \
  --image myimage:latest \
  .

# Build from a remote Git repo
az acr build \
  --registry myACR \
  --image myimage:{{.Run.ID}} \
  https://github.com/myorg/myrepo.git#main
```

### Triggered Tasks

**Git commit trigger** (webhooks from GitHub/Azure Repos):
```bash
az acr task create \
  --registry myACR \
  --name buildOnCommit \
  --image myimage:{{.Run.ID}} \
  --context https://github.com/myorg/myrepo.git#main \
  --file Dockerfile \
  --git-access-token {PAT_TOKEN}
```

**Base image update trigger** (auto-rebuild when base image changes):
```bash
az acr task create \
  --registry myACR \
  --name buildOnBaseUpdate \
  --image myapp:latest \
  --context https://github.com/myorg/myapp.git \
  --file Dockerfile \
  --base-image-trigger-enabled true \
  --git-access-token {PAT_TOKEN}
```

**Timer trigger** (scheduled build):
```bash
az acr task timer add \
  --registry myACR \
  --name buildOnCommit \
  --timer-name nightly \
  --schedule "0 2 * * *"
```

### Multi-Step Tasks (YAML)
```yaml
# acr-task.yaml
version: v1.1.0
steps:
  - id: build
    build: -t $Registry/myapp:$ID -f Dockerfile .

  - id: test
    cmd: $Registry/myapp:$ID pytest /app/tests
    env:
      - TEST_ENV=ci

  - id: push
    push:
      - $Registry/myapp:$ID
      - $Registry/myapp:latest
    when:
      - test
```

### Task Managed Identity
- ACR Tasks support managed identity for authenticating to other Azure resources during build
- Common use: pull secrets from Key Vault during build, push to another registry, access private Git repos via managed identity

---

## Content Trust and Image Signing

### Notation (Recommended)
- CNCF-standard Notary v2 / Notation tool for container image signing
- Sign images after push; store signatures as OCI artifacts in the same registry
- Verify signatures before deployment (AKS admission controller, Azure Policy, Gatekeeper)
- Integration with Azure Key Vault for signing keys (HSM-backed)

### Docker Content Trust (legacy)
- Older signing mechanism using Notary v1; less preferred for new deployments
- Enable per-repository; requires Notary server (Premium tier)

---

## Vulnerability Scanning

- **Microsoft Defender for Containers**: scans images for vulnerabilities on push and on a recurring schedule (weekly)
- Scanning results appear in Microsoft Defender for Cloud security recommendations
- Supported: OS package vulnerabilities (CVE), Node.js/Python/Java application vulnerabilities
- Integration with Azure Policy: deny deployment of images with critical vulnerabilities

---

## Repository-Scoped Access (Tokens)

- Create tokens with fine-grained permissions per repository (not registry-wide)
- Permissions per repository: `content/read`, `content/write`, `content/delete`, `metadata/read`, `metadata/write`
- Use cases: give a CI system push access only to specific repos; give external partners pull-only access to specific images
- Scope maps: reusable permission set applied to one or more tokens

```bash
# Create a scope map for pull access to one repo
az acr scope-map create \
  --registry myACR \
  --name pullonly-scopemap \
  --repository myapp content/read metadata/read

# Create a token using the scope map
az acr token create \
  --registry myACR \
  --name pullonly-token \
  --scope-map pullonly-scopemap
```

---

## Private Endpoint (Premium)

- Disable public network access entirely; all registry traffic via private endpoint
- Private endpoint gives registry a private IP in your VNet
- DNS: private DNS zone `privatelink.azurecr.io` maps registry hostname to private IP
- Combine with dedicated data endpoints (separate endpoints per region for geo-replicated registries)

---

## OCI Artifacts

ACR stores any OCI-compatible artifact, not just container images:

| Artifact Type | Description |
|---|---|
| **Helm charts** | Store and distribute Helm charts via `helm push` / `helm pull` using OCI registry |
| **Bicep modules** | Store reusable Bicep modules in ACR for IaC consumption |
| **WASM modules** | WebAssembly modules as OCI artifacts |
| **Supply chain artifacts** | SBOMs, SLSA attestations, Notation signatures stored alongside images |

---

## Webhooks

- Trigger HTTP POST to an external endpoint on registry events
- Supported events: `push` (image or artifact pushed), `delete` (image or tag deleted), `quarantine`
- Use cases: trigger Container Apps revision update, notify CI system of new image, update deployment pipeline

---

## Image Import

- Copy images from Docker Hub, another ACR, or any public/private registry into your ACR
- Avoids rate limits (Docker Hub), centralizes images, enables air-gapped scenarios
- `az acr import` — no local Docker daemon required; runs server-side

---

## Authentication Methods

| Method | Use Case |
|---|---|
| **Admin account** | Quick dev/test; disabled by default; username/password |
| **Service principal** | CI/CD pipelines; assign AcrPull / AcrPush role |
| **Managed identity** | AKS, Container Apps, Azure Functions; `az acr login` not needed |
| **Token (repository-scoped)** | Fine-grained per-repo access |
| **Entra ID (interactive)** | Developer access via `az acr login --name myACR` |

### Built-in ACR RBAC Roles

| Role | Permissions |
|---|---|
| `AcrPull` | Pull images from registry |
| `AcrPush` | Pull and push images |
| `AcrDelete` | Pull, push, and delete images and tags |
| `AcrImageSigner` | Sign images (Content Trust) |
| `Reader` | View registry metadata but cannot pull images |
| `Contributor` / `Owner` | Full management including registry configuration |
