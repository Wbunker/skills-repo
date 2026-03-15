# AWS Messaging & Email — Capabilities Reference

For CLI commands, see [messaging-email-cli.md](messaging-email-cli.md).

## Amazon SES v2 (Simple Email Service)

**Purpose**: Scalable cloud email service for sending transactional, marketing, and bulk email with high deliverability.

### Core Concepts

| Concept | Description |
|---|---|
| **Identity** | A verified sending domain or email address; must be verified before sending |
| **DKIM** | DomainKeys Identified Mail; cryptographic signing to prove email authenticity |
| **DMARC** | Domain-based Message Authentication; policy specifying how to handle unauthenticated mail |
| **Configuration set** | Named group of rules applied to email sends; controls event publishing and tracking |
| **Dedicated IP** | IP address exclusively assigned to your account for sending (vs shared IP pool) |
| **Suppression list** | Account-level or global list of addresses that should not receive email |
| **Sending quota** | Maximum send rate and daily volume limits; increase via support request |

### Email Identities & Authentication

| Feature | Description |
|---|---|
| **Domain identity** | Verify ownership of a domain via DNS TXT records; enables sending from any address in domain |
| **Email address identity** | Verify a specific email address; simpler setup for low-volume use |
| **Easy DKIM** | SES generates 2048-bit RSA key pair; publishes CNAME records automatically |
| **BYODKIM** | Bring your own DKIM private key; 1024, 2048, or 4096-bit RSA or ED25519 |
| **DMARC enforcement** | Set `p=reject` or `p=quarantine` in DNS; SES honors receiving-side DMARC |
| **Custom MAIL FROM domain** | Use a subdomain (e.g., `bounce.example.com`) for bounce handling |

### Configuration Sets

Applied per send call via `ConfigurationSetName` parameter:

| Feature | Description |
|---|---|
| **Event destinations** | Publish send/delivery/bounce/complaint/open/click events to SNS, Kinesis Firehose, CloudWatch, EventBridge |
| **Sending pool** | Associate a dedicated IP pool with the configuration set |
| **Reputation metrics** | Track bounce and complaint rates per configuration set |
| **Suppression options** | Override account-level suppression at configuration set level |
| **TLS policy** | Require TLS for email delivery (`REQUIRE` or `OPTIONAL`) |

### Dedicated IPs

| Feature | Description |
|---|---|
| **Dedicated IP (Standard)** | Static IPs assigned to your account; manually managed reputation warming |
| **Dedicated IP (Managed)** | SES manages a pool of dedicated IPs and auto-warms them based on your volume |
| **IP warmup** | Gradually increase sending volume on a new IP to build reputation with ISPs |
| **IP pools** | Group dedicated IPs; assign pools to configuration sets |

### Virtual Deliverability Manager

ML-powered deliverability insights:

| Feature | Description |
|---|---|
| **Engagement metrics** | Open and click rates per domain and ISP |
| **Deliverability dashboard** | Health scores for sending domains and IPs |
| **Blacklist monitoring** | Alerts when sending IPs appear on major blocklists |
| **Recommendations** | Actionable suggestions for improving deliverability |

### Email Templates & Bulk Sends

| Feature | Description |
|---|---|
| **Templates** | Handlebars-style `{{variable}}` substitution in HTML/text email bodies |
| **Bulk send** | `SendBulkEmail` API sends one template to many recipients with per-recipient substitution data |
| **Subscription management** | Contact lists with topic preferences; unsubscribe links with one-click support |
| **Contact lists** | Named lists of email addresses with opt-in/opt-out tracking per topic |

### Email Receiving

| Feature | Description |
|---|---|
| **Receipt rules** | Ordered rule sets triggered on incoming email for a verified domain |
| **Actions** | S3 (store message), Lambda (process), SNS (notify), Bounce, WorkMail forwarding, Stop |
| **IP filter rules** | Block or allow incoming email from specific IP ranges |
| **MX record** | Point domain MX to the SES inbound SMTP endpoint to receive via SES |

---

## Amazon Pinpoint

**Purpose**: Multi-channel customer engagement platform for targeted campaigns, journeys, and transactional messaging across email, SMS, push, voice, and in-app channels.

### Core Concepts

| Concept | Description |
|---|---|
| **Project (App)** | Container for all Pinpoint resources; each project has a unique App ID |
| **Endpoint** | A destination to send messages to (device token, email address, phone number); tied to a user |
| **Segment** | A group of endpoints that match criteria; used to target campaigns and journeys |
| **Campaign** | A scheduled or triggered message to a segment |
| **Journey** | Multi-step automated workflow triggered by events with branching and wait states |
| **Template** | Reusable message content with variable substitution |
| **Channel** | A communication pathway: email, SMS, push notification, voice, in-app, custom |

### Segments

| Type | Description |
|---|---|
| **Dynamic segment** | Automatically recalculated based on endpoint attribute filters and demographics |
| **Imported segment** | Static list of endpoints uploaded as CSV or JSON from S3 |
| **Segment group** | Combine multiple segments with AND/OR/NOT logic |

