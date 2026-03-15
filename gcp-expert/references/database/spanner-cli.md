# Cloud Spanner — CLI Reference

## Instance Management

```bash
# List available instance configurations (regional and multi-region)
gcloud spanner instance-configs list
gcloud spanner instance-configs describe regional-us-central1

# Create a regional instance (1 node)
gcloud spanner instances create my-spanner-instance \
  --config=regional-us-central1 \
  --description="Production Spanner" \
  --nodes=1

# Create a regional instance using processing units (smaller, cheaper)
gcloud spanner instances create my-spanner-dev \
  --config=regional-us-central1 \
  --description="Dev Spanner" \
  --processing-units=100

# Create a multi-region instance (nam4 = N. Virginia + N. Carolina)
gcloud spanner instances create my-global-spanner \
  --config=nam4 \
  --description="Global Production Spanner" \
  --nodes=3

# Create multi-region global instance
gcloud spanner instances create my-global-spanner \
  --config=nam-eur-asia1 \
  --description="Truly Global Spanner" \
  --nodes=5

# Describe an instance
gcloud spanner instances describe my-spanner-instance

# List all instances
gcloud spanner instances list

# Update instance (scale up/down nodes)
gcloud spanner instances update my-spanner-instance \
  --nodes=3

# Update instance using processing units
gcloud spanner instances update my-spanner-dev \
  --processing-units=200

# Update instance description
gcloud spanner instances update my-spanner-instance \
  --description="Production Spanner v2"

# Add IAM policy binding (grant Spanner database user role)
gcloud spanner instances add-iam-policy-binding my-spanner-instance \
  --member="serviceAccount:myapp@my-project.iam.gserviceaccount.com" \
  --role="roles/spanner.databaseUser"

# Delete an instance (also deletes all databases and backups in the instance)
gcloud spanner instances delete my-spanner-dev
```

---

## Database Management

```bash
# Create a database (GoogleSQL dialect)
gcloud spanner databases create myapp-db \
  --instance=my-spanner-instance

# Create a database (PostgreSQL dialect)
gcloud spanner databases create myapp-pg-db \
  --instance=my-spanner-instance \
  --database-dialect=POSTGRESQL

# Create a database with initial DDL
gcloud spanner databases create myapp-db \
  --instance=my-spanner-instance \
  --ddl="CREATE TABLE Users (
    UserId    STRING(36)  NOT NULL,
    Username  STRING(256) NOT NULL,
    Email     STRING(512),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
  ) PRIMARY KEY (UserId)"

# Describe a database
gcloud spanner databases describe myapp-db \
  --instance=my-spanner-instance

# List databases in an instance
gcloud spanner databases list \
  --instance=my-spanner-instance

# Get current DDL for a database
gcloud spanner databases get-ddl myapp-db \
  --instance=my-spanner-instance

# Apply DDL changes (alter schema; zero-downtime for additive changes)
gcloud spanner databases update-ddl myapp-db \
  --instance=my-spanner-instance \
  --ddl="ALTER TABLE Users ADD COLUMN PhoneNumber STRING(32);
CREATE INDEX UsersByEmail ON Users(Email);"

# Apply DDL from a file
gcloud spanner databases update-ddl myapp-db \
  --instance=my-spanner-instance \
  --ddl-file=schema_changes.sql

# Delete a database
gcloud spanner databases delete myapp-db \
  --instance=my-spanner-instance
```

---

## Executing SQL (REPL and One-Shot)

```bash
# Execute a SQL query (read)
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="SELECT UserId, Username FROM Users LIMIT 10"

# Execute a query and format as CSV
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="SELECT * FROM Users" \
  --format=csv

# Execute a DML statement (INSERT/UPDATE/DELETE)
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="INSERT INTO Users (UserId, Username, Email) VALUES ('abc-123', 'alice', 'alice@example.com')"

# Execute a stale read (bounded staleness: data at most 10 seconds old)
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="SELECT COUNT(*) FROM Users" \
  --read-timestamp=$(date -u -d "10 seconds ago" +%Y-%m-%dT%H:%M:%SZ)

# Execute with query options (optimizer version)
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="SELECT * FROM Users WHERE Username = 'alice'" \
  --optimizer-version=5

# Use Spanner REPL (interactive SQL shell)
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --repl
```

---

## Backups

