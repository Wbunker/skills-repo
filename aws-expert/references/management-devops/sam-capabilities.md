# AWS SAM — Capabilities Reference

For CLI commands, see [sam-cli.md](sam-cli.md).

## AWS SAM (Serverless Application Model)

**Purpose**: Open-source framework that extends CloudFormation with simplified syntax for defining serverless applications; reduces hundreds of lines of CloudFormation to concise resource declarations and handles packaging, local testing, and deployment of Lambda-based architectures.

### Core Concepts

| Concept | Description |
|---|---|
| **SAM template** | A `template.yaml` (or `.json`) file declaring serverless resources; identical to a CloudFormation template but with the `Transform: AWS::Serverless-2016-10-31` directive that triggers macro expansion |
| **Transform** | CloudFormation macro (`AWS::Serverless-2016-10-31`) that expands SAM shorthand into full CloudFormation resources before deployment |
| **SAM CLI** | Local development and deployment tool (`sam`); wraps CloudFormation for deploy and provides Docker-based local invocation |
| **Build artifact** | Output of `sam build`; a `.aws-sam/build/` directory containing compiled/packaged code ready for upload |
| **Changeset** | CloudFormation changeset created by `sam deploy`; SAM surfaces the diff before applying it |
| **Accelerate / Sync** | `sam sync` feature that hot-updates Lambda code and configuration directly without going through full CloudFormation changesets (faster iteration loop) |
| **Serverless Application Repository (SAR)** | Managed catalog for sharing and deploying packaged SAM applications; `sam publish` pushes an app to SAR |

---

### SAM Resource Types

| Resource Type | CloudFormation Expansion | Description |
|---|---|---|
| `AWS::Serverless::Function` | `AWS::Lambda::Function` + IAM role + event source mappings | Lambda function with event triggers declared inline |
| `AWS::Serverless::Api` | `AWS::ApiGateway::RestApi` + stage + deployment | REST API (API Gateway v1); can reference an OpenAPI definition |
| `AWS::Serverless::HttpApi` | `AWS::ApiGatewayV2::Api` + stage | HTTP API (API Gateway v2); lower latency, lower cost, JWT authorizers built-in |
| `AWS::Serverless::SimpleTable` | `AWS::DynamoDB::Table` | DynamoDB table with a single primary key and optional TTL |
| `AWS::Serverless::StateMachine` | `AWS::StepFunctions::StateMachine` + IAM role | Step Functions state machine with event triggers |
| `AWS::Serverless::LayerVersion` | `AWS::Lambda::LayerVersion` | Lambda layer; SAM handles packaging the layer content directory |
| `AWS::Serverless::Application` | `AWS::CloudFormation::Stack` | Nested application; pulls from SAR or a local/S3 template |
| `AWS::Serverless::Connector` | IAM policies between two resources | Generates least-privilege IAM policies for resource-to-resource access without writing policy JSON |

---

### AWS::Serverless::Function — Event Sources

| Event Type | Trigger |
|---|---|
| `Api` | API Gateway REST API (v1) |
| `HttpApi` | API Gateway HTTP API (v2) |
| `S3` | S3 bucket notifications |
| `SQS` | SQS queue message consumption |
| `SNS` | SNS topic subscription |
| `DynamoDB` | DynamoDB Streams |
| `Kinesis` | Kinesis Data Streams |
| `EventBridgeRule` | EventBridge rule (scheduled or pattern-based) |
| `Schedule` | EventBridge Scheduler expression |
| `Cognito` | Cognito User Pool triggers |
| `IoTRule` | IoT Rules Engine |
| `MQ` | Amazon MQ broker |
| `MSK` | Amazon MSK (Managed Kafka) |
| `SelfManagedKafka` | Self-managed Kafka cluster |
| `AlbEvent` | Application Load Balancer |

---

### Global Section

`Globals` applies defaults to all functions, APIs, or tables in the template — avoids repeating the same property on every resource:

```yaml
Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Environment:
      Variables:
        LOG_LEVEL: INFO
    Layers:
      - !Ref SharedDepsLayer
  Api:
    Cors:
      AllowOrigin: "'*'"
      AllowHeaders: "'Content-Type,Authorization'"
```

Individual resources can override any global value.

---

### SAM Policy Templates

SAM ships built-in policy templates that expand to scoped IAM policies — no policy JSON required:

| Template | Grants |
|---|---|
| `S3ReadPolicy` | `s3:GetObject`, `s3:ListBucket` on a named bucket |
| `S3CrudPolicy` | Full CRUD on a named bucket |
| `DynamoDBCrudPolicy` | Full CRUD on a named DynamoDB table |
| `DynamoDBReadPolicy` | Read-only on a named DynamoDB table |
| `SQSPollerPolicy` | Receive/delete messages from a named SQS queue |
| `SQSSendMessagePolicy` | Send messages to a named SQS queue |
| `SNSPublishMessagePolicy` | Publish to a named SNS topic |
| `StepFunctionsExecutionPolicy` | Start execution on a named state machine |
| `SecretsManagerReadWrite` | Read and write a named secret |
| `SSMParameterReadPolicy` | Read SSM parameters under a named path prefix |
| `EventBridgePutEventsPolicy` | PutEvents to a named EventBridge bus |
| `VPCAccessPolicy` | Attach Lambda to a VPC (creates ENIs) |

