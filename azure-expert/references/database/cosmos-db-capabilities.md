# Azure Cosmos DB — Capabilities Reference
For CLI commands, see [cosmos-db-cli.md](cosmos-db-cli.md).

## Azure Cosmos DB

**Purpose**: Globally distributed, multi-model NoSQL database service. Offers single-digit millisecond latency at the 99th percentile, elastic scaling of throughput and storage, and comprehensive SLAs covering availability, latency, consistency, and throughput.

### Hierarchy

```
Cosmos DB Account → Database → Container → Item
```

| Level | Description |
|---|---|
| **Account** | Top-level resource; chooses API, consistency level, regions; globally unique DNS name |
| **Database** | Logical namespace within account; share throughput across containers or per-container |
| **Container** | Core scalable unit; partition key required; stores items, triggers, stored procedures, UDFs |
| **Item** | Individual document/row/node/edge (terminology varies by API) |

---

## API Options

| API | Wire Protocol | Data Model | Use Case |
|---|---|---|---|
| **Core (SQL / NoSQL)** | Cosmos DB native | JSON documents with SQL query syntax | Default for new workloads; richest feature set; full Cosmos DB capabilities |
| **API for MongoDB** | MongoDB wire protocol | BSON documents | Migrate existing MongoDB apps; MongoDB drivers work natively |
| **API for Apache Cassandra** | CQL wire protocol | Wide-column (rows + columns) | Migrate Cassandra workloads; CQL queries |
| **API for Apache Gremlin** | Gremlin/WebSocket | Property graph (vertices + edges) | Social graphs, recommendation engines, network topology |
| **API for Table** | Azure Table Storage REST API | Key-value (partition key + row key) | Migrate from Azure Table Storage; global distribution upgrade |

- **Core (SQL) API is recommended for all new workloads** unless you have an existing wire-protocol dependency
- Each account is locked to one API; cannot change API after creation
- MongoDB, Cassandra, Gremlin, Table APIs are compatibility layers — not all features of native systems are supported

---

## Consistency Levels

Cosmos DB offers five well-defined consistency levels forming a spectrum between strong consistency and high availability:

| Level | Description | Read Latency | Throughput | Use Case |
|---|---|---|---|---|
| **Strong** | Linearizability; reads always see latest committed write | Higher | Lower | Financial transactions; critical inventory |
| **Bounded Staleness** | Reads lag behind writes by at most K operations or T time interval; ordered | Medium | Medium | Leaderboards; near-real-time feeds; global consistency with predictable staleness |
| **Session** (default) | Within a session: read-your-own-writes, monotonic reads, consistent prefix | Low | High | Most apps; single-user scenarios; shopping cart |
| **Consistent Prefix** | Reads never see out-of-order writes; no staleness guarantee | Low | High | Social media feeds; collaborative apps |
| **Eventual** | No ordering guarantee; highest availability; lowest latency | Lowest | Highest | Non-critical reads; social likes/favorites; DNS propagation |

- Default is **Session** consistency; optimal for most workloads
- Set at account level; override per request (only to weaker consistency)
- Strong consistency not available with multi-region write (multi-master)

---

## Capacity and Billing Modes

### Provisioned Throughput

- Measured in **Request Units per second (RU/s)**: normalized unit covering CPU, I/O, memory for any operation
- **Manual**: set specific RU/s; scale up/down manually or via autoscale
- **Autoscale**: set max RU/s; Cosmos automatically scales between 10% and 100% of max; billed at highest RU/s consumed per hour
- Minimum: 400 RU/s (database-level shared) or 1,000 RU/s (per container, indexed)

### Serverless

- Pay per operation (per RU consumed); no minimum throughput provisioning
- No guaranteed throughput; subject to account-level and container-level limits
- Best for: dev/test, bursty low-traffic workloads, new applications with unknown traffic
- Cannot use with multi-region

### Free Tier

- 1,000 RU/s + 25 GB storage per account; perpetually free
- Maximum 1 free tier account per Azure subscription

---

## Global Distribution

### Multi-Region Writes (Multi-Master)

| Feature | Description |
|---|---|
| **Read regions** | Replicate reads to any Azure region; low-latency local reads globally |
| **Write regions** | Single write region (default) or multi-region writes (any region accepts writes) |
| **Conflict resolution** | **Last-Write-Wins (LWW)**: system timestamp or custom `_ts` property; or **Custom**: stored procedure-based conflict resolution |
| **Transparent failover** | If write region fails, another region automatically promoted (with single write region); reads from any region continue |

