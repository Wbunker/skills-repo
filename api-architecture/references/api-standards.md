# Industry REST API Standards Reference

Synthesizes conventions from the Microsoft REST API Guidelines, Google API Design Guide (AIP), Zalando RESTful API Guidelines, and community standards (Adidas, Atlassian, Heroku, White House) via masteringapi/rest-api-standards. Divergences are noted explicitly.

## URL and Resource Naming

**Use nouns, not verbs.** URLs identify resources; HTTP methods express actions.

```
GET  /articles        POST /articles        GET /articles/42       # correct
GET  /getArticles     POST /createArticle   POST /articles/delete  # wrong
```

Exception: custom actions that do not map to CRUD. Google and Microsoft allow colon-delimited verbs (`POST /articles/42:publish`). Zalando prefers modeling actions as sub-resources (`POST /articles/42/publications`).

**Plural collection names.** All major standards mandate this. Address individuals by appending an ID to the collection: `GET /customers/8a3b`.

**Kebab-case in paths.** Lowercase, hyphen-separated: `/service-contracts`, `/line-items`. Zalando rule #129 and Microsoft both require this. Google maps protobuf names to kebab-case in REST transcoding.

**Hierarchical nesting.** Alternate collection/ID segments: `/users/{userId}/orders/{orderId}`. Limit depth to three levels; provide top-level shortcuts for globally unique IDs.

**Property and query parameter casing:**

| Standard  | Properties  | Query Params | Example          |
|-----------|-------------|-------------|------------------|
| Microsoft | camelCase   | camelCase   | `firstName`      |
| Google    | camelCase   | camelCase   | `pageToken`      |
| Zalando   | snake_case  | snake_case  | `first_name`     |
| Heroku    | snake_case  | snake_case  | `created_at`     |

Pick one convention and enforce it consistently.

## HTTP Methods and Semantics

| Method   | Semantics                  | Safe | Idempotent | Body | Typical Success |
|----------|----------------------------|------|------------|------|-----------------|
| `GET`    | Retrieve                   | Yes  | Yes        | No   | 200             |
| `POST`   | Create or trigger action   | No   | No         | Yes  | 201 / 200       |
| `PUT`    | Full replace (or create)   | No   | Yes        | Yes  | 200 / 201       |
| `PATCH`  | Partial update             | No   | No*        | Yes  | 200             |
| `DELETE` | Remove                     | No   | Yes        | No   | 204             |

*JSON Merge Patch (RFC 7396) is effectively idempotent; JSON Patch (RFC 6902) may not be.

**POST: creation vs actions.** For creation, return `201 Created` with a `Location` header. For non-CRUD actions, return `200 OK` (synchronous) or `202 Accepted` (async).

**PUT** replaces the entire resource. Omitted fields reset to defaults. If the resource does not exist and the client controls the ID, PUT may create it (`201`).

**PATCH** applies partial changes. Microsoft recommends JSON Merge Patch (`application/merge-patch+json`). Google uses field masks. Limitation: Merge Patch cannot distinguish "set to null" from "omit."

**DELETE** is idempotent. Deleting an already-deleted resource should return `204`, not `404`. Google recommends soft-delete with an `Undelete` custom method.

**Idempotency keys** prevent duplicate creation on POST retries:

```
POST /payments
Idempotency-Key: 8a3b4c5d-e6f7-4a8b-9c0d-1e2f3a4b5c6d
```

Microsoft uses `Repeatability-Request-ID` + `Repeatability-First-Sent`. Stripe popularized `Idempotency-Key`, now a de facto standard. Servers store and replay the response for a given key (typically TTL of 24-48 hours).

## Status Codes

**Success:**

| Code | Name        | Use                                                    |
|------|-------------|--------------------------------------------------------|
| 200  | OK          | GET, PUT, PATCH, synchronous POST action               |
| 201  | Created     | POST/PUT that created a resource (include `Location`)  |
| 202  | Accepted    | Async processing; include status monitor URL           |
| 204  | No Content  | DELETE, or operations with no response body            |

**Redirection:** Prefer `307`/`308` over `301`/`302` to preserve the original HTTP method. A `301` on POST may cause clients to follow up with GET.

**Client errors:**

| Code | Name                   | Use                                                      |
|------|------------------------|----------------------------------------------------------|
| 400  | Bad Request            | Malformed syntax, invalid parameters, missing fields     |
| 401  | Unauthorized           | Missing or invalid credentials                           |
| 403  | Forbidden              | Authenticated but not authorized                         |
| 404  | Not Found              | Resource absent (also use instead of 403 for security)   |
| 409  | Conflict               | Duplicate creation, concurrent edit collision             |
| 412  | Precondition Failed    | `If-Match`/`If-Unmodified-Since` not met                 |
| 422  | Unprocessable Entity   | Well-formed but semantically invalid body                |
| 429  | Too Many Requests      | Rate limit exceeded; include `Retry-After`               |

Zalando prefers `400` for all validation. RFC 9110 reserves `422` for well-formed but unprocessable content.

