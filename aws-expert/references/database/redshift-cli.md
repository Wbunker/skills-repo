# AWS Redshift — CLI Reference
For service concepts, see [redshift-capabilities.md](redshift-capabilities.md).

## Amazon Redshift

```bash
# --- Provisioned Clusters ---
aws redshift create-cluster \
  --cluster-identifier my-redshift \
  --cluster-type multi-node \
  --node-type ra3.xlplus \
  --number-of-nodes 3 \
  --master-username admin \
  --master-user-password Secret99! \
  --db-name dev \
  --cluster-subnet-group-name my-redshift-subnets \
  --vpc-security-group-ids sg-12345678 \
  --encrypted \
  --enhanced-vpc-routing

aws redshift describe-clusters
aws redshift describe-clusters --cluster-identifier my-redshift

aws redshift modify-cluster \
  --cluster-identifier my-redshift \
  --node-type ra3.4xlarge \
  --number-of-nodes 4

aws redshift reboot-cluster --cluster-identifier my-redshift

aws redshift delete-cluster \
  --cluster-identifier my-redshift \
  --final-cluster-snapshot-identifier my-redshift-final-snap

# Pause / resume (save compute costs)
aws redshift pause-cluster --cluster-identifier my-redshift
aws redshift resume-cluster --cluster-identifier my-redshift

# --- Snapshots ---
aws redshift create-cluster-snapshot \
  --cluster-identifier my-redshift \
  --snapshot-identifier my-redshift-snap-$(date +%Y%m%d)

aws redshift describe-cluster-snapshots --cluster-identifier my-redshift
aws redshift describe-cluster-snapshots --snapshot-type manual

aws redshift copy-cluster-snapshot \
  --source-snapshot-identifier my-redshift-snap-20240101 \
  --source-snapshot-cluster-identifier my-redshift \
  --target-snapshot-identifier my-redshift-snap-copy

aws redshift restore-from-cluster-snapshot \
  --cluster-identifier my-redshift-restored \
  --snapshot-identifier my-redshift-snap-20240101 \
  --node-type ra3.xlplus \
  --number-of-nodes 3

aws redshift delete-cluster-snapshot \
  --snapshot-identifier my-redshift-snap-20240101

# --- Subnet and Security Groups ---
aws redshift create-cluster-subnet-group \
  --cluster-subnet-group-name my-redshift-subnets \
  --description "Redshift subnet group" \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc

aws redshift create-cluster-security-group \
  --cluster-security-group-name my-redshift-sg \
  --description "Redshift security group"

# --- Parameter Groups ---
aws redshift create-cluster-parameter-group \
  --parameter-group-name my-redshift-params \
  --parameter-group-family redshift-1.0 \
  --description "Custom Redshift parameters"

aws redshift modify-cluster-parameter-group \
  --parameter-group-name my-redshift-params \
  --parameters "ParameterName=enable_user_activity_logging,ParameterValue=true,ApplyType=static"

# --- Concurrency Scaling & WLM ---
aws redshift modify-cluster \
  --cluster-identifier my-redshift \
  --cluster-parameter-group-name my-redshift-params

# --- Data Sharing ---
aws redshift create-data-share --data-share-name sales-share
aws redshift authorize-data-share \
  --data-share-arn arn:aws:redshift:us-east-1:123456789012:datashare:cluster-id/sales-share \
  --consumer-identifier 999999999999  # consumer AWS account ID

aws redshift describe-data-shares
aws redshift describe-data-shares-for-producer --status ACTIVE

# Consumer side
aws redshift describe-data-shares-for-consumer
aws redshift associate-data-share-consumer \
  --data-share-arn arn:aws:redshift:us-east-1:123456789012:datashare:cluster-id/sales-share \
  --consumer-arn arn:aws:redshift:us-east-1:999999999999:namespace:consumer-namespace-id

# --- Serverless ---
aws redshift-serverless create-namespace \
  --namespace-name my-namespace \
  --admin-username admin \
  --admin-user-password Secret99! \
  --db-name dev

aws redshift-serverless create-workgroup \
  --workgroup-name my-workgroup \
  --namespace-name my-namespace \
  --base-capacity 32 \
  --subnet-ids subnet-aaa subnet-bbb subnet-ccc \
  --security-group-ids sg-12345678 \
  --enhanced-vpc-routing

aws redshift-serverless list-workgroups
aws redshift-serverless get-workgroup --workgroup-name my-workgroup
aws redshift-serverless list-namespaces
aws redshift-serverless get-namespace --namespace-name my-namespace

aws redshift-serverless update-workgroup \
  --workgroup-name my-workgroup \
  --base-capacity 64

# Serverless snapshots
aws redshift-serverless create-snapshot \
  --namespace-name my-namespace \
  --snapshot-name my-serverless-snap-$(date +%Y%m%d)

aws redshift-serverless list-snapshots --namespace-name my-namespace

aws redshift-serverless restore-from-snapshot \
  --namespace-name my-namespace-restored \
  --workgroup-name my-workgroup-restored \
  --snapshot-name my-serverless-snap-20240101

aws redshift-serverless delete-workgroup --workgroup-name my-workgroup
aws redshift-serverless delete-namespace --namespace-name my-namespace
```
