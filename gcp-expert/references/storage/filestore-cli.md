# Filestore — CLI Reference

Capabilities reference: [filestore-capabilities.md](filestore-capabilities.md)

All commands use `gcloud filestore`.

```bash
gcloud config set project my-project-id
```

---

## Instances

### Create Instances

```bash
# Create a Basic HDD instance (development/low-cost)
gcloud filestore instances create my-basic-hdd \
  --zone=us-central1-a \
  --tier=BASIC_HDD \
  --file-share=name=vol1,capacity=1TB \
  --network=name=my-vpc,reserved-ip-range=10.0.100.0/29

# Create a Basic SSD instance
gcloud filestore instances create my-basic-ssd \
  --zone=us-central1-a \
  --tier=BASIC_SSD \
  --file-share=name=data,capacity=2.5TB \
  --network=name=my-vpc,reserved-ip-range=10.0.101.0/29 \
  --description="Shared app data NFS"

# Create a Zonal (High Scale) instance for HPC/genomics
gcloud filestore instances create my-hpc-scratch \
  --zone=us-central1-a \
  --tier=ZONAL \
  --file-share=name=scratch,capacity=10TB \
  --network=name=my-vpc,reserved-ip-range=10.0.102.0/29 \
  --performance-mode=HIGH_SCALE_SSD

# Create an Enterprise instance (HA, multi-zone)
gcloud filestore instances create my-enterprise-nfs \
  --location=us-central1 \
  --tier=ENTERPRISE \
  --file-share=name=home,capacity=1TB \
  --network=name=my-vpc,reserved-ip-range=10.0.103.0/29 \
  --description="Enterprise HA file share for home directories"

# Create an Enterprise instance with NFS v4.1
gcloud filestore instances create my-nfsv4-instance \
  --location=us-central1 \
  --tier=ENTERPRISE \
  --file-share=name=shares,capacity=2TB,nfs-export-options="ip-ranges=10.0.0.0/8:access-mode=READ_WRITE:squash-mode=NO_ROOT_SQUASH" \
  --network=name=my-vpc,reserved-ip-range=10.0.104.0/29
```

### Describe and List Instances

```bash
# List all Filestore instances in a region
gcloud filestore instances list --location=us-central1

# List instances in a specific zone
gcloud filestore instances list --zone=us-central1-a

# List all instances across all locations
gcloud filestore instances list

# Describe a specific instance (shows IP, share name, capacity, etc.)
gcloud filestore instances describe my-basic-ssd --zone=us-central1-a

# Get the NFS IP address for mounting
gcloud filestore instances describe my-basic-ssd \
  --zone=us-central1-a \
  --format="get(networks[0].ipAddresses[0])"

# Get the file share name
gcloud filestore instances describe my-basic-ssd \
  --zone=us-central1-a \
  --format="get(fileShares[0].name)"

# List instances with format showing IP and share
gcloud filestore instances list \
  --location=us-central1 \
  --format="table(name,tier,fileShares[0].name,networks[0].ipAddresses[0],state)"
```

### Update Instances

```bash
# Resize a file share (increase capacity)
gcloud filestore instances update my-basic-ssd \
  --zone=us-central1-a \
  --file-share=name=data,capacity=5TB

# Update description
gcloud filestore instances update my-basic-ssd \
  --zone=us-central1-a \
  --description="Updated shared app data NFS"

# Update labels
gcloud filestore instances update my-basic-ssd \
  --zone=us-central1-a \
  --update-labels=env=production,team=backend

# Update NFS export options (access controls)
gcloud filestore instances update my-basic-ssd \
  --zone=us-central1-a \
  --file-share=name=data,capacity=5TB,nfs-export-options="ip-ranges=10.0.0.0/8:access-mode=READ_WRITE:squash-mode=ROOT_SQUASH"
```

### Delete Instances

```bash
# Delete an instance (ALL data and in-instance snapshots are permanently deleted)
gcloud filestore instances delete my-basic-hdd --zone=us-central1-a --quiet

# Force delete (skips confirmation)
gcloud filestore instances delete my-basic-hdd \
  --zone=us-central1-a \
  --force \
  --quiet
```

---

## Snapshots

