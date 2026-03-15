# Source Repositories & Cloud Workstations — Capabilities

## Cloud Source Repositories

Cloud Source Repositories (CSR) is GCP's managed private Git hosting service. It provides unlimited private Git repositories with IAM-based access control and deep integration with Cloud Build and other GCP services.

### Core Features

- **Standard Git protocol**: use standard `git clone`, `push`, `pull`, `fetch` over HTTPS or SSH.
- **Unlimited repositories**: no per-repository cost; storage is billed per GB.
- **IAM access control**: grant access at the project level or per-repository using standard GCP IAM roles:
  - `roles/source.reader`: clone and view repository contents.
  - `roles/source.writer`: push changes.
  - `roles/source.admin`: manage repository settings and IAM.
- **Repository mirroring**: automatically mirror from GitHub, GitLab, or Bitbucket. CSR stays synchronized with every push to the upstream. Mirroring is one-way (upstream → CSR); CSR does not push back to GitHub.

### Integration with Cloud Build

Cloud Build can trigger automatically on CSR events:
- Push to a specific branch (e.g., `main`).
- Push matching a regex pattern (e.g., `^release/.*$`).
- Tag creation matching a pattern (e.g., `^v[0-9]+\.[0-9]+\.[0-9]+$`).

Triggers reference the CSR repository by project and name. This eliminates the need to connect an external Git provider for simple GCP-native CI/CD.

### What CSR Is Not

CSR does not provide:
- Pull requests / merge requests (no PR workflow, code review UI).
- Issue tracking.
- CI/CD pipelines built into the UI (use Cloud Build separately).
- Branch protection rules.
- Code owners files.

For collaboration workflows requiring PR review, use GitHub or GitLab and mirror to CSR (or use Cloud Build GitHub/GitLab integration directly).

### Authentication Methods

- **gcloud SSH key**: `gcloud source repos clone` configures SSH automatically using gcloud credentials.
- **HTTPS with credential helper**: configure `git config --global credential.https://source.developers.google.com.helper gcloud.sh`; gcloud provides credentials transparently.
- **SSH keys**: manually generate SSH key pair; add public key to `ssh-keygen` output in your Google account profile (`console.cloud.google.com/iam-admin/user-settings`).

---

## Cloud Workstations

Cloud Workstations is a managed cloud-based development environment service. It provides fully managed, customizable, secure development environments hosted on GCP infrastructure.

### How It Works

1. **Workstation Cluster**: GKE-based infrastructure cluster in your VPC where workstation VMs run. Created once per region; takes ~10 minutes to provision. The cluster defines the network configuration.

2. **Workstation Configuration**: a template defining the VM machine type, disk size, container image, environment variables, ephemeral timeouts, and which cluster to use. Multiple configurations can exist per cluster (e.g., "frontend-dev" with 4 CPU, "ml-dev" with GPU).

3. **Workstation**: an instance of a workstation configuration assigned to a specific developer. The developer starts the workstation on demand; it runs until stopped or the idle timeout triggers.

### Access Methods

- **Browser-based**: access via `https://PORT-WORKSTATION_NAME-HASH.cloudworkstations.dev`. Opens a VS Code-like editor (Code OSS / code-server) in the browser.
- **SSH**: `gcloud workstations ssh WORKSTATION_NAME --cluster=CLUSTER --config=CONFIG --project=PROJECT_ID`. SSH directly to the workstation VM.
- **Local VS Code**: install the Cloud Workstations extension; connect via Remote-SSH using gcloud as the proxy command.
- **JetBrains IDEs**: connect via JetBrains Gateway with the Cloud Workstations plugin.

### Key Features

- **Persistent home directory**: each workstation has a persistent Persistent Disk for `$HOME`. Code, configurations, and installed tools persist across stops/starts. The base container image is re-pulled on restart; changes outside `$HOME` are ephemeral.
- **Custom container images**: bring your own base image with pre-installed tools, language runtimes, SDKs, and internal certificates. Host on Artifact Registry. Update the configuration to deploy new image versions to all workstations.
- **Security**:
  - Workstations run in your VPC (private IP only by default).
  - No public internet exposure of the workstation VM.
  - IAM controls who can start/use a workstation.
  - Forced idle stop after configurable inactivity timeout (prevents costs from forgotten running workstations).
  - Integration with BeyondCorp (IAP) for identity-based access without VPN.
- **GPU support**: configure an Accelerator (NVIDIA L4, T4, A100) in the workstation configuration for ML development, model fine-tuning, and GPU-based debugging.
- **Ephemeral workstations**: configure workstations to delete on stop (no persistent disk) for cost-optimized, security-sensitive environments where no data should persist between sessions.

### Use Cases

- **Onboarding new developers**: provide a pre-configured environment with all tools installed; developers are productive immediately.
- **Regulated industries**: keep all code and secrets in a Google-managed environment; code never leaves GCP; no risk of local machine compromise.
- **Reproducible environments**: all developers use the same container image; eliminates "works on my machine" issues.
- **Heavy compute needs**: give ML engineers a GPU-equipped workstation without shipping them a GPU laptop.
- **Contractor/partner access**: provide temporary workstation access without giving access to a corporate laptop.

---

## Cloud Code

Cloud Code is an IDE extension for Visual Studio Code and JetBrains IDEs (IntelliJ IDEA, PyCharm, GoLand, WebStorm, etc.) that provides GCP-native development integrations.

### Key Features

- **Kubernetes integration**: browse cluster resources; deploy to GKE or local Kubernetes (Minikube, Docker Desktop); view pod logs; port-forward; debug running pods.
- **Cloud Run local development**: run Cloud Run services locally with the Cloud Run emulator; hot reload; environment variable injection from Secret Manager.
- **Cloud SQL debugging**: browse Cloud SQL instances; connect via IAM; inspect databases and tables.
- **Secret Manager integration**: browse secrets; insert secret references into code.
- **API Explorer**: browse GCP APIs; generate code snippets.
- **Cloud Build integration**: view build history and logs.
- **Skaffold integration**: run `skaffold dev` within the IDE for continuous development.

---

## Gemini Code Assist (formerly Duet AI for Developers)

Gemini Code Assist is Google's AI coding assistant integrated into VS Code, JetBrains IDEs, and Cloud Workstations.

### Features

- **Code completion**: inline suggestions as you type; multi-line completions for boilerplate and repetitive patterns.
- **Code generation**: generate complete functions, classes, or files from a natural language description or comment.
- **Code explanation**: explain selected code in plain English; useful for understanding unfamiliar codebases.
- **Test generation**: generate unit tests for selected functions.
- **Bug fixing suggestions**: highlight problematic code and ask for fix suggestions.
- **Chat interface**: ask questions about GCP APIs, architecture, debugging in a chat panel within the IDE.
- **Transformation**: refactor code, translate between languages (e.g., Python to Go).

### Enterprise Tier

- **Private codebase indexing**: index your organization's private GitHub/GitLab/Bitbucket repositories; Code Assist uses the index for more accurate, context-aware completions.
- **Data governance**: no customer code is used to train Google's models; queries stay within your organization's boundary.
- **Usage controls**: administrators can enable/disable Code Assist for specific users or projects.
