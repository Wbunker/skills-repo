# Memorystore — Capabilities Reference

## Purpose

Memorystore is Google Cloud's fully managed in-memory data store service. It provides managed Redis and Memcached instances, eliminating the operational burden of managing cache infrastructure (patching, replication, failover, monitoring). Memorystore instances are accessible only via VPC-internal private IP — there is no public internet endpoint.

---

## Memorystore for Redis

### Redis Versions and Tiers

| Product | Versions | Tier | Description |
|---|---|---|---|
| Memorystore for Redis | 6.x, 7.x | Basic | Single node; no replication; no automatic failover. For dev/test only. |
| Memorystore for Redis | 6.x, 7.x | Standard | Primary + one replica in separate zones; automatic failover within ~2 minutes; 99.9% SLA. |
| Memorystore for Redis Cluster | 7.0 | N/A (cluster only) | Horizontally sharded cluster; multiple shards; each shard has primary + replica; scales to 300+ GB and 1M+ QPS. |

### Redis Instance Sizes

Standard and Basic instances are configured with a memory capacity:
- Minimum: 1 GB
- Maximum: 300 GB (for single-instance Standard tier)

Redis Cluster scales horizontally by adding shards:
- Each shard: ~12 GB usable
- Minimum: 3 shards (36 GB)
- Maximum: 250 shards (~3 TB)
- Each shard has a primary node and one replica for HA

### Redis Features

| Feature | Description |
|---|---|
| Data structures | Strings, hashes, lists, sets, sorted sets, bitmaps, hyperloglogs, streams, geospatial indexes, pub/sub |
| Pub/Sub | Redis PUBLISH/SUBSCRIBE channels. Used for real-time messaging. Not persistent. |
| Lua scripting | Execute Lua scripts atomically via EVAL command |
| Transactions | MULTI/EXEC blocks for atomic command groups |
| Keyspace notifications | Notify clients of key events (expiry, mutations) via pub/sub |
| Persistence - RDB | Periodic snapshots to disk. Enabled on Standard tier. Configurable interval. |
| Persistence - AOF | Append-only file; logs every write. More durable but slower. Available on Standard tier. |
| AUTH | Redis AUTH password. Enforced on all Memorystore instances (required). |
| TLS | In-transit encryption. Configurable (disabled by default; enable for compliance). |
| Read replicas | Memorystore for Redis Cluster supports read replicas per shard. |
| Import/Export | Import RDB files from Cloud Storage; export RDB snapshots to Cloud Storage. |

### High Availability (Standard Tier)

- Primary instance + one replica in a different zone within the same region.
- Automatic failover when primary fails. Failover time: ~1–2 minutes.
- The replica is promoted to primary automatically; a new replica is created.
- During failover, connections are dropped — applications must implement reconnection logic.
- Standard tier SLA: 99.9%.
- RDB persistence enabled by default on Standard tier.

### Redis Cluster (Memorystore for Redis Cluster)

Redis Cluster uses consistent hashing to distribute keys across shards:
- 16,384 hash slots divided among shards.
- Clients must use a cluster-aware client library (redis-py-cluster, Lettuce, etc.).
- Multi-key operations (MGET, MSET, transactions) require all keys to be in the same hash slot (use hash tags `{tag}` to co-locate keys).
- No cross-slot transactions.
- Scale shards up/down with a `gcloud` command — Memorystore handles re-sharding automatically.

### Persistence Options

| Mode | Description | Durability | Performance Impact |
|---|---|---|---|
| None (Basic tier) | No persistence. All data lost on restart. | None | Best |
| RDB snapshots | Periodic full snapshot to disk. Configurable: hourly, every 6h, every 12h, every 24h. | Data loss since last snapshot | Low |
| AOF (every second) | Write to AOF every second. Up to 1 second of data loss. | High | Moderate |
| AOF (every write) | Write to AOF on every command. Minimal data loss. | Very high | Higher |

---

## Memorystore for Memcached

### Features

| Feature | Value |
|---|---|
| Versions | Memcached 1.5, 1.6 |
| Multi-node | 1–20 nodes per instance |
| Node memory | 1–5 GB per node |
| Max total memory | 5 GB × 20 nodes = 100 GB |
| Auto-discovery | Built-in Memcached auto-discovery via a metadata IP |
| Protocol | Standard Memcached protocol |
| Persistence | None (cache only) |
| Replication | None |
| Failover | None (if a node fails, its data is lost; cache miss occurs) |

