# AWS Lambda — Capabilities Reference

For CLI commands, see [lambda-cli.md](lambda-cli.md).

## AWS Lambda

**Purpose**: Serverless compute that runs code in response to events without provisioning or managing servers; scales automatically from zero to thousands of concurrent executions.

### Core Concepts

| Concept | Description |
|---|---|
| **Function** | Unit of deployment; contains code and configuration (runtime, memory, timeout, IAM role) |
| **Execution environment** | Isolated container running one invocation at a time; reused for warm invocations |
| **Runtime** | Language-specific execution environment; managed by AWS or custom (via `provided.al2023`) |
| **Handler** | Entry point function Lambda invokes (e.g., `index.handler`) |
| **Execution role** | IAM role Lambda assumes to access AWS services |
| **Event** | JSON payload passed to the function from the invoking service |
| **Context object** | Runtime information (request ID, deadline, function name, log stream) passed alongside the event |
| **Cold start** | Latency incurred when Lambda must initialize a new execution environment |

### Supported Runtimes

| Language | Versions | SnapStart Support |
|---|---|---|
| **Node.js** | 20, 22, 24 (Amazon Linux 2023) | No |
| **Python** | 3.10, 3.11, 3.12, 3.13, 3.14 | No |
| **Java** | 8 (al2), 11, 17, 21, 25 | Java 11+ only |
| **.NET** | 8, 9, 10 | No |
| **Ruby** | 3.2, 3.3, 3.4 | No |
| **Custom / Go / Rust** | `provided.al2`, `provided.al2023` | No |
| **Container image** | Any (up to 10 GB image) | No |

### Resource Limits

| Resource | Limit |
|---|---|
| Memory | 128 MB – 10,240 MB (1 MB increments) |
| Timeout | 1 second – 15 minutes |
| Ephemeral storage (`/tmp`) | 512 MB – 10,240 MB |
| Deployment package (zip) | 50 MB compressed / 250 MB uncompressed |
| Container image size | Up to 10 GB |
| Environment variables | 4 KB total |
| Synchronous request payload | 6 MB (request + response each) |
| Asynchronous request payload | 256 KB |
| Layers per function | Up to 5 |
| vCPUs | Proportional to memory; 1 vCPU per 1,769 MB |

### Invocation Types

| Type | Behavior | Error Handling | Example Sources |
|---|---|---|---|
| **Synchronous** | Caller waits for response; errors returned to caller | Caller must retry | API Gateway, ALB, Lambda Function URLs, SDK/CLI |
| **Asynchronous** | Lambda queues the event; returns 202 immediately | Built-in 2× retry with optional DLQ/destination | S3 events, SNS, EventBridge, SES |
| **Event source mapping** | Lambda polls the source and batches records | Bisect on error, retry, DLQ | Kinesis, DynamoDB Streams, SQS, MSK, Kafka |

For full error handling coverage (error types, retry config, DLQ vs Destinations, partial batch response, per-source ESM behavior, CloudWatch error metrics, Powertools), see [lambda-error-handling-capabilities.md](lambda-error-handling-capabilities.md).

### Layers

- ZIP archives containing shared libraries, dependencies, or custom runtimes
- Up to 5 layers per function; uncompressed total (function + layers) ≤ 250 MB
- Layers can be shared across accounts using resource-based policies
- AWS provides AWS SDK, AWS PowerTools, and other managed layers

### Concurrency

| Type | Description | Cost |
|---|---|---|
| **Unreserved** | Shared pool; default; 1,000 account-level limit per region | No additional charge |
| **Reserved concurrency** | Dedicate a portion of account quota to a function; also caps maximum | No additional charge |
| **Provisioned concurrency** | Pre-initialize environments; eliminates cold starts for those requests | Charged per hour per initialized environment |

- Default account concurrency limit: **1,000 concurrent executions per region**
- Burst limit: **1,000 new environments per 10 seconds per function**
- Throttled requests receive a `429 TooManyRequestsException`

### Lambda SnapStart

- Available for **Java 11+ runtimes**
- Lambda takes a snapshot of the initialized execution environment and caches it
- Restores from snapshot on invocation — reduces cold start to sub-second
- **Cannot be used with provisioned concurrency on the same function version**
- No additional cost

