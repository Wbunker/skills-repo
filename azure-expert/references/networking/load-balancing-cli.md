# Azure Load Balancing — CLI Reference

---

## Azure Load Balancer

```bash
# Create a Standard external Load Balancer with public IP
az network public-ip create \
  --name myLBPublicIP \
  --resource-group myRG \
  --sku Standard \
  --zone 1 2 3

az network lb create \
  --name myLoadBalancer \
  --resource-group myRG \
  --sku Standard \
  --location eastus \
  --frontend-ip-name myFrontend \
  --public-ip-address myLBPublicIP \
  --backend-pool-name myBackendPool

# Create a Standard internal Load Balancer with private IP
az network lb create \
  --name myInternalLB \
  --resource-group myRG \
  --sku Standard \
  --vnet-name myVNet \
  --subnet mySubnet \
  --frontend-ip-name myFrontend \
  --private-ip-address 10.0.1.10 \
  --backend-pool-name myBackendPool

# Create a health probe (HTTP)
az network lb probe create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name myHTTPProbe \
  --protocol Http \
  --port 80 \
  --path /health \
  --interval 15 \
  --threshold 2

# Create a health probe (TCP)
az network lb probe create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name myTCPProbe \
  --protocol Tcp \
  --port 443 \
  --interval 5 \
  --threshold 2

# Create a load balancing rule
az network lb rule create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name myHTTPRule \
  --protocol Tcp \
  --frontend-port 80 \
  --backend-port 80 \
  --frontend-ip-name myFrontend \
  --backend-pool-name myBackendPool \
  --probe-name myHTTPProbe \
  --idle-timeout 15 \
  --enable-tcp-reset true

# Create an HA Ports rule (NVA / internal LB scenario)
az network lb rule create \
  --lb-name myInternalLB \
  --resource-group myRG \
  --name HAPortsRule \
  --protocol All \
  --frontend-port 0 \
  --backend-port 0 \
  --frontend-ip-name myFrontend \
  --backend-pool-name myBackendPool \
  --probe-name myTCPProbe \
  --enable-floating-ip true

# Create an inbound NAT rule (single VM SSH access)
az network lb inbound-nat-rule create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name SSHToVM1 \
  --protocol Tcp \
  --frontend-port 50001 \
  --backend-port 22 \
  --frontend-ip-name myFrontend

# Create a backend address pool
az network lb address-pool create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name mySecondPool

# Add IP-based backend address (cross-VNet or on-premises)
az network lb address-pool address add \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --pool-name myBackendPool \
  --name myOnPremServer \
  --ip-address 192.168.1.10 \
  --vnet myVNet

# Create outbound rule for SNAT
az network lb outbound-rule create \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --name myOutboundRule \
  --frontend-ip-configs myFrontend \
  --protocol All \
  --backend-pool-name myBackendPool \
  --idle-timeout 15 \
  --outbound-ports 10000

# List load balancers
az network lb list \
  --resource-group myRG \
  --output table

# Show effective load balancer configuration
az network lb show \
  --name myLoadBalancer \
  --resource-group myRG

# Show all frontend IP configs
az network lb frontend-ip list \
  --lb-name myLoadBalancer \
  --resource-group myRG \
  --output table
```

---

## Application Gateway

