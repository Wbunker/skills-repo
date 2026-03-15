# AWS Lambda — Capabilities Reference
For CLI commands, see [lambda-cli.md](lambda-cli.md).

## AWS Lambda

**Purpose**: Run code without provisioning or managing servers. Scales automatically, charges only for compute time consumed.

### Core Concepts

| Concept | Description |
|---|---|
| **Function** | Discrete unit of code; deployed as a zip archive or container image |
| **Handler** | Entry point called by Lambda runtime; receives event and context objects |
| **Execution environment** | Isolated Firecracker microVM hosting one function instance at a time |
| **Event** | JSON document passed to the handler describing the triggering action |
| **Context** | Object passed to handler with invocation metadata (request ID, deadline, function name) |
| **Execution role** | IAM role assumed by the function; defines what AWS resources the function can access |
| **Layer** | ZIP archive attached to a function containing shared dependencies or runtimes |
| **Extension** | Process that runs alongside the function for monitoring, security, or tooling integration |

### Managed Runtimes

| Runtime | Identifier examples |
|---|---|
| Node.js | `nodejs20.x`, `nodejs22.x` |
| Python | `python3.11`, `python3.12`, `python3.13` |
| Java | `java11`, `java17`, `java21` |
| .NET | `dotnet8` |
| Ruby | `ruby3.3` |
| Custom runtime | `provided.al2023` — bring any language via bootstrap executable |

### Execution Environment Lifecycle

| Phase | What happens |
|---|---|
| **Init** | Download code, start runtime, run initialization code outside the handler; billed only for provisioned concurrency, not reserved or unreserved |
| **Invoke** | Run the handler; Lambda measures duration from first byte to return |
| **Shutdown** | Runtime receives `SHUTDOWN` event; extensions have up to 2 seconds to finish |

Cold starts occur during the Init phase when Lambda must create a new execution environment. Warm invocations skip Init.

### Layers

- Content: libraries, custom runtimes, configuration, binary dependencies
- Size limit: 50 MB compressed per layer (250 MB unzipped per function across all layers)
- Up to 5 layers per function
- Layers can be shared across accounts via resource-based policies
- Versioned; functions reference a specific version ARN

### Extensions

| Type | Description |
|---|---|
| **Internal** | Run inside the runtime process; share the same lifecycle |
| **External** | Run as separate processes alongside the runtime; can run during Init and Shutdown phases |

Use cases: logging agents, APM tools, secrets caching, config providers.

### Concurrency

| Model | Description | Cost | Cold starts |
|---|---|---|---|
| **Unreserved** | Draws from the account pool (default 1,000/region) | No extra charge | Possible |
| **Reserved** | Sets both the maximum AND guaranteed minimum for the function; subtracts from the account pool | No extra charge | Possible |
| **Provisioned** | Pre-initializes N environments; eliminates cold starts for that N; scales above N using unreserved | Additional charge | None up to provisioned count |

**Concurrency scaling rate**: 1,000 new environments per 10 seconds per function (burst: 500 additional per 10 seconds account-wide).

**Throttling**: When reserved or account limits are hit, Lambda returns HTTP 429 (`TooManyRequestsException`). Synchronous callers receive the 429; async callers retry automatically (up to 2 times) before sending to a dead-letter queue or failure destination.

**Account defaults**: 1,000 concurrent executions per region; 10,000 requests per second (10× concurrency quota). Increase via Service Quotas.

### Event Source Mappings

Lambda polls stream and queue sources on your behalf. Supported sources:

| Source | Batch size | Batch window | Bisect on error | Filters |
|---|---|---|---|---|
| **Amazon SQS** | 1–10,000 | 0–300 s | No (delete failed message) | Yes |
| **Amazon Kinesis** | 1–10,000 | 0–300 s | Yes | Yes |
| **Amazon DynamoDB Streams** | 1–10,000 | 0–300 s | Yes | Yes |
| **Amazon MSK** | 1–10,000 | 0–300 s | No | Yes |
| **Self-managed Kafka** | 1–10,000 | 0–300 s | No | Yes |
| **Amazon MQ (ActiveMQ/RabbitMQ)** | 1–10,000 | 0–300 s | No | No |
| **Amazon DocumentDB** | 1–10,000 | 0–300 s | No | Yes |

