# Lambda Event Sources
## Chapter 5: API Gateway, S3, Kinesis, DynamoDB Streams, SQS/SNS, Event Source Semantics

---

## Event Source Concepts

An **event source** is an AWS service that triggers your Lambda function. The invocation model varies by source:

| Model | How It Works | Examples |
|-------|-------------|---------|
| **Push (sync)** | Source calls Lambda synchronously; waits for response | API Gateway, ALB |
| **Push (async)** | Source calls Lambda asynchronously; Lambda retries on failure | S3, SNS, EventBridge |
| **Poll (streaming)** | Lambda polls source; invoked with a batch of records | Kinesis, DynamoDB Streams, SQS |

---

## API Gateway (HTTP / REST)

API Gateway is the most common synchronous event source. It translates HTTP requests into Lambda invocations.

### Two API Types

| Type | Use When |
|------|----------|
| REST API (v1) | Full feature set, usage plans, request validation |
| HTTP API (v2) | Lower cost, lower latency, simpler config |

### Request Event Shape (REST API)

```json
{
  "httpMethod": "POST",
  "path": "/orders",
  "pathParameters": {"orderId": "abc-123"},
  "queryStringParameters": {"page": "1"},
  "headers": {"Content-Type": "application/json", "Authorization": "Bearer ..."},
  "body": "{\"quantity\": 5}",
  "isBase64Encoded": false,
  "requestContext": {
    "requestId": "abc-xyz",
    "stage": "Prod",
    "identity": {"sourceIp": "1.2.3.4"}
  }
}
```

### Response Shape

Lambda must return a specific structure for API Gateway to form an HTTP response:

```java
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;

public class ApiHandler implements
        RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Override
    public APIGatewayProxyResponseEvent handleRequest(
            APIGatewayProxyRequestEvent request, Context context) {

        String body = request.getBody();
        // ... process ...

        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withHeaders(Map.of("Content-Type", "application/json"))
            .withBody("{\"result\": \"ok\"}");
    }
}
```

**Error handling**: Return appropriate HTTP status codes (`400`, `404`, `500`) rather than throwing exceptions. Thrown exceptions result in API Gateway returning a 502.

### SAM Configuration

```yaml
Events:
  GetOrder:
    Type: Api
    Properties:
      Path: /orders/{orderId}
      Method: get
  CreateOrder:
    Type: Api
    Properties:
      Path: /orders
      Method: post
```

---

## Amazon S3

S3 invokes Lambda asynchronously when objects are created, modified, or deleted.

### Event Shape

```java
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.s3.event.S3EventNotification.S3EventNotificationRecord;

public class S3Handler implements RequestHandler<S3Event, Void> {
    private static final AmazonS3 s3 = AmazonS3ClientBuilder.defaultClient();

    @Override
    public Void handleRequest(S3Event event, Context context) {
        for (S3EventNotificationRecord record : event.getRecords()) {
            String bucket = record.getS3().getBucket().getName();
            String key = record.getS3().getObject().getUrlDecodedKey();
            // Download and process object
            S3Object obj = s3.getObject(bucket, key);
        }
        return null;
    }
}
```

### SAM Configuration

```yaml
Events:
  S3Upload:
    Type: S3
    Properties:
      Bucket: !Ref InputBucket
      Events: s3:ObjectCreated:*
      Filter:
        S3Key:
          Rules:
            - Name: suffix
              Value: .csv
```

### S3 Semantics

