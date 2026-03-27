# Advanced AWS Lambda
## Chapter 8: Cold Starts, Scaling, Error Handling, Versions and Aliases, State and Caching

---

## Cold Starts

### What Is a Cold Start?

A cold start occurs when Lambda must initialize a new execution environment before invoking your handler. It happens when:
- No existing container is available (first invocation, scale-out, container recycled)
- You deploy a new function version
- Lambda reclaims idle containers (no defined SLA)

```
COLD START TIMELINE (Java):
│
├── Container provisioning (microVM startup)     ~50–100ms (platform)
├── JVM startup                                  ~200–500ms
├── Class loading (your classes + dependencies)  varies (50ms–2s+)
├── Static initializers                          your code
└── Handler method invoked                       ← user-visible start
```

**Warm invocation**: container already exists → only handler method executes → no cold start overhead.

### Identifying Cold Starts

```
# REPORT log line on cold start includes Init Duration:
REPORT RequestId: abc-123  Duration: 45.23 ms  Billed Duration: 46 ms
       Memory Size: 512 MB  Max Memory Used: 112 MB  Init Duration: 1823.45 ms
#                                                     ^^^^^^^^^^^^^^^^^^^^
#                                                     Present only on cold starts

# CloudWatch Logs Insights query
fields @timestamp, @initDuration
| filter @type = "REPORT" and ispresent(@initDuration)
| stats avg(@initDuration) as avgColdStart,
        max(@initDuration) as maxColdStart,
        count() as coldStarts by bin(1h)
```

### Impact of Cold Starts

| Factor | Effect on Cold Start |
|--------|---------------------|
| JAR size | Larger → more classes → slower class loading |
| Number of dependencies | More → more to load |
| Static initialization complexity | Heavy work in `<clinit>` → slower |
| Memory setting | More memory → more CPU → faster JVM startup |
| VPC configuration | Additional ENI attachment: +1–10 seconds (pre-2020 issue, now mitigated by HyperPlane) |

### Mitigating Cold Starts

**1. Reduce deployment artifact size**
- Remove unused dependencies with Maven Dependency Plugin
- Use `jdeps` to identify what you actually need
- Exclude test dependencies (`<scope>test</scope>`)

**2. Minimize static initializer work**
- Initialize clients statically (reuse across warm invocations)
- But keep static initialization fast — defer heavy work until first invocation if rarely cold-started

**3. Increase memory**
- More memory → more vCPU → faster JVM startup
- Often worth it: higher memory reduces cold start enough to offset price difference

**4. Provisioned Concurrency**
Pre-warms a specified number of execution environments. They are initialized (INIT phase complete) before any invocation arrives.

```yaml
# SAM template
OrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    AutoPublishAlias: live
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 5
```

```bash
# Or directly
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier my-alias \
  --provisioned-concurrent-executions 5
```

**Cost**: Provisioned Concurrency is billed for the number of pre-warmed instances × duration, even if unused. Use Application Auto Scaling to scale it with demand.

