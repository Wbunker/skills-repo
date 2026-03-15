# AWS Streaming, Interactive Video & Render — CLI Reference

For service concepts, see [streaming-ivs-capabilities.md](streaming-ivs-capabilities.md).

---

## aws ivs

### Channels

```bash
# List channels
aws ivs list-channels

# List channels filtered by name prefix
aws ivs list-channels --filter-by-name "prod-"

# Get a channel
aws ivs get-channel --arn arn:aws:ivs:us-east-1:123456789012:channel/AbCdEfGhIjKl

# Create a channel (low-latency, STANDARD type)
aws ivs create-channel \
  --name my-stream \
  --type STANDARD \
  --latency-mode LOW \
  --authorized false

# Create a channel with recording configuration attached
aws ivs create-channel \
  --name my-recorded-stream \
  --type STANDARD \
  --latency-mode LOW \
  --recording-configuration-arn arn:aws:ivs:us-east-1:123456789012:recording-configuration/AbCdEf

# Create an authorized channel (requires signed playback tokens)
aws ivs create-channel \
  --name my-private-stream \
  --type STANDARD \
  --authorized true

# Update a channel
aws ivs update-channel \
  --arn <channel-arn> \
  --latency-mode NORMAL \
  --type ADVANCED_HD

# Delete a channel
aws ivs delete-channel --arn <channel-arn>

# Batch get channels (up to 50 at a time)
aws ivs batch-get-channel \
  --arns <arn1> <arn2> <arn3>
```

### Stream Keys

```bash
# List stream keys for a channel
aws ivs list-stream-keys --channel-arn <channel-arn>

# Get a stream key value (used in the RTMPS ingest URL)
aws ivs get-stream-key --arn <stream-key-arn>

# Create a new stream key for a channel
aws ivs create-stream-key --channel-arn <channel-arn>

# Delete a stream key
aws ivs delete-stream-key --arn <stream-key-arn>

# Batch get stream keys
aws ivs batch-get-stream-key --arns <arn1> <arn2>
```

### Streams (Live Sessions)

```bash
# List currently live streams
aws ivs list-streams

# List streams filtered by state
aws ivs list-streams --filter-by-state LIVE

# Get the current live stream on a channel
aws ivs get-stream --channel-arn <channel-arn>

# List stream sessions (historical) for a channel
aws ivs list-stream-sessions --channel-arn <channel-arn>

# Get a specific stream session
aws ivs get-stream-session \
  --channel-arn <channel-arn> \
  --stream-id <stream-id>

# Stop a live stream (forcibly end the current stream)
aws ivs stop-stream --channel-arn <channel-arn>
```

### Timed Metadata

```bash
# Insert timed metadata into a live stream (synchronized to playback)
aws ivs put-metadata \
  --channel-arn <channel-arn> \
  --metadata '{"type":"poll","question":"What is your favorite game?","options":["A","B","C"]}'
```

### Recording Configurations

```bash
# List recording configurations
aws ivs list-recording-configurations

# Get a recording configuration
aws ivs get-recording-configuration --arn <recording-config-arn>

# Create a recording configuration (record all streams on attached channels to S3)
aws ivs create-recording-configuration \
  --name my-recording-config \
  --destination-configuration '{
    "s3": {
      "bucketName": "my-ivs-recordings"
    }
  }' \
  --thumbnail-configuration '{
    "recordingMode": "INTERVAL",
    "targetIntervalSeconds": 60
  }'

# Delete a recording configuration
aws ivs delete-recording-configuration --arn <recording-config-arn>
```

### Playback Key Pairs (Authorized Channels)

```bash
# List playback key pairs
aws ivs list-playback-key-pairs

# Get a playback key pair
aws ivs get-playback-key-pair --arn <key-pair-arn>

# Import a public key (the corresponding private key signs playback tokens)
# Generate keypair: openssl ecparam -name prime256v1 -genkey -noout -out private.pem
#                   openssl ec -in private.pem -pubout -out public.pem
aws ivs import-playback-key-pair \
  --name my-key-pair \
  --public-key-material "$(cat public.pem)"

# Delete a playback key pair
aws ivs delete-playback-key-pair --arn <key-pair-arn>
```

