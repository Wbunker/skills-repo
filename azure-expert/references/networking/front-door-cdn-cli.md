# Azure Front Door & CDN — CLI Reference

All AFD Standard/Premium commands use the `az afd` command group. Classic CDN uses `az cdn`.

---

## Azure Front Door Standard / Premium

```bash
# Create an AFD Standard profile
az afd profile create \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --sku Standard_AzureFrontDoor

# Create an AFD Premium profile (required for managed WAF rules and Private Link origins)
az afd profile create \
  --profile-name myAFDPremium \
  --resource-group myRG \
  --sku Premium_AzureFrontDoor

# List AFD profiles
az afd profile list \
  --resource-group myRG \
  --output table

# Show profile details (including usage metrics)
az afd profile show \
  --profile-name myAFDProfile \
  --resource-group myRG

# Show resource usage for a profile (endpoints, origins, routes remaining)
az afd profile usage \
  --profile-name myAFDProfile \
  --resource-group myRG
```

### Endpoints

```bash
# Create an AFD endpoint
az afd endpoint create \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --enabled-state Enabled

# List endpoints in a profile
az afd endpoint list \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table

# Show endpoint details (includes generated FQDN: *.z01.azurefd.net)
az afd endpoint show \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG

# Purge cached content from an endpoint
az afd endpoint purge \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --content-paths "/*" \
  --domains www.example.com

# Purge specific paths
az afd endpoint purge \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --content-paths "/images/*" "/css/*"
```

### Origin Groups

```bash
# Create an origin group with health probe and load balancing settings
az afd origin-group create \
  --origin-group-name myOriginGroup \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --probe-request-type GET \
  --probe-protocol Https \
  --probe-interval-in-seconds 60 \
  --probe-path /health \
  --sample-size 4 \
  --successful-samples-required 3 \
  --additional-latency-in-milliseconds 50

# List origin groups
az afd origin-group list \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table

# Update origin group (change health probe settings)
az afd origin-group update \
  --origin-group-name myOriginGroup \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --probe-interval-in-seconds 30 \
  --probe-path /api/health
```

### Origins

```bash
# Create an origin (App Service)
az afd origin create \
  --origin-name myAppServiceOrigin \
  --origin-group-name myOriginGroup \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --host-name myapp.azurewebsites.net \
  --origin-host-header myapp.azurewebsites.net \
  --http-port 80 \
  --https-port 443 \
  --priority 1 \
  --weight 1000 \
  --enabled-state Enabled

# Create an origin for a secondary region (failover)
az afd origin create \
  --origin-name myAppServiceOriginDR \
  --origin-group-name myOriginGroup \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --host-name myapp-dr.azurewebsites.net \
  --origin-host-header myapp-dr.azurewebsites.net \
  --https-port 443 \
  --priority 2 \
  --weight 1000 \
  --enabled-state Enabled

# Create a Private Link origin (Premium only) — connects to internal App Service
az afd origin create \
  --origin-name myPrivateOrigin \
  --origin-group-name myOriginGroup \
  --profile-name myAFDPremium \
  --resource-group myRG \
  --host-name myapp.azurewebsites.net \
  --origin-host-header myapp.azurewebsites.net \
  --https-port 443 \
  --priority 1 \
  --weight 1000 \
  --enable-private-link true \
  --private-link-resource /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/myapp \
  --private-link-location eastus \
  --private-link-request-message "AFD Private Link request"

# List origins in an origin group
az afd origin list \
  --origin-group-name myOriginGroup \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table
```

### Routes

```bash
# Create a route (maps endpoint + path to origin group, with HTTPS redirect and caching)
az afd route create \
  --route-name myRoute \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --origin-group myOriginGroup \
  --supported-protocols Http Https \
  --https-redirect Enabled \
  --forwarding-protocol HttpsOnly \
  --link-to-default-domain Enabled \
  --enable-compression true \
  --query-string-caching-behavior IgnoreQueryString \
  --patterns-to-match "/*"

# Create a route with custom domains and caching for static assets
az afd route create \
  --route-name staticRoute \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --origin-group myStaticOriginGroup \
  --supported-protocols Https \
  --forwarding-protocol HttpsOnly \
  --enable-compression true \
  --query-string-caching-behavior UseQueryString \
  --patterns-to-match "/static/*" "/assets/*" \
  --cache-duration "7.00:00:00"

# List routes
az afd route list \
  --endpoint-name myEndpoint \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table
```

### WAF Policy (Standard/Premium)

