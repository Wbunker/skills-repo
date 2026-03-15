# AWS Elemental Delivery — Capabilities Reference

For CLI commands, see [elemental-delivery-cli.md](elemental-delivery-cli.md).

---

## Services in this namespace

| Service | Purpose | Workload type |
|---|---|---|
| AWS Elemental MediaPackage v2 | Origin packaging and DRM for live and VOD streams | Origin / packaging |
| AWS Elemental MediaStore | Low-latency origin storage for streaming | Origin storage |
| AWS Elemental MediaConnect | Reliable live video transport (contribution/distribution) | Transport |
| AWS Elemental MediaTailor | Server-side ad insertion and channel assembly | Monetization / playout |

---

## AWS Elemental MediaPackage v2

### Purpose
MediaPackage v2 is a video origination and packaging service. It receives encoded live streams (from MediaLive or other encoders) or VOD content and re-packages them into adaptive bitrate formats for delivery through a CDN. It handles origin logic, DRM encryption, time-delay, and harvest jobs (VOD clips from live archives).

### Core Concepts

| Concept | Description |
|---|---|
| Channel group | A logical grouping of channels. Shared ingest endpoints within the group. |
| Channel | Receives the encoded stream from the upstream encoder. Contains one or more origin endpoints. |
| Origin endpoint | Defines the packaging format (HLS, DASH, CMAF), segment duration, DRM settings, and CDN authorization for a specific audience/use case. |
| Harvest job | Records a live stream time-window to S3 as a VOD asset. |

### Supported Output Formats

| Format | Manifest type | Use case |
|---|---|---|
| HLS (fMP4 segments) | .m3u8 | Apple devices, broad OTT support |
| HLS (MPEG-2 TS segments) | .m3u8 | Legacy player compatibility |
| DASH | .mpd | Android, smart TVs, web |
| CMAF | .m3u8 / .mpd | Single-segment store for both HLS and DASH |

### DRM Support (SPEKE API)
MediaPackage v2 integrates with DRM providers through the SPEKE (Secure Packager and Encoder Key Exchange) v2.0 API.

- Supported DRM systems: FairPlay (iOS/Safari), Widevine (Chrome/Android), PlayReady (Windows/Xbox), ClearKey
- Multi-DRM: A single origin endpoint can serve multiple DRM systems from one stream
- Content key rotation: periodic key rotation for enhanced security
- SPEKE integration: MediaPackage calls a customer-configured SPEKE endpoint (typically a DRM vendor proxy) to obtain content keys

### Time-Delay (Live-to-Linear)
- Introduce a configurable delay (seconds to hours) between ingest and viewer delivery
- Commonly used for live-to-linear catchup, ad replacement, and live event rebroadcasting

### Origin Shield
- Optional caching layer between the CDN and MediaPackage origin
- Reduces origin load by aggregating manifest and segment requests before they reach MediaPackage
- Configured per origin endpoint via CDN authorization and CloudFront origin shield settings

### Harvest Jobs (VOD from Live)
- Record a time-bounded window of a live archive to an S3 bucket in HLS format
- Specified by start and end times (ISO 8601)
- Harvested output can be ingested into MediaConvert or served directly as VOD

### CDN Authorization
- Origin endpoints can require a secret authorization header validated against AWS Secrets Manager
- CloudFront distributions configured with the same secret can pull from MediaPackage
- Prevents direct origin access without CDN

### Key Use Cases
- OTT live streaming with multi-format delivery (HLS + DASH) from a single ingest
- Live-to-VOD clipping for highlights or catchup
- Subscription content with multi-DRM protection
- Time-shifted viewing (start-over, catch-up TV)

---

## AWS Elemental MediaStore

### Purpose
MediaStore is an origin storage service optimized for live and on-demand video streaming. It provides low-latency HTTP-based storage with consistent read/write performance suited to streaming media workloads, as an alternative to S3 for latency-sensitive origins.

### Core Concepts