**5. Scheduled warm-up pings** (poor man's solution)
Invoke the function every few minutes on a schedule to keep containers warm. Unreliable — Lambda may still spin up new containers under load, and this does not help scale-out cold starts.

**6. SnapStart (Java on Corretto 11+)**
AWS SnapStart takes a snapshot of an initialized execution environment and restores it for cold starts. Available for Corretto 11/17/21. Dramatically reduces cold starts for Java.

```yaml
SnapStart:
  ApplyOn: PublishedVersions
```

---

## Scaling

### How Lambda Scales

Lambda scales by creating new execution environments in parallel. Each environment handles one invocation at a time.

```
Invocations over time:
Time 0:  [Req1] [Req2] [Req3]
         Container1 Container2 Container3  ← 3 cold starts

Time 1:  [Req4] [Req5]
         Container1 Container2            ← 2 warm invocations (Req4 reuses C1, Req5 reuses C2)
         Container3 idle

Time 2:  (burst traffic) [Req6..Req20]
         Lambda adds more containers      ← more cold starts
```

### Concurrency Limits

| Limit | Default | Configurable? |
|-------|---------|--------------|
| Account-level concurrent executions | 1,000 per region | Yes (request increase) |
| Function reserved concurrency | None (shares account pool) | Yes |
| Function provisioned concurrency | 0 | Yes |

**Reserved Concurrency**: Guarantee a function gets a fixed slice of account concurrency. Also caps it — useful to protect downstream services from Lambda over-scaling.

```yaml
ReservedConcurrentExecutions: 50  # this function gets exactly 50, no more, no less
```

**Throttling behavior by invocation type:**
- Synchronous → caller receives 429 TooManyRequestsException
- Asynchronous → Lambda queues and retries for up to 6 hours
- Stream (Kinesis/DDB) → Lambda stops reading from the shard until concurrency is available

### Thread Safety

Each execution environment is single-threaded from Lambda's perspective (one invocation at a time). However:
- Multiple containers run concurrently (one per concurrent invocation)
- Static fields are shared within a container across invocations (sequential, not concurrent)
- If you use Java threads inside your handler, you are responsible for thread safety within that invocation

**Safe pattern**: Use static clients (DynamoDB, S3) — they are thread-safe per AWS SDK design. Use them from your single handler thread without additional synchronization.

### Vertical Scaling

Increase `MemorySize` to get more CPU:

```
512 MB  → ~0.28 vCPU
1769 MB → ~1.0 vCPU (full vCPU)
3538 MB → ~2.0 vCPU
```

For CPU-bound tasks, increasing memory to 1,769+ MB can halve execution time, potentially reducing cost (you pay for GB × seconds).

---

## Error Handling

### Classes of Error

| Class | Example | Behavior |
|-------|---------|---------|
| Function error | Uncaught exception, OOM | Invocation marked as error; retry depends on source |
| Timeout | Exceeds `Timeout` setting | Lambda kills JVM; invocation marked as error |
| Throttle | Concurrency limit hit | 429 returned (sync); queued (async) |
| Platform error | Container crash | Lambda retries automatically |

### Invocation Type × Error Handling

**Synchronous**:
- Lambda returns the exception detail to the caller
- No automatic Lambda retry — the caller must handle it
- API Gateway returns 502 for unhandled exceptions (configure error mapping for cleaner responses)

**Asynchronous**:
- Lambda retries up to **2 additional times** with exponential backoff (total: 3 attempts)
- After all retries fail, events go to the **Dead Letter Queue (DLQ)** or an **EventBridge Pipes failure destination**
- Configure DLQ: SQS queue or SNS topic

```yaml
# SAM template
OrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    DeadLetterQueue:
      Type: SQS
      TargetArn: !GetAtt FailedOrderQueue.Arn
    EventInvokeConfig:
      MaximumRetryAttempts: 1          # 0, 1, or 2 (default 2)
      MaximumEventAgeInSeconds: 3600   # discard events older than 1 hour
      DestinationConfig:
        OnFailure:
          Destination: !GetAtt FailedOrderQueue.Arn
```

**Kinesis / DynamoDB Streams**:
- On failure, Lambda **retries the batch indefinitely** until records expire from the stream
- Use `BisectBatchOnFunctionError` to isolate bad records by splitting batches
- Use `DestinationConfig.OnFailure` to route irrecoverable records to SQS/SNS

**SQS**:
- On failure (exception), Lambda does not delete messages; they return to the queue
- After `maxReceiveCount` failures, SQS sends to DLQ
- Use `ReportBatchItemFailures` for partial batch success

### Error Handling Strategies

```java
public OrderResponse handleRequest(OrderRequest request, Context ctx) {
    try {
        return processOrder(request);
    } catch (RetryableException e) {
        // For async sources: throw to trigger Lambda retry
        ctx.getLogger().log("Retryable error, will retry: " + e.getMessage());
        throw e;
    } catch (PermanentException e) {
        // For async sources: log and return (don't retry bad data)
        ctx.getLogger().log("Permanent error, skipping: " + e.getMessage());
        // Route to DLQ via structured logging or custom metric
        return new OrderResponse("FAILED", e.getMessage());
    }
}
```

---

## Versions and Aliases

### Lambda Versions

A **version** is an immutable snapshot of your function's code and configuration at a specific point in time.

```bash
# Publish a version from $LATEST
aws lambda publish-version --function-name my-function
# Returns: {"Version": "3", "FunctionArn": "...my-function:3", ...}

# Invoke a specific version
aws lambda invoke --function-name my-function:3 output.json
```

`$LATEST` is the mutable working copy. Published versions are immutable — code, memory, timeout, environment variables are all frozen.

### Lambda Aliases

An **alias** is a named pointer to a specific version. Aliases are mutable — you update them to point to new versions.

```bash
# Create alias pointing to version 3
aws lambda create-alias \
  --function-name my-function \
  --name live \
  --function-version 3

# Update alias to point to version 4
aws lambda update-alias \
  --function-name my-function \
  --name live \
  --function-version 4

# Invoke via alias
aws lambda invoke --function-name my-function:live output.json
```

### Traffic Shifting (Canary / Blue-Green)

Aliases support weighted routing between two versions. Use this for canary deployments:

```bash
# Route 10% of traffic to version 4 (canary), 90% to version 3 (stable)
aws lambda update-alias \
  --function-name my-function \
  --name live \
  --function-version 4 \
  --routing-config AdditionalVersionWeights={"3": 0.9}
```

Monitor error rates and latency. If canary looks good, shift all traffic to version 4.

SAM supports traffic shifting with CodeDeploy:

```yaml
OrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    AutoPublishAlias: live
    DeploymentPreference:
      Type: Canary10Percent5Minutes  # or Linear10PercentEvery1Minute, AllAtOnce
      Alarms:
        - !Ref OrderFunctionErrorAlarm
      Hooks:
        PreTraffic: !Ref PreTrafficHook
```

### When to Use Versions and Aliases

| Use Case | Approach |
|----------|----------|
| Stable reference for downstream callers | Alias (`live`, `stable`) pointing to a version |
| Rollback capability | Keep previous version; update alias back |
| Canary deployment | Alias with weighted traffic split |
| Environment promotion | `dev` alias → version X; `prod` alias → version Y |
| Avoid using | `$LATEST` directly in production |

---

## State and Caching

### Persistent State in Lambda

Lambda functions are designed to be stateless between invocations. For persistent state, use external services:

| State Type | AWS Service |
|------------|------------|
| Key-value / document store | DynamoDB |
| Relational data | RDS (Aurora Serverless) |
| Cache / session | ElastiCache (Redis/Memcached) |
| File / blob | S3 |
| Ephemeral temp files | /tmp (512 MB, per-container) |

### In-Container Caching (Warm Invocation Optimization)

Static fields persist across warm invocations within the same container. Use this for:

```java
public class OrderHandler {
    // Cache initialized once per container, reused across warm invocations
    private static final AmazonDynamoDB dynamo =
        AmazonDynamoDBClientBuilder.defaultClient();

    // Cache API responses or config for a TTL period
    private static volatile Config cachedConfig = null;
    private static volatile long configLoadedAt = 0;
    private static final long CONFIG_TTL_MS = 5 * 60 * 1000; // 5 minutes

    private static Config getConfig() {
        long now = System.currentTimeMillis();
        if (cachedConfig == null || (now - configLoadedAt) > CONFIG_TTL_MS) {
            cachedConfig = loadConfigFromSSM();
            configLoadedAt = now;
        }
        return cachedConfig;
    }
}
```

**Caveats:**
- Cache is per-container — multiple containers do not share caches
- Container may be recycled at any time; cache is lost on cold start
- Stale data risk: cached data may be outdated if underlying store changes between container recycling
- TTL-based invalidation (shown above) is the standard pattern

### Lambda and Java: GC Considerations

Java GC runs within the Lambda execution environment. Long-running functions with large heaps may see GC pauses that count against your timeout.

- Monitor `Max Memory Used` in REPORT logs — if close to `Memory Size`, increase memory
- G1GC is the default for Java 11 — generally well-suited for Lambda's pause sensitivity
- Avoid large object graphs that trigger major GC during invocations
