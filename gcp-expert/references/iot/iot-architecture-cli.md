# IoT Architecture on GCP — CLI Reference

## Pub/Sub for IoT Ingestion

### Create IoT topics and subscriptions

```bash
# Create topics for IoT data streams
gcloud pubsub topics create iot-telemetry \
  --project=my-iot-project

gcloud pubsub topics create iot-commands \
  --project=my-iot-project

gcloud pubsub topics create iot-alerts \
  --project=my-iot-project

gcloud pubsub topics create iot-device-lifecycle \
  --project=my-iot-project

gcloud pubsub topics create iot-dlq \
  --project=my-iot-project \
  --message-retention-duration=7d

# Create subscription with dead letter topic
gcloud pubsub subscriptions create iot-telemetry-bq-sub \
  --topic=iot-telemetry \
  --ack-deadline=60 \
  --dead-letter-topic=iot-dlq \
  --max-delivery-attempts=5 \
  --project=my-iot-project

# Create subscription with message ordering (per-device ordering)
gcloud pubsub subscriptions create iot-telemetry-ordered-sub \
  --topic=iot-telemetry \
  --enable-message-ordering \
  --ack-deadline=60 \
  --project=my-iot-project

# Create a filtered subscription (only receive alerts with level=critical)
gcloud pubsub subscriptions create iot-critical-alerts-sub \
  --topic=iot-alerts \
  --message-filter='attributes.alert_level = "critical"' \
  --ack-deadline=30 \
  --project=my-iot-project

# Create push subscription to deliver to Cloud Function endpoint
gcloud pubsub subscriptions create iot-telemetry-push-sub \
  --topic=iot-telemetry \
  --push-endpoint=https://us-central1-my-iot-project.cloudfunctions.net/processTelemetry \
  --ack-deadline=60 \
  --project=my-iot-project
```

### Attach schema validation to Pub/Sub topic

```bash
# Create Avro schema for telemetry messages
cat > telemetry-schema.avro <<'EOF'
{
  "type": "record",
  "name": "DeviceTelemetry",
  "fields": [
    {"name": "device_id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "temperature", "type": "float"},
    {"name": "humidity", "type": ["null", "float"], "default": null},
    {"name": "battery_level", "type": "int"}
  ]
}
EOF

# Create schema in Pub/Sub
gcloud pubsub schemas create telemetry-schema \
  --type=AVRO \
  --definition-file=telemetry-schema.avro \
  --project=my-iot-project

# Create topic with schema validation
gcloud pubsub topics create iot-telemetry-validated \
  --schema=telemetry-schema \
  --message-encoding=JSON \
  --project=my-iot-project

# List schemas
gcloud pubsub schemas list --project=my-iot-project

# Validate a message against a schema
gcloud pubsub schemas validate-message \
  --schema=telemetry-schema \
  --message-encoding=JSON \
  --message='{"device_id":"sensor-001","timestamp":1704067200,"temperature":22.5,"humidity":null,"battery_level":85}' \
  --project=my-iot-project
```

### Publish test messages

```bash
# Publish a single telemetry message
gcloud pubsub topics publish iot-telemetry \
  --message='{"device_id":"sensor-001","timestamp":1704067200,"temperature":22.5,"battery_level":85}' \
  --attribute=device_id=sensor-001,region=us-central,alert_level=normal \
  --project=my-iot-project

# Publish with ordering key (ensures ordered delivery per device)
gcloud pubsub topics publish iot-telemetry \
  --message='{"device_id":"sensor-001","seq":42,"temperature":23.1}' \
  --ordering-key=sensor-001 \
  --project=my-iot-project

# Pull and ack messages for testing
gcloud pubsub subscriptions pull iot-telemetry-bq-sub \
  --max-messages=10 \
  --auto-ack \
  --project=my-iot-project
```

---

## BigQuery for IoT Time-Series Analytics

```bash
# Create a dataset for IoT data
bq --location=US mk --dataset \
  --description="IoT time-series analytics" \
  my-iot-project:iot_analytics

# Create a partitioned, clustered table for device telemetry
bq mk --table \
  --schema='device_id:STRING,timestamp:TIMESTAMP,temperature:FLOAT,humidity:FLOAT,battery_level:INTEGER,region:STRING' \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=device_id,region \
  --description="Device telemetry time series" \
  my-iot-project:iot_analytics.device_telemetry

# Set partition expiration (keep 90 days of raw data)
bq update \
  --time_partitioning_expiration=7776000 \
  my-iot-project:iot_analytics.device_telemetry

# Query recent telemetry for a specific device (uses partition pruning)
bq query --use_legacy_sql=false \
  --project_id=my-iot-project \
'SELECT
  device_id,
  TIMESTAMP_TRUNC(timestamp, HOUR) AS hour,
  AVG(temperature) AS avg_temp,
  MIN(temperature) AS min_temp,
  MAX(temperature) AS max_temp,
  COUNT(*) AS reading_count
FROM `my-iot-project.iot_analytics.device_telemetry`
WHERE
  DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND device_id = "sensor-001"
GROUP BY device_id, hour
ORDER BY hour DESC
LIMIT 168'
```

---

## Bigtable for High-Throughput IoT Time-Series

