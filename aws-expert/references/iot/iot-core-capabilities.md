# AWS IoT Core & Device Management — Capabilities Reference

For CLI commands, see [iot-core-cli.md](iot-core-cli.md).

---

## AWS IoT Core

**Purpose**: Managed cloud service that enables connected devices to interact with cloud applications and other devices. Acts as a message broker and rule engine for IoT workloads.

### Core Concepts

| Concept | Description |
|---|---|
| **Thing** | A representation of a device or logical entity in the Device Registry; stores metadata as attributes |
| **Thing Type** | Shared configuration and description for a group of things (e.g., "LightBulb"); simplifies bulk management |
| **Thing Group** | Static or dynamic collection of things; supports hierarchical group membership for policy/job targeting |
| **Certificate** | X.509 certificate used for mutual TLS authentication between device and AWS IoT Core |
| **Policy** | JSON document (similar to IAM) that grants permissions to connect, publish, subscribe, receive on MQTT topics |
| **Client ID** | Identifier the device uses when connecting via MQTT; typically matches the Thing name |
| **MQTT Topic** | UTF-8 string hierarchy used for message routing (e.g., `factory/line1/temperature`) |
| **Endpoint** | Per-account MQTT broker endpoint: `<account-prefix>.iot.<region>.amazonaws.com` |

---

## MQTT Broker

AWS IoT Core supports MQTT 3.1.1 and MQTT 5.0 over:

| Protocol | Port | Notes |
|---|---|---|
| **MQTT over TLS** | 8883 | Primary device protocol; mutual TLS with X.509 certs |
| **MQTT over WebSocket** | 443 | For devices behind firewalls; uses SigV4 or custom auth |
| **HTTPS** | 443 | For devices that cannot maintain persistent connections; publish-only |
| **LoRaWAN** (via FTP over CUPS) | — | Managed LoRaWAN support; AWS manages gateways |

**Limits**: Up to 500,000 concurrent connections per account (soft); messages up to 128 KB; QoS 0 and QoS 1 supported (QoS 2 not supported).

---

## Message Routing — Rules Engine

The Rules Engine evaluates inbound MQTT messages against SQL-based rules and routes matching messages to one or more AWS service targets.

### Rule SQL

```sql
-- Select fields from any topic matching the pattern
SELECT temperature, humidity, clientid() AS device_id, timestamp() AS ts
FROM 'sensors/+/telemetry'
WHERE temperature > 80
```

Wildcards: `+` (single level), `#` (multi-level, must be last segment).

### Rule Actions (Destinations)

| Destination | Use case |
|---|---|
| **Amazon S3** | Archive raw telemetry; supports key prefix expressions |
| **Amazon DynamoDB** | Write individual rows; DynamoDBv2 action supports full JSON document |
| **Amazon Kinesis Data Streams** | High-throughput streaming ingestion |
| **Amazon Data Firehose** | Stream to S3, Redshift, OpenSearch |
| **Amazon SQS** | Decouple processing; fan-out via SNS+SQS pattern |
| **Amazon SNS** | Push notifications, fan-out |
| **AWS Lambda** | Custom processing logic |
| **Amazon OpenSearch** | Index telemetry for search and dashboards |
| **Amazon Timestream** | Time-series database; native IoT integration |
| **IoT Events** | Feed state machine detector models |
| **IoT Analytics** | Pipeline-based message enrichment and storage |
| **Step Functions** | Trigger workflows |
| **CloudWatch Logs / Metrics** | Observability |
| **Kafka (MSK)** | Publish to Kafka topics |
| **Republish** | Route to another MQTT topic within IoT Core |
| **HTTP** | POST to an HTTPS endpoint |

**Error handling**: Each rule has an optional error action that captures routing failures.

---

## Device Shadow

A JSON document that stores and retrieves the current state (reported) and desired state of a device.

### Shadow Types

| Type | Description |
|---|---|
| **Classic (unnamed) shadow** | Single shadow per thing; accessed via reserved topics `$aws/things/<name>/shadow/...` |
| **Named shadow** | Multiple shadows per thing; accessed via `$aws/things/<name>/shadow/name/<shadowName>/...` |

### Shadow Document Structure

```json
{
  "state": {
    "desired": { "color": "red", "brightness": 80 },
    "reported": { "color": "red", "brightness": 75 },
    "delta": { "brightness": 80 }
  },
  "metadata": { ... },
  "version": 12,
  "timestamp": 1700000000
}
```

**Delta**: Automatically computed by IoT Core; contains fields where `desired` and `reported` differ. Device subscribes to `$aws/things/<name>/shadow/update/delta` to receive change notifications.

**Optimistic locking**: Include `"version"` in update to prevent lost-update races; returns 409 Conflict on mismatch.

---

## Device Registry

Stores metadata about devices (things). Attributes are key-value pairs (string values). Supports:
- Up to 50 attributes per thing
- Thing types with fixed attribute names and descriptions
- Searchable via Fleet Indexing