### Destinations

Configure where Lambda sends asynchronous invocation results:

| Condition | Destination Options |
|---|---|
| On success | SQS, SNS, Lambda, EventBridge |
| On failure | SQS, SNS, Lambda, EventBridge |

Destinations replace the need for DLQs for most use cases and carry more event context.

### Event Source Mappings (ESM)

- Lambda manages polling for stream and queue sources
- **SQS**: Lambda polls and deletes messages on success; configurable batch size, concurrency, filtering
- **Kinesis / DynamoDB Streams**: Lambda checkpoints shard position; supports bisect-on-error, retry limits
- **MSK / Self-managed Kafka**: Lambda polls topic partitions; SASL/SCRAM or mTLS authentication
- **Filtering**: JSON pattern filters reduce invocations by discarding unwanted records at source

### Function URLs

- Dedicated HTTPS endpoint for a Lambda function or alias
- No API Gateway required
- Auth modes: `AWS_IAM` (SigV4) or `NONE` (public)
- Supports CORS configuration
- Supports response streaming (requires `ResponseStream` invocation mode)

### Container Images

- Package function as OCI container image (up to 10 GB)
- Use AWS base images or bring your own (must implement Lambda Runtime Interface Client)
- Images stored in Amazon ECR
- Supports all Lambda features (layers are not applicable to container images)

---

## Versions

A version is an **immutable snapshot** of a Lambda function's code and configuration. Publishing a version captures the current `$LATEST` state.

### What gets locked at publish time

Code, runtime, architecture, handler, memory, timeout, VPC config, environment variables, layers, DLQ config, execution role, ephemeral storage size, SnapStart config, tracing config.

### What can still change on a published version

Event source mappings, destinations, provisioned concurrency, async invocation settings. These do not require republishing.

### $LATEST

- Every function has a mutable `$LATEST` version that code deployments overwrite.
- Invoking via the **unqualified ARN** targets `$LATEST` implicitly.
- Lambda will not publish a new numbered version if `$LATEST` is identical to the most recently published version.
- Provisioned concurrency and SnapStart **cannot** be used on `$LATEST`.

### Version ARN format

```
arn:aws:lambda:<region>:<account>:function:<name>:<version-number>
```

Unqualified ARN (targets `$LATEST`):
```
arn:aws:lambda:<region>:<account>:function:<name>
```

### Version numbering

- Monotonically increasing integers starting at 1 — never reused, even if the function is deleted and recreated.
- `PublishVersion` returns the new version number and qualified ARN.

### Storage quota

All function versions and layers share a **75 GB per-region** deployment package storage quota (soft limit, increasable). No documented hard limit on version count per function — storage is the practical constraint.

### Runtime management caveat

With **Auto** runtime management mode, the managed runtime used by a published version may be updated by AWS automatically. With **Function update** or **Manual** mode, it is not.

---

## Aliases

An alias is a **named, mutable pointer** to a specific published version. Callers use a stable alias ARN while the underlying version can be updated.

### Alias ARN format

```
arn:aws:lambda:<region>:<account>:function:<name>:<alias-name>
```

The qualifier in an ARN can be: a version number, an alias name, or `$LATEST`. There is no built-in `$LATEST` alias — it is a special qualifier on the function itself.

### ARN qualifier summary

| Qualifier | Targets |
|---|---|
| None (unqualified ARN) | `$LATEST` implicitly |
| `$LATEST` | Mutable unpublished version |
| Version number (e.g., `42`) | Immutable version 42 |
| Alias name (e.g., `prod`) | Whatever version the alias currently points to |

### Alias with Function URLs

Function URLs can be attached to any **named alias** or to `$LATEST`. They **cannot** be attached to a specific numbered version (other than via `$LATEST`).

### Resource-based policies scope

A policy on the unqualified ARN does **not** automatically apply to versions or aliases. Grant permissions explicitly on each qualifier you want callers to invoke. This is critical for event sources that invoke via a specific alias.

---

## Traffic Shifting (Weighted Aliases)

An alias can simultaneously route traffic to **up to two published versions** using `AdditionalVersionWeights`. This is the primitive that powers canary and blue/green deployments.

