# AWS ElastiCache & MemoryDB — Capabilities Reference
For CLI commands, see [elasticache-memorydb-cli.md](elasticache-memorydb-cli.md).

## Amazon ElastiCache

**Purpose**: Fully managed in-memory caching service supporting Valkey, Redis OSS, and Memcached; sub-millisecond latency for read-heavy workloads and session/data caching.

### Engine Comparison

| Feature | Memcached | Redis OSS / Valkey |
|---|---|---|
| **Data types** | Simple strings/objects | Rich: strings, hashes, lists, sets, sorted sets, bitmaps, streams, geospatial |
| **Persistence** | None | RDB snapshots + AOF append-only file |
| **Replication** | None | Yes (primary + up to 5 replicas per shard) |
| **Automatic failover** | No | Yes (cluster mode enabled: required; disabled: optional) |
| **Multi-threading** | Yes | No (single-threaded core) |
| **Cluster mode** | Horizontal sharding (implicit) | Disabled (single shard) or Enabled (multiple shards) |
| **Global Datastore** | No | Yes |
| **Backup/restore** | Serverless only | Yes |
| **Data tiering (SSD)** | No | Yes (r6gd nodes, v6.2+) |
| **Auth / ACLs** | No | Auth token (v6.0+: Redis ACLs) |
| **Pub/Sub** | No | Yes |

### Key Concepts

| Concept | Description |
|---|---|
| **Replication Group** | One or more shards; each shard has a primary node and up to 5 read replicas |
| **Cluster Mode Disabled** | Single shard; scale vertically; replicas serve reads; simpler |
| **Cluster Mode Enabled** | Data sharded across up to 500 shards; online resharding supported (v3.2.10+) |
| **Global Datastore** | Cross-region replication for Redis OSS/Valkey; one primary region + up to 2 secondary regions; < 1 s replication lag |
| **Data Tiering** | Automatically move infrequently used data to SSD on r6gd nodes; extends effective memory |
| **Auth Token** | Password for Redis OSS clusters (pre-ACL); required when `TransitEncryptionEnabled` is set |
| **Serverless** | Auto-scaling ElastiCache; no node provisioning; available for Valkey 7.2, Redis OSS 7.1, Memcached 1.6.22+ |

### Key Features

| Feature | Description |
|---|---|
| **Multi-AZ with auto failover** | Promotes replica on primary failure; requires at least one replica; typically completes in < 60 s |
| **Read replicas** | Up to 5 per shard (Redis/Valkey); serve read traffic; can be in separate AZs |
| **Global Datastore** | Cross-region active-passive replication; promote secondary to primary for DR |
| **Backup and restore** | Manual and automated snapshots; restore to new cluster; Redis/Valkey only |
| **Data tiering** | Hot data in DRAM, warm data on NVMe SSD; reduces cost for large datasets with hot/cold access patterns |
| **Encryption** | In-transit (TLS) and at-rest (KMS); Auth token or ACL-based authentication |
| **Serverless** | Automatically adjusts capacity; charged per ElastiCache Processing Units (ECPUs) and GB stored |

### When to Use ElastiCache

- Database query result caching to reduce read load on RDS/Aurora
- Session storage for web applications
- Real-time leaderboards and counting (sorted sets)
- Pub/sub messaging and fan-out
- Rate limiting and distributed locking

---

## Amazon MemoryDB

**Purpose**: Durable, Redis OSS–compatible in-memory database designed for use as a primary database; eliminates the need for a separate cache layer in front of a persistent store.

### Key Concepts

| Concept | Description |
|---|---|
| **Multi-AZ transaction log** | All writes persisted to a durable, distributed transaction log across AZs before acknowledging; source of durability |
| **Cluster** | Sharded cluster of nodes; each shard has a primary and replicas |
| **Shard** | Subset of keyspace managed by one primary node; replicas provide read scale and failover |
| **Snapshot** | Point-in-time backup stored in S3 |

### Key Features

| Feature | Description |
|---|---|
| **Durability** | Multi-AZ transactional log ensures zero data loss on failover; data survives node restarts |
| **Redis OSS / Valkey compatibility** | Same data structures, APIs, and commands as Redis OSS; existing SDKs and tools work without changes |
| **High availability** | Automatic failover to replica on primary failure; fast recovery via transaction log replay |
| **Strong consistency** | Reads from primary are strongly consistent; in-memory primary + durable log = ACID-like guarantees |
| **Encryption** | In-transit (TLS) and at-rest (KMS); ACL-based authentication |

### MemoryDB vs ElastiCache

| | MemoryDB | ElastiCache |
|---|---|---|
| **Primary role** | Primary database (durable) | Cache layer in front of another DB |
| **Durability** | Multi-AZ transaction log; zero data loss | Optional persistence (RDB/AOF); possible data loss on failure |
| **Consistency** | Strong (primary reads) | Eventual (replica reads) |
| **Use when** | Redis IS your database of record | Caching in front of RDS, DynamoDB, etc. |
| **Cost** | Higher | Lower |
