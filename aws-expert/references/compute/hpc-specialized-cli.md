# HPC & Specialized Compute — CLI Reference

For service concepts, see [hpc-specialized-capabilities.md](hpc-specialized-capabilities.md).

## AWS ParallelCluster / AWS PCS

```bash
# --- ParallelCluster CLI (pcluster) ---
# Install ParallelCluster CLI
pip install aws-parallelcluster

# Create a cluster from a YAML config file
pcluster create-cluster \
  --cluster-name my-hpc-cluster \
  --cluster-configuration cluster-config.yaml \
  --region us-east-1

# cluster-config.yaml example (multi-queue with FSx for Lustre):
# Region: us-east-1
# Image:
#   Os: alinux2
# HeadNode:
#   InstanceType: c5.xlarge
#   Networking:
#     SubnetId: subnet-0abc123
#   Ssh:
#     KeyName: my-keypair
#   CustomActions:
#     OnNodeConfigured:
#       Script: s3://my-bucket/scripts/head-node-setup.sh
# Scheduling:
#   Scheduler: slurm
#   SlurmQueues:
#     - Name: cpu-queue
#       ComputeResources:
#         - Name: c5-nodes
#           InstanceType: c5n.18xlarge
#           MinCount: 0
#           MaxCount: 64
#           Efa:
#             Enabled: true
#       Networking:
#         SubnetIds: [subnet-0abc123]
#         PlacementGroup:
#           Enabled: true
#       CustomActions:
#         OnNodeConfigured:
#           Script: s3://my-bucket/scripts/compute-setup.sh
#     - Name: gpu-queue
#       ComputeResources:
#         - Name: p4d-nodes
#           InstanceType: p4d.24xlarge
#           MinCount: 0
#           MaxCount: 8
#       Networking:
#         SubnetIds: [subnet-0abc123]
# SharedStorage:
#   - MountDir: /scratch
#     Name: fsx-scratch
#     StorageType: FsxLustre
#     FsxLustreSettings:
#       StorageCapacity: 1200
#       DeploymentType: SCRATCH_2
#       ImportPath: s3://my-data-bucket/inputs
#       ExportPath: s3://my-data-bucket/outputs
#   - MountDir: /home
#     Name: efs-home
#     StorageType: Efs
#     EfsSettings:
#       Encrypted: true

# Describe a cluster
pcluster describe-cluster --cluster-name my-hpc-cluster

# List all clusters
pcluster list-clusters

# SSH into the head node
pcluster ssh --cluster-name my-hpc-cluster -i ~/.ssh/my-keypair.pem

# Update a cluster (update config and rolling update compute nodes)
pcluster update-cluster \
  --cluster-name my-hpc-cluster \
  --cluster-configuration cluster-config-v2.yaml

# Delete a cluster
pcluster delete-cluster --cluster-name my-hpc-cluster

# List available instance types and their HPC features
pcluster list-official-images --region us-east-1

# Export cluster logs to S3 for debugging
pcluster export-cluster-logs \
  --cluster-name my-hpc-cluster \
  --bucket my-logs-bucket \
  --bucket-prefix my-hpc-cluster/logs

# Get the cluster stack events (CloudFormation)
pcluster get-cluster-stack-events --cluster-name my-hpc-cluster

# --- Slurm job submission (run on head node) ---
# Submit a simple MPI job
srun --nodes=4 --ntasks-per-node=36 --partition=cpu-queue \
  mpirun -np 144 ./my-mpi-application

# Submit via sbatch script
sbatch <<'SBATCH'
#!/bin/bash
#SBATCH --job-name=cfd-sim
#SBATCH --partition=cpu-queue
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=36
#SBATCH --time=04:00:00
#SBATCH --output=/home/ec2-user/logs/%j.out

module load openmpi
mpirun ./cfd-solver --input /scratch/case1/input.dat --output /scratch/case1/output/
SBATCH

# Check job status
squeue -u $USER
squeue -p cpu-queue

# Cancel a job
scancel 12345

# Check node status
sinfo
sinfo -p gpu-queue -N

# --- AWS PCS (Parallel Computing Service) CLI ---
# Create a PCS cluster
aws pcs create-cluster \
  --name my-pcs-cluster \
  --scheduler '{"type": "SLURM", "version": "23.11"}' \
  --size MEDIUM \
  --networking '{
    "subnetIds": ["subnet-0abc123"],
    "securityGroupIds": ["sg-0abc123def456789"]
  }' \
  --region us-east-1

# Describe a PCS cluster
aws pcs get-cluster \
  --cluster-identifier my-pcs-cluster \
  --region us-east-1

# List PCS clusters
aws pcs list-clusters --region us-east-1

# Create a compute node group
aws pcs create-compute-node-group \
  --cluster-identifier my-pcs-cluster \
  --name cpu-node-group \
  --ami-id ami-0abcdef1234567890 \
  --subnet-ids '["subnet-0abc123"]' \
  --purchase-option ON_DEMAND \
  --iam-instance-profile-arn arn:aws:iam::123456789012:instance-profile/PCSNodeInstanceProfile \
  --instance-configs '[{"instanceType": "c5n.18xlarge"}]' \
  --scaling-config '{"minInstanceCount": 0, "maxInstanceCount": 64}' \
  --region us-east-1

# List compute node groups in a cluster
aws pcs list-compute-node-groups \
  --cluster-identifier my-pcs-cluster \
  --region us-east-1

# Create a Slurm queue mapped to the compute node group
aws pcs create-queue \
  --cluster-identifier my-pcs-cluster \
  --name cpu-queue \
  --compute-node-group-configurations '[
    {"computeNodeGroupId": "cng-0abc123"}
  ]' \
  --region us-east-1

# List queues
aws pcs list-queues \
  --cluster-identifier my-pcs-cluster \
  --region us-east-1

# Delete a PCS cluster
aws pcs delete-cluster \
  --cluster-identifier my-pcs-cluster \
  --region us-east-1
```

