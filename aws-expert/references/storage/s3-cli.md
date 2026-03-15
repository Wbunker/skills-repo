# AWS S3 — CLI Reference
For service concepts, see [s3-capabilities.md](s3-capabilities.md).

## S3 — High-Level

The `aws s3` commands provide a Unix-like interface for common operations. They handle multipart uploads and recursive operations automatically.

```bash
# --- Buckets ---
aws s3 mb s3://my-bucket                                    # create bucket
aws s3 mb s3://my-bucket --region us-west-2
aws s3 rb s3://my-bucket                                    # remove empty bucket
aws s3 rb s3://my-bucket --force                            # remove bucket + all objects

# --- Listing ---
aws s3 ls                                                   # list all buckets
aws s3 ls s3://my-bucket                                    # list top-level prefixes and objects
aws s3 ls s3://my-bucket/prefix/ --recursive                # list all objects under prefix
aws s3 ls s3://my-bucket --recursive --human-readable --summarize

# --- Copy ---
aws s3 cp file.txt s3://my-bucket/file.txt                  # upload local file
aws s3 cp s3://my-bucket/file.txt ./file.txt                # download file
aws s3 cp s3://src-bucket/key s3://dst-bucket/key           # server-side copy
aws s3 cp ./localdir s3://my-bucket/prefix/ --recursive     # upload directory
aws s3 cp s3://my-bucket/prefix/ ./localdir --recursive     # download prefix

# Copy with metadata and storage class
aws s3 cp file.txt s3://my-bucket/file.txt \
  --storage-class STANDARD_IA \
  --server-side-encryption aws:kms \
  --sse-kms-key-id alias/my-key \
  --metadata '{"owner":"team-a"}'

# Copy with include/exclude filters
aws s3 cp ./logs s3://my-bucket/logs/ --recursive \
  --include "*.log" --exclude "*.tmp"

# --- Move ---
aws s3 mv file.txt s3://my-bucket/file.txt                  # move local to S3
aws s3 mv s3://my-bucket/old-key s3://my-bucket/new-key     # rename object
aws s3 mv s3://src-bucket/ s3://dst-bucket/ --recursive     # move all objects

# --- Sync ---
# Sync local directory to S3 (uploads new/modified files; does not delete by default)
aws s3 sync ./localdir s3://my-bucket/prefix/

# Sync and delete objects not in source
aws s3 sync ./localdir s3://my-bucket/prefix/ --delete

# Sync S3 to S3 (cross-bucket, cross-region)
aws s3 sync s3://src-bucket/ s3://dst-bucket/ --source-region us-east-1 --region us-west-2

# Sync with storage class override
aws s3 sync ./archive s3://my-bucket/archive/ \
  --storage-class GLACIER \
  --sse aws:kms

# Dry run (what would be transferred)
aws s3 sync ./localdir s3://my-bucket/ --dryrun

# --- Delete ---
aws s3 rm s3://my-bucket/file.txt                           # delete single object
aws s3 rm s3://my-bucket/prefix/ --recursive                # delete all objects under prefix

# --- Presigned URL ---
aws s3 presign s3://my-bucket/file.txt                      # URL valid for 1 hour (default)
aws s3 presign s3://my-bucket/file.txt --expires-in 3600    # explicit 1-hour expiry

# --- Static Website ---
aws s3 website s3://my-bucket \
  --index-document index.html \
  --error-document error.html
```

---

## S3 — Low-Level

The `aws s3api` commands map directly to S3 REST API operations, providing full control over all parameters.

