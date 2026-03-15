# AWS FSx — CLI Reference
For service concepts, see [fsx-capabilities.md](fsx-capabilities.md).

The `aws fsx` namespace covers all FSx variants (Lustre, NetApp ONTAP, OpenZFS, Windows File Server).

```bash
# --- Create File Systems ---

# FSx for Lustre (Scratch 2)
aws fsx create-file-system \
  --file-system-type LUSTRE \
  --storage-capacity 1200 \
  --subnet-ids subnet-0123456789abcdef0 \
  --lustre-configuration \
  'DeploymentType=SCRATCH_2,PerUnitStorageThroughput=200'

# FSx for Lustre (Persistent 2 with S3 data repository)
aws fsx create-file-system \
  --file-system-type LUSTRE \
  --storage-capacity 2400 \
  --subnet-ids subnet-0123456789abcdef0 \
  --lustre-configuration \
  'DeploymentType=PERSISTENT_2,PerUnitStorageThroughput=250'

# FSx for NetApp ONTAP (Multi-AZ)
aws fsx create-file-system \
  --file-system-type ONTAP \
  --storage-capacity 1024 \
  --subnet-ids subnet-az1 subnet-az2 \
  --ontap-configuration \
  'DeploymentType=MULTI_AZ_1,ThroughputCapacity=512,PreferredSubnetId=subnet-az1,RouteTableIds=[rtb-xxx]'

# FSx for OpenZFS (Single-AZ)
aws fsx create-file-system \
  --file-system-type OPENZFS \
  --storage-capacity 64 \
  --subnet-ids subnet-0123456789abcdef0 \
  --open-zfs-configuration \
  'DeploymentType=SINGLE_AZ_1,ThroughputCapacity=64'

# FSx for Windows File Server (Multi-AZ)
aws fsx create-file-system \
  --file-system-type WINDOWS \
  --storage-capacity 300 \
  --subnet-ids subnet-az1 subnet-az2 \
  --windows-configuration \
  'ActiveDirectoryId=d-xxxxxxxxxxxx,ThroughputCapacity=32,DeploymentType=MULTI_AZ_1,PreferredSubnetId=subnet-az1'

# --- Describe / List ---
aws fsx describe-file-systems
aws fsx describe-file-systems --file-system-ids fs-0123456789abcdef0

# --- Update / Delete ---
aws fsx update-file-system \
  --file-system-id fs-0123456789abcdef0 \
  --windows-configuration 'ThroughputCapacity=64'

aws fsx delete-file-system --file-system-id fs-0123456789abcdef0

# --- FSx Volumes (ONTAP / OpenZFS) ---
# Create ONTAP volume
aws fsx create-volume \
  --volume-type ONTAP \
  --name my-vol \
  --ontap-configuration \
  'JunctionPath=/data,SizeInMegabytes=10240,StorageEfficiencyEnabled=true,StorageVirtualMachineId=svm-xxx'

# Create OpenZFS volume
aws fsx create-volume \
  --volume-type OPENZFS \
  --name my-zfs-vol \
  --open-zfs-configuration \
  'ParentVolumeId=fsvol-root,StorageCapacityReservationGiB=10,StorageCapacityQuotaGiB=100,DataCompressionType=LZ4'

aws fsx describe-volumes
aws fsx describe-volumes --volume-ids fsvol-0123456789abcdef0
aws fsx update-volume --volume-id fsvol-0123456789abcdef0 \
  --open-zfs-configuration 'StorageCapacityQuotaGiB=200'
aws fsx delete-volume --volume-id fsvol-0123456789abcdef0

# --- SVMs (ONTAP only) ---
aws fsx create-storage-virtual-machine \
  --file-system-id fs-0123456789abcdef0 \
  --name my-svm \
  --root-volume-security-style UNIX

aws fsx describe-storage-virtual-machines
aws fsx delete-storage-virtual-machine --storage-virtual-machine-id svm-0123456789abcdef0

# --- Data Repository Associations (Lustre only) ---
aws fsx create-data-repository-association \
  --file-system-id fs-0123456789abcdef0 \
  --file-system-path /ns1 \
  --data-repository-path s3://my-bucket/prefix \
  --s3 'AutoImportPolicy={Events=[NEW,CHANGED,DELETED]},AutoExportPolicy={Events=[NEW,CHANGED,DELETED]}'

aws fsx describe-data-repository-associations
aws fsx delete-data-repository-association \
  --association-id dra-0123456789abcdef0

# Create data repository task (export changes to S3)
aws fsx create-data-repository-task \
  --type EXPORT_TO_REPOSITORY \
  --file-system-id fs-0123456789abcdef0 \
  --paths /ns1/results/ \
  --report 'Enabled=true,Scope=FAILED_FILES_ONLY,Format=REPORT_CSV_20191124,Path=s3://my-bucket/fsx-task-reports/'

# --- Backups ---
aws fsx create-backup --file-system-id fs-0123456789abcdef0 \
  --tags Key=Name,Value=manual-backup
aws fsx describe-backups
aws fsx describe-backups --backup-ids backup-0123456789abcdef0
aws fsx copy-backup \
  --source-backup-id backup-0123456789abcdef0 \
  --source-region us-east-1 \
  --region us-west-2
aws fsx delete-backup --backup-id backup-0123456789abcdef0

# Restore file system from backup
aws fsx create-file-system-from-backup \
  --backup-id backup-0123456789abcdef0 \
  --subnet-ids subnet-0123456789abcdef0
```

