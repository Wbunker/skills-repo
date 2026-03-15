# Persistent Disk and Hyperdisk — CLI Reference

Capabilities reference: [persistent-disk-capabilities.md](persistent-disk-capabilities.md)

All commands use `gcloud compute disks` and `gcloud compute snapshots`.

```bash
gcloud config set project my-project-id
gcloud config set compute/zone us-central1-a
```

---

## Disks

### Create Disks

```bash
# Create a pd-balanced disk
gcloud compute disks create my-app-data \
  --size=200GB \
  --type=pd-balanced \
  --zone=us-central1-a

# Create a pd-ssd disk
gcloud compute disks create my-db-data \
  --size=500GB \
  --type=pd-ssd \
  --zone=us-central1-a \
  --labels=env=production,team=db

# Create a pd-extreme disk with provisioned IOPS and throughput
gcloud compute disks create my-extreme-disk \
  --size=2TB \
  --type=pd-extreme \
  --provisioned-iops=100000 \
  --zone=us-central1-a

# Create a Hyperdisk Balanced with custom IOPS and throughput
gcloud compute disks create my-hyperdisk \
  --size=1TB \
  --type=hyperdisk-balanced \
  --provisioned-iops=20000 \
  --provisioned-throughput=750 \
  --zone=us-central1-a

# Create a Hyperdisk Extreme for SAP HANA / Oracle
gcloud compute disks create my-hana-data \
  --size=4TB \
  --type=hyperdisk-extreme \
  --provisioned-iops=200000 \
  --provisioned-throughput=5000 \
  --zone=us-central1-a

# Create a Hyperdisk ML (for ML model serving — read-only, multi-attach)
gcloud compute disks create my-model-disk \
  --size=500GB \
  --type=hyperdisk-ml \
  --provisioned-iops=500000 \
  --provisioned-throughput=12000 \
  --zone=us-central1-a

# Create a Hyperdisk Throughput (streaming/analytics, HDD-equivalent)
gcloud compute disks create my-streaming-disk \
  --size=10TB \
  --type=hyperdisk-throughput \
  --provisioned-throughput=1000 \
  --zone=us-central1-a

# Create a regional persistent disk (replicated across two zones)
gcloud compute disks create my-ha-disk \
  --size=500GB \
  --type=pd-ssd \
  --region=us-central1 \
  --replica-zones=us-central1-a,us-central1-b \
  --labels=role=ha-database

# Create a disk from a snapshot
gcloud compute disks create my-restored-disk \
  --source-snapshot=my-snapshot-20240115 \
  --type=pd-ssd \
  --size=500GB \
  --zone=us-central1-a

# Create a disk from an image
gcloud compute disks create my-prepopulated-disk \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --size=50GB \
  --type=pd-balanced \
  --zone=us-central1-a

# Create a CMEK-encrypted disk
gcloud compute disks create my-encrypted-disk \
  --size=200GB \
  --type=pd-ssd \
  --kms-key=projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
  --zone=us-central1-a
```

### Describe and List Disks

```bash
# List all disks in a zone
gcloud compute disks list --zone=us-central1-a

# List all disks in a region
gcloud compute disks list --filter="zone~us-central1"

# List unattached disks (no users)
gcloud compute disks list \
  --filter="NOT users:*" \
  --format="table(name,zone.basename(),sizeGb,type.basename(),status)"

# List disks with labels
gcloud compute disks list --filter="labels.env=production"

# Describe a specific disk
gcloud compute disks describe my-app-data --zone=us-central1-a

# Get disk type and size
gcloud compute disks describe my-app-data \
  --zone=us-central1-a \
  --format="get(type.basename(),sizeGb)"
```

### Attach and Detach Disks

