# Azure Cache for Redis — Capabilities Reference
For CLI commands, see [redis-cli.md](redis-cli.md).

## Azure Cache for Redis

**Purpose**: Fully managed in-memory data store based on open-source Redis. Provides sub-millisecond latency for caching, session management, real-time leaderboards, message brokering, and distributed locking patterns.

### Tier Comparison

| Tier | Nodes | Replication | Cluster | Persistence | VNet | Geo-replication | Redis Modules | Use Case |
|---|---|---|---|---|---|---|---|---|
| **Basic** | 1 | None | No | No | No | No | No | Dev/test only; no SLA |
| **Standard** | 2 (primary + replica) | Yes | No | No | No | Passive only | No | Production with HA; most workloads |
| **Premium** | 2+ (with shards) | Yes | Yes (up to 10 shards) | RDB + AOF | Yes (VNet injection) | Passive (geo-replication) | No | High-throughput; compliance; geo-DR |
| **Enterprise** | 3+ (cluster) | Yes | Yes (unlimited) | RDB + AOF | Private Endpoint | Active geo-replication | Yes (RediSearch, RedisJSON, etc.) | Mission-critical; full Redis Enterprise features |
| **Enterprise Flash** | 3+ | Yes | Yes | RDB + AOF | Private Endpoint | Active geo-replication | Yes | Large datasets; cost-efficient; NVMe-backed |

### Capacity and Sizing

| Tier | Cache Size Options |
|---|---|
| **Basic / Standard** | C0 (250 MB) → C6 (53 GB) |
| **Premium** | P1 (6 GB) → P5 (120 GB); clustered: multiply by shard count |
| **Enterprise** | E10 (12 GB) → E200 (200+ GB); clustered for larger sizes |
| **Enterprise Flash** | F300 (345 GB flash) → F1500 (1,455 GB); RAM + NVMe flash tiering |

---

## High Availability

- **Basic**: no HA; single node; avoid for production
- **Standard**: primary + replica; automatic failover; ~20–30 seconds for failover; within same datacenter
- **Premium**: zone redundancy option — replicas placed in different AZs; protects against AZ failure
- **Enterprise/Enterprise Flash**: 3-node minimum cluster per region; built-in HA; automatic sharding
- All tiers except Basic are covered by Microsoft SLA (99.9%+)

---

## Clustering

### Standard Tier
- No clustering; single Redis instance; max 53 GB per cache

### Premium Tier Clustering
- Up to 10 shards; each shard has primary + replica
- Data partitioned across shards using key hash slots (16,384 slots total)
- Commands must target a single shard (multi-key operations limited to same slot via hash tags: `{user}:profile` + `{user}:session`)
- Scale out: add shards; scale up: increase shard size

### Enterprise Tier Clustering
- OSS cluster mode (default): clients must handle cluster redirects
- Enterprise cluster mode: proxy handles redirects transparently; works with non-cluster-aware clients
- No shard limit; linear scale-out

---

## Persistence

### RDB Snapshots (Redis Database)

- Point-in-time snapshots saved to Azure Storage at configurable intervals
- Intervals: 1 hour, 6 hours, 12 hours (Premium); configurable in Enterprise
- On restart: load last snapshot; data since last snapshot may be lost
- Best for: tolerance for some data loss; fast restart

### AOF (Append-Only File)

- Every write command appended to file; full durability
- `appendfsync everysec` (default): sync to disk every second; lose at most 1 second of data
- `appendfsync always`: sync after every write; highest durability; lower throughput
- Higher write overhead than RDB
- Premium tier: AOF stored in separate Premium storage account

### Combined RDB + AOF

- Both enabled: AOF used for restart (more current); RDB for faster initial load if AOF corrupt

---

## Geo-Replication

### Passive Geo-Replication (Premium Tier)

- Link two Premium Redis caches in different regions
- Primary (linked primary) → Secondary (linked secondary)
- Secondary is read-only; data replicated asynchronously
- Manual failover: unlink and promote secondary; requires application connection string update
- Use case: DR; read offload in secondary region
- Cannot be combined with clustering in Standard model

### Active Geo-Replication (Enterprise Tier)

