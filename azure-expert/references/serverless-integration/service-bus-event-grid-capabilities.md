# Azure Service Bus & Event Grid — Capabilities Reference
For CLI commands, see [service-bus-event-grid-cli.md](service-bus-event-grid-cli.md).

---

## Azure Service Bus

**Purpose**: Enterprise-grade cloud messaging service for reliable, ordered, transactional asynchronous communication between distributed applications and services.

### Service Bus Tiers

| Feature | Standard | Premium |
|---|---|---|
| **Infrastructure** | Shared multi-tenant | Dedicated single-tenant |
| **Message size** | Up to 256 KB | Up to 100 MB |
| **Throughput** | Variable (shared) | Predictable, high throughput |
| **VNet integration** | Not supported | Private endpoints, VNet service endpoints |
| **Geo-Disaster Recovery** | Not supported | Supported (namespace pairing) |
| **Zone redundancy** | Not supported | Supported |
| **BYOK (customer-managed keys)** | Not supported | Supported |
| **JMS 2.0** | Not supported | Supported |
| **Pricing** | Pay per operation | Per messaging unit (dedicated) |

---

### Queues

Point-to-point messaging: one sender, one receiver. Each message processed by exactly one consumer.

| Feature | Description |
|---|---|
| **FIFO (Sessions)** | Enable sessions for ordered processing; session ID groups related messages; only one consumer processes a session at a time |
| **At-least-once delivery** | Default guarantee; message re-delivered if not settled within lock duration |
| **At-most-once delivery** | Enable `ReceiveAndDelete` mode; message deleted on receive (no lock, no redelivery) |
| **Message lock** | `lockDuration` (default 60s, max 5 min); consumer must complete/abandon/defer before lock expires |
| **Dead-letter queue (DLQ)** | Sub-queue automatically receiving messages exceeding max delivery count or explicitly dead-lettered |
| **Max delivery count** | Default 10; message moved to DLQ after exceeding count |
| **Auto-forward** | Automatically forward messages from queue/subscription to another queue or topic |
| **Dead-letter forwarding** | Forward DLQ messages to another entity for centralized error handling |
| **Message deferral** | Consumer defers a message (sets aside without abandoning); retrieved later by sequence number |
| **Scheduled messages** | Enqueue at current time but specify `ScheduledEnqueueTimeUtc` for future delivery |
| **Duplicate detection** | Deduplicate messages within a configurable window (10 seconds to 7 days) using `MessageId` |
| **Transactions** | Atomic multi-operation transactions (send/complete/defer across multiple messages/entities) |
| **Message TTL** | `TimeToLive` per message or queue-level default; expired messages go to DLQ |

---

### Topics & Subscriptions

Publish-subscribe messaging: one sender, multiple independent receivers via subscriptions.

| Feature | Description |
|---|---|
| **Topics** | Logical endpoint where publishers send messages; topic has one or more subscriptions |
| **Subscriptions** | Named receiver on a topic; each subscription gets a copy of every message matching its filter |
| **Max subscriptions** | Up to 2,000 subscriptions per topic |
| **Fan-out** | Every subscriber receives a copy — ideal for broadcasting events to multiple consumers |
| **Subscription filters** | Control which messages each subscription receives |
| **Filter types** | See table below |

### Subscription Filter Types

| Filter Type | Description | Example |
|---|---|---|
| **True filter** (default) | All messages received by subscription | Default when no filter specified |
| **False filter** | No messages received (subscription disabled effectively) | Useful to temporarily pause subscription |
| **Correlation filter** | Match on standard properties: `CorrelationId`, `ContentType`, `Label`, `MessageId`, `To`, `ReplyTo`, user properties | `CorrelationId = 'order-123'` |
| **SQL filter** | SQL-92 WHERE clause expression evaluated against message properties (not body) | `Region = 'EMEA' AND OrderType = 'B2B'` |

### Sessions

- Enable sessions by setting `requiresSession: true` on queue or subscription
- Group related messages by `SessionId` (e.g., all messages for a given order, customer, or conversation)
- Exactly one active session receiver at a time per session ID — guarantees FIFO ordering within session
- Session state: store and retrieve arbitrary state blob associated with a session (useful for workflow state)
- Use cases: ordered processing, stateful workflows, conversation management

---

### Dead-Letter Queue (DLQ)

- Every queue and topic subscription has a corresponding DLQ: `{queue-name}/$DeadLetterQueue`
- Messages moved to DLQ when:
  - `MaxDeliveryCount` exceeded (default 10 failed deliveries)
  - Message TTL expired (if `DeadLetteringOnMessageExpiration` enabled)
  - Subscription filter evaluation error (if `DeadLetteringOnFilterEvaluationExceptions` enabled)
  - Application explicitly calls `DeadLetter()` on the message
- DLQ messages retain original properties plus `DeadLetterReason` and `DeadLetterErrorDescription`
- Inspect DLQ with Service Bus Explorer, Azure portal, or SDK; resubmit after fixing root cause

---

### Message Protocols

| Protocol | Description |
|---|---|
| **AMQP 1.0** | Primary protocol; efficient binary protocol; supported by all tiers |
| **HTTPS/REST** | Available for send/receive; less efficient than AMQP |
| **JMS 2.0** | Java Message Service 2.0 API; Premium tier only; enables Spring, Quarkus, Jakarta EE apps |

---

### Service Bus vs Event Hubs vs Storage Queue

| Scenario | Recommended Service |
|---|---|
| Ordered, transactional enterprise messaging; FIFO; sessions | **Service Bus** |
| High-throughput streaming (millions/sec); telemetry; logs; Kafka | **Event Hubs** |
| Simple decoupled queue, large volume, cost-sensitive, 7-day retention | **Storage Queue** |
| Broad event routing (one event, react now); Azure resource events | **Event Grid** |

