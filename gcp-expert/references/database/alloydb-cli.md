# AlloyDB — CLI Reference

## Clusters

```bash
# Create a cluster (with private IP via PSA)
gcloud alloydb clusters create my-alloydb-cluster \
  --region=us-central1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --password=STRONG_INITIAL_PASSWORD

# Create cluster with automated backup policy (14-day retention)
gcloud alloydb clusters create my-alloydb-cluster \
  --region=us-central1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --password=STRONG_INITIAL_PASSWORD \
  --automated-backup-enabled \
  --automated-backup-days-of-week=MONDAY \
  --automated-backup-start-times=03:00 \
  --automated-backup-retention-count=14

# Create a secondary cluster (cross-region DR)
gcloud alloydb clusters create my-alloydb-secondary \
  --region=europe-west1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc-eu \
  --primary-cluster=projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster

# Describe a cluster
gcloud alloydb clusters describe my-alloydb-cluster \
  --region=us-central1

# List all clusters
gcloud alloydb clusters list --region=us-central1

# List across all regions
gcloud alloydb clusters list

# Update cluster (e.g., change backup retention)
gcloud alloydb clusters update my-alloydb-cluster \
  --region=us-central1 \
  --automated-backup-retention-count=30

# Restore cluster from a backup to a new cluster
gcloud alloydb clusters restore my-alloydb-cluster-restored \
  --region=us-central1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --backup=projects/MY_PROJECT/locations/us-central1/backups/my-backup-id

# Restore cluster to a point in time (PITR)
gcloud alloydb clusters restore my-alloydb-pitr-cluster \
  --region=us-central1 \
  --network=projects/MY_PROJECT/global/networks/my-vpc \
  --point-in-time=2024-03-01T15:30:00.000Z \
  --source-cluster=projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster

# Promote secondary cluster to primary (DR cutover)
# This makes the secondary cluster independent; original primary is unaffected
gcloud alloydb clusters promote my-alloydb-secondary \
  --region=europe-west1

# Delete a cluster
gcloud alloydb clusters delete my-alloydb-cluster \
  --region=us-central1

# Force-delete a cluster (including instances and backups)
gcloud alloydb clusters delete my-alloydb-cluster \
  --region=us-central1 \
  --force
```

---

## Instances

### Create Instances

```bash
# Create primary instance
gcloud alloydb instances create my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --instance-type=PRIMARY \
  --cpu-count=8

# Create primary instance with specific memory
gcloud alloydb instances create my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --instance-type=PRIMARY \
  --cpu-count=16 \
  --read-pool-node-count=1  # Not valid on PRIMARY; see read-pool below

# Create read pool instance (horizontal read scaling)
gcloud alloydb instances create my-read-pool \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --instance-type=READ_POOL \
  --cpu-count=4 \
  --read-pool-node-count=3

# Create secondary instance (within secondary cluster for DR reads)
gcloud alloydb instances create my-secondary-instance \
  --cluster=my-alloydb-secondary \
  --region=europe-west1 \
  --instance-type=SECONDARY
```

### Manage Instances

```bash
# Describe an instance
gcloud alloydb instances describe my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1

# List instances in a cluster
gcloud alloydb instances list \
  --cluster=my-alloydb-cluster \
  --region=us-central1

# Update instance (resize CPU)
gcloud alloydb instances update my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --cpu-count=16

# Update read pool node count (scale out/in)
gcloud alloydb instances update my-read-pool \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --read-pool-node-count=5

# Update database flags on primary
gcloud alloydb instances update my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --database-flags=max_connections=300,work_mem=16384

# Initiate manual failover (for testing; promotes a read replica within cluster to primary)
gcloud alloydb instances failover my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1

# Delete an instance
gcloud alloydb instances delete my-read-pool \
  --cluster=my-alloydb-cluster \
  --region=us-central1
```

---

## Backups

```bash
# Create an on-demand backup
gcloud alloydb backups create my-ondemand-backup \
  --cluster=projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster \
  --region=us-central1 \
  --description="Pre-migration snapshot"

# Describe a backup
gcloud alloydb backups describe my-ondemand-backup \
  --region=us-central1

# List all backups (for a region)
gcloud alloydb backups list --region=us-central1

# List backups with project scope
gcloud alloydb backups list

# Delete a backup
gcloud alloydb backups delete my-ondemand-backup \
  --region=us-central1

# Restore from backup (creates a new cluster)
# See cluster restore commands above for PITR and backup-based restore
```

---

## Users

```bash
# Create a built-in (password-based) user
gcloud alloydb users create appuser \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --password=STRONG_PASSWORD \
  --type=BUILT_IN

# Create an IAM-authenticated user (service account)
gcloud alloydb users create "myapp@my-project.iam" \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --type=IAM_BASED

# Create an IAM-authenticated user (human user)
gcloud alloydb users create "developer@example.com" \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --type=IAM_BASED

# List users
gcloud alloydb users list \
  --cluster=my-alloydb-cluster \
  --region=us-central1

# Set password for a user
gcloud alloydb users set-password appuser \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --password=NEW_STRONG_PASSWORD

# Delete a user
gcloud alloydb users delete appuser \
  --cluster=my-alloydb-cluster \
  --region=us-central1
```

---

## Operations

```bash
# List operations for a cluster
gcloud alloydb operations list \
  --cluster=my-alloydb-cluster \
  --region=us-central1

# List all AlloyDB operations in a region
gcloud alloydb operations list --region=us-central1

# Describe a specific operation
gcloud alloydb operations describe OPERATION_ID \
  --region=us-central1

# Cancel a running operation
gcloud alloydb operations cancel OPERATION_ID \
  --region=us-central1
```

---

## AlloyDB Auth Proxy

```bash
# Download AlloyDB Auth Proxy (Linux)
curl -o alloydb-auth-proxy \
  https://storage.googleapis.com/alloydb-auth-proxy/v1.8.0/alloydb-auth-proxy.linux.amd64
chmod +x alloydb-auth-proxy

# Start proxy for a cluster's primary instance (TCP on localhost:5432)
./alloydb-auth-proxy \
  --port=5432 \
  projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster/instances/my-primary-instance

# Start proxy for read pool instance
./alloydb-auth-proxy \
  --port=5433 \
  projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster/instances/my-read-pool

# Start proxy with Unix socket
./alloydb-auth-proxy \
  --unix-socket=/alloydb-sockets \
  projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster/instances/my-primary-instance

# Use service account credentials
./alloydb-auth-proxy \
  --credentials-file=/path/to/sa-key.json \
  projects/MY_PROJECT/locations/us-central1/clusters/my-alloydb-cluster/instances/my-primary-instance

# Get the instance URI (full resource path) for proxy
gcloud alloydb instances describe my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --format="value(name)"

# Connect using psql through proxy
psql "host=127.0.0.1 port=5432 dbname=myapp user=appuser sslmode=disable"
```

---

## Columnar Engine Management

The columnar engine can be configured via database flags on the primary instance:

```bash
# Enable columnar engine (set memory size in MB; 0 to disable)
gcloud alloydb instances update my-primary-instance \
  --cluster=my-alloydb-cluster \
  --region=us-central1 \
  --database-flags=google_columnar_engine.enabled=on,google_columnar_engine.memory_size_in_mb=8192

# Check columnar engine status (run in psql)
# SELECT * FROM g_columnar_columns;
# SELECT * FROM g_columnar_relations;

# Manually populate columnar engine for a specific table (run in psql)
# SELECT google_columnar_engine_add_relation('my_schema.my_table');
```
