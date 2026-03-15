# AWS Elemental Live & Encode — Capabilities Reference

For CLI commands, see [elemental-live-encode-cli.md](elemental-live-encode-cli.md).

---

## Services in this namespace

| Service | Purpose | Workload type |
|---|---|---|
| AWS Elemental MediaLive | Broadcast-grade live video encoding | Live |
| AWS Elemental MediaConvert | File-based VOD transcoding | VOD / file-based |
| Amazon Elastic Transcoder | Legacy file transcoding (prefer MediaConvert) | VOD (legacy) |

---

## AWS Elemental MediaLive

### Purpose
MediaLive encodes live video streams for broadcast and streaming delivery. It accepts contribution-quality live inputs, applies real-time video/audio processing, and outputs encoded streams to delivery targets. It is purpose-built for 24/7 high-availability broadcast workflows.

### Core Concepts

| Concept | Description |
|---|---|
| Channel | The primary processing unit. Encodes one live stream. Tied to an input and one or more output groups. |
| Channel class | **STANDARD** (dual pipeline, redundant) or **SINGLE_PIPELINE** (single pipeline, lower cost). |
| Input | The video source attached to a channel. One active input at a time; additional inputs can be prepared for instant switching. |
| Input security group | Allowlist of CIDR blocks permitted to push video to the channel's push endpoints. |
| Output group | A destination for encoded output (e.g., an HLS package to S3, a UDP stream to a downstream encoder). |
| Multiplex | Combines multiple MediaLive channels into a single MPTS (multi-program transport stream) for satellite/cable distribution. |
| Schedule action | Time-based or immediate actions: switch input, activate image overlay, insert SCTE-35 message, pause channel. |

### Input Types

| Input type | Protocol | Direction |
|---|---|---|
| RTMP push | RTMP/RTMPS | Push (source pushes to MediaLive endpoint) |
| RTP push | RTP | Push |
| RTMP pull | RTMP | Pull (MediaLive pulls from source URL) |
| HLS pull | HTTP/HTTPS | Pull — MediaLive reads an HLS source |
| MP4 pull | HTTP/HTTPS | Pull — file-based input for file-to-live workflows |
| MediaConnect | AWS Elemental MediaConnect flow | Pull — contribution transport |
| Elemental Link | HDMI/SDI hardware appliance | Direct hardware input |
| SMPTE 2110 | IP video (via VPC) | Push — professional IP production |

### Channel Classes & Pipelines

- **STANDARD**: Two independent encoding pipelines (pipeline 0 and pipeline 1). Redundant delivery to downstream systems that support dual-feed failover. Required for disaster-recovery SLAs.
- **SINGLE_PIPELINE**: One encoding pipeline. Lower cost, suitable for less-critical streams or development.

Both class types support the same codec and output group capabilities.

### Output Groups

| Output group type | Use case |
|---|---|
| HLS | Adaptive bitrate delivery; pushes to S3, HTTP PUT endpoint, or MediaPackage |
| DASH ISO | MPEG-DASH adaptive bitrate; pushes to S3 or HTTP PUT |
| MS Smooth | Microsoft Smooth Streaming; pushes to IIS Media Services or Azure |
| RTMP | Push encoded stream to CDN ingest point (e.g., YouTube, Twitch, Wowza) |
| UDP/TS | MPEG-2 transport stream over UDP; used for broadcast contribution |
| MediaPackage | Direct integration with MediaPackage origin (recommended for OTT) |
| MediaConnect | Push encoded output back through MediaConnect for transport |
| Multiplex | Output to a MediaLive Multiplex for MPTS distribution |
| Archive | Record raw TS to S3 |
| Frame capture | Periodic JPEG frame captures to S3 |

### Video Codecs

| Codec | Notes |
|---|---|
| H.264 (AVC) | Most widely supported. Profiles: Baseline, Main, High. |
| H.265 (HEVC) | Better compression at same quality. Required for 4K/UHD. |
| AV1 | Open codec; available for select output types. |
| MPEG-2 Video | Legacy; used for broadcast TS workflows. |

### Audio Capabilities
- Up to 20 audio tracks per output group
- Codecs: AAC (LC, HE-v1, HE-v2), AC-3, E-AC-3 (Dolby Digital Plus), MP2, PCM, pass-through
- Audio normalization (CALM Act / EBU R128)
- Audio descriptions (AD) track support
- Audio selector: extract by PID, language code, or track number from input

### Captions
Supported input caption formats: embedded (CEA-608/708), SCTE-27, DVB-Sub, Teletext, ARIB, SRT, TTML, WebVTT.
Supported output caption formats: embedded, burn-in, DVB-Sub, TTML, WebVTT, SCTE-27, SRT.
Caption conversion between formats is supported within a channel.

### Motion Graphics Overlays
- Static or animated graphics overlays (PNG images or HTML5 via Elemental Live)
- Activated/deactivated via schedule actions at specific timecodes or wall-clock times
- Supports follow-mode (overlay appears when input switches)

### SCTE-35 Ad Signaling
- Passthrough, replace, or generate SCTE-35 splice_insert and time_signal messages
- Upconvert SCTE-35 to SCTE-104 for broadcast workflows
- Used with MediaTailor for server-side ad insertion

