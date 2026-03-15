# Governance, Testing & Business ML — CLI Reference
For capabilities, see [governance-testing-ml-capabilities.md](governance-testing-ml-capabilities.md).

## Amazon CodeGuru Reviewer

```bash
# --- Repository Associations ---
# Associate a GitHub repository
aws codeguru-reviewer associate-repository \
  --repository '{
    "GitHub": {
      "Name": "my-org/my-app",
      "Owner": "my-org",
      "Type": "GitHub"
    }
  }'

# Associate a CodeCommit repository
aws codeguru-reviewer associate-repository \
  --repository '{
    "CodeCommit": {
      "Name": "my-codecommit-repo"
    }
  }'

aws codeguru-reviewer describe-repository-association \
  --association-arn arn:aws:codeguru-reviewer:us-east-1:123456789012:association:ASSOCIATION_ID

aws codeguru-reviewer list-repository-associations
aws codeguru-reviewer list-repository-associations \
  --states Associated \
  --providers GitHub

aws codeguru-reviewer disassociate-repository \
  --association-arn arn:aws:codeguru-reviewer:us-east-1:123456789012:association:ASSOCIATION_ID

# --- Code Reviews ---
# Trigger an on-demand repository analysis (full branch scan)
aws codeguru-reviewer create-code-review \
  --name baseline-review-2024 \
  --repository-association-arn arn:aws:codeguru-reviewer:us-east-1:123456789012:association:ASSOCIATION_ID \
  --type '{
    "RepositoryAnalysis": {
      "RepositoryHead": {
        "BranchName": "main"
      }
    }
  }'

aws codeguru-reviewer describe-code-review --code-review-arn CODE_REVIEW_ARN
aws codeguru-reviewer list-code-reviews \
  --type PullRequest \
  --repository-names my-app

# --- Recommendations ---
aws codeguru-reviewer list-recommendations \
  --code-review-arn CODE_REVIEW_ARN

# List with severity filter
aws codeguru-reviewer list-recommendations \
  --code-review-arn CODE_REVIEW_ARN \
  --query 'RecommendationSummaries[?Severity==`High`]'

# --- Feedback ---
# Submit positive feedback on a recommendation
aws codeguru-reviewer put-recommendation-feedback \
  --code-review-arn CODE_REVIEW_ARN \
  --recommendation-id RECOMMENDATION_ID \
  --reactions '["ThumbsUp"]'

# Submit negative feedback (marks as not useful)
aws codeguru-reviewer put-recommendation-feedback \
  --code-review-arn CODE_REVIEW_ARN \
  --recommendation-id RECOMMENDATION_ID \
  --reactions '["ThumbsDown"]'

aws codeguru-reviewer describe-recommendation-feedback \
  --code-review-arn CODE_REVIEW_ARN \
  --recommendation-id RECOMMENDATION_ID

aws codeguru-reviewer list-recommendation-feedback \
  --code-review-arn CODE_REVIEW_ARN

# Tagging
aws codeguru-reviewer tag-resource \
  --resource-arn arn:aws:codeguru-reviewer:us-east-1:123456789012:association:ASSOCIATION_ID \
  --tags env=production,team=platform
```

---

## Amazon CodeGuru Profiler

