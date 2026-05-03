# AWS CloudWatch Metric Filters — CLI Reference
For concepts and patterns, see [cloudwatch-metric-filters-capabilities.md](cloudwatch-metric-filters-capabilities.md).

```bash
# ============================================================
# PUT (CREATE OR UPDATE)
# ============================================================

# Simple text pattern — count occurrences, with default value
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "ErrorCount" \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0,unit=Count

# OR pattern — count errors or warnings
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "ErrorOrWarning" \
  --filter-pattern "?ERROR ?WARNING" \
  --metric-transformations \
    metricName=ErrorOrWarningCount,metricNamespace=MyApp,metricValue=1,defaultValue=0,unit=Count

# Space-delimited — count 4xx HTTP responses
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "Http4xx" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code=4*, bytes]' \
  --metric-transformations \
    metricName=Http4xxCount,metricNamespace=MyApp/HTTP,metricValue=1,defaultValue=0,unit=Count

# Space-delimited — count 5xx responses
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "Http5xx" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code=5*, bytes]' \
  --metric-transformations \
    metricName=Http5xxCount,metricNamespace=MyApp/HTTP,metricValue=1,defaultValue=0,unit=Count

# JSON pattern — extract numeric latency from structured logs
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-api" \
  --filter-name "RequestLatency" \
  --filter-pattern '{ $.latency = * }' \
  --metric-transformations \
    metricName=RequestLatency,metricNamespace=MyApp,metricValue='$.latency',unit=Milliseconds

# JSON pattern — Lambda timeout detection
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "Timeouts" \
  --filter-pattern '"Task timed out"' \
  --metric-transformations \
    metricName=TimeoutCount,metricNamespace=MyApp,metricValue=1,defaultValue=0,unit=Count

# JSON pattern — count specific event type
aws logs put-metric-filter \
  --log-group-name "/myapp/events" \
  --filter-name "UserLogins" \
  --filter-pattern '{ $.eventType = "UserLogin" }' \
  --metric-transformations \
    metricName=UserLoginCount,metricNamespace=MyApp/Auth,metricValue=1,defaultValue=0,unit=Count

# JSON compound — CloudTrail unauthorized API calls
aws logs put-metric-filter \
  --log-group-name "CloudTrail/DefaultLogGroup" \
  --filter-name "UnauthorizedAPICalls" \
  --filter-pattern '{ ($.errorCode = "AccessDenied") || ($.errorCode = "UnauthorizedAccess") }' \
  --metric-transformations \
    metricName=UnauthorizedAPICalls,metricNamespace=CloudTrailMetrics,metricValue=1,defaultValue=0,unit=Count

# JSON — CloudTrail root account activity
aws logs put-metric-filter \
  --log-group-name "CloudTrail/DefaultLogGroup" \
  --filter-name "RootActivity" \
  --filter-pattern '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }' \
  --metric-transformations \
    metricName=RootActivityCount,metricNamespace=CloudTrailMetrics,metricValue=1,defaultValue=0,unit=Count

# JSON — extract bytes from space-delimited log into metric
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "ResponseBytes" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code, bytes]' \
  --metric-transformations \
    metricName=ResponseBytes,metricNamespace=MyApp/HTTP,metricValue='$bytes',unit=Bytes

# With dimensions — request count by status code (low-cardinality only — never use RequestId/IP/userId)
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "RequestsByStatus" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code, bytes]' \
  --metric-transformations '[{
    "metricName": "RequestCount",
    "metricNamespace": "MyApp",
    "metricValue": "1",
    "dimensions": {"StatusCode": "$status_code"}
  }]'

# With dimensions — JSON event type (note: cannot use defaultValue with dimensions)
aws logs put-metric-filter \
  --log-group-name "/myapp/events" \
  --filter-name "EventsByType" \
  --filter-pattern '{ $.eventType = * }' \
  --metric-transformations '[{
    "metricName": "EventCount",
    "metricNamespace": "MyApp",
    "metricValue": "1",
    "dimensions": {"EventType": "$.eventType"}
  }]'

# Apply filter on transformed logs (log group has an active transformer)
aws logs put-metric-filter \
  --log-group-name "/myapp/production" \
  --filter-name "ErrorOnTransformed" \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=TransformedErrors,metricNamespace=MyApp,metricValue=1,defaultValue=0 \
  --apply-on-transformed-logs

# Cross-account aggregation — add account/region as system field dimensions
aws logs put-metric-filter \
  --log-group-name "/central/logs" \
  --filter-name "ErrorsByAccount" \
  --filter-pattern "ERROR" \
  --metric-transformations '[{
    "metricName": "ErrorCount",
    "metricNamespace": "MyApp",
    "metricValue": "1",
    "dimensions": {"Account": "@aws.account", "Region": "@aws.region"}
  }]' \
  --emit-system-field-dimensions @aws.account @aws.region

# Field selection criteria — filter which log sources are evaluated
aws logs put-metric-filter \
  --log-group-name "/central/logs" \
  --filter-name "ProdErrors" \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ProdErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0 \
  --field-selection-criteria '@aws.region = "us-east-1"'


# ============================================================
# TEST (VALIDATE PATTERN WITHOUT CREATING FILTER)
# ============================================================

# Test a simple text pattern
aws logs test-metric-filter \
  --filter-pattern "ERROR" \
  --log-event-messages \
    "2024-01-01 ERROR: connection refused" \
    "2024-01-01 INFO: server started" \
    "2024-01-01 Error: disk full"
# Returns: matched events with extractedValues (empty for simple text patterns)

# Test a space-delimited pattern — shows extractedValues for named fields
aws logs test-metric-filter \
  --filter-pattern '[ip, user, username, timestamp, request, status_code=4*, bytes]' \
  --log-event-messages \
    '127.0.0.1 - frank [10/Jan/2024:12:00:00] "GET /foo HTTP/1.1" 404 512' \
    '127.0.0.1 - frank [10/Jan/2024:12:00:01] "GET /bar HTTP/1.1" 200 1024'
# Only the 404 line appears in matches; extractedValues shows all named field values

# Test a JSON pattern with value extraction
aws logs test-metric-filter \
  --filter-pattern '{ $.latency = * }' \
  --log-event-messages \
    '{"latency": 250, "path": "/api/users", "method": "GET"}' \
    '{"error": "timeout", "path": "/api/orders"}' \
    '{"latency": 18, "path": "/health"}'
# Returns matches for the two events that have $.latency; extractedValues includes $.latency value

# Test a JSON compound pattern
aws logs test-metric-filter \
  --filter-pattern '{ ($.errorCode = "AccessDenied") || ($.errorCode = "UnauthorizedAccess") }' \
  --log-event-messages \
    '{"errorCode": "AccessDenied", "eventName": "DescribeInstances"}' \
    '{"errorCode": "NoCredentialsError", "eventName": "ListBuckets"}' \
    '{"errorCode": "UnauthorizedAccess", "eventName": "GetObject"}'


# ============================================================
# DESCRIBE
# ============================================================

# All filters for a log group
aws logs describe-metric-filters \
  --log-group-name "/aws/lambda/my-function"

# Filter by name prefix (requires --log-group-name)
aws logs describe-metric-filters \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name-prefix "Error"

# Find filters by metric name + namespace (reverse lookup)
aws logs describe-metric-filters \
  --metric-name "ErrorCount" \
  --metric-namespace "MyApp"

# Paginate through many filters
aws logs describe-metric-filters \
  --log-group-name "/myapp/production" \
  --page-size 10


# ============================================================
# DELETE
# ============================================================

aws logs delete-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "ErrorCount"


# ============================================================
# ALARM ON METRIC FILTER OUTPUT
# ============================================================

# Alarm on error count — recommended settings for metric filter alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "LambdaHighErrorRate" \
  --metric-name "ErrorCount" \
  --namespace "MyApp" \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:on-call-topic \
  --ok-actions arn:aws:sns:us-east-1:123456789012:on-call-topic

# Alarm on latency metric (extracted value)
aws cloudwatch put-metric-alarm \
  --alarm-name "HighP99Latency" \
  --metric-name "RequestLatency" \
  --namespace "MyApp" \
  --extended-statistic p99 \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:on-call-topic
```
