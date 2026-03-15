# AWS CI/CD Pipeline Tools — Capabilities Reference

For CLI commands, see [cicd-pipeline-cli.md](cicd-pipeline-cli.md).

---

## AWS CodeCommit

**Purpose**: Fully managed private Git repositories hosted on AWS; tightly integrated with IAM for access control, encryption, and event-driven triggers.

> **Closed to New Customers**: CodeCommit stopped accepting new customers in July 2024. Existing customers can continue using it. New projects should use Amazon CodeCatalyst (native AWS), GitHub, GitLab, or Bitbucket — all connectable to CodePipeline via AWS CodeStar Connections.

### Core Features

| Feature | Description |
|---|---|
| **Repository** | A standard Git repository; supports all Git operations (clone, fetch, push, branch, merge, rebase, tag) |
| **Authentication** | HTTPS (IAM credentials via Git Credential Manager or git-remote-codecommit helper) or SSH (upload SSH public key to IAM user) |
| **Encryption** | At-rest encryption using AWS KMS (customer-managed or AWS-managed); in-transit via TLS |
| **Triggers** | Repository triggers fire SNS notifications or invoke Lambda functions on push, create-branch, or delete-branch events |
| **Notifications** | CloudWatch Events (EventBridge) rules for pull request and comment events; notify via SNS, Slack (Chatbot), or email |
| **Approval rule templates** | Enforce N-of-M approvals on pull requests; can be applied automatically to all repositories in an account |
| **Pull requests** | Code review workflow with inline comments, activity feed, approvals, and merge strategies (fast-forward, squash, three-way) |
| **Repository tags** | AWS resource tags on the repository for cost allocation and access control (tag-based IAM conditions) |
| **Cross-account access** | Use IAM roles and resource-based policies to allow cross-account repository access |
| **Migration** | Migrate from GitHub/GitLab/Bitbucket using `git clone --mirror` followed by `git push --mirror` to the CodeCommit remote |

### git-remote-codecommit

`git-remote-codecommit` (GRC) is the recommended HTTPS credential helper — it generates temporary credentials from the IAM role rather than requiring long-term HTTPS Git credentials:

```bash
pip install git-remote-codecommit
git clone codecommit::us-east-1://my-repo
```

---

## AWS CodeBuild

**Purpose**: Fully managed build service; compiles source code, runs tests, and produces deployment-ready artifacts without managing build servers.

### Core Concepts

| Concept | Description |
|---|---|
| **Build project** | Configuration defining source location, environment, buildspec, artifacts, and cache |
| **Buildspec** | YAML file (`buildspec.yml`) or inline definition specifying phases and commands |
| **Build phases** | `install` → `pre_build` → `build` → `post_build`; each phase can have commands and on-failure behavior |
| **Environment** | Docker image defining the build OS and tools; AWS-managed images or custom images from ECR |
| **Compute type** | Instance size for the build environment (e.g., `BUILD_GENERAL1_SMALL`, `BUILD_GENERAL1_LARGE`, ARM, GPU) |
| **Artifacts** | Build outputs uploaded to S3; supports multiple named artifact configurations |
| **Cache** | Local cache (inside build container) or S3 cache; speeds up dependency downloads |
| **Reports** | Test reports (JUnit XML, Cucumber JSON) and code coverage reports (Clover/Cobertura XML); viewable in console |
| **Environment variables** | Plaintext, SSM Parameter Store, or Secrets Manager — injected at build time |
| **Batch builds** | Run a matrix of build configurations from a single trigger |
| **VPC support** | Run builds inside a VPC for access to private resources (RDS, internal APIs) |
| **Concurrent builds** | Up to 60 concurrent builds per account per region by default (adjustable via Service Quotas) |

### Compute Types

`BUILD_GENERAL1_SMALL/MEDIUM/LARGE/2XLARGE` (x86), `BUILD_ARM1_SMALL/LARGE` (ARM), GPU types.

### Source Providers

CodeCommit, GitHub, GitHub Enterprise, Bitbucket, S3, ECR (for container builds), CodeCatalyst.

### Buildspec Example

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      nodejs: 18
    commands:
      - npm ci
  build:
    commands:
      - npm test
      - npm run build
  post_build:
    commands:
      - aws s3 sync dist/ s3://my-bucket/
artifacts:
  files:
    - '**/*'
  base-directory: dist
reports:
  unit-tests:
    files:
      - 'test-results/junit.xml'
    file-format: JUnit
cache:
  paths:
    - node_modules/**/*
