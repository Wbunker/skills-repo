# Secret Manager — CLI Reference

## Creating Secrets

```bash
# Create a secret with automatic replication
gcloud secrets create my-api-key \
  --project=PROJECT_ID

# Create a secret and immediately set an initial value from a file
gcloud secrets create my-db-password \
  --data-file=password.txt \
  --project=PROJECT_ID

# Create a secret with a string value (use with caution — value visible in shell history)
echo -n "my-secret-value" | gcloud secrets create my-secret \
  --data-file=- \
  --project=PROJECT_ID

# Create a secret with user-managed replication (specific regions)
gcloud secrets create my-regional-secret \
  --replication-policy=user-managed \
  --locations=us-central1,us-east1 \
  --project=PROJECT_ID

# Create a secret with user-managed replication and CMEK per region
gcloud secrets create my-cmek-secret \
  --replication-policy=user-managed \
  --locations=us-central1 \
  --kms-key-name=projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
  --project=PROJECT_ID

# Create a secret with automatic replication and CMEK
gcloud secrets create my-auto-cmek-secret \
  --replication-policy=automatic \
  --kms-key-name=projects/PROJECT_ID/locations/global/keyRings/global-keyring/cryptoKeys/my-key \
  --project=PROJECT_ID

# Create a secret with labels
gcloud secrets create my-labeled-secret \
  --labels=env=production,team=backend,app=my-service \
  --project=PROJECT_ID

# Create a secret with a TTL (auto-destroy after 24 hours)
gcloud secrets create temp-setup-cred \
  --ttl=86400s \
  --project=PROJECT_ID

# Create a secret with rotation and Pub/Sub notification
gcloud secrets create my-rotating-secret \
  --rotation-period=7776000s \
  --next-rotation-time="2025-06-01T00:00:00Z" \
  --topics=projects/PROJECT_ID/topics/secret-rotation \
  --project=PROJECT_ID
```

---

## Describing and Listing Secrets

```bash
# List all secrets in a project
gcloud secrets list --project=PROJECT_ID

# List secrets with specific format
gcloud secrets list \
  --project=PROJECT_ID \
  --format="table(name,createTime,replication.replicationPolicy)"

# Filter secrets by label
gcloud secrets list \
  --filter="labels.env=production" \
  --project=PROJECT_ID

# Describe a secret (metadata only; not the payload)
gcloud secrets describe my-api-key \
  --project=PROJECT_ID

# Describe a secret as JSON
gcloud secrets describe my-api-key \
  --project=PROJECT_ID \
  --format=json
```

---

## Updating Secrets

```bash
# Update labels on a secret
gcloud secrets update my-api-key \
  --update-labels=team=platform \
  --project=PROJECT_ID

# Remove a specific label
gcloud secrets update my-api-key \
  --remove-labels=old-label \
  --project=PROJECT_ID

# Add a Pub/Sub rotation topic
gcloud secrets update my-api-key \
  --add-topics=projects/PROJECT_ID/topics/rotation-notifications \
  --project=PROJECT_ID

# Remove a rotation topic
gcloud secrets update my-api-key \
  --remove-topics=projects/PROJECT_ID/topics/rotation-notifications \
  --project=PROJECT_ID

# Update rotation schedule
gcloud secrets update my-rotating-secret \
  --rotation-period=15552000s \
  --next-rotation-time="2026-01-01T00:00:00Z" \
  --project=PROJECT_ID

# Remove rotation schedule
gcloud secrets update my-rotating-secret \
  --remove-rotation-schedule \
  --project=PROJECT_ID

# Set annotations (requires beta)
gcloud beta secrets update my-api-key \
  --update-annotations=owner=alice@example.com,rotation-contact=security@example.com \
  --project=PROJECT_ID
```

---

## Deleting Secrets

```bash
# Delete a secret and all its versions (irreversible)
gcloud secrets delete my-api-key \
  --project=PROJECT_ID

# Delete without interactive confirmation
gcloud secrets delete my-api-key \
  --project=PROJECT_ID \
  --quiet
```

---

## Secret Versions — Adding

```bash
# Add a new version from a file
gcloud secrets versions add my-api-key \
  --data-file=new-api-key.txt \
  --project=PROJECT_ID

# Add a new version from stdin
echo -n "new-secret-value" | gcloud secrets versions add my-api-key \
  --data-file=- \
  --project=PROJECT_ID

# Add a version from an environment variable value (pipe without newline)
printf '%s' "$MY_SECRET_VALUE" | gcloud secrets versions add my-api-key \
  --data-file=- \
  --project=PROJECT_ID
```

---

## Secret Versions — Accessing

```bash
# Access (read) the latest enabled version of a secret
gcloud secrets versions access latest \
  --secret=my-api-key \
  --project=PROJECT_ID

# Access a specific version number
gcloud secrets versions access 3 \
  --secret=my-api-key \
  --project=PROJECT_ID

# Access and write to a file
gcloud secrets versions access latest \
  --secret=my-api-key \
  --project=PROJECT_ID \
  --out-file=retrieved-secret.txt

# Access and pipe to another command
gcloud secrets versions access latest \
  --secret=my-db-password \
  --project=PROJECT_ID | psql -U admin -h db.example.com

# Access a regional secret
gcloud secrets versions access latest \
  --secret=my-regional-secret \
  --location=us-central1 \
  --project=PROJECT_ID
```

---

## Secret Versions — Listing and Describing

