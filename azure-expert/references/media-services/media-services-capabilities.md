# Azure Media Services — Capabilities Reference
For CLI commands, see [media-services-cli.md](media-services-cli.md).

> **Important**: Azure Media Services (AMS) is being retired. Live streaming and encoding retirement: June 30, 2024 (encoding), September 30, 2025 (live). Microsoft recommends migrating encoding to FFmpeg-based solutions, live streaming to third-party providers + Azure CDN, and AI video analysis to Azure AI Video Indexer.

## Azure Media Services (AMS)

**Purpose**: Cloud-based media encoding, packaging, and streaming platform for video-on-demand (VOD) and live streaming workflows.

### Core Resources

| Resource | Description |
|---|---|
| **Media Services Account** | Top-level resource; linked to an Azure Storage account for media assets |
| **Asset** | Container for video/audio/image files stored in Azure Storage (one blob container per asset) |
| **Transform** | Reusable encoding pipeline definition; specifies one or more output presets |
| **Job** | Single execution of a Transform against an input Asset; produces output Asset(s) |
| **Streaming Endpoint** | Origin server for content delivery; packages encoded content (MPEG-DASH, HLS, Smooth Streaming) |
| **Streaming Locator** | URL generator for an Asset + Streaming Policy combination |
| **Streaming Policy** | Defines delivery protocol and encryption settings for streaming |
| **Content Key Policy** | Defines DRM/AES key delivery conditions (token validation, license restrictions) |
| **Live Event** | Receives live ingest feed and makes it available for live streaming |
| **Live Output** | Records live stream to an asset (DVR window) |

---

### Encoding: Transforms and Jobs

#### Built-in Presets

| Preset | Description |
|---|---|
| `AdaptiveStreaming` | Auto-generates multi-bitrate ladder based on input resolution; H.264/AAC; recommended |
| `H264MultipleBitrate1080p` | Fixed 8-bitrate H.264 ladder up to 1080p |
| `H264MultipleBitrate720p` | Fixed 6-bitrate H.264 ladder up to 720p |
| `H264MultipleBitrateSD` | Fixed 5-bitrate H.264 ladder, SD only |
| `H265AdaptiveStreaming` | Auto-generates multi-bitrate ladder using HEVC (H.265) |
| `AACGoodQualityAudio` | Audio-only encoding at 192 kbps AAC |
| `ContentAwareEncoding` | Analyzes content complexity per-scene; optimizes bitrate ladder (best quality/size ratio) |
| `ContentAwareEncodingExperimental` | Experimental version of content-aware encoding |

#### Custom Presets

- Define custom H.264, H.265, or AV1 encoding parameters (bitrate, resolution, keyframe interval, codec profile)
- Multiple output formats in a single job (HLS + DASH + smooth streaming)
- Thumbnail extraction, audio normalization, subclipping
- Overlay images and captions

#### Job States

`Queued` → `Scheduled` → `Processing` → `Finished` | `Error` | `Canceled`

---

### Streaming Endpoints

| Type | Description |
|---|---|
| **Standard** | Default; shared infrastructure; suitable for development and moderate traffic |
| **Premium** | Dedicated units; SLA-backed; required for high-scale production; pay per streaming unit |

- **Dynamic packaging**: Single MP4 asset delivered as MPEG-DASH, HLS, or Smooth Streaming on demand
- **Dynamic encryption**: Apply AES-128 or DRM at delivery time without re-encoding
- **CDN integration**: Built-in Azure CDN (Verizon Premium, Verizon Standard, Akamai); also works with third-party CDNs

---

### Live Streaming

#### Live Event Types

| Type | Description |
|---|---|
| **Pass-through (Basic)** | Ingest RTMP(S)/Smooth; no cloud transcoding; ingest stream passed directly to packaging |
| **Pass-through (Standard)** | Same as Basic but with higher SLA |
| **Live Encoding (Standard)** | Single-bitrate RTMP(S) ingest; cloud transcodes to multi-bitrate for adaptive streaming |
| **Live Encoding (Premium)** | Higher quality encoding; custom presets; 4K transcoding |

#### Live Streaming Flow

```
Encoder (OBS, vMix, hardware encoder)
  → RTMP(S) ingest to Live Event
  → Live Output (DVR window, records to Asset)
  → Streaming Endpoint (packages to HLS/DASH)
  → Azure CDN
  → Viewers (Web, Mobile, TV)
```

#### Low-Latency Live Streaming

- **LL-HLS** (Low-Latency HLS): 2–4 second glass-to-glass latency
- **LL-DASH**: Similar latency profile via CMAF chunked transfer
- Requires encoder support (e.g., Wirecast, OBS WHIP output)

---

### Content Protection (DRM)

| DRM | Platforms |
|---|---|
| **Microsoft PlayReady** | Windows, Xbox, some Smart TVs, Edge |
| **Google Widevine** | Chrome, Android, Chromecast, Firefox |
| **Apple FairPlay** | Safari, iOS, tvOS, macOS |
| **AES-128 Encryption** | Any player supporting AES-128 clear key (no DRM license needed) |

#### Content Key Policy

- Define token requirements (JWT or SWT) for license/key acquisition
- Set license restrictions: play count, duration, HD/SD restriction, output protection (HDCP)
- Multi-DRM: Single encrypted asset delivered with different DRM per client

---

## Azure Video Indexer (Azure AI Video Indexer)

**Purpose**: AI-powered video and audio analysis platform. Extract rich metadata and insights from media without writing ML code.

### AI Insights Extracted

| Category | Insights |
|---|---|
| **Speech** | Transcript (with timestamps), speaker diarization, closed captions (SRT, VTT, TXT) |
| **Vision** | Face detection and identification, shot detection, scene detection, labels (objects, animals, activities) |
| **Text** | OCR (on-screen text), named entities (people, locations, organizations, brands) |
| **Audio** | Audio effects (silence, laughter, crowd, music), language detection |
| **Sentiment** | Sentence-level sentiment (positive, neutral, negative) |
| **Topics** | IAB (Interactive Advertising Bureau) taxonomy topics |
| **Keywords** | Extracted keyphrases |

### Integration Modes

| Mode | Description |
|---|---|
| **Classic (Trial/Paid accounts)** | Standalone portal (`www.videoindexer.ai`); REST API; not ARM-integrated |
| **ARM-integrated** | `Microsoft.VideoIndexer` resource in Azure; Managed Identity auth; Bicep/ARM deployable |

### Key Capabilities

- **Widget embedding**: Drop-in video player and insights panel for web apps with a few lines of JavaScript
- **Azure OpenAI integration**: Generate video summaries and search across video archives using semantic search
- **Custom models**: Train custom person models (face recognition), brand models, language models
- **Multi-language**: Transcription in 50+ languages; multi-lingual video support
- **Searchable index**: Search across all indexed videos by keyword, face, label, brand name

### Use Cases

- Content moderation and NSFW detection
- Accessibility (auto-captioning)
- Content recommendation (topic/keyword extraction)
- Media archive search
- Sports analytics (shot detection, athlete identification)
- News media monitoring (brand/person mentions)
