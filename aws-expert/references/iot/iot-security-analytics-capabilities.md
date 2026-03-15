# AWS IoT Security & Analytics — Capabilities Reference

For CLI commands, see [iot-security-analytics-cli.md](iot-security-analytics-cli.md).

---

## AWS IoT Device Defender

**Purpose**: Audit device configurations and continuously monitor device behavior to detect abnormalities that may indicate a compromised device or security misconfiguration.

### Two Pillars: Audit and Detect

| Pillar | Description |
|---|---|
| **Audit** | Point-in-time or scheduled checks of IoT configurations (cloud-side) against security best practices |
| **Detect** | Continuous behavioral monitoring of devices using cloud-side and device-side metrics; ML-based anomaly detection |

---

## Device Defender Audit

Audit checks evaluate your AWS IoT Core configuration. Each check produces: COMPLIANT, NON_COMPLIANT, or NOT_APPLICABLE.

### Audit Check Categories

| Check | Description |
|---|---|
| **AUTHENTICATED_COGNITO_ROLE_OVERLY_PERMISSIVE** | Cognito identity pool roles allow more than needed |
| **CA_CERTIFICATE_EXPIRING** | CA certificates expiring within 30 days |
| **CA_CERTIFICATE_KEY_QUALITY** | CA certificates with weak key algorithms |
| **CONFLICTING_CLIENT_IDS** | Multiple devices connecting with same client ID (one forces disconnect) |
| **DEVICE_CERTIFICATE_EXPIRING** | Device certificates expiring within 30 days |
| **DEVICE_CERTIFICATE_KEY_QUALITY** | Certificates using weak key lengths or algorithms (RSA < 2048 bits) |
| **DEVICE_CERTIFICATE_SHARED_USE** | Same device certificate used across multiple concurrent connections |
| **IOT_POLICY_OVERLY_PERMISSIVE** | Policies with wildcard resources (`*`) or overly broad actions |
| **IOT_ROLE_ALIAS_ALLOWS_ACCESS_TO_UNUSED_SERVICES** | Role aliases granting permissions to services the device doesn't need |
| **IOT_ROLE_ALIAS_OVERLY_PERMISSIVE** | Role aliases with excessive IAM permissions |
| **LOGGING_DISABLED** | AWS IoT logging is not enabled |
| **REVOKED_CA_CERTIFICATE_STILL_ACTIVE** | Revoked CA certificates still have ACTIVE status |
| **REVOKED_DEVICE_CERTIFICATE_STILL_ACTIVE** | Revoked device certificates still have ACTIVE status |
| **UNAUTHENTICATED_COGNITO_ROLE_OVERLY_PERMISSIVE** | Unauthenticated Cognito roles too permissive |

### Audit Scheduling

- **On-demand**: Run immediately via API/console
- **Scheduled**: Daily, weekly, monthly (configurable per check)

### Audit Findings and Suppression

Non-compliant findings include: resource type, resource identifier, check name, severity. Findings can be suppressed for specific resources with an expiration date and justification reason.

---

## Device Defender Detect

Detect monitors for anomalous device behavior by comparing actual behavior against expected profiles.

### Metric Sources

| Metric Source | Description |
|---|---|
| **Cloud-side metrics** | Collected by AWS from IoT Core connection and messaging patterns (no device code changes needed) |
| **Device-side metrics** | Reported by the device itself using the Device Defender SDK/agent over a reserved MQTT topic |

### Cloud-Side Behaviors (examples)

| Metric | Description |
|---|---|
| `aws:num-messages-sent` | Number of MQTT messages sent by device |
| `aws:num-messages-received` | Number of MQTT messages received |
| `aws:num-disconnects` | Number of MQTT disconnects |
| `aws:num-authorization-failures` | Number of auth failures (wrong topic, missing permission) |
| `aws:source-ip-address` | IP addresses the device connects from |
| `aws:message-byte-size` | Size of messages published |

### Device-Side Behaviors (examples)

| Metric | Description |
|---|---|
| `aws:all-bytes-out` | Total bytes sent over all network connections |
| `aws:all-bytes-in` | Total bytes received |
| `aws:listening-tcp-ports` | Open TCP listening ports on the device |
| `aws:established-connections` | Current established TCP connections |
| `aws:num-listening-tcp-ports` | Number of open TCP ports |
| `aws:num-established-connections` | Number of established connections |

Custom metrics (device-reported): Define custom metrics (numeric values, lists of IPs, lists of ports) that devices report and Defender tracks.

