# AWS EventBridge — Capabilities Reference
For CLI commands, see [eventbridge-cli.md](eventbridge-cli.md).

## Amazon EventBridge

**Purpose**: Serverless event bus connecting applications using events. Route events from AWS services, SaaS partners, and custom applications to targets with flexible filtering and transformation.

### Event Buses

| Bus type | Description |
|---|---|
| **Default** | Receives events from AWS services automatically; one per account per region |
| **Custom** | Created by you for application events; supports cross-account delivery |
| **Partner** | Receives events from SaaS partners (Datadog, Zendesk, PagerDuty, Shopify, etc.) |

### Rules

- **Event pattern**: JSON filter matching event fields; supports prefix, suffix, exists, numeric range, anything-but conditions
- **Schedule**: cron or rate expression (moved to EventBridge Scheduler for new use cases)
- Up to 300 rules per bus (default)
- Rules can fan out to up to 5 targets each

### Targets

EventBridge supports 50+ AWS service targets including: Lambda, Step Functions, SQS, SNS, Kinesis Firehose, ECS tasks, API Gateway, CodeBuild, SSM Run Command, API destinations (HTTP endpoints), and EventBridge buses in other accounts/regions.

### Input Transformation

Transform the event before delivering to a target:
- **Input path**: Extract a JSON field
- **Input template**: Build a new JSON document from extracted paths and constants
- **Matched event**: Pass the full matched event (default)

### Schema Registry and Discovery

- EventBridge can infer schemas from events on a bus (enable schema discovery)
- Schemas stored in the schema registry (AWS service schemas + custom schemas)
- Download code bindings for schemas in Java, Python, TypeScript

### Archive and Replay

- Archive events from any bus with optional event pattern filter and retention period
- Replay archived events back to the bus from a time range; useful for re-processing after bug fixes

### Cross-Account Event Bus Policies

Add a resource-based policy to a custom bus to allow another account or organization to put events (`events:PutEvents`).

### EventBridge Pipes

Point-to-point integration: one source → optional filter → optional enrichment → one target. Reduces integration code.

| Stage | Options |
|---|---|
| **Source** | SQS, Kinesis, DynamoDB Streams, MSK, self-managed Kafka, Amazon MQ, DynamoDB (via ESM) |
| **Filtering** | JSON event patterns (same syntax as EventBridge rules); only matching events proceed |
| **Enrichment** | Lambda, Step Functions (Express), API Gateway, EventBridge API Destination |
| **Target** | 14+ targets: Lambda, Step Functions, SQS, SNS, EventBridge bus, Kinesis, Firehose, API Gateway, API Destination, ECS task, Redshift, SageMaker Pipeline, CloudWatch Logs, Inspector |

You are only charged for events that pass the filter.

### EventBridge Scheduler

Fully managed scheduler decoupled from EventBridge rules. Supports:

| Schedule type | Expression example |
|---|---|
| **One-time** | ISO 8601 datetime: `at(2025-01-15T17:00:00)` |
| **Rate** | `rate(5 minutes)` |
| **Cron** | `cron(0 9 ? * MON-FRI *)` |

**Key features**:
- **Flexible time windows**: Deliver within a time window (e.g., within 15 minutes of scheduled time) to reduce thundering herd
- **Timezone support**: Specify IANA timezone (e.g., `America/New_York`)
- **270+ AWS services**: Universal targets via SDK API calls (not limited to EventBridge rule targets)
- **At-least-once delivery** with configurable retry policy and max retention
- **Schedule groups**: Organize schedules; tag-based; delete group to delete all schedules within it

---

## Amazon EventBridge Pipes

**Purpose**: Point-to-point integrations connecting event producers to consumers with optional filtering and enrichment — reduces custom glue code.

### Core Concepts

| Concept | Description |
|---|---|
| **Pipe** | The end-to-end integration resource: source → filter → enrichment → target |
| **Source** | The polling event producer (queue, stream, or broker) |
| **Filter** | JSON path filter criteria; only events matching the pattern proceed to enrichment/target |
| **Enrichment** | Optional call to a Lambda, Step Functions Express, API Gateway, or API destination to transform/augment the event |
| **Target** | The destination service that receives the (optionally enriched) event |
| **Batching** | Source-level batch size and batch window configuration |
| **Source Parameters** | Per-source-type settings (e.g., starting position for streams, visibility timeout for SQS) |
| **Target Parameters** | Per-target-type settings (e.g., invocation type for Step Functions, message group ID for SQS FIFO) |

### Supported Sources

| Source | Notes |
|---|---|
| SQS queue | Standard and FIFO; configurable batch size and batching window |
| DynamoDB Streams | Requires stream enabled on table; configurable starting position |
| Kinesis Data Streams | Configurable starting position and batch window |
| Amazon MSK | Managed Streaming for Apache Kafka; topic-level configuration |
| Self-managed Kafka | Bring your own Kafka cluster |
| Amazon MQ (ActiveMQ) | Managed ActiveMQ broker |
| Amazon MQ (RabbitMQ) | Managed RabbitMQ broker |

