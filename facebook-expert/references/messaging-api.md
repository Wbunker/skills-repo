# Messenger Platform & WhatsApp Business API

## Table of Contents
1. [Messenger Platform API](#messenger-platform-api)
2. [WhatsApp Business API (Cloud API)](#whatsapp-business-api-cloud-api)

---

## Messenger Platform API

Build chatbots and automated experiences in Facebook Messenger.

**Reference:** developers.facebook.com/docs/messenger-platform

### Setup
1. Create a Facebook App at developers.facebook.com
2. Add "Messenger" product to your app
3. Generate a Page Access Token for the Page your bot will represent
4. Configure a webhook to receive incoming messages

### Required Permissions
- `pages_messaging` — send/receive messages on behalf of a Page
- `pages_show_list` — list Pages the user manages
- `pages_manage_metadata` — subscribe to webhook events

### Webhook Setup
Subscribe your endpoint to receive events:
```bash
POST https://graph.facebook.com/v22.0/me/subscribed_apps
  body: subscribed_fields=messages,messaging_postbacks,message_reads
  access_token={page-token}
```

Your webhook must:
- Accept GET for verification challenge: check `hub.verify_token` matches your secret, return `hub.challenge`
- Accept POST for incoming events
- Respond with HTTP 200 within 20 seconds

### Webhook Event Types
| Event | Trigger |
|---|---|
| `messages` | User sends a message |
| `messaging_postbacks` | User taps a button/quick reply |
| `message_reads` | User reads your message |
| `messaging_referrals` | User clicks a m.me link or referral |
| `messaging_optins` | User opts in via checkbox or one-time notification |

### Sending Messages

**Text message:**
```bash
POST https://graph.facebook.com/v22.0/me/messages
  access_token={page-token}
```
```json
{
  "recipient": { "id": "{user-psid}" },
  "message": { "text": "Hello! How can I help you?" }
}
```

**Quick replies:**
```json
{
  "recipient": { "id": "{user-psid}" },
  "message": {
    "text": "What would you like to do?",
    "quick_replies": [
      { "content_type": "text", "title": "Browse Products", "payload": "BROWSE_PRODUCTS" },
      { "content_type": "text", "title": "Contact Support", "payload": "CONTACT_SUPPORT" }
    ]
  }
}
```

**Generic template (cards):**
```json
{
  "recipient": { "id": "{user-psid}" },
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [{
          "title": "Product Name",
          "image_url": "https://example.com/image.jpg",
          "subtitle": "Product description",
          "buttons": [
            { "type": "web_url", "url": "https://example.com", "title": "View" },
            { "type": "postback", "title": "Buy Now", "payload": "BUY_PRODUCT_123" }
          ]
        }]
      }
    }
  }
}
```

**Button template:**
```json
{
  "recipient": { "id": "{user-psid}" },
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "button",
        "text": "What would you like to do?",
        "buttons": [
          { "type": "web_url", "url": "https://example.com", "title": "Visit Website" },
          { "type": "postback", "title": "Get Started", "payload": "GET_STARTED" },
          { "type": "phone_number", "title": "Call Us", "payload": "+15551234567" }
        ]
      }
    }
  }
}
```

### Persistent Menu
Set a persistent menu visible in every Messenger conversation:
```bash
POST https://graph.facebook.com/v22.0/me/messenger_profile
```
```json
{
  "persistent_menu": [{
    "locale": "default",
    "composer_input_disabled": false,
    "call_to_actions": [
      { "type": "postback", "title": "Get Started", "payload": "GET_STARTED" },
      { "type": "web_url", "title": "Our Website", "url": "https://example.com" }
    ]
  }]
}
```

### User Profile API
Get basic info about a message sender:
```bash
GET https://graph.facebook.com/v22.0/{user-psid}?fields=name,first_name,last_name,profile_pic
  access_token={page-token}
```

### Messaging Window Rules
- **Standard Messaging**: Respond within 24 hours of the user's last message (free)
- **After 24 hours**: Must use a Message Tag or One-Time Notification
- **Message Tags** (for post-24hr): `CONFIRMED_EVENT_UPDATE`, `POST_PURCHASE_UPDATE`, `ACCOUNT_UPDATE`
- **Promotional messages**: Only allowed within the 24-hour window

### Testing
- Use the Graph API Explorer or Postman to test message sends
- Messenger Platform has a test user feature in App Dashboard → Messenger → Settings

---

## WhatsApp Business API (Cloud API)

Send and receive WhatsApp messages programmatically. Hosted by Meta (no server needed).

**Reference:** developers.facebook.com/docs/whatsapp/cloud-api
**Pricing:** Fee per conversation (24-hour window), varies by country and category

### Conversation Categories & Pricing
| Category | Direction | Fee |
|---|---|---|
| **Marketing** | Business-initiated | Charged |
| **Utility** | Business-initiated (transactional) | Charged |
| **Authentication** | Business-initiated (OTP) | Charged |
| **Service** | User-initiated | Free within 24-hr window |

First 1,000 service conversations per month are free.

### Setup
1. Create a Meta App with WhatsApp product
2. Add a phone number (test number provided or verify your own)
3. Get the Phone Number ID and WhatsApp Business Account ID
4. Generate a System User token with `whatsapp_business_messaging` permission
5. Configure webhook for incoming messages

### Required Permissions
- `whatsapp_business_messaging` — send/receive messages
- `whatsapp_business_management` — manage WhatsApp Business accounts and templates

### Sending a Text Message
```bash
POST https://graph.facebook.com/v22.0/{phone-number-id}/messages
  Authorization: Bearer {system-user-token}
```
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "text",
  "text": { "body": "Hello from WhatsApp!" }
}
```

### Sending a Template Message (Business-Initiated)
Templates must be pre-approved by Meta. Use for marketing, utility, or authentication outside the 24-hour service window.
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
          { "type": "text", "text": "John" },
          { "type": "text", "text": "ORDER-12345" }
        ]
      }
    ]
  }
}
```

### Sending Media Messages
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "image",
  "image": { "link": "https://example.com/image.jpg" }
}
```

Supported types: `image`, `video`, `audio`, `document`, `sticker`

### Interactive Messages (Buttons & Lists)
```json
{
  "messaging_product": "whatsapp",
  "to": "15551234567",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": { "text": "Choose an option:" },
    "action": {
      "buttons": [
        { "type": "reply", "reply": { "id": "btn_1", "title": "Option 1" } },
        { "type": "reply", "reply": { "id": "btn_2", "title": "Option 2" } }
      ]
    }
  }
}
```

**List messages** (up to 10 rows):
```json
{
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": { "text": "Select a department:" },
    "action": {
      "button": "Choose",
      "sections": [{
        "title": "Support",
        "rows": [
          { "id": "tech", "title": "Technical Support" },
          { "id": "billing", "title": "Billing" }
        ]
      }]
    }
  }
}
```

### Receiving Messages (Webhook)
Incoming messages arrive at your webhook as POST requests:
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "15551234567",
          "type": "text",
          "text": { "body": "Hello!" },
          "timestamp": "1680000000",
          "id": "wamid.xxx"
        }]
      }
    }]
  }]
}
```

Mark messages as read:
```bash
POST /{phone-number-id}/messages
```
```json
{
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": "{message-id}"
}
```

### Template Management
```bash
# List approved templates
GET /{whatsapp-business-account-id}/message_templates?fields=name,status,components

# Create a template (pending Meta review, 1-3 days)
POST /{whatsapp-business-account-id}/message_templates
```
```json
{
  "name": "appointment_reminder",
  "language": "en_US",
  "category": "UTILITY",
  "components": [
    {
      "type": "body",
      "text": "Hi {{1}}, your appointment is confirmed for {{2}} at {{3}}."
    }
  ]
}
```

### Phone Number Management
```bash
# List registered phone numbers
GET /{whatsapp-business-account-id}/phone_numbers?fields=id,display_phone_number,status

# Verify a phone number (OTP)
POST /{phone-number-id}/request_code  (sends OTP to phone)
POST /{phone-number-id}/verify_code   (body: code=123456)
```

### Rate Limits
- **Messaging**: 80 messages/second per phone number (default)
- **Template creation**: Limited; rejected templates count against limits
- Phone numbers gain higher limits (tiers) as messaging volume and quality increase
