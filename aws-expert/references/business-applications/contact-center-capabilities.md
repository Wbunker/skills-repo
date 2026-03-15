# AWS Contact Center — Capabilities Reference

For CLI commands, see [contact-center-cli.md](contact-center-cli.md).

## Amazon Connect

**Purpose**: Omnichannel cloud contact center service enabling voice, chat, and task-based customer interactions at scale, with built-in AI/ML capabilities.

### Core Concepts

| Concept | Description |
|---|---|
| **Instance** | An isolated Amazon Connect deployment; all resources (flows, queues, agents) belong to an instance |
| **Contact flow** | Visual IVR/routing logic builder; defines how contacts are handled end-to-end |
| **Queue** | Buffer holding contacts waiting to be connected to an agent; each queue has routing rules |
| **Routing profile** | Assigned to agents; specifies which queues they handle and the priority/delay per queue |
| **Agent** | A user configured to handle contacts; operates via the Connect agent workspace (CCP) |
| **Hours of operation** | Schedule defining when a queue is open; used in contact flows to branch by time |
| **Phone number** | DID or toll-free number claimed into an instance; associated with a contact flow |
| **Contact** | A single customer interaction (call, chat, or task); has a unique ContactId |
| **Contact attributes** | Key-value pairs attached to a contact; accessible in flows, Lambda, and reporting |

---

## Contact Flows (IVR / Routing Logic)

Contact flows are drag-and-drop visual editors with typed blocks:

| Block Type | Description |
|---|---|
| **Play prompt** | Text-to-speech or audio file playback |
| **Get customer input** | DTMF or speech recognition input with intent matching |
| **Set working queue** | Assign a queue before transferring to agent |
| **Check hours of operation** | Branch based on queue schedule |
| **Invoke AWS Lambda** | Call a Lambda function; return values become contact attributes |
| **Set contact attributes** | Store dynamic data on the contact |
| **Transfer to queue** | Place contact in a queue for agent connection |
| **Transfer to phone number** | Blind or supervised transfer to external number |
| **Disconnect** | End the contact |

Flow types: `CONTACT_FLOW` (inbound), `CUSTOMER_QUEUE` (hold experience), `CUSTOMER_HOLD`, `AGENT_HOLD`, `OUTBOUND_WHISPER`, `AGENT_WHISPER`, `TRANSFER_TO_AGENT`, `CUSTOMER_WHISPER`.

---

## Queues & Routing Profiles

| Feature | Description |
|---|---|
| **Queue metrics** | Real-time: contacts in queue, oldest contact, agents online/available/staffed |
| **Queue priority** | Contacts can be assigned a numeric priority; higher priority dequeued first |
| **Maximum contacts** | Cap on queued contacts; overflow branch in flow when exceeded |
| **Routing profile channels** | Each routing profile can specify voice, chat, and task concurrency limits per agent |
| **Queue-to-queue transfers** | Contacts can be transferred between queues preserving attributes |
| **Skills-based routing** | Route contacts to agents with specific skill tags (via routing profiles + queues) |

---

## Outbound Campaigns

Amazon Connect Outbound Campaigns enables high-volume predictive, progressive, and preview dialing:

| Mode | Description |
|---|---|
| **Predictive** | Algorithm dials ahead of available agents; minimizes wait time |
| **Progressive** | Dials one contact per available agent |
| **Preview** | Agent reviews contact info before initiating dial |
| **Agentless** | Automated message delivery without agent involvement |

Requires Amazon Connect Outbound Campaigns to be enabled; uses a campaign, a contact list (S3 CSV), and a connected outbound contact flow.

---

## Contact Lens for Amazon Connect

Real-time and post-call analytics powered by ML:

| Capability | Description |
|---|---|
| **Conversation analytics** | Transcription of voice/chat interactions; sentiment scoring per turn |
| **Sentiment analysis** | Per-turn and aggregate sentiment (positive/neutral/negative) for customer and agent |
| **Contact categorization** | Rules-based and ML-based tagging of contacts by topic/issue |
| **Sensitive data redaction** | Automatically redact PII (SSN, credit card, etc.) from transcripts and audio |
| **Alert rules** | Real-time notifications when keywords/phrases are spoken during a call |
| **Performance evaluation** | Scorecards to measure agent performance against defined criteria |
| **Transcript search** | Full-text search across all contact transcripts in the instance |

---

## Amazon Q in Connect (Agent Assist)

Formerly Amazon Connect Wisdom. Real-time AI-powered agent assistance:

