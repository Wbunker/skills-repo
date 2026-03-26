# Jira Webhooks Reference

## Registration Methods Comparison

| Method | Endpoint | Best for | Expiry |
|---|---|---|---|
| Admin UI | Jira Settings → System → Webhooks | One-off, admin-managed | None (permanent) |
| REST v1 (any auth) | `POST /rest/webhooks/1.0/webhook` | Scripts, third-party integrations | None (permanent) |
| REST v3 dynamic (OAuth 2.0) | `POST /rest/api/3/webhook` | OAuth 2.0 apps | 30 days, renewable |
| REST v3 dynamic (Connect) | `POST /rest/api/3/webhook` | Connect Marketplace apps | 30 days, renewable |

---

## Register via REST v1 (Permanent — for scripts/integrations)

```http
POST https://your-domain.atlassian.net/rest/webhooks/1.0/webhook
Authorization: Basic ...
Content-Type: application/json

{
  "name": "my-webhook",
  "url": "https://example.com/webhooks/jira",
  "events": [
    "jira:issue_created",
    "jira:issue_updated",
    "jira:issue_deleted",
    "comment_created"
  ],
  "filters": {
    "issue-related-events-section": "project = PROJ AND issuetype in (Bug, Story)"
  },
  "excludeBody": false,
  "secret": "YOUR_WEBHOOK_SECRET"
}
```

**Manage existing webhooks:**
```
GET    /rest/webhooks/1.0/webhook          # list all
GET    /rest/webhooks/1.0/webhook/{id}     # get one
PUT    /rest/webhooks/1.0/webhook/{id}     # update
DELETE /rest/webhooks/1.0/webhook/{id}     # delete
```

---

## Register via REST v3 (Dynamic — OAuth 2.0 apps, 30-day expiry)

```http
POST /rest/api/3/webhook
Authorization: Bearer ACCESS_TOKEN

{
  "url": "https://example.com/webhooks/jira",
  "webhooks": [
    {
      "jqlFilter": "project = PROJ AND status = 'Done'",
      "events": ["jira:issue_created", "jira:issue_updated"]
    },
    {
      "jqlFilter": "project = SUPPORT",
      "events": ["comment_created", "comment_updated"]
    }
  ]
}
```

Limits: 5 webhooks per user per tenant (OAuth 2.0), 100 per app per tenant (Connect).

**Refresh before expiry (extend 30 days):**
```http
PUT /rest/api/3/webhook/refresh
{
  "webhookIds": [10001, 10002]
}
```

**List registered dynamic webhooks:**
```
GET /rest/api/3/webhook
```

**Delete dynamic webhooks:**
```http
DELETE /rest/api/3/webhook
{ "webhookIds": [10001, 10002] }
```

**Get failed webhooks (for debugging):**
```
GET /rest/api/3/webhook/failed
```

---

## Complete Event Type List

### Issue events (support JQL filtering)
| Event | Trigger |
|---|---|
| `jira:issue_created` | New issue created |
| `jira:issue_updated` | Issue field changed |
| `jira:issue_deleted` | Issue deleted |

### Comment events (support JQL filtering on parent issue)
| Event | Trigger |
|---|---|
| `comment_created` | Comment added |
| `comment_updated` | Comment edited |
| `comment_deleted` | Comment removed |

### Attachment events (support JQL filtering)
| Event | Trigger |
|---|---|
| `attachment_created` | File attached |
| `attachment_deleted` | Attachment removed |

### Worklog events (support JQL filtering)
| Event | Trigger |
|---|---|
| `worklog_created` | Work logged |
| `worklog_updated` | Worklog edited |
| `worklog_deleted` | Worklog removed |

### Issue link events
| Event | Trigger |
|---|---|
| `issuelink_created` | Link between issues created |
| `issuelink_deleted` | Link removed |

### Project events
| Event | Trigger |
|---|---|
| `project_created` | New project |
| `project_updated` | Project settings changed |
| `project_deleted` | Project deleted |
| `project_soft_deleted` | Project moved to trash |
| `project_restored_deleted` | Project restored from trash |
| `project_archived` | Project archived |
| `project_restored_archived` | Project unarchived |

### Version events (JQL filtering ignored)
| Event | Trigger |
|---|---|
| `jira:version_created` | Version created |
| `jira:version_updated` | Version details changed |
| `jira:version_released` | Version marked released |
| `jira:version_unreleased` | Version unrelease |
| `jira:version_deleted` | Version deleted |
| `jira:version_moved` | Version reordered |
| `jira:version_merged` | Versions merged |

### Sprint events (JQL filtering ignored)
| Event | Trigger |
|---|---|
| `sprint_created` | Sprint created |
| `sprint_updated` | Sprint details changed |
| `sprint_started` | Sprint activated |
| `sprint_closed` | Sprint completed |
| `sprint_deleted` | Sprint deleted |

### Board events
| Event | Trigger |
|---|---|
| `board_created` | Board created |
| `board_updated` | Board config changed |
| `board_deleted` | Board deleted |
| `board_configuration_changed` | Column/swimlane config changed |

### User events
| Event | Trigger |
|---|---|
| `user_created` | New user added |
| `user_updated` | User profile changed |
| `user_deleted` | User removed |

