# AWS Security Hub, Inspector & Macie — CLI Reference
For service concepts, see [security-hub-inspector-macie-capabilities.md](security-hub-inspector-macie-capabilities.md).

## AWS Security Hub

```bash
# --- Enable ---
aws securityhub enable-security-hub \
  --enable-default-standards \
  --tags Environment=Production
aws securityhub describe-hub
aws securityhub disable-security-hub

# --- Standards ---
aws securityhub describe-standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0 \
    StandardsArn=arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0
aws securityhub get-enabled-standards
aws securityhub batch-disable-standards \
  --standards-subscription-arns arn:aws:securityhub:us-east-1:123456789012:subscription/pci-dss/v/3.2.1

# Controls
aws securityhub describe-standards-controls \
  --standards-subscription-arn arn:aws:securityhub:us-east-1:123456789012:subscription/aws-foundational-security-best-practices/v/1.0.0
aws securityhub update-standards-control \
  --standards-control-arn arn:aws:securityhub:us-east-1:123456789012:control/cis-aws-foundations-benchmark/v/1.2.0/2.9 \
  --control-status DISABLED \
  --disabled-reason "S3 access logging not required for this bucket"

# --- Findings ---
aws securityhub get-findings
aws securityhub get-findings \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}'
aws securityhub batch-update-findings \
  --finding-identifiers Id=finding-id,ProductArn=arn:aws:securityhub:us-east-1::product/aws/guardduty \
  --workflow Status=RESOLVED \
  --note Text="Investigated and resolved - false positive",UpdatedBy=soc-analyst

# Custom findings (from your own tools)
aws securityhub batch-import-findings --findings file://findings.json  # must follow ASFF format

# --- Insights ---
aws securityhub get-insights
aws securityhub create-insight \
  --name "Critical unresolved findings by account" \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"WorkflowStatus":[{"Value":"NEW","Comparison":"EQUALS"}]}' \
  --group-by-attribute AwsAccountId
aws securityhub get-insight-results --insight-arn arn:aws:securityhub:us-east-1:123456789012:insight/123456789012/custom/xxx
aws securityhub delete-insight --insight-arn arn:aws:securityhub:...:insight/xxx

# --- Custom actions (for EventBridge) ---
aws securityhub create-action-target \
  --name "Notify Slack" \
  --description "Send finding to Slack channel via EventBridge" \
  --id NOTIFY-SLACK
aws securityhub describe-action-targets
aws securityhub update-action-target \
  --action-target-arn arn:aws:securityhub:us-east-1:123456789012:action/custom/NOTIFY-SLACK \
  --description "Updated description"
aws securityhub delete-action-target \
  --action-target-arn arn:aws:securityhub:us-east-1:123456789012:action/custom/NOTIFY-SLACK

# --- Multi-account ---
aws securityhub enable-organization-admin-account --admin-account-id 123456789012
aws securityhub list-organization-admin-accounts
aws securityhub describe-organization-configuration
aws securityhub update-organization-configuration \
  --auto-enable \
  --auto-enable-standards DEFAULT

# Aggregation
aws securityhub create-finding-aggregator --region-linking-mode ALL_REGIONS
aws securityhub get-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx
aws securityhub update-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx \
  --region-linking-mode SPECIFIED_REGIONS \
  --regions us-east-1 us-west-2 eu-west-1
aws securityhub delete-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx
```

---

## Amazon Inspector

