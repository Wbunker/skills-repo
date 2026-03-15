# Governance & Advisory Tools — CLI Reference

For service concepts, see [governance-advisory-capabilities.md](governance-advisory-capabilities.md).

## AWS Service Catalog

```bash
# --- Portfolios ---
# Create a portfolio
aws servicecatalog create-portfolio \
  --display-name "Platform Engineering Products" \
  --provider-name "Platform Team" \
  --description "Approved infrastructure products"

# List all portfolios
aws servicecatalog list-portfolios

# Share a portfolio with another account
aws servicecatalog create-portfolio-share \
  --portfolio-id port-xxxxxxxxxx \
  --account-id 234567890123

# Share a portfolio with an entire Organizations OU
aws servicecatalog create-portfolio-share \
  --portfolio-id port-xxxxxxxxxx \
  --organization-node '{"Type":"ORGANIZATIONAL_UNIT","Value":"ou-xxxx-xxxxxxxx"}'

# Accept a shared portfolio (run in the receiving account)
aws servicecatalog accept-portfolio-share \
  --portfolio-id port-xxxxxxxxxx

# --- Products ---
# Create a product backed by a CloudFormation template in S3
aws servicecatalog create-product \
  --name "VPC Standard" \
  --product-type CLOUD_FORMATION_TEMPLATE \
  --provisioning-artifact-parameters '{
    "Name": "v1.0",
    "Type": "CLOUD_FORMATION_TEMPLATE",
    "Info": {"LoadTemplateFromURL": "https://s3.amazonaws.com/my-bucket/vpc-template.yaml"}
  }' \
  --owner "Platform Team"

# List products in a portfolio
aws servicecatalog search-products-as-admin \
  --portfolio-id port-xxxxxxxxxx

# Add a new version (provisioning artifact) to a product
aws servicecatalog create-provisioning-artifact \
  --product-id prod-xxxxxxxxxx \
  --parameters '{
    "Name": "v2.0",
    "Type": "CLOUD_FORMATION_TEMPLATE",
    "Info": {"LoadTemplateFromURL": "https://s3.amazonaws.com/my-bucket/vpc-template-v2.yaml"}
  }'

# Associate a product with a portfolio
aws servicecatalog associate-product-with-portfolio \
  --product-id prod-xxxxxxxxxx \
  --portfolio-id port-xxxxxxxxxx

# --- Constraints ---
# Create a launch constraint (IAM role assumed during provisioning)
aws servicecatalog create-constraint \
  --portfolio-id port-xxxxxxxxxx \
  --product-id prod-xxxxxxxxxx \
  --type LAUNCH \
  --parameters '{"RoleArn":"arn:aws:iam::123456789012:role/ServiceCatalogLaunchRole"}'

# Create a StackSet constraint (deploy to multiple accounts/regions)
aws servicecatalog create-constraint \
  --portfolio-id port-xxxxxxxxxx \
  --product-id prod-xxxxxxxxxx \
  --type STACKSET \
  --parameters '{
    "Version": "String",
    "Properties": {
      "AccountList": ["123456789012","234567890123"],
      "RegionList": ["us-east-1","us-west-2"],
      "AdminRole": "AWSCloudFormationStackSetAdministrationRole",
      "ExecutionRole": "AWSCloudFormationStackSetExecutionRole"
    }
  }'

# List constraints for a portfolio
aws servicecatalog list-constraints-for-portfolio \
  --portfolio-id port-xxxxxxxxxx

# --- TagOptions ---
# Create a TagOption (reusable tag key/value pair)
aws servicecatalog create-tag-option \
  --key "Environment" \
  --value "production"

# List all TagOptions
aws servicecatalog list-tag-options

# Associate a TagOption with a portfolio
aws servicecatalog associate-tag-option-with-resource \
  --resource-id port-xxxxxxxxxx \
  --tag-option-id tag-xxxxxxxxxx

# --- Provisioning ---
# Provision a product (launch it for an end user)
aws servicecatalog provision-product \
  --product-id prod-xxxxxxxxxx \
  --provisioning-artifact-id pa-xxxxxxxxxx \
  --provisioned-product-name "my-vpc-prod" \
  --provisioning-parameters Key=VpcCidr,Value=10.0.0.0/16

# List provisioned products
aws servicecatalog search-provisioned-products

# Describe a provisioned product
aws servicecatalog describe-provisioned-product \
  --name my-vpc-prod

# Update a provisioned product
aws servicecatalog update-provisioned-product \
  --provisioned-product-name my-vpc-prod \
  --provisioning-parameters Key=VpcCidr,Value=10.1.0.0/16

# Terminate a provisioned product
aws servicecatalog terminate-provisioned-product \
  --provisioned-product-name my-vpc-prod

# --- Service Actions ---
# Execute a service action on a provisioned product
aws servicecatalog execute-provisioned-product-service-action \
  --provisioned-product-id pp-xxxxxxxxxx \
  --service-action-id act-xxxxxxxxxx
```

