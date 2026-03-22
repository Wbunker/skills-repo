# Azure Communication Services — Capabilities Reference
For CLI commands, see [communication-cli.md](communication-cli.md).

## Azure Communication Services (ACS)

**Purpose**: Cloud-based communication platform with developer-friendly APIs for embedding voice, video, chat, SMS, and email into any application — without building or managing communication infrastructure.

### Communication Channels

| Channel | Capabilities |
|---|---|
| **Email** | SMTP relay + marketing email; custom domains with DMARC/DKIM/SPF; high-volume transactional email |
| **SMS** | Send and receive SMS; toll-free and short code numbers; opt-out management (STOP/HELP keywords); US, Canada, UK, and international |
| **Voice (PSTN)** | Inbound and outbound PSTN calls; telephone numbers (direct dial, toll-free); Teams Direct Routing |
| **VoIP** | WebRTC-based voice calls via Calling SDK; browser, iOS, Android |
| **Video** | Group video calls up to 350 participants; rooms API for pre-configured sessions; recording |
| **Chat** | Real-time chat threads; read receipts; typing indicators; file attachments; push notifications |
| **UI Library** | Pre-built React and React Native UI components for calling and chat |

---

## Email

### Azure Communication Email

- **Azure Email Communication Service**: Managed email sending infrastructure (separate resource from ACS)
- **Azure Managed Domain**: `<unique>.azurecomm.net` — instant use, no DNS setup
- **Custom domain**: Bring your own domain with SPF, DKIM, and DMARC DNS records required
- **Sending limits**: Up to 100 emails/minute by default (increase via support ticket)
- **Attachments**: Up to 10 MB total
- **Tracking**: Delivery status (delivered, bounced, spam complaints) via webhook or polling

### Email Integration Patterns

```python
from azure.communication.email import EmailClient

client = EmailClient.from_connection_string(connection_string)
message = {
    "senderAddress": "no-reply@mycompany.azurecomm.net",
    "recipients": {"to": [{"address": "user@example.com"}]},
    "content": {
        "subject": "Welcome to our service",
        "plainText": "Hello, welcome!",
        "html": "<h1>Hello, welcome!</h1>"
    }
}
result = client.begin_send(message)
```

---

## SMS

### Key Capabilities

- **Toll-free numbers**: Quick setup; suitable for notifications and alerts
- **Short codes (5-6 digit)**: High throughput; requires approval; US/Canada only
- **10DLC (local numbers)**: Standard US business SMS; requires brand/campaign registration
- **International SMS**: Coverage in 200+ countries; pricing varies by destination
- **Two-way SMS**: Inbound SMS received as events (webhook or Event Grid)
- **Opt-out management**: Automatic STOP/UNSTOP/HELP handling (regulatory requirement)
- **Delivery receipts**: Webhook callback with delivered/failed status per message

---

## Voice and PSTN

### Telephone Numbers

| Type | Use Case |
|---|---|
| **Local numbers** | Geographic numbers (US/Canada/UK/etc.) for local presence |
| **Toll-free numbers** | 800/888/etc.; callers not charged; good for support lines |
| **Short codes** | 5-6 digit numbers for SMS only; high throughput |

### Calling SDK

- **Platforms**: Browser (Chrome, Edge, Safari), iOS, Android, Windows
- **Features**: Audio/video calls, screen sharing, call hold/transfer, DTMF, mute
- **CallAgent**: Manages calls; make/receive calls; push notifications for incoming
- **Call recording**: Server-side recording to Azure Blob Storage
- **Call automation**: Programmable call flows (IVR) via REST API — play audio, recognize speech, transfer

### Call Automation (Programmable Calls)

```python
# Outbound call with IVR
from azure.communication.callautomation import CallAutomationClient

client = CallAutomationClient.from_connection_string(conn_str)
call = client.create_call(
    target_participant="tel:+15551234567",
    callback_url="https://myapp.com/callback",
    call_intelligence_options={"cognitive_services_endpoint": "..."}
)
# Then in callback: play audio, recognize speech, branch on input, transfer to agent
```