**Server errors:** `500` (unexpected failure), `502` (bad upstream response), `503` (overloaded/maintenance; include `Retry-After`), `504` (upstream timeout).

## Pagination

**Offset-based:** Simple but breaks under concurrent writes and degrades at high offsets.

```
GET /articles?offset=40&limit=20
```

Microsoft uses OData `$skip`/`$top`.

**Cursor-based (recommended):** Stable under writes, constant performance. Zalando rule #160 and Google (`pageToken`/`nextPageToken`) both prefer this.

```
GET /events?limit=25
-> {"data": [...], "pagination": {"nextCursor": "eyJpZCI6MTAwfQ==", "hasMore": true}}

GET /events?cursor=eyJpZCI6MTAwfQ==&limit=25
```

**Page-based:** `?page=3&pageSize=50`. Syntactic sugar over offset; shares its drawbacks.

**Pagination links.** Zalando and JSON:API include links in the response body (`self`, `first`, `prev`, `next`, `last`). GitHub uses HTTP `Link` headers (RFC 8288). Body links are easier to parse and not subject to header size limits.

| Aspect        | Microsoft              | Google                  | Zalando            |
|---------------|------------------------|-------------------------|--------------------|
| Parameters    | `$skip`, `$top`        | `pageSize`, `pageToken` | `cursor`, `limit`  |
| Style         | Offset                 | Cursor (token)          | Cursor (preferred) |
| Total count   | `@odata.count`         | `totalSize` (optional)  | Discouraged        |

## Filtering, Sorting, and Field Selection

**Filtering** ranges from simple field equality to expression languages:

```
GET /orders?status=shipped&customerId=c-1                          # simple
GET /orders?$filter=status eq 'shipped' and total gt 100           # OData (Microsoft)
GET /v1/projects/p1/logs?filter=severity>=ERROR                    # Google (CEL-inspired)
```

OData operators: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`, `not`, plus functions (`contains`, `startswith`).

**Sorting:**

```
GET /products?$orderby=price desc,name asc      # Microsoft
GET /v1/products?orderBy=price desc              # Google
GET /products?sort=price,name&order=desc,asc     # Zalando
```

**Field selection** reduces payload size:

```
GET /users/u-1?$select=name,email               # Microsoft
GET /v1/users/u-1?fields=name,email              # Google (supports nesting: address(city,zip))
GET /articles/42?fields[articles]=title,body      # JSON:API sparse fieldsets
```

## Error Response Format

**RFC 7807 Problem Details** (`application/problem+json`) -- Zalando mandates (rule #176); becoming the industry default:

```json
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Balance of $30.00 is below the required $50.00.",
  "instance": "/transfers/txn-789"
}
```

Fields: `type` (URI for docs), `title` (stable summary), `status`, `detail` (occurrence-specific), `instance` (occurrence URI). Extensible with custom members.

**Google error model** -- `google.rpc.Status` with typed `details` array:

```json
{
  "error": {
    "code": 429,
    "message": "Quota exceeded for project 'my-project'.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "RATE_LIMIT_EXCEEDED",
      "domain": "googleapis.com",
      "metadata": {"quota": "requests-per-minute", "limit": "100"}
    }]
  }
}
```

Uses canonical status enums (`NOT_FOUND`, `PERMISSION_DENIED`, etc.). Detail types include `ErrorInfo`, `BadRequest`, `PreconditionFailure`, `Help`.

**Microsoft error model** -- nested `innererror` for progressive debugging detail:

```json
{
  "error": {
    "code": "InvalidRange",
    "message": "The value 'abc' is not valid for field 'age'.",
    "target": "age",
    "details": [{"code": "OutOfRange", "message": "Must be 0-150.", "target": "age"}],
    "innererror": {"code": "ValueOutOfRange"}
  }
}
```

The `x-ms-error-code` header duplicates the top-level code for clients that cannot parse the body. Never expose `innererror` to end users.

**Zalando** extends RFC 7807 with `invalid-params` for validation errors:

```json
{"type": "...", "title": "Constraint Violation", "status": 400,
 "invalid-params": [{"name": "email", "reason": "must be valid email"}]}
```

## Versioning Strategies

**Google:** Major version in URL path, no minor/patch: `/v1/users/u-1`. Pre-release channels: `v1alpha`, `v1beta`. New major versions must not depend on previous ones. 180-day minimum beta deprecation.

**Microsoft:** URL path (`/v1.0/`) or query parameter (`?api-version=2024-06-01`). Azure uses date-based version strings.

**Zalando:** Media type versioning preferred (rule #114): `Accept: application/vnd.example.v2+json`. URL versioning discouraged (rule #115). Avoiding versioning entirely through additive-only changes is the ideal (rule #113).

| Strategy        | Pros                                    | Cons                                  |
|-----------------|-----------------------------------------|---------------------------------------|
| URL path        | Explicit, easy routing and caching      | Proliferates base URLs                |
| Query param     | Single base URL, easy defaults          | Forgettable, harder to cache          |
| Media type      | Clean URLs, content negotiation         | Complex tooling, poor discoverability |
| No versioning   | Simplest                                | Requires strict additive evolution    |

URL path versioning dominates in public APIs. Reserve major bumps for truly breaking changes.

## Headers and Content Negotiation

**Standard headers:** `Accept`, `Content-Type`, `Authorization` (Bearer tokens). Return `406 Not Acceptable` or `415 Unsupported Media Type` for mismatches.

**Custom headers:** The `X-` prefix was deprecated by RFC 6648 (2012). Use descriptive names without it. Zalando uses kebab-case with capitalized words (rule #132).

**Conditional requests and optimistic concurrency:**

```
GET /documents/doc-1  ->  ETag: "a1b2c3d4"

