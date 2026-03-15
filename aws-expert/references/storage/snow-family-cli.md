# AWS Snow Family — CLI Reference

For service concepts, see [snow-family-capabilities.md](snow-family-capabilities.md).

```bash
# --- Jobs ---
# Create an import job (ship data to AWS)
aws snowball create-job \
  --job-type IMPORT \
  --resources '{"S3Resources":[{"BucketArn":"arn:aws:s3:::my-bucket","KeyRange":{}}]}' \
  --address-id address-id-xxx \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/key-id \
  --role-arn arn:aws:iam::123456789012:role/SnowballRole \
  --snowball-capacity-preference T80 \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --shipping-option NEXT_DAY

# Create an export job (ship data from AWS)
aws snowball create-job \
  --job-type EXPORT \
  --resources '{"S3Resources":[{"BucketArn":"arn:aws:s3:::my-bucket","KeyRange":{"BeginMarker":"prefix/","EndMarker":"prefix0"}}]}' \
  --address-id address-id-xxx \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/key-id \
  --role-arn arn:aws:iam::123456789012:role/SnowballRole \
  --snowball-type EDGE_COMPUTE_OPTIMIZED \
  --shipping-option STANDARD

# Local compute and storage job (no data import/export)
aws snowball create-job \
  --job-type LOCAL_USE \
  --snowball-type EDGE_COMPUTE_OPTIMIZED \
  --address-id address-id-xxx \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/key-id \
  --role-arn arn:aws:iam::123456789012:role/SnowballRole

# --- Job management ---
aws snowball list-jobs
aws snowball describe-job --job-id job-0123456789abcdef0
aws snowball describe-jobs --job-ids job-0123456789abcdef0 job-9876543210fedcba0

# Get shipping label (after job is in WithCustomer state, to return device)
aws snowball get-job-manifest --job-id job-0123456789abcdef0   # returns S3 presigned URL
aws snowball get-job-unlock-code --job-id job-0123456789abcdef0

# Cancel a job (only when in New or PreparingAppliance state)
aws snowball cancel-job --job-id job-0123456789abcdef0

# --- Addresses ---
aws snowball create-address --address file://shipping-address.json
aws snowball list-addresses
aws snowball describe-address --address-id address-id-xxx

# --- Clusters (Snowball Edge clustering, 5–10 nodes) ---
aws snowball create-cluster \
  --job-type LOCAL_USE \
  --resources '{"S3Resources":[{"BucketArn":"arn:aws:s3:::my-bucket","KeyRange":{}}]}' \
  --address-id address-id-xxx \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/key-id \
  --role-arn arn:aws:iam::123456789012:role/SnowballRole \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --shipping-option NEXT_DAY

aws snowball describe-cluster --cluster-id cluster-0123456789abcdef0
aws snowball list-clusters
aws snowball list-cluster-jobs --cluster-id cluster-0123456789abcdef0
aws snowball cancel-cluster --cluster-id cluster-0123456789abcdef0

# --- Long-term pricing ---
aws snowball list-long-term-pricing
aws snowball create-long-term-pricing \
  --long-term-pricing-type OneYear \
  --snowball-type EDGE_STORAGE_OPTIMIZED \
  --is-long-term-pricing-auto-renew
```
