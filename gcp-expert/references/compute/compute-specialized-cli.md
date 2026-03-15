# Compute Specialized — CLI Reference

Capabilities reference: [compute-specialized-capabilities.md](compute-specialized-capabilities.md)

---

## TPUs

### Create and Manage TPU VMs

```bash
# List available TPU accelerator types in a zone
gcloud compute tpus accelerator-types list --zone=us-central1-b

# List available TPU VM runtime versions
gcloud compute tpus versions list --zone=us-central1-b

# Create a single TPU v4 VM (v4-8 = 8 chips / 1 host)
gcloud compute tpus tpu-vm create my-tpu-vm \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-tf-2.16.0-pjrt

# Create a TPU v5e pod slice (v5litepod-16 = 16 chips)
gcloud compute tpus tpu-vm create my-tpu-slice \
  --zone=us-east1-c \
  --accelerator-type=v5litepod-16 \
  --version=tpu-vm-tf-2.16.0-pjrt

# Create a TPU VM with a startup script
gcloud compute tpus tpu-vm create my-tpu-vm \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-jax-stable-stack \
  --metadata=startup-script='#!/bin/bash
pip install -q jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html'

# List TPU VMs
gcloud compute tpus tpu-vm list --zone=us-central1-b

# Describe a TPU VM
gcloud compute tpus tpu-vm describe my-tpu-vm --zone=us-central1-b

# SSH into a TPU VM
gcloud compute tpus tpu-vm ssh my-tpu-vm --zone=us-central1-b

# SSH into a specific host in a multi-host TPU slice (worker index)
gcloud compute tpus tpu-vm ssh my-tpu-slice \
  --zone=us-east1-c \
  --worker=0

# Run a command on all workers of a multi-host slice
gcloud compute tpus tpu-vm ssh my-tpu-slice \
  --zone=us-east1-c \
  --worker=all \
  --command="python3 /home/user/verify_tpu.py"

# Stop a TPU VM (saves cost; preserves config)
gcloud compute tpus tpu-vm stop my-tpu-vm --zone=us-central1-b

# Start a stopped TPU VM
gcloud compute tpus tpu-vm start my-tpu-vm --zone=us-central1-b

# Delete a TPU VM
gcloud compute tpus tpu-vm delete my-tpu-vm --zone=us-central1-b --quiet
```

### TPU Node API (Legacy)

```bash
# Create a legacy TPU node (not recommended for new workloads)
gcloud compute tpus create my-tpu-node \
  --zone=us-central1-b \
  --accelerator-type=v3-8 \
  --version=2.16.0 \
  --network=my-vpc \
  --range=10.240.1.0/29

# List TPU nodes
gcloud compute tpus list --zone=us-central1-b

# Delete a TPU node
gcloud compute tpus delete my-tpu-node --zone=us-central1-b --quiet
```

---

## GPU Instances

### Create GPU Instances

```bash
# Create an instance with a T4 GPU
gcloud compute instances create my-t4-instance \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --restart-on-failure \
  --metadata=install-nvidia-driver=True \
  --zone=us-central1-a

# Create an A2 instance with 2x A100 40 GB GPUs
gcloud compute instances create my-a100-instance \
  --machine-type=a2-highgpu-2g \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --zone=us-central1-a

# Create an A3 instance with 8x H100 80 GB GPUs
gcloud compute instances create my-h100-instance \
  --machine-type=a3-highgpu-8g \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=500GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --zone=us-central1-a

# Create an L4 GPU instance (inference)
gcloud compute instances create my-l4-inference \
  --machine-type=g2-standard-8 \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=100GB \
  --maintenance-policy=TERMINATE \
  --zone=us-central1-a

# Create a Spot GPU instance (for training with checkpointing)
gcloud compute instances create my-spot-gpu \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-v100,count=1 \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=200GB \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --zone=us-central1-a

# List GPU instance types available in a zone
gcloud compute accelerator-types list --filter="zone:us-central1-a"
```

### GPU Reservations

```bash
# Create a reservation for A100 GPUs
gcloud compute reservations create my-a100-reservation \
  --machine-type=a2-highgpu-2g \
  --vm-count=4 \
  --zone=us-central1-a

# Create a shared reservation (usable across a project)
gcloud compute reservations create my-shared-gpu-reservation \
  --machine-type=a2-highgpu-1g \
  --vm-count=8 \
  --zone=us-central1-a \
  --share-setting=specific-projects \
  --share-with=my-second-project

# List reservations
gcloud compute reservations list --filter="zone:us-central1-a"

# Create an instance that consumes a specific reservation
gcloud compute instances create my-reserved-gpu \
  --machine-type=a2-highgpu-2g \
  --reservation=my-a100-reservation \
  --reservation-affinity=specific \
  --zone=us-central1-a
```

---

## Sole-Tenant Nodes

