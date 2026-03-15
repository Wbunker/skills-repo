# Cloud Storage — CLI Reference

Capabilities reference: [cloud-storage-capabilities.md](cloud-storage-capabilities.md)

Cloud Storage can be managed with `gcloud storage` (recommended, newer) or `gsutil` (legacy, still fully supported). Both are shown below.

```bash
gcloud config set project my-project-id
```

---

## Buckets

### Create Buckets

```bash
# Create a regional bucket (preferred for compute-adjacent storage)
gcloud storage buckets create gs://my-project-prod-data \
  --location=us-central1 \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access \
  --public-access-prevention

# Create a multi-region bucket
gcloud storage buckets create gs://my-project-global-assets \
  --location=us \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access

# Create an archive bucket for compliance
gcloud storage buckets create gs://my-project-compliance-archive \
  --location=us-central1 \
  --default-storage-class=ARCHIVE \
  --uniform-bucket-level-access \
  --public-access-prevention

# Create a dual-region bucket with Turbo Replication
gcloud storage buckets create gs://my-project-ha-data \
  --location=nam4 \
  --default-storage-class=STANDARD \
  --rpo=ASYNC_TURBO \
  --uniform-bucket-level-access

# Create a bucket with CMEK
gcloud storage buckets create gs://my-project-encrypted-data \
  --location=us-central1 \
  --default-kms-key=projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
  --uniform-bucket-level-access

# Create a bucket with soft delete disabled (no soft-delete retention period)
gcloud storage buckets create gs://my-project-transient-data \
  --location=us-central1 \
  --no-soft-delete
```

### List and Describe Buckets

```bash
# List all buckets in the project
gcloud storage buckets list

# List with details (location, storage class, labels)
gcloud storage buckets list \
  --format="table(name,location,storageClass,timeCreated.date())"

# Describe a specific bucket
gcloud storage buckets describe gs://my-project-prod-data

# Get only the bucket location
gcloud storage buckets describe gs://my-bucket \
  --format="get(location)"

# List buckets with a prefix
gcloud storage buckets list --filter="name:my-project-*"
```

### Update Bucket Settings

```bash
# Enable versioning on an existing bucket
gcloud storage buckets update gs://my-bucket --versioning

# Disable versioning
gcloud storage buckets update gs://my-bucket --no-versioning

# Update default storage class
gcloud storage buckets update gs://my-bucket --default-storage-class=NEARLINE

# Add labels to a bucket
gcloud storage buckets update gs://my-bucket \
  --update-labels=env=production,team=backend

# Remove a label
gcloud storage buckets update gs://my-bucket --remove-labels=old-label

# Enable Autoclass (automatically manages object storage classes)
gcloud storage buckets update gs://my-bucket --enable-autoclass

# Disable Autoclass
gcloud storage buckets update gs://my-bucket --no-enable-autoclass

# Set retention policy (objects cannot be deleted for 365 days)
gcloud storage buckets update gs://my-bucket \
  --retention-period=365d

# Lock the retention policy (makes it permanent/immutable — irreversible!)
gcloud storage buckets update gs://my-bucket --lock-retention-period

# Enable public access prevention
gcloud storage buckets update gs://my-bucket --public-access-prevention

# Disable public access prevention (allows public IAM grants)
gcloud storage buckets update gs://my-bucket --no-public-access-prevention

# Set soft delete retention (in seconds; 0 disables)
gcloud storage buckets update gs://my-bucket \
  --soft-delete-duration=604800  # 7 days in seconds
```

### Delete Buckets

```bash
# Delete an empty bucket
gcloud storage buckets delete gs://my-empty-bucket

# Delete a bucket and ALL its contents (irreversible!)
gcloud storage rm --recursive gs://my-bucket/**
gcloud storage buckets delete gs://my-bucket
```

---

## Objects

### Copy and Upload

```bash
# Upload a single file
gcloud storage cp local-file.txt gs://my-bucket/path/local-file.txt

# Upload with a specific storage class
gcloud storage cp local-file.csv gs://my-bucket/data/file.csv \
  --storage-class=NEARLINE

# Upload a directory recursively
gcloud storage cp --recursive ./my-dir/ gs://my-bucket/my-dir/

# Parallel upload of many files (faster for many small files)
gcloud storage cp --recursive ./dataset/ gs://my-bucket/dataset/

# Copy between buckets
gcloud storage cp gs://source-bucket/file.txt gs://dest-bucket/file.txt

# Copy all objects matching a prefix
gcloud storage cp gs://my-bucket/logs/* gs://backup-bucket/logs/

# gsutil equivalent with parallel composite upload (for large files >150 MB)
gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" \
  cp large-file.tar.gz gs://my-bucket/
```

