# Azure Cosmos DB — CLI Reference
For service concepts, see [cosmos-db-capabilities.md](cosmos-db-capabilities.md).

## Cosmos DB Account

```bash
# --- Create Account (Core SQL API) ---
az cosmosdb create \
  --name mycosmosaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
  --default-consistency-level Session \
  --kind GlobalDocumentDB \         # GlobalDocumentDB (SQL/Core) | MongoDB | Parse
  --capabilities EnableServerless   # Remove this line for provisioned throughput

# Create with multiple regions (geo-replication)
az cosmosdb create \
  --name mycosmosaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
             regionName=westus failoverPriority=1 isZoneRedundant=false \
  --default-consistency-level BoundedStaleness \
  --max-interval 10 \               # Staleness: max seconds (BoundedStaleness only)
  --max-staleness-prefix 200 \      # Staleness: max operations (BoundedStaleness only)
  --enable-automatic-failover true

# Create MongoDB API account
az cosmosdb create \
  --name mymongoaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --kind MongoDB \
  --server-version 4.2              # MongoDB compatibility version

# Create Cassandra API account
az cosmosdb create \
  --name mycassandraaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --capabilities EnableCassandra

# Create Gremlin API account
az cosmosdb create \
  --name mygremlinaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --capabilities EnableGremlin

# Create Table API account
az cosmosdb create \
  --name mytableaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --capabilities EnableTable

# Create with free tier
az cosmosdb create \
  --name myfreetieraccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 \
  --enable-free-tier true

# --- List / Show Accounts ---
az cosmosdb list \
  --resource-group myRG \
  --output table

az cosmosdb show \
  --name mycosmosaccount \
  --resource-group myRG

# --- List Available Regions ---
az cosmosdb locations list \
  --output table

# --- Update Account ---
# Add a read region
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myRG \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
             regionName=westus failoverPriority=1 isZoneRedundant=false \
             regionName=northeurope failoverPriority=2 isZoneRedundant=false

# Change consistency level
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myRG \
  --default-consistency-level Eventual

# Enable multi-region write (multi-master)
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myRG \
  --enable-multiple-write-locations true

# Enable Synapse Link (analytical store)
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myRG \
  --enable-analytical-storage true

# --- Account Keys ---
az cosmosdb keys list \
  --name mycosmosaccount \
  --resource-group myRG \
  --type keys                       # keys | read-only-keys | connection-strings

# Regenerate key
az cosmosdb keys regenerate \
  --name mycosmosaccount \
  --resource-group myRG \
  --key-kind primary                # primary | secondary | primaryReadonly | secondaryReadonly

# --- Manual Failover ---
az cosmosdb failover-priority-change \
  --name mycosmosaccount \
  --resource-group myRG \
  --failover-policies eastus=0 westus=1

# --- Delete Account ---
az cosmosdb delete \
  --name mycosmosaccount \
  --resource-group myRG --yes
```

---

## SQL (Core) API — Database and Container

```bash
# --- Create SQL Database ---
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --name myDatabase

# Create with shared throughput (shared across containers)
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --name myDatabase \
  --throughput 400                  # Minimum 400 RU/s shared

# --- List / Show Databases ---
az cosmosdb sql database list \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --output table

az cosmosdb sql database show \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --name myDatabase

# --- Create SQL Container ---
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer \
  --partition-key-path /userId \    # Required; immutable after creation
  --throughput 1000                 # Container-level throughput (RU/s)

# Create container with autoscale
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer \
  --partition-key-path /tenantId \
  --max-throughput 10000 \          # Max RU/s for autoscale (min is 10%)
  --analytical-storage-ttl -1      # Enable analytical store (-1 = no expiry)

# Create container with TTL
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name sessionContainer \
  --partition-key-path /sessionId \
  --throughput 400 \
  --ttl 86400                       # Default TTL in seconds (86400 = 1 day); -1 = no default

# Create container with hierarchical partition key
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name multiTenantContainer \
  --partition-key-path /tenantId /userId \  # Hierarchical (up to 3 levels)
  --partition-key-version 2 \              # Required for hierarchical keys
  --throughput 1000

# --- List / Show Containers ---
az cosmosdb sql container list \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --output table

az cosmosdb sql container show \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer

# --- Update Container Throughput ---
az cosmosdb sql container throughput update \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer \
  --throughput 5000                 # New manual RU/s

# Switch from manual to autoscale
az cosmosdb sql container throughput migrate \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer \
  --throughput-type autoscale

# --- Show Container Throughput ---
az cosmosdb sql container throughput show \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer

# --- Delete Container ---
az cosmosdb sql container delete \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer --yes

# --- Delete Database ---
az cosmosdb sql database delete \
  --account-name mycosmosaccount \
  --resource-group myRG \
  --name myDatabase --yes
```

---

## MongoDB API

```bash
# Create MongoDB database
az cosmosdb mongodb database create \
  --account-name mymongoaccount \
  --resource-group myRG \
  --name myMongoDB \
  --throughput 400

# Create MongoDB collection (container)
az cosmosdb mongodb collection create \
  --account-name mymongoaccount \
  --resource-group myRG \
  --database-name myMongoDB \
  --name myCollection \
  --shard userId \                  # Shard key (partition key)
  --throughput 1000

# List collections
az cosmosdb mongodb collection list \
  --account-name mymongoaccount \
  --resource-group myRG \
  --database-name myMongoDB
```

---

## Cassandra API

```bash
# Create Cassandra keyspace
az cosmosdb cassandra keyspace create \
  --account-name mycassandraaccount \
  --resource-group myRG \
  --name myKeyspace \
  --throughput 400

# Create Cassandra table
az cosmosdb cassandra table create \
  --account-name mycassandraaccount \
  --resource-group myRG \
  --keyspace-name myKeyspace \
  --name myTable \
  --throughput 400 \
  --schema @cassandra-schema.json
```

---

## Network and Security

```bash
# --- Enable Virtual Network Rule ---
az cosmosdb network-rule add \
  --name mycosmosaccount \
  --resource-group myRG \
  --subnet /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet

# --- List Network Rules ---
az cosmosdb network-rule list \
  --name mycosmosaccount \
  --resource-group myRG

# --- Add IP Rule ---
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myRG \
  --ip-range-filter "203.0.113.0/24,198.51.100.1"

# --- Enable Private Endpoint ---
az network private-endpoint create \
  --name myCosmosEndpoint \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az cosmosdb show --name mycosmosaccount --resource-group myRG --query id --output tsv) \
  --group-id Sql \                  # Sql | MongoDB | Cassandra | Gremlin | Table
  --connection-name myCosmosConnection
```