```bash
# --- Bucket creation and location ---
# Create bucket in us-east-1 (no LocationConstraint needed)
aws s3api create-bucket --bucket my-bucket

# Create bucket in other regions
aws s3api create-bucket --bucket my-bucket \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

aws s3api get-bucket-location --bucket my-bucket
aws s3api list-buckets
aws s3api head-bucket --bucket my-bucket
aws s3api delete-bucket --bucket my-bucket

# --- Block Public Access ---
aws s3api put-public-access-block --bucket my-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api get-public-access-block --bucket my-bucket

# --- Bucket policy ---
aws s3api put-bucket-policy --bucket my-bucket --policy file://bucket-policy.json
aws s3api get-bucket-policy --bucket my-bucket
aws s3api delete-bucket-policy --bucket my-bucket

# Example: enforce HTTPS-only access
cat > https-policy.json <<'EOF'
{
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
    "Condition": {"Bool": {"aws:SecureTransport": "false"}}
  }]
}
EOF
aws s3api put-bucket-policy --bucket my-bucket --policy file://https-policy.json

# --- Versioning ---
aws s3api put-bucket-versioning --bucket my-bucket \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning --bucket my-bucket \
  --versioning-configuration Status=Suspended

aws s3api get-bucket-versioning --bucket my-bucket

# --- Lifecycle configuration ---
aws s3api put-bucket-lifecycle-configuration --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

aws s3api get-bucket-lifecycle-configuration --bucket my-bucket
aws s3api delete-bucket-lifecycle --bucket my-bucket

# Example lifecycle: transition to IA at 30 days, Glacier at 90 days, expire at 365 days
cat > lifecycle.json <<'EOF'
{
  "Rules": [{
    "ID": "archive-rule",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER"}
    ],
    "Expiration": {"Days": 365},
    "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
  }]
}
EOF

# --- Replication (CRR / SRR) ---
aws s3api put-bucket-replication --bucket src-bucket \
  --replication-configuration file://replication.json

aws s3api get-bucket-replication --bucket src-bucket
aws s3api delete-bucket-replication --bucket src-bucket

# Example replication config (source and destination must have versioning enabled)
cat > replication.json <<'EOF'
{
  "Role": "arn:aws:iam::123456789012:role/ReplicationRole",
  "Rules": [{
    "Status": "Enabled",
    "Filter": {"Prefix": ""},
    "Destination": {
      "Bucket": "arn:aws:s3:::dst-bucket",
      "StorageClass": "STANDARD_IA"
    }
  }]
}
EOF

# --- Event notifications ---
aws s3api put-bucket-notification-configuration --bucket my-bucket \
  --notification-configuration file://notification.json

aws s3api get-bucket-notification-configuration --bucket my-bucket

# Example: trigger Lambda on object creation
cat > notification.json <<'EOF'
{
  "LambdaFunctionConfigurations": [{
    "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessUpload",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {"Key": {"FilterRules": [{"Name": "suffix", "Value": ".csv"}]}}
  }]
}
EOF

# --- Object operations ---
aws s3api put-object --bucket my-bucket --key path/to/file.txt --body ./file.txt
aws s3api put-object --bucket my-bucket --key file.txt --body ./file.txt \
  --storage-class STANDARD_IA \
  --server-side-encryption aws:kms \
  --ssekms-key-id alias/my-key \
  --content-type "text/plain"

aws s3api get-object --bucket my-bucket --key file.txt ./output.txt
aws s3api get-object --bucket my-bucket --key file.txt ./output.txt \
  --version-id abc123                                       # get specific version

aws s3api head-object --bucket my-bucket --key file.txt
aws s3api delete-object --bucket my-bucket --key file.txt
aws s3api delete-object --bucket my-bucket --key file.txt --version-id abc123

# Delete multiple objects at once
aws s3api delete-objects --bucket my-bucket \
  --delete '{"Objects":[{"Key":"a.txt"},{"Key":"b.txt"}]}'

# Copy object server-side (change storage class, re-encrypt, etc.)
aws s3api copy-object \
  --copy-source my-bucket/old-key \
  --bucket my-bucket --key new-key \
  --storage-class GLACIER

# --- Object tagging ---
aws s3api put-object-tagging --bucket my-bucket --key file.txt \
  --tagging '{"TagSet":[{"Key":"env","Value":"prod"}]}'
aws s3api get-object-tagging --bucket my-bucket --key file.txt

# --- Listing objects ---
aws s3api list-objects-v2 --bucket my-bucket
aws s3api list-objects-v2 --bucket my-bucket --prefix logs/ --max-items 100
aws s3api list-objects-v2 --bucket my-bucket \
  --query 'Contents[?Size>`1048576`].[Key,Size]' --output table  # objects >1MB

aws s3api list-object-versions --bucket my-bucket --prefix path/
aws s3api list-multipart-uploads --bucket my-bucket

# --- Multipart upload ---
# Initiate
UPLOAD_ID=$(aws s3api create-multipart-upload \
  --bucket my-bucket --key large-file.tar.gz \
  --query UploadId --output text)

# Upload parts (each ≥5 MB except the last)
aws s3api upload-part --bucket my-bucket --key large-file.tar.gz \
  --part-number 1 --upload-id "$UPLOAD_ID" --body part1.bin

# Complete multipart upload
aws s3api complete-multipart-upload --bucket my-bucket --key large-file.tar.gz \
  --upload-id "$UPLOAD_ID" \
  --multipart-upload '{"Parts":[{"ETag":"etag1","PartNumber":1}]}'

# Abort (clean up incomplete upload)
aws s3api abort-multipart-upload --bucket my-bucket --key large-file.tar.gz \
  --upload-id "$UPLOAD_ID"

# --- Encryption defaults ---
aws s3api put-bucket-encryption --bucket my-bucket \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"alias/my-key"},"BucketKeyEnabled":true}]}'

# --- Object Lock ---
aws s3api put-object-lock-configuration --bucket my-bucket \
  --object-lock-configuration \
  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"GOVERNANCE","Days":90}}}'

# --- Intelligent-Tiering ---
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-bucket --id all-objects \
  --intelligent-tiering-configuration \
  '{"Id":"all-objects","Status":"Enabled","Tierings":[{"Days":90,"AccessTier":"ARCHIVE_ACCESS"},{"Days":180,"AccessTier":"DEEP_ARCHIVE_ACCESS"}]}'

# --- Static website ---
aws s3api put-bucket-website --bucket my-bucket \
  --website-configuration \
  '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"error.html"}}'

# --- CORS ---
aws s3api put-bucket-cors --bucket my-bucket \
  --cors-configuration file://cors.json

# --- Access logging ---
aws s3api put-bucket-logging --bucket my-bucket \
  --bucket-logging-status \
  '{"LoggingEnabled":{"TargetBucket":"my-log-bucket","TargetPrefix":"s3-access-logs/"}}'

# --- Requester Pays ---
aws s3api put-bucket-request-payment --bucket my-bucket \
  --request-payment-configuration Payer=Requester
```

