# Building Data Pipelines with Kafka Connect
## Chapter 8: Kafka Connect, Connectors, Transforms, Data Pipeline Design

---

## Why Kafka Connect

Building custom producers/consumers for every data source and sink is expensive and repetitive. Kafka Connect provides a **standardized framework** for integrating Kafka with external systems:

```
External Systems:                    Kafka Connect Framework:
─────────────────                    ─────────────────────────
MySQL, Postgres    → SOURCE          Workers (JVM processes)
MongoDB, Cassandra → CONNECTOR  →    Connectors (config + logic)
S3, GCS, ADLS      → SINK            Tasks (parallel work units)
Elasticsearch      ← CONNECTOR  ←    Converters (serialization)
Snowflake, BigQuery                  Transforms (SMTs)
Salesforce, SAP
```

Kafka Connect handles:
- Offset management (tracking what has been ingested)
- Worker fault tolerance and horizontal scaling
- Schema evolution
- REST API for lifecycle management
- Exactly-once delivery (for supported connectors)

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                  KAFKA CONNECT CLUSTER                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  WORKER 1              WORKER 2              WORKER 3│   │
│  │  ──────────            ──────────            ────────│   │
│  │  Source Task 1         Source Task 2         Sink T1 │   │
│  │  Source Task 2         Sink Task 1           Sink T2 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Connectors run as tasks distributed across workers         │
│  Workers store state in Kafka topics (config/offsets/status)│
└─────────────────────────────────────────────────────────────┘
```

**Worker**: JVM process that runs connector tasks. Workers form a cluster and distribute task load. Workers are stateless — all state (connector config, task offsets, connector status) is stored in Kafka topics.

**Connector**: Logical configuration defining what to connect and how. A connector splits its work into one or more **tasks**.

**Task**: The actual unit of work — a source task reads from an external system and produces to Kafka; a sink task consumes from Kafka and writes to an external system.

### Internal Kafka Topics

Connect workers store state in internal Kafka topics (configured on startup):
```properties
config.storage.topic=connect-configs
offset.storage.topic=connect-offsets
status.storage.topic=connect-status
group.id=connect-cluster
```

These topics should have `replication.factor=3` for production.

---

## Running Kafka Connect

### Standalone Mode

Single worker; stores offsets in a local file. Good for development/testing only.

```bash
bin/connect-standalone.sh config/connect-standalone.properties \
    connector1.properties connector2.properties
```

### Distributed Mode (Production)

Multiple workers; all state in Kafka. Workers auto-distribute tasks.

```bash
bin/connect-distributed.sh config/connect-distributed.properties
```

Workers join via `group.id`; any number of workers can be added/removed.

### REST API

```bash
# List connectors
GET /connectors

# Create connector
POST /connectors
{
  "name": "postgres-source",
  "config": { "connector.class": "...", ... }
}

# Get connector status
GET /connectors/postgres-source/status

# Pause / resume
PUT /connectors/postgres-source/pause
PUT /connectors/postgres-source/resume

# Delete connector
DELETE /connectors/postgres-source

