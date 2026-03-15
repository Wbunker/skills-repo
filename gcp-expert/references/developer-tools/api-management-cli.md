# API Management — CLI

## Cloud Endpoints

### Deploy Service Configurations

```bash
# Enable required APIs
gcloud services enable endpoints.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com

# Deploy an OpenAPI 2.0 spec to Cloud Endpoints
# The spec's `host` field becomes the service name
gcloud endpoints services deploy openapi.yaml

# Deploy a gRPC API (proto descriptor + service config)
# First generate the proto descriptor:
protoc \
  --include_imports \
  --include_source_info \
  --proto_path=. \
  --descriptor_set_out=api_descriptor.pb \
  api.proto

# Then deploy descriptor + config
gcloud endpoints services deploy api_descriptor.pb api_config.yaml

# Deploy with a specific service name (override if not in spec)
gcloud endpoints services deploy openapi.yaml \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog

# Get service configuration ID after deployment (needed for ESPv2)
gcloud endpoints configs list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --limit=1 \
  --sort-by="~id" \
  --format="value(id)"

# Combine into a variable for ESPv2 deploy
CONFIG_ID=$(gcloud endpoints configs list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --format="value(id)" \
  --limit=1 \
  --sort-by="~id")
echo "Latest config: $CONFIG_ID"
```

### Manage Services

```bash
# List all Cloud Endpoints services in the project
gcloud endpoints services list

# Describe a service
gcloud endpoints services describe my-api.endpoints.PROJECT_ID.cloud.goog

# List all service configurations (versions)
gcloud endpoints configs list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog

# Describe a specific service configuration
gcloud endpoints configs describe $CONFIG_ID \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog

# Describe and view the full service config (API methods, quota, auth)
gcloud endpoints configs describe $CONFIG_ID \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --format=yaml

# Delete a Cloud Endpoints service (and all its configs)
gcloud endpoints services delete my-api.endpoints.PROJECT_ID.cloud.goog

# Undelete a recently deleted service (within 30 days)
gcloud endpoints services undelete my-api.endpoints.PROJECT_ID.cloud.goog
```

### Deploy ESPv2 on Cloud Run (Standalone Mode)

```bash
# Build and deploy ESPv2 as a Cloud Run service fronting a backend
SERVICE_NAME=my-api.endpoints.PROJECT_ID.cloud.goog
CONFIG_ID=$(gcloud endpoints configs list \
  --service=$SERVICE_NAME \
  --format="value(id)" \
  --limit=1 \
  --sort-by="~id")

BACKEND_URL=https://my-backend-HASH-uc.a.run.app

gcloud run deploy my-api-espv2 \
  --image=gcr.io/endpoints-release/endpoints-runtime-serverless:2 \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENDPOINTS_SERVICE_NAME=${SERVICE_NAME}" \
  --set-env-vars="ENDPOINTS_SERVICE_VERSION=${CONFIG_ID}" \
  --set-env-vars="ESPv2_ARGS=--rollout_strategy=managed --backend=${BACKEND_URL} --cors_preset=basic" \
  --service-account=espv2-sa@PROJECT_ID.iam.gserviceaccount.com

# Grant ESPv2 SA the Cloud Run invoker role on the backend
gcloud run services add-iam-policy-binding my-backend \
  --region=us-central1 \
  --member="serviceAccount:espv2-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Grant ESPv2 SA the Service Controller role (required for ESPv2)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:espv2-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/servicemanagement.serviceController"
```

---

## API Gateway

```bash
# Enable required APIs
gcloud services enable apigateway.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com

# Create service account for API Gateway to invoke backend
gcloud iam service-accounts create api-gw-sa \
  --display-name="API Gateway Backend SA"

gcloud run services add-iam-policy-binding my-backend \
  --region=us-central1 \
  --member="serviceAccount:api-gw-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Create an API resource
gcloud api-gateway apis create my-gateway-api \
  --project=PROJECT_ID \
  --display-name="My Gateway API"

# Create an API config from an OpenAPI spec
gcloud api-gateway api-configs create my-api-config-v1 \
  --api=my-gateway-api \
  --openapi-spec=api-definition.yaml \
  --project=PROJECT_ID \
  --backend-auth-service-account=api-gw-sa@PROJECT_ID.iam.gserviceaccount.com

# Create a gateway (deploy to an endpoint)
gcloud api-gateway gateways create my-gateway \
  --api=my-gateway-api \
  --api-config=my-api-config-v1 \
  --location=us-central1 \
  --project=PROJECT_ID

# Get the gateway default hostname (URL)
gcloud api-gateway gateways describe my-gateway \
  --location=us-central1 \
  --project=PROJECT_ID \
  --format="value(defaultHostname)"

# List APIs
gcloud api-gateway apis list --project=PROJECT_ID

# List API configs for an API
gcloud api-gateway api-configs list \
  --api=my-gateway-api \
  --project=PROJECT_ID

# Describe an API config
gcloud api-gateway api-configs describe my-api-config-v1 \
  --api=my-gateway-api \
  --project=PROJECT_ID

# Update a gateway to a new config (deploy new version)
gcloud api-gateway gateways update my-gateway \
  --api=my-gateway-api \
  --api-config=my-api-config-v2 \
  --location=us-central1 \
  --project=PROJECT_ID

# List all gateways
gcloud api-gateway gateways list \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe a gateway
gcloud api-gateway gateways describe my-gateway \
  --location=us-central1 \
  --project=PROJECT_ID

# Delete a gateway
gcloud api-gateway gateways delete my-gateway \
  --location=us-central1 \
  --project=PROJECT_ID

# Delete an API config (must not be in use by a gateway)
gcloud api-gateway api-configs delete my-api-config-v1 \
  --api=my-gateway-api \
  --project=PROJECT_ID

# Delete an API (must delete all configs first)
gcloud api-gateway apis delete my-gateway-api --project=PROJECT_ID
```