---

## S3 Vectors

The `aws s3vectors` namespace manages vector buckets, indexes, and vector data for ANN similarity search.

```bash
# --- Vector Buckets ---
aws s3vectors create-vector-bucket \
  --vector-bucket-name my-vector-bucket \
  --region us-east-1

aws s3vectors list-vector-buckets
aws s3vectors get-vector-bucket --vector-bucket-name my-vector-bucket
aws s3vectors delete-vector-bucket --vector-bucket-name my-vector-bucket

# --- Bucket Policies ---
aws s3vectors put-vector-bucket-policy \
  --vector-bucket-name my-vector-bucket \
  --policy file://vector-bucket-policy.json
aws s3vectors get-vector-bucket-policy --vector-bucket-name my-vector-bucket
aws s3vectors delete-vector-bucket-policy --vector-bucket-name my-vector-bucket

# --- Vector Indexes ---
# Create an index (distance metric and dimension are immutable after creation)
aws s3vectors create-index \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --data-type float32 \
  --dimension 1024 \
  --distance-metric cosine

aws s3vectors list-indexes --vector-bucket-name my-vector-bucket
aws s3vectors get-index \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index
aws s3vectors delete-index \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index

# --- Vector Operations ---
# Write vectors (up to 500 per call)
aws s3vectors put-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --vectors '[
    {
      "key": "doc-001",
      "data": {"float32": [0.1, 0.2, 0.3]},
      "metadata": {"source": "wiki", "lang": "en"}
    }
  ]'

# Retrieve specific vectors by key (up to 100 per call)
aws s3vectors get-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --keys '["doc-001", "doc-002"]'

# List vectors in an index
aws s3vectors list-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --max-results 100

# Delete vectors (up to 500 per call)
aws s3vectors delete-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --keys '["doc-001"]'

# --- ANN Query (similarity search) ---
# Basic top-K query
aws s3vectors query-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --query-vector '{"float32": [0.15, 0.25, 0.35]}' \
  --top-k 10

# Query with metadata filter and return distances
aws s3vectors query-vectors \
  --vector-bucket-name my-vector-bucket \
  --index-name my-index \
  --query-vector '{"float32": [0.15, 0.25, 0.35]}' \
  --top-k 5 \
  --filter '{"lang": {"$eq": "en"}}' \
  --return-distance \
  --return-metadata

# --- Tagging ---
aws s3vectors tag-resource \
  --resource-arn arn:aws:s3vectors:us-east-1:123456789012:bucket/my-vector-bucket \
  --tags '{"project": "rag-pipeline"}'
aws s3vectors list-tags-for-resource \
  --resource-arn arn:aws:s3vectors:us-east-1:123456789012:bucket/my-vector-bucket
```
