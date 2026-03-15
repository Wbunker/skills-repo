# Cloud CDN — Capabilities Reference

## Purpose

Cloud CDN (Content Delivery Network) leverages Google's global network of edge points of presence (PoPs) — 200+ locations worldwide — to cache and serve content close to users, reducing latency and origin server load. Cloud CDN is enabled on backend services (backed by MIGs, GKE, Cloud Run) or backend buckets (Cloud Storage) attached to an external Application Load Balancer.

---

## How Cloud CDN Works

1. A user requests `https://cdn.example.com/image.jpg`
2. DNS resolves to the load balancer's anycast IP
3. The request arrives at the nearest Google edge PoP
4. Cloud CDN checks its edge cache:
   - **Cache hit**: served immediately from the edge; does not reach origin
   - **Cache miss**: request forwarded to the origin backend; response cached at the edge (if cacheable); served to client
5. Subsequent requests for the same cache key are served from the edge

---

## Cache Modes

The cache mode controls when Cloud CDN caches responses from the origin:

| Cache Mode | Description | When to Use |
|---|---|---|
| `USE_ORIGIN_HEADERS` | Caches responses only when origin sets explicit `Cache-Control: public` or `Expires` headers with valid max-age. Respects `Cache-Control: no-store`, `no-cache`, and `private`. | Default. Origin controls caching behavior. Use when your app sets correct cache headers. |
| `CACHE_ALL_STATIC` | Caches responses with static content MIME types (CSS, JS, images, fonts, etc.) regardless of origin cache headers, UNLESS the origin sets `Cache-Control: no-store` or `private`. Also caches responses following `USE_ORIGIN_HEADERS` rules. | Mixed apps where static assets should be cached even if origin doesn't set headers. |
| `FORCE_CACHE_ALL` | Caches ALL successful responses (200, 203, 206, 300, 301, 302, 307, 308, 404, 410) with a positive TTL, overriding any `no-store` or `private` directives from the origin. Does NOT cache `Set-Cookie` responses. | Static-only origins, object storage backends, fully cacheable content. Do NOT use if any responses are user-specific. |

---

## Cache Key Customization

The cache key determines when two requests are considered the same (cache hit vs. miss). By default, the cache key is the full URL (scheme + host + path + query string).

Custom cache key options:

| Option | Description |
|---|---|
| Include/exclude query parameters | Exclude tracking params (e.g., `utm_source`, `fbclid`) that don't affect content to improve hit rate |
| Include specific query params only | Only include params that actually affect the response |
| Include/exclude request headers | Include `Accept-Language` if serving localized content |
| Include/exclude cookies | Include a specific cookie if content varies by cookie value |
| Include host header | Exclude to serve same cached content for multiple hostnames |

Example: if your URL is `/api/products?lang=en&utm_campaign=spring`, and `utm_campaign` does not affect the response, exclude it from the cache key. This increases the cache hit rate for `/api/products?lang=en` regardless of UTM parameters.

---

## TTL Settings

When Cloud CDN caches a response, the TTL determines how long it is cached:

| Setting | Description |
|---|---|
| `default-ttl` | TTL used when origin sends no `Cache-Control` max-age (only in `CACHE_ALL_STATIC` and `FORCE_CACHE_ALL` modes). Default: 3600s. |
| `max-ttl` | Maximum TTL regardless of origin headers. Cloud CDN caps origin-specified max-age at this value. Default: 86400s. |
| `client-ttl` | Maximum TTL for client browsers (`Cache-Control: max-age`). Separate from CDN cache TTL. |
| `negative-caching` | Cache error responses (404, 410, etc.) with a short TTL to prevent origin overload during errors. |

---

## Signed URLs and Signed Cookies

Protect private content from unauthorized access using cryptographic signatures.

### Signed URLs

- A URL with an expiration time and HMAC signature appended as query parameters
- Client cannot access the content without the signature
- Best for: one-time downloads, time-limited access to individual files

URL format:
```
https://cdn.example.com/private-file.mp4?Expires=1709280000&KeyName=my-key&Signature=base64url-signature
```

