# AWS Streaming, Interactive Video & Render — Capabilities Reference

For CLI commands, see [streaming-ivs-cli.md](streaming-ivs-cli.md).

---

## Services in this namespace

| Service | Purpose | Workload type |
|---|---|---|
| Amazon IVS | Managed low-latency live streaming | Live streaming / interactive |
| Amazon Kinesis Video Streams | Live video ingestion from devices; WebRTC | IoT / surveillance / ML |
| Amazon Nimble Studio | Cloud-based content production workstations | VFX / animation / post-production |
| AWS Deadline Cloud | Managed cloud render farm for VFX, animation, and 3D rendering | Batch rendering / compute |

---

## Amazon IVS (Interactive Video Service)

### Purpose
Amazon IVS is a managed live streaming service for interactive applications. It provides low-latency video delivery at global scale without requiring encoder infrastructure management. IVS is optimized for interactive live streaming — gaming, talk shows, e-commerce — where viewer interaction synchronized with video is critical.

### Channel Types

| Channel type | Ingest | Latency | Use case |
|---|---|---|---|
| BASIC | RTMPS (push) | ~5s (low-latency) | Simple streaming, lower cost, limited features |
| STANDARD | RTMPS (push) | ~5s (low-latency) | Full feature set, timed metadata, higher resolutions |
| ADVANCED_SD | RTMPS (push) | ~5s | SD output, advanced features |
| ADVANCED_HD | RTMPS (push) | ~5s | HD output, advanced features |

### Core Concepts

| Concept | Description |
|---|---|
| Channel | The top-level IVS resource. Has an ingest endpoint and a playback URL. |
| Stream key | Secret key embedded in the RTMPS stream URL used to authenticate the encoder. |
| Playback URL | HLS URL distributed to viewers. Delivered globally via IVS CDN. |
| Recording configuration | Automatically records streams to S3 in HLS format as they occur. |
| Timed metadata | Arbitrary metadata inserted into the stream at specific times, synchronized with playback for interactive experiences. |
| Playback restriction policy | Restricts playback by allowed origin domains and/or geographic regions (countries). |
| Stream session | A single continuous live stream event on a channel. Automatically logged with start/end times. |

### Ingest
- Protocol: RTMPS (RTMP over TLS), port 443
- Ingest endpoint is per-channel: `rtmps://<channel-ingest-endpoint>:443/app/<stream-key>`
- Compatible with OBS Studio, Streamlabs, XSplit, hardware encoders
- Recommended encoder settings: H.264, 6 Mbps max bitrate for STANDARD channels

### Playback
- HLS playback URL provided per channel
- IVS manages CDN distribution globally (no CloudFront configuration needed)
- Playback SDKs available for Web (HTML5), iOS, Android
- The IVS Player SDK enables timed metadata callback integration with application UI

### Latency Modes
| Mode | Approximate latency | Description |
|---|---|---|
| Low latency | ~5 seconds | Default; HLS-based, global CDN delivery |
| Real-time (Stages) | <300 ms | WebRTC-based; up to 12 participants; for interactive co-streaming |

### Timed Metadata
- Inserted into the live stream by the broadcaster or server-side application
- Delivered to viewers synchronized to the video frame via the IVS Player SDK
- Use cases: interactive polls, product overlays in e-commerce, quiz answers, synchronized UI updates

### Recording to S3
- Attach a recording configuration to a channel
- All streams on the channel are automatically recorded to a specified S3 bucket in HLS format
- Thumbnail generation at configurable intervals
- Post-recording S3 renditions can be served as VOD

### Real-Time Streaming (Stages)
- WebRTC-based co-streaming for <300ms latency
- A Stage hosts up to 12 participants who can publish and subscribe to each other's audio/video
- Participants join via a short-lived participant token (JWT)
- Server-side composition: combine participant streams into a single composite stream for broadcast
- Use cases: interactive talk shows, co-gaming, audience-on-screen experiences

