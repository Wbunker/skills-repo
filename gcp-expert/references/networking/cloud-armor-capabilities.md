# Cloud Armor — Capabilities Reference

## Purpose

Cloud Armor is Google Cloud's managed web application firewall (WAF) and DDoS protection service. It protects internet-facing applications served behind Cloud Load Balancing from web attacks, volumetric DDoS, and malicious traffic. Cloud Armor evaluates rules at Google's network edge before traffic reaches your backends.

---

## Architecture

- Cloud Armor security policies are **attached to backend services** on the load balancer.
- Traffic arrives at the load balancer → security policy evaluated → allowed traffic forwarded to backends; blocked traffic returned with 403/404/redirect.
- Evaluation happens at Google's PoPs — blocked traffic never reaches your VPC or backend instances.
- For volumetric DDoS, Google's network infrastructure absorbs the attack before the security policy layer.

---

## Security Policy Types

| Type | Attachment Point | Use Case |
|---|---|---|
| Backend security policy | Backend service | WAF rules, rate limiting, geo-blocking for internet-facing applications |
| Edge security policy | Backend bucket or backend service with CDN | Allow/deny traffic at the CDN edge; prevent cache poisoning; control who can access cached content |
| Network edge security policy | Cloud Armor Enterprise (preview) | Layer 4 DDoS protection at the edge |

---

## Rule Components

Each security policy consists of ordered rules:

| Component | Description |
|---|---|
| Priority | Integer 0–2,147,483,646. Lower = higher priority. Evaluated in order; first match wins. Default rule is priority 2,147,483,647 (INT32_MAX). |
| Match condition | Expression evaluated against the request. Uses CEL (Common Expression Language) or pre-configured expressions. |
| Action | `allow`, `deny(STATUS_CODE)`, `redirect`, `rate_based_ban`, `throttle` |
| Description | Human-readable rule description |
| Preview mode | Log rule match but don't enforce action. Use for testing before enabling. |

### Default Rule

Every security policy has a default rule at the lowest priority (INT32_MAX):
- Default action: `allow` (permissive default; explicitly tighten for high-security)
- Can be changed to `deny(403)` for allowlist-only policies

---

## Match Conditions (CEL Expressions)

Custom rules use CEL expressions to match request attributes:

| Attribute | Expression | Example |
|---|---|---|
| Source IP | `inIpRange(origin.ip, 'CIDR')` | `inIpRange(origin.ip, '1.2.3.0/24')` |
| Multiple IPs | `inIpRange(origin.ip, 'CIDR') \|\| inIpRange(origin.ip, 'CIDR2')` | |
| Country/Region | `origin.region_code == 'RU'` | |
| Not in country | `!(origin.region_code in ['CN', 'RU', 'KP'])` | |
| Request header | `request.headers['user-agent'].matches('badbot')` | |
| URL path | `request.path.matches('/admin.*')` | |
| HTTP method | `request.method == 'POST'` | |
| Query param | `has(request.query) && request.query.contains('sql_injection')` | |
| Combination | Multiple conditions with `&&` and `\|\|` | |

---

## Preconfigured WAF Rules

Cloud Armor provides preconfigured rule sets based on OWASP ModSecurity Core Rule Set (CRS) 3.3:

| Rule Set ID | Category | Protection Against |
|---|---|---|
| `xss-v33-stable` | Cross-site scripting | XSS attacks in request body, headers, URIs |
| `sqli-v33-stable` | SQL injection | SQLi attacks in request body, headers, URIs |
| `lfi-v33-stable` | Local file inclusion | Path traversal, LFI attacks |
| `rfi-v33-stable` | Remote file inclusion | Remote file inclusion attacks |
| `rce-v33-canary` | Remote code execution | RCE/Shell injection |
| `scannerdetection-v33-stable` | Scanner detection | Automated scanner signatures |
| `protocolattack-v33-stable` | Protocol attacks | HTTP protocol violations |
| `php-v33-stable` | PHP injection | PHP-specific attack vectors |
| `sessionfixation-v33-stable` | Session fixation | Session hijacking attempts |
| `java-v33-stable` | Java attacks | Java deserialization, Log4j |
| `nodejs-v33-stable` | Node.js attacks | Node.js-specific vulnerabilities |
| `cve-canary` | Known CVEs | Specific CVE-based attacks |
| `methodenforcement-v33-stable` | Method enforcement | Block non-standard HTTP methods |

