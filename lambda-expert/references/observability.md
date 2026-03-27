# Lambda Observability: Logging, Metrics, and Tracing
## Chapter 7: CloudWatch Logs, Structured Logging, Metrics, Alarms, X-Ray Distributed Tracing

---

## Logging

Every Lambda invocation produces log output visible in Amazon CloudWatch Logs.

### Log Group and Log Stream Structure

```
/aws/lambda/<function-name>       ← Log group (one per function)
    └── YYYY/MM/DD/[$LATEST]<hash> ← Log stream (one per container instance)
```

Log streams rotate when a new execution environment (container) is created. Logs from a warm container continue in the same stream.

**Lambda platform log lines** (automatic, not from your code):
```
START RequestId: abc-123 Version: $LATEST
END RequestId: abc-123
REPORT RequestId: abc-123  Duration: 123.45 ms  Billed Duration: 124 ms  Memory Size: 512 MB  Max Memory Used: 89 MB  Init Duration: 312.10 ms
```

The `REPORT` line is critical for monitoring: it shows billed duration, actual memory used, and (on cold starts) init duration.

---

### LambdaLogger (Built-in)

The simplest logging approach. Available via `Context.getLogger()`. No dependencies required.

```java
LambdaLogger logger = context.getLogger();
logger.log("Processing order: " + orderId + "\n");
logger.log(String.format("Processed %d items in %d ms\n", count, elapsed));
```

**Caveats:**
- Always append `\n` — LambdaLogger buffers until newline
- No log levels (INFO, WARN, ERROR) — all goes to CloudWatch as plain text
- Hard to filter in CloudWatch Logs Insights

---

### Java Logging Frameworks (Log4j2 / SLF4J)

AWS provides a Log4j2 appender that routes to CloudWatch Logs. Use SLF4J as the facade for framework-agnostic code.

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-lambda-java-log4j2</artifactId>
    <version>1.5.1</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-slf4j-impl</artifactId>
    <version>2.17.1</version>
</dependency>
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>1.7.36</version>
</dependency>
```

```xml
<!-- src/main/resources/log4j2.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<Configuration>
  <Appenders>
    <Lambda name="Lambda">
      <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss} %-5level %logger{36} - %msg%n"/>
    </Lambda>
  </Appenders>
  <Loggers>
    <Root level="INFO">
      <AppenderRef ref="Lambda"/>
    </Root>
  </Loggers>
</Configuration>
```

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderHandler {
    private static final Logger log = LoggerFactory.getLogger(OrderHandler.class);

    public void handleRequest(OrderRequest request, Context ctx) {
        log.info("Received order {}", request.getOrderId());
        log.warn("Inventory low for SKU {}", sku);
        log.error("Failed to save order", exception);
    }
}
```

---

### Structured Logging (JSON)

Plain-text logs are hard to query. Structured JSON logs allow CloudWatch Logs Insights to filter and aggregate by field.

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.Map;

private static final ObjectMapper mapper = new ObjectMapper();

private void logStructured(Context ctx, String level, String message, Map<String, Object> extra) {
    Map<String, Object> entry = new LinkedHashMap<>();
    entry.put("timestamp", Instant.now().toString());
    entry.put("level", level);
    entry.put("requestId", ctx.getAwsRequestId());
    entry.put("message", message);
    if (extra != null) entry.putAll(extra);
    try {
        ctx.getLogger().log(mapper.writeValueAsString(entry) + "\n");
    } catch (JsonProcessingException e) {
        ctx.getLogger().log("Failed to serialize log entry\n");
    }
}

// Usage
logStructured(ctx, "INFO", "Order processed", Map.of(
    "orderId", order.getId(),
    "itemCount", order.getItems().size(),
    "durationMs", elapsed
));
```

**Output in CloudWatch:**
```json
{"timestamp":"2024-01-15T10:30:00Z","level":"INFO","requestId":"abc-123","message":"Order processed","orderId":"ord-456","itemCount":3,"durationMs":45}
```

Now you can query:
```sql
-- CloudWatch Logs Insights
fields @timestamp, level, orderId, durationMs
| filter level = "ERROR"
| sort @timestamp desc
| limit 50
```

---

## CloudWatch Logs Insights

Query language for analyzing Lambda logs.

```sql
-- Find slow invocations (from REPORT lines)
fields @timestamp, @duration, @memorySize, @maxMemoryUsed
| filter @type = "REPORT"
| filter @duration > 5000
| sort @duration desc
| limit 20

-- Find cold starts (REPORT lines with Init Duration)
fields @timestamp, @initDuration
| filter @type = "REPORT" and ispresent(@initDuration)
| stats avg(@initDuration), max(@initDuration), count() by bin(5m)

-- Count errors by type from structured logs
fields @timestamp, level, message
| filter level = "ERROR"
| stats count() by message
| sort count desc
```

---

## Metrics

### Lambda Platform Metrics (Automatic)

Available in CloudWatch under namespace `AWS/Lambda`:

| Metric | Description |
|--------|-------------|
| `Invocations` | Count of invocations (including errors) |
| `Errors` | Count of invocations that threw an exception |
| `Throttles` | Count of invocations throttled by concurrency limit |
| `Duration` | Time from invocation start to return (ms) |
| `ConcurrentExecutions` | Number of function instances running at a point in time |
| `IteratorAge` | For Kinesis/DDB streams: age of oldest record in batch |
| `DeadLetterErrors` | Failures to write to DLQ |
| `UnreservedConcurrentExecutions` | Concurrency used by functions without reserved concurrency |

### Custom Business Metrics

Use CloudWatch custom metrics to track application-specific KPIs.

```java
import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;
import software.amazon.awssdk.services.cloudwatch.model.*;

