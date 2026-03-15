# AWS CUR & Billing — CLI Reference
For service concepts, see [cur-billing-capabilities.md](cur-billing-capabilities.md).

## Cost and Usage Reports (aws cur)

Note: `aws cur` commands must be run against `us-east-1` as CUR is a global service.

```bash
# --- Create a CUR Report ---

# Create a CUR report with hourly granularity delivered to S3
aws cur put-report-definition \
  --region us-east-1 \
  --report-definition '{
    "ReportName": "MyCostReport",
    "TimeUnit": "HOURLY",
    "Format": "textORcsv",
    "Compression": "GZIP",
    "AdditionalSchemaElements": ["RESOURCES"],
    "S3Bucket": "my-cur-bucket",
    "S3Prefix": "cur/",
    "S3Region": "us-east-1",
    "AdditionalArtifacts": ["ATHENA"],
    "RefreshClosedReports": true,
    "ReportVersioning": "CREATE_NEW_REPORT"
  }'

# Create a CUR 2.0 (Data Exports) report with Parquet format for Athena
aws cur put-report-definition \
  --region us-east-1 \
  --report-definition '{
    "ReportName": "MyCostReportParquet",
    "TimeUnit": "DAILY",
    "Format": "Parquet",
    "Compression": "Parquet",
    "AdditionalSchemaElements": ["RESOURCES", "SPLIT_COST_ALLOCATION_DATA"],
    "S3Bucket": "my-cur-bucket",
    "S3Prefix": "cur-parquet/",
    "S3Region": "us-east-1",
    "AdditionalArtifacts": ["ATHENA"],
    "RefreshClosedReports": true,
    "ReportVersioning": "CREATE_NEW_REPORT"
  }'

# --- Manage Reports ---

# List all CUR report definitions
aws cur describe-report-definitions \
  --region us-east-1

# Modify an existing CUR report
aws cur modify-report-definition \
  --region us-east-1 \
  --report-name MyCostReport \
  --report-definition '{
    "ReportName": "MyCostReport",
    "TimeUnit": "HOURLY",
    "Format": "textORcsv",
    "Compression": "GZIP",
    "AdditionalSchemaElements": ["RESOURCES"],
    "S3Bucket": "my-cur-bucket-new",
    "S3Prefix": "cur/",
    "S3Region": "us-east-1",
    "RefreshClosedReports": true,
    "ReportVersioning": "CREATE_NEW_REPORT"
  }'

# Delete a CUR report definition
aws cur delete-report-definition \
  --region us-east-1 \
  --report-name MyCostReport

# --- Tagging CUR Resources ---

aws cur tag-resource \
  --resource-arn arn:aws:cur:us-east-1:123456789012:definition/MyCostReport \
  --tags-map Environment=prod,Owner=finops

aws cur list-tags-for-resource \
  --resource-arn arn:aws:cur:us-east-1:123456789012:definition/MyCostReport
```

---

## Billing Conductor (aws billingconductor)

