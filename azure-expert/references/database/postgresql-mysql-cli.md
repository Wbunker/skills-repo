# Azure Database for PostgreSQL & MySQL — CLI Reference
For service concepts, see [postgresql-mysql-capabilities.md](postgresql-mysql-capabilities.md).

## Azure Database for PostgreSQL — Flexible Server

```bash
# --- Create PostgreSQL Flexible Server (Private VNet access) ---
az postgres flexible-server create \
  --name mypgsqlserver \
  --resource-group myRG \
  --location eastus \
  --admin-user pgadmin \
  --admin-password 'P@ssw0rd123!' \
  --sku-name Standard_D4s_v3 \      # Burstable: Standard_B1ms; GP: Standard_D4s_v3; MO: Standard_E4s_v3
  --tier GeneralPurpose \           # Burstable | GeneralPurpose | MemoryOptimized
  --version 16 \                    # PostgreSQL major version
  --storage-size 128 \              # GiB
  --storage-auto-grow Enabled \
  --backup-retention 14 \           # Days (7–35)
  --geo-redundant-backup Enabled \  # Enable cross-region backup
  --high-availability ZoneRedundant \ # Disabled | SameZone | ZoneRedundant
  --zone 1 \                        # Primary AZ
  --standby-zone 2 \               # Standby AZ (ZoneRedundant only)
  --vnet myVNet \
  --subnet myPGSubnet \
  --private-dns-zone myPGSubnet.private.postgres.database.azure.com

# Create with public access
az postgres flexible-server create \
  --name mypgsqlserver \
  --resource-group myRG \
  --location eastus \
  --admin-user pgadmin \
  --admin-password 'P@ssw0rd123!' \
  --sku-name Standard_D4s_v3 \
  --tier GeneralPurpose \
  --version 16 \
  --storage-size 256 \
  --public-access 203.0.113.0/24   # Firewall IP range; 0.0.0.0 = allow all Azure services

# --- List / Show ---
az postgres flexible-server list \
  --resource-group myRG \
  --output table

az postgres flexible-server show \
  --name mypgsqlserver \
  --resource-group myRG

# Connection string
az postgres flexible-server show-connection-string \
  --server-name mypgsqlserver \
  --database-name mydb \
  --admin-user pgadmin \
  --admin-password 'P@ssw0rd123!'

# --- Start / Stop / Restart ---
az postgres flexible-server start \
  --name mypgsqlserver \
  --resource-group myRG

az postgres flexible-server stop \
  --name mypgsqlserver \
  --resource-group myRG

az postgres flexible-server restart \
  --name mypgsqlserver \
  --resource-group myRG \
  --fail-over Forced               # Forced failover to standby (HA only)

# --- Update Server ---
# Scale compute
az postgres flexible-server update \
  --name mypgsqlserver \
  --resource-group myRG \
  --sku-name Standard_D8s_v3 \
  --tier GeneralPurpose

# Update backup retention
az postgres flexible-server update \
  --name mypgsqlserver \
  --resource-group myRG \
  --backup-retention 35

# Enable/disable HA
az postgres flexible-server update \
  --name mypgsqlserver \
  --resource-group myRG \
  --high-availability ZoneRedundant \
  --zone 1 \
  --standby-zone 2

# Set maintenance window
az postgres flexible-server update \
  --name mypgsqlserver \
  --resource-group myRG \
  --maintenance-window "Sunday:02:00"   # day:HH:MM UTC

# --- Server Parameters ---
az postgres flexible-server parameter list \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --output table

az postgres flexible-server parameter show \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --name shared_buffers

az postgres flexible-server parameter set \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --name max_connections \
  --value 500

az postgres flexible-server parameter set \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --name shared_preload_libraries \
  --value "pg_cron,pgvector"

# --- Firewall Rules (public access only) ---
az postgres flexible-server firewall-rule create \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --name AllowMyIP \
  --start-ip-address 203.0.113.10 \
  --end-ip-address 203.0.113.10

az postgres flexible-server firewall-rule list \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --output table

az postgres flexible-server firewall-rule delete \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --name AllowMyIP --yes
```

---

## PostgreSQL Databases

```bash
# --- Create Database ---
az postgres flexible-server db create \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --database-name mydb \
  --charset UTF8 \
  --collation en_US.UTF8

# --- List Databases ---
az postgres flexible-server db list \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --output table

# --- Delete Database ---
az postgres flexible-server db delete \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --database-name mydb --yes
```

---

## PostgreSQL Read Replicas

```bash
# --- Create Read Replica ---
az postgres flexible-server replica create \
  --replica-name mypgsqlreplica \
  --resource-group myRG \
  --source-server /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.DBforPostgreSQL/flexibleServers/mypgsqlserver

# Cross-region replica
az postgres flexible-server replica create \
  --replica-name mypgsqlreplica-westus \
  --resource-group myDR-RG \
  --source-server /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.DBforPostgreSQL/flexibleServers/mypgsqlserver \
  --location westus

# --- List Replicas ---
az postgres flexible-server replica list \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --output table

# --- Stop Replication (promote to standalone) ---
az postgres flexible-server replica stop-replication \
  --name mypgsqlreplica \
  --resource-group myRG
```

