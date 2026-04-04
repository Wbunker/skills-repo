---
name: facebook-expert
description: >
  Comprehensive guide to Facebook (Meta) — covers all website features and all developer APIs.
  Use when users ask about:
  (1) Using Facebook effectively: Feed, Profile, Stories, Reels, Facebook Live, Events, Marketplace, Groups, Pages, Dating, Gaming, Watch
  (2) Account management: privacy settings, security, 2FA, passkeys, off-Facebook activity, app permissions
  (3) Facebook for business: Pages, Meta Business Suite, Facebook Shop, organic content strategy
  (4) Facebook advertising: Ads Manager, campaign setup, targeting, audiences, ad formats, Pixel/CAPI, reporting
  (5) Developer APIs: Graph API (nodes/edges/fields, auth, tokens, permissions, rate limits), Marketing API (campaign management, Ads Insights, Custom Audiences, catalogs), Messenger Platform API (chatbots, webhooks, templates), WhatsApp Business Cloud API (messaging, templates, interactive messages)
  (6) Any question about how Meta/Facebook platforms work, best practices, or integration troubleshooting
---

# Facebook Expert

## Quick Navigation

| Task | Reference File |
|---|---|
| Using Facebook website features (Feed, Stories, Reels, Live, Events, Marketplace, Dating, Gaming) | [website-features.md](references/website-features.md) |
| Managing Pages, Groups, or Meta Business Suite | [pages-groups.md](references/pages-groups.md) |
| Running Facebook Ads — campaign setup, targeting, formats, Pixel, reporting | [ads-marketing.md](references/ads-marketing.md) |
| Privacy settings, account security, 2FA, data controls | [privacy-security.md](references/privacy-security.md) |
| Graph API — auth, tokens, nodes/edges, permissions, rate limits | [graph-api.md](references/graph-api.md) |
| Marketing API — campaign management, Ads Insights, Audiences, Catalogs | [marketing-api.md](references/marketing-api.md) |
| Messenger Platform API or WhatsApp Business Cloud API | [messaging-api.md](references/messaging-api.md) |

---

## Platform Overview

**Facebook (Meta)** is a multi-surface platform combining social networking, business tools, a marketplace, and a developer ecosystem.

### Surface Areas

```
facebook.com / mobile app
├── Social
│   ├── Feed (posts, Reels, Stories)
│   ├── Profile & Timeline
│   ├── Friends & Follows
│   ├── Groups
│   └── Events
├── Content Formats
│   ├── Reels (short video, highest reach)
│   ├── Stories (24-hour ephemeral)
│   ├── Live (real-time broadcast)
│   └── Watch (video hub)
├── Commerce
│   ├── Marketplace (P2P buying/selling)
│   └── Facebook/Instagram Shop (brand storefronts)
├── Other
│   ├── Dating
│   └── Gaming
└── Business Tools
    ├── Pages
    ├── Meta Business Suite
    ├── Ads Manager
    └── Events Manager (Pixel, CAPI)

Meta Developer Platform (developers.facebook.com)
├── Graph API v22.0 (core data access)
├── Marketing API (ads management)
├── Messenger Platform API (chatbots)
├── WhatsApp Business Cloud API (messaging)
└── Instagram Graph API (Instagram-side; overlaps with Graph API)
```

---

## Key Facts (2026)

- **Graph API current version:** v22.0 (each version supported ~2 years)
- **Reels:** All videos uploaded to Facebook default to Reels; 140B Reels watched/day globally
- **Facebook Gaming Creator Program** ended Oct 2025 — casual gaming features remain
- **Passkeys:** Now supported for login (phishing-resistant alternative to passwords)
- **Marketing API Jan 2026 change:** Some attribution window metrics and breakdowns limited in Ads Insights API
- **WhatsApp pricing:** Per-conversation fees vary by market and category; first 1,000 service conversations/month free
- **Advantage+ Audience / ASC:** Meta's AI-driven targeting — often outperforms manual setups when conversion history exists

---

## Loading the Right Reference

Load only what's needed:

- **"How do I use Facebook Marketplace?"** → read `website-features.md` (Marketplace section)
- **"Set up a Facebook Page for my business"** → read `pages-groups.md`
- **"Run a retargeting campaign"** → read `ads-marketing.md`
- **"How do I make my Facebook private?"** → read `privacy-security.md`
- **"Call the Graph API to get my posts"** → read `graph-api.md`
- **"Pull ad performance data with the Marketing API"** → read `marketing-api.md`
- **"Build a WhatsApp chatbot"** → read `messaging-api.md`
- **Multi-topic question** → load the 2 most relevant reference files
