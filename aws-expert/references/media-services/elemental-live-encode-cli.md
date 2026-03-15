# AWS Elemental Live & Encode — CLI Reference

For service concepts, see [elemental-live-encode-capabilities.md](elemental-live-encode-capabilities.md).

---

## aws medialive

### Inputs

```bash
# List all inputs
aws medialive list-inputs

# Describe a specific input
aws medialive describe-input --input-id <input-id>

# Create an RTMP push input
aws medialive create-input \
  --name "my-rtmp-push" \
  --type RTMP_PUSH \
  --input-security-groups <security-group-id>

# Create an HLS pull input
aws medialive create-input \
  --name "my-hls-pull" \
  --type URL_PULL \
  --sources "[{\"Url\":\"https://example.com/live.m3u8\"}]"

# Create a MediaConnect input (pull from a MediaConnect flow)
aws medialive create-input \
  --name "my-mediaconnect-input" \
  --type MEDIACONNECT \
  --media-connect-flows "[{\"FlowArn\":\"arn:aws:mediaconnect:us-east-1:123456789012:flow:my-flow\"}]" \
  --role-arn arn:aws:iam::123456789012:role/MediaLiveRole

# Create an RTP push input (dual-pipeline)
aws medialive create-input \
  --name "my-rtp-input" \
  --type RTP_PUSH \
  --input-security-groups <security-group-id>

# Delete an input
aws medialive delete-input --input-id <input-id>
```

### Input Security Groups

```bash
# List input security groups
aws medialive list-input-security-groups

# Create an input security group (allowlist CIDR ranges)
aws medialive create-input-security-group \
  --whitelist-rules "[{\"Cidr\":\"203.0.113.0/24\"},{\"Cidr\":\"198.51.100.5/32\"}]"

# Update CIDR allowlist on an existing security group
aws medialive update-input-security-group \
  --input-security-group-id <sg-id> \
  --whitelist-rules "[{\"Cidr\":\"203.0.113.0/24\"}]"

# Delete an input security group
aws medialive delete-input-security-group --input-security-group-id <sg-id>
```

### Channels

```bash
# List all channels
aws medialive list-channels

# List channels filtered by state
aws medialive list-channels --filter-by-state RUNNING

# Describe a channel (full configuration)
aws medialive describe-channel --channel-id <channel-id>

# Create a channel from a JSON body file
# (channel body includes InputAttachments, EncoderSettings, Destinations, ChannelClass)
aws medialive create-channel --cli-input-json file://channel-config.json

# Start a channel
aws medialive start-channel --channel-id <channel-id>

# Stop a channel
aws medialive stop-channel --channel-id <channel-id>

# Delete a channel (must be in IDLE state)
aws medialive delete-channel --channel-id <channel-id>

# Update channel settings (channel must be IDLE)
aws medialive update-channel \
  --channel-id <channel-id> \
  --cli-input-json file://updated-channel-config.json

# Wait until channel reaches RUNNING state
aws medialive wait channel-running --channel-id <channel-id>

# Wait until channel reaches STOPPED (IDLE) state
aws medialive wait channel-stopped --channel-id <channel-id>
```

### Channel Schedule (Schedule Actions)

```bash
# Describe the current schedule for a channel
aws medialive describe-schedule --channel-id <channel-id>

# Batch update schedule: add actions
# Action types: INPUT_SWITCH, STATIC_IMAGE_ACTIVATE, STATIC_IMAGE_DEACTIVATE,
#               SCTE35_SPLICE_INSERT, SCTE35_RETURN_TO_NETWORK, PAUSE, UNPAUSE
aws medialive batch-update-schedule \
  --channel-id <channel-id> \
  --creates '{
    "ScheduleActions": [
      {
        "ActionName": "switch-to-backup",
        "ScheduleActionStartSettings": {
          "FixedModeScheduleActionStartSettings": {
            "Time": "2026-03-14T20:00:00Z"
          }
        },
        "ScheduleActionSettings": {
          "InputSwitchSettings": {
            "InputAttachmentNameReference": "backup-input"
          }
        }
      }
    ]
  }'

# Remove a scheduled action by name
aws medialive batch-update-schedule \
  --channel-id <channel-id> \
  --deletes '{"ActionNames": ["switch-to-backup"]}'
```

