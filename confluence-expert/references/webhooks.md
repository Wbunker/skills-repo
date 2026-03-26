# Confluence Webhooks Reference

## Overview

Confluence webhooks send HTTP POST requests to your endpoint when events occur in a space or globally. Webhooks are the primary mechanism for event-driven integration.

**Delivery note:** Webhook delivery is **best-effort, not guaranteed**. If your endpoint is down or returns an error, the event may be lost — Confluence has limited retry behavior. Design integrations to be idempotent and resilient to missed events.

---

## Registration Methods

### 1. Connect App Descriptor (atlassian-connect.json)

The most common method for Cloud integrations. Declare webhooks in your app descriptor:

```json
{
  "modules": {
    "webhooks": [
      {
        "event": "page_created",
        "url": "/webhooks/page-created"
      },
      {
        "event": "page_updated",
        "url": "/webhooks/page-updated"
      }
    ]
  }
}
```

JWT validation is handled automatically by the Connect framework (e.g., `atlassian-connect-express`).

### 2. REST API Registration (v1)

Register webhooks programmatically without building a full Connect app:

```http
POST /rest/webhooks/1.0/webhook
Authorization: Basic ...
Content-Type: application/json

{
  "name": "My Page Watcher",
  "url": "https://myapp.example.com/webhook",
  "events": ["page_created", "page_updated"],
  "filters": {
    "space-related": [
      { "spaceKey": "ENG" }
    ]
  },
  "excludeBody": false
}
```

**List registered webhooks:**
```bash
GET /rest/webhooks/1.0/webhook
```

**Delete a webhook:**
```bash
DELETE /rest/webhooks/1.0/webhook/{webhookId}
```

### 3. Forge App

Forge apps use trigger declarations in `manifest.yml`:

```yaml
triggers:
  - key: page-created-trigger
    function: handlePageCreated
    events:
      - avi:confluence:created:page
```

The Forge runtime handles delivery and authentication.

---

## All Webhook Event Types

### Page Events

| Event | Trigger |
|---|---|
| `page_created` | A new page is published |
| `page_updated` | An existing page is edited and saved |
| `page_removed` | A page is deleted (moved to trash) |
| `page_restored` | A deleted page is restored from trash |
| `page_trashed` | A page is moved to trash |
| `page_moved` | A page is moved to a different parent or space |
| `page_copied` | A page is copied |
| `page_archived` | A page is archived |
| `page_unarchived` | A page is unarchived |
| `page_viewed` | A user views a page |
| `page_children_reordered` | Child pages are reordered |
| `page_initialized` | A new page editor is opened (draft started) |
| `page_started` | Draft page editing started |
| `page_snapshotted` | A page snapshot is created |
| `page_published` | A live page is published |

### Blogpost Events

| Event | Trigger |
|---|---|
| `blog_created` | A new blogpost is published |
| `blog_updated` | A blogpost is updated |
| `blog_removed` | A blogpost is deleted |
| `blog_restored` | A blogpost is restored |
| `blog_trashed` | A blogpost is moved to trash |
| `blog_moved` | A blogpost is moved |
| `blog_viewed` | A user views a blogpost |

### Attachment Events

| Event | Trigger |
|---|---|
| `attachment_created` | A new file is attached to a page |
| `attachment_updated` | An attachment is replaced with a new version |
| `attachment_removed` | An attachment is deleted |
| `attachment_restored` | An attachment is restored |
| `attachment_trashed` | An attachment is moved to trash |
| `attachment_archived` | An attachment is archived |
| `attachment_unarchived` | An attachment is unarchived |
| `attachment_viewed` | An attachment is viewed/downloaded |

### Comment Events

| Event | Trigger |
|---|---|
| `comment_removed` | A comment is deleted |
| `comment_updated` | A comment is edited |

### Content Events (Generic)

| Event | Trigger |
|---|---|
| `content_created` | Any content object is created |
| `content_updated` | Any content object is updated |
| `content_removed` | Any content object is removed |
| `content_restored` | Any content object is restored |
| `content_trashed` | Any content object is trashed |
| `content_permissions_updated` | Page-level restrictions changed |
| `blueprint_page_created` | A page from a blueprint template is created |

### Space Events

| Event | Trigger |
|---|---|
| `space_created` | A new space is created |
| `space_updated` | Space metadata is updated |
| `space_removed` | A space is deleted |
| `space_logo_updated` | The space logo image changes |
| `space_permissions_updated` | Space permissions are modified |

### Label and Relation Events

| Event | Trigger |
|---|---|
| `label_created` | A new label is defined |
| `label_deleted` | A label is removed from the system |
| `label_added` | A label is applied to content |
| `label_removed` | A label is removed from content |
| `relation_created` | A content relation is created |
| `relation_deleted` | A content relation is deleted |

### User and Group Events

| Event | Trigger |
|---|---|
| `user_removed` | A user is removed from the site |
| `user_reactivated` | A previously removed user is reactivated |
| `group_created` | A new group is created |
| `group_removed` | A group is deleted |