**Key parameters**:
- `BatchSize`: Max records per invocation
- `MaximumBatchingWindowInSeconds`: Wait up to N seconds to fill a batch (default 0 for SQS/Kinesis/DynamoDB; 500 ms for MSK/Kafka/MQ/DocumentDB)
- `BisectBatchOnFunctionError`: Split failing batch in half to isolate poison pills (Kinesis/DynamoDB only)
- `FilterCriteria`: JSON filter patterns; Lambda only invokes when events match, reducing cost
- `MaximumRetryAttempts` / `MaximumRecordAgeInSeconds`: Stream source error handling limits
- `DestinationConfig`: Where to send discarded batches (SQS or SNS)

### Async Invocation & Destinations

For async invocations (SNS, S3, EventBridge triggers), Lambda retries twice on failure. Configure `PutFunctionEventInvokeConfig` to set:
- `MaximumRetryAttempts`: 0–2
- `MaximumEventAgeInSeconds`: 60–21,600
- `DestinationConfig.OnSuccess`: SQS queue, SNS topic, EventBridge bus, or another Lambda function
- `DestinationConfig.OnFailure`: Same options, plus SQS dead-letter queue

### Function URLs

| Feature | Details |
|---|---|
| **Format** | `https://<url-id>.lambda-url.<region>.on.aws` |
| **Auth type: AWS_IAM** | Requires SigV4 signed requests; uses resource-based policy |
| **Auth type: NONE** | Public; optionally use resource-based policy to restrict callers |
| **CORS** | Configure AllowOrigins, AllowMethods, AllowHeaders, ExposeHeaders, AllowCredentials, MaxAge |
| **Throttling** | RPS limit = 10 × reserved concurrency; returns HTTP 429 when exceeded |
| **Applies to** | `$LATEST` or a published alias; not a numbered version |

### SnapStart

Available for Java 11+, Python 3.12+, .NET 8+. Not compatible with provisioned concurrency or EFS.

| Phase | What happens |
|---|---|
| **Publish version** | Lambda runs Init, takes a Firecracker microVM snapshot (memory + disk state) |
| **Cache snapshot** | Encrypted snapshot stored in multiple copies; automatically patched with security updates |
| **Invoke** | Lambda resumes a new environment from the snapshot; skips Init |

**Restore hooks**: Implement `BeforeCheckpoint` and `AfterRestore` hooks to handle uniqueness requirements, network reconnection, and ephemeral data refresh.

**Compatibility considerations**: Do not generate unique IDs, secrets, or entropy in Init. Re-establish network connections and refresh cached tokens/timestamps in the handler or AfterRestore hook.

### Container Image Support

- Package function as a container image up to 10 GB
- Base images available for all managed runtimes
- Custom base images must implement the Lambda Runtime Interface Client (RIC) and Runtime Interface Emulator (RIE)
- Deployed like any other function; all Lambda features (layers excluded) apply

### Environment Variables & Secrets Integration

- Up to 4 KB total environment variables per function
- Encrypted at rest using Lambda's service key or a CMK
- For larger secrets: use SSM Parameter Store (`GetParameter`) or Secrets Manager (`GetSecretValue`) in handler or via Lambda Extensions (e.g., Parameters and Secrets Lambda Extension for caching)

### Lambda@Edge vs CloudFront Functions

| Feature | Lambda@Edge | CloudFront Functions |
|---|---|---|
| **Runtime** | Node.js, Python | JavaScript (ES5.1+) |
| **Trigger points** | Viewer request/response, Origin request/response | Viewer request/response only |
| **Max execution time** | 5 s (viewer), 30 s (origin) | 1 ms |
| **Memory** | 128 MB – 10 GB | 2 MB |
| **Network access** | Yes | No |
| **File system access** | No | No |
| **Pricing** | Per request + duration | Per request (sub-millisecond pricing) |
| **Use case** | Complex logic, auth, A/B testing, origin selection | URL rewrites, header manipulation, simple redirects |

### VPC Access

To access resources in a VPC (RDS, ElastiCache), configure the function with a VPC, subnets, and security groups. Lambda creates Hyperplane ENIs shared across functions in the same subnet configuration. Cold start overhead for VPC attachment is now minimal (~100 ms) due to Hyperplane.

### Power Tuning

Use the AWS Lambda Power Tuning open-source tool (Step Functions state machine) to find the optimal memory setting balancing cost and performance. Lambda CPU allocation scales proportionally with memory (128 MB – 10,240 MB in 1 MB increments).
