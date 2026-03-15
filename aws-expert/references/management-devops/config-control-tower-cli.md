# AWS Config / Control Tower — CLI Reference

For service concepts, see [config-control-tower-capabilities.md](config-control-tower-capabilities.md).

## AWS Config

```bash
# --- Config Rules ---
# Create a managed Config rule
aws configservice put-config-rule \
  --config-rule '{
    "ConfigRuleName": "s3-bucket-public-read-prohibited",
    "Source": {
      "Owner": "AWS",
      "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
    }
  }'

# Create a custom Lambda Config rule
aws configservice put-config-rule \
  --config-rule '{
    "ConfigRuleName": "my-custom-rule",
    "Source": {
      "Owner": "CUSTOM_LAMBDA",
      "SourceIdentifier": "arn:aws:lambda:us-east-1:123456789012:function:my-config-rule",
      "SourceDetails": [
        {"EventSource": "aws.config", "MessageType": "ConfigurationItemChangeNotification"},
        {"EventSource": "aws.config", "MessageType": "ScheduledNotification", "MaximumExecutionFrequency": "One_Hour"}
      ]
    },
    "Scope": {
      "ComplianceResourceTypes": ["AWS::EC2::Instance"]
    }
  }'

# Describe Config rules
aws configservice describe-config-rules
aws configservice describe-config-rules \
  --config-rule-names s3-bucket-public-read-prohibited my-custom-rule

# Start evaluation of a Config rule
aws configservice start-config-rules-evaluation \
  --config-rule-names s3-bucket-public-read-prohibited

# Get compliance by config rule
aws configservice describe-compliance-by-config-rule \
  --config-rule-names s3-bucket-public-read-prohibited \
  --compliance-types NON_COMPLIANT

# Get compliance details (which resources are non-compliant)
aws configservice get-compliance-details-by-config-rule \
  --config-rule-name s3-bucket-public-read-prohibited \
  --compliance-types NON_COMPLIANT

# Get compliance by resource type
aws configservice describe-compliance-by-resource \
  --resource-type AWS::S3::Bucket \
  --compliance-types NON_COMPLIANT

# Delete a Config rule
aws configservice delete-config-rule \
  --config-rule-name my-custom-rule

# --- Conformance Packs ---
# Deploy a conformance pack
aws configservice put-conformance-pack \
  --conformance-pack-name my-security-pack \
  --template-body file://conformance-pack.yaml \
  --delivery-s3-bucket my-config-bucket

# Describe conformance packs
aws configservice describe-conformance-packs
aws configservice describe-conformance-packs \
  --conformance-pack-names my-security-pack

# Get compliance summary for a conformance pack
aws configservice get-conformance-pack-compliance-summary \
  --conformance-pack-names my-security-pack

# Get compliance details for a conformance pack
aws configservice get-conformance-pack-compliance-details \
  --conformance-pack-name my-security-pack \
  --filters ComplianceType=NON_COMPLIANT

# Delete a conformance pack
aws configservice delete-conformance-pack \
  --conformance-pack-name my-security-pack

# --- Aggregators ---
# Authorize a source account to contribute to an aggregator
aws configservice put-aggregation-authorization \
  --authorized-account-id 123456789012 \
  --authorized-aws-region us-east-1

# Create an aggregator (aggregate across accounts/regions)
aws configservice put-configuration-aggregator \
  --configuration-aggregator-name my-aggregator \
  --account-aggregation-sources '[
    {
      "AccountIds": ["123456789012", "234567890123"],
      "AllAwsRegions": true
    }
  ]'

# Create an org-wide aggregator
aws configservice put-configuration-aggregator \
  --configuration-aggregator-name org-aggregator \
  --organization-aggregation-source \
    RoleArn=arn:aws:iam::123456789012:role/ConfigOrgRole,AllAwsRegions=true

# Describe aggregators
aws configservice describe-configuration-aggregators

# Get aggregated compliance data
aws configservice get-aggregate-compliance-details-by-config-rule \
  --configuration-aggregator-name org-aggregator \
  --config-rule-name s3-bucket-public-read-prohibited \
  --compliance-type NON_COMPLIANT \
  --account-id 123456789012 \
  --aws-region us-east-1

# --- Remediation ---
# Configure automatic remediation
aws configservice put-remediation-configurations \
  --remediation-configurations '[
    {
      "ConfigRuleName": "s3-bucket-public-read-prohibited",
      "TargetType": "SSM_DOCUMENT",
      "TargetId": "AWS-DisableS3BucketPublicReadWrite",
      "Parameters": {
        "AutomationAssumeRole": {
          "StaticValue": {"Values": ["arn:aws:iam::123456789012:role/RemediationRole"]}
        },
        "S3BucketName": {"ResourceValue": {"Value": "RESOURCE_ID"}}
      },
      "Automatic": true,
      "MaximumAutomaticAttempts": 3,
      "RetryAttemptSeconds": 60
    }
  ]'

# Start manual remediation
aws configservice start-remediation-execution \
  --config-rule-name s3-bucket-public-read-prohibited \
  --resource-keys '[{"resourceType":"AWS::S3::Bucket","resourceId":"my-bucket"}]'

# --- Resource Queries ---
# Advanced SQL query against current config state
aws configservice select-resource-config \
  --expression "SELECT resourceId, resourceType, configuration WHERE resourceType='AWS::EC2::Instance' AND configuration.state.name='running'"

# Select aggregate resource config (across accounts)
aws configservice select-aggregate-resource-config \
  --configuration-aggregator-name org-aggregator \
  --expression "SELECT accountId, awsRegion, resourceId WHERE resourceType='AWS::S3::Bucket' AND supplementaryConfiguration.PublicAccessBlockConfiguration IS NULL"

# --- Configuration Recorder ---
aws configservice describe-configuration-recorders
aws configservice describe-configuration-recorder-status

aws configservice start-configuration-recorder \
  --configuration-recorder-name default

aws configservice stop-configuration-recorder \
  --configuration-recorder-name default

# --- Delivery Channel ---
aws configservice describe-delivery-channels
aws configservice deliver-config-snapshot \
  --delivery-channel-name default
```