```bash
# Create WAF policy (Premium — includes managed rule sets)
az afd waf-policy create \
  --policy-name myAFDWAFPolicy \
  --resource-group myRG \
  --sku Premium_AzureFrontDoor \
  --mode Prevention \
  --enable-managed-rule-set true

# Create WAF policy (Standard — custom rules only)
az afd waf-policy create \
  --policy-name myAFDStdWAFPolicy \
  --resource-group myRG \
  --sku Standard_AzureFrontDoor \
  --mode Detection

# Add a managed rule set to WAF policy
az afd waf-policy managed-rule-definition list \
  --resource-group myRG

# Associate WAF policy with a security policy on the profile/endpoint
az afd security-policy create \
  --security-policy-name mySecurityPolicy \
  --profile-name myAFDPremium \
  --resource-group myRG \
  --domains /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Cdn/profiles/myAFDPremium/afdEndpoints/myEndpoint \
  --waf-policy /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/frontDoorWebApplicationFirewallPolicies/myAFDWAFPolicy

# List security policies
az afd security-policy list \
  --profile-name myAFDPremium \
  --resource-group myRG \
  --output table
```

### Rule Sets and Rules

```bash
# Create a rule set
az afd rule-set create \
  --rule-set-name myRuleSet \
  --profile-name myAFDProfile \
  --resource-group myRG

# Create a rule: redirect HTTP to HTTPS
az afd rule create \
  --rule-set-name myRuleSet \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --rule-name HttpToHttps \
  --order 1 \
  --match-variable RequestScheme \
  --operator Equal \
  --match-values HTTP \
  --action-name UrlRedirect \
  --redirect-type PermanentRedirect \
  --redirect-protocol Https

# Create a rule: add security response header
az afd rule create \
  --rule-set-name myRuleSet \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --rule-name AddHSTS \
  --order 2 \
  --action-name ModifyResponseHeader \
  --header-action Overwrite \
  --header-name Strict-Transport-Security \
  --header-value "max-age=31536000; includeSubDomains"

# Create a rule: geo-block specific countries
az afd rule create \
  --rule-set-name myRuleSet \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --rule-name GeoBlock \
  --order 3 \
  --match-variable RemoteAddress \
  --operator GeoMatch \
  --match-values CN KP \
  --action-name Block

# List rules in a rule set
az afd rule list \
  --rule-set-name myRuleSet \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table
```

### Custom Domains

```bash
# Create a custom domain (requires DNS CNAME to AFD endpoint)
az afd custom-domain create \
  --custom-domain-name wwwExampleCom \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --host-name www.example.com \
  --minimum-tls-version TLS12 \
  --certificate-type ManagedCertificate

# Create custom domain with customer-managed cert (from Key Vault)
az afd custom-domain create \
  --custom-domain-name wwwExampleComBYO \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --host-name www.example.com \
  --minimum-tls-version TLS12 \
  --certificate-type CustomerCertificate \
  --secret myAFDSecret

# List custom domains
az afd custom-domain list \
  --profile-name myAFDProfile \
  --resource-group myRG \
  --output table
```

---

## Azure CDN (Classic)

```bash
# Create a CDN profile (Microsoft classic)
az cdn profile create \
  --name myCDNProfile \
  --resource-group myRG \
  --sku Standard_Microsoft

# Create a CDN endpoint
az cdn endpoint create \
  --name myCDNEndpoint \
  --profile-name myCDNProfile \
  --resource-group myRG \
  --origin myapp.azurewebsites.net \
  --origin-host-header myapp.azurewebsites.net \
  --enable-compression true \
  --query-string-caching-behavior IgnoreQueryString

# List CDN endpoints
az cdn endpoint list \
  --profile-name myCDNProfile \
  --resource-group myRG \
  --output table

# Purge cached content
az cdn endpoint purge \
  --name myCDNEndpoint \
  --profile-name myCDNProfile \
  --resource-group myRG \
  --content-paths "/*"

# Add custom domain to CDN endpoint
az cdn custom-domain create \
  --endpoint-name myCDNEndpoint \
  --profile-name myCDNProfile \
  --resource-group myRG \
  --name wwwExampleCom \
  --hostname www.example.com

# Enable HTTPS on custom domain (managed cert)
az cdn custom-domain enable-https \
  --endpoint-name myCDNEndpoint \
  --profile-name myCDNProfile \
  --resource-group myRG \
  --name wwwExampleCom \
  --min-tls-version 1.2

# List CDN profiles
az cdn profile list \
  --resource-group myRG \
  --output table
```