```bash
# --- Enable ---
aws inspector2 enable \
  --account-ids 123456789012 \
  --resource-types EC2 ECR LAMBDA LAMBDA_CODE
aws inspector2 describe-organization-configuration
aws inspector2 update-organization-configuration \
  --auto-enable Ec2=true,Ecr=true,Lambda=true,LambdaCode=true
aws inspector2 disable --account-ids 123456789012 --resource-types ECR

# --- Findings ---
aws inspector2 list-findings
aws inspector2 list-findings \
  --filter-criteria '{"severities":[{"comparison":"EQUALS","value":"CRITICAL"}],"findingStatus":[{"comparison":"EQUALS","value":"ACTIVE"}]}'
aws inspector2 batch-get-finding-details --finding-arns arn:aws:inspector2:us-east-1:123456789012:finding/xxx
aws inspector2 list-finding-aggregations \
  --aggregation-type AWS_EC2_INSTANCE
aws inspector2 get-findings-report-status

# Suppress findings
aws inspector2 create-filter \
  --name SuppressAcceptedRisk \
  --action SUPPRESS \
  --filter-criteria '{"vulnerabilityId":[{"comparison":"EQUALS","value":"CVE-2021-44228"}]}'
aws inspector2 list-filters
aws inspector2 update-filter \
  --filter-arn arn:aws:inspector2:us-east-1:123456789012:filter/xxx \
  --name UpdatedFilterName
aws inspector2 delete-filter --filter-arn arn:aws:inspector2:...:filter/xxx

# --- Coverage ---
aws inspector2 list-coverage  # see all resources being scanned
aws inspector2 list-coverage-statistics  # summary counts
aws inspector2 get-configuration  # EC2/ECR/Lambda scan settings

# --- CIS Scans ---
aws inspector2 create-cis-scan-configuration \
  --scan-name "CIS Level 1 Weekly" \
  --security-level LEVEL_1 \
  --schedule Weekly='{Day=MONDAY,StartTime={TimeOfDay="08:00",Timezone="UTC"}}' \
  --targets AccountIds=123456789012,All=false
aws inspector2 list-cis-scan-configurations
aws inspector2 list-cis-scans
aws inspector2 get-cis-scan-report \
  --scan-arn arn:aws:inspector2:us-east-1:123456789012:owner/123456789012/cis-scan/xxx \
  --target-accounts 123456789012 \
  --report-format PDF \
  --s3-destination BucketName=my-bucket,KeyPrefix=cis-reports/

# --- SBOM export ---
aws inspector2 create-sbom-export \
  --report-format CYCLONEDX_1_4 \
  --s3-destination BucketName=my-bucket,KeyPrefix=sboms/ \
  --resource-filter-criteria '{"ec2InstanceTags":[{"comparison":"EQUALS","key":"Environment","value":"Production"}]}'
aws inspector2 get-sbom-export --report-id report-id
aws inspector2 cancel-sbom-export --report-id report-id

# --- Multi-account ---
aws inspector2 enable-delegated-admin-account --delegated-admin-account-id 123456789012
aws inspector2 get-delegated-admin-account
aws inspector2 disable-delegated-admin-account --delegated-admin-account-id 123456789012
aws inspector2 list-member-accounts
aws inspector2 associate-member --account-id 111111111111
aws inspector2 disassociate-member --account-id 111111111111
```

---

## Amazon Macie

