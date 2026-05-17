# AWS Lambda Error Handling — Capabilities Reference

For CLI commands (DLQ, destinations, ESM config), see [lambda-error-handling-cli.md](lambda-error-handling-cli.md).
For Lambda core concepts, see [lambda-capabilities.md](lambda-capabilities.md).

## Error Types

| Error type | HTTP status | `X-Amz-Function-Error` header | Cause |
|---|---|---|---|
| **Function error (handled)** | 200 | `Handled` | Code caught and returned error object |
| **Function error (unhandled)** | 200 | `Unhandled` | Uncaught exception, timeout, OOM, runtime crash |
| **Invocation error** | 4xx / 5xx | Not present | Throttle, malformed request, auth failure, resource not found |

**JSON error response body:**
```json
{
  "errorType": "TypeError",
  "errorMessage": "Cannot read property 'x' of undefined",
  "stackTrace": [
    "at Object.<anonymous> (/var/task/index.js:5:15)"
  ]
}
```

Common `errorType` values from the runtime: `TimeoutError`, `Runtime.OutOfMemory`, `Runtime.ExitError` (crash), `Runtime.HandlerNotFound`.

---

## By Invocation Type

### Synchronous

- Function error returns HTTP **200** with error body + `X-Amz-Function-Error` header
- Throttle / invocation error returns HTTP **4xx/5xx**
- Lambda does **not** auto-retry; caller is responsible
- The `StatusCode` in the CLI/SDK response reflects the invocation HTTP status (200 even for function errors)

### Asynchronous

| Setting | Range | Default |
|---|---|---|
| `MaximumRetryAttempts` | 0 – 2 | 2 (3 total attempts) |
| `MaximumEventAgeInSeconds` | 60 – 21600 | 21600 (6 hours) |

**Retry backoff:** 1 min between attempt 1→2; 2 min between attempt 2→3.
**Throttle/system errors (429, 5xx):** exponential backoff from 1s to 5 min intervals, retried up to 6 hours.
After exhausting retries or max age: event sent to on-failure destination or DLQ (if configured), otherwise dropped (`AsyncEventsDropped` metric fires).

API: `put-function-event-invoke-config` / `update-function-event-invoke-config`

### Event Source Mapping (ESM)

See per-source sections below.

---

## Dead Letter Queues (DLQ)

- Targets: **SQS standard queue** or **SNS standard topic** only (no FIFO)
- Lambda sends the **original event payload only** — no response context
- Message attributes included:

| Attribute | Type | Value |
|---|---|---|
| `RequestID` | String | Invocation request ID |
| `ErrorCode` | Number | HTTP status code |
| `ErrorMessage` | String | First 1 KB of error message |

- If Lambda cannot deliver to DLQ: event is deleted and `DeadLetterErrors` CloudWatch metric fires
- DLQ is configured at the **function level** (not alias/version)
- For SQS as an event source: configure DLQ on the **SQS queue itself**, not on the Lambda function

---

## Lambda Destinations

More information than DLQ — includes full request/response context.

**Valid destination types:**

| Condition | Valid targets |
|---|---|
| `OnSuccess` (async) | SQS, SNS, Lambda, EventBridge |
| `OnFailure` (async) | SQS, SNS, Lambda, EventBridge, S3 |
| `OnFailure` (ESM — Kinesis/DynamoDB/Kafka) | SQS, SNS, Lambda, EventBridge, S3 |

**Destination payload:**
```json
{
  "version": "1.0",
  "timestamp": "2019-11-14T18:16:05.568Z",
  "requestContext": {
    "requestId": "...",
    "functionArn": "...",
    "condition": "RetriesExhausted",
    "approximateInvokeCount": 3
  },
  "requestPayload": { "...original event..." },
  "responseContext": {
    "statusCode": 200,
    "executedVersion": "$LATEST",
    "functionError": "Unhandled"
  },
  "responsePayload": { "...error body..." }
}
```

**Precedence:** Destination takes precedence over DLQ. If both are set, destination receives the record; DLQ only fires if no on-failure destination is configured.

API: `put-function-event-invoke-config --destination-config`

---

## Event Source Mapping Error Handling

### SQS

