# Integration Services — CLI

## Application Integration

```bash
# List all integrations in a region
gcloud integrations list --location=us-central1

# Describe an integration
gcloud integrations describe my-order-integration --location=us-central1

# List versions of an integration
gcloud integrations versions list my-order-integration --location=us-central1

# Describe a specific version
gcloud integrations versions describe VERSION_ID \
  --integration=my-order-integration \
  --location=us-central1

# Create a new integration (from JSON export)
gcloud integrations create my-new-integration --location=us-central1

# Upload/publish a new integration version from JSON file
gcloud integrations versions publish \
  --integration=my-order-integration \
  --location=us-central1 \
  --file=integration-config.json

# Create a new draft version
gcloud integrations versions create \
  --integration=my-order-integration \
  --location=us-central1 \
  --file=draft-config.json

# Execute an integration (via API trigger)
gcloud integrations executions run my-order-integration \
  --location=us-central1 \
  --trigger-id=api_trigger/order_trigger \
  --input-parameters='{"order_id": {"string_value": "ORD-12345"}}'

# List recent executions
gcloud integrations executions list my-order-integration --location=us-central1

# Describe an execution (with task execution details)
gcloud integrations executions describe EXECUTION_ID \
  --integration=my-order-integration \
  --location=us-central1

# Cancel a running execution
gcloud integrations executions cancel EXECUTION_ID \
  --integration=my-order-integration \
  --location=us-central1

# Delete an integration (all versions must be unpublished)
gcloud integrations delete my-order-integration --location=us-central1

# Export integration version as JSON (for backup/CI-CD)
gcloud integrations versions get VERSION_ID \
  --integration=my-order-integration \
  --location=us-central1 \
  --format=json > integration-backup.json
```

---

## Integration Connectors

```bash
# List available connector types (providers)
gcloud connectors providers list --location=us-central1

# List connection types for a provider (e.g., Salesforce)
gcloud connectors connectors list --location=us-central1

# List all connections in a region
gcloud connectors connections list --location=us-central1

# Describe a connection
gcloud connectors connections describe my-salesforce-connection \
  --location=us-central1

# Create a connection (example: Salesforce with OAuth 2.0)
# First, store credentials in Secret Manager
gcloud secrets create salesforce-client-secret \
  --data-file=client-secret.txt

gcloud connectors connections create my-salesforce-connection \
  --location=us-central1 \
  --connector-version=projects/PROJECT_ID/locations/us-central1/providers/salesforce/connectors/salesforce/versions/1 \
  --display-name="Salesforce Production" \
  --connection-auth-type=OAUTH2_CLIENT_CREDENTIALS \
  --oauth2-client-id=YOUR_CLIENT_ID \
  --oauth2-client-secret-secret-version=projects/PROJECT_ID/secrets/salesforce-client-secret/versions/latest \
  --configuration-variables=instanceUrl=https://yourorg.my.salesforce.com

# Create a ServiceNow connection (Basic Auth)
gcloud connectors connections create my-servicenow-connection \
  --location=us-central1 \
  --connector-version=projects/PROJECT_ID/locations/us-central1/providers/servicenow/connectors/servicenow/versions/1 \
  --display-name="ServiceNow Production" \
  --connection-auth-type=USER_PASSWORD \
  --username=integration-user \
  --password-secret-version=projects/PROJECT_ID/secrets/servicenow-password/versions/latest \
  --configuration-variables=instanceUrl=https://yourinstance.service-now.com

# Update a connection
gcloud connectors connections update my-salesforce-connection \
  --location=us-central1 \
  --display-name="Salesforce Production Updated"

# Delete a connection
gcloud connectors connections delete my-salesforce-connection \
  --location=us-central1

# Get connection status (check if healthy)
gcloud connectors connections describe my-salesforce-connection \
  --location=us-central1 \
  --format="value(status.state)"

# List operations (long-running operations for connection create/update)
gcloud connectors operations list --location=us-central1

# Describe a long-running operation
gcloud connectors operations describe OPERATION_ID --location=us-central1
```

---

## Cloud Endpoints

### Deploy Service Configuration

```bash
# Deploy an OpenAPI spec to Cloud Endpoints (creates a new service config version)
gcloud endpoints services deploy openapi.yaml

# The openapi.yaml must include:
# host: my-api.endpoints.PROJECT_ID.cloud.goog
# x-google-management:
#   metrics: ...
#   quota: ...

# Check service config status
gcloud endpoints services describe my-api.endpoints.PROJECT_ID.cloud.goog

# List all endpoint services in the project
gcloud endpoints services list

# List all service configurations (versions)
gcloud endpoints configs list \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog

# Describe a specific service config (get the config ID for ESP deployment)
gcloud endpoints configs describe CONFIG_ID \
  --service=my-api.endpoints.PROJECT_ID.cloud.goog

# Delete a service
gcloud endpoints services delete my-api.endpoints.PROJECT_ID.cloud.goog

# Undelete a recently deleted service (within 30 days)
gcloud endpoints services undelete my-api.endpoints.PROJECT_ID.cloud.goog
```

### Example openapi.yaml for Cloud Endpoints with Cloud Run backend