| Feature | Description |
|---|---|
| **Real-time recommendations** | Detects customer intent during a call/chat and surfaces relevant articles/steps |
| **Knowledge bases** | Ingests content from S3, Salesforce, ServiceNow, Zendesk, SharePoint |
| **Generative AI answers** | LLM-generated responses grounded in knowledge base content (RAG) |
| **Manual search** | Agents can search the knowledge base directly from the agent workspace |
| **Quick responses** | Pre-defined canned responses agents can insert into chats |
| **Segments** | Filter knowledge articles by product, team, or customer type |

Requires an Amazon Q in Connect assistant and a knowledge base resource associated with the Connect instance.

---

## Amazon Connect Voice ID

Real-time caller authentication using voice biometrics:

| Concept | Description |
|---|---|
| **Domain** | Container for voice prints and fraud watchlists |
| **Enrollment** | Caller's voice print is captured and stored (requires ~30 seconds of speech) |
| **Authentication** | Compares live caller voice against stored voice print; returns score + decision |
| **Fraud detection** | Compares caller voice against a watchlist of known fraudulent voices |
| **Speaker status** | `ENROLLED`, `NOT_ENROLLED`, `OPTED_OUT` |
| **Authentication result** | `AUTHENTICATED`, `NOT_AUTHENTICATED`, `INCONCLUSIVE`, `NOT_ENROLLED` |

Integrates via the `SetVoiceIdAttributes` and `CheckVoiceId` flow blocks in the contact flow editor.

---

## Amazon Connect Customer Profiles

Unified customer record that aggregates data from CRM, ticketing, e-commerce, and call history:

| Feature | Description |
|---|---|
| **Domain** | Container for customer profile data; one domain per Connect instance |
| **Profile** | A unified record merging data from multiple sources for one customer |
| **Integrations** | Salesforce, ServiceNow, Marketo, Zendesk, S3 object type mappings |
| **Identity resolution** | ML-based matching to auto-merge duplicate profiles |
| **Object types** | Schema definitions for custom data objects (orders, tickets, etc.) |
| **Calculated attributes** | Derived metrics computed from profile data (e.g., total order value) |

Agents see Customer Profile in the agent workspace sidebar during a contact.

---

## Amazon Connect Cases

Tracks and manages customer issues across contacts:

| Feature | Description |
|---|---|
| **Case** | A record grouping multiple contacts related to a single customer issue |
| **Case template** | Defines required and optional fields for a case type |
| **Case field** | Typed attributes (text, number, date, boolean, single-select) on a case |
| **Case status** | Open, Pending, Closed (configurable) |
| **Related contacts** | Cases can link multiple voice/chat contacts and tasks |
| **Case event streams** | Publish case change events to Kinesis for downstream processing |

---

## Amazon Connect Tasks

Create, assign, route, and track agent work items that don't involve a live customer:

| Feature | Description |
|---|---|
| **Task** | A unit of work with a subject, description, due date, and contact attributes |
| **Task template** | Pre-defined task structure with required/optional fields |
| **Routing** | Tasks route through the same queues and routing profiles as voice/chat |
| **Integrations** | Create tasks automatically from Salesforce, Zendesk, EventBridge |
| **TaskID** | Each task has a unique ContactId; attributes accessible in flows |

---

## Amazon Connect Chat Channel

| Feature | Description |
|---|---|
| **Chat contact** | Asynchronous or synchronous text conversation |
| **Chat widget** | Embeddable JavaScript widget for websites |
| **Persistent chat** | Conversations persist across sessions so customers continue where they left off |
| **Message attachments** | Agents and customers can share files in chat |
| **Rich messaging** | Markdown, interactive messages (lists, buttons), receipt notifications |
| **Chatbot integration** | Integrate Amazon Lex bots in chat flows for automated responses |

---

## Amazon Connect Forecasting, Scheduling & Capacity Planning

Workforce Management (WFM) capabilities built into Connect:

| Feature | Description |
|---|---|
| **Forecasting** | ML-based prediction of contact volume and handle time by queue/channel |
| **Scheduling** | Generates agent schedules based on forecast demand and shift constraints |
| **Capacity planning** | Long-range headcount planning against forecasted demand |
| **Schedule adherence** | Real-time comparison of agent activity vs. scheduled activity |
| **Staffing groups** | Logical groupings of agents for scheduling purposes |

---

## Real-Time & Historical Metrics

| Report Type | Description |
|---|---|
| **Real-time metrics** | Live dashboard: contacts in queue, agents by state, service level |
| **Historical metrics** | Aggregated performance data; exported to S3 or queried via API |
| **Contact Trace Records (CTR)** | Per-contact JSON record with all attributes, timestamps, recordings metadata |
| **Agent event streams** | Kinesis stream of agent state change events (login, available, on-call, etc.) |
| **Contact event streams** | Kinesis stream of contact lifecycle events (initiated, connected, disconnected) |
| **Data streaming** | CTRs and agent events pushed to Kinesis Data Streams → S3/Redshift for BI |
