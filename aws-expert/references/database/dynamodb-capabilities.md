# AWS DynamoDB — Capabilities Reference
For CLI commands, see [dynamodb-cli.md](dynamodb-cli.md).

## Amazon DynamoDB

**Purpose**: Serverless, fully managed NoSQL key-value and document database delivering single-digit millisecond performance at any scale; no servers to provision, patch, or manage.

### Key Concepts

| Concept | Description |
|---|---|
| **Table** | Collection of items; schema-less except for the primary key |
| **Item** | Single record in a table; equivalent to a row; up to 400 KB |
| **Attribute** | Name-value pair within an item; equivalent to a column; supports nested up to 32 levels |
| **Partition Key** | Required; DynamoDB hashes it to determine storage partition; must be scalar (String, Number, Binary) |
| **Sort Key** | Optional; combined with partition key to form a composite primary key; items with same partition key ordered by sort key |
| **GSI (Global Secondary Index)** | Alternate partition/sort key; spans entire table; up to 20 per table; eventually consistent reads only |
| **LSI (Local Secondary Index)** | Same partition key as table; alternate sort key; up to 5 per table; must be defined at table creation; supports strongly consistent reads |
| **DynamoDB Streams** | Ordered log of item-level changes; 24-hour retention; triggers Lambda; enables replication and CDC |
| **DAX (DynamoDB Accelerator)** | In-memory write-through cache cluster; microsecond read latency; API-compatible; no application code changes |
| **Global Tables** | Multi-active (multi-master) replication across Regions; 99.999% availability SLA |
| **TTL** | Epoch timestamp attribute; DynamoDB automatically deletes expired items at no extra cost |
| **Table Class** | Standard (default) or Standard-Infrequent Access (Standard-IA; lower storage cost, higher read/write cost) |

### Capacity Modes

| Mode | Description | Use Case |
|---|---|---|
| **On-Demand** | Pay per request; automatically handles any traffic level | Unpredictable or spiky traffic; new tables |
| **Provisioned** | Specify RCUs and WCUs; can overprovision; cheaper at steady load | Predictable, steady-state traffic |
| **Auto Scaling** | Adjusts provisioned capacity within min/max bounds based on target utilization | Predictable-but-variable traffic |

### Key Features

| Feature | Description |
|---|---|
| **Transactions** | `TransactWriteItems` and `TransactGetItems`; ACID across up to 100 items in multiple tables; 2× the cost of standard reads/writes |
| **PartiQL** | SQL-compatible query language for DynamoDB; batch operations supported |
| **Exports to S3** | Point-in-time export to S3 in DynamoDB JSON or Ion format; no table read capacity consumed |
| **DynamoDB Streams** | CDC log; 24-hour retention; power Lambda triggers, cross-region replication, audit trails |
| **DAX** | Write-through cache; microsecond reads; cluster-based (multi-node for HA) |
| **Global Tables** | Multi-active multi-region; last-writer-wins conflict resolution; requires on-demand or auto-scaling |
| **Point-in-time Recovery (PITR)** | Restore table to any second in the last 35 days; no performance impact |
| **Encryption at rest** | Default; choose AWS-owned key, AWS managed key, or CMK |
| **Fine-grained access control** | IAM policies with `dynamodb:LeadingKeys` condition to restrict access to own partition key items |

### When to Use DynamoDB

- High-traffic web, mobile, and gaming applications needing single-digit ms latency
- Serverless architectures (Lambda + DynamoDB = fully serverless data tier)
- Session stores, shopping carts, user profiles with simple access patterns
- IoT telemetry ingestion at high write rates
- Global applications needing multi-region active-active replication