```bash
# --- Profiling Groups ---
aws codeguruprofiler create-profiling-group \
  --profiling-group-name my-service-profiler \
  --agent-orchestration-config '{"profilingEnabled": true}' \
  --compute-platform Default
  # compute-platform: Default (EC2/ECS/Lambda) or AWSLambda (Lambda-specific)

aws codeguruprofiler describe-profiling-group --profiling-group-name my-service-profiler
aws codeguruprofiler list-profiling-groups
aws codeguruprofiler update-profiling-group \
  --profiling-group-name my-service-profiler \
  --agent-orchestration-config '{"profilingEnabled": false}'
aws codeguruprofiler delete-profiling-group --profiling-group-name my-service-profiler

# --- Recommendations ---
# Get the latest recommendation report
aws codeguruprofiler get-recommendations \
  --profiling-group-name my-service-profiler \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T00:00:00Z \
  --locale en-US

# List findings reports
aws codeguruprofiler list-findings-reports \
  --profiling-group-name my-service-profiler \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T00:00:00Z

# Summary of findings across your account
aws codeguruprofiler get-findings-report-account-summary

# --- Profile Data ---
# Retrieve aggregated profile (for flame graph rendering)
aws codeguruprofiler get-profile \
  --profiling-group-name my-service-profiler \
  --start-time 2024-01-15T09:00:00Z \
  --end-time 2024-01-15T10:00:00Z \
  --period PT1H \
  --format application/json \
  profile-output.json

# List available profile times
aws codeguruprofiler list-profile-times \
  --profiling-group-name my-service-profiler \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T00:00:00Z \
  --period P1D \
  --order-by TimestampDescending

# Frame metric data (latency/cost of specific methods over time)
aws codeguruprofiler batch-get-frame-metric-data \
  --profiling-group-name my-service-profiler \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-16T00:00:00Z \
  --period PT1H \
  --frame-metrics '[{"frameName":"com.example.PaymentService.processPayment","type":"AggregatedRelativeTotalTime","threadStates":["RUNNABLE"]}]'

# --- Notifications ---
aws codeguruprofiler get-notification-configuration \
  --profiling-group-name my-service-profiler

aws codeguruprofiler add-notification-channels \
  --profiling-group-name my-service-profiler \
  --channels '[{
    "id": "channel-001",
    "uri": "arn:aws:sns:us-east-1:123456789012:profiler-alerts",
    "eventPublishers": ["AnomalyDetection"]
  }]'

aws codeguruprofiler remove-notification-channel \
  --profiling-group-name my-service-profiler \
  --channel-id channel-001

# --- Feedback ---
aws codeguruprofiler submit-feedback \
  --profiling-group-name my-service-profiler \
  --anomaly-instance-id ANOMALY_INSTANCE_ID \
  --type Positive
  # type: Positive (useful finding) or Negative (not useful)
```

---

## Amazon DevOps Guru

```bash
# --- Resource Coverage ---
# Enable DevOps Guru for all account resources
aws devops-guru update-resource-collection \
  --action ADD \
  --resource-collection '{
    "CloudFormation": {
      "StackNames": ["*"]
    }
  }'

# Enable for specific CloudFormation stacks
aws devops-guru update-resource-collection \
  --action ADD \
  --resource-collection '{
    "CloudFormation": {
      "StackNames": ["my-api-stack","my-db-stack"]
    }
  }'

# Enable for resources with specific tags
aws devops-guru update-resource-collection \
  --action ADD \
  --resource-collection '{
    "Tags": [{
      "AppBoundaryKey": "DevOpsGuruApp",
      "TagValues": ["my-production-app"]
    }]
  }'

aws devops-guru get-resource-collection \
  --resource-collection-type CloudFormation

aws devops-guru list-monitored-resources \
  --filters '{"ResourcePermission": "FULL_PERMISSION"}'

# --- Account Health ---
aws devops-guru describe-account-health
aws devops-guru describe-account-overview \
  --from-time 2024-01-01T00:00:00Z \
  --to-time 2024-01-31T23:59:59Z

# --- Insights ---
# List ongoing reactive insights
aws devops-guru list-insights \
  --status-filter '{
    "Ongoing": {
      "Type": "REACTIVE"
    }
  }'

# List all insights in a time range
aws devops-guru list-insights \
  --status-filter '{
    "Closed": {
      "Type": "ANY",
      "StartTimeRange": {
        "FromTime": 1704067200,
        "ToTime": 1706745600
      }
    }
  }'

# List proactive insights
aws devops-guru list-insights \
  --status-filter '{"Ongoing": {"Type": "PROACTIVE"}}'

aws devops-guru describe-insight --id INSIGHT_ID

# Search insights by resource ARN
aws devops-guru search-insights \
  --type REACTIVE \
  --search-criteria '{
    "OptInTagValues": [{
      "AppBoundaryKey": "DevOpsGuruApp",
      "TagValues": ["my-production-app"]
    }]
  }' \
  --start-time-range '{
    "FromTime": 1704067200,
    "ToTime": 1706745600
  }'

# --- Recommendations ---
aws devops-guru list-recommendations \
  --insight-id INSIGHT_ID \
  --locale EN_US

# --- Anomalies ---
aws devops-guru describe-anomaly --id ANOMALY_ID

aws devops-guru list-anomalies-for-insight \
  --insight-id INSIGHT_ID \
  --start-time-range '{
    "FromTime": 1704067200,
    "ToTime": 1706745600
  }'

aws devops-guru list-anomalous-log-groups \
  --insight-id INSIGHT_ID

# --- Events ---
aws devops-guru list-events \
  --filters '{
    "InsightId": "INSIGHT_ID"
  }'

# --- Notifications ---
aws devops-guru add-notification-channel \
  --config '{
    "Sns": {
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:devops-guru-alerts"
    },
    "Filters": {
      "Severities": ["HIGH","MEDIUM"],
      "MessageTypes": ["NEW_INSIGHT","CLOSED_INSIGHT","SEVERITY_UPGRADED"]
    }
  }'

aws devops-guru list-notification-channels
aws devops-guru remove-notification-channel --id CHANNEL_ID

# --- Service Integrations ---
# Enable OpsCenter integration
aws devops-guru update-service-integration \
  --service-integration '{
    "OpsCenter": {
      "OptInStatus": "ENABLED"
    }
  }'

aws devops-guru describe-service-integration

# --- Cost Estimation ---
aws devops-guru start-cost-estimation \
  --resource-collection '{
    "CloudFormation": {
      "StackNames": ["*"]
    }
  }'

aws devops-guru get-cost-estimation

# --- Feedback ---
aws devops-guru put-feedback \
  --insight-feedback '{
    "Id": "INSIGHT_ID",
    "Feedback": "VALID_COLLECTION"
  }'
  # Feedback values: VALID_COLLECTION, RECOMMENDATION_USEFUL,
  # ALERT_TOO_SENSITIVE, DATA_NOISY_ANOMALY, DATA_INCORRECT
```

