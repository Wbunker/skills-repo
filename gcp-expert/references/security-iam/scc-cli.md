# Security Command Center — CLI Reference

## Setup and Configuration

```bash
# SCC is configured at the org level; get your org ID
gcloud organizations list

# Enable the SCC API
gcloud services enable securitycenter.googleapis.com \
  --project=PROJECT_ID

# Get the SCC settings for an organization
gcloud scc settings describe \
  --organization=ORG_ID

# Update SCC settings (enable/disable built-in services)
gcloud scc settings update \
  --organization=ORG_ID \
  --enable-web-security-scanner
```

---

## Findings

```bash
# List all active findings for an organization (paginated)
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE"

# List CRITICAL and HIGH severity active findings
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE AND (severity=CRITICAL OR severity=HIGH)"

# List findings for a specific project
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE AND resource.project_display_name:my-project"

# List findings by category
gcloud scc findings list \
  --organization=ORG_ID \
  --filter='state=ACTIVE AND category="OPEN_FIREWALL"'

# List findings from a specific source (e.g., Security Health Analytics)
gcloud scc findings list \
  --source=organizations/ORG_ID/sources/SOURCE_ID \
  --filter="state=ACTIVE"

# List findings with a time range
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE AND event_time>2025-01-01T00:00:00Z"

# List findings formatted as a table with key fields
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE AND severity=CRITICAL" \
  --format="table(finding.name,finding.category,finding.severity,finding.resourceName,finding.eventTime)"

# Describe a specific finding (full details)
gcloud scc findings describe \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --finding=FINDING_ID

# Update a finding's state to INACTIVE (mark as resolved)
gcloud scc findings update FINDING_ID \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --state=INACTIVE

# Update finding state and add a comment (via API; gcloud uses state only)
gcloud scc findings update FINDING_ID \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --state=INACTIVE

# Mute a specific finding (hide from active views; does not delete)
gcloud scc findings update FINDING_ID \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --mute=MUTED

# Unmute a finding
gcloud scc findings update FINDING_ID \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --mute=UNMUTED

# Count findings by severity
gcloud scc findings list \
  --organization=ORG_ID \
  --filter="state=ACTIVE" \
  --format="value(finding.severity)" | sort | uniq -c
```

---

## Sources

```bash
# List all sources for an organization (built-in and custom)
gcloud scc sources list \
  --organization=ORG_ID

# List sources formatted as a table
gcloud scc sources list \
  --organization=ORG_ID \
  --format="table(name,displayName,description)"

# Describe a specific source
gcloud scc sources describe \
  --organization=ORG_ID \
  --source=SOURCE_ID

# Create a custom source (for writing your own findings)
gcloud scc sources create \
  --organization=ORG_ID \
  --display-name="My Custom Scanner" \
  --description="Findings from my internal vulnerability scanner"

# Update a custom source
gcloud scc sources update SOURCE_ID \
  --organization=ORG_ID \
  --display-name="Updated Scanner Name"

# Get IAM policy on a source
gcloud scc sources get-iam-policy \
  --organization=ORG_ID \
  --source=SOURCE_ID

# Grant a service account permission to write findings to a custom source
gcloud scc sources set-iam-policy \
  --organization=ORG_ID \
  --source=SOURCE_ID \
  --member="serviceAccount:scanner-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/securitycenter.findingsEditor"
```

---

## Assets

```bash
# List assets in an organization
gcloud scc assets list \
  --organization=ORG_ID

# List assets of a specific type
gcloud scc assets list \
  --organization=ORG_ID \
  --filter='securityCenterProperties.resourceType="google.compute.Instance"'

# List public Cloud Storage buckets
gcloud scc assets list \
  --organization=ORG_ID \
  --filter='securityCenterProperties.resourceType="google.cloud.storage.Bucket" AND resource.iamPolicy.bindings.members="allUsers"'

# List assets changed within the last 24 hours
gcloud scc assets list \
  --organization=ORG_ID \
  --filter="updateTime>2025-03-13T00:00:00Z"

# Describe a specific asset
gcloud scc assets describe \
  --organization=ORG_ID \
  --asset=ASSET_ID

# Get security marks on an asset
gcloud scc assets get-security-marks \
  --organization=ORG_ID \
  --asset=ASSET_ID

# Update security marks on an asset
gcloud scc assets update-security-marks ASSET_ID \
  --organization=ORG_ID \
  --security-marks=data_classification=pii,env=production

# Remove a security mark
gcloud scc assets update-security-marks ASSET_ID \
  --organization=ORG_ID \
  --remove-security-marks=old_mark
```

---

## Notification Configs

```bash
# Create a Pub/Sub topic for SCC notifications
gcloud pubsub topics create scc-findings-notifications \
  --project=PROJECT_ID

# Grant the SCC service account permission to publish
gcloud pubsub topics add-iam-policy-binding scc-findings-notifications \
  --member="serviceAccount:service-org-ORG_ID@security-center-api.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher" \
  --project=PROJECT_ID

# Create a notification config for all CRITICAL and HIGH findings
gcloud scc notifications create critical-high-findings \
  --organization=ORG_ID \
  --description="Notify on critical and high severity findings" \
  --pubsub-topic=projects/PROJECT_ID/topics/scc-findings-notifications \
  --filter="state=ACTIVE AND (severity=CRITICAL OR severity=HIGH)"

# Create a notification config for all active findings (no filter)
gcloud scc notifications create all-active-findings \
  --organization=ORG_ID \
  --pubsub-topic=projects/PROJECT_ID/topics/scc-findings-notifications \
  --filter="state=ACTIVE"

# Create a notification for threat findings only
gcloud scc notifications create threat-notifications \
  --organization=ORG_ID \
  --pubsub-topic=projects/PROJECT_ID/topics/scc-findings-notifications \
  --filter='state=ACTIVE AND finding_class=THREAT'

# List notification configs
gcloud scc notifications list \
  --organization=ORG_ID

# Describe a notification config
gcloud scc notifications describe critical-high-findings \
  --organization=ORG_ID

# Update a notification config filter
gcloud scc notifications update critical-high-findings \
  --organization=ORG_ID \
  --filter="state=ACTIVE AND severity=CRITICAL"

# Delete a notification config
gcloud scc notifications delete critical-high-findings \
  --organization=ORG_ID
```