### Playback Restriction Policies

```bash
# List playback restriction policies
aws ivs list-playback-restriction-policies

# Get a playback restriction policy
aws ivs get-playback-restriction-policy --arn <policy-arn>

# Create a playback restriction policy (geo-block and referrer control)
aws ivs create-playback-restriction-policy \
  --name my-restriction-policy \
  --allowed-countries US CA GB \
  --allowed-origins "https://myapp.example.com" "https://www.myapp.example.com" \
  --enable-strict-origin-enforcement true

# Update a restriction policy
aws ivs update-playback-restriction-policy \
  --arn <policy-arn> \
  --allowed-countries US CA

# Delete a restriction policy
aws ivs delete-playback-restriction-policy --arn <policy-arn>
```

### Tags

```bash
# List tags on an IVS resource
aws ivs list-tags-for-resource --resource-arn <arn>

# Tag a resource
aws ivs tag-resource \
  --resource-arn <arn> \
  --tags Env=prod Team=streaming

# Untag a resource
aws ivs untag-resource \
  --resource-arn <arn> \
  --tag-keys Env Team
```

---

## aws ivs-realtime

### Stages (Real-Time WebRTC)

```bash
# List stages
aws ivs-realtime list-stages

# Get a stage
aws ivs-realtime get-stage --arn <stage-arn>

# Create a stage
aws ivs-realtime create-stage \
  --name my-interactive-stage

# Update a stage
aws ivs-realtime update-stage \
  --arn <stage-arn> \
  --name my-interactive-stage-v2

# Delete a stage
aws ivs-realtime delete-stage --arn <stage-arn>

# List stage sessions (historical)
aws ivs-realtime list-stage-sessions --stage-arn <stage-arn>

# Get a stage session
aws ivs-realtime get-stage-session \
  --stage-arn <stage-arn> \
  --session-id <session-id>

# List participants in a stage session
aws ivs-realtime list-participants \
  --stage-arn <stage-arn> \
  --session-id <session-id>

# Get a participant's details
aws ivs-realtime get-participant \
  --stage-arn <stage-arn> \
  --session-id <session-id> \
  --participant-id <participant-id>
```

### Participant Tokens

```bash
# Create a participant token (JWT for a user to join the stage)
aws ivs-realtime create-participant-token \
  --stage-arn <stage-arn> \
  --duration 60 \
  --user-id "user-123" \
  --attributes '{"role":"host","displayName":"Alice"}' \
  --capabilities PUBLISH SUBSCRIBE

# Disconnect a participant from the stage
aws ivs-realtime disconnect-participant \
  --stage-arn <stage-arn> \
  --participant-id <participant-id> \
  --reason "Removed by moderator"
```

### Compositions (Server-Side Mixing)

```bash
# List compositions
aws ivs-realtime list-compositions

# Get a composition
aws ivs-realtime get-composition --arn <composition-arn>

# Start a composition (mix stage participants into an output stream)
aws ivs-realtime start-composition \
  --stage-arn <stage-arn> \
  --destinations '[
    {
      "channel": {
        "channelArn": "arn:aws:ivs:us-east-1:123456789012:channel/AbCdEfGhIjKl",
        "encoderConfigurationArn": "<encoder-config-arn>"
      }
    }
  ]'

# Stop a composition
aws ivs-realtime stop-composition --arn <composition-arn>

# List encoder configurations
aws ivs-realtime list-encoder-configurations

# Create an encoder configuration for compositions
aws ivs-realtime create-encoder-configuration \
  --name my-encoder \
  --video '{
    "width": 1280,
    "height": 720,
    "framerate": 30,
    "bitrate": 2500000
  }'
```

### Storage Configurations (Record Real-Time to S3)

```bash
# List storage configurations
aws ivs-realtime list-storage-configurations

# Get a storage configuration
aws ivs-realtime get-storage-configuration --arn <storage-config-arn>

# Create a storage configuration
aws ivs-realtime create-storage-configuration \
  --name my-realtime-recording \
  --s3 '{
    "bucketName": "my-realtime-recordings"
  }'

# Delete a storage configuration
aws ivs-realtime delete-storage-configuration --arn <storage-config-arn>
```

