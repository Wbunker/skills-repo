# Memorystore — CLI Reference

---

## Memorystore for Redis — Instance Management

```bash
# Create a Basic tier Redis instance (development only)
gcloud redis instances create my-redis-dev \
  --region=us-central1 \
  --size=1 \
  --tier=basic \
  --redis-version=redis_7_0

# Create a Standard tier (HA) Redis instance
gcloud redis instances create my-redis-prod \
  --region=us-central1 \
  --size=5 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --network=projects/MY_PROJECT/global/networks/my-vpc

# Create Standard tier with RDB persistence
gcloud redis instances create my-redis-persistent \
  --region=us-central1 \
  --size=10 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --persistence-mode=rdb \
  --rdb-snapshot-period=one-hour

# Create Standard tier with TLS enabled
gcloud redis instances create my-redis-tls \
  --region=us-central1 \
  --size=5 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --transit-encryption-mode=server-authentication \
  --network=projects/MY_PROJECT/global/networks/my-vpc

# Create Standard tier with AUTH string and specific Redis configs
gcloud redis instances create my-redis-configured \
  --region=us-central1 \
  --size=8 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --enable-auth \
  --redis-configs=maxmemory-policy=allkeys-lru,notify-keyspace-events=Ex

# Create in a specific zone (primary zone)
gcloud redis instances create my-redis-zoned \
  --region=us-central1 \
  --zone=us-central1-a \
  --replica-zone=us-central1-f \
  --size=5 \
  --tier=standard \
  --redis-version=redis_7_0

# Create with reserved IP range (for PSA)
gcloud redis instances create my-redis-psa \
  --region=us-central1 \
  --size=5 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --reserved-ip-range=10.100.0.0/29

# Describe a Redis instance (shows IP address, port, AUTH string location)
gcloud redis instances describe my-redis-prod \
  --region=us-central1

# Get just the IP address
gcloud redis instances describe my-redis-prod \
  --region=us-central1 \
  --format="value(host)"

# Get AUTH string
gcloud redis instances describe my-redis-prod \
  --region=us-central1 \
  --format="value(authString)"

# List all Redis instances
gcloud redis instances list --region=us-central1

# List across all regions
gcloud redis instances list

# Update instance (resize memory)
gcloud redis instances update my-redis-prod \
  --region=us-central1 \
  --size=16

# Update Redis configs
gcloud redis instances update my-redis-prod \
  --region=us-central1 \
  --update-redis-config=maxmemory-policy=volatile-lru,hz=15

# Upgrade Redis version
gcloud redis instances upgrade my-redis-prod \
  --region=us-central1 \
  --redis-version=redis_7_0

# Initiate manual failover (test HA; promotes replica to primary)
gcloud redis instances failover my-redis-prod \
  --region=us-central1 \
  --data-protection-mode=limited-data-loss

# Delete a Redis instance
gcloud redis instances delete my-redis-dev \
  --region=us-central1
```

---

## Redis Export and Import

```bash
# Export Redis data (RDB snapshot) to Cloud Storage
gcloud redis instances export my-redis-prod \
  gs://my-backup-bucket/redis-exports/redis-$(date +%Y%m%d).rdb \
  --region=us-central1

# Import data from an RDB file in Cloud Storage
# Note: Import overwrites all current data in the instance
# TLS must be disabled for import/export
gcloud redis instances import my-redis-prod \
  gs://my-backup-bucket/redis-exports/redis-20240301.rdb \
  --region=us-central1
```

---

## Memorystore for Redis Cluster

```bash
# Create a Redis Cluster (minimum 3 shards, each with primary + replica)
gcloud redis clusters create my-redis-cluster \
  --region=us-central1 \
  --shard-count=3 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --redis-version=redis_7_0

# Create Redis Cluster with replica count (1 replica per shard for HA)
gcloud redis clusters create my-redis-cluster-ha \
  --region=us-central1 \
  --shard-count=5 \
  --replica-count=1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --redis-version=redis_7_0

# Create with TLS and AUTH
gcloud redis clusters create my-redis-cluster-secure \
  --region=us-central1 \
  --shard-count=3 \
  --replica-count=1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --redis-version=redis_7_0 \
  --transit-encryption-mode=server-authentication \
  --enable-auth

# Describe a Redis Cluster
gcloud redis clusters describe my-redis-cluster \
  --region=us-central1

# List Redis Clusters
gcloud redis clusters list --region=us-central1

# Scale cluster (change shard count)
gcloud redis clusters update my-redis-cluster \
  --region=us-central1 \
  --shard-count=8

# Update Redis configs on cluster
gcloud redis clusters update my-redis-cluster \
  --region=us-central1 \
  --update-redis-config=maxmemory-policy=allkeys-lru

# Delete a Redis Cluster
gcloud redis clusters delete my-redis-cluster \
  --region=us-central1
```

---

## Memorystore for Memcached — Instance Management

