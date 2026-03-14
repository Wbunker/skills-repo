# Event Brokers and Messaging

Reference for AMQP, MQTT, STOMP protocols, RabbitMQ vs. ActiveMQ, message queues vs. event logs, pub/sub patterns, fan-out, content-based routing, and dead letter queues.

---

## Messaging Protocols

### AMQP (Advanced Message Queuing Protocol)
AMQP 0-9-1 is the de facto standard protocol for enterprise message brokers. It defines a wire-level protocol and a model of exchanges, queues, and bindings.

**AMQP Model**
```
Producer → Exchange → Binding(s) → Queue(s) → Consumer(s)
```

**Components**:
- **Exchange**: Receives messages from producers and routes them to queues based on routing rules
- **Queue**: Durable or transient buffer holding messages until consumed
- **Binding**: A rule linking an exchange to a queue, with an optional routing key or arguments

**Exchange Types**:

| Exchange Type | Routing Logic | Use Case |
|---|---|---|
| Direct | Route by exact routing key match | Point-to-point, request-reply |
| Fanout | Route to all bound queues | Broadcast notifications |
| Topic | Route by pattern matching on routing key (`*` = one word, `#` = zero or more) | Flexible pub/sub |
| Headers | Route by message header values | Complex routing without changing routing key |

**Topic Exchange Example (RabbitMQ)**:
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare topic exchange
channel.exchange_declare(exchange='events', exchange_type='topic', durable=True)

# Publish with routing key: orders.us.placed
channel.basic_publish(
    exchange='events',
    routing_key='orders.us.placed',
    body=json.dumps(event_payload),
    properties=pika.BasicProperties(
        delivery_mode=2,     # Persistent (survives broker restart)
        content_type='application/json'
    )
)

# Consumer binding: receive all order events from US
channel.queue_bind(
    exchange='events',
    queue='us-order-processor',
    routing_key='orders.us.*'    # Matches orders.us.placed, orders.us.shipped, etc.
)

# Consumer binding: receive all events (for audit log)
channel.queue_bind(
    exchange='events',
    queue='audit-logger',
    routing_key='#'    # Matches everything
)
```

**AMQP 1.0** is a newer, incompatible standard supported by Azure Service Bus, ActiveMQ Artemis, and some enterprise brokers. It has a different model but similar purpose.

### MQTT (Message Queuing Telemetry Transport)
MQTT is a lightweight publish/subscribe protocol designed for constrained devices and low-bandwidth networks. Originally developed for satellite telemetry.

**Key Properties**:
- Minimal overhead: fixed 2-byte header; designed for 8-bit microcontrollers
- TCP/IP based; MQTT over WebSockets supported
- Topic-based routing with wildcard subscriptions
- Three QoS levels
- Persistent sessions for intermittently connected devices

**MQTT Topic Hierarchy** (uses `/` as separator, `+` and `#` as wildcards):
```
sensors/factory1/line3/temperature
sensors/factory1/line3/pressure
sensors/factory1/+/temperature    ← matches any sensor on factory1
sensors/#                         ← matches all sensor topics
```

**MQTT QoS Levels**:
| QoS | Guarantee | Description |
|---|---|---|
| 0 | At-most-once | Fire and forget; no acknowledgment |
| 1 | At-least-once | Broker acknowledges; possible duplicates |
| 2 | Exactly-once | Four-way handshake; no duplicates |

**Retained Messages**: A broker retains the last message on a topic. New subscribers receive the retained message immediately upon subscription — useful for "last known state" of sensors.

**Last Will and Testament (LWT)**: A message the broker publishes on a client's behalf if the client disconnects unexpectedly:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="sensor-001")