| Behavior | Detail |
|---|---|
| Batch failure (exception) | All messages in batch become visible again after visibility timeout; entire batch re-queued |
| Partial batch response | Return `{ "batchItemFailures": [{"itemIdentifier": "msgId"}] }` — only listed messages re-queued |
| FIFO queues | Stops after first failure; all remaining messages in group treated as failed |
| Visibility timeout | Must be **≥ function timeout**; messages are hidden during processing |
| SQS redrive / DLQ | Triggered by SQS `maxReceiveCount` independently of Lambda retry logic |

**Enable partial batch response:**
```
FunctionResponseTypes=["ReportBatchItemFailures"]
```
on the event source mapping (not the function config).

### Kinesis and DynamoDB Streams

| Setting | Range | Default |
|---|---|---|
| `MaximumRetryAttempts` | -1 (infinite) – 10,000 | -1 (infinite) |
| `MaximumRecordAgeInSeconds` | -1 or 60 – 604800 | -1 (infinite) |
| `BisectBatchOnFunctionError` | true / false | false |

- On error: **shard processing blocks** until error resolves or records expire — can stall for up to 7 days (Kinesis) or 24 hours (DynamoDB) with default settings
- `BisectBatchOnFunctionError`: splits failed batch in half to isolate bad records; cannot be combined with `MaximumRetryAttempts=-1`
- On-failure destination payload includes `KinesisBatchInfo` or `DDBStreamBatchInfo` with shardId, sequence number range, batchSize, streamArn (S3 destination also includes full payload)
- Throttles do **not** count toward `MaximumRetryAttempts`

### MSK / Kafka

- `BisectBatchOnFunctionError` available (same constraints as Kinesis)
- On-failure destination: Kafka topic (`kafka://<topic-name>`); cannot be the same as source topic
- Execution role needs `kafka-cluster:WriteData` on destination topic
- Error handling and on-failure destinations require **provisioned polling** (`ProvisionedPollerConfig`)

---

## Partial Batch Response Summary

| Source | `itemIdentifier` field | Enable via |
|---|---|---|
| SQS | `messageId` | `FunctionResponseTypes=["ReportBatchItemFailures"]` on ESM |
| Kinesis | `sequenceNumber` | Same ESM config key |
| DynamoDB Streams | `sequenceNumber` | Same ESM config key |

Return empty `batchItemFailures` (or null) for complete success. Return invalid JSON or empty `itemIdentifier` to fail the entire batch.

---

## Throttle Error Handling (429)

| Invocation type | Behavior |
|---|---|
| Synchronous | 429 returned directly to caller; caller retries |
| Asynchronous | Event returned to internal queue; exponential backoff (1s–5min) for up to 6 hours |
| ESM (SQS) | Lambda backs off polling; message stays in queue until visibility timeout expires, then re-appears |
| ESM (Kinesis/DynamoDB) | Shard processing paused; retried; throttles do NOT count toward `MaximumRetryAttempts` |

---

## CloudWatch Error Metrics

| Metric | Scope | Description |
|---|---|---|
| `Errors` | Invocations | Function errors (exceptions + runtime errors like timeouts). Use `Sum`. |
| `Throttles` | Invocations | 429 rejections. Not counted in `Errors` or `Invocations`. |
| `DeadLetterErrors` | Async | Failed DLQ delivery attempts. |
| `DestinationDeliveryFailures` | Async + ESM | Failed destination delivery attempts. |
| `AsyncEventsDropped` | Async | Events discarded after exhausting retries/max age. |
| `AsyncEventAge` | Async | Time between queuing and invocation; rises during retries. |
| `IteratorAge` | Kinesis / DynamoDB ESM | Age of last record processed; rising = growing shard backlog. |
| `DroppedEventCount` | ESM | Events dropped due to MaxRecordAge or MaxRetryAttempts exhaustion. |

---

## Lambda Powertools — Error Handling Utilities

**Batch Processor** (`aws_lambda_powertools.utilities.batch`):
- Handles `ReportBatchItemFailures` automatically for SQS, Kinesis, and DynamoDB
- Available in Python, TypeScript, Java, .NET
- Usage: `BatchProcessor(event_type=EventType.SQS)` + `process_partial_response()`
- Raises exceptions per-record; builds `batchItemFailures` response automatically — no manual response construction needed

**Idempotency** (`aws_lambda_powertools.utilities.idempotency`):
- Prevents duplicate processing using DynamoDB as a persistence layer
- Wraps handler or individual operations; relevant for retry scenarios