---

## aws ivschat

### Chat Rooms

```bash
# List chat rooms
aws ivschat list-rooms

# Get a chat room
aws ivschat get-room --identifier <room-arn-or-id>

# Create a chat room
aws ivschat create-room \
  --name my-chat-room \
  --maximum-message-rate-per-second 10 \
  --maximum-message-length 256

# Update a chat room
aws ivschat update-room \
  --identifier <room-arn> \
  --maximum-message-rate-per-second 20

# Delete a chat room
aws ivschat delete-room --identifier <room-arn>
```

### Chat Tokens (Authentication)

```bash
# Create a chat token (server-side; issued to authenticated users)
aws ivschat create-chat-token \
  --room-identifier <room-arn> \
  --user-id "user-456" \
  --session-duration-in-minutes 60 \
  --capabilities SEND_MESSAGE \
  --attributes '{"displayName":"Bob","role":"viewer"}'

# Create a moderator token
aws ivschat create-chat-token \
  --room-identifier <room-arn> \
  --user-id "mod-789" \
  --session-duration-in-minutes 480 \
  --capabilities SEND_MESSAGE DELETE_MESSAGE DISCONNECT_USER \
  --attributes '{"role":"moderator"}'
```

### Logging Configurations

```bash
# List logging configurations
aws ivschat list-logging-configurations

# Create a logging configuration (send chat events to CloudWatch Logs)
aws ivschat create-logging-configuration \
  --name my-chat-logs \
  --destination-configuration '{
    "cloudWatchLogs": {
      "logGroupName": "/ivschat/my-chat-room"
    }
  }'

# Create a logging configuration (send to Kinesis Firehose)
aws ivschat create-logging-configuration \
  --name my-chat-firehose-logs \
  --destination-configuration '{
    "firehose": {
      "deliveryStreamName": "ivschat-events"
    }
  }'

# Delete a logging configuration
aws ivschat delete-logging-configuration --identifier <logging-config-arn>
```

### Chat Moderation

```bash
# Send an event to a room (server-side event, not a chat message)
aws ivschat send-event \
  --room-identifier <room-arn> \
  --event-name "poll-started" \
  --attributes '{"pollId":"p1","question":"Rate this stream!"}'

# Delete a chat message (moderation)
aws ivschat delete-message \
  --room-identifier <room-arn> \
  --id <message-id> \
  --reason "Violated community guidelines"

# Disconnect a user from a chat room
aws ivschat disconnect-user \
  --room-identifier <room-arn> \
  --user-id "user-456" \
  --reason "Banned by moderator"
```

---

## aws kinesisvideo

### Streams

```bash
# List streams
aws kinesisvideo list-streams

# List streams with a filter
aws kinesisvideo list-streams \
  --stream-name-condition '{"ComparisonOperator":"BEGINS_WITH","ComparisonValue":"camera-"}'

# Describe a stream
aws kinesisvideo describe-stream --stream-name my-camera-stream

# Create a stream
aws kinesisvideo create-stream \
  --stream-name my-camera-stream \
  --data-retention-in-hours 24 \
  --media-type "video/h264" \
  --device-name "front-door-camera"

# Update a stream's data retention
aws kinesisvideo update-data-retention \
  --stream-name my-camera-stream \
  --current-version <version-from-describe> \
  --operation INCREASE_DATA_RETENTION \
  --data-retention-change-in-hours 48

# Update stream metadata
aws kinesisvideo update-stream \
  --stream-name my-camera-stream \
  --current-version <version-from-describe> \
  --device-name "front-door-camera-v2" \
  --media-type "video/h265"

# Get a data endpoint for the stream (required before GetMedia/PutMedia calls)
aws kinesisvideo get-data-endpoint \
  --stream-name my-camera-stream \
  --api-name GET_HLS_STREAMING_SESSION_URL

# Delete a stream
aws kinesisvideo delete-stream --stream-arn <stream-arn>
```

### HLS Playback (via kinesis-video-archived-media)

