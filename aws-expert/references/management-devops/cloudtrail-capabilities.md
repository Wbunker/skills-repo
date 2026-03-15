# AWS CloudTrail — Capabilities Reference
For CLI commands, see [cloudtrail-cli.md](cloudtrail-cli.md).

**Purpose**: Records AWS API calls and account activity for auditing, compliance, and security analysis.

## Core Concepts

| Concept | Description |
|---|---|
| **Trail** | Configuration that delivers event records to an S3 bucket; optionally to CloudWatch Logs and EventBridge |
| **Management events** | Control-plane operations (CreateBucket, TerminateInstances, AttachRolePolicy); enabled by default in Event History |
| **Data events** | Data-plane operations on resources (S3 object-level GetObject/PutObject, Lambda Invoke, DynamoDB GetItem); high volume, must be explicitly enabled |
| **Insights events** | Anomalous API call rates or error rates detected by CloudTrail Insights; separate from regular events |
| **Event history** | Free, 90-day rolling record of management events in each region; viewable in the console without a trail |
| **CloudTrail Lake** | Managed event data lake; converts events to Apache ORC format; supports SQL queries; retention up to 10 years |
| **Event data store** | The storage unit within CloudTrail Lake; can span accounts via Organizations |
| **Multi-region trail** | Single trail configuration that records events in all current and future regions |
| **Organization trail** | Trail created in the management account that records events for all accounts in the AWS Organization |
| **Log file validation** | CloudTrail creates a digest file for each log delivery; use `validate-logs` to verify no tampering |
| **Log file encryption** | Optionally encrypt trail log files in S3 using a KMS CMK |

## Event Types

| Type | Examples | Default |
|---|---|---|
| **Management (control plane)** | CreateBucket, RunInstances, CreateUser, AttachPolicy | Yes (read+write in Event History) |
| **Data (data plane)** | S3 GetObject/PutObject, Lambda InvokeFunction, DynamoDB GetItem | No (opt-in per resource type) |
| **Insights** | Unusual spike in EC2 TerminateInstances calls; spike in AccessDenied errors | No (opt-in per trail) |
| **Network activity** | VPC endpoint API calls | No (opt-in) |

## CloudTrail Lake

- Query events with standard SQL (`SELECT * FROM eds WHERE eventTime > '2024-01-01' AND errorCode IS NOT NULL`)
- Import historical CloudTrail logs from S3 into Lake for unified querying
- Federation: query Lake event data stores from Amazon Athena
- Dashboards: pre-built visualizations of CloudTrail event trends

## Key Patterns

```
# Typical compliance trail setup:
- Multi-region trail enabled
- Management + S3 data events + Lambda data events
- CloudWatch Logs integration for real-time alerting
- S3 bucket with Object Lock (WORM) for log immutability
- KMS CMK encryption
- SNS notification on log delivery
- Log file validation enabled
```
