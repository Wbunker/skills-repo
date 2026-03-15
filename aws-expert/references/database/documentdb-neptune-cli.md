# AWS DocumentDB & Neptune — CLI Reference
For service concepts, see [documentdb-neptune-capabilities.md](documentdb-neptune-capabilities.md).

## Amazon DocumentDB

```bash
# --- Clusters ---
aws docdb create-db-cluster \
  --db-cluster-identifier my-docdb \
  --engine docdb \
  --engine-version 5.0.0 \
  --master-username admin \
  --master-user-password secret99 \
  --db-subnet-group-name my-docdb-subnets \
  --vpc-security-group-ids sg-12345678 \
  --storage-encrypted \
  --backup-retention-period 7

aws docdb describe-db-clusters
aws docdb describe-db-clusters --db-cluster-identifier my-docdb

aws docdb modify-db-cluster \
  --db-cluster-identifier my-docdb \
  --backup-retention-period 14 \
  --apply-immediately

aws docdb failover-db-cluster \
  --db-cluster-identifier my-docdb \
  --target-db-instance-identifier my-docdb-reader-1

aws docdb delete-db-cluster \
  --db-cluster-identifier my-docdb \
  --final-db-cluster-snapshot-identifier my-docdb-final-snap

# --- Instances ---
aws docdb create-db-instance \
  --db-instance-identifier my-docdb-writer \
  --db-cluster-identifier my-docdb \
  --db-instance-class db.r6g.large \
  --engine docdb

# Add a reader instance
aws docdb create-db-instance \
  --db-instance-identifier my-docdb-reader-1 \
  --db-cluster-identifier my-docdb \
  --db-instance-class db.r6g.large \
  --engine docdb

aws docdb describe-db-instances
aws docdb describe-db-instances --db-instance-identifier my-docdb-writer

aws docdb modify-db-instance \
  --db-instance-identifier my-docdb-writer \
  --db-instance-class db.r6g.xlarge \
  --apply-immediately

aws docdb reboot-db-instance --db-instance-identifier my-docdb-writer

aws docdb delete-db-instance --db-instance-identifier my-docdb-reader-1

# --- Snapshots ---
aws docdb create-db-cluster-snapshot \
  --db-cluster-identifier my-docdb \
  --db-cluster-snapshot-identifier my-docdb-snap-$(date +%Y%m%d)

aws docdb describe-db-cluster-snapshots --db-cluster-identifier my-docdb

aws docdb restore-db-cluster-from-snapshot \
  --db-cluster-identifier my-docdb-restored \
  --snapshot-identifier my-docdb-snap-20240101 \
  --engine docdb

aws docdb delete-db-cluster-snapshot --db-cluster-snapshot-identifier my-docdb-snap-20240101

# --- Subnet Groups ---
aws docdb create-db-subnet-group \
  --db-subnet-group-name my-docdb-subnets \
  --db-subnet-group-description "DocumentDB subnets" \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc
```

---

## Amazon Neptune

```bash
# --- Clusters ---
aws neptune create-db-cluster \
  --db-cluster-identifier my-neptune \
  --engine neptune \
  --engine-version 1.3.0.0 \
  --db-subnet-group-name my-neptune-subnets \
  --vpc-security-group-ids sg-12345678 \
  --storage-encrypted \
  --backup-retention-period 7 \
  --enable-cloudwatch-logs-exports '["audit"]'

aws neptune describe-db-clusters
aws neptune describe-db-clusters --db-cluster-identifier my-neptune

aws neptune modify-db-cluster \
  --db-cluster-identifier my-neptune \
  --backup-retention-period 14 \
  --apply-immediately

aws neptune failover-db-cluster \
  --db-cluster-identifier my-neptune \
  --target-db-instance-identifier my-neptune-reader-1

aws neptune delete-db-cluster \
  --db-cluster-identifier my-neptune \
  --final-db-cluster-snapshot-identifier my-neptune-final-snap

# --- Instances ---
aws neptune create-db-instance \
  --db-instance-identifier my-neptune-writer \
  --db-cluster-identifier my-neptune \
  --db-instance-class db.r6g.large \
  --engine neptune

# Add reader
aws neptune create-db-instance \
  --db-instance-identifier my-neptune-reader-1 \
  --db-cluster-identifier my-neptune \
  --db-instance-class db.r6g.large \
  --engine neptune

aws neptune describe-db-instances
aws neptune modify-db-instance \
  --db-instance-identifier my-neptune-writer \
  --db-instance-class db.r6g.xlarge \
  --apply-immediately

aws neptune reboot-db-instance --db-instance-identifier my-neptune-writer
aws neptune delete-db-instance --db-instance-identifier my-neptune-reader-1

# --- Snapshots ---
aws neptune create-db-cluster-snapshot \
  --db-cluster-identifier my-neptune \
  --db-cluster-snapshot-identifier my-neptune-snap-$(date +%Y%m%d)

aws neptune describe-db-cluster-snapshots --db-cluster-identifier my-neptune

aws neptune restore-db-cluster-from-snapshot \
  --db-cluster-identifier my-neptune-restored \
  --snapshot-identifier my-neptune-snap-20240101 \
  --engine neptune

aws neptune delete-db-cluster-snapshot --db-cluster-snapshot-identifier my-neptune-snap-20240101

# --- Subnet Groups ---
aws neptune create-db-subnet-group \
  --db-subnet-group-name my-neptune-subnets \
  --db-subnet-group-description "Neptune subnets" \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc

# --- Neptune Analytics ---
aws neptune-graph create-graph \
  --graph-name my-graph \
  --provisioned-memory 128 \
  --replica-count 1 \
  --public-connectivity false

aws neptune-graph list-graphs
aws neptune-graph describe-graph --graph-identifier my-graph-id

aws neptune-graph execute-query \
  --graph-identifier my-graph-id \
  --query-string "MATCH (n) RETURN n LIMIT 10" \
  --language OPEN_CYPHER

aws neptune-graph delete-graph --graph-identifier my-graph-id --skip-snapshot
```