Memcached is a distributed cache only — no data structures beyond string/binary values, no persistence, no pub/sub, no scripting.

---

## Redis vs. Memcached — Decision Guide

| Factor | Use Redis | Use Memcached |
|---|---|---|
| Data structures | Need hashes, lists, sorted sets, streams | String/binary values only |
| Persistence | Need RDB or AOF for cache durability | Pure cache, data loss acceptable |
| High availability | Need automatic failover | Can tolerate node loss (cache miss ok) |
| Pub/Sub messaging | Need lightweight pub/sub | Not needed |
| Lua scripting | Need atomic custom logic | Not needed |
| Lua-free atomic ops | INCR, DECR, SETNX | Not needed |
| Horizontal scale | Use Redis Cluster | Multi-node Memcached |
| Simplicity | Standard key-value get/set | Memcached is simpler to operate |
| GCP default choice | Preferred (richer, HA) | Only if existing Memcached apps |

---

## Connection Architecture

### VPC-Internal Only

Memorystore instances are not accessible from the internet. They use a private IP in your VPC (via VPC peering with the Memorystore managed service network).

- GCE instances connect directly via private IP.
- GKE pods connect directly (GKE is in the same VPC).
- Cloud Run / Cloud Functions require **Serverless VPC Access** (VPC connector) to reach Memorystore private IP.
- App Engine standard requires VPC connector. App Engine flexible connects directly.

### Connection from Cloud Run / Functions

```bash
# Create a VPC connector (required for serverless → Memorystore)
gcloud compute networks vpc-access connectors create my-vpc-connector \
  --region=us-central1 \
  --subnet=my-subnet \
  --subnet-project=my-project \
  --min-instances=2 \
  --max-instances=10

# Deploy Cloud Run service with VPC connector
gcloud run deploy my-service \
  --vpc-connector=my-vpc-connector \
  --vpc-egress=private-ranges-only \
  --set-env-vars=REDIS_HOST=10.100.0.3,REDIS_PORT=6379 \
  --region=us-central1 \
  --image=gcr.io/my-project/my-app
```

---

## Use Cases

| Use Case | Redis Feature | Notes |
|---|---|---|
| Session storage | String keys with TTL | `SET session:abc <data> EX 3600` |
| Rate limiting | INCR + TTL on IP/user keys | Atomic increment; expiry resets counter |
| Cache-aside | GET + SET with EX | Reduce database load |
| Leaderboards | Sorted sets (ZADD, ZRANK) | `ZADD leaderboard 1500 user:alice` |
| Real-time pub/sub | PUBLISH / SUBSCRIBE | Lightweight message passing |
| Distributed locks | SET NX PX (or Redlock) | `SET lock:resource uuid NX PX 30000` |
| Task queues | Lists (LPUSH, BRPOP) | Producer/consumer queues |
| Geospatial queries | GEOADD, GEODIST, GEORADIUS | Location-based lookups |
| Real-time analytics | HyperLogLog for cardinality | Approximate unique count at low memory |
| ML feature serving | Hash per entity | `HGETALL features:user:12345` |

---

## Important Constraints

- **VPC-only access**: No public endpoint. All clients must be in the same VPC (or use Serverless VPC Access for serverless).
- **Single region**: Memorystore instances are regional. No cross-region replication. Plan for regional failure with application-level fallback to the database.
- **Redis AUTH is required**: Memorystore always enables authentication. The AUTH string is generated by Google and must be used by all connecting clients.
- **Maintenance windows**: Memorystore applies updates during maintenance windows. Standard tier performs rolling updates (failover to replica); Basic tier has downtime.
- **Persistence on Standard tier only**: Basic tier has no RDB or AOF. Do not store data in Basic tier that cannot be reconstructed from the database.
- **Redis Cluster multi-key limitations**: Multi-key operations across different hash slots are not supported. Use hash tags `{tag}` in key names to co-locate related keys on the same slot.
- **Import/Export format**: Import and export use RDB format only (Redis Database file). TLS must be disabled for import/export operations.
- **Node count changes in Memcached**: Adding/removing nodes does not automatically redistribute keys. Clients using consistent hashing will remap keys; clients using modulus hashing will experience a high cache miss rate on reconfiguration.
- **Max connection count**: Redis Basic: ~65,000 connections per instance; Standard: same. Connection pooling is recommended (use redis-py connection pool, Lettuce pool, etc.).
