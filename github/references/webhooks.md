# GitHub Webhooks Reference

## Webhook Types

| Type | Scope | Config Location |
|------|-------|-----------------|
| Repository webhook | Events for a single repository | Repo Settings > Webhooks |
| Organization webhook | Events across all repos in an org | Org Settings > Webhooks |
| GitHub App webhook | Events for all installations of the App | App settings, single endpoint |
| Marketplace webhook | Purchase/cancellation events for a listed App | App's Marketplace listing |

Repository and organization webhooks are managed per-resource. GitHub App webhooks use one global endpoint; delivery includes `installation` context to identify which account triggered the event.

---

## Creating and Managing Webhooks via REST API

### Endpoints

| Action | Method | Path |
|--------|--------|------|
| List repo webhooks | GET | `/repos/{owner}/{repo}/hooks` |
| Create repo webhook | POST | `/repos/{owner}/{repo}/hooks` |
| Get repo webhook | GET | `/repos/{owner}/{repo}/hooks/{hook_id}` |
| Update repo webhook | PATCH | `/repos/{owner}/{repo}/hooks/{hook_id}` |
| Delete repo webhook | DELETE | `/repos/{owner}/{repo}/hooks/{hook_id}` |
| Ping repo webhook | POST | `/repos/{owner}/{repo}/hooks/{hook_id}/pings` |
| Redeliver delivery | POST | `/repos/{owner}/{repo}/hooks/{hook_id}/deliveries/{delivery_id}/attempts` |
| List deliveries | GET | `/repos/{owner}/{repo}/hooks/{hook_id}/deliveries` |
| Get a delivery | GET | `/repos/{owner}/{repo}/hooks/{hook_id}/deliveries/{delivery_id}` |

Replace `/repos/{owner}/{repo}` with `/orgs/{org}` for organization webhooks.

For GitHub Apps: `GET/PATCH /app/hook/config`, `GET /app/hook/deliveries`, `POST /app/hook/deliveries/{delivery_id}/attempts`.

### Create Request Body

```json
{
  "name": "web",
  "active": true,
  "events": ["push", "pull_request"],
  "config": {
    "url": "https://example.com/webhook",
    "content_type": "json",
    "secret": "your-secret-token",
    "insecure_ssl": "0"
  }
}
```

### Config Fields

| Field | Values | Description |
|-------|--------|-------------|
| `url` | string | Endpoint to deliver payloads to |
| `content_type` | `json` \| `form` | `json` sends `application/json`; `form` sends `application/x-www-form-urlencoded` with a `payload` key |
| `secret` | string | Used to compute `X-Hub-Signature-256`; store securely |
| `insecure_ssl` | `"0"` \| `"1"` | `"1"` disables SSL verification (not recommended) |

Use `"events": ["*"]` to subscribe to all events.

---

## Webhook Event Types

### Code & Repository

| Event | Trigger |
|-------|---------|
| `push` | Commits pushed to a branch or tag |
| `create` | Branch or tag created |
| `delete` | Branch or tag deleted |
| `fork` | Repository forked |
| `repository` | Repository created, deleted, archived, renamed, transferred, made public/private, etc. |
| `repository_import` | Repository import initiated or completed |
| `public` | Repository changed from private to public (legacy; use `repository`) |

### Pull Requests

| Event | Trigger |
|-------|---------|
| `pull_request` | PR opened, closed, synchronized, labeled, assigned, review requested, converted to draft, ready for review, auto-merge enabled/disabled |
| `pull_request_review` | PR review submitted, edited, dismissed |
| `pull_request_review_comment` | Comment on PR diff created, edited, deleted |
| `pull_request_review_thread` | Review thread resolved or unresolved |

### Issues

| Event | Trigger |
|-------|---------|
| `issues` | Issue opened, edited, deleted, transferred, closed, reopened, assigned, labeled, milestoned, etc. |
| `issue_comment` | Comment on issue or PR created, edited, deleted |
| `label` | Label created, edited, deleted |
| `milestone` | Milestone created, edited, deleted, opened, closed |

### CI/CD & Deployments

| Event | Trigger |
|-------|---------|
| `check_run` | Check run created, completed, rerequested, requested_action |
| `check_suite` | Check suite completed, requested, rerequested |
| `deployment` | Deployment created |
| `deployment_status` | Deployment status created (pending, in_progress, success, failure, error, inactive, waiting, queued) |
| `deployment_protection_rule` | Deployment protection rule evaluation requested |
| `workflow_run` | Actions workflow run requested, in_progress, completed |
| `workflow_job` | Actions workflow job queued, in_progress, completed, waiting |
| `status` | Commit status updated via the Statuses API |

### Packages & Releases

| Event | Trigger |
|-------|---------|
| `release` | Release published, unpublished, created, edited, deleted, prereleased, released |
| `package` | GitHub Package published or updated |
| `registry_package` | Legacy event for GitHub Container Registry; prefer `package` |

