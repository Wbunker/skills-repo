# AWS Elemental Delivery — CLI Reference

For service concepts, see [elemental-delivery-capabilities.md](elemental-delivery-capabilities.md).

---

## aws mediapackagev2

### Channel Groups

```bash
# List channel groups
aws mediapackagev2 list-channel-groups

# Get a channel group
aws mediapackagev2 get-channel-group --channel-group-name my-group

# Create a channel group
aws mediapackagev2 create-channel-group \
  --channel-group-name my-group \
  --description "Production OTT channel group"

# Update a channel group description
aws mediapackagev2 update-channel-group \
  --channel-group-name my-group \
  --description "Updated description"

# Delete a channel group (all channels and endpoints must be deleted first)
aws mediapackagev2 delete-channel-group --channel-group-name my-group
```

### Channels

```bash
# List channels in a channel group
aws mediapackagev2 list-channels --channel-group-name my-group

# Get a channel
aws mediapackagev2 get-channel \
  --channel-group-name my-group \
  --channel-name my-channel

# Create a channel
aws mediapackagev2 create-channel \
  --channel-group-name my-group \
  --channel-name my-channel \
  --input-type HLS

# Get ingest endpoints for a channel (use these URLs in MediaLive output groups)
aws mediapackagev2 get-channel \
  --channel-group-name my-group \
  --channel-name my-channel \
  --query 'IngestEndpoints'

# Delete a channel
aws mediapackagev2 delete-channel \
  --channel-group-name my-group \
  --channel-name my-channel
```

### Origin Endpoints

```bash
# List origin endpoints for a channel
aws mediapackagev2 list-origin-endpoints \
  --channel-group-name my-group \
  --channel-name my-channel

# Get an origin endpoint
aws mediapackagev2 get-origin-endpoint \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name hls-endpoint

# Create an HLS origin endpoint
aws mediapackagev2 create-origin-endpoint \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name hls-endpoint \
  --container-type TS \
  --hls-manifests '[{"ManifestName":"index","ManifestWindowSeconds":30}]' \
  --segment '{
    "SegmentDurationSeconds": 6,
    "SegmentName": "segment",
    "TsUseAudioRenditionGroup": true
  }'

# Create a CMAF origin endpoint with DRM (SPEKE)
aws mediapackagev2 create-origin-endpoint \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name cmaf-drm-endpoint \
  --container-type CMAF \
  --hls-manifests '[{"ManifestName":"hls/index"}]' \
  --dash-manifests '[{"ManifestName":"dash/index","ManifestWindowSeconds":60}]' \
  --segment '{
    "SegmentDurationSeconds": 6,
    "Encryption": {
      "SpekeKeyProvider": {
        "ResourceId": "my-resource-id",
        "SystemIds": [
          "94ce86fb-07ff-4f43-adb8-93d2fa968ca2",
          "edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"
        ],
        "Url": "https://speke.example.com/v2/keydelivery",
        "RoleArn": "arn:aws:iam::123456789012:role/MediaPackageSpekeRole",
        "EncryptionMethod": {
          "CmafEncryptionMethod": "CBCS"
        }
      }
    }
  }'

# Update an origin endpoint (e.g., change manifest window)
aws mediapackagev2 update-origin-endpoint \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name hls-endpoint \
  --hls-manifests '[{"ManifestName":"index","ManifestWindowSeconds":60}]'

# Delete an origin endpoint
aws mediapackagev2 delete-origin-endpoint \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name hls-endpoint
```

### Harvest Jobs

```bash
# List harvest jobs for a channel
aws mediapackagev2 list-harvest-jobs \
  --channel-group-name my-group \
  --channel-name my-channel

# Get a harvest job
aws mediapackagev2 get-harvest-job \
  --channel-group-name my-group \
  --channel-name my-channel \
  --harvest-job-name my-clip

# Create a harvest job (clip a window from live archive to S3)
aws mediapackagev2 create-harvest-job \
  --channel-group-name my-group \
  --channel-name my-channel \
  --origin-endpoint-name hls-endpoint \
  --harvest-job-name my-clip \
  --harvested-manifests '{
    "Items": [{"ManifestKey": "index.m3u8"}]
  }' \
  --schedule-configuration '{
    "StartTime": "2026-03-14T18:00:00Z",
    "EndTime": "2026-03-14T19:00:00Z"
  }' \
  --destination '{
    "S3Destination": {
      "BucketName": "my-vod-bucket",
      "DestinationPath": "clips/game1/"
    }
  }' \
  --description "First half highlights"

# Cancel a harvest job
aws mediapackagev2 cancel-harvest-job \
  --channel-group-name my-group \
  --channel-name my-channel \
  --harvest-job-name my-clip
```

### Tags

