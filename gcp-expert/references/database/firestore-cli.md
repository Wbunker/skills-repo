# Firestore — CLI Reference

Firestore management uses a combination of `gcloud firestore` (for infrastructure operations) and the Firebase CLI (`firebase`) for rules and indexes deployment.

---

## Database Management (Multi-Database)

Projects can have up to 100 Firestore databases. The default database is named `(default)`.

```bash
# Create a new named Firestore database (Native mode, us-east1)
gcloud firestore databases create \
  --database=my-app-db \
  --location=us-east1 \
  --type=firestore-native

# Create a Firestore database in Datastore mode
gcloud firestore databases create \
  --database=my-legacy-db \
  --location=us-central1 \
  --type=datastore-mode

# Create database with delete protection enabled
gcloud firestore databases create \
  --database=my-prod-db \
  --location=us-central1 \
  --type=firestore-native \
  --delete-protection

# List all databases in the project
gcloud firestore databases list

# Describe a specific database
gcloud firestore databases describe --database=my-app-db

# Describe the default database
gcloud firestore databases describe --database="(default)"

# Update database (enable/disable delete protection)
gcloud firestore databases update --database=my-prod-db \
  --delete-protection

gcloud firestore databases update --database=my-dev-db \
  --no-delete-protection

# Update PITR (point-in-time recovery) retention
gcloud firestore databases update --database=my-prod-db \
  --enable-pitr

gcloud firestore databases update --database=my-dev-db \
  --disable-pitr

# Delete a database (must disable delete protection first if enabled)
gcloud firestore databases delete --database=my-dev-db
```

---

## Export and Import

Exports go to Cloud Storage. Useful for backups, migrations, and loading data into BigQuery.

```bash
# Export entire database to Cloud Storage
gcloud firestore export gs://my-backup-bucket/firestore-exports/$(date +%Y%m%d) \
  --database="(default)"

# Export to a named database
gcloud firestore export gs://my-backup-bucket/exports/my-app-db-$(date +%Y%m%d) \
  --database=my-app-db

# Export specific collection groups only
gcloud firestore export gs://my-backup-bucket/partial-export/ \
  --collection-ids=users,orders,products \
  --database="(default)"

# Import from Cloud Storage (restores documents; does not delete existing docs)
gcloud firestore import gs://my-backup-bucket/firestore-exports/20240301 \
  --database="(default)"

# Import specific collection groups only
gcloud firestore import gs://my-backup-bucket/firestore-exports/20240301 \
  --collection-ids=users,orders \
  --database="(default)"

# Check export/import operation status
gcloud firestore operations list --database="(default)"
gcloud firestore operations describe OPERATION_ID --database="(default)"

# Cancel an in-progress export/import
gcloud firestore operations cancel OPERATION_ID --database="(default)"
```

---

## Indexes

### Using gcloud

```bash
# List all indexes for a database
gcloud firestore indexes composite list \
  --database="(default)"

# List composite indexes with filter
gcloud firestore indexes composite list \
  --database="(default)" \
  --filter="queryScope=COLLECTION"

# Describe a composite index
gcloud firestore indexes composite describe INDEX_ID \
  --database="(default)"

# Delete a composite index
gcloud firestore indexes composite delete INDEX_ID \
  --database="(default)"

# List single-field index configurations (overrides)
gcloud firestore indexes fields list \
  --database="(default)"

# Describe a field index configuration
gcloud firestore indexes fields describe FIELD_PATH \
  --collection-group=users \
  --database="(default)"

# Update field index config (e.g., disable auto-indexing for a large field)
gcloud firestore indexes fields update rawContent \
  --collection-group=logs \
  --database="(default)" \
  --disable-indexes
```

### Using Firebase CLI (Recommended for Indexes)

Managing indexes via `firestore.indexes.json` and Firebase CLI is the standard approach for version-controlled index management.

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in a project directory
firebase init firestore

