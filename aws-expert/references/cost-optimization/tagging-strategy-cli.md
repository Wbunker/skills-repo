# AWS Tagging Strategy — CLI Reference

For service concepts, see [tagging-strategy-capabilities.md](tagging-strategy-capabilities.md).

## Resource Tagging (aws resourcegroupstaggingapi)

```bash
# --- Find Resources by Tag ---

# Find all resources tagged Environment=prod
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=prod

# Find all EC2 instances and S3 buckets tagged with CostCenter=CC-1234
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=CostCenter,Values=CC-1234 \
  --resource-type-filters ec2:instance s3:bucket

# Find all resources missing the Environment tag
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=  # empty value means tag is missing or empty

# Get all resources across all types (paginated)
aws resourcegroupstaggingapi get-resources \
  --resources-per-page 100

# --- Bulk Tagging ---

# Apply tags to multiple resources at once
aws resourcegroupstaggingapi tag-resources \
  --resource-arn-list \
    arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0 \
    arn:aws:s3:::my-bucket \
  --tags Environment=prod,CostCenter=CC-1234,Owner=platform-team

# Remove tags from multiple resources
aws resourcegroupstaggingapi untag-resources \
  --resource-arn-list \
    arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0 \
  --tag-keys OldTag UnusedTag

# --- Tag Discovery ---

# List all tag keys used in the account
aws resourcegroupstaggingapi get-tag-keys

# List all values used for a specific tag key
aws resourcegroupstaggingapi get-tag-values \
  --key Environment

# --- Tag Compliance Report ---

# Generate a tag compliance report (evaluates against tag policies)
aws resourcegroupstaggingapi start-report-creation \
  --s3-bucket my-compliance-reports-bucket

# Check the status of the compliance report generation
aws resourcegroupstaggingapi describe-report-creation
```

---

## Cost Allocation Tags (aws ce)

```bash
# List all cost allocation tags and their status
aws ce list-cost-allocation-tags

# Activate tags for cost allocation
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
    TagKey=Environment,Status=Active \
    TagKey=CostCenter,Status=Active \
    TagKey=Owner,Status=Active

# Backfill cost allocation tags (apply retroactively to past CUR data)
aws ce start-cost-allocation-tag-backfill \
  --backfill-from 2024-01-01T00:00:00Z
```
