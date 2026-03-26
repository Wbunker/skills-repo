# GitHub Actions Reference

## Workflow File Structure

Workflow files are YAML files stored in `.github/workflows/` in the repository root.

```yaml
name: CI                        # Optional display name
run-name: Deploy ${{ github.ref_name }}  # Optional dynamic run name

on:                             # Trigger events (required)
  push:
    branches: [main]

env:                            # Workflow-level environment variables
  NODE_VERSION: '20'

permissions:                    # Workflow-level permissions
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
```

---

## Trigger Events

### Code Events

| Event | Description | Key filters |
|-------|-------------|-------------|
| `push` | Push to branch or tag | `branches`, `tags`, `paths`, `branches-ignore`, `tags-ignore`, `paths-ignore` |
| `pull_request` | PR opened/updated (fork-safe, limited token) | `branches`, `paths`, `types` |
| `pull_request_target` | PR events with full repo token (runs in base context) | same as above |
| `create` | Branch or tag created | — |
| `delete` | Branch or tag deleted | — |
| `fork` | Repository forked | — |
| `release` | Release published/created/etc. | `types` |
| `check_run` / `check_suite` | CI check events | `types` |
| `status` | Commit status changes | — |

### Issue/Discussion Events

| Event | Description |
|-------|-------------|
| `issues` | Issue opened, edited, labeled, etc. |
| `issue_comment` | Comment on issue or PR |
| `discussion` | Discussion created, answered, etc. |
| `discussion_comment` | Comment on discussion |
| `label` | Label created, edited, deleted |
| `milestone` | Milestone created, closed, etc. |

### Scheduled and Manual

```yaml
on:
  schedule:
    - cron: '0 9 * * 1-5'       # Weekdays at 9am UTC

  workflow_dispatch:             # Manual trigger via UI/API
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options: [staging, production]
      dry_run:
        type: boolean
        default: false

  repository_dispatch:           # External webhook trigger
    types: [deploy, rollback]

  workflow_call:                 # Called by another workflow (reusable)
    inputs:
      version:
        type: string
        required: true
    secrets:
      TOKEN:
        required: true
    outputs:
      artifact_id:
        value: ${{ jobs.build.outputs.artifact_id }}
```

### Other Events

`deployment`, `deployment_status`, `page_build`, `project`, `project_card`, `project_column`, `public`, `registry_package`, `watch` (starred), `merge_group`, `workflow_run`

**`workflow_run`** — triggers when another workflow completes:
```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
```

---

## Workflow Syntax

### Jobs

```yaml
jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest          # Required: runner label
    needs: [lint]                   # Wait for other jobs
    if: github.event_name == 'push'
    timeout-minutes: 30
    continue-on-error: true         # Don't fail workflow if job fails
    environment: production         # Link to environment
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
      cancel-in-progress: true
    outputs:
      result: ${{ steps.test.outputs.result }}
    permissions:
      contents: read
    env:
      CI: true
    steps: [...]
```

### Steps

```yaml
steps:
  # Use an action
  - name: Checkout
    id: checkout
    uses: actions/checkout@v4
    with:
      fetch-depth: 0
      token: ${{ secrets.GITHUB_TOKEN }}

  # Run a shell command
  - name: Build
    run: |
      npm ci
      npm run build
    shell: bash                     # bash (default), sh, pwsh, python, cmd
    working-directory: ./frontend
    env:
      API_URL: ${{ vars.API_URL }}

  # Conditional step
  - name: Deploy
    if: success() && github.ref == 'refs/heads/main'
    run: ./deploy.sh

  # Capture output
  - name: Set version
    id: version
    run: echo "tag=$(git describe --tags)" >> $GITHUB_OUTPUT

  - name: Use output
    run: echo "Version is ${{ steps.version.outputs.tag }}"
```

### Special Shell Syntax

