---
name: lambda-expert
description: AWS Lambda expertise for Java developers covering serverless concepts, Lambda programming model, build/deploy with SAM/CloudFormation, event sources (API Gateway, Kinesis, S3, DynamoDB), testing strategies, observability (CloudWatch, X-Ray), advanced topics (cold starts, scaling, error handling, versions/aliases), and serverless architecture patterns. Use when writing Java Lambda functions, designing serverless applications, diagnosing cold starts or errors, setting up CI/CD pipelines, or reviewing serverless architectures. Based on "Programming AWS Lambda" by John Chapin and Mike Roberts (O'Reilly, 2020).
---

# AWS Lambda Expert (Java)

Based on: *Programming AWS Lambda: Build and Deploy Serverless Applications with Java* by John Chapin and Mike Roberts (O'Reilly, 2020).

Lambda is Amazon's FaaS (Functions as a Service) platform. You provide code; AWS handles servers, OS, runtime patching, and scaling. Java functions run in a managed JVM environment with a defined lifecycle: init → invoke → shutdown.

## Lambda Runtime Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        AWS LAMBDA PLATFORM                           │
│                                                                      │
│  ┌────────────────────┐         ┌─────────────────────────────────┐  │
│  │   EVENT SOURCES    │         │       EXECUTION ENVIRONMENT     │  │
│  │────────────────────│         │─────────────────────────────────│  │
│  │ API Gateway (sync) │──────▶  │  INIT PHASE                     │  │
│  │ S3 (async)         │         │  ├── JVM startup                │  │
│  │ DynamoDB Streams   │         │  ├── Handler class load         │  │
│  │ Kinesis (streaming)│         │  └── Static initializers        │  │
│  │ SNS (async)        │         │                                 │  │
│  │ SQS (polling)      │         │  INVOKE PHASE (per request)     │  │
│  │ EventBridge        │         │  ├── Handler method called      │  │
│  │ CloudWatch Events  │         │  ├── Timeout enforced           │  │
│  └────────────────────┘         │  └── Response returned         │  │
│                                 │                                 │  │
│  ┌────────────────────┐         │  WARM CONTAINER REUSE           │  │
│  │   DEPLOYMENT       │         │  └── Static state persists     │  │
│  │────────────────────│         └─────────────────────────────────┘  │
│  │ SAM Template       │                                               │
│  │ CloudFormation     │         ┌─────────────────────────────────┐  │
│  │ ZIP / Uber JAR     │         │       OBSERVABILITY             │  │
│  │ IAM Roles          │         │  CloudWatch Logs / Metrics      │  │
│  └────────────────────┘         │  X-Ray Distributed Tracing     │  │
│                                 └─────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Serverless concepts, Lambda overview, AWS setup, dev environment | [foundations.md](references/foundations.md) |
| Handler signatures, invocation types, I/O types, context, timeout, memory, env vars | [programming-model.md](references/programming-model.md) |
| Building uberjars/ZIPs, SAM templates, CloudFormation, IAM/security, deploying | [build-and-deploy.md](references/build-and-deploy.md) |
| API Gateway, S3, Kinesis, DynamoDB Streams, SQS/SNS, event source semantics | [event-sources.md](references/event-sources.md) |
| Unit tests, functional tests, end-to-end tests, local SAM testing, test pyramid | [testing.md](references/testing.md) |
| CloudWatch Logs, structured logging, metrics, alarms, X-Ray tracing | [observability.md](references/observability.md) |
| Cold starts, scaling/throttling, error handling, versions/aliases, state/caching | [advanced-lambda.md](references/advanced-lambda.md) |
| At-least-once delivery, downstream impacts, architecture patterns, SAR | [advanced-architecture.md](references/advanced-architecture.md) |

## Reference Files

| File | Chapters | Key Topics |
|------|----------|-----------|
| `foundations.md` | 1–2 | FaaS vs BaaS, serverless tradeoffs, Lambda concepts, IAM basics, hello world, SAM CLI |
| `programming-model.md` | 3 | Execution environment, invocation types (sync/async/stream), handler signatures, I/O, Context object |
| `build-and-deploy.md` | 4 | Maven/Gradle packaging, uber JAR, ZIP assembly, SAM template anatomy, CloudFormation, IAM least privilege |
| `event-sources.md` | 5 | API Gateway (REST), S3, Kinesis, DynamoDB Streams, SQS, SNS — input shapes and semantics |
| `testing.md` | 6 | Test pyramid for Lambda, refactoring for testability, unit/functional/E2E, SAM local, cloud test envs |
| `observability.md` | 7 | LambdaLogger, Log4j2/SLF4J, structured JSON logs, CloudWatch Logs Insights, custom metrics, X-Ray |
| `advanced-lambda.md` | 8 | Cold start anatomy, provisioned concurrency, scaling limits, error classes, DLQs, versions, aliases |
| `advanced-architecture.md` | 9 | Idempotency, at-least-once delivery, fan-out patterns, Serverless Application Repository |

## Core Decision Trees

### Which Handler Signature Should I Use?

```
What is your input/output situation?
├── Typed Java object in, typed Java object out
│   └── public OutputType handler(InputType input, Context ctx)
│       └── Jackson deserializes JSON automatically
├── Raw JSON with unknown structure
│   └── public Map<String,Object> handler(Map<String,Object> event, Context ctx)
├── Streaming (large payload or custom serialization)
│   └── public void handler(InputStream in, OutputStream out, Context ctx)
├── AWS SDK event types (S3Event, KinesisEvent, etc.)
│   └── public void handler(S3Event event, Context ctx)
│       └── Add aws-lambda-java-events dependency
└── No response needed (async invocation)
    └── public void handler(InputType input, Context ctx)
```

### How Should I Package My Lambda?

```
What is your build situation?
├── Single module, all deps self-contained
│   ├── Maven shade plugin → uber JAR (fat JAR)
│   └── Handler: com.example.MyHandler::handleRequest
├── Multiple modules / want smaller artifacts
│   └── ZIP file: classes/ + lib/*.jar
├── Minimizing cold start / artifact size is critical
│   └── Use jdeps to find minimal deps, shade only what's needed
└── Native performance needed
    └── Consider GraalVM native (outside book scope)
```

### Which Event Source Semantics Apply?

```
How is your Lambda invoked?
├── Synchronous (caller waits for response)
│   ├── API Gateway → HTTP request/response
│   ├── ALB → same pattern
│   └── Direct SDK invoke with RequestResponse type
├── Asynchronous (fire and forget, Lambda retries on failure)
│   ├── S3 → object events
│   ├── SNS → notifications
│   └── EventBridge / CloudWatch Events
└── Streaming / polling (Lambda polls source)
    ├── Kinesis Data Streams → ordered, at-least-once per shard
    ├── DynamoDB Streams → ordered per partition key
    └── SQS → at-least-once, unordered (standard queue)
        └── SQS FIFO → ordered within message group
```

### Cold Start or Warm Invocation?

```
Is this a cold start?
├── Yes (new container) → INIT + INVOKE phases run
│   ├── JVM startup: ~200–500ms
│   ├── Class loading + static init: varies widely
│   └── Mitigation options:
│       ├── Provisioned Concurrency → pre-warm containers
│       ├── Reduce JAR size → faster class loading
│       ├── Minimize static init work
│       └── SnapStart (newer, Corretto 11+)
└── No (warm container) → only INVOKE phase runs
    └── Static state (connections, caches) persists — exploit this
```

### How to Handle Errors?

```
What kind of error occurred?
├── Transient (timeout, downstream blip)
│   ├── Async source → Lambda retries up to 2x, then DLQ/EventBridge
│   ├── Kinesis/DDB Streams → retries until success or record expires
│   └── SQS → message returns to queue, retry up to maxReceiveCount
├── Permanent (bad data, business logic)
│   ├── Catch exception, log structured error, return error response
│   └── For streams: use bisect-on-error or destination on failure
└── Throttle (concurrency limit hit)
    └── Async → queued and retried; Sync → 429 to caller
```

## Key Java Lambda Patterns

### Minimal Handler (POJO I/O)

```java
public class MyHandler implements RequestHandler<MyInput, MyOutput> {
    @Override
    public MyOutput handleRequest(MyInput input, Context context) {
        LambdaLogger logger = context.getLogger();
        logger.log("Processing: " + input.getId());
        return new MyOutput("done");
    }
}
```

### Reuse Expensive Resources Across Warm Invocations

```java
public class MyHandler implements RequestHandler<MyInput, MyOutput> {
    // Initialized ONCE during INIT phase, reused across warm invocations
    private static final AmazonDynamoDB dynamo =
        AmazonDynamoDBClientBuilder.defaultClient();
    private static final ObjectMapper mapper = new ObjectMapper();

    @Override
    public MyOutput handleRequest(MyInput input, Context context) {
        // dynamo client already connected — no cold-start penalty here
        return processWithDynamo(input);
    }
}
```

### Structured Logging Pattern

```java
// Log JSON so CloudWatch Logs Insights can filter by field
Map<String, Object> logEntry = new LinkedHashMap<>();
logEntry.put("level", "INFO");
logEntry.put("message", "Order processed");
logEntry.put("orderId", order.getId());
logEntry.put("durationMs", elapsed);
context.getLogger().log(mapper.writeValueAsString(logEntry));
```

## Lambda Configuration Quick Reference

| Setting | Default | Notes |
|---------|---------|-------|
| Timeout | 3 seconds | Max 15 minutes |
| Memory | 128 MB | 128–10,240 MB in 1 MB steps |
| CPU | Proportional to memory | ~1 vCPU at 1,769 MB |
| Ephemeral storage (/tmp) | 512 MB | Max 10 GB (configurable) |
| Concurrency (soft limit) | 1,000 per region | Request increase via support |
| Payload size (sync) | 6 MB request / 6 MB response | |
| Payload size (async) | 256 KB | |
| Deployment package (ZIP) | 50 MB compressed / 250 MB unzipped | |
| Environment variables | 4 KB total | |
