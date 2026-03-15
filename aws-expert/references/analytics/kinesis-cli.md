# AWS Kinesis — CLI Reference
For service concepts, see [kinesis-capabilities.md](kinesis-capabilities.md).

## Amazon Kinesis Data Streams

```bash
# --- Stream management ---
aws kinesis create-stream --stream-name my-stream --shard-count 4
aws kinesis create-stream --stream-name auto-stream --stream-mode-details StreamMode=ON_DEMAND

aws kinesis describe-stream --stream-name my-stream
aws kinesis describe-stream-summary --stream-name my-stream
aws kinesis list-streams

aws kinesis update-stream-mode \
  --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
  --stream-mode-details StreamMode=ON_DEMAND

aws kinesis delete-stream --stream-name my-stream

# --- Shard management ---
aws kinesis list-shards --stream-name my-stream

aws kinesis split-shard \
  --stream-name my-stream \
  --shard-to-split shardId-000000000003 \
  --new-starting-hash-key 170141183460469231731687303715884105728

aws kinesis merge-shards \
  --stream-name my-stream \
  --shard-to-merge shardId-000000000000 \
  --adjacent-shard-to-merge shardId-000000000001

aws kinesis update-shard-count \
  --stream-name my-stream \
  --target-shard-count 8 \
  --scaling-type UNIFORM_SCALING

# --- Produce records ---
aws kinesis put-record \
  --stream-name my-stream \
  --partition-key user-123 \
  --data '{"event": "click", "user_id": "123"}' \
  --cli-binary-format raw-in-base64-out

aws kinesis put-records \
  --stream-name my-stream \
  --records '[
    {"Data": "{\"event\": \"view\"}", "PartitionKey": "user-123"},
    {"Data": "{\"event\": \"click\"}", "PartitionKey": "user-456"}
  ]' \
  --cli-binary-format raw-in-base64-out

# --- Consume records ---
aws kinesis get-shard-iterator \
  --stream-name my-stream \
  --shard-id shardId-000000000000 \
  --shard-iterator-type TRIM_HORIZON

aws kinesis get-records \
  --shard-iterator AAAAAAAA... \
  --limit 100

# LATEST: only new records after iterator creation
aws kinesis get-shard-iterator \
  --stream-name my-stream \
  --shard-id shardId-000000000000 \
  --shard-iterator-type LATEST

# AT_TIMESTAMP: start from a specific time
aws kinesis get-shard-iterator \
  --stream-name my-stream \
  --shard-id shardId-000000000000 \
  --shard-iterator-type AT_TIMESTAMP \
  --timestamp 2024-01-01T00:00:00Z

# --- Enhanced Fan-Out (registered consumers) ---
aws kinesis register-stream-consumer \
  --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
  --consumer-name my-consumer

aws kinesis describe-stream-consumer \
  --consumer-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream/consumer/my-consumer:...

aws kinesis list-stream-consumers \
  --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream

# Subscribe (HTTP/2 push; typically used by SDK, not CLI)
aws kinesis subscribe-to-shard \
  --consumer-arn arn:aws:kinesis:...consumer... \
  --shard-id shardId-000000000000 \
  --starting-position ShardIteratorType=TRIM_HORIZON

aws kinesis deregister-stream-consumer \
  --consumer-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream/consumer/my-consumer:...

# --- Retention ---
aws kinesis increase-stream-retention-period \
  --stream-name my-stream \
  --retention-period-hours 168   # 7 days

aws kinesis decrease-stream-retention-period \
  --stream-name my-stream \
  --retention-period-hours 24

# --- Monitoring and tagging ---
aws kinesis enable-enhanced-monitoring \
  --stream-name my-stream \
  --shard-level-metrics IncomingBytes IncomingRecords OutgoingBytes ReadProvisionedThroughputExceeded

aws kinesis disable-enhanced-monitoring \
  --stream-name my-stream \
  --shard-level-metrics ALL

aws kinesis add-tags-to-stream \
  --stream-name my-stream \
  --tags Environment=prod Team=data
```

---

## Amazon Data Firehose

