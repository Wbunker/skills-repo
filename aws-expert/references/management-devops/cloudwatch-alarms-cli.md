# AWS CloudWatch Alarms — CLI Reference
For service concepts, see [cloudwatch-alarms-capabilities.md](cloudwatch-alarms-capabilities.md).

```bash
# ============================================================
# CREATING / UPDATING ALARMS
# ============================================================

# Static threshold alarm — M out of N (2/3 prevents false positives from delayed metrics)
aws cloudwatch put-metric-alarm \
  --alarm-name "prod-api-high-error-rate" \
  --alarm-description "5xx rate above 5% for 2 of 3 minutes" \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiName,Value=my-api \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 3 \
  --datapoints-to-alarm 2 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts \
  --ok-actions arn:aws:sns:us-east-1:123456789012:ops-alerts

# High CPU — EC2 recover on system check failure
aws cloudwatch put-metric-alarm \
  --alarm-name "ec2-system-check-fail" \
  --namespace AWS/EC2 \
  --metric-name StatusCheckFailed_System \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data missing \
  --alarm-actions arn:aws:automate:us-east-1:ec2:recover

# EC2 reboot on instance check failure (use 3 periods — different from recover to avoid race condition)
aws cloudwatch put-metric-alarm \
  --alarm-name "ec2-instance-check-fail" \
  --namespace AWS/EC2 \
  --metric-name StatusCheckFailed_Instance \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 3 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:automate:us-east-1:ec2:reboot

# Percentile alarm — p99 Lambda latency
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-p99-latency" \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=my-function \
  --extended-statistic p99 \
  --period 60 \
  --evaluation-periods 5 \
  --datapoints-to-alarm 3 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts

# Metric math alarm — error rate percentage across two metrics
aws cloudwatch put-metric-alarm \
  --alarm-name "api-error-rate-percent" \
  --metrics '[
    {
      "Id": "errors",
      "MetricStat": {
        "Metric": {"Namespace": "AWS/ApiGateway", "MetricName": "5XXError",
                   "Dimensions": [{"Name": "ApiName", "Value": "my-api"}]},
        "Period": 60, "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "requests",
      "MetricStat": {
        "Metric": {"Namespace": "AWS/ApiGateway", "MetricName": "Count",
                   "Dimensions": [{"Name": "ApiName", "Value": "my-api"}]},
        "Period": 60, "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "error_rate",
      "Expression": "(errors / requests) * 100",
      "ReturnData": true
    }
  ]' \
  --comparison-operator GreaterThanThreshold \
  --threshold 5 \
  --evaluation-periods 3 \
  --datapoints-to-alarm 2 \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts

# ============================================================
# ANOMALY DETECTION ALARMS
# ============================================================

# Step 1: Create the anomaly detection model
aws cloudwatch put-anomaly-detector \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=my-function \
  --stat Sum

# Step 2: Create alarm using the model (band width = 2 standard deviations)
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-invocations-anomaly" \
  --metrics '[
    {
      "Id": "m1",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/Lambda",
          "MetricName": "Invocations",
          "Dimensions": [{"Name": "FunctionName", "Value": "my-function"}]
        },
        "Period": 300,
        "Stat": "Sum"
      },
      "ReturnData": true
    },
    {
      "Id": "ad1",
      "Expression": "ANOMALY_DETECTION_BAND(m1, 2)",
      "ReturnData": false
    }
  ]' \
  --comparison-operator GreaterThanUpperThreshold \
  --threshold-metric-id ad1 \
  --evaluation-periods 2 \
  --treat-missing-data missing

# List anomaly detection models
aws cloudwatch describe-anomaly-detectors \
  --namespace AWS/Lambda \
  --metric-name Invocations

# Delete an anomaly detection model
aws cloudwatch delete-anomaly-detector \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=my-function \
  --stat Sum

# ============================================================
# COMPOSITE ALARMS
# ============================================================

# Composite alarm — AND logic to reduce noise
aws cloudwatch put-composite-alarm \
  --alarm-name "prod-service-degraded" \
  --alarm-description "Alerts only when both error rate and latency are elevated" \
  --alarm-rule 'ALARM("api-high-error-rate") AND ALARM("api-high-latency")' \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts \
  --ok-actions arn:aws:sns:us-east-1:123456789012:ops-alerts

# Composite with suppressor — suppress during deployments
aws cloudwatch put-composite-alarm \
  --alarm-name "prod-service-degraded-with-suppressor" \
  --alarm-rule 'ALARM("api-high-error-rate") AND ALARM("api-high-latency")' \
  --actions-suppressor "deployment-in-progress" \
  --actions-suppressor-wait-period 60 \
  --actions-suppressor-extension-period 60 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:ops-alerts

# Composite — AT_LEAST for AZ-level failure detection
aws cloudwatch put-composite-alarm \
  --alarm-name "multi-az-failure" \
  --alarm-rule 'AT_LEAST(2, ALARM, ("az1-errors", "az2-errors", "az3-errors"))' \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:critical-alerts

# Multi-window SLO burn rate composite alarm (Google SRE pattern)
aws cloudwatch put-composite-alarm \
  --alarm-name "slo-fast-burn-rate" \
  --alarm-description "2% budget consumed in 1h AND 5-min window confirms trend" \
  --alarm-rule 'ALARM("slo-1hour-burn-rate") AND ALARM("slo-5min-burn-rate")' \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:pagerduty-critical

# ============================================================
# DESCRIBING AND QUERYING ALARMS
# ============================================================

# List all alarms
aws cloudwatch describe-alarms

# Filter by state
aws cloudwatch describe-alarms --state-value ALARM
aws cloudwatch describe-alarms --state-value INSUFFICIENT_DATA  # find orphaned/broken alarms

# Filter by name prefix
aws cloudwatch describe-alarms --alarm-name-prefix "prod-"

# Filter by type
aws cloudwatch describe-alarms --alarm-types MetricAlarm
aws cloudwatch describe-alarms --alarm-types CompositeAlarm

# Get alarms for a specific metric
aws cloudwatch describe-alarms-for-metric \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0

# Get alarm history (last 30 days)
aws cloudwatch describe-alarm-history \
  --alarm-name "prod-api-high-error-rate" \
  --history-item-type StateUpdate

# All history types: StateUpdate | Action | ConfigurationUpdate
aws cloudwatch describe-alarm-history \
  --alarm-name "prod-api-high-error-rate" \
  --start-date 2024-01-01T00:00:00Z \
  --end-date 2024-01-31T23:59:59Z

# ============================================================
# ALARM STATE MANAGEMENT
# ============================================================

# Force alarm into ALARM state for testing
aws cloudwatch set-alarm-state \
  --alarm-name "prod-api-high-error-rate" \
  --state-value ALARM \
  --state-reason "Testing alarm action delivery"

# Force back to OK
aws cloudwatch set-alarm-state \
  --alarm-name "prod-api-high-error-rate" \
  --state-value OK \
  --state-reason "Test complete"

# Disable all actions on an alarm (permanent until re-enabled)
aws cloudwatch disable-alarm-actions \
  --alarm-names "prod-api-high-error-rate" "prod-api-high-latency"

# Re-enable actions
aws cloudwatch enable-alarm-actions \
  --alarm-names "prod-api-high-error-rate" "prod-api-high-latency"

# ============================================================
# DELETING ALARMS
# ============================================================

# Delete up to 100 alarms at once
aws cloudwatch delete-alarms \
  --alarm-names "old-alarm-1" "old-alarm-2"

# Find and delete all INSUFFICIENT_DATA alarms (orphaned alarm cleanup)
aws cloudwatch describe-alarms \
  --state-value INSUFFICIENT_DATA \
  --query 'MetricAlarms[].AlarmName' \
  --output text | tr '\t' '\n' | \
  xargs -P 5 -I{} aws cloudwatch delete-alarms --alarm-names {}

# ============================================================
# TAGS
# ============================================================

# Add tags (works on existing alarms; Tags in PutMetricAlarm only applies on creation)
aws cloudwatch tag-resource \
  --resource-arn arn:aws:cloudwatch:us-east-1:123456789012:alarm:prod-api-high-error-rate \
  --tags Key=Environment,Value=prod Key=Team,Value=platform Key=CostCenter,Value=123

# List tags
aws cloudwatch list-tags-for-resource \
  --resource-arn arn:aws:cloudwatch:us-east-1:123456789012:alarm:prod-api-high-error-rate

# Remove tags
aws cloudwatch untag-resource \
  --resource-arn arn:aws:cloudwatch:us-east-1:123456789012:alarm:prod-api-high-error-rate \
  --tag-keys Environment Team

# ============================================================
# ALARM MUTE RULES
# ============================================================

# Create a one-time mute rule (scheduled maintenance window)
aws cloudwatch put-alarm-mute-rule \
  --rule-name "planned-maintenance-2024-01-15" \
  --rule-description "Nightly maintenance window" \
  --schedule "at(2024-01-15T02:00)" \
  --duration "PT2H" \
  --timezone "America/Chicago" \
  --alarm-names "prod-api-high-error-rate" "prod-api-high-latency" "prod-db-connections"

# Create a recurring mute rule (weekly maintenance window, cron)
aws cloudwatch put-alarm-mute-rule \
  --rule-name "weekly-maintenance-window" \
  --schedule "cron(0 2 ? * SUN *)" \
  --duration "PT4H" \
  --timezone "America/New_York" \
  --alarm-names "prod-api-high-error-rate"

# ============================================================
# BULK OPERATIONS AND PATTERNS
# ============================================================

# Create a standard set of Lambda alarms for a function
FUNCTION_NAME="my-function"
SNS_ARN="arn:aws:sns:us-east-1:123456789012:ops-alerts"

aws cloudwatch put-metric-alarm \
  --alarm-name "${FUNCTION_NAME}-errors" \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=${FUNCTION_NAME} \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 3 \
  --datapoints-to-alarm 2 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions ${SNS_ARN}

aws cloudwatch put-metric-alarm \
  --alarm-name "${FUNCTION_NAME}-throttles" \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=${FUNCTION_NAME} \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 5 \
  --datapoints-to-alarm 3 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions ${SNS_ARN}

aws cloudwatch put-metric-alarm \
  --alarm-name "${FUNCTION_NAME}-duration-p99" \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=${FUNCTION_NAME} \
  --extended-statistic p99 \
  --period 300 \
  --evaluation-periods 3 \
  --datapoints-to-alarm 2 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions ${SNS_ARN}

# Roll up Lambda alarms into a composite
aws cloudwatch put-composite-alarm \
  --alarm-name "${FUNCTION_NAME}-health" \
  --alarm-rule "ALARM(\"${FUNCTION_NAME}-errors\") OR ALARM(\"${FUNCTION_NAME}-throttles\") OR ALARM(\"${FUNCTION_NAME}-duration-p99\")" \
  --alarm-actions ${SNS_ARN}

# Export all alarm configurations to JSON (for audit/backup)
aws cloudwatch describe-alarms \
  --output json \
  --query 'MetricAlarms[*].{Name:AlarmName,State:StateValue,Threshold:Threshold,Period:Period}' \
  > alarm-inventory.json

# Count alarms by state
aws cloudwatch describe-alarms \
  --query 'MetricAlarms[*].StateValue' \
  --output text | tr '\t' '\n' | sort | uniq -c

# Find alarms without any actions configured
aws cloudwatch describe-alarms \
  --query 'MetricAlarms[?length(AlarmActions)==`0`].AlarmName' \
  --output text
```
