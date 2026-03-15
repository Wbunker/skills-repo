# Bigtable — CLI Reference

Bigtable is managed via two tools:
- `gcloud bigtable` — instance, cluster, app profile, backup management
- `cbt` — table-level operations, data reads/writes (Bigtable-specific CLI tool)

---

## cbt Tool Setup

```bash
# Install cbt via gcloud components
gcloud components install cbt

# Configure cbt (creates ~/.cbtrc)
# Set project and instance
echo "project = my-project
instance = my-bigtable-instance" > ~/.cbtrc

# Or specify per-command
cbt -project=my-project -instance=my-bigtable-instance ls

# Verify cbt is configured
cat ~/.cbtrc
```

---

## Instances

```bash
# Create an SSD instance (single-cluster, for development)
gcloud bigtable instances create my-bigtable-dev \
  --display-name="Dev Bigtable" \
  --cluster-config=id=my-bigtable-dev-c1,zone=us-central1-f,nodes=1,storage-type=SSD

# Create an SSD instance with 3 nodes (minimum recommended for production)
gcloud bigtable instances create my-bigtable-prod \
  --display-name="Production Bigtable" \
  --cluster-config=id=my-bigtable-prod-c1,zone=us-central1-f,nodes=3,storage-type=SSD

# Create an HDD instance (for batch/archival)
gcloud bigtable instances create my-bigtable-archive \
  --display-name="Archive Bigtable" \
  --cluster-config=id=my-bigtable-archive-c1,zone=us-central1-a,nodes=3,storage-type=HDD

# Create a multi-cluster instance with replication (two clusters, same region)
gcloud bigtable instances create my-bigtable-ha \
  --display-name="HA Bigtable" \
  --cluster-config=id=my-bigtable-ha-c1,zone=us-central1-a,nodes=3,storage-type=SSD \
  --cluster-config=id=my-bigtable-ha-c2,zone=us-central1-f,nodes=3,storage-type=SSD

# Describe an instance
gcloud bigtable instances describe my-bigtable-prod

# List all instances
gcloud bigtable instances list

# Update instance display name
gcloud bigtable instances update my-bigtable-prod \
  --display-name="Production Bigtable v2"

# Delete an instance
gcloud bigtable instances delete my-bigtable-dev

# Upgrade instance type (from development to production)
gcloud bigtable instances upgrade my-bigtable-dev

# Add IAM policy binding
gcloud bigtable instances add-iam-policy-binding my-bigtable-prod \
  --member="serviceAccount:myapp@my-project.iam.gserviceaccount.com" \
  --role="roles/bigtable.user"
```

---

## Clusters

```bash
# Add a cluster to an existing instance (for replication)
gcloud bigtable clusters create my-bigtable-prod-c2 \
  --instance=my-bigtable-prod \
  --zone=us-east1-b \
  --nodes=3 \
  --storage-type=SSD

# Describe a cluster
gcloud bigtable clusters describe my-bigtable-prod-c1 \
  --instance=my-bigtable-prod

# List clusters in an instance
gcloud bigtable clusters list --instance=my-bigtable-prod

# Update cluster node count (scale up)
gcloud bigtable clusters update my-bigtable-prod-c1 \
  --instance=my-bigtable-prod \
  --nodes=6

# Scale down cluster
gcloud bigtable clusters update my-bigtable-prod-c1 \
  --instance=my-bigtable-prod \
  --nodes=3

# Enable autoscaling on a cluster
gcloud bigtable clusters update my-bigtable-prod-c1 \
  --instance=my-bigtable-prod \
  --autoscaling-min-nodes=3 \
  --autoscaling-max-nodes=10 \
  --autoscaling-cpu-target=70 \
  --autoscaling-storage-target=70

# Disable autoscaling (switch back to manual)
gcloud bigtable clusters update my-bigtable-prod-c1 \
  --instance=my-bigtable-prod \
  --nodes=5 \
  --disable-autoscaling

# Delete a cluster
gcloud bigtable clusters delete my-bigtable-prod-c2 \
  --instance=my-bigtable-prod
```

---

## Tables (cbt tool)

```bash
# List all tables in the instance
cbt ls

# Create a table
cbt createtable my-table

# Create a table with column families
cbt createtable telemetry-data \
  "families=cf:maxversions=1,meta:maxversions=3"

# Describe a table (view schema, column families, GC policy)
cbt ls my-table

# Delete a table
cbt deletetable my-table

# Count rows in a table (full scan — slow for large tables)
cbt count telemetry-data

# Count rows in a row range
cbt count telemetry-data \
  start=sensor-001 \
  end=sensor-002
```

---

## Column Families and Garbage Collection (cbt)

```bash
# Add a column family
cbt createfamily telemetry-data stats

# Set GC policy: keep max 1 version
cbt setgcpolicy telemetry-data stats maxversions=1

# Set GC policy: keep data no older than 30 days
cbt setgcpolicy telemetry-data stats maxage=30d

# Set GC policy: keep max 3 versions OR data newer than 7 days (union)
cbt setgcpolicy telemetry-data stats "(maxversions=3 || maxage=7d)"

# Set GC policy: keep max 3 versions AND data newer than 7 days (intersection)
cbt setgcpolicy telemetry-data stats "(maxversions=3 && maxage=7d)"

# Delete a column family
cbt deletefamily telemetry-data old-family
```

---

## Reading Data (cbt)