```bash
# Create Application Gateway WAF v2 with autoscaling
az network application-gateway create \
  --name myAppGW \
  --resource-group myRG \
  --location eastus \
  --sku WAF_v2 \
  --capacity 2 \
  --vnet-name myVNet \
  --subnet AppGWSubnet \
  --public-ip-address myAppGWPublicIP \
  --http-settings-cookie-based-affinity Disabled \
  --frontend-port 443 \
  --http-settings-port 443 \
  --http-settings-protocol Https \
  --priority 100 \
  --zones 1 2 3

# Enable autoscaling on existing App Gateway
az network application-gateway update \
  --name myAppGW \
  --resource-group myRG \
  --min-capacity 1 \
  --max-capacity 10

# Create WAF policy with managed rule sets
az network application-gateway waf-policy create \
  --name myWAFPolicy \
  --resource-group myRG \
  --location eastus \
  --type OWASP \
  --version 3.2

# Set WAF policy to Prevention mode
az network application-gateway waf-policy update \
  --name myWAFPolicy \
  --resource-group myRG \
  --state Enabled \
  --mode Prevention

# Add managed rule set to WAF policy
az network application-gateway waf-policy managed-rule rule-set add \
  --policy-name myWAFPolicy \
  --resource-group myRG \
  --type Microsoft_BotManagerRuleSet \
  --version 1.0

# Create a backend pool
az network application-gateway address-pool create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name myBackendPool \
  --servers 10.0.1.4 10.0.1.5

# Create HTTP settings
az network application-gateway http-settings create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name myHTTPSettings \
  --port 443 \
  --protocol Https \
  --cookie-based-affinity Enabled \
  --timeout 30 \
  --connection-draining-timeout 60

# Create a listener (HTTPS with certificate)
az network application-gateway ssl-cert create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name myCert \
  --cert-file /path/to/cert.pfx \
  --cert-password "certpassword"

az network application-gateway frontend-port create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name port443 \
  --port 443

# Create URL path map for path-based routing
az network application-gateway url-path-map create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name myPathMap \
  --paths "/api/*" \
  --address-pool myApiPool \
  --http-settings myHTTPSettings \
  --default-address-pool myDefaultPool \
  --default-http-settings myHTTPSettings

# Add additional path rule to URL path map
az network application-gateway url-path-map rule create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name imagesRule \
  --path-map-name myPathMap \
  --paths "/images/*" \
  --address-pool myImagesPool \
  --http-settings myHTTPSettings

# Create rewrite rule set (add security headers)
az network application-gateway rewrite-rule set create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name myRewriteRuleSet

az network application-gateway rewrite-rule create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --rule-set-name myRewriteRuleSet \
  --name addSecurityHeaders \
  --sequence 100 \
  --response-headers \
    Strict-Transport-Security="max-age=31536000; includeSubDomains" \
    X-Content-Type-Options="nosniff"

# Create HTTP-to-HTTPS redirect
az network application-gateway redirect-config create \
  --gateway-name myAppGW \
  --resource-group myRG \
  --name HTTPtoHTTPS \
  --type Permanent \
  --target-listener myHTTPSListener \
  --include-path true \
  --include-query-string true

# Show Application Gateway health
az network application-gateway show-backend-health \
  --name myAppGW \
  --resource-group myRG \
  --output table

# List Application Gateways
az network application-gateway list \
  --resource-group myRG \
  --output table
```

---

## Traffic Manager

```bash
# Create Traffic Manager profile (Priority routing — active/standby)
az network traffic-manager profile create \
  --name myTMProfile \
  --resource-group myRG \
  --routing-method Priority \
  --unique-dns-name mytmprofile \
  --ttl 30 \
  --protocol HTTPS \
  --port 443 \
  --path /health

# Create Traffic Manager profile (Performance routing — latency-based)
az network traffic-manager profile create \
  --name myPerfTMProfile \
  --resource-group myRG \
  --routing-method Performance \
  --unique-dns-name myperfprofile \
  --ttl 60 \
  --protocol HTTP \
  --port 80 \
  --path /health

# Create Traffic Manager profile (Weighted routing — A/B testing)
az network traffic-manager profile create \
  --name myWeightedTM \
  --resource-group myRG \
  --routing-method Weighted \
  --unique-dns-name myweightedprofile \
  --ttl 30 \
  --protocol HTTPS \
  --port 443 \
  --path /health

# Add Azure endpoint (App Service)
az network traffic-manager endpoint create \
  --name primaryEndpoint \
  --profile-name myTMProfile \
  --resource-group myRG \
  --type azureEndpoints \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/myAppService \
  --endpoint-status Enabled \
  --priority 1

# Add Azure endpoint (secondary/failover)
az network traffic-manager endpoint create \
  --name secondaryEndpoint \
  --profile-name myTMProfile \
  --resource-group myRG \
  --type azureEndpoints \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/myAppServiceDR \
  --endpoint-status Enabled \
  --priority 2

# Add external endpoint (non-Azure)
az network traffic-manager endpoint create \
  --name onPremEndpoint \
  --profile-name myTMProfile \
  --resource-group myRG \
  --type externalEndpoints \
  --target myonprem.example.com \
  --endpoint-status Enabled \
  --endpoint-location "East US"

# Add weighted endpoint
az network traffic-manager endpoint create \
  --name prodEndpoint \
  --profile-name myWeightedTM \
  --resource-group myRG \
  --type azureEndpoints \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/myProdApp \
  --weight 90 \
  --endpoint-status Enabled

az network traffic-manager endpoint create \
  --name canaryEndpoint \
  --profile-name myWeightedTM \
  --resource-group myRG \
  --type azureEndpoints \
  --target-resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Web/sites/myCanaryApp \
  --weight 10 \
  --endpoint-status Enabled

# Update endpoint (change weight or disable)
az network traffic-manager endpoint update \
  --name canaryEndpoint \
  --profile-name myWeightedTM \
  --resource-group myRG \
  --type azureEndpoints \
  --weight 25 \
  --endpoint-status Enabled

# Show endpoint health status
az network traffic-manager endpoint show \
  --name primaryEndpoint \
  --profile-name myTMProfile \
  --resource-group myRG \
  --type azureEndpoints

# List all endpoints in a profile
az network traffic-manager endpoint list \
  --profile-name myTMProfile \
  --resource-group myRG \
  --output table

# List all Traffic Manager profiles
az network traffic-manager profile list \
  --resource-group myRG \
  --output table

# Show profile details including DNS name
az network traffic-manager profile show \
  --name myTMProfile \
  --resource-group myRG
```