### How it works

- The alias has a **primary version** and an optional secondary version with a decimal weight (0.0–1.0).
- Primary version receives `1.0 - weight`; secondary receives `weight`.
- Lambda uses a **probabilistic model** — at low traffic volumes, actual percentages may vary from the configured weights.

### Constraints

- Maximum **2 versions** per alias at any time.
- **Neither version can be `$LATEST`** — both must be published numbered versions.
- Both versions must share the same **execution role** and **DLQ configuration** (or both must have none).

### Detecting which version was invoked

- **CloudWatch Logs**: Every invocation emits a `START` log line with `Version: <number>`.
- **CloudWatch metric dimension**: Filter Lambda error/duration metrics by `ExecutedVersion`.
- **Synchronous response header**: `x-amz-executed-version`.

### Provisioned concurrency during traffic shifts

When using weighted aliases, provisioned concurrency is associated with the alias, not with a specific version. Consider increasing provisioned concurrency during the shift window to avoid cold-start overflow invocations on the new version.

---

## Traffic Shifting with CodeDeploy

AWS SAM + CodeDeploy automate weighted alias shifts by:
1. Publishing a new version when code changes (`AutoPublishAlias`).
2. Incrementally updating `AdditionalVersionWeights` according to a deployment config.
3. Monitoring CloudWatch alarms and rolling back automatically on failure.

### SAM template pattern

```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    AutoPublishAlias: live
    DeploymentPreference:
      Type: Linear10PercentEvery2Minutes
      Alarms:
        - !Ref MyErrorAlarm
      Hooks:
        PreTraffic: !Ref PreTrafficHookFunction
        PostTraffic: !Ref PostTrafficHookFunction
```

### Predefined deployment configurations

**Canary** — shifts a fixed percentage first, waits, then shifts the remainder:

| Config name | Behavior |
|---|---|
| `LambdaCanary10Percent5Minutes` | 10% → wait 5 min → 90% |
| `LambdaCanary10Percent10Minutes` | 10% → wait 10 min → 90% |
| `LambdaCanary10Percent15Minutes` | 10% → wait 15 min → 90% |
| `LambdaCanary10Percent30Minutes` | 10% → wait 30 min → 90% |

**Linear** — shifts traffic in equal increments on a fixed interval:

| Config name | Behavior |
|---|---|
| `LambdaLinear10PercentEvery1Minute` | +10%/min → completes in 10 min |
| `LambdaLinear10PercentEvery2Minutes` | +10% every 2 min → completes in 20 min |
| `LambdaLinear10PercentEvery3Minutes` | +10% every 3 min → completes in 30 min |
| `LambdaLinear10PercentEvery10Minutes` | +10% every 10 min → completes in 100 min |

**All-at-once**: `LambdaAllAtOnce` — shifts 100% immediately (equivalent to alias update with no weighting).

Full CodeDeploy config names are prefixed with `CodeDeployDefault.` (e.g., `CodeDeployDefault.LambdaLinear10PercentEvery2Minutes`).

### Lifecycle event hooks

Lambda CodeDeploy deployments support exactly **two** AppSpec hooks:

| Hook | Runs |
|---|---|
| `BeforeAllowTraffic` | Before any traffic is shifted to the new version |
| `AfterAllowTraffic` | After all traffic has shifted to the new version |

Hook execution order: `Start → BeforeAllowTraffic → AllowTraffic → AfterAllowTraffic → End`

(`AllowTraffic` is reserved — it cannot be scripted.)

**Hook functions must call back to CodeDeploy** via `PutLifecycleEventHookExecutionStatus` with `status: "Succeeded"` or `"Failed"`. If CodeDeploy does not receive a callback within **1 hour**, the deployment is considered failed.

### Automatic rollback

Rollback is implemented as a **new deployment** of the previous revision (new deployment ID), not a direct alias pointer revert. Two triggers:
1. **Deployment failure** — any failed step triggers automatic redeployment of the last good revision.
2. **CloudWatch alarm** — any named alarm entering `ALARM` state during the deployment window triggers rollback. The alarm must be created in CloudWatch before being referenced in the CodeDeploy deployment group.