```bash
# List tags on a MediaPackage v2 resource
aws mediapackagev2 list-tags-for-resource --resource-arn <arn>

# Tag a resource
aws mediapackagev2 tag-resource \
  --resource-arn <arn> \
  --tags '{"Env":"prod","Team":"streaming"}'

# Untag a resource
aws mediapackagev2 untag-resource \
  --resource-arn <arn> \
  --tag-keys Env Team
```

---

## aws mediastore

### Containers

```bash
# List containers
aws mediastore list-containers

# Describe a container
aws mediastore describe-container --container-name my-container

# Create a container
aws mediastore create-container --container-name my-container

# Delete a container (must be empty)
aws mediastore delete-container --container-name my-container
```

### Container Policies

```bash
# Get the access policy for a container
aws mediastore get-container-policy --container-name my-container

# Put (replace) a container access policy
aws mediastore put-container-policy \
  --container-name my-container \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AllowCloudFrontRead",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity EXAMPLEID"
        },
        "Action": [
          "mediastore:GetObject",
          "mediastore:DescribeObject"
        ],
        "Resource": "arn:aws:mediastore:us-east-1:123456789012:container/my-container/*",
        "Condition": {
          "Bool": {"aws:SecureTransport": "true"}
        }
      }
    ]
  }'

# Delete a container policy
aws mediastore delete-container-policy --container-name my-container
```

### CORS Policy

```bash
# Get CORS policy
aws mediastore get-cors-policy --container-name my-container

# Put a CORS policy (allow browser-based HLS playback)
aws mediastore put-cors-policy \
  --container-name my-container \
  --cors-policy '[
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET","HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]'

# Delete CORS policy
aws mediastore delete-cors-policy --container-name my-container
```

### Lifecycle Policy

```bash
# Get lifecycle policy
aws mediastore get-lifecycle-policy --container-name my-container

# Put a lifecycle policy (delete objects older than 1 hour)
aws mediastore put-lifecycle-policy \
  --container-name my-container \
  --lifecycle-policy '{
    "rules": [
      {
        "definition": {
          "path": [{"wildcard": "live/*"}],
          "days_since_create": [{"numeric": [">" ,0]}],
          "seconds_since_create": [{"numeric": ["<=", 3600]}]
        },
        "action": "EXPIRE"
      }
    ]
  }'

# Delete lifecycle policy
aws mediastore delete-lifecycle-policy --container-name my-container
```

### Metric Policy

```bash
# Get metric policy (controls which CloudWatch metrics are published)
aws mediastore get-metric-policy --container-name my-container

# Put a metric policy
aws mediastore put-metric-policy \
  --container-name my-container \
  --metric-policy '{
    "ContainerLevelMetrics": "ENABLED",
    "MetricPolicyRules": [
      {
        "ObjectGroup": "live/",
        "ObjectGroupName": "live-segments"
      }
    ]
  }'

# Delete metric policy
aws mediastore delete-metric-policy --container-name my-container
```

## aws mediastore-data

```bash
# Upload (PUT) an object to a container
aws mediastore-data put-object \
  --endpoint https://my-container.data.mediastore.us-east-1.amazonaws.com \
  --path live/segment001.ts \
  --body ./segment001.ts \
  --content-type "video/MP2T"

# Download (GET) an object
aws mediastore-data get-object \
  --endpoint https://my-container.data.mediastore.us-east-1.amazonaws.com \
  --path live/segment001.ts \
  ./downloaded-segment001.ts

# Describe (HEAD) an object
aws mediastore-data describe-object \
  --endpoint https://my-container.data.mediastore.us-east-1.amazonaws.com \
  --path live/segment001.ts

# List items in a container (path prefix optional)
aws mediastore-data list-items \
  --endpoint https://my-container.data.mediastore.us-east-1.amazonaws.com \
  --path live/

# Delete an object
aws mediastore-data delete-object \
  --endpoint https://my-container.data.mediastore.us-east-1.amazonaws.com \
  --path live/segment001.ts
```

---

## aws mediaconnect

### Flows

```bash
# List flows
aws mediaconnect list-flows

# Describe a flow
aws mediaconnect describe-flow --flow-arn arn:aws:mediaconnect:us-east-1:123456789012:flow:my-flow

# Create a flow with an SRT listener source
aws mediaconnect create-flow \
  --name my-flow \
  --source '{
    "Name": "srt-source",
    "Protocol": "srt-listener",
    "IngestPort": 5000,
    "MaxBitrate": 80000000,
    "Description": "SRT contribution feed"
  }' \
  --availability-zone us-east-1a

# Create a flow with a Zixi push source
aws mediaconnect create-flow \
  --name my-zixi-flow \
  --source '{
    "Name": "zixi-push-source",
    "Protocol": "zixi-push",
    "IngestPort": 2088,
    "StreamId": "my-stream-id",
    "MaxBitrate": 50000000
  }' \
  --availability-zone us-east-1a

# Start a flow
aws mediaconnect start-flow --flow-arn <flow-arn>

# Stop a flow
aws mediaconnect stop-flow --flow-arn <flow-arn>

# Update flow source
aws mediaconnect update-flow-source \
  --flow-arn <flow-arn> \
  --source-arn <source-arn> \
  --max-bitrate 100000000

# Delete a flow (must be stopped)
aws mediaconnect delete-flow --flow-arn <flow-arn>
```