```bash
# Create a backup
gcloud spanner backups create my-backup-20240301 \
  --instance=my-spanner-instance \
  --database=myapp-db \
  --expiration-date=2024-06-01T00:00:00Z

# Create a backup with retention duration
gcloud spanner backups create my-backup-20240301 \
  --instance=my-spanner-instance \
  --database=myapp-db \
  --retention-period=30d

# Create a backup at a specific point in time (PITR backup)
gcloud spanner backups create my-pitr-backup \
  --instance=my-spanner-instance \
  --database=myapp-db \
  --version-time=2024-03-01T12:00:00Z \
  --retention-period=7d

# Describe a backup
gcloud spanner backups describe my-backup-20240301 \
  --instance=my-spanner-instance

# List backups
gcloud spanner backups list \
  --instance=my-spanner-instance

# List backups with filter
gcloud spanner backups list \
  --instance=my-spanner-instance \
  --filter="database:myapp-db"

# Update backup expiration
gcloud spanner backups update my-backup-20240301 \
  --instance=my-spanner-instance \
  --expiration-date=2024-09-01T00:00:00Z

# Delete a backup
gcloud spanner backups delete my-backup-20240301 \
  --instance=my-spanner-instance

# Restore a backup to a new database
gcloud spanner databases restore myapp-db-restored \
  --destination-instance=my-spanner-instance \
  --source-backup=projects/MY_PROJECT/instances/my-spanner-instance/backups/my-backup-20240301

# Restore to a different instance (cross-region restore)
gcloud spanner databases restore myapp-db-restored \
  --destination-instance=my-spanner-instance-us-east \
  --source-backup=projects/MY_PROJECT/instances/my-spanner-instance/backups/my-backup-20240301
```

---

## Operations

```bash
# List operations for an instance (includes backup, restore, database create, DDL)
gcloud spanner operations list \
  --instance=my-spanner-instance

# List operations for a specific database
gcloud spanner operations list \
  --instance=my-spanner-instance \
  --database=myapp-db

# List operations for a specific backup
gcloud spanner operations list \
  --instance=my-spanner-instance \
  --backup=my-backup-20240301

# Describe a specific operation
gcloud spanner operations describe OPERATION_ID \
  --instance=my-spanner-instance

# Cancel an in-progress operation
gcloud spanner operations cancel OPERATION_ID \
  --instance=my-spanner-instance
```

---

## PITR (Version Retention)

PITR in Spanner uses version retention — data is retained for a configurable window allowing reads and restores to any timestamp within that window.

```bash
# Set version retention period on a database (1-7 days)
gcloud spanner databases update myapp-db \
  --instance=my-spanner-instance \
  --version-retention-period=7d

# Read data at a specific past timestamp via execute-sql
gcloud spanner databases execute-sql myapp-db \
  --instance=my-spanner-instance \
  --sql="SELECT * FROM Users" \
  --read-timestamp=2024-03-01T10:00:00Z

# Create a backup from a specific past timestamp (PITR backup)
gcloud spanner backups create my-pitr-snapshot \
  --instance=my-spanner-instance \
  --database=myapp-db \
  --version-time=2024-03-01T10:00:00Z \
  --retention-period=14d
```

---

## IAM for Spanner

```bash
# Grant database user role (read/write access to databases in instance)
gcloud spanner instances add-iam-policy-binding my-spanner-instance \
  --member="serviceAccount:myapp@my-project.iam.gserviceaccount.com" \
  --role="roles/spanner.databaseUser"

# Grant database reader role (read-only)
gcloud spanner instances add-iam-policy-binding my-spanner-instance \
  --member="user:analyst@example.com" \
  --role="roles/spanner.databaseReader"

# Grant admin role
gcloud spanner instances add-iam-policy-binding my-spanner-instance \
  --member="user:admin@example.com" \
  --role="roles/spanner.admin"

# View current IAM policy
gcloud spanner instances get-iam-policy my-spanner-instance

# Fine-grained database-level IAM (database policy, not instance)
gcloud spanner databases add-iam-policy-binding myapp-db \
  --instance=my-spanner-instance \
  --member="serviceAccount:myapp@my-project.iam.gserviceaccount.com" \
  --role="roles/spanner.databaseUser"
```

---

## Useful Flags Reference

```bash
# Instance config flags
--config=CONFIG_NAME               # e.g., regional-us-central1, nam4, eur3
--nodes=N                          # Number of nodes (1 node = 1000 PUs)
--processing-units=N               # Fine-grained capacity (min 100)

# Database flags
--ddl="DDL STATEMENT"              # DDL to execute at creation or update time
--ddl-file=FILE                    # DDL from a file
--database-dialect=GOOGLE_STANDARD_SQL|POSTGRESQL

# Backup flags
--expiration-date=DATETIME         # Absolute expiration (RFC3339 format)
--retention-period=DURATION        # Relative retention e.g., 7d, 30d, 1y
--version-time=DATETIME            # PITR point in time for backup

# execute-sql flags
--sql="QUERY"                      # SQL to execute
--read-timestamp=DATETIME          # Stale read at a specific timestamp
--repl                             # Start interactive REPL
--format=json|csv|table            # Output format
```
