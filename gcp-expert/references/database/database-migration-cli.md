# Database Migration Service — CLI Reference

---

## Connection Profiles

Connection profiles store credentials and connection info for source and destination databases.

### Create Connection Profiles

```bash
# Create a MySQL source connection profile
gcloud database-migration connection-profiles create mysql-source-profile \
  --region=us-central1 \
  --display-name="MySQL Source" \
  --database-engine=mysql \
  --host=10.1.2.3 \
  --port=3306 \
  --username=dms_user \
  --password=MIGRATION_PASSWORD \
  --ssl-mode=REQUIRE

# Create a MySQL source profile with client certificates (mTLS)
gcloud database-migration connection-profiles create mysql-source-mtls \
  --region=us-central1 \
  --database-engine=mysql \
  --host=10.1.2.3 \
  --port=3306 \
  --username=dms_user \
  --password=MIGRATION_PASSWORD \
  --ssl-mode=VERIFY_CA \
  --ca-certificate="$(cat server-ca.pem)" \
  --client-certificate="$(cat client-cert.pem)" \
  --client-key="$(cat client-key.pem)"

# Create a PostgreSQL source connection profile
gcloud database-migration connection-profiles create pg-source-profile \
  --region=us-central1 \
  --display-name="PostgreSQL Source" \
  --database-engine=postgresql \
  --host=10.1.2.4 \
  --port=5432 \
  --username=dms_user \
  --password=MIGRATION_PASSWORD

# Create an Oracle source connection profile (for heterogeneous migration)
gcloud database-migration connection-profiles create oracle-source-profile \
  --region=us-central1 \
  --display-name="Oracle Source" \
  --database-engine=oracle \
  --host=10.1.2.5 \
  --port=1521 \
  --username=dms_user \
  --password=MIGRATION_PASSWORD \
  --oracle-service-name=ORCL

# Create a Cloud SQL for PostgreSQL destination profile
gcloud database-migration connection-profiles create cloudsql-pg-dest \
  --region=us-central1 \
  --display-name="Cloud SQL PostgreSQL Destination" \
  --database-engine=postgresql \
  --cloudsql-instance-id=my-cloudsql-dest \
  --username=postgres \
  --password=DEST_PASSWORD

# Create an AlloyDB destination connection profile
gcloud database-migration connection-profiles create alloydb-dest \
  --region=us-central1 \
  --display-name="AlloyDB Destination" \
  --database-engine=postgresql \
  --alloydb-cluster=my-alloydb-cluster \
  --username=postgres \
  --password=DEST_PASSWORD
```

### Manage Connection Profiles

```bash
# Describe a connection profile
gcloud database-migration connection-profiles describe mysql-source-profile \
  --region=us-central1

# List all connection profiles in a region
gcloud database-migration connection-profiles list \
  --region=us-central1

# List with format
gcloud database-migration connection-profiles list \
  --region=us-central1 \
  --format="table(name,displayName,engine,state)"

# Update a connection profile (e.g., change password)
gcloud database-migration connection-profiles update mysql-source-profile \
  --region=us-central1 \
  --password=NEW_PASSWORD

# Delete a connection profile
gcloud database-migration connection-profiles delete mysql-source-profile \
  --region=us-central1
```

---

## Migration Jobs

### Create Migration Jobs