### Outputs

```bash
# Add an output to a flow (SRT caller to a downstream system)
aws mediaconnect add-flow-outputs \
  --flow-arn <flow-arn> \
  --outputs '[
    {
      "Name": "downstream-encoder",
      "Protocol": "srt-caller",
      "RemoteId": "10.0.1.50",
      "Port": 5000,
      "MaxLatency": 100,
      "Description": "Output to on-prem encoder"
    }
  ]'

# Add a MediaLive-compatible RTP output
aws mediaconnect add-flow-outputs \
  --flow-arn <flow-arn> \
  --outputs '[
    {
      "Name": "medialive-output",
      "Protocol": "rtp-fec",
      "Destination": "10.0.2.100",
      "Port": 5000,
      "SmoothingLatency": 100
    }
  ]'

# Update an output
aws mediaconnect update-flow-output \
  --flow-arn <flow-arn> \
  --output-arn <output-arn> \
  --max-latency 200

# Remove an output
aws mediaconnect remove-flow-output \
  --flow-arn <flow-arn> \
  --output-arn <output-arn>
```

### Entitlements

```bash
# List entitlements on a flow
aws mediaconnect describe-flow \
  --flow-arn <flow-arn> \
  --query 'Flow.Entitlements'

# Grant an entitlement to another AWS account
aws mediaconnect grant-flow-entitlements \
  --flow-arn <flow-arn> \
  --entitlements '[
    {
      "Name": "partner-entitlement",
      "Subscribers": ["123456789013"],
      "Description": "Affiliate distribution feed",
      "DataTransferSubscriberFeePercent": 0
    }
  ]'

# Update an entitlement (e.g., change subscribers)
aws mediaconnect update-flow-entitlement \
  --flow-arn <flow-arn> \
  --entitlement-arn <entitlement-arn> \
  --subscribers '["123456789013","123456789014"]'

# Revoke an entitlement
aws mediaconnect revoke-flow-entitlement \
  --flow-arn <flow-arn> \
  --entitlement-arn <entitlement-arn>
```

### Bridges & Gateways

```bash
# List bridges
aws mediaconnect list-bridges

# Describe a bridge
aws mediaconnect describe-bridge --bridge-arn <bridge-arn>

# List gateways
aws mediaconnect list-gateways

# Describe a gateway
aws mediaconnect describe-gateway --gateway-arn <gateway-arn>

# List gateway instances (on-prem appliances registered to a gateway)
aws mediaconnect list-gateway-instances \
  --filter-arn <gateway-arn>

# Describe a gateway instance
aws mediaconnect describe-gateway-instance \
  --gateway-instance-arn <instance-arn>
```

### Tags

```bash
# List tags on a MediaConnect resource
aws mediaconnect list-tags-for-resource --resource-arn <arn>

# Add tags
aws mediaconnect tag-resource \
  --resource-arn <arn> \
  --tags '{"Env":"prod"}'

# Remove tags
aws mediaconnect untag-resource \
  --resource-arn <arn> \
  --tag-keys Env
```

---

## aws mediatailor

### Playback Configurations

```bash
# List playback configurations
aws mediatailor list-playback-configurations

# Get a playback configuration
aws mediatailor get-playback-configuration --name my-config

# Create a playback configuration (SSAI)
aws mediatailor put-playback-configuration \
  --name my-ssai-config \
  --video-content-source-url https://my-mediapackage-endpoint.example.com/out/v1/channel/index.m3u8 \
  --ad-decision-server-url "https://ads.example.com/vast?correlator=[session.id]&ua=[player_params.UserAgent]&ip=[session.client_ip]" \
  --slate-ad-url https://s3.amazonaws.com/my-bucket/slate.mp4 \
  --cdn-configuration '{
    "AdSegmentUrlPrefix": "https://d123.cloudfront.net",
    "ContentSegmentUrlPrefix": "https://d456.cloudfront.net"
  }'

# Update a playback configuration (put-playback-configuration is idempotent)
aws mediatailor put-playback-configuration \
  --name my-ssai-config \
  --video-content-source-url https://new-origin.example.com/index.m3u8 \
  --ad-decision-server-url "https://ads.example.com/vast?id=[session.id]"

# Delete a playback configuration
aws mediatailor delete-playback-configuration --name my-ssai-config
```