### Campaigns

| Feature | Description |
|---|---|
| **Scheduled** | Send at a specific date/time; once or recurring on a schedule |
| **Event-triggered** | Fire when an endpoint records a specific event |
| **A/B testing** | Split audience into variants to test different message content or send times |
| **Holdout** | Reserve a percentage of the segment that does not receive the campaign (control group) |
| **Quiet hours** | Do not send outside configured time windows per timezone |
| **Message limits** | Cap on messages per endpoint per campaign and per day globally |

### Journeys

Multi-step customer lifecycle automation:

| Activity Type | Description |
|---|---|
| **Send message** | Deliver via any configured channel |
| **Wait** | Pause for a duration or until a specific date |
| **Yes/No split** | Branch based on segment membership or event |
| **Multivariate split** | Branch into up to 5 paths based on weighted random or condition |
| **Holdout** | Remove a percentage from the journey at a given step |
| **Random split** | Randomly split audience for A/B/n testing within a journey |
| **Event trigger** | Start or re-enter journey based on an event |
| **Contact center** | Transfer to Amazon Connect queue as a journey step |

### Channels

| Channel | Description |
|---|---|
| **Email** | Powered by SES; supports open/click tracking; requires verified identity |
| **SMS** | Long code, short code, or toll-free; supports two-way SMS; keyword management |
| **Push notifications** | APNs (iOS), FCM (Android), Baidu, ADM; transactional and campaign push |
| **Voice** | Outbound voice messages using text-to-speech; for OTP and notifications |
| **In-app** | Display messages inside mobile/web apps when user is active; supports banners, modals, carousels |
| **Custom channel** | Invoke a Lambda function or webhook as a channel; fully extensible |

### Analytics

| Metric | Description |
|---|---|
| **Campaign metrics** | Sends, deliveries, opens, clicks, unsubscribes, bounces, complaints per campaign |
| **Journey execution metrics** | Activities executed, participants per step, conversion rates |
| **Funnel analytics** | Track user progression through defined event sequences |
| **Revenue** | Attribute revenue events to campaigns/journeys |
| **App and endpoint analytics** | Daily/monthly active users, session count, retention cohorts |

### Transactional Messaging API

Send individual messages outside of campaigns:

| API | Use Case |
|---|---|
| `SendMessages` | Send a direct message to specific endpoints (email, SMS, push) |
| `SendOTPMessage` | Generate and send a one-time password via SMS or voice |
| `VerifyOTPMessage` | Validate the OTP entered by the user |
| `PhoneNumberValidate` | Validate and enrich a phone number (carrier, line type, timezone) |

---

## Amazon Chime SDK

**Purpose**: Embeddable real-time communications capabilities (meetings, messaging, telephony) integrated into custom applications.

### Chime SDK Meetings

| Concept | Description |
|---|---|
| **Meeting** | A real-time audio/video session; up to 250 attendees |
| **Attendee** | A participant in a meeting; has a unique join token |
| **MediaRegion** | AWS Region where the media server hosts the meeting |
| **Meeting features** | Audio/video/content sharing; attendee capabilities control who can unmute, share |
| **Meeting retention** | Meeting ends when all attendees leave or after 6 hours |
| **Transcription** | Real-time transcription via Amazon Transcribe; per-attendee or merged transcript |

### Chime SDK Media Pipelines

| Pipeline Type | Description |
|---|---|
| **Concatenation pipeline** | Merge recording artifacts from multiple sources into a single file |
| **Media capture pipeline** | Record meeting audio/video/content to S3 (per-attendee or composite) |
| **Media live connector** | Stream meeting content to Kinesis Video Streams or RTMP endpoint |
| **Media insights pipeline** | Real-time analytics via Amazon Transcribe, Voice Analytics, Kinesis Data Streams |

### Chime SDK Messaging

| Concept | Description |
|---|---|
| **App instance** | Container for messaging resources (channels, users) |
| **App instance user** | A user identity within a messaging app instance |
| **Channel** | A conversation space; standard (ordered) or elastic (high-volume) |
| **Channel message** | A message in a channel; supports attachments and metadata |
| **Channel flow** | Lambda processor that intercepts messages before or after delivery |
| **Push notifications** | Deliver message notifications via SNS to mobile devices |

### Chime SDK Voice (PSTN Audio)

| Concept | Description |
|---|---|
| **Voice Connector** | SIP trunking to/from the PSTN; supports inbound and outbound calling |
| **SIP media application (SMA)** | Serverless Lambda-based call control for programmable telephony |
| **SIP rule** | Routes incoming calls to an SMA or Voice Connector based on the dialed number |
| **Call leg** | One direction of a call; SMA can manipulate both legs independently |
| **PSTN audio features** | Call recording, DTMF, text-to-speech (Polly), call bridging, hold music |
| **Voice Connector streaming** | Stream call audio to Kinesis Video Streams for real-time processing |