### Members & Permissions

| Event | Trigger |
|-------|---------|
| `member` | Collaborator added, removed, or permission changed on a repository |
| `membership` | Member added/removed from a team (org webhook only) |
| `team` | Team created, deleted, edited, added to/removed from repository |
| `team_add` | Repository added to a team |
| `organization` | Member invited, added, removed; org blocked/unblocked |
| `org_block` | User blocked or unblocked by the org |

### Security & Governance

| Event | Trigger |
|-------|---------|
| `security_advisory` | Security advisory published, updated, withdrawn |
| `secret_scanning_alert` | Secret scanning alert created, resolved, revoked, reopened |
| `code_scanning_alert` | Code scanning alert appeared, closed, fixed, reopened, auto-dismissed |
| `dependabot_alert` | Dependabot alert created, dismissed, fixed, reintroduced, reopened, auto-dismissed |
| `repository_vulnerability_alert` | Legacy Dependabot alert event |
| `branch_protection_rule` | Branch protection rule created, edited, deleted |
| `bypass_push_rulesets` | Push ruleset bypass request created or dismissed |

### Projects & Discussions

| Event | Trigger |
|-------|---------|
| `projects_v2` | Projects (v2) created, edited, closed, reopened, deleted |
| `projects_v2_item` | Item added, edited, converted, archived, restored, reordered, deleted |
| `discussion` | Discussion created, edited, deleted, pinned, answered, labeled, category changed, etc. |
| `discussion_comment` | Discussion comment created, edited, deleted |

### GitHub Apps & Installations

| Event | Trigger |
|-------|---------|
| `installation` | App installed, uninstalled, suspended, unsuspended; new_permissions_accepted |
| `installation_repositories` | Repos added/removed from an installation |
| `installation_target` | Installation target (user/org) renamed |
| `github_app_authorization` | User revokes authorization of a GitHub App |

### Marketplace

| Event | Trigger |
|-------|---------|
| `marketplace_purchase` | Purchase, cancelled, pending_change, pending_change_cancelled, changed (plan change) |

### Miscellaneous

| Event | Trigger |
|-------|---------|
| `ping` | Sent once when the webhook is first created |
| `commit_comment` | Commit comment created |
| `gollum` | Wiki page created or updated |
| `star` | Repository starred or unstarred |
| `watch` | User starts watching (subscribes to) a repository |
| `meta` | The webhook itself was deleted |
| `project` | Classic project created, updated, closed, reopened, deleted |
| `project_card` | Classic project card created, edited, moved, deleted, converted |
| `project_column` | Classic project column created, updated, moved, deleted |

---

## Payload Structure

### Common Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | What happened (e.g., `opened`, `closed`, `created`); absent on `push` |
| `sender` | object | User who triggered the event |
| `repository` | object | Repo where the event occurred (absent for some org events) |
| `organization` | object | Org context; present on org webhooks and some repo events |
| `installation` | object | GitHub App installation context; includes `id` for auth |
| `enterprise` | object | Present when the webhook is on an enterprise account |

### Per-Event Key Fields

| Event | Key Fields |
|-------|-----------|
| `push` | `ref`, `before`, `after`, `commits[]`, `head_commit`, `forced`, `compare` |
| `pull_request` | `action`, `number`, `pull_request` (full PR object) |
| `issues` | `action`, `issue` (full issue object) |
| `issue_comment` | `action`, `issue`, `comment` |
| `release` | `action`, `release` |
| `check_run` | `action`, `check_run` (includes `conclusion`, `output`) |
| `check_suite` | `action`, `check_suite` |
| `workflow_run` | `action`, `workflow_run`, `workflow` |
| `workflow_job` | `action`, `workflow_job` (includes `steps[]`) |
| `deployment` | `action`, `deployment`, `deployment.environment` |
| `deployment_status` | `action`, `deployment_status`, `deployment` |
| `installation` | `action`, `installation`, `repositories` |
| `marketplace_purchase` | `action`, `marketplace_purchase` (plan, billing cycle, account) |

---

## Delivery Headers

| Header | Description |
|--------|-------------|
| `X-GitHub-Event` | Event name (e.g., `push`, `pull_request`) |
| `X-GitHub-Delivery` | UUID uniquely identifying this delivery |
| `X-Hub-Signature-256` | HMAC-SHA256 of the raw request body, prefixed `sha256=` |
| `X-Hub-Signature` | HMAC-SHA1 (legacy); prefer `X-Hub-Signature-256` |
| `X-GitHub-Hook-ID` | ID of the webhook that triggered the delivery |
| `X-GitHub-Hook-Installation-Target-ID` | ID of the resource (repo, org) the hook belongs to |
| `X-GitHub-Hook-Installation-Target-Type` | Type: `repository`, `organization`, `app` |
| `Content-Type` | `application/json` or `application/x-www-form-urlencoded` |

