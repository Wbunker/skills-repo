# GCP Media Processing — Capabilities

## Transcoder API

The **Transcoder API** is a fully managed, serverless video encoding service that converts video files stored in Cloud Storage into streaming-optimized formats.

### Core Features

**Input/Output:**
- Input from Cloud Storage (gs:// URIs)
- Output to Cloud Storage
- Supports virtually all common input formats: MP4, MOV, AVI, MKV, WebM, MXF, and many more
- Processes audio-only, video-only, or muxed A/V files

**Output codecs and containers:**

| Video Codec | Use Case |
|---|---|
| H.264 (AVC) | Maximum device compatibility; streaming, download |
| H.265 (HEVC) | Better quality at lower bitrate; Apple devices, modern players |
| VP9 | Open codec; YouTube, web browsers |
| AV1 | Best compression efficiency; modern OTT platforms |

| Container / Manifest | Use Case |
|---|---|
| MP4 | Download, progressive play |
| HLS (M3U8 + TS segments) | Apple devices, CDN streaming |
| MPEG-DASH (MPD + fragmented MP4) | Android, smart TVs, web |

**Adaptive Bitrate (ABR):**
- Define multiple renditions (resolution + bitrate ladders) in one job config
- Transcoder API generates HLS or DASH manifest automatically
- Example ladder: 1080p@5Mbps, 720p@3Mbps, 480p@1.5Mbps, 360p@0.8Mbps, 240p@0.4Mbps
- Players automatically select the appropriate rendition based on available bandwidth

**Audio features:**
- Multiple audio track support (different languages)
- Audio normalization (loudness normalization to LUFS target)
- Audio codec: AAC, Opus

**Overlay and watermarking:**
- Image overlay (PNG with transparency) positioned on video (logo watermarks)
- Text overlay (via image-based text; no native text rendering)
- Time-limited overlays (appear during specific time ranges)

**Subtitle and caption processing:**
- Input: SRT, WebVTT
- Embedded in MP4 (TTML), HLS (WebVTT), DASH (WebVTT)
- Burn-in captions (hardcode into video frames)

**Sprite sheets (thumbnail generation):**
- Extract periodic thumbnails (e.g., every 10 seconds) into a sprite sheet image
- Used by video players for seek preview thumbnails
- Also supports individual thumbnail frames per-interval

**Processing model:**
- Asynchronous job-based; submit job → poll for completion or use Pub/Sub notification
- Serverless; no infrastructure to manage; scales automatically
- Pricing: per minute of output video, varies by codec and resolution tier

### Job Templates

Predefined templates for common configurations:
- `preset/web-hd`: H.264, 720p, HLS output
- `preset/web-sd`: H.264, 480p, HLS output
- Custom templates: create reusable `JobTemplate` resources

---

## Live Stream API

The **Live Stream API** ingests live video streams, transcodes them in real time, and outputs adaptive bitrate segments to Cloud Storage.

### Input Protocols

| Protocol | Use Case |
|---|---|
| RTMP | Most common; OBS, streaming encoders, broadcast hardware |
| SRT (Secure Reliable Transport) | Low-latency; reliable over internet; used in broadcast workflows |
| RTP (MPEG-TS over UDP) | Professional broadcast; SMPTE 2022 |
| RTMPS | RTMP over TLS; for secure ingest |

### Channel-Based Architecture

- **Input**: endpoint that receives the inbound live stream; has a unique ingest IP/port
- **Channel**: main resource; associates inputs with transcode config; manages lifecycle
- **Event**: scheduled operation on a channel (e.g., insert slate, switch input)

### Output Formats

- HLS: segments to GCS; M3U8 manifest
- MPEG-DASH: fragmented MP4 segments to GCS; MPD manifest
- Resolution support: up to 1080p (1920x1080) and 4K (3840x2160) depending on config

### High-Availability Configuration

- **Redundant inputs**: define a primary and backup input; automatic failover if primary fails
- **Channel redundancy**: deploy channels in multiple regions; use global load balancer to route viewers

### Low-Latency Considerations

- Standard HLS/DASH: ~15-30 seconds latency (segment duration based)
- Reduce segment duration (2-4 seconds) for lower latency (~10-15 second E2E)
- For sub-5-second latency: use DASH-LL or HLS-LL protocols (not yet supported natively; requires custom setup)

---

## Video Stitcher API

The **Video Stitcher API** enables server-side ad insertion (SSAI) by dynamically stitching advertisements into video streams without client-side involvement.

### How SSAI Works

1. Player requests video stream URL from Video Stitcher API (with ad tag URL as parameter)
2. Video Stitcher API fetches the VAST/VMAP ad tag from the ad server
3. Ad creatives are transcoded (once, then cached) to match stream specs
4. Modified HLS/DASH manifest is returned with ad segments interleaved
5. Player plays the seamless stream; cannot easily skip ads (no client-side manipulation)

### Supported Ad Formats

- **VAST 3.0, 4.0**: Video Ad Serving Template; single inline ad
- **VMAP 1.0**: Video Multiple Ad Playlist; ad break schedule definition
- **VPAID 2.0**: interactive ad (JavaScript); requires special handling

### Content Sources

- VOD (Video on Demand): HLS/DASH manifest stored in GCS or served from CDN
- Live: live stream HLS/DASH from Live Stream API or third-party encoder

### CDN Integration

- Signed URLs and cookies for content protection
- Integration with Media CDN (edge cache serving), Cloud CDN, or any CDN
- Ad transcoding cache: transcoded ad creatives cached to avoid repeated transcoding

---

## Video Intelligence API

The **Video Intelligence API** uses ML to analyze video content and extract structured information.

### Analysis Features

| Feature | Description |
|---|---|
| Label detection | Identify objects, scenes, activities (e.g., "car", "outdoor", "running") |
| Shot change detection | Identify timestamps where camera shots change |
| Face detection | Detect and track faces across frames; does NOT identify who they are |
| Person detection | Detect and track full body presence in frames |
| Object tracking | Track bounding boxes of detected objects across frames |
| Text detection (OCR) | Extract text visible in video frames (signs, titles, overlays) |
| Speech transcription | Transcribe spoken audio to text with timestamps |
| Logo recognition | Identify brand logos in video frames |
| Safe search detection | Detect adult, violent, or sensitive content |
| Explicit content detection | Frame-level adult content classification |

### Processing Modes

- **SHOT_MODE**: analyze per shot change
- **SEGMENT_MODE**: analyze a specific time segment
- **FRAME_MODE**: analyze every frame (most detailed; most expensive)

### Input Sources

- Cloud Storage URI (gs://): asynchronous processing; returns operation name; poll for completion
- Inline video data: synchronous for very short clips (not recommended for production)

### Output

Results returned as JSON with time offsets (`startTimeOffset`, `endTimeOffset`) for each detected entity, enabling downstream indexing and search.

### Use Cases

- **Content moderation**: auto-detect policy violations before publishing
- **Video indexing**: build searchable catalog of video content
- **Highlight extraction**: identify shots with specific objects/activities
- **Accessibility**: auto-generate transcripts for closed captions
- **Ad targeting**: understand video content for contextual ad placement
- **Compliance**: verify brand safety and content standards at scale

---

## Media CDN

**Media CDN** is Google's large-scale video delivery CDN, distinct from Cloud CDN. It is optimized for streaming media workloads (large files, high concurrency).

> Primary documentation: see `networking/cloud-cdn-capabilities.md`

Key differentiators from Cloud CDN:
- **Edge PoPs co-located with major ISPs**: lower RTT and better throughput for end users
- **Large object optimization**: handles multi-GB video segment requests efficiently; parallel chunk fetching
- **First-chunk optimization**: prioritizes low latency for the first segment to reduce startup time
- **Shielding (origin protection)**: shield tier prevents origin overload during peak concurrency
- **Signed requests**: per-URL token signing, signed cookies, or URL expiration for content protection
- **Media content awareness**: understands HLS/DASH manifest structures for smarter caching
- **Routing policy**: anycast routing with ISP-level peering for optimal path selection
