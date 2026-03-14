# Event Discovery and Federation

Reference for event catalogs, event mesh architecture, federated event grids, cross-domain event routing, event subscriptions, and the World-Wide Flow vision.

---

## The Discovery Problem

### Why Discovery Matters
In a mature event-driven organization, hundreds or thousands of event streams may exist across teams, domains, and systems. Without discovery infrastructure, organizations face:

- **Shadow integration**: Teams build direct API calls because they can't find the event stream
- **Duplicate streams**: Multiple teams create overlapping events because they don't know existing ones exist
- **Tribal knowledge**: Only the original team knows what events are available
- **Integration bottlenecks**: All new integrations require consulting the producing team directly
- **Dead events**: Streams that have no consumers but continue to be maintained

The event catalog solves the discovery problem by making the event landscape navigable.

---

## Event Catalogs

### What Is an Event Catalog?
An event catalog is a **searchable registry of available event streams**, their schemas, owners, consumers, and integration guides. It functions like an API portal, but for events.

An event catalog entry typically includes:
- Event type name and description
- Schema (with version history)
- Producer service and team ownership
- Topic/channel name and connection details
- SLA and reliability guarantees
- Sample events
- Known consumers
- Changelog and deprecation notices

### Catalog Implementation Approaches

**Tool-based Catalog (EventCatalog)**
EventCatalog (eventcatalog.dev) is an open-source static site generator for event documentation:

```yaml
# event-catalog/events/OrderPlaced/index.md
---
name: OrderPlaced
version: 2.0.0
summary: |
  Published when a customer successfully places an order.
  Triggered after cart validation, inventory reservation, and payment authorization.
producers:
  - Order Management Service
consumers:
  - Shipment Service
  - Notification Service
  - Loyalty Service
  - Analytics Platform
schema:
  $ref: schema.json
tags:
  - orders
  - commerce
owners:
  - order-platform-team@acme.com
badges:
  - content: Stable
    backgroundColor: green
---

# OrderPlaced

## Overview
The `OrderPlaced` event signals that a customer order has been successfully submitted...

## Schema Changes from v1 to v2
- Added `promoCode` field (optional)
- Added `loyaltyPointsEarned` field (optional)
- `items` now includes `discountAmount` per line item

## Consumer Guide
Subscribe to Kafka topic `orders-placed-v2`. Use consumer group name prefixed with your service name.
```

**Schema Registry as Catalog**
Confluent Schema Registry and Apicurio Registry provide catalog-like functionality:
- Schema versioning and search
- Compatibility checking
- REST API for tooling integration

However, they lack the human-readable documentation and consumer/producer relationship tracking of a dedicated catalog.

