# IoT Architecture on GCP — Capabilities

## Cloud IoT Core (Deprecated)

**Cloud IoT Core was deprecated on August 16, 2023 and is no longer available.**

Organizations previously using Cloud IoT Core must migrate to alternative solutions. GCP no longer provides a first-party managed MQTT broker service. This section documents the current recommended approach.

---

## Current GCP IoT Architecture Pattern

The recommended architecture for IoT on GCP uses a combination of self-managed or third-party MQTT brokers, Pub/Sub for message ingestion, and downstream GCP analytics services.

```
IoT Devices (MQTT/HTTP)
        │
        ▼
┌─────────────────────┐
│  MQTT Broker         │   (Self-managed on GCE/GKE, or partner solution)
│  HiveMQ / EMQX /    │   Handles device connections, auth, QoS, last will
│  VerneMQ / Mosquitto │
└─────────┬───────────┘
          │  Pub/Sub integration (bridge/export)
          ▼
┌─────────────────────┐
│   Cloud Pub/Sub     │   Managed, scalable message bus
│   (Topics per type) │   Device telemetry, command acknowledgment, alerts
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
Dataflow    Cloud Functions
(streaming)  (event-driven)
    │           │
    ▼           ▼
BigQuery    Firestore / Pub/Sub downstream
(analytics) (real-time state)
```

---

## Cloud Pub/Sub for IoT Ingestion

Pub/Sub is the primary GCP-managed service for IoT telemetry ingestion at scale.

**Key capabilities for IoT:**
- **Throughput**: billions of messages per day; no pre-provisioning needed
- **Durability**: messages retained for up to 7 days (configurable)
- **Fan-out**: one topic, multiple subscriptions (telemetry → BigQuery AND → alerting function simultaneously)
- **Schema validation**: enforce message schema (Avro or Protobuf) at the topic level; reject malformed messages
- **Dead letter topics**: route undeliverable messages to a DLQ for investigation
- **Message ordering**: use message ordering keys (e.g., device ID) to ensure in-order processing per device
- **Filtering**: subscriptions can filter messages by attributes (e.g., `device_type=sensor`, `alert_level=critical`) to route to different consumers

**Pub/Sub Lite** for high-volume, cost-sensitive IoT:
- Lower cost than standard Pub/Sub (pre-provisioned capacity model)
- Zonal (single zone) or Regional
- Ordered delivery within a partition
- Suitable for high-throughput, cost-sensitive telemetry where 7-day retention is not needed

**Topic design for IoT:**
```
iot-telemetry          # raw device readings; high volume
iot-commands           # commands sent to devices (if using Pub/Sub for bidirectional)
iot-alerts             # threshold-exceeded events; lower volume
iot-device-lifecycle   # connect/disconnect events
iot-dlq                # dead letter queue for failed processing
```

---

## MQTT Broker Options on GCP

Without Cloud IoT Core, you need a self-managed or partner MQTT broker:

### Self-Managed Options on GCE/GKE

| Broker | Strengths | Deployment |
|---|---|---|
| **HiveMQ** | Enterprise-grade; clustering; GCP-native Pub/Sub extension; MQTT 5.0 | GKE Helm chart; HiveMQ operator |
| **EMQX** | High throughput (millions of connections); cluster mode; REST API | GKE Helm chart; GCE cluster |
| **VerneMQ** | High availability; clustering; Lua plugins | GCE or GKE |
| **Eclipse Mosquitto** | Simple; lightweight; single-broker; low device count | GCE single VM; dev/test |

**HiveMQ on GKE** is the most common enterprise choice:
- Native Google Cloud Pub/Sub extension pushes MQTT messages to Pub/Sub topics
- Supports MQTT 3.1.1 and MQTT 5.0
- Cluster across zones for HA
- Mutual TLS (mTLS) for device authentication

### Device Authentication in Brokers

Replace Cloud IoT Core's JWT-based auth with:
- **mTLS**: each device has a client certificate; broker validates against CA certificate; strong, per-device identity
- **Username/password with LDAP or custom auth plugin**: simpler for smaller deployments
- **Token-based auth via custom plugin**: validate JWT from Firebase Auth or Google Identity Platform

---

## Edge TPU (Coral)

**Edge TPU** is Google's purpose-built ASIC for running TensorFlow Lite ML models at the edge (on devices, not in the cloud).