### Security Profiles

A security profile defines expected behaviors (threshold rules) and attaches to a target (thing group or all registered things).

**Behavior operators**: `less-than`, `less-than-equals`, `greater-than`, `greater-than-equals`, `in-cidr-set`, `not-in-cidr-set`, `in-port-set`, `not-in-port-set`, `in-set`, `not-in-set`

**Consecutive data points**: Alarm when metric exceeds threshold for N consecutive data points.

### ML Detect

ML Detect uses machine learning to automatically learn the normal behavior baseline for each device and alert when behavior deviates significantly. No manual threshold configuration required.

- Models trained per metric per device over 14 days of data
- Confidence levels: LOW, MEDIUM, HIGH
- Minimum 25 data points per metric required before model activates

### Violations and Mitigation Actions

When a device violates a behavior, a **violation** record is created. Violations move through states: ACTIVE → VERIFIED | BENIGN_POSITIVE | FALSE_POSITIVE | UNKNOWN.

**Mitigation actions** can be automatically or manually triggered on violations:

| Action type | Description |
|---|---|
| **ADD_THINGS_TO_THING_GROUP** | Move device to a quarantine thing group |
| **REPLACE_DEFAULT_POLICY_VERSION** | Replace device policy with a blank/restricted policy |
| **ENABLE_IOT_LOGGING** | Enable detailed IoT Core logging |
| **PUBLISH_FINDING_TO_SNS** | Send violation details to SNS |
| **UPDATE_CA_CERTIFICATE** | Mark CA certificate as inactive |
| **UPDATE_DEVICE_CERTIFICATE** | Mark device certificate as inactive |

---

## AWS IoT Events

**Purpose**: Fully managed service for detecting and responding to events from IoT sensors and applications. Implements state machine logic without writing server infrastructure code.

### Core Concepts

| Concept | Description |
|---|---|
| **Input** | JSON message schema defining the fields that IoT Events receives; routes messages to detector models |
| **Detector model** | State machine definition: states, events (transitions), conditions, and actions |
| **Detector** | A running instance of a detector model; one instance per unique `key` value (e.g., one per `deviceId`) |
| **State** | A stable condition within the detector model; a detector is always in exactly one state |
| **Event** | A rule that fires within a state when a condition is true and an input is received |
| **Condition** | Boolean expression evaluated against input fields and internal variables |
| **Variable** | Named internal state for a detector instance; persists across events |
| **Timer** | Named timer within a detector; can trigger events on expiration |
| **Action** | Side effect triggered when an event fires |
| **Alarm model** | Simplified pattern for threshold-based alarms (built on top of detector models) |

---

## IoT Events State Machine

### State Lifecycle

```
                 ┌──────────────────────────────────────────┐
                 │           Detector Instance               │
    Input ──────▶│  State A ──(condition)──▶ State B        │
    arrives      │    ↑                          │           │
                 │    └──────(condition)──────────┘           │
                 └──────────────────────────────────────────┘
```

Within each state, you define:
- **On Enter events**: Fire once when entering the state
- **On Input events**: Fire each time an input is received while in this state
- **On Exit events**: Fire once when leaving the state

### Condition Expressions

IoT Events uses a built-in expression language:

```
$input.TemperatureSensor.temperature > 90
AND $variable.consecutiveHighCount >= 3

$input.MotorMonitor.rpm > 5000
OR timeout("motorStall")

convert(Decimal, $input.Device.status) == 1
```

### Actions

| Action | Description |
|---|---|
| **iotTopicPublish** | Publish an MQTT message to IoT Core topic |
| **lambda** | Invoke an AWS Lambda function |
| **sns** | Publish to an SNS topic |
| **sqs** | Send message to SQS queue |
| **firehose** | Put record to Kinesis Data Firehose |
| **dynamoDB** | Write item to a DynamoDB table |
| **dynamoDBv2** | Write full JSON to DynamoDB |
| **iotEvents** | Send an input to another IoT Events input |
| **iotSiteWise** | Ingest a property value to SiteWise asset |
| **setVariable** | Set or update an internal variable |
| **setTimer** | Set a timer with name and duration |
| **clearTimer** | Clear a running timer |
| **resetTimer** | Reset a running timer to full duration |

---

## IoT Events Alarm Models

Simplified alarm pattern for threshold-based monitoring. An alarm model automatically creates a detector model with states: NORMAL → ACTIVE → ACKNOWLEDGED → SNOOZE_DISABLED → LATCHED.

