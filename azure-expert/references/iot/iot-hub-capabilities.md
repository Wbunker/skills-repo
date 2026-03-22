# IoT Hub & DPS — Capabilities Reference
For CLI commands, see [iot-hub-cli.md](iot-hub-cli.md).

## Azure IoT Hub

**Purpose**: Managed cloud gateway for bidirectional communication between IoT devices and the cloud. Handles device authentication, connection management, telemetry ingestion, and command delivery at massive scale.

### Tiers

| Tier | Free Units/day | Max Message Size | Features |
|---|---|---|---|
| **Free** | 8,000 messages | 0.5 KB | Development/testing only; one per subscription |
| **Basic** | Scales with units | 256 KB | D2C telemetry, C2D messaging; no device twins or direct methods |
| **Standard** | Scales with units | 256 KB | Full feature set: twins, direct methods, file upload, streams, routing |

> Note: Standard is required for production deployments with full management capabilities.

### Messaging Patterns

| Pattern | Direction | Use Case |
|---|---|---|
| **Device-to-Cloud (D2C) Telemetry** | Device → Cloud | Sensor readings, status updates, event data |
| **Cloud-to-Device (C2D) Messages** | Cloud → Device | Commands, configurations, notifications |
| **Direct Methods** | Cloud → Device (synchronous) | Reboot, firmware update triggers, immediate commands with response |
| **Device Twins** | Bidirectional | Synchronize configuration (desired properties) and status (reported properties) |
| **File Upload** | Device → Blob Storage | Large payloads: logs, firmware, images (up to 256 GB) |

### Protocols

| Protocol | Port | Notes |
|---|---|---|
| **MQTT** | 8883 (TLS) | Most efficient for constrained devices; preferred for IoT |
| **MQTT over WebSocket** | 443 | For devices behind firewalls blocking 8883 |
| **AMQP** | 5671 (TLS) | Efficient multiplexing; good for gateways handling many devices |
| **AMQP over WebSocket** | 443 | For firewall-restricted environments |
| **HTTPS** | 443 | Request/response only (polling); no persistent connection |

### Endpoints and Routing

| Endpoint Type | Description |
|---|---|
| **Built-in Event Hubs-compatible** | Default endpoint for D2C telemetry; Event Hubs SDK-compatible; 1–7 day retention |
| **Custom routing endpoints** | Route messages to Azure Storage, Service Bus Queue/Topic, Event Hubs, Event Grid |
| **Message routes** | Filter rules based on message body (JSON), application properties, or system properties |
| **Fallback route** | Catches messages not matched by any route; routes to built-in endpoint |

### Message Routing Conditions

```sql
-- Route only temperature alerts
temperatureAlert = true AND temperature > 100

-- Route messages from a specific device
$connectionDeviceId = 'device001'

-- Route based on message body (requires content type application/json)
$body.messageType = 'telemetry' AND $body.sensorId > 10
```

### Device Identity Registry

| Concept | Description |
|---|---|
| **Device identity** | Unique record per device: deviceId, authentication credentials, enabled/disabled status |
| **Authentication** | Symmetric key (SAS tokens), X.509 certificates (self-signed or CA-signed) |
| **Module identity** | Sub-identity within a device; used by IoT Edge modules |
| **Device twin** | JSON document for each device: tags (service-side metadata), desired properties (cloud → device config), reported properties (device → cloud state) |

### Device Twin Properties

```json
{
  "deviceId": "myDevice01",
  "tags": {
    "location": "building-A",
    "department": "facilities"
  },
  "properties": {
    "desired": {
      "telemetryInterval": 30,
      "fanSpeed": 70,
      "$version": 12
    },
    "reported": {
      "firmwareVersion": "1.4.2",
      "telemetryInterval": 30,
      "$version": 8
    }
  }
}
```

---

## Device Provisioning Service (DPS)

**Purpose**: Zero-touch, just-in-time device provisioning to IoT Hub without human intervention. Devices auto-register to the correct IoT Hub based on enrollment configuration when they first connect.

### Key Concepts

| Concept | Description |
|---|---|
| **Enrollment** | Configuration that allows a device or group of devices to auto-register |
| **Individual enrollment** | Single device; identified by X.509 certificate thumbprint or TPM endorsement key |
| **Enrollment group** | Group of devices sharing an X.509 CA certificate or symmetric key |
| **Attestation** | Mechanism to prove device identity: X.509 certificates, TPM, or symmetric key |
| **Allocation policy** | Determines which IoT Hub to assign: lowest latency, hashed distribution, static, custom (Azure Function) |
| **Linked IoT Hub** | IoT Hubs registered with DPS that can receive provisioned devices |
| **Re-provisioning** | Device can re-register to change IoT Hub (e.g., after location move) |

### Attestation Mechanisms

| Mechanism | Security Level | Use Case |
|---|---|---|
| **X.509 CA certificates** | Highest | Production; factory-provisioned certificates |
| **TPM** | High | Devices with TPM chip; hardware-protected private key |
| **Symmetric key** | Moderate | Development/testing; or devices without TPM/certificates |

### DPS Provisioning Flow

1. Device manufactured with credential (X.509 cert, TPM endorsement key, or SAS key)
2. Device powers on; calls DPS global endpoint (`global.azure-devices-provisioning.net`)
3. DPS validates attestation and finds matching enrollment
4. DPS provisions device in target IoT Hub (creates device identity)
5. DPS returns IoT Hub hostname to device
6. Device connects directly to assigned IoT Hub

### Per-Device and Per-Group Settings

- **Initial device twin state**: Set desired properties applied to device twin at first provisioning
- **Reprovision policy**: Update device configuration on re-registration (always, never, or on migration only)
- **Enrollment-level webhooks**: Trigger Azure Function for custom allocation logic