```bash
# Create a snapshot of an instance's file share
gcloud filestore snapshots create my-snapshot-20240115 \
  --instance=my-basic-ssd \
  --instance-zone=us-central1-a \
  --description="Pre-maintenance snapshot"

# List snapshots for an instance
gcloud filestore snapshots list \
  --instance=my-basic-ssd \
  --instance-zone=us-central1-a

# Describe a snapshot
gcloud filestore snapshots describe my-snapshot-20240115 \
  --instance=my-basic-ssd \
  --instance-zone=us-central1-a

# Restore a file share from a snapshot (overwrites current data)
gcloud filestore instances restore my-basic-ssd \
  --zone=us-central1-a \
  --source-snapshot=my-snapshot-20240115 \
  --source-snapshot-instance=my-basic-ssd \
  --source-snapshot-instance-zone=us-central1-a \
  --file-share=data

# Delete a snapshot
gcloud filestore snapshots delete my-snapshot-20240115 \
  --instance=my-basic-ssd \
  --instance-zone=us-central1-a \
  --quiet
```

---

## Backups

```bash
# Create a backup of an instance (stored independently in Cloud Storage)
gcloud filestore backups create my-backup-20240115 \
  --instance=my-basic-ssd \
  --instance-zone=us-central1-a \
  --region=us-central1 \
  --description="Full backup before major upgrade"

# List all backups in a region
gcloud filestore backups list --region=us-central1

# List backups for a specific instance
gcloud filestore backups list \
  --region=us-central1 \
  --filter="sourceInstance:my-basic-ssd"

# Describe a backup
gcloud filestore backups describe my-backup-20240115 --region=us-central1

# Restore a backup to a new instance
gcloud filestore instances create my-restored-instance \
  --zone=us-central1-a \
  --tier=BASIC_SSD \
  --file-share=name=data,capacity=5TB \
  --network=name=my-vpc,reserved-ip-range=10.0.200.0/29 \
  --source-backup=projects/my-project/locations/us-central1/backups/my-backup-20240115

# Restore a backup to an existing instance (replaces all data in the file share)
gcloud filestore instances restore my-basic-ssd \
  --zone=us-central1-a \
  --source-backup=projects/my-project/locations/us-central1/backups/my-backup-20240115 \
  --file-share=data

# Delete a backup
gcloud filestore backups delete my-backup-20240115 \
  --region=us-central1 \
  --quiet
```

---

## Mounting a Filestore Share (Linux)

```bash
# Install NFS client utilities
sudo apt-get install -y nfs-common   # Debian/Ubuntu
sudo yum install -y nfs-utils        # RHEL/CentOS/Rocky

# Get the Filestore IP and share name
FILESTORE_IP=$(gcloud filestore instances describe my-basic-ssd \
  --zone=us-central1-a \
  --format="get(networks[0].ipAddresses[0])")
SHARE_NAME=$(gcloud filestore instances describe my-basic-ssd \
  --zone=us-central1-a \
  --format="get(fileShares[0].name)")

# Create mount point and mount
sudo mkdir -p /mnt/filestore
sudo mount -t nfs \
  -o rw,hard,intr,timeo=600,retrans=3 \
  ${FILESTORE_IP}:/${SHARE_NAME} \
  /mnt/filestore

# Verify the mount
df -h /mnt/filestore
ls /mnt/filestore

# Make mount persistent across reboots (add to /etc/fstab)
echo "${FILESTORE_IP}:/${SHARE_NAME}  /mnt/filestore  nfs  defaults,hard  0  0" | \
  sudo tee -a /etc/fstab

# Unmount
sudo umount /mnt/filestore
```

---

## Firewall Rule for NFS Access

```bash
# Create a firewall rule to allow NFS from GCE instances to Filestore
gcloud compute firewall-rules create allow-nfs-filestore \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:2049,udp:2049 \
  --source-ranges=10.0.0.0/8 \
  --target-service-accounts=my-app-sa@my-project.iam.gserviceaccount.com \
  --description="Allow NFS traffic to Filestore from app VMs"
```

---

## GKE — Filestore CSI Driver

```bash
# Enable the Filestore CSI addon on a GKE cluster
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --update-addons=GcpFilestoreCsiDriver=ENABLED

# Or create a cluster with Filestore CSI driver enabled
gcloud container clusters create my-cluster \
  --region=us-central1 \
  --num-nodes=2 \
  --addons=GcpFilestoreCsiDriver

# After enabling CSI driver, create a StorageClass and PVC in Kubernetes:
# kubectl apply -f - <<EOF
# apiVersion: storage.k8s.io/v1
# kind: StorageClass
# metadata:
#   name: filestore-sc
# provisioner: filestore.csi.storage.gke.io
# parameters:
#   tier: standard
#   network: my-vpc
# volumeBindingMode: WaitForFirstConsumer
# allowVolumeExpansion: true
# ---
# apiVersion: v1
# kind: PersistentVolumeClaim
# metadata:
#   name: my-filestore-pvc
# spec:
#   accessModes:
#   - ReadWriteMany
#   storageClassName: filestore-sc
#   resources:
#     requests:
#       storage: 1Ti
# EOF
```
