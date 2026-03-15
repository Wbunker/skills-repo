# AWS Conversation & Recommendation Services — CLI Reference
For service concepts, see [conversation-recommendation-capabilities.md](conversation-recommendation-capabilities.md).

## Amazon Lex V2 Models

```bash
# --- Bots ---
aws lexv2-models create-bot \
  --bot-name CustomerServiceBot \
  --role-arn arn:aws:iam::123456789012:role/LexBotRole \
  --data-privacy '{"childDirected":false}' \
  --idle-session-ttl-in-seconds 300 \
  --description "Customer service bot for order management"

aws lexv2-models describe-bot --bot-id BOT_ID
aws lexv2-models list-bots
aws lexv2-models update-bot \
  --bot-id BOT_ID \
  --bot-name CustomerServiceBot \
  --role-arn arn:aws:iam::123456789012:role/LexBotRole \
  --data-privacy '{"childDirected":false}' \
  --idle-session-ttl-in-seconds 600
aws lexv2-models delete-bot --bot-id BOT_ID --skip-resource-in-use-check

# --- Bot Locales ---
aws lexv2-models create-bot-locale \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --nlu-intent-confidence-threshold 0.4 \
  --description "English US locale"

aws lexv2-models describe-bot-locale --bot-id BOT_ID --bot-version DRAFT --locale-id en_US
aws lexv2-models list-bot-locales --bot-id BOT_ID --bot-version DRAFT
aws lexv2-models delete-bot-locale --bot-id BOT_ID --bot-version DRAFT --locale-id en_US

# Build bot locale (compile for deployment)
aws lexv2-models build-bot-locale \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US

# --- Intents ---
aws lexv2-models create-intent \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-name OrderStatus \
  --description "Check the status of an order" \
  --sample-utterances '[{"utterance":"Where is my order"},{"utterance":"Track my order"},{"utterance":"What is the status of order {orderNumber}"},{"utterance":"Check order status"}]' \
  --fulfillment-code-hook '{"enabled":true}' \
  --dialog-code-hook '{"enabled":false}'

aws lexv2-models describe-intent --bot-id BOT_ID --bot-version DRAFT --locale-id en_US --intent-id INTENT_ID
aws lexv2-models list-intents --bot-id BOT_ID --bot-version DRAFT --locale-id en_US
aws lexv2-models update-intent \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-id INTENT_ID \
  --intent-name OrderStatus \
  --sample-utterances '[{"utterance":"Whats my order status"},{"utterance":"Order tracking"}]'
aws lexv2-models delete-intent --bot-id BOT_ID --bot-version DRAFT --locale-id en_US --intent-id INTENT_ID

# --- Slots ---
aws lexv2-models create-slot \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --intent-id INTENT_ID \
  --slot-name orderNumber \
  --slot-type-id AMAZON.AlphaNumeric \
  --value-elicitation-setting '{"promptSpecification":{"messageGroups":[{"message":{"plainTextMessage":{"value":"What is your order number?"}}}],"maxRetries":3},"slotConstraint":"Required"}'

aws lexv2-models describe-slot --bot-id BOT_ID --bot-version DRAFT --locale-id en_US --intent-id INTENT_ID --slot-id SLOT_ID
aws lexv2-models list-slots --bot-id BOT_ID --bot-version DRAFT --locale-id en_US --intent-id INTENT_ID

# --- Slot Types ---
aws lexv2-models create-slot-type \
  --bot-id BOT_ID \
  --bot-version DRAFT \
  --locale-id en_US \
  --slot-type-name ProductCategory \
  --slot-type-values '[{"sampleValue":{"value":"electronics"}},{"sampleValue":{"value":"clothing"}},{"sampleValue":{"value":"books"}}]' \
  --value-selection-setting '{"resolutionStrategy":"ORIGINAL_VALUE"}'

aws lexv2-models list-slot-types --bot-id BOT_ID --bot-version DRAFT --locale-id en_US

# --- Bot Versions and Aliases ---
aws lexv2-models create-bot-version \
  --bot-id BOT_ID \
  --bot-version-locale-specification '{"en_US":{"sourceBotVersion":"DRAFT"}}'

aws lexv2-models list-bot-versions --bot-id BOT_ID

aws lexv2-models create-bot-alias \
  --bot-id BOT_ID \
  --bot-alias-name production \
  --bot-version 1 \
  --bot-alias-locale-settings '{"en_US":{"enabled":true,"codeHookSpecification":{"lambdaCodeHook":{"lambdaARN":"arn:aws:lambda:us-east-1:123456789012:function:OrderFulfillment","codeHookInterfaceVersion":"1.0"}}}}'

aws lexv2-models list-bot-aliases --bot-id BOT_ID
aws lexv2-models describe-bot-alias --bot-id BOT_ID --bot-alias-id ALIAS_ID
```