# LWT: if sensor disconnects ungracefully, publish this alert
client.will_set(
    topic="alerts/sensor-001/status",
    payload='{"status": "offline", "reason": "unexpected_disconnect"}',
    qos=1,
    retain=True
)
```

**MQTT Versions**:
- MQTT 3.1.1: Widely supported, most IoT devices
- MQTT 5.0: Adds user properties, request/reply pattern, message expiry, shared subscriptions

**MQTT in IoT Architecture**:
```
IoT Devices (MQTT) → MQTT Broker (HiveMQ, Mosquitto, EMQX)
                          ↓
                    MQTT-to-Kafka Bridge
                    (Kafka Connect MQTT Source)
                          ↓
                    Kafka (stream processing, analytics)
```

### STOMP (Simple Text Oriented Messaging Protocol)
STOMP is a text-based protocol (human-readable frames, like HTTP), supported by ActiveMQ, RabbitMQ (via plugin), and others.

**STOMP Frame**:
```
SEND
destination:/topic/orders
content-type:application/json

{"orderId": "123", "status": "placed"}
^@
```

Less efficient than AMQP or MQTT due to text encoding. Primary use: web browser clients via WebSocket (browsers can't use TCP-based binary protocols directly). Often replaced by MQTT over WebSocket in modern applications.

---

## RabbitMQ

### Architecture and Strengths
RabbitMQ is the most widely deployed AMQP 0-9-1 broker. Written in Erlang for high concurrency and fault tolerance.

**Strengths**:
- Rich routing: exchanges, bindings, routing keys enable complex message routing
- Management UI and REST API for operations
- Plugins ecosystem: shovel (cross-broker forwarding), federation, delayed message, MQTT, STOMP
- Reliable delivery with publisher confirms and consumer acknowledgments
- Priority queues, TTL on messages, TTL on queues

**Cluster Architecture**:
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  RabbitMQ   │  │  RabbitMQ   │  │  RabbitMQ   │
│   Node 1    │◄─►│   Node 2    │◄─►│   Node 3    │
│ (disk node) │  │ (disk node) │  │  (ram node) │
└─────────────┘  └─────────────┘  └─────────────┘
       ↑ Quorum Queues (Raft-based replication)
```

**Queue Types**:
- **Classic Queues**: Original RabbitMQ queues; mirroring deprecated in favor of quorum queues
- **Quorum Queues**: Raft-based replication across N nodes; recommended for production (RabbitMQ 3.8+)
- **Streams**: Append-only log with consumer position tracking — Kafka-like semantics within RabbitMQ (3.9+)

```python
# RabbitMQ Quorum Queue declaration (recommended for production)
channel.queue_declare(
    queue='orders',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',        # Raft-based replication
        'x-delivery-limit': 5,            # Max redelivery attempts
        'x-dead-letter-exchange': 'dlx'  # DLQ on max retries
    }
)
```

### RabbitMQ Best Practices
- Use quorum queues for all production workloads (replace classic mirrored queues)
- Enable publisher confirms for at-least-once delivery
- Set message TTL or queue TTL to prevent unbounded growth
- Configure dead letter exchanges for failed message handling
- Use prefetch count (`basic.qos`) to prevent consumer overload
- Monitor queue depth and consumer utilization via management API

---

## ActiveMQ and ActiveMQ Artemis

### ActiveMQ Classic
The original Apache ActiveMQ is one of the oldest open-source message brokers. Supports JMS, AMQP, STOMP, MQTT, OpenWire.

**Use cases**: Legacy Java enterprise applications using JMS API, Spring Integration workloads.

**Limitations**: Older codebase; performance lags behind Artemis and RabbitMQ for modern workloads.

### ActiveMQ Artemis
A complete rewrite of ActiveMQ with a higher-performance non-blocking I/O core:
- Native AMQP 1.0 support (also OpenWire, STOMP, MQTT, HornetQ)
- Journal-based persistence (fast sequential I/O)
- Unified address model: addresses (like exchanges) → queues with configurable routing types
- Used as the message broker embedded in Red Hat AMQ and other enterprise products

