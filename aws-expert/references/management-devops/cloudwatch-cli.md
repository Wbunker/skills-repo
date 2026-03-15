# AWS CloudWatch — CLI Reference
For service concepts, see [cloudwatch-capabilities.md](cloudwatch-capabilities.md).

```bash
# --- Metrics ---
# Publish a custom metric
aws cloudwatch put-metric-data \
  --namespace MyApp/Latency \
  --metric-data '[
    {
      "MetricName": "RequestLatency",
      "Dimensions": [{"Name": "Environment", "Value": "prod"}],
      "Value": 250.0,
      "Unit": "Milliseconds"
    }
  ]'

# Get metric statistics (historical aggregated data)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Average Maximum

# Get metric data (flexible, supports math expressions, multiple metrics)
aws cloudwatch get-metric-data \
  --metric-data-queries '[
    {
      "Id": "m1",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/Lambda",
          "MetricName": "Errors",
          "Dimensions": [{"Name": "FunctionName", "Value": "my-function"}]
        },
        "Period": 300,
        "Stat": "Sum"
      }
    }
  ]' \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z

# List available metrics
aws cloudwatch list-metrics --namespace AWS/Lambda
aws cloudwatch list-metrics --namespace AWS/EC2 --metric-name CPUUtilization
aws cloudwatch list-metrics --namespace AWS/EC2 \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0

# --- Alarms ---
# Create a metric alarm (static threshold)
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "CPU above 80%" \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 80 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:my-alarm-topic \
  --ok-actions arn:aws:sns:us-east-1:123456789012:my-alarm-topic

# Create an anomaly detection alarm
aws cloudwatch put-anomaly-detector \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=my-function \
  --stat Sum

aws cloudwatch put-metric-alarm \
  --alarm-name lambda-anomaly \
  --metrics '[
    {
      "Id": "m1",
      "MetricStat": {
        "Metric": {"Namespace": "AWS/Lambda", "MetricName": "Invocations",
          "Dimensions": [{"Name": "FunctionName", "Value": "my-function"}]},
        "Period": 300, "Stat": "Sum"
      }
    },
    {
      "Id": "ad1",
      "Expression": "ANOMALY_DETECTION_BAND(m1, 2)"
    }
  ]' \
  --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
  --threshold-metric-id ad1 \
  --evaluation-periods 2 \
  --treat-missing-data notBreaching

# Create a composite alarm
aws cloudwatch put-composite-alarm \
  --alarm-name composite-app-health \
  --alarm-description "App unhealthy if CPU high AND error rate high" \
  --alarm-rule "ALARM(high-cpu) AND ALARM(high-errors)" \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:pagerduty-topic

# Describe alarms
aws cloudwatch describe-alarms
aws cloudwatch describe-alarms --alarm-names high-cpu composite-app-health
aws cloudwatch describe-alarms --state-value ALARM
aws cloudwatch describe-alarms --alarm-types MetricAlarm CompositeAlarm

# Describe alarms for a specific metric
aws cloudwatch describe-alarms-for-metric \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0

# Manually set alarm state (useful for testing actions)
aws cloudwatch set-alarm-state \
  --alarm-name high-cpu \
  --state-value ALARM \
  --state-reason "Manual test"

# Delete alarms
aws cloudwatch delete-alarms --alarm-names high-cpu high-errors

# Disable/enable alarm actions (silence without deleting)
aws cloudwatch disable-alarm-actions --alarm-names high-cpu
aws cloudwatch enable-alarm-actions --alarm-names high-cpu

# --- Dashboards ---
# Create or update a dashboard
aws cloudwatch put-dashboard \
  --dashboard-name MyAppDashboard \
  --dashboard-body file://dashboard.json

# Get dashboard definition
aws cloudwatch get-dashboard --dashboard-name MyAppDashboard

# List dashboards
aws cloudwatch list-dashboards
aws cloudwatch list-dashboards --dashboard-name-prefix MyApp

# Delete dashboards
aws cloudwatch delete-dashboards --dashboard-names MyAppDashboard OldDashboard

# --- Anomaly Detectors ---
aws cloudwatch describe-anomaly-detectors \
  --namespace AWS/Lambda \
  --metric-name Errors

aws cloudwatch delete-anomaly-detector \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --stat Sum \
  --dimensions Name=FunctionName,Value=my-function

# --- Contributor Insights ---
aws cloudwatch put-insight-rule \
  --rule-name TopErrorIPs \
  --rule-state ENABLED \
  --rule-definition file://contributor-insight-rule.json

aws cloudwatch get-insight-rule-report \
  --rule-name TopErrorIPs \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 3600 \
  --max-contributor-count 10

aws cloudwatch describe-insight-rules

# --- Metric Streams ---
# Stream metrics to Kinesis Firehose in real time
aws cloudwatch put-metric-stream \
  --name my-metric-stream \
  --firehose-arn arn:aws:firehose:us-east-1:123456789012:deliverystream/my-stream \
  --role-arn arn:aws:iam::123456789012:role/CWMetricStreamRole \
  --output-format json \
  --include-filters '[{"Namespace": "AWS/EC2"}, {"Namespace": "AWS/Lambda"}]'

aws cloudwatch start-metric-streams --names my-metric-stream
aws cloudwatch stop-metric-streams --names my-metric-stream
aws cloudwatch list-metric-streams
aws cloudwatch get-metric-stream --name my-metric-stream

# --- CloudWatch Logs ---
# --- Log Groups ---
# Create a log group
aws logs create-log-group \
  --log-group-name /myapp/production

# Create with KMS encryption
aws logs create-log-group \
  --log-group-name /myapp/production \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/my-key

# Set retention policy on a log group (days: 1,3,5,7,14,30,60,90,120,150,180,365,400,545,731,1096,1827,2192,2557,2922,3288,3653)
aws logs put-retention-policy \
  --log-group-name /myapp/production \
  --retention-in-days 90

# Remove retention policy (never expire)
aws logs delete-retention-policy --log-group-name /myapp/production

# Describe log groups
aws logs describe-log-groups
aws logs describe-log-groups --log-group-name-prefix /myapp
aws logs describe-log-groups --limit 50

# Delete a log group
aws logs delete-log-group --log-group-name /myapp/production

# --- Log Streams ---
# Create a log stream
aws logs create-log-stream \
  --log-group-name /myapp/production \
  --log-stream-name app-instance-1

# Describe log streams
aws logs describe-log-streams \
  --log-group-name /myapp/production
aws logs describe-log-streams \
  --log-group-name /myapp/production \
  --order-by LastEventTime \
  --descending

# Delete a log stream
aws logs delete-log-stream \
  --log-group-name /myapp/production \
  --log-stream-name app-instance-1

# --- Log Events ---
# Put log events (sequence token required after first put)
aws logs put-log-events \
  --log-group-name /myapp/production \
  --log-stream-name app-instance-1 \
  --log-events '[
    {"timestamp": 1704067200000, "message": "Application started"},
    {"timestamp": 1704067201000, "message": "Listening on port 8080"}
  ]'

# Get log events from a stream
aws logs get-log-events \
  --log-group-name /myapp/production \
  --log-stream-name app-instance-1 \
  --start-time 1704067200000 \
  --end-time 1704070800000 \
  --limit 100

# Filter log events across streams in a log group
aws logs filter-log-events \
  --log-group-name /myapp/production \
  --filter-pattern "ERROR" \
  --start-time 1704067200000 \
  --end-time 1704070800000

# Filter with a pattern on a specific stream
aws logs filter-log-events \
  --log-group-name /myapp/production \
  --log-stream-names app-instance-1 \
  --filter-pattern '[timestamp, requestId, level="ERROR", ...]'

# --- Logs Insights Queries ---
# Start a query
aws logs start-query \
  --log-group-name /myapp/production \
  --start-time 1704067200 \
  --end-time 1704070800 \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20'
# Returns queryId

# Get query results
aws logs get-query-results --query-id <query-id>

# Multi-log-group query
aws logs start-query \
  --log-group-names /myapp/production /myapp/staging \
  --start-time 1704067200 \
  --end-time 1704070800 \
  --query-string 'stats count(*) as errors by bin(5m) | sort errors desc'

# List running or recent queries
aws logs describe-queries
aws logs describe-queries --log-group-name /myapp/production --status Running

# Stop a running query
aws logs stop-query --query-id <query-id>

# --- Metric Filters ---
# Create a metric filter (count ERRORs → custom metric)
aws logs put-metric-filter \
  --log-group-name /myapp/production \
  --filter-name error-count \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0

# Describe metric filters
aws logs describe-metric-filters \
  --log-group-name /myapp/production

# Delete a metric filter
aws logs delete-metric-filter \
  --log-group-name /myapp/production \
  --filter-name error-count

# --- Subscription Filters ---
# Stream logs to Lambda in real time
aws logs put-subscription-filter \
  --log-group-name /myapp/production \
  --filter-name to-lambda \
  --filter-pattern "ERROR" \
  --destination-arn arn:aws:lambda:us-east-1:123456789012:function:log-processor

# Stream logs to Kinesis Firehose
aws logs put-subscription-filter \
  --log-group-name /myapp/production \
  --filter-name to-firehose \
  --filter-pattern "" \
  --destination-arn arn:aws:firehose:us-east-1:123456789012:deliverystream/log-delivery \
  --role-arn arn:aws:iam::123456789012:role/CWLSubscriptionRole

# Describe subscription filters
aws logs describe-subscription-filters \
  --log-group-name /myapp/production

# Delete a subscription filter
aws logs delete-subscription-filter \
  --log-group-name /myapp/production \
  --filter-name to-lambda

# --- Export Tasks ---
# Export logs to S3 (asynchronous; up to 12-hour delay)
aws logs create-export-task \
  --task-name my-export \
  --log-group-name /myapp/production \
  --from 1704067200000 \
  --to 1704154800000 \
  --destination my-log-archive-bucket \
  --destination-prefix logs/myapp/production/2024-01

# Describe export tasks
aws logs describe-export-tasks
aws logs describe-export-tasks --status-code COMPLETED
```
