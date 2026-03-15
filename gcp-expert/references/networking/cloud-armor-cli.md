# Cloud Armor — CLI Reference

---

## Security Policies

```bash
# Create a new security policy
gcloud compute security-policies create my-security-policy \
  --description="WAF policy for production API"

# Create an edge security policy (for CDN-enabled backends)
gcloud compute security-policies create my-edge-policy \
  --type=CLOUD_ARMOR_EDGE \
  --description="Edge policy for CDN backend"

# Describe a security policy (view all rules)
gcloud compute security-policies describe my-security-policy

# List all security policies
gcloud compute security-policies list

# Export security policy to JSON (for version control)
gcloud compute security-policies export my-security-policy \
  --file-name=my-security-policy.json \
  --file-format=json

# Export to YAML
gcloud compute security-policies export my-security-policy \
  --file-name=my-security-policy.yaml \
  --file-format=yaml

# Import security policy from file (replaces all rules)
gcloud compute security-policies import my-security-policy \
  --file-name=my-security-policy.json \
  --file-format=json

# Delete a security policy (must detach from all backends first)
gcloud compute security-policies delete my-security-policy
```

---

## Rules — List and Describe

```bash
# List all rules in a security policy
gcloud compute security-policies rules list my-security-policy \
  --format="table(priority,description,action,preview)"

# Describe a specific rule by priority
gcloud compute security-policies rules describe 1000 \
  --security-policy=my-security-policy
```

---

## Rules — IP Allow/Deny

```bash
# Allow traffic from a trusted IP range (higher priority = lower number)
gcloud compute security-policies rules add-rule 100 \
  --security-policy=my-security-policy \
  --description="Allow office network" \
  --expression="inIpRange(origin.ip, '203.0.113.0/24')" \
  --action=allow

# Deny a specific IP
gcloud compute security-policies rules add-rule 200 \
  --security-policy=my-security-policy \
  --description="Block known bad IP" \
  --expression="inIpRange(origin.ip, '198.51.100.1/32')" \
  --action=deny-403

# Block a list of IP ranges
gcloud compute security-policies rules add-rule 300 \
  --security-policy=my-security-policy \
  --description="Block known bad ranges" \
  --expression="inIpRange(origin.ip, '192.0.2.0/24') || inIpRange(origin.ip, '198.51.100.0/24')" \
  --action=deny-403

# Block all traffic except specific ranges (default deny + allowlist)
# Step 1: Update the default rule to deny
gcloud compute security-policies rules update 2147483647 \
  --security-policy=my-security-policy \
  --action=deny-403 \
  --description="Default deny all"

# Step 2: Add allow rules for trusted sources
gcloud compute security-policies rules add-rule 100 \
  --security-policy=my-security-policy \
  --description="Allow production network" \
  --expression="inIpRange(origin.ip, '10.0.0.0/8')" \
  --action=allow
```

---

## Rules — Geo-Blocking

```bash
# Block traffic from specific countries
gcloud compute security-policies rules add-rule 500 \
  --security-policy=my-security-policy \
  --description="Block high-risk regions" \
  --expression="origin.region_code in ['CN', 'RU', 'KP', 'IR']" \
  --action=deny-403

# Allow only specific countries (deny all others)
gcloud compute security-policies rules add-rule 500 \
  --security-policy=my-security-policy \
  --description="Allow US and CA only" \
  --expression="!(origin.region_code in ['US', 'CA'])" \
  --action=deny-403

# Block country but allow specific IP from that country
gcloud compute security-policies rules add-rule 400 \
  --security-policy=my-security-policy \
  --description="Allowlist partner IP from blocked region" \
  --expression="inIpRange(origin.ip, '1.2.3.4/32')" \
  --action=allow

# Geo rule at lower priority (500) fires after allowlist (400) for matching IPs
```

---

## Rules — Preconfigured WAF Rules