```bash
# Read a single row by row key
cbt read telemetry-data row=sensor-001#device-abc#9007199254739990

# Read rows in a range (start inclusive, end exclusive)
cbt read telemetry-data \
  start=sensor-001 \
  end=sensor-002

# Read a prefix of rows
cbt read telemetry-data \
  prefix=sensor-001#device-abc

# Read with regex on row key
cbt read telemetry-data \
  regex="sensor-001.*"

# Limit number of rows returned
cbt read telemetry-data \
  prefix=sensor-001 \
  count=10

# Read only specific columns (family:qualifier)
cbt read telemetry-data \
  prefix=sensor-001 \
  columns="stats:temperature,stats:humidity"

# Read only specific column family
cbt read telemetry-data \
  prefix=sensor-001 \
  family=stats

# Read with multiple cell versions
cbt read telemetry-data \
  row=sensor-001#device-abc#9007199254739990 \
  cells-per-column=3

# Lookup a single row (faster than read for single row)
cbt lookup telemetry-data sensor-001#device-abc#9007199254739990

# Lookup specific columns
cbt lookup telemetry-data sensor-001#device-abc \
  columns="stats:temperature"
```

---

## Writing Data (cbt)

```bash
# Set a cell value
cbt set telemetry-data \
  sensor-001#device-abc#9007199254739990 \
  stats:temperature=23.5

# Set multiple cells in a row
cbt set telemetry-data \
  sensor-001#device-abc#9007199254739990 \
  stats:temperature=23.5 \
  stats:humidity=65 \
  meta:device_type=thermometer

# Set a cell with a specific timestamp (microseconds)
cbt set telemetry-data \
  sensor-001#device-abc \
  "stats:temperature@1709280000000000=23.5"

# Delete a row
cbt deleterow telemetry-data sensor-001#device-abc#9007199254739990

# Delete a specific cell (column in a row)
cbt delete telemetry-data \
  sensor-001#device-abc \
  stats:temperature

# Delete a column family from a row
cbt delete telemetry-data \
  sensor-001#device-abc \
  family=meta
```

---

## App Profiles

```bash
# Create an app profile with single-cluster routing
gcloud bigtable app-profiles create serving-profile \
  --instance=my-bigtable-prod \
  --description="Serving traffic" \
  --route-to=my-bigtable-prod-c1 \
  --transactional-writes

# Create an app profile with multi-cluster routing (any available cluster)
gcloud bigtable app-profiles create analytics-profile \
  --instance=my-bigtable-prod \
  --description="Analytics reads — any cluster" \
  --route-any

# Describe an app profile
gcloud bigtable app-profiles describe serving-profile \
  --instance=my-bigtable-prod

# List app profiles
gcloud bigtable app-profiles list \
  --instance=my-bigtable-prod

# Update app profile routing
gcloud bigtable app-profiles update serving-profile \
  --instance=my-bigtable-prod \
  --route-to=my-bigtable-prod-c2

# Delete an app profile
gcloud bigtable app-profiles delete analytics-profile \
  --instance=my-bigtable-prod
```

---

## Backups

```bash
# Create a backup of a table
gcloud bigtable backups create my-telemetry-backup-20240301 \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1 \
  --table=telemetry-data \
  --expiration-date=2024-06-01T00:00:00Z

# Create a backup with relative retention
gcloud bigtable backups create my-backup \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1 \
  --table=telemetry-data \
  --retention-period=30d

# Describe a backup
gcloud bigtable backups describe my-telemetry-backup-20240301 \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1

# List backups in a cluster
gcloud bigtable backups list \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1

# List all backups across all clusters
gcloud bigtable backups list \
  --instance=my-bigtable-prod

# Update backup expiration
gcloud bigtable backups update my-telemetry-backup-20240301 \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1 \
  --expiration-date=2024-09-01T00:00:00Z

# Delete a backup
gcloud bigtable backups delete my-telemetry-backup-20240301 \
  --instance=my-bigtable-prod \
  --cluster=my-bigtable-prod-c1

# Restore a backup to a new table (in same or different instance)
gcloud bigtable backups restore \
  --source=projects/MY_PROJECT/instances/my-bigtable-prod/clusters/my-bigtable-prod-c1/backups/my-telemetry-backup-20240301 \
  --destination-instance=my-bigtable-prod \
  --destination-table=telemetry-data-restored \
  --destination-cluster=my-bigtable-prod-c1
```

---

## Useful Reference

```bash
# View Key Visualizer (in Cloud Console — not CLI)
# https://console.cloud.google.com/bigtable/instances/INSTANCE/tables/TABLE/key-visualizer

# Import data from Cloud Storage (using Dataflow)
# Use the Bigtable → Dataflow templates for bulk imports:
# gs://dataflow-templates/latest/GCS_Avro_to_Cloud_Bigtable
# gs://dataflow-templates/latest/GCS_SequenceFile_to_Cloud_Bigtable

# Export data to Cloud Storage (using Dataflow)
# gs://dataflow-templates/latest/Cloud_Bigtable_to_GCS_Avro

# Check IAM roles
gcloud bigtable instances get-iam-policy my-bigtable-prod

# Key IAM roles
# roles/bigtable.admin       — full control
# roles/bigtable.user        — read/write data, manage tables
# roles/bigtable.reader      — read-only data access
# roles/bigtable.viewer      — view metadata only
```
