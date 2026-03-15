# GCP Media Processing — CLI Reference

## Transcoder API

### Job Templates

```bash
# List built-in job templates
gcloud transcoder job-templates list \
  --location=us-central1 \
  --project=my-project

# Describe a preset template
gcloud transcoder job-templates describe preset/web-hd \
  --location=us-central1 \
  --project=my-project

# Create a custom job template (save and reuse)
cat > my-template.json << 'EOF'
{
  "config": {
    "inputs": [{"key": "input0", "uri": ""}],
    "output": {"uri": ""},
    "elementaryStreams": [
      {
        "key": "video-360p",
        "videoStream": {
          "h264": {
            "heightPixels": 360,
            "widthPixels": 640,
            "bitrateBps": 800000,
            "frameRate": 30,
            "pixelFormat": "yuv420p"
          }
        }
      },
      {
        "key": "video-720p",
        "videoStream": {
          "h264": {
            "heightPixels": 720,
            "widthPixels": 1280,
            "bitrateBps": 3000000,
            "frameRate": 30,
            "pixelFormat": "yuv420p"
          }
        }
      },
      {
        "key": "video-1080p",
        "videoStream": {
          "h264": {
            "heightPixels": 1080,
            "widthPixels": 1920,
            "bitrateBps": 5000000,
            "frameRate": 30,
            "pixelFormat": "yuv420p"
          }
        }
      },
      {
        "key": "audio-aac",
        "audioStream": {
          "codec": "aac",
          "bitrateBps": 128000,
          "channelCount": 2,
          "sampleRateHertz": 44100
        }
      }
    ],
    "muxStreams": [
      {
        "key": "hls-360p",
        "container": "ts",
        "elementaryStreams": ["video-360p", "audio-aac"],
        "segmentSettings": {"segmentDuration": "4s"}
      },
      {
        "key": "hls-720p",
        "container": "ts",
        "elementaryStreams": ["video-720p", "audio-aac"],
        "segmentSettings": {"segmentDuration": "4s"}
      },
      {
        "key": "hls-1080p",
        "container": "ts",
        "elementaryStreams": ["video-1080p", "audio-aac"],
        "segmentSettings": {"segmentDuration": "4s"}
      }
    ],
    "manifests": [
      {
        "fileName": "master.m3u8",
        "type": "HLS",
        "muxStreams": ["hls-360p", "hls-720p", "hls-1080p"]
      }
    ]
  }
}
EOF

gcloud transcoder job-templates create my-hls-abr-template \
  --location=us-central1 \
  --file=my-template.json \
  --project=my-project
```

### Create Transcoder Jobs

```bash
# Simple job using a built-in template
gcloud transcoder jobs create \
  --location=us-central1 \
  --input-uri=gs://my-input-bucket/raw/video.mp4 \
  --output-uri=gs://my-output-bucket/transcoded/video/ \
  --template-id=preset/web-hd \
  --project=my-project

# Job using a custom template
gcloud transcoder jobs create \
  --location=us-central1 \
  --input-uri=gs://my-input-bucket/raw/video.mp4 \
  --output-uri=gs://my-output-bucket/transcoded/video/ \
  --template-id=my-hls-abr-template \
  --project=my-project

# Job with full inline JSON config (most flexible)
cat > job-config.json << 'EOF'
{
  "config": {
    "inputs": [
      {
        "key": "input0",
        "uri": "gs://my-input-bucket/raw/video.mp4"
      }
    ],
    "output": {
      "uri": "gs://my-output-bucket/transcoded/video/"
    },
    "elementaryStreams": [
      {
        "key": "video-720p",
        "videoStream": {
          "h264": {
            "heightPixels": 720,
            "widthPixels": 1280,
            "bitrateBps": 3000000,
            "frameRate": 30
          }
        }
      },
      {
        "key": "audio-en",
        "audioStream": {
          "codec": "aac",
          "bitrateBps": 128000,
          "channelCount": 2,
          "sampleRateHertz": 44100,
          "languageCode": "en-US"
        }
      }
    ],
    "muxStreams": [
      {
        "key": "mp4-720p",
        "container": "mp4",
        "elementaryStreams": ["video-720p", "audio-en"]
      }
    ],
    "overlays": [
      {
        "image": {
          "uri": "gs://my-input-bucket/assets/watermark.png",
          "resolution": {"x": 0.1, "y": 0.1}
        },
        "animations": [
          {
            "animationStatic": {
              "xy": {"x": 0.85, "y": 0.02},
              "startTimeOffset": "0s"
            }
          }
        ]
      }
    ],
    "spriteSheets": [
      {
        "filePrefix": "thumbnails/thumb",
        "spriteWidthPixels": 128,
        "spriteHeightPixels": 72,
        "interval": "10s"
      }
    ]
  }
}
EOF

gcloud transcoder jobs create \
  --location=us-central1 \
  --file=job-config.json \
  --project=my-project
```

