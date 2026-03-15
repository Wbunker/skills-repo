# AWS Cost Explorer & Budgets — CLI Reference
For service concepts, see [cost-explorer-budgets-capabilities.md](cost-explorer-budgets-capabilities.md).

## Cost Explorer (aws ce)

The Cost Explorer API endpoint is always `https://ce.us-east-1.amazonaws.com` regardless of the region your resources run in.

```bash
# --- Cost and Usage ---

# Monthly costs by service for the last month
aws ce get-cost-and-usage \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY \
  --metrics BlendedCost UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Daily costs grouped by service and Environment tag
aws ce get-cost-and-usage \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE Type=TAG,Key=Environment

# Costs filtered to EC2 only, grouped by linked account
aws ce get-cost-and-usage \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon EC2"]}}' \
  --group-by Type=DIMENSION,Key=LINKED_ACCOUNT

# Costs with resource-level detail (requires hourly granularity enabled)
aws ce get-cost-and-usage-with-resources \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon EC2"]}}'

# --- Forecasting ---

# Forecast total spend for the next 3 months
aws ce get-cost-forecast \
  --time-period Start=2025-03-01,End=2025-06-01 \
  --granularity MONTHLY \
  --metric UNBLENDED_COST

# Forecast usage for EC2 instance hours
aws ce get-usage-forecast \
  --time-period Start=2025-03-01,End=2025-06-01 \
  --granularity MONTHLY \
  --metric USAGE_QUANTITY \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon EC2"]}}'

# --- Dimensions and Tags ---

# List all services that have cost data
aws ce get-dimension-values \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --dimension SERVICE

# List all linked accounts in cost data
aws ce get-dimension-values \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --dimension LINKED_ACCOUNT

# List all distinct values for the Environment tag
aws ce get-tags \
  --time-period Start=2025-02-01,End=2025-03-01 \
  --tag-key Environment

# Get values for all cost categories
aws ce get-cost-categories \
  --time-period Start=2025-02-01,End=2025-03-01

# --- Right-Sizing ---

# Get EC2 right-sizing recommendations
aws ce get-rightsizing-recommendation \
  --service "Amazon EC2" \
  --configuration '{"RecommendationTarget":"SAME_INSTANCE_FAMILY","BenefitsConsidered":true}'

# --- Anomaly Detection ---

# Create a monitor for all AWS services
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "AllServicesMonitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'

# Create a monitor for all linked accounts (management account only)
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "AllAccountsMonitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "MEMBER_ACCOUNT"
  }'

# Create an alert subscription for individual alerts via SNS
aws ce create-anomaly-subscription \
  --anomaly-subscription '{
    "SubscriptionName": "ImmediateAlerts",
    "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/abcd1234"],
    "Subscribers": [
      {
        "Address": "arn:aws:sns:us-east-1:123456789012:cost-alerts",
        "Type": "SNS"
      }
    ],
    "Threshold": 100,
    "Frequency": "IMMEDIATE"
  }'

# Create a daily summary alert via email
aws ce create-anomaly-subscription \
  --anomaly-subscription '{
    "SubscriptionName": "DailySummary",
    "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/abcd1234"],
    "Subscribers": [
      {
        "Address": "finops-team@example.com",
        "Type": "EMAIL"
      }
    ],
    "Threshold": 50,
    "Frequency": "DAILY"
  }'

# Get detected anomalies for the last 30 days
aws ce get-anomalies \
  --monitor-arn arn:aws:ce::123456789012:anomalymonitor/abcd1234 \
  --date-interval Start=2025-02-01,End=2025-03-01

# List all anomaly monitors
aws ce get-anomaly-monitors

# List all anomaly subscriptions
aws ce get-anomaly-subscriptions

# --- Cost Categories ---

# Create a cost category to group workloads
aws ce create-cost-category-definition \
  --name "Environment" \
  --rule-version "CostCategoryExpression.v1" \
  --rules '[
    {
      "Value": "Production",
      "Rule": {"Tags": {"Key": "Environment", "Values": ["prod", "production"]}}
    },
    {
      "Value": "Development",
      "Rule": {"Tags": {"Key": "Environment", "Values": ["dev", "development", "staging"]}}
    }
  ]'

# List all cost category definitions
aws ce list-cost-category-definitions

# Describe a specific cost category
aws ce describe-cost-category-definition \
  --cost-category-arn arn:aws:ce::123456789012:costcategory/abcd1234
```

