# Azure Front Door & CDN — Capabilities

## Overview

Azure Front Door (AFD) is Microsoft's global anycast network for accelerating and securing web applications. The Standard and Premium tiers (launched 2022) unify the classic Azure Front Door, Azure CDN from Microsoft (classic), and add Private Link origin support. Classic Front Door and Azure CDN classic SKUs are being consolidated into AFD Standard/Premium.

---

## Azure Front Door Standard / Premium

### Architecture

- **Anycast network**: 150+ Points of Presence (PoPs) worldwide; client connects to nearest PoP
- Traffic is pulled across Microsoft's private WAN backbone to the origin, avoiding public internet latency/congestion
- Single entry point (AFD endpoint FQDN) for global traffic distribution
- Unified platform: routing, WAF, caching, CDN, Private Link origins, DDoS protection

### SKU Comparison

| Feature | Standard | Premium |
|---|---|---|
| Static/dynamic site acceleration | Yes | Yes |
| Custom domains + HTTPS | Yes | Yes |
| WAF (managed + custom rules) | Custom rules only | Full managed + custom + bot protection |
| Private Link origins | No | Yes |
| Security reports, analytics | Basic | Advanced |
| Microsoft-managed rule sets | No | Yes |
| Bot manager rule set | No | Yes |
| Price (approx.) | Lower | Higher |

### Core Components

| Component | Description |
|---|---|
| Profile | Top-level resource; Standard or Premium tier |
| Endpoint | AFD entry point with a unique FQDN (`*.z01.azurefd.net`) |
| Origin Group | Group of backend origins with load balancing and health probe settings |
| Origin | Individual backend: App Service, Storage, App Gateway, VM, external IP |
| Route | Maps endpoint domain + path to an origin group; controls caching and forwarding |
| Rule Set | Collection of rules to manipulate requests/responses |
| Custom Domain | Your own domain (e.g., `www.example.com`) associated with an endpoint |
| WAF Policy | Web Application Firewall policy (Premium for managed rules) |

### Origins and Origin Groups

- **Origins**: any publicly accessible IP or FQDN, or (Premium only) Private Link-enabled services
- **Origin Group settings**:
  - Load balancing: latency sensitivity (ms), sample size, successful samples
  - Health probes: path, protocol, interval (minimum 5s at PoP level, not origin)
  - Session affinity (enabled/disabled on origin group)
- **Private Link origins (Premium)**: connect AFD to App Service, Internal Load Balancer, Storage, or Application Gateway via Private Endpoint — origin never needs a public IP

### Routing Rules and Caching

- **Route**: binds `domain + path pattern` → `origin group`
  - Accepted protocols: HTTP, HTTPS, or both
  - Forwarding protocol: HTTP only, HTTPS only, or match request
  - Redirect: HTTP → HTTPS redirect built into route
  - Caching: enabled per route with configurable TTL and query string behavior

- **Caching Options**:
  - `IgnoreQueryString`: ignore query params for cache key (good for static assets)
  - `UseQueryString`: include all query params in cache key (good for dynamic pages)
  - `IgnoreSpecifiedQueryStrings` / `IncludeSpecifiedQueryStrings`: granular control
  - Content compression: Brotli + gzip at edge PoPs
  - Cache TTL override: set `Cache-Control` max-age at the edge
  - Purge cache: via portal, CLI, or API for immediate invalidation

### URL Rewrite and Redirect

- **URL Rewrite**: modify request URL before forwarding to origin
  - Source pattern (prefix match or regex), destination, preserve unmatched path
  - Example: rewrite `/api/v1/` to `/v1/` before sending to origin
- **URL Redirect**: return 301/302 to client with new URL
  - Redirect type: Moved (301), Found (302), TemporaryRedirect (307), PermanentRedirect (308)
  - Redirect protocol, host, path, query string can be overridden

### Rules Engine

AFD Rules Engine evaluates conditions and applies actions on requests or responses:

**Conditions (match on)**:
- Request method (GET, POST, etc.)
- Request URL (path, query string, filename, extension)
- Request headers (any header name/value)
- Request cookies
- Client IP address or geo (country/region)
- SSL/TLS protocol version
- Device type (mobile vs desktop)