```bash
# Get the HLS streaming session URL (first, get the data endpoint)
ENDPOINT=$(aws kinesisvideo get-data-endpoint \
  --stream-name my-camera-stream \
  --api-name GET_HLS_STREAMING_SESSION_URL \
  --query 'DataEndpoint' --output text)

# Get a LIVE HLS playback URL
aws kinesis-video-archived-media get-hls-streaming-session-url \
  --endpoint-url "$ENDPOINT" \
  --stream-name my-camera-stream \
  --playback-mode LIVE

# Get an ON_DEMAND HLS URL for a time range
aws kinesis-video-archived-media get-hls-streaming-session-url \
  --endpoint-url "$ENDPOINT" \
  --stream-name my-camera-stream \
  --playback-mode ON_DEMAND \
  --hls-fragment-selector '{
    "FragmentSelectorType": "SERVER_TIMESTAMP",
    "TimestampRange": {
      "StartTimestamp": "2026-03-14T10:00:00Z",
      "EndTimestamp": "2026-03-14T10:30:00Z"
    }
  }'

# Get a DASH streaming session URL
aws kinesis-video-archived-media get-dash-streaming-session-url \
  --endpoint-url "$ENDPOINT" \
  --stream-name my-camera-stream \
  --playback-mode LIVE
```

### WebRTC Signaling Channels

```bash
# List signaling channels
aws kinesisvideo list-signaling-channels

# Describe a signaling channel
aws kinesisvideo describe-signaling-channel \
  --channel-name my-signaling-channel

# Create a signaling channel
aws kinesisvideo create-signaling-channel \
  --channel-name my-signaling-channel \
  --channel-type SINGLE_MASTER

# Get signaling channel endpoints (for WebRTC SDK connection)
aws kinesisvideo get-signaling-channel-endpoint \
  --channel-arn <channel-arn> \
  --single-master-channel-endpoint-configuration '{
    "Protocols": ["WSS", "HTTPS"],
    "Role": "MASTER"
  }'

# Get ICE server configuration (STUN/TURN credentials)
# First get the HTTPS endpoint from the above command, then:
aws kinesis-video-signaling get-ice-server-config \
  --endpoint-url <https-endpoint-from-above> \
  --channel-arn <channel-arn> \
  --client-id my-viewer \
  --service TURN

# Delete a signaling channel
aws kinesisvideo delete-signaling-channel --channel-arn <channel-arn>
```

### Image Extraction

```bash
# Describe image generation configuration on a stream
aws kinesisvideo describe-image-generation-configuration \
  --stream-name my-camera-stream

# Enable image extraction (extract JPEG every 5 seconds to S3)
aws kinesisvideo update-image-generation-configuration \
  --stream-name my-camera-stream \
  --image-generation-configuration '{
    "Status": "ENABLED",
    "ImageSelectorType": "SERVER_TIMESTAMP",
    "DestinationConfig": {
      "Uri": "s3://my-frames-bucket/camera1/",
      "DestinationRegion": "us-east-1"
    },
    "SamplingInterval": 5000,
    "Format": "JPEG",
    "FormatConfig": {"JPEGQuality": "80"},
    "WidthPixels": 1280,
    "HeightPixels": 720
  }'

# Disable image extraction
aws kinesisvideo update-image-generation-configuration \
  --stream-name my-camera-stream \
  --image-generation-configuration '{"Status": "DISABLED"}'
```

### Notification Configuration

```bash
# Describe notification configuration
aws kinesisvideo describe-notification-configuration \
  --stream-name my-camera-stream

# Update notification configuration (send fragment events to SNS)
aws kinesisvideo update-notification-configuration \
  --stream-name my-camera-stream \
  --notification-configuration '{
    "Status": "ENABLED",
    "DestinationConfig": {
      "Uri": "arn:aws:sns:us-east-1:123456789012:video-events"
    }
  }'
```

### Tags

```bash
# List tags on a stream
aws kinesisvideo list-tags-for-stream --stream-name my-camera-stream

# Add tags to a stream
aws kinesisvideo tag-stream \
  --stream-name my-camera-stream \
  --tags Location=FrontDoor Building=HQ

# Remove tags from a stream
aws kinesisvideo untag-stream \
  --stream-name my-camera-stream \
  --tag-key-list Location Building
```

---

## aws nimble

### Studios

