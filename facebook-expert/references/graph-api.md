# Facebook Graph API

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Authentication & Access Tokens](#authentication--access-tokens)
4. [Permissions](#permissions)
5. [Making API Requests](#making-api-requests)
6. [Key Nodes & Edges Reference](#key-nodes--edges-reference)
7. [Graph API Explorer](#graph-api-explorer)
8. [Versioning & Deprecation](#versioning--deprecation)
9. [Error Handling](#error-handling)
10. [Rate Limits](#rate-limits)

---

## Overview

The Graph API is the primary way to programmatically read and write to the Facebook social graph. All Meta SDKs and products interact with it under the hood.

**Base URL:** `https://graph.facebook.com/v{version}/{node}/{edge}?fields={fields}&access_token={token}`

**Current version:** v22.0 (2025/2026)
**Reference docs:** developers.facebook.com/docs/graph-api

---

## Core Concepts

### Nodes
Individual objects with unique IDs:
- User (`/{user-id}`)
- Page (`/{page-id}`)
- Post (`/{post-id}`)
- Photo (`/{photo-id}`)
- Video (`/{video-id}`)
- Group (`/{group-id}`)
- Event (`/{event-id}`)
- Comment (`/{comment-id}`)
- Ad Account (`/act_{ad-account-id}`)

Use `/me` as shorthand for the authenticated user's node.

### Edges
Connections between nodes (collections):
- `/me/friends` — the user's friends
- `/me/feed` — the user's posts
- `/{page-id}/posts` — a Page's posts
- `/{page-id}/photos` — a Page's photos
- `/{post-id}/comments` — comments on a post

### Fields
Properties of a node, requested via `?fields=`:
- `GET /me?fields=id,name,email`
- `GET /{page-id}?fields=name,fan_count,about,website`
- Nested fields: `GET /me/posts?fields=message,created_time,likes.limit(5){name}`

---

## Authentication & Access Tokens

### Token Types

| Token Type | Description | Expiry |
|---|---|---|
| **User Access Token** | Acts on behalf of a user | 1–2 hours (short-lived); 60 days (long-lived) |
| **Page Access Token** | Acts on behalf of a Page | Non-expiring (if generated from long-lived user token) |
| **App Access Token** | App-level access; no user context | Non-expiring |
| **System User Token** | For automated servers; no user OAuth flow | Long-lived or non-expiring |

### Getting a User Access Token (OAuth 2.0 Flow)

1. **Authorization URL:**
```
https://www.facebook.com/v22.0/dialog/oauth?
  client_id={app-id}
  &redirect_uri={redirect-uri}
  &scope={permissions}
  &response_type=code
```

2. **Exchange code for token:**
```
GET https://graph.facebook.com/v22.0/oauth/access_token?
  client_id={app-id}
  &redirect_uri={redirect-uri}
  &client_secret={app-secret}
  &code={code-from-step-1}
```

3. **Extend to long-lived token (60 days):**
```
GET https://graph.facebook.com/v22.0/oauth/access_token?
  grant_type=fb_exchange_token
  &client_id={app-id}
  &client_secret={app-secret}
  &fb_exchange_token={short-lived-token}
```

### Getting a Page Access Token
```
GET /me/accounts?access_token={user-token}
```
Returns all Pages the user manages with their individual Page Access Tokens.

### Debugging a Token
```
GET https://graph.facebook.com/debug_token?
  input_token={token-to-inspect}
  &access_token={app-id}|{app-secret}
```

---

## Permissions

Apps must request specific permissions in their OAuth scope. Meta requires App Review for most non-basic permissions.

### Public Profile (No Review Required)
- `public_profile` — name, profile picture, age range, gender
- `email` — email address

### Common Permissions (Require App Review)

| Permission | Access |
|---|---|
| `pages_show_list` | List Pages the user manages |
| `pages_read_engagement` | Read Page posts, comments, likes |
| `pages_manage_posts` | Create, edit, delete posts on a Page |
| `pages_manage_metadata` | Read/write Page settings |
| `pages_messaging` | Send/receive Messenger messages on behalf of a Page |
| `read_insights` | Read Page/Post insights |
| `business_management` | Manage Business Manager assets |
| `groups_access_member_info` | Access group member info |
| `publish_to_groups` | Post to Groups on behalf of user |
| `user_posts` | Read the user's posts |
| `user_photos` | Read the user's photos |

### Permission Request Best Practice
- Request only permissions you actively need (principle of least privilege)
- Meta audits apps and may reject requests for unused permissions
- Users can deny individual permissions while approving others — always handle partial permission grants

---

## Making API Requests

### GET (Read)
```bash
curl "https://graph.facebook.com/v22.0/me?fields=id,name&access_token={token}"
```

### POST (Write/Create)
```bash
# Post to a Page's feed
curl -X POST "https://graph.facebook.com/v22.0/{page-id}/feed" \
  -d "message=Hello world" \
  -d "access_token={page-token}"
```

### DELETE
```bash
curl -X DELETE "https://graph.facebook.com/v22.0/{post-id}?access_token={token}"
```

### Batch Requests
Send up to 50 requests in a single HTTP call:
```bash
curl -X POST "https://graph.facebook.com/v22.0/" \
  -d 'access_token={token}' \
  -d 'batch=[
    {"method":"GET","relative_url":"me"},
    {"method":"GET","relative_url":"me/friends?limit=5"}
  ]'
```

### Pagination
Large result sets use cursor-based pagination:
```json
{
  "data": [...],
  "paging": {
    "cursors": {
      "before": "...",
      "after": "..."
    },
    "next": "https://graph.facebook.com/..."
  }
}
```
Use `after` cursor in the next request: `?after={cursor}`

---

## Key Nodes & Edges Reference

### User Node (`/me`)
```
GET /me?fields=id,name,email,picture,friends{name}
POST /me/feed  (create post for user)
GET /me/posts  (user's posts)
GET /me/photos (user's photos)
GET /me/videos (user's videos)
GET /me/groups (groups user belongs to)
GET /me/events (events user is attending)
GET /me/accounts (Pages user manages)
```

### Page Node (`/{page-id}`)
```
GET /{page-id}?fields=name,fan_count,about,website,link
GET /{page-id}/feed           (Page posts)
POST /{page-id}/feed          (create post)
GET /{page-id}/photos         (Page photos)
POST /{page-id}/photos        (upload photo)
GET /{page-id}/videos         (Page videos)
GET /{page-id}/insights       (Page analytics)
GET /{page-id}/conversations  (Messenger conversations)
GET /{page-id}/events         (Page events)
```

### Post Node (`/{post-id}`)
```
GET /{post-id}?fields=message,created_time,likes.summary(true)
GET /{post-id}/comments
GET /{post-id}/likes
POST /{post-id}/comments   (create comment)
DELETE /{post-id}          (delete post)
```

### Event Node (`/{event-id}`)
```
GET /{event-id}?fields=name,start_time,description,attending_count
GET /{event-id}/attending
GET /{event-id}/feed
POST /me/events            (create event for user)
POST /{page-id}/events     (create event for Page)
```

---

## Graph API Explorer

**URL:** developers.facebook.com/tools/explorer

Interactive tool to:
- Build and test Graph API queries without code
- Generate and inspect access tokens
- Explore available fields for any node
- Test permissions

**Usage:**
1. Select your App from the dropdown
2. Click "Generate Access Token" and choose required permissions
3. Enter a path (e.g., `/me?fields=name,email`) and click Submit
4. Copy the generated curl command for use in your code

---

## Versioning & Deprecation

- Meta releases new API versions approximately every 6 months
- Each version is supported for ~2 years after release
- Always specify version in URL: `/v22.0/` (not just `/`)
- Changelog: developers.facebook.com/docs/graph-api/changelog

**Breaking changes:** Subscribe to Meta for Developers blog and the App Dashboard for deprecation notices.

---

## Error Handling

Common error codes:

| Code | Meaning | Action |
|---|---|---|
| `1` | Unknown/internal error | Retry with exponential backoff |
| `2` | Service temporarily unavailable | Retry |
| `4` | App-level rate limit exceeded | Slow down requests |
| `10` | Permission denied | Check app permissions and user consent |
| `17` | User-level rate limit exceeded | Back off for this user |
| `100` | Invalid parameter | Fix the request parameter |
| `190` | Access token expired | Refresh or re-authenticate |
| `200-299` | Permission error | User needs to re-grant permission |

**Error response format:**
```json
{
  "error": {
    "message": "Invalid OAuth access token.",
    "type": "OAuthException",
    "code": 190,
    "fbtrace_id": "..."
  }
}
```

---

## Rate Limits

Meta enforces rate limits at app and user levels:

| Limit Type | Threshold |
|---|---|
| **App-level** | 200 calls per hour per user (default) |
| **Page API** | 4,800 calls per page per 24 hours |
| **Ads API** | 200 calls per ad account per hour |

**Headers to monitor:**
- `X-App-Usage` — current app-level consumption
- `X-Ad-Account-Usage` — ad account consumption

**Best practices:**
- Use batch requests to reduce call count
- Cache responses where possible
- Implement exponential backoff on rate limit errors (code 4, 17)
- Use webhooks instead of polling for real-time data
