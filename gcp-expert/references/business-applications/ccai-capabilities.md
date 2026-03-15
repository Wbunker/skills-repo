# Contact Center AI (CCAI) — Capabilities

## Overview

**Contact Center AI (CCAI)** is Google Cloud's suite of AI services for contact centers. It combines conversational AI (Dialogflow), real-time agent assistance, post-call analytics, and a fully managed CCaaS platform.

| Component | Purpose | Audience |
|---|---|---|
| Dialogflow CX | Virtual agents / chatbots / IVR | Self-service automation |
| Dialogflow ES | Simple conversational agents (legacy) | Lightweight automation |
| CCAI Agent Assist | Real-time help for human agents | Human agent augmentation |
| CCAI Insights | Post-call analytics | QA, compliance, coaching |
| CCAI Platform | Full CCaaS (cloud contact center) | Replace legacy on-prem CC |

---

## Dialogflow CX

**Dialogflow CX** (Customer Experience) is Google's advanced conversational AI platform for building sophisticated virtual agents. It uses a state machine model rather than the intent-cascade model of Dialogflow ES.

### Core Architecture

**Agent**: the top-level resource; contains all conversational logic for a virtual agent

**Flows**: manage conversation segments; each flow has its own intents, entities, pages, and transition routes
- Default Start Flow: entry point for all conversations
- Flows enable modular design (e.g., `Billing Flow`, `Technical Support Flow`, `Account Management Flow`)

**Pages**: states within a flow; define what the agent says and what it waits for
- Each page has an **Entry fulfillment** (what the agent says when entering)
- **Form parameters**: slots to fill (e.g., account number, issue type)
- **Transition routes**: conditions/intents that move to another page

**Intents**: user's communicative goal (e.g., "I want to pay my bill", "Cancel my subscription")
- Training phrases: examples of how users express this intent
- Head intents vs supplemental intents (for sub-topics within a flow)
- Default system intents: `Default Welcome Intent`, `Default Negative Match Intent`

**Entities**: extract structured data from user input
- System entities: `@sys.date`, `@sys.number`, `@sys.email`, `@sys.phone-number`, `@sys.location`
- Custom entities: define your own (e.g., `@product-name`, `@plan-type`)
- Regexp entities: match patterns (e.g., account numbers)
- Fuzzy matching: handles typos and variations

**Fulfillment**: what happens when a route is triggered
- Static response (text, audio, rich content)
- Webhook call (call external API; dynamic responses)
- Parameter preset (set session parameters)
- Conditional responses (different text based on session state)

### Environments and Versioning

- **Versions**: snapshot of an agent's state at a point in time; create before releases
- **Environments**: named deployment targets (Development, Staging, Production)
- **Test cases**: scripted test conversations; regression test before deploying a new version

### Multi-Channel Support

- Web chat (Dialogflow CX Messenger)
- Telephony (PSTN via Telephony Integration: Genesys, Avaya, Cisco, CCAI Platform)
- Messaging (Twilio, Vonage, WhatsApp via integration)
- Google Assistant (via integration)

### Multi-Language

- Up to 50 languages per agent
- Language-specific training phrases and responses
- Automatic language detection based on session configuration

### Session and Context

- **Session parameters**: key-value pairs stored for the conversation session; accessed in fulfillment and conditions
- **No contexts**: Dialogflow CX does not use contexts (that is Dialogflow ES); state is managed via Pages and Flows

### Telephony and DTMF

- DTMF (touch tone) input supported for IVR use cases
- Speech adaptation for domain-specific vocabulary (brand names, product codes)
- SSML (Speech Synthesis Markup Language) for custom TTS output (pauses, emphasis, pronunciation)
- Barge-in: user can interrupt agent speech

---

## Dialogflow ES (Essentials)

**Dialogflow ES** is the original, simpler Dialogflow product. Still widely deployed but Dialogflow CX is the recommended path for new builds.

### Key Concepts

- **Intents**: map user input to a response; no flow/page structure
- **Entities**: structured data extraction (same as CX)
- **Contexts**: input/output contexts control intent activation scope; simulate conversation state
- **Fulfillment**: inline editor (deprecated) or webhook
- **Follow-up intents**: child intents triggered after a parent intent