---

## AWS Budgets (aws budgets)

```bash
# --- Create Budgets ---

# Create a monthly cost budget with 80% actual and 100% forecasted alerts
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "MonthlyEC2Budget",
    "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {
      "Service": ["Amazon EC2"]
    },
    "CostTypes": {
      "IncludeTax": true,
      "IncludeSubscription": true,
      "UseBlended": false
    }
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@example.com"},
        {"SubscriptionType": "SNS", "Address": "arn:aws:sns:us-east-1:123456789012:billing-alerts"}
      ]
    },
    {
      "Notification": {
        "NotificationType": "FORECASTED",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 100,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@example.com"}
      ]
    }
  ]'

# Create a Savings Plans coverage budget (alert when coverage drops below 70%)
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "SPCoverageBudget",
    "BudgetLimit": {"Amount": "70", "Unit": "PERCENTAGE"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "SAVINGS_PLANS_COVERAGE"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "LESS_THAN",
        "Threshold": 70,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@example.com"}
      ]
    }
  ]'

# Create an RI utilization budget (alert when utilization drops below 80%)
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "RIUtilizationBudget",
    "BudgetLimit": {"Amount": "80", "Unit": "PERCENTAGE"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "RI_UTILIZATION"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "LESS_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {"SubscriptionType": "EMAIL", "Address": "finops@example.com"}
      ]
    }
  ]'

# --- Manage Budgets ---

# List all budgets for an account
aws budgets describe-budgets --account-id 123456789012

# Get details for a specific budget
aws budgets describe-budget \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget

# Update a budget limit
aws budgets update-budget \
  --account-id 123456789012 \
  --new-budget '{
    "BudgetName": "MonthlyEC2Budget",
    "BudgetLimit": {"Amount": "1500", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'

# View performance history for a budget
aws budgets describe-budget-performance-history \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget

# Delete a budget
aws budgets delete-budget \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget

# --- Budget Actions ---

# Create a budget action that stops EC2 instances when 100% threshold is hit
aws budgets create-budget-action \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget \
  --notification-type ACTUAL \
  --action-type STOP_EC2_INSTANCES \
  --action-threshold '{"ActionThresholdValue": 100, "ActionThresholdType": "PERCENTAGE"}' \
  --definition '{
    "IamActionDefinition": {
      "PolicyArn": "arn:aws:iam::123456789012:policy/BudgetDenyProvisioningPolicy",
      "Roles": ["arn:aws:iam::123456789012:role/DeveloperRole"]
    }
  }' \
  --execution-role-arn arn:aws:iam::123456789012:role/BudgetActionsRole \
  --approval-model AUTOMATIC \
  --subscribers '[{"SubscriptionType": "EMAIL", "Address": "finops@example.com"}]'

# List budget actions for a budget
aws budgets describe-budget-actions-for-budget \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget

# List all budget actions for the account
aws budgets describe-budget-actions-for-account \
  --account-id 123456789012

# Manually execute a budget action
aws budgets execute-budget-action \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget \
  --action-id abcd1234-5678-90ab-cdef-EXAMPLE \
  --execution-type APPROVE_BUDGET_ACTION

# View budget action execution history
aws budgets describe-budget-action-histories \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget \
  --action-id abcd1234-5678-90ab-cdef-EXAMPLE

# --- Notifications and Subscribers ---

# List notifications for a budget
aws budgets describe-notifications-for-budget \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget

# List subscribers for a notification
aws budgets describe-subscribers-for-notification \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget \
  --notification '{"NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN", "Threshold": 80}'

# Add a new subscriber to an existing notification
aws budgets create-subscriber \
  --account-id 123456789012 \
  --budget-name MonthlyEC2Budget \
  --notification '{"NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN", "Threshold": 80}' \
  --subscriber '{"SubscriptionType": "EMAIL", "Address": "manager@example.com"}'
```
