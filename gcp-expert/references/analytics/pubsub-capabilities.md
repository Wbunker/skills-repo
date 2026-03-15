# Pub/Sub — Capabilities

## Purpose

Global, durable, asynchronous messaging service for event streaming and system decoupling. Pub/Sub delivers messages from producers (publishers) to consumers (subscribers) reliably, at scale, and with low latency across regions. Designed for IoT telemetry, application integration, streaming analytics pipelines, and fan-out notification systems.

---

## Core Concepts

| Concept | Description |
|---|---|
| Topic | Named resource where publishers send messages; global |
| Subscription | Named resource attached to a topic; defines how messages are delivered to a subscriber |
| Message | Unit of data; body (bytes) + attributes (key-value string map) + message ID + publish timestamp |
| Message ID | Unique ID assigned by Pub/Sub on publish; used for deduplication |
| Ordering key | Optional string on a message; messages with same key delivered in order to a single subscriber |
| Acknowledge ID (ackId) | Token returned with each delivered message; used to acknowledge receipt |
| Ack deadline | Time subscriber has to ack before message is redelivered (10s–600s; default 10s) |
| Dead letter topic | Topic where messages are forwarded after max delivery attempts |
| Snapshot | Point-in-time capture of subscription state; used to replay messages |
| Message retention | How long topic retains undelivered messages (default 7 days; configurable 10 min–7 days) |
| Schema | Avro or Protocol Buffer schema enforced on message bodies |
| Filter | Server-side expression filtering messages on attributes before delivery |

---

## Subscription Types

| Type | Delivery Method | Best For |
|---|---|---|
| **Pull** | Subscriber calls `subscriptions.pull` API; receives batch of messages (up to 1000) | High-throughput consumers, controlled processing rate |
| **Push** | Pub/Sub delivers via HTTPS POST to subscriber endpoint | Serverless consumers (Cloud Run, Cloud Functions, App Engine) |
| **BigQuery** | Pub/Sub writes messages directly to a BigQuery table | Streaming to BigQuery without custom pipeline code |
| **Cloud Storage** | Pub/Sub batches and writes messages to GCS files | Archival, batch processing, data lake ingestion |

### Pull Subscription Details
- Synchronous pull: `subscriptions.pull` returns immediately; up to 1000 messages per call
- Streaming pull (gRPC): bidirectional stream; lower latency; preferred for high-throughput consumers
- Subscriber must ack messages within the ack deadline; otherwise redelivered
- `modifyAckDeadline` to extend deadline during long processing

### Push Subscription Details
- Pub/Sub POSTs to configured HTTPS URL with `{message, subscription}` JSON body
- Endpoint must return HTTP 200/201/204 to acknowledge; any other response = retry
- Supports OIDC token for authenticating to Cloud Run / Cloud Functions
- Configured with max outstanding messages and backoff for flow control

### BigQuery Subscription
- Schema must match BigQuery table schema (or use `write_metadata=true` for message attributes)
- Messages written as-is (Avro/JSON/protobuf based on topic schema) or raw bytes
- No Dataflow pipeline needed for simple streaming insert patterns

### Cloud Storage Subscription
- Messages batched and written to GCS objects
- Configure: bucket, filename prefix/suffix, max duration, max bytes per batch
- Useful for archiving message streams, feeding data lake pipelines

---

## Delivery Guarantees

| Guarantee | Default | Notes |
|---|---|---|
| At-least-once | Yes | Standard delivery; duplicate messages possible |
| Exactly-once | Optional (extra cost) | Available for pull subscriptions; subscriber acks are idempotent within the exactly-once window |
| Ordered delivery | Per ordering key | Enable message ordering on subscription; same-key messages delivered in publish order |

**Important**: at-least-once means consumers should be idempotent or implement deduplication. Exactly-once delivery uses server-side deduplication keyed on publisher-assigned message IDs.

---

## Message Ordering

- Enable with `enable_message_ordering=true` on the subscription
- Publisher sets `ordering_key` on messages
- Messages with the same key are delivered in published order to a single subscriber client
- **Regional requirement**: publisher and subscription in same region for ordering guarantees (or use regional endpoints)
- Order is maintained per key; different keys may be interleaved