### System Events

| Event | Trigger |
|---|---|
| `connect_addon_disabled` | A Connect app is disabled |
| `connect_addon_enabled` | A Connect app is enabled |
| `theme_enabled` | A site theme is changed |
| `search_performed` | A search is executed |

---

## Payload Structure

Webhook payloads are sent as JSON in an HTTP POST request body.

### Page Created / Updated

```json
{
  "timestamp": 1742932800000,
  "userAccountId": "99:abc123-...",
  "accountType": "atlassian",
  "updateTrigger": "page_updated",
  "page": {
    "id": "12345678",
    "title": "My Page Title",
    "spaceKey": "ENG",
    "contentType": "page",
    "version": 3,
    "creatorAccountId": "99:abc123-...",
    "lastModifierAccountId": "99:def456-...",
    "creationDate": 1742800000000,
    "modificationDate": 1742932800000,
    "self": "https://domain.atlassian.net/wiki/spaces/ENG/pages/12345678/My+Page+Title"
  }
}
```

### Comment Created

```json
{
  "timestamp": 1742932800000,
  "userAccountId": "99:abc123-...",
  "comment": {
    "id": "987654",
    "contentType": "comment",
    "creatorAccountId": "99:abc123-...",
    "pageId": "12345678",
    "spaceKey": "ENG",
    "creationDate": 1742932800000,
    "modificationDate": 1742932800000
  }
}
```

### Space Event

```json
{
  "timestamp": 1742932800000,
  "userAccountId": "99:abc123-...",
  "space": {
    "key": "NEWSPACE",
    "name": "New Space",
    "type": "global",
    "self": "https://domain.atlassian.net/wiki/rest/api/space/NEWSPACE"
  }
}
```

### Attachment Event

```json
{
  "timestamp": 1742932800000,
  "userAccountId": "99:abc123-...",
  "attachment": {
    "id": "att12345",
    "title": "diagram.png",
    "spaceKey": "ENG",
    "pageId": "12345678",
    "contentType": "attachment",
    "mediaType": "image/png",
    "fileSize": 40960,
    "creatorAccountId": "99:abc123-...",
    "creationDate": 1742932800000
  }
}
```

---

## Security (Connect App JWT Validation)

For Connect apps, Atlassian signs webhook requests with a JWT token in the `Authorization` header. Use the `atlassian-connect-express` framework (or similar) to validate automatically:

```javascript
app.post('/webhook', addon.authenticate(), (req, res) => {
  // Request is authenticated if it reaches here
  const { userAccountId, page } = req.body;
  console.log(`${userAccountId} triggered event on page: ${page.title}`);
  res.sendStatus(200);
});
```

For manual validation, verify the JWT using the shared secret from your app's installation record.

---

## Filtering Webhooks by Space

When registering via REST API, scope webhooks to specific spaces to reduce noise:

```json
{
  "name": "ENG Space Watcher",
  "url": "https://myapp.example.com/webhook",
  "events": ["page_created", "page_updated"],
  "filters": {
    "space-related": [
      { "spaceKey": "ENG" }
    ]
  }
}
```

Without filters, the webhook fires for all matching events across all spaces.

---

## Handling Webhooks in Python

```python
from flask import Flask, request, jsonify
import hmac, hashlib

app = Flask(__name__)
SHARED_SECRET = "your-app-shared-secret"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_json()
    event_type = request.headers.get('X-Confluence-Event') or payload.get('updateTrigger', '')

    if 'page' in payload:
        page = payload['page']
        print(f"Event: {event_type}, Page: {page['title']} in space {page['spaceKey']}")

    return jsonify({"status": "ok"}), 200
```

Always return `200 OK` quickly. If your handler is slow, process events asynchronously (queue the payload, acknowledge immediately):

```python
from celery import Celery
import queue

task_queue = queue.Queue()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    task_queue.put(request.get_json())
    return '', 200  # acknowledge immediately
```

---

## Gotchas

- **Best-effort delivery** — Confluence does not guarantee delivery or order; design for idempotency
- **Forge is the future** — Atlassian has deprecated Connect app development in favor of Forge; new webhook integrations should use Forge event triggers
- **No built-in HMAC signing for REST-registered webhooks** — unlike GitHub webhooks, REST-registered Confluence webhooks don't include a signature for verification; secure your endpoint with authentication or IP allowlisting
- **page_viewed is high-volume** — subscribing to `page_viewed` can generate extremely high event volume on busy instances; only use if necessary
- **Timestamps are milliseconds** — all `timestamp`, `creationDate`, and `modificationDate` values are Unix timestamps in **milliseconds**, not seconds
- **Payload does not include content body** — webhook payloads contain metadata only; if you need the page content, call back to the REST API after receiving the event
- **Connect apps deprecated on Cloud** — Atlassian's "Connect support is ending" announcement means all new apps should use Forge; however, existing Connect webhooks continue to work