```bash
# Create a continuous MySQL migration job
gcloud database-migration migration-jobs create mysql-to-cloudsql-job \
  --region=us-central1 \
  --display-name="MySQL to Cloud SQL Migration" \
  --type=CONTINUOUS \
  --source=mysql-source-profile \
  --destination=cloudsql-pg-dest \
  --dump-flags=--single-transaction,--set-gtid-purged=off

# Create a continuous PostgreSQL to Cloud SQL migration
gcloud database-migration migration-jobs create pg-to-cloudsql-job \
  --region=us-central1 \
  --display-name="PostgreSQL to Cloud SQL Migration" \
  --type=CONTINUOUS \
  --source=pg-source-profile \
  --destination=cloudsql-pg-dest

# Create a continuous PostgreSQL to AlloyDB migration
gcloud database-migration migration-jobs create pg-to-alloydb-job \
  --region=us-central1 \
  --display-name="PostgreSQL to AlloyDB Migration" \
  --type=CONTINUOUS \
  --source=pg-source-profile \
  --destination=alloydb-dest

# Create a one-time (dump and restore) migration job
gcloud database-migration migration-jobs create mysql-one-time-job \
  --region=us-central1 \
  --display-name="MySQL One-Time Migration" \
  --type=ONE_TIME \
  --source=mysql-source-profile \
  --destination=cloudsql-pg-dest

# Create a migration job with connectivity via reverse-SSH tunnel
gcloud database-migration migration-jobs create pg-reverse-ssh-job \
  --region=us-central1 \
  --type=CONTINUOUS \
  --source=pg-source-profile \
  --destination=cloudsql-pg-dest \
  --peer-vpc=projects/MY_PROJECT/global/networks/my-vpc

# Create migration job with VPC peering connectivity
gcloud database-migration migration-jobs create pg-vpc-job \
  --region=us-central1 \
  --type=CONTINUOUS \
  --source=pg-source-profile \
  --destination=cloudsql-pg-dest \
  --vpc=projects/MY_PROJECT/global/networks/my-vpc

# Create heterogeneous migration job (Oracle → PostgreSQL)
# Note: Requires a conversion workspace to be created first
gcloud database-migration migration-jobs create oracle-to-pg-job \
  --region=us-central1 \
  --display-name="Oracle to PostgreSQL Migration" \
  --type=CONTINUOUS \
  --source=oracle-source-profile \
  --destination=cloudsql-pg-dest \
  --conversion-workspace=my-conversion-workspace
```

### Verify, Start, Stop, Describe, List Migration Jobs

```bash
# Verify a migration job (checks connectivity, permissions, CDC prerequisites)
# Always run verify before start
gcloud database-migration migration-jobs verify mysql-to-cloudsql-job \
  --region=us-central1

# Start a migration job (begins full dump then continuous replication)
gcloud database-migration migration-jobs start mysql-to-cloudsql-job \
  --region=us-central1

# Describe a migration job (shows state, replication lag, errors)
gcloud database-migration migration-jobs describe mysql-to-cloudsql-job \
  --region=us-central1

# List migration jobs
gcloud database-migration migration-jobs list \
  --region=us-central1

# List with state filter
gcloud database-migration migration-jobs list \
  --region=us-central1 \
  --filter="state=RUNNING"

# Stop a migration job (pause replication; can be restarted)
gcloud database-migration migration-jobs stop mysql-to-cloudsql-job \
  --region=us-central1

# Restart a stopped migration job
gcloud database-migration migration-jobs start mysql-to-cloudsql-job \
  --region=us-central1

# Promote a migration job (final cutover — makes destination standalone)
# WARNING: This operation is irreversible. Stop writes to source before promoting.
gcloud database-migration migration-jobs promote mysql-to-cloudsql-job \
  --region=us-central1

# Delete a migration job (only when in STOPPED or COMPLETED state)
gcloud database-migration migration-jobs delete mysql-to-cloudsql-job \
  --region=us-central1
```

### Monitor Migration Progress

```bash
# Check replication lag and job status
gcloud database-migration migration-jobs describe mysql-to-cloudsql-job \
  --region=us-central1 \
  --format="yaml(state,phase,error,metrics)"

# Get state only
gcloud database-migration migration-jobs describe mysql-to-cloudsql-job \
  --region=us-central1 \
  --format="value(state)"

# Get replication lag
gcloud database-migration migration-jobs describe mysql-to-cloudsql-job \
  --region=us-central1 \
  --format="value(metrics.cdcLatency)"
```

---

## Conversion Workspaces (Heterogeneous Migrations)

Conversion workspaces are used for Oracle → PostgreSQL migrations. They contain the schema conversion and allow manual editing before applying to the destination.

