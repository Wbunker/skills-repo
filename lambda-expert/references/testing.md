# Testing Lambda Functions
## Chapter 6: Test Pyramid, Refactoring for Testability, Unit/Functional/E2E Tests, Local Testing

---

## The Testing Challenge

Lambda functions are harder to test than traditional services because:
- The platform (execution environment, event routing, IAM) is managed by AWS
- Cold starts and container reuse are platform behaviors you cannot replicate locally
- Local execution gaps: environment variables, IAM role, VPC, timeouts behave differently

The solution: a **test pyramid** with layers of increasing fidelity and decreasing speed.

---

## The Lambda Test Pyramid

```
           /\
          /E2E\          ← Slow, costly, high confidence
         /______\           Deploy to AWS, invoke via real event source
        /Functional\     ← Medium speed, medium cost
       /____________\       Call handler directly against real AWS services
      /  Unit Tests  \    ← Fast, cheap, catches logic bugs early
     /________________\     Pure Java, no AWS, heavily mocked
```

| Layer | What It Tests | Speed | Cost | AWS Needed? |
|-------|--------------|-------|------|-------------|
| Unit | Business logic in isolation | Milliseconds | Free | No |
| Functional | Handler + real AWS services (test account) | Seconds | Low | Yes |
| End-to-End | Full stack via real event source | Seconds–minutes | Medium | Yes |

---

## Refactoring for Testability

Vanilla Lambda handlers are hard to unit test because they mix business logic with AWS SDK calls. Refactor to separate concerns.

### Before: Untestable Handler

```java
public class BulkEventsLambda implements RequestHandler<SQSEvent, Void> {
    @Override
    public Void handleRequest(SQSEvent event, Context context) {
        AmazonDynamoDB dynamo = AmazonDynamoDBClientBuilder.defaultClient();
        DynamoDBMapper mapper = new DynamoDBMapper(dynamo);
        for (SQSEvent.SQSMessage msg : event.getRecords()) {
            Order order = parseJson(msg.getBody());
            mapper.save(order);
        }
        return null;
    }
}
```

Problems: can't inject mock DynamoDB; constructs client inside handler method; no seam for testing.

### After: Testable Handler

**Step 1 — Add constructors for dependency injection:**

```java
public class BulkEventsLambda implements RequestHandler<SQSEvent, Void> {
    private final DynamoDBMapper mapper;
    private final ObjectMapper objectMapper;

    // Production constructor (used by Lambda runtime via no-arg → calls this)
    public BulkEventsLambda() {
        this(new DynamoDBMapper(AmazonDynamoDBClientBuilder.defaultClient()),
             new ObjectMapper());
    }

    // Test constructor (inject mocks)
    BulkEventsLambda(DynamoDBMapper mapper, ObjectMapper objectMapper) {
        this.mapper = mapper;
        this.objectMapper = objectMapper;
    }

    @Override
    public Void handleRequest(SQSEvent event, Context context) {
        event.getRecords().forEach(msg -> processMessage(msg.getBody()));
        return null;
    }

    void processMessage(String body) {
        try {
            Order order = objectMapper.readValue(body, Order.class);
            saveOrder(order);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse message", e);
        }
    }

    void saveOrder(Order order) {
        mapper.save(order);
    }
}
```

**Step 2 — Isolate side effects into small, overrideable methods** (shown above: `processMessage`, `saveOrder`).

**Step 3 — Split large handler methods** so each is independently testable.

---

## Unit Tests

Pure Java tests. Mock all AWS SDK calls. Fast, no network, no AWS account required.

### Mocking with Mockito

```java
// pom.xml test dependencies
// junit:junit:4.13 or org.junit.jupiter:junit-jupiter:5.x
// org.mockito:mockito-core:4.x

import org.junit.Test;
import org.mockito.Mockito;
import static org.mockito.Mockito.*;
import static org.junit.Assert.*;

public class BulkEventsLambdaTest {
    @Test
    public void processesValidMessage() {
        DynamoDBMapper mockMapper = mock(DynamoDBMapper.class);
        ObjectMapper objectMapper = new ObjectMapper();
        BulkEventsLambda handler = new BulkEventsLambda(mockMapper, objectMapper);

        handler.processMessage("{\"orderId\":\"abc\",\"quantity\":3}");

        ArgumentCaptor<Order> captor = ArgumentCaptor.forClass(Order.class);
        verify(mockMapper).save(captor.capture());
        assertEquals("abc", captor.getValue().getOrderId());
        assertEquals(3, captor.getValue().getQuantity());
    }

    @Test(expected = RuntimeException.class)
    public void throwsOnInvalidJson() {
        DynamoDBMapper mockMapper = mock(DynamoDBMapper.class);
        BulkEventsLambda handler = new BulkEventsLambda(mockMapper, new ObjectMapper());
        handler.processMessage("not valid json");
    }
}
```

### Mocking the Context Object