### IVS Chat
- Managed chat rooms tightly integrated with IVS channels
- Chat message delivery synchronized with stream playback
- Moderation: message review, message delete, disconnect user
- Chat tokens issued server-side for authenticated users
- Configurable message rate limits and retention

### Key Use Cases
- Interactive live streaming for gaming and esports
- Live shopping / e-commerce with synchronized product overlays
- Fitness and wellness live classes with viewer engagement
- Live trivia and quiz shows with timed metadata events
- Talk shows and panel discussions with real-time audience (Stages)

---

## Amazon Kinesis Video Streams

### Purpose
Kinesis Video Streams ingests live video from connected devices (cameras, smartphones, drones, industrial sensors) into AWS for processing, storage, playback, and machine learning analysis. It manages the complexity of streaming protocols, infrastructure scaling, and durable storage.

### Core Concepts

| Concept | Description |
|---|---|
| Stream | The primary resource. A named channel for a single video (or audio/data) source. |
| Producer SDK | Client library for devices to push video into a stream (C++, Java, Android). |
| Fragment | A self-contained unit of video data (typically 1–10 seconds) stored in the stream. |
| Retention period | Duration (hours) that stream data is retained before automatic deletion. 0 = no retention. |
| HLS playback | Retrieve historical or live video from a stream as an HLS manifest for browser/player playback. |
| DASH playback | Same as HLS but returns an MPEG-DASH manifest. |
| WebRTC | Two-way low-latency video via a signaling channel; peer-to-peer or via TURN relay. |
| Signaling channel | WebRTC signaling resource; manages offer/answer exchange and ICE candidate gathering. |
| Image extraction | Extract JPEG frames from a stream on a schedule or per fragment for ML inference. |

### Producer SDKs
| SDK | Platform |
|---|---|
| C++ Producer SDK | Linux, macOS, Windows, embedded Linux |
| Java Producer SDK | Java/Android applications |
| Android Producer SDK | Android devices |
| GStreamer plugin | Linux pipeline-based video sources (GStreamer KVS sink plugin) |

### Ingest Protocols
- **Custom streaming API** via Producer SDK (recommended): HTTPS/TLS streaming using `PutMedia` API
- **WebRTC ingest**: via signaling channel for two-way or one-way WebRTC streaming

### Playback Modes

| Mode | API | Use case |
|---|---|---|
| LIVE | GetHLSStreamingSessionURL (LIVE) | View latest ingested content as HLS (~3s latency) |
| LIVE_REPLAY | GetHLSStreamingSessionURL (LIVE_REPLAY) | Start at a historical point, continue to live |
| ON_DEMAND | GetHLSStreamingSessionURL (ON_DEMAND) | Review archived footage |
| WebRTC | Two-way via signaling channel | Low-latency two-way video (<500ms) |

### WebRTC
- Signaling channels handle SDP offer/answer and ICE candidate exchange
- Peer-to-peer mode: direct media path between camera and viewer
- TURN relay: media routed through AWS relay when P2P not possible
- One-to-one or one-to-many fan-out via the Master/Viewer model
- Use cases: remote monitoring with two-way audio, doorbell cameras, remote assistance

### Image Extraction
- Configure a stream to extract JPEG frames at a defined sampling interval
- Frames published to S3 or delivered via callback
- Enables integration with Amazon Rekognition Video for real-time object/face detection
- Use cases: smart cameras, retail analytics, safety monitoring

### Archival and Retention
- Fragments stored durably in the stream for the configured retention period
- Minimum retention: 1 hour; maximum: 10 years (87,600 hours)
- Retention period 0 = no archival (live only)
- Stored fragments accessible for on-demand HLS/DASH playback and GetMedia/GetMediaForFragmentList API

### Key Use Cases
- IoT and connected camera video ingestion
- Smart home security cameras with cloud recording and remote viewing
- Industrial equipment monitoring with ML-based anomaly detection
- Two-way video for telehealth or remote support
- Drone and mobile device video capture at scale