**Hardware form factors:**
| Form Factor | Use Case |
|---|---|
| USB Accelerator (USB 3.0) | Attach to Raspberry Pi, NVIDIA Jetson, any Linux host with USB |
| PCIe Accelerator (M.2 or PCIe) | Embedded in industrial computers and single-board computers |
| Dev Board | Standalone compute board with Edge TPU + CPU + connectivity |
| System-on-Module (SOM) | Integrate Edge TPU into custom hardware products |

**Performance:**
- Up to 4 TOPS (tera-operations per second) for inference
- Typical inference latency: <1ms for MobileNet-class models
- Power consumption: ~2W; suitable for battery-powered devices

**How it works:**
1. Train ML model in TensorFlow/Keras (full precision)
2. Convert to TensorFlow Lite (`.tflite`) with quantization (int8)
3. Compile with Edge TPU Compiler — maps operations to Edge TPU hardware
4. Run compiled model on device with PyCoral library or TFLite runtime
5. Model operations not supported by Edge TPU fall back to CPU automatically

**Coral Model Zoo**: pre-compiled models available for immediate use:
- MobileNet image classification (1000-class ImageNet)
- SSD MobileNet object detection (COCO dataset)
- DeepLab image segmentation
- MediaPipe face detection, pose estimation

**Deployment pattern:**
```
Cloud (Vertex AI)              Edge (Coral)
─────────────────              ────────────────
Train model                →   Compile for Edge TPU
Evaluate accuracy              Run inference locally (<1ms)
Update model                   Send anomaly events to Pub/Sub
                               Upload compressed/summarized data
```

---

## Time-Series Data Storage for IoT

Choosing the right storage backend for IoT data depends on query patterns and volume:

### Cloud Bigtable (High-Throughput Raw Time-Series)

Best for: high write throughput (millions of events/second), raw device readings, low-latency point reads

**Row key design for IoT:**
```
{device_type}#{device_id}#{reversed_timestamp}

Example: sensor#device-001#9999999999999

Reversed timestamp = MAX_LONG - epoch_milliseconds
→ scans return most-recent-first within a device
```

**Column family design:**
```
cf:temp     # temperature reading
cf:humidity # humidity reading
cf:battery  # battery level
```

Write pattern: one row per event; column qualifier = metric name; value = reading.

### BigQuery (Analytics Time-Series)

Best for: SQL queries, historical analysis, aggregations, joining with other data

- Partition by `DATE(event_timestamp)` or `TIMESTAMP_TRUNC(event_timestamp, DAY)`
- Cluster by `device_id` and `sensor_type`
- Streaming insert from Dataflow or direct from Pub/Sub subscription
- Use materialized views for common hourly/daily aggregations
- Long-term storage tier (auto-applied after 90 days) reduces storage cost

### Cloud SQL / Cloud Spanner (Moderate Time-Series with Relational Queries)

Best for: moderate event rates with SQL joins to device metadata (device registry, customer records)

- Cloud SQL: PostgreSQL with TimescaleDB extension for time-series optimization; single region
- Cloud Spanner: global consistency; use for multi-region IoT deployments needing strong consistency

### Managed Service for Prometheus (Metrics)

Best for: operational device metrics (CPU, memory, connectivity), alerting, dashboards

- Google Cloud Managed Service for Prometheus: drop-in replacement for self-managed Prometheus
- Collect device metrics via Prometheus exporters on gateway devices
- Query with PromQL; visualize in Grafana or Cloud Monitoring dashboards

---

## Device Management Alternatives

Without Cloud IoT Core's device registry, manage device identity and configuration via:

| Approach | Best For |
|---|---|
| **Firebase Realtime DB / Firestore** | Store device shadow/registry (last state, config); real-time sync to devices via Firebase SDKs |
| **GKE + Config Sync** | Fleet management for edge compute devices running GKE (edge); sync K8s configurations via GitOps |
| **IoT partner platforms** (see below) | Full device lifecycle management including firmware OTA, provisioning, monitoring |
| **Custom device registry in Firestore** | Device registration, certificate management, feature flags, shadow documents |

**IoT Partner Platforms on GCP Marketplace:**
- **Particle**: hardware + cloud platform; device provisioning, OTA firmware, telemetry, integration with GCP Pub/Sub
- **Blues Wireless**: cellular + BLE edge devices; Notehub.io cloud with GCP route integration
- **Losant**: enterprise IoT platform; device management, visual workflow builder, dashboards; runs on GCP
- **Leverege**: enterprise IoT data platform; GCP-native; Pub/Sub/BigQuery integration