---

## AWS SimSpace Weaver

```bash
# --- Simulation Management ---
# Start a simulation from an app package in S3
aws simspaceweaver start-simulation \
  --name my-city-sim \
  --role-arn arn:aws:iam::123456789012:role/SimSpaceWeaverRole \
  --schema-s3-location '{
    "BucketName": "my-simspaceweaver-bucket",
    "ObjectKey": "schemas/city-traffic-sim.yaml"
  }' \
  --region us-east-1

# Start simulation from a snapshot (resume from saved state)
aws simspaceweaver start-simulation \
  --name my-city-sim-resumed \
  --role-arn arn:aws:iam::123456789012:role/SimSpaceWeaverRole \
  --schema-s3-location '{
    "BucketName": "my-simspaceweaver-bucket",
    "ObjectKey": "schemas/city-traffic-sim.yaml"
  }' \
  --snapshot '{
    "S3Location": {
      "BucketName": "my-simspaceweaver-bucket",
      "ObjectKey": "snapshots/city-traffic-sim/snapshot-2024-01-15T12:00:00Z"
    }
  }' \
  --region us-east-1

# Describe a simulation (check status, worker count, app states)
aws simspaceweaver describe-simulation \
  --simulation my-city-sim \
  --region us-east-1

# List all simulations
aws simspaceweaver list-simulations --region us-east-1

# Stop a running simulation
aws simspaceweaver stop-simulation \
  --simulation my-city-sim \
  --region us-east-1

# Delete a stopped simulation
aws simspaceweaver delete-simulation \
  --simulation my-city-sim \
  --region us-east-1

# --- App Management ---
# Start a custom app within a running simulation
aws simspaceweaver start-app \
  --simulation my-city-sim \
  --domain-name MyDomain \
  --name analytics-app \
  --launch-overrides '{
    "Command": ["/app/analytics", "--mode", "realtime"],
    "EnvironmentVariables": [
      {"Name": "SAMPLE_RATE", "Value": "10"}
    ]
  }' \
  --region us-east-1

# Describe a running app
aws simspaceweaver describe-app \
  --simulation my-city-sim \
  --domain MyDomain \
  --app analytics-app \
  --region us-east-1

# List apps in a simulation
aws simspaceweaver list-apps \
  --simulation my-city-sim \
  --region us-east-1

# Stop a specific app
aws simspaceweaver stop-app \
  --simulation my-city-sim \
  --domain MyDomain \
  --app analytics-app \
  --region us-east-1

# Delete a stopped app
aws simspaceweaver delete-app \
  --simulation my-city-sim \
  --domain MyDomain \
  --app analytics-app \
  --region us-east-1

# --- Snapshots ---
# Create a snapshot of simulation state to S3
aws simspaceweaver create-snapshot \
  --simulation my-city-sim \
  --destination '{
    "S3Destination": {
      "BucketName": "my-simspaceweaver-bucket",
      "ObjectKeyPrefix": "snapshots/city-traffic-sim/"
    }
  }' \
  --region us-east-1

# --- Tagging ---
# Tag a simulation for cost allocation
aws simspaceweaver tag-resource \
  --resource-arn arn:aws:simspaceweaver:us-east-1:123456789012:simulation/my-city-sim \
  --tags '{"Project": "urban-planning", "Environment": "production"}' \
  --region us-east-1

# List tags on a simulation
aws simspaceweaver list-tags-for-resource \
  --resource-arn arn:aws:simspaceweaver:us-east-1:123456789012:simulation/my-city-sim \
  --region us-east-1
```