```xml
<!-- Artemis address configuration -->
<address name="orders">
  <multicast>  <!-- Topic/pub-sub semantics -->
    <queue name="shipment-service-subscription" />
    <queue name="analytics-subscription" />
  </multicast>
  <anycast>    <!-- Queue/competing consumers semantics -->
    <queue name="order-processor" />
  </anycast>
</address>
```

---

## Message Queues vs. Event Logs

This is one of the most important architectural distinctions in flow systems:

### Message Queue Semantics
| Property | Behavior |
|---|---|
| Message consumption | Message removed from queue after ACK |
| Consumer groups | One queue → one consumer group; fan-out requires multiple queues |
| Consumer failure | Unacknowledged message requeued for redelivery |
| Ordering | Best-effort (strict ordering requires exclusive consumer or single queue) |
| Replay | Not supported; once consumed, messages are gone |
| Consumer speed | Consumer must keep up or queue grows unboundedly |
| Best for | Task queues, work distribution, point-to-point messaging |

### Event Log Semantics (Kafka/Pulsar)
| Property | Behavior |
|---|---|
| Message consumption | Event remains in log after consumer reads it |
| Consumer groups | Multiple independent consumer groups, each reading all events |
| Consumer failure | Consumer restarts from last committed offset |
| Ordering | Guaranteed within partition/shard |
| Replay | Full replay from any offset within retention window |
| Consumer speed | Consumer can fall behind and catch up; backpressure via pause |
| Best for | Multi-consumer fan-out, event sourcing, stream processing, audit |

### Decision Framework

```
Can I lose a message if a consumer is unavailable?
└── No → Do I need multiple independent consumers?
    ├── No → Message Queue (RabbitMQ/SQS)
    └── Yes → Event Log (Kafka/Kinesis)

Do I need to replay events?
└── Yes → Event Log

Is this IoT / sensor data with constrained devices?
└── Yes → MQTT Broker → Event Log bridge

Am I processing work items (jobs) that should be distributed across workers?
└── Yes → Message Queue (competing consumers)

Am I distributing information to multiple interested parties?
└── Yes → Event Log or Pub/Sub (SNS/EventBridge for cloud)
```

---

## Pub/Sub Patterns

### Simple Pub/Sub
One producer, one or more consumers. All consumers receive all messages.
```
Topic: order-notifications
Producer: OrderService
Consumers:
  - EmailService (sends confirmation email)
  - SMSService (sends SMS if opted in)
  - LoyaltyService (awards points)
  - AnalyticsService (records for reporting)
```

### Fan-Out Pattern
One event produces multiple downstream events or triggers:
```
SNS Topic: order.placed
  → SQS Queue: order-fulfillment (fan-out to fulfillment)
  → SQS Queue: inventory-reservation (fan-out to inventory)
  → Lambda: real-time-dashboard (fan-out to dashboard update)
  → HTTP Endpoint: third-party-webhook (fan-out to partner)
```

AWS SNS + SQS fan-out is a classic cloud-native implementation:
```json
{
  "Type": "Subscription",
  "TopicArn": "arn:aws:sns:us-east-1:123456789:order-placed",
  "Protocol": "sqs",
  "Endpoint": "arn:aws:sqs:us-east-1:123456789:order-fulfillment-queue",
  "FilterPolicy": {
    "orderType": ["standard", "expedited"]   // Only non-express orders
  }
}
```

### Content-Based Routing
Route events to different consumers based on message content rather than just topic:

**RabbitMQ Headers Exchange**:
```python
channel.exchange_declare(exchange='events', exchange_type='headers')

# High-value orders go to premium processing queue
channel.queue_bind(
    exchange='events',
    queue='premium-order-processor',
    arguments={
        'x-match': 'all',              # Must match ALL headers
        'orderType': 'standard',
        'customerTier': 'gold'
    }
)

# All orders go to general processor
channel.queue_bind(
    exchange='events',
    queue='standard-order-processor',
    arguments={'x-match': 'any', 'orderType': 'standard'}
)
```