```bash
# --- Create delivery stream ---

# S3 destination
aws firehose create-delivery-stream \
  --delivery-stream-name my-s3-stream \
  --delivery-stream-type DirectPut \
  --s3-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "BucketARN": "arn:aws:s3:::my-bucket",
    "Prefix": "data/year=!{timestamp:yyyy}/month=!{timestamp:MM}/",
    "ErrorOutputPrefix": "errors/",
    "BufferingHints": {"SizeInMBs": 128, "IntervalInSeconds": 300},
    "CompressionFormat": "GZIP"
  }'

# Redshift destination (stages to S3 first)
aws firehose create-delivery-stream \
  --delivery-stream-name my-redshift-stream \
  --delivery-stream-type DirectPut \
  --redshift-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "ClusterJDBCURL": "jdbc:redshift://my-cluster.abc.us-east-1.redshift.amazonaws.com:5439/dev",
    "CopyCommand": {"DataTableName": "orders", "CopyOptions": "JSON AS AUTO"},
    "Username": "admin",
    "Password": "P@ssw0rd!",
    "S3Configuration": {
      "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
      "BucketARN": "arn:aws:s3:::my-staging-bucket",
      "BufferingHints": {"SizeInMBs": 10, "IntervalInSeconds": 60}
    }
  }'

# OpenSearch destination
aws firehose create-delivery-stream \
  --delivery-stream-name my-opensearch-stream \
  --delivery-stream-type DirectPut \
  --amazon-open-search-service-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "DomainARN": "arn:aws:es:us-east-1:123456789012:domain/my-domain",
    "IndexName": "application-logs",
    "IndexRotationPeriod": "OneDay",
    "BufferingHints": {"IntervalInSeconds": 60, "SizeInMBs": 5},
    "S3BackupMode": "AllDocuments",
    "S3Configuration": {
      "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
      "BucketARN": "arn:aws:s3:::my-backup-bucket"
    }
  }'

# From Kinesis Data Streams source
aws firehose create-delivery-stream \
  --delivery-stream-name kds-to-s3 \
  --delivery-stream-type KinesisStreamAsSource \
  --kinesis-stream-source-configuration '{
    "KinesisStreamARN": "arn:aws:kinesis:us-east-1:123456789012:stream/my-stream",
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole"
  }' \
  --s3-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "BucketARN": "arn:aws:s3:::my-bucket"
  }'

# --- Stream operations ---
aws firehose list-delivery-streams
aws firehose describe-delivery-stream --delivery-stream-name my-s3-stream

# --- Send records ---
aws firehose put-record \
  --delivery-stream-name my-s3-stream \
  --record '{"Data": "{\"key\": \"value\"}"}' \
  --cli-binary-format raw-in-base64-out

aws firehose put-record-batch \
  --delivery-stream-name my-s3-stream \
  --records '[
    {"Data": "{\"event\": \"view\"}"},
    {"Data": "{\"event\": \"click\"}"}
  ]' \
  --cli-binary-format raw-in-base64-out

# --- Update destination ---
aws firehose update-destination \
  --delivery-stream-name my-s3-stream \
  --current-delivery-stream-version-id 1 \
  --destination-id destinationId-000000000001 \
  --s3-destination-update '{
    "BufferingHints": {"SizeInMBs": 64, "IntervalInSeconds": 120}
  }'

# --- Tagging ---
aws firehose tag-delivery-stream \
  --delivery-stream-name my-s3-stream \
  --tags Key=Environment,Value=prod Key=Team,Value=data

aws firehose delete-delivery-stream --delivery-stream-name my-s3-stream
```

---

## Amazon Kinesis Video Streams