---

## PostgreSQL Backup and Restore

```bash
# --- List Backups ---
az postgres flexible-server backup list \
  --server-name mypgsqlserver \
  --resource-group myRG \
  --output table

# --- Point-in-Time Restore ---
az postgres flexible-server restore \
  --resource-group myRG \
  --name mypgsqlserver-restored \
  --source-server mypgsqlserver \
  --restore-time "2024-12-01T10:30:00Z" \
  --location eastus

# --- Geo-Restore (cross-region) ---
az postgres flexible-server geo-restore \
  --resource-group myDR-RG \
  --name mypgsqlserver-georestore \
  --source-server mypgsqlserver \
  --location westus
```

---

## PostgreSQL Major Version Upgrade

```bash
# --- In-place Major Version Upgrade ---
az postgres flexible-server upgrade \
  --name mypgsqlserver \
  --resource-group myRG \
  --version 16                      # Target major version
```

---

## Azure Database for MySQL — Flexible Server

```bash
# --- Create MySQL Flexible Server ---
az mysql flexible-server create \
  --name mymysqlserver \
  --resource-group myRG \
  --location eastus \
  --admin-user mysqladmin \
  --admin-password 'P@ssw0rd123!' \
  --sku-name Standard_D4ds_v4 \     # Burstable: Standard_B1ms; GP: Standard_D4ds_v4; BC: Standard_E4ds_v4
  --tier GeneralPurpose \           # Burstable | GeneralPurpose | BusinessCritical
  --version 8.0 \
  --storage-size 128 \
  --storage-auto-grow Enabled \
  --backup-retention 14 \
  --geo-redundant-backup Enabled \
  --high-availability ZoneRedundant \
  --zone 1 \
  --standby-zone 2 \
  --vnet myVNet \
  --subnet myMySQLSubnet

# Create with public access and firewall
az mysql flexible-server create \
  --name mymysqlserver \
  --resource-group myRG \
  --location eastus \
  --admin-user mysqladmin \
  --admin-password 'P@ssw0rd123!' \
  --sku-name Standard_D4ds_v4 \
  --tier GeneralPurpose \
  --version 8.0 \
  --public-access 0.0.0.0           # Allow all IPs; add specific rules after

# --- List / Show ---
az mysql flexible-server list \
  --resource-group myRG \
  --output table

az mysql flexible-server show \
  --name mymysqlserver \
  --resource-group myRG

# --- Start / Stop / Restart ---
az mysql flexible-server start \
  --name mymysqlserver \
  --resource-group myRG

az mysql flexible-server stop \
  --name mymysqlserver \
  --resource-group myRG

az mysql flexible-server restart \
  --name mymysqlserver \
  --resource-group myRG \
  --fail-over Forced

# --- Update Server ---
az mysql flexible-server update \
  --name mymysqlserver \
  --resource-group myRG \
  --sku-name Standard_D8ds_v4

# --- Server Parameters ---
az mysql flexible-server parameter list \
  --server-name mymysqlserver \
  --resource-group myRG \
  --output table

az mysql flexible-server parameter set \
  --server-name mymysqlserver \
  --resource-group myRG \
  --name innodb_buffer_pool_size \
  --value 4294967296                # 4 GiB in bytes

az mysql flexible-server parameter set \
  --server-name mymysqlserver \
  --resource-group myRG \
  --name slow_query_log \
  --value ON

# --- Firewall Rules ---
az mysql flexible-server firewall-rule create \
  --name mymysqlserver \
  --resource-group myRG \
  --rule-name AllowMyIP \
  --start-ip-address 203.0.113.10 \
  --end-ip-address 203.0.113.10

az mysql flexible-server firewall-rule list \
  --name mymysqlserver \
  --resource-group myRG
```

---

## MySQL Databases and Replicas

```bash
# --- Create Database ---
az mysql flexible-server db create \
  --server-name mymysqlserver \
  --resource-group myRG \
  --database-name myappdb \
  --charset utf8mb4 \
  --collation utf8mb4_unicode_ci

# --- List Databases ---
az mysql flexible-server db list \
  --server-name mymysqlserver \
  --resource-group myRG \
  --output table

# --- Create Read Replica ---
az mysql flexible-server replica create \
  --replica-name mymysqlreplica \
  --resource-group myRG \
  --source-server mymysqlserver

# --- Stop Replication ---
az mysql flexible-server replica stop-replication \
  --name mymysqlreplica \
  --resource-group myRG

# --- Point-in-Time Restore ---
az mysql flexible-server restore \
  --resource-group myRG \
  --name mymysqlserver-restored \
  --source-server mymysqlserver \
  --restore-time "2024-12-01T10:30:00Z"

# --- Geo-Restore ---
az mysql flexible-server geo-restore \
  --resource-group myDR-RG \
  --name mymysqlserver-georestore \
  --source-server mymysqlserver \
  --location westus

# --- Delete Server ---
az mysql flexible-server delete \
  --name mymysqlserver \
  --resource-group myRG --yes
```