### Move and Rename

```bash
# Move/rename an object within a bucket
gcloud storage mv gs://my-bucket/old-name.txt gs://my-bucket/new-name.txt

# Move from one bucket to another
gcloud storage mv gs://source-bucket/file.txt gs://dest-bucket/file.txt
```

### List Objects

```bash
# List objects in a bucket
gcloud storage ls gs://my-bucket/

# List with full details (size, time, storage class)
gcloud storage ls --long gs://my-bucket/

# Recursively list all objects
gcloud storage ls --recursive gs://my-bucket/

# List objects with a prefix
gcloud storage ls gs://my-bucket/logs/

# List with format
gcloud storage objects list gs://my-bucket/ \
  --format="table(name,size,timeCreated.date(),storageClass)"

# List all versions of objects (when versioning is enabled)
gcloud storage ls --all-versions gs://my-bucket/important-file.txt
```

### Describe Objects

```bash
# Describe a single object (metadata, size, hash, storage class)
gcloud storage objects describe gs://my-bucket/path/to/file.txt

# Get only the object size
gcloud storage objects describe gs://my-bucket/file.txt \
  --format="get(size)"

# Get MD5 hash for integrity verification
gcloud storage objects describe gs://my-bucket/file.txt \
  --format="get(md5Hash)"
```

### Download (Cat)

```bash
# Download a file to local disk
gcloud storage cp gs://my-bucket/file.txt ./local-file.txt

# Print object contents to stdout
gcloud storage cat gs://my-bucket/config.json

# Download a directory recursively
gcloud storage cp --recursive gs://my-bucket/data/ ./local-data/
```

### Delete Objects

```bash
# Delete a single object
gcloud storage rm gs://my-bucket/old-file.txt

# Delete all objects with a prefix
gcloud storage rm gs://my-bucket/logs/**

# Delete all objects in a bucket (but keep bucket)
gcloud storage rm --recursive gs://my-bucket/**

# Delete a specific non-current version (requires generation number)
gcloud storage rm gs://my-bucket/file.txt#1712345678901234

# Delete all non-current versions
gcloud storage rm --all-versions gs://my-bucket/file.txt
# (keeps the live version)
```

### Rsync (Sync Directories)

```bash
# Sync local directory to GCS (upload new and modified files only)
gcloud storage rsync ./local-dir/ gs://my-bucket/remote-dir/

# Sync with deletion of files in destination that are not in source
gcloud storage rsync --delete-unmatched-destination-objects \
  ./local-dir/ gs://my-bucket/remote-dir/

# Recursive sync
gcloud storage rsync --recursive ./local-dir/ gs://my-bucket/remote-dir/

# Sync between two GCS locations
gcloud storage rsync gs://source-bucket/data/ gs://dest-bucket/data/

# Exclude certain patterns
gcloud storage rsync --recursive \
  --exclude=".git/.*|.*\.pyc" \
  ./project/ gs://my-bucket/project/
```

---

## Signed URLs

```bash
# Generate a signed URL valid for 1 hour (read)
gcloud storage sign-url gs://my-bucket/private-file.pdf \
  --duration=1h \
  --impersonate-service-account=my-sa@my-project.iam.gserviceaccount.com

# Generate a signed URL for upload (PUT)
gcloud storage sign-url gs://my-bucket/upload-target.json \
  --method=PUT \
  --duration=30m \
  --content-type=application/json \
  --impersonate-service-account=my-sa@my-project.iam.gserviceaccount.com

# Legacy gsutil signurl (requires local service account key file)
gsutil signurl -d 1h -m GET /path/to/key.json gs://my-bucket/file.pdf
```

---

## IAM

```bash
# View the IAM policy for a bucket
gcloud storage buckets get-iam-policy gs://my-bucket

# Grant Storage Object Viewer to a service account
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member=serviceAccount:my-app@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Grant Storage Object Admin to a service account
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member=serviceAccount:my-writer@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin

# Grant read access to a user
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member=user:analyst@example.com \
  --role=roles/storage.objectViewer

# Make bucket publicly readable (do NOT do this for sensitive data)
gcloud storage buckets add-iam-policy-binding gs://my-public-assets \
  --member=allUsers \
  --role=roles/storage.objectViewer

# Remove an IAM binding
gcloud storage buckets remove-iam-policy-binding gs://my-bucket \
  --member=user:former-employee@example.com \
  --role=roles/storage.objectAdmin

# Grant access to a specific prefix (path) using IAM Conditions
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member=serviceAccount:my-app@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer \
  --condition='expression=resource.name.startsWith("projects/_/buckets/my-bucket/objects/data/team-a/"),title=team-a-only'
```