```bash
# List available preconfigured expression sets
gcloud compute security-policies list-preconfigured-expression-sets

# Add SQLi protection (sensitivity level 1, stable)
gcloud compute security-policies rules add-rule 10000 \
  --security-policy=my-security-policy \
  --description="SQLi protection" \
  --expression="evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 1})" \
  --action=deny-403

# Add XSS protection
gcloud compute security-policies rules add-rule 10001 \
  --security-policy=my-security-policy \
  --description="XSS protection" \
  --expression="evaluatePreconfiguredWaf('xss-v33-stable', {'sensitivity': 1})" \
  --action=deny-403

# Add LFI (Local File Inclusion) protection
gcloud compute security-policies rules add-rule 10002 \
  --security-policy=my-security-policy \
  --description="LFI protection" \
  --expression="evaluatePreconfiguredWaf('lfi-v33-stable', {'sensitivity': 1})" \
  --action=deny-403

# Add RCE protection
gcloud compute security-policies rules add-rule 10003 \
  --security-policy=my-security-policy \
  --description="RCE protection" \
  --expression="evaluatePreconfiguredWaf('rce-v33-canary', {'sensitivity': 1})" \
  --action=deny-403

# Add Scanner Detection
gcloud compute security-policies rules add-rule 10004 \
  --security-policy=my-security-policy \
  --description="Scanner detection" \
  --expression="evaluatePreconfiguredWaf('scannerdetection-v33-stable', {'sensitivity': 1})" \
  --action=deny-403

# Add rule in PREVIEW mode (log but don't block — for testing)
gcloud compute security-policies rules add-rule 10010 \
  --security-policy=my-security-policy \
  --description="SQLi level 2 preview" \
  --expression="evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 2})" \
  --action=deny-403 \
  --preview

# Add preconfigured rule with exclusion (exclude a specific field from SQLi scanning)
gcloud compute security-policies rules add-rule 10005 \
  --security-policy=my-security-policy \
  --description="SQLi with exclusion for password field" \
  --expression="evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 1, 'opt_in_rule_ids': [], 'opt_out_rule_ids': ['owasp-crs-v030301-id942440-sqli']})" \
  --action=deny-403
```

---

## Rules — Rate Limiting

```bash
# Throttle requests: allow burst of 100/minute per IP, return 429 for excess
gcloud compute security-policies rules add-rule 6000 \
  --security-policy=my-security-policy \
  --description="Rate limit per IP" \
  --expression="true" \
  --action=throttle \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP

# Rate-based ban: ban an IP for 300 seconds after exceeding 50 requests/10 seconds
gcloud compute security-policies rules add-rule 6100 \
  --security-policy=my-security-policy \
  --description="Ban IPs that exceed aggressive rate" \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=50 \
  --rate-limit-threshold-interval-sec=10 \
  --ban-duration-sec=300 \
  --ban-threshold-count=1000 \
  --ban-threshold-interval-sec=600 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP

# Rate limit keyed on a header value (e.g., x-api-key)
gcloud compute security-policies rules add-rule 6200 \
  --security-policy=my-security-policy \
  --description="Rate limit by API key" \
  --expression="has(request.headers['x-api-key'])" \
  --action=throttle \
  --rate-limit-threshold-count=1000 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=HTTP_HEADER \
  --enforce-on-key-name=x-api-key
```

---

## Rules — Update and Remove

```bash
# Update a rule's action
gcloud compute security-policies rules update 10000 \
  --security-policy=my-security-policy \
  --action=deny-403

# Update a rule's description
gcloud compute security-policies rules update 10000 \
  --security-policy=my-security-policy \
  --description="SQLi protection - enabled"

# Disable preview mode (start enforcing)
gcloud compute security-policies rules update 10010 \
  --security-policy=my-security-policy \
  --no-preview

# Enable preview mode on an existing rule (to test changes)
gcloud compute security-policies rules update 10000 \
  --security-policy=my-security-policy \
  --preview

# Change rule priority (must delete and recreate at new priority)
# Cloud Armor doesn't support renumbering — you must remove and re-add

# Remove a rule
gcloud compute security-policies rules remove-rule 10010 \
  --security-policy=my-security-policy
```

---

## Attach Security Policy to Backend Service