```bash
# --- Stream management ---
aws kinesisvideo create-stream \
  --stream-name my-camera-stream \
  --data-retention-in-hours 24 \
  --media-type video/h264

aws kinesisvideo describe-stream --stream-name my-camera-stream
aws kinesisvideo list-streams
aws kinesisvideo list-streams \
  --stream-name-condition '{"ComparisonOperator": "BEGINS_WITH", "ComparisonValue": "camera-"}'

aws kinesisvideo update-stream \
  --stream-arn arn:aws:kinesisvideo:us-east-1:123456789012:stream/my-camera-stream/1234567890 \
  --media-type video/h264

aws kinesisvideo update-data-retention \
  --stream-name my-camera-stream \
  --current-version 1 \
  --operation INCREASE_DATA_RETENTION \
  --data-retention-change-in-hours 48

aws kinesisvideo delete-stream \
  --stream-arn arn:aws:kinesisvideo:us-east-1:123456789012:stream/my-camera-stream/1234567890

# --- Get data endpoint (required before PutMedia/GetMedia) ---
aws kinesisvideo get-data-endpoint \
  --stream-name my-camera-stream \
  --api-name PUT_MEDIA

aws kinesisvideo get-data-endpoint \
  --stream-name my-camera-stream \
  --api-name GET_HLS_STREAMING_SESSION_URL

# --- HLS playback URL (via kinesis-video-archived-media sub-service) ---
# Note: use the endpoint returned by get-data-endpoint with --endpoint-url
aws kinesis-video-archived-media get-hls-streaming-session-url \
  --endpoint-url https://b-1234abcd.kinesisvideo.us-east-1.amazonaws.com \
  --stream-name my-camera-stream \
  --playback-mode LIVE \
  --hls-fragment-selector '{
    "FragmentSelectorType": "SERVER_TIMESTAMP",
    "TimestampRange": {}
  }'

# On-demand (archived) HLS playback
aws kinesis-video-archived-media get-hls-streaming-session-url \
  --endpoint-url https://b-1234abcd.kinesisvideo.us-east-1.amazonaws.com \
  --stream-name my-camera-stream \
  --playback-mode ON_DEMAND \
  --hls-fragment-selector '{
    "FragmentSelectorType": "SERVER_TIMESTAMP",
    "TimestampRange": {
      "StartTimestamp": 1700000000,
      "EndTimestamp": 1700003600
    }
  }'

# DASH playback URL
aws kinesis-video-archived-media get-dash-streaming-session-url \
  --endpoint-url https://b-1234abcd.kinesisvideo.us-east-1.amazonaws.com \
  --stream-name my-camera-stream \
  --playback-mode LIVE

# Get a clip (MP4 download)
aws kinesis-video-archived-media get-clip \
  --endpoint-url https://b-1234abcd.kinesisvideo.us-east-1.amazonaws.com \
  --stream-name my-camera-stream \
  --clip-fragment-selector '{
    "FragmentSelectorType": "SERVER_TIMESTAMP",
    "TimestampRange": {
      "StartTimestamp": 1700000000,
      "EndTimestamp": 1700000300
    }
  }' \
  output-clip.mp4

# List fragments
aws kinesis-video-archived-media list-fragments \
  --endpoint-url https://b-1234abcd.kinesisvideo.us-east-1.amazonaws.com \
  --stream-name my-camera-stream \
  --fragment-selector '{
    "FragmentSelectorType": "SERVER_TIMESTAMP",
    "TimestampRange": {
      "StartTimestamp": 1700000000,
      "EndTimestamp": 1700003600
    }
  }'

# --- WebRTC: Signaling channels ---
aws kinesisvideo create-signaling-channel \
  --channel-name my-doorbell-channel \
  --channel-type SINGLE_MASTER

aws kinesisvideo describe-signaling-channel --channel-name my-doorbell-channel
aws kinesisvideo list-signaling-channels

aws kinesisvideo get-signaling-channel-endpoint \
  --channel-arn arn:aws:kinesisvideo:us-east-1:123456789012:channel/my-doorbell-channel/1234567890 \
  --single-master-channel-endpoint-configuration '{
    "Protocols": ["WSS", "HTTPS"],
    "Role": "MASTER"
  }'

aws kinesisvideo delete-signaling-channel \
  --channel-arn arn:aws:kinesisvideo:us-east-1:123456789012:channel/my-doorbell-channel/1234567890

# --- Image generation configuration ---
aws kinesisvideo update-image-generation-configuration \
  --stream-name my-camera-stream \
  --image-generation-configuration '{
    "Status": "ENABLED",
    "ImageSelectorType": "SERVER_TIMESTAMP",
    "DestinationConfig": {
      "Uri": "s3://my-bucket/frames/",
      "DestinationRegion": "us-east-1"
    },
    "SamplingInterval": 3000,
    "Format": "JPEG",
    "FormatConfig": {"JPEGQuality": "80"},
    "WidthPixels": 320,
    "HeightPixels": 240
  }'

# --- Tagging ---
aws kinesisvideo tag-stream \
  --stream-arn arn:aws:kinesisvideo:us-east-1:123456789012:stream/my-camera-stream/1234567890 \
  --tags Environment=prod Location=building-a

aws kinesisvideo list-tags-for-stream \
  --stream-arn arn:aws:kinesisvideo:us-east-1:123456789012:stream/my-camera-stream/1234567890
```
