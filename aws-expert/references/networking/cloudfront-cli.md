# AWS CloudFront — CLI Reference
For service concepts, see [cloudfront-capabilities.md](cloudfront-capabilities.md).

## CloudFront

```bash
# --- Distributions ---
# Create distribution from a JSON config file
aws cloudfront create-distribution \
  --distribution-config file://distribution-config.json

# List all distributions
aws cloudfront list-distributions

# Get distribution details (includes ETag needed for updates)
aws cloudfront get-distribution --id E1234ABCDEF

# Get just the config (lighter output, includes ETag)
aws cloudfront get-distribution-config --id E1234ABCDEF

# Update distribution (requires ETag from get-distribution-config)
aws cloudfront update-distribution \
  --id E1234ABCDEF \
  --distribution-config file://updated-config.json \
  --if-match E2QWRUHEXAMPLE

# Disable a distribution (required before deletion)
# Edit JSON: set "Enabled": false, then update-distribution
aws cloudfront delete-distribution --id E1234ABCDEF --if-match E2QWRUHEXAMPLE

# --- Cache Invalidation ---
# Invalidate specific paths
aws cloudfront create-invalidation \
  --distribution-id E1234ABCDEF \
  --paths /index.html /images/*

# Invalidate everything
aws cloudfront create-invalidation \
  --distribution-id E1234ABCDEF \
  --paths "/*"

aws cloudfront list-invalidations --distribution-id E1234ABCDEF
aws cloudfront get-invalidation --distribution-id E1234ABCDEF --id I1234ABCDEF

# --- Origin Access Control (OAC) ---
aws cloudfront create-origin-access-control \
  --origin-access-control-config '{
    "Name": "my-s3-oac",
    "Description": "OAC for S3 bucket origin",
    "OriginAccessControlOriginType": "s3",
    "SigningBehavior": "always",
    "SigningProtocol": "sigv4"
  }'

aws cloudfront list-origin-access-controls
aws cloudfront get-origin-access-control --id EABCDEF12345

# --- Cache & Origin Policies ---
aws cloudfront create-cache-policy \
  --cache-policy-config file://cache-policy.json

aws cloudfront list-cache-policies --type custom
aws cloudfront get-cache-policy --id abc123

aws cloudfront create-origin-request-policy \
  --origin-request-policy-config file://origin-request-policy.json

# --- CloudFront Functions ---
aws cloudfront create-function \
  --name url-rewrite-function \
  --function-config Comment="URL rewrite",Runtime=cloudfront-js-2.0 \
  --function-code fileb://function.js

aws cloudfront publish-function \
  --name url-rewrite-function \
  --if-match EABCDEF12345

aws cloudfront list-functions --stage LIVE

# --- Response Headers Policies ---
aws cloudfront create-response-headers-policy \
  --response-headers-policy-config file://security-headers.json

# --- Real-time Log Config ---
aws cloudfront create-realtime-log-config \
  --end-points '[{"StreamType":"Kinesis","KinesisStreamConfig":{"RoleARN":"arn:aws:iam::123456789012:role/CloudFrontRealtimeLogs","StreamARN":"arn:aws:kinesis:us-east-1:123456789012:stream/cf-logs"}}]' \
  --fields timestamp c-ip cs-method sc-status cs-uri-stem \
  --name my-realtime-config \
  --sampling-rate 5

# --- Key Groups (for Signed URLs/Cookies) ---
aws cloudfront create-key-group \
  --key-group-config '{
    "Name": "my-key-group",
    "Items": ["K1234ABCDEF"],
    "Comment": "Key group for signed URLs"
  }'

aws cloudfront create-public-key \
  --public-key-config '{
    "CallerReference": "my-key-2024",
    "Name": "my-public-key",
    "EncodedKey": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"
  }'
```