**Kafka Streams Content-Based Routing**:
```java
KStream<String, Order> orders = builder.stream("orders");

// Branch into separate streams based on content
Map<String, KStream<String, Order>> branches = orders.split(Named.as("branch-"))
    .branch((key, order) -> order.getCustomerTier().equals("gold"),
            Branched.as("premium"))
    .branch((key, order) -> order.getAmount() > 10000,
            Branched.as("high-value"))
    .defaultBranch(Branched.as("standard"));

branches.get("branch-premium").to("premium-orders");
branches.get("branch-high-value").to("high-value-orders");
branches.get("branch-standard").to("standard-orders");
```

---

## Dead Letter Queues (DLQ)

### What Is a Dead Letter Queue?
A dead letter queue (DLQ) is a holding area for messages that cannot be successfully processed. Messages end up in the DLQ when:
- Maximum retry count exceeded
- Message TTL expired before consumption
- Consumer explicitly rejects without requeue
- Queue length limit exceeded (overflow)

### DLQ Configuration

**RabbitMQ**:
```python
# Main queue with DLQ configuration
channel.queue_declare(
    queue='order-processor',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',           # DLX exchange name
        'x-dead-letter-routing-key': 'order.failed', # Routing key for DLQ
        'x-message-ttl': 30000,                    # Message expires after 30s
        'x-max-length': 100000                     # Max 100K messages
    }
)

# DLX exchange and DLQ
channel.exchange_declare(exchange='dlx', exchange_type='direct')
channel.queue_declare(queue='order-dlq', durable=True)
channel.queue_bind(exchange='dlx', queue='order-dlq', routing_key='order.failed')
```

**AWS SQS**:
```json
{
  "QueueName": "order-processor",
  "Attributes": {
    "RedrivePolicy": {
      "deadLetterTargetArn": "arn:aws:sqs:us-east-1:123:order-dlq",
      "maxReceiveCount": "5"    // Move to DLQ after 5 failed attempts
    }
  }
}
```

### DLQ Handling Strategy
DLQs should not be black holes. Establish operational procedures:

1. **Alert on DLQ growth**: PagerDuty/OpsGenie alert when DLQ > threshold
2. **DLQ inspection**: Tooling to view, categorize, and investigate failed messages
3. **Replay mechanism**: After fixing the consumer bug, replay DLQ messages to the main queue
4. **Dead message analysis**: Log DLQ entries to data lake for trend analysis
5. **Poison pill handling**: Identify messages that consistently fail (schema errors, corrupt data) and route to separate alert/investigation queue

### Retry Strategies
```
Immediate retry (1 attempt) → Short backoff retry (2-3 attempts) → DLQ

Exponential backoff with jitter:
  Attempt 1: 1s
  Attempt 2: 2s + random(0-1s)
  Attempt 3: 4s + random(0-2s)
  Attempt 4: 8s + random(0-4s)
  Attempt 5: → DLQ
```

**Delayed retry queue pattern** (RabbitMQ):
```
Main Queue → Consumer fails → DLX (with per-attempt TTL) → Retry Queue
                ↑                                                  ↓
                └──────────────────────────────────────────────────┘
                              (after TTL expires, message re-enters main queue)
```

---

## Managed Cloud Broker Services

| Service | Protocol | Best For |
|---|---|---|
| AWS SQS | HTTP/HTTPS (own protocol) | Simple task queues, Lambda triggers |
| AWS SNS | HTTP/HTTPS | Fan-out, mobile push |
| AWS EventBridge | HTTP/HTTPS | Event-driven SaaS integration, rule-based routing |
| Google Cloud Pub/Sub | HTTP/gRPC | GCP-native pub/sub, global fan-out |
| Azure Service Bus | AMQP 1.0 | Enterprise messaging, JMS compatibility |
| Azure Event Grid | HTTP/HTTPS | Azure resource events, webhook delivery |
| Confluent Cloud | Kafka protocol | Managed Kafka at enterprise scale |
| CloudAMQP | AMQP | Managed RabbitMQ |
