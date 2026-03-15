# Cloud Load Balancing — CLI Reference

---

## Health Checks

```bash
# Create an HTTP health check
gcloud compute health-checks create http my-http-health-check \
  --port=80 \
  --request-path=/health \
  --check-interval=10s \
  --timeout=5s \
  --healthy-threshold=2 \
  --unhealthy-threshold=3

# Create an HTTPS health check
gcloud compute health-checks create https my-https-health-check \
  --port=443 \
  --request-path=/health \
  --check-interval=10s \
  --timeout=5s \
  --healthy-threshold=2 \
  --unhealthy-threshold=3

# Create a TCP health check
gcloud compute health-checks create tcp my-tcp-health-check \
  --port=8080 \
  --check-interval=10s \
  --timeout=5s

# Create a gRPC health check
gcloud compute health-checks create grpc my-grpc-health-check \
  --port=50051 \
  --grpc-service-name=my.grpc.Service \
  --check-interval=10s

# Create an HTTP/2 health check
gcloud compute health-checks create http2 my-h2-health-check \
  --port=8443 \
  --request-path=/healthz

# List health checks
gcloud compute health-checks list

# Describe a health check
gcloud compute health-checks describe my-http-health-check

# Delete a health check
gcloud compute health-checks delete my-http-health-check
```

---

## Backend Services

```bash
# Create a global backend service (for Global Application LB)
gcloud compute backend-services create my-web-backend \
  --global \
  --protocol=HTTPS \
  --port-name=https \
  --health-checks=my-https-health-check \
  --timeout=30 \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Create a regional backend service (for Regional Application LB or Internal LB)
gcloud compute backend-services create my-internal-backend \
  --region=us-central1 \
  --protocol=HTTP \
  --port-name=http \
  --health-checks=my-http-health-check \
  --load-balancing-scheme=INTERNAL_MANAGED

# Add a MIG backend to the backend service
gcloud compute backend-services add-backend my-web-backend \
  --global \
  --instance-group=my-mig \
  --instance-group-zone=us-central1-a \
  --balancing-mode=UTILIZATION \
  --max-utilization=0.8 \
  --capacity-scaler=1.0

# Add a MIG backend using RATE balancing mode
gcloud compute backend-services add-backend my-web-backend \
  --global \
  --instance-group=my-mig-eu \
  --instance-group-zone=europe-west1-b \
  --balancing-mode=RATE \
  --max-rate-per-instance=100

# Add a Cloud Run backend via Serverless NEG
gcloud compute backend-services add-backend my-api-backend \
  --global \
  --network-endpoint-group=my-cloudrun-neg \
  --network-endpoint-group-region=us-central1

# Enable Cloud CDN on a backend service
gcloud compute backend-services update my-web-backend \
  --global \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC

# Attach a Cloud Armor security policy
gcloud compute backend-services update my-web-backend \
  --global \
  --security-policy=my-security-policy

# Update session affinity
gcloud compute backend-services update my-web-backend \
  --global \
  --session-affinity=GENERATED_COOKIE \
  --affinity-cookie-ttl=3600

# Update connection timeout
gcloud compute backend-services update my-web-backend \
  --global \
  --timeout=60

# Enable request logging
gcloud compute backend-services update my-web-backend \
  --global \
  --enable-logging \
  --logging-sample-rate=1.0

# Describe a backend service
gcloud compute backend-services describe my-web-backend --global

# List backend services
gcloud compute backend-services list

# Delete a backend service
gcloud compute backend-services delete my-web-backend --global
```

---

## Backend Buckets (Cloud Storage)

```bash
# Create a backend bucket (for serving static content from GCS)
gcloud compute backend-buckets create my-static-bucket-backend \
  --gcs-bucket-name=my-static-website-bucket

# Create backend bucket with CDN enabled
gcloud compute backend-buckets create my-cdn-bucket-backend \
  --gcs-bucket-name=my-cdn-bucket \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC

# Update backend bucket CDN settings
gcloud compute backend-buckets update my-cdn-bucket-backend \
  --cache-mode=FORCE_CACHE_ALL \
  --default-ttl=3600 \
  --max-ttl=86400

# Delete a backend bucket
gcloud compute backend-buckets delete my-cdn-bucket-backend
```

---

## URL Maps

