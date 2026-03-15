# NetApp Cloud Volumes — CLI Reference

See also: [netapp-volumes-capabilities.md](netapp-volumes-capabilities.md)

---

## NetApp Volumes — Setup and Storage Pools

```bash
# Enable NetApp Cloud Volumes API
gcloud services enable netapp.googleapis.com --project=PROJECT_ID

# List available NetApp locations (regions)
gcloud netapp locations list --project=PROJECT_ID

# Create a storage pool (capacity pool — required before creating volumes)
gcloud netapp storage-pools create my-pool \
  --location=us-central1 \
  --service-level=PREMIUM \
  --capacity=4096 \
  --network=projects/PROJECT_ID/global/networks/default \
  --project=PROJECT_ID

# List storage pools
gcloud netapp storage-pools list \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe a storage pool
gcloud netapp storage-pools describe my-pool \
  --location=us-central1 \
  --project=PROJECT_ID

# Delete a storage pool (must be empty)
gcloud netapp storage-pools delete my-pool \
  --location=us-central1 \
  --project=PROJECT_ID
```

---

## NetApp Volumes — Volume Management

```bash
# Create an NFS volume
gcloud netapp volumes create my-nfs-volume \
  --location=us-central1 \
  --capacity-gib=1024 \
  --storage-pool=my-pool \
  --protocols=NFSV3 \
  --share-name=my-nfs-share \
  --unix-permissions=0755 \
  --export-policy-rules='accessType=READ_WRITE,allowedClients=10.0.0.0/8,nfsv3=true' \
  --project=PROJECT_ID

# Create an NFS v4.1 volume with Kerberos
gcloud netapp volumes create my-nfs4-volume \
  --location=us-central1 \
  --capacity-gib=2048 \
  --storage-pool=my-pool \
  --protocols=NFSV4 \
  --share-name=my-nfs4-share \
  --export-policy-rules='accessType=READ_WRITE,allowedClients=10.128.0.0/14,nfsv4=true,kerberos5ReadWrite=true' \
  --project=PROJECT_ID

# Create an SMB volume (requires Active Directory config)
gcloud netapp volumes create my-smb-volume \
  --location=us-central1 \
  --capacity-gib=1024 \
  --storage-pool=my-pool \
  --protocols=SMB \
  --share-name=my-smb-share \
  --project=PROJECT_ID

# Create a dual-protocol volume (NFS + SMB)
gcloud netapp volumes create my-dual-volume \
  --location=us-central1 \
  --capacity-gib=2048 \
  --storage-pool=my-pool \
  --protocols=NFSV3,SMB \
  --share-name=my-dual-share \
  --security-style=NTFS \
  --project=PROJECT_ID

# List volumes
gcloud netapp volumes list \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe a volume (get mount path)
gcloud netapp volumes describe my-nfs-volume \
  --location=us-central1 \
  --project=PROJECT_ID

# Resize a volume
gcloud netapp volumes update my-nfs-volume \
  --location=us-central1 \
  --capacity-gib=2048 \
  --project=PROJECT_ID

# Delete a volume
gcloud netapp volumes delete my-nfs-volume \
  --location=us-central1 \
  --project=PROJECT_ID
```

---

## NetApp Volumes — Snapshots

```bash
# Create a manual snapshot
gcloud netapp volumes snapshots create my-snapshot \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# List snapshots for a volume
gcloud netapp volumes snapshots list \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Describe a snapshot
gcloud netapp volumes snapshots describe my-snapshot \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Restore volume from snapshot
gcloud netapp volumes revert my-nfs-volume \
  --location=us-central1 \
  --snapshot-id=SNAPSHOT_ID \
  --project=PROJECT_ID

# Delete a snapshot
gcloud netapp volumes snapshots delete my-snapshot \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Create a snapshot schedule (snapshot policy)
gcloud netapp volumes snapshot-policies create hourly-policy \
  --location=us-central1 \
  --enabled=true \
  --hourly-schedule-snapshots-to-keep=6 \
  --hourly-schedule-minute=0 \
  --daily-schedule-snapshots-to-keep=7 \
  --daily-schedule-hour=0 \
  --daily-schedule-minute=0 \
  --project=PROJECT_ID
```

---

## NetApp Volumes — Replication

```bash
# Create a replication (source volume in us-central1 → destination in us-east1)
gcloud netapp volumes replications create my-replication \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --destination-volume-parameters-storage-pool=projects/PROJECT_ID/locations/us-east1/storagePools/dr-pool \
  --destination-volume-parameters-share-name=my-nfs-share-dr \
  --destination-volume-parameters-capacity-gib=1024 \
  --replication-schedule=EVERY_10_MINUTES \
  --project=PROJECT_ID

# List replications
gcloud netapp volumes replications list \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Describe replication (check lag time, state)
gcloud netapp volumes replications describe my-replication \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Pause replication
gcloud netapp volumes replications stop my-replication \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Resume replication
gcloud netapp volumes replications resume my-replication \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID

# Reverse replication (DR failover — promote destination to source)
gcloud netapp volumes replications reverse my-replication \
  --location=us-central1 \
  --volume=my-nfs-volume \
  --project=PROJECT_ID
```

---

## NetApp Volumes — Active Directory (for SMB)

```bash
# Create Active Directory configuration for SMB volumes
gcloud netapp active-directories create my-ad \
  --location=us-central1 \
  --dns=10.0.0.2,10.0.0.3 \
  --domain=corp.example.com \
  --net-bios-prefix=GCP \
  --username=svc-netapp \
  --password=PASSWORD \
  --project=PROJECT_ID

# List Active Directory configurations
gcloud netapp active-directories list \
  --location=us-central1 \
  --project=PROJECT_ID

# Update Active Directory configuration
gcloud netapp active-directories update my-ad \
  --location=us-central1 \
  --dns=10.0.0.2,10.0.0.4 \
  --project=PROJECT_ID

# Delete Active Directory configuration
gcloud netapp active-directories delete my-ad \
  --location=us-central1 \
  --project=PROJECT_ID
```

---

## NetApp Volumes — Mounting

```bash
# Mount NFS volume on Linux (get mount path from describe command)
# Mount path format: VOLUME_IP:/SHARE_NAME
sudo mkdir -p /mnt/netapp-volume
sudo mount -t nfs -o rw,hard,intr,rsize=65536,wsize=65536,vers=3 \
  10.x.x.x:/my-nfs-share /mnt/netapp-volume

# Add to /etc/fstab for persistent mount
echo "10.x.x.x:/my-nfs-share /mnt/netapp-volume nfs rw,hard,intr,rsize=65536,wsize=65536,vers=3 0 0" \
  | sudo tee -a /etc/fstab

# NFS v4.1 mount
sudo mount -t nfs4 -o rw,hard,intr,rsize=65536,wsize=65536 \
  10.x.x.x:/my-nfs4-share /mnt/netapp-nfs4

# SMB mount on Linux
sudo mkdir -p /mnt/netapp-smb
sudo mount -t cifs -o username=USER,password=PASS,domain=DOMAIN \
  //10.x.x.x/my-smb-share /mnt/netapp-smb
```
