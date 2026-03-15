# Looker — CLI Reference

Most Looker administration is performed through the Looker web UI or Looker REST API. The `gcloud looker` CLI manages Looker Core instances (Google Cloud managed deployments). Pipeline and content operations use the Looker REST API directly.

---

## Looker Instances (gcloud)

```bash
# Create a Looker Core instance (standard edition)
gcloud looker instances create my-looker \
  --region=us-central1 \
  --platform-edition=LOOKER_CORE_STANDARD \
  --project=my-project

# Create a Looker Core instance with VPC peering for BigQuery private access
gcloud looker instances create prod-looker \
  --region=us-central1 \
  --platform-edition=LOOKER_CORE_ENTERPRISE \
  --consumer-network=projects/my-project/global/networks/my-vpc \
  --reserved-range=looker-psa-range \
  --project=my-project

# Create instance with custom OAuth credentials
gcloud looker instances create my-looker \
  --region=us-central1 \
  --platform-edition=LOOKER_CORE_STANDARD \
  --oauth-client-id=my-oauth-client-id \
  --oauth-client-secret=my-oauth-client-secret \
  --project=my-project

# List Looker instances
gcloud looker instances list \
  --region=us-central1 \
  --project=my-project

# List instances across all regions
gcloud looker instances list \
  --region=- \
  --project=my-project

# Describe a Looker instance (includes URL, state, version)
gcloud looker instances describe my-looker \
  --region=us-central1 \
  --project=my-project

# Get the Looker instance URL
gcloud looker instances describe my-looker \
  --region=us-central1 \
  --format="value(ingressPrivateIp)" \
  --project=my-project

# Update a Looker instance (e.g., upgrade platform edition)
gcloud looker instances update my-looker \
  --region=us-central1 \
  --platform-edition=LOOKER_CORE_ENTERPRISE \
  --project=my-project

# Export instance backup
gcloud looker instances export my-looker \
  --region=us-central1 \
  --target-gcs-uri=gs://my-backup-bucket/looker-backups/$(date +%Y%m%d) \
  --project=my-project

# Import from backup
gcloud looker instances import my-looker \
  --region=us-central1 \
  --source-gcs-uri=gs://my-backup-bucket/looker-backups/20240101 \
  --project=my-project

# Restart a Looker instance
gcloud looker instances restart my-looker \
  --region=us-central1 \
  --project=my-project

# Delete a Looker instance
gcloud looker instances delete my-looker \
  --region=us-central1 \
  --project=my-project
```

---

## Looker REST API

The Looker API is the primary interface for content management, query execution, and user administration. Authenticate with an API3 key (client_id + client_secret) from the Looker Admin panel.

```bash
# Authenticate and get access token
LOOKER_URL="https://my-looker.looker.com"
CLIENT_ID="my_api_client_id"
CLIENT_SECRET="my_api_client_secret"

TOKEN=$(curl -s -X POST "${LOOKER_URL}:19999/api/4.0/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}" \
  | jq -r '.access_token')

# Get all LookML models
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/lookml_models" \
  -H "Authorization: token ${TOKEN}" \
  | jq '.[].name'

# Get explores in a model
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/lookml_models/ecommerce/explores" \
  -H "Authorization: token ${TOKEN}" \
  | jq '.[].name'

# Run a query inline and get results as JSON
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/queries/run/json" \
  -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ecommerce",
    "view": "orders",
    "fields": ["orders.order_date", "orders.order_count", "orders.total_revenue"],
    "filters": {"orders.order_date": "30 days"},
    "sorts": ["orders.order_date desc"],
    "limit": 1000
  }'

# Run a saved Look and get CSV output
LOOK_ID=42
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/looks/${LOOK_ID}/run/csv" \
  -H "Authorization: token ${TOKEN}" \
  > look_output.csv

# List all dashboards
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/dashboards" \
  -H "Authorization: token ${TOKEN}" \
  | jq '.[] | {id: .id, title: .title}'

# Run a dashboard and get results
DASHBOARD_ID=15
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/dashboards/${DASHBOARD_ID}/run_look" \
  -H "Authorization: token ${TOKEN}"

# List all users
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/users" \
  -H "Authorization: token ${TOKEN}" \
  | jq '.[] | {id: .id, email: .email}'

# Create a user
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/users" \
  -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com"
  }'

# Generate a signed SSO embed URL
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/embed/sso_url" \
  -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "/embed/dashboards/15",
    "session_length": 3600,
    "external_user_id": "user-123",
    "first_name": "Embedded",
    "last_name": "User",
    "permissions": ["access_data", "see_looks", "see_user_dashboards"],
    "models": ["ecommerce"],
    "user_attributes": {"account_id": "12345"}
  }'

# Schedule a Look for email delivery
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/scheduled_plans" \
  -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Revenue Report",
    "look_id": 42,
    "crontab": "0 8 * * *",
    "scheduled_plan_destination": [{
      "type": "email",
      "address": "team@example.com",
      "format": "csv_zip",
      "apply_formatting": true
    }]
  }'

# Trigger a scheduled plan to run immediately
PLAN_ID=7
curl -s -X POST "${LOOKER_URL}:19999/api/4.0/scheduled_plans/${PLAN_ID}/run_once" \
  -H "Authorization: token ${TOKEN}"

# List all scheduled plans
curl -s -X GET "${LOOKER_URL}:19999/api/4.0/scheduled_plans" \
  -H "Authorization: token ${TOKEN}" \
  | jq '.[] | {id: .id, name: .name, crontab: .crontab}'
```

---

## LookML Linting (lookml-linter)

```bash
# Install lookml-linter (Python-based community tool)
pip install lookml-linter

# Run linter on LookML project directory
lookml-linter --path ./lookml-project/

# Run with specific rules
lookml-linter --path ./lookml-project/ --config .lookml-lintrc

# Example .lookml-lintrc config
cat > .lookml-lintrc << 'EOF'
rules:
  - name: no_count_without_type_count
    enabled: true
  - name: no_duplicate_view_label
    enabled: true
  - name: sql_ref_without_double_curly_braces
    enabled: true
EOF
```

---

## Gazer (Community CLI for Bulk Operations)

```bash
# Install Gazer (Ruby gem for bulk Looker operations)
gem install gazer

# Configure Gazer
gzr --host my-looker.looker.com --port 443 --client-id MY_ID --client-secret MY_SECRET

# Export all dashboards to a local directory
gzr dashboard cat --dir ./dashboard-backups/ 1 2 3 4 5

# Export all Looks in a folder
gzr look cat --dir ./look-backups/

# List all dashboards
gzr dashboard ls

# Import (restore) a dashboard from file
gzr dashboard import ./dashboard-backups/Sales_Overview.json --folder 10

# Deploy LookML to production (via gcloud or API)
# Looker's native deploy happens via Git integration; see Looker Admin > Projects > Deploy
```

---

## IAM for Looker Instances

```bash
# Grant Looker Instance Admin role
gcloud projects add-iam-policy-binding my-project \
  --member="user:admin@example.com" \
  --role="roles/looker.admin"

# Grant Looker Instance Viewer role
gcloud projects add-iam-policy-binding my-project \
  --member="user:viewer@example.com" \
  --role="roles/looker.viewer"

# Key IAM roles for Looker (gcloud/GCP level):
# roles/looker.admin   - manage Looker instances via gcloud
# roles/looker.viewer  - view instance metadata
# (User-level Looker permissions — access to explores, dashboards, models —
#  are managed within the Looker application UI, not via gcloud IAM)
```