---

## Schema Registry

- Define Avro or Protocol Buffer schemas for topics
- Messages published to the topic are validated against the schema
- Schema evolution: add new schema revisions; control which revisions are accepted
- Benefits: data quality enforcement, backward/forward compatibility checking

```bash
# Create Avro schema
gcloud pubsub schemas create my-event-schema \
  --type=AVRO \
  --definition-file=event-schema.avsc

# Create topic with schema
gcloud pubsub topics create my-topic \
  --schema=my-event-schema \
  --message-encoding=JSON

# Validate a message against the schema
gcloud pubsub schemas validate-message \
  --message-encoding=JSON \
  --schema=my-event-schema \
  --message='{"user_id": 123, "event_type": "click"}'
```

---

## Pub/Sub Lite

Pub/Sub Lite is a separate, lower-cost product for high-volume, cost-sensitive workloads:

| Feature | Pub/Sub | Pub/Sub Lite |
|---|---|---|
| Pricing | Per message/storage | Explicit provisioned throughput + storage capacity |
| Availability | Global (multi-region) | Zonal (single-zone) or Regional |
| Throughput limits | Auto-scaling | User-provisioned MiB/s |
| Storage | Serverless | User-provisioned GiB |
| Ordering | Per-key, optional | Per-partition, always |
| Replay | Via snapshots | Via seek to offset or timestamp |

**When to use Pub/Sub Lite**: IoT data ingestion at high volume where per-message pricing would be expensive; predictable workloads with known throughput.

---

## Dead Letter Topics

- Configure on a subscription: `--dead-letter-topic` + `--max-delivery-attempts` (5–100)
- Messages exceeding max delivery attempts are forwarded to the dead letter topic
- Add message attributes: `CloudPubSubDeadLetterSourceDeliveryCount`, `CloudPubSubDeadLetterSourceSubscription`, etc.
- Pub/Sub service account needs `pubsub.publisher` on DLT and `pubsub.subscriber` on source subscription

---

## Message Filtering

- Server-side filtering on message attributes before message is delivered to subscription
- Filter expression language: attribute exists (`hasPrefix`, `hasValue`), string comparisons, logical operators
- Reduces delivered messages (and subscriber processing load) without requiring subscriber-side filtering

```
# Example filter: only deliver messages with attribute type=order
gcloud pubsub subscriptions create filtered-sub \
  --topic=my-topic \
  --message-filter='attributes.type = "order"'
```

---

## Retention and Replay

- **Topic retention**: messages retained on topic for 10 minutes to 7 days (configurable)
- **Snapshots**: capture subscription cursor at a point in time; seek subscription to snapshot to replay messages
- **Seek by timestamp**: seek subscription to specific timestamp; replay messages from that point
- **Use cases**: replay after consumer bug, catch up after downtime, backfill new subscriber

---

## Typical Patterns

**IoT telemetry ingestion:**
```
IoT Device → Pub/Sub Topic → Dataflow (windowed aggregation) → BigQuery
                           → Cloud Storage Subscription (raw archival)
```

**Fan-out (1 publisher → many consumers):**
```
Payment Service → Pub/Sub Topic → Subscription A (fraud detection)
                               → Subscription B (ledger update)
                               → Subscription C (notification service)
```

**Application decoupling:**
```
Web App → Pub/Sub → Background Worker (Cloud Run / Cloud Functions)
```

**CDC via Datastream:**
```
Database → Datastream → Pub/Sub → Dataflow → BigQuery
```

---

## Monitoring

- Key metrics: `subscription/num_undelivered_messages` (backlog), `subscription/oldest_unacked_message_age`, `topic/send_message_operation_count`, `subscription/pull_request_count`
- Cloud Monitoring dashboards for Pub/Sub available pre-built
- Alert on `oldest_unacked_message_age` to detect stuck consumers
- Alert on `num_undelivered_messages` backlog growth for capacity planning