---

## AWS Trusted Advisor

```bash
# --- Checks ---
# List all available Trusted Advisor checks
aws trustedadvisor list-checks

# List checks filtered by category (COST_OPTIMIZING, PERFORMANCE, SECURITY, FAULT_TOLERANCE, SERVICE_LIMITS)
aws trustedadvisor list-checks \
  --pillar SECURITY

# --- Recommendations ---
# List all recommendations for this account
aws trustedadvisor list-recommendations

# List recommendations filtered by pillar and status
aws trustedadvisor list-recommendations \
  --pillar COST_OPTIMIZING \
  --status warning

# Get details of a specific recommendation
aws trustedadvisor get-recommendation \
  --recommendation-identifier <recommendation-id>

# List resources affected by a recommendation
aws trustedadvisor list-recommendation-resources \
  --recommendation-identifier <recommendation-id>

# Exclude specific resources from a recommendation (suppress false positives)
aws trustedadvisor batch-update-recommendation-resource-exclusion \
  --recommendation-resource-exclusions '[
    {"arn":"arn:aws:ec2:us-east-1:123456789012:instance/i-xxxxxxxxxx","isExcluded":true}
  ]'

# Update recommendation lifecycle (track remediation)
aws trustedadvisor update-recommendation-lifecycle \
  --recommendation-identifier <recommendation-id> \
  --lifecycle-stage in_progress \
  --update-reason "Scheduled for remediation in next sprint"

# Mark recommendation as resolved
aws trustedadvisor update-recommendation-lifecycle \
  --recommendation-identifier <recommendation-id> \
  --lifecycle-stage resolved

# --- Organizational View ---
# List recommendations across all accounts in the organization
aws trustedadvisor list-organization-recommendations \
  --pillar SECURITY

# Get a specific organization-level recommendation
aws trustedadvisor get-organization-recommendation \
  --organization-recommendation-identifier <org-recommendation-id>

# List affected resources across organization for a recommendation
aws trustedadvisor list-organization-recommendation-resources \
  --organization-recommendation-identifier <org-recommendation-id>

# List which accounts are affected by an organization recommendation
aws trustedadvisor list-organization-recommendation-accounts \
  --organization-recommendation-identifier <org-recommendation-id>

# Update lifecycle status at the organization level
aws trustedadvisor update-organization-recommendation-lifecycle \
  --organization-recommendation-identifier <org-recommendation-id> \
  --lifecycle-stage resolved
```

---

## AWS Health Dashboard

```bash
# Note: The Health API endpoint is global (us-east-1); use --region us-east-1
# Business, Enterprise On-Ramp, or Enterprise Support plan required for API access

# --- Events ---
# Describe all open Health events affecting this account
aws health describe-events \
  --region us-east-1 \
  --filter '{"eventStatusCodes":["open","upcoming"]}'

# Filter events by service and category
aws health describe-events \
  --region us-east-1 \
  --filter '{
    "services": ["EC2","RDS"],
    "eventCategories": ["scheduledChange"],
    "eventStatusCodes": ["upcoming","open"]
  }'

# Get detailed information about specific events
aws health describe-event-details \
  --region us-east-1 \
  --event-arns arn:aws:health:us-east-1::event/EC2/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED_EXAMPLE

# List all Health event types for a service
aws health describe-event-types \
  --region us-east-1 \
  --filter '{"services":["EC2"]}'

# --- Affected Entities ---
# List resources affected by a Health event
aws health describe-affected-entities \
  --region us-east-1 \
  --filter '{
    "eventArns": ["arn:aws:health:us-east-1::event/EC2/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED/EXAMPLE"]
  }'

# Get aggregate counts of affected entities by status
aws health describe-entity-aggregates \
  --region us-east-1 \
  --event-arns arn:aws:health:us-east-1::event/EC2/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED/EXAMPLE

# --- Organizational View ---
# Enable organizational view (run from management account)
aws health enable-health-service-access-for-organization \
  --region us-east-1

# Describe Health events across the entire organization
aws health describe-events-for-organization \
  --region us-east-1 \
  --organization-event-detail-filters '[{
    "eventStatusCodes": ["open"],
    "eventTypeCategories": ["issue"]
  }]'

# Get details of an organization event
aws health describe-event-details-for-organization \
  --region us-east-1 \
  --organization-event-detail-filters '[{
    "eventArn": "arn:aws:health:us-east-1::event/EC2/AWS_EC2_ISSUE_EXAMPLE"
  }]'

# List accounts affected by an organization event
aws health describe-affected-accounts-for-organization \
  --region us-east-1 \
  --event-arn arn:aws:health:us-east-1::event/EC2/AWS_EC2_ISSUE_EXAMPLE

# List affected entities across the organization for an event
aws health describe-affected-entities-for-organization \
  --region us-east-1 \
  --organization-entity-filters '[{
    "eventArn": "arn:aws:health:us-east-1::event/EC2/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED/EXAMPLE",
    "awsAccountId": "123456789012"
  }]'
```

