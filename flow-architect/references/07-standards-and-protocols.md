# Standards and Protocols

Reference for the CloudEvents specification, AsyncAPI specification, CNCF serverless landscape, schema registries (Avro, Protobuf, JSON Schema), and event versioning strategies.

---

## CloudEvents Specification

### What Is CloudEvents?
CloudEvents is a CNCF (Cloud Native Computing Foundation) specification for describing event data in a common format. It standardizes the **envelope** of an event — the metadata that describes what the event is — while remaining agnostic about the payload format.

**Why CloudEvents?**
Without a standard, every event producer uses different metadata conventions:
- AWS uses `eventSource`, `eventName`, `eventTime`
- Azure uses `eventType`, `subject`, `eventTime`
- Google uses `type`, `source`, `timestamp`

CloudEvents creates interoperability: a consumer can parse any CloudEvents-compliant event without knowing the producer.

**CloudEvents is adopted by**: AWS EventBridge, Azure Event Grid, Google Cloud Eventarc, Knative Eventing, Dapr, NATS, Keptn, and many others.

### Required CloudEvents Attributes

| Attribute | Type | Description |
|---|---|---|
| `specversion` | String | CloudEvents spec version (currently "1.0") |
| `id` | String | Unique ID for this event (UUID recommended) |
| `source` | URI-Reference | Identifies the event producer/context |
| `type` | String | Event type (reverse-DNS namespaced) |

### Optional CloudEvents Attributes

| Attribute | Type | Description |
|---|---|---|
| `time` | Timestamp | When the event occurred (RFC 3339) |
| `datacontenttype` | String | Content type of the `data` field |
| `dataschema` | URI | Schema reference for the data |
| `subject` | String | Subject/entity the event is about |
| `data` | * | The event payload |
| `data_base64` | String | Base64-encoded binary data |

### CloudEvents JSON Example
```json
{
  "specversion": "1.0",
  "id": "7e5e03c4-9e5a-4a3b-a4a7-0f2d3e8e9f1c",
  "source": "https://orders.acme.com/api/v1/orders",
  "type": "com.acme.orders.order.placed",
  "subject": "orders/ord-12345",
  "time": "2024-01-15T14:23:01.123Z",
  "datacontenttype": "application/json",
  "dataschema": "https://schemas.acme.com/orders/v1/order-placed.json",
  "data": {
    "orderId": "ord-12345",
    "customerId": "cust-789",
    "items": [
      {"sku": "SKU-001", "quantity": 2, "price": 29.99}
    ],
    "totalAmount": 59.98,
    "currency": "USD"
  }
}
```

### CloudEvents Format Bindings
CloudEvents can be serialized in different formats:

**Structured Content Mode** (full CloudEvents envelope in the message body):
```http
POST /events HTTP/1.1
Content-Type: application/cloudevents+json

{
  "specversion": "1.0",
  "type": "com.acme.orders.order.placed",
  ...entire CloudEvent including data...
}
```

**Binary Content Mode** (attributes as headers, data as body — lower overhead):
```http
POST /events HTTP/1.1
Content-Type: application/json
ce-specversion: 1.0
ce-id: 7e5e03c4
ce-source: https://orders.acme.com
ce-type: com.acme.orders.order.placed
ce-time: 2024-01-15T14:23:01.123Z

{"orderId": "ord-12345", ...}
```

### CloudEvents Extensions
Custom attributes can be added using extension points:
```json
{
  "specversion": "1.0",
  "type": "com.acme.orders.order.placed",
  "id": "...",
  "source": "...",
  "partitionkey": "cust-789",    // Custom extension: Kafka partition key
  "traceparent": "00-4bf92f...", // W3C Trace Context extension
  "sequence": "42",              // Sequence number extension
  "correlationid": "saga-001"    // Custom correlation ID
}
```

**Registered CNCF Extensions**:
- `partitionkey`: Key for partitioned event logs
- `traceparent`, `tracestate`: W3C Distributed Tracing
- `sequence`, `sequencetype`: Event ordering
- `dataref`: Claim-check pattern (reference to large payload stored externally)

---

## AsyncAPI Specification

### What Is AsyncAPI?
AsyncAPI is an open specification for describing event-driven and asynchronous APIs. It is to event-driven systems what OpenAPI (Swagger) is to REST APIs.

**AsyncAPI enables**:
- Machine-readable API documentation for event-driven systems
- Code generation (consumers, producers, models)
- Documentation portals (like Swagger UI, but for event APIs)
- Contract-first development
- API governance and discovery

**AsyncAPI is adopted by**: Slack, SAP, Salesforce, IBM, Mulesoft, and many others.

