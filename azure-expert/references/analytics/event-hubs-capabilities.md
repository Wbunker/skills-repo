# Azure Event Hubs — Capabilities

## Service Overview

Azure Event Hubs is a fully managed, real-time data ingestion service capable of receiving and processing millions of events per second. It is the "front door" of Azure's event streaming architecture — a durable, ordered event log designed for high-throughput ingestion from telemetry, logs, clickstreams, and IoT devices.

**Apache Kafka compatibility**: Event Hubs exposes the Kafka protocol endpoint — existing Kafka producers and consumers work without code changes by pointing to Event Hubs.

---

## Hierarchy

```
Event Hubs Namespace
├── Namespace-level: network config, geo-DR, schema registry, TUs/PUs
└── Event Hub (topic equivalent)
    ├── Partitions (immutable, ordered log per partition)
    │   ├── Partition 0
    │   ├── Partition 1
    │   └── Partition N
    └── Consumer Groups (independent cursor/offset per group)
        ├── $Default (always exists)
        ├── analytics-consumer-group
        └── storage-consumer-group
```

---

## Service Tiers

| Tier | Throughput | Retention | Consumer Groups | Kafka | Schema Registry | Key Features |
|---|---|---|---|---|---|---|
| **Basic** | 1 TU | 1 day | 1 | No | No | Development/test only |
| **Standard** | 40 TUs (auto-inflate to 400) | 7 days | 20 | Yes | Yes | Most production workloads |
| **Premium** | Processing Units (PUs) | Up to 90 days | 100 | Yes | Yes | Mission-critical, dedicated resources, private endpoint |
| **Dedicated** | Dedicated cluster (10+ CUs) | Up to 90 days | 1000 | Yes | Yes | Largest tenants, single-tenant, predictable performance |

### Throughput Units (Standard)

- 1 TU = 1 MB/s ingress, 2 MB/s egress.
- **Auto-inflate**: Automatically scale TUs up to configured maximum during spikes.

### Processing Units (Premium)

- PUs are dedicated compute (no shared infrastructure).
- Predictable low-latency and throughput.
- Supports dynamic PU scaling (scale in/out as needed).

### Capacity Units (Dedicated)

- Minimum 10 CUs, multitenant within a dedicated cluster.
- Highest throughput, lowest latency, single-tenant cluster.
- Monthly commitment required.

---

## Partitions

Partitions are the core unit of parallelism and ordering in Event Hubs:

### Key Characteristics

- **Immutable ordered log**: Events within a partition are strictly ordered by offset.
- **Parallel consumers**: Each partition can be consumed by one consumer in a consumer group simultaneously — max parallelism = partition count.
- **Partition count**: Configured at Event Hub creation time.
  - Standard: 1–32 (cannot be changed after creation — choose carefully).
  - Premium/Dedicated: 1–2000 (can be increased after creation).
- **Partition key**: Producers can specify a key → consistent hashing ensures same-key events go to the same partition (order preservation).
- **No key**: Round-robin across partitions (good for throughput, no ordering guarantee).

### Partition Count Planning

| Scenario | Recommendation |
|---|---|
| Throughput-optimized | Partition count = max expected TU count |
| Consumer parallelism | Partition count ≥ max consumer instances |
| Ordered processing per entity | Use entity ID as partition key |
| Standard tier | Cannot increase after creation — start with enough (e.g., 32) |

---

## Consumer Groups

Independent cursors (offsets) into the event stream for different consumers:

- Each consumer group maintains its own offset independently.
- Multiple applications can read the same stream simultaneously without interfering.
- `$Default` consumer group always exists.
- Standard tier: 20 consumer groups max.
- Consumer group + partition = one concurrent reader (AMQP exclusive receiver).

### Checkpointing

Consumers must checkpoint (save) their current offset to resume after failure:
- Azure Event Processor Host (EPH) / `EventProcessorClient` handles checkpointing automatically to Azure Blob Storage.
- Kafka consumers checkpoint to the Kafka offset topic on Event Hubs.

---

## Protocols

| Protocol | Port | Description |
|---|---|---|
| **AMQP 1.0** | 5671 (TLS), 5672 | Native Event Hubs protocol — Azure SDKs |
| **Kafka** | 9093 (TLS) | Kafka-compatible — existing Kafka clients |
| **HTTPS** | 443 | REST API for sending events (lower throughput) |
| **WebSocket** | 443 | AMQP over WebSocket (for firewalled environments) |

### Kafka Compatibility

Point Kafka clients to Event Hubs by changing bootstrap servers:

```properties
bootstrap.servers=mynamespace.servicebus.windows.net:9093
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="<connection-string>";
```

- **MirrorMaker 2**: Replicate from Apache Kafka cluster to Event Hubs for migration.
- **Kafka Connect**: Use Event Hubs as source or sink in Kafka Connect pipelines.
- Most Kafka client libraries (Java, Python, .NET, Go) work without modification.

---

## Event Retention

| Tier | Default | Maximum |
|---|---|---|
| Basic | 1 day | 1 day |
| Standard | 1 day (configurable) | 7 days |
| Premium | 1 day (configurable) | 90 days |
| Dedicated | 1 day (configurable) | 90 days |