---

## AWS License Manager

```bash
# --- License Configurations ---
# Create a license configuration for SQL Server (vCPU-based)
aws license-manager create-license-configuration \
  --name "SQLServer-Enterprise-vCPU" \
  --license-counting-type vCPU \
  --license-count 100 \
  --license-count-hard-limit  # Hard limit: blocks launches exceeding count

# Create a license configuration with soft limit (warn only)
aws license-manager create-license-configuration \
  --name "Windows-Server-Sockets" \
  --license-counting-type Socket \
  --license-count 50
  # Without --license-count-hard-limit, the limit is a soft warning

# List all license configurations
aws license-manager list-license-configurations

# Get details of a specific configuration
aws license-manager get-license-configuration \
  --license-configuration-arn arn:aws:license-manager:us-east-1:123456789012:license-configuration:lic-xxxxxxxxxx

# Update license count
aws license-manager update-license-configuration \
  --license-configuration-arn arn:aws:license-manager:us-east-1:123456789012:license-configuration:lic-xxxxxxxxxx \
  --license-count 200

# List resources (EC2 instances) consuming a license configuration
aws license-manager list-associations-for-license-configuration \
  --license-configuration-arn arn:aws:license-manager:us-east-1:123456789012:license-configuration:lic-xxxxxxxxxx

# --- Resource Inventory ---
# Discover on-premises and AWS resource inventory
aws license-manager list-resource-inventory

# --- Managed Licenses (ISV / Marketplace) ---
# List licenses received (e.g., from AWS Marketplace or a grant)
aws license-manager list-received-licenses

# List licenses you have distributed to other accounts
aws license-manager list-distributed-grants

# Create a grant to share license use rights with another account
aws license-manager create-grant \
  --grant-name "DataTeam-Access" \
  --license-arn arn:aws:license-manager::123456789012:license:EXAMPLE \
  --principals '["arn:aws:iam::234567890123:root"]' \
  --home-region us-east-1 \
  --allowed-operations '["CheckoutLicense","CheckInLicense","ExtendConsumptionLicense"]'

# Accept a grant (run in the receiving account)
aws license-manager accept-grant \
  --grant-arn arn:aws:license-manager:us-east-1:123456789012:grant:EXAMPLE

# List grants received by this account
aws license-manager list-received-grants

# --- License Checkout (Application-Level) ---
# Check out a license entitlement at runtime
aws license-manager checkout-license \
  --product-sku "EXAMPLE-SKU" \
  --checkout-type PROVISIONAL \
  --key-fingerprint "arn:aws:license-manager:us-east-1:123456789012:license:EXAMPLE" \
  --entitlements '[{"Name":"admin-users","Value":"10","Unit":"Count"}]' \
  --client-token "unique-idempotency-token"

# Check in (return) a checked-out license
aws license-manager check-in-license \
  --license-consumption-token <token-from-checkout>

# Get usage for a specific license
aws license-manager get-license-usage \
  --license-arn arn:aws:license-manager::123456789012:license:EXAMPLE

# --- License Type Conversion ---
# Create a license type conversion task (BYOL ↔ License Included)
aws license-manager create-license-conversion-task-for-resource \
  --resource-arn arn:aws:ec2:us-east-1:123456789012:instance/i-xxxxxxxxxx \
  --source-license-context '{"UsageOperation":"RunInstances:0002"}' \
  --destination-license-context '{"UsageOperation":"RunInstances:0800"}'
```

---

## AWS Resource Explorer