```bash
# --- Enable ---
aws macie2 enable-macie --finding-publishing-frequency FIFTEEN_MINUTES --status ENABLED
aws macie2 get-macie-session
aws macie2 update-macie-session \
  --finding-publishing-frequency ONE_HOUR \
  --status PAUSED  # or ENABLED
aws macie2 disable-macie

# --- S3 bucket inventory ---
aws macie2 describe-buckets  # all S3 buckets Macie monitors
aws macie2 describe-buckets \
  --criteria '{"sharedAccess":{"eq":["EXTERNAL"]}}'  # externally shared buckets
aws macie2 get-bucket-statistics
aws macie2 get-s3-resources  # S3 resources Macie is configured to monitor

# --- Sensitive data discovery jobs ---
aws macie2 create-classification-job \
  --name WeeklyS3Scan \
  --job-type SCHEDULED \
  --s3-job-definition '{
    "bucketDefinitions": [{"accountId":"123456789012","buckets":["my-data-bucket"]}]
  }' \
  --schedule-frequency DailySchedule={} \
  --sampling-percentage 100 \
  --managed-data-identifier-selector ALL

aws macie2 list-classification-jobs
aws macie2 describe-classification-job --job-id job-id
aws macie2 update-classification-job \
  --job-id job-id \
  --job-status CANCELLED  # RUNNING, PAUSED, CANCELLED (permanent)

# --- Findings ---
aws macie2 list-findings
aws macie2 list-findings \
  --finding-criteria '{"criterion":{"severity.description":{"eq":["High","Critical"]}}}'
aws macie2 get-findings --finding-ids finding-id-1 finding-id-2
aws macie2 get-finding-statistics \
  --group-by resourcesAffected.s3Object.path

# Suppress findings
aws macie2 create-findings-filter \
  --name SuppressTestData \
  --action ARCHIVE \
  --finding-criteria '{"criterion":{"resourcesAffected.s3Bucket.name":{"eq":["test-data-bucket"]}}}'
aws macie2 list-findings-filters
aws macie2 get-findings-filter --id filter-id
aws macie2 update-findings-filter \
  --id filter-id \
  --name UpdatedFilterName
aws macie2 delete-findings-filter --id filter-id

# --- Custom data identifiers ---
aws macie2 create-custom-data-identifier \
  --name InternalEmployeeID \
  --regex "EMP-[0-9]{6}" \
  --keywords "employee" "staff" \
  --ignore-words "test" "sample" \
  --maximum-match-distance 50
aws macie2 list-custom-data-identifiers
aws macie2 get-custom-data-identifier --id identifier-id
aws macie2 test-custom-data-identifier \
  --regex "EMP-[0-9]{6}" \
  --sample-text "Employee EMP-123456 has been flagged"  # returns matchCount
aws macie2 delete-custom-data-identifier --id identifier-id

# --- Allow lists ---
aws macie2 create-allow-list \
  --name KnownTestSSNs \
  --criteria Regex="{Regex=\"123-45-6789|000-00-0000\"}"
aws macie2 list-allow-lists
aws macie2 get-allow-list --id list-id
aws macie2 update-allow-list \
  --id list-id \
  --name UpdatedListName \
  --criteria Regex="{Regex=\"123-45-6789\"}"
aws macie2 delete-allow-list --id list-id

# --- Multi-account ---
aws macie2 enable-organization-admin-account --admin-account-id 123456789012
aws macie2 describe-organization-configuration
aws macie2 update-organization-configuration --auto-enable
aws macie2 list-members
aws macie2 create-member --account AccountId=111111111111,Email=account@example.com
aws macie2 get-member --id 111111111111
aws macie2 delete-member --id 111111111111

# --- Finding export ---
aws macie2 put-findings-publication-configuration \
  --security-hub-configuration PublishClassificationFindings=true,PublishPolicyFindings=true
aws macie2 get-findings-publication-configuration
```

---

## AWS Security Incident Response

```bash
# --- Membership ---
# Enroll an account in Security Incident Response
aws security-ir create-membership \
  --account-id 123456789012 \
  --client-token $(uuidgen) \
  --membership-name "MyOrg-SecurityIR"

aws security-ir get-membership \
  --membership-id <membership-id>

aws security-ir list-memberships

# --- Cases ---
# Create a new incident case
aws security-ir create-case \
  --membership-id <membership-id> \
  --title "Possible credential compromise - prod account" \
  --description "GuardDuty finding indicates unusual API calls from an assumed role." \
  --engagement-type Security \
  --reported-time-stamp $(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --impact-scope "Production environment, account 123456789012" \
  --watchers '[{"email":"ciso@example.com","name":"CISO"}]' \
  --resolvers '[{"principal":"arn:aws:iam::123456789012:role/IRAnalystRole","name":"IR Analyst"}]'

aws security-ir get-case \
  --case-id <case-id>

aws security-ir list-cases \
  --membership-id <membership-id>

# Update case fields (title, description, status, etc.)
aws security-ir update-case \
  --case-id <case-id> \
  --title "Confirmed credential compromise - prod account" \
  --impact-scope "Production environment — credential rotated"

# Add a comment or evidence note to a case
aws security-ir create-case-comment \
  --case-id <case-id> \
  --body "Identified the compromised access key. Rotated credentials and revoked sessions."

# List all edits and comments on a case (audit trail)
aws security-ir list-case-edits \
  --case-id <case-id>

# Close a case
aws security-ir close-case \
  --case-id <case-id>

# --- Attachments ---
# Get a pre-signed URL to upload an attachment (log file, screenshot, etc.)
aws security-ir get-case-attachment-upload-url \
  --case-id <case-id> \
  --file-name "cloudtrail-evidence.json" \
  --content-type application/json
# Then upload the file to the returned pre-signed S3 URL
```