- Inputs come from IoT Core rule actions or direct API calls
- Alarm notifications delivered to SNS
- Alarm state transitions trigger configurable actions
- Supports acknowledge, snooze, disable, and reset operations via API or IoT Events console

---

## IoT Events Pricing

| Resource | Basis |
|---|---|
| **Messages evaluated** | Per message evaluated against a detector model |
| **Detector instance-hours** | Per detector instance active per hour (for stateful detectors) |
| **Alarm evaluations** | Per message evaluated against alarm models |

---

## AWS IoT Analytics

**Purpose**: Managed service for collecting, processing, enriching, storing, and analyzing IoT data at scale. Provides a pipeline-based model to prepare data for ML and BI tools.

### Core Concepts

| Concept | Description |
|---|---|
| **Channel** | Entry point; receives raw messages from IoT Core rules or direct API; stores raw messages durably |
| **Pipeline** | Series of activities that transform, enrich, and route messages from a channel to a datastore |
| **Datastore** | Storage layer for processed messages; queryable via SQL datasets |
| **Dataset** | Named query (SQL or container) that materializes a result on a schedule or on-demand |
| **Dataset content** | The materialized result of a dataset query; accessible as CSV or JSON via presigned URL |

---

## IoT Analytics Channels

Channels receive and durably store raw messages.

| Option | Description |
|---|---|
| **Service-managed S3** | IoT Analytics manages S3 storage; configurable retention period |
| **Customer-managed S3** | Bring your own S3 bucket; you control encryption and lifecycle |

IoT Core routes messages to a channel via the `iotAnalytics` rule action. Direct ingestion via `batch-put-message` API.

---

## IoT Analytics Pipelines

A pipeline applies a sequence of **activities** to messages:

| Activity | Description |
|---|---|
| **channel** | Source of messages (input from a channel) |
| **lambda** | Invoke Lambda function to transform or enrich each message |
| **addAttributes** | Add new key-value attributes to each message |
| **removeAttributes** | Remove specified keys from the message |
| **selectAttributes** | Keep only specified keys (drop everything else) |
| **filter** | Drop messages not matching a SQL condition |
| **math** | Compute a numeric expression and add result as a new attribute |
| **deviceRegistryEnrich** | Look up the device's attributes from IoT Core Thing Registry and add to message |
| **deviceShadowEnrich** | Look up the device's classic shadow and merge into message |
| **datastore** | Output to a datastore (terminal activity) |

**Pipeline ordering**: Activities execute sequentially; the `channel` activity is always first, `datastore` is always last.

---

## IoT Analytics Datastores

| Option | Description |
|---|---|
| **Service-managed S3** | IoT Analytics manages partitioned Parquet storage; configurable retention |
| **Customer-managed S3** | Custom S3 bucket with custom partitioning |
| **IoT SiteWise multi-layer storage** | Route SiteWise data from IoT Analytics pipelines |

**File format**: Parquet (columnar) for efficient SQL querying.

---

## IoT Analytics Datasets

### SQL Dataset

Runs an Athena SQL query against a datastore to materialize a result set.

```sql
-- Example: daily average temperature per device
SELECT deviceId,
       DATE_TRUNC('hour', from_unixtime(timestamp)) AS hour,
       AVG(CAST(temperature AS DOUBLE)) AS avg_temp
FROM my_datastore
WHERE __dt >= current_date - interval '7' day
GROUP BY 1, 2
```

### Container Dataset

Runs a Docker container (SageMaker training job) to perform arbitrary analytics or ML training on dataset content. The container reads input from an S3 URI, writes output back to S3.

### Dataset Triggers

| Trigger | Description |
|---|---|
| **Schedule** | Cron expression (e.g., daily at midnight) |
| **Dataset dependency** | Triggered when another dataset's content is updated |
| **On-demand** | Manual via API or console |

---

## IoT Analytics Limits

| Limit | Default |
|---|---|
| Max channels per account | 100 |
| Max pipelines per account | 100 |
| Max datastores per account | 100 |
| Max datasets per account | 100 |
| Max message size | 128 KB |
| Max batch put messages per call | 100 messages |
| Message attribute value size | 32 KB per attribute |

---

## IoT Analytics Pricing

| Resource | Basis |
|---|---|
| **Message processing** | Per GB of data processed through pipelines |
| **Storage (channel/datastore)** | Per GB per month stored |
| **Dataset queries** | Per TB of data scanned (Athena pricing) |
| **Dataset content storage** | Per GB per month |