```bash
# Create a conversion workspace
gcloud database-migration conversion-workspaces create my-conversion-workspace \
  --region=us-central1 \
  --display-name="Oracle to PG Conversion" \
  --database-engine=oracle \
  --database-version=19 \
  --destination-database-engine=postgresql \
  --destination-database-version=15

# Describe a conversion workspace
gcloud database-migration conversion-workspaces describe my-conversion-workspace \
  --region=us-central1

# List conversion workspaces
gcloud database-migration conversion-workspaces list \
  --region=us-central1

# Seed (import schema) from source database into the conversion workspace
gcloud database-migration conversion-workspaces seed my-conversion-workspace \
  --region=us-central1 \
  --source-connection-profile=oracle-source-profile

# Seed from a SQL file (alternative to live source)
gcloud database-migration conversion-workspaces seed my-conversion-workspace \
  --region=us-central1 \
  --database-engine=oracle \
  --sql-file=gs://my-bucket/oracle-schema.sql

# Convert the seeded schema (run automatic conversion)
gcloud database-migration conversion-workspaces convert my-conversion-workspace \
  --region=us-central1

# Apply the converted schema to the destination database
gcloud database-migration conversion-workspaces apply-draft my-conversion-workspace \
  --region=us-central1 \
  --connection-profile=cloudsql-pg-dest

# Get conversion workspace assessment report
gcloud database-migration conversion-workspaces describe my-conversion-workspace \
  --region=us-central1 \
  --format=json

# List conversion issues (objects that need manual intervention)
# Note: Detailed issue management is done in the Cloud Console UI
# The gcloud CLI exports the workspace for review:
gcloud database-migration conversion-workspaces describe-issues my-conversion-workspace \
  --region=us-central1

# Delete a conversion workspace
gcloud database-migration conversion-workspaces delete my-conversion-workspace \
  --region=us-central1
```

---

## Operations

```bash
# List all DMS operations in a region
gcloud database-migration operations list \
  --region=us-central1

# List operations for a specific migration job
gcloud database-migration operations list \
  --region=us-central1 \
  --filter="metadata.verb=create AND metadata.target=*mysql-to-cloudsql-job*"

# Describe a specific operation
gcloud database-migration operations describe OPERATION_ID \
  --region=us-central1

# Cancel an in-progress operation
gcloud database-migration operations cancel OPERATION_ID \
  --region=us-central1

# Delete a completed/failed operation
gcloud database-migration operations delete OPERATION_ID \
  --region=us-central1
```

---

## Complete Migration Workflow Example

```bash
# Example: Migrate PostgreSQL (on-prem) to Cloud SQL for PostgreSQL

# Step 1: Create source connection profile
gcloud database-migration connection-profiles create pg-onprem-source \
  --region=us-central1 \
  --database-engine=postgresql \
  --host=10.0.0.100 \
  --port=5432 \
  --username=dms_replication_user \
  --password=REPL_PASSWORD

# Step 2: Let DMS create the destination Cloud SQL instance automatically,
#         OR reference an existing Cloud SQL instance
gcloud database-migration connection-profiles create pg-cloudsql-dest \
  --region=us-central1 \
  --database-engine=postgresql \
  --cloudsql-instance-id=my-dest-pg-instance \
  --username=postgres \
  --password=DEST_PASSWORD

# Step 3: Create the migration job
gcloud database-migration migration-jobs create pg-migration-job \
  --region=us-central1 \
  --display-name="PostgreSQL Migration" \
  --type=CONTINUOUS \
  --source=pg-onprem-source \
  --destination=pg-cloudsql-dest

# Step 4: Verify (fix any issues reported)
gcloud database-migration migration-jobs verify pg-migration-job \
  --region=us-central1

# Step 5: Start migration
gcloud database-migration migration-jobs start pg-migration-job \
  --region=us-central1

# Step 6: Monitor until replication lag → 0
gcloud database-migration migration-jobs describe pg-migration-job \
  --region=us-central1 \
  --format="table(state,phase,metrics.cdcLatency)"

# Step 7: Cutover window — stop application writes, then promote
# (Stop application writes manually first)
gcloud database-migration migration-jobs promote pg-migration-job \
  --region=us-central1

# Step 8: Update application connection string to Cloud SQL destination
# Step 9: Validate application against Cloud SQL
# Step 10: Decommission source (when ready)
```