**Internal Developer Portal Integration**
Backstage (Spotify's open-source IDP) can serve as an event catalog through plugins:
```yaml
# catalog-info.yaml in event producer repository
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: order-events-api
  description: Event streams from the Order Management domain
  tags:
    - kafka
    - orders
spec:
  type: asyncapi
  lifecycle: production
  owner: order-platform-team
  definition:
    $text: ./asyncapi.yaml   # AsyncAPI spec
```

### Catalog Governance
- **Producer responsibility**: Producing teams own their event documentation
- **Review process**: New events reviewed for naming conventions, schema standards
- **Deprecation policy**: Events deprecated with minimum 6-month notice, communicated through catalog
- **Discovery SLA**: Catalog updated within 24 hours of new event deployment

---

## Event Mesh Architecture

### What Is an Event Mesh?
An event mesh is a **dynamically routable, interconnected network of event brokers** that enables any producer to reach any consumer, regardless of location (cloud region, data center, edge, SaaS).

Unlike a single centralized broker or streaming platform, an event mesh:
- Distributes event routing intelligence across nodes
- Routes events based on subscriptions (no need to configure explicit forwarding)
- Supports multiple protocols simultaneously (MQTT, AMQP, REST, Kafka)
- Provides geographic routing and failover

**Event Mesh Reference Architecture**:
```
┌──────────────────────────────────────────────────────────────────┐
│                         Event Mesh                               │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Broker     │◄──►│  Broker     │◄──►│  Broker     │         │
│  │  (AWS       │    │  (Azure     │    │  (On-prem   │         │
│  │   us-east)  │    │   West EU)  │    │   DC)       │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
    ┌─────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │ Order      │    │ Analytics   │    │ ERP System  │
    │ Service    │    │ Platform    │    │ (on-prem)   │
    │ (producer) │    │ (consumer)  │    │ (consumer)  │
    └────────────┘    └─────────────┘    └─────────────┘
```

### Event Mesh Products and Technologies

**Solace PubSub+**
Enterprise event mesh platform with:
- Hardware and software brokers
- Native MQTT, AMQP, JMS, REST, Kafka protocol support
- Dynamic message routing using hierarchical topics
- Built-in geographic routing and replication

**NATS**
High-performance, cloud-native messaging system designed for event mesh scenarios:
- Simple, text-based protocol (lighter weight than AMQP)
- JetStream persistence layer for durable event streaming
- Built-in cluster, gateway (inter-cluster), and leaf node (edge) support
- Extremely low latency (<1ms P99 within a region)

**NATS JetStream example**:
```go
// NATS JetStream: stream creation
js, _ := nc.JetStream()

js.AddStream(&nats.StreamConfig{
    Name:     "ORDERS",
    Subjects: []string{"orders.>"},      // All orders.* topics
    MaxAge:   7 * 24 * time.Hour,        // 7-day retention
    Replicas: 3,                          // 3-node replication
    Storage:  nats.FileStorage,
})

// Publish
js.Publish("orders.placed", eventBytes)

// Subscribe with durable consumer
js.Subscribe("orders.placed", handler,
    nats.Durable("shipment-service"),
    nats.AckExplicit(),
)
```

**HiveMQ**
Enterprise MQTT broker designed for IoT event mesh scenarios:
- Kubernetes-native deployment
- MQTT Sparkplug B support for industrial IoT
- Extension SDK for custom routing logic
- Cluster-aware with dynamic topic routing

### Event Mesh vs. Centralized Kafka

| Dimension | Event Mesh | Centralized Kafka |
|---|---|---|
| Geographic scope | Multi-region, global native | Requires MirrorMaker or Confluent replication |
| Protocol flexibility | Multi-protocol | Kafka protocol only |
| IoT/Edge support | Native (MQTT, constrained networks) | Via bridge |
| Latency | Very low (sub-ms same region) | Low (few ms) |
| Throughput | High | Very high (Kafka's strength) |
| Stream processing | Limited | Rich (Kafka Streams, Flink, ksqlDB) |
| Data replay | Limited | Excellent |
| Ecosystem | Smaller | Large (Kafka connectors, Schema Registry) |

---

## Federated Event Grids

### Concept: Federation
Federation allows **independent event domains** (different companies, business units, or cloud accounts) to share events without a central authority owning all infrastructure.

Like DNS federation (each domain manages its own zone, but queries route globally), a federated event grid allows:
- Each domain to own its event infrastructure
- Cross-domain subscriptions based on agreement and access control
- Decentralized governance with interoperability

### Federation Patterns

**Hub-and-Spoke Federation**
One central event hub federates multiple domain-owned spokes:
```
Domain A events → Hub → Domain B (subscribed topics)
Domain B events → Hub → Domain C (subscribed topics)
Domain C events → Hub → Domain A (subscribed topics)
```
- Simple routing
- Hub is a governance and operational bottleneck
- Suitable for intra-enterprise federation

**Peer-to-Peer Federation**
Domains establish bilateral event exchange agreements:
```
Domain A ↔ (agreed topics) ↔ Domain B
Domain B ↔ (agreed topics) ↔ Domain C
```
- No central hub
- Scales poorly as number of domains grows
- Good for partner ecosystem with limited participants

**Hierarchical Federation (The World-Wide Flow Vision)**
Inspired by how the internet routes IP packets — events route through hierarchical event grids:
```
Global Root Grid (internet-scale routing)
├── Regional Grid (continent/cloud-region level)
│   ├── Enterprise Grid (organization level)
│   │   ├── Domain Grid (business domain level)
│   │   │   └── Service-level brokers (individual producers/consumers)
```

### Cross-Domain Event Routing

**Event Subscriptions**
In federated grids, a consumer in Domain B expresses interest in events from Domain A using a subscription:

```yaml
# Cross-domain subscription
subscription:
  id: sub-order-events-from-retail
  consumer:
    domain: logistics.acme.com
    service: shipment-planning
  producer:
    domain: retail.partner.com
    eventTypes:
      - com.partner.retail.order.placed
      - com.partner.retail.order.cancelled
  filter:
    region: "US"
    orderValue:
      minimum: 100
  deliveryEndpoint:
    type: kafka
    topic: partner-order-events
    cluster: logistics-kafka.acme.com
  accessControl:
    authToken: "${PARTNER_API_KEY}"
```

**Protocol Translation at Federation Boundaries**
When domains use different protocols, federation gateways handle translation:
```
Partner (uses webhooks) → Federation Gateway → Internal Kafka
                          - Validates signature
                          - Transforms to CloudEvents format
                          - Publishes to internal topic

Internal Kafka → Federation Gateway → Partner (uses MQTT)
                 - Subscribes to topics
                 - Transforms event envelope
                 - Publishes via MQTT
```

---

## The World-Wide Flow Vision

### Urquhart's Vision
Urquhart posits that the internet is evolving from a **document web** (HTTP/REST) to a **flow web** — where events flow as naturally as web pages are served today. The World-Wide Flow is the infrastructure vision that makes this possible.

Key pillars of the World-Wide Flow:
1. **Standardized event format** (CloudEvents) — events are universally parseable
2. **Standardized event API** (AsyncAPI, WebSub) — anyone can discover and subscribe to event streams
3. **Federated event routing** — events route across organizational boundaries like DNS routes queries
4. **Decentralized access control** — producers grant subscription access; consumers manage their own access

### WebSub (W3C Standard)
WebSub (formerly PubSubHubbub) is a W3C-standardized protocol for web-scale pub/sub:
- Publishers notify a hub when content changes
- Subscribers register with the hub for push notifications
- Hub pushes updates to subscriber HTTP endpoints

```
Publisher → Hub (discovers via <link rel="hub"> in HTML/JSON)
Subscriber → Hub (subscribes with callback URL)
Publisher → Hub → Subscriber callback (event delivery)
```

WebSub enables decentralized internet-scale event distribution without a central broker.

### Cloud Provider Event Grids
Major cloud providers have implemented internet-facing event grids:

**Azure Event Grid**
- Natively routes events from Azure services (Storage, Cosmos DB, IoT Hub) to subscribers
- Supports custom events from any source
- EventGrid Domains allow multi-tenant event distribution
- Delivery to webhooks, Azure Functions, Event Hubs, Service Bus

```json
{
  "topic": "/subscriptions/.../resourceGroups/rg1/providers/Microsoft.EventGrid/topics/myTopic",
  "subject": "/orders/ord-12345",
  "eventType": "com.acme.orders.order.placed",
  "eventTime": "2024-01-15T14:23:01.123Z",
  "id": "7e5e03c4-9e5a-4a3b-a4a7-0f2d3e8e9f1c",
  "data": {"orderId": "ord-12345"},
  "dataVersion": "1.0"
}
```

**AWS EventBridge**
- Event bus service with rule-based routing
- EventBridge Pipes: point-to-point integration with filtering and transformation
- Schema Registry: auto-discovered schemas from events
- Partner event sources: SaaS partners (Salesforce, Zendesk, Datadog) publish directly to EventBridge

```json
// EventBridge rule: route order events to SQS for fulfillment
{
  "source": ["com.acme.orders"],
  "detail-type": ["OrderPlaced"],
  "detail": {
    "orderType": ["standard", "expedited"],
    "totalAmount": [{"numeric": [">=", 0]}]
  }
}
```

**Google Cloud Eventarc**
- Routes events from GCP services and custom sources
- Native CloudEvents format
- Targets: Cloud Run, Cloud Functions, GKE

---

## Event Subscription Management

### Subscription Lifecycle
```
CREATED → PENDING_VALIDATION → ACTIVE → SUSPENDED → TERMINATED
```

**Validation handshake** (WebSub/EventGrid pattern):
1. Consumer registers subscription with callback URL
2. Hub/Grid sends validation request to callback with challenge token
3. Consumer responds with the challenge token (proves they control the endpoint)
4. Subscription becomes ACTIVE

**Suspension conditions**:
- Consumer endpoint consistently returns errors (>X% failure rate)
- Consumer fails to acknowledge events within SLA
- Access token revoked or expired

### Subscription Filters
Most event grids support subscription-level filtering to reduce bandwidth:

```yaml
# EventGrid subscription filter
filter:
  includedEventTypes:
    - com.acme.orders.order.placed
    - com.acme.orders.order.shipped
  advancedFilters:
    - operatorType: StringContains
      key: data.region
      values: ["us-east", "us-west"]
    - operatorType: NumberGreaterThanOrEquals
      key: data.totalAmount
      value: 100
```

This filtering at the subscription level reduces:
- Consumer compute cost (no need to filter in-application)
- Network bandwidth (events not matching filter are not delivered)
- Consumer complexity (simpler event processing logic)
