# AWS IoT Edge — Capabilities Reference

For CLI commands, see [iot-edge-cli.md](iot-edge-cli.md).

---

## AWS IoT Greengrass v2

**Purpose**: Open-source edge runtime that extends AWS capabilities to local devices. Runs AWS Lambda functions, Docker containers, native OS processes, and custom components at the edge with local processing, messaging, data management, and ML inference.

### Core Concepts

| Concept | Description |
|---|---|
| **Core device** | A device (EC2 instance, physical hardware) running the Greengrass nucleus; registered as a thing in AWS IoT Core |
| **Component** | Deployable unit of software on Greengrass: recipe + artifacts; versioned and reusable |
| **Recipe** | YAML or JSON manifest describing component metadata, dependencies, lifecycle scripts, and configuration schema |
| **Artifact** | Binary file, script, or container image associated with a component; stored in S3 |
| **Deployment** | A desired set of components and their configurations pushed to one or more core devices |
| **Nucleus** | The Greengrass kernel component (`aws.greengrass.Nucleus`); manages lifecycle and IPC |
| **IPC** | Inter-process communication bus for local components to publish/subscribe, access secrets, read shadows, etc. |
| **Local MQTT broker** | Moquette broker provided by `aws.greengrass.clientdevices.mqtt.Bridge`; handles local device-to-device and device-to-cloud MQTT |

---

## Greengrass Nucleus

The nucleus is the only required component. It:
- Registers the device with AWS IoT Core
- Manages component lifecycle (install, run, update, shutdown)
- Handles deployment polling and application
- Provides the IPC server on a Unix domain socket
- Manages log rotation

**Installation**: Bootstrap script downloads nucleus JAR, configures as a system service, registers as a thing+cert+policy.

```bash
# Bootstrap install (on device)
sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar /tmp/greengrass-nucleus-latest.jar \
  --init-config /tmp/config.yaml \
  --component-default-user ggc_user:ggc_group \
  --setup-system-service true
```

---

## Components

### Public (AWS-provided) Components

| Component | Purpose |
|---|---|
| `aws.greengrass.Nucleus` | Core runtime; required |
| `aws.greengrass.Cli` | Local CLI for interacting with Greengrass from the device terminal |
| `aws.greengrass.StreamManager` | Local stream manager for buffering and routing data to AWS services |
| `aws.greengrass.LambdaManager` | Run Lambda functions locally |
| `aws.greengrass.DockerApplicationManager` | Pull and run Docker containers |
| `aws.greengrass.TokenExchangeService` | Issues TES (Token Exchange Service) credentials to components accessing AWS APIs |
| `aws.greengrass.clientdevices.mqtt.Moquette` | Local MQTT broker for client devices |
| `aws.greengrass.clientdevices.mqtt.Bridge` | Bridge local MQTT topics to/from IoT Core |
| `aws.greengrass.clientdevices.Auth` | Authenticate and authorize client devices connecting locally |
| `aws.greengrass.ShadowManager` | Sync thing shadows between local and cloud; serve shadow requests locally without connectivity |
| `aws.greengrass.LogManager` | Upload component logs to CloudWatch Logs |
| `aws.greengrass.SecretManager` | Cache and provide AWS Secrets Manager secrets locally |
| `aws.iotAnalytics.EdgeConnector` | Send data to IoT Analytics from edge |
| `aws.greengrass.DiskSpooler` | Spool MQTT messages to disk during cloud disconnection |

### Custom Components

You create custom components with:
1. A **recipe** (YAML/JSON) defining lifecycle phases: `Install`, `Startup`, `Run`, `Shutdown`, `Recover`
2. **Artifacts**: scripts, binaries, model files uploaded to S3
3. Optional **configuration schema** with default values; operators can override via deployment

**Recipe lifecycle example**:
```yaml
ComponentName: com.example.TempSensor
ComponentVersion: 1.0.0
ComponentDescription: Temperature sensor publisher
ComponentPublisher: MyCompany
ComponentDependencies:
  aws.greengrass.Nucleus:
    VersionRequirement: ">=2.0.0"
Manifests:
  - Platform:
      os: linux
    Lifecycle:
      Install:
        Script: "pip3 install -r {artifacts:path}/requirements.txt"
      Run:
        Script: "python3 {artifacts:path}/sensor.py --interval {configuration:/publishIntervalSeconds}"
    Artifacts:
      - URI: s3://my-bucket/components/temp-sensor/1.0.0/sensor.py
      - URI: s3://my-bucket/components/temp-sensor/1.0.0/requirements.txt
ComponentConfiguration:
  DefaultConfiguration:
    publishIntervalSeconds: 5
    topic: sensors/temperature
```