```bash
# Attach a disk to a running or stopped instance (read-write)
gcloud compute instances attach-disk my-vm \
  --disk=my-app-data \
  --zone=us-central1-a

# Attach as read-only (allows multiple instances to read the same disk)
gcloud compute instances attach-disk my-vm \
  --disk=my-shared-data \
  --mode=ro \
  --zone=us-central1-a

# Attach a regional disk (use --disk-scope=regional)
gcloud compute instances attach-disk my-vm \
  --disk=my-ha-disk \
  --disk-scope=regional \
  --zone=us-central1-a

# Attach Hyperdisk ML disk to multiple VMs for model serving
gcloud compute instances attach-disk inference-vm-1 \
  --disk=my-model-disk \
  --mode=ro \
  --zone=us-central1-a

gcloud compute instances attach-disk inference-vm-2 \
  --disk=my-model-disk \
  --mode=ro \
  --zone=us-central1-a

# Force-attach a regional disk to failover zone (HA failover)
gcloud compute instances attach-disk my-standby-vm \
  --disk=my-ha-disk \
  --disk-scope=regional \
  --force-attach \
  --zone=us-central1-b

# Detach a disk from an instance
gcloud compute instances detach-disk my-vm \
  --disk=my-app-data \
  --zone=us-central1-a
```

### Resize Disks

```bash
# Resize a disk (can only grow, never shrink)
gcloud compute disks resize my-app-data \
  --size=500GB \
  --zone=us-central1-a

# Resize a regional disk
gcloud compute disks resize my-ha-disk \
  --size=1TB \
  --region=us-central1

# After resizing, expand the filesystem within the VM:
# For ext4:
# sudo resize2fs /dev/sdb
# For xfs:
# sudo xfs_growfs /mnt/data
# For LVM: pvresize, lvextend, resize2fs/xfs_growfs
```

### Update Disk Properties

```bash
# Update Hyperdisk Balanced IOPS and throughput (no downtime required)
gcloud compute disks update my-hyperdisk \
  --provisioned-iops=40000 \
  --provisioned-throughput=1500 \
  --zone=us-central1-a

# Add labels to a disk
gcloud compute disks update my-app-data \
  --update-labels=backup=daily,owner=team-backend \
  --zone=us-central1-a
```

### Delete Disks

```bash
# Delete a disk (must be detached from all instances)
gcloud compute disks delete my-old-disk --zone=us-central1-a --quiet

# Delete multiple disks
gcloud compute disks delete disk1 disk2 disk3 --zone=us-central1-a --quiet
```

---

## Snapshots

### Create Snapshots

```bash
# Create a snapshot from a disk (disk can be running — crash consistent)
gcloud compute disks snapshot my-app-data \
  --snapshot-names=my-app-data-$(date +%Y%m%d-%H%M) \
  --zone=us-central1-a \
  --storage-location=us-central1

# Create a snapshot with description and labels
gcloud compute snapshots create my-pre-upgrade-snapshot \
  --source-disk=my-app-data \
  --source-disk-zone=us-central1-a \
  --description="Pre-upgrade snapshot before v2.0 deployment" \
  --labels=reason=pre-upgrade,version=v2.0 \
  --storage-location=us

# Create a snapshot stored in multi-region
gcloud compute disks snapshot my-db-data \
  --snapshot-names=my-db-backup-$(date +%Y%m%d) \
  --zone=us-central1-a \
  --storage-location=us

# Create snapshot of a regional disk
gcloud compute disks snapshot my-ha-disk \
  --snapshot-names=my-ha-backup \
  --region=us-central1 \
  --storage-location=us
```

### List and Describe Snapshots

```bash
# List all snapshots
gcloud compute snapshots list

# List snapshots from a specific source disk
gcloud compute snapshots list \
  --filter="sourceDisk~my-app-data" \
  --format="table(name,creationTimestamp.date(),diskSizeGb,storageBytes,status)"

# List with labels filter
gcloud compute snapshots list --filter="labels.reason=pre-upgrade"

# Describe a snapshot
gcloud compute snapshots describe my-app-data-20240115-1200

# Get snapshot size (storage bytes used)
gcloud compute snapshots describe my-snapshot \
  --format="get(storageBytes)"
```

### Delete Snapshots

