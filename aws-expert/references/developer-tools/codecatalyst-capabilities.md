# Amazon CodeCatalyst — Capabilities Reference

For CLI commands, see [codecatalyst-cli.md](codecatalyst-cli.md).

## Amazon CodeCatalyst

**Purpose**: Unified software development service that brings together project management, source control, CI/CD workflows, and cloud development environments in a single service. Billed through a Space (the top-level organizational unit).

---

## Core Organizational Concepts

| Concept | Description |
|---|---|
| **Space** | Top-level organizational unit and billing container; maps to a company or team; linked to one or more AWS accounts; members have roles within the space |
| **Project** | A collection of work items, source repositories, workflows, dev environments, and team members; scoped inside a Space |
| **Member** | A user invited to a Space or Project; roles: Space Administrator, Project Contributor, Viewer |
| **AWS account connection** | Associates an AWS account and IAM role with a Space; used by workflows to deploy to that account |

---

## Source Repositories

| Feature | Description |
|---|---|
| **Repository** | A Git-based source repository hosted in CodeCatalyst; supports standard Git operations (clone, push, pull, branch, merge) |
| **Branch** | Standard Git branches; default branch configurable; branch protection rules settable |
| **Pull request** | Code review mechanism with inline comments, approvals, and required-reviewer rules |
| **Linked repository** | Connect an external GitHub.com repository to a CodeCatalyst project for workflow triggers without migrating source |

---

## Issues (Backlog & Sprint Boards)

| Feature | Description |
|---|---|
| **Issue** | Work item with title, description, assignee, priority (critical/high/medium/low), status, and estimate |
| **Backlog** | Prioritized list of all open issues for a project |
| **Sprint board** | Kanban-style board showing issues organized by sprint with status columns (To Do / In Progress / Done) |
| **Sprint** | Time-boxed iteration; issues assigned to a sprint appear on the sprint board |

---

## Workflows (CI/CD Pipelines)

Workflows define CI/CD automation for a project; stored as YAML files in the `.codecatalyst/workflows/` directory of a source repository.

### Workflow YAML Structure

```yaml
Name: MyWorkflow
SchemaVersion: "1.0"

Triggers:
  - Type: PUSH
    Branches:
      - main

Actions:
  Build:
    Identifier: aws/build@v1
    Inputs:
      Sources:
        - WorkflowSource
    Configuration:
      Steps:
        - Run: npm ci
        - Run: npm run build
    Outputs:
      Artifacts:
        - Name: BuildOutput
          Files:
            - "dist/**"

  Test:
    Identifier: aws/build@v1
    DependsOn:
      - Build
    Configuration:
      Steps:
        - Run: npm test

  Deploy:
    Identifier: aws/cfn-deploy@v1
    DependsOn:
      - Test
    Environment:
      Name: Production
      Connections:
        - Name: MyAWSConnection
          Role: CodeCatalystDeployRole
    Configuration:
      parameter-overrides: "Env=prod"
      template: deploy/template.yaml
      region: us-east-1
      name: my-stack
```

### Triggers

| Trigger Type | Description |
|---|---|
| **PUSH** | Triggers on Git push; can filter by branch and file paths |
| **PULLREQUEST** | Triggers on pull request events (OPEN, CLOSED, REVISION); used for PR validation workflows |
| **SCHEDULE** | Cron or rate-based schedule (e.g., nightly builds) |
| **MANUAL** | No automatic trigger; workflow must be started manually or via API |

### Action Types

| Action Identifier | Purpose |
|---|---|
| `aws/build@v1` | Run arbitrary shell commands (build, test, package); most versatile action |
| `aws/cfn-deploy@v1` | Deploy a CloudFormation stack |
| `aws/cdk-deploy@v1` | Run `cdk deploy` |
| `aws/sam-deploy@v1` | Deploy a SAM application |
| `aws/ecs-deploy@v1` | Update an ECS service with a new container image |
| `aws/github-actions-runner@v1` | Run GitHub Actions inside a CodeCatalyst workflow |
| `aws/managed-test@v1` | Run tests with reporting integration |

### Variable Management

- **Workflow-level variables**: Defined in `Variables` block; referenced as `${{ variables.MY_VAR }}`
- **Action outputs as variables**: Actions can export named variables consumed by downstream actions via `${{ actions.ActionName.variables.VarName }}`
- **Secrets**: Stored encrypted in the Space; referenced as `${{ secrets.MY_SECRET }}`; never logged

### Compute for Workflows

| Option | Description |
|---|---|
| **CodeCatalyst-managed (Linux.x86-64)** | Default fleet; small, large, xlarge sizes |
| **On-demand fleet** | Specify instance type for compute; auto-provisioned per run |
| **Custom fleet** | Bring your own EC2 instances registered as a custom fleet for persistent tooling |

---

## Dev Environments

Cloud-based ephemeral development environments that run in AWS, pre-configured with project source repositories and your chosen IDE.

### Dev Environment Features

| Feature | Description |
|---|---|
| **Instance type** | `dev.standard1.small` (2 vCPU/4 GB), `dev.standard1.medium` (4 vCPU/8 GB), `dev.standard1.large` (8 vCPU/16 GB), `dev.standard1.xlarge` (16 vCPU/32 GB) |
| **Storage** | 16 GB – 64 GB persistent storage per dev environment |
| **Inactivity timeout** | Auto-stop after 15–60 minutes of inactivity (configurable); state is preserved on resume |
| **Supported IDEs** | AWS Cloud9 (browser), VS Code (desktop via SSH extension), JetBrains IDEs (desktop via JetBrains Gateway), VS Code browser (web) |
| **Devfile** | `.codecatalyst/devfiles/devfile.yaml` — defines container image, tools, extensions, and startup commands for the dev environment |
| **Branch checkout** | Dev environment can be started on any branch; changes persist to the branch |

### Dev Environment Lifecycle

```
Create → Starting → Running → Stopping → Stopped → Deleted
                         ↑_______________|  (resume)
```

---

## Blueprints

| Feature | Description |
|---|---|
| **Blueprint** | A project template that creates source repositories, workflows, issues, and environments from a predefined pattern |
| **AWS blueprints** | Built-in templates (e.g., Web Application, Serverless, Modern Three-Tier Web App, .NET on AWS) |
| **Community blueprints** | Published to CodeCatalyst catalog by the community |
| **Custom blueprints** | Build and publish your own blueprints using the CodeCatalyst Blueprints SDK (TypeScript-based, similar to CDK constructs) |
| **Blueprint version** | Blueprints are versioned; projects can be updated to newer blueprint versions |

---

## Reporting

| Feature | Description |
|---|---|
| **Test reports** | Workflows can publish JUnit XML or other test result formats; viewable in the console with pass/fail counts and history |
| **Code coverage reports** | Coverage XML (Clover, Cobertura, SimpleCov) published from workflow actions; tracks line/branch coverage over time |
| **Report group** | Named container aggregating reports across workflow runs |

---

## Amazon Q Integration

| Feature | Description |
|---|---|
| **Code reviews** | Amazon Q performs automated code reviews on pull requests; flags issues, security vulnerabilities, and suggests fixes |
| **Feature development** | Amazon Q can be assigned an issue and will autonomously generate code and open a pull request |
| **Chat** | Ask Amazon Q questions about the codebase within the CodeCatalyst console |
