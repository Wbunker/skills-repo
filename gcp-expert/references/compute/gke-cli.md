# Google Kubernetes Engine — CLI Reference

Capabilities reference: [gke-capabilities.md](gke-capabilities.md)

All GKE management commands use `gcloud container`. After authenticating to a cluster with `get-credentials`, use standard `kubectl` commands.

```bash
gcloud config set project my-project-id
```

---

## Clusters

### Create a Standard Cluster

```bash
# Regional private cluster (recommended for production)
gcloud container clusters create my-prod-cluster \
  --region=us-central1 \
  --num-nodes=2 \
  --machine-type=n2-standard-4 \
  --disk-type=pd-ssd \
  --disk-size=100GB \
  --image-type=COS_CONTAINERD \
  --enable-private-nodes \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-ip-alias \
  --network=my-vpc \
  --subnetwork=my-gke-subnet \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-master-authorized-networks \
  --master-authorized-networks=10.0.0.0/8,203.0.113.0/24 \
  --workload-pool=my-project.svc.id.goog \
  --enable-dataplane-v2 \
  --release-channel=regular \
  --enable-autoupgrade \
  --enable-autorepair \
  --enable-shielded-nodes \
  --shielded-secure-boot \
  --shielded-integrity-monitoring \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

# Zonal cluster for development (simpler, cheaper)
gcloud container clusters create my-dev-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --release-channel=rapid \
  --enable-autoupgrade \
  --enable-autorepair \
  --workload-pool=my-project.svc.id.goog

# Cluster with application-layer secret encryption
gcloud container clusters create my-secure-cluster \
  --region=us-central1 \
  --num-nodes=2 \
  --machine-type=n2-standard-4 \
  --database-encryption-key=projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-cluster-key \
  --workload-pool=my-project.svc.id.goog \
  --release-channel=regular \
  --enable-private-nodes \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-ip-alias
```

### Create an Autopilot Cluster

```bash
# Basic Autopilot cluster (recommended for most new workloads)
gcloud container clusters create-auto my-autopilot-cluster \
  --region=us-central1

# Autopilot with private nodes
gcloud container clusters create-auto my-private-autopilot \
  --region=us-central1 \
  --enable-private-nodes \
  --master-ipv4-cidr=172.16.0.0/28 \
  --network=my-vpc \
  --subnetwork=my-gke-subnet

# Autopilot with Workload Identity (enabled by default, but explicit)
gcloud container clusters create-auto my-autopilot-cluster \
  --region=us-central1 \
  --workload-pool=my-project.svc.id.goog \
  --release-channel=regular
```

### Manage Clusters

```bash
# List clusters
gcloud container clusters list
gcloud container clusters list --format="table(name,location,status,currentMasterVersion,currentNodeVersion)"

# Describe a cluster
gcloud container clusters describe my-cluster --region=us-central1

# Get credentials (configure kubectl to connect to the cluster)
gcloud container clusters get-credentials my-cluster --region=us-central1

# Get credentials for a zonal cluster
gcloud container clusters get-credentials my-dev-cluster --zone=us-central1-a

# Upgrade a cluster's control plane
gcloud container clusters upgrade my-cluster \
  --region=us-central1 \
  --master \
  --cluster-version=1.29.4-gke.1000001

# Upgrade a node pool
gcloud container clusters upgrade my-cluster \
  --region=us-central1 \
  --node-pool=default-pool

# Resize the default node pool
gcloud container clusters resize my-cluster \
  --region=us-central1 \
  --node-pool=default-pool \
  --num-nodes=5

# Update authorized networks
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --update-master-authorized-networks \
  --master-authorized-networks=10.0.0.0/8,203.0.113.10/32

# Enable Workload Identity on existing cluster
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --workload-pool=my-project.svc.id.goog

# Delete a cluster
gcloud container clusters delete my-cluster --region=us-central1 --quiet
```

---

## Node Pools