```bash
# Create a simple URL map with a default backend service
gcloud compute url-maps create my-url-map \
  --default-service=my-web-backend

# Create URL map with a default backend bucket (for static sites)
gcloud compute url-maps create my-static-url-map \
  --default-backend-bucket=my-cdn-bucket-backend

# Add a host rule and path matcher to the URL map
gcloud compute url-maps import my-url-map \
  --global \
  --source=url-map.yaml

# url-map.yaml example for complex routing:
# name: my-url-map
# defaultService: https://www.googleapis.com/.../my-web-backend
# hostRules:
# - hosts: [api.example.com]
#   pathMatcher: api-matcher
# - hosts: [www.example.com, example.com]
#   pathMatcher: web-matcher
# pathMatchers:
# - name: api-matcher
#   defaultService: https://www.googleapis.com/.../my-api-backend
#   pathRules:
#   - paths: [/v1/*, /v2/*]
#     service: https://www.googleapis.com/.../my-api-v2-backend
# - name: web-matcher
#   defaultService: https://www.googleapis.com/.../my-web-backend
#   pathRules:
#   - paths: [/static/*, /assets/*]
#     service: https://www.googleapis.com/.../my-static-bucket-backend

# Set a redirect rule (HTTP → HTTPS redirect)
gcloud compute url-maps import my-http-redirect-map \
  --global \
  --source=- <<'EOF'
name: my-http-redirect-map
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF

# Export URL map to YAML (for editing)
gcloud compute url-maps export my-url-map --global > url-map.yaml

# List URL maps
gcloud compute url-maps list

# Describe URL map
gcloud compute url-maps describe my-url-map --global

# Validate URL map
gcloud compute url-maps validate --source=url-map.yaml --global

# Delete URL map
gcloud compute url-maps delete my-url-map --global
```

---

## Target Proxies

```bash
# Create a target HTTP proxy
gcloud compute target-http-proxies create my-http-proxy \
  --url-map=my-http-redirect-map \
  --global

# Create a target HTTPS proxy (with Google-managed SSL certificate)
gcloud compute target-https-proxies create my-https-proxy \
  --url-map=my-url-map \
  --ssl-certificates=my-ssl-cert \
  --global

# Create a target HTTPS proxy with multiple SSL certificates
gcloud compute target-https-proxies create my-https-proxy-multi-cert \
  --url-map=my-url-map \
  --ssl-certificates=cert-example-com,cert-api-example-com \
  --global

# Update target proxy with new SSL certificate
gcloud compute target-https-proxies update my-https-proxy \
  --ssl-certificates=my-new-ssl-cert \
  --global

# Create a target SSL proxy (for non-HTTP TLS termination)
gcloud compute target-ssl-proxies create my-ssl-proxy \
  --backend-service=my-ssl-backend \
  --ssl-certificates=my-ssl-cert

# List target HTTP proxies
gcloud compute target-http-proxies list

# List target HTTPS proxies
gcloud compute target-https-proxies list

# Delete target proxy
gcloud compute target-https-proxies delete my-https-proxy --global
```

---

## Forwarding Rules

```bash
# Create a global forwarding rule for HTTPS (uses ephemeral global IP)
gcloud compute forwarding-rules create my-https-forwarding-rule \
  --global \
  --target-https-proxy=my-https-proxy \
  --ports=443 \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Create a global forwarding rule with a static IP
gcloud compute addresses create my-global-ip --global --ip-version=IPV4
gcloud compute forwarding-rules create my-https-forwarding-rule \
  --global \
  --target-https-proxy=my-https-proxy \
  --address=my-global-ip \
  --ports=443 \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Create a global forwarding rule for HTTP (port 80, for redirect)
gcloud compute forwarding-rules create my-http-forwarding-rule \
  --global \
  --target-http-proxy=my-http-proxy \
  --address=my-global-ip \
  --ports=80 \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Create a regional forwarding rule (Internal Application LB)
gcloud compute forwarding-rules create my-internal-forwarding-rule \
  --region=us-central1 \
  --target-http-proxy=my-internal-http-proxy \
  --ports=80 \
  --load-balancing-scheme=INTERNAL_MANAGED \
  --network=my-vpc \
  --subnet=my-subnet-us

# Create a regional forwarding rule for External pass-through Network LB
gcloud compute forwarding-rules create my-tcp-forwarding-rule \
  --region=us-central1 \
  --backend-service=my-tcp-backend \
  --ports=8080 \
  --load-balancing-scheme=EXTERNAL

# Describe a forwarding rule
gcloud compute forwarding-rules describe my-https-forwarding-rule --global

# List forwarding rules
gcloud compute forwarding-rules list

# Get the external IP of a global forwarding rule
gcloud compute forwarding-rules describe my-https-forwarding-rule \
  --global \
  --format="value(IPAddress)"

# Delete a forwarding rule
gcloud compute forwarding-rules delete my-https-forwarding-rule --global
```