### Multiplex

```bash
# List multiplexes
aws medialive list-multiplexes

# Describe a multiplex
aws medialive describe-multiplex --multiplex-id <multiplex-id>

# Create a multiplex (MPTS)
aws medialive create-multiplex \
  --name "my-mpts" \
  --multiplex-settings '{
    "TransportStreamBitrate": 20000000,
    "TransportStreamId": 1,
    "TransportStreamReservedBitrate": 0,
    "MaximumVideoBufferDelayMilliseconds": 1000
  }' \
  --availability-zones us-east-1a us-east-1b

# List programs within a multiplex
aws medialive list-multiplex-programs --multiplex-id <multiplex-id>

# Create a program within a multiplex
aws medialive create-multiplex-program \
  --multiplex-id <multiplex-id> \
  --program-name "program-1" \
  --multiplex-program-settings '{
    "ProgramNumber": 1,
    "ServiceDescriptor": {
      "ProviderName": "MyProvider",
      "ServiceName": "Channel1"
    },
    "VideoSettings": {
      "ConstantBitrate": 5000000
    }
  }'

# Start a multiplex
aws medialive start-multiplex --multiplex-id <multiplex-id>

# Stop a multiplex
aws medialive stop-multiplex --multiplex-id <multiplex-id>

# Delete a multiplex
aws medialive delete-multiplex --multiplex-id <multiplex-id>
```

### Tags & Miscellaneous

```bash
# List tags on a MediaLive resource
aws medialive list-tags-for-resource --resource-arn <arn>

# Add tags
aws medialive create-tags \
  --resource-arn <arn> \
  --tags '{"Environment":"prod","Team":"broadcast"}'

# Remove tags
aws medialive delete-tags \
  --resource-arn <arn> \
  --tag-keys Environment Team

# List offerings (reserved capacity)
aws medialive list-offerings

# Purchase a reserved offering
aws medialive purchase-offering \
  --offering-id <offering-id> \
  --count 1 \
  --name "prod-reservation"

# List existing reservations
aws medialive list-reservations
```

---

## aws mediaconvert

### Jobs

```bash
# Submit a transcoding job from a JSON body file
aws mediaconvert create-job \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --cli-input-json file://job.json

# Get the account-specific MediaConvert endpoint (required before API calls)
aws mediaconvert describe-endpoints

# List recent jobs
aws mediaconvert list-jobs \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com

# List jobs filtered by status
aws mediaconvert list-jobs \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --status COMPLETE

# List jobs filtered by queue
aws mediaconvert list-jobs \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --queue arn:aws:mediaconvert:us-east-1:123456789012:queues/Default

# Get job details (includes progress and error messages)
aws mediaconvert get-job \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --id <job-id>

# Cancel a running or queued job
aws mediaconvert cancel-job \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --id <job-id>
```

### Job Templates

```bash
# List job templates
aws mediaconvert list-job-templates \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com

# Get a specific job template
aws mediaconvert get-job-template \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-hls-template"

# Create a job template from a JSON body file
aws mediaconvert create-job-template \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --cli-input-json file://job-template.json

# Update a job template
aws mediaconvert update-job-template \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-hls-template" \
  --cli-input-json file://updated-template.json

# Delete a job template
aws mediaconvert delete-job-template \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-hls-template"
```

### Output Presets

```bash
# List output presets (includes AWS system presets)
aws mediaconvert list-presets \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com

# List only custom presets
aws mediaconvert list-presets \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --list-by NAME \
  --category ""

# Get a specific preset
aws mediaconvert get-preset \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "System-Generic_Hd_Mp4_Avc_Aac_16x9_1920x1080p_24Hz_6Mbps"

# Create a custom output preset
aws mediaconvert create-preset \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-1080p-h264" \
  --settings file://preset-settings.json

# Update a custom preset
aws mediaconvert update-preset \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-1080p-h264" \
  --settings file://updated-preset-settings.json

# Delete a custom preset
aws mediaconvert delete-preset \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "my-1080p-h264"
```