---

## Lifecycle Configuration

```bash
# Set lifecycle rules from a JSON file
gcloud storage buckets update gs://my-bucket \
  --lifecycle-file=lifecycle.json

# lifecycle.json example:
# {
#   "rule": [
#     {
#       "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
#       "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
#     },
#     {
#       "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
#       "condition": {"age": 90}
#     },
#     {
#       "action": {"type": "Delete"},
#       "condition": {"age": 365}
#     },
#     {
#       "action": {"type": "Delete"},
#       "condition": {"isLive": false, "numNewerVersions": 2}
#     }
#   ]
# }

# View current lifecycle configuration
gcloud storage buckets describe gs://my-bucket \
  --format="get(lifecycle)"

# Remove all lifecycle rules
gcloud storage buckets update gs://my-bucket --clear-lifecycle
```

---

## Versioning

```bash
# Enable versioning
gcloud storage buckets update gs://my-bucket --versioning

# Check versioning status
gcloud storage buckets describe gs://my-bucket \
  --format="get(versioning)"

# List all versions of an object
gcloud storage ls --all-versions gs://my-bucket/file.txt

# Restore a previous version (copy from non-current to current)
gcloud storage cp \
  "gs://my-bucket/file.txt#GENERATION_NUMBER" \
  gs://my-bucket/file.txt

# Delete all non-current versions of an object
gsutil rm -a gs://my-bucket/file.txt  # legacy gsutil

# Disable versioning
gcloud storage buckets update gs://my-bucket --no-versioning
```

---

## CORS Configuration

```bash
# Set CORS configuration from a JSON file
gcloud storage buckets update gs://my-bucket \
  --cors-file=cors.json

# cors.json example:
# [
#   {
#     "origin": ["https://app.example.com", "https://staging.example.com"],
#     "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
#     "responseHeader": ["Content-Type", "x-goog-resumable"],
#     "maxAgeSeconds": 3600
#   }
# ]

# View current CORS configuration
gcloud storage buckets describe gs://my-bucket --format="get(cors)"

# Remove CORS configuration
gcloud storage buckets update gs://my-bucket --clear-cors
```

---

## Pub/Sub Notifications

```bash
# Create a notification on a bucket to publish to a Pub/Sub topic
gcloud storage buckets notifications create gs://my-bucket \
  --topic=my-bucket-notifications \
  --event-types=OBJECT_FINALIZE,OBJECT_DELETE \
  --payload-format=JSON_API_V1

# Create notification for all events
gcloud storage buckets notifications create gs://my-bucket \
  --topic=projects/my-project/topics/my-topic \
  --event-types=OBJECT_FINALIZE \
  --object-prefix=uploads/ \
  --payload-format=JSON_API_V1

# List notifications for a bucket
gcloud storage buckets notifications list gs://my-bucket

# Delete a notification
gcloud storage buckets notifications delete 1 --bucket=my-bucket
```

---

## Transfer Operations

```bash
# Use gsutil for parallel transfer with multiple streams (legacy but effective for large files)
gsutil -m cp -r gs://source-bucket/ gs://dest-bucket/

# Large file: parallel composite upload (uploads in parallel chunks then composes)
gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" \
  cp 50GB-file.tar.gz gs://my-bucket/

# Parallel download
gsutil -m cp -r gs://my-bucket/large-dataset/ ./local-copy/

# Resume an interrupted transfer
gsutil -m rsync -r gs://source-bucket/data/ gs://dest-bucket/data/
```

---

## gsutil — Legacy Commands (Still Useful)

```bash
# Check gsutil version
gsutil version

# Get bucket and object statistics
gsutil du -s gs://my-bucket/          # Total size of all objects
gsutil du -sh gs://my-bucket/         # Human-readable size
gsutil du gs://my-bucket/prefix/      # Size per object with prefix

# Change object storage class
gsutil rewrite -s NEARLINE gs://my-bucket/old-data/**

# Set bucket labels via gsutil
gsutil label set labels.json gs://my-bucket

# Enable/disable object versioning
gsutil versioning set on gs://my-bucket
gsutil versioning set off gs://my-bucket

# Get object ACL (legacy)
gsutil acl get gs://my-bucket/file.txt

# Test bucket access (check if you have permission)
gsutil ls gs://my-bucket/ &>/dev/null && echo "Access OK" || echo "No access"
```
