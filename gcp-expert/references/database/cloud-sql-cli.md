# Cloud SQL — CLI Reference

## Instance Management

### Create Instances

**MySQL instance with HA and private IP:**
```bash
gcloud sql instances create my-mysql-instance \
  --database-version=MYSQL_8_0 \
  --tier=db-custom-4-15360 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --storage-type=SSD \
  --storage-size=100GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --retained-backups-count=14 \
  --retained-transaction-log-days=7 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --no-assign-ip \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=4 \
  --deletion-protection
```

**PostgreSQL instance with HA:**
```bash
gcloud sql instances create my-pg-instance \
  --database-version=POSTGRES_15 \
  --tier=db-custom-8-32768 \
  --region=us-east1 \
  --availability-type=REGIONAL \
  --storage-type=SSD \
  --storage-size=200GB \
  --storage-auto-increase \
  --backup-start-time=02:00 \
  --retained-backups-count=30 \
  --retained-transaction-log-days=7 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --no-assign-ip \
  --database-flags=max_connections=200,log_min_duration_statement=1000 \
  --deletion-protection
```

**SQL Server instance:**
```bash
gcloud sql instances create my-sqlserver-instance \
  --database-version=SQLSERVER_2022_STANDARD \
  --tier=db-custom-4-15360 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --storage-type=SSD \
  --storage-size=200GB \
  --storage-auto-increase \
  --root-password=STRONG_PASSWORD_HERE \
  --backup-start-time=03:00 \
  --deletion-protection
```

**Shared core (dev/test):**
```bash
gcloud sql instances create my-dev-instance \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=10GB
```

### Describe, List, Delete

```bash
# Describe instance (connection name, IP, version, status)
gcloud sql instances describe my-pg-instance

# List all instances in project
gcloud sql instances list

# List with specific fields
gcloud sql instances list \
  --format="table(name,databaseVersion,region,state,settings.tier)"

# Delete instance (use --quiet to skip confirmation prompt)
gcloud sql instances delete my-dev-instance --quiet

# Delete with async (don't wait for completion)
gcloud sql instances delete my-dev-instance --async
```

### Patch (Modify) Instance

```bash
# Resize machine type
gcloud sql instances patch my-pg-instance \
  --tier=db-custom-16-65536

# Add or update database flags
gcloud sql instances patch my-pg-instance \
  --database-flags=max_connections=300,log_min_duration_statement=500

# Clear all database flags (reset to defaults)
gcloud sql instances patch my-pg-instance \
  --clear-database-flags

# Enable private IP and disable public IP
gcloud sql instances patch my-pg-instance \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --no-assign-ip

# Increase storage size
gcloud sql instances patch my-pg-instance \
  --storage-size=500GB

# Enable storage auto-increase
gcloud sql instances patch my-pg-instance \
  --storage-auto-increase

# Enable deletion protection
gcloud sql instances patch my-pg-instance \
  --deletion-protection

# Update maintenance window
gcloud sql instances patch my-pg-instance \
  --maintenance-window-day=SAT \
  --maintenance-window-hour=2

# Enable IAM database authentication (PostgreSQL/MySQL)
gcloud sql instances patch my-pg-instance \
  --database-flags=cloudsql.iam_authentication=on
```

### Instance Operations

```bash
# Restart instance
gcloud sql instances restart my-pg-instance

# Initiate HA failover (for testing failover)
gcloud sql instances failover my-pg-instance

# Clone instance (creates new instance from current state)
gcloud sql instances clone my-pg-instance my-pg-instance-clone \
  --bin-log-file-name=mysql-bin.000001 \
  --bin-log-position=107

# Clone to a specific point in time (PITR clone)
gcloud sql instances clone my-pg-instance my-pg-pitr-clone \
  --point-in-time=2024-03-01T12:00:00.000Z
```

---

## Read Replicas

