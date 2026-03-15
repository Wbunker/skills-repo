# AWS X-Ray / Fault Injection Service — CLI Reference

For service concepts, see [xray-fis-capabilities.md](xray-fis-capabilities.md).

## X-Ray

```bash
# --- Service Graph ---
# Get service graph (visual map of services and connections)
aws xray get-service-graph \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z

# Get service graph scoped to a group
aws xray get-service-graph \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --group-name my-service-group

# --- Traces ---
# Get trace summaries (search for traces matching criteria)
aws xray get-trace-summaries \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --filter-expression 'error = true AND responsetime > 5'

# Get trace summaries with sampling
aws xray get-trace-summaries \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --sampling \
  --sampling-strategy name=PartialScan

# Get full trace details (segments and subsegments)
aws xray batch-get-traces \
  --trace-ids 1-58406520-a006649127e371903a2de979 1-58406520-b006649127e371903a2de980

# --- Groups ---
# Create a group (named filter for traces)
aws xray create-group \
  --group-name production-errors \
  --filter-expression 'error = true AND service("my-service")' \
  --insights-configuration InsightsEnabled=true,NotificationsEnabled=true

# Get groups
aws xray get-groups

# Get a specific group
aws xray get-group --group-name production-errors

# Update a group
aws xray update-group \
  --group-name production-errors \
  --filter-expression 'error = true OR fault = true AND service("my-service")'

# Delete a group
aws xray delete-group --group-name production-errors

# --- Sampling Rules ---
# Create a sampling rule
aws xray create-sampling-rule \
  --sampling-rule '{
    "RuleName": "HighValueRequests",
    "Priority": 1,
    "FixedRate": 0.05,
    "ReservoirSize": 10,
    "ServiceName": "my-api",
    "ServiceType": "AWS::APIGateway::Stage",
    "Host": "*",
    "HTTPMethod": "POST",
    "URLPath": "/checkout*",
    "ResourceARN": "*",
    "Version": 1
  }'

# Get sampling rules
aws xray get-sampling-rules

# Update a sampling rule
aws xray update-sampling-rule \
  --sampling-rule-update RuleName=HighValueRequests,FixedRate=0.10,ReservoirSize=20

# Delete a sampling rule
aws xray delete-sampling-rule --rule-name HighValueRequests

# Get sampling targets (used by SDK to decide whether to sample each request)
aws xray get-sampling-targets \
  --sampling-statistics-documents '[
    {
      "RuleName": "HighValueRequests",
      "ClientID": "my-service-instance",
      "Timestamp": 1704067200,
      "RequestCount": 100,
      "SampledCount": 5,
      "BorrowCount": 1
    }
  ]'

# --- Encryption ---
# Get current encryption config
aws xray get-encryption-config

# Set encryption to use KMS
aws xray put-encryption-config \
  --type KMS \
  --key-id alias/my-xray-key

# Set back to AWS managed encryption
aws xray put-encryption-config --type NONE
```

---

## Fault Injection Service (FIS)

```bash
# --- Experiment Templates ---
# Create an experiment template
aws fis create-experiment-template \
  --description "Terminate 10% of prod EC2 instances" \
  --stop-conditions '[{"source":"aws:cloudwatch:alarm","value":"arn:aws:cloudwatch:us-east-1:123456789012:alarm:app-health"}]' \
  --targets '{
    "ec2Instances": {
      "resourceType": "aws:ec2:instance",
      "resourceTags": {"Env": "prod"},
      "selectionMode": "PERCENT(10)"
    }
  }' \
  --actions '{
    "terminateInstances": {
      "actionId": "aws:ec2:terminate-instances",
      "targets": {"Instances": "ec2Instances"}
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/FISRole

# List experiment templates
aws fis list-experiment-templates

# Get experiment template details
aws fis get-experiment-template --id EXT123456789ABCDEF

# Update an experiment template
aws fis update-experiment-template \
  --id EXT123456789ABCDEF \
  --description "Updated description"

# Delete an experiment template
aws fis delete-experiment-template --id EXT123456789ABCDEF

# --- Experiments ---
# Start an experiment
aws fis start-experiment \
  --experiment-template-id EXT123456789ABCDEF \
  --tags Name=chaos-2024-01-01

# Get experiment status and details
aws fis get-experiment --id EXP123456789ABCDEF

# List experiments
aws fis list-experiments
aws fis list-experiments \
  --max-results 10

# Stop a running experiment
aws fis stop-experiment --id EXP123456789ABCDEF

# --- Actions ---
# List available FIS actions
aws fis list-actions

# Get details of a specific action
aws fis get-action --id aws:ec2:terminate-instances

# --- Target Account Configurations ---
# Create a target account configuration (for cross-account experiments)
aws fis create-target-account-configuration \
  --experiment-template-id EXT123456789ABCDEF \
  --account-id 123456789012 \
  --role-arn arn:aws:iam::123456789012:role/FISCrossAccountRole \
  --description "Target account for chaos experiments"

# List target account configurations
aws fis list-target-account-configurations \
  --experiment-template-id EXT123456789ABCDEF

# Get a target account configuration
aws fis get-target-account-configuration \
  --experiment-template-id EXT123456789ABCDEF \
  --account-id 123456789012

# Delete a target account configuration
aws fis delete-target-account-configuration \
  --experiment-template-id EXT123456789ABCDEF \
  --account-id 123456789012

# --- Experiment Templates from Running Experiments ---
# List experiment resolved targets (see what was actually targeted)
aws fis list-experiment-resolved-targets \
  --id EXP123456789ABCDEF
```