---

## Amazon Lex V2 Runtime

```bash
# --- Text Recognition ---
aws lexv2-runtime recognize-text \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session-$(date +%s) \
  --text "What is the status of my order?"

# With session attributes
aws lexv2-runtime recognize-text \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id existing-session-id \
  --text "Track order 12345" \
  --session-state '{"sessionAttributes":{"customerId":"CUST-001"}}'

# With request attributes
aws lexv2-runtime recognize-text \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session \
  --text "I want to return my purchase" \
  --request-attributes '{"channel":"web","x-amz-lex:channels:platform":"CUSTOM"}'

# --- Utterance Recognition ---
aws lexv2-runtime recognize-utterance \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session \
  --request-content-type "audio/x-l16; sample-rate=16000; channel-count=1" \
  --input-stream audio.raw \
  response.json

# --- Session Management ---
aws lexv2-runtime get-session \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session

aws lexv2-runtime put-session \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session \
  --session-state '{"intent":{"name":"OrderStatus","state":"InProgress","slots":{"orderNumber":{"value":{"originalValue":"12345","interpretedValue":"12345","resolvedValues":["12345"]}}}}}'

aws lexv2-runtime delete-session \
  --bot-id BOT_ID \
  --bot-alias-id ALIAS_ID \
  --locale-id en_US \
  --session-id my-session
```

---

## Amazon Personalize