---

## Amazon Nimble Studio

### Purpose
Nimble Studio provides cloud-based creative workstations and shared file systems for VFX, animation, and media production teams. It enables production studios to burst capacity to the cloud without shipping hardware, giving artists access to GPU-accelerated workstations with professional software from any location.

### Core Concepts

| Concept | Description |
|---|---|
| Studio | The top-level resource in Nimble Studio. Represents a production organization. Contains all other resources. |
| Launch profile | Defines a workstation configuration: streaming image, instance type, shared file systems, and EC2 subnet. Artists connect using a launch profile. |
| Streaming image | An Amazon Machine Image (AMI) pre-configured with creative software (DCC tools, codecs, rendering agents). Custom AMIs can be created and registered. |
| Streaming session | An active workstation session. An artist streams the workstation desktop over the network to their local device using the Nimble Studio portal. |
| Shared file system | An Amazon FSx for Lustre or FSx for Windows file system attached to streaming sessions for shared project assets. |
| Studio component | A reusable configuration block (shared file system, AD/LDAP configuration, license server, custom script) associated with launch profiles. |

### Workstation Streaming
- Artists access workstations via the Nimble Studio portal (browser or Nimble application)
- Streaming protocol: NICE DCV for high-quality, GPU-accelerated remote desktop delivery
- Supports pen tablets, color-accurate displays, and high-resolution streaming
- Instance types: GPU instances (G4, G5) for GPU-accelerated DCC tools; compute instances for CPU rendering

### Streaming Images
- AWS-provided base images for Amazon Linux 2 and Windows Server
- Custom images: build on base images, install DCC tools (Autodesk Maya, Houdini, Nuke, Blender, etc.), rendering agents (Arnold, V-Ray, RenderMan), codecs, and plugins
- Images registered to the studio; referenced by launch profiles
- Regular image updates via SSM automation or manual process

### Shared File Systems
- Amazon FSx for Lustre: high-throughput parallel file system for Linux workstations; optimal for large VFX project files
- Amazon FSx for Windows File Server: SMB-based shared storage for Windows workstations
- File systems linked to S3 buckets (FSx for Lustre) for asset interchange
- Mounted automatically when an artist starts a streaming session from a launch profile

### Launch Profiles
- Define the complete workstation environment for a group of artists or a production phase
- Specify: streaming image, EC2 instance type family, volume size, shared file systems, VPC subnets
- Multiple launch profiles in a studio (e.g., compositing profile, rendering profile, editorial profile)
- Access controlled via IAM and Nimble Studio accept/reject mechanisms

### Identity Integration
- Integrates with AWS IAM Identity Center (SSO) for artist authentication
- Active Directory or LDAP integration via studio component for file system permissions and software licensing

### Key Use Cases
- VFX and animation production workstations in the cloud
- Remote and distributed production teams
- Burst capacity for deadline-driven production crunch
- Cloud rendering farm management alongside artist workstations
- Secure content production without physical hardware shipping

---

## AWS Deadline Cloud

### Purpose
AWS Deadline Cloud is a managed cloud-based render farm service for VFX, animation, and 3D rendering workloads. It provides fully managed, auto-scaling compute fleets that process rendering jobs without requiring studios to provision or manage EC2 infrastructure. Deadline Cloud is the successor to Thinkbox Deadline and provides a migration path for existing Deadline on-premises farms.

### Core Concepts

