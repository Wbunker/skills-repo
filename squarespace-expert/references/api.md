# Squarespace Commerce API Reference

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [General Conventions](#general-conventions)
4. [Rate Limits](#rate-limits)
5. [Error Handling](#error-handling)
6. [Products API (v2)](#products-api-v2)
7. [Inventory API (v1)](#inventory-api-v1)
8. [Orders API (v1)](#orders-api-v1)
9. [Transactions API (v1)](#transactions-api-v1)
10. [Profiles API (v1)](#profiles-api-v1)
11. [Websites API (v1)](#websites-api-v1)
12. [Webhook Subscriptions API (v1)](#webhook-subscriptions-api-v1)
13. [Webhooks — Event Delivery](#webhooks--event-delivery)

---

## Overview

Squarespace has two API generations that coexist:

| Base URL | Resources |
|---|---|
| `https://api.squarespace.com/v2/commerce/` | Products (newer) |
| `https://api.squarespace.com/1.0/` | Orders, Inventory, Transactions, Profiles, Webhooks, Websites |

All API access is REST over HTTPS. All request and response bodies are JSON.

**Plan requirements:** Core, Plus, Advanced, Commerce Basic, or Commerce Advanced plans required for API access.

---

## Authentication

### API Key

Generate in Squarespace Admin → Settings → Developer Tools → API Keys.

Available permission scopes when creating a key:
- `Orders` — view and manage orders
- `Forms` — access form submissions
- `Inventory` — view and update inventory
- `Transactions` — view transaction records

Required headers on every request:
```http
Authorization: Bearer YOUR_API_KEY
User-Agent: YourAppName/1.0 (contact@yourdomain.com)
```

### OAuth 2.0

Use OAuth for apps that access multiple Squarespace sites. Register via Squarespace support to obtain `client_id` and `client_secret`.

**Authorization URL:**
```
GET https://login.squarespace.com/api/1/login/oauth/provider/authorize
  ?client_id=CLIENT_ID
  &redirect_uri=REDIRECT_URI
  &scope=website.orders,website.inventory
  &state=RANDOM_STATE
  &access_type=offline        # include for refresh token
  &website_id=SITE_ID         # optional: pre-select site
```

**Token exchange:**
```http
POST https://login.squarespace.com/api/1/login/oauth/provider/tokens
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=CLIENT_ID
&client_secret=CLIENT_SECRET
&redirect_uri=REDIRECT_URI
&code=AUTH_CODE
```

**Token lifetimes:**
- Access token: 30 minutes
- Refresh token: 7 days, one-time use (new pair issued on each refresh)

**OAuth scopes:**

| Scope | Permission |
|---|---|
| `website.orders` | View and fulfill orders |
| `website.orders.read` | View orders only |
| `website.transactions.read` | View transactions |
| `website.inventory` | View and update inventory |
| `website.inventory.read` | View inventory only |
| `website.products` | View and modify products |
| `website.products.read` | View products only |

**Note:** Webhook subscription management requires OAuth (not API keys).

---

## General Conventions

- **Partial updates:** Use POST (not PATCH) with only the fields to change
- **Timestamps:** ISO 8601 format (e.g., `2024-01-15T12:00:00Z`)
- **Monetary values:** Object with `currency` (ISO 4217) and `value` (decimal string)
  ```json
  { "currency": "USD", "value": "29.99" }
  ```
- **Pagination:** Cursor-based; max 50 items per page
  - Response includes `pagination.nextPageCursor` when more results exist
  - Pass `cursor=NEXT_PAGE_CURSOR` as query param

---

## Rate Limits

| Scope | Limit |
|---|---|
| General (all endpoints) | 300 requests/minute (5 req/sec) |
| Create Order (API key only) | 100 requests/hour per website |

- OAuth Create Order calls are **not** subject to the 100/hour limit
- Exceeded limit returns `429 Too Many Requests`
- Wait 1 minute before retrying after a 429

---

## Error Handling

**Error response schema:**
```json
{
  "type": "ERROR_TYPE",
  "subtype": "SKU_UNAVAILABLE",
  "message": "Human-readable description",
  "contextId": "request-uuid",
  "details": [ ... ]
}
```

**Common HTTP status codes:**

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No content (successful delete) |
| 400 | Bad request / validation error |
| 404 | Resource not found |
| 409 | Conflict (concurrent modification, insufficient stock) |
| 429 | Rate limit exceeded |

**Common subtypes:** `SKU_UNAVAILABLE`, `URL_SLUG_UNAVAILABLE`, `INSUFFICIENT_STOCK`

---

## Products API (v2)

Base: `https://api.squarespace.com/v2/commerce/products`

**Product types:** `PHYSICAL`, `SERVICE`, `GIFT_CARD`, `DIGITAL`

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/v2/commerce/products` | List products |
| POST | `/v2/commerce/products` | Create product |
| GET | `/v2/commerce/products/{productIdCsvs}` | Get up to 50 products by ID |
| POST | `/v2/commerce/products/{productId}` | Update product (partial) |
| DELETE | `/v2/commerce/products/{productId}` | Delete product |
| POST | `/v2/commerce/products/{productId}/variants` | Create variant |
| POST | `/v2/commerce/products/{productId}/variants/{variantId}` | Update variant |
| DELETE | `/v2/commerce/products/{productId}/variants/{variantId}` | Delete variant |
| POST | `/v2/commerce/products/{productId}/variants/{variantId}/image` | Associate image to variant |
| POST | `/v2/commerce/products/{productId}/images` | Upload image (multipart/form-data) |
| POST | `/v2/commerce/products/{productId}/images/{imageId}` | Update image alt text |
| DELETE | `/v2/commerce/products/{productId}/images/{imageId}` | Delete image |
| POST | `/v2/commerce/products/{productId}/images/{imageId}/order` | Reorder images |
| GET | `/v2/commerce/products/{productId}/images/{imageId}/status` | Check image processing status |

**List products query params:**
- `modifiedAfter`, `modifiedBefore` — ISO 8601 date filter
- `cursor` — pagination cursor
- `query` — text search
- `type[]` — filter by product type

**Constraints:**
- Max 100 images per product
- SKU: max 60 characters
- Variant attributes: max 100 chars per key and value, max 6 attribute pairs

---

## Inventory API (v1)

Base: `https://api.squarespace.com/1.0/commerce/inventory`

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/commerce/inventory` | List all inventory (paginated) |
| GET | `/1.0/commerce/inventory/{variantIdCsvs}` | Get up to 50 variants by ID |
| POST | `/1.0/commerce/inventory/adjustments` | Adjust stock quantities |

**InventoryItem fields:** `variantId`, `descriptor`, `quantity`, `isUnlimited`, `sku`

**Adjustment request body:**
```json
{
  "incrementOperations": [{ "variantId": "abc", "quantity": 5 }],
  "decrementOperations": [{ "variantId": "abc", "quantity": 2 }],
  "setFiniteOperations": [{ "variantId": "abc", "quantity": 10 }],
  "setUnlimitedOperations": [{ "variantId": "abc" }]
}
```

Returns `409` on concurrent modification, insufficient stock, or exceeding max quantity.

---

## Orders API (v1)

Base: `https://api.squarespace.com/1.0/commerce/orders`

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/commerce/orders` | List orders |
| POST | `/1.0/commerce/orders` | Create order |
| GET | `/1.0/commerce/orders/{id}` | Get order |
| POST | `/1.0/commerce/orders/{id}/fulfillments` | Fulfill order |

**List orders query params:** `customerId`, `modifiedAfter`, `modifiedBefore`, `cursor`, `fulfillmentStatus`

**Order statuses:** `PENDING`, `FULFILLED`, `CANCELED`

**Create order required fields:**
```json
{
  "channelName": "MyChannel",           // max 30 chars
  "createdOn": "2024-01-15T12:00:00Z",
  "externalOrderReference": "ext-123",  // max 200 chars
  "fulfillments": [],                   // up to 100
  "grandTotal": { "currency": "USD", "value": "29.99" },
  "lineItems": [ ... ],
  "priceTaxInterpretation": "EXCLUSIVE" // or "INCLUSIVE"
}
```

Create order requires `Idempotency-Key` header to prevent duplicate orders on retry.

**Fulfill order body:**
```json
{
  "shipments": [
    {
      "trackingNumber": "1Z999...",
      "carrierName": "UPS",
      "trackingUrl": "https://..."
    }
  ],
  "shouldSendNotification": true
}
```

---

## Transactions API (v1)

Base: `https://api.squarespace.com/1.0/commerce/transactions`

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/commerce/transactions` | List all transactions |
| GET | `/1.0/commerce/transactions/{documentIdCsvs}` | Get up to 50 transactions |

**Query params:** `cursor`, `modifiedAfter`, `modifiedBefore`

**Transaction data available:** total amounts, net payments, sales, shipping, taxes, payment method, card type, provider, external transaction IDs, processing fees, refunds, exchange rates, void flag

---

## Profiles API (v1)

Base: `https://api.squarespace.com/1.0/profiles`

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/profiles` | List profiles |
| GET | `/1.0/profiles/{profileIdCsvs}` | Get up to 50 profiles |

**Profile fields:** `id`, `email`, `firstName`, `lastName`, `hasAccount`, `isCustomer`, `acceptsMarketing`, `shippingAddress`, `createdOn`, plus transaction summary (order count, donation count, first/last order dates, totals)

**List query params:**
- `email` — URL-encoded, case-insensitive exact match
- `filter` — `isCustomer` or `hasAccount`
- `sortField` — `createdOn`, `id`, `email`, `lastName`
- `sortDirection` — `asc` or `dsc`

**Note:** Slight delay between order creation and profile reflection in API.

---

## Websites API (v1)

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/authorization/member` | Get OAuth token owner's profile |
| GET | `/1.0/authorization/website` | Get website details (API key or token) |
| GET | `/1.0/commerce/store_pages` | List store pages (paginated) |

**Website response fields:** site ID, title, currency, language, time zone, location, measurement standard, URL

**Store page fields:** page ID, title, URL slug, enabled status

---

## Webhook Subscriptions API (v1)

**Requires OAuth** (API keys not supported for webhook management).

Base: `https://api.squarespace.com/1.0/commerce/webhook_subscriptions`

| Method | Path | Description |
|---|---|---|
| GET | `/1.0/commerce/webhook_subscriptions` | List all subscriptions |
| POST | `/1.0/commerce/webhook_subscriptions` | Create subscription |
| GET | `/1.0/commerce/webhook_subscriptions/{id}` | Get subscription |
| POST | `/1.0/commerce/webhook_subscriptions/{id}` | Update subscription |
| DELETE | `/1.0/commerce/webhook_subscriptions/{id}` | Delete subscription |
| POST | `/1.0/commerce/webhook_subscriptions/{id}/actions/rotateSecret` | Rotate HMAC secret |
| POST | `/1.0/commerce/webhook_subscriptions/{id}/actions/sendTestNotification` | Send test event |

Subscriptions never expire.
The HMAC secret is returned **only** at creation or after rotation — store it immediately.

---

## Webhooks — Event Delivery

**Available event topics:**
- `extension.uninstall`
- `order.create`
- `order.update`

**Notification payload:**
```json
{
  "id": "notification-uuid",
  "websiteId": "site-id",
  "subscriptionId": "sub-id",
  "topic": "order.create",
  "createdOn": "2024-01-15T12:00:00Z",
  "data": { }
}
```

**Notification headers:**
```http
User-Agent: Squarespace/1.0
Content-Type: application/json
Squarespace-Signature: <hmac-hex-digest>
```

**Signature verification (HMAC-SHA256):**
```javascript
const crypto = require('crypto');
const expectedSig = crypto
  .createHmac('sha256', Buffer.from(secret, 'hex'))
  .update(rawRequestBody)
  .digest('hex');
const isValid = crypto.timingSafeEqual(
  Buffer.from(expectedSig),
  Buffer.from(headerSig)
);
```

Always use **constant-time comparison** to prevent timing attacks.

Squarespace may add new fields to webhook payloads without a version bump — write tolerant parsers.