---

## Mute Configurations

```bash
# Create a mute rule (bulk-mute findings matching a filter)
gcloud scc muteconfigs create test-env-mute \
  --organization=ORG_ID \
  --description="Mute all findings in test projects" \
  --filter='resource.project_display_name="my-test-project"'

# Create a mute rule for a specific finding category
gcloud scc muteconfigs create open-ssh-mute \
  --organization=ORG_ID \
  --description="Mute OPEN_SSH_PORT for approved bastion hosts" \
  --filter='category="OPEN_SSH_PORT" AND resource.name:"my-bastion"'

# List mute configs for an organization
gcloud scc muteconfigs list \
  --organization=ORG_ID

# Describe a mute config
gcloud scc muteconfigs describe test-env-mute \
  --organization=ORG_ID

# Update a mute config filter
gcloud scc muteconfigs update test-env-mute \
  --organization=ORG_ID \
  --filter='resource.project_display_name="test-project" OR resource.project_display_name="dev-project"'

# Delete a mute config
gcloud scc muteconfigs delete test-env-mute \
  --organization=ORG_ID

# Bulk-mute existing findings matching a filter (one-time operation, not a persistent rule)
gcloud scc findings bulk-mute \
  --organization=ORG_ID \
  --filter='state=ACTIVE AND category="AUDIT_LOGGING_DISABLED" AND resource.project_display_name:"test"'
```

---

## Custom Findings (Writing to a Custom Source)

```bash
# Create a finding in a custom source via REST API (gcloud does not have a findings create subcommand)
# Use curl with Application Default Credentials:
TOKEN=$(gcloud auth print-access-token)
curl -X POST \
  "https://securitycenter.googleapis.com/v1/organizations/ORG_ID/sources/SOURCE_ID/findings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "ACTIVE",
    "resourceName": "//cloudresourcemanager.googleapis.com/projects/my-project",
    "category": "EXPOSED_CREDENTIAL",
    "severity": "HIGH",
    "findingClass": "VULNERABILITY",
    "eventTime": "2025-03-14T12:00:00Z",
    "sourceProperties": {
      "scanner_name": "my-custom-scanner",
      "detail": "API key found in Cloud Storage object",
      "affected_object": "gs://my-bucket/config.json"
    }
  }'
```

---

## Export to BigQuery and Cloud Storage

```bash
# Create a BigQuery dataset for SCC export
bq mk \
  --dataset \
  --location=US \
  PROJECT_ID:scc_findings

# Create a continuous export to BigQuery (via SCC API; gcloud supports this in beta)
gcloud scc bqexports create my-bq-export \
  --organization=ORG_ID \
  --dataset=projects/PROJECT_ID/datasets/scc_findings \
  --filter="state=ACTIVE"

# List BigQuery exports
gcloud scc bqexports list \
  --organization=ORG_ID

# Describe a BigQuery export
gcloud scc bqexports describe my-bq-export \
  --organization=ORG_ID

# Delete a BigQuery export
gcloud scc bqexports delete my-bq-export \
  --organization=ORG_ID

# Example BigQuery query: count active findings by severity (after export is running)
bq query --use_legacy_sql=false '
  SELECT
    finding.severity,
    COUNT(*) as finding_count
  FROM `PROJECT_ID.scc_findings.findings`
  WHERE finding.state = "ACTIVE"
  GROUP BY finding.severity
  ORDER BY finding_count DESC
'

# Example BigQuery query: findings by category for compliance review
bq query --use_legacy_sql=false '
  SELECT
    finding.category,
    finding.severity,
    COUNT(*) as count
  FROM `PROJECT_ID.scc_findings.findings`
  WHERE finding.state = "ACTIVE"
    AND finding.event_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY 1, 2
  ORDER BY count DESC
  LIMIT 50
'
```

---

## Posture and Compliance

```bash
# List security posture configurations (if using SCC Posture feature)
gcloud scc postures list \
  --organization=ORG_ID \
  --location=global

# Create a security posture from a YAML file
gcloud scc postures create my-posture \
  --organization=ORG_ID \
  --location=global \
  --posture-file=posture.yaml

# Deploy a posture to a project or folder
gcloud scc posture-deployments create my-posture-deployment \
  --organization=ORG_ID \
  --location=global \
  --posture-name=organizations/ORG_ID/locations/global/postures/my-posture \
  --posture-revision-id=REVISION_ID \
  --target-resource=projects/PROJECT_ID

# List posture deployments
gcloud scc posture-deployments list \
  --organization=ORG_ID \
  --location=global

# Run a posture drift check (compare deployed posture vs actual config)
gcloud scc posture-deployments validate my-posture-deployment \
  --organization=ORG_ID \
  --location=global
```
