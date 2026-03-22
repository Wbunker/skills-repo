# Azure SQL — CLI Reference
For service concepts, see [azure-sql-capabilities.md](azure-sql-capabilities.md).

## SQL Logical Server

```bash
# --- Create SQL Logical Server ---
az sql server create \
  --name mysqlserver \
  --resource-group myRG \
  --location eastus \
  --admin-user sqladmin \
  --admin-password 'P@ssw0rd123!' \
  --enable-ad-only-auth false       # Set true to enforce Entra-only auth

# Enable Entra ID admin
az sql server ad-admin create \
  --server-name mysqlserver \
  --resource-group myRG \
  --display-name "DBA Group" \
  --object-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# --- List / Show Servers ---
az sql server list \
  --resource-group myRG \
  --output table

az sql server show \
  --name mysqlserver \
  --resource-group myRG

# --- Firewall Rules ---
az sql server firewall-rule create \
  --server-name mysqlserver \
  --resource-group myRG \
  --name AllowMyIP \
  --start-ip-address 203.0.113.10 \
  --end-ip-address 203.0.113.10

# Allow all Azure services (use sparingly)
az sql server firewall-rule create \
  --server-name mysqlserver \
  --resource-group myRG \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

az sql server firewall-rule list \
  --server-name mysqlserver \
  --resource-group myRG

az sql server firewall-rule delete \
  --server-name mysqlserver \
  --resource-group myRG \
  --name AllowMyIP

# --- Update Server ---
az sql server update \
  --name mysqlserver \
  --resource-group myRG \
  --minimal-tls-version 1.2

# --- Delete Server ---
az sql server delete \
  --name mysqlserver \
  --resource-group myRG --yes
```

---

## SQL Database

```bash
# --- Create Database (General Purpose vCore) ---
az sql db create \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --edition GeneralPurpose \
  --family Gen5 \
  --capacity 4 \                    # Number of vCores
  --zone-redundant false \
  --backup-storage-redundancy Geo   # Local | Zone | Geo

# Create Business Critical database
az sql db create \
  --server mysqlserver \
  --resource-group myRG \
  --name myBCdb \
  --edition BusinessCritical \
  --family Gen5 \
  --capacity 8 \
  --zone-redundant true

# Create Hyperscale database
az sql db create \
  --server mysqlserver \
  --resource-group myRG \
  --name myHSdb \
  --edition Hyperscale \
  --family Gen5 \
  --capacity 4 \
  --read-scale Enabled \            # Enable read-scale named replicas
  --ha-replicas 1                   # Number of HA replicas (0-4)

# Create Serverless database
az sql db create \
  --server mysqlserver \
  --resource-group myRG \
  --name myServerlessdb \
  --edition GeneralPurpose \
  --family Gen5 \
  --capacity 2 \
  --compute-model Serverless \
  --min-capacity 0.5 \             # Minimum vCores when auto-scaled down
  --auto-pause-delay 60            # Minutes of idle before auto-pause (60–10080; -1=disabled)

# Create with DTU model (Standard tier)
az sql db create \
  --server mysqlserver \
  --resource-group myRG \
  --name myDTUdb \
  --edition Standard \
  --service-objective S3           # S0, S1, S2, S3, S4, S6, S7, S9, S12

# --- List Databases ---
az sql db list \
  --server mysqlserver \
  --resource-group myRG \
  --output table

# --- Show Database ---
az sql db show \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb

# Show database performance stats
az sql db show-usage \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb

# --- Update Database (scale) ---
az sql db update \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --edition BusinessCritical \
  --family Gen5 \
  --capacity 16

# Change auto-pause settings (serverless)
az sql db update \
  --server mysqlserver \
  --resource-group myRG \
  --name myServerlessdb \
  --auto-pause-delay -1            # Disable auto-pause

# --- Copy Database ---
az sql db copy \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --dest-server mysqlserver-dr \
  --dest-resource-group myDR-RG \
  --dest-name mydb-copy

# --- Export to BACPAC ---
az sql db export \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --admin-user sqladmin \
  --admin-password 'P@ssw0rd123!' \
  --storage-key-type StorageAccessKey \
  --storage-key <storage-account-key> \
  --storage-uri https://mystorageaccount.blob.core.windows.net/backups/mydb.bacpac

# --- Import from BACPAC ---
az sql db import \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --admin-user sqladmin \
  --admin-password 'P@ssw0rd123!' \
  --storage-key-type StorageAccessKey \
  --storage-key <storage-account-key> \
  --storage-uri https://mystorageaccount.blob.core.windows.net/backups/mydb.bacpac

# --- Delete Database ---
az sql db delete \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb --yes
```

---

## Elastic Pool