PUT /documents/doc-1
If-Match: "a1b2c3d4"   ->  200 OK (success) or 412 Precondition Failed (stale)
```

| Header             | Purpose                                        |
|--------------------|------------------------------------------------|
| `ETag`             | Opaque resource version identifier             |
| `If-Match`         | Write only if ETag matches (optimistic lock)   |
| `If-None-Match`    | Read only if ETag differs (cache validation)   |
| `If-Modified-Since`| Read only if modified after date               |
| `Last-Modified`    | Timestamp of last modification                 |

Microsoft requires ETag support across all APIs. Use strong ETags (no `W/` prefix) for byte-level accuracy.

## Rate Limiting

Include these headers on every response for client self-throttling:

| Header                  | Value                                          |
|-------------------------|------------------------------------------------|
| `X-RateLimit-Limit`     | Max requests in current window                 |
| `X-RateLimit-Remaining` | Requests remaining                             |
| `X-RateLimit-Reset`     | Unix timestamp when window resets              |
| `Retry-After`           | Seconds to wait (on 429 responses)             |

An IETF draft proposes standardized `RateLimit-*` headers without the `X-` prefix.

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/problem+json

{"type": "https://api.example.com/errors/rate-limit", "title": "Rate Limit Exceeded",
 "status": 429, "detail": "Exceeded 1000 req/min. Retry after 30s."}
```

Zalando rule #153 requires 429 responses to include rate limit headers.

## API Deprecation and Sunsetting

**Sunset header (RFC 8594)** communicates removal date. **Deprecation header** signals the resource is deprecated. Zalando rule #189 recommends both:

```
HTTP/1.1 200 OK
Sunset: Sat, 01 Mar 2025 00:00:00 GMT
Deprecation: true
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

**Deprecation lifecycle:**

1. **Announce** -- add `Deprecation: true`, publish migration guide, include `Link` with `rel="successor-version"`.
2. **Warn** -- log usage of deprecated endpoints, conduct client outreach.
3. **Remove** -- after sunset date, return `410 Gone` with replacement details.

Google: 180-day minimum for beta deprecation. Stable APIs: 6-12 months. Zalando rule #185: obtain explicit client approval before shutdown.

## HATEOAS and Hypermedia

The server provides available actions as links, so clients discover transitions rather than hardcoding URLs:

```json
{"id": "ord-482", "status": "pending", "total": 8500,
 "links": [
   {"rel": "self", "href": "/orders/ord-482"},
   {"rel": "cancel", "href": "/orders/ord-482/cancellation", "method": "POST"},
   {"rel": "payment", "href": "/orders/ord-482/payment", "method": "PUT"}
 ]}
```

When the order ships, the `cancel` link disappears. Clients adapting to link presence handle state transitions automatically.

**Formats:** HAL (`_links`/`_embedded`), JSON:API (structured `relationships`/`links`), JSON-LD + Hydra (linked data vocabularies -- most semantic, most complex).

**When it adds value:** workflow-driven APIs (order processing, approvals), APIs needing URL evolution without breaking clients, multi-client discovery scenarios.

**When to skip it:** small stable surface areas, tightly coupled BFF patterns, bandwidth-constrained environments (mobile, IoT).

Most standards acknowledge HATEOAS but do not mandate it. Zalando recommends pagination links (minimal hypermedia). Google omits hypermedia entirely. The majority of production APIs operate at Richardson Maturity Level 2.

## Cross-Standard Comparison

| Topic              | Microsoft                   | Google                    | Zalando                    |
|--------------------|-----------------------------|---------------------------|----------------------------|
| Property casing    | camelCase                   | camelCase                 | snake_case                 |
| Path casing        | kebab-case                  | varies (protobuf mapping) | kebab-case                 |
| Versioning         | URL path or query param     | URL path (`/v1/`)         | Media type (preferred)     |
| Pagination         | OData (`$skip`/`$top`)      | `pageToken`/`pageSize`    | Cursor-based (preferred)   |
| Error format       | `error.code`/`innererror`   | `google.rpc.Status`       | RFC 7807 Problem Details   |
| Filtering          | OData `$filter`             | Custom `filter` language  | Query parameters           |
| Idempotency header | `Repeatability-Request-ID`  | Not specified             | `Idempotency-Key`          |
| Deprecation        | `azure-deprecating` header  | 180-day beta notice       | `Sunset` + `Deprecation`  |
