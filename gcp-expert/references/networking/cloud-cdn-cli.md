# Cloud CDN — CLI Reference

Cloud CDN is configured through `gcloud compute backend-services` and `gcloud compute backend-buckets` — there is no separate `gcloud cdn` command. CDN settings are attached to backend services/buckets, which are attached to load balancers via URL maps.

---

## Enable and Configure CDN on Backend Services

```bash
# Enable CDN on an existing backend service (USE_ORIGIN_HEADERS mode)
gcloud compute backend-services update my-web-backend \
  --global \
  --enable-cdn

# Enable CDN with CACHE_ALL_STATIC mode
gcloud compute backend-services update my-web-backend \
  --global \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC

# Enable CDN with FORCE_CACHE_ALL mode (for fully static origins)
gcloud compute backend-services update my-static-backend \
  --global \
  --enable-cdn \
  --cache-mode=FORCE_CACHE_ALL

# Set default TTL and max TTL
gcloud compute backend-services update my-web-backend \
  --global \
  --cache-mode=CACHE_ALL_STATIC \
  --default-ttl=3600 \
  --max-ttl=86400 \
  --client-ttl=600

# Enable negative caching
gcloud compute backend-services update my-web-backend \
  --global \
  --enable-cdn \
  --negative-caching

# Enable serve-while-stale (serve stale content for up to 86400s during re-validation)
gcloud compute backend-services update my-web-backend \
  --global \
  --serve-while-stale=86400

# Disable CDN on a backend service
gcloud compute backend-services update my-web-backend \
  --global \
  --no-enable-cdn

# View current CDN configuration on a backend service
gcloud compute backend-services describe my-web-backend \
  --global \
  --format="yaml(cdnPolicy,enableCDN)"
```

---

## CDN Policy (Cache Key Customization)

CDN policy flags must be passed as a JSON/YAML `--cdn-policy` argument for complex configurations, or via the Console. Use `gcloud compute backend-services update` with `--cdn-policy` or individual flags.

```bash
# Customize cache key: exclude all query parameters
gcloud compute backend-services update my-web-backend \
  --global \
  --cdn-policy='queryStringWhitelist=[],includeProtocol=true,includeHost=true'

# Note: For complex CDN policy configuration, use the import/export approach:
# Export current backend service config
gcloud compute backend-services export my-web-backend \
  --global \
  --destination=backend-service.yaml

# Edit backend-service.yaml to add cdnPolicy block:
# cdnPolicy:
#   cacheMode: CACHE_ALL_STATIC
#   defaultTtl: 3600
#   maxTtl: 86400
#   clientTtl: 600
#   negativeCaching: true
#   negativeCachingPolicy:
#   - code: 404
#     ttl: 60
#   - code: 410
#     ttl: 300
#   serveWhileStale: 86400
#   cacheKeyPolicy:
#     includeProtocol: true
#     includeHost: true
#     includeQueryString: true
#     queryStringWhitelist:
#     - lang
#     - version
#     # or use queryStringBlacklist to exclude tracking params:
#     # queryStringBlacklist:
#     # - utm_source
#     # - utm_campaign
#     # - fbclid

# Import the modified configuration
gcloud compute backend-services import my-web-backend \
  --global \
  --source=backend-service.yaml
```

---

## Enable and Configure CDN on Backend Buckets

```bash
# Enable CDN on a backend bucket
gcloud compute backend-buckets update my-static-bucket-backend \
  --enable-cdn

# Enable CDN with FORCE_CACHE_ALL mode on backend bucket
gcloud compute backend-buckets update my-static-bucket-backend \
  --enable-cdn \
  --cache-mode=FORCE_CACHE_ALL \
  --default-ttl=86400 \
  --max-ttl=604800

# Disable CDN on backend bucket
gcloud compute backend-buckets update my-static-bucket-backend \
  --no-enable-cdn

# Describe backend bucket CDN configuration
gcloud compute backend-buckets describe my-static-bucket-backend \
  --format="yaml(cdnPolicy,enableCdn)"
```

---

## Cache Invalidation

```bash
# Invalidate a specific URL path
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/images/hero.jpg"

# Invalidate a path prefix (all files under /static/)
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/static/*"

# Invalidate all cached content
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/*"

# Invalidate a specific host path combination (when URL map has multiple hosts)
gcloud compute url-maps invalidate-cdn-cache my-url-map \
  --global \
  --path="/api/products" \
  --host=api.example.com

# Check invalidation operation status
gcloud compute operations list \
  --filter="operationType=invalidateCache" \
  --global
```

