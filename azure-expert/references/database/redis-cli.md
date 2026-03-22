# Azure Cache for Redis — CLI Reference
For service concepts, see [redis-capabilities.md](redis-capabilities.md).

## Redis Cache Management

```bash
# --- Create Redis Cache (Standard Tier) ---
az redis create \
  --name myrediscache \
  --resource-group myRG \
  --location eastus \
  --sku Standard \                  # Basic | Standard | Premium
  --vm-size C2 \                    # C0–C6 for Basic/Standard; P1–P5 for Premium
  --enable-non-ssl-port false \     # Disable plaintext port 6379 (recommended)
  --minimum-tls-version 1.2

# Create Premium Cache with zone redundancy
az redis create \
  --name mypremiumredis \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --vm-size P3 \
  --zones 1 2 3                     # Zone-redundant placement (Premium only)

# Create Premium Cache with VNet injection
az redis create \
  --name mypremiumredis \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --vm-size P2 \
  --subnet-id /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/redisSubnet

# Create Premium Cache with clustering
az redis create \
  --name myclusteredredis \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --vm-size P2 \
  --shard-count 3 \                 # 1–10 shards (Premium); each shard has primary + replica
  --enable-non-ssl-port false

# Create Premium Cache with Redis persistence (RDB)
az redis create \
  --name mypersistentredis \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --vm-size P1 \
  --redis-configuration @redis-config.json
# redis-config.json: {"rdb-backup-enabled":"true","rdb-backup-frequency":"60","rdb-backup-max-snapshot-count":"1","rdb-storage-connection-string":"<connection-string>"}

# --- List Caches ---
az redis list \
  --resource-group myRG \
  --output table

az redis list \
  --output table                    # List across all resource groups in subscription

# --- Show Cache Details ---
az redis show \
  --name myrediscache \
  --resource-group myRG

# Show specific properties
az redis show \
  --name myrediscache \
  --resource-group myRG \
  --query '{hostName: hostName, port: sslPort, sku: sku.name, capacity: sku.capacity, provisioningState: provisioningState}' \
  --output json

# --- Get Access Keys ---
az redis list-keys \
  --name myrediscache \
  --resource-group myRG

# --- Regenerate Keys ---
az redis regenerate-keys \
  --name myrediscache \
  --resource-group myRG \
  --key-type Primary               # Primary | Secondary

# --- Update Cache ---
# Enable/disable non-SSL port
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --set enableNonSslPort=false

# Change SKU (scale up)
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --sku Standard \
  --vm-size C4

# Update Redis configuration (maxmemory policy)
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --redis-configuration maxmemory-policy=allkeys-lru

# Update TLS minimum version
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --minimum-tls-version 1.2

# --- Add Shard (Premium clustered cache) ---
az redis update \
  --name myclusteredredis \
  --resource-group myRG \
  --shard-count 5                   # Increase shard count (scale out)

# --- Delete Cache ---
az redis delete \
  --name myrediscache \
  --resource-group myRG --yes
```

---

## Patch Schedule

```bash
# --- Set Maintenance Window ---
az redis patch-schedule set \
  --name myrediscache \
  --resource-group myRG \
  --schedule-entries '[
    {
      "dayOfWeek": "Sunday",
      "startHourUtc": 2,
      "maintenanceWindow": "PT5H"
    }
  ]'

# --- Show Patch Schedule ---
az redis patch-schedule show \
  --name myrediscache \
  --resource-group myRG

# --- Delete Patch Schedule ---
az redis patch-schedule delete \
  --name myrediscache \
  --resource-group myRG
```

---

## Firewall Rules

```bash
# --- Create Firewall Rule ---
az redis firewall-rules create \
  --name myrediscache \
  --resource-group myRG \
  --rule-name AllowOffice \
  --start-ip 203.0.113.0 \
  --end-ip 203.0.113.255

# --- List Firewall Rules ---
az redis firewall-rules list \
  --name myrediscache \
  --resource-group myRG \
  --output table

# --- Delete Firewall Rule ---
az redis firewall-rules delete \
  --name myrediscache \
  --resource-group myRG \
  --rule-name AllowOffice
```

---

## Geo-Replication (Premium Tier — Passive)