---

## Amazon Chime

**Purpose**: Cloud communications service for online meetings, video conferencing, business calling, and team chat (distinct from Chime SDK, which provides developer APIs for embedding real-time communications into custom applications).

### Amazon Chime vs Chime SDK

| | Amazon Chime | Amazon Chime SDK |
|---|---|---|
| **Target user** | End users (employees, meeting participants) | Developers building custom applications |
| **Nature** | SaaS meeting and collaboration app | Developer APIs and client SDKs |
| **Use case** | Video meetings, team chat, business phone | Embed real-time comms into your own app |

### Core Concepts

| Concept | Description |
|---|---|
| **Meeting** | A video/audio conferencing session hosted in the Chime service |
| **Attendee** | A participant in a Chime meeting |
| **Channel** | A persistent messaging space for ongoing team conversations |
| **Channel Message** | A message posted within a channel; supports attachments and metadata |
| **App Instance** | Container for Chime Messaging resources (channels, users) |
| **SIP media application** | Serverless Lambda-based call control for programmable telephony |
| **Voice Connector** | SIP trunking service for PSTN origination and termination |
| **Phone Number** | A PSTN number provisioned through Chime for business calling |
| **User Account** | An individual Chime user identity within an organization |

### Voice Connector

| Feature | Description |
|---|---|
| **SIP trunking** | Connect on-premises PBX or SIP infrastructure to the PSTN via AWS |
| **PSTN origination** | Configure inbound call routing rules by priority and weight |
| **PSTN termination** | Configure outbound calling credentials and allowed CIDR ranges |
| **Kinesis Video Streams** | Stream call audio to Kinesis Video Streams for real-time processing or recording |

### Chime Messaging

| Feature | Description |
|---|---|
| **Persistent channels** | Channels retain message history; members can retrieve past messages |
| **Channel flows** | Lambda processors that intercept messages before or after delivery for moderation or enrichment |
| **Channel membership** | Manage which users belong to a channel; supports hidden membership |
| **Push notifications** | Deliver message notifications via SNS to mobile devices |

### Use Cases

- Video meetings and virtual conferences for business teams
- Team chat with persistent channel history
- Business phone system replacement using Voice Connector SIP trunking

---

## AWS End User Messaging

**Purpose**: Consolidated service for sending SMS, voice, and push notification messages to end users. Supersedes fragmented SMS capabilities that were spread across SNS and Pinpoint by providing a dedicated, purpose-built delivery infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Phone Pool** | A collection of origination identities (phone numbers) that share sending capacity and opt-out lists |
| **Origination Identity** | A number used to send messages: long code, toll-free number, short code, or 10DLC-registered number |
| **Destination Phone Number** | The end user phone number receiving the message |
| **Protect Configuration** | A set of rules restricting which destination countries or number types can receive messages |
| **Keyword** | A word a recipient can text back to trigger an automated response (e.g., STOP, HELP, INFO) |
| **Opted-Out Number** | A destination number that has opted out of messages and is blocked from future sends |
| **Registration** | A formal carrier compliance record — includes brand registration and campaign registration for 10DLC |

### SMS

| Feature | Description |
|---|---|
| **Transactional SMS** | Time-sensitive messages such as OTPs, alerts, and confirmations; higher delivery priority |
| **Promotional SMS** | Marketing or non-time-sensitive messages; subject to quiet hours and carrier filtering |
| **Delivery tiers** | Throughput and latency vary by origination type; short codes offer the highest throughput |
| **Two-way SMS** | Use keywords to receive inbound replies and route them to Lambda or other handlers |

### 10DLC Registration

| Step | Description |
|---|---|
| **Brand registration** | Register your company with The Campaign Registry (TCR) for US carrier compliance |
| **Campaign registration** | Describe the messaging use case (e.g., account notifications, marketing) and associate with a brand |
| **Number association** | Link 10DLC phone numbers to a registered campaign before sending |

### Protect Configuration

Restrict sending destinations to control compliance and cost:

| Feature | Description |
|---|---|
| **Country-level restriction** | Block or allow sending to specific countries |
| **Number type restriction** | Block specific destination number types (e.g., premium rate numbers) |
| **Account default** | A default protect configuration applied to all sends unless overridden at the pool level |

### Push Notifications

| Channel | Description |
|---|---|
| **APNs** | Apple Push Notification service for iOS devices |
| **FCM** | Firebase Cloud Messaging for Android devices |
| **ADM** | Amazon Device Messaging for Kindle and Fire devices |

### Service Positioning

| Comparison | Detail |
|---|---|
| **vs SNS mobile push** | End User Messaging is the dedicated service for programmatic messaging; SNS mobile push capabilities are being superseded |
| **vs Pinpoint** | End User Messaging handles delivery infrastructure (numbers, pools, carrier compliance); Pinpoint handles audience segmentation and campaign orchestration on top of that infrastructure |