---

## Signed URLs

```bash
# Create a CDN signing key (HMAC)
gcloud compute backend-services update my-web-backend \
  --global \
  --signed-url-cache-max-age=3600

# Add a CDN signing key to a backend service
# Step 1: Generate a random signing key (32 bytes, base64-encoded)
python3 -c "import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())" > key.txt

# Step 2: Add the key to the backend service
gcloud compute backend-services add-signed-url-key my-web-backend \
  --global \
  --key-name=my-signing-key \
  --key-file=key.txt

# Add a CDN signing key to a backend bucket
gcloud compute backend-buckets add-signed-url-key my-static-bucket-backend \
  --key-name=my-signing-key \
  --key-file=key.txt

# List signing keys on a backend service
gcloud compute backend-services describe my-web-backend \
  --global \
  --format="yaml(cdnPolicy.signedUrlKeyNames)"

# Delete a signing key from backend service
gcloud compute backend-services delete-signed-url-key my-web-backend \
  --global \
  --key-name=my-signing-key

# Delete a signing key from backend bucket
gcloud compute backend-buckets delete-signed-url-key my-static-bucket-backend \
  --key-name=my-signing-key

# Generate a signed URL (using sign-url command)
gcloud compute sign-url \
  "https://cdn.example.com/private/file.mp4" \
  --key-name=my-signing-key \
  --key-file=key.txt \
  --expires-in=3600
```

---

## Media CDN (Edge Cache)

Media CDN uses separate `gcloud edge-cache` commands. It is a distinct product from Cloud CDN.

```bash
# Create an Edge Cache origin (pointing to your Cloud Storage or load balancer)
gcloud edge-cache origins create my-media-origin \
  --origin-address=storage.googleapis.com \
  --description="Media origin from GCS"

# Create an Edge Cache keyset (for signed requests)
gcloud edge-cache keysets create my-media-keyset \
  --description="Media CDN signing keys"

# Add a public key to the keyset (ED25519 key)
# Generate key pair: openssl genpkey -algorithm Ed25519 -out private.pem && openssl pkey -in private.pem -pubout -out public.pem
gcloud edge-cache keysets update my-media-keyset \
  --add-public-key="id=key1,managed-token-public-key-file=public.pem"

# Create an Edge Cache service (the CDN endpoint)
gcloud edge-cache services create my-media-service \
  --description="Media CDN service" \
  --routing=routing.yaml

# routing.yaml example:
# hostRules:
# - hosts: [media.example.com]
#   pathMatcher: media-matcher
# pathMatchers:
# - name: media-matcher
#   routeRules:
#   - priority: 1
#     matchRules:
#     - prefixMatch: /videos/
#     routeAction:
#       cdnPolicy:
#         cacheMode: FORCE_CACHE_ALL
#         defaultTtl: 86400s
#         signedRequestMode: REQUIRE_SIGNATURES
#         signedRequestKeyset: my-media-keyset
#       origin: my-media-origin

# Describe an Edge Cache service
gcloud edge-cache services describe my-media-service

# List Edge Cache services
gcloud edge-cache services list

# Invalidate Media CDN cache
gcloud edge-cache services invalidate-cache my-media-service \
  --path="/videos/movie-123/*"

# Delete Edge Cache service
gcloud edge-cache services delete my-media-service
```

---

## Monitoring CDN Cache Performance

```bash
# View CDN cache hit ratio via Cloud Monitoring metrics
# Relevant metrics (query via Cloud Monitoring or gcloud monitoring):
# loadbalancing.googleapis.com/https/request_count
# loadbalancing.googleapis.com/https/total_latencies
# (Filter by cache_result=HIT or MISS)

# Use Cloud Logging to analyze CDN logs
# Log filter for cache hits on a backend service
gcloud logging read \
  'resource.type="http_load_balancer" AND
   jsonPayload.cacheHit=true AND
   jsonPayload.backendTargetProjectNumber="PROJECT_NUMBER"' \
  --limit=50 \
  --format=json

# Log filter for cache misses
gcloud logging read \
  'resource.type="http_load_balancer" AND
   jsonPayload.cacheLookupStatus="MISS"' \
  --limit=50
```
