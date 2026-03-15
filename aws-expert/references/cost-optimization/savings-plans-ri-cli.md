# AWS Savings Plans & Reserved Instances — CLI Reference
For service concepts, see [savings-plans-ri-capabilities.md](savings-plans-ri-capabilities.md).

## Savings Plans (aws savingsplans)

```bash
# --- View Existing Savings Plans ---

# List all active Savings Plans
aws savingsplans describe-savings-plans

# Filter to Compute Savings Plans only
aws savingsplans describe-savings-plans \
  --filters '[{"name": "savingsPlanType", "values": ["Compute"]}]'

# Filter by state (ACTIVE, QUEUED, RETIRED)
aws savingsplans describe-savings-plans \
  --filters '[{"name": "state", "values": ["ACTIVE"]}]'

# --- Browse Available Offerings ---

# List available Savings Plans offerings (types, terms, payment options)
aws savingsplans describe-savings-plans-offerings \
  --product-type EC2 \
  --plan-types EC2_INSTANCE_SP \
  --durations 31536000    # 1-year in seconds

# Get offering rates for Compute Savings Plans
aws savingsplans describe-savings-plans-offering-rates \
  --savings-plan-offer-ids <offering-id> \
  --products EC2 \
  --service-codes AmazonEC2

# --- Purchase and Manage ---

# Queue a Savings Plan for future purchase (starts at renewal date)
aws savingsplans create-savings-plan \
  --savings-plan-offering-id <offering-id> \
  --commitment 0.10 \
  --purchase-time "2025-04-01T00:00:00Z"

# Create a Savings Plan immediately
aws savingsplans create-savings-plan \
  --savings-plan-offering-id <offering-id> \
  --commitment 0.50    # $0.50/hour commitment

# Delete a queued (not-yet-started) Savings Plan
aws savingsplans delete-queued-savings-plan \
  --savings-plan-id sp-abcd1234

# Return an eligible Savings Plan (within 7 days of purchase, if return is available)
aws savingsplans return-savings-plan \
  --savings-plan-id sp-abcd1234

# --- View Rates for an Existing Plan ---

# View the effective rates being applied by an active Savings Plan
aws savingsplans describe-savings-plan-rates \
  --savings-plan-id sp-abcd1234

# --- Tagging ---

# Tag a Savings Plan
aws savingsplans tag-resource \
  --resource-arn arn:aws:savingsplans::123456789012:savingsplan/sp-abcd1234 \
  --tags Environment=prod,Owner=finops-team

# List tags on a Savings Plan
aws savingsplans list-tags-for-resource \
  --resource-arn arn:aws:savingsplans::123456789012:savingsplan/sp-abcd1234

# Remove tags from a Savings Plan
aws savingsplans untag-resource \
  --resource-arn arn:aws:savingsplans::123456789012:savingsplan/sp-abcd1234 \
  --tag-keys Owner
```

---

## EC2 Reserved Instances (aws ec2)

```bash
# --- Reserved Instances ---

# View all your Reserved Instances
aws ec2 describe-reserved-instances

# View active/available RIs only
aws ec2 describe-reserved-instances \
  --filters Name=state,Values=active

# Browse available RI offerings for a specific instance type
aws ec2 describe-reserved-instances-offerings \
  --instance-type m5.large \
  --instance-tenancy default \
  --product-description "Linux/UNIX (Amazon VPC)" \
  --offering-class standard \
  --offering-type "No Upfront"

# Browse Convertible RI offerings
aws ec2 describe-reserved-instances-offerings \
  --instance-type m5.large \
  --instance-tenancy default \
  --product-description "Linux/UNIX (Amazon VPC)" \
  --offering-class convertible

# Purchase a Reserved Instance
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id abcd1234-5678-90ab-cdef-EXAMPLE \
  --instance-count 2

# Modify an existing RI (change AZ or instance size within same family)
aws ec2 modify-reserved-instances \
  --reserved-instances-ids abcd1234-5678-90ab-cdef-EXAMPLE \
  --target-configurations '[
    {
      "AvailabilityZone": "us-east-1b",
      "InstanceCount": 1,
      "InstanceType": "m5.large",
      "Platform": "Linux/UNIX (Amazon VPC)"
    }
  ]'

# Check modification status
aws ec2 describe-reserved-instances-modifications \
  --reserved-instances-modification-ids rimod-abcd1234

# --- RI Marketplace ---

# List your RIs that are listed for sale on the Marketplace
aws ec2 describe-reserved-instances-listings
```

---

## Savings Plans coverage/utilization via Cost Explorer (aws ce)

```bash
# Savings Plans coverage report
aws ce get-savings-plans-coverage \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY

# Savings Plans utilization (are we consuming the full commitment?)
aws ce get-savings-plans-utilization \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY

# Detailed utilization by Savings Plan ARN
aws ce get-savings-plans-utilization-details \
  --time-period Start=2025-02-01,End=2025-03-01

# Savings Plans purchase recommendation
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days THIRTY_DAYS

# Generate fresh Savings Plans recommendations (async)
aws ce start-savings-plans-purchase-recommendation-generation
aws ce list-savings-plans-purchase-recommendation-generation

# RI utilization report (are we using our RIs efficiently?)
aws ce get-reservation-utilization \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY

# RI coverage report (what % of eligible hours are covered by RIs?)
aws ce get-reservation-coverage \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY \
  --group-by Type=DIMENSION,Key=SERVICE

# Get RI purchase recommendations
aws ce get-reservation-purchase-recommendation \
  --service "Amazon EC2" \
  --lookback-period-in-days SIXTY_DAYS \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT
```