---

## Azure Event Grid

**Purpose**: Fully managed event routing service that enables reactive, event-driven architectures by connecting event publishers to subscribers via a declarative subscription model.

---

### Core Concepts

| Concept | Description |
|---|---|
| **Event** | Smallest unit of information describing something that happened; max 1 MB per event (batched) |
| **Publisher** | Service or app that sends events to Event Grid |
| **Topic** | Endpoint where publishers send events; subscribers create event subscriptions on topics |
| **Event subscription** | Declaration of which events from a topic a subscriber wants to receive, and where to deliver them |
| **Event handler** | Destination that receives and processes events |
| **Domain** | Management construct grouping thousands of related topics for multi-tenant solutions |

---

### Topic Types

| Type | Description | Examples |
|---|---|---|
| **System topics** | Built-in topics for Azure services; auto-created when you subscribe to service events | Azure Blob Storage (create/delete), Azure Resource Manager (resource create/update/delete), Azure Container Registry, IoT Hub, Service Bus, Event Hubs, Azure Maps |
| **Custom topics** | User-created topics for publishing application events | Your app order events, sensor readings, business events |
| **Partner topics** | Events from 3rd-party SaaS partners via Event Grid Partner Network | Salesforce, SAP, Auth0, Microsoft Graph API changes |

---

### Event Delivery (Push Model)

| Handler Type | Description |
|---|---|
| **Azure Functions** | Trigger function on event delivery; most common pattern |
| **Logic Apps** | HTTP trigger with Event Grid connector; visual workflows |
| **Event Hubs** | Fan-out to high-throughput streaming pipeline |
| **Service Bus queue/topic** | Fan-out to enterprise messaging |
| **Storage Queue** | Simple, durable delivery to Azure Storage Queue |
| **Webhook (HTTP endpoint)** | Deliver to any HTTP endpoint; requires endpoint validation handshake |
| **Azure Relay Hybrid Connections** | Deliver to on-premises listeners |

### Event Delivery (Pull Model)

- **Event Grid Namespaces** (newer resource type): consumers pull events on-demand using HTTP
- Enables decoupled consumption where consumers control their rate
- Supports MQTT protocol for IoT device telemetry (see MQTT Broker section)
- Pull model: `receiveEvents`, `acknowledgeEvents`, `rejectEvents`, `releaseEvents` API operations

---

### Event Subscriptions & Filtering

Filters control which events are delivered to a subscriber:

| Filter Type | Description |
|---|---|
| **Event type filter** | Include or exclude specific event types (e.g., only `Microsoft.Storage.BlobCreated`) |
| **Subject filter** | Filter by event subject using prefix or suffix match (e.g., subject begins with `/blobServices/default/containers/images/`) |
| **Advanced filter** | Up to 25 conditions on any event property or data field using operators: NumberGreaterThan, StringContains, BoolEquals, IsNullOrUndefined, etc. |

---

### Retry Policy & Dead-lettering

| Feature | Description |
|---|---|
| **Retry policy** | Exponential backoff; retries for up to 24 hours (default) or configurable max delivery attempts |
| **Retry schedule** | Immediate retry → 10s → 30s → 1min → 5min → 10min → 30min → 1hr → ... up to 24hr |
| **Dead-lettering** | Configure a Storage Blob destination for events that cannot be delivered after all retries |
| **Dead-letter triggers** | MaxDeliveryAttemptExceeded, EventExpirationReached |

---

### Event Grid vs Event Hubs vs Service Bus

| Scenario | Use |
|---|---|
| Discrete event routing — react to one thing happening | **Event Grid** |
| High-throughput streaming — telemetry, logs, millions/sec | **Event Hubs** |
| Ordered, transactional enterprise messaging — FIFO, sessions | **Service Bus** |
| Batch processing with consumer groups, replay | **Event Hubs** |
| Fan-out with filtering per subscriber | **Event Grid** (few subs) or **Service Bus Topics** (complex filtering) |

---

### Event Schema

**CloudEvents 1.0 (recommended for new workloads):**
```json
{
  "specversion": "1.0",
  "type": "com.contoso.order.created",
  "source": "/contoso/orders",
  "id": "A234-1234-1234",
  "time": "2024-01-15T17:31:00Z",
  "datacontenttype": "application/json",
  "data": {
    "orderId": "ORD-123",
    "customerId": "CUST-456",
    "amount": 99.99
  }
}
```

**Event Grid Schema (legacy):**
```json
{
  "id": "A234-1234-1234",
  "topic": "/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorage",
  "subject": "/blobServices/default/containers/images/blobs/photo.jpg",
  "eventType": "Microsoft.Storage.BlobCreated",
  "eventTime": "2024-01-15T17:31:00Z",
  "data": { ... },
  "dataVersion": "1.0"
}
```

---

### Event Grid Namespaces (MQTT Broker)

- Newer resource type providing MQTT broker capability (Event Grid Namespaces)
- Supports **MQTT 3.1.1 and MQTT 5.0** over TLS (port 8883)
- Use cases: IoT device telemetry, bidirectional command-and-control, device-to-cloud and cloud-to-device messaging
- Topic spaces: define patterns of MQTT topics (wildcard support)
- Publisher and subscriber clients authenticated via X.509 certificates or Microsoft Entra ID
- Routing rules: route MQTT messages to Event Grid topics, Event Hubs, or Service Bus for further processing

---

### Event Domains

- Group management for up to 100,000 event topics in a single Event Grid resource
- Use case: multi-tenant SaaS applications where each tenant has their own topic
- Publishers send to domain topic: `domain-endpoint/topics/{tenant-id}`
- Subscribers create subscriptions on specific domain topics
- Centralized access management and monitoring for all topics within a domain
