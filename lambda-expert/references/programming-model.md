# AWS Lambda Programming Model
## Chapter 3: Execution Environment, Invocation Types, Handler Signatures, I/O, Context

---

## The Lambda Execution Environment

Lambda runs your code inside a managed microVM (Firecracker). Understanding the lifecycle is essential for correctness and performance.

### Lifecycle Phases

```
INIT PHASE (cold start only)
  1. Download deployment package (ZIP/JAR)
  2. Start JVM
  3. Load handler class and its dependencies
  4. Run static initializers and instance constructors

INVOKE PHASE (every invocation)
  1. Call your handler method with (event, context)
  2. Serialize return value to JSON response
  3. Return response or exception

SHUTDOWN PHASE (Lambda decides to reclaim container)
  1. Send SIGTERM to JVM
  2. Brief window for cleanup (not guaranteed)
```

### Warm Container Reuse

After the INIT phase, Lambda *may* reuse the same container for subsequent invocations. There is no guarantee of reuse — Lambda may create new containers to scale out or may discard idle containers.

**Implications:**
- Static fields and JVM heap state persist across warm invocations
- Connections (database, HTTP) created in static initializers survive and can be reused
- Do not store per-invocation state in static fields — it leaks between invocations
- `/tmp` filesystem (up to 512 MB) persists within a container but is not shared across containers

```java
public class OrderHandler implements RequestHandler<OrderRequest, OrderResponse> {
    // Initialized ONCE during cold start, reused on warm invocations
    private static final AmazonDynamoDB dynamo =
        AmazonDynamoDBClientBuilder.defaultClient();

    @Override
    public OrderResponse handleRequest(OrderRequest request, Context ctx) {
        // dynamo is already initialized — fast path
        return processOrder(request);
    }
}
```

---

## Invocation Types

### Synchronous (RequestResponse)

The caller waits for the function to complete and return a value.

| Trigger | Caller |
|---------|--------|
| API Gateway / ALB | HTTP client through AWS |
| Direct SDK invoke | Your application code |

```java
// Caller blocks until Lambda returns
InvokeRequest req = new InvokeRequest()
    .withFunctionName("my-function")
    .withInvocationType(InvocationType.RequestResponse)
    .withPayload("{\"key\":\"value\"}");
InvokeResult result = lambdaClient.invoke(req);
```

### Asynchronous (Event)

The caller sends the event and immediately receives HTTP 202. Lambda queues the event internally and invokes the function. On failure, Lambda retries up to 2 times.

| Trigger | Notes |
|---------|-------|
| S3 object events | Fire and forget |
| SNS notifications | Fan-out capable |
| EventBridge rules | Scheduled or pattern-matched |
| Direct SDK invoke (Event type) | Application fire-and-forget |

**Dead Letter Queue (DLQ)**: Configure an SQS queue or SNS topic to receive events that fail after all retries. Essential for async invocations where data loss is unacceptable.

### Stream (Polling)

Lambda polls the source on your behalf and invokes your function with a batch of records. Failures are handled per-source (see `event-sources.md`).

| Source | Ordering | Retry Behavior |
|--------|---------|----------------|
| Kinesis Data Streams | Per shard, ordered | Retry until success or record expires |
| DynamoDB Streams | Per partition key | Retry until success or record expires |
| SQS Standard | Unordered | Return to queue, retry up to maxReceiveCount |
| SQS FIFO | Per message group | Blocks group until success or DLQ |

---

## Handler Method Signatures

Lambda calls your handler via reflection. The method must be `public` (static or instance).

### Option 1: Implement `RequestHandler<I, O>` (Most Common)

```java
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;

public class MyHandler implements RequestHandler<InputType, OutputType> {
    @Override
    public OutputType handleRequest(InputType input, Context context) {
        // Jackson deserializes JSON event into InputType automatically
        return new OutputType(...);
    }
}
```

**SAM template handler string:** `com.example.MyHandler::handleRequest`

### Option 2: Plain Method (No Interface)

```java
public class MyHandler {
    public OutputType handleRequest(InputType input, Context context) { ... }
}
```

Lambda uses reflection; no interface required. The `RequestHandler` interface provides no functional advantage — just type safety and IDE support.

### Option 3: Streaming I/O

Use when you need raw byte access (large payloads, custom serialization, binary data).