```java
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;

Context mockContext = mock(Context.class);
LambdaLogger mockLogger = mock(LambdaLogger.class);
when(mockContext.getLogger()).thenReturn(mockLogger);
when(mockContext.getRemainingTimeInMillis()).thenReturn(30000);
```

### Building Test Event Objects

For typed event classes, construct them directly:

```java
SQSEvent event = new SQSEvent();
SQSEvent.SQSMessage message = new SQSEvent.SQSMessage();
message.setBody("{\"orderId\":\"abc\",\"quantity\":3}");
message.setMessageId("msg-001");
event.setRecords(List.of(message));
```

For raw JSON events, use Jackson:
```java
ObjectMapper mapper = new ObjectMapper();
MyEvent event = mapper.readValue(
    getClass().getResourceAsStream("/test-events/order-event.json"),
    MyEvent.class);
```

Store test event JSON files in `src/test/resources/test-events/`.

---

## Functional Tests

Test the handler against real AWS services in a dedicated test AWS account/environment. No mocks — real DynamoDB, S3, etc.

```java
// Integration test: uses real AWS services configured via env vars or test profile
@Test
public void savesOrderToDynamoDB() {
    // Use real DynamoDB pointing at test table
    AmazonDynamoDB dynamo = AmazonDynamoDBClientBuilder.defaultClient();
    DynamoDBMapper mapper = new DynamoDBMapper(dynamo);
    BulkEventsLambda handler = new BulkEventsLambda(mapper, new ObjectMapper());

    SQSEvent event = buildSQSEvent("{\"orderId\":\"test-123\",\"quantity\":1}");
    handler.handleRequest(event, buildContext());

    // Assert directly against DynamoDB
    Order saved = mapper.load(Order.class, "test-123");
    assertNotNull(saved);
    assertEquals(1, saved.getQuantity());

    // Cleanup
    mapper.delete(saved);
}
```

**Best practices:**
- Use a dedicated AWS test account or at minimum a test environment prefix (`test-orders-table` vs `prod-orders-table`)
- Clean up test data in `@After` / `@AfterEach`
- Run via Maven `failsafe` plugin (separates from unit tests):

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-failsafe-plugin</artifactId>
  <executions>
    <execution>
      <goals>
        <goal>integration-test</goal>
        <goal>verify</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

Name integration test classes `*IT.java` to separate from unit tests.

---

## End-to-End Tests

Test the entire system through the real event source (API Gateway, SQS, etc.) with real infrastructure deployed via SAM.

```bash
# Deploy test stack
sam deploy --stack-name my-app-test --parameter-overrides Env=test

# Get API URL from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name my-app-test \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text)

# Run E2E test
curl -X POST "$API_URL/orders" \
  -H "Content-Type: application/json" \
  -d '{"orderId":"e2e-test-001","quantity":2}'
```

Or use Java HttpClient in a JUnit test:

```java
@Test
public void endToEndOrderCreation() throws Exception {
    String apiUrl = System.getenv("API_URL");
    HttpClient client = HttpClient.newHttpClient();
    HttpRequest request = HttpRequest.newBuilder()
        .uri(URI.create(apiUrl + "/orders"))
        .POST(HttpRequest.BodyPublishers.ofString("{\"orderId\":\"e2e-001\",\"quantity\":1}"))
        .header("Content-Type", "application/json")
        .build();
    HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
    assertEquals(200, response.statusCode());
}
```

---

## Local Testing with SAM Local

`sam local` runs your Lambda function locally using Docker (requires Docker daemon running).

```bash
# Invoke function with a test event JSON file
sam local invoke OrderFunction --event events/order-event.json

# Start a local API Gateway server
sam local start-api
# Then: curl http://localhost:3000/orders

# Start a local Lambda endpoint (for SDK testing)
sam local start-lambda
```

**Limitations of SAM local:**
- Does NOT replicate cold start timing accurately
- AWS SDK calls still hit real AWS (or need LocalStack)
- IAM is not enforced
- No real Kinesis/DynamoDB Stream polling simulation
- Environment variables must be set manually or via `--env-vars env.json`

```json
// env.json for sam local
{
  "OrderFunction": {
    "TABLE_NAME": "local-orders",
    "LOG_LEVEL": "DEBUG"
  }
}
```

```bash
sam local invoke OrderFunction --event events/test.json --env-vars env.json
```

---

## Cloud Test Environments

A dedicated AWS environment (account or namespace) for integration and E2E testing:

| Approach | Description |
|----------|-------------|
| Separate AWS account (recommended) | Complete isolation; no risk to prod |
| Same account, different stage | Simpler; risk of cross-contamination |
| Ephemeral stacks per PR | Deploy, test, delete per PR (expensive but isolated) |

**CI/CD integration:**

```bash
# In CI pipeline (GitHub Actions, Jenkins, etc.)
sam build
sam deploy --stack-name my-app-$CI_BRANCH --no-confirm-changeset
mvn verify -P integration-tests  # runs *IT.java tests
sam delete --stack-name my-app-$CI_BRANCH --no-prompts  # cleanup
```