---

## Video

### Rooms API

- **Rooms**: Pre-configured meeting rooms with defined participants and roles
- **Roles**: Presenter (can share screen, admit participants), Attendee (view only), Consumer
- **Valid lifetime**: Set start/end time for room; participants cannot join outside window
- **Recording**: Server-side recording + transcription to Azure Blob Storage

### Group Calling

- Up to 350 participants in a group call
- Browser-based via Calling SDK (no app install required)
- Video tile layout management in UI Library

---

## Chat

### Chat Thread

- Persistent message thread with participants
- **Messages**: Text, rich text, attachments (via Blob URL)
- **Events**: Message received, read receipt, typing indicator, participant added/removed
- **Push notifications**: Via ACS Notification service (push to mobile apps)
- **Storage**: Messages retained for 90 days (default); configurable

### Chat Integration

```javascript
import { ChatClient } from "@azure/communication-chat";
import { AzureCommunicationTokenCredential } from "@azure/communication-common";

const chatClient = new ChatClient(endpoint, new AzureCommunicationTokenCredential(userToken));
const threadClient = chatClient.getChatThreadClient(threadId);

await threadClient.sendMessage({ content: "Hello team!" });

// Real-time events
chatClient.startRealtimeNotifications();
chatClient.on("chatMessageReceived", (event) => {
    console.log(`Message: ${event.message}`);
});
```

---

## Identity and Access Tokens

- **ACS Users**: Create anonymous communication users (not tied to Entra ID)
- **Access tokens**: Short-lived JWT tokens scoped to specific capabilities (voip, chat)
- **Token refresh**: Tokens expire after 24 hours; application must refresh them
- **Entra ID users**: Map ACS communication user IDs to Entra ID identities for your own records

```python
from azure.communication.identity import CommunicationIdentityClient

identity_client = CommunicationIdentityClient.from_connection_string(conn_str)
user = identity_client.create_user()
token = identity_client.get_token(user, ["voip", "chat"])
# token.token is the JWT access token; token.expires_on is expiry
```

---

## Azure Relay (Hybrid Connections)

**Purpose**: Enable on-premises applications and services to be reachable from the cloud without opening firewall ports. Alternative to VPN for hybrid connectivity.

### Key Capabilities

- **Hybrid Connections**: WebSocket-based relay using standard HTTPS (443); works through NAT/firewalls
- **WCF Relay** (legacy): SOAP-based services; being retired — use Hybrid Connections for new work
- **No infrastructure changes**: On-premises listener initiates outbound HTTPS to Azure Relay; no inbound firewall rules
- **Use case**: Expose on-premises REST APIs, databases, or file servers to Azure-hosted applications

---

## Notification Hubs (Cross-platform Push)

**Purpose**: Send push notifications to millions of mobile devices across iOS (APNs), Android (FCM), Windows (WNS), and other platforms from a single API.

### Architecture Pattern

```
Backend API → Azure Notification Hubs → [APNs → iOS devices]
                                      → [FCM → Android devices]
                                      → [WNS → Windows devices]
```

### Key Features

| Feature | Details |
|---|---|
| **Scale** | 500M+ devices; millions of notifications/hour |
| **Tags** | Label registrations for targeting (userId, topic, region); Boolean tag expressions |
| **Templates** | Per-device payload format; send platform-agnostic body |
| **Registration management** | Client app registers device handle; backend manages tags |
| **Installation model** | Preferred over legacy registrations; supports templates and tags |
| **Telemetry** | Per-notification delivery counts, error breakdown by platform |
| **Scheduled push** | Send at future time |
| **Direct send** | Send to specific device handle (bypasses registrations) |

### Tiers

| Tier | Registrations | Pushes/month |
|---|---|---|
| **Free** | 500 | 1M |
| **Basic** | 200,000 | 10M |
| **Standard** | Unlimited | Unlimited |
