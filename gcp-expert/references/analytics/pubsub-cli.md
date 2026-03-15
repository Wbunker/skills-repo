# Pub/Sub — CLI Reference

---

## Topics

```bash
# Create a topic
gcloud pubsub topics create my-topic \
  --project=my-project

# Create a topic with message retention (7 days)
gcloud pubsub topics create my-topic-retained \
  --message-retention-duration=7d \
  --project=my-project

# Create a topic with schema and encoding
gcloud pubsub topics create schematized-topic \
  --schema=my-event-schema \
  --message-encoding=JSON \
  --project=my-project

# Create a topic with CMEK
gcloud pubsub topics create encrypted-topic \
  --topic-encryption-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --project=my-project

# List topics
gcloud pubsub topics list --project=my-project

# Describe a topic
gcloud pubsub topics describe my-topic --project=my-project

# Update topic message retention
gcloud pubsub topics update my-topic \
  --message-retention-duration=3d \
  --project=my-project

# Delete a topic
gcloud pubsub topics delete my-topic --project=my-project

# Publish a single message to a topic
gcloud pubsub topics publish my-topic \
  --message="Hello, world!" \
  --project=my-project

# Publish a message with attributes
gcloud pubsub topics publish my-topic \
  --message='{"user_id": 123, "event": "click"}' \
  --attribute=type=click,source=web \
  --project=my-project

# Publish a message with an ordering key
gcloud pubsub topics publish my-topic \
  --message="ordered message" \
  --ordering-key="user-123" \
  --project=my-project

# Add IAM policy binding to a topic
gcloud pubsub topics add-iam-policy-binding my-topic \
  --member="serviceAccount:publisher-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher" \
  --project=my-project

# Get IAM policy for a topic
gcloud pubsub topics get-iam-policy my-topic --project=my-project

# List subscriptions for a topic
gcloud pubsub topics list-subscriptions my-topic --project=my-project
```

---

## Subscriptions

```bash
# Create a pull subscription
gcloud pubsub subscriptions create my-pull-sub \
  --topic=my-topic \
  --project=my-project

# Create pull subscription with custom ack deadline and retention
gcloud pubsub subscriptions create my-pull-sub-custom \
  --topic=my-topic \
  --ack-deadline=60 \
  --message-retention-duration=2d \
  --retain-acked-messages \
  --project=my-project

# Create pull subscription with message ordering
gcloud pubsub subscriptions create ordered-sub \
  --topic=my-topic \
  --enable-message-ordering \
  --project=my-project

# Create pull subscription with dead letter topic
gcloud pubsub subscriptions create my-sub-with-dlq \
  --topic=my-topic \
  --dead-letter-topic=projects/my-project/topics/my-dead-letter-topic \
  --max-delivery-attempts=10 \
  --project=my-project

# Create pull subscription with server-side filter
gcloud pubsub subscriptions create filtered-sub \
  --topic=my-topic \
  --message-filter='attributes.type = "order"' \
  --project=my-project

# Create push subscription to Cloud Run endpoint with OIDC auth
gcloud pubsub subscriptions create my-push-sub \
  --topic=my-topic \
  --push-endpoint=https://my-service-abc123-uc.a.run.app/pubsub \
  --push-auth-service-account=pubsub-invoker@my-project.iam.gserviceaccount.com \
  --ack-deadline=30 \
  --project=my-project

# Create BigQuery subscription (streams messages directly to BQ table)
gcloud pubsub subscriptions create my-bq-sub \
  --topic=my-topic \
  --bigquery-table=my-project:my_dataset.events \
  --write-metadata \
  --project=my-project

# Create Cloud Storage subscription
gcloud pubsub subscriptions create my-gcs-sub \
  --topic=my-topic \
  --cloud-storage-bucket=my-archive-bucket \
  --cloud-storage-file-prefix=pubsub/events \
  --cloud-storage-file-suffix=.json \
  --cloud-storage-max-duration=5m \
  --cloud-storage-max-bytes=100000000 \
  --project=my-project

# List subscriptions
gcloud pubsub subscriptions list --project=my-project

# Describe a subscription
gcloud pubsub subscriptions describe my-pull-sub --project=my-project

# Update subscription ack deadline
gcloud pubsub subscriptions update my-pull-sub \
  --ack-deadline=120 \
  --project=my-project

# Update push endpoint
gcloud pubsub subscriptions update my-push-sub \
  --push-endpoint=https://new-service-abc123-uc.a.run.app/pubsub \
  --project=my-project

# Delete a subscription
gcloud pubsub subscriptions delete my-pull-sub --project=my-project

# Pull messages from a subscription (synchronous pull)
gcloud pubsub subscriptions pull my-pull-sub \
  --auto-ack \
  --limit=10 \
  --project=my-project

# Pull without auto-ack (get ackId for manual ack)
gcloud pubsub subscriptions pull my-pull-sub \
  --limit=5 \
  --format=json \
  --project=my-project

# Acknowledge a message by ackId
gcloud pubsub subscriptions ack my-pull-sub \
  --ack-ids=ACK_ID_1,ACK_ID_2 \
  --project=my-project

# Modify ack deadline (extend processing time)
gcloud pubsub subscriptions modify-ack-deadline my-pull-sub \
  --ack-ids=ACK_ID_1 \
  --ack-deadline=300 \
  --project=my-project

# Add IAM binding to subscription
gcloud pubsub subscriptions add-iam-policy-binding my-pull-sub \
  --member="serviceAccount:subscriber-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber" \
  --project=my-project

# Seek to a timestamp (replay from a point in time)
gcloud pubsub subscriptions seek my-pull-sub \
  --time="2024-01-01T00:00:00Z" \
  --project=my-project

# Seek to a snapshot
gcloud pubsub subscriptions seek my-pull-sub \
  --snapshot=my-snapshot \
  --project=my-project
```