### Manage Transcoder Jobs

```bash
# List all jobs
gcloud transcoder jobs list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,state,createTime,ttlAfterCompletionDays)"

# Describe a job (shows state, progress, output details)
gcloud transcoder jobs describe JOB_ID \
  --location=us-central1 \
  --project=my-project

# Delete a completed job
gcloud transcoder jobs delete JOB_ID \
  --location=us-central1 \
  --project=my-project

# List job templates
gcloud transcoder job-templates list \
  --location=us-central1 \
  --project=my-project

# Delete a custom template
gcloud transcoder job-templates delete my-hls-abr-template \
  --location=us-central1 \
  --project=my-project
```

---

## Live Stream API

### Manage Inputs

```bash
# Create an RTMP input
gcloud live-stream inputs create rtmp-input-1 \
  --location=us-central1 \
  --type=RTMP_PUSH \
  --project=my-project

# Create an SRT input
gcloud live-stream inputs create srt-input-1 \
  --location=us-central1 \
  --type=SRT_PUSH \
  --project=my-project

# Describe an input (shows ingest endpoint URI)
gcloud live-stream inputs describe rtmp-input-1 \
  --location=us-central1 \
  --project=my-project
# Look for: uri field with rtmp://... endpoint

# List inputs
gcloud live-stream inputs list \
  --location=us-central1 \
  --project=my-project

# Delete an input
gcloud live-stream inputs delete rtmp-input-1 \
  --location=us-central1 \
  --project=my-project
```

### Manage Channels

```bash
# Create a channel with HLS output
cat > channel-config.json << 'EOF'
{
  "inputAttachments": [
    {
      "key": "my-input",
      "input": "projects/PROJECT_NUMBER/locations/us-central1/inputs/rtmp-input-1"
    }
  ],
  "output": {
    "uri": "gs://my-live-bucket/live-output/"
  },
  "elementaryStreams": [
    {
      "key": "es_video_720p",
      "videoStream": {
        "h264": {
          "profile": "high",
          "widthPixels": 1280,
          "heightPixels": 720,
          "bitrateBps": 3000000,
          "frameRate": 30
        }
      }
    },
    {
      "key": "es_audio",
      "audioStream": {
        "codec": "aac",
        "channelCount": 2,
        "bitrateBps": 128000
      }
    }
  ],
  "muxStreams": [
    {
      "key": "mux_hls_720p",
      "container": "ts",
      "elementaryStreams": ["es_video_720p", "es_audio"],
      "segmentSettings": {"segmentDuration": "4s"}
    }
  ],
  "manifests": [
    {
      "fileName": "master.m3u8",
      "type": "HLS",
      "muxStreams": ["mux_hls_720p"],
      "maxSegmentCount": 5
    }
  ]
}
EOF

gcloud live-stream channels create my-channel \
  --location=us-central1 \
  --file=channel-config.json \
  --project=my-project

# Start a channel (begin accepting ingest)
gcloud live-stream channels start my-channel \
  --location=us-central1 \
  --project=my-project

# Stop a channel
gcloud live-stream channels stop my-channel \
  --location=us-central1 \
  --project=my-project

# List channels
gcloud live-stream channels list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,streamingState,inputAttachments[0].key)"

# Describe a channel (shows current state)
gcloud live-stream channels describe my-channel \
  --location=us-central1 \
  --project=my-project

# Delete a channel (must be stopped first)
gcloud live-stream channels delete my-channel \
  --location=us-central1 \
  --project=my-project
```

