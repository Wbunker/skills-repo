# WhatsApp Cloud API

Meta-hosted REST API for enterprise WhatsApp messaging. No server infrastructure to manage. All API calls go to `graph.facebook.com`.

## Table of Contents
1. [Setup & Access](#setup--access)
2. [Authentication](#authentication)
3. [Sending Messages — All Types](#sending-messages--all-types)
4. [Interactive Messages](#interactive-messages)
5. [WhatsApp Flows](#whatsapp-flows)
6. [Media Handling](#media-handling)
7. [Phone Number Management](#phone-number-management)
8. [Opt-In Requirements](#opt-in-requirements)
9. [Common Errors](#common-errors)

---

## Setup & Access

### Direct API Access (via Meta)
1. Create a **Meta Business Account** at business.facebook.com
2. Create a **Meta Developer App** at developers.facebook.com → Add "WhatsApp Business" product
3. Use the **test sandbox number** Meta provides (send to up to 5 pre-verified numbers for free testing)
4. Add your own phone number via OTP (SMS or voice call)
5. Create a **System User** in Business Manager → assign as admin on the WABA → generate a permanent token

### Via Business Solution Provider (BSP)
Partners like Twilio, 360dialog, Infobip, WATI, Vonage — managed endpoints, dashboards, higher cost, faster onboarding. Use when you lack engineering bandwidth for direct setup.

### Embedded Signup (for SaaS platforms)
Meta-hosted JavaScript flow you embed on your website. Customers authenticate with Facebook, create/connect their WABA, and verify a phone number — all in one flow. Returns an authorization code you exchange for access tokens and WABA/phone number IDs. Best for platforms onboarding multiple business customers.

### Key Identifiers
- **`PHONE_NUMBER_ID`**: the sending number's internal ID (used in every send request)
- **`WABA_ID`**: the WhatsApp Business Account ID (used for templates, phone management)
- **`ACCESS_TOKEN`**: a System User token (permanent) or page access token (expiring)

---

## Authentication

All API requests require `Authorization: Bearer {ACCESS_TOKEN}` header.

**System User token** (recommended for production):
1. Business Manager → System Users → Add System User
2. Assign the System User as Admin on the WABA
3. Generate token with `whatsapp_business_messaging` and `whatsapp_business_management` permissions
4. Tokens are permanent until manually revoked

**Temporary tokens** (for testing only): available in the Meta App Dashboard under WhatsApp → API Setup. Expire after 24 hours.

---

## Sending Messages — All Types

Base endpoint:
```
POST https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

Phone numbers in `to` field must be in **E.164 format without `+`** (e.g., `15551234567`).

### Text Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "text",
  "text": {
    "body": "Hello! How can I help you today?",
    "preview_url": false
  }
}
```
- Max 4,096 characters
- Set `"preview_url": true` to render link previews

### Template Message (required outside 24-hour session window)
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "template",
  "template": {
    "name": "order_confirmation",
    "language": { "code": "en_US" },
    "components": [
      {
        "type": "body",
        "parameters": [
          { "type": "text", "text": "Order #12345" },
          { "type": "text", "text": "$49.99" }
        ]
      }
    ]
  }
}
```
See `templates.md` for full template structure and component types.

### Image Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "image",
  "image": {
    "link": "https://example.com/image.jpg",
    "caption": "Optional caption text"
  }
}
```
Use `"id": "MEDIA_ID"` instead of `"link"` if uploading via the media API.

**Media limits**:
| Type | Formats | Max Size |
|------|---------|---------|
| Image | JPEG, PNG | 5 MB |
| Audio | MP3, OGG, AMR | 16 MB |
| Video | MP4 | 16 MB |
| Document | PDF, DOC, XLSX, etc. | 100 MB |
| Sticker | WebP | 100 KB |

### Audio Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "audio",
  "audio": { "link": "https://example.com/audio.mp3" }
}
```

### Video Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "video",
  "video": {
    "link": "https://example.com/video.mp4",
    "caption": "Optional caption"
  }
}
```

### Document Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "document",
  "document": {
    "link": "https://example.com/file.pdf",
    "caption": "Invoice #001",
    "filename": "invoice_001.pdf"
  }
}
```

### Location Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "location",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "name": "Acme HQ",
    "address": "123 Main St, San Francisco, CA"
  }
}
```

### Reaction Message
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.XXXXXXX",
    "emoji": "👍"
  }
}
```

### Read Receipt (Mark as Read)
```json
POST /{PHONE_NUMBER_ID}/messages
{
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": "wamid.XXXXXXX"
}
```

---

## Interactive Messages

Only available within the **24-hour session window** (user must have messaged first). Cannot be sent as templates.

### Reply Buttons
Up to **3 buttons**. Each button has a `reply.id` (payload, max 256 chars) and `reply.title` (label, max 20 chars).

```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": { "type": "text", "text": "Choose an option" },
    "body": { "text": "How would you like to proceed?" },
    "footer": { "text": "Optional footer" },
    "action": {
      "buttons": [
        { "type": "reply", "reply": { "id": "confirm", "title": "Confirm Order" } },
        { "type": "reply", "reply": { "id": "modify", "title": "Modify Order" } },
        { "type": "reply", "reply": { "id": "cancel", "title": "Cancel" } }
      ]
    }
  }
}
```
Button replies arrive via webhook with `type: "interactive"` and `interactive.type: "button_reply"`.

### List Messages
A menu with sections. Up to **10 rows total** across all sections; user selects one item.

```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": { "type": "text", "text": "Our Services" },
    "body": { "text": "Select a service below" },
    "footer": { "text": "We're here to help" },
    "action": {
      "button": "View Services",
      "sections": [
        {
          "title": "Support",
          "rows": [
            { "id": "billing", "title": "Billing", "description": "Payment and invoices" },
            { "id": "technical", "title": "Technical Support", "description": "Tech help" }
          ]
        },
        {
          "title": "Sales",
          "rows": [
            { "id": "new_order", "title": "New Order", "description": "Start a new purchase" }
          ]
        }
      ]
    }
  }
}
```
List replies arrive via webhook with `interactive.type: "list_reply"`.

### CTA URL Button
Single button linking to a URL.

```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "cta_url",
    "body": { "text": "Track your shipment" },
    "action": {
      "name": "cta_url",
      "parameters": {
        "display_text": "Track Order",
        "url": "https://example.com/track/ORDER123"
      }
    }
  }
}
```

### Location Request
Prompt user to share their location.

```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "location_request_message",
    "body": { "text": "Please share your delivery address" },
    "action": { "name": "send_location" }
  }
}
```

---

## WhatsApp Flows

Rich multi-screen interactive forms embedded in a chat. Builds complex UX (appointment booking, surveys, registration) without leaving WhatsApp.

**Two types**:
- **Static Flows**: data collection forms (surveys, registrations, feedback)
- **Dynamic Flows**: real-time backend exchange — your endpoint is called between screens (appointment availability, real-time pricing)

**Components**: text fields, radio buttons, checkboxes, dropdowns, date pickers, toggle switches, image displays

**Build flows**: WhatsApp Manager → Flows tab → drag-and-drop UI + Flows JSON code editor

**Send a Flow as interactive message** (within session):
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "flow",
    "header": { "type": "text", "text": "Book an Appointment" },
    "body": { "text": "Select a time that works for you" },
    "footer": { "text": "Powered by Acme" },
    "action": {
      "name": "flow",
      "parameters": {
        "flow_message_version": "3",
        "flow_token": "UNIQUE_FLOW_TOKEN",
        "flow_id": "FLOW_ID",
        "flow_cta": "Book Now",
        "flow_action": "navigate",
        "flow_action_payload": {
          "screen": "APPOINTMENT_SCREEN"
        }
      }
    }
  }
}
```

