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
