# Apigee — CLI

## Important Note on Apigee CLI Coverage

The `gcloud apigee` command covers a subset of Apigee management operations. Most day-to-day Apigee work (editing proxy policies, configuring flows, managing KVMs, portal content) is done via the **Apigee UI** (`console.cloud.google.com/apigee`) or the **Apigee Management REST API** (`apigee.googleapis.com`). The `apigeecli` open-source tool (github.com/apigee/apigeecli) provides much more complete CLI coverage than `gcloud apigee`.

---

## Organizations

```bash
# Describe the Apigee organization for the current project
gcloud apigee organizations describe

# List all Apigee organizations accessible to the current account
gcloud apigee organizations list

# Provision an Apigee X organization (initial setup)
gcloud apigee organizations provision \
  --authorized-network=my-vpc \
  --runtime-location=us-central1 \
  --analytics-region=us-central1
```

---

## Environments

```bash
# List all environments in the organization
gcloud apigee environments list

# Describe an environment
gcloud apigee environments describe prod

# Create an environment
gcloud apigee environments create staging \
  --display-name="Staging Environment"

# Delete an environment
gcloud apigee environments delete staging

# Deploy an API proxy revision to an environment
gcloud apigee deployments apply \
  --environment=prod \
  --api=my-api-proxy \
  --revision=3

# List all deployments in an environment
gcloud apigee deployments list --environment=prod

# Undeploy a proxy revision from an environment
gcloud apigee deployments delete \
  --environment=prod \
  --api=my-api-proxy \
  --revision=3
```

---

## API Proxies

```bash
# List all API proxies
gcloud apigee apis list

# Describe a proxy (shows revisions)
gcloud apigee apis describe my-api-proxy

# Create (import) a new API proxy from a zip bundle
gcloud apigee apis create my-api-proxy \
  --source=my-proxy-bundle.zip

# Delete a proxy (all revisions must be undeployed first)
gcloud apigee apis delete my-api-proxy

# List revisions of a proxy
gcloud apigee apis describe my-api-proxy \
  --format="value(revision)"

# Export a proxy revision bundle to a local zip file
gcloud apigee apis export my-api-proxy \
  --revision=3 \
  --output-directory=./exported-proxies
```

---

## API Products

```bash
# List all API products
gcloud apigee products list

# Describe an API product
gcloud apigee products describe my-product

# Create an API product
gcloud apigee products create my-product \
  --display-name="My Product" \
  --environments=prod \
  --proxies=my-api-proxy \
  --quota=1000 \
  --quota-interval=1 \
  --quota-unit=hour \
  --description="Public API product for external developers"

# Update an API product (add quota)
gcloud apigee products update my-product \
  --quota=5000 \
  --quota-interval=1 \
  --quota-unit=hour

# Delete an API product
gcloud apigee products delete my-product
```

---

## Developers

```bash
# List all developers in the org
gcloud apigee developers list

# Describe a developer
gcloud apigee developers describe developer@example.com

# Create a developer
gcloud apigee developers create \
  --email=developer@example.com \
  --first-name=John \
  --last-name=Developer \
  --username=johndeveloper

# Delete a developer
gcloud apigee developers delete developer@example.com
```

---

## Developer Applications

```bash
# List all developer apps
gcloud apigee applications list

# List apps for a specific developer
gcloud apigee applications list \
  --developer=developer@example.com

# Describe a developer app (includes API keys)
gcloud apigee applications describe MY_APP_ID

# Create a developer app
gcloud apigee applications create \
  --developer=developer@example.com \
  --name=my-mobile-app \
  --api-products=my-product

# Delete a developer app
gcloud apigee applications delete MY_APP_ID
```

---

## Analytics Export

```bash
# List analytics datastores (export destinations)
gcloud apigee analytics datastores list

# Create a BigQuery datastore for analytics export
gcloud apigee analytics datastores create \
  --display-name="BQ Analytics Export" \
  --datastore-type=bigquery \
  --project=my-analytics-project \
  --dataset-id=apigee_analytics

# Export analytics data to BigQuery
gcloud apigee analytics export \
  --datastore=DATASTORE_ID \
  --date=2024-11-15 \
  --environment=prod

# List analytics exports
gcloud apigee analytics exports list --environment=prod
```

---

## Using apigeecli (Recommended for Advanced Operations)

The `apigeecli` tool provides complete Apigee management capabilities beyond what `gcloud apigee` supports.

```bash
# Install apigeecli
curl -L https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | sh -
export PATH=$PATH:$HOME/.apigeecli/bin

# Authenticate using gcloud token
TOKEN=$(gcloud auth print-access-token)

# Import and deploy a proxy bundle
apigeecli apis create bundle \
  --name my-api-proxy \
  --proxy-zip ./my-proxy.zip \
  --org PROJECT_ID \
  --token $TOKEN

# Deploy proxy to environment
apigeecli apis deploy \
  --name my-api-proxy \
  --ovr \
  --org PROJECT_ID \
  --env prod \
  --token $TOKEN

# Create or update a Key-Value Map entry
apigeecli kvms entries create \
  --map my-config-kvm \
  --org PROJECT_ID \
  --env prod \
  --name api-backend-url \
  --value "https://my-backend.internal" \
  --token $TOKEN

# Export all proxy bundles from org
apigeecli apis export \
  --org PROJECT_ID \
  --token $TOKEN \
  --output ./proxies-backup

# Sync shared flows
apigeecli sharedflows create bundle \
  --name common-security-flow \
  --sf-zip ./security-flow.zip \
  --org PROJECT_ID \
  --token $TOKEN

apigeecli sharedflows deploy \
  --name common-security-flow \
  --org PROJECT_ID \
  --env prod \
  --token $TOKEN

# List all API products with details
apigeecli products list \
  --org PROJECT_ID \
  --token $TOKEN \
  --expand
```

---

## Apigee Management REST API (via curl)

For operations not supported by `gcloud apigee` or `apigeecli`:

```bash
TOKEN=$(gcloud auth print-access-token)
ORG=my-project-id

# List all proxy revisions
curl -H "Authorization: Bearer $TOKEN" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/apis/my-api-proxy/revisions"

# Get proxy revision deployment status
curl -H "Authorization: Bearer $TOKEN" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/apis/my-api-proxy/revisions/3/deployments"

# Get analytics data (custom report)
curl -H "Authorization: Bearer $TOKEN" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/environments/prod/stats/apiproxy?select=sum(message_count)&timeRange=last7days"

# Create/update KVM entry in environment
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "backend-url", "value": "https://backend.example.com"}' \
  "https://apigee.googleapis.com/v1/organizations/$ORG/environments/prod/keyvaluemaps/my-kvm/entries/backend-url"

# Trace a proxy (create a trace session for debugging)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/environments/prod/apis/my-api-proxy/revisions/3/debugsessions" \
  -d '{"count": 10, "timeout": "600s"}'
```

---

## Environment Groups and Hostname Routing

```bash
# List environment groups
gcloud apigee envgroups list

# Describe an environment group (see hostnames)
gcloud apigee envgroups describe my-envgroup

# Create an environment group
gcloud apigee envgroups create prod-group \
  --hostnames=api.example.com,api2.example.com

# Attach an environment to an environment group
gcloud apigee envgroups attachments create \
  --envgroup=prod-group \
  --environment=prod

# Detach an environment from an environment group
gcloud apigee envgroups attachments delete ATTACHMENT_ID \
  --envgroup=prod-group

# List attachments for an environment group
gcloud apigee envgroups attachments list --envgroup=prod-group
```