```bash
# List studios
aws nimble list-studios

# Get a studio
aws nimble get-studio --studio-id <studio-id>

# Create a studio
aws nimble create-studio \
  --display-name "My Production Studio" \
  --studio-name "my-studio" \
  --user-role-arn arn:aws:iam::123456789012:role/NimbleStudioUserRole \
  --admin-role-arn arn:aws:iam::123456789012:role/NimbleStudioAdminRole \
  --studio-encryption-configuration '{
    "keyType": "AWS_OWNED_KEY"
  }'

# Update a studio display name
aws nimble update-studio \
  --studio-id <studio-id> \
  --display-name "My Updated Production Studio"

# Delete a studio
aws nimble delete-studio --studio-id <studio-id>
```

### Launch Profiles

```bash
# List launch profiles in a studio
aws nimble list-launch-profiles --studio-id <studio-id>

# Get a launch profile
aws nimble get-launch-profile \
  --studio-id <studio-id> \
  --launch-profile-id <launch-profile-id>

# Get initialization details for a launch profile (streaming image, init scripts)
aws nimble get-launch-profile-initialization \
  --studio-id <studio-id> \
  --launch-profile-id <launch-profile-id> \
  --launch-profile-protocol-versions 2021-03-31 \
  --launch-purpose WORKSTATION \
  --platform LINUX

# Create a launch profile
aws nimble create-launch-profile \
  --studio-id <studio-id> \
  --name "Compositing Artists" \
  --description "Profile for Nuke compositing" \
  --studio-component-ids <component-id-1> <component-id-2> \
  --stream-configuration '{
    "clipboardMode": "ENABLED",
    "ec2InstanceTypes": ["g4dn.xlarge", "g4dn.2xlarge"],
    "maxSessionLengthInMinutes": 480,
    "maxStoppedSessionLengthInMinutes": 60,
    "sessionPersistenceMode": "ACTIVATED",
    "streamingImageIds": ["<streaming-image-id>"]
  }' \
  --ec2-subnet-ids subnet-abcdef01 subnet-abcdef02

# Update a launch profile
aws nimble update-launch-profile \
  --studio-id <studio-id> \
  --launch-profile-id <launch-profile-id> \
  --description "Updated compositing profile"

# Delete a launch profile
aws nimble delete-launch-profile \
  --studio-id <studio-id> \
  --launch-profile-id <launch-profile-id>
```

### Streaming Images

```bash
# List streaming images in a studio
aws nimble list-streaming-images --studio-id <studio-id>

# Get a streaming image
aws nimble get-streaming-image \
  --studio-id <studio-id> \
  --streaming-image-id <streaming-image-id>

# Create (register) a custom streaming image
aws nimble create-streaming-image \
  --studio-id <studio-id> \
  --name "Houdini 20 Artist Image" \
  --description "Amazon Linux 2, Houdini 20.0, Arnold" \
  --ec2-image-id ami-0123456789abcdef0

# Update a streaming image name/description
aws nimble update-streaming-image \
  --studio-id <studio-id> \
  --streaming-image-id <streaming-image-id> \
  --name "Houdini 20.5 Artist Image"

# Delete a streaming image
aws nimble delete-streaming-image \
  --studio-id <studio-id> \
  --streaming-image-id <streaming-image-id>
```

### Streaming Sessions

```bash
# List streaming sessions in a studio
aws nimble list-streaming-sessions --studio-id <studio-id>

# Get a streaming session
aws nimble get-streaming-session \
  --studio-id <studio-id> \
  --session-id <session-id>

# Create a streaming session (start a workstation)
aws nimble create-streaming-session \
  --studio-id <studio-id> \
  --launch-profile-id <launch-profile-id> \
  --streaming-image-id <streaming-image-id> \
  --ec2-instance-type g4dn.xlarge

# Create a streaming session stream (get the connect URL)
aws nimble create-streaming-session-stream \
  --studio-id <studio-id> \
  --session-id <session-id> \
  --expiration-in-seconds 60

# Stop a streaming session (stop the workstation, preserve data)
aws nimble stop-streaming-session \
  --studio-id <studio-id> \
  --session-id <session-id>

# Start a stopped streaming session
aws nimble start-streaming-session \
  --studio-id <studio-id> \
  --session-id <session-id> \
  --backup-id <backup-id>

# Delete a streaming session
aws nimble delete-streaming-session \
  --studio-id <studio-id> \
  --session-id <session-id>
```