# Restart a failed task
POST /connectors/postgres-source/tasks/0/restart
```

---

## Source Connectors

Source connectors read from external systems and produce to Kafka.

### JDBC Source Connector (Database → Kafka)

```json
{
  "name": "postgres-orders-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://db:5432/orders",
    "connection.user": "kafka_user",
    "connection.password": "${file:/secrets.properties:db.password}",
    "mode": "timestamp+incrementing",
    "timestamp.column.name": "updated_at",
    "incrementing.column.name": "id",
    "table.whitelist": "orders,order_items",
    "topic.prefix": "postgres.orders.",
    "poll.interval.ms": "5000",
    "tasks.max": "4"
  }
}
```

**Modes:**
- `bulk` — read entire table each poll (expensive; use for small tables)
- `incrementing` — track max ID; fetch new rows only
- `timestamp` — track max timestamp; fetch rows updated since last poll
- `timestamp+incrementing` — both columns for correctness (handles same-timestamp rows)

### Debezium CDC Connector (Database → Kafka via CDC)

Debezium reads the database transaction log (binary log, WAL, redo log) for exactly-once change capture:

```json
{
  "name": "debezium-postgres",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "debezium",
    "database.dbname": "inventory",
    "database.server.name": "dbserver1",
    "table.include.list": "public.orders",
    "plugin.name": "pgoutput"
  }
}
```

**Output**: Events contain `before` and `after` fields with the full row state:
```json
{
  "op": "u",                     // u=update, c=create, d=delete, r=read (snapshot)
  "before": {"id": 1, "status": "pending"},
  "after":  {"id": 1, "status": "shipped"},
  "source": {"ts_ms": 1690000000000, "lsn": 12345}
}
```

### File Source, S3 Source, and Others

Popular connectors available from Confluent Hub, Apache, and community:
- S3 Source (read files from S3 → Kafka)
- Salesforce Source, ServiceNow Source
- HTTP Source (poll REST APIs)
- MQ Source (ActiveMQ, IBM MQ, RabbitMQ)

---

## Sink Connectors

Sink connectors consume from Kafka and write to external systems.

### S3 Sink Connector (Kafka → S3)

```json
{
  "name": "s3-sink-orders",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "s3.region": "us-east-1",
    "s3.bucket.name": "my-data-lake",
    "s3.part.size": "67108864",
    "topics": "postgres.orders.orders",
    "flush.size": "10000",
    "rotate.interval.ms": "300000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "tasks.max": "4"
  }
}
```

This is a common building block for **Kafka → Data Lake** pipelines. Files are written as Parquet, partitioned by date/hour.

### Elasticsearch Sink, JDBC Sink, BigQuery Sink, Snowflake Sink

Most popular data stores have maintained connectors. Key configs to check:
- `batch.size` — records per write call
- `tasks.max` — parallel write tasks (limited by partition count)
- Error handling and dead letter queue configuration

---

## Single Message Transforms (SMTs)

SMTs modify records **in-flight** as they pass through a connector — no need to write custom code for common transformations.

```json
"transforms": "renameField,addTimestamp",
"transforms.renameField.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
"transforms.renameField.renames": "order_id:orderId,cust_id:customerId",
"transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
"transforms.addTimestamp.timestamp.field": "processedAt"
```

### Common Built-in SMTs

| SMT | Purpose |
|-----|---------|
| `ReplaceField` | Rename, whitelist, or blacklist fields |
| `InsertField` | Add fields (topic name, partition, offset, timestamp, static value) |
| `MaskField` | Replace field value with null or zeros (PII masking) |
| `ExtractField` | Pull a single field out of a struct or map |
| `ValueToKey` | Promote a value field to become the record key |
| `TimestampConverter` | Convert timestamp format (epoch → string, etc.) |
| `Filter` | Drop records matching a predicate |
| `RegexRouter` | Modify topic name using regex |
| `Flatten` | Flatten nested structs to dot-notation fields |

### Limitations of SMTs

SMTs operate on one record at a time and cannot:
- Join records from multiple topics
- Aggregate records
- Perform stateful operations

For complex transformations, use **Kafka Streams** or **ksqlDB** instead.

---

## Schema Registry Integration

Kafka Connect integrates with Schema Registry to:
- Automatically register schemas when producing (source connectors)
- Validate schemas when consuming (sink connectors)
- Track schema evolution

```json
"key.converter": "io.confluent.kafka.connect.avro.AvroConverter",
"key.converter.schema.registry.url": "http://schema-registry:8081",
"value.converter": "io.confluent.kafka.connect.avro.AvroConverter",
"value.converter.schema.registry.url": "http://schema-registry:8081"
```

For JSON without schema registry:
```json
"value.converter": "org.apache.kafka.connect.json.JsonConverter",
"value.converter.schemas.enable": "false"
```

---

## Error Handling and Dead Letter Queues

```json
"errors.tolerance": "all",              // none=fail fast; all=skip errors
"errors.log.enable": "true",            // log all errors
"errors.log.include.messages": "true",  // include original message in log
"errors.deadletterqueue.topic.name": "orders-dlq",
"errors.deadletterqueue.topic.replication.factor": "3",
"errors.deadletterqueue.context.headers.enable": "true"  // add error context headers
```

With DLQ enabled, failed records go to the DLQ topic with headers explaining the failure. Operators can inspect and replay from the DLQ.

---

## Data Pipeline Design Patterns

### Pattern 1: Database → Kafka → Data Lake (CDC)

```
Postgres (operational) → [Debezium CDC] → Kafka → [S3 Sink] → S3 (Parquet/Iceberg)
                                                  → [ES Sink] → Elasticsearch
                                                  → [DW Sink] → Snowflake
```

Single Kafka topic serves multiple sinks without extra load on the source database.

### Pattern 2: Event-Driven Microservices

```
Service A → produce to "orders" topic
         ↓
Service B → consume "orders" → produce to "fulfillment" topic
         ↓
Service C → consume "fulfillment" → produce to "notifications" topic
```

Services are fully decoupled — each evolves independently.

### Pattern 3: Log Aggregation

```
App servers → [File Source / Beats] → Kafka → [ES Sink] → Elasticsearch + Kibana
                                             → [S3 Sink] → S3 (long-term archive)
```

### Pattern 4: Real-Time + Batch (Lambda-like with Kafka)

```
Events → Kafka → [Kafka Streams] → Real-time aggregates → Serving layer
               → [S3 Sink]      → S3 (raw events)      → Spark batch jobs
```
