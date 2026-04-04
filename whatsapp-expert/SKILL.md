---
name: whatsapp-expert
description: >
  Comprehensive expert guide to WhatsApp — covers all consumer app features and
  the full WhatsApp Business Platform. Use when users ask about:
  (1) Using WhatsApp: messaging, calls, groups, communities, channels, status,
      disappearing messages, privacy settings, web/desktop, Meta AI integration
  (2) WhatsApp Business App (free): business profiles, catalogs, quick replies,
      labels, automated messages, broadcasts for small businesses
  (3) WhatsApp Business Platform (Cloud API): sending messages, receiving webhooks,
      message templates, interactive messages, WhatsApp Flows, media handling
  (4) Message templates (HSM): categories, approval, variables, buttons, Flows
  (5) Webhooks: setup, payload structure, security, inbound message handling
  (6) Pricing and tiers: per-message pricing model, messaging tiers, quality ratings,
      official business account (green checkmark), business verification
  (7) Developer setup: WABA structure, Cloud API vs On-Premises, BSPs, Embedded Signup,
      opt-in requirements, phone number management
  Also triggers on: "WhatsApp API", "WABA", "WhatsApp Cloud API", "WhatsApp Business",
  "send WhatsApp message programmatically", "WhatsApp template", "WhatsApp webhook",
  "WhatsApp chatbot", "HSM message", "WhatsApp Business Platform"
---

# WhatsApp Expert

## Quick Navigation

| Task | Reference File |
|---|---|
| Consumer app features (messaging, calls, groups, channels, status, privacy) | [consumer-features.md](references/consumer-features.md) |
| WhatsApp Business App — free app for small businesses | [business-app.md](references/business-app.md) |
| Cloud API setup, sending messages, interactive messages, media, Flows | [cloud-api.md](references/cloud-api.md) |
| Message templates (HSM) — categories, approval, variables, buttons | [templates.md](references/templates.md) |
| Webhooks — setup, payload structure, inbound handling, security | [webhooks.md](references/webhooks.md) |
| Pricing, messaging tiers, quality ratings, green checkmark | [pricing-tiers.md](references/pricing-tiers.md) |

---

## Platform Overview

```
WhatsApp Platform
├── Consumer App (2B+ users)
│   ├── Messaging (text, media, voice, location, contacts)
│   ├── Calls (voice/video, up to 32 participants)
│   ├── Groups (up to 1,024 members)
│   ├── Communities (groups of groups)
│   ├── Channels (one-way broadcast)
│   ├── Status/Stories (24-hour ephemeral)
│   └── Meta AI assistant
│
├── WhatsApp Business App (free, small businesses)
│   ├── Business profile + catalog (up to 500 items)
│   ├── Quick replies, labels, automated messages
│   └── Broadcast to 256 contacts at once
│
└── WhatsApp Business Platform (Cloud API)
    ├── Cloud API — Meta-hosted REST API (recommended)
    ├── On-Premises API — DEPRECATED (sunset Oct 23, 2025)
    ├── Message types: text, media, templates, interactive, Flows
    ├── Webhooks — inbound messages + delivery status
    └── WhatsApp Manager UI — templates, analytics, Flows builder
```

---

## Critical Facts (2026)

- **On-Premises API is dead** — fully sunset October 23, 2025; use Cloud API only
- **Pricing model changed July 1, 2025** — now per-message (not per-conversation)
- **Service messages are free** — replies within a 24-hour customer-initiated window
- **72-hour free window** — all message categories free after user clicks a Click-to-WhatsApp ad
- **Phone number can't be shared** — a number registered to the API cannot simultaneously run the Business App
- **Templates required for first contact** — can't send free-form messages outside a 24-hour session window
- **Opt-in is mandatory** — must collect explicit opt-in before sending marketing/utility messages

---

## Account Hierarchy

```
Personal Facebook Account (admin)
  └── Meta Business Manager (business.facebook.com)
        └── WhatsApp Business Account (WABA)
              ├── Phone Numbers (up to 20 per WABA; default: 2)
              ├── Message Templates (up to 250 per WABA)
              └── Meta App (developers.facebook.com → WhatsApp product)
                    └── System User with permanent access token
```

Key IDs used in every API call:
- **`PHONE_NUMBER_ID`** — the sending phone number's internal ID
- **`WABA_ID`** — the WhatsApp Business Account ID

---

## Loading the Right Reference

- **"How do I use WhatsApp groups / communities / channels?"** → `consumer-features.md`
- **"Set up WhatsApp Business App for my small business"** → `business-app.md`
- **"Send my first WhatsApp message via API" / "Set up Cloud API"** → `cloud-api.md`
- **"Create or approve a message template"** → `templates.md`
- **"Set up webhooks / handle inbound messages"** → `webhooks.md`
- **"Messaging tiers / quality rating / pricing / green checkmark"** → `pricing-tiers.md`
- **Multi-topic question** → load the 2 most relevant reference files