### AsyncAPI Document Structure
```yaml
asyncapi: '2.6.0'

info:
  title: Order Management Events API
  version: '2.0.0'
  description: |
    Event streams produced by the Order Management domain.
    Consumers should use the CloudEvents format for all event envelopes.
  contact:
    name: Order Platform Team
    email: orders-platform@acme.com

servers:
  production:
    url: kafka.acme.com:9092
    protocol: kafka
    description: Production Kafka cluster
  staging:
    url: kafka-staging.acme.com:9092
    protocol: kafka

channels:
  orders.placed:
    description: Published when a customer places a new order
    bindings:
      kafka:
        topic: orders-placed-v2
        partitions: 12
        replicas: 3
    subscribe:
      operationId: receiveOrderPlaced
      summary: Receive new order placements
      message:
        $ref: '#/components/messages/OrderPlaced'

  orders.cancelled:
    description: Published when an order is cancelled
    subscribe:
      operationId: receiveOrderCancelled
      message:
        $ref: '#/components/messages/OrderCancelled'

components:
  messages:
    OrderPlaced:
      name: OrderPlaced
      title: Order Placed Event
      contentType: application/json
      headers:
        type: object
        properties:
          ce-specversion:
            type: string
            const: '1.0'
          ce-type:
            type: string
            const: 'com.acme.orders.order.placed'
      payload:
        $ref: '#/components/schemas/OrderPlacedPayload'
      examples:
        - name: StandardOrder
          payload:
            orderId: ord-12345
            customerId: cust-789
            items:
              - sku: SKU-001
                quantity: 2
                price: 29.99
            totalAmount: 59.98
            currency: USD
            placedAt: '2024-01-15T14:23:01.123Z'

  schemas:
    OrderPlacedPayload:
      type: object
      required: [orderId, customerId, items, totalAmount, currency, placedAt]
      properties:
        orderId:
          type: string
          format: uuid
        customerId:
          type: string
        items:
          type: array
          minItems: 1
          items:
            $ref: '#/components/schemas/OrderItem'
        totalAmount:
          type: number
          minimum: 0
        currency:
          type: string
          pattern: '^[A-Z]{3}$'
        placedAt:
          type: string
          format: date-time
```

### AsyncAPI Tooling
- **AsyncAPI Studio**: Browser-based editor with live preview
- **AsyncAPI Generator**: Generates code (Python, Java, Node.js, Go) from AsyncAPI docs
- **AsyncAPI Validator**: CI/CD linting and validation
- **Microcks**: API mocking from AsyncAPI specs

---

## CNCF Serverless Landscape

### CNCF and Flow Standards
The Cloud Native Computing Foundation hosts several projects relevant to flow:

| Project | Role in Flow |
|---|---|
| **CloudEvents** | Event envelope standard |
| **Knative Eventing** | Kubernetes-native event routing and delivery |
| **KEDA** | Kubernetes event-driven autoscaling |
| **Dapr** | Event-driven microservice building blocks |
| **OpenTelemetry** | Observability (traces, metrics, logs) for flow systems |
| **Strimzi** | Kubernetes operator for Apache Kafka |
| **NATS** | High-performance messaging and event streaming |
| **Argo Events** | Kubernetes event-driven workflow triggers |

### Knative Eventing
Knative Eventing provides a Kubernetes-native event broker and trigger mechanism:

```yaml
# EventBroker: receives and routes events
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: default
  namespace: orders

---
# Trigger: route matching events to a subscriber
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: order-to-shipment
spec:
  broker: default
  filter:
    attributes:
      type: com.acme.orders.order.placed   # Only OrderPlaced events
  subscriber:
    ref:
      apiVersion: v1
      kind: Service
      name: shipment-service
```

---

## Schema Registries

### Why Schema Registries?
In event-driven systems, schemas need to be:
- Centrally stored and versioned
- Validated before events are published
- Accessible by consumers at runtime without out-of-band schema sharing
- Managed for compatibility (backward, forward, full compatibility)

### Confluent Schema Registry
The most widely used schema registry for Kafka ecosystems. Supports Avro, Protobuf, and JSON Schema.

**How it works**:
```
Producer → Schema Registry (register/retrieve schema by ID) → Kafka
Consumer ← Schema Registry (retrieve schema by ID embedded in message) ← Kafka
```

**Wire format**:
```
Message bytes: [0x00] [4-byte schema ID] [serialized event data]
               Magic   Schema Registry    Avro/Protobuf/JSON
               byte    schema ID          payload
```

**REST API**:
```bash
# Register a schema
curl -X POST http://schema-registry:8081/subjects/orders-placed-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{\"type\": \"record\", \"name\": \"OrderPlaced\", ...}"}'

# Get schema by ID
curl http://schema-registry:8081/schemas/ids/1

# List all versions for a subject
curl http://schema-registry:8081/subjects/orders-placed-value/versions

# Check compatibility before registering
curl -X POST http://schema-registry:8081/compatibility/subjects/orders-placed-value/versions/latest \
  -d '{"schema": "..."}'
```