### Prefetch Schedules

```bash
# List prefetch schedules for a playback configuration
aws mediatailor list-prefetch-schedules \
  --playback-configuration-name my-ssai-config

# Get a prefetch schedule
aws mediatailor get-prefetch-schedule \
  --name my-prefetch \
  --playback-configuration-name my-ssai-config

# Create a prefetch schedule
aws mediatailor create-prefetch-schedule \
  --name my-prefetch \
  --playback-configuration-name my-ssai-config \
  --retrieval '{
    "DynamicVariables": {
      "session.id": "prefetch-session"
    },
    "StartTime": "2026-03-14T20:00:00Z",
    "EndTime": "2026-03-14T20:05:00Z"
  }' \
  --consumption '{
    "StartTime": "2026-03-14T20:05:00Z",
    "EndTime": "2026-03-14T20:30:00Z",
    "AvailMatchingCriteria": [
      {
        "DynamicVariable": "scte35.SpliceInsert.UniqueProgramId",
        "Operator": "EQUALS"
      }
    ]
  }'

# Delete a prefetch schedule
aws mediatailor delete-prefetch-schedule \
  --name my-prefetch \
  --playback-configuration-name my-ssai-config
```

### Channel Assembly — Channels

```bash
# List channels
aws mediatailor list-channels

# Describe a channel
aws mediatailor describe-channel --channel-name my-fast-channel

# Create a channel (FAST / channel assembly)
aws mediatailor create-channel \
  --channel-name my-fast-channel \
  --outputs '[
    {
      "HlsPlaylistSettings": {"ManifestWindowSeconds": 30},
      "ManifestName": "index",
      "SourceGroup": "hls-group"
    }
  ]' \
  --playback-mode LINEAR \
  --tier STANDARD

# Start a channel
aws mediatailor start-channel --channel-name my-fast-channel

# Stop a channel
aws mediatailor stop-channel --channel-name my-fast-channel

# Delete a channel
aws mediatailor delete-channel --channel-name my-fast-channel
```

### Channel Assembly — Source Locations & VOD Sources

```bash
# List source locations
aws mediatailor list-source-locations

# Create a source location (S3-backed VOD library)
aws mediatailor create-source-location \
  --source-location-name my-vod-library \
  --http-configuration '{
    "BaseUrl": "https://my-vod-bucket.s3.amazonaws.com/"
  }'

# Create a VOD source within a source location
aws mediatailor create-vod-source \
  --source-location-name my-vod-library \
  --vod-source-name my-episode-1 \
  --http-package-configurations '[
    {
      "Path": "episodes/ep1/hls/index.m3u8",
      "SourceGroup": "hls-group",
      "Type": "HLS"
    }
  ]'

# List VOD sources in a source location
aws mediatailor list-vod-sources \
  --source-location-name my-vod-library

# Delete a VOD source
aws mediatailor delete-vod-source \
  --source-location-name my-vod-library \
  --vod-source-name my-episode-1

# Delete a source location
aws mediatailor delete-source-location --source-location-name my-vod-library
```

### Channel Assembly — Programs (Schedule)

```bash
# List programs scheduled on a channel
aws mediatailor list-programs --channel-name my-fast-channel

# Describe a scheduled program
aws mediatailor describe-program \
  --channel-name my-fast-channel \
  --program-name ep1-slot

# Create (schedule) a program on a channel
aws mediatailor create-program \
  --channel-name my-fast-channel \
  --program-name ep1-slot \
  --source-location-name my-vod-library \
  --vod-source-name my-episode-1 \
  --schedule-configuration '{
    "TransitionType": "ABSOLUTE",
    "StartTime": "2026-03-14T21:00:00Z"
  }' \
  --ad-breaks '[
    {
      "MessageType": "SPLICE_INSERT",
      "OffsetMillis": 600000,
      "Slate": {"SourceLocationName": "my-vod-library", "VodSourceName": "slate"},
      "SpliceInsertMessage": {"AvailNum": 1, "AvailsExpected": 1, "SpliceEventId": 1001, "UniqueProgramId": 101}
    }
  ]'

# Delete a program from the schedule
aws mediatailor delete-program \
  --channel-name my-fast-channel \
  --program-name ep1-slot
```

### Tags

```bash
# List tags on a MediaTailor resource
aws mediatailor list-tags-for-resource --resource-arn <arn>

# Tag a resource
aws mediatailor tag-resource \
  --resource-arn <arn> \
  --tags '{"Env":"prod","Stream":"FAST-channel-1"}'

# Untag a resource
aws mediatailor untag-resource \
  --resource-arn <arn> \
  --tag-keys Env Stream
```