---

## Amazon Augmented AI (A2I)

A2I is split across two CLI namespaces: `sagemaker` for resource management (flow definitions, task UIs) and `sagemaker-a2i-runtime` for human loop management.

```bash
# --- Worker Task UI (Human Task Template) ---
# Create a worker task template (HTML Liquid template)
aws sagemaker create-human-task-ui \
  --human-task-ui-name document-review-ui \
  --ui-template '{
    "Content": "<crowd-form>\n  <crowd-key-value-text-input\n    name=\"form-data\"\n    src.s3=\"{{ task.input.taskObject }}\"\n    initial-value=\"{{ task.input.selectedAiService }}\"\n    header=\"Review the extracted form fields\"\n    no-strip>\n  </crowd-key-value-text-input>\n</crowd-form>"
  }'

aws sagemaker describe-human-task-ui --human-task-ui-name document-review-ui
aws sagemaker list-human-task-uis \
  --creation-time-after 2024-01-01T00:00:00Z
aws sagemaker delete-human-task-ui --human-task-ui-name document-review-ui

# --- Flow Definitions ---
# Create a flow definition (private workforce example)
aws sagemaker create-flow-definition \
  --flow-definition-name invoice-review-flow \
  --human-loop-config '{
    "WorkteamArn": "arn:aws:sagemaker:us-east-1:123456789012:workteam/private-crowd/my-review-team",
    "HumanTaskUiArn": "arn:aws:sagemaker:us-east-1:123456789012:human-task-ui/document-review-ui",
    "TaskTitle": "Review Invoice Extraction",
    "TaskDescription": "Verify the extracted invoice fields are correct.",
    "TaskCount": 1,
    "TaskAvailabilityLifetimeInSeconds": 86400,
    "TaskTimeLimitInSeconds": 600
  }' \
  --output-config '{
    "S3OutputPath": "s3://my-a2i-output/invoice-reviews/",
    "KmsKeyId": "alias/my-key"
  }' \
  --role-arn arn:aws:iam::123456789012:role/A2IRole

# Flow definition with activation conditions (trigger on low confidence)
aws sagemaker create-flow-definition \
  --flow-definition-name textract-low-confidence-review \
  --human-loop-request-source '{
    "AwsManagedHumanLoopRequestSource": "AWS/Textract/AnalyzeDocument/Forms/V1"
  }' \
  --human-loop-activation-config '{
    "HumanLoopActivationConditionsConfig": {
      "HumanLoopActivationConditions": "{\"Conditions\":[{\"ConditionType\":\"ImportantFormKeyConfidenceCheck\",\"ConditionParameters\":{\"ImportantFormKey\":\"*\",\"ImportantFormKeyAliases\":[\"*\"],\"KeyValueBlockConfidenceLessThan\":90,\"WordBlockConfidenceLessThan\":90}}]}"
    }
  }' \
  --human-loop-config '{
    "WorkteamArn": "arn:aws:sagemaker:us-east-1:123456789012:workteam/private-crowd/my-team",
    "HumanTaskUiArn": "arn:aws:sagemaker:us-east-1:123456789012:human-task-ui/textract-forms-ui",
    "TaskTitle": "Review low-confidence form extraction",
    "TaskDescription": "Verify extracted key-value pairs from document",
    "TaskCount": 1,
    "TaskAvailabilityLifetimeInSeconds": 43200,
    "TaskTimeLimitInSeconds": 300
  }' \
  --output-config '{"S3OutputPath": "s3://my-a2i-output/textract-reviews/"}' \
  --role-arn arn:aws:iam::123456789012:role/A2IRole

aws sagemaker describe-flow-definition --flow-definition-name invoice-review-flow
aws sagemaker list-flow-definitions
aws sagemaker delete-flow-definition --flow-definition-name invoice-review-flow

# --- Human Loops (Runtime) ---
# Start a human loop (custom task types only; built-in types start automatically)
aws sagemaker-a2i-runtime start-human-loop \
  --flow-definition-arn arn:aws:sagemaker:us-east-1:123456789012:flow-definition/invoice-review-flow \
  --human-loop-name review-invoice-20240115-001 \
  --human-loop-input '{
    "InputContent": "{\"taskObject\": \"s3://my-bucket/invoices/inv-001.jpg\", \"selectedAiService\": {\"vendor\":\"AcmeCo\",\"total\":\"$1,234.56\",\"date\":\"2024-01-15\"}}"
  }'

aws sagemaker-a2i-runtime describe-human-loop \
  --human-loop-name review-invoice-20240115-001

aws sagemaker-a2i-runtime list-human-loops \
  --flow-definition-arn arn:aws:sagemaker:us-east-1:123456789012:flow-definition/invoice-review-flow

aws sagemaker-a2i-runtime list-human-loops \
  --flow-definition-arn FLOW_ARN \
  --filter-status Completed \
  --sort-order Descending

aws sagemaker-a2i-runtime stop-human-loop \
  --human-loop-name review-invoice-20240115-001

aws sagemaker-a2i-runtime delete-human-loop \
  --human-loop-name review-invoice-20240115-001
```