---

## AWS Elastic VMware Service (EVS)

```bash
# --- EVS Environment Management ---
# Create an EVS environment (deploys vCenter, vSAN, NSX-T on bare metal)
aws evs create-environment \
  --environment-name my-evs-env \
  --vpc-id vpc-0abc123def456789 \
  --service-access-subnet-id subnet-0abc123 \
  --vcenter-configuration '{
    "datacenter": "my-aws-datacenter",
    "cluster": "my-vsphere-cluster",
    "morefFolder": "/my-aws-datacenter/vm",
    "resourcePool": "/my-aws-datacenter/host/my-vsphere-cluster/Resources",
    "datastore": "vsanDatastore"
  }' \
  --initial-vlan-info '[
    {"cidr": "192.168.0.0/24", "vlanId": 100, "function": "MANAGEMENT"},
    {"cidr": "192.168.1.0/24", "vlanId": 101, "function": "VMOTION"},
    {"cidr": "192.168.2.0/24", "vlanId": 102, "function": "REPLICATION"},
    {"cidr": "192.168.3.0/24", "vlanId": 103, "function": "UPLINK1"},
    {"cidr": "192.168.4.0/24", "vlanId": 104, "function": "UPLINK2"},
    {"cidr": "192.168.5.0/24", "vlanId": 105, "function": "VSAN"},
    {"cidr": "192.168.6.0/24", "vlanId": 106, "function": "NSXT_EDGE_UPLINK1"},
    {"cidr": "192.168.7.0/24", "vlanId": 107, "function": "NSXT_EDGE_UPLINK2"},
    {"cidr": "192.168.8.0/24", "vlanId": 108, "function": "NSXT_EDGE_TEP"},
    {"cidr": "192.168.9.0/24", "vlanId": 109, "function": "NSXT_HOST_TEP"}
  ]' \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abcd1234-ab12-ab12-ab12-abcdef123456 \
  --region us-east-1

# Describe an EVS environment
aws evs get-environment \
  --environment-id env-0abc123def456789 \
  --region us-east-1

# List all EVS environments
aws evs list-environments --region us-east-1

# --- EVS Host Management ---
# Create (add) a host to an EVS environment
aws evs create-environment-host \
  --environment-id env-0abc123def456789 \
  --host '{
    "hostName": "esxi-host-01",
    "keyName": "my-keypair",
    "instanceType": "i4i.metal"
  }' \
  --region us-east-1

# List hosts in an EVS environment
aws evs list-environment-hosts \
  --environment-id env-0abc123def456789 \
  --region us-east-1

# Get details of a specific host
aws evs get-environment-host \
  --environment-id env-0abc123def456789 \
  --host-id host-0abc123 \
  --region us-east-1

# Delete a host from an EVS environment (drain from vSphere first)
aws evs delete-environment-host \
  --environment-id env-0abc123def456789 \
  --host-id host-0abc123 \
  --region us-east-1

# --- VLANs ---
# List VLANs associated with an EVS environment
aws evs list-environment-vlans \
  --environment-id env-0abc123def456789 \
  --region us-east-1

# --- Tagging ---
# Tag an EVS environment for cost tracking
aws evs tag-resource \
  --resource-arn arn:aws:evs:us-east-1:123456789012:environment/env-0abc123def456789 \
  --tags '{"CostCenter": "vmware-migration", "Owner": "infra-team"}' \
  --region us-east-1

# List tags on an EVS environment
aws evs list-tags-for-resource \
  --resource-arn arn:aws:evs:us-east-1:123456789012:environment/env-0abc123def456789 \
  --region us-east-1
```
