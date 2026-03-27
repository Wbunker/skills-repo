# Advanced Serverless Architecture
## Chapter 9: At-Least-Once Delivery, Scaling Impacts, Event Source Gotchas, Architecture Patterns, SAR

---

## Serverless Architecture "Gotchas"

Serverless introduces operational characteristics that differ fundamentally from traditional servers. Understanding these prevents production surprises.

---

## At-Least-Once Delivery

**Most Lambda event sources deliver events at least once, not exactly once.** This means your handler may be invoked multiple times for the same logical event.

### Sources and Their Delivery Guarantees

| Source | Delivery Guarantee | Notes |
|--------|--------------------|-------|
| API Gateway (sync) | At-most-once | Caller controls retries |
| S3 | At-least-once | Rare duplicate deliveries |
| SNS | At-least-once | Can deliver same message multiple times |
| EventBridge | At-least-once | |
| SQS Standard | At-least-once | Visibility timeout gap can cause re-delivery |
| SQS FIFO | Exactly-once (within message group) | Within deduplication window |
| Kinesis | At-least-once per shard | Checkpoint lag causes re-reads |
| DynamoDB Streams | At-least-once | |

### Idempotency: The Required Response

**Idempotent**: Processing the same event N times produces the same result as processing it once.

**Pattern 1: Natural idempotency**
If your operation is a DynamoDB `PutItem` with a fixed primary key derived from the event, repeating it produces the same state. Design data writes to be naturally idempotent.

```java
// Idempotent: re-processing order-123 produces the same DynamoDB item
Order order = parseEvent(event);
dynamoMapper.save(order);  // PutItem by primary key — safe to repeat
```

**Pattern 2: Idempotency key with deduplication store**

```java
public void handleRequest(SQSEvent event, Context ctx) {
    for (SQSEvent.SQSMessage msg : event.getRecords()) {
        String idempotencyKey = msg.getMessageId(); // or a business ID from the payload

        // Check if already processed
        if (alreadyProcessed(idempotencyKey)) {
            ctx.getLogger().log("Duplicate: " + idempotencyKey + ", skipping\n");
            continue;
        }

        process(msg);
        markProcessed(idempotencyKey); // Store in DynamoDB with TTL
    }
}

private boolean alreadyProcessed(String key) {
    try {
        GetItemResult result = dynamo.getItem(new GetItemRequest()
            .withTableName("IdempotencyKeys")
            .withKey(Map.of("key", new AttributeValue(key))));
        return result.getItem() != null;
    } catch (Exception e) {
        return false; // Fail open: process if uncertain
    }
}
```

**AWS Lambda Powertools for Java** provides a managed idempotency module — consider it for production use:

```java
@Idempotent
public OrderResponse handleRequest(@IdempotencyKey OrderRequest request, Context ctx) {
    // Automatically deduplicated using DynamoDB
    return processOrder(request);
}
```

**Pattern 3: Conditional writes**

Use DynamoDB `ConditionExpression` to only write if the item doesn't already exist:

```java
PutItemRequest req = new PutItemRequest()
    .withTableName("Orders")
    .withItem(orderItem)
    .withConditionExpression("attribute_not_exists(orderId)");
try {
    dynamo.putItem(req);
} catch (ConditionalCheckFailedException e) {
    // Already exists — idempotent, continue
}
```

---

## Impacts of Lambda Scaling on Downstream Systems

Lambda scales aggressively. When traffic bursts, Lambda can spin up hundreds of concurrent containers. If each container holds a connection to your database or downstream service, you can exhaust connection pools instantly.

### The Connection Exhaustion Problem

```
Traffic spike → Lambda scales to 200 concurrent executions
Each execution opens a DynamoDB/RDS connection
RDS max_connections = 100
→ 100 Lambda containers succeed; 100 fail with "too many connections"
```

### Solutions by Downstream Service

**DynamoDB**: Not an issue. DynamoDB uses HTTP, not persistent connections. Scales independently.

