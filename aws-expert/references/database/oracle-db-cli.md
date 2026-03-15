# Oracle Database@AWS — CLI Reference
For service concepts, see [oracle-db-capabilities.md](oracle-db-capabilities.md).

## Oracle Database@AWS (`aws odb`)

> **Prerequisite**: AWS CLI v2.27.47 or higher required for `odb` subcommands.
> Oracle-layer operations (database creation, patching, Data Guard, GoldenGate) are performed through OCI APIs and tools after AWS-layer infrastructure is provisioned.

```bash
# --- Service Initialization & Onboarding ---
aws odb initialize-service
aws odb get-oci-onboarding-status

# --- Discover Available Shapes and Versions ---
aws odb list-db-system-shapes
aws odb list-gi-versions                  # Oracle Grid Infrastructure versions
aws odb list-system-versions

# Map logical AZ names to physical IDs (Oracle Database@AWS requires physical AZ IDs)
aws ec2 describe-availability-zones \
  --region us-east-1 \
  --query "AvailabilityZones[*].{ZoneName:ZoneName, ZoneId:ZoneId}" \
  --output table

# --- ODB Networks ---
aws odb create-odb-network \
  --display-name my-odb-network \
  --availability-zone-id use1-az4 \
  --client-subnet-cidr 10.0.1.0/24 \
  --backup-subnet-cidr 10.0.2.0/24 \
  --s3-access ENABLED \
  --zero-etl-access ENABLED

aws odb list-odb-networks
aws odb get-odb-network --odb-network-id odbnet-0abc1234567890000

aws odb update-odb-network \
  --odb-network-id odbnet-0abc1234567890000 \
  --s3-access ENABLED

aws odb delete-odb-network --odb-network-id odbnet-0abc1234567890000

# --- ODB Peering Connections ---
# Connect an Amazon VPC to an ODB Network for private connectivity
aws odb create-odb-peering-connection \
  --odb-network-id odbnet-0abc1234567890000 \
  --vpc-id vpc-0abc1234567890000 \
  --display-name my-odb-peering

aws odb list-odb-peering-connections
aws odb get-odb-peering-connection --odb-peering-connection-id odbpcx-0abc1234567890000

# After peering is created, manually add a route in the application VPC route table
aws ec2 create-route \
  --route-table-id rtb-0abc1234567890000 \
  --destination-cidr-block 10.0.1.0/24 \
  --vpc-peering-connection-id odbpcx-0abc1234567890000

aws odb update-odb-peering-connection \
  --odb-peering-connection-id odbpcx-0abc1234567890000 \
  --display-name updated-peering

aws odb delete-odb-peering-connection --odb-peering-connection-id odbpcx-0abc1234567890000

# --- Cloud Exadata Infrastructure ---
aws odb create-cloud-exadata-infrastructure \
  --display-name my-exadata-infra \
  --availability-zone-id use1-az4 \
  --shape Exadata.X11M \
  --compute-count 2 \
  --storage-count 3

aws odb list-cloud-exadata-infrastructures
aws odb get-cloud-exadata-infrastructure \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1...

aws odb get-cloud-exadata-infrastructure-unallocated-resources \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1...

aws odb update-cloud-exadata-infrastructure \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1... \
  --compute-count 4

aws odb delete-cloud-exadata-infrastructure \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1...

# --- Cloud VM Clusters (Exadata Database Service) ---
# Customer manages the Oracle database layer; Oracle manages infrastructure
aws odb create-cloud-vm-cluster \
  --display-name my-vm-cluster \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1... \
  --odb-network-id odbnet-0abc1234567890000 \
  --cpu-core-count 4 \
  --gi-version 19.0.0.0 \
  --hostname-prefix mydb \
  --ssh-public-keys file://~/.ssh/id_rsa.pub \
  --db-servers '["ocid1.dbserver.oc1...a","ocid1.dbserver.oc1...b"]'

aws odb list-cloud-vm-clusters
aws odb get-cloud-vm-cluster --cloud-vm-cluster-id ocid1.cloudvmcluster.oc1...

aws odb delete-cloud-vm-cluster --cloud-vm-cluster-id ocid1.cloudvmcluster.oc1...

# --- Autonomous VM Clusters (Oracle Autonomous AI Database) ---
# Oracle manages the full stack; no manual database administration required
aws odb create-cloud-autonomous-vm-cluster \
  --display-name my-auto-vm-cluster \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1... \
  --odb-network-id odbnet-0abc1234567890000 \
  --cpu-core-count-per-node 4 \
  --memory-per-oracle-compute-unit-in-gbs 15 \
  --total-container-databases 5 \
  --autonomous-data-storage-size-in-tbs 10.0

aws odb list-cloud-autonomous-vm-clusters
aws odb get-cloud-autonomous-vm-cluster \
  --cloud-autonomous-vm-cluster-id ocid1.cloudautonomousvmcluster.oc1...

aws odb list-autonomous-virtual-machines \
  --cloud-autonomous-vm-cluster-id ocid1.cloudautonomousvmcluster.oc1...

aws odb delete-cloud-autonomous-vm-cluster \
  --cloud-autonomous-vm-cluster-id ocid1.cloudautonomousvmcluster.oc1...

# --- Database Nodes & Servers ---
aws odb list-db-nodes --cloud-vm-cluster-id ocid1.cloudvmcluster.oc1...
aws odb get-db-node --db-node-id ocid1.dbnode.oc1...

aws odb start-db-node --db-node-id ocid1.dbnode.oc1...
aws odb stop-db-node --db-node-id ocid1.dbnode.oc1...
aws odb reboot-db-node --db-node-id ocid1.dbnode.oc1...

aws odb list-db-servers \
  --cloud-exadata-infrastructure-id ocid1.cloudexadatainfrastructure.oc1...
aws odb get-db-server --db-server-id ocid1.dbserver.oc1...

# --- IAM Role Associations ---
aws odb associate-iam-role-to-resource \
  --resource-id ocid1.cloudvmcluster.oc1... \
  --role-arn arn:aws:iam::123456789012:role/OracleDBRole

aws odb disassociate-iam-role-from-resource \
  --resource-id ocid1.cloudvmcluster.oc1... \
  --role-arn arn:aws:iam::123456789012:role/OracleDBRole

# --- Tagging ---
aws odb tag-resource \
  --resource-id ocid1.cloudvmcluster.oc1... \
  --tags '{"Environment":"prod","Team":"dba"}'

aws odb list-tags-for-resource --resource-id ocid1.cloudvmcluster.oc1...

aws odb untag-resource \
  --resource-id ocid1.cloudvmcluster.oc1... \
  --tag-keys Environment Team

# --- AWS Marketplace Registration ---
aws odb accept-marketplace-registration
```