- Invocation is **asynchronous** (fire and forget from S3's perspective)
- Lambda retries up to **2 times** on failure
- Configure a DLQ to capture failed events
- S3 event notifications can have **duplicate deliveries** — design your handler to be idempotent

---

## Amazon Kinesis Data Streams

Kinesis is a real-time streaming service. Lambda polls Kinesis and invokes your function with batches of records.

### Event Shape

```java
import com.amazonaws.services.lambda.runtime.events.KinesisEvent;

public class KinesisHandler implements RequestHandler<KinesisEvent, Void> {
    @Override
    public Void handleRequest(KinesisEvent event, Context context) {
        for (KinesisEvent.KinesisEventRecord record : event.getRecords()) {
            String shardId = record.getEventID();
            String data = record.getKinesis().getData().toString();
            // Data is Base64-encoded in the event; SDK decodes it
            byte[] bytes = record.getKinesis().getData().array();
            String payload = new String(bytes, StandardCharsets.UTF_8);
        }
        return null;
    }
}
```

### Kinesis Semantics

- Records within a shard are **ordered and delivered at-least-once**
- Lambda processes one shard at a time per event source mapping
- On failure (unhandled exception), Lambda **retries the entire batch** repeatedly until it succeeds or the record expires (default 24h–7 days retention)
- An unprocessable record in a batch blocks all subsequent records in that shard

**Handling poison-pill records:**
- Configure `bisectBatchOnFunctionError: true` — Lambda splits batch in half to isolate bad records
- Configure `destinationConfig.onFailure` to send failed records to SQS/SNS

### SAM Configuration

```yaml
Events:
  KinesisStream:
    Type: Kinesis
    Properties:
      Stream: !GetAtt OrderStream.Arn
      StartingPosition: LATEST         # or TRIM_HORIZON (read from start)
      BatchSize: 100
      BisectBatchOnFunctionError: true
      DestinationConfig:
        OnFailure:
          Destination: !GetAtt FailedRecordQueue.Arn
```

---

## Amazon DynamoDB Streams

DynamoDB Streams capture item-level changes (INSERT, MODIFY, REMOVE) from a DynamoDB table.

### Event Shape

```java
import com.amazonaws.services.lambda.runtime.events.DynamodbEvent;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;

public class DynamoDBHandler implements RequestHandler<DynamodbEvent, Void> {
    @Override
    public Void handleRequest(DynamodbEvent event, Context context) {
        for (DynamodbEvent.DynamodbStreamRecord record : event.getRecords()) {
            String eventName = record.getEventName(); // INSERT, MODIFY, REMOVE
            Map<String, AttributeValue> newImage = record.getDynamodb().getNewImage();
            Map<String, AttributeValue> oldImage = record.getDynamodb().getOldImage();
        }
        return null;
    }
}
```

### DynamoDB Streams Semantics

- Ordered per partition key (each shard maps to one or more partition key ranges)
- Same retry semantics as Kinesis: blocks on failure until success or stream record expires
- Use `bisectBatchOnFunctionError` and failure destinations (same as Kinesis)
- Common use case: **change data capture** — propagate DynamoDB changes to Elasticsearch, S3, or another service

### SAM Configuration

```yaml
Events:
  DDBStream:
    Type: DynamoDB
    Properties:
      Stream: !GetAtt OrdersTable.StreamArn
      StartingPosition: TRIM_HORIZON
      BatchSize: 25
      BisectBatchOnFunctionError: true
```

Requires `StreamSpecification` on the DynamoDB table:
```yaml
StreamSpecification:
  StreamViewType: NEW_AND_OLD_IMAGES  # NEW_IMAGE, OLD_IMAGE, KEYS_ONLY, or NEW_AND_OLD_IMAGES
```

---

## Amazon SQS

SQS is a managed message queue. Lambda polls SQS and invokes your function with batches of messages.

### Event Shape

```java
import com.amazonaws.services.lambda.runtime.events.SQSEvent;

public class SQSHandler implements RequestHandler<SQSEvent, Void> {
    @Override
    public Void handleRequest(SQSEvent event, Context context) {
        for (SQSEvent.SQSMessage message : event.getRecords()) {
            String body = message.getBody();
            String messageId = message.getMessageId();
            // Process message
        }
        return null;
    }
}
```

### SQS Semantics

- **Standard queue**: Unordered, at-least-once delivery
- **FIFO queue**: Ordered within a message group, exactly-once delivery
- Lambda **deletes messages from SQS automatically** if the handler returns successfully
- On failure (unhandled exception), Lambda does NOT delete messages — they return to the queue
- After `maxReceiveCount` failures, SQS moves the message to the DLQ

**Partial batch failures**: If some messages succeed and others fail, Lambda deletes all or none. Use `ReportBatchItemFailures` to return only failed message IDs:

```java
public SQSBatchResponse handleRequest(SQSEvent event, Context context) {
    List<SQSBatchResponse.BatchItemFailure> failures = new ArrayList<>();
    for (SQSEvent.SQSMessage msg : event.getRecords()) {
        try {
            process(msg);
        } catch (Exception e) {
            failures.add(SQSBatchResponse.BatchItemFailure.builder()
                .withItemIdentifier(msg.getMessageId()).build());
        }
    }
    return SQSBatchResponse.builder().withBatchItemFailures(failures).build();
}
```

### SAM Configuration

```yaml
Events:
  SQSTrigger:
    Type: SQS
    Properties:
      Queue: !GetAtt OrderQueue.Arn
      BatchSize: 10
      FunctionResponseTypes:
        - ReportBatchItemFailures
```

---

## Amazon SNS

SNS invokes Lambda asynchronously. SNS is a fan-out mechanism — one message can trigger multiple Lambda subscriptions.

```java
import com.amazonaws.services.lambda.runtime.events.SNSEvent;

public class SNSHandler implements RequestHandler<SNSEvent, Void> {
    @Override
    public Void handleRequest(SNSEvent event, Context context) {
        for (SNSEvent.SNSRecord record : event.getRecords()) {
            String message = record.getSNS().getMessage();
            String subject = record.getSNS().getSubject();
        }
        return null;
    }
}
```

SNS uses async invocation semantics (same retry/DLQ behavior as S3).

---

## Event Source Comparison Summary

| Source | Invocation | Ordering | Retry on Failure | Batch | Ideal For |
|--------|-----------|---------|-----------------|-------|-----------|
| API Gateway | Sync | N/A | Caller retries | No | REST APIs, webhooks |
| S3 | Async | No | 2x then DLQ | No | File processing |
| SNS | Async | No | 2x then DLQ | No | Fan-out notifications |
| EventBridge | Async | No | Configurable | No | Scheduled tasks, events |
| Kinesis | Stream/Poll | Per shard | Until success or expiry | Yes | Ordered stream processing |
| DynamoDB Streams | Stream/Poll | Per partition | Until success or expiry | Yes | Change data capture |
| SQS Standard | Stream/Poll | No | Until maxReceiveCount | Yes | Decoupled work queues |
| SQS FIFO | Stream/Poll | Per group | Until maxReceiveCount | Yes | Ordered work queues |

---

## Example: Serverless API (API Gateway + DynamoDB)

```
Client → API Gateway → Lambda (OrderHandler) → DynamoDB
```

Architecture:
1. API Gateway REST API with routes `POST /orders`, `GET /orders/{id}`
2. Single Lambda function handles all routes (or separate functions per route)
3. DynamoDB table for persistence
4. IAM execution role with DynamoDB CRUD permissions

Key considerations:
- Parse `httpMethod` and `path` to route within handler if using one function
- Return proper HTTP status codes
- Set CORS headers if called from a browser

## Example: Serverless Data Pipeline (S3 + Lambda + S3)

```
Source S3 Bucket (CSV uploads)
    → S3 Event Notification
    → Lambda (transform CSV to JSON)
    → Write to Destination S3 Bucket
    → Trigger downstream (Kinesis / DynamoDB / Notification)
```

Key considerations:
- Use object key prefix/suffix filters in S3 event to avoid infinite loops (input ≠ output bucket or prefix)
- Handle large files: stream from S3 using `S3Object.getObjectContent()` rather than loading fully into memory
- Idempotency: if re-invoked with same S3 key, produce same output
