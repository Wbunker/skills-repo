# AWS Step Functions — Capabilities Reference
For CLI commands, see [step-functions-cli.md](step-functions-cli.md).

## AWS Step Functions

**Purpose**: Coordinate distributed components into serverless workflows using visual state machines. Handles sequencing, error handling, retries, and parallel execution.

### Standard vs Express Workflows

| Feature | Standard | Express |
|---|---|---|
| **Execution semantics** | Exactly-once | At-least-once |
| **Max duration** | 1 year | 5 minutes |
| **Max execution rate** | 2,000/second | 100,000/second |
| **State transition rate** | 4,000/second | ~unlimited |
| **Pricing** | Per state transition | Per execution (count + duration) |
| **Execution history** | Stored in Step Functions (queryable via API) | Sent to CloudWatch Logs |
| **Synchronous invocation** | No (`StartExecution` only) | Yes (`StartSyncExecution`) |
| **SDK integrations** | Request-response, .sync, .waitForTaskToken | Request-response only |
| **Best for** | Long-running, auditable, human-in-the-loop | High-throughput, IoT, streaming, microservice orchestration |

### Amazon States Language (ASL)

State machines are defined in JSON using ASL. Top-level fields:

```json
{
  "Comment": "optional description",
  "StartAt": "FirstState",
  "States": { ... }
}
```

### State Types

| State | Purpose | Key fields |
|---|---|---|
| **Task** | Invoke a resource (Lambda, ECS, DynamoDB, etc.) | `Resource`, `Parameters`, `ResultPath`, `Retry`, `Catch`, `TimeoutSeconds` |
| **Choice** | Branch based on input data | `Choices` array (each with condition + `Next`), `Default` |
| **Wait** | Pause execution | `Seconds`, `Timestamp`, `SecondsPath`, `TimestampPath` |
| **Parallel** | Execute multiple branches concurrently | `Branches` array; all must complete before proceeding |
| **Map** | Iterate over an array | `Iterator` (inline state machine), `ItemsPath`, `MaxConcurrency` |
| **Pass** | Pass input to output with optional transformation | `Result`, `ResultPath`, `Parameters` |
| **Succeed** | End execution successfully | Terminal state |
| **Fail** | End execution with error | `Error`, `Cause`; terminal state |

### Map State: Inline vs Distributed

| Mode | Max concurrency | Input limit | Use case |
|---|---|---|---|
| **Inline** | 40 | 32,768 characters | Small arrays, moderate concurrency |
| **Distributed** | 10,000 | S3 object (unlimited) | Large-scale parallel processing (millions of items) |

### Error Handling

**Retry**: Define retry behavior per error code.

```json
"Retry": [
  {
    "ErrorEquals": ["Lambda.ServiceException", "Lambda.TooManyRequestsException"],
    "IntervalSeconds": 2,
    "MaxAttempts": 3,
    "BackoffRate": 2,
    "JitterStrategy": "FULL"
  }
]
```

**Catch**: Redirect to a fallback state on unretryable error.

```json
"Catch": [
  {
    "ErrorEquals": ["States.ALL"],
    "Next": "ErrorHandler",
    "ResultPath": "$.error"
  }
]
```

### SDK Integration Patterns

| Pattern | Suffix | Behavior | Availability |
|---|---|---|---|
| **Request response** | (none) | Send request, advance immediately on HTTP 200 | Standard + Express |
| **Optimistic (.sync)** | `.sync:2` | Wait for job completion (Step Functions polls) | Standard only |
| **Callback (.waitForTaskToken)** | `.waitForTaskToken` | Pause until `SendTaskSuccess`/`SendTaskFailure` called with token | Standard only |

Use `.waitForTaskToken` for human approval steps, legacy system integration, or any asynchronous process.

### Activity Tasks

An alternative to SDK integrations where a worker polls Step Functions (`GetActivityTask`), processes the work, then calls `SendTaskSuccess` or `SendTaskFailure`. Useful for on-premises workers or custom compute.

### Workflow Studio

Visual drag-and-drop designer in the AWS console. Generates ASL JSON. Supports real-time execution visualization for debugging.