## Notes on OCI Tool Usage

After provisioning the AWS-layer infrastructure (Exadata hardware, ODB network, VM cluster) via `aws odb`, Oracle-layer operations are performed through the OCI CLI or OCI Console:

```bash
# OCI CLI examples (requires OCI CLI and credentials configured)

# Create an Oracle Database on a VM Cluster
oci db database create \
  --vm-cluster-id ocid1.cloudvmcluster.oc1... \
  --db-home-id ocid1.dbhome.oc1... \
  --db-version 19.0.0.0 \
  --db-name MYPROD \
  --admin-password <password>

# Configure Oracle Data Guard
oci db data-guard-association create \
  --database-id ocid1.database.oc1... \
  --creation-type NewDbSystem \
  --database-admin-password <password> \
  --protection-mode MAXIMUM_PERFORMANCE \
  --transport-type ASYNC

# Initiate Data Guard switchover
oci db data-guard-association switchover \
  --database-id ocid1.database.oc1... \
  --data-guard-association-id ocid1.dataguardassociation.oc1... \
  --database-admin-password <password>
```

## CloudFormation / Infrastructure-as-Code

Oracle Database@AWS resources are also available via AWS CloudFormation, AWS CDK (L1 constructs), and Terraform:

```bash
# Deploy an Oracle Database@AWS stack via CloudFormation
aws cloudformation deploy \
  --template-file oracle-db-aws-stack.yaml \
  --stack-name my-oracle-db-stack \
  --capabilities CAPABILITY_IAM

aws cloudformation describe-stacks --stack-name my-oracle-db-stack
```