---

## Control Tower

```bash
# --- Landing Zones ---
# List landing zones
aws controltower list-landing-zones

# Get details of a landing zone
aws controltower get-landing-zone \
  --landing-zone-identifier arn:aws:controltower:us-east-1:123456789012:landingzone/EXAMPLE

# Get the latest landing zone operation status
aws controltower get-landing-zone-operation \
  --operation-identifier <operation-id>

# --- Controls (Guardrails) ---
# List all enabled controls for an OU
aws controltower list-enabled-controls \
  --target-identifier arn:aws:organizations::123456789012:ou/o-example/ou-example-xxxxxxxx

# Enable a control on an OU
aws controltower enable-control \
  --control-identifier arn:aws:controltower:us-east-1::control/AWS-GR_DISALLOW_VPC_INTERNET_ACCESS \
  --target-identifier arn:aws:organizations::123456789012:ou/o-example/ou-example-xxxxxxxx
# Returns operationIdentifier

# Get the status of a control operation
aws controltower get-control-operation \
  --operation-identifier <operation-identifier>

# Disable a control on an OU
aws controltower disable-control \
  --control-identifier arn:aws:controltower:us-east-1::control/AWS-GR_DISALLOW_VPC_INTERNET_ACCESS \
  --target-identifier arn:aws:organizations::123456789012:ou/o-example/ou-example-xxxxxxxx

# Get enabled control details
aws controltower get-enabled-control \
  --enabled-control-identifier arn:aws:controltower:us-east-1:123456789012:enabledcontrol/EXAMPLE

# List all available controls
aws controltower list-controls

# Get details for a specific control definition
aws controltower get-control \
  --control-identifier arn:aws:controltower:us-east-1::control/AWS-GR_DISALLOW_VPC_INTERNET_ACCESS

# --- Baselines ---
# List available baselines (e.g., AWSControlTowerBaseline)
aws controltower list-baselines

# Enable a baseline on a target (OU or account)
aws controltower enable-baseline \
  --baseline-identifier arn:aws:controltower:us-east-1::baseline/AWSControlTowerBaseline \
  --baseline-version "3.0" \
  --target-identifier arn:aws:organizations::123456789012:ou/o-example/ou-example-xxxxxxxx
# Returns operationIdentifier

# List enabled baselines
aws controltower list-enabled-baselines

# Get an enabled baseline
aws controltower get-enabled-baseline \
  --enabled-baseline-identifier arn:aws:controltower:us-east-1:123456789012:enabledbaseline/EXAMPLE

# Reset an enabled baseline (re-apply baseline configuration)
aws controltower reset-enabled-baseline \
  --enabled-baseline-identifier arn:aws:controltower:us-east-1:123456789012:enabledbaseline/EXAMPLE

# Disable a baseline
aws controltower disable-baseline \
  --enabled-baseline-identifier arn:aws:controltower:us-east-1:123456789012:enabledbaseline/EXAMPLE
```