```bash
# List all versions of a secret
gcloud secrets versions list my-api-key \
  --project=PROJECT_ID

# List with state filter
gcloud secrets versions list my-api-key \
  --filter="state=ENABLED" \
  --project=PROJECT_ID

# List all versions (including disabled and destroyed)
gcloud secrets versions list my-api-key \
  --filter="state!=DESTROYED" \
  --project=PROJECT_ID

# Describe a specific version (metadata only)
gcloud secrets versions describe 2 \
  --secret=my-api-key \
  --project=PROJECT_ID

# Describe the latest version
gcloud secrets versions describe latest \
  --secret=my-api-key \
  --project=PROJECT_ID
```

---

## Secret Versions — Lifecycle Management

```bash
# Disable a version (payload retained; cannot be accessed)
gcloud secrets versions disable 2 \
  --secret=my-api-key \
  --project=PROJECT_ID

# Re-enable a disabled version
gcloud secrets versions enable 2 \
  --secret=my-api-key \
  --project=PROJECT_ID

# Destroy a version (payload irrevocably deleted)
gcloud secrets versions destroy 1 \
  --secret=my-api-key \
  --project=PROJECT_ID

# Destroy without confirmation prompt
gcloud secrets versions destroy 1 \
  --secret=my-api-key \
  --project=PROJECT_ID \
  --quiet
```

---

## IAM — Secret-Level Access Control

```bash
# Get the IAM policy for a secret
gcloud secrets get-iam-policy my-api-key \
  --project=PROJECT_ID

# Grant a service account access to read a secret
gcloud secrets add-iam-policy-binding my-api-key \
  --member="serviceAccount:app-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# Grant a user access to read a specific secret
gcloud secrets add-iam-policy-binding my-api-key \
  --member="user:developer@example.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# Grant a service account the ability to add new versions (rotation automation)
gcloud secrets add-iam-policy-binding my-rotating-secret \
  --member="serviceAccount:rotation-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretVersionAdder" \
  --project=PROJECT_ID

# Grant full version management (add, enable, disable, destroy)
gcloud secrets add-iam-policy-binding my-api-key \
  --member="serviceAccount:lifecycle-manager@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretVersionManager" \
  --project=PROJECT_ID

# Remove a binding
gcloud secrets remove-iam-policy-binding my-api-key \
  --member="user:former-employee@example.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# Set the complete IAM policy from a file (replaces all bindings)
gcloud secrets set-iam-policy my-api-key policy.json \
  --project=PROJECT_ID
```

---

## Replication Configuration Examples

```bash
# Create a secret with 3-region user-managed replication
gcloud secrets create multi-region-secret \
  --replication-policy=user-managed \
  --locations=us-central1,us-east1,europe-west1 \
  --project=PROJECT_ID

# Create with per-region CMEK keys (different key per region)
# (requires a YAML-based approach via the API; gcloud currently supports single KMS key)
# Use the REST API or Terraform for per-region CMEK with different keys:
# REST API body:
# {
#   "replication": {
#     "userManaged": {
#       "replicas": [
#         {
#           "location": "us-central1",
#           "customerManagedEncryption": {
#             "kmsKeyName": "projects/P/locations/us-central1/keyRings/R/cryptoKeys/K1"
#           }
#         },
#         {
#           "location": "europe-west1",
#           "customerManagedEncryption": {
#             "kmsKeyName": "projects/P/locations/europe-west1/keyRings/R/cryptoKeys/K2"
#           }
#         }
#       ]
#     }
#   }
# }
```

---

## Rotation Notification Setup

```bash
# Step 1: Create a Pub/Sub topic for rotation events
gcloud pubsub topics create secret-rotation-notifications \
  --project=PROJECT_ID

# Step 2: Grant Secret Manager permission to publish to the topic
gcloud pubsub topics add-iam-policy-binding secret-rotation-notifications \
  --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-secretmanager.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher" \
  --project=PROJECT_ID

# Step 3: Create a secret with rotation schedule pointing at the topic
gcloud secrets create my-auto-rotating-key \
  --rotation-period=7776000s \
  --next-rotation-time="2025-04-01T00:00:00Z" \
  --topics=projects/PROJECT_ID/topics/secret-rotation-notifications \
  --data-file=initial-key.txt \
  --project=PROJECT_ID

# Step 4: Create a Pub/Sub subscription for the rotation handler
gcloud pubsub subscriptions create rotation-handler-sub \
  --topic=secret-rotation-notifications \
  --push-endpoint=https://my-cloud-run-service-HASH-uc.a.run.app/rotate \
  --push-auth-service-account=rotation-invoker@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID
```

---

## Bulk Operations and Auditing

```bash
# List all secrets with their latest version state
gcloud secrets list \
  --project=PROJECT_ID \
  --format="table(name,createTime)" | while read name rest; do
    echo -n "$name: "
    gcloud secrets versions describe latest --secret="$name" --project=PROJECT_ID \
      --format="value(name,state)" 2>/dev/null || echo "no versions"
  done

# Find secrets that have not been rotated recently (no new versions in 90 days)
gcloud secrets list \
  --project=PROJECT_ID \
  --format="value(name)" | while read name; do
    latest_time=$(gcloud secrets versions describe latest \
      --secret="$name" --project=PROJECT_ID \
      --format="value(createTime)" 2>/dev/null)
    echo "$name: $latest_time"
  done

# View audit log entries for secret access (requires Data Access logs enabled)
gcloud logging read \
  'resource.type="secretmanager.googleapis.com/Secret" AND logName:"cloudaudit.googleapis.com%2Fdata_access"' \
  --project=PROJECT_ID \
  --limit=100 \
  --format="table(timestamp,protoPayload.methodName,protoPayload.resourceName,protoPayload.authenticationInfo.principalEmail)"

# View secret access audit logs for a specific secret
gcloud logging read \
  'resource.type="secretmanager.googleapis.com/Secret" AND resource.labels.secret_id="my-api-key"' \
  --project=PROJECT_ID \
  --limit=50
```