### Studio Components

```bash
# List studio components
aws nimble list-studio-components --studio-id <studio-id>

# Get a studio component
aws nimble get-studio-component \
  --studio-id <studio-id> \
  --studio-component-id <component-id>

# Create a shared file system studio component (FSx for Lustre)
aws nimble create-studio-component \
  --studio-id <studio-id> \
  --name "Shared Asset Store" \
  --type SHARED_FILE_SYSTEM \
  --subtype AMAZON_FSX_FOR_LUSTRE \
  --configuration '{
    "sharedFileSystemConfiguration": {
      "fileSystemId": "fs-0123456789abcdef0",
      "linuxMountPoint": "/mnt/project",
      "shareType": "AWS_MANAGED"
    }
  }' \
  --ec2-security-group-ids sg-0123456789abcdef0

# Create a license service studio component
aws nimble create-studio-component \
  --studio-id <studio-id> \
  --name "Deadline License Server" \
  --type LICENSE_SERVICE \
  --subtype DEADLINE \
  --configuration '{
    "licenseServiceConfiguration": {
      "endpoint": "https://license.example.com"
    }
  }'

# Delete a studio component
aws nimble delete-studio-component \
  --studio-id <studio-id> \
  --studio-component-id <component-id>
```

### Studio Members

```bash
# List studio members
aws nimble list-studio-members --studio-id <studio-id>

# Get a studio member
aws nimble get-studio-member \
  --studio-id <studio-id> \
  --principal-id <iam-identity-center-user-id>

# Add studio members
aws nimble put-studio-members \
  --studio-id <studio-id> \
  --members '[
    {"principalId": "user-id-1", "persona": "ADMINISTRATOR"},
    {"principalId": "user-id-2", "persona": "USER"}
  ]' \
  --identity-store-id <identity-store-id>

# Remove a studio member
aws nimble delete-studio-member \
  --studio-id <studio-id> \
  --principal-id <iam-identity-center-user-id>
```

---

## aws deadline

### Farms

```bash
# List farms
aws deadline list-farms

# Get a farm
aws deadline get-farm --farm-id <farm-id>

# Create a farm
aws deadline create-farm \
  --display-name "My Render Farm" \
  --description "Production VFX render farm"
```

### Queues

```bash
# List queues in a farm
aws deadline list-queues --farm-id <farm-id>

# Get a queue
aws deadline get-queue \
  --farm-id <farm-id> \
  --queue-id <queue-id>

# Create a queue
aws deadline create-queue \
  --farm-id <farm-id> \
  --display-name "Main Render Queue" \
  --description "Primary queue for VFX renders" \
  --role-arn arn:aws:iam::123456789012:role/DeadlineCloudWorkerRole \
  --job-attachment-settings '{
    "s3BucketName": "my-deadline-assets",
    "rootPrefix": "job-attachments/"
  }'
```

### Fleets

```bash
# List fleets in a farm
aws deadline list-fleets --farm-id <farm-id>

# Get a fleet
aws deadline get-fleet \
  --farm-id <farm-id> \
  --fleet-id <fleet-id>

# Create a service-managed fleet (AWS manages EC2 instances)
aws deadline create-fleet \
  --farm-id <farm-id> \
  --display-name "Service-Managed Spot Fleet" \
  --role-arn arn:aws:iam::123456789012:role/DeadlineCloudWorkerRole \
  --max-worker-count 100 \
  --configuration '{
    "serviceManagedEc2": {
      "instanceCapabilities": {
        "vCpuCount": {"min": 8, "max": 64},
        "memoryMiB": {"min": 16384},
        "osFamily": "LINUX",
        "cpuArchitectureType": "x86_64",
        "allowedInstanceTypes": [],
        "excludedInstanceTypes": ["t3", "t3a"]
      },
      "instanceMarketOptions": {
        "type": "spot"
      }
    }
  }'

# Create a customer-managed fleet (customer manages EC2 Auto Scaling group)
aws deadline create-fleet \
  --farm-id <farm-id> \
  --display-name "Customer-Managed Fleet" \
  --role-arn arn:aws:iam::123456789012:role/DeadlineCloudWorkerRole \
  --max-worker-count 50 \
  --configuration '{
    "customerManaged": {
      "workerCapabilities": {
        "vCpuCount": {"min": 16},
        "memoryMiB": {"min": 32768},
        "osFamily": "LINUX",
        "cpuArchitectureType": "x86_64"
      },
      "storageProfileId": "<storage-profile-id>"
    }
  }'
```