```java
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;

public class StreamingHandler implements RequestStreamHandler {
    @Override
    public void handleRequest(InputStream input, OutputStream output, Context context)
            throws IOException {
        // Read raw bytes from input
        byte[] bytes = input.readAllBytes();
        // Write raw bytes to output
        output.write(processBytes(bytes));
    }
}
```

**Handler string:** `com.example.StreamingHandler::handleRequest`

---

## Input and Output Types

### Basic Types

| Java Type | JSON Equivalent | Notes |
|-----------|----------------|-------|
| `String` | JSON string | Entire event as a string |
| `Integer` / `Long` | JSON number | |
| `Boolean` | JSON boolean | |
| `List<T>` | JSON array | |
| `Map<String,Object>` | JSON object | Untyped, flexible |
| Custom POJO | JSON object | Fields must match JSON keys (Jackson default) |

### Custom POJO I/O

Jackson performs deserialization/serialization automatically. Follow standard Jackson conventions:

```java
// Input POJO
public class OrderRequest {
    private String orderId;
    private int quantity;
    // Getters and setters (or public fields, or @JsonProperty)
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
}
```

**JSON event → Lambda → Java:**
```json
{"orderId": "abc-123", "quantity": 5}
```
becomes `OrderRequest` with `orderId="abc-123"`, `quantity=5`.

### AWS SDK Event Types

Add `aws-lambda-java-events` dependency for typed event classes:

```java
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.lambda.runtime.events.KinesisEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;

public class S3Handler implements RequestHandler<S3Event, Void> {
    @Override
    public Void handleRequest(S3Event event, Context context) {
        event.getRecords().forEach(record -> {
            String bucket = record.getS3().getBucket().getName();
            String key = record.getS3().getObject().getKey();
            // process...
        });
        return null;
    }
}
```

---

## The Context Object

`com.amazonaws.services.lambda.runtime.Context` provides runtime metadata for the current invocation.

| Method | Returns | Use Case |
|--------|---------|---------|
| `getLogger()` | `LambdaLogger` | Write to CloudWatch Logs |
| `getRemainingTimeInMillis()` | `int` | Check time before timeout |
| `getFunctionName()` | `String` | Function name |
| `getFunctionVersion()` | `String` | Version or `$LATEST` |
| `getAwsRequestId()` | `String` | Unique per-invocation ID for tracing |
| `getMemoryLimitInMB()` | `int` | Configured memory |
| `getInvokedFunctionArn()` | `String` | Full ARN including alias |
| `getIdentity()` | `CognitoIdentity` | Mobile identity (if applicable) |
| `getClientContext()` | `ClientContext` | Mobile app metadata (if applicable) |

### Using the Logger

```java
LambdaLogger logger = context.getLogger();
logger.log("Processing order: " + orderId + "\n");  // \n flushes to CloudWatch
```

All output to `LambdaLogger` appears in CloudWatch Logs under `/aws/lambda/<function-name>`.

### Checking Remaining Time

```java
if (context.getRemainingTimeInMillis() < 1000) {
    // Less than 1 second left — abort gracefully
    throw new RuntimeException("Aborting: insufficient time remaining");
}
```

---

## Configuration: Timeout, Memory, Environment Variables

### Timeout

- Default: 3 seconds. Maximum: 15 minutes.
- Lambda terminates the JVM when timeout is reached — no cleanup.
- Set timeout to realistic worst-case plus buffer. A 5-second API call needs at least 8-second timeout.

```yaml
# SAM template
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 30  # seconds
```

### Memory and CPU

Memory setting (128–10,240 MB) directly controls both RAM and vCPU allocation:

| Memory | Approximate vCPU |
|--------|-----------------|
| 128 MB | ~0.07 vCPU |
| 512 MB | ~0.28 vCPU |
| 1,769 MB | ~1 vCPU |
| 3,538 MB | ~2 vCPU |
| 10,240 MB | ~6 vCPU |

**Increasing memory beyond what you need for RAM may be cost-effective** if it reduces duration enough (you pay for GB-seconds).

```yaml
Properties:
  MemorySize: 512  # MB
```

### Environment Variables

```yaml
Properties:
  Environment:
    Variables:
      TABLE_NAME: !Ref OrdersTable
      LOG_LEVEL: INFO
```

```java
String tableName = System.getenv("TABLE_NAME");
```

- Total size limit: 4 KB across all variables.
- Use AWS Systems Manager Parameter Store or Secrets Manager for sensitive values larger than this limit.
- For secrets (passwords, API keys): retrieve from Secrets Manager at init time and cache in a static field.