```yaml
# openapi.yaml
swagger: "2.0"
info:
  title: My API
  version: "1.0.0"
host: "my-api.endpoints.PROJECT_ID.cloud.goog"
x-google-backend:
  address: https://my-backend-HASH-uc.a.run.app
  jwt_audience: https://my-backend-HASH-uc.a.run.app
schemes:
  - https
produces:
  - application/json
security:
  - api_key: []
securityDefinitions:
  api_key:
    type: apiKey
    name: key
    in: query
paths:
  /items:
    get:
      summary: List items
      operationId: listItems
      x-google-quota:
        metricCosts:
          read-requests: 1
      responses:
        "200":
          description: Success
  /items/{id}:
    get:
      summary: Get item
      operationId: getItem
      parameters:
        - name: id
          in: path
          required: true
          type: string
      responses:
        "200":
          description: Success
x-google-management:
  metrics:
    - name: read-requests
      displayName: Read Requests
      valueType: INT64
      metricKind: DELTA
  quota:
    limits:
      - name: read-requests-per-minute
        metric: read-requests
        unit: 1/min/{project}
        values:
          STANDARD: 1000
```

### Deploy ESPV2 on Cloud Run (ESP as a Cloud Run service fronting a backend)

```bash
# Get the latest ESPV2 image tag
ESP_VERSION=$(gcloud container images list-tags gcr.io/endpoints-release/endpoints-runtime-serverless \
  --format="value(tags)" --limit=1 --sort-by="~timestamp")

# Deploy ESPV2 as a Cloud Run service
gcloud run deploy my-api-esp \
  --image=gcr.io/endpoints-release/endpoints-runtime-serverless:2 \
  --allow-unauthenticated \
  --region=us-central1 \
  --set-env-vars="ENDPOINTS_SERVICE_NAME=my-api.endpoints.PROJECT_ID.cloud.goog" \
  --set-env-vars="ENDPOINTS_SERVICE_VERSION=CONFIG_ID" \
  --set-env-vars="ESPv2_ARGS=--rollout_strategy=managed"
```

### Manage API Keys for Cloud Endpoints

```bash
# Create an API key for a service consumer
gcloud alpha services api-keys create \
  --display-name="Mobile App Key" \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog

# List API keys
gcloud alpha services api-keys list

# Get a key's string value
gcloud alpha services api-keys get-key-string KEY_ID

# Restrict an API key to specific services
gcloud alpha services api-keys update KEY_ID \
  --api-target=service=my-api.endpoints.PROJECT_ID.cloud.goog

# Delete an API key
gcloud alpha services api-keys delete KEY_ID
```

---

## API Gateway

### Create and Deploy an API Gateway

```bash
# Enable required APIs
gcloud services enable apigateway.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com

# Create an API resource
gcloud api-gateway apis create my-gateway-api \
  --project=PROJECT_ID

# Create an API config from an OpenAPI spec
gcloud api-gateway api-configs create my-api-config-v1 \
  --api=my-gateway-api \
  --openapi-spec=api-definition.yaml \
  --project=PROJECT_ID \
  --backend-auth-service-account=api-gateway-sa@PROJECT_ID.iam.gserviceaccount.com

# Deploy a gateway (creates the endpoint that serves traffic)
gcloud api-gateway gateways create my-gateway \
  --api=my-gateway-api \
  --api-config=my-api-config-v1 \
  --location=us-central1 \
  --project=PROJECT_ID

# Get the gateway URL
gcloud api-gateway gateways describe my-gateway \
  --location=us-central1 \
  --project=PROJECT_ID \
  --format="value(defaultHostname)"

# Update gateway to use a new API config (deploy new version)
gcloud api-gateway gateways update my-gateway \
  --api=my-gateway-api \
  --api-config=my-api-config-v2 \
  --location=us-central1 \
  --project=PROJECT_ID
```

### Manage API Configs and Gateways

```bash
# List all APIs
gcloud api-gateway apis list --project=PROJECT_ID

# List all API configs for an API
gcloud api-gateway api-configs list \
  --api=my-gateway-api \
  --project=PROJECT_ID

# Describe an API config
gcloud api-gateway api-configs describe my-api-config-v1 \
  --api=my-gateway-api \
  --project=PROJECT_ID

# List all gateways in a region
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

# Delete an API config (gateway must be deleted or pointing to different config first)
gcloud api-gateway api-configs delete my-api-config-v1 \
  --api=my-gateway-api \
  --project=PROJECT_ID

# Delete an API
gcloud api-gateway apis delete my-gateway-api --project=PROJECT_ID
```

### Example API Gateway OpenAPI spec with Cloud Run backend

```yaml
# api-definition.yaml
swagger: "2.0"
info:
  title: My API Gateway
  version: "1.0"
schemes:
  - https
produces:
  - application/json
security:
  - firebase: []
securityDefinitions:
  firebase:
    authorizationUrl: ""
    flow: implicit
    type: oauth2
    x-google-issuer: https://securetoken.google.com/PROJECT_ID
    x-google-jwks_uri: https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com
    x-google-audiences: PROJECT_ID
paths:
  /users/{userId}:
    get:
      operationId: getUser
      parameters:
        - name: userId
          in: path
          required: true
          type: string
      x-google-backend:
        address: https://user-service-HASH-uc.a.run.app/users/{userId}
        path_translation: APPEND_PATH_TO_ADDRESS
        jwt_audience: https://user-service-HASH-uc.a.run.app
      responses:
        "200":
          description: OK
  /orders:
    post:
      operationId: createOrder
      x-google-backend:
        address: https://order-service-HASH-uc.a.run.app/orders
        jwt_audience: https://order-service-HASH-uc.a.run.app
      responses:
        "201":
          description: Created
```

### Grant API Gateway SA the Cloud Run invoker role

```bash
# Create a service account for API Gateway backend auth
gcloud iam service-accounts create api-gateway-sa \
  --display-name="API Gateway Backend SA"

# Grant Cloud Run invoker (for JWT-authenticated backend calls)
gcloud run services add-iam-policy-binding user-service \
  --region=us-central1 \
  --member="serviceAccount:api-gateway-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud run services add-iam-policy-binding order-service \
  --region=us-central1 \
  --member="serviceAccount:api-gateway-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```