### Issue type events
| Event | Trigger |
|---|---|
| `issuetype_created` | Issue type added |
| `issuetype_updated` | Issue type changed |
| `issuetype_deleted` | Issue type removed |

### Filter events
| Event | Trigger |
|---|---|
| `filter_created` | Saved filter created |
| `filter_updated` | Saved filter changed |
| `filter_deleted` | Saved filter removed |

### Issue property events (support JQL filtering)
| Event | Trigger |
|---|---|
| `issue_property_set` | Issue property set |
| `issue_property_deleted` | Issue property deleted |

---

## Payload Structure

### Issue update payload
```json
{
  "timestamp": 1606480436302,
  "webhookEvent": "jira:issue_updated",
  "issue_event_type_name": "issue_comment_edited",
  "user": {
    "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
    "accountType": "atlassian",
    "displayName": "Alice Smith"
  },
  "issue": {
    "id": "10001",
    "key": "PROJ-42",
    "fields": {
      "summary": "Login fails on Safari",
      "status": { "name": "In Progress", "statusCategory": { "key": "indeterminate" } },
      "assignee": { "accountId": "...", "displayName": "Bob Jones" },
      "issuetype": { "name": "Bug" },
      "project": { "key": "PROJ", "name": "My Project" }
    }
  },
  "changelog": {
    "id": "10002",
    "items": [
      {
        "field": "status",
        "fieldtype": "jira",
        "fieldId": "status",
        "from": "10000",
        "fromString": "To Do",
        "to": "10001",
        "toString": "In Progress"
      }
    ]
  },
  "comment": {
    "id": "10003",
    "body": { "type": "doc", "version": 1, "content": [...] },
    "author": { "accountId": "...", "displayName": "Alice Smith" }
  }
}
```

### Dynamic webhook payload additions
When using dynamic webhooks (REST v3), the payload also includes:
```json
{
  "matchedWebhookIds": [10001, 10002]
}
```
This lists which of your registered webhooks matched the event's JQL filter.

---

## HMAC Signature Validation

When a `secret` is set on a webhook, Jira includes an `X-Hub-Signature` header with each delivery.

### Header format
```
X-Hub-Signature: sha256=a4771c39fbe90f317c7824e83ddef3caae9cb3d976c214ace1f2937e133263c9
```

### Validate in Python
```python
import hmac
import hashlib

def validate_jira_webhook(payload_bytes: bytes, secret: str, signature_header: str) -> bool:
    method, _, received_sig = signature_header.partition("=")
    expected_sig = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        getattr(hashlib, method)
    ).hexdigest()
    return hmac.compare_digest(expected_sig, received_sig)

# In your Flask/FastAPI handler:
raw_body = request.get_data()
sig = request.headers.get("X-Hub-Signature", "")
if not validate_jira_webhook(raw_body, WEBHOOK_SECRET, sig):
    return Response("Unauthorized", status=401)
```

### Validate in Node.js
```javascript
const crypto = require('crypto');

function validateJiraWebhook(payloadBuffer, secret, signatureHeader) {
  const [method, receivedSig] = signatureHeader.split('=');
  const expectedSig = crypto
    .createHmac(method, secret)
    .update(payloadBuffer)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expectedSig, 'hex'),
    Buffer.from(receivedSig, 'hex')
  );
}
```

**Test values:**
- Secret: `It's a Secret to Everybody`
- Payload: `Hello World!`
- Expected: `sha256=a4771c39fbe90f317c7824e83ddef3caae9cb3d976c214ace1f2937e133263c9`

---

## Retry Behavior

Jira retries failed webhook deliveries up to **5 times** on these HTTP status codes:
`5xx`, `408`, `409`, `425`, `429`, or connection timeout.

**Retry detection headers:**
```
X-Atlassian-Webhook-Identifier: <unique-per-tenant-id>   # same on retries
X-Atlassian-Webhook-Retry: 1                              # increments with each retry
```

**Webhook types:**
- **Primary webhooks** (single operations): 30-second delivery target
- **Secondary webhooks** (bulk operations like bulk edits): up to 15-minute delivery window

**Best practices for receivers:**
1. Respond `200 OK` as fast as possible (< 5 seconds ideal)
2. Queue the payload for async processing — don't do heavy work in the HTTP handler
3. Use `X-Atlassian-Webhook-Identifier` to detect and deduplicate retries
4. Return `429` if you're overwhelmed — Jira will back off

**Concurrency limits per tenant+host pair:**
- Primary: 20 concurrent requests
- Secondary: 10 concurrent requests

---

## JQL Filtering for Webhooks

Only a **subset of JQL** is supported for webhook event filtering:

**Supported left-hand fields:** `issueKey`, `project`, `issuetype`, `status`, `priority`, `assignee`, `reporter`, `issue.property`, `cf[epicId]`

**Supported operators:** `=`, `!=`, `IN`, `NOT IN`

```json
{
  "jqlFilter": "project = PROJ AND issuetype IN (Bug, Story) AND priority = High"
}
```

> Warning: An empty `jqlFilter` (`""`) matches ALL issues across ALL projects and may leak sensitive data. Always use a specific filter.

> Sprint and version events ignore JQL filters entirely — they fire for all matching events regardless.