### Queue-Fleet Associations

```bash
# Create a queue-fleet association (link a fleet to a queue)
aws deadline create-queue-fleet-association \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --fleet-id <fleet-id>

# Update a queue-fleet association (change status)
aws deadline update-queue-fleet-association \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --fleet-id <fleet-id> \
  --status ACTIVE

# Pause a queue-fleet association (stop dispatching new tasks to this fleet)
aws deadline update-queue-fleet-association \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --fleet-id <fleet-id> \
  --status STOP_SCHEDULING_AND_CANCEL_TASKS
```

### Jobs

```bash
# List jobs in a queue
aws deadline list-jobs \
  --farm-id <farm-id> \
  --queue-id <queue-id>

# Get a job
aws deadline get-job \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --job-id <job-id>

# Create a job (submit a render job from an inline job template)
aws deadline create-job \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --template '{"specificationVersion":"jobtemplate-2023-09","name":"My Render","steps":[{"name":"Render","script":{"actions":{"onRun":{"command":"blender","args":["--background","{{Param.SceneFile}}","--frame-start","{{Task.Param.Frame}}","--frame-end","{{Task.Param.Frame}}","--render-output","{{Param.OutputDir}}","--render-format","PNG","-a"]}}}}],"parameterDefinitions":[{"name":"SceneFile","type":"STRING"},{"name":"OutputDir","type":"STRING"}],"jobParameters":[{"name":"Frame","type":"INT","range":{"min":1,"max":250}}]}' \
  --template-type JSON \
  --parameters '{"SceneFile":{"string":"/mnt/project/scene.blend"},"OutputDir":{"string":"/mnt/output/render/"}}' \
  --priority 50
```

### Sessions & Session Actions

```bash
# List sessions for a job
aws deadline list-sessions \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --job-id <job-id>

# Get a session
aws deadline get-session \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --job-id <job-id> \
  --session-id <session-id>

# List session actions (tasks and sync actions within a session)
aws deadline list-session-actions \
  --farm-id <farm-id> \
  --queue-id <queue-id> \
  --job-id <job-id> \
  --session-id <session-id>
```

### Workers

```bash
# List workers in a fleet
aws deadline list-workers \
  --farm-id <farm-id> \
  --fleet-id <fleet-id>

# Get a worker
aws deadline get-worker \
  --farm-id <farm-id> \
  --fleet-id <fleet-id> \
  --worker-id <worker-id>
```

### Budgets

```bash
# List budgets for a farm
aws deadline list-budgets --farm-id <farm-id>

# Get a budget
aws deadline get-budget \
  --farm-id <farm-id> \
  --budget-id <budget-id>

# Create a budget (stop scheduling when spend limit is reached)
aws deadline create-budget \
  --farm-id <farm-id> \
  --display-name "Monthly Render Budget" \
  --usage-tracking-resource '{"queueId": "<queue-id>"}' \
  --approximate-dollar-limit 5000 \
  --schedule '{
    "fixed": {
      "startTime": "2026-04-01T00:00:00Z",
      "endTime": "2026-04-30T23:59:59Z"
    }
  }' \
  --actions '[
    {
      "type": "STOP_SCHEDULING_AND_CANCEL_TASKS",
      "thresholdPercentage": 100
    },
    {
      "type": "STOP_SCHEDULING_AND_COMPLETE_TASKS",
      "thresholdPercentage": 80
    }
  ]'
```

### Metered Products (License Tracking)

```bash
# Record usage of a metered product (commercial software license)
aws deadline put-metered-product \
  --license-endpoint-id <license-endpoint-id> \
  --product-id <product-id>
```