| Concept | Description |
|---|---|
| Container | Top-level storage namespace. Each container has a unique HTTP endpoint. Similar to an S3 bucket but optimized for streaming. |
| Object | A media file (segment, manifest, etc.) stored in the container. Addressed by path within the container. |
| Access policy | IAM-style JSON resource policy controlling who can access the container. |
| CORS policy | Cross-Origin Resource Sharing rules for browser-based playback clients. |
| Lifecycle policy | Rules to automatically delete objects after a TTL (in seconds). Critical for keeping storage costs low in live workflows. |

### Key Features
- **Consistent low-latency**: Optimized for high PUT and GET throughput at low latency, unlike general-purpose S3
- **HTTP PUT/GET interface**: Compatible with standard HTTP clients; encoder outputs push directly via HTTP PUT
- **HLS-optimized delivery**: Designed for the small, frequent object writes of HLS segment workflows
- **Lifecycle management**: TTL-based automatic deletion prevents live segment accumulation
- **Metric-based monitoring**: CloudWatch metrics for request rates, latency, and errors per container

### Access Policies
Containers support resource-based IAM policies granting or denying access by principal, action, and condition. Example actions: `mediastore:GetObject`, `mediastore:PutObject`, `mediastore:DeleteObject`, `mediastore:ListItems`.

### CORS
Enables web players to fetch HLS manifests and segments directly from MediaStore over HTTP. Configured per container with allowed origins, methods, and headers.

### Typical Workflow
1. Upstream encoder (e.g., MediaLive) pushes HLS segments and manifests to MediaStore via HTTP PUT
2. CloudFront distribution points to the MediaStore container endpoint as origin
3. Players request content from CloudFront; CloudFront fetches from MediaStore on cache miss
4. Lifecycle policy deletes segments older than the DVR window

### When to Use vs S3
Use MediaStore when live ingest requires low-latency consistent PUT performance and immediate readback. Use S3 for archival, VOD assets, and workflows tolerant of S3's eventual-consistency behavior.

---

## AWS Elemental MediaConnect

### Purpose
MediaConnect provides reliable, high-quality transport of live video streams. It is used for contribution workflows (moving broadcast-quality video from source to cloud or between facilities) rather than delivery to viewers. MediaConnect replaces satellite uplink, leased-line circuits, and unreliable internet streaming for professional video transport.

### Core Concepts

| Concept | Description |
|---|---|
| Flow | The core resource. Represents a single live video transport stream with one source and one or more outputs. |
| Source | The ingest endpoint of a flow. Accepts video over SRT, Zixi, RTP/FEC, RTMP, CDI, or ST 2110. |
| Output | A destination that receives the transported stream. Each output can use a different protocol. |
| Entitlement | Grants another AWS account permission to subscribe to a flow as a source. Enables cross-account stream sharing. |
| Bridge | Connects on-premises video infrastructure to a MediaConnect flow in the cloud. Uses Ethernet connections to AWS Direct Connect or internet. |
| Gateway | On-premises component paired with a MediaConnect Bridge for on-prem/cloud interconnect. |

### Supported Transport Protocols

| Protocol | Use case |
|---|---|
| SRT (Secure Reliable Transport) | Reliable low-latency transport over public internet; error correction via ARQ |
| Zixi | Proprietary reliable transport; widely used in broadcast contribution |
| RTP (with FEC) | Real-time Transport Protocol with Forward Error Correction for unidirectional contribution |
| MPEG-2 TS over UDP | Simple transport; no error correction |
| AWS CDI (Cloud Digital Interface) | Uncompressed or lightly compressed video transport within AWS (inter-AZ, same region) |
| SMPTE ST 2110 | Professional IP video standard; via VPC/Direct Connect |
| NDI | Network Device Interface; for local IP production environments |
| RTMP | Less common for contribution; supported for compatibility |

### Entitlements (Cross-Account Sharing)
- Flow owner grants an entitlement to a subscriber AWS account
- Subscriber creates a new flow using the entitlement as its source
- Enables content distribution across accounts and organizations without file transfer
- Entitlements can specify encryption and subscriber limits

