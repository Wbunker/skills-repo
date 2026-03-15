# AWS Redshift — CLI Reference
For service concepts, see [redshift-capabilities.md](redshift-capabilities.md).

## Amazon Redshift (Provisioned)

```bash
# --- Cluster lifecycle ---
aws redshift create-cluster \
  --cluster-identifier my-cluster \
  --node-type ra3.xlplus \
  --master-username admin \
  --master-user-password 'P@ssw0rd!' \
  --number-of-nodes 2 \
  --cluster-subnet-group-name my-subnet-group \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --iam-roles arn:aws:iam::123456789012:role/RedshiftRole

aws redshift describe-clusters
aws redshift describe-clusters --cluster-identifier my-cluster

aws redshift modify-cluster \
  --cluster-identifier my-cluster \
  --master-user-password 'NewP@ssw0rd!' \
  --automated-snapshot-retention-period 7

aws redshift resize-cluster \
  --cluster-identifier my-cluster \
  --node-type ra3.4xlarge \
  --number-of-nodes 4

aws redshift reboot-cluster --cluster-identifier my-cluster

aws redshift pause-cluster --cluster-identifier my-cluster
aws redshift resume-cluster --cluster-identifier my-cluster

aws redshift delete-cluster \
  --cluster-identifier my-cluster \
  --final-cluster-snapshot-identifier my-cluster-final-snap

# --- Snapshots ---
aws redshift create-cluster-snapshot \
  --cluster-identifier my-cluster \
  --snapshot-identifier my-snap-$(date +%Y%m%d)

aws redshift describe-cluster-snapshots \
  --cluster-identifier my-cluster

aws redshift restore-from-cluster-snapshot \
  --cluster-identifier restored-cluster \
  --snapshot-identifier my-snap-20240101 \
  --node-type ra3.xlplus \
  --number-of-nodes 2

aws redshift delete-cluster-snapshot \
  --snapshot-identifier my-snap-20240101

# --- Subnet groups ---
aws redshift create-cluster-subnet-group \
  --cluster-subnet-group-name my-subnet-group \
  --description "Subnet group for Redshift" \
  --subnet-ids subnet-0123456789abcdef0 subnet-0987654321fedcba0

aws redshift describe-cluster-subnet-groups
aws redshift delete-cluster-subnet-group --cluster-subnet-group-name my-subnet-group

# --- Parameter groups ---
aws redshift create-cluster-parameter-group \
  --parameter-group-name my-params \
  --parameter-group-family redshift-1.0 \
  --description "Custom parameter group"

aws redshift modify-cluster-parameter-group \
  --parameter-group-name my-params \
  --parameters 'ParameterName=enable_user_activity_logging,ParameterValue=true,ApplyType=static'

aws redshift describe-cluster-parameter-groups
aws redshift delete-cluster-parameter-group --parameter-group-name my-params

# --- Credentials ---
aws redshift get-cluster-credentials \
  --cluster-identifier my-cluster \
  --db-user temp_user \
  --db-name dev \
  --duration-seconds 3600 \
  --auto-create

aws redshift get-cluster-credentials-with-iam \
  --cluster-identifier my-cluster \
  --db-name dev

# --- Data sharing ---
aws redshift describe-data-shares
aws redshift describe-data-shares-for-producer --producer-arn arn:aws:redshift:us-east-1:123456789012:namespace:...
aws redshift authorize-data-share \
  --data-share-arn arn:aws:redshift:us-east-1:123456789012:datashare:... \
  --consumer-identifier 210987654321

aws redshift associate-data-share-consumer \
  --data-share-arn arn:aws:redshift:us-east-1:123456789012:datashare:... \
  --consumer-arn arn:aws:redshift:us-east-1:210987654321:namespace:...

# --- AQUA ---
aws redshift modify-aqua-configuration \
  --cluster-identifier my-cluster \
  --aqua-configuration-status enabled

# --- IAM roles ---
aws redshift modify-cluster-iam-roles \
  --cluster-identifier my-cluster \
  --add-iam-roles arn:aws:iam::123456789012:role/NewRedshiftRole

# --- Usage limits ---
aws redshift create-usage-limit \
  --cluster-identifier my-cluster \
  --feature-type concurrency-scaling \
  --limit-type time \
  --amount 60 \
  --breach-action log

aws redshift describe-usage-limits --cluster-identifier my-cluster
```

