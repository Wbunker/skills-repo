# AWS Aurora & RDS — CLI Reference
For service concepts, see [aurora-rds-capabilities.md](aurora-rds-capabilities.md).

## Amazon RDS & Aurora

```bash
# --- DB Instances (RDS) ---
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.medium \
  --engine mysql \
  --master-username admin \
  --master-user-password secret99 \
  --allocated-storage 20 \
  --multi-az \
  --storage-encrypted

aws rds describe-db-instances
aws rds describe-db-instances --db-instance-identifier mydb

aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.r6g.large \
  --apply-immediately

aws rds stop-db-instance --db-instance-identifier mydb
aws rds start-db-instance --db-instance-identifier mydb
aws rds reboot-db-instance --db-instance-identifier mydb

aws rds delete-db-instance \
  --db-instance-identifier mydb \
  --final-db-snapshot-identifier mydb-final-snap
  # add --skip-final-snapshot to skip

# --- Snapshots ---
aws rds create-db-snapshot \
  --db-instance-identifier mydb \
  --db-snapshot-identifier mydb-snap-$(date +%Y%m%d)

aws rds describe-db-snapshots --db-instance-identifier mydb
aws rds describe-db-snapshots --snapshot-type manual

aws rds copy-db-snapshot \
  --source-db-snapshot-identifier mydb-snap-20240101 \
  --target-db-snapshot-identifier mydb-snap-copy \
  --copy-tags

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mydb-restored \
  --db-snapshot-identifier mydb-snap-20240101 \
  --db-instance-class db.t3.medium

aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier mydb \
  --target-db-instance-identifier mydb-pitr \
  --restore-time 2024-01-15T12:00:00Z

aws rds delete-db-snapshot --db-snapshot-identifier mydb-snap-20240101

# --- Aurora Clusters ---
aws rds create-db-cluster \
  --db-cluster-identifier my-aurora-cluster \
  --engine aurora-mysql \
  --engine-version 8.0.mysql_aurora.3.04.0 \
  --master-username admin \
  --master-user-password secret99 \
  --db-subnet-group-name my-subnet-group \
  --vpc-security-group-ids sg-12345678 \
  --storage-encrypted \
  --enable-cloudwatch-logs-exports '["audit","error","general","slowquery"]'

# Add an instance to an Aurora cluster
aws rds create-db-instance \
  --db-instance-identifier my-aurora-writer \
  --db-cluster-identifier my-aurora-cluster \
  --db-instance-class db.r6g.large \
  --engine aurora-mysql

aws rds describe-db-clusters
aws rds describe-db-clusters --db-cluster-identifier my-aurora-cluster

aws rds modify-db-cluster \
  --db-cluster-identifier my-aurora-cluster \
  --backup-retention-period 14 \
  --apply-immediately

aws rds failover-db-cluster \
  --db-cluster-identifier my-aurora-cluster
  # optionally: --target-db-instance-identifier my-aurora-reader

aws rds delete-db-cluster \
  --db-cluster-identifier my-aurora-cluster \
  --final-db-cluster-snapshot-identifier my-aurora-final-snap

# Aurora cluster snapshots
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier my-aurora-cluster \
  --db-cluster-snapshot-identifier my-aurora-snap-$(date +%Y%m%d)

aws rds describe-db-cluster-snapshots --db-cluster-identifier my-aurora-cluster

aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier my-aurora-restored \
  --snapshot-identifier my-aurora-snap-20240101 \
  --engine aurora-mysql

# Aurora Backtrack (MySQL only)
aws rds backtrack-db-cluster \
  --db-cluster-identifier my-aurora-cluster \
  --backtrack-to 2024-01-15T08:00:00Z \
  --force-backtrack \
  --use-earliest-time-on-point-in-time-unavailable

# --- Read Replicas ---
aws rds create-db-instance-read-replica \
  --db-instance-identifier mydb-replica \
  --source-db-instance-identifier mydb \
  --db-instance-class db.t3.medium

# Cross-region read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier mydb-replica-eu \
  --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:mydb \
  --db-instance-class db.t3.medium \
  --region eu-west-1

aws rds promote-read-replica --db-instance-identifier mydb-replica

# --- RDS Proxy ---
aws rds create-db-proxy \
  --db-proxy-name my-rds-proxy \
  --engine-family MYSQL \
  --auth '[{"AuthScheme":"SECRETS","SecretArn":"arn:aws:secretsmanager:us-east-1:123456789012:secret:my-db-secret","IAMAuth":"DISABLED"}]' \
  --role-arn arn:aws:iam::123456789012:role/RDSProxyRole \
  --vpc-subnet-ids subnet-aaa subnet-bbb

aws rds describe-db-proxies
aws rds describe-db-proxies --db-proxy-name my-rds-proxy

aws rds register-db-proxy-targets \
  --db-proxy-name my-rds-proxy \
  --db-instance-identifiers mydb

aws rds describe-db-proxy-targets --db-proxy-name my-rds-proxy
aws rds delete-db-proxy --db-proxy-name my-rds-proxy

# --- Parameter Groups ---
aws rds create-db-parameter-group \
  --db-parameter-group-name my-mysql8-params \
  --db-parameter-group-family mysql8.0 \
  --description "Custom MySQL 8.0 parameters"

aws rds modify-db-parameter-group \
  --db-parameter-group-name my-mysql8-params \
  --parameters "ParameterName=max_connections,ParameterValue=500,ApplyMethod=pending-reboot"

aws rds describe-db-parameters --db-parameter-group-name my-mysql8-params

# --- Subnet Groups ---
aws rds create-db-subnet-group \
  --db-subnet-group-name my-subnet-group \
  --db-subnet-group-description "Multi-AZ subnets" \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc

# --- Event Subscriptions ---
aws rds create-event-subscription \
  --subscription-name db-events \
  --sns-topic-arn arn:aws:sns:us-east-1:123456789012:my-db-alerts \
  --source-type db-instance \
  --event-categories '["availability","failure","maintenance"]' \
  --source-ids mydb

aws rds add-source-identifier-to-subscription \
  --subscription-name db-events \
  --source-identifier mydb-replica

aws rds describe-event-subscriptions

# --- Performance Insights ---
aws pi describe-dimension-keys \
  --service-type RDS \
  --identifier db-XXXXXXXX \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T01:00:00Z \
  --metric db.load.avg \
  --group-by '{"Group":"db.sql","Dimensions":["db.sql.statement"],"Limit":10}'
```