### Sensitivity Levels

Preconfigured rules have sensitivity levels (0–4):
- Level 0: no rules (rule set disabled)
- Level 1: basic protection, low false positives
- Level 2–3: more rules, moderate false positive risk
- Level 4: comprehensive protection, higher false positive risk

**Best practice**: Start with level 1 in preview mode, review false positives in logs, then raise sensitivity and enforce.

### Exclusions

Preconfigured rules may trigger on legitimate application traffic (e.g., a login form sending passwords that match SQL patterns). Exclusions suppress specific rule signatures:
```
--request-header-to-exclude name=Authorization
--request-body-field-to-exclude name=password
```

---

## Adaptive Protection

Cloud Armor Adaptive Protection uses ML to detect and block L7 DDoS attacks:
- Analyzes baseline traffic patterns per backend service.
- Detects anomalous traffic spikes characteristic of L7 DDoS.
- Automatically generates suggested security policy rules to block the attack.
- Alerts sent to Cloud Monitoring and Security Command Center.
- Operators can manually apply suggested rules or configure auto-deploy thresholds.
- Requires Cloud Armor Enterprise subscription for full features (suggested rules, auto-deploy).

---

## Rate Limiting

Rate-based rules limit requests from specific sources to prevent abuse:

| Action | Description |
|---|---|
| `throttle` | Limit request rate per client; excess requests still received but returned with 429. Configurable conform and exceed actions. |
| `rate_based_ban` | Block a client for a duration after exceeding rate threshold. Excess traffic blocked with a configurable deny code. |

Rate can be keyed on:
- ALL (aggregate)
- IP
- X-Forwarded-For header IP
- HTTP header value (e.g., `x-api-key`)
- Region code

---

## Bot Management

Cloud Armor integrates with reCAPTCHA Enterprise for bot detection:

| Action | Description |
|---|---|
| `redirect` with `GOOGLE_RECAPTCHA` | Redirect suspicious requests to a reCAPTCHA challenge page |
| `allow` with `GOOGLE_RECAPTCHA` | Allow but inject a reCAPTCHA JS into the response |
| Exempt tokens | Accept valid reCAPTCHA tokens to bypass bot challenge rules |
| Manual challenge | Requires users to complete a CAPTCHA before accessing content |

---

## Geo-Blocking

Block or allow traffic based on source country:

```
# Block China, Russia, North Korea
expression: origin.region_code in ['CN', 'RU', 'KP']
action: deny(403)

# Allow only US and CA
expression: !(origin.region_code in ['US', 'CA'])
action: deny(403)
```

Country codes follow ISO 3166-1 alpha-2 standard.

---

## Threat Intelligence

Cloud Armor Enterprise includes Google's Threat Intelligence feeds:
- `iplist-tor-exit-nodes`: known Tor exit nodes
- `iplist-known-malicious-ips`: IP addresses with known malicious activity
- `iplist-search-engine-crawlers`: Google/Bing/Yahoo crawler IPs (use for allowlisting crawlers)
- `iplist-vpn-providers`: known VPN provider IP ranges
- Feeds are automatically updated — no manual IP list management required

---

## Cloud Armor Enterprise

Cloud Armor Enterprise (paid tier) provides:
- Named IP lists (threat intelligence feeds above)
- DDoS response support (access to Google DDoS response team)
- Adaptive Protection with auto-deploy
- Higher request limits
- Network-layer DDoS (Layer 3/4) protection visibility

---

## Important Constraints

- **HTTPS LB only**: Cloud Armor attaches to backend services on external HTTP(S) load balancers. Not available for internal load balancers.
- **Rule limit**: 100 rules per security policy; up to 20 security policies per project (can be increased via quota).
- **Preview mode for testing**: Always deploy new WAF rules in preview mode first. Review false positives in Cloud Logging before enforcing.
- **Preconfigured rules are signatures**: They may flag legitimate traffic. Test with your actual application traffic, not just synthetic tests.
- **Adaptive Protection baseline**: Adaptive Protection needs ~24 hours of traffic to establish a baseline before it can detect anomalies.
- **No blocking of GCP-internal traffic**: Cloud Armor only inspects external traffic arriving through the load balancer. Internal VPC traffic to backends is not filtered by Cloud Armor.
- **Rate limiting granularity**: Rate limits apply per VIP + rule combination. A single backend service can have multiple rate rules at different priorities.