| Concept | Description |
|---|---|
| Farm | The top-level Deadline Cloud resource. Represents a rendering organization or facility. Contains queues and fleets. |
| Queue | A named queue that receives and prioritizes rendering jobs. Jobs submitted to a queue are dispatched to associated fleets. |
| Fleet | A pool of compute workers that process jobs from associated queues. Two types: service-managed and customer-managed. |
| Job | A single rendering workload submitted to a queue. Defined by a job bundle; broken into steps and tasks. |
| Job Bundle | A portable job template combining a job template file (YAML) and associated asset references. The unit of job submission. |
| Job Attachment | Automatic asset management via S3. Input files are uploaded to S3 before job submission; output files are downloaded after task completion. Managed transparently by the client libraries. |
| Step | A logical phase within a job (e.g., rendering, compositing, encoding). Steps can depend on each other. |
| Task | The smallest unit of work; a single parameter combination within a step (e.g., one frame or frame range). |
| Worker | A single compute instance within a fleet that executes tasks. Workers check out tasks, run them, and report results. |
| Deadline Cloud Monitor | A desktop application (Windows and macOS) for artists and TDs to monitor farms, queues, jobs, and workers without using the AWS Console. |
| Budget | A spend limit applied to a farm. When the budget maximum is reached, Deadline Cloud stops scaling new workers to prevent cost overruns. |
| Queue-Fleet Association | A join resource that links a queue to a fleet, specifying which fleets process jobs from which queues. A queue can be associated with multiple fleets; priority and limits are set per association. |

### Service-Managed Fleet vs Customer-Managed Fleet

| Attribute | Service-Managed Fleet | Customer-Managed Fleet |
|---|---|---|
| Infrastructure management | AWS manages EC2 lifecycle, scaling, and patching | Customer manages EC2 instances and Auto Scaling groups |
| Worker software | Installed and updated automatically by the service | Customer installs and updates the Deadline Cloud worker agent |
| Instance selection | Flexible: specify vCPU/memory/GPU ranges; AWS picks instance types | Customer specifies exact instance types in Auto Scaling group |
| Scaling | Automatic; scales to zero when idle | Customer-controlled via Auto Scaling group policies |
| Spot support | Yes; AWS handles Spot interruptions and replacement | Yes; customer configures Spot in the Auto Scaling group |
| Use case | Fully managed, minimal ops overhead | Existing EC2 infrastructure, specialized hardware, on-premises hybrid |

### Key Features

- **Automatic scaling**: service-managed fleets scale worker count up and down based on queue depth; scales to zero when no jobs are pending, eliminating idle compute costs
- **Job prioritization**: queue priority settings and per-job priority values control dispatch order; higher-priority jobs preempt lower-priority tasks
- **Queue policies**: configure maximum worker count, minimum worker count, and fleet associations per queue to control resource allocation across productions
- **Resource tagging**: farms, queues, fleets, and jobs support AWS resource tags for cost allocation and access control
- **Deadline Cloud Monitor**: standalone desktop application for monitoring and managing all farm resources without requiring AWS Console access; targeted at artists and render wranglers
- **Submitter plugins**: `deadline-cloud-for-*` open-source plugins integrate DCC tools directly with Deadline Cloud job submission — available for Maya, Blender, Nuke, Cinema 4D, Houdini, 3ds Max, and others
- **Job attachments (S3 auto-sync)**: the Deadline Cloud client library automatically hashes and uploads input assets to S3 before submission and downloads outputs after task completion, with deduplication to avoid redundant transfers
- **Flexible instance selection**: service-managed fleets accept capability-based instance requirements (vCPU range, memory range, GPU count, OS) rather than hard-coded instance types, enabling Spot diversification across many instance families

### Integration

| Integration | Description |
|---|---|
| Amazon S3 | Job attachments use S3 as the asset staging area; input files uploaded pre-job, output files downloaded post-task |
| Amazon Nimble Studio | Deadline Cloud workers can be deployed within the same VPC as Nimble Studio for shared file system access (FSx for Lustre) |
| Thinkbox Deadline migration | Deadline Cloud provides a migration path from self-managed Thinkbox Deadline farms; job bundles use the same OpenJD (Open Job Description) specification |
| IAM roles for workers | Service-managed fleet workers assume an IAM role for S3 access and Deadline Cloud API calls; customer-managed workers use an instance profile attached to the EC2 Auto Scaling group |
| AWS License Manager | License tracking for commercial DCC tool licenses used on render workers |