```bash
# Delete a snapshot
gcloud compute snapshots delete my-old-snapshot --quiet

# Delete multiple snapshots
gcloud compute snapshots delete snap1 snap2 snap3 --quiet

# Delete all snapshots older than 30 days (using shell date arithmetic)
CUTOFF=$(date -d "30 days ago" --utc +%Y-%m-%dT%H:%M:%SZ)
gcloud compute snapshots list \
  --filter="creationTimestamp < ${CUTOFF}" \
  --format="get(name)" | \
xargs gcloud compute snapshots delete --quiet
```

---

## Snapshot Schedules (Resource Policies)

```bash
# Create a daily snapshot schedule with 7-day retention
gcloud compute resource-policies create snapshot-schedule daily-7d \
  --region=us-central1 \
  --max-retention-days=7 \
  --start-time=02:00 \
  --daily-schedule \
  --on-source-disk-delete=keep-auto-snapshots \
  --storage-location=us-central1

# Create an hourly snapshot schedule with 48-hour retention
gcloud compute resource-policies create snapshot-schedule hourly-48h \
  --region=us-central1 \
  --max-retention-days=2 \
  --start-time=00:00 \
  --hourly-schedule=1 \
  --storage-location=us-central1

# Create a weekly snapshot schedule (every Sunday at 03:00)
gcloud compute resource-policies create snapshot-schedule weekly-4wk \
  --region=us-central1 \
  --max-retention-days=28 \
  --start-time=03:00 \
  --weekly-schedule=sunday \
  --storage-location=us

# Attach a snapshot schedule to a disk
gcloud compute disks add-resource-policies my-app-data \
  --resource-policies=daily-7d \
  --zone=us-central1-a

# Detach a snapshot schedule from a disk
gcloud compute disks remove-resource-policies my-app-data \
  --resource-policies=daily-7d \
  --zone=us-central1-a

# List snapshot schedule policies
gcloud compute resource-policies list \
  --filter="snapshotSchedulePolicy:*" \
  --region=us-central1

# Describe a snapshot schedule
gcloud compute resource-policies describe daily-7d --region=us-central1

# Delete a snapshot schedule
gcloud compute resource-policies delete daily-7d --region=us-central1 --quiet
```

---

## Disk Encryption with CMEK

```bash
# Create a KMS key ring and key for disk encryption
gcloud kms keyrings create my-disk-keyring \
  --location=us-central1

gcloud kms keys create my-disk-key \
  --keyring=my-disk-keyring \
  --location=us-central1 \
  --purpose=encryption

# Grant the Compute Engine SA permission to use the key
PROJECT_NUMBER=$(gcloud projects describe my-project --format="get(projectNumber)")
gcloud kms keys add-iam-policy-binding my-disk-key \
  --keyring=my-disk-keyring \
  --location=us-central1 \
  --member=serviceAccount:service-${PROJECT_NUMBER}@compute-system.iam.gserviceaccount.com \
  --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Create a disk with CMEK
gcloud compute disks create my-cmek-disk \
  --size=200GB \
  --type=pd-ssd \
  --kms-key=projects/my-project/locations/us-central1/keyRings/my-disk-keyring/cryptoKeys/my-disk-key \
  --zone=us-central1-a

# Verify encryption key on a disk
gcloud compute disks describe my-cmek-disk \
  --zone=us-central1-a \
  --format="get(diskEncryptionKey)"
```

---

## Monitoring Disk Performance

```bash
# View disk operations metrics using Cloud Monitoring (gcloud monitoring is limited; use Console or API)
# Or use this filter in Cloud Monitoring query:
# metric.type="compute.googleapis.com/instance/disk/read_ops_count"
# resource.labels.device_name="my-disk-name"

# Check disk IOPS limits for a given VM
gcloud compute instances describe my-vm \
  --zone=us-central1-a \
  --format="get(machineType)"

# Verify disk is attached and in use
gcloud compute instances describe my-vm \
  --zone=us-central1-a \
  --format="get(disks)"
```