### Channel Events

```bash
# Create a mute event (insert slate/black frame)
gcloud live-stream channels events create slate-event \
  --channel=my-channel \
  --location=us-central1 \
  --type=MUTE \
  --project=my-project

# List events for a channel
gcloud live-stream channels events list \
  --channel=my-channel \
  --location=us-central1 \
  --project=my-project

# Delete an event
gcloud live-stream channels events delete slate-event \
  --channel=my-channel \
  --location=us-central1 \
  --project=my-project
```

---

## Video Intelligence API

```bash
# Detect labels in a Cloud Storage video file (async)
gcloud ml video detect-labels gs://my-bucket/videos/sample.mp4 \
  --format=json \
  --project=my-project

# Detect faces in video
gcloud ml video detect-faces gs://my-bucket/videos/sample.mp4 \
  --format=json \
  --project=my-project

# Detect shot changes
gcloud ml video detect-shots gs://my-bucket/videos/sample.mp4 \
  --format=json \
  --project=my-project

# Detect text in video (OCR)
gcloud ml video detect-text gs://my-bucket/videos/sample.mp4 \
  --format=json \
  --project=my-project

# All detect-* commands return an operation name for async results
# Check operation status
gcloud ml video operations describe OPERATION_NAME \
  --project=my-project

# Transcribe speech in video
gcloud ml video transcribe-speech gs://my-bucket/videos/presentation.mp4 \
  --language-code=en-US \
  --format=json \
  --project=my-project
```

---

## Media CDN

```bash
# Create an origin for Media CDN (Cloud Storage or load balancer)
gcloud edge-cache origins create my-video-origin \
  --origin-address=my-video-bucket.storage.googleapis.com \
  --description="GCS origin for video assets" \
  --project=my-project

# List origins
gcloud edge-cache origins list --project=my-project

# Create a Media CDN service
cat > media-cdn-config.yaml << 'EOF'
routing:
  hostRules:
  - hosts:
    - video.example.com
    pathMatcher: video-matcher
  pathMatchers:
  - name: video-matcher
    routeRules:
    - priority: 1
      matchRules:
      - prefixMatch: /hls/
      origin: my-video-origin
      routeAction:
        cdnPolicy:
          cacheMode: CACHE_ALL_STATIC
          defaultTtl: 3600s
          maxTtl: 86400s
          signedRequestMode: REQUIRE_SIGNATURES
          signedRequestKeyset: my-keyset
EOF

gcloud edge-cache services create my-media-cdn \
  --routing-file=media-cdn-config.yaml \
  --project=my-project

# Create a keyset for signed URL requests
gcloud edge-cache keysets create my-keyset \
  --project=my-project

# Add a key to the keyset
gcloud edge-cache keysets update my-keyset \
  --add-public-key=id=key1,value=BASE64_ENCODED_PUBLIC_KEY \
  --project=my-project

# List Media CDN services
gcloud edge-cache services list --project=my-project

# Describe a Media CDN service
gcloud edge-cache services describe my-media-cdn --project=my-project

# Invalidate cached objects (purge content)
gcloud edge-cache services invalidate-cache my-media-cdn \
  --path=/hls/event-123/* \
  --project=my-project

# Delete a Media CDN service
gcloud edge-cache services delete my-media-cdn --project=my-project
```