# firestore.indexes.json example structure:
# {
#   "indexes": [
#     {
#       "collectionGroup": "orders",
#       "queryScope": "COLLECTION",
#       "fields": [
#         { "fieldPath": "userId", "order": "ASCENDING" },
#         { "fieldPath": "createdAt", "order": "DESCENDING" }
#       ]
#     },
#     {
#       "collectionGroup": "orders",
#       "queryScope": "COLLECTION_GROUP",
#       "fields": [
#         { "fieldPath": "status", "order": "ASCENDING" },
#         { "fieldPath": "updatedAt", "order": "DESCENDING" }
#       ]
#     }
#   ],
#   "fieldOverrides": [
#     {
#       "collectionGroup": "logs",
#       "fieldPath": "rawContent",
#       "indexes": []
#     }
#   ]
# }

# Deploy indexes to Firestore
firebase deploy --only firestore:indexes

# Deploy indexes to a specific database
firebase deploy --only firestore:indexes --project my-project
```

---

## Security Rules

```bash
# Deploy Firestore Security Rules (firestore.rules file)
firebase deploy --only firestore:rules

# Deploy rules to a named database
# In firebase.json, configure the database target:
# "firestore": [
#   {
#     "database": "(default)",
#     "rules": "firestore.rules",
#     "indexes": "firestore.indexes.json"
#   },
#   {
#     "database": "my-app-db",
#     "rules": "firestore-myapp.rules",
#     "indexes": "firestore-myapp.indexes.json"
#   }
# ]

firebase deploy --only firestore:rules --project my-project

# Get current rules (via gcloud)
gcloud alpha firestore databases documents get --database="(default)"
# Note: security rules are best managed via Firebase CLI and source control

# Test rules locally using Firebase Emulator
firebase emulators:start --only firestore
```

---

## TTL Policies

```bash
# Enable TTL on a field in a collection group
gcloud firestore fields ttls update expireAt \
  --collection-group=sessions \
  --enable-ttl \
  --database="(default)"

# Enable TTL on a named database
gcloud firestore fields ttls update expireAt \
  --collection-group=cache_entries \
  --enable-ttl \
  --database=my-app-db

# Disable TTL on a field
gcloud firestore fields ttls update expireAt \
  --collection-group=sessions \
  --disable-ttl \
  --database="(default)"

# List TTL configurations
gcloud firestore indexes fields list \
  --database="(default)" \
  --filter="indexConfig.ttl=true"
```

---

## Operations

```bash
# List recent operations (exports, imports, index builds)
gcloud firestore operations list --database="(default)"

# List operations for a named database
gcloud firestore operations list --database=my-app-db

# Describe a specific operation
gcloud firestore operations describe projects/MY_PROJECT/databases/(default)/operations/OPERATION_ID

# Cancel a running operation
gcloud firestore operations cancel projects/MY_PROJECT/databases/(default)/operations/OPERATION_ID
```

---

## Firestore Emulator (Local Development)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Start Firestore emulator only
firebase emulators:start --only firestore

# Start Firestore emulator on a specific port (default: 8080)
firebase emulators:start --only firestore --project my-project

# Export emulator data (save state between sessions)
firebase emulators:export ./emulator-data

# Start emulator with previously exported data
firebase emulators:start --only firestore --import=./emulator-data

# Connect application to emulator (Node.js example):
# process.env.FIRESTORE_EMULATOR_HOST = 'localhost:8080';
```

---

## BigQuery Integration

Firestore data can be exported to BigQuery for analytics.

```bash
# Export Firestore data to BigQuery via export + BigQuery load
# Step 1: Export to GCS
gcloud firestore export gs://my-bucket/export-for-bq/

# Step 2: Load into BigQuery using the Firestore export format
bq load \
  --source_format=DATASTORE_BACKUP \
  my_dataset.users_table \
  "gs://my-bucket/export-for-bq/all_namespaces/kind_users/all_namespaces_kind_users.export_metadata"

# Alternative: Use Firestore + BigQuery extension (Firebase Extensions)
# or use Datastream for continuous CDC to BigQuery
```

---

## Useful gcloud Flags

```bash
# Specify database (required for multi-database setups)
--database="(default)"
--database=my-app-db

# Specify project explicitly
--project=my-gcp-project

# Async flag (don't wait for operation)
--async

# Output format
--format=json
--format="table(name,state,createTime)"
```