---

## File Cache

The `aws fsx` commands also manage Amazon File Cache resources. Cache type is always `LUSTRE`, deployment type is always `CACHE_1`, and throughput is always 1,000 MB/s per TiB.

```bash
# --- Create File Cache linked to an S3 bucket ---
aws fsx create-file-cache \
  --file-cache-type LUSTRE \
  --file-cache-type-version 2.12 \
  --storage-capacity 1200 \
  --subnet-ids subnet-0123456789abcdef0 \
  --security-group-ids sg-0123456789abcdef0 \
  --lustre-configuration \
  'DeploymentType=CACHE_1,PerUnitStorageThroughput=1000,MetadataConfiguration={StorageCapacity=2400}' \
  --data-repository-associations '[{
    "FileCachePath": "/ns1",
    "DataRepositoryPath": "s3://my-bucket/datasets/"
  }]'

# --- Create File Cache linked to an on-premises NFS server ---
aws fsx create-file-cache \
  --file-cache-type LUSTRE \
  --file-cache-type-version 2.12 \
  --storage-capacity 2400 \
  --subnet-ids subnet-0123456789abcdef0 \
  --security-group-ids sg-0123456789abcdef0 \
  --lustre-configuration \
  'DeploymentType=CACHE_1,PerUnitStorageThroughput=1000,MetadataConfiguration={StorageCapacity=2400}' \
  --data-repository-associations '[{
    "FileCachePath": "/nfs-data",
    "DataRepositoryPath": "nfs://nfs.mycompany.com/exports/hpc",
    "DataRepositorySubdirectories": ["/datasets", "/results"],
    "NFS": {"Version": "NFS3", "DnsIps": ["10.0.1.10"]}
  }]'

# --- Describe / List ---
aws fsx describe-file-caches
aws fsx describe-file-caches --file-cache-ids fc-0123456789abcdef0

# --- Delete ---
aws fsx delete-file-cache --file-cache-id fc-0123456789abcdef0

# --- Data Repository Associations on a File Cache ---
# List DRAs for a cache
aws fsx describe-data-repository-associations \
  --filters 'Name=file-cache-id,Values=fc-0123456789abcdef0'

# Delete a DRA (removes the link; does not affect source data)
aws fsx delete-data-repository-association \
  --association-id dra-0123456789abcdef0

# --- Explicit data pre-load from S3 into the cache ---
aws fsx create-data-repository-task \
  --type IMPORT_METADATA_FROM_REPOSITORY \
  --file-cache-id fc-0123456789abcdef0 \
  --paths /ns1/models/ \
  --report 'Enabled=true,Scope=FAILED_FILES_ONLY,Format=REPORT_CSV_20191124,Path=s3://my-bucket/task-reports/'
```