---

## HMAC-SHA256 Signature Validation

Compute `HMAC-SHA256(secret, raw_body)` and compare to the `sha256=` prefix stripped from `X-Hub-Signature-256`. Always use a constant-time comparison to prevent timing attacks.

### Python

```python
import hashlib
import hmac

def verify_signature(payload_body: bytes, secret: str, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)

# In a Flask handler:
# body = request.get_data()
# sig  = request.headers.get("X-Hub-Signature-256", "")
# if not verify_signature(body, SECRET, sig):
#     abort(403)
```

### Node.js

```js
const crypto = require("crypto");

function verifySignature(payloadBuffer, secret, signatureHeader) {
  if (!signatureHeader || !signatureHeader.startsWith("sha256=")) return false;
  const expected = "sha256=" + crypto
    .createHmac("sha256", secret)
    .update(payloadBuffer)
    .digest("hex");
  // timingSafeEqual requires same-length buffers
  const a = Buffer.from(expected);
  const b = Buffer.from(signatureHeader);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

// Express example:
// app.use(express.raw({ type: "application/json" }));
// const valid = verifySignature(req.body, process.env.WEBHOOK_SECRET, req.headers["x-hub-signature-256"]);
// if (!valid) return res.sendStatus(403);
```

Always validate against the **raw** request body before any JSON parsing.

---

## Ping Event

When a webhook is created (or when you manually send a ping via `POST /repos/{owner}/{repo}/hooks/{hook_id}/pings`), GitHub sends a `ping` event with `X-GitHub-Event: ping`.

Key payload fields:

| Field | Description |
|-------|-------------|
| `zen` | A random GitHub Zen aphorism |
| `hook_id` | ID of the webhook |
| `hook` | Full webhook config object |

Respond with HTTP 200 to confirm the endpoint is reachable.

---

## Delivery History and Re-delivery

### View Deliveries

```
GET /repos/{owner}/{repo}/hooks/{hook_id}/deliveries
```

Returns a paginated list. Each entry includes `id`, `guid` (same as `X-GitHub-Delivery`), `delivered_at`, `redelivery`, `duration`, `status`, `status_code`, `event`, `action`.

### Get Full Delivery (with request/response detail)

```
GET /repos/{owner}/{repo}/hooks/{hook_id}/deliveries/{delivery_id}
```

Adds `request` (headers + body) and `response` (headers + payload) to the summary fields.

### Redeliver a Delivery

```
POST /repos/{owner}/{repo}/hooks/{hook_id}/deliveries/{delivery_id}/attempts
```

No request body required. Returns `202 Accepted`. GitHub will retry delivery asynchronously. Use the `redelivery: true` flag in the delivery list to distinguish redeliveries from originals.

---

## GitHub App Webhook Differences

- **Single endpoint**: one URL for all events across every installation; use `installation.id` to scope auth.
- **Config managed via API**: `GET /app/hook/config` and `PATCH /app/hook/config` (requires App auth, not installation auth).
- **Installation events**: Apps always receive `installation` and `installation_repositories` events regardless of subscribed events.
- **Permissions gate events**: An App only receives events for resources it has permission to access. Requesting additional permissions triggers an `installation` event with `action: new_permissions_accepted` after the owner approves.
- **No `insecure_ssl` toggle** for App webhooks via the API; configure in the App's settings UI.

---

## Best Practices

| Practice | Detail |
|----------|--------|
| **Respond within 10 seconds** | GitHub expects HTTP 2xx in under 10 s; for slow processing, return 200 immediately and handle the payload asynchronously (queue + worker). |
| **Return 2xx for all processed events** | Non-2xx responses cause GitHub to mark the delivery as failed and schedule retries. |
| **Handle retries idempotently** | Use `X-GitHub-Delivery` as an idempotency key; store processed GUIDs to skip duplicates. |
| **Validate the signature first** | Reject requests missing or failing `X-Hub-Signature-256` before any processing. |
| **Use `json` content type** | `application/json` is easier to parse and preserves types; avoid `form` for new integrations. |
| **Filter events at creation time** | Subscribe only to needed events to reduce noise and load; avoid `"*"` in production. |
| **Rotate secrets periodically** | Update `config.secret` via PATCH; keep a brief dual-validation window during rotation. |
| **Log `X-GitHub-Delivery`** | Always log the delivery UUID for correlation with GitHub's delivery history UI. |
| **Monitor failed deliveries** | Poll `GET /hooks/{id}/deliveries` or watch for `meta` event (hook deleted) as a health signal. |
| **Expect out-of-order delivery** | Network conditions can cause deliveries to arrive out of order; use timestamps or sequence fields in the payload, not delivery order. |
