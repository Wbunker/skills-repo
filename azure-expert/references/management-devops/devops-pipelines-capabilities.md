# Azure DevOps & GitHub Actions — Capabilities

## Azure DevOps Overview

Azure DevOps Services is Microsoft's cloud-hosted DevOps platform providing integrated tools for the full software development lifecycle. Access at [dev.azure.com](https://dev.azure.com).

**Organization**: Top-level container → Projects → Services (Boards, Repos, Pipelines, Artifacts, Test Plans).

---

## Azure Boards

Work item tracking and agile project management:

### Work Item Types

| Type | Description |
|---|---|
| **Epic** | Large body of work spanning multiple sprints/quarters |
| **Feature** | Functional capability (child of Epic) |
| **User Story** / **Product Backlog Item** | User-facing work (child of Feature) |
| **Task** | Implementation task (child of Story) |
| **Bug** | Defect to be fixed |
| **Test Case** | Manual or automated test scenario |
| **Impediment** / **Issue** | Blocking item |

### Views

- **Backlog**: Prioritized list of work items.
- **Sprint Board (Kanban)**: Columns by state (To Do / Active / Resolved / Done) for sprint work.
- **Queries**: Ad-hoc saved queries for filtering work items.
- **Delivery Plans**: Timeline view across multiple teams.
- **Analytics / Dashboards**: Velocity charts, burndown, cumulative flow.

### Process Templates

| Template | Description |
|---|---|
| **Agile** | User Stories, Tasks, Bugs — for Scrum/Kanban teams |
| **Scrum** | Product Backlog Items, Sprints, Bugs |
| **CMMI** | Requirements, Change Requests — for formal processes |
| **Basic** | Issues and Tasks — simplest structure |

---

## Azure Repos

Git-based version control:

### Key Features

- Unlimited private Git repositories per organization.
- **Branch policies**: Require code reviews, linked work items, successful builds before merge.
- **Pull requests**: Code review workflow with comments, votes (Approve / Approve with suggestions / Wait for author / Reject).
- **Branch protection**: Enforce policies on `main`/`develop` branches.
- **TFVC** (Team Foundation Version Control): Legacy centralized VCS — use Git for new projects.

### Branch Policies (per branch)

| Policy | Description |
|---|---|
| Minimum reviewers | Require N approvals before merge |
| Linked work items | Require work item association |
| Comment resolution | All comments must be resolved |
| Status checks | Require CI pipeline success |
| Limit merge types | Allow only squash, rebase, no-fast-forward |
| Auto-complete | Auto-merge when conditions met |

---

## Azure Pipelines

CI/CD engine for any language, platform, and cloud.

### YAML Pipeline Structure

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main, release/*]
  paths:
    exclude: [docs/**, '*.md']

pr:
  branches:
    include: [main]
  autoCancel: true

schedules:
- cron: '0 2 * * 1-5'  # 2 AM UTC weekdays
  displayName: 'Nightly Build'
  branches:
    include: [main]
  always: true

variables:
  solution: '**/*.sln'
  buildConfiguration: 'Release'
  vmImage: ubuntu-latest

# Variable groups from Azure DevOps Library
variables:
- group: production-secrets
- name: myVariable
  value: myValue

# Stages → Jobs → Steps
stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildJob
    pool:
      vmImage: $(vmImage)
    steps:
    - task: UseDotNet@2
      inputs:
        version: '8.x'

    - script: dotnet build $(solution) --configuration $(buildConfiguration)
      displayName: 'Build'

    - task: DotNetCoreCLI@2
      displayName: 'Test'
      inputs:
        command: test
        projects: '**/*Tests/*.csproj'
        arguments: '--configuration $(buildConfiguration) --collect "Code coverage"'

    - task: PublishPipelineArtifact@1
      inputs:
        targetPath: '$(Build.ArtifactStagingDirectory)'
        artifact: 'drop'