```bash
# Set environment variable for subsequent steps
echo "MY_VAR=value" >> $GITHUB_ENV

# Set step output
echo "result=success" >> $GITHUB_OUTPUT

# Add to PATH
echo "/custom/bin" >> $GITHUB_PATH

# Multi-line output
{
  echo "summary<<EOF"
  cat report.txt
  echo "EOF"
} >> $GITHUB_OUTPUT

# Write to step summary (shown in UI)
echo "## Build Results" >> $GITHUB_STEP_SUMMARY
```

---

## Contexts

Contexts are objects accessed with `${{ context.property }}` syntax.

### `github` Context

| Property | Description |
|----------|-------------|
| `github.event_name` | Triggering event name |
| `github.event` | Full webhook payload |
| `github.sha` | Commit SHA |
| `github.ref` | Full ref (`refs/heads/main`) |
| `github.ref_name` | Short branch/tag name |
| `github.ref_type` | `branch` or `tag` |
| `github.head_ref` | PR source branch |
| `github.base_ref` | PR target branch |
| `github.actor` | User who triggered the run |
| `github.triggering_actor` | User who triggered (may differ for re-runs) |
| `github.repository` | `owner/repo` |
| `github.repository_owner` | Owner name |
| `github.run_id` | Unique run ID |
| `github.run_number` | Sequential run number |
| `github.run_attempt` | Retry attempt number |
| `github.job` | Current job ID |
| `github.workflow` | Workflow name |
| `github.workspace` | Runner workspace path |
| `github.server_url` | GitHub server URL |
| `github.api_url` | GitHub API URL |
| `github.token` | Same as `secrets.GITHUB_TOKEN` |

### Other Contexts

| Context | Description |
|---------|-------------|
| `env.VAR` | Environment variables set in workflow |
| `vars.VAR` | Configuration variables (repo/org/env) |
| `secrets.NAME` | Encrypted secrets |
| `inputs.NAME` | `workflow_dispatch` or `workflow_call` inputs |
| `job.status` | Current job status: `success`, `failure`, `cancelled` |
| `job.container.id` | Container ID |
| `steps.<id>.outputs.<name>` | Output from a previous step |
| `steps.<id>.outcome` | Step result before `continue-on-error` |
| `steps.<id>.conclusion` | Step result after `continue-on-error` |
| `runner.os` | `Linux`, `Windows`, `macOS` |
| `runner.arch` | `X64`, `ARM64` |
| `runner.name` | Runner name |
| `runner.tool_cache` | Path to tool cache |
| `runner.temp` | Temporary directory path |
| `matrix.PROPERTY` | Current matrix value |
| `needs.<job>.outputs.<name>` | Output from a needed job |
| `needs.<job>.result` | Result of a needed job |

---

## Expressions

Expressions use `${{ }}` syntax and can appear in most value fields.

### Operators

`==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`

### Functions

| Function | Description |
|----------|-------------|
| `contains(search, item)` | String/array containment check |
| `startsWith(string, prefix)` | Prefix check (case-insensitive) |
| `endsWith(string, suffix)` | Suffix check (case-insensitive) |
| `format(string, val0, val1, ...)` | String formatting with `{0}`, `{1}` placeholders |
| `join(array, separator)` | Join array elements into string |
| `toJSON(value)` | Convert to JSON string |
| `fromJSON(string)` | Parse JSON string |
| `hashFiles(path)` | SHA-256 hash of matched files |

### Status Check Functions

These are used in `if:` conditions:

| Function | True when |
|----------|-----------|
| `success()` | All previous steps/jobs succeeded (default behavior) |
| `failure()` | Any previous step/job failed |
| `always()` | Always, regardless of status |
| `cancelled()` | Workflow was cancelled |

```yaml
- name: Notify on failure
  if: failure()
  run: ./notify.sh

- name: Always cleanup
  if: always()
  run: ./cleanup.sh
```

---

## GITHUB_TOKEN Permissions