```bash
# Create a Bigtable instance for IoT
gcloud bigtable instances create iot-timeseries \
  --display-name="IoT Time Series" \
  --cluster-config=id=iot-cluster,zone=us-central1-a,nodes=3 \
  --project=my-iot-project

# Create a table for device readings
cbt -project=my-iot-project -instance=iot-timeseries \
  createtable device_readings

# Create column families with garbage collection (keep 30 days)
cbt -project=my-iot-project -instance=iot-timeseries \
  createfamily device_readings metrics

cbt -project=my-iot-project -instance=iot-timeseries \
  setgcpolicy device_readings metrics maxage=30d

# Write a test reading (row key: devicetype#deviceid#reversed_timestamp)
# reversed_ts = 9999999999999 - epoch_milliseconds
cbt -project=my-iot-project -instance=iot-timeseries \
  set device_readings "sensor#sensor-001#9999998920000" \
  "metrics:temp=22.5" \
  "metrics:humidity=65.3" \
  "metrics:battery=85"

# Read the latest 10 readings for sensor-001
cbt -project=my-iot-project -instance=iot-timeseries \
  read device_readings \
  prefix="sensor#sensor-001#" \
  count=10
```

---

## Dataflow for IoT Streaming Pipeline

```bash
# Run Pub/Sub to BigQuery streaming pipeline (pre-built template)
gcloud dataflow jobs run iot-telemetry-to-bq \
  --gcs-location=gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery \
  --region=us-central1 \
  --staging-location=gs://my-iot-project-df-staging/temp \
  --parameters=\
inputTopic=projects/my-iot-project/topics/iot-telemetry,\
outputTableSpec=my-iot-project:iot_analytics.device_telemetry,\
outputDeadletterTable=my-iot-project:iot_analytics.device_telemetry_dlq \
  --project=my-iot-project

# Run Pub/Sub to Cloud Storage (for raw archiving)
gcloud dataflow jobs run iot-telemetry-archive \
  --gcs-location=gs://dataflow-templates-us-central1/latest/Cloud_PubSub_to_GCS_Text \
  --region=us-central1 \
  --staging-location=gs://my-iot-project-df-staging/temp \
  --parameters=\
inputTopic=projects/my-iot-project/topics/iot-telemetry,\
outputDirectory=gs://my-iot-archive/telemetry/,\
outputFilenamePrefix=telemetry-,\
outputFilenameSuffix=.json,\
windowDuration=1h \
  --project=my-iot-project

# List running Dataflow jobs
gcloud dataflow jobs list \
  --region=us-central1 \
  --filter="state=JOB_STATE_RUNNING" \
  --project=my-iot-project
```

---

## Cloud Functions for Device Event Processing

```bash
# Deploy a Cloud Function triggered by IoT alerts topic
cat > main.py << 'EOF'
import base64
import json
import os
from google.cloud import firestore

db = firestore.Client()

def process_alert(event, context):
    """Process IoT alert from Pub/Sub."""
    message = base64.b64decode(event['data']).decode('utf-8')
    alert = json.loads(message)

    device_id = alert.get('device_id')
    alert_type = alert.get('alert_type')
    value = alert.get('value')

    # Update device state in Firestore
    db.collection('devices').document(device_id).update({
        'last_alert': alert_type,
        'last_alert_value': value,
        'last_alert_time': firestore.SERVER_TIMESTAMP
    })

    print(f"Processed {alert_type} alert for device {device_id}: {value}")
EOF

cat > requirements.txt << 'EOF'
google-cloud-firestore==2.14.0
EOF

gcloud functions deploy process-iot-alert \
  --runtime=python311 \
  --region=us-central1 \
  --trigger-topic=iot-alerts \
  --entry-point=process_alert \
  --memory=256MB \
  --timeout=60s \
  --service-account=iot-function-sa@my-iot-project.iam.gserviceaccount.com \
  --project=my-iot-project

# View function logs
gcloud functions logs read process-iot-alert \
  --region=us-central1 \
  --limit=50 \
  --project=my-iot-project
```

---

## Firestore for Device Registry and Shadow Documents

```bash
# Create a Firestore database (if not already exists)
gcloud firestore databases create \
  --location=us-central1 \
  --project=my-iot-project

# Deploy Firestore security rules for device shadow access
cat > firestore.rules << 'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Devices collection: only service accounts can write
    match /devices/{deviceId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.iot_service == true;
    }
    // Device config: devices can read their own config
    match /device_configs/{deviceId} {
      allow read: if request.auth.uid == deviceId;
      allow write: if request.auth.token.admin == true;
    }
  }
}
EOF

firebase deploy --only firestore:rules --project=my-iot-project
```

---

## Migration Note: Cloud IoT Core Decommission

Cloud IoT Core was shut down on August 16, 2023. If encountering legacy references:

```bash
# These commands no longer work (Cloud IoT Core is shut down):
# gcloud iot registries create ...
# gcloud iot devices create ...
# gcloud iot registries credentials create ...

# Migration path:
# 1. Set up HiveMQ or EMQX on GKE as MQTT broker replacement
# 2. Implement device authentication via mTLS or custom JWT validation
# 3. Configure broker bridge to publish to Pub/Sub topics
# 4. Build device registry in Firestore (replaces Cloud IoT device registry)
# 5. Redirect devices to new MQTT broker endpoint

echo "Cloud IoT Core deprecated; use Pub/Sub + self-managed MQTT broker"
```
