# AWS ElastiCache & MemoryDB — CLI Reference
For service concepts, see [elasticache-memorydb-capabilities.md](elasticache-memorydb-capabilities.md).

## Amazon ElastiCache

```bash
# --- Replication Groups (Redis OSS / Valkey) ---
# Create Redis cluster with Multi-AZ and replicas
aws elasticache create-replication-group \
  --replication-group-id my-redis \
  --replication-group-description "Production Redis cluster" \
  --engine redis \
  --engine-version 7.1 \
  --cache-node-type cache.r6g.large \
  --num-cache-clusters 3 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --auth-token MySecretToken123

# Create Redis cluster with cluster mode enabled (sharded)
aws elasticache create-replication-group \
  --replication-group-id my-redis-cluster \
  --replication-group-description "Sharded Redis cluster" \
  --engine redis \
  --engine-version 7.1 \
  --cache-node-type cache.r6g.large \
  --num-node-groups 3 \
  --replicas-per-node-group 2 \
  --automatic-failover-enabled \
  --multi-az-enabled

aws elasticache describe-replication-groups
aws elasticache describe-replication-groups --replication-group-id my-redis

aws elasticache modify-replication-group \
  --replication-group-id my-redis \
  --cache-node-type cache.r6g.xlarge \
  --apply-immediately

# Scale out: add a read replica
aws elasticache increase-replica-count \
  --replication-group-id my-redis \
  --new-replica-count 3 \
  --apply-immediately

# Scale in: remove a read replica
aws elasticache decrease-replica-count \
  --replication-group-id my-redis \
  --new-replica-count 1 \
  --apply-immediately

aws elasticache delete-replication-group \
  --replication-group-id my-redis \
  --final-snapshot-identifier my-redis-final-snap

# Manual failover (promote a replica to primary)
aws elasticache test-failover \
  --replication-group-id my-redis \
  --node-group-id 0001

# --- Memcached Clusters ---
aws elasticache create-cache-cluster \
  --cache-cluster-id my-memcached \
  --engine memcached \
  --engine-version 1.6.22 \
  --cache-node-type cache.t3.medium \
  --num-cache-nodes 3

aws elasticache describe-cache-clusters
aws elasticache describe-cache-clusters --cache-cluster-id my-memcached --show-cache-node-info

aws elasticache modify-cache-cluster \
  --cache-cluster-id my-memcached \
  --num-cache-nodes 5 \
  --apply-immediately

aws elasticache delete-cache-cluster --cache-cluster-id my-memcached

# --- Snapshots ---
aws elasticache create-snapshot \
  --replication-group-id my-redis \
  --snapshot-name my-redis-snap-$(date +%Y%m%d)

aws elasticache describe-snapshots --replication-group-id my-redis
aws elasticache describe-snapshots --snapshot-name my-redis-snap-20240101

aws elasticache copy-snapshot \
  --source-snapshot-name my-redis-snap-20240101 \
  --target-snapshot-name my-redis-snap-copy

aws elasticache restore-replication-group-from-snapshot \
  --replication-group-id my-redis-restored \
  --replication-group-description "Restored from snapshot" \
  --snapshot-name my-redis-snap-20240101

aws elasticache delete-snapshot --snapshot-name my-redis-snap-20240101

# --- Global Datastore ---
aws elasticache create-global-replication-group \
  --global-replication-group-id-suffix my-global \
  --primary-replication-group-id my-redis

aws elasticache describe-global-replication-groups

# Add secondary region
aws elasticache create-replication-group \
  --replication-group-id my-redis-eu \
  --replication-group-description "EU secondary" \
  --global-replication-group-id ldgnf-my-global \
  --region eu-west-1

aws elasticache failover-global-replication-group \
  --global-replication-group-id ldgnf-my-global \
  --primary-region eu-west-1 \
  --primary-replication-group-id my-redis-eu

# --- Subnet Groups ---
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name my-cache-subnets \
  --cache-subnet-group-description "Multi-AZ subnets for ElastiCache" \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc

# --- Serverless ---
aws elasticache create-serverless-cache \
  --serverless-cache-name my-serverless-cache \
  --engine redis \
  --security-group-ids sg-12345678 \
  --subnet-ids subnet-aaa subnet-bbb

aws elasticache describe-serverless-caches
aws elasticache delete-serverless-cache --serverless-cache-name my-serverless-cache
```

---

## Amazon MemoryDB

```bash
# --- Clusters ---
aws memorydb create-cluster \
  --cluster-name my-memorydb \
  --node-type db.r6g.large \
  --acl-name open-access \
  --engine-version 7.0 \
  --num-shards 2 \
  --num-replicas-per-shard 1 \
  --tls-enabled \
  --subnet-group-name my-memorydb-subnet-group

aws memorydb describe-clusters
aws memorydb describe-clusters --cluster-name my-memorydb

aws memorydb update-cluster \
  --cluster-name my-memorydb \
  --node-type db.r6g.xlarge

aws memorydb delete-cluster \
  --cluster-name my-memorydb \
  --final-snapshot-name my-memorydb-final-snap

# --- Snapshots ---
aws memorydb create-snapshot \
  --cluster-name my-memorydb \
  --snapshot-name my-memorydb-snap-$(date +%Y%m%d)

aws memorydb describe-snapshots --cluster-name my-memorydb

aws memorydb restore-cluster \
  --cluster-name my-memorydb-restored \
  --snapshot-name my-memorydb-snap-20240101 \
  --node-type db.r6g.large \
  --acl-name open-access \
  --subnet-group-name my-memorydb-subnet-group

aws memorydb delete-snapshot --snapshot-name my-memorydb-snap-20240101

# --- Failover ---
aws memorydb failover-shard \
  --cluster-name my-memorydb \
  --shard-name 0001

# --- ACLs ---
aws memorydb create-acl --acl-name my-acl
aws memorydb create-user \
  --user-name app-user \
  --access-string "on ~* &* +@all" \
  --authentication-mode '{"Type":"password","Passwords":["MySecurePass!1"]}'

aws memorydb update-acl \
  --acl-name my-acl \
  --user-names-to-add app-user

aws memorydb update-cluster \
  --cluster-name my-memorydb \
  --acl-name my-acl

# --- Subnet Groups ---
aws memorydb create-subnet-group \
  --subnet-group-name my-memorydb-subnet-group \
  --description "MemoryDB subnets" \
  --subnet-ids subnet-aaa subnet-bbb
```