```bash
# --- Dataset Groups ---
aws personalize create-dataset-group \
  --name ecommerce-recommendations \
  --domain ECOMMERCE

aws personalize create-dataset-group \
  --name video-recommendations \
  --domain VIDEO_ON_DEMAND

aws personalize describe-dataset-group --dataset-group-arn DATASET_GROUP_ARN
aws personalize list-dataset-groups
aws personalize delete-dataset-group --dataset-group-arn DATASET_GROUP_ARN

# --- Datasets ---
# Create interactions dataset (required for all recipes)
aws personalize create-dataset \
  --name interactions-dataset \
  --dataset-type Interactions \
  --dataset-group-arn DATASET_GROUP_ARN \
  --schema-arn SCHEMA_ARN

# Create items dataset (optional, enhances recommendations)
aws personalize create-dataset \
  --name items-dataset \
  --dataset-type Items \
  --dataset-group-arn DATASET_GROUP_ARN \
  --schema-arn ITEMS_SCHEMA_ARN

# Create users dataset
aws personalize create-dataset \
  --name users-dataset \
  --dataset-type Users \
  --dataset-group-arn DATASET_GROUP_ARN \
  --schema-arn USERS_SCHEMA_ARN

aws personalize describe-dataset --dataset-arn DATASET_ARN
aws personalize list-datasets --dataset-group-arn DATASET_GROUP_ARN

# Import data from S3
aws personalize create-dataset-import-job \
  --job-name initial-data-import \
  --dataset-arn DATASET_ARN \
  --data-source '{"dataLocation":"s3://my-bucket/interactions.csv"}' \
  --role-arn arn:aws:iam::123456789012:role/PersonalizeRole
aws personalize describe-dataset-import-job --dataset-import-job-arn IMPORT_JOB_ARN

# --- Schema ---
aws personalize create-schema \
  --name interactions-schema \
  --schema '{"type":"record","name":"Interactions","namespace":"com.amazonaws.personalize.schema","fields":[{"name":"USER_ID","type":"string"},{"name":"ITEM_ID","type":"string"},{"name":"TIMESTAMP","type":"long"},{"name":"EVENT_TYPE","type":"string"}],"version":"1.0"}'

aws personalize list-schemas
aws personalize describe-schema --schema-arn SCHEMA_ARN

# --- Solutions (train a model) ---
aws personalize create-solution \
  --name personalized-ranking-solution \
  --dataset-group-arn DATASET_GROUP_ARN \
  --recipe-arn arn:aws:personalize:::recipe/aws-personalized-ranking \
  --solution-config '{"eventValueThreshold":"0.5"}'

# With hyperparameter optimization
aws personalize create-solution \
  --name user-personalization-solution \
  --dataset-group-arn DATASET_GROUP_ARN \
  --recipe-arn arn:aws:personalize:::recipe/aws-user-personalization \
  --perform-h-p-o true \
  --solution-config '{"hpoConfig":{"hpoObjective":{"type":"maximize","metricName":"coverage","metricRegex":".*coverage=(.*)"},"hpoResourceConfig":{"maxNumberOfTrainingJobs":"10","maxParallelTrainingJobs":"2"}}}'

aws personalize describe-solution --solution-arn SOLUTION_ARN
aws personalize list-solutions --dataset-group-arn DATASET_GROUP_ARN

# Create solution version (train the model)
aws personalize create-solution-version --solution-arn SOLUTION_ARN
aws personalize describe-solution-version --solution-version-arn SOLUTION_VERSION_ARN
aws personalize list-solution-versions --solution-arn SOLUTION_ARN

# --- Campaigns (deploy for real-time inference) ---
aws personalize create-campaign \
  --name recommendations-campaign \
  --solution-version-arn SOLUTION_VERSION_ARN \
  --min-provisioned-t-p-s 5

aws personalize describe-campaign --campaign-arn CAMPAIGN_ARN
aws personalize list-campaigns --solution-arn SOLUTION_ARN
aws personalize update-campaign \
  --campaign-arn CAMPAIGN_ARN \
  --solution-version-arn NEW_SOLUTION_VERSION_ARN \
  --min-provisioned-t-p-s 10
aws personalize delete-campaign --campaign-arn CAMPAIGN_ARN

# --- Real-time Recommendations ---
aws personalize-runtime get-recommendations \
  --campaign-arn CAMPAIGN_ARN \
  --user-id "user-123" \
  --num-results 10

# Get recommendations with filter
aws personalize-runtime get-recommendations \
  --campaign-arn CAMPAIGN_ARN \
  --user-id "user-123" \
  --num-results 10 \
  --filter-arn FILTER_ARN \
  --filter-values '{"CATEGORY":"\"electronics\""}'

# Get personalized ranking
aws personalize-runtime get-personalized-ranking \
  --campaign-arn RANKING_CAMPAIGN_ARN \
  --user-id "user-123" \
  --input-list '["item-1","item-2","item-3","item-4","item-5"]'

# --- Event Tracking (real-time interaction ingestion) ---
aws personalize create-event-tracker \
  --name my-event-tracker \
  --dataset-group-arn DATASET_GROUP_ARN
# Use the returned trackingId in your application to send events via personalize-events API
aws personalize-events put-events \
  --tracking-id TRACKING_ID \
  --user-id "user-123" \
  --session-id "session-abc" \
  --event-list '[{"eventId":"evt-001","eventType":"Click","itemId":"item-456","sentAt":1700000000}]'

# --- Filters ---
aws personalize create-filter \
  --name exclude-purchased \
  --dataset-group-arn DATASET_GROUP_ARN \
  --filter-expression 'EXCLUDE ItemID WHERE INTERACTIONS.event_type = "purchase"'

aws personalize list-filters --dataset-group-arn DATASET_GROUP_ARN
aws personalize describe-filter --filter-arn FILTER_ARN

# --- Batch Recommendations ---
aws personalize create-batch-inference-job \
  --job-name batch-recs-job \
  --solution-version-arn SOLUTION_VERSION_ARN \
  --job-input '{"s3DataSource":{"path":"s3://my-bucket/user-ids/users.json"}}' \
  --job-output '{"s3DataDestination":{"path":"s3://my-bucket/recommendations/"}}' \
  --role-arn arn:aws:iam::123456789012:role/PersonalizeRole \
  --num-results 25
aws personalize describe-batch-inference-job --batch-inference-job-arn JOB_ARN
```

---

## Amazon Forecast

