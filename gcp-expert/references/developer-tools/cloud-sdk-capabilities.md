# Cloud SDK & Shell — Capabilities

## gcloud CLI Overview

The `gcloud` CLI is the primary command-line interface for Google Cloud Platform. It is part of the **Cloud SDK** — a set of tools that includes gcloud, `gsutil` (now `gcloud storage`), `bq` (BigQuery CLI), `kubectl`, and additional components.

### Component System

The Cloud SDK uses a component model — the core gcloud CLI is always installed, and optional components are installed on demand:
- `gcloud components install kubectl` — Kubernetes CLI (for GKE).
- `gcloud components install minikube` — local Kubernetes for development.
- `gcloud components install skaffold` — Skaffold for container dev workflows.
- `gcloud components install alpha` / `beta` — pre-GA command groups.
- `gcloud components install cloud-firestore-emulator` — local Firestore.
- `gcloud components install pubsub-emulator` — local Pub/Sub.
- `gcloud components install bigtable` — Cloud Bigtable emulator.
- `gcloud components install spanner-emulator` — Cloud Spanner emulator.

Update all installed components: `gcloud components update`.

---

## Authentication

### User Account Authentication

`gcloud auth login` opens a browser window for OAuth 2.0 authentication with your Google account. Stores credentials in `~/.config/gcloud/credentials.db`. All gcloud commands subsequently run as this user identity.

`gcloud auth list` shows all authenticated accounts and the active account.

`gcloud auth revoke` removes stored credentials for an account.

### Application Default Credentials (ADC)

ADC is a standard way for applications (not just gcloud) to find credentials automatically. Client libraries (Python, Java, Go, Node.js) use ADC.

**ADC discovery chain (in order)**:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable — points to a service account key JSON file. Used in CI/CD or Docker containers.
2. `gcloud auth application-default login` — stores user credentials at `~/.config/gcloud/application_default_credentials.json`. Used for local development.
3. GCE/GKE/Cloud Run/App Engine metadata server — on GCP infrastructure, the metadata server provides the VM/pod/service's service account token automatically.
4. Workload Identity (GKE) — the pod's projected service account token is exchanged for a GCP access token via the metadata server.

**Best practice**: never use option 1 (service account key file) in production. Use the metadata server (option 3) or Workload Identity (option 4) in GCP-hosted environments.

`gcloud auth application-default login` — store ADC for local development. Use `--scopes` to limit access.

`gcloud auth application-default set-quota-project PROJECT_ID` — set the billing project for ADC quota.

### Service Account Authentication

For CI/CD pipelines or batch jobs that need to authenticate as a service account:

- `gcloud auth activate-service-account --key-file=sa-key.json` — activates a service account key for gcloud commands in the current session. After this, all gcloud commands run as that SA.
- Alternatively: set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json` for client libraries.

**Avoid service account keys** — they are long-lived credentials that can be leaked. Prefer Workload Identity, Workload Identity Federation (for external workloads), or the GCE metadata server.

### Service Account Impersonation

`gcloud --impersonate-service-account=SA_EMAIL COMMAND` — runs a single gcloud command impersonating the specified service account. The calling user account must have `roles/iam.serviceAccountTokenCreator` on the target SA.

Use cases:
- Test IAM permissions as a service account without downloading a key.
- Debug "what can this SA do?" scenarios.
- Automation scripts that should run with a specific SA identity.

`gcloud config set auth/impersonate_service_account SA_EMAIL` — impersonate by default for all commands in the current configuration. Clear with `gcloud config unset auth/impersonate_service_account`.

### Workload Identity Federation

For CI/CD systems outside GCP (GitHub Actions, GitLab CI, AWS, Azure AD) that need to authenticate to GCP without a service account key:
- Create a Workload Identity Pool and Provider (OIDC or SAML) in GCP.
- The external identity (e.g., GitHub Actions OIDC token) is exchanged for a short-lived GCP access token via the STS API.
- No long-lived credential stored anywhere.
- `gcloud iam workload-identity-pools create/list/describe`.
- `gcloud iam workload-identity-pools providers create-oidc/create-aws`.

---

## Configurations (Named Profiles)

gcloud configurations allow you to maintain multiple named sets of properties — useful when working across multiple GCP projects, accounts, or regions.

**Configuration properties**:
- `core/project` — default GCP project ID.
- `core/account` — default Google account.
- `compute/region` — default Compute Engine region.
- `compute/zone` — default Compute Engine zone.
- `run/region` — default Cloud Run region.
- `container/cluster` — default GKE cluster.
- `container/zone` — default GKE cluster zone/region.

**Switching configurations**: `gcloud config configurations activate my-config` instantly changes all defaults to that configuration's values.

**Per-command override**: any property can be overridden for a single command with `--project`, `--account`, `--region`, `--zone` flags.

**Environment variable override**: `CLOUDSDK_CORE_PROJECT`, `CLOUDSDK_COMPUTE_REGION`, etc. override configuration values for the duration of a shell session.

---

## Output Formatting

gcloud output is highly customizable and scriptable.

### Format Types
- `--format=json`: JSON output (for scripting with `jq`).
- `--format=yaml`: YAML output (for Kubernetes-style config).
- `--format=table`: tabular output (default for humans; customizable columns).
- `--format=csv`: comma-separated values (for spreadsheet import or awk).
- `--format=value`: bare field values (for scripting, one field per line).
- `--format=get(FIELD)`: extract a nested field using dot notation.
- `--format=list`: indented list of values.
- `--format=text`: key: value text format.

### Format Expressions

```bash
# Custom table with specific columns and titles
gcloud compute instances list \
  --format="table(name,status,zone.basename(),machineType.basename():label=TYPE)"

