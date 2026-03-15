# AWS CloudFront — Capabilities Reference
For CLI commands, see [cloudfront-cli.md](cloudfront-cli.md).

## Amazon CloudFront

**Purpose**: Global content delivery network (CDN) that caches content at edge locations worldwide for low-latency delivery of static, dynamic, and streaming content.

### Core Concepts

| Concept | Description |
|---|---|
| **Distribution** | The top-level CloudFront resource; has a unique `*.cloudfront.net` domain; two types: Standard and Multi-Tenant (SaaS Manager) |
| **Edge location** | Data center where content is cached; 400+ globally |
| **Regional edge cache** | Intermediate cache between origin and edge locations; larger cache, fewer origin hits |
| **Origin** | Where CloudFront fetches content: S3 bucket, ALB, API Gateway, MediaPackage, or custom HTTP server |
| **Origin group** | Two origins with failover; primary and secondary; CloudFront fails over on specified HTTP status codes |
| **Behavior** | Path pattern matched against the request URL; determines caching, origin, and feature settings per path |
| **Cache policy** | Defines which request attributes (headers, cookies, query strings) are included in the cache key |
| **Origin request policy** | Defines what CloudFront forwards to the origin (beyond the cache key) |
| **Response headers policy** | Add/override HTTP response headers (e.g., CORS, security headers) |

### Origins

| Origin Type | Notes |
|---|---|
| **Amazon S3** | Use Origin Access Control (OAC) to restrict bucket access to CloudFront only |
| **ALB / Custom HTTP** | CloudFront connects using the origin domain; can require HTTPS; supports custom headers for secret validation |
| **API Gateway** | Supported as a custom origin |
| **MediaPackage** | Streaming origin for live/VOD video |

### Origin Access Control (OAC)

Replaces the older Origin Access Identity (OAI). OAC uses SigV4 signing to authenticate CloudFront to S3. Configure the S3 bucket policy to allow `cloudfront.amazonaws.com` principal with a `StringEquals` condition on `AWS:SourceArn` matching the distribution ARN. OAC also supports S3 SSE-KMS.

### Edge Compute

| Option | Runtime | Triggers | Use case |
|---|---|---|---|
| **Lambda@Edge** | Node.js, Python (full Lambda) | Viewer request/response, origin request/response | Complex logic, A/B testing, auth, response generation; runs in regional edge cache PoPs |
| **CloudFront Functions** | JavaScript (lightweight) | Viewer request/response only | Simple URL rewrites, header manipulation, cache key normalization; sub-millisecond; cheaper |

**Key differences**: CloudFront Functions run at all 400+ edge locations (extremely low latency); Lambda@Edge runs at ~13 regional PoPs. CloudFront Functions cannot make network calls or access the request body.

### Access Control

| Feature | Description |
|---|---|
| **Signed URLs** | Restrict access to a single object; include expiration, IP restriction, and signature; use when distributing individual files to end users |
| **Signed cookies** | Restrict access to multiple objects with a single signature; use for authenticated streaming or access to many files |
| **Trusted key groups** | Preferred method for managing key pairs used to sign URLs/cookies; replaces legacy trusted signers |
| **Geo-restriction** | Allow or block requests by country using CloudFront's built-in geo-IP database |
| **WAF integration** | Associate an AWS WAF Web ACL (must be in `us-east-1`) to filter requests at edge locations |

### Cache & Performance

| Feature | Description |
|---|---|
| **Cache invalidation** | Remove objects from edge caches before TTL expires; first 1,000 paths/month free; then charged per path |
| **Price classes** | Limit which edge locations serve content (all, 200-only, 100-only) to reduce cost; trading global reach for lower price |
| **Compression** | CloudFront can compress files (gzip, Brotli) automatically for eligible content types |
| **HTTP/2 and HTTP/3** | Supported by default on all distributions |

### Logging

| Type | Description |
|---|---|
| **Standard logs** | Delivered to S3 hourly; fields include date, IP, status, bytes, referrer, user agent |
| **Real-time logs** | Near real-time delivery to Kinesis Data Streams; configurable sampling rate and field selection |