- Multi-active: write to any participating region; conflicts resolved automatically
- Up to 5 regions per geo-replication group
- Sub-second replication latency between regions
- Each region serves reads and writes locally
- Use case: globally distributed active-active applications with multi-region writes
- Requires Enterprise or Enterprise Flash tier

---

## Redis Modules (Enterprise Tier Only)

| Module | Description | Use Cases |
|---|---|---|
| **RediSearch** | Full-text search engine; secondary indexing on Redis data | Search, autocomplete, faceted filtering, document search |
| **RedisJSON** | Native JSON document storage and atomic operations | JSON documents; avoid serialize/deserialize overhead |
| **RedisTimeSeries** | Time-series data structure; downsampling; aggregation | IoT metrics, monitoring, financial tick data |
| **RedisBloom** | Probabilistic data structures (Bloom filter, Cuckoo filter, Count-Min Sketch, Top-K) | Duplicate detection, cardinality estimation, frequency counting |
| **RedisGraph** (deprecated) | Graph database on Redis | Property graphs (being replaced by FalkorDB) |

---

## Network Security

| Option | Availability | Description |
|---|---|---|
| **Public endpoint** | All tiers | Access via public IP + SSL; firewall rules for IP allowlisting |
| **VNet injection** | Premium only | Server deployed in customer VNet; no public IP; access via VNet/peering |
| **Private Endpoint** | Enterprise, Enterprise Flash, Standard, Premium | Private IP in customer VNet; coexists with public endpoint |
| **TLS** | All tiers | TLS 1.2+ required; TLS 1.0/1.1 deprecated |

- Access keys rotated via Azure Portal, CLI, or Key Vault rotation
- Microsoft Entra ID authentication (token-based) available (preview in some tiers)
- Disable non-TLS port (6379) in production; use SSL port 6380

---

## Common Usage Patterns

### Cache-Aside (Lazy Loading)

```
1. App checks Redis cache for data
2. Cache miss → app reads from database
3. App writes result to Redis with TTL
4. Future reads served from cache
```

Best for read-heavy workloads; stale data possible during TTL window.

### Write-Through

```
1. App writes to Redis
2. Simultaneously writes to database
3. Cache always in sync with database
```

No stale reads; higher write latency; use for write-heavy data requiring consistency.

### Session Store

- Store user session data in Redis with TTL equal to session timeout
- Stateless app servers; horizontal scaling without sticky sessions
- Use Redis key prefix by user/session ID

### Pub/Sub Messaging

- Publisher sends message to channel; subscribers receive without polling
- Fire-and-forget; no message persistence (unlike Streams)
- Use for real-time notifications, cache invalidation signals

### Redis Streams

- Persistent, ordered message log; consumer groups; acknowledge semantics
- More durable than Pub/Sub; consumers can replay from offset
- Use for event sourcing, decoupled microservice communication

### Distributed Lock (Redlock)

- `SET key value NX EX <timeout>` — acquire lock atomically
- Release: check key value before DEL (avoid releasing another holder's lock)
- For distributed systems: use Redlock algorithm with multiple Redis instances

---

## Important Patterns & Constraints

- Basic tier has no SLA and no replica; **never use for production**
- Standard tier replica is not readable; it is a warm standby only
- Premium VNet injection is a deployment-time decision; cannot add VNet to existing non-VNet cache
- Enterprise tier uses a different architecture (Redis Enterprise from Redis Labs) with different operational model than open-source Redis
- Cluster mode: keys with different hash slots cannot be used in multi-key commands; use hash tags `{tag}` to co-locate related keys on same shard
- TTL precision: Standard/Premium use seconds precision; Enterprise supports milliseconds
- `KEYS` command blocks server in production — use `SCAN` for iterating keys
- Connection pool your Redis client; do not open a new connection per request
- Persistence (AOF) doubles I/O; size your cache and storage account accordingly
- Patch schedules: Azure applies patches weekly; configure maintenance window (Premium/Enterprise) to control timing
- maxmemory policy: set appropriate eviction policy (`allkeys-lru` for pure cache, `volatile-lru` for mixed persistent + cache)