**Send a Flow via template** (to initiate outside session window): use a template with a Flow button component (see `templates.md`).

---

## Media Handling

### Upload Media (get a reusable media ID)
```
POST https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/media
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: multipart/form-data

messaging_product=whatsapp
file=@/path/to/file.jpg
type=image/jpeg
```
Returns `{ "id": "MEDIA_ID" }` — use this ID instead of a URL for sending.

### Get Media URL (to download inbound media)
```
GET https://graph.facebook.com/v20.0/{MEDIA_ID}
Authorization: Bearer {ACCESS_TOKEN}
```
Returns a temporary download URL (expires in minutes). Download immediately and store in your own system.

### Delete Media
```
DELETE https://graph.facebook.com/v20.0/{MEDIA_ID}
```

---

## Phone Number Management

### Register a Number
1. Add number in Meta App Dashboard (WhatsApp → Phone Numbers → Add Phone Number)
2. Verify via OTP (SMS or voice call)
3. Request display name approval (must reflect your brand)
4. Number is ready once display name is approved

### Display Name
- Appears in the chat header and contact info
- Must match your business name; reviewed by Meta
- Statuses: PENDING / APPROVED / DECLINED
- Gray checkmark = display name verified (not the same as Official Business Account)

### Number Migration (Business App → API)
Use the phone number migration API to transfer a number from the Business App to the Cloud API:
1. Initiate migration via WhatsApp Manager
2. The Business App number is deregistered
3. Number is registered to the Cloud API
Migration is **one-way** — cannot revert to Business App.

---

## Opt-In Requirements

WhatsApp requires **explicit opt-in** before sending proactive messages. Key rules:

- Collect opt-in **outside WhatsApp** (website form, checkout, SMS, IVR, in-person)
- Clearly state: user will receive WhatsApp messages from **[Business Name]**
- State the **type** of messages they'll receive
- Provide a way to **opt out**
- If user messages your business first → implicit opt-in for that session; collect explicit opt-in for future proactive messages
- Can also collect opt-in within a conversation using WhatsApp Flows
- Meta can audit; violations result in account restrictions or WABA suspension

---

## Common Errors

| Error Code | Meaning | Fix |
|------------|---------|-----|
| 131047 | Re-engagement message — session window closed | Use a template message |
| 131056 | Too many messages to this number | Rate limit or tier limit hit |
| 132000 | Template not found or not approved | Check template name/language/status |
| 132001 | Template parameter count mismatch | Match parameters to template variables |
| 133004 | Phone number not registered | Register number in Meta App Dashboard |
| 100 | Invalid parameter | Check request body structure |
| 190 | Access token expired or invalid | Regenerate/replace access token |
| 80007 | Rate limit hit | Slow down; implement exponential backoff |