---

## Deployments

A deployment defines the target (single device, thing group, or all core devices) and the desired component list with versions and configuration overrides.

| Deployment type | Description |
|---|---|
| **Cloud deployment** | Created via AWS console, CLI, or API; Greengrass polls and applies |
| **Local deployment** | Applied directly on-device via `greengrass-cli`; useful for development |

**Deployment states**: `ACTIVE` (in progress) → `COMPLETED` | `FAILED` | `CANCELED` | `TIMED_OUT`

**Configuration merge**: Each component has a configuration object; deployments can merge (partial update) or reset (full replace) the configuration.

---

## Stream Manager

`aws.greengrass.StreamManager` provides an SDK-accessible local FIFO buffer with automatic routing to AWS cloud services.

| Destination | Notes |
|---|---|
| **Amazon Kinesis Data Streams** | Real-time streaming at scale |
| **Amazon Data Firehose** | Delivery to S3, Redshift, OpenSearch |
| **Amazon S3** | Batch upload with size/time triggers |
| **AWS IoT Analytics** | Channel ingestion |
| **AWS IoT SiteWise** | Asset property data ingestion |

**Key behaviors**:
- Configurable maximum stream size; supports size-based and time-based export triggering
- Data persisted to disk; survives process restarts
- Priority queues; streams can be paused and resumed
- Automatic retry with exponential backoff on export failure

---

## Local AWS Services (Token Exchange Service)

The Token Exchange Service (TES) allows Greengrass components to call AWS APIs without embedding long-term credentials. TES exchanges the core device's X.509 certificate for temporary STS credentials via an IAM role alias. Components use the local TES HTTP endpoint or let the AWS SDK auto-discover it.

---

## Local ML Inference (SageMaker Edge)

| Feature | Description |
|---|---|
| **SageMaker Edge Manager** | Component that runs the SageMaker Edge Agent on a Greengrass device; packages and deploys compiled models |
| **Model component** | A Greengrass component containing a compiled ML model (via SageMaker Neo or TensorRT) and its runtime |
| **Inference component** | Custom component that calls the local Edge Agent gRPC API to run predictions |
| **DLR runtime** | Deep Learning Runtime packaged as a public Greengrass component; supports models compiled with SageMaker Neo |

Supported frameworks: TensorFlow Lite, PyTorch, MXNet (via SageMaker Neo compilation).

---

## Greengrass CLI (On-Device)

The `greengrass-cli` is installed via the `aws.greengrass.Cli` component and runs on the device itself.

```bash
# List installed components
sudo /greengrass/v2/bin/greengrass-cli component list

# Deploy components locally (development workflow)
sudo /greengrass/v2/bin/greengrass-cli deployment create \
  --recipeDir ~/components/recipes \
  --artifactDir ~/components/artifacts \
  --merge "com.example.TempSensor=1.0.0"

# Remove a component
sudo /greengrass/v2/bin/greengrass-cli deployment create \
  --remove com.example.OldComponent

# Restart a component
sudo /greengrass/v2/bin/greengrass-cli component restart \
  --names com.example.TempSensor

# Tail component logs
sudo tail -f /greengrass/v2/logs/com.example.TempSensor.log

# Get device-level logs
sudo tail -f /greengrass/v2/logs/greengrass.log
```

---

## Client Device Support

Local client devices (not running Greengrass nucleus) can connect to a Greengrass core device via MQTT and use cloud features:

1. **`aws.greengrass.clientdevices.Auth`**: Validates device certificates against IoT Core and enforces local policies
2. **`aws.greengrass.clientdevices.mqtt.Moquette`**: Local MQTT broker
3. **`aws.greengrass.clientdevices.mqtt.Bridge`**: Routes topic patterns between local MQTT ↔ IoT Core ↔ local Pub/Sub