- stage: DeployDev
  displayName: 'Deploy to Dev'
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployDev
    environment: 'dev'                   # linked to Azure DevOps Environment
    pool:
      vmImage: ubuntu-latest
    strategy:
      runOnce:
        deploy:
          steps:
          - download: current
            artifact: drop
          - task: AzureCLI@2
            displayName: 'Deploy to Azure'
            inputs:
              azureSubscription: 'my-azure-service-connection'
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                az webapp deploy --resource-group myRG --name mywebapp \
                  --src-path $(Pipeline.Workspace)/drop/app.zip --type zip

- stage: DeployProd
  dependsOn: DeployDev
  jobs:
  - deployment: DeployProd
    environment: 'production'            # has approval gate configured
    pool:
      vmImage: ubuntu-latest
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'prod-azure-service-connection'
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                # Production deployment steps
```

### Matrix Strategy (Multi-Platform)

```yaml
jobs:
- job: Test
  strategy:
    matrix:
      Python38_Linux:
        pythonVersion: '3.8'
        vmImage: 'ubuntu-latest'
      Python310_Linux:
        pythonVersion: '3.10'
        vmImage: 'ubuntu-latest'
      Python310_Windows:
        pythonVersion: '3.10'
        vmImage: 'windows-latest'
    maxParallel: 3
  pool:
    vmImage: $(vmImage)
  steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: $(pythonVersion)
  - script: python -m pytest tests/
```

### Pipeline Templates

Reusable YAML templates for common patterns:

```yaml
# templates/build-dotnet.yml (step template)
parameters:
- name: buildConfig
  type: string
  default: Release
- name: solution
  type: string
  default: '**/*.sln'

steps:
- task: UseDotNet@2
  inputs:
    version: '8.x'
- script: dotnet build ${{ parameters.solution }} --configuration ${{ parameters.buildConfig }}
  displayName: 'Build ${{ parameters.buildConfig }}'
```

```yaml
# Using the template
steps:
- template: templates/build-dotnet.yml
  parameters:
    buildConfig: Release
    solution: 'src/MyApp.sln'
```

```yaml
# Extend from template (enforce required steps, e.g., security scanning)
extends:
  template: templates/secure-pipeline.yml
  parameters:
    buildSteps:
    - script: dotnet build
```

---

## Agents

| Type | Description | OS Support |
|---|---|---|
| **Microsoft-hosted** | Microsoft manages VM, patches, cleanup; fresh VM per job | Ubuntu 22.04/20.04, Windows 2019/2022, macOS 13/14 |
| **Self-hosted** | Customer-managed; persistent, custom software, private network access | Any OS/architecture |
| **Scale set agents** | Self-hosted backed by VMSS; auto-scale based on queue | Windows, Linux |

### Microsoft-Hosted Agent Pools

| Pool Name | Image |
|---|---|
| `ubuntu-latest` | Latest Ubuntu LTS |
| `windows-latest` | Latest Windows Server |
| `macos-latest` | Latest macOS |

### Self-Hosted Agent Setup

```bash
# Download agent software from Azure DevOps org settings
# Configure with PAT or service principal
./config.sh --url https://dev.azure.com/myorg --auth pat --token <PAT>
./run.sh  # start agent (or install as service)
```

---

## Environments

Deployment targets with approvals, checks, and history:

- Created in Azure DevOps under Pipelines → Environments.
- Resource types: Kubernetes namespaces, Virtual Machines (via Azure DevOps agent), generic (no resource).
- **Approval gates**: Require manual approval from specified users/groups before deployment proceeds.
- **Check types**: Business hours, Required template (enforce pipeline template use), Exclusive lock (only one deployment at a time), Query Azure Monitor alerts, Invoke REST API.
- **Deployment history**: Full audit trail of which pipeline/commit deployed to which environment.

---

## Service Connections

Connections from Azure Pipelines to external services:

| Type | Description |
|---|---|
| **Azure Resource Manager** | Connect to Azure subscription/resource group |
| **Docker Registry** | Push/pull from ACR or Docker Hub |
| **GitHub** | Checkout code from GitHub repos |
| **Kubernetes** | Deploy to Kubernetes clusters |
| **npm/NuGet/PyPI** | Authenticate to package registries |
| **SSH** | Connect to remote servers |
| **Generic** | Custom endpoint with username/password or token |

### Azure RM Service Connection Authentication Methods

| Method | Security | Description |
|---|---|---|
| **Workload Identity Federation (OIDC)** | Best | No secrets stored; uses OIDC tokens; recommended for all new connections |
| **Service Principal (secret)** | Medium | Client secret stored in ADO; rotate regularly |
| **Service Principal (certificate)** | Good | Certificate-based auth |
| **Managed Identity** | N/A | Only for self-hosted agents on Azure VMs |

---

## Azure Artifacts

Package management for NuGet, npm, Maven, PyPI, and Universal packages:

- **Feeds**: Package repositories with version management.
- **Upstream sources**: Proxy public registries (nuget.org, npmjs.com, PyPI) through private feed — cache public packages + internal packages in one feed.
- **Retention policies**: Auto-delete old package versions.
- **Scoped feeds**: Org-level or project-level visibility.

```yaml
# Use Azure Artifacts feed in pipeline
- task: NuGetAuthenticate@1  # authenticates to artifacts feed
- task: NuGetRestore@2
  inputs:
    restoreSolution: '$(solution)'
    feedsToUse: select
    vstsFeed: 'myorg/myfeed'