Permissions can be set at workflow or job level. Values: `read`, `write`, `none`.

```yaml
permissions:
  actions: read           # Workflow runs and artifacts
  attestations: write     # Artifact attestations
  checks: write           # Check runs and suites
  contents: write         # Repository contents, commits, tags
  deployments: write      # Deployments
  discussions: read       # GitHub Discussions
  id-token: write         # OIDC JWT token (needed for cloud auth)
  issues: write           # Issues and comments
  models: read            # GitHub Models inference
  packages: write         # GitHub Packages
  pages: write            # GitHub Pages
  pull-requests: write    # PRs and PR reviews
  repository-projects: read  # Projects (classic)
  security-events: write  # Code scanning, secret scanning
  statuses: write         # Commit statuses
```

Set `permissions: {}` to grant no permissions. Omitting a key defaults to `none` when any key is set.

---

## Secrets and Variables

### Scopes

| Scope | Access | Set in |
|-------|--------|--------|
| Repository secret | That repo only | Repo Settings > Secrets |
| Environment secret | Jobs using that environment | Repo Settings > Environments |
| Organization secret | Selected/all repos in org | Org Settings > Secrets |
| Repository variable | That repo only | Repo Settings > Variables |
| Environment variable | Jobs using that environment | Repo Settings > Environments |
| Organization variable | Selected/all repos in org | Org Settings > Variables |

```yaml
env:
  DB_URL: ${{ secrets.DATABASE_URL }}    # Secret
  API_URL: ${{ vars.API_BASE_URL }}      # Variable (plain text, visible in logs)
```

Secrets are masked in logs. Variables are not masked. Neither can be used in `if:` expressions directly (use `env` intermediary for conditionals on secrets).

---

## Artifacts

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: build-output          # Artifact name (default: artifact)
    path: |
      dist/
      !dist/**/*.map            # Exclusion pattern
    retention-days: 30          # Default: 90, max: 90
    if-no-files-found: error    # error | warn | ignore (default: warn)
    compression-level: 6        # 0-9 (default: 6)
    overwrite: false

- name: Download artifact
  uses: actions/download-artifact@v4
  with:
    name: build-output          # Omit to download all artifacts
    path: ./downloaded          # Default: current directory
    run-id: ${{ github.run_id }}  # Download from specific run (needs actions:read)
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

Artifacts are stored per workflow run. Use `actions/upload-artifact` and `actions/download-artifact` from the same run to pass files between jobs.

---

## Caching

```yaml
- name: Cache dependencies
  id: cache
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Install (only if cache miss)
  if: steps.cache.outputs.cache-hit != 'true'
  run: npm ci
```

### Cache Key Strategies

| Pattern | Use case |
|---------|----------|
| `${{ runner.os }}-<tool>-${{ hashFiles('lockfile') }}` | Exact match on lockfile |
| `${{ runner.os }}-<tool>-${{ github.sha }}` | Per-commit cache |
| `${{ runner.os }}-<tool>-${{ github.ref_name }}-` | Per-branch with fallback |

`restore-keys` are prefix-matched fallbacks in order. The cache action sets `cache-hit` output to `'true'` on exact key match.

- Cache limit: 10 GB per repository. Entries unused for 7 days are evicted.
- `actions/cache/save` and `actions/cache/restore` are available as separate actions.

---

## Job Matrix