```bash
# Create a Memcached instance (3 nodes, 1 GB each)
gcloud memcache instances create my-memcache-prod \
  --region=us-central1 \
  --node-count=3 \
  --node-cpu=1 \
  --node-memory=1024 \
  --memcache-version=memcache-1-6 \
  --network=projects/MY_PROJECT/global/networks/my-vpc

# Create with larger nodes (2 vCPU, 5 GB each)
gcloud memcache instances create my-memcache-large \
  --region=us-central1 \
  --node-count=5 \
  --node-cpu=2 \
  --node-memory=5120 \
  --memcache-version=memcache-1-6

# Describe a Memcached instance (shows discovery endpoint, node IPs)
gcloud memcache instances describe my-memcache-prod \
  --region=us-central1

# Get discovery endpoint
gcloud memcache instances describe my-memcache-prod \
  --region=us-central1 \
  --format="value(discoveryEndpoint)"

# List Memcached instances
gcloud memcache instances list --region=us-central1

# Update instance (resize — scale up node count or memory)
gcloud memcache instances update my-memcache-prod \
  --region=us-central1 \
  --node-count=5

# Apply Memcached parameter updates
# First, update parameters
gcloud memcache instances update my-memcache-prod \
  --region=us-central1 \
  --parameters=max_item_size=8388608

# Then apply parameters to nodes (requires restart of nodes)
gcloud memcache instances apply-parameters my-memcache-prod \
  --region=us-central1 \
  --node-ids=node-0,node-1,node-2

# Apply software update to nodes
gcloud memcache instances apply-software-update my-memcache-prod \
  --region=us-central1 \
  --node-ids=node-0

# Delete a Memcached instance
gcloud memcache instances delete my-memcache-prod \
  --region=us-central1
```

---

## Operations

```bash
# List operations for Redis instances in a region
gcloud redis operations list --region=us-central1

# Describe a specific Redis operation
gcloud redis operations describe OPERATION_ID \
  --region=us-central1

# List Memcached operations
gcloud memcache operations list --region=us-central1

# Describe a Memcached operation
gcloud memcache operations describe OPERATION_ID \
  --region=us-central1
```

---

## Useful Flags Reference

```bash
# Redis tier flags
--tier=basic              # Single node, no HA (dev only)
--tier=standard           # Primary + replica, automatic failover

# Redis version flags
--redis-version=redis_6_x
--redis-version=redis_7_0

# Redis persistence flags
--persistence-mode=disabled|rdb|aof
--rdb-snapshot-period=one-hour|six-hours|twelve-hours|twenty-four-hours
--aof-append-fsync=no|everysec|always

# Redis security flags
--enable-auth                                         # Enable AUTH string
--transit-encryption-mode=disabled|server-authentication

# Redis network flags
--network=NETWORK_RESOURCE_URL
--reserved-ip-range=CIDR                              # e.g., 10.100.0.0/29
--connect-mode=DIRECT_PEERING|PRIVATE_SERVICE_ACCESS

# Redis config flags (comma-separated key=value)
--redis-configs=maxmemory-policy=allkeys-lru,hz=10
--update-redis-config=KEY=VALUE                       # For updates

# Common maxmemory-policy values:
#   noeviction       — return errors on OOM (default)
#   allkeys-lru      — evict least recently used keys
#   volatile-lru     — evict LRU keys with TTL set
#   allkeys-lfu      — evict least frequently used
#   volatile-lfu     — evict LFU keys with TTL set
#   allkeys-random   — evict random keys
#   volatile-random  — evict random keys with TTL set
#   volatile-ttl     — evict keys with shortest TTL

# Zone flags for Standard tier
--zone=ZONE               # Primary zone (e.g., us-central1-a)
--replica-zone=ZONE       # Replica zone (e.g., us-central1-f)

# Memcached flags
--node-count=N            # Number of nodes (1-20)
--node-cpu=N              # vCPUs per node (1-4)
--node-memory=MB          # Memory per node in MB (1024-5120)
--memcache-version=memcache-1-5|memcache-1-6
```

---

## Connect to Redis (Testing and Debugging)

```bash
# Get Redis host and port
REDIS_HOST=$(gcloud redis instances describe my-redis-prod \
  --region=us-central1 --format="value(host)")
REDIS_PORT=$(gcloud redis instances describe my-redis-prod \
  --region=us-central1 --format="value(port)")

# Connect from a GCE VM in the same VPC using redis-cli
# Install: sudo apt-get install redis-tools
redis-cli -h $REDIS_HOST -p $REDIS_PORT

# With AUTH
REDIS_AUTH=$(gcloud redis instances describe my-redis-prod \
  --region=us-central1 --format="value(authString)")
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_AUTH

# Test connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_AUTH PING
# Expected: PONG

# Connect to Redis Cluster
gcloud redis clusters describe my-redis-cluster \
  --region=us-central1 \
  --format="value(discoveryEndpoints)"
redis-cli -c -h DISCOVERY_HOST -p DISCOVERY_PORT CLUSTER INFO
```