```bash
# Create in-region read replica
gcloud sql instances create my-pg-replica \
  --master-instance-name=my-pg-instance \
  --region=us-east1 \
  --tier=db-custom-4-15360 \
  --storage-type=SSD

# Create cross-region read replica
gcloud sql instances create my-pg-replica-eu \
  --master-instance-name=my-pg-instance \
  --region=europe-west1 \
  --tier=db-custom-4-15360 \
  --availability-type=REGIONAL

# Promote replica to standalone (DR cutover)
# Note: This breaks replication permanently
gcloud sql instances promote-replica my-pg-replica-eu

# Create cascade replica (replica of a replica)
gcloud sql instances create my-pg-cascade-replica \
  --master-instance-name=my-pg-replica \
  --region=us-central1 \
  --tier=db-custom-2-7680
```

---

## Database Management

```bash
# Create a database
gcloud sql databases create myapp_db \
  --instance=my-pg-instance \
  --charset=UTF8 \
  --collation=en_US.UTF8

# Create MySQL database with charset
gcloud sql databases create myapp_db \
  --instance=my-mysql-instance \
  --charset=utf8mb4 \
  --collation=utf8mb4_unicode_ci

# List databases
gcloud sql databases list --instance=my-pg-instance

# Describe a database
gcloud sql databases describe myapp_db --instance=my-pg-instance

# Delete a database
gcloud sql databases delete myapp_db --instance=my-pg-instance
```

---

## User Management

```bash
# Create a user (PostgreSQL)
gcloud sql users create appuser \
  --instance=my-pg-instance \
  --password=STRONG_PASSWORD

# Create a user (MySQL)
gcloud sql users create appuser \
  --instance=my-mysql-instance \
  --host=% \
  --password=STRONG_PASSWORD

# Create IAM-authenticated user (PostgreSQL)
# Use the service account email as the username
gcloud sql users create "myapp@my-project.iam" \
  --instance=my-pg-instance \
  --type=CLOUD_IAM_SERVICE_ACCOUNT

# Create IAM user for a human user
gcloud sql users create "developer@example.com" \
  --instance=my-pg-instance \
  --type=CLOUD_IAM_USER

# List users
gcloud sql users list --instance=my-pg-instance

# Set/change password
gcloud sql users set-password appuser \
  --instance=my-pg-instance \
  --password=NEW_STRONG_PASSWORD

# Delete a user
gcloud sql users delete appuser \
  --instance=my-pg-instance

# Delete MySQL user with host
gcloud sql users delete appuser \
  --instance=my-mysql-instance \
  --host=%
```

---

## Backup Management

```bash
# Create an on-demand backup
gcloud sql backups create --instance=my-pg-instance \
  --description="Pre-migration backup"

# List backups for an instance
gcloud sql backups list --instance=my-pg-instance

# Describe a specific backup
gcloud sql backups describe BACKUP_ID --instance=my-pg-instance

# Delete a backup
gcloud sql backups delete BACKUP_ID --instance=my-pg-instance

# Restore from a backup to the same instance (overwrites data)
gcloud sql backups restore BACKUP_ID \
  --restore-instance=my-pg-instance

# Restore from a backup to a different instance
gcloud sql backups restore BACKUP_ID \
  --restore-instance=my-pg-instance \
  --backup-instance=my-pg-instance-source
```

---

## Export and Import

```bash
# Export to Cloud Storage (SQL dump format)
gcloud sql export sql my-pg-instance \
  gs://my-backup-bucket/exports/myapp_db-$(date +%Y%m%d).sql \
  --database=myapp_db

# Export specific tables
gcloud sql export sql my-pg-instance \
  gs://my-backup-bucket/exports/users-table.sql \
  --database=myapp_db \
  --table=users,orders

# Export as CSV
gcloud sql export csv my-pg-instance \
  gs://my-backup-bucket/exports/users.csv \
  --database=myapp_db \
  --query="SELECT * FROM users WHERE created_at > '2024-01-01'"

# Import from Cloud Storage (SQL)
gcloud sql import sql my-pg-instance \
  gs://my-backup-bucket/exports/myapp_db-20240301.sql \
  --database=myapp_db

# Import CSV
gcloud sql import csv my-pg-instance \
  gs://my-backup-bucket/exports/users.csv \
  --database=myapp_db \
  --table=users
```

---

