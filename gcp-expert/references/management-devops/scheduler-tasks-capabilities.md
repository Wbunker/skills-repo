# Cloud Scheduler & Cloud Tasks — Capabilities

## Cloud Scheduler

### Purpose

Fully managed cron job service. Execute scheduled HTTP/HTTPS requests, Pub/Sub messages, or App Engine tasks on a time-based schedule. Equivalent to traditional server cron jobs but fully serverless with built-in retry, monitoring, and global availability.

### Core Concepts

| Concept | Description |
|---|---|
| Job | A single scheduled action with a cron schedule and target |
| Schedule | Cron expression defining when the job fires (unix-cron format) |
| Target type | HTTP, Pub/Sub, or App Engine HTTP |
| Retry config | Number of retries, minimum backoff, maximum backoff, max doublings |
| Timezone | IANA timezone for the schedule (e.g., `America/New_York`, `UTC`) |
| Paused | Job suspended; continues to exist but does not fire on schedule |
| Manual trigger | Force-run a job outside its schedule via API/CLI |
| Attempt deadline | Timeout for the HTTP target to respond before retrying |

### Target Types

**HTTP/HTTPS target:**
- POST to any HTTPS endpoint (Cloud Run, GKE Ingress, external services)
- Supports OIDC or OAuth2 tokens for authenticated targets (Cloud Run, Cloud Functions)
- Request body, headers, and HTTP method configurable
- Timeout (attempt deadline): 1 second to 30 minutes

**Pub/Sub target:**
- Publish a message to a Pub/Sub topic
- Configure message body and attributes
- No authentication config needed (uses project service account)

**App Engine HTTP target:**
- POST to an App Engine service/version handler
- Legacy; prefer HTTP target for new jobs

### Schedule Format (unix-cron)

```
# Format: minute hour day-of-month month day-of-week
# ┌───────── minute (0-59)
# │ ┌───────── hour (0-23)
# │ │ ┌───────── day of month (1-31)
# │ │ │ ┌───────── month (1-12 or JAN-DEC)
# │ │ │ │ ┌───────── day of week (0-6 or SUN-SAT; 0 = Sunday)
# │ │ │ │ │
  * * * * *

# Examples:
0 8 * * *       # Daily at 8:00 AM
0 */4 * * *     # Every 4 hours
0 0 1 * *       # First day of every month at midnight
0 9 * * MON-FRI # Weekdays at 9 AM
*/15 * * * *    # Every 15 minutes
0 2 * * SUN     # Sundays at 2 AM
```

**Important**: Cloud Scheduler does not support second-granularity. For sub-minute scheduling, use Cloud Tasks.

### Retry Configuration

- `maxRetryCount`: 0–5 (default: 0 = no retry)
- `minBackoffDuration`: minimum wait between retries (default: 5s)
- `maxBackoffDuration`: maximum wait between retries (default: 1h)
- `maxDoublings`: number of times to double the backoff (default: 5)

### Authentication for HTTP Targets

**OIDC (OpenID Connect):**
- Used for Cloud Run, Cloud Functions, internal Google services
- Cloud Scheduler generates an OIDC token signed by a service account
- Target must validate the token (Cloud Run does this automatically)
- Configure: service account email + audience (target URL)

**OAuth2:**
- Used for Google APIs (Admin SDK, BigQuery, etc.)
- Generates an access token with specified scope
- Less common; prefer OIDC for custom targets

### Common Use Cases

- Nightly BigQuery scheduled queries (alternatives: BigQuery scheduled queries)
- Daily report generation and email delivery
- Hourly data synchronization from external APIs
- Weekly cleanup jobs (delete old GCS objects, expire sessions)
- Periodic health checks and cache warming
- Triggering Cloud Workflows or Dataflow jobs on schedule
- Invoking Cloud Run jobs (batch processing) on schedule

---

## Cloud Tasks

### Purpose

Managed task queue for asynchronous, distributed background work. Decouple task creation (dispatch) from task execution (handler). Enable rate limiting, deduplication, retries, and scheduled future execution of HTTP tasks handled by Cloud Run, Cloud Functions, App Engine, or any HTTPS endpoint.

### Core Concepts