Usage:
```yaml
Policies:
  - DynamoDBCrudPolicy:
      TableName: !Ref OrdersTable
  - SQSSendMessagePolicy:
      QueueName: !GetAtt DeadLetterQueue.QueueName
```

---

### Connectors (`AWS::Serverless::Connector`)

Connectors generate least-privilege IAM policies between two SAM/CloudFormation resources without hand-writing policy JSON:

```yaml
MyConnector:
  Type: AWS::Serverless::Connector
  Properties:
    Source:
      Id: ProcessOrderFunction
    Destination:
      Id: OrdersTable
    Permissions:
      - Read
      - Write
```

Supported permission sets: `Read`, `Write`. SAM determines the correct IAM actions based on source and destination resource types.

---

### Local Development with SAM CLI

SAM CLI uses Docker to emulate the Lambda execution environment locally.

| Command | Purpose |
|---|---|
| `sam local invoke` | Invoke a single function once with an event payload |
| `sam local start-api` | Start a local HTTP server emulating API Gateway; hot-reloads on code change |
| `sam local start-lambda` | Start a local Lambda endpoint compatible with the AWS SDK (`endpoint-url`) |
| `sam local generate-event` | Generate sample event payloads for any trigger type |

Supported runtimes for local emulation: Node.js, Python, Java, .NET, Ruby, Go, custom runtime.

---

### SAM Accelerate (`sam sync`)

`sam sync` bypasses CloudFormation changesets for faster iteration:

| Change type | Method used |
|---|---|
| Lambda function code | Direct `UpdateFunctionCode` API call (seconds) |
| Lambda configuration | Direct `UpdateFunctionConfiguration` (seconds) |
| Layer version | Direct upload + alias update |
| API Gateway definition | Direct `PutRestApi` |
| Infrastructure changes (new resources, IAM) | Falls back to CloudFormation changeset |

Use `--watch` flag to enable file-system watching for continuous sync.

---

### SAM Pipeline

`sam pipeline` bootstraps CI/CD infrastructure for SAM applications:

| Command | Purpose |
|---|---|
| `sam pipeline bootstrap` | Create IAM roles, S3 artifact bucket, and ECR repo for a pipeline stage (dev/prod) |
| `sam pipeline init` | Generate pipeline config files for CodePipeline, GitHub Actions, GitLab, Jenkins, or Bitbucket |

The generated pipeline configuration runs `sam build`, `sam package`, and `sam deploy` in sequence with stage-appropriate IAM roles.

---

### Deployment Workflow

```
sam init          → Scaffold a new project from a template
sam build         → Compile/package code into .aws-sam/build/
sam local invoke  → Test locally with Docker
sam deploy --guided → Interactive first-time deploy (writes samconfig.toml)
sam deploy        → Deploy using saved samconfig.toml (CI/CD friendly)
sam sync --watch  → Continuous hot-sync for rapid iteration
sam logs          → Tail CloudWatch Logs for deployed functions
sam traces        → View X-Ray traces for recent invocations
sam delete        → Delete the CloudFormation stack and S3 artifacts
```

---

### samconfig.toml

`sam deploy --guided` writes deployment parameters to `samconfig.toml`, making subsequent `sam deploy` non-interactive:

```toml
version = 0.1

[default.global.parameters]
stack_name = "my-app"

[default.build.parameters]
cached = true
parallel = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = true
resolve_s3 = true
region = "us-east-1"
s3_prefix = "my-app"
```

Multiple environments can be configured as named profiles (`[prod.deploy.parameters]`) and selected with `--config-env prod`.

---

### SAM vs CDK vs CloudFormation

| Dimension | SAM | CDK | CloudFormation |
|---|---|---|---|
| **Abstraction level** | Moderate — shorthand YAML for serverless | High — general-purpose programming language | Low — raw JSON/YAML |
| **Best for** | Lambda-centric serverless apps | Complex multi-service architectures, reusable constructs | Full control, existing templates, non-serverless |
| **Local testing** | Built-in (`sam local`) | No native local; use CDK + SAM via `cdk synth \| sam local` | No |
| **Language** | YAML (superset of CloudFormation) | TypeScript, Python, Java, C#, Go | YAML / JSON |
| **Deployment** | `sam deploy` (wraps CloudFormation) | `cdk deploy` (synthesizes then calls CloudFormation) | `aws cloudformation deploy` |
| **Hot iteration** | `sam sync --watch` | `cdk watch` (hotswap for Lambda/ECS) | None |
| **Policy authoring** | Policy templates + Connectors | IAM grant methods on L2 constructs | Manual IAM JSON |

---

### Key Patterns

- **API + Lambda + DynamoDB**: Define `AWS::Serverless::HttpApi`, one or more `AWS::Serverless::Function` with `HttpApi` event, and `AWS::Serverless::SimpleTable`; use `DynamoDBCrudPolicy` — no IAM JSON needed
- **Event-driven pipeline**: SQS source → Lambda processor → DynamoDB writer using Connectors for all IAM wiring
- **Multi-stage deployment**: Use `samconfig.toml` named profiles (`dev`, `staging`, `prod`) + `sam pipeline` for CodePipeline/GitHub Actions
- **Shared dependencies**: Package common libraries as `AWS::Serverless::LayerVersion` and reference via `Globals`
- **Nested apps from SAR**: Pull pre-built serverless components from the Serverless Application Repository with `AWS::Serverless::Application` + SAR URL