### Bridge (On-Prem ↔ Cloud)
- MediaConnect Bridge connects on-premises video sources or destinations to AWS
- Uses a Gateway appliance deployed on-premises (hardware or software)
- Video travels over Direct Connect or internet with SRT/Zixi reliability
- Enables hybrid cloud production workflows

### Encryption
- Source-level encryption: AES-128 or AES-256 using static key or Zixi/SPEKE
- Output-level encryption: same options
- Protects in-transit video from interception

### Key Use Cases
- Contribution from remote venues to broadcast facility or cloud production
- Distribution of a master stream to multiple facilities or CDN ingest points
- Cross-region or cross-account stream sharing for affiliate or partner distribution
- Replacing satellite uplinks or expensive leased lines with internet-based reliable transport

---

## AWS Elemental MediaTailor

### Purpose
MediaTailor performs server-side ad insertion (SSAI) and channel assembly for personalized video streams. It stitches ads from an Ad Decision Server (ADS) into live or VOD streams at the manifest level, delivering a seamless viewer experience without client-side ad blockers interfering.

### Core Concepts

| Concept | Description |
|---|---|
| Playback configuration | The primary resource. Associates an HLS/DASH content source, an ADS URL template, and CDN prefixes. |
| Ad decision server (ADS) | External VAST/VMAP ad server queried by MediaTailor for each session to determine which ads to insert. |
| Session | A viewer playback session. MediaTailor personalizes the manifest per session using ADS responses. |
| SCTE-35 markers | In-stream cue points signaling available ad breaks. MediaTailor reads these to know when to insert ads. |
| Channel assembly | Builds a linear channel by stitching together VOD assets on a schedule. No live encoder required. |
| Source location | A storage origin (S3, MediaStore, HTTP) containing VOD assets used in channel assembly. |
| Program | A single VOD asset scheduled on a channel assembly channel for a specific time slot. |
| Prefetch | Pre-fetches ADS responses before an ad break starts to reduce insertion latency. |

### Server-Side Ad Insertion (SSAI) Flow
1. Player requests a MediaTailor session initialization URL with session and targeting parameters
2. MediaTailor calls the ADS with the VAST/VMAP URL, substituting session variables
3. ADS returns a VAST/VMAP response with ad creative URLs
4. MediaTailor transcodes ad creatives (via MediaConvert) to match the content stream's bitrates (one-time, cached)
5. MediaTailor rewrites the HLS/DASH manifest to seamlessly replace ad break segments with ad segments
6. Player receives a single, personalized manifest and plays content + ads without gaps

### Supported Ad Standards
- VAST 2.0, 3.0, 4.x (Video Ad Serving Template)
- VMAP 1.0 (Video Multiple Ad Playlist) for pre-roll, mid-roll, post-roll definitions
- VPAID: Not supported (server-side only; VPAID requires client-side execution)

### Manifest Manipulation
- HLS and DASH manifests are rewritten in real-time per session
- MediaTailor injects or replaces segments corresponding to SCTE-35 ad break markers
- Supports ad slate (filler content when no ad is available)
- Supports ad pod filling (back-to-back ads within a break window)

### Prefetch
- MediaTailor can prefetch ADS responses before the ad break cue point is reached
- Reduces latency between SCTE-35 signal and first ad segment availability
- Configured with a prefetch window (how far ahead to fetch)

### Channel Assembly
- Create a 24/7 linear channel from VOD assets without a live encoder
- Define a schedule of programs (VOD assets) with start times
- MediaTailor handles transitions and looping
- SSAI applies to channel assembly streams just like live streams
- Supports recurring programs and filler content

### Reporting & Beacons
- MediaTailor fires IAB-standard tracking beacons (impression, first quartile, midpoint, third quartile, complete) on behalf of the player
- Server-side beaconing works even with ad-blocking clients
- Logs available via CloudWatch and Kinesis Data Firehose

### Key Use Cases
- OTT AVOD (ad-supported video on demand) monetization
- Live stream ad monetization with personalized targeted ads
- Building FAST (Free Ad-Supported Streaming TV) linear channels with channel assembly
- Replacing client-side ad SDKs with server-side insertion to defeat ad blockers