## SSL/TLS Certificate Management

```bash
# Create a client certificate
gcloud sql ssl client-certs create my-client-cert \
  --instance=my-pg-instance

# List client certificates
gcloud sql ssl client-certs list --instance=my-pg-instance

# Describe a client certificate
gcloud sql ssl client-certs describe my-client-cert \
  --instance=my-pg-instance

# Delete a client certificate
gcloud sql ssl client-certs delete my-client-cert \
  --instance=my-pg-instance

# List server CA certificates
gcloud sql ssl server-ca-certs list --instance=my-pg-instance

# Rotate server CA certificate
gcloud sql ssl server-ca-certs create --instance=my-pg-instance

# Rollback server CA rotation
gcloud sql ssl server-ca-certs rollback --instance=my-pg-instance

# Require SSL for all connections
gcloud sql instances patch my-pg-instance \
  --require-ssl
```

---

## Operations (Monitor Long-Running Tasks)

```bash
# List recent operations for an instance
gcloud sql operations list --instance=my-pg-instance

# List operations with limit
gcloud sql operations list --instance=my-pg-instance --limit=20

# Describe a specific operation
gcloud sql operations describe OPERATION_ID \
  --instance=my-pg-instance

# Wait for an operation to complete
gcloud sql operations wait OPERATION_ID \
  --instance=my-pg-instance \
  --timeout=600
```

---

## Connecting via Cloud SQL Auth Proxy

```bash
# Download Cloud SQL Auth Proxy v2 (Linux)
curl -o cloud-sql-proxy \
  https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.13.0/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Start proxy for PostgreSQL (TCP mode, listens on localhost:5432)
./cloud-sql-proxy \
  --port=5432 \
  MY_PROJECT:us-east1:my-pg-instance

# Start proxy for multiple instances
./cloud-sql-proxy \
  "MY_PROJECT:us-east1:my-pg-instance?port=5432" \
  "MY_PROJECT:us-central1:my-mysql-instance?port=3306"

# Start proxy using Unix socket (recommended for production)
./cloud-sql-proxy \
  --unix-socket=/cloudsql \
  MY_PROJECT:us-east1:my-pg-instance

# Start proxy with a specific service account
./cloud-sql-proxy \
  --credentials-file=/path/to/service-account-key.json \
  MY_PROJECT:us-east1:my-pg-instance

# Connect using psql through the proxy
psql "host=127.0.0.1 port=5432 dbname=myapp_db user=appuser password=STRONG_PASSWORD sslmode=disable"

# Connect using mysql through the proxy
mysql -h 127.0.0.1 -P 3306 -u appuser -p myapp_db

# Get the connection name for an instance (used in proxy command)
gcloud sql instances describe my-pg-instance \
  --format="value(connectionName)"
```

---

## Flags Reference for Common Scenarios

```bash
# HA setup flags
--availability-type=REGIONAL       # Enable HA (primary + standby in different zones)
--availability-type=ZONAL          # Single zone (no standby)

# Network flags
--network=VPC_RESOURCE_URL         # Enable private IP on specified VPC
--no-assign-ip                     # Disable public IP
--authorized-networks=CIDR,CIDR    # Allowlist for public IP access

# Storage flags
--storage-type=SSD|HDD
--storage-size=SIZE                # e.g. 100GB, 1TB
--storage-auto-increase            # Enable auto-grow
--storage-auto-increase-limit=0    # 0 = unlimited growth

# Backup flags
--backup-start-time=HH:MM          # UTC time, e.g. 03:00
--retained-backups-count=N         # Number of automated backups to keep (1-365)
--retained-transaction-log-days=N  # PITR window (0-7 for MySQL, 1-7 for PostgreSQL)
--no-backup                        # Disable automated backups

# Maintenance flags
--maintenance-window-day=DAY       # MON, TUE, WED, THU, FRI, SAT, SUN
--maintenance-window-hour=H        # 0-23 UTC

# Security flags
--deletion-protection              # Prevent accidental deletion
--require-ssl                      # Require SSL for all connections
--database-flags=KEY=VALUE,...     # Engine-specific parameters
```