# Extract a single field value (for use in scripts)
gcloud run services describe my-service \
  --region=us-central1 \
  --format="value(status.url)"

# Extract nested JSON field
gcloud iam service-accounts describe my-sa@PROJECT.iam.gserviceaccount.com \
  --format="value(email,disabled)"

# JSON with flattened output
gcloud container clusters list \
  --format="json(name,status,currentMasterVersion)"
```

### Server-Side Filtering

`--filter` applies filtering on the server (or on the response before printing). Uses the gcloud filter expression syntax:

```bash
# Filter by field value
gcloud compute instances list --filter="status=RUNNING"

# Filter by zone
gcloud compute instances list --filter="zone:us-central1-a"

# Filter by name prefix
gcloud compute instances list --filter="name:my-app-*"

# Combine filters (AND)
gcloud compute instances list --filter="status=RUNNING AND zone:us-central1"

# Filter with list membership
gcloud compute instances list --filter="tags.items=web-server"

# Filter with NOT
gcloud compute instances list --filter="NOT status=TERMINATED"

# Pagination
gcloud compute instances list --limit=50 --sort-by=name
gcloud compute instances list --limit=50 --sort-by="~createTime"   # reverse sort
```

---

## Cloud Shell

Cloud Shell is a browser-based terminal available from the GCP Console at `console.cloud.google.com/cloudshell`.

**Key characteristics**:
- **Free**: no additional charge for Cloud Shell usage.
- **Pre-installed tools**: Cloud SDK (gcloud, gsutil, bq), kubectl, Docker, Helm, Terraform, git, vim, emacs, tmux, Python 3, Node.js, Go, Java, Ruby, and many more.
- **Always up-to-date**: Google keeps the Cloud SDK installation current.
- **Persistent home directory**: 5 GB persistent disk attached to `$HOME`; survives between sessions (even across VM restarts). Use for storing credentials, SSH keys, project files.
- **Ephemeral VM**: the underlying VM (Debian-based) is provisioned on demand; if inactive for 20 minutes, it's stopped (home disk persists). After ~120 days of inactivity, the home disk may be deleted.
- **Web Preview**: forward a port from the Cloud Shell VM to your browser; useful for testing web apps locally with `gcloud app run` or `python -m http.server`.
- **Code Editor**: browser-based VS Code-like editor (Theia) available from Cloud Shell.
- **Boost Mode**: request an upgrade to an n1-standard-8 VM for compute-intensive tasks (limited hours per week).

**Cloud Shell environment variables**:
- `GOOGLE_CLOUD_PROJECT` — current project ID.
- `DEVSHELL_PROJECT_ID` — same as above (legacy).
- `GCLOUD_SHELL_VERSION` — Cloud SDK version.

**Limitations**:
- Not for production workloads — sessions are ephemeral.
- No inbound connections from the internet (only Web Preview for browser-based access).
- Not suitable as a long-running server.

---

## gcloud CLI Debugging and Troubleshooting

### Verbose Output

```bash
# Log all HTTP requests and responses (very verbose)
gcloud compute instances list --log-http

# Set verbosity level
gcloud compute instances list --verbosity=debug    # debug, info, warning, error, critical, none

# Show gcloud diagnostic information
gcloud info

# Check SDK installation and components
gcloud info --run-diagnostics
```

### Configuration Debugging

```bash
# Show the effective configuration (what config file is in use, properties)
gcloud config list

# Show all properties including defaults
gcloud config list --all

# Show a specific property
gcloud config get-value core/project
gcloud config get-value compute/region
```

### API and Quota Errors

- `RESOURCE_EXHAUSTED` / `429`: quota exceeded; check `gcloud services quota` or Console > IAM > Quotas.
- `PERMISSION_DENIED` / `403`: IAM permission missing on the resource.
- `SERVICE_DISABLED`: the API is not enabled; run `gcloud services enable SERVICE_NAME`.
- `ALREADY_EXISTS`: resource with the same name already exists.
- `NOT_FOUND`: resource doesn't exist or you don't have permission to see it.

```bash
# Enable a service (API)
gcloud services enable run.googleapis.com

# List enabled services
gcloud services list --enabled

# Check if a service is enabled
gcloud services list --enabled --filter="NAME:run.googleapis.com"
```