private static final CloudWatchClient cloudWatch = CloudWatchClient.create();

private void publishMetric(String metricName, double value, StandardUnit unit) {
    cloudWatch.putMetricData(PutMetricDataRequest.builder()
        .namespace("MyApp/Orders")
        .metricData(MetricDatum.builder()
            .metricName(metricName)
            .value(value)
            .unit(unit)
            .timestamp(Instant.now())
            .build())
        .build());
}

// Usage
publishMetric("OrdersProcessed", 1.0, StandardUnit.COUNT);
publishMetric("OrderValue", order.getTotalAmount(), StandardUnit.NONE);
```

**Cost note**: Each unique metric (namespace + name + dimensions) is billed per custom metric per month. Use dimensions sparingly.

### CloudWatch Alarms

Trigger notifications (SNS, auto-scaling) when metrics breach thresholds.

```yaml
# SAM template: alarm on high error rate
OrderFunctionErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: OrderFunction-HighErrorRate
    MetricName: Errors
    Namespace: AWS/Lambda
    Dimensions:
      - Name: FunctionName
        Value: !Ref OrderFunction
    Statistic: Sum
    Period: 60          # 1-minute window
    EvaluationPeriods: 5
    Threshold: 10       # alert if > 10 errors in any 1-minute window over 5 periods
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref AlertTopic  # SNS topic
    TreatMissingData: notBreaching
```

---

## Distributed Tracing with AWS X-Ray

X-Ray captures traces across multiple services, showing where time is spent across a request's path through Lambda, DynamoDB, S3, HTTP calls, etc.

### Enable X-Ray on a Lambda Function

```yaml
# SAM template
OrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    Tracing: Active  # or PassThrough (propagates existing trace, no new segment)
```

```bash
# Or via CLI
aws lambda update-function-configuration \
  --function-name my-function \
  --tracing-config Mode=Active
```

### X-Ray Java SDK

Add the X-Ray SDK to instrument outgoing AWS SDK calls and HTTP requests automatically.

```xml
<dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-xray-recorder-sdk-core</artifactId>
    <version>2.14.0</version>
</dependency>
<dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-xray-recorder-sdk-aws-sdk-v2-instrumentor</artifactId>
    <version>2.14.0</version>
</dependency>
```

With `aws-sdk-v2-instrumentor` on the classpath, all AWS SDK v2 clients are automatically instrumented — no code changes needed.

### Adding Custom Subsegments

```java
import com.amazonaws.xray.AWSXRay;

public void handleRequest(OrderRequest request, Context context) {
    AWSXRay.beginSubsegment("validateOrder");
    try {
        validateOrder(request);
        AWSXRay.endSubsegment();
    } catch (Exception e) {
        AWSXRay.endSubsegment();
        throw e;
    }

    AWSXRay.beginSubsegment("saveOrder");
    try {
        saveOrder(request);
        AWSXRay.endSubsegment();
    } catch (Exception e) {
        AWSXRay.endSubsegment();
        throw e;
    }
}
```

Or use the functional form:

```java
AWSXRay.createSubsegment("validateOrder", (subsegment) -> {
    validateOrder(request);
    return null;
});
```

### Adding Metadata and Annotations

```java
// Annotations: indexed, filterable in X-Ray console
AWSXRay.getCurrentSegment().putAnnotation("orderId", request.getOrderId());
AWSXRay.getCurrentSegment().putAnnotation("orderTotal", request.getTotal());

// Metadata: not indexed, visible in trace detail
AWSXRay.getCurrentSegment().putMetadata("orderDetails", request);
```

### Finding Errors with X-Ray

In the X-Ray console:
- **Service map**: Visual graph of services involved in a request
- **Traces**: Filter by error, fault, throttle, or annotation value
- **Analytics**: Aggregate trace data by response time percentile

```
Filter expression examples:
  error = true                    ← client errors (4xx)
  fault = true                    ← server errors (5xx)
  annotation.orderId = "abc-123" ← find specific order traces
  duration > 5                    ← slow traces over 5 seconds
```

---

## Observability Checklist

| Concern | Solution |
|---------|---------|
| Function errors | CloudWatch `Errors` metric alarm |
| Throttling | CloudWatch `Throttles` metric alarm |
| Slow performance | CloudWatch `Duration` P99 alarm |
| Stream lag | CloudWatch `IteratorAge` alarm (Kinesis/DDB) |
| Cold starts | Logs Insights query on `@initDuration` |
| Distributed request tracing | X-Ray Active tracing |
| Business KPIs | Custom CloudWatch metrics |
| Log querying | CloudWatch Logs Insights with structured JSON |
| Memory sizing | REPORT logs: compare `Memory Size` vs `Max Memory Used` |