**Compatibility Modes**:
| Mode | Meaning | Safe Changes |
|---|---|---|
| BACKWARD | New schema can read old data | Delete optional fields, add optional fields |
| FORWARD | Old schema can read new data | Add optional fields, delete optional fields |
| FULL | Both backward and forward | Add optional fields only |
| NONE | No compatibility checking | Any change |

### Apache Avro
Avro is a compact binary serialization format with schema embedded in the registry (not in each message):

```json
{
  "type": "record",
  "name": "OrderPlaced",
  "namespace": "com.acme.orders",
  "doc": "Emitted when a customer places a new order",
  "fields": [
    {
      "name": "orderId",
      "type": "string",
      "doc": "Unique order identifier (UUID)"
    },
    {
      "name": "customerId",
      "type": "string"
    },
    {
      "name": "totalAmount",
      "type": "double"
    },
    {
      "name": "currency",
      "type": "string",
      "default": "USD"
    },
    {
      "name": "placedAt",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "promoCode",
      "type": ["null", "string"],   // Nullable optional field
      "default": null
    }
  ]
}
```

**Avro Strengths**:
- Compact binary format (no field names in messages — schema handles that)
- Dynamic typing support (schema can evolve without recompilation)
- Schema evolution with defaults for added fields
- Native support in Kafka ecosystem

### Protocol Buffers (Protobuf)
Google's language-neutral, platform-neutral serialization format:

```protobuf
syntax = "proto3";
package com.acme.orders;

message OrderPlaced {
  string order_id = 1;
  string customer_id = 2;
  repeated OrderItem items = 3;
  double total_amount = 4;
  string currency = 5;
  google.protobuf.Timestamp placed_at = 6;
  optional string promo_code = 7;   // optional in proto3
}

message OrderItem {
  string sku = 1;
  int32 quantity = 2;
  double price = 3;
}
```

**Protobuf Strengths**:
- Strong typing with code generation (Java, Python, Go, C++, etc.)
- Smaller payload than Avro for small messages (field tag numbers are compact)
- gRPC native format — useful if you're mixing streaming and RPC
- Excellent tooling ecosystem

**Avro vs. Protobuf for Kafka**:
| Dimension | Avro | Protobuf |
|---|---|---|
| Kafka ecosystem maturity | Higher (Confluent native) | Growing (Confluent supports) |
| Code generation | Optional | Required for typed access |
| Schema evolution | Simple (defaults) | Requires field numbering discipline |
| Message size | Small (schema-less wire) | Small (tag-number encoding) |
| Human readability | JSON-based schema | Proto file format |
| Best for | Data engineering, Kafka-native teams | Multi-language with gRPC |

### JSON Schema
Schema validation using JSON Schema (Draft-07 or newer):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.acme.com/orders/v1/order-placed.json",
  "title": "OrderPlaced",
  "type": "object",
  "required": ["orderId", "customerId", "items", "totalAmount", "placedAt"],
  "properties": {
    "orderId": {
      "type": "string",
      "format": "uuid"
    },
    "customerId": {
      "type": "string",
      "minLength": 1
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/definitions/OrderItem"
      }
    },
    "totalAmount": {
      "type": "number",
      "minimum": 0,
      "exclusiveMinimum": true
    },
    "currency": {
      "type": "string",
      "pattern": "^[A-Z]{3}$",
      "default": "USD"
    },
    "placedAt": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

**JSON Schema trade-offs**:
- No binary encoding — larger messages than Avro/Protobuf
- Human-readable and easy to share (just JSON)
- Best for REST/webhook events where JSON is already the format
- Validation tooling is ubiquitous

---

## Event Versioning Strategies

### Semantic Versioning for Events
Apply semantic versioning to event schemas:
- **Patch** (1.0.0 → 1.0.1): Documentation or description changes only
- **Minor** (1.0.0 → 1.1.0): Backward-compatible additions (new optional fields)
- **Major** (1.0.0 → 2.0.0): Breaking changes (removed fields, type changes, semantic changes)

### Topic/Channel Versioning
For breaking schema changes, create a new topic version:
```
orders-placed-v1   (deprecated, consumers migrating off)
orders-placed-v2   (current)
orders-placed-v3   (new, currently migrating consumers to this)
```

**Migration process**:
1. Deploy v2 producer alongside v1 (dual-publish to both topics)
2. Migrate consumers one by one to v2
3. Once all consumers on v2, stop publishing to v1
4. Decommission v1 topic after retention window

### Schema Negotiation
Some systems support runtime schema negotiation where consumers declare which schema version they support:
```
Consumer headers:
  Accept-Schema-Version: 1, 2   // I can handle v1 or v2
  Preferred-Schema-Version: 2   // I prefer v2

Producer behavior:
  If consumer prefers v2 and can support it → send v2
  If consumer only supports v1 → send v1 (downgrade)
```

This requires per-consumer routing or content negotiation in the broker — complex to implement but enables zero-downtime schema migrations.