```bash
# --- Create Elastic Pool ---
az sql elastic-pool create \
  --server mysqlserver \
  --resource-group myRG \
  --name myPool \
  --edition GeneralPurpose \
  --family Gen5 \
  --capacity 8 \                    # Total pool vCores
  --db-min-capacity 0 \             # Min vCores per DB
  --db-max-capacity 4               # Max vCores per DB

# --- Move Database to Elastic Pool ---
az sql db update \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --elastic-pool myPool

# Remove database from pool (to standalone)
az sql db update \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --edition GeneralPurpose \
  --family Gen5 \
  --capacity 2

# --- List Databases in Pool ---
az sql elastic-pool list-dbs \
  --server mysqlserver \
  --resource-group myRG \
  --name myPool \
  --output table

# --- Update Pool ---
az sql elastic-pool update \
  --server mysqlserver \
  --resource-group myRG \
  --name myPool \
  --capacity 16                     # Scale pool up

# --- Delete Pool ---
az sql elastic-pool delete \
  --server mysqlserver \
  --resource-group myRG \
  --name myPool --yes
```

---

## Geo-Replication and Failover Groups

```bash
# --- Active Geo-Replication (add readable secondary) ---
az sql db replica create \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --partner-server mysqlserver-dr \
  --partner-resource-group myDR-RG \
  --secondary-type Geo              # Geo | Named (Hyperscale named replica)

# List geo-replicas
az sql db replica list-links \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb

# Remove geo-replica
az sql db replica delete-link \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --partner-server mysqlserver-dr \
  --partner-resource-group myDR-RG

# --- Auto-Failover Group ---
az sql failover-group create \
  --name myFOG \
  --server mysqlserver \
  --resource-group myRG \
  --partner-server mysqlserver-dr \
  --failover-policy Automatic \     # Automatic | Manual
  --grace-period 2 \                # Hours before automatic failover
  --add-db mydb

# Show failover group
az sql failover-group show \
  --name myFOG \
  --server mysqlserver \
  --resource-group myRG

# Manual failover (planned; zero data loss)
az sql failover-group set-primary \
  --name myFOG \
  --server mysqlserver-dr \
  --resource-group myDR-RG

# List failover groups on a server
az sql failover-group list \
  --server mysqlserver \
  --resource-group myRG

# Delete failover group
az sql failover-group delete \
  --name myFOG \
  --server mysqlserver \
  --resource-group myRG
```

---

## SQL Managed Instance

```bash
# --- Create SQL Managed Instance ---
az sql mi create \
  --name mySQLMI \
  --resource-group myRG \
  --location eastus \
  --admin-user sqladmin \
  --admin-password 'P@ssw0rd123!' \
  --subnet /subscriptions/<sub-id>/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mi-subnet \
  --edition GeneralPurpose \
  --family Gen5 \
  --capacity 8 \
  --storage-size 256 \              # Storage in GiB (min 32)
  --license-type LicenseIncluded    # LicenseIncluded | BasePrice (Azure Hybrid Benefit)

# --- List Managed Instances ---
az sql mi list \
  --resource-group myRG \
  --output table

# --- Show Managed Instance ---
az sql mi show \
  --name mySQLMI \
  --resource-group myRG

# --- Update Managed Instance ---
az sql mi update \
  --name mySQLMI \
  --resource-group myRG \
  --capacity 16 \                   # Scale vCores
  --storage-size 1024               # Scale storage

# --- List Databases on MI ---
az sql midb list \
  --managed-instance mySQLMI \
  --resource-group myRG \
  --output table

# --- Create Database on MI ---
az sql midb create \
  --managed-instance mySQLMI \
  --resource-group myRG \
  --name myMIdb

# --- Delete Managed Instance ---
az sql mi delete \
  --name mySQLMI \
  --resource-group myRG --yes
```

---

## Security and Auditing

```bash
# --- Enable Auditing ---
az sql db audit-policy update \
  --server mysqlserver \
  --resource-group myRG \
  --name mydb \
  --state Enabled \
  --storage-account mystorageaccount \
  --storage-key <key> \
  --retention-days 90

# Audit to Log Analytics workspace
az sql server audit-policy update \
  --name mysqlserver \
  --resource-group myRG \
  --state Enabled \
  --log-analytics-workspace-resource-id /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace \
  --log-analytics-subscription-id <sub-id>

# --- Enable Microsoft Defender for SQL ---
az sql server security-policy update \
  --server mysqlserver \
  --resource-group myRG \
  --email-account-admins Enabled \
  --state Enabled

# --- Transparent Data Encryption ---
az sql db tde set \
  --server mysqlserver \
  --resource-group myRG \
  --database mydb \
  --status Enabled

az sql db tde show \
  --server mysqlserver \
  --resource-group myRG \
  --database mydb
```