Devices use standard MQTT (port 8883) with mutual TLS using their IoT Core certificate.

---

## Greengrass Pricing

| Resource | Pricing basis |
|---|---|
| **Core devices** | First 3 core devices free per account; $0.16/device/month for additional devices |
| **Component storage** | Standard S3 pricing for artifact storage |
| **Data transfer** | Standard data transfer rates |

---

## FreeRTOS

**Purpose**: Open-source real-time operating system kernel for microcontrollers (MCUs) with tight memory and power constraints. AWS maintains and extends FreeRTOS with connectivity libraries and cloud integration.

### Core Concepts

| Concept | Description |
|---|---|
| **FreeRTOS kernel** | Pre-emptive/cooperative RTOS; tasks, queues, semaphores, mutexes, timers, event groups |
| **Task** | Independently schedulable execution unit; each has a priority, stack, and code function |
| **Tick** | Configurable heartbeat (e.g., 1 ms); basis for delays, timeouts, and time-slicing |
| **Heap** | Five heap allocation schemes (heap_1 through heap_5) for different fragmentation trade-offs |
| **Port** | Architecture-specific layer; supports ARM Cortex-M0/M3/M4/M7, RISC-V, Xtensa, MSP430, and many others |

### FreeRTOS Libraries (AWS-Maintained)

| Library | Purpose |
|---|---|
| **coreMQTT** | MQTT 3.1.1 client; minimal dependencies; supports QoS 0 and QoS 1 |
| **coreMQTT-Agent** | Thread-safe MQTT operations over coreMQTT; serializes access via a task |
| **coreHTTP** | HTTP/1.1 client library |
| **coreJSON** | Stateful JSON parser; no dynamic memory allocation |
| **corePKCS11** | PKCS #11 cryptography abstraction; plugs into mbedTLS or hardware secure elements |
| **FreeRTOS+TCP** | Full TCP/IP stack; Ethernet, Wi-Fi, PPP; IPv4 and IPv6 |
| **FreeRTOS+FAT** | FAT12/FAT16/FAT32 filesystem for flash and SD card storage |
| **AWS IoT OTA** | Over-the-air firmware update agent; integrates with AWS IoT Jobs |
| **AWS IoT Device Shadow** | Device Shadow client library |
| **AWS IoT Jobs** | Jobs client library for processing job documents |
| **AWS IoT Fleet Provisioning** | Client library for fleet provisioning via MQTT APIs |
| **AWS IoT Device Defender** | Metrics collection and reporting for Device Defender Detect |
| **Cellular Interface** | Abstraction for LTE-M/NB-IoT modems (Sierra, Quectel, u-blox) |
| **backoffAlgorithm** | Jitter/exponential backoff utility |

### OTA Update Flow (FreeRTOS)

1. Device polls an MQTT topic for new job notifications
2. IoT Jobs delivers job document containing S3 presigned URL to firmware image
3. OTA agent downloads image in chunks, verifies code-signing signature
4. Agent writes image to secondary flash partition
5. On reboot, bootloader checks signature; swaps partitions if valid

**Code signing**: AWS Signer or custom signing key registered via `aws signer` CLI. Devices verify using a public key stored in secure element or flash.

### Partner Ecosystem

FreeRTOS is qualified on hardware from: ST Microelectronics, Espressif (ESP32), NXP, Microchip, Renesas, Texas Instruments, Nordic Semiconductor, Infineon, Nuvoton, and many others. Qualified boards listed in the AWS Partner Device Catalog.

### FreeRTOS and AWS IoT Core

FreeRTOS devices connect to AWS IoT Core like any other MQTT device. They are registered as things, use X.509 certificates, and are governed by IoT policies. FreeRTOS does not have its own separate AWS CLI namespace — all cloud-side management uses `aws iot` commands.

### Important Limits and Characteristics

| Item | Value |
|---|---|
| Minimum RAM footprint | ~6–10 KB for kernel; libraries add more |
| Max priority levels | Configurable; typically 8–32 levels |
| Max tasks | Limited by available RAM (stack per task) |
| MQTT message size | Constrained by device RAM; typically 256 B – 4 KB practical |
| OTA image size | Limited by available flash and download bandwidth |