---

## Amazon Fraud Detector

```bash
# --- Variables ---
aws frauddetector create-variable \
  --name email_address \
  --variable-type EMAIL_ADDRESS \
  --data-type STRING \
  --data-source EVENT \
  --default-value "<unknown>"

aws frauddetector create-variable \
  --name order_amount \
  --variable-type PRICE \
  --data-type FLOAT \
  --data-source EVENT \
  --default-value "0.0"

aws frauddetector batch-create-variable --variable-entries file://variables.json
aws frauddetector get-variables
aws frauddetector delete-variable --name email_address

# --- Entity Types and Event Types ---
aws frauddetector put-entity-type \
  --name customer \
  --description "End customer making a purchase"

aws frauddetector put-event-type \
  --name online_payment \
  --entity-types '["customer"]' \
  --event-variables '["email_address","order_amount","ip_address","card_bin"]' \
  --labels '["fraud","legit"]' \
  --event-ingestion ENABLED

aws frauddetector get-event-types
aws frauddetector delete-event-type --name online_payment

# --- Labels ---
aws frauddetector put-label --name fraud --description "Confirmed fraudulent event"
aws frauddetector put-label --name legit --description "Confirmed legitimate event"
aws frauddetector get-labels
aws frauddetector delete-label --name fraud

# --- Outcomes ---
aws frauddetector put-outcome --name approve --description "Approve the transaction"
aws frauddetector put-outcome --name review --description "Send for manual review"
aws frauddetector put-outcome --name block --description "Block the transaction"
aws frauddetector get-outcomes
aws frauddetector delete-outcome --name block

# --- Models ---
# Create and train a model
aws frauddetector create-model \
  --model-id payment-fraud-model \
  --event-type-name online_payment \
  --model-type ONLINE_FRAUD_INSIGHTS

aws frauddetector create-model-version \
  --model-id payment-fraud-model \
  --model-type ONLINE_FRAUD_INSIGHTS \
  --training-data-source EXTERNAL_EVENTS \
  --training-data-schema '{
    "modelVariables": ["email_address","order_amount","ip_address","card_bin"],
    "labelSchema": {
      "labelMapper": {
        "FRAUD": ["fraud"],
        "LEGIT": ["legit"]
      },
      "unlabeledEventsTreatment": "IGNORE"
    }
  }' \
  --external-events-detail '{
    "dataLocation": "s3://my-fraud-data/training/",
    "dataAccessRoleArn": "arn:aws:iam::123456789012:role/FraudDetectorRole"
  }'

aws frauddetector describe-model-versions \
  --model-id payment-fraud-model \
  --model-type ONLINE_FRAUD_INSIGHTS

# Activate a model version for use in detectors
aws frauddetector update-model-version-status \
  --model-id payment-fraud-model \
  --model-type ONLINE_FRAUD_INSIGHTS \
  --model-version-number 1.00 \
  --status ACTIVE

# --- Detectors and Rules ---
aws frauddetector put-detector \
  --detector-id payment-fraud-detector \
  --event-type-name online_payment \
  --description "Payment fraud detection detector"

# Create a rule based on model score
aws frauddetector create-rule \
  --rule-id high-risk-rule \
  --detector-id payment-fraud-detector \
  --expression '$payment_fraud_model_insightscore > 900' \
  --language DETECTORPL \
  --outcomes '["block"]'

aws frauddetector create-rule \
  --rule-id medium-risk-rule \
  --detector-id payment-fraud-detector \
  --expression '$payment_fraud_model_insightscore > 700 and $payment_fraud_model_insightscore <= 900' \
  --language DETECTORPL \
  --outcomes '["review"]'

aws frauddetector create-rule \
  --rule-id low-risk-rule \
  --detector-id payment-fraud-detector \
  --expression '$payment_fraud_model_insightscore <= 700' \
  --language DETECTORPL \
  --outcomes '["approve"]'

aws frauddetector get-rules --detector-id payment-fraud-detector

# Create detector version with model and rules
aws frauddetector create-detector-version \
  --detector-id payment-fraud-detector \
  --rules '[
    {"detectorId":"payment-fraud-detector","ruleId":"high-risk-rule","ruleVersion":"1"},
    {"detectorId":"payment-fraud-detector","ruleId":"medium-risk-rule","ruleVersion":"1"},
    {"detectorId":"payment-fraud-detector","ruleId":"low-risk-rule","ruleVersion":"1"}
  ]' \
  --model-versions '[{
    "modelId": "payment-fraud-model",
    "modelType": "ONLINE_FRAUD_INSIGHTS",
    "modelVersionNumber": "1.00",
    "arn": "arn:aws:frauddetector:us-east-1:123456789012:model-version/payment-fraud-model/ONLINE_FRAUD_INSIGHTS/1.00"
  }]' \
  --rule-execution-mode FIRST_MATCHED

aws frauddetector update-detector-version-status \
  --detector-id payment-fraud-detector \
  --detector-version-id 1 \
  --status ACTIVE

aws frauddetector describe-detector --detector-id payment-fraud-detector

# --- Real-Time Prediction ---
aws frauddetector get-event-prediction \
  --detector-id payment-fraud-detector \
  --detector-version-id 1 \
  --event-id txn-$(date +%s) \
  --event-type-name online_payment \
  --event-timestamp $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --entities '[{"entityType":"customer","entityId":"cust-12345"}]' \
  --event-variables '{
    "email_address": "user@example.com",
    "order_amount": "299.99",
    "ip_address": "192.168.1.100",
    "card_bin": "411111"
  }'

# --- Batch Predictions ---
aws frauddetector create-batch-prediction-job \
  --job-id batch-score-jan-2024 \
  --event-type-name online_payment \
  --detector-name payment-fraud-detector \
  --detector-version 1 \
  --input-path "s3://my-fraud-data/batch-input/january-txns.csv" \
  --output-path "s3://my-fraud-data/batch-output/january-scores/" \
  --iam-role-arn arn:aws:iam::123456789012:role/FraudDetectorRole

aws frauddetector get-batch-prediction-jobs

# --- Events and Lists ---
aws frauddetector send-event \
  --event-id txn-historical-001 \
  --event-type-name online_payment \
  --event-timestamp "2024-01-15T10:00:00Z" \
  --event-variables '{"email_address":"buyer@example.com","order_amount":"500.00"}' \
  --assigned-label fraud \
  --label-timestamp "2024-01-20T00:00:00Z" \
  --entities '[{"entityType":"customer","entityId":"cust-99999"}]'

# Maintain a block list for known fraudulent IPs
aws frauddetector create-list \
  --name blocked-ips \
  --variable-type IP_ADDRESS

aws frauddetector update-list \
  --name blocked-ips \
  --elements '["192.168.1.1","10.0.0.1"]' \
  --action PUT
```