```

---

## AWS CodeDeploy

**Purpose**: Automates application deployments to EC2, on-premises servers, Lambda functions, and ECS services.

### Compute Platforms

| Platform | Deployment Types | Traffic Shifting |
|---|---|---|
| **EC2 / On-Premises** | In-place, Blue/Green | Load balancer registration/deregistration |
| **AWS Lambda** | Blue/Green only | Canary, Linear, All-at-once |
| **Amazon ECS** | Blue/Green only | Canary, Linear, All-at-once |

- **EC2/On-Premises**: In-place and blue/green; CodeDeploy agent required on each instance
- **AWS Lambda**: Blue/green only; traffic shifting via weighted alias
- **Amazon ECS**: Blue/green only; integrates with ALB target group shifting

### Deployment Types

| Type | How it works | Rollback |
|---|---|---|
| **In-place** | Stop, install, restart on existing instances; deregister from LB during update | Redeploy previous revision |
| **Blue/Green** | Provision new instances or task set; shift traffic; optionally terminate old | Shift traffic back to original |

### Traffic Shifting Configurations (Lambda/ECS)

| Configuration | Behavior |
|---|---|
| **Canary** | Shift a small % first (e.g., 10%); wait for validation; shift remaining |
| **Linear** | Shift traffic in equal increments on a schedule (e.g., 10% every 5 minutes) |
| **All-at-once** | Shift 100% of traffic immediately |

### Key Concepts

| Concept | Description |
|---|---|
| **Application** | Named container grouping deployment groups and revisions for a compute platform |
| **Deployment group** | Set of target instances/functions/ECS services; defines deployment config, load balancer, rollback triggers |
| **Deployment configuration** | Traffic shifting strategy (e.g., `CodeDeployDefault.AllAtOnce`, `CodeDeployDefault.LambdaCanary10Percent5Minutes`) |
| **AppSpec file** | `appspec.yml` defines file mappings and lifecycle hook scripts for EC2; Lambda/ECS use JSON format |
| **Lifecycle hooks** | Script entry points at each deployment phase (BeforeInstall, AfterInstall, ApplicationStart, ValidateService, etc.) |
| **Rollback** | Automatic rollback on deployment failure or CloudWatch alarm threshold breach; redeploys last known-good revision |
| **Blue/green (EC2)** | Provisions new instances, installs, shifts load balancer traffic, then terminates old instances |
| **Blue/green (ECS/Lambda)** | Creates new task set or Lambda version; shifts traffic incrementally; rollback by shifting back |

### AppSpec File Structure (EC2)

```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/myapp
hooks:
  BeforeInstall:
    - location: scripts/stop_server.sh
      timeout: 60
  AfterInstall:
    - location: scripts/install_dependencies.sh
  ApplicationStart:
    - location: scripts/start_server.sh
  ValidateService:
    - location: scripts/validate.sh
      timeout: 30
```

### EC2 Lifecycle Hooks (In-Place)

`BeforeBlockTraffic` → `BlockTraffic` → `BeforeInstall` → `Install` → `AfterInstall` → `ApplicationStart` → `ValidateService` → `AllowTraffic` → `AfterAllowTraffic`

---

## AWS CodePipeline

**Purpose**: Fully managed continuous delivery service; orchestrates build, test, and deploy stages as a visual workflow.

### Core Concepts

| Concept | Description |
|---|---|
| **Pipeline** | A workflow definition consisting of stages and actions; triggered by source changes or manually |
| **Stage** | A logical phase of the pipeline (e.g., Source, Build, Test, Deploy); stages run sequentially |
| **Action** | A task within a stage; can run in parallel with other actions in the same stage |
| **Artifact** | Files passed between actions; stored in S3; each action can declare input and output artifacts |
| **Artifact store** | S3 bucket where artifacts are passed between actions; one bucket per pipeline per region |
| **Transition** | The link between stages; can be enabled or disabled manually to gate progress |
| **Execution** | One run of the pipeline triggered by a source change or manual start |
| **Manual approval** | An action type that pauses the pipeline; approver uses console/CLI/API to approve/reject with optional comment |
| **Connection** | An AWS CodeStar connection to a third-party provider (GitHub, GitLab, Bitbucket) |

### Pipeline Types

| Type | Description |
|---|---|
| **V1** | Original pipeline type; stage-level parallelism |
| **V2** | Supports pipeline-level variables, stage-level conditions, git-based triggers with filters, and execution modes |

### Execution Modes (V2)

| Mode | Behavior |
|---|---|
| **QUEUED** | Default; queue subsequent runs until current completes |
| **SUPERSEDED** | Newer commit supersedes any queued (but not in-progress) run |
| **PARALLEL** | All triggered runs execute concurrently |

### Action Categories and Providers

| Category | Providers |
|---|---|
| **Source** | CodeCommit, S3, ECR, GitHub (via connection), GitLab, Bitbucket |
| **Build** | CodeBuild, Jenkins |
| **Test** | CodeBuild, Device Farm, third-party |
| **Deploy** | CodeDeploy, CloudFormation, ECS, S3, Elastic Beanstalk, Service Catalog, AppConfig |
| **Approval** | Manual approval |
| **Invoke** | Lambda, Step Functions |

### Cross-Region and Cross-Account

- **Cross-region**: Route an action to a different AWS Region by specifying a region on the action; CodePipeline replicates the artifact to that region
- **Cross-account**: Use a cross-account IAM role on the action; pipeline and target account must share the artifact store KMS key

### Pipeline Triggers (V2)

- Push to branch with optional file path filter
- Pull request events (opened, updated, closed)
- Git tags
- EventBridge rules (scheduled, custom events)

---

## AWS CodeArtifact

**Purpose**: Fully managed artifact repository; stores and proxies software packages (npm, PyPI, Maven, NuGet, Swift, generic).

### Core Concepts

| Concept | Description |
|---|---|
| **Domain** | Top-level grouping; all repositories in a domain share storage and a KMS key; simplifies cross-account sharing |
| **Repository** | Stores packages of one or more formats; can have upstream repositories |
| **Upstream repository** | When a package is not found locally, CodeArtifact fetches it from upstream (another CodeArtifact repo or public registry) |
| **External connection** | Link a repository to a public registry (npmjs.com, pypi.org, Maven Central, NuGet Gallery, etc.) as the outermost upstream |
| **Authorization token** | Short-lived token (12 hours) obtained via CLI; used to configure package managers (npm, pip, mvn) to authenticate against CodeArtifact endpoints |
| **Package formats** | `npm`, `pypi`, `maven`, `nuget`, `swift`, `generic` |
| **Package version** | A specific version of a published package; states: `Published`, `Unfinished`, `Unlisted`, `Archived`, `Disposed`, `Deleted` |

### Cross-Account Access

Grant access to a CodeArtifact domain or repository from another account via resource-based policy on the domain:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::OTHER_ACCOUNT:root"},
    "Action": ["codeartifact:GetAuthorizationToken", "codeartifact:ReadFromRepository"],
    "Resource": "*"
  }]
}
```