---

## SSL Certificates

```bash
# Create a Google-managed SSL certificate
gcloud compute ssl-certificates create my-ssl-cert \
  --domains=example.com,www.example.com \
  --global

# Check SSL certificate status
gcloud compute ssl-certificates describe my-ssl-cert --global \
  --format="table(name,managed.status,managed.domains,managed.domainStatus)"

# Create a self-managed certificate (from files)
gcloud compute ssl-certificates create my-self-managed-cert \
  --certificate=cert.pem \
  --private-key=key.pem \
  --global

# List SSL certificates
gcloud compute ssl-certificates list

# Delete SSL certificate
gcloud compute ssl-certificates delete my-ssl-cert --global
```

---

## Network Endpoint Groups (NEGs)

```bash
# Create a Serverless NEG for a Cloud Run service
gcloud compute network-endpoint-groups create my-cloudrun-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --cloud-run-service=my-cloud-run-service

# Create a Serverless NEG for Cloud Functions
gcloud compute network-endpoint-groups create my-cloudfunctions-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --cloud-function-name=my-function

# Create a Serverless NEG for App Engine
gcloud compute network-endpoint-groups create my-appengine-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --app-engine-app

# Create a Zonal NEG (for container-native GKE LB)
gcloud compute network-endpoint-groups create my-gke-neg \
  --zone=us-central1-a \
  --network=my-vpc \
  --subnet=my-gke-subnet \
  --network-endpoint-type=GCE_VM_IP_PORT \
  --default-port=8080

# Create an Internet NEG (external backend)
gcloud compute network-endpoint-groups create my-internet-neg \
  --global \
  --network-endpoint-type=INTERNET_FQDN_PORT \
  --default-port=443

# Add endpoint to Internet NEG
gcloud compute network-endpoint-groups update my-internet-neg \
  --global \
  --add-endpoint="fqdn=api.external-service.com,port=443"

# Describe a NEG
gcloud compute network-endpoint-groups describe my-cloudrun-neg \
  --region=us-central1

# List NEGs
gcloud compute network-endpoint-groups list

# Delete a NEG
gcloud compute network-endpoint-groups delete my-cloudrun-neg \
  --region=us-central1
```

---

## End-to-End Example: Global HTTPS LB with Cloud Run Backend

```bash
# 1. Create a Serverless NEG for Cloud Run
gcloud compute network-endpoint-groups create my-run-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --cloud-run-service=my-api-service

# 2. Create backend service
gcloud compute backend-services create my-api-backend \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED

# 3. Add NEG to backend service
gcloud compute backend-services add-backend my-api-backend \
  --global \
  --network-endpoint-group=my-run-neg \
  --network-endpoint-group-region=us-central1

# 4. Reserve a static global IP
gcloud compute addresses create my-api-ip --global --ip-version=IPV4

# 5. Create Google-managed SSL certificate
gcloud compute ssl-certificates create my-api-cert \
  --domains=api.example.com \
  --global

# 6. Create URL map
gcloud compute url-maps create my-api-url-map \
  --default-service=my-api-backend \
  --global

# 7. Create HTTP redirect URL map
gcloud compute url-maps import my-http-redirect \
  --global \
  --source=- <<'EOF'
name: my-http-redirect
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF

# 8. Create target proxies
gcloud compute target-http-proxies create my-api-http-proxy \
  --url-map=my-http-redirect \
  --global

gcloud compute target-https-proxies create my-api-https-proxy \
  --url-map=my-api-url-map \
  --ssl-certificates=my-api-cert \
  --global

# 9. Create forwarding rules
gcloud compute forwarding-rules create my-api-http-rule \
  --global \
  --target-http-proxy=my-api-http-proxy \
  --address=my-api-ip \
  --ports=80 \
  --load-balancing-scheme=EXTERNAL_MANAGED

gcloud compute forwarding-rules create my-api-https-rule \
  --global \
  --target-https-proxy=my-api-https-proxy \
  --address=my-api-ip \
  --ports=443 \
  --load-balancing-scheme=EXTERNAL_MANAGED

# 10. Get the assigned IP address
gcloud compute addresses describe my-api-ip --global --format="value(address)"
# Point api.example.com DNS A record to this IP
```