```bash
# --- Dataset Groups ---
aws forecast create-dataset-group \
  --dataset-group-name retail-demand-forecast \
  --domain RETAIL

aws forecast describe-dataset-group --dataset-group-arn DATASET_GROUP_ARN
aws forecast list-dataset-groups
aws forecast delete-dataset-group --dataset-group-arn DATASET_GROUP_ARN

# --- Datasets ---
# Create target time series dataset (required)
aws forecast create-dataset \
  --dataset-name retail-sales \
  --domain RETAIL \
  --dataset-type TARGET_TIME_SERIES \
  --data-frequency D \
  --schema '{"Attributes":[{"AttributeName":"item_id","AttributeType":"string"},{"AttributeName":"timestamp","AttributeType":"timestamp"},{"AttributeName":"demand","AttributeType":"float"}]}'

# Create related time series (optional, improves accuracy)
aws forecast create-dataset \
  --dataset-name retail-prices \
  --domain RETAIL \
  --dataset-type RELATED_TIME_SERIES \
  --data-frequency D \
  --schema '{"Attributes":[{"AttributeName":"item_id","AttributeType":"string"},{"AttributeName":"timestamp","AttributeType":"timestamp"},{"AttributeName":"price","AttributeType":"float"}]}'

aws forecast describe-dataset --dataset-arn DATASET_ARN
aws forecast list-datasets

# Import data from S3
aws forecast create-dataset-import-job \
  --dataset-import-job-name import-sales-data \
  --dataset-arn DATASET_ARN \
  --data-source '{"S3Config":{"Path":"s3://my-bucket/sales-data.csv","RoleArn":"arn:aws:iam::123456789012:role/ForecastRole"}}' \
  --timestamp-format "yyyy-MM-dd"

aws forecast describe-dataset-import-job --dataset-import-job-arn IMPORT_JOB_ARN

# Link datasets to dataset group
aws forecast update-dataset-group \
  --dataset-group-arn DATASET_GROUP_ARN \
  --dataset-arns '["TARGET_TS_ARN","RELATED_TS_ARN"]'

# --- Predictors (AutoPredictor - recommended) ---
aws forecast create-auto-predictor \
  --predictor-name retail-predictor \
  --forecast-horizon 30 \
  --forecast-frequency D \
  --dataset-import-job-arns '["IMPORT_JOB_ARN"]' \
  --forecast-dimensions '["location"]' \
  --optimization-metric AverageWeightedQuantileLoss

aws forecast describe-auto-predictor --predictor-arn PREDICTOR_ARN
aws forecast list-predictors --dataset-group-arn DATASET_GROUP_ARN

# Legacy predictor (manual algorithm selection)
aws forecast create-predictor \
  --predictor-name manual-predictor \
  --algorithm-arn arn:aws:forecast:::algorithm/Deep_AR_Plus \
  --forecast-horizon 30 \
  --input-data-config '{"DatasetGroupArn":"DATASET_GROUP_ARN"}' \
  --featurization-config '{"ForecastFrequency":"D"}'

# --- Forecasts ---
aws forecast create-forecast \
  --forecast-name retail-30day-forecast \
  --predictor-arn PREDICTOR_ARN \
  --forecast-types '["p10","p50","p90"]'

aws forecast describe-forecast --forecast-arn FORECAST_ARN
aws forecast list-forecasts --predictor-arn PREDICTOR_ARN

# Export forecast to S3
aws forecast create-forecast-export-job \
  --forecast-export-job-name export-forecast \
  --forecast-arn FORECAST_ARN \
  --destination '{"S3Config":{"Path":"s3://my-bucket/forecast-output/","RoleArn":"arn:aws:iam::123456789012:role/ForecastRole"}}'

aws forecast describe-forecast-export-job --forecast-export-job-arn EXPORT_JOB_ARN

# Query forecast (point-in-time)
aws forecastquery query-forecast \
  --forecast-arn FORECAST_ARN \
  --filters '{"item_id":"ITEM-001","location":"STORE-NYC"}' \
  --start-date "2025-01-01T00:00:00" \
  --end-date "2025-01-31T00:00:00"

# What-if analysis
aws forecast create-what-if-analysis \
  --what-if-analysis-name promo-scenario \
  --forecast-arn FORECAST_ARN

aws forecast create-what-if-forecast \
  --what-if-forecast-name promo-20-pct-increase \
  --what-if-analysis-arn WHAT_IF_ARN \
  --time-series-transformations '[{"action":{"operation":"MULTIPLY","value":1.2},"timeSeriesConditions":[{"attributeName":"item_id","attributeValue":"ITEM-001","condition":"EQUALS"}]}]'

aws forecast describe-what-if-forecast --what-if-forecast-arn WHAT_IF_FORECAST_ARN

# Delete resources
aws forecast delete-forecast --forecast-arn FORECAST_ARN
aws forecast delete-predictor --predictor-arn PREDICTOR_ARN
```

---

## Amazon Kendra

