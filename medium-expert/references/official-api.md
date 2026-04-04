# Medium Official API

## Status: Archived

**The official Medium API is no longer supported.** Medium has explicitly stated: "We do not recommend using it."

- No new OAuth2 integrations are being accepted
- Existing integrations continue to function
- Self-issued access tokens still work for personal use

**For reading Medium data programmatically, use the Unofficial API instead** — see `references/unofficial-api.md`.

The official API is still useful for: **publishing stories to your own Medium account programmatically** via self-issued tokens.

---

## Authentication

### Self-Issued Tokens (Recommended for Personal Use)
- Generate in Medium account: Settings → Security → Integration tokens
- Tokens do not expire (but can be revoked)
- Treat like a password — do not expose in public code
- Works for all non-OAuth operations on your own account

### OAuth2 (Existing Integrations Only)
- No new integrations accepted
- Access tokens valid 60 days; refresh tokens do not expire
- Authorization URL: `https://medium.com/m/oauth/authorize`

---

## Base URL

```
https://api.medium.com/v1
```

All requests over HTTPS. Responses wrapped in `{ "data": { ... } }`.

---

## Endpoints

### Users
```
GET /me
```
Returns authenticated user: `id`, `username`, `name`, `url`, `imageUrl`

---

### Publications
```
GET /users/{userId}/publications
```
Lists publications where user is editor or writer. Returns up to 200 publications.

```
GET /publications/{publicationId}/contributors
```
Returns contributors with their `userId` and `role` (editor/writer).

---

### Posts (Create)

**Create post on personal account:**
```
POST /users/{authorId}/posts
```

**Create post in a publication:**
```
POST /publications/{publicationId}/posts
```

**Required fields:**
```json
{
  "title": "Story Title",
  "contentFormat": "html",  // or "markdown"
  "content": "<p>Your content here</p>"
}
```

**Optional fields:**
```json
{
  "tags": ["technology", "writing"],  // max 5, 25 chars each
  "canonicalUrl": "https://yourblog.com/original-post",
  "publishStatus": "draft",  // "draft" | "published" | "unlisted"
  "license": "all-rights-reserved",  // default
  "notifyFollowers": true
}
```

**Notes:**
- Titles over 100 characters are ignored; Medium synthesizes one from content
- Writers can only create **drafts** in publications; editors can publish directly
- `contentFormat: "markdown"` is the easiest for programmatic publishing

---

### Images
```
POST /images
```
Upload image via `multipart/form-data`. Supported: JPEG, PNG, GIF, TIFF.
Returns: `{ "url": "...", "md5": "..." }`

---

## Scopes

| Scope | Access | Extended? |
|---|---|---|
| `basicProfile` | Read user profile | No |
| `listPublications` | List publications | No |
| `publishPost` | Create posts | No |
| `uploadImage` | Upload images | Yes (requires Medium approval) |

Extended scopes are not available for new integrations.

---

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Invalid or missing fields |
| 401 | Invalid/revoked token or insufficient scope |
| 403 | Permission denied or wrong user |

---

## Example: Publish a Draft via Python

```python
import requests

TOKEN = "your-self-issued-token"
USER_ID = "your-medium-user-id"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "title": "My Article Title",
    "contentFormat": "markdown",
    "content": "# My Article\n\nContent goes here.",
    "tags": ["writing", "technology"],
    "publishStatus": "draft"
}

response = requests.post(
    f"https://api.medium.com/v1/users/{USER_ID}/posts",
    json=payload,
    headers=headers
)
print(response.json())
```

Get your `USER_ID` first:
```python
me = requests.get("https://api.medium.com/v1/me", headers=headers)
user_id = me.json()["data"]["id"]
```