```bash
# --- Create Geo-Replication Link ---
# Primary and secondary must be same SKU and in different regions
az redis force-reboot \
  --name myprimaryredis \
  --resource-group myRG \
  --reboot-type AllNodes            # AllNodes | PrimaryNode | SecondaryNode

# Link primary to secondary (passive geo-replication)
az redis geo-replication link create \
  --name myrediscache \
  --resource-group myRG \
  --linked-redis-cache-id /subscriptions/<sub>/resourceGroups/myDR-RG/providers/Microsoft.Cache/Redis/myrediscache-dr \
  --linked-redis-cache-location westus

# --- List Geo-Replication Links ---
az redis geo-replication link list \
  --name myrediscache \
  --resource-group myRG

# --- Delete Geo-Replication Link (promotes secondary) ---
az redis geo-replication link delete \
  --name myrediscache \
  --resource-group myRG \
  --linked-redis-cache-name myrediscache-dr
```

---

## Private Endpoint

```bash
# --- Create Private Endpoint for Redis ---
REDIS_ID=$(az redis show \
  --name myrediscache \
  --resource-group myRG \
  --query id --output tsv)

az network private-endpoint create \
  --name myRedisEndpoint \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id "$REDIS_ID" \
  --group-id redisCache \
  --connection-name myRedisConnection

# Create private DNS zone for Redis
az network private-dns zone create \
  --resource-group myRG \
  --name privatelink.redis.cache.windows.net

az network private-dns link vnet create \
  --resource-group myRG \
  --zone-name privatelink.redis.cache.windows.net \
  --name myDNSLink \
  --virtual-network myVNet \
  --registration-enabled false

# Create DNS record for private endpoint
az network private-endpoint dns-zone-group create \
  --endpoint-name myRedisEndpoint \
  --resource-group myRG \
  --name myZoneGroup \
  --private-dns-zone privatelink.redis.cache.windows.net \
  --zone-name redisCache
```

---

## Redis Configuration Reference

```bash
# --- View All Redis Configuration ---
az redis show \
  --name myrediscache \
  --resource-group myRG \
  --query redisConfiguration

# --- Common Configuration Keys ---
# maxmemory-policy: allkeys-lru | volatile-lru | allkeys-lfu | volatile-lfu | allkeys-random | volatile-random | volatile-ttl | noeviction
# maxfragmentationmemory-reserved: percentage of memory reserved for fragmentation
# maxmemory-reserved: memory reserved for non-cache operations (replication, persistence)
# notify-keyspace-events: keyspace notifications (e.g., "Ex" for expired events)
# rdb-backup-enabled: true | false (Premium with persistence)
# rdb-backup-frequency: 15 | 30 | 60 | 360 | 720 | 1440 (minutes)
# aof-backup-enabled: true | false
# aof-storage-connection-string: Premium AOF persistence storage account

# Set keyspace notifications (for cache invalidation events)
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --redis-configuration notify-keyspace-events=Ex  # E=keyevent, x=expired events

# Set maxmemory eviction policy
az redis update \
  --name myrediscache \
  --resource-group myRG \
  --redis-configuration maxmemory-policy=allkeys-lru
```

---

## Diagnostic and Monitoring

```bash
# --- Enable Diagnostics (send metrics to Log Analytics) ---
REDIS_ID=$(az redis show --name myrediscache --resource-group myRG --query id --output tsv)
WORKSPACE_ID=$(az monitor log-analytics workspace show --workspace-name myWorkspace --resource-group myRG --query id --output tsv)

az monitor diagnostic-settings create \
  --name RedisDiagnostics \
  --resource "$REDIS_ID" \
  --workspace "$WORKSPACE_ID" \
  --metrics '[{"category":"AllMetrics","enabled":true,"retentionPolicy":{"enabled":false,"days":0}}]'

# --- List Diagnostic Settings ---
az monitor diagnostic-settings list \
  --resource "$REDIS_ID" \
  --output table

# --- View Cache Metrics (CLI preview) ---
az monitor metrics list \
  --resource "$REDIS_ID" \
  --metric "usedmemory,cachehits,cachemisses,connectedclients,totalcommandssecond" \
  --interval PT1M \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --output table
```
