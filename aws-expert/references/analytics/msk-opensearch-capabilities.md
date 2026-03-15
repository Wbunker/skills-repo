# AWS MSK & OpenSearch — Capabilities Reference
For CLI commands, see [msk-opensearch-cli.md](msk-opensearch-cli.md).

## Amazon MSK

**Purpose**: Fully managed Apache Kafka service; handles control-plane operations (cluster provisioning, patching, scaling) while you manage producers, consumers, and topics.

### Cluster Types

| Type | Description |
|---|---|
| **Provisioned** | You specify broker count, instance type, and storage; full control over configuration |
| **Serverless** | MSK manages broker nodes and scales automatically; no capacity planning required |

### Key Concepts

| Concept | Description |
|---|---|
| **Broker node** | Apache Kafka broker; MSK creates at least one per Availability Zone |
| **ZooKeeper node** | Coordination service for Kafka metadata (legacy); MSK manages these |
| **KRaft controller** | Replaces ZooKeeper for metadata management; included at no extra cost in newer clusters |
| **Topic** | Logical stream of records; divided into partitions |
| **Consumer group** | Set of consumers that coordinate to read a topic; each partition assigned to one consumer |

### Broker Instance Types (Provisioned)

| Type | Description |
|---|---|
| **Standard brokers** | General-purpose; kafka.m5.large through kafka.m5.4xlarge and others |
| **Express brokers** | Higher throughput; kafka.express.*; faster scaling |

### Key Features

| Feature | Description |
|---|---|
| **MSK Connect** | Managed Kafka Connect service; run source and sink connectors without managing workers |
| **MSK Replicator** | Fully managed cross-region or same-region replication between MSK Provisioned clusters |
| **Tiered storage** | Offload older log segments to S3; reduces broker storage costs; consumers can still read tiered data |
| **Auto-scaling** | Scale broker storage automatically based on utilization thresholds |
| **Automatic recovery** | Detect and recover from broker failures; replacement broker inherits same IP and storage |

### Authentication Methods

| Method | Description |
|---|---|
| **IAM access control** | IAM-based authentication and authorization; recommended for AWS-native workloads |
| **SASL/SCRAM** | Username/password authentication stored in AWS Secrets Manager |
| **TLS mutual auth** | Certificate-based client authentication using ACM Private CA |
| **Unauthenticated** | No authentication; use only in tightly controlled network environments |

---

## Amazon OpenSearch Service

**Purpose**: Managed service for deploying, operating, and scaling OpenSearch and legacy Elasticsearch clusters for log analytics, full-text search, and real-time application monitoring.

### Deployment Modes

| Mode | Description |
|---|---|
| **Domain** | Managed OpenSearch/Elasticsearch cluster; you choose instance types, count, and storage |
| **Serverless** | Fully managed compute and storage; scales automatically; organized into collections |

### Core Concepts (Domain)

| Concept | Description |
|---|---|
| **Domain** | Synonymous with a cluster; defines instance types, count, storage, network, and security settings |
| **Index** | Collection of documents with a shared mapping (schema) |
| **Shard** | Subdivision of an index; distributed across nodes for parallelism and fault tolerance |
| **Replica** | Copy of a shard; provides redundancy and read scaling |
| **Dedicated master node** | Manages cluster state; offloads cluster management from data nodes |

### Storage Tiers

| Tier | Description |
|---|---|
| **Hot (instance storage / EBS)** | Active data on data nodes; lowest latency |
| **UltraWarm** | S3-backed warm storage; read-only; much lower cost than hot; for infrequently accessed data |
| **Cold storage** | Even cheaper S3-backed storage; data is detached (must be migrated to UltraWarm to query) |

### Key Features

| Feature | Description |
|---|---|
| **ISM (Index State Management)** | Policy-based lifecycle automation: rollover, delete, migrate to UltraWarm/cold |
| **Alerting** | Define monitors (query-based or anomaly-based) and triggers to send notifications |
| **Anomaly Detection** | ML-based detection of anomalies in time-series data using Random Cut Forest |
| **k-NN (k-Nearest Neighbor)** | Vector similarity search; store and query embeddings for semantic search and ML workloads |
| **OpenSearch Dashboards** | Built-in visualization UI (successor to Kibana); included with every domain |
| **Data Prepper** | Managed ingestion pipeline server; transforms and routes data into OpenSearch (ECS/Kubernetes) |
| **Ingestion pipelines** | Native OpenSearch Ingestion: managed Data Prepper pipelines without running your own server |
| **Fine-grained access control** | Index-, document-, and field-level security using roles and role mappings |
| **Cross-cluster search** | Query across multiple OpenSearch domains simultaneously |
