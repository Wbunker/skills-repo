# WhatsApp Message Templates (HSM)

Templates (Highly Structured Messages) are pre-approved message structures required for reaching users outside the 24-hour session window. Every business-initiated conversation starts with a template.

## Table of Contents
1. [Template Categories](#template-categories)
2. [Template Structure & Components](#template-structure--components)
3. [Variables / Parameters](#variables--parameters)
4. [Button Types](#button-types)
5. [Creating Templates](#creating-templates)
6. [Approval Process & Statuses](#approval-process--statuses)
7. [Sending a Template via API](#sending-a-template-via-api)
8. [Template Management](#template-management)
9. [Best Practices](#best-practices)

---

## Template Categories

Meta classifies templates into three categories with different pricing:

| Category | Purpose | Cost |
|----------|---------|------|
| **Marketing** | Promotions, product recommendations, announcements, re-engagement, abandoned cart | Highest |
| **Utility** | Transactional messages triggered by user action — order confirmations, shipping updates, appointment reminders, payment alerts | ~80% cheaper than Marketing |
| **Authentication** | OTPs, verification codes, login links — has special button types | Lowest |

**Important (effective April 9, 2025)**: Meta auto-reclassifies templates. If you submit as UTILITY but Meta determines the content is promotional, it gets approved as MARKETING. Review the final category after approval.

**Rule of thumb**:
- Utility = triggered by something the user did (placed an order, made a payment, booked an appointment)
- Marketing = initiated by the business to drive engagement or sales
- Authentication = code delivery only

---

## Template Structure & Components

A template has up to 4 components:

```
┌─────────────────────────────────────────┐
│ HEADER (optional)                        │
│   Text (60 chars) | Image | Video |      │
│   Document | Location                    │
├─────────────────────────────────────────┤
│ BODY (required)                          │
│   Up to 1,024 characters                 │
│   Supports {{1}} {{2}} variables         │
├─────────────────────────────────────────┤
│ FOOTER (optional)                        │
│   Plain text, up to 60 characters        │
├─────────────────────────────────────────┤
│ BUTTONS (optional, up to 10 total)       │
│   Quick Reply | Call | URL | Flow | etc. │
└─────────────────────────────────────────┘
```

### Header Types
- **text**: static or with one variable `{{1}}`
- **image**: JPEG/PNG sent at template send time (by media URL or ID)
- **video**: MP4 sent at template send time
- **document**: PDF or other document
- **location**: latitude/longitude/name/address (sent at send time)

### Body
- Required; main message content
- Up to 1,024 characters
- Supports `{{1}}`, `{{2}}`, etc. positional variables
- Formatting: `*bold*`, `_italic_`, `~strikethrough~`, ` ```code``` `

### Footer
- Optional plain text shown below the body in smaller font
- Often used for opt-out language: "Reply STOP to unsubscribe"
- Cannot contain variables

---

## Variables / Parameters

Variables use the format `{{1}}`, `{{2}}` (1-indexed positional placeholders).

- Header can have at most **1 variable** (`{{1}}`)
- Body can have **multiple variables** (`{{1}}`, `{{2}}`, etc.)
- Button URLs can include **1 variable** at the end of the URL path

Fill variables at send time via the `components` array in the API request:

```json
"components": [
  {
    "type": "header",
    "parameters": [
      { "type": "text", "text": "Will Smith" }
    ]
  },
  {
    "type": "body",
    "parameters": [
      { "type": "text", "text": "Order #98765" },
      { "type": "text", "text": "Thursday, April 10" },
      { "type": "currency", "currency": { "fallback_value": "$49.99", "code": "USD", "amount_1000": 49990 } }
    ]
  }
]
```

**Parameter types**:
- `text` — plain string
- `currency` — amount with currency code (auto-formats by locale)
- `date_time` — timestamp (auto-formats by locale)
- `image` / `video` / `document` — for media headers (with `link` or `id`)
- `location` — for location headers

---

## Button Types

### Quick Reply Buttons
- User taps to send a predefined payload back to your webhook
- Up to **3** quick reply buttons per template
- `title`: displayed on button (up to 25 chars)
- `payload`: returned in webhook when user taps (up to 128 chars)
- Example use: "Yes, confirm" / "No, cancel" / "Contact support"

```json
{
  "type": "button",
  "sub_type": "quick_reply",
  "index": "0",
  "parameters": [{ "type": "payload", "payload": "confirm_order_yes" }]
}
```

### Call to Action — Phone Number
- Tap to call a phone number
- Defined statically at template creation time (number cannot vary at send time)

### Call to Action — URL
- Tap to open a URL in the browser
- URL can be static or dynamic (append one variable at the end)
- Static: `https://example.com/support`
- Dynamic: `https://example.com/track/{{1}}` — fill `{{1}}` at send time

```json
{
  "type": "button",
  "sub_type": "url",
  "index": "0",
  "parameters": [{ "type": "text", "text": "ORDER123" }]
}
```

### Copy Code (Authentication only)
- Displays a code with a "Copy Code" button that copies to clipboard
- Available only for Authentication category templates

### OTP Autofill (Authentication only)
- Automatically fills the OTP on Android (zero-tap authentication)
- Requires linking your Android app package name to the template

### Marketing Opt-Out
- Adds a standardized "Stop promotions" button to marketing templates
- Users who tap are added to your opt-out list; Meta stops delivering marketing templates to them

### Flow Button
- Opens a WhatsApp Flow (multi-screen form) directly from the template
- Include `flow_id` and initial `flow_action_payload` in the button definition
- Allows starting a Flow outside the session window

---

## Creating Templates

### Via API
```
POST https://graph.facebook.com/v20.0/{WABA_ID}/message_templates
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "name": "order_shipped",
  "language": "en_US",
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Your order has shipped! 📦"
    },
    {
      "type": "BODY",
      "text": "Hi {{1}}, your order {{2}} is on its way. Expected delivery: {{3}}."
    },
    {
      "type": "FOOTER",
      "text": "Reply STOP to unsubscribe from order updates"
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {
          "type": "URL",
          "text": "Track Package",
          "url": "https://example.com/track/{{1}}"
        }
      ]
    }
  ]
}
```

### Via WhatsApp Manager UI
Business Manager → WhatsApp Manager → Message Templates → Create Template
Use the visual builder — good for non-developers and for reviewing what templates look like.

### Template Name Rules
- Lowercase letters, numbers, underscores only
- No spaces or special characters
- Max 512 characters
- Must be unique within your WABA

---

## Approval Process & Statuses

| Status | Meaning |
|--------|---------|
| `PENDING` | Under Meta review (seconds to minutes for most) |
| `APPROVED` | Ready to use |
| `REJECTED` | Did not meet WhatsApp policy; can edit and resubmit |
| `PAUSED` | High negative user feedback (blocks/reports); temporary suspension |
| `DISABLED` | Policy violation; requires manual resolution with Meta |
| `FLAGGED` | Under quality review; still deliverable but being monitored |
| `LIMIT_EXCEEDED` | WABA template limit reached |

**Common rejection reasons**:
- Promotional content submitted as Utility
- Unclear opt-out mechanism in marketing templates
- Misleading or deceptive content
- Missing variable samples (add example values when submitting)

**After rejection**: edit the template and resubmit. You cannot resubmit without changes.

**Template limit**: up to **250 templates** per WABA (request increase via Meta support).

---

## Sending a Template via API

Full example with media header, body variables, and URL button:

```json
POST /{PHONE_NUMBER_ID}/messages
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "template",
  "template": {
    "name": "order_shipped",
    "language": { "code": "en_US" },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "image",
            "image": { "link": "https://example.com/logo.png" }
          }
        ]
      },
      {
        "type": "body",
        "parameters": [
          { "type": "text", "text": "Jane" },
          { "type": "text", "text": "#ORD-9876" },
          { "type": "text", "text": "April 12, 2026" }
        ]
      },
      {
        "type": "button",
        "sub_type": "url",
        "index": "0",
        "parameters": [{ "type": "text", "text": "ORD-9876" }]
      }
    ]
  }
}
```

**Response**:
```json
{
  "messaging_product": "whatsapp",
  "contacts": [{ "input": "15551234567", "wa_id": "15551234567" }],
  "messages": [{ "id": "wamid.HBgLMTU1NTEyMzQ1NjcAER..." }]
}
```
Save the `wamid` to correlate with delivery status webhooks.

---

## Template Management

### List Templates
```
GET https://graph.facebook.com/v20.0/{WABA_ID}/message_templates
  ?fields=name,status,category,language,components
```

### Get a Specific Template
```
GET https://graph.facebook.com/v20.0/{TEMPLATE_ID}
```

### Edit a Template
```
POST https://graph.facebook.com/v20.0/{TEMPLATE_ID}
{ "components": [...updated components...] }
```
Editing a PAUSED template and resubmitting can restore it to APPROVED if quality improves.

### Delete a Template
```
DELETE https://graph.facebook.com/v20.0/{WABA_ID}/message_templates
  ?name={TEMPLATE_NAME}
```
Deletes all languages of that template name.

---

## Best Practices

- **Include example values** when submitting: reduces rejection rate significantly
- **Utility over Marketing where valid**: utility messages are ~80% cheaper
- **Keep body under 160 chars if possible**: displays without truncation on all devices
- **One clear CTA**: templates with a single button have higher engagement than 3
- **Opt-out button on marketing templates**: reduces user blocks; protects quality rating
- **Language codes**: submit separate templates for each language (e.g., `en_US`, `es_MX`, `pt_BR`) — cannot share components across languages
- **Test before production**: use the sandbox number to verify rendering before sending to real users