```bash
# --- Index Management ---
aws kendra create-index \
  --name my-enterprise-search \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --edition ENTERPRISE_EDITION \
  --description "Corporate knowledge base index"

# Developer edition (lower cost, for testing)
aws kendra create-index \
  --name my-dev-index \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --edition DEVELOPER_EDITION

aws kendra describe-index --id INDEX_ID
aws kendra list-indices
aws kendra update-index \
  --id INDEX_ID \
  --document-metadata-configuration-updates '[{"Name":"_category","Relevance":{"Importance":2},"Search":{"Facetable":true,"Searchable":true,"Displayable":true,"Sortable":true}}]'
aws kendra delete-index --id INDEX_ID

# --- Data Sources ---
# S3 data source
aws kendra create-data-source \
  --index-id INDEX_ID \
  --name s3-documents \
  --type S3 \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --configuration '{"S3Configuration":{"BucketName":"my-docs-bucket","InclusionPrefixes":["public-docs/"],"DocumentsMetadataConfiguration":{"S3Prefix":"metadata/"}}}'

# SharePoint data source
aws kendra create-data-source \
  --index-id INDEX_ID \
  --name sharepoint-source \
  --type SHAREPOINT \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --configuration '{"SharePointConfiguration":{"SharePointVersion":"SHAREPOINT_ONLINE","Urls":["https://mycompany.sharepoint.com/sites/docs"],"SecretArn":"arn:aws:secretsmanager:us-east-1:123456789012:secret:sharepoint-creds"}}'

aws kendra describe-data-source --index-id INDEX_ID --id DATA_SOURCE_ID
aws kendra list-data-sources --index-id INDEX_ID
aws kendra delete-data-source --index-id INDEX_ID --id DATA_SOURCE_ID

# --- Data Source Sync ---
aws kendra start-data-source-sync-job \
  --index-id INDEX_ID \
  --id DATA_SOURCE_ID

aws kendra describe-data-source-sync-job --index-id INDEX_ID --id DATA_SOURCE_ID
aws kendra list-data-source-sync-jobs --index-id INDEX_ID --id DATA_SOURCE_ID
aws kendra stop-data-source-sync-job --index-id INDEX_ID --id DATA_SOURCE_ID

# --- Direct Document Operations ---
# Add documents directly to index (without data source)
aws kendra batch-put-document \
  --index-id INDEX_ID \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --documents '[{"Id":"doc-001","Title":"Company Return Policy","ContentType":"PLAIN_TEXT","Blob":"'$(base64 -i policy.txt)'","Attributes":[{"Key":"_category","Value":{"StringValue":"HR"}},{"Key":"_source_uri","Value":{"StringValue":"https://internal.example.com/policy"}}]}]'

aws kendra batch-delete-document \
  --index-id INDEX_ID \
  --document-id-list '["doc-001","doc-002"]'

# --- FAQ Management ---
aws kendra create-faq \
  --index-id INDEX_ID \
  --name company-faqs \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --s3-path '{"Bucket":"my-bucket","Key":"faqs/company-faqs.csv"}' \
  --file-format CSV_WITH_HEADER \
  --description "Common company questions and answers"

aws kendra list-faqs --index-id INDEX_ID
aws kendra describe-faq --index-id INDEX_ID --id FAQ_ID
aws kendra delete-faq --index-id INDEX_ID --id FAQ_ID

# --- Querying ---
# Basic natural language query
aws kendra query \
  --index-id INDEX_ID \
  --query-text "What is the vacation policy?"

# Query with result type filter
aws kendra query \
  --index-id INDEX_ID \
  --query-text "How do I submit an expense report?" \
  --query-result-type-filter DOCUMENT

# Query with attribute filter
aws kendra query \
  --index-id INDEX_ID \
  --query-text "safety procedures" \
  --attribute-filter '{"EqualsTo":{"Key":"_category","Value":{"StringValue":"Safety"}}}'

# Query with user context (for ACL filtering)
aws kendra query \
  --index-id INDEX_ID \
  --query-text "confidential project roadmap" \
  --user-context '{"Token":"USER_JWT_TOKEN"}'

# --- Thesaurus and Synonyms ---
aws kendra create-thesaurus \
  --index-id INDEX_ID \
  --name company-synonyms \
  --role-arn arn:aws:iam::123456789012:role/KendraRole \
  --source-s3-path '{"Bucket":"my-bucket","Key":"thesaurus/synonyms.txt"}' \
  --description "Company-specific synonym mappings"

aws kendra list-thesauri --index-id INDEX_ID
aws kendra delete-thesaurus --index-id INDEX_ID --id THESAURUS_ID

# --- Query Suggestions ---
aws kendra get-query-suggestions \
  --index-id INDEX_ID \
  --query-text "how do I"

# --- Tagging ---
aws kendra list-tags-for-resource --resource-arn RESOURCE_ARN
aws kendra tag-resource --resource-arn RESOURCE_ARN --tags key=env,value=production
aws kendra untag-resource --resource-arn RESOURCE_ARN --tag-keys env
```