```bash
# --- Initial Setup ---
# Enable Resource Explorer in a region (creates a local index)
aws resource-explorer-2 create-index \
  --region us-east-1 \
  --type LOCAL

# Enable Resource Explorer across the entire organization (quick setup)
aws resource-explorer-2 create-resource-explorer-setup \
  --type DELEGATED_ADMINISTRATOR \
  --delegated-admin-account-id 123456789012

# --- Index Management ---
# Get index status for the current region
aws resource-explorer-2 get-index \
  --region us-east-1

# List all indexes across all regions
aws resource-explorer-2 list-indexes \
  --type LOCAL

# Promote a local index to an aggregator index (one per account)
aws resource-explorer-2 update-index-type \
  --arn arn:aws:resource-explorer-2:us-east-1:123456789012:index/INDEX-UUID \
  --type AGGREGATOR

# List indexes from member accounts in the organization
aws resource-explorer-2 list-indexes-for-members \
  --org-states enabled

# --- Views ---
# Create a view that includes tag information in results
aws resource-explorer-2 create-view \
  --view-name AllResources-WithTags \
  --included-properties '[{"Name":"tags"}]'

# Create a filtered view (only EC2 and S3 in us-east-1)
aws resource-explorer-2 create-view \
  --view-name EC2-S3-UsEast1 \
  --filters '{"FilterString":"resourcetype:AWS::EC2::Instance OR resourcetype:AWS::S3::Bucket region:us-east-1"}'

# Set a view as the default for a region
aws resource-explorer-2 associate-default-view \
  --view-arn arn:aws:resource-explorer-2:us-east-1:123456789012:view/AllResources-WithTags/VIEW-UUID

# Get the current default view
aws resource-explorer-2 get-default-view

# List all views in the current region
aws resource-explorer-2 list-views

# --- Search ---
# Search for all resources (uses default view)
aws resource-explorer-2 search \
  --query-string "*"

# Search for EC2 instances with a specific tag
aws resource-explorer-2 search \
  --query-string "resourcetype:AWS::EC2::Instance tag.Env=prod"

# Search for S3 buckets in a specific region
aws resource-explorer-2 search \
  --query-string "resourcetype:AWS::S3::Bucket region:us-east-1"

# Search using a specific view
aws resource-explorer-2 search \
  --query-string "tag.CostCenter=*" \
  --view-arn arn:aws:resource-explorer-2:us-east-1:123456789012:view/AllResources-WithTags/VIEW-UUID

# List supported resource types
aws resource-explorer-2 list-supported-resource-types
```

---

## AWS Well-Architected Tool

```bash
# --- Workloads ---
# Create a workload
aws wellarchitected create-workload \
  --workload-name "ecommerce-platform" \
  --description "Primary e-commerce application" \
  --environment PRODUCTION \
  --review-owner "platform-team@example.com" \
  --lenses wellarchitected serverless \
  --account-ids 123456789012 \
  --aws-regions us-east-1 eu-west-1

# List all workloads
aws wellarchitected list-workloads

# Get workload details (shows risk summary)
aws wellarchitected get-workload \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Update workload metadata
aws wellarchitected update-workload \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --description "Updated description after migration"

# --- Lenses ---
# List available lenses (AWS-provided and custom)
aws wellarchitected list-lenses

# Associate additional lenses with a workload
aws wellarchitected associate-lenses \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-aliases serverless saas

# Import a custom lens (from a JSON definition file)
aws wellarchitected import-lens \
  --json-string file://my-custom-lens.json

# Export a lens definition (to share or version-control)
aws wellarchitected export-lens \
  --lens-alias my-custom-lens \
  --lens-version LATEST

# --- Reviews & Answers ---
# Get the lens review for a workload
aws wellarchitected get-lens-review \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected

# List all answers for a lens review
aws wellarchitected list-answers \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected \
  --pillar-id security

# Get a specific answer (question and current selection)
aws wellarchitected get-answer \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected \
  --question-id sec_securely_operate_multi_accounts

# Update an answer (select best practices that are followed)
aws wellarchitected update-answer \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected \
  --question-id sec_securely_operate_multi_accounts \
  --selected-choices SEC01-BP01 SEC01-BP02 \
  --notes "Using Control Tower with SCPs across all OUs"

# List improvement recommendations (HRIs and MRIs)
aws wellarchitected list-lens-review-improvements \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected \
  --pillar-id reliability

# Generate a lens review report (returns S3 pre-signed URL for PDF)
aws wellarchitected get-lens-review-report \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --lens-alias wellarchitected

# --- Milestones ---
# Create a milestone (snapshot of current review state)
aws wellarchitected create-milestone \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --milestone-name "Pre-launch baseline $(date +%Y-%m-%d)"

# List milestones for a workload
aws wellarchitected list-milestones \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Get a milestone (historical risk summary)
aws wellarchitected get-milestone \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --milestone-number 1

# --- Sharing & Reports ---
# Share a workload with another IAM principal (read-only)
aws wellarchitected create-workload-share \
  --workload-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --shared-with "arn:aws:iam::234567890123:root" \
  --permission-type READONLY

# List pending share invitations
aws wellarchitected list-share-invitations

# Accept a share invitation
aws wellarchitected update-share-invitation \
  --share-invitation-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  --share-invitation-action ACCEPT

# Generate a consolidated report across all workloads (returns S3 URL)
aws wellarchitected get-consolidated-report \
  --format PDF \
  --include-shared-resources
```