```bash
# --- Billing Groups ---

# Create a billing group for a team/customer
aws billingconductor create-billing-group \
  --name "TeamA" \
  --primary-account-id 123456789012 \
  --computation-preference '{"PricingPlanArn": "arn:aws:billingconductor::123456789012:pricingplan/abcd1234"}' \
  --account-grouping '{"LinkedAccountIds": ["111111111111", "222222222222"]}'

# List all billing groups
aws billingconductor list-billing-groups

# Get cost report for a billing group
aws billingconductor get-billing-group-cost-report \
  --arn arn:aws:billingconductor::123456789012:billinggroup/abcd1234 \
  --billing-period-range Start=2025-02-01,End=2025-03-01

# List all billing group cost reports
aws billingconductor list-billing-group-cost-reports

# Associate additional accounts with a billing group
aws billingconductor associate-accounts \
  --arn arn:aws:billingconductor::123456789012:billinggroup/abcd1234 \
  --account-ids 333333333333 444444444444

# Disassociate accounts from a billing group
aws billingconductor disassociate-accounts \
  --arn arn:aws:billingconductor::123456789012:billinggroup/abcd1234 \
  --account-ids 333333333333

# --- Pricing Plans ---

# Create a pricing plan
aws billingconductor create-pricing-plan \
  --name "CustomerAPricingPlan" \
  --pricing-rule-arns "arn:aws:billingconductor::123456789012:pricingrule/rule1"

# List all pricing plans
aws billingconductor list-pricing-plans

# --- Pricing Rules ---

# Create a markup pricing rule (+15% over On-Demand for EC2)
aws billingconductor create-pricing-rule \
  --name "EC2Markup15Pct" \
  --scope SERVICE \
  --service AmazonEC2 \
  --type MARKUP \
  --modifier-percentage 15

# Create a markdown pricing rule (pass EDP discount to customer)
aws billingconductor create-pricing-rule \
  --name "GlobalDiscount10Pct" \
  --scope GLOBAL \
  --type DISCOUNT \
  --modifier-percentage 10

# List all pricing rules
aws billingconductor list-pricing-rules

# Associate pricing rules with a plan
aws billingconductor associate-pricing-rules \
  --arn arn:aws:billingconductor::123456789012:pricingplan/abcd1234 \
  --pricing-rule-arns \
    arn:aws:billingconductor::123456789012:pricingrule/rule1 \
    arn:aws:billingconductor::123456789012:pricingrule/rule2

# --- Custom Line Items ---

# Create a flat monthly fee custom line item (e.g., support charge)
aws billingconductor create-custom-line-item \
  --name "ManagedSupportFee" \
  --billing-group-arn arn:aws:billingconductor::123456789012:billinggroup/abcd1234 \
  --custom-line-item-charge-details '{
    "Flat": {"ChargeValue": 500},
    "Type": "FEE"
  }' \
  --billing-period-range '{"InclusiveStartBillingPeriod": "2025-01", "ExclusiveEndBillingPeriod": "2025-12"}'

# List all custom line items
aws billingconductor list-custom-line-items

# --- Account Associations ---

# List all account associations across billing groups
aws billingconductor list-account-associations
```

---

## Pricing API (aws pricing)

Note: The Pricing API endpoint is `https://api.pricing.us-east-1.amazonaws.com`. Always query from `us-east-1` or `ap-south-1`.

```bash
# --- Service Discovery ---

# List all AWS service codes
aws pricing describe-services \
  --region us-east-1

# Get attribute names for EC2
aws pricing describe-services \
  --service-code AmazonEC2 \
  --region us-east-1

# --- Attribute Values ---

# Get all valid values for the 'instanceType' attribute in EC2
aws pricing get-attribute-values \
  --service-code AmazonEC2 \
  --attribute-name instanceType \
  --region us-east-1

# Get all valid values for 'location' (region names)
aws pricing get-attribute-values \
  --service-code AmazonEC2 \
  --attribute-name location \
  --region us-east-1

# --- Product Price Lookup ---

# Get On-Demand pricing for m5.large Linux in us-east-1
aws pricing get-products \
  --service-code AmazonEC2 \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=instanceType,Value=m5.large" \
    "Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)" \
    "Type=TERM_MATCH,Field=operatingSystem,Value=Linux" \
    "Type=TERM_MATCH,Field=preInstalledSw,Value=NA" \
    "Type=TERM_MATCH,Field=tenancy,Value=Shared" \
    "Type=TERM_MATCH,Field=capacitystatus,Value=Used"

# Get pricing for RDS db.r6g.large MySQL
aws pricing get-products \
  --service-code AmazonRDS \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=instanceType,Value=db.r6g.large" \
    "Type=TERM_MATCH,Field=databaseEngine,Value=MySQL" \
    "Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)"

# Get S3 storage pricing
aws pricing get-products \
  --service-code AmazonS3 \
  --region us-east-1 \
  --filters \
    "Type=TERM_MATCH,Field=storageClass,Value=General Purpose" \
    "Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)"

# --- Price List Files ---

# List available price list files for EC2
aws pricing list-price-lists \
  --service-code AmazonEC2 \
  --effective-date 2025-01-01T00:00:00Z \
  --region us-east-1 \
  --currency-code USD

# Get download URL for a price list file
aws pricing get-price-list-file-url \
  --price-list-arn arn:aws:pricing:::price-list/AmazonEC2 \
  --file-format json
```

---

## Cost Allocation Tags via Cost Explorer (aws ce)

```bash
# List all cost allocation tags and their status
aws ce list-cost-allocation-tags

# Activate tags for cost allocation
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
    TagKey=Environment,Status=Active \
    TagKey=CostCenter,Status=Active \
    TagKey=Owner,Status=Active

# Backfill cost allocation tags (apply retroactively)
aws ce start-cost-allocation-tag-backfill \
  --backfill-from 2024-01-01T00:00:00Z
```