---

## Fleet Indexing

Enables search across thing attributes, connectivity status, shadow state, and named shadow data using a query language similar to Elasticsearch.

| Index | Contents |
|---|---|
| `AWS_Things` | Thing attributes, thing groups, connectivity status, shadow state |
| `AWS_ThingGroups` | Group hierarchy and attributes |

**Query examples**:
```
connectivity.connected:true AND attributes.location:"us-east"
shadow.reported.temperature:[70 TO *]
```

**Aggregation**: Count, average, min, max, sum, percentile over numeric attributes.

---

## Jobs (Remote Operations)

Define and send remote operations (firmware update, reboot, config change) to one or more devices.

| Concept | Description |
|---|---|
| **Job** | Operation defined by a JSON document; targeted at things or thing groups |
| **Job document** | JSON stored in S3 or inline; contains instructions for the device agent |
| **Job execution** | Per-device instance of a job; tracks state: QUEUED → IN_PROGRESS → SUCCEEDED/FAILED |
| **Job template** | Reusable job document configuration |
| **Snapshot job** | Targets current set of things; does not add new devices added later |
| **Continuous job** | Targets dynamic groups; automatically picks up newly added devices |

**Rollout configuration**: Rate-based rollouts (max per-minute), exponential rollout with base rate + increment factor + criteria for automatic cancellation.

**Pre/post conditions**: `abortConfig` stops a job if failure percentage exceeds threshold.

---

## Secure Tunneling

Opens a bidirectional WebSocket tunnel (WebTunnel) from the cloud to a device behind NAT/firewall, without opening inbound ports.

- Device runs the `aws-iot-securetunnel` local proxy agent
- Operator connects their local proxy to the source end of the tunnel
- Tunnels are time-limited (up to 12 hours) and encrypted

---

## Credential Provider

AWS IoT Core can exchange an X.509 device certificate for temporary AWS credentials (via STS AssumeRoleWithCertificate). Devices can then directly call AWS services (e.g., S3, Kinesis) without storing long-term IAM keys.

---

## Custom Domains and Custom Authentication

| Feature | Description |
|---|---|
| **Custom domain** | Configure your own domain (e.g., `iot.example.com`) with ACM certificates for the MQTT endpoint |
| **Custom authorizer** | Lambda-based token/header validation for non-X.509 auth (e.g., JWT, OAuth, API key); supports MQTT username/password or HTTP headers |

---

## AWS IoT Device Management

**Purpose**: Register, organize, monitor, and remotely manage IoT devices at scale.

### Fleet Hub

Web application for field operators: view fleet health, search devices, create alarms, run jobs. Backed by Fleet Indexing. No custom application code required for a basic operational console.

### Bulk Registration

Register thousands of devices in one operation using a CSV file and a provisioning template stored in S3.

```
# CSV format: certificateId, thingName, attribute1...
# CLI: aws iot start-thing-registration-task
```

### Provisioning Templates

JSON templates that define the resources (thing, certificate, policy) created when a device first connects. Two types:

| Type | Description |
|---|---|
| **Fleet provisioning** | Device calls `CreateKeysAndCertificate` API using a claim certificate; template creates the permanent certificate and thing |
| **Just-In-Time Provisioning (JITP)** | Triggered automatically when a device with an unregistered certificate (signed by a registered CA) first connects |
| **Just-In-Time Registration (JITR)** | Like JITP but fires an SNS notification; you handle registration logic via Lambda |

### OTA Updates (Jobs-based)

AWS IoT Device Management wraps the Jobs service to deliver firmware images:
- Job document includes S3 presigned URL to firmware binary
- Device agent downloads and applies update
- Integrates with FreeRTOS OTA agent and AWS IoT Greengrass update mechanism

### Device Groups

| Type | Description |
|---|---|
| **Static group** | Manually add/remove things; used for targeted policies and jobs |
| **Dynamic group** | Query-based membership using Fleet Indexing; automatically includes matching things |

---

## Pricing Model Notes

| Resource | Pricing basis |
|---|---|
| **Connectivity** | Per connection-minute (MQTT) or per 5 KB of messages (HTTP) |
| **Messaging** | Per million messages; tiered pricing |
| **Rules Engine** | Per rule triggered + per action executed |
| **Device Shadow** | Per operation (get/update/delete) |
| **Fleet Indexing** | Per thing indexed per month + per query |
| **Jobs** | Per remote operation per device |
| **Secure Tunneling** | Per tunnel-minute |

---

## Important Limits

| Limit | Default |
|---|---|
| Max MQTT message size | 128 KB |
| Max shadow document size | 8 KB |
| Max concurrent Jobs per device | 1 (configurable via job execution limit) |
| Max rules per account | 1,000 |
| Max rule actions per rule | 10 |
| Max thing groups per thing | 10 |
| Thing attribute value max length | 800 bytes |
| Fleet Indexing query max results | 500 per page |