```

---

## GitHub Actions with Azure

### OIDC Authentication (Recommended — No Secrets)

```yaml
# .github/workflows/deploy.yml
permissions:
  id-token: write   # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Azure Login (OIDC)
      uses: azure/login@v2
      with:
        client-id: ${{ secrets.AZURE_CLIENT_ID }}
        tenant-id: ${{ secrets.AZURE_TENANT_ID }}
        subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        # No client-secret needed — uses OIDC federation
```

### OIDC Federated Credential Setup

```bash
# Create app registration for GitHub Actions
APP_ID=$(az ad app create --display-name "GitHub-Actions-MyRepo" --query appId -o tsv)
SP_ID=$(az ad sp create --id $APP_ID --query id -o tsv)

# Add federated credential (for specific repo + branch)
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/my-repo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Add credential for pull requests
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "pull-requests",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/my-repo:pull_request",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Assign Contributor role to subscription
az role assignment create \
  --assignee $SP_ID \
  --role Contributor \
  --scope /subscriptions/{sub-id}

# Store in GitHub secrets:
# AZURE_CLIENT_ID = $APP_ID
# AZURE_TENANT_ID = $(az account show --query tenantId -o tsv)
# AZURE_SUBSCRIPTION_ID = $(az account show --query id -o tsv)
```

### Key GitHub Actions for Azure

| Action | Description |
|---|---|
| `azure/login@v2` | Authenticate to Azure (OIDC or secret) |
| `azure/arm-deploy@v2` | Deploy ARM/Bicep templates |
| `azure/CLI@v2` | Run Azure CLI commands in step |
| `azure/aks-set-context@v3` | Configure kubectl for AKS |
| `azure/container-apps-deploy@v1` | Deploy to Azure Container Apps |
| `azure/webapps-deploy@v3` | Deploy to Azure App Service |
| `azure/functions-action@v1` | Deploy to Azure Functions |
| `Azure/sql-action@v2` | Run SQL scripts against Azure SQL |

---

## DevOps Best Practices

### Branch Strategy

| Strategy | Description | Best For |
|---|---|---|
| **Trunk-based** | All developers commit to `main`; short-lived feature branches (<1 day) | High-velocity teams, microservices |
| **GitFlow** | `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` branches | Release-cadence teams |
| **GitHub Flow** | `main` + feature branches; deploy from `main` | Continuous deployment |

### Deployment Patterns

| Pattern | Description |
|---|---|
| **Blue-green** | Two identical prod environments; switch traffic on deploy |
| **Canary** | Gradually roll out to percentage of traffic |
| **Deployment rings** | Dev → QA → Staging → 5% Prod → Full Prod |
| **Feature flags** | Deploy code off; enable feature for users gradually |

### Pipeline Security

- Use Workload Identity Federation (OIDC) — eliminates secret management.
- Store secrets in Azure Key Vault, not pipeline variables.
- Use branch protection to require successful pipeline before merge.
- Separate service connections per environment (dev/staging/prod) with least-privilege RBAC.
- Use pipeline templates to enforce required security scans (SAST, dependency scanning).
