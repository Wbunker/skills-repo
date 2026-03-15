# Managed Grafana & Managed Prometheus — CLI Reference
For service concepts, see [observability-monitoring-capabilities.md](observability-monitoring-capabilities.md).

```bash
# =========================================================
# --- Amazon Managed Grafana (AMG) ---
# Service: grafana
# =========================================================

# --- Workspaces ---
# Create a Grafana workspace with IAM Identity Center authentication
aws grafana create-workspace \
  --account-access-type CURRENT_ACCOUNT \
  --authentication-providers AWS_SSO \
  --permission-type SERVICE_MANAGED \
  --workspace-name my-grafana-workspace \
  --workspace-description "Production observability workspace" \
  --workspace-role-arn arn:aws:iam::123456789012:role/GrafanaWorkspaceRole

# Create a workspace with SAML authentication
aws grafana create-workspace \
  --account-access-type CURRENT_ACCOUNT \
  --authentication-providers SAML \
  --permission-type CUSTOMER_MANAGED \
  --workspace-name my-saml-workspace \
  --workspace-role-arn arn:aws:iam::123456789012:role/GrafanaWorkspaceRole

# Describe a workspace
aws grafana describe-workspace \
  --workspace-id g-1234567890

# List all workspaces
aws grafana list-workspaces

# Update workspace properties (name, description, role)
aws grafana update-workspace \
  --workspace-id g-1234567890 \
  --workspace-name updated-workspace-name \
  --workspace-description "Updated description"

# Delete a workspace
aws grafana delete-workspace \
  --workspace-id g-1234567890

# --- Authentication ---
# Update workspace authentication (switch to SAML or SSO)
aws grafana update-workspace-authentication \
  --workspace-id g-1234567890 \
  --authentication-providers AWS_SSO

# Update workspace to SAML with assertion mapping
aws grafana update-workspace-authentication \
  --workspace-id g-1234567890 \
  --authentication-providers SAML \
  --saml-configuration '{
    "idpMetadata": {
      "url": "https://idp.example.com/saml/metadata"
    },
    "assertionAttributes": {
      "name": "displayName",
      "login": "mail",
      "email": "mail",
      "role": "role"
    },
    "roleValues": {
      "admin": ["grafana-admin"],
      "editor": ["grafana-editor"]
    }
  }'

# --- Licensing ---
# Associate a Grafana Enterprise license
aws grafana associate-license \
  --workspace-id g-1234567890 \
  --license-type ENTERPRISE

# Disassociate the license
aws grafana disassociate-license \
  --workspace-id g-1234567890 \
  --license-type ENTERPRISE

# --- Permissions ---
# List user and group permissions for a workspace
aws grafana list-permissions \
  --workspace-id g-1234567890

# Grant Admin role to a user (IAM Identity Center user)
aws grafana update-permissions \
  --workspace-id g-1234567890 \
  --update-instruction-batch '[
    {
      "action": "ADD",
      "role": "ADMIN",
      "users": [
        {
          "id": "user-id-from-sso",
          "type": "SSO_USER"
        }
      ]
    }
  ]'

# Grant Editor role to a group
aws grafana update-permissions \
  --workspace-id g-1234567890 \
  --update-instruction-batch '[
    {
      "action": "ADD",
      "role": "EDITOR",
      "users": [
        {
          "id": "group-id-from-sso",
          "type": "SSO_GROUP"
        }
      ]
    }
  ]'

# Revoke a role
aws grafana update-permissions \
  --workspace-id g-1234567890 \
  --update-instruction-batch '[
    {
      "action": "REVOKE",
      "role": "EDITOR",
      "users": [
        {
          "id": "user-id-from-sso",
          "type": "SSO_USER"
        }
      ]
    }
  ]'

# --- API Keys ---
# Create a workspace API key (for programmatic Grafana API access)
aws grafana create-workspace-api-key \
  --workspace-id g-1234567890 \
  --key-name ci-provisioner \
  --key-role EDITOR \
  --seconds-to-live 86400

# Delete a workspace API key
aws grafana delete-workspace-api-key \
  --workspace-id g-1234567890 \
  --key-name ci-provisioner

# =========================================================
# --- Amazon Managed Service for Prometheus (AMP) ---
# Service: amp
# =========================================================

# --- Workspaces ---
# Create an AMP workspace
aws amp create-workspace \
  --alias my-prometheus-workspace

# Create with tags
aws amp create-workspace \
  --alias production-metrics \
  --tags Environment=production,Team=platform

# Describe a workspace
aws amp describe-workspace \
  --workspace-id ws-1234567890abcdef0

# List all AMP workspaces
aws amp list-workspaces

# List workspaces filtered by alias
aws amp list-workspaces \
  --alias production-metrics

# Delete a workspace (permanently deletes all stored metrics)
aws amp delete-workspace \
  --workspace-id ws-1234567890abcdef0

# --- Rule Groups Namespaces ---
# Create a rule groups namespace with recording and alerting rules
aws amp create-rule-groups-namespace \
  --workspace-id ws-1234567890abcdef0 \
  --name application-rules \
  --data fileb://rules.yaml
# rules.yaml example:
# groups:
#   - name: recording-rules
#     interval: 1m
#     rules:
#       - record: job:http_requests:rate5m
#         expr: rate(http_requests_total[5m])
#   - name: alerting-rules
#     rules:
#       - alert: HighErrorRate
#         expr: job:http_requests:rate5m{status="5xx"} > 0.05
#         for: 5m
#         labels:
#           severity: critical
#         annotations:
#           summary: "High error rate on {{ $labels.job }}"

# Update (replace) a rule groups namespace
aws amp put-rule-groups-namespace \
  --workspace-id ws-1234567890abcdef0 \
  --name application-rules \
  --data fileb://updated-rules.yaml

# Describe a rule groups namespace
aws amp describe-rule-groups-namespace \
  --workspace-id ws-1234567890abcdef0 \
  --name application-rules

# List all rule groups namespaces in a workspace
aws amp list-rule-groups-namespaces \
  --workspace-id ws-1234567890abcdef0

# Delete a rule groups namespace
aws amp delete-rule-groups-namespace \
  --workspace-id ws-1234567890abcdef0 \
  --name application-rules

# --- Alert Manager Definition ---
# Create the alert manager configuration
aws amp create-alert-manager-definition \
  --workspace-id ws-1234567890abcdef0 \
  --data fileb://alertmanager.yaml
# alertmanager.yaml example:
# alertmanager_config: |
#   route:
#     receiver: default
#     group_by: [alertname, job]
#     group_wait: 30s
#     group_interval: 5m
#     repeat_interval: 12h
#     routes:
#       - match:
#           severity: critical
#         receiver: pagerduty
#   receivers:
#     - name: default
#       sns_configs:
#         - topic_arn: arn:aws:sns:us-east-1:123456789012:amp-alerts
#           sigv4:
#             region: us-east-1
#     - name: pagerduty
#       pagerduty_configs:
#         - routing_key: <integration-key>
#   inhibit_rules:
#     - source_match:
#         severity: critical
#       target_match:
#         severity: warning
#       equal: [alertname, job]

# Update (replace) the alert manager definition
aws amp put-alert-manager-definition \
  --workspace-id ws-1234567890abcdef0 \
  --data fileb://updated-alertmanager.yaml

# Describe the alert manager definition
aws amp describe-alert-manager-definition \
  --workspace-id ws-1234567890abcdef0

# Delete the alert manager definition
aws amp delete-alert-manager-definition \
  --workspace-id ws-1234567890abcdef0

# --- Scrapers (AWS-managed scraping from EKS) ---
# Create a scraper to ingest metrics from an EKS cluster
aws amp create-scraper \
  --source '{
    "eksConfiguration": {
      "clusterArn": "arn:aws:eks:us-east-1:123456789012:cluster/my-cluster",
      "subnetIds": ["subnet-0abc12345def67890", "subnet-0def67890abc12345"],
      "securityGroupIds": ["sg-0abc12345def67890"]
    }
  }' \
  --scrape-configuration '{
    "configurationBlob": "<base64-encoded-scrape-config>"
  }' \
  --destination '{
    "ampConfiguration": {
      "workspaceArn": "arn:aws:aps:us-east-1:123456789012:workspace/ws-1234567890abcdef0"
    }
  }' \
  --alias my-eks-scraper

# Describe a scraper
aws amp describe-scraper \
  --scraper-id s-1234567890abcdef0

# List all scrapers
aws amp list-scrapers

# List scrapers for a specific EKS cluster
aws amp list-scrapers \
  --filters '{"sourceArn": ["arn:aws:eks:us-east-1:123456789012:cluster/my-cluster"]}'

# Delete a scraper
aws amp delete-scraper \
  --scraper-id s-1234567890abcdef0

# --- Ad-hoc PromQL queries via awscurl ---
# Install: pip install awscurl
# Instant query
awscurl --service aps --region us-east-1 \
  "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-1234567890abcdef0/api/v1/query?query=up"

# Range query
awscurl --service aps --region us-east-1 \
  "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-1234567890abcdef0/api/v1/query_range?query=rate(http_requests_total[5m])&start=2024-01-01T00:00:00Z&end=2024-01-01T01:00:00Z&step=60"
```