---

## Schemas

```bash
# Create an Avro schema (provide schema definition inline or from file)
gcloud pubsub schemas create my-event-schema \
  --type=AVRO \
  --definition='{
    "type": "record",
    "name": "Event",
    "fields": [
      {"name": "user_id", "type": "int"},
      {"name": "event_type", "type": "string"},
      {"name": "timestamp", "type": "long"}
    ]
  }' \
  --project=my-project

# Create schema from file
gcloud pubsub schemas create my-event-schema \
  --type=AVRO \
  --definition-file=event-schema.avsc \
  --project=my-project

# Create a Protocol Buffer schema
gcloud pubsub schemas create proto-schema \
  --type=PROTOCOL_BUFFER \
  --definition-file=event.proto \
  --project=my-project

# List schemas
gcloud pubsub schemas list --project=my-project

# Describe a schema
gcloud pubsub schemas describe my-event-schema --project=my-project

# List all revisions of a schema
gcloud pubsub schemas list-revisions my-event-schema --project=my-project

# Commit a new revision to an existing schema
gcloud pubsub schemas commit my-event-schema \
  --type=AVRO \
  --definition-file=event-schema-v2.avsc \
  --project=my-project

# Validate a message against a schema
gcloud pubsub schemas validate-message \
  --schema=my-event-schema \
  --message-encoding=JSON \
  --message='{"user_id": 123, "event_type": "purchase", "timestamp": 1704067200}' \
  --project=my-project

# Delete a schema
gcloud pubsub schemas delete my-event-schema --project=my-project
```

---

## Snapshots

```bash
# Create a snapshot of a subscription state
gcloud pubsub snapshots create my-snapshot \
  --subscription=my-pull-sub \
  --project=my-project

# List snapshots
gcloud pubsub snapshots list --project=my-project

# Describe a snapshot
gcloud pubsub snapshots describe my-snapshot --project=my-project

# Delete a snapshot
gcloud pubsub snapshots delete my-snapshot --project=my-project

# Use snapshot to replay: seek subscription back to snapshot
gcloud pubsub subscriptions seek my-pull-sub \
  --snapshot=my-snapshot \
  --project=my-project
```

---

## Pub/Sub Lite

```bash
# Create a Pub/Sub Lite topic (zonal)
gcloud pubsub lite-topics create my-lite-topic \
  --location=us-central1-a \
  --partitions=4 \
  --per-partition-publish-mib=4 \
  --per-partition-subscribe-mib=8 \
  --per-partition-storage-mib=30720 \
  --project=my-project

# Create a Pub/Sub Lite topic (regional)
gcloud pubsub lite-topics create my-regional-lite-topic \
  --location=us-central1 \
  --partitions=8 \
  --per-partition-publish-mib=4 \
  --per-partition-subscribe-mib=8 \
  --per-partition-storage-mib=30720 \
  --project=my-project

# List Lite topics
gcloud pubsub lite-topics list \
  --location=us-central1-a \
  --project=my-project

# Create a Lite subscription
gcloud pubsub lite-subscriptions create my-lite-sub \
  --location=us-central1-a \
  --topic=my-lite-topic \
  --delivery-requirement=DELIVER_IMMEDIATELY \
  --project=my-project

# List Lite subscriptions
gcloud pubsub lite-subscriptions list \
  --location=us-central1-a \
  --project=my-project

# Subscribe and receive messages from Lite topic
gcloud pubsub lite-subscriptions subscribe my-lite-sub \
  --location=us-central1-a \
  --num-messages=10 \
  --project=my-project
```

---

## Dead Letter Topic Setup Example

```bash
# Step 1: Create the dead letter topic
gcloud pubsub topics create my-dead-letter-topic --project=my-project

# Step 2: Create the main subscription with dead letter config
gcloud pubsub subscriptions create my-sub \
  --topic=my-main-topic \
  --dead-letter-topic=projects/my-project/topics/my-dead-letter-topic \
  --max-delivery-attempts=5 \
  --project=my-project

# Step 3: Grant Pub/Sub service account permissions
# (Pub/Sub needs to publish to DLT and ack from main subscription)
PROJECT_NUMBER=$(gcloud projects describe my-project --format='value(projectNumber)')
PUBSUB_SA="service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"

gcloud pubsub topics add-iam-policy-binding my-dead-letter-topic \
  --member="serviceAccount:${PUBSUB_SA}" \
  --role="roles/pubsub.publisher" \
  --project=my-project

gcloud pubsub subscriptions add-iam-policy-binding my-sub \
  --member="serviceAccount:${PUBSUB_SA}" \
  --role="roles/pubsub.subscriber" \
  --project=my-project

# Step 4: Create a subscription on the DLT to inspect failed messages
gcloud pubsub subscriptions create my-dlq-sub \
  --topic=my-dead-letter-topic \
  --project=my-project
```

---

## IAM Roles for Pub/Sub

```bash
# Common IAM bindings:

# Publisher: can publish to a topic
gcloud pubsub topics add-iam-policy-binding my-topic \
  --member="serviceAccount:publisher-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Subscriber: can consume from a subscription
gcloud pubsub subscriptions add-iam-policy-binding my-sub \
  --member="serviceAccount:subscriber-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

# Key IAM roles:
# roles/pubsub.admin       - full control
# roles/pubsub.editor      - create/delete topics and subscriptions
# roles/pubsub.publisher   - publish messages to topics
# roles/pubsub.subscriber  - consume messages from subscriptions
# roles/pubsub.viewer      - read metadata only
```