### Enrichment Options

- **Lambda function**: Invoke synchronously; return value replaces event payload
- **Step Functions (Express Workflow)**: Synchronous execution; output replaces event payload
- **API Gateway**: HTTP/REST call; response body replaces event payload
- **API destinations**: HTTP endpoint (OAuth, API key, or basic auth); response body replaces event payload

### Supported Targets

All EventBridge targets are supported, including: Lambda, Step Functions, SQS, SNS, EventBridge bus, API Gateway, API destinations, Kinesis Firehose, Kinesis Data Streams, ECS task, Redshift, SageMaker Pipeline, CloudWatch Logs, Inspector, and more.

### Input Transformation

- **JSONata**: Full JSONata expression language for complex transformations
- **Input transformer**: InputPathsMap + InputTemplate (same syntax as EventBridge rule input transformers)

### Use Case: Pipes vs EventBridge Rules

| Scenario | Recommended |
|---|---|
| Polling a queue or stream, with optional enrichment before routing | EventBridge Pipes |
| Fan-out from an event bus to multiple targets based on event patterns | EventBridge Rules |
| Cross-account/cross-region event routing | EventBridge Rules + custom bus |

### Batching

Configure at the source level:
- **Batch size**: Number of records per invocation (e.g., 1–10,000 for SQS)
- **Batch window**: Maximum time to wait before invoking target with a partial batch (available for SQS, Kinesis, DynamoDB Streams)

---

## Amazon EventBridge Scheduler

**Purpose**: Fully managed scheduler for invoking AWS targets on a schedule; 270+ target APIs across 35+ AWS services.

### Core Concepts

| Concept | Description |
|---|---|
| **Schedule** | The scheduling resource: expression + target + delivery settings |
| **Schedule Group** | Logical container for schedules; supports tagging; deleting a group deletes all schedules in it |
| **One-Time Schedule** | Fires once at a specified datetime (`at()` expression) |
| **Recurring Schedule** | Fires repeatedly on a rate or cron expression |
| **Rate Expression** | `rate(value unit)` — e.g., `rate(5 minutes)` |
| **Cron Expression** | `cron(Minutes Hours Day-of-month Month Day-of-week Year)` |
| **at() Expression** | `at(yyyy-mm-ddThh:mm:ss)` — ISO 8601 datetime for one-time schedules |
| **Flexible Time Window** | Allows Scheduler to invoke within a window around the scheduled time for load distribution |
| **DLQ** | Dead-letter queue; receives event payload when all retries are exhausted |
| **Retry Policy** | Maximum retry attempts and maximum event age before sending to DLQ |
| **Target** | The AWS SDK API action or templated target to invoke |
| **Execution Role** | IAM role Scheduler assumes to invoke the target |

### Schedule Types

| Type | Expression syntax | Example | Use case |
|---|---|---|---|
| **One-time** | `at(datetime)` | `at(2025-06-01T09:00:00)` | Send a welcome email at account creation + 1 day |
| **Rate-based** | `rate(value unit)` | `rate(5 minutes)` | Poll a data source every 5 minutes |
| **Cron-based** | `cron(...)` | `cron(0 9 ? * MON-FRI *)` | Run a report every weekday at 9 AM |

### Flexible Time Window

Allows Scheduler to invoke the target within a configurable window (1–1440 minutes) around the scheduled time. Use to distribute load when many schedules fire at the same moment (e.g., thousands of cron schedules set for midnight).

### Supported Targets

- **Universal targets**: Any AWS SDK API action via `arn:aws:scheduler:::aws-sdk:<service>:<action>` — e.g., start an EC2 instance, send an SQS message, start a Step Functions execution, invoke Lambda, run an ECS task, put a Kinesis record, and more
- **Templated targets**: Pre-configured for common services with simplified parameter schemas — Lambda Invoke, SQS SendMessage, Step Functions StartExecution, AWS Batch SubmitJob, ECS RunTask, and more

### EventBridge Scheduler vs CloudWatch Events / EventBridge Rules Scheduled

| Feature | EventBridge Scheduler | EventBridge Rules (scheduled) |
|---|---|---|
| Scale | Millions of schedules | Hundreds of rules per bus |
| Per-schedule DLQ | Yes | No |
| Per-schedule retry policy | Yes | No |
| Flexible time windows | Yes | No |
| Timezone support | Yes (IANA) | No |
| Universal SDK targets | Yes (270+ APIs) | No (fixed target list) |
| Recommendation | Preferred for new use cases | Legacy; migrate to Scheduler |
