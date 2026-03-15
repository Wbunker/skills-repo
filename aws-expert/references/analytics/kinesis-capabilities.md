# AWS Kinesis — Capabilities Reference
For CLI commands, see [kinesis-cli.md](kinesis-cli.md).

## Amazon Kinesis Data Streams

**Purpose**: Collect and process large streams of data records in real time with sub-second put-to-get latency.

### Core Concepts

| Concept | Description |
|---|---|
| **Stream** | Ordered sequence of data records; durably stored and replicated across AZs |
| **Shard** | Unit of capacity; 1 MB/s write, 2 MB/s read; streams scale by adding/removing shards |
| **Record** | The unit of data: partition key + sequence number + data blob (up to 1 MB) |
| **Partition key** | String that determines which shard a record goes to (via MD5 hash) |
| **Sequence number** | Unique identifier assigned by Kinesis; determines ordering within a shard |
| **Retention period** | How long records are available: 24 hours (default) up to 365 days |
| **Consumer** | Application that reads records from a stream; multiple consumers can read same stream |

### Capacity Modes

| Mode | Description |
|---|---|
| **Provisioned** | Manually specify shard count; 1,000 records/s write per shard; $0.015/shard-hour |
| **On-demand** | Automatically scales capacity; no shard management; pay per GB in/out |

### Enhanced Fan-Out

Dedicated throughput per registered consumer: 2 MB/s per shard per consumer (vs. shared 2 MB/s total for polling consumers). Uses HTTP/2 push model via `SubscribeToShard`. Supports up to 20 registered consumers per stream.

### Kinesis Client Library (KCL)

Java library (also available for Python, Ruby, Node.js via MultiLangDaemon) that handles shard enumeration, checkpointing, lease coordination, and fault tolerance. Each KCL worker processes one or more shards; KCL automatically rebalances workers.

### Key Features

| Feature | Description |
|---|---|
| **Server-side encryption** | Encrypt records at rest using KMS key |
| **Enhanced monitoring** | Shard-level metrics: `IncomingBytes`, `OutgoingBytes`, `ReadProvisionedThroughputExceeded` |
| **Shard splitting/merging** | Increase capacity by splitting hot shards; reduce cost by merging cold shards |
| **Resource-based policy** | Control cross-account access to streams |

---

## Amazon Data Firehose

**Purpose**: Fully managed service for reliably loading real-time streaming data to destinations without writing delivery applications or managing infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Firehose stream** | The delivery pipeline; receives records from producers and delivers to a destination |
| **Record** | Unit of data sent to Firehose; maximum 1,000 KB |
| **Buffer** | Firehose buffers incoming data; flushes when Buffer Size (MB) or Buffer Interval (seconds) threshold is met |
| **Source** | Where data originates: Direct PUT, Kinesis Data Streams, MSK, or Waf |
| **Destination** | Where data is delivered |

### Destinations

| Destination | Notes |
|---|---|
| **Amazon S3** | Primary destination; supports prefix/suffix patterns, error output prefix |
| **Amazon Redshift** | Stages to S3 first, then issues a COPY command to load into Redshift |
| **Amazon OpenSearch Service** | Index documents in OpenSearch; optional S3 backup |
| **Amazon OpenSearch Serverless** | Index into serverless OpenSearch collection |
| **Apache Iceberg Tables** | Write to Iceberg tables in S3 via Glue Data Catalog |
| **Splunk** | Index events in Splunk; S3 backup for failed events |
| **HTTP endpoint** | Any custom HTTP endpoint (Datadog, New Relic, Coralogix, Dynatrace, MongoDB) |

### Key Features

| Feature | Description |
|---|---|
| **Lambda transformation** | Invoke a Lambda function to transform records before delivery; supports filtering |
| **Dynamic partitioning** | Extract values from record content (inline parsing or Lambda) to create S3 prefixes dynamically |
| **Format conversion** | Convert JSON input to Parquet or ORC before writing to S3; uses Glue Data Catalog schema |
| **Data compression** | GZIP, Snappy, ZIP, Hadoop-compatible SNAPPY for S3 destination |
| **Error output** | Failed records written to a separate S3 prefix for reprocessing |
| **Source record backup** | Optionally back up all source records to S3 regardless of transformation outcome |

---

## Amazon Kinesis Video Streams

**Purpose**: Securely ingest, store, and process video, audio, and time-serialized sensor data from connected devices. Automatically provisions and elastically scales infrastructure to handle millions of device streams.

### Core Concepts

| Concept | Description |
|---|---|
| **Stream** | The named channel for a single device feed; stores time-indexed media fragments |
| **Fragment** | Atomic unit of media data; a self-contained group of frames with timestamps |
| **Producer** | Device or application that ingests media into a stream (uses Producer SDK or GStreamer kvssink plugin) |
| **Consumer** | Application that reads archived or live media from a stream |
| **Data endpoint** | Per-stream endpoint used for PutMedia and GetMedia calls; obtained via `GetDataEndpoint` |
| **Retention period** | How long data is durably stored; 0 hours (no retention) to 87,600 hours (10 years) |

### Supported Data Types

Kinesis Video Streams is not limited to video. Supported data types include live video, audio, thermal imagery, depth data, RADAR data, and any time-serialized sensor data.

### Playback APIs

| API | Description |
|---|---|
| **GetMedia** | Retrieve live/real-time media fragments as a continuous stream |
| **PutMedia** | Ingest media from a producer; sends media fragments to the stream |
| **GetHLSStreamingSessionURL** | Generate a time-limited HLS URL for playback in standard video players and browsers |
| **GetDASHStreamingSessionURL** | Generate a time-limited MPEG-DASH URL for adaptive bitrate playback |
| **GetClip** | Retrieve a single MP4 clip from archived media for a specified time range |
| **GetMediaForFragmentList** | Retrieve media for a specific list of fragment numbers |
| **ListFragments** | List fragments in a stream filtered by time range or fragment numbers |

### WebRTC Support (Signaling Channels)

Kinesis Video Streams includes a fully managed WebRTC implementation for low-latency, two-way peer-to-peer streaming — no signaling or TURN servers to operate.

| Concept | Description |
|---|---|
| **Signaling channel** | AWS-managed WebRTC signaling service; connects a master (device/camera) to one or more viewers |
| **Master** | The device that streams media; connects to the signaling channel and waits for viewer offers |
| **Viewer** | Web or mobile client that connects to the master and receives the stream |
| **ICE / STUN / TURN** | AWS-managed infrastructure for NAT traversal and media relay; configured via `GetIceServerConfig` |
| **Single-master channel** | One master, up to 10 simultaneous viewers |

Typical WebRTC flow: `CreateSignalingChannel` → `GetSignalingChannelEndpoint` → SDK WebSocket handshake → `GetIceServerConfig` → peer connection established.

### Integration with Amazon Rekognition Video

Stream live video from Kinesis Video Streams directly to Rekognition Video for real-time face detection, activity recognition, and connected-home analysis without storing video first. Rekognition Video reads from the stream and returns results to a Kinesis Data Stream.

### Key Features

| Feature | Description |
|---|---|
| **Automatic encryption** | All data encrypted at rest with AWS-managed or customer-managed KMS keys |
| **Producer SDKs** | C, C++, Java, Python, Android SDKs; GStreamer plugin (kvssink) for RTSP cameras |
| **Image generation** | Extract JPEG/PNG images from streams on a schedule; delivered to S3 |
| **Time-indexed storage** | Retrieve media by producer or server timestamps, not arbitrary byte offsets |