### When to use ES vs CX

| Use Dialogflow ES | Use Dialogflow CX |
|---|---|
| Simple FAQ bot | Complex multi-turn conversations |
| Small number of intents (<50) | Large agent with 100s of intents |
| Single-flow conversation | Multi-flow, multi-topic agent |
| Low budget / free tier | Enterprise production agent |
| Migrating a legacy ES agent | New agent builds |

---

## CCAI Agent Assist

**Agent Assist** provides real-time AI suggestions to human contact center agents during live customer interactions.

### Features

**Smart Reply:**
- Suggests pre-approved responses to common customer questions
- Agents click to insert suggested replies into chat
- Reduces handle time; ensures consistent answers

**FAQ / Article Suggestions:**
- Knowledge base integration (upload articles, FAQs, manuals)
- Real-time surface of relevant articles based on conversation context
- Agent can reference or share article with customer

**Conversation Summarization:**
- Real-time summary of conversation so far
- Reduces after-call work (ACW); agent can copy summary into CRM notes

**Smart Compose (Agent-Facing):**
- Autocomplete suggestions as agent types
- Drafts responses using knowledge base and conversation context

**Integration:**
- Integrates with existing CCaaS platforms via SIPREC or agent desktop SDK
- CCAI Platform (Google's native CCaaS) has native Agent Assist integration
- Genesys, Avaya, NICE, Salesforce Service Cloud integrations available
- Agent desktop widget: overlay on top of existing CRM/ticketing tools

---

## CCAI Insights

**CCAI Insights** performs post-call analytics on recorded and transcribed conversations.

### Analysis Capabilities

| Capability | Description |
|---|---|
| Transcription | Speech-to-text transcription of call audio |
| Sentiment analysis | Customer and agent sentiment throughout call (positive/negative/neutral) |
| Entity detection | Extract products, account numbers, dates, locations from transcripts |
| Topic modeling | Automatically discover recurring topics across thousands of calls |
| Talk time ratio | Agent vs customer talk time; silence detection |
| Hold time analysis | Identify excessive hold times |
| Smart highlighters | Custom phrase detection (e.g., competitor names, compliance phrases, escalation language) |
| Agent coaching | Identify calls where agent deviated from best practices |
| Issue model | ML-trained model that categorizes calls by issue type |

### Conversation Labels

- Define custom labels for compliance, quality scoring, or business taxonomy
- Auto-label conversations using ML classifiers
- Manual labeling for training data

### Export to BigQuery

- Export all conversation metadata, transcripts, sentiment scores, labels to BigQuery
- Run SQL analytics across millions of conversations
- Build Looker dashboards for QA teams, operations, compliance reporting

---

## CCAI Platform

**CCAI Platform** (formerly Contact Center AI Platform) is Google's fully managed cloud contact center (CCaaS) solution.

### Components

- **Telephony**: PSTN connectivity; SIP trunking; global reach via Google's network
- **Routing engine**: skill-based routing, queue management, IVR flows
- **Virtual agent (Dialogflow CX)**: automated self-service for calls and chats
- **Agent desktop**: browser-based agent workspace with integrated Agent Assist
- **Supervisor tools**: real-time monitoring, whisper/barge, queue management
- **Workforce management**: scheduling, forecasting, adherence
- **Quality management**: call scoring, calibration, e-learning
- **Analytics dashboard**: real-time and historical reporting (powered by Looker)

### Differentiators

- Native integration of Dialogflow CX virtual agents with human agents (seamless escalation)
- Agent Assist built into every agent interaction
- Automatic transcription and CCAI Insights on all calls
- Google's global infrastructure for reliability and low latency

---

## Speaker ID

**Speaker ID** provides voice biometric authentication for contact center callers:
- Passive voice enrollment (during normal conversation)
- Active verification (say a passphrase)
- Fraud detection: identify known fraudsters' voice patterns
- Integration with Dialogflow CX via webhook fulfillment
- Available as a standalone API or integrated with CCAI Platform
