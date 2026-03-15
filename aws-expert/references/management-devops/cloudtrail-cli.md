# AWS CloudTrail — CLI Reference
For service concepts, see [cloudtrail-capabilities.md](cloudtrail-capabilities.md).

```bash
# --- Trails ---
# Create a trail (multi-region, org-level)
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail \
  --include-global-service-events \
  --enable-log-file-validation \
  --kms-key-id alias/my-cloudtrail-key \
  --cloud-watch-logs-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:CloudTrail \
  --cloud-watch-logs-role-arn arn:aws:iam::123456789012:role/CloudTrail-CWLogs-Role

# Start logging on a trail
aws cloudtrail start-logging --name my-trail

# Stop logging on a trail
aws cloudtrail stop-logging --name my-trail

# Describe trails
aws cloudtrail describe-trails
aws cloudtrail describe-trails --include-shadow-trails false  # exclude shadow trails

# Get trail status (logging, last delivery, etc.)
aws cloudtrail get-trail-status --name my-trail

# Update a trail
aws cloudtrail update-trail \
  --name my-trail \
  --s3-bucket-name new-bucket \
  --is-multi-region-trail

# Delete a trail
aws cloudtrail delete-trail --name my-trail

# --- Event Selectors (what to record) ---
# Get current event selectors
aws cloudtrail get-event-selectors --trail-name my-trail

# Enable S3 data events + Lambda invoke events
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '[
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": true,
      "DataResources": [
        {"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::"]},
        {"Type": "AWS::Lambda::Function", "Values": ["arn:aws:lambda"]}
      ]
    }
  ]'

# Advanced event selectors (more granular filtering)
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --advanced-event-selectors '[
    {
      "Name": "S3PutObject",
      "FieldSelectors": [
        {"Field": "eventCategory", "Equals": ["Data"]},
        {"Field": "resources.type", "Equals": ["AWS::S3::Object"]},
        {"Field": "readOnly", "Equals": ["false"]}
      ]
    }
  ]'

# --- Insights ---
# Enable Insights on a trail (detects anomalous API call rates / error rates)
aws cloudtrail put-insight-selectors \
  --trail-name my-trail \
  --insight-selectors '[
    {"InsightType": "ApiCallRateInsight"},
    {"InsightType": "ApiErrorRateInsight"}
  ]'

# Get current Insight selectors
aws cloudtrail get-insight-selectors --trail-name my-trail

# --- Event History (90-day lookup) ---
# Look up events by attribute
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=ConsoleLogin \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z

# Look up events by username
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=alice

# Look up events by resource (S3 bucket)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=my-bucket

# --- CloudTrail Lake ---
# Create an event data store
aws cloudtrail create-event-data-store \
  --name my-event-data-store \
  --retention-period 365 \
  --multi-region-enabled \
  --organization-enabled \
  --termination-protection-enabled

# Start a SQL query against an event data store
aws cloudtrail start-query \
  --query-statement "SELECT eventName, userIdentity.arn, eventTime FROM eds WHERE eventTime > '2024-01-01 00:00:00' AND errorCode IS NOT NULL ORDER BY eventTime DESC LIMIT 100"
# Returns QueryId

# Get query results
aws cloudtrail get-query-results --query-id <query-id>

# List event data stores
aws cloudtrail list-event-data-stores

# Get event data store details
aws cloudtrail get-event-data-store \
  --event-data-store arn:aws:cloudtrail:us-east-1:123456789012:eventdatastore/<id>

# --- Log file validation ---
aws cloudtrail validate-logs \
  --trail-arn arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail \
  --start-time 2024-01-01T00:00:00Z
```