```yaml
jobs:
  test:
    strategy:
      fail-fast: false            # Don't cancel others on failure (default: true)
      max-parallel: 3             # Limit concurrent jobs
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: ['18', '20', '22']
        include:
          - os: ubuntu-latest
            node: '20'
            experimental: true    # Add extra property for specific combo
          - os: windows-latest
            extra_flag: '--no-sandbox'
        exclude:
          - os: macos-latest
            node: '18'
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

Matrix generates a job for each combination. `include` adds to existing combinations or creates new ones. `exclude` removes combinations. Access values via `${{ matrix.PROPERTY }}`.

---

## Reusable Workflows

### Defining a Reusable Workflow

```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
      image_tag:
        type: string
        default: latest
    secrets:
      DEPLOY_KEY:
        required: true
    outputs:
      deployment_url:
        description: "URL of the deployed environment"
        value: ${{ jobs.deploy.outputs.url }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - name: Deploy
        id: deploy
        run: ./deploy.sh ${{ inputs.environment }}
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

### Calling a Reusable Workflow

```yaml
jobs:
  call-deploy:
    uses: org/repo/.github/workflows/reusable-deploy.yml@main
    with:
      environment: production
      image_tag: ${{ needs.build.outputs.tag }}
    secrets:
      DEPLOY_KEY: ${{ secrets.PROD_DEPLOY_KEY }}
    # Or pass all secrets: secrets: inherit

  post-deploy:
    needs: call-deploy
    steps:
      - run: echo "Deployed to ${{ needs.call-deploy.outputs.deployment_url }}"
```

Reusable workflow jobs count against the concurrency limit. A caller can call up to 20 reusable workflows. Nesting is supported up to 4 levels deep.

---

## Composite Actions

Composite actions package multiple steps into a reusable action, defined in `action.yml`.

```yaml
# .github/actions/setup-and-build/action.yml
name: Setup and Build
description: Install dependencies and build the project
inputs:
  node-version:
    description: Node.js version
    required: false
    default: '20'
  working-directory:
    description: Directory to build in
    default: '.'
outputs:
  build-path:
    description: Path to build output
    value: ${{ steps.build.outputs.path }}

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - name: Install
      run: npm ci
      shell: bash
      working-directory: ${{ inputs.working-directory }}
    - name: Build
      id: build
      run: |
        npm run build
        echo "path=${{ inputs.working-directory }}/dist" >> $GITHUB_OUTPUT
      shell: bash
      working-directory: ${{ inputs.working-directory }}
```

Each step in a composite action must specify `shell`. Call it like any action:

```yaml
- uses: ./.github/actions/setup-and-build
  with:
    node-version: '22'
```

---

## Environment Deployments

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://example.com   # Displayed as link in UI
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

### Protection Rules

Configured in Repo Settings > Environments:
- **Required reviewers** — up to 6 users/teams must approve before job runs
- **Wait timer** — delay (minutes) before job runs
- **Deployment branches** — restrict which branches can deploy
- **Custom deployment protection rules** — call an external webhook for approval

Jobs targeting a protected environment are paused until all protection rules pass.

---

## Actions REST API

Base URL: `https://api.github.com`

### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/workflows` | List workflows |
| `GET` | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}` | Get workflow |
| `POST` | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` | Trigger `workflow_dispatch` |
| `GET` | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | List runs for workflow |

### Workflow Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/runs` | List all runs |
| `GET` | `/repos/{owner}/{repo}/actions/runs/{run_id}` | Get run |
| `DELETE` | `/repos/{owner}/{repo}/actions/runs/{run_id}` | Delete run |
| `POST` | `/repos/{owner}/{repo}/actions/runs/{run_id}/cancel` | Cancel run |
| `POST` | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun` | Re-run all jobs |
| `POST` | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` | Re-run failed jobs |
| `GET` | `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` | Download logs (redirect to ZIP) |
| `DELETE` | `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` | Delete logs |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | List jobs for run |
| `GET` | `/repos/{owner}/{repo}/actions/jobs/{job_id}` | Get job |
| `GET` | `/repos/{owner}/{repo}/actions/jobs/{job_id}/logs` | Download job logs |

### Artifacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/artifacts` | List repo artifacts |
| `GET` | `/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts` | List run artifacts |
| `GET` | `/repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | Get artifact |
| `DELETE` | `/repos/{owner}/{repo}/actions/artifacts/{artifact_id}` | Delete artifact |
| `GET` | `/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip` | Download artifact ZIP |

### Secrets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/secrets` | List repo secrets (names only) |
| `GET` | `/repos/{owner}/{repo}/actions/secrets/{name}` | Get secret metadata |
| `PUT` | `/repos/{owner}/{repo}/actions/secrets/{name}` | Create or update secret |
| `DELETE` | `/repos/{owner}/{repo}/actions/secrets/{name}` | Delete secret |
| `GET` | `/repos/{owner}/{repo}/actions/secrets/public-key` | Get public key for encryption |
| `GET` | `/orgs/{org}/actions/secrets` | List org secrets |
| `GET` | `/repos/{owner}/{repo}/environments/{env}/secrets` | List environment secrets |

Secrets must be encrypted with the repo's public key (libsodium sealed box) before upload.

### Variables

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/variables` | List repo variables |
| `POST` | `/repos/{owner}/{repo}/actions/variables` | Create variable |
| `GET` | `/repos/{owner}/{repo}/actions/variables/{name}` | Get variable |
| `PATCH` | `/repos/{owner}/{repo}/actions/variables/{name}` | Update variable |
| `DELETE` | `/repos/{owner}/{repo}/actions/variables/{name}` | Delete variable |
| `GET` | `/orgs/{org}/actions/variables` | List org variables |
| `GET` | `/repos/{owner}/{repo}/environments/{env}/variables` | List environment variables |

### Runners

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{owner}/{repo}/actions/runners` | List self-hosted runners |
| `GET` | `/repos/{owner}/{repo}/actions/runners/{runner_id}` | Get runner |
| `DELETE` | `/repos/{owner}/{repo}/actions/runners/{runner_id}` | Delete runner |
| `GET` | `/repos/{owner}/{repo}/actions/runners/downloads` | List runner applications |
| `POST` | `/repos/{owner}/{repo}/actions/runners/registration-token` | Create registration token |
| `POST` | `/repos/{owner}/{repo}/actions/runners/remove-token` | Create remove token |
| `GET` | `/orgs/{org}/actions/runners` | List org runners |

---

## Self-Hosted Runners

### Setup

1. Go to Repo/Org Settings > Actions > Runners > New self-hosted runner
2. Download and configure the runner application
3. Runner registers with GitHub using a short-lived registration token

```bash
./config.sh --url https://github.com/org/repo --token TOKEN
./run.sh         # Interactive
# Or as a service:
sudo ./svc.sh install && sudo ./svc.sh start
```

### Runner Labels and Targeting

```yaml
runs-on: [self-hosted, linux, x64, gpu]   # All labels must match
runs-on: self-hosted                        # Any self-hosted runner
```

Default labels applied automatically: `self-hosted`, OS (`linux`, `windows`, `macos`), architecture (`x64`, `arm64`, `arm`).

Custom labels can be added during registration or via the API/UI.

### Runner Groups

- Runners can be organized into groups (org-level)
- Groups control which repositories can use the runners
- Default group: all repositories in org

### Security Considerations

- **Do not use self-hosted runners with public repositories** — PRs from forks can execute arbitrary code on the runner
- Runner process has access to the host system; use ephemeral runners (re-image after each job) for sensitive workloads
- Use `--ephemeral` flag or just-in-time (JIT) tokens for single-use runners
- JIT token endpoint: `POST /repos/{owner}/{repo}/actions/runners/generate-jitconfig`

### Runner Environment Variables

| Variable | Description |
|----------|-------------|
| `RUNNER_NAME` | Runner name |
| `RUNNER_OS` | `Linux`, `Windows`, `macOS` |
| `RUNNER_ARCH` | `X64`, `ARM64`, `ARM` |
| `RUNNER_TEMP` | Temp directory (cleaned after job) |
| `RUNNER_TOOL_CACHE` | Cached tool versions directory |
| `RUNNER_WORKSPACE` | Workspace root for all repos |
