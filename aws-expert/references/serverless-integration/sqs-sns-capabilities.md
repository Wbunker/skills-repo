# AWS SQS & SNS — Capabilities Reference
For CLI commands, see [sqs-sns-cli.md](sqs-sns-cli.md).

## Amazon SQS

**Purpose**: Fully managed message queuing service for decoupling and scaling distributed systems and microservices.

### Queue Types

| Feature | Standard Queue | FIFO Queue |
|---|---|---|
| **Ordering** | Best-effort (not guaranteed) | Strict FIFO per message group |
| **Delivery** | At-least-once (occasional duplicates) | Exactly-once processing |
| **Throughput** | Unlimited | 300 msg/s (3,000 with batching); high-throughput mode: 9,000/s (70,000 with batching) |
| **Deduplication** | No | 5-minute deduplication window (content-based or explicit ID) |
| **Use case** | Maximum throughput, order not critical | Order-critical processing (financial transactions, user sessions) |

### Key Parameters

| Parameter | Default | Range | Notes |
|---|---|---|---|
| **VisibilityTimeout** | 30 s | 0 s – 12 h | Time a received message is hidden from other consumers |
| **MessageRetentionPeriod** | 4 days | 60 s – 14 days | After expiry, message deleted automatically |
| **WaitTimeSeconds** | 0 | 0–20 s | Long polling; 0 = short poll; >0 = wait for messages |
| **DelaySeconds** | 0 | 0–15 min | Delay before message becomes visible after send |
| **MaximumMessageSize** | 256 KB | 1 KB – 256 KB | — |

### Dead-Letter Queues (DLQ)

- Set `RedrivePolicy` with `maxReceiveCount` and `deadLetterTargetArn`
- Message moves to DLQ after `maxReceiveCount` failed receive+delete cycles
- DLQ must be the same type as source queue (FIFO DLQ for FIFO source)
- Use DLQ redrive (message move tasks) to replay DLQ messages back to the source queue

### FIFO Queue Specifics

| Concept | Description |
|---|---|
| **MessageGroupId** | Messages with the same group ID are processed in order; different groups processed in parallel |
| **MessageDeduplicationId** | Explicit deduplication ID; or enable content-based deduplication (SHA-256 of body) |
| **Deduplication scope** | 5-minute deduplication window; duplicate messages with same ID are not delivered |

### Long Polling

Set `WaitTimeSeconds` to 1–20 seconds on `ReceiveMessage`. Benefits:
- Reduces empty responses when queue has no messages
- Reduces cost (fewer API calls)
- Can return up to 10 messages per call

### Large Message Handling

Messages > 256 KB: use the Amazon SQS Extended Client Library. Stores the payload in S3 and puts a pointer in the SQS message. Alternatively, send a reference (S3 key) manually.

### Server-Side Encryption

- **SQS managed keys (SSE-SQS)**: Default; no additional cost
- **AWS KMS CMK (SSE-KMS)**: Use your own key; each message encrypted/decrypted with a data key from KMS

### Message Attributes

Up to 10 metadata attributes per message (string, binary, or number). Sent alongside message body; useful for routing, filtering, or metadata without parsing the body.

---

## Amazon SNS

**Purpose**: Fully managed pub/sub messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.

### Topic Types

| Feature | Standard Topic | FIFO Topic |
|---|---|---|
| **Ordering** | Best-effort | Strict FIFO per message group |
| **Delivery** | At-least-once | Exactly-once |
| **Throughput** | ~unlimited | 300 msg/s (3,000 with batching) |
| **Subscribers** | SQS, Lambda, HTTP/S, email, SMS, mobile push, Firehose | SQS FIFO only |
| **Filtering** | Yes | Yes |

### Subscription Protocols

| Protocol | Description |
|---|---|
| **Amazon SQS** | Delivers to an SQS queue; supports Standard and FIFO topics |
| **AWS Lambda** | Invokes Lambda function |
| **HTTP/HTTPS** | POSTs JSON to an endpoint |
| **Email / Email-JSON** | Sends email; requires subscription confirmation |
| **SMS** | Sends text message to a phone number |
| **Mobile push** | FCM (Android), APNS (iOS), ADM (Amazon), Baidu (China) |
| **Amazon Data Firehose** | Delivers to Kinesis Firehose |
| **Application** | Delivers to a platform endpoint (mobile push) |

### Message Filtering

- Each subscription can have a filter policy (JSON object)
- SNS evaluates the filter against message attributes (or message body with `FilterPolicyScope: MessageBody`)
- Messages not matching the filter are not delivered to that subscriber
- Reduces subscriber costs and processing overhead

### Fanout Pattern

Single SNS topic → multiple SQS queues, each with independent consumers. Provides:
- Parallel asynchronous processing
- Message durability (SQS stores messages until processed)
- Independent scaling per consumer

### Cross-Account Delivery

Add an SNS topic policy (`aws:SourceAccount` or specific ARN conditions) to allow another account's SQS queue or Lambda to subscribe. The subscribing principal must also have permission to invoke the SNS actions.

### SMS

- A2P SMS: transactional and promotional messages
- Origination numbers: long codes, short codes, toll-free numbers (varies by country)
- Monthly spending limit configurable per account
- Opt-out handling: SNS manages opt-out lists automatically

### Mobile Push

Create a **Platform Application** (FCM, APNS, ADM, Baidu) then register device tokens as **Platform Endpoints**. Publish to an endpoint or topic with subscribed endpoints.

### Data Protection Policy

Define data protection policies on SNS topics to detect, mask, and audit PII/PHI data in transit (credit card numbers, SSNs, email addresses, etc.) using managed or custom data identifiers. Uses AWS Macie's data identifier engine.
