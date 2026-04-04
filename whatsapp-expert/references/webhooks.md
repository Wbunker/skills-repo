# WhatsApp Webhooks

Webhooks deliver real-time events: inbound messages, delivery status updates, template approvals, quality rating changes, and more.

## Table of Contents
1. [Setup & Verification](#setup--verification)
2. [Webhook Fields to Subscribe](#webhook-fields-to-subscribe)
3. [Payload Structure](#payload-structure)
4. [Inbound Message Types](#inbound-message-types)
5. [Delivery Status Events](#delivery-status-events)
6. [Other Event Types](#other-event-types)
7. [Security — Signature Validation](#security--signature-validation)
8. [Reliability & Best Practices](#reliability--best-practices)
9. [Processing Inbound Messages — Workflow](#processing-inbound-messages--workflow)

---

## Setup & Verification

1. Build a public HTTPS endpoint (no self-signed certs; must be TLS 1.2+)
2. In Meta App Dashboard: App → WhatsApp → Configuration → Webhook
3. Enter your **Callback URL** and a **Verify Token** (any string you choose)
4. Meta sends a GET request to verify:

```
GET {YOUR_CALLBACK_URL}
  ?hub.mode=subscribe
  &hub.verify_token={YOUR_VERIFY_TOKEN}
  &hub.challenge={RANDOM_STRING}
```

5. Your endpoint must:
   - Check `hub.mode === "subscribe"`
   - Check `hub.verify_token` matches your stored token
   - Return HTTP 200 with the value of `hub.challenge` as the response body (plain text, not JSON)

```python
# Python (Flask) example
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == MY_VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403
```

6. After verification, subscribe to specific fields in the Meta App Dashboard

---

## Webhook Fields to Subscribe

| Field | Delivers |
|-------|---------|
| `messages` | Inbound messages + outbound delivery/read status updates |
| `message_template_status_update` | Template approved / rejected / paused / disabled |
| `phone_number_quality_update` | Quality rating changed (GREEN → YELLOW → RED) |
| `phone_number_name_update` | Display name approval status |
| `account_update` | Policy violations, account restrictions, bans |
| `account_review_update` | Business verification status changes |
| `flows` | Flow status changes and errors |
| `message_echoes` | Echo of outbound messages sent via the API (optional) |

Subscribe to at minimum: `messages` + `message_template_status_update` + `phone_number_quality_update`

---

## Payload Structure

All webhook payloads share the same outer envelope:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WABA_ID",
      "changes": [
        {
          "field": "messages",
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551234567",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "contacts": [...],
            "messages": [...],
            "statuses": [...]
          }
        }
      ]
    }
  ]
}
```

- `entry` is an array — process all entries, not just `entry[0]`
- `changes` is an array — process all changes
- `value.messages` contains inbound messages
- `value.statuses` contains delivery status updates
- Both `messages` and `statuses` can appear in the same webhook call

---

## Inbound Message Types

All inbound messages arrive in `value.messages[]`. Check `messages[0].type` to determine how to parse.

### Text Message
```json
{
  "from": "15551234567",
  "id": "wamid.XXXXX",
  "timestamp": "1712000000",
  "type": "text",
  "text": { "body": "Hello, I need help with my order" }
}
```

### Image / Audio / Video / Document / Sticker
```json
{
  "from": "15551234567",
  "id": "wamid.XXXXX",
  "timestamp": "1712000000",
  "type": "image",
  "image": {
    "id": "MEDIA_ID",
    "mime_type": "image/jpeg",
    "sha256": "HASH",
    "caption": "Optional caption"
  }
}
```
Download the media: `GET /{MEDIA_ID}` → get temporary URL → download immediately.

### Location
```json
{
  "type": "location",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "name": "Golden Gate Park",
    "address": "San Francisco, CA"
  }
}
```

### Interactive — Button Reply (Quick Reply button tapped)
```json
{
  "type": "interactive",
  "interactive": {
    "type": "button_reply",
    "button_reply": {
      "id": "confirm_order_yes",
      "title": "Yes, confirm"
    }
  }
}
```

### Interactive — List Reply (List item selected)
```json
{
  "type": "interactive",
  "interactive": {
    "type": "list_reply",
    "list_reply": {
      "id": "billing",
      "title": "Billing",
      "description": "Payment and invoices"
    }
  }
}
```

### Interactive — Flow Response (nfm_reply)
```json
{
  "type": "interactive",
  "interactive": {
    "type": "nfm_reply",
    "nfm_reply": {
      "response_json": "{\"appointment_date\":\"2026-04-15\",\"time\":\"10:00\"}",
      "body": "Sent",
      "name": "flow"
    }
  }
}
```
Parse `response_json` as a JSON string to get the Flow form submission data.

### Reaction
```json
{
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.ORIGINAL_MESSAGE",
    "emoji": "👍"
  }
}
```

### Contacts
```json
{
  "type": "contacts",
  "contacts": [
    {
      "name": { "formatted_name": "Jane Smith" },
      "phones": [{ "phone": "+15559876543", "type": "CELL" }]
    }
  ]
}
```

### Unsupported
```json
{ "type": "unsupported", "errors": [...] }
```
Occurs for message types not supported by the API (e.g., polls from groups).

---

## Delivery Status Events

Status events arrive in `value.statuses[]`:

```json
{
  "id": "wamid.XXXXX",
  "status": "read",
  "timestamp": "1712000100",
  "recipient_id": "15551234567",
  "conversation": {
    "id": "CONV_ID",
    "expiration_timestamp": "1712086400",
    "origin": { "type": "utility" }
  },
  "pricing": {
    "billable": true,
    "pricing_model": "PMP",
    "category": "utility"
  }
}
```

| Status | Meaning |
|--------|---------|
| `sent` | Message accepted by WhatsApp server |
| `delivered` | Message delivered to recipient's device |
| `read` | Recipient opened the message (blue ticks) |
| `failed` | Delivery failed; check `errors[]` for reason |

The `pricing` object tells you the billing category and whether it's a paid message. Use this to track costs.

---

## Other Event Types

### Template Status Update
```json
{
  "field": "message_template_status_update",
  "value": {
    "event": "APPROVED",
    "message_template_id": 12345,
    "message_template_name": "order_shipped",
    "message_template_language": "en_US",
    "reason": null
  }
}
```
`event` values: `APPROVED`, `REJECTED`, `PAUSED`, `DISABLED`, `FLAGGED`

### Phone Number Quality Update
```json
{
  "field": "phone_number_quality_update",
  "value": {
    "display_phone_number": "15551234567",
    "event": "FLAGGED",
    "current_limit": "TIER_1K"
  }
}
```

---

## Security — Signature Validation

Every POST webhook includes the header `X-Hub-Signature-256`.

**Validation process**:
1. Get the raw request body (before any JSON parsing)
2. Compute HMAC-SHA256 of the raw body using your App Secret as the key
3. Compare `sha256={computed_hash}` against the `X-Hub-Signature-256` header
4. Use **constant-time comparison** (prevent timing attacks)
5. Reject requests that fail validation with HTTP 403

```python
import hmac, hashlib

def validate_signature(raw_body: bytes, signature_header: str, app_secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        app_secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

**Never skip signature validation** in production — any internet actor can POST to your webhook URL.

---

## Reliability & Best Practices

### Return 200 Immediately
- Return HTTP 200 **within 5–10 seconds** of receiving the webhook
- Process the payload **asynchronously** (queue it, then respond)
- If Meta doesn't receive 200 within the timeout, it will retry

### Retry Behavior
- Meta retries failed webhook deliveries with **exponential backoff**
- Retries continue for up to **7 days**
- At-least-once delivery: the same event may arrive more than once

### Idempotency
- Deduplicate using `messages[0].id` (the `wamid`)
- Store processed `wamid`s and skip duplicates
- Status updates for the same message arrive as separate events (sent → delivered → read)

### Message Ordering
- Messages may arrive out of order
- Use `timestamp` field to order if sequence matters

### 24-Hour Session Window
- Any inbound message from a user opens a **24-hour session window**
- During this window: send any message type (text, media, interactive) for free
- After the window closes: must use a template to re-engage

### Process All Array Entries
```python
for entry in payload["entry"]:
    for change in entry["changes"]:
        if change["field"] == "messages":
            value = change["value"]
            for msg in value.get("messages", []):
                process_message(msg)
            for status in value.get("statuses", []):
                process_status(status)
```

---

## Processing Inbound Messages — Workflow

```
1. Receive POST → validate X-Hub-Signature-256 → return 200 immediately

2. Queue payload for async processing

3. Extract sender:
   contacts[0].wa_id  (E.164 without +, e.g., "15551234567")
   contacts[0].profile.name  (display name)
   metadata.phone_number_id  (which of your numbers received it)

4. Check message type:
   - text → messages[0].text.body
   - interactive button_reply → messages[0].interactive.button_reply.id
   - interactive list_reply → messages[0].interactive.list_reply.id
   - interactive nfm_reply → parse messages[0].interactive.nfm_reply.response_json
   - image/audio/video/document → download via GET /{messages[0].image.id}
   - location → messages[0].location.{latitude,longitude}
   - reaction → messages[0].reaction.{message_id, emoji}

5. Deduplicate on messages[0].id (wamid)

6. Update your session state / CRM

7. Reply within the 24-hour window (free-form messages allowed)
   OR if window closed, send a template
```