Events are automatically deleted after the retention period. Extend retention with **Capture** for long-term storage.

---

## Capture (Auto-Archive)

Automatically archive events to Azure Blob Storage or ADLS Gen2 in Avro or Parquet format:

- **No custom consumer required** — Microsoft handles archiving.
- Archives organized in time-windowed folders: `{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}.avro`
- Configurable: capture interval (1–900 seconds) and capture size limit (10 MB–524 MB) — whichever triggers first.
- **Schema**: Captures event body + metadata (partition key, offset, sequence number, enqueue time).

```bash
# Enable capture to ADLS Gen2 in Parquet format
az eventhubs eventhub update \
  --name myeventhub \
  --namespace-name myns \
  --resource-group myRG \
  --enable-capture true \
  --capture-interval 300 \
  --capture-size-limit 104857600 \
  --destination-name EventHubArchive.AzureBlockBlob \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account} \
  --blob-container capture \
  --archive-name-format "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}" \
  --skip-empty-archives true
```

---

## Schema Registry

Store and manage Avro, JSON Schema, and Protobuf schemas:

- **Schema validation**: Producers validate messages against registered schema before sending.
- **Schema evolution**: Manage compatibility (backward, forward, full) as schemas change.
- **Schema groups**: Organize schemas by team or domain.
- Integrated with Kafka (uses Confluent Schema Registry-compatible API) and AMQP clients.

---

## Geo-Disaster Recovery and Geo-Replication

### Metadata Geo-DR (Standard+)

- Replicates namespace **metadata only** (Event Hub names, consumer groups, consumer group configurations).
- **Does not replicate events** — data must be managed by application.
- Failover: Change DNS alias to secondary namespace. RPO = near-zero metadata; data RPO = depends on producer/consumer behavior.
- Alias: Single connection string for both primary and secondary — applications don't change config.

### Geo-Replication (Premium/Dedicated)

- **Full event data replication** across regions.
- Near-real-time data sync — provides data durability across regions.
- Configurable replication lag tolerance.

---

## Security

### Authentication

| Method | Description |
|---|---|
| **Connection String (SAS)** | Shared Access Signature policy — key-based, for legacy/non-AAD scenarios |
| **Entra ID (RBAC)** | Recommended — Azure Event Hubs Data Owner/Sender/Receiver roles |
| **Managed Identity** | Keyless auth for Azure-hosted services |

```python
from azure.eventhub import EventHubProducerClient
from azure.identity import DefaultAzureCredential

# Managed identity (keyless)
producer = EventHubProducerClient(
    fully_qualified_namespace="mynamespace.servicebus.windows.net",
    eventhub_name="myeventhub",
    credential=DefaultAzureCredential()
)
```

### Network Security

- **Public**: Default — accessible from internet with auth.
- **IP firewall rules**: Allow specific IP ranges.
- **Virtual Network service endpoints**: Restrict to specific VNet subnets.
- **Private Endpoint**: Fully private — namespace only accessible from within VNet. DNS via Private DNS Zone `privatelink.servicebus.windows.net`.

---

## Publishing Events

### Python SDK

```python
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential

producer = EventHubProducerClient(
    fully_qualified_namespace="mynamespace.servicebus.windows.net",
    eventhub_name="myeventhub",
    credential=DefaultAzureCredential()
)

with producer:
    # Batch send for efficiency
    event_batch = producer.create_batch(partition_key="customer-123")

    for i in range(100):
        event = EventData(f'{{"customerId": "customer-123", "action": "purchase", "seq": {i}}}')
        event.properties = {"source": "web-app", "region": "us-east"}
        event_batch.add(event)

    producer.send_batch(event_batch)
```

### Consuming Events

```python
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
import asyncio

checkpoint_store = BlobCheckpointStore.from_connection_string(
    "<storage-connection-string>", container_name="checkpoints"
)

client = EventHubConsumerClient(
    fully_qualified_namespace="mynamespace.servicebus.windows.net",
    eventhub_name="myeventhub",
    consumer_group="analytics-consumer-group",
    checkpoint_store=checkpoint_store,
    credential=DefaultAzureCredential()
)

async def on_event(partition_context, event):
    print(f"Partition: {partition_context.partition_id}")
    print(f"Offset: {event.offset}, SequenceNumber: {event.sequence_number}")
    print(f"Body: {event.body_as_str()}")
    await partition_context.update_checkpoint(event)  # save offset

async def main():
    async with client:
        await client.receive(on_event=on_event, starting_position="-1")  # -1 = earliest

asyncio.run(main())
```

---

## Integration with Azure Services

| Service | Integration |
|---|---|
| **IoT Hub** | IoT Hub built on Event Hubs — IoT Hub's event routing endpoint is Event Hubs |
| **Stream Analytics** | Event Hubs as input source for real-time SQL processing |
| **Azure Functions** | Event Hubs trigger — scale to partition count, checkpoint managed |
| **Azure Databricks** | Structured Streaming connector (`readStream.format("eventhubs")`) |
| **Azure Monitor** | Export diagnostic logs and platform metrics to Event Hubs |
| **Logic Apps** | Event Hubs trigger and action connectors |
| **Data Factory** | Event Hubs as source (copy or event trigger) |