**RDS (relational databases)**:
- Each Lambda instance holds an RDS connection for the container's lifetime
- At 200 concurrent Lambdas → 200 connections → exceeds typical RDS max_connections

Solutions:
1. **RDS Proxy**: Managed connection pooler in front of RDS. Lambda connects to RDS Proxy; proxy pools and multiplexes to RDS. Strongly recommended for RDS + Lambda.
2. **Reserved concurrency**: Cap Lambda at a concurrency that fits within RDS connection limit.
3. **Aurora Serverless**: Scales database connections elastically (though has its own tradeoffs).

**HTTP APIs (third-party services)**:
- Rate limits: 200 concurrent Lambdas may blow through per-second rate limits
- Use SQS as a buffer between Lambda and rate-limited downstream:
  ```
  Event Source → Lambda (fast) → SQS → Lambda (rate-limited consumer) → API
  ```

**ElastiCache (Redis/Memcached)**:
- Connection limits apply
- Use connection pooling within each Lambda container
- Static client initialization ensures connections are shared within a container

---

## The Fine Print of Lambda Event Sources

### S3 Event Notification Ordering

S3 does not guarantee event delivery order. For a workflow that expects `file-part-1`, `file-part-2`, `file-part-3`, you cannot rely on Lambda being invoked in that sequence. Use a manifest/aggregation pattern:

```
Parts uploaded → S3 events → Lambda records completion in DynamoDB
Final part triggers manifest check → all parts present → merge step
```

### Kinesis and DynamoDB Stream Shard Limits

Each shard is processed by exactly one Lambda invocation at a time. Scaling is tied to shard count:
- 10 shards → max 10 concurrent Lambda invocations for that stream
- To scale out, increase shard count (Kinesis) or ensure enough DynamoDB partitions
- `IteratorAge` metric signals processing lag — alarm on high values

### SQS Visibility Timeout and Duplicate Processing

If your Lambda invocation takes longer than the SQS visibility timeout, SQS makes the message visible again (another consumer picks it up) before your function completes. This causes duplicate processing.

**Rule**: Set SQS visibility timeout to at least 6× your Lambda function timeout.

```yaml
OrderQueue:
  Type: AWS::SQS::Queue
  Properties:
    VisibilityTimeout: 180  # if Lambda timeout is 30s, use 180s
```

### Async Invocation Event Age

Lambda queues async events internally. If Lambda cannot process them within the `MaximumEventAgeInSeconds` window (default: 6 hours), it discards them. Configure `MaximumEventAgeInSeconds` to balance between retrying stale data and data loss.

---

## New Architecture Patterns Enabled by Serverless

### Fan-Out with SNS + SQS + Lambda

```
Event → SNS Topic
    ├── SQS Queue A → Lambda (process orders)
    ├── SQS Queue B → Lambda (send notifications)
    └── SQS Queue C → Lambda (update analytics)
```

Each consumer is independent; failure in one does not affect others. Use SNS filter policies to route only relevant events to each queue.

### Scatter-Gather

Fan out work to parallel Lambda invocations, then aggregate:

```
Orchestrator Lambda
    ├── Invoke Lambda A (process shard 1) [async]
    ├── Invoke Lambda B (process shard 2) [async]
    └── Invoke Lambda C (process shard 3) [async]
         ↓
    Each writes result to DynamoDB
         ↓
    Aggregator Lambda (triggered when all complete)
```

Or use AWS Step Functions for complex orchestration with retries, parallel branches, and error handling.

### Event-Driven State Machine with Step Functions

For workflows with multiple steps, conditional branching, and error handling, Step Functions is preferable to chaining Lambdas directly:

```yaml
# Each step is a Lambda; Step Functions handles sequencing, retry, and state
States:
  ValidateOrder:
    Type: Task
    Resource: !GetAtt ValidateOrderFunction.Arn
    Next: CheckInventory
    Retry:
      - ErrorEquals: ["RetryableError"]
        MaxAttempts: 3
  CheckInventory:
    Type: Task
    Resource: !GetAtt CheckInventoryFunction.Arn
    ...
```