- Multi-region writes requires Bounded Staleness or weaker consistency (not Strong)
- Automatic failover order configurable in account settings
- Data replicated asynchronously; consistency level determines read behavior

### Replication Latency

- 99th percentile write latency: <10ms (same region); replication lag: typically <15 minutes
- With Strong consistency: writes require acknowledgment from all regions in sync

---

## Partitioning

### Logical Partitions

- Defined by **partition key**: single property on items; all items with same partition key value in same logical partition
- Max logical partition size: 20 GB; 10,000 RU/s
- **Choose partition key wisely** — cannot change without recreating container; poor choice causes hot partitions

### Physical Partitions

- Cosmos DB maps logical partitions to physical partitions automatically (transparent to app)
- Physical partition: up to 50 GB storage; up to 10,000 RU/s; replicated across 4 replicas
- Splitting: automatic when limits approached; non-disruptive
- **Hierarchical partition keys**: up to 3-level hierarchy (e.g., tenantId → userId → sessionId) for better distribution

### Partition Key Best Practices

- High cardinality (many distinct values)
- Even distribution of reads and writes
- Avoid hot partitions (e.g., `userId` better than `country` for global social app)
- For large items per partition: use synthetic partition key or hierarchical partition key

---

## Indexing

- **Default**: all item properties indexed automatically (inverted index); no schema or index management required
- **Custom index policy**: include/exclude specific paths; reduces storage and RU cost for write-heavy workloads
- **Composite indexes**: required for ORDER BY across multiple properties or range filters + ORDER BY

```json
{
  "indexingMode": "consistent",
  "includedPaths": [{"path": "/*"}],
  "excludedPaths": [{"path": "/largePayload/*"}],
  "compositeIndexes": [
    [
      {"path": "/lastName", "order": "ascending"},
      {"path": "/firstName", "order": "ascending"}
    ]
  ],
  "spatialIndexes": [{"path": "/location/*", "types": ["Point", "Polygon"]}]
}
```

- **Lazy indexing** (deprecated; use consistent mode)
- **None mode**: disables indexing; only ID + partition key lookup; use for bulk imports

---

## Time to Live (TTL)

- Set TTL at container level (default TTL) and/or per-item level (`ttl` property)
- After TTL expiration, Cosmos automatically deletes items (background process; no RU cost)
- Use cases: session data, temporary shopping carts, event logs with retention

---

## Change Feed

- Ordered, persistent log of all inserts and updates (not deletes) to a container
- **Push model**: Change Feed Processor library (Java/.NET/Python) — multiple consumers, lease management, checkpointing
- **Pull model**: SDK `ReadChangeFeedAsync`; manual cursor management
- Use cases: event sourcing, CDC pipelines, cache invalidation, real-time materialized views
- Integrates natively with Azure Functions (Cosmos DB trigger) for serverless event processing
- Does not include DELETE operations by default; use soft-delete pattern (set a `deleted: true` flag + TTL)

---

## Integrated Vector Search

- Native vector search directly in Cosmos DB Core API (SQL API)
- Store vector embeddings alongside document data; no separate vector database
- Distance metrics: cosine, dotProduct, euclidean
- Use cases: RAG (Retrieval Augmented Generation) applications, semantic search, GenAI
- Query with `VectorDistance()` function in SQL; combine with scalar filters

---

## Azure Synapse Link (HTAP)

- Zero-ETL integration between Cosmos DB operational data and Azure Synapse Analytics
- **Analytical store**: automatic column-format copy of Cosmos data; updated continuously; no impact on transactional performance
- Query with Synapse Analytics (Spark or serverless SQL) for analytical workloads
- Eliminates need for ETL pipelines to analytics data warehouse
- Supports Core (SQL) and MongoDB APIs

---

## Important Patterns & Constraints

- Partition key is **immutable** — cannot change after container creation; plan schema carefully
- Cross-partition queries are supported but consume more RU/s; single-partition queries are most efficient
- Item max size: 2 MB
- Stored procedures, triggers, and UDFs run in JavaScript within a single partition scope
- Autoscale minimum is 10% of configured max (e.g., max 10,000 RU/s → minimum 1,000 RU/s billed)
- Serverless accounts cannot be converted to provisioned throughput (create new account)
- Multi-region write conflicts resolved with Last-Write-Wins by default; implement idempotent writes to avoid issues
- Cosmos DB does not support ACID transactions across multiple containers or accounts; use stored procedures within a partition for multi-document transactions
- When using Cosmos DB with Azure Functions, use change feed trigger to avoid polling; polling wastes RU/s
- SDK retry policies should handle 429 (TooManyRequests) with exponential backoff — never retry on same item without backoff