| Concept | Description |
|---|---|
| Queue | Named container for tasks; has rate limiting and retry settings |
| Task | Unit of work with a target, payload, and optional scheduling delay |
| HTTP task | Delivers HTTP request to Cloud Run, Cloud Functions, or any HTTPS target |
| App Engine task | Legacy; delivers to App Engine handler; configures service/version routing |
| Dispatch rate | Max tasks dispatched per second across the queue |
| Concurrency | Max concurrent task executions at a time |
| Deduplication | Tasks with the same name deduplicated for ~1 hour window |
| Retry | Configurable retry schedule (backoff, max attempts, max age) |
| Scheduled delivery | `scheduleTime` to deliver task at a future time (up to 30 days) |
| Task name | Optional; enables deduplication; format: `projects/p/locations/l/queues/q/tasks/my-task-id` |

### Queue Configuration

```yaml
# Queue settings
rateLimits:
  maxDispatchesPerSecond: 100.0   # max tasks dispatched per second
  maxBurstSize: 200               # max burst capacity
  maxConcurrentDispatches: 50     # max concurrent in-flight tasks
retryConfig:
  maxAttempts: 10                 # 0 = unlimited retries
  maxRetryDuration: 3600s         # maximum total retry window
  minBackoff: 0.1s                # minimum backoff between retries
  maxBackoff: 3600s               # maximum backoff between retries
  maxDoublings: 16                # times to double the backoff
```

### HTTP Task Details

```json
{
  "name": "projects/my-project/locations/us-central1/queues/my-queue/tasks/task-001",
  "scheduleTime": "2024-01-01T12:00:00Z",
  "httpRequest": {
    "httpMethod": "POST",
    "url": "https://my-service-abc123-uc.a.run.app/process",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": "eyJ1c2VyX2lkIjogMTIzfQ==",
    "oidcToken": {
      "serviceAccountEmail": "task-invoker@my-project.iam.gserviceaccount.com",
      "audience": "https://my-service-abc123-uc.a.run.app"
    }
  }
}
```

### Task Handler Requirements

The HTTP endpoint that handles tasks must:
1. Return HTTP 2xx to acknowledge successful processing (removes task from queue)
2. Return non-2xx to signal failure (task will be retried per retry config)
3. Be idempotent (task may be delivered more than once due to at-least-once delivery)
4. Respond within the dispatch deadline (default: 10 minutes for HTTP; 24 hours for App Engine)

### Delivery Guarantees

- **At-least-once delivery**: tasks may be executed more than once; handlers must be idempotent
- **Deduplication**: tasks with the same name are deduplicated for approximately 1 hour; after that, a task with the same name can be created again
- **Ordering**: tasks are generally delivered in FIFO order but not guaranteed

### Cloud Tasks vs Cloud Scheduler

| Dimension | Cloud Scheduler | Cloud Tasks |
|---|---|---|
| Trigger | Time-based (cron) | Programmatic (API/SDK) |
| Volume | Low (1 job per schedule) | High (millions of tasks) |
| Rate control | N/A (fires once per schedule) | Yes (max dispatches/second, concurrency) |
| Deduplication | N/A | Yes (by task name, ~1 hour) |
| Fan-out | No | Yes (create many tasks from one trigger) |
| Delay | No | Yes (scheduleTime up to 30 days) |
| Use case | Periodic batch jobs | Background work, fan-out, rate-limited API calls |

### Common Use Cases

- **Fan-out**: process a large set of records by creating one task per record (e.g., send 10,000 notification emails at controlled rate)
- **Rate-limited API calls**: queue API requests and dispatch at a rate that doesn't overwhelm external service
- **Retry-with-backoff**: tasks automatically retried with exponential backoff; no custom retry logic needed
- **Deferred work**: defer expensive operations from a web request handler to a background worker
- **Scheduled future execution**: schedule a task for delivery 5 minutes, 1 hour, or 7 days in the future
- **App Engine queue migration**: modernize legacy App Engine push/pull queues to Cloud Tasks HTTP queues

### App Engine Queue Migration

Legacy App Engine task queues (`queue.yaml`) map to Cloud Tasks:
- **Push queues** → Cloud Tasks HTTP queues targeting App Engine services
- **Pull queues** → Cloud Tasks pull (deprecated in Cloud Tasks; consider Pub/Sub for new designs)
- Migrate by creating Cloud Tasks queues and updating task creation code to use Cloud Tasks client library

---

## Comparison Summary

| Feature | Cloud Scheduler | Cloud Tasks |
|---|---|---|
| Max tasks/jobs | Limited (designed for few jobs) | Millions of tasks |
| Task creation | Automatic (time-based) | Programmatic |
| Task payload | Fixed per job | Per-task payload |
| Task deduplication | N/A | Yes |
| Concurrency control | N/A | Yes |
| Future scheduling | Up to 1 year | Up to 30 days |
| Best for | Cron replacement | Background workers, fan-out |