### Signed Cookies

- An HTTP cookie (`Cloud-CDN-Cookie`) containing expiration and signature
- All requests from the client within the session use the same cookie
- Best for: streaming video, authenticated media sessions, accessing multiple files

### CDN Key Types

| Key Type | Description | Best For |
|---|---|---|
| HMAC key | Symmetric key. Fast to generate signatures. Server and CDN share secret. | Most use cases |
| RSA key | Asymmetric key. Private key signs; public key verifies. Rotate private key without updating CDN. | High-security; key rotation |

---

## Negative Caching

Negative caching caches error responses (4xx, 5xx) to prevent thundering herd when an origin is down or a resource doesn't exist.

- Enable with `--negative-caching`
- Configure per-status-code TTLs: e.g., 404 cached for 60s, 410 for 300s
- Prevents the origin from receiving repeated requests for missing resources

---

## Serve Stale

When a cached response expires and the origin is unavailable or slow, Cloud CDN can serve the stale (expired) cached response:
- `--serve-while-stale=N`: serve stale content for up to N seconds while re-validating in the background
- Improves availability during origin failures or slow revalidations

---

## Cache Invalidation

When content changes at the origin, cached copies at edge nodes can be invalidated:

```bash
# Invalidate a specific URL
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/images/hero.jpg"

# Invalidate a path pattern
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/static/*"

# Invalidate everything
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/*"
```

**Notes on invalidation**:
- Invalidation is eventually consistent — may take several minutes to propagate globally
- Invalidation costs money ($0.005 per URL path after the free monthly allowance)
- Prefer versioned URLs (`/static/app.v2.js`) to avoid needing invalidation

---

## Cloud CDN vs. Media CDN

| Feature | Cloud CDN | Media CDN |
|---|---|---|
| PoP network | 200+ locations (Google's network) | 1700+ PoPs including ISP-level CDN peering |
| Optimized for | Web apps, APIs, general static assets | Large media files (video streaming, large downloads) |
| Pricing | Per-request + per-GB | Per-GB only (no per-request fee) |
| Streaming protocols | Basic HTTP | HLS, DASH, CMAF with segment-level caching |
| Latency | Very low (general web) | Optimized for high-throughput large file delivery |
| Request signing | Signed URLs/cookies | Signed requests with Token and ED25519 signing |
| Route control | Via Cloud LB URL map | Dedicated Media CDN routing |
| Use case | App static assets, API acceleration | Video-on-demand, live streaming, game downloads |

**Decision rule**: Use Cloud CDN for web applications, API caching, and standard static assets. Use Media CDN for video streaming, large file downloads, or when you need ISP-level CDN peering for highest video quality.

---

## Cache Behavior for Common Content Types

Cloud CDN respects these content types as "static" in `CACHE_ALL_STATIC` mode:

- Images: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml`, `image/x-icon`
- Video/Audio: `video/mp4`, `audio/mpeg`, etc.
- Web assets: `text/css`, `application/javascript`, `application/x-javascript`, `text/javascript`
- Fonts: `font/woff2`, `application/font-woff`, `font/ttf`
- Documents: `application/pdf`

---

## Important Constraints

- **Cloud CDN requires external Application LB**: Cloud CDN is only available on external HTTP(S) Load Balancers (global and classic). Not available on internal LBs or Network LBs.
- **No caching of POST requests**: Only GET and HEAD requests are cacheable. POST responses are never cached.
- **No caching with Set-Cookie (FORCE_CACHE_ALL)**: Even in `FORCE_CACHE_ALL` mode, responses containing `Set-Cookie` are not cached to prevent sharing session cookies across users.
- **Bypass cache**: Set `Cache-Control: no-store` on the origin response. Or use `Pragma: no-cache`.
- **Max object size**: Individual cached objects can be up to 100 GB.
- **HTTPS required for cookies**: Signed cookies require HTTPS.
- **Vary header**: Cloud CDN partially supports the `Vary` header. `Vary: Accept-Encoding` is handled automatically. Other `Vary` values (like `Vary: Cookie`) result in cache bypass — use cache key customization instead.
