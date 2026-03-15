# AWS DocumentDB & Neptune — Capabilities Reference
For CLI commands, see [documentdb-neptune-cli.md](documentdb-neptune-cli.md).

## Amazon DocumentDB

**Purpose**: Fully managed document database with MongoDB compatibility; stores, queries, and indexes JSON data; designed for workloads moving MongoDB to the cloud.

### Key Concepts

| Concept | Description |
|---|---|
| **Cluster** | 0–16 instances + 1 cluster storage volume; separates compute and storage |
| **Storage volume** | Distributed; 6 copies across 3 AZs; auto-grows in 10 GiB increments up to 128 TiB |
| **Instance-based cluster** | Traditional cluster type; up to 15 read replicas; up to 15 replica instances for read scaling |
| **Elastic cluster** | Serverless cluster type for millions of reads/writes per second and petabyte-scale storage; sharded |
| **Reader endpoint** | Load-balances reads across all replica instances; no need to track individual replicas |
| **MongoDB compatibility** | Compatible with MongoDB 3.6, 4.0, and 5.0 APIs; uses the same drivers and tools |

### Key Features

| Feature | Description |
|---|---|
| **MongoDB API compatibility** | Run MongoDB 3.6, 4.0, and 5.0 workloads without code changes; same drivers, tools, and queries |
| **Storage replication** | 6 copies across 3 AZs; tolerates loss of up to 2 copies without affecting writes |
| **Read scaling** | Up to 15 replica instances; reader endpoint for load-balanced reads; replica lag typically single-digit ms |
| **Elastic clusters** | Sharded serverless DocumentDB; for petabyte-scale document workloads with millions of requests/s |
| **Automated failover** | Promotes a replica on primary failure; no cache recovery needed (database cache is isolated from process) |
| **Point-in-time recovery** | Restore to any second within backup retention period (up to 35 days); incremental and continuous |
| **Global clusters** | Cross-region replication for DocumentDB; read globally, write regionally |
| **Storage options** | Standard (pay per I/O) or I/O-Optimized (included I/O, higher instance cost) |
| **Encryption** | KMS encryption at rest; applies to cluster volume, backups, and replicas |

### When to Use DocumentDB

- Migrating existing MongoDB workloads to a managed AWS service
- Document-centric data models (catalogs, user profiles, content management)
- Need for automatic scaling of storage and read capacity
- Compliance-sensitive environments (FedRAMP authorized)

---

## Amazon Neptune

**Purpose**: Fully managed graph database service optimized for storing billions of relationships and querying with millisecond latency; supports both Property Graph and RDF graph models.

### Key Concepts

| Concept | Description |
|---|---|
| **Property Graph** | Graph model where vertices and edges have arbitrary key-value properties |
| **RDF (Resource Description Framework)** | W3C standard graph model using subject-predicate-object triples |
| **Gremlin** | Apache TinkerPop traversal language for Property Graph |
| **openCypher** | Neo4j-originated declarative query language for Property Graph (also supported on Neptune) |
| **SPARQL** | W3C standard query language for RDF graphs |
| **Cluster volume** | Shared distributed storage; auto-replicates across 3 AZs |
| **Neptune Replica** | Read-only instance; up to 15 per cluster; failover target |
| **Neptune ML** | Uses Graph Neural Networks (GNNs) via SageMaker to make predictions on graph data |
| **Neptune Analytics** | Separate in-memory analytics engine for running graph algorithms and low-latency analytics queries on large graphs |

### Key Features

| Feature | Description |
|---|---|
| **Multiple query languages** | Gremlin and openCypher for Property Graph; SPARQL for RDF; can query same PG data with both Gremlin and openCypher |
| **High availability** | > 99.99% availability; up to 15 read replicas; automatic failover |
| **Neptune ML** | Trains GNN models on graph structure; predictions accessible via Gremlin/openCypher; backed by SageMaker |
| **Neptune Analytics** | In-memory graph analytics engine; low-latency graph algorithms (PageRank, community detection, shortest path); works with Neptune DB or data lake |
| **Bulk loader** | Load data from S3 in CSV (Gremlin), N-Quads, or Turtle formats without impacting performance |
| **Streams** | Change log for graph mutations; enables CDC and event-driven architectures |
| **Encryption** | At-rest (KMS) and in-transit (TLS); VPC network isolation |

### When to Use Neptune

- Social networks, recommendations, fraud detection (highly connected relationship data)
- Knowledge graphs and ontologies (RDF/SPARQL)
- Network topology, IT infrastructure dependency mapping
- Drug discovery and life sciences (molecular relationship graphs)
- When SQL JOIN complexity makes relational queries impractical