```bash
# Create a standard node pool
gcloud container node-pools create my-app-pool \
  --cluster=my-cluster \
  --region=us-central1 \
  --machine-type=n2-standard-8 \
  --num-nodes=2 \
  --disk-type=pd-ssd \
  --disk-size=100GB \
  --image-type=COS_CONTAINERD \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=20 \
  --enable-autoupgrade \
  --enable-autorepair \
  --node-labels=role=application,team=backend \
  --node-taints=dedicated=backend:NoSchedule

# Create a Spot node pool (for fault-tolerant workloads)
gcloud container node-pools create spot-pool \
  --cluster=my-cluster \
  --region=us-central1 \
  --machine-type=n2-standard-4 \
  --spot \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=50 \
  --enable-autoupgrade \
  --enable-autorepair

# Create a GPU node pool
gcloud container node-pools create gpu-pool \
  --cluster=my-cluster \
  --zone=us-central1-a \
  --machine-type=a2-highgpu-1g \
  --accelerator=type=nvidia-tesla-a100,count=1,gpu-driver-version=latest \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=4 \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --enable-autoupgrade \
  --enable-autorepair

# List node pools in a cluster
gcloud container node-pools list --cluster=my-cluster --region=us-central1

# Describe a node pool
gcloud container node-pools describe my-app-pool \
  --cluster=my-cluster \
  --region=us-central1

# Update autoscaling for a node pool
gcloud container node-pools update my-app-pool \
  --cluster=my-cluster \
  --region=us-central1 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=30

# Add taints to a node pool
gcloud container node-pools update my-app-pool \
  --cluster=my-cluster \
  --region=us-central1 \
  --node-taints=environment=production:NoSchedule

# Delete a node pool (pods are evicted and rescheduled)
gcloud container node-pools delete old-pool \
  --cluster=my-cluster \
  --region=us-central1 \
  --quiet
```

---

## Workload Identity Setup

```bash
# Step 1: Verify Workload Identity is enabled on the cluster
gcloud container clusters describe my-cluster \
  --region=us-central1 \
  --format="get(workloadIdentityConfig.workloadPool)"

# Step 2: Create a Kubernetes service account (or use existing)
kubectl create serviceaccount my-app-ksa --namespace=my-namespace

# Step 3: Create a GCP service account
gcloud iam service-accounts create my-app-gsa \
  --display-name="My App GCP Service Account"

# Step 4: Grant the GCP SA the roles it needs (example: Cloud Storage reader)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-app-gsa@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Step 5: Bind the Kubernetes SA to the GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  my-app-gsa@my-project.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:my-project.svc.id.goog[my-namespace/my-app-ksa]"

# Step 6: Annotate the Kubernetes SA
kubectl annotate serviceaccount my-app-ksa \
  --namespace=my-namespace \
  iam.gke.io/gcp-service-account=my-app-gsa@my-project.iam.gserviceaccount.com

# Verify Workload Identity is working (from a pod using the KSA)
# kubectl exec -it my-pod -n my-namespace -- curl -H "Metadata-Flavor: Google" \
#   http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email
```

---

## kubectl After get-credentials

Once credentials are configured, use standard kubectl:

```bash
# View current context
kubectl config current-context

# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context gke_my-project_us-central1_my-cluster

# View cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes -o wide

# Apply a manifest
kubectl apply -f deployment.yaml

# Get all resources in a namespace
kubectl get all -n my-namespace

# Check pod resource usage (requires metrics-server, included in GKE)
kubectl top pods -n my-namespace
kubectl top nodes

# View pod logs
kubectl logs my-pod -n my-namespace --tail=100 -f

# Execute into a pod
kubectl exec -it my-pod -n my-namespace -- /bin/bash

# Drain a node (for manual maintenance)
kubectl drain my-node --ignore-daemonsets --delete-emptydir-data

# Cordon a node (prevent new pod scheduling)
kubectl cordon my-node

# Uncordon a node
kubectl uncordon my-node
```

---

## Private Cluster Creation with Authorized Networks

```bash
# Full private cluster setup with authorized networks for corporate access
gcloud container clusters create my-private-cluster \
  --region=us-central1 \
  --num-nodes=2 \
  --machine-type=n2-standard-4 \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-ip-alias \
  --network=my-vpc \
  --subnetwork=my-gke-subnet \
  --cluster-secondary-range-name=pods-range \
  --services-secondary-range-name=services-range \
  --no-enable-master-authorized-networks \
  --workload-pool=my-project.svc.id.goog \
  --release-channel=regular

# Update master authorized networks after creation
gcloud container clusters update my-private-cluster \
  --region=us-central1 \
  --enable-master-authorized-networks \
  --master-authorized-networks=10.0.0.0/8

# Connect to private cluster endpoint via Cloud Shell or bastion host
# Ensure the bastion/Cloud Shell has access to the master_ipv4_cidr network
gcloud container clusters get-credentials my-private-cluster \
  --region=us-central1 \
  --internal-ip
```

---

## Cluster Operations

```bash
# Enable Binary Authorization on cluster
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE

# Enable network policy enforcement
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --update-addons=NetworkPolicy=ENABLED

# Enable GKE Backup
gcloud beta container clusters update my-cluster \
  --region=us-central1 \
  --update-addons=BackupRestore=ENABLED

# View available Kubernetes versions in a release channel
gcloud container get-server-config --region=us-central1 \
  --format="yaml(channels)"

# Check cluster operations (upgrades in progress, etc.)
gcloud container operations list --filter="target:my-cluster"

# Describe a specific operation
gcloud container operations describe OPERATION_ID --region=us-central1
```
