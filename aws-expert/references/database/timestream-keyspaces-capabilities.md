# AWS Timestream & Keyspaces — Capabilities Reference
For CLI commands, see [timestream-keyspaces-cli.md](timestream-keyspaces-cli.md).

## Amazon Timestream

**Purpose**: Fully managed, serverless time-series database for storing and analyzing trillions of time-series data points per day; built-in time series functions and automatic data lifecycle management.

### Key Concepts

| Concept | Description |
|---|---|
| **Record** | A single time-series data point: dimensions (metadata), measure name, measure value, and timestamp |
| **Dimension** | Metadata that identifies a time series (e.g., `region=us-east-1`, `server=web-01`); stored with every record |
| **Measure** | The actual metric value; a record can contain multiple measure values (multi-measure records) |
| **Memory store** | High-performance in-memory tier for recent, frequently queried data; configurable retention (hours to days) |
| **Magnetic store** | Cost-optimized storage tier for historical data; configurable retention (days to years) |
| **Scheduled query** | Pre-computed aggregation stored as a derived table; reduces query cost and latency for dashboards |
| **Database** | Logical container for tables; analogous to a schema |

### Key Features

| Feature | Description |
|---|---|
| **Dual-store architecture** | Memory store for recent data + magnetic store for historical data; unified SQL queries span both tiers automatically |
| **Automatic tiering** | Data automatically moves from memory to magnetic store based on per-table retention policies |
| **Time series SQL** | Built-in functions: time binning, interpolation, smoothing, approximation, percentiles, window functions |
| **Scheduled queries** | Compute aggregations on a schedule and write results to a derived table; reduces real-time query cost |
| **Multi-measure records** | Store multiple measures per record (e.g., CPU + memory + disk in one write); reduces storage and improves query performance |
| **Serverless scaling** | No capacity to provision; automatically scales compute and storage |
| **High durability** | Data replicated across ≥ 3 AZs; durably written to disk before acknowledging writes |
| **Integrations** | Ingest from IoT Core, Kinesis, MSK, Telegraf; visualize with QuickSight, Grafana; analyze with SageMaker |
| **Encryption** | At rest (KMS CMK supported for magnetic store) and in transit |

### When to Use Timestream

- IoT sensor data and device telemetry
- Application performance monitoring (APM) and observability metrics
- Industrial equipment monitoring and predictive maintenance
- DevOps metrics (infrastructure, container, and application metrics)
- Financial tick data and time-based analytics

---

## Amazon Keyspaces

**Purpose**: Serverless, managed Apache Cassandra–compatible database service; run Cassandra workloads with no infrastructure to provision or manage.

### Key Concepts

| Concept | Description |
|---|---|
| **Keyspace** | Highest-level namespace; analogous to a database schema in Cassandra |
| **Table** | Collection of rows within a keyspace; defined with CQL |
| **CQL (Cassandra Query Language)** | Cassandra-compatible query language; Keyspaces supports CQL 3.x |
| **Cassandra compatibility** | Compatible with Apache Cassandra 3.11 API and CQL; same drivers, tools, and existing application code |
| **Serverless** | No nodes to provision; pay per read/write request and storage; scales automatically |
| **On-Demand mode** | Pay per request; no capacity planning; for unpredictable traffic |
| **Provisioned mode** | Specify read/write capacity units; cost-effective for predictable workloads; supports auto scaling |

### Key Features

| Feature | Description |
|---|---|
| **Cassandra API compatibility** | Use existing Cassandra 3.11 application code, drivers (e.g., DataStax Java driver), and tools without changes |
| **Serverless scaling** | Automatically scales tables up/down based on application traffic; virtually unlimited throughput and storage |
| **On-demand and provisioned capacity** | On-demand for variable traffic; provisioned with auto scaling for steady-state workloads |
| **Point-in-time recovery** | Restore table to any second in the last 35 days |
| **Encryption at rest** | Automatic; AWS-owned, AWS managed, or CMK |
| **Multi-AZ replication** | Data replicated across 3 AZs within a region; 99.99% availability SLA |
| **Client-side timestamps** | Preserve original write timestamps when migrating data |

### When to Use Keyspaces

- Migrating Apache Cassandra workloads to AWS without infrastructure management
- High-throughput, low-latency workloads using wide-column data model
- Applications that use CQL and need a serverless, auto-scaling database
- Time-series and IoT data with known access patterns using partition keys