### Strangler Fig Pattern (Incremental Serverless Migration)

Migrate a monolith to serverless incrementally:

```
Client → API Gateway
    ├── /new-feature → Lambda (serverless)
    └── /legacy/* → Existing monolith (via HTTP proxy integration)
```

Move one route at a time. The monolith shrinks; the serverless surface grows.

### CQRS with Lambda

Separate read and write paths:

```
Write path: API Gateway → Lambda (write) → DynamoDB (write-optimized model)
                                         → DynamoDB Streams
                                         → Lambda (projection builder)
                                         → DynamoDB (read-optimized model)
Read path:  API Gateway → Lambda (read) → DynamoDB (read-optimized model)
```

---

## Serverless Application Repository (SAR)

SAR is a managed repository of serverless applications (SAM templates + Lambda code) published by AWS, partners, and the community.

### Using SAR Applications

Browse: https://serverlessrepo.aws.amazon.com

```yaml
# Embed a SAR application in your SAM template
Transform: AWS::Serverless-2016-10-31

Resources:
  SecretsManagerRotationFunction:
    Type: AWS::Serverless::Application
    Properties:
      Location:
        ApplicationId: arn:aws:serverlessrepo:us-east-1:297356227824:applications/SecretsManagerRDSMySQLRotationSingleUser
        SemanticVersion: 1.1.60
      Parameters:
        functionName: my-rotation-function
        endpoint: !Sub "https://secretsmanager.${AWS::Region}.amazonaws.com"
```

### Publishing to SAR

```bash
sam package --s3-bucket my-deployment-bucket --output-template-file packaged.yaml

sam publish --template packaged.yaml --region us-east-1
```

The published application is private by default. Share with specific AWS accounts or make public.

### Common SAR Use Cases

| Application | Use Case |
|-------------|---------|
| `lambda-powertools-*` | AWS Lambda Powertools (logging, tracing, idempotency) |
| Secrets Manager rotation functions | Automatic secret rotation for RDS, Redshift |
| CloudWatch dashboards | Pre-built dashboards for Lambda observability |
| Custom authorizers | JWT/OAuth authorizers for API Gateway |

---

## Serverless Architecture Decision Framework

```
Is this workload appropriate for Lambda?
├── Yes if:
│   ├── Event-driven (reacts to events rather than constant polling)
│   ├── Intermittent or unpredictable traffic
│   ├── Max execution time < 15 minutes
│   ├── Stateless (or state can be externalized)
│   └── Team comfortable with distributed systems complexity
└── Reconsider if:
    ├── Constant, high-throughput compute (use ECS/Fargate instead)
    ├── Requires persistent connections (e.g., WebSockets with session state)
    ├── Sub-10ms latency requirements (cold starts are incompatible)
    ├── Complex local state or in-memory data structures shared across requests
    └── Regulatory requirements preclude multi-tenant shared infrastructure

Choosing between sync and async processing?
├── User is waiting for a response → synchronous (API Gateway + Lambda)
├── Background processing, user doesn't wait → asynchronous (SQS/SNS + Lambda)
└── Ordered stream processing → Kinesis/DDB Streams + Lambda

Handling downstream rate limits or connection limits?
├── RDS → mandatory: use RDS Proxy
├── Third-party API with rate limits → buffer with SQS, rate-limit consumer Lambda
├── DynamoDB → no action needed (HTTP, scales independently)
└── ElastiCache → static connection in Lambda, monitor connection count

Ensuring data integrity with at-least-once delivery?
├── Writes to DynamoDB → use condition expressions or idempotency keys
├── External API calls → idempotency key in request header + dedup store
└── Multi-step transactions → Step Functions with idempotent Lambda tasks
```