### VPC Delivery
- MediaLive channels can be deployed inside a customer VPC
- Enables private connectivity to on-premises sources or downstream services
- Requires VPC input with ENIs in customer subnets

### Key Use Cases
- Live linear broadcast channel playout
- Live event encoding (sports, concerts, news)
- 24/7 live-to-VOD with archive output groups
- Contribution encoding for satellite uplink
- OTT live streaming with MediaPackage and CloudFront

---

## AWS Elemental MediaConvert

### Purpose
MediaConvert is a file-based video transcoding service for VOD workflows. It processes media files stored in S3 (or accessible via HTTP/HTTPS) and outputs transcoded files to S3. Designed for high throughput, broad format support, and professional broadcast features.

### Core Concepts

| Concept | Description |
|---|---|
| Job | Single transcoding request. Specifies input(s), output groups, and settings. |
| Job template | Reusable job configuration. Applied to a job to pre-populate settings. |
| Output preset | Reusable output settings (codec, bitrate, resolution) applied to a single output within a job. |
| Queue | Controls job concurrency and priority. On-demand (default) or Reserved. |
| Input clipping | Transcode only a portion of the input using timecode-based in/out points. |

### Queue Types

| Queue type | Description |
|---|---|
| On-demand | Pay-per-minute of output video processed. Shared resource pool. |
| Reserved | Commit to 12-month pricing for a fixed number of parallel slots. Lower per-minute cost for high throughput workloads. |

### Input Formats
Wide format support including: MP4, MOV, MXF, AVI, WMV, MPEG-2 TS, IMF (Interoperable Master Format), XDCAM, ProRes, DNxHR/DNxHD, R3D, and more. Inputs sourced from S3, HTTP/HTTPS, or other accessible URLs.

### Output Groups

| Output group | Use case |
|---|---|
| HLS | Adaptive bitrate for Apple devices and broad OTT support |
| DASH ISO | MPEG-DASH; widely supported by Android, smart TVs |
| CMAF | Common Media Application Format; single package for HLS/DASH |
| MS Smooth | Microsoft Smooth Streaming |
| File group | Single output file per output (MP4, MXF, MO V, etc.) |

### Video Codecs (Output)
H.264 (AVC), H.265 (HEVC), AV1, VP9, MPEG-2, ProRes, DNxHR/DNxHD, XDCAM. Supports 8-bit and 10-bit color depth.

### Audio Mixing
- Up to 24 audio tracks per output
- Audio normalization: CALM Act, EBU R128, ITU-R BS.1770
- Audio remix: remap multi-channel input to different output channel layouts
- Codecs: AAC, MP3, AC-3, E-AC-3, PCM, FLAC, Vorbis, Opus

### Captions Formats
Input: CEA-608/708 embedded, SCTE-20, SCC, TTML, DFXP, STL, SRT, SMI, WebVTT, IMSC, Teletext.
Output: Embedded, burn-in, SCC, SRT, TTML, WebVTT, IMSC, DVB-Sub.

### HDR Support
| Standard | Support |
|---|---|
| HDR10 | Static HDR metadata passthrough and conversion |
| HDR10+ | Dynamic HDR metadata |
| HLG | Hybrid Log-Gamma |
| Dolby Vision | Profile 5 and 8.1 |
| SDR-to-HDR tone mapping | Supported via color space conversion |

### Accelerated Transcoding
- Available for eligible jobs (minimum duration and complexity thresholds apply)
- Splits the video into fragments and processes them in parallel
- Modes: **ENABLED** (use acceleration if eligible), **PREFERRED** (fall back if not eligible), **DISABLED**
- Dramatically reduces turnaround time for long-form content

### Input Clipping & Stitch
- Define multiple input clips from the same or different source files
- Clips are stitched in sequence to produce a single output
- Supports audio-only inputs mixed with video inputs

### Pricing Model
Billed per minute of output video processed. Rate varies by output resolution tier (SD, HD, UHD/4K) and whether Advanced Audio, Advanced Captions, or reserved capacity is used.

---

## Amazon Elastic Transcoder (Legacy)

### Purpose
Elastic Transcoder is an older managed media transcoding service. It converts media files stored in S3 to consumer playback formats. **For new workloads, AWS recommends AWS Elemental MediaConvert**, which offers broader format support, professional features, and better performance.

### Core Concepts

| Concept | Description |
|---|---|
| Pipeline | Processing queue that manages transcoding jobs. Associated with input and output S3 buckets and an IAM role. |
| Job | Transcoding request: specifies input object key, output key, preset, and optional settings. |
| Preset | Output format template (container, codec, bitrate, resolution). AWS provides system presets; custom presets can be created. |

### Key Limitations vs MediaConvert
- No HDR support
- Limited caption format support
- No accelerated transcoding
- No IMF or professional format input support
- Simpler audio capabilities
- Lower maximum output bitrates

### When to Use
Only for maintaining existing pipelines that cannot be migrated. All new VOD transcoding workloads should use MediaConvert.

### Pricing
Per-minute pricing based on output resolution (SD ≤720p, HD >720p).