**Actions**:
- Modify request header (add, overwrite, delete)
- Modify response header
- URL redirect
- URL rewrite
- Cache bypass
- Set cache TTL override
- Set forwarding protocol

**Use cases**:
- Add security headers (`Strict-Transport-Security`, `X-Frame-Options`)
- Geo-block specific countries
- Route mobile clients to a different origin
- Add `Cache-Control` headers for specific content types

### WAF Integration (Premium)

WAF is applied at the PoP level (globally) before traffic reaches origin:

- **Managed Rule Sets**:
  - `Microsoft_DefaultRuleSet_2.1`: OWASP-based, regularly updated by Microsoft
  - `Microsoft_BotManagerRuleSet_1.1`: bot detection and mitigation (good bots allowed, bad bots blocked)
- **Custom Rules**:
  - Match conditions: IP, geo, request URI, headers, cookies, query strings, HTTP method, size
  - Actions: Allow, Block, Log, Redirect (to URL), Rate-limit
  - Priority determines evaluation order
- **Rate Limiting** (custom rule): client IP-based rate limits (requests per minute/5 min)
- **WAF Modes**: Detection (log only) vs Prevention (block and log)
- **WAF Exclusions**: exclude specific request elements (variable, selector) from rule evaluation
- Per-endpoint or profile-level WAF policy association

---

## Azure Front Door vs Application Gateway — Combined Architecture

| Concern | Azure Front Door | Application Gateway |
|---|---|---|
| Scope | Global (150+ PoPs) | Regional (single region) |
| WAF | Global WAF at edge | Regional WAF |
| TLS termination | At edge PoP | At gateway in your VNet |
| Private origin | Private Link (Premium) | VNet-native |
| Path routing | Yes | Yes |
| Custom error pages | Yes | Yes |

### Common Combined Pattern

```
Internet → Azure Front Door (global WAF, caching, anycast)
                    ↓
         Application Gateway (regional WAF, path-based routing, backend pool)
                    ↓
              Backend VMs / App Service in VNet
```

- Front Door handles global distribution, DDoS mitigation, CDN caching, and WAF for OWASP/bot threats
- Application Gateway handles regional routing, TLS re-termination within VNet, and backend health management
- Lock down Application Gateway to only accept traffic from AFD IP ranges (use `AzureFrontDoor.Backend` service tag in NSG/App Gateway)

---

## Azure CDN (Classic — Being Consolidated)

Classic Azure CDN profiles are being migrated to Azure Front Door Standard/Premium. Understanding legacy CDN profiles is still needed during migration periods.

### Classic CDN Providers

| Profile Type | Notes |
|---|---|
| Azure CDN Standard from Microsoft | Classic profile; migration path to AFD Standard |
| Azure CDN Standard from Edgio (formerly Verizon Standard) | Third-party PoP network |
| Azure CDN Premium from Edgio (formerly Verizon Premium) | Advanced rules engine |
| Azure CDN Standard from Akamai | Third-party PoP network |

### Key CDN Features (Classic)

- **Origins**: Storage, Cloud Service, Web App, custom origin
- **Endpoint hostname**: `<name>.azureedge.net`
- **Custom domains**: CNAME to `<name>.azureedge.net`; HTTPS via AFD-managed or customer-managed certs
- **Rules engine**: conditional logic for caching behavior, headers, redirects (capability varies by profile)
- **Geo-filtering**: allow or block content by country/region
- **Query string caching**: ignore, bypass, or use query strings for cache key
- **Compression**: gzip for supported content types
- **HTTPS custom domain**: managed TLS certificates or bring-your-own via DigiCert integration
- **Purge**: content purge via portal, CLI, API; wildcard path support

### Migration to Azure Front Door

Microsoft is consolidating all CDN profiles into Azure Front Door Standard/Premium by October 2027. Classic CDN from Microsoft profiles can be migrated using the in-portal migration tool. Key mapping:
- CDN endpoint → AFD endpoint
- CDN origin → AFD origin
- CDN delivery rules → AFD rule sets
- CDN custom domains → AFD custom domains
