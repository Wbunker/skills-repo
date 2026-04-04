# WhatsApp Business App

The free mobile app for small businesses. Different from the API — no coding required, no webhooks, no CRM integration. Suitable for micro/small businesses handling conversations manually.

## Table of Contents
1. [Setup & Business Profile](#setup--business-profile)
2. [Catalog](#catalog)
3. [Quick Replies](#quick-replies)
4. [Labels](#labels)
5. [Automated Messages](#automated-messages)
6. [Broadcasts](#broadcasts)
7. [Multi-Device & Multi-Agent](#multi-device--multi-agent)
8. [Meta Verified Badge](#meta-verified-badge)
9. [Business App vs. API — When to Upgrade](#business-app-vs-api--when-to-upgrade)

---

## Setup & Business Profile

- Download **WhatsApp Business** (separate app from personal WhatsApp; package: `com.whatsapp.w4b`)
- Register with a phone number not in use on regular WhatsApp
- A number cannot be used in the Business App and the API simultaneously
- **Business profile fields**:
  - Business name (permanent once set; contact Meta support to change)
  - Category (e.g., retail, restaurant, beauty)
  - Description (up to 256 characters)
  - Email address
  - Website URL(s)
  - Business address
  - Business hours (per day, open/closed toggle)

The business profile is visible to anyone who messages you. Business name appears in the chat header instead of the phone number.

---

## Catalog

- List up to **500 products or services**
- Each item includes: image, name, price (optional), description, link, product code
- Organize items into **collections** (categories within the catalog)
- Customers browse and share items without leaving WhatsApp
- **Cart functionality**: customers build carts from the catalog and send as an order message
- Share the catalog (or individual items) to WhatsApp chats, Facebook, and Instagram
- Access: Business Settings → Catalog
- No inventory management or payment processing (catalog is informational/discovery only)

---

## Quick Replies

Pre-saved response templates for common messages.

- Trigger by typing `/` + shortcut keyword in the message box (e.g., `/thanks` expands to full message)
- Supports text and media attachments
- Examples: FAQ answers, directions, pricing info, order confirmation thank-you
- Create up to ~50 quick replies
- Access: Business Settings → Quick Replies

---

## Labels

Color-coded tags to organize chats and contacts.

- Up to **20 labels** (default labels: New Customer, New Order, Pending Payment, Paid, Order Complete)
- Apply to entire conversations or specific messages
- Filter the chat list by label to see all chats with a given status
- Useful for sales pipeline tracking, order management, customer segmentation
- Access: tap a chat → label icon, or hold a chat in list → label

---

## Automated Messages

### Greeting Message
- Sent automatically to a new contact's **first message**, or after **14 days of inactivity**
- Customize the message text
- Schedule: Always / Outside business hours / Custom schedule
- Cannot be conditional or personalized with variables

### Away Message
- Sent when a customer messages **outside your business hours** or when you toggle it on manually
- Configure when it activates:
  - **Always**: sends to all incoming messages regardless of time
  - **Custom schedule**: specific hours/days
  - **Outside business hours**: uses your business hours settings
- Customize the message text (cannot include buttons or media)

### Limitations
- No branching logic or conditional automation
- No chatbot-style flows
- No integration with external systems
- For complex automation, upgrade to the API

---

## Broadcasts

- Send a message to up to **256 contacts** at once
- Recipients must have **your number saved** in their contacts to receive the broadcast (otherwise it's blocked)
- Messages appear as individual DMs to each recipient — not a group chat
- Recipients cannot see each other
- Manual contact addition only (no bulk CSV import)
- **2025 enhanced broadcasts**: schedule messages for optimal delivery time, add action buttons, view engagement metrics (sent/delivered/read)

---

## Multi-Device & Multi-Agent

- Link up to **4 companion devices** (WhatsApp Web, desktop, tablets) — phone doesn't need to be online
- Up to **10 agents** can handle conversations across linked companion devices
- Useful for small teams with 1 shared business number
- No role-based permissions (all linked devices have full access)
- For larger teams with assignment/routing: upgrade to API + inbox platform (e.g., WATI, Respond.io)

---

## Meta Verified Badge

- Paid monthly subscription (pricing varies by country, ~$14–25/month)
- Provides:
  - **Authentication badge** (blue checkmark on business profile — different from API's gray/green checkmarks)
  - Impersonation protection
  - Priority customer support from Meta
  - Enhanced search visibility in WhatsApp search
- Distinct from the API's Official Business Account (green checkmark) — that's reserved for top brands

---

## Business App vs. API — When to Upgrade

| Need | Business App | API |
|------|-------------|-----|
| Volume | Up to ~256/broadcast, manual | Unlimited (tier-based) |
| Automation / chatbot | No | Yes |
| CRM / helpdesk integration | No | Yes |
| Multiple agents with routing | 10 linked devices, no routing | Full inbox platform support |
| Analytics | Basic (2025 broadcasts only) | Full delivery/read webhooks |
| Programmatic sending | No | Yes |
| Message templates for proactive outreach | No | Yes (requires approval) |
| Multiple phone numbers | 1 per app install | Up to 20 per WABA |

**Migrate from Business App to API**: phone number migration is supported — you can transfer a number from the Business App to the Cloud API using the number migration flow in Meta Business Manager. Migration is **one-way** (API → Business App migration is not supported).