```bash
# Attach security policy to a global backend service
gcloud compute backend-services update my-web-backend \
  --global \
  --security-policy=my-security-policy

# Attach edge security policy to a backend bucket
gcloud compute backend-buckets update my-cdn-bucket-backend \
  --edge-security-policy=my-edge-policy

# Remove a security policy from a backend service
gcloud compute backend-services update my-web-backend \
  --global \
  --no-security-policy

# View attached security policy
gcloud compute backend-services describe my-web-backend \
  --global \
  --format="value(securityPolicy)"
```

---

## Threat Intelligence (Cloud Armor Enterprise)

```bash
# Block traffic from Tor exit nodes
gcloud compute security-policies rules add-rule 700 \
  --security-policy=my-security-policy \
  --description="Block Tor exit nodes" \
  --expression="evaluateThreatIntelligence('iplist-tor-exit-nodes')" \
  --action=deny-403

# Block known malicious IPs
gcloud compute security-policies rules add-rule 710 \
  --security-policy=my-security-policy \
  --description="Block known malicious IPs" \
  --expression="evaluateThreatIntelligence('iplist-known-malicious-ips')" \
  --action=deny-403

# Allow search engine crawlers (priority higher than geo-block)
gcloud compute security-policies rules add-rule 50 \
  --security-policy=my-security-policy \
  --description="Allow search engine crawlers" \
  --expression="evaluateThreatIntelligence('iplist-search-engine-crawlers')" \
  --action=allow
```

---

## Adaptive Protection

```bash
# Enable Adaptive Protection on a security policy
gcloud compute security-policies update my-security-policy \
  --enable-layer7-ddos-defense

# View Adaptive Protection status
gcloud compute security-policies describe my-security-policy \
  --format="yaml(adaptiveProtectionConfig)"

# Check for suggested rules in Cloud Logging (Adaptive Protection generates alerts)
gcloud logging read \
  'resource.type="audited_resource" AND
   protoPayload.methodName="compute.securityPolicies.adaptiveProtection.suggestedRule"' \
  --limit=10
```

---

## Complete Example: Production WAF Policy

```bash
# Create policy
gcloud compute security-policies create prod-waf-policy \
  --description="Production WAF"

# Allow Google health checks (required for load balancer)
gcloud compute security-policies rules add-rule 50 \
  --security-policy=prod-waf-policy \
  --description="Allow Google health probers" \
  --expression="inIpRange(origin.ip, '130.211.0.0/22') || inIpRange(origin.ip, '35.191.0.0/16')" \
  --action=allow

# Block known bad countries
gcloud compute security-policies rules add-rule 1000 \
  --security-policy=prod-waf-policy \
  --description="Geo block" \
  --expression="origin.region_code in ['KP', 'IR']" \
  --action=deny-403

# SQLi protection (preview first)
gcloud compute security-policies rules add-rule 10000 \
  --security-policy=prod-waf-policy \
  --description="SQLi L1 preview" \
  --expression="evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 1})" \
  --action=deny-403 \
  --preview

# XSS protection (preview first)
gcloud compute security-policies rules add-rule 10001 \
  --security-policy=prod-waf-policy \
  --description="XSS L1 preview" \
  --expression="evaluatePreconfiguredWaf('xss-v33-stable', {'sensitivity': 1})" \
  --action=deny-403 \
  --preview

# LFI protection (preview first)
gcloud compute security-policies rules add-rule 10002 \
  --security-policy=prod-waf-policy \
  --description="LFI L1 preview" \
  --expression="evaluatePreconfiguredWaf('lfi-v33-stable', {'sensitivity': 1})" \
  --action=deny-403 \
  --preview

# Rate limit: 300 requests/minute per IP
gcloud compute security-policies rules add-rule 9000 \
  --security-policy=prod-waf-policy \
  --description="Rate limit" \
  --expression="true" \
  --action=throttle \
  --rate-limit-threshold-count=300 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP

# Default: allow (change to deny for strict allowlist policies)
gcloud compute security-policies rules update 2147483647 \
  --security-policy=prod-waf-policy \
  --description="Default allow" \
  --action=allow

# Attach to backend service
gcloud compute backend-services update my-web-backend \
  --global \
  --security-policy=prod-waf-policy
```
