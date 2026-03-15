# AWS CDK — Capabilities Reference
For CLI commands, see [cdk-cli.md](cdk-cli.md).

**Purpose**: Open-source framework for defining cloud infrastructure in general-purpose programming languages (TypeScript, Python, Java, C#, Go), synthesized into CloudFormation templates.

## Core Concepts

| Concept | Description |
|---|---|
| **App** | Root of the CDK construct tree; represents the entire CDK application |
| **Stack** | Unit of deployment; maps 1:1 to a CloudFormation stack; scoped to one account and region by default |
| **Stage** | Logical grouping of one or more stacks for a deployment target (e.g., dev, staging, prod); enables multi-stage pipelines |
| **Construct** | The basic building block; represents a cloud component; can contain other constructs |
| **L1 construct (Cfn*)** | Direct CloudFormation resource mapping (e.g., `CfnBucket`); all properties available, no defaults |
| **L2 construct** | Curated, opinionated abstractions with sensible defaults, grant methods, and event subscriptions (e.g., `s3.Bucket`) |
| **L3 construct (Pattern)** | Higher-level multi-service patterns (e.g., `ecs_patterns.ApplicationLoadBalancedFargateService`) |
| **Asset** | Files or Docker images bundled with the app and uploaded to S3/ECR during `cdk deploy`; referenced in stack |
| **Context** | Key-value pairs stored in `cdk.json` or passed via `--context`; used for feature flags and environment config |
| **Bootstrapping** | One-time setup (`cdk bootstrap`) that creates a CDKToolkit CloudFormation stack with an S3 bucket, ECR repo, and IAM roles needed for deployments |
| **Aspect** | Visitor pattern for traversing the construct tree and applying cross-cutting logic (e.g., tagging all resources, enforcing encryption) |
| **cdk-nag** | Third-party library that applies security and compliance rule packs (NIST, HIPAA, PCI, AWS Solutions) as CDK Aspects |
| **CDK Pipelines** | High-level construct for self-mutating CI/CD pipelines; pipeline updates itself before deploying application stages |

## Construct Levels Compared

| Level | Example | Use case |
|---|---|---|
| **L1** | `new s3.CfnBucket(this, 'Bucket', { versioningConfiguration: { status: 'Enabled' } })` | Full control; escape hatch to CloudFormation |
| **L2** | `new s3.Bucket(this, 'Bucket', { versioned: true })` | Typical use; sensible defaults, IAM grant methods |
| **L3** | `new ecsPatterns.ApplicationLoadBalancedFargateService(...)` | Entire architecture patterns in a few lines |

## CDK Lifecycle

```
cdk synth     → Synthesize CloudFormation template(s) from CDK code
cdk diff      → Show diff between deployed stack and local code
cdk deploy    → Synthesize + deploy to AWS (calls CloudFormation)
cdk destroy   → Delete the stack
cdk bootstrap → Set up CDKToolkit stack in target account/region
```

## Key Features

| Feature | Description |
|---|---|
| **Hotswap deployments** | `cdk deploy --hotswap` skips CloudFormation for Lambda, ECS, and Step Functions changes; directly updates the resource for faster iteration |
| **Watch mode** | `cdk watch` monitors source files and automatically hotswaps or deploys on changes |
| **CDK Pipelines** | Self-mutating: the pipeline first updates its own definition, then deploys application stages; uses CodePipeline + CodeBuild under the hood |
| **Escape hatch** | Access the underlying L1 construct via `.node.defaultChild as CfnXxx` to set any CloudFormation property not exposed by L2 |
| **Cross-stack references** | Reference a resource from another stack in the same app; CDK automatically creates CloudFormation exports/imports |
| **Aspects** | `Aspects.of(app).add(new MyAspect())` visits every node; common uses: tag all resources, enforce bucket encryption, run cdk-nag checks |