### Queues

```bash
# List queues
aws mediaconvert list-queues \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com

# Get queue details
aws mediaconvert get-queue \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name Default

# Create an on-demand queue
aws mediaconvert create-queue \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "priority-queue" \
  --pricing-plan ON_DEMAND

# Create a reserved queue (requires reservation plan)
aws mediaconvert create-queue \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "reserved-queue" \
  --pricing-plan RESERVED \
  --reservation-plan-settings '{
    "Commitment": "ONE_YEAR",
    "ReservedSlots": 5,
    "RenewalType": "AUTO_RENEW"
  }'

# Update queue (e.g., change status to PAUSED)
aws mediaconvert update-queue \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "priority-queue" \
  --status PAUSED

# Delete a queue (must be empty)
aws mediaconvert delete-queue \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --name "priority-queue"
```

### Tags

```bash
# List tags on a MediaConvert resource
aws mediaconvert list-tags-for-resource \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --arn <resource-arn>

# Tag a resource
aws mediaconvert tag-resource \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --arn <resource-arn> \
  --tags '{"Project":"my-ott","Env":"prod"}'

# Untag a resource
aws mediaconvert untag-resource \
  --endpoint-url https://<account-id>.mediaconvert.<region>.amazonaws.com \
  --arn <resource-arn> \
  --tag-keys Project Env
```

---

## aws elastictranscoder

> Elastic Transcoder is a legacy service. For new workloads use `aws mediaconvert`.

### Pipelines

```bash
# List pipelines
aws elastictranscoder list-pipelines

# Read a pipeline
aws elastictranscoder read-pipeline --id <pipeline-id>

# Create a pipeline
aws elastictranscoder create-pipeline \
  --name "my-pipeline" \
  --input-bucket my-input-bucket \
  --output-bucket my-output-bucket \
  --role arn:aws:iam::123456789012:role/ElasticTranscoderRole

# Update a pipeline
aws elastictranscoder update-pipeline \
  --id <pipeline-id> \
  --name "my-pipeline-updated" \
  --input-bucket my-input-bucket \
  --role arn:aws:iam::123456789012:role/ElasticTranscoderRole

# Update pipeline status (Active or Paused)
aws elastictranscoder update-pipeline-status \
  --id <pipeline-id> \
  --status Paused

# Delete a pipeline (must have no pending jobs)
aws elastictranscoder delete-pipeline --id <pipeline-id>
```

### Jobs

```bash
# Create a transcoding job
aws elastictranscoder create-job \
  --pipeline-id <pipeline-id> \
  --input '{"Key":"input/video.mp4"}' \
  --output '{
    "Key": "output/video-720p.mp4",
    "PresetId": "1351620000001-000010"
  }'

# Read a job
aws elastictranscoder read-job --id <job-id>

# List jobs in a pipeline
aws elastictranscoder list-jobs-by-pipeline --pipeline-id <pipeline-id>

# List jobs by status
aws elastictranscoder list-jobs-by-status --status Complete

# Cancel a job (only while Submitted)
aws elastictranscoder cancel-job --id <job-id>
```

### Presets

```bash
# List all presets (system + custom)
aws elastictranscoder list-presets

# Read a preset
aws elastictranscoder read-preset --id <preset-id>

# Create a custom preset
aws elastictranscoder create-preset \
  --name "my-720p" \
  --container "mp4" \
  --video '{
    "Codec": "H.264",
    "BitRate": "2500",
    "FrameRate": "30",
    "Resolution": "1280x720",
    "CodecOptions": {"Profile": "main"}
  }' \
  --audio '{
    "Codec": "AAC",
    "SampleRate": "44100",
    "BitRate": "128",
    "Channels": "2"
  }'

# Delete a custom preset (cannot delete system presets)
aws elastictranscoder delete-preset --id <preset-id>
```