```bash
# List available sole-tenant node types
gcloud compute sole-tenancy node-types list --zone=us-central1-a

# Describe a node type
gcloud compute sole-tenancy node-types describe n2-node-80-640 --zone=us-central1-a

# Create a node template
gcloud compute sole-tenancy node-templates create my-node-template \
  --node-type=n2-node-80-640 \
  --region=us-central1 \
  --node-affinity-labels=workload=production,compliance=hipaa

# Create a node template for BYOL Windows Server
gcloud compute sole-tenancy node-templates create my-windows-byol-template \
  --node-type=n2-node-80-640 \
  --region=us-central1 \
  --node-affinity-labels=os=windows,byol=true

# Create a node group from a template
gcloud compute sole-tenancy node-groups create my-node-group \
  --node-template=my-node-template \
  --target-size=2 \
  --zone=us-central1-a

# Create a node group with autoscaling
gcloud compute sole-tenancy node-groups create my-auto-node-group \
  --node-template=my-node-template \
  --target-size=1 \
  --zone=us-central1-a \
  --autoscaler-mode=ONLY_SCALE_OUT \
  --min-nodes=1 \
  --max-nodes=4

# List node groups
gcloud compute sole-tenancy node-groups list

# Describe a node group
gcloud compute sole-tenancy node-groups describe my-node-group --zone=us-central1-a

# List nodes in a group
gcloud compute sole-tenancy node-groups list-nodes my-node-group --zone=us-central1-a

# Create an instance on a sole-tenant node group
gcloud compute instances create my-sole-tenant-vm \
  --machine-type=n2-standard-8 \
  --image-family=windows-2022 \
  --image-project=windows-cloud \
  --node-group=my-node-group \
  --zone=us-central1-a \
  --maintenance-policy=MIGRATE

# Create an instance using node affinity labels
gcloud compute instances create my-byol-vm \
  --machine-type=n2-standard-16 \
  --image-family=sql-ent-2022-win-2022 \
  --image-project=windows-sql-cloud \
  --node-affinities=workload=IN:production,compliance=IN:hipaa \
  --zone=us-central1-a \
  --maintenance-policy=RESTART_NODE_ON_ANY_SERVER

# Delete a node group (all instances must be removed first)
gcloud compute sole-tenancy node-groups delete my-node-group --zone=us-central1-a --quiet
```

---

## Google Cloud VMware Engine (GCVE)

```bash
# List available GCVE locations
gcloud vmware locations list

# Create a private cloud (minimum 3 nodes; takes 2-3 hours)
gcloud vmware private-clouds create my-private-cloud \
  --location=us-central1-a \
  --cluster-id=cluster-1 \
  --node-type-id=standard-72 \
  --node-count=3 \
  --management-range=192.168.30.0/24 \
  --vmware-engine-network=my-vmware-network

# Create a VMware Engine network (connects GCVE to GCP VPC)
gcloud vmware networks create my-vmware-network \
  --location=global \
  --type=STANDARD

# List private clouds
gcloud vmware private-clouds list

# Describe a private cloud
gcloud vmware private-clouds describe my-private-cloud --location=us-central1-a

# Get vCenter credentials for a private cloud
gcloud vmware private-clouds vcenter credentials describe my-private-cloud \
  --location=us-central1-a

# Get NSX-T credentials
gcloud vmware private-clouds nsx credentials describe my-private-cloud \
  --location=us-central1-a

# List clusters in a private cloud
gcloud vmware private-clouds clusters list \
  --private-cloud=my-private-cloud \
  --location=us-central1-a

# Add a cluster (scale out GCVE)
gcloud vmware private-clouds clusters create cluster-2 \
  --private-cloud=my-private-cloud \
  --location=us-central1-a \
  --node-type-id=standard-72 \
  --node-count=3

# Create a network policy (for external IP access from GCVE VMs)
gcloud vmware network-policies create my-network-policy \
  --location=us-central1 \
  --vmware-engine-network=my-vmware-network \
  --edge-services-cidr=192.168.254.0/24 \
  --internet-access \
  --external-ip

# List network policies
gcloud vmware network-policies list --location=us-central1

# Delete a private cloud (destructive; frees all resources)
gcloud vmware private-clouds delete my-private-cloud \
  --location=us-central1-a \
  --quiet
```

---

## HPC — Compact Placement Policy

```bash
# Create a compact placement policy for HPC cluster
gcloud compute resource-policies create group-placement my-hpc-placement \
  --region=us-central1 \
  --collocation=COLLOCATED \
  --vm-count=32

# Create HPC instances using the placement policy
gcloud compute instances create my-hpc-node-{0..31} \
  --machine-type=c3-standard-176 \
  --image-family=hpc-rocky-linux-8 \
  --image-project=cloud-hpc-image-public \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --network-interface=nic-type=GVNIC \
  --resource-policies=my-hpc-placement \
  --zone=us-central1-a

# Create a MIG for HPC with compact placement
gcloud compute instance-templates create my-hpc-template \
  --machine-type=c3-standard-176 \
  --image-family=hpc-rocky-linux-8 \
  --image-project=cloud-hpc-image-public \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --network-interface=nic-type=GVNIC

gcloud compute instance-groups managed create my-hpc-mig \
  --template=my-hpc-template \
  --size=8 \
  --zone=us-central1-a

# List resource policies (including placement policies)
gcloud compute resource-policies list --filter="region:us-central1"

# Describe a placement policy
gcloud compute resource-policies describe my-hpc-placement --region=us-central1

# Delete a placement policy
gcloud compute resource-policies delete my-hpc-placement --region=us-central1 --quiet
```

---

## HPC Toolkit Reference

The Google Cloud HPC Toolkit is a Terraform-based tool for deploying HPC environments. Install and use:

```bash
# Clone the HPC Toolkit
git clone https://github.com/GoogleCloudPlatform/hpc-toolkit.git
cd hpc-toolkit

# Build the ghpc binary
make

# Deploy a Slurm cluster using a blueprint
./ghpc create blueprints/slurm-gcp-v6-startstop.yaml \
  -v project_id=my-project \
  -v region=us-central1 \
  -v zone=us-central1-a

# Deploy Terraform modules generated by ghpc
cd my-hpc-deployment/primary
terraform init
terraform apply

# List available blueprint examples
ls blueprints/
```

The HPC Toolkit generates Terraform configurations that provision:
- Slurm controller VM
- Slurm login VM
- Auto-scaling compute partitions (MIGs)
- Shared filesystem (NFS or Filestore)
- VPC and firewall rules
- IAP tunnel access