---

## API Keys

```bash
# Enable the API Keys API
gcloud services enable apikeys.googleapis.com

# Create an API key (unrestricted — not recommended for production)
gcloud alpha services api-keys create \
  --display-name="My App API Key" \
  --project=PROJECT_ID

# Create an API key restricted to specific APIs
gcloud alpha services api-keys create \
  --display-name="Mobile App Key" \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --project=PROJECT_ID

# Create an API key with HTTP referrer restriction (web apps)
gcloud alpha services api-keys create \
  --display-name="Web App Key" \
  --allowed-referrers=https://example.com/*,https://www.example.com/* \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --project=PROJECT_ID

# Create an API key with IP address restriction (server-side)
gcloud alpha services api-keys create \
  --display-name="Server Key" \
  --allowed-ips=203.0.113.0/24,198.51.100.100 \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --project=PROJECT_ID

# Create an API key with Android app restriction
gcloud alpha services api-keys create \
  --display-name="Android App Key" \
  --allowed-application="[{\"sha1_fingerprint\":\"AA:BB:CC...\",\"package_name\":\"com.example.myapp\"}]" \
  --api-target=service=maps.googleapis.com \
  --project=PROJECT_ID

# List all API keys
gcloud alpha services api-keys list --project=PROJECT_ID

# Describe an API key (shows restrictions, but NOT the key string)
gcloud alpha services api-keys describe KEY_ID --project=PROJECT_ID

# Get the actual key string value (shown only once at creation or via this command)
gcloud alpha services api-keys get-key-string KEY_ID --project=PROJECT_ID

# Update key restrictions
gcloud alpha services api-keys update KEY_ID \
  --display-name="Updated Mobile Key" \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --allowed-ips=203.0.113.0/24 \
  --project=PROJECT_ID

# Undelete (restore) a deleted key
gcloud alpha services api-keys undelete KEY_ID --project=PROJECT_ID

# Delete an API key
gcloud alpha services api-keys delete KEY_ID --project=PROJECT_ID
```

---

## Service Consumer Quotas

### View and Override Quotas

```bash
# List all quota metrics for a service
gcloud services quota list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --project=PROJECT_ID

# List quota with consumer override info
gcloud services quota list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --consumer=project:CONSUMER_PROJECT_ID

# Get specific quota info
gcloud services quota describe METRIC_NAME \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --project=PROJECT_ID

# Set a producer override (increase limit for a specific consumer project)
gcloud services quota override \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --consumer=project:CONSUMER_PROJECT_ID \
  --metric=read-requests \
  --unit=1/min/{project} \
  --value=10000

# Delete a quota override (reverts to default)
gcloud services quota delete-override \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog \
  --consumer=project:CONSUMER_PROJECT_ID \
  --metric=read-requests \
  --unit=1/min/{project}

# View GCP platform quota limits for a project
gcloud services quota list \
  --service=compute.googleapis.com \
  --project=PROJECT_ID

# Request a quota increase (opens the quotas page)
# Quota increases must be requested via the Console:
# IAM & Admin > Quotas
# Or via the serviceusage.googleapis.com API

# List consumer quota limits for a specific metric
gcloud services quota list \
  --service=run.googleapis.com \
  --project=PROJECT_ID \
  --filter="metric:run.googleapis.com"
```

### Monitor Quota Usage

```bash
# Check current quota usage via Cloud Monitoring
# Use the `serviceruntime.googleapis.com/api/request_count` metric
gcloud monitoring metrics list \
  --filter="metric.type=serviceruntime.googleapis.com/api/request_count"

# View quota-related logs
gcloud logging read \
  'resource.type="endpoints_api" AND labels."serviceruntime.googleapis.com/quota_metric"="read-requests"' \
  --project=PROJECT_ID \
  --limit=50
```

---

## Viewing Cloud Endpoints Metrics

```bash
# View API request counts in the last hour
gcloud monitoring metrics list \
  --filter='metric.type:"serviceruntime.googleapis.com"' \
  --project=PROJECT_ID

# Read metrics for a specific Cloud Endpoints service
# Use Cloud Monitoring API; gcloud metric-descriptors for available metrics:
gcloud monitoring metric-descriptors list \
  --filter='metric.type:serviceruntime.googleapis.com' \
  --project=PROJECT_ID \
  --format="value(type)"

# Typical available metrics for Cloud Endpoints:
# serviceruntime.googleapis.com/api/request_count
# serviceruntime.googleapis.com/api/request_latencies
# serviceruntime.googleapis.com/api/producer/total_latencies
# serviceruntime.googleapis.com/quota/consumer/usage
# serviceruntime.googleapis.com/quota/rate/consumer/exceeded_request_count
```