---

## Amazon Redshift Serverless

```bash
# --- Namespace (data/storage layer) ---
aws redshift-serverless create-namespace \
  --namespace-name my-namespace \
  --admin-username admin \
  --admin-user-password 'P@ssw0rd!' \
  --db-name dev \
  --iam-roles arn:aws:iam::123456789012:role/RedshiftServerlessRole

aws redshift-serverless get-namespace --namespace-name my-namespace
aws redshift-serverless list-namespaces

aws redshift-serverless update-namespace \
  --namespace-name my-namespace \
  --admin-user-password 'NewP@ssw0rd!'

aws redshift-serverless delete-namespace \
  --namespace-name my-namespace \
  --final-snapshot-name my-namespace-final-snap

# --- Workgroup (compute layer) ---
aws redshift-serverless create-workgroup \
  --workgroup-name my-workgroup \
  --namespace-name my-namespace \
  --base-capacity 8 \
  --subnet-ids subnet-0123456789abcdef0 subnet-0987654321fedcba0 \
  --security-group-ids sg-0123456789abcdef0

aws redshift-serverless get-workgroup --workgroup-name my-workgroup
aws redshift-serverless list-workgroups

aws redshift-serverless update-workgroup \
  --workgroup-name my-workgroup \
  --base-capacity 16 \
  --max-capacity 128

aws redshift-serverless delete-workgroup --workgroup-name my-workgroup

# --- Snapshots ---
aws redshift-serverless create-snapshot \
  --namespace-name my-namespace \
  --snapshot-name my-snap-$(date +%Y%m%d)

aws redshift-serverless list-snapshots --namespace-name my-namespace

aws redshift-serverless restore-from-snapshot \
  --namespace-name restored-namespace \
  --workgroup-name restored-workgroup \
  --snapshot-name my-snap-20240101

aws redshift-serverless delete-snapshot --snapshot-name my-snap-20240101

# --- Endpoint access (VPC endpoint) ---
aws redshift-serverless create-endpoint-access \
  --endpoint-name my-endpoint \
  --workgroup-name my-workgroup \
  --subnet-ids subnet-0123456789abcdef0 \
  --vpc-security-group-ids sg-0123456789abcdef0

aws redshift-serverless list-endpoint-access
aws redshift-serverless delete-endpoint-access --endpoint-name my-endpoint
```

---

## Redshift Data API

Execute SQL against both Serverless and Provisioned clusters without managing connections.

```bash
# --- Execute against Serverless ---
aws redshift-data execute-statement \
  --workgroup-name my-workgroup \
  --database dev \
  --sql "SELECT COUNT(*) FROM orders"

# --- Execute against Provisioned ---
aws redshift-data execute-statement \
  --cluster-identifier my-cluster \
  --database dev \
  --db-user admin \
  --sql "SELECT COUNT(*) FROM orders"

# --- Check status ---
aws redshift-data describe-statement \
  --id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# --- Get results ---
aws redshift-data get-statement-result \
  --id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# --- Batch execute (multiple statements in a transaction) ---
aws redshift-data batch-execute-statement \
  --workgroup-name my-workgroup \
  --database dev \
  --sqls "INSERT INTO t1 VALUES (1)" "INSERT INTO t2 VALUES (2)"

# --- List recent statements ---
aws redshift-data list-statements \
  --workgroup-name my-workgroup \
  --status FINISHED

# --- List tables and schemas ---
aws redshift-data list-databases \
  --workgroup-name my-workgroup

aws redshift-data list-schemas \
  --workgroup-name my-workgroup \
  --database dev

aws redshift-data list-tables \
  --workgroup-name my-workgroup \
  --database dev \
  --schema-pattern public
```
